"""CRASH-RECOVERY WATCHDOG -- catches a campaign unit that died and never came back.

=============================== WHY THIS EXISTS ===============================================
On 2026-08-03 the core line's `bayes_opt` search pipeline crashed during the 7-hour transport
outage and never resumed. It went unnoticed for hours. The failure was NOT a lack of detection:
`campaign_guards.py` printed the crash and returned RC=2. The failure was that **RC=2 had been
continuously red for days** on an older, unrelated issue, so a NEW fault inside that aggregate
changed nothing observable. Signal saturation, not blindness.

`src/cluster/campaign.py` catches a per-unit crash deliberately -- "one unit must not sink the
ladder" -- records `ok: False`, and moves on WITHOUT retrying. The supervisor only relaunches a
driver that EXITS, and a driver whose other pipelines are healthy does not exit. So a crashed
unit inside a living driver stays dead indefinitely, silently, while the line looks fine.

=============================== WHAT IT CHECKS ================================================
For every `pipeline crashed` event in every driver log, it asks whether that arm ACTUALLY
resumed, using TWO INDEPENDENT SIGNALS:

  1. LOG: any later activity for a unit whose name CONTAINS the arm, and
  2. ARCHIVE: any record.json for that arm with an mtime after the crash.

Both are needed because either alone is wrong in a way that matters:
  * exact-token matching on the log gives FALSE POSITIVES -- the crash line names the ARM
    (`[placebo]`) while later work is logged under the BATCH
    (`leg4_leg_qwen3_5_9b_placebo_g3`). A first version of this check used exact matching and
    reported 7 dead units when only 1 was dead;
  * records alone give FALSE NEGATIVES -- a unit can be legitimately working with nothing newly
    archived yet (measured live: nemotron's `scalar_cvar5` had 0 newer records but was plainly
    active in the log).

It ALSO tracks state between runs so a NEW death is loud even when older known ones persist --
which is precisely the failure mode that let bayes_opt hide.

=============================== WHAT IT DOES NOT DO ===========================================
It does not restart anything. Restarting a driver is a judgement call with real consequences
(it re-stampedes the login node, and the campaign is irreplaceable), so this reports and lets a
human decide. It reads logs and file mtimes; it never touches the archive or the cluster.

USAGE
    python docs/ops/crash_watchdog.py --once       # exit 0 clean, 1 = something is dead
    python docs/ops/crash_watchdog.py              # loop, default 300 s
    python docs/ops/crash_watchdog.py --selftest   # no filesystem, proves the logic

Printed output is ASCII-only (this repo's console is cp1251).
"""

from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import pathlib
import re
import sys
import time

ROOT = "outputs/campaign_cluster_run4"
_HERE = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(_HERE, "watch", "CRASH_WATCHDOG.log")
STATE_PATH = os.path.join(_HERE, "watch", ".crash_watchdog_state.json")

BST = dt.timedelta(hours=1)                 # driver logs are Europe/London local
TS_PIPE = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| (\w+)")
TS_COMMA = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ (\w+)")
UNIT = re.compile(r"\[([A-Za-z0-9_.\-]+)\]")
CRASH_MARK = "pipeline crashed"
DEFAULT_INTERVAL = 300.0


def parse_ts(raw: str):
    """Both log formats. The older `,%f` shape existed on launch day and a first version of this
    check silently skipped it, which hid every crash from 2026-07-28."""
    for rx in (TS_PIPE, TS_COMMA):
        m = rx.match(raw)
        if m:
            return dt.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S") - BST
    return None


#: Every arm token that can appear in a unit name. Needed because two roster arms are PREFIXES of
#: two others (`scalar` of `scalar_cvar5`, `placebo` of `placebo_shuffled`), so "does this unit name
#: arm X" is only answerable against the whole roster.
_KNOWN_ARMS = ("placebo_shuffled", "scalar_cvar5", "distributional", "scalar", "placebo",
               "random_search", "bayes_opt", "cma_es", "tpe")


