"""Parameterised reward family — the search space of the random_search and bayesopt_tpe
arms (PREREGISTRATION §4a; ADR-010; config `eureka_loop.reward_family`).

Six-term linear family over contract-context quantities:

    r_t =  w_return  · net_return
         + w_log     · log1p(net_return)
         − w_turnover· turnover
         − w_drawdown· drawdown_t                       (episode running peak)
         − w_cvar    · max(0, −CVaR̂_α(rolling window))  (Rockafellar & Uryasev 2000)
         − w_vol     · σ̂(rolling window)                (sample std of net returns)

Its vertices recover the hand-designed canon in `rewards_baselines.py`, which is what
makes H4 a like-for-like comparison of SEARCH PROCEDURES at matched budget rather than
of unrelated reward spaces. Both H4 arms draw from THIS space and only this space:
`sample_params` (random arm, seeded) and `params_to_reward` (shared constructor; the
BayesOpt-TPE arm optimises over the same dict — dependency added later via ADR, R8).

Trust posture: family rewards are repository code, NOT LLM-generated text — they do not
pass through the sandbox (R6 governs untrusted generated code only). They satisfy the
same reward contract and probe battery as every other reward.

Leakage posture: pure function of ctx plus own past-episode state; uses only
information ≤ t (R3).
"""
from __future__ import annotations

import hashlib
import json

import numpy as np

from .config import get
from .reward_contract import RewardContext, RewardOutput

WEIGHT_KEYS = ("w_return", "w_log", "w_turnover", "w_drawdown", "w_cvar", "w_vol")


def family_space() -> dict:
    """The frozen search space from config (ranges + discrete choices)."""
    return get("eureka_loop.reward_family")


def sample_params(rng: np.random.Generator) -> dict:
    """Draw one parameter point: weights ~ U[low, high]; α and window uniform over
    their discrete choice sets. Deterministic given the generator state."""
    space = family_space()
    params: dict = {}
    for key in WEIGHT_KEYS:
        bounds = space["weights"][key]
        params[key] = float(rng.uniform(bounds["low"], bounds["high"]))
    params["cvar_alpha"] = float(rng.choice(space["cvar_alpha_choices"]))
    params["window"] = int(rng.choice(space["window_choices"]))
    return params


def params_id(params: dict) -> str:
    """Stable candidate id for the TrialLedger / archive: sha256 of the sorted params."""
    blob = json.dumps({k: params[k] for k in sorted(params)}, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


class FamilyReward:
    """Contract-conforming stateful reward for one parameter point of the family."""

    def __init__(self, params: dict) -> None:
        missing = [k for k in (*WEIGHT_KEYS, "cvar_alpha", "window") if k not in params]
        if missing:
            raise ValueError(f"family params missing keys: {missing}")
        self.p = {k: float(params[k]) for k in WEIGHT_KEYS}
        self.alpha = float(params["cvar_alpha"])
        self.window = int(params["window"])
        if not 0.0 < self.alpha <= 1.0 or self.window < 2:
            raise ValueError("invalid cvar_alpha/window")
        self.reset()

    def reset(self) -> None:
        self._buf: list[float] = []
        self._peak = 0.0

    def __call__(self, ctx: RewardContext) -> RewardOutput:
        r = ctx.net_return
        self._buf.append(r)
        if len(self._buf) > self.window:
            self._buf.pop(0)
        self._peak = max(self._peak, ctx.wealth)
        dd = 0.0 if self._peak <= 0 else max(0.0, 1.0 - ctx.wealth / self._peak)

        cvar_shortfall = 0.0
        vol = 0.0
        if len(self._buf) >= self.window:
            arr = np.sort(np.asarray(self._buf))
            k = max(1, int(np.ceil(self.alpha * len(arr))))
            cvar_shortfall = max(0.0, -float(arr[:k].mean()))
            vol = float(np.std(arr, ddof=1))

        comps = {
            "return_term": self.p["w_return"] * r,
            "log_term": self.p["w_log"] * float(np.log1p(max(r, -0.999999))),
            "turnover_term": -self.p["w_turnover"] * ctx.turnover,
            "drawdown_term": -self.p["w_drawdown"] * dd,
            "cvar_term": -self.p["w_cvar"] * cvar_shortfall,
            "vol_term": -self.p["w_vol"] * vol,
        }
        reward = float(np.clip(sum(comps.values()), -1e5, 1e5))
        return reward, {k: float(v) for k, v in comps.items()}


def params_to_reward(params: dict) -> FamilyReward:
    """Shared constructor for BOTH H4 arms — random sampling and BayesOpt must search
    the identical family for the comparison to be like-for-like."""
    return FamilyReward(params)
