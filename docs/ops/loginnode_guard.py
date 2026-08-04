"""LOGIN-NODE USAGE GUARD -- early warning before UCL's automatic penalty fires again.

WHY THIS EXISTS
---------------
On 2026-08-03 at 01:33:47 BST (00:33:47Z) UCL automatically detected a usage-policy violation
for `ucestes` on login12 and applied "penalty1": CPU and memory capped at 80% of the allowance
(6.0 cores / 30 GB) for 30 minutes. Repeat violations escalate.

WHAT ACTUALLY HAPPENED, measured rather than assumed:

  * The trigger was a STAMPEDE, not steady state. SSH access was restored at 00:31:59Z after a
    7-hour outage; two minutes later all twelve driver lines resumed at once, `tar`-extracting a
    ~1,400-record backlog while simultaneously running qacct forensics on every array that had
    drained while we were blind.
  * The email's own averages total ~3.5 cores, which is UNDER the 6-core limit -- it says so
    itself: "Usage values are recent averages. Instantaneous usage metrics may differ." So the
    detector fired on the PEAK.
  * Steady state, measured over four consecutive minutes: 236-314% CPU, 0.05 GB RSS, with
    EXACTLY 4 concurrent `qacct` processes at ~73% each.
  * Those qacct processes are NOT stuck orphans -- checked: ELAPSED=00:01 with live sshd
    parents. They are a continuous stream of short, very expensive calls.
  * They are expensive because `/opt/sge/default/common/accounting` is **33 GB** and
    `qacct -j <jobid>` scans it end to end. Four concurrent scans is ~2.9 of our 6 cores, and
    it is also 4x33 GB of shared-filesystem traffic.

So the floor is ~2.9 cores and the ceiling is 6 (4.8 while penalised): only ~3 cores of burst
headroom, and any transport interruption recreates the same stampede.

WHAT THIS TOOL DOES -- AND DELIBERATELY DOES NOT DO
---------------------------------------------------
It WATCHES and WARNS. It does not kill anything. Killing a qacct would be actively dangerous:
the driver treats a missing qacct trace as evidence that an array was purged
(`driver.py` P13, "drain with NO qacct trace") and can RESUBMIT work on that basis. Trading a
CPU spike for spurious re-training on an irreplaceable campaign is a bad trade, so this tool
refuses to make it.

Its footprint is one lightweight `ps` over ssh per cycle -- far below what it is measuring.

USAGE
    python docs/ops/loginnode_guard.py --once
    python docs/ops/loginnode_guard.py                  # loop, default 120 s
    python docs/ops/loginnode_guard.py --selftest       # no network

Exit codes for --once: 0 = comfortable, 1 = WARN (approaching), 2 = OVER the policy limit.

Printed output is ASCII-only: this repo's PowerShell console is cp1251 and a non-ASCII glyph in
a print() raises UnicodeEncodeError.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys
import time

# UCL's stated allowance, from the penalty email of 2026-08-03.
POLICY_CORES = 6.0
POLICY_MEM_GB = 30.0
#: While on penalty1 the allowance itself is cut to 80%, so the effective ceiling is lower.
PENALTY1_FACTOR = 0.80
#: Warn well before the ceiling -- the point is to act BEFORE the detector does.
#: Calibrated against the MEASURED floor, not picked round: steady state is ~2.5-2.9 cores and a
#: stampede adds ~3 more, so anything at or above ~2.7 is already one burst away from the ceiling.
#: 0.60 was too lax -- it rated the measured 2.9-core floor "comfortable", which is exactly the
#: state that produced the penalty. The selftest pins this.
WARN_FRACTION = 0.45
#: Ceilings are products of floats (6.0*0.8 = 4.800000000000001), so a measurement exactly AT the
#: ceiling compared with >= reads as under it. That is not pedantry: it made a real breach report
#: WARN instead of OVER in the selftest. Compare with a tolerance.
_EPS = 1e-9

#: ⚠ DELIBERATELY `myriad13`, NOT `myriad`. Since 2026-08-03 the `myriad` alias routes through
#: docs/ops/ssh_gate.py, so measuring through it would put the OBSERVER inside the mechanism it is
#: observing: the guard's own probe queues behind driver traffic, and a probe that loses its slot
#: returns nothing (observed live as `PROBE-UNPARSED ''`). `myriad13` reaches the same physical
#: login node ungated, so the reading is of the node rather than of the gate. Its cost is one `ps`.
HOST = "myriad13"
DEFAULT_INTERVAL = 120.0
_HERE = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(_HERE, "watch", "LOGINNODE_GUARD.log")

REMOTE = (
    "printf '%s ' \"$(hostname)\"; "
    "ps -u ucestes -o pcpu=,rss= | awk '{c+=$1; m+=$2} END {printf \"%.1f %.4f \", c, m/1048576}'; "
    "printf '%s\\n' \"$(ps -u ucestes -o comm= | grep -c qacct)\""
)


def classify(cores: float, mem_gb: float, penalised: bool = False) -> tuple[str, str]:
    """Pure: map a measurement to (level, human reason). Separated so --selftest can prove it."""
    ceiling = POLICY_CORES * (PENALTY1_FACTOR if penalised else 1.0)
    mem_ceiling = POLICY_MEM_GB * (PENALTY1_FACTOR if penalised else 1.0)
    if cores >= ceiling - _EPS or mem_gb >= mem_ceiling - _EPS:
        return "OVER", "at/above the policy ceiling (%.1f cores / %.0f GB)" % (ceiling, mem_ceiling)
    if cores >= ceiling * WARN_FRACTION - _EPS or mem_gb >= mem_ceiling * WARN_FRACTION - _EPS:
        return "WARN", "past %.0f%% of the ceiling -- a burst from here would trip it" % (WARN_FRACTION * 100)
    return "OK", "comfortable"


def _utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append(line: str) -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


#: Exit codes. 0 OK * 1 WARN * 2 OVER * 3 UNKNOWN (the probe did not produce a reading).
#: ⚠ P279, 2026-08-04. BOTH failure branches used to `return 0` -- the SAME code as "comfortable" --
#: and printed NOTHING AT ALL, because the only `print` sits in the success path below. So
#: `loginnode_guard.py --once` produced EMPTY STDOUT AND rc=0 while its own log recorded
#: `PROBE-UNPARSED ''`. That was not hypothetical: it was the LIVE state from 2026-08-04T12:00:29Z
#: through a real login13 transport refusal (`kex_exchange_identification: Connection reset by
#: peer`), for seven consecutive probes, while twelve driver lines were accumulating pull failures.
#: A session running the documented FIRST command of the session-prompt board saw nothing and would
#: have read it as healthy. The old comment justified this as "never let the guard itself fail
#: loudly" -- but the maintenance playbook names this tool as THE ONE INSTRUMENT whose verdict
#: should change behaviour on an at-risk day, so a guard that goes silent exactly when the login
#: node is in trouble is worse than no guard. Failing loudly is the entire point.
#: No caller reads this exit code programmatically (verified by grep across docs/, scripts/, src/
#: and .claude/ -- every reference is documentation or a human invocation), so widening the code
#: space breaks nothing.
UNKNOWN_RC = 3


def _unknown(kind: str, detail: str) -> int:
    """Record AND announce a probe that produced no reading. Never silent, never 0."""
    line = "%s  %-4s  %s  %s" % (_utc(), "UNKN", kind, detail)
    _append(line)
    print(line)
    print("  *** THE LOGIN-NODE GUARD HAS NO READING. This is NOT 'comfortable'. ***")
    print("  The probe reached no usable answer, so nothing is known about our CPU/memory")
    print("  footprint on the login node or about whether a UCL penalty is in force.")
    print("  Most likely causes, in the order they have actually occurred here:")
    print("    1. the login node is refusing SSH (kex reset / connection closed) -- a transport")
    print("       event, ours or UCL's; check driver logs for rising 'pull failed' counts;")
    print("    2. a probe that lost its slot behind gated driver traffic (the 2026-08-03 cause);")
    print("    3. the node was renamed or the ps/awk output shape changed.")
    print("  DO NOT retry in a loop and DO NOT relaunch lines by hand: a stampede of reconnects")
    print("  is exactly what earned the 2026-08-03 00:33:47Z penalty. Wait for the drivers'")
    print("  own backoff. Death clocks: TEST 240 x 180 s = 12.0 h, SEARCH 240 x 45 s = 3.0 h.")
    return UNKNOWN_RC


def sample(penalised: bool = False, quiet: bool = False) -> int:
    try:
        out = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", HOST, REMOTE],
            capture_output=True, text=True, timeout=90,
        ).stdout.strip()
    except Exception as exc:                                   # noqa: BLE001
        return _unknown("PROBE-FAIL", "%s: %s" % (type(exc).__name__, exc))
    parts = out.split()
    if len(parts) < 4:
        return _unknown("PROBE-UNPARSED", repr(out[:120]))
    node, cpu_pct, mem_gb, nqacct = parts[0], float(parts[1]), float(parts[2]), int(parts[3])
    cores = cpu_pct / 100.0
    level, reason = classify(cores, mem_gb, penalised)
    line = "%s  %-4s  node=%-28s cores=%.2f/%.1f  mem=%.2fGB  qacct=%d  %s" % (
        _utc(), level, node, cores, POLICY_CORES, mem_gb, nqacct, reason)
    _append(line)
    if not quiet or level != "OK":
        print(line)
    if level == "OVER":
        msg = ("%s  *** LOGIN-NODE CEILING EXCEEDED -- a UCL penalty is likely imminent. "
               "Do NOT kill qacct (the driver reads a missing trace as a purge and may resubmit). "
               "The durable fix is a relaunch with longer --poll-secs/--search-poll-secs." % _utc())
        _append(msg)
        print(msg)
        return 2
    return 1 if level == "WARN" else 0


def _selftest() -> int:
    cases = [
        ("idle",            (0.10, 0.01, False), "OK"),
        ("steady-measured", (2.90, 0.05, False), "WARN"),   # the floor that produced the penalty
        ("just-below-warn", (2.60, 0.05, False), "OK"),     # 2.7 is the warn edge at 0.45x6.0
        ("over-base",       (6.00, 0.05, False), "OVER"),   # EXACTLY at the ceiling must be OVER
        ("over-penalised",  (4.80, 0.05, True),  "OVER"),   # 6.0*0.8 float artefact -- regression pin
        ("warn-penalised",  (2.50, 0.05, True),  "WARN"),   # 0.45*4.8 = 2.16
        ("memory-blowout",  (0.10, 31.0, False), "OVER"),
    ]
    bad = 0
    print("loginnode_guard --selftest (no network)")
    for name, args, expected in cases:
        got, why = classify(*args)
        ok = got == expected
        bad += 0 if ok else 1
        print("  %-16s cores=%-5.2f mem=%-5.2f penalised=%-5s expect %-4s got %-4s %s"
              % (name, args[0], args[1], args[2], expected, got, "OK" if ok else "FAIL"))
    # the measured steady state MUST already register as WARN, or the guard is useless
    lvl, _ = classify(2.90, 0.05, False)
    if lvl == "OK":
        print("  MUTANT FAIL: the measured 2.9-core steady state must not read OK")
        bad += 1
    else:
        print("  %-16s OK -- the measured steady state registers as %s, not OK" % ("mutant-guard", lvl))
    print("")
    print("selftest: %d FAILED" % bad if bad else "selftest: ALL PASS")
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Warn before a UCL login-node usage penalty.")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--interval-secs", type=float, default=DEFAULT_INTERVAL)
    ap.add_argument("--penalised", action="store_true", help="assume the 80%% penalty ceiling")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.once:
        return sample(args.penalised, args.quiet)
    print("loginnode_guard: every %.0fs -> %s" % (args.interval_secs, LOG_PATH))
    while True:
        try:
            sample(args.penalised, args.quiet)
        except Exception as exc:                               # noqa: BLE001
            _append("%s  GUARD-ERROR %s: %s" % (_utc(), type(exc).__name__, exc))
        time.sleep(args.interval_secs)


if __name__ == "__main__":
    sys.exit(main())
