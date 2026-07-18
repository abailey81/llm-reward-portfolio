"""Polling layer: pull the remote archive, read completion truth, plan compacted resumes (§14.1).

The archive IS the queue: a task is DONE iff its record.json exists (the same atomic-commit
truth the whole pipeline rests on). Completion therefore survives any scheduler/driver/network
failure. ``pending_specs`` implements the COMPACTED-RESUME diff: given the full task list and
the pulled archive, return only the specs whose run_ids are missing — the next array contains
exactly the unfinished work and nothing else (zero wasted fair-share).

Transfer (V9 audit fix): the Windows driver host has NO rsync (verified 2026-07-06 — only
scp/ssh in PATH), so the pull is tar-over-ssh with EXACT incrementality derived from our own
architecture: records are immutable after their atomic commit, so the remote-vs-local run-dir
set DIFF is the complete transfer list — nothing approximate about it. Dirs land in a staging
area and move into the mirror only once whole (record.json verified), preserving the archive's
write-then-rename discipline end-to-end; the nightly mirror chain re-verifies content hashes
downstream.
"""
from __future__ import annotations

import json
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable

__all__ = [
    "pull_archive",
    "remote_completed_dirs",
    "remote_reject_files",
    "completed_run_ids",
    "permanent_reject_ids",
    "pending_specs",
    "spec_run_id",
]

#: fetch(relpaths, staging_dir) — stream those run dirs from the cluster into staging_dir.
Fetch = Callable[[list[str], Path], None]

_STAGING = ".pull_tmp"


def remote_completed_dirs(
    remote_outputs_root: str, runner: Callable[[list[str]], str]
) -> set[str]:
    """POSIX relpaths of every COMMITTED record dir on the cluster (one ssh round-trip).

    record.json is written LAST by the atomic archive commit, so find-by-record.json lists only
    COMPLETE run dirs — the same completion truth :func:`completed_run_ids` reads locally.
    Fails LOUD (with guidance) on a missing root: silently returning 0 forever would mask a
    wrong-path config bug; ``prepare_remote`` pre-creates ``outputs/`` so empty-but-existing
    cleanly means "0 completed".
    """
    root = remote_outputs_root.rstrip("/")
    try:
        out = runner(["find", root, "-name", "record.json", "-type", "f"])
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"listing {root} on the cluster failed — wrong outputs root, or prepare_remote was "
            f"never run? ({exc})"
        ) from exc
    dirs: set[str] = set()
    for line in out.splitlines():
        line = line.strip()
        if not line.endswith("/record.json"):
            continue
        rel = line[len(root):].lstrip("/")
        if "/" not in rel:  # a stray root-level record.json is not a run dir
            continue
        dirs.add(rel.rsplit("/", 1)[0])
    return dirs


def remote_reject_files(
    remote_outputs_root: str, runner: Callable[[list[str]], str]
) -> set[str]:
    """POSIX relpaths of every node-side reject MARKER on the cluster (P9): flat JSON files under
    any ``_rejects/`` dir (written atomically by ``run_one._write_reject_marker``). Same loud
    missing-root behavior as :func:`remote_completed_dirs` (the pull calls that first anyway)."""
    root = remote_outputs_root.rstrip("/")
    try:
        out = runner(["find", root, "-path", "*/_rejects/*.json", "-type", "f"])
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"listing reject markers under {root} on the cluster failed ({exc})"
        ) from exc
    rels: set[str] = set()
    for line in out.splitlines():
        line = line.strip()
        if not line.endswith(".json"):
            continue
        rel = line[len(root):].lstrip("/")
        if "_rejects/" not in rel:
            continue
        rels.add(rel)
    return rels


