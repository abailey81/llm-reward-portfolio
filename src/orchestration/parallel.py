"""Heterogeneous GPU+CPU candidate-training scheduler — MAX laptop throughput (P5+).

Decouples the (fast, sequential) arm logic — LLM reflection / search — from the (heavy, parallel)
per-candidate SAC training. Arm DRIVERS run as threads in the main process and submit candidate
TASKS to a shared process pool of device-tagged workers; a device-token queue load-balances
``n_gpu`` 'cuda' + ``n_cpu`` 'cpu' concurrent trainings so the (faster) GPU AND all CPU threads stay
saturated, and the slow per-arm-serial bottleneck of arm-level parallelism is removed.

Per the compute deep-research (sources recorded in CHANGELOG): each worker pins threads=1 (OMP/MKL
+ torch) BEFORE imports; per job ``batch_size=512`` + TF32 on (AMP off); ``DummyVecEnv``;
``ProcessPoolExecutor`` with NON-daemon workers (so the sandbox validate-once child can spawn);
``empty_cache()`` between GPU tasks; the panel is loaded ONCE per worker and cached.

This is the FAST path for the real run; ``scripts/run_prototype.py`` keeps the simple arm-level path
(verified by the dry-run + tests). DIRECTIONAL / plumbing only — no number enters the dissertation.
"""
from __future__ import annotations

import hashlib
import multiprocessing as mp
import queue
import time
from collections.abc import Sequence
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, cast

import numpy as np

__all__ = [
    "DevicePool",
    "train_candidate",
    "run_parallel",
    "run_recycling",
    "auto_n_gpu",
    "max_power_config",
]


def auto_n_gpu(train_steps: int = 25000, *, obs_dim: int = 1900, reserve_gb: float = 4.0,
               vram_ctx_mb: int = 1400, cap: int = 12) -> int:
    """Max sustainable CONCURRENT training workers on THIS machine — bounded by RAM, VRAM, and cores.

    Each worker holds a replay buffer of ``train_steps x obs_dim x 4 B x 2`` (obs+next_obs, float32) plus
    a torch/SB3/panel base (~0.8 GB) in RAM, and a CUDA context + model/batch (~``vram_ctx_mb``) in VRAM.
    We pick the largest worker count that fits available RAM (minus ``reserve_gb`` for the OS/main process)
    AND free VRAM AND the physical-core count — pushing the laptop to its real ceiling WITHOUT swapping
    (which would be slower). Measured + tuned by the Phase-0 scaling probe; override with ``--gpu N``.
    """
    import psutil

    phys = psutil.cpu_count(logical=False) or 4
    buf_gb = train_steps * obs_dim * 4 * 2 / 2**30
    # Per-worker RAM = replay buffer + torch/SB3/panel/CUDA-context overhead. The ~1.4 GB base is calibrated
    # to the MEASURED ceiling (2026-06-20): n_gpu=5 hit CPU MemoryError + CUDA-OOM, n_gpu=4 was the max.
    per_worker_gb = buf_gb + 1.4
    vm = psutil.virtual_memory()
    # Budget off TOTAL RAM minus a fixed OS/main reserve (steady state) — NOT the momentary ``available``,
    # which is depressed by transient caches / other processes; the run's lasting working set is the worker
    # replay buffers. Take the larger of the two so a transient dip doesn't under-provision the max run.
    budget_gb = max(vm.available / 2**30, vm.total / 2**30 - reserve_gb)
    ram_bound = max(1, int(budget_gb / max(per_worker_gb, 0.1)))
    vram_bound = cap
    try:
        import pynvml

        pynvml.nvmlInit()
        free_mb = pynvml.nvmlDeviceGetMemoryInfo(pynvml.nvmlDeviceGetHandleByIndex(0)).free // 2**20
        vram_bound = max(1, int(free_mb / vram_ctx_mb))
    except Exception:  # pragma: no cover - no NVML / no GPU
        pass
    return max(1, min(phys, ram_bound, vram_bound, cap))


