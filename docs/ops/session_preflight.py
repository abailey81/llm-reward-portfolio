"""SESSION PREFLIGHT — one command that PROVES the campaign's state, so nothing rests on memory.

WHY THIS EXISTS (2026-08-01, RUN 12 close). The session model collapsed from four lanes to two, and
the surviving BUILDER session inherits ops + the monitor line + coord. The handover brief lists what
to check; a list is only as good as the reader's diligence at 3 a.m. **This makes the check
mechanical.** It was written immediately after I nearly handed over without D21 (reboot recovery) —
not because the risk was live (it is resolved) but because I had to REMEMBER to look, and the next
person will not.

WHAT IT IS NOT: a re-implementation. Every check either reads an artefact the campaign already
maintains or shells out to the tool that already owns that truth (`freeze.py`, `audit_reproducibility`,
`openitems.py`). Duplicating a check is how two instruments come to disagree about the same fact.

READ-ONLY. Touches no archive, submits nothing, changes no design.

    python docs/ops/session_preflight.py           # fast (~5 s): the state that can kill a run
    python docs/ops/session_preflight.py --full    # + freeze, reproducibility, board
#
# ⚠ --full is ~200 s, NOT the '~60 s' this line advertised until 2026-08-04 (F12). It grew
# with the archive; a session that budgets 60 s for it either kills it or concludes it hung.
# Re-measure and correct this number rather than letting it drift again.

EXIT: 0 all clear · 1 ATTENTION (something needs a human) · 2 FAIL (a run-killer is live).
"""
from __future__ import annotations

import calendar
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUN = REPO / "outputs" / "campaign_cluster_run4"
CYCLE_LOG = REPO / "docs" / "ops" / "watch" / "CYCLE_LOG.md"
MIRROR = Path("D:/llm_rp_archive_mirror/campaign_cluster_run4")
DISK_FLOOR_GB = 20.0          # same floor scripts/sentinel.py::check_disk enforces
CYCLE_STALE_S = 150.0         # the mandate's "~2 minutes" — a FLOOR, never the whole test (P205)
CYCLE_SLEEP_S = 30.0          # cycle_loop.sh INTERVAL default; the sleep between sweeps
CYCLE_BUDGET_CAP_S = 900.0    # however slow sweeps get, a silent loop is reported within 15 min

#: The subject prefix and the SOLE path `docs/ops/publish_status.sh:527` gives its auto-commits
#: (`git commit -q --only docs/RUN4_STATUS.md -m "status: ..."`).
#: ⚠ THE SUBJECT ALONE IS NOT PROOF OF CONTENT, AND THIS REPOSITORY HOLDS THE COUNTEREXAMPLE.
#: Commit d7b85965, subject "status: T+147h38m - 10/12 lines up, ...", carries 366 insertions and 46
#: deletions across SIX files: CHANGELOG.md, docs/RUN4_STATUS.md, docs/ops/run_record_layers.sh,
#: docs/ops/session_preflight.py, docs/ops/stage_eta.py and docs/ops/watch/FLAWLESS_LEDGER.md.
#: (An earlier version of this comment listed five, omitting docs/RUN4_STATUS.md and so attributing
#: all 366 insertions to the other five. Corrected on an auditor's count, verified with
#: `git show --stat d7b85965`.) It was a bare `git commit` sweeping a dirty index, which is exactly
#: why `--only` was added the same day (P251). A subject-only test would have graded that commit as
#: safe to leave unpushed. So check_git_backup requires BOTH: the prefix AND a file set of exactly
#: this one path.
_PUBLISHER_COMMIT_PREFIX = "status:"
_PUBLISHER_COMMIT_PATH = "docs/RUN4_STATUS.md"
#: How many publisher commits may sit unpushed before the row stops calling it a race.
#: ⚠ MEASURE IT WITH THIS EXACT COMMAND, because an earlier version of this comment quoted
#: "median 77 s, mean 76 s, max 113 s" from a window over ALL branch commits rather than publisher
#: commits, and no publisher window reproduces it -- an auditor caught that `mean < median` is
#: impossible for this right-skewed distribution:
#:     git log --format=%ct --grep '^status:' -n 101
#: Over the newest 100 publisher gaps (2026-08-04): median 78 s, mean 83.7 s, min 68 s, max 185 s.
#: Five unpushed is therefore about SIX AND A HALF MINUTES of a stuck publisher -- not the "~10 min"
#: an even earlier version claimed. Crossing it IS the dead-publisher detector, and is why grading
#: the race as OK is not a weakening. `check_status_page` (NOT "check_publish_loop", which does not
#: exist anywhere in this repository) quotes "~67 s" from publish_loop.sh's configured sleep; the
#: measured spacing is longer because the sweep itself takes time.
_PUBLISHER_RACE_MAX = 5

OK, ATTN, FAIL = "OK", "ATTENTION", "FAIL"
_rows: list[tuple[str, str, str]] = []


def add(name: str, status: str, detail: str) -> None:
    _rows.append((name, status, detail))


