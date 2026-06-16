"""Portfolio environment — the risk-sensitive RL MDP with an injected reward.

This module implements the trading MDP described in FINAL_PLAN Part B.2 / F.1.
The defining feature (audit A-4) is that the reward is **not** hardcoded: a
callable conforming to the reward contract (`src/reward/contract.py`) is injected
at construction and invoked every `step`. This lets the LLM-designed reward arms,
the hand-designed baseline rewards, and the search baselines all drive the *same*
fixed SB3 SAC agent through an identical environment.

Algorithm sketch (FINAL_PLAN F.1, Part B.2):
  - Action a_t is a raw vector in R^{N+1} (N risky assets + cash). It is projected
    to the long-only simplex Delta^N by a *frozen* projection chosen in Phase 1
    (softmax OR L1-normalization-of-clipped; selected via cfg, audit C-8).
  - Reward-timing (audit C-5): the asset-return vector r_t = panel.returns[t] is
    realized *after* the action is taken. gross = w[:N] @ r_t.
  - Transaction cost = c * ||w - w_prev||_1, c from the cost grid (headline 10 bps).
  - Portfolio return port_ret = gross - cost; log-wealth += log1p(port_ret).
  - reward_fn(w, r_t, w_prev, port_ret, info) -> (total, components, reward_state).
    The agent optimizes `total`; `components` are logged; `reward_state` is
    round-tripped via `info` to support stateful rewards (audit B-4).
  - Observations are built from data with index <= t only — no look-ahead. Lagged
    VIX / realized vol / lookback returns / cash row / previous weights.

Audit refs: A-4 (reward slot), B-4 (stateful reward via info), C-5 (reward timing),
C-8 (frozen simplex projection, lagged VIX in obs).
"""

from __future__ import annotations

from typing import Any

import numpy as np

import gymnasium as gym
from gymnasium.spaces import Box

from src.data.panel import Panel
from src.reward.contract import RewardFn

__all__ = ["PortfolioEnv", "project_simplex"]


def project_simplex(action: np.ndarray, kind: str = "softmax") -> np.ndarray:
    """Project a raw action vector onto the long-only simplex.

    Parameters
    ----------
    action : np.ndarray, shape (N+1,)
        Raw action over the ``N`` risky assets plus cash.
    kind : str
        Frozen projection (audit C-8). ``"softmax"`` maps any real vector to the
        interior of the simplex; ``"l1_normalize_of_clipped"`` clips at zero and
        normalises by the L1 norm (falls back to uniform when all-zero).

    Returns
    -------
    np.ndarray, shape (N+1,)
        Non-negative weights summing to 1.
    """
    a = np.asarray(action, dtype=np.float64).ravel()
    if kind == "softmax":
        z = a - np.max(a)  # numerical stability
        e = np.exp(z)
        w = e / np.sum(e)
    elif kind == "l1_normalize_of_clipped":
        clipped = np.clip(a, 0.0, None)
        s = clipped.sum()
        w = clipped / s if s > 0.0 else np.full_like(a, 1.0 / a.size)
    else:
        raise ValueError(f"unknown simplex projection {kind!r}")
    return w


