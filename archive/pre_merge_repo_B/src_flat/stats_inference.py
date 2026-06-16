"""Selection-aware inference (Pillar V) — the 'faultless execution' statistical core.

Implements, formula-exact with citations:
  * Probabilistic Sharpe Ratio (PSR) — Bailey & López de Prado (2012).
  * Deflated Sharpe Ratio (DSR) with the expected-maximum-SR benchmark using the
    Euler–Mascheroni term — Bailey & López de Prado (2014), JPM 40(5).
  * Minimum Track Record Length (MinTRL) — same source.
  * Probability of Backtest Overfitting via CSCV — Bailey, Borwein, López de Prado & Zhu.
  * TrialLedger — programmatic enforcement of PREREGISTRATION §4's trial-count rule:
    N = EVERY candidate evaluated across all arms (CLAUDE.md R5).

HARD RULE (R5): all Sharpe inputs are UNANNUALISED (per-period). The ledger warns on
suspiciously large values that look annualised.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import combinations
from typing import Callable, Sequence

import numpy as np
from scipy.stats import norm

EULER_MASCHERONI = 0.5772156649015329


# --------------------------------------------------------------------------- PSR / DSR
def probabilistic_sharpe_ratio(
    sr: float, sr_benchmark: float, n_obs: int, skew: float, kurt: float
) -> float:
    """PSR = Phi( (SR - SR*) * sqrt(T - 1) / sqrt(1 - g3*SR + ((g4 - 1)/4) * SR^2) ).

    kurt is RAW kurtosis (normal = 3), per Bailey & López de Prado. Unannualised SRs.
    """
    if n_obs < 2:
        raise ValueError("n_obs must be >= 2")
    denom_sq = 1.0 - skew * sr + ((kurt - 1.0) / 4.0) * sr**2
    if denom_sq <= 0:
        # Pathological higher moments: variance estimate of SR non-positive -> undefined.
        return float("nan")
    z = (sr - sr_benchmark) * math.sqrt(n_obs - 1) / math.sqrt(denom_sq)
    return float(norm.cdf(z))


def expected_max_sharpe(n_trials: int, var_trial_srs: float) -> float:
    """SR0 = sqrt(V[SR_n]) * [ (1 - g) * Phi^-1(1 - 1/N) + g * Phi^-1(1 - 1/(N*e)) ].

    The expected maximum Sharpe among N independent zero-skill trials with cross-sectional
    variance V[SR_n]; g = Euler–Mascheroni. N=1 (no selection) => SR0 = 0 by construction.
    """
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")
    if var_trial_srs < 0:
        raise ValueError("variance cannot be negative")
    if n_trials == 1 or var_trial_srs == 0.0:
        return 0.0
    g = EULER_MASCHERONI
    term = (1.0 - g) * norm.ppf(1.0 - 1.0 / n_trials) + g * norm.ppf(
        1.0 - 1.0 / (n_trials * math.e)
    )
    return float(math.sqrt(var_trial_srs) * term)


def deflated_sharpe_ratio(
    sr_selected: float,
    trial_srs: Sequence[float],
    n_obs: int,
    skew: float,
    kurt: float,
) -> dict:
    """DSR = PSR evaluated against SR0 computed from the FULL trial record.

    `trial_srs` must contain every candidate evaluated (all arms, all restarts) —
    enforce via TrialLedger, never a hand-picked subset.
    Returns dict with dsr, sr0, n_trials, var_trials for table-ready reporting.
    """
    srs = np.asarray(list(trial_srs), dtype=float)
    if srs.size < 1:
        raise ValueError("trial_srs must be non-empty")
    n_trials = int(srs.size)
    var_trials = float(srs.var(ddof=1)) if n_trials > 1 else 0.0
    sr0 = expected_max_sharpe(n_trials, var_trials)
    dsr = probabilistic_sharpe_ratio(sr_selected, sr0, n_obs, skew, kurt)
    return {"dsr": dsr, "sr0": sr0, "n_trials": n_trials, "var_trials": var_trials}


def min_track_record_length(
    sr: float, sr_benchmark: float, skew: float, kurt: float, alpha: float = 0.05
) -> float:
    """MinTRL = 1 + [1 - g3*SR + ((g4-1)/4)*SR^2] * ( Phi^-1(1-alpha) / (SR - SR*) )^2.

    Smallest sample length such that PSR(SR*) >= 1 - alpha. Requires SR > SR*.
    """
    if sr <= sr_benchmark:
        return float("inf")
    num = 1.0 - skew * sr + ((kurt - 1.0) / 4.0) * sr**2
    z = norm.ppf(1.0 - alpha)
    return float(1.0 + num * (z / (sr - sr_benchmark)) ** 2)


# ------------------------------------------------------------------------- PBO / CSCV
def _sharpe(x: np.ndarray) -> float:
    sd = x.std(ddof=1)
    return float(x.mean() / sd) if sd > 0 else 0.0


def pbo_cscv(
    pnl_matrix: np.ndarray,
    n_blocks: int = 16,
    metric: Callable[[np.ndarray], float] = _sharpe,
    max_combinations: int | None = None,
    rng: np.random.Generator | None = None,
) -> dict:
    """Probability of Backtest Overfitting via Combinatorially Symmetric Cross-Validation.

    Bailey, Borwein, López de Prado & Zhu. Steps: split the T x N per-period PnL matrix
    into S even row-blocks; for every C(S, S/2) IS/OOS split: select argmax IS metric,
    take its OOS relative rank w = rank/(N+1), logit lambda = ln(w/(1-w));
    PBO = fraction(lambda <= 0), i.e. IS-best at-or-below the OOS median.

    Args:
        pnl_matrix: shape (T, N) per-period returns for N strategies/candidates.
        n_blocks: S (even, >= 4; PREREGISTRATION fixes 16).
        max_combinations: optional cap with deterministic subsampling (tests only —
            production runs use the full C(S, S/2) set).
    Returns dict: pbo, lambdas (np.ndarray), n_combinations.
    """
    pnl = np.asarray(pnl_matrix, dtype=float)
    if pnl.ndim != 2:
        raise ValueError("pnl_matrix must be 2-D (T x N)")
    t, n = pnl.shape
    if n_blocks % 2 != 0 or n_blocks < 4:
        raise ValueError("n_blocks must be even and >= 4")
    if t < n_blocks:
        raise ValueError("not enough rows for the requested number of blocks")

    blocks = np.array_split(np.arange(t), n_blocks)
    combos = list(combinations(range(n_blocks), n_blocks // 2))
    if max_combinations is not None and len(combos) > max_combinations:
        rng = rng or np.random.default_rng(0)
        idx = rng.choice(len(combos), size=max_combinations, replace=False)
        combos = [combos[i] for i in sorted(idx)]

    lambdas = np.empty(len(combos))
    for c_i, is_blocks in enumerate(combos):
        is_mask = np.concatenate([blocks[b] for b in is_blocks])
        oos_mask = np.concatenate([blocks[b] for b in range(n_blocks) if b not in is_blocks])
        is_metric = np.apply_along_axis(metric, 0, pnl[is_mask])
        oos_metric = np.apply_along_axis(metric, 0, pnl[oos_mask])
        best = int(np.argmax(is_metric))
        # relative OOS rank of the IS-best (1 = worst), w in (0, 1)
        rank = float(np.sum(oos_metric <= oos_metric[best]))
        w = rank / (n + 1.0)
        lambdas[c_i] = math.log(w / (1.0 - w))

    return {
        "pbo": float(np.mean(lambdas <= 0)),
        "lambdas": lambdas,
        "n_combinations": len(combos),
    }


# ------------------------------------------------------------------------ TrialLedger
@dataclass
class TrialRecord:
    arm: str
    candidate_id: str
    sharpe_unannualised: float
    n_obs: int


@dataclass
class TrialLedger:
    """Append-only record of EVERY candidate evaluated on validation fitness.

    PREREGISTRATION §4: the DSR's N is this ledger's length — all arms, all restarts,
    nothing excluded. CLAUDE.md R5 forbids computing DSR on any subset.
    """

    records: list[TrialRecord] = field(default_factory=list)
    _warned: bool = field(default=False, repr=False)

    def register(self, arm: str, candidate_id: str, sharpe_unannualised: float, n_obs: int) -> None:
        if not np.isfinite(sharpe_unannualised):
            raise ValueError("non-finite Sharpe cannot be registered")
        if abs(sharpe_unannualised) > 1.0 and not self._warned:
            # Daily SR ~ 0.06 is already annualised ~1.0; |SR|>1 per-period is almost
            # certainly an annualised figure slipping through (R5 violation).
            import warnings

            warnings.warn(
                "TrialLedger received |SR| > 1.0 — inputs must be UNANNUALISED (R5).",
                stacklevel=2,
            )
            self._warned = True
        self.records.append(TrialRecord(arm, candidate_id, sharpe_unannualised, n_obs))

    @property
    def n_trials(self) -> int:
        return len(self.records)

    @property
    def trial_srs(self) -> np.ndarray:
        return np.array([r.sharpe_unannualised for r in self.records], dtype=float)

    def dsr_for(self, sr_selected: float, n_obs: int, skew: float, kurt: float) -> dict:
        """Headline-table DSR for the selected candidate against the FULL ledger."""
        return deflated_sharpe_ratio(sr_selected, self.trial_srs, n_obs, skew, kurt)
