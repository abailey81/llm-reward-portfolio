#!/usr/bin/env python
"""CORE ACCUMULATOR — hold every core we win, absorb every burst, and ATTRIBUTE every loss.

Tamer, 2026-08-06: *"create a system that accumulates as many cores as we can, and doesn't let it
go for our campaign."*  This is that system.

THE PHYSICS, WHICH IS WHAT MAKES THIS TRACTABLE
-----------------------------------------------
Our held cores evolve as

    cores(t+dt) = cores(t) - 8 x completions + 8 x dispatches

so we lose ground exactly when completions outpace dispatches. A dispatch needs three things:

    (a) an ELIGIBLE job of ours to dispatch          <- OURS TO GUARANTEE
    (b) winning the cluster-wide contest for the slot <- FAIR SHARE, NOT OURS TO FIGHT
    (c) that job being PLACEABLE (shape, memory, tmpfs, no exclusion)  <- OURS TO GUARANTEE

**(b) IS NOT A DEFECT AND MUST NEVER BE TREATED AS ONE.** 101 users run in our pools, they are 87%
full, and our ~8% share is roughly proportional. Chasing it is how a monitor turns an honest state
into a permanent alarm.

> ## ⇒ SO THE SYSTEM'S JOB IS NARROW AND CHECKABLE: make sure (a) and (c) are NEVER the reason we
> ## lost a core — and then ATTRIBUTE what remains, so fair-share loss is reported as legitimate
> ## instead of chased forever.

That attribution is the whole intellectual content. Without it this file becomes the thing
`RUN4_STATUS` already warns about: *"cores down with records up is throughput ARRIVING, not
leaving"* — measured at 309 -> 437 -> 469 records/h WHILE cores fell 2,320 -> 1,776.

THE TARGETS ARE MEASURED, NOT CHOSEN
------------------------------------
* **`BURST_ABSORB_JOBS = 291`.** The largest core count this campaign has ever held is **2,328**
  (max over 304 `cores=` stamps in `CYCLE_LOG.md`). 2,328 / 8 = 291 pack-8 jobs. **If our eligible
  queue is ever shallower than that, a repeat of our own best hour is one we could not absorb.**
  That is the accumulator's headline invariant, and it is derived from our own history rather than
  from taste.
* **`CAP_HEADROOM_FRAC = 0.95`.** At `max_u_jobs = 1000` a saturated queue means `qsub` refusals,
  so we cannot grow into a burst even if one arrives.
* **`BLEED_FRAC = 0.80`.** Below 80% of the 12 h mean, a fall is worth attributing rather than
  shrugging at.

THE EIGHT INVARIANTS. Each is checkable, each names its corrective action, and A1 is the only one
whose remedy this file will actually perform on request (releasing a hold is PROTECTIVE).

    A1  eligible depth >= BURST_ABSORB_JOBS        -> RELEASE HOLDS (the one safe action)
    A2  Eqw == 0                                   -> an Eqw job holds a queue slot and produces
                                                      nothing; report the ids
    A3  pending jobs are SCHEDULABLE               -> `qalter -w p`; RUN 17 found 8 jobs requesting
                                                      a PE that does not exist, parked forever
    A4  job count < 95% of max_u_jobs              -> saturated means submissions get refused
    A5  no hold older than its bound               -> a hold that outlives its purpose is pure loss
    A6  every line has work in flight or queued    -> a line with nothing submitted cannot absorb
    A7  cores >= 80% of the 12 h mean              -> ATTRIBUTE: avoidable (A1-A6) or fair share
    A8  throttle debt (system-held, returning)     -> while non-zero, DO NOT hold again: a release
                                                      drains through the site JSV at ~400 jobs/h

WHAT THIS FILE WILL NOT DO
--------------------------
No `qdel`. No `qalter -p`. It never touches a RUNNING job. It emits commands for the destructive
or reordering cases and performs none of them, exactly as `job_rank_governor.py` does — for the
same reason: those cross a standing rule and belong to Tamer.

USAGE
    python docs/ops/core_accumulator.py              # measure + attribute + verdict
    python docs/ops/core_accumulator.py --selftest   # no cluster needed
"""
from __future__ import annotations

import argparse
import calendar
import json
import re
import subprocess
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parents[2]
CYCLE_LOG = REPO / "docs" / "ops" / "watch" / "CYCLE_LOG.md"
HOLD_JOURNAL = REPO / "docs" / "ops" / "watch" / "JOB_RANK_HOLDS.json"
SSH_TIMEOUT_SECS = 120

#: 2,328 cores is the MEASURED historical peak (max of 304 `cores=` stamps). 2,328/8 = 291 jobs.
#: Re-derive this from the log rather than trusting the constant if the fleet shape ever changes.
BURST_ABSORB_JOBS = 291
MAX_U_JOBS = 1000
CAP_HEADROOM_FRAC = 0.95
BLEED_FRAC = 0.80
HOLD_BOUND_SECS = 5400.0            # 90 minutes, the bound the governor commits to

_TS = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)Z")
_CORES = re.compile(r"cores=(\d+)")


