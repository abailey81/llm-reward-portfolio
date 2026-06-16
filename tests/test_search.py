"""Tests for the non-LLM search ablations (FINAL_PLAN F.10).

Covers:
  - random_search_over_code returns a valid (gate-passing) best reward, consumes
    EXACTLY the matched budget, and every sampled source passes ``ast_gate``;
  - bayes_opt_over_template approaches the optimum of a known concave objective
    within the budget and BEATS budget-matched random sampling on average;
  - both respect the matched budget read from ``cfg``.

The injected fitness/eval closures are deterministic — no agent training.
"""

from __future__ import annotations


import numpy as np
import pytest

from src.sandbox.executor import ast_gate, validate_once
from src.search import bayes_opt, random_search


# ----------------------------------------------------------------------------- #
# Random search over the reward CODE space (H4a)
# ----------------------------------------------------------------------------- #
def _fixture() -> tuple:
    weights = np.array([0.4, 0.3, 0.3], dtype=float)
    returns = np.array([0.01, -0.02, 0.005], dtype=float)
    prev_weights = np.array([0.34, 0.33, 0.33], dtype=float)
    return (weights, returns, prev_weights, 0.002, {})


def _deterministic_reward_fitness(reward) -> float:
    """Score a reward by replaying a fixed return path through it.

    Deterministic given the reward callable: feeds a short canned sequence of
    portfolio returns and returns the mean total reward. No agent training.
    """
    fixture_weights = np.array([0.4, 0.3, 0.3], dtype=float)
    fixture_returns = np.array([0.01, -0.02, 0.005], dtype=float)
    prev = np.array([0.34, 0.33, 0.33], dtype=float)
    path = [0.01, -0.03, 0.02, -0.05, 0.015, 0.0, -0.01]
    info: dict = {}
    totals = []
    for r in path:
        total, _components, state = reward(
            fixture_weights, fixture_returns, prev, r, info
        )
        info["reward_state"] = state
        totals.append(float(total))
    return float(np.mean(totals))


def test_random_search_consumes_exact_budget() -> None:
    """random_search evaluates exactly the matched budget of valid candidates."""
    cfg = {"matched_budget": 12}
    rng = np.random.default_rng(0)
    out = random_search.random_search_over_code(
        env_builder=None,
        fitness_fn=_deterministic_reward_fitness,
        cfg=cfg,
        rng=rng,
    )
    assert out["budget"] == 12
    assert out["n_evaluated"] == 12
    assert len(out["archive"]) == 12


def test_random_search_returns_valid_gate_passing_best() -> None:
    """The returned best reward passes the AST gate and validates against the
    reward contract."""
    cfg = {"matched_budget": 10}
    rng = np.random.default_rng(1)
    out = random_search.random_search_over_code(
        env_builder=None,
        fitness_fn=_deterministic_reward_fitness,
        cfg=cfg,
        rng=rng,
    )
    best_source = out["best_source"]
    assert best_source is not None
    assert ast_gate(best_source) is True
    # Re-validate the best source end-to-end (raises SandboxError on failure).
    reward = validate_once(best_source, _fixture())
    assert callable(reward)
    # Best score is the archive maximum.
    assert out["best_score"] == max(rec["score"] for rec in out["archive"])


def test_random_search_every_source_passes_gate() -> None:
    """Every sampled source in the archive passes ast_gate (code-space draws)."""
    cfg = {"matched_budget": 20}
    rng = np.random.default_rng(2)
    out = random_search.random_search_over_code(
        env_builder=None,
        fitness_fn=_deterministic_reward_fitness,
        cfg=cfg,
        rng=rng,
    )
    for rec in out["archive"]:
        assert ast_gate(rec["source"]) is True
        # Each is genuine reward CODE (a def, not a coefficient vector).
        assert rec["source"].lstrip().startswith("def reward(")


def test_random_search_budget_from_candidate_budget_key() -> None:
    """The budget may also be read from candidate_budget_total (llm.yaml style)."""
    cfg = {"candidate_budget_total": 7}
    rng = np.random.default_rng(3)
    out = random_search.random_search_over_code(
        env_builder=None,
        fitness_fn=_deterministic_reward_fitness,
        cfg=cfg,
        rng=rng,
    )
    assert out["n_evaluated"] == 7


