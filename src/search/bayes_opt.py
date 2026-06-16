"""Bayesian optimization over a fixed parametric reward template (H4b).

Purpose
-------
A non-LLM control arm (FINAL_PLAN F.10, hypothesis H4b). Rather than searching
over arbitrary code, it FIXES a parametric reward template and optimizes its
continuous coefficients with a real Bayesian-optimization loop. Compared under
the MATCHED budget, it isolates how much value comes from discovering reward
*structure* (only the LLM / random-code arms can) versus merely tuning a known
structure.

Algorithm (FINAL_PLAN F.10, H4b)
--------------------------------
    1. Fix a parametric reward template; its coefficients live in a bounded box.
    2. Seed with ``n_init`` Latin-hypercube-ish random points (uniform in box).
    3. Fit a Gaussian-process surrogate (Matern kernel) to the observed
       (coefficient -> held-out fitness) pairs.
    4. Maximize the Expected-Improvement acquisition over a dense random sample
       of the box to choose the next coefficient vector.
    5. Evaluate it via the injected ``template_eval_fn`` (which, in production,
       instantiates the templated reward, trains the fixed headline agent, and
       scores validation fitness; deterministic in tests), update the surrogate.
    6. Stop when the matched candidate budget is exhausted; return the best
       coefficients + score + full history.

The total number of ``template_eval_fn`` calls equals the matched candidate
budget (``n_init`` random seed points + the remaining BO-guided steps), so this
arm consumes exactly the same compute as the others.

Tests (tests/test_search.py)
----------------------------
    - on a known concave objective (``-(x-0.3)^2-(y+0.1)^2``) the optimizer gets
      close to the optimum within the budget;
    - it BEATS random sampling of the same budget on average;
    - it respects the matched budget from ``cfg``.
"""

from __future__ import annotations


from typing import Any, Callable, Optional, Sequence

import numpy as np
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel

from src.utils.config import DotDict

__all__ = ["bayes_opt_over_template", "random_search_over_template"]


def _budget(cfg: Any) -> int:
    """Read the matched candidate budget from ``cfg``."""
    if cfg is None:
        raise ValueError("bayes_opt_over_template requires a cfg with a budget")
    if isinstance(cfg, (DotDict, dict)):
        for key in ("matched_budget", "candidate_budget", "candidate_budget_total"):
            if key in cfg:
                return int(cfg[key])
        raise KeyError(
            "cfg must carry one of matched_budget / candidate_budget / "
            "candidate_budget_total"
        )
    return int(cfg)


def _as_bounds(bounds: Sequence[Sequence[float]]) -> np.ndarray:
    """Coerce bounds to a validated ``(d, 2)`` lower/upper array."""
    arr = np.asarray(bounds, dtype=float)
    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError(
            f"bounds must be a (d, 2) array of [low, high] pairs; got shape "
            f"{arr.shape}"
        )
    if np.any(arr[:, 0] >= arr[:, 1]):
        raise ValueError("each bound must satisfy low < high")
    return arr


def _sample_uniform(
    bounds: np.ndarray, n: int, rng: np.random.Generator
) -> np.ndarray:
    """Draw ``n`` points uniformly inside the bounding box."""
    low, high = bounds[:, 0], bounds[:, 1]
    return rng.uniform(low, high, size=(n, bounds.shape[0]))


def _expected_improvement(
    candidates: np.ndarray,
    gp: GaussianProcessRegressor,
    best_y: float,
    xi: float = 0.01,
) -> np.ndarray:
    """Expected Improvement acquisition (maximization), vectorized over rows.

    Parameters
    ----------
    candidates : ndarray, shape (m, d)
        Candidate coefficient vectors.
    gp : GaussianProcessRegressor
        Fitted surrogate.
    best_y : float
        Best observed objective value so far (incumbent).
    xi : float
        Exploration margin.

    Returns
    -------
    ndarray, shape (m,)
        EI value at each candidate (>= 0).
    """
    mu, sigma = gp.predict(candidates, return_std=True)
    sigma = np.maximum(sigma, 1e-9)
    improvement = mu - best_y - xi
    z = improvement / sigma
    ei = improvement * norm.cdf(z) + sigma * norm.pdf(z)
    ei[sigma < 1e-9] = 0.0
    return np.maximum(ei, 0.0)


