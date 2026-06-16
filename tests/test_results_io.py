"""Tests for the canonical results IO loader (FINAL_PLAN F.13, audit C-1)."""

from __future__ import annotations


import pytest

from src.io.results import REQUIRED_FIELDS, load_all, load_run, write_run


def _record(run_id: str = "run-0001", arm: str = "scalar", **overrides) -> dict:
    rec = {
        "run_id": run_id,
        "arm": arm,
        "seed": 12345,
        "fold": 0,
        "candidate_id": "cand-42",
        "generation": 3,
        "reward_source_hash": "deadbeef",
        "feedback_block": {"type": arm, "text": "tail stats here"},
        "metrics": {"sharpe": 1.23, "cvar_95": -0.04},
        "wall_clock": 12.5,
        "env_fingerprint": {"python": "3.11.0", "numpy": "2.3.5"},
    }
    rec.update(overrides)
    return rec


def test_write_read_round_trip(results_dir) -> None:
    """write_run then load_run round-trips a record without loss."""
    rec = _record()
    path = write_run(rec, results_dir)
    assert path.is_file()
    loaded = load_run(rec["run_id"], results_dir)
    for k, v in rec.items():
        assert loaded[k] == v


@pytest.mark.parametrize("missing", list(REQUIRED_FIELDS))
def test_loader_fails_on_missing_required_field(results_dir, missing) -> None:
    """write_run raises KeyError naming a missing required field."""
    rec = _record()
    del rec[missing]
    with pytest.raises(KeyError) as exc:
        write_run(rec, results_dir)
    assert missing in str(exc.value)


def test_load_all_returns_all_and_respects_filter(results_dir) -> None:
    """load_all returns every written run and honours a simple filter."""
    write_run(_record(run_id="r1", arm="scalar"), results_dir)
    write_run(_record(run_id="r2", arm="distributional"), results_dir)
    write_run(_record(run_id="r3", arm="scalar"), results_dir)

    everything = load_all(results_dir)
    assert {r["run_id"] for r in everything} == {"r1", "r2", "r3"}

    scalars = load_all(results_dir, filter={"arm": "scalar"})
    assert {r["run_id"] for r in scalars} == {"r1", "r3"}


def test_reward_source_written_and_reloadable(results_dir) -> None:
    """reward.py is written when reward_source is present and reloadable."""
    source = "def reward(weights, returns, prev_weights, port_ret, info):\n    return port_ret, {}, None\n"
    rec = _record(run_id="rw", reward_source=source)
    write_run(rec, results_dir)
    assert (results_dir / "rw" / "reward.py").read_text() == source

    loaded = load_run("rw", results_dir)
    assert loaded["reward_source"] == source
