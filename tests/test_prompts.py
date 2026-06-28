"""Tests for src/llm/prompts.py + the C3 loop wiring (P4).

Verifies the env-interface rendering (anonymised shapes + the exact reward contract), that
build_prompt_set fills {ENV_INTERFACE}, and that run_loop actually SENDS the injected prompts
(the C3 fix — previously loop.py used hardcoded contentless prompts and ignored prompts/).
"""
from __future__ import annotations

import numpy as np

from src.llm.prompts import build_prompt_set, render_env_interface
from src.utils.config import load_config


def test_render_env_interface_has_contract_and_shapes() -> None:
    cfg = load_config("environment")
    s = render_env_interface(cfg, n_assets=30)
    assert "def reward(weights, returns, prev_weights, port_ret, info)" in s
    assert "softmax" in s
    assert "numpy" in s.lower()
    assert "(31,)" in s  # n_act = 30 + 1 (weights/prev_weights shape)
    assert "(30,)" in s  # per-asset returns shape
    # Anonymised by construction (rendered from shapes/config, never from data): it
    # instructs the designer to use "no dates" and contains only numbers/shapes — there is
    # no asset identifier or calendar value to leak (N3).
    assert "ANONYMISED" in s


def test_build_prompt_set_fills_env_interface() -> None:
    cfg = load_config("environment")
    ps = build_prompt_set(cfg, n_assets=30)
    assert "{ENV_INTERFACE}" not in ps.initial  # placeholder filled
    assert "reward(weights, returns, prev_weights, port_ret, info)" in ps.initial
    assert "reward" in ps.system.lower()


def test_loop_sends_injected_prompts(tmp_path) -> None:
    """run_loop sends the injected env-interface-rich system/initial prompts (C3)."""
    from src.feedback.measurement import ReturnDistribution
    from src.llm import loop
    from src.selection.fitness import held_out_fitness

    class _RecLLM:
        def __init__(self) -> None:
            self.prompts: list[tuple[str, str]] = []
            self.cfg = {"model": "x"}

        def complete(self, system: str, user: str) -> str:
            self.prompts.append((system, user))
            return (
                "def reward(weights, returns, prev_weights, port_ret, info):\n"
                "    return float(port_ret), {'r': float(port_ret)}, None\n"
            )

    class _FakeEnv:
        def __init__(self, reward_fn) -> None:
            self.reward_fn = reward_fn

        def train_env(self):
            return self

        def train_returns(self, _policy):
            return -0.001 + 0.01 * np.random.default_rng(1).standard_t(5, size=256)

        def val_returns(self, _policy):
            return 0.01 * np.random.default_rng(2).standard_normal(256)

    env_cfg = load_config("environment")
    ps = build_prompt_set(env_cfg, n_assets=8)
    rec = _RecLLM()
    loop_cfg = {
        "generations": 1,
        "candidates_per_gen": 1,
        "budget": 1,
        "n_trials": 2,
        "prompts": {"system": ps.system, "initial": ps.initial},
    }
    loop.run_loop(
        "scalar",
        _FakeEnv,
        rec,
        lambda _env: object(),  # fake policy (FakeEnv ignores it)
        ReturnDistribution,
        held_out_fitness,
        loop_cfg,
        tmp_path,
    )
    system_sent, initial_sent = rec.prompts[0]
    assert system_sent == ps.system
    assert "reward(weights, returns, prev_weights, port_ret, info)" in initial_sent
