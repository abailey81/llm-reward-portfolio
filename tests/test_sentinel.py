"""Tests for the campaign SENTINEL (scripts/sentinel.py) — the invariant health-monitor.

Pin the PURE check functions (severity boundaries, total on bad input), the aggregation to the worst
severity, the divergence-run clustering heuristic, and the disk-backed gatherer + report round-trip.
Import-light (no torch/live run); the sentinel is READ-ONLY by construction.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import sentinel as S  # noqa: E402


# --------------------------------------------------------------------------- #
# Severity ladder + aggregation                                               #
# --------------------------------------------------------------------------- #
def test_worst_severity_ordering() -> None:
    assert S.worst([]) == S.OK
    assert S.worst([S.OK, S.INFO]) == S.INFO
    assert S.worst([S.OK, S.WARN, S.INFO]) == S.WARN
    assert S.worst([S.WARN, S.CRITICAL]) == S.CRITICAL
    # UNKNOWN is NOT healthy — it ranks with WARN (an uncheckable invariant is not "OK").
    assert S.worst([S.OK, S.UNKNOWN]) == S.UNKNOWN
    assert S._RANK[S.UNKNOWN] == S._RANK[S.WARN]


# --------------------------------------------------------------------------- #
# System-resource checks                                                       #
# --------------------------------------------------------------------------- #
def test_check_disk_boundaries() -> None:
    assert S.check_disk(None).severity == S.UNKNOWN
    assert S.check_disk(50.0).severity == S.OK
    assert S.check_disk(25.0).severity == S.WARN     # < warn 30, >= floor 20
    assert S.check_disk(5.0).severity == S.CRITICAL  # < floor 20


def test_check_ram_and_gpu_boundaries() -> None:
    assert S.check_ram(None).severity == S.UNKNOWN
    assert S.check_ram(50.0).severity == S.OK
    assert S.check_ram(90.0).severity == S.WARN
    assert S.check_ram(97.0).severity == S.CRITICAL
    assert S.check_gpu_temp(None).severity == S.UNKNOWN
    assert S.check_gpu_temp(60.0).severity == S.OK
    assert S.check_gpu_temp(86.0).severity == S.WARN
    assert S.check_gpu_temp(92.0).severity == S.CRITICAL


def test_check_silent_hang_terminal_is_never_hung() -> None:
    assert S.check_silent_hang(99999.0, terminal=True).severity == S.OK
    assert S.check_silent_hang(None).severity == S.UNKNOWN
    assert S.check_silent_hang(60.0).severity == S.OK
    assert S.check_silent_hang(1500.0).severity == S.WARN
    assert S.check_silent_hang(4000.0).severity == S.CRITICAL


# --------------------------------------------------------------------------- #
# Run-integrity checks (the "surfaces at the end" class)                       #
# --------------------------------------------------------------------------- #
def test_check_gate_failure_rate() -> None:
    assert S.check_gate_failure_rate(0, 0).severity == S.INFO       # nothing attempted
    assert S.check_gate_failure_rate(1, 40).severity == S.OK        # ~prototype 2.5%
    assert S.check_gate_failure_rate(6, 40).severity == S.WARN      # 15%
    assert S.check_gate_failure_rate(20, 40).severity == S.CRITICAL # 50%


def test_check_nan_rate_any_nonfinite_warns() -> None:
    assert S.check_nan_rate(0, 100).severity == S.OK
    assert S.check_nan_rate(1, 100).severity == S.WARN      # ANY non-finite is worth surfacing
    assert S.check_nan_rate(15, 100).severity == S.CRITICAL


def test_check_divergence_rate_and_diverged_winner() -> None:
    assert S.check_divergence_rate(0, 30).severity == S.OK
    assert S.check_divergence_rate(2, 30).severity == S.WARN       # ~6.7%
    assert S.check_divergence_rate(10, 30).severity == S.CRITICAL
    # A diverged WINNER is a selection-integrity alarm regardless of the rate.
    assert S.check_divergence_rate(0, 30, winner_diverged=True).severity == S.CRITICAL


def test_check_reward_scale_drift_p5_confound() -> None:
    assert S.check_reward_scale_drift({}).severity == S.INFO
    assert S.check_reward_scale_drift({"a": 1.0}).severity == S.INFO   # need >= 2
    assert S.check_reward_scale_drift({"a": 1.0, "b": 2.0}).severity == S.OK
    assert S.check_reward_scale_drift({"a": 1.0, "b": 500.0}).severity == S.WARN
    assert S.check_reward_scale_drift({"a": 1e-2, "b": 1e4}).severity == S.CRITICAL


def test_check_api_error_rate() -> None:
    assert S.check_api_error_rate(0, 0).severity == S.INFO
    assert S.check_api_error_rate(1, 100).severity == S.OK
    assert S.check_api_error_rate(8, 100).severity == S.WARN
    assert S.check_api_error_rate(30, 100).severity == S.CRITICAL


def test_check_progress_husk_is_critical() -> None:
    assert S.check_progress(7, 7).severity == S.OK
    assert S.check_progress(3, 7).severity == S.INFO
    # a completed run whose gate says not-all-tested is a husk (M19 class)
    assert S.check_progress(7, 7, all_arms_tested=False).severity == S.CRITICAL


def test_check_exit_code() -> None:
    assert S.check_exit_code(None).severity == S.OK
    assert S.check_exit_code(0).severity == S.OK
    assert S.check_exit_code(3).severity == S.CRITICAL


# --------------------------------------------------------------------------- #
# Divergence-run clustering (line count over-states runs)                      #
# --------------------------------------------------------------------------- #
def test_cluster_diverged_runs_by_step_reset() -> None:
    # 5 explosion lines with ONE step reset (100 -> 5) = 2 distinct diverged runs.
    lines = [
        {"kind": "critic_explosion", "step": 50},
        {"kind": "critic_explosion", "step": 100},
        {"kind": "critic_explosion", "step": 5},    # step went backwards -> new run
        {"kind": "critic_explosion", "step": 20},
        {"kind": "ram_pressure", "step": 999},       # not a critic line -> ignored
    ]
    assert S._cluster_diverged_runs(lines) == 2
    assert S._cluster_diverged_runs([]) == 0


# --------------------------------------------------------------------------- #
# Aggregation + gatherer round-trip                                            #
# --------------------------------------------------------------------------- #
def test_evaluate_health_aggregates_worst() -> None:
    report = S.evaluate_health({
        "disk_free_gb": 5.0,           # CRITICAL
        "ram_used_pct": 50.0,          # OK
        "n_failed": 1, "n_attempted": 40,  # OK
        "seen_arms": 7, "expected_arms": 7,
    })
    assert report.severity == S.CRITICAL
    assert not report.healthy
    assert any(c.name == "disk" and c.severity == S.CRITICAL for c in report.checks)


def test_evaluate_health_all_ok_is_healthy() -> None:
    report = S.evaluate_health({
        "disk_free_gb": 100.0, "ram_used_pct": 40.0, "gpu_temp_c": 55.0,
        "progress_age_s": 30.0, "n_failed": 0, "n_attempted": 30,
        "n_nonfinite": 0, "n_records": 30, "n_diverged_runs": 0, "n_candidates": 30,
        "raw_rms_by_arm": {"a": 1.0, "b": 1.5}, "n_api_errors": 0, "n_api_calls": 30,
        "seen_arms": 7, "expected_arms": 7, "exit_code": 0,
    })
    assert report.healthy
    assert report.severity in (S.OK, S.INFO)


def test_gather_inputs_reads_summary_and_anomalies(tmp_path: Path) -> None:
    (tmp_path / "campaign_summary.json").write_text(
        json.dumps({"exit_code": 3, "all_arms_tested": False,
                    "arms": [{"arm": "distributional"}, {"arm": "scalar"}]}),
        encoding="utf-8")
    (tmp_path / "anomalies.jsonl").write_text(
        "\n".join(json.dumps(x) for x in [
            {"kind": "critic_explosion", "step": 10},
            {"kind": "critic_explosion", "step": 3},  # reset -> 2 runs
        ]), encoding="utf-8")
    got = S.gather_inputs(tmp_path)
    assert got["exit_code"] == 3
    assert got["all_arms_tested"] is False
    assert got["seen_arms"] == 2
    assert got["n_diverged_runs"] == 2
    # the report built from a real husk summary is CRITICAL (exit 3 + not-all-tested)
    report = S.evaluate_health(got)
    assert report.severity == S.CRITICAL


def test_render_report_is_stringable() -> None:
    report = S.evaluate_health({"disk_free_gb": 100.0, "seen_arms": 1, "expected_arms": 1})
    text = S.render_report(report)
    assert "CAMPAIGN SENTINEL" in text and "disk" in text


# --------------------------------------------------------------------------- #
# Statistical process control — CUSUM change-point drift detection             #
# --------------------------------------------------------------------------- #
def test_cusum_stable_series_no_alarm() -> None:
    alarmed, idx, s = S.cusum([0.02, 0.03, 0.02, 0.03, 0.02, 0.03], 0.0, k=0.03, h=0.15)
    assert alarmed is False and idx == -1 and s == 0.0


def test_cusum_upward_drift_alarms_early() -> None:
    # a slowly-rising rate breaches the CUSUM decision interval BEFORE any single value is extreme
    alarmed, idx, s = S.cusum([0.02, 0.05, 0.09, 0.13, 0.18, 0.22], 0.0, k=0.03, h=0.15)
    assert alarmed is True
    assert idx == 3            # caught mid-stream, not at the last (extreme) point
    assert s > 0.15


def test_cusum_total_on_bad_input() -> None:
    # non-numeric entries are skipped, never raise
    alarmed, _, _ = S.cusum([0.0, None, "x", 0.0], 0.0, k=0.01, h=0.05)  # type: ignore[list-item]
    assert alarmed is False


def test_check_metric_drift_needs_min_points_then_warns() -> None:
    assert S.check_metric_drift("gate_failure", [0.5, 0.5], 0.0, k=0.03, h=0.15).severity == S.INFO
    drifting = [0.02, 0.05, 0.09, 0.13, 0.18, 0.22]
    assert S.check_metric_drift("gate_failure", drifting, 0.0, k=0.03, h=0.15).severity == S.WARN
    stable = [0.02, 0.03, 0.02, 0.03, 0.02, 0.03]
    assert S.check_metric_drift("gate_failure", stable, 0.0, k=0.03, h=0.15).severity == S.OK


def test_evaluate_health_runs_drift_checks_when_history_present() -> None:
    report = S.evaluate_health({
        "disk_free_gb": 100.0, "seen_arms": 7, "expected_arms": 7,
        "gate_failure_history": [0.02, 0.05, 0.09, 0.13, 0.18, 0.22],  # drifting up
    })
    drift = next(c for c in report.checks if c.name == "gate_failure_drift")
    assert drift.severity == S.WARN
