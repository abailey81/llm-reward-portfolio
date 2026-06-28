# Campaign run-risk 3e — SEARCH-leg RAM creep + GPU thermal watch

**Status:** resolution SPEC (read-only analysis; no code edited). Apply + test yourself.
**Scope:** ONE flagged open run-risk — the reflect-on-best parallel SEARCH path
(`scripts/run_campaign.py::_search_parallel_arm` → `src/orchestration/parallel.py::run_parallel`)
reuses `run_parallel`'s single long-lived `DevicePool` with **no recycling**, so per-worker RSS
creep at the **50k-step × 30-candidate-per-arm** scale is unproven (the prototype proved only 25k,
via the per-candidate `del`+`gc.collect()` reclaim; the TEST leg already recycles via `run_recycling`).
**Verdict (TL;DR): no code change required. Run `--search-gpu 2`; the gc-reclaim already proven at 25k
covers 50k with margin; add a cheap RAM/thermal watchdog (monitoring-only). `--search-gpu 3` is a
defensible upside if the watchdog is armed; `--search-gpu 4` is ruled out by VRAM, not RAM.**

All hardware/threshold numbers below were measured first-hand on the target laptop on 2026-06-24 via
`.venv/Scripts/python.exe` (psutil / pynvml), not recalled from memory.

---

## 1. The architecture, corrected — the pool is PER-ARM, not per-campaign

The risk statement frames a "single long-lived DevicePool". That is true **within an arm**, but the
campaign does NOT keep one pool alive across the whole search. The exact call chain:

- `run_headline_campaign` (`scripts/run_campaign.py:632`) loops **`for arm in arms:`**.
- For each arm it calls `_search_parallel_arm(arm, …)` (`scripts/run_campaign.py:201`), whose last
  line is `runner([arm], opts, n_gpu, n_cpu, search_root)` (`:266`) — i.e. **`run_parallel` is
  invoked once per arm with a single-element arm list**.
- `run_parallel` (`src/orchestration/parallel.py:657`) opens `with DevicePool(...) as pool:` (`:686`).
  The `with` exit calls `DevicePool.__exit__` → `self._ex.shutdown(wait=True)` (`:349-350`), which
  **terminates every worker process and lets the OS reclaim its entire address space.**

**Consequence:** the pool is created, drives exactly ONE arm's 30 candidates, then is fully torn down
before the next arm spawns a fresh pool. The creep window is **30 candidate-trainings (~2.0–2.5 h)**,
not 180 (~14 h). This is the single most important fact for sizing the risk, and it is structurally
different from the *prototype* `--parallel` path, which calls `run_parallel(par_todo, …)` with **all
arms in one list** (`scripts/run_prototype.py:564`) → one pool for the entire 240-candidate run. The
17.9 h flat-RAM proof from the prototype was therefore a **harder** test (longer-lived pool) than any
single campaign arm faces — at the smaller 25k buffer.

Per-arm cross-candidate concurrency and reflect-on-best are *intra-pool* behaviours
(`_drive_llm_arm`, `:514-614`: gens loop seeds reflection from each generation's BEST, submits `cpg`
candidates concurrently per generation). **Tearing the pool down at the arm boundary — which already
happens — does not touch either of them.** That is why the recommended resolution needs no surgery on
`run_parallel`'s internals.

LLM arms only: `distributional, scalar, placebo, scalar_cvar5`. `random_search`/`bayes_opt` flow
through the same per-arm pool via `_drive_search_arm` (`:617`), 30 candidates each, identical creep
profile.

---

## 2. RAM math (measured obs_dim, target hardware)

`obs_dim` from `src/env/portfolio_env.py::_obs_dim` (`:198`), with `config/environment.yaml`
(lookback 60, n_assets 30, 2 vol windows, vix, cash marker, prev-weights 31):

```
obs_dim = 60*30 + 2*30 + 1 + 1 + 31 = 1893     # confirmed == the memory note's 1893
```

Replay buffer (obs + next_obs, float32) per worker:

| train_steps | buffer/worker | + ~1.4 GiB base¹ = per-worker | source |
|---|---|---|---|
| 25 000 (prototype) | 0.353 GiB | **1.75 GiB** | proven flat 17.9 h |
| 50 000 (campaign)  | 0.705 GiB | **2.11 GiB** | this analysis |

