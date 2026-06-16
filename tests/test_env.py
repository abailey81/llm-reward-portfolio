"""Tests for src/env/portfolio_env.py — construction, stepping, no-NaN (F.1)."""

from __future__ import annotations

import numpy as np
import pytest

from src.data.panel import Panel
from src.env.portfolio_env import PortfolioEnv, project_simplex
from src.utils.config import load_config


def _port_ret_reward(weights, returns, prev_weights, port_ret, info):
    """A reward returning the portfolio return; round-trips a step-counter state."""
    state = info.get("reward_state")
    count = 0 if state is None else int(state) + 1
    return float(port_ret), {"port_ret": float(port_ret)}, count


@pytest.fixture
def env(synthetic_panel: Panel) -> PortfolioEnv:
    cfg = load_config("environment")
    return PortfolioEnv(synthetic_panel, cfg, _port_ret_reward)


def test_env_constructs_with_injected_reward_fn(env: PortfolioEnv) -> None:
    """PortfolioEnv accepts (panel, cfg, reward_fn) and exposes gym spaces (A-4)."""
    assert env.action_space.shape == (env.N + 1,)
    assert env.observation_space.shape[0] == env._obs_dim()
    assert np.dtype(env.observation_space.dtype) == np.float32


def test_reset_returns_obs_in_observation_space(env: PortfolioEnv) -> None:
    """reset returns (obs, info); obs lies in the observation space."""
    obs, info = env.reset(seed=0)
    assert isinstance(info, dict)
    assert env.observation_space.contains(obs)
    assert obs.dtype == np.float32


def test_action_always_on_simplex_under_frozen_projection(env: PortfolioEnv) -> None:
    """Every projected action is non-negative and sums to 1 (frozen projection, C-8)."""
    rng = np.random.default_rng(1)
    env.reset(seed=0)
    for _ in range(50):
        action = rng.standard_normal(env.N + 1) * 5.0
        w = project_simplex(action, env.projection)
        assert np.all(w >= 0.0)
        assert w.sum() == pytest.approx(1.0)
        env.step(action)


def test_log_wealth_has_no_nans_across_full_panel(env: PortfolioEnv) -> None:
    """Stepping through the whole panel produces no NaN in obs or log-wealth."""
    obs, _ = env.reset(seed=0)
    assert np.isfinite(obs).all()
    rng = np.random.default_rng(2)
    terminated = False
    while not terminated:
        action = rng.standard_normal(env.N + 1)
        obs, reward, terminated, truncated, info = env.step(action)
        assert np.isfinite(obs).all()
        assert np.isfinite(env.log_wealth)
        assert not truncated or terminated
    assert np.isfinite(env.log_wealth)


def test_step_returns_gymnasium_five_tuple(env: PortfolioEnv) -> None:
    """step returns (obs, reward, terminated, truncated, info) with reward a float."""
    env.reset(seed=0)
    out = env.step(np.zeros(env.N + 1))
    assert len(out) == 5
    obs, reward, terminated, truncated, info = out
    assert isinstance(obs, np.ndarray)
    assert isinstance(reward, float)
    assert isinstance(terminated, bool)
    assert isinstance(truncated, bool)
    assert isinstance(info, dict)


def test_reward_state_round_trips_via_info(env: PortfolioEnv) -> None:
    """reward_state from one step is delivered to the next via info (stateful, B-4)."""
    env.reset(seed=0)
    _, _, _, _, info0 = env.step(np.zeros(env.N + 1))
    assert info0["reward_state"] == 0
    _, _, _, _, info1 = env.step(np.zeros(env.N + 1))
    assert info1["reward_state"] == 1
    _, _, _, _, info2 = env.step(np.zeros(env.N + 1))
    assert info2["reward_state"] == 2
