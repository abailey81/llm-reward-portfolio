"""Cluster campaign entry point — run the headline campaign on UCL Myriad (PLAN §7 / §12 B-A1).

This is the thin, professional GLUE that turns the certified orchestrator (``src.cluster.campaign``)
into a runnable campaign: it ASSEMBLES the campaign config by reusing the SAME helpers the laptop
``run_campaign.run_headline_campaign`` uses (``load_config`` / panel loader / ``resolve_windows`` /
``run_prototype._agent_cfg`` / ``build_parallel_opts``), so the cluster runs byte-identical science —
there is no second, drift-prone config path. It then wires :func:`build_cluster_run` and calls
:func:`run_campaign_on_cluster`.

The GO-time runsheet (PLAN §12 B-B) precedes this: VPN up, ``~/.ssh/config`` username filled + key
installed, repo pushed (``git archive HEAD | ssh myriad tar -x -C ~/llmrp``), gold staged to ACFS,
``scripts/myriad/build_env.sh`` run + G1 cert passed. THEN, on the laptop driver::

    # validate the wiring WITHOUT touching the cluster (renders one jobscript + one gen's specs):
    python scripts/run_campaign_cluster.py --dry-run --synthetic
    # the real run (over the VPN):
    python scripts/run_campaign_cluster.py \
        --remote-root ~/Scratch/llmrp --gold-dir /acfs/users/<u>/llmrp-inputs \
        --arms distributional scalar scalar_cvar5 ... --seeds 0-402 --resume

Nothing here runs a confirmatory unit on the laptop — training is 100% on Myriad; authoring/reflection
/selection are laptop-side (keys are laptop-only, R10). The laptop track remains the certified default
until Tamer says GO; this script is inert unless invoked.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any

_LOG = logging.getLogger("run_campaign_cluster")


def _parse_seeds(spec: str) -> list[int]:
    """Parse ``--seeds`` as a comma list and/or ``a-b`` inclusive ranges (e.g. ``0-402`` or ``0,1,5``)."""
    out: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return sorted(set(out))


def assemble_cluster_inputs(
    *,
    arms: list[str],
    seeds: list[int],
    output_dir: str | Path,
    synthetic: bool,
    train_steps: int | None,
    n_trials: int,
    candidates: int,
    generations: int,
    search_seed: int,
    embargo: int,
    pass_mode: str,
    provider: str,
    llm_cfg: dict[str, Any] | None,
    resume: bool,
) -> dict[str, Any]:
    """Assemble ``(opts_for, seeds, test_leg_kwargs, frozen_root, agent_cfg, panel_descriptor)``.

    A pure, cluster-free function (loads the panel on the DRIVER only to resolve the integer windows
    the nodes reuse) — MIRRORS ``run_headline_campaign``'s synthetic/gold + window + agent-config +
    opts assembly so the two paths cannot drift. Unit-testable without a cluster.
    """
    import sys as _sys

    _sys.path.insert(0, str(Path(__file__).resolve().parent))  # scripts on path (codebase convention)
    from run_campaign import make_agent_trainer_factory, resolve_windows  # noqa: F401  (parity import)
    from run_prototype import _agent_cfg, build_parallel_opts

    from src.utils.config import cfg_get, load_config

    env_cfg = load_config("environment")
    inf_cfg = load_config("inference")
    lookback = int(env_cfg["state"]["lookback_days"])

    # Panel (driver-side, ONLY to derive the integer windows the nodes reuse) + the picklable
    # descriptor the on-node worker reloads from (mirror of run_headline_campaign 1424-1490).
    if synthetic:
        from src.data.synthetic import make_synthetic_panel

        panel = make_synthetic_panel(n_assets=30, n_days=7800, seed=0)
        panel_descriptor: dict[str, Any] = {"synthetic": True, "n_assets": 30, "n_days": 7800}
    else:
        from src.data.loaders import load_gold_panel

        span = cfg_get(cfg_get(cfg_get(inf_cfg, "splits", {}), "evaluation", {}), "span",
                       ["2020-01-01", "2026-06-30"])
        panel = load_gold_panel(phase="development", end=str(span[1]),
                                verify_checksum=True, validate=True).panel
        panel_descriptor = {"synthetic": False, "phase": "development", "end": str(span[1]),
                            "on_missing": "liquidate_to_cash"}

    splits = cfg_get(inf_cfg, "splits", {})
    train_window, val_window, test_window = resolve_windows(panel, lookback, splits, embargo=embargo)

    # Agent config (matched-compute B*): prototype base + campaign overlay (mirror 1522-1540).
    agent_cfg = _agent_cfg(load_config("prototype"), train_steps)
    for _k, _v in dict(cfg_get(load_config("campaign"), "agent", {}) or {}).items():
        agent_cfg[_k] = _v

    # Search opts — the SAME build_parallel_opts the laptop search uses (mirror _search_parallel_arm).
    proto = load_config("prototype")
    structural = {"agent": agent_cfg, "reward_family": cfg_get(proto, "reward_family", {}),
                  "data": cfg_get(proto, "data", {})}
    opts = build_parallel_opts(
        structural, env_cfg, llm_block=(llm_cfg if llm_cfg is not None else cfg_get(proto, "llm", {})),
        train_steps=int(agent_cfg["train_steps_per_candidate"]), n_trials=n_trials, synthetic=synthetic,
        seed=search_seed, candidates=candidates, generations=generations, pass_mode=pass_mode,
        provider=provider, resume=resume,
    )

    frozen_root = Path(output_dir) / "frozen"
    test_leg_kwargs = dict(
        panel_descriptor=panel_descriptor, env_cfg=env_cfg, agent_cfg=agent_cfg,
        train_window=train_window, val_window=val_window, test_window=test_window,
        embargo=embargo, lookback=lookback,
    )
    return {
        "opts_for": (lambda _arm: opts),  # opts are arm-independent; the arm is a run_search_arm param
        "opts": opts, "seeds": seeds, "test_leg_kwargs": test_leg_kwargs,
        "frozen_root": frozen_root, "agent_cfg": agent_cfg, "panel_descriptor": panel_descriptor,
        "windows": (train_window, val_window, test_window),
    }


def _dry_run(inputs: dict[str, Any], arms: list[str], *, remote_root: str, gold_dir: str,
             pool: str, pack: int) -> int:
    """Validate wiring WITHOUT the cluster: build one generation's specs (fails loud on a
    non-JSON-serializable config, BUG-3) + render one jobscript. No ssh, no submit."""
    import tempfile

    from src.cluster.campaign import _search_spec
    from src.cluster.jobscript import render_jobscript
    from src.cluster.spec_io import write_specs

    opts = inputs["opts"]
    arm = arms[0]
    cpg = max(1, int(opts["candidates"]) // max(1, int(opts["generations"])))
    specs = [_search_spec(arm, f"# stub reward {k}\n", f"{arm}-g0-c{k}", opts,
                          "PROMPT", 0, f"{remote_root}/outputs/search") for k in range(cpg)]
    with tempfile.TemporaryDirectory() as td:
        n = write_specs(specs, Path(td) / f"{arm}_g0")  # strict-JSON guard runs here
    js = render_jobscript(f"{arm}_g0", cpg, remote_root, gold_dir, pool=pool, pack=pack)
    _LOG.info("DRY-RUN OK: %d arms, %d seeds; one gen = %d JSON-clean specs; jobscript renders (%d lines)",
              len(arms), len(inputs["seeds"]), n, len(js.splitlines()))
    print(f"[dry-run] wiring valid — {len(arms)} arms, {len(inputs['seeds'])} seeds, "
          f"{cpg} candidates/gen, windows={inputs['windows']}, pool={pool}, pack={pack}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run the headline campaign on UCL Myriad.")
    p.add_argument("--arms", nargs="+", default=["distributional", "scalar"],
                   help="Arms to run (the frozen roster at GO; default is the two headline arms).")
    p.add_argument("--baselines", nargs="*", default=None,
                   help="H1 hand-designed baseline REWARD_CANON names (fixed rewards, no search; "
                        "flood the pool from minute 0). Omit to skip the H1 leg.")
    p.add_argument("--seeds", default="0-567", help="Test seeds for the NON-tiered path: comma list "
                   "and/or a-b ranges. Default = the full E1 ladder [0..567]. IGNORED under --tiered "
                   "(the config seed schema drives the tiers).")
    p.add_argument("--search-seed", type=int, default=0)
    p.add_argument("--candidates", type=int, default=30)
    p.add_argument("--generations", type=int, default=6)
    p.add_argument("--train-steps", type=int, default=None, help="B* (default: campaign.yaml).")
    p.add_argument("--n-trials", type=int, default=30)
    p.add_argument("--embargo", type=int, default=21)
    p.add_argument("--pass-mode", default="A")
    p.add_argument("--provider", default="stub")
    p.add_argument("--synthetic", action="store_true", help="Synthetic panel (dry-run / cert only).")
    p.add_argument("--output-dir", default="outputs/campaign_cluster")
    p.add_argument("--resume", action="store_true")
    p.add_argument(
        "--tiered", action="store_true",
        help="Run the Stage-1 C-LADDER (config/campaign.yaml 'seeds' schema): C0 canary -> C1-C3 "
        "priority-laddered core (n=30 floor, H2 pair-adjacent) -> EFFECT-BLIND review gate -> C4 "
        "uniform-n round-robin sweep in assurance blocks (90/95/99).",
    )
    p.add_argument(
        "--approve-tier1", action="store_true",
        help="Create the TIER1_APPROVED file (after reviewing the effect-blind integrity report) so "
        "a tiered --resume run proceeds past the C3 review gate into the C4 sweep.",
    )
    p.add_argument(
        "--no-review-gate", action="store_true",
        help="Tiered mode: skip the C3 review stop (NOT recommended for the real campaign).",
    )
    p.add_argument(
        "--hold-at-gate", action="store_true",
        help="Tiered mode: STOP at the C3 gate for a manual eyeball of the effect-blind integrity "
        "report even when execution health is green (default: auto-proceed on green, stop only on a "
        "real execution defect). Release with --approve-tier1 --resume.",
    )
    p.add_argument(
        "--canary", nargs="*", default=None,
        help="C0 canary baseline names (default: the first 3 of --baselines). Pass an empty list "
        "to skip the canary (NOT recommended).",
    )
    p.add_argument("--dry-run", action="store_true", help="Validate wiring; no ssh, no submit.")
    # Cluster wiring
    p.add_argument("--host", default="myriad")
    p.add_argument("--remote-root", default="~/Scratch/llmrp", help="Scratch working root on Myriad.")
    p.add_argument("--gold-dir", default="~/Scratch/llmrp/inputs", help="Staged gold dir on Myriad.")
    p.add_argument("--pool", default="EF", help="Confirmatory GPU pool (device homogeneity).")
    p.add_argument("--pack", type=int, default=1, help="§15 GPU packing (concurrent trainings/job).")
    p.add_argument("--poll-secs", type=float, default=600.0)
    p.add_argument("--max-author-calls", type=int, default=None, help="Hard authoring spend cap.")
    return p


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    args = build_parser().parse_args(argv)

    inputs = assemble_cluster_inputs(
        arms=list(args.arms), seeds=_parse_seeds(args.seeds), output_dir=args.output_dir,
        synthetic=bool(args.synthetic), train_steps=args.train_steps, n_trials=args.n_trials,
        candidates=args.candidates, generations=args.generations, search_seed=args.search_seed,
        embargo=args.embargo, pass_mode=args.pass_mode, provider=args.provider, llm_cfg=None,
        resume=bool(args.resume),
    )
    if args.dry_run:
        return _dry_run(inputs, list(args.arms), remote_root=args.remote_root, gold_dir=args.gold_dir,
                        pool=args.pool, pack=args.pack)

    from src.cluster.campaign import build_cluster_run, run_campaign_on_cluster

    remote_root = args.remote_root.rstrip("/")
    # local_archive_root == output_dir so the pulled mirror is output_dir/{search,test,frozen}/... —
    # EXACTLY the laptop campaign's layout, so analyze_campaign reads the cluster archive identically
    # (parity). Batches/logs live under output_dir/batches, disjoint from the archive dirs.
    run = build_cluster_run(
        remote_root=remote_root, remote_outputs_root=f"{remote_root}/outputs",
        local_batch_root=f"{args.output_dir}/batches", local_archive_root=args.output_dir,
        gold_dir=args.gold_dir, host=args.host, pool_confirmatory=args.pool, pack=args.pack,
        poll_secs=args.poll_secs, max_author_calls=args.max_author_calls, concurrent=True,
    )
    baselines = list(args.baselines) if args.baselines else None
    if args.tiered:
        from src.cluster.campaign import run_campaign_tiered
        from src.utils.config import load_config

        if args.approve_tier1:
            approval = Path(args.output_dir) / "TIER1_APPROVED"
            approval.parent.mkdir(parents=True, exist_ok=True)
            approval.write_text("approved via --approve-tier1\n", encoding="utf-8")
            _LOG.info("review gate approved: %s", approval)
        canary = args.canary if args.canary is not None else (baselines or [])[:3]
        seeds_cfg = load_config("campaign").get("seeds")  # the schema (list -> one tier; tiered -> ladder)
        out = run_campaign_tiered(
            list(args.arms), inputs["opts_for"], seeds_cfg, run,
            test_leg_kwargs=inputs["test_leg_kwargs"], frozen_root=inputs["frozen_root"],
            baseline_names=baselines, canary_baselines=(canary or None),
            review_gate=not args.no_review_gate, hold_at_gate=bool(args.hold_at_gate),
            resume=bool(args.resume),
        )
        if out.get("awaiting_review"):
            reason = out.get("gate", "review")
            why = ("a REAL execution defect (a short/incomplete unit or device inhomogeneity) — "
                   "inspect and fix it before releasing" if reason == "RED-execution-health"
                   else "you asked to hold for a manual eyeball (--hold-at-gate)")
            print(f"[campaign] C3 FLOOR COMPLETE, gate STOPPED: {why}. Review the EFFECT-BLIND report "
                  f"({out['integrity_report']}), then re-run with --approve-tier1 --resume. "
                  f"(On green health without --hold-at-gate the gate auto-proceeds — no manual wait.)")
            return 0
        ok = bool(out.get("ok"))
        print(f"[campaign] TIERED {'OK' if ok else 'INCOMPLETE'} — "
              f"{out['n_tiers']} tiers, sizes {out['tier_sizes']}")
        return 0 if ok else 1

    results = run_campaign_on_cluster(
        list(args.arms), inputs["opts_for"], inputs["seeds"], run,
        test_leg_kwargs=inputs["test_leg_kwargs"], frozen_root=inputs["frozen_root"],
        baseline_names=baselines, resume=bool(args.resume),
    )
    ok = all(r.get("ok") for r in results.values())
    for arm, r in results.items():
        _LOG.info("[%s] ok=%s %s", arm, r.get("ok"),
                  {k: v for k, v in r.items() if k not in ("search", "test")})
    print(f"[campaign] {'ALL OK' if ok else 'INCOMPLETE'} — "
          f"{sum(1 for r in results.values() if r.get('ok'))}/{len(results)} arms")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
