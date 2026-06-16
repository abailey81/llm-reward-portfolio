"""No-look-ahead and reward-timing tests for PortfolioEnv (F.1, audit C-5)."""

from __future__ import annotations

import numpy as np
import pytest

from src.data.panel import Panel
from src.env.portfolio_env import PortfolioEnv, project_simplex
from src.utils.config import load_config


def _port_ret_reward(weights, returns, prev_weights, port_ret, info):
    """Reward = realized portfolio return (stateless)."""
    return float(port_ret), {}, None


def _make_env(panel: Panel) -> PortfolioEnv:
    cfg = load_config("environment")
    return PortfolioEnv(panel, cfg, _port_ret_reward)


def _hand_panel(n_days: int = 80, n_assets: int = 3, seed: int = 7) -> Panel:
    rng = np.random.default_rng(seed)
    returns = rng.normal(0.0, 0.01, size=(n_days, n_assets))
    vix = 10.0 + np.abs(rng.normal(0.0, 5.0, size=n_days))
    dates = np.arange("2010-01-04", n_days, dtype="datetime64[D]")
    asset_ids = np.arange(n_assets, dtype=np.int64)
    caps = np.full((n_days, n_assets), 1e9)
    return Panel(returns=returns, vix=vix, dates=dates, asset_ids=asset_ids, market_caps=caps)


def test_truncation_invariance_over_all_columns() -> None:
    """obs on the panel truncated at t equals obs from the full panel, all columns.

    _obs reads only data with index < t (returns) and t-1 (vix), so building it on
    ``panel.slice(0, t+1)`` (which keeps rows 0..t) must reproduce every column.
    """
    panel = _hand_panel()
    full = _make_env(panel)
    for t in range(full.start, full.T):
        full.t = t
        obs_full = full._obs()

        sub = panel.slice(0, t + 1)  # keeps rows 0..t inclusive
        env_sub = _make_env(sub)
        env_sub.t = t
        env_sub.w_prev = full.w_prev
        obs_sub = env_sub._obs()

        np.testing.assert_array_equal(obs_full, obs_sub)


def test_perturbation_invariance_future_rows_do_not_change_past_obs() -> None:
    """Perturbing future panel rows leaves all past observations unchanged."""
    panel = _hand_panel()
    env = _make_env(panel)
    t = env.start + 5
    env.t = t
    obs_before = env._obs().copy()

    perturbed_returns = panel.returns.copy()
    perturbed_returns[t:] += 100.0  # corrupt every row at or after t
    perturbed_vix = panel.vix.copy()
    perturbed_vix[t:] += 1000.0
    perturbed = Panel(
        returns=perturbed_returns,
        vix=perturbed_vix,
        dates=panel.dates,
        asset_ids=panel.asset_ids,
        market_caps=panel.market_caps,
    )
    env_p = _make_env(perturbed)
    env_p.t = t
    obs_after = env_p._obs()
    np.testing.assert_array_equal(obs_before, obs_after)


def test_obs_never_reads_future_rows() -> None:
    """_obs is invariant to any modification of panel rows with index >= t."""
    panel = _hand_panel()
    env = _make_env(panel)
    rng = np.random.default_rng(0)
    for t in range(env.start, env.T):
        env.t = t
        base = env._obs().copy()
        corrupt = panel.returns.copy()
        corrupt[t:] = rng.normal(0.0, 10.0, size=corrupt[t:].shape)
        cvix = panel.vix.copy()
        cvix[t:] = rng.normal(500.0, 1.0, size=cvix[t:].shape)
        cpanel = Panel(
            returns=corrupt, vix=cvix, dates=panel.dates,
            asset_ids=panel.asset_ids, market_caps=panel.market_caps,
        )
        env_c = _make_env(cpanel)
        env_c.t = t
        np.testing.assert_array_equal(base, env_c._obs())


def test_reward_timing_uses_returns_at_t() -> None:
    """On a known-return panel, the reward at t uses returns[t] (C-5).

    With a zero transaction cost and a known projected weight, the portfolio return
    (and hence the reward) must equal w[:N] @ returns[t] exactly.
    """
    panel = _hand_panel()
    cfg = load_config("environment")
    # zero out cost so reward == gross == w @ returns[t]
    env = PortfolioEnv(panel, cfg, _port_ret_reward)
    env.cost = 0.0
    env.reset(seed=0)

    action = np.zeros(env.N + 1)
    w = project_simplex(action, env.projection)
    t = env.t
    expected = float(w[: env.N] @ panel.returns[t])
    _, reward, _, _, info = env.step(action)
    assert reward == pytest.approx(expected)
    assert info["gross"] == pytest.approx(expected)


def test_reward_timing_shifting_action_shifts_reward() -> None:
    """Shifting the action by one step changes the reward as expected (C-5).

    Applying action A at step t consumes returns[t]; applying the same A one step
    later consumes returns[t+1]. With distinct return rows the rewards differ and
    each matches the contemporaneous realized return.
    """
    panel = _hand_panel()
    cfg = load_config("environment")

    # Make a clearly asymmetric action so different asset weights matter.
    raw = np.array([5.0, -5.0, 0.0, 0.0])  # N=3 + cash

    env_a = PortfolioEnv(panel, cfg, _port_ret_reward)
    env_a.cost = 0.0
    env_a.reset(seed=0)
    w = project_simplex(raw, env_a.projection)
    t0 = env_a.t
    _, reward_t0, _, _, _ = env_a.step(raw)
    assert reward_t0 == pytest.approx(float(w[: env_a.N] @ panel.returns[t0]))

    env_b = PortfolioEnv(panel, cfg, _port_ret_reward)
    env_b.cost = 0.0
    env_b.reset(seed=0)
    env_b.step(np.zeros(env_b.N + 1))  # consume t0 with a neutral action
    t1 = env_b.t
    _, reward_t1, _, _, _ = env_b.step(raw)
    assert reward_t1 == pytest.approx(float(w[: env_b.N] @ panel.returns[t1]))
    assert reward_t0 != pytest.approx(reward_t1)
