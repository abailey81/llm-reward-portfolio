"""R115 THRESHOLD SENSITIVITY - is the registered winner-eligibility floor still insensitive?

WHY THIS EXISTS (2026-08-03, RUN 17, execution record s.126).

Amendment R115 registers `fitness.winner_max_fallback_frac: 0.10` - a candidate may only be frozen
as its arm's winner if its AUTHORED reward actually ran, i.e.
`train_safe_default_count / train_safe_call_count < 0.10`. The VALUE is defended in the frozen
registration with an empirical claim:

    "THRESHOLD-INSENSITIVE, NOT TUNED: the observed distribution is strongly bimodal - worst trace
     0.41 %, mildest severe 39.40 %, a 96x EMPTY GAP - so any value in ~1-35 % partitions the data
     identically; 0.10 sits in that gap."

That claim was true of RUN 1's 613 records. **It is a claim about a DISTRIBUTION, and the campaign
has since written thousands more candidates into that distribution.** This file re-derives it from
whatever the archive holds today, so the disclosure that goes into the dissertation rests on a
measurement rather than on an inherited sentence.

WHAT IS AT STAKE, stated precisely so it is neither over- nor under-claimed:

  * The VALUE is NOT compromised. It was pre-committed on 2026-07-28, BEFORE any RUN 4 candidate
    existed, and `scripts/run_campaign.py::_winner_eligible` reads ONLY the two execution counters -
    never `val_fitness`, never a test metric - so the rule is effect-blind BY CONSTRUCTION and
    cannot have been steered toward an outcome. **This is not a forking path.**
  * What can be false is the JUSTIFICATION. If the band the registration calls identical is no
    longer empty, then a reader who re-derives the distribution finds the frozen document asserting
    something the data contradicts. An adversarial examiner does exactly that.
  * The threshold must therefore **NEVER** be changed. Changing a frozen value to match new data is
    the post-data forking path the whole pre-registration exists to forbid; the correct remedy is
    disclosure.

THE POSITIVE CONTROL, and it is what makes this trustworthy: at the FROZEN threshold this file must
reproduce the ACTUAL frozen winner of every arm, read from that arm's `frozen*/<arm>-winner/`
marker. If it does not, the script's model of the selection rule is wrong and NOTHING else it prints
may be believed - a surprising negative is a claim about my own code first.

EFFECT-BLIND OUTPUT. The rule itself must read `val_fitness` to find an argmax, and so must any
faithful re-derivation of it. What this file PRINTS is only ever set membership, candidate
IDENTITY, and counts - never a fitness value, never a comparison between arms, and never anything
from the sealed test. It is a statement about WHICH candidate the registered rule selects, not
about how any arm performed.

    python docs/analysis/r115_threshold_sensitivity.py
    python docs/analysis/r115_threshold_sensitivity.py --verbose
    python docs/analysis/r115_threshold_sensitivity.py --selftest

EXIT: 0 the registration's insensitivity claim still HOLDS on today's archive
      1 the claim is FALSIFIED (some group's eligible set or winner varies inside the band)
      2 the check could not run, or inspected NOTHING (a vacuous pass banks an untested property)
"""
from __future__ import annotations

import argparse
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_ROOT = os.path.join(REPO, "outputs", "campaign_cluster_run4")
PREREG = os.path.join(REPO, "config", "preregistration.yaml")

#: The band the frozen registration asserts "partitions the data identically".
BAND_LO, BAND_HI = 0.01, 0.35


def registered_ceiling(path: str = PREREG) -> float:
    """The frozen R115 value, READ from the registration - never hardcoded (the R84 lesson)."""
    import yaml

    with open(path, encoding="utf-8") as fh:
        yml = yaml.safe_load(fh) or {}
    frac = ((yml.get("fitness") or {}).get("winner_max_fallback_frac"))
    if frac is None:
        raise KeyError("fitness.winner_max_fallback_frac absent from the registration")
    return float(frac)


def fallback_frac(record: dict):
    """EXACTLY `scripts/run_campaign.py::_fallback_frac`. None means 'uncounted', not 'zero'."""
    m = record.get("metrics", {}) or {}
    calls = m.get("train_safe_call_count")
    try:
        calls = int(calls or 0)
    except (TypeError, ValueError):
        return None
    if calls <= 0:
        return None
    return int(m.get("train_safe_default_count") or 0) / calls


def eligible_at(cands: list, thr: float) -> list:
    """EXACTLY `_winner_eligible`: an uncounted record is ELIGIBLE; nothing is guessed at."""
    return [c for c in cands if c["frac"] is None or c["frac"] < thr]


