"""Tests for the Design Determination Pipeline (scripts/determine_design.py).

Covers the search-saturation engine (the candidate-budget analogue of recommend_budget), the record->curve
reduction, and the determination-status overlay + freeze-readiness logic. No torch, no GPU, no test data.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import determine_design as dd  # noqa: E402


# --------------------------------------------------------------------------- #
# Search-saturation engine (recommend_candidates)                              #
# --------------------------------------------------------------------------- #
def test_recommend_candidates_all_saturated_picks_slowest_arm() -> None:
    curves = {
        "distributional": [0.10, 0.20, 0.20, 0.20],   # plateaus at gen 1
        "scalar": [0.05, 0.05, 0.30, 0.30],            # plateaus at gen 2 (the slowest)
    }
    rec = dd.recommend_candidates(curves, candidates_per_gen=5, patience=1)
    assert rec["saturated"] is True
    assert rec["recommended_candidates"] == (2 + 1) * 5  # slowest arm saturated at gen 2 -> 15 candidates


def test_recommend_candidates_flags_still_rising() -> None:
    curves = {
        "distributional": [0.10, 0.20, 0.20],
        "scalar": [0.05, 0.15, 0.40],   # still climbing at the last generation
    }
    rec = dd.recommend_candidates(curves, candidates_per_gen=5, patience=1)
    assert rec["saturated"] is False
    assert rec["recommended_candidates"] is None
    assert "scalar" in rec["reason"]


def test_recommend_candidates_insufficient_generations() -> None:
    rec = dd.recommend_candidates({"a": [0.1]}, candidates_per_gen=5, patience=2)
    assert rec["saturated"] is None and rec["recommended_candidates"] is None


def test_best_so_far_curves_is_monotone_and_per_arm() -> None:
    records = [
        {"arm": "a", "generation": 0, "metrics": {"val_fitness": 0.1}},
        {"arm": "a", "generation": 1, "metrics": {"val_fitness": 0.05}},  # worse -> best-so-far stays 0.1
        {"arm": "a", "generation": 2, "metrics": {"val_fitness": 0.3}},
        {"arm": "b", "generation": 0, "metrics": {"val_fitness": 0.2}},
        {"arm": "b", "generation": 0, "metrics": {"val_fitness": 0.25}},  # same gen -> max within gen
    ]
    curves = dd.best_so_far_curves(records)
    assert curves["a"] == [0.1, 0.1, 0.3]      # monotone non-decreasing
    assert curves["b"] == [0.25]


# --------------------------------------------------------------------------- #
# Determination-status overlay + freeze readiness                              #
# --------------------------------------------------------------------------- #
def test_determine_blocks_freeze_when_measure_params_pending() -> None:
    res = dd.determine({})  # no evidence: B*, candidates, seeds, lambda all unresolved
    assert res["freeze_ready"] is False
    for blocker in ("train_steps_per_candidate", "n_seeds", "candidates_per_arm", "lambda_frozen"):
        assert blocker in res["blockers"]


def test_determine_cash_rate_zero_is_fix_needed() -> None:
    rows = {r["name"]: r["status"] for r in dd.determine({"cash_daily_rate": 0.0})["rows"]}
    assert rows["cash_daily_rate"] == dd.Status.FIX_NEEDED.value
    # A non-zero (risk-free) rate clears it.
    rows2 = {r["name"]: r["status"] for r in dd.determine({"cash_daily_rate": 0.00012})["rows"]}
    assert rows2["cash_daily_rate"] == dd.Status.DETERMINED.value


def test_determine_freeze_ready_when_all_blockers_resolved() -> None:
    ev = {
        "recommended_budget": 150_000,
        "candidates_saturated": True,
        "sigma_seed_pilot": True,
        "lambda_frozen": 2.0,
        "cash_daily_rate": 0.00012,
    }
    res = dd.determine(ev)
    assert res["freeze_ready"] is True and res["blockers"] == []


def test_registry_blockers_are_only_measure_or_calibrate() -> None:
    for spec in dd.REGISTRY:
        if spec.blocks_freeze:
            assert spec.klass in (dd.ParamClass.MEASURE, dd.ParamClass.CALIBRATE)
