"""Shared + PARALLEL campaign TEST leg (the 180 winner re-runs).

The campaign's TEST stage trains the FROZEN winner at each of 30 seeds and touches the sealed
2018-2025 test leg EXACTLY ONCE per seed (``scripts/run_campaign.py::evaluate_winner_on_test``). Those
180 ``(winner × seed)`` runs are embarrassingly parallel — each reseeds the full stack, trains from
scratch, and rolls the test leg once, with NO reflection coupling — so they run across the device pool
via :func:`src.orchestration.parallel.run_recycling` for the max-throughput laptop campaign.

Three pieces, with their responsibilities split so the heavy worker stays out of the fast tests:

* :func:`build_test_record` — the SINGLE source of truth for the per-seed record schema, called by BOTH
  the serial ``evaluate_winner_on_test`` and the parallel worker so the two paths cannot drift. PURE
  (numpy + the inference Sharpe/CVaR only — no torch); unit-tested without a GPU.
* :func:`_test_seed_worker` — the spawn-process worker that reconstructs the heavy objects (panel,
  reward, env, trainer) from a picklable spec (mirroring ``parallel.train_candidate``) and replicates
  the serial per-seed body EXACTLY (the B1-B6 invariants documented on it). Verified by the live smoke.
* :func:`evaluate_winners_on_test_parallel` — the driver: applies the frozen/test desync guard once per
  winner, builds the ``(arm, seed)`` specs (skipping ``done_ids`` for ``--resume``), runs them through
  the device pool, and writes each ok record under ``test_root/<arm>/``. Its ``runner``/``worker``/
  ``write`` are injectable so the orchestration is fast-unit-tested with no spawn / no torch.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from src.orchestration.parallel import _FIXTURE, run_recycling

__all__ = ["build_test_record", "evaluate_winners_on_test_parallel"]


# --------------------------------------------------------------------------- #
# The shared record schema (pure; serial + parallel both call this)            #
# --------------------------------------------------------------------------- #
def build_test_record(
    *,
    winner: dict[str, Any],
    arm: str,
    seed: int,
    reward_hash: str,
    env_fp: Any,
    test_returns: Any,
    test_gross: Any = None,
    test_turnover: Any = None,
    popart_scale: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble the ONE archive record for a ``(winner, seed)`` TEST run.

    Byte-for-byte the record that ``evaluate_winner_on_test`` writes per seed: the raw per-step NET
    ``test_returns`` (+ its GROSS/TURNOVER decomposition when the bundle exposes ``test_series``, for the
    Rank-15 cost sweep's analytic re-pricing), ``test_sharpe`` (RAW — no Deflated-Sharpe correction at
    the test leg; the search-stage multiplicity is already consumed), ``test_cvar05``, the ``val_fitness``
    carried from the frozen winner, and ``frozen: True``. ``run_id = f"{arm}-s{seed}"`` is deterministic
    so ``--resume`` keys on it.
    """
    from src.inference.bootstrap import cvar, sharpe_ratio

    tr = np.asarray(test_returns, dtype=float)
    per_period_pnl = tr.tolist()
    val_fitness = float(winner.get("metrics", {}).get("val_fitness", float("nan")))

    metrics: dict[str, Any] = {
        "val_fitness": val_fitness,
        "test_sharpe": float(sharpe_ratio(tr)),
        "test_cvar05": float(cvar(tr, 0.05)),
        "test_returns": per_period_pnl,
        "per_period_pnl": per_period_pnl,
    }
    if test_gross is not None and test_turnover is not None:
        metrics["test_gross"] = np.asarray(test_gross, dtype=float).tolist()
        metrics["test_turnover"] = np.asarray(test_turnover, dtype=float).tolist()
    if popart_scale is not None:
        # T2.4: the realised PopArt scale (sigma_max/last) the FROZEN-winner critic saw at THIS seed, so
        # the per-seed cross-arm sigma distribution is auditable at the test leg too (mirrors the search leg).
        metrics["popart_scale"] = popart_scale

    return {
        "run_id": f"{arm}-s{int(seed)}",
        "arm": arm,
        "seed": int(seed),
        "fold": 0,
        "candidate_id": winner.get("candidate_id", f"{arm}-winner"),
        "generation": int(winner.get("generation", 0)),
        "reward_source": winner.get("reward_source", ""),
        "reward_source_hash": reward_hash,
        "feedback_block": winner.get("feedback_block", ""),
        "metrics": metrics,
        "wall_clock": 0.0,
        "env_fingerprint": env_fp,
        # Additive optional fields (OPTIONAL_FIELDS) — back-compatible with the results schema.
        "frozen": True,
        "test_returns": per_period_pnl,
        "per_period_pnl": per_period_pnl,
    }


