"""Submission layer: push batches up (tar-over-ssh), qsub arrays, marker jobs for hold-chains (§12.4/§14.3).

Every function takes a ``runner`` callable (``runner(cmd: list[str]) -> str`` returning stdout)
so tests inject a fake and NOTHING here touches the network at import or test time. Production
passes :func:`ssh_runner` (the ``myriad`` Host alias — key auth, keepalives from ~/.ssh/config;
credentials never appear here, R10).

Researched rules encoded: one ARRAY = one queue entry (R3: never loop qsub); submit-rate safety
via a single qsub per batch; ``-hold_jid`` released by 5-minute MARKER jobs so dependent arrays
are pre-submitted with ZERO driver latency (§14.3); job ids parsed from Grid Engine's canonical
"Your job[-array] <id>" line.
"""
from __future__ import annotations

import re
import shlex
import subprocess
from pathlib import Path
from typing import Callable

__all__ = [
    "ssh_runner", "ssh_base", "push_batch", "qsub", "submit_marker", "parse_job_id",
    "sanitize_name", "prepare_remote",
]

Runner = Callable[[list[str]], str]

_JOB_ID_RE = re.compile(r"Your job(?:-array)? (\d+)")

# Driver-scoped ssh hardening (2026-07-08). Scoped to the driver's OWN calls — Tamer's interactive
# ``ssh myriad`` (incl. the first-login key install that may need his UCL password) is UNTOUCHED.
#  * BatchMode=yes            — never block on a password/passphrase PROMPT: the unattended driver
#                               uses KEY auth, so a missing/broken key must fail FAST, not hang a
#                               multi-day run forever waiting on stdin no one will type into.
#  * StrictHostKeyChecking=accept-new — auto-trust the host key on FIRST connect (no yes/no prompt
#                               to wedge the driver) while still REFUSING a CHANGED key (MITM guard).
_SSH_OPTS = ["-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new"]


def ssh_base(host: str = "myriad") -> list[str]:
    """The hardened ``ssh`` argv prefix for a DRIVER call to ``host`` (see :data:`_SSH_OPTS`)."""
    return ["ssh", *_SSH_OPTS, host]


def ssh_runner(host: str = "myriad") -> Runner:
    """The production runner: ``cmd`` executed via ssh on ``host`` (checked, stdout returned).

    V10 audit fix: ssh joins its argument vector with spaces and the REMOTE shell re-splits the
    result — so an unquoted ``["bash", "-c", script]`` would deliver only ``printf`` to ``-c``
    and scatter the rest. Every word is therefore ``shlex.quote``d (POSIX quoting — correct for
    the remote Linux side regardless of the local OS) so the remote shell sees exactly the argv
    we intended. Hardened with :func:`ssh_base` so an unattended driver never hangs on a prompt.
    """

    def _run(cmd: list[str]) -> str:
        remote = " ".join(shlex.quote(c) for c in cmd)
        out = subprocess.run(
            [*ssh_base(host), remote], capture_output=True, text=True, timeout=300, check=True
        )
        return out.stdout
    return _run


def parse_job_id(qsub_stdout: str) -> str:
    """Extract the numeric job id from qsub output; fail loud on anything unexpected."""
    m = _JOB_ID_RE.search(qsub_stdout)
    if not m:
        raise RuntimeError(f"could not parse a job id from qsub output: {qsub_stdout!r}")
    return m.group(1)