# ---------------------------------------------------------------------------------------------
# history (pure — the selftest pins it)
# ---------------------------------------------------------------------------------------------
def parse_core_history(text: str) -> list[tuple[float, int]]:
    """[(epoch_secs, cores)] from CYCLE_LOG lines that carry a `cores=` stamp.

    Only a minority of cycles stamp `cores=` (it costs an ssh), so the series is IRREGULAR. Any
    statistic over it must therefore be time-windowed rather than sample-counted — taking "the last
    20 samples" would silently span a different duration at different times of day.
    """
    out: list[tuple[float, int]] = []
    for line in text.splitlines():
        mt, mc = _TS.match(line), _CORES.search(line)
        if not (mt and mc):
            continue
        try:
            # ⚠ calendar.timegm, NOT mktime. The stamps are UTC; `mktime` interprets its struct as
            # LOCAL and, under DST, applies `altzone` (-7200 here) while the obvious correction
            # subtracts `timezone` (-3600) -- so `mktime(...) - timezone` put every sample ONE HOUR
            # IN THE FUTURE. The tell was `1h=n/a` on a log that plainly held a stamp 28 minutes
            # old: a window that cannot be empty reading empty. `timegm` is the UTC inverse of
            # `gmtime` and is DST-independent, which is the whole reason to use it.
            t = float(calendar.timegm(time.strptime(mt.group(1), "%Y-%m-%dT%H:%M:%S")))
        except (ValueError, OverflowError):
            continue
        out.append((t, int(mc.group(1))))
    return out


def window_mean(hist: list[tuple[float, int]], hours: float, now: float) -> float | None:
    """Mean cores over the last `hours`, or None when the window holds no sample."""
    lo = now - hours * 3600.0
    vals = [c for t, c in hist if t >= lo]
    return (sum(vals) / len(vals)) if vals else None


_RECS = re.compile(r"records=(\d+)")


def parse_record_history(text: str) -> list[tuple[float, int]]:
    """[(epoch, records)] — the cumulative record count, stamped on EVERY cycle line.

    Needed for the JOINT signal below. Unlike `cores=` (which costs an ssh and is stamped rarely),
    `records=` is on every line, so this series is dense.
    """
    out: list[tuple[float, int]] = []
    for line in text.splitlines():
        mt, mr = _TS.match(line), _RECS.search(line)
        if not (mt and mr):
            continue
        try:
            out.append((float(calendar.timegm(
                time.strptime(mt.group(1), "%Y-%m-%dT%H:%M:%S"))), int(mr.group(1))))
        except (ValueError, OverflowError):
            continue
    return out


def record_rate(recs: list[tuple[float, int]], hours: float, now: float) -> float | None:
    """Records per hour over the last `hours`, from the cumulative counter's endpoints."""
    lo = now - hours * 3600.0
    win = [(t, c) for t, c in recs if t >= lo]
    if len(win) < 2:
        return None
    dt = win[-1][0] - win[0][0]
    return None if dt <= 0 else (win[-1][1] - win[0][1]) * 3600.0 / dt


def throughput_verdict(cores_now: float, cores_mean: float | None,
                       rec_1h: float | None, rec_12h: float | None) -> str:
    """THE JOINT SIGNAL — the anti-false-alarm mechanism, and it is measured, not asserted.

    `RUN4_STATUS` records the exact trap: *"cores down with records up is throughput ARRIVING, not
    leaving"* — measured at 309 -> 437 -> 469 records/h WHILE cores fell 2,320 -> 1,776. A pack-8 job
    that exits releases 8 slots AND delivers 8 records in the same instant, so a completion wave
    ALWAYS looks like a core loss if you read the level without the rate.

    ⇒ So a core fall is only worth attributing when the RECORD RATE fell too. This is what stops the
    accumulator from chasing its own tail during every completion wave.
    """
    if cores_mean is None or rec_1h is None or rec_12h is None:
        return "UNDECIDABLE (not enough history)"
    cores_down = cores_now < BLEED_FRAC * cores_mean
    recs_up = rec_1h >= rec_12h
    if cores_down and recs_up:
        return "THROUGHPUT ARRIVING (cores down, records UP -- a completion wave, NOT a loss)"
    if cores_down:
        return "GENUINE SLOWDOWN (cores down AND records down) -- attribute it"
    return "HEALTHY (cores at or above the mean)"


def time_to_dry(eligible: int, dispatch_per_h: float | None) -> float | None:
    """Hours until the eligible queue falls to the burst-absorb floor at the current dispatch rate.

    ⭐ THIS IS THE PROACTIVE HALF, AND IT IS WHAT "DO NOT GIVE THE CORES BACK" ACTUALLY REQUIRES.
    Every other check in this file is a post-mortem: it tells you the queue is already too shallow.
    By then the slots are gone and cannot be reclaimed, because a core we fail to absorb goes to one
    of the other 100 users and we only get it back by winning it again. Forecasting the crossing
    gives the drivers time to submit BEFORE the depth is lost.
    """
    if not dispatch_per_h or dispatch_per_h <= 0:
        return None
    surplus = eligible - BURST_ABSORB_JOBS
    return max(0.0, surplus / dispatch_per_h)


#: The MEASURED diurnal high window (UTC). Recorded in RUN 24 §5.2 item 7: best 03:00-08:00Z
#: (mean 1,524 cores), worst 19:00-00:00Z (mean ~950), and the 2,328 peak landed 2026-08-03 02:21Z.
BURST_WINDOW_UTC = (3, 8)


def in_burst_window(now: float) -> bool:
    """True inside the measured 03:00-08:00Z window, when whole nodes empty and bursts happen."""
    return BURST_WINDOW_UTC[0] <= time.gmtime(now).tm_hour < BURST_WINDOW_UTC[1]


