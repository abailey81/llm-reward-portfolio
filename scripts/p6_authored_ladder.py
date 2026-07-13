"""P6 pilot — the authored-winner convergence ladder ON MYRIAD (docs/PILOT_BATTERY_2026-07-11.md §P6).

Closes the R74 blind spot from the cluster side, fast: the frozen convergence dossier measured
budget-flatness on ONE hand-written reward (``differential_sharpe``); this array measures it on the
two ARCHIVED LLM-authored prototype winners, {100k, 200k, 400k} x CRN seeds {0,1,2} x 2 rewards
= 18 independent tasks — wall-clock ~= the slowest single task (~65 min at 400k on a V100) plus
queue wait, vs ~21 h serial on the laptop. The laptop ``learning_curve.py --reward-source`` ladder
runs the SAME (reward, budget, seed) grid concurrently: together they are a cross-substrate parity
exhibit, and they answer complementary questions — the laptop replicates the R74 dossier protocol
(held-out eval-IQM, comparable to the frozen curve); this array records the campaign's own
SELECTION metric (validation DSR ``val_fitness``), i.e. "would anything selection-relevant improve
past B*?" in the units that decide the campaign.

PARITY: every spec is built by the campaign's own ``assemble_cluster_inputs`` + ``_search_spec``
and executed on-node by the certified ``parallel.train_candidate`` via ``run_one`` — nothing is
reimplemented. Train/val windows only; the sealed test leg is read by nothing here. Keyless
(pass A / stub designer): the rewards are already authored.

Usage:
    python scripts/p6_authored_ladder.py --submit            # build 18 specs + jobscript, push, qsub
    python scripts/p6_authored_ladder.py --build-only        # local validation, no ssh
    python scripts/p6_authored_ladder.py --pull              # pull records + per-budget summary
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # repo root: `scripts.` + `src.` importable

BUDGETS = [100_000, 200_000, 400_000]
SEEDS = [0, 1, 2]  # CRN: shared across budgets AND rewards (paired comparisons throughout)
SOLO_STEPS_PER_SEC = 102.2  # G1 anchor (job 764154, V100-PCIE-32GB, pack=1) — walltime scaling
REWARDS = {  # label -> archived authored winner (Sonnet prototype, val-fitness argmax per arm)
    "p6dist": "outputs/prototype/distributional/distributional-g3-c0/reward.py",
    "p6scal": "outputs/prototype/scalar/scalar-g7-c3/reward.py",
}
BATCH = "p6ladder"


def build_specs(remote_root: str, local_out: str, budgets: list[int]) -> list[dict[str, Any]]:
    """Search-leg specs via the campaign's own assembly (one assemble per budget)."""
    from scripts.run_campaign_cluster import assemble_cluster_inputs
    from src.cluster.campaign import _search_spec

    specs: list[dict[str, Any]] = []
    for budget in budgets:
        inputs = assemble_cluster_inputs(
            arms=["distributional"], seeds=[0], output_dir=local_out, synthetic=False,
            train_steps=budget, n_trials=30, candidates=1, generations=1, search_seed=0,
            embargo=21, pass_mode="A", provider="stub", llm_cfg=None, resume=False,
        )
        opts = inputs["opts"]
        for label, path in REWARDS.items():
            source = Path(path).read_text(encoding="utf-8")
            if not source.strip():
                raise ValueError(f"empty reward source: {path}")
            for seed in SEEDS:
                o = dict(opts)
                o["seed"] = int(seed)
                cid = f"{label}-b{budget}-s{seed}"
                specs.append(_search_spec(label, source, cid, o,
                                          f"P6 authored-winner ladder ({path})", 0,
                                          f"{remote_root}/outputs/search"))
    return specs


PLANNING_STEPS_PER_SEC = 25.0  # planning FLOOR, revised DOWN 2026-07-13: job 774923 (800k steps)
# was h_rt-killed at its full 6 h (qacct failed=37, ru_wallclock 21,612 s) ⇒ that node sustained
# UNDER 37 st/s — worse than the previous worst measurement (51). Two successive downward
# surprises (102 anchor → 51 → <37) say co-tenancy has a heavier tail than any point estimate;
# 25 st/s prices the observed floor with margin. h_rt is a LIMIT, not a reservation — the only
# cost of generosity is backfill placement, and these report-only rungs prefer certainty.


