"""JOINT placeability: how many of OUR jobs could be dispatched right now?

A single-resource free count OVERSTATES placeability, because a job needs every constraint satisfied
on the SAME host at the SAME moment. Our search job asks for, per `qstat -j` on a live queued job:
    snx=1, tmpfs=1G, memory=1G (per slot), h_rt=54000, -pe smp 8, pool d, minus the D15 host fence.
So the joint test per host is: free_slots >= 8  AND  free_memory >= 8 G  AND  free_tmpfs >= 1 G.

Reads stdin: `qhost -F slots,memory,tmpfs`.

Units are parsed EXPLICITLY (a bare `$1+0` reads "1.293T" as 1.293 -- the bug behind record s.60's
false claim, which I also reproduced myself as P33). A bare "0.000" means genuinely zero free and is
treated as 0, not as unparseable.
"""
import re
import sys

MULT = {"K": 1 / 1024.0, "M": 1.0, "G": 1024.0, "T": 1024.0 ** 2, "P": 1024.0 ** 3}
FENCED = {"node-d00a-230", "node-d00b-024"}          # D15
NEED_SLOTS, NEED_MEM_MB, NEED_TMPFS_MB = 8, 8 * 1024.0, 1 * 1024.0


def to_mb(text):
    t = text.strip()
    m = re.fullmatch(r"([0-9]*\.?[0-9]+)\s*([KMGTP])", t)
    if m:
        return float(m.group(1)) * MULT[m.group(2)]
    m = re.fullmatch(r"([0-9]*\.?[0-9]+)", t)          # unsuffixed => already MB (SGE prints 0.000)
    return float(m.group(1)) if m else None


host = None
S, M, T = {}, {}, {}
for line in sys.stdin:
    line = line.rstrip("\n")
    h = re.match(r"^(node-d\S+)", line)
    if h:
        host = h.group(1)
        continue
    if not host:
        continue
    for key, store, conv in (("hc:slots=", S, lambda x: float(x)),
                             ("hc:memory=", M, to_mb),
                             ("hc:tmpfs=", T, to_mb)):
        if key in line:
            try:
                v = conv(line.split(key)[1].strip())
            except Exception:
                v = None
            if v is not None:
                store[host] = v

hosts = sorted(set(S) | set(M) | set(T))
print(f"pool-d hosts seen: {len(hosts)}")

elig = 0
capacity_jobs = 0
blocked = {"slots": 0, "memory": 0, "tmpfs": 0, "fenced": 0}
for h in hosts:
    if h in FENCED:
        blocked["fenced"] += 1
        continue
    s, m, t = S.get(h, 0.0), M.get(h, 0.0), T.get(h, 0.0)
    ok_s, ok_m, ok_t = s >= NEED_SLOTS, m >= NEED_MEM_MB, t >= NEED_TMPFS_MB
    if ok_s and ok_m and ok_t:
        elig += 1
        capacity_jobs += min(int(s // NEED_SLOTS), int(m // NEED_MEM_MB), int(t // NEED_TMPFS_MB))
    else:
        if not ok_s:
            blocked["slots"] += 1
        elif not ok_m:
            blocked["memory"] += 1
        elif not ok_t:
            blocked["tmpfs"] += 1

print()
print(f"hosts that could take one of OUR jobs RIGHT NOW (all constraints jointly): {elig}")
print(f"TOTAL such jobs placeable right now                                     : {capacity_jobs}")
print()
print("first binding constraint on the hosts that CANNOT take one:")
for k, v in blocked.items():
    print(f"   {k:8s}: {v}")
print()
print("Interpretation: compare `jobs placeable` against our QUEUED count. If placeable >> queued,")
print("we are NOT capacity-blocked -- we simply have nothing more to submit, which during a serial")
print("6-generation reflection chain is the expected and correct state (record s.43).")
