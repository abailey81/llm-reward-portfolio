"""HEADLINE campaign driver — the Eureka post-loop, single-split (FINAL_PLAN 3.A, H Phase 3).

Purpose
-------
This is the real experiment whose numbers enter the dissertation. It turns the
DIRECTIONAL prototype (``scripts/run_prototype.py``) into the headline result by
running the FROZEN select-on-validation -> freeze -> test-once protocol
(PREREGISTRATION §5/§6/§7/§10) on the **single development/evaluation split**:

  - **development** train 2005-2014 / val 2015-2017 — search + selection live here ONLY.
  - **evaluation**  test 2018-2025 — the *sealed* leg, touched EXACTLY ONCE on the
    frozen winner, per campaign seed; embargo 21 trading days between splits.

The "Eureka post-loop" is four sealed stages per arm:

  1. **SEARCH**  — reuse ``run_prototype.run_arm`` on the DEVELOPMENT split at the
     search seed (the loop/search machinery, matched compute, archived per candidate).
  2. **SELECT**  — pick the arm's winner by **validation Deflated Sharpe** through the
     existing ``src.selection.fitness`` path (``analyze_results._winner`` reads the same
     ``metrics['val_fitness']``). Selection NEVER builds a test-window bundle.
  3. **FREEZE**  — persist the winner's ``reward_source`` + ``reward_source_hash`` with a
     ``frozen`` marker via ``src.io.results.write_run`` (replay-from-archive, audit C-2).
  4. **TEST**    — re-instantiate the FROZEN winner reward, build a **3-window** bundle
     (``make_env_builder(..., test_window=<2018-2025 [start,end)>, embargo=21)``),
     re-train via the trainer, and call ``bundle.test_returns(policy)`` EXACTLY ONCE per
     (arm, seed). One record per (arm, seed) carries ``val_fitness``, the realized
     per-step ``test_returns`` vector, ``per_period_pnl``, ``test_sharpe``, ``test_cvar05``.

Scope (frozen design)
---------------------
This implements ONLY the headline single-split campaign. The rolling walk-forward
folds (5y/1y/1y, ``config/inference.yaml: deferred_walk_forward`` — R43 — the frozen
scheme is single_sealed_split) and any
per-fold re-selection are DEFERRED — see the ``# TODO(Rank 2b)`` marker. We do NOT
invent a walk-forward validation-split scheme.

Testability (dependency injection)
----------------------------------
Every heavy collaborator is injectable so the post-loop is unit-testable WITHOUT real
SAC training or torch: ``run_winner_search`` takes an ``arm_runner``;
``evaluate_winner_on_test`` takes a ``trainer`` and ``env_builder`` (and a
``reward_builder`` for winner re-instantiation). ``tests/test_run_campaign.py`` drives
the whole post-loop on the synthetic panel with a FAKE trainer/policy.

Flags
-----
  --config        Campaign config (default config/campaign.yaml).
  --resume        Skip (arm, seed) test records already archived (idempotent).
  --arms          Comma list overriding the configured arms.
  --search-seed   Override the development-split search seed (default seeds[0]).
  --synthetic     Use the synthetic panel (no gold load) — for smoke/dev only.
  --dry-run       Tiny synthetic grid (1 LLM arm, 2 candidates, 1 seed) — gated smoke.
  --no-shutdown   Do not auto-shutdown the host on completion.
"""

from __future__ import annotations

import argparse
import json
import signal
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np

from src.utils.config import cfg_get

# --------------------------------------------------------------------------- #
# Graceful-shutdown flag (campaign-robustness §A). A ~27 h single-shot run WILL #
# be interrupted (Ctrl-C, OS sleep, thermal trip, crash). On the FIRST          #
# SIGINT/SIGTERM we set this Event so the arm loop stops scheduling NEW arms +   #
# defers the un-started test leg, draining whatever is already in flight; on a  #
# SECOND signal we restore the default handler and hard-exit. Nothing here       #
# deletes or overwrites archived work — ``--resume`` picks up from the on-disk   #
# records, so an interrupt is always NON-DESTRUCTIVE. The flag is checked only   #
# at arm/stage BOUNDARIES (never mid-candidate), so the science is untouched.    #
# --------------------------------------------------------------------------- #
SHUTDOWN = threading.Event()


# --------------------------------------------------------------------------- #
# Freeze ENFORCEMENT (verify-or-refuse). The pre-registration `--check` is a    #
# by-hand CI guard; this turns it into a MECHANICAL gate the REAL campaign       #
# cannot bypass. Before any non-dry-run / Pass-B (real-LLM) run we re-run the    #
# SAME verify path `scripts/freeze.py` exposes (prose<->yaml gate + Phase-0 +    #
# the canonical SHA-256 over the bound configs) and REFUSE to launch unless the  #
# design is FROZEN (`frozen: true`) AND the recorded hash matches the live one   #
# (no drift). The freeze module is REUSED — the hash is never re-implemented      #
# here. A `--allow-unfrozen` dev escape hatch (default OFF) is the only bypass,   #
# for synthetic-panel dev iteration before the user runs the real freeze.        #
# --------------------------------------------------------------------------- #
class CampaignNotFrozenError(RuntimeError):
    """The REAL campaign was launched against an un-frozen / drifted pre-registration."""


def enforce_freeze(*, allow_unfrozen: bool = False) -> dict[str, Any]:
    """Verify the pre-registration is FROZEN + un-drifted, or REFUSE the real run.

    Reuses ``scripts/freeze.py``'s ``verify`` (the prose<->yaml gate, the Phase-0
    precondition, and the canonical hash over the bound configs) — the hashing is NEVER
    re-implemented here. Returns a small stamp dict ``{frozen, freeze_hash, recorded_hash,
    phase0_marker, enforced}`` to record in the campaign summary.

    Raises :class:`CampaignNotFrozenError` when the design is not ``frozen: true`` or the
    recorded ``freeze_hash`` differs from the freshly-recomputed canonical hash (drift) —
    UNLESS ``allow_unfrozen`` is set (the dev escape hatch), in which case it WARNS and
    returns the stamp with ``enforced=False`` so a synthetic dev run can proceed.
    """
    import sys as _sys

    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    import freeze as _freeze  # the single source of truth for the hash + gate (reused, not re-implemented)

    try:
        status = _freeze.verify()  # prose<->yaml + Phase-0 + canonical hash (no writes)
    except _freeze.FreezeError as exc:
        if allow_unfrozen:
            print(
                f"[run_campaign] WARNING: --allow-unfrozen: pre-registration verify FAILED ({exc}); "
                f"proceeding UNFROZEN (dev only — results are NOT pre-registered).",
                file=sys.stderr, flush=True,
            )
            return {"frozen": False, "freeze_hash": None, "recorded_hash": None,
                    "phase0_marker": None, "enforced": False, "verify_error": str(exc)}
        raise CampaignNotFrozenError(
            f"REFUSING to launch the REAL campaign: pre-registration verify FAILED ({exc}). "
            f"Fix the prose<->yaml gate / Phase-0 precondition, then run `python scripts/freeze.py` "
            f"to freeze. Use --allow-unfrozen ONLY for a synthetic dev run."
        ) from exc

    drifted = bool(status.recorded_hash) and status.recorded_hash != status.hash
    stamp = {
        "frozen": bool(status.already_frozen),
        "freeze_hash": status.hash,                 # the freshly-recomputed canonical design hash
        "recorded_hash": status.recorded_hash,      # what config/preregistration.yaml records
        "phase0_marker": status.phase0_marker,
        "enforced": True,
    }
    if not status.already_frozen or drifted:
        reason = (
            f"recorded freeze_hash {status.recorded_hash} != current {status.hash} (the frozen "
            f"artifacts changed since the freeze — DRIFT)"
            if drifted else
            "config/preregistration.yaml is NOT frozen (frozen: false / freeze_hash: null). Run "
            "`python scripts/freeze.py` to freeze the design before the headline run."
        )
        if allow_unfrozen:
            print(
                f"[run_campaign] WARNING: --allow-unfrozen: {reason}. Proceeding anyway "
                f"(dev only — results are NOT pre-registered).",
                file=sys.stderr, flush=True,
            )
            stamp["enforced"] = False
            return stamp
        raise CampaignNotFrozenError(
            f"REFUSING to launch the REAL campaign: {reason} "
            f"(re-run with --allow-unfrozen ONLY for a synthetic dev run)."
        )
    print(f"[run_campaign] freeze ENFORCED — design FROZEN, hash {status.hash} (no drift).")
    return stamp


def _install_signal_handlers() -> None:
    """Install cooperative SIGINT/SIGTERM handlers (first signal -> drain; second -> hard exit)."""

    def _handler(signum: int, _frame: Any) -> None:
        if SHUTDOWN.is_set():
            # Second Ctrl-C: restore the default handler and re-raise so the user can force-kill.
            signal.signal(signum, signal.SIG_DFL)
            print(
                "\n[run_campaign] second interrupt — hard exit "
                "(work already on disk; re-run with --resume).",
                file=sys.stderr, flush=True,
            )
            raise KeyboardInterrupt
        SHUTDOWN.set()
        print(
            f"\n[run_campaign] signal {signum} received — finishing in-flight work, then stopping. "
            f"Press Ctrl-C again to force-quit. Re-launch with --resume to continue.",
            file=sys.stderr, flush=True,
        )

    for _sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(_sig, _handler)
        except (ValueError, OSError):  # not the main thread / unsupported on this platform
            pass

