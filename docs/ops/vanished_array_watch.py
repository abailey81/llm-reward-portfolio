"""VANISHED-ARRAY WATCH -- the missing instrument for RUN 4's single largest latency defect.

THE DEFECT (measured, RUN 13, 2026-08-02). `src/cluster/driver.py` line 6 states the design plainly:
"SGE's own walltime is the stall detector". That is a deliberate and defensible choice -- a job that
is merely SLOW must not be second-guessed -- but it has a consequence nobody had measured: a job that
VANISHES (purged in Eqw by the site cleanup, which leaves no qacct row at all) is indistinguishable
from a slow one until its h_rt walltime of 54,000 s has elapsed. The driver then reports

    [<block>] drain with NO qacct trace (1/3) -- the array was purged before dispatch; requeueing

and only THEN resubmits. Traced end to end on the core line's `cma_es-c4`:

    07-30 14:56:09  submitted c1_cma_es_c4 as array 45015
    07-31 11:10:14  drain with NO qacct trace -> requeue        <-- 20.2 HOURS of nothing
    07-31 11:10:19  resubmitted as 53735  (ran ~9 h, wrote the record)
    07-31 20:15:24  drain with NO qacct trace -> requeue        <-- FALSE this time
    07-31 20:16:30  batch complete (45 s: the record already existed)

Twenty hours on ONE candidate of `cma_es`, which is the campaign's critical path: 9 of 30 candidates
done, STRICTLY SEQUENTIAL (each CMA-ES proposal is a function of the fitnesses already observed), and
the C1 barrier cannot release until its 30-candidate budget is spent. Across the 12 driver logs there
are 76 of these events. This is why the campaign sat at 560 slots with 864 entitled slots FREE and
only 6 jobs queued: the bottleneck was never capacity.

WHAT THIS DOES. Every line runs SEVERAL arms concurrently, so it tracks EVERY block that is currently
pending -- not the newest log line, which was this script's own first bug and would have hidden the
very stall it exists to find. For each pending block it takes the array ids the driver last submitted
and asks the cluster whether ANY of them is still alive. A pending block whose arrays have all left
the queue is either (a) finishing inside the current poll -- benign, resolves in ~3 min -- or (b)
VANISHED, in which case the driver burns up to 15 h before noticing. Age separates the two.

WHY IT IS SAFE. Strictly read-only: driver logs plus one `qstat`. It submits nothing, deletes
nothing, touches no record, and reads no outcome. It reports; a human decides.

THREE VALUES, NOT TWO. A block with no parsed array id is UNKNOWN, never "vanished" -- absence of
evidence is reported as absence of evidence. That is the register's own rule, and the trap this
project has fallen into more than once.
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ARGS = [a for a in sys.argv[1:]]
SELFTEST = "--selftest" in ARGS
# `--live-ids a,b,c` substitutes the cluster query. It exists ONLY so the selftest can drive both
# branches; without it a detector that never fires and a detector that cannot fire look identical.
_LIVE_OVERRIDE: set[str] | None = None
for _a in ARGS:
    if _a.startswith("--live-ids="):
        _LIVE_OVERRIDE = {x.strip() for x in _a.split("=", 1)[1].split(",") if x.strip()}
# "--qacct=yes|no|unknown" substitutes the accounting probe. It exists so the P186 discrimination --
# COMPLETED (a qacct row) versus PURGED (none) -- is itself testable; a fix that cannot be exercised
# is a fix nobody has verified.
_QACCT_OVERRIDE: bool | None = None
_QACCT_SET = False
for _a in ARGS:
    if _a.startswith("--qacct="):
        _v = _a.split("=", 1)[1].strip().lower()
        _QACCT_SET = True
        _QACCT_OVERRIDE = {"yes": True, "no": False, "unknown": None}.get(_v)
POSITIONAL = [a for a in ARGS if not a.startswith("--")]
ROOT = Path(POSITIONAL[0] if POSITIONAL else "outputs/campaign_cluster_run4")
BENIGN_GRACE_MIN = 12.0    # driver polls every 180 s, then has to pull; below this, say nothing
STALE_BLOCK_MIN = 15.0     # a block whose last poll line is older than this is not "current"

TS = r"(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)"
# `\s+` not a literal space on BOTH sides of the block name: the un-wrap rejoins a wrapped record
# with a separator, and the wrap point falls right after "submitted ", so the joined line carries
# TWO spaces there. A single-space pattern matched none of the 14 multi-array blocks -- the second
# time in one script that a parsing detail, not the cluster, produced a clean "nothing found".
SUBMITTED = re.compile(TS + r".*?\[([A-Za-z0-9_.\-]+)\]\s+submitted\s+\S+\s+as\s+\d+ array\(s\):\s*\[(.*?)\]")
PENDING = re.compile(TS + r".*?\[([A-Za-z0-9_.\-]+)\]\s+(\d+)/(\d+) done,\s*(\d+) pending")


def parse_ts(s: str) -> float:
    """Driver logs carry the driver host's LOCAL time; compare against local time too."""
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").timestamp()


