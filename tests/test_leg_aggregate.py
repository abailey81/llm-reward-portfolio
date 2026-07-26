"""Tests for the multi-root leg aggregation (R80/R82) — schema-true via the real writer."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.inference.leg_aggregate import (  # noqa: E402
    empirical_cvar,
    leg_results_for_synthesis,
    per_seed_series,
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
        write_run(_record("distributional", seed, dist), root)
        write_run(_record("scalar", seed, base), root)
    out = leg_results_for_synthesis({"leg": root}, seeds, floor_sharpe=-10.0)
    assert np.all(out["leg"]["cvar_diff_per_seed"] > 0)
