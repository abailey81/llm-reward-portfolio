"""SLOT FRAGMENTATION on the entitled set — can a SMALLER job shape place where ours cannot?

WHY (RUN 13, 2026-08-02, second capacity pass). C4 is live and the campaign now has REAL demand:
526 jobs queued against 216 running and 1,728 cores held. So the earlier answer ("demand-bound") has
expired and the question is a different one -- why is the scheduler giving us 1,728 and not more.

One candidate explanation is invisible to every free-slot TOTAL: our jobs ask for `-pe smp 8`, which
needs EIGHT free slots ON ONE HOST simultaneously. If the entitled hosts' free capacity is fragmented
into chunks smaller than 8, a large aggregate free-slot count coexists with nowhere to put a job.
That would make the total a mirage, exactly as "a capacity number computed over nodes you are not
entitled to is not a capacity number" made the naive pool-d total a mirage.

THE TEST, and it is decisive either way. For each candidate pack width P (which for the TEST lane is
also the slot request, because `threads = 1` there), count how many jobs would place right now. If
the counts are roughly proportional to 8/P the free space is CONTIGUOUS and shrinking the pack buys
nothing; if smaller widths place disproportionately MORE jobs, the free space is FRAGMENTED and the
pack width is costing us placements.

⚠ WHY PACK WIDTH IS EVEN A CANDIDATE — the arithmetic does NOT change. In the test lane every
training runs at `threads = 1` regardless of how many are packed (measured: pack 8 -> 12.8 steps/s,
pack 6 -> 13.3, i.e. flat), and the archived `determinism_env` is `OMP_NUM_THREADS=1` on all 1,446
sealed-test records. A narrower pack is the SAME per-training arithmetic in a smaller box. It is a
DISPATCH change, the same class as D27 -- not a science change.

⚠ AND THE COST THAT MUST BE PRICED WITH IT: halving the pack doubles the JOB count, and `max_u_jobs`
is 1000. This script therefore reports the job count each width implies, so the two constraints are
weighed together rather than one at a time.

Reads `qhost -F slots,memory,tmpfs` and a PAID node list. Units are parsed explicitly -- a bare cast
reads "1.293T" as 1.293 and loses three orders of magnitude.
"""
from __future__ import annotations

import argparse
import re

MULT = {"K": 1 / 1024.0, "M": 1.0, "G": 1024.0, "T": 1024.0 ** 2, "P": 1024.0 ** 3}
FENCED = {"node-d00a-230", "node-d00b-024"}      # D15
MEM_PER_SLOT_MB = 1024.0                          # memory=1G per slot, from the live `qstat -j`
TMPFS_MB = 1024.0                                 # tmpfs=1G per job


def to_mb(t: str):
    t = t.strip()
    m = re.fullmatch(r"([0-9]*\.?[0-9]+)\s*([KMGTP])", t)
    if m:
        return float(m.group(1)) * MULT[m.group(2)]
    m = re.fullmatch(r"([0-9]*\.?[0-9]+)", t)
    return float(m.group(1)) if m else None


ap = argparse.ArgumentParser()
ap.add_argument("--qhost", required=True)
ap.add_argument("--paid", required=True)
args = ap.parse_args()

paid = {ln.strip() for ln in open(args.paid, encoding="utf-8") if ln.strip()}

host = None
S: dict[str, float] = {}
M: dict[str, float] = {}
T: dict[str, float] = {}
for line in open(args.qhost, encoding="utf-8", errors="replace"):
    h = re.match(r"^(node-\S+)", line.rstrip("\n"))
    if h:
        host = h.group(1).split(".")[0]
        continue
    if not host:
        continue
    for key, store in (("hc:slots=", S), ("hc:memory=", M), ("hc:tmpfs=", T)):
        if key in line:
            raw = line.split(key)[1].strip()
            v = float(raw) if key == "hc:slots=" and re.fullmatch(r"[0-9.]+", raw) else to_mb(raw)
            if v is not None:
                store[host] = v

entitled = [h for h in sorted(set(S) | set(M) | set(T))
            if h.startswith("node-d") and h not in paid and h not in FENCED]

print(f"entitled pool-d hosts: {len(entitled)}")
print()
print("FREE-SLOT HISTOGRAM on the entitled set (this is where fragmentation would show)")
buckets = {"0": 0, "1-3": 0, "4-7": 0, "8-15": 0, "16-35": 0, "36": 0}
free_total = 0.0
for h in entitled:
    s = int(S.get(h, 0.0))
    free_total += s
    if s == 0:
        buckets["0"] += 1
    elif s <= 3:
        buckets["1-3"] += 1
    elif s <= 7:
        buckets["4-7"] += 1
    elif s <= 15:
        buckets["8-15"] += 1
    elif s <= 35:
        buckets["16-35"] += 1
    else:
        buckets["36"] += 1
for k, v in buckets.items():
    print(f"   hosts with {k:>6} free slots : {v}")
print(f"   TOTAL free slots on the entitled set: {free_total:.0f}")
print()

print("PLACEABLE JOBS BY PACK WIDTH (test lane: slots == pack, because threads = 1)")
print(f"{'pack':>5} {'slots/job':>10} {'jobs placeable':>15} {'trainings':>11} {'vs pack8':>9}  note")
base = None
for pack in (8, 6, 4, 2, 1):
    jobs = 0
    for h in entitled:
        s, m, t = S.get(h, 0.0), M.get(h, 0.0), T.get(h, 0.0)
        if t < TMPFS_MB:
            continue
        jobs += min(int(s // pack), int(m // (MEM_PER_SLOT_MB * pack)))
    trainings = jobs * pack
    if base is None:
        base = trainings
    ratio = (trainings / base) if base else 0.0
    note = ""
    if pack != 8:
        note = ("MORE trainings placeable -- FRAGMENTED" if ratio > 1.05
                else "no gain -- free space is CONTIGUOUS at width 8")
    print(f"{pack:>5} {pack:>10} {jobs:>15,} {trainings:>11,} {ratio:>8.2f}x  {note}")
print()
print("HOW TO READ IT. If every width places about the SAME number of TRAININGS, the free space is")
print("contiguous and the pack width is not costing us anything -- leave it alone. If narrower packs")
print("place materially more, the 8-slot request is the constraint. Weigh any change against")
print("max_u_jobs = 1000: halving the pack doubles the job count for the same work.")
