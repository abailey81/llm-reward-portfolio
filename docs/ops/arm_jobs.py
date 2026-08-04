#!/usr/bin/env python
"""ARM-LEVEL JOB JOIN -- the detector RUN 19 handed to RUN 20 as its highest-value open row (A-d14).

★ THE QUESTION THIS ANSWERS, AND WHY NOTHING ELSE COULD.

Under R101 the reported scientific result is the COMMON RUNG, a MINIMUM over every registered arm
of every line. So a single arm that stops producing caps the entire campaign. The two instruments
that look at this each hold one half of the signal and neither joins them:

  * `docs/analysis/record_seed_completeness.py` (S15) knows exactly WHICH arm caps each line -- and
    says in its own verdict that it "cannot see jobs", so it cannot tell a mid-fill from a death.
  * `docs/ops/line_balance.py` knows the jobs -- but its STUCK/WAITING split is PER LINE
    (`line_balance.py:265` `run, queued = jobs.get(tag, (0, 0))`, one pair per line), so a line whose
    CAPPING arm has no job anywhere still reads WAITING as long as ANY OTHER arm on it has one.
    It even computes the per-arm "arms at ZERO" column at `:255` and then never joins it to the jobs.

This file performs that join.

⚠⚠ WHY THE JOIN COULD NOT BE BUILT FROM WHAT `line_balance` ALREADY COLLECTS, and this is the part
worth keeping: **`qstat` TRUNCATES the job name to 10 characters.** Measured live 2026-08-04:

    76849 2.00578 leg8_leg_s ucestes      r     08/04/2026 01:48:57 ...

`leg8_leg_s` is all the default format gives. The arm token is destroyed by the SCHEDULER'S OUTPUT
FORMAT, not by line_balance's parse, so no amount of care in that parser could have recovered it.
`qstat -xml` returns the untruncated `JB_name` for the same scheduler query, and that is what this
file uses. RUN 19 recorded the detector as buildable from what was already there; it was not.

★ THE COVERING RULE -- READ FROM THE LAUNCHER, NEVER ASSUMED. A job covers an arm when:

  1. its name contains the arm as a WHOLE token          -- `run_test_leg`'s per-arm name
  2. its name contains `h2_pair`  and the arm is in the H2 pair (distributional, scalar)
                                                          -- `src/cluster/campaign.py:1908`
  3. its name contains `_sweep_t<N>` (the C4 sweep runs every arm in the sweep unit list)
                                                          -- `src/cluster/campaign.py:2012`

⚠ RULE 1 MUST PREFER THE LONGEST MATCHING ARM. `leg7_..._scalar_cvar5_test_p01` contains the
substring `_scalar_`, so a naive `("_%s_" % arm) in name` test reports that job as covering
`scalar`. It does not -- it covers `scalar_cvar5` only. My first version made exactly this mistake
and reported nemotron's `scalar` as covered while it was not.

★ FAILURE DIRECTION. Every path here fails toward "CANNOT DECIDE", never toward "clean":
  * the queue could not be read, or the XML did not parse  -> exit 2, and NOTHING is reported clean
  * a line's `frozen*/` roster is unreadable               -> the line is named LOUDLY, never dropped
  * a line's batch tag could not be resolved               -> the line is UNDECIDABLE, never clean
This is deliberate. `line_balance.frozen_arms()` returning an empty set makes the line vanish from
its table with no message at all (`line_balance.py:134-135` `if not arms: continue`), which is the
"silent non-match reads as all clean" shape this campaign keeps finding.

★ WHAT A FLAGGED ARM MEANS. It is NOT automatically a fault, and reading it as one would be the
opposite error. An arm is flagged when it sits BELOW ITS OWN LINE'S FRONTIER and no job covers it.
Three benign causes, in descending order of how often they are the answer:
  1. the line has not yet reached the pipeline stage that tests that arm (every line tests its
     `h2_pair` LAST, and the core line's C2 pair-test fires only after its serial C1 DFO chain);
  2. a driver repair round is about to submit (measured 2026-08-03: gpt-5.6-luna sat job-less for
     20 minutes and then repaired its own 8 seeds);
  3. the arm is waiting behind a gate its line has not cleared.
The DISCRIMINATOR is the driver log. This file names the arm and the evidence; it does not diagnose.

Usage:  python docs/ops/arm_jobs.py [--selftest]
Exit:   0 nothing flagged * 1 at least one arm flagged * 2 could not decide (read failure)

READ-ONLY with respect to the campaign: one `qstat -xml`, one directory census, no writes anywhere.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "outputs" / "campaign_cluster_run4"
SSH_TIMEOUT_SECS = 120

# The H2 pair, read from the launcher's own name for it. `campaign.py:1907` builds `h2_present`
# from `h2_arms`; the two arms are the manipulated contrast the whole study rests on.
H2_PAIR = frozenset({"distributional", "scalar"})

SEED_DIR = re.compile(r"-s\d+$")


# --------------------------------------------------------------------------------------------
# the queue, untruncated
# --------------------------------------------------------------------------------------------
def queue_jobs(host: str = "myriad") -> tuple[list[tuple[str, str]], str]:
    """[(job_name, state)] from ONE `qstat -xml`, plus a status string.

    Returns ([], "<reason>") on ANY read failure. The caller MUST treat a non-"OK" status as
    undecidable -- an empty job list from a failed transport is indistinguishable from a genuinely
    empty queue, and `line_balance.cluster_jobs()` collapses exactly those two into the same `{}`.
    """
    try:
        p = subprocess.run(["ssh", "-o", "BatchMode=yes", host, "qstat -u ucestes -xml"],
                           capture_output=True, text=True, timeout=SSH_TIMEOUT_SECS)
    except Exception as exc:  # noqa: BLE001 - transport failure is reported, never fatal
        return [], "TRANSPORT-FAILED: %s" % repr(exc)[:90]
    if p.returncode not in (0, 1):
        return [], "TRANSPORT-FAILED: rc=%d %s" % (p.returncode, (p.stderr or "")[:120])
    return parse_qstat_xml(p.stdout)


def parse_qstat_xml(text: str) -> tuple[list[tuple[str, str]], str]:
    """Split out so the selftest can exercise it without a cluster."""
    if not text.strip():
        return [], "EMPTY-OUTPUT: qstat returned nothing at all"
    try:
        tree = ET.fromstring(text)
    except Exception as exc:  # noqa: BLE001
        return [], "UNPARSEABLE-XML: %s" % repr(exc)[:90]
    jobs: list[tuple[str, str]] = []
    for jl in tree.iter("job_list"):
        nm = jl.findtext("JB_name") or ""
        st = jl.findtext("state") or (jl.get("state") or "")
        if nm:
            jobs.append((nm, st))
    return jobs, "OK"


# --------------------------------------------------------------------------------------------
# the roster, the depths and the tags
# --------------------------------------------------------------------------------------------
def registered_arms(root: Path, line_dir: str) -> set[str]:
    """The arms a line has COMMITTED to test, from its frozen-winner markers.

    S15's rule is used deliberately: a `-winner` SUFFIX is REQUIRED. `line_balance.frozen_arms()`
    accepts ANY subdirectory, so a `_tmp`, `logs` or `.ipynb_checkpoints` sibling becomes a phantom
    arm with zero records that pins its line below the frontier forever. Two instruments that
    disagree about what an arm IS cannot be reconciled, so this one follows the stricter of the two.
    """
    frozen = root / ("frozen" + line_dir[len("test"):])
    if not frozen.is_dir():
        return set()
    return {d.name[:-len("-winner")] for d in frozen.iterdir()
            if d.is_dir() and d.name.endswith("-winner")}


def seed_count(root: Path, line_dir: str, arm: str) -> int:
    """Distinct seed directories holding a record, matching S15's `scan()` rule exactly."""
    p = root / line_dir / arm
    if not p.is_dir():
        return 0
    return sum(1 for d in p.iterdir()
               if d.is_dir() and SEED_DIR.search(d.name) and (d / "record.json").is_file())