def max_power_config(
    train_steps: int = 50000,
    *,
    gpu_cap: int = 2,
    obs_dim: int = 1900,
    reserve_gb: float = 4.0,
    cpu_only: bool = False,
) -> tuple[int, int]:
    """Recommended ``(n_gpu, n_cpu)`` to drive THIS machine at its full *heterogeneous* throughput.

    Rationale (compute deep-research + ``docs/CAMPAIGN_SPEC_ram_thermal.md``): SAC on the small portfolio
    nets is OVERHEAD-bound, so a CPU worker trains within ~1.5x of a GPU worker AND bypasses the 6 GiB VRAM
    ceiling entirely. GPU workers are therefore capped at ``gpu_cap`` (the transition-wave-safe ceiling at
    50k — ``n_gpu=4`` OOMs the 6 GiB RTX-4050), and CPU workers fill the remaining PHYSICAL cores within a
    RAM budget (each worker holds a ~``train_steps`` replay buffer + ~1.4 GB torch/SB3/panel/CUDA base; one
    thread per worker). ``cpu_only=True`` returns ``(0, all-safe-cores)`` for a GPU-less box.

    .. warning::
       This is a *hardware* recommendation; it is NOT automatically safe for the frozen confirmatory run.
       Two pre-registration constraints cap the usable parallelism BELOW this hardware ceiling:

       * **TEST leg (the winner seeds = inference data):** the parallel path is byte-identical to serial
         only on a SINGLE device. Mixing CPU + GPU workers makes results device-dependent (CPU != CUDA
         bit-for-bit), so for the frozen run use **GPU-only** here (``n_cpu=0``), not this heterogeneous mix.
       * **SEARCH leg:** ``run_parallel`` reflects on the generation's BEST candidate, whereas the FROZEN
         protocol is ``serial_reflect_on_last`` — so enabling search parallelism is an *amendment-gated
         frozen-decision change*, not a free speed-up.

       The heterogeneous ``(n_gpu, n_cpu)`` returned here is therefore appropriate for the ``--synthetic`` /
       dev / ``bench_compute`` paths (no pre-registration in force), or for a leg the user has explicitly
       amended. Pure recommendation — it trains nothing.
    """
    import psutil

    phys = int(psutil.cpu_count(logical=False) or 4)
    buf_gb = train_steps * obs_dim * 4 * 2 / 2**30
    per_worker_gb = buf_gb + 1.4
    vm = psutil.virtual_memory()
    budget_gb = max(vm.available / 2**30, vm.total / 2**30 - reserve_gb)
    ram_workers = max(1, int(budget_gb / max(per_worker_gb, 0.1)))
    n_gpu = 0 if cpu_only else max(1, min(int(gpu_cap), ram_workers))
    n_cpu = max(0, min(phys - n_gpu, ram_workers - n_gpu))
    return int(n_gpu), int(n_cpu)


#: Per-worker caches (loaded once; workers are reused, max_tasks_per_child=None).
_PANEL_CACHE: dict[str, Any] = {}

#: Anonymised validation fixture for the sandbox (no tickers/dates). Real-ish length (~30 risky +
#: cash) so an allocation that scales with the input surfaces at validate_once (final-audit #12).
_FIXTURE: tuple[Any, ...] = (
    np.full(31, 1.0 / 31),
    np.full(31, 0.001),
    np.full(31, 1.0 / 31),
    0.0,
    {},
)
_LLM_ARMS = ("distributional", "scalar", "placebo", "scalar_cvar5", "placebo_shuffled")


def _worker_init() -> None:
    """ProcessPoolExecutor initializer: pin threads BEFORE any heavy import (research §2/§3)."""
    import os

    for var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[var] = "1"
    os.environ.setdefault(
        "PYTORCH_CUDA_ALLOC_CONF", "max_split_size_mb:128,garbage_collection_threshold:0.8"
    )
    # Preload pyarrow BEFORE torch: the worker loads the REAL gold parquet (pyarrow) + trains (torch), and
    # importing pyarrow AFTER torch SIGSEGVs (ABI conflict, verified 2026-06-20). pyarrow must win the native
    # load. See src.utils.preload. Inline (not the helper) so it runs before ANY src import in the spawn child.
    import pyarrow.parquet  # noqa: F401

    import torch

    torch.set_num_threads(1)
    try:
        torch.set_num_interop_threads(1)
    except Exception:  # noqa: BLE001 - only settable once
        pass


def _panel_and_windows(synthetic: bool, data: dict, lookback: int):
    key = "syn" if synthetic else f"gold:{data.get('phase')}:{data.get('train_end')}:{data.get('val_end')}"
    if key in _PANEL_CACHE:
        return _PANEL_CACHE[key]
    if synthetic:
        from src.data.synthetic import make_synthetic_panel

        panel = make_synthetic_panel(n_assets=30, n_days=600, seed=0)
        res = (panel, (lookback, 400), (400, panel.T))
    else:
        from src.data.loaders import OnMissing, embargoed_val_start, load_gold_panel

        phase = str(data.get("phase", "development"))
        train_end = str(data.get("train_end", "2014-12-31"))
        from src.utils.config import load_config

        # Embargo fallback = the canonical config/data.yaml floor, NOT a bare literal 21 (no-hardcoding audit).
        _emb_floor = int(load_config("data").get("embargo_days", 21))
        embargo_days = int(data.get("embargo_days", _emb_floor))
        r = load_gold_panel(
            phase=phase,
            end=str(data.get("val_end", "2017-12-31")),
            on_missing=cast(OnMissing, data.get("on_missing", "liquidate_to_cash")),
        )
        panel = r.panel
        dates = np.asarray(panel.dates)
        # Train ends at ``train_end``; validation begins at the PURGED boundary (PREREGISTRATION §7, R18):
        # embargoed_val_start(lookback=lookback) = max(materialized embargo boundary 2015-02-03,
        # train_end + max(embargo, lookback)). With lookback=60 the lookback purge dominates (val ~2015-03-31).
        # Matches run_prototype._load_panel_and_windows so BOTH executed paths drop the same gap (R18).
        train_split = int(np.searchsorted(dates, np.datetime64(train_end)) + 1)
        train_split = max(lookback + 1, min(train_split, panel.T - 1))
        val_split = embargoed_val_start(
            dates, train_end, phase=phase, embargo_days=embargo_days, lookback=lookback
        )
        val_split = max(train_split, min(val_split, panel.T - 1))
        res = (panel, (lookback, train_split), (val_split, panel.T))
    _PANEL_CACHE[key] = res
    return res


