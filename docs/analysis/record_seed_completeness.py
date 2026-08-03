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


def registered_rungs(path: str = PREREG) -> list:
    """The frozen assurance-tier ladder, READ from the registration (Amendment E1)."""
    import yaml

    with open(path, encoding="utf-8") as fh:
        yml = yaml.safe_load(fh) or {}
    seeds = yml.get("seeds")
    if isinstance(seeds, dict) and isinstance(seeds.get("tiers"), list):
        return [int(t) for t in seeds["tiers"]]
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


def scan(root: str) -> dict:
    """{(line, arm): {seeds, holes, frontier, dupes}} over every sealed-test root."""
    out = {}
    if not os.path.isdir(root):
        return out
    for line in sorted(os.listdir(root)):
        if not line.startswith("test"):
            continue
        lp = os.path.join(root, line)
        if not os.path.isdir(lp):
            continue
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
            if not seeds:
                continue
            frontier = max(seeds)
            holes = sorted(set(range(frontier + 1)) - seeds)
            out[(line, arm)] = {"seeds": seeds, "holes": holes, "frontier": frontier,
                                "dupes": dupes, "n": len(seeds)}
    return out


def report(root: str, verbose: bool = False) -> int:
    try:
        rungs = registered_rungs()
    except Exception as exc:  # noqa: BLE001
        print("*** cannot read the registered rungs: %r" % (exc,))
        return 2
    data = scan(root)
    if not data:
        print("*** NO started test arms found. This check inspected NOTHING and is VACUOUS.")
        print("    A vacuous pass banks a property that was never tested (P197/P213). Exiting 2.")
        return 2

    top = max(rungs)
    print("=== S15 SEED-SET COMPLETENESS (sealed test) ===")
    print("  registered rungs (READ from config/preregistration.yaml): %s" % rungs)
    print("  (line, arm) started arms inspected                      : %d" % len(data))
    print()

    holed = {k: v for k, v in data.items() if v["holes"]}
    over = {k: sorted(s for s in v["seeds"] if s >= top) for k, v in data.items()
            if any(s >= top for s in v["seeds"])}
    dupes = {k: v["dupes"] for k, v in data.items() if v["dupes"]}

    print("--- C2/C3: the rung each LINE has actually banked (its own MINIMUM over arms) ---")
    by_line = {}
    for (line, arm), v in data.items():
        by_line.setdefault(line, []).append((arm, banked_rung(v["seeds"], rungs), v["n"],
                                             v["frontier"], len(v["holes"])))
    for line in sorted(by_line, key=lambda x: min(a[1] for a in by_line[x])):
        arms = by_line[line]
        lo = min(a[1] for a in arms)
        note = ""
        worst = max(arms, key=lambda a: a[4])
        if worst[4]:
            note = ("   <<< %s has %d HOLE(S) below its frontier %d -- that is what caps this line"
                    % (worst[0], worst[4], worst[3]))
        print("  %-30s banked rung %4d  (arms: %s)%s"
              % (line, lo, " ".join("%s=%d" % (a[0][:12], a[1]) for a in arms) if verbose
                 else "%d arms" % len(arms), note))

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
    print("EFFECT-BLIND: directory names and counts only. No record was opened, no metric read.")
    print()
    if holed or over or dupes:
        print("VERDICT: %d arm(s) hold a HOLE below their own frontier." % len(holed))
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
    check("D and len()/max() BOTH fail to see it -- which is why no other layer caught it",
          len(gpt) == 566 and max(gpt) == 567)
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
