"""PLACEABLE capacity per pool, from QUEUE-INSTANCE state — the correction to `pool_capacity_compare.py`.

★ WHY THIS EXISTS (RUN 14, 2026-08-02). `pool_capacity_compare.py` reads free slots from
`qhost -F slots`, i.e. from the HOST's resource counter. That counter says nothing about whether the
queue instance on that host will ACCEPT a job. Measured on pool b the same minute:

    qhost  free slots on b00a ............ 279
    enabled queue instances on b00a ...... 137   <- 4 hosts are `d`/`adu` (disabled/alarm/unreachable)
                                                    and their 144 slots can never be given to us

So the instrument that the D30 pool-widening decision rests on OVERSTATES usable capacity by every
disabled host it meets — 51 % on pool b. It is the same family of error as P187 (a resource figure
read off the wrong object) and it points the same way every time: OPTIMISTIC. This module reads the
authoritative object instead — `qstat -f`, which reports the queue instance and its STATE.

★ AND IT PRICES FRAGMENTATION, WHICH IS THE SECOND HALF OF THE ANSWER. A pack-8 training needs EIGHT
free slots ON ONE HOST. A pool with 137 free slots spread one-and-two at a time across twelve hosts
can place ZERO of them. So free slots is the wrong unit entirely: the unit that predicts throughput
is PLACEABLE JOBS = sum over hosts of floor(free_on_host / pack), and this reports both so the gap
between them is visible rather than assumed.

★ STATE LETTERS THAT MEAN "NOT OURS" (SGE queue instance states):
    a  alarm (load threshold exceeded)      d  disabled by an administrator
    u  unreachable (sge_execd not responding)  E  error
    C  calendar-suspended                   s/S  suspended
A queue instance carrying ANY of these cannot start our job now, so its free slots are excluded.
`o` (orphaned) is also excluded. Anything else counts.

⚠ IT REPORTS. IT CHANGES NOTHING — no qsub, no qalter, no qdel. Run it before and after any pool
change; a capacity claim that was not re-derived after the change is an assumption.

★ THE TWO INPUTS DO DIFFERENT JOBS, AND SWAPPING THEM IS A MEASURED TRAP I FELL INTO FIRST.
`qstat -f` prints one row per HOST *per QUEUE* (Bran, Bronn, Brienne, Catelyn, …), and the slots are
the SAME physical slots seen through each queue. Reading free slots from these rows overcounts
enormously — taking the most-idle queue instance per host reported **d00a as 7,264 free cores**, which
is more than the pool physically holds. Verified against the host consumable:

    node-e00a-003:  Bran 0/13/36  ->  23 free      qhost hc:slots = 23   <- Bran agrees
                    Bronn 0/0/36  ->  36 free                            <- and this is FICTION

So free slots come from `qhost -F slots` (`hc:slots`, the authoritative per-HOST consumable) and
`qstat -f` is used ONLY to decide whether a host's queue instances are in a state that can accept
work. Each input answers the question it is actually authoritative for.

USAGE
    ssh myriad "qhost -F slots" > /tmp/qh.txt
    ssh myriad "qstat -f"       > /tmp/qf.txt
    python docs/ops/placeable_capacity.py --qhost /tmp/qh.txt --qstat /tmp/qf.txt

    --pack N   slots per training job (default 8, the live supervisor setting)
    --pools    comma-separated pool prefixes to report (default: every pool seen)
    --paid     optional file of PAID hostnames (one per line) to exclude as unreachable
"""
from __future__ import annotations

import argparse
import re
from collections import defaultdict

# A queue instance carrying any of these letters cannot accept our job right now.
UNUSABLE_STATES = set("adusSECo")