def test_dir_for_cmd(cmd: str) -> str:
    """The sealed-test directory a launch command writes into (line_balance's rule, verbatim)."""
    if "--h3-singleshot" in cmd:
        return "test_h3_singleshot"
    m = re.search(r"--leg\s+(\S+)", cmd)
    if not m:
        return "test"                                    # the core line carries no --leg
    return "test_leg_" + re.sub(r"[^a-z0-9]", "_", m.group(1).lower())


def batch_tag_map(root: Path) -> dict[str, str]:
    """{test_dir: batch_tag} from each supervisor log's most recent launch command.

    The batch tag (`leg2`) is NOT derivable from the archive name (`test_leg_glm_5_2`). My first
    version of this file derived the job prefix from the archive name, matched nothing on all ten
    leg lines, and flagged 23 arms as uncovered -- including arms whose covering jobs I had read
    off the queue by hand minutes earlier. The tag has to come from the launch command.
    """
    out: dict[str, str] = {}
    if not root.is_dir():
        return out
    for name in sorted(os.listdir(root)):
        if not (name.startswith("supervisor_") and name.endswith(".log")):
            continue
        try:
            with open(root / name, "r", encoding="utf-8", errors="replace") as fh:
                lns = fh.readlines()
        except OSError:
            continue
        for ln in reversed(lns):                         # the most recent launch wins
            if "line supervisor started:" not in ln:
                continue
            m = re.search(r"--batch-tag\s+(\S+)", ln)
            if m:
                out[test_dir_for_cmd(ln)] = m.group(1)
            break
    return out


