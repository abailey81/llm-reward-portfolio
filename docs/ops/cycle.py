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
  5. docs/ops/budget_watch.py        -- per-(line, arm) authoring projection; REPORTED, never RED
  6. driver-log freshness            -- a line can hold its process and stop progressing
  7. drift vs the RUNNING sha        -- what the live drivers execute vs what HEAD now says
  8. records + spend                 -- and the DELTA since the previous cycle, which is the real
                                        health signal: a flat record count across cycles is a stall
  9. THE RESULTS LAYER (see below)   -- science_watch.py + results_audit.py, EVERY cycle

** 9. THE RESULTS LAYER -- Tamer, 2026-07-31 **

    "when you monitor, very deeply and strictly check not only the processes, they must be
     accurate and logical and meaningful as well, but also the RESULTS, they must be very
     logical, correct and meaningful."

Checks 1-8 are all PROCESS: is it running, is it placing, is it spending, is it drifting. A campaign
can pass every one of them and be producing meaningless numbers -- which is the standing rule that a
green check proves execution, never truth. So every cycle now also runs the two tools that open the
science, both of which cost ~1.8 s (MEASURED 2026-07-31, so there is no tiering and no excuse):

  * docs/ops/science_watch.py   -- is the search SEARCHING (non-zero spread), is the reflection chain
                                   ADVANCING, are the scored-record invariants (400k steps, the R115
                                   execution floor) intact, are there impossible numbers?
  * docs/ops/results_audit.py   -- opens every record: reward_source_hash == sha256(source), schema,
                                   ranges, finiteness, the fed block RE-DERIVED from every LLM-arm
                                   prompt, authored-program diversity, PopArt engagement, the D17
                                   repeated-fraction anomaly hunt.

Their numbers are extracted into STATE.json and DIFFED against the previous cycle, because on a live
run the dangerous event is not a bad absolute value -- it is a value that MOVED. Four quantities are
hard validity invariants and go RED on any non-zero reading (a construct-validity leak, a program
shared across arms, a source-hash mismatch, a non-finite metric); the rest escalate on CHANGE.

⚠ EXTRACTION FAILS LOUD. If a regex stops matching -- because a tool's output format changed -- the
cycle says so rather than reporting the check as passed. A monitor that silently stops monitoring is
the D15 failure mode, and it is worse than no monitor at all.

EXIT CODES -- read them, they are the point:
  0  all clear, nothing needs a human
  1  ATTENTION: something changed or is worth a look (new remote instruction, no new records, drift,
     the budget projection, a science quantity that moved)
  2  RED: guards failed, the stop file exists, a driver log is stale, or a RESULTS invariant broke

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


# --------------------------------------------------------------------------------------------------
# THE RESULTS LAYER
# --------------------------------------------------------------------------------------------------
#: Quantities pulled out of the two science tools. Each entry is (key, regex, source) where source is
#: "sw" (science_watch) or "ra" (results_audit). Group 1 of every regex is an integer.
#:
#: These are deliberately ANCHORED on distinctive words rather than on line position, so a tool
#: gaining a line does not silently break extraction -- and any that fails to match is REPORTED,
#: never treated as zero. "Absent" and "zero" are different facts and must never be conflated.
_SCIENCE_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("sw_records",          r"SCIENCE WATCH:\s+(\d+)\s+records",                          "sw"),
    ("sw_budget_breaches",  r"train_safe_call_count\s*!=\s*400,000\s*:\s*(\d+)",           "sw"),
    ("sw_r115_breaches",    r"R115 floor breaches[^:]*:\s*(\d+)",                          "sw"),
    ("sw_impossible",       r"impossible/non-finite scores\s*:\s*(\d+)",                   "sw"),
    ("ra_records",          r"results_audit:\s+(\d+)\s+records",                           "ra"),
    ("ra_dup_runid",        r"duplicate \(root, run_id\)\s*:\s*(\d+)",                     "ra"),
    ("ra_hash_mismatch",    r"reward_source_hash mismatches\s*:\s*(\d+)",                  "ra"),
    ("ra_out_of_range",     r"out-of-range gen/seed\s*:\s*(\d+)",                          "ra"),
    ("ra_non_finite",       r"non-finite metrics\s*:\s*(\d+)",                             "ra"),
    ("ra_scalar_leaks",     r"scalar prompts leaking a tail statistic\s*:\s*(\d+)",        "ra"),
    ("ra_cross_arm_shared", r"programs identical ACROSS arms\s*:\s*(\d+)",                 "ra"),
    ("ra_popart_engaged",   r"engaged\s+(\d+)\s+\(",                                       "ra"),
    ("ra_popart_pinned",    r"pinned at the floor\s+(\d+)\s+\(",                           "ra"),
    ("ra_popart_breaks",    r"invariant sigma_max ==[^:]*:\s*(\d+)",                       "ra"),
)

