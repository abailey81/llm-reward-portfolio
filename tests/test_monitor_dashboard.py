"""Behaviour tests for the read-only watcher helpers in ``scripts/monitor.py`` (silent-hang detection,
the anomaly error-tracker, LLM token/cost accounting, and the alert payload).

The dashboard is strictly READ-ONLY over on-disk run artefacts, so these tests synthesise a tiny
``progress.json`` / ``events.jsonl`` / ``anomalies.jsonl`` and assert the pure logic — no rich, no torch,
no network (``post_alert`` is never called against a real URL).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import monitor  # noqa: E402


def _write(run_dir: Path, name: str, rows: list[dict]) -> None:
    (run_dir / name).write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def _state(phase: str, *, updated: str) -> dict:
    return {
        "title": "campaign", "model": "claude-opus-4-8", "phase": phase, "updated": updated,
        "arms": {"total": 7, "done": 2, "current": "distributional"},
        "candidates": {"run_total": 210, "run_done": 60, "in_arm_total": 30, "in_arm_done": 4},
        "anomalies": {"count": 0, "recent": []},
    }


def test_state_age_and_staleness_threshold() -> None:
    now = time.time()
    fresh = _state("training", updated=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(now - 5)))
    old = _state("training", updated=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(now - 1200)))
    assert monitor.state_age_seconds(fresh, now) is not None and monitor.state_age_seconds(fresh, now) < 60
    assert monitor.is_stale(fresh, now, threshold=300.0) is False
    assert monitor.is_stale(old, now, threshold=300.0) is True  # 20 min silence -> silent-hang flagged


def test_terminal_and_starting_phases_are_never_stale() -> None:
    now = time.time()
    long_ago = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(now - 99999))
    for phase in ("done", "error", "starting"):
        assert monitor.is_stale(_state(phase, updated=long_ago), now, threshold=300.0) is False
    assert monitor.is_stale(None, now, threshold=300.0) is False
    assert monitor.state_age_seconds({"updated": "not-a-timestamp"}, now) is None


def test_anomaly_counts_group_by_kind(tmp_path: Path) -> None:
    _write(tmp_path, "anomalies.jsonl", [
        {"kind": "critic_explosion", "detail": "x"},
        {"kind": "critic_explosion", "detail": "y"},
        {"kind": "ram_pressure_warn", "detail": "z"},
    ])
    counts = monitor.anomaly_counts(tmp_path)
    assert counts == {"critic_explosion": 2, "ram_pressure_warn": 1}
    assert monitor.anomaly_counts(tmp_path / "absent") == {}


def test_token_spend_and_cost_estimate(tmp_path: Path) -> None:
    _write(tmp_path, "events.jsonl", [
        {"event": "run_start"},
        {"event": "llm_call", "in_tok": 1_000_000, "out_tok": 200_000, "model": "claude-opus-4-8"},
        {"event": "llm_call", "in_tok": 500_000, "out_tok": 100_000, "model": "claude-opus-4-8"},
        {"event": "candidate_done", "fitness": 0.1},
    ])
    spend = monitor.token_spend(tmp_path)
    assert spend["calls"] == 2 and spend["costed_calls"] == 2
    assert spend["in_tok"] == 1_500_000 and spend["out_tok"] == 300_000
    # Opus 4.8 list price = $5/Mtok in, $25/Mtok out: 1.5*5 + 0.3*25 = 7.5 + 7.5 = 15.0
    assert abs(spend["usd"] - 15.0) < 1e-6


def test_price_resolution_by_substring_and_unknown_model() -> None:
    assert monitor._resolve_price("claude-sonnet-4-6") == (3.0, 15.0)
    assert monitor._resolve_price("claude-fable-5") == (10.0, 50.0)
    assert monitor._resolve_price("some-other-llm") is None
    assert monitor._resolve_price(None) is None


def test_unknown_model_tokens_counted_but_not_costed(tmp_path: Path) -> None:
    _write(tmp_path, "events.jsonl", [
        {"event": "llm_call", "in_tok": 100, "out_tok": 50, "model": "mystery-model"},
    ])
    spend = monitor.token_spend(tmp_path)
    assert spend["calls"] == 1 and spend["costed_calls"] == 0 and spend["usd"] == 0.0
    assert spend["in_tok"] == 100 and spend["out_tok"] == 50


def test_build_alert_is_status_only(tmp_path: Path) -> None:
    st = _state("done", updated=time.strftime("%Y-%m-%dT%H:%M:%S"))
    msg = monitor.build_alert(st, "done", tmp_path)
    assert "DONE" in msg and "arms 2/7" in msg and "cand 60/210" in msg
    # no progress.json -> graceful
    assert "no progress.json" in monitor.build_alert(None, "stall", tmp_path)


def test_jsonl_cache_reparses_on_change(tmp_path: Path) -> None:
    p = tmp_path / "events.jsonl"
    _write(tmp_path, "events.jsonl", [{"event": "llm_call", "in_tok": 10, "out_tok": 1, "model": "claude-opus-4-8"}])
    assert monitor.token_spend(tmp_path)["calls"] == 1
    time.sleep(0.01)
    p.write_text(p.read_text() + json.dumps({"event": "llm_call", "in_tok": 10, "out_tok": 1, "model": "claude-opus-4-8"}) + "\n", encoding="utf-8")
    assert monitor.token_spend(tmp_path)["calls"] == 2  # cache invalidated on (mtime,size) change
