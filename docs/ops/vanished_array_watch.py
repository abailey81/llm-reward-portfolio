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

★ P305 (RUN 22, 2026-08-04) -- THE ARRAY ID WAS NEVER THE ONLY WITNESS, AND THE BETTER ONE WAS
ALREADY IN THE `qstat` WE RUN. After RUN 21 made unresolved blocks VISIBLE (correctly -- an UNKNOWN
is not a negative), the tool exited 2 on every pass and held the board at ATTENTION for an hour on a
state that is benign and recurs hourly: a sweep tier the driver has not submitted YET. Measured
2026-08-04 21:37Z -- five `qwen3_6-27b` tiers carrying 2,233 pending units, while that line's driver
was mid-ramp and submitting its six tiers exactly as haiku had forty minutes earlier (sonnet 7.5 min
for six, haiku 40 min, qwen3.5-9b 55 min).

⚠ THE OBVIOUS DISCRIMINATOR IS WRONG AND WAS REFUTED BEFORE IT WAS USED. "`round 0` means never
submitted" is FALSE: `round` counts REQUEUES, not submissions, and a sweep over all twelve driver
logs found **180 blocks reporting `round 0` while carrying a submission record**. Building the fix
on it would have blinded the detector across those 180 blocks.

⇒ THE SOUND WITNESS IS THE JOB **NAME**, taken from the cluster rather than parsed from a
hard-wrapped log. The driver names every job `<block>_p<NN>` (and `<block>_r<N>_p<NN>` after a
requeue), so a live job whose name is the block, or begins with the block plus an underscore,
RESOLVES that block directly -- no log parsing, no dependence on wrapping or on the log being
complete. The id route stays primary; this is the fallback that converts an UNKNOWN into a
measurement instead of into an alarm.

⚠ THE UNDERSCORE IS LOAD-BEARING, NOT TIDINESS. A bare `startswith(block)` makes `c1_tpe_c1` match
`c1_tpe_c12_p01` -- the same substring defect that let `crash_watchdog` recover `scalar` from
`scalar_cvar5`. Selftest case H is the control for exactly that and fails against the naive form.
Names require `qstat -xml`: plain `qstat` TRUNCATES them (P276).
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
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
#: `--live-names=a,b` substitutes the live job NAME set (P305). Separate from `--live-ids` because
#: the two witnesses must be drivable independently: a case that supplies both cannot show which one
#: resolved the block, and a fallback that is never exercised alone is a fallback nobody has tested.
_LIVE_NAMES_OVERRIDE: set[str] | None = None
for _a in ARGS:
    if _a.startswith("--live-names="):
        _LIVE_NAMES_OVERRIDE = {x.strip() for x in _a.split("=", 1)[1].split(",") if x.strip()}
#: ⚠ P305-b (auditor finding, same hour). EITHER live override means "this is an OFFLINE run": no
#: `qstat`, and no `qacct` either. The guard below used to test `_LIVE_OVERRIDE` ALONE, so the NEW
#: `--live-names` hook looked offline and was not -- a fixture carrying ids would have fired the real
#: `qacct` ssh, which is six scans of a 33 GB accounting file on a login node (the exact abuse P204
#: records). The selftest never tripped it because cases G/H use a fixture with no ids, so the hook
#: was documented as a test hook while being the one hook that could reach the cluster.
_OFFLINE = _LIVE_OVERRIDE is not None or _LIVE_NAMES_OVERRIDE is not None
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


