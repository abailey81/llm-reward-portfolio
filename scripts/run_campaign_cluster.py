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
    # 2026-07-13 audit: the LAPTOP-calibrated thermal governor (88C hi on the RTX-4050) must not
    # ship onto V100 nodes — a co-tenanted card crossing 88C would pause trainings up to 1800s
    # each inside an already-tight h_rt. Nodes have datacenter thermal management; the governor is
    # a laptop concern. Result-neutral (wall-clock-only knob).
    agent_cfg["thermal_guardian"] = None

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


def _write_campaign_summary(output_dir: str | Path, inputs: dict[str, Any], *,
                            freeze_stamp: dict[str, Any] | None,
                            extra: dict[str, Any],
                            filename: str = "campaign_summary.json") -> None:
    """P7 (2026-07-13 pre-spend audit): the cluster mirror had NO ``campaign_summary.json``, so
    ``analyze_campaign.py`` silently skipped the DeMiguel benchmark floor (it reads ``test_window``
    from the summary) and the sentinel/monitor had no terminal-state sentinel to key off. Mirrors
    ``run_campaign``'s summary keys (windows + freeze stamp + gold-panel provenance) and REUSES its
    atomic writer. Written ONLY on terminal completion — never at the C3 review stop, where the
    watcher would misread the file as "campaign done"."""
    import sys as _sys

    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run_campaign import _write_summary_atomic

    train_window, val_window, test_window = inputs["windows"]
    if inputs["panel_descriptor"].get("synthetic"):
        provenance: dict[str, Any] = {"synthetic": True}
    else:
        try:
            from capture_env import _gold_panel_provenance

            provenance = _gold_panel_provenance()
        except Exception as exc:  # noqa: BLE001 — provenance is best-effort; the descriptor still names the panel
            print(f"[cluster] gold-panel provenance unavailable ({type(exc).__name__}: {exc}); "
                  "recording the panel descriptor instead", flush=True)
            provenance = dict(inputs["panel_descriptor"])
    summary = {
        "source": "run_campaign_cluster",
        "train_window": list(train_window),
        "val_window": list(val_window),
        "test_window": list(test_window),
        "freeze": freeze_stamp if freeze_stamp is not None else {"enforced": False, "frozen": None},
        "gold_panel": provenance,
        **extra,
    }
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    _write_summary_atomic(Path(output_dir), summary, filename=filename)


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
    p.add_argument("--apptainer-sif", default="~/python311.sif",
                   help="Container image the node trains through (the cluster venv is built INSIDE it; "
                        "RHEL7 glibc is too old for the cu124 wheels natively). Empty string = native venv.")
    p.add_argument("--llm-from", choices=["campaign", "prototype"], default="campaign",
                   help="Which config's `llm` block authors the rewards (2026-07-13 pre-spend audit "
                        "fix: llm_cfg was hardcoded None, silently inheriting prototype.yaml's block "
                        "— the WRONG MODEL for the confirmatory run). Default `campaign` = "
                        "config/campaign.yaml's Opus 4.8 block (the campaign OWNS its author, "
                        "ADR-035). Rehearsals/prototypes pass `prototype` EXPLICITLY.")
    p.add_argument("--batch-tag", default=None,
                   help="Per-run batch-name namespace (2026-07-11d bug fix): the driver's "
                        "double-submit guard matches queued jobs by NAME across the whole user "
                        "queue, so concurrent runs sharing arm names collide (the later run adopts "
                        "the earlier run's array and polls forever). Tag every concurrent run, "
                        "e.g. --batch-tag pm.")
    p.add_argument("--seed-pool-blocks", default=None, metavar="POOL:LO-HI,...",
                   help='Device-stratified seed blocks (RATIFIED 2026-07-11c), e.g. '
                        '"EF:0-283,L:284-567": whole seed blocks run on different GPU pools while '
                        'every CRN pair (same seed, all arms) stays device-homogeneous — a '
                        'randomized-block design that adds the A100 pools to confirmatory C. '
                        'Blocks must be disjoint; unassigned seeds fall back to --pool.')
    p.add_argument("--h-rt", default=None, metavar="H:M:S",
                   help="Per-array walltime request. Default: AUTO-SIZED from the measured aggregate "
                        "throughput curve at worst-node contention (steps x pack / (0.5 x F-curve) + "
                        "overhead, x1.3) — NEVER a per-training number: at pack=5 the per-training "
                        "wall stretches ~2x under GPU time-slicing and a per-training h_rt would "
                        "walltime-kill every packed task (the 2026-07-12 p6ext incident class).")
    p.add_argument("--cores-per-training", type=int, default=None,
                   help="CPU cores requested per packed training (total job cores = this × --pack). "
                        "Default (None) keeps the jobscript's 4×pack. Myriad GPU-node CORES are the "
                        "binding scheduling constraint, so lowering this (e.g. 2) makes packed jobs place.")
    p.add_argument("--poll-secs", type=float, default=600.0)
    p.add_argument("--max-author-calls", type=int, default=None, help="Hard authoring spend cap.")
    p.add_argument("--allow-unfrozen", action="store_true",
                   help="Dev escape hatch (P19, 2026-07-13 audit): downgrade the freeze "
                        "verify-or-refuse gate to a WARNING. ONLY for rehearsals/prototypes "
                        "(e.g. the pm2 prototype) — the real confirmatory campaign runs frozen.")
    p.add_argument("--root-suffix", default=None, metavar="NAME",
                   help="C6-class namespace guard (2026-07-13): ANY report-only re-search "
                        "invocation (e.g. the D1 search-saturation curve levels) MUST pass a "
                        "suffix — its archives go to search_<NAME>/, test_<NAME>/, frozen_<NAME>/ "
                        "and its batch names are prefixed <NAME>_. Sharing the confirmatory roots "
                        "would let the compacted resume ADOPT headline run_ids and fabricate the "
                        "exhibit (the P4 hazard class). Lowercase [a-z0-9_]+ only.")
    p.add_argument("--priority", type=int, default=None,
                   help="SGE -p override for THIS invocation's arrays (default: the mode's "
                        "ladder value — confirmatory 0/-100; report-only invocations should "
                        "pass -200 per §14.3).")
    p.add_argument("--h3-singleshot", action="store_true",
                   help="C5 (P4 closed 2026-07-13): run the pre-registered H3 SINGLE-SHOT control "
                        "on the cluster — the distributional arm at generations=1 (no reflection), "
                        "same candidate budget + agent config + seeds, archived to the SEPARATE "
                        "*_h3_singleshot/ roots at -p -100. A separate invocation from the "
                        "headline campaign (shares --output-dir; roots are disjoint by "
                        "construction; batch names force-prefixed h3ss_). Forces "
                        "--arms distributional and --generations from campaign.yaml's "
                        "h3_singleshot_generations.")
    return p


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    # Load .env -> os.environ so the authoring key (ANTHROPIC_API_KEY / OPENROUTER_API_KEY) is available
    # to the LAPTOP-side driver that authors before shipping specs (parity with run_campaign.py:2111).
    # Without this, real-authoring (--pass-mode B) crashes with a "key unset" RuntimeError.
    from src.cluster.submit import expand_remote, remote_home, ssh_runner
    from src.utils.config import load_config as _load_config
    from src.utils.env import load_env

    load_env()
    args = build_parser().parse_args(argv)

    # P19 (2026-07-13 pre-spend audit): the cluster entry point had NO freeze gate at all — the
    # laptop campaign REFUSES to launch on an unfrozen/drifted pre-registration (verify-or-refuse,
    # run_campaign.py enforce_freeze) but the Myriad path would happily author + train the whole
    # confirmatory campaign against an unfrozen design. Mirror the laptop semantics exactly: the
    # keyless --dry-run is exempt; --allow-unfrozen downgrades to a warning (rehearsals only).
    import sys as _sys

    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run_campaign import CampaignNotFrozenError, enforce_freeze

    freeze_stamp: dict[str, Any] | None = None
    if not args.dry_run:
        try:
            freeze_stamp = enforce_freeze(allow_unfrozen=bool(args.allow_unfrozen))
        except CampaignNotFrozenError as exc:
            raise SystemExit(f"[run_campaign_cluster] {exc}") from exc

    # C5 (P4): the H3 single-shot control is its OWN invocation — force its fixed shape BEFORE
    # the guards/assembly so the spend cap, divisibility check, and dry-run all see the truth.
    if args.h3_singleshot:
        if args.tiered:
            raise SystemExit("--h3-singleshot and --tiered are SEPARATE invocations (C5 vs "
                             "C1-C4) — run the H3 control after (or alongside) the ladder.")
        from src.utils.config import cfg_get as _h3cg
        args.arms = ["distributional"]
        args.generations = int(_h3cg(_load_config("campaign"), "h3_singleshot_generations", 1) or 1)
        _LOG.info("C5 H3 single-shot: arms forced to ['distributional'], generations=%d",
                  args.generations)

    # P17/A3-F12 (2026-07-13 audit): --hold-at-gate is meaningless without the review gate —
    # the hold would be SILENTLY ignored and C4 would launch unreviewed.
    if args.hold_at_gate and args.no_review_gate:
        raise SystemExit("--hold-at-gate requires the review gate, but --no-review-gate disables "
                         "it — drop one of the two flags.")
    # P17/A3-F9 (2026-07-13 audit): the search authors candidates//generations per generation
    # (floor division, laptop-parity). A non-divisible pair silently DROPS the remainder from
    # the budget — e.g. a D1 curve level would train fewer candidates than its x-axis claims.
    if args.candidates % max(1, args.generations) != 0:
        _dropped = args.candidates - (args.candidates // max(1, args.generations)) * max(1, args.generations)
        raise SystemExit(
            f"--candidates {args.candidates} is not divisible by --generations "
            f"{args.generations}: {_dropped} candidate(s) would be SILENTLY dropped from the "
            f"budget (candidates-per-generation is floor division, laptop-parity). Pick a "
            f"divisible pair (e.g. --generations 1 for small D1 curve levels)."
        )

    # ---- 2026-07-13 PRE-SPEND AUDIT GUARDS (all fail LOUD before any submission/authoring) ---- #
    from src.utils.config import cfg_get as _cfg_get
    llm_cfg = None  # None -> assemble falls back to prototype.yaml (the legacy rehearsal path)
    if args.llm_from == "campaign":
        llm_cfg = dict(_cfg_get(_load_config("campaign"), "llm", {}) or {})
        if not llm_cfg:
            raise SystemExit("--llm-from campaign but config/campaign.yaml has no `llm` block")
    # F1 (agent audit, CRITICAL): pass-mode B with the DEFAULT provider=stub silently authors the
    # whole "Opus" campaign with the keyless stub and completes "successfully". Derive the provider
    # from the resolved llm block when possible (campaign.yaml carries provider: anthropic), else
    # fail loud — a real-spend run must never fall through to the stub.
    if args.pass_mode.upper() == "B" and args.provider == "stub":
        _blk = llm_cfg if llm_cfg is not None else _cfg_get(_load_config("prototype"), "llm", {})
        _blk_provider = str(_cfg_get(_blk, "provider", "") or "")
        if _blk_provider and _blk_provider != "stub":
            args.provider = _blk_provider
            _LOG.info("provider DERIVED from the %s llm block: %s", args.llm_from, args.provider)
        else:
            raise SystemExit(
                "pass-mode B with provider=stub: a real-spend run would silently author with the "
                "keyless stub designer. Pass --provider explicitly (or --llm-from campaign, whose "
                "block carries provider: anthropic)."
            )
    # F2 (agent audit, CRITICAL): restarting WITHOUT --resume re-authors every candidate (paid)
    # while archive-truth training discards the new sources — the full authoring budget wasted.
    if not args.resume and not args.dry_run:
        _dirty = list(Path(args.output_dir).glob("search/*/*/record.json"))
        if _dirty:
            raise SystemExit(
                f"{len(_dirty)} search records already exist under {args.output_dir} but --resume "
                "was not passed. A fresh start here RE-AUTHORS every candidate (paid API calls) and "
                "then DISCARDS the new sources (training is archive-truth). Pass --resume, or move "
                "the output dir aside if you truly want a fresh run."
            )
    # Provider<->model consistency: authoring with a mismatched pair either 400s (burning retries)
    # or silently authors with the wrong family — both unacceptable at real spend.
    if args.pass_mode.upper() == "B" and args.provider != "stub":
        _block = llm_cfg if llm_cfg is not None else _cfg_get(_load_config("prototype"), "llm", {})
        _model = str(_cfg_get(_block, "model_snapshot", ""))
        if args.provider == "anthropic" and not _model.startswith("claude"):
            raise SystemExit(f"provider=anthropic but the {args.llm_from} llm block's model is "
                             f"{_model!r} — wrong-model spend guard (pass --llm-from correctly)")
        if args.provider == "openrouter" and _model.startswith("claude"):
            raise SystemExit(f"provider=openrouter with model {_model!r} — the campaign authors "
                             "Opus via the NATIVE anthropic provider (ADR-035)")

    inputs = assemble_cluster_inputs(
        arms=list(args.arms), seeds=_parse_seeds(args.seeds), output_dir=args.output_dir,
        synthetic=bool(args.synthetic), train_steps=args.train_steps, n_trials=args.n_trials,
        candidates=args.candidates, generations=args.generations, search_seed=args.search_seed,
        embargo=args.embargo, pass_mode=args.pass_mode, provider=args.provider, llm_cfg=llm_cfg,
        resume=bool(args.resume),
    )
    if args.dry_run:
        # No ssh in a dry-run: expand a leading '~' against a documented STUB home so the render
        # is representative and passes the tilde-free jobscript contract (2026-07-11 incident).
        # 2026-07-13 (launch readiness): the dry-run now ALSO validates the two launch-critical
        # configs that previously only failed at real launch — the seed-pool block spec and the
        # tiered seeds schema — so the keyless pre-flight step 3 exercises the WHOLE launch shape.
        if args.seed_pool_blocks:
            from src.cluster.campaign import parse_seed_pool_blocks as _pspb
            _blocks = _pspb(args.seed_pool_blocks)  # fail-loud on overlap/shape
            _LOG.info("dry-run: seed-pool blocks OK — %s",
                      {p: len(sd) for p, sd in _blocks})
        if args.tiered:
            from src.utils.seeds import seed_tiers as _st
            _tiers = _st(_load_config("campaign").get("seeds"))  # fail-loud on a bad schema
            _LOG.info("dry-run: tiered seeds schema OK — %d tiers, sizes %s",
                      len(_tiers), [len(t) for t in _tiers])
        stub = "/home/USER"
        return _dry_run(inputs, list(args.arms),
                        remote_root=expand_remote(args.remote_root, stub),
                        gold_dir=expand_remote(args.gold_dir, stub),
                        pool=args.pool, pack=args.pack)

    from src.cluster.campaign import build_cluster_run, parse_seed_pool_blocks, run_campaign_on_cluster

    # 2026-07-11 incident fix: '~' survives LITERALLY through the quoted ssh runner, SGE '#$'
    # directives, and the jobscript's quoted strings (the rehearsal arrays Eqw-died at dispatch
    # and were admin-purged without a qacct trace). Resolve the REAL remote home once and expand
    # every user-supplied remote path before anything is rendered, pushed, or submitted.
    if any(str(p).startswith("~") for p in (args.remote_root, args.gold_dir, args.apptainer_sif or "")):
        home = remote_home(ssh_runner(args.host))
        args.remote_root = expand_remote(args.remote_root, home)
        args.gold_dir = expand_remote(args.gold_dir, home)
        if args.apptainer_sif:
            args.apptainer_sif = expand_remote(args.apptainer_sif, home)
        _LOG.info("remote '~' paths expanded against home=%s", home)

    # ---- 2026-07-13 pre-spend audit: safe DEFAULTS for the two silent money sinks ---- #
    # (a) Spend cap: --max-author-calls defaulted to None = the spend_guard was a NO-OP on an
    #     unattended run. Default it to 2x the structural authoring bound + slack, logged.
    _LLM_ARMS = {"distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled"}
    if args.max_author_calls is None and args.pass_mode.upper() == "B" and args.provider != "stub":
        n_llm = len(set(args.arms) & _LLM_ARMS)
        args.max_author_calls = max(30, 2 * n_llm * int(args.candidates) + 60)
        _LOG.info("spend cap DEFAULTED: max_author_calls=%d (2 x %d LLM arms x %d candidates + 60 "
                  "slack); override with --max-author-calls", args.max_author_calls, n_llm,
                  args.candidates)
    # (b) Walltime: the renderer's pack>1 default (1:30) was sized for 50k probes — a pack-5 B*
    #     task needs ~2.4h on a contended node and would be h_rt-KILLED after burning the GPU
    #     (the p6ext800/1600 incident class). Size on the measured aggregate curve at its worst
    #     (x0.5 contention) + overhead + 30% margin.
    if args.h_rt is None:
        _agg_clean = {1: 102.0, 2: 133.0, 3: 220.0, 4: 240.0, 5: 253.0, 8: 257.0}
        agg = 0.5 * _agg_clean.get(int(args.pack), 253.0)
        steps = int(args.train_steps or (_load_config("campaign").get("agent") or {})
                    .get("train_steps_per_candidate") or 200000)
        secs = (steps * int(args.pack) / agg + 1200.0) * 1.3
        hours = int(secs // 3600) + 1
        args.h_rt = f"{hours}:0:0"
        _LOG.info("walltime DEFAULTED: h_rt=%s (steps=%d, pack=%d, worst-agg=%.0f steps/s); "
                  "override with --h-rt", args.h_rt, steps, args.pack, agg)

    remote_root = args.remote_root.rstrip("/")
    # local_archive_root == output_dir so the pulled mirror is output_dir/{search,test,frozen}/... —
    # EXACTLY the laptop campaign's layout, so analyze_campaign reads the cluster archive identically
    # (parity). Batches/logs live under output_dir/batches, disjoint from the archive dirs.
    run = build_cluster_run(
        remote_root=remote_root, remote_outputs_root=f"{remote_root}/outputs",
        local_batch_root=f"{args.output_dir}/batches", local_archive_root=args.output_dir,
        gold_dir=args.gold_dir, host=args.host, pool_confirmatory=args.pool, pack=args.pack,
        poll_secs=args.poll_secs, max_author_calls=args.max_author_calls, concurrent=True,
        apptainer_sif=(args.apptainer_sif or None), cores_per_training=args.cores_per_training,
        h_rt=(args.h_rt or None),
        seed_pool_blocks=(parse_seed_pool_blocks(args.seed_pool_blocks)
                          if args.seed_pool_blocks else None),
        batch_tag=(args.batch_tag or None),
    )
    baselines = list(args.baselines) if args.baselines else None

    if args.root_suffix:
        # C6-class guard: namespaced roots + batch names for report-only re-search invocations.
        import re as _re
        from dataclasses import replace as _dc_replace

        if not _re.fullmatch(r"[a-z0-9_]+", args.root_suffix):
            raise SystemExit(f"--root-suffix {args.root_suffix!r} must be lowercase [a-z0-9_]+")
        if args.h3_singleshot:
            raise SystemExit("--h3-singleshot manages its own roots — do not combine it with "
                             "--root-suffix.")
        _sfx = args.root_suffix
        _base_rb = run.run_batch

        def _sfx_run_batch(specs, name, **kw):
            return _base_rb(specs, f"{_sfx}_{name}", **kw)

        run = _dc_replace(run, run_batch=_sfx_run_batch,
                          search_subdir=f"search_{_sfx}", test_subdir=f"test_{_sfx}")
        inputs["frozen_root"] = Path(args.output_dir) / f"frozen_{_sfx}"
        _LOG.info("root-suffix %r: archives -> search_%s/ test_%s/ frozen_%s/; batches %s_*",
                  _sfx, _sfx, _sfx, _sfx, _sfx)

    if args.h3_singleshot:
        # C5: the H3 single-shot control — disjoint *_h3_singleshot roots, h3ss_ batch names,
        # -p -100. Its sentinel is its OWN file (h3_singleshot_summary.json): clobbering the
        # HEADLINE campaign_summary.json in the shared output dir would fool the watcher/analyze.
        from src.cluster.campaign import run_h3_singleshot_on_cluster

        out = run_h3_singleshot_on_cluster(
            inputs["opts"], inputs["seeds"], run,
            test_leg_kwargs=inputs["test_leg_kwargs"],
            frozen_root=Path(args.output_dir) / "frozen_h3_singleshot",
            search_seed=args.search_seed, resume=bool(args.resume),
        )
        ok = bool(out.get("ok"))
        _write_campaign_summary(args.output_dir, inputs, freeze_stamp=freeze_stamp, extra={
            "h3_singleshot": True, "all_arms_tested": ok, "exit_code": 0 if ok else 1,
            "winner_id": out.get("winner_id"),
        }, filename="h3_singleshot_summary.json")
        print(f"[campaign] H3 SINGLE-SHOT {'OK' if ok else 'INCOMPLETE'} — "
              f"winner={out.get('winner_id')} ({out.get('reason', 'tested at the campaign seeds')})")
        return 0 if ok else 1

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
        _write_campaign_summary(args.output_dir, inputs, freeze_stamp=freeze_stamp, extra={
            "tiered": True, "all_arms_tested": ok, "exit_code": 0 if ok else 1,
            "n_tiers": out.get("n_tiers"), "tier_sizes": out.get("tier_sizes"),
        })
        print(f"[campaign] TIERED {'OK' if ok else 'INCOMPLETE'} — "
              f"{out['n_tiers']} tiers, sizes {out['tier_sizes']}")
        return 0 if ok else 1

    results = run_campaign_on_cluster(
        list(args.arms), inputs["opts_for"], inputs["seeds"], run,
        test_leg_kwargs=inputs["test_leg_kwargs"], frozen_root=inputs["frozen_root"],
        baseline_names=baselines, resume=bool(args.resume),
        priority=(args.priority if args.priority is not None else 0),
    )
    ok = all(r.get("ok") for r in results.values())
    for arm, r in results.items():
        _LOG.info("[%s] ok=%s %s", arm, r.get("ok"),
                  {k: v for k, v in r.items() if k not in ("search", "test")})
    _write_campaign_summary(args.output_dir, inputs, freeze_stamp=freeze_stamp, extra={
        "tiered": False, "all_arms_tested": ok, "exit_code": 0 if ok else 1,
        "arms": {arm: bool(r.get("ok")) for arm, r in results.items()},
    })
    print(f"[campaign] {'ALL OK' if ok else 'INCOMPLETE'} — "
          f"{sum(1 for r in results.values() if r.get('ok'))}/{len(results)} arms")
    return 0 if ok else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