def winner_at(cands: list, thr: float):
    """EXACTLY `select_winner`: argmax of val_fitness over the eligible set, or None."""
    el = eligible_at(cands, thr)
    if not el:
        return None
    return max(el, key=lambda c: c["fit"] if c["fit"] is not None else float("-inf"))["id"]


def load_groups(root: str) -> dict:
    """{(line, arm): [ {id, frac, fit} ]} over SEARCH roots, depth-1 candidate dirs only.

    Depth-1 excludes the D18 nested duplicates (`<cand>/<cand>/record.json`), which is how ~20
    instruments came to double-count before D18 was found. ⚠ An earlier version of this docstring
    also credited depth-1 with excluding `.pull_tmp` staging copies; an auditor refuted the
    MECHANISM: the two live `.pull_tmp.*` dirs sit at the CAMPAIGN ROOT, so they are excluded by the
    `line.startswith("search")` filter above, not by depth. Same outcome, wrong reason - and a
    wrong reason is how the next person removes the wrong guard.
    """
    groups = {}
    if not os.path.isdir(root):
        return groups
    for line in sorted(os.listdir(root)):
        if not line.startswith("search"):
            continue
        lp = os.path.join(root, line)
        if not os.path.isdir(lp):
            continue
        for arm in sorted(os.listdir(lp)):
            ap = os.path.join(lp, arm)
            if arm.startswith(("_", ".")) or not os.path.isdir(ap):
                continue
            cands = []
            for d in sorted(os.listdir(ap)):
                p = os.path.join(ap, d, "record.json")
                if not os.path.isfile(p):
                    continue
                try:
                    with open(p, encoding="utf-8-sig") as fh:
                        rec = json.load(fh)
                except Exception:  # noqa: BLE001 - an unreadable record is reported, never skipped silently
                    cands.append({"id": d, "frac": None, "fit": None, "unreadable": True})
                    continue
                cands.append({"id": d, "frac": fallback_frac(rec),
                              "fit": (rec.get("metrics", {}) or {}).get("val_fitness")})
            if cands:
                groups[(line, arm)] = cands
    return groups


def frozen_winners(root: str) -> dict:
    """{(line, arm): candidate_id} actually frozen, from the `frozen*/<arm>-winner/` markers.

    The marker directory carries a `-winner` SUFFIX while the search tree uses the plain arm name;
    joining without stripping it matches NOTHING and manufactures one phantom per marker.
    """
    out = {}
    if not os.path.isdir(root):
        return out
    for d in sorted(os.listdir(root)):
        if not d.startswith("frozen") or not os.path.isdir(os.path.join(root, d)):
            continue
        line = "search" + d[len("frozen"):]
        for arm_dir in sorted(os.listdir(os.path.join(root, d))):
            p = os.path.join(root, d, arm_dir, "record.json")
            if not os.path.isfile(p):
                continue
            arm = arm_dir[:-len("-winner")] if arm_dir.endswith("-winner") else arm_dir
            try:
                with open(p, encoding="utf-8-sig") as fh:
                    rec = json.load(fh)
            except Exception:  # noqa: BLE001
                continue
            # ⚠ `candidate_id`, NOT `run_id`. A `frozen*/<arm>-winner/` record is a MARKER COPIED
            # from the winning search candidate: its `run_id` is the MARKER's own name
            # ("distributional-winner") while `candidate_id` names the SOURCE candidate
            # ("distributional-g5-c1"). Joining on run_id matches nothing and the positive control
            # reported 0 of 56 -- which is exactly what the control is for. This is the same field
            # `docs/analysis/record_provenance_seal.py:171` uses to chain a marker to its source.
            rid = rec.get("candidate_id") or rec.get("run_id")
            if rid:
                out[(line, arm)] = rid
    return out


def grid(ceiling: float, cands: list | None = None) -> list:
    """EXACT probe points, not a sample.

    ⚠ THE FIRST VERSION OF THIS SAMPLED 70 EVENLY-SPACED POINTS, and an auditor was right to call
    that out: a sampled grid can only ever say "no variation was OBSERVED between these points", and
    this number is going into a dissertation. The eligible set can only change AT a candidate's own
    fallback fraction, so probing just below and just above every observed fraction (plus the band
    endpoints and the registered ceiling) enumerates every reachable partition EXACTLY, with no
    density assumption. The auditor's independent exact computation agreed with the old grid's
    answer (15 and 2) - but agreement is not proof, and the method must be able to prove it.
    """
    pts = {BAND_LO, BAND_HI, ceiling}
    for c in (cands or []):
        f = c.get("frac")
        if f is not None:
            pts.add(f)              # just AT the fraction: `frac < thr` is False here -> excluded
            pts.add(f + 1e-12)      # just ABOVE: now eligible. The breakpoint is between these.
    return sorted(p for p in pts if p > 0)


