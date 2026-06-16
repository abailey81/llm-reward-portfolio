"""Behaviour tests for the selection-aware inference stack (FINAL_PLAN F.11)."""

from __future__ import annotations


import math

import numpy as np
import pytest
from scipy.stats import norm

from src.inference.bootstrap import (
    cvar,
    cvar_difference_test,
    null_calibration,
    sharpe_difference_test,
    sharpe_ratio,
    stationary_bootstrap_indices,
)
from src.inference.deflated_sharpe import (
    deflated_sharpe_ratio,
    expected_max_sharpe,
    probabilistic_sharpe_ratio,
)
from src.inference.multiple_testing import benjamini_hochberg, romano_wolf
from src.inference.overfitting import pbo
from src.inference.reporting import (
    iqm,
    probability_of_improvement,
    stratified_bootstrap_ci,
)


# ---------------------------------------------------------------------------
# bootstrap.py
# ---------------------------------------------------------------------------
def _mean_run_length(idx: np.ndarray) -> float:
    """Mean length of consecutive +1 (mod n) runs in an index path."""
    n = idx.size
    runs = []
    cur = 1
    for t in range(1, n):
        if idx[t] == (idx[t - 1] + 1) % n:
            cur += 1
        else:
            runs.append(cur)
            cur = 1
    runs.append(cur)
    return float(np.mean(runs))


def test_bootstrap_indices_length_and_range(rng) -> None:
    n = 500
    idx = stationary_bootstrap_indices(n, p=0.1, rng=rng)
    assert idx.shape == (n,)
    assert idx.min() >= 0 and idx.max() < n
    assert idx.dtype.kind == "i"


def test_bootstrap_block_structure_grows_as_p_shrinks(rng) -> None:
    """p~1 => ~iid (short runs); small p => long blocks."""
    n = 2000
    rl_iid = _mean_run_length(stationary_bootstrap_indices(n, p=0.99, rng=rng))
    rl_small = _mean_run_length(stationary_bootstrap_indices(n, p=0.05, rng=rng))
    assert rl_iid < 1.5  # near-iid: almost every step restarts
    assert rl_small > rl_iid
    # Expected block length is ~1/p; 1/0.05 = 20, allow generous tolerance.
    assert rl_small > 5.0


def test_sharpe_ratio_sign_and_scale() -> None:
    # Constant series has zero std => Sharpe defined as 0.0.
    assert sharpe_ratio(np.full(1000, 0.01)) == 0.0
    rng = np.random.default_rng(0)
    good = 0.001 + 0.01 * rng.standard_normal(50_000)
    bad = -0.001 + 0.01 * rng.standard_normal(50_000)
    assert sharpe_ratio(good) > 0
    assert sharpe_ratio(bad) < 0
    # Annualization scales by sqrt(252).
    daily = sharpe_ratio(good, periods_per_year=1)
    annual = sharpe_ratio(good, periods_per_year=252)
    assert annual == pytest.approx(daily * math.sqrt(252), rel=1e-9)


def test_cvar_monotone_in_alpha(normal_returns) -> None:
    c1 = cvar(normal_returns, 0.01)
    c5 = cvar(normal_returns, 0.05)
    c10 = cvar(normal_returns, 0.10)
    # All negative (lower tail of N(0,1)).
    assert c1 < 0 and c5 < 0 and c10 < 0
    # Smaller alpha => more extreme => more negative.
    assert c1 < c5 < c10
    # Closed-form ES of N(0,1) at 5%: -phi(z)/alpha ~ -2.063.
    assert c5 == pytest.approx(-2.063, abs=0.05)


def _equal_pair_sampler(rng):
    a = 0.0005 + 0.01 * rng.standard_normal(800)
    b = 0.0005 + 0.01 * rng.standard_normal(800)
    return a, b


def test_sharpe_test_null_calibration() -> None:
    rng = np.random.default_rng(7)

    def test_fn(a, b):
        return sharpe_difference_test(a, b, n_boot=600, rng=rng)

    res = null_calibration(test_fn, _equal_pair_sampler, n_reps=160, rng=rng)
    assert res["rejection_rate"] <= 0.15
    assert 0.35 <= res["mean_pvalue"] <= 0.65


def test_cvar_test_null_calibration() -> None:
    rng = np.random.default_rng(11)

    def test_fn(a, b):
        return cvar_difference_test(a, b, alpha=0.05, n_boot=600, rng=rng)

    res = null_calibration(test_fn, _equal_pair_sampler, n_reps=160, rng=rng)
    assert res["rejection_rate"] <= 0.15
    assert 0.35 <= res["mean_pvalue"] <= 0.65


def test_sharpe_test_returns_keys(rng) -> None:
    a = 0.001 + 0.01 * rng.standard_normal(500)
    b = 0.0005 + 0.01 * rng.standard_normal(500)
    res = sharpe_difference_test(a, b, n_boot=500, rng=rng)
    assert set(res) == {"stat", "pvalue", "ci_low", "ci_high"}
    assert 0.0 <= res["pvalue"] <= 1.0
    assert res["ci_low"] <= res["ci_high"]


# ---------------------------------------------------------------------------
# overfitting.py (PBO / CSCV)
# ---------------------------------------------------------------------------
def test_pbo_in_unit_interval() -> None:
    rng = np.random.default_rng(1)
    mat = rng.standard_normal((400, 10))
    val = pbo(mat, n_blocks=10, rng=rng)
    assert 0.0 <= val <= 1.0