def live_job_ids() -> set[str]:
    if _LIVE_OVERRIDE is not None:
        return set(_LIVE_OVERRIDE)
    # P204, same nesting invariant as _qacct_has_trace below: this must stay strictly under the
    # caller's timeout (cycle.py:907 = 300 s) or the outer kill orphans this ssh. 90 s matches the
    # timeout cycle.py already uses for its own direct `qstat` and is ~60x the measured 1.5 s cost.
    out = subprocess.run(["ssh", "-o", "BatchMode=yes", "myriad", "qstat -u ucestes"],
                         capture_output=True, text=True, timeout=90)
    ids = set()
    for ln in out.stdout.splitlines()[2:]:
        f = ln.split()
        if f and f[0].isdigit():
            ids.add(f[0])
    return ids


def has_qacct_trace(job_ids: list[str]) -> bool | None:
    """Did ANY of these arrays leave an accounting row? None = could not tell.

    ⚠ THIS EXISTS BECAUSE THE SCRIPT RAISED A FALSE POSITIVE ON ITS FIRST LIVE FIRING (P186).
    "arrays gone from qstat AND the block still reports pending" is ALSO the signature of "the arrays
    FINISHED and the driver has not pulled the last records yet". On 2026-08-02 it flagged
    `leg10_leg_kimi_k3_placebo_shuffled_test` as vanished for 617 minutes; `qacct` showed
    `failed 0` on all four arrays and the block reported `batch complete` four minutes later. Acting
    on that would have restarted a HEALTHY line for nothing.

    The discriminator is the one the driver itself uses, and its own message names it: a purged array
    leaves **NO qacct trace**, while a completed one leaves a row. So a block is only VANISHED if its
    arrays are absent from the queue AND absent from accounting. Absence of evidence is reported as
    UNKNOWN, never as vanished -- the register's own rule, applied to the instrument that enforces it.
    """
    if not job_ids:
        return None
    q = "; ".join(f"qacct -j {j} 2>/dev/null | head -1" for j in job_ids[:6])
    # ⚠ THIS TIMEOUT MUST STAY STRICTLY BELOW THE CALLER'S (P204, 2026-08-03).
    #
    # It was 300 s and `cycle.py:907` runs this script with timeout=300, so the OUTER timeout could
    # never lose the race. When it fired, cycle.py killed THIS PYTHON PROCESS and Windows did not
    # cascade the kill to its ssh grandchild: the ssh survived, ORPHANED, still running six
    # `qacct -j` scans of the 33 GB /opt/sge/default/common/accounting file with nobody left to read
    # a byte of its output. Measured 2026-08-03: one such orphan alive 8.8 minutes, holding an
    # ssh-gate slot and burning login-node CPU -- the exact resource whose overuse auto-penalised
    # this account at 00:33:47Z. It also starved the monitoring cycle itself, which went 7 minutes
    # without writing a line while the DEAD-loop threshold is 150 s.
    #
    # At 120 s the INNER timeout always wins, and `subprocess.run` then kills ssh.exe -- which is
    # this process's DIRECT child, so that kill does land. Shortening it is safe in the only
    # direction that matters: a timeout returns None, which this function's contract renders as
    # UNKNOWN, and UNKNOWN is never reported as vanished (see the docstring above). A slow qacct can
    # therefore only make the detector quieter, never make it fire falsely.
    _SSH_TIMEOUT_SECS = 120
    try:
        out = subprocess.run(["ssh", "-o", "BatchMode=yes", "myriad", q],
                             capture_output=True, text=True, timeout=_SSH_TIMEOUT_SECS)
    except Exception:
        return None
    if out.returncode not in (0, 1):
        return None
    return bool(out.stdout.strip())