def _auto_h_rt(budgets: list[int]) -> str:
    """Walltime = slowest rung at the WORST measured rate + overhead, x1.3, floored at 3 h."""
    hours = max(3.0, (max(budgets) / PLANNING_STEPS_PER_SEC + 900) / 3600.0 * 1.3)
    return f"{int(hours) + (1 if hours % 1 else 0)}:0:0"


def build_batch(remote_root: str, gold_dir: str, local_out: str, *, pool: str, cores: int,
                budgets: list[int], batch: str) -> Path:
    """Write task_N.json + the jobscript into the local batch dir; return it."""
    from src.cluster.jobscript import render_jobscript, write_jobscript
    from src.cluster.spec_io import write_specs

    specs = build_specs(remote_root, local_out, budgets)
    batch_dir = Path(local_out) / "batches" / batch
    n = write_specs(specs, batch_dir)  # strict-JSON guard runs here
    js = render_jobscript(batch, n, remote_root, gold_dir, pool=pool, pack=1,
                          cores=cores, h_rt=_auto_h_rt(budgets), apptainer_sif="$HOME/python311.sif")
    write_jobscript(js, batch_dir / f"{batch}.sh")
    print(f"[p6] built {n} specs + jobscript at {batch_dir} (h_rt {_auto_h_rt(budgets)})")
    return batch_dir


def submit(remote_root: str, gold_dir: str, local_out: str, *, host: str, pool: str, cores: int,
           budgets: list[int], batch: str) -> str:
    from src.cluster.submit import prepare_remote, push_batch, qsub, ssh_runner

    runner = ssh_runner(host)
    batch_dir = build_batch(remote_root, gold_dir, local_out, pool=pool, cores=cores,
                            budgets=budgets, batch=batch)
    prepare_remote(remote_root, [batch], runner)
    push_batch(batch_dir, f"{remote_root.rstrip('/')}/specs", host=host)
    job = qsub(f"{remote_root.rstrip('/')}/specs/{batch}/{batch}.sh", runner)
    print(f"[p6] submitted {batch} as job {job} ({len(budgets) * len(REWARDS) * len(SEEDS)} tasks, pool {pool})")
    return job


def submit_singles(remote_root: str, gold_dir: str, local_out: str, *, host: str, pool: str,
                   cores: int, budgets: list[int], batch: str,
                   exclude: set[str], skip_done: bool) -> list[str]:
    """Submit each (winner, budget, seed) spec as its OWN 1-task array (2026-07-13 recovery).

    WHY: the scheduler's serialization policy holds an array's tail tasks (``snx=1``) and has
    twice PURGED pending tails outright (the rehearsal arrays 07-08; the p6ext800b/1600b tails
    07-13 — qacct confirms tasks 2-6 left no trace). Single-task arrays have NO pending tail to
    purge and every task is immediately eligible — the many-small-arrays lever (runbook §2b).
    ``exclude`` drops named candidate ids (e.g. one currently RUNNING elsewhere); ``skip_done``
    drops specs whose record already exists in the local mirror (idempotent re-entry).
    """
    from src.cluster.jobscript import render_jobscript, write_jobscript
    from src.cluster.spec_io import write_specs
    from src.cluster.submit import prepare_remote, push_batch, qsub, ssh_runner

    runner = ssh_runner(host)
    specs = build_specs(remote_root, local_out, budgets)
    done: set[str] = set()
    if skip_done:
        for rec_path in Path(local_out).glob("search/**/record.json"):
            done.add(rec_path.parent.name)
    todo = [s for s in specs
            if s["candidate_id"] not in exclude and s["candidate_id"] not in done]
    skipped = len(specs) - len(todo)
    if skipped:
        print(f"[p6] singles: skipping {skipped} spec(s) (excluded/already archived)")
    jobs: list[str] = []
    names: list[str] = []
    for i, spec in enumerate(todo, start=1):
        name = f"{batch}{i:02d}"
        names.append(name)
        batch_dir = Path(local_out) / "batches" / name
        write_specs([spec], batch_dir)
        h_rt = _auto_h_rt([int(spec.get("train_steps") or max(budgets))])
        js = render_jobscript(name, 1, remote_root, gold_dir, pool=pool, pack=1,
                              cores=cores, h_rt=h_rt, apptainer_sif="$HOME/python311.sif")
        write_jobscript(js, batch_dir / f"{name}.sh")
    prepare_remote(remote_root, names, runner)
    for name, spec in zip(names, todo):
        push_batch(Path(local_out) / "batches" / name, f"{remote_root.rstrip('/')}/specs")
        job = qsub(f"{remote_root.rstrip('/')}/specs/{name}/{name}.sh", runner)
        jobs.append(job)
        print(f"[p6] single {name} = job {job}: {spec['candidate_id']}")
    print(f"[p6] {len(jobs)} single-task arrays submitted (pool {pool})")
    return jobs


