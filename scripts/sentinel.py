#!/usr/bin/env python3
"""Campaign SENTINEL — a continuous, read-only invariant health-monitor for the unattended run.

The dashboard (``scripts/monitor.py``) shows you what is HAPPENING; the sentinel decides whether what
is happening is HEALTHY, and it is designed to catch **anything even slightly off, as early as
possible** — the whole point being that nothing about a wrong result surfaces only at the end
(2026-07-05, world-class-monitoring requirement).

Design.
* **Pure check functions** (``check_*``) take already-parsed inputs and return a :class:`HealthCheck`
  with a severity + human detail + a machine ``evidence`` dict. They are total (never raise on bad
  input) and unit-tested WITHOUT disk or a live run.
* A **gatherer** (:func:`gather_inputs`) reads the on-disk campaign artifacts + system telemetry
  READ-ONLY (records, ``anomalies.jsonl``, ``progress.json``, ``campaign_summary.json``, disk/RAM/GPU),
  each probe guarded so one failure degrades a single check to ``UNKNOWN`` rather than killing the
  sentinel.
* :func:`evaluate_health` runs every check and aggregates the worst severity into a
  :class:`HealthReport`. The CLI (:func:`main`) prints it (``--once``) or watches on an interval
  (``--watch``), emits every status TRANSITION to the structured event log (``events.jsonl``) so the
  precise log carries the full health history, and exits non-zero on a CRITICAL so a supervisor/cron
  can act.

Severity ladder: ``OK`` < ``INFO`` < ``WARN`` < ``CRITICAL`` (and ``UNKNOWN`` for an unreadable probe,
ranked with WARN — an invariant we cannot check is not silently "healthy"). READ-ONLY: the sentinel
never touches the run; it only observes.
"""
from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# --------------------------------------------------------------------------- #
# Severity model                                                              #
# --------------------------------------------------------------------------- #
OK = "OK"
INFO = "INFO"
WARN = "WARN"
CRITICAL = "CRITICAL"
UNKNOWN = "UNKNOWN"

#: Rank for aggregation + exit-code. UNKNOWN ranks with WARN (an uncheckable invariant is NOT healthy).
_RANK: dict[str, int] = {OK: 0, INFO: 1, UNKNOWN: 2, WARN: 2, CRITICAL: 3}


def worst(severities: list[str]) -> str:
    """The highest-rank severity in the list (``OK`` if empty)."""
    return max(severities, key=lambda s: _RANK.get(s, 0)) if severities else OK


@dataclass
class HealthCheck:
    """One invariant's verdict: a name, a severity, a human detail, and machine evidence."""

    name: str
    severity: str
    detail: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "severity": self.severity, "detail": self.detail,
                "evidence": self.evidence}


@dataclass
class HealthReport:
    """The aggregate: every check + the worst severity + the CRITICAL/WARN shortlists."""

    checks: list[HealthCheck]

    @property
    def severity(self) -> str:
        return worst([c.severity for c in self.checks])

    @property
    def healthy(self) -> bool:
        return self.severity in (OK, INFO)

    def by_severity(self, sev: str) -> list[HealthCheck]:
        return [c for c in self.checks if c.severity == sev]

    def as_dict(self) -> dict[str, Any]:
        return {"severity": self.severity, "healthy": self.healthy,
                "checks": [c.as_dict() for c in self.checks]}


# --------------------------------------------------------------------------- #
# PURE CHECK FUNCTIONS (unit-tested without disk or a live run)               #
# --------------------------------------------------------------------------- #
def check_disk(free_gb: float | None, *, floor_gb: float = 20.0, warn_gb: float = 30.0) -> HealthCheck:
    """The run drive: the pagefile + Windows Update live on C:, and a full drive kills the run in ways
    the stall detector only reports after the fact."""
    if free_gb is None:
        return HealthCheck("disk", UNKNOWN, "could not read free disk space")
    if free_gb < floor_gb:
        return HealthCheck("disk", CRITICAL, f"free disk {free_gb:.1f} GB < floor {floor_gb} GB",
                           {"free_gb": free_gb, "floor_gb": floor_gb})
    if free_gb < warn_gb:
        return HealthCheck("disk", WARN, f"free disk {free_gb:.1f} GB approaching floor {floor_gb} GB",
                           {"free_gb": free_gb})
    return HealthCheck("disk", OK, f"free disk {free_gb:.1f} GB", {"free_gb": free_gb})


def check_ram(used_pct: float | None, *, warn: float = 88.0, crit: float = 95.0) -> HealthCheck:
    """RAM pressure — the transition-wave OOM (why n_gpu is capped at 3) shows here first."""
    if used_pct is None:
        return HealthCheck("ram", UNKNOWN, "could not read RAM usage")
    if used_pct >= crit:
        return HealthCheck("ram", CRITICAL, f"RAM {used_pct:.0f}% used (OOM risk)", {"used_pct": used_pct})
    if used_pct >= warn:
        return HealthCheck("ram", WARN, f"RAM {used_pct:.0f}% used", {"used_pct": used_pct})
    return HealthCheck("ram", OK, f"RAM {used_pct:.0f}% used", {"used_pct": used_pct})


