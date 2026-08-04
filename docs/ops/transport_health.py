"""TRANSPORT HEALTH - how close is any line to a transport-induced ARM CRASH, right now?

WHY THIS EXISTS (2026-08-03, RUN 17, execution record s.127).

Tamer, mid-session: *"I think there might be a time outs issue."* He was right that there was a
burst, and the published number could not tell him whether it mattered.

`docs/RUN4_STATUS.md` published **"transport timeouts: 58"**. That figure is:

  * **CUMULATIVE-EVER over an append-only set of logs**, so it can only ever rise. It went 58 -> 116
    inside one session. This is the P205 / `guard:transport` antipattern that this project has now
    found FOUR times: *a cumulative counter used as a current-state alarm*. It cannot distinguish a
    dead campaign from a healthy one.
  * **A count of LINES, not of events** - it greps two markers and sums, so one event that emits
    both `ssh_timeout_diagnostic` and `TimeoutExpired` is counted twice.
  * **Severity-blind.** A timeout only matters through the CONSECUTIVE STREAK it belongs to, and
    that number was published nowhere.

THE ONLY NUMBER THAT DISTINGUISHES NOISE FROM A CRASH is the current consecutive-failure streak
against the bound that actually kills an arm. Read from the live code rather than assumed:

    src/cluster/campaign.py:183   max_consecutive_errors = 240      (overrides driver.py's own 72)
    src/cluster/driver.py:350     max_transport_outage_secs = 43200 s = 12 h
    src/cluster/driver.py:434     _outage_is_fatal = EITHER bound, whichever trips first
    live driver flags             --poll-secs 180 (test) | --search-poll-secs 45 (search)

  => SEARCH lane: 240 x 45 s  = **3.0 h** of continuous outage is FATAL to the arm
  => TEST   lane: 240 x 180 s = 12.0 h, where the wall-clock bound (12 h) coincides

The 3.0 h figure is not theoretical: it is verbatim what killed `nemotron/scalar_cvar5` on
2026-08-02 at 20:06:45Z - *"240 consecutive pull failures over 3.0 h"* - and the count bound, not
the advertised 12 h wall bound, is what tripped. That is the substance of **D24**, now quantified.
(D24's other half is stale: it says the docstring claims BOTH bounds while the code is an OR; the
docstring at `driver.py:435-437` now correctly says EITHER/OR and matches the code.)

TWO COUNTERS, TWO CONSEQUENCES - the status page conflated them:

    pull_failures   the `find` over the remote outputs tree. THIS is the fatal path: at the bound
                    the driver raises and the ARM CRASHES, leaving a D14 marker.
    ops_failures    the `qstat -r` / `qsub` queue path. Tracked separately by the driver.

EFFECT-BLIND: it reads driver log lines only. No record is opened and no result is touched.

FAILS LOUD ON AN EMPTY INPUT SET (exit 2) - "found nothing wrong" and "looked at nothing" are
indistinguishable in a green board (P197/P213).

    python docs/ops/transport_health.py
    python docs/ops/transport_health.py --hours 6
    python docs/ops/transport_health.py --oneline     # for the status page / cycle line
    python docs/ops/transport_health.py --selftest

EXIT: 0 healthy   1 a streak is materially advanced toward fatal   2 could not run / inspected nothing
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from datetime import datetime, timedelta

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_ROOT = os.path.join(REPO, "outputs", "campaign_cluster_run4")

#: Read from the live code, NOT guessed. campaign.py passes 240, overriding driver.py's own 72.
FATAL_CONSECUTIVE = 240
SEARCH_POLL_SECS = 45
TEST_POLL_SECS = 180
#: A streak at or above this fraction of the bound is worth a human's attention.
WARN_FRACTION = 0.25

# ⚠⚠ EVERY LITERAL SPACE HERE IS `\s+`, AND THE TIMESTAMP ACCEPTS BOTH LOG FORMATS.
#
# THE FIRST VERSION OF THIS FILE WAS WRONG FOR HALF THE FLEET, and an auditor measured it:
#
#   (a) `unwrap` re-joined a wrapped line with `" " + ln.strip()` while the wrapped physical line
#       ALREADY ended in a space, producing DOUBLE spaces that single-space literals reject:
#           '... pull failed (1 consecutive, 0 min  down): shared pull failed recently...'
#           '... queue op failed (1  consecutive, 0 min): Command ...'
#       Measured: 5,913 `pull failed (` occurrences -> only 2,354 regex matches. A naive
#       `grep -c` -- the method this file's docstring criticises -- found MORE than it did.
#
#   (b) `_TS` matched only the `YYYY-MM-DD HH:MM:SS |` form. The logs also carry a legacy
#       `2026-07-30 01:26:27,164 WARNING src.cluster.driver:` form with no ` |`, so every legacy
#       line was GLUED onto the preceding record -- `driver_h3.log` collapsed into a single 625 KB
#       "record", and `.search()` returns at most one match per record.
#
# THE CONSEQUENCE, and it is the number this file exists to report: SIX of twelve lines had their
# peak streak understated as 0-2 when the true peak was 140-149 -- i.e. a line that came 62 % of
# the way to death was reported as not existing. Fixed and re-measured; s.127.3 is corrected.
_TS = re.compile(r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d[ ,|]")
_PULL = re.compile(r"pull\s+failed\s+\((\d+)\s+consecutive,\s+([\d.]+)\s+min\s+down")
_OPS = re.compile(r"queue\s+op\s+failed\s+\((\d+)\s+consecutive,\s+([\d.]+)\s+min")
_TMO = re.compile(r"ssh_timeout_diagnostic\s+cmd=(\[[^\]]*\]).*?elapsed=([\d.]+)s")


def peak_history(root: str) -> list:
    """[(line, worst_pull, minutes_down_at_that_peak, when)] over the WHOLE campaign.

    THE NUMBER THIS EXISTS TO SURFACE, and it is the one the status page never carried: how close
    has each line ACTUALLY come to dying? Measured 2026-08-03 over the whole of RUN 4:

        core              240 / 240   3.0 h down   2026-08-02 23:20:08Z   <- DIED (bayes_opt)
        nemotron-3-super  240 / 240   3.0 h down   2026-08-02 20:06:45Z   <- DIED (scalar_cvar5)
        glm-5.2           149 / 240   7.4 h down   survived
        deepseek-v4-pro   148 / 240   7.3 h down   survived
        gemini-2.5-flash  148 / 240   7.3 h down   survived

    The split is the whole finding. The two that DIED were in the SEARCH lane (45 s poll), where
    240 failures is reached in **3.0 h**. The three that SURVIVED an outage more than twice as long
    were in the TEST lane (180 s poll), where the same 240 is 12.0 h. One VPN outage of 7 h 24 m
    therefore killed exactly the lines whose lane could not ride it out - and it explains BOTH of
    the campaign's open crash markers with a single mechanism.
    """
    out = []
    for f in sorted(glob.glob(os.path.join(root, "driver_*.log"))):
        name = os.path.basename(f)[len("driver_"):-len(".log")]
        worst, mins, when = 0, 0.0, ""
        for r in unwrap(f):
            m = _PULL.search(r)
            if m and int(m.group(1)) > worst:
                worst, mins, when = int(m.group(1)), float(m.group(2)), r[:19]
        out.append((name, worst, mins, when))
    return out


#: Bytes read from the TAIL of each driver log for a windowed scan. The logs are append-only and
#: already total 44 MB; reading them whole costs 2.0 s and RISES FOREVER, which is exactly the
#: P194 shape ("a new monitor is a load on the monitor it joins") this session found operating live
#: in the status page. 4 MB per log is many hours of driver output at the observed rate, so the
#: 6 h window is covered with wide margin while the cost stays CONSTANT. `peak_history` deliberately
#: reads whole files, because "how close did we EVER come" cannot be answered from a tail - and it
#: is a session-level question, not a per-cycle one.
TAIL_BYTES = 4 * 1024 * 1024


def unwrap(path: str, tail_bytes: int | None = None) -> list:
    """Driver logs are LINE-WRAPPED; a logical record spans several physical lines.

    Every grep-based count over these files is a count of PHYSICAL LINES and will disagree with the
    number of EVENTS whenever a record wraps across the marker. Re-joining on the timestamp prefix
    is the only way to count events, and it is why this file does not use grep.

    ``tail_bytes`` bounds the read. The first (possibly truncated) record is discarded, so a partial
    line at the seek point can never be mis-parsed as an event.
    """
    try:
        if tail_bytes is not None and os.path.getsize(path) > tail_bytes:
            with open(path, "rb") as fb:
                fb.seek(-tail_bytes, os.SEEK_END)
                raw = fb.read()
            txt = raw.decode("utf-8", errors="replace")
            nl = txt.find("\n")
            txt = txt[nl + 1:] if nl >= 0 else ""
        else:
            with open(path, encoding="utf-8", errors="replace") as fh:
                txt = fh.read()
    except OSError:
        return []
    txt = txt.replace("\r\n", "\n").replace("\r", "")
    recs, cur = [], None
    for ln in txt.split("\n"):
        if _TS.match(ln):
            if cur is not None:
                recs.append(cur)
            cur = ln
        elif cur is not None:
            # rstrip the accumulator too: the wrapped physical line already ends in a space, so a
            # bare `+ " "` produced the double spaces that broke every streak regex above.
            cur = cur.rstrip() + " " + ln.strip()
    if cur is not None:
        recs.append(cur)
    return recs


def scan(root: str, hours: float) -> dict:
    """Per line: timeout events in window, and the LAST-SEEN consecutive streaks."""
    cutoff = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    lines = {}
    total_events = 0
    by_cmd = {}
    for f in sorted(glob.glob(os.path.join(root, "driver_*.log"))):
        name = os.path.basename(f)[len("driver_"):-len(".log")]
        rec = {"events": 0, "pull_last": 0, "ops_last": 0, "pull_worst": 0, "ops_worst": 0,
               "last_event": "", "last_failure": ""}
        for r in unwrap(f, TAIL_BYTES):
            ts = r[:19]
            m = _TMO.search(r)
            if m and ts >= cutoff:
                rec["events"] += 1
                total_events += 1
                cmd = m.group(1)[:40]
                by_cmd[cmd] = by_cmd.get(cmd, 0) + 1
                rec["last_event"] = ts
            # Streaks are read WITHOUT the window: the last value seen IS the current streak,
            # because the driver only logs the line when the streak is live. A streak that ended
            # is superseded by the next success, which logs nothing -- so a stale `last` is only
            # meaningful together with its timestamp, which is why both are printed.
            mp = _PULL.search(r)
            if mp:
                n = int(mp.group(1))
                rec["pull_last"] = n
                rec["last_failure"] = ts
                if ts >= cutoff:
                    rec["pull_worst"] = max(rec["pull_worst"], n)
            mo = _OPS.search(r)
            if mo:
                n = int(mo.group(1))
                rec["ops_last"] = n
                rec["last_failure"] = ts
                if ts >= cutoff:
                    rec["ops_worst"] = max(rec["ops_worst"], n)
        lines[name] = rec
    return {"lines": lines, "total_events": total_events, "by_cmd": by_cmd, "hours": hours}


def parsed_anything(s: dict) -> bool:
    """Did the parser match ANY streak line at all, anywhere?

    ⚠ THE ORIGINAL "FAILS LOUD ON EMPTY" GUARD ONLY COVERED *NO DRIVER LOGS*. When logs existed but
    NOTHING matched -- which is exactly what the regex defect above produced for six of twelve
    lines -- every counter read 0, `verdict()` returned 0, and the page published HEALTHY.
    **A total parse failure was indistinguishable from perfect health**, which is the precise
    P197/P213 shape this file's docstring claims immunity to. It is now a separate, explicit check:
    the campaign has a known, permanent history of streaks (core and nemotron both reached 240), so
    a scan of the full logs that matches NOTHING is a broken parser, never a clean fleet.
    """
    return any(v["pull_last"] or v["ops_last"] or v["pull_worst"] or v["ops_worst"] or v["events"]
               for v in s["lines"].values())


def verdict(s: dict) -> int:
    if not parsed_anything(s):
        return 2
    worst = max((max(v["pull_worst"], v["ops_worst"]) for v in s["lines"].values()), default=0)
    return 1 if worst >= FATAL_CONSECUTIVE * WARN_FRACTION else 0


def _age_minutes(ts: str) -> float | None:
    """Minutes since a `YYYY-mm-dd HH:MM:SS` driver-log stamp, or None if unreadable."""
    try:
        return (datetime.now() - datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S")).total_seconds() / 60.0
    except Exception:  # noqa: BLE001 - an unparseable stamp must not break the summary
        return None


def _age_str(mins: float | None) -> str:
    if mins is None:
        return "age UNKNOWN"
    if mins < 90:
        return "%.0f min ago" % mins
    return "%.1f h ago" % (mins / 60.0)


def oneline(s: dict) -> str:
    # ⚠ P292, 2026-08-04. THIS LINE USED TO REPORT A WINDOWED MAXIMUM WITH NO AGE, AND IT RAISED A
    # FALSE ALARM ON THE PERSON THE PAGE EXISTS FOR. It read "worst streak 21/240 (8.8% to fatal),
    # pull on core" more than two hours after core's last failure -- the tail of INC-1, the 31m50s
    # login-node refusal that ended at 12:32:19Z. A streak that ENDED was byte-indistinguishable
    # from one CLIMBING.
    # The module already had the fix in hand: `scan()` records `last_failure` per line and its own
    # comment says "a stale `last` is only meaningful together with its timestamp, which is why both
    # are printed" -- but `oneline()` never printed it. Same family as P278 (a re-triage trigger on
    # a monotone counter) and W1 (a process-local CUSUM quoted as a trend): a statistic with no time
    # attached cannot be acted on.
    # Two things are added, both computed from data already collected: the AGE of the worst streak,
    # and whether ANY line has failed recently ("none live" vs "LIVE"). Nothing is removed, so any
    # reader or scraper of the existing prefix is unaffected.
    worst_line, worst_n, worst_kind = "-", 0, "-"
    for k, v in s["lines"].items():
        for kind in ("pull", "ops"):
            if v[kind + "_worst"] > worst_n:
                worst_n, worst_line, worst_kind = v[kind + "_worst"], k, kind
    pct = 100.0 * worst_n / FATAL_CONSECUTIVE
    worst_age = _age_minutes((s["lines"].get(worst_line) or {}).get("last_failure", ""))
    newest = None
    for v in s["lines"].values():
        a = _age_minutes(v.get("last_failure", ""))
        if a is not None and (newest is None or a < newest):
            newest = a
    # LIVE_MINUTES is deliberately generous: the TEST poll is 180 s, so a genuinely live streak
    # re-logs within 3 minutes. 10 minutes covers the SEARCH poll, clock skew and a slow cycle
    # without ever calling a two-hour-old streak "live".
    live = newest is not None and newest <= 10.0
    state = ("LIVE, still failing" if live
             else ("none live, newest failure %s" % _age_str(newest)) if newest is not None
             else "no failure ever recorded")
    # NO PIPE CHARACTER. This string is rendered into a MARKDOWN TABLE CELL by
    # docs/ops/publish_status.sh, and a literal `|` splits the cell into extra columns -- which is
    # exactly what it did on the first publish. ASCII only, for the same page's phone rendering.
    return ("timeouts %dh=%d; worst streak %d/%d (%.1f%% to fatal), %s on %s, %s; %s"
            % (int(s["hours"]), s["total_events"], worst_n, FATAL_CONSECUTIVE, pct,
               worst_kind, worst_line, _age_str(worst_age), state))


def report(root: str, hours: float) -> int:
    if not os.path.isdir(root):
        print("*** archive root does not exist: %s" % root)
        return 2
    s = scan(root, hours)
    if not s["lines"]:
        print("*** NO driver logs found. This check inspected NOTHING and is VACUOUS. Exiting 2.")
        return 2

    print("=== TRANSPORT HEALTH  (window: last %g h) ===" % hours)
    print("  FATAL BOUND (read from src/cluster/campaign.py:183): %d consecutive failures"
          % FATAL_CONSECUTIVE)
    print("  => SEARCH lane %d x %ds = %.1f h of continuous outage kills the arm"
          % (FATAL_CONSECUTIVE, SEARCH_POLL_SECS, FATAL_CONSECUTIVE * SEARCH_POLL_SECS / 3600))
    print("  => TEST   lane %d x %ds = %.1f h  (the 12 h wall bound coincides there)"
          % (FATAL_CONSECUTIVE, TEST_POLL_SECS, FATAL_CONSECUTIVE * TEST_POLL_SECS / 3600))
    print()
    print("%-24s %8s %10s %10s %10s %10s  %s" % (
        "line", "events", "pull_last", "pull_wrst", "ops_last", "ops_wrst", "last failure"))
    for k in sorted(s["lines"]):
        v = s["lines"][k]
        w = max(v["pull_worst"], v["ops_worst"])
        flag = "  <<< ATTENTION" if w >= FATAL_CONSECUTIVE * WARN_FRACTION else ""
        print("%-24s %8d %10d %10d %10d %10d  %s%s" % (
            k, v["events"], v["pull_last"], v["pull_worst"], v["ops_last"], v["ops_worst"],
            v["last_failure"] or "-", flag))
    print("-" * 100)
    print("  timeout EVENTS in window (not lines; the logs wrap): %d" % s["total_events"])
    for cmd, n in sorted(s["by_cmd"].items(), key=lambda kv: -kv[1]):
        print("      %-44s %d" % (cmd, n))
    worst = max((max(v["pull_worst"], v["ops_worst"]) for v in s["lines"].values()), default=0)
    print("  WORST CONSECUTIVE STREAK IN WINDOW: %d of %d  =  %.1f%% of the way to a crash"
          % (worst, FATAL_CONSECUTIVE, 100.0 * worst / FATAL_CONSECUTIVE))
    print()
    print("=== HOW CLOSE HAS EACH LINE EVER COME? (whole campaign; the number that was never published) ===")
    hist = sorted(peak_history(root), key=lambda r: -r[1])
    for name, w, mins, when in hist:
        if w == 0:
            continue
        tag = "  *** REACHED THE BOUND - THE ARM CRASHED" if w >= FATAL_CONSECUTIVE else ""
        print("  %-24s %4d / %d  (%.1f%%)  %5.1f h down   %s%s"
              % (name, w, FATAL_CONSECUTIVE, 100.0 * w / FATAL_CONSECUTIVE, mins / 60.0,
                 when or "-", tag))
    died = [h for h in hist if h[1] >= FATAL_CONSECUTIVE]
    if died:
        print("  => %d line(s) have ALREADY been killed by transport. Both were in the SEARCH lane,"
              % len(died))
        print("     where 240 x 45 s = 3.0 h. The lines that SURVIVED the same 7 h 24 m outage were")
        print("     in the TEST lane, where the same 240 is 12.0 h. THE LANE IS THE WHOLE DIFFERENCE.")
    print()
    print("  A TIMEOUT ONLY MATTERS THROUGH ITS STREAK. Isolated timeouts are absorbed by the retry")
    print("  loop and cost nothing; only an UNBROKEN run of them reaches the bound and crashes an")
    print("  arm. Read the streak column, never the event count.")
    print()
    rc = verdict(s)
    if rc:
        print("VERDICT: ATTENTION -- a streak has passed %.0f%% of the fatal bound." % (100 * WARN_FRACTION))
    else:
        print("VERDICT: HEALTHY -- every streak recovered far below the bound.")
    return rc


def selftest() -> int:
    import tempfile
    ok = fail = 0

    def check(name, cond, detail=""):
        nonlocal ok, fail
        if cond:
            ok += 1
            print("  PASS  %s" % name)
        else:
            fail += 1
            print("  FAIL  %s  %s" % (name, detail))

    with tempfile.TemporaryDirectory() as td:
        check("A no driver logs at all exits 2, never 0", report(td, 6) == 2)

    now = datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M:%S")

    def write(td, name, body):
        with open(os.path.join(td, "driver_%s.log" % name), "w", encoding="utf-8") as fh:
            fh.write(body)

    # B. a WRAPPED record must count as ONE event, not two. This is the defect in the published
    #    counter, so the test that pins it must be able to fail against a grep-based count.
    with tempfile.TemporaryDirectory() as td:
        write(td, "x", "%s | WARNING | src.cluster.submit | ssh_timeout_diagnostic\n"
                       "cmd=['qstat', '-r'] elapsed=120.0s child_already_exited=True\n" % ts)
        s = scan(td, 6)
        check("B a line-WRAPPED timeout record counts as ONE event", s["total_events"] == 1,
              str(s["total_events"]))

    # C. the streak, not the event count, drives the verdict.
    with tempfile.TemporaryDirectory() as td:
        write(td, "x", "".join(
            "%s | WARNING | src.cluster.driver | [b] pull failed (%d  consecutive, 1 min down): x\n"
            % (ts, i) for i in range(1, 4)))
        s = scan(td, 6)
        check("C three isolated failures are HEALTHY (3 of 240)",
              s["lines"]["x"]["pull_worst"] == 3 and verdict(s) == 0)

    with tempfile.TemporaryDirectory() as td:
        write(td, "x", "%s | WARNING | src.cluster.driver | [b] pull failed (60  consecutive, "
                       "45 min down): x\n" % ts)
        s = scan(td, 6)
        check("D a streak at 25%% of the bound raises ATTENTION", verdict(s) == 1,
              str(s["lines"]["x"]))

    # E. an ops streak must be tracked SEPARATELY from a pull streak.
    with tempfile.TemporaryDirectory() as td:
        write(td, "x", "%s | WARNING | src.cluster.driver | [b] queue op failed (7 consecutive, "
                       "2 min): x\n" % ts)
        s = scan(td, 6)
        check("E queue-op failures land in ops_*, never in pull_*",
              s["lines"]["x"]["ops_worst"] == 7 and s["lines"]["x"]["pull_worst"] == 0)

    # F. an event OUTSIDE the window must not be counted.
    with tempfile.TemporaryDirectory() as td:
        old = (now - timedelta(hours=48)).strftime("%Y-%m-%d %H:%M:%S")
        write(td, "x", "%s | WARNING | src.cluster.submit | ssh_timeout_diagnostic "
                       "cmd=['qstat', '-r'] elapsed=120.0s\n" % old)
        check("F an event 48 h old is outside a 6 h window", scan(td, 6)["total_events"] == 0)

    # G. the fatal bound must be the one the LIVE code passes (240), not driver.py's own default 72.
    src = os.path.join(REPO, "src", "cluster", "campaign.py")
    live = None
    if os.path.isfile(src):
        with open(src, encoding="utf-8") as fh:
            m = re.search(r"max_consecutive_errors:\s*int\s*=\s*(\d+)", fh.read())
            live = int(m.group(1)) if m else None
    # ⚠ was `live is None or live == FATAL_CONSECUTIVE` -- if the regex ever stopped matching,
    # `live` became None and the DRIFT GUARD PASSED SILENTLY. A guard that cannot fail is not a
    # guard; a non-match is now itself a failure.
    check("G FATAL_CONSECUTIVE matches what campaign.py actually passes (non-match = FAIL)",
          live == FATAL_CONSECUTIVE,
          "campaign.py says %s, this file says %d" % (live, FATAL_CONSECUTIVE))

    # H: THE WRAP THAT ACTUALLY OCCURS -- inside the streak phrase, where the join broke the regex
    #    and understated six of twelve lines. Case B wrapped at a harmless point; this is the real one.
    with tempfile.TemporaryDirectory() as td:
        body = ("%s | WARNING | src.cluster.driver | [b] pull failed (149  consecutive, \n"
                "445.0 min  down): listing /home/ucestes/Scratch\n") % ts
        write(td, "x", body)
        s2 = scan(td, 6)
        check("H a wrap INSIDE the streak phrase still parses (the six-line understatement bug)",
              s2["lines"]["x"]["pull_worst"] == 149, str(s2["lines"]["x"]))

    # I: the LEGACY timestamp format must start a new record, not glue onto the previous one.
    with tempfile.TemporaryDirectory() as td:
        body = ("%s | WARNING | src.cluster.driver | [b] pull failed (5 consecutive, 1 min down): x\n"
                "%s,164 WARNING src.cluster.driver: [b] pull failed (200 consecutive, "
                "90 min down): y\n") % (ts, ts)
        write(td, "x", body)
        s3 = scan(td, 6)
        check("I the LEGACY `,mmm` timestamp starts a new record (h3 collapsed to one 625 KB blob)",
              s3["lines"]["x"]["pull_worst"] == 200, str(s3["lines"]["x"]))

    # J: logs present but NOTHING parseable must exit 2, never HEALTHY.
    with tempfile.TemporaryDirectory() as td:
        write(td, "x", "this file contains no timestamps and no streak lines at all\n")
        rcj = report(td, 6)
        check("J logs present but ZERO parsed -> exit 2, never a HEALTHY verdict", rcj == 2,
              "rc=%d" % rcj)

    print("\nselftest: %d passed, %d failed" % (ok, fail))
    return 0 if fail == 0 else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Distance to a transport-induced arm crash.")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--hours", type=float, default=6.0)
    ap.add_argument("--oneline", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.oneline:
        if not os.path.isdir(a.root):
            print("transport: root missing")
            return 2
        s = scan(a.root, a.hours)
        if not s["lines"]:
            print("transport: NO driver logs -- this check inspected nothing")
            return 2
        print(oneline(s))
        return verdict(s)
    return report(a.root, a.hours)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