def train_candidate(spec: dict) -> dict:
    """Worker: build the reward, train the fixed SAC on ``spec['device']``, return fitness + tails.

    ``spec['reward_kind']`` is ``"source"`` (untrusted LLM/search code → sandbox-validated),
    ``"coeffs"`` (H4 reward family), or ``"baseline"`` (a hand-designed reward by name). Returns a
    picklable dict ``{ok, candidate_id, arm, fitness, val_returns, tail_stats, reward_source, ...}``.
    """
    from src.utils.env import load_env

    load_env()  # ensure the LLM key is in this worker's env (ADR-038) in case spawn didn't inherit it
    import torch  # kept for cuda.empty_cache below; TF32 is now set by train_agent
    # (config-driven, ``tf32`` default on) so the SEARCH worker, the serial trainer, and the parallel TEST
    # worker share IDENTICAL float32 numerics (no scheduler-dependent precision drift — manager review P2).

    out: dict[str, Any] = {"ok": False, "candidate_id": spec.get("candidate_id"), "arm": spec.get("arm")}
    # Candidate-parallel monitoring: stream per-step training metrics + lifecycle to the main
    # ParallelMonitor over ``spec['monitor_queue']`` (a Manager queue; absent in tests/unmonitored runs).
    sink = None
    _mq = spec.get("monitor_queue")
    if _mq is not None:
        from src.utils.monitoring import QueueSink

        sink = QueueSink(_mq, str(spec.get("candidate_id")), str(spec.get("arm")))
    _cand_t0 = time.perf_counter()
    try:
        from src.utils.seeding import set_global_seed

        # P0-3 (audit 2026-06-19): seed EVERY RNG stack in the worker process -- not just the
        # SAC kwarg. Python random, the legacy np.random global (read by VecNormalize/SB3),
        # PYTHONHASHSEED, torch + cuDNN, and the deterministic-algorithm flags.
        set_global_seed(int(spec["seed"]), deterministic_torch=True)

        from src.agents.trainer import make_agent_trainer
        from src.env.runner import make_env_builder
        from src.feedback.measurement import ReturnDistribution
        from src.selection.fitness import held_out_fitness
        from src.utils.config import load_config

        env_cfg = load_config("environment")
        lookback = int(env_cfg["state"]["lookback_days"])
        panel, tw, vw = _panel_and_windows(bool(spec["synthetic"]), spec.get("data", {}), lookback)
        device = spec.get("device", "cpu")

        kind = spec["reward_kind"]
        if kind == "source":
            from src.sandbox.executor import SandboxError, validate_once

            src = spec["reward"]
            out["reward_source"] = src
            out["reward_hash"] = hashlib.sha256(src.encode("utf-8")).hexdigest()
            try:
                reward_fn = validate_once(src, _FIXTURE)
            except SandboxError as exc:
                out["error"] = f"sandbox: {exc}"
                out["failed_validation"] = True
                return out
        elif kind == "coeffs":
            from src.baselines.reward_family import params_to_reward, params_to_source

            alpha, window = spec.get("cvar_alpha", 0.05), spec.get("window", 20)
            reward_fn = params_to_reward(spec["reward"], alpha, window)
            # Rank 2c: archive the MATERIALIZED EXECUTABLE source so the frozen BO winner rehydrates
            # through validate_once for the sealed TEST leg (H4) — not a non-executable comment stub.
            out["reward_source"] = params_to_source(spec["reward"], cvar_alpha=alpha, window=window)
            out["reward_hash"] = hashlib.sha256(out["reward_source"].encode("utf-8")).hexdigest()
        else:  # baseline
            from src.baselines import rewards as R

            reward_fn = getattr(R, spec["reward"])
            out["reward_source"] = f"# baseline:{spec['reward']}\n"
            out["reward_hash"] = hashlib.sha256(out["reward_source"].encode("utf-8")).hexdigest()

        env_builder = make_env_builder(panel, env_cfg, tw, vw)
        if sink is not None:
            sink.candidate_start()
        trainer = make_agent_trainer(
            {
                "train_steps_per_candidate": int(spec["train_steps"]),
                "buffer_size": int(spec["train_steps"]),
                "batch_size": int(spec.get("batch_size", 256)),  # ONE canonical default (SB3); was 512 -> 256/512 drift
                "normalize_obs": bool(spec.get("normalize_obs", True)),
                "learning_rate": float(spec.get("learning_rate", 3e-4)),  # honor the full agent block (parity)
                "gamma": float(spec.get("gamma", 0.99)),
                "ent_coef": spec.get("ent_coef", "auto"),
                # learning_starts (gated 1000, not SB3's silent 100) + PopArt scale-normalization (default on):
                # thread them through the parallel worker so the SEARCH/TEST path trains the SAME agent as the
                # serial path (the trainer floors learning_starts at 1000 and gates popart on `popart`).
                "learning_starts": int(spec.get("learning_starts", 1000)),
                "popart": bool(spec.get("popart", True)),
                "popart_beta": float(spec.get("popart_beta", 1e-3)),
                "popart_min_scale": float(spec.get("popart_min_scale", 1.0)),
                "popart_warmup": int(spec.get("popart_warmup", 0)),
                "tf32": bool(spec.get("tf32", True)),
                "device": device,
            },
            int(spec["seed"]),
            monitor=sink,  # streams per-step SAC metrics to the main ParallelMonitor (anomaly detection)
        )
        bundle = env_builder(reward_fn)
        policy = trainer(bundle.train_env())
        popart_scale = getattr(policy, "popart_scale", None)  # T2.4 realised scale (read before the del below)
        val = np.asarray(bundle.val_returns(policy), dtype=float)
        train = np.asarray(bundle.train_returns(policy), dtype=float)
        fitness = float(held_out_fitness(val, int(spec.get("n_trials", 40))))
        tail = ReturnDistribution().fit(train).tail_stats()
        if str(device).startswith("cuda"):
            torch.cuda.empty_cache()
        out.update(ok=True, fitness=fitness, val_returns=[float(x) for x in val], tail_stats=tail,
                   popart_scale=popart_scale)
        if sink is not None:
            sink.candidate_done(fitness=fitness, status="ok", secs=time.perf_counter() - _cand_t0)
        # Reclaim this candidate's heavy objects in the PERSISTENT pool worker BEFORE the next candidate.
        # SB3's SAC holds cyclic refs (policy <-> optimizer <-> replay buffer, ~0.36 GiB obs arrays), so
        # without an explicit del + gc.collect() the freed memory is NOT reclaimed and the worker RSS CREEPS
        # across candidates -> OOM over a long run (measured without this: n_gpu=2 71 -> 85% in 40 min; n_gpu=3
        # 89.6 -> 96.3%). The clean fix (max_tasks_per_child worker recycling) DEADLOCKS on Python 3.11.9 +
        # Windows spawn, so reclaim in-process instead. Results are already captured in `out` (no science
        # change); numpy replay buffers are mmap'd -> returned to the OS on collection.
        del trainer, bundle, policy, val, train
        import gc

        gc.collect()
    except Exception as exc:  # noqa: BLE001 - a failed candidate must not crash the pool
        import traceback

        out["error"] = f"{type(exc).__name__}: {exc}"
        out["trace"] = traceback.format_exc().splitlines()[-3:]
        if sink is not None:
            # Surface the ERROR REASON to the live monitor (not just status) so a failure wave -- e.g. the
            # CUDA-OOM cascade at too-high n_gpu -- is caught immediately, not buried in failures.jsonl.
            sink.candidate_done(fitness=None, status="error", secs=time.perf_counter() - _cand_t0,
                                error=str(out["error"])[:200])
        if str(spec.get("device", "")).startswith("cuda"):
            try:
                import torch

                torch.cuda.empty_cache()  # release this candidate's VRAM after an OOM/error before the next
            except Exception:  # noqa: BLE001
                pass
    return out


