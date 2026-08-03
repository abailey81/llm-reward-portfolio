"""MEASURE genuinely-free pool-d capacity: SLOTS and MEMORY, per host, correctly.

WHY NOT `qstat -f`: it lists every host under ~35 named queue instances, so filtering on `node-d`
multi-counts and produced "431,382 free slots" on a ~21,600-core cluster (P30, and P32 when I
repeated it). The HOST CONSUMABLE (`qhost -F <resource>`) is one line per host and is the quantity
the scheduler actually decrements.

WHY THE UNIT PARSER: `qhost` prints suffixed values (`1.293T`, `150.5G`). A bare `$1+0` reads
"1.293T" as 1.293 and silently loses three orders of magnitude -- that is the exact bug that produced
record s.60's false "11 of 348 hosts" claim, and I reproduced it myself (P33). Suffixes are parsed
explicitly here and an unparseable value is REPORTED, never guessed.

Reads stdin: the raw output of `qhost -F slots,memory`.

SANITY BOUNDS (checked before anything is printed as a result):
  pool d = 294 hosts x 36 slots = 10,584 slots, and 294 x ~160 G = ~47 TB of memory.
Any total exceeding those is an instrument error, not a discovery.
"""
import re
import sys

MULT = {"K": 1 / 1024.0, "M": 1.0, "G": 1024.0, "T": 1024.0 ** 2, "P": 1024.0 ** 3}
HOST_SLOTS = 36
EXPECT_HOSTS = 294


def to_mb(text):
    m = re.fullmatch(r"([0-9]*\.?[0-9]+)\s*([KMGTP])", text.strip())
    return float(m.group(1)) * MULT[m.group(2)] if m else None


def to_num(text):
    m = re.fullmatch(r"([0-9]*\.?[0-9]+)", text.strip())
    return float(m.group(1)) if m else None


host = None
slots, mem = {}, {}
unparsed = []
for line in sys.stdin:
    line = line.rstrip("\n")
    m = re.match(r"^(node-d\S+)", line)
    if m:
        host = m.group(1)
        continue
    if not host:
        continue
    if "hc:slots=" in line:
        v = to_num(line.split("hc:slots=")[1])
        (slots.__setitem__(host, v) if v is not None else unparsed.append((host, "slots", line.strip())))
    elif "hc:memory=" in line:
        raw = line.split("hc:memory=")[1].strip()
        v = to_mb(raw)
        (mem.__setitem__(host, v) if v is not None else unparsed.append((host, "memory", raw)))

print(f"pool-d hosts reporting free SLOTS : {len(slots)}")
print(f"pool-d hosts reporting free MEMORY: {len(mem)}")
if unparsed:
    print(f"UNPARSED (reported, not guessed): {len(unparsed)} e.g. {unparsed[:3]}")
print()

if slots:
    tot_free = sum(slots.values())
    ceiling = EXPECT_HOSTS * HOST_SLOTS
    print(f"FREE SLOTS total : {tot_free:,.0f}   (pool-d ceiling {ceiling:,})")
    if tot_free > ceiling:
        print("  *** EXCEEDS THE CEILING -- INSTRUMENT ERROR, DISCARDING ***")
    else:
        # our search jobs ask for 8 slots each; C4 jobs ask 8 as well (pack 8 x 1 core, OMP=1)
        placeable = sum(int(v // 8) for v in slots.values())
        hosts_with_8 = sum(1 for v in slots.values() if v >= 8)
        print(f"  hosts with >= 8 free slots : {hosts_with_8} of {len(slots)}")
        print(f"  8-slot jobs that could be placed RIGHT NOW on slots alone: {placeable}")
        busy = sum(1 for v in slots.values() if v == 0)
        print(f"  hosts fully saturated (0 free): {busy}")

if mem:
    tot_mb = sum(mem.values())
    print()
    print(f"FREE MEMORY total: {tot_mb/1024/1024:,.1f} TB")
    # C4 sizing: pack 8, cores 8, mem 2G/slot -> 16 GB per job; 1,000-job cap
    per_job_gb = 16.0
    by_mem = sum(int(v / 1024 // per_job_gb) for v in mem.values())
    print(f"  C4 jobs (16 GB each) placeable on MEMORY alone: {by_mem:,}")
    print("  C4 target is min(1000 job cap, slots, memory)")