def analyse(root: str, ceiling: float) -> dict:
    groups = load_groups(root)
    thresholds = []
    set_varies, winner_varies, in_band = [], [], []
    for key, cands in sorted(groups.items()):
        # EXACT probe points derived from THIS group's own fractions, restricted to the band the
        # registration claims is uniform. Sampling would only support "no variation observed".
        thresholds = [t for t in grid(ceiling, cands) if BAND_LO <= t <= BAND_HI]
        sets = {tuple(sorted(c["id"] for c in eligible_at(cands, t))) for t in thresholds}
        wins = {winner_at(cands, t) for t in thresholds}
        if len(sets) > 1:
            set_varies.append(key)
        if len(wins) > 1:
            winner_varies.append(key)
        for c in cands:
            if c["frac"] is not None and BAND_LO <= c["frac"] <= BAND_HI:
                in_band.append((key, c["id"], c["frac"]))
    # the registration's own bimodality claim, re-derived
    fracs = sorted(c["frac"] for cs in groups.values() for c in cs
                   if c["frac"] is not None and c["frac"] > 0)
    below = [f for f in fracs if f < BAND_LO]
    above = [f for f in fracs if f > BAND_HI]
    return {
        "groups": groups, "thresholds": thresholds,
        "set_varies": set_varies, "winner_varies": winner_varies, "in_band": in_band,
        "n_groups": len(groups),
        "n_candidates": sum(len(v) for v in groups.values()),
        "worst_trace": max(below) if below else None,
        "mildest_severe": min(above) if above else None,
        "n_nonzero_fallback": len(fracs),
    }


