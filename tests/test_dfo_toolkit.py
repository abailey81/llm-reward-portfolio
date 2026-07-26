"""The H4 DFO toolkit (CMA-ES + TPE) — drop-in siblings of bayes_opt: matched budget, deterministic,
valid, and they actually optimise. No agent training (a deterministic closed-form fitness)."""
import numpy as np
import pytest

from src.search.dfo_toolkit import cma_es_over_template, tpe_over_template

_OPTS = [cma_es_over_template, tpe_over_template]


@pytest.mark.parametrize("opt", _OPTS)
def test_dfo_matched_budget_deterministic_valid_and_optimizes(opt) -> None:
    bounds = [(-1.0, 1.0)] * 4

    def fit(x: np.ndarray) -> float:  # convex, max 0 at the origin; no training
        return -float(np.sum(np.asarray(x, dtype=float) ** 2))

    r1 = opt(fit, bounds, 20, rng=np.random.default_rng(0))
    r2 = opt(fit, bounds, 20, rng=np.random.default_rng(0))
    # EXACT matched candidate budget (the fair H4 comparison)
    assert r1["n_evaluated"] == 20 and r1["budget"] == 20 and len(r1["history"]) == 20
    # deterministic from the seed (the reproducibility contract)
    assert np.isclose(r1["best_score"], r2["best_score"]) and np.allclose(r1["best_coeffs"], r2["best_coeffs"])
    # valid: winner inside the box
    assert (r1["best_coeffs"] >= -1.0 - 1e-9).all() and (r1["best_coeffs"] <= 1.0 + 1e-9).all()
    # actually optimises: comfortably beats the ~-1.33 expected of a single uniform draw
    assert r1["best_score"] > -0.8, f"{opt.__name__} did not optimise: {r1['best_score']}"


@pytest.mark.parametrize("opt", _OPTS)
def test_dfo_cache_lookup_short_circuits_training(opt) -> None:
    bounds = [(0.0, 1.0)] * 3
    calls = {"n": 0}

    def fit(x: np.ndarray) -> float:
        calls["n"] += 1
        return float(np.sum(np.asarray(x, dtype=float)))

    # a cache hit for every candidate -> the (expensive) template_eval_fn is NEVER called, history stays full
    r = opt(fit, bounds, 8, rng=np.random.default_rng(1), cache_lookup=lambda i, x: 0.5)
    assert calls["n"] == 0 and r["n_evaluated"] == 8 and r["best_score"] == 0.5
