"""PopArt-style value-target scale normalization for the fixed SB3-SAC critic (the engine gap).

Why this exists (the verified failure)
--------------------------------------
The reward is the *object of study* (H2) and is **never** rescaled in the data we analyse: every
realized-return number — selection fitness, the tail/EVT statistics, all inference — is read from
``info["port_ret"]`` (the realized portfolio return), NOT from the reward ``total`` the agent
maximizes (see ``src/env/runner.py``). But an LLM-authored reward is free to emit a ``total`` of
almost any *scale*: a Sharpe-style reward that divides a one-step return by a variance floored at
``1e-8`` produces a per-step target of order ``1e4`` (verified: prototype candidate ``scalar-g5-c3``
peaked at ``|total| = 1.146e4``). Feeding a target of magnitude ``R`` into SAC's Bellman backup
drives the Q-target toward ``R / (1 - gamma)`` — at ``gamma = 0.99`` that is ``~1e6`` — so the MSE
critic loss explodes to ``~5e6`` and the run diverges at the LAST training step
(``outputs/prototype/anomalies.jsonl``: ``critic_loss`` up to ``1.12e7``; ``critic_explosion`` logged
at step 25000). That is an *engine* pathology — a scale-sensitive learner — not a property of the
reward we want to study.

The principled fix (PopArt invariance, applied to the target only)
------------------------------------------------------------------
PopArt (van Hasselt et al., *Learning values across many orders of magnitude*, NeurIPS 2016) makes a
value learner invariant to the **scale** of its returns by learning in a *normalized* target space
while preserving the greedy policy. The exact, network-surgery form ("ART": adaptively rescale the
output layer so predictions are preserved when the statistics change) is fragile to bolt onto SB3's
compiled ``SAC.train`` loop. We implement the *behaviourally equivalent* invariance the cleanest way
that does not touch SB3 internals: a running **scale** ``sigma`` (EMA of the reward's root second
moment) divides the reward the **critic** regresses on. Because SAC's critic target, its current-Q
prediction, AND the actor's ``min_q`` objective all live in that single scaled space, dividing the
reward by ``sigma`` rescales *every* Q by the same ``~1 / (sigma (1 - gamma))`` factor — a positive
affine map of the value function. The argmax over actions, hence the learned **policy**, is therefore
unchanged (PopArt's invariance theorem; the entropy temperature ``ent_coef="auto"`` re-adapts to the
normalized reward scale on its own). What changes is only the *conditioning*: the regression target is
held at unit scale, so the critic loss can no longer reach ``1e6``.

Crucially this is **not** ``VecNormalize(norm_reward=True)`` and it does **not** alter the object of
study: only ``sigma`` divides the *learning* signal; ``info["port_ret"]`` (and the components dict) are
forwarded byte-for-byte, so ``EnvBundle.{val,train,test}_returns`` — every number that enters the
dissertation — are identical with or without this wrapper. We normalize **scale only** (no mean shift):
shifting the reward would change the entropy-vs-return trade-off and is unnecessary for the divergence,
which is purely a magnitude effect.

Design choices (each load-bearing)
----------------------------------
* **Scale, not standardize.** ``sigma = sqrt(EMA[r^2])`` (root second moment, not std). A floored
  variance pathology is a *magnitude* explosion; dividing by the RMS magnitude is exactly the quantity
  that tames it, and it leaves a genuinely tiny well-behaved reward (``sigma -> small``) untouched in
  *relative* terms (we clamp ``sigma`` below to avoid amplifying a near-zero reward into noise).
* **Deterministic, seed-free, replay-safe.** The statistic is a plain EMA over the rewards the agent
  actually sees, updated inside the env ``step``; it draws no RNG, so determinism/replay (CLAUDE.md §6)
  is preserved and the cross-arm architecture+hyperparameter equivalence (the arms differ only by seed
  and by the authored reward; see the T2.4 disclosure below for the effective-regularisation caveat) still
  holds — the wrapper is applied identically to every arm.
* **Bias-corrected EMA, scale from step 1 (NOT a warmup hold).** The scale must act from the FIRST
  reward: a warmup that passes early rewards through unscaled would let a ``1e4`` opening transition into
  the replay buffer, where it is resampled for the whole run and re-explodes the critic (the buffer is
  full-history, ADR-025). We instead debias the EMA Adam-style — ``sq_hat = sq_ema / (1 - (1-beta)^count)``
  — so after a single reward ``v`` the estimate is exactly ``v^2`` and the scaled output is ``v/|v| = ±1``
  (perfectly normalized), not ``v/sqrt(beta*v^2)``. ``warmup`` therefore defaults to ``0``; it is kept as
  a knob only for ablations.

Disclosure — a residual SCALE-DEPENDENCE the design carries (T2.4)
-----------------------------------------------------------------
``min_scale`` clamps ``sigma >= 1.0`` (default), so this wrapper is the EXACT IDENTITY for a unit-scale
reward but a ``>1`` divisor for a large-magnitude one. This qualifies the cross-arm "fixed agent" claim,
which must be stated PRECISELY: what is held identical across the H2 arms is the agent **ARCHITECTURE and
hyperparameters** (the SB3-SAC network, ``learning_rate``, ``gamma``, ``ent_coef="auto"``, the PopArt knobs
— everything in :func:`resolve_agent_kwargs`); the arms differ only by seed AND by the authored reward. The
*effective entropy regularisation* is NOT held identical — it can vary with the authored reward magnitude —
so "fixed agent" means fixed architecture+hyperparameters, not a fixed effective regulariser. Two
consequences are worth stating plainly:

1. **Entropy regularisation re-adapts to the NORMALISED scale.** With ``ent_coef="auto"`` SAC tunes the
   temperature against the reward the critic sees, i.e. ``raw / sigma``. Two arms that author rewards of
   different *magnitude* are therefore regularised against different *normalised* scales unless their
   ``sigma`` coincide — a LATENT, scale-driven cross-arm difference inside an agent that is fixed in
   architecture and hyperparameters but whose effective entropy regularisation is reward-magnitude
   dependent. This is not a bug (PopArt is exactly what makes the critic scale-invariant; the alternative
   — letting a 1e4 reward explode the critic — is worse), but it IS a confound that must be *visible*.

2. **It is made auditable, not assumed away.** The exposure is bounded two ways, both of which REQUIRE the
   campaign run (not yet executed): (a) every training path logs the realised per-candidate scale
   (:meth:`PopArtRewardScaler.realized_scale_stats`: ``sigma_max``/``sigma_last``/``count``, amendment R48)
   into the candidate AND test records, so the cross-arm ``sigma_max`` table can be inspected directly —
   when ``sigma_max == 1.0`` across all arms the wrapper was the identity everywhere and there is no
   scale-driven entropy-regularisation difference, while a spread in ``sigma_max`` quantifies it; (b) the
   ``popart=False`` ablation (``scripts/popart_ablation.py``) re-evaluates the FROZEN winners with PopArt
   off at one seed and confirms the H2 ordering is unchanged. Until the campaign runs, both the cross-arm
   ``sigma_max`` table and the ablation are SPECIFIED but UNEXECUTED.

This module is config-gated by ``popart`` (default on) and exercised by ``tests/test_popart.py``
(a large-magnitude reward no longer diverges the critic; ``port_ret`` is preserved exactly; the realised
``sigma_max``/``sigma_last`` are tracked and surfaced for the cross-arm audit).
"""
from __future__ import annotations