# `qstat -f` queue-instance row:
#   Bran@node-b00a-013.myriad.ucl. BIP   0/13/36        2.40     lx-amd64      adu
# fields: queuename qtype resv/used/tot load_avg arch [states]
ROW = re.compile(
    r"^(?P<queue>[A-Za-z0-9_.-]+)@(?P<host>node-[A-Za-z0-9-]+)\S*\s+"
    r"(?P<qtype>\S+)\s+"
    r"(?P<resv>\d+)/(?P<used>\d+)/(?P<tot>\d+)\s+"
    r"(?P<rest>.*)$"
)


def pool_of(host: str) -> str | None:
    """`node-b00a-013` -> `b00a`. Returns None for a name that is not pool-shaped."""
    m = re.match(r"node-([a-z]\d{2}[a-z])-", host)
    return m.group(1) if m else None


def states_of(rest: str) -> str:
    """The trailing state letters of a `qstat -f` row, or "" when the column is absent.

    The row's tail is `load_avg arch [states]`; load_avg may be `-NA-` on an unreachable host, and
    the states column is simply MISSING on a healthy instance. So the state token is the last field
    only when it is pure state letters — testing that explicitly rather than positionally, because a
    positional read silently turns the `arch` value (`lx-amd64`) into a state string on healthy rows.
    """
    toks = rest.split()
    if not toks:
        return ""
    last = toks[-1]
    return last if last and all(c in "adusSECoirRwqhtxpz" for c in last) and "-" not in last else ""


_MULT = {"K": 1.0 / 1024, "M": 1.0, "G": 1024.0, "T": 1024.0 ** 2, "P": 1024.0 ** 3}


def _to_mb(tok: str) -> float | None:
    """`188.4G` -> MB. Units are parsed EXPLICITLY: a bare float cast reads `1.293T` as 1.293."""
    tok = tok.strip()
    m = re.fullmatch(r"([0-9]*\.?[0-9]+)\s*([KMGTP])", tok)
    if m:
        return float(m.group(1)) * _MULT[m.group(2)]
    m = re.fullmatch(r"([0-9]*\.?[0-9]+)", tok)
    return float(m.group(1)) if m else None


