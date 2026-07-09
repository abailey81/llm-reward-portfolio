"""Render the §14.6 Myriad jobscript (Grid Engine array) — the ONE template every batch uses.

Encodes every researched rule/lever: ``#!/bin/bash -l`` (R13), per-core ``-l mem`` (R13),
``$TMPDIR`` gold staging (§14.2), ``-r y`` native resume (§14.1), the ``-p`` intra-user
priority ladder (§14.3), ``-hold_jid`` pipelining, organized ``-o`` logs, ``umask 077`` (§14.5),
the per-task epilogue ledger line (§14.4), and §15 GPU packing via ``run_one --pack``.

ALWAYS write the rendered text to disk via :func:`write_jobscript` (V11 audit fix): the driver
runs on Windows, where a bare ``write_text`` translates ``\\n`` to ``\\r\\n`` — and a CRLF
shebang (``#!/bin/bash -l\\r``) makes qsub/exec fail on the cluster. The classic landmine,
killed at the API level.
"""
from __future__ import annotations

from pathlib import Path

__all__ = ["render_jobscript", "write_jobscript"]

_TEMPLATE = """#!/bin/bash -l
#$ -N {name}
#$ -l gpu=1
#$ -pe smp {cores}
#$ -l mem={mem_per_core}
#$ -l tmpfs={tmpfs}
#$ -l h_rt={h_rt}
#$ -ac allow={pool}
#$ -r y
#$ -p {priority}
#$ -t 1-{n_tasks} -tc {tc}
{hold_line}#$ -wd {remote_root}
#$ -o {remote_root}/logs/{name}/$TASK_ID.o -j y
umask 077
mkdir -p "{remote_root}/logs/{name}" "{remote_root}/ledger"
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
{launcher} -m src.cluster.run_one --spec "{remote_root}/specs/{name}/task_${{SGE_TASK_ID}}.json" --pack {pack}
RC=$?
GPUINFO=$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null | head -1)
echo "{{\\"task\\":${{SGE_TASK_ID}},\\"host\\":\\"$(hostname)\\",\\"gpu\\":\\"${{GPUINFO}}\\",\\"rc\\":${{RC}},\\"secs\\":${{SECONDS}}}}" >> "{remote_root}/ledger/{name}.epilogue.jsonl"
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
    venv: str = "~/venvs/llmrp",
    repo_root: str = "~/llmrp",
    apptainer_sif: str | None = None,
) -> str:
    """Return the §14.6 jobscript text for one array batch.

    Defaults implement the researched decisions: EF/V100 pool, ``-tc`` = the full pool width,
    priority 0 (the caller passes the §14.3 ladder value: 0 / -100 / -200 / -500), cores scale
    with the pack (4 per concurrent training), walltime scales with the pack wave (1h30 per
    §15's one-wave shape, 3h for pack=1's conservative margin).
    """
    if pack < 1:
        raise ValueError(f"pack must be >= 1, got {pack}")
    if priority > 0:
        raise ValueError("SGE -p only accepts <= 0 for users (self-deprioritization)")
    cores = cores if cores is not None else 4 * pack
    h_rt = h_rt if h_rt is not None else ("3:0:0" if pack == 1 else "1:30:0")
    from src.cluster.submit import sanitize_name

    name = sanitize_name(name)
    hold_line = f"#$ -hold_jid {hold_jid}\n" if hold_jid else ""
    # V3 audit fix: the launcher is PART OF THE RUN LINE — the old apptainer branch set a shell
    # variable the run line never used (containerized jobs would have crashed on bare python).
    if apptainer_sif is None:
        env_line = f"source {venv}/bin/activate"
        launcher = "python"
    else:
        env_line = f"# containerized: {apptainer_sif}"
        launcher = f"apptainer exec --nv {apptainer_sif} python"
    return _TEMPLATE.format(
        name=name, n_tasks=n_tasks, remote_root=remote_root.rstrip("/"),
        gold_dir=gold_dir.rstrip("/"), pool=pool, tc=tc, priority=priority,
        hold_line=hold_line, pack=pack, cores=cores, mem_per_core=mem_per_core,
        tmpfs=tmpfs, h_rt=h_rt, env_line=env_line, launcher=launcher,
        repo_root=repo_root.rstrip("/"),
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
