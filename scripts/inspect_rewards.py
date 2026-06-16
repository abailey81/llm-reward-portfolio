"""Qualitative reward inspection (FINAL_PLAN Phase 4.C).

Purpose
-------
Open the black box of LLM-authored reward functions: summarize what the model
wrote across generations, trace how its responses tracked distributional
feedback, and surface failure modes through the reward-hacking lens.

What it WILL produce (acceptance criteria for Phase 4.C):
  1. A per-generation summary of the reward functions the LLM authored
     (structure, terms, complexity, drift across generations).
  2. A trace linking LLM responses to the distributional feedback signals they
     were given (did edits follow the feedback?).
  3. A failure-mode catalogue framed by the reward-hacking literature
     (Skalse et al. on reward gaming; Hadfield-Menell et al. on misspecified /
     proxy rewards) — e.g. specification gaming, proxy exploitation, tautology.

Flags
-----
  --results-dir   Archived runs directory (default outputs/runs).
  --out-dir       Where to write the qualitative report (default outputs/tables).
"""

from __future__ import annotations


import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect LLM-authored rewards (FINAL_PLAN Phase 4.C).",
    )
    parser.add_argument("--results-dir", default="outputs/runs")
    parser.add_argument("--out-dir", default="outputs/tables")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    print("[inspect_rewards] Phase 4.C — planned actions:")
    print(f"  1. Load LLM reward artifacts from {args.results_dir}.")
    print("  2. Summarize what the LLM wrote across generations.")
    print("  3. Trace responses to the distributional feedback they were given.")
    print("  4. Catalogue failure modes via the reward-hacking lens "
          "(Skalse, Hadfield-Menell).")
    print(f"  5. Write the qualitative report to {args.out_dir}.")

    try:
        from src.io.results import ResultStore  # noqa: F401
        from src.feedback import distributional  # noqa: F401
    except ImportError as exc:  # pragma: no cover - stub guard
        print(f"[inspect_rewards] NOTE: a results/feedback module is missing ({exc}).")

    # TODO(FINAL_PLAN Phase 4.C): implement.
    #   - collect reward source + LLM prompts/responses per generation.
    #   - diff successive generations; correlate edits with feedback deltas.
    #   - tag candidates against a reward-hacking taxonomy; tabulate failures.
    #   - emit a markdown report into out_dir.
    raise SystemExit("STUB — implement per FINAL_PLAN Phase 4.C")


if __name__ == "__main__":
    main()
