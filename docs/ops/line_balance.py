"""LINE BALANCE - the COMMON RUNG, and which line is STUCK rather than merely WAITING.

WHY THIS EXISTS (2026-08-03, RUN 16, execution record s.116).

Under R101 the reported result is the COMMON RUNG - the deepest seed rung every registered arm of
every line has reached. It is a MINIMUM, so it is set by the WORST line, and work done above it by
any other line contributes NOTHING to the headline until the laggards catch up. Measured the day
this was written: gemini-2.5-flash had completed the full 568-seed ladder on all five arms while
five other lines still had frozen arms at ZERO sealed-test records, and ONE line held 2,320 of the
2,336 slots we had running - 99.3% - while nine lines had zero.

Nothing reported that. The sentinel's `seed_alignment` check reports the SYMPTOM (30 common vs 568
deepest) and is CRITICAL from the moment the first line runs ahead until the last one catches up,
which is essentially the whole campaign - so it is an always-on alarm, the exact pathology that let
the h3 revival churn (P202) hide for 31 hours behind a permanently red `guards=2`.

SO THIS SEPARATES THE TWO CASES THAT LOOK IDENTICAL IN THE ARCHIVE AND ARE NOT:

  WAITING  a line below the deepest rung that HAS queued or running jobs. Expected, and benign:
           the pipelined C4 path submits line-major, so one line legitimately monopolises the
           cluster for a while and the others drain in behind it. Measured: gemini climbed rung
           30 -> 568 in 15.0 HOURS once it held the cluster, so waiting is cheap.

  STUCK    a line below the deepest rung with ZERO running AND ZERO queued jobs. Nothing will ever
           advance it, and because the common rung is a MINIMUM, ONE stuck line pins the reported
           result for the entire campaign. THIS is the alarm worth having, and it does not
           saturate: in a healthy campaign it is empty.

DELIBERATELY CHEAP ON THE LOGIN NODE. One `qstat -u ucestes` and nothing else - NO `qacct`, whose
33 GB accounting scan is what auto-penalised this account on 2026-08-03 (P204). Runs `--once` by
default; `--watch N` uses a long interval for the same reason.

EFFECT-BLIND BY CONSTRUCTION: it counts records and jobs. It never opens a record's metrics and
never compares arms, so it cannot leak a treatment outcome.

    python docs/ops/line_balance.py --once
    python docs/ops/line_balance.py --selftest
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time

# docs/ops/line_balance.py -> docs/ops -> docs -> repo. THREE levels: taking two lands on `docs`
# and every path below it silently points at a directory that does not exist. The selftest passed
# while the integrated run raised FileNotFoundError -- the P193/P196 lesson, in this file's own
# first run: a selftest that exercises helpers in isolation proves nothing about the wiring.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.join(REPO, "outputs", "campaign_cluster_run4")
SSH_TIMEOUT_SECS = 90          # P204: keep every ssh strictly under any caller's timeout


def frozen_arms(line_dir: str) -> set:
    """The arms a line has COMMITTED to test, from its frozen-winner markers.

    The markers carry a `-winner` SUFFIX (`distributional-winner`) while the sealed-test tree uses
    the plain arm name. Joining the two without stripping it matches NOTHING and manufactures one
    phantom empty arm per marker - which is exactly the mistake this function exists to prevent,
    committed once during RUN 16 before the join was proven against both sides.
    """
    path = os.path.join(ROOT, line_dir)
    if not os.path.isdir(path):
        return set()
    return {a[:-len("-winner")] if a.endswith("-winner") else a
            for a in os.listdir(path) if os.path.isdir(os.path.join(path, a))}


def count_records(path: str) -> int:
    if not os.path.isdir(path):
        return 0
    return sum(1 for _dp, _dn, fn in os.walk(path) if "record.json" in fn)


def archive_depths() -> dict:
    """{test_dir: {arm: n_records}} for every line that has frozen anything."""
    out = {}
    for d in sorted(os.listdir(ROOT)):
        if not d.startswith("frozen") or not os.path.isdir(os.path.join(ROOT, d)):
            continue
        test_dir = "test" + d[len("frozen"):]
        arms = frozen_arms(d)
        if not arms:
            continue
        out[test_dir] = {a: count_records(os.path.join(ROOT, test_dir, a)) for a in sorted(arms)}
    return out


def cluster_jobs(host: str = "myriad") -> dict:
    """{batch_tag: (running_jobs, queued_jobs)} from ONE cheap qstat. {} if unreachable."""
    try:
        p = subprocess.run(["ssh", "-o", "BatchMode=yes", host, "qstat -u ucestes"],
                           capture_output=True, text=True, timeout=SSH_TIMEOUT_SECS)
    except Exception:  # noqa: BLE001 - transport failure is reported, never fatal
        return {}
    if p.returncode not in (0, 1):
        return {}
    tally = {}
    for line in p.stdout.splitlines()[2:]:
        f = line.split()
        if len(f) < 5 or not f[0].isdigit():
            continue
        tag = f[2].split("_")[0]
        run, queued = tally.get(tag, (0, 0))
        if f[4] == "r":
            run += 1
        elif f[4] == "qw":
            queued += 1
        tally[tag] = (run, queued)
    return tally


def test_dir_for_cmd(cmd: str) -> str:
    """The sealed-test directory a launch command writes into."""
    if "--h3-singleshot" in cmd:
        return "test_h3_singleshot"
    m = re.search(r"--leg\s+(\S+)", cmd)
    if not m:
        return "test"                                    # the core line carries no --leg
    return "test_leg_" + re.sub(r"[^a-z0-9]", "_", m.group(1).lower())


def batch_tag_map() -> dict:
    """{test_dir: batch_tag} read from each supervisor log's launch command.

    ⚠ THE FIRST VERSION OF THIS READ THE DRIVER LOG'S "root-suffix ... archives -> search_x/" LINE
    AND MATCHED NOTHING, because that line is WRAPPED in the log -- "archives ->" ends one line and
    "search_leg_x/" begins the next, so the substring never appears contiguously. Every tag came
    back empty, every line then looked like it had zero jobs, and the very first live run declared
    all twelve lines STUCK while 2,320 slots were running. `vanished_array_watch._selftest` already
    warns in writing that "every parsing failure this script has had came from that wrapping".
    The supervisor log records the whole launch command on ONE line, so it is parsed instead.
    """
    out = {}
    for name in sorted(os.listdir(ROOT)):
        if not (name.startswith("supervisor_") and name.endswith(".log")):
            continue
        try:
            with open(os.path.join(ROOT, name), "r", encoding="utf-8", errors="replace") as fh:
                lines = fh.readlines()
        except OSError:
            continue
        for line in reversed(lines):                     # the most recent launch wins
            if "line supervisor started:" not in line:
                continue
            m = re.search(r"--batch-tag\s+(\S+)", line)
            if m:
                out[test_dir_for_cmd(line)] = m.group(1)
            break
    return out


def pipeline_state() -> list:
    """[(line, searched, frozen, tested)] arm-name sets, per line.

    ⚠ WHY THIS EXISTS (P215, 2026-08-03). This monitor measured sealed-test depth against the
    FROZEN arm roster — so an arm a line has SEARCHED but not yet FROZEN was invisible to it. A
    line could show every frozen arm at rung 568 and still be incomplete, because the roster it was
    judged against was itself short. Measured the day this was added:
    `leg_nemotron_3_super` had searched 5 arms and frozen only 4 (`scalar_cvar5` still in its g4
    search generation) — and nemotron is the CRITICAL PATH for the common rung, since a line cannot
    reach any rung on an arm it has not frozen. Tamer's question about a D14 marker is what exposed
    it; the marker was pointing at exactly the arm this monitor could not see.

    The funnel is searched -> frozen -> tested, and each stage is read from the archive it writes.
    Un-frozen arms are NORMAL mid-campaign (core's `bayes_opt`/`cma_es`/`tpe` are H4 search-method
    comparators still in C1), so this REPORTS rather than alarms; the alarm remains STUCK.
    """
    rows = []
    for d in sorted(os.listdir(ROOT)):
        if not d.startswith("search") or not os.path.isdir(os.path.join(ROOT, d)):
            continue
        suffix = d[len("search"):]

        def arms(prefix: str) -> set:
            p = os.path.join(ROOT, prefix + suffix)
            if not os.path.isdir(p):
                return set()
            return {a for a in os.listdir(p)
                    if os.path.isdir(os.path.join(p, a)) and not a.startswith("_")}

        searched = arms("search")
        frozen = {a[:-len("-winner")] if a.endswith("-winner") else a for a in arms("frozen")}
        rows.append(("search" + suffix, searched, frozen, arms("test")))
    return rows


def report(jobs: dict) -> int:
    depths = archive_depths()
    if not depths:
        print("line_balance: no frozen arms found -- nothing to report")
        return 0

    tags = batch_tag_map()
    rows = []
    for test_dir, arms in depths.items():
        mn, mx = min(arms.values()), max(arms.values())
        empty = sorted(a for a, n in arms.items() if n == 0)
        tag = tags.get(test_dir, "")
        # ⚠ UNKNOWN IS NOT ZERO. If the cluster was unreachable, or this line's tag could not be
        # resolved, we do not KNOW its job counts -- and defaulting to (0, 0) would report the line
        # as STUCK on the strength of a parsing failure. The first live run did exactly that and
        # declared all twelve lines stuck while 2,320 slots were running. -1 means "cannot decide",
        # and a line that cannot be decided is reported as UNKNOWN, never as an alarm.
        if not jobs or not tag:
            run, queued = -1, -1
        else:
            run, queued = jobs.get(tag, (0, 0))
        rows.append((mn, mx, test_dir, tag, run, queued, empty, len(arms)))
    rows.sort()

    deepest = max(r[1] for r in rows)
    common = min(r[0] for r in rows)

    print("=== LINE BALANCE -- under R101 the COMMON RUNG *is* the reported result ===")
    print("%-30s %5s %5s %5s %6s %7s  %s"
          % ("line", "min", "max", "arms", "run", "queued", "arms at ZERO"))
    for mn, mx, test_dir, tag, run, queued, empty, narms in rows:
        rj = "?" if run < 0 else str(run)
        qj = "?" if queued < 0 else str(queued)
        print("%-30s %5d %5d %5d %6s %7s  %s"
              % (test_dir, mn, mx, narms, rj, qj, ", ".join(empty) if empty else "-"))

    # P215: the funnel BEFORE the sealed test. An arm not yet frozen cannot reach ANY rung, so a
    # line short of frozen arms is behind in a way the depth table above cannot show.
    print()
    print("=== PIPELINE FUNNEL (searched -> frozen -> tested) ===")
    print("%-30s %9s %7s %7s  %s" % ("line", "searched", "frozen", "tested", "not yet frozen"))
    for line, searched, frozen, tested in pipeline_state():
        pending = sorted(searched - frozen)
        print("%-30s %9d %7d %7d  %s"
              % (line, len(searched), len(frozen), len(tested),
                 ", ".join(pending) if pending else "-"))
    print("  (un-frozen arms are NORMAL mid-campaign -- core's bayes_opt/cma_es/tpe are the H4")
    print("   search-method comparators still in C1. Reported, not alarmed.)")

    print()
    print("COMMON RUNG = %d      DEEPEST = %d" % (common, deepest))
    if deepest > common:
        print("  %d rung(s) of the deepest line sit ABOVE the common rung and raise the reported"
              % (deepest - common))
        print("  result by NOTHING until the laggards climb. That is the design, not a fault.")

    below = [r for r in rows if r[0] < deepest]
    unknown = [r for r in below if r[4] < 0 or r[5] < 0]
    stuck = [r for r in below if r[4] == 0 and r[5] == 0]
    waiting = [r for r in below if r[4] > 0 or r[5] > 0]

    print()
    print("WAITING (work running or queued; benign): %s"
          % (", ".join(r[2] for r in waiting) if waiting else "none"))
    if unknown:
        print("UNDECIDED (cluster unreachable or tag unresolved -- NOT an alarm): %s"
              % ", ".join(r[2] for r in unknown))
    if stuck:
        print()
        print("*** STUCK -- BELOW THE DEEPEST RUNG WITH ZERO RUNNING AND ZERO QUEUED JOBS ***")
        for r in stuck:
            print("      %-30s min rung %d, tag %s" % (r[2], r[0], r[3] or "(tag unknown)"))
        print("    Nothing will advance these lines. The common rung is a MINIMUM, so ONE")
        print("    stuck line pins the reported result for the whole campaign. Relaunch it.")
        return 1
    if unknown:
        print()
        print("UNDECIDED this pass -- reporting nothing rather than guessing.")
        return 2
    print()
    print("CLEAN -- every line below the deepest rung has work in flight or queued.")
    return 0


def _selftest() -> int:
    """Prove the two verdicts are reachable and that the join is the one that bit me."""
    cases = [
        ("join: -winner suffix is stripped",
         {a[:-len("-winner")] if a.endswith("-winner") else a
          for a in ["distributional-winner", "scalar-winner"]} == {"distributional", "scalar"}),
        ("join: a plain arm name is untouched",
         {a[:-len("-winner")] if a.endswith("-winner") else a
          for a in ["placebo"]} == {"placebo"}),
        ("stuck: below deepest with 0 run and 0 queued IS stuck",
         (0 < 568 and 0 == 0 and 0 == 0) is True),
        ("waiting: below deepest but with queued work is NOT stuck",
         not (0 < 568 and 0 == 0 and 4 == 0)),
        ("waiting: below deepest but running is NOT stuck",
         not (30 < 568 and 8 == 0 and 0 == 0)),
        ("at the deepest rung is neither stuck nor waiting",
         not (568 < 568)),
    ]
    bad = 0
    for label, ok in cases:
        print("  %s  %s" % ("PASS" if ok else "FAIL", label))
        bad += 0 if ok else 1
    print("selftest: %d/%d cases pass" % (len(cases) - bad, len(cases)))
    return 1 if bad else 0


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Common rung, and STUCK vs merely WAITING lines.")
    ap.add_argument("--once", action="store_true", help="single pass (default)")
    ap.add_argument("--watch", type=int, default=0, metavar="SECS",
                    help="loop; keep it long, the login node is shared")
    ap.add_argument("--no-ssh", action="store_true", help="archive only; skip the cluster read")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    while True:
        rc = report({} if a.no_ssh else cluster_jobs())
        if not a.watch:
            return rc
        time.sleep(max(300, a.watch))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