def check_gpu_temp(temp_c: float | None, *, warn: float = 84.0, crit: float = 90.0) -> HealthCheck:
    """Sustained thermal throttling collapses fps over a multi-day run; the governor pauses at the
    hardware limit, but a rising trend is an early warning."""
    if temp_c is None:
        return HealthCheck("gpu_temp", UNKNOWN, "no GPU temperature telemetry")
    if temp_c >= crit:
        return HealthCheck("gpu_temp", CRITICAL, f"GPU {temp_c:.0f}C (throttling/limit)", {"temp_c": temp_c})
    if temp_c >= warn:
        return HealthCheck("gpu_temp", WARN, f"GPU {temp_c:.0f}C (warm)", {"temp_c": temp_c})
    return HealthCheck("gpu_temp", OK, f"GPU {temp_c:.0f}C", {"temp_c": temp_c})


def check_silent_hang(mtime_age_s: float | None, *, warn_s: float = 1200.0, crit_s: float = 3600.0,
                      terminal: bool = False) -> HealthCheck:
    """No fresh write in a long time = a silent hang (a wedged CUDA candidate, a deadlock). A terminal
    (done/error) run is intentionally quiet, so it is never 'hung'."""
    if terminal:
        return HealthCheck("silent_hang", OK, "run reached a terminal phase (quiet by design)")
    if mtime_age_s is None:
        return HealthCheck("silent_hang", UNKNOWN, "no progress artifact to age-check")
    if mtime_age_s >= crit_s:
        return HealthCheck("silent_hang", CRITICAL,
                           f"no progress write for {mtime_age_s/60:.0f} min (silent hang)",
                           {"age_s": mtime_age_s})
    if mtime_age_s >= warn_s:
        return HealthCheck("silent_hang", WARN, f"no progress write for {mtime_age_s/60:.0f} min",
                           {"age_s": mtime_age_s})
    return HealthCheck("silent_hang", OK, f"last progress write {mtime_age_s/60:.1f} min ago",
                       {"age_s": mtime_age_s})


def check_gate_failure_rate(n_failed: int, n_attempted: int, *, warn: float = 0.10,
                            crit: float = 0.40) -> HealthCheck:
    """LLM gate/validation failures burn a budget slot; the prototype ran ~1/40 (~2.5%). A rising rate
    is an early sign of a systemic authoring fault (a prompt regression, an API degradation)."""
    if n_attempted <= 0:
        return HealthCheck("gate_failures", INFO, "no candidates attempted yet")
    rate = n_failed / n_attempted
    ev = {"n_failed": n_failed, "n_attempted": n_attempted, "rate": rate}
    if rate >= crit:
        return HealthCheck("gate_failures", CRITICAL,
                           f"{rate:.0%} of candidates failed the gate ({n_failed}/{n_attempted})", ev)
    if rate >= warn:
        return HealthCheck("gate_failures", WARN,
                           f"{rate:.0%} gate-failure rate ({n_failed}/{n_attempted})", ev)
    return HealthCheck("gate_failures", OK, f"{rate:.1%} gate-failure rate", ev)


def check_nan_rate(n_nonfinite: int, n_records: int, *, warn: float = 0.02,
                   crit: float = 0.10) -> HealthCheck:
    """Any non-finite fitness/score in the archive is corruption that would only bite at analysis time —
    the exact 'surfaces at the end' failure the sentinel exists to pre-empt."""
    if n_records <= 0:
        return HealthCheck("nan_rate", INFO, "no records yet")
    rate = n_nonfinite / n_records
    ev = {"n_nonfinite": n_nonfinite, "n_records": n_records, "rate": rate}
    if rate >= crit:
        return HealthCheck("nan_rate", CRITICAL, f"{rate:.0%} of records carry a non-finite score", ev)
    if n_nonfinite > 0 or rate >= warn:
        return HealthCheck("nan_rate", WARN, f"{n_nonfinite}/{n_records} records non-finite", ev)
    return HealthCheck("nan_rate", OK, "all records finite", ev)


def check_divergence_rate(n_diverged_runs: int, n_candidates: int, *, warn: float = 0.05,
                          crit: float = 0.20, winner_diverged: bool = False) -> HealthCheck:
    """Critic-explosion clustering. PopArt makes these rare; a rising diverged-RUN rate flags a
    genuinely mis-scaled reward regime, and a DIVERGED WINNER is critical (a diverged candidate should
    lose selection, so a winner that diverged is a selection-integrity alarm)."""
    if winner_diverged:
        return HealthCheck("divergence", CRITICAL, "a FROZEN WINNER's training diverged (selection integrity)",
                           {"winner_diverged": True})
    if n_candidates <= 0:
        return HealthCheck("divergence", INFO, "no candidates yet")
    rate = n_diverged_runs / n_candidates
    ev = {"n_diverged_runs": n_diverged_runs, "n_candidates": n_candidates, "rate": rate}
    if rate >= crit:
        return HealthCheck("divergence", CRITICAL, f"{rate:.0%} of candidates diverged (critic explosions)", ev)
    if rate >= warn:
        return HealthCheck("divergence", WARN, f"{rate:.0%} divergence rate", ev)
    return HealthCheck("divergence", OK, f"{rate:.1%} divergence rate", ev)


