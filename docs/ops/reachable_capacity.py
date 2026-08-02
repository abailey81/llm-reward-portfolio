"""REACHABLE capacity for RUN 4 -- joint placeability with the PAID allocations REMOVED.

WHY THIS EXISTS SEPARATELY FROM `joint_capacity.py` (RUN 13, 2026-08-02). `joint_capacity.py`
answers "how many of our jobs fit on pool d right now" and is correct as far as it goes, but it
counts every `node-d*` host -- including the 89 nodes that belong to PAID departmental allocations
(`@PAID_Economics` = ALL 24 d97a + ALL 8 d97b, `@PAID_MathsStatSci` = 44 of the d00a, plus BLIC,
MEDPHYS and hpc.10/11). Queue `Bran`'s per-hostgroup `user_lists` gate them, so we cannot be placed
there at all -- 22 probe jobs pinned to d97 never placed. The standing rule from that measurement:

    A capacity number computed over nodes you are not entitled to is not a capacity number.
    Filter @PAID_* FIRST.

This instrument therefore takes the PAID node list as DATA (generated from `qconf -shgrp`, not
hardcoded from memory) and reports capacity on the entitled set only. It is the number the C4
forecast must be built on, because C4 is the ONLY stage where the campaign is capacity-bound at all
-- during C1 we are demand-bound (measured 2026-08-02: 70 jobs running, 6 queued, 387 placeable).

Inputs (both plain text, both read-only, both produced on the cluster):
    --qhost  output of `qhost -F slots,memory,tmpfs`
    --paid   one hostname per line (short form, no domain)

The per-host test is the LIVE job spec, read off `qstat -j` on a running campaign job:
    -pe smp-[D]* 8   memory=1G per slot   tmpfs=1G   batch=true   minus the D15 host fence
so a host qualifies only if free_slots >= 8 AND free_memory >= 8G AND free_tmpfs >= 1G.

UNITS ARE PARSED EXPLICITLY. `qhost` prints "1.293T"/"150.5G"; a bare float cast reads 1.293T as
1.293 and loses three orders of magnitude -- the exact bug behind the false "11 of 348 hosts" claim.
An unparseable value is REPORTED, never guessed.
"""
from __future__ import annotations

import argparse
import re
import sys

MULT = {"K": 1 / 1024.0, "M": 1.0, "G": 1024.0, "T": 1024.0 ** 2, "P": 1024.0 ** 3}
FENCED = {"node-d00a-230", "node-d00b-024"}          # D15: the 6140 node + its sibling
# ⚠ CORRECTED 2026-08-02 (P187): the live C4 job asks **memory=2G PER SLOT**, not 1G. Read off
# `qstat -j` on eight running jobs, all agreeing. The 1G figure came from a SEARCH job (pack 1,
# threads 8) and does not describe the test/C4 lane that now dominates. Using 1G made every
# "placeable" count OPTIMISTIC wherever memory, not slots, is the binding resource.
NEED_SLOTS, NEED_MEM_MB, NEED_TMPFS_MB = 8, 8 * 2048.0, 1 * 1024.0
TRAININGS_PER_SLOT = 1.0     # test lane packs 8 trainings onto 8 slots at threads=1


def to_mb(text: str):
    t = text.strip()
    m = re.fullmatch(r"([0-9]*\.?[0-9]+)\s*([KMGTP])", t)
    if m:
        return float(m.group(1)) * MULT[m.group(2)]
    m = re.fullmatch(r"([0-9]*\.?[0-9]+)", t)        # unsuffixed => already MB (SGE prints 0.000)
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
unparsed: list[tuple[str, str, str]] = []
for line in open(args.qhost, encoding="utf-8", errors="replace"):
    line = line.rstrip("\n")
    h = re.match(r"^(node-\S+)", line)
    if h:
        host = h.group(1).split(".")[0]
        continue
    if not host:
        continue
    for key, store in (("hc:slots=", S), ("hc:memory=", M), ("hc:tmpfs=", T)):
        if key in line:
            raw = line.split(key)[1].strip()
            v = float(raw) if key == "hc:slots=" and re.fullmatch(r"[0-9.]+", raw) else to_mb(raw)
            if v is None:
                unparsed.append((host, key, raw))
            else:
                store[host] = v

hosts = sorted(set(S) | set(M) | set(T))
pool_d = [h for h in hosts if h.startswith("node-d")]

elig_all = elig_ok = 0
jobs_all = jobs_ok = 0
slots_all = slots_ok = 0.0
blocked = {"slots": 0, "memory": 0, "tmpfs": 0, "fenced": 0, "PAID": 0}

for h in pool_d:
    s, m, t = S.get(h, 0.0), M.get(h, 0.0), T.get(h, 0.0)
    fits = s >= NEED_SLOTS and m >= NEED_MEM_MB and t >= NEED_TMPFS_MB
    n_jobs = min(int(s // NEED_SLOTS), int(m // NEED_MEM_MB), int(t // NEED_TMPFS_MB)) if fits else 0
    if fits:
        elig_all += 1
        jobs_all += n_jobs
        slots_all += n_jobs * NEED_SLOTS
    if h in FENCED:
        blocked["fenced"] += 1
        continue
    if h in paid:
        blocked["PAID"] += 1
        continue
    if fits:
        elig_ok += 1
        jobs_ok += n_jobs
        slots_ok += n_jobs * NEED_SLOTS
    elif s < NEED_SLOTS:
        blocked["slots"] += 1
    elif m < NEED_MEM_MB:
        blocked["memory"] += 1
    else:
        blocked["tmpfs"] += 1

print(f"pool-d hosts seen            : {len(pool_d)}")
print(f"PAID hosts in the list       : {len(paid)}  (of which in pool d: {len([p for p in paid if p.startswith('node-d')])})")
if unparsed:
    print(f"!! UNPARSEABLE resource values: {len(unparsed)}  e.g. {unparsed[:3]}")
print()
print("               ENTITLED SET (PAID + D15 fence removed)   |   naive all-pool-d")
print(f"eligible hosts : {elig_ok:>6}                                  |  {elig_all:>6}")
print(f"placeable jobs : {jobs_ok:>6}                                  |  {jobs_all:>6}")
print(f"placeable slots: {slots_ok:>6.0f}                                  |  {slots_all:>6.0f}")
print()
print(f"=> CONCURRENT TRAININGS AVAILABLE NOW (1 slot each, threads=1): {slots_ok * TRAININGS_PER_SLOT:.0f}")
print()
print("first binding constraint on entitled hosts that CANNOT take one of our jobs:")
for k, v in blocked.items():
    print(f"   {k:8s}: {v}")
print()
print("READ IT LIKE THIS: compare `placeable jobs` with our QUEUED count. During C1 the campaign is")
print("DEMAND-bound -- the serial reflection chain simply has nothing more to submit -- so a large")
print("placeable number is the EXPECTED state and is not a capacity failure. The number matters at")
print("C4, which is the only stage that can consume it.")
