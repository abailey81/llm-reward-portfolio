"""Campaign-lane health checks — the five SILENT failure modes the sentinel cannot see.

Every one of these is a failure where the machine looks fine, the test flood keeps streaming, and
every existing check stays green while the campaign quietly loses days or validity. The tests are
written around that: each asserts the check FIRES on the silent case and stays quiet otherwise.
"""
from __future__ import annotations

import pytest

from src.cluster.campaign_health import (
    check_capacity_accumulation,
    check_chain_progress,
    check_determinism_homogeneity,
    check_host_failure_concentration,
    check_rung_forecast,
)


# --- 1. capacity accumulation ----------------------------------------------------------------

def test_climbing_capacity_is_OK_and_forbids_premature_reforecast():
    c = check_capacity_accumulation({"status": "climbing", "late_mean_cores": 1500},
                                    expected_cores=2500, hours_in=1.5)
    assert c.severity == "OK" and "do NOT re-forecast" in c.detail


def test_early_plateau_does_NOT_cry_wolf():
    """Accumulation legitimately takes ~2-3 h; a low reading at 1 h is expected, not a fault."""
    c = check_capacity_accumulation({"status": "plateaued", "late_mean_cores": 400},
                                    expected_cores=2500, hours_in=1.0)
    assert c.severity == "INFO" and "too early" in c.detail


def test_a_LOW_plateau_after_the_grace_window_WARNS_and_says_what_to_do():
    """THE plan-changing case: stuck near the probe floor, so the rung must be re-forecast."""
    c = check_capacity_accumulation({"status": "plateaued", "late_mean_cores": 640},
                                    expected_cores=2500, hours_in=6.0)
    assert c.severity == "WARN"
    assert "RE-FORECAST" in c.detail and "26%" in c.detail


def test_a_healthy_plateau_is_OK():
    c = check_capacity_accumulation({"status": "plateaued", "late_mean_cores": 2300},
                                    expected_cores=2500, hours_in=6.0)
    assert c.severity == "OK"


def test_declining_capacity_warns_and_names_the_likely_causes():
    c = check_capacity_accumulation({"status": "declining", "late_mean_cores": 200},
                                    expected_cores=2500, hours_in=8.0)
    assert c.severity == "WARN" and "kill event" in c.detail


def test_insufficient_data_is_INFO_not_a_false_alarm():
    assert check_capacity_accumulation({"status": "insufficient"}, expected_cores=2500,
                                       hours_in=0.5).severity == "INFO"


def test_NO_declared_forecast_reports_the_measurement_instead_of_warning_on_every_run():
    """Judging a plateau against a zero forecast would fire a WARN on every healthy campaign."""
    c = check_capacity_accumulation({"status": "plateaued", "late_mean_cores": 900},
                                    expected_cores=0, hours_in=9.0)
    assert c.severity == "INFO" and "900" in c.detail and "no forecast recorded" in c.detail


# --- 2. critical-path chain progress ---------------------------------------------------------

def test_advancing_chains_are_OK():
    c = check_chain_progress({"bayes_opt": {"completed": 7, "total": 25, "hours_since_last": 3.0},
                              "tpe": {"completed": 5, "total": 20, "hours_since_last": 2.5}})
    assert c.severity == "OK" and "advancing" in c.detail


def test_a_STALLED_chain_is_caught_even_though_everything_else_looks_green():
    """The worst silent failure: the test flood streams on, the makespan floor slips daily."""
    c = check_chain_progress({"bayes_opt": {"completed": 9, "total": 25, "hours_since_last": 18.0}})
    assert c.severity == "WARN"
    assert "STALLED" in c.detail and "not the test flood" in c.detail


def test_a_long_stall_escalates_to_CRITICAL():
    c = check_chain_progress({"bayes_opt": {"completed": 9, "total": 25, "hours_since_last": 40.0}})
    assert c.severity == "CRITICAL"