def check_reward_scale_drift(raw_rms_by_arm: dict[str, float], *, ratio_warn: float = 100.0,
                             ratio_crit: float = 1e4) -> HealthCheck:
    """The P5 confound made auditable: the reward SCALE (unclamped PopArt raw_rms) differing wildly
    across arms is a latent scale-driven entropy-regularisation difference that entangles with the
    treatment. A large cross-arm max/min ratio is worth surfacing DURING the run (it re-baselines the
    mechanism story), not at analysis time."""
    vals = {a: float(v) for a, v in raw_rms_by_arm.items() if v is not None and float(v) > 0.0}
    if len(vals) < 2:
        return HealthCheck("reward_scale", INFO, "need >= 2 arms' raw_rms for a drift check",
                           {"n_arms": len(vals)})
    hi, lo = max(vals.values()), min(vals.values())
    ratio = hi / lo if lo > 0 else float("inf")
    ev = {"max": hi, "min": lo, "ratio": ratio, "by_arm": vals}
    if ratio >= ratio_crit:
        return HealthCheck("reward_scale", CRITICAL, f"cross-arm reward-scale ratio {ratio:.0f}x", ev)
    if ratio >= ratio_warn:
        return HealthCheck("reward_scale", WARN, f"cross-arm reward-scale ratio {ratio:.0f}x", ev)
    return HealthCheck("reward_scale", OK, f"cross-arm reward-scale ratio {ratio:.1f}x", ev)


def check_api_error_rate(n_api_errors: int, n_api_calls: int, *, warn: float = 0.05,
                         crit: float = 0.25) -> HealthCheck:
    """A rising LLM API error/refusal rate (rate-limit, outage, a systematically-refused prompt) is an
    early sign the authoring loop is degrading — caught in hours, not at the end."""
    if n_api_calls <= 0:
        return HealthCheck("api_errors", INFO, "no API calls logged yet")
    rate = n_api_errors / n_api_calls
    ev = {"n_errors": n_api_errors, "n_calls": n_api_calls, "rate": rate}
    if rate >= crit:
        return HealthCheck("api_errors", CRITICAL, f"{rate:.0%} API error rate ({n_api_errors}/{n_api_calls})", ev)
    if rate >= warn:
        return HealthCheck("api_errors", WARN, f"{rate:.0%} API error rate", ev)
    return HealthCheck("api_errors", OK, f"{rate:.1%} API error rate", ev)


def check_progress(seen_arms: int, expected_arms: int, *, all_arms_tested: bool | None = None) -> HealthCheck:
    """Coverage: are all pre-registered arms progressing? A completed run whose gate says not-all-tested
    is a husk (the exact-M19 failure class), CRITICAL."""
    if all_arms_tested is False:
        return HealthCheck("coverage", CRITICAL,
                           "campaign summary reports NOT all arms tested (husk/failure)",
                           {"all_arms_tested": False})
    ev = {"seen_arms": seen_arms, "expected_arms": expected_arms}
    if expected_arms > 0 and seen_arms < expected_arms:
        return HealthCheck("coverage", INFO, f"{seen_arms}/{expected_arms} arms have produced records", ev)
    return HealthCheck("coverage", OK, f"{seen_arms}/{max(expected_arms, seen_arms)} arms progressing", ev)


def check_exit_code(exit_code: int | None) -> HealthCheck:
    """A recorded FAILED exit (EXIT_INCOMPLETE=3 etc.) from the last pass is a resumable failure worth
    an alert; 0/None = clean or still running."""
    if exit_code is None or int(exit_code) == 0:
        return HealthCheck("exit_code", OK, "no failing exit recorded", {"exit_code": exit_code})
    return HealthCheck("exit_code", CRITICAL, f"last pass exited {exit_code} (resumable failure)",
                       {"exit_code": int(exit_code)})


def cusum(series: list[float], target: float, *, k: float, h: float,
          direction: str = "up") -> tuple[bool, int, float]:
    """One-sided Page (1954) CUSUM change-point detector: does a streaming metric DRIFT off ``target``?

    A hard threshold only fires once a value crosses it; a CUSUM accumulates small persistent
    deviations and alarms on a sustained SHIFT of size ~``k`` (in the series' units) before any single
    value is extreme — the right tool for "catch anything EARLY". For ``direction='up'`` the statistic
    is ``S_i = max(0, S_{i-1} + (x_i - target - k))`` and it alarms when ``S_i > h`` (``down`` mirrors
    it). ``k`` is the allowable slack (half the shift you want to detect); ``h`` is the decision
    interval. Returns ``(alarmed, first_alarm_index, S_final)``. Pure + total (empty series -> no
    alarm)."""
    s = 0.0
    first = -1
    sign = 1.0 if direction == "up" else -1.0
    for i, x in enumerate(series):
        try:
            xf = float(x)
        except (TypeError, ValueError):
            continue
        s = max(0.0, s + sign * (xf - target) - k)
        if s > h and first < 0:
            first = i
    return (first >= 0, first, s)


def check_metric_drift(name: str, history: list[float], target: float, *, k: float, h: float,
                       min_points: int = 5, direction: str = "up") -> HealthCheck:
    """Statistical-process-control check: a CUSUM drift alarm on a streaming rate/metric.

    Catches a SUSTAINED creep (e.g. the gate-failure or NaN rate slowly rising, or the training fps
    slowly sinking under thermal creep) that the point-in-time threshold checks would only flag once
    it becomes extreme — so a degrading run is seen in hours, not at the end. WARN (not CRITICAL):
    the drift is an EARLY signal to investigate, and the hard-threshold checks above escalate if it
    actually reaches a breach. Needs ``min_points`` samples before it can alarm (a short history is
    not yet evidence of drift). ``direction='down'`` alarms on a sustained FALL below ``target``."""
    hist = [float(x) for x in history if x is not None]
    if len(hist) < int(min_points):
        return HealthCheck(f"{name}_drift", INFO, f"{len(hist)} samples (need {min_points} for a drift check)",
                           {"n": len(hist)})
    alarmed, idx, s = cusum(hist, target, k=k, h=h, direction=direction)
    word = "upward" if direction == "up" else "downward"
    ev = {"n": len(hist), "cusum": round(s, 4), "target": target, "k": k, "h": h,
          "first_alarm_i": idx, "direction": direction}
    if alarmed:
        return HealthCheck(f"{name}_drift", WARN,
                           f"{name} is DRIFTING {word} (CUSUM {s:.2f} > {h}, since sample {idx})", ev)
    return HealthCheck(f"{name}_drift", OK, f"{name} stable (CUSUM {s:.2f} <= {h})", ev)


