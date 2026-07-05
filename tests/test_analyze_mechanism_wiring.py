"""Tests for the report-only mechanism kernel wired into scripts/analyze_campaign.py (ADR-039).

Four DISJOINT, report-only blocks (NEVER gate the frozen m=6 headline; each degrades gracefully):

  1. ``out["responsiveness"]`` — SQ1 fed-tail -> authored-tail-construct-count association (Spearman + CI);
  2. ``out["mediation"]``      — fed (X) -> code (M) -> realised tail Y = cvar(val_returns, 0.05) decomposition;
  3. ``out["regime_stratified"]`` — panel-DEPENDENT; per-arm seed-averaged TEST returns by VIX regime, with a
     CRITICAL labels-length ASSERT that SKIPS (never stratifies) on misalignment;
  4. ``out["named_vs_blinded_structural"]`` / ``out["legible_format_responsiveness"]`` — HONEST DEGRADE to
     ``executed=False`` (the NAMED / legible re-authoring passes do not exist as runnable code).

Synthetic per-candidate records carry ``tail_stats`` + ``reward_source`` + ``val_returns`` (and, for the
frozen-winner TEST records, ``test_returns``); they are written to a real archive via
``src.io.results.write_run`` so the disk-backed ``analyze()`` path exercises the full wiring. A minimal
``Panel`` + ``test_window`` drives the regime block.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import analyze_campaign as AC  # noqa: E402

from src.data.panel import Panel  # noqa: E402
from src.io.results import write_run  # noqa: E402

# A reward-source body carrying ``n`` of the TAIL-shaped constructs (cvar / quantile / drawdown / sortino /
# left_tail_mass), so ``_construct_prevalence`` recovers a tail-construct count M that varies per candidate.
_TAIL_SNIPPETS = ("cvar", "np.percentile(r, 5)", "drawdown", "sortino", "left_tail")


def _reward_source(n_tail: int) -> str:
    body = " + ".join(_TAIL_SNIPPETS[: max(0, n_tail)]) or "mean"
    return f"def reward(r):\n    x = {body}\n    return x\n"


def _search_record(
    i: int, cvar05: float, n_tail: int, *, arm: str = "distributional", generation: int | None = None
) -> dict:
    """A search candidate in the CORRECTED archive shape (2026-07-05 M13 construct fix).

    Serial-faithful semantics: the record's OWN ``feedback_block`` carries the block built FROM this
    candidate (fed to the NEXT generation), while the tail the DESIGNER WAS FED (``cvar05``) rides in
    the archived ``prompt`` — for generation >= 1 only; a generation-0 candidate authors from the
    tail-neutral base prompt and must be gated OUT of the fed set."""
    rng = np.random.default_rng(1000 + i)
    gen = (i // 4) if generation is None else int(generation)
    own_cvar = cvar05 * 1.1 - 0.002  # the candidate's own measured tail differs from the FED one
    prompt = (
        "Improve the reward function. Feedback from the previous candidate:\n"
        f"CVaR 5%: {cvar05:+.4f}\nleft-tail mass: +0.100\n"
        if gen >= 1
        else "Write a reward function for a portfolio agent. (base prompt - no feedback)"
    )
    return {
        "run_id": f"{arm}-search-c{i:02d}",
        "arm": arm,
        "seed": 0,
        "fold": 0,
        "candidate_id": f"c{i:02d}",
        "generation": gen,
        "reward_source_hash": f"hash{i:02d}",
        "reward_source": _reward_source(n_tail),
        # The archived PROMPT is what the designer SAW (the fed block); _was_fed_tail gates on it.
        "prompt": prompt,
        # Own block (fed to the NEXT generation) — must NOT leak into the fed set (M13).
        "feedback_block": f"CVaR 5%: {own_cvar:+.4f}\nleft-tail mass: 0.10",
        "metrics": {
            "val_fitness": 0.1 + 0.001 * i,
            "tail_stats": {
                "cvar_05": own_cvar,
                "cvar_10": own_cvar * 0.9,
                "cvar_25": own_cvar * 0.7,
                "cvar_01": own_cvar * 1.2,
                "left_tail_mass": 0.10,
                "robust_skew": -0.20,
            },
            "val_returns": list(rng.normal(0.0005 + 0.01 * cvar05, 0.01, 200)),
        },
        "wall_clock": 1.0,
        "env_fingerprint": "test",
    }


def _test_record(arm: str, seed: int, returns: np.ndarray) -> dict:
    """A frozen-winner TEST record carrying ``metrics['test_returns']`` (drives the regime block)."""
    return {
        "run_id": f"{arm}-test-s{seed}",
        "arm": arm,
        "seed": seed,
        "fold": 0,
        "candidate_id": f"{arm}-winner",
        "generation": 0,
        "reward_source_hash": "winnerhash",
        "feedback_block": "",
        "metrics": {"val_fitness": 0.2, "test_returns": [float(x) for x in returns]},
        "wall_clock": 1.0,
        "env_fingerprint": "test",
    }


def _write_search_arm(root: Path) -> None:
    """12 tail-FED candidates (gens 1..6, 2 per generation; the FED value is generation-constant as in
    the real loop) with the fed cvar_05 and the authored tail-construct count correlated across
    generations (a non-degenerate X, M, Y — and a non-degenerate REGISTERED delta form, n=5 deltas),
    plus 2 generation-0 candidates that the corrected gate must EXCLUDE (M13)."""
    for i in range(12):
        gen = 1 + i // 2
        fed = -0.05 - 0.004 * gen  # generation-constant fed value, varying across generations
        rec = _search_record(i, cvar05=fed, n_tail=1 + (gen % 5), generation=gen)
        write_run(rec, root / "search" / "distributional")
    for i in (90, 91):  # gen-0: base prompt, fed nothing -> gated out
        rec = _search_record(i, cvar05=-0.05, n_tail=1, generation=0)
        write_run(rec, root / "search" / "distributional")


def _minimal_panel(t: int) -> Panel:
    """A tiny (T, N) panel whose VIX spans calm/normal/stress so label_regimes yields >1 regime."""
    rng = np.random.default_rng(0)
    returns = rng.normal(0.0, 0.01, (t, 3))
    vix = np.linspace(10.0, 30.0, t)  # 10..30 crosses calm<15 and stress>25
    dates = np.arange(t).astype("datetime64[D]")
    asset_ids = np.arange(3)
    return Panel(returns=returns, vix=vix, dates=dates, asset_ids=asset_ids)


# --------------------------------------------------------------------------- #
# 1 + 2 — responsiveness + mediation (panel-independent), via the disk-backed analyze() path
# --------------------------------------------------------------------------- #
def test_responsiveness_and_mediation_fire_ok(tmp_path: Path) -> None:
    _write_search_arm(tmp_path)
    out = AC.analyze(tmp_path)

    # PRIMARY = the registered §2a per-generation DELTA form (gens 1..6 -> 5 deltas); the
    # per-candidate LEVELS association rides along as the clustered descriptive companion.
    assert out["responsiveness"]["status"] == "ok"
    assert out["responsiveness"]["form"] == "registered_generation_deltas"
    assert out["responsiveness"]["n"] == 5
    assert "coef" in out["responsiveness"] and "ci_low" in out["responsiveness"]
    assert out["responsiveness"]["levels_companion"]["n"] == 12  # gen-0 records gated OUT

    assert out["mediation"]["status"] == "ok"
    assert out["mediation"]["n"] == 12  # per-candidate FED level -> code -> outcome
    # the standard mediation decomposition keys are present
    for k in ("a", "b", "c_total", "c_direct", "indirect"):
        assert k in out["mediation"]

    # markdown renderers emit a section (and the mediation one surfaces the endogeneity caveat)
    resp_md = AC.responsiveness_markdown(out["responsiveness"])
    assert "Responsiveness" in resp_md
    assert "FED" in resp_md  # the corrected estimand is stated
    med_md = AC.mediation_markdown(out["mediation"])
    assert "Mediation" in med_md
    assert "endogenous" in med_md.lower()


def test_mechanism_pairs_gate_to_tail_fed_only() -> None:
    """Non-tail-fed candidates AND generation-0 candidates must be excluded from the paired arrays
    (M13: the old gate let gen-0 candidates leak in via their OWN feedback_block)."""
    fed = [_search_record(i, -0.05 - 0.004 * (1 + i // 2), 1 + (i % 3), generation=1 + i // 2)
           for i in range(6)]
    # a non-tail-fed record: no "CVaR 5%:" label in its prompt -> _was_fed_tail False
    not_fed = dict(_search_record(99, -0.09, 2, arm="scalar", generation=2))
    not_fed["prompt"] = "Improve the reward. Feedback: Deflated Sharpe: 0.42"
    not_fed["feedback_block"] = "Deflated Sharpe: 0.42"
    # a gen-0 distributional record whose OWN block carries tail labels — must NOT leak in (M13)
    gen0 = _search_record(98, -0.05, 2, generation=0)
    pairs = AC._mechanism_pairs(fed + [not_fed, gen0])
    assert pairs["x"].size == 6  # scalar + gen-0 records were gated OUT
    assert pairs["m"].size == 6 and pairs["y"].size == 6
    # x is the FED value (from the prompt), not the candidate's own measured tail
    assert pairs["x"][0] == pytest.approx(-0.05 - 0.004 * 1)


def test_responsiveness_mediation_degrade_with_no_tail_fed(tmp_path: Path) -> None:
    """No tail-fed candidates -> the modules return status='no_data' (degrade, never raise)."""
    # a single non-tail-fed scalar candidate
    rec = _search_record(0, -0.05, 0, arm="scalar")
    rec["feedback_block"] = "Deflated Sharpe: 0.4"
    write_run(rec, tmp_path / "search" / "scalar")
    out = AC.analyze(tmp_path)
    assert out["responsiveness"]["status"] == "no_data"
    assert out["mediation"]["status"] == "no_data"


# --------------------------------------------------------------------------- #
# 3 — regime-stratified (panel-DEPENDENT): fires ok when aligned, SKIPS on length mismatch
# --------------------------------------------------------------------------- #
def test_regime_block_fires_when_labels_align(tmp_path: Path) -> None:
    _write_search_arm(tmp_path)
    t_test = 120
    for arm in ("distributional", "scalar"):
        for seed in range(3):
            rng = np.random.default_rng(hash((arm, seed)) % (2**32))
            write_run(_test_record(arm, seed, rng.normal(0, 0.01, t_test)), tmp_path / "test" / arm)
    # panel long enough that [test_window] slices to exactly t_test labels
    test_start = 50
    panel = _minimal_panel(test_start + t_test)
    out = AC.analyze(
        tmp_path, panel=panel, cfg=object(), test_window=(test_start, test_start + t_test)
    )
    rs = out["regime_stratified"]
    assert rs["status"] == "ok", rs
    assert rs["n_dates"] == t_test
    assert rs["regimes"], "at least one regime present"
    # the module's own renderer is used (no new markdown fn) — it renders a table
    md = AC.write_report(out, tmp_path / "report")
    assert "Regime-stratified" in md.read_text(encoding="utf-8")


def test_regime_block_skips_on_length_mismatch(tmp_path: Path) -> None:
    """If the label window length != the common test-series length T, the block SKIPS (never stratifies)."""
    _write_search_arm(tmp_path)
    t_test = 120
    for seed in range(3):
        rng = np.random.default_rng(seed + 7)
        write_run(_test_record("distributional", seed, rng.normal(0, 0.01, t_test)),
                  tmp_path / "test" / "distributional")
    # panel test window is DELIBERATELY shorter than t_test -> labels length != T -> skip
    test_start = 50
    panel = _minimal_panel(test_start + t_test - 30)
    out = AC.analyze(
        tmp_path, panel=panel, cfg=object(), test_window=(test_start, test_start + t_test)
    )
    rs = out["regime_stratified"]
    assert rs["status"] == "skipped"
    assert rs["reason"] == "length/embargo misalignment"
    assert rs["t_common"] == t_test and rs["n_labels"] != t_test


# --------------------------------------------------------------------------- #
# 4 — named-vs-blinded / legible-format: HONEST DEGRADE (executed=False)
# --------------------------------------------------------------------------- #
def test_named_blinded_and_legible_degrade_executed_false(tmp_path: Path) -> None:
    _write_search_arm(tmp_path)
    out = AC.analyze(tmp_path)

    nvb = out["named_vs_blinded_structural"]
    assert nvb["status"] == "no_data" and nvb["executed"] is False
    assert "PREREGISTRATION" in nvb["reason"]

    leg = out["legible_format_responsiveness"]
    assert leg["status"] == "no_data" and leg["executed"] is False
    assert "PREREGISTRATION" in leg["reason"]

    # the one-line disclosure markdown reports NOT RUN / executed=False
    nvb_md = AC.named_vs_blinded_structural_markdown(nvb)
    leg_md = AC.legible_format_responsiveness_markdown(leg)
    assert "NOT RUN" in nvb_md and "executed=False" in nvb_md
    assert "NOT RUN" in leg_md and "executed=False" in leg_md


def test_mechanism_blocks_never_gate_headline(tmp_path: Path) -> None:
    """The four report-only blocks are DISJOINT from the frozen m=6 family — they never touch out['h2']."""
    _write_search_arm(tmp_path)
    out = AC.analyze(tmp_path)
    # all four keys present, and the headline h2 block is unaffected by their presence/status
    for key in ("responsiveness", "mediation", "named_vs_blinded_structural",
                "legible_format_responsiveness"):
        assert key in out
    assert "h2" in out  # the frozen headline still computed independently


# --------------------------------------------------------------------------- #
# P3 — comparative_es_backtest + bayesian_null_report + model_confidence_set wired into analyze()
# --------------------------------------------------------------------------- #
def _p3_test_record(arm: str, seed: int) -> dict:
    """A per-seed frozen-winner TEST record with BOTH test_returns and val_returns (drives ES/bayes/MCS)."""
    rng = np.random.default_rng(hash((arm, seed, "p3")) % (2**32))
    tr = rng.normal(0.0006, 0.012, 250)
    vr = rng.normal(0.0005, 0.012, 250)
    return {
        "run_id": f"{arm}-p3-s{seed}",
        "arm": arm,
        "seed": int(seed),
        "fold": 0,
        "candidate_id": f"{arm}-winner",
        "generation": 0,
        "reward_source_hash": "p3hash",
        "feedback_block": "",
        "metrics": {
            "val_fitness": 0.2,
            "test_returns": [float(x) for x in tr],
            "val_returns": [float(x) for x in vr],
        },
        "wall_clock": 1.0,
        "env_fingerprint": "test",
    }


def _write_p3_archive(root: Path) -> None:
    """Search (tail-fed) + per-seed TEST records for distributional + the three H2 comparators."""
    _write_search_arm(root)
    for arm in ("distributional", "scalar", "placebo", "scalar_cvar5"):
        for seed in range(4):
            write_run(_p3_test_record(arm, seed), root / "test" / arm)


def test_p3_blocks_are_emitted_disjoint_and_do_not_gate(tmp_path: Path) -> None:
    """The three built-but-uninvoked analyses are wired as DISJOINT report-only blocks in analyze()."""
    _write_p3_archive(tmp_path)
    out = AC.analyze(tmp_path)

    # all three keys are present (the whole point of P3 — CH4 §4.7 claims the ES backtest; it must run)
    for key in ("comparative_es_backtest", "bayesian_null_report", "model_confidence_set"):
        assert key in out, key

    # comparative ES backtest: with data present it runs and yields tail legs corroborating (or not) H2-Tail
    es = out["comparative_es_backtest"]
    assert es["status"] in {"ok", "skipped", "error"}
    if es["status"] == "ok":
        assert es["legs"], es
        for leg in es["legs"]:
            assert "corroborates_h2_tail" in leg and "pvalue_dm_hln" in leg

    # bayesian null: paired per-seed diffs -> BF01 + ROPE, for both co-primary metrics
    bn = out["bayesian_null_report"]
    assert bn["status"] in {"ok", "skipped"}
    if bn["status"] == "ok":
        for leg in bn.get("ra", []) + bn["tail"]["legs"]:
            assert "bf01" in leg and "verdict" in leg and "hdi_in_rope" in leg

    # model confidence set needs the optional `arch` dep; either it ran (ok) or degraded gracefully.
    mcs = out["model_confidence_set"]
    assert mcs["status"] in {"ok", "skipped", "error"}

    # DISJOINT: none of the three carry family-tuple keys, and the frozen headline is untouched.
    for key in ("comparative_es_backtest", "bayesian_null_report", "model_confidence_set"):
        assert not any(k in out[key] for k in ("arm_a", "arm_b", "metric", "level_tuple"))
    assert "h2" in out


def test_p3_blocks_degrade_gracefully_when_data_absent(tmp_path: Path) -> None:
    """With only tail-fed SEARCH records (no test leg), the three blocks skip/error, never raise."""
    _write_search_arm(tmp_path)  # no test/ leg -> no per-seed test scores, no realized test series
    out = AC.analyze(tmp_path)
    assert out["comparative_es_backtest"]["status"] in {"skipped", "error"}
    assert out["bayesian_null_report"]["status"] in {"skipped", "error"}
    assert out["model_confidence_set"]["status"] in {"skipped", "error"}


def test_p3_renderers_emit_sections(tmp_path: Path) -> None:
    """The three renderers appear in the written report (or degrade to an n/a section)."""
    _write_p3_archive(tmp_path)
    out = AC.analyze(tmp_path)
    md = AC.write_report(out, tmp_path / "report").read_text(encoding="utf-8")
    assert "Comparative ES backtest" in md
    assert "Bayesian evidence-for-the-null" in md
    assert "Model Confidence Set" in md


# --------------------------------------------------------------------------- #
# P6-code — CVaR-Tail equivalence margin as a FRACTION of baseline CVaR (report both)
# --------------------------------------------------------------------------- #
def test_p6_h2_tost_reports_both_raw_and_fractional_tail_margin(tmp_path: Path) -> None:
    """Each H2-Tail leg carries the raw ±0.05 band AND a fraction-of-baseline-CVaR band, both verdicts."""
    _write_p3_archive(tmp_path)
    records = AC.load_campaign_records(tmp_path)
    tost = AC.h2_tost(records, tail_margin_fraction=0.25, rng=np.random.default_rng(0))
    assert tost["status"] == "ok"
    assert tost["tail_margin_fraction"] == 0.25
    tail_legs = tost["tail"]["legs"]
    assert tail_legs, "at least one tail leg with >= 2 shared seeds"
    for leg in tail_legs:
        # raw band verdict is present (existing behaviour, unchanged)
        assert "equivalent" in leg
        # the fractional variant reports BOTH the baseline CVaR and the fractional verdict
        assert "baseline_cvar" in leg and "margin_fraction_abs" in leg
        assert "equivalent_fraction" in leg
        # the fractional margin equals fraction * |baseline CVaR|
        assert abs(leg["margin_fraction_abs"] - 0.25 * abs(leg["baseline_cvar"])) < 1e-12
        # the fractional band is a scale-appropriate SUBSET of the large raw band (baseline CVaR is small),
        # so if the CI is inside the (smaller) fractional band it is also inside the raw band.
        if leg["equivalent_fraction"]:
            assert leg["equivalent"]
    # the RA (Sharpe) legs are unchanged — no fractional keys added there
    for leg in tost["ra"]:
        assert "margin_fraction_abs" not in leg


# --------------------------------------------------------------------------- #
# BH-mechanism — Bonferroni/BH-across-mechanism-legs forking-paths sensitivity
# --------------------------------------------------------------------------- #
def test_mechanism_multiplicity_bonferroni_and_bh_over_p_bearing_legs() -> None:
    """The sensitivity applies Bonferroni (alpha/n_p) + BH over the p-BEARING legs, lists CI-based legs."""
    # A (hypothetical) NAMED-pass aggregator layout: the structural p-values NESTED under their leg keys,
    # plus the flat p_random_pairing_matches the wired named_vs_blinded_structural actually returns.
    nvb = {
        "status": "ok",
        "structural_ast": {"p_value": 0.02},   # AST label-permutation (nested)
        "mcnemar": {"pvalue": 0.30},
        "mahalanobis": {"pvalue": 0.01},
        "p_random_pairing_matches": 0.04,
    }
    m = AC.mechanism_multiplicity(
        responsiveness={"status": "ok", "responsive": True},
        mediation={"status": "ok", "mediated": False},
        named_vs_blinded_structural=nvb,
        legible_format_responsiveness={"status": "no_data"},
        regime_stratified={"status": "ok"},
        alpha=0.05, q=0.05,
    )
    assert m["n_p_tests"] == 4
    assert abs(m["bonferroni_alpha"] - 0.05 / 4) < 1e-12
    by_leg = {r["leg"]: r for r in m["rows"]}
    # p-bearing legs get a Bonferroni + BH decision
    assert by_leg["Coefficient Mahalanobis-perm"]["survives_bonferroni"] is True   # 0.01 <= 0.0125
    assert by_leg["AST label-permutation"]["survives_bonferroni"] is False         # 0.02 > 0.0125
    assert by_leg["Structural McNemar"]["reject_bh"] is False                      # 0.30 fails BH
    # CI-based legs are LISTED with has_p=False and Bonferroni/BH n/a (mirrors H1 in cross-hypothesis)
    assert by_leg["SQ1 responsiveness"]["has_p"] is False
    assert by_leg["SQ1 responsiveness"]["survives_bonferroni"] is None
    assert by_leg["SQ2 mediation (a·b)"]["has_p"] is False


def test_mechanism_multiplicity_degrades_when_no_p_bearing_legs() -> None:
    """The confirmatory default: no NAMED authoring pass -> no p-bearing legs -> n_p_tests==0, never raises."""
    m = AC.mechanism_multiplicity(
        responsiveness={"status": "ok", "responsive": False},
        mediation={"status": "ok", "mediated": False},
        named_vs_blinded_structural={"status": "no_data", "executed": False},
        legible_format_responsiveness={"status": "no_data", "executed": False},
        regime_stratified={"status": "skipped"},
    )
    assert m["n_p_tests"] == 0
    assert all(r["survives_bonferroni"] is None for r in m["rows"])  # nothing corrected
    assert m["rows"], "CI-based legs still listed"


def test_mechanism_multiplicity_wired_into_analyze_disjoint(tmp_path: Path) -> None:
    """analyze() emits out['mechanism_multiplicity'] as a DISJOINT report-only block that never gates."""
    _write_p3_archive(tmp_path)
    out = AC.analyze(tmp_path)
    assert "mechanism_multiplicity" in out
    mm = out["mechanism_multiplicity"]
    assert "rows" in mm and mm["rows"]
    # DISJOINT: no family-tuple keys
    assert not any(k in mm for k in ("arm_a", "arm_b", "metric", "level"))
    # the renderer appears in the report
    md = AC.write_report(out, tmp_path / "report").read_text(encoding="utf-8")
    assert "Mechanism multiplicity" in md
