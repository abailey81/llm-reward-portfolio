"""Multi-root leg aggregation — leg archives -> the cross-model synthesis input (R80/R82).

Each replication leg archives its test-leg records under its own TEST sub-root (disjoint by
construction: ``run_campaign_cluster`` forces ``--root-suffix leg_<label>``, so the leg root is
``<output_dir>/test_leg_<sanitized label>``), holding one record per arm at
``<arm>/<arm>-s<seed>`` via ``src.io.results``. This module walks a
mapping of ``leg label -> archive root`` and assembles exactly the input contract of
:mod:`src.inference.cross_model`:

* per-seed CVaR-5% difference arrays (distributional − scalar, seed-aligned on the COMMON floor
  seed set), computed from each record's realized ``metrics['test_returns']`` with the empirical
  worst-⌈αT⌉ mean under the signed-return convention (more negative = worse tail);
* the registered T0-floor leg-inclusion flag: a leg votes in the synthesis ONLY if the mean
  per-seed Sharpe of BOTH contrasted arms clears the supplied naive-benchmark floor (legs that
  fail report as authoring/search failures — a finding, never a vote);
* per-arm per-seed Sharpe arrays (for the pair-DiD instrument and the reporting tables).

Missing seeds fail LOUD (a silent subset would quietly change the paired estimator); a wholly
missing arm marks the leg failed with the reason recorded. Deterministic; read-only.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from src.inference.bootstrap import sharpe_ratio
from src.io.results import load_run

__all__ = ["empirical_cvar", "per_seed_series", "leg_results_for_synthesis"]


def empirical_cvar(returns: np.ndarray, alpha: float = 0.05) -> float:
    """Mean of the worst ``ceil(alpha*T)`` signed returns (house convention: more negative = worse)."""
    arr = np.asarray(returns, dtype=float)
    arr = np.sort(arr[np.isfinite(arr)])  # row 30c: strip non-finite (mirrors bootstrap.cvar);
    if arr.size == 0:                     # -inf would otherwise poison the tail mean silently
        raise ValueError("empirical_cvar: no finite returns")
    k = max(1, math.ceil(alpha * arr.size))
    return float(arr[:k].mean())


def per_seed_series(
    root: str | Path, arm: str, seeds: list[int], alpha: float = 0.05
) -> dict[str, np.ndarray]:
    """Per-seed CVaR and Sharpe arrays for ``arm`` under ``root`` (records ``<arm>/{arm}-s{seed}``).

    ``root`` is the leg's TEST sub-root (``<output_dir>/test_leg_<label>``); each arm's records sit
    in their OWN ``<arm>/`` directory beneath it.

    LAYOUT FIX 2026-07-26 (deep review, row 34). This previously called ``load_run(f"{arm}-s{seed}",
    root)`` — i.e. it assumed a FLAT ``root/{arm}-s{seed}``. The real archive is TWO-level: the
    campaign hands ``write_run`` an ARM-level root (``src/cluster/run_one.py:108``), producing
    ``test_<sfx>/<arm>/<arm>-s<seed>/`` — verified first-hand on disk
    (``outputs/campaign_dryrun/test/distributional/distributional-s0``). Because
    :func:`leg_results_for_synthesis` passes ONE root for BOTH contrasted arms, the flat assumption
    was not merely wrong but unsatisfiable: no single ``root`` makes ``distributional-s0`` and
    ``scalar-s0`` both resolve when they live in sibling arm directories. Wired as it stood, EVERY
    leg would have raised FileNotFoundError, been caught as a leg failure, and reported
    ``t0_floor_pass: False`` — so the R86 pooled bound would have been computed over ZERO legs and
    read as "every leg failed the floor": a plausible-looking, wholly fabricated scientific outcome.
    The unit fixture wrote the same flat layout, which is why the tests passed; it now mirrors the
    producer.

    Raises FileNotFoundError naming the missing run — a silent seed subset would change the
    paired estimator, so absence is loud, never skipped.
    """
    arm_root = Path(root) / arm
    cvars: list[float] = []
    sharpes: list[float] = []
    for seed in seeds:
        rec = load_run(f"{arm}-s{seed}", arm_root)
        rets = np.asarray(rec["metrics"]["test_returns"], dtype=float)
        cvars.append(empirical_cvar(rets, alpha))
        # UNIT FIX 2026-07-26 (deep review; write-time registry row 34's "latent trap that only bites
        # on wiring"). This computed a PER-PERIOD, ddof=1 Sharpe (`rets.mean()/rets.std(ddof=1)`),
        # while `floor_sharpe` below — and every other Sharpe in the stack — is the ANNUALISED, ddof=0
        # `bootstrap.sharpe_ratio`. Passing the real T0 floor would therefore have compared ~0.04
        # against ~0.6: `floor_ok` False for EVERY leg, so every leg would be excluded from the sign
        # count and the R86 pooled bound, and the registered cross-model statement would come back
        # empty — silently, since an excluded leg is a legitimate reported outcome. Two mismatches
        # (annualisation AND ddof) are removed at once by delegating to the canonical estimator, so
        # there is exactly ONE Sharpe definition in the codebase. The CVaR arrays that feed the pooled
        # bound are untouched.
        sharpes.append(sharpe_ratio(rets))
    return {"cvar": np.asarray(cvars), "sharpe": np.asarray(sharpes)}


def leg_results_for_synthesis(
    leg_roots: dict[str, str | Path],
    seeds: list[int],
    floor_sharpe: float,
    *,
    arm_a: str = "distributional",
    arm_b: str = "scalar",
    alpha: float = 0.05,
) -> dict[str, dict[str, Any]]:
    """Assemble the :func:`cross_model.sign_count`/``permutation_test`` input across legs.

    ``floor_sharpe`` is the T0 naive-benchmark floor (from the shared baseline records); the
    registered criterion: BOTH arms' mean per-seed Sharpe must clear it or the leg is marked
    ``t0_floor_pass: False`` (reported, never voting). A leg whose records are missing/corrupt is
    included with ``t0_floor_pass: False`` and the reason in ``failure`` — reliability data,
    never silence.
    """
    out: dict[str, dict[str, Any]] = {}
    for label, root in leg_roots.items():
        try:
            a = per_seed_series(root, arm_a, seeds, alpha)
            b = per_seed_series(root, arm_b, seeds, alpha)
        except Exception as exc:  # noqa: BLE001 — a broken leg is a FINDING, not a crash
            out[label] = {
                "cvar_diff_per_seed": np.zeros(0),
                "t0_floor_pass": False,
                "failure": f"{type(exc).__name__}: {exc}",
            }
            continue
        floor_ok = bool(a["sharpe"].mean() > floor_sharpe and b["sharpe"].mean() > floor_sharpe)
        out[label] = {
            "cvar_diff_per_seed": a["cvar"] - b["cvar"],   # dist − scalar; positive = dist safer
            "t0_floor_pass": floor_ok,
            "sharpe_a_per_seed": a["sharpe"],
            "sharpe_b_per_seed": b["sharpe"],
            "cvar_a_per_seed": a["cvar"],
            "cvar_b_per_seed": b["cvar"],
        }
    return out