#: Sentinel so ``DevicePool(initializer=None)`` means "no worker initializer" (used by fast unit
#: tests that must not import torch/pyarrow), while the default stays the production ``_worker_init``.
_DEFAULT_INIT = object()


class DevicePool:
    """A device-load-balanced process pool: ``n_gpu`` cuda + ``n_cpu`` cpu concurrent training slots.

    ``submit(spec)`` blocks until a device token frees, tags the spec with that device, submits
    ``train_candidate`` to the pool, and returns the token when the future completes — so at most
    ``n_gpu`` trainings run on the GPU and ``n_cpu`` on the CPU at any instant (no VRAM/RAM blow-up,
    GPU time-slicing bounded).
    """

    def __init__(
        self,
        n_gpu: int,
        n_cpu: int,
        max_tasks_per_child: int | None = None,
        initializer: Any = _DEFAULT_INIT,
    ) -> None:
        self.n_gpu = max(0, int(n_gpu))
        self.n_cpu = max(0, int(n_cpu))
        if self.n_gpu + self.n_cpu == 0:
            self.n_cpu = 1  # CPU-only fallback when no GPU is present
        self._tokens: queue.Queue[str] = queue.Queue()
        for _ in range(self.n_gpu):
            self._tokens.put("cuda")
        for _ in range(self.n_cpu):
            self._tokens.put("cpu")
        ctx = mp.get_context("spawn")
        # max_tasks_per_child: RECYCLE each worker after N candidates so the OS reclaims its heap (each
        # candidate alloc/frees a ~0.36 GiB replay buffer; without recycling the persistent workers' RSS
        # creeps from fragmentation). None = reuse workers forever (the PROVEN behavior). WARNING: a non-None
        # value HANGS on Windows + spawn across CPython 3.11-3.14 (deadlock measured 2026-06-24, all four) ->
        # the campaign reclaims RAM via ``run_recycling`` (fresh pools per batch) instead, and config keeps
        # this null. Passed explicitly (not via ``**kwargs``) so the call type-checks cleanly.
        # The initializer pins worker threads + preloads pyarrow-before-torch (production). Tests pass
        # ``initializer=None`` to spawn bare workers (no heavy imports), keeping the recycling unit test fast.
        _init: Callable[[], object] | None = (
            _worker_init if initializer is _DEFAULT_INIT else initializer
        )
        self._ex = ProcessPoolExecutor(
            max_workers=self.n_gpu + self.n_cpu,
            mp_context=ctx,
            initializer=_init,
            max_tasks_per_child=None if max_tasks_per_child is None else int(max_tasks_per_child),
        )

    def submit(self, spec: dict) -> Future:
        token = self._tokens.get()  # blocks until a device is free
        fut = self._ex.submit(train_candidate, {**spec, "device": token})
        # token is a fresh per-call local (NOT a mutating loop var), so a plain closure captures it
        # correctly; no `t=token` default needed (which also broke the callback's type inference).
        fut.add_done_callback(lambda _f: self._tokens.put(token))
        return fut

    def submit_with(self, fn: Any, spec: dict) -> Future:
        """Like :meth:`submit` but runs an ARBITRARY picklable ``fn(spec)`` on the next free device
        token, instead of the default :func:`train_candidate`. Used for the TEST-leg worker so the
        winner re-runs share the SAME device-load-balanced pool as the search trainings.
        """
        token = self._tokens.get()  # blocks until a device is free
        fut = self._ex.submit(fn, {**spec, "device": token})
        # token is a fresh per-call local (NOT a mutating loop var), so a plain closure captures it
        # correctly; no `t=token` default needed (which also broke the callback's type inference).
        fut.add_done_callback(lambda _f: self._tokens.put(token))
        return fut

    def __enter__(self) -> "DevicePool":
        return self

    def __exit__(self, *exc: Any) -> None:
        self._ex.shutdown(wait=True)