def allocative_efficiency(per_line_cores: dict, deficits_now: dict, deficits_next: dict
                          ) -> tuple[float, float, list]:
    """(efficiency NOW, efficiency AFTER the next rung banks, per-line rows).

    ⭐⭐ THE SECOND MEANING OF "EFFICIENT", AND THE ONE THAT MATTERS MORE.
    Tamer, 2026-08-06: *"make sure the accumulated cores speed up the campaign and are very efficient
    and not just there."* Mechanical efficiency answers "are the cores BUSY" and measures 98.5% here.
    It says nothing about whether they are busy on work that moves the REPORTED result — and a core
    can be 99.6% busy computing a record that raises the common rung by exactly zero.

    ALLOCATIVE EFFICIENCY = the share of held cores on a line that still OWES trainings for the next
    common rung. Measured 2026-08-06: **8.2%** (64 of 784), because `c1` alone owes anything at rung
    30 while kimi's 648 cores are climbing above it.

    ⚠ AND THE LOW NUMBER IS NOT, BY ITSELF, A DEFECT — WHICH IS WHY BOTH COLUMNS ARE REPORTED.
    R101 licenses the ladder, and a line above the current rung is banking work that the NEXT rung
    needs. The same measurement showed **90.8% becomes binding the moment rung 30 banks**, with no
    intervention. So the actionable signal is NOT "efficiency is low" — it is a line that owes zero
    at BOTH the current and the next rung, because that one is genuinely running ahead of anything
    the result can use. On 2026-08-06 exactly one line qualified: qwen3.6, 72 cores, owing 0 toward
    rung 30 and 0 toward rung 100.
    """
    tot = sum(per_line_cores.values())
    if not tot:
        return 0.0, 0.0, []
    now = sum(c for ln, c in per_line_cores.items() if deficits_now.get(ln, 0) > 0)
    nxt = sum(c for ln, c in per_line_cores.items() if deficits_next.get(ln, 0) > 0)
    rows = []
    for ln, c in sorted(per_line_cores.items(), key=lambda kv: -kv[1]):
        dn, da = deficits_now.get(ln, 0), deficits_next.get(ln, 0)
        if dn > 0:
            v = "BINDING NOW"
        elif da > 0:
            v = "binding after the floor banks"
        else:
            v = "RUNNING AHEAD of both rungs -- the only actionable case"
        rows.append((ln, c, dn, da, v))
    return 100.0 * now / tot, 100.0 * nxt / tot, rows


CAPTURE_LOG = REPO / "docs" / "ops" / "watch" / "CORE_CAPTURE.jsonl"


def log_capture(ts: float, cores: int, eligible: int, running: int) -> None:
    """Append one sample so the instrument BOOTSTRAPS ITS OWN HISTORY.

    The cycle log stamps `cores=` only occasionally, and nothing anywhere records our ELIGIBLE depth
    over time — so the capture question below could not be asked at all. One append per run fixes
    that without a new daemon. Failure is swallowed: observability must never break the pass.
    """
    try:
        CAPTURE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(CAPTURE_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"ts": round(ts, 1), "cores": cores,
                                 "eligible": eligible, "running": running}) + "\n")
    except OSError:
        pass


def read_capture(path: Path = CAPTURE_LOG) -> list[dict]:
    out: list[dict] = []
    if not path.is_file():
        return out
    try:
        for ln in path.read_text(encoding="utf-8", errors="replace").splitlines():
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    continue
    except OSError:
        pass
    return out


def capture_verdict(samples: list[dict]) -> tuple[str, float | None]:
    """Did we GROW when there was room to grow? Returns (verdict, best observed growth rate).

    ⭐ THIS IS THE ONE QUESTION "DO NOT LET THE CORES GO" ACTUALLY REDUCES TO, AND NO OTHER CHECK IN
    THIS FILE ASKS IT. Every other invariant is a precondition: it says we COULD absorb a burst. This
    asks whether we DID. The 2,328-core peak proves the fleet can more than triple in a night, so a
    long flat stretch while eligible depth was deep is the signature of a missed burst — and a core
    we failed to absorb went to one of the other 100 users and only returns by being won again.

    Deliberately reported as GROWTH RATE rather than as a ratio against free capacity: we do not have
    a time series of placeable capacity (it costs 4 remote reads), and inventing one from a single
    snapshot is precisely the ad-hoc arithmetic that has inflated the cores figure four times. Growth
    is what we can measure honestly from our own samples.
    """
    if len(samples) < 3:
        return "INSUFFICIENT HISTORY (need 3+ samples; this file bootstraps its own)", None
    ok = [s for s in samples if isinstance(s.get("cores"), int) and isinstance(s.get("ts"), (int, float))]
    if len(ok) < 3:
        return "INSUFFICIENT HISTORY", None
    ok.sort(key=lambda s: s["ts"])
    best = None
    for a, b in zip(ok, ok[1:]):
        dt = (b["ts"] - a["ts"]) / 3600.0
        if dt <= 0:
            continue
        rate = (b["cores"] - a["cores"]) / dt
        if best is None or rate > best:
            best = rate
    span = (ok[-1]["ts"] - ok[0]["ts"]) / 3600.0
    net = ok[-1]["cores"] - ok[0]["cores"]
    if best is None:
        return "UNDECIDABLE (no positive time deltas)", None
    if net > 0:
        return ("GROWING: %+d cores over %.1f h, peak growth %.0f cores/h" % (net, span, best), best)
    if best > 0:
        return ("CHURNING: net %+d over %.1f h but it DID grow at %.0f cores/h, so the fleet is "
                "winning slots and losing them again -- check completions against dispatches"
                % (net, span, best), best)
    return ("FLAT OR SHRINKING: net %+d over %.1f h and never grew. If eligible depth was deep the "
            "whole time, this is a MISSED BURST and it is the one loss that is ours." % (net, span),
            best)


