"""Tests for src/env/runner.py — the env_builder keystone (MASTER_EXECUTION_PLAN P3).

These are FAST: they use a deterministic fake policy (no Stable-Baselines3 / torch), so
they verify the runner's window logic, rollout shape, determinism, and no-look-ahead
split guard without training an agent.
"""
from __future__ import annotations

import numpy as np
import pytest

from src.data.panel import Panel
from src.env.runner import make_env_builder, rollout_port_returns
from src.utils.config import load_config


class _FakePolicy:
    """Predicts a fixed zero action (-> uniform simplex via softmax). No torch."""

    def __init__(self, n_act: int) -> None:
        self.n_act = n_act

    def predict(self, obs: np.ndarray, deterministic: bool = True):  # noqa: ARG002
        return np.zeros(self.n_act, dtype=np.float32), None


def _reward(weights, returns, prev_weights, port_ret, info):  # noqa: ANN001
    pr = float(port_ret)
    return pr, {"port_ret": pr}, None


@pytest.fixture
def env_cfg():
    return load_config("environment")


def test_rollout_length_matches_window_and_is_finite(synthetic_panel: Panel, env_cfg) -> None:
    """A rollout produces exactly (end - start) finite per-step portfolio returns."""
    lookback = int(env_cfg["state"]["lookback_days"])
    train_window = (lookback, 400)
    val_window = (400, synthetic_panel.T)
    builder = make_env_builder(synthetic_panel, env_cfg, train_window, val_window)
    bundle = builder(_reward)
    policy = _FakePolicy(synthetic_panel.N + 1)

    train_rets = bundle.train_returns(policy)
    val_rets = bundle.val_returns(policy)

    assert train_rets.shape == (train_window[1] - train_window[0],)
    assert val_rets.shape == (val_window[1] - val_window[0],)
    assert np.isfinite(train_rets).all()
    assert np.isfinite(val_rets).all()


def test_rollout_is_deterministic(synthetic_panel: Panel, env_cfg) -> None:
    """The same (panel, reward, policy) yields identical realized returns."""
    lookback = int(env_cfg["state"]["lookback_days"])
    builder = make_env_builder(synthetic_panel, env_cfg, (lookback, 400), (400, synthetic_panel.T))
    bundle = builder(_reward)
    policy = _FakePolicy(synthetic_panel.N + 1)
    a = bundle.val_returns(policy)
    b = bundle.val_returns(policy)
    assert np.array_equal(a, b)


def test_uniform_policy_returns_match_panel_mean(synthetic_panel: Panel, env_cfg) -> None:
    """A uniform (zero-logit -> softmax) policy's net return matches a closed form EVERY step.

    The policy outputs the SAME uniform target ``w = 1/(N+1)`` at every step, so the
    pre-trade weights ``w_prev`` are uniform on every step (the reset weights are uniform
    too). Therefore each step is structurally identical — there is NO special first step:
        gross[t]    = mean over assets of returns[t] * N/(N+1)   (uniform over N risky + cash)
        w_tilde[t]  = uniform * (1+r_t,cash=1) / portfolio_growth   (held weights DRIFT)
        turnover[t] = 0.5 * |uniform - w_tilde[t]|.sum()           (small, NONZERO under drift)
        port_ret[t] = gross[t] - cost * turnover[t]
    Under the half-L1-DRIFTED cost (ADR / docs/environment_spec_v1.md) the held uniform
    weights drift between trades, so there is ongoing turnover every step — the old
    'zero turnover after t0' assumption is wrong. We assert the full net series against
    this closed form to 1e-12, a strong check that the rollout reads realised returns and
    applies the drifted cost correctly.
    """
    from src.env.portfolio_env import PortfolioEnv

    lookback = int(env_cfg["state"]["lookback_days"])
    # Use a bare env (not the builder) so we can roll over a single full window.
    env = PortfolioEnv(synthetic_panel, env_cfg, _reward, start=lookback, end=synthetic_panel.T)
    rets = rollout_port_returns(env, _FakePolicy(synthetic_panel.N + 1))

    n = synthetic_panel.N
    n_act = n + 1
    uniform = np.full(n_act, 1.0 / n_act, dtype=np.float64)
    r = synthetic_panel.returns[lookback:].astype(np.float64)  # (steps, N)

    gross = r.mean(axis=1) * (n / n_act)
    # Drift the uniform pre-trade weights by realized returns (cash element grows at 1.0).
    growth = np.ones((r.shape[0], n_act), dtype=np.float64)
    growth[:, :n] = 1.0 + r
    port_growth = growth @ uniform  # uniform is constant -> w_prev @ growth per step
    w_tilde = uniform[None, :] * growth / port_growth[:, None]
    turnover = 0.5 * np.abs(uniform[None, :] - w_tilde).sum(axis=1)
    expected_net = gross - env.cost * turnover

    # Closed form holds on EVERY step (including the first) to machine precision.
    assert np.allclose(rets, expected_net, atol=1e-12, rtol=0.0)
    # Sanity: drift really does induce nonzero ongoing turnover (so this is not the
    # degenerate zero-cost case the old test silently assumed).
    assert turnover.max() > 0.0