#: Non-zero on ANY of these is a validity failure, not a slowdown -- it means the experiment is no
#: longer measuring what it was registered to measure. Each names the hypothesis it would destroy.
_HARD_ZERO: dict[str, str] = {
    "ra_scalar_leaks":     "a SCALAR-arm prompt contains a tail statistic -- H2's manipulation has "
                           "leaked and the arm contrast is no longer clean",
    "ra_cross_arm_shared": "an authored program is IDENTICAL across two arms -- the arms are no "
                           "longer independent draws and H2 compares contaminated populations",
    "ra_hash_mismatch":    "reward_source_hash != sha256(reward_source) -- an archived reward is not "
                           "the reward that was run, so the record cannot be replayed",
    "ra_non_finite":       "a non-finite metric is archived -- it will propagate into the analysis",
    "ra_out_of_range":     "a generation or seed is outside the registered range",
    "sw_impossible":       "an impossible/non-finite score is present in a scored record",
    "sw_budget_breaches":  "a scored record's train_safe_call_count != 400,000 -- the registered "
                           "training budget was not honoured",
    "ra_popart_breaks":    "the PopArt invariant sigma_max == max(floor, raw_rms_max) is broken",
}

#: Quantities that legitimately grow on a live run. A rise is worth a LOOK, never a halt -- but it
#: must be SEEN, because "it drifted slowly" is how a real regression hides in a healthy-looking run.
_WATCH_RISING: dict[str, str] = {
    "sw_r115_breaches": "R115 execution-floor breaches",
    "ra_dup_runid":     "duplicate (root, run_id) pairs -- D18 baseline is 1",
}