# --------------------------------------------------------------------------------------------
# the covering rule
# --------------------------------------------------------------------------------------------
def names_arm(job_name: str, arm: str, roster: set[str]) -> bool:
    """True when `job_name` names `arm` as a WHOLE token, preferring the LONGEST matching arm.

    `leg7_..._scalar_cvar5_test_p01` contains `_scalar_`. It covers `scalar_cvar5`, NOT `scalar`.
    A plain substring test gets this wrong in the reassuring direction, which is why the roster is
    passed in: at every position where `arm` matches, a LONGER roster arm matching at the same
    position wins and this returns False.
    """
    padded = "_" + job_name + "_"
    needle = "_" + arm + "_"
    start = 0
    while True:
        i = padded.find(needle, start)
        if i < 0:
            return False
        # any longer roster arm anchored at the same '_' beats this match
        beaten = False
        for other in roster:
            if len(other) > len(arm) and padded.startswith("_" + other + "_", i):
                beaten = True
                break
        if not beaten:
            return True
        start = i + 1


def covering_jobs(jobs: list[tuple[str, str]], arm: str, roster: set[str]) -> list[tuple[str, str]]:
    out = []
    for jn, st in jobs:
        if names_arm(jn, arm, roster):
            out.append((jn, st))
        elif "h2_pair" in jn and arm in H2_PAIR:
            out.append((jn, st))
        elif "_sweep_t" in jn:
            out.append((jn, st))
    return out


