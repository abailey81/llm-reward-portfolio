"""Distributional measurement estimator — the project's core contribution (B.4).

This estimator measures the *realized-return distribution* that the LLM
reward-designer is fed in the distributional arm, decoupled from the agent's
critic (audit A-1). It is computed on the **training-period** realized portfolio
log-returns (audit B-2): measuring on validation and then selecting on validation
would re-introduce overfitting, so the LLM shapes the in-sample distribution while
the agent is judged out-of-sample.

Estimator design (FINAL_PLAN F.2, B.4, audit B-1):
  - EMPIRICAL is PRIMARY for the body of the distribution (CVaR / quantiles /
    left-tail mass / robust skew) — for a 1-D sample the empirical quantile is the
    efficient estimator. Used for alpha in {25%, 10%}.
  - GENERALIZED-PARETO / EVT tail fit (per EX-DRL) for the extreme levels
    (CVaR-5%, CVaR-1%): the tail holds only ~7-37 observations, so an EVT fit makes
    those signals estimable rather than sample-noise. A neural quantile network is
    NOT used for the headline statistics.
  - left_tail_mass and robust_skew are derived from empirical quantiles (B.10).

Frozen tail-diagnostic set (returned by `tail_stats`, exactly these keys):
  cvar_01, cvar_05, cvar_10, cvar_25, left_tail_mass, robust_skew.
  cvar_01 is RETAINED BUT EXPLICITLY FLAGGED HIGH-VARIANCE (audit B-7); it is the
  EVT-estimated extreme and must be documented as such wherever it is reported.

EVT-tail CVaR derivation (peaks-over-threshold). Working on losses ``L = -returns``
with a high threshold ``u`` (the empirical loss-quantile at ``threshold_q``), the
exceedances ``Y = L - u | L > u`` follow a Generalized-Pareto law GPD(xi, beta).
With tail probability ``p`` (= ``alpha``) and tail-exceedance fraction
``F_u = P(L > u)`` the loss Value-at-Risk and Conditional VaR are::

    VaR_p  = u + (beta / xi) * ((p / F_u) ** (-xi) - 1)            (xi != 0)
    CVaR_p = (VaR_p + beta - xi * u) / (1 - xi)                    (xi < 1)

and the (signed) return-space CVaR reported to callers is ``-CVaR_p``.

Audit refs: B-1 (empirical primary + EVT tails), B-2 (measure on training returns),
B-7 (CVaR-1% kept-but-flagged).
"""

from __future__ import annotations

import math

import numpy as np
from scipy import stats

#: CVaR-1% is the EVT-estimated extreme; it is retained but flagged high-variance
#: (audit B-7). Reported wherever cvar_01 appears.
CVAR_01_HIGH_VARIANCE_NOTE = (
    "cvar_01 is an EVT-extrapolated extreme estimated from few tail "
    "observations and is high-variance (audit B-7)."
)

#: Levels at or above this fraction use the empirical estimator for CVaR; below it,
#: the EVT/GPD tail fit is used (audit B-1).
EVT_ALPHA_CUTOFF = 0.05

#: Pre-registered multiplier for left_tail_mass = P(return < -k * std) (B.10).
LEFT_TAIL_K = 2.0


