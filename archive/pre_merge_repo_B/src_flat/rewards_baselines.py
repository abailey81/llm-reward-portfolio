"""Hand-designed baseline rewards (the canon — PREREGISTRATION §4 / config eureka_loop).
Each satisfies the reward contract and carries its original citation. Stateful rewards
expose .reset() which the environment calls at episode start. Parameters live in
config `environment.reward_defaults` (ADR-009) — no magic numbers here.

The full canon (all six registered in config eureka_loop.baseline_rewards; the registry
at the bottom of this module maps names to factories):
    differential_sharpe   Moody & Saffell — primary baseline
    log_wealth            Sood 2023 / Jiang 2017 building block
    sharpe_episodic       expanding-Sharpe increment (telescopes to episode Sharpe)
    cvar_penalised_mean   mean - lambda * CVaR shortfall (Rockafellar & Uryasev 2000)
    drawdown_penalised    return - lambda * drawdown level
    turnover_penalised    return - lambda * turnover (extra shaping beyond realised cost)

Leakage posture: every baseline is a pure function of ctx (plus own past-episode state);
nothing here sees the future or the validation window (R3).
"""
from __future__ import annotations

from typing import Callable

import numpy as np

from .config import get
from .reward_contract import RewardContext, RewardFn, RewardOutput


class DifferentialSharpe:
    """Moody & Saffell (2001, IEEE TNN 12(4)); Moody, Wu, Liao & Saffell (1998).

    D_t = (B_{t-1}*dA_t - 0.5*A_{t-1}*dB_t) / (B_{t-1} - A_{t-1}^2)^{3/2}
    A_t = A_{t-1} + eta*dA_t,  B_t = B_{t-1} + eta*dB_t,
    dA_t = R_t - A_{t-1},      dB_t = R_t^2 - B_{t-1}.
    EWMA moments on timescale 1/eta; the canonical online risk-adjusted reward and the
    primary hand-designed baseline this project must beat (or rigorously fail to).
    """

    def __init__(self, eta: float | None = None, eps: float = 1e-12) -> None:
        self.eta = float(eta if eta is not None else get("environment.reward_defaults.differential_sharpe_eta"))
        self.eps = eps
        self.reset()

    def reset(self) -> None:
        self.A = 0.0
        self.B = 0.0
        self._warm = False

    def __call__(self, ctx: RewardContext) -> RewardOutput:
        r = ctx.net_return
        if not self._warm:
            # Initialise moments on the first observation; D_1 defined as 0.
            self.A, self.B, self._warm = r, r * r, True
            return 0.0, {"dsr": 0.0}
        dA = r - self.A
        dB = r * r - self.B
        denom = max(self.B - self.A * self.A, self.eps) ** 1.5
        d_t = (self.B * dA - 0.5 * self.A * dB) / denom
        self.A += self.eta * dA
        self.B += self.eta * dB
        d_t = float(np.clip(d_t, -1e5, 1e5))
        return d_t, {"dsr": d_t}


def log_wealth_reward(ctx: RewardContext) -> RewardOutput:
    """log(1 + r_net): the standard log-wealth building block (Sood 2023; Jiang 2017)."""
    r = max(ctx.net_return, -0.999999)
    val = float(np.log1p(r))
    return val, {"log_net_return": val}


class SharpeEpisodic:
    """Expanding-window Sharpe increment: reward_t = SR_t − SR_{t−1}.

    SR_t is the UNANNUALISED Sharpe (R5 convention) of all net returns observed so far
    in the episode (Welford running moments; sample std, ddof=1). The sum of rewards
    telescopes to the final expanding Sharpe, so maximising return-to-go maximises the
    episode Sharpe — the objective of Moody, Wu, Liao & Saffell (1998), of which
    differential Sharpe is the EWMA-gradient approximation. SR_t := 0 while fewer than
    2 observations or under zero variance (guarded).
    """

    def __init__(self, eps: float = 1e-12) -> None:
        self.eps = eps
        self.reset()

    def reset(self) -> None:
        self.n = 0
        self.mean = 0.0
        self.m2 = 0.0
        self._prev_sr = 0.0

    def _sr(self) -> float:
        if self.n < 2:
            return 0.0
        var = self.m2 / (self.n - 1)
        if var <= self.eps:
            return 0.0
        return self.mean / float(np.sqrt(var))

    def __call__(self, ctx: RewardContext) -> RewardOutput:
        r = ctx.net_return
        self.n += 1
        delta = r - self.mean
        self.mean += delta / self.n
        self.m2 += delta * (r - self.mean)
        sr = self._sr()
        inc = float(np.clip(sr - self._prev_sr, -1e5, 1e5))
        self._prev_sr = sr
        return inc, {"sharpe_delta": inc, "sharpe_level": float(np.clip(sr, -1e5, 1e5))}