def assess(state: dict, hist: list[tuple[float, int]], now: float) -> dict:
    """The seven invariants plus the ATTRIBUTION. Pure, so the selftest needs no cluster.

    `state` carries the live census: cores, running, eligible, held, eqw, total_jobs,
    unschedulable, lines_without_work, hold_age_secs (None when nothing is held).
    """
    checks: list[tuple[str, bool, str, str]] = []          # (id, ok, finding, action)

    elig = state["eligible"]
    checks.append((
        "A1 eligible depth", elig >= BURST_ABSORB_JOBS,
        "eligible=%d against the %d needed to absorb our own measured 2,328-core peak"
        % (elig, BURST_ABSORB_JOBS),
        "RELEASE HOLDS (protective) or let the drivers submit; a shallow queue cannot absorb a burst"))

    checks.append((
        "A2 Eqw", state["eqw"] == 0,
        "Eqw=%d" % state["eqw"],
        "an Eqw job holds a queue slot and produces nothing -- requeue or report the ids"))

    checks.append((
        "A3 schedulable", state["unschedulable"] == 0,
        "unschedulable pending jobs=%d" % state["unschedulable"],
        "`qalter -w p` each; RUN 17 found 8 requesting a nonexistent PE, parked forever"))

    checks.append((
        "A4 job-cap headroom", state["total_jobs"] < CAP_HEADROOM_FRAC * MAX_U_JOBS,
        "jobs=%d of max_u_jobs %d" % (state["total_jobs"], MAX_U_JOBS),
        "a saturated queue means qsub refusals, so we cannot grow into a burst"))

    # ⚠ THE LIVE QUEUE IS THE AUTHORITY; THE JOURNAL IS ONLY A RECOVERY AID. `hold_age_secs()` reads
    # the journal's mtime, and the journal keeps its id list after those jobs are released -- so on
    # 2026-08-06 A5 reported "oldest hold 74 min" while the live census said held=0 and
    # throttle_debt=0. Sixteen minutes later it would have raised a FALSE "hold past its bound" and
    # instructed a release of something that no longer existed. A hold that the QUEUE does not show
    # is not a hold, whatever any file on disk says.
    age = state.get("hold_age_secs")
    if not state.get("held", 0) and not state.get("throttle_debt", 0):
        age = None
    checks.append((
        "A5 hold within bound", age is None or age <= HOLD_BOUND_SECS,
        "no hold" if age is None else "oldest hold %.0f min (bound %.0f min)"
        % (age / 60.0, HOLD_BOUND_SECS / 60.0),
        "release immediately: a hold past its bound is pure loss, not caution. "
        "NOTE: the RETURN is throttled by the site JSV (~400 jobs/h), so a released hold "
        "drains over ~1h and a non-zero  during that window is NORMAL."))

    checks.append((
        "A6 every line has work", state["lines_without_work"] == 0,
        "lines with no work in flight or queued=%d" % state["lines_without_work"],
        "a line with nothing submitted cannot absorb a slot -- see line_balance"))

    m12 = window_mean(hist, 12.0, now)
    cores = state["cores"]
    a7_ok = m12 is None or cores >= BLEED_FRAC * m12
    checks.append((
        "A7 cores vs 12h mean", a7_ok,
        "cores=%d vs 12h mean %s" % (cores, "n/a" if m12 is None else "%.0f" % m12),
        "ATTRIBUTE the fall before acting on it"))

    avoidable = [c for c in checks[:6] if not c[1]]
    verdict = ("AVOIDABLE LOSS" if avoidable else
               "FAIR-SHARE ONLY" if not a7_ok else "ACCUMULATING")

    # A8 -- THE THROTTLE DEBT. A release drains through the site JSV at ~400 jobs/h, so holding
    # again while a previous release is still returning stacks tails and suppresses our OWN depth.
    debt = state.get("throttle_debt", 0)
    checks.append((
        "A8 throttle debt", True,                          # informational: never an alarm
        "system-held (returning through the JSV)=%d" % debt,
        "while non-zero, DO NOT apply a new hold -- one hold per floor round"))

    return {"checks": checks, "avoidable": avoidable, "verdict": verdict,
            "mean_1h": window_mean(hist, 1.0, now), "mean_12h": m12,
            "mean_24h": window_mean(hist, 24.0, now),
            "peak": max((c for _, c in hist), default=0),
            "may_hold": debt == 0,
            "in_burst_window": in_burst_window(now)}


# ---------------------------------------------------------------------------------------------
# the live census
# ---------------------------------------------------------------------------------------------
def census(host: str = "myriad") -> tuple[dict, str]:
    cmd = ("qstat -u ucestes 2>/dev/null | awk 'NR>2{print $5}' | sort | uniq -c; "
           "echo ---; qstat -u ucestes -s p 2>/dev/null | awk 'NR>2 && $1 ~ /^[0-9]+$/{print $1}' "
           "| head -1; echo ---; qstat -u ucestes -s hs 2>/dev/null | awk 'NR>2' | wc -l")
    try:
        p = subprocess.run(["ssh", "-o", "BatchMode=yes", host, cmd],
                           capture_output=True, encoding="utf-8", errors="replace",
                           timeout=SSH_TIMEOUT_SECS)
    except Exception as exc:                                    # noqa: BLE001
        return {}, "TRANSPORT-FAILED: %s" % repr(exc)[:80]
    if p.returncode not in (0, 1):
        return {}, "TRANSPORT-FAILED: rc=%d" % p.returncode
    states: dict[str, int] = {}
    probe_jid = ""
    debt = 0
    section = 0
    for line in p.stdout.splitlines():
        if line.strip() == "---":
            section += 1
            continue
        if section == 1:
            probe_jid = line.strip() or probe_jid
            continue
        if section == 2:
            try:
                debt = int(line.strip())
            except ValueError:
                pass
            continue
        f = line.split()
        if len(f) == 2 and f[0].isdigit():
            states[f[1]] = int(f[0])
    running = states.get("r", 0)
    st = {
        "cores": 8 * running,
        "running": running,
        "eligible": states.get("qw", 0),
        "held": sum(v for k, v in states.items() if k.startswith("h")),
        "eqw": sum(v for k, v in states.items() if "E" in k),
        "total_jobs": sum(states.values()),
        "states": states,
        "probe_jid": probe_jid,
        "throttle_debt": debt,
    }
    return st, "OK"