# --------------------------------------------------------------------------------------------
# the report
# --------------------------------------------------------------------------------------------
def report(root: Path, jobs: list[tuple[str, str]], status: str) -> int:
    print("=== ARM-LEVEL JOB JOIN -- which arm below its line's frontier has NO job at all ===")
    print("qstat -xml status: %s   jobs seen: %d" % (status, len(jobs)))
    if status != "OK":
        print("*** CANNOT DECIDE -- the queue was not read, so NOTHING here is a clean result. ***")
        print("    An empty job list from a failed transport is indistinguishable from an empty")
        print("    queue, so this exits 2 rather than reporting every arm as uncovered.")
        return 2
    if not root.is_dir():
        print("*** CANNOT DECIDE -- campaign root does not exist: %s" % root)
        return 2

    states: dict[str, int] = {}
    for _n, s in jobs:
        states[s] = states.get(s, 0) + 1
    print("state census: %s" % dict(sorted(states.items())))
    print("  (line_balance counts ONLY exact 'r' and 'qw'. Every other state above -- 'Rq', 'hqw',")
    print("   't', 'dr' -- is invisible to it, so its queued column can read low. This file counts")
    print("   a job as COVERING in whatever state it holds, because a held job is still work.)")

    tags = batch_tag_map(root)
    test_dirs = sorted(d.name for d in root.iterdir()
                       if d.is_dir() and d.name.startswith("test") and not d.name.startswith("."))
    print("lines enumerated: %d   batch tags resolved: %d" % (len(test_dirs), len(tags)))
    print()

    flagged: list[str] = []
    undecidable: list[str] = []
    rosterless: list[str] = []

    for td in test_dirs:
        roster = registered_arms(root, td)
        if not roster:
            rosterless.append(td)
            continue
        tag = tags.get(td, "")
        if not tag:
            undecidable.append(td)
            continue
        mine = [(n, s) for n, s in jobs if n.startswith(tag + "_")]
        depths = {a: seed_count(root, td, a) for a in sorted(roster)}
        frontier = max(depths.values()) if depths else 0
        rows = []
        for arm in sorted(roster):
            n = depths[arm]
            if n >= frontier:
                continue          # at its own line's frontier: it is not what caps this line
            cov = covering_jobs(mine, arm, roster)
            rows.append((arm, n, cov))
        if not rows:
            continue
        print("%s   tag=%s  jobs on this line=%d  frontier=%d records"
              % (td, tag, len(mine), frontier))
        for arm, n, cov in rows:
            ex = ("e.g. %s [%s]" % (cov[0][0], cov[0][1])) if cov else ""
            flag = "   <<< NO JOB COVERS THIS ARM" if not cov else ""
            print("   %-20s records=%-5d covering=%-4d %s%s" % (arm, n, len(cov), ex, flag))
            if not cov:
                flagged.append("%s / %s (records=%d, line frontier=%d)" % (td, arm, n, frontier))
        print()

    rc = 0
    if rosterless:
        print("*** %d LINE(S) HAVE NO READABLE frozen*/ ROSTER -- NOT judged, and NOT clean ***"
              % len(rosterless))
        for t in rosterless:
            print("    %s" % t)
        print("  line_balance drops these silently (`if not arms: continue`). They are named here")
        print("  because an unannounced empty roster is indistinguishable from a healthy line.")
        print()
        rc = max(rc, 2)
    if undecidable:
        print("*** %d LINE(S) UNDECIDABLE -- batch tag unresolved from the supervisor log ***"
              % len(undecidable))
        for t in undecidable:
            print("    %s" % t)
        print()
        rc = max(rc, 2)

    print("=== VERDICT ===")
    if flagged:
        print("%d ARM(S) SIT BELOW THEIR LINE'S FRONTIER WITH NO COVERING JOB:" % len(flagged))
        for a in flagged:
            print("    %s" % a)
        print()
        print("  *** THIS IS NOT AUTOMATICALLY A FAULT. *** It is the case S15 calls ACTIONABLE and")
        print("  line_balance's per-LINE aggregation structurally cannot see. Before concluding")
        print("  anything, read the line's driver log: an arm whose line has not yet reached the")
        print("  stage that tests it is waiting BY DESIGN (every line tests its h2_pair LAST, and")
        print("  the core line's C2 pair-test fires only after its serial C1 chain completes), and")
        print("  a driver repair round may be about to submit.")
        rc = max(rc, 1)
    else:
        print("Every arm below its line's frontier has at least one covering job.")
    return rc