class PortfolioEnv(gym.Env):  # type: ignore[misc]
    """Single-agent portfolio-allocation MDP with an injected reward callable.

    The environment is held fixed across all feedback arms; only ``reward_fn``
    varies. See module docstring and FINAL_PLAN F.1 for the full specification.

    Parameters
    ----------
    panel : Panel
        Anonymised return panel (numpy arrays only; no tickers/dates).
    cfg : Any
        Config object (``config/environment.yaml``). Provides the lookback,
        realized-vol windows, frozen ``action.projection`` and the cost.
    reward_fn : RewardFn
        A callable conforming to the reward contract, invoked once per ``step``.
    start, end : int | None
        Half-open trading window ``[start, end)`` into the panel. ``start``
        defaults to the lookback (so the observation window exists) and ``end``
        defaults to ``panel.T``.
    """

    metadata: dict[str, Any] = {"render_modes": []}

    def __init__(
        self,
        panel: Panel,
        cfg: Any,
        reward_fn: RewardFn,
        start: int | None = None,
        end: int | None = None,
    ) -> None:
        self.panel = panel
        self.cfg = cfg
        self.reward_fn = reward_fn

        # --- read frozen config (code reads config, never hardcodes) ---
        state_cfg = cfg["state"] if "state" in cfg else cfg.state
        self.lookback: int = int(state_cfg["lookback_days"])
        self.vol_windows: list[int] = [int(w) for w in state_cfg["realized_vol_windows"]]
        self.include_vix: bool = bool(state_cfg.get("include_vix", True))
        self.include_prev_weights: bool = bool(state_cfg.get("include_prev_weights", True))

        action_cfg = cfg["action"] if "action" in cfg else cfg.action
        self.projection: str = str(action_cfg["projection"])

        costs_cfg = cfg["costs"] if "costs" in cfg else cfg.costs
        self.cost: float = float(costs_cfg["headline_bps"]) * 1e-4

        self.N: int = panel.N
        self.start: int = self.lookback if start is None else int(start)
        self.end: int = panel.T if end is None else int(end)
        if self.start < self.lookback:
            raise ValueError(
                f"start ({self.start}) must be >= lookback ({self.lookback}) so the window exists"
            )
        if self.end > panel.T:
            raise ValueError(f"end ({self.end}) must be <= panel.T ({panel.T})")
        if self.start >= self.end:
            raise ValueError(f"start ({self.start}) must be < end ({self.end})")

        # --- gym spaces ---
        n_act = self.N + 1
        self.action_space = Box(low=-np.inf, high=np.inf, shape=(n_act,), dtype=np.float32)

        obs_dim = self._obs_dim()
        self.observation_space = Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32
        )

        # runtime state (set in reset)
        self.t: int = self.start
        self.w_prev: np.ndarray = np.full(n_act, 1.0 / n_act, dtype=np.float64)
        self.reward_state: object = None
        self.log_wealth: float = 0.0

    @property
    def T(self) -> int:  # noqa: N802 - conventional dimension name
        """Number of time steps in the underlying panel."""
        return self.panel.T

    # -- observation dimension -----------------------------------------------
    def _obs_dim(self) -> int:
        """Length of the flattened observation vector."""
        n_act = self.N + 1
        dim = self.lookback * self.N  # lookback returns per asset
        dim += len(self.vol_windows) * self.N  # realized vol per window per asset
        if self.include_vix:
            dim += 1  # lagged vix
        dim += 1  # cash row marker (constant 1.0)
        if self.include_prev_weights:
            dim += n_act  # previous weights (incl. cash)
        return dim

    # -- reset ----------------------------------------------------------------
    def reset(
        self, seed: int | None = None, options: dict | None = None
    ) -> tuple[np.ndarray, dict]:
        """Reset to the start index with a uniform-simplex previous weight.

        Parameters
        ----------
        seed : int | None
            Optional seed (Gymnasium convention; passed to the base RNG).
        options : dict | None
            Unused; accepted for Gymnasium API compatibility.

        Returns
        -------
        tuple
            ``(obs, info)`` with ``obs`` an ``np.ndarray`` and ``info`` a dict.
        """
        super().reset(seed=seed)
        n_act = self.N + 1
        self.t = self.start
        self.w_prev = np.full(n_act, 1.0 / n_act, dtype=np.float64)
        self.reward_state = None
        self.log_wealth = 0.0
        return self._obs(), {}

    # -- step -----------------------------------------------------------------
    def step(
        self, action: np.ndarray
    ) -> tuple[np.ndarray, float, bool, bool, dict]:
        """Advance one step: project action, realize return, cost, reward, advance.

        Implements the audit C-5 timing: the realized return ``r_t`` is read at
        the *current* index ``t`` (after the action), the portfolio return nets
        the proportional turnover cost, log-wealth is accumulated, and the
        injected reward is invoked with the stateful ``reward_state`` round-tripped
        through ``info``.

        Returns
        -------
        tuple
            ``(obs, reward, terminated, truncated, info)``. ``terminated`` is True
            once ``t`` reaches ``end``; ``truncated`` is always False; ``reward``
            is a Python float.
        """
        w = project_simplex(action, self.projection)
        r_t = np.asarray(self.panel.returns[self.t], dtype=np.float64)

        gross = float(w[: self.N] @ r_t)
        cost = self.cost * float(np.abs(w - self.w_prev).sum())
        port_ret = gross - cost
        self.log_wealth += float(np.log1p(port_ret))

        info: dict[str, Any] = {
            "weights": w,
            "prev_weights": self.w_prev,
            "reward_state": self.reward_state,
        }
        total, components, reward_state = self.reward_fn(
            w, r_t, self.w_prev, port_ret, info
        )
        self.reward_state = reward_state
        info["reward_state"] = reward_state
        info["components"] = components
        info["port_ret"] = port_ret
        info["gross"] = gross
        info["cost"] = cost

        self.w_prev = w
        self.t += 1
        terminated = self.t >= self.end
        truncated = False

        obs = self._obs()
        return obs, float(total), terminated, truncated, info

    # -- observation ----------------------------------------------------------
    def _obs(self) -> np.ndarray:
        """Build the observation from data with index <= t only (no look-ahead).

        The window uses ``returns[t-lookback : t]`` (strictly past), realized vol
        over each configured window on the same strictly-past returns, the LAGGED
        VIX ``vix[t-1]``, a constant cash-row marker, and the previous weights.
        It never reads any panel row with index ``>= t`` (note ``returns[t]`` is
        the *future* realisation consumed only in :meth:`step`).

        Returns
        -------
        np.ndarray
            The flattened ``float32`` observation vector.
        """
        t = self.t
        # Strictly-past returns window: rows [t-lookback, t).
        lb = self.lookback
        ret_win = self.panel.returns[t - lb : t]  # (lookback, N)

        parts: list[np.ndarray] = [ret_win.ravel()]

        for w in self.vol_windows:
            win = self.panel.returns[t - w : t]  # (<=w, N)
            vol = win.std(axis=0)  # (N,)
            parts.append(vol)

        if self.include_vix:
            # Lagged VIX: value at t-1 is knowable at decision time t.
            parts.append(np.asarray([self.panel.vix[t - 1]], dtype=np.float64))

        # Constant cash-row marker (the cash asset is always available).
        parts.append(np.asarray([1.0], dtype=np.float64))

        if self.include_prev_weights:
            parts.append(np.asarray(self.w_prev, dtype=np.float64))

        obs = np.concatenate([np.asarray(p, dtype=np.float64).ravel() for p in parts])
        return obs.astype(np.float32)
