"""SAC trainer — builds the FIXED headline agent and trains it on a reward-bound env.

``make_agent_trainer(cfg, seed) -> (train_env -> policy)`` is the ``agent_trainer`` the
discovery loop (``src/llm/loop.py``) injects, and ``train_agent`` is the standalone
trainer the search-arm evaluator (``src/agents/evaluator.py``) uses. The agent is a
single SB3 SAC (Haarnoja et al. 2018; audit A-1) whose ARCHITECTURE and HYPERPARAMETERS
are held fixed across arms (see :func:`resolve_agent_kwargs`) so that performance
differences are attributable to the *reward*, not the learner. One precise caveat: with
``ent_coef="auto"`` and the PopArt scale-normalisation (fact 3 below), the *effective entropy
regularisation* can vary with the authored reward magnitude — so "fixed agent" means fixed
architecture+hyperparameters, not a fixed effective regulariser. This is made auditable by the
per-candidate ``sigma_max`` logging (``src/agents/popart.py``, amendment R48) and bounded by the
``popart=False`` ablation (``scripts/popart_ablation.py``); both the cross-arm ``sigma_max`` table
and the ablation REQUIRE the campaign run (not yet executed).

Two engineering facts, each load-bearing (MASTER_EXECUTION_PLAN §5, deep-research §2):

1. **Memory-safe replay buffer (ADR-025).** SB3's default ``buffer_size=1_000_000`` at
   the 1,893-dim observation needs ``1e6 x 1893 x 4 B x 2 ~= 15 GB`` of CPU RAM — it
   would OOM a 16 GB laptop. The buffer is sized to the (fixed, matched) per-candidate
   step budget instead (``buffer_size = train_steps``), ~0.76 GB at 50k
   (50000 x 1893 x 4 B x 2, the same obs+next_obs float32 allocation the 15 GB figure
   above assumes). We do **not** use ``optimize_memory_usage=True`` (its
   handle-timeout-termination caveat is unsafe at our split-boundary episode
   truncation — review m1).

2. **Train-only observation normalization (deep-research §2).** The 1,893-dim obs mixes
   returns (~1e-3), realized vol (~1e-2), lagged VIX (~10-80) and weights (0-1); SAC is
   sensitive to that scale spread. We wrap the *training* env in SB3 ``VecNormalize``
   (``norm_obs=True``), then **freeze** the running statistics and carry them on the
   returned :class:`NormalizedPolicy`, which re-applies the *same train-period* stats at
   evaluation time. We deliberately keep ``norm_reward=False`` — the reward is the object
   of study and must not be rescaled by the trainer (that would distort H2). Entropy
   auto-tuning (``ent_coef="auto"``) further adapts to the reward scale.

3. **PopArt-style value-target scale normalization (the engine gap; src/agents/popart.py).** An
   LLM-authored reward can emit a ``total`` of almost any scale (a Sharpe that divides a one-step
   return by a variance floored at ``1e-8`` peaks at ``|total| ~ 1e4``; verified prototype candidate
   ``scalar-g5-c3``). SAC's Bellman backup turns a target of magnitude ``R`` into a Q-target near
   ``R/(1-gamma) ~ 1e6`` (``gamma=0.99``) and the MSE critic loss explodes to ``~5e6`` at the LAST
   training step (``outputs/prototype/anomalies.jsonl``). We make the critic invariant to reward
   *scale* by dividing ONLY the learning signal by a running scale ``sqrt(EMA[r^2])`` — a positive
   affine map of the value function, so the optimal policy is unchanged (van Hasselt et al. 2016),
   while the regression target is held at unit scale. ``info["port_ret"]`` (the object of study) is
   forwarded UNCHANGED, so ``norm_reward`` stays False and every realized-return number we analyse is
   identical. Config-gated by ``popart`` (default on); applied identically across arms.

All behaviours are config-gated; ``normalize_obs`` and ``popart`` default on. ``learning_starts``
defaults to 1000 (the value the Phase-0 GATE validated; SB3's UNSET default is 100, so leaving it
unset would run a DIFFERENT warmup than the gate proved).
"""
from __future__ import annotations

from typing import Any, Callable

import numpy as np

from src.agents.factory import make_headline_agent
from src.utils.config import cfg_get

__all__ = [
    "NormalizedPolicy",
    "resolve_agent_kwargs",
    "train_agent",
    "make_agent_trainer",
]


