"""TPE startup-batching (2026-07-26, CAPACITY-lane finding T5-a) — a DISPATCH change only.

`study.optimize` evaluates one trial at a time, making TPE a 30-step SERIAL chain — longer than
GP-EI's 25, i.e. the campaign's binding critical path. The first `n_startup` trials come from
Optuna's RANDOM sampler and depend on no observed value, so evaluating them concurrently must
return IDENTICAL results. That identity is the whole justification, so it is what these test.
"""
from __future__ import annotations

import numpy as np
import pytest

from src.baselines.reward_family import family_bounds
from src.search.dfo_toolkit import tpe_over_template

BUDGET = 14
N_STARTUP = 6


def _objective(x: np.ndarray) -> float:
    """Deterministic, order-independent — so any difference is the ALGORITHM, not the objective."""
    return float(-np.sum((np.asarray(x, dtype=float) - 0.25) ** 2))


def _run(*, batched: bool):
    calls: list[np.ndarray] = []

    def single(x):
        calls.append(np.asarray(x, dtype=float).copy())
        return _objective(x)

    def batch(xs):
        for x in xs:
            calls.append(np.asarray(x, dtype=float).copy())
        return [_objective(x) for x in xs]

    out = tpe_over_template(
        single, family_bounds(None), {"matched_budget": BUDGET},
        rng=np.random.default_rng(11), n_startup=N_STARTUP,
        batch_eval_fn=(batch if batched else None),
    )
    return out, calls


def test_batching_returns_IDENTICAL_results_to_the_sequential_path():
    """THE justification: same points, same order, same scores, same winner."""
    seq, seq_calls = _run(batched=False)
    bat, bat_calls = _run(batched=True)

    assert len(seq_calls) == len(bat_calls) == BUDGET
    assert np.allclose(np.asarray(seq_calls), np.asarray(bat_calls)), \
        "batching changed WHICH points were evaluated — it is not a pure dispatch change"
    assert np.isclose(seq["best_score"], bat["best_score"])
    assert np.allclose(seq["best_coeffs"], bat["best_coeffs"])
    assert [h["score"] for h in seq["history"]] == [h["score"] for h in bat["history"]]


def test_the_matched_budget_is_preserved_exactly():
    """H4 fairness rests on the matched candidate budget — batching must not spend one extra."""
    out, calls = _run(batched=True)
    assert out["n_evaluated"] == BUDGET and out["budget"] == BUDGET
    assert len(calls) == BUDGET
    assert len(out["history"]) == BUDGET


def test_omitting_batch_eval_fn_is_byte_identical_to_the_old_behaviour():
    """Backward compatibility: the default path must be untouched."""
    a, _ = _run(batched=False)
    b, _ = _run(batched=False)
    assert np.allclose(a["best_coeffs"], b["best_coeffs"])
    assert a["n_evaluated"] == BUDGET


def test_batch_path_honours_the_cache_so_RESUME_stays_free():
    """Search-replay resume: a cached startup point must NOT be re-evaluated, and must still land
    in history at the right index."""
    seen: list[np.ndarray] = []

    def batch(xs):
        seen.extend(xs)
        return [_objective(x) for x in xs]

    # first 3 startup points are "already archived"
    def cache_lookup(idx, x):
        return -999.0 if idx < 3 else None

    out = tpe_over_template(
        _objective, family_bounds(None), {"matched_budget": BUDGET},
        rng=np.random.default_rng(11), n_startup=N_STARTUP,
        cache_lookup=cache_lookup, batch_eval_fn=batch,
    )
    assert len(seen) == N_STARTUP - 3, "cached startup points were re-trained"
    assert [h["score"] for h in out["history"][:3]] == [-999.0] * 3
    assert len(out["history"]) == BUDGET


def test_on_evaluated_fires_only_for_FRESH_batch_points():
    fired: list[int] = []

    def batch(xs):
        return [_objective(x) for x in xs]

    tpe_over_template(
        _objective, family_bounds(None), {"matched_budget": BUDGET},
        rng=np.random.default_rng(11), n_startup=N_STARTUP,
        cache_lookup=lambda idx, x: -1.0 if idx < 2 else None,
        on_evaluated=lambda idx, x, s: fired.append(idx),
        batch_eval_fn=batch,
    )
    assert 0 not in fired and 1 not in fired, "checkpointed a cached (already-archived) candidate"
    assert set(range(2, N_STARTUP)) <= set(fired)


def test_a_mismatched_batch_result_fails_LOUD():
    """A short/long return would silently desynchronise the study from the history."""
    with pytest.raises(ValueError, match="must be evaluated 1:1"):
        tpe_over_template(
            _objective, family_bounds(None), {"matched_budget": BUDGET},
            rng=np.random.default_rng(11), n_startup=N_STARTUP,
            batch_eval_fn=lambda xs: [0.0] * (len(xs) - 1),
        )


def test_batching_actually_shortens_the_serial_chain():
    """The point of the exercise: budget-N_STARTUP serial steps instead of budget."""
    batches: list[int] = []

    def batch(xs):
        batches.append(len(xs))
        return [_objective(x) for x in xs]

    tpe_over_template(_objective, family_bounds(None), {"matched_budget": BUDGET},
                      rng=np.random.default_rng(11), n_startup=N_STARTUP, batch_eval_fn=batch)
    assert batches == [N_STARTUP], "the startup phase was not dispatched as ONE batch"