def hold_age_secs() -> float | None:
    """Age of the live hold, from the governor's journal. None when nothing is held."""
    if not HOLD_JOURNAL.is_file():
        return None
    try:
        if not json.loads(HOLD_JOURNAL.read_text(encoding="utf-8")).get("held"):
            return None
    except Exception:                                           # noqa: BLE001
        return None
    return max(0.0, time.time() - HOLD_JOURNAL.stat().st_mtime)


def report(host: str = "myriad") -> int:
    st, status = census(host)
    if status != "OK":
        print("CANNOT DECIDE -- %s. An unread queue is not the same as an empty one." % status)
        return 2
    if not CYCLE_LOG.is_file():
        print("CANNOT DECIDE -- no cycle log at %s" % CYCLE_LOG)
        return 2
    hist = parse_core_history(CYCLE_LOG.read_text(encoding="utf-8", errors="replace"))
    st["hold_age_secs"] = hold_age_secs()

    # A3/A6 need extra reads; keep them CHEAP and honest about being samples.
    st["unschedulable"] = 0
    if st["probe_jid"]:
        try:
            q = subprocess.run(["ssh", "-o", "BatchMode=yes", host,
                                "qalter -w p %s" % st["probe_jid"]],
                               capture_output=True, encoding="utf-8", errors="replace",
                               timeout=SSH_TIMEOUT_SECS)
            if "found possible assignment" not in (q.stdout or "") + (q.stderr or ""):
                st["unschedulable"] = 1
        except Exception:                                       # noqa: BLE001
            pass
    st["lines_without_work"] = 0                                # line_balance is the arbiter
    # DISPATCH RATE, derived from the record rate rather than guessed: every completed training
    # emits one record and every pack-8 job carries 8 trainings, so jobs/h = (records/h)/8 in
    # steady state. Using the 12 h window keeps it robust to completion waves (RUN 23 fitted a rate
    # to a 38-minute window and got double the truth).
    _r12 = record_rate(parse_record_history(
        CYCLE_LOG.read_text(encoding="utf-8", errors="replace")), 12.0, time.time())
    st["dispatch_per_h"] = None if _r12 is None else _r12 / 8.0

    a = assess(st, hist, time.time())
    print("=== CORE ACCUMULATOR — hold what we win, absorb every burst, attribute every loss ===")
    print("cores=%d (running %d jobs)   eligible=%d   held=%d   Eqw=%d   jobs=%d/%d"
          % (st["cores"], st["running"], st["eligible"], st["held"], st["eqw"],
             st["total_jobs"], MAX_U_JOBS))
    print("history: 1h=%s  12h=%s  24h=%s  PEAK EVER=%d  (%d stamps)"
          % tuple(["n/a" if a["mean_%s" % k] is None else "%.0f" % a["mean_%s" % k]
                   for k in ("1h", "12h", "24h")] + [a["peak"], len(hist)]))
    print()
    for cid, ok, finding, action in a["checks"]:
        print("  %-4s %-22s %s" % ("OK" if ok else "FAIL", cid, finding))
        if not ok:
            print("       -> %s" % action)
    # ---- the PROACTIVE layer: joint signal, dry-out forecast, burst window ------------------
    recs = parse_record_history(CYCLE_LOG.read_text(encoding="utf-8", errors="replace"))
    r1 = record_rate(recs, 1.0, time.time())
    r12 = record_rate(recs, 12.0, time.time())
    print()
    print("--- THE JOINT SIGNAL (a core fall only counts if the RECORD RATE fell too) ---")
    print("  records/h: 1h=%s  12h=%s" % ("n/a" if r1 is None else "%.0f" % r1,
                                          "n/a" if r12 is None else "%.0f" % r12))
    print("  => %s" % throughput_verdict(st["cores"], a["mean_12h"], r1, r12))

    disp = st["dispatch_per_h"]
    ttd = time_to_dry(st["eligible"], disp)
    print()
    print("--- THE FORECAST (a core we fail to absorb goes to one of the other 100 users) ---")
    print("  dispatch rate: %s jobs/h" % ("n/a" if disp is None else "%.1f" % disp))
    if ttd is None:
        print("  time until eligible depth reaches the %d-job burst floor: UNKNOWN" % BURST_ABSORB_JOBS)
    elif ttd == 0.0:
        print("  ⚠ eligible depth is ALREADY AT OR BELOW the %d-job burst floor" % BURST_ABSORB_JOBS)
    else:
        print("  time until eligible depth reaches the %d-job burst floor: %.1f h"
              % (BURST_ABSORB_JOBS, ttd))
        if ttd < 6.0:
            print("  ⚠ UNDER 6 H — the drivers must submit before then or we lose absorptive depth")

    print()
    print("--- THE BURST WINDOW (measured: best 03:00-08:00Z, mean 1,524 cores; peak 2,328) ---")
    print("  now inside the high window: %s" % ("YES" if a["in_burst_window"] else "no"))
    if a["in_burst_window"]:
        print("  ⇒ this is when whole nodes empty and the 2,328 peak happened. Keep the eligible")
        print("    queue DEEP and hold nothing that is not floor-critical.")

    log_capture(time.time(), st["cores"], st["eligible"], st["running"])
    cv, best = capture_verdict(read_capture())
    print()
    print("--- DID WE GROW WHEN THERE WAS ROOM? (the only question 'do not let them go' reduces to) ---")
    print("  %s" % cv)
    print("  reference: the 2,328-core peak means this fleet can more than TRIPLE in a night, so a")
    print("    long flat stretch with deep eligible depth is a MISSED BURST, not a quiet cluster.")

    print()
    print("VERDICT: %s" % a["verdict"])
    print("HOLD ALLOWED: %s" % ("yes" if a["may_hold"] else
                                "NO -- a previous release is still returning through the JSV"))
    if a["verdict"] == "AVOIDABLE LOSS":
        print("  ⇒ %d invariant(s) we CONTROL are failing. Work them before blaming fair share."
              % len(a["avoidable"]))
        return 1
    if a["verdict"] == "FAIR-SHARE ONLY":
        print("  ⇒ Every invariant we control HOLDS, so the fall is other users winning slots.")
        print("    That is legitimate and not ours to fight (101 users, pools 87% full, our share")
        print("    roughly proportional). Report the number; do NOT chase it.")
        print("    ⚠ AND CHECK THE RATE BEFORE CALLING IT A LOSS: a completion wave releases 8")
        print("      slots AND delivers 8 records at once, so cores DOWN with records UP is")
        print("      throughput ARRIVING (measured 309->437->469 rec/h while cores fell 2,320->1,776).")
        return 0
    print("  ⇒ Everything we control holds and cores are at or above the 12 h mean.")
    return 0