def live_jobs() -> tuple[set[str], set[str]]:
    """Return `(live array ids, live job NAMES)` from ONE `qstat`.

    ⚠ `-xml` IS REQUIRED FOR THE NAMES AND IS NOT A STYLE CHOICE. Plain `qstat -u` TRUNCATES
    `JB_name` to ten characters, so `leg3_leg_qwen3_6_27b_sweep_t4_p02` arrives as `leg3_leg_q`
    and every block would match every other block on the same line (P276). The ids are read from
    the same document, so this is still ONE ssh round trip, not two.
    """
    if _LIVE_OVERRIDE is not None or _LIVE_NAMES_OVERRIDE is not None:
        return set(_LIVE_OVERRIDE or ()), set(_LIVE_NAMES_OVERRIDE or ())
    # P204, same nesting invariant as _qacct_has_trace below: this must stay strictly under the
    # caller's timeout (cycle.py:1455 = 300 s; it was :907 when this was written) or the outer kill
    # orphans this ssh. 90 s matches the
    # timeout cycle.py already uses for its own direct `qstat` and is ~60x the measured 1.5 s cost.
    #
    # ⚠ AND IT MUST NOT FAIL SILENTLY. Shortening the timeout moved WHICH timeout fires, and that
    # changed how the failure is REPORTED. At 300 s the outer timeout won and cycle.py reported
    # rc=99 -> "the blind-spot detector could not run". At 90 s an unguarded TimeoutExpired would
    # propagate as a traceback and exit 1 -- and cycle.py:1460 only alerts on rc==1 AND "VANISHED"
    # in the output, while :1480 only attends on rc not in (0,1) (and :1466 now has its own rc==2
    # branch, which did not exist when this comment was written). So the layer's own failure would
    # have become INVISIBLE. Raising a distinct code keeps it on the ":918 attends" path, which is
    # where "this check could not run" belongs. Found by an independent auditor, not by me.
    try:
        out = subprocess.run(["ssh", "-o", "BatchMode=yes", "myriad", "qstat -u ucestes -xml"],
                             capture_output=True, text=True, timeout=90)
    except subprocess.TimeoutExpired:
        print("UNKNOWN -- qstat timed out after 90 s; the purge blind spot is UNWATCHED this cycle")
        raise SystemExit(99)
    ids: set[str] = set()
    names: set[str] = set()
    # A malformed or truncated document must not kill the sweep, and it must not read as "nothing
    # is alive" either -- that is the shape that turns a monitoring outage into a false incident.
    # 99 keeps it on cycle.py's "this check could not run" path, exactly as the timeout does.
    # ⚠⚠ P305-b (auditor finding). THE COMMENT ABOVE WAS TRUE AND THE CODE UNDER IT WAS NOT.
    # `ET.fromstring(out.stdout or "<x/>")` turned a FAILED qstat into a well-formed EMPTY document:
    # zero ids, zero names, and therefore EVERY pending block reading as dead. Proven by stubbing
    # ssh to exit 255 with empty stdout -- the tool reported `*** VANISHED ARRAY ***`. The dangerous
    # trigger is qmaster unreachable while ssh and qacct still answer, in which case nothing
    # downgrades the alarm and the whole board fires at once. `out.returncode` was never inspected.
    if out.returncode != 0 or not out.stdout.strip():
        print(f"UNKNOWN -- qstat -xml failed (rc={out.returncode}, {len(out.stdout or '')} bytes); "
              "the purge blind spot is UNWATCHED this cycle")
        raise SystemExit(99)
    try:
        root = ET.fromstring(out.stdout)
    except ET.ParseError:
        print("UNKNOWN -- qstat -xml did not parse; the purge blind spot is UNWATCHED this cycle")
        raise SystemExit(99)
    for j in root.iter("job_list"):
        jid = (j.findtext("JB_job_number") or "").strip()
        if jid.isdigit():
            ids.add(jid)
        nm = (j.findtext("JB_name") or "").strip()
        if nm:
            names.add(nm)
    return ids, names


