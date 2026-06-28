"""Tests for the training-budget learning curve (scripts/learning_curve.py, the under-training gate).

Two layers:
  - FAST (default): the pure helpers (subsample, the per-budget seed-IQM summary aggregation, the markdown
    table, the plot) with ``run_one_budget`` STUBBED — no torch, no training. These pin the reporting
    contract the operator reads to pick the budget.
  - SLOW (``-m slow``): a real end-to-end run of the smoke ladder (tiny budgets, synthetic, cpu) proving the
    harness trains the FIXED agent and emits json + md (+ png) — the build+smoke acceptance.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import learning_curve as lc  # noqa: E402


# --------------------------------------------------------------------------- #
# FAST — pure helpers / reporting (no torch)                                   #
# --------------------------------------------------------------------------- #
def test_subsample_caps_points_and_preserves_endpoints() -> None:
    steps = list(range(1000))
    losses = [float(s) for s in steps]
    sub = lc._subsample(steps, losses, k=60)
    assert len(sub) <= 60
    assert sub[0][0] == 0.0 and sub[-1][0] == 999.0  # endpoints preserved
    # empty trajectory -> empty payload (a budget below learning_starts records no loss)
    assert lc._subsample([], []) == []


def _fake_run(budget: int, seed: int, *, eval_iqm: float, critic_max: float, finite: bool = True) -> dict:
    return {
        "budget": budget,
        "seed": seed,
        "ok": True,
        "eval_iqm": eval_iqm,
        "eval_mean": eval_iqm,
        "eval_n": 100,
        "critic_loss_terminal": critic_max * 0.5,
        "critic_loss_max": critic_max,
        "critic_loss_finite": finite,
        "critic_trajectory": [[0.0, critic_max], [budget, critic_max * 0.5]],
        "seconds": 1.0,
    }


def test_run_curve_summary_aggregates_seed_iqm(monkeypatch) -> None:
    """run_curve builds a per-budget seed-median eval IQM + max critic loss from the per-seed runs."""
    table = {
        (25000, 0): _fake_run(25000, 0, eval_iqm=0.10, critic_max=5.0),
        (25000, 1): _fake_run(25000, 1, eval_iqm=0.20, critic_max=7.0),
        (50000, 0): _fake_run(50000, 0, eval_iqm=0.30, critic_max=6.0),
        (50000, 1): _fake_run(50000, 1, eval_iqm=0.32, critic_max=6.5),
    }

    def _stub(budget, seed, reward_key, **kw):  # noqa: ANN001, ANN003
        return table[(budget, seed)]

    monkeypatch.setattr(lc, "run_one_budget", _stub)
    result = lc.run_curve([25000, 50000], [0, 1], "differential_sharpe", synthetic=True, end="x", device="cpu")

    by_budget = {r["budget"]: r for r in result["summary"]}
    assert by_budget[25000]["n_ok"] == 2
    assert by_budget[25000]["eval_iqm_over_seeds"] == pytest.approx(0.15)   # median(0.10, 0.20)
    assert by_budget[50000]["eval_iqm_over_seeds"] == pytest.approx(0.31)   # median(0.30, 0.32)
    assert by_budget[25000]["critic_loss_max"] == pytest.approx(7.0)        # max over seeds
    assert by_budget[50000]["critic_finite_all"] is True


def test_write_markdown_and_plot(tmp_path, monkeypatch) -> None:
    """The md table has one row per budget; the png is written when matplotlib is present."""
    table = {
        (25000, 0): _fake_run(25000, 0, eval_iqm=0.10, critic_max=5.0),
        (50000, 0): _fake_run(50000, 0, eval_iqm=0.30, critic_max=6.0),
    }
    monkeypatch.setattr(lc, "run_one_budget", lambda b, s, r, **kw: table[(b, s)])
    result = lc.run_curve([25000, 50000], [0], "differential_sharpe", synthetic=True, end="x", device="cpu")

    md = tmp_path / "learning_curve.md"
    lc._write_markdown(result, md)
    text = md.read_text(encoding="utf-8")
    assert "| 25000 |" in text and "| 50000 |" in text
    assert text.count("\n|") >= 4  # header + separator + 2 data rows

    png = tmp_path / "learning_curve.png"
    if lc._write_plot(result, png):  # matplotlib may be absent in a minimal env
        assert png.exists() and png.stat().st_size > 0


def test_unknown_reward_is_reported_not_raised() -> None:
    """A bad reward key surfaces as ok=False on the run (the ladder never aborts)."""
    out = lc.run_one_budget(200, 0, "not_a_reward", synthetic=True, end="x", device="cpu")
    assert out["ok"] is False and "not_a_reward" in str(out["error"])


def test_build_parser_defaults() -> None:
    args = lc.build_parser().parse_args([])
    # Brackets the 50k campaign budget and reaches 16x above (wide enough to expose a plateau even if the
    # agent is ~10-40x under-trained; the detector says to extend further if it hasn't plateaued).
    assert args.budgets == "50000,100000,200000,400000,800000"
    assert args.reward == "differential_sharpe"


# --------------------------------------------------------------------------- #
# Convergence-knee detector (recommend_budget) — objective, pre-registerable   #
# --------------------------------------------------------------------------- #
def _summ(pairs: list[tuple[int, float]], *, finite: bool = True, n_ok: int = 2) -> list[dict]:
    return [
        {"budget": b, "eval_iqm_over_seeds": e, "eval_spread": 0.0,
         "critic_loss_max": 5.0, "critic_finite_all": finite, "n_ok": n_ok}
        for b, e in pairs
    ]


def test_recommend_budget_picks_plateau_knee() -> None:
    """A curve that rises then flattens -> CONVERGED at the smallest flat budget."""
    s = _summ([(50_000, 0.10), (100_000, 0.30), (200_000, 0.50), (400_000, 0.505), (800_000, 0.50)])
    rec = lc.recommend_budget(s, plateau_rel_tol=0.05)
    assert rec["converged"] is True
    assert rec["recommended_budget"] == 200_000  # first budget past which eval is flat to the ceiling
    assert rec["plateau_eval"] == pytest.approx(0.50, abs=0.02)


def test_recommend_budget_flags_still_rising_at_ceiling() -> None:
    """A monotonically-rising curve -> NOT converged; tell the operator to extend the ladder."""
    s = _summ([(50_000, 0.10), (100_000, 0.25), (200_000, 0.45), (400_000, 0.70), (800_000, 0.95)])
    rec = lc.recommend_budget(s, plateau_rel_tol=0.05)
    assert rec["converged"] is False
    assert "RISING" in rec["reason"].upper() or "EXTEND" in rec["reason"].upper()
    assert rec["recommended_budget"] == 800_000  # the ceiling, but flagged under-trained


def test_recommend_budget_insufficient_budgets() -> None:
    rec = lc.recommend_budget(_summ([(50_000, 0.1), (100_000, 0.3)]), min_budgets=3)
    assert rec["converged"] is None and rec["recommended_budget"] is None


def test_recommend_budget_nonfinite_critic_at_ceiling_not_converged() -> None:
    """Flat eval but a non-finite critic near the ceiling -> not safe to fix the budget there."""
    s = _summ([(50_000, 0.49), (100_000, 0.50), (200_000, 0.50)], finite=False)
    rec = lc.recommend_budget(s, plateau_rel_tol=0.05)
    assert rec["converged"] is False


def test_recommend_budget_wired_into_run_curve(monkeypatch) -> None:
    table = {
        (50000, 0): _fake_run(50000, 0, eval_iqm=0.10, critic_max=5.0),
        (100000, 0): _fake_run(100000, 0, eval_iqm=0.50, critic_max=5.0),
        (200000, 0): _fake_run(200000, 0, eval_iqm=0.51, critic_max=5.0),
    }
    monkeypatch.setattr(lc, "run_one_budget", lambda b, s, r, **kw: table[(b, s)])
    result = lc.run_curve([50000, 100000, 200000], [0], "differential_sharpe", synthetic=True, end="x", device="cpu")
    assert "convergence" in result and result["convergence"]["converged"] in (True, False)


# --------------------------------------------------------------------------- #
# SLOW — real end-to-end smoke ladder                                          #
# --------------------------------------------------------------------------- #
@pytest.mark.slow
def test_smoke_ladder_trains_and_writes_outputs(tmp_path) -> None:
    """The smoke ladder trains the FIXED agent at tiny budgets and emits a finite-critic curve + files."""
    budgets, seeds = [1100, 1300], [0]
    result = lc.run_curve(budgets, seeds, "differential_sharpe", synthetic=True, end="2014-12-31", device="cpu")

    assert len(result["runs"]) == 2
    assert all(r["ok"] for r in result["runs"]), [r.get("error") for r in result["runs"]]
    # The representative (well-conditioned) reward must NOT explode the critic — bounded + finite.
    for r in result["runs"]:
        assert r["critic_loss_finite"] is True
        assert r["critic_loss_max"] is not None and r["critic_loss_max"] < 1.0e4

    lc._write_markdown(result, tmp_path / "learning_curve.md")
    (tmp_path / "learning_curve.json").write_text(json.dumps(result), encoding="utf-8")
    assert (tmp_path / "learning_curve.md").exists()
    # eval IQM is finite (a real held-out number)
    assert np.isfinite(result["summary"][0]["eval_iqm_over_seeds"])