# --------------------------------------------------------------------------- #
# The spawn-process worker (one (winner, seed) TEST run)                        #
# --------------------------------------------------------------------------- #
#: Process-local panel cache (workers are reused within a recycling batch; the panel-on-disk is frozen
#: + deterministic, so the worker's reload equals the main process's panel).
_TEST_PANEL_CACHE: dict[str, Any] = {}


def _load_test_panel(descriptor: dict[str, Any]) -> Any:
    """Load (and per-worker cache) the TEST-leg panel from a picklable descriptor.

    The panel is NOT pickled per spec (it is ~40 MB); the worker reloads it from the frozen gold parquet
    (deterministic given ``phase``/``end``/``on_missing``) or rebuilds the synthetic panel
    (``make_synthetic_panel(seed=0)``) — both identical to the panel the main process resolved windows on.
    """
    if descriptor.get("synthetic"):
        key = "syn"
    else:
        key = f"gold:{descriptor.get('phase')}:{descriptor.get('end')}:{descriptor.get('on_missing')}"
    if key in _TEST_PANEL_CACHE:
        return _TEST_PANEL_CACHE[key]
    if descriptor.get("synthetic"):
        from src.data.synthetic import make_synthetic_panel

        panel = make_synthetic_panel(n_assets=30, n_days=600, seed=0)
    else:
        from src.data.loaders import load_gold_panel

        panel = load_gold_panel(
            phase=str(descriptor.get("phase", "development")),
            end=str(descriptor.get("end")),
            on_missing=str(descriptor.get("on_missing", "liquidate_to_cash")),  # type: ignore[arg-type]
        ).panel
    _TEST_PANEL_CACHE[key] = panel
    return panel


