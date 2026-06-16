"""Benchmark portfolio allocators (non-learned baselines).

Purpose
-------
Classical and rule-based allocators that compete against the learned agents
(FINAL_PLAN F.6). Each function maps market state to a vector of portfolio
weights lying on the probability simplex (non-negative, summing to one — long
only, fully invested). They provide the floor that any discovered reward must
beat to be interesting.

Allocator canon (FINAL_PLAN F.6)
--------------------------------
    spy_buy_and_hold : single-asset (market proxy) buy-and-hold; no forecast.
    equal_weight     : 1/N naive diversification; no forecast.
    mean_variance    : Markowitz with Ledoit-Wolf shrinkage of the covariance.
    risk_parity      : equal risk contribution allocation.
    hrp              : Hierarchical Risk Parity (Lopez de Prado): hierarchical
                       clustering -> quasi-diagonalization -> recursive bisection.

Conventions
-----------
    returns : a window of per-asset returns (rows = time, cols = assets) used
              to estimate moments where required.
    cfg     : configuration object (risk aversion, shrinkage flags, lookback).
    output  : 1-D weight vector on the simplex with one entry per asset.

Tests (tests/test_baselines.py)
-------------------------------
    - test_strategies_return_simplex: every allocator returns simplex weights.
    - test_mean_variance_uses_shrinkage: mean_variance applies Ledoit-Wolf.
    - test_no_forecast_baselines: equal_weight and hrp need no return forecast.
"""

from __future__ import annotations


from typing import Any

import numpy as np