def block_is_alive_by_name(blk: str, names: set[str]) -> bool:
    """Is any live job the driver's own job for `blk`? (P305)

    The driver names jobs `<block>_p<NN>`, and `<block>_r<N>_p<NN>` after a requeue, so the block
    name is an exact prefix followed by an underscore.

    ⚠ THE UNDERSCORE IS THE WHOLE POINT. `blk.startswith` alone makes `c1_tpe_c1` match
    `c1_tpe_c12_p01`, which is the substring class that let `crash_watchdog` recover `scalar` from
    `scalar_cvar5`. Selftest case H fails against the naive form.
    """
    pref = blk + "_"
    return any(n == blk or n.startswith(pref) for n in names)


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
    # It was 300 s and `cycle.py:1455` runs this script with timeout=300, so the OUTER timeout could
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
        # ⚠⚠ P305-b CHANGED THIS CASE'S EXPECTED EXIT CODE FROM 0 TO 2, AND THAT CHANGE IS THE WHOLE
        # POINT. It asserted rc==0, i.e. it asserted the FAIL-OPEN: the block is untested and the
        # tool exited clean over it. Measured live on `leg10_leg_kimi_k3_h2_pair_test` at 17.5 h.
        # UNKNOWN is not a negative, so an untested block must reach the UNRESOLVED list and rc=2.
        ee = subprocess.run(here + ["--live-ids=99999", "--qacct=unknown"], capture_output=True, text=True)
        if ee.returncode != 2 or "VANISHED" in ee.stdout or "UNKNOWN (qacct" not in ee.stdout:
            fails.append(f"E: unreachable qacct must report UNKNOWN, got {ee.returncode}\n{ee.stdout}")
        # CASE I -- the same state, asserted on the ARTEFACT A HUMAN READS rather than on the code:
        # an untested block must be NAMED in the UNRESOLVED listing, not merely counted. Separate
        # from E because E could pass on the exit code alone while the listing stayed silent.
        ii = subprocess.run(here + ["--live-ids=99999", "--qacct=unknown"], capture_output=True, text=True)
        if "UNRESOLVED" not in ii.stdout or "qacct unreachable" not in ii.stdout.split("UNRESOLVED")[-1]:
            fails.append(f"I: an untested block must be listed as UNRESOLVED with its reason\n{ii.stdout}")
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

        # ---- P305: the NAME fallback, on its own ISOLATED fixture -------------------------------
        # The fixture carries a pending block with NO `submitted` record at all, which is the only
        # state in which the name route can decide anything. Sharing case A/B's fixture would let
        # these pass through the id path and prove nothing (the P299-c isolation rule).
        with tempfile.TemporaryDirectory() as td2:
            d2 = Path(td2)
            (d2 / "driver_names.log").write_text(
                f"{recent} | INFO    | src.cluster.driver | [c1_tpe_c1] 0/9 done, 9 pending, round 0\n",
                encoding="utf-8")
            here2 = [sys.executable, str(Path(__file__).resolve()), str(d2)]
            # CASE G -- a live job carries the block's own name. The cluster has ANSWERED, so the
            # block is resolved and must NOT be counted unresolved. FAILS against every version of
            # this script before P305, which had no name route and exited 2 here.
            g = subprocess.run(here2 + ["--live-names=c1_tpe_c1_p01"], capture_output=True, text=True)
            if g.returncode != 0 or "UNRESOLVED" in g.stdout or "by NAME" not in g.stdout:
                fails.append(f"G: name match must resolve the block, got {g.returncode}\n{g.stdout}")
            # CASE H -- THE CONTROL, and the reason the underscore is in the matcher. The only live
            # job belongs to a DIFFERENT block that merely has this one as a prefix. Nothing has
            # answered for `c1_tpe_c1`, so it must STAY unresolved at rc=2. A naive
            # `startswith(blk)` passes G and FAILS this.
            h = subprocess.run(here2 + ["--live-names=c1_tpe_c12_p01"], capture_output=True, text=True)
            if h.returncode != 2 or "UNRESOLVED" not in h.stdout:
                fails.append(f"H: prefix-only name must NOT resolve, got {h.returncode}\n{h.stdout}")
        # CASE J -- P305-b: `--live-names` ALONE must mean OFFLINE, exactly as `--live-ids` does.
        # ⚠ IT NEEDS ITS OWN FIXTURE AND THE FIRST VERSION OF IT DID NOT HAVE ONE. Reusing the
        # case-A directory made it run AFTER case C unlinks that log, so it read the fresh fixture,
        # landed in the grace window and reported "benign" -- a green that had nothing to do with
        # the guard under test. It needs an AGED block that DOES carry array ids, because that is
        # the only shape in which the qacct guard is reachable at all (cases G/H have no ids and so
        # could never have exercised it, which is exactly why the defect shipped).
        # Guard correct  -> offline, no probe, `traced` stays None -> VANISHED at rc=1.
        # Guard as it was -> `_LIVE_OVERRIDE is None` -> FIRES A REAL `qacct` SSH -> anything else.
        with tempfile.TemporaryDirectory() as td3:
            d3 = Path(td3)
            (d3 / "driver_offline.log").write_text(body, encoding="utf-8")
            j = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), str(d3),
                 "--live-names=zzz_no_such_block_p01"], capture_output=True, text=True)
            if j.returncode != 1 or "VANISHED" not in j.stdout:
                fails.append(
                    f"J: --live-names alone must be OFFLINE (no qacct ssh), got {j.returncode}\n{j.stdout}")
    for f in fails:
        print("SELFTEST FAIL " + f)
    print(f"selftest: {10 - len(fails)}/10 cases pass")
    return 1 if fails else 0


if SELFTEST:
    raise SystemExit(_selftest())

live, live_names = live_jobs()
now = time.time()
print(f"live job ids on the cluster: {len(live)}  (distinct job names: {len(live_names)})")
print()
print("%-18s %-46s %5s %-24s %8s  %s"
      % ("LINE", "PENDING BLOCK", "PEND", "LAST ARRAYS", "AGE_MIN", "VERDICT"))