def _default_fetch(host: str, remote_outputs_root: str) -> Fetch:
    """Production transport: remote ``tar -cf -`` | ssh | local ``tar -xf -`` into staging.

    check=True on BOTH ends — ssh exits nonzero on a dropped connection and tar -x errors on a
    truncated stream ("Unexpected EOF in archive") — so a torn pull fails loud here rather than
    leaving a silently short mirror. The remote side is POSIX-quoted; the local tar runs with
    cwd=staging (no -C: Windows bsdtar/GNU-tar path-flavor quirks).
    """
    from src.cluster.submit import ssh_base

    root = remote_outputs_root.rstrip("/")

    def _fetch(relpaths: list[str], staging: Path) -> None:
        remote_cmd = (
            "tar -C " + shlex.quote(root) + " -cf - "
            + " ".join(shlex.quote(p) for p in relpaths)
        )
        ssh = subprocess.Popen([*ssh_base(host), remote_cmd], stdout=subprocess.PIPE)
        try:
            subprocess.run(
                ["tar", "-xf", "-"], stdin=ssh.stdout, check=True, timeout=3600,
                cwd=str(staging),
            )
        finally:
            if ssh.stdout is not None:
                ssh.stdout.close()
        if ssh.wait(timeout=300) != 0:
            raise subprocess.CalledProcessError(ssh.returncode, "ssh tar -cf - (remote)")

    return _fetch


