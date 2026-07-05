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


# --------------------------------------------------------------------------- #
# 2026-07-06 deep-monitoring layer: B1 stall / B3 forecast / B4 coverage / B5 taxonomy
# --------------------------------------------------------------------------- #
def test_completion_stall_self_calibrates_to_the_cadence() -> None:
    # 10 completions at a steady 100 s cadence, last one at t=1000
    times = [float(100 * i) for i in range(1, 11)]
    # fresh (silence 50 s < 3x median) -> OK
    assert S.check_completion_stall(times, 1050.0, floor_s=10.0).severity == S.OK
    # silence 400 s > 3x median(100) -> WARN
    assert S.check_completion_stall(times, 1400.0, floor_s=10.0).severity == S.WARN
    # silence 900 s > 8x median -> CRITICAL (a wedged training with an alive driver)
    c = S.check_completion_stall(times, 1900.0, floor_s=10.0)
    assert c.severity == S.CRITICAL
    assert c.evidence["median_gap_s"] == 100.0


def test_completion_stall_floor_prevents_fast_cadence_false_alarms() -> None:
    # a dev run completing every 2 s must not WARN after 30 s of silence: the floor dominates
    times = [float(2 * i) for i in range(1, 11)]
    assert S.check_completion_stall(times, 50.0).severity == S.OK  # default floor 1800 s


def test_completion_stall_edges() -> None:
    assert S.check_completion_stall(None, 100.0).severity == S.INFO      # no journal yet
    assert S.check_completion_stall([1.0, 2.0], 100.0).severity == S.INFO  # <3 completions
    assert S.check_completion_stall(None, 100.0, terminal=True).severity == S.OK
    # the in-driver detector corroborates: stall events escalate even without a yardstick
    assert S.check_completion_stall([1.0], 100.0, n_recent_stall_events=2).severity == S.WARN
    times = [float(100 * i) for i in range(1, 11)]
    assert S.check_completion_stall(times, 1050.0, n_recent_stall_events=1,
                                    floor_s=10.0).severity == S.WARN


def test_disk_forecast_flat_shrinking_and_edges() -> None:
    assert S.check_disk_forecast(None).severity == S.INFO
    assert S.check_disk_forecast([(0.0, 100.0)] * 3).severity == S.INFO  # <5 samples
    flat = [(float(3600 * i), 100.0) for i in range(6)]
    assert S.check_disk_forecast(flat).severity == S.INFO or S.check_disk_forecast(flat).severity == S.OK
    # shrinking 1 GB/h from 40 GB -> floor 20 GB in ~20 h -> WARN (48 h) not CRITICAL (12 h)
    shrink = [(float(3600 * i), 45.0 - 1.0 * i) for i in range(6)]
    c = S.check_disk_forecast(shrink)
    assert c.severity == S.WARN
    assert 15.0 < c.evidence["hours_to_floor"] < 25.0
    # shrinking 4 GB/h from 40 GB -> floor in ~5 h -> CRITICAL
    fast = [(float(3600 * i), 60.0 - 4.0 * i) for i in range(6)]
    assert S.check_disk_forecast(fast).severity == S.CRITICAL


def test_disk_forecast_degenerate_spacing_is_info() -> None:
    assert S.check_disk_forecast([(5.0, 50.0)] * 6).severity == S.INFO


def test_unit_coverage_progress_shortfall_and_overrun() -> None:
    # mid-run progress -> INFO with pct + ETA
    c = S.check_unit_coverage(105, 210, "search", rate_per_h=2.0)
    assert c.severity == S.INFO
    assert c.evidence["eta_h"] == 52.5
    # complete -> OK
    assert S.check_unit_coverage(210, 210, "search").severity == S.OK
    # claims complete but units missing -> CRITICAL (the silent-shortfall husk class)
    c = S.check_unit_coverage(300, 330, "test", claimed_complete=True)
    assert c.severity == S.CRITICAL
    # MORE units than the frozen design expects -> WARN (duplicates / config drift)
    assert S.check_unit_coverage(340, 330, "test").severity == S.WARN
    # ledger unavailable -> INFO, never a false alarm
    assert S.check_unit_coverage(None, 330, "test").severity == S.INFO
    assert S.check_unit_coverage(10, None, "test").severity == S.INFO