# NOTE (audit fix): the arm-membership tuples (_LLM_ARMS / _SEARCH_ARMS) deliberately do NOT
# live here. The campaign never decides arm membership locally — that logic is the single
# source of truth in ``run_prototype.run_arm`` (``arm in _LLM_ARMS``). Re-declaring them here
# was dead code AND a drift hazard (a future editor could "fix" an unread copy or let the two
# diverge), so the tuples were removed; consult run_prototype's copies where membership matters.


# --------------------------------------------------------------------------- #
# Panel + the three integer windows (development train/val + evaluation test)  #
# --------------------------------------------------------------------------- #
def _index_for_date(dates: np.ndarray, when: str, *, inclusive: bool) -> int:
    """Integer position of ``when`` in a sorted ``dates`` axis (np.searchsorted).

    ``inclusive`` -> the index ONE PAST the last session ``<= when`` (a half-open END
    bound for ``[start, end)`` windows, mirroring run_prototype's ``searchsorted + 1``).
    Otherwise -> the index of the first session ``>= when`` (a half-open START bound).
    A non-datetime axis (the synthetic panel ships integer dates in tests that pass an
    integer-like ``when``) is handled by ``np.searchsorted`` directly.
    """
    arr = np.asarray(dates)
    try:
        target: Any = np.datetime64(when)
    except (ValueError, TypeError):
        target = when
    if inclusive:
        return int(np.searchsorted(arr, target, side="right"))
    return int(np.searchsorted(arr, target, side="left"))


def resolve_windows(
    panel: Any,
    lookback: int,
    splits: Any,
    *,
    embargo: int,
) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    """Derive ``(train_window, val_window, test_window)`` as half-open ``[start, end)``.

    The three windows are the integer positions of the FROZEN calendar splits
    (``config/inference.yaml: splits``) on ``panel.dates`` via ``np.searchsorted`` —
    the SAME window-construction approach ``run_prototype``/``parallel`` use for the dev
    windows, extended additively to the evaluation (test) span:

      - development.train       [2005-01-01, 2014-12-31] -> train ``[lookback, train_end)``
      - development.validation  [2015-01-01, 2017-12-31] -> val   ``[train_end, val_end)``
      - evaluation.span         [2018-01-01, 2025-12-31] -> test  ``[val_end+embargo?, test_end)``

    Indices are clamped into ``[lookback+1, T]`` (and the test start is pushed past the
    val end + embargo) so a SHORT panel (e.g. the 600-day synthetic panel used in tests)
    degrades gracefully instead of producing an empty or look-ahead window. On the real
    5,283-session gold panel the clamps are inert.
    """
    dates = np.asarray(panel.dates)
    T = int(panel.T)

    dev = cfg_get(splits, "development", {})
    ev = cfg_get(splits, "evaluation", {})
    train_span = cfg_get(dev, "train", ["2005-01-01", "2014-12-31"])
    val_span = cfg_get(dev, "validation", ["2015-01-01", "2017-12-31"])
    test_span = cfg_get(ev, "span", ["2018-01-01", "2025-12-31"])

    emb = max(0, int(embargo))
    # The inter-split PURGE must cover the FEATURE LOOKBACK, not merely the embargo. Each observation
    # reads returns[t-lookback:t], so a gap of only embargo(21) < lookback(60) leaves the downstream
    # window's first (lookback - embargo) = 39 observations reading prior-split returns — a López de
    # Prado purge-insufficiency (leakage audit 2026-06-20, PREREGISTRATION R18). The effective purge is
    # therefore max(embargo, lookback): the embargo handles any label/serial-correlation margin, the
    # lookback ensures NO downstream feature window reaches back across the boundary.
    purge = max(emb, int(lookback))
    train_end = _index_for_date(dates, str(train_span[1]), inclusive=True)
    val_end = _index_for_date(dates, str(val_span[1]), inclusive=True)
    test_end = _index_for_date(dates, str(test_span[1]), inclusive=True)

    # The FROZEN calendar splits are CONTIGUOUS (train ends 2014-12-31, val begins 2015-01-01), so the
    # date axis gives val_start == train_end. The purge is carved out at EACH split boundary by pushing
    # the later window's START forward ``purge`` sessions, so the builder's lookback-aware guard holds.
    lo = lookback + 1
    train_end = max(lo, min(train_end, T - 1))
    val_start = min(train_end + purge, max(train_end, T - 1))
    val_end = max(val_start + 1, min(val_end, T))
    test_start = min(val_end + purge, max(val_end, T - 1))
    test_end = max(test_start + 1, min(test_end, T))

    return (lookback, train_end), (val_start, val_end), (test_start, test_end)