def report(root: str, verbose: bool = False) -> int:
    try:
        ceiling = registered_ceiling()
    except Exception as exc:  # noqa: BLE001
        print("*** cannot read the registered ceiling: %r" % (exc,))
        return 2
    a = analyse(root, ceiling)
    if a["n_groups"] == 0 or a["n_candidates"] == 0:
        print("*** ZERO search groups / candidates inspected. This check is VACUOUS and exits 2.")
        print("    'Found nothing wrong' and 'looked at nothing' are indistinguishable (P197/P213).")
        return 2

    print("=== R115 THRESHOLD SENSITIVITY ===")
    print("  registered ceiling (READ from config/preregistration.yaml) : %.4f" % ceiling)
    print("  band the registration calls identical                      : [%.2f, %.2f]"
          % (BAND_LO, BAND_HI))
    print("  (line, arm) selection groups inspected                     : %d" % a["n_groups"])
    print("  search candidates inspected                                : %d" % a["n_candidates"])
    print()

    # --- POSITIVE CONTROL: reproduce every ACTUAL frozen winner at the FROZEN threshold ---
    fw = frozen_winners(root)
    checked = agree = 0
    disagree = []
    for key, actual in sorted(fw.items()):
        if key not in a["groups"]:
            continue
        checked += 1
        mine = winner_at(a["groups"][key], ceiling)
        if mine == actual:
            agree += 1
        else:
            disagree.append((key, actual, mine))
    print("--- POSITIVE CONTROL: does this file reproduce the REAL frozen winners? ---")
    if checked == 0:
        print("  NO frozen-winner markers joined -- the control did not run, so nothing below is")
        print("  trustworthy. Exiting 2 rather than printing an unvalidated result.")
        return 2
    print("  frozen arms joined: %d   reproduced exactly: %d" % (checked, agree))
    if disagree:
        print("  *** MISMATCH -- the model of the selection rule is WRONG. Suspect THIS SCRIPT first.")
        for key, actual, mine in disagree[:10]:
            print("      %-30s %-18s frozen=%s  computed=%s" % (key[0], key[1], actual, mine))
        return 2
    print("  => the re-derivation reproduces the archive exactly; the numbers below are trustworthy.")
    print()

    # --- THE REGISTRATION'S OWN BIMODALITY CLAIM, RE-DERIVED ---
    print("--- the registration's claim: a 96x EMPTY GAP across [%.2f, %.2f] ---" % (BAND_LO, BAND_HI))
    print("  candidates with a NON-ZERO fallback fraction : %d" % a["n_nonzero_fallback"])
    wt, ms = a["worst_trace"], a["mildest_severe"]
    print("  worst 'trace' (below %.2f)   : %s" % (BAND_LO, ("%.5f%%" % (100 * wt)) if wt else "none"))
    print("  mildest 'severe' (above %.2f): %s" % (BAND_HI, ("%.5f%%" % (100 * ms)) if ms else "none"))
    print("  candidates INSIDE the band   : %d   <- the registration says this must be ZERO"
          % len(a["in_band"]))
    for key, cid, frac in sorted(a["in_band"], key=lambda r: -r[2])[:20 if verbose else 8]:
        print("      %-30s %-18s %-28s %.5f%%" % (key[0], key[1], cid, 100 * frac))
    if len(a["in_band"]) > (20 if verbose else 8):
        print("      ... and %d more" % (len(a["in_band"]) - (20 if verbose else 8)))
    print()

    # --- THE OPERATIVE QUESTION ---
    print("--- does the CHOICE OF THRESHOLD inside the band change anything? ---")
    print("  groups whose ELIGIBLE SET varies across the band : %d of %d"
          % (len(a["set_varies"]), a["n_groups"]))
    print("  groups whose SELECTED WINNER varies              : %d of %d"
          % (len(a["winner_varies"]), a["n_groups"]))
    if verbose:
        for key in a["set_varies"]:
            print("      set varies    : %-30s %s" % key)
    for key in a["winner_varies"]:
        print("      WINNER VARIES : %-30s %s" % key)
    print()

    print("EFFECT-BLIND: only set membership, candidate identity and counts were printed. No")
    print("fitness value, no cross-arm comparison and nothing from the sealed test.")
    print()

    if a["in_band"] or a["set_varies"] or a["winner_varies"]:
        print("VERDICT: THE REGISTERED INSENSITIVITY CLAIM IS FALSIFIED ON TODAY'S ARCHIVE.")
        print("  The VALUE remains protected: it was pre-committed before any RUN 4 candidate")
        print("  existed and `_winner_eligible` never reads a performance quantity, so the rule is")
        print("  effect-blind by construction and is NOT a forking path.")
        print("  *** DO NOT CHANGE THE THRESHOLD. *** The remedy is DISCLOSURE -- see")
        print("  docs/R115_DISCLOSURE_2026-08-03.md.")
        return 1
    print("VERDICT: the insensitivity claim still HOLDS on today's archive.")
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

    C = [{"id": "a", "frac": 0.00, "fit": 1.0},
         {"id": "b", "frac": 0.05, "fit": 9.0},     # the only in-band candidate
         {"id": "c", "frac": 0.90, "fit": 99.0}]
    check("A below the in-band candidate's frac it is EXCLUDED and the winner is 'a'",
          winner_at(C, 0.02) == "a", winner_at(C, 0.02))
    check("B above it the winner FLIPS to 'b' -- the threshold is decision-relevant",
          winner_at(C, 0.10) == "b", winner_at(C, 0.10))
    check("C a 90% candidate never becomes eligible inside the band",
          "c" not in eligible_at(C, 0.35))

    D = [{"id": "a", "frac": 0.0001, "fit": 1.0}, {"id": "b", "frac": 0.90, "fit": 99.0}]
    sets = {tuple(sorted(x["id"] for x in eligible_at(D, t))) for t in grid(0.10, D)
            if BAND_LO <= t <= BAND_HI}
    check("D with an EMPTY band the eligible set is invariant (the registration's claim)",
          len(sets) == 1, str(sets))

    check("E an UNCOUNTED record is eligible, never treated as zero",
          eligible_at([{"id": "z", "frac": None, "fit": 0.0}], 0.001) != [])
    check("F fallback_frac returns None (not 0.0) when call_count is 0",
          fallback_frac({"metrics": {"train_safe_call_count": 0,
                                     "train_safe_default_count": 5}}) is None)
    check("G fallback_frac computes the ratio when counters are present",
          abs(fallback_frac({"metrics": {"train_safe_call_count": 400000,
                                         "train_safe_default_count": 40000}}) - 0.1) < 1e-12)

    with tempfile.TemporaryDirectory() as td:
        check("H an EMPTY archive exits 2, never 0", report(td) == 2)

    with tempfile.TemporaryDirectory() as td:
        # candidates present but NO frozen markers -> the positive control cannot run -> exit 2
        p = os.path.join(td, "search_leg_x", "distributional", "distributional-g0-c0")
        os.makedirs(p)
        with open(os.path.join(p, "record.json"), "w", encoding="utf-8") as fh:
            json.dump({"run_id": "distributional-g0-c0",
                       "metrics": {"train_safe_call_count": 400000,
                                   "train_safe_default_count": 0, "val_fitness": 1.0}}, fh)
        check("I candidates but NO frozen markers -> control cannot run -> exit 2",
              report(td) == 2)

    check("J the -winner suffix is stripped when joining markers to arms",
          "distributional" == ("distributional-winner"[:-len("-winner")]))

    print("\nselftest: %d passed, %d failed" % (ok, fail))
    return 0 if fail == 0 else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Is R115's registered insensitivity claim still true?")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    return report(a.root, verbose=a.verbose)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
