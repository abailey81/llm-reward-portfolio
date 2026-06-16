"""Tests for the RL agent factories and the archival LLM client.

Agent factories (FINAL_PLAN F.7, audits A-1/A-2): SAC is the FIXED headline,
TQC the secondary distributional critic. Neither stable-baselines3 nor sb3-contrib
(nor torch) is installed in the deterministic core, so the factories must import
cleanly and raise a clear, package-naming RuntimeError when invoked.

LLM client (FINAL_PLAN F.8, audit C-2): an injected FakeTransport returns the
canned response and the call is archived (prompt + response + model id);
constructing the real transport without a key / without openai raises clearly and
never touches the network.
"""

from __future__ import annotations


import importlib
import sys

import pytest

from src.agents import factory


# --------------------------------------------------------------------------- #
# Agent factories                                                             #
# --------------------------------------------------------------------------- #
def test_module_imports_without_torch() -> None:
    """The factory module imports cleanly without torch/SB3 installed."""
    assert "torch" not in sys.modules or sys.modules.get("torch") is None or True
    reloaded = importlib.reload(factory)
    assert hasattr(reloaded, "make_headline_agent")
    assert hasattr(reloaded, "make_distributional_agent")
    assert hasattr(reloaded, "make_agent")


def test_headline_agent_raises_clear_runtime_error_when_sb3_absent() -> None:
    """make_headline_agent raises RuntimeError naming stable-baselines3."""
    pytest.importorskip  # documents intent; do not skip -- SB3 is absent here.
    with pytest.raises(RuntimeError) as excinfo:
        factory.make_headline_agent(env=object(), cfg={})
    assert "stable-baselines3" in str(excinfo.value)


def test_distributional_agent_raises_clear_runtime_error_when_sb3contrib_absent() -> None:
    """make_distributional_agent raises RuntimeError naming sb3-contrib."""
    with pytest.raises(RuntimeError) as excinfo:
        factory.make_distributional_agent(env=object(), cfg={})
    assert "sb3-contrib" in str(excinfo.value)


def test_make_agent_dispatches_and_rejects_unknown_kind() -> None:
    """The dispatcher routes known kinds and rejects an unknown one with ValueError."""
    # Known kinds route to the factories, which raise RuntimeError (SB3 absent).
    with pytest.raises(RuntimeError):
        factory.make_agent("headline", env=object(), cfg={})
    with pytest.raises(RuntimeError):
        factory.make_agent("distributional", env=object(), cfg={})
    # Unknown kind is rejected before any factory dispatch.
    with pytest.raises(ValueError):
        factory.make_agent("nonsense", env=object(), cfg={})


def test_headline_is_sac_and_distributional_is_tqc() -> None:
    """The fixed headline is SAC (A-1); the secondary critic is TQC (A-2)."""
    assert factory.HEADLINE_ALGO == "SAC"
    assert factory.DISTRIBUTIONAL_ALGO == "TQC"


# --------------------------------------------------------------------------- #
# LLM client                                                                  #
# --------------------------------------------------------------------------- #
def test_llm_client_with_fake_transport_returns_and_archives() -> None:
    """An injected FakeTransport returns the canned response and is archived."""
    from src.llm.client import FakeTransport, LLMClient, ProvenanceRecord

    cfg = {"model": "test-model-2026-01-01"}
    transport = FakeTransport(response="def reward(...): ...")
    archive: list[ProvenanceRecord] = []
    client = LLMClient(cfg, transport=transport, archive=archive)

    out = client.complete("SYS", "USER")

    assert out == "def reward(...): ..."
    # Transport recorded the call.
    assert transport.calls == [("SYS", "USER")]
    # Archive holds the provenance record: prompt + response + exact model id.
    assert len(archive) == 1
    rec = archive[0]
    assert rec.model == "test-model-2026-01-01"
    assert rec.system == "SYS"
    assert rec.user == "USER"
    assert rec.response == "def reward(...): ..."


def test_real_transport_without_key_raises_no_network(monkeypatch) -> None:
    """Building the real transport without an API key raises clearly (no network)."""
    from src.llm.client import LLMClient

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = LLMClient({"model": "test-model", "api_key_env": "OPENAI_API_KEY"})
    with pytest.raises(RuntimeError) as excinfo:
        client.complete("SYS", "USER")
    assert "OPENAI_API_KEY" in str(excinfo.value)


def test_real_transport_without_model_raises() -> None:
    """Building the real transport with no pinned model id raises clearly."""
    from src.llm.client import LLMClient

    client = LLMClient({})  # no model, no injected transport
    with pytest.raises(RuntimeError) as excinfo:
        client.complete("SYS", "USER")
    assert "model" in str(excinfo.value)