# ----------------------------------------------------------------------------- #
# Bayesian optimization over a parametric template (H4b)
# ----------------------------------------------------------------------------- #
def _concave_objective(x: np.ndarray) -> float:
    """Known concave objective with a unique optimum at (0.3, -0.1), value 0."""
    return float(-((x[0] - 0.3) ** 2) - ((x[1] + 0.1) ** 2))


BOUNDS = [(-2.0, 2.0), (-2.0, 2.0)]
OPTIMUM = np.array([0.3, -0.1])


def test_bayes_opt_consumes_exact_budget() -> None:
    """bayes_opt makes exactly ``budget`` evaluations (n_init + BO steps)."""
    cfg = {"matched_budget": 18}
    rng = np.random.default_rng(0)
    out = bayes_opt.bayes_opt_over_template(
        _concave_objective, BOUNDS, cfg, n_init=5, rng=rng
    )
    assert out["budget"] == 18
    assert out["n_evaluated"] == 18
    assert len(out["history"]) == 18
    assert out["n_init"] == 5


def test_bayes_opt_optimizes_template_coefficients() -> None:
    """History records coefficient VECTORS of the template, not code."""
    cfg = {"matched_budget": 15}
    rng = np.random.default_rng(1)
    out = bayes_opt.bayes_opt_over_template(
        _concave_objective, BOUNDS, cfg, n_init=5, rng=rng
    )
    best = np.asarray(out["best_coeffs"], dtype=float)
    assert best.shape == (2,)
    for rec in out["history"]:
        coeffs = np.asarray(rec["coeffs"], dtype=float)
        assert coeffs.shape == (2,)
        # Inside the box.
        assert np.all(coeffs >= -2.0) and np.all(coeffs <= 2.0)


def test_bayes_opt_approaches_optimum() -> None:
    """Within the budget, BO lands close to the known optimum (0.3, -0.1)."""
    cfg = {"matched_budget": 25}
    rng = np.random.default_rng(7)
    out = bayes_opt.bayes_opt_over_template(
        _concave_objective, BOUNDS, cfg, n_init=5, rng=rng
    )
    dist = float(np.linalg.norm(np.asarray(out["best_coeffs"]) - OPTIMUM))
    assert dist < 0.25, f"BO best {out['best_coeffs']} too far from optimum (d={dist})"
    # Best objective value is near the maximum of 0.
    assert out["best_score"] > -0.06


def test_bayes_opt_beats_random_on_average() -> None:
    """BO beats budget-matched random sampling on average over several seeds."""
    cfg = {"matched_budget": 20}
    n_seeds = 6
    bo_scores = []
    rand_scores = []
    for seed in range(n_seeds):
        bo_out = bayes_opt.bayes_opt_over_template(
            _concave_objective,
            BOUNDS,
            cfg,
            n_init=5,
            rng=np.random.default_rng(100 + seed),
        )
        rand_out = bayes_opt.random_search_over_template(
            _concave_objective,
            BOUNDS,
            cfg,
            rng=np.random.default_rng(500 + seed),
        )
        bo_scores.append(bo_out["best_score"])
        rand_scores.append(rand_out["best_score"])

    assert np.mean(bo_scores) > np.mean(rand_scores), (
        f"BO mean {np.mean(bo_scores):.4f} did not beat random "
        f"{np.mean(rand_scores):.4f}"
    )


def test_bayes_opt_budget_from_int() -> None:
    """The budget may be passed as a bare int."""
    rng = np.random.default_rng(2)
    out = bayes_opt.bayes_opt_over_template(_concave_objective, BOUNDS, 9, rng=rng)
    assert out["n_evaluated"] == 9


def test_bayes_opt_rejects_bad_bounds() -> None:
    """Malformed bounds raise ValueError."""
    with pytest.raises(ValueError):
        bayes_opt.bayes_opt_over_template(_concave_objective, [(1.0, 0.0)], 5)
