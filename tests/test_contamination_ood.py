"""Synthetic-behaviour tests for the N3 contamination + OOD-stress harnesses.

These are FAST, fully synthetic, and assert the *documented behaviour* of
``src.inference.contamination`` and ``src.inference.ood_stress`` (no campaign data, no GPU):

* TOST: equivalence is declared for a near-zero, tight-CI difference and refused for a shifted
  one; the paired A/B returns invariance on identical-up-to-noise coefficients and flags a
  shifted coefficient.
* the difference-direction complements (Mahalanobis permutation, McNemar) are correctly sized
  under the null and detect a planted effect.
* every harness DEGRADES GRACEFULLY: absent inputs -> ``{"status": "no_data"}``, never a crash,
  never a fabricated number.
* OOD generators return the right shapes, preserve the cross-section, and the GARCH-EVT FHS
  output clears the stylised-facts validation battery on heavy-tailed clustered input.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.inference.contamination import (
    DEFAULT_EQUIVALENCE_SD_FRAC,
    coefficient_mahalanobis_permutation,
    contamination_report,
    cross_model_disagreement,
    named_vs_blinded_oos_gap,
    named_vs_blinded_tost,
    paired_tost,
    post_cutoff_persistence,
    structural_mcnemar,
)
from src.inference.ood_stress import (
    block_bootstrap_paths,
    claims,
    garch_evt_fhs,
    markov_crash_paths,
    optimal_block_length,
    score_paths,
    tail_metrics,
    validate_stylized_facts,
    vol_spike_paths,
)

SEED = 20260624


def _garch_like_panel(n: int = 900, k: int = 4, seed: int = SEED) -> np.ndarray:
    """A heavy-tailed, volatility-clustered, single-factor return panel (stylised-fact rich)."""
    rng = np.random.default_rng(seed)
    # Common volatility-clustering factor via a simple GARCH(1,1) sigma path.
    sig2 = np.empty(n)
    sig2[0] = 1.0
    z = rng.standard_t(6, size=n)  # fat-tailed innovations
    eps = np.empty(n)
    eps[0] = z[0]  # init BEFORE the loop reads eps[t-1]; else t=1 reads uninitialised np.empty memory
    for t in range(1, n):
        sig2[t] = 0.02 + 0.10 * eps[t - 1] ** 2 + 0.87 * sig2[t - 1]
        eps[t] = np.sqrt(sig2[t]) * z[t]
    market = 0.0003 + 0.01 * eps / (np.std(eps) or 1.0)
    betas = np.linspace(0.8, 1.2, k)
    panel = (
        market[:, None] * betas[None, :]
        + 0.004 * rng.standard_normal((n, k))
        + 0.0001 * np.arange(k)[None, :]
    )
    return panel


# ===========================================================================
# contamination.py — TOST (primary)
# ===========================================================================
def test_paired_tost_declares_equivalence_for_tiny_difference() -> None:
    rng = np.random.default_rng(SEED)
    base = rng.standard_normal(40)
    named = base + 0.001 * rng.standard_normal(40)  # essentially identical
    blinded = base + 0.001 * rng.standard_normal(40)
    res = paired_tost(named, blinded, low=-0.5, high=0.5)
    assert res["equivalent"] is True
    assert res["p_tost"] < 0.05
    assert res["low"] < res["ci_low"] and res["ci_high"] < res["high"]


def test_paired_tost_refuses_equivalence_for_shifted_difference() -> None:
    rng = np.random.default_rng(SEED)
    base = rng.standard_normal(40)
    named = base + 2.0  # a large, real shift -> NOT equivalent within +/-0.5
    blinded = base
    res = paired_tost(named, blinded, low=-0.5, high=0.5)
    assert res["equivalent"] is False
    assert res["p_tost"] > 0.05
    assert res["mean_diff"] == pytest.approx(2.0, abs=0.2)


def test_paired_tost_pvalue_is_max_of_one_sided() -> None:
    rng = np.random.default_rng(1)
    a = rng.standard_normal(30)
    b = rng.standard_normal(30)
    res = paired_tost(a, b, low=-0.4, high=0.6)  # asymmetric bounds
    assert res["p_tost"] == pytest.approx(max(res["p_lower"], res["p_upper"]))


def test_paired_tost_degenerate_identical_pairs() -> None:
    x = np.array([0.1, 0.2, 0.3, 0.4])
    res = paired_tost(x, x, low=-0.5, high=0.5)  # zero difference, zero SE
    assert res["equivalent"] is True
    assert res["mean_diff"] == 0.0


def test_paired_tost_validates_inputs() -> None:
    with pytest.raises(ValueError):
        paired_tost(np.zeros(3), np.zeros(4), low=-1, high=1)  # mismatched
    with pytest.raises(ValueError):
        paired_tost(np.zeros(1), np.zeros(1), low=-1, high=1)  # < 2 pairs
    with pytest.raises(ValueError):
        paired_tost(np.zeros(3), np.zeros(3), low=1.0, high=-1.0)  # low >= high


def test_named_vs_blinded_tost_all_equivalent_when_labels_irrelevant() -> None:
    """Identical-up-to-seed-noise coefficients across arms -> bounded contamination (positive).

    NB the seed count here (200) is DELIBERATELY large: the equivalence bound Delta = 0.5*SD is
    tight, so the TOST equivalence claim is underpowered at the campaign's 30 main-experiment
    seeds (see :func:`test_named_vs_blinded_tost_is_underpowered_at_30_seeds`). The named-vs-
    blinded A/B is a CHEAP dedicated sub-experiment (one reward authoring + one eval per seed),
    so it can and MUST run many more seeds than the main campaign to license the positive claim.
    """
    rng = np.random.default_rng(SEED)
    n_seeds, n_coeffs = 200, 4
    truth = np.array([1.0, -0.5, 0.2, 0.0])
    sd = 0.1
    named = truth[None, :] + sd * rng.standard_normal((n_seeds, n_coeffs))
    blinded = truth[None, :] + sd * rng.standard_normal((n_seeds, n_coeffs))
    out = named_vs_blinded_tost(named, blinded, coefficient_names=list("abcd"))
    assert out["status"] == "ok"
    assert out["all_equivalent"] is True
    assert out["fraction_equivalent"] == 1.0
    assert out["equivalence_sd_frac"] == DEFAULT_EQUIVALENCE_SD_FRAC


def test_named_vs_blinded_tost_is_underpowered_at_30_seeds() -> None:
    """Document (in the suite) that Delta=0.5*SD TOST cannot yield 'all equivalent' at n=30.

    This is a load-bearing LIMITATION, not a bug: with 30 seeds the 90% CI half-width on the
    paired mean difference is comparable to Delta=0.5*SD, so a true-zero difference does NOT
    clear the equivalence bound. The harness reports ``all_equivalent=False`` honestly rather
    than fabricating equivalence; the A/B needs more seeds (or a pre-registered wider Delta).
    """
    rng = np.random.default_rng(SEED)
    n_seeds, n_coeffs = 30, 4
    truth = np.array([1.0, -0.5, 0.2, 0.0])
    sd = 0.1
    named = truth[None, :] + sd * rng.standard_normal((n_seeds, n_coeffs))
    blinded = truth[None, :] + sd * rng.standard_normal((n_seeds, n_coeffs))
    out = named_vs_blinded_tost(named, blinded)
    assert out["status"] == "ok"
    assert out["all_equivalent"] is False  # underpowered at Delta=0.5*SD, n=30


def test_named_vs_blinded_tost_flags_a_contaminated_coefficient() -> None:
    rng = np.random.default_rng(SEED)
    n_seeds, n_coeffs = 200, 4
    truth = np.array([1.0, -0.5, 0.2, 0.0])
    sd = 0.1
    named = truth[None, :] + sd * rng.standard_normal((n_seeds, n_coeffs))
    blinded = truth[None, :] + sd * rng.standard_normal((n_seeds, n_coeffs))
    # Coefficient 1 shifts hugely when the data is NAMED (concept contamination).
    named[:, 1] += 1.0
    out = named_vs_blinded_tost(named, blinded)
    assert out["status"] == "ok"
    assert out["all_equivalent"] is False
    assert out["per_coefficient"][1]["equivalent"] is False
    # The untouched coefficients remain equivalent.
    assert out["per_coefficient"][0]["equivalent"] is True


def test_named_vs_blinded_tost_no_data_paths() -> None:
    assert named_vs_blinded_tost(np.zeros((0, 3)), np.zeros((0, 3)))["status"] == "no_data"
    assert named_vs_blinded_tost(np.zeros((5, 3)), np.zeros((5, 2)))["status"] == "no_data"
    assert named_vs_blinded_tost(np.zeros((1, 3)), np.zeros((1, 3)))["status"] == "no_data"


# ===========================================================================
# contamination.py — difference-direction complements
# ===========================================================================
def test_mahalanobis_permutation_is_sized_under_null() -> None:
    """Identical coefficient laws across arms -> permutation p-value should be non-significant."""
    rng = np.random.default_rng(SEED)
    named = rng.standard_normal((25, 3))
    blinded = rng.standard_normal((25, 3))
    res = coefficient_mahalanobis_permutation(named, blinded, n_perm=1000, rng=rng)
    assert res["status"] == "ok"
    assert res["pvalue"] > 0.05


def test_mahalanobis_permutation_detects_a_centroid_shift() -> None:
    rng = np.random.default_rng(SEED)
    named = rng.standard_normal((25, 3)) + np.array([2.0, 0.0, 0.0])
    blinded = rng.standard_normal((25, 3))
    res = coefficient_mahalanobis_permutation(named, blinded, n_perm=1000, rng=rng)
    assert res["status"] == "ok"
    assert res["pvalue"] < 0.05


def test_structural_mcnemar_agreement_and_discord() -> None:
    same = np.array([1, 1, 0, 0, 1, 0])
    res = structural_mcnemar(same, same)
    assert res["pvalue"] == 1.0 and res["n01"] == 0 and res["n10"] == 0
    # A strong, consistent flip (named always has the motif, blinded never).
    named = np.ones(12, dtype=int)
    blinded = np.zeros(12, dtype=int)
    res2 = structural_mcnemar(named, blinded)
    assert res2["n10"] == 12 and res2["n01"] == 0
    assert res2["pvalue"] < 0.05


def test_structural_mcnemar_rejects_non_binary() -> None:
    with pytest.raises(ValueError):
        structural_mcnemar(np.array([0, 1, 2]), np.array([0, 1, 0]))
    assert structural_mcnemar(np.array([], dtype=int), np.array([], dtype=int))["status"] == "no_data"


def test_named_vs_blinded_oos_gap_equivalence_within_sesoi() -> None:
    rng = np.random.default_rng(SEED)
    seeds = range(30)
    named = {s: 0.5 + 0.02 * rng.standard_normal() for s in seeds}
    blinded = {s: 0.5 + 0.02 * rng.standard_normal() for s in seeds}  # same level, tiny noise
    res = named_vs_blinded_oos_gap(named, blinded, sesoi=0.05, rng=rng)
    assert res["status"] == "ok"
    assert res["equivalent"] is True
    # And degrades gracefully with too few shared seeds.
    assert named_vs_blinded_oos_gap({0: 1.0}, {0: 1.0})["status"] == "no_data"


def test_post_cutoff_persistence_runs_and_carries_caveat() -> None:
    rng = np.random.default_rng(SEED)
    seeds = range(20)
    pre = {s: 0.3 + 0.05 * rng.standard_normal() for s in seeds}
    post = {s: 0.28 + 0.05 * rng.standard_normal() for s in seeds}  # gap persists
    res = post_cutoff_persistence(pre, post, rng=rng)
    assert res["status"] == "ok"
    assert "underpowered" in res["caveat"]
    assert np.isfinite(res["pre_iqm"]) and np.isfinite(res["post_iqm"])
    assert post_cutoff_persistence({0: 1.0}, {0: 1.0})["status"] == "no_data"


def test_cross_model_disagreement_small_when_models_agree() -> None:
    rng = np.random.default_rng(SEED)
    truth = np.array([1.0, -0.5, 0.2])
    a = truth[None, :] + 0.1 * rng.standard_normal((20, 3))
    b = truth[None, :] + 0.1 * rng.standard_normal((15, 3))  # different seed count is fine
    res = cross_model_disagreement(a, b, coefficient_names=list("xyz"))
    assert res["status"] == "ok"
    assert res["max_abs_d"] < 1.0  # well within a "small" standardised difference
    # Dimension mismatch -> no_data, not a crash.
    assert cross_model_disagreement(a, np.zeros((10, 2)))["status"] == "no_data"


def test_contamination_report_degrades_on_empty_inputs() -> None:
    rep = contamination_report()
    assert "load_bearing_note" in rep
    for key in ("tost", "mahalanobis", "structural_mcnemar", "oos_gap",
                "post_cutoff_persistence", "cross_model"):
        assert rep[key]["status"] == "no_data"
    # "Min-K" / theatre must NOT silently masquerade as a result.
    assert "MIA" in rep["load_bearing_note"] and "chance" in rep["load_bearing_note"]


def test_contamination_report_runs_available_legs() -> None:
    rng = np.random.default_rng(SEED)
    named = np.array([1.0, -0.5])[None, :] + 0.1 * rng.standard_normal((20, 2))
    blinded = np.array([1.0, -0.5])[None, :] + 0.1 * rng.standard_normal((20, 2))
    rep = contamination_report(named_coeffs=named, blinded_coeffs=blinded, rng=rng)
    assert rep["tost"]["status"] == "ok"
    assert rep["mahalanobis"]["status"] == "ok"
    assert rep["structural_mcnemar"]["status"] == "no_data"  # not provided


# ===========================================================================
# ood_stress.py
# ===========================================================================
def test_block_bootstrap_shape_and_membership() -> None:
    panel = _garch_like_panel()
    rng = np.random.default_rng(SEED)
    paths = block_bootstrap_paths(panel, n_paths=8, rng=rng)
    assert paths.shape == (8, panel.shape[0], panel.shape[1])
    # Every simulated row is a verbatim row of the panel (block bootstrap re-orders, never invents),
    # so the cross-section (row copula) is preserved exactly.
    panel_rows = {tuple(np.round(r, 12)) for r in panel}
    for r in paths[0]:
        assert tuple(np.round(r, 12)) in panel_rows


def test_block_bootstrap_longer_horizon() -> None:
    panel = _garch_like_panel(n=300, k=3)
    paths = block_bootstrap_paths(panel, n_paths=3, horizon=500, rng=np.random.default_rng(2))
    assert paths.shape == (3, 500, 3)


def test_optimal_block_length_positive() -> None:
    panel = _garch_like_panel(n=400, k=3)
    bl = optimal_block_length(panel)
    assert np.isfinite(bl) and bl >= 1.0


def test_vol_spike_scales_variance_mean_preserving() -> None:
    panel = _garch_like_panel(n=400, k=3)
    out = vol_spike_paths(panel, multiplier=4.0)  # variance x4 => std x2
    assert out.shape == (1, panel.shape[0], panel.shape[1])
    np.testing.assert_allclose(out[0].mean(axis=0), panel.mean(axis=0), atol=1e-10)
    ratio = out[0].std(axis=0) / panel.std(axis=0)
    np.testing.assert_allclose(ratio, 2.0, rtol=1e-6)


def test_garch_evt_fhs_shape_and_finiteness() -> None:
    panel = _garch_like_panel(n=600, k=3)
    rng = np.random.default_rng(SEED)
    paths = garch_evt_fhs(panel, n_paths=12, horizon=250, rng=rng)
    assert paths.shape == (12, 250, 3)
    assert np.all(np.isfinite(paths))


@pytest.mark.slow
def test_garch_evt_fhs_passes_stylized_facts() -> None:
    """The FHS output should reproduce fat tails + volatility clustering of the history."""
    panel = _garch_like_panel(n=900, k=4)
    rng = np.random.default_rng(SEED)
    paths = garch_evt_fhs(panel, n_paths=40, horizon=900, rng=rng)
    battery = validate_stylized_facts(paths, panel)
    assert battery["checks"]["fat_tails"] is True
    assert battery["checks"]["vol_clustering"] is True
    assert battery["passed"] is True


def test_garch_evt_fhs_cross_section_flag_runs() -> None:
    panel = _garch_like_panel(n=400, k=3)
    rng = np.random.default_rng(SEED)
    indep = garch_evt_fhs(panel, n_paths=4, horizon=120, preserve_cross_section=False, rng=rng)
    assert indep.shape == (4, 120, 3) and np.all(np.isfinite(indep))


def test_markov_crash_paths_runs_or_degrades() -> None:
    panel = _garch_like_panel(n=600, k=3)
    rng = np.random.default_rng(SEED)
    res = markov_crash_paths(panel, n_paths=6, horizon=200, k_regimes=2, rng=rng)
    assert res["status"] in {"ok", "fit_failed"}
    if res["status"] == "ok":
        assert res["paths"].shape == (6, 200, 3)
        assert np.all(np.isfinite(res["paths"]))
        # Transition columns sum to 1 (valid stochastic matrix).
        np.testing.assert_allclose(res["transition"].sum(axis=0), 1.0, atol=1e-6)
        assert res["n_regimes"] == 2


def test_score_paths_default_equal_weight_and_custom_policy() -> None:
    panel = _garch_like_panel(n=300, k=4)
    paths = block_bootstrap_paths(panel, n_paths=10, rng=np.random.default_rng(3))
    default = score_paths(paths)
    assert default["n_paths"] == 10
    assert set(default["cvar"].keys()) == {0.05, 0.01}
    assert np.isfinite(default["sharpe"]["iqm"])

    # A custom policy closure (the seam for a frozen winner's rolled-out policy).
    def first_asset_only(p: np.ndarray) -> np.ndarray:
        return p[:, :, 0]

    custom = score_paths(paths, policy_returns=first_asset_only)
    assert custom["n_paths"] == 10


def test_tail_metrics_reports_sharpe_and_drawdown_with_tail() -> None:
    rng = np.random.default_rng(SEED)
    port = 0.0005 + 0.01 * rng.standard_normal((20, 400))
    m = tail_metrics(port)
    # Sharpe + drawdown reported ALONGSIDE the tail (over-claim guard: no tautological tail win).
    assert {"sharpe", "max_drawdown", "cvar"} <= set(m)
    assert m["max_drawdown"]["iqm"] >= 0.0
    # CVaR is SIGNED (negative for a loss tail); the 1% tail is no LESS extreme (more negative)
    # than the 5% tail, so cvar_01 <= cvar_05.
    assert m["cvar"][0.01]["iqm"] <= m["cvar"][0.05]["iqm"] + 1e-9


def test_validate_stylized_facts_distinguishes_gaussian_from_garch() -> None:
    panel = _garch_like_panel(n=900, k=3)
    rng = np.random.default_rng(SEED)
    gaussian = rng.standard_normal((20, 900, 3)) * 0.01  # iid -> no clustering, thin tails
    battery = validate_stylized_facts(gaussian, panel)
    # An iid-Gaussian generator should FAIL the volatility-clustering gate.
    assert battery["checks"]["vol_clustering"] is False
    assert battery["passed"] is False


def test_ood_input_validation() -> None:
    with pytest.raises(ValueError):
        block_bootstrap_paths(np.zeros((1, 3)))  # < 2 time steps
    with pytest.raises(ValueError):
        garch_evt_fhs(np.full((10, 2), np.nan))  # non-finite
    with pytest.raises(ValueError):
        vol_spike_paths(_garch_like_panel(n=50, k=2), multiplier=-1.0)


def test_claims_states_load_bearing_distinction() -> None:
    c = claims()
    assert "falsification" in c["can_claim"].lower() or "stress-probe" in c["can_claim"].lower()
    assert "generalisation" in c["cannot_claim"].lower()
    assert "Bauer" in c["power_caveat"]
