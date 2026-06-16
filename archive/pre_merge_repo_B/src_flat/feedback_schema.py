"""Distributional feedback schema — the dissertation's novelty artefact (Pillar II).

Turns a vector of quantile samples (from the IQN critic at Z(s0, .) or from empirical
held-out episode returns) into the structured risk profile serialized into the LLM's
reward reflection.

Theory anchor (docs/distributional_feedback_schema.md): a CVaR profile across confidence
levels is a discretisation of the canonical coordinates of law-invariant coherent risk
measures (Kusuoka 2001); spectral measures are weighted quantile integrals (Acerbi 2002).

Hard rules implemented here (CLAUDE.md R5):
  * all tail statistics are computed on SORTED values;
  * `crossing_rate` is computed on the RAW tau-ordered array BEFORE sorting and reported,
    because IQN's sampled-tau design makes quantile crossing more likely than QR-DQN
    (Non-Crossing Quantile Regression, NeurIPS 2020).

Leakage posture: pure function of the supplied sample; no market data access.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np

from .config import get


def _alpha_grid_from_config() -> tuple[float, ...]:
    """The CVaR profile levels, single-sourced from config/inference.yaml (ADR-001:
    a numeric literal in src/ that exists in config/ is a bug). The schema's field
    names (cvar_01..cvar_25) structurally require {1, 5, 10, 25}% to be present —
    `build_feedback` validates that."""
    return tuple(float(a) for a in get("inference.distributional_feedback.alpha_grid"))


def empirical_cvar(sorted_values: np.ndarray, alpha: float) -> float:
    """CVaR_alpha = mean of the worst ceil(alpha*N) values (lower tail of returns).

    `sorted_values` MUST be ascending — enforced here so the R5 sorting rule is
    self-policing rather than a caller convention. For returns, CVaR at smaller alpha
    is more negative (deeper tail), so cvar_01 <= cvar_05 <= ... <= mean.
    """
    if not 0.0 < alpha <= 1.0:
        raise ValueError(f"alpha must be in (0, 1], got {alpha}")
    if sorted_values.shape[0] > 1 and np.any(np.diff(sorted_values) < 0):
        raise ValueError("empirical_cvar requires ASCENDING-sorted values (R5: sort before tail stats)")
    n = sorted_values.shape[0]
    k = max(1, math.ceil(alpha * n))
    return float(np.mean(sorted_values[:k]))


def crossing_rate(raw_tau_ordered: np.ndarray) -> float:
    """Fraction of adjacent pairs that DECREASE in a tau-ascending quantile array.

    A correctly monotone quantile function has rate 0. Computed pre-sort by definition.
    """
    if raw_tau_ordered.shape[0] < 2:
        return 0.0
    diffs = np.diff(raw_tau_ordered)
    return float(np.mean(diffs < 0))


def bowley_skew(sorted_values: np.ndarray) -> float:
    """Robust quartile skewness: (Q3 + Q1 - 2*Q2) / (Q3 - Q1); 0 for symmetric."""
    q1, q2, q3 = np.quantile(sorted_values, [0.25, 0.50, 0.75])
    denom = q3 - q1
    if denom <= 0:
        return 0.0
    return float((q3 + q1 - 2.0 * q2) / denom)


def moment_skew(values: np.ndarray) -> float:
    """Standard third standardized moment (population convention)."""
    mu = values.mean()
    sd = values.std()
    if sd == 0:
        return 0.0
    return float(np.mean(((values - mu) / sd) ** 3))


def left_tail_slope(sorted_values: np.ndarray, tail_alpha: float = 0.10) -> float:
    """OLS slope of quantile value on tau over tau <= tail_alpha (plotting positions).

    Steeper (more negative-to-flat... i.e. LARGER) slope across training checkpoints means
    the lower tail is stretching: the policy is concentrating crash risk. Units: return per
    unit tau.
    """
    n = sorted_values.shape[0]
    taus = (np.arange(1, n + 1) - 0.5) / n  # midpoint plotting positions
    mask = taus <= tail_alpha
    if mask.sum() < 2:
        mask = np.zeros(n, dtype=bool)
        mask[: max(2, int(0.1 * n))] = True
    x = taus[mask]
    y = sorted_values[mask]
    x_c = x - x.mean()
    denom = float(np.dot(x_c, x_c))
    if denom == 0:
        return 0.0
    return float(np.dot(x_c, y - y.mean()) / denom)


@dataclass(frozen=True)
class DistributionalFeedback:
    """The serializable risk profile. `source` labels Z(s0) vs empirical (they differ —
    the divergence is itself the calibration diagnostic, Pillar III)."""

    source: str  # "iqn_z_s0" | "empirical_episode_returns"
    n_quantiles: int
    mean: float
    std: float
    cvar_01: float
    cvar_05: float
    cvar_10: float
    cvar_25: float
    bowley_skew: float
    moment_skew: float
    left_tail_slope: float
    crossing_rate: float

    def to_dict(self, ndigits: int = 6) -> dict:
        return {k: (round(v, ndigits) if isinstance(v, float) else v) for k, v in asdict(self).items()}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True)

    def to_prompt_block(self) -> str:
        """Compact block for the distributional reflection template. Stays well under
        config/llm.yaml: prompt_token_budget_reflection."""
        d = self.to_dict(ndigits=4)
        lines = [
            f"source={d['source']}  n_quantiles={d['n_quantiles']}",
            f"mean={d['mean']:+.4f}  std={d['std']:.4f}",
            (
                f"CVaR profile: 1%={d['cvar_01']:+.4f}  5%={d['cvar_05']:+.4f}  "
                f"10%={d['cvar_10']:+.4f}  25%={d['cvar_25']:+.4f}"
            ),
            (
                f"bowley_skew={d['bowley_skew']:+.4f}  moment_skew={d['moment_skew']:+.4f}  "
                f"left_tail_slope={d['left_tail_slope']:+.4f}  crossing_rate={d['crossing_rate']:.3f}"
            ),
        ]
        return "\n".join(lines)


def build_feedback(
    quantile_values: Sequence[float] | np.ndarray,
    source: str,
    taus: Sequence[float] | np.ndarray | None = None,
    alpha_grid: Sequence[float] | None = None,
) -> DistributionalFeedback:
    """Construct the feedback profile from raw quantile samples.

    Args:
        quantile_values: quantile/return samples. If `taus` is given, values are first
            ordered by ascending tau (so crossing_rate is meaningful); otherwise the
            given order is assumed to already be tau-ascending.
        source: provenance label (see DistributionalFeedback.source).
        taus: optional tau levels matching `quantile_values`.
        alpha_grid: defaults to config inference.distributional_feedback.alpha_grid;
            must contain 0.01, 0.05, 0.10, 0.25 (the schema's fixed fields).
    """
    if alpha_grid is None:
        alpha_grid = _alpha_grid_from_config()
    values = np.asarray(quantile_values, dtype=float).ravel()
    if values.size < 4:
        raise ValueError("need at least 4 quantile samples")
    if not np.all(np.isfinite(values)):
        raise ValueError("quantile samples contain non-finite values")

    if taus is not None:
        taus_arr = np.asarray(taus, dtype=float).ravel()
        if taus_arr.shape != values.shape:
            raise ValueError("taus and quantile_values must have identical shape")
        order = np.argsort(taus_arr, kind="stable")
        values = values[order]

    xrate = crossing_rate(values)            # pre-sort, by definition
    sorted_vals = np.sort(values)            # ALL stats below on sorted values (R5)

    required = {0.01, 0.05, 0.10, 0.25}
    if not required.issubset({round(a, 6) for a in alpha_grid}):
        raise ValueError(f"alpha_grid must include {sorted(required)}")

    return DistributionalFeedback(
        source=source,
        n_quantiles=int(sorted_vals.size),
        mean=float(sorted_vals.mean()),
        std=float(sorted_vals.std()),
        cvar_01=empirical_cvar(sorted_vals, 0.01),
        cvar_05=empirical_cvar(sorted_vals, 0.05),
        cvar_10=empirical_cvar(sorted_vals, 0.10),
        cvar_25=empirical_cvar(sorted_vals, 0.25),
        bowley_skew=bowley_skew(sorted_vals),
        moment_skew=moment_skew(sorted_vals),
        left_tail_slope=left_tail_slope(sorted_vals),
        crossing_rate=xrate,
    )
