#!/usr/bin/env python
"""OCCUPANCY WATCH -- is the fleet as large as the WORK WE OWE justifies?

★ WHY THIS EXISTS. On 2026-08-04 the fleet fell from 1,952 slots to 984 over three hours with the
queue at ZERO, and **nothing on the board said anything**. Tamer noticed it by reading the core
count off the status page and asked what was going on. Every existing instrument was green and
correct: `line_balance` reported CLEAN because every line had *some* work in flight, `preflight`
passed all seventeen rows, and `vanished_array_watch` printed "no vanished arrays detected" while it
could not resolve the twelve blocks that mattered. **No instrument compared the size of the fleet to
the size of the work.**

★★ THE DIAGNOSIS, and it is why this file measures what it measures. `src/cluster/driver.py:550-553`
requeues a tier's remaining specs only when NO job of that tier is still alive:

    if alive_names:  alive_seen = True
    else:            <DRAIN TRANSITION -> requeue>

So each line runs a SAWTOOTH -- submit a tier as ~50-100 arrays, drain it over ~9.4 h, sit at low
occupancy through the TAIL while one straggler holds the transition shut, then requeue en masse. A
trough is therefore NORMAL and self-healing. What is NOT normal, and what this file exists to catch,
is a trough that does not end: pending work that is large, occupancy that is low, and a queue that is
empty, **persisting across passes**.

★★★ THE DISCRIMINATOR, because a trough and a stall look identical in a single sample. A snapshot
cannot tell them apart -- only PERSISTENCE can. So this file keeps a small history and reports:

    OWED      units the drivers say are pending, per line, from their own logs
    IN FLIGHT slots we actually hold
    QUEUED    slots waiting to dispatch
    RATIO     in-flight units / owed units
    PERSISTED how many consecutive passes this line has been below the floor

A single low-ratio pass is INFO. Three consecutive low-ratio passes with an empty queue is the
actionable state, and the message says which line and for how long.

⚠ IT DOES NOT ALARM ON A LOW RATIO ALONE, and that restraint is the design. A line legitimately runs
at a low ratio through every tail, so a per-sample threshold would fire several times a day, teach
its reader to ignore it, and reproduce the alarm-fatigue pathology that let `guards=2` hide a real
defect for 31 hours on this campaign.

EFFECT-BLIND: job counts, slot counts and the drivers' own pending integers. No record is opened and
no outcome is read.

    python docs/ops/occupancy_watch.py [--floor 0.15] [--passes 3] [--once]

exit 0 = healthy, or a trough within tolerance   exit 1 = a line has persisted below the floor
exit 2 = could not measure (UNKNOWN -- never reported as healthy)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parents[2]
RUN = REPO / "outputs" / "campaign_cluster_run4"
STATE = REPO / "docs" / "ops" / "watch" / ".occupancy_watch_state.json"

#: `[<batch>] <done>/<total> done, <pending> pending, round <n>` -- the driver's own progress line.
#: ⚠⚠ P306-b -- EVERY LITERAL SPACE IN THESE PATTERNS IS A BUG, AND TWO OF THEM WERE.
#: The driver log is hard-wrapped by the PowerShell host that runs the supervisor, and the wrap can
#: fall immediately after the pending COUNT ("... done, 8 \npending, round 1") or inside "batch
#: complete". This module collapses newlines to a SPACE, so those records arrive carrying DOUBLE
#: spaces, and a pattern with a literal single space matches neither.
#:
#: MEASURED over the live logs, 2026-08-04 22:3xZ: the strict pattern saw 21,164 of 24,549 progress
#: records -- **3,385 missed, 13.8%** -- and the damage is not spread evenly, it is concentrated:
#:
#:      line              owed as reported      owed in truth
#:      glm-5_2                          1              2,691
#:      kimi-k3                          2              2,692
#:      deepseek-v4-pro                  0                 60
#:
#: A line owing 2,691 units and reported as owing 1 can never be flagged under-covered -- the ratio
#: divides by a near-zero denominator, which is exactly why kimi printed **247.273**. So the
#: instrument built to detect under-coverage was structurally blind to the two largest owing lines,
#: and it failed toward OK. `vanished_array_watch` already carries this same lesson in its own
#: SUBMITTED pattern ("a single-space pattern matched none of the 14 multi-array blocks"); this file
#: was never given the fix. **A class fix is only as complete as the population you drew it over.**
PROGRESS = re.compile(r"\[([A-Za-z0-9_.\-]+)\]\s+(\d+)/(\d+)\s+done,\s*(\d+)\s+pending", re.M)
#: `[<batch>] batch complete: {...}` -- the driver's own end-of-batch announcement (P306). A batch
#: that has printed this AFTER its last progress line owes nothing, whatever that progress line said.
#: ⚠ `\s+`, not a literal space: this one wraps too. `[leg2_..._h2_pair_test] batch \ncomplete: {...}`
#: is a REAL line from `driver_glm-5_2.log`, so a strict pattern would have under-corrected P306-a
#: on precisely the batches that had just finished.
COMPLETE = re.compile(r"\[([A-Za-z0-9_.\-]+)\]\s+batch\s+complete", re.M)
#: A driver line is only current if it is recent; a dead driver's last line must not count as owed.
STALE_LOG_MIN = 30.0


def owed_by_line() -> tuple[dict[str, int], list[str], dict[str, int]]:
    """Units each line's driver currently says are pending, from the LAST line per batch.

    ⚠⚠ P306 (RUN 22 pass 2, 2026-08-04) -- A COMPLETED BATCH KEPT OWING WORK FOREVER, AND IT MADE
    THIS FILE'S FLAGSHIP ALARM FIRE ON A HEALTHY LINE.

    The driver announces a finished batch with `[<batch>] batch complete: {...}`. It does NOT emit a
    final `0 pending` progress line, because completion is detected on the poll AFTER the last record
    lands. So a batch's last PROGRESS line carries a non-zero `pending` for the rest of the log, and
    summing "the last line per batch" counted work that no longer exists.

    MEASURED on the live logs at 2026-08-04 22:2xZ, which is how it was found:

        sonnet-5   owed = 63     truly pending = 10     53 units from FIVE COMPLETED batches
                   (sweep_t1 11, t3 11, t4 10, t5 10, t6 11)

    Its true ratio is 8 in-flight / 10 pending = **0.8**; the tool reported **0.127** and had
    escalated it to `3 pass(es)` -- the ACTIONABLE state this module exists to raise. Campaign-wide
    the phantom total was 90 of 5,692 units (1.6%), but it is CONCENTRATED on the lines that have
    completed the most batches, i.e. exactly the lines furthest along.

    ⚠ THIS IS A CORRECTNESS FIX, NOT A WIDENED THRESHOLD. The floor and the persistence count are
    untouched. A batch that has completed owes nothing, so excluding it makes `owed` mean what this
    module's own header already claims it means. The discriminator is POSITIONAL, not the mere
    presence of a completion line: a batch can complete and then be re-entered in a later round, so
    only a `batch complete` appearing AFTER that batch's last progress line counts as finished.

    Returns `(owed, stale, dropped)`, where `dropped` is the per-line phantom total. It is REPORTED
    rather than silently discarded -- a correction nobody can see is a correction nobody can check.
    """
    owed: dict[str, int] = {}
    stale: list[str] = []
    dropped: dict[str, int] = {}
    for log in sorted(RUN.glob("driver_*.log")):
        line = log.stem[len("driver_"):]
        try:
            age_min = (time.time() - log.stat().st_mtime) / 60.0
            text = log.read_text(encoding="utf-8", errors="replace")[-400_000:]
        except OSError:
            stale.append(line)
            continue
        if age_min > STALE_LOG_MIN:
            stale.append(line)          # COMPLETE lines land here too, and that is correct
            continue
        flat = text.replace("\n", " ")
        last: dict[str, int] = {}
        at: dict[str, int] = {}
        for m in PROGRESS.finditer(flat):
            last[m.group(1)] = int(m.group(4))
            at[m.group(1)] = m.start()
        done_at: dict[str, int] = {}
        for m in COMPLETE.finditer(flat):
            done_at[m.group(1)] = m.start()
        live = {b: k for b, k in last.items() if done_at.get(b, -1) <= at[b]}
        owed[line] = sum(live.values())
        dropped[line] = sum(last.values()) - owed[line]
    return owed, stale, dropped


def fleet() -> tuple[dict[str, tuple[int, int]], int, int] | None:
    """{tag: (running_slots, queued_slots)} plus fleet totals, from one `qstat -xml`."""
    try:
        out = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=25",
                              "myriad", "qstat -u ucestes -xml"],
                             capture_output=True, text=True, timeout=120)
    except Exception:                                          # noqa: BLE001
        return None
    if out.returncode != 0:
        return None
    raw = out.stdout
    i = raw.find("<?xml")
    if i < 0:
        return None
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(raw[i:])
    except Exception:                                          # noqa: BLE001
        return None
    per: dict[str, list[int]] = {}
    run_s = q_s = 0
    for jl in root.iter("job_list"):
        st = (jl.findtext("state") or "").strip()
        name = (jl.findtext("JB_name") or "").strip()
        try:
            slots = int(jl.findtext("slots") or 0)
        except ValueError:
            slots = 0
        # ⚠ KEY ON THE WHOLE JOB NAME, NOT ITS FIRST TOKEN. The first version bucketed by the `legN`
        # / `c1` prefix and then tried to match a driver's line name against it -- `haiku_4_5`[:4]
        # against `leg5` -- which never matches, so EVERY line reported 0 in flight and the tool
        # printed a calm "reported, not alarmed" over a fleet of 2,024 slots. A monitor that is
        # useless and green is the exact class this file was written to catch, and I built one.
        # The job name CONTAINS the line token (`leg5_leg_haiku_4_5_sweep_t3_p01`), so the caller
        # matches on that; the whole name is kept here and the bucketing is done there.
        cell = per.setdefault(name, [0, 0])
        if st.startswith("r") or st == "Rr":
            cell[0] += slots
            run_s += slots
        else:
            cell[1] += slots
            q_s += slots
    return {k: (v[0], v[1]) for k, v in per.items()}, run_s, q_s


#: A driver log is `driver_<line>.log`; a job name embeds the line with `_` for `-` and `.`.
#: `core` is the one line whose jobs carry no form of its own name -- they are tagged `c1`.
_LINE_JOB_TOKEN = {"core": "c1_", "h3": "h3ss"}


def _job_token(line: str) -> str:
    return _LINE_JOB_TOKEN.get(line, line.replace("-", "_").replace(".", "_"))


def _load() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save(d: dict) -> None:
    try:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        tmp = STATE.with_suffix(".tmp")
        tmp.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
        tmp.replace(STATE)
    except OSError:
        pass


def main() -> int:
    ap = argparse.ArgumentParser(description="Fleet size against the work we owe.")
    ap.add_argument("--floor", type=float, default=0.15,
                    help="in-flight units / owed units below which a line counts as low")
    ap.add_argument("--passes", type=int, default=3,
                    help="consecutive low passes before a line is reported as ACTIONABLE")
    ap.add_argument("--once", action="store_true", help="accepted for symmetry; this tool is one-shot")
    args = ap.parse_args()

    owed, stale, dropped = owed_by_line()
    got = fleet()
    print("=== OCCUPANCY WATCH -- is the fleet as large as the work we owe? ===")
    if got is None:
        print("  COULD NOT REACH THE SCHEDULER -- UNKNOWN, never reported as healthy.")
        return 2
    per, run_s, q_s = got
    if not owed:
        print("  NO CURRENT DRIVER PROGRESS LINES -- UNKNOWN, not healthy. Stale/absent: %s"
              % (", ".join(stale) or "none"))
        return 2

    hist = _load()
    print("  fleet: %d running slot(s), %d queued slot(s) across %d tag(s)" % (run_s, q_s, len(per)))
    print("  a QUEUED slot is work already accepted by the scheduler, so it counts as covered.")
    # P306: state the correction rather than applying it invisibly. A reader comparing this table
    # against a driver log must be able to see WHY the two differ.
    _drop_tot = sum(dropped.values())
    if _drop_tot:
        _who = ", ".join(f"{k} {v}" for k, v in sorted(dropped.items()) if v)
        print("  P306: %d unit(s) excluded from 'owed' because their batch has COMPLETED "
              "(the driver prints 'batch complete', never a final '0 pending'): %s"
              % (_drop_tot, _who))
    print()
    print("  %-20s %8s %10s %9s %7s %9s" % ("line", "owed", "in-flight", "queued", "ratio", "low for"))
    low_now: list[str] = []
    for line in sorted(owed):
        units = owed[line]
        # driver log name -> qstat tag is not derivable, so aggregate: compare per-line owed against
        # the FLEET, and report the per-line ratio only where the mapping is unambiguous.
        tok = _job_token(line)
        rs = qs = 0
        for jobname, (r_, q_) in per.items():
            if tok in jobname:
                rs += r_
                qs += q_
        ratio = ((rs + qs) / units) if units else float("inf")
        prev = int((hist.get("low_streak") or {}).get(line, 0))
        streak = prev + 1 if (units > 0 and ratio < args.floor and qs == 0) else 0
        if streak:
            low_now.append(line)
        print("  %-20s %8d %10d %9d %7s %9s"
              % (line, units, rs, qs, ("inf" if units == 0 else "%.3f" % ratio),
                 ("%d pass(es)" % streak) if streak else "-"))
        hist.setdefault("low_streak", {})[line] = streak
    hist["last_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    _save(hist)

    actionable = [ln for ln in low_now
                  if int(hist["low_streak"].get(ln, 0)) >= args.passes]
    print()
    if actionable:
        print("  !! %d LINE(S) HAVE PERSISTED BELOW THE FLOOR FOR %d+ PASSES: %s"
              % (len(actionable), args.passes, ", ".join(actionable)))
        print("     A single low pass is the NORMAL tail of a tier. This many in a row, with an")
        print("     EMPTY queue, is the state the sawtooth cannot explain. Read that line's driver")
        print("     log for a DRAIN TRANSITION, and `qstat -u ucestes -xml` for its surviving pack.")
        return 1
    if low_now:
        print("  %d line(s) are low THIS PASS but have not persisted: %s"
              % (len(low_now), ", ".join(low_now)))
        print("  That is the ordinary tail of a tier draining. Reported, not alarmed.")
    else:
        print("  every line's fleet is proportionate to the work it owes.")
    if stale:
        print("  (no current progress line, so not assessed: %s -- COMPLETE lines land here too)"
              % ", ".join(stale))
    return 0


def _selftest() -> int:
    """Prove `owed` counts PENDING work and only pending work (P306).

    This module shipped with NO test at all, which is how a completed batch could keep owing work
    for a whole campaign and escalate a healthy line to the ACTIONABLE state. The fixture uses the
    driver's REAL grammar, hard-wrapped exactly as the PowerShell host writes it, because every
    parsing defect in this project has come from that wrapping.

    Case C is the one that matters most: it is the control against OVER-correcting. A batch can
    complete and then be re-entered in a later round, so a naive `if this batch ever completed:
    skip it` would drop live work and blind the alarm in the opposite direction. Only a completion
    that appears AFTER the batch's last progress line counts.
    """
    global RUN
    import tempfile

    body = (
        # A -- completed AFTER its last progress line: owes NOTHING despite saying "8 pending".
        "2026-08-04 20:00:00 | INFO | src.cluster.driver | [leg8_sweep_t1] 437/445 done, 8 \n"
        "pending, round 1\n"
        "2026-08-04 20:03:00 | INFO | src.cluster.driver | [leg8_sweep_t1] batch \n"
        "complete: {'ok': True, 'completed': 445, 'total': 445, 'rounds': 1}\n"
        # B -- never completed: owes its 5.
        "2026-08-04 20:04:00 | INFO | src.cluster.driver | [leg8_sweep_t2] 440/445 done, 5 \n"
        "pending, round 1\n"
        # C -- completed EARLY, then re-entered: owes its 3. A presence-only test would say 0.
        "2026-08-04 19:00:00 | INFO | src.cluster.driver | [leg8_sweep_t3] batch \n"
        "complete: {'ok': True, 'completed': 100, 'total': 100, 'rounds': 0}\n"
        "2026-08-04 20:05:00 | INFO | src.cluster.driver | [leg8_sweep_t3] 97/100 done, 3 \n"
        "pending, round 2\n"
    )
    fails: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "driver_x.log").write_text(body, encoding="utf-8")
        saved, RUN = RUN, d
        try:
            owed, stale, dropped = owed_by_line()
        finally:
            RUN = saved
    got, drop = owed.get("x"), dropped.get("x")
    # 5 (B) + 3 (C) = 8. The pre-P306 code returns 8 + 8 (A) = 16 and drops nothing.
    if got != 8:
        fails.append(f"A+B+C: owed must be 8 (5 pending + 3 re-entered), got {got}")
    if drop != 8:
        fails.append(f"A: the completed batch's 8 phantom units must be REPORTED as dropped, got {drop}")
    if stale:
        fails.append(f"fixture must not be stale, got {stale}")
    for f in fails:
        print("SELFTEST FAIL " + f)
    print(f"selftest: {3 - len(fails)}/3 checks pass")
    return 1 if fails else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    raise SystemExit(main())