def test_pbo_zero_when_one_config_dominates() -> None:
    rng = np.random.default_rng(2)
    t, n = 400, 8
    mat = rng.standard_normal((t, n)) * 0.1
    # Config 0 has a large mean everywhere -> best IS and best OOS always.
    mat[:, 0] += 5.0
    val = pbo(mat, n_blocks=10, rng=rng)
    assert val == pytest.approx(0.0, abs=0.02)


def test_pbo_near_half_on_pure_noise() -> None:
    vals = []
    for seed in range(5):
        rng = np.random.default_rng(100 + seed)
        mat = rng.standard_normal((500, 12))
        vals.append(pbo(mat, n_blocks=12, rng=rng))
    assert np.mean(vals) == pytest.approx(0.5, abs=0.15)


# ---------------------------------------------------------------------------
# deflated_sharpe.py
# ---------------------------------------------------------------------------
def test_psr_matches_hand_computed_normal() -> None:
    # Normal: skew 0, kurt 3 => denom var = 1 + (3-1)/4 * sr^2.
    sr, n = 0.1, 101
    denom = math.sqrt(1.0 + (3.0 - 1.0) / 4.0 * sr * sr)
    expected = float(norm.cdf(sr * math.sqrt(n - 1) / denom))
    got = probabilistic_sharpe_ratio(sr, 0.0, n, skew=0.0, kurt=3.0)
    assert got == pytest.approx(expected, abs=1e-10)
    assert 0.0 <= got <= 1.0


def test_dsr_in_unit_interval_and_monotone_in_trials() -> None:
    rng = np.random.default_rng(3)
    returns = 0.0008 + 0.01 * rng.standard_normal(2000)
    d_few = deflated_sharpe_ratio(returns, n_trials=2)
    d_many = deflated_sharpe_ratio(returns, n_trials=500)
    assert 0.0 <= d_few <= 1.0 and 0.0 <= d_many <= 1.0
    # More trials => higher SR_star => lower DSR.
    assert d_many <= d_few


def test_expected_max_sharpe_increases_with_trials() -> None:
    e10 = expected_max_sharpe(1.0, 10)
    e1000 = expected_max_sharpe(1.0, 1000)
    assert e1000 > e10 > 0.0


# ---------------------------------------------------------------------------
# multiple_testing.py
# ---------------------------------------------------------------------------
def test_bh_controls_fdr_on_all_null() -> None:
    rng = np.random.default_rng(4)
    rates = []
    for _ in range(40):
        pvals = rng.random(50)  # all-null => Uniform(0,1)
        rej = benjamini_hochberg(pvals, q=0.1)
        rates.append(rej.mean())
    # Under all-null, expected number of rejections is tiny.
    assert np.mean(rates) <= 0.1


def test_bh_rejects_tiny_pvalue_in_nulls() -> None:
    rng = np.random.default_rng(5)
    pvals = rng.random(50)
    pvals[7] = 1e-8
    rej = benjamini_hochberg(pvals, q=0.1)
    assert rej[7]


def test_bh_monotone_in_q() -> None:
    rng = np.random.default_rng(6)
    pvals = np.sort(rng.random(40))
    pvals[:5] = np.array([0.001, 0.004, 0.01, 0.02, 0.03])
    r_low = benjamini_hochberg(pvals, q=0.05)
    r_high = benjamini_hochberg(pvals, q=0.25)
    # Larger q rejects a superset.
    assert np.all(r_high[r_low])


def test_romano_wolf_rejects_strong_signal() -> None:
    rng = np.random.default_rng(8)
    m = 6
    boot = rng.standard_normal((2000, m))  # centred null draws
    stats = np.array([5.0, 0.1, 0.2, 0.0, 0.3, 0.1])  # hypothesis 0 is strong
    rej = romano_wolf(stats, boot, alpha=0.05)
    assert rej[0]
    assert not rej[3]


# ---------------------------------------------------------------------------
# reporting.py
# ---------------------------------------------------------------------------
def test_iqm_matches_fixture() -> None:
    data = np.arange(1, 101, dtype=float)  # 1..100
    assert iqm(data) == pytest.approx(50.5, abs=1e-9)


def test_iqm_robust_to_outliers() -> None:
    base = np.arange(1, 101, dtype=float)
    contaminated = np.concatenate([base, [1e9, 1e9, -1e9, -1e9]])
    assert iqm(contaminated) == pytest.approx(iqm(base), abs=2.0)


def test_probability_of_improvement_fixture() -> None:
    a = np.array([10.0, 11.0, 12.0])
    b = np.array([1.0, 2.0, 3.0])
    assert probability_of_improvement(a, b) == pytest.approx(1.0)
    assert probability_of_improvement(b, a) == pytest.approx(0.0)
    # Equal populations => 0.5 (all ties).
    c = np.array([5.0, 5.0])
    assert probability_of_improvement(c, c) == pytest.approx(0.5)


def test_stratified_bootstrap_ci_brackets_iqm(rng) -> None:
    scores = 1.0 + 0.5 * rng.standard_normal(200)
    point, low, high = stratified_bootstrap_ci(scores, n_boot=1000, ci=0.95, rng=rng)
    assert point == pytest.approx(iqm(scores))
    assert low < high
    assert low <= point <= high