def _selftest() -> int:
    """Prove the detector can FIRE and can STAY SILENT, on the real log grammar.

    Both cases are built from a VERBATIM wrapped extract of `driver_core.log`, wrap points and
    trailing spaces included, because every parsing failure this script has had came from that
    wrapping and a hand-tidied fixture would have passed all of them.
    """
    import tempfile

    old = (datetime.fromtimestamp(time.time() - 3 * 3600)).strftime("%Y-%m-%d %H:%M:%S")
    recent = (datetime.fromtimestamp(time.time() - 60)).strftime("%Y-%m-%d %H:%M:%S")
    body = (
        f"{old} | INFO    | src.cluster.driver | [c1_cma_es_c4] submitted c1_cma_es_c4 as 4 \n"
        "array(s): ['45015', '45016', '45017', '45018']\n"
        f"{recent} | INFO    | src.cluster.driver | [c1_cma_es_c4] 0/1 done, 1 pending, round 1\n"
    )
    fails = []
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "driver_selftest.log").write_text(body, encoding="utf-8")
        here = [sys.executable, str(Path(__file__).resolve()), str(d)]
        # CASE A -- every array gone: MUST alert (exit 1).
        a = subprocess.run(here + ["--live-ids=99999"], capture_output=True, text=True)
        if a.returncode != 1 or "VANISHED" not in a.stdout:
            fails.append(f"A: expected exit 1 + VANISHED, got {a.returncode}\n{a.stdout}")
        # CASE B -- one array still alive: MUST stay silent (exit 0). Without this control an
        # always-alerting detector would pass case A.
        b = subprocess.run(here + ["--live-ids=45017"], capture_output=True, text=True)
        if b.returncode != 0 or "VANISHED" in b.stdout:
            fails.append(f"B: expected exit 0 + no alert, got {b.returncode}\n{b.stdout}")
        # CASE D -- P186, THE FALSE POSITIVE THIS SCRIPT ACTUALLY PRODUCED. Arrays gone from the
        # queue, block still pending, well past the grace window -- but a qacct row EXISTS, so they
        # COMPLETED and the driver simply has not pulled yet. MUST stay silent. Without this case the
        # P186 fix is unverified, and acting on that false positive would have restarted a healthy
        # line for nothing.
        dd = subprocess.run(here + ["--live-ids=99999", "--qacct=yes"], capture_output=True, text=True)
        if dd.returncode != 0 or "VANISHED" in dd.stdout:
            fails.append(f"D: qacct row present must NOT alert, got {dd.returncode}\n{dd.stdout}")
        # CASE E -- qacct unreachable: MUST report UNKNOWN, never "vanished". Absence of evidence is
        # not evidence, and a monitoring outage must not manufacture an incident.
        ee = subprocess.run(here + ["--live-ids=99999", "--qacct=unknown"], capture_output=True, text=True)
        if ee.returncode != 0 or "VANISHED" in ee.stdout or "UNKNOWN (qacct" not in ee.stdout:
            fails.append(f"E: unreachable qacct must report UNKNOWN, got {ee.returncode}\n{ee.stdout}")
        # CASE F -- gone from BOTH: the real defect. MUST fire.
        ff = subprocess.run(here + ["--live-ids=99999", "--qacct=no"], capture_output=True, text=True)
        if ff.returncode != 1 or "VANISHED" not in ff.stdout:
            fails.append(f"F: no qstat AND no qacct must alert, got {ff.returncode}\n{ff.stdout}")
        # CASE C -- gone but INSIDE the grace window: MUST stay silent, so a normal completion
        # between two polls is never reported as a stall.
        fresh = (d / "driver_fresh.log")
        fresh.write_text(body.replace(old, recent), encoding="utf-8")
        (d / "driver_selftest.log").unlink()
        c = subprocess.run(here + ["--live-ids=99999"], capture_output=True, text=True)
        if c.returncode != 0 or "VANISHED" in c.stdout:
            fails.append(f"C: expected exit 0 (grace), got {c.returncode}\n{c.stdout}")
    for f in fails:
        print("SELFTEST FAIL " + f)
    print(f"selftest: {6 - len(fails)}/6 cases pass")
    return 1 if fails else 0


if SELFTEST:
    raise SystemExit(_selftest())

live = live_job_ids()
now = time.time()
print(f"live job ids on the cluster: {len(live)}")
print()
print("%-18s %-46s %5s %-24s %8s  %s"
      % ("LINE", "PENDING BLOCK", "PEND", "LAST ARRAYS", "AGE_MIN", "VERDICT"))