alerts: list[tuple[str, str, list[str], float]] = []
#: Blocks this run could NOT test -- no job id parsed, an unparsed timestamp, or qacct unreachable.
#: They must never be absorbed into "no vanished arrays detected": an UNKNOWN is not a negative.
unresolved: list[tuple[str, str, int, str]] = []
#: How many blocks the ID route could not resolve and the NAME route could (P305). Counted so the
#: all-clear line can state what actually happened: it used to claim "every batch resolved to a job
#: id", which was FALSE the moment the name route started resolving anything.
resolved_by_name = 0
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
            # P305: the log could not give an array id -- so ASK THE CLUSTER instead of giving up.
            # A live job carrying this block's name resolves it directly, and that is a measurement
            # rather than an absence. Only when the NAME is absent too is the block genuinely
            # untested, and it stays UNRESOLVED with the same rc=2 it had before.
            if block_is_alive_by_name(blk, live_names):
                resolved_by_name += 1
                print("%-18s %-46s %5d %-24s %8s  %s"
                      % (line, blk, pend, "(by name)", "-", "ok (job alive by NAME; no id in log)"))
                continue
            print("%-18s %-46s %5d %-24s %8s  %s" % (line, blk, pend, "-", "-", "UNKNOWN (no id parsed)"))
            unresolved.append((line, blk, pend, "no job id parsed, and no live job carries its name"))
            continue
        if any(i in live for i in ids):
            print("%-18s %-46s %5d %-24s %8s  %s"
                  % (line, blk, pend, ",".join(ids)[:24], "-", "ok (array alive)"))
            continue
        mins = (now - sts) / 60.0 if sts else -1.0
        if mins < 0:
            # P305-b: same class as the qacct branch below. Without a parsable submit timestamp the
            # grace window cannot be evaluated at all, so this block was NOT tested and must not be
            # absorbed into the all-clear.
            verdict = "UNKNOWN (unparsed ts)"
            unresolved.append((line, blk, pend, "submit timestamp did not parse"))
        elif mins < BENIGN_GRACE_MIN:
            verdict = "benign (just finished?)"
        else:
            # THE SECOND, DECISIVE TEST (P186). Gone from the queue is not enough -- a COMPLETED array
            # is also gone. Only an array with no accounting row was purged, which is precisely the
            # condition the driver's own "drain with NO qacct trace" message names.
            traced = _QACCT_OVERRIDE if _QACCT_SET else (
                None if _OFFLINE else has_qacct_trace(ids))
            if traced is True:
                verdict = "ok (arrays COMPLETED -- qacct row present; driver has yet to pull)"
            elif traced is None and (_QACCT_SET or not _OFFLINE):
                verdict = "UNKNOWN (qacct unreachable -- cannot distinguish purged from completed)"
                # ⚠⚠ P305-b. THIS BRANCH USED TO FALL STRAIGHT THROUGH TO exit(0). The block's
                # arrays are gone from the queue, no live job carries its name, it is past the
                # grace window, and accounting cannot say whether they COMPLETED or were PURGED.
                # That is the definition of untested, and the summary at the bottom of this file
                # then printed "no vanished arrays detected". Measured live 2026-08-04 22:0xZ on
                # `leg10_leg_kimi_k3_h2_pair_test` at age 1,048 min. The declaration above the
                # `unresolved` list has ALWAYS named this case; only the no-id branch implemented
                # it. An UNKNOWN is not a negative, and this is the third time in two days that
                # sentence has had to be enforced somewhere new.
                unresolved.append((line, blk, pend,
                                   "qacct unreachable -- purged and completed are indistinguishable"))
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
# ⚠⚠ THIS SAID "no vanished arrays detected" WHILE REPORTING `UNKNOWN (no id parsed)` FOR THE
# TWELVE MOST IMPORTANT BATCHES ON THE BOARD (2026-08-04, RUN 21). haiku and qwen3.6-27b each had
# SIX open sweep tiers -- 2,464 and 2,626 units pending -- and the watcher could not parse a job id
# for any of them, so it did not know whether their arrays were alive, purged or gone. It then
# printed a clean summary. **An UNKNOWN is not a negative**, and a summary that absorbs UNKNOWNs
# into "detected nothing" is the single defect class this campaign has fixed most often.
if unresolved:
    _tot = sum(r[2] for r in unresolved)
    print("no vanished array detected AMONG THE BLOCKS THIS RUN COULD RESOLVE -- but %d block(s) "
          "carrying %d PENDING UNIT(S) returned UNKNOWN and were NOT tested:" % (len(unresolved), _tot))
    for _r in unresolved[:14]:
        print("    UNRESOLVED  %-18s %-46s %6d pending  (%s)" % (_r[0], _r[1], _r[2], _r[3]))
    print("    An UNKNOWN is not a negative. Read this as 'the detector could not see these',")
    print("    never as 'these are fine'. Check the line's driver log and `qstat -u ucestes -xml`.")
    sys.exit(2)
# P305-b: state what actually happened. This line read "every batch resolved to a job id and was
# tested", which the name route falsified the first time it fired -- four blocks that pass resolved
# by NAME, not by id. A summary that overstates its own coverage is how an all-clear stops meaning
# anything.
print("no vanished arrays detected -- every pending block was TESTED "
      f"({resolved_by_name} of them resolved by job NAME rather than by an array id from the log)")
