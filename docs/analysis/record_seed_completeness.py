"""S15 - SEED-SET COMPLETENESS: which rung has each arm ACTUALLY banked, and is any hole hiding?

WHY THIS EXISTS (2026-08-03, RUN 17, execution record s.130).

The seven record layers verify that every record is INDIVIDUALLY sound - its contract (R1-R9), its
provenance seal (P1-P4), its science (S1-S10), its fed text (S11), its authored code (S12), its fed
values (S13) and its window/device identity (S14). **Not one of them asks whether the SET of records
an arm holds is COMPLETE.**

That gap has a precise cost. Under R101 the reported result is the COMMON RUNG, and an arm banks the
largest registered rung whose whole seed prefix it possesses. **A single missing seed below the
frontier silently demotes an arm's bankable rung**, and because the common rung is a MINIMUM over
every arm of every line, one demoted arm caps the ENTIRE CAMPAIGN.

IT IS NOT HYPOTHETICAL. On 2026-08-03 `test_leg_gpt_5_6_luna` held 2,832 of 2,840 records with a
frontier at seed 567 - and was missing exactly seeds **192 and 193**. Every per-record layer was
CLEAN, because every record it had was perfect. Its bankable rung was **189, not 568**, and if the
other eleven lines had climbed to 568 the campaign would have reported 189. It was found only
because the line happened to be momentarily job-less and `line_balance` raised STUCK - i.e. **by
luck**. Had it still had jobs running, nothing in the repository would have reported it.

WHAT THIS LAYER ASKS, and no other does:

  C1  Is the seed set a CONTIGUOUS PREFIX 0..n-1, or are there holes below the frontier?
  C2  What is the LARGEST REGISTERED RUNG each arm has actually completed?
  C3  Do all arms of a line agree on that rung (a line banks its own minimum)?
  C4  Are there seeds ABOVE the registered ladder (568), which would mean an unregistered seed ran?
  C5  Are there DUPLICATE seed directories for one arm?
  C6  Is every arm the line is REGISTERED to run actually PRESENT in the minimum? (added 2026-08-03)

**C6 EXISTS BECAUSE C2/C3 WERE COMPUTED OVER THE WRONG POPULATION, AND THE ERROR RAN TOWARD
REASSURANCE (P244).** `scan()` dropped any arm holding zero records (`if not seeds: continue`), so a
line's "minimum over arms" was a minimum over the arms that had STARTED. Measured live on
2026-08-03: `test` (the CONFIRMATORY core line) holds a frozen `distributional-winner` and a frozen
`scalar-winner` and has **no sealed-test directory for either**, yet this file printed
`banked rung 30`. Same for `glm_5_2`, `kimi_k3` and `nemotron_3_super`. All four bank **0**.

The cost was not academic. RUN 18's handover read this table and concluded that deepseek's
`placebo_shuffled` hole was the single thing capping the campaign at rung 0, and that landing one
queued 8-record repair job would lift it. It would not: with that hole filled the common rung is
STILL 0, because four other lines have not begun their two headline arms at all. A session was
pointed at the wrong critical path by an instrument that looked precise.

⚠ **THE ROSTER IS ITSELF A LOWER BOUND, AND THAT IS DISCLOSED RATHER THAN HIDDEN.** It is read from
the `frozen*/` winner directories, so an arm still in C1 that has not frozen yet (core's `bayes_opt` and
`tpe`; `cma_es` froze 2026-08-04 and is now IN the roster) is in NEITHER population and cannot be counted. Every per-line rung
printed here is therefore an UPPER BOUND on what the line banks. It is labelled as one.

THE RUNGS ARE READ FROM THE FROZEN REGISTRATION, never hardcoded - the R84 lesson ("a registered
NAME requires a registered VALUE"), and the reason this file cannot silently drift from the design.

EFFECT-BLIND BY CONSTRUCTION: it reads directory names and counts. It never opens a record, never
touches a metric, and cannot leak a treatment outcome.

FAILS LOUD ON AN EMPTY INPUT SET (exit 2). "Found nothing wrong" and "looked at nothing" are
indistinguishable in a green board - P197/P213.

    python docs/analysis/record_seed_completeness.py
    python docs/analysis/record_seed_completeness.py --verbose
    python docs/analysis/record_seed_completeness.py --selftest

EXIT: 0 every started arm is a contiguous prefix   1 a HOLE exists below some arm's frontier
      2 could not run, or inspected nothing
"""
from __future__ import annotations

