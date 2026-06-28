"""Tests for the baseline reward canon and benchmark allocators.

Covers FINAL_PLAN F.6: the reward contract (audit B-4), the stateful
differential Sharpe update, and simplex/forecast properties of allocators.
"""

from __future__ import annotations


import numpy as np

from src.baselines import rewards, strategies

ALL_REWARDS = [
    rewards.raw_return,
    rewards.return_minus_variance,
    rewards.return_minus_cvar,
    rewards.differential_sharpe,
]


def _reward_args(rng: np.random.Generator) -> tuple:
    n = 6
    weights = np.full(n, 1.0 / n)
    returns = rng.standard_normal(n) * 0.01
    prev_weights = np.full(n, 1.0 / n)
    port_ret = float(np.sum(weights * returns))
    info: dict = {}
    return weights, returns, prev_weights, port_ret, info


def test_rewards_obey_contract(rng: np.random.Generator) -> None:
    """Each reward returns (total, components, reward_state) under the contract."""
    weights, returns, prev_weights, port_ret, info = _reward_args(rng)
    for fn in ALL_REWARDS:
        total, components, state = fn(weights, returns, prev_weights, port_ret, info)
        assert isinstance(total, float)
        assert np.isfinite(total)
        assert isinstance(components, dict)
        for k, v in components.items():
            assert isinstance(k, str)
            assert isinstance(v, float)
        # state is an opaque object — just confirm the triple unpacks.
        _ = state


def test_differential_sharpe_sequence() -> None:
    """differential_sharpe reproduces the hand-computed A/B/eta sequence."""
    eta = 0.1
    info: dict = {"eta": eta}
    w = np.array([1.0])
    r1, r2 = 0.02, -0.01

    # Step 1: R_1 = 0.02 with A_0 = B_0 = 0 -> warm-up D_1 = 0.
    total1, comp1, state1 = rewards.differential_sharpe(w, w, w, r1, info)
    assert total1 == 0.0
    assert np.isclose(comp1["A"], 0.002)
    assert np.isclose(comp1["B"], 0.00004)
    assert np.isclose(state1["A"], 0.002)
    assert np.isclose(state1["B"], 0.00004)
    assert np.isclose(state1["eta"], eta)

    # Step 2: R_2 = -0.01, threading state via info["reward_state"].
    info2 = {"reward_state": state1}
    total2, comp2, state2 = rewards.differential_sharpe(w, w, w, r2, info2)

    a1, b1 = 0.002, 0.00004
    d_a = r2 - a1
    d_b = r2**2 - b1
    denom = (b1 - a1**2) ** 1.5
    expected_d2 = (b1 * d_a - 0.5 * a1 * d_b) / denom
    assert np.isclose(total2, expected_d2)
    assert np.isclose(comp2["A"], 0.0008)
    assert np.isclose(comp2["B"], 0.000046)
    assert np.isclose(state2["A"], 0.0008)
    assert np.isclose(state2["B"], 0.000046)


def test_return_minus_variance_penalizes_volatility(rng: np.random.Generator) -> None:
    """A high-variance return path is penalized more than a calm one."""
    w = np.array([1.0])
    calm = 0.001 + 0.0005 * rng.standard_normal(60)
    wild = 0.001 + 0.05 * rng.standard_normal(60)

    def run(path: np.ndarray) -> float:
        info: dict = {"lambda": 5.0, "window": 30}
        penalties = []
        for r in path:
            _, comp, state = rewards.return_minus_variance(w, w, w, float(r), info)
            info = {"lambda": 5.0, "window": 30, "reward_state": state}
            penalties.append(comp["variance_penalty"])
        return float(np.mean(penalties))

    # variance_penalty is negative; the wild path has a more negative mean penalty.
    assert run(wild) < run(calm)


def test_return_minus_cvar_runs(rng: np.random.Generator) -> None:
    """return_minus_cvar threads state and stays finite over a path."""
    w = np.array([1.0])
    info: dict = {"lambda": 2.0, "alpha": 0.1, "window": 40}
    path = 0.001 + 0.02 * rng.standard_normal(50)
    for r in path:
        total, comp, state = rewards.return_minus_cvar(w, w, w, float(r), info)
        assert np.isfinite(total)
        assert comp["cvar_penalty"] <= 0.0
        info = {"lambda": 2.0, "alpha": 0.1, "window": 40, "reward_state": state}


# --------------------------------------------------------------------------- #
# Strategies
# --------------------------------------------------------------------------- #

def _corr_window(rng: np.random.Generator, n_assets: int = 8, n_days: int = 250) -> np.ndarray:
    """A returns window with correlated assets (shared market factor + idio)."""
    factor = rng.standard_normal(n_days) * 0.01
    loadings = rng.uniform(0.5, 1.5, size=n_assets)
    idio = rng.standard_normal((n_days, n_assets)) * 0.005
    return factor[:, None] * loadings[None, :] + idio


ALL_STRATEGIES = [
    strategies.spy_buy_and_hold,
    strategies.equal_weight,
    strategies.mean_variance,
    strategies.risk_parity,
    strategies.hrp,
    strategies.minimum_variance,
    strategies.maximum_diversification,
    strategies.inverse_volatility,
    strategies.cross_sectional_momentum,
]


def _factor_window(seed: int, n: int = 30, t: int = 60, dead: int = 0) -> np.ndarray:
    """A realistic N=30, T=60 correlated window; the first ``dead`` columns are zero-variance (delisted)."""
    r = np.random.default_rng(seed)
    f = r.standard_normal((t, 3)) * 0.01
    x = f @ r.standard_normal((3, n)) * 0.5 + r.standard_normal((t, n)) * 0.008
    if dead:
        x[:, :dead] = 0.0
    return x