class ReturnDistribution:
    """Empirical-body + EVT-tail estimator over realized training returns.

    Fit once on the training-period realized portfolio log-returns, then query
    quantiles, CVaR at a level, or the full frozen tail-diagnostic set. See the
    module docstring and FINAL_PLAN F.2 for the algorithm and audit references.

    Attributes
    ----------
    sorted_returns : np.ndarray
        The training returns sorted ascending.
    T : int
        Number of training observations.
    threshold_q : float
        Lower-tail probability defining the EVT threshold (default 0.10).
    xi, beta, u, exceed_frac : float
        Fitted GPD shape and scale, the loss threshold, and the fraction of losses
        exceeding it.
    """

    def __init__(self, threshold_q: float = 0.10) -> None:
        self.threshold_q = float(threshold_q)
        self.sorted_returns: np.ndarray | None = None
        self.T: int = 0
        self.xi: float = float("nan")
        self.beta: float = float("nan")
        self.u: float = float("nan")
        self.exceed_frac: float = float("nan")

    def fit(self, train_realized_returns: np.ndarray) -> "ReturnDistribution":
        """Sort the training returns and fit the EVT lower-tail model.

        Parameters
        ----------
        train_realized_returns : np.ndarray
            1-D array of training-period realized portfolio log-returns
            (anonymized; no tickers/dates).

        Returns
        -------
        ReturnDistribution
            ``self``, fitted.

        Raises
        ------
        ValueError
            If the input is empty or not 1-D after flattening.
        """
        arr = np.asarray(train_realized_returns, dtype=float).ravel()
        arr = arr[np.isfinite(arr)]
        if arr.size == 0:
            raise ValueError("train_realized_returns must be non-empty and finite")

        self.sorted_returns = np.sort(arr)
        self.T = int(arr.size)

        # Peaks-over-threshold on losses L = -returns.
        losses = -arr
        self.u = float(np.quantile(losses, 1.0 - self.threshold_q))
        exceedances = losses[losses > self.u] - self.u
        self.exceed_frac = float(exceedances.size) / float(self.T)

        if exceedances.size >= 2:
            # Fit GPD with location fixed at 0 (exceedances are >= 0 by construction).
            xi, _loc, beta = stats.genpareto.fit(exceedances, floc=0.0)
            self.xi = float(xi)
            self.beta = float(beta)
        else:
            # Too few exceedances to fit; fall back to exponential-tail (xi -> 0).
            self.xi = 0.0
            self.beta = float(exceedances.mean()) if exceedances.size else float("nan")

        return self

    def _check_fitted(self) -> np.ndarray:
        if self.sorted_returns is None:
            raise RuntimeError("ReturnDistribution.fit must be called before querying")
        return self.sorted_returns

    def quantiles(self, taus: list[float]) -> dict[float, float]:
        """Return empirical quantiles of the fitted return sample.

        Parameters
        ----------
        taus : list of float
            Quantile levels in (0, 1), e.g. [0.05, 0.10, 0.25, 0.50, 0.95].

        Returns
        -------
        dict
            Mapping from each tau to its empirical quantile.
        """
        arr = self._check_fitted()
        return {float(t): float(np.quantile(arr, t)) for t in taus}

    def _empirical_cvar(self, alpha: float) -> float:
        """Empirical CVaR: mean of the worst ceil(alpha*T) returns (signed)."""
        arr = self._check_fitted()
        n = max(1, math.ceil(alpha * self.T))
        worst = arr[:n]
        return float(worst.mean())

    def _evt_cvar(self, alpha: float) -> float:
        """EVT/GPD-based CVaR at level alpha (signed return-space).

        Uses the fitted (xi, beta, u, exceed_frac) per the peaks-over-threshold
        formulas in the module docstring. Falls back to empirical if the level is
        not in the fitted tail or the fit is degenerate.
        """
        xi, beta, u, fu = self.xi, self.beta, self.u, self.exceed_frac
        if not (np.isfinite(beta) and np.isfinite(u) and fu > 0.0):
            return self._empirical_cvar(alpha)
        # The POT approximation is only valid for alpha within the tail mass.
        if alpha > fu:
            return self._empirical_cvar(alpha)

        if abs(xi) < 1e-8:
            # xi -> 0: exponential tail.
            var_loss = u + beta * math.log(fu / alpha)
            cvar_loss = var_loss + beta
        else:
            var_loss = u + (beta / xi) * ((alpha / fu) ** (-xi) - 1.0)
            if xi >= 1.0:
                # Infinite-mean tail; CVaR undefined — fall back to empirical.
                return self._empirical_cvar(alpha)
            cvar_loss = (var_loss + beta - xi * u) / (1.0 - xi)
        return -float(cvar_loss)

    def cvar(self, alpha: float, *, method: str = "auto") -> float:
        """Conditional Value-at-Risk at level alpha (mean of the worst alpha tail).

        For ``alpha`` >= :data:`EVT_ALPHA_CUTOFF` the empirical estimator is used;
        for smaller ``alpha`` the EVT/GPD tail fit is used (audit B-1). cvar_01 is
        therefore EVT-estimated and high-variance (audit B-7,
        :data:`CVAR_01_HIGH_VARIANCE_NOTE`).

        Parameters
        ----------
        alpha : float
            Tail probability level, e.g. 0.01, 0.05, 0.10, 0.25.
        method : {"auto", "empirical", "evt"}, optional
            Force an estimator for cross-checking EVT against empirical. ``"auto"``
            (default) routes by ``alpha`` as described above.

        Returns
        -------
        float
            The (signed) CVaR at level alpha (negative for a loss tail). Monotone
            non-increasing as ``alpha`` shrinks.
        """
        self._check_fitted()
        if not 0.0 < alpha < 1.0:
            raise ValueError("alpha must be in (0, 1)")
        if method == "empirical":
            return self._empirical_cvar(alpha)
        if method == "evt":
            return self._evt_cvar(alpha)
        if method != "auto":
            raise ValueError(f"unknown method: {method!r}")
        if alpha <= EVT_ALPHA_CUTOFF:
            return self._evt_cvar(alpha)
        return self._empirical_cvar(alpha)

    def tail_stats(self) -> dict:
        """Return the frozen tail-diagnostic set fed to the distributional arm.

        Returns EXACTLY the keys:
            cvar_01, cvar_05, cvar_10, cvar_25, left_tail_mass, robust_skew.

        cvar_01 is the EVT-estimated extreme and is documented high-variance
        (B-7, :data:`CVAR_01_HIGH_VARIANCE_NOTE`). left_tail_mass and robust_skew
        are derived from empirical quantiles (B.10):

            left_tail_mass = mean(returns < -k * std), k = 2.0
            robust_skew    = ((Q95 - Q50) - (Q50 - Q05)) / (Q95 - Q05 + eps)

        This is the (quantile-based) Bowley skewness, written so that it is
        NEGATIVE when the left tail is longer, per the frozen design's stated
        sign convention. Equivalently ``-((Q50-Q05)-(Q95-Q50))/(Q95-Q05+eps)``.

        Returns
        -------
        dict
            Dict with exactly the six frozen fields above.
        """
        arr = self._check_fitted()
        q = self.quantiles([0.05, 0.50, 0.95])
        q05, q50, q95 = q[0.05], q[0.50], q[0.95]
        eps = 1e-12
        std = float(arr.std())
        left_tail_mass = float(np.mean(arr < -LEFT_TAIL_K * std))
        robust_skew = ((q95 - q50) - (q50 - q05)) / ((q95 - q05) + eps)
        return {
            "cvar_01": self.cvar(0.01),
            "cvar_05": self.cvar(0.05),
            "cvar_10": self.cvar(0.10),
            "cvar_25": self.cvar(0.25),
            "left_tail_mass": left_tail_mass,
            "robust_skew": float(robust_skew),
        }

    def threshold_sensitivity(
        self,
        alpha: float = 0.01,
        threshold_qs: tuple[float, ...] = (0.05, 0.10, 0.15, 0.20),
    ) -> dict[str, float]:
        """Diagnostic for the POT bias-variance trade-off (deep-research #2, audit B-7).

        Re-estimates the EVT CVaR at level ``alpha`` across several peaks-over-threshold
        choices and reports the spread. The extreme-tail CVaR (esp. CVaR-1% on ~750
        returns, ~7-8 exceedances) is sensitive to the threshold; a large spread flags an
        unstable estimate to treat with caution. Side-effect-free (uses fresh fits, does
        not mutate ``self``).

        NOTE: a *bias-corrected* POT estimator (Troop et al. 2021) is the frozen Phase-1
        enhancement (PREREGISTRATION §4); this method is the accompanying diagnostic.

        Parameters
        ----------
        alpha : float
            Tail level to probe (default 0.01).
        threshold_qs : tuple of float
            Lower-tail threshold probabilities to refit at.

        Returns
        -------
        dict
            ``{"<q>": cvar, ..., "spread": max-min, "cv": spread/|mean|}``.
        """
        arr = self._check_fitted()
        per_threshold: dict[str, float] = {}
        vals: list[float] = []
        for q in threshold_qs:
            cv = ReturnDistribution(threshold_q=q).fit(arr)._evt_cvar(alpha)
            per_threshold[f"{q:.2f}"] = cv
            vals.append(cv)
        v = np.asarray(vals, dtype=float)
        spread = float(np.nanmax(v) - np.nanmin(v))
        mean = float(np.nanmean(v))
        per_threshold["spread"] = spread
        per_threshold["cv"] = float(spread / (abs(mean) + 1e-12))
        return per_threshold