# --------------------------------------------------------------------------- #
# (1) SEARCH — reuse run_prototype.run_arm on the development split            #
# --------------------------------------------------------------------------- #
def run_winner_search(
    arm: str,
    *,
    search_seed: int,
    archive_root: str,
    synthetic: bool,
    candidates: int,
    generations: int,
    train_steps: int | None,
    n_trials: int,
    pass_mode: str = "A",
    provider: str = "stub",
    llm_cfg: dict[str, Any] | None = None,
    arm_runner: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """SEARCH stage: run ONE arm end-to-end on the DEVELOPMENT split at ``search_seed``.

    Reuses ``run_prototype.run_arm`` (the exact loop/search/select pipeline the prototype
    de-risked) so "matched compute" holds across arms. ``arm_runner`` is injectable so the
    stage is unit-testable without real SAC training; it defaults to the real
    ``run_prototype.run_arm``. ``llm_cfg`` carries the campaign's OWN reward-author block
    (Opus 4.8) so the campaign does NOT inherit the prototype's Gemini config.
    """
    if arm_runner is None:
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from run_prototype import run_arm as arm_runner  # type: ignore[no-redef]

    assert arm_runner is not None  # narrow past the injectable None default (mypy)
    return arm_runner(
        arm,
        synthetic=synthetic,
        candidates=candidates,
        generations=generations,
        train_steps=train_steps,
        n_trials=n_trials,
        seed=search_seed,
        pass_mode=pass_mode,
        provider=provider,
        archive_root=archive_root,
        llm_cfg=llm_cfg,
    )


def _search_parallel_arm(
    arm: str,
    *,
    agent_cfg: dict[str, Any],
    env_cfg: Any,
    synthetic: bool,
    candidates: int,
    generations: int,
    n_trials: int,
    pass_mode: str,
    provider: str,
    llm_cfg: dict[str, Any] | None,
    search_seed: int,
    search_root: Path,
    n_gpu: int,
    n_cpu: int,
    opts_builder: Callable[..., dict[str, Any]] | None = None,
    runner: Callable[..., list[dict[str, Any]]] | None = None,
) -> None:
    """Reflect-on-BEST parallel SEARCH for ONE campaign arm (the within-generation/cross-arm scheduler).

    Builds the parallel ``opts`` from the campaign's RESOLVED ``agent_cfg`` (so SEARCH trains the fixed
    agent at the SAME budget as the TEST leg — ``parallel.train_candidate`` couples buffer==train_steps,
    which also resolves the documented serial-search 25k-buffer skew) and the campaign's OWN reward-author
    block (Opus via ``llm_cfg``, mapped into the flat ``model``/``api_key_env``/``temperature`` keys the
    parallel driver reads), then runs ``parallel.run_parallel`` — which archives the SAME
    ``val_fitness``/``val_returns`` record schema that :func:`select_winner` reads, so SELECT/FREEZE/TEST
    downstream are unchanged. The ONLY behavioural difference from the serial loop is the reflection seed
    (each generation's BEST candidate vs the serial loop's LAST) — the amendment-gated science change;
    the default ``search_n_gpu=0`` keeps the serial ``run_winner_search`` path untouched. ``opts_builder``
    / ``runner`` are injectable so the wiring is unit-testable without real SAC training or an LLM.
    """
    from src.utils.config import load_config

    if opts_builder is None:
        import sys as _sys

        _sys.path.insert(0, str(Path(__file__).resolve().parent))
        from run_prototype import build_parallel_opts as opts_builder  # type: ignore[no-redef]
    if runner is None:
        from src.orchestration.parallel import run_parallel as runner
    assert opts_builder is not None and runner is not None  # narrow past the injectable None defaults (mypy)

    # Structural config: prototype base for reward_family/data (the panel + windows the serial run_arm and
    # the proven prototype --parallel path both build from), with the campaign's RESOLVED agent block so
    # the worker trains at the 50k campaign budget (train_steps threaded straight in below).
    proto_base = load_config("prototype")
    structural = {
        "agent": agent_cfg,
        "reward_family": cfg_get(proto_base, "reward_family", {}),
        "data": cfg_get(proto_base, "data", {}),
    }
    opts = opts_builder(
        structural,
        env_cfg,
        llm_block=(llm_cfg if llm_cfg is not None else cfg_get(proto_base, "llm", {})),
        train_steps=int(agent_cfg["train_steps_per_candidate"]),
        n_trials=n_trials,
        synthetic=synthetic,
        seed=search_seed,
        candidates=candidates,
        generations=generations,
        pass_mode=pass_mode,
        provider=provider,
    )
    runner([arm], opts, int(n_gpu), int(n_cpu), str(search_root))


# --------------------------------------------------------------------------- #
# (2) SELECT — winner by validation DSR via the existing fitness path          #
# --------------------------------------------------------------------------- #
def select_winner(arm_archive_root: str | Path) -> dict[str, Any] | None:
    """SELECT stage: the candidate with the best **validation Deflated Sharpe**.

    Reads the arm's archived candidate records through the canonical loader
    (``src.io.results.load_all`` — audit C-1) and returns the record whose
    ``metrics['val_fitness']`` is greatest, EXACTLY the ``analyze_results._winner`` rule
    (the val DSR computed by ``src.selection.fitness.held_out_fitness`` during search).
    Returns ``None`` when the arm produced no candidates.

    This path NEVER constructs a test-window bundle: selection lives wholly on the
    validation split (the seal in ``EnvBundle.test_returns`` holds structurally).
    """
    from src.io.results import load_all  # EXPLICIT: collides with src.utils.config.load_all

    records = load_all(arm_archive_root)
    if not records:
        return None
    return max(records, key=lambda r: r.get("metrics", {}).get("val_fitness", float("-inf")))


def _reinstantiate_frozen_winner(reward_source: str | None) -> Any:
    """Re-instantiate the FROZEN winner reward from its archived source via the sandbox.

    Routes the source through ``validate_once`` (the SAME AST-gate + contract check the
    candidate passed during search), so the test-leg reward is provably the frozen winner
    and replays from the archive (audit C-2). Raises ``ValueError`` when the source is
    absent or not an EXECUTABLE reward (e.g. a ``# bayes_opt coeffs=...`` comment stub) —
    see the FLAG in the module note.
    """
    from src.sandbox.executor import SandboxError, validate_once

    if not reward_source or not reward_source.strip():
        raise ValueError("winner record carries no reward_source to re-instantiate")
    fixture: tuple = (
        np.array([0.5, 0.5], dtype=float),
        np.array([0.01, -0.02], dtype=float),
        np.array([0.5, 0.5], dtype=float),
        0.0,
        {},
    )
    try:
        return validate_once(reward_source, fixture)
    except SandboxError as exc:
        raise ValueError(
            f"frozen winner reward_source did not re-instantiate as an executable reward "
            f"({exc}); search-arm comment-stub sources cannot be tested on the sealed leg"
        ) from exc


# --------------------------------------------------------------------------- #
# (3) FREEZE — persist the winner + a frozen marker                            #
# --------------------------------------------------------------------------- #
def freeze_winner(
    arm: str,
    winner: dict[str, Any],
    *,
    search_seed: int,
    frozen_root: str | Path,
    env_fingerprint: str,
) -> Path:
    """FREEZE stage: persist the winner's reward_source + hash with a ``frozen`` marker.

    Writes ONE sealed record (``<frozen_root>/<arm>-winner/record.json`` + ``reward.py``)
    via ``src.io.results.write_run``; the ``frozen: True`` marker and the carried
    ``reward_source`` make the winner reproducible from the archive (audit C-2). The hash
    is the winner's own ``reward_source_hash`` (recomputed if absent) so a later test
    record can be cross-checked against the exact frozen source.
    """
    import hashlib

    from src.io.results import write_run

    source = winner.get("reward_source", "")
    reward_hash = winner.get("reward_source_hash") or hashlib.sha256(
        str(source).encode("utf-8")
    ).hexdigest()
    record = {
        "run_id": f"{arm}-winner",
        "arm": arm,
        "seed": int(search_seed),
        "fold": 0,
        "candidate_id": winner.get("candidate_id", f"{arm}-winner"),
        "generation": int(winner.get("generation", 0)),
        "reward_source": source,
        "reward_source_hash": reward_hash,
        "feedback_block": winner.get("feedback_block", ""),
        "metrics": {"val_fitness": float(winner.get("metrics", {}).get("val_fitness", float("nan")))},
        "wall_clock": 0.0,
        "env_fingerprint": env_fingerprint,
        # Additive optional markers (OPTIONAL_FIELDS); back-compatible with all readers.
        "frozen": True,
    }
    return write_run(record, frozen_root)


# --------------------------------------------------------------------------- #
# (4) TEST — frozen winner, sealed 2018-2025 leg, touched EXACTLY ONCE         #
# --------------------------------------------------------------------------- #
def evaluate_winner_on_test(
    winner: dict[str, Any],
    panel: Any,
    cfg: Any,
    seeds: list[int],
    test_window: tuple[int, int],
    *,
    train_window: tuple[int, int],
    val_window: tuple[int, int],
    embargo: int,
    trainer: Callable[[Any, int], Callable[[Any], Any]],
    env_builder: Callable[..., Callable[[Any], Any]],
    archive_root: str | Path,
    arm: str | None = None,
    # NOTE (audit fix): no ``n_trials`` here. The TEST leg reports a RAW ``test_sharpe`` with no
    # Deflated-Sharpe / expected-max correction by design; the search-stage multiplicity is already
    # consumed inside run_winner_search/run_arm. The parameter was dead and misleading (a reader of
    # the matched-multiplicity story could assume the test Sharpe is deflated here — it is not), so
    # it was removed rather than left as a no-op argument.
    agent_cfg: Any = None,
    reward_builder: Callable[[str | None], Any] = _reinstantiate_frozen_winner,
    write: Callable[..., Any] | None = None,
    done_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """TEST stage: evaluate the FROZEN winner on the sealed 2018-2025 leg, once per seed.

    For EACH campaign ``seed`` this:
      1. re-instantiates the FROZEN winner reward (``reward_builder``);
      2. builds a **3-window** bundle ``env_builder(panel, cfg, train_window, val_window,
         test_window=<2018-2025 [start,end)>, embargo=embargo)`` (test bundle exists ONLY
         here — selection's 2-window bundles keep the seal);
      3. re-trains the FIXED agent via ``trainer(agent_cfg, seed)`` on the train env;
      4. calls ``bundle.test_returns(policy)`` **EXACTLY ONCE** (never re-selects);
      5. writes ONE record per (arm, seed) with deterministic ``run_id = f"{arm}-s{seed}"``
         carrying ``val_fitness``, the realized per-step ``test_returns`` (NET) vector, its
         per-step GROSS + TURNOVER decomposition (``test_gross`` + ``test_turnover``, for the
         Rank-15 cost sweep's analytic re-pricing), ``per_period_pnl``, ``test_sharpe``,
         ``test_cvar05`` (and ``frozen: True``).

    Dependency injection (``trainer``/``env_builder``/``reward_builder``/``write``) makes
    this unit-testable with a FAKE trainer/policy (no torch). ``done_ids`` (from
    ``--resume``) skips (arm, seed) records already archived.

    Returns the list of records WRITTEN this call (skipped-as-resumed ones are omitted).
    """
    import hashlib

    from src.orchestration.test_leg import build_test_record
    from src.utils.seeding import set_global_seed

    if write is None:
        from src.io.results import write_run as write
    assert write is not None  # narrow past the injectable None default (mypy)

    arm = arm or str(winner.get("arm", "winner"))
    done_ids = done_ids or set()
    reward_hash = winner.get("reward_source_hash", "")
    env_fp = f"campaign:{arm}:test[{test_window[0]},{test_window[1]})"

    # Re-instantiate the frozen winner ONCE (same reward across seeds — only the seed varies).
    reward_fn = reward_builder(winner.get("reward_source"))
    # Guard the select->freeze->test chain (final-audit #10): the frozen source MUST hash to the
    # recorded hash, so a winner swap (e.g. a re-searched resume) can never silently desync the
    # frozen and test legs into describing two different rewards. Scoped to a real content hash
    # (64-char sha256, as _reward_hash always emits) so it never fires on a test placeholder.
    if reward_hash and len(reward_hash) == 64:
        _actual = hashlib.sha256(str(winner.get("reward_source", "")).encode("utf-8")).hexdigest()
        if _actual != reward_hash:
            raise ValueError(
                f"frozen winner hash mismatch for {arm}: recorded {reward_hash[:12]}.. "
                f"!= actual {_actual[:12]}.. (frozen/test desync guard)"
            )

    written: list[dict[str, Any]] = []
    for seed in seeds:
        run_id = f"{arm}-s{int(seed)}"
        if run_id in done_ids:
            continue

        # Reseed the FULL stack per seed (final-audit #11): SEARCH reseeds via set_global_seed, but
        # TEST previously only set the SB3 `seed` kwarg, leaving the legacy np.random global (read by
        # VecNormalize/DummyVecEnv) to advance cumulatively across seeds — so the 30 "independent"
        # test seeds were not independently/reproducibly seeded the way the search candidates are.
        set_global_seed(int(seed), deterministic_torch=True)

        # 3-window bundle: the ONLY place a test_window is constructed (seal stays intact). Pass the
        # feature ``lookback`` so the builder guard enforces the R18 purge max(embargo, lookback) — the
        # leakage invariant no longer rests solely on resolve_windows producing the 60-session gap.
        builder = env_builder(
            panel,
            cfg,
            train_window,
            val_window,
            test_window=test_window,
            embargo=embargo,
            lookback=int(cfg_get(cfg_get(cfg, "state", {}), "lookback_days", 0)),
        )
        bundle = builder(reward_fn)

        # Re-train the FIXED agent at this campaign seed, then touch the test leg ONCE.
        train_fn = trainer(agent_cfg, int(seed))
        policy = train_fn(bundle.train_env())
        popart_scale = getattr(policy, "popart_scale", None)  # T2.4 realised scale at this seed
        # Prefer the gross/turnover/net superset (Rank 15: persist the decomposition so the
        # cost sweep re-prices analytically). A bundle/fake without `test_series` (e.g. the
        # counting wrapper in tests) falls back to the NET-only `test_returns` — the test leg
        # is still touched EXACTLY ONCE either way.
        if hasattr(bundle, "test_series"):
            series = bundle.test_series(policy)
            test_returns = np.asarray(series["net"], dtype=float)
            test_gross = np.asarray(series["gross"], dtype=float)
            test_turnover = np.asarray(series["turnover"], dtype=float)
        else:
            test_returns = np.asarray(bundle.test_returns(policy), dtype=float)
            test_gross = None
            test_turnover = None

        # The per-seed record schema lives in ONE place (src.orchestration.test_leg.build_test_record)
        # so this serial path and the parallel winner-re-run worker cannot drift: RAW test Sharpe (no
        # Deflated-Sharpe correction here — the search-stage multiplicity is already consumed), the NET
        # per-step vector + its GROSS/TURNOVER decomposition for the Rank-15 cost sweep, and frozen=True.
        record = build_test_record(
            winner=winner,
            arm=arm,
            seed=int(seed),
            reward_hash=reward_hash,
            env_fp=env_fp,
            test_returns=test_returns,
            test_gross=test_gross,
            test_turnover=test_turnover,
            popart_scale=popart_scale,  # T2.4 cross-arm sigma audit (serial path; parity with the parallel worker)
        )
        write(record, archive_root)
        written.append(record)

    return written


# --------------------------------------------------------------------------- #
# (H1) BASELINE TEST stage — the pre-registered "beat-the-human" hand rewards   #
# --------------------------------------------------------------------------- #
def _baseline_winner_record(name: str) -> dict[str, Any]:
    """A pre-frozen "winner" record for a hand-designed REWARD_CANON baseline (H1).

    Each H1 baseline (PREREGISTRATION §1) is dispatched through the SAME test machinery as a frozen
    LLM/search winner — but it is FIXED (no search/select/freeze), so the record carries a comment-stub
    ``reward_source`` (``# baseline:<name>``) plus ``reward_kind='baseline'`` + ``reward_name`` so the
    worker / serial reward_builder resolve the canonical callable BY NAME from
    ``src.baselines.rewards.REWARD_CANON`` (the single source of truth), never re-deriving the reward body.
    ``val_fitness`` is ``NaN`` (a baseline is never validation-selected) and is only carried for the
    record schema; the H1 metric reads the realized ``metrics['test_returns']``, not it.
    """
    import hashlib

    source = f"# baseline:{name}\n"
    return {
        "arm": f"baseline_{name}",
        "candidate_id": f"baseline_{name}",
        "generation": 0,
        "reward_source": source,
        "reward_source_hash": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "feedback_block": "",
        "metrics": {"val_fitness": float("nan")},
        # Routing fields (additive): the worker (parallel) and the reward_builder (serial) resolve the
        # canonical callable from these instead of compiling executable source. NOT in OPTIONAL_FIELDS,
        # so they ride only on the in-memory record handed to the test machinery (never written to disk).
        "reward_kind": "baseline",
        "reward_name": name,
    }


def _baseline_reward_builder(name: str) -> Callable[[str | None], Any]:
    """Serial ``reward_builder`` for a named baseline: resolve ``getattr(REWARD_CANON-module, name)``.

    Mirrors the SEARCH-leg baseline worker branch (``parallel.train_candidate:210-215``) on the serial
    TEST path: the canonical hand-reward callable is returned directly (the ``reward_source`` arg the
    winner path passes is ignored — a baseline has no executable source). Raises ``AttributeError`` LOUD
    if ``name`` is not a real REWARD_CANON key (a stale config name must fail, not silently no-op).
    """
    from src.baselines import rewards as R

    fn = getattr(R, name)  # fail-loud on a name that is not in the canon

    def _build(_reward_source: str | None) -> Any:  # noqa: ARG001 - baseline ignores the (stub) source
        return fn

    return _build


def evaluate_baselines_on_test(
    baseline_names: list[str],
    *,
    panel: Any,
    panel_descriptor: dict[str, Any],
    env_cfg: Any,
    agent_cfg: Any,
    seeds: list[int],
    train_window: tuple[int, int],
    val_window: tuple[int, int],
    test_window: tuple[int, int],
    embargo: int,
    lookback: int,
    test_root: str | Path,
    trainer: Callable[[Any, int], Callable[[Any], Any]],
    resume: bool = False,
    n_gpu: int = 0,
    n_cpu: int = 0,
    recycle_every: int = 12,
) -> list[dict[str, Any]]:
    """H1 BASELINE stage: train each hand-designed REWARD_CANON baseline at the 30 seeds (PREREG §1).

    The pre-registered "beat-the-human" test (Eureka, Ma et al. 2024) compares the LLM-designed winner
    against the BEST of the hand-designed baselines on the SEALED test leg. Each baseline is a FIXED,
    pre-frozen "winner" (NO search / NO select / NO freeze — there is no multiplicity to deflate), so this
    runs each ``baseline_<name>`` through the SAME path as the winner re-runs
    (``evaluate_winner_on_test`` serial / ``evaluate_winners_on_test_parallel`` parallel): the IDENTICAL
    matched-budget agent (``agent_cfg`` — train_steps/buffer/lr/...), the ONCE-only test touch, the shared
    ``build_test_record`` schema (``frozen: True``, the realized per-step ``test_returns`` the H1 metric
    reads). Records are archived under ``test_root/baseline_<name>/`` (disjoint from the arms' ``test_root/
    <arm>/``), so ``--resume`` keys on the per-(baseline, seed) ``run_id`` and a separate analysis can pick
    them up. ``n_gpu > 0`` runs the seeds across the device pool (the laptop headline path); ``n_gpu=0``
    keeps the serial trainer. Returns the flat list of records written this call.

    Budget: ``len(baseline_names) x len(seeds)`` runs (the 4-name H1 family x 30 seeds = 120 runs) at the
    SAME 50k step budget as the arms — the matched compute the Eureka comparison requires.
    """
    from src.env.runner import make_env_builder

    test_root = Path(test_root)
    written: list[dict[str, Any]] = []

    if int(n_gpu) > 0:
        # PARALLEL: one device-pooled batch over ALL (baseline, seed) cells (science-neutral with serial:
        # same records via build_test_record, same once-only touch in the worker). The baseline "winner"
        # carries reward_kind='baseline' + reward_name so the worker resolves the canonical callable by
        # name. Each baseline writes to test_root/baseline_<name>/ (the driver appends /<arm> itself, and
        # the baseline's arm IS "baseline_<name>").
        from src.orchestration.test_leg import evaluate_winners_on_test_parallel

        winners = [(f"baseline_{name}", _baseline_winner_record(name)) for name in baseline_names]
        done = (
            {r["run_id"] for name in baseline_names
             for r in load_all_safe(str(test_root / f"baseline_{name}"))}
            if resume else set()
        )
        res = evaluate_winners_on_test_parallel(
            winners=winners,
            seeds=seeds,
            panel_descriptor=panel_descriptor,
            env_cfg=env_cfg,
            agent_cfg=agent_cfg or {},
            train_window=train_window,
            val_window=val_window,
            test_window=test_window,
            embargo=embargo,
            lookback=lookback,
            n_gpu=int(n_gpu),
            n_cpu=int(n_cpu),
            recycle_every=int(recycle_every),
            test_root=test_root,
            done_ids=done,
        )
        return list(res["written"])

    # SERIAL: each baseline re-runs at the 30 seeds via evaluate_winner_on_test, with a reward_builder that
    # resolves the canonical callable by name (the stub reward_source is ignored). Mirrors the winner path.
    for name in baseline_names:
        arm = f"baseline_{name}"
        archive_root = test_root / arm
        done = {r["run_id"] for r in load_all_safe(str(archive_root))} if resume else set()
        written.extend(
            evaluate_winner_on_test(
                _baseline_winner_record(name),
                panel,
                env_cfg,
                seeds,
                test_window,
                train_window=train_window,
                val_window=val_window,
                embargo=embargo,
                trainer=trainer,
                env_builder=make_env_builder,
                archive_root=str(archive_root),
                arm=arm,
                agent_cfg=agent_cfg,
                reward_builder=_baseline_reward_builder(name),
                done_ids=done,
            )
        )
    return written


def load_all_safe(directory: str | Path) -> list[dict[str, Any]]:
    """``src.io.results.load_all`` that returns ``[]`` for a not-yet-created archive dir (resume-safe)."""
    from src.io.results import load_all

    if not Path(directory).is_dir():
        return []
    return load_all(directory)


# --------------------------------------------------------------------------- #
# (H3) SINGLE-SHOT stage — the distributional arm's best-of-N control          #
# --------------------------------------------------------------------------- #
def run_h3_singleshot(
    *,
    panel: Any,
    panel_descriptor: dict[str, Any],
    env_cfg: Any,
    agent_cfg: Any,
    seeds: list[int],
    search_seed: int,
    candidates: int,
    train_steps: int | None,
    n_trials: int,
    train_window: tuple[int, int],
    val_window: tuple[int, int],
    test_window: tuple[int, int],
    embargo: int,
    lookback: int,
    output_dir: str | Path,
    synthetic: bool,
    pass_mode: str = "A",
    provider: str = "stub",
    singleshot_generations: int = 1,
    llm_cfg: dict[str, Any] | None = None,
    resume: bool = False,
    trainer: Callable[[Any, int], Callable[[Any], Any]] | None = None,
    arm_runner: Callable[..., dict[str, Any]] | None = None,
    n_gpu: int = 0,
    n_cpu: int = 0,
    recycle_every: int = 12,
) -> dict[str, Any]:
    """H3 SINGLE-SHOT stage: the **distributional** arm re-run at ``generations=1`` (DEEP_H3 §1).

    The pre-registered H3 contrast (DEEP_H3 §1, canonical) is, *within the distributional arm*,
    iterative reflection (the headline: ``generations:6`` x ``candidates_per_gen:5`` = 30, reflect-on-best)
    versus a SINGLE-SHOT best-of-N control that spends the **same candidate budget** (``candidates`` = 30)
    in ONE generation with **no reflection** (``src/llm/loop.py``: ``generations==1`` never enters the
    reflection branch — every candidate is drawn from the INITIAL prompt). Winner selection is identical
    (best validation Deflated Sharpe) and the single-shot winner is re-run at the **same campaign seeds**,
    so the two conditions are a clean, like-for-like, matched-budget A/B.

    This mirrors the per-arm SEARCH -> SELECT -> FREEZE -> TEST flow of :func:`run_headline_campaign` for the
    one ``distributional`` arm, but archives to a SEPARATE root tree so the headline iterative winner is
    never overwritten and the analyze-H3 test (built separately) can load BOTH conditions:

      - ``<output_dir>/search_h3_singleshot/distributional/``  — the single-shot search candidates,
      - ``<output_dir>/frozen_h3_singleshot/distributional-winner/`` — the frozen single-shot winner,
      - ``<output_dir>/test_h3_singleshot/distributional/`` — the single-shot winner's 30 sealed test seeds.

    Matched-compute (DEEP_H3 §4): the single-shot search trains each candidate at the SAME ``agent_cfg``
    (``train_steps``/``buffer``) as the iterative headline, so the H3 contrast is not confounded by replay
    capacity (the R24 50k-buffer concern). ``trainer``/``arm_runner`` are injectable so the stage is
    unit-testable WITHOUT real SAC training or an LLM; defaults are the production factory / serial
    ``run_winner_search``. Resume-aware: a missing frozen single-shot winner triggers a fresh single-shot
    search; an existing one is loaded (no paid re-search), and per-(seed) test records already on disk are
    skipped. ``n_gpu > 0`` runs the TEST seeds across the device pool (science-neutral with serial).

    Returns a one-entry-shaped summary dict (``{"arm": "distributional_singleshot", "status": ...}``).
    """
    from src.env.runner import make_env_builder

    arm = "distributional"  # the H3 contrast lives wholly on the distributional arm (DEEP_H3 §1)
    output_dir = Path(output_dir)
    search_root = output_dir / "search_h3_singleshot"
    frozen_root = output_dir / "frozen_h3_singleshot"
    test_root = output_dir / "test_h3_singleshot"
    for d in (search_root, frozen_root, test_root):
        d.mkdir(parents=True, exist_ok=True)
    arm_search_root = str(search_root / arm)

    if trainer is None:
        trainer = make_agent_trainer_factory()

    # Resume-aware SEARCH+FREEZE (mirrors run_headline_campaign): a re-search is non-deterministic (real
    # Opus author + seeded search), so loading an existing frozen single-shot winner keeps select->freeze
    # ->test one stable, idempotent chain AND never re-burns the paid single-shot search budget on resume.
    winner: dict[str, Any] | None = None
    if resume:
        try:
            from src.io.results import load_run

            winner = load_run(f"{arm}-winner", str(frozen_root))
        except FileNotFoundError:
            winner = None  # only a MISSING frozen record => not searched yet (corrupt records propagate)

    if winner is None:
        # (1) SINGLE-SHOT SEARCH: the SAME candidate budget at generations=1 (no reflection). Reuses the
        # serial run_winner_search (== run_arm) so "matched compute" holds with the iterative headline arm;
        # the ONLY change is generations -> singleshot_generations (1), giving best-of-(candidates).
        run_winner_search(
            arm,
            search_seed=search_seed,
            archive_root=str(search_root),
            synthetic=synthetic,
            candidates=candidates,
            generations=int(singleshot_generations),
            train_steps=train_steps,
            n_trials=n_trials,
            pass_mode=pass_mode,
            provider=provider,
            llm_cfg=llm_cfg,
            arm_runner=arm_runner,
        )
        # (2) SELECT the single-shot winner by validation DSR (identical selector to the iterative arm).
        winner = select_winner(arm_search_root)
        if winner is None:
            return {"arm": "distributional_singleshot", "status": "no_candidates"}
        # (3) FREEZE the single-shot winner into the SEPARATE frozen root.
        freeze_winner(
            arm,
            winner,
            search_seed=search_seed,
            frozen_root=str(frozen_root),
            env_fingerprint="campaign:distributional_singleshot",
        )

    # (4) TEST the frozen single-shot winner on the sealed 2018-2025 leg at the SAME campaign seeds.
    done = (
        {r["run_id"] for r in load_all_safe(str(test_root / arm))} if resume else set()
    )
    if int(n_gpu) > 0:
        # PARALLEL test leg (science-neutral with serial): the single-shot winner's seeds run across the
        # device pool with manual recycling. The driver appends ``/<arm>`` to ``test_root`` itself.
        from src.orchestration.test_leg import evaluate_winners_on_test_parallel

        _res = evaluate_winners_on_test_parallel(
            winners=[(arm, winner)],
            seeds=seeds,
            panel_descriptor=panel_descriptor,
            env_cfg=env_cfg,
            agent_cfg=agent_cfg or {},
            train_window=train_window,
            val_window=val_window,
            test_window=test_window,
            embargo=embargo,
            lookback=lookback,
            n_gpu=int(n_gpu),
            n_cpu=int(n_cpu),
            recycle_every=int(recycle_every),
            test_root=test_root,
            done_ids=done,
        )
        written = list(_res["written"])
    else:
        written = evaluate_winner_on_test(
            winner,
            panel,
            env_cfg,
            seeds,
            test_window,
            train_window=train_window,
            val_window=val_window,
            embargo=embargo,
            trainer=trainer,
            env_builder=make_env_builder,
            archive_root=str(test_root / arm),
            arm=arm,
            agent_cfg=agent_cfg,
            done_ids=done,
        )
    return {
        "arm": "distributional_singleshot", "status": "tested",
        "n_seeds_written": len(written), "winner_id": winner.get("candidate_id"),
        "singleshot_generations": int(singleshot_generations),
    }


# --------------------------------------------------------------------------- #
# Headline campaign driver (single split) — SEARCH -> SELECT -> FREEZE -> TEST #
# --------------------------------------------------------------------------- #
def run_headline_campaign(
    *,
    arms: list[str],
    seeds: list[int],
    search_seed: int,
    candidates: int,
    train_steps: int | None,
    n_trials: int,
    output_dir: str | Path,
    synthetic: bool,
    embargo: int,
    pass_mode: str = "A",
    provider: str = "stub",
    generations: int = 1,
    llm_cfg: dict[str, Any] | None = None,
    resume: bool = False,
    agent_cfg: Any = None,
    n_gpu: int = 0,
    n_cpu: int = 0,
    recycle_every: int = 12,
    search_n_gpu: int = 0,
    search_n_cpu: int = 0,
    baseline_names: list[str] | None = None,
    run_h3_singleshot: bool = False,
    h3_singleshot_generations: int = 1,
    freeze_stamp: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the headline single-split campaign for ``arms`` and return a summary dict.

    ``n_gpu > 0`` runs the TEST leg (the 30 winner re-runs per arm) in PARALLEL across the device pool
    with manual recycling (``src.orchestration.test_leg.evaluate_winners_on_test_parallel``); this is
    science-neutral with the serial path (same records, same once-only touch, same numerics). Default
    ``n_gpu=0`` keeps the serial ``evaluate_winner_on_test``.

    ``run_h3_singleshot=True`` appends the H3 SINGLE-SHOT control (DEEP_H3 §1) AFTER the arms (+ baselines):
    the distributional arm re-searched at ``h3_singleshot_generations`` (=1) on the same candidate budget,
    selected/frozen/tested at the same seeds, archived to DISJOINT ``*_h3_singleshot/`` roots. It is
    report-only and wrapped in try/except so it can never sink the headline arms.

    This is the production path (real SAC training); it is GATED on the user and is not
    exercised by the fast suite. The unit tests drive the four stages directly with fakes.
    """
    from src.env.runner import make_env_builder
    from src.utils.config import load_config

    env_cfg = load_config("environment")
    inf_cfg = load_config("inference")
    lookback = int(env_cfg["state"]["lookback_days"])

    # Load the panel ONCE (real gold or synthetic), then derive the three windows.
    if synthetic:
        from src.data.synthetic import make_synthetic_panel

        panel = make_synthetic_panel(n_assets=30, n_days=600, seed=0)
        panel_descriptor: dict[str, Any] = {"synthetic": True}
    else:
        from src.data.loaders import load_gold_panel

        # Single-split headline: the development window is loaded to its val end; the test
        # leg (2018-2025) lives in the SAME panel object. The gold loader's development
        # phase + an explicit evaluation end give the full 2005-2025 span.
        #
        # UNIVERSE CAVEAT (#13, documented limitation): the agent allocates over a FIXED 30-asset
        # action space, so train and test share ONE universe — the DEVELOPMENT-phase point-in-time
        # top-30 (selected at 2005-01-03). The sealed test leg (2018-2025) therefore trades the
        # 2005 cohort (names dead by 2018 are held at 0%; later large-caps never enter) — a known
        # COMPOSITION bias, deliberately accepted for train/test universe consistency. It is NOT
        # dev->test return leakage (the splits are disjoint + embargoed). The gold ships point-in-time
        # walk-forward selections (incl. a 2018-01-02 top-30) so a PIT-universe ROBUSTNESS re-evaluation
        # is available as a follow-up; see docs/RUN_READINESS + PREREGISTRATION §10 (R17 note). The
        # prototype prose calls this cohort bias disqualifying FOR THE PROTOTYPE; the campaign reports
        # it as a headline limitation rather than silently inheriting it.
        ev = cfg_get(cfg_get(inf_cfg, "splits", {}), "evaluation", {})
        span = cfg_get(ev, "span", ["2018-01-01", "2025-12-31"])
        panel = load_gold_panel(phase="development", end=str(span[1])).panel
        # Picklable descriptor so the parallel TEST worker reloads the SAME frozen panel (rather than
        # pickling the ~40 MB object per task); must mirror this load (phase / end / default on_missing).
        panel_descriptor = {
            "synthetic": False, "phase": "development", "end": str(span[1]),
            "on_missing": "liquidate_to_cash",
        }

    splits = cfg_get(inf_cfg, "splits", {})
    train_window, val_window, test_window = resolve_windows(
        panel, lookback, splits, embargo=embargo
    )

    output_dir = Path(output_dir)
    search_root = output_dir / "search"
    frozen_root = output_dir / "frozen"
    test_root = output_dir / "test"
    for d in (search_root, frozen_root, test_root):
        d.mkdir(parents=True, exist_ok=True)

    trainer = make_agent_trainer_factory()

    # Matched compute (final-audit #4/5/8): SEARCH and TEST must train the FIXED agent on the SAME
    # train_steps budget, else the winner is SELECTED under one budget and the headline number produced
    # under another. The campaign train_steps (50k) is threaded into BOTH stages — TEST via `agent_cfg`
    # here; SEARCH via run_arm building its config from the SAME train_steps. (Previously SEARCH fell back
    # to prototype.yaml's 25k while TEST used the resolve_agent_kwargs 50k default — a training-budget skew.)
    # NOTE (buffer/steps audit fix): the TEST agent's ``buffer_size`` is here re-coupled to the 50k
    # train_steps (the documented ``buffer_size == train_steps`` invariant). The SEARCH leg builds its
    # config independently in run_prototype.run_arm via ``_agent_cfg(proto_cfg, ...)``, which still reads
    # prototype.yaml's pinned 25k buffer; matching SEARCH's buffer to 50k requires a campaign ``agent:``
    # block read by run_arm OR buffer/steps coupling inside ``_agent_cfg`` (out of this file's scope —
    # see this finding's test_impact). train_steps remains matched across both legs.
    if agent_cfg is None:
        import sys as _sys

        _sys.path.insert(0, str(Path(__file__).resolve().parent))
        from run_prototype import _agent_cfg  # type: ignore[import-not-found,no-redef]

        # Base the headline agent on the prototype agent block (batch_size, learning_rate, gamma,
        # ent_coef, normalize_obs, device, ...), but resolve agent hyperparameters from the CAMPAIGN
        # config where it provides them, falling back to prototype only for unset keys.
        agent_cfg = _agent_cfg(load_config("prototype"), train_steps)
        camp_agent = cfg_get(load_config("campaign"), "agent", {})
        for _k, _v in dict(camp_agent or {}).items():
            agent_cfg[_k] = _v
        # audit fix (buffer/steps invariant): prototype.yaml pins ``buffer_size: 25000`` ("== train_steps"
        # for the 25k laptop budget), so without an override the 50k-step HEADLINE agent would train with a
        # 25k replay buffer — the first half of training is evicted before training ends and prototype.yaml's
        # own ``buffer_size == train_steps`` invariant is violated for the campaign. Re-couple the buffer to
        # the campaign train_steps UNLESS the campaign config explicitly pins ``buffer_size`` itself, so the
        # headline replay buffer matches its 50k step budget per the documented invariant.
        if train_steps is not None and "buffer_size" not in (camp_agent or {}):
            agent_cfg["buffer_size"] = int(agent_cfg["train_steps_per_candidate"])

    summaries: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for arm in arms:
        if SHUTDOWN.is_set():
            # Graceful-shutdown §A.2: stop at the cheapest, safest cut point — BETWEEN arms, never
            # mid-candidate. Completed arms are archived; the operator re-runs with --resume to continue.
            print(
                f"[run_campaign] shutdown requested — stopping before arm {arm!r}; "
                f"completed arms are archived. Re-run with --resume to continue."
            )
            summaries.append({"arm": arm, "status": "skipped_shutdown"})
            break
        arm_search_root = str(search_root / arm)
        winner = None
        # Resume-aware SEARCH+FREEZE (final-audit #10/17): if a frozen winner already exists, LOAD it
        # instead of re-searching. Re-search is non-deterministic (real Opus author + now-seeded
        # search), so a resumed run could SELECT a DIFFERENT winner, overwrite the frozen record, yet
        # skip its TEST seeds (done_ids holds the OLD ids) -> frozen and test legs describing two
        # different rewards; it also re-burns the paid SEARCH budget every resume. Loading the
        # existing frozen winner keeps select->freeze->test one stable, idempotent chain.
        if resume:
            try:
                from src.io.results import load_run

                winner = load_run(f"{arm}-winner", str(frozen_root))
            except FileNotFoundError:
                # Only a MISSING frozen record means "not searched yet" -> fall through to a fresh
                # search. A corrupted/schema-invalid record (KeyError/ValueError from load_run, incl.
                # the env.json hash guard) PROPAGATES — failing loud beats silently re-searching and
                # overwriting it (re-audit hardening of final-audit #10/17).
                winner = None
        if winner is None:
            # (1) SEARCH on the development split.
            if int(search_n_gpu) > 0:
                # Reflect-on-BEST PARALLEL search (~4x the serial search on the dev split). Trains each
                # candidate at the campaign budget and resolves the serial 25k-buffer skew (buffer==train_steps
                # in the worker). Reflection seeds from each generation's BEST candidate, NOT the serial loop's
                # LAST -> a frozen-decision change GATED on the dated amendment; default search_n_gpu=0 = serial.
                _search_parallel_arm(
                    arm,
                    agent_cfg=agent_cfg,
                    env_cfg=env_cfg,
                    synthetic=synthetic,
                    candidates=candidates,
                    generations=generations,
                    n_trials=n_trials,
                    pass_mode=pass_mode,
                    provider=provider,
                    llm_cfg=llm_cfg,
                    search_seed=search_seed,
                    search_root=search_root,
                    n_gpu=int(search_n_gpu),
                    n_cpu=int(search_n_cpu),
                )
            else:
                run_winner_search(
                    arm,
                    search_seed=search_seed,
                    archive_root=str(search_root),
                    synthetic=synthetic,
                    candidates=candidates,
                    generations=generations,
                    train_steps=train_steps,
                    n_trials=n_trials,
                    pass_mode=pass_mode,
                    provider=provider,
                    llm_cfg=llm_cfg,
                )
            # (2) SELECT the winner by validation DSR.
            winner = select_winner(arm_search_root)
            if winner is None:
                summaries.append({"arm": arm, "status": "no_candidates"})
                continue
            # (3) FREEZE the winner.
            freeze_winner(
                arm,
                winner,
                search_seed=search_seed,
                frozen_root=str(frozen_root),
                env_fingerprint=f"campaign:{arm}",
            )
        if SHUTDOWN.is_set():
            # Graceful-shutdown §A.3: search+select+freeze for THIS arm are already on disk; stop
            # BEFORE launching the (long) test leg. On --resume the frozen winner is loaded and the
            # test seeds resume from done_ids — so no paid search is re-burned and the test leg picks
            # up where it left off.
            print(
                f"[run_campaign] shutdown requested after FREEZE for {arm!r}; test leg deferred. "
                f"Re-run with --resume (frozen winner will be loaded, test seeds resumed)."
            )
            summaries.append(
                {"arm": arm, "status": "frozen_test_deferred", "winner_id": winner.get("candidate_id")}
            )
            break
        # (4) TEST the frozen winner on the sealed 2018-2025 leg (resume-aware).
        done = (
            {r["run_id"] for r in load_all_safe(str(test_root / arm))} if resume else set()
        )
        try:
            if int(n_gpu) > 0:
                # PARALLEL test leg (science-neutral): this arm's 30 seeds run across the device pool
                # with manual recycling. Same records as the serial path (shared build_test_record),
                # same frozen/test desync guard + once-only touch (enforced in the worker), same
                # numerics (TF32 is config-driven in train_agent). The driver appends ``/<arm>`` to
                # ``test_root`` itself, so it writes to the same place the serial ``archive_root`` does.
                from src.orchestration.test_leg import evaluate_winners_on_test_parallel

                _res = evaluate_winners_on_test_parallel(
                    winners=[(arm, winner)],
                    seeds=seeds,
                    panel_descriptor=panel_descriptor,
                    env_cfg=env_cfg,
                    agent_cfg=agent_cfg or {},
                    train_window=train_window,
                    val_window=val_window,
                    test_window=test_window,
                    embargo=embargo,
                    lookback=lookback,
                    n_gpu=int(n_gpu),
                    n_cpu=int(n_cpu),
                    recycle_every=int(recycle_every),
                    test_root=test_root,
                    done_ids=done,
                )
                written = _res["written"]
                if _res["n_failed"]:
                    # Fail-loud failure-wave guard (§G): distinguish a PARTIAL failure (warn, keep the
                    # arm's good seeds) from a TOTAL wave (a systemic fault — dead CUDA ctx, OOM cascade,
                    # degenerate window — that writes 0 usable records). A total wave must NOT be banked
                    # as a silent "tested (0)"; surface it as an ERROR + a machine-detectable
                    # ``test_failure_wave`` status so the operator stops and fixes the root cause rather
                    # than discovering an empty arm hours later at analysis time.
                    _first = (_res["failures"][0] or {}).get("error")
                    if not _res.get("matched_budget_ok") or len(written) == 0:
                        print(
                            f"[run_campaign] ERROR: {arm} TEST leg FAILURE WAVE — "
                            f"{_res['n_failed']}/{_res['n_specs']} seeds failed, {len(written)} written. "
                            f"First error: {_first}",
                            flush=True,
                        )
                        summaries.append(
                            {"arm": arm, "status": "test_failure_wave",
                             "n_failed": _res["n_failed"], "first_error": str(_first)[:200]}
                        )
                        if SHUTDOWN.is_set():
                            break
                        continue  # skip the 'tested' summary append for this arm
                    print(
                        f"[run_campaign] WARNING: {arm} parallel TEST leg had {_res['n_failed']} "
                        f"failed seed(s) — first error: {_first}"
                    )
            else:
                written = evaluate_winner_on_test(
                    winner,
                    panel,
                    env_cfg,
                    seeds,
                    test_window,
                    train_window=train_window,
                    val_window=val_window,
                    embargo=embargo,
                    trainer=trainer,
                    env_builder=make_env_builder,
                    archive_root=str(test_root / arm),
                    arm=arm,
                    # audit fix: n_trials dropped — the test Sharpe is raw, the multiplicity is
                    # consumed in SEARCH; passing it here was a misleading dead argument.
                    agent_cfg=agent_cfg,
                    done_ids=done,
                )
            summaries.append(
                {"arm": arm, "status": "tested", "n_seeds_written": len(written),
                 "winner_id": winner.get("candidate_id")}
            )
        except ValueError as exc:  # non-executable winner source (search-arm stub) — FLAGGED
            summaries.append({"arm": arm, "status": "winner_not_testable", "reason": str(exc)})

    # (H1) BASELINE stage — the pre-registered "beat-the-human" hand rewards (PREREGISTRATION §1).
    # POST-arms, additive: each REWARD_CANON baseline is run at the SAME 30 seeds + matched 50k budget as
    # the winners, archived under test/baseline_<name>/. It is SCIENCE-NEUTRAL to the frozen H2 arms (a
    # disjoint archive subtree, no search/select/freeze) — analyze_campaign.beat_human_baseline reads these
    # records POST-FREEZE and does NOT re-select the winner. Skipped when no baselines are configured or a
    # shutdown was requested (resume re-runs only the un-done (baseline, seed) cells).
    if baseline_names and not SHUTDOWN.is_set():
        try:
            base_written = evaluate_baselines_on_test(
                list(baseline_names),
                panel=panel,
                panel_descriptor=panel_descriptor,
                env_cfg=env_cfg,
                agent_cfg=agent_cfg,
                seeds=seeds,
                train_window=train_window,
                val_window=val_window,
                test_window=test_window,
                embargo=embargo,
                lookback=lookback,
                test_root=test_root,
                trainer=trainer,
                resume=resume,
                n_gpu=int(n_gpu),
                n_cpu=int(n_cpu),
                recycle_every=int(recycle_every),
            )
            summaries.append(
                {"arm": "h1_baselines", "status": "tested",
                 "baselines": list(baseline_names), "n_records_written": len(base_written)}
            )
        except Exception as exc:  # noqa: BLE001 - the report-only H1 stage must not sink the headline arms
            summaries.append({"arm": "h1_baselines", "status": "error", "reason": str(exc)[:200]})

    # (H3) SINGLE-SHOT stage — the distributional arm at generations=1 (DEEP_H3 §1, canonical contrast).
    # POST-arms, additive + SCIENCE-NEUTRAL to the frozen H2 arms: it re-runs ONLY the distributional arm's
    # search at generations=1 (best-of-N, no reflection) on the SAME candidate budget, selects on validation
    # DSR, freezes, and tests at the SAME campaign seeds — all into the DISJOINT *_h3_singleshot/ subtrees
    # (search_h3_singleshot/, frozen_h3_singleshot/, test_h3_singleshot/) so the headline ITERATIVE winner is
    # never touched and the analyze-H3 difference test can load both conditions. Resolved through the module
    # object (``sys.modules[__name__]``) so the ``run_h3_singleshot`` gate parameter never shadows the stage
    # function at the call site (and a test monkeypatch on the module attr is honoured). Wrapped in try/except
    # so this report-only control can NEVER sink the headline arms; skipped on a requested shutdown.
    if run_h3_singleshot and not SHUTDOWN.is_set():
        try:
            _h3_stage = getattr(sys.modules[__name__], "run_h3_singleshot")
            h3_summary = _h3_stage(
                panel=panel,
                panel_descriptor=panel_descriptor,
                env_cfg=env_cfg,
                agent_cfg=agent_cfg,
                seeds=seeds,
                search_seed=search_seed,
                candidates=candidates,
                train_steps=train_steps,
                n_trials=n_trials,
                train_window=train_window,
                val_window=val_window,
                test_window=test_window,
                embargo=embargo,
                lookback=lookback,
                output_dir=output_dir,
                synthetic=synthetic,
                pass_mode=pass_mode,
                provider=provider,
                singleshot_generations=int(h3_singleshot_generations),
                llm_cfg=llm_cfg,
                resume=resume,
                n_gpu=int(n_gpu),
                n_cpu=int(n_cpu),
                recycle_every=int(recycle_every),
            )
            summaries.append(h3_summary)
        except Exception as exc:  # noqa: BLE001 - the report-only H3 control must not sink the headline arms
            summaries.append(
                {"arm": "distributional_singleshot", "status": "error", "reason": str(exc)[:200]}
            )

    summary = {
        "arms": summaries,
        "train_window": list(train_window),
        "val_window": list(val_window),
        "test_window": list(test_window),
        "wall_clock_s": round(time.perf_counter() - t0, 1),
        # Stamp the freeze provenance (the canonical design hash + frozen/enforced flags) into the
        # campaign summary so every headline artifact carries the pre-registration it was run under
        # (verify-or-refuse converts the by-hand `--check` into a recorded, mechanical guarantee).
        "freeze": freeze_stamp if freeze_stamp is not None else {"enforced": False, "frozen": None},
    }
    (output_dir / "campaign_summary.json").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )
    return summary


def make_agent_trainer_factory() -> Callable[[Any, int], Callable[[Any], Any]]:
    """Return the production ``trainer(agent_cfg, seed) -> (train_env -> policy)`` factory.

    Thin adapter over ``src.agents.trainer.make_agent_trainer`` so ``evaluate_winner_on_test``
    can be handed a fake trainer of the SAME shape in tests.
    """
    from src.agents.trainer import make_agent_trainer

    def _factory(agent_cfg: Any, seed: int) -> Callable[[Any], Any]:
        return make_agent_trainer(agent_cfg or {}, int(seed))

    return _factory


# TODO(Rank 2b): walk-forward folds — confirm per-fold val-split vs frozen prereg.
#   R43: the frozen scheme is single_sealed_split; the rolling params live under
#   config/inference.yaml: deferred_walk_forward = {train_years: 5,
#   test_years: 1, step_years: 1, span: 2018-2025}. The rolling 5y/1y/1y folds and any
#   per-fold re-selection are DEFERRED: the prereg freezes ONE val split (2015-2017) for
#   selection but does NOT specify a per-fold validation split for walk-forward selection.
#   Do NOT invent one — STOP-AND-FLAG to confirm the per-fold protocol (re-select per fold
#   on a rolled val window, or carry the single frozen winner across all folds) before
#   building the walk-forward driver.


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the HEADLINE single-split campaign (FINAL_PLAN 3.A).",
    )
    parser.add_argument(
        "--config", default="config/campaign.yaml",
        help="Campaign config (default config/campaign.yaml); resolved by stem via load_config.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip (arm, seed) test records already archived (idempotent).",
    )
    parser.add_argument("--arms", default=None, help="Comma list overriding the configured arms.")
    parser.add_argument(
        "--search-seed", type=int, default=None,
        help="Development-split search seed (default seeds[0]).",
    )
    parser.add_argument("--synthetic", action="store_true", help="Use the synthetic panel (no gold load).")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Tiny synthetic grid (1 LLM arm, 2 candidates, 1 seed) — gated smoke.",
    )
    parser.add_argument(
        "--no-shutdown", action="store_true",
        help="Do not auto-shutdown the host on completion.",
    )
    parser.add_argument(
        "--gpu", type=int, default=None,
        help="GPU worker slots for the PARALLEL test leg (default: serial). Laptop ceiling ~4.",
    )
    parser.add_argument("--cpu", type=int, default=0, help="CPU worker slots for the parallel test leg.")
    parser.add_argument(
        "--search-gpu", type=int, default=None,
        help="GPU worker slots for the reflect-on-BEST PARALLEL search (default: serial reflect-on-last). "
             "AMENDMENT-GATED: parallel search reflects on the generation's BEST candidate (a frozen-decision "
             "change vs the serial loop's LAST) and trains at the matched 50k buffer; keep 0 until ratified.",
    )
    parser.add_argument("--search-cpu", type=int, default=0, help="CPU worker slots for the parallel search.")
    parser.add_argument(
        "--allow-unfrozen", action="store_true",
        help="DEV ESCAPE HATCH (default OFF): run the REAL campaign even if the pre-registration is "
             "not frozen / has drifted. Default behaviour REFUSES an unfrozen real run; pass this ONLY "
             "for synthetic-panel dev iteration before `python scripts/freeze.py` has been run. Results "
             "produced under it are NOT pre-registered.",
    )
    parser.add_argument(
        "--h3-singleshot", action="store_true",
        help="Append the H3 SINGLE-SHOT control (DEEP_H3 §1): re-run the distributional arm at "
             "h3_singleshot_generations (config, =1) on the same candidate budget -> best-of-N, no "
             "reflection; selected/frozen/tested at the same seeds into the disjoint *_h3_singleshot/ roots. "
             "Report-only (cannot sink the headline arms); OFF by default until the R30 amendment is ratified.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    from src.utils.config import load_config
    from src.utils.env import load_env
    from src.utils.preload import preload

    preload()  # pyarrow before torch (gold-parquet ABI segfault guard) -- BEFORE any torch import
    load_env()  # .env -> os.environ so the LLM key is available (ADR-038); workers inherit it
    _install_signal_handlers()  # cooperative graceful shutdown (a 27 h run WILL be interrupted)

    # audit fix: HONOR --config. ``load_config`` resolves config/<stem>.yaml by stem, so derive the
    # stem from the user-supplied path (default config/campaign.yaml -> "campaign"). Previously
    # ``args.config`` was parsed but never read — ``--config config/other.yaml`` silently ran
    # config/campaign.yaml, a real foot-gun for the gated single-shot headline run. Only the CAMPAIGN
    # config is overridable here; the inference splits are a separate, fixed file.
    camp_stem = Path(args.config).stem
    camp = load_config(camp_stem)
    inf = load_config("inference")
    arms = args.arms.split(",") if args.arms else list(camp["arms"])
    seeds = [int(s) for s in camp["seeds"]]
    search_seed = int(args.search_seed if args.search_seed is not None else seeds[0])
    candidates = int(camp["candidates_per_arm"])
    train_steps = int(camp["train_steps_per_candidate"])
    embargo = int(cfg_get(cfg_get(inf, "splits", {}), "embargo_trading_days", 21))
    n_trials = candidates  # DSR expected-max correction = per-arm candidate count
    output_dir = "outputs/campaign"
    synthetic = bool(args.synthetic)
    # H1 "beat-the-human" baselines (PREREGISTRATION §1), READ from config (no hardcoding — CLAUDE.md);
    # absent => the stage is skipped. Each name must be a real REWARD_CANON key (validated when resolved).
    baseline_names = [str(b) for b in cfg_get(camp, "h1_baselines", [])]

    # The headline RUN MODE *and* reward-author are read from config/campaign.yaml: llm and threaded
    # as `llm_cfg` into run_arm, so the campaign uses its OWN author (Claude Opus 4.8) and does NOT
    # inherit the prototype's (Gemini 3.5 Flash). (Previously hardcoded to the stub, and earlier read
    # the model/key from prototype.yaml — both fixed by the provider-neutral wiring, 2026-06-19.)
    camp_llm = dict(cfg_get(camp, "llm", {}))  # plain dict: picklable across the process pool
    pass_mode = str(cfg_get(camp_llm, "pass", "A"))
    provider = str(cfg_get(camp_llm, "provider", "stub"))
    generations = int(cfg_get(camp_llm, "generations", 1))
    # H3 single-shot CONTROL generation count (DEEP_H3 §1), READ from config (no hardcoding — CLAUDE.md):
    # the distributional arm re-searched at this many generations (=1 -> best-of-N, no reflection) on the
    # SAME candidate budget. The stage itself is OFF unless --h3-singleshot is passed (R30-gated).
    h3_singleshot_generations = int(cfg_get(camp_llm, "h3_singleshot_generations", 1))
    run_h3_singleshot = bool(args.h3_singleshot)

    if args.dry_run:
        # Keyless stub smoke — never burns the API key (overrides any Pass-B config).
        arms = ["distributional"]
        candidates, train_steps, seeds, synthetic, n_trials = 2, 200, [0], True, 2
        pass_mode, provider, generations = "A", "stub", 1
        h3_singleshot_generations = 1  # single-shot control is generations=1 by definition; 1 candidate in dry-run
        output_dir = "outputs/campaign_dryrun"
        baseline_names = ["raw_return"]  # exercise the H1 baseline stage too (1 baseline x 1 seed)
        if run_h3_singleshot:
            # Dry-run = 1 candidate single-shot (best-of-1): the cheapest exercise of the H3 wiring.
            candidates = 1
        print("[run_campaign] DRY RUN — 1 LLM arm x 2 candidates x 1 seed + 1 H1 baseline (synthetic stub).")

    # Fail-loud frozen-family guard (final-audit #24 — PREREGISTRATION §10/R13 states run_campaign
    # carries this assertion). The campaign arms MUST cover the pre-registered H2 contrast family
    # (distributional vs {scalar, placebo, scalar_cvar5}) so the headline contrast set can never
    # silently drift from the frozen one. Skipped for the 1-arm keyless dry-run smoke.
    if not args.dry_run:
        import sys as _sys

        _sys.path.insert(0, str(Path(__file__).resolve().parent))
        from analyze_campaign import H2_CONTRASTS

        _family = {a for pair in H2_CONTRASTS for a in pair}
        _missing = sorted(_family - set(arms))
        if _missing:
            raise SystemExit(
                f"[run_campaign] frozen H2 family arms missing from campaign arms: {_missing} "
                f"(config/preregistration.yaml: inference.testing_family / PREREGISTRATION §10)."
            )

    # FREEZE ENFORCEMENT (verify-or-refuse): the REAL headline run requires a FROZEN, un-drifted
    # pre-registration. This re-runs scripts/freeze.py's verify (prose<->yaml gate + Phase-0 + the
    # canonical hash) and REFUSES to launch unless frozen + the recorded hash matches — converting the
    # by-hand `--check` into a mechanical gate. The keyless --dry-run smoke is exempt (it never touches
    # the API key or the sealed leg; it exercises the wiring on a 1-arm synthetic stub). The --allow-
    # unfrozen dev escape hatch downgrades the refusal to a warning for synthetic-panel dev iteration.
    freeze_stamp: dict[str, Any] | None = None
    if not args.dry_run:
        try:
            freeze_stamp = enforce_freeze(allow_unfrozen=bool(args.allow_unfrozen))
        except CampaignNotFrozenError as exc:
            raise SystemExit(f"[run_campaign] {exc}") from exc

    # RAM/VRAM-safety guard (ram_thermal §3): the 50k replay buffer doubles vs the prototype's 25k, so
    # the gen-transition wave (up to 2x co-resident buffers across all workers) OOMs the 15.6 GiB laptop
    # at search_n_gpu>=4 — AND n_gpu=4 already saturates the 6 GiB RTX-4050 VRAM ceiling with no slack.
    # n_gpu=4 is the MEASURED search OOM (the prototype lost 52 candidates there). Refuse it LOUDLY at
    # the CLI boundary rather than silently clamping, so a stray ``--search-gpu 4`` cannot melt the
    # single-shot, grade-critical run. Use --search-gpu 2 (proven-flat) or 3 (watchdog-armed).
    if args.search_gpu is not None and int(args.search_gpu) >= 4:
        raise SystemExit(
            f"[run_campaign] --search-gpu {args.search_gpu} is unsafe on this 15.6 GiB-RAM / 6 GiB-VRAM "
            f"laptop at the 50k buffer (gen-transition-wave OOM + VRAM ceiling; n_gpu=4 is the measured "
            f"search OOM). Use --search-gpu 2 (proven) or 3 (thermal/RAM watchdog armed)."
        )

    print(
        f"[run_campaign] HEADLINE single-split: arms={arms} seeds={seeds} "
        f"search_seed={search_seed} candidates={candidates} steps={train_steps} "
        f"gens={generations} pass={pass_mode} provider={provider} "
        f"embargo={embargo} resume={args.resume} h1_baselines={baseline_names} "
        f"h3_singleshot={run_h3_singleshot}(gens={h3_singleshot_generations}) -> {output_dir}"
    )
    summary = run_headline_campaign(
        arms=arms,
        seeds=seeds,
        search_seed=search_seed,
        candidates=candidates,
        # Pass the campaign's REAL train_steps (config: 50000) to BOTH stages — never None (final-
        # audit #4/5/8). None previously leaked the prototype's 25k into SEARCH while TEST used the
        # 50k default, selecting and testing the fixed agent at different budgets; the banner above
        # printed 50000 (`steps={train_steps}`), masking the 25k SEARCH actually ran.
        train_steps=train_steps,
        n_trials=n_trials,
        output_dir=output_dir,
        synthetic=synthetic,
        embargo=embargo,
        pass_mode=pass_mode,
        provider=provider,
        generations=generations,
        llm_cfg=camp_llm,
        resume=args.resume,
        n_gpu=int(args.gpu) if args.gpu is not None else 0,
        n_cpu=int(args.cpu),
        search_n_gpu=int(args.search_gpu) if args.search_gpu is not None else 0,
        search_n_cpu=int(args.search_cpu),
        baseline_names=baseline_names,  # H1 "beat-the-human" hand rewards (config: h1_baselines)
        run_h3_singleshot=run_h3_singleshot,        # H3 single-shot control gate (--h3-singleshot, R30)
        h3_singleshot_generations=h3_singleshot_generations,  # config: llm.h3_singleshot_generations (=1)
        freeze_stamp=freeze_stamp,  # verify-or-refuse stamp (canonical hash + frozen/enforced) -> summary
    )
    print(f"[run_campaign] windows train={summary['train_window']} val={summary['val_window']} "
          f"test={summary['test_window']}")
    for s in summary["arms"]:
        print(f"  {s['arm']:>14}: {s.get('status')} "
              f"({s.get('n_seeds_written', s.get('reason', ''))})")
    print(f"[run_campaign] done in {summary['wall_clock_s']}s -> {output_dir}/campaign_summary.json")

    if not args.no_shutdown and cfg_get(camp, "auto_shutdown_on_complete", False):
        print("[run_campaign] auto-shutdown ENABLED by config (rented GPU); host would power off now.")


if __name__ == "__main__":
    main()
