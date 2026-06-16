"""Robust aggregate reporting statistics (rliable-style) (FINAL_PLAN F.11).

Purpose
-------
Aggregate held-out scores with estimators robust to outlier runs and that
report uncertainty honestly, following the ``rliable`` methodology (Agarwal et
al. 2021).

Estimators
----------
- ``iqm`` -- the interquartile mean: average the middle 50% of scores.
- ``probability_of_improvement`` -- ``P(a > b)`` over all pairs, ties = 0.5.
- ``stratified_bootstrap_ci`` -- a bootstrap confidence interval whose point
  estimate is the IQM, returning ``(point, low, high)``.
"""

from __future__ import annotations


import numpy as np

__all__ = ["iqm", "probability_of_improvement", "stratified_bootstrap_ci"]


def iqm(scores: np.ndarray) -> float:
    """Interquartile mean: mean of the middle 50% of ``scores``.

    Parameters
    ----------
    scores:
        One-dimensional array of scores.

    Returns
    -------
    float
        The mean of the values in the ``[25th, 75th]`` percentile band. Values
        are sorted and the lower/upper 25% are trimmed by count.
    """
    s = np.sort(np.asarray(scores, dtype=float))
    n = s.size
    if n == 0:
        return float("nan")
    lo = int(np.floor(n * 0.25))
    hi = int(np.ceil(n * 0.75))
    middle = s[lo:hi]
    if middle.size == 0:
        return float(s.mean())
    return float(middle.mean())


def probability_of_improvement(a: np.ndarray, b: np.ndarray) -> float:
    """Probability that a draw from ``a`` improves on a draw from ``b``.

    Parameters
    ----------
    a, b:
        Score populations (need not be paired or equal length).

    Returns
    -------
    float
        ``P(a > b)`` in ``[0, 1]`` over all pairs, with ties counted as one half.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.size == 0 or b.size == 0:
        return float("nan")
    # Pairwise comparison via broadcasting.
    diff = a[:, None] - b[None, :]
    greater = np.count_nonzero(diff > 0)
    ties = np.count_nonzero(diff == 0)
    total = a.size * b.size
    return float((greater + 0.5 * ties) / total)


def stratified_bootstrap_ci(
    scores: np.ndarray,
    n_boot: int = 2000,
    ci: float = 0.95,
    rng: np.random.Generator | None = None,
) -> tuple[float, float, float]:
    """Bootstrap confidence interval for the IQM of ``scores``.

    Parameters
    ----------
    scores:
        One-dimensional array of run scores.
    n_boot:
        Number of bootstrap replications.
    ci:
        Target two-sided coverage (e.g. ``0.95``).
    rng:
        Optional NumPy generator for reproducibility.

    Returns
    -------
    tuple[float, float, float]
        ``(point, low, high)`` where ``point`` is the IQM of ``scores`` and
        ``low``/``high`` are the percentile bootstrap CI bounds for the IQM.
    """
    s = np.asarray(scores, dtype=float)
    n = s.size
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    if rng is None:
        rng = np.random.default_rng()

    point = iqm(s)
    boot = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        sample = s[rng.integers(0, n, size=n)]
        boot[i] = iqm(sample)
    alpha = 1.0 - ci
    low = float(np.quantile(boot, alpha / 2.0))
    high = float(np.quantile(boot, 1.0 - alpha / 2.0))
    return (point, low, high)