def test_a_COMPLETED_chain_is_not_reported_as_stalled():
    """A finished chain has no 'last progress' by definition — it must not alarm forever."""
    c = check_chain_progress({"bayes_opt": {"completed": 25, "total": 25,
                                            "hours_since_last": 99.0}})
    assert c.severity == "OK"


# --- 3. bad-node concentration ---------------------------------------------------------------

def test_a_single_bad_node_is_caught_despite_a_tiny_GLOBAL_failure_rate():
    """node-d00a-230 really did this: no apptainer -> rc=127 on every task routed to it. A 1%
    global rate passes every aggregate check while the host keeps eating work."""
    attempts = {f"node-d00a-{i}": 100 for i in range(40)}
    attempts["node-d00a-230"] = 40
    failures = {"node-d00a-230": 40}
    c = check_host_failure_concentration(failures, attempts)
    assert c.severity == "WARN"
    assert "node-d00a-230" in c.detail and "exclude them" in c.detail
    # the global rate is ~1%, which no aggregate check would flag
    assert sum(failures.values()) / sum(attempts.values()) < 0.02


def test_failures_spread_thinly_do_NOT_flag_a_bad_node():
    attempts = {f"n{i}": 50 for i in range(20)}
    failures = {f"n{i}": 2 for i in range(20)}
    assert check_host_failure_concentration(failures, attempts).severity == "OK"


def test_a_host_with_too_few_attempts_is_not_condemned():
    """One failure on a host's first task is noise, not evidence."""
    c = check_host_failure_concentration({"nX": 1}, {"nX": 1, "nY": 200})
    assert c.severity == "OK"


def test_epilogue_rows_aggregate_into_the_bad_node_detectors_input():
    """End-to-end from the ledger line the jobscript actually writes to the fired check."""
    from src.cluster.ledger import host_task_counts

    rows = ([{"task": i, "host": "node-d00a-230", "rc": 127, "secs": 1} for i in range(10)]
            + [{"task": i, "host": "node-e00a-001", "rc": 0, "secs": 30_000} for i in range(50)])
    attempts, failed = host_task_counts(rows)
    assert attempts == {"node-d00a-230": 10, "node-e00a-001": 50}
    assert failed == {"node-d00a-230": 10}
    assert check_host_failure_concentration(failed, attempts).severity == "WARN"


def test_host_counts_skip_unusable_rows_instead_of_inventing_a_phantom_node():
    """A torn/hostless row must not become a bucket — a fake key would read as a bad node."""
    from src.cluster.ledger import host_task_counts

    attempts, failed = host_task_counts(
        [{"task": 1, "rc": 1}, {"task": 2, "host": "", "rc": 1},
         {"task": 3, "host": "nA", "rc": "?"}, {"task": 4, "host": "nA", "rc": 0}])
    assert attempts == {"nA": 2}
    assert failed == {}          # an UNPARSEABLE rc is unknown, never counted as a failure


# --- 4. rung forecast ------------------------------------------------------------------------

RUNGS = {30: 3_930, 100: 8_900, 189: 15_219, 279: 21_609, 340: 25_940, 403: 30_413, 568: 42_128}


def test_forecast_names_the_reachable_rung_and_the_shortfall_to_the_next():
    """6,000 done in 48 h = 125/h; 96 h left -> ~18,000 => rung 189, and 279 is 3,609 short."""
    c = check_rung_forecast(completed_trainings=6_000, elapsed_hours=48.0,
                            hours_remaining=96.0, rung_targets=RUNGS)
    assert c.evidence["rate_per_hour"] == pytest.approx(125.0)
    assert c.evidence["projected"] == 18_000
    assert c.evidence["reachable_rung"] == 189 and c.evidence["next_rung"] == 279
    assert "next rung 279 needs 3,609 more" in c.detail


def test_forecast_reports_the_TOP_rung_when_on_pace_for_it():
    c = check_rung_forecast(completed_trainings=20_000, elapsed_hours=100.0,
                            hours_remaining=300.0, rung_targets=RUNGS)
    assert c.evidence["reachable_rung"] == 568 and c.severity == "OK"


