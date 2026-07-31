"""THE 2-MINUTE MONITORING CYCLE -- one command, the whole sweep, a compact verdict.

Tamer's standing order (2026-07-31): **monitor everything, constantly, every 2 minutes.** The reason
the previous session drifted to 20-40 minute gaps was friction -- six separate commands, each with its
own output format, none of which said "nothing changed, carry on". This is that sweep as ONE call.

    python docs/ops/cycle.py                 # the full sweep, ~7 s
    python docs/ops/cycle.py --note "..."     # ...and record what you were doing this cycle
    python docs/ops/cycle.py --ssh            # ...and also read cores/jobs off Myriad (adds ~5-20 s)

WHAT IT CHECKS (everything the campaign can plausibly fail at, cheapest first):
  1. docs/REMOTE_CONTROL.md          -- Tamer's inbound channel; flagged LOUDLY the cycle it changes
  2. the STOP_CAMPAIGN lever         -- present means someone (or something) asked for a halt
  3. campaign_guards.py <root> all   -- the six repo guards (freeze hash, rejects, transport, ...)
  4. docs/ops/arm_coverage.py        -- the guards CANNOT see a missing arm; this can (defect D14)
  5. docs/ops/budget_watch.py        -- per-(line, arm) authoring projection vs credited headroom
  6. driver-log freshness            -- a line can hold its process and stop progressing
  7. drift vs the RUNNING sha        -- what the live drivers execute vs what HEAD now says
  8. records + spend                 -- and the DELTA since the previous cycle, which is the real
                                        health signal: a flat record count across cycles is a stall

EXIT CODES -- read them, they are the point:
  0  all clear, nothing needs a human
  1  ATTENTION: something changed or is worth a look (new remote instruction, no new records, drift)
  2  RED: guards failed, the stop file exists, a driver log is stale, or the budget is projected short

Every run appends one line to docs/ops/watch/CYCLE_LOG.md and rewrites docs/ops/watch/STATE.json, so
the cadence is auditable after the fact -- "I monitored continuously" becomes a checkable claim rather
than an assertion, which is the standard the rest of this project is held to.

Nothing here mutates the campaign. It is safe at any cadence, including from a loop.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WATCH = REPO / "docs" / "ops" / "watch"
STATE_PATH = WATCH / "STATE.json"
LOG_PATH = WATCH / "CYCLE_LOG.md"
ROOT = REPO / "outputs" / "campaign_cluster_run4"
REMOTE = REPO / "docs" / "REMOTE_CONTROL.md"
ACK_FILE = REPO / "docs" / "ops" / "acknowledged_alarms.txt"

# The commit the LIVE drivers were launched from -- re-based 2026-07-30 by the memory relaunch
# (CAMPAIGN_EXECUTION_RECORD section 46). Change this ONLY when the drivers are actually relaunched;
# it is the reference for the drift invariant and a wrong value here silently disarms that check.
RUNNING_SHA = "c99716e"
DRIFT_PATHS = ("src", "scripts", "config", "prompts")

# A driver log older than this means its line has stopped writing -- the D14 failure mode, where the
# process is alive (so the supervisor never relaunches it) but no longer progressing.
STALE_DRIVER_MINUTES = 30.0


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], timeout: int = 120) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)
    except Exception as exc:  # noqa: BLE001 - a probe that cannot run is itself a finding
        return 99, f"<probe failed: {exc}>"
    return p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.exists() else ""


def _prev_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--note", default="", help="one line: what you are doing this cycle")
    ap.add_argument("--ssh", action="store_true", help="also read cores/jobs off Myriad")
    ap.add_argument("--quiet", action="store_true", help="print the verdict line only")
    args = ap.parse_args()

    WATCH.mkdir(parents=True, exist_ok=True)
    prev = _prev_state()
    stamp = _utc()
    alerts: list[str] = []      # exit 2
    attention: list[str] = []   # exit 1
    lines: list[str] = []

    if not ROOT.exists():
        print(f"RED  campaign root missing: {ROOT}", file=sys.stderr)
        return 2

    # 1. Tamer's channel, first, always -- anything he wrote outranks everything below it.
    remote_hash = _sha256(REMOTE)
    remote_changed = bool(prev) and remote_hash != prev.get("remote_control_sha", remote_hash)
    if remote_changed:
        attention.append("*** docs/REMOTE_CONTROL.md CHANGED -- READ IT NOW, before anything else ***")

    # 2. the stop lever
    stop_file = ROOT / "STOP_CAMPAIGN"
    if stop_file.exists():
        alerts.append(f"STOP_CAMPAIGN EXISTS at {stop_file} -- the campaign is being halted")

    # 3-5. the three monitors, filtered through the ACKNOWLEDGED ledger.
    #
    # Alarm hygiene is the whole point (docs/ops/acknowledged_alarms.txt: "make the KNOWN quiet so the
    # NEW is loud"). Two guard verdicts and two sentinel CRITICALs are permanently rc=2 because the
    # underlying ledgers are append-only and can never return green -- so a raw rc=2 every cycle would
    # train the operator to ignore rc=2, which is precisely how D15 survived ten hours. Anything in the
    # ledger is reported as (known); anything NOT in it is RED.
    acked = {ln.strip() for ln in ACK_FILE.read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.lstrip().startswith("#")} if ACK_FILE.exists() else set()

    guards_rc, guards_out = _run([sys.executable, "scripts/campaign_guards.py",
                                  str(ROOT.relative_to(REPO)), "all"], timeout=300)
    failing = [ln.split("]")[0].lstrip("[") for ln in guards_out.splitlines()
               if ln.startswith("[") and not ln.rstrip().endswith(" ok")]
    new_guards = [g for g in failing if f"guard:{g}" not in acked]
    known_guards = [g for g in failing if f"guard:{g}" in acked]
    if new_guards:
        alerts.append(f"campaign_guards: UNACKNOWLEDGED verdict(s) {', '.join(new_guards)} "
                      f"-- investigate, then either fix or add a REASONED entry to "
                      f"docs/ops/acknowledged_alarms.txt")
    elif guards_rc != 0 and not failing:
        attention.append(f"campaign_guards rc={guards_rc} but no failing guard parsed -- read the output")

    cov_rc, cov_out = _run([sys.executable, "docs/ops/arm_coverage.py"], timeout=120)
    full_lines = cov_out.count("5/5 arms submitted")
    if "VERDICT: ALL LINES FULL" not in cov_out:
        alerts.append("arm_coverage: A LINE IS MISSING AN ARM (defect D14) -- the six repo guards "
                      "cannot see this. Find which arm, and why it stopped being submitted.")
    sentinel_bad = re.findall(r"^\[sentinel\]\s+(CRITICAL|UNKNOWN)\s+(\S+)", cov_out, flags=re.M)
    new_sentinel = [f"{chk}:{sev}" for sev, chk in sentinel_bad if f"{chk}:{sev}" not in acked]
    known_sentinel = [f"{chk}:{sev}" for sev, chk in sentinel_bad if f"{chk}:{sev}" in acked]
    if new_sentinel:
        alerts.append(f"sentinel: UNACKNOWLEDGED verdict(s) {', '.join(new_sentinel)} -- a CRITICAL "
                      f"is a VALIDITY issue, not a slowdown. Run it to ground before anything else.")

    bud_rc, bud_out = _run([sys.executable, "docs/ops/budget_watch.py"], timeout=180)
    if bud_rc == 2:
        alerts.append("budget_watch rc=2 -- PROJECTED SHORTFALL. The confirmatory line stops if a key "
                      "runs dry. Check the real console balance, and tell Tamer.")

    # 6. driver-log freshness
    now = time.time()
    ages = {p.name: round((now - p.stat().st_mtime) / 60.0, 1) for p in sorted(ROOT.glob("driver*.log"))}
    stalest_name, stalest = ("", 0.0)
    if ages:
        stalest_name, stalest = max(ages.items(), key=lambda kv: kv[1])
        if stalest > STALE_DRIVER_MINUTES:
            alerts.append(f"{stalest_name} is {stalest:.0f} min stale (>{STALE_DRIVER_MINUTES:.0f}) "
                          f"-- that line has stopped progressing (defect D14)")

    # 7. drift vs the RUNNING sha, not vs HEAD
    _, drift_out = _run(["git", "diff", "--name-only", RUNNING_SHA, "HEAD", "--", *DRIFT_PATHS])
    drift = [ln for ln in drift_out.splitlines() if ln.strip() and not ln.startswith("<")]

    # 8. records + spend, and the DELTA that actually tells you whether it is moving
    _, st_out = _run([sys.executable, "scripts/campaign_guards.py",
                      str(ROOT.relative_to(REPO)), "status"], timeout=120)
    records = spend = None
    m = re.search(r"records=(\d+)", st_out)
    if m:
        records = int(m.group(1))
    m = re.search(r"spend_total=\$([0-9.]+)", st_out)
    if m:
        spend = float(m.group(1))
    d_rec = (records - prev["records"]) if records is not None and isinstance(prev.get("records"), int) else None
    prev_ts = prev.get("written_utc")
    if d_rec == 0 and prev_ts:
        attention.append(f"no new record since the previous cycle ({prev_ts}) -- normal for a few "
                         f"cycles at 4-6 h per training, a stall if it persists across many")

    cores = jobs = ""
    if args.ssh:
        rc, out = _run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", "myriad",
                        'Q=$(qstat -u ucestes | tail -n +3); '
                        'echo "run=$(echo "$Q" | awk "\\$5==\\"r\\"" | grep -c .)"; '
                        'echo "qw=$(echo "$Q" | awk "\\$5 ~ /qw/" | grep -c .)"; '
                        'echo "cores=$(echo "$Q" | awk "\\$5==\\"r\\" {s+=\\$9} END {print s+0}")"'],
                       timeout=90)
        if rc == 0:
            got = dict(ln.split("=", 1) for ln in out.splitlines() if "=" in ln)
            cores = got.get("cores", "")
            jobs = f"{got.get('run', '?')}r/{got.get('qw', '?')}q"
        else:
            attention.append("ssh to myriad failed this cycle (the campaign is unaffected; retry next cycle)")

    state = {
        "written_utc": stamp,
        "note": args.note,
        "records": records,
        "records_delta": d_rec,
        "spend_total_usd": spend,
        "guards_rc": guards_rc,
        "guards_failing": failing,
        "guards_known_acked": known_guards,
        "sentinel_known_acked": known_sentinel,
        "lines_with_all_arms": full_lines,
        "budget_rc": bud_rc,
        "driver_log_age_minutes": ages,
        "stalest_driver": [stalest_name, stalest],
        "running_sha": RUNNING_SHA,
        "head_sha": _run(["git", "rev-parse", "--short", "HEAD"])[1],
        "drift_vs_running_sha": drift,
        "remote_control_sha": remote_hash,
        "remote_control_changed": remote_changed,
        "stop_file_present": stop_file.exists(),
        "cores": cores,
        "jobs": jobs,
        "alerts": alerts,
        "attention": attention,
    }
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    verdict = "RED" if alerts else ("ATTN" if attention else "OK")
    summary = (f"{stamp}  {verdict}  records={records}"
               f"{'' if d_rec is None else f' ({d_rec:+d})'}  spend=${spend}  guards={guards_rc}  "
               f"arms_full={full_lines}/10  budget={bud_rc}  stalest={stalest:.1f}m  "
               f"drift={len(drift)}" + (f"  cores={cores}" if cores else "")
               + (f"  {args.note}" if args.note else ""))
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(summary + "\n")

    if not args.quiet:
        for a in alerts:
            lines.append("RED   " + a)
        for a in attention:
            lines.append("ATTN  " + a)
        if known_guards or known_sentinel:
            lines.append("known " + ", ".join(known_guards + known_sentinel)
                         + "  (acknowledged in docs/ops/acknowledged_alarms.txt -- re-read the entry, "
                           "each one carries its own RE-TRIAGE trigger)")
        if drift:
            lines.append(f"note  drift vs running sha {RUNNING_SHA}: {', '.join(drift)} "
                         f"(prove unreachable with docs/ops/import_closure.py, or re-base at restart)")
        for ln in lines:
            print(ln)
    print(summary)
    return 2 if alerts else (1 if attention else 0)


if __name__ == "__main__":
    raise SystemExit(main())
