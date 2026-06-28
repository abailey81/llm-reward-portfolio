"""Tests for the live H4 reward family (P5; src/baselines/reward_family.py).

The family must obey the LIVE 5-arg/3-tuple contract (the archived version used the old
RewardContext contract), expose a (6,2) search box, and accumulate rolling stats via reward_state.
"""
from __future__ import annotations

import numpy as np
import pytest

from src.baselines.reward_family import WEIGHT_KEYS, family_bounds, params_to_reward
from src.reward.contract import validate_signature


def test_family_bounds_shape_and_order() -> None:
    b = family_bounds()
    assert b.shape == (len(WEIGHT_KEYS), 2)
    assert (b[:, 0] <= b[:, 1]).all()
    # Frozen ranges (mirror eureka_loop.yaml).
    assert tuple(b[0]) == (0.0, 2.0)  # w_return
    assert tuple(b[2]) == (0.0, 0.02)  # w_turnover


def test_family_bounds_reads_cfg() -> None:
    cfg = {"reward_family": {"weights": {"w_return": {"low": 0.5, "high": 1.5}}}}
    b = family_bounds(cfg)
    assert tuple(b[0]) == (0.5, 1.5)


def test_params_to_reward_obeys_live_contract() -> None:
    reward = params_to_reward(np.array([1.0, 0.5, 0.01, 0.05, 1.0, 0.5]))
    assert validate_signature(reward)  # exactly (weights, returns, prev_weights, port_ret, info)
    w = np.full(4, 0.25)
    r = np.array([0.01, -0.02, 0.0])
    total, components, state = reward(w, r, w, 0.005, {})
    assert isinstance(total, float) and np.isfinite(total)
    assert isinstance(components, dict) and "cvar" in components
    assert state is not None  # stateful (history, peak, cum)


def test_params_to_reward_threads_state_and_window() -> None:
    reward = params_to_reward([1.0, 0.0, 0.0, 0.0, 1.0, 1.0], window=5)
    w = np.full(4, 0.25)
    r = np.array([0.01, -0.02, 0.0])
    _t1, _c1, s1 = reward(w, r, w, -0.03, {})
    t2, _c2, s2 = reward(w, r, w, -0.05, {"reward_state": s1})
    assert len(s2[0]) == 2  # rolling history accumulated
    assert np.isfinite(t2)


def test_params_to_reward_rejects_wrong_length() -> None:
    with pytest.raises(ValueError):
        params_to_reward([1.0, 2.0])
