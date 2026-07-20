"""Offline tests for the per-leg gates (R80/R82): the transport seam takes a fake — no network."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from leg_gates import _flagged, _screen_probes, run_leg_gates  # noqa: E402

_LEG = {"label": "test-leg", "provider": "openrouter", "model": "v/m",
        "api_key_env": "K", "max_tokens": 100}


class _FakeTransport:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls: list[tuple[str, str]] = []
        self.last_cost_usd = 0.001
        self.last_served_model = "v/m-served"
        self.last_stop_reason = "stop"

    def __call__(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        return self._responses.pop(0) if self._responses else "I cannot determine that."


def test_screen_probes_are_deterministic():
    a, b = _screen_probes(), _screen_probes()
    assert a == b and [p["name"] for p in a] == ["continuation", "identification", "canary"]


def test_flag_rules():
    assert _flagged("This is clearly the Lehman collapse of 2008.")
    assert _flagged("These are the returns of Apple during covid.")
    assert not _flagged("The data are anonymized; I cannot determine the source.")


def test_clean_model_passes_screen(tmp_path: Path):
    fake = _FakeTransport(["SMOKE-OK"] + ["I cannot determine that; the series is anonymized."] * 3)
    s = run_leg_gates(_LEG, tmp_path, which=("smoke", "screen"),
                      transport_factory=lambda leg: fake)
    assert s["smoke_ok"] is True
    assert s["screen_verdict"] == "pass" and s["screen_flags"] == []
    rows = [json.loads(x) for x in (tmp_path / "test-leg.jsonl").read_text(
        encoding="utf-8").splitlines()]
    assert len(rows) == 4 and all(r["cost_usd"] == 0.001 for r in rows)  # all archived
    assert (tmp_path / "test-leg.summary.json").exists()


def test_contaminated_model_is_flagged_not_dropped(tmp_path: Path):
    fake = _FakeTransport(["I recognize this — clearly the 2008 Lehman window."] * 3)
    s = run_leg_gates(_LEG, tmp_path, which=("screen",), transport_factory=lambda leg: fake)
    assert s["screen_verdict"] == "FLAG->review"          # routed to Tamer, never silently dropped
    assert set(s["screen_flags"]) <= {"continuation", "identification", "canary"}
    assert len(s["screen_flags"]) >= 1


def test_compliance_rate_scored_on_real_prompts(tmp_path: Path):
    good = "```python\ndef reward(weights, returns, prev_weights, port_ret, info):\n" \
           "    return float(port_ret), {}, None\n```"
    fake = _FakeTransport([good, good, "sorry, no code here", good])
    s = run_leg_gates(_LEG, tmp_path, which=("compliance",), n_compliance=4,
                      transport_factory=lambda leg: fake)
    assert s["compliance_rate"] == pytest.approx(0.75)
    # the REAL frozen prompts were used (same-exam principle)
    system_sent = fake.calls[0][0]
    assert "ANONYMIZED numeric arrays" in system_sent


def test_spend_rides_the_advisory_ledger(tmp_path: Path):
    fake = _FakeTransport(["SMOKE-OK"])
    led = tmp_path / "ledger.jsonl"
    run_leg_gates(_LEG, tmp_path, which=("smoke",), transport_factory=lambda leg: fake,
                  ledger_path=led)
    from src.llm.spend_ledger import spend_summary
    assert spend_summary(led)["n_calls"] == 1