def pull_archive(
    remote_outputs_root: str,
    local_root: str | Path,
    *,
    host: str = "myriad",
    runner: Callable[[list[str]], str] | None = None,
    fetch: Fetch | None = None,
    chunk: int = 150,
    progress: Callable[[int, int], None] | None = None,
) -> int:
    """Pull every remote-complete run dir the local mirror lacks; return how many were pulled.

    EXACT incremental: the run-dir diff (immutable records) is the transfer list. Each chunk is
    fetched into ``<local_root>/.pull_tmp`` and every dir is moved into the mirror ONLY after
    its record.json is verified present — the local archive never contains a torn dir, even if
    the process is killed mid-extract (stale staging is swept on the next call and never counts
    as completed). ``chunk`` bounds the remote argv length (~150 relpaths ≈ 12 KB, far under
    ARG_MAX) and keeps each pipe short and restartable.
    """
    from src.cluster.submit import ssh_runner

    local = Path(local_root)
    local.mkdir(parents=True, exist_ok=True)
    staging = local / _STAGING
    if staging.exists():  # a previous pull died mid-extract — its content is untrusted
        shutil.rmtree(staging)
    runner = runner or ssh_runner(host)
    fetch = fetch or _default_fetch(host, remote_outputs_root)

    remote = remote_completed_dirs(remote_outputs_root, runner)
    have = {
        p.parent.relative_to(local).as_posix()
        for p in local.rglob("record.json")
        if _STAGING not in p.parts
    }
    missing = sorted(remote - have)
    # P9: reject MARKERS ride the same pull (flat immutable JSON files under _rejects/) so the
    # driver can abandon deterministic node-side rejects without waiting out requeue rounds.
    rej_have = {
        p.relative_to(local).as_posix()
        for p in local.rglob("_rejects/*.json")
        if _STAGING not in p.parts
    }
    rej_missing = sorted(remote_reject_files(remote_outputs_root, runner) - rej_have)
    if not missing and not rej_missing:
        return 0

    # P14: a big pull is MANY chunked pipes (each up to an hour) — report per-chunk progress so
    # the driver can heartbeat mid-pull instead of looking hung to the sentinel. Best-effort.
    n_chunks = -(-len(missing) // chunk) + -(-len(rej_missing) // chunk)
    chunks_done = 0

    def _tick() -> None:
        nonlocal chunks_done
        chunks_done += 1
        if progress is not None:
            try:
                progress(chunks_done, n_chunks)
            except Exception:  # noqa: BLE001 — observability must never break the pull
                pass

    for i in range(0, len(missing), chunk):
        batch = missing[i : i + chunk]
        staging.mkdir(parents=True, exist_ok=True)
        fetch(batch, staging)
        for rel in batch:
            src = staging / rel
            if not (src / "record.json").is_file():
                raise RuntimeError(
                    f"pulled dir {rel!r} arrived without record.json — torn transfer; the "
                    f"local mirror was left untouched for it"
                )
            dest = local / rel
            if dest.exists():
                continue  # landed by an earlier overlapping pull — keep the committed copy
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
        shutil.rmtree(staging, ignore_errors=True)
        _tick()

    for i in range(0, len(rej_missing), chunk):
        batch = rej_missing[i : i + chunk]
        staging.mkdir(parents=True, exist_ok=True)
        fetch(batch, staging)
        for rel in batch:
            src = staging / rel
            if not src.is_file():
                raise RuntimeError(
                    f"pulled reject marker {rel!r} missing after extract — torn transfer"
                )
            dest = local / rel
            if dest.exists():
                continue  # markers are effectively immutable — keep the committed copy
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
        shutil.rmtree(staging, ignore_errors=True)
        _tick()
    return len(missing) + len(rej_missing)


def completed_run_ids(local_root: str | Path) -> set[str]:
    """Every run_id with a committed record under ``local_root`` (recursive; layout-agnostic).

    Staging content (``.pull_tmp`` — a torn pull's leftovers) is EXCLUDED: a record is complete
    only once it has been moved whole into the mirror proper.
    """
    root = Path(local_root)
    if not root.is_dir():
        return set()
    return {
        p.parent.name for p in root.rglob("record.json") if _STAGING not in p.parts
    }


def permanent_reject_ids(local_root: str | Path) -> set[str]:
    """Run_ids with a PERMANENT node-side reject marker in the mirror (P9): the deterministic
    validation-reject class the driver abandons immediately (no requeue rounds — same-source
    retry is provably futile). Transient markers (``permanent: false``) are diagnostics only;
    torn/unreadable markers are skipped (that spec just keeps the normal bounded retry)."""
    root = Path(local_root)
    if not root.is_dir():
        return set()
    ids: set[str] = set()
    for p in root.rglob("_rejects/*.json"):
        if _STAGING in p.parts:
            continue
        try:
            row = json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 — a torn marker must not sink the poll cycle
            continue
        if row.get("permanent"):
            ids.add(str(row.get("run_id") or p.stem))
    return ids


def spec_run_id(spec: dict[str, Any]) -> str:
    """The run_id a spec will archive under (search: candidate_id; test: run_id)."""
    rid = spec.get("run_id") or spec.get("candidate_id")
    if not rid:
        raise KeyError(f"spec carries neither run_id nor candidate_id: {sorted(spec)}")
    return str(rid)


def pending_specs(
    all_specs: list[dict[str, Any]], local_root: str | Path
) -> list[dict[str, Any]]:
    """The COMPACTED-RESUME diff: specs whose run_ids are not yet in the archive.

    2026-07-19 (35-agent audit, CONFIRMED critical): completion truth is scoped to each spec's
    OWN archive sub-root, NOT the whole mirror. Test run_ids are bare ``{arm}-s{seed}``
    (``test_leg.py``), so a disjoint-root invocation — the H3 C5 single-shot (``test_h3_singleshot/``)
    or a ``--root-suffix`` re-search — reuses run_ids like ``distributional-s0`` that ALSO exist
    under the headline ``test/`` root. A mirror-wide diff would see the headline's record, mark the
    H3/re-search unit "done", never submit its training, and leave the disjoint archive EMPTY — a
    silently fabricated H3 null. Grouping by sub-root (the ``archive_root`` basename: ``test`` vs
    ``test_h3_singleshot`` vs ``search`` vs ``search_<suffix>``) restores disjointness; a spec with
    no ``archive_root`` falls back to the mirror-wide check (unchanged behaviour)."""
    local_root = Path(local_root)
    done_by_subroot: dict[str, set[str]] = {}
    out: list[dict[str, Any]] = []
    for s in all_specs:
        sub = Path(str(s.get("archive_root", ""))).name
        if sub not in done_by_subroot:
            done_by_subroot[sub] = completed_run_ids(local_root / sub if sub else local_root)
        if spec_run_id(s) not in done_by_subroot[sub]:
            out.append(s)
    return out
