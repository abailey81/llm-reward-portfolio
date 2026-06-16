"""Tests for the experimental-arm factory (FINAL_PLAN F.9).

Covers: all six arms build; every arm shares the same matched candidate budget;
the four LLM arms are identical except their feedback kind; the two search arms
are non-LLM with the correct search kind; and each LLM feedback kind maps onto a
valid feedback-schema arm.
"""

from __future__ import annotations


from dataclasses import replace

import pytest

from src.arms.factory import (
    FEEDBACK_KIND_TO_SCHEMA_ARM,
    Arm,
    all_arms,
    build_arm,
    schema_arm_for,
)
from src.feedback import schema

EXPECTED_NAMES = {
    "distributional",
    "scalar",
    "placebo",
    "scalar_cvar5",
    "random_search",
    "bayes_opt",
}
LLM_NAMES = {"distributional", "scalar", "placebo", "scalar_cvar5"}


def test_all_six_arms_build() -> None:
    """Every declared arm builds into a frozen Arm with the right name set."""
    arms = all_arms()
    assert len(arms) == 6
    assert {a.name for a in arms} == EXPECTED_NAMES
    for a in arms:
        assert isinstance(a, Arm)
        # Frozen dataclass: assignment must fail.
        with pytest.raises(Exception):
            a.name = "mutated"  # type: ignore[misc]


def test_equal_budget_across_arms() -> None:
    """Every arm receives the same matched candidate budget (matched compute)."""
    arms = all_arms()
    budgets = {a.candidate_budget for a in arms}
    assert len(budgets) == 1, f"budgets differ across arms: {budgets}"
    (budget,) = budgets
    assert budget > 0


def test_llm_arms_are_llm_with_search_none() -> None:
    """The four feedback arms are LLM arms carrying no search kind."""
    for name in LLM_NAMES:
        arm = build_arm(name)
        assert arm.is_llm is True
        assert arm.search_kind is None
        assert arm.feedback_kind is not None


def test_llm_arms_identical_except_feedback_kind() -> None:
    """LLM arms differ ONLY in feedback_kind; all other fields are identical."""
    arms = [build_arm(n) for n in sorted(LLM_NAMES)]

    # All feedback kinds are distinct.
    kinds = [a.feedback_kind for a in arms]
    assert len(set(kinds)) == len(kinds)

    # Normalizing away name + feedback_kind makes every LLM arm identical.
    normalized = {
        replace(a, name="x", feedback_kind="x") for a in arms
    }
    assert len(normalized) == 1, f"LLM arms differ beyond feedback_kind: {normalized}"


def test_search_arms_are_non_llm_with_correct_kind() -> None:
    """random_search/bayes_opt are non-LLM with the right search kind."""
    rs = build_arm("random_search")
    bo = build_arm("bayes_opt")

    assert rs.is_llm is False
    assert rs.search_kind == "code"
    assert rs.feedback_kind is None

    assert bo.is_llm is False
    assert bo.search_kind == "template"
    assert bo.feedback_kind is None


def test_feedback_kinds_map_to_valid_schema_arms() -> None:
    """Each LLM feedback_kind maps onto a real feedback-schema arm.

    Cross-checked against ``src.feedback.schema.block_fields``: the mapped schema
    arm must produce a non-empty field list (i.e. it is a recognized arm).
    """
    for name in LLM_NAMES:
        arm = build_arm(name)
        schema_arm = schema_arm_for(arm)
        assert schema_arm in FEEDBACK_KIND_TO_SCHEMA_ARM.values()
        # Must be a valid arm for the schema module (raises ValueError otherwise).
        fields = schema.block_fields(schema_arm)
        assert isinstance(fields, list) and len(fields) >= 1
        # And the block renders without error.
        tail = {
            "cvar_05": -0.04,
            "cvar_10": -0.03,
            "cvar_25": -0.02,
            "cvar_01": -0.07,
            "left_tail_mass": 0.06,
            "robust_skew": -0.4,
        }
        block = schema.build_block(schema_arm, 0.83, tail)
        assert isinstance(block, str) and len(block) > 0


def test_distributional_maps_to_full_tail_set() -> None:
    """The headline contribution arm carries the full tail set."""
    arm = build_arm("distributional")
    assert arm.feedback_kind == "full_tail_set"
    assert schema_arm_for(arm) == "distributional"


def test_unknown_arm_raises() -> None:
    """Building an undeclared arm raises KeyError."""
    with pytest.raises(KeyError):
        build_arm("does_not_exist")
