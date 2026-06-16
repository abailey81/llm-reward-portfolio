"""Held-out fitness — reward-independent candidate selection (F.4, audit B-3).

The winning reward candidate is selected on the **validation** Deflated Sharpe of
its realized validation returns. This is deliberately INDEPENDENT of the candidate
reward's own units/value (so selection cannot be reward-hacked) and is computed on
a DIFFERENT split from the fed-back signal (training returns), so the loop cannot
tune-then-select on the same data (audit B-3).

Algorithm (FINAL_PLAN F.4 / B.7):
  - Compute the validation Deflated Sharpe (F.11 / src/inference/deflated_sharpe.py)
    on the realized validation returns, using `n_trials` for the expected-max
    Sharpe correction under guided search.
  - Optionally subtract lam * |validation-CVaR(5%)| per the pre-registered fitness.
  - Never touch the candidate reward's own scalar value -- the fitness depends ONLY
    on realized returns.

Guard: training-split input must be rejected (the measurement/feedback signal lives
on the training split; fitness lives on validation -- mixing them re-introduces the
overfitting B-2/B-3 are designed to prevent).

Audit refs: B-3 (loop-once, validation selection independent of reward units).
"""

from __future__ import annotations

import numpy as np


def held_out_fitness(
    returns: np.ndarray,
    n_trials: int,
    split: str = "val",
    lam: float = 0.0,
    rng: np.random.Generator | None = None,
) -> float:
    """Validation Deflated Sharpe (optionally penalized by validation CVaR).

    Parameters
    ----------
    returns:
        Realized portfolio returns on the VALIDATION split only (anonymized
        array; no tickers/dates). Depends ONLY on realized returns -- never on
        any reward value.
    n_trials:
        Number of trials for the Deflated-Sharpe expected-max correction.
    split:
        Must be ``"val"``; any other value raises ``ValueError`` (selection
        lives on the validation split, audit B-2/B-3).
    lam:
        Optional weight on ``|validation-CVaR(5%)|`` (pre-registered fitness);
        ``0`` disables the penalty.
    rng:
        Accepted for interface symmetry; the fitness is deterministic given the
        returns and is not used.

    Returns
    -------
    float
        ``deflated_sharpe_ratio(returns, n_trials) - lam * |cvar(returns, 0.05)|``.

    Raises
    ------
    ValueError
        If ``split != "val"``.
    """
    if split != "val":
        raise ValueError(
            f"held_out_fitness must be computed on the validation split; "
            f"got split={split!r} (selection lives on validation, audit B-2/B-3)"
        )

    # Lazy imports to avoid import-order issues within the inference package.
    from src.inference.bootstrap import cvar
    from src.inference.deflated_sharpe import deflated_sharpe_ratio

    r = np.asarray(returns, dtype=float)
    dsr = deflated_sharpe_ratio(r, n_trials)
    if lam == 0.0:
        return float(dsr)
    penalty = lam * abs(cvar(r, 0.05))
    return float(dsr - penalty)
