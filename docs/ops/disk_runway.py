"""DISK RUNWAY — at which seed rung does C: cross the 20 GB floor? Measured, not assumed.

WHY (RUN 13, 2026-08-02). The disk guard reports a LEVEL ("26.5 GB free, floor 20") and a RATE
("-0.02 GB/h"), and both are reassuring right now for the same reason the core count was low: the
campaign is still in C1, where records arrive a handful at a time. C4 is where the archive actually
grows -- the seed ladder multiplies every unit by the tier -- so a rate measured during C1 forecasts
nothing about C4, and a level says nothing at all.

The honest question is not "how much is free" but "how many records fit, and which RUNG is that".
This computes it from three measured quantities and no guesses:

  * the MEAN ON-DISK SIZE of a unit directory (record.json + env.json + reward.py), measured over a
    sample of the real archive rather than taken from the "~480 KB each" that circulates in the docs;
  * the registered ladder, from `config/campaign.yaml`;
  * `lanes.total_trainings(rung)`, the campaign-wide record count at a rung -- the SAME function the
    sentinel's rung forecast uses, so the two cannot come to disagree about the same fact.

⚠ THE COUPLING THAT MAKES THIS URGENT RATHER THAN INTERESTING. D27 would take days off the critical
path, which means the campaign reaches HIGHER rungs, which means it meets this wall SOONER. Speed and
disk are not independent decisions and must not be taken separately.

Read-only: it stats files and reads config. It never opens a record's contents.
"""
from __future__ import annotations

import os
import random
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.cluster import lanes                      # noqa: E402
from src.utils.config import load_config           # noqa: E402

ROOT = Path("outputs/campaign_cluster_run4")
FLOOR_GB = 20.0          # scripts/sentinel.py::check_disk and docs/ops/session_preflight.py agree
SAMPLE = 400


def measure_unit_bytes() -> tuple[float, int]:
    """Mean bytes per UNIT directory, sampled from the live archive."""
    units = []
    for r in ROOT.glob("test*"):
        if not r.is_dir():
            continue
        for arm in r.iterdir():
            if not arm.is_dir() or arm.name.startswith((".", "_")):
                continue
            for u in arm.iterdir():
                if u.is_dir() and (u / "record.json").is_file():
                    units.append(u)
    if not units:
        return 0.0, 0
    rng = random.Random(0)                    # deterministic sample -> reproducible number
    pick = units if len(units) <= SAMPLE else rng.sample(units, SAMPLE)
    tot = 0
    for u in pick:
        for dirpath, _d, files in os.walk(u):
            for fn in files:
                try:
                    tot += os.path.getsize(os.path.join(dirpath, fn))
                except OSError:
                    pass
    return tot / len(pick), len(units)


def main() -> int:
    mean_b, n_units = measure_unit_bytes()
    if not mean_b:
        print("no test units found -- nothing to measure")
        return 2
    free_gb = shutil.disk_usage(str(Path.cwd())).free / 1e9     # DECIMAL GB, the repo's convention
    cfg = load_config("campaign")   # load_config takes a STEM, not a path
    tiers = (((cfg.get("seeds") or {}).get("tiers")) or [30, 100, 189, 279, 340, 403, 568])

    have = sum(1 for _ in ROOT.rglob("record.json"))
    print(f"measured mean unit size : {mean_b/1e6:.3f} MB   (sampled {min(SAMPLE, n_units)} of {n_units} test units)")
    print(f"records on disk now     : {have:,}")
    print(f"C: free                 : {free_gb:.1f} GB (decimal), CRITICAL floor {FLOOR_GB:.0f}")
    print()
    print(f"{'rung':>6} {'total records':>14} {'still to write':>15} {'GB needed':>11} {'GB left after':>15}  verdict")
    crossed = None
    for rung in tiers:
        total = lanes.total_trainings(rung)
        todo = max(0, total - have)
        need = todo * mean_b / 1e9
        left = free_gb - need
        ok = left >= FLOOR_GB
        if not ok and crossed is None:
            crossed = rung
        print(f"{rung:>6} {total:>14,} {todo:>15,} {need:>11.1f} {left:>15.1f}  "
              f"{'ok' if ok else '*** BELOW THE FLOOR ***'}")
    print()
    if crossed is None:
        print("The full ladder fits above the floor on the CURRENT free space.")
    else:
        print(f"THE FLOOR IS CROSSED AT RUNG {crossed}. Every rung at or above it needs space this")
        print("machine does not have, so the ladder is disk-capped there unless the archive moves.")
        print("Relocating it is a 12-line relaunch, which is Tamer's call -- and it is COUPLED to D27:")
        print("a faster campaign reaches the capped rung sooner, not later.")
    print()
    print("NOTE ON THE RATE. A GB/h figure measured during C1 does not forecast C4 and must not be")
    print("used for one: C1 writes a handful of records at a time, C4 multiplies every unit by the")
    print("tier. This table is a function of RECORDS, which is the quantity that actually scales.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