def test_forecast_stays_quiet_before_any_completion():
    assert check_rung_forecast(completed_trainings=0, elapsed_hours=0.0,
                               hours_remaining=700.0, rung_targets=RUNGS).severity == "INFO"


# --- 5. determinism homogeneity --------------------------------------------------------------

def test_a_homogeneous_scored_leg_is_OK():
    c = check_determinism_homogeneity({"envA|dev=cpu": 500})
    assert c.severity == "OK" and c.evidence["n_records"] == 500


def test_a_DEVICE_MIX_in_the_scored_leg_is_CRITICAL_not_a_warning():
    """This is a VALIDITY failure, not a slowdown: a substrate mix confounds every paired
    contrast, and the post-hoc S6 audit would find it far too late to re-run."""
    c = check_determinism_homogeneity({"envA|dev=cpu": 480, "envA|dev=cuda": 20})
    assert c.severity == "CRITICAL"
    assert "not bit-identical" in c.detail and "Quarantine" in c.detail


def test_a_THREAD_regime_mix_is_caught_too():
    c = check_determinism_homogeneity({"omp1|dev=cpu": 300, "omp8|dev=cpu": 5})
    assert c.severity == "CRITICAL"


def test_capture_FAILURES_are_distinguished_from_a_real_substrate_mix():
    """A failed fingerprint capture is an instrumentation problem, not a science problem — the
    operator must not be sent chasing a phantom device mix."""
    c = check_determinism_homogeneity({"envA|dev=cpu": 100, "capture-failed:envA": 3})
    assert c.severity == "CRITICAL"
    assert "capture FAILURES" in c.detail


# --- 6. admin-kill verdict --------------------------------------------------------------------

def test_an_ADMIN_KILL_is_CRITICAL_and_says_RETREAT_not_fight():
    """Tamer's standing priority: keeping Myriad access outranks throughput. The correct response
    is to stop submitting, not to re-submit into an administrative kill."""
    from src.cluster.campaign_health import check_admin_kill

    c = check_admin_kill({"classification": "admin_kill", "action": "retreat",
                          "reason": "18 deaths / 9 hosts in 300s", "n_deaths": 18, "n_hosts": 9,
                          "n_undated": 0})
    assert c.severity == "CRITICAL"
    assert "RETREAT" in c.detail and "do NOT" in c.detail


def test_ordinary_node_failures_do_NOT_alarm():
    from src.cluster.campaign_health import check_admin_kill

    c = check_admin_kill({"classification": "node_failure", "action": "requeue", "n_deaths": 3,
                          "n_hosts": 1, "n_undated": 0})
    assert c.severity == "INFO" and "not an administrative kill" in c.detail


def test_UNDATED_rows_warn_because_the_burst_window_cannot_see_them():
    """A row with no usable ts is invisible to the 300s window, so a real kill could go undetected —
    the failure mode the epilogue `ts` fallback exists to prevent."""
    from src.cluster.campaign_health import check_admin_kill

    c = check_admin_kill({"classification": "ok", "action": "continue", "n_deaths": 5,
                          "n_hosts": 3, "n_undated": 5})
    assert c.severity == "WARN" and "no usable timestamp" in c.detail


def test_the_watcher_NEVER_claims_to_have_enforced_anything():
    """Writing the incident file blocks ALL submission until a human clears it — it can halt a
    23-day campaign, so a read-only watcher must not do it."""
    from src.cluster.campaign_health import check_admin_kill

    for kind in ("admin_kill", "node_failure", "ok"):
        c = check_admin_kill({"classification": kind, "action": "retreat", "n_deaths": 1,
                              "n_hosts": 1, "n_undated": 0})
        assert c.evidence["enforced"] is False


def test_the_kill_verdict_REACHES_the_sentinel_report():
    """The verdict was computed into the inputs dict and read by NO check — so it never reached the
    report, the severity, or the phone alert. This is the wiring lock."""
    from scripts.sentinel import evaluate_health

    report = evaluate_health({
        "exit_code": 0,
        "kill_verdict": {"classification": "admin_kill", "action": "retreat", "n_deaths": 20,
                         "n_hosts": 10, "n_undated": 0},
    })
    names = {c.name for c in report.checks}
    assert "admin_kill" in names
    assert report.severity == "CRITICAL"


