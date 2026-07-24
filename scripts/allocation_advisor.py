"""The adaptive allocation advisor CLI — one command = the current optimal launch settings.

Usage (GO morning, or any time during the campaign):
    python scripts/allocation_advisor.py                       # live snapshot -> the plan
    python scripts/allocation_advisor.py --probe-age-hours 30  # age the U/V probe verdict
    python scripts/allocation_advisor.py --vram-per-training 2.8 --rate 700 \
        --remaining "tier403=6800,legs=3000"                   # canary-measured facts -> ETAs

Prints the PLAN (regime, chunk-tasks, search-lane pool, the exact --seed-pool-blocks string,
pack depths, ETAs) and appends the raw snapshot to outputs/myriad_telemetry.jsonl. Advisory
only: nothing is submitted, nothing is altered, priorities are never touched.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cluster.allocation import advise  # noqa: E402
from src.cluster.telemetry import (append_log, collect, contention_trend,  # noqa: E402
                                   measure_rate, observed_gpus)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default="myriad")
    ap.add_argument("--probe-age-hours", type=float, default=0.0,
                    help="Hours since the U/V probes were submitted (drives the 48h verdict).")
    ap.add_argument("--vram-per-training", type=float, default=None,
                    help="Canary-measured GB per training; unlocks pack>5 recommendations.")
    ap.add_argument("--rate", type=float, default=None,
                    help="Measured trainings/day from the live archive; unlocks ETAs.")
    ap.add_argument("--remaining", default=None,
                    help='Milestones as "name=count,...", e.g. "tier403=6800,legs=3000".')
    ap.add_argument("--archive-root", default=None,
                    help="Live archive root: AUTO-measures the rate + the granted GPU models "
                         "(supersedes --rate when records exist).")
    ap.add_argument("--prev-regime", choices=["CONTENDED", "QUIET"], default=None,
                    help="The previous plan regime (the hysteresis anchor).")
    args = ap.parse_args(argv)

    remaining = None
    if args.remaining:
        remaining = {}
        for part in args.remaining.split(","):
            k, v = part.split("=", 1)
            remaining[k.strip()] = int(v)

    snap = collect(args.host, probe_age_hours=args.probe_age_hours)
    append_log(snap)

    rate = args.rate
    if args.archive_root:
        measured, n = measure_rate(args.archive_root)
        if n:
            rate = measured
            print(f"[self-measured] {n} records -> {measured:.0f} trainings/day; granted GPUs "
                  f"so far: {observed_gpus(args.archive_root) or 'none archived'}")
    plan = advise(snap,
                  measured_vram_per_training_gb=args.vram_per_training,
                  remaining_trainings=remaining,
                  measured_trainings_per_day=rate,
                  prev_regime=args.prev_regime)
    print(f"[telemetry {snap.ts}] pools free: {snap.pool_free} | cluster qw: {snap.cluster_qw} "
          f"({snap.cluster_users} users) | our jobs: {len(snap.our_jobs)}")
    print(f"CONTENTION TREND: {contention_trend()}")
    print(plan.render())
    return 0


if __name__ == "__main__":
    sys.exit(main())
