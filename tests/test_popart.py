"""Behaviour tests for PopArt-style value-target scale normalization (src/agents/popart.py).

The engine gap the prototype exposed: an LLM reward that divides a one-step return by a variance
floored at 1e-8 emits |reward| ~ 1e4, which drives SAC's Bellman target to ~1e4/(1-gamma) ~ 1e6 and
explodes the critic loss to ~5e6 at the LAST training step (outputs/prototype/anomalies.jsonl). PopArt
scale-normalization makes the critic invariant to the reward SCALE (van Hasselt et al. 2016), holding
the regression target at unit scale WITHOUT rescaling info["port_ret"] (the object of study).

Two layers:
  - FAST unit invariances (default run): the wrapper preserves info["port_ret"] byte-for-byte, leaves a
    well-behaved unit-scale reward essentially unchanged, and shrinks a 1e4-magnitude reward to ~O(1).
  - SLOW end-to-end (``-m slow``): training the fixed SAC on the EXACT variance-floor reward pattern
    diverges the critic WITHOUT PopArt and stays bounded WITH it — the load-bearing proof.
"""
from __future__ import annotations

import numpy as np
import pytest

from src.agents.popart import PopArtRewardScaler, wrap_popart
from src.data.panel import Panel
from src.env.portfolio_env import PortfolioEnv
from src.utils.config import load_config


# The EXACT pathology verified in the archive (prototype scalar-g5-c3): a per-step Sharpe with the
# std floored at 1e-8, so a single early return becomes mu/1e-8*0.1 ~ 1e4. This is the object that
# blows the critic up; the test reproduces it faithfully.
_EXPLODING_REWARD_SRC = """
def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np
    st = info.get("reward_state") or {"hist": []}
    hist = st["hist"]
    hist.append(float(port_ret))
    arr = np.array(hist, dtype=np.float64)
    n = len(arr)
    if n >= 5:
        mu = float(np.mean(arr)); sigma = float(np.std(arr, ddof=1)) + 1e-8
        sharpe = mu / sigma
    else:
        mu = float(np.mean(arr)) if n > 0 else 0.0
        sigma = 1e-8
        sharpe = mu / sigma * 0.1   # <-- single-sample: mu/1e-8 ~ 1e4 (the explosion source)
    return float(sharpe), {"sharpe": float(sharpe)}, {"hist": hist}
"""


def _exploding_reward(weights, returns, prev_weights, port_ret, info):  # noqa: ANN001
    st = info.get("reward_state") or {"hist": []}
    hist = st["hist"]
    hist.append(float(port_ret))
    arr = np.array(hist, dtype=np.float64)
    n = len(arr)
    if n >= 5:
        mu = float(np.mean(arr))
        sigma = float(np.std(arr, ddof=1)) + 1e-8
        sharpe = mu / sigma
    else:
        mu = float(np.mean(arr)) if n > 0 else 0.0
        sharpe = mu / 1e-8 * 0.1
    return float(sharpe), {"sharpe": float(sharpe)}, {"hist": hist}


# --------------------------------------------------------------------------- #
# FAST unit invariances                                                        #
# --------------------------------------------------------------------------- #
def test_popart_preserves_port_ret_and_info(synthetic_panel: Panel) -> None:
    """The wrapper forwards info UNCHANGED — info['port_ret'] (the object of study) is byte-for-byte."""
    cfg = load_config("environment")
    # Two INDEPENDENT envs (separate w_prev/reward_state), stepped with identical actions: the bare env
    # and a wrapped fresh copy must realize the SAME info['port_ret'] (the wrapper touches only the reward).
    bare = PortfolioEnv(synthetic_panel, cfg, _exploding_reward)
    wrapped = PopArtRewardScaler(
        PortfolioEnv(synthetic_panel, cfg, _exploding_reward), warmup=0
    )  # warmup=0 so it normalizes immediately
    bare.reset(seed=0)
    wrapped.reset(seed=0)
    rng = np.random.default_rng(0)
    saw_scaling = False
    for _ in range(30):
        a = rng.standard_normal(synthetic_panel.N + 1).astype(np.float32)
        _o0, r_bare, _t0, _tr0, i_bare = bare.step(a)
        _o1, r_wrap, _t1, _tr1, i_wrap = wrapped.step(a)
        # info['port_ret'] is the realized return — IDENTICAL through the wrapper.
        assert i_wrap["port_ret"] == pytest.approx(i_bare["port_ret"], abs=0.0)
        # and the scaled LEARNING reward differs from the raw reward once the scale has moved off 1.
        if abs(float(r_wrap) - float(r_bare)) > 1e-9:
            saw_scaling = True
    assert saw_scaling, "PopArt must scale the learning reward away from the raw reward on this stream"