def parse_qhost(path: str) -> dict[str, dict[str, float]]:
    """{host: {slots, memory_mb, tmpfs_mb}} from `qhost -F slots,memory,tmpfs`.

    A host with NO `hc:` line for a resource is recorded as 0 rather than skipped — dropping it
    would silently shrink the denominator and make every pool look better than it is.
    """
    out: dict[str, dict[str, float]] = {}
    host: str | None = None
    for line in open(path, encoding="utf-8", errors="replace"):
        m = re.match(r"^(node-\S+)", line.rstrip("\n"))
        if m:
            host = m.group(1).split(".")[0]
            out.setdefault(host, {"slots": 0.0, "memory_mb": 0.0, "tmpfs_mb": 0.0})
            continue
        if not host:
            continue
        for key, field in (("hc:slots=", "slots"), ("hc:memory=", "memory_mb"),
                           ("hc:tmpfs=", "tmpfs_mb")):
            if key in line:
                v = _to_mb(line.split(key)[1])
                if v is not None:
                    out[host][field] = v
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qhost", required=True, help="file holding the output of `qhost -F slots`")
    ap.add_argument("--qstat", required=True, help="file holding the output of `qstat -f`")
    ap.add_argument("--pack", type=int, default=8, help="slots per training job (live default 8)")
    ap.add_argument("--pools", default="", help="comma-separated pool prefixes (default: all)")
    ap.add_argument("--paid", default="", help="optional file of PAID hostnames to exclude")
    # P187: the live C4 job asks memory=2G PER SLOT and tmpfs=1G per JOB (read off `qstat -j` on
    # eight running jobs, all agreeing). Gating on slots alone reports capacity that memory forbids.
    ap.add_argument("--mem-per-slot-mb", type=float, default=2048.0)
    ap.add_argument("--tmpfs-per-job-mb", type=float, default=1024.0)
    args = ap.parse_args()

    want = {p.strip() for p in args.pools.split(",") if p.strip()}
    paid = set()
    if args.paid:
        paid = {ln.strip() for ln in open(args.paid, encoding="utf-8") if ln.strip()}

    qhost = parse_qhost(args.qhost)

    # A host is USABLE if at least one of its queue instances is in an accepting state. Blocked
    # states are per-instance, so requiring EVERY instance to be clean would wrongly condemn a host
    # whose unrelated queue happens to be disabled.
    host_pool: dict[str, str] = {}
    host_blocked: dict[str, bool] = {}
    seen_rows = 0

    with open(args.qstat, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = ROW.match(line.rstrip("\n"))
            if not m:
                continue
            seen_rows += 1
            host = m.group("host")
            pool = pool_of(host)
            if pool is None or (want and pool not in want):
                continue
            st = states_of(m.group("rest"))
            blocked = bool(set(st) & UNUSABLE_STATES)
            host_pool[host] = pool
            # any accepting instance clears the host
            host_blocked[host] = host_blocked.get(host, True) and blocked

    if not seen_rows:
        raise SystemExit("parsed 0 queue-instance rows — is that file really `qstat -f` output?")

    agg: dict[str, dict[str, int]] = defaultdict(
        lambda: {"hosts": 0, "blocked": 0, "free": 0, "placeable": 0, "frag": 0,
                 "slots_only": 0, "memcapped": 0}
    )
    need_mem = args.mem_per_slot_mb * args.pack
    for host, pool in host_pool.items():
        row = agg[pool]
        row["hosts"] += 1
        if host_blocked.get(host) or host in paid:
            row["blocked"] += 1
            continue
        h = qhost.get(host, {"slots": 0.0, "memory_mb": 0.0, "tmpfs_mb": 0.0})
        free = int(h["slots"])
        row["free"] += free
        by_slots = free // args.pack
        by_mem = int(h["memory_mb"] // need_mem) if need_mem > 0 else by_slots
        by_tmp = int(h["tmpfs_mb"] // args.tmpfs_per_job_mb) if args.tmpfs_per_job_mb > 0 else by_slots
        jobs = min(by_slots, by_mem, by_tmp)
        row["slots_only"] += by_slots
        row["placeable"] += jobs
        row["memcapped"] += by_slots - jobs           # jobs the SLOTS allow but memory/tmpfs forbid
        row["frag"] += free - by_slots * args.pack    # slots free but too few on this host to use

    print(f"PLACEABLE CAPACITY at pack={args.pack}  "
          f"(mem {args.mem_per_slot_mb:.0f}MB/slot, tmpfs {args.tmpfs_per_job_mb:.0f}MB/job)")
    print(f"{'pool':>6} {'hosts':>6} {'blockd':>7} {'free':>6} {'strand':>7} "
          f"{'byslot':>7} {'memcap':>7} {'jobs':>6} {'CORES':>7}")
    tot_cores = 0
    for pool in sorted(agg):
        r = agg[pool]
        cores = r["placeable"] * args.pack
        tot_cores += cores
        print(f"{pool:>6} {r['hosts']:>6} {r['blocked']:>7} {r['free']:>6} {r['frag']:>7} "
              f"{r['slots_only']:>7} {r['memcapped']:>7} {r['placeable']:>6} {cores:>7}")
    print(f"{'TOTAL':>6} {'':>6} {'':>7} {'':>6} {'':>7} {'':>7} {'':>7} {'':>6} {tot_cores:>7}")
    print()
    print("'free'   = slots free on ENABLED queue instances (disabled/alarm/unreachable excluded)")
    print("'strand' = free slots on hosts holding FEWER than one pack — real, unusable at this width.")
    print("'byslot' = jobs the SLOTS alone would allow; 'memcap' = how many of those memory/tmpfs")
    print("           forbids. A large memcap means pack width is NOT the binding lever here.")
    print("'CORES'  = placeable jobs x pack — the only figure that predicts throughput.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
