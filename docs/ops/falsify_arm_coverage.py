"""FALSIFICATION TEST for arm_coverage.py -- VALID input this time.

MY FIRST ATTEMPT WAS STRUCTURALLY INVALID and I nearly reported "we are blind to a missing arm".
arm_coverage reads the BATCH REGISTRY (`<root>/batches/`, one entry per submitted batch), NOT
`record.json` files. My synthetic archive had only records, so `coverage()` returned empty, the tool
correctly printed "no batch registry -- nothing submitted yet", and the baseline was 0 -- which makes
"0 after planting" prove nothing. The tell was that the CLEAN baseline already read 0.

This builds the input the tool actually consumes. arm_coverage is the D14 WORKAROUND -- the six repo
guards cannot see a missing arm -- so if it is blind, nothing covers that failure at all.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REAL = Path("outputs/campaign_cluster_run4")
BASE = Path(sys.argv[1])


def run(root: Path) -> tuple[int, str]:
    p = subprocess.run([sys.executable, "docs/ops/arm_coverage.py", str(root)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def build(dst: Path) -> int:
    """Copy the REAL batch registry -- that is the tool's actual input."""
    if dst.exists():
        shutil.rmtree(dst)
    (dst / "batches").mkdir(parents=True)
    n = 0
    for e in (REAL / "batches").iterdir():
        (dst / "batches" / e.name).mkdir(exist_ok=True)
        n += 1
    return n


def main() -> int:
    clean = BASE / "clean"
    n = build(clean)
    rc0, out0 = run(clean)
    full0 = out0.count("arms submitted")
    print(f"synthetic batch registry: {n} entries copied")
    print(f"BASELINE : rc={rc0}  lines reporting 'arms submitted' = {full0}")
    print(f"           verdict line -> {[l for l in out0.splitlines() if 'VERDICT' in l]}")

    # PLANT D14: remove EVERY batch entry for one (line, arm) -- a partial arm failure.
    d = BASE / "missing_arm"
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(clean, d)
    victim_arm, victim_line = "scalar_cvar5", "leg9"
    removed = 0
    for e in list((d / "batches").iterdir()):
        if e.name.startswith(victim_line) and victim_arm in e.name:
            shutil.rmtree(e)
            removed += 1
    print(f"\nPLANTED  : removed all {removed} batch entries for {victim_line}/{victim_arm}")

    rc1, out1 = run(d)
    full1 = out1.count("arms submitted")
    missing_line = [l for l in out1.splitlines() if "MISSING" in l]
    verdict = [l for l in out1.splitlines() if "VERDICT" in l]
    detected = (rc1 != 0) or bool(missing_line)
    print(f"RESULT   : rc={rc1}  'arms submitted' lines = {full1}")
    print(f"           MISSING line -> {missing_line}")
    print(f"           verdict      -> {verdict}")
    print()
    print("DETECTED -- arm_coverage sees a missing arm" if detected
          else "*** MISSED -- WE ARE BLIND TO A MISSING ARM (D14 has no cover) ***")
    return 0


if __name__ == "__main__":
    sys.exit(main())
