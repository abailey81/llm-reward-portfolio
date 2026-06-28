"""Unit test for the manual pool-recycling primitive (``src.orchestration.parallel.run_recycling``).

In-pool worker recycling (``ProcessPoolExecutor(max_tasks_per_child=...)``) DEADLOCKS on Windows +
spawn across CPython 3.11-3.14 (measured 2026-06-24, all four versions). The campaign therefore reclaims
each worker's fragmented replay-buffer heap by tearing the ``DevicePool`` down and recreating it every
``recycle_every`` tasks. This test locks in the contract: every spec is processed, order is preserved,
device tokens are assigned, and fresh pools spawn fresh workers (the reclaim mechanism).

Uses ``initializer=None`` so the spawned workers are bare (no torch / no pyarrow) -> the test is fast and
has no heavy-dependency requirement.
"""
from __future__ import annotations

import os

from src.orchestration.parallel import run_recycling


def _ping(spec: dict) -> dict:
    """Bare worker (no torch): echo the pid + index + the assigned device token."""
    return {"pid": os.getpid(), "i": spec["i"], "device": spec.get("device")}


def _raises_on_odd(spec: dict) -> dict:
    """Worker that RAISES on odd indices (vs returning an error dict) — exercises 1A-4."""
    if spec["i"] % 2 == 1:
        raise RuntimeError(f"boom on {spec['i']}")
    return {"ok": True, "i": spec["i"]}


def test_run_recycling_processes_all_in_order_and_recycles_workers() -> None:
    specs = [{"i": i} for i in range(10)]
    res = run_recycling(specs, worker=_ping, n_gpu=0, n_cpu=2, recycle_every=4, initializer=None)

    # every spec processed, in submission order
    assert [r["i"] for r in res] == list(range(10))
    # device tokens assigned from the cpu pool (n_gpu=0)
    assert all(r["device"] == "cpu" for r in res)
    # 10 tasks / recycle_every=4 -> 3 fresh pools -> strictly more than n_cpu (2) distinct worker pids,
    # i.e. the pool was actually torn down + respawned between batches (the RAM-reclaim mechanism).
    assert len(set(r["pid"] for r in res)) > 2


def test_run_recycling_single_batch_when_recycle_every_exceeds_count() -> None:
    """recycle_every >= len(specs) -> one pool, still correct (no spurious teardown)."""
    specs = [{"i": i} for i in range(3)]
    res = run_recycling(specs, worker=_ping, n_gpu=0, n_cpu=2, recycle_every=16, initializer=None)
    assert [r["i"] for r in res] == [0, 1, 2]


def test_run_recycling_captures_raising_worker_without_aborting() -> None:
    """1A-4: a worker that RAISES must not abort the run — every spec is still attempted, in order."""
    specs = [{"i": i} for i in range(6)]
    res = run_recycling(specs, worker=_raises_on_odd, n_gpu=0, n_cpu=2, recycle_every=4, initializer=None)
    assert len(res) == 6  # all 6 attempted despite the 3 odd ones raising
    # order preserved: even indices returned ok with their i; odd indices captured as error dicts
    assert res[0].get("i") == 0 and res[2].get("i") == 2 and res[4].get("i") == 4
    assert all(not res[j].get("ok") and "boom" in res[j]["error"] for j in (1, 3, 5))


def test_run_recycling_empty_specs_returns_empty() -> None:
    """Edge case: no specs -> no pool spawned, returns []."""
    assert run_recycling([], worker=_ping, n_gpu=0, n_cpu=2, recycle_every=4, initializer=None) == []
