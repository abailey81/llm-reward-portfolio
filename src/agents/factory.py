"""RL agent factories for the headline and distributional critics.

Purpose
-------
Construct the two reinforcement-learning agents compared in the dissertation
(FINAL_PLAN F.7). To keep the comparison fair, both factories must be invoked
with an identical environment, training budget, and seed schedule wherever the
two agents are compared head to head -- only the *algorithm/critic* differs.

Agents
------
    make_headline_agent      : Stable-Baselines3 SAC. This is the FIXED
                               headline algorithm used everywhere the reward is
                               the object of study (audit A-1) -- the reward
                               changes, the agent does not.
    make_distributional_agent: sb3_contrib TQC, the distributional/secondary
                               critic (audit A-2). TQC truncates the top
                               quantiles of its critic ensemble; the contrast
                               with SAC is therefore precisely *mean critic vs
                               truncated-quantile critic*, with library, entropy
                               coefficient, and hyperparameters held fixed.

Heavy optional dependencies
---------------------------
``stable-baselines3`` / ``sb3-contrib`` (and their ``torch`` backend) are heavy
optional dependencies. They are imported LAZILY inside each factory so this
module -- and the deterministic core that imports it -- loads cleanly without
torch installed. When a factory is actually invoked without the relevant
package present, it raises a clear :class:`RuntimeError` naming the package.

Tests (tests/test_agents.py)
----------------------------
    - make_headline_agent / make_distributional_agent raise the documented
      RuntimeError naming stable-baselines3 / sb3-contrib when those packages
      are absent.
    - the dispatcher rejects an unknown kind with ValueError.
    - the module imports cleanly without torch installed.
"""

from __future__ import annotations


from typing import Any

from src.utils.config import cfg_get

__all__ = [
    "make_headline_agent",
    "make_distributional_agent",
    "make_agent",
    "HEADLINE_ALGO",
    "DISTRIBUTIONAL_ALGO",
]

#: The fixed headline algorithm (audit A-1): Stable-Baselines3 SAC.
HEADLINE_ALGO = "SAC"

#: The secondary distributional-critic algorithm (audit A-2): sb3-contrib TQC.
DISTRIBUTIONAL_ALGO = "TQC"


def _policy_kwargs(cfg: Any) -> dict[str, Any]:
    """Resolve common policy/network/entropy/seed/budget kwargs from ``cfg``.

    Pulls the shared learner settings used by BOTH factories so that the
    SAC-vs-TQC contrast holds library, entropy coefficient, and hyperparameters
    fixed -- only the critic differs (audit A-2).

    Parameters
    ----------
    cfg : Any
        Configuration object/mapping carrying agent settings. Recognised keys
        (all optional, with sensible SB3 defaults): ``policy``, ``learning_rate``,
        ``gamma``, ``ent_coef``, ``buffer_size``, ``batch_size``, ``seed``,
        ``verbose``, ``policy_kwargs``.

    Returns
    -------
    dict
        Keyword arguments common to SAC and TQC constructors.
    """

    kwargs: dict[str, Any] = {
        "policy": cfg_get(cfg, "policy", "MlpPolicy"),
        "learning_rate": cfg_get(cfg, "learning_rate", 3e-4),
        "gamma": cfg_get(cfg, "gamma", 0.99),
        "ent_coef": cfg_get(cfg, "ent_coef", "auto"),
        # buffer_size defaults to the train-step budget (ADR-025: full-history replay, no eviction), NOT a
        # 1M literal that OOMs the 4090 AND diverges from trainer.resolve_agent_kwargs (no-hardcoding audit).
        "buffer_size": int(
            cfg_get(
                cfg,
                "buffer_size",
                cfg_get(cfg, "train_steps_per_candidate", cfg_get(cfg, "train_steps", 50000)),
            )
        ),
        "batch_size": cfg_get(cfg, "batch_size", 256),
        # learning_starts: the warm-up steps collected (random policy) before the critic starts
        # regressing. SB3's UNSET default is 100, but the Phase-0 smoke gate validated 1000, and the
        # live trainer (trainer.resolve_agent_kwargs) now resolves it explicitly — so resolve it HERE
        # too (default 1000) and the factory honours whatever the resolved kwargs carry. Only set when
        # present-or-default so the SAC/TQC contrast stays identical (both factories read this).
        "learning_starts": cfg_get(cfg, "learning_starts", 1000),
        "seed": cfg_get(cfg, "seed", None),
        "verbose": cfg_get(cfg, "verbose", 0),
        # Device is explicit so a heterogeneous GPU+CPU worker pool can place each training
        # on a chosen device ("cpu" / "cuda" / "cuda:0"); "auto" picks CUDA when available.
        "device": cfg_get(cfg, "device", "auto"),
    }
    policy_kwargs = cfg_get(cfg, "policy_kwargs", None)
    if policy_kwargs is not None:
        kwargs["policy_kwargs"] = policy_kwargs
    return kwargs


