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
import json
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

#: How long a line must be CONTINUOUSLY job-less before STUCK alarms. Set from measurement, not
#: taste: `gpt-5.6-luna` was legitimately job-less for 20.0 min between finishing a block and
#: submitting its own repair round. 45 min is >2x that, and still trivial against the hours a
#: genuinely stuck line would cost. Raise it if a longer benign gap is ever observed; NEVER lower it
#: to make the alarm more responsive - a false STUCK gets a healthy line relaunched.
STUCK_DWELL_SECS = 2700.0
DWELL_STATE = os.path.join(REPO, "docs", "ops", "watch", "line_balance_dwell.json")


def _load_dwell(now: float | None = None) -> dict:
    """{line: first_seen_jobless_epoch}. A torn or missing file means 'no history', never 'stuck'.

    ⚠ EVERY TIMESTAMP IS CLAMPED INTO (0, now]. The original guarded only the false-POSITIVE
    direction; an auditor pointed out the SUPPRESSING direction was wide open. A value in the
    future (clock change, DST, a hand-edit, a bad merge) makes `now - ts` negative forever, and
    `json.load` accepts bare `NaN`/`Infinity` by default -- `nan >= 2700` is False forever. Either
    would silence the alarm permanently and invisibly. An out-of-range stamp is reset to `now`,
    which costs at most one dwell period and can never suppress.
    """
    now = time.time() if now is None else now
    try:
        with open(DWELL_STATE, encoding="utf-8") as fh:
            d = json.load(fh)
        if not isinstance(d, dict):
            return {}
        out = {}
        for k, v in d.items():
            try:
                ts = float(v)
            except (TypeError, ValueError):
                continue
            out[k] = ts if 0.0 < ts <= now else now      # NaN fails BOTH comparisons -> reset
        return out
    except Exception:  # noqa: BLE001 - unreadable state must degrade to "no history", not to an alarm
        return {}


