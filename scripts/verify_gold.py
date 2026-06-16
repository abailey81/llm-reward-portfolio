"""Verify the GOLD data panel (FINAL_PLAN data verification).

Purpose
-------
Independent verification that the built gold panel is sound and matches the
pre-registration before it is used in any campaign run.

What it WILL check (acceptance criteria — all must pass):
  1. Checksums: every artifact matches the recorded SHA-256 manifest.
  2. Split boundaries byte-match the pre-registered split definition.
  3. Membership reconciliation: index membership ties out over time.
  4. Delisting returns are present (no survivorship gaps).
  5. Environment no-look-ahead test passes on the built panel.
  6. Reward-timing test passes on the built panel.

Flags
-----
  --config   Path to the data config (default config/data.yaml).
"""

from __future__ import annotations


import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify the gold data panel (FINAL_PLAN data verification).",
    )
    parser.add_argument("--config", default="config/data.yaml")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    print("[verify_gold] planned checks:")
    print(f"  (config: {args.config})")
    print("  1. Checksums match recorded manifest.")
    print("  2. Split boundaries byte-match pre-registration.")
    print("  3. Membership reconciliation ties out.")
    print("  4. Delisting returns present.")
    print("  5. Env no-look-ahead test passes.")
    print("  6. Reward-timing test passes.")

    try:
        from src.env.portfolio import PortfolioEnv  # noqa: F401
    except ImportError as exc:  # pragma: no cover - stub guard
        print(f"[verify_gold] NOTE: src.env.portfolio not yet implemented ({exc}).")

    # TODO(FINAL_PLAN data verification): implement.
    #   - recompute hashes vs data/gold/checksums.json.
    #   - load preregistration.yaml splits; assert byte-identical boundaries.
    #   - reconcile membership table; assert delisting returns non-null.
    #   - run env look-ahead + reward-timing assertions on the panel.
    #   - aggregate pass/fail; exit non-zero on any failure.
    raise SystemExit("STUB — implement per FINAL_PLAN data verification")


if __name__ == "__main__":
    main()
