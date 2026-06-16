"""Stationary-bootstrap inference for dependent return series (FINAL_PLAN F.11).

Purpose
-------
Provide block-resampling machinery and paired performance-difference tests that
remain valid under the serial correlation present in daily portfolio returns.
These tests back the headline pairwise comparisons between arms (distributional
vs scalar feedback) and feed the multiple-testing family in
``src.inference.multiple_testing``.

Why the stationary bootstrap
----------------------------
Daily P&L is autocorrelated (volatility clustering, momentum/mean-reversion),
so the iid bootstrap and naive t-tests understate sampling error. The
Politis-Romano (1994) stationary bootstrap resamples *blocks* of random,
geometrically distributed length with wrap-around, which preserves the
short-range dependence structure while keeping the resampled series stationary.

Algorithm (stationary bootstrap, index form)
---------------------------------------------
1. Draw a starting index uniformly in ``[0, n)``.
2. With probability ``p`` start a fresh block (draw a new uniform start); with
   probability ``1 - p`` continue the current block by stepping the index
   forward by one (mod ``n`` -- wrap-around).
3. Expected block length is ``1 / p``; block lengths are ``Geometric(p)``.
4. Repeat until ``n`` indices are produced -- that is one bootstrap path.

Difference tests
----------------
``sharpe_difference_test`` implements a *studentized block-bootstrap* test for
``H0: SR(a) - SR(b) = 0``: the observed difference is divided by a bootstrap
estimate of its standard error and the two-sided p-value is read off the
bootstrap distribution of the studentized, null-recentred difference. The
studentization follows Ledoit & Wolf (2008) in spirit, but note two precise
distinctions (verified against the source): Ledoit & Wolf (2008) use the
*circular* block bootstrap of Politis & Romano (**1992**, fixed block size),
whereas here we use the *stationary* bootstrap of Politis & Romano (**1994**,
random geometric block lengths) on its own merits for autocorrelated returns —
we do NOT attribute the stationary bootstrap to Ledoit-Wolf.

``cvar_difference_test`` applies the analogous studentized stationary-bootstrap
construction to the difference in CVaR (expected shortfall) at level ``alpha``.
No published studentized difference-in-CVaR test was located, so this is a
*bespoke* extension whose size is certified empirically by ``null_calibration``
(audit C-7) rather than by a citation.

``null_calibration`` repeatedly applies a difference test under a true null and
reports the empirical rejection rate at the 5% level together with the raw
p-values, certifying that the test machinery is correctly sized (audit C-7).

FINAL_PLAN refs
---------------
- F.11 (selection-aware inference stack): block bootstrap + paired tests.
- audit C-7: null-calibration certification of the test machinery.
"""

from __future__ import annotations


import math
from typing import Callable

import numpy as np

__all__ = [
    "stationary_bootstrap_indices",
    "sharpe_ratio",
    "cvar",
    "sharpe_difference_test",
    "cvar_difference_test",
    "null_calibration",
]


