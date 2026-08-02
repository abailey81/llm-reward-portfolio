"""PER-LINE CRITICAL PATH for RUN 4 -- where the COMMON RUNG actually is, and what gates it.

WHY (RUN 13, 2026-08-02). Under R101 the reported result is the COMMON rung: a MINIMUM over the 11
supervised lines, not a sum. That single fact makes almost every intuitive throughput question the
wrong one -- capacity handed to a LEADING line is worth exactly zero to the reported number, and the
only quantity that matters is how long the SLOWEST line still needs. Tamer's live question ("we are
at a very low amount of cores, 520 is unacceptable") is answered by this table and not by a slot
count: on 2026-08-02 the campaign held 560 slots with 6 jobs queued and 864 entitled slots free, so
it was DEMAND-bound, and demand is set by the serial reflection chain on the laggard lines.

WHAT IT SHOWS, per line: arms frozen / arms present, the stage, how many search and test records the
line holds, and the block the driver is currently waiting on.

READ `BLK_AGE_H` CAREFULLY -- it is the age of the BLOCK, which spans every requeue, NOT the age of
the current attempt. leg4's `placebo_shuffled_test` reads 28.7 h here while its array is alive and
about an hour from finishing: a healthy round-1 retry, not a stall. This table therefore SAYS "long
block" and defers the verdict to `vanished_array_watch.py`, which asks the cluster whether the block's
arrays still exist. Reporting a live retry as STALLED would be exactly the false alarm this project
keeps paying for.

BLIND: reads directory structure, driver-log block names and record COUNTS. No outcome value is
read -- not one metric, not one return series.
"""
from __future__ import annotations

import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "outputs/campaign_cluster_run4")
P99_TRAINING_H = 10.8      # measured: 1,484 search records, p99 wall-clock
STALL_H = 14.0             # a block older than this is past the h_rt wall of its own trainings

LINE_OF_LOG = re.compile(r"^driver_(.+)\.log$")
BLOCK = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d).*\[([a-zA-Z0-9_.\-]+)\]\s+(\d+)/(\d+) done")


def count_records(p: Path) -> int:
    if not p.is_dir():
        return 0
    return sum(1 for _ in p.rglob("record.json"))


def suffix_for(log_name: str) -> str:
    """Map driver_<model>.log to the archive suffix used by that line's roots."""
    m = LINE_OF_LOG.match(log_name)
    tag = m.group(1) if m else log_name
    if tag == "core":
        return ""
    if tag == "h3":
        return "_h3_singleshot"
    return "_leg_" + tag.replace("-", "_").replace(".", "_")


rows = []
now = time.time()
for log in sorted(ROOT.glob("driver_*.log")):
    sfx = suffix_for(log.name)
    frozen_root = ROOT / f"frozen{sfx}"
    search_root = ROOT / f"search{sfx}"
    test_root = ROOT / f"test{sfx}"
    n_frozen = len([d for d in frozen_root.iterdir() if d.is_dir()]) if frozen_root.is_dir() else 0
    n_search_arms = len([d for d in search_root.iterdir() if d.is_dir()]) if search_root.is_dir() else 0
    n_test = count_records(test_root)
    n_srch = count_records(search_root)

    # The driver re-prints its CURRENT waiting block every poll; the newest such line is the state.
    cur, cur_first, cur_last, done, total = "-", None, None, 0, 0
    try:
        txt = log.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        txt = []
    firsts: dict[str, str] = {}
    for ln in txt:
        m = BLOCK.match(ln)
        if m:
            firsts.setdefault(m.group(2), m.group(1))
            cur, cur_first, cur_last = m.group(2), firsts[m.group(2)], m.group(1)
            done, total = int(m.group(3)), int(m.group(4))
    age_h = None
    last_seen_h = None
    if cur_first:
        try:
            # Driver logs carry the driver host's LOCAL time and this script runs on that same host,
            # so compare NAIVE-to-naive. Stamping them UTC produced a NEGATIVE age for the core line
            # (local 00:24 read as 00:24 UTC while now was 23:3x UTC) -- a wrong sign is the cheapest
            # possible tell that a clock convention is wrong, and it was mine.
            age_h = (now - datetime.strptime(cur_first, "%Y-%m-%d %H:%M:%S").timestamp()) / 3600.0
            last_seen_h = (now - datetime.strptime(cur_last, "%Y-%m-%d %H:%M:%S").timestamp()) / 3600.0
        except Exception:
            age_h = last_seen_h = None
    stage = "C1-search" if cur.endswith(tuple(f"_g{i}" for i in range(9))) else (
        "C1-test" if cur.endswith("_test") else ("C2-pair" if "h2_pair" in cur else
                                                 ("C4-sweep" if cur.startswith("sweep") else "?")))
    # A line the driver has stopped REPORTING is not stalled -- it is finished (h3 completed 568/568
    # and its last block line is hours old, which the first version of this script cried "STALLED?"
    # over). Only a block the driver is STILL polling can be stalled, and only relative to the p99
    # training wall. Three values, not two: done / live-and-slow / live-and-stuck.
    if last_seen_h is not None and last_seen_h > 0.5:
        verdict = "idle (driver no longer polling this block)"
    elif age_h is not None and age_h > STALL_H:
        # AGE_H is the age of the BLOCK, which spans every requeue -- NOT the age of the current
        # attempt. leg4's `placebo_shuffled_test` read 28.7 h here while its array 67608 was alive and
        # 1.2 h from finishing, i.e. a healthy round-1 retry. Calling that "STALLED?" would be a false
        # alarm of exactly the kind this project keeps paying for, so the honest label names what was
        # actually measured and points at the instrument that CAN decide.
        verdict = "long block (spans retries) -- run vanished_array_watch.py to decide"
    else:
        verdict = "ok"
    rows.append((log.name.replace("driver_", "").replace(".log", ""), n_frozen, n_search_arms,
                 n_srch, n_test, stage, cur, f"{done}/{total}",
                 ("%.1f" % age_h) if age_h is not None else "-", verdict))

hdr = ("LINE", "FROZ", "ARMS", "SRCH_REC", "TEST_REC", "STAGE", "CURRENT BLOCK", "DONE", "BLK_AGE_H", "VERDICT")
print("%-18s %5s %5s %9s %9s %-10s %-46s %8s %7s %s" % hdr)
for r in sorted(rows, key=lambda x: (x[1], -float(x[8]) if x[8] != "-" else 0)):
    print("%-18s %5d %5d %9d %9d %-10s %-46s %8s %7s %s" % r)
print()
print(f"stall threshold {STALL_H} h  (p99 measured training wall = {P99_TRAINING_H} h; h_rt = 15.0 h)")
print("A line is on the CRITICAL PATH if its arms are not all frozen: the common rung cannot rise")
print("above the slowest line, so capacity spent elsewhere does not move the reported result.")
