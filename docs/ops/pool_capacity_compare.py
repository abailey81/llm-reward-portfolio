"""FREE CAPACITY BY POOL — re-opening the pool-widening question on its OWN stated condition.

WHY, AND WHY THIS IS NOT RE-LITIGATION (RUN 13, 2026-08-02). `docs/DEFERRED_FIXES_RUN4.md`
"CONSIDERED AND DECLINED — pool widening d -> d,b" measured this on 2026-07-31 and declined it,
recording the decision so it "is not re-litigated from first principles a third time". That entry is
respected here: its CPU finding is REUSED, not re-derived —

    §46.2 established pool b is microarchitecture-IDENTICAL
    (both `Intel Xeon Gold 6240 @ 2.60GHz`), so there is no CRN hazard in principle

— which is exactly the fact a fresh probe would have spent an hour rediscovering.

What re-opens it is the entry's OWN condition, stated verbatim:

    Re-open only if pool d's own capacity becomes the binding constraint
    — it is not; our constraint was priority (§54) and is now queue position.

**That condition is now MET.** On 2026-07-31 pool d had 272 usable hosts and 2,472 free slots. Measured
2026-08-02 with C4 live: the ENTITLED d set is 206 hosts / 7,416 slots, of which **we hold 23 %, other
users hold 63 %, and only 13 % is free** — an absolute ceiling of ~2,713 cores even if we took every
free slot. Pool d's own capacity IS the constraint now, and the decline was explicitly conditional on
it not being.

This script therefore re-measures what the decline was priced against — free capacity per pool, on the
ENTITLED set only — so the decision is re-taken on today's numbers rather than on July's.

⚠ IT REPORTS. IT CHANGES NOTHING. Pool widening is a launch-flag change requiring a rolling restart of
every line, and D15 is the standing reminder that ONE heterogeneous host cost four archived records.
"""
from __future__ import annotations

import argparse
import re
from collections import defaultdict

MULT = {"K": 1 / 1024.0, "M": 1.0, "G": 1024.0, "T": 1024.0 ** 2, "P": 1024.0 ** 3}
FENCED = {"node-d00a-230", "node-d00b-024"}
# ⚠ CORRECTED 2026-08-02 (P187): the live C4 job asks **memory=2G PER SLOT**, not 1G. Read off
# `qstat -j` on eight running jobs, all agreeing. The 1G figure came from a SEARCH job (pack 1,
# threads 8) and does not describe the test/C4 lane that now dominates. Using 1G made every
# "placeable" count OPTIMISTIC wherever memory, not slots, is the binding resource.
NEED_SLOTS, NEED_MEM_MB, NEED_TMPFS_MB = 8, 8 * 2048.0, 1024.0

# Topology measured 2026-08-02 from `qhost`. Only pools whose hosts are 36 NCPU / 2 sockets can even
# be candidates: t00a is 64-core single-socket and u00a/v00a are 48-core, so they are a DIFFERENT
# microarchitecture and would break the per-seed substrate homogeneity the C3 gate enforces.
SAME_TOPOLOGY = {"d00a", "d00b", "b00a", "e00a", "e96a", "f00a", "l00a"}
GPU_POOLS = {"l00a"}          # `qconf -se node-l00a-001` -> gpu=4; a GPU pool is not our lane


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

by_pool: dict[str, dict[str, float]] = defaultdict(lambda: {"hosts": 0, "free": 0.0, "jobs": 0,
                                                            "paid": 0, "eligible": 0})
for h in sorted(set(S) | set(M) | set(T)):
    m = re.match(r"node-([a-z]\d+[a-z])", h)
    if not m:
        continue
    p = m.group(1)
    row = by_pool[p]
    row["hosts"] += 1
    if h in paid or h in FENCED:
        row["paid"] += 1
        continue
    s, mem, t = S.get(h, 0.0), M.get(h, 0.0), T.get(h, 0.0)
    row["free"] += s
    if s >= NEED_SLOTS and mem >= NEED_MEM_MB and t >= NEED_TMPFS_MB:
        row["eligible"] += 1
        row["jobs"] += min(int(s // NEED_SLOTS), int(mem // NEED_MEM_MB))

print(f"{'pool':>6} {'hosts':>6} {'paid/fenced':>12} {'free slots':>11} {'8-slot jobs':>12} "
      f"{'cores':>7}  note")
tot_extra_cores = 0
for p in sorted(by_pool):
    r = by_pool[p]
    cores = r["jobs"] * NEED_SLOTS
    if p in ("d00a", "d00b"):
        note = "OURS TODAY"
    elif p not in SAME_TOPOLOGY:
        note = "DIFFERENT microarchitecture (36-core/2-socket is the only match) -- REFUSED"
    elif p in GPU_POOLS:
        note = "GPU pool -- not our lane"
    else:
        note = "CANDIDATE: same topology, non-PAID"
        tot_extra_cores += cores
    print(f"{p:>6} {r['hosts']:>6} {r['paid']:>12} {r['free']:>11.0f} {r['jobs']:>12} "
          f"{cores:>7}  {note}")

d_cores = (by_pool['d00a']['jobs'] + by_pool['d00b']['jobs']) * NEED_SLOTS
print()
print(f"pool d free capacity we could take RIGHT NOW      : {d_cores:,} cores")
print(f"CANDIDATE pools would add                        : {tot_extra_cores:,} cores")
if d_cores:
    print(f"                                        i.e. a {100.0 * tot_extra_cores / d_cores:.0f} % increase "
          f"on what pool d itself can currently give us")
print()
print("DECIDE ON TODAY'S NUMBERS. The 2026-07-31 decline priced widening at +4 % when pool d had 2,472")
print("free slots; it also said to re-open if pool d's own capacity became binding, which it now is.")
print("The CPU question is already SETTLED for pool b (§46.2: identical Xeon Gold 6240) and is OPEN")
print("for e00a/f00a -- same topology, never probed. D15 stands: one heterogeneous host cost four")
print("archived records, so any widening needs the substrate census re-run immediately afterwards.")