def _test_seed_worker(spec: dict[str, Any]) -> dict[str, Any]:
    """Worker: train the FROZEN winner at ONE seed, roll the sealed test leg ONCE, return its record.

    Reconstructs the heavy objects (panel, reward, env, trainer) IN the spawn process from the picklable
    ``spec`` — mirroring ``parallel.train_candidate`` — because closures and the panel are not efficiently
    picklable per task. It replicates the serial ``evaluate_winner_on_test`` per-seed body EXACTLY:

    * **B1 matched budget** — trains the FIXED SAC via ``make_agent_trainer(agent_cfg, seed)`` on the SAME
      ``agent_cfg`` (train_steps/buffer/lr/...) the search used; only ``device`` is set per worker.
    * **B2 per-seed determinism** — ``set_global_seed(seed, deterministic_torch=True)`` BEFORE anything.
    * **B3 frozen winner** — re-instantiates the reward from the frozen ``reward_source`` via the sandbox
      (the per-winner hash desync guard runs once in the driver, not per seed).
    * **B4 once-only test touch** — builds the 3-window bundle (the ONLY place a test_window is created),
      trains on the train env, and calls ``test_series``/``test_returns`` EXACTLY ONCE (never val_returns).
    * **B5/B6 fingerprint + R18 purge** — same ``env_fp`` string + passes ``lookback`` so the builder's
      ``max(embargo, lookback)`` leakage guard is active.

    Catches its own failures (like ``train_candidate``) and returns ``{"ok": False, "error": ...}`` so a
    crash returns an error result rather than aborting :func:`run_recycling`.
    """
    out: dict[str, Any] = {"ok": False, "run_id": spec.get("run_id"), "arm": spec.get("arm")}
    try:
        from src.utils.env import load_env

        load_env()  # spawn child may not inherit the env; harmless for the (LLM-free) test leg
        import torch  # used for cuda.empty_cache below

        # NB: float32 precision (TF32) is NOT set here — it is applied by ``train_agent`` from the agent
        # config (key ``tf32``, default on for Ampere/Ada speed), which the serial trainer, the SEARCH
        # worker (``train_candidate``), and THIS parallel TEST worker all flow through. So all three paths
        # SELECT and EVALUATE the fixed agent at the SAME float32 precision setting — no scheduler-dependent
        # drift (the cousin of the batch_size 256/512 search/test asymmetry the audit caught). Do NOT
        # re-set TF32 here (that is what created the asymmetry in the first place).

        from src.agents.trainer import make_agent_trainer
        from src.env.runner import make_env_builder
        from src.sandbox.executor import validate_once
        from src.utils.seeding import set_global_seed

        seed = int(spec["seed"])
        set_global_seed(seed, deterministic_torch=True)  # B2

        # B3 re-instantiate the reward. The LLM/random/BO winners carry EXECUTABLE source -> the sandbox.
        # The H1 hand-designed baselines (PREREGISTRATION §18-19) are NAMED REWARD_CANON callables with no
        # executable source (a ``# baseline:<name>`` stub), so they resolve by name straight from the canon
        # -- EXACTLY mirroring the SEARCH-leg baseline branch (parallel.train_candidate:210-215) so the
        # single source of truth (src.baselines.rewards.REWARD_CANON) is reused, never re-derived.
        if str(spec.get("reward_kind")) == "baseline":
            from src.baselines import rewards as _R

            reward_fn = getattr(_R, str(spec["reward_name"]))
        else:
            reward_fn = validate_once(spec["reward_source"], _FIXTURE)  # frozen winner source via the sandbox

        panel = _load_test_panel(spec["panel_descriptor"])
        device = spec.get("device", "cpu")

        builder = make_env_builder(
            panel,
            spec["env_cfg"],
            tuple(spec["train_window"]),
            tuple(spec["val_window"]),
            test_window=tuple(spec["test_window"]),  # B4 the ONLY 3-window bundle
            embargo=int(spec["embargo"]),
            lookback=int(spec["lookback"]),  # B6 R18 purge guard
        )
        bundle = builder(reward_fn)

        agent_cfg = {**spec["agent_cfg"], "device": device}  # B1 matched agent cfg
        trainer = make_agent_trainer(agent_cfg, seed)
        policy = trainer(bundle.train_env())
        popart_scale = getattr(policy, "popart_scale", None)  # T2.4 realised scale at this seed

        if hasattr(bundle, "test_series"):  # B4 once-only; prefer the gross/turnover superset
            series = bundle.test_series(policy)
            test_returns = series["net"]
            test_gross = series["gross"]
            test_turnover = series["turnover"]
        else:
            test_returns = bundle.test_returns(policy)
            test_gross = None
            test_turnover = None

        record = build_test_record(
            winner=spec["winner"],
            arm=str(spec["arm"]),
            seed=seed,
            reward_hash=str(spec["reward_hash"]),
            env_fp=spec["env_fp"],  # B5
            test_returns=test_returns,
            test_gross=test_gross,
            test_turnover=test_turnover,
            popart_scale=popart_scale,  # T2.4 cross-arm sigma audit at the test leg
        )
        if str(device).startswith("cuda"):
            torch.cuda.empty_cache()
        out.update(ok=True, record=record)
    except Exception as exc:  # noqa: BLE001 — a failed seed must not crash the pool/run
        import traceback

        out["error"] = f"{type(exc).__name__}: {exc}"
        out["trace"] = traceback.format_exc().splitlines()[-12:]  # enough frames to diagnose a real-run crash
        try:
            import torch

            if str(spec.get("device", "")).startswith("cuda"):
                torch.cuda.empty_cache()
        except Exception:  # noqa: BLE001
            pass
    return out


