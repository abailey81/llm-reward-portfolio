"""Unit tests for the shared TEST-leg record builder (``src.orchestration.test_leg.build_test_record``).

Pure (no torch): locks the per-seed record schema that BOTH the serial ``evaluate_winner_on_test`` and
the parallel winner-re-run worker emit, so the two paths cannot drift.
"""
from __future__ import annotations

import numpy as np
import pytest

from src.io.results import OPTIONAL_FIELDS, REQUIRED_FIELDS
from src.orchestration.test_leg import build_test_record, evaluate_winners_on_test_parallel


def test_build_test_record_schema_and_metrics() -> None:
    winner = {
        "candidate_id": "distributional-g0-c0",
        "generation": 0,
        "reward_source": "def reward(w, r, p, pr, i): return pr, {}, None\n",
        "feedback_block": "blk",
        "metrics": {"val_fitness": 0.42},
    }
    tr = np.array([0.01, -0.02, 0.03, 0.0, -0.01])
    rec = build_test_record(
        winner=winner, arm="distributional", seed=7, reward_hash="h" * 64,
        env_fp="campaign:distributional:test[420,600)", test_returns=tr,
    )
    # deterministic, resume-keyed run_id + identity fields
    assert rec["run_id"] == "distributional-s7"
    assert rec["seed"] == 7 and rec["arm"] == "distributional" and rec["fold"] == 0
    assert rec["candidate_id"] == "distributional-g0-c0"
    assert rec["reward_source_hash"] == "h" * 64 and rec["frozen"] is True
    # metrics carry val_fitness + raw test stats + the per-step vector (in metrics AND top-level)
    m = rec["metrics"]
    assert m["val_fitness"] == 0.42 and "test_sharpe" in m and "test_cvar05" in m
    assert m["test_returns"] == [0.01, -0.02, 0.03, 0.0, -0.01]
    assert rec["test_returns"] == m["test_returns"] and rec["per_period_pnl"] == m["per_period_pnl"]
    assert "test_gross" not in m  # absent when no decomposition supplied
    # the schema this record is written under: required fields present, extras are documented optionals
    assert all(f in rec for f in REQUIRED_FIELDS)
    assert {"frozen", "test_returns", "per_period_pnl"}.issubset(set(OPTIONAL_FIELDS))


def test_build_test_record_includes_gross_turnover_and_default_candidate_id() -> None:
    winner = {"metrics": {"val_fitness": 0.1}}  # no candidate_id -> default "{arm}-winner"
    tr = np.array([0.01, -0.01])
    rec = build_test_record(
        winner=winner, arm="scalar", seed=0, reward_hash="", env_fp="fp",
        test_returns=tr, test_gross=np.array([0.012, -0.008]), test_turnover=np.array([0.5, 0.3]),
    )
    m = rec["metrics"]
    assert m["test_gross"] == [0.012, -0.008] and m["test_turnover"] == [0.5, 0.3]
    assert rec["candidate_id"] == "scalar-winner"


# --------------------------------------------------------------------------- #
# Parallel driver orchestration (no torch / no spawn: injected runner + worker) #
# --------------------------------------------------------------------------- #
def _fake_record_worker(spec: dict) -> dict:
    """No-torch worker: returns an ok result with a build_test_record-shaped record (canned returns)."""
    rec = build_test_record(
        winner=spec["winner"], arm=spec["arm"], seed=spec["seed"],
        reward_hash=spec["reward_hash"], env_fp=spec["env_fp"], test_returns=[0.01, -0.01, 0.02],
    )
    return {"ok": True, "run_id": spec["run_id"], "arm": spec["arm"], "record": rec}


def _inproc_runner(specs, *, worker, n_gpu, n_cpu, recycle_every):  # noqa: ANN001, ARG001
    """In-process runner (no spawn): map the worker over specs in order, like run_recycling does."""
    return [worker(s) for s in specs]


_COMMON = dict(
    panel_descriptor={"synthetic": True}, env_cfg={}, agent_cfg={},
    train_window=(0, 1), val_window=(1, 2), test_window=(2, 5), embargo=21, lookback=60,
    n_gpu=0, n_cpu=2, recycle_every=4, runner=_inproc_runner, worker=_fake_record_worker,
)


def test_parallel_driver_builds_specs_writes_per_arm_and_summarizes(tmp_path) -> None:
    winners = [
        ("distributional", {"reward_source": "s1", "reward_source_hash": "", "metrics": {"val_fitness": 0.4}}),
        ("scalar", {"reward_source": "s2", "reward_source_hash": "", "metrics": {"val_fitness": 0.5}}),
    ]
    writes: list = []
    summary = evaluate_winners_on_test_parallel(
        winners=winners, seeds=[0, 1, 2], test_root=tmp_path,
        write=lambda r, root: writes.append((r["run_id"], root)), **_COMMON,
    )
    assert summary["n_specs"] == 6 and summary["n_written"] == 6 and summary["n_failed"] == 0
    assert summary["matched_budget_ok"] is True
    # records written under test_root/<arm>/, one per (arm, seed)
    assert ("distributional-s0", str(tmp_path / "distributional")) in writes
    assert ("scalar-s2", str(tmp_path / "scalar")) in writes


def test_parallel_driver_resume_skips_done(tmp_path) -> None:
    winners = [("scalar", {"reward_source": "s", "reward_source_hash": "", "metrics": {"val_fitness": 0.1}})]
    summary = evaluate_winners_on_test_parallel(
        winners=winners, seeds=[0, 1, 2], test_root=tmp_path, done_ids={"scalar-s0", "scalar-s1"},
        write=lambda r, root: None, **_COMMON,
    )
    assert summary["n_specs"] == 1  # only seed 2 remains


def test_parallel_driver_desync_guard_fires(tmp_path) -> None:
    winners = [("scalar", {"reward_source": "s", "reward_source_hash": "a" * 64, "metrics": {"val_fitness": 0.1}})]
    with pytest.raises(ValueError, match="desync"):
        evaluate_winners_on_test_parallel(
            winners=winners, seeds=[0], test_root=tmp_path, write=lambda r, root: None, **_COMMON,
        )


def test_parallel_driver_counts_worker_failures(tmp_path) -> None:
    winners = [("scalar", {"reward_source": "s", "reward_source_hash": "", "metrics": {"val_fitness": 0.1}})]

    def _failing(spec: dict) -> dict:
        return {"ok": False, "run_id": spec["run_id"], "arm": spec["arm"], "error": "boom"}

    common = {**_COMMON, "worker": _failing}
    summary = evaluate_winners_on_test_parallel(
        winners=winners, seeds=[0, 1], test_root=tmp_path, write=lambda r, root: None, **common,
    )
    assert summary["n_written"] == 0 and summary["n_failed"] == 2
    assert summary["matched_budget_ok"] is False  # full budget but zero successes
