"""Render the §14.6 Myriad jobscript (Grid Engine array) — the ONE template every batch uses.

Encodes every researched rule/lever: ``#!/bin/bash -l`` (R13), per-core ``-l mem`` (R13),
``$TMPDIR`` gold staging (§14.2), ``-r y`` native resume (§14.1), the ``-p`` intra-user
priority ladder (§14.3), ``-hold_jid`` pipelining, organized ``-o`` logs, ``umask 077`` (§14.5),
the per-task epilogue ledger line (§14.4), and §15 GPU packing via ``run_one --pack``.

ALWAYS write the rendered text to disk via :func:`write_jobscript` (V11 audit fix): the driver
runs on Windows, where a bare ``write_text`` translates ``\\n`` to ``\\r\\n`` — and a CRLF
shebang (``#!/bin/bash -l\\r``) makes qsub/exec fail on the cluster. The classic landmine,
killed at the API level.

PATH CONTRACT (2026-07-11 incident fix): every path handed to :func:`render_jobscript` must be
**tilde-free**, and ``remote_root`` must be **absolute**. ``~`` is expanded by NOTHING this
template touches: SGE ``#$`` directives (``-wd``/``-o``) expand neither ``~`` nor ``$HOME``
(an invalid ``-wd`` puts the whole array in ``Eqw`` at dispatch, where UCL's cleanup deletes it
with NO qacct record — the observed fate of the 2026-07-11 rehearsal), double-quoted bash
strings keep ``~`` literal (``mkdir -p "~/..."`` creates a directory named ``~``; the Apptainer
``--bind`` list fails on the nonexistent literal path), and Python never expands ``~`` in
``PYTHONPATH``. ``$HOME`` IS allowed in the shell-only paths (``gold_dir``/``venv``/
``repo_root``/``apptainer_sif``: they appear only inside the bash body, where double quotes
expand variables) but NOT in ``remote_root`` (directive sink). Callers expand user-supplied
``~`` against the REAL remote home via ``submit.remote_home`` + ``submit.expand_remote``.
"""
from __future__ import annotations

from pathlib import Path

__all__ = ["render_jobscript", "write_jobscript"]

