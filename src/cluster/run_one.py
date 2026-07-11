"""On-node entrypoint: run ONE task file (a single spec, or a §15 GPU pack of N specs).

Routes every spec through the EXISTING certified machinery — ``parallel.train_candidate`` for
search/test trainings and ``parallel._archive`` for the atomic record commit — so a cluster run
produces byte-compatible archives with the local pipeline (the resume/replay guarantees carry
over untouched). Pack mode exploits the researched cgroup fact (§15): a ``-l gpu=1`` job owns
its GPU exclusively, so N concurrent trainings inside the job are safe — the exact pattern the
laptop DevicePool certified (3-way == serial, byte-identical).

Exit code: 0 iff EVERY spec in the task succeeded (a pack with any failure exits 1 so SGE/qacct
and the epilogue ledger flag it; the driver's compacted-resume re-emits only the missing
run_ids — completed pack-mates are skipped by run_id idempotency).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

__all__ = ["run_task", "main"]


def _worker_for(spec: dict[str, Any]) -> Any:
    """The certified worker for this spec's LEG: search ``train_candidate`` vs sealed-leg
    ``_test_seed_worker``. The cluster reuses the EXACT laptop workers — a cluster record is
    byte-compatible with the local one, so downstream inference reads them identically."""
    if spec.get("leg") == "test":
        from src.orchestration.test_leg import _test_seed_worker

        return _test_seed_worker
    from src.orchestration.parallel import train_candidate

    return train_candidate


def _archive_result(result: dict[str, Any], spec: dict[str, Any]) -> None:
    """Archive an OK result via the LEG-appropriate path — the SAME atomic ``write_run`` the local
    paths use (search: ``parallel._archive``; test: ``test_leg`` record → ``write_run`` under the
    winner's arm dir). Both workers return their record WITHOUT archiving, so this is the single,
    first archival — no double-write; the poll layer's completion truth reads exactly these dirs."""
    if not result.get("ok"):
        return
    if spec.get("leg") == "test":
        rec = result.get("record")
        if rec is not None:
            from src.io.results import write_run
            from src.orchestration.parallel import _run_env_fp

            arm_root = str(Path(spec["archive_root"]) / str(rec["arm"]))
            # Node-side env fingerprint (the GPU that ACTUALLY trained this seed), overriding the
            # driver-computed spec["env_fp"] the worker carried — parity with the search leg
            # (``_archive`` -> ``_run_env_fp``) and CORRECT for the S6 sealed-leg homogeneity audit,
            # which must attribute each test seed to the node it ran on, not the laptop that authored
            # the spec. Best-effort (falls back to the driver label if capture fails), writes the
            # replayable <run_dir>/env.json exactly like the search records.
            node_fp = _run_env_fp(
                arm_root, str(rec["run_id"]),
                {"seed": rec.get("seed"), "env_fp": rec.get("env_fingerprint")},
            )
            write_run({**rec, "env_fingerprint": node_fp}, arm_root)
    else:
        from src.orchestration.parallel import _archive

        # Provenance parity (CLAUDE.md directive 6): the record must carry the EXACT authored prompt,
        # but authoring is laptop-side so the job's result lacks it — the orchestrator threads it onto
        # the spec, and we copy it onto the result so ``_archive`` persists it exactly as the local
        # ``_drive_llm_arm`` does (which sets ``r["prompt"]`` before archiving).
        if spec.get("prompt") and not result.get("prompt"):
            result = {**result, "prompt": spec["prompt"]}
        _archive(result, spec["arm"], spec, spec["archive_root"], int(spec.get("generation", 0)))


def _run_single(spec: dict[str, Any]) -> dict[str, Any]:
    """One training through the certified LEG worker; archives on success; returns the result row."""
    spec = dict(spec)
    spec.setdefault("device", "cuda")  # the job's cgroup-exclusive GPU
    result = _worker_for(spec)(spec)
    _archive_result(result, spec)
    return result


def run_task(payload: Any, pack: int = 1) -> list[dict[str, Any]]:
    """Execute a task payload (dict = one spec; list = a pack). Returns all result rows.

    ``pack`` > 1 with a list payload runs the specs CONCURRENTLY on this job's exclusive GPU via
    the certified DevicePool (n_gpu=pack tokens on the same physical card). A dict payload or
    pack=1 runs inline (no spawn overhead).
    """
    specs = payload if isinstance(payload, list) else [payload]
    if len(specs) <= 1 or pack <= 1:
        return [_run_single(s) for s in specs]

    from concurrent.futures import as_completed

    from src.orchestration.parallel import DevicePool

    if len(specs) > pack:
        # More specs than concurrent slots means MULTIPLE WAVES inside one job — legal (the pool
        # queues), but the jobscript's h_rt must have been sized for it (render_jobscript sizes
        # for ONE wave by default). Surface it loudly rather than time out silently at 1h30.
        print(
            f"[run_one] WARNING: {len(specs)} specs > pack={pack} -> "
            f"{-(-len(specs) // pack)} waves; ensure h_rt was sized accordingly",
            flush=True,
        )
    rows: list[dict[str, Any]] = []
    # submit_with routes each spec to its LEG worker (the pool injects the device token); a pack is
    # homogeneous in practice (one array = one leg), but per-spec routing keeps mixed packs correct.
    with DevicePool(n_gpu=min(pack, len(specs)), n_cpu=0) as pool:
        futs = {pool.submit_with(_worker_for(s), dict(s)): s for s in specs}
        for fut in as_completed(futs):
            s = futs[fut]
            try:
                row = fut.result()  # the worker captures its own failures -> a result dict
            except Exception as exc:  # noqa: BLE001 — V5 audit fix: a pool-level crash (worker
                # killed by the OS, unpicklable result) must not lose the SIBLING pack-mates'
                # results or leave this spec unattributed for the compacted resume.
                row = {
                    "ok": False,
                    "error": f"{type(exc).__name__}: {exc}",
                    "candidate_id": s.get("candidate_id"),
                    "run_id": s.get("run_id"),
                }
            rows.append(row)
            _archive_result(row, s)
    return rows


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Run one Myriad task file (spec or pack).")
    p.add_argument("--spec", required=True, help="Path to task_<i>.json (sha-verified).")
    p.add_argument("--pack", type=int, default=1, help="Concurrent trainings on this GPU (§15).")
    args = p.parse_args(argv)

    from src.cluster.spec_io import read_spec

    payload = read_spec(args.spec)
    rows = run_task(payload, pack=args.pack)
    n_ok = sum(1 for r in rows if r.get("ok"))
    # 2026-07-12 (live-rehearsal fix): failed rows carried their error string but the log printed
    # only counts — a node-side failure was UNDIAGNOSABLE from the .o file (the scalar_g0 sandbox
    # reject surfaced as a bare rc=1). One line per failure, greppable, before the summary.
    for r in rows:
        if not r.get("ok"):
            print(json.dumps({"failed": r.get("candidate_id") or r.get("run_id"),
                              "error": str(r.get("error"))[:500]}), flush=True)
    print(json.dumps({"task": args.spec, "n": len(rows), "ok": n_ok}))
    return 0 if n_ok == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