alerts: list[tuple[str, str, list[str], float]] = []
for log in sorted(ROOT.glob("driver_*.log")):
    line = log.name[len("driver_"):-len(".log")]
    try:
        raw = log.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        continue
    # THE DRIVER LOG IS HARD-WRAPPED BY THE POWERSHELL HOST that runs the supervisor: a long record
    # continues on the next PHYSICAL line with no timestamp, so "submitted <blk> as 4 array(s):"
    # and its id list end up on different lines. Parsing physical lines silently dropped every
    # multi-array block -- this script reported "UNKNOWN (no id parsed)" for 14 of 16 pending blocks
    # before the un-wrap, which is exactly the shape of a monitor that looks healthy and sees
    # nothing. Rejoin continuations before matching anything.
    txt: list[str] = []
    for ln in raw:
        if re.match(TS, ln) or not txt:
            txt.append(ln)
        else:
            txt[-1] += " " + ln.strip()
    # The wrap point is arbitrary -- it fell after "submitted " on one line and after "as 4 " on
    # another -- and each wrapped line already ends with a space, so rejoining yields DOUBLE spaces
    # at unpredictable places. Collapse whitespace once here rather than making every pattern
    # whitespace-tolerant; two separate patterns had already been defeated by exactly this.
    txt = [re.sub(r"\s+", " ", s) for s in txt]
    last_state: dict[str, tuple[float, int]] = {}      # block -> (ts, pending)
    submits: dict[str, tuple[float, list[str]]] = {}   # block -> (ts, ids)
    for ln in txt:
        m = PENDING.search(ln)
        if m:
            try:
                last_state[m.group(2)] = (parse_ts(m.group(1)), int(m.group(5)))
            except Exception:
                pass
            continue
        m = SUBMITTED.search(ln)
        if m:
            ids = [x.strip().strip("'\"") for x in m.group(3).split(",") if x.strip()]
            try:
                submits[m.group(2)] = (parse_ts(m.group(1)), ids)
            except Exception:
                pass

    for blk, (bts, pend) in sorted(last_state.items()):
        if pend == 0:
            continue
        if (now - bts) / 60.0 > STALE_BLOCK_MIN:
            continue                                    # the driver has stopped reporting it
        sts, ids = submits.get(blk, (None, []))
        if not ids:
            print("%-18s %-46s %5d %-24s %8s  %s" % (line, blk, pend, "-", "-", "UNKNOWN (no id parsed)"))
            continue
        if any(i in live for i in ids):
            print("%-18s %-46s %5d %-24s %8s  %s"
                  % (line, blk, pend, ",".join(ids)[:24], "-", "ok (array alive)"))
            continue
        mins = (now - sts) / 60.0 if sts else -1.0
        if mins < 0:
            verdict = "UNKNOWN (unparsed ts)"
        elif mins < BENIGN_GRACE_MIN:
            verdict = "benign (just finished?)"
        else:
            # THE SECOND, DECISIVE TEST (P186). Gone from the queue is not enough -- a COMPLETED array
            # is also gone. Only an array with no accounting row was purged, which is precisely the
            # condition the driver's own "drain with NO qacct trace" message names.
            traced = _QACCT_OVERRIDE if _QACCT_SET else (
                None if _LIVE_OVERRIDE is not None else has_qacct_trace(ids))
            if traced is True:
                verdict = "ok (arrays COMPLETED -- qacct row present; driver has yet to pull)"
            elif traced is None and (_QACCT_SET or _LIVE_OVERRIDE is None):
                verdict = "UNKNOWN (qacct unreachable -- cannot distinguish purged from completed)"
            else:
                verdict = "*** VANISHED ARRAY -- no qstat, no qacct; driver waits up to 15 h ***"
                alerts.append((line, blk, ids, mins))
        print("%-18s %-46s %5d %-24s %8.0f  %s" % (line, blk, pend, ",".join(ids)[:24], mins, verdict))

print()
if alerts:
    print(f"!!! {len(alerts)} VANISHED ARRAY(S) -- each costs its line up to 15 h of pure latency:")
    for line, blk, ids, mins in alerts:
        print(f"    {line}: block {blk}, arrays {ids}, gone for {mins:.0f} min")
    print()
    print("    The driver WILL recover on its own once h_rt expires; the cost is the WAIT, not lost")
    print("    work. Recovery is far faster if that line's driver is restarted (its `--resume`")
    print("    re-derives the diff and resubmits at once) -- but a stale `.driver.lock` left by an")
    print("    unclean stop has itself cost this campaign 4.5 h, so that is a decision, not a reflex.")
    sys.exit(1)
print("no vanished arrays detected")
