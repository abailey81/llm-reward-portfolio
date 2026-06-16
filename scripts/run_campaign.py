"""Campaign orchestration (FINAL_PLAN 3.A).

Purpose
-------
Launch the full experimental campaign: the cross product of
arms x candidates x seeds x folds defined in ``config/campaign.yaml``. Each run
is independent and archived by run id via ``src/io/results.py``.

What it WILL do (acceptance criteria for 3.A):
  1. Read ``config/campaign.yaml`` and expand the arms x candidates x seeds x
     folds grid into a list of runs, each with a deterministic run id.
  2. Launch independent runs (sequentially or in parallel).
  3. Archive each run via ``src/io/results.py`` keyed by run id.
  4. --resume is idempotent: skip runs already archived as complete.
  5. --dry-run executes a tiny grid (2 arms, 2 candidates, 1 seed, 1 fold).
  6. On full completion, auto-shutdown the host (for rented GPUs).

Flags
-----
  --config         Campaign config (default config/campaign.yaml).
  --resume         Skip already-completed runs (idempotent).
  --dry-run        Tiny grid: 2 arms, 2 candidates, 1 seed, 1 fold.
  --no-shutdown    Disable auto-shutdown on completion.
"""

from __future__ import annotations


import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the experimental campaign (FINAL_PLAN 3.A).",
    )
    parser.add_argument("--config", default="config/campaign.yaml")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip runs already archived as complete (idempotent).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Tiny grid: 2 arms, 2 candidates, 1 seed, 1 fold.",
    )
    parser.add_argument(
        "--no-shutdown",
        action="store_true",
        help="Do not auto-shutdown the host on completion.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    print("[run_campaign] FINAL_PLAN 3.A — planned actions:")
    print(f"  1. Read {args.config} and expand the run grid.")
    if args.dry_run:
        print("     (DRY-RUN grid: 2 arms x 2 candidates x 1 seed x 1 fold)")
    print("  2. Launch independent runs.")
    print("  3. Archive each via src/io/results.py keyed by run id.")
    print(f"  4. Resume mode: {'ON (skip completed)' if args.resume else 'OFF'}.")
    print(
        f"  5. Auto-shutdown on completion: "
        f"{'DISABLED' if args.no_shutdown else 'ENABLED'}."
    )

    try:
        from src.io.results import ResultStore  # noqa: F401
    except ImportError as exc:  # pragma: no cover - stub guard
        print(f"[run_campaign] NOTE: src.io.results not yet implemented ({exc}).")

    # TODO(FINAL_PLAN 3.A): implement.
    #   - parse campaign.yaml; build grid (override sizes if --dry-run).
    #   - for each run: compute run id; if --resume and complete -> skip.
    #   - execute the run; archive results via ResultStore keyed by run id.
    #   - on full completion and not --no-shutdown: shut down the host.
    raise SystemExit("STUB — implement per FINAL_PLAN 3.A")


if __name__ == "__main__":
    main()