def test_disjoint_split_guard() -> None:
    """make_env_builder rejects a val window that overlaps the train window (audit B-3)."""
    panel = Panel(
        returns=np.zeros((100, 3)),
        vix=np.full(100, 20.0),
        dates=np.arange(100),
        asset_ids=np.arange(3),
    )
    cfg = load_config("environment")
    with pytest.raises(ValueError, match="disjoint"):
        make_env_builder(panel, cfg, (60, 90), (80, 100))  # val starts before train ends


def test_rollout_port_returns_accepts_bare_env(synthetic_panel: Panel, env_cfg) -> None:
    """rollout_port_returns works on a directly-built PortfolioEnv (helper is standalone)."""
    from src.env.portfolio_env import PortfolioEnv

    lookback = int(env_cfg["state"]["lookback_days"])
    env = PortfolioEnv(synthetic_panel, env_cfg, _reward, start=lookback, end=200)
    rets = rollout_port_returns(env, _FakePolicy(synthetic_panel.N + 1))
    assert rets.shape == (200 - lookback,)
    assert np.isfinite(rets).all()


def test_test_leg_sealed_until_test_window_provided(synthetic_panel: Panel, env_cfg) -> None:
    """A selection bundle (no test_window) REFUSES test_returns; a campaign bundle allows it.

    This is the structural seal that makes it impossible to read the 2018-2025 test leg
    during selection (PREREGISTRATION.md §10): every search/selection bundle is 2-window,
    so ``test_returns`` raises; only the campaign's frozen-winner bundle is 3-window.
    """
    lookback = int(env_cfg["state"]["lookback_days"])
    policy = _FakePolicy(synthetic_panel.N + 1)

    # Selection bundle: 2 windows -> the test leg is sealed.
    sealed = make_env_builder(synthetic_panel, env_cfg, (lookback, 300), (300, 400))(_reward)
    assert sealed.test_window is None
    with pytest.raises(RuntimeError, match="sealed"):
        sealed.test_returns(policy)

    # Campaign bundle: 3 windows -> the test leg is reachable with the right shape + finite.
    test_window = (400, synthetic_panel.T)
    campaign = make_env_builder(
        synthetic_panel, env_cfg, (lookback, 300), (300, 400), test_window=test_window
    )(_reward)
    test_rets = campaign.test_returns(policy)
    assert test_rets.shape == (test_window[1] - test_window[0],)
    assert np.isfinite(test_rets).all()


def test_test_leg_embargo_guard(synthetic_panel: Panel, env_cfg) -> None:
    """make_env_builder rejects a test window that violates the val->test embargo."""
    lookback = int(env_cfg["state"]["lookback_days"])
    # train/val satisfy the embargo (300 >= 250 + 21); test (385) violates it (< 380 + 21 = 401).
    with pytest.raises(ValueError, match="test"):
        make_env_builder(
            synthetic_panel,
            env_cfg,
            (lookback, 250),
            (300, 380),
            test_window=(385, synthetic_panel.T),
            embargo=21,
        )


def test_train_val_embargo_guard(synthetic_panel: Panel, env_cfg) -> None:
    """With embargo>0 the val window must clear train_end + embargo, not merely abut it."""
    lookback = int(env_cfg["state"]["lookback_days"])
    with pytest.raises(ValueError, match="embargo"):
        make_env_builder(synthetic_panel, env_cfg, (lookback, 300), (310, 400), embargo=21)
