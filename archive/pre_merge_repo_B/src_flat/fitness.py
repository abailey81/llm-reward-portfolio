"""Held-out fitness F (PREREGISTRATION §3) — the selection criterion, NEVER the training
reward (Eureka separation, made out-of-sample because finance has no oracle).

F = SR_val - lambda * max(0, -CVaR_alpha(r_val)),   unannualised, daily net returns.
"""
from __future__ import annotations

import math

import numpy as np

from .config import get
from .feedback_schema import empirical_cvar


def unannualised_sharpe(returns: np.ndarray) -> float:
    r = np.asarray(returns, dtype=float)
    sd = r.std(ddof=1)
    return float(r.mean() / sd) if sd > 0 else 0.0


def cvar_penalised_sharpe(
    validation_returns: np.ndarray,
    alpha: float | None = None,
    lam: float | None = None,
) -> float:
    """The frozen fitness. `lam=None` reads inference.fitness.lambda_frozen and FAILS
    LOUDLY if it has not been set by the §3 calibration procedure — running the search
    with an unfrozen lambda is a pre-registration violation."""
    r = np.asarray(validation_returns, dtype=float).ravel()
    if r.size < 30:
        raise ValueError("validation window too short for a meaningful fitness")
    alpha = float(alpha if alpha is not None else get("inference.fitness.alpha"))
    if lam is None:
        lam = get("inference.fitness.lambda_frozen")
        if lam is None:
            raise RuntimeError(
                "fitness lambda not frozen — run the PREREGISTRATION §3 calibration, set "
                "inference.fitness.lambda_frozen, and record the ADR before any search."
            )
    lam = float(lam)
    cvar = empirical_cvar(np.sort(r), alpha)          # negative in the loss tail
    shortfall = max(0.0, -cvar)
    f = unannualised_sharpe(r) - lam * shortfall
    if not math.isfinite(f):
        raise ValueError("fitness evaluated non-finite")
    return float(f)
