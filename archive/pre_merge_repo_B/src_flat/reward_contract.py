"""The reward contract every candidate (LLM-generated or hand-designed) must satisfy:

    fn(ctx: RewardContext) -> tuple[float, dict[str, float]]

The component dict is what makes Eureka-style reflection and the forensics chapter
possible (CLAUDE.md conventions). `validate_reward_callable` is the gate the sandbox
applies before any candidate reaches training.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Tuple

import numpy as np

from .config import get

RewardOutput = Tuple[float, Mapping[str, float]]
RewardFn = Callable[["RewardContext"], RewardOutput]


@dataclass(frozen=True)
class RewardContext:
    """Exactly the fields promised to the LLM in prompts/portfolio_system_prompt_v0.md.
    Everything here is lag-safe by construction (leakage law R3); candidates may not
    access anything else."""

    net_return: float
    gross_return: float
    turnover: float
    cost: float
    weights: np.ndarray          # current target weights, cash last, sums to 1
    prev_weights: np.ndarray     # drifted previous weights
    wealth: float
    step: int
    lookback_returns: np.ndarray  # (n_assets, T_lookback) strictly-past log returns
    regime_probs: np.ndarray      # filtered, shift(1) HMM probabilities (k_states,)


def validate_reward_output(out: object, max_abs: float | None = None) -> RewardOutput:
    """Raise ValueError unless `out` is a contract-conforming (float, components) pair."""
    max_abs = max_abs or float(get("eureka_loop.contract.max_abs_reward"))
    if not (isinstance(out, tuple) and len(out) == 2):
        raise ValueError("reward must return a 2-tuple (reward, components)")
    reward, components = out
    reward = float(reward)
    if not np.isfinite(reward) or abs(reward) >= max_abs:
        raise ValueError(f"reward not finite/bounded: {reward}")
    if not isinstance(components, Mapping) or len(components) == 0:
        raise ValueError("components must be a non-empty mapping (R: component dict required)")
    for k, v in components.items():
        if not isinstance(k, str):
            raise ValueError("component keys must be strings")
        v = float(v)
        if not np.isfinite(v) or abs(v) >= max_abs:
            raise ValueError(f"component '{k}' not finite/bounded: {v}")
    return reward, {k: float(v) for k, v in components.items()}


def probe_contexts(n_assets: int = 5, t_lookback: int = 60,
                   n_probe: int = 32, seed: int = 0) -> list["RewardContext"]:
    """The synthetic probe battery (incl. zero-variance and crash days). Single source
    of truth for both in-process validation (below) and the sandbox's serialized
    battery (`sandbox.probe_payloads`) — the two must never drift apart."""
    rng = np.random.default_rng(seed)
    contexts = []
    for i in range(n_probe):
        lb = rng.normal(0, 0.01, size=(n_assets, t_lookback))
        if i == 0:
            lb[:] = 0.0                                   # zero-variance guard probe
        if i == 1:
            lb[:, -1] = -0.20                             # crash-day probe
        w = rng.dirichlet(np.ones(n_assets + 1))
        contexts.append(RewardContext(
            net_return=float(rng.normal(0, 0.01)),
            gross_return=float(rng.normal(0, 0.01)),
            turnover=float(rng.uniform(0, 1)),
            cost=float(rng.uniform(0, 0.001)),
            weights=w,
            prev_weights=w,
            wealth=float(np.exp(rng.normal(0, 0.1))),
            step=i,
            lookback_returns=lb,
            regime_probs=rng.dirichlet(np.ones(3)),
        ))
    return contexts


def validate_reward_callable(fn: RewardFn, n_assets: int = 5, t_lookback: int = 60,
                             n_probe: int = 32, seed: int = 0) -> None:
    """Probe `fn` on the synthetic ctx battery (incl. zero-variance and crash days).
    Raises on the first violation; passing here is necessary, not sufficient."""
    for ctx in probe_contexts(n_assets, t_lookback, n_probe, seed):
        validate_reward_output(fn(ctx))