def check_mirror_freshness(mirror_age_s: float | None, *, warn_s: float = 43200.0) -> HealthCheck:
    """The irreplaceable archive mirror should refresh (~6-hourly). A stale mirror means a C: failure
    would lose recent runs — worth a nudge, not a stop."""
    if mirror_age_s is None:
        return HealthCheck("mirror", INFO, "no archive mirror found (register the 6-hourly task)")
    if mirror_age_s >= warn_s:
        return HealthCheck("mirror", WARN, f"archive mirror is {mirror_age_s/3600:.0f} h stale",
                           {"age_s": mirror_age_s})
    return HealthCheck("mirror", OK, f"archive mirror {mirror_age_s/3600:.1f} h old", {"age_s": mirror_age_s})


def check_completion_stall(
    completion_times: list[float] | None,
    now: float,
    *,
    n_recent_stall_events: int = 0,
    terminal: bool = False,
    factor_warn: float = 3.0,
    factor_crit: float = 8.0,
    floor_s: float = 1800.0,
) -> HealthCheck:
    """Multi-granularity STALL detection (B1, 2026-07-06): is the run still COMPLETING units?

    ``progress.json`` freshness (the silent-hang check) proves the driver process is ALIVE; this
    check proves it is PRODUCTIVE, from the journal's per-unit completion stream (``candidate_done``
    / ``seed_done`` events). The yardstick is the run's OWN measured cadence — the median
    inter-completion gap — so it self-calibrates to any (n_workers, B*) configuration: silence
    longer than ``factor_warn`` x median (min ``floor_s``) is a WARN, ``factor_crit`` x median a
    CRITICAL (a wedged CUDA training with a happily-alive driver — the hang liveness checks cannot
    see). Median (not mean) so one legitimate thermal pause does not inflate the yardstick.

    ``n_recent_stall_events`` counts run_recycling's own ``test_leg_stall`` detections in the recent
    window — the in-driver detector and this outside view corroborate each other (>=1 -> at least
    WARN). Terminal runs are exempt (no units expected); fewer than 3 completions -> INFO (no
    yardstick yet; the mtime hang check covers the early phase)."""
    if terminal:
        return HealthCheck("completion_stall", OK, "run is terminal — no units expected")
    times = sorted(float(t) for t in (completion_times or []))
    if len(times) < 3:
        base = HealthCheck("completion_stall", INFO,
                           f"{len(times)} unit completions journaled (need 3 for a cadence yardstick)",
                           {"n_completions": len(times)})
        if n_recent_stall_events > 0:
            return HealthCheck("completion_stall", WARN,
                               f"run_recycling reported {n_recent_stall_events} stall event(s)",
                               {"n_stall_events": n_recent_stall_events})
        return base
    gaps = sorted(b - a for a, b in zip(times, times[1:]))
    n = len(gaps)
    median = gaps[n // 2] if n % 2 == 1 else 0.5 * (gaps[n // 2 - 1] + gaps[n // 2])
    silence = max(0.0, float(now) - times[-1])
    warn_at = max(floor_s, factor_warn * median)
    crit_at = max(2.0 * floor_s, factor_crit * median)
    ev = {"silence_s": round(silence, 1), "median_gap_s": round(median, 1),
          "warn_at_s": round(warn_at, 1), "crit_at_s": round(crit_at, 1),
          "n_completions": len(times), "n_stall_events": n_recent_stall_events}
    if silence >= crit_at:
        return HealthCheck("completion_stall", CRITICAL,
                           f"NO unit completed for {silence/3600:.1f} h (median cadence "
                           f"{median/60:.0f} min) — a training is wedged", ev)
    if silence >= warn_at or n_recent_stall_events > 0:
        return HealthCheck("completion_stall", WARN,
                           f"quiet for {silence/60:.0f} min vs median cadence {median/60:.0f} min"
                           + (f"; {n_recent_stall_events} in-driver stall event(s)"
                              if n_recent_stall_events else ""), ev)
    return HealthCheck("completion_stall", OK,
                       f"last unit {silence/60:.0f} min ago (median cadence {median/60:.0f} min)", ev)


def check_disk_forecast(
    samples: list[tuple[float, float]] | None,
    *,
    floor_gb: float = 20.0,
    warn_h: float = 48.0,
    crit_h: float = 12.0,
    min_points: int = 5,
) -> HealthCheck:
    """PREDICTIVE disk exhaustion (B3, 2026-07-06): "hits the floor in N hours", not just "low now".

    Least-squares slope over the ``--watch`` history of ``(epoch_s, free_gb)`` samples -> hours until
    the free space crosses the same floor the hard ``disk`` check enforces. A multi-week run fills
    the disk SLOWLY (records + logs + mirror), so the lead time is what turns an eventual CRITICAL
    into a calm, planned cleanup. RAM deliberately gets NO forecast twin: worker RSS oscillates by
    design (pool recycling), so a linear leak model would false-alarm every transition wave."""
    pts = [(float(t), float(g)) for t, g in (samples or [])]
    if len(pts) < int(min_points):
        return HealthCheck("disk_forecast", INFO,
                           f"{len(pts)} disk samples (need {min_points} for a fill-rate forecast)",
                           {"n": len(pts)})
    t0 = pts[0][0]
    xs = [t - t0 for t, _g in pts]
    ys = [g for _t, g in pts]
    n = float(len(pts))
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0.0:
        return HealthCheck("disk_forecast", INFO, "degenerate sample spacing", {"n": len(pts)})
    slope_gb_s = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    slope_gb_h = slope_gb_s * 3600.0
    free_now = ys[-1]
    ev = {"slope_gb_per_h": round(slope_gb_h, 4), "free_gb": round(free_now, 1),
          "floor_gb": floor_gb, "n": len(pts)}
    if slope_gb_h >= -1e-3:
        return HealthCheck("disk_forecast", OK,
                           f"disk not shrinking ({slope_gb_h:+.2f} GB/h)", ev)
    hours_to_floor = max(0.0, (free_now - floor_gb) / (-slope_gb_h))
    ev["hours_to_floor"] = round(hours_to_floor, 1)
    if hours_to_floor <= crit_h:
        return HealthCheck("disk_forecast", CRITICAL,
                           f"disk hits the {floor_gb:.0f} GB floor in ~{hours_to_floor:.0f} h "
                           f"at {slope_gb_h:+.2f} GB/h", ev)
    if hours_to_floor <= warn_h:
        return HealthCheck("disk_forecast", WARN,
                           f"disk hits the {floor_gb:.0f} GB floor in ~{hours_to_floor:.0f} h "
                           f"at {slope_gb_h:+.2f} GB/h", ev)
    return HealthCheck("disk_forecast", OK,
                       f"~{hours_to_floor:.0f} h of headroom at {slope_gb_h:+.2f} GB/h", ev)


def check_unit_coverage(
    done_units: int | None,
    expected_units: int | None,
    stage: str,
    *,
    claimed_complete: bool = False,
    rate_per_h: float | None = None,
) -> HealthCheck:
    """Expected-vs-done UNIT ledger (B4, 2026-07-06) — the anti-husk guarantee at unit granularity.

    The frozen design fixes exactly how many units each stage must produce (arms x candidates for
    SEARCH; (arms + baselines) x seeds for TEST). Three verdicts:

    * ``claimed_complete`` (the summary says the stage is done) with ``done < expected`` -> CRITICAL:
      a silent SHORTFALL — units are missing yet the run claims completeness (the husk class the
      boolean-level M19 check cannot see at this granularity).
    * ``done > expected`` -> WARN: duplicate ids or a config/roster drift — never healthy.
    * otherwise OK/INFO progress, with a data-driven ETA in the evidence when a completion rate is
      available."""
    if done_units is None or expected_units is None or expected_units <= 0:
        return HealthCheck(f"coverage_{stage}", INFO, f"{stage}: expected-unit ledger unavailable")
    ev: dict[str, Any] = {"done": int(done_units), "expected": int(expected_units),
                          "claimed_complete": bool(claimed_complete)}
    if rate_per_h is not None and rate_per_h > 0 and done_units < expected_units:
        ev["eta_h"] = round((expected_units - done_units) / rate_per_h, 1)
    if claimed_complete and done_units < expected_units:
        return HealthCheck(f"coverage_{stage}", CRITICAL,
                           f"{stage} claims complete but {done_units}/{expected_units} units on disk "
                           "(silent shortfall)", ev)
    if done_units > expected_units:
        return HealthCheck(f"coverage_{stage}", WARN,
                           f"{stage} has {done_units} units for {expected_units} expected "
                           "(duplicates or config drift)", ev)
    pct = 100.0 * done_units / expected_units
    eta = f", ETA ~{ev['eta_h']:.0f} h" if "eta_h" in ev else ""
    sev = OK if done_units == expected_units else INFO
    return HealthCheck(f"coverage_{stage}", sev, f"{stage}: {done_units}/{expected_units} ({pct:.0f}%){eta}", ev)


def check_error_taxonomy(
    taxonomy: dict[str, dict[str, Any]] | None,
    *,
    kind_warn: int = 10,
    total_warn: int = 25,
) -> HealthCheck:
    """The clustered error/triage panel (B5, 2026-07-06): errors BY KIND with counts + affected arms.

    The hard checks alarm on specific rates; this one alarms on VOLUME — any single failure kind
    reaching ``kind_warn`` occurrences (a systematic fault, e.g. an OOM cascade or an API refusal
    wave), or ``total_warn`` failures overall. Otherwise it surfaces the taxonomy as evidence so the
    triage protocol (runbook §5b) starts from data, not from grepping logs."""
    tax = taxonomy or {}
    if not tax:
        return HealthCheck("error_taxonomy", OK, "no failures/warnings journaled")
    counts = {k: int(v.get("count", 0)) for k, v in tax.items()}
    total = sum(counts.values())
    worst_kind = max(counts, key=lambda k: counts[k])
    ev: dict[str, Any] = {"counts": counts, "total": total,
                          "arms": {k: v.get("arms", []) for k, v in tax.items()}}
    if counts[worst_kind] >= kind_warn or total >= total_warn:
        return HealthCheck("error_taxonomy", WARN,
                           f"{total} failure events — dominant kind '{worst_kind}' x{counts[worst_kind]}",
                           ev)
    summary = ", ".join(f"{k} x{v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1]))
    return HealthCheck("error_taxonomy", INFO, f"{total} failure event(s): {summary}", ev)


# --------------------------------------------------------------------------- #
# Aggregation                                                                 #
# --------------------------------------------------------------------------- #
def evaluate_health(inputs: dict[str, Any]) -> HealthReport:
    """Run every invariant check over a parsed-inputs dict (see :func:`gather_inputs`). Pure."""
    g = inputs.get
    checks = [
        check_exit_code(g("exit_code")),
        check_progress(int(g("seen_arms", 0) or 0), int(g("expected_arms", 0) or 0),
                       all_arms_tested=g("all_arms_tested")),
        check_disk(g("disk_free_gb")),
        check_ram(g("ram_used_pct")),
        check_gpu_temp(g("gpu_temp_c")),
        check_silent_hang(g("progress_age_s"), terminal=bool(g("terminal", False))),
        check_gate_failure_rate(int(g("n_failed", 0) or 0), int(g("n_attempted", 0) or 0)),
        check_nan_rate(int(g("n_nonfinite", 0) or 0), int(g("n_records", 0) or 0)),
        check_divergence_rate(int(g("n_diverged_runs", 0) or 0), int(g("n_candidates", 0) or 0),
                              winner_diverged=bool(g("winner_diverged", False))),
        check_reward_scale_drift(g("raw_rms_by_arm", {}) or {}),
        check_api_error_rate(int(g("n_api_errors", 0) or 0), int(g("n_api_calls", 0) or 0)),
        check_mirror_freshness(g("mirror_age_s")),
        # 2026-07-06 deep-monitoring layer (B1/B4/B5): productivity, unit-coverage, triage.
        check_completion_stall(
            g("completion_times"), float(g("now", time.time()) or time.time()),
            n_recent_stall_events=int(g("n_recent_stall_events", 0) or 0),
            terminal=bool(g("terminal", False)),
        ),
        check_unit_coverage(g("done_search_units"), g("expected_search_units"), "search",
                            claimed_complete=bool(g("search_claimed_complete", False)),
                            rate_per_h=g("completion_rate_per_h")),
        check_unit_coverage(g("done_test_units"), g("expected_test_units"), "test",
                            claimed_complete=bool(g("all_arms_tested") is True),
                            rate_per_h=g("completion_rate_per_h")),
        check_error_taxonomy(g("error_taxonomy")),
    ]
    # Statistical-process-control drift checks (opt-in: the --watch loop accumulates a per-tick history
    # and passes it in). Target 0 with slack k = half the shift we care about; h the decision interval.
    if g("gate_failure_history") is not None:
        checks.append(check_metric_drift("gate_failure", g("gate_failure_history"), 0.0, k=0.03, h=0.15))
    if g("nan_rate_history") is not None:
        checks.append(check_metric_drift("nan_rate", g("nan_rate_history"), 0.0, k=0.01, h=0.05))
    # Training-throughput drift (B2): a sustained fps FALL across candidates = thermal creep /
    # swap / fragmentation degrading the whole run. fps IS comparable across candidates (same net,
    # same hardware), unlike critic loss — whose scale is per-candidate, so its cross-candidate
    # CUSUM would mix distributions and false-alarm (the per-candidate explosion detection in the
    # monitor + the divergence/NaN-rate checks above own that axis). Target/k/h are supplied by the
    # --watch loop from the run's OWN early-baseline median (self-calibrating).
    if g("fps_history") is not None and g("fps_target") is not None:
        t = float(g("fps_target"))
        checks.append(check_metric_drift("fps", g("fps_history"), t,
                                         k=0.05 * t, h=0.30 * t, direction="down"))
    # Predictive exhaustion (B3): fed by the --watch loop's accumulated (epoch_s, free_gb) samples.
    if g("disk_history") is not None:
        checks.append(check_disk_forecast(g("disk_history")))
    return HealthReport(checks)


# --------------------------------------------------------------------------- #
# Disk/telemetry gatherer (best-effort; each probe guarded)                   #
# --------------------------------------------------------------------------- #
def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass
    return out


def _cluster_diverged_runs(anomaly_lines: list[dict[str, Any]]) -> int:
    """Count DISTINCT diverged runs from anomalies.jsonl (append-only; the LINE count over-states it).

    Mirrors ``analyze_campaign.divergence_report``: a critic_explosion line belongs to a NEW run when
    its step goes BACKWARDS vs the previous explosion (a step reset = a fresh training). Report-only
    heuristic — good enough for a live rate alarm."""
    explosions = [a for a in anomaly_lines if str(a.get("kind", a.get("event", ""))).startswith("critic")]
    if not explosions:
        return 0
    runs = 1
    prev_step = -1
    for a in explosions:
        step = int(a.get("step", a.get("fields", {}).get("step", 0)) or 0)
        if step < prev_step:
            runs += 1
        prev_step = step
    return runs


def gather_inputs(run_dir: Path) -> dict[str, Any]:
    """Read the on-disk campaign artifacts + system telemetry into the :func:`evaluate_health` dict.

    READ-ONLY and best-effort: every probe is guarded so one failure degrades a single check to
    ``UNKNOWN`` (via a missing key) rather than killing the sentinel. ``run_dir`` is the campaign
    output dir (the sentinel checks both it and ``run_dir/search`` for progress.json / summary)."""
    run_dir = Path(run_dir)
    out: dict[str, Any] = {}

    # System telemetry.
    try:
        import shutil as _sh
        out["disk_free_gb"] = _sh.disk_usage(str(run_dir if run_dir.exists() else Path.cwd())).free / 1e9
    except OSError:
        pass
    try:
        import psutil  # type: ignore
        out["ram_used_pct"] = float(psutil.virtual_memory().percent)
    except Exception:  # noqa: BLE001 — psutil absent or probe failed
        pass
    try:
        import pynvml  # type: ignore
        pynvml.nvmlInit()
        h = pynvml.nvmlDeviceGetHandleByIndex(0)
        out["gpu_temp_c"] = float(pynvml.nvmlDeviceGetTemperature(h, pynvml.NVML_TEMPERATURE_GPU))
        pynvml.nvmlShutdown()
    except Exception:  # noqa: BLE001 — no GPU telemetry available
        pass

    # Progress freshness + terminal state.
    prog = None
    for p in (run_dir / "search" / "progress.json", run_dir / "progress.json"):
        if p.is_file():
            prog = p
            break
    if prog is not None:
        try:
            out["progress_age_s"] = max(0.0, time.time() - prog.stat().st_mtime)
        except OSError:
            pass
        try:
            state = json.loads(prog.read_text(encoding="utf-8"))
            out["terminal"] = state.get("phase") in ("done", "error")
            # Live training throughput (B2): the current fps sample for the cross-candidate
            # thermal-creep drift check (the --watch loop accumulates the history).
            fps = (state.get("training") or {}).get("fps")
            if fps is not None:
                out["fps_now"] = float(fps)
        except (OSError, ValueError, TypeError):
            pass

    # Campaign summary (exit code + coverage).
    for p in (run_dir / "campaign_summary.json", run_dir.parent / "campaign_summary.json"):
        if p.is_file():
            try:
                summary = json.loads(p.read_text(encoding="utf-8"))
                out["exit_code"] = summary.get("exit_code", 0)
                out["all_arms_tested"] = summary.get("all_arms_tested")
                arms = summary.get("arms") or summary.get("summaries") or []
                out["seen_arms"] = len({a.get("arm") for a in arms if isinstance(a, dict)})
            except (OSError, ValueError):
                pass
            break

    # Anomalies -> divergence clustering.
    anomalies = _read_jsonl(run_dir / "anomalies.jsonl")
    if not anomalies:
        anomalies = _read_jsonl(run_dir / "search" / "anomalies.jsonl")
    out["n_diverged_runs"] = _cluster_diverged_runs(anomalies)

    # Events -> API error + gate-failure rate (best-effort tallies over the structured log).
    events = _read_jsonl(run_dir / "events.jsonl")
    if events:
        kinds = Counter(str(e.get("event", "")) for e in events)
        out["n_api_calls"] = sum(v for k, v in kinds.items() if "llm_call" in k or "api" in k)
        out["n_api_errors"] = sum(v for k, v in kinds.items() if "error" in k or "refus" in k or "degrad" in k)

    # Failures ledger (gate failures + attempted count).
    failures = _read_jsonl(run_dir / "failures.jsonl") or _read_jsonl(run_dir / "search" / "failures.jsonl")
    if failures:
        out["n_failed"] = len(failures)

    # 2026-07-06 deep-monitoring inputs: the journal's per-unit completion stream (B1), the
    # expected-vs-done unit ledger (B4), and the error taxonomy (B5). All guarded — an absent/
    # unreadable source degrades those checks to INFO, never kills the sentinel. The watcher often
    # points at <campaign>/search (the progress.json home); the archive/journal ledgers live at the
    # campaign ROOT, so resolve it for these probes.
    out["now"] = time.time()
    camp_root = run_dir.parent if run_dir.name == "search" else run_dir
    try:
        import sys as _sys

        _root = Path(__file__).resolve().parents[1]
        if str(_root) not in _sys.path:
            _sys.path.insert(0, str(_root))
        from src.utils.journal import completions as _completions
        from src.utils.journal import error_taxonomy as _taxonomy
        from src.utils.journal import parse_ts as _parse_ts
        from src.utils.journal import read_events as _read_events

        evs = _read_events(run_dir / "events.jsonl") or _read_events(camp_root / "events.jsonl")
        if evs:
            comp = _completions(evs)
            out["completion_times"] = [t for t, _e in comp]
            out["error_taxonomy"] = _taxonomy(evs)
            _now = float(out["now"])
            n_stall = 0
            for e in evs:
                if e.get("event") != "test_leg_stall":
                    continue
                t = _parse_ts(e)
                if t is not None and _now - t <= 7200.0:
                    n_stall += 1
            out["n_recent_stall_events"] = n_stall
            recent = [t for t in out["completion_times"] if _now - t <= 6 * 3600.0]
            if len(recent) >= 2:
                out["completion_rate_per_h"] = len(recent) / 6.0
    except Exception:  # noqa: BLE001 — journal read is best-effort
        pass

    # Expected units come from config (the frozen source of truth); done units from the archive.
    # NB when the per-arm adaptive seed schema lands (seed ratification), the expected-test formula
    # must switch to summing each arm's own seed count.
    try:
        from src.utils.config import load_config

        camp = load_config("campaign")
        arms = list(camp.get("arms") or [])
        cpa = int(camp.get("candidates_per_arm") or 0)
        seeds = list(camp.get("seeds") or [])
        baselines = list(camp.get("h1_baselines") or [])
        if arms and cpa:
            out["expected_search_units"] = len(arms) * cpa
        if arms and seeds:
            out["expected_test_units"] = (len(arms) + len(baselines)) * len(seeds)
    except Exception:  # noqa: BLE001 — config unavailable -> the coverage checks degrade to INFO
        pass
    for key, sub in (("done_search_units", "search"), ("done_test_units", "test")):
        d = camp_root / sub
        if d.is_dir():
            try:
                out[key] = sum(1 for _ in d.rglob("record.json"))
            except OSError:
                pass
        elif camp_root.is_dir():
            # The campaign root exists but this stage hasn't produced its subtree yet: truthfully
            # ZERO done (renders "0/210 (0%)"), vs a mis-pointed run_dir which stays unavailable.
            out[key] = 0
    out["search_claimed_complete"] = out.get("all_arms_tested") is True

    return out


# --------------------------------------------------------------------------- #
# Rendering + CLI                                                             #
# --------------------------------------------------------------------------- #
_ICON = {OK: "OK  ", INFO: "info", WARN: "WARN", CRITICAL: "CRIT", UNKNOWN: "??  "}


def render_report(report: HealthReport) -> str:
    lines = [f"CAMPAIGN SENTINEL — {report.severity} ({'HEALTHY' if report.healthy else 'ATTENTION'})"]
    for c in sorted(report.checks, key=lambda x: -_RANK.get(x.severity, 0)):
        lines.append(f"  [{_ICON.get(c.severity, '?')}] {c.name:<14} {c.detail}")
    return "\n".join(lines)


def _emit_transitions(report: HealthReport, last: dict[str, str]) -> None:
    """Structured-log every check whose severity CHANGED since the last tick (precise health history)."""
    try:
        from src.utils.logging import get_logger, log_event
        import logging as _lg

        logger = get_logger("sentinel")
        level = {OK: _lg.INFO, INFO: _lg.INFO, WARN: _lg.WARNING, CRITICAL: _lg.ERROR, UNKNOWN: _lg.WARNING}
        for c in report.checks:
            if last.get(c.name) != c.severity:
                log_event(logger, "sentinel_check", level=level.get(c.severity, _lg.INFO),
                          check=c.name, severity=c.severity, detail=c.detail, **c.evidence)
                last[c.name] = c.severity
    except Exception:  # noqa: BLE001 — logging must never break the sentinel
        for c in report.checks:
            last[c.name] = c.severity


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Campaign health sentinel (read-only invariant monitor).")
    ap.add_argument("run_dir", help="Campaign output dir (e.g. outputs/campaign).")
    ap.add_argument("--watch", action="store_true", help="Poll on an interval instead of a single check.")
    ap.add_argument("--interval", type=float, default=120.0, help="Seconds between polls in --watch.")
    ap.add_argument("--json", action="store_true", help="Emit the report as JSON (one object per tick).")
    args = ap.parse_args(argv)
    run_dir = Path(args.run_dir)
    last: dict[str, str] = {}
    # Streaming histories for the CUSUM drift checks (accumulate across --watch ticks).
    gate_hist: list[float] = []
    nan_hist: list[float] = []
    # (epoch_s, free_gb) samples for the predictive disk-exhaustion forecast (B3).
    disk_hist: list[tuple[float, float]] = []
    # fps samples for the cross-candidate throughput drift (B2; thermal creep / swap).
    fps_hist: list[float] = []

    def _tick() -> HealthReport:
        inputs = gather_inputs(run_dir)
        na, nc = int(inputs.get("n_failed", 0) or 0), int(inputs.get("n_attempted", 0) or 0)
        if nc > 0:
            gate_hist.append(na / nc)
            inputs["gate_failure_history"] = list(gate_hist)
        nf, nr = int(inputs.get("n_nonfinite", 0) or 0), int(inputs.get("n_records", 0) or 0)
        if nr > 0:
            nan_hist.append(nf / nr)
            inputs["nan_rate_history"] = list(nan_hist)
        if inputs.get("disk_free_gb") is not None:
            disk_hist.append((float(inputs.get("now") or time.time()), float(inputs["disk_free_gb"])))
            del disk_hist[:-720]  # keep ~24 h of samples at the default 2-min tick
            inputs["disk_history"] = list(disk_hist)
        if inputs.get("fps_now") is not None:
            fps_hist.append(float(inputs["fps_now"]))
            del fps_hist[:-720]
            # Self-calibrating baseline: the median of the run's own FIRST 10 samples. Only armed
            # once that baseline exists — a drift check against a half-formed target is noise.
            if len(fps_hist) >= 10:
                base = sorted(fps_hist[:10])
                inputs["fps_target"] = 0.5 * (base[4] + base[5])
                inputs["fps_history"] = list(fps_hist)
        report = evaluate_health(inputs)
        _emit_transitions(report, last)
        print(json.dumps(report.as_dict()) if args.json else render_report(report), flush=True)
        return report

    if not args.watch:
        report = _tick()
        return 1 if report.severity == CRITICAL else 0
    try:
        while True:
            _tick()
            time.sleep(max(5.0, float(args.interval)))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