class CVaRPenalisedMean:
    """Mean return minus CVaR shortfall: reward_t = r_t − λ·max(0, −CVaR̂_α(window)).

    CVaR̂_α = mean of the worst ⌈α·w⌉ net returns over a rolling window INCLUDING
    today's realised return (rewards may use realised outcomes at t; the leakage laws
    bind features/decisions, R3). Empirical-CVaR objective per Rockafellar & Uryasev
    (2000). The penalty is inactive until the window is full — a deterministic warm-up
    documented in config (`environment.reward_defaults.cvar_penalised_mean`).
    """

    def __init__(self, alpha: float | None = None, window: int | None = None,
                 lam: float | None = None) -> None:
        cfg = get("environment.reward_defaults.cvar_penalised_mean")
        self.alpha = float(alpha if alpha is not None else cfg["alpha"])
        self.window = int(window if window is not None else cfg["window"])
        self.lam = float(lam if lam is not None else cfg["lam"])
        self.reset()

    def reset(self) -> None:
        self._buf: list[float] = []

    def __call__(self, ctx: RewardContext) -> RewardOutput:
        r = ctx.net_return
        self._buf.append(r)
        if len(self._buf) > self.window:
            self._buf.pop(0)
        penalty = 0.0
        if len(self._buf) >= self.window:
            tail = np.sort(np.asarray(self._buf))
            k = max(1, int(np.ceil(self.alpha * len(tail))))
            cvar = float(tail[:k].mean())
            penalty = self.lam * max(0.0, -cvar)
        reward = float(r - penalty)
        return reward, {"mean_return": float(r), "cvar_penalty": float(-penalty)}


class DrawdownPenalised:
    """Return minus drawdown-level penalty: reward_t = r_t − λ·dd_t.

    dd_t = 1 − wealth_t / max_{s≤t}(wealth_s) ∈ [0, 1], from the episode's running
    wealth peak. The level form (rather than the drawdown increment) keeps pressure on
    the policy for as long as it sits below high-water mark — the standard
    drawdown-penalised shaping in trading RL.
    """

    def __init__(self, lam: float | None = None) -> None:
        self.lam = float(lam if lam is not None else get("environment.reward_defaults.drawdown_penalised.lam"))
        self.reset()

    def reset(self) -> None:
        self._peak = 0.0

    def __call__(self, ctx: RewardContext) -> RewardOutput:
        self._peak = max(self._peak, ctx.wealth)
        dd = 0.0 if self._peak <= 0 else max(0.0, 1.0 - ctx.wealth / self._peak)
        penalty = self.lam * dd
        reward = float(ctx.net_return - penalty)
        return reward, {"mean_return": float(ctx.net_return), "drawdown_penalty": float(-penalty)}


class TurnoverPenalised:
    """Return minus turnover penalty: reward_t = r_t − λ·turnover_t.

    EXTRA shaping on top of the realised proportional cost already inside net_return
    (cost convention: DeMiguel et al. 2009; one-way turnover = ½Σ|Δw|, config
    environment.costs). Discourages churn beyond what the cost model charges —
    the canonical anti-churn baseline.
    """

    def __init__(self, lam: float | None = None) -> None:
        self.lam = float(lam if lam is not None else get("environment.reward_defaults.turnover_penalised.lam"))

    def __call__(self, ctx: RewardContext) -> RewardOutput:
        penalty = self.lam * ctx.turnover
        reward = float(ctx.net_return - penalty)
        return reward, {"mean_return": float(ctx.net_return), "turnover_penalty": float(-penalty)}


# --------------------------------------------------------------------------- registry
#: name -> zero-arg factory; names are exactly config eureka_loop.baseline_rewards.
BASELINE_FACTORIES: dict[str, Callable[[], RewardFn]] = {
    "differential_sharpe": DifferentialSharpe,
    "log_wealth": lambda: log_wealth_reward,
    "sharpe_episodic": SharpeEpisodic,
    "cvar_penalised_mean": CVaRPenalisedMean,
    "drawdown_penalised": DrawdownPenalised,
    "turnover_penalised": TurnoverPenalised,
}


def make_baseline(name: str) -> RewardFn:
    """Build a fresh contract-conforming instance of a registered baseline reward."""
    if name not in BASELINE_FACTORIES:
        raise KeyError(f"unknown baseline reward '{name}' — registry: {sorted(BASELINE_FACTORIES)}")
    return BASELINE_FACTORIES[name]()
