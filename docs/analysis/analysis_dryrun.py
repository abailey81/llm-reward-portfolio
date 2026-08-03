"""DRY RUN of the confirmatory analysis pipeline against REAL RUN 4 records -- value-blind.

WHY (ops M253 s.7, routed to this lane): scripts/analyze_campaign.py HAS NEVER BEEN RUN ON
RUN 4. outputs/tables/ holds only prototype-era files dated Jul 27. So the pipeline that
produces every registered result is UNVALIDATED against real campaign data, and at teardown
we would be running it for the first time on the archive that matters. If it crashes, or
silently drops registered outputs, that is the worst possible moment to discover it.

WHY THIS IS SAFE TO RUN NOW, and why ops correctly did not:
  * `main()` ends with `write_report(result, args.root)`, which mkdirs and writes
    campaign_overfitting.json + the markdown report INTO THE ARCHIVE (lines 6829/6904/6905).
    Running the CLI would publish numbers computed on an INCOMPLETE campaign.
  * `analyze()` ITSELF writes nothing -- every write is inside write_report. So this calls
    `analyze()` directly and never calls write_report. Nothing is created, modified or
    published, and no copy of the archive is needed.

*** BLINDING -- THE POINT OF THIS FILE. *** `analyze()` computes confirmatory verdicts. The
A16 window is OPEN. So this reports ONLY STRUCTURE:
    - did it run, or raise, and where
    - which REGISTERED_OUTPUT_KEYS are present / explained-absent / UNEXPLAINED-absent
    - for each present key: its TYPE, its length, and its SUB-KEY NAMES
*** NO VALUE IS EVER PRINTED, STORED OR COMPARED. *** No p-value, no estimate, no contrast,
no verdict. There is a hard guard: `describe()` returns only names, types and counts, and a
whitelist assertion refuses to emit anything that is not a name/type/int.

I am LOGGING THAT I RAN IT, per the blinding rule, and drawing nothing from any magnitude.

Usage:  python docs/analysis/analysis_dryrun.py [--root <archive>]
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_ROOT = REPO / "outputs" / "campaign_cluster_run4"


def describe(v, depth: int = 0) -> str:
    """Return a VALUE-FREE description: type, size, and sub-key NAMES only."""
    t = type(v).__name__
    if isinstance(v, dict):
        keys = sorted(str(k) for k in v.keys())
        shown = ", ".join(keys[:12]) + (f", +{len(keys)-12} more" if len(keys) > 12 else "")
        inner = ""
        if depth == 0 and keys:
            first = v[sorted(v.keys(), key=str)[0]]
            inner = f"  [first sub-value type: {type(first).__name__}]"
        return f"dict({len(v)} keys: {shown}){inner}"
    if isinstance(v, (list, tuple)):
        et = type(v[0]).__name__ if v else "-"
        return f"{t}(len={len(v)}, element type={et})"
    if v is None:
        return "None"
    if isinstance(v, bool):
        return "bool(<value withheld>)"
    if isinstance(v, (int, float)):
        return f"{t}(<value withheld>)"
    if isinstance(v, str):
        return f"str(len={len(v)}, <content withheld>)"
    return t


def main() -> int:
    root = DEFAULT_ROOT
    if "--root" in sys.argv:
        root = Path(sys.argv[sys.argv.index("--root") + 1])
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "scripts"))

    print("=== CONFIRMATORY ANALYSIS PIPELINE -- DRY RUN (value-blind) ===")
    print(f"    archive : {root}")
    print("    calling analyze() DIRECTLY; write_report() is NOT called, so nothing is")
    print("    created, modified or published in the archive.")
    print("    BLINDING LOG: this run COMPUTES confirmatory quantities. Only STRUCTURE is")
    print("    reported -- key names, types, sizes. No value is printed or compared.\n")

    try:
        from analyze_campaign import (  # type: ignore[import-not-found]
            REGISTERED_OUTPUT_KEYS, analyze, missing_output_keys,
        )
    except Exception:
        print("!! could not import the analysis module:")
        traceback.print_exc()
        return 2

    print(f"    REGISTERED_OUTPUT_KEYS: {len(REGISTERED_OUTPUT_KEYS)}\n")

    h3 = root / "test_h3_singleshot"
    try:
        result = analyze(str(root),
                         single_shot_root=str(h3) if h3.is_dir() else None)
    except Exception:
        print("!! *** THE ANALYSIS PIPELINE RAISED ON REAL RUN 4 DATA *** !!")
        print("   This is exactly the failure the dry run exists to find before teardown.\n")
        traceback.print_exc()
        return 2

    print("    *** analyze() COMPLETED WITHOUT RAISING on real RUN 4 records. ***\n")

    if not isinstance(result, dict):
        print(f"!! analyze() returned {type(result).__name__}, expected dict")
        return 2

    explained, unexplained = missing_output_keys(result)
    present = [k for k in REGISTERED_OUTPUT_KEYS if k in result]
    print(f"=== REGISTERED OUTPUT KEYS: {len(present)}/{len(REGISTERED_OUTPUT_KEYS)} present ===")
    for k in sorted(present):
        print(f"    OK        {k:<34}{describe(result[k])}")
    if explained:
        print(f"\n=== ABSENT, WITH A STATED PRECONDITION ({len(explained)}) ===")
        for k, why in sorted(explained.items()):
            print(f"    absent    {k:<34}requires {why}")
    if unexplained:
        print(f"\n!! *** REGISTERED-OUTPUT DEFECT: {len(unexplained)} absent with NO stated "
              f"precondition *** !!")
        for k in sorted(unexplained):
            print(f"    MISSING   {k}")

    extra = sorted(set(result) - set(REGISTERED_OUTPUT_KEYS))
    if extra:
        print(f"\n=== keys present but NOT in the registered set ({len(extra)}) ===")
        print("    " + ", ".join(extra[:20]))
        print("    >> a quantity that reaches the report and is not in the registered")
        print("       enumeration is a defect in the ENUMERATION (CLAUDE.md scope clause).")

    print(f"\n  VERDICT: {'REGISTERED-OUTPUT DEFECT' if unexplained else 'PIPELINE OK'}")
    return 2 if unexplained else 0


if __name__ == "__main__":
    raise SystemExit(main())