class NormalizedPolicy:
    """A trained SAC model plus the FROZEN train-period observation statistics.

    Re-applies the exact ``VecNormalize`` transform the policy was trained under
    (``clip((obs - mean) / sqrt(var + eps), -clip, clip)``) before delegating to the
    model, so evaluation observations are normalized with *train* statistics (no
    val-set leakage; deep-research §2). Exposes ``predict`` so it is a drop-in for a
    raw SB3 model in ``src.env.runner.rollout_port_returns``.
    """

    def __init__(
        self,
        model: Any,
        mean: np.ndarray,
        var: np.ndarray,
        epsilon: float,
        clip_obs: float,
        popart_scale: dict[str, float] | None = None,
    ) -> None:
        self.model = model
        self._mean = np.asarray(mean, dtype=np.float32)
        self._std = np.sqrt(np.asarray(var, dtype=np.float32) + float(epsilon))
        self._clip = float(clip_obs)
        #: T2.4 realised PopArt scale (sigma_max/sigma_last/count, or {"popart": 0.0} when off) the critic
        #: saw during training — copied into the candidate + test record for the cross-arm sigma audit.
        self.popart_scale = popart_scale

    def _normalize(self, obs: np.ndarray) -> np.ndarray:
        norm = (np.asarray(obs, dtype=np.float32) - self._mean) / self._std
        return np.clip(norm, -self._clip, self._clip)

    def predict(self, obs: np.ndarray, deterministic: bool = True) -> tuple[Any, Any]:
        """Normalize ``obs`` with the frozen train stats, then delegate to the model."""
        return self.model.predict(self._normalize(obs), deterministic=deterministic)


def resolve_agent_kwargs(cfg: Any, seed: int) -> tuple[dict[str, Any], int]:
    """Resolve the SAC kwargs (factory-supported keys) + the training-step budget.

    The buffer is sized to ``train_steps`` (memory-safe, ADR-025). Hyperparameters are
    SB3 defaults unless overridden in ``cfg`` (kept IDENTICAL across feedback arms so
    only the reward differs — audit A-1 / the runtime equivalence test).
    """
    train_steps = int(
        cfg_get(cfg, "train_steps_per_candidate", cfg_get(cfg, "train_steps", 50000))
    )
    buffer_size = int(cfg_get(cfg, "buffer_size", train_steps))  # <= train_steps (ADR-025)
    # SB3-SAC's UNSET default is learning_starts=100, but the Phase-0 GATE (scripts/smoke_test.py)
    # validated the agent with learning_starts=1000 — so the gate proved a DIFFERENT warmup than the
    # study ran (the gate validity bug). We resolve it here (config-driven, default 1000) so EVERY
    # training path (serial / SEARCH / TEST) trains under the GATED 1000-step warmup, and floor it at
    # 1000 so a config can never silently drop below the value the gate validated. (The critic-explosion
    # CURE is the PopArt scale-normalization in train_agent below; this fix aligns the warmup with the
    # gate and gives the buffer more pre-regression transitions.)
    learning_starts = max(int(cfg_get(cfg, "learning_starts", 1000)), 1000)
    kwargs: dict[str, Any] = {
        "policy": "MlpPolicy",
        "learning_rate": float(cfg_get(cfg, "learning_rate", 3e-4)),
        "buffer_size": buffer_size,
        "batch_size": int(cfg_get(cfg, "batch_size", 256)),
        "learning_starts": learning_starts,
        "gamma": float(cfg_get(cfg, "gamma", 0.99)),
        "ent_coef": cfg_get(cfg, "ent_coef", "auto"),
        "seed": int(seed),
        "verbose": int(cfg_get(cfg, "verbose", 0)),
        "device": cfg_get(cfg, "device", "auto"),  # "cpu" | "cuda" | "auto" (heterogeneous pool)
    }
    return kwargs, train_steps


def _apply_tf32(enabled: bool) -> None:
    """Set float32 matmul precision on the (process-global) torch backends, idempotently.

    Called by :func:`train_agent` so the SAME setting applies in EVERY training path — the serial
    trainer, the SEARCH worker (``parallel.train_candidate``), and the parallel TEST worker — preventing
    a SEARCH-vs-TEST numerics asymmetry (the frozen winner must be EVALUATED under the precision it was
    SELECTED under; TF32 is active on Ampere/Ada GPUs). Torch absent / no CUDA -> a safe no-op.
    """
    try:
        import torch

        torch.backends.cuda.matmul.allow_tf32 = enabled
        torch.backends.cudnn.allow_tf32 = enabled
        torch.set_float32_matmul_precision("high" if enabled else "highest")
    except Exception:  # noqa: BLE001
        pass


