# Campaign Hardening Plan — risk register + resilience architecture (2026-06-30)

De-risking the ~2-week laptop campaign (RTX 4050, 24/7). Built from a 5-subsystem first-hand scout
(orchestration/resume · LLM cache · verify/freeze/monitor · storage · parallelization). Every system here is
**result-neutral** (byte-identical replay — anything else corrupts the science) and **space-bounded** (the whole
campaign is ~50–200 MB; models/buffers are never persisted, so the cache is a *replay index*, not compression).

## What is ALREADY robust (do not rebuild)
Atomic writes (temp+fsync+`os.replace`, `results.py:137`); idempotent arm/candidate/seed resume; frozen-winner
load-not-re-search (`run_campaign.py:1110`); mechanical freeze-hash enforcement that refuses to launch on drift
(`run_campaign.py:1535`); full determinism pinning (seeds, cuBLAS workspace, cudnn-deterministic, TF32-frozen,
`seeding.py`); in-process anomaly monitor (NaN/critic-explosion/entropy/FPS/thermal/RAM, `monitoring.py:333`).

## Risk register (ranked by exposure over 2 weeks)
| # | Risk | Likelihood | Impact | Existing guard | Fix (build) |
|---|---|---|---|---|---|
| R1 | Mid-search crash re-bills Opus + picks a *different* winner | High | $ + repro break | resume = test-only | **#1 search-replay cache — DONE** |
| R2 | API retry-exhaustion crashes the whole arm | Med | lost arm | 6× backoff then reraise | #2 graceful skip+archive |
| R3 | No pre-flight before a 2-week commit | Med | wasted days | Phase-0 (historical) | #3 pre-flight gauntlet |
| R4 | Anomalies detected but **not acted on** (95 °C, 96% RAM, divergence) | High | throttle/OOM | monitor logs only | #4 auto-guardian controller |
| R5 | Mid-candidate crash loses in-flight steps | Med | ~20 min (post-#1) | seed re-run | obviated by #1 |
| R6 | Manual `--resume` (unattended run stalls) | High | lost wall-clock | none | #5 auto-restart supervisor |
| R7 | n_gpu=3 RAM creep → OOM | Med | crash | `run_recycling` | pin recycling + pilot-verify |
| R8 | Buffer-cap second site (`parallel.py:277`) unwired | Med | OOM when B* rises | one site capped | #6 wire the cap |
| R9 | Power loss / Windows auto-reboot | Med | crash (recoverable) | atomic writes | #5 supervisor + disable auto-reboot |
| R10 | Thermal throttle over weeks | High | slower | telemetry | #4 back-off + clock pin |
| R11 | Determinism drift (torch/driver update mid-run) | Low | repro break | deterministic flags | #3 env-hash + freeze venv |
| R13 | Came-out-with-nothing (σ high / all-diverged) | Low-Med | the run | the 2 pilots | pilots gate the run |
| R14 | Disk exhaustion | **Negligible** | — | ~50–200 MB total | none needed |
| R15 | Silent freeze-drift mid-run | Low | invalid results | freeze at start | #4 re-assert per arm |

## Architecture (three systems)
1. **Cache = content-addressable replay index** over the existing tiny archive. Before any paid/expensive op,
   hash `(arm, generation, candidate-idx, rendered prompt)`; on a hit replay the archived `reward_source`
   byte-identically. Zero extra space (archive already exists). **Built for the search leg.**
2. **Resume = write-ahead intent + auto-restart supervisor.** A wrapper relaunches `--resume` on non-zero exit
   (bounded retries) after a resume-verification (freeze hash + data hash + 1-unit determinism spot-check).
3. **Verification = pre-flight gauntlet + in-run auto-guardian + post-run audit.** Pre-flight (disk/API/data-hash/
   freeze/VRAM/thermal/determinism-smoke) *before* the commit; guardian *acts* on monitor anomalies (cool at
   90 °C, abort+archive a diverged candidate, throttle n_gpu on RAM, re-assert freeze each arm); post-run replay
   audit (byte-identity sample, N-per-arm, hash-chain).

## Build order (each test-then-commit, result-neutral)
**ALL DONE 2026-06-30 → 07-01 (32+ tests green, ruff clean). The headline serial path is fully covered.**
- **#1 search-replay cache — DONE** (`src/llm/loop.py`; replays successes via `load_run` + failures via a
  `{run_prefix}-{arm}.failures.jsonl` ledger; resume-gated, fresh run byte-unchanged; +3 tests). **WIRED** into the
  serial search cfg (`run_prototype.run_arm` → `loop_cfg["resume"]`).
- **#2 graceful API-degradation — DONE** (`loop.py`: an LLM-call failure logs+skips, not cached → resume
  re-attempts; never crashes the arm; +1 test).
- **#3 pre-flight gauntlet — DONE** (`scripts/preflight.py`, read-only GO/NO-GO; +8 tests; freeze fn = `canonical_hash`).
- **#4 auto-guardian — DONE** (`src/utils/guardian.py` hysteresis thermal governor + RAM throttle; **wired into the
  SB3 callback** via `trainer._make_governor` + `monitoring.make_training_callback(governor=…)`, config-gated
  `thermal_guardian`, result-neutral; +7 tests).
- **#5 auto-restart supervisor — DONE** (`scripts/supervisor.py`, relaunch `--resume` w/ backoff + pre-flight; +6 tests).
- **#6 buffer-cap second site — DONE** (`parallel.py` honors a spec `buffer_size` cap, never exceeds `train_steps`).
- **Remaining completeness (deferred, non-blocking):** parallel-path search cache (`parallel.py::_drive_llm_arm`) —
  the headline run is serial, which #1 + the guardian already cover.

## Parallelization verdict (the "are we maxed" question)
n_gpu=4 is **physically impossible** on 6 GB (measured OOM cascade; refused at `run_campaign.py:1547`). n_gpu=2 is
proven-flat (~178 steps/s); n_gpu=3 is faster but RAM-creeps without recycling. Env is GPU-forward-pass-bound (pure
NumPy, not CPU). **Every remaining speed lever changes the frozen experiment** (batch/UTD/precision) EXCEPT
`torch.compile`, which is **not wired** and carries a determinism risk → pilot-test "compile ON: faster AND still
byte-identical?" before adopting. We are at the practical ceiling for a determinism-preserving frozen run; n_gpu
(2 vs 3) and compile are **pilot measurements**, not missing optimizations.