def _names_arm(unit: str, arm: str) -> bool:
    """Does this unit name THIS arm, as a whole token rather than as a substring?

    ⚠⚠ `arm in unit` CREDITED RECOVERY FROM A DIFFERENT ARM (auditor, 2026-08-04, RUN 21).
    The live roster is distributional / scalar / placebo / scalar_cvar5 / placebo_shuffled, and
    **`scalar` is a substring of `scalar_cvar5`, `placebo` of `placebo_shuffled`.** So a crashed
    `scalar` unit was marked recovered by any later log line naming `scalar_cvar5`, and a crashed
    `placebo` by any line naming `placebo_shuffled` -- silently clearing a crash on the strength of
    a different arm's progress, which is the one thing this watchdog exists to prevent. The
    selftest's own other-arm case used `bayes_opt` vs `c1_tpe_c22` and never exercised the prefix
    pair, so it passed throughout. Units are `_`-separated (`leg8_leg_sonnet_5_scalar_test_p01`), so
    a token match on that separator is both correct and sufficient.
    """
    padded = "_" + unit + "_"
    if ("_" + arm + "_") not in padded:
        return False
    # ⚠ AND MY FIRST FIX FOR THIS WAS ALSO WRONG, WHICH IS WHY THE FALSIFIER EXISTS. Splitting on
    # "_" does not help: `scalar_cvar5` SPLITS INTO the token `scalar`, so a token test still
    # credited the wrong arm. The property that actually separates them is MAXIMALITY -- if a LONGER
    # known arm also matches at this position, the unit names that one, not this one.
    return not any(len(a) > len(arm) and ("_" + a + "_") in padded for a in _KNOWN_ARMS)


def is_recovered(arm: str, crash_ts, events, newer_records: int) -> bool:
    """Pure, so --selftest can prove both signals and their interaction."""
    resumed_log = any(ts > crash_ts and unit and _names_arm(unit, arm) for ts, unit in events)
    return bool(resumed_log or newer_records > 0)


#: `driver_<line>.log` names the CORE line "core", but its archive directories are `search`,
#: `test` and `frozen` -- no directory contains the token "core" at all. So `root.glob("*core*")`
#: matched NOTHING and `_count_newer_records` returned 0 unconditionally **for the one line whose
#: crash this watchdog was written for** (auditor, 2026-08-04, RUN 21). Two consequences: the core
#: line ran on the log signal alone, which this file's own docstring says is insufficient; and the
#: alarm string "no log activity and no newer records" asserted a measurement that never happened.
#: Mapped explicitly rather than by pattern, so a rename fails loudly instead of silently matching 0.
_LINE_DIR_TOKENS = {"core": ("test", "search", "frozen")}


def _count_newer_records(line: str, arm: str, crash_ts) -> tuple[int, bool]:
    """Returns (count, measured). `measured=False` means NO directory matched this line at all.

    The second element exists so a caller can tell "I looked and found none" from "I could not
    look", which is the P230/P232 rule: a verdict channel must not share a value with a
    could-not-measure channel.
    """
    key = line.replace("-", "_").replace(".", "_")
    n = 0
    root = pathlib.Path(ROOT)
    if not root.is_dir():
        return 0, False
    subs = []
    for token in _LINE_DIR_TOKENS.get(key, ("*%s*" % key,)):
        subs.extend(root.glob(token if "*" in token else token))
    if not subs:
        return 0, False
    for sub in subs:
        armdir = sub / arm
        if not armdir.is_dir():
            continue
        for rec in armdir.rglob("record.json"):
            try:
                if dt.datetime.utcfromtimestamp(rec.stat().st_mtime) > crash_ts:
                    n += 1
            except OSError:
                pass
    return n, True


def scan() -> list[dict]:
    """Every arm that crashed and shows NO evidence of having resumed."""
    dead = []
    for path in sorted(glob.glob(os.path.join(ROOT, "driver_*.log"))):
        line = os.path.basename(path)[len("driver_"):-len(".log")]
        events, crashes = [], {}
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as fh:
                for raw in fh:
                    ts = parse_ts(raw)
                    if ts is None:
                        continue
                    u = UNIT.search(raw)
                    unit = u.group(1) if u else None
                    events.append((ts, unit))
                    if CRASH_MARK in raw and unit:
                        if unit not in crashes or ts > crashes[unit]:
                            crashes[unit] = ts
        except OSError:
            continue
        for arm, cts in crashes.items():
            newer, measured = _count_newer_records(line, arm, cts)
            if not is_recovered(arm, cts, events, newer):
                dead.append({"line": line, "arm": arm, "crashed_utc": cts.strftime("%Y-%m-%dT%H:%M:%SZ"),
                             "age_h": round((dt.datetime.utcnow() - cts).total_seconds() / 3600.0, 1),
                             # False => NO archive directory matched this line, so the record signal
                             # was never evaluated. The alarm text must not claim it was.
                             "record_signal_measured": measured})
    return dead


