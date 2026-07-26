"""Tests for the multi-root leg aggregation (R80/R82) — schema-true via the real writer."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.inference.leg_aggregate import (  # noqa: E402
    T0_FLOOR_ARM,
    T0_FLOOR_SEEDS,
    empirical_cvar,
    leg_results_for_synthesis,
    per_seed_series,
    t0_floor_sharpe,
)
from src.io.results import write_run  # noqa: E402


def _record(arm: str, seed: int, returns: np.ndarray) -> dict:
    return {
        "run_id": f"{arm}-s{seed}",
        "arm": arm,
        "seed": seed,
        "fold": 0,
        "candidate_id": f"{arm}-winner",
        "generation": 0,
        "reward_source_hash": "h" * 64,
        "feedback_block": "",
        "metrics": {"test_returns": [float(x) for x in returns]},
        "wall_clock": 1.0,
        "env_fingerprint": "test-env",
    }


def _write_leg(root: Path, seeds: list[int], rng, a_shift=0.0, b_shift=0.0) -> None:
    """Build a leg TEST sub-root in the REAL archive shape: ``root/<arm>/<arm>-s<seed>/``.

    Row 34 (2026-07-26): this used to write FLAT (``root/<arm>-s<seed>``), matching what
    ``per_seed_series`` then assumed rather than what the campaign actually produces — the
    campaign hands ``write_run`` an ARM-level root (``src/cluster/run_one.py:108``). The fixture
    and the code agreed with each other and BOTH disagreed with reality, so a green suite proved
    nothing about the only layout that will ever exist. Mirroring the producer is what makes these
    tests load-bearing.
    """
    for seed in seeds:
        base = rng.standard_normal(200) * 0.01
        write_run(_record("distributional", seed, base + a_shift), root / "distributional")
        write_run(_record("scalar", seed, base + b_shift), root / "scalar")


def test_the_T0_floor_matches_what_amendment_R84_REGISTERED():
    """The floor was treated as an open science decision; it is registered, in BOTH places.

    This is the guard that keeps the implementation tied to the design of record rather than to a
    docstring: if either the registered arm or the registered seed set is ever edited, this fails.
    """
    import yaml

    cfg = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / "config" / "preregistration.yaml")
        .read_text(encoding="utf-8"))
    registered = cfg["model_suite"]["synthesis_exactness"]["t0_floor_definition"].lower()
    assert "equal-weight" in registered and "mean per-seed sharpe" in registered
    assert "0-29" in registered
    assert T0_FLOOR_ARM == "equal_weight"
    assert T0_FLOOR_SEEDS == list(range(30))       # the "common floor seeds 0-29"


def test_t0_floor_is_the_equal_weight_MEAN_per_seed_sharpe(tmp_path: Path):
    rng = np.random.default_rng(11)
    seeds = [0, 1, 2, 3]
    for seed in seeds:
        write_run(_record("equal_weight", seed, rng.standard_normal(300) * 0.01),
                  tmp_path / "equal_weight")
    expected = per_seed_series(tmp_path, "equal_weight", seeds)["sharpe"].mean()
    assert t0_floor_sharpe(tmp_path, seeds) == pytest.approx(float(expected))


def test_the_floor_is_ANNUALISED_so_it_is_comparable_to_the_leg_sharpes(tmp_path: Path):
    """The row-34 trap: a per-period floor would be ~sqrt(252) smaller and pass every leg.

    The floor and the leg statistic must be the SAME estimator, so this pins the floor to the
    annualised ddof=0 bootstrap.sharpe_ratio rather than a hand-rolled mean/std.
    """
    from src.inference.bootstrap import sharpe_ratio

    rng = np.random.default_rng(5)
    rets = {s: rng.standard_normal(300) * 0.01 + 0.0004 for s in range(3)}
    for seed, r in rets.items():
        write_run(_record("equal_weight", seed, r), tmp_path / "equal_weight")
    floor = t0_floor_sharpe(tmp_path, list(rets))
    annualised = float(np.mean([sharpe_ratio(r) for r in rets.values()]))
    per_period = float(np.mean([r.mean() / r.std(ddof=1) for r in rets.values()]))
    assert floor == pytest.approx(annualised)
    assert abs(floor) > 5 * abs(per_period)        # unmistakably NOT the per-period statistic


def test_a_partial_seed_set_FAILS_LOUD_rather_than_lowering_the_floor(tmp_path: Path):
    """A floor averaged over whatever happens to be on disk is a different number from the
    registered one — and it would silently change which legs vote in the pooled bound."""
    write_run(_record("equal_weight", 0, np.random.default_rng(1).standard_normal(200) * 0.01),
              tmp_path / "equal_weight")
    with pytest.raises(FileNotFoundError):
        t0_floor_sharpe(tmp_path, [0, 1, 2])


def test_empirical_cvar_worst_alpha_mean():
    r = np.array([0.05, -0.10, 0.01, -0.02, 0.03] * 20)   # T=100 -> worst 5 values
    assert empirical_cvar(r, alpha=0.05) == pytest.approx(-0.10)  # the five -0.10s


def test_per_seed_series_shapes_and_loud_missing(tmp_path: Path):
    rng = np.random.default_rng(0)
    seeds = [0, 1, 2]
    _write_leg(tmp_path, seeds, rng)
    s = per_seed_series(tmp_path, "distributional", seeds)
    assert s["cvar"].shape == s["sharpe"].shape == (3,)
    with pytest.raises(FileNotFoundError):
        per_seed_series(tmp_path, "distributional", [0, 1, 2, 99])  # missing seed is LOUD


def test_flat_layout_is_refused_loudly(tmp_path: Path):
    """LAYOUT LOCK (row 34, 2026-07-26). The archive is ``root/<arm>/<arm>-s<seed>``, never flat.

    Reverting to the flat assumption is not a cosmetic regression: because
    ``leg_results_for_synthesis`` shares ONE root across both contrasted arms, a flat reader fails
    on every leg, every failure is caught as a leg failure, and the R86 pooled bound is then
    computed over ZERO legs while reporting "all legs failed the T0 floor". This test writes the
    flat shape and demands a LOUD failure, so that silent-empty outcome cannot come back.
    """
    write_run(_record("distributional", 0, np.zeros(200) + 0.001), tmp_path)  # FLAT — the old shape
    with pytest.raises(FileNotFoundError):
        per_seed_series(tmp_path, "distributional", [0])


def test_sharpe_is_the_canonical_annualised_estimator(tmp_path: Path):
    """UNIT LOCK (row 34, 2026-07-26): the per-seed Sharpe IS ``bootstrap.sharpe_ratio``.

    It used to be a per-period, ddof=1 ratio while ``floor_sharpe`` — and every other Sharpe in the
    stack — is annualised, ddof=0: a ~sqrt(252) = 15.87x mismatch that would have failed the T0
    floor for EVERY leg. One definition, asserted here against the canonical implementation so the
    two can never drift apart again.
    """
    from src.inference.bootstrap import sharpe_ratio

    rng = np.random.default_rng(7)
    rets = rng.standard_normal(200) * 0.01 + 0.0004
    write_run(_record("distributional", 0, rets), tmp_path / "distributional")
    got = per_seed_series(tmp_path, "distributional", [0])["sharpe"][0]
    assert got == pytest.approx(sharpe_ratio(rets))
    # and it is emphatically NOT the old per-period ddof=1 number
    assert got != pytest.approx(float(rets.mean()) / float(rets.std(ddof=1)))


def test_synthesis_input_contract_and_floor(tmp_path: Path):
    rng = np.random.default_rng(1)
    seeds = list(range(5))
    good = tmp_path / "leg_good"
    _write_leg(good, seeds, rng, a_shift=0.002, b_shift=0.002)    # both arms clearly profitable
    weak = tmp_path / "leg_weak"
    _write_leg(weak, seeds, rng, a_shift=-0.01, b_shift=-0.01)    # both arms fail any floor
    out = leg_results_for_synthesis(
        {"good": good, "weak": weak}, seeds, floor_sharpe=0.0)
    assert out["good"]["t0_floor_pass"] is True
    assert out["good"]["cvar_diff_per_seed"].shape == (5,)
    assert out["weak"]["t0_floor_pass"] is False                  # reported, never a vote


def test_broken_leg_is_a_finding_not_a_crash(tmp_path: Path):
    out = leg_results_for_synthesis({"ghost": tmp_path / "absent"}, [0], floor_sharpe=0.0)
    assert out["ghost"]["t0_floor_pass"] is False
    assert "failure" in out["ghost"]


def test_diff_sign_convention_dist_safer_positive(tmp_path: Path):
    """dist − scalar CVaR: a MILDER dist tail (less negative CVaR) => positive diff."""
    rng = np.random.default_rng(2)
    seeds = [0, 1]
    root = tmp_path / "leg"
    for seed in seeds:
        base = rng.standard_normal(200) * 0.01
        dist = np.where(base < -0.015, -0.015, base)   # dist: tail clipped => safer
        write_run(_record("distributional", seed, dist), root / "distributional")
        write_run(_record("scalar", seed, base), root / "scalar")
    out = leg_results_for_synthesis({"leg": root}, seeds, floor_sharpe=-10.0)
    diff = out["leg"]["cvar_diff_per_seed"]
    # NON-VACUITY FIRST (row 34, 2026-07-26). This test wrote the FLAT layout, so after the
    # layout fix every record was missing, the leg was caught as a failure, and `diff` came back
    # EMPTY — whereupon `np.all(empty > 0)` is True and the test passed while asserting NOTHING.
    # That is the vacuous-truth-on-empty class, and a sign-convention test that cannot fail is
    # worse than no test: it certifies the convention it never checked. Assert the array is the
    # expected size, and that the leg actually loaded, BEFORE reading the sign.
    assert "failure" not in out["leg"], out["leg"].get("failure")
    assert diff.shape == (len(seeds),)
    assert np.all(diff > 0)