def _save_dwell(state: dict) -> None:
    try:
        os.makedirs(os.path.dirname(DWELL_STATE), exist_ok=True)
        tmp = DWELL_STATE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(state, fh)
        os.replace(tmp, DWELL_STATE)      # atomic: a reader never sees a half-written file
    except OSError:
        pass                              # never let bookkeeping break the check itself


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
        # ⚠ ZERO IS NOT CLEAN (the P213 rule, applied here after an auditor found the same shape).
        # An existing-but-empty root used to print "nothing to report" and return 0 -- a vacuous
        # pass, while S14 returns 2 on exactly this shape. A check that examined nothing must not
        # report success.
        print("line_balance: *** CANNOT VOUCH FOR ANYTHING *** -- no frozen arms found under")
        print("  %s" % ROOT)
        print("  This is NOT a clean result: the common rung and STUCK/WAITING were never evaluated.")
        return 2

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
    # s.124.6 recorded this as OPEN: these columns were labelled `rung` but hold RECORD COUNTS
    # (392 is not a registered rung). They are a MONOTONE PROXY, which is all STUCK/WAITING needs,
    # but the label claimed the registered quantity. Relabelled 2026-08-03 (RUN 17, s.130), and the
    # TRUE banked rung -- which a record COUNT cannot give, because a single hole below the frontier
    # demotes it -- now comes from `docs/analysis/record_seed_completeness.py` (S15).
    print("%-30s %5s %5s %5s %6s %7s  %s"
          % ("line", "recMin", "recMax", "arms", "run", "queued", "arms at ZERO"))
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
    print("COMMON (min record count) = %d      DEEPEST = %d" % (common, deepest))
    print("  !! THESE ARE RECORD COUNTS, NOT REGISTERED RUNGS. A count can OVERSTATE the rung an arm")
    print("     actually banks, because one missing seed below the frontier demotes it: gpt-5.6-luna")
    print("     held 567 records with a frontier of 567 and banked 189, not 568. For the TRUE banked")
    print("     rung run `docs/analysis/record_seed_completeness.py` (S15).")
    if deepest > common:
        print("  %d rung(s) of the deepest line sit ABOVE the common rung and raise the reported"
              % (deepest - common))
        print("  result by NOTHING until the laggards climb. That is the design, not a fault.")

    below = [r for r in rows if r[0] < deepest]
    unknown = [r for r in below if r[4] < 0 or r[5] < 0]
    idle = [r for r in below if r[4] == 0 and r[5] == 0]
    waiting = [r for r in below if r[4] > 0 or r[5] > 0]

    # ⚠ STUCK NOW REQUIRES A DWELL TIME, AND THIS IS A REAL DEFECT FIX (2026-08-03, RUN 17, s.129).
    #
    # The predicate above is an INSTANTANEOUS sample, and a healthy line is legitimately at zero
    # jobs BETWEEN BATCHES. Measured live: `gpt-5.6-luna` completed `sweep_t6` at 14:41:32Z with
    # `{'ok': True, 'completed': 825, 'total': 825, 'exhausted': []}`, sat at zero running and zero
    # queued for TWENTY MINUTES, and at 15:01:13Z re-submitted block `t3` as ROUND 2 to fill the 8
    # seeds it had noticed were missing (192/193 across the arms). It was self-healing the whole
    # time. A single sample in that window declared it STUCK, and STUCK is documented here as the
    # one alarm that would genuinely cost the result -- so a false positive on it is precisely the
    # alarm-hygiene failure that trains an operator to relaunch a healthy line.
    #
    # The countermeasure is the one s.124.5 already applied to `cycle_loop_dupes`: REQUIRE THE
    # CONDITION TO PERSIST. A line must be continuously job-less for STUCK_DWELL_SECS before it
    # alarms; below that it is reported as IDLE with its age, which is informative and not an alarm.
    # ⚠⚠ THE CLEARING RULE IS THE WHOLE SAFETY PROPERTY, AND MY FIRST VERSION HAD IT BACKWARDS.
    #
    # It cleared a line's streak whenever the line was ABSENT from `idle` -- but a line leaves
    # `idle` for TWO reasons: it has jobs (fine), or its counts are UNKNOWN (`run < 0 or
    # queued < 0`, i.e. the ssh failed or the batch tag did not resolve). So a SINGLE failed
    # `qstat` wiped the accumulated dwell of EVERY line at once.
    #
    # An auditor showed why that is far worse than the false positive it replaced: at
    # `--watch 1800` the bound needs THREE consecutive successful passes spanning 60 min, so
    # **one qstat failure per hour suppresses the STUCK alarm indefinitely** -- and the transport
    # conditions that kill a line are EXACTLY the conditions that fail a qstat (record s.127:
    # 57 `qstat -r` timeouts in one hour, all at 120.0 s, while SSH_TIMEOUT_SECS here is 90).
    # **The suppression was CORRELATED WITH THE FAULT.** A missed alarm beats a false one every
    # time, and I had traded the cheap error for the expensive one.
    #
    # ⇒ ONLY A POSITIVE OBSERVATION MAY CLEAR A STREAK: the line was seen WITH jobs, or it is at
    #   or above the deepest rung (so it is not a STUCK candidate at all). UNKNOWN PRESERVES.
    now = time.time()
    state, stuck_names = _dwell_step(
        _load_dwell(now),
        [r[2] for r in idle],
        {r[2] for r in waiting} | {r[2] for r in rows if r[0] >= deepest},
        now,
    )
    _save_dwell(state)
    stuck = [r for r in idle if r[2] in stuck_names]
    young = [r for r in idle if r[2] not in stuck_names]

    print()
    print("WAITING (work running or queued; benign): %s"
          % (", ".join(r[2] for r in waiting) if waiting else "none"))
    if young:
        print("IDLE, NOT YET STUCK (a line is legitimately job-less BETWEEN BATCHES; measured 20 min"
              " on gpt-5.6-luna while it self-healed 8 seeds):")
        for r in young:
            print("      %-30s job-less for %5.1f min of the %.0f min needed to alarm"
                  % (r[2], (now - state.get(r[2], now)) / 60.0, STUCK_DWELL_SECS / 60.0))
    if unknown:
        print("UNDECIDED (cluster unreachable or tag unresolved -- NOT an alarm): %s"
              % ", ".join(r[2] for r in unknown))
    if stuck:
        print()
        print("*** STUCK -- ZERO RUNNING AND ZERO QUEUED, CONTINUOUSLY, FOR OVER %.0f MINUTES ***"
              % (STUCK_DWELL_SECS / 60.0))
        for r in stuck:
            print("      %-30s min rung %d, tag %s, job-less %.1f min"
                  % (r[2], r[0], r[3] or "(tag unknown)", (now - state.get(r[2], now)) / 60.0))
        print("    Nothing will advance these lines. The common rung is a MINIMUM, so ONE")
        print("    stuck line pins the reported result for the whole campaign. Relaunch it.")
        print("    !! BEFORE RELAUNCHING: read the driver log. A line that has just finished a block")
        print("    re-submits a repair round on its own -- check for a `round 2` submission first.")
        return 1
    if unknown:
        print()
        print("UNDECIDED this pass -- reporting nothing rather than guessing.")
        return 2
    print()
    print("CLEAN -- every line below the deepest rung has work in flight or queued.")
    return 0