def run_recycling(
    specs: list[dict],
    *,
    worker: Any,
    n_gpu: int,
    n_cpu: int,
    recycle_every: int,
    initializer: Any = _DEFAULT_INIT,
) -> list:
    """Run ``specs`` through a SEQUENCE of fresh :class:`DevicePool`s of ``recycle_every`` tasks each.

    Tearing each pool down between batches (the ``with`` exit calls ``shutdown(wait=True)`` ->
    worker processes terminate) makes the OS reclaim each worker's ENTIRE address space — the
    fragmented SAC replay-buffer heap included — so per-worker RSS cannot creep across a long run.
    This is the deadlock-free substitute for ``max_tasks_per_child`` worker recycling, which HANGS on
    Windows + spawn across CPython 3.11-3.14 (measured 2026-06-24). The pool re-spawn (~15 s) is
    amortized over ``recycle_every`` trainings. Results are returned in submission order.

    Parameters
    ----------
    specs:
        The per-task spec dicts (e.g. one per ``(winner, seed)`` TEST run).
    worker:
        The picklable worker callable ``worker(spec) -> result`` run in each pool process. It SHOULD
        catch its own failures and return a result (e.g. ``{"ok": False, "error": ...}`` like
        ``train_candidate``); if it instead RAISES, the exception is captured as a failed result so a
        single worker crash (e.g. a CUDA OOM) never aborts the batch or the remaining batches.
    n_gpu, n_cpu:
        Concurrent cuda / cpu slots per pool (see :class:`DevicePool`).
    recycle_every:
        Tasks per pool before it is torn down and a fresh one is spawned (the RAM-reclaim cadence).
    initializer:
        Worker initializer; defaults to the production ``_worker_init`` (thread pinning +
        pyarrow-before-torch). Tests pass ``None`` for bare workers.
    """
    out: list = []
    specs = list(specs)
    step = max(1, int(recycle_every))
    for i in range(0, len(specs), step):
        batch = specs[i : i + step]
        with DevicePool(n_gpu, n_cpu, initializer=initializer) as pool:
            futs = [pool.submit_with(worker, s) for s in batch]
            for f in futs:
                try:
                    out.append(f.result())
                except Exception as exc:  # noqa: BLE001 — a worker that RAISES (rather than returning
                    # an error result like ``train_candidate``) must NOT abort the batch or the remaining
                    # batches; capture it so every spec is still attempted (the caller checks ``ok`` and
                    # the matched-budget guard surfaces a failure wave). Order is preserved (futs order).
                    out.append({"ok": False, "error": f"{type(exc).__name__}: {exc}"})
    return out