# --------------------------------------------------------------------------- #
# The driver (all arms' winners × all seeds, device-pooled with recycling)     #
# --------------------------------------------------------------------------- #
def evaluate_winners_on_test_parallel(
    *,
    winners: list[tuple[str, dict[str, Any]]],
    seeds: list[int],
    panel_descriptor: dict[str, Any],
    env_cfg: Any,
    agent_cfg: dict[str, Any],
    train_window: tuple[int, int],
    val_window: tuple[int, int],
    test_window: tuple[int, int],
    embargo: int,
    lookback: int,
    n_gpu: int,
    n_cpu: int,
    recycle_every: int,
    test_root: str | Path,
    done_ids: set[str] | None = None,
    runner: Any = None,
    worker: Any = None,
    write: Any = None,
) -> dict[str, Any]:
    """Run the campaign TEST leg for ALL ``winners`` across ``seeds`` in parallel (the 180 re-runs).

    Builds one spec per ``(arm, seed)`` (skipping ``done_ids`` for ``--resume``), runs them through the
    device pool with manual recycling (``run_recycling``), and writes each ok record under
    ``test_root/<arm>/``. Science-neutral with the serial path: the same records via
    :func:`build_test_record`, the same once-only test touch (in the worker), and the SAME frozen/test
    **desync guard** applied here once per winner (so a re-searched-resume winner swap can never silently
    test a different reward — audit final-#10). ``runner``/``worker``/``write`` default to the production
    implementations and are injectable so this orchestration is unit-tested with no spawn / no torch.
    """
    import hashlib

    if runner is None:
        runner = run_recycling
    if worker is None:
        worker = _test_seed_worker
    if write is None:
        from src.io.results import write_run as write
    done_ids = done_ids or set()
    test_root = Path(test_root)

    specs: list[dict[str, Any]] = []
    for arm, winner in winners:
        reward_source = winner.get("reward_source", "")
        reward_hash = winner.get("reward_source_hash", "")
        # Frozen/test desync guard (ONCE per winner): the frozen source must hash to its recorded hash.
        if reward_hash and len(reward_hash) == 64:
            actual = hashlib.sha256(str(reward_source).encode("utf-8")).hexdigest()
            if actual != reward_hash:
                raise ValueError(
                    f"frozen winner hash mismatch for {arm}: recorded {reward_hash[:12]}.. "
                    f"!= actual {actual[:12]}.. (frozen/test desync guard)"
                )
        env_fp = f"campaign:{arm}:test[{test_window[0]},{test_window[1]})"
        for seed in seeds:
            run_id = f"{arm}-s{int(seed)}"
            if run_id in done_ids:
                continue
            specs.append(
                {
                    "run_id": run_id,
                    "arm": arm,
                    "seed": int(seed),
                    "winner": winner,
                    "reward_source": reward_source,
                    "reward_hash": reward_hash,
                    # H1 baselines (PREREGISTRATION §18-19): a baseline "winner" carries reward_kind=
                    # "baseline" + the REWARD_CANON name so the worker resolves the canonical callable by
                    # name (no executable source). Absent for the LLM/search winners (default None -> the
                    # worker takes the sandbox source path). Read from the record so a future caller need
                    # only set these two fields to route a named hand-reward through the parallel TEST leg.
                    "reward_kind": winner.get("reward_kind"),
                    "reward_name": winner.get("reward_name"),
                    "env_fp": env_fp,
                    "panel_descriptor": panel_descriptor,
                    "env_cfg": env_cfg,
                    "agent_cfg": agent_cfg,
                    "train_window": list(train_window),
                    "val_window": list(val_window),
                    "test_window": list(test_window),
                    "embargo": int(embargo),
                    "lookback": int(lookback),
                }
            )

    results = runner(specs, worker=worker, n_gpu=n_gpu, n_cpu=n_cpu, recycle_every=recycle_every)

    written: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for r in results:
        if r.get("ok") and r.get("record") is not None:
            rec = r["record"]
            write(rec, str(test_root / str(rec["arm"])))
            written.append(rec)
        else:
            failures.append({"run_id": r.get("run_id"), "arm": r.get("arm"), "error": r.get("error")})

    return {
        "n_specs": len(specs),
        "n_written": len(written),
        "n_failed": len(failures),
        "written": written,
        "failures": failures,
        # Mirror the search-leg matched-budget health flag: full budget AND at least one success.
        "matched_budget_ok": (len(written) + len(failures)) == len(specs) and len(written) > 0,
    }
