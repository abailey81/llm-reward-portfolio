"""Calibrate MAX training throughput across GPU+CPU (heterogeneous concurrency).

Runs several short SB3-SAC trainings concurrently across a mix of GPU and CPU workers and
reports the AGGREGATE steps/s (sum of per-worker rates — each worker measures its own rate, so
the sum correctly accounts for GPU time-slicing / CPU oversubscription). The configuration with
the highest aggregate throughput is the one to use for the prototype run; its aggregate rate
directly gives the wall-clock for the full campaign (total_steps / aggregate_steps_s).

Usage:
    python scripts/bench_compute.py                 # default sweep, 2500 steps/worker
    python scripts/bench_compute.py --steps 4000    # longer (more steady-state, less spawn noise)
"""
from __future__ import annotations

import argparse
import multiprocessing as mp
import os
import time


def _worker(device: str, steps: int, idx: int, threads: int, q) -> None:
    """Train one SAC for ``steps`` on ``device``; report its own steps/s on ``q``."""
    try:
        # Limit CPU threads per worker so concurrent CPU jobs don't oversubscribe the 16 threads.
        os.environ["OMP_NUM_THREADS"] = str(threads)
        import torch

        torch.set_num_threads(max(1, threads))
        from src.agents.factory import make_headline_agent
        from src.data.synthetic import make_synthetic_panel
        from src.env.portfolio_env import PortfolioEnv
        from src.utils.config import load_config

        panel = make_synthetic_panel(n_assets=30, n_days=600, seed=idx)
        cfg = load_config("environment")

        def reward(w, r, pw, pr, info):  # noqa: ANN001
            return float(pr), {"pr": float(pr)}, None

        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        try:
            torch.set_float32_matmul_precision("high")
        except Exception:  # noqa: BLE001
            pass
        env = PortfolioEnv(panel, cfg, reward)
        agent = make_headline_agent(
            env,
            {"buffer_size": steps, "batch_size": 512, "device": device, "seed": idx, "verbose": 0},
        )
        t0 = time.perf_counter()
        agent.learn(total_timesteps=steps)
        dt = time.perf_counter() - t0
        q.put((device, steps / dt if dt > 0 else 0.0))
    except Exception as exc:  # noqa: BLE001
        q.put((device, -1.0))
        import sys

        print(f"[worker {idx} {device}] FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)


def bench(n_gpu: int, n_cpu: int, steps: int) -> dict:
    """Run ``n_gpu`` cuda + ``n_cpu`` cpu workers concurrently; return aggregate throughput."""
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    # Per the compute research: 1 thread per worker (avoid oversubscribing the 16 hardware threads;
    # SB3 SAC's small matmuls don't parallelize well, so many 1-thread workers beat few fat ones).
    specs = [("cuda", i, 1) for i in range(n_gpu)] + [("cpu", n_gpu + i, 1) for i in range(n_cpu)]
    procs = [ctx.Process(target=_worker, args=(dev, steps, idx, th, q)) for dev, idx, th in specs]
    t0 = time.perf_counter()
    for p in procs:
        p.start()
    rates = [q.get() for _ in procs]
    for p in procs:
        p.join()
    wall = time.perf_counter() - t0
    gpu = [r for d, r in rates if d == "cuda" and r > 0]
    cpu = [r for d, r in rates if d == "cpu" and r > 0]
    return {
        "n_gpu": n_gpu,
        "n_cpu": n_cpu,
        "agg": sum(r for _, r in rates if r > 0),
        "wall": wall,
        "gpu_each": gpu,
        "cpu_each": cpu,
        "n_failed": sum(1 for _, r in rates if r <= 0),
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Calibrate max GPU+CPU training throughput.")
    p.add_argument("--steps", type=int, default=2500, help="Steps per worker (default 2500).")
    p.add_argument(
        "--configs",
        default="1x0,3x0,0x10,3x8,3x10,2x12,4x8",
        help="Comma list of '<gpu>x<cpu>' worker configs.",
    )
    args = p.parse_args()
    configs = [tuple(int(x) for x in c.split("x")) for c in args.configs.split(",")]

    print(f"Calibrating ({args.steps} steps/worker). Full prototype = 240 cand x 25k = 6,000,000 steps.\n")
    print(f"{'gpu':>3} {'cpu':>3} | {'agg steps/s':>11} | {'full-run h':>10} | gpu_each / cpu_each")
    print("-" * 78)
    best = None
    for g, c in configs:
        r = bench(g, c, args.steps)
        agg = r["agg"]
        full_h = (6_000_000 / agg / 3600) if agg > 0 else float("inf")
        ge = ",".join(f"{x:.0f}" for x in r["gpu_each"]) or "-"
        ce = ",".join(f"{x:.0f}" for x in r["cpu_each"]) or "-"
        fail = f"  FAILED={r['n_failed']}" if r["n_failed"] else ""
        print(f"{g:>3} {c:>3} | {agg:>11.0f} | {full_h:>10.1f} | [{ge}] / [{ce}]{fail}")
        if r["n_failed"] == 0 and (best is None or agg > best[2]):
            best = (g, c, agg)
    if best:
        g, c, agg = best
        print("-" * 78)
        print(
            f"BEST: gpu={g} cpu={c} -> {agg:.0f} aggregate steps/s  "
            f"=> full 240x25k prototype ~ {6_000_000 / agg / 3600:.1f} hours "
            f"(at 20k steps ~ {4_800_000 / agg / 3600:.1f} h)"
        )


if __name__ == "__main__":
    main()