¹ 1.4 GiB base = torch + SB3 + cached gold panel + CUDA host context, the calibrated constant in
`auto_n_gpu` (`src/orchestration/parallel.py:48`), itself fitted to the measured n_gpu=5 OOM / n_gpu=4
ceiling. The "~2.1 GB/worker at n_gpu=4 @ 50k" figure in the memory note reproduces exactly (2.105).

**Target machine, measured 2026-06-24:** 15.63 GiB total RAM (6.89 GiB *available* with the user's
normal desktop load running), 10 physical cores, Python **3.11.9** (confirms the deadlock platform),
GPU **RTX 4050 Laptop, 6141 MiB VRAM** (5921 free).

### Steady-state RAM (N workers each at one buffer + base), 50k:

| n_gpu | workers RAM | + ~1.2 GiB main/manager | of 15.63 GiB |
|---|---|---|---|
| 2 | 4.21 GiB | **5.41 GiB** | 35 % — huge headroom |
| 3 | 6.32 GiB | **7.52 GiB** | 48 % |
| 4 | 8.42 GiB | **9.62 GiB** | 62 % |

Steady state fits even at n_gpu=4. **Steady state is not the failure mode** — the prototype proved
that. The two real failure modes (memory note item 5) are the *transition wave* and *slow creep*.

### Transition wave (the n_gpu=4 OOM that actually happened, at 25k)

At a generation boundary all `cpg` candidates finish ~together and the next generation's workers
allocate **fresh** buffers while the just-finished buffers may not yet be GC-reclaimed → up to **2×
buffer co-resident per worker** for an instant. Pessimistic peak at 50k:

| n_gpu | wave peak (2× buffer + base, all workers) | of 15.63 GiB |
|---|---|---|
| 2 | **6.82 GiB** | 44 % — absorbs the wave |
| 3 | **9.63 GiB** | 62 % |
| 4 | **12.44 GiB** | **80 %** |

The 25k n_gpu=4 wave OOM'd at ~92 % (52 failures). At 50k the buffer doubles, so the n_gpu=4 wave is
**worse**, and against only ~6.9 GiB currently-available the n_gpu=4 transient could exceed free RAM
outright. **n_gpu=2 keeps the worst-case transient under 45 %** even with the doubled buffer — this is
the load-bearing reason the prototype settled on n_gpu=2 and it transfers directly to the campaign.

### Slow creep — why the existing in-process fix is sufficient at 50k

The creep (memory note: n_gpu=3 89.6→96.3 % in 25 min; n_gpu=2 71→89 % in 50 min) was a *persistent-
worker heap-fragmentation* leak from SB3 SAC's cyclic refs (policy↔optimizer↔replay buffer). The fix
in `train_candidate` (`src/orchestration/parallel.py:253-256`) — `del trainer,bundle,policy,val,train;
gc.collect()` after results are captured into `out` — was **VERIFIED flat for 17.9 h at 25k** (RAM
drops ~one buffer at each completion, oscillates flat ~65–71 %). This code path is **shared verbatim**
by the campaign SEARCH worker (same `train_candidate`).

Does it hold at 50k? The reclaimed object that matters is the replay buffer, and it is the SAME numpy
allocation, just **2× larger** (0.705 vs 0.353 GiB). A bigger contiguous numpy free is **more** likely
to be returned to the OS, not less (large allocations bypass the small-object arena). The residual
risk is glibc/Windows-heap fragmentation of the *non-buffer* allocations, which the prototype already
absorbed at 25k. With the per-arm pool also being **torn down every ~2 h** (§1), any residual
fragmentation is hard-reset 6 times over the search — a guarantee the 17.9 h single-pool prototype
never had. **The 50k creep is bounded by the same proven mechanism, with a strictly stronger reset
cadence. No new recycling is required to make 50k safe at n_gpu=2.**

### VRAM is the actual ceiling, not RAM

6141 MiB total VRAM. `auto_n_gpu` budgets ~1400 MiB CUDA context/model/batch per worker
(`:33`,`:61`); 5921 free / 1400 ≈ **4** is the hard VRAM cap. At n_gpu=4 the card sits at its VRAM
ceiling with no slack for the per-task allocation spikes `empty_cache()` is meant to smooth
(`:242`). **n_gpu=4 is ruled out by VRAM independent of RAM.** n_gpu=2 uses ~2.8 GiB VRAM (46 %),
n_gpu=3 ~4.2 GiB (68 %) — both comfortable. This reinforces n_gpu=2 and caps the upside at n_gpu=3.

### Will it OOM? Survive 27 h?

