"""Tests for the comparative ES backtest (Fissler-Ziegel joint elicitability + Nolde-Ziegel DM test).

The load-bearing test is STRICT CONSISTENCY: the FZ0 score must be minimized at the true (VaR, ES).
If that holds, the scoring function is implemented correctly regardless of sign-convention worries.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy import stats

from src.inference.es_backtest import comparative_es_backtest, fz0_loss, var_es_estimates

ALPHA = 0.05
# Analytic standard-normal lower-tail (VaR, ES) at alpha=5%.
TRUE_VAR = float(stats.norm.ppf(ALPHA))                       # ~ -1.6449
TRUE_ES = float(-stats.norm.pdf(TRUE_VAR) / ALPHA)            # ~ -2.0627


def test_fz0_strictly_consistent_minimized_at_truth(normal_returns: np.ndarray) -> None:
    """E[FZ0] is minimized at the true (VaR, ES): every perturbation raises the mean score."""
    base = fz0_loss(normal_returns, TRUE_VAR, TRUE_ES, ALPHA).mean()
    perturbations = [
        (TRUE_VAR * 0.8, TRUE_ES),
        (TRUE_VAR * 1.2, TRUE_ES),
        (TRUE_VAR, TRUE_ES * 0.8),
        (TRUE_VAR, TRUE_ES * 1.2),
        (TRUE_VAR * 0.9, TRUE_ES * 1.1),
    ]
    for v, e in perturbations:
        assert fz0_loss(normal_returns, v, e, ALPHA).mean() > base, f"({v:.3f},{e:.3f}) not worse"


def test_var_es_estimates_match_normal_closed_form(normal_returns: np.ndarray) -> None:
    v, e = var_es_estimates(normal_returns, ALPHA)
    assert v == pytest.approx(TRUE_VAR, abs=0.03)
    assert e == pytest.approx(TRUE_ES, abs=0.05)


def test_fz0_rejects_nonnegative_es(normal_returns: np.ndarray) -> None:
    with pytest.raises(ValueError, match="negative"):
        fz0_loss(normal_returns, TRUE_VAR, 0.0, ALPHA)
    with pytest.raises(ValueError, match="alpha"):
        fz0_loss(normal_returns, TRUE_VAR, TRUE_ES, 1.5)


def test_comparative_backtest_prefers_the_better_forecast(rng: np.random.Generator) -> None:
    """A correctly-specified (VaR, ES) forecast beats one that badly underestimates the tail."""
    realized = rng.standard_normal(5_000)
    good = (TRUE_VAR, TRUE_ES)
    bad = (TRUE_VAR, TRUE_ES * 0.5)  # ES magnitude halved -> underestimates tail loss
    res = comparative_es_backtest(realized, good, bad, alpha=ALPHA, n_boot=500, rng=rng)
    assert res["better"] == "model1"
    assert res["mean_score_diff"] < 0.0
    assert res["pvalue"] < 0.05  # clear misspecification, ample data -> rejects equal accuracy


def test_comparative_backtest_tie_for_identical_forecasts(rng: np.random.Generator) -> None:
    realized = rng.standard_normal(1_000)
    f = (TRUE_VAR, TRUE_ES)
    res = comparative_es_backtest(realized, f, f, alpha=ALPHA, n_boot=200, rng=rng)
    assert res["mean_score_diff"] == 0.0
    assert res["better"] == "tie"
