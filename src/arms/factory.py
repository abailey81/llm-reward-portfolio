"""Experimental-arm factory for the reward-discovery study (FINAL_PLAN F.9).

Purpose
-------
Construct a runnable *arm* descriptor by name. The dissertation compares several
reward-discovery strategies under a single MATCHED candidate budget. To keep the
comparison fair, every arm shares the same headline agent and the same budget;
the arms differ only in *how* candidate rewards are proposed.

The six arms (config/arms.yaml; FINAL_PLAN B.5)
-----------------------------------------------
Four LLM arms — identical in every respect except the feedback block fed back to
the model (audit A-1: the feedback channel is the contribution):

    distributional : scalar + the full frozen tail-diagnostic set.
    scalar         : scalar performance number only.
    placebo        : scalar + an inert block matched in length/field-count.
    scalar_cvar5   : scalar + one downside number (CVaR 5%).

Two non-LLM search baselines:

    random_search  : H4a — samples reward CODE from the same code space the LLM
                     uses (src/search/random_search.py).
    bayes_opt      : H4b — Bayesian optimization of the coefficients of a fixed
                     parametric reward template (src/search/bayes_opt.py).

Invariant
---------
Whatever the arm, the candidate budget is identical (matched compute) and the
headline agent is the fixed SB3 SAC learner (audit A-1) — only the proposal
mechanism varies. The four LLM arms differ ONLY in ``feedback_kind`` (which maps
straight onto ``src.feedback.schema.build_block``'s ``arm`` string).

Tests (tests/test_arms.py)
--------------------------
    - all six arms build;
    - every arm shares the same candidate budget (matched compute);
    - the four LLM arms have ``is_llm=True`` and are identical except
      ``feedback_kind``;
    - random_search / bayes_opt have ``is_llm=False`` and the right
      ``search_kind``;
    - LLM ``feedback_kind`` values map to valid schema arms.
"""

from __future__ import annotations


from dataclasses import dataclass
from typing import Any, Optional

from src.feedback.schema import block_fields
from src.utils.config import DotDict, load_config

__all__ = ["Arm", "build_arm", "all_arms"]


@dataclass(frozen=True)
class Arm:
    """Immutable descriptor of one experimental arm.

    Attributes
    ----------
    name : str
        Arm identifier, matching a key under ``arms:`` in config/arms.yaml.
    feedback_kind : str or None
        For LLM arms, the feedback-block kind — one of ``"full_tail_set"``,
        ``"scalar_only"``, ``"scalar_plus_inert_block"``, ``"scalar_plus_cvar5"``.
        ``None`` for the non-LLM search arms.
    is_llm : bool
        ``True`` for the four feedback arms (which use the LLM reward designer),
        ``False`` for ``random_search`` and ``bayes_opt``.
    search_kind : str or None
        For non-LLM arms, ``"code"`` (random search over reward code) or
        ``"template"`` (Bayesian optimization over template coefficients).
        ``None`` for LLM arms.
    candidate_budget : int
        Total reward candidates evaluated by the arm. Identical across all arms
        (matched compute, the property that licenses the comparative claim).
    """

    name: str
    feedback_kind: Optional[str]
    is_llm: bool
    search_kind: Optional[str]
    candidate_budget: int


#: Maps the ``feedback`` value stored in config/arms.yaml onto this module's
#: ``feedback_kind`` vocabulary AND onto the ``arm`` string consumed by
#: ``src.feedback.schema.build_block`` / ``block_fields``. The dictionary is the
#: single source of truth tying the two vocabularies together.
_FEEDBACK_TO_KIND: dict[str, str] = {
    "full_tail_set": "full_tail_set",
    "scalar_only": "scalar_only",
    "scalar_plus_inert_block": "scalar_plus_inert_block",
    "scalar_plus_cvar5": "scalar_plus_cvar5",
}

#: Maps a ``feedback_kind`` onto the corresponding ``src.feedback.schema`` arm
#: string. Used to render the feedback block and cross-checked by the tests.
FEEDBACK_KIND_TO_SCHEMA_ARM: dict[str, str] = {
    "full_tail_set": "distributional",
    "scalar_only": "scalar",
    "scalar_plus_inert_block": "placebo",
    "scalar_plus_cvar5": "scalar_cvar5",
}