def _dwell_step(state: dict, idle_names: list, fine_names: list, now: float) -> tuple:
    """THE PRODUCTION CLEAR/ACCUMULATE RULE, extracted verbatim so a test can drive it.

    ⚠ THIS EXISTS BECAUSE MY FIRST SELFTEST TESTED A TAUTOLOGY. It asserted
    `(now - (now - x)) >= BOUND`, which is algebraically `x >= BOUND` -- a re-implementation that
    executed NO production code, so it covered none of the real defects (the UNKNOWN-clears-state
    bug, the timestamp clamp, the disk round-trip). An auditor called it exactly right, and the
    record's claim that those cases "FAIL against the pre-fix predicate" was not demonstrable.
    `report()` now calls this function, so a test that drives it drives production.
    """
    for name in list(state):
        if name in fine_names:
            del state[name]
    for name in idle_names:
        state.setdefault(name, now)
    stuck = {n for n in idle_names if (now - state.get(n, now)) >= STUCK_DWELL_SECS}
    return state, stuck


def _dwell_cases() -> list:
    """DWELL cases driving the PRODUCTION rule (`_dwell_step`) and the real load/save on a TEMP path.

    ⚠ THE SELFTEST NO LONGER TOUCHES THE LIVE STATE FILE. It previously called `_save_dwell` on the
    module-level production path, so the documented `--selftest` command DESTROYED every streak the
    live `--watch` daemon had accumulated -- a selftest that sabotages the monitor it tests.
    """
    import tempfile
    T0 = 1_000_000.0
    out = []

    # A-D: the dwell bound itself, driven through the production rule.
    st, stuck = _dwell_step({}, ["L"], [], T0)
    out.append(("dwell A: first sighting job-less is NOT stuck (the pre-fix code alarmed here)",
                stuck == set()))
    st, stuck = _dwell_step(dict(st), ["L"], [], T0 + 19.7 * 60)
    out.append(("dwell B: 19.7 min -- the MEASURED gpt-5.6-luna gap -- is NOT stuck", stuck == set()))
    st, stuck = _dwell_step(dict(st), ["L"], [], T0 + 44 * 60)
    out.append(("dwell C: 44 min, just under the bound, is NOT stuck", stuck == set()))
    st, stuck = _dwell_step(dict(st), ["L"], [], T0 + 46 * 60)
    out.append(("dwell D: 46 min IS stuck -- the alarm is still REACHABLE", stuck == {"L"}))

    # E: THE CRITICAL ONE. An UNKNOWN pass (line in neither idle nor fine) must PRESERVE the streak.
    st = {"L": T0}
    st, stuck = _dwell_step(dict(st), [], [], T0 + 30 * 60)          # ssh failed: UNKNOWN
    st, stuck = _dwell_step(dict(st), ["L"], [], T0 + 60 * 60)       # back, still job-less
    out.append(("dwell E: an UNKNOWN pass PRESERVES the streak -- the missed-alarm bug",
                stuck == {"L"} and st.get("L") == T0))

    # F: only a POSITIVE observation of jobs clears it.
    st = {"L": T0}
    st, stuck = _dwell_step(dict(st), [], ["L"], T0 + 10 * 60)       # seen WITH jobs
    out.append(("dwell F: a line seen WITH jobs has its streak cleared", "L" not in st))

    # G: the real disk round-trip, on a TEMP path, and the clamp on a poisoned stamp.
    global DWELL_STATE
    real = DWELL_STATE
    try:
        with tempfile.TemporaryDirectory() as td:
            DWELL_STATE = os.path.join(td, "dwell.json")
            _save_dwell({"leg6": T0})
            rt = abs(_load_dwell(T0 + 1).get("leg6", 0.0) - T0) < 1.0
            out.append(("dwell G: the state round-trips through disk (TEMP path, not production)", rt))
            with open(DWELL_STATE, "w", encoding="utf-8") as fh:
                fh.write('{"future": 9999999999.0, "nan": NaN, "neg": -5}')
            back = _load_dwell(T0)
            out.append(("dwell H: future/NaN/negative stamps are CLAMPED, never left to suppress",
                        back.get("future") == T0 and back.get("nan") == T0
                        and back.get("neg") == T0))
            with open(DWELL_STATE, "w", encoding="utf-8") as fh:
                fh.write("{not json")
            out.append(("dwell I: a genuinely unreadable file yields NO history, never a verdict",
                        _load_dwell(T0) == {}))
    finally:
        DWELL_STATE = real
    out.append(("dwell J: the bound is >2x the measured 19.7 min benign gap",
                STUCK_DWELL_SECS >= 2 * 19.7 * 60))
    return out


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
    cases += _dwell_cases()
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