from typing import Any

import numpy as np

import gymnasium as gym

__all__ = ["PopArtRewardScaler", "wrap_popart", "realized_scale_stats"]


class PopArtRewardScaler(gym.Wrapper):  # type: ignore[misc]
    """Divide the reward the agent learns on by an adaptive running **scale** (PopArt, scale-only).

    The wrapper sits between the :class:`~src.env.portfolio_env.PortfolioEnv` and the SAC learner. On
    every ``step`` it updates ``sigma = sqrt(EMA[r^2])`` from the *raw* reward and returns ``raw / sigma``
    as the learning signal, while forwarding the original ``info`` (so ``info["port_ret"]`` — the object
    of study — is unchanged). The transform is a positive scaling of the value function, so the optimal
    policy is invariant (van Hasselt et al. 2016); only the critic's target conditioning improves.

    Parameters
    ----------
    env : gym.Env
        The reward-bound ``PortfolioEnv`` to wrap.
    beta : float, default 1e-3
        EMA decay for the second-moment estimate ``EMA[r^2]`` (smaller = longer memory). ``1e-3``
        gives an effective horizon of ~1000 steps, matching the ``learning_starts`` warmup scale.
    epsilon : float, default 1e-8
        Numerical floor inside the square root.
    min_scale : float, default 1.0
        Lower clamp on ``sigma``. Clamping at ``1.0`` makes the wrapper a pure **shrink** of large
        rewards: a well-behaved reward already near unit scale is passed through essentially unchanged
        (``sigma`` never drops below 1, so a tiny reward is never *amplified* into noise), while a
        ``1e4``-scale reward is divided down to unit scale. This one-sided design keeps the common,
        already-conditioned case a no-op and only acts on the pathological large-magnitude case.
    warmup : int, default 0
        Number of initial rewards passed through unscaled (``sigma = 1``). Defaults to ``0`` — the
        bias-corrected EMA already gives a sound scale from the FIRST reward (``v -> ±1``), and any hold
        would leak a pathological opening reward into the (full-history) replay buffer. Kept for ablations.

    Attributes
    ----------
    sq_ema : float
        The (raw, un-debiased) running second-moment accumulator.
    count : int
        Number of rewards observed (drives the bias correction and the optional warmup gate).
    sigma_max : float
        The LARGEST realised scale ``sigma`` seen over the run (0.0 before any step). With the default
        ``min_scale=1.0`` this is ``1.0`` for a unit-scale reward (the wrapper is the identity) and ``>1``
        for a large-magnitude reward — so the per-candidate ``sigma_max`` is exactly the auditable signal
        for the latent cross-arm entropy-regularisation difference (T2.4): ``ent_coef="auto"`` adapts to
        the NORMALISED scale, so two arms whose rewards differ in magnitude are regularised differently
        only insofar as their ``sigma`` differs. ``sigma_max == 1.0`` across all arms ⇒ no such confound.
    sigma_last : float
        The MOST RECENT realised scale (the scale in force at the end of training; ``0.0`` before any
        step). Together with ``sigma_max`` it bounds the per-candidate divisor the critic actually used.
    """

    def __init__(
        self,
        env: Any,
        beta: float = 1e-3,
        epsilon: float = 1e-8,
        min_scale: float = 1.0,
        warmup: int = 0,
    ) -> None:
        super().__init__(env)
        self.beta = float(beta)
        self.epsilon = float(epsilon)
        self.min_scale = float(min_scale)
        self.warmup = int(warmup)
        self.sq_ema: float = 0.0
        self.count: int = 0
        # Realised-scale audit trail (T2.4): the cross-arm distribution of these is what makes the
        # "fixed-agent" claim (fixed architecture+hyperparameters; effective entropy regularisation may
        # vary with reward magnitude) falsifiable. Updated every step from the SAME sigma the critic divides by.
        self.sigma_max: float = 0.0
        self.sigma_last: float = 0.0

    def _scale(self) -> float:
        """Current normalization scale ``sigma`` from the BIAS-CORRECTED second moment.

        ``1.0`` during the (default-empty) warmup; otherwise ``max(sqrt(sq_ema / (1-(1-beta)^count)), floor)``.
        The Adam-style debias makes the estimate exactly ``v^2`` after one reward ``v`` (so ``sigma=|v|`` and
        the scaled reward is ``±1``), removing the cold-start bias of a raw EMA.
        """
        if self.count < self.warmup or self.count == 0:
            return 1.0
        bias_correction = 1.0 - (1.0 - self.beta) ** self.count
        sq_hat = self.sq_ema / max(bias_correction, self.epsilon)
        return max(float(np.sqrt(sq_hat + self.epsilon)), self.min_scale)

    def step(self, action: Any) -> tuple[Any, float, bool, bool, dict]:
        """Step the inner env, update the running scale from the RAW reward, return ``raw / sigma``.

        ``info`` (hence ``info["port_ret"]`` and the logged components) is forwarded UNCHANGED — only
        the scalar the SAC critic regresses on is normalized.
        """
        obs, reward, terminated, truncated, info = self.env.step(action)
        raw = float(reward)
        # Update the second-moment EMA from the raw reward BEFORE scaling (so the divisor reflects the
        # magnitude the critic would otherwise have to fit). Deterministic, no RNG. The scale (computed
        # below, AFTER this update) therefore already reflects the current reward -> a 1e4 opening reward
        # is normalized to ±1 on the SAME step, never entering the buffer at raw magnitude.
        self.count += 1
        self.sq_ema = (1.0 - self.beta) * self.sq_ema + self.beta * (raw * raw)
        sigma = self._scale()
        # Record the SAME sigma the critic divides by (computed once, reused) for the cross-arm audit (T2.4).
        self.sigma_last = sigma
        if sigma > self.sigma_max:
            self.sigma_max = sigma
        scaled = raw / sigma
        return obs, float(scaled), bool(terminated), bool(truncated), info

    def realized_scale_stats(self) -> dict[str, float]:
        """The per-candidate realised-scale summary for the candidate/test record (T2.4 audit).

        Returns ``{"popart": 1.0, "sigma_max": ..., "sigma_last": ..., "count": ...}`` (JSON-friendly
        floats so it round-trips through the results-IO archive). ``sigma_max == 1.0`` (with the default
        ``min_scale=1.0``) means the wrapper was the IDENTITY for this reward — no rescaling, hence no
        latent entropy-regularisation difference vs. a unit-scale arm; ``sigma_max > 1`` quantifies the
        shrink the critic applied (and therefore the normalised scale ``ent_coef="auto"`` adapted to).
        """
        return {
            "popart": 1.0,
            "sigma_max": float(self.sigma_max),
            "sigma_last": float(self.sigma_last),
            "count": float(self.count),
        }

    def reset(self, **kwargs: Any) -> tuple[Any, dict]:
        """Reset the inner env. The running scale PERSISTS across episodes (one continuing learner)."""
        return self.env.reset(**kwargs)