def test_popart_shrinks_large_reward_but_keeps_unit_reward() -> None:
    """sigma scales a 1e4-magnitude stream to ~O(1); a unit-scale stream is left ~unchanged (min_scale=1)."""
    # Large-magnitude stream: feed constant ~1e4 rewards; after warmup the scaled output is ~O(1).
    big = PopArtRewardScaler(_DummyEnv(reward=1.0e4), warmup=5, beta=0.5)
    big.reset()
    outs = [big.step(0)[1] for _ in range(200)]
    tail = np.abs(outs[-20:])
    assert tail.max() < 5.0, f"large reward not shrunk to O(1): max|scaled|={tail.max():.3g}"

    # Unit-scale stream: min_scale=1.0 means sigma never drops below 1, so a ~unit reward passes through.
    small = PopArtRewardScaler(_DummyEnv(reward=0.5), warmup=5, beta=0.5)
    small.reset()
    souts = [small.step(0)[1] for _ in range(200)]
    assert np.allclose(souts[-20:], 0.5, atol=1e-6), "a unit-scale reward must be ~unchanged (min_scale=1)"


def test_wrap_popart_off_is_identity(synthetic_panel: Panel) -> None:
    """wrap_popart returns the bare env when popart is disabled (explicit opt-out parity)."""
    cfg = load_config("environment")
    env = PortfolioEnv(synthetic_panel, cfg, _exploding_reward)
    assert wrap_popart(env, {"popart": False}) is env
    assert isinstance(wrap_popart(env, {"popart": True}), PopArtRewardScaler)


def test_realized_scale_tracks_unit_vs_large_reward() -> None:
    """T2.4: sigma_max == 1.0 for a unit-scale reward (identity) and > 1 for a large-magnitude one.

    This is the cross-arm audit signal: a unit ``sigma_max`` across arms proves the wrapper was the
    identity everywhere, so there is no scale-driven entropy-regularisation difference between arms.
    """
    unit = PopArtRewardScaler(_DummyEnv(reward=0.5), warmup=0)
    unit.reset()
    for _ in range(50):
        unit.step(0)
    su = unit.realized_scale_stats()
    assert su["popart"] == 1.0
    assert su["sigma_max"] == pytest.approx(1.0)  # min_scale floor -> identity for a sub-unit reward
    assert su["sigma_last"] == pytest.approx(1.0)
    assert su["count"] == 50.0

    big = PopArtRewardScaler(_DummyEnv(reward=1.0e4), warmup=0, beta=0.5)
    big.reset()
    for _ in range(50):
        big.step(0)
    sb = big.realized_scale_stats()
    assert sb["sigma_max"] > 100.0, f"large reward must drive sigma_max well above 1: {sb['sigma_max']}"
    # sigma_max is the running MAX, so it is >= the last scale.
    assert sb["sigma_max"] >= sb["sigma_last"]


def test_realized_scale_stats_helper_handles_on_and_off() -> None:
    """The module-level helper returns the scaler's stats when on, and a {"popart":0.0} marker when off."""
    from src.agents.popart import realized_scale_stats

    on = PopArtRewardScaler(_DummyEnv(reward=1.0), warmup=0)
    on.reset()
    on.step(0)
    assert realized_scale_stats(on)["popart"] == 1.0
    # popart off -> wrap_popart returns the bare env -> helper marks it explicitly (not a silent None).
    bare = _DummyEnv(reward=1.0)
    assert realized_scale_stats(bare) == {"popart": 0.0}