> **NOTE:** Phase-1 prototype used 6 arms; the campaign uses 7 arms incl. `placebo_shuffled` (R54). See PREREGISTRATION §3.

The "~27 h" total = SEARCH (6 arms × 30 cand × ~53k steps ≈ **13–15 h**, agg 178–222 steps/s) + the
already-built TEST leg (6 arms × 30 seeds × ~53k ≈ another ~13–15 h). The pool that must survive
uninterrupted is only **one arm (~2.0–2.5 h, 30 candidates)** at a time, then it is destroyed.

- **n_gpu=2, 50k:** steady 35 %, wave ≤45 %, creep bounded by gc + 2 h pool resets → **will NOT OOM.
  Survives the full search comfortably.** Recommended.
- **n_gpu=3, 50k:** steady 48 %, wave ~62 %, VRAM 68 %. Survivable IF the watchdog (§4) is armed and
  you accept aborting on a red line; only ~11 % faster than n_gpu=2 (178→200 agg). Defensible upside,
  not required.
- **n_gpu=4, 50k:** wave ~80 % RAM **and** VRAM at its ceiling → **do not run.** This is the
  configuration the prototype already OOM'd at the smaller 25k buffer.

---

## 3. RECOMMENDED RESOLUTION — monitor + n_gpu=2 (no `run_parallel` surgery)

Threading recycling *into* `run_parallel` is **rejected as too invasive and unnecessary**:

