"""Tests for the run-provenance env capture (scripts/capture_env.py).

Focus: the C1 gold-panel provenance block — every run RECORD must name EXACTLY which gold panel
(the active suffix + per-artifact manifest SHA-256s) produced it, so the headline panel's identity
is recoverable from ``env.json`` (and, via run_campaign, from ``campaign_summary.json``).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import capture_env  # noqa: E402


def test_gold_panel_provenance_records_active_suffix(monkeypatch) -> None:
    """``_gold_panel_provenance`` records the ACTIVE gold suffix (C1)."""
    from src.data import loaders

    monkeypatch.setattr(loaders, "gold_suffix", lambda: "univ7")
    gp = capture_env._gold_panel_provenance()
    assert gp["available"] is True
    assert gp["suffix"] == "univ7"
    # Every production gold artifact is keyed (value may be None if that suffix isn't manifested).
    assert set(gp["manifest_sha256"]) == {"returns_panel", "cash_features", "top30_selection", "splits"}


def test_capture_env_includes_gold_panel_block() -> None:
    """capture_env() carries the C1 gold_panel provenance + the bumped schema tag."""
    env = capture_env.capture_env(seed=0)
    assert env["schema"] == "capture_env/2"
    assert "gold_panel" in env
    assert "suffix" in env["gold_panel"]


def test_gold_panel_provenance_matches_default_suffix() -> None:
    """With no override, the recorded suffix is the config-primary default (univ5, Split C ADR-044/051)."""
    from src.data.loaders import gold_suffix

    gp = capture_env._gold_panel_provenance()
    assert gp["suffix"] == gold_suffix() == "univ5"