def _spec(arm: str, kind: str, reward: Any, cid: str, opts: dict) -> dict:
    return {
        "arm": arm,
        "reward_kind": kind,
        "reward": reward,
        "candidate_id": cid,
        "train_steps": opts["train_steps"],
        "batch_size": opts["batch_size"],
        "normalize_obs": opts["normalize_obs"],
        "learning_rate": opts.get("learning_rate", 3e-4),  # honor the full agent block (parity w/ serial + TEST)
        "gamma": opts.get("gamma", 0.99),
        "ent_coef": opts.get("ent_coef", "auto"),
        # learning_starts (gated 1000) + PopArt scale-normalization: threaded so the SEARCH worker trains the
        # SAME agent as serial/TEST (parity; the trainer floors learning_starts at 1000 and gates popart).
        "learning_starts": opts.get("learning_starts", 1000),
        "popart": opts.get("popart", True),
        "popart_beta": opts.get("popart_beta", 1e-3),
        "popart_min_scale": opts.get("popart_min_scale", 1.0),
        "popart_warmup": opts.get("popart_warmup", 0),
        "tf32": opts.get("tf32", True),
        "n_trials": opts["n_trials"],
        "synthetic": opts["synthetic"],
        "data": opts["data"],
        "cvar_alpha": opts["cvar_alpha"],
        "window": opts["window"],
        "seed": opts["seed"],
        "monitor_queue": opts.get("monitor_queue"),  # main ParallelMonitor's queue (None when unmonitored)
    }


#: Process-local cache of the (expensive) env capture + its sha256, keyed by seed. The environment
#: doesn't change within a run, so capture pip-freeze/nvidia-smi/torch-cuda ONCE per (process, seed).
_ENV_CACHE: dict[Any, tuple[dict, str]] = {}


def _capture_env_cached(seed: Any) -> tuple[dict, str]:
    key = seed
    if key not in _ENV_CACHE:
        from scripts.capture_env import capture_env, env_json_sha256

        env = capture_env(seed=int(seed) if isinstance(seed, (int, float)) else None)
        _ENV_CACHE[key] = (env, env_json_sha256(env=env))
    return _ENV_CACHE[key]


def _run_env_fp(arm_root: str, run_id: str, opts: dict) -> Any:
    """Write ``<arm_root>/<run_id>/env.json`` and return the record's ``env_fingerprint`` (Rank 14).

    Best-effort: on any failure (e.g. torch absent in a degraded env) it falls back to the bare
    ``opts['env_fp']`` label so archiving never breaks. On success the returned dict pairs the
    human-readable label with the content-hash of the on-disk ``env.json`` so the record resolves
    back to a full, replayable environment snapshot (audit C-2/C-6).
    """
    import json as _json

    label = opts.get("env_fp", "")
    try:
        env, digest = _capture_env_cached(opts.get("seed"))
        run_dir = Path(arm_root) / str(run_id)
        run_dir.mkdir(parents=True, exist_ok=True)
        with (run_dir / "env.json").open("w", encoding="utf-8") as fh:
            _json.dump(env, fh, indent=2, sort_keys=True, default=str)
        return {"label": label, "env_json_sha256": digest}
    except Exception:  # noqa: BLE001 - provenance capture must never crash a candidate's archive
        return label


def _archive(result: dict, arm: str, opts: dict, archive_root: str, generation: int = 0) -> None:
    from src.io.results import write_run

    cid = result["candidate_id"]
    arm_root = str(Path(archive_root) / arm)
    write_run(
        {
            "run_id": cid,
            "arm": arm,
            "seed": opts["seed"],
            "fold": 0,
            "candidate_id": cid,
            "generation": generation,
            # Rank 14: persist the rendered prompt so the replay archive doesn't DROP it (CLAUDE.md
            # directive 6). The LLM driver injects ``prompt``; search arms have no prompt -> "".
            "prompt": result.get("prompt", ""),
            "reward_source": result.get("reward_source", ""),
            "reward_source_hash": result.get("reward_hash", ""),
            "feedback_block": "",
            "metrics": {
                "val_fitness": result.get("fitness", float("-inf")),
                "val_returns": result.get("val_returns"),
                "tail_stats": result.get("tail_stats"),
                # T2.4: realised PopArt scale (sigma_max/last) the critic saw, for the cross-arm sigma audit.
                # Optional/back-compatible — omitted when the worker didn't surface it (older records / fakes).
                **(
                    {"popart_scale": result["popart_scale"]}
                    if result.get("popart_scale") is not None
                    else {}
                ),
            },
            "wall_clock": 0.0,
            # Rank 14: the env_fingerprint is the REAL provenance now, not a bare label. ``_run_env_fp``
            # writes <run_dir>/env.json (full CI-grade capture) and returns {label, env_json_sha256} so
            # the record points at a replayable, content-hashed environment snapshot (audit C-2/C-6).
            "env_fingerprint": _run_env_fp(arm_root, cid, opts),
        },
        arm_root,
    )


