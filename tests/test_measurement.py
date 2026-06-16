"""Tests for src/feedback/measurement.py — empirical body + EVT tails (F.2, B.4)."""

from __future__ import annotations

import math

import numpy as np
from scipy import stats

from src.feedback.measurement import (
    CVAR_01_HIGH_VARIANCE_NOTE,
    ReturnDistribution,
)

FROZEN_KEYS = {"cvar_01", "cvar_05", "cvar_10", "cvar_25", "left_tail_mass", "robust_skew"}


def _normal_es(alpha: float) -> float:
    """Closed-form standard-normal Expected Shortfall (signed, left tail)."""
    z = stats.norm.ppf(alpha)
    return -stats.norm.pdf(z) / alpha


def test_empirical_cvar_and_quantiles_match_closed_form_on_normal_fixture(
    normal_returns: np.ndarray,
) -> None:
    """Empirical CVaR/quantiles match the closed-form normal values within tol (B-1)."""
    rd = ReturnDistribution().fit(normal_returns)

    # Empirical CVaR(5%) vs closed-form normal ES within ~3%.
    emp_cvar5 = rd.cvar(0.05, method="empirical")
    closed = _normal_es(0.05)
    assert abs(emp_cvar5 - closed) / abs(closed) < 0.03

    # Quantiles match scipy norm.ppf within tolerance.
    qs = rd.quantiles([0.05, 0.25, 0.50, 0.95])
    for tau, val in qs.items():
        assert abs(val - stats.norm.ppf(tau)) < 0.02


def test_evt_cvar_recovers_known_gpd_tail_within_tolerance() -> None:
    """GPD/EVT tail fit recovers CVaR of a synthetic known-GPD tail (B-1, EX-DRL)."""
    rng = np.random.default_rng(7)
    xi_true, beta_true = 0.2, 0.5
    # Build returns whose losses have a GPD upper tail: body N(0,1), tail GPD above u.
    u = 2.0
    fu = 0.10  # tail fraction
    n = 200_000
    n_tail = int(n * fu)
    body = stats.truncnorm.rvs(-np.inf, u, size=n - n_tail, random_state=rng)
    tail = u + stats.genpareto.rvs(xi_true, loc=0.0, scale=beta_true, size=n_tail,
                                   random_state=rng)
    losses = np.concatenate([body, tail])
    returns = -losses

    rd = ReturnDistribution(threshold_q=fu).fit(returns)

    # Closed-form GPD CVaR for losses at alpha=0.01 (within tail), signed return-space.
    alpha = 0.01
    var_loss = u + (beta_true / xi_true) * ((alpha / fu) ** (-xi_true) - 1.0)
    cvar_loss = (var_loss + beta_true - xi_true * u) / (1.0 - xi_true)
    expected = -cvar_loss

    evt = rd.cvar(alpha, method="evt")
    assert abs(evt - expected) / abs(expected) < 0.10

    # Fitted shape/scale recovered reasonably.
    assert abs(rd.xi - xi_true) < 0.1
    assert abs(rd.beta - beta_true) < 0.15


def test_cvar_is_monotone_in_alpha(heavy_tail_returns: np.ndarray) -> None:
    """cvar(alpha) is non-increasing as alpha shrinks (deeper tail <= shallower)."""
    rd = ReturnDistribution().fit(heavy_tail_returns)
    c01 = rd.cvar(0.01)
    c05 = rd.cvar(0.05)
    c10 = rd.cvar(0.10)
    c25 = rd.cvar(0.25)
    assert c01 <= c05 <= c10 <= c25


def test_cvar_monotone_on_normal(normal_returns: np.ndarray) -> None:
    """Monotonicity also holds on the light-tailed normal fixture."""
    rd = ReturnDistribution().fit(normal_returns)
    assert rd.cvar(0.01) <= rd.cvar(0.05) <= rd.cvar(0.10) <= rd.cvar(0.25)


def test_tail_stats_returns_exactly_frozen_fields(normal_returns: np.ndarray) -> None:
    """tail_stats keys are EXACTLY the six frozen fields."""
    rd = ReturnDistribution().fit(normal_returns)
    ts = rd.tail_stats()
    assert set(ts.keys()) == FROZEN_KEYS
    assert all(math.isfinite(v) for v in ts.values())


def test_robust_skew_negative_on_left_skewed_fixture() -> None:
    """robust_skew is negative when the left tail is longer (B.10)."""
    rng = np.random.default_rng(11)
    # Negative-shifted lognormal -> long left tail.
    left_skewed = -rng.lognormal(mean=0.0, sigma=0.5, size=100_000)
    rd = ReturnDistribution().fit(left_skewed)
    assert rd.tail_stats()["robust_skew"] < 0.0


def test_empirical_evt_crosscheck_path(heavy_tail_returns: np.ndarray) -> None:
    """The method flag lets a test compare EVT vs empirical CVaR in the tail."""
    rd = ReturnDistribution().fit(heavy_tail_returns)
    emp = rd.cvar(0.05, method="empirical")
    evt = rd.cvar(0.05, method="evt")
    # Both are valid downside estimates of the same order of magnitude.
    assert emp < 0 and evt < 0
    assert abs(evt - emp) / abs(emp) < 0.5


def test_cvar_01_documented_high_variance() -> None:
    """cvar_01 is EVT-estimated and documented high-variance (audit B-7)."""
    assert "high-variance" in CVAR_01_HIGH_VARIANCE_NOTE.lower()
    assert "B-7" in CVAR_01_HIGH_VARIANCE_NOTE


def test_threshold_sensitivity_diagnostic(heavy_tail_returns: np.ndarray) -> None:
    """threshold_sensitivity returns per-threshold CVaRs + a finite, non-negative spread,
    and does not mutate the fitted estimator (side-effect-free)."""
    rd = ReturnDistribution(threshold_q=0.10).fit(heavy_tail_returns)
    before = rd.tail_stats()
    sens = rd.threshold_sensitivity(alpha=0.01, threshold_qs=(0.05, 0.10, 0.20))
    assert {"0.05", "0.10", "0.20", "spread", "cv"} <= set(sens)
    assert np.isfinite(sens["spread"]) and sens["spread"] >= 0.0
    assert all(v <= 0.0 for k, v in sens.items() if k not in {"spread", "cv"})  # signed losses
    # estimator state unchanged by the diagnostic
    assert rd.threshold_q == 0.10
    assert rd.tail_stats() == before