def make_headline_agent(env: Any, cfg: Any) -> Any:
    """Build the fixed headline SAC agent (audit A-1).

    Instantiates Stable-Baselines3 ``SAC`` bound to ``env``'s observation and
    action spaces with policy/network/entropy/seed/budget settings drawn from
    ``cfg``. This is the single, frozen learner used across all reward
    experiments so that performance differences are attributable to the reward,
    not the agent.

    Parameters
    ----------
    env : Any
        A Gymnasium environment (e.g. ``src.env.portfolio_env``) supplying the
        observation and action spaces the policy is bound to.
    cfg : Any
        Agent configuration; see :func:`_policy_kwargs`.

    Returns
    -------
    Any
        A constructed ``stable_baselines3.SAC`` instance.

    Raises
    ------
    RuntimeError
        If ``stable-baselines3`` (or its torch backend) is not importable.

    Notes
    -----
    FINAL_PLAN F.7 (headline agent; audit A-1 fixed headline). ``SAC`` is imported
    lazily so this module loads without torch installed.
    """
    try:
        from stable_baselines3 import SAC
    except ImportError as exc:
        raise RuntimeError(
            "stable-baselines3 is required for agent training; install the full "
            "env (see pyproject). The deterministic core does not need it."
        ) from exc

    kwargs = _policy_kwargs(cfg)
    policy = kwargs.pop("policy")
    return SAC(policy, env, **kwargs)


def make_distributional_agent(env: Any, cfg: Any) -> Any:
    """Build the distributional TQC agent (audit A-2).

    Instantiates ``sb3_contrib.TQC`` bound to the SAME ``env`` spaces, with the
    SAME library, entropy coefficient, and budget/seed schedule as
    :func:`make_headline_agent` -- the only difference is the critic. TQC
    truncates the top quantiles of its quantile-critic ensemble to curb
    overestimation, so the SAC-vs-TQC comparison isolates *mean critic vs
    truncated-quantile critic*.

    Parameters
    ----------
    env : Any
        A Gymnasium environment supplying the observation and action spaces.
    cfg : Any
        Agent configuration; see :func:`_policy_kwargs`. Held identical to the
        headline agent so only the critic differs.

    Returns
    -------
    Any
        A constructed ``sb3_contrib.TQC`` instance.

    Raises
    ------
    RuntimeError
        If ``sb3-contrib`` (or its torch backend) is not importable.

    Notes
    -----
    FINAL_PLAN F.7 (distributional agent; audit A-2 secondary critic). ``TQC`` is
    imported lazily so this module loads without torch installed.
    """
    try:
        from sb3_contrib import TQC
    except ImportError as exc:
        raise RuntimeError(
            "sb3-contrib is required for agent training; install the full env "
            "(see pyproject). The deterministic core does not need it."
        ) from exc

    kwargs = _policy_kwargs(cfg)
    # Pull the TQC-DEFINING hyperparameters through (audit fix 2026-06-20): _policy_kwargs resolves only the
    # SAC/TQC-common keys, so the TQC-specific knobs were silently dropped — config/algos.yaml advertises
    # them as configurable, so they MUST take effect when present (a missing key keeps the sb3-contrib
    # default). CRUCIALLY their homes differ: ``top_quantiles_to_drop_per_net`` (the knob that DEFINES the
    # truncated-quantile critic, audit A-2) is a TOP-LEVEL ``TQC()`` arg, while ``n_quantiles`` and
    # ``n_critics`` are ``TQCPolicy`` args — passing those two top-level raises ``TypeError`` (TQC.__init__
    # has no **kwargs), so they go via ``policy_kwargs`` (merged with any set by _policy_kwargs, not clobbered).
    tqdn = cfg_get(cfg, "top_quantiles_to_drop_per_net", None)
    if tqdn is not None:
        kwargs["top_quantiles_to_drop_per_net"] = tqdn
    policy_kwargs = dict(kwargs.get("policy_kwargs") or {})
    for key in ("n_quantiles", "n_critics"):
        value = cfg_get(cfg, key, None)
        if value is not None:
            policy_kwargs[key] = value
    if policy_kwargs:
        kwargs["policy_kwargs"] = policy_kwargs
    policy = kwargs.pop("policy")
    return TQC(policy, env, **kwargs)


def make_agent(kind: str, env: Any, cfg: Any) -> Any:
    """Dispatch to the requested agent factory.

    Parameters
    ----------
    kind : str
        ``"headline"`` (SAC, audit A-1) or ``"distributional"`` (TQC, audit A-2).
    env : Any
        The Gymnasium environment to bind the agent to.
    cfg : Any
        Agent configuration passed through to the chosen factory.

    Returns
    -------
    Any
        The constructed agent.

    Raises
    ------
    ValueError
        If ``kind`` is not one of the recognised agent kinds.
    RuntimeError
        Propagated from the chosen factory when its package is unavailable.
    """
    if kind == "headline":
        return make_headline_agent(env, cfg)
    if kind == "distributional":
        return make_distributional_agent(env, cfg)
    raise ValueError(
        f"unknown agent kind: {kind!r} (expected 'headline' or 'distributional')"
    )
