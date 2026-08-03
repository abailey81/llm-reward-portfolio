"""PROOF OF THE A79 FIX + THE FULL CONTAMINATION SURFACE. Value-blind.

TWO THINGS OPS NEEDS AND DOES NOT HAVE:

  1. A VERIFIED FIX. I said a wrong fix is as dangerous as the defect, so ops should not have
     to invent one. This applies the proposed fix by MONKEY-PATCHING in THIS file (nothing
     under scripts/ or src/ is touched) and proves it works against the REAL archive.

  2. THE FULL BLAST RADIUS. M259/M264 reported H2. But every registered output that consumes
     the pooled record set is affected, and I had not enumerated them. `h1_beat_human` in
     particular compares an LLM arm against the 11-name canon -- if that arm's test records
     are a LEG's, then H1 (confirmatory node N6) is contaminated too.

METHOD: run analyze() TWICE -- once with the shipped loader, once with the fixed loader --
and diff the two results by STRUCTURE AND COUNTS ONLY.

*** BLINDING, ENFORCED IN CODE. *** The comparison walks both result trees and compares only:
  - which keys exist
  - list/dict LENGTHS
  - integer fields whose name is a COUNT (n, n_seeds, n_legs, size, count, ...)
*** Floats, p-values, effects, verdicts and booleans are NEVER read, printed or compared. ***
`_count_only()` whitelists by name and type; anything else is reported as "present" alone.
I am logging that both runs COMPUTE confirmatory quantities and that I read no magnitude.

Usage:  python docs/analysis/a79_fix_proof.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARCHIVE = REPO / "outputs" / "campaign_cluster_run4"

#: Integer fields that are COUNTS and are therefore safe to compare. Anything not on this
#: list is compared for PRESENCE only, never for value.
COUNT_NAMES = {"n", "n_seeds", "n_pairs", "n_legs", "n_legs_found", "n_legs_included",
               "n_trials", "n_records", "n_blocks", "size", "count", "n_tests",
               "n_hypotheses", "n_p_tests", "n_boot", "n_missing_source", "dsr_raw_n",
               "n_eff_raw", "n_verified", "expected", "present"}


def _count_only(node, path=""):
    """Yield (path, comparable) pairs. Comparable is a COUNT or the literal '<present>'."""
    if isinstance(node, dict):
        yield (path or "<root>", f"dict[{len(node)}]")
        for k in sorted(node, key=str):
            kk = f"{path}.{k}" if path else str(k)
            v = node[k]
            if isinstance(v, int) and not isinstance(v, bool) and str(k) in COUNT_NAMES:
                yield (kk, f"count={v}")
            elif isinstance(v, (dict, list)):
                yield from _count_only(v, kk)
            else:
                yield (kk, "<present>")
    elif isinstance(node, list):
        yield (path, f"list[{len(node)}]")
        for i, v in enumerate(node[:40]):
            if isinstance(v, (dict, list)):
                yield from _count_only(v, f"{path}[{i}]")


def fixed_loader(original, exclude=("_leg_",)):
    """THE PROPOSED FIX, as a wrapper: drop records whose SOURCE LINE is a leg.

    The shipped walk keys `seen` on run_id across a multi-line root, so leg ids that do not
    collide with a core id are POOLED INTO THE CORE ARM. The fix mirrors the existing
    `*_h3_singleshot` exclusion at analyze_campaign.py:1158.

    Implemented here WITHOUT editing scripts/: re-walk each top-level subtree separately and
    keep only the non-leg, non-h3 lines -- which is exactly what excluding them in the walk
    would produce.
    """
    def _loader(root):
        root = Path(root)
        keep = []
        for sub in sorted(p for p in root.iterdir() if p.is_dir()):
            if sub.name.startswith(".pull_tmp"):
                continue
            if any(x in sub.name for x in exclude) or sub.name.endswith("_h3_singleshot"):
                continue
            keep.extend(original(sub))
        # de-duplicate WITHIN the core line only (run_id IS unique there)
        seen = {}
        for r in keep:
            seen.setdefault(str(r.get("run_id")), r)
        return list(seen.values())
    return _loader


def main() -> int:
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "scripts"))
    import analyze_campaign as ac

    print("=== A79 FIX PROOF (value-blind) ===")
    print("    BLINDING LOG: both runs COMPUTE confirmatory quantities. Only key names,")
    print("    container LENGTHS and whitelisted COUNT fields are compared. No p-value,")
    print("    effect, verdict or boolean is read.\n")

    original = ac.load_campaign_records

    print("--- run 1: SHIPPED loader (the defect) ---")
    broken = ac.analyze(str(ARCHIVE),
                        single_shot_root=str(ARCHIVE / "test_h3_singleshot"))
    print("    done.")

    print("--- run 2: FIXED loader (legs + h3 excluded from the core walk) ---")
    ac.load_campaign_records = fixed_loader(original)
    try:
        fixed = ac.analyze(str(ARCHIVE),
                           single_shot_root=str(ARCHIVE / "test_h3_singleshot"))
    finally:
        ac.load_campaign_records = original
    print("    done.\n")

    a = dict(_count_only(broken))
    b = dict(_count_only(fixed))
    keys = sorted(set(a) | set(b))

    changed = [(k, a.get(k, "<absent>"), b.get(k, "<absent>"))
               for k in keys if a.get(k) != b.get(k)]
    # Group by the registered output they belong to.
    by_out = {}
    for k, av, bv in changed:
        top = k.split(".")[0].split("[")[0]
        by_out.setdefault(top, []).append((k, av, bv))

    print("=== REGISTERED OUTPUTS WHOSE STRUCTURE/COUNTS CHANGE UNDER THE FIX ===")
    print("    (a change means the shipped run CONSUMED contaminated records)\n")
    if not by_out:
        print("    NONE -- the contamination does not reach any registered output.")
    for top in sorted(by_out):
        rows = by_out[top]
        print(f"  *** {top} *** ({len(rows)} differing field(s))")
        for k, av, bv in rows[:8]:
            print(f"        {k:<58} shipped={av:<14} fixed={bv}")
        if len(rows) > 8:
            print(f"        ... +{len(rows)-8} more")
    print(f"\n  registered outputs affected: {len(by_out)}")
    print(f"  outputs identical under both: "
          f"{len({k.split('.')[0].split('[')[0] for k in keys}) - len(by_out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