_TEMPLATE = """#!/bin/bash -l
#$ -N {name}
{gpu_line}#$ -pe smp {cores}
#$ -l mem={mem_per_core}
#$ -l tmpfs={tmpfs}
#$ -l h_rt={h_rt}
{pool_line}#$ -notify
#$ -r y
#$ -p {priority}
#$ -t 1-{n_tasks} -tc {tc}
{hold_line}#$ -wd {remote_root}
#$ -o {remote_root}/logs/{name}/$TASK_ID.o -j y
umask 077
mkdir -p "{remote_root}/logs/{name}" "{remote_root}/ledger"
# The Apptainer run below bind-mounts {gold_dir}; a NON-EXISTENT bind source makes Apptainer
# FATAL at container creation BEFORE any python runs (caught live 2026-07-24: the synthetic
# rehearsal crashed rc=255/secs=1 every dispatch on a missing inputs/ dir). mkdir -p makes the
# mount always succeed: a synthetic run needs no gold; a REAL run whose gold is genuinely absent
# then fails LOUD in the loader (a clear "panel not found") instead of a cryptic mount FATAL.
mkdir -p "{gold_dir}"
# Gold artifacts staged to node-local tmpfs (§14.2) — LOAD-BEARING via the loaders' staged-dir
# hook (V7 closed 2026-07-07): LLM_RP_GOLD_STAGED_DIR is honoured per file by its canonical
# <name>_<suffix>.parquet filename (wrong-suffix staging = filename miss -> canonical fallback)
# and staged bytes are still checksum-verified against the frozen manifest. If the tmpfs copy
# fails, the ACFS input dir itself is exported instead — gold reads keep working either way
# (the repo-default data/gold/ does not exist on a node; licensed gold is never in git).
mkdir -p "$TMPDIR/gold"
if cp "{gold_dir}"/*.parquet "$TMPDIR/gold/"; then
  export LLM_RP_GOLD_STAGED_DIR="$TMPDIR/gold"
else
  export LLM_RP_GOLD_STAGED_DIR="{gold_dir}"
fi
export TORCH_HOME="$TMPDIR/torch"
{env_line}
# Make `src` importable: the job's -wd is {remote_root} (Scratch, where logs/specs/outputs live),
# but the CODE is at {repo_root} and the venv does NOT pip-install the repo, so without this
# `python -m src.cluster.run_one` dies with ModuleNotFoundError on EVERY task. $HOME auto-binds
# into Apptainer, so this also works inside the container.
export PYTHONPATH="{repo_root}:${{PYTHONPATH:-}}"
# P17/A4-F10 (2026-07-13 audit): the epilogue line rides an EXIT trap so a SOFT kill (SGE sends
# SIGUSR2/SIGTERM ahead of the h_rt SIGKILL) still records the task — the old echo-after-the-run
# missed exactly the walltime-killed/node-failed cases the ledger exists for. RC=126 marks
# "trapped before the run returned"; a hard SIGKILL remains unrecordable (forensics via qacct).
RC=126
{apptainer_guard}GPUINFO=$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null | head -1)
# `ts` (epoch seconds at task exit) is REQUIRED, not decorative (deep review 2026-07-26, #56):
# killswitch.classify_task_deaths judges an ADMIN KILL by burstiness — N deaths across M hosts
# inside a 300s window. Without a timestamp its window admits every row ever written, so a whole
# campaign's scattered benign failures read as one burst and the killswitch retreats + blocks
# submission. MEASURED: 12 ordinary deaths spread over 20 days classified as `admin_kill`.
# The `|| echo 0` is NOT defensive noise: a bare `$(date +%s)` that yields nothing emits a
# `"ts":` with NO VALUE — invalid JSON — and `read_epilogue` is torn-line tolerant, so it
# silently DISCARDS the row. The death record is then lost, defeating the very detector `ts` was
# added for, and the loss is invisible. Reproduced 2026-07-26: `bash.exe` invoked directly (no
# MSYS PATH) has no `date`, and the epilogue test failed to parse at exactly that column. A
# numeric fallback keeps the row PARSEABLE and merely un-timed, which the window treats as old.
trap 'echo "{{\\"task\\":${{SGE_TASK_ID}},\\"host\\":\\"$(hostname)\\",\\"gpu\\":\\"${{GPUINFO}}\\",\\"rc\\":${{RC}},\\"secs\\":${{SECONDS}},\\"ts\\":$(date +%s 2>/dev/null || echo 0)}}" >> "{remote_root}/ledger/{name}.epilogue.jsonl"' EXIT
trap 'exit 143' TERM USR2
{launcher} -m {entry_module} --spec "{remote_root}/specs/{name}/task_${{SGE_TASK_ID}}.json" --pack {pack}
RC=$?
exit $RC
"""