def random_search_over_template(
    template_eval_fn: Callable[[np.ndarray], float],
    bounds: Sequence[Sequence[float]],
    cfg: Any,
    rng: Optional[np.random.Generator] = None,
) -> dict[str, Any]:
    """Pure random search over the same template box (budget-matched baseline).

    Used by the tests to confirm Bayesian optimization beats random sampling of
    the same budget on average. Evaluates exactly ``budget`` uniform draws.

    Parameters
    ----------
    template_eval_fn : Callable[[ndarray], float]
        Maps a coefficient vector to a fitness score (higher is better).
    bounds : sequence of (low, high)
        Per-coefficient box bounds.
    cfg : DotDict or dict or int
        Carries the matched candidate budget.
    rng : numpy.random.Generator, optional
        Source of randomness.

    Returns
    -------
    dict
        ``{"best_coeffs", "best_score", "history", "n_evaluated", "budget"}``.
    """
    box = _as_bounds(bounds)
    budget = _budget(cfg)
    if budget <= 0:
        raise ValueError(f"matched budget must be positive; got {budget}")
    if rng is None:
        rng = np.random.default_rng()

    points = _sample_uniform(box, budget, rng)
    history: list[dict[str, Any]] = []
    best_score = -np.inf
    best_coeffs: Optional[np.ndarray] = None
    for x in points:
        score = float(template_eval_fn(x))
        history.append({"coeffs": x.copy(), "score": score})
        if score > best_score:
            best_score = score
            best_coeffs = x.copy()

    return {
        "best_coeffs": best_coeffs,
        "best_score": best_score,
        "history": history,
        "n_evaluated": len(history),
        "budget": budget,
    }


def bayes_opt_over_template(
    template_eval_fn: Callable[[np.ndarray], float],
    bounds: Sequence[Sequence[float]],
    cfg: Any,
    n_init: int = 5,
    rng: Optional[np.random.Generator] = None,
) -> dict[str, Any]:
    """Bayesian-optimize reward-template coefficients under the matched budget.

    Parameters
    ----------
    template_eval_fn : Callable[[ndarray], float]
        Maps a coefficient vector to a held-out fitness score (higher is
        better). In production this instantiates the templated reward, trains
        the fixed headline agent, and scores validation fitness; in tests it is
        a deterministic closure (no agent training required).
    bounds : sequence of (low, high)
        Per-coefficient box bounds defining the template's coefficient space.
    cfg : DotDict or dict or int
        Carries the matched candidate budget (total ``template_eval_fn`` calls).
    n_init : int, optional
        Number of random seed evaluations before the GP-guided loop. Clamped to
        the budget. Default 5.
    rng : numpy.random.Generator, optional
        Source of randomness; a fresh default generator is created when ``None``.

    Returns
    -------
    dict
        ``{"best_coeffs", "best_score", "history", "n_evaluated", "budget",
        "n_init"}`` where ``history`` records every evaluation in order.

    Notes
    -----
    The surrogate is a ``GaussianProcessRegressor`` with a Matern(nu=2.5) kernel
    plus a white-noise term, and the acquisition is Expected Improvement
    maximized over a dense uniform sample of the box. The total number of
    ``template_eval_fn`` calls equals ``budget``.
    """
    box = _as_bounds(bounds)
    dim = box.shape[0]
    budget = _budget(cfg)
    if budget <= 0:
        raise ValueError(f"matched budget must be positive; got {budget}")
    if rng is None:
        rng = np.random.default_rng()

    n_init = int(max(1, min(n_init, budget)))

    history: list[dict[str, Any]] = []
    x_obs: list[np.ndarray] = []
    y_obs: list[float] = []

    def _evaluate(x: np.ndarray, source: str) -> float:
        score = float(template_eval_fn(x))
        x_obs.append(x.copy())
        y_obs.append(score)
        history.append({"coeffs": x.copy(), "score": score, "source": source})
        return score

    # 1. Random seed phase.
    init_points = _sample_uniform(box, n_init, rng)
    for x in init_points:
        _evaluate(x, "init")

    # 2. BO-guided phase for the remaining budget.
    kernel = (
        ConstantKernel(1.0, (1e-3, 1e3))
        * Matern(
            length_scale=np.ones(dim),
            length_scale_bounds=(1e-2, 1e3),
            nu=2.5,
        )
        + WhiteKernel(noise_level=1e-5, noise_level_bounds=(1e-10, 1e-1))
    )

    n_remaining = budget - n_init
    n_acq = 2000  # acquisition-optimization sample size

    for _ in range(n_remaining):
        X = np.asarray(x_obs, dtype=float)
        y = np.asarray(y_obs, dtype=float)

        gp = GaussianProcessRegressor(
            kernel=kernel,
            normalize_y=True,
            n_restarts_optimizer=2,
            random_state=int(rng.integers(0, 2**31 - 1)),
        )
        gp.fit(X, y)

        candidates = _sample_uniform(box, n_acq, rng)
        ei = _expected_improvement(candidates, gp, best_y=float(np.max(y)))
        next_x = candidates[int(np.argmax(ei))]
        _evaluate(next_x, "bo")

    y_all = np.asarray(y_obs, dtype=float)
    best_idx = int(np.argmax(y_all))

    return {
        "best_coeffs": x_obs[best_idx].copy(),
        "best_score": float(y_all[best_idx]),
        "history": history,
        "n_evaluated": len(history),
        "budget": budget,
        "n_init": n_init,
    }
