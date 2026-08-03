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

import ctypes
import os
import random
import shutil
import sys
from ctypes import wintypes
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.cluster import lanes                      # noqa: E402
from src.utils.config import load_config           # noqa: E402

ROOT = Path("outputs/campaign_cluster_run4")
FLOOR_GB = 20.0          # scripts/sentinel.py::check_disk and docs/ops/session_preflight.py agree
SAMPLE = 400

_KERNEL32 = ctypes.WinDLL("kernel32", use_last_error=True) if os.name == "nt" else None


def _on_disk_bytes(path: str) -> int:
    """Bytes the file actually OCCUPIES — which is the only quantity the floor cares about.

    ⚠ THE ARCHIVE IS NTFS-COMPRESSED (RUN 15, 2026-08-03; measured 1.7:1 over 36,123 files).
    ``os.path.getsize`` returns the LOGICAL length, so using it here overstates the footprint
    by the whole compression ratio and forecasts a ceiling that does not exist — it reported
    rung 568 as below the floor when the compressed ladder in fact clears it by ~6.7 GB.
    ``GetCompressedFileSizeW`` returns the allocated size and is correct for both compressed
    and uncompressed files, so this needs no flag and cannot drift out of step with reality.
    """
    if _KERNEL32 is None:                                    # non-Windows: st_blocks is allocation
        try:
            return os.stat(path).st_blocks * 512             # type: ignore[attr-defined]
        except (OSError, AttributeError):
            return os.path.getsize(path)
    fn = _KERNEL32.GetCompressedFileSizeW
    fn.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(wintypes.DWORD)]
    fn.restype = wintypes.DWORD
    high = wintypes.DWORD(0)
    low = fn(path, ctypes.byref(high))
    if low == 0xFFFFFFFF and ctypes.get_last_error() != 0:   # INVALID_FILE_SIZE *and* a real error
        return os.path.getsize(path)                          # fail OPEN to the conservative number
    return (high.value << 32) | low


def measure_unit_bytes() -> tuple[float, float, int]:
    """Mean ON-DISK and LOGICAL bytes per UNIT directory, sampled from the live archive.

    Returns ``(mean_on_disk, mean_logical, n_units)``. The forecast uses the on-disk figure;
    the logical one is reported alongside so the compression ratio is visible rather than
    silently baked into a number nobody can check.
    """
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
        return 0.0, 0.0, 0
    rng = random.Random(0)                    # deterministic sample -> reproducible number
    pick = units if len(units) <= SAMPLE else rng.sample(units, SAMPLE)
    tot_disk = 0
    tot_logical = 0
    for u in pick:
        for dirpath, _d, files in os.walk(u):
            for fn in files:
                p = os.path.join(dirpath, fn)
                try:
                    tot_logical += os.path.getsize(p)
                    tot_disk += _on_disk_bytes(p)
                except OSError:
                    pass
    return tot_disk / len(pick), tot_logical / len(pick), len(units)


def main() -> int:
    mean_b, mean_logical, n_units = measure_unit_bytes()
    if not mean_b:
        print("no test units found -- nothing to measure")
        return 2
    free_gb = shutil.disk_usage(str(Path.cwd())).free / 1e9     # DECIMAL GB, the repo's convention
    cfg = load_config("campaign")   # load_config takes a STEM, not a path
    tiers = (((cfg.get("seeds") or {}).get("tiers")) or [30, 100, 189, 279, 340, 403, 568])

    have = sum(1 for _ in ROOT.rglob("record.json"))
    ratio = (mean_logical / mean_b) if mean_b else 1.0
    print(f"measured mean unit size : {mean_b/1e6:.3f} MB ON DISK   (sampled {min(SAMPLE, n_units)} of {n_units} test units)")
    print(f"                          {mean_logical/1e6:.3f} MB logical -> compression {ratio:.2f} to 1")
    if ratio > 1.05:
        print("                          (the archive is NTFS-compressed; the ROOT carries the attribute,")
        print("                           so .pull_tmp staging inherits it and NEW records land compressed)")
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
        print("machine does not have, so the ladder is disk-capped there.")
        print()
        print("*** DO NOT 'MOVE THE ARCHIVE' -- an earlier version of this message advised exactly that,")
        print("   and it is WRONG. src/cluster/poll.py:305 commits every pulled record with os.rename,")
        print("   whose stated correctness argument is 'same filesystem by construction'. Junctioning")
        print("   the archive (or any leg sub-root) onto another volume makes that rename raise")
        print("   OSError winerror=17, and poll.py:306's except-branch rmtree's the record -- every")
        print("   pulled record silently DELETED while the driver reports a successful pull. Measured")
        print("   2026-08-03; see docs/DEFERRED_FIXES_RUN4.md 'PROHIBITION'.")
        print()
        print("   THE SAFE LEVERS, in order: (1) NTFS-compress the archive root -- transparent, byte-")
        print("   identical, reversible, and NEW records inherit it (measured 1.7:1, no sweep-time")
        print("   cost); (2) relocate INERT trees (caches, literature, .venv-lseg) behind verified")
        print("   junctions; (3) move the pagefile to D: -- one registry value + one reboot, ~12 GB.")
    print()
    print("NOTE ON THE RATE. A GB/h figure measured during C1 does not forecast C4 and must not be")
    print("used for one: C1 writes a handful of records at a time, C4 multiplies every unit by the")
    print("tier. This table is a function of RECORDS, which is the quantity that actually scales.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