def wrap_popart(env: Any, cfg: Any) -> Any:
    """Wrap ``env`` in :class:`PopArtRewardScaler` using ``cfg`` knobs (no-op if ``popart`` is off).

    Reads (all optional, with the documented defaults): ``popart`` (bool, default True),
    ``popart_beta``, ``popart_min_scale``, ``popart_warmup``. Returns the bare ``env`` when ``popart``
    is False so the behaviour is identical to the pre-fix trainer for an explicit opt-out.
    """
    from src.utils.config import cfg_get

    if not bool(cfg_get(cfg, "popart", True)):
        return env
    return PopArtRewardScaler(
        env,
        beta=float(cfg_get(cfg, "popart_beta", 1e-3)),
        min_scale=float(cfg_get(cfg, "popart_min_scale", 1.0)),
        warmup=int(cfg_get(cfg, "popart_warmup", 0)),
    )


def realized_scale_stats(env: Any) -> dict[str, float] | None:
    """Realised-scale summary for whatever :func:`wrap_popart` returned (T2.4 audit logging).

    Returns the :meth:`PopArtRewardScaler.realized_scale_stats` dict when ``env`` is a PopArt scaler,
    or ``{"popart": 0.0}`` when PopArt was OFF (``wrap_popart`` returned the bare env). Either way the
    per-candidate record can carry an explicit, JSON-friendly marker of the scale the critic saw (or of
    the explicit opt-out) — never a silent ``None`` that an analyst could misread as "PopArt unverified".
    Robust to a future wrapper layered ON TOP of the scaler: it unwraps ``.env`` up to a small depth.
    """
    node = env
    for _ in range(8):  # bounded unwrap; the scaler sits directly on PortfolioEnv today (depth 0)
        if isinstance(node, PopArtRewardScaler):
            return node.realized_scale_stats()
        node = getattr(node, "env", None)
        if node is None:
            break
    return {"popart": 0.0}
