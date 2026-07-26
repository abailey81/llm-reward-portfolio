"""CAMPAIGN-LANE HEALTH — the five failure modes the existing sentinel cannot see.

``scripts/sentinel.py`` already covers the MACHINE and the RUN well (disk, RAM, silent hang, gate
failure rate, NaN/divergence rates, reward-scale drift, API errors, driver lease, queue health,
completion stall). What it has no visibility into is the thing that actually decides whether the
2026-07-26 CPU-lane campaign succeeds: **are we holding the capacity we assumed, is the critical
path advancing, and is the substrate staying homogeneous?**

Each function is PURE (no disk, no ssh) so it is unit-testable, and each returns the sentinel's own
``HealthCheck`` vocabulary so these compose into the existing report and alerting rather than
forming a second, parallel monitor.

THE FIVE, and why each earns its place — every one is a failure that would otherwise be SILENT:

1. :func:`check_capacity_accumulation` — the campaign plan's one UNMEASURED assumption is that
   ~8.5 h tasks ACCUMULATE to far more than the 636 cores measured with 20-min probes. If instead
   concurrency plateaus low, the reachable seed rung falls and we must know on DAY ONE, not at the
   Aug-27 stop. Compares the observed curve to the forecast and says which.
2. :func:`check_chain_progress` — the makespan is ``max(throughput, longest serial chain)``. The
   `bayes_opt` (25 serial) and TPE (20 serial) chains FLOOR the campaign, so a stalled chain wastes
   the whole run even while thousands of test-leg trainings stream in and every other indicator
   looks green. Nothing else watches the critical path.
3. :func:`check_host_failure_concentration` — a SINGLE bad node silently eats tasks. We measured
   this for real: ``node-d00a-230`` had no apptainer and returned rc=127 on every task routed to
   it. A global failure RATE hides it; concentration by host exposes it.
4. :func:`check_rung_forecast` — re-forecasts the reachable rung from the OBSERVED completion rate
   instead of the model, so the exogenous Aug-27 stop is planned against reality.
5. :func:`check_determinism_homogeneity` — CPU/CUDA and 1-thread/8-thread are not bit-identical,
   and every paired contrast depends on CRN pairing. The env fingerprint now records device and
   thread regime; this makes a mix visible DURING the run rather than at the post-hoc S6 audit,
   when it would be too late to re-run.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

# Reuse the sentinel's vocabulary rather than inventing a second one. Imported as `scripts.sentinel`
# (a PEP-420 namespace package from the repo root, exactly as tests/test_sentinel.py does) and NOT via
# a sys.path hack: `import sentinel` would bind a SECOND module object whose `HealthCheck` is a
# different class, so isinstance would fail and the two report vocabularies would silently diverge.
from scripts.sentinel import CRITICAL, INFO, OK, WARN, HealthCheck

__all__ = [
    "check_capacity_accumulation",
    "check_chain_progress",
    "check_host_failure_concentration",
    "check_rung_forecast",
    "check_determinism_homogeneity",
]


def check_capacity_accumulation(report: dict[str, Any], *, expected_cores: int,
                                hours_in: float) -> HealthCheck:
    """Is concurrency climbing toward the forecast, or stuck at the probe-measured floor?

    ``report`` is :func:`src.cluster.telemetry.accumulation_report` output. The grace period matters:
    accumulation is EXPECTED to take ~2-3 h (dispatch ~3.3 jobs/min against ~8.5 h jobs), so a low
    reading in the first hours is normal and must not cry wolf — but a plateau far below forecast
    AFTER that window is a real, plan-changing finding.
    """
    status = report.get("status")
    if status in ("no-data", "insufficient"):
        return HealthCheck("capacity_accumulation", INFO,
                           f"not yet measurable ({status}) — keep the telemetry watcher running",
                           {"report": report})
    late = float(report.get("late_mean_cores") or 0)
    if expected_cores <= 0:
        # No DECLARED forecast to hold ourselves to (GO never wrote one). Report the measurement and
        # stop: judging a plateau against a zero forecast would fire a WARN on every healthy run.
        return HealthCheck("capacity_accumulation", INFO,
                           f"holding ~{late:.0f} cores ({status}); no forecast recorded in "
                           "allocation_state (lane_expected_cores) to compare against",
                           {"report": report})
    frac = late / expected_cores

    if status == "climbing":
        return HealthCheck("capacity_accumulation", OK,
                           f"still ACCUMULATING ({late:.0f} cores and rising) — do NOT re-forecast "
                           "the rung yet", {"report": report, "frac_of_forecast": round(frac, 2)})
    if status == "declining":
        return HealthCheck("capacity_accumulation", WARN,
                           f"concurrency DECLINING to ~{late:.0f} cores — check for a kill event, a "
                           "drained queue, or a cluster-wide load spike",
                           {"report": report, "frac_of_forecast": round(frac, 2)})
    # plateaued
    if hours_in < 3.0:
        return HealthCheck("capacity_accumulation", INFO,
                           f"plateaued at ~{late:.0f} cores but only {hours_in:.1f} h in — "
                           "accumulation needs ~2-3 h; too early to conclude",
                           {"report": report, "frac_of_forecast": round(frac, 2)})
    if frac < 0.5:
        return HealthCheck("capacity_accumulation", WARN,
                           f"plateaued at ~{late:.0f} cores = {frac:.0%} of the {expected_cores} "
                           "forecast — RE-FORECAST the reachable rung from this number and plan "
                           "against it (the forecast was a model, this is the measurement)",
                           {"report": report, "frac_of_forecast": round(frac, 2)})
    return HealthCheck("capacity_accumulation", OK,
                       f"plateaued at ~{late:.0f} cores ({frac:.0%} of forecast) — steady state",
                       {"report": report, "frac_of_forecast": round(frac, 2)})


def check_chain_progress(chains: dict[str, dict[str, Any]], *,
                         stall_warn_h: float = 14.0,
                         stall_crit_h: float = 28.0) -> HealthCheck:
    """The CRITICAL PATH: are the serial search chains advancing?

    ``chains`` maps arm -> ``{"completed": int, "total": int, "hours_since_last": float}``.

    Thresholds are anchored on the measured step cost, not guessed: one chain step is ~8.5 h at
    1 thread and ~3.1 h at the ratified 8 threads, so ~14 h without progress is already several
    missed steps (WARN) and ~28 h is unambiguously stuck (CRITICAL). A stalled chain is the
    campaign's worst silent failure: the test flood keeps streaming, every other indicator stays
    green, and the makespan floor quietly slips a day for every day the chain sits still.
    """
    if not chains:
        return HealthCheck("chain_progress", INFO, "no serial chains reported yet", {})
    stalled, done, worst_h = [], [], 0.0
    for arm, st in chains.items():
        completed, total = int(st.get("completed", 0)), int(st.get("total", 0))
        idle = float(st.get("hours_since_last") or 0.0)
        if total and completed >= total:
            done.append(arm)
            continue
        worst_h = max(worst_h, idle)
        if idle >= stall_warn_h:
            stalled.append(f"{arm} {completed}/{total} idle {idle:.1f}h")
    if not stalled:
        prog = ", ".join(f"{a} {s.get('completed')}/{s.get('total')}" for a, s in chains.items())
        return HealthCheck("chain_progress", OK, f"critical path advancing ({prog})",
                           {"chains": chains, "complete": done})
    sev = CRITICAL if worst_h >= stall_crit_h else WARN
    return HealthCheck("chain_progress", sev,
                       "CRITICAL-PATH CHAIN STALLED: " + "; ".join(stalled) +
                       " — the makespan floor slips a day for every day this sits still; check the "
                       "chain job, not the test flood",
                       {"chains": chains, "stalled": stalled, "max_idle_h": worst_h})


def check_host_failure_concentration(failures_by_host: dict[str, int],
                                     attempts_by_host: dict[str, int], *,
                                     min_attempts: int = 5,
                                     bad_host_rate: float = 0.5) -> HealthCheck:
    """Is ONE node eating tasks? (measured for real: node-d00a-230 had no apptainer -> rc=127)

    A global failure rate hides this completely: 40 dead tasks on one bad host among 4,000 good
    ones is a 1% rate that every aggregate check passes, while that host keeps accepting and
    killing work for the rest of the run. Concentration is the signal, not volume.
    """
    if not attempts_by_host:
        return HealthCheck("host_failure_concentration", INFO, "no per-host attempts recorded", {})
    bad = {}
    for host, att in attempts_by_host.items():
        if att < min_attempts:
            continue
        rate = failures_by_host.get(host, 0) / att
        if rate >= bad_host_rate:
            bad[host] = {"failed": failures_by_host.get(host, 0), "attempts": att,
                         "rate": round(rate, 2)}
    if not bad:
        tot_f, tot_a = sum(failures_by_host.values()), sum(attempts_by_host.values())
        return HealthCheck("host_failure_concentration", OK,
                           f"no bad node ({tot_f}/{tot_a} failures spread across "
                           f"{len(attempts_by_host)} hosts)",
                           {"n_hosts": len(attempts_by_host)})
    return HealthCheck("host_failure_concentration", WARN,
                       f"{len(bad)} node(s) failing >= {bad_host_rate:.0%} of their tasks: "
                       + ", ".join(f"{h} ({v['failed']}/{v['attempts']})" for h, v in bad.items())
                       + " — exclude them (`-l h=!<host>`) or the run keeps feeding them work",
                       {"bad_hosts": bad})


def check_rung_forecast(*, completed_trainings: int, elapsed_hours: float,
                        hours_remaining: float, rung_targets: dict[int, int]) -> HealthCheck:
    """Which seed rung do we actually reach by the exogenous stop, at the OBSERVED rate?

    The stop is exogenous (calendar, never the effect), so this is a planning readout, not a
    decision rule — but planning against a stale model instead of the live rate is how a campaign
    discovers on the last day that it banked a lower rung than the write-up assumed.
    """
    if elapsed_hours <= 0 or completed_trainings <= 0:
        return HealthCheck("rung_forecast", INFO, "no completions yet", {})
    rate = completed_trainings / elapsed_hours
    projected = completed_trainings + rate * hours_remaining
    reachable = [n for n, need in sorted(rung_targets.items()) if need <= projected]
    top = max(reachable) if reachable else 0
    nxt = min((n for n in sorted(rung_targets) if n > top), default=None)
    detail = (f"{completed_trainings:,} done at {rate:.1f}/h -> ~{projected:,.0f} by the stop "
              f"=> rung {top}")
    if nxt is not None:
        short = rung_targets[nxt] - projected
        detail += f" (next rung {nxt} needs {short:,.0f} more)"
    sev = OK if top >= max(rung_targets, default=0) else INFO
    return HealthCheck("rung_forecast", sev, detail,
                       {"rate_per_hour": round(rate, 2), "projected": round(projected),
                        "reachable_rung": top, "next_rung": nxt})


def check_determinism_homogeneity(env_label_census: dict[str, int], *,
                                  scope: str = "test leg") -> HealthCheck:
    """Are all SCORED trainings on one substrate? CPU/CUDA and 1/8-thread are NOT bit-identical.

    Takes the census produced by :func:`src.cluster.integrity.env_label_census` (``{label: count}``)
    — the SAME normalisation the post-hoc S6 gate uses, so the live verdict and the gate verdict can
    never disagree.

    Every paired contrast rests on CRN pairing, so a device or thread-regime MIX inside the scored
    leg silently confounds the arm effect with a substrate effect. The env fingerprint now carries
    both (``|dev=`` from ``run_one``; ``OMP_NUM_THREADS`` + ``torch.get_num_threads()`` from
    ``capture_env``), which makes this checkable DURING the run — the post-hoc S6 audit finds it far
    too late to re-run anything. CRITICAL, not WARN: this is a validity failure, not a slowdown.
    """
    counts = Counter({str(k): int(v) for k, v in (env_label_census or {}).items() if int(v) > 0})
    total = sum(counts.values())
    if not total:
        return HealthCheck("determinism_homogeneity", INFO, "no env fingerprints yet", {})
    if len(counts) == 1:
        return HealthCheck("determinism_homogeneity", OK,
                           f"{scope} homogeneous across {total} records "
                           f"({next(iter(counts))})", {"n_records": total})
    capture_failed = [c for c in counts if c.startswith("capture-failed")]
    top = counts.most_common()
    return HealthCheck("determinism_homogeneity", CRITICAL,
                       f"{scope} is NOT substrate-homogeneous: {len(counts)} distinct environments "
                       + ", ".join(f"{lbl}x{n}" for lbl, n in top[:4])
                       + " — CPU/CUDA and 1/8-thread are not bit-identical, so a mix confounds "
                       "every paired contrast. Quarantine the minority substrate and re-run it."
                       + (f" ({len(capture_failed)} label(s) are capture FAILURES, not a real mix)"
                          if capture_failed else ""),
                       {"distinct": len(counts), "counts": dict(top[:8])})