import argparse
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_ROOT = os.path.join(REPO, "outputs", "campaign_cluster_run4")
PREREG = os.path.join(REPO, "config", "preregistration.yaml")

_SEED = re.compile(r"-s(\d+)$")


def registered_baselines(path: str = PREREG) -> list:
    """The 11 H1 hand-written reward baselines, READ from the registration.

    They are CONFIRMATORY (node N6, promoted by R108) and climb the ladder under R111, but they
    never receive a `frozen*/<arm>-winner` directory -- so `registered_arms()` structurally cannot
    supply them and the C6 roster has a hole exactly their shape.
    """
    import yaml

    try:
        with open(path, encoding="utf-8") as fh:
            yml = yaml.safe_load(fh) or {}
        names = yml.get("h1_baselines") or []
        return ["baseline_" + str(n) for n in names]
    except Exception:  # noqa: BLE001
        return []


BASELINE_ARMS = registered_baselines()


def registered_rungs(path: str = PREREG) -> list:
    """The frozen assurance-tier ladder, READ from the registration (Amendment E1)."""
    import yaml

    with open(path, encoding="utf-8") as fh:
        yml = yaml.safe_load(fh) or {}
    seeds = yml.get("seeds")
    if isinstance(seeds, dict) and isinstance(seeds.get("tiers"), list):
        tiers = [int(t) for t in seeds["tiers"]]
        # ⚠ An EMPTY list passes the isinstance check and then `max(rungs)` raises ValueError, so
        # the tool died with a traceback and exit 1 -- which reads as "a hole exists", the WRONG
        # verdict. A ladder we cannot read is "could not run" (exit 2), never a finding.
        if not tiers or any(t <= 0 for t in tiers):
            raise KeyError("seeds.tiers is empty or non-positive - refusing to guess the ladder")
        return tiers
    raise KeyError("seeds.tiers absent from the registration - refusing to guess the ladder")


def banked_rung(seeds: set, rungs: list) -> int:
    """The largest registered rung whose ENTIRE seed prefix 0..r-1 is present.

    This is the quantity that actually determines what an arm contributes to the common rung, and
    it is NOT the same as len(seeds) or max(seeds) - which is exactly how a hole hides.
    """
    best = 0
    for r in sorted(rungs):
        if all(s in seeds for s in range(r)):
            best = r
        else:
            break
    return best


def registered_arms(root: str, line: str) -> set:
    """The arms `line` is registered to run, read from its `frozen*/` winner directory.

    A line's sealed-test roster is exactly the set of arms that have a frozen winner: the C4
    precondition is "every arm this line runs has a frozen winner", and the test leg then re-trains
    each winner across the seed ladder. Reading the roster from the archive rather than from a
    hardcoded list means a roster change cannot silently desynchronise this check (the R84 lesson).

    ⚠ RETURNS A LOWER BOUND. An arm still searching in C1 has no winner yet and so is absent here.
    Callers must treat a rung computed from this roster as an UPPER BOUND on the line's true bank.
    """
    fp = os.path.join(root, "frozen" + line[len("test"):])
    if not os.path.isdir(fp):
        return set()
    return {d[: -len("-winner")] for d in os.listdir(fp)
            if d.endswith("-winner") and os.path.isdir(os.path.join(fp, d))}


