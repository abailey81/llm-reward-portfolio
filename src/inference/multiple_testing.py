"""Multiple-testing corrections across the arm x metric family (FINAL_PLAN F.11, audit B-8).

Purpose
-------
Control the family-wise error rate / false-discovery rate over the family of
hypotheses formed by the cross-product of arms and held-out metrics.

Methods
-------
- ``benjamini_hochberg`` -- the Benjamini-Hochberg (1995) linear step-up
  procedure controlling the false-discovery rate at level ``q``.
- ``romano_wolf`` -- the Romano & Wolf (2005) stepdown procedure for strong
  control of the family-wise error rate, using a bootstrap null distribution of
  the test statistics (via the max statistic) to account for dependence.
"""

from __future__ import annotations


import numpy as np

__all__ = ["benjamini_hochberg", "romano_wolf"]


def benjamini_hochberg(pvals: np.ndarray, q: float = 0.05) -> np.ndarray:
    """Benjamini-Hochberg FDR control at level ``q``.

    Parameters
    ----------
    pvals:
        One p-value per hypothesis.
    q:
        Target false-discovery rate. The default MIRRORS the registered value
        (``config/inference.yaml: multiplicity.q = 0.05``) — it was ``0.1`` until
        2026-07-26, i.e. TWICE the pre-registered FDR, so any caller that omitted ``q``
        would silently have run a more permissive correction than the design registers.
        The change is behaviour-free today (every call site in ``src/``, ``scripts/`` and
        ``tests/`` passes ``q`` explicitly, so the default was unreachable) and removes the
        trap for future callers. ``config/inference.yaml`` remains the single source of
        truth; production code must keep passing it explicitly rather than lean on this.

    Returns
    -------
    numpy.ndarray
        Boolean array of rejections (``True`` = reject the null), aligned with
        the input order.
    """
    p = np.asarray(pvals, dtype=float)
    m = p.size
    reject = np.zeros(m, dtype=bool)
    if m == 0:
        return reject
    order = np.argsort(p, kind="mergesort")
    sorted_p = p[order]
    # Largest k with p_(k) <= (k/m) * q.
    thresholds = (np.arange(1, m + 1) / m) * q
    below = sorted_p <= thresholds
    if not below.any():
        return reject
    k_max = np.max(np.nonzero(below)[0])  # 0-based index of largest passing rank
    reject[order[: k_max + 1]] = True
    return reject


def romano_wolf(
    stats: np.ndarray,
    boot_stats: np.ndarray,
    alpha: float = 0.05,
) -> np.ndarray:
    """Romano-Wolf stepdown FWER control via a bootstrap max-statistic null.

    Parameters
    ----------
    stats:
        Observed test statistics, one per hypothesis (larger = more evidence
        against the null; e.g. ``|t|`` or a one-sided statistic).
    boot_stats:
        Bootstrap draws of the (centred, null) statistics, shape
        ``(n_boot, n_hypotheses)``.
    alpha:
        Target family-wise error rate.

    Returns
    -------
    numpy.ndarray
        Boolean array of rejections aligned with ``stats``.

    Notes
    -----
    Stepdown: order hypotheses by observed statistic (descending). At each step,
    over the *remaining* (not-yet-rejected) hypotheses, compute the bootstrap
    distribution of the maximum statistic and its ``1 - alpha`` quantile. Reject
    the leading hypothesis if its statistic exceeds this critical value; repeat
    on the remainder. Stop at the first non-rejection.
    """
    s = np.asarray(stats, dtype=float)
    boot = np.asarray(boot_stats, dtype=float)
    m = s.size
    reject = np.zeros(m, dtype=bool)
    if m == 0:
        return reject
    if boot.ndim != 2 or boot.shape[1] != m:
        raise ValueError("boot_stats must have shape (n_boot, n_hypotheses)")

    order = np.argsort(s, kind="mergesort")[::-1]  # descending observed stats
    remaining = list(order)

    while remaining:
        rem_idx = np.array(remaining)
        # Bootstrap max over the remaining hypotheses.
        max_boot = boot[:, rem_idx].max(axis=1)
        crit = np.quantile(max_boot, 1.0 - alpha)
        lead = remaining[0]
        if s[lead] > crit:
            reject[lead] = True
            remaining.pop(0)
        else:
            break
    return reject
