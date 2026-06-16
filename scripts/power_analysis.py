"""Statistical power analysis (FINAL_PLAN B-5).

Purpose
-------
Compute the design-time power numbers that justify the campaign size and
write them into ``docs/POWER_ANALYSIS.md``. This must run BEFORE the freeze so
the pre-registered trial count is defensible.

What it WILL produce (acceptance criteria for B-5):
  1. The count of INDEPENDENT regimes available (drives effective n).
  2. A simulated power curve for H2 (reward beats scalar/placebo) as a function
     of effect size.
  3. The minimum detectable effect (MDE) at the target power (e.g. 0.80) and
     alpha (e.g. 0.05), accounting for the selection-aware penalty.
  4. An explicit, justified trial count (arms x candidates x seeds x folds)
     written back to the doc.

Flags
-----
  --target-power   Desired power (default 0.80).
  --alpha          Significance level (default 0.05).
  --n-sims         Monte Carlo simulations per effect size (default 10000).
  --out            Output markdown path (default docs/POWER_ANALYSIS.md).
"""

from __future__ import annotations


import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Power analysis for the campaign (FINAL_PLAN B-5).",
    )
    parser.add_argument("--target-power", type=float, default=0.80)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--n-sims", type=int, default=10000)
    parser.add_argument("--out", default="docs/POWER_ANALYSIS.md")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    print("[power_analysis] B-5 — planned actions:")
    print("  1. Count independent regimes (effective sample size).")
    print(f"  2. Simulate H2 power vs effect size ({args.n_sims} sims/point).")
    print(
        f"  3. Compute MDE at power={args.target_power}, alpha={args.alpha} "
        "with selection-aware penalty."
    )
    print("  4. Emit an explicit, justified trial count.")
    print(f"  5. Write numbers to {args.out}.")

    try:
        from src.regimes import detect  # noqa: F401
    except ImportError as exc:  # pragma: no cover - stub guard
        print(f"[power_analysis] NOTE: src.regimes not yet implemented ({exc}).")

    # TODO(FINAL_PLAN B-5): implement.
    #   - load regime labels; count independent (non-overlapping) regimes.
    #   - Monte Carlo: sample paired diffs at each effect size; apply the
    #     selection correction; estimate power; locate MDE at target_power.
    #   - render a markdown table and overwrite args.out.
    raise SystemExit("STUB — implement per FINAL_PLAN B-5")


if __name__ == "__main__":
    main()