def _load_state() -> set:
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as fh:
            return set(json.load(fh).get("known", []))
    except Exception:                                       # noqa: BLE001
        return set()


def _save_state(keys: set) -> None:
    try:
        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        with open(STATE_PATH, "w", encoding="utf-8") as fh:
            json.dump({"known": sorted(keys)}, fh)
    except Exception:                                       # noqa: BLE001
        pass


def _log(msg: str) -> None:
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write("%s  %s\n" % (dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), msg))
    except Exception:                                       # noqa: BLE001
        pass


def report(quiet: bool = False) -> int:
    dead = scan()
    keys = {"%s/%s" % (d["line"], d["arm"]) for d in dead}
    known = _load_state()
    new = keys - known
    _save_state(keys)

    if not dead:
        line = "CLEAN -- every crashed unit shows evidence of having resumed"
        _log(line)
        if not quiet:
            print(line)
        return 0

    for d in sorted(dead, key=lambda x: -x["age_h"]):
        k = "%s/%s" % (d["line"], d["arm"])
        tag = "*** NEW ***" if k in new else "(known)"
        msg = "DEAD UNIT %-12s %-22s %-24s crashed %s, %.1f h ago, no log activity and no newer records" % (
            tag, d["line"], d["arm"], d["crashed_utc"], d["age_h"])
        _log(msg)
        print(msg)
    if new:
        hint = ("=> A UNIT DIED AND WILL NOT SELF-HEAL. campaign.py catches a per-unit crash without "
                "retrying, and the supervisor only relaunches a driver that EXITS -- a living driver "
                "with other healthy pipelines never does. Restarting that ONE line resumes it.")
        _log(hint)
        print(hint)
    return 1


def _selftest() -> int:
    T = dt.datetime(2026, 8, 2, 12, 0, 0)
    later, earlier = T + dt.timedelta(hours=1), T - dt.timedelta(hours=1)
    cases = [
        ("exact-token-resumed",   ("placebo", [(later, "placebo")], 0), True),
        # THE false positive that made a first version report 7 dead when 1 was:
        ("batch-name-resumed",    ("placebo", [(later, "leg4_leg_qwen3_5_9b_placebo_g3")], 0), True),
        ("records-only-resumed",  ("bayes_opt", [(earlier, "bayes_opt")], 5), True),
        # THE false negative records-alone would give (measured live on nemotron):
        ("log-only-resumed",      ("scalar_cvar5", [(later, "leg7_scalar_cvar5_g4")], 0), True),
        ("genuinely-dead",        ("bayes_opt", [(earlier, "c1_bayes_opt_c24")], 0), False),
        ("no-events-dead",        ("bayes_opt", [], 0), False),
        ("other-arm-not-credit",  ("bayes_opt", [(later, "c1_tpe_c22")], 0), False),
    ]
    bad = 0
    print("crash_watchdog --selftest (no filesystem)")
    for name, (arm, events, newer), expected in cases:
        got = is_recovered(arm, T, events, newer)
        ok = got == expected
        bad += 0 if ok else 1
        print("  %-24s expect %-5s got %-5s %s" % (name, expected, got, "OK" if ok else "FAIL"))

    print("  --- timestamp parsing (a first version skipped the comma format and hid launch-day crashes) ---")
    for name, raw, should in (
        ("pipe-format",  "2026-08-03 00:20:08 | ERROR   | x | [bayes_opt] pipeline crashed", True),
        ("comma-format", "2026-07-28 23:14:47,886 ERROR src.cluster.campaign: [placebo] pipeline crashed", True),
        ("not-a-stamp",  "Traceback (most recent call last):", False),
    ):
        got = parse_ts(raw) is not None
        ok = got == should
        bad += 0 if ok else 1
        print("  %-24s expect %-5s got %-5s %s" % (name, should, got, "OK" if ok else "FAIL"))

    print("")
    print("selftest: %d FAILED" % bad if bad else "selftest: ALL PASS")
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Detect campaign units that crashed and never resumed.")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--interval-secs", type=float, default=DEFAULT_INTERVAL)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.once:
        return report(args.quiet)
    print("crash_watchdog: every %.0fs -> %s" % (args.interval_secs, LOG_PATH))
    while True:
        try:
            report(args.quiet)
        except Exception as exc:                            # noqa: BLE001
            _log("WATCHDOG-ERROR %s: %s" % (type(exc).__name__, exc))
        time.sleep(args.interval_secs)


if __name__ == "__main__":
    sys.exit(main())