def pull_and_summarize(remote_root: str, local_out: str, *, host: str) -> None:
    """Pull node-written records and print the per-(reward, budget) seed summary of val_fitness."""
    from src.cluster.poll import pull_archive

    local_root = Path(local_out)
    n = pull_archive(f"{remote_root.rstrip('/')}/outputs", local_root, host=host)
    rows: dict[tuple[str, int], list[float]] = {}
    for rec_path in sorted(local_root.glob("search/**/record.json")):
        rec = json.loads(rec_path.read_text(encoding="utf-8"))
        cid = str(rec.get("candidate_id", ""))
        if not cid.startswith("p6"):
            continue
        label, b_tok, _s_tok = cid.split("-")
        vf = (rec.get("metrics") or {}).get("val_fitness")
        if vf is not None:
            rows.setdefault((label, int(b_tok[1:])), []).append(float(vf))
    print(f"[p6] pulled {n} records; {sum(len(v) for v in rows.values())} P6 rows")
    print(f"{'reward':8} {'budget':>8} {'n':>2}  val_fitness (per CRN seed)")
    for (label, budget) in sorted(rows):
        vals = rows[(label, budget)]
        print(f"{label:8} {budget:>8,} {len(vals):>2}  " + "  ".join(f"{v:+.4f}" for v in sorted(vals)))
    out = {f"{label}|{budget}": sorted(vals) for (label, budget), vals in rows.items()}
    (local_root / "p6_summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser(description="P6: authored-winner convergence ladder on Myriad.")
    p.add_argument("--submit", action="store_true")
    p.add_argument("--build-only", action="store_true", help="Build specs + jobscript locally; no ssh.")
    p.add_argument("--pull", action="store_true")
    p.add_argument("--host", default="myriad")
    p.add_argument("--remote-root", default="~/Scratch/p6ladder")
    p.add_argument("--gold-dir", default="/acfs/users/ucestes/gold")
    p.add_argument("--output-dir", default="outputs/p6ladder")
    p.add_argument("--pool", default="EF")
    p.add_argument("--cores-per-task", type=int, default=2)
    p.add_argument("--budgets", default=",".join(str(b) for b in BUDGETS),
                   help="Comma list of step budgets (extension rungs, e.g. 800000,1600000).")
    p.add_argument("--batch-name", default=BATCH, help="SGE batch name (extension arrays need their own).")
    p.add_argument("--singles", action="store_true",
                   help="Submit each (winner,budget,seed) spec as its OWN 1-task array — no "
                        "pending tail for the scheduler policy to purge (2026-07-13 recovery).")
    p.add_argument("--exclude", default="",
                   help="Comma list of candidate ids to drop (e.g. one running elsewhere).")
    p.add_argument("--skip-done", action="store_true",
                   help="Drop specs whose record already exists in the local mirror.")
    args = p.parse_args()
    budgets = [int(x) for x in str(args.budgets).split(",") if x.strip()]

    from src.utils.preload import preload
    preload(strict=True)

    remote_root = args.remote_root
    if remote_root.startswith("~"):
        if args.build_only:
            from src.cluster.submit import expand_remote
            remote_root = expand_remote(remote_root, "/home/USER")  # documented stub (no ssh)
        else:
            from src.cluster.submit import expand_remote, remote_home, ssh_runner
            remote_root = expand_remote(remote_root, remote_home(ssh_runner(args.host)))

    if args.build_only:
        build_batch(remote_root, args.gold_dir, args.output_dir, pool=args.pool,
                    cores=args.cores_per_task, budgets=budgets, batch=args.batch_name)
        return 0
    if args.submit and args.singles:
        submit_singles(remote_root, args.gold_dir, args.output_dir, host=args.host,
                       pool=args.pool, cores=args.cores_per_task, budgets=budgets,
                       batch=args.batch_name,
                       exclude={x.strip() for x in args.exclude.split(",") if x.strip()},
                       skip_done=bool(args.skip_done))
        return 0
    if args.submit:
        submit(remote_root, args.gold_dir, args.output_dir, host=args.host,
               pool=args.pool, cores=args.cores_per_task, budgets=budgets, batch=args.batch_name)
        return 0
    if args.pull:
        pull_and_summarize(remote_root, args.output_dir, host=args.host)
        return 0
    p.error("pass one of --submit / --build-only / --pull")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
