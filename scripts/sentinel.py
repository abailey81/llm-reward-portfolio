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
                       min_points: int = 5) -> HealthCheck:
    """Statistical-process-control check: a CUSUM upward-drift alarm on a streaming rate/metric.

    Catches a SUSTAINED creep (e.g. the gate-failure or NaN rate slowly rising) that the point-in-time
    threshold checks would only flag once it becomes extreme — so a degrading authoring loop is seen in
    hours, not at the end. WARN (not CRITICAL): the drift is an EARLY signal to investigate, and the
    hard-threshold checks above escalate if it actually reaches a breach. Needs ``min_points`` samples
    before it can alarm (a short history is not yet evidence of drift)."""
    hist = [float(x) for x in history if x is not None]
    if len(hist) < int(min_points):
        return HealthCheck(f"{name}_drift", INFO, f"{len(hist)} samples (need {min_points} for a drift check)",
                           {"n": len(hist)})
    alarmed, idx, s = cusum(hist, target, k=k, h=h, direction="up")
    ev = {"n": len(hist), "cusum": round(s, 4), "target": target, "k": k, "h": h, "first_alarm_i": idx}
    if alarmed:
        return HealthCheck(f"{name}_drift", WARN,
                           f"{name} is DRIFTING upward (CUSUM {s:.2f} > {h}, since sample {idx})", ev)
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
    ]
    # Statistical-process-control drift checks (opt-in: the --watch loop accumulates a per-tick history
    # and passes it in). Target 0 with slack k = half the shift we care about; h the decision interval.
    if g("gate_failure_history") is not None:
        checks.append(check_metric_drift("gate_failure", g("gate_failure_history"), 0.0, k=0.03, h=0.15))
    if g("nan_rate_history") is not None:
        checks.append(check_metric_drift("nan_rate", g("nan_rate_history"), 0.0, k=0.01, h=0.05))
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
        st = _read_jsonl(prog) if prog.suffix == ".jsonl" else None
        try:
            phase = json.loads(prog.read_text(encoding="utf-8")).get("phase") if st is None else None
            out["terminal"] = phase in ("done", "error")
        except (OSError, ValueError):
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