# --- integration with the sentinel's report ---------------------------------------------------

def test_a_LAPTOP_run_supplies_none_of_these_inputs_and_gets_none_of_the_checks():
    """No false alarms off-cluster: absent inputs mean the lane checks simply do not appear."""
    from scripts.sentinel import evaluate_health

    names = {c.name for c in evaluate_health({"exit_code": 0}).checks}
    assert not (names & {"capacity_accumulation", "chain_progress", "host_failure_concentration",
                         "rung_forecast", "determinism_homogeneity"})


def test_the_lane_checks_REACH_the_sentinel_report_and_drive_its_severity():
    """The whole point of integrating: a lane failure must escalate the REPORT, not sit in a
    library nobody reads. A device mix has to turn the sentinel CRITICAL."""
    from scripts.sentinel import evaluate_health

    report = evaluate_health({
        "exit_code": 0,
        "accumulation_report": {"status": "plateaued", "late_mean_cores": 600},
        "expected_cores": 2500, "lane_hours_in": 6.0, "lane_hours_remaining": 400.0,
        "chain_progress": {"bayes_opt": {"completed": 3, "total": 25, "hours_since_last": 40.0}},
        "host_attempts": {"nA": 40}, "host_failures": {"nA": 40},
        "rung_targets": RUNGS, "done_test_units": 900,
        "env_fp_labels": {"e|dev=cpu": 800, "e|dev=cuda": 100},
    })
    names = {c.name for c in report.checks}
    assert {"capacity_accumulation", "chain_progress", "host_failure_concentration",
            "rung_forecast", "determinism_homogeneity"} <= names
    assert report.severity == "CRITICAL" and not report.healthy


def test_ONE_lane_input_alone_is_enough_to_activate_just_that_check():
    """The checks are independently opt-in — a partial gather must not suppress the rest."""
    from scripts.sentinel import evaluate_health

    names = {c.name for c in evaluate_health(
        {"exit_code": 0, "chain_progress": {"tpe": {"completed": 1, "total": 20,
                                                    "hours_since_last": 1.0}}}).checks}
    assert "chain_progress" in names and "rung_forecast" not in names


def test_no_fingerprints_yet_is_INFO():
    assert check_determinism_homogeneity({}).severity == "INFO"
    assert check_determinism_homogeneity({"envA": 0}).severity == "INFO"


def test_the_LIVE_check_and_the_S6_GATE_key_on_the_SAME_label():
    """If the live check and the post-hoc gate normalised differently, one would lie about
    homogeneity — and the liar decides whether a paired contrast is valid."""
    from src.cluster.integrity import record_env_label

    cpu = {"env_fingerprint": {"label": "abc|dev=cpu", "env_json_sha256": "0" * 8}}
    gpu = {"env_fingerprint": {"label": "abc|dev=cuda", "env_json_sha256": "0" * 8}}
    census: dict[str, int] = {}
    for rec in [cpu] * 9 + [gpu]:
        lbl = record_env_label(rec)
        census[lbl] = census.get(lbl, 0) + 1
    assert census == {"abc|dev=cpu": 9, "abc|dev=cuda": 1}
    assert check_determinism_homogeneity(census).severity == "CRITICAL"


def test_record_env_label_survives_a_bare_string_and_a_nested_dict():
    """Older records carry a bare string; the 2026-07-13 run_one bug produced a nested dict. Neither
    may crash the gate — the census must still key deterministically."""
    from src.cluster.integrity import record_env_label

    assert record_env_label({"env_fingerprint": "legacy-label"}) == "legacy-label"
    nested = record_env_label({"env_fingerprint": {"label": {"label": "x"}}})
    assert isinstance(nested, str) and record_env_label({"env_fingerprint": {"label": {"label": "x"}}}) == nested