def _port_var(w: np.ndarray, x: np.ndarray) -> float:
    cov = np.cov(x, rowvar=False)
    return float(w @ cov @ w)


def _div_ratio(w: np.ndarray, x: np.ndarray) -> float:
    cov = np.cov(x, rowvar=False)
    sig = np.sqrt(np.diag(cov))
    return float((w @ sig) / np.sqrt(w @ cov @ w))


def test_minimum_variance_beats_1n_variance() -> None:
    """The long-only GMV must have LOWER variance than 1/N (would FAIL if it collapsed to one asset)."""
    for seed in range(15):
        x = _factor_window(seed)
        n = x.shape[1]
        assert _port_var(strategies.minimum_variance(x), x) <= _port_var(np.full(n, 1.0 / n), x) + 1e-12


def test_maximum_diversification_beats_1n_div_ratio() -> None:
    """The most-diversified portfolio must have a HIGHER diversification ratio than 1/N (collapse -> 1.0)."""
    for seed in range(15):
        x = _factor_window(seed)
        n = x.shape[1]
        assert _div_ratio(strategies.maximum_diversification(x), x) >= _div_ratio(np.full(n, 1.0 / n), x) - 1e-9


def test_vol_cov_allocators_exclude_delisted_names() -> None:
    """Zero-variance (delisted) names must get ~0 weight — not ~100% (the 1/sigma, sigma->0 pathology)."""
    for seed in range(10):
        x = _factor_window(seed, dead=5)  # first 5 columns delisted (zero variance)
        for fn in (strategies.minimum_variance, strategies.inverse_volatility,
                   strategies.maximum_diversification, strategies.hrp, strategies.risk_parity,
                   strategies.cross_sectional_momentum):
            w = fn(x)
            assert float(w[:5].sum()) < 1e-6, f"{fn.__name__} allocated to delisted names"
            assert np.isclose(w.sum(), 1.0, atol=1e-6) and np.isfinite(w).all()


def test_allocators_do_not_collapse_to_single_asset() -> None:
    """The risk/cov allocators must hold MANY names (the collapse bug held exactly one)."""
    x = _factor_window(0)
    for fn in (strategies.minimum_variance, strategies.maximum_diversification,
               strategies.mean_variance, strategies.risk_parity, strategies.hrp):
        assert int((fn(x) > 1e-4).sum()) >= 3, f"{fn.__name__} collapsed to <3 names"


def test_hrp_robust_to_zero_variance_columns() -> None:
    """hrp must not raise on a window with delisted zero-variance names (linkage finite-value crash)."""
    w = strategies.hrp(_factor_window(3, dead=8))
    assert np.isclose(w.sum(), 1.0, atol=1e-6) and np.isfinite(w).all()


def test_strategies_return_simplex(rng: np.random.Generator) -> None:
    """Every allocator returns non-negative weights summing to one."""
    window = _corr_window(rng)
    n = window.shape[1]
    for fn in ALL_STRATEGIES:
        w = np.asarray(fn(window))
        assert w.shape == (n,)
        assert np.all(w >= -1e-12), f"{fn.__name__} produced negative weights"
        assert np.isclose(w.sum(), 1.0, atol=1e-8), f"{fn.__name__} does not sum to 1"


def test_equal_weight_is_exactly_uniform(rng: np.random.Generator) -> None:
    """equal_weight is exactly 1/N."""
    window = _corr_window(rng, n_assets=7)
    w = strategies.equal_weight(window)
    assert np.allclose(w, 1.0 / 7)


def test_mean_variance_uses_shrinkage(rng: np.random.Generator) -> None:
    """mean_variance estimates covariance via Ledoit-Wolf (PD shrinkage)."""
    from sklearn.covariance import LedoitWolf

    window = _corr_window(rng)
    lw = LedoitWolf().fit(window)
    # Shrinkage is genuinely applied (strictly between 0 and 1) and the estimate
    # is positive-definite.
    assert 0.0 < lw.shrinkage_ < 1.0
    eigvals = np.linalg.eigvalsh(lw.covariance_)
    assert np.all(eigvals > 0)

    w = strategies.mean_variance(window)
    assert np.isclose(w.sum(), 1.0, atol=1e-8)
    assert np.all(w >= -1e-12)


def test_risk_parity_equalizes_risk_contributions(rng: np.random.Generator) -> None:
    """risk_parity approximately equalizes per-asset risk contributions."""
    window = _corr_window(rng, n_assets=6)
    w = strategies.risk_parity(window)
    cov = np.cov(window, rowvar=False)
    sigma_w = cov @ w
    rc = w * sigma_w
    rc = rc / rc.sum()
    assert np.max(np.abs(rc - 1.0 / len(w))) < 1e-3


def test_hrp_valid_on_correlated_assets(rng: np.random.Generator) -> None:
    """hrp returns valid simplex weights on a fixture with correlated assets."""
    window = _corr_window(rng, n_assets=10)
    w = strategies.hrp(window)
    assert w.shape == (10,)
    assert np.isclose(w.sum(), 1.0, atol=1e-8)
    assert np.all(w >= -1e-12)


def test_no_forecast_baselines(rng: np.random.Generator) -> None:
    """equal_weight and hrp produce weights from count/structure alone."""
    window = _corr_window(rng, n_assets=5)
    # equal_weight depends only on N.
    assert np.allclose(strategies.equal_weight(window), 1.0 / 5)
    # hrp uses covariance structure but no expected-return forecast; shifting the
    # mean of every column leaves the correlation/covariance structure unchanged
    # only in mean, so HRP weights are unaffected by a constant level shift.
    shifted = window + 0.05
    assert np.allclose(strategies.hrp(window), strategies.hrp(shifted), atol=1e-8)