def _summary(arm: str, accepted: list, failed: int, expected: int) -> dict:
    winner = max(accepted, key=lambda r: r["fitness"]) if accepted else None
    return {
        "arm": arm,
        "n_candidates": len(accepted),
        "n_failed": failed,
        "winner_fitness": None if winner is None else float(winner["fitness"]),
        # Require the full budget AND at least one ACCEPTED candidate (re-audit: this parallel twin
        # of run_arm's matched-budget check lacked the accepted>0 guard from final-audit #21, so an
        # all-failures arm reported healthy; this flag drives the campaign-level health verdict).
        "matched_budget_ok": (len(accepted) + failed) == expected and len(accepted) > 0,
    }


def _drive_llm_arm(arm: str, pool: DevicePool, opts: dict, archive_root: str) -> dict:
    from src.feedback import schema
    from src.llm.client import LLMClient
    from src.llm.loop import _REFLECTION_PREAMBLE, _diversity_directive
    from src.llm.prompts import build_prompt_set
    from src.sandbox.executor import extract_reward_source

    if opts["pass_mode"].upper() == "A" or opts["provider"] == "stub":
        from src.llm.stub_designer import StubDesignerTransport

        transport: Any = StubDesignerTransport(seed=opts["seed"])
        model = f"stub-designer/seed{opts['seed']}"
    else:
        from src.llm.client import build_transport, default_key_env

        model = opts["model"]
        temp_raw = opts.get("temperature")
        temperature = float(temp_raw) if temp_raw is not None else None
        key_env = opts.get("api_key_env") or default_key_env(opts["provider"])
        transport = build_transport(opts["provider"], model, key_env, temperature=temperature)

    diversity = bool(opts.get("diversity_prompt_variation", False))

    prompts = build_prompt_set(opts["env_cfg"], opts["n_assets"])
    llm = LLMClient({"model": model}, transport=transport)
    gens = max(1, int(opts["generations"]))
    cpg = max(1, int(opts["candidates"]) // gens)
    accepted: list = []
    failures: list = []
    failed = 0
    prev_block: str | None = None
    for gen in range(gens):
        # Reflection PREAMBLE identical to src/llm/loop.py (final-audit #34: both paths share the same
        # preamble string, not two different hand-written ones). NB the appended feedback `prev_block`
        # itself derives from each path's OWN selection — the serial loop seeds from its LAST candidate,
        # this scheduler from the generation's BEST — so the full reflection prompt is not byte-identical
        # across paths for multi-candidate generations; the headline campaign uses the SERIAL path.
        user = prompts.initial if prev_block is None else f"{_REFLECTION_PREAMBLE}\n{prev_block}"
        futs = []
        for k in range(cpg):
            # Per-candidate prompt variation -> within-generation diversity without temperature
            # (mirrors src/llm/loop.py; uniform across arms, not a feedback confound).
            cand_user = user
            if diversity and cpg > 1:
                cand_user = f"{user}\n\n{_diversity_directive(k, cpg)}"
            # Salvage fenced / prose-wrapped LLM output before it reaches the gate (final-audit P0).
            src = extract_reward_source(llm.complete(prompts.system, cand_user))
            # Rank 14: carry the rendered user prompt alongside the future so the archive can persist
            # the EXACT prompt sent (the worker result dict has no prompt; directive 6). candidate_id
            # uses the per-generation index `k` (final-audit #22/#33: matches src/llm/loop.py and keeps
            # the archived directive index consistent with the id, instead of a global counter).
            futs.append((cand_user, pool.submit(_spec(arm, "source", src, f"{arm}-g{gen}-c{k}", opts))))
        best = None
        for user_prompt, f in futs:
            r = f.result()
            if not r.get("ok"):
                failed += 1
                # Capture the failed source + error (re-audit / final-audit #21 parity: the parallel
                # path discarded failures, so a total-failure arm was undiagnosable from the archive).
                failures.append({
                    "candidate_id": r.get("candidate_id"),
                    "prompt": user_prompt,
                    "reward_source": r.get("reward_source"),
                    "error": r.get("error"),
                })
                continue
            r["prompt"] = user_prompt
            _archive(r, arm, opts, archive_root, generation=gen)
            accepted.append(r)
            if best is None or r["fitness"] > best["fitness"]:
                best = r
        if best is not None:
            tail_for = (
                best.get("tail_stats")
                if arm in ("distributional", "scalar_cvar5", "placebo_shuffled")
                else None
            )
            prev_block = schema.build_block(
                arm,
                best["fitness"],
                tail_for,
                shuffle_seed=(
                    schema.shuffle_seed_from_id(str(best.get("candidate_id", "")))
                    if arm == "placebo_shuffled"
                    else None
                ),
            )
    # Persist the raw LLM provenance + token usage (final-audit #36: the parallel path built the
    # LLMClient archive then discarded it, like the serial path before #16). Stubs archive nothing.
    _llm_archive = getattr(llm, "archive", None)
    if _llm_archive:
        import dataclasses
        import json

        _arm_dir = Path(archive_root) / arm
        _arm_dir.mkdir(parents=True, exist_ok=True)
        with (_arm_dir / "llm_calls.jsonl").open("w", encoding="utf-8") as _fh:
            for _rec in _llm_archive:
                _row = (
                    dataclasses.asdict(_rec)
                    if dataclasses.is_dataclass(_rec) and not isinstance(_rec, type)
                    else dict(_rec)
                )
                _fh.write(json.dumps(_row, default=str) + "\n")
    # Persist failed candidate sources (re-audit / final-audit #21 parity with run_arm).
    if failures:
        import json as _failjson

        _fdir = Path(archive_root) / arm
        _fdir.mkdir(parents=True, exist_ok=True)
        with (_fdir / "failures.jsonl").open("w", encoding="utf-8") as _ff:
            for _fl in failures:
                _ff.write(_failjson.dumps(_fl, default=str) + "\n")
    return _summary(arm, accepted, failed, gens * cpg)


def _drive_search_arm(arm: str, pool: DevicePool, opts: dict, archive_root: str) -> dict:
    n = int(opts["candidates"])
    if arm == "random_search":
        from src.search.random_search import sample_reward_source

        rng = np.random.default_rng(opts["seed"])
        # Draw the six family weights from the SAME frozen ranges the BO arm uses
        # (proto_cfg.reward_family.weights), so both H4 arms search the identical space.
        _rf_cfg = opts.get("proto_cfg")
        futs = [
            pool.submit(_spec(arm, "source", sample_reward_source(rng, _rf_cfg), f"{arm}-c{i}", opts))
            for i in range(n)
        ]
        results = [f.result() for f in futs]
        accepted = [r for r in results if r.get("ok")]
        for r in accepted:
            _archive(r, arm, opts, archive_root)
        return _summary(arm, accepted, len(results) - len(accepted), n)

    # bayes_opt — sequential BO (each evaluation trained via the shared pool, so it overlaps the
    # other arms; BO itself is inherently sequential).
    from src.baselines.reward_family import family_bounds
    from src.search.bayes_opt import bayes_opt_over_template

    state: dict[str, Any] = {"i": 0, "results": []}

    def template_eval(coeffs) -> float:
        cid = f"{arm}-c{state['i']}"
        state["i"] += 1
        r = pool.submit(_spec(arm, "coeffs", list(coeffs), cid, opts)).result()
        state["results"].append(r)
        return float(r["fitness"]) if r.get("ok") else -1e9

    # Seed the BO sampler from the run seed (re-audit: this parallel BO arm still drew OS entropy via
    # the rng=None default, so its winner was non-reproducible — the exact defect final-audit #2 closed
    # on the sequential path; random_search above already seeds the same way).
    bayes_opt_over_template(
        template_eval,
        cast(Sequence[Sequence[float]], family_bounds(opts.get("proto_cfg"))),
        {"matched_budget": n},
        rng=np.random.default_rng(opts["seed"]),
    )
    accepted = [r for r in state["results"] if r.get("ok")]
    for r in accepted:
        _archive(r, arm, opts, archive_root)
    return _summary(arm, accepted, len(state["results"]) - len(accepted), n)


def run_parallel(arms: list[str], opts: dict, n_gpu: int, n_cpu: int, archive_root: str) -> list[dict]:
    """Run all ``arms`` concurrently across a heterogeneous GPU+CPU candidate pool.

    Arm drivers run as threads (they only generate reward code / run light BO + archive); the heavy
    SAC trainings run in the ``DevicePool`` process workers, device-load-balanced.
    """
    # Live monitoring (candidate-parallel): the main ParallelMonitor drains a Manager queue that every
    # training worker streams per-step SAC metrics + lifecycle into — precise progress (run_done/run_total,
    # N concurrent trainings, ETA), deep JSONL event logs (incl. the driver threads' LLM/sandbox logs),
    # GPU/CPU/RAM telemetry, and CENTRAL anomaly detection. scripts/monitor.py renders it from progress.json.
    import threading

    from src.utils.monitoring import ParallelMonitor

    mgr = mp.Manager()
    opts = {**opts, "monitor_queue": mgr.Queue()}
    monitor = ParallelMonitor(
        archive_root,
        title="Prototype (parallel)",
        total_arms=len(arms),
        candidates_per_arm=int(opts.get("candidates", 0) or 0),
        train_steps=int(opts.get("train_steps") or 25000),
        model=str(opts.get("model", "?")),
    )
    stop = threading.Event()
    pump = threading.Thread(target=monitor.pump, args=(opts["monitor_queue"], stop), daemon=True)
    pump.start()
    summaries: list[dict] = []
    try:
        with DevicePool(n_gpu, n_cpu, opts.get("max_tasks_per_child")) as pool, \
                ThreadPoolExecutor(max_workers=max(1, len(arms))) as drivers:
            futs = {}
            for arm in arms:
                drive = _drive_llm_arm if arm in _LLM_ARMS else _drive_search_arm
                futs[drivers.submit(drive, arm, pool, opts, archive_root)] = arm
            for f in as_completed(futs):
                summaries.append(f.result())
        monitor.close(status="done")
    except BaseException:
        monitor.close(status="error")
        raise
    finally:
        stop.set()
        pump.join(timeout=3)
    return summaries