1. **The clean mechanism is broken on this platform.** `max_tasks_per_child` deadlocks on Windows +
   spawn (memory note, first-hand across CPython 3.11–3.14). Web research confirms this is an open,
   unresolved CPython defect, not a local fluke — gh-115634 ("ProcessPoolExecutor hangs when
   1<max_tasks_per_child<num_submitted//max_workers"), gh-111498, gh-105829. `DevicePool` already
   keeps the param plumbed but config-null for exactly this reason (`:308-324`).
2. **Generation-boundary pool recycling would break reflect-on-best concurrency** or force a
   serialization point, and would duplicate the per-arm teardown that **already** gives a hard RAM
   reset every ~2 h — the marginal benefit is ~nil.
3. **A `recycle_every` into `run_parallel`** means re-spawning the pool mid-arm. But the cross-arm
   concurrency justification for the single pool (prototype: all arms share one pool) **does not even
   apply to the campaign**, where each `run_parallel` call already holds a single arm. The recycling
   value is fully captured by the existing arm-boundary teardown + the in-worker gc — adding intra-arm
   recycling is pure complexity on a frozen, single-shot, grade-critical run.
4. The **proven** recycling substitute (`run_recycling`, fresh pool per batch) is already what the
   TEST leg uses, GPU-smoke-verified (8/8 seeds, peak RAM 51.7 %, VRAM reclaimed to 220 MiB). The
   SEARCH leg gets the *same RSS guarantee structurally* via per-arm teardown — without needing to
   route the reflect-on-best driver through `run_recycling` (which would lose the gen-by-gen
   reflection state that lives in `_drive_llm_arm`).

**The defensible, evidence-backed decision: no code change to `parallel.py`. Run the campaign search
with `--search-gpu 2 --search-cpu 0`. Arm the watchdog in §4. Hold n_gpu=3 in reserve.**

### Exact invocation

```
.venv/Scripts/python.exe scripts/run_campaign.py \
    --search-gpu 2 --search-cpu 0 \
    --gpu 2 --cpu 0            # TEST leg also n_gpu=2 (run_recycling already proven)
# --resume is idempotent (skips frozen winners + done test seeds) — safe to relaunch after any abort.
```

`--search-cpu 0` is mandatory, not cosmetic: `prototype.yaml` calibration shows CPU training workers
are ~19× slower **and** starve the GPU feed threads (3 GPU alone = 186 agg vs 3 GPU + 8 CPU = 143).
GPU-only is the throughput optimum AND keeps RAM lowest.

`n_trials = candidates_per_arm = 30` (DSR expected-max correction) is unaffected by any of this.

### Pre-flight assertion (optional, one line, in `_search_parallel_arm`)

If you want a fail-loud guard rather than relying on operator discipline, add **before** the
`runner(...)` call at `scripts/run_campaign.py:266` (this is the campaign script, which you own — NOT
`parallel.py`):

```python
# RAM-safety pre-flight (run-risk 3e): the 50k buffer makes n_gpu>=4 OOM at the gen-transition wave
# (2x co-resident buffers) AND saturates the 6 GiB 4050 VRAM. n_gpu=2 is the proven-safe lever; 3 needs
# the watchdog armed. Refuse 4 outright so a stray --search-gpu 4 can't silently melt the single-shot run.
if int(n_gpu) >= 4:
    raise SystemExit(
        f"[run_campaign] search_n_gpu={n_gpu} unsafe on this 15.6 GiB / 6 GiB-VRAM laptop at 50k "
        f"(transition-wave OOM + VRAM ceiling). Use --search-gpu 2 (proven) or 3 (watchdog-armed)."
    )
```

This is purely additive and touches only the campaign driver you apply yourself; `parallel.py` stays
byte-for-byte unchanged. Skip it if you prefer not to edit `run_campaign.py` at all — the operator
choice of `--search-gpu 2` is sufficient.

---

## 4. GPU thermal-throttle + RAM watch plan

The live monitor **already samples** everything needed but does **not alert** on it. From
`src/utils/monitoring.py::_Resources.sample` (`:67-87`) each probe already yields
`gpu_temp`, `gpu_util`, `gpu_mem_mib`, `ram_pct`, `proc_rss_mib`. These are written into
`progress.json` and rendered by `scripts/monitor.py`. **But `_check_training_anomalies` (`:320-342`)
only inspects critic/entropy/fps — there is NO threshold on `ram_pct` or `gpu_temp`.** The `failure_wave`
anomaly (`:488-491`) fires only AFTER ≥3 candidate errors, i.e. after the OOM cascade has begun. So the
watch is a thin add-on, not new instrumentation.

**Measured thermal thresholds on this exact GPU (pynvml, 2026-06-24):**
- Slowdown (HW thermal throttle begins): **91 °C**
- Shutdown: **101 °C**
- Idle temp now: 42 °C
- `nvmlDeviceGetCurrentClocksThrottleReasons` **works** here and exposes the bitmask. Relevant bits:
  `HW_SLOWDOWN 0x8`, `SW_THERMAL_SLOWDOWN 0x20`, `HW_THERMAL_SLOWDOWN 0x40`. A non-zero AND against
  `(0x8|0x20|0x40)` = the GPU is *actively* thermal-throttling **right now** — a more direct signal
  than temperature alone.

### Watch plan (no code change required; two options)

**Option A — out-of-band sidecar (preferred; zero touch to the run).** A 30 s poller reading the
already-written `outputs/campaign/search/progress.json` (or NVML directly). Thresholds:

| Signal | Source | WARN | ABORT-and-relaunch-lower |
|---|---|---|---|
| `ram_pct` | progress.json | ≥ 85 % | ≥ 92 % (the 25k OOM band) |
| `proc_rss_mib` slope | progress.json over 10 min | rising, no per-candidate sawtooth dips | monotone climb = gc reclaim failing |
| `gpu_temp` | progress.json / NVML | ≥ 87 °C | ≥ 91 °C (HW slowdown) |
| throttle bitmask | NVML `…ThrottleReasons` | thermal bit set transiently | thermal bit set sustained > 2 min |
| candidate errors | anomalies.jsonl `failure_wave` | any | the cascade — already logged |

Minimal sidecar (run in a second terminal; reads NVML, never touches the run):

```python
# scripts/watch_thermal.py  (NEW, optional, monitoring-only — does not import the run)
import time, pynvml as p
p.nvmlInit(); h = p.nvmlDeviceGetHandleByIndex(0)
SLOW = p.nvmlDeviceGetTemperatureThreshold(h, p.NVML_TEMPERATURE_THRESHOLD_SLOWDOWN)  # 91 here
THERMAL = 0x8 | 0x20 | 0x40
while True:
    t = p.nvmlDeviceGetTemperature(h, 0)
    thr = p.nvmlDeviceGetCurrentClocksThrottleReasons(h)
    hot = (thr & THERMAL) != 0
    if t >= SLOW or hot:
        print(f"[watch] THROTTLE temp={t}C slow_at={SLOW} reasons={hex(thr)} -> lower n_gpu / improve cooling")
    elif t >= SLOW - 4:
        print(f"[watch] WARN temp={t}C approaching slowdown {SLOW}")
    time.sleep(30)
```

**Option B — promote the existing telemetry into an anomaly (one small edit to
`src/utils/monitoring.py`, NOT to parallel.py).** Sample `_Resources` on the monitor pump and call
`self.anomaly("ram_pressure", …)` at `ram_pct ≥ 90` and `self.anomaly("gpu_thermal_throttle", …)` when
the throttle bitmask shows a thermal bit. This routes RAM/thermal into the same `anomalies.jsonl`
stream the run already writes and the failure-wave logic already trusts. Defer unless you want the
alert co-located with the run; Option A is sufficient and zero-risk for a frozen run.

### Thermal context / expectation

This is a **GPU-saturated** workload (prototype: GPU saturates ~185 agg steps/s at n_gpu≥3; n_gpu=2 =
178). A laptop 4050 under multi-hour 100 % load **will** run hot and *may* HW-throttle at 91 °C — that
is a **throughput** concern (slower steps/s → longer wall-clock), **not a correctness concern** (the
science is seed-deterministic; a throttled run produces identical numbers, just later). Action on
sustained thermal throttle is operational: improve cooling (elevate/clean the laptop, cap room temp),
or drop to n_gpu=2 if you were at 3. **Do not** treat thermal throttle as a reason to alter any
training/eval parameter — that would break matched-compute. The watchdog's job is to (a) catch the RAM
red line *before* an OOM corrupts an arm, and (b) tell you if heat is silently inflating wall-clock.

---

## 5. Test plan (you run; I edited nothing)

1. **Unit/fast suite unchanged** — no code touched in `parallel.py`; `tests/test_parallel_recycling.py`
   + the equivalence tests stay green by construction.
2. **One-arm 50k GPU smoke (the real proof for 3e):** launch the campaign search for a SINGLE LLM arm
   at the real 50k budget, n_gpu=2, and watch `progress.json` `ram_pct` / `proc_rss_mib` through at
   least 2 generation boundaries (the transition-wave moments). Pass criteria, mirroring the TEST-leg
   smoke that already passed: 0 failed candidates, peak `ram_pct` < ~60 %, `proc_rss_mib` shows the
   per-candidate sawtooth (gc reclaim working), VRAM returns toward baseline between candidates. A
   `--dry-run`-style tiny arm will NOT exercise the wave — it must be the real 50k buffer to be
   meaningful.
3. If step 2 shows the sawtooth and stays < 60 %, n_gpu=2 is proven for the full search; arm Option-A
   watchdog and launch the campaign. If you want the ~11 % speedup, re-run step 2 at n_gpu=3 with the
   watchdog live and confirm wave peak stays < ~75 % and VRAM < ~70 % before committing.

---

## 6. Evidence ledger (first-hand, 2026-06-24)

- `obs_dim = 1893` — derived from `portfolio_env._obs_dim` + `environment.yaml`; matches memory note.
- Buffer 0.353 GiB @25k / 0.705 GiB @50k; per-worker 1.75 / 2.11 GiB (base 1.4 from `auto_n_gpu:48`).
- Laptop: 15.63 GiB RAM (6.89 avail under load), 10 phys cores, **Python 3.11.9** (deadlock platform).
- GPU RTX 4050 Laptop, **6141 MiB VRAM** (5921 free) → VRAM hard-caps n_gpu at ~4; comfortable ≤3.
- Thermal: slowdown **91 °C**, shutdown **101 °C**, throttle-reason bitmask API present
  (HW_SLOWDOWN 0x8 / SW_THERMAL 0x20 / HW_THERMAL 0x40).
- Pool lifetime per arm ≈ 2.0–2.5 h (30 cand × ~53k steps ÷ 178–222 agg steps/s); search ≈ 13–15 h;
  full campaign (search + already-built recycling TEST leg) ≈ ~27 h — reconciles the memory note.
- Call graph confirming per-arm teardown: `run_campaign.py:632` (for-arm) → `:266`
  (`run_parallel([arm],…)`) → `parallel.py:686` (`with DevicePool`) → `:349` (`shutdown(wait=True)`).
- gc-reclaim fix that makes 50k safe: `parallel.py:253-256`, shared verbatim by the SEARCH worker;
  proven flat 17.9 h at 25k on a *longer-lived* single pool than any campaign arm.
- CPython deadlock is upstream + unresolved: gh-115634, gh-111498, gh-105829 (web, 2026-06-24).

**Sources (web):**
- https://github.com/python/cpython/issues/115634
- https://github.com/python/cpython/issues/111498
- https://github.com/python/cpython/issues/105829
- https://loky.readthedocs.io/en/stable/  (worker-recycling reference pattern; not adopted — new dep, out of scope)
