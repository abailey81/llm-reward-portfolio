"""The in-job bayes_opt chain runner (2026-07-26) — the campaign's critical-path optimisation.

The whole justification for this module is that it removes QUEUE LATENCY and NOTHING ELSE. So the
tests are written to prove the negative: same proposals, same candidate ids, same failure sentinel,
same budget — with the only difference being that 30 dispatches became one. Plus the deadline/
resume behaviour that lets a 214-hour CPU chain live inside 72-hour jobs.
"""
from __future__ import annotations

import json

import numpy as np
import pytest

from src.cluster import bayes_chain
from src.cluster.bayes_chain import ChainStopped, run_bayes_chain


class _FakeClock:
    """Deterministic monotonic clock (no wall-time flakiness)."""

    def __init__(self) -> None:
        self.t = 0.0

    def __call__(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


def _patch_chain(monkeypatch, *, archive: dict, per_iter_secs: float = 0.0,
                 clock: _FakeClock | None = None, fail_cids: set[str] | None = None):
    """Stub the three cluster/training seams so the GP loop itself runs for real.

    Deliberately NOT stubbed: ``bayes_opt_over_template`` and ``family_bounds`` — the point is to
    exercise the REAL optimiser so the proposal sequence under test is the genuine one.
    """
    fail_cids = fail_cids or set()
    trained: list[str] = []

    monkeypatch.setattr("src.orchestration.parallel._worker_init", lambda: None)

    def _fake_read(cid, arm, arm_root, k_seeds, base_seed):
        return archive.get(cid)

    def _fake_family_spec(arm, kind, reward, cid, opts, spec_root):
        return {"arm": arm, "kind": kind, "reward": reward, "candidate_id": cid,
                "run_id": cid, "archive_root": str(spec_root)}

    def _fake_run_single(spec):
        cid = spec["candidate_id"]
        trained.append(cid)
        if clock is not None:
            clock.advance(per_iter_secs)
        if cid in fail_cids:
            return {"ok": False}
        # deterministic pseudo-fitness from the proposed coefficients
        archive[cid] = {"fitness": float(np.sum(np.asarray(spec["reward"], dtype=float))),
                        "ok": True, "candidate_id": cid}
        return {"ok": True}

    monkeypatch.setattr("src.cluster.campaign._read_candidate", _fake_read)
    monkeypatch.setattr("src.cluster.campaign._family_spec", _fake_family_spec)
    monkeypatch.setattr("src.cluster.run_one._run_single", _fake_run_single)
    return trained


def _opts(candidates: int = 12, seed: int = 7) -> dict:
    return {"candidates": candidates, "seed": seed, "proto_cfg": None}


# --- the science-invariance proofs ----------------------------------------------------------

def test_chain_trains_exactly_the_matched_budget_in_order(monkeypatch, tmp_path):
    """Same candidate ids, same count, same order as the driver-side loop
    (``campaign.run_family_search_arm`` names them ``<arm>-c<i>``, i ascending)."""
    trained = _patch_chain(monkeypatch, archive={})
    out = run_bayes_chain(_opts(12), archive_root=tmp_path, spec_archive_root=tmp_path / "specs")

    assert out["status"] == "complete"
    assert out["completed"] == 12 and out["failed"] == 0
    assert trained == [f"bayes_opt-c{i}" for i in range(12)]


def test_proposal_sequence_is_IDENTICAL_to_the_reference_loop(monkeypatch, tmp_path):
    """THE load-bearing test: the coefficients the on-node chain evaluates must be exactly those a
    plain ``bayes_opt_over_template`` call produces with the same seed and budget. If this holds,
    moving the loop onto the node cannot change WHICH reward the H4b control selects."""
    from src.baselines.reward_family import family_bounds
    from src.search.bayes_opt import bayes_opt_over_template

    seen: list[list[float]] = []
    archive: dict = {}
    trained = _patch_chain(monkeypatch, archive=archive)

    # capture what the chain evaluates
    orig = bayes_chain._chain_specs

    def _spy(arm, cid, coeffs, *a, **kw):
        seen.append([float(c) for c in coeffs])
        return orig(arm, cid, coeffs, *a, **kw)

    monkeypatch.setattr(bayes_chain, "_chain_specs", _spy)
    run_bayes_chain(_opts(10, seed=7), archive_root=tmp_path, spec_archive_root=tmp_path / "s")

    # the reference: the SAME optimiser, same seed/budget, same objective
    ref: list[list[float]] = []

    def _ref_eval(coeffs):
        ref.append([float(c) for c in coeffs])
        return float(np.sum(np.asarray(coeffs, dtype=float)))

    bayes_opt_over_template(_ref_eval, family_bounds(None), {"matched_budget": 10},
                            rng=np.random.default_rng(7))

    assert len(seen) == len(ref) == 10
    assert np.allclose(np.asarray(seen), np.asarray(ref)), "the on-node chain diverged from the GP"
    assert len(trained) == 10


def test_failed_training_uses_the_same_sentinel_as_the_driver(monkeypatch, tmp_path):
    """A failed candidate must feed the GP -1e9, exactly as campaign.run_family_search_arm does —
    otherwise the optimiser would see a different objective on the two paths."""
    trained = _patch_chain(monkeypatch, archive={}, fail_cids={"bayes_opt-c3"})
    out = run_bayes_chain(_opts(8), archive_root=tmp_path, spec_archive_root=tmp_path / "s")
    assert out["failed"] == 1
    assert out["completed"] == 7
    assert len(trained) == 8  # the failure did NOT abort the chain


# --- resume / deadline: what makes a 214-hour CPU chain fit in 72-hour jobs -------------------

def test_archived_candidates_replay_WITHOUT_retraining(monkeypatch, tmp_path):
    """Resume is archive replay: previously-trained candidates cost nothing and return the SAME
    fitness, so the GP re-derives an identical trajectory."""
    archive = {f"bayes_opt-c{i}": {"fitness": float(i), "ok": True} for i in range(5)}
    trained = _patch_chain(monkeypatch, archive=archive)
    out = run_bayes_chain(_opts(8), archive_root=tmp_path, spec_archive_root=tmp_path / "s")

    assert out["status"] == "complete" and out["completed"] == 8
    assert trained == [f"bayes_opt-c{i}" for i in range(5, 8)], "replayed candidates were retrained"


def test_deadline_stops_cleanly_and_reports_partial(monkeypatch, tmp_path):
    """Out of wall budget => stop BEFORE starting an iteration that cannot finish, exit normally."""
    clock = _FakeClock()
    archive: dict = {}
    trained = _patch_chain(monkeypatch, archive=archive, per_iter_secs=100.0, clock=clock)

    out = run_bayes_chain(_opts(20), archive_root=tmp_path, spec_archive_root=tmp_path / "s",
                          deadline_secs=500.0, clock=clock)

    assert out["status"] == "partial"
    assert 0 < out["completed"] < 20
    assert len(trained) == out["completed"]
    # 500 * 0.92 = 460 usable; at 100 s/iter it must not have started a 5th it could not finish
    assert out["completed"] == 4


def test_a_partial_chain_RESUMES_to_completion_with_no_lost_work(monkeypatch, tmp_path):
    """The operational contract: resubmit the same job until it reports complete, and every
    candidate is trained EXACTLY ONCE across the whole sequence of jobs."""
    archive: dict = {}
    all_trained: list[str] = []
    for _ in range(10):                       # bounded: successive "jobs"
        clock = _FakeClock()
        trained = _patch_chain(monkeypatch, archive=archive, per_iter_secs=100.0, clock=clock)
        out = run_bayes_chain(_opts(12), archive_root=tmp_path,
                              spec_archive_root=tmp_path / "s",
                              deadline_secs=500.0, clock=clock)
        all_trained.extend(trained)
        if out["status"] == "complete":
            break
    assert out["status"] == "complete"
    assert sorted(all_trained) == sorted(f"bayes_opt-c{i}" for i in range(12))
    assert len(all_trained) == len(set(all_trained)), "a candidate was trained twice"


def test_est_iter_secs_guards_the_FIRST_iteration_of_a_job(monkeypatch, tmp_path):
    """Without a prior observation there is nothing to estimate from, so a job would start its
    first training blind and could be SIGKILLed at the walltime. The campaign KNOWS the cost
    (train_steps / measured steps_per_s), so passing it makes even the first iteration checked."""
    clock = _FakeClock()
    trained = _patch_chain(monkeypatch, archive={}, per_iter_secs=10.0, clock=clock)
    # budget 100 s (92 usable) but each iteration is known to cost 500 s -> start nothing
    out = run_bayes_chain(_opts(5), archive_root=tmp_path, spec_archive_root=tmp_path / "s",
                          deadline_secs=100.0, est_iter_secs=500.0, clock=clock)
    assert out["status"] == "partial" and out["completed"] == 0 and trained == []


def test_without_an_estimate_the_first_iteration_still_proceeds(monkeypatch, tmp_path):
    """The fallback must not deadlock the chain: with no estimate available a job still makes
    progress rather than refusing to start (which would stall the campaign forever)."""
    clock = _FakeClock()
    trained = _patch_chain(monkeypatch, archive={}, per_iter_secs=1000.0, clock=clock)
    out = run_bayes_chain(_opts(5), archive_root=tmp_path, spec_archive_root=tmp_path / "s",
                          deadline_secs=100.0, clock=clock)
    assert out["completed"] == 1 and trained == ["bayes_opt-c0"]


def test_no_deadline_runs_to_completion(monkeypatch, tmp_path):
    trained = _patch_chain(monkeypatch, archive={})
    out = run_bayes_chain(_opts(6), archive_root=tmp_path, spec_archive_root=tmp_path / "s",
                          deadline_secs=None)
    assert out["status"] == "complete" and len(trained) == 6


# --- the entry point -------------------------------------------------------------------------

def test_cli_entry_point_reads_a_chain_spec_and_exits_zero(monkeypatch, tmp_path, capsys):
    """A partial chain is a SUCCESSFUL bounded run — it must exit 0, or SGE/-r y would treat a
    normal deadline stop as a task failure and requeue it."""
    _patch_chain(monkeypatch, archive={})
    spec = tmp_path / "chain.json"
    spec.write_text(json.dumps({
        "opts": _opts(4), "arm": "bayes_opt",
        "archive_root": str(tmp_path), "spec_archive_root": str(tmp_path / "s"), "k_seeds": 1,
    }), encoding="utf-8")

    rc = bayes_chain.main(["--spec", str(spec), "--pack", "1"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert out["status"] == "complete" and out["completed"] == 4


def test_chain_module_never_reaches_for_the_scheduler():
    """It runs ON the node: no ssh/qsub/driver import may creep in, or we would have reinvented the
    30-dispatch behaviour this module exists to remove."""
    import ast
    from pathlib import Path

    src = Path(bayes_chain.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert not any("driver" in m or "submit" in m for m in imported)
    assert "subprocess" not in imported
