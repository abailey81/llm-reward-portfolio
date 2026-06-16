"""Pre-registration freeze (FINAL_PLAN Phase 1.E).

Purpose
-------
Lock the experimental design before any results are seen. Stages the
pre-registration artifacts, hashes them, and records the hash + the Phase-0
pass precondition into the immutable decision log.

What it WILL do (acceptance criteria for Phase 1.E):
  1. Stage ``PREREGISTRATION.md`` and ``config/preregistration.yaml``.
  2. Compute a SHA-256 over the staged bytes (canonical, order-stable).
  3. Write the hash into ``docs/DECISION_LOG.md`` with a UTC timestamp.
  4. Record the Phase-0 GATE pass as an explicit precondition (refuse to freeze
     if Phase 0 has not gone GREEN/AMBER).
  --check verifies the CURRENT files hash to the recorded value (no rewrite).

Flags
-----
  --check   Verify current hash matches the recorded one; non-zero exit on drift.
"""

from __future__ import annotations


import argparse

PREREG_MD = "PREREGISTRATION.md"
PREREG_YAML = "config/preregistration.yaml"
DECISION_LOG = "docs/DECISION_LOG.md"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Freeze / verify the pre-registration (FINAL_PLAN Phase 1.E).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the current files match the recorded SHA-256 (no rewrite).",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.check:
        print("[freeze] --check — planned actions:")
        print(f"  1. Recompute SHA-256 over {PREREG_MD} + {PREREG_YAML}.")
        print(f"  2. Compare against the value recorded in {DECISION_LOG}.")
        print("  3. Exit non-zero on any drift.")
    else:
        print("[freeze] Phase 1.E — planned actions:")
        print(f"  1. Stage {PREREG_MD} and {PREREG_YAML}.")
        print("  2. Compute canonical SHA-256 over staged bytes.")
        print(f"  3. Write hash + UTC timestamp into {DECISION_LOG}.")
        print("  4. Record the Phase-0 pass precondition (refuse if not passed).")

    # TODO(FINAL_PLAN Phase 1.E): implement.
    #   - hashlib.sha256 over sorted, normalized file bytes.
    #   - confirm Phase-0 status (e.g. a marker written by smoke_test) before write.
    #   - on --check: parse recorded hash from DECISION_LOG, compare, exit code.
    raise SystemExit("STUB — implement per FINAL_PLAN Phase 1.E")


if __name__ == "__main__":
    main()