def scan(root: str) -> dict:
    """{(line, arm): {seeds, holes, frontier, dupes, n, started}} over every sealed-test root.

    ⚠ INCLUDES REGISTERED ARMS THAT HAVE NOT STARTED, with `started=False` and an empty seed set.
    They are the reason C6 exists: an arm with zero records banks rung 0, and dropping it from the
    population turns a line's minimum into a minimum over whatever happened to be running. See the
    module docstring (P244).
    """
    out = {}
    if not os.path.isdir(root):
        return out
    for line in sorted(os.listdir(root)):
        if not line.startswith("test"):
            continue
        lp = os.path.join(root, line)
        if not os.path.isdir(lp):
            continue
        seen = set()
        for arm in sorted(os.listdir(lp)):
            ap = os.path.join(lp, arm)
            if arm.startswith(("_", ".")) or not os.path.isdir(ap):
                continue
            seeds, dupes = set(), 0
            for d in os.listdir(ap):
                m = _SEED.search(d)
                if not m or not os.path.isfile(os.path.join(ap, d, "record.json")):
                    continue
                s = int(m.group(1))
                if s in seeds:
                    dupes += 1
                seeds.add(s)
            seen.add(arm)
            if not seeds:
                # An empty test DIRECTORY is an arm that has been dispatched and has landed
                # nothing yet. It banks 0 exactly like an arm with no directory at all.
                out[(line, arm)] = {"seeds": set(), "holes": [], "frontier": -1,
                                    "dupes": 0, "n": 0, "started": False}
                continue
            frontier = max(seeds)
            holes = sorted(set(range(frontier + 1)) - seeds)
            out[(line, arm)] = {"seeds": seeds, "holes": holes, "frontier": frontier,
                                "dupes": dupes, "n": len(seeds), "started": True}
        for arm in sorted(registered_arms(root, line) - seen):
            out[(line, arm)] = {"seeds": set(), "holes": [], "frontier": -1,
                                "dupes": 0, "n": 0, "started": False}
    return out