def stationary_bootstrap_indices(
    n: int,
    p: float,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Politis-Romano stationary-bootstrap index path of length ``n``.

    Parameters
    ----------
    n:
        Length of the series / number of indices to generate.
    p:
        Geometric block-restart probability in ``(0, 1]``; expected block
        length is ``1 / p``. With ``p == 1`` every step restarts, giving an iid
        bootstrap; small ``p`` produces long contiguous blocks.
    rng:
        Optional NumPy generator for reproducibility.

    Returns
    -------
    numpy.ndarray
        Integer array of shape ``(n,)`` with values in ``[0, n)``: a single
        stationary-bootstrap resampling path with wrap-around.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if not (0.0 < p <= 1.0):
        raise ValueError("p must lie in (0, 1]")
    if rng is None:
        rng = np.random.default_rng()

    idx = np.empty(n, dtype=np.intp)
    # Pre-draw the restart decisions and candidate fresh starts for speed.
    restart = rng.random(n) < p
    fresh = rng.integers(0, n, size=n)

    cur = int(fresh[0])  # always start a fresh block at position 0
    idx[0] = cur
    for t in range(1, n):
        if restart[t]:
            cur = int(fresh[t])
        else:
            cur = (cur + 1) % n
        idx[t] = cur
    return idx


def sharpe_ratio(returns: np.ndarray, periods_per_year: int = 252) -> float:
    """Annualized Sharpe ratio of a per-period return series.

    Parameters
    ----------
    returns:
        One-dimensional array of per-period (e.g. daily) returns.
    periods_per_year:
        Number of periods per year used for annualization (default ``252``).

    Returns
    -------
    float
        ``mean / std * sqrt(periods_per_year)`` using the population (ddof=0)
        standard deviation. Returns ``0.0`` if the standard deviation is zero.
    """
    r = np.asarray(returns, dtype=float)
    if r.size == 0:
        return 0.0
    sd = r.std(ddof=0)
    if sd == 0.0 or not np.isfinite(sd):
        return 0.0
    return float(r.mean() / sd * math.sqrt(periods_per_year))


def cvar(returns: np.ndarray, alpha: float) -> float:
    """Conditional Value-at-Risk (expected shortfall) of the lower tail.

    Parameters
    ----------
    returns:
        One-dimensional array of returns.
    alpha:
        Tail level in ``(0, 1]`` (e.g. ``0.05`` for the 5% expected shortfall).

    Returns
    -------
    float
        The mean of the worst ``ceil(alpha * T)`` returns (the lower tail).
        For loss-making tails this is negative; smaller ``alpha`` selects a
        more extreme (more negative) tail.
    """
    if not (0.0 < alpha <= 1.0):
        raise ValueError("alpha must lie in (0, 1]")
    r = np.asarray(returns, dtype=float)
    t = r.size
    if t == 0:
        return float("nan")
    k = max(1, int(math.ceil(alpha * t)))
    # The k smallest (worst) returns.
    worst = np.partition(r, k - 1)[:k]
    return float(worst.mean())


def _bootstrap_statistic_distribution(
    a: np.ndarray,
    b: np.ndarray,
    stat_fn: Callable[[np.ndarray, np.ndarray], float],
    p: float,
    n_boot: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Bootstrap distribution of ``stat_fn(a, b)`` under matched index resampling.

    Both series are resampled with the *same* stationary-bootstrap index path so
    that any contemporaneous dependence between ``a`` and ``b`` is preserved.
    """
    n = a.size
    out = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        idx = stationary_bootstrap_indices(n, p, rng)
        out[i] = stat_fn(a[idx], b[idx])
    return out


def sharpe_difference_test(
    a: np.ndarray,
    b: np.ndarray,
    p: float = 0.1,
    n_boot: int = 2000,
    rng: np.random.Generator | None = None,
) -> dict[str, float]:
    """Studentized stationary-bootstrap test for ``H0: SR(a) - SR(b) = 0``.

    Parameters
    ----------
    a, b:
        Aligned per-period return series for the two strategies.
    p:
        Stationary-bootstrap block-restart probability.
    n_boot:
        Number of bootstrap replications.
    rng:
        Optional NumPy generator for reproducibility.

    Returns
    -------
    dict
        ``{"stat", "pvalue", "ci_low", "ci_high"}`` where ``stat`` is the
        studentized observed difference, ``pvalue`` is the two-sided bootstrap
        p-value, and ``ci_low``/``ci_high`` form a 95% percentile bootstrap CI
        for the raw Sharpe difference.

    Notes
    -----
    The standard error is estimated from the bootstrap spread of the difference.
    The two-sided p-value is the bootstrap probability that the studentized,
    null-recentred statistic exceeds the observed studentized statistic in
    absolute value (studentized stationary block bootstrap; see the module
    docstring for the precise Ledoit-Wolf 1992-vs-1994 bootstrap distinction).
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError("a and b must have the same shape")
    if rng is None:
        rng = np.random.default_rng()

    def diff(x: np.ndarray, y: np.ndarray) -> float:
        return sharpe_ratio(x) - sharpe_ratio(y)

    obs = diff(a, b)
    boot = _bootstrap_statistic_distribution(a, b, diff, p, n_boot, rng)

    se = boot.std(ddof=1)
    if se == 0.0 or not np.isfinite(se):
        se = float("nan")

    stat = obs / se if np.isfinite(se) else 0.0
    # Studentized, null-recentred bootstrap statistics.
    centred = (boot - obs) / se if np.isfinite(se) else np.zeros_like(boot)
    if np.isfinite(se):
        pvalue = float((np.abs(centred) >= abs(stat)).mean())
    else:
        pvalue = 1.0
    # Guard against an exact-zero p-value (finite bootstrap resolution).
    pvalue = min(1.0, max(pvalue, 1.0 / (n_boot + 1)))

    ci_low = float(np.quantile(boot, 0.025))
    ci_high = float(np.quantile(boot, 0.975))
    return {"stat": float(stat), "pvalue": pvalue, "ci_low": ci_low, "ci_high": ci_high}


def cvar_difference_test(
    a: np.ndarray,
    b: np.ndarray,
    alpha: float = 0.05,
    n_boot: int = 2000,
    rng: np.random.Generator | None = None,
) -> dict[str, float]:
    """Two-sample studentized stationary-bootstrap test for ``H0: CVaR(a) - CVaR(b) = 0``.

    This is the appropriate tool when ``a`` and ``b`` are the *realized* return series of two different
    strategies (e.g. the distributional vs scalar arm) and the question is whether their realized tail
    losses differ — the direct analogue of the Ledoit-Wolf (2008) studentized-bootstrap Sharpe-difference
    test, applied to the CVaR functional. No *published, named* two-sample difference-in-CVaR test exists
    (deep-research #2/#3), so this bespoke construction's size is certified empirically by
    :func:`null_calibration` (audit C-7). CVaR/ES is a well-defined estimable functional because the pair
    (VaR, ES) is *jointly* elicitable (Fissler & Ziegel, 2016), even though ES alone is not.

    NOT to be confused with a *comparative backtest*: if instead you are comparing the tail-FORECAST
    accuracy of two risk models on a COMMON realized series, use
    :func:`src.inference.es_backtest.comparative_es_backtest` (the Diebold-Mariano test on the strictly
    consistent FZ0 (VaR, ES) score; Nolde & Ziegel, 2017).

    Power caveat (Bauer, 2025): tail-risk difference tests have low power at the most extreme quantiles
    (``alpha`` = 1%, 2.5%) and short windows — interpret CVaR-1% comparisons with care.

    Parameters
    ----------
    a, b:
        Aligned per-period realized return series for the two strategies.
    alpha:
        Tail level for CVaR (e.g. ``0.05``). The stationary-bootstrap block-restart
        probability is fixed internally at ``0.1`` (expected block length 10).
    n_boot:
        Number of bootstrap replications.
    rng:
        Optional NumPy generator for reproducibility.

    Returns
    -------
    dict
        ``{"stat", "pvalue", "ci_low", "ci_high"}``; semantics mirror
        :func:`sharpe_difference_test` for the CVaR difference.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.shape != b.shape:
        raise ValueError("a and b must have the same shape")
    if rng is None:
        rng = np.random.default_rng()

    p = 0.1

    def diff(x: np.ndarray, y: np.ndarray) -> float:
        return cvar(x, alpha) - cvar(y, alpha)

    obs = diff(a, b)
    boot = _bootstrap_statistic_distribution(a, b, diff, p, n_boot, rng)

    se = boot.std(ddof=1)
    if se == 0.0 or not np.isfinite(se):
        se = float("nan")

    stat = obs / se if np.isfinite(se) else 0.0
    centred = (boot - obs) / se if np.isfinite(se) else np.zeros_like(boot)
    if np.isfinite(se):
        pvalue = float((np.abs(centred) >= abs(stat)).mean())
    else:
        pvalue = 1.0
    pvalue = min(1.0, max(pvalue, 1.0 / (n_boot + 1)))

    ci_low = float(np.quantile(boot, 0.025))
    ci_high = float(np.quantile(boot, 0.975))
    return {"stat": float(stat), "pvalue": pvalue, "ci_low": ci_low, "ci_high": ci_high}


def null_calibration(
    test_fn: Callable[[np.ndarray, np.ndarray], dict[str, float]],
    dist_sampler: Callable[[np.random.Generator], tuple[np.ndarray, np.ndarray]],
    n_reps: int = 200,
    rng: np.random.Generator | None = None,
) -> dict[str, object]:
    """Certify a difference test's size under a true null (audit C-7).

    Parameters
    ----------
    test_fn:
        Callable ``(a, b) -> dict`` returning a mapping with a ``"pvalue"`` key.
    dist_sampler:
        Callable ``(rng) -> (a, b)`` drawing a pair of series under the null.
    n_reps:
        Number of null replications.
    rng:
        Optional NumPy generator for reproducibility.

    Returns
    -------
    dict
        ``{"rejection_rate", "mean_pvalue", "pvalues"}`` where
        ``rejection_rate`` is the empirical fraction of p-values below 0.05.
    """
    if rng is None:
        rng = np.random.default_rng()
    pvalues = np.empty(n_reps, dtype=float)
    for i in range(n_reps):
        a, b = dist_sampler(rng)
        res = test_fn(a, b)
        pvalues[i] = float(res["pvalue"])
    rejection_rate = float((pvalues < 0.05).mean())
    return {
        "rejection_rate": rejection_rate,
        "mean_pvalue": float(pvalues.mean()),
        "pvalues": pvalues,
    }