@pytest.mark.parametrize(
    "cfg, expected",
    [
        ({}, 1000),                          # UNSET -> the gated 1000, NOT SB3's silent default of 100
        ({"learning_starts": 100}, 1000),    # a too-small value is FLOORED to the gate's 1000
        ({"learning_starts": 5000}, 5000),   # a larger value is honoured
    ],
)
def test_learning_starts_resolved_and_floored(cfg, expected) -> None:
    """resolve_agent_kwargs sets learning_starts (was UNSET -> SB3 default 100, a gate/study mismatch).

    The Phase-0 GATE (scripts/smoke_test.py) validated learning_starts=1000, but the live trainer never
    set it, so the campaign would have trained at SB3's silent 100 — a different warmup than was gated.
    """
    from src.agents.trainer import resolve_agent_kwargs

    kwargs, _ = resolve_agent_kwargs(cfg, seed=0)
    assert kwargs["learning_starts"] == expected


import gymnasium as gym  # noqa: E402


class _DummyEnv(gym.Env):  # type: ignore[misc]
    """A minimal gymnasium.Env emitting a CONSTANT reward (isolates the scaler's arithmetic)."""

    def __init__(self, reward: float) -> None:
        super().__init__()
        self._r = float(reward)
        self.observation_space = gym.spaces.Box(-1.0, 1.0, shape=(1,), dtype=np.float32)
        self.action_space = gym.spaces.Box(-1.0, 1.0, shape=(1,), dtype=np.float32)

    def reset(self, **kwargs):  # noqa: ANN003, ANN201
        return np.zeros(1, dtype=np.float32), {}

    def step(self, action):  # noqa: ANN001, ANN201
        return np.zeros(1, dtype=np.float32), self._r, False, False, {"port_ret": self._r}


# --------------------------------------------------------------------------- #
# SLOW end-to-end: the load-bearing divergence proof                          #
# --------------------------------------------------------------------------- #
@pytest.mark.slow
def test_popart_prevents_critic_explosion_on_pathological_reward(synthetic_panel: Panel) -> None:
    """Training the fixed SAC on the variance-floor reward: critic diverges WITHOUT PopArt, bounded WITH.

    This is the behaviour the prototype anomalies showed (critic_loss -> ~1e6). With PopArt the target
    is held at unit scale, so the max critic loss stays many orders of magnitude smaller and finite.
    """
    from src.agents.trainer import train_agent
    from src.env.runner import make_env_builder

    cfg = load_config("environment")
    lookback = int(cfg["state"]["lookback_days"])
    builder = make_env_builder(
        synthetic_panel, cfg, (lookback, 400), (400, synthetic_panel.T)
    )

    def _max_critic_loss(popart: bool) -> float:
        # Capture critic loss via a tiny callback (reusing the smoke-test recorder pattern).
        from stable_baselines3.common.callbacks import BaseCallback

        losses: list[float] = []

        class _Rec(BaseCallback):
            def _on_step(self) -> bool:
                v = self.model.logger.name_to_value.get("train/critic_loss")
                if v is not None and np.isfinite(v):
                    losses.append(float(v))
                return True

        bundle = builder(_exploding_reward)
        agent_cfg = {
            "train_steps_per_candidate": 1500,
            "learning_starts": 100,   # short warmup so the critic regresses within the test budget
            "normalize_obs": True,
            "popart": popart,
            "popart_warmup": 0,       # scale from step 1 (the bias-corrected EMA normalizes the opening reward)
            "seed": 0,
        }
        train_agent(bundle.train_env(), agent_cfg, seed=0, callback=_Rec())
        return max(losses) if losses else 0.0

    with_popart = _max_critic_loss(popart=True)
    without_popart = _max_critic_loss(popart=False)

    # WITHOUT PopArt the variance-floor reward (|r|~1e4) blows the critic up by orders of magnitude;
    # WITH PopArt the target is unit-scaled so the loss stays bounded. Assert both the absolute bound
    # and the large relative gap (robust to SAC noise across SB3 versions).
    assert np.isfinite(with_popart)
    assert with_popart < 1.0e3, f"PopArt critic loss not bounded: {with_popart:.3g}"
    assert without_popart > 50.0 * (with_popart + 1e-9), (
        f"expected divergence without PopArt to dwarf the PopArt run: "
        f"without={without_popart:.3g} vs with={with_popart:.3g}"
    )