def train_agent(env: Any, cfg: Any, seed: int, callback: Any = None) -> Any:
    """Build the fixed SAC agent and train it on ``env`` for the fixed step budget.

    Parameters
    ----------
    env : Any
        A reward-bound ``PortfolioEnv`` (the TRAIN-window env from ``EnvBundle``).
    cfg : Any
        Agent/training config (``train_steps_per_candidate``, ``buffer_size``,
        ``normalize_obs``, SB3 hyperparameters, ...).
    seed : int
        The run seed (determinism; ``src/utils/seeding.py`` seeds the wider stack).
    callback : Any, optional
        An SB3 ``BaseCallback`` (e.g. from ``src.utils.monitoring.make_training_callback``) streaming
        per-step training metrics to the live monitor. ``None`` (default) trains with no callback.

    Returns
    -------
    Any
        A :class:`NormalizedPolicy` when ``normalize_obs`` is on (default), else the raw
        SB3 model. Both expose ``predict(obs, deterministic=True)``.
    """
    kwargs, train_steps = resolve_agent_kwargs(cfg, seed)
    # Float32 matmul precision is set HERE (not as a per-scheduler side effect) so EVERY training path —
    # the serial trainer, the SEARCH worker, and the parallel TEST worker — selects AND evaluates the
    # fixed agent under IDENTICAL numerics (config key ``tf32``, default on for Ampere/Ada speed).
    _apply_tf32(bool(cfg_get(cfg, "tf32", True)))
    normalize_obs = bool(cfg_get(cfg, "normalize_obs", True))

    # PopArt-style value-target SCALE normalization (src/agents/popart.py): make the SAC critic
    # invariant to the reward's SCALE so a large-magnitude LLM reward (a variance-floored Sharpe can emit
    # |reward| ~ 1e4) cannot drive the Q-target to ~1e4/(1-gamma) ~ 1e6 and explode the critic loss. This
    # divides ONLY the learning signal by a running scale; info["port_ret"] (the object of study) is
    # forwarded unchanged, so norm_reward stays False and every realized-return number we analyse is
    # identical. The wrapper sits INSIDE VecNormalize (it wraps the PortfolioEnv; VecNormalize then
    # normalizes observations on top), and is applied identically across arms (not an H2 confound).
    from src.agents.popart import realized_scale_stats, wrap_popart

    if not normalize_obs:
        popart_env = wrap_popart(env, cfg)
        model = make_headline_agent(popart_env, kwargs)
        model.learn(total_timesteps=train_steps, callback=callback)
        # T2.4: surface the realised PopArt scale (sigma_max/last) the critic actually used so the
        # cross-arm sigma distribution is auditable. Attached to the returned policy; the loop / TEST
        # worker copy it into the candidate + test record. No effect on training or on info["port_ret"].
        model.popart_scale = realized_scale_stats(popart_env)  # type: ignore[attr-defined]
        return model

    # Train-only observation normalization (deep-research §2). norm_reward=False: the
    # reward is the object of study and must not be rescaled by the trainer.
    from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

    clip_obs = float(cfg_get(cfg, "clip_obs", 10.0))
    wrapped = wrap_popart(env, cfg)
    venv = VecNormalize(
        DummyVecEnv([lambda: wrapped]),
        norm_obs=True,
        norm_reward=False,
        clip_obs=clip_obs,
        training=True,
    )
    model = make_headline_agent(venv, kwargs)
    model.learn(total_timesteps=train_steps, callback=callback)

    rms: Any = venv.obs_rms  # frozen train-period running mean/var (single-obs RunningMeanStd at runtime)
    return NormalizedPolicy(
        model=model,
        mean=rms.mean,
        var=rms.var,
        epsilon=float(venv.epsilon),
        clip_obs=clip_obs,
        # T2.4: ``wrapped`` is the PopArt scaler (or the bare env when popart is off); read the realised
        # scale it logged during training so the candidate/test record can carry the cross-arm sigma audit.
        popart_scale=realized_scale_stats(wrapped),
    )


def make_agent_trainer(cfg: Any, seed: int, monitor: Any = None) -> Callable[[Any], Any]:
    """Return the ``agent_trainer(train_env) -> policy`` closure the loop injects.

    Binds ``cfg`` + ``seed`` so the discovery loop only has to pass the train env. When ``monitor`` is
    given, a FRESH SB3 monitoring callback (per-step metrics + anomaly detection) is built for EACH
    candidate's training and streamed to the live :class:`src.utils.monitoring.RunMonitor`.
    """

    def _trainer(train_env: Any) -> Any:
        callback = None
        if monitor is not None:
            from src.utils.monitoring import make_training_callback

            callback = make_training_callback(monitor)
        return train_agent(train_env, cfg, seed, callback=callback)

    return _trainer