def report(root: str, verbose: bool = False) -> int:
    try:
        rungs = registered_rungs()
    except Exception as exc:  # noqa: BLE001
        print("*** cannot read the registered rungs: %r" % (exc,))
        return 2
    data = scan(root)
    started = {k: v for k, v in data.items() if v["started"]}
    unstarted = {k: v for k, v in data.items() if not v["started"]}
    # ⚠ THE VACUITY GUARD KEYS ON *STARTED* ARMS, DELIBERATELY. Since C6 the roster is read from
    # `frozen*/`, so an archive with winners but not one sealed-test record would populate `data`
    # and this guard would pass on an input it had learned nothing from -- the exact P197/P213
    # shape the guard exists to stop.
    if not started:
        print("*** NO started test arms found. This check inspected NOTHING and is VACUOUS.")
        print("    A vacuous pass banks a property that was never tested (P197/P213). Exiting 2.")
        return 2

    top = max(rungs)
    print("=== S15 SEED-SET COMPLETENESS (sealed test) ===")
    print("  registered rungs (READ from config/preregistration.yaml): %s" % rungs)
    print("  (line, arm) STARTED arms inspected                      : %d" % len(started))
    print("  (line, arm) REGISTERED arms holding NO record yet       : %d  <- these bank rung 0"
          % len(unstarted))
    print()

    holed = {k: v for k, v in data.items() if v["holes"]}
    over = {k: sorted(s for s in v["seeds"] if s >= top) for k, v in data.items()
            if any(s >= top for s in v["seeds"])}
    dupes = {k: v["dupes"] for k, v in data.items() if v["dupes"]}

    print("--- C2/C3: the rung each LINE has actually banked (its own MINIMUM over arms) ---")
    print("    the minimum is over REGISTERED arms, NOT over the arms that happen to have started")
    by_line = {}
    for (line, arm), v in data.items():
        by_line.setdefault(line, []).append((arm, banked_rung(v["seeds"], rungs), v["n"],
                                             v["frontier"], len(v["holes"]), v["started"]))
    for line in sorted(by_line, key=lambda x: min(a[1] for a in by_line[x])):
        arms = by_line[line]
        lo = min(a[1] for a in arms)
        # An arm with NO records caps the line at 0 outright, and that outranks any hole as the
        # explanation -- report the binding cause, not the most eye-catching one.
        idle = sorted(a[0] for a in arms if not a[5])
        if idle:
            note = ("   <<< %d registered arm(s) hold NO record: %s -- that is what caps this line"
                    % (len(idle), ", ".join(idle)))
        else:
            # ⚠⚠ P253 -- THIS PICKED THE ARM WITH THE MOST HOLES, WHICH IS NOT THE ARM THAT CAPS.
            # The comment three lines up says "report the binding cause, not the most eye-catching
            # one", and then this branch picked the most eye-catching one: `max(..., key=holes)`.
            # Hole COUNT and hole POSITION are different quantities. An arm with ONE hole at seed 5
            # banks 0 and caps the line; an arm with 200 holes all above rung 403 banks 403 and does
            # not. The first version would have named the second. **That is the P244 failure mode
            # recurring inside the P244 fix** -- a number computed over the wrong population, again,
            # and it would point a session at the wrong repair job, which is the exact harm P244 was
            # written to stop. Found by a read-only auditor, not by me.
            # The cap is an arm whose banked rung EQUALS the line's minimum; among those, the one
            # with the most holes is the most informative to name.
            capping = [a for a in arms if a[1] == lo and a[4]]
            worst = max(capping, key=lambda a: a[4]) if capping else None
            note = ("   <<< %s has %d HOLE(S) below its frontier %d -- that is what caps this line"
                    % (worst[0], worst[4], worst[3])) if worst else ""
        print("  %-30s banked rung %4d  (arms: %s)%s"
              % (line, lo, " ".join("%s=%d" % (a[0][:12], a[1]) for a in arms) if verbose
                 else "%d arms" % len(arms), note))
    common = min(min(a[1] for a in arms) for arms in by_line.values())
    print()
    print("  ==> COMMON RUNG (the MINIMUM over every line -- under R101 this IS the result) = %d"
          % common)
    print("      it is an UPPER BOUND. FOUR channels remove a low-banking unit from the minimum,")
    print("      and every one pushes the printed number UP (auditor, 2026-08-04):")
    print("        1. an arm still in C1 has no frozen winner, so it is in neither population")
    print("        2. a LINE with no test* directory is not enumerated at all -- the line-level")
    print("           twin of the arm-level bug C6 fixed, and the archive is a PULL MIRROR, so")
    print("           'not here yet' is a reachable state")
    print("        3. a line whose frozen* directory is unreadable gets an EMPTY roster, which")
    print("           silently degrades C6 to pre-fix behaviour for that line")
    print("        4. the 11 H1 baselines NEVER get a -winner dir, so they can never enter a")
    print("           roster -- if a baseline test dir were absent it would be invisible")
    print("      The true bank is this number or lower, never higher.")
    # Channels 2 and 3 are made LOUD rather than left as prose: an unannounced empty roster is
    # indistinguishable from a line whose roster is genuinely fully started, and that is exactly
    # the silence C6 exists to remove.
    rosterless = sorted(ln for ln in by_line if not registered_arms(root, ln))
    if rosterless:
        print()
        print("  *** %d LINE(S) HAVE NO READABLE frozen*/ ROSTER: %s"
              % (len(rosterless), ", ".join(rosterless)))
        print("  *** For those lines C6 IS INERT and the rung above is the PRE-FIX number.")
    missing_baselines = []
    for ln in by_line:
        if ln != "test":
            continue
        have = {a[0] for a in by_line[ln]}
        missing_baselines = [b for b in BASELINE_ARMS if b not in have]
    if missing_baselines:
        print()
        print("  *** %d REGISTERED H1 BASELINE(S) ABSENT FROM THE CORE LINE: %s"
              % (len(missing_baselines), ", ".join(missing_baselines)))
        print("  *** They cannot be supplied by the frozen roster (baselines never get a -winner")
        print("  *** dir), so they are invisible to the minimum. N6 is CONFIRMATORY under R108.")

    print()
    print("--- C1: HOLES below an arm's own frontier (the defect no other layer sees) ---")
    if not holed:
        print("  NONE -- every started arm is a contiguous seed prefix 0..n-1.")
    for (line, arm), v in sorted(holed.items()):
        shown = v["holes"][:12]
        print("  %-30s %-20s frontier %4d, n=%-4d holes=%d %s%s"
              % (line, arm, v["frontier"], v["n"], len(v["holes"]), shown,
                 " ..." if len(v["holes"]) > 12 else ""))
        print("        -> banks rung %d instead of the %d its frontier suggests"
              % (banked_rung(v["seeds"], rungs),
                 banked_rung(set(range(v["frontier"] + 1)), rungs)))

    print()
    print("--- C4: seeds at or above the registered ceiling %d (would be UNREGISTERED) ---" % top)
    print("  NONE." if not over else "  *** %s" % over)
    print("--- C5: duplicate seed directories ---")
    print("  NONE." if not dupes else "  *** %s" % dupes)

    print()
    print("--- C6: REGISTERED arms holding NO sealed-test record (each banks rung 0) ---")
    if not unstarted:
        print("  NONE -- every arm with a frozen winner has begun its sealed-test ladder.")
    else:
        for line in sorted({ln for ln, _ in unstarted}):
            arms = sorted(a for ln, a in unstarted if ln == line)
            print("  %-30s %s" % (line, ", ".join(arms)))
        print()
        print("  A frozen winner with no sealed-test record is the NORMAL state before a line")
        print("  enters C4, and on every line the h2_pair (distributional + scalar) is tested LAST.")
        print("  It is reported here because it is what the per-line minimum above is made of, and")
        print("  because omitting it is what made this table read 30 for four lines that bank 0.")

    print()
    print("EFFECT-BLIND: directory names and counts only. No record was opened, no metric read.")
    print()
    if holed or over or dupes:
        # ⚠ This printed "N arm(s) hold a HOLE" even when the ONLY failure was C4 (a seed above the
        # ladder) or C5 (a duplicate). Naming the wrong check sends a reader to the wrong evidence.
        parts = []
        if holed:
            parts.append("%d arm(s) hold a HOLE below their own frontier" % len(holed))
        if over:
            parts.append("%d arm(s) carry a seed AT OR ABOVE the registered ceiling (C4)"
                         % len(over))
        if dupes:
            parts.append("%d arm(s) have DUPLICATE seed directories (C5)" % len(dupes))
        print("VERDICT: " + "; ".join(parts) + ".")
        print("  A hole DEMOTES that arm's bankable rung, and the common rung is a MINIMUM over")
        print("  every arm of every line -- so one hole can cap the ENTIRE campaign's reported result.")
        print()
        print("  *** A HOLE IS NOT BY ITSELF A DEFECT, AND THIS CHECK MUST NOT BE READ AS AN ALARM. ***")
        print("  During pipelined C4 a line lands seeds OUT OF ORDER as pack-8 jobs return, so a")
        print("  climbing line ALWAYS shows holes. That is the normal state and it self-heals.")
        print("  THE DISCRIMINATOR IS WHETHER WORK IS IN FLIGHT, and this file cannot see jobs:")
        print("    hole + jobs running/queued  -> MID-FILL. Benign. Expected. Do nothing.")
        print("    hole + ZERO running AND ZERO queued -> the line will never fill it by itself")
        print("       unless its driver submits a repair round. THAT is the actionable case.")
        print("  Run `docs/ops/line_balance.py --once` for the job counts, and read the driver log")
        print("  for a `round 2` submission before concluding anything -- measured 2026-08-03,")
        print("  gpt-5.6-luna sat job-less for 20 min and then repaired its own 8 seeds.")
        return 1
    print("VERDICT: CLEAN -- every started arm is a contiguous prefix with no hole below its frontier.")
    return 0


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

    R = [30, 100, 189, 279, 340, 403, 568]

    check("A a complete 0..567 set banks the top rung",
          banked_rung(set(range(568)), R) == 568)
    check("B a complete 0..188 set banks 189, not 279",
          banked_rung(set(range(189)), R) == 189)
    # C IS THE WHOLE POINT: the live gpt-5.6-luna shape.
    gpt = set(range(568)) - {192, 193}
    check("C THE LIVE CASE: 566 seeds with a frontier of 567 but holes at 192/193 banks 189, not 568",
          banked_rung(gpt, R) == 189, banked_rung(gpt, R))
    # ⚠ D asserts on the FIXTURE, not on code under test, so it can never fail. Kept because it
    # states WHY the other layers missed the live gpt case, but it is illustrative, not a check --
    # labelled so it cannot inflate the pass count's meaning (auditor, 2026-08-04).
    check("D [illustrative, not a check] len()/max() BOTH miss it, which is why no layer caught it",
          len(gpt) == 566 and max(gpt) == 567 and banked_rung(gpt, R) != 568)
    check("E a hole at seed 0 banks NOTHING", banked_rung(set(range(1, 568)), R) == 0)
    check("F a hole just above a rung does not demote below it",
          banked_rung(set(range(568)) - {300}, R) == 279)

    with tempfile.TemporaryDirectory() as td:
        check("G an EMPTY archive exits 2, never 0", report(td) == 2)

    with tempfile.TemporaryDirectory() as td:
        d = os.path.join(td, "test_leg_x", "distributional")
        for s in list(range(30)):
            os.makedirs(os.path.join(d, "distributional-s%d" % s), exist_ok=True)
            with open(os.path.join(d, "distributional-s%d" % s, "record.json"), "w",
                      encoding="utf-8") as fh:
                fh.write("{}")
        rc_clean = report(td)
        # now punch a hole and prove the verdict FLIPS -- a check that cannot fail verifies nothing
        import shutil
        shutil.rmtree(os.path.join(d, "distributional-s7"))
        rc_holed = report(td)
        check("H a contiguous arm is CLEAN(0) and punching ONE hole flips it to 1",
              rc_clean == 0 and rc_holed == 1, "clean=%s holed=%s" % (rc_clean, rc_holed))

    check("I the rungs are READ from the registration, not hardcoded",
          registered_rungs() == R, str(registered_rungs()))

    # ---------------------------------------------------------------------------------------
    # C6 -- THE LIVE DEFECT (P244). The pre-fix code dropped zero-record arms from the
    # population before taking the per-line minimum.
    # ⚠ CORRECTED 2026-08-04: this said "EVERY case below FAILS against the pre-fix code",
    # which is FALSE and was a trust claim inside the file whose whole purpose is trust.
    # J, K, L and N DISCRIMINATE (they read one way after the fix and the other before).
    # M is a REGRESSION GUARD and passes both sides by design. O and P also pass pre-fix:
    # they guard the fix's own failure modes (a weakened vacuity guard, an invented arm),
    # not the original defect. The commit message said "the four new cases" and was right;
    # this comment was the one that overstated.
    # ---------------------------------------------------------------------------------------
    def _plant(base, line, arm, seeds):
        d = os.path.join(base, line, arm)
        os.makedirs(d, exist_ok=True)
        for s in seeds:
            u = os.path.join(d, "%s-s%d" % (arm, s))
            os.makedirs(u, exist_ok=True)
            with open(os.path.join(u, "record.json"), "w", encoding="utf-8") as fh:
                fh.write("{}")

    def _freeze(base, line, arms):
        d = os.path.join(base, "frozen" + line[len("test"):])
        for a in arms:
            os.makedirs(os.path.join(d, "%s-winner" % a), exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        # THE EXACT LIVE SHAPE: a line with a frozen winner for an arm that has no test dir.
        _plant(td, "test", "placebo", range(30))
        _freeze(td, "test", ["placebo", "distributional", "scalar"])
        d = scan(td)
        check("J a REGISTERED arm with no test directory IS in the population",
              ("test", "distributional") in d and ("test", "scalar") in d,
              str(sorted(k[1] for k in d)))
        check("K and it is marked started=False with an empty seed set",
              d[("test", "distributional")]["started"] is False
              and d[("test", "distributional")]["n"] == 0)
        check("L so the line's minimum is 0, NOT the 30 its started arm holds",
              min(banked_rung(v["seeds"], R) for v in d.values()) == 0,
              str({k[1]: banked_rung(v["seeds"], R) for k, v in d.items()}))
        check("M while the STARTED arm still reads 30 -- the fix must not damage the real number",
              banked_rung(d[("test", "placebo")]["seeds"], R) == 30)

    with tempfile.TemporaryDirectory() as td:
        # An arm whose test DIRECTORY exists but is EMPTY is the same condition, and it was the
        # live shape on glm_5_2 and kimi_k3 -- the directory was created, no record had landed.
        _plant(td, "test_leg_x", "placebo", range(30))
        os.makedirs(os.path.join(td, "test_leg_x", "scalar"), exist_ok=True)
        d = scan(td)
        check("N an EMPTY arm directory also banks 0 rather than vanishing",
              ("test_leg_x", "scalar") in d
              and d[("test_leg_x", "scalar")]["started"] is False
              and min(banked_rung(v["seeds"], R) for v in d.values()) == 0)

    with tempfile.TemporaryDirectory() as td:
        # The vacuity guard must survive C6: winners but no records is LEARNING NOTHING, not a pass.
        _freeze(td, "test", ["placebo", "scalar"])
        os.makedirs(os.path.join(td, "test"), exist_ok=True)
        rc_o = report(td)   # ⚠ called ONCE: the detail arg is eager, so `str(report(td))` re-ran
        check("O winners but ZERO records still exits 2 (the guard was not weakened by C6)",
              rc_o == 2, str(rc_o))

    with tempfile.TemporaryDirectory() as td:
        # The roster is READ, not assumed: no frozen dir means no phantom arms are invented.
        _plant(td, "test_leg_y", "placebo", range(30))
        d = scan(td)
        check("P with no frozen/ directory the roster adds NOTHING (no invented arms)",
              set(d) == {("test_leg_y", "placebo")}, str(sorted(d)))

    # ---------------------------------------------------------------------------------------
    # P253 -- THE BINDING CAUSE IS THE ARM WITH THE LOWEST BANKED RUNG, NOT THE MOST HOLES.
    # Fixture: `arm_low` has ONE hole at seed 5, so it banks 0 and CAPS the line. `arm_many` has
    # ~80 holes, all above rung 403, so it banks 403 and caps nothing. The pre-fix
    # `max(arms, key=hole_count)` named `arm_many`. Both cases read the RENDERED note, because the
    # rendered note is what a session acts on.
    # ---------------------------------------------------------------------------------------
    with tempfile.TemporaryDirectory() as td:
        plan = {"arm_low": [x for x in range(30) if x != 5],
                "arm_many": [x for x in range(568) if not (403 <= x and x % 2)]}
        for arm, seeds in plan.items():
            d = os.path.join(td, "test_leg_p", arm)
            os.makedirs(d, exist_ok=True)
            for sd in seeds:
                u = os.path.join(d, "%s-s%d" % (arm, sd))
                os.makedirs(u, exist_ok=True)
                with open(os.path.join(u, "record.json"), "w", encoding="utf-8") as fh:
                    fh.write("{}")
        dat = scan(td)
        r_low = banked_rung(dat[("test_leg_p", "arm_low")]["seeds"], R)
        r_many = banked_rung(dat[("test_leg_p", "arm_many")]["seeds"], R)
        h_low = len(dat[("test_leg_p", "arm_low")]["holes"])
        h_many = len(dat[("test_leg_p", "arm_many")]["holes"])
        check("Q1 fixture: the CAPPING arm has FEWER holes than the non-capping one",
              r_low == 0 and r_many == 403 and h_low < h_many,
              "low=(rung %s, %s holes) many=(rung %s, %s holes)" % (r_low, h_low, r_many, h_many))
        import contextlib as _cl
        import io as _io
        buf = _io.StringIO()
        with _cl.redirect_stdout(buf):
            report(td)
        cap = [ln for ln in buf.getvalue().splitlines()
               if "test_leg_p" in ln and "banked rung" in ln]
        check("Q2 the note names the arm that CAPS (rung 0), not the one with the most holes",
              bool(cap) and "arm_low" in cap[0] and "arm_many" not in cap[0],
              cap[0].strip() if cap else "NO LINE RENDERED")

    print("\nselftest: %d passed, %d failed" % (ok, fail))
    return 0 if fail == 0 else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Seed-set completeness and the rung actually banked.")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    return report(a.root, verbose=a.verbose)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