def render_jobscript(
    name: str,
    n_tasks: int,
    remote_root: str,
    gold_dir: str,
    *,
    pool: str = "EF",
    tc: int = 38,
    priority: int = 0,
    hold_jid: str | None = None,
    pack: int = 1,
    cores: int | None = None,
    mem_per_core: str = "4G",
    tmpfs: str = "15G",
    h_rt: str | None = None,
    venv: str = "$HOME/venvs/llmrp",
    repo_root: str = "$HOME/llmrp",
    apptainer_sif: str | None = None,
    device: str = "cuda",
    entry_module: str = "src.cluster.run_one",
) -> str:
    """Return the §14.6 jobscript text for one array batch.

    Defaults implement the researched decisions: EF/V100 pool, ``-tc`` = the full pool width,
    priority 0 (the caller passes the §14.3 ladder value: 0 / -100 / -200 / -500), cores scale
    with the pack (4 per concurrent training), walltime scales with the pack wave (1h30 per
    §15's one-wave shape, 3h for pack=1's conservative margin).

    ``device`` selects the LANE (2026-07-26, the CPU-lane build — dossier §0-PRE):

    * ``"cuda"`` (default, unchanged): requests ``-l gpu=1`` + ``-ac allow=<pool>``.
    * ``"cpu"``: NO ``gpu`` request and NO pool ``allow`` (a CPU job places on any node type, which
      is the whole point — the d pool alone is 10,584 cores vs 74 GPUs cluster-wide), ``--nv`` is
      dropped from the Apptainer line, and ``cores`` defaults to ONE PER PACKED TRAINING (a
      training is single-threaded; the 4-per-training GPU sizing would over-request 4x).
      Pass ``pool`` explicitly to pin a CPU node type (e.g. ``"D"``/``"B"``/``"T"``).

    Two guards encode live-probed Myriad facts (2026-07-26); both fail LOUD at render:

    * **``-pe smp 36`` is an EXCLUSIVE WHOLE-NODE request.** UCL's JSV silently adds ``exb=true``
      + ``exd=true`` when the core count equals a full node, so the job needs an ENTIRELY EMPTY
      node and starves (job ``cpucurve_d`` sat queued 2+ days). 35 is clean; 36 is not.
    * **Apptainer is not on every node** (``node-d00a-230`` had none): the venv python lives INSIDE
      the ``.sif``, so a missing container means ``rc=127`` after the slot was already granted. The
      rendered script probes for it and exits with a named error instead.

    ``entry_module`` selects the on-node entry point. The default trains the task's specs; pass
    ``"src.cluster.bayes_chain"`` to run the WHOLE bayes_opt GP chain inside one job instead of
    dispatching its 30 sequential proposals as 30 separate array-of-1 jobs (each paying a queue
    wait). That packaging change is what makes the GPU lane worth having for the campaign's
    critical path — see ``src/cluster/bayes_chain.py`` and ``src/cluster/lanes.py``.
    """
    if pack < 1:
        raise ValueError(f"pack must be >= 1, got {pack}")
    device = str(device).lower()
    if device not in ("cuda", "cpu"):
        raise ValueError(f"device must be 'cuda' or 'cpu', got {device!r}")
    if priority > 0:
        raise ValueError("SGE -p only accepts <= 0 for users (self-deprioritization)")
    # PATH CONTRACT (2026-07-11 rehearsal incident — see the module docstring). Fail LOUD here,
    # at the single render choke point, instead of silently shipping a script whose array Eqw-dies
    # at dispatch (deleted with no qacct trace) or whose every task dies on a literal-~ path.
    if not remote_root.startswith("/"):
        raise ValueError(
            f"remote_root must be an ABSOLUTE path (got {remote_root!r}): it lands in the SGE "
            "'#$ -wd'/'#$ -o' directives, which expand neither '~' nor '$HOME' — an invalid -wd "
            "sends the whole array to Eqw at dispatch. Expand via submit.remote_home/expand_remote."
        )
    for label, val in (
        ("remote_root", remote_root), ("gold_dir", gold_dir), ("venv", venv),
        ("repo_root", repo_root), ("apptainer_sif", apptainer_sif or ""),
    ):
        if "~" in val:
            raise ValueError(
                f"{label} contains a literal '~' (got {val!r}): nothing in the jobscript expands "
                "it (SGE directives, double-quoted bash strings, PYTHONPATH). Pass an absolute "
                "path, or '$HOME/...' for shell-only paths; expand user input via "
                "submit.remote_home + submit.expand_remote."
            )
        if ":" in val.split("=", 1)[-1][:12] and (":/" in val or ":\\" in val):
            # 2026-07-12 incident: Git Bash (MSYS) path conversion rewrote a laptop CLI arg
            # '/acfs/users/.../gold' into 'C:/Program Files/Git/acfs/...' BEFORE Python saw it —
            # every task of the batch then died at the Apptainer mount (rc=255, 1s). A Windows
            # drive-letter path can never be valid on the cluster: fail at render, not on-node.
            # (Launcher-side fix: prefix the command with MSYS_NO_PATHCONV=1, or keep POSIX paths
            # in argparse DEFAULTS rather than shell argv.)
            raise ValueError(
                f"{label} looks like a Windows drive-letter path (got {val!r}) — Git Bash MSYS "
                "path conversion has mangled a POSIX argument. Launch with MSYS_NO_PATHCONV=1 "
                "or avoid passing absolute POSIX paths through the shell."
            )
    # CPU trainings are single-threaded (the 2026-07-25 profile: ~97% is the SAC gradient update,
    # and multi-thread BLAS would change float reduction order = break CRN determinism), so the
    # GPU lane's 4-cores-per-training sizing would over-request 4x on CPU.
    cores = cores if cores is not None else ((1 if device == "cpu" else 4) * pack)
    if int(cores) == 36 or (device == "cpu" and int(cores) >= 36):
        raise ValueError(
            f"cores={cores}: a full-node core request makes UCL's JSV add the EXCLUSIVE complexes "
            "(exb/exd/ext), so the job needs an ENTIRELY EMPTY node and starves — live-probed "
            "2026-07-26 (job cpucurve_d, '-pe smp 36', queued 2+ days). Use <= 35 (35 still gets "
            "97% of a node); 8 places best. See docs/MYRIAD_EXPERT_DOSSIER_2026-07-24.md §0-PRE M2."
        )
    h_rt = h_rt if h_rt is not None else ("3:0:0" if pack == 1 else "1:30:0")
    from src.cluster.submit import sanitize_name

    name = sanitize_name(name)
    hold_line = f"#$ -hold_jid {hold_jid}\n" if hold_jid else ""
    gold_dir = gold_dir.rstrip("/")
    # V3 audit fix: the launcher is PART OF THE RUN LINE — the old apptainer branch set a shell
    # variable the run line never used (containerized jobs would have crashed on bare python).
    # A CPU lane requests no GPU and pins no GPU pool; pass `pool` explicitly to pin a CPU node
    # type (D/B/T) if a contrast ever needs CPU-model homogeneity beyond the seed-block scheme.
    gpu_line = "" if device == "cpu" else "#$ -l gpu=1\n"
    pool_line = f"#$ -ac allow={pool}\n" if (pool and (device == "cuda" or pool not in ("", "EF"))) else ""
    if apptainer_sif is None:
        env_line = f"source {venv}/bin/activate"
        launcher = "python"
    else:
        # G1 audit fix (2026-07-10): the container image is BARE python — every dep lives in
        # the venv on $HOME (auto-bound), so the run line must call the VENV interpreter
        # through the container, not the container's own `python`. And $TMPDIR is NOT
        # auto-bound: without the explicit --bind, the staged-gold dir and TORCH_HOME would
        # not exist inside the container and gold reads would fall back to a data/gold that
        # is absent on nodes. gold_dir is bound too, for the cp-failed ACFS fallback path.
        env_line = f"# containerized: {apptainer_sif} (venv python called through the container)"
        # --nv injects the host NVIDIA stack; it is meaningless (and noise) on a CPU node.
        nv = "" if device == "cpu" else "--nv "
        launcher = (
            f'apptainer exec {nv}--bind "$TMPDIR,{gold_dir}" {apptainer_sif} {venv}/bin/python'
        )
    # Apptainer is NOT installed on every node (node-d00a-230, 2026-07-26): the venv python lives
    # INSIDE the .sif, so a missing container burns the granted slot with a bare rc=127 and no
    # diagnosis. Fail with a NAMED error the ledger can count instead.
    apptainer_guard = "" if apptainer_sif is None else (
        'command -v apptainer >/dev/null 2>&1 || { '
        'echo "FATAL apptainer missing on $(hostname) - cannot start the containerized venv" >&2; '
        'exit 127; }\n'
    )
    return _TEMPLATE.format(
        name=name, n_tasks=n_tasks, remote_root=remote_root.rstrip("/"),
        gold_dir=gold_dir, pool=pool, tc=tc, priority=priority,
        hold_line=hold_line, pack=pack, cores=cores, mem_per_core=mem_per_core,
        tmpfs=tmpfs, h_rt=h_rt, env_line=env_line, launcher=launcher,
        repo_root=repo_root.rstrip("/"), gpu_line=gpu_line, pool_line=pool_line,
        apptainer_guard=apptainer_guard, entry_module=entry_module,
    )


def write_jobscript(text: str, path: str | Path) -> Path:
    """Write a rendered jobscript with FORCED LF endings (V11: Windows driver, Linux cluster).

    ``newline=""`` disables the platform translation that would otherwise smuggle ``\\r`` into
    the shebang and every ``#$`` directive. The bytes on disk are exactly what qsub executes.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return p
