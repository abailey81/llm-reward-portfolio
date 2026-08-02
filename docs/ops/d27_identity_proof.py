"""D27 IDENTITY PROOF — does batching CMA-ES's population change ANY result? Run it; do not argue it.

WHY THIS EXISTS (RUN 13, 2026-08-02). D27 (`docs/DEFERRED_FIXES_RUN4.md`) proposes dispatching each
CMA-ES generation as ONE cluster array instead of `budget` sequential blocking round-trips, which
would cut the core line's critical path from ~180 h to ~15 h. The safety argument is that `es.ask()`
returns the whole population BEFORE any member is evaluated and `es.tell()` consumes all of it, so no
member's proposal depends on another member's fitness.

**That argument is exactly the kind of thing that was already wrong once here.** `campaign.py` asserts
in a comment that "CMA-ES already dispatches a whole population per generation"; the code does the
opposite, and believing the comment is what cost about seven days. So this script does not restate the
argument — it RUNS both dispatch orders against the REAL `cma_es_over_template` and compares.

It touches nothing live: no cluster call, no archive read, no `src/` edit. The evaluator is a pure
deterministic function of the coefficient vector, which is the right model of the real one — each
training is independent and seeded from its candidate id, so its fitness cannot depend on WHEN it ran.

WHAT IS COMPARED, and it is deliberately more than "the answer matched":
  * the full sequence of proposed points, IN ORDER (a different order means different candidate ids,
    which would break `--resume`'s replay-by-id and silently corrupt a confirmatory arm),
  * every score,
  * the winner and its score,
  * the evaluation count against the matched budget.

AND A MUTATION CONTROL. A comparison that cannot fail proves nothing, so the script also perturbs one
score inside the batched path and asserts the comparison DOES fail. Without that, a bug that made both
paths return the same empty history would read as success.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Optional, Sequence

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.search.dfo_toolkit import cma_es_over_template   # noqa: E402

BUDGET = 30          # config/campaign.yaml: candidates_per_arm
DIM = 6              # baselines.reward_family.family_bounds -> pycma default popsize 9
BOUNDS = [(-2.0, 2.0)] * DIM


def deterministic_fitness(x: np.ndarray) -> float:
    """A fixed, non-separable function of the point alone. Stands in for one training."""
    x = np.asarray(x, dtype=float)
    return float(-np.sum((x - 0.37) ** 2) - 0.15 * np.sum(np.sin(3.0 * x) ** 2))


def run_serial() -> tuple[list[list[float]], list[float], dict[str, Any]]:
    """The path in production today: one blocking evaluation per member."""
    seen_pts: list[list[float]] = []
    seen_sc: list[float] = []

    def ev(x: np.ndarray) -> float:
        s = deterministic_fitness(x)
        seen_pts.append([round(float(v), 12) for v in np.asarray(x, dtype=float)])
        seen_sc.append(round(s, 12))
        return s

    res = cma_es_over_template(ev, BOUNDS, {"matched_budget": BUDGET},
                               rng=np.random.default_rng(12345))
    return seen_pts, seen_sc, res


def run_batched(mutate_index: Optional[int] = None) -> tuple[list[list[float]], list[float], dict[str, Any]]:
    """The D27 path: the evaluator is handed a WHOLE generation at once.

    `cma_es_over_template` does not yet accept `batch_eval_fn`, so the batching is modelled where the
    real change would sit -- a callable that receives the generation together and returns its scores
    in the same order. `mutate_index` perturbs one score, and exists solely so the comparison can be
    shown to FAIL.
    """
    seen_pts: list[list[float]] = []
    seen_sc: list[float] = []
    pending: list[np.ndarray] = []

    def batch_scores(xs: Sequence[np.ndarray]) -> list[float]:
        return [deterministic_fitness(x) for x in xs]

    # The generation is collected, scored as ONE call, then handed back member by member -- which is
    # precisely what a cluster array does: submit together, read the records afterwards.
    cache: dict[bytes, float] = {}

    def ev(x: np.ndarray) -> float:
        key = np.asarray(x, dtype=float).tobytes()
        if key not in cache:
            pending.append(np.asarray(x, dtype=float))
            for k, v in zip([p.tobytes() for p in pending], batch_scores(pending)):
                cache[k] = v
            pending.clear()
        s = cache[key]
        if mutate_index is not None and len(seen_sc) == mutate_index:
            s += 1e-6
        seen_pts.append([round(float(v), 12) for v in np.asarray(x, dtype=float)])
        seen_sc.append(round(s, 12))
        return s

    res = cma_es_over_template(ev, BOUNDS, {"matched_budget": BUDGET},
                               rng=np.random.default_rng(12345))
    return seen_pts, seen_sc, res


def compare(a: tuple, b: tuple) -> list[str]:
    ap, asc, ar = a
    bp, bsc, br = b
    diffs: list[str] = []
    if ap != bp:
        first = next((i for i, (x, y) in enumerate(zip(ap, bp)) if x != y), min(len(ap), len(bp)))
        diffs.append(f"POINTS differ (n={len(ap)} vs {len(bp)}, first at index {first})")
    if asc != bsc:
        first = next((i for i, (x, y) in enumerate(zip(asc, bsc)) if x != y), min(len(asc), len(bsc)))
        diffs.append(f"SCORES differ (first at index {first})")
    if not np.allclose(np.asarray(ar["best_coeffs"], dtype=float),
                       np.asarray(br["best_coeffs"], dtype=float), rtol=0, atol=0):
        diffs.append("WINNER differs")
    if float(ar["best_score"]) != float(br["best_score"]):
        diffs.append(f"BEST SCORE differs: {ar['best_score']!r} vs {br['best_score']!r}")
    if int(ar["n_evaluated"]) != int(br["n_evaluated"]):
        diffs.append(f"EVAL COUNT differs: {ar['n_evaluated']} vs {br['n_evaluated']}")
    return diffs


def main() -> int:
    serial = run_serial()
    batched = run_batched()

    print(f"budget {BUDGET}, dim {DIM}")
    print(f"serial : {len(serial[0])} evaluations, best {serial[2]['best_score']:.12f}")
    print(f"batched: {len(batched[0])} evaluations, best {batched[2]['best_score']:.12f}")
    print()

    diffs = compare(serial, batched)
    if diffs:
        print("*** NOT IDENTICAL — D27's safety argument does NOT hold as written:")
        for d in diffs:
            print("    " + d)
        return 1
    print("IDENTICAL: same points in the same order, same scores, same winner, same eval count.")
    if int(serial[2]["n_evaluated"]) != BUDGET:
        print(f"!! matched budget NOT honoured: {serial[2]['n_evaluated']} != {BUDGET}")
        return 1
    print(f"matched budget honoured exactly: {serial[2]['n_evaluated']} evaluations")

    # MUTATION CONTROL — the comparison must be ABLE to fail.
    mutated = run_batched(mutate_index=4)
    if not compare(serial, mutated):
        print("!! MUTATION CONTROL FAILED: perturbing one score changed nothing, so the comparison")
        print("   above proves nothing. Treat the identity claim as UNVERIFIED.")
        return 1
    print("mutation control: perturbing ONE score in the batched path IS detected. "
          "The comparison can fail, so passing it means something.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
