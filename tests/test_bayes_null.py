"""Behaviour tests for the report-only Bayesian evidence-for-the-null complement (R67).

Pins the load-bearing properties: BF01 > 1 = evidence FOR the null, the BIC cross-check agrees with the
JZS integral, the prior-robustness curve behaves (the forking-path guard), the ROPE/HDI decision mirrors
TOST, and the whole thing is deterministic and degenerate-safe. Pure scipy/numpy; import-light (no torch).
"""

from __future__ import annotations

import math

import numpy as np

from src.inference.bayes_null import (
    R_GRID,
    bayesian_null_report,
    bf01_robustness_curve,
    bic_bf01,
    hdi,
    jzs_bf10,
)


def test_bf01_direction_null_vs_effect() -> None:
    """A small standardized effect -> BF01 > 1 (evidence for H0); a large one -> BF01 < 1 (against)."""
    assert 1.0 / jzs_bf10(0.3, 30) > 1.0      # near-null
    assert 1.0 / jzs_bf10(2.5, 30) < 1.0      # strong effect


def test_bic_cross_check_agrees_with_jzs() -> None:
    """The prior-free BIC BF01 agrees with the JZS BF01 within the known ~2-15% gap (a free robustness)."""
    for t, n in [(0.5, 20), (0.3, 30), (1.0, 40)]:
        jzs = 1.0 / jzs_bf10(t, n)
        bic = bic_bf01(t, n)
        assert abs(bic - jzs) / jzs < 0.20


def test_robustness_curve_keys_and_monotone_for_small_effect() -> None:
    """The curve spans the pre-declared R_GRID and, for a SMALL effect, BF01 grows with the prior width
    (the Bartlett/Jeffreys-Lindley hazard the fixed-r + curve design discloses rather than hides)."""
    curve = bf01_robustness_curve(0.3, 30)
    assert set(curve) == {float(r) for r in R_GRID}
    vals = [curve[float(r)] for r in R_GRID]
    assert all(b > a for a, b in zip(vals, vals[1:]))  # strictly increasing in r for a near-null


def test_hdi_is_an_interval_covering_about_the_mass() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(0.0, 1.0, 5000)
    lo, hi = hdi(x, mass=0.90)
    assert lo < hi
    assert 0.86 <= float(((x >= lo) & (x <= hi)).mean()) <= 0.94  # ~90% of mass inside


def test_report_evidence_for_equivalence_on_tight_null() -> None:
    """Tiny, low-variance differences well inside the ROPE -> 'evidence_for_practical_equivalence',
    BF01 > threshold across the whole band, and the credible interval sits inside the ROPE."""
    rng = np.random.default_rng(1)
    diffs = rng.normal(0.0, 0.01, 30)  # |effect| << SESOI=0.05, tiny spread
    rep = bayesian_null_report(diffs, sesoi=0.05)
    assert rep["status"] == "ok"
    assert rep["bf01"] > 3.0 and rep["robust_for_null"] is True
    assert rep["hdi_in_rope"] is True
    assert rep["verdict"] == "evidence_for_practical_equivalence"
    assert 0.0 <= rep["posterior"]["rope_mass"] <= 1.0


def test_report_evidence_against_null_on_strong_effect() -> None:
    rng = np.random.default_rng(2)
    diffs = rng.normal(0.5, 0.1, 30)  # large standardized effect
    rep = bayesian_null_report(diffs, sesoi=0.05)
    assert rep["bf01"] < 1.0
    assert rep["verdict"] == "evidence_against_null"


def test_report_is_deterministic_and_degenerate_safe() -> None:
    diffs = np.array([0.01, -0.02, 0.0, 0.015, -0.005] * 6, dtype=float)
    a = bayesian_null_report(diffs, sesoi=0.05)
    b = bayesian_null_report(diffs, sesoi=0.05)
    assert a == b  # deterministic
    # all-constant zero differences: exact point null, ROPE mass 1, evidence for the null
    zero = bayesian_null_report(np.zeros(30), sesoi=0.05)
    assert zero["status"] == "ok"
    assert zero["posterior"]["rope_mass"] == 1.0
    assert zero["bf01"] > 1.0
    assert math.isfinite(zero["t"])  # t=0, not NaN/inf


def test_report_insufficient_n() -> None:
    assert bayesian_null_report(np.array([0.1]), sesoi=0.05)["status"] == "insufficient"


def test_uses_bootstrap_draws_for_hdi_when_given() -> None:
    """When bootstrap draws are supplied the HDI is taken from them (the existing paired-seed bootstrap),
    not the conjugate-t interval."""
    rng = np.random.default_rng(3)
    diffs = rng.normal(0.0, 0.01, 30)
    draws = rng.normal(0.0, 0.2, 4000)  # deliberately wide -> HDI spills outside the ROPE
    rep = bayesian_null_report(diffs, sesoi=0.05, bootstrap_draws=draws)
    assert rep["hdi_in_rope"] is False  # the wide bootstrap HDI, not the tight conjugate interval
