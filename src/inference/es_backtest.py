"""Comparative Expected-Shortfall (CVaR) backtesting via the jointly-elicitable (VaR, ES) pair.

Closes the methodology gap that **ES alone is not elicitable** — so no strictly consistent loss exists
for ES by itself — whereas the **pair (VaR_alpha, ES_alpha) IS jointly elicitable** (Fissler & Ziegel,
2016, *Higher order elicitability and Osband's principle*, Ann. Statist. 44(4):1680-1707). That joint
elicitability licenses a strictly consistent scoring function, and comparing the *tail-forecast accuracy*
of two models is then a **Diebold-Mariano-style comparative backtest** on the per-period score
differential (Nolde & Ziegel, 2017, *Elicitability and backtesting*, Ann. Appl. Statist.
11(4):1833-1874). The score-difference variance may be estimated by a HAC estimator or the stationary
bootstrap (the latter reused here).

Scope / what this is NOT (read carefully — these answer different questions):
  * THIS module answers: "does risk-FORECAST model 1 predict the tail better than model 2 on the SAME
    realized return series?" — a *comparative backtest* (Nolde-Ziegel). Use it e.g. to check whether the
    measurement instrument's (VaR, ES) forecasts beat a benchmark's.
  * Comparing the *realized* CVaR of two DIFFERENT return series (e.g. the distributional vs scalar arm,
    which have different policies and hence different realizations) is a TWO-SAMPLE comparison of the ES
    functional. No published named test exists for that; use the studentized stationary bootstrap in
    ``src.inference.bootstrap.cvar_difference_test`` (the Ledoit-Wolf-for-Sharpe analogue).

Power caveat (audit B-7 / Bauer 2025, arXiv:2505.23333): comparative tail-risk tests have **low power at
the most extreme quantiles** (alpha = 1%, 2.5%) and short out-of-sample windows; power improves with
alpha and OOS length. Report this for CVaR-1% comparisons.

Convention: lower tail at level ``alpha`` (small, e.g. 0.05); ``var`` = the alpha-quantile of returns,
``es`` = E[r | r <= var] <= var; both negative for a loss tail. The scoring function is the FZ0
(0-homogeneous) strictly consistent loss (Patton, Ziegel & Chen 2019; GAS::FZLoss):

    S(v, e, r) = -(1 / (alpha * e)) * 1{r <= v} * (v - r) + v / e + log(-e) - 1,   e < 0.
"""

from __future__ import annotations

import numpy as np

from src.inference.bootstrap import stationary_bootstrap_indices

__all__ = ["fz0_loss", "var_es_estimates", "comparative_es_backtest"]


def fz0_loss(
    returns: np.ndarray,
    var: float | np.ndarray,
    es: float | np.ndarray,
    alpha: float,
) -> np.ndarray:
    """Per-observation FZ0 strictly consistent score for the (VaR_alpha, ES_alpha) pair.

    Strict consistency: ``E[fz0_loss]`` is uniquely minimized (over ``(v, e)``) at the true
    ``(VaR_alpha, ES_alpha)`` — this is the property exploited by the comparative backtest and asserted
    in the tests.

    Parameters
    ----------
    returns : np.ndarray
        Realized return series (lower values = worse).
    var, es : float or np.ndarray
        The (VaR, ES) forecast(s); scalar (constant forecast) or per-period arrays. ``es`` must be < 0.
    alpha : float
        Tail level in (0, 1).

    Returns
    -------
    np.ndarray
        The per-observation scores (same length as ``returns``).
    """
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    r = np.asarray(returns, dtype=float)
    v = np.asarray(var, dtype=float)
    e = np.asarray(es, dtype=float)
    if np.any(e >= 0.0):
        raise ValueError("es must be strictly negative (a loss) for the FZ0 score")
    hit = (r <= v).astype(float)
    return -(1.0 / (alpha * e)) * hit * (v - r) + v / e + np.log(-e) - 1.0


def var_es_estimates(returns: np.ndarray, alpha: float) -> tuple[float, float]:
    """Empirical (VaR_alpha, ES_alpha) of a return series (lower tail).

    Returns ``(var, es)`` with ``var`` the alpha-quantile and ``es`` the mean of the worst
    ``ceil(alpha * T)`` returns.
    """
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be in (0, 1)")
    r = np.sort(np.asarray(returns, dtype=float))
    k = max(1, int(np.ceil(alpha * r.size)))
    return float(np.quantile(r, alpha)), float(r[:k].mean())


def comparative_es_backtest(
    realized: np.ndarray,
    forecast1: tuple[float | np.ndarray, float | np.ndarray],
    forecast2: tuple[float | np.ndarray, float | np.ndarray],
    alpha: float = 0.05,
    p: float = 0.1,
    n_boot: int = 2000,
    rng: np.random.Generator | None = None,
) -> dict[str, object]:
    """Diebold-Mariano comparative ES backtest (Nolde & Ziegel, 2017) on a common realized series.

    Tests H0: the two (VaR, ES) forecasts have equal predictive accuracy for the tail, via the mean of
    the per-period FZ0 score differential ``d_t = S(f1) - S(f2)``. The standard error of ``mean(d)`` is
    estimated by the stationary bootstrap (Politis-Romano 1994), a valid HAC-robust choice for the
    autocorrelated score differential.

    Parameters
    ----------
    realized : np.ndarray
        The common realized return series both forecasts are scored against.
    forecast1, forecast2 : (var, es)
        Each model's (VaR, ES) forecast — scalar or per-period array (es < 0).
    alpha : float
        Tail level.
    p, n_boot, rng :
        Stationary-bootstrap block-restart probability, replications, and generator.

    Returns
    -------
    dict
        ``{"mean_score_diff", "stat", "pvalue", "better"}``. ``mean_score_diff < 0`` => model 1 scores
        lower (better tail forecast); ``"better"`` is "model1" / "model2" / "tie".
    """
    r = np.asarray(realized, dtype=float)
    s1 = fz0_loss(r, forecast1[0], forecast1[1], alpha)
    s2 = fz0_loss(r, forecast2[0], forecast2[1], alpha)
    d = s1 - s2
    obs = float(d.mean())
    if rng is None:
        rng = np.random.default_rng()

    n = d.size
    boot = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        boot[i] = d[stationary_bootstrap_indices(n, p, rng)].mean()
    se = boot.std(ddof=1)

    if se > 0.0 and np.isfinite(se):
        stat = obs / se
        centred = (boot - obs) / se
        pvalue = float((np.abs(centred) >= abs(stat)).mean())
    else:
        stat, pvalue = 0.0, 1.0
    pvalue = min(1.0, max(pvalue, 1.0 / (n_boot + 1)))

    better = "model1" if obs < 0 else "model2" if obs > 0 else "tie"
    return {"mean_score_diff": obs, "stat": float(stat), "pvalue": pvalue, "better": better}
