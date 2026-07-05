"""Build the immutable GOLD data panel (FINAL_PLAN data build).

Purpose
-------
Run the 13-stage data pipeline (``src/data/pipeline.py``) over the entitled
universe and emit immutable, checksummed artifacts under ``data/gold/``.

What it WILL do (acceptance criteria):
  1. Read the data config (default ``config/data.yaml``).
  2. Run all 13 pipeline stages on the entitled universe (no look-ahead).
  3. Write immutable artifacts (panel, membership, splits, delisting returns).
  4. Compute and persist SHA-256 checksums for every artifact (manifest).
  5. Refuse to overwrite an existing gold build unless forced.

Flags
-----
  --config   Path to the data config (default config/data.yaml).
"""

from __future__ import annotations


import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build the immutable gold data panel (FINAL_PLAN data build).",
    )
    parser.add_argument("--config", default="config/data.yaml")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    print("[build_gold] planned actions:")
    print(f"  1. Load config from {args.config}.")
    print("  2. Run the 13-stage pipeline (src/data/pipeline.py) on entitled universe.")
    print("  3. Emit immutable artifacts to data/gold/.")
    print("  4. Compute + persist SHA-256 checksum manifest.")

    # final-audit #29: the REAL gold is built by the self-contained data_pipeline/ package
    # (data_pipeline/src/data/cli.py + panel.build_gold), NOT this deferred stub. Reference the real
    # symbol so the guard message is accurate (src/data/pipeline.py exposes GoldPipeline, never run_pipeline).
    try:
        from src.data.pipeline import GoldPipeline  # noqa: F401
    except ImportError as exc:  # pragma: no cover - stub guard
        print(f"[build_gold] NOTE: deferred stub — build via data_pipeline/ ({exc}).")

    # TODO(FINAL_PLAN data build): implement.
    #   - load yaml config; resolve entitled universe.
    #   - run_pipeline(config) -> 13 stages, returning artifact paths.
    #   - hash each artifact; write data/gold/checksums.json (or .sha256).
    #   - guard against clobbering an existing immutable build.
    # C4 NOTE: this BUILD is a stub — the REAL gold is built by the self-contained data_pipeline/
    # package (data_pipeline/build_universe). VALIDATION of a rebuilt panel is a WORKING executable:
    # `python scripts/verify_gold.py` byte-diffs the candidate vs frozen univ3 over the 2005-2025
    # overlap (src.data.validation.panel_overlap_diff). Do NOT rely on this build stub for validation.
    raise SystemExit("STUB — build via data_pipeline/build_universe; validate via scripts/verify_gold.py")


if __name__ == "__main__":
    main()
