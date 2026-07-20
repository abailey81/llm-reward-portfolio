"""Multi-root leg aggregation — leg archives -> the cross-model synthesis input (R80/R82).

Each replication leg archives its test-leg records under its own root (disjoint by
construction), one record per ``{arm}-s{seed}`` via ``src.io.results``. This module walks a
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

from src.io.results import load_run

__all__ = ["empirical_cvar", "per_seed_series", "leg_results_for_synthesis"]


def empirical_cvar(returns: np.ndarray, alpha: float = 0.05) -> float:
    """Mean of the worst ``ceil(alpha*T)`` signed returns (house convention: more negative = worse)."""
    arr = np.sort(np.asarray(returns, dtype=float))
    k = max(1, math.ceil(alpha * arr.size))
    return float(arr[:k].mean())


def per_seed_series(
    root: str | Path, arm: str, seeds: list[int], alpha: float = 0.05
) -> dict[str, np.ndarray]:
    """Per-seed CVaR and Sharpe arrays for ``arm`` under ``root`` (records ``{arm}-s{seed}``).

    Raises FileNotFoundError naming the missing run — a silent seed subset would change the
    paired estimator, so absence is loud, never skipped.
    """
    cvars: list[float] = []
    sharpes: list[float] = []
    for seed in seeds:
        rec = load_run(f"{arm}-s{seed}", root)
        rets = np.asarray(rec["metrics"]["test_returns"], dtype=float)
        cvars.append(empirical_cvar(rets, alpha))
        sd = float(rets.std(ddof=1))
        sharpes.append(float(rets.mean()) / sd if sd > 0 else 0.0)
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