def test_error_taxonomy_volume_thresholds() -> None:
    assert S.check_error_taxonomy(None).severity == S.OK
    assert S.check_error_taxonomy({}).severity == S.OK
    small = {"oom": {"count": 2, "arms": ["scalar"]}, "stall": {"count": 1, "arms": []}}
    c = S.check_error_taxonomy(small)
    assert c.severity == S.INFO and c.evidence["total"] == 3
    wave = {"oom": {"count": 12, "arms": ["scalar", "placebo"]}}
    c = S.check_error_taxonomy(wave)
    assert c.severity == S.WARN and "oom" in c.detail


def test_gatherer_reads_journal_and_coverage(tmp_path: Path) -> None:
    """events.jsonl seed_done lines -> completion_times + taxonomy; archive record.json counts ->
    done units; config -> expected units (present when config/campaign.yaml is loadable)."""
    run = tmp_path / "campaign"
    (run / "search" / "scalar" / "c0").mkdir(parents=True)
    (run / "search" / "scalar" / "c0" / "record.json").write_text("{}", encoding="utf-8")
    (run / "test" / "scalar" / "scalar-s0").mkdir(parents=True)
    (run / "test" / "scalar" / "scalar-s0" / "record.json").write_text("{}", encoding="utf-8")
    lines = [
        json.dumps({"ts": "2026-07-06T10:00:00", "level": "INFO", "event": "seed_done",
                    "run_id": "scalar-s0", "arm": "scalar"}),
        json.dumps({"ts": "2026-07-06T10:05:00", "level": "WARNING", "event": "seed_failed",
                    "run_id": "scalar-s1", "arm": "scalar", "error": "CUDA out of memory"}),
    ]
    (run / "events.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    inputs = S.gather_inputs(run)
    assert inputs["done_search_units"] == 1
    assert inputs["done_test_units"] == 1
    assert len(inputs.get("completion_times", [])) == 1
    assert inputs["error_taxonomy"]["oom"]["count"] == 1
    assert "now" in inputs
    # the report over these inputs runs the new checks without raising
    report = S.evaluate_health(inputs)
    names = {c.name for c in report.checks}
    assert {"completion_stall", "coverage_search", "coverage_test", "error_taxonomy"} <= names


def test_fps_downward_drift_alarms_and_stable_is_ok() -> None:
    """B2: a sustained fps FALL (thermal creep) alarms via the direction='down' CUSUM; normal
    fluctuation around the baseline stays OK."""
    target = 200.0
    sinking = [200.0, 198.0, 192.0, 185.0, 176.0, 168.0, 160.0, 152.0]
    c = S.check_metric_drift("fps", sinking, target, k=0.05 * target, h=0.30 * target,
                             direction="down")
    assert c.severity == S.WARN and "downward" in c.detail
    stable = [200.0, 203.0, 197.0, 201.0, 199.0, 202.0, 198.0]
    assert S.check_metric_drift("fps", stable, target, k=0.05 * target, h=0.30 * target,
                                direction="down").severity == S.OK


def test_evaluate_health_runs_fps_drift_when_armed() -> None:
    report = S.evaluate_health({
        "disk_free_gb": 100.0,
        "fps_target": 200.0,
        "fps_history": [200.0, 198.0, 192.0, 185.0, 176.0, 168.0, 160.0, 152.0],
    })
    drift = next(c for c in report.checks if c.name == "fps_drift")
    assert drift.severity == S.WARN


# --------------------------------------------------------------------------- #
# 2026-07-06 S17-S20: the gatherer PRODUCES the rate/scale inputs; coverage
# reconciles ledgered failures; transitions persist to the sidecar; the journal
# probe unions the search/ ledger location.
# --------------------------------------------------------------------------- #
def _mk_record(root: Path, stage: str, arm: str, rid: str, *, fitness: float = 0.1,
               raw_rms: float | None = None) -> None:
    d = root / stage / arm / rid
    d.mkdir(parents=True, exist_ok=True)
    metrics: dict = {"val_fitness": fitness}
    if raw_rms is not None:
        metrics["popart_scale"] = {"raw_rms_max": raw_rms, "raw_rms_last": raw_rms * 0.9}
    (d / "record.json").write_text(
        json.dumps({"run_id": rid, "arm": arm, "candidate_id": rid, "metrics": metrics}),
        encoding="utf-8",
    )


def test_gatherer_produces_rate_scale_and_failure_inputs(tmp_path: Path) -> None:
    """S17: n_records/n_nonfinite/n_candidates/n_attempted/raw_rms_by_arm/n_failed must be PRODUCED
    from the archive + BOTH failure-ledger layouts (they were never produced before — six checks
    plus both CUSUM monitors were permanently inert live)."""
    run = tmp_path / "campaign"
    S._RECORD_CACHE.clear()
    _mk_record(run, "search", "scalar", "scalar-c0", fitness=0.2, raw_rms=1.5)
    _mk_record(run, "search", "scalar", "scalar-c1", fitness=float("nan"))
    _mk_record(run, "search", "distributional", "distributional-c0", fitness=0.3, raw_rms=160.0)
    _mk_record(run, "test", "scalar", "scalar-s0", fitness=0.1)
    # parallel-layout ledger + serial-layout ledger, one failure each (distinct candidate ids)
    (run / "search" / "scalar").mkdir(parents=True, exist_ok=True)
    (run / "search" / "scalar" / "failures.jsonl").write_text(
        json.dumps({"candidate_id": "scalar-g0-c9", "error": "sandbox: rejected"}) + "\n",
        encoding="utf-8",
    )
    (run / "search" / "proto-distributional.failures.jsonl").write_text(
        json.dumps({"candidate_id": "distributional-g1-c4", "error": "sandbox: rejected"}) + "\n",
        encoding="utf-8",
    )
    inputs = S.gather_inputs(run)
    assert inputs["n_records"] == 4 and inputs["n_nonfinite"] == 1
    assert inputs["n_candidates"] == 3  # search records only
    assert inputs["n_failed"] == 2  # one per ledger layout, deduped by candidate_id
    assert inputs["n_attempted"] == 5  # 3 archived search candidates + 2 ledgered failures
    assert inputs["raw_rms_by_arm"] == {"scalar": 1.5, "distributional": 160.0}
    # the reward-scale drift check now has real inputs: 160/1.5 > 100 -> WARN fires
    report = S.evaluate_health(inputs)
    scale = next(c for c in report.checks if c.name == "reward_scale")
    assert scale.severity in (S.WARN, S.CRITICAL)
    nan = next(c for c in report.checks if c.name == "nan_rate")
    assert nan.severity != S.INFO  # no longer inert: 1/4 non-finite exceeds the warn threshold


def test_coverage_reconciles_ledgered_failures_S19(tmp_path: Path) -> None:
    """S19: a claimed-complete stage whose record shortfall is ACCOUNTED by known failures is a
    disclosed partial (WARN), not the silent-shortfall CRITICAL husk class."""
    c = S.check_unit_coverage(300, 330, "test", claimed_complete=True, known_failures=30)
    assert c.severity == S.WARN and "accounted" in c.detail
    c = S.check_unit_coverage(300, 330, "test", claimed_complete=True, known_failures=5)
    assert c.severity == S.CRITICAL  # 25 units of UNACCOUNTED shortfall remain


def test_transitions_persist_to_sidecar_S18(tmp_path: Path) -> None:
    """S18: severity transitions must land in <run_dir>/sentinel_events.jsonl (the sentinel runs in
    its own process, so the run's root-logger events.jsonl handler can never see them)."""
    report = S.HealthReport([S.HealthCheck("disk", S.CRITICAL, "free disk 1.0 GB < floor")])
    last: dict = {}
    S._emit_transitions(report, last, tmp_path)
    side = tmp_path / "sentinel_events.jsonl"
    rows = [json.loads(ln) for ln in side.read_text(encoding="utf-8").splitlines()]
    assert rows and rows[0]["check"] == "disk" and rows[0]["severity"] == S.CRITICAL
    # no re-emit while the severity holds; a change re-emits
    S._emit_transitions(report, last, tmp_path)
    assert len(side.read_text(encoding="utf-8").splitlines()) == 1
    S._emit_transitions(S.HealthReport([S.HealthCheck("disk", S.OK, "free disk 100 GB")]), last, tmp_path)
    assert len(side.read_text(encoding="utf-8").splitlines()) == 2


def test_journal_probe_unions_search_ledger_S20(tmp_path: Path) -> None:
    """S20: the campaign logs under <output>/search — pointing the sentinel at the campaign ROOT
    (the documented invocation) must still find the completion stream."""
    run = tmp_path / "campaign"
    (run / "search").mkdir(parents=True)
    line = json.dumps({"ts": "2026-07-06T10:00:00", "level": "INFO", "event": "seed_done",
                       "run_id": "scalar-s0", "arm": "scalar"})
    (run / "search" / "events.jsonl").write_text(line + "\n", encoding="utf-8")
    S._RECORD_CACHE.clear()
    inputs = S.gather_inputs(run)
    assert len(inputs.get("completion_times", [])) == 1