# --------------------------------------------------------------------------------------------
# selftest -- every case must FAIL against the behaviour it replaces
# --------------------------------------------------------------------------------------------
def _selftest() -> int:
    import json
    import tempfile

    passed = failed = 0

    def check(name: str, got, want) -> None:
        nonlocal passed, failed
        if got == want:
            passed += 1
            print("  PASS  %-58s %r" % (name, got))
        else:
            failed += 1
            print("  FAIL  %-58s got %r want %r" % (name, got, want))

    roster = {"distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled"}

    print("A. names_arm -- the LONGEST-ARM rule (the bug my first version shipped)")
    # A1/A2 are the pair that discriminates: the naive `"_scalar_" in name` test passes BOTH.
    check("A1 scalar_cvar5 job does NOT cover scalar",
          names_arm("leg7_leg_nemotron_3_super_scalar_cvar5_test_p01", "scalar", roster), False)
    check("A2 scalar_cvar5 job DOES cover scalar_cvar5",
          names_arm("leg7_leg_nemotron_3_super_scalar_cvar5_test_p01", "scalar_cvar5", roster), True)
    check("A3 a real scalar job covers scalar",
          names_arm("leg7_leg_nemotron_3_super_scalar_test_p01", "scalar", roster), True)
    check("A4 placebo_shuffled job does NOT cover placebo",
          names_arm("leg1_leg_deepseek_v4_pro_placebo_shuffled_test", "placebo", roster), False)
    check("A5 placebo_shuffled job DOES cover placebo_shuffled",
          names_arm("leg1_leg_deepseek_v4_pro_placebo_shuffled_test", "placebo_shuffled", roster), True)
    check("A6 trailing-token match (name ends with the arm)",
          names_arm("leg6_leg_gpt_5_6_luna_scalar", "scalar", roster), True)
    check("A7 an unrelated arm is not matched",
          names_arm("leg2_leg_glm_5_2_h2_pair_test_p01", "placebo", roster), False)

    print("B. covering_jobs -- the three launcher rules")
    jobs = [("leg2_leg_glm_5_2_h2_pair_test_p01", "r"),
            ("leg4_leg_qwen3_5_9b_sweep_t2_p01", "qw"),
            ("leg7_leg_nemotron_3_super_scalar_cvar5_test_p01", "r")]
    check("B1 h2_pair covers distributional", len(covering_jobs(jobs, "distributional", roster)), 2)
    check("B2 h2_pair covers scalar", len(covering_jobs(jobs, "scalar", roster)), 2)
    check("B3 sweep covers an arm no per-arm job names",
          len(covering_jobs(jobs, "placebo", roster)), 1)
    check("B4 scalar_cvar5 matched by its own job AND the sweep",
          len(covering_jobs(jobs, "scalar_cvar5", roster)), 2)

    print("C. parse_qstat_xml -- failure must never look like an empty queue")
    check("C1 empty output is not OK", parse_qstat_xml("")[1].startswith("EMPTY-OUTPUT"), True)
    check("C2 garbage is not OK", parse_qstat_xml("not xml at all")[1].startswith("UNPARSEABLE"), True)
    ok_xml = ("<job_info><queue_info>"
              "<job_list state='running'><JB_name>c1_tpe_c27</JB_name><state>r</state></job_list>"
              "</queue_info></job_info>")
    check("C3 a real payload parses", parse_qstat_xml(ok_xml)[0], [("c1_tpe_c27", "r")])
    check("C4 a well-formed EMPTY queue is OK, not an error",
          parse_qstat_xml("<job_info></job_info>"), ([], "OK"))

    print("D. report -- an unreadable roster is LOUD, and a read failure is never clean")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        # one line with a roster and a producing arm, one line with NO roster at all
        for arm in ("distributional", "scalar"):
            (root / "frozen_leg_x" / (arm + "-winner")).mkdir(parents=True)
        (root / "test_leg_x" / "distributional" / "distributional-s0").mkdir(parents=True)
        (root / "test_leg_x" / "distributional" / "distributional-s0" / "record.json").write_text(
            json.dumps({}), encoding="utf-8")
        (root / "test_leg_y").mkdir()          # a test dir whose frozen_leg_y does not exist
        (root / "supervisor_x.log").write_text(
            "line supervisor started: run_campaign_cluster.py --leg x --batch-tag legX\n",
            encoding="utf-8")
        rc_fail = report(root, [], "TRANSPORT-FAILED: injected")
        check("D1 a failed queue read exits 2, never 0", rc_fail, 2)
        rc_ok = report(root, [("legX_leg_x_placebo_test", "r")], "OK")
        # scalar sits at 0 below a frontier of 1 and no job covers it -> flagged (rc 1);
        # test_leg_y has no roster -> rosterless -> rc 2 dominates.
        check("D2 a rosterless line forces 2 rather than vanishing", rc_ok, 2)

    print()
    print("selftest: %d passed, %d FAILED" % (passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    _jobs, _status = queue_jobs()
    sys.exit(report(ROOT, _jobs, _status))
