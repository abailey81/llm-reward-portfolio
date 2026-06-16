"""Tests for the infrastructure utilities (config, provenance, logging) and the reward
contract's signature validator — locking behaviour the agent-written suite did not cover."""

from __future__ import annotations

import logging

import pytest

from src.reward.contract import ALLOWED_IMPORTS, SAFE_DEFAULT, validate_signature
from src.utils import provenance as pv
from src.utils.config import DotDict, load_all, load_config
from src.utils.logging import configure_logging, get_logger


# --- reward contract -------------------------------------------------------------------
def test_validate_signature_accepts_exact_contract() -> None:
    def reward(weights, returns, prev_weights, port_ret, info):  # noqa: ANN001
        return 0.0, {}, None

    assert validate_signature(reward) is True


def test_validate_signature_rejects_wrong_arity_and_varargs() -> None:
    def bad_arity(a, b):  # noqa: ANN001
        return None

    def varargs(*a):  # noqa: ANN002
        return None

    assert validate_signature(bad_arity) is False
    assert validate_signature(varargs) is False


def test_contract_constants() -> None:
    assert ALLOWED_IMPORTS == {"numpy", "np"}
    assert SAFE_DEFAULT == 0.0


# --- provenance ------------------------------------------------------------------------
def test_hashes_are_deterministic_and_order_independent() -> None:
    assert pv.sha256_text("abc") == pv.sha256_text("abc")
    assert pv.sha256_bytes(b"abc") == pv.sha256_text("abc")
    # sha256_obj is canonical (sorted keys) so key order does not matter.
    assert pv.sha256_obj({"a": 1, "b": 2}) == pv.sha256_obj({"b": 2, "a": 1})
    assert pv.sha256_obj({"a": 1}) != pv.sha256_obj({"a": 2})


def test_env_fingerprint_shape_and_git() -> None:
    fp = pv.env_fingerprint()
    assert {"python", "platform", "git_commit", "packages"} <= set(fp)
    assert "numpy" in fp["packages"]
    assert pv.git_commit() is None or isinstance(pv.git_commit(), str)


# --- config ----------------------------------------------------------------------------
def test_load_all_has_every_config() -> None:
    cfgs = load_all()
    assert {
        "environment",
        "algos",
        "llm",
        "data",
        "arms",
        "campaign",
        "preregistration",
        "regimes",
    } <= set(cfgs)


def test_dotdict_nested_access_and_require() -> None:
    d = DotDict({"x": {"y": 1}, "z": None})
    assert d.require("x").require("y") == 1
    with pytest.raises(KeyError):
        d.require("missing")
    with pytest.raises(ValueError, match="null"):
        d.require("z")  # present but null -> fail loud


def test_matched_budget_consistent_across_configs() -> None:
    """The matched compute budget must agree across arms/llm/campaign (no silent drift)."""
    arms = load_config("arms").require("matched_budget")
    llm = load_config("llm").require("candidate_budget_total")
    camp = load_config("campaign").require("candidates_per_arm")
    assert arms == llm == camp


# --- logging ---------------------------------------------------------------------------
def test_logging_configures_idempotently() -> None:
    configure_logging(logging.INFO)
    configure_logging(logging.DEBUG)  # second call must not duplicate handlers
    assert len(logging.getLogger().handlers) == 1
    assert isinstance(get_logger("x"), logging.Logger)
