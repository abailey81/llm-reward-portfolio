"""Portfolio Gymnasium environment — spec: docs/environment_spec_v1.md (Pillar IV).

Precedents: Sood et al. 2023 (state/softmax/reward template), Jiang et al. 2017
(prev-weight injection). Core accounting (drift, turnover, costs, wealth) is implemented
and unit-tested to 1e-10 (tests/test_portfolio_env.py). The Sood cash-row features
(vol20, vol20/vol60, VIX) are built by `src/features.py` (shift(1), leakage-tested —
ADR-007) and passed in via `cash_features`; observations append the current row.

Leakage posture: observations expose only strictly-past returns, current weights, and
(if supplied) cash-row features that are shift(1)-lagged by construction. The env
verifies feature finiteness on every decision row and fails loudly otherwise.
Fitness is never computed here (CLAUDE.md R3).
"""
from __future__ import annotations

from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .config import get
from .reward_contract import RewardContext, RewardFn, validate_reward_output


def softmax(logits: np.ndarray, clip: float) -> np.ndarray:
    z = np.clip(np.asarray(logits, dtype=float), -clip, clip)
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()


def drift_weights(prev_w: np.ndarray, asset_returns_with_cash: np.ndarray) -> np.ndarray:
    """Weights drift between rebalances: w~_i = w_i (1+r_i) / (1 + w·r)."""
    growth = 1.0 + asset_returns_with_cash
    port_growth = float(np.dot(prev_w, growth))
    if port_growth <= 0:
        raise FloatingPointError("portfolio wiped out — check data/returns scaling")
    return prev_w * growth / port_growth


class PortfolioEnv(gym.Env):
    """Daily-rebalanced long-only portfolio with a cash asset (cash LAST index).

    Args:
        returns: (T, n_assets) array of SIMPLE daily returns (accounting convention —
            config environment.returns.convention_accounting).
        reward_fn: contract-conforming callable; stateful rewards expose .reset().
        cost_bps: proportional one-way cost; default from config.
        lookback: state lookback T (default config environment.state.lookback_T).
        cash_features: optional (T, n_feat) leakage-safe feature block from
            `features.build_cash_features` (already shift(1)-lagged); appended to the
            observation. Must be finite on every row >= lookback (fail-loud guard).
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        returns: np.ndarray,
        reward_fn: RewardFn,
        cost_bps: float | None = None,
        lookback: int | None = None,
        cash_daily_rate: float | None = None,
        regime_probs: np.ndarray | None = None,
        cash_features: np.ndarray | None = None,
    ) -> None:
        super().__init__()
        self.returns = np.asarray(returns, dtype=float)
        if self.returns.ndim != 2:
            raise ValueError("returns must be (T, n_assets)")
        self.T, self.n_assets = self.returns.shape
        self.reward_fn = reward_fn
        self.cost_rate = float(cost_bps if cost_bps is not None else get("environment.costs.default_bps")) / 1e4
        self.lookback = int(lookback if lookback is not None else get("environment.state.lookback_T"))
        self.cash_rate = float(
            cash_daily_rate if cash_daily_rate is not None else get("environment.returns.cash_daily_rate")
        )
        self.logit_clip = float(get("environment.action.logit_clip"))
        if self.T <= self.lookback + 1:
            raise ValueError("not enough rows for the configured lookback")
        # filtered+shifted regime probabilities, (T, k) — zeros placeholder until wired
        self.regime_probs = (
            np.asarray(regime_probs, dtype=float)
            if regime_probs is not None
            else np.zeros((self.T, 3))
        )

        if cash_features is not None:
            cf = np.asarray(cash_features, dtype=float)
            if cf.ndim != 2 or cf.shape[0] != self.T:
                raise ValueError("cash_features must be (T, n_feat) aligned with returns")
            if not np.all(np.isfinite(cf[self.lookback:])):
                raise ValueError(
                    "cash_features contain non-finite values on decision rows — "
                    "warm-up must end before `lookback` (check feature windows; ADR-007)"
                )
            self.cash_features: np.ndarray | None = cf
            self.n_cash_features = cf.shape[1]
        else:
            self.cash_features = None
            self.n_cash_features = 0

        n_w = self.n_assets + 1  # + cash
        obs_dim = n_w + self.n_assets * self.lookback + self.n_cash_features
        self.observation_space = spaces.Box(-np.inf, np.inf, shape=(obs_dim,), dtype=np.float32)
        self.action_space = spaces.Box(-self.logit_clip, self.logit_clip, shape=(n_w,), dtype=np.float32)
        self._rng = np.random.default_rng()

    # ----------------------------------------------------------------- helpers
    def _obs(self) -> np.ndarray:
        lb = self.returns[self.t - self.lookback : self.t]            # strictly past
        log_lb = np.log1p(np.clip(lb, -0.999999, None)).T             # (n_assets, L)
        parts = [self.w, log_lb.ravel()]
        if self.cash_features is not None:
            parts.append(self.cash_features[self.t])                  # shift(1)-lagged row
        return np.concatenate(parts).astype(np.float32)

    # ------------------------------------------------------------------- API
    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        if hasattr(self.reward_fn, "reset"):
            self.reward_fn.reset()
        self.t = self.lookback
        n_w = self.n_assets + 1
        self.w = np.zeros(n_w)
        self.w[-1] = 1.0  # start fully in cash
        self.wealth = 1.0
        return self._obs(), {}

    def step(self, action: np.ndarray):
        target_w = softmax(action, self.logit_clip)

        # 1. drift yesterday's weights by today's realised returns? No — convention:
        #    weights set at t earn returns of day t; drift uses day t's returns to form
        #    tomorrow's pre-rebalance weights. Turnover compares today's target with the
        #    weights drifted from the PREVIOUS day (held in self.w post-drift).
        turnover = 0.5 * float(np.abs(target_w - self.w).sum())
        cost = turnover * self.cost_rate

        r_assets = self.returns[self.t]                                # day t simple returns
        r_with_cash = np.concatenate([r_assets, [self.cash_rate]])
        gross = float(np.dot(target_w, r_with_cash))
        net = gross - cost
        self.wealth *= 1.0 + net

        ctx = RewardContext(
            net_return=net,
            gross_return=gross,
            turnover=turnover,
            cost=cost,
            weights=target_w.copy(),
            prev_weights=self.w.copy(),
            wealth=self.wealth,
            step=self.t,
            lookback_returns=np.log1p(
                np.clip(self.returns[self.t - self.lookback : self.t], -0.999999, None)
            ).T,
            regime_probs=self.regime_probs[self.t],
        )
        reward, components = validate_reward_output(self.reward_fn(ctx))

        # post-trade weights drift through day t's returns -> next step's prev weights
        self.w = drift_weights(target_w, r_with_cash)
        self.t += 1
        terminated = self.t >= self.T
        info: dict[str, Any] = {
            "components": components,
            "turnover": turnover,
            "cost": cost,
            "net_return": net,
            "gross_return": gross,
            "wealth": self.wealth,
        }
        obs = self._obs() if not terminated else np.zeros(self.observation_space.shape, dtype=np.float32)
        return obs, float(reward), terminated, False, info
