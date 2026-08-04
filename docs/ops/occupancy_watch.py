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
PROGRESS = re.compile(r"\[([A-Za-z0-9_.\-]+)\]\s+(\d+)/(\d+) done,\s*(\d+) pending", re.M)
#: A driver line is only current if it is recent; a dead driver's last line must not count as owed.
STALE_LOG_MIN = 30.0


def owed_by_line() -> tuple[dict[str, int], list[str]]:
    """Units each line's driver currently says are pending, from the LAST line per batch."""
    owed: dict[str, int] = {}
    stale: list[str] = []
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
        last: dict[str, int] = {}
        for m in PROGRESS.finditer(text.replace("\n", " ")):
            last[m.group(1)] = int(m.group(4))
        owed[line] = sum(last.values())
    return owed, stale


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

    owed, stale = owed_by_line()
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


if __name__ == "__main__":
    raise SystemExit(main())
