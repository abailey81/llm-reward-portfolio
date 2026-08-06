#!/usr/bin/env python
"""JOB RANK GOVERNOR — rank OUR OWN pending queue by marginal value to the REPORTED RESULT.

Tamer, 2026-08-06: *"have a very smart ranking system that places jobs, don't place the jobs
blindly."*  This is that ranking system.

THE PROBLEM, AND IT IS NOT A CLUSTER PROBLEM
--------------------------------------------
Our pending jobs are dispatched in an order set almost entirely by ACCRUED WAITING TIME (the
Myriad priority formula gives waiting time weight 1.0 while our functional tickets sit pinned at
the cluster floor — dossier §1). Waiting time is a function of SUBMISSION ORDER, which is an
accident of which driver reached its next batch boundary first. **It has no relationship whatever
to what the dissertation needs next.**

Measured on 2026-08-06 04:2x UTC, that accident costs us everything:

    our pending set              892 jobs
    jobs outranking c1_tpe       410  (233 leg10 + 157 leg2 + 13 leg3 + 7 c1)
    => c1_tpe sits at rank 408-411 of 892, behind ~60 h of queue drain at 6.4-6.8 jobs/h

and c1 is **the only line whose work can raise the reported result at all** (below).

THE VALUE MODEL — WHY "MARGINAL VALUE" HAS AN EXACT DEFINITION HERE
-------------------------------------------------------------------
Under R101 the reported result is the COMMON RUNG: the MINIMUM banked rung over every registered
(line, arm). So a job's value is not "does it produce a record" — every job does that. It is:

    >>> by how much does completing this job raise that MINIMUM? <<<

That makes the ranking objective rather than a matter of taste, and it makes most of our fleet
worthless *at the margin*: eleven of twelve lines already bank rung 30, so a record landing on any
of them moves the reported minimum by exactly ZERO. Tamer's 2026-08-06 priority — *"bank all the
results for absolutely all arms at 30 seeds first, the ladder is optional comparing to that"* — is
therefore not a preference imposed on the arithmetic. It IS the arithmetic.

    V0  FLOOR-CRITICAL     the (line, arm) banks BELOW the floor rung. These arms are PINNING the
                           common rung right now, so ONLY these jobs can raise the reported result.
    V1  HOLE REPAIR        the arm's banked rung is demoted by a hole below its own frontier.
                           Cheap and violently non-linear: haiku holds 566 records with a frontier
                           of 567 and banks 189, because seeds 272/273 are missing. Eight trainings
                           would take that line 189 -> 568.
    V2  LINE MINIMUM       the arm is the minimum inside its own line, so it gates that line's next
                           rung. Real value, but above the floor.
    V3  LADDER EXTENSION   everything else. ZERO marginal value to the floor.

WHAT THIS IS NOT — AND WHY THAT DISTINCTION IS THE WHOLE SAFETY ARGUMENT
------------------------------------------------------------------------
`MYRIAD_EXPERT_DOSSIER §0-PRE M5` REFUTED "hold jobs to concentrate tickets", by controlled test:
holding 228 of 309 pending jobs moved our top priority 2.0165 -> 2.0413 (waiting-time accrual,
which happens anyway) and **decayed our running count 44 -> 9. We starved ourselves.**

This governor does not claim, and does not need, the mechanism M5 refuted. It makes NO claim about
our standing against other users, which is fair-share and not ours to move. It claims only the
tautology that a HELD job is not eligible, so among OUR OWN jobs the next free slot goes to the
highest-priority job we have left eligible. M5 starved because it left 81 eligible against 44
running, and 60 of those 81 were 32-core jobs that could never place. The corresponding invariant
here is `min_eligible`, and it is enforced, not hoped for:

    eligible_after >= max(DEPTH_FACTOR * running_jobs, DEPTH_FLOOR)

At the live 68 running jobs that is 272, and the plan below leaves 489. Queue depth stays ~7x our
running count, i.e. the same backfill flow that currently sustains the fleet (dossier M4).

SAFETY INVARIANTS — all enforced in code, all covered by `--selftest`
--------------------------------------------------------------------
 1. `qhold` / `qrls` ONLY. This module never emits `qdel` and never emits `qalter -p`
    (CLAUDE.md: never lower the priority of any of our jobs, EVER; `qalter -p` is one-way for a
    non-operator, `qdel` destroys up to 15 h of irreplaceable sealed-test work).
 2. Only state `qw` is ever considered. A RUNNING job is structurally unreachable here.
 3. `min_eligible` is a hard floor: the plan is TRUNCATED to respect it, never the reverse.
 4. **THIS MODULE EXECUTES NOTHING.** It emits a command list for a human to run. Reordering our
    own queue crosses a standing rule (CLAUDE.md ★ MYRIAD PRIORITY) and is Tamer's call, so the
    tool does the arithmetic and the human takes the decision.
 5. Every emitted plan writes a JOURNAL of held ids, so a full release is possible even if this
    process, the session, or the laptop dies mid-way. `--release-from` regenerates that release.

USAGE
    python docs/ops/job_rank_governor.py                 # measure + rank + print the plan
    python docs/ops/job_rank_governor.py --selftest      # no cluster needed
    python docs/ops/job_rank_governor.py --release-from docs/ops/watch/JOB_RANK_HOLDS.json
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "docs" / "ops"))
sys.path.insert(0, str(REPO / "docs" / "analysis"))

import arm_jobs as AJ                       # noqa: E402  — reuse, never re-derive
import record_seed_completeness as S15      # noqa: E402

ROOT = REPO / "outputs" / "campaign_cluster_run4"
JOURNAL = REPO / "docs" / "ops" / "watch" / "JOB_RANK_HOLDS.json"
# ⚠ A SEPARATE JOURNAL, DELIBERATELY. The rung-order plan and the floor-promotion plan are
# different hold sets with different release predicates, and writing both to one file would let a
# release of one silently discard the record of the other — the single-file collision class that
# `TIER1_APPROVED` already cost this campaign once (campaign.py:1927).
TIER_JOURNAL = REPO / "docs" / "ops" / "watch" / "RUNG_ORDER_HOLDS.json"
SSH_TIMEOUT_SECS = 120

DEPTH_FACTOR = 4          # eligible queue must stay >= 4x the running job count (backfill flow)
DEPTH_FLOOR = 200         # ... and never below this in absolute terms
# ⚠ DEFAULT IS 0 — FLOOR ONLY — AND THAT IS A MEASURED CHOICE, NOT TIMIDITY. Promoting V0+V1
# together costs far more than it buys: haiku's repair job carries a LOWER priority than c1's, so
# including it drags the promotion target down and turns a 402-job hold into a 619-job hold that
# hits the depth guard exactly (272 eligible, 4.0x running, 14 blockers left in on purpose).
# Promoting V0 alone holds 402 and leaves 489 eligible (7.2x running) with no truncation at all.
# Tamer's 2026-08-06 priority is the FLOOR — "the ladder is optional comparing to that" — and
# haiku's +379 rungs are ladder. Use --promote-max-tier 1 to include the repair deliberately.
PROMOTE_MAX_TIER = 0

# ⚠ THE HOLE-COST BOUND, AND IT IS LOAD-BEARING. A hole alone does NOT make an arm worth
# promoting, because `FLAWLESS_LEDGER` records the reason plainly: "During pipelined C4 a line
# lands seeds OUT OF ORDER as pack-8 jobs return, so a CLIMBING LINE ALWAYS SHOWS HOLES. That is
# the normal state and it self-heals." Without this bound the first live run promoted 321 of 891
# pending jobs — every kimi sweep job, because kimi is mid-climb with 312 holes per arm — and
# buried the 8 floor-critical jobs the whole instrument exists to surface. V1 must therefore mean
# what it says: a CHEAP repair with a LARGE rung payoff (haiku, 8 missing records for +379 rungs),
# never "this line is still climbing". 24 = three pack-8 jobs' worth of trainings.
REPAIR_MAX_HOLES = 24

# ⚠ MY OWN DEFECT, CAUGHT ON RE-READING THE DIFF. This was written as
#     max(0.0, (date(2026, 8, 27) - date(2026, 8, 6)).days)
# i.e. a HARDCODED 21 dressed up as an arithmetic expression. It would have read 21 for the rest of
# the campaign, and every capacity figure derived from it would have been silently optimistic by a
# day per day. That is precisely the stale-count defect class this project keeps finding, and the
# comment beside it said "Recompute, never carry forward" while the code did the opposite.
EXOGENOUS_STOP = _dt.date(2026, 8, 27)          # R101, frozen


def days_to_stop(today: _dt.date | None = None) -> float:
    """Days remaining to the exogenous stop, from the REAL clock. Never negative."""
    return float(max(0, (EXOGENOUS_STOP - (today or _dt.date.today())).days))

TIER_NAME = {0: "V0 FLOOR-CRITICAL", 1: "V1 HOLE-REPAIR",
             2: "V2 LINE-MINIMUM", 3: "V3 LADDER-EXTENSION"}


# ---------------------------------------------------------------------------------------------
# the live read
# ---------------------------------------------------------------------------------------------
def _ssh(cmd: str, host: str) -> tuple[str, str]:
    try:
        p = subprocess.run(["ssh", "-o", "BatchMode=yes", host, cmd],
                           capture_output=True, encoding="utf-8", errors="replace",
                           timeout=SSH_TIMEOUT_SECS)
    except Exception as exc:                                    # noqa: BLE001
        return "", "TRANSPORT-FAILED: %s" % repr(exc)[:90]
    if p.returncode not in (0, 1):
        return "", "TRANSPORT-FAILED: rc=%d %s" % (p.returncode, (p.stderr or "")[:120])
    return p.stdout, "OK"


def parse_jobs_xml(text: str) -> tuple[list[dict], str]:
    """[{jid, name, state, prior}] from `qstat -u ucestes -xml`.

    Split out from the transport so the selftest exercises it with no cluster. `arm_jobs`
    deliberately returns only (name, state); the governor additionally needs the job ID (to emit a
    command) and the priority (to know what is actually in FRONT), so this is the one piece of
    qstat parsing that cannot be reused as-is.
    """
    if not text.strip():
        return [], "EMPTY-OUTPUT: qstat returned nothing at all"
    try:
        tree = ET.fromstring(text)
    except Exception as exc:                                    # noqa: BLE001
        return [], "UNPARSEABLE-XML: %s" % repr(exc)[:90]
    out: list[dict] = []
    for jl in tree.iter("job_list"):
        jid = (jl.findtext("JB_job_number") or "").strip()
        nm = (jl.findtext("JB_name") or "").strip()
        st = (jl.findtext("state") or jl.get("state") or "").strip()
        try:
            pr = float(jl.findtext("JAT_prio") or "0")
        except ValueError:
            pr = 0.0
        if jid and nm:
            out.append({"jid": jid, "name": nm, "state": st, "prior": pr})
    return out, "OK"


# ---------------------------------------------------------------------------------------------
# the value model  (pure — this is what the selftest pins)
# ---------------------------------------------------------------------------------------------
def common_rung(scan: dict, rungs: list) -> tuple[int, int]:
    """(current COMMON rung, the NEXT registered rung above it).

    The common rung is the MINIMUM banked rung over every registered `(line, arm)` — under R101 it
    IS the reported result, so it is the only quantity a job can be valuable *relative to*.
    Computed, never assumed: it was 0 on 2026-08-06 because `c1` holds four arms at 0 while eleven
    lines bank >= 30.
    """
    if not scan:
        return 0, min(rungs)
    cur = min(S15.banked_rung(d["seeds"], rungs) for d in scan.values())
    nxt = next((r for r in sorted(rungs) if r > cur), max(rungs))
    return cur, nxt


def line_deficits(scan: dict, target: int) -> dict:
    """{line: trainings still needed for EVERY arm on that line to bank `target`}.

    ⭐ THIS IS THE QUANTITY THE RANKING TURNS ON, AND IT CORRECTED MY FIRST MODEL.
    Because the reported result is a MINIMUM over lines, it rises only when the LAST line arrives —
    so the makespan is set by the line with the LARGEST remaining deficit, and cores are worth most
    on THAT line, not on the cheapest one. Finishing a cheap laggard first feels like progress and
    moves the reported result by nothing. Measured 2026-08-06 at target 100: nemotron and glm and
    deepseek owe 350 each, kimi 278, and every other line owes 0 — while kimi held 6.5x more queued
    work than it needed and qwen3.6 held 640 trainings against a deficit of ZERO.
    """
    per: dict[str, int] = {}
    for (line, arm), d in scan.items():
        per[line] = per.get(line, 0) + sum(1 for s in range(target) if s not in d["seeds"])
    return per


def arm_tiers(scan: dict, rungs: list) -> dict:
    """{(line, arm): (tier, banked, banked_if_repaired)} for every registered (line, arm).

    `banked_if_repaired` answers the question that makes V1 worth a tier of its own: what would
    this arm bank if the holes below its frontier were filled? For haiku that is 568 against a
    banked 189, and the gap is the value of ~8 trainings.
    """
    floor = min(rungs)
    per_line: dict[str, list] = {}
    banked: dict = {}
    repaired: dict = {}
    for (line, arm), d in scan.items():
        b = S15.banked_rung(d["seeds"], rungs)
        banked[(line, arm)] = b
        if d["started"] and d["holes"] and len(d["holes"]) <= REPAIR_MAX_HOLES:
            filled = set(d["seeds"]) | set(d["holes"])
            repaired[(line, arm)] = S15.banked_rung(filled, rungs)
        else:
            # either no holes at all, or too many to be a repair: a mid-climb line is NOT a
            # repair candidate however large its notional rung gap (REPAIR_MAX_HOLES).
            repaired[(line, arm)] = b
        per_line.setdefault(line, []).append(b)

    out = {}
    for (line, arm), b in banked.items():
        if b < floor:
            tier = 0
        elif repaired[(line, arm)] > b:
            tier = 1
        elif b == min(per_line[line]):
            tier = 2
        else:
            tier = 3
        out[(line, arm)] = (tier, b, repaired[(line, arm)])
    return out


def job_tier(job_name: str, tag_to_line: dict, rosters: dict, tiers: dict) -> tuple[int, list]:
    """The BEST (numerically lowest) tier of any arm this job covers, plus the arms it covers.

    A job is worth what its most valuable covered arm is worth: a pack-8 job carrying one
    floor-critical seed is floor-critical, whatever else rides along with it.

    ⚠ THE COVERING RULE IS `arm_jobs.covering_jobs`'s, REPRODUCED EXACTLY, AND THE `_sweep_t`
    CLAUSE IS THE ONE THAT MATTERS. A sweep job (`leg5_leg_haiku_4_5_sweep_t3_r1`) names NO arm
    and covers ALL of them. My first version omitted that clause, and the live run scored haiku's
    pending hole-repair job — worth +379 rungs on five arms — as V3 LADDER-EXTENSION, i.e. as
    worthless. A ranking instrument that silently misranks the highest-value job in the queue is
    worse than no instrument, because it launders a bad placement as a considered one.
    """
    tag = job_name.split("_", 1)[0]
    line = tag_to_line.get(tag)
    if line is None:
        return 3, []                       # unknown tag -> treat as ladder, never as critical
    roster = rosters.get(line, set())
    covered = [a for a in roster if AJ.names_arm(job_name, a, roster)]
    if "h2_pair" in job_name:
        covered = sorted(set(covered) | (AJ.H2_PAIR & roster))
    if "_sweep_t" in job_name:
        covered = sorted(roster)
    if not covered:
        return 3, []
    best = min(tiers.get((line, a), (3, 0, 0))[0] for a in covered)
    return best, [(line, a) for a in covered]


def balance_targets(deficits: dict, total_cores: int, per_line_cores: dict) -> dict:
    """{line: (target_cores, held_cores, starved)} — the DEFICIT-PROPORTIONAL allocation.

    ⭐⭐⭐ THE SCHEDULING RESULT THAT MAKES THIS THE RIGHT ANSWER, AND IT IS NOT INTUITIVE.
    The reported result is a MINIMUM over lines, so it rises only when the LAST binding line arrives.
    For a min-over-lines objective at fixed total capacity, the makespan is minimised when every
    binding line FINISHES AT THE SAME TIME — which means cores must be allocated in proportion to
    each line's REMAINING DEFICIT. Concentrating capacity on one line is therefore not merely
    suboptimal, it is the WORST available allocation: it finishes a line that was never the
    constraint while the actual constraint sits idle.

    ⚠ MEASURED 2026-08-06, AND IT IS WHY THIS FUNCTION EXISTS. Tamer asked why work was sequential.
    It was: kimi held **81 of 98 running jobs = 648 cores = 83% of the fleet** while deepseek (165
    queued), glm (157), nemotron (248) and haiku (1) held **ZERO RUNNING JOBS between them**. Kimi
    owed the LEAST toward rung 100 (254 trainings) and the three starved lines owed the MOST (350
    each). At 648 cores kimi clears its 254 in 3.7 h and then climbs PAST the common rung while the
    lines that actually gate it have not started.

    The cause is the same accidental ordering as the floor defect: kimi's jobs carry the oldest
    submission time (08/04 22:52), so accrued waiting time hands them every freed slot.
    """
    binding = {ln: d for ln, d in deficits.items() if d > 0}
    tot_def = sum(binding.values())
    out: dict = {}
    for ln, d in binding.items():
        target = int(round(total_cores * d / tot_def)) if tot_def else 0
        have = per_line_cores.get(ln, 0)
        out[ln] = (target, have, have < 0.5 * target)
    return out


def balance_hold_plan(jobs: list[dict], tag_to_line: dict, targets: dict, run_cores: dict,
                      deficits: dict, *, depth_factor: int = DEPTH_FACTOR,
                      depth_floor: int = DEPTH_FLOOR) -> dict:
    """Hold the OVER-SERVED lines' pending jobs so freed slots go to the STARVED binding lines.

    ⚠ THE MECHANISM IS INDIRECT AND THAT IS WHY IT IS SAFE. It does NOT touch a running job, so it
    frees nothing immediately: kimi's 82 running jobs run to completion. What it changes is where
    each slot goes WHEN it frees. Today accrued waiting time hands it straight back to kimi, because
    kimi's queued jobs carry the oldest submission time. With those queued jobs held, the next
    eligible job belongs to a starved binding line instead. Over roughly one job-duration (~9.4 h)
    the fleet re-shapes itself onto the lines that actually gate the common rung.

    A line is OVER-SERVED at more than 1.5x its deficit-proportional target, and a line owing ZERO
    toward the target rung is over-served at ANY core count — it cannot advance the result at all.
    """
    running = [j for j in jobs if j["state"].strip() == "r"]
    pending = [j for j in jobs if j["state"].strip() == "qw"]
    over: set = set()
    for ln, c in run_cores.items():
        if deficits.get(ln, 0) <= 0:
            over.add(ln)                                   # owes nothing: any core is misallocated
        else:
            t = targets.get(ln, (0, 0, False))[0]
            if t and c > 1.5 * t:
                over.add(ln)
    cand = [j for j in pending if tag_to_line.get(j["name"].split("_", 1)[0]) in over]
    cand.sort(key=lambda j: -j["prior"])                   # the ones actually winning slots first
    min_elig = max(depth_factor * len(running), depth_floor)
    max_hold = max(0, len(pending) - min_elig)
    hold = cand[:max_hold]
    return {"over_served": sorted(over), "candidates": len(cand), "hold": hold,
            "min_eligible": min_elig, "eligible_after": len(pending) - len(hold),
            "running": len(running), "pending": len(pending),
            "truncated": len(hold) < len(cand)}


# ---------------------------------------------------------------------------------------------
# ⭐⭐⭐ THE RUNG-DISTANCE TERM — the dimension the V0..V3 model above is STRUCTURALLY BLIND TO
# ---------------------------------------------------------------------------------------------
# **THE DEFECT THIS EXISTS TO CLOSE, measured 2026-08-06 (RUN 25), three independent routes.**
#
# `job_tier` scores a job by the best tier of any arm it COVERS, and for a `_sweep_t<k>` job it sets
# `covered = sorted(roster)` — EVERY arm on the line. So `leg10_..._sweep_t1` and
# `leg10_..._sweep_t6` receive the **IDENTICAL** tier. The value model cannot tell apart the block
# that lifts a line's banked rung from the block that cannot count for another five blocks.
# That blindness is not academic:
#
#   * LIVE CENSUS (111 running jobs / 888 cores): `c1` floor 64 cores, kimi t1 120 cores, and
#     **704 cores (79.3%) on blocks ABOVE their own line's next-needed block** — records that
#     cannot raise ANY banked rung when they land. qwen3.6 had NINE running jobs and **zero** on
#     t2, the only block that can lift it off rung 100.
#   * ARCHIVE (16,791 sealed-test records): kimi holds six DISCONNECTED seed blocks
#     (0-48, 100-120, 189-212, 279-301, 340-354, 403-417) and banks rung **30**. 2,328 records
#     (13.9%) sit above their own arm's next rung boundary.
#   * QUEUE: every line's six blocks were submitted inside a 3-5 MINUTE window, and on glm, kimi
#     and deepseek a HIGH block carries a LOWER job id than t1 (glm t5=91245 vs t1=91250).
#
# **ROOT CAUSE, read from the source rather than inferred.** Two mechanisms were meant to make the
# ladder climb in order and NEITHER operates. (1) `campaign.PRIORITY_RUNG_BASE = 0` — the `-p`
# ladder was retired 2026-07-31, CORRECTLY: `-p` is a GLOBAL POSIX priority weighted 4.0, so it sank
# us beneath every other user instead of ordering our own work. That retirement must never be
# undone. (2) Its stated replacement, `campaign.py:2006-2007` — *"blocks are submitted in rung order
# and weight_waiting_time = 1.0, so the earlier block outranks the later one on age alone"* — is
# structurally false: twelve lines below, `campaign.py:2016` submits all six blocks CONCURRENTLY
# through a `ThreadPoolExecutor`, so there is no meaningful age difference to order them by.
# **A half-applied amendment — the same failure mode the comment block itself names for R106.**
#
# ⇒ So the ordering must be restored where it still CAN be: in what we allow to be ELIGIBLE.
# This term is deliberately NOT a priority change. It never touches `-p`, never touches a running
# job, and frees nothing immediately. It only changes WHICH job takes the next freed slot.
_SWEEP_TIER = re.compile(r"_sweep_t(\d+)")


def job_sweep_tier(job_name: str) -> int | None:
    """The assurance-BLOCK index a `_sweep_t<k>` job carries, or None if the job is not a sweep.

    Returns None for floor/round jobs (`c1_tpe_test_p01`, `..._h2_pair_test_...`) and for probes.
    None means "this term has no opinion", and a job this term has no opinion about is NEVER held
    by it — the floor work must be untouchable by an ordering heuristic.
    """
    m = _SWEEP_TIER.search(job_name)
    return int(m.group(1)) if m else None


def line_needed_block(scan: dict, rungs: list) -> dict:
    """{line: the assurance-BLOCK index that must complete for that line to bank its NEXT rung}.

    The blocks are `src.utils.seeds.seed_tiers`' partition and the naming is `sweep_t<i>` for
    `enumerate(tiers[1:], start=1)`, so block `i` spans `[rungs[i-1], rungs[i])` and completing it
    banks `rungs[i]`. Therefore the needed block index is simply the INDEX of the line's next rung
    in the sorted ladder: banked 30 -> next 100 -> index 1 -> `sweep_t1` (seeds 30-99). Verified
    against the live archive for all three distinct cases on 2026-08-06 — kimi 30->t1,
    qwen3.6 100->t2, haiku 189->t3 (and haiku's queued repair is indeed named `sweep_t3_r1`).

    A line already at the ceiling gets `len(rungs)`, which no block index can reach, so every one
    of its jobs scores the maximum distance. That is correct: it owes nothing.
    """
    srt = sorted(rungs)
    per_line: dict[str, int] = {}
    for (line, arm), d in scan.items():
        b = S15.banked_rung(d["seeds"], srt)
        per_line[line] = b if line not in per_line else min(per_line[line], b)
    out: dict[str, int] = {}
    for line, b in per_line.items():
        nxt = next((r for r in srt if r > b), None)
        out[line] = len(srt) if nxt is None else srt.index(nxt)
    return out


def rung_distance(job_name: str, tag_to_line: dict, needed: dict) -> int | None:
    """How many assurance blocks ABOVE its own line's next-needed block this job sits.

    ``0``  it fills the block that LIFTS the line's banked rung -> it converts into result today.
    ``k>0`` it cannot lift ANY rung until `k` lower blocks complete first -> deferred value.
    ``None`` not a sweep job, or an unknown line: this term declines to score it, and a job it
    declines to score is never held by it.

    Clamped at 0 below: a block BELOW the needed one is already complete for the line minimum, so
    a stray job there is a repair, not a demotion candidate.
    """
    k = job_sweep_tier(job_name)
    if k is None:
        return None
    line = tag_to_line.get(job_name.split("_", 1)[0])
    if line is None:
        return None
    n = needed.get(line)
    if n is None:
        return None
    return max(0, k - n)


def allocative_efficiency(jobs: list[dict], tag_to_line: dict, needed: dict,
                          slots_per_job: int = 8) -> dict:
    """What share of the RUNNING fleet is producing a record that can raise a banked rung TODAY.

    This is the number Tamer asked for on 2026-08-06: *"I dont need a higher number if there is no
    use to it and it doesnt speed up the eta and doesnt contribute to the records."* A core is
    counted USEFUL iff its job sits at rung-distance 0, or is a floor/round job this term declines
    to score (those are `c1`'s pair rounds, which are the binding work by definition).
    """
    useful = deferred = 0
    by_dist: dict[int, int] = {}
    for j in jobs:
        if j["state"].strip() != "r":
            continue
        d = rung_distance(j["name"], tag_to_line, needed)
        if d is None or d == 0:
            useful += slots_per_job
        else:
            deferred += slots_per_job
        by_dist[-1 if d is None else d] = by_dist.get(-1 if d is None else d, 0) + slots_per_job
    tot = useful + deferred
    return {"useful_cores": useful, "deferred_cores": deferred, "total_cores": tot,
            "efficiency": (useful / tot) if tot else 0.0, "by_distance": by_dist}


def tier_value_hold_plan(jobs: list[dict], tag_to_line: dict, needed: dict, *,
                         depth_factor: int = DEPTH_FACTOR,
                         depth_floor: int = DEPTH_FLOOR) -> dict:
    """Hold the pending jobs FURTHEST above their own line's next-needed block, worst first.

    ⚠ THE THREE PROPERTIES THAT MAKE THIS SAFE, each expressed as code rather than as a promise:
      1. **Only `qw` jobs are candidates.** A running job is never considered (invariant 2).
      2. **Distance 0 and `None` are never held.** The block that lifts a rung, and every floor or
         round job, stay eligible whatever else happens.
      3. **The depth guard binds first.** We hold at most `pending - max(4 x running, 200)`, so the
         eligible queue can never be thinned below the burst-absorption floor. M5 measured what
         happens when it is: holding 228 of 309 left 80 eligible and our running count decayed
         44 -> 9. The guard is what keeps this the opposite of that experiment.

    Within the candidate set the sort is `(-distance, -prior)`: the furthest-from-useful first,
    and inside a distance bucket the ones with the HIGHEST priority — because those are precisely
    the jobs that would otherwise take the next freed slot.
    """
    running = [j for j in jobs if j["state"].strip() == "r"]
    pending = [j for j in jobs if j["state"].strip() == "qw"]
    scored = []
    for j in pending:
        d = rung_distance(j["name"], tag_to_line, needed)
        if d is None or d <= 0:
            continue
        scored.append((d, j))
    scored.sort(key=lambda t: (-t[0], -t[1]["prior"]))
    min_elig = max(depth_factor * len(running), depth_floor)
    max_hold = max(0, len(pending) - min_elig)
    hold = [j for _, j in scored[:max_hold]]
    dist_hist: dict[int, int] = {}
    for d, _ in scored:
        dist_hist[d] = dist_hist.get(d, 0) + 1
    return {"hold": hold, "candidates": len(scored), "distance_histogram": dist_hist,
            "min_eligible": min_elig, "eligible_after": len(pending) - len(hold),
            "running": len(running), "pending": len(pending),
            "truncated": len(hold) < len(scored)}


def build_plan(jobs: list[dict], tier_of: dict, *, promote_max_tier: int = PROMOTE_MAX_TIER,
               depth_factor: int = DEPTH_FACTOR, depth_floor: int = DEPTH_FLOOR) -> dict:
    """The minimal, depth-respecting hold set that puts promoted work at the front of OUR queue.

    `tier_of` maps job id -> tier. Only `qw` jobs are eligible for holding; a running job is not
    even considered, which is invariant 2 expressed as code rather than as a comment.
    """
    running = [j for j in jobs if j["state"].strip() == "r"]
    pending = [j for j in jobs if j["state"].strip() == "qw"]

    promote = [j for j in pending if tier_of.get(j["jid"], 3) <= promote_max_tier]
    others = [j for j in pending if tier_of.get(j["jid"], 3) > promote_max_tier]

    min_eligible = max(depth_factor * len(running), depth_floor)
    plan = {"running": len(running), "pending": len(pending), "promote": promote,
            "min_eligible": min_eligible, "hold": [], "truncated": False,
            "blockers_total": 0}
    if not promote:
        return plan

    # a "blocker" is a non-promoted pending job that currently outranks the WEAKEST promoted job:
    # those, and only those, are what the scheduler tries before it reaches the work that matters.
    target = min(j["prior"] for j in promote)
    blockers = sorted([j for j in others if j["prior"] > target],
                      key=lambda j: -j["prior"])       # hold the ones actually in front FIRST
    plan["blockers_total"] = len(blockers)

    max_holdable = max(0, len(pending) - min_eligible)
    hold = blockers[:max_holdable]
    plan["hold"] = hold
    plan["truncated"] = len(hold) < len(blockers)
    return plan


# ---------------------------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------------------------
def _chunks(seq, n=40):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def deep_report(scan: dict, rungs: list, queued_by_tag: dict, tag_to_line: dict,
                cores: int, days_left: float, hours_per_training: float = 9.4) -> dict:
    """THE DEEP ANALYSIS: what each rung costs, what each line owes, and what is being WASTED.

    Answers the question that decides every ranking decision and that no other instrument computes:
    **under R101 the reported result is the COMMON rung, so a record that never completes a rung is
    worth zero — which of our queued trainings are producing those?**
    """
    cur, nxt = common_rung(scan, rungs)
    line2tag = {v: k for k, v in tag_to_line.items()}
    print("=== DEEP JOB ANALYSIS — value measured against the REPORTED result (R101 common rung) ===")
    print("COMMON RUNG = %d   NEXT COMMON RUNG = %d   ladder = %s" % (cur, nxt, rungs))

    print("\n--- WHAT EACH COMMON RUNG COSTS (trainings still owed, over EVERY registered arm) ---")
    costs = {}
    for r in sorted(rungs):
        if r <= cur:
            continue
        costs[r] = sum(sum(1 for s in range(r) if s not in d["seeds"]) for d in scan.values())
        print("  common rung %3d  needs %6d more trainings" % (r, costs[r]))

    rate = cores / hours_per_training                      # trainings per hour
    cap = rate * 24.0 * days_left
    print("\n--- CAPACITY AGAINST THE EXOGENOUS STOP ---")
    print("  %d cores / %.1f h per training = %.1f trainings/h = %.0f/day" % (
        cores, hours_per_training, rate, rate * 24))
    print("  %.1f days left => capacity ~%.0f trainings" % (days_left, cap))
    reach = [r for r, c in costs.items() if c <= cap]
    print("  => HIGHEST common rung the remaining capacity can pay for: %s" % (
        max(reach) if reach else "NONE above %d" % cur))
    print("     (a ceiling, not a forecast: it assumes every training goes to a BINDING line)")

    print("\n--- PER LINE: what it owes for the next common rung, against what it has QUEUED ---")
    print("  %-26s %-6s %7s %10s %9s %8s  %s" % (
        "line", "tag", "banked", "owes->%d" % nxt, "QUEUED", "ratio", "verdict"))
    defs_ = line_deficits(scan, nxt)
    per_line_banked: dict[str, int] = {}
    for (line, arm), d in scan.items():
        b = S15.banked_rung(d["seeds"], rungs)
        per_line_banked[line] = min(per_line_banked.get(line, 10 ** 9), b)
    waste = 0
    rows = []
    for line in sorted(defs_):
        tag = line2tag.get(line, "?")
        owed = defs_[line]
        qd = queued_by_tag.get(tag, 0) * 8
        if owed == 0:
            verdict = "ZERO marginal value (already at/above the next common rung)"
            waste += qd
            ratio = "inf" if qd else "-"
        elif qd > owed:
            verdict = "OVER-PROVISIONED by %d trainings" % (qd - owed)
            waste += qd - owed
            ratio = "%.1fx" % (qd / owed)
        elif qd == 0:
            verdict = "UNDER-PROVISIONED: owes %d and has NOTHING queued" % owed
            ratio = "0.0x"
        else:
            verdict = "under-provisioned (%.0f%% covered)" % (100.0 * qd / owed)
            ratio = "%.1fx" % (qd / owed)
        rows.append((owed, line, tag, per_line_banked[line], qd, ratio, verdict))
    for owed, line, tag, b, qd, ratio, verdict in sorted(rows, key=lambda r: -r[0]):
        print("  %-26s %-6s %7d %10d %9d %8s  %s" % (line, tag, b, owed, qd, ratio, verdict))

    tot_owed = sum(defs_.values())
    tot_q = sum(queued_by_tag.values()) * 8
    print("\n  trainings needed for common rung %d : %d" % (nxt, tot_owed))
    print("  trainings currently QUEUED          : %d" % tot_q)
    print("  ⇒ QUEUED WORK THAT CANNOT RAISE THE REPORTED RESULT AT THIS RUNG: %d trainings"
          % waste)
    print("    (%.0f%% of everything queued. It is not WRONG work -- it is the ladder, and R101"
          % (100.0 * waste / max(1, tot_q)))
    print("     licenses it -- but under Tamer's floor-first priority it is strictly OPTIONAL,")
    print("     and it is what the ranking below deprioritises.)")

    print("\n--- ⭐ THE CRITICAL PATH, and it is the opposite of what it looks like ---")
    crit = sorted(((o, ln) for ln, o in defs_.items() if o > 0), reverse=True)
    if not crit:
        print("  every line is at or above the next common rung -- nothing is binding.")
    else:
        print("  The reported result is a MINIMUM, so it rises only when the LAST line arrives.")
        print("  The makespan is therefore set by the LARGEST deficit, and cores are worth most")
        print("  there -- finishing a cheap laggard first feels like progress and moves the")
        print("  reported result by NOTHING.  Ranked by what actually gates the result:")
        for i, (o, line_name) in enumerate(crit, 1):
            eta = o * hours_per_training / max(1.0, rate)
            print("    %d. %-26s owes %5d trainings  (%.1f h if it had the WHOLE fleet)"
                  % (i, line_name, o, eta))
    return {"common": cur, "next": nxt, "costs": costs, "deficits": defs_,
            "waste": waste, "queued": tot_q, "capacity": cap}


def report(host: str = "myriad", *, promote_max_tier: int = PROMOTE_MAX_TIER) -> int:
    try:
        rungs = S15.registered_rungs()
    except Exception as exc:                                    # noqa: BLE001
        print("COULD NOT READ THE REGISTERED LADDER: %s" % exc)
        return 2                                                # undecidable, never a finding
    scan = S15.scan(str(ROOT))
    if not scan:
        print("COULD NOT READ THE ARCHIVE at %s" % ROOT)
        return 2

    raw, status = _ssh("qstat -u ucestes -xml", host)
    if status != "OK":
        print("qstat status: %s  -> UNDECIDABLE, no plan emitted" % status)
        return 2
    jobs, pstat = parse_jobs_xml(raw)
    if pstat != "OK":
        print("qstat parse: %s  -> UNDECIDABLE, no plan emitted" % pstat)
        return 2

    tag_to_line = {tag: line for line, tag in AJ.batch_tag_map(ROOT).items()}
    rosters = {line: AJ.registered_arms(ROOT, line) for line in {ln for ln, _ in scan}}
    tiers = arm_tiers(scan, rungs)
    floor = min(rungs)

    qbt: dict[str, int] = {}
    for j in jobs:
        if j["state"].strip() in ("qw", "hqw"):
            qbt[j["name"].split("_", 1)[0]] = qbt.get(j["name"].split("_", 1)[0], 0) + 1
    live_cores = 8 * sum(1 for j in jobs if j["state"].strip() == "r")
    deep_report(scan, rungs, qbt, tag_to_line, live_cores or 8, days_left=days_to_stop())
    print()

    print("=== JOB RANK GOVERNOR — floor-first value ranking of OUR pending queue ===")
    print("registered ladder: %s   FLOOR RUNG = %d" % (rungs, floor))
    print("jobs seen: %d   (states: %s)" % (
        len(jobs), ", ".join("%s=%d" % (s, sum(1 for j in jobs if j["state"].strip() == s))
                             for s in sorted({j["state"].strip() for j in jobs}))))

    print("\n--- ARMS PINNING THE COMMON RUNG (tier V0: banked < %d) ---" % floor)
    v0 = sorted(k for k, v in tiers.items() if v[0] == 0)
    if not v0:
        print("  NONE — every registered arm banks at or above the floor rung.")
    for line, arm in v0:
        print("  %-28s %-18s banked=%d" % (line, arm, tiers[(line, arm)][1]))

    print("\n--- ARMS DEMOTED BY A HOLE (tier V1: repair lifts the banked rung) ---")
    v1 = sorted(k for k, v in tiers.items() if v[0] == 1)
    if not v1:
        print("  NONE")
    for line, arm in v1:
        t, b, r = tiers[(line, arm)]
        print("  %-28s %-18s banked=%-4d -> %-4d if repaired  (+%d rungs)" % (line, arm, b, r, r - b))

    tier_of, arms_of = {}, {}
    for j in jobs:
        t, cov = job_tier(j["name"], tag_to_line, rosters, tiers)
        tier_of[j["jid"]] = t
        arms_of[j["jid"]] = cov

    print("\n--- OUR PENDING JOBS BY VALUE TIER ---")
    pending = [j for j in jobs if j["state"].strip() == "qw"]
    for t in (0, 1, 2, 3):
        n = sum(1 for j in pending if tier_of[j["jid"]] == t)
        print("  %-22s %4d job(s)" % (TIER_NAME[t], n))

    # ---- THE BALANCER: is the fleet CONCENTRATED on one line while binding lines starve? --------
    cur, nxt_rung = common_rung(scan, rungs)
    after_floor = next((r for r in sorted(rungs) if r > max(cur, min(rungs))), max(rungs))
    line_of_tag = tag_to_line
    run_cores: dict = {}
    for j in jobs:
        if j["state"].strip() == "r":
            ln = line_of_tag.get(j["name"].split("_", 1)[0])
            if ln:
                run_cores[ln] = run_cores.get(ln, 0) + 8
    defs_next = line_deficits(scan, after_floor)
    tg = balance_targets(defs_next, sum(run_cores.values()), run_cores)
    print("\n=== FLEET BALANCE — cores must go to the LARGEST deficit, not the oldest queue ===")
    print("The reported result is a MINIMUM over lines, so it rises only when the LAST binding line")
    print("arrives. At fixed capacity the makespan is minimised when every binding line FINISHES AT")
    print("THE SAME TIME, i.e. cores in proportion to remaining DEFICIT. Concentrating on one line is")
    print("not merely suboptimal -- it is the WORST allocation, finishing a line that was never the")
    print("constraint while the actual constraint sits idle.")
    print("  target rung for this table: %d" % after_floor)
    print("  %-28s %8s %8s %8s  %s" % ("line", "owes", "cores", "target", "verdict"))
    starved = []
    for ln, (target, held_c, is_starved) in sorted(tg.items(), key=lambda kv: -kv[1][0]):
        v = "STARVED" if is_starved else ("over-served" if held_c > 1.5 * target else "balanced")
        if is_starved:
            starved.append(ln)
        print("  %-28s %8d %8d %8d  %s" % (ln, defs_next.get(ln, 0), held_c, target, v))
    if starved:
        print("  ⇒ %d BINDING LINE(S) STARVED: %s" % (len(starved), ", ".join(sorted(starved))))
        print("    These gate the common rung and hold under half their deficit-proportional share.")
        print("    The cause is accrued waiting time, not the cluster: the line holding the fleet")
        print("    simply has the OLDEST submission time, so it wins every freed slot.")
    else:
        print("  ⇒ no binding line is starved; the fleet is reasonably balanced.")

    if starved:
        bp = balance_hold_plan(jobs, line_of_tag, tg, run_cores, defs_next)
        print("\n  --- THE REBALANCE (holds nothing that is running; changes only WHERE the NEXT")
        print("      freed slot goes, so the fleet re-shapes over ~one job duration) ---")
        print("    over-served lines : %s" % ", ".join(bp["over_served"]))
        print("    their pending jobs: %d" % bp["candidates"])
        print("    TO HOLD           : %d" % len(bp["hold"]))
        print("    eligible after    : %d  (guard %d, %.1fx running)"
              % (bp["eligible_after"], bp["min_eligible"],
                 bp["eligible_after"] / max(1, bp["running"])))
        if bp["truncated"]:
            print("    ⚠ truncated by the depth guard: %d left eligible on purpose"
                  % (bp["candidates"] - len(bp["hold"])))
        if bp["hold"]:
            ids = [j["jid"] for j in bp["hold"]]
            JOURNAL.parent.mkdir(parents=True, exist_ok=True)
            JOURNAL.write_text(json.dumps({"held": ids, "promote": [], "mode": "balance",
                                           "min_eligible": bp["min_eligible"]}, indent=1),
                               encoding="utf-8")
            print("    journal: %s (%d ids)" % (JOURNAL.relative_to(REPO), len(ids)))
            print("    ⇒ COMMANDS (this tool executes NOTHING):")
            for ch in _chunks(ids):
                print("       ssh myriad \"qhold %s\"" % " ".join(ch))
            print("    ⇒ RELEASE (bounded at 90 min, and re-check `qstat -s hs` before re-holding):")
            print("       python docs/ops/job_rank_governor.py --release-from %s"
                  % JOURNAL.relative_to(REPO))

    # --- ⭐ ALLOCATIVE EFFICIENCY: is every core producing a record that RAISES a rung? --------- #
    needed = line_needed_block(scan, rungs)
    eff = allocative_efficiency(jobs, line_of_tag, needed)
    print("\n=== ARE THE CORES USEFUL? — rung-distance of the RUNNING fleet ===")
    print("Tamer, 2026-08-06: \"I dont need a higher number if there is no use to it and it doesnt")
    print("speed up the eta and doesnt contribute to the records.\" A core is USEFUL iff its job")
    print("fills the assurance block that LIFTS its line's banked rung. Everything else is deferred:")
    print("real work, but it raises the reported result by ZERO until every block below it lands.")
    print("  %-34s %s" % ("line", "next-needed block"))
    for ln in sorted(needed):
        print("  %-34s t%d" % (ln, needed[ln]))
    print("  cores at distance 0 (USEFUL NOW) : %4d" % eff["useful_cores"])
    print("  cores at distance > 0 (DEFERRED) : %4d" % eff["deferred_cores"])
    print("  ⇒ ALLOCATIVE EFFICIENCY          : %.1f%%  of %d cores"
          % (100.0 * eff["efficiency"], eff["total_cores"]))
    if eff["by_distance"]:
        print("  running cores by distance: %s"
              % ", ".join("%s=%d" % ("floor/round" if k < 0 else "d%d" % k, v)
                          for k, v in sorted(eff["by_distance"].items())))
    tvp = tier_value_hold_plan(jobs, line_of_tag, needed)
    print("\n  --- THE RUNG-ORDER RESTORE (holds nothing running; the floor is never touched) ---")
    print("    ⚠ WHY THIS IS NEEDED: `campaign.PRIORITY_RUNG_BASE = 0` (the -p ladder was retired")
    print("      2026-07-31, correctly) and its stated replacement — submission age — is defeated")
    print("      by `campaign.py:2016`, which submits ALL six blocks concurrently through a")
    print("      ThreadPoolExecutor. So nothing orders the ladder any more. This restores it in the")
    print("      only place still available: which jobs we allow to be ELIGIBLE.")
    print("    pending jobs above their own next block: %d" % tvp["candidates"])
    print("    by distance: %s" % ", ".join("d%d=%d" % kv
                                            for kv in sorted(tvp["distance_histogram"].items())))
    print("    TO HOLD           : %d" % len(tvp["hold"]))
    print("    eligible after    : %d  (guard %d, %.1fx running)"
          % (tvp["eligible_after"], tvp["min_eligible"],
             tvp["eligible_after"] / max(1, tvp["running"])))
    if tvp["truncated"]:
        print("    ⚠ truncated by the depth guard: %d left eligible on purpose (M5: holding 228 of"
              % (tvp["candidates"] - len(tvp["hold"])))
        print("      309 left 80 eligible and our running count decayed 44 -> 9)")
    if tvp["hold"]:
        tids = [j["jid"] for j in tvp["hold"]]
        TIER_JOURNAL.parent.mkdir(parents=True, exist_ok=True)
        TIER_JOURNAL.write_text(json.dumps({"held": tids, "promote": [], "mode": "rung_order",
                                            "min_eligible": tvp["min_eligible"]}, indent=1),
                                encoding="utf-8")
        print("    journal: %s (%d ids)" % (TIER_JOURNAL.relative_to(REPO), len(tids)))
        print("    ⇒ COMMANDS (this tool executes NOTHING):")
        for ch in _chunks(tids):
            print("       ssh myriad \"qhold %s\"" % " ".join(ch))
        print("    ⇒ RELEASE:  python docs/ops/job_rank_governor.py --release-from %s"
              % TIER_JOURNAL.relative_to(REPO))

    plan = build_plan(jobs, tier_of, promote_max_tier=promote_max_tier)
    print("\n--- THE PLAN ---")
    print("  running jobs               : %d" % plan["running"])
    print("  pending jobs               : %d" % plan["pending"])
    print("  promoted (tier <= %d)       : %d" % (promote_max_tier, len(plan["promote"])))
    print("  blockers ahead of them     : %d" % plan["blockers_total"])
    print("  min_eligible (depth guard) : %d   [max(%d x running, %d)]"
          % (plan["min_eligible"], DEPTH_FACTOR, DEPTH_FLOOR))
    print("  TO HOLD                    : %d" % len(plan["hold"]))
    print("  eligible AFTER the hold    : %d  (%.1fx the running job count)"
          % (plan["pending"] - len(plan["hold"]),
             (plan["pending"] - len(plan["hold"])) / max(1, plan["running"])))
    if plan["truncated"]:
        print("  ⚠ TRUNCATED by the depth guard: %d blocker(s) left eligible on purpose."
              % (plan["blockers_total"] - len(plan["hold"])))
    if not plan["promote"]:
        print("\n  NOTHING TO PROMOTE — no pending job serves the floor. No action; this is a")
        print("  legitimate state (it means the floor work is already running or already banked).")
        return 0
    if not plan["hold"]:
        print("\n  NO HOLD NEEDED — the promoted work is already at the front of our eligible set.")
        return 0

    print("\n  promoted jobs, which are what this is FOR:")
    for j in sorted(plan["promote"], key=lambda j: -j["prior"])[:20]:
        print("    %-8s %-34s tier=%d prior=%.5f" % (j["jid"], j["name"][:34],
                                                     tier_of[j["jid"]], j["prior"]))

    held_by_prefix: dict[str, int] = {}
    for j in plan["hold"]:
        held_by_prefix[j["name"].split("_", 1)[0]] = held_by_prefix.get(j["name"].split("_", 1)[0], 0) + 1
    print("\n  hold set by line tag: %s"
          % ", ".join("%s=%d" % kv for kv in sorted(held_by_prefix.items(), key=lambda kv: -kv[1])))

    ids = [j["jid"] for j in plan["hold"]]
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    JOURNAL.write_text(json.dumps(
        {"held": ids, "promote": [j["jid"] for j in plan["promote"]],
         "min_eligible": plan["min_eligible"]}, indent=1), encoding="utf-8")
    print("\n  journal written: %s  (%d ids — release is possible even if this session dies)"
          % (JOURNAL.relative_to(REPO), len(ids)))

    print("\n  ⇒ COMMANDS TO APPLY (this tool executes NOTHING — invariant 4):")
    for ch in _chunks(ids):
        print("     ssh myriad \"qhold %s\"" % " ".join(ch))
    print("\n  ⇒ COMMANDS TO RELEASE (run these the moment the promoted work dispatches,")
    print("    and unconditionally within 90 minutes whatever the outcome):")
    for ch in _chunks(ids):
        print("     ssh myriad \"qrls %s\"" % " ".join(ch))
    return 0


def verify_release(host: str = "myriad") -> int:
    """Assert the hold is GONE, by reading the live queue — never by trusting `qrls`'s exit code.

    ⚠ THIS EXISTS BECAUSE MY OWN RELEASE WATCHER LIED ON 2026-08-06. It ran the `qrls` loop with
    `>/dev/null 2>&1`, saw the ssh exit 0, and logged **"RELEASE COMPLETE"** while **395 jobs were
    still `hqw`**. That is the exact defect class this repository has hit repeatedly: a banner that
    asserts an outcome it never measured (`run_record_layers.sh` printed "ALL SEVEN LAYERS RC=0"
    after executing three).

    ⚠ AND THE OPPOSITE ERROR IS EQUALLY AVAILABLE, WHICH IS WHY THIS REPORTS EVIDENCE RATHER THAN A
    VERDICT ALONE. On the same day I then declared the release BROKEN on the strength of the state
    string, when `qstat -j` showed **no hold field at all**, `ntckts` 0.00000 and `version: 11` —
    i.e. the release HAD applied and only the state/priority display lagged the 10-minute
    `schedule_interval`. **`hqw` in `qstat` is a DISPLAY; the absence of a hold field in `qstat -j`
    is the STATE.** So this checks BOTH and says which it saw.

    Exit 0 only when the queue itself shows zero held jobs.
    """
    ids = []
    if JOURNAL.is_file():
        try:
            ids = json.loads(JOURNAL.read_text(encoding="utf-8")).get("held", [])
        except Exception:                                       # noqa: BLE001
            ids = []
    raw, status = _ssh("qstat -u ucestes", host)
    if status != "OK":
        print("CANNOT VERIFY -- %s. An unread queue is NOT a released one." % status)
        return 2
    held = [ln.split()[0] for ln in raw.splitlines()[2:]
            if len(ln.split()) >= 5 and ln.split()[0].isdigit() and ln.split()[4].startswith("h")]
    print("journalled hold: %d id(s)   still showing a hold state: %d" % (len(ids), len(held)))
    if not held:
        print("RELEASE VERIFIED: zero jobs in a hold state.")
        return 0
    still = sorted(set(held) & set(ids))
    print("NOT YET RELEASED: %d of the journalled ids still display a hold." % len(still))
    if still:
        detail, s2 = _ssh("qstat -j %s 2>/dev/null | egrep -i '^(job_number|version)|hold'"
                          % still[0], host)
        if s2 == "OK":
            print("  sample job %s:" % still[0])
            for ln in detail.splitlines()[:4]:
                print("    %s" % ln.strip())
            print("  ⇒ if NO hold field appears above, the release APPLIED and only the state")
            print("    string lags the 10-minute schedule_interval. Re-check, do NOT re-issue.")
    print("  release commands: python docs/ops/job_rank_governor.py --release-from %s"
          % JOURNAL.relative_to(REPO))
    return 1


def release_from(path: str) -> int:
    try:
        ids = json.loads(Path(path).read_text(encoding="utf-8"))["held"]
    except Exception as exc:                                    # noqa: BLE001
        print("could not read the journal %s: %s" % (path, exc))
        return 2
    print("=== RELEASE PLAN from %s (%d held ids) ===" % (path, len(ids)))
    for ch in _chunks(ids):
        print("  ssh myriad \"qrls %s\"" % " ".join(ch))
    return 0


# ---------------------------------------------------------------------------------------------
# selftest — every case is a MUTATION that must change the answer, so a broken model cannot pass
# ---------------------------------------------------------------------------------------------
def selftest() -> int:
    fails = []

    def ck(name, got, want):
        if got != want:
            fails.append("%s: got %r want %r" % (name, got, want))

    rungs = [30, 100, 189, 568]

    # --- banked-rung / tier model -------------------------------------------------------------
    sc = {
        ("test", "bayes_opt"): {"seeds": set(), "holes": [], "frontier": -1, "n": 0, "started": False},
        ("test", "cma_es"): {"seeds": set(range(30)), "holes": [], "frontier": 29, "n": 30, "started": True},
        # haiku shape: frontier 567 with two holes -> banks 189, would bank 568 repaired
        ("test_leg_h", "scalar"): {"seeds": set(range(568)) - {272, 273}, "holes": [272, 273],
                                   "frontier": 567, "n": 566, "started": True},
        ("test_leg_h", "placebo"): {"seeds": set(range(568)), "holes": [], "frontier": 567,
                                    "n": 568, "started": True},
    }
    t = arm_tiers(sc, rungs)
    ck("V0 for an arm with no records", t[("test", "bayes_opt")][0], 0)
    ck("V0 banked is 0", t[("test", "bayes_opt")][1], 0)
    ck("cma_es at exactly the floor is NOT V0", t[("test", "cma_es")][0] == 0, False)
    ck("holed arm is V1", t[("test_leg_h", "scalar")][0], 1)
    ck("holed arm banks 189", t[("test_leg_h", "scalar")][1], 189)
    ck("holed arm would bank 568", t[("test_leg_h", "scalar")][2], 568)
    ck("complete arm above its line min is V3", t[("test_leg_h", "placebo")][0], 3)
    # THE HOLE-COST BOUND. A MID-CLIMB arm (kimi's real shape: frontier 409, banked 30, 312 holes)
    # must NOT be V1, however large its notional rung gap. Without this the live plan promoted 321
    # of 891 jobs and buried the floor-critical eight.
    mid = {("test_leg_k", "scalar"): {"seeds": set(range(30)) | set(range(350, 410)),
                                      "holes": list(range(30, 350)), "frontier": 409,
                                      "n": 90, "started": True}}
    ck("a mid-climb arm with 320 holes is NOT V1", arm_tiers(mid, rungs)[("test_leg_k", "scalar")][0] != 1, True)
    ck("a mid-climb arm's repaired == banked",
       arm_tiers(mid, rungs)[("test_leg_k", "scalar")][1] == arm_tiers(mid, rungs)[("test_leg_k", "scalar")][2], True)
    # MUTATION: fill the holes and V1 must collapse to V2/V3 — if it does not, the tier is
    # keyed on something other than the repair gap and the model is wrong.
    sc2 = dict(sc)
    sc2[("test_leg_h", "scalar")] = {"seeds": set(range(568)), "holes": [], "frontier": 567,
                                     "n": 568, "started": True}
    ck("repairing the hole removes V1", arm_tiers(sc2, rungs)[("test_leg_h", "scalar")][0] != 1, True)

    # --- job -> tier --------------------------------------------------------------------------
    tag_to_line = {"c1": "test", "leg5": "test_leg_h"}
    rosters = {"test": {"bayes_opt", "cma_es"}, "test_leg_h": {"scalar", "scalar_cvar5", "placebo"}}
    ck("floor-critical job", job_tier("c1_bayes_opt_test_p01", tag_to_line, rosters, t)[0], 0)
    ck("banked-arm job", job_tier("c1_cma_es_test_p01", tag_to_line, rosters, t)[0],
       t[("test", "cma_es")][0])
    ck("unknown tag is never critical", job_tier("zz9_whatever_p01", tag_to_line, rosters, t)[0], 3)
    # the longest-arm rule must hold: a scalar_cvar5 job must NOT be scored as `scalar`
    ck("scalar_cvar5 does not match scalar",
       job_tier("leg5_scalar_cvar5_test_p01", tag_to_line, rosters, t)[1], [("test_leg_h", "scalar_cvar5")])
    # THE SWEEP RULE. A sweep job names no arm and covers the whole roster, so it must inherit the
    # BEST tier on the line. Without this clause it scored V3 and the live plan ignored haiku's
    # +379-rung repair job entirely.
    ck("sweep job covers the whole roster and inherits the best tier",
       job_tier("leg5_leg_haiku_4_5_sweep_t3_r1", tag_to_line, rosters, t)[0], 1)
    ck("sweep job covers all three roster arms",
       len(job_tier("leg5_leg_haiku_4_5_sweep_t3_r1", tag_to_line, rosters, t)[1]), 3)
    # MUTATION: a sweep job on a line whose arms are ALL complete must NOT be promoted — otherwise
    # the clause is promoting on the word "sweep" rather than on measured value.
    t_all_done = arm_tiers({("test_leg_h", a): {"seeds": set(range(568)), "holes": [],
                                                "frontier": 567, "n": 568, "started": True}
                            for a in ("scalar", "scalar_cvar5", "placebo")}, rungs)
    ck("sweep on a fully-banked line is NOT promoted",
       job_tier("leg5_leg_haiku_4_5_sweep_t3_r1", tag_to_line, rosters, t_all_done)[0] <= 1, False)

    # --- THE BALANCER: cores in proportion to DEFICIT, so binding lines finish together --------
    # The live 2026-08-06 shape that prompted it: kimi 648 cores owing 254, three lines owing 350
    # each with ZERO cores. The optimum for a min-over-lines objective is deficit-proportional.
    defs_ = {"kimi": 254, "deepseek": 350, "glm": 350, "nemotron": 350, "done": 0}
    have = {"kimi": 648, "deepseek": 0, "glm": 0, "nemotron": 0, "done": 72}
    tg = balance_targets(defs_, 784, have)
    ck("a line owing nothing gets NO target at all", "done" in tg, False)
    ck("targets are deficit-proportional: 350/1304 of 784", tg["deepseek"][0], 210)
    ck("the smallest deficit gets the smallest target", tg["kimi"][0], 153)
    ck("targets sum to about the total capacity", sum(v[0] for v in tg.values()) in (783, 784, 785), True)
    # ⭐ THE STARVATION FLAGS ARE THE ACTIONABLE OUTPUT
    ck("a line at ZERO against a 210 target is STARVED", tg["deepseek"][2], True)
    ck("kimi at 648 against a 153 target is NOT starved", tg["kimi"][2], False)
    ck("starved lines are exactly the three at zero",
       sorted(k for k, v in tg.items() if v[2]), ["deepseek", "glm", "nemotron"])
    # a line at HALF its target is on the boundary and must NOT be called starved
    ck("a line at exactly half its target is not starved",
       balance_targets({"a": 100}, 100, {"a": 50})["a"][2], False)
    ck("an empty deficit set cannot divide by zero", balance_targets({}, 784, {}), {})

    # --- the plan, and its invariants ---------------------------------------------------------
    jobs = ([{"jid": "1", "name": "c1_bayes_opt_test_p01", "state": "qw", "prior": 2.001}]
            + [{"jid": str(100 + i), "name": "leg10_x_sweep_p01", "state": "qw", "prior": 2.010 + i * 1e-5}
               for i in range(500)]
            + [{"jid": str(900 + i), "name": "leg10_x_sweep_p01", "state": "r", "prior": 2.0}
               for i in range(10)])
    tier_of = {"1": 0}
    tier_of.update({str(100 + i): 3 for i in range(500)})
    tier_of.update({str(900 + i): 3 for i in range(10)})
    p = build_plan(jobs, tier_of, depth_factor=4, depth_floor=200)
    ck("running counted", p["running"], 10)
    ck("pending counted", p["pending"], 501)
    ck("one promoted", len(p["promote"]), 1)
    ck("all 500 are blockers", p["blockers_total"], 500)
    ck("min_eligible is the floor here", p["min_eligible"], 200)
    ck("hold truncated to respect depth", len(p["hold"]), 301)
    ck("plan reports truncation", p["truncated"], True)
    ck("eligible after >= min_eligible", p["pending"] - len(p["hold"]) >= p["min_eligible"], True)
    ck("no RUNNING job is ever held", any(j["state"] == "r" for j in p["hold"]), False)
    ck("no promoted job is ever held", any(j["jid"] == "1" for j in p["hold"]), False)
    ck("highest-priority blockers held first",
       p["hold"][0]["prior"] > p["hold"][-1]["prior"], True)
    # MUTATION: raise the depth floor above what is holdable and the plan must empty, not overrun.
    p2 = build_plan(jobs, tier_of, depth_factor=4, depth_floor=5000)
    ck("an impossible depth guard yields an EMPTY hold", len(p2["hold"]), 0)
    # MUTATION: if the promoted job already outranks everything, no hold is needed at all.
    jobs3 = [dict(j) for j in jobs]
    jobs3[0]["prior"] = 9.0
    ck("already-front promoted work needs no hold", len(build_plan(jobs3, tier_of)["hold"]), 0)

    # --- days_to_stop: the case that catches a hardcoded constant ------------------------------
    # The original was `max(0.0, (date(2026,8,27) - date(2026,8,6)).days)` — a hardcoded 21 wearing
    # an arithmetic disguise. The SECOND assertion below is the one that matters: it fails against
    # any implementation that ignores its argument, which is exactly what the defect did.
    ck("days_to_stop on the day it was written", days_to_stop(_dt.date(2026, 8, 6)), 21.0)
    ck("days_to_stop LATER (kills a hardcoded 21)", days_to_stop(_dt.date(2026, 8, 26)), 1.0)
    ck("days_to_stop on the stop date", days_to_stop(_dt.date(2026, 8, 27)), 0.0)
    ck("days_to_stop never goes negative", days_to_stop(_dt.date(2026, 9, 10)), 0.0)

    # --- parser ------------------------------------------------------------------------------
    xml = ("<job_info><queue_info>"
           "<job_list state='running'><JB_job_number>7</JB_job_number>"
           "<JB_name>c1_x</JB_name><state>r</state><JAT_prio>2.5</JAT_prio></job_list>"
           "</queue_info></job_info>")
    js, st = parse_jobs_xml(xml)
    ck("parser status", st, "OK")
    ck("parser jid", js[0]["jid"], "7")
    ck("parser prior", js[0]["prior"], 2.5)
    ck("empty input is undecidable", parse_jobs_xml("")[1].startswith("EMPTY-OUTPUT"), True)
    ck("bad xml is undecidable", parse_jobs_xml("<not xml")[1].startswith("UNPARSEABLE"), True)

    # --- THE RUNG-DISTANCE TERM (RUN 25) ------------------------------------------------------
    # Every case below is a DISCRIMINATOR: it reads one way with the term and the opposite way
    # without it. The pre-fix model scored `sweep_t1` and `sweep_t6` on the same line IDENTICALLY,
    # so cases R2/R3/R6/R7 all fail against it. That is the point — a test that cannot fail
    # against the pre-fix behaviour verifies nothing.
    LR = [30, 100, 189, 279, 340, 403, 568]
    ck("R0 a non-sweep job has no block index", job_sweep_tier("c1_tpe_test_p01"), None)
    ck("R0b a sweep job's block index is parsed", job_sweep_tier("leg10_leg_kimi_k3_sweep_t6_p15"), 6)
    ck("R0c the repair suffix does not break the parse",
       job_sweep_tier("leg5_leg_haiku_4_5_sweep_t3_r1"), 3)

    # THE THREE LIVE SHAPES, 2026-08-06. Each maps a banked rung to the block that lifts it.
    nsc = {
        ("test_leg_kimi_k3", "scalar"): {"seeds": set(range(49)), "holes": [], "frontier": 48,
                                         "n": 49, "started": True},
        ("test_leg_qwen3_6_27b", "scalar"): {"seeds": set(range(120)), "holes": [], "frontier": 119,
                                             "n": 120, "started": True},
        ("test_leg_haiku_4_5", "scalar"): {"seeds": set(range(568)) - {272, 273},
                                           "holes": [272, 273], "frontier": 567, "n": 566,
                                           "started": True},
    }
    nb = line_needed_block(nsc, LR)
    ck("R1a kimi banks 30 so it needs block t1 (seeds 30-99)", nb["test_leg_kimi_k3"], 1)
    ck("R1b qwen3.6 banks 100 so it needs block t2 (seeds 100-188)", nb["test_leg_qwen3_6_27b"], 2)
    ck("R1c haiku banks 189 so it needs block t3 — and its queued repair IS sweep_t3_r1",
       nb["test_leg_haiku_4_5"], 3)

    t2l = {"leg10": "test_leg_kimi_k3", "leg3": "test_leg_qwen3_6_27b", "leg5": "test_leg_haiku_4_5"}
    ck("R2 kimi t1 is distance 0 — it lifts the rung",
       rung_distance("leg10_leg_kimi_k3_sweep_t1_p01", t2l, nb), 0)
    ck("R3 kimi t6 is distance 5 — it lifts NOTHING until five blocks below it land",
       rung_distance("leg10_leg_kimi_k3_sweep_t6_p01", t2l, nb), 5)
    ck("R4 qwen3.6 t6 is distance 4 (its needed block is t2, not t1)",
       rung_distance("leg3_leg_qwen3_6_27b_sweep_t6_p01", t2l, nb), 4)
    ck("R5 haiku's repair is distance 0",
       rung_distance("leg5_leg_haiku_4_5_sweep_t3_r1", t2l, nb), 0)
    ck("R5b a FLOOR job is scored None, so this term can never demote c1",
       rung_distance("c1_tpe_test_p01", t2l, nb), None)
    ck("R5c an unknown tag is scored None, never held",
       rung_distance("zz9_leg_x_sweep_t6_p01", t2l, nb), None)

    def _j(jid, name, state, prior):
        return {"jid": jid, "name": name, "state": state, "prior": prior}

    # 12 pending: 2 useful (t1), 1 floor, 9 deferred (t6). Depth floor 200 must BLOCK every hold.
    jobs = ([_j("1", "leg10_leg_kimi_k3_sweep_t1_p01", "qw", 2.01),
             _j("2", "leg10_leg_kimi_k3_sweep_t1_p02", "qw", 2.01),
             _j("3", "c1_tpe_test_p01", "qw", 2.00)]
            + [_j(str(10 + i), "leg10_leg_kimi_k3_sweep_t6_p%02d" % i, "qw", 2.02)
               for i in range(9)]
            + [_j("99", "leg10_leg_kimi_k3_sweep_t6_p99", "r", 2.03)])
    p_guarded = tier_value_hold_plan(jobs, t2l, nb)
    ck("R6 the DEPTH GUARD binds first — nothing is held when the queue is shallow",
       len(p_guarded["hold"]), 0)
    ck("R6b and it says so rather than reporting a clean plan", p_guarded["truncated"], True)
    p = tier_value_hold_plan(jobs, t2l, nb, depth_factor=0, depth_floor=3)
    held = {j["name"] for j in p["hold"]}
    ck("R7 with room, exactly the 9 deferred jobs are held", len(held), 9)
    ck("R7b the block that LIFTS the rung is never held",
       any("_sweep_t1_" in n for n in held), False)
    ck("R7c the FLOOR job is never held", any(n.startswith("c1_") for n in held), False)
    ck("R7d the RUNNING job is never held", "leg10_leg_kimi_k3_sweep_t6_p99" not in held, True)
    ck("R7e the distance histogram is reported, not just the count",
       p["distance_histogram"], {5: 9})

    eff = allocative_efficiency(jobs, t2l, nb)
    ck("R8 one running t6 job scores 0% allocative efficiency", eff["efficiency"], 0.0)
    ck("R8b and it is counted in cores, not jobs", eff["total_cores"], 8)
    eff2 = allocative_efficiency(jobs + [_j("100", "c1_tpe_test_p02", "r", 2.0)], t2l, nb)
    ck("R8c adding one FLOOR job takes it to 50% — floor work counts as useful",
       round(eff2["efficiency"], 3), 0.5)

    if fails:
        print("SELFTEST FAILED (%d)" % len(fails))
        for f in fails:
            print("  " + f)
        return 1
    print("SELFTEST OK — 46 + 22 assertions incl. 8 mutation controls, the 8 rung-distance "
          "discriminators, and 2 undecidable-input cases")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default="myriad")
    ap.add_argument("--promote-max-tier", type=int, default=PROMOTE_MAX_TIER,
                    choices=(0, 1, 2),
                    help="0 = floor-critical only (default, Tamer's floor-first priority); "
                         "1 additionally promotes cheap hole repairs; 2 adds line minima.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--release-from", metavar="JOURNAL")
    ap.add_argument("--verify-release", action="store_true",
                    help="assert the hold is GONE by reading the live queue, never from qrls rc")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.verify_release:
        return verify_release(a.host)
    if a.release_from:
        return release_from(a.release_from)
    return report(a.host, promote_max_tier=a.promote_max_tier)


if __name__ == "__main__":
    raise SystemExit(main())