def push_batch(batch_dir: str | Path, remote_specs_root: str, *, host: str = "myriad") -> None:
    """Push one local batch directory to ``<host>:<remote_specs_root>/<batch_name>/`` (tar-over-ssh).

    V9 audit fix: the Windows driver host has NO rsync (verified 2026-07-06 — only scp/ssh live
    in PATH), so the batch streams as a tar pipe: local ``tar -cf -`` | ssh | remote ``tar -xf -``.
    Idempotent — re-pushing overwrites byte-identical content-addressed files (spec_io writes
    sorted-keys JSON). A torn push cannot start a wrong training: ``read_spec`` on the node
    fail-CLOSES on a missing index / sha mismatch (V6), so partial arrival is caught at the
    moment of use, not silently trained.
    """
    src = Path(batch_dir)
    if not src.is_dir():
        raise FileNotFoundError(f"batch dir {src} does not exist")
    name = sanitize_name(src.name)
    root = remote_specs_root.rstrip("/")
    # The local tar runs with cwd=parent (no -C: Windows bsdtar/GNU-tar path-flavor quirks); the
    # REMOTE side is POSIX-quoted for the cluster's shell. check=True on ssh catches a dropped
    # connection; tar.wait() catches a local read failure.
    remote_cmd = "mkdir -p " + shlex.quote(root) + " && tar -xf - -C " + shlex.quote(root)
    tar = subprocess.Popen(["tar", "-cf", "-", name], stdout=subprocess.PIPE, cwd=str(src.parent))
    try:
        subprocess.run([*ssh_base(host), remote_cmd], stdin=tar.stdout, check=True, timeout=1800)
    finally:
        if tar.stdout is not None:
            tar.stdout.close()
    if tar.wait(timeout=300) != 0:
        raise subprocess.CalledProcessError(tar.returncode, f"tar -cf - {name} (local)")


def qsub(jobscript_remote_path: str, runner: Runner) -> str:
    """Submit ONE array jobscript (already on the cluster); return the job id."""
    return parse_job_id(runner(["qsub", jobscript_remote_path]))


def submit_marker(name: str, after_job_id: str, remote_root: str, runner: Runner) -> str:
    """A 5-minute 1-core job holding on ``after_job_id`` — the anchor dependent arrays hold on.

    Chain shape: search_array(id=A) -> marker(hold A, id=M) -> test_array(hold M). The test
    array is thereby PRE-SUBMITTED at launch and released by Grid Engine itself the second the
    arm's search completes (zero driver latency, §14.3).
    """
    name = sanitize_name(name)
    if not after_job_id.isdigit():
        raise ValueError(f"after_job_id must be a numeric SGE job id, got {after_job_id!r}")
    # V2 audit fix: build the script with ``printf '%s\n'`` (one argument per line). Plain
    # ``echo`` does NOT interpret ``\n`` in POSIX sh, so the old version collapsed every ``#$``
    # directive onto one dead comment line — the hold/h_rt would silently never apply.
    lines = [
        "#!/bin/bash -l",
        f"#$ -N {name}",
        "#$ -l h_rt=0:5:0",
        f"#$ -hold_jid {after_job_id}",
        f"#$ -wd {remote_root}",
        "true",
    ]
    # shlex.quote (not hand-rolled '...') so embedded quotes/spaces in remote_root can never
    # break the script; the redirect target is quoted for the same reason.
    quoted = " ".join(shlex.quote(ln) for ln in lines)
    target = shlex.quote(f"{remote_root}/{name}.sh")
    script = f"printf '%s\\n' {quoted} > {target} && qsub {target}"
    return parse_job_id(runner(["bash", "-c", script]))


_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]*$")


def sanitize_name(name: str) -> str:
    """Validate a job/batch name for SGE ``-N`` and shell interpolation (fail loud, not filter)."""
    if not _NAME_RE.match(name):
        raise ValueError(f"invalid SGE job name {name!r} (must match {_NAME_RE.pattern})")
    return name


def prepare_remote(remote_root: str, batch_names: list[str], runner: Runner) -> None:
    """Create the remote dirs a batch needs BEFORE qsub (V4 audit fix).

    Grid Engine must be able to open the ``#$ -o`` log path at job START, so ``logs/<name>``
    cannot be left to the job body alone (the in-script ``mkdir`` is only a belt). Call once per
    batch, before :func:`qsub`.
    """
    root = remote_root.rstrip("/")
    # outputs/ is pre-created too (V9): the first pull's remote ``find`` must never race the
    # first job's mkdir — an existing-but-empty outputs root cleanly means "0 completed".
    dirs = [f"{root}/specs", f"{root}/ledger", f"{root}/outputs"]
    dirs += [f"{root}/logs/{sanitize_name(n)}" for n in batch_names]
    runner(["mkdir", "-p", *dirs])
