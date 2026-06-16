"""Results analysis and selection-aware inference (FINAL_PLAN Phase 4.B).

Purpose
-------
Load archived campaign results and produce the primary hypothesis tests with
honest, selection-aware inference, writing publication tables to
``outputs/tables/``.

What it WILL produce (acceptance criteria for Phase 4.B):
  Hypotheses:
    H1  — primary effect.
    H2  — reward vs {scalar, placebo, scalar_cvar5}.
    H3  — secondary effect.
    H4a / H4b — sub-hypotheses + secondary critic comparison.
  Selection-aware inference:
    - PBO / CSCV (probability of backtest overfitting).
    - DSR (deflated Sharpe ratio).
    - Bootstrap difference tests (paired, block).
    - FDR control across the hypothesis family.
    - rliable aggregate metrics + stratified bootstrap CIs.
  Outputs:
    - Tables written to outputs/tables/.

Flags
-----
  --results-dir   Archived runs directory (default outputs/runs).
  --out-dir       Tables output directory (default outputs/tables).
"""

from __future__ import annotations


import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze campaign results (FINAL_PLAN Phase 4.B).",
    )
    parser.add_argument("--results-dir", default="outputs/runs")
    parser.add_argument("--out-dir", default="outputs/tables")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    print("[analyze_results] Phase 4.B — planned actions:")
    print(f"  1. Load archived results from {args.results_dir} via src/io/results.py.")
    print("  2. Test H1, H2 (vs scalar/placebo/scalar_cvar5), H3, H4a, H4b + critic.")
    print("  3. Selection-aware inference: PBO/CSCV, DSR, bootstrap diff, FDR, rliable.")
    print(f"  4. Write tables to {args.out_dir}.")

    try:
        from src.io.results import ResultStore  # noqa: F401
        from src.selection import cscv  # noqa: F401
    except ImportError as exc:  # pragma: no cover - stub guard
        print(f"[analyze_results] NOTE: a results/selection module is missing ({exc}).")

    # TODO(FINAL_PLAN Phase 4.B): implement.
    #   - load runs into a tidy frame keyed by arm/candidate/seed/fold.
    #   - per hypothesis: effect estimate + paired/block bootstrap difference.
    #   - PBO via CSCV; DSR per selected config; FDR across the family.
    #   - rliable aggregate scores with stratified-bootstrap CIs.
    #   - render LaTeX/markdown tables into out_dir.
    raise SystemExit("STUB — implement per FINAL_PLAN Phase 4.B")


if __name__ == "__main__":
    main()
