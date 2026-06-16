"""Fitness-λ calibration machinery (PREREGISTRATION §3; ADR-010 operationalisation).

PREREG §3: λ is calibrated ONCE on the pre-2015 calibration fold (train 2005–2012,
validate 2013–2014, hand-designed rewards only), "chosen to maximise rank stability of
known-good vs known-degenerate rewards", then frozen into `config/inference.yaml:
fitness.lambda_frozen` with an ADR before the first LLM call.

Operationalisation (deterministic, pre-registered before the freeze):
  * separation accuracy of λ = fraction of (good, degenerate) reward pairs whose
    fitness F_λ orders good ABOVE degenerate, averaged over seeds;
  * primary criterion: maximise mean separation accuracy;
  * tie-break 1: minimise the across-seed std of that accuracy (stability);
  * tie-break 2: the SMALLEST such λ (parsimony).
The full per-λ table is returned for the freezing ADR.

This module never writes config — freezing the chosen value is a human ADR action.
Pass `lam` explicitly to the fitness here; `fitness.cvar_penalised_sharpe` continues to
fail loudly on the unfrozen default elsewhere (by design).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import get
from .fitness import cvar_penalised_sharpe


@dataclass(frozen=True)
class LambdaCalibrationRow:
    lam: float
    mean_accuracy: float
    std_accuracy: float
    per_seed_accuracy: tuple[float, ...]


def _accuracy_for_seed(
    good_returns: list[np.ndarray], degenerate_returns: list[np.ndarray],
    lam: float, alpha: float,
) -> float:
    """Fraction of (good, degenerate) pairs correctly ordered by F_λ for one seed."""
    f_good = [cvar_penalised_sharpe(r, alpha=alpha, lam=lam) for r in good_returns]
    f_bad = [cvar_penalised_sharpe(r, alpha=alpha, lam=lam) for r in degenerate_returns]
    pairs = [(g, b) for g in f_good for b in f_bad]
    return float(np.mean([g > b for g, b in pairs]))


def select_lambda(
    good: dict[str, list[np.ndarray]],
    degenerate: dict[str, list[np.ndarray]],
    lambda_grid: list[float] | None = None,
    alpha: float | None = None,
) -> dict:
    """Run the §3 selection rule over the grid.

    Args:
        good / degenerate: reward name -> list of validation-return arrays, ONE PER
            SEED (seed-aligned across rewards; calibration-fold returns only — using
            any later window here would contaminate the development split, R3).
    Returns:
        {"chosen_lambda": float, "table": [LambdaCalibrationRow, ...]} — the table is
        the evidence block for the freezing ADR.
    """
    if not good or not degenerate:
        raise ValueError("need at least one known-good and one known-degenerate reward")
    grid = [float(x) for x in (lambda_grid if lambda_grid is not None
                               else get("inference.fitness.lambda_grid"))]
    alpha = float(alpha if alpha is not None else get("inference.fitness.alpha"))

    n_seeds = {len(v) for v in (*good.values(), *degenerate.values())}
    if len(n_seeds) != 1:
        raise ValueError("all rewards must supply the same number of seed return-series")
    n = n_seeds.pop()
    if n < 1:
        raise ValueError("need at least one seed")

    table: list[LambdaCalibrationRow] = []
    for lam in grid:
        per_seed = []
        for s in range(n):
            acc = _accuracy_for_seed(
                [v[s] for v in good.values()], [v[s] for v in degenerate.values()],
                lam=lam, alpha=alpha,
            )
            per_seed.append(acc)
        table.append(LambdaCalibrationRow(
            lam=lam,
            mean_accuracy=float(np.mean(per_seed)),
            std_accuracy=float(np.std(per_seed)),
            per_seed_accuracy=tuple(per_seed),
        ))

    # max mean accuracy -> min std -> smallest lambda (lexicographic, deterministic)
    chosen = min(table, key=lambda row: (-row.mean_accuracy, row.std_accuracy, row.lam))
    return {"chosen_lambda": chosen.lam, "table": table}