def _as_window(returns: Any) -> np.ndarray:
    """Coerce a returns window to a 2-D (time, assets) float array."""
    arr = np.asarray(returns, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    if arr.ndim != 2:
        raise ValueError("returns window must be 1-D or 2-D (time, assets)")
    return arr


def _n_assets(returns: Any) -> int:
    return _as_window(returns).shape[1]


def spy_buy_and_hold(returns: Any, cfg: Any = None) -> np.ndarray:
    """Documented full-invested equal-weight market proxy.

    Algorithm sketch
    -----------------
    The anonymized panel carries no explicit SPY column, so the market proxy is
    a fully-invested equal-weight basket of the available assets — a standard
    cap-agnostic stand-in for "the market". No forecast, no rebalancing logic.

    FINAL_PLAN F.6 (benchmark allocators).
    """
    n = _n_assets(returns)
    return np.full(n, 1.0 / n, dtype=float)


def equal_weight(returns: Any, cfg: Any = None) -> np.ndarray:
    """Naive 1/N equal-weight allocation.

    Algorithm sketch
    -----------------
    w_i = 1 / N for all N assets. Requires NO return forecast — only the asset
    count is needed.

    FINAL_PLAN F.6 (benchmark allocators).
    """
    n = _n_assets(returns)
    return np.full(n, 1.0 / n, dtype=float)


def mean_variance(returns: Any, cfg: Any = None) -> np.ndarray:
    """Markowitz mean-variance allocation with Ledoit-Wolf shrinkage.

    Algorithm sketch
    -----------------
    1. Estimate expected returns mu from ``returns``.
    2. Estimate covariance Sigma via Ledoit-Wolf shrinkage (shrinks the sample
       covariance toward a structured target; stabilizes inversion).
    3. Solve w* proportional to Sigma^{-1} mu under risk aversion from ``cfg``,
       then project onto the long-only simplex.

    FINAL_PLAN F.6 (benchmark allocators; shrinkage is the audited detail).
    """
    from sklearn.covariance import LedoitWolf

    arr = _as_window(returns)
    n = arr.shape[1]
    if n == 1:
        return np.ones(1, dtype=float)

    mu = arr.mean(axis=0)
    # Ledoit-Wolf shrinkage of the covariance toward a scaled-identity target;
    # the resulting estimate is symmetric positive-definite (stable inversion).
    cov = LedoitWolf().fit(arr).covariance_
    cov = cov + 1e-12 * np.eye(n)  # numerical floor

    # Max-Sharpe direction w* proportional to Sigma^{-1} mu; if mu has no upside
    # signal, fall back to the global minimum-variance portfolio Sigma^{-1} 1.
    inv = np.linalg.inv(cov)
    raw = inv @ mu
    if not np.isfinite(raw).all() or raw.sum() <= 0:
        raw = inv @ np.ones(n)

    # Project onto the long-only simplex.
    return _project_simplex(raw)


def _project_simplex(v: np.ndarray) -> np.ndarray:
    """Euclidean projection of vector ``v`` onto the probability simplex."""
    v = np.asarray(v, dtype=float).ravel()
    n = v.size
    u = np.sort(v)[::-1]
    cssv = np.cumsum(u) - 1.0
    ind = np.arange(1, n + 1)
    cond = u - cssv / ind > 0
    if not cond.any():
        return np.full(n, 1.0 / n)
    rho = ind[cond][-1]
    theta = cssv[cond][-1] / rho
    w = np.maximum(v - theta, 0.0)
    s = w.sum()
    return w / s if s > 0 else np.full(n, 1.0 / n)


def risk_parity(returns: Any, cfg: Any = None) -> np.ndarray:
    """Equal-risk-contribution (risk parity) allocation.

    Algorithm sketch
    -----------------
    Estimate Sigma, then solve for weights such that each asset contributes
    equally to total portfolio risk: w_i * (Sigma w)_i is constant across i.
    Solved by iterative/convex optimization; result projected to the simplex.

    FINAL_PLAN F.6 (benchmark allocators).
    """
    arr = _as_window(returns)
    n = arr.shape[1]
    if n == 1:
        return np.ones(1, dtype=float)

    cov = np.cov(arr, rowvar=False)
    cov = np.atleast_2d(cov) + 1e-12 * np.eye(n)

    # Iterative (cyclical) update for equal risk contribution. Starting from the
    # inverse-volatility seed, repeatedly rescale each weight by the ratio of the
    # target risk share to its current marginal risk contribution.
    inv_vol = 1.0 / np.sqrt(np.diag(cov))
    w = inv_vol / inv_vol.sum()
    target = 1.0 / n
    for _ in range(10_000):
        sigma_w = cov @ w
        port_var = float(w @ sigma_w)
        rc = w * sigma_w / port_var  # risk contributions, sum to 1
        if np.max(np.abs(rc - target)) < 1e-10:
            break
        w = w * (target / rc)
        w = np.maximum(w, 0.0)
        w = w / w.sum()
    return w


def hrp(returns: Any, cfg: Any = None) -> np.ndarray:
    """Hierarchical Risk Parity allocation (Lopez de Prado).

    Algorithm sketch
    -----------------
    1. Compute the correlation-distance matrix from ``returns``.
    2. Hierarchical clustering (linkage) of assets.
    3. Quasi-diagonalization: reorder assets so similar ones are adjacent.
    4. Recursive bisection: split the ordered tree and allocate inversely to
       cluster variance down the dendrogram.
    Requires NO expected-return forecast — only the covariance structure.

    FINAL_PLAN F.6 (benchmark allocators).
    """
    from scipy.cluster.hierarchy import linkage
    from scipy.spatial.distance import squareform

    arr = _as_window(returns)
    n = arr.shape[1]
    if n == 1:
        return np.ones(1, dtype=float)

    cov = np.cov(arr, rowvar=False)
    cov = np.atleast_2d(cov)
    std = np.sqrt(np.diag(cov))
    corr = cov / np.outer(std, std)
    corr = np.clip(corr, -1.0, 1.0)
    np.fill_diagonal(corr, 1.0)

    # 1. Correlation distance d = sqrt(0.5 * (1 - corr)).
    dist = np.sqrt(0.5 * (1.0 - corr))
    np.fill_diagonal(dist, 0.0)
    dist = (dist + dist.T) / 2.0  # enforce exact symmetry for squareform

    # 2. Hierarchical (single-linkage) clustering.
    link = linkage(squareform(dist, checks=False), method="single")

    # 3. Quasi-diagonalization: recover the leaf order from the dendrogram.
    sort_ix = _quasi_diag(link, n)

    # 4. Recursive bisection allocating inversely to cluster variance.
    weights = _recursive_bisection(cov, sort_ix)
    s = weights.sum()
    return weights / s if s > 0 else np.full(n, 1.0 / n)


def _quasi_diag(link: np.ndarray, n_leaves: int) -> list[int]:
    """Return the leaf ordering implied by a SciPy linkage matrix."""
    link = link.astype(int)
    sort_ix = [int(link[-1, 0]), int(link[-1, 1])]
    # Expand any cluster ids (>= n_leaves) into their constituent leaves.
    while max(sort_ix) >= n_leaves:
        new_order: list[int] = []
        for item in sort_ix:
            if item < n_leaves:
                new_order.append(item)
            else:
                row = item - n_leaves
                new_order.append(int(link[row, 0]))
                new_order.append(int(link[row, 1]))
        sort_ix = new_order
    return sort_ix


def _cluster_var(cov: np.ndarray, items: list[int]) -> float:
    """Inverse-variance-weighted variance of a sub-portfolio (HRP)."""
    sub = cov[np.ix_(items, items)]
    ivp = 1.0 / np.diag(sub)
    ivp = ivp / ivp.sum()
    return float(ivp @ sub @ ivp)


def _recursive_bisection(cov: np.ndarray, sort_ix: list[int]) -> np.ndarray:
    """Allocate weights by recursive bisection over the quasi-diagonal order."""
    w = np.ones(cov.shape[0], dtype=float)
    clusters = [sort_ix]
    while clusters:
        clusters = [
            c[start:stop]
            for c in clusters
            for start, stop in ((0, len(c) // 2), (len(c) // 2, len(c)))
            if len(c) > 1
        ]
        for i in range(0, len(clusters), 2):
            left = clusters[i]
            right = clusters[i + 1]
            var_left = _cluster_var(cov, left)
            var_right = _cluster_var(cov, right)
            alpha = 1.0 - var_left / (var_left + var_right)
            for idx in left:
                w[idx] *= alpha
            for idx in right:
                w[idx] *= 1.0 - alpha
    return w
