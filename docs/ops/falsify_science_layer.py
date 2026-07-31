"""FALSIFICATION TEST for the FULL science layer, scoped to the tool that OWNS each invariant.

CORRECTION TO MY FIRST ATTEMPT. I planted six violations and tested only `science_watch.py`, then read
four `rc=0` results as "the monitor cannot see them". That was MY scoping error: `cycle.py` extracts by
REGEX FROM THE TEXT (not from the return code), and six of the eight invariants are owned by
`results_audit.py`, not by science_watch. science_watch returning 0 for them is correct -- they are not
its job.

So the honest test has TWO parts, and both must pass or `sci=OK` is not evidence:

  (1) DETECTION -- does the owning tool's REPORTED COUNT go non-zero when the invariant is violated?
  (2) EXTRACTION -- does cycle.py's regex for that count actually MATCH the tool's real output?
      A perfect detector whose count cycle.py cannot parse is exactly as useless as no detector,
      and this session already found three instruments that failed at (2)-shaped problems.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REAL = Path("outputs/campaign_cluster_run4")
BASE = Path(sys.argv[1])
RA = "docs/ops/results_audit.py"
SW = "docs/ops/science_watch.py"

# cycle.py's own extraction table, copied verbatim so the test checks the REAL contract.
FIELDS = {
    "sw_budget_breaches":  (SW, r"train_safe_call_count\s*!=\s*400,000\s*:\s*(\d+)"),
    "sw_impossible":       (SW, r"impossible/non-finite scores\s*:\s*(\d+)"),
    "ra_hash_mismatch":    (RA, r"reward_source_hash mismatches\s*:\s*(\d+)"),
    "ra_out_of_range":     (RA, r"out-of-range gen/seed\s*:\s*(\d+)"),
    "ra_non_finite":       (RA, r"non-finite metrics\s*:\s*(\d+)"),
    "ra_scalar_leaks":     (RA, r"scalar prompts leaking a tail statistic\s*:\s*(\d+)"),
    "ra_cross_arm_shared": (RA, r"programs identical ACROSS arms\s*:\s*(\d+)"),
}


def build(dst: Path, n=4) -> int:
    if dst.exists():
        shutil.rmtree(dst)
    c = 0
    for arm in ("distributional", "scalar", "placebo", "scalar_cvar5", "placebo_shuffled"):
        for s in sorted((REAL / "search" / arm).glob("*/record.json"))[:n]:
            d = dst / "search" / arm / s.parent.name / "record.json"
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, d)
            for side in ("prompt.txt", "reward.py", "env.json"):
                if (s.parent / side).exists():
                    shutil.copy2(s.parent / side, d.parent / side)
            c += 1
    return c


def run(tool: str, root: Path) -> str:
    p = subprocess.run([sys.executable, tool, str(root)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return (p.stdout or "") + (p.stderr or "")


def read(field: str, root: Path) -> int | None:
    tool, rx = FIELDS[field]
    m = re.search(rx, run(tool, root))
    return int(m.group(1)) if m else None


def first(root: Path) -> Path:
    return sorted(root.glob("search/*/*/record.json"))[0]


def edit(root: Path, fn):
    p = first(root)
    rec = json.load(open(p, encoding="utf-8"))
    fn(rec, p)
    json.dump(rec, open(p, "w", encoding="utf-8"), allow_nan=True)


CASES = [
    ("sw_budget_breaches", "steps != 400,000",
     lambda r, p: r.setdefault("metrics", {}).__setitem__("train_safe_call_count", 123)),
    ("sw_impossible", "impossible score",
     lambda r, p: r.setdefault("metrics", {}).__setitem__("val_fitness", 42.0)),
    ("ra_hash_mismatch", "hash mismatch",
     lambda r, p: r.__setitem__("reward_source_hash", "0" * 64)),
    ("ra_out_of_range", "out-of-range seed",
     lambda r, p: r.__setitem__("seed", 999999)),
    ("ra_non_finite", "non-finite metric",
     lambda r, p: r.setdefault("metrics", {}).__setitem__("val_fitness", float("nan"))),
]


def main() -> int:
    clean = BASE / "clean"
    n = build(clean)
    print(f"synthetic archive: {n} records\n")

    print("STEP 1 -- EXTRACTION: does cycle.py's regex match each tool's REAL output?")
    base = {}
    for f in FIELDS:
        v = read(f, clean)
        base[f] = v
        print(f"   {'OK  ' if v is not None else '*** NO MATCH ***'}  {f:22s} baseline = {v}")
    unmatched = [f for f, v in base.items() if v is None]
    print()

    print("STEP 2 -- DETECTION: plant the violation, require the OWNING count to rise")
    missed = []
    for field, name, fn in CASES:
        d = BASE / ("c_" + field)
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(clean, d)
        edit(d, fn)
        after = read(field, d)
        before = base.get(field)
        ok = (before is not None and after is not None and after > before)
        if not ok:
            missed.append(name)
        print(f"   {'DETECTED' if ok else '*** MISSED ***':16s} {name:22s} "
              f"{field}: {before} -> {after}")

    print()
    if unmatched:
        print(f"*** EXTRACTION BROKEN for: {unmatched} -- cycle.py cannot read these at all")
    if missed:
        print(f"*** NOT DETECTED: {missed}")
    if not unmatched and not missed:
        print("BOTH LEGS PASS: every tested invariant is detected by its owning tool AND")
        print("readable by cycle.py's extractor. `sci=OK` is falsifiable evidence, not decoration.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