def _results_layer(prev: dict, alerts: list[str], attention: list[str]) -> dict:
    """Run the two science tools, extract their numbers, and judge them against the invariants.

    Returns the extracted quantities for STATE.json. Escalates through `alerts` / `attention` in
    place. Never raises: a probe that cannot run is itself reported as a finding.
    """
    sw_rc, sw_out = _run([sys.executable, "docs/ops/science_watch.py"], timeout=300)
    ra_rc, ra_out = _run([sys.executable, "docs/ops/results_audit.py"], timeout=300)
    text = {"sw": sw_out, "ra": ra_out}

    got: dict[str, int | None] = {}
    unparsed: list[str] = []
    for key, pattern, src in _SCIENCE_FIELDS:
        m = re.search(pattern, text[src])
        if m:
            got[key] = int(m.group(1))
        else:
            got[key] = None
            unparsed.append(key)

    # A tool that fails to RUN, and a field that fails to PARSE, are both blind spots. Say so.
    if ra_rc == 2:
        alerts.append("results_audit rc=2 -- a HARD record invariant failed. Read its output in full "
                      "before anything else; this is a validity failure, not a slowdown.")
    if sw_rc not in (0, 1):
        alerts.append(f"science_watch rc={sw_rc} -- the science check could not complete")
    if unparsed:
        attention.append(f"results layer: could NOT parse {', '.join(unparsed)} -- the tool's output "
                         f"format may have changed. These checks are BLIND until fixed; absent is "
                         f"not the same as zero.")

    for key, why in _HARD_ZERO.items():
        val = got.get(key)
        if val:
            alerts.append(f"RESULTS INVARIANT BROKEN -- {key}={val}: {why}")

    for key, label in _WATCH_RISING.items():
        val, was = got.get(key), (prev.get("science") or {}).get(key)
        if isinstance(val, int) and isinstance(was, int) and val > was:
            attention.append(f"{label} rose {was} -> {val} since the previous cycle -- identify the "
                             f"new one and confirm it is the known mechanism, not a new failure")

    # R115 BINDING means a fallback-contaminated candidate currently TOPS its arm. That is the floor
    # doing its job (record §35), but the moment it happens on a line whose winner is about to be
    # frozen it stops being academic -- so its ARRIVAL is surfaced, not just its presence.
    binding = "R115 IS BINDING" in sw_out
    got["sw_r115_binding"] = int(binding)
    if binding and not (prev.get("science") or {}).get("sw_r115_binding"):
        attention.append("R115 is now BINDING -- a fallback-contaminated candidate tops its arm. "
                         "Expected behaviour of the floor; confirm the affected line and that the "
                         "best ELIGIBLE candidate is the one that gets frozen.")

    got["science_watch_rc"] = sw_rc
    got["results_audit_rc"] = ra_rc
    return got


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
    info: list[str] = []        # reported every cycle, never changes the exit code
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

    # 5. the budget. TAMER, 2026-07-31: "The budget is fine, cross it out, I will just top up whenever
    # needed, I watch the balance. Just make sure you precisely monitor it as well."
    #
    # So the OWNER holds the balance and the top-up decision, and this check stops being a run-stopper.
    # It is NOT dropped -- it is downgraded from RED to a REPORTED number, because the thing it was
    # comparing against was never observable to us: `budget_watch.CREDIT` is a LEDGER ESTIMATE from a
    # 2026-07-28 console quote (record §49.3), and Tamer tops up ad hoc, so the credit side of that
    # comparison is stale by design. Escalating on a number we cannot observe is the alarm-hygiene
    # failure this file exists to prevent. What we CAN observe precisely -- spend to date and the
    # projected remaining authoring cost -- is extracted and logged every cycle instead.
    bud_rc, bud_out = _run([sys.executable, "docs/ops/budget_watch.py"], timeout=180)
    budget: dict[str, dict[str, float]] = {}
    for m in re.finditer(r"^(anthropic|openrouter)\s+spent \$\s*([0-9.]+)\s*\+ still to author "
                         r"\$\s*([0-9.]+)\s*= \$\s*([0-9.]+)", bud_out, flags=re.M):
        budget[m.group(1)] = {"spent": float(m.group(2)), "to_author": float(m.group(3)),
                              "projected_total": float(m.group(4))}
    if not budget:
        attention.append("budget_watch: could not parse the per-provider projection -- that number is "
                         "BLIND this cycle, which is not the same as healthy")
    else:
        for prov, b in sorted(budget.items()):
            was = ((prev.get("budget") or {}).get(prov) or {}).get("spent")
            delta = f" ({b['spent'] - was:+.4f} this cycle)" if isinstance(was, (int, float)) else ""
            info.append(f"budget {prov:<10} spent ${b['spent']:.4f}{delta}  + to author "
                        f"${b['to_author']:.4f}  = projected ${b['projected_total']:.4f}")

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

    # MONOTONICITY. The archive and the spend ledgers are both APPEND-ONLY, so neither count can ever
    # fall. A decrease is not a slowdown -- it means records were deleted, a ledger was truncated, or
    # the monitor is pointed at a different root than it was last cycle. Any of those invalidates the
    # numbers being reported, so it is RED rather than ATTN. (Added 2026-07-31 after the budget print
    # was widened to 4 dp and the first cross-format comparison produced a spurious -$0.0034: the
    # artefact was harmless, but nothing in the cycle would have told me a REAL one was impossible.)
    prev_spend = prev.get("spend_total_usd")
    if isinstance(d_rec, int) and d_rec < 0:
        alerts.append(f"RECORD COUNT FELL {prev['records']} -> {records}. The archive is append-only; "
                      f"a decrease means deletion, a truncated tree, or a changed root.")
    if isinstance(spend, (int, float)) and isinstance(prev_spend, (int, float)) and spend < prev_spend:
        alerts.append(f"SPEND TOTAL FELL ${prev_spend} -> ${spend}. The spend ledgers are append-only; "
                      f"a decrease means a ledger was truncated, rewritten, or replaced.")

    if d_rec == 0 and prev_ts:
        attention.append(f"no new record since the previous cycle ({prev_ts}) -- normal for a few "
                         f"cycles at 4-6 h per training, a stall if it persists across many")

    # 9. THE RESULTS LAYER -- are the numbers themselves logical, correct and meaningful?
    science = _results_layer(prev, alerts, attention)

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
        "budget": budget,
        "science": science,
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
    # `sci=` is the results layer in one token: OK when every hard invariant reads zero, otherwise the
    # broken ones by name. r115 is carried separately because it is expected to move and its VALUE is
    # the signal. A cadence log that records only process health cannot evidence "the results were
    # monitored", which is precisely the claim Tamer asked to be able to check.
    broken = [k for k in _HARD_ZERO if science.get(k)]
    sci = "OK" if not broken else "!" + ",".join(broken)
    summary = (f"{stamp}  {verdict}  records={records}"
               f"{'' if d_rec is None else f' ({d_rec:+d})'}  spend=${spend}  guards={guards_rc}  "
               f"arms_full={full_lines}/10  budget={bud_rc}  stalest={stalest:.1f}m  "
               f"drift={len(drift)}  sci={sci}  r115={science.get('sw_r115_breaches')}"
               f"{'B' if science.get('sw_r115_binding') else ''}"
               + (f"  cores={cores}" if cores else "")
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
        lines.append(
            "sci   records sw={sw}/ra={ra}  r115={r115}{b}  popart engaged={eng}/pinned={pin}  "
            "leaks={lk} cross-arm={xa} hash={hm} non-finite={nf}".format(
                sw=science.get("sw_records"), ra=science.get("ra_records"),
                r115=science.get("sw_r115_breaches"),
                b=" BINDING" if science.get("sw_r115_binding") else "",
                eng=science.get("ra_popart_engaged"), pin=science.get("ra_popart_pinned"),
                lk=science.get("ra_scalar_leaks"), xa=science.get("ra_cross_arm_shared"),
                hm=science.get("ra_hash_mismatch"), nf=science.get("ra_non_finite")))
        for ln in info:
            lines.append("info  " + ln)
        for ln in lines:
            print(ln)
    print(summary)
    return 2 if alerts else (1 if attention else 0)


if __name__ == "__main__":
    raise SystemExit(main())
