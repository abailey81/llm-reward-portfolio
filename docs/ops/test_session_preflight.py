"""Tests for the RUN 16 additions to session_preflight.py.

WHY THIS EXISTS. Four things were added to `session_preflight.py` during RUN 16 and NONE of them had
a test: the per-line census (P203), the adaptive cycle-log staleness budget (P205), the
`cycle_loop_dupes` persistence rule, and the three-way terminal-state predicate shared with
`docs/ops/watchdog_fenced.ps1`. They were verified only by reading their output on a healthy fleet —
which is precisely how this session's own defects got in:

  * P205  my first adaptive budget used max() and one outlier widened it to 1,413 s
  * P211  a join whose key semantics I had not checked, three times
  * P213  a new layer that returned CLEAN having inspected ZERO records
  * D33   an instrument that forbade a resource it could not see

Every one of those is "a check that passes for the wrong reason", and none is caught by running the
tool once on a healthy system. So these tests assert that each check FAILS when it should — mutation
controls, not smoke tests.

    python docs/ops/test_session_preflight.py
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import session_preflight as sp  # noqa: E402

PASS, FAIL = [], []


def check(label: str, got, want) -> None:
    (PASS if got == want else FAIL).append(label)
    mark = "PASS" if got == want else "FAIL"
    extra = "" if got == want else "   got %r, want %r" % (got, want)
    print("  %s  %s%s" % (mark, label, extra))


# --------------------------------------------------------------------------------------------
# 1. THE THREE-WAY TERMINAL STATE (shared with watchdog_fenced.ps1 -- they MUST agree)
# --------------------------------------------------------------------------------------------
START = "2026-08-03 01:00:00 | supervisor[x] | line supervisor started: run_campaign_cluster.py --resume"
ATTEMPT = "2026-08-03 01:00:01 | supervisor[x] | attempt 1: launching the driver"
EXITING = "2026-08-03 01:00:02 | supervisor[x] | line supervisor exiting."
RELAUNCH = "2026-08-03 01:00:00 | supervisor[x] | driver exited -1 - relaunching in 600s"
COMPLETE = "2026-08-03 01:00:00 | supervisor[x] | driver exited 0 - LINE COMPLETE."
AMBIG = "2026-07-28 23:14:45 | supervisor[x] | driver exited 0 - LINE COMPLETE (or gate stop handled)."
GATE = "2026-08-03 01:00:00 | supervisor[x] | driver exited 3 - STOPPED AT THE REVIEW GATE."
WEIRD = "2026-08-03 01:00:00 | supervisor[x] | driver exited 3221225786 - relaunching in 600s"


def _mk(tmp: str, tag: str, sup_lines, driver_ok: bool = True) -> None:
    with open(os.path.join(tmp, "supervisor_%s.log" % tag), "w", encoding="ascii") as fh:
        fh.write("\n".join(sup_lines) + "\n")
    body = "noise\n" + ("[campaign] TIERED OK - 7 tiers\n" if driver_ok else "no verdict\n")
    with open(os.path.join(tmp, "driver_%s.log" % tag), "w", encoding="ascii") as fh:
        fh.write(body)


def test_terminal_state() -> None:
    print("\n1. terminal state -- MUST agree with watchdog_fenced.ps1::Get-LineTerminalState")
    tmp = tempfile.mkdtemp(prefix="sp_ts_")
    try:
        f = sp.line_terminal_state_by_tag
        _mk(tmp, "a", [START, COMPLETE, EXITING, START, COMPLETE, EXITING])
        check("two consecutive post-D12 completions + clean exit + driver OK", f(tmp, "a"), "COMPLETE")

        _mk(tmp, "b", [START, RELAUNCH, EXITING])
        check("last outcome is a relaunch", f(tmp, "b"), "MISSING")

        _mk(tmp, "c", [START, RELAUNCH, START, COMPLETE, EXITING])
        check("exactly ONE trailing completion (confirmation retry)", f(tmp, "c"), "MISSING")

        # THE AUDITOR'S REFUTATION, pinned on this side too: D12's six legs used the AMBIGUOUS
        # pre-D12 wording, and ten of them in a row must NOT suppress a line.
        _mk(tmp, "d", [START] + [AMBIG] * 10 + [EXITING])
        check("D12's ten AMBIGUOUS completions must NOT read as COMPLETE", f(tmp, "d"), "MISSING")

        _mk(tmp, "e", [START, COMPLETE, EXITING, START, COMPLETE, EXITING], driver_ok=False)
        check("no campaign-level OK in the driver log", f(tmp, "e"), "MISSING")

        _mk(tmp, "f", [START, COMPLETE, EXITING, START, COMPLETE, EXITING, START, ATTEMPT])
        check("supervisor KILLED mid-attempt after old completions", f(tmp, "f"), "MISSING")

        _mk(tmp, "g", [START, COMPLETE, COMPLETE, GATE, EXITING])
        check("review-gate stop wins over prior completions", f(tmp, "g"), "GATE")

        _mk(tmp, "h", [START, COMPLETE, COMPLETE, WEIRD, EXITING])
        check("exit 3221225786 must NOT read as a review-gate stop", f(tmp, "h"), "MISSING")

        check("absent log is MISSING, never excused", f(tmp, "nosuch"), "MISSING")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------------------------------------
# 2. THE ADAPTIVE CYCLE-LOG BUDGET (P205)
# --------------------------------------------------------------------------------------------
def _cycle_budget(sweeps_desc: list) -> float:
    """Run check_cycle_log against a synthetic log and return the budget it chose."""
    tmp = tempfile.mkdtemp(prefix="sp_cl_")
    try:
        path = os.path.join(tmp, "CYCLE_LOG.md")
        # A `None` entry writes a TIMESTAMPED line carrying NO `sweep=` token. That is the case the
        # "no timings on record" branch is for. Writing an EMPTY file instead would trip the
        # earlier, different branch ("no timestamped line found") and test nothing of the sort --
        # which is exactly what the first version of this fixture did.
        lines = []
        for i, s in enumerate(sweeps_desc):
            base = "2026-08-03T%02d:00:00Z  RED  records=%d (+1)  drift=0  sci=OK" % (i % 24, 1000 + i)
            lines.append(base if s is None else base + "  sweep=%.1fs" % s)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        import pathlib
        saved_log, saved_rows = sp.CYCLE_LOG, list(sp._rows)
        sp.CYCLE_LOG = pathlib.Path(path)
        del sp._rows[:]
        try:
            sp.check_cycle_log()
            detail = next(d for n, _s, d in sp._rows if n == "cycle_log")
        finally:
            sp.CYCLE_LOG = saved_log
            del sp._rows[:]
            sp._rows.extend(saved_rows)
        import re
        m = re.search(r"dead >(\d+)s", detail)
        return float(m.group(1)) if m else -1.0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_adaptive_budget() -> None:
    print("\n2. adaptive cycle-log budget (P205) -- one outlier must NOT blind it")
    # 11 normal sweeps + ONE pathological 440.9 s (the real P204 outlier).
    b_outlier = _cycle_budget([55.0] * 11 + [440.9])
    # 3*(2nd worst 55 + 30) = 255
    check("a single 440.9s outlier does NOT set the budget", b_outlier, 255.0)

    # If the slow sweep is genuinely RECURRING, the budget widens -- 3*(440.9+30) = 1,412.7, which
    # the 900 s cap then binds. Both behaviours are asserted at once by this expectation.
    check("two 440.9s sweeps DO widen it, and the cap then binds",
          _cycle_budget([55.0] * 10 + [440.9, 440.9]), 900.0)

    check("floored at the mandate's 150s on fast sweeps", _cycle_budget([5.0] * 12), 150.0)
    check("capped at 900s however slow it gets", _cycle_budget([5000.0] * 12), 900.0)
    check("a single sweep on record still yields a budget", _cycle_budget([60.0]), 270.0)
    check("timestamped lines but NO sweep tokens -> the 150s floor", _cycle_budget([None] * 3), 150.0)


# --------------------------------------------------------------------------------------------
# 3. THE ROSTER REGEX (P203) -- the census is worthless if it mis-reads the fleet
# --------------------------------------------------------------------------------------------
def test_roster() -> None:
    print("\n3. roster parsing -- read from mode_d_launch.ps1, never hardcoded")
    import re
    src = open(os.path.join(sp.REPO, "scripts", "mode_d_launch.ps1"),
               encoding="utf-8", errors="replace").read()
    m = re.search(r"\$lines\s*=\s*@\((.*?)\)", src, re.S)
    check("the $lines array is found", bool(m), True)
    roster = re.findall(r'"([^"]+)"', m.group(1)) if m else []
    check("exactly 12 lines parsed", len(roster), 12)
    check("no duplicates", len(set(roster)), 12)
    check("core is present", "core" in roster, True)
    check("h3 is present", "h3" in roster, True)
    check("nothing spurious (every entry is a plausible line tag)",
          all(re.fullmatch(r"[A-Za-z0-9._-]+", r) for r in roster), True)


def test_cross_instrument_agreement() -> None:
    """The PowerShell actor and this Python observer implement the SAME predicate.

    `session_preflight._line_terminal_state` and `watchdog_fenced.ps1::Get-LineTerminalState` are a
    DELIBERATE duplication: the watchdog acts, the preflight observes independently, so reading the
    watchdog's own verdict would go blind the moment the watchdog died. The cost of that choice is
    that they can DRIFT APART, and each one's own tests would still pass while they disagreed.

    Until now only a comment said "if you change one, re-check the other". This runs the PowerShell
    side's selftest so that a change to either predicate fails THIS suite too. It also asserts the
    two agree on the REAL campaign logs, which is the only place drift would actually bite.
    """
    print("\n4. cross-instrument agreement with watchdog_fenced.ps1")
    import subprocess
    ps_test = os.path.join(sp.REPO, "docs", "ops", "test_watchdog_completion.ps1")
    if not os.path.isfile(ps_test):
        check("the PowerShell selftest exists", False, True)
        return
    try:
        p = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                            "-File", ps_test], capture_output=True, text=True, timeout=300)
        check("watchdog_fenced.ps1 predicate selftest passes", p.returncode, 0)
    except Exception as exc:  # noqa: BLE001
        check("watchdog selftest ran (%s)" % type(exc).__name__, False, True)
        return

    # AGREEMENT ON THE REAL LOGS. The PowerShell suite already asserts h3 and gemini are COMPLETE
    # and every other line REVIVE; assert the Python side says the same, so a divergence in either
    # direction fails here.
    out_dir = os.path.join(sp.REPO, "outputs", "campaign_cluster_run4")
    if os.path.isdir(out_dir):
        expect = {"h3": "COMPLETE", "gemini-2_5-flash": "COMPLETE",
                  "core": "MISSING", "sonnet-5": "MISSING", "qwen3_5-9b": "MISSING",
                  "nemotron-3-super": "MISSING"}
        for tag, want in expect.items():
            if os.path.isfile(os.path.join(out_dir, "supervisor_%s.log" % tag)):
                check("real log agrees for %s" % tag,
                      sp.line_terminal_state_by_tag(out_dir, tag), want)


def main() -> int:
    print("=== session_preflight RUN-16 additions: mutation-controlled tests ===")
    test_terminal_state()
    test_adaptive_budget()
    test_roster()
    test_cross_instrument_agreement()
    print("\nRESULT: %d passed, %d failed" % (len(PASS), len(FAIL)))
    for f in FAIL:
        print("  FAILED: %s" % f)
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
