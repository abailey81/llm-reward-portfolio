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
  - Transaction cost = c * turnover with half-L1-DRIFTED turnover (docs/environment_spec_v1.md):
    turnover = 0.5 * ||w - w_tilde||_1 where w_tilde = w_prev * (1+r_t) / (w_prev @ (1+r_t))
    is the previous weights DRIFTED by realized returns (cash grows at 1.0); c from the
    cost grid (headline 10 bps). info["turnover"] is emitted for logging sidecars.
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
from src.sandbox.executor import safe_call

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

    Limitations
    -----------
    The frozen ``"softmax"`` projection maps onto the OPEN interior of the simplex:
    every weight (including the cash sleeve) is strictly positive, so it can NEVER
    reach an EXACT corner — in particular it cannot output a true 100%-cash allocation
    (``w_cash == 1`` with every risky weight exactly 0). It can only approach it
    asymptotically as the cash logit dominates (bounded further by ``action.bound``,
    which caps the pre-softmax logit magnitude). This structurally DAMPS the full
    "flee to cash" response that a tail-risk-averse agent most wants in a crisis. The
    alternative ``"l1_normalize_of_clipped"`` projection (clip-at-zero then L1-normalise)
    CAN hit exact zero weights / the cash corner, but ``"softmax"`` is the FROZEN
    Phase-1 choice (audit C-8) and is NOT changed here. This is a ceiling that applies
    EQUALLY to every feedback arm (scalar and tail-fed alike), so it is a shared
    limitation of the action parameterisation, not a confound for the H2 contrast.
    Disclosed for the write-up's limitations section; behaviour is unchanged.
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
    cost_bps : float | None, default None
        Optional per-unit-turnover cost OVERRIDE in basis points (the
        ``costs.grid_bps`` cost-robustness sweep, ``config/environment.yaml``).
        When ``None`` (the default — preserving every existing caller's
        behaviour) the headline cost ``costs.headline_bps`` is used. When given,
        ``self.cost = cost_bps * 1e-4`` replaces it, so the cost-sweep harness
        (``scripts/cost_sweep.py``) can RE-PRICE a frozen policy at each grid
        level without retraining. Everything else (timing, turnover, reward) is
        identical, so a swept env differs from the headline env ONLY in ``self.cost``.
    """

    metadata: dict[str, Any] = {"render_modes": []}

    def __init__(
        self,
        panel: Panel,
        cfg: Any,
        reward_fn: RewardFn,
        start: int | None = None,
        end: int | None = None,
        cost_bps: float | None = None,
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
        # Per-session cash return (decimal). DEFAULT 0.0 preserves every existing caller/test byte-for-byte
        # and leaves cash growing at 1.0. A non-zero value lets the cash sleeve earn a money-market return
        # (R20). NB a CONSTANT is only a first-order proxy: the 3-month T-bill ranged 0–5.6%/yr over
        # 2005–2025, so a per-session DGS3MO SERIES (not a constant) is the correct refinement — a constant
        # would overpay cash in the ZIRP stress periods (2008/2020) where the tail-aware arm flees to cash.
        self.cash_daily_rate: float = float(state_cfg.get("cash_daily_rate", 0.0))

        action_cfg = cfg["action"] if "action" in cfg else cfg.action
        self.projection: str = str(action_cfg["projection"])
        # SAC/TQC require a FINITE action space (they rescale the tanh-squashed action to the bounds;
        # an infinite bound -> inf/NaN actions). The raw action is pre-softmax logits in
        # [-bound, bound]; softmax then projects to the simplex, so `bound` caps concentration
        # (bound=10 -> softmax can still reach ~full concentration). Frozen at Phase 1 (ADR-027).
        self.action_bound: float = float(action_cfg["bound"]) if "bound" in action_cfg else 10.0

        costs_cfg = cfg["costs"] if "costs" in cfg else cfg.costs
        # Per-unit-turnover cost (fraction): bps charged on the half-L1-DRIFTED turnover
        # computed in step() (docs/environment_spec_v1.md). headline 10 bps -> 1e-3.
        # The optional `cost_bps` OVERRIDE drives the costs.grid_bps robustness sweep
        # (scripts/cost_sweep.py): when None (default), fall back to the config headline,
        # so every existing caller is byte-for-byte unchanged (additive).
        if cost_bps is None:
            self.cost: float = float(costs_cfg["headline_bps"]) * 1e-4
        else:
            self.cost = float(cost_bps) * 1e-4
        self.cost_bps: float | None = None if cost_bps is None else float(cost_bps)

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
        # Every realized-vol window must fit inside the lookback so returns[t-w:t] is fully populated
        # at the first step (final-audit #28: a window > lookback silently produced a negative-index/
        # empty slice -> NaN obs + RuntimeWarning, not a raise). The pipeline enforces the same.
        if self.vol_windows and max(self.vol_windows) > self.lookback:
            raise ValueError(
                f"every realized_vol_window must be <= lookback ({self.lookback}); got {self.vol_windows}"
            )

        # --- gym spaces ---
        n_act = self.N + 1
        self.action_space = Box(
            low=-self.action_bound, high=self.action_bound, shape=(n_act,), dtype=np.float32
        )

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
        the half-L1-DRIFTED turnover cost (``0.5 * ||w - w_tilde||_1``; see the
        module docstring and ``docs/environment_spec_v1.md``), log-wealth is
        accumulated, and the injected reward is invoked with the stateful
        ``reward_state`` round-tripped through ``info`` (which also carries the
        realized ``turnover``).

        Returns
        -------
        tuple
            ``(obs, reward, terminated, truncated, info)``. The MDP has no absorbing
            terminal state — the episode ends ONLY because the fixed ``[start, end)``
            walk-forward window runs out of timesteps, which is a Gymnasium
            *truncation*, not a *termination*. So ``terminated`` is always False and
            ``truncated`` is True once ``t`` reaches ``end`` (final-audit fix: the
            boundary is a data/time limit, not an absorbing state — reporting it as
            terminated makes SB3 SAC's ``(1 - dones)`` factor zero the value bootstrap
            at every window edge, biasing the critic). ``reward`` is a Python float.
        """
        w = project_simplex(action, self.projection)
        # V15a extension (2026-07-03): freeze the projected weights. This SAME array is emitted below as
        # info["weights"], becomes `self.w_prev` at the end of this step, and is re-emitted NEXT step as
        # info["prev_weights"] — one live array aliased across the env boundary, so a trusted info
        # consumer writing in place (`info["weights"][:] = ...`) would silently corrupt the next step's
        # drift/cost arithmetic. `project_simplex` always returns a fresh env-owned array and the env
        # itself only READS it, so the zero-copy read-only flag (the V15a setflags pattern) closes the
        # write path outright — cheaper than emitting per-step copies. The UNTRUSTED reward still gets
        # its own DETACHED read-only copies (w_ro / prev_ro below), unchanged.
        w.setflags(write=False)
        # `self.panel.returns[self.t]` is a row of the SHARED, frozen gold panel; `np.asarray`
        # with a matching dtype returns a VIEW that aliases that row's memory. Take a COPY so the
        # env's own arithmetic (and, below, the untrusted reward) can never write through to the
        # panel and corrupt the data later candidates/steps replay from (determinism guarantee,
        # V15a). The copy is cheap (one (N,) row) and leaves all downstream numerics identical.
        r_t = np.array(self.panel.returns[self.t], dtype=np.float64, copy=True)

        # Half-L1-DRIFTED turnover (docs/environment_spec_v1.md "Dynamics & accounting").
        # Between the previous trade and this one the held weights DRIFT by realised
        # returns, so the agent only trades — and only pays cost on — the gap between
        # the new target w and the *drifted* prior weights w_tilde, not the raw w_prev.
        # growth[i] = 1 + r_t[i] for the N risky assets; the cash sleeve grows at 1 + cash_daily_rate
        # (default 0.0 -> grows at 1.0, the legacy behaviour; R20).
        growth = np.ones(self.N + 1, dtype=np.float64)
        growth[: self.N] = 1.0 + r_t
        growth[self.N] = 1.0 + self.cash_daily_rate
        port_growth = float(self.w_prev @ growth)
        if port_growth <= 0.0:
            raise FloatingPointError(
                f"non-positive portfolio growth {port_growth!r} at t={self.t}: drifted "
                "weights are undefined (a -100% combined move wiped the portfolio)"
            )
        w_tilde = self.w_prev * growth / port_growth
        turnover = 0.5 * float(np.abs(w - w_tilde).sum())

        # Gross = risky leg (w·r_t) + the cash sleeve's money-market return (w_cash · cash_daily_rate).
        gross = float(w[: self.N] @ r_t) + float(w[self.N]) * self.cash_daily_rate
        cost = self.cost * turnover
        port_ret = gross - cost
        # Clip port_ret > -1 before log1p, mirroring the baseline rewards (src/baselines/rewards.py:305,364):
        # a <= -100% step (>=100% combined loss after cost) gives log1p(<=-1) = -inf/NaN. This makes the
        # accumulation consistent with the port_growth <= 0.0 raise above (which already rejects a drifted
        # wipeout) and with the baselines' max(port_ret, -0.9999) floor (final-audit fix).
        self.log_wealth += float(np.log1p(max(port_ret, -0.9999)))

        info: dict[str, Any] = {
            "weights": w,
            "prev_weights": self.w_prev,
            "reward_state": self.reward_state,
        }
        # No-cross-contamination / determinism boundary (V15a): the reward is UNTRUSTED LLM code and
        # received MUTABLE references to env-owned state — `w` (which becomes next step's `self.w_prev`),
        # `self.w_prev`, the `r_t` panel data, and this very `info` dict. A reward doing an in-place write
        # (`weights[:] = ...`, `returns[:] = 0`) or injecting/clobbering an `info` key would silently
        # corrupt the env's state across steps AND across candidates, breaking the "results replay from the
        # archive" guarantee. So the reward is handed READ-ONLY COPIES and a SHALLOW-COPIED info dict:
        #   * read-only blocks every in-place ndarray write but preserves all reads / new-array ops, so a
        #     BENIGN reward sees byte-identical inputs and produces identical outputs (verified by the
        #     unchanged env/sandbox tests + the V15 regression);
        #   * the shallow info copy means the reward CANNOT add/remove/clobber keys on the env's dict, yet
        #     it still READS the same `info["reward_state"]` value, so stateful rewards round-trip exactly
        #     (the reward persists its OWN next state via the RETURNED `reward_state`, never by mutating info).
        # r_t is already a fresh copy (above); marking it read-only additionally blocks in-place writes.
        r_t.setflags(write=False)
        # Hand the reward DETACHED read-only COPIES (not views): a read-only *view* still exposes a
        # writable parent via ``.base`` (protection would then lean on the AST gate denying ``.base``);
        # a copy has ``base is None`` so the array boundary is self-sufficient (``r_t`` is already a copy).
        w_ro = np.array(w, copy=True)
        w_ro.setflags(write=False)
        prev_ro = np.array(self.w_prev, copy=True)
        prev_ro.setflags(write=False)
        reward_info: dict[str, Any] = dict(info)
        reward_info["weights"] = w_ro
        reward_info["prev_weights"] = prev_ro
        # Stage-2 sandbox (audit A-5 / P0-2): a reward that passed validate_once on the
        # tiny fixture can still raise or return non-finite on a real N-asset observation.
        # safe_call substitutes SAFE_DEFAULT and flags the candidate, so the rollout never
        # crashes mid-training (the failed candidate then simply scores poorly).
        total, components, reward_state = safe_call(
            self.reward_fn, w_ro, r_t, prev_ro, port_ret, reward_info
        )
        self.reward_state = reward_state
        info["reward_state"] = reward_state
        info["components"] = components
        info["port_ret"] = port_ret
        info["gross"] = gross
        info["cost"] = cost
        info["turnover"] = turnover
        # Emit the accumulated log-wealth as a logging sidecar (final-audit fix): it was previously
        # init/reset/accumulated but NEVER consumed (pure dead state), while the module docstring
        # advertises it as a tracked quantity. Surfacing it here makes that contract real.
        info["log_wealth"] = self.log_wealth

        self.w_prev = w
        self.t += 1
        # The window edge is data EXHAUSTION (a time limit), not an absorbing MDP state, so it is a
        # Gymnasium *truncation* (final-audit fix). Mechanism (corrected 2026-07-03, verified against the
        # installed SB3 2.8.0): DummyVecEnv itself SYNTHESIZES info['TimeLimit.truncated'] = truncated and
        # not terminated on every step (dummy_vec_env.py:66 — no TimeLimit/Monitor wrapper needed; the
        # earlier claim that the key is never set without one was wrong), and SAC's ReplayBuffer
        # (handle_timeout_termination=True, the default) stores it as `timeouts`, sampling with
        # dones * (1 - timeouts) (buffers.py:278/320-322). So reporting the edge as TRUNCATED keeps the
        # value bootstrap reward + gamma*Q(next) alive, while reporting it as `terminated` would zero it
        # (dones=1, timeouts=0) once per episode at every window edge, biasing the critic — the outcome
        # the original comment described, now with the true mechanism.
        terminated = False
        truncated = self.t >= self.end

        obs = self._obs()
        return obs, float(total), terminated, truncated, info

    # -- observation ----------------------------------------------------------
    def _obs(self) -> np.ndarray:
        """Build the observation from data knowable at decision time ``t`` (no look-ahead).

        The window uses ``returns[t-lookback : t]`` (strictly past), realized vol
        over each configured window on the same strictly-past returns, the VIX value
        knowable at ``t``, a constant cash-row marker, and the previous weights.

        The *returns* window invariant is strict: it never reads any return row with
        index ``>= t`` (``returns[t]`` is the *future* realisation consumed only in
        :meth:`step`). The VIX index is convention-dependent and is corrected here to
        match the implementation (final-audit fix to a previously false "never index
        ``>= t``" claim): on the contemporaneous (synthetic) convention the env lags to
        ``vix[t-1]``; on a prelagged gold panel (``vix_prelagged=True``) row ``t`` already
        holds the ``t-1`` close, so the env reads ``vix[t]`` (index ``== t``) — still a
        ``t-1`` close, hence no look-ahead, but it IS a panel row at index ``t``.

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
            # VIX knowable at decision time t = the t-1 close, exposed EXACTLY ONCE. A gold panel is
            # ALREADY shift(1)-lagged by the pipeline (vix_prelagged=True) -> read vix[t] directly; the
            # synthetic/contemporaneous convention -> lag here to vix[t-1] (final-audit #7: this avoids
            # double-lagging the gold panel to a t-2 close). The index is CLAMPED to the last row so the
            # (unused) terminal observation — step() advances to t==panel.T, where the prelagged read
            # vix[t] would be out of bounds — never raises (re-audit regression: would crash the gold
            # campaign's once-per-arm sealed evaluation on its final step).
            vix_idx = t if getattr(self.panel, "vix_prelagged", False) else t - 1
            vix_idx = min(vix_idx, self.panel.vix.shape[0] - 1)
            parts.append(np.asarray([self.panel.vix[vix_idx]], dtype=np.float64))

        # Constant cash-row marker (the cash asset is always available).
        parts.append(np.asarray([1.0], dtype=np.float64))

        if self.include_prev_weights:
            parts.append(np.asarray(self.w_prev, dtype=np.float64))

        obs = np.concatenate([np.asarray(p, dtype=np.float64).ravel() for p in parts])
        return obs.astype(np.float32)