def _resolve_cfg(cfg: Any) -> DotDict:
    """Return the arms config, loading config/arms.yaml when ``cfg`` is None."""
    if cfg is None:
        return load_config("arms")
    if isinstance(cfg, DotDict):
        return cfg
    return DotDict(cfg)


def _matched_budget(cfg: DotDict) -> int:
    """Read the single matched candidate budget shared by every arm."""
    return int(cfg.require("matched_budget"))


def build_arm(name: str, cfg: Any = None) -> Arm:
    """Build the experimental arm identified by ``name``.

    Parameters
    ----------
    name : str
        Arm identifier. One of the four LLM arms (``distributional``,
        ``scalar``, ``placebo``, ``scalar_cvar5``) or the two search arms
        (``random_search``, ``bayes_opt``).
    cfg : DotDict or dict or None, optional
        Arms configuration carrying ``matched_budget`` and the ``arms`` table.
        When ``None`` (default), ``config/arms.yaml`` is loaded.

    Returns
    -------
    Arm
        A frozen descriptor wired to the matched budget. LLM arms carry only a
        differing ``feedback_kind``; search arms carry only a differing
        ``search_kind``.

    Raises
    ------
    KeyError
        If ``name`` is not present in the ``arms`` table.
    ValueError
        If an arm entry is malformed (e.g. an LLM arm with an unknown feedback
        kind, or an arm declaring neither feedback nor search).
    """
    config = _resolve_cfg(cfg)
    budget = _matched_budget(config)

    arms_table = config.require("arms")
    if name not in arms_table:
        raise KeyError(
            f"unknown arm {name!r}; available: {sorted(arms_table)}"
        )
    spec = dict(arms_table[name])

    # The four LLM (feedback) arms.
    if "feedback" in spec:
        feedback_raw = str(spec["feedback"])
        if feedback_raw not in _FEEDBACK_TO_KIND:
            raise ValueError(
                f"arm {name!r} has unknown feedback {feedback_raw!r}; "
                f"expected one of {sorted(_FEEDBACK_TO_KIND)}"
            )
        feedback_kind = _FEEDBACK_TO_KIND[feedback_raw]
        return Arm(
            name=name,
            feedback_kind=feedback_kind,
            is_llm=True,
            search_kind=None,
            candidate_budget=budget,
        )

    # The two non-LLM search baselines.
    if "search" in spec:
        search_kind = str(spec["search"])
        if search_kind not in ("code", "template"):
            raise ValueError(
                f"arm {name!r} has unknown search kind {search_kind!r}; "
                f"expected 'code' or 'template'"
            )
        is_llm = bool(spec.get("llm", False))
        return Arm(
            name=name,
            feedback_kind=None,
            is_llm=is_llm,
            search_kind=search_kind,
            candidate_budget=budget,
        )

    raise ValueError(
        f"arm {name!r} declares neither 'feedback' nor 'search' in config"
    )


def all_arms(cfg: Any = None) -> list[Arm]:
    """Build every arm declared in the config, in declaration order.

    Parameters
    ----------
    cfg : DotDict or dict or None, optional
        Arms configuration; loaded from ``config/arms.yaml`` when ``None``.

    Returns
    -------
    list of Arm
        One :class:`Arm` per entry under ``arms:`` in the config.
    """
    config = _resolve_cfg(cfg)
    return [build_arm(name, config) for name in config.require("arms")]


def schema_arm_for(arm: Arm) -> str:
    """Return the ``src.feedback.schema`` arm string for an LLM arm.

    Parameters
    ----------
    arm : Arm
        An LLM arm (``is_llm=True``).

    Returns
    -------
    str
        The matching ``build_block`` / ``block_fields`` arm string.

    Raises
    ------
    ValueError
        If ``arm`` is not an LLM arm or its ``feedback_kind`` is unknown.
    """
    if not arm.is_llm or arm.feedback_kind is None:
        raise ValueError(f"arm {arm.name!r} is not an LLM arm")
    schema_arm = FEEDBACK_KIND_TO_SCHEMA_ARM.get(arm.feedback_kind)
    if schema_arm is None:
        raise ValueError(f"no schema arm for feedback kind {arm.feedback_kind!r}")
    # Cross-check the schema arm is real (raises ValueError if not).
    block_fields(schema_arm)
    return schema_arm