def sh(args: list[str], timeout: int = 120) -> tuple[int, str]:
    try:
        p = subprocess.run(args, cwd=REPO, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as exc:  # noqa: BLE001 — a preflight must never be the thing that fails
        return 99, f"{type(exc).__name__}: {exc}"


# --------------------------------------------------------------------------- #
def check_cycle_log() -> None:
    """The monitoring mandate: >~2 min old means the loop is DEAD."""
    if not CYCLE_LOG.is_file():
        add("cycle_log", FAIL, "CYCLE_LOG.md missing — the monitoring loop has never run")
        return
    last = ""
    for line in CYCLE_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        if re.match(r"^\d{4}-\d\d-\d\dT", line):
            last = line
    m = re.match(r"^(\S+Z)", last)
    if not m:
        add("cycle_log", FAIL, "no timestamped line found")
        return
    # UTC, unambiguously. `time.mktime` interprets the struct as LOCAL time, so on this box (UTC+2)
    # the very first run of this file reported a FRESH log as 7,222 s stale and returned FAIL — a
    # claim about THIS SCRIPT, not about the campaign. `calendar.timegm` is the inverse of gmtime and
    # needs no correction term to get wrong.
    age = time.time() - calendar.timegm(time.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ"))
    fields = dict(re.findall(r"(\w+)=([^\s]+)", last))
    drift, sci = fields.get("drift", "?"), fields.get("sci", "?")
    # ⚠ THE THRESHOLD MUST TRACK THE SWEEP, NOT BE A CONSTANT (P205, 2026-08-03).
    #
    # A fixed 150 s was already wrong and was guaranteed to get worse. `cycle_loop.sh`'s own header
    # states the design intent: the sweep opens every record every cycle, so it "WILL LENGTHEN AS THE
    # ARCHIVE GROWS ... at C4's full seed ladder the sweep will take minutes and the effective cadence
    # will be sweep-bound, not sleep-bound. That is NOT a fault." Measured 2026-08-03 at 6,600 of a
    # projected ~42,000 records: ordinary sweeps 50-68 s, and the SSH/science cycles 98-101 s. Against
    # a 150 s constant this check therefore fires on healthy cycles TODAY and would sit permanently
    # red long before the campaign ends.
    #
    # That matters more than a cosmetic false alarm. A permanently red signal is how the h3 crash
    # (P202) stayed invisible for 31 hours: `guards=2` had been red for days, so a NEW fault inside it
    # changed nothing observable. Adding a second always-on alarm to this board would repeat exactly
    # the mistake this session exists to fix.
    #
    # So the loop is judged against ITS OWN recent behaviour: three times the recent worst period
    # (sweep + sleep), floored at the mandate's 150 s so it can never become more permissive than the
    # standing rule. A loop that has genuinely stopped still trips it, because the age then grows
    # without bound while the threshold stays fixed to the sweeps already on record.
    # ⚠ DROP THE SINGLE WORST SWEEP, and cap the result. Taking a plain max was this check's own
    # first bug: the one pathological 441 s sweep of 2026-08-03 (an orphaned qacct, P204) pushed the
    # budget to 1,413 s, so a loop that died would have gone unreported for 23 minutes. An adaptive
    # threshold that any single outlier can blind is worse than the constant it replaced. Using the
    # SECOND-worst tolerates the recurring SSH/science spike (~1 cycle in 12-30, 98-101 s) while a
    # lone anomaly still trips the alarm once, which is the correct outcome -- that sweep WAS wrong.
    # The cap is a backstop: if sweeps ever legitimately approach it, the cadence itself needs
    # revisiting rather than the alarm being widened again.
    # ⚠ A TORN LINE MUST NOT CRASH THE INSTRUMENT THAT REPORTS TORN LINES. `cycle_loop_dupes`
    # exists because two writers can race the same append; such a tear can yield `sweep=1.23.4s`,
    # and an unguarded float() raises ValueError and kills session_preflight itself.
    def _f(tok):
        try:
            return float(tok)
        except ValueError:
            return None
    sweeps = sorted(v for v in (_f(x) for x in re.findall(
        r"sweep=([0-9.]+)s", CYCLE_LOG.read_text(encoding="utf-8", errors="replace"))[-12:])
        if v is not None)
    # ⚠⚠ SWEEP-1-fix (2026-08-04, RUN 21). THE COMMENT ABOVE SAYS "if sweeps ever legitimately
    # approach [the cap], the cadence itself needs revisiting rather than the alarm being widened
    # again" -- AND THEY NOW DO. The three full-archive layers inside every sweep were timed
    # individually under live load at 13,611 records: science_watch 114 s + results_audit 139 s +
    # integrity_gate 51 s = 304 s, i.e. ~22.3 ms/record. At the registered ~42,128-record end state
    # those three ALONE are ~940 s, above the 900 s cap, before anything else in the sweep. A
    # constant cap against a cost that is LINEAR IN ARCHIVE SIZE must eventually declare a perfectly
    # healthy loop DEAD, and on the observed 655 s sweeps that day is roughly one day out.
    #
    # ⛔⛔ AND MY FIRST ATTEMPT AT THIS FIX LET THE BUDGET FOLLOW THE SWEEP UPWARD, WHICH IS THE
    # WIDENING THIS REPO FORBIDS OUTRIGHT -- AND THE COMMITTED TEST CAUGHT ME DOING IT
    # (`test_session_preflight.py`: "capped at 900s however slow it gets", which went RED).
    # The budget reached **1,353 s**, almost exactly the 1,413 s that the cap was introduced to
    # prevent in the first place, so I had re-opened P205 by hand. The comment four lines above
    # states the correct remedy and I should have followed it: *"if sweeps ever legitimately
    # approach it, the CADENCE itself needs revisiting rather than the alarm being widened again."*
    # ⇒ THE CAP STAYS. What is added is an EARLY WARNING, which weakens nothing: crossing the cap
    # now raises its own ATTENTION row naming the sweep duration and the real remedy, so the
    # condition is VISIBLE well before it can produce a false "the monitoring loop is DEAD".
    if sweeps:
        ref = sweeps[-2] if len(sweeps) >= 2 else sweeps[-1]
        uncapped = max(CYCLE_STALE_S, 3.0 * (ref + CYCLE_SLEEP_S))
        budget = min(CYCLE_BUDGET_CAP_S, uncapped)
        basis = (f"3x(2nd-worst of last {len(sweeps)} sweeps={ref:.0f}s "
                 f"+ sleep {CYCLE_SLEEP_S:.0f}s), cap {CYCLE_BUDGET_CAP_S:.0f}s")
        if uncapped > CYCLE_BUDGET_CAP_S:
            add("cycle_cadence", ATTN,
                f"the SWEEP has outgrown the {CYCLE_BUDGET_CAP_S:.0f}s design cap: 2nd-worst of the "
                f"last {len(sweeps)} sweeps is {ref:.0f}s, so the ADAPTIVE budget would be "
                f"{uncapped:.0f}s and is being CLAMPED to {CYCLE_BUDGET_CAP_S:.0f}s. The cap is "
                f"deliberately NOT raised -- a widening was tried and the committed test caught it "
                f"-- so a legitimately slow sweep will eventually be called DEAD. "
                f"THE REAL FIX IS TO MAKE THE THREE FULL-ARCHIVE LAYERS INCREMENTAL "
                f"(science_watch + results_audit + integrity_gate = 304s at 13,611 records, "
                f"~22.3 ms/record, ~940s at the 42,128-record end state). Ledger row SWEEP-1-fix.")
    else:
        budget = CYCLE_STALE_S
        basis = "no sweep timings on record"
    st = OK if age <= budget else FAIL
    add("cycle_log", st, f"{age:.0f}s old (dead >{budget:.0f}s = {basis}) · "
                         f"records={fields.get('records','?')} drift={drift} sci={sci}")
    # drift and sci are the two that must NEVER change
    add("drift_sci", OK if (drift == "0" and sci == "OK") else FAIL,
        f"drift={drift} sci={sci} (both are invariants; a transient drift=N around your own "
        f"commits is expected and clears in ~100 s)")


def check_drift_arms(running_sha: str) -> None:
    """BOTH arms: committed diff vs RUNNING_SHA, and the working tree."""
    paths = ["src", "scripts", "config", "prompts"]
    _, a1 = sh(["git", "diff", "--name-only", running_sha, "HEAD", "--", *paths])
    _, a2 = sh(["git", "status", "--porcelain", "--", *paths])
    n1 = len([x for x in a1.splitlines() if x.strip()])
    n2 = len([x for x in a2.splitlines() if x.strip()])
    add("drift_arm1", OK if n1 == 0 else FAIL, f"{n1} file(s) differ {running_sha}..HEAD")
    add("drift_arm2", OK if n2 == 0 else FAIL, f"{n2} uncommitted file(s) in {'/'.join(paths)}")


def check_processes() -> None:
    """Driver/supervisor/loop census.

    ⚠ THE TRAP THIS ENCODES: a `$(...)` subshell inherits its parent's command line, and a loose
    match also matches THIS PROCESS'S OWN QUERY. Both have invented processes for three separate
    sessions. So: match on the executable name, and EXCLUDE any candidate whose parent is itself a
    candidate.
    """
    try:
        import psutil  # type: ignore
    except Exception:  # noqa: BLE001
        add("processes", ATTN, "psutil unavailable — count processes manually (see the brief §3)")
        return
    procs = []
    for p in psutil.process_iter(["pid", "ppid", "name", "cmdline"]):
        try:
            cl = " ".join(p.info.get("cmdline") or [])
        except Exception:  # noqa: BLE001
            continue
        if p.info["pid"] == os.getpid():
            continue
        procs.append((p.info["pid"], p.info["ppid"], (p.info.get("name") or "").lower(), cl))

    def census(pred) -> list[int]:
        hit = [(pid, ppid) for pid, ppid, nm, cl in procs if pred(nm, cl)]
        ids = {pid for pid, _ in hit}
        return [pid for pid, ppid in hit if ppid not in ids]   # drop children of the same class

    drivers = census(lambda nm, cl: "python" in nm and "run_campaign_cluster" in cl)
    sups = census(lambda nm, cl: "powershell" in nm and re.search(r"-File .*mode_d_supervisor\.ps1", cl))
    loops = census(lambda nm, cl: "bash" in nm and "cycle_loop.sh" in cl)
    sent = census(lambda nm, cl: "python" in nm and "sentinel.py" in cl)
    add("processes", OK if (loops and sent and sups) else FAIL,
        f"driver-lines={len(drivers)} supervisors={len(sups)} cycle_loops={len(loops)} sentinel={len(sent)}")
    # ⚠ A DUPLICATE LOOP IS A PERSISTENT CONDITION, NOT A MOMENTARY ONE (P205b, 2026-08-03).
    # This fired `2 cycle loops` while only ONE independent loop existed. TWO sources, and the
    # dominant one is the trap in this file's own docstring turned on this file:
    #   (a) ANY shell whose command line merely MENTIONS cycle_loop.sh is a candidate — including
    #       the shell an OPERATOR is using to grep for it. Measured 2026-08-03: pid 25040 up 55 h
    #       (the real loop) plus a 1.0 s shell running the very query that was inspecting it. The
    #       `os.getpid()` guard above excludes THIS process but not its parent shell.
    #   (b) `cycle_loop.sh` runs `out=$(python docs/ops/cycle.py ...)`, and a command-substitution
    #       subshell inherits its parent's command line. Those ARE dropped by the parent rule —
    #       measured, both were children of 25040 — but only while the parent link resolves.
    # Both are momentary; a second REAL loop is started deliberately and persists. So require the
    # extras to have survived 60 s, and a genuine duplicate is still caught on the very next run.
    # A FAIL that flickers teaches people to ignore FAILs, which is precisely the alarm-saturation
    # failure that let P202 hide inside a permanently red `guards=2`.
    if len(loops) > 1:
        now, persistent = time.time(), []
        for pid in loops:
            try:
                if now - psutil.Process(pid).create_time() > 60:
                    persistent.append(pid)
            except Exception:  # noqa: BLE001 — a vanished pid is exactly the transient case
                continue
        if len(persistent) > 1:
            add("cycle_loop_dupes", FAIL,
                f"{len(persistent)} cycle loops alive >60s — two writers race the same '>>' "
                f"append and TEAR lines in ALERTS.txt. Kill all but one. pids={persistent}")

    _check_line_census(procs)


def _check_line_census(procs) -> None:
    """Per-line accounting: WHICH lines are up, and is an absent one dead or finished?

    ⚠ WHY THIS EXISTS (2026-08-03, defect P203). `processes` above passes whenever `sups` is
    merely NON-EMPTY, so ELEVEN supervisors out of twelve rated OK — and one out of twelve
    would too. That is what let the h3 line sit outside the fleet for 31 hours while the
    watchdog revived it 278 times (P202). A census that cannot count is not a census.

    An absent supervisor has three very different meanings and they must not be merged:
      MISSING  — nothing says it stopped on purpose. A genuinely dead line. FAIL.
      COMPLETE — it ran out of work and exited 0. Expected; every line ends this way.
      GATE     — it stopped at the review gate (rc=3) and is waiting for a human. ATTENTION.

    The roster is READ FROM `scripts/mode_d_launch.ps1`, never hardcoded here, so a line added
    to the fleet cannot be silently missing from the thing that counts the fleet.

    ⚠ COUPLED TO `docs/ops/watchdog_fenced.ps1`: it uses the same three-way predicate to decide
    revival. The duplication is DELIBERATE — the watchdog is the actor and this is an
    INDEPENDENT observer, so reading the watchdog's own verdict would go blind the moment the
    watchdog itself died. If you change one predicate, re-check the other.
    """
    roster, alive, states = _fleet_state()
    if roster is None:
        add("line_census", ATTN, f"could not determine the fleet: {alive}")
        return
    missing = sorted(k for k, v in states.items() if v == "MISSING")
    complete = sorted(k for k, v in states.items() if v == "COMPLETE")
    gate = sorted(k for k, v in states.items() if v == "GATE")
    # A value none of the three branches claims must not vanish -- that is how a finding becomes
    # silence. `__stray__` is the off-roster supervisor pseudo-entry from `_fleet_state` (P219).
    stray = states.get("__stray__", "")

    bits = [f"roster={len(roster)} up={len(alive)}"]
    if stray:
        bits.append("**" + stray + "** (a supervisor is running a line NOT on the roster)")
    if complete:
        bits.append("COMPLETE=" + ",".join(complete))
    if gate:
        bits.append("REVIEW-GATE=" + ",".join(gate))
    if missing:
        bits.append("MISSING=" + ",".join(missing))
    status = FAIL if (missing or stray) else (ATTN if gate else OK)
    if missing:
        bits.append("-- a MISSING line is dead with no recorded reason; relaunch it")
    if gate:
        bits.append("-- a REVIEW-GATE line needs a human decision, not a relaunch")
    add("line_census", status, "  ".join(bits))


def _fleet_state():
    """(roster, alive, {absent_line: state}) or (None, reason, None).

    Factored out so `_check_line_census`, `line_summary` and any future caller share ONE
    derivation. Enumerates its own processes rather than taking `procs`, so it is usable from a
    bare `--line-summary` invocation.
    """
    launcher = os.path.join(REPO, "scripts", "mode_d_launch.ps1")
    try:
        with open(launcher, "r", encoding="utf-8", errors="replace") as fh:
            src = fh.read()
    except OSError as exc:
        return None, f"cannot read the roster from mode_d_launch.ps1: {exc}", None
    m = re.search(r"\$lines\s*=\s*@\((.*?)\)", src, re.S)
    if not m:
        return None, "could not parse $lines from mode_d_launch.ps1 — roster unknown", None
    roster = re.findall(r'"([^"]+)"', m.group(1))
    if not roster:
        return None, "roster parsed as EMPTY from mode_d_launch.ps1", None

    try:
        import psutil  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return None, f"psutil unavailable: {exc}", None
    alive = set()
    for p in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cl = " ".join(p.info.get("cmdline") or [])
        except Exception:  # noqa: BLE001
            continue
        if p.info["pid"] == os.getpid():
            continue
        if "powershell" in (p.info.get("name") or "").lower() and \
                re.search(r"-File .*mode_d_supervisor\.ps1", cl):
            # ⚠ IT MUST BE **THIS RUN'S** SUPERVISOR (P219). The predicate used to match the script
            # and `-Line` only. `outputs/campaign_cluster_run2` and `_run3` both still exist on this
            # box, and a leftover supervisor from either carries the SAME script and the SAME -Line
            # names -- so it would have been counted as this run's line being up, and the census
            # would report a dead line as alive. Latent today (all ten carry -OutDir ...run4) and
            # cheap to close, so closed.
            if "campaign_cluster_run4" not in cl:
                continue
            hit = re.search(r"-Line\s+(\S+)", cl)
            if hit:
                alive.add(hit.group(1))

    # ⚠ `alive` MUST BE A SUBSET OF THE ROSTER (P219). It was not intersected, so a supervisor
    # carrying a -Line name that is not on the roster inflated the count and `line_summary` could
    # print "13 / 12 running" while `_check_line_census` still reported OK with nothing MISSING.
    # Anything alive but off-roster is a real anomaly, so it is surfaced rather than dropped.
    stray = sorted(alive - set(roster))
    alive &= set(roster)

    out_dir = os.path.join(REPO, "outputs", "campaign_cluster_run4")
    states = {ln: _line_terminal_state(out_dir, ln) for ln in roster if ln not in alive}
    if stray:
        states["__stray__"] = "STRAY:" + ",".join(stray)
    return roster, alive, states


def _line_terminal_state(out_dir: str, line: str) -> str:
    """Why is this line's supervisor absent? See _check_line_census for the three answers.

    ⚠ THIS MIRRORS `docs/ops/watchdog_fenced.ps1::Get-LineTerminalState` AND MUST STAY IN STEP.
    Read that function's header for the full reasoning; the short version is that suppressing a
    line needs THREE independent agreements, because ">=2 consecutive completions" ALONE was
    refuted on this repo's own logs: `supervisor_deepseek-v4-pro.log` carries TEN consecutive
    `driver exited 0` entries on 2026-07-28/29 and the ELEVENTH revival launched a driver that
    ran for a full day. Those are D12's six legs, which reported complete having produced nothing.

      (1) the supervisor ended CLEANLY (last non-empty line is `line supervisor exiting.`), so a
          supervisor killed mid-attempt cannot inherit an earlier episode's completion pair;
      (2) the completions use the ANCHORED post-D12 wording `LINE COMPLETE.` — the pre-D12
          supervisor could not tell completion from a gate stop and said so in its message
          (`LINE COMPLETE (or gate stop handled).`), and that text appears in EXACTLY D12's six
          legs and nowhere else;
      (3) the driver's own log carries a campaign-level success, which the supervisor does not
          write. `driver_deepseek-v4-pro.log` has ZERO; gemini has 2 and h3 has 279.

    Fail-safe: anything unreadable or unrecognised returns MISSING, so a parsing gap raises an
    alarm instead of quietly excusing a dead line.
    """
    return line_terminal_state_by_tag(out_dir, re.sub(r"[^a-zA-Z0-9_-]", "_", line))


def line_terminal_state_by_tag(out_dir: str, safe: str) -> str:
    """`_line_terminal_state` keyed by the already-normalised log tag (mode_d_supervisor.ps1:81).

    PUBLIC because `cycle.py` needs the same answer for a `driver_<tag>.log` it found by glob, and
    a third copy of this predicate is exactly how the two would come to disagree about one fact.
    """
    try:
        with open(os.path.join(out_dir, f"supervisor_{safe}.log"),
                  "r", encoding="utf-8", errors="replace") as fh:
            tail = fh.readlines()[-400:]
    except OSError:
        return "MISSING"
    outcomes = [ln for ln in tail if "driver exited" in ln]
    if not outcomes:
        return "MISSING"
    # Anchored: a bare "driver exited 3" also matches 3221225786 (STATUS_CONTROL_C_EXIT) and
    # every other code starting with 3, and the failure direction is "stop reviving".
    if "driver exited 3 -" in outcomes[-1]:
        return "GATE"
    meaningful = [ln for ln in tail if ln.strip()]
    if not meaningful or not meaningful[-1].rstrip().endswith("line supervisor exiting."):
        return "MISSING"
    consec = 0
    for ln in reversed(outcomes):
        if ln.rstrip().endswith("driver exited 0 - LINE COMPLETE."):
            consec += 1
        else:
            break
    if consec < 2:
        return "MISSING"
    try:
        with open(os.path.join(out_dir, f"driver_{safe}.log"),
                  "r", encoding="utf-8", errors="replace") as fh:
            dtail = fh.readlines()[-200:]
    except OSError:
        return "MISSING"
    if not any(("TIERED OK" in ln or "SINGLE-SHOT OK" in ln) for ln in dtail):
        return "MISSING"
    return "COMPLETE"


def check_reboot_recovery() -> None:
    """D21: without a boot task, a Windows Update reboot kills the whole fleet and NOTHING returns."""
    rc, out = sh(["powershell", "-NoProfile", "-Command",
                  "$t=Get-ScheduledTask -TaskName 'LLMRewardCampaignResume' -ErrorAction "
                  "SilentlyContinue; if($t){ $t.State; ($t.Actions | ForEach-Object { $_.Arguments }) } "
                  "else { 'MISSING' }"], timeout=60)
    if "MISSING" in out or rc not in (0, 1):
        add("reboot_recovery", FAIL,
            "NO boot task — a reboot kills 12 supervisors + all drivers + the cycle loop and NONE "
            "come back, while Myriad keeps running with nobody polling (D21)")
        return
    # The 2026-08-01 fix re-enters through mode_d_launch.ps1 (the single source of truth) and MUST
    # carry BOTH excluded hosts, or the substrate fence is absent on the reboot path (the D15 defect).
    good = "mode_d_launch.ps1" in out and "node-d00a-230" in out and "node-d00b-024" in out
    add("reboot_recovery", OK if good else ATTN,
        "boot task present, re-enters via mode_d_launch.ps1 with BOTH host exclusions" if good
        else "boot task present but its action looks WRONG (must call mode_d_launch.ps1 and carry "
             "node-d00a-230 AND node-d00b-024) — see D21")


def check_disk() -> None:
    t, u, f = shutil.disk_usage(str(REPO))
    gb = f / 1e9
    st = FAIL if gb < DISK_FLOOR_GB else (ATTN if gb < DISK_FLOOR_GB + 10 else OK)
    add("disk", st, f"C: {gb:.1f} GB free (CRITICAL floor {DISK_FLOOR_GB:.0f}); "
                    f"test records are ~480 KB each")


def check_mirror() -> None:
    """The mirror is what makes a C: failure cost records rather than the campaign."""
    if not MIRROR.is_dir():
        add("mirror", FAIL, f"archive mirror {MIRROR} MISSING — a disk failure would be total")
        return
    newest = 0.0
    for root, _dirs, files in os.walk(MIRROR):
        for fn in files:
            try:
                newest = max(newest, os.path.getmtime(os.path.join(root, fn)))
            except OSError:
                pass
        if time.time() - newest < 600:      # fresh enough; stop walking a 20 GB tree
            break
    age_h = (time.time() - newest) / 3600 if newest else 999
    add("mirror", OK if age_h < 2 else ATTN, f"archive mirror {age_h:.1f} h old")


def check_status_page() -> None:
    """Is the page Tamer reads from his phone still being REGENERATED?

    ⚠⚠ WHY THIS EXISTS (auditor, 2026-08-04). `publish_status.sh` gained an ASCII gate that REFUSES
    to publish a page containing a non-ASCII character, restores the previous good page, and exits 1.
    `publish_loop.sh` swallows that non-zero exit (`|| echo "publish attempt failed" >>"$LOG"`) and
    keeps looping every ~67 s. So one bad character injected by ANY interpolated variable freezes the
    page at its last good version **indefinitely**, and the only evidence is a line in /tmp.

    That is precisely the P210/P218 failure the publisher itself condemns twice: an artefact that
    goes on reading plausible after the instrument behind it stopped. A page that is WRONG is caught
    by the gate; a page that is STALE was caught by nothing. The gate made the second failure mode
    more likely while removing the first, so the freshness check is the other half of that fix.

    The publisher's configured sleep is ~67 s, but the MEASURED spacing between its commits is
    longer because the sweep itself takes time: median 78 s, mean 83.7 s over the newest 100
    (`git log --format=%ct --grep '^status:' -n 101`, 2026-08-04). So 15 min is ~11 missed cycles,
    not ~13 -- still unambiguous, and stated from the measurement rather than the config.

    ⚠⚠ AND THE ROW'S REAL BLIND SPOT, REGISTERED RATHER THAN FIXED (auditor, 2026-08-04, P302).
    THIS CHECK GRADES THE PUBLISHER BY THE **LOCAL** PAGE'S MTIME, WHICH IS A NAME-SHAPED PROXY FOR
    A THING IT NEVER MEASURES: whether anything reached GitHub. `publish_status.sh:259` writes the
    page unconditionally, and `:501` restores it with `git checkout --` when the ASCII gate rejects
    it, which REFRESHES the mtime; `:527` documents that `--only` returns rc=128 while a merge is in
    progress. In either state the local page keeps looking fresh, nothing accumulates unpushed, so
    `check_git_backup` ALSO reads OK -- **both rows green while the page a human reads on their
    phone is frozen.** Fixing it means checking the remote (a push timestamp or `git log
    origin/<branch> -1`), which costs a network call this row deliberately avoids. Registered as a
    known limitation of THIS row so nobody reads it as proof of publication.
    """
    page = REPO / "docs" / "RUN4_STATUS.md"
    if not page.exists():
        add("status_page", FAIL, "docs/RUN4_STATUS.md MISSING -- the phone page is gone")
        return
    age_m = (time.time() - page.stat().st_mtime) / 60.0
    add("status_page", OK if age_m < 15 else ATTN,
        f"phone page {age_m:.1f} min old"
        + ("" if age_m < 15 else " -- the publisher may be REFUSING to publish (ASCII gate) or dead;"
                                " check /tmp/publish_loop.log and docs/ops/watch/PUBLISH_LOOP_STDERR.log"))


def check_records() -> None:
    """Per-tier counts + the arm-freeze census — the campaign's actual progress."""
    if not RUN.is_dir():
        add("records", FAIL, f"{RUN} missing")
        return
    def n(pat: str) -> int:
        return sum(1 for _ in RUN.glob(pat))
    core = n("test/*/*/record.json")
    legs = n("test_leg_*/*/*/record.json")
    h3 = n("test_h3_singleshot/*/*/record.json")
    search = n("search*/*/*/record.json")
    frozen = {p.name.replace("frozen_leg_", "").replace("frozen", "core"): len(list(p.iterdir()))
              for p in sorted(RUN.glob("frozen*")) if p.is_dir()}
    add("records", OK, f"core_test={core} leg_test={legs} h3={h3} search={search} "
                       f"TOTAL={core+legs+h3+search}")
    add("arms_frozen", OK, " ".join(f"{k}={v}" for k, v in frozen.items()))
    # The H2 headline: distributional/scalar are tested ONLY in C2, behind the C1 barrier.
    c4 = sum(1 for p in RUN.glob("driver_*.log")
             if "C4|pipelined" in p.read_text(encoding="utf-8", errors="replace")[-400_000:])
    add("c4_entered", OK, f"{c4} line(s) have executed a C4 block "
                          f"(0 = still C1/C2; expect qw to jump to hundreds when the first enters)")


def check_git_backup() -> None:
    """Is this session's work SAFE OFF-MACHINE? That is the question the row exists to answer.

    ⚠ IT USED TO ASK A NARROWER ONE (fixed 2026-08-04). It compared HEAD only against
    `origin/myriad-cluster-and-tier-system` and then said, in its own message, *"the backup branch
    may still carry them"* -- an imprecision the author DOCUMENTED instead of MEASURING. The result
    was an ATTENTION every single time a session committed, for the ~2 minutes until the status
    publisher's next push, on work that was already safe on the backup branch. It fired three times
    in one session. **A board that raises a routine, self-clearing ATTENTION teaches its reader to
    ignore ATTENTIONs**, which is the cost that matters -- the same reasoning as the always-on-alarm
    pathology that let `guards=2` hide P202 for 31 h.

    ⚠ THAT PARAGRAPH USED TO END *"the dangerous state -- a commit that exists on NO remote at all
    -- still raises ATTENTION"*, and P299 below made it FALSE without editing it: up to
    `_PUBLISHER_RACE_MAX` publisher status commits on no remote now read OK. The current, true
    statement of the boundary is in the P299 block at the end of this docstring. A stale sentence
    left standing beside its own replacement is how a reader is told the wrong rule.

    ⚠⚠⚠ AND THE FIRST VERSION OF THAT FIX FAILED **OPEN** -- the worst defect class in this
    repository, introduced by me while removing a false positive (P257, found by an auditor).
    `sh()` returns `(stdout + stderr)` and a return code, and I discarded the code (`_, refs = ...`).
    The only filter dropped lines starting with `fatal`. So:
      * `warning: ignoring broken ref refs/remotes/origin/x` goes to STDERR, is merged in, survives
        the filter, and becomes a "holding ref";
      * `sh()`'s own exception path returns `99, "TimeoutExpired: ..."`, which likewise becomes one.
    Either way `holding` is non-empty and the row prints **OK -- safe off-machine** while ZERO
    remotes contain HEAD. The OLD code counted `git log` lines, so an error string INCREASED the
    count and raised ATTENTION: it failed SAFE. **My rewrite inverted the failure direction of the
    one alarm it promised to preserve.** This is exactly P230/P232's rule -- a verdict channel must
    not share a value with a failure channel -- and it is now enforced: a non-zero return code is
    UNKNOWN, never a backup, and only strict `refs/remotes/<name>` lines count.

    ⚠ THE STALENESS CAVEAT WAS ALSO BACKWARDS. This file previously claimed *"a stale ref can only
    make it MORE pessimistic, never less."* FALSE: a tracking ref for a branch that was deleted or
    force-pushed server-side still satisfies `--contains HEAD` locally, so a stale ref makes this
    OPTIMISTIC. It is stated as the real caveat now rather than as a reassurance.

    SCOPE, narrowed to what is actually measured: this covers COMMITTED work only. Uncommitted
    edits in the working tree are outside it, and `drift_arm2` covers only
    `src|scripts|config|prompts`, so `docs/**` and `paper/**` edits are covered by no row.

    ⚠⚠ P299 (RUN 21, 2026-08-04) -- THE ROW STILL FIRED CATASTROPHICALLY ON THE PUBLISHER RACE,
    AND IT MEASURED THE WRONG QUANTITY TO DO IT. Two defects, one line apart:

      1. `holding` empty meant "no remote ref contains HEAD", which is the NORMAL state for the
         ~2 minutes between the status publisher's auto-commit and its push. The row then printed
         *"N commit(s) on NO REMOTE AT ALL -- this work exists only on this machine"*, which reads
         as "nothing has ever been backed up" when the true state was one machine-generated status
         commit in flight and the entire branch safe on `origin`. Observed live at 16:05Z with
         `rev-list --count HEAD --not --remotes` returning 1, then 0 two minutes later.
      2. the COUNT came from `origin/myriad-cluster-and-tier-system..HEAD`, a hardcoded branch, so
         on any other branch the number was meaningless while the verdict still spoke with
         authority.

    Both are fixed by measuring the dangerous quantity DIRECTLY: `git rev-list --count HEAD --not
    --remotes` is exactly "commits reachable from HEAD that no remote ref contains", branch-agnostic
    and free of the `..` two-dot ambiguity.

    ⚠ AND THE GRADING IS NOT A WEAKENING, WHICH IS THE ONLY THING THAT MATTERS HERE. Unpushed work
    that is not a publisher status commit still raises ATTENTION on the FIRST commit. A publisher
    that STOPS pushing is still caught, and caught with a true message, because its status commits
    then accumulate at a measured ~77 s each and cross `_PUBLISHER_RACE_MAX` within ~6 minutes. What
    no longer fires is the one state that was benign, self-clearing and mis-described.

    ⚠⚠ P299-b (same day, an auditor sent at my own fix): THE FIRST VERSION GRADED ON THE COMMIT
    SUBJECT, WHICH IS NOT PROOF OF CONTENT, and this repository holds the counterexample -- see
    `_PUBLISHER_COMMIT_PREFIX`. It also crashed the whole preflight with an `IndexError` when
    `n_local > _PUBLISHER_RACE_MAX` and every subject was empty, because empty subjects were
    filtered out of the list it then indexed, and those same empty subjects graded as publisher
    commits. Both are closed by parsing `%H %s` TOGETHER WITH `--name-only` in one call, requiring
    the parse to account for exactly `n_local` commits, and requiring a publisher commit to touch
    exactly one path. Anything unaccounted for is UNKNOWN and routes to ATTENTION.

    THE BOUNDARY, stated once and truly: this row reads OK only when (a) nothing is unpushed, or
    (b) everything unpushed is a machine-generated status commit touching only
    `_PUBLISHER_COMMIT_PATH`, and there are at most `_PUBLISHER_RACE_MAX` of them.
    """
    rc_cnt, cnt_out = sh(["git", "rev-list", "--count", "HEAD", "--not", "--remotes"])
    # %H and %s and the file list in ONE call, chunked on \x01 so a subject containing any
    # ordinary character cannot be mistaken for a record separator.
    rc_sub, sub_out = sh(["git", "log", "--format=%x01%H%x1f%s", "--name-only",
                          "HEAD", "--not", "--remotes"])
    rc_refs, refs = sh(["git", "for-each-ref", "--contains", "HEAD", "--format=%(refname)",
                        "refs/remotes/"])

    # A ref line is only a ref if it LOOKS like one. Anything else is git talking, not git answering.
    def _is_ref(line: str) -> bool:
        t = line.strip()
        return (t.startswith("refs/remotes/") and not t.endswith("/HEAD")
                and all(c.isalnum() or c in "._/-" for c in t))

    holding = [t.strip()[len("refs/remotes/"):] for t in refs.splitlines() if _is_ref(t)]

    # P257 again: sh() merges stderr, so a warning line can masquerade as data. A count is only a
    # count if the whole output is one line of digits. Anything else is UNKNOWN, never a backup.
    cnt_lines = [x.strip() for x in cnt_out.splitlines() if x.strip()]
    n_local = int(cnt_lines[0]) if (len(cnt_lines) == 1 and cnt_lines[0].isdigit()) else None

    if rc_cnt != 0 or rc_sub != 0 or rc_refs != 0 or n_local is None:
        # UNKNOWN is not a backup. Reserve a value for "I could not tell" (P230/P232).
        add("unpushed", ATTN,
            f"could NOT determine backup state (git rc count={rc_cnt} subj={rc_sub} "
            f"refs={rc_refs}, count parsed as {n_local!r}) -- treat as UNBACKED until re-checked, "
            f"never as safe")
        return

    where = ", ".join(holding[:3]) if holding else "no ref contains HEAD yet"
    if n_local == 0:
        add("unpushed", OK,
            f"0 commit(s) exist only on this machine; HEAD is on {len(holding)} remote ref(s) "
            f"({where}) -- committed work only, and local tracking refs may be stale, which makes "
            f"this OPTIMISTIC not pessimistic")
        return

    # One record per commit: (sha, subject, set-of-paths). A merge commit lists no paths under
    # --name-only, so its empty path set makes it substantive, which is the safe direction.
    commits: list[tuple[str, str, frozenset[str]]] = []
    for chunk in sub_out.split("\x01")[1:]:
        head, _, rest = chunk.partition("\n")
        sha, _, subject = head.partition("\x1f")
        paths = frozenset(ln.strip() for ln in rest.splitlines() if ln.strip())
        commits.append((sha.strip(), subject.strip(), paths))

    # THE PARSE MUST ACCOUNT FOR EVERY COMMIT THE COUNT FOUND. If it does not -- a git warning
    # merged into the listing, an empty commit message, a format git chose not to honour -- then
    # something is unpushed that this row cannot describe, and undescribable is UNKNOWN, not safe.
    if len(commits) != n_local:
        add("unpushed", ATTN,
            f"{n_local} commit(s) exist only on this machine but the listing parsed "
            f"{len(commits)} of them -- UNKNOWN, treated as UNBACKED until re-checked")
        return

    substantive = [c for c in commits
                   if not (c[1].startswith(_PUBLISHER_COMMIT_PREFIX)
                           and c[2] == frozenset({_PUBLISHER_COMMIT_PATH}))]
    if not substantive and n_local <= _PUBLISHER_RACE_MAX:
        add("unpushed", OK,
            f"{n_local} auto-generated '{_PUBLISHER_COMMIT_PREFIX}' commit(s), each touching only "
            f"{_PUBLISHER_COMMIT_PATH}, awaiting the publisher's next push (measured ~77 s); every "
            f"commit carrying real work is already on a remote. If this count CLIMBS past "
            f"{_PUBLISHER_RACE_MAX} the publisher has stopped and this row turns ATTENTION -- that "
            f"is the detector, not the count itself")
        return

    lead = (substantive[0] if substantive else commits[0])[1] or "<empty commit message>"
    add("unpushed", ATTN,
        f"{n_local} commit(s) exist on NO REMOTE AT ALL ({len(substantive)} carrying real work, "
        f"newest: {lead[:60]!r}) -- push before this machine is the only copy")


def check_full() -> None:
    rc, out = sh([sys.executable, "scripts/freeze.py", "--check"], timeout=180)
    add("freeze", OK if rc == 0 and "MATCHES" in out else FAIL,
        "canonical hash MATCHES" if "MATCHES" in out else f"freeze --check rc={rc}")
    rc, out = sh([sys.executable, "scripts/audit_reproducibility.py"], timeout=300)
    m = re.search(r"(\d+) pass / (\d+) warn / (\d+) fail", out)
    if m:
        p, w, f = m.groups()
        add("reproducibility", OK if (w == "0" and f == "0") else FAIL,
            f"{p} pass / {w} warn / {f} fail — Priority 5 requires ZERO warn AND zero fail")
    else:
        add("reproducibility", ATTN, f"could not parse the audit (rc={rc})")
    # ⚠⚠ THIS ROW WAS HARDCODED `OK` AND PRINTED `?` WHEN IT COULD NOT PARSE (P236, 2026-08-03).
    # MEASURED: `openitems.py --open` takes **197 s** and the timeout here was **180 s**, so it was
    # being KILLED every run; `out` came back empty, the regex matched nothing, and the row rendered
    # `? open row(s) on the verified board` -- as **OK**. The board genuinely holds 4 open rows, one
    # of which (M166, the absent `campaign_summary.json`) is recorded as UNRECOVERABLE LATER.
    # So the single row that reports outstanding work was reporting nothing, in the reassuring
    # direction, on a timeout the tool had simply outgrown. Third instance of that family in one
    # session (cf. P230's `sci=OK`, and the sandbox_gap crash code).
    # 600 s because the board re-derives every status from git on each run and will keep growing.
    rc, out = sh([sys.executable, str(REPO.parent / ".claude" / "lanes" / "openitems.py"), "--open"],
                 timeout=600)
    m = re.search(r"NOT DONE:\s*(\d+)", out)
    if m:
        add("open_items", OK, f"{m.group(1)} open row(s) on the verified board")
    else:
        add("open_items", ATTN,
            f"could NOT read the open-items board (rc={rc}, {len(out)} bytes) -- the count of "
            f"outstanding work is UNKNOWN this run, which is not the same as zero")


def main(argv: list[str]) -> int:
    full = "--full" in argv
    running_sha = "unknown"
    try:
        cyc = (REPO / "docs" / "ops" / "cycle.py").read_text(encoding="utf-8", errors="replace")
        m = re.search(r'RUNNING_SHA\s*=\s*"([0-9a-f]+)"', cyc)
        running_sha = m.group(1) if m else "unknown"
    except OSError:
        pass

    check_cycle_log()
    check_drift_arms(running_sha)
    check_processes()
    check_reboot_recovery()
    check_disk()
    check_mirror()
    check_status_page()
    check_records()
    check_git_backup()
    if full:
        check_full()

    width = max(len(n) for n, _, _ in _rows)
    worst = OK
    print(f"\n=== SESSION PREFLIGHT — RUNNING_SHA {running_sha} "
          f"{'(full)' if full else '(fast; --full adds freeze/repro/board)'} ===")
    for name, st, detail in _rows:
        mark = {OK: "  OK ", ATTN: " ATTN", FAIL: " FAIL"}[st]
        print(f"[{mark}] {name.ljust(width)}  {detail}")
        if st == FAIL or (st == ATTN and worst == OK):
            worst = st if st == FAIL else ATTN
    print(f"\nVERDICT: {worst}")
    if worst != OK:
        print("A FAIL is a run-killer or an invariant breach — act before doing anything else.\n"
              "An ATTENTION needs a human decision, not necessarily an action.")
    return {OK: 0, ATTN: 1, FAIL: 2}[worst]


def line_summary() -> int:
    """One line of honest fleet accounting, for `publish_status.sh`'s phone panel.

    ⚠ WHY (P210, 2026-08-03). That panel read its "lines up" from
    `drivers=$(ls driver_*.log | wc -l)` — it counted LOG FILES, and a driver log exists forever
    once created. **It therefore printed "12 / 12" permanently and would have printed "12 / 12"
    with every single line dead.** It is the instrument Tamer actually reads to know the campaign is
    healthy, and it was structurally incapable of reporting a dead line: P203's defect in the most
    user-visible place. Reuses the census predicate rather than re-deriving a fourth copy.
    """
    roster, alive, states = _fleet_state()
    if roster is None:
        print("? / ?")
        return 1
    done = sorted(k for k, v in states.items() if v == "COMPLETE")
    gate = sorted(k for k, v in states.items() if v == "GATE")
    missing = sorted(k for k, v in states.items() if v == "MISSING")
    stray = states.get("__stray__", "")   # P219 pseudo-entry; never a roster line
    bits = [f"{len(alive)} / {len(roster)} running"]
    if done:
        bits.append(f"{len(done)} COMPLETE ({', '.join(done)})")
    if gate:
        bits.append(f"{len(gate)} AT THE REVIEW GATE ({', '.join(gate)})")
    if missing:
        bits.append(f"**{len(missing)} MISSING ({', '.join(missing)})**")
    if stray:
        bits.append("**" + stray + "**")
    print("; ".join(bits))
    return 1 if (missing or stray) else 0


if __name__ == "__main__":
    if "--line-summary" in sys.argv[1:]:
        raise SystemExit(line_summary())
    raise SystemExit(main(sys.argv[1:]))
