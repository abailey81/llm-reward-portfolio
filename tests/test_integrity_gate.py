"""Falsification tests for docs/ops/integrity_gate.py.

The gate reported CLEAN against the live archive on 2026-08-01. **That proves nothing on its own** —
a check that cannot fail is not a check. Every test below CORRUPTS a synthetic archive in exactly one
way and asserts the corresponding invariant fires, plus that the CONFIRMATORY/report-only severity
split works, because treating a report-only breach as a run-stopper is the cry-wolf failure that makes
real alarms ignorable.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "integrity_gate", Path(__file__).resolve().parents[1] / "docs" / "ops" / "integrity_gate.py")
gate = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(gate)

SRC_A = "def reward(w, r, p, pr, i):\n    return float(pr), {}, None\n"
SRC_B = "def reward(w, r, p, pr, i):\n    return float(pr) * 2.0, {}, None\n"


def _h(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _rec(root: Path, lane_dir: str, run_id: str, *, arm: str, cid: str, src: str,
         hash_override: str | None = None, fitness: float | None = None,
         fallback: tuple[int, int] | None = None) -> None:
    d = root / lane_dir / arm / run_id
    d.mkdir(parents=True, exist_ok=True)
    metrics: dict = {}
    if fitness is not None:
        metrics["val_fitness"] = fitness
    if fallback is not None:
        metrics["train_safe_default_count"], metrics["train_safe_call_count"] = fallback
    (d / "record.json").write_text(json.dumps({
        "run_id": run_id, "arm": arm, "candidate_id": cid,
        "reward_source": src, "reward_source_hash": hash_override or _h(src),
        "metrics": metrics,
    }), encoding="utf-8")


def _calls(root: Path, lane_dir: str, rows: list[dict]) -> None:
    d = root / lane_dir / "arm"
    d.mkdir(parents=True, exist_ok=True)
    (d / "llm_calls.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


@pytest.fixture()
def clean(tmp_path: Path) -> Path:
    """A minimal archive that satisfies every invariant."""
    root = tmp_path / "run"
    _rec(root, "search", "c0", arm="distributional", cid="c0", src=SRC_A, fitness=0.5)
    _rec(root, "search", "c1", arm="distributional", cid="c1", src=SRC_B, fitness=0.1)
    _rec(root, "frozen", "w", arm="distributional", cid="c0", src=SRC_A)
    _rec(root, "test", "t0", arm="distributional", cid="c0", src=SRC_A)
    return root


def test_clean_archive_passes(clean: Path):
    """POSITIVE CONTROL: with nothing corrupted the gate must be silent."""
    assert gate.check(clean) == []


class TestFalsification:
    def test_I1_self_hash_breach_fires(self, clean: Path):
        _rec(clean, "search", "bad", arm="distributional", cid="bad", src=SRC_A,
             hash_override=_h("something else"), fitness=0.0)
        assert any(b["invariant"].startswith("I1") for b in gate.check(clean))

    def test_I2_search_to_frozen_breach_fires(self, clean: Path):
        # the frozen winner claims candidate c0 but carries a DIFFERENT program
        _rec(clean, "frozen", "w", arm="distributional", cid="c0", src=SRC_B)
        assert any(b["invariant"].startswith("I2") for b in gate.check(clean))

    def test_I3_frozen_to_test_breach_fires(self, clean: Path):
        """The one that would invalidate the headline: TEST scored code that never won."""
        _rec(clean, "test", "t0", arm="distributional", cid="c0", src=SRC_B)
        breaches = gate.check(clean)
        assert any(b["invariant"].startswith("I3") for b in breaches)
        assert any(b["confirmatory"] for b in breaches)

    def test_I4_selection_breach_fires(self, clean: Path):
        # freeze the WORSE candidate while a better ELIGIBLE one exists
        _rec(clean, "frozen", "w", arm="distributional", cid="c1", src=SRC_B)
        assert any(b["invariant"].startswith("I4") for b in gate.check(clean))

    def test_I4_ineligible_best_is_NOT_a_breach(self, clean: Path):
        """R115 exclusion is CORRECT behaviour, not a selection defect.

        A higher-fitness candidate that sits at/above the fallback floor must be skipped, and the
        gate must not report that as a breach — otherwise it would fire on every arm where the floor
        did its job, which is the fastest way to make an alarm ignorable.
        """
        _rec(clean, "search", "hot", arm="distributional", cid="hot", src=SRC_B,
             fitness=99.0, fallback=(200_000, 400_000))     # 50% -> ineligible
        assert not any(b["invariant"].startswith("I4") for b in gate.check(clean))

    def test_I5_model_pin_breach_fires(self, clean: Path):
        _calls(clean, "search", [{"model": "claude-opus-5", "served_model": "claude-haiku-4-5",
                                  "request_pins": {}}])
        breaches = gate.check(clean)
        assert any(b["invariant"].startswith("I5") for b in breaches)
        assert any(b["confirmatory"] for b in breaches)

    def test_I5_known_kimi_alias_is_NOT_a_breach(self, clean: Path):
        """§100.26 is DISCLOSED, not silenced — and allow-listed by EXACT pair, not by prefix."""
        _calls(clean, "search_leg_kimi_k3",
               [{"model": "moonshotai/kimi-k3-20260715", "served_model": "moonshotai/kimi-k3",
                 "request_pins": {}}])
        assert not any(b["invariant"].startswith("I5") for b in gate.check(clean))

    def test_I5_a_DIFFERENT_alias_still_fires(self, clean: Path):
        """The allow-list must not become a blanket family-match."""
        _calls(clean, "search_leg_kimi_k3",
               [{"model": "moonshotai/kimi-k3-20260715", "served_model": "moonshotai/kimi-k2",
                 "request_pins": {}}])
        assert any(b["invariant"].startswith("I5") for b in gate.check(clean))


class TestSeverity:
    def test_report_only_breach_is_NOT_confirmatory(self, clean: Path):
        _rec(clean, "search_leg_glm_5_2", "bad", arm="scalar", cid="bad", src=SRC_A,
             hash_override=_h("nope"), fitness=0.0)
        breaches = gate.check(clean)
        assert breaches, "the breach must still be reported"
        assert not any(b["confirmatory"] for b in breaches), "a leg breach must not read CONFIRMATORY"

    def test_core_and_h3ss_both_count_as_confirmatory(self, clean: Path):
        _rec(clean, "search_h3_singleshot", "bad", arm="distributional", cid="bad", src=SRC_A,
             hash_override=_h("nope"), fitness=0.0)
        assert any(b["confirmatory"] for b in gate.check(clean))

    def test_exit_codes(self, clean: Path, capsys):
        assert gate.main([str(clean), "--quiet"]) == 0
        _rec(clean, "search_leg_glm_5_2", "bad", arm="scalar", cid="bad", src=SRC_A,
             hash_override=_h("nope"), fitness=0.0)
        assert gate.main([str(clean), "--quiet"]) == 1          # report-only -> ATTN
        _rec(clean, "test", "t0", arm="distributional", cid="c0", src=SRC_B)
        assert gate.main([str(clean), "--quiet"]) == 2          # confirmatory -> CRITICAL


class TestRobustness:
    def test_quarantine_and_pull_tmp_are_excluded(self, clean: Path):
        """A quarantined record must not be able to fail the gate (§100.9 / D16)."""
        _rec(clean, "_quarantine_x", "bad", arm="distributional", cid="bad", src=SRC_A,
             hash_override=_h("nope"))
        _rec(clean, ".pull_tmp_y", "bad2", arm="distributional", cid="bad2", src=SRC_A,
             hash_override=_h("nope"))
        assert gate.check(clean) == []

    def test_baseline_marker_records_do_not_trip_I3(self, clean: Path):
        """Hand-written baselines carry a marker comment and no hash — they must be skipped."""
        d = clean / "test" / "baseline_raw_return" / "s0"
        d.mkdir(parents=True, exist_ok=True)
        (d / "record.json").write_text(json.dumps({
            "run_id": "s0", "arm": "baseline_raw_return", "candidate_id": "s0",
            "reward_source": "# baseline:raw_return\n", "reward_source_hash": "", "metrics": {},
        }), encoding="utf-8")
        assert not any(b["invariant"].startswith("I3") for b in gate.check(clean))

    def test_missing_archive_does_not_raise(self, tmp_path: Path):
        assert gate.check(tmp_path / "nope") == []