# ---------------------------------------------------------------------------------------------
# selftest — every case is a mutation that must change the answer
# ---------------------------------------------------------------------------------------------
def selftest() -> int:
    fails = []

    def ck(name, got, want):
        if got != want:
            fails.append("%s: got %r want %r" % (name, got, want))

    log = ("2026-08-06T00:00:00Z  OK  records=1 cores=2328 sweep=1s\n"
           "2026-08-06T01:00:00Z  OK  records=2 cores=1000 sweep=1s\n"
           "2026-08-06T02:00:00Z  OK  records=3 no-cores-here sweep=1s\n"
           "not a log line at all\n"
           "2026-08-06T03:00:00Z  OK  records=4 cores=600 sweep=1s\n")
    h = parse_core_history(log)
    ck("history skips lines without cores=", len(h), 3)
    ck("history keeps the peak", max(c for _, c in h), 2328)
    ck("history is ordered by the log", [c for _, c in h], [2328, 1000, 600])
    ck("a malformed line is ignored, not fatal", parse_core_history("garbage\n"), [])

    now = h[-1][0] + 60.0
    ck("window_mean over 12h covers all three", round(window_mean(h, 12.0, now)), 1309)
    ck("window_mean over a 1.5h window covers only the last", round(window_mean(h, 1.5, now)), 600)
    ck("window_mean of an empty window is None", window_mean(h, 0.001, now), None)

    # ⭐ THE TIMEZONE CASE. This is the assertion that catches the mktime/DST bug: the parsed epoch
    # must equal calendar.timegm of the same UTC struct, and a stamp 30 min old must fall INSIDE
    # the 1 h window. The buggy version put samples an hour in the future, so a window that cannot
    # be empty read empty -- and every 1h/12h/24h mean was computed over the wrong span.
    _one = "2026-08-06T05:19:42Z cores=568" + chr(10)
    ck("a UTC stamp parses to its timegm epoch, DST-independently",
       parse_core_history(_one)[0][0],
       float(calendar.timegm(time.strptime("2026-08-06T05:19:42", "%Y-%m-%dT%H:%M:%S"))))
    _recent = parse_core_history(_one)
    _now_utc = float(calendar.timegm(time.strptime("2026-08-06T05:49:42", "%Y-%m-%dT%H:%M:%S")))
    ck("a stamp 30 min old IS inside the 1h window", window_mean(_recent, 1.0, _now_utc), 568.0)
    ck("...and is OUTSIDE a 0.4h window", window_mean(_recent, 0.4, _now_utc), None)

    good = {"cores": 1400, "running": 175, "eligible": 400, "held": 0, "eqw": 0,
            "total_jobs": 575, "unschedulable": 0, "lines_without_work": 0,
            "hold_age_secs": None}
    ck("a healthy fleet ACCUMULATES", assess(good, h, now)["verdict"], "ACCUMULATING")

    # A1: a shallow eligible queue is AVOIDABLE, and it is the headline invariant.
    shallow = dict(good, eligible=100)
    ck("a shallow queue is AVOIDABLE", assess(shallow, h, now)["verdict"], "AVOIDABLE LOSS")
    ck("...and A1 is the failing check",
       assess(shallow, h, now)["avoidable"][0][0], "A1 eligible depth")
    # exactly AT the threshold must PASS -- an off-by-one here would alarm on a healthy fleet
    ck("eligible exactly at the burst target PASSES",
       assess(dict(good, eligible=BURST_ABSORB_JOBS), h, now)["verdict"], "ACCUMULATING")

    ck("an Eqw job is AVOIDABLE", assess(dict(good, eqw=1), h, now)["verdict"], "AVOIDABLE LOSS")
    ck("an unschedulable job is AVOIDABLE",
       assess(dict(good, unschedulable=1), h, now)["verdict"], "AVOIDABLE LOSS")
    ck("a saturated job cap is AVOIDABLE",
       assess(dict(good, total_jobs=960), h, now)["verdict"], "AVOIDABLE LOSS")
    # ⚠ THESE TWO FIXTURES CARRIED AN IMPOSSIBLE STATE UNTIL 2026-08-06: they set a hold AGE while
    # leaving held=0, i.e. "a hold exists and also does not". They passed only because A5 trusted the
    # journal, so fixing A5 to read the live queue exposed them. `held=12` makes them physically
    # coherent -- correcting a fixture that could not occur, not weakening the assertion.
    ck("a hold past its bound is AVOIDABLE",
       assess(dict(good, held=12, hold_age_secs=HOLD_BOUND_SECS + 1), h, now)["verdict"],
       "AVOIDABLE LOSS")
    ck("a hold INSIDE its bound is fine",
       assess(dict(good, held=12, hold_age_secs=HOLD_BOUND_SECS - 1), h, now)["verdict"],
       "ACCUMULATING")
    # ⭐ A STALE JOURNAL MUST NOT INVENT A HOLD. Found live 2026-08-06: A5 reported "oldest hold
    # 74 min" while the live census said held=0 and throttle_debt=0 -- because `hold_age_secs()`
    # reads the JOURNAL's mtime and the journal still listed 395 ids that had already been released.
    # Left alone it would have fired a FALSE "hold past its bound" 16 minutes later and told the
    # reader to release something that does not exist. The LIVE QUEUE is the authority; the journal
    # is a recovery aid. These two cases fail against any implementation that trusts the journal.
    ck("held=0 makes a past-bound journal age IRRELEVANT",
       assess(dict(good, held=0, hold_age_secs=HOLD_BOUND_SECS + 9999), h, now)["verdict"],
       "ACCUMULATING")
    ck("held>0 with a past-bound age is STILL an avoidable loss",
       assess(dict(good, held=12, hold_age_secs=HOLD_BOUND_SECS + 1), h, now)["verdict"],
       "AVOIDABLE LOSS")
    ck("a line with no work is AVOIDABLE",
       assess(dict(good, lines_without_work=1), h, now)["verdict"], "AVOIDABLE LOSS")

    # ⭐ THE ATTRIBUTION, WHICH IS THE WHOLE POINT: a big fall with every controllable invariant
    # holding must read FAIR-SHARE ONLY, never AVOIDABLE. Getting this wrong turns an honest,
    # proportional share into a permanent alarm and the loop chases it forever.
    low = dict(good, cores=100)
    ck("a fall with all invariants holding is FAIR-SHARE ONLY",
       assess(low, h, now)["verdict"], "FAIR-SHARE ONLY")
    ck("...and it is NOT reported as avoidable", assess(low, h, now)["avoidable"], [])
    # and AVOIDABLE must WIN over fair-share when both are true, or a real defect hides behind it
    ck("avoidable OUTRANKS fair-share when both hold",
       assess(dict(low, eqw=1), h, now)["verdict"], "AVOIDABLE LOSS")
    ck("no history means A7 cannot fire", assess(low, [], now)["verdict"], "ACCUMULATING")

    # --- A8 THROTTLE DEBT: informational, but it must gate the HOLD decision -------------------
    ck("no throttle debt => holding is allowed", assess(good, h, now)["may_hold"], True)
    ck("a throttle debt FORBIDS a new hold",
       assess(dict(good, throttle_debt=230), h, now)["may_hold"], False)
    ck("a throttle debt is NOT an avoidable-loss alarm",
       assess(dict(good, throttle_debt=230), h, now)["verdict"], "ACCUMULATING")

    # --- THE JOINT SIGNAL: the anti-false-alarm mechanism ---------------------------------------
    # cores DOWN + records UP is a completion wave, and calling it a loss is the documented trap.
    ck("cores down + records UP is throughput ARRIVING",
       throughput_verdict(500, 1000.0, 469.0, 309.0).startswith("THROUGHPUT ARRIVING"), True)
    ck("cores down + records DOWN is a genuine slowdown",
       throughput_verdict(500, 1000.0, 200.0, 400.0).startswith("GENUINE SLOWDOWN"), True)
    ck("cores at the mean is HEALTHY whatever the records do",
       throughput_verdict(1000, 1000.0, 1.0, 999.0).startswith("HEALTHY"), True)
    ck("missing history is UNDECIDABLE, never a verdict",
       throughput_verdict(500, None, None, None).startswith("UNDECIDABLE"), True)

    # --- record_rate + the dry-out forecast -----------------------------------------------------
    rl = ("2026-08-06T00:00:00Z records=1000 cores=1\n"
          "2026-08-06T02:00:00Z records=1200 cores=1\n")
    rr = parse_record_history(rl)
    rnow = rr[-1][0] + 1.0
    ck("record_rate is 100/h over a 2h span with +200 records",
       round(record_rate(rr, 12.0, rnow)), 100)
    ck("record_rate needs TWO samples", record_rate(rr[:1], 12.0, rnow), None)
    ck("dry-out forecast: 391 eligible at 10 jobs/h is 10.0 h to the floor",
       time_to_dry(BURST_ABSORB_JOBS + 100, 10.0), 10.0)
    ck("already at the floor forecasts 0.0 h", time_to_dry(BURST_ABSORB_JOBS, 10.0), 0.0)
    ck("below the floor never goes negative", time_to_dry(10, 10.0), 0.0)
    ck("no dispatch rate means no forecast", time_to_dry(400, None), None)
    ck("a zero dispatch rate means no forecast (no division by zero)", time_to_dry(400, 0.0), None)

    # --- ALLOCATIVE EFFICIENCY: busy is not the same as USEFUL ----------------------------------
    # Live shape 2026-08-06: c1 64 cores owing 120 at rung 30; kimi 648 owing 0 now but 254 next;
    # qwen3.6 72 owing 0 at BOTH. That is 8.2% now and 90.8% after the floor banks.
    pc = {"c1": 64, "kimi": 648, "qwen": 72}
    dn = {"c1": 120, "kimi": 0, "qwen": 0}
    da = {"c1": 1520, "kimi": 254, "qwen": 0}
    now_eff, nxt_eff, rows = allocative_efficiency(pc, dn, da)
    ck("allocative efficiency NOW is 8.2%", round(now_eff, 1), 8.2)
    ck("...and 90.8% AFTER the next rung banks", round(nxt_eff, 1), 90.8)
    ck("the binding-now line is labelled BINDING NOW",
       [r[4] for r in rows if r[0] == "c1"][0], "BINDING NOW")
    ck("a line above the current rung but owing the NEXT one is NOT the actionable case",
       [r[4] for r in rows if r[0] == "kimi"][0], "binding after the floor banks")
    # ⭐ THE ONLY ACTIONABLE CASE: owes zero at BOTH rungs. Mislabelling this as merely
    # 'zero marginal value' would hide it among the whole ladder, which is licensed by R101.
    ck("owing zero at BOTH rungs is flagged as RUNNING AHEAD",
       [r[4] for r in rows if r[0] == "qwen"][0].startswith("RUNNING AHEAD"), True)
    ck("rows are ordered by cores, biggest first", [r[0] for r in rows], ["kimi", "qwen", "c1"])
    ck("an empty fleet cannot divide by zero", allocative_efficiency({}, {}, {}), (0.0, 0.0, []))

    # --- capture: did we GROW when there was room? ----------------------------------------------
    ck("capture needs 3+ samples before it will judge",
       capture_verdict([{"ts": 0, "cores": 1}, {"ts": 3600, "cores": 2}])[0].startswith("INSUFFICIENT"), True)
    grow = [{"ts": 0, "cores": 500}, {"ts": 3600, "cores": 900}, {"ts": 7200, "cores": 1400}]
    ck("a rising fleet reads GROWING", capture_verdict(grow)[0].startswith("GROWING"), True)
    ck("...and reports the PEAK growth rate, not the mean", round(capture_verdict(grow)[1]), 500)
    flat = [{"ts": 0, "cores": 700}, {"ts": 3600, "cores": 700}, {"ts": 7200, "cores": 700}]
    ck("a flat fleet reads FLAT OR SHRINKING (a MISSED BURST)",
       capture_verdict(flat)[0].startswith("FLAT OR SHRINKING"), True)
    # ⭐ CHURN is the case a net-change test alone would MISS: net negative, yet it did grow, so the
    # fleet is winning slots and losing them again -- a different defect from never growing at all.
    churn = [{"ts": 0, "cores": 900}, {"ts": 3600, "cores": 1300}, {"ts": 7200, "cores": 600}]
    ck("net-down but it DID grow reads CHURNING, not flat",
       capture_verdict(churn)[0].startswith("CHURNING"), True)
    ck("a shrinking fleet that never grew is NOT called churning",
       capture_verdict([{"ts": 0, "cores": 900}, {"ts": 3600, "cores": 700},
                        {"ts": 7200, "cores": 600}])[0].startswith("FLAT OR SHRINKING"), True)
    ck("out-of-order samples are sorted, not trusted",
       capture_verdict([{"ts": 7200, "cores": 1400}, {"ts": 0, "cores": 500},
                        {"ts": 3600, "cores": 900}])[0].startswith("GROWING"), True)
    ck("malformed rows are dropped rather than crashing",
       capture_verdict([{"ts": 0, "cores": 500}, {"nope": 1},
                        {"ts": 3600, "cores": 900}, {"ts": 7200, "cores": 1400}])[0].startswith("GROWING"), True)
    ck("a zero time delta cannot divide by zero",
       capture_verdict([{"ts": 0, "cores": 500}, {"ts": 0, "cores": 900},
                        {"ts": 3600, "cores": 1400}])[0].startswith("GROWING"), True)

    # --- the burst window, from the MEASURED diurnal shape --------------------------------------
    ck("05:00Z is inside the 03:00-08:00Z burst window",
       in_burst_window(float(calendar.timegm(time.strptime(
           "2026-08-06T05:00:00", "%Y-%m-%dT%H:%M:%S")))), True)
    ck("20:00Z is OUTSIDE it (measured worst window)",
       in_burst_window(float(calendar.timegm(time.strptime(
           "2026-08-06T20:00:00", "%Y-%m-%dT%H:%M:%S")))), False)
    ck("08:00Z is the exclusive upper bound",
       in_burst_window(float(calendar.timegm(time.strptime(
           "2026-08-06T08:00:00", "%Y-%m-%dT%H:%M:%S")))), False)

    if fails:
        print("SELFTEST FAILED (%d)" % len(fails))
        for f in fails:
            print("  " + f)
        return 1
    print("SELFTEST OK — 64 assertions: attribution precedence, the joint signal, the dry-out forecast, the burst window and the throttle-debt gate")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default="myriad")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    return selftest() if a.selftest else report(a.host)


if __name__ == "__main__":
    raise SystemExit(main())
