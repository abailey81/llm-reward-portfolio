# CAMPAIGN_SPEC — long-run robustness for the ~27 h headline campaign

**Audience:** the operator (you) applying changes to `scripts/run_campaign.py`,
`src/orchestration/{parallel.py,test_leg.py}`, `src/utils/monitoring.py`, `scripts/monitor.py`.
**Author:** SRE audit, 2026-06-24. **Mode:** read-only audit → apply-ready spec. I did **not** edit code.

> **NOTE:** Phase-1 prototype used 6 arms; the campaign uses 7 arms incl. `placebo_shuffled` (R54). See PREREGISTRATION §3.
> **NOTE (2026-07-02, Split C / univ5 — ADR-044/051, R73):** the sealed leg is now **2020–2026H1 on univ5**
> (train 2005–2016 / val 2017–2019); the "sealed 2018-2025 leg" in the quoted code comments below reflects
> `run_campaign.py` as read on 2026-06-24 and is kept verbatim as audit evidence. Also since applied:
> `--gpu`/`--search-gpu` ≥ 4 are now **refused by the CLI** (the §C/§D OOM concern is enforced at launch).

**Run under audit:** 6 arms × 30 candidates (1 search seed) → SELECT/FREEZE → 6 winners × 30 test seeds × 50k SAC steps.
Real **Claude Opus 4.8** reward-author (Pass B, `ANTHROPIC_API_KEY`). Target host = **maxed RTX-4050-Laptop (6141 MiB VRAM) / 15.6 GB RAM**,
`n_gpu=4`, ~27 h (user chose laptop over rented 4090). Calibration anchors (verified): prototype ran **17.9 h at n_gpu=2** for
the *search legs only* at 25k steps; campaign **doubles steps (25k→50k → 2× replay buffer ≈ 0.76 GB/worker)** and **adds the 180-run test leg**.
`m ≈ 18 min / 50k-run` on a 4050 (`docs/COMPUTE_AND_TRAINING_TIME.md`). 360 core runs ÷ ~3.5 effective concurrency × 18 min ≈ **30 h** — an interruption over that span is **near-certain**.

---

## 0. The single most important finding (read first)

> **There is ZERO signal/atexit/graceful-shutdown handling anywhere in the run path, and SEARCH cannot resume mid-arm.**
> A Ctrl-C, OS sleep, thermal trip, or crash during the SEARCH stage of an arm **silently discards every Opus call already paid for in that arm and re-issues all 30 on the next `--resume`.** The only `KeyboardInterrupt` handler in the repo is in `scripts/monitor.py` (the *dashboard*, not the run). `auto_shutdown_on_complete` is a harmless no-op print (verified — it does not power off, so no data-loss risk there).

Confirmed by:
- `grep signal|SIGINT|SIGTERM|atexit|KeyboardInterrupt` over `scripts/` + `src/` → only `monitor.py:168` (dashboard) and `run_prototype.py:653` `os._exit(0)` (a *success-path* exit-code workaround, not a handler).
- `src/llm/loop.py` has **no** `load_run`/`exists`/skip/resume logic — `run_loop` always iterates `range(generations)` from gen 0 and calls `llm.complete(...)` for every candidate (`loop.py:323,353`).
- `src/orchestration/parallel.py::_drive_llm_arm` (the `--search-gpu` path) likewise has **no** per-candidate resume — `run_parallel` re-runs the whole arm.
- `scripts/run_campaign.py:641-651`: `--resume` for SEARCH is **all-or-nothing at the arm level** — it loads a *frozen winner* if one exists, else re-runs the **entire** search (all 30 candidates → all 30 paid Opus calls).

**Blast radius of one mid-search interruption:** up to **30 wasted Opus 4.8 calls** for the in-flight arm (the prototype's analogue was ~$3.17 for 160 Sonnet calls; Opus is ≫ pricier per token), plus the GPU-hours already spent. Over a 27 h run with ≥1 expected interruption, this is the dominant operational risk to **both budget and timeline**.

---

## 1. PRIORITIZED RISK REGISTER

Likelihood is over the **full ~27 h single-shot run**. Blast radius = what is lost / corrupted if it fires.

| # | Failure mode | Likelihood (27 h) | Blast radius | Fix (→ §) |
|---|---|---|---|---|
| **R1** | **Interruption during SEARCH (Ctrl-C / sleep / thermal / crash) → all paid Opus calls in the in-flight arm re-burned on resume.** No candidate-level resume; `run_loop` re-issues every `llm.complete`. | **High** (≥1 interruption near-certain) | **Up to 30 Opus 4.8 calls re-billed per affected arm + GPU-hours; can recur every restart.** Dominant $ + time risk. | **§A** (SIGINT handler) + **§B** (candidate-level SEARCH resume) |
| **R2** | **No SIGINT/atexit handler → Ctrl-C kills the process pool mid-`learn()`; partial/zero in-flight candidate flush; spawn workers may orphan / leave a half-written `record.json`.** | **High** | In-flight candidate(s) lost; possible **truncated `record.json`** that fails `load_run` schema check on resume → loud crash (or silent skip of a real result). | **§A** + **§F** (atomic record write) |
| **R3** | **`n_gpu=4` is the MEASURED OOM setting for SEARCH** (transition-wave: 4 simultaneous 0.76 GB buffer allocs at ~92% RAM → MemoryError cascade; prototype lost 52 candidates at n_gpu=4). The `--gpu 4` smoke that survived was the **TEST** leg *with recycling*; SEARCH (`run_parallel`) uses a **single persistent pool, no recycling**. | **High if `--search-gpu 4`** | A failure *wave* — dozens of candidates fail their gate as `MemoryError`, arm reports few/zero accepted, winner is selected from a depleted pool (science-corrupting, not just slow). | **§C** (OOM-wave adaptive n_gpu back-off) + **§D** (SEARCH must use recycling) |
| **R4** | **GPU temperature is sampled but never thresholded.** `_Resources.sample()` reads `gpu_temp` and writes it to `progress.json`, but there is **no anomaly** on it. A laptop 4050 under 27 h sustained load **will** thermally throttle (or the OS will sleep). No telemetry-driven warning, no pause. | **High** (sustained laptop load) | Silent throughput collapse (throttle), or a sleep that suspends CUDA → on wake, CUDA context is often dead → cascade of worker failures. | **§E** (GPU-temp anomaly + thermal-pause hook) |
| **R5** | **Resume re-derives the winner only if a *frozen* record exists; a crash AFTER search completes but BEFORE freeze re-runs the whole search.** SELECT/FREEZE are not checkpointed independently of the per-candidate archive. | Medium | Re-burns the full arm's Opus budget even though every candidate is already on disk. | **§B** (load winner from the existing candidate archive, not only from `frozen/`) |
| **R6** | **`run_recycling` swallows a RAISING worker but the campaign never aborts on a total failure wave.** A bad config / dead CUDA context makes *every* seed return `{"ok": False}`; the driver prints a WARNING and **continues to the next arm**, writing 0 records. `matched_budget_ok` is computed but **not acted on** at the campaign level. | Medium | A whole arm (or the whole run) silently produces no usable test records; discovered only at analysis time, hours later. | **§G** (fail-loud on a campaign-level failure wave) |
| **R7** | **Monolithic `.learn(total_timesteps=50k)` per candidate — no mid-training checkpoint.** A crash 49k steps into a 50k run loses the whole candidate. Unavoidable per-candidate, but the *granularity* of loss is one full ~18 min run. | Medium | One candidate/seed re-trained from scratch on resume (acceptable — *if* §B/test-leg resume skip it). | Accept; mitigated by §B + existing `done_ids` |
| **R8** | **No disk-space / inode guard.** Each candidate writes `record.json` + `reward.py` + `env.json` (full pip-freeze/nvidia-smi capture, cached per-seed but still 360+ dirs). A full disk mid-run → `write_run` raises → arm crashes; worse, a *partial* write corrupts a record. | Low-Med | Crash mid-arm (→ R1), or a corrupt record that fails `load_run` on resume. | **§F** (atomic write) + **§H** (preflight disk check) |
| **R9** | **`anomaly()` writes are advisory only — critic-loss divergence in the prototype did NOT halt the run** (6 diverged runs, ~2.5%; the 64 `anomalies.jsonl` *lines* are a line-count, not a run-count)**.** Correct by design (PopArt-absent is a known cause), but means the monitor **cannot** stop a genuinely diverging run. | Low (by design) | Wasted compute on a diverged arm; not data loss. | Documented; no change (see §J note) |
| **R10** | **Long-run RAM creep on the SEARCH persistent pool despite the gc fix** — the gc fix made it *flat* at n_gpu=2/25k; at n_gpu=3-4/**50k** (2× buffer) the transition-wave peak is higher and the fix is necessary-but-maybe-not-sufficient. | Medium | Gradual RAM climb → OOM hours in. | **§C** (back-off) + **§D** (recycling caps it hard) |
| **R11** | **Opus rate-limit / 5xx storm mid-search.** `tenacity` retries 6× with exp backoff (max 30 s) on transient errors (`client.py:261`). A sustained 429/overloaded wave exhausts retries → `SandboxError`? No — it **raises** out of `llm.complete` → **crashes the arm** (the loop only catches `SandboxError`, not API errors). | Medium | Arm crash mid-search → R1 re-burn. | **§B** (so the crash is cheap to resume) + **§I** (note: widen catch — optional) |
| **R12** | **Wall-clock truncation / overnight host sleep.** Windows default sleep/hibernate will suspend the run; on resume CUDA context is usually invalid. | High (if power settings untouched) | Whole run suspended; CUDA-dead cascade on wake. | **§K** (operational runbook: disable sleep) + §A/§B make the restart cheap |

---

## 2. CODE-CHANGE SPEC (apply-ready, file:line, before/after)

> All line numbers are against the files as read on 2026-06-24. Apply in order A → B → C → D → E → F → G; the rest are operational (§H, §K) or optional (§I, §J).
> **Design constraint honored throughout:** *science-neutral* — none of these change the numerics, the matched budget, the once-only test touch, the frozen-winner identity, or the per-seed seeding. They change only *when work is flushed* and *whether already-paid work is re-done*.

---

### §A — SIGINT / graceful-shutdown handler (R1, R2, R11, R12)

**Goal:** Ctrl-C (or SIGTERM) flushes in-flight work, shuts the process pool down cleanly, and exits **non-destructively** — never leaving a half-written record, never re-billing on the next run. Because SEARCH's heavy work happens inside spawned pool workers and a monolithic `.learn()`, the handler's job is to (1) stop *scheduling new* candidates, (2) let in-flight futures drain (bounded), (3) shut pools with `wait=True`, (4) exit with a clear code so the operator knows to `--resume`.

**A.1 — Install a cooperative shutdown flag in `scripts/run_campaign.py`.**

Add a module-level event + handler near the imports (after line 63, `import numpy as np`):

```python
# --- BEFORE (run_campaign.py, ~line 55-64) ---
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np

from src.utils.config import cfg_get
```

```python
# --- AFTER ---
from __future__ import annotations

import argparse
import json
import signal
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np

from src.utils.config import cfg_get

# --------------------------------------------------------------------------- #
# Graceful-shutdown flag. A long campaign WILL be interrupted (Ctrl-C, sleep,  #
# thermal, crash). On the FIRST SIGINT/SIGTERM we set this event so the arm    #
# loop stops scheduling NEW arms/candidates and drains in-flight work; on a    #
# SECOND signal we let the default handler hard-kill. Nothing here deletes or  #
# overwrites archived work — resume (--resume) picks up from the on-disk       #
# records, so an interrupt is always non-destructive.                          #
# --------------------------------------------------------------------------- #
SHUTDOWN = threading.Event()


def _install_signal_handlers() -> None:
    def _handler(signum: int, _frame: Any) -> None:
        if SHUTDOWN.is_set():
            # Second Ctrl-C: restore default and re-raise so the user can force-kill.
            signal.signal(signum, signal.SIG_DFL)
            print("\n[run_campaign] second interrupt — hard exit (work already on disk; use --resume).",
                  file=sys.stderr, flush=True)
            raise KeyboardInterrupt
        SHUTDOWN.set()
        print(f"\n[run_campaign] signal {signum} received — finishing in-flight work, then stopping. "
              f"Press Ctrl-C again to force-quit. Re-launch with --resume to continue.",
              file=sys.stderr, flush=True)

    for _sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(_sig, _handler)
        except (ValueError, OSError):  # not main thread / unsupported on this platform
            pass
```

> **Windows note (verified relevant):** `signal.SIGTERM` exists on Windows but is only raised by `os.kill(pid, SIGTERM)` / process termination; `SIGINT` is what Ctrl-C delivers. `signal.signal` must run on the **main thread** — `main()` does, so this is safe. We do **not** rely on `SIGBREAK`; Ctrl-C → `SIGINT` is sufficient.

**A.2 — Check the flag at the arm-loop boundary** in `run_headline_campaign` (the cheapest, safest cut point — between arms, never mid-candidate).

```python
# --- BEFORE (run_campaign.py:630-633) ---
    summaries: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for arm in arms:
        arm_search_root = str(search_root / arm)
```

```python
# --- AFTER ---
    summaries: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for arm in arms:
        if SHUTDOWN.is_set():
            print(f"[run_campaign] shutdown requested — stopping before arm {arm!r}; "
                  f"completed arms are archived. Re-run with --resume to continue.")
            summaries.append({"arm": arm, "status": "skipped_shutdown"})
            break
        arm_search_root = str(search_root / arm)
```

**A.3 — Also check between the SEARCH and TEST sub-stages** (so a signal during a long SEARCH still lets the *already-finished* search/select/freeze persist, then stops before launching the 30-seed test leg). Insert right before the `# (4) TEST` block:

```python
# --- BEFORE (run_campaign.py:702-705) ---
        # (4) TEST the frozen winner on the sealed 2018-2025 leg (resume-aware).
        done = (
            {r["run_id"] for r in load_all(str(test_root / arm))} if resume else set()
        )
```

```python
# --- AFTER ---
        if SHUTDOWN.is_set():
            # Search+select+freeze for THIS arm are already on disk; stop before the 30-seed test leg.
            print(f"[run_campaign] shutdown requested after FREEZE for {arm!r}; test leg deferred. "
                  f"Re-run with --resume (frozen winner will be loaded, test seeds resumed).")
            summaries.append({"arm": arm, "status": "frozen_test_deferred",
                              "winner_id": winner.get("candidate_id")})
            break
        # (4) TEST the frozen winner on the sealed 2018-2025 leg (resume-aware).
        done = (
            {r["run_id"] for r in load_all(str(test_root / arm))} if resume else set()
        )
```

**A.4 — Wire the installer in `main()`** right after `load_env()`:

```python
# --- BEFORE (run_campaign.py:854-855) ---
    preload()  # pyarrow before torch (gold-parquet ABI segfault guard) -- BEFORE any torch import
    load_env()  # .env -> os.environ so the LLM key is available (ADR-038); workers inherit it
```

```python
# --- AFTER ---
    preload()  # pyarrow before torch (gold-parquet ABI segfault guard) -- BEFORE any torch import
    load_env()  # .env -> os.environ so the LLM key is available (ADR-038); workers inherit it
    _install_signal_handlers()  # cooperative graceful shutdown (a 27 h run WILL be interrupted)
```

**A.5 — Propagate the flag into the parallel SEARCH driver (deeper cut, optional but recommended).**
The arm-boundary check (A.2) only stops *between* arms. To stop *within* a parallel-search arm's generation loop, `run_parallel` / `_drive_llm_arm` need to observe `SHUTDOWN`. Since these run in the **main process** (the drivers are threads; only training is in workers), pass the event in via `opts`:

In `_search_parallel_arm` (run_campaign.py:266) the call is `runner([arm], opts, ...)`. Add `opts["shutdown_event"] = SHUTDOWN` to the opts dict built by `build_parallel_opts` *or* set it on the opts at the call site. Then in `parallel.py::_drive_llm_arm` (the per-generation loop at parallel.py:545), check it before submitting each generation:

```python
# --- parallel.py:545, BEFORE ---
    for gen in range(gens):
```
```python
# --- AFTER ---
    _shutdown = opts.get("shutdown_event")
    for gen in range(gens):
        if _shutdown is not None and _shutdown.is_set():
            break  # stop launching new generations; already-archived candidates persist
```

> A `threading.Event` is **not picklable into spawn workers**, so this only works in the main-process driver threads — which is exactly where the generation loop runs. Do **not** put `shutdown_event` into the per-task `_spec` (it crosses the spawn boundary). Keep it out of `_spec` (`parallel.py:406`).
> **The serial SEARCH path** (`run_winner_search` → `run_loop`) cannot observe the flag without editing `src/llm/loop.py`; the arm-boundary check (A.2) is the resume granularity there. **§B is what makes a serial-search interrupt cheap.**

---

### §B — Candidate-level SEARCH resume (R1, R5, R11) — **highest $-value change**

**Problem:** `run_loop` re-issues *every* `llm.complete` on resume because it has no concept of "this candidate is already archived." But the archive **is** written incrementally (verified: the real `distributional/` arm has `distributional-g0-c0 … g7-c4` dirs, one per completed candidate, written by `write_run` at `loop.py:421`). So the data to skip already-paid calls **is on disk** — the loop just never reads it.

There are two layers; do **B1** (cheap, no `loop.py` edit, recovers the *whole-arm* re-search) first, then **B2** (the real mid-arm fix) if you want per-candidate granularity.

**B1 — Resume the winner from the candidate archive, not only from `frozen/` (run_campaign.py).**
Today (run_campaign.py:641-651) resume only short-circuits if a **frozen** record exists. If the crash happened after search finished all 30 candidates but before/at freeze, the entire search re-runs. Fix: if a frozen winner is absent **but the candidate archive is already complete**, SELECT+FREEZE from disk instead of re-searching.

```python
# --- BEFORE (run_campaign.py:652-688) ---
        if winner is None:
            # (1) SEARCH on the development split.
            if int(search_n_gpu) > 0:
                _search_parallel_arm( ... )
            else:
                run_winner_search( ... )
            # (2) SELECT the winner by validation DSR.
            winner = select_winner(arm_search_root)
            if winner is None:
                summaries.append({"arm": arm, "status": "no_candidates"})
                continue
            # (3) FREEZE the winner.
            freeze_winner( ... )
```

```python
# --- AFTER (insert a resume-from-archive short-circuit BEFORE re-searching) ---
        if winner is None and resume:
            # CRASH-AFTER-SEARCH recovery: if this arm already produced its FULL candidate budget
            # on disk (search completed, crash before/at freeze), SELECT+FREEZE from the archive
            # instead of re-burning all `candidates` paid Opus calls. We require the full budget so a
            # PARTIAL search (interrupted mid-arm) still resumes the search rather than freezing a
            # winner chosen from an incomplete pool.
            _existing = select_winner(arm_search_root)
            if _existing is not None:
                from src.io.results import load_all as _load_all
                _n_on_disk = len(_load_all(arm_search_root))
                if _n_on_disk >= int(candidates):
                    winner = _existing
                    freeze_winner(arm, winner, search_seed=search_seed,
                                  frozen_root=str(frozen_root), env_fingerprint=f"campaign:{arm}")
                    print(f"[run_campaign] {arm}: resumed winner from archive "
                          f"({_n_on_disk} candidates on disk) — search NOT re-run.")
        if winner is None:
            # (1) SEARCH on the development split.
            ...
```

> **Caveat to verify before relying on B1:** `select_winner` reads `metrics['val_fitness']`; a *partially-written* last candidate dir (R2) could be picked up by `load_all`. §F (atomic write) closes that — apply §F first, or keep the `_n_on_disk >= candidates` guard (a truncated final record would make the count short → falls through to re-search, which is safe).

**B2 — Per-candidate skip inside `run_loop` (src/llm/loop.py) — the real mid-arm fix.**
This is the change that makes an interrupt at candidate 25/30 re-bill only 5 calls instead of 30. It is a **behavior-additive** change gated on a new optional `cfg` key so existing tests/callers are untouched.

```python
# --- BEFORE (loop.py:338-353) ---
        for cidx in range(candidates_per_gen):
            candidate_id = f"{arm}-g{gen}-c{cidx}"
            cand_n = gen * candidates_per_gen + cidx  # 0-based candidate index WITHIN the arm
            monitor.candidate_start(arm, cand_n, gen)
            cand_t0 = time.perf_counter()

            # Per-candidate prompt variation -> ...
            cand_prompt = user_prompt
            if diversity and candidates_per_gen > 1:
                cand_prompt = f"{user_prompt}\n\n{_diversity_directive(cidx, candidates_per_gen)}"

            # 2. Sample a candidate reward source from the LLM ...
            _llm_t0 = time.perf_counter()
            src = extract_reward_source(llm.complete(system_prompt, cand_prompt))
```

```python
# --- AFTER (skip already-archived candidates BEFORE the paid llm.complete) ---
        for cidx in range(candidates_per_gen):
            candidate_id = f"{arm}-g{gen}-c{cidx}"
            cand_n = gen * candidates_per_gen + cidx  # 0-based candidate index WITHIN the arm
            run_id = f"{run_prefix}-{candidate_id}"

            # RESUME (additive, opt-in via cfg['resume_archive_root']): if this candidate's record is
            # ALREADY on disk, re-load it instead of re-issuing the (paid) LLM call + re-training. This
            # makes a mid-search interrupt cost only the UNFINISHED candidates, not the whole arm.
            # NB: a resumed candidate must still seed the reflection chain, so we rebuild prev_feedback_block
            # from the archived feedback_block (keeping the next generation's prompt identical to a
            # non-interrupted run). Off by default -> unit tests / fresh runs are byte-identical.
            _resume_root = cfg_get(cfg, "resume_archive_root", None)
            if _resume_root is not None:
                try:
                    from src.io.results import load_run
                    _rec = load_run(run_id, _resume_root)
                    archive.candidates.append(CandidateRecord(
                        prompt=_rec.get("prompt", ""), reward_source=_rec.get("reward_source", ""),
                        reward_hash=_rec.get("reward_source_hash", ""),
                        feedback_block=_rec.get("feedback_block", ""),
                        val_fitness=float(_rec.get("metrics", {}).get("val_fitness", float("nan"))),
                        tail_stats=_rec.get("metrics", {}).get("tail_stats", {}) or {},
                        generation=gen, candidate_id=candidate_id))
                    prev_feedback_block = _rec.get("feedback_block", prev_feedback_block)
                    monitor.candidate_done(arm, cand_n, fitness=archive.candidates[-1].val_fitness,
                                           status="resumed", secs=0.0)
                    continue
                except (FileNotFoundError, KeyError, ValueError):
                    pass  # not archived (or corrupt) -> fall through and (re)compute this candidate

            monitor.candidate_start(arm, cand_n, gen)
            cand_t0 = time.perf_counter()
            cand_prompt = user_prompt
            if diversity and candidates_per_gen > 1:
                cand_prompt = f"{user_prompt}\n\n{_diversity_directive(cidx, candidates_per_gen)}"
            _llm_t0 = time.perf_counter()
            src = extract_reward_source(llm.complete(system_prompt, cand_prompt))
```

Then thread the resume root from the campaign through `run_arm` into `loop_cfg`:
- `scripts/run_prototype.py:304` (`loop_cfg = {...}`): add `"resume_archive_root": arm_root if cfg_get(... resume ...) else None`. Cleanest: have `run_arm` accept a `resume: bool` kwarg and set `loop_cfg["resume_archive_root"] = arm_root if resume else None`.
- `scripts/run_campaign.py::run_winner_search` (line 156) and its `arm_runner(...)` call (line 186): pass `resume=resume` through, and have `run_headline_campaign` forward its `resume` flag into `run_winner_search`.

> **Science-neutrality argument (must hold for the prereg):** a resumed candidate replays the *exact archived `reward_source`, `val_fitness`, `feedback_block`* — identical to what a non-interrupted run computed and archived. The reflection chain (`prev_feedback_block`) is reconstructed from the same archived block. The **only** non-determinism a resume could introduce is if the *un-finished* candidate, when re-computed, draws a different LLM sample than it would have pre-crash — but that candidate was never archived, so there is no "original" to diverge from. **Document this in PREREGISTRATION as an explicitly-permitted resume policy** (it is the same class as the existing `done_ids` test-leg resume). If you are unwilling to touch `loop.py` before the freeze, ship **B1 only** and accept whole-arm re-search on a mid-arm crash (still far better than today, which re-searches even a *completed* arm that wasn't frozen).

---

### §C — OOM-wave adaptive `n_gpu` back-off (R3, R10)

**Problem:** `n_gpu` is fixed for the whole run (`--gpu`/`--search-gpu` read once; `auto_n_gpu` exists at `parallel.py:32` but **is never called by `run_campaign`** — verified). The prototype proved `n_gpu=4` OOMs the SEARCH transition wave on this exact laptop. There is no mechanism to detect a failure wave and **drop a worker slot** for the next batch.

This is cleanest in the **TEST leg's `run_recycling`** (it already runs in discrete batches with fresh pools — the natural place to lower `n_gpu` between batches) and, with §D, in SEARCH too.

**C.1 — Make `run_recycling` back off `n_gpu` after an OOM-classified batch (src/orchestration/parallel.py).**

```python
# --- BEFORE (parallel.py:388-403) ---
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
                except Exception as exc:  # noqa: BLE001 ...
                    out.append({"ok": False, "error": f"{type(exc).__name__}: {exc}"})
    return out
```

```python
# --- AFTER (drop a GPU slot when a batch shows an OOM wave; floor at 1) ---
    out: list = []
    specs = list(specs)
    step = max(1, int(recycle_every))
    cur_gpu = max(0, int(n_gpu))
    _OOM = ("CUDA out of memory", "MemoryError", "out of memory", "CUBLAS_STATUS_ALLOC_FAILED")
    i = 0
    while i < len(specs):
        batch = specs[i : i + step]
        with DevicePool(cur_gpu, n_cpu, initializer=initializer) as pool:
            batch_out: list = []
            futs = [pool.submit_with(worker, s) for s in batch]
            for f in futs:
                try:
                    batch_out.append(f.result())
                except Exception as exc:  # noqa: BLE001
                    batch_out.append({"ok": False, "error": f"{type(exc).__name__}: {exc}"})
        # OOM-wave back-off: if >=2 of this batch failed with an allocation error, halve concurrency
        # (floor 1) and RE-RUN this batch at the lower setting instead of advancing — so the OOM'd
        # specs are actually completed, not lost. A non-OOM failure (bad reward, degenerate window)
        # does NOT trigger back-off (those are per-spec, not contention).
        _oom_n = sum(1 for r in batch_out
                     if not r.get("ok") and any(t in str(r.get("error", "")) for t in _OOM))
        if cur_gpu > 1 and _oom_n >= 2:
            cur_gpu = max(1, cur_gpu // 2)
            print(f"[run_recycling] OOM wave ({_oom_n}/{len(batch)} alloc-failed) -> n_gpu={cur_gpu}; "
                  f"re-running this batch.", flush=True)
            continue  # retry SAME batch at lower concurrency
        out.extend(batch_out)
        i += step
    return out
```

> This makes the **TEST leg** self-healing under an OOM wave with **no lost seeds**. It is bounded (each batch retried at most ~log2(n_gpu) times). Because the test leg already starts each batch with a fresh pool, lowering `n_gpu` for the next pool is free. **Recommended runtime setting:** start the test leg at `--gpu 3` (the prototype's proven-survivable steady-state), not 4 — let the back-off catch the rest.

**C.2 — Optionally wire `auto_n_gpu` as the campaign default** (so the operator does not have to guess). In `run_campaign.py::main`, when `--gpu`/`--search-gpu` are omitted, call `auto_n_gpu(train_steps)` instead of defaulting to 0/serial. Given the freeze risk, **prefer explicit `--gpu 3 --search-gpu 0` for the headline run** and treat `auto_n_gpu` as a convenience; the binding constraint here is the **transition wave**, which `auto_n_gpu` (steady-state VRAM/RAM math) under-estimates — the prototype note says so explicitly. Do **not** raise `n_gpu` above 3 for SEARCH on this laptop.

---

### §D — SEARCH must use recycling, not a single persistent pool (R3, R10)

**Problem:** `run_parallel` (the `--search-gpu` path) builds **one** `DevicePool` for the entire arm set (`parallel.py:686`) and relies solely on the in-process `del+gc` fix to bound RSS. The TEST leg uses `run_recycling` (fresh pool per `recycle_every` tasks → OS reclaims the whole worker address space). At **50k steps (2× the prototype's buffer)** the SEARCH persistent pool is the highest RAM-creep risk, and it does not benefit from §C's back-off.

**Two options — pick by appetite for editing the search scheduler before the freeze:**

- **D1 (low-risk, recommended for the single-shot run):** run SEARCH **serially** (`--search-gpu 0`, the default) so each candidate trains in the main process via `run_loop`/`make_agent_trainer` and the gc fix + monolithic single-worker memory profile applies. Serial search at 50k on a 4050 is ~180 candidates × 18 min ≈ 54 h **for search alone** — *too slow*. So D1 is only viable if you accept the longer wall-clock. **Not recommended** given the 27 h target.

- **D2 (the throughput path, needs the amendment ratified):** keep `--search-gpu 3` but **route the parallel search through `run_recycling`** the same way the test leg does, instead of `run_parallel`'s single pool. This is a larger change (the LLM driver threads need to submit into recycled pools), and the memory says SEARCH parallelization is *gated on the user freeze + amendment*. **Until then, the only safe high-throughput configuration is: serial SEARCH is too slow, parallel SEARCH at n_gpu=4 OOMs.** The pragmatic resolution for the single-shot run:

  **→ Run SEARCH at `--search-gpu 2` (the prototype's PROVEN-flat setting at the gc fix), accept ~2× the prototype's 17.9 h search wall (because 50k vs 25k), and run the TEST leg at `--gpu 3` with §C back-off.** This sidesteps the un-recycled-pool risk by using the exact concurrency that ran flat for 17 h, and isolates the aggressive setting to the *recycled, self-healing* test leg.

> **Concrete recommendation (no code change required for the safe path):**
> `python scripts/run_campaign.py --resume --search-gpu 2 --gpu 3 --cpu 0`
> — search at the proven-flat n_gpu=2, test leg at n_gpu=3 with the §C back-off as the safety net. Apply §C so the test leg self-heals; do **not** push either leg to 4.

---

### §E — GPU-temperature telemetry → anomaly + thermal-pause hook (R4)

**Problem:** `gpu_temp` is sampled (`monitoring.py:76`) and displayed, but there is **no threshold and no anomaly**. A 4050 laptop under 27 h sustained load throttles or the host sleeps; neither is surfaced as an anomaly, and nothing pauses scheduling to let it cool.

**E.1 — Add a GPU-temperature anomaly threshold (src/utils/monitoring.py).**

```python
# --- BEFORE (monitoring.py:33-39) ---
# Anomaly thresholds (RL-training early-warning signals; web-research-grounded 2026-06-20).
_CRITIC_EXPLOSION_ABS = 1e7
_CRITIC_EXPLOSION_REL = 100.0
_ENT_COEF_COLLAPSE = 1e-4
_ENT_COEF_EXPLODE = 1e3
_FPS_COLLAPSE = 3.0
```

```python
# --- AFTER ---
# Anomaly thresholds (RL-training early-warning signals; web-research-grounded 2026-06-20).
_CRITIC_EXPLOSION_ABS = 1e7
_CRITIC_EXPLOSION_REL = 100.0
_ENT_COEF_COLLAPSE = 1e-4
_ENT_COEF_EXPLODE = 1e3
_FPS_COLLAPSE = 3.0
# Laptop-GPU thermal guard (RTX 4050 Laptop). NVIDIA consumer GPUs throttle ~83-87C and the
# hardware slowdown/shutdown limit is ~90C; warn well below so a 27 h run is visibly throttling
# BEFORE it loses throughput silently. Tune to the observed idle->load delta on the host.
_GPU_TEMP_WARN_C = 82
_GPU_TEMP_CRIT_C = 87
```

**E.2 — Check it on every resource flush.** `_flush()` (monitoring.py:212) already calls `self._res.sample()`. Add a temperature check there so it fires on *every* update (training metric or idle pump tick), independent of training callbacks:

```python
# --- BEFORE (monitoring.py:215-219, inside _flush) ---
        self.state["updated"] = _now_iso()
        self.state["elapsed_s"] = round(time.time() - self.t0, 1)
        self.state["resources"] = self._res.sample()
        self.state["best_fitness"] = dict(self._best)
        self.state["anomalies"] = {"count": len(self._anomalies), "recent": self._anomalies[-5:]}
```

```python
# --- AFTER ---
        self.state["updated"] = _now_iso()
        self.state["elapsed_s"] = round(time.time() - self.t0, 1)
        self.state["resources"] = self._res.sample()
        self._check_thermal(self.state["resources"])  # GPU-temp guard (long-run laptop throttle/sleep)
        self.state["best_fitness"] = dict(self._best)
        self.state["anomalies"] = {"count": len(self._anomalies), "recent": self._anomalies[-5:]}
```

Add the method (next to `_check_training_anomalies`, ~monitoring.py:320). De-dupe with a cooldown so a hot GPU does not spam `anomalies.jsonl` every 0.3 s:

```python
    def _check_thermal(self, res: dict[str, Any]) -> None:
        """Flag GPU thermal throttle/limit on a long laptop run (deduped, ~60 s cooldown)."""
        t = res.get("gpu_temp")
        if not isinstance(t, (int, float)):
            return
        now = time.time()
        last = getattr(self, "_last_thermal_ts", 0.0)
        if now - last < 60.0:
            return
        if t >= _GPU_TEMP_CRIT_C:
            self._last_thermal_ts = now
            self.anomaly("gpu_thermal_critical",
                         f"gpu_temp={t}C >= {_GPU_TEMP_CRIT_C}C (throttling/limit imminent)", level=40)
        elif t >= _GPU_TEMP_WARN_C:
            self._last_thermal_ts = now
            self.anomaly("gpu_thermal_warn", f"gpu_temp={t}C >= {_GPU_TEMP_WARN_C}C", level=30)
```

> `_check_thermal` lives on `RunMonitor` and is inherited by `ParallelMonitor`, so it fires on **both** the serial-search in-process monitor **and** the parallel `ParallelMonitor` pump (which calls `_flush()` on every idle tick, `monitoring.py:514`). One edit covers all paths.

**E.3 — (Optional) thermal pause in the TEST recycling loop.** With E.1/E.2 the temperature is *observable* and *logged*; to make it *actuating*, `run_recycling` (§C) can read the current GPU temp between batches and `time.sleep` until it drops below `_GPU_TEMP_WARN_C`. This couples `parallel.py` to NVML; given the freeze constraint, **prefer the observe-and-alert version (E.1/E.2) plus the operational mitigation in §K (cap the GPU power/clocks, ensure cooling)** over an auto-pause that complicates the scheduler. If you do want it, gate it behind a config flag and put the NVML read in a tiny best-effort helper that returns `None` on any error (mirror `_Resources`).

---

### §F — Atomic record write (R2, R8) — prevents corrupt records on a mid-write kill

**Problem:** `write_run` (`src/io/results.py:137`) writes `record.json` with a plain `open(...,"w")` + `json.dump`. A SIGINT / power-loss *during* that write leaves a **truncated JSON** that `load_run` will fail to parse (`json.load` raises) → on `--resume`, `load_all` (which calls `load_run` on every dir) **crashes the whole resume**. The monitor already uses the atomic temp-file+replace pattern for `progress.json` (`monitoring.py:221`) — apply the same to records.

```python
# --- BEFORE (results.py:136-138) ---
    record_path = run_dir / _RECORD_NAME
    with record_path.open("w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True, default=str)
```

```python
# --- AFTER (atomic: write to a temp sibling, fsync, then os.replace) ---
    import os as _os

    record_path = run_dir / _RECORD_NAME
    tmp_path = record_path.with_suffix(".json.tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True, default=str)
        fh.flush()
        _os.fsync(fh.fileno())  # durability: the bytes hit disk before the rename
    _os.replace(tmp_path, record_path)  # atomic on Windows + POSIX (same dir)
```

> `os.replace` is atomic within a directory on both Windows and POSIX. A crash now leaves either the *old* record or the *new* one — never a half. This makes B1/B2's `load_all`-based resume robust against R2. Apply the **same** temp+replace to the `reward.py`/`prompt.txt` sidecars if you want full belt-and-suspenders, but the `record.json` is the schema-validated one that breaks resume, so it is the priority.
> **Note:** `load_all` (`results.py:268`) iterates dirs and calls `load_run`; a stray `.json.tmp` left by a crash is ignored (it looks for exactly `record.json`). Good — no cleanup needed.

---

### §G — Fail loud on a campaign-level failure wave (R6)

**Problem:** if the TEST leg returns all-failures for an arm, `run_campaign.py:733-739` prints a WARNING and **moves on**; `matched_budget_ok` from `evaluate_winners_on_test_parallel` (`test_leg.py:332`) is computed but **never inspected** by the campaign. The same is true if `n_failed == len(seeds)`. The run can complete "successfully" having written zero usable records for an arm.

```python
# --- BEFORE (run_campaign.py:732-739) ---
                written = _res["written"]
                if _res["n_failed"]:
                    print(
                        f"[run_campaign] WARNING: {arm} parallel TEST leg had {_res['n_failed']} "
                        f"failed seed(s) — first error: {(_res['failures'][0] or {}).get('error')}"
                    )
```

```python
# --- AFTER (escalate a TOTAL failure wave; warn on partial) ---
                written = _res["written"]
                if _res["n_failed"]:
                    _first = (_res["failures"][0] or {}).get("error")
                    if not _res.get("matched_budget_ok") or len(written) == 0:
                        # EVERY (or nearly every) seed failed -> a systemic fault (dead CUDA ctx, OOM
                        # wave that back-off couldn't absorb, degenerate window). Do NOT silently bank
                        # an empty arm; surface it so the operator stops and fixes root cause.
                        print(f"[run_campaign] ERROR: {arm} TEST leg FAILURE WAVE — "
                              f"{_res['n_failed']}/{_res['n_specs']} seeds failed, {len(written)} written. "
                              f"First error: {_first}", flush=True)
                        summaries.append({"arm": arm, "status": "test_failure_wave",
                                          "n_failed": _res["n_failed"], "first_error": str(_first)[:200]})
                        if SHUTDOWN.is_set():
                            break
                        continue  # skip the 'tested' summary append for this arm
                    print(f"[run_campaign] WARNING: {arm} TEST leg had {_res['n_failed']} failed "
                          f"seed(s) — first error: {_first}")
```

> Keep it a loud **continue** (not a hard `raise`) so a single bad arm does not torch the other five arms' already-written results — but the `test_failure_wave` status in `campaign_summary.json` is now machine-detectable, and a human watching the console sees `ERROR`. Pair with §J (final summary scan) so the end-of-run banner refuses to claim success if any arm has this status.

---

### §H — Preflight disk-space + key check (R8) — cheap insurance at `main()` start

Add to `run_campaign.py::main()` after `_install_signal_handlers()`:

```python
    # Preflight: a 360-run campaign writes ~hundreds of record dirs + per-seed env.json captures;
    # a full disk mid-run corrupts a write (R8). Fail BEFORE burning Opus calls, not 10 h in.
    import shutil as _shutil
    _free_gb = _shutil.disk_usage(Path(output_dir).anchor or ".").free / 2**30
    if _free_gb < 5.0:
        raise SystemExit(f"[run_campaign] preflight: only {_free_gb:.1f} GB free on the output volume; "
                         f"need >=5 GB headroom for the campaign archive. Free space and re-run.")
    # Preflight: real Pass-B run needs the key NOW (not after the first arm's search). build_transport
    # raises lazily; surface it before any GPU work.
    if not args.dry_run and provider != "stub" and not __import__("os").environ.get(
        cfg_get(camp_llm, "api_key_env", "ANTHROPIC_API_KEY")):
        raise SystemExit(f"[run_campaign] preflight: {cfg_get(camp_llm, 'api_key_env', 'ANTHROPIC_API_KEY')} "
                         f"is unset; the real reward-author cannot run. Set it in .env and re-run.")
```

> (Place after `camp_llm`/`provider`/`output_dir` are defined — i.e. near run_campaign.py:884, before the `args.dry_run` block or just after it. Adjust the variable references to the in-scope names.)

---

### §I — (Optional) Widen the LLM-error catch so an API storm degrades instead of crashing (R11)

`run_loop` (loop.py:360) catches only `SandboxError`. A sustained Opus 429/5xx wave (after tenacity's 6 retries) raises a provider exception out of `llm.complete` → **crashes the arm**. With §B applied, that crash is cheap to resume — but you can also make the loop *log + skip* the candidate (treat an exhausted-retry API error like a failed candidate) so the arm finishes with N-1 candidates rather than dying. This is a **science-sensitive** change (it changes the matched budget if a candidate is dropped), so **do not** apply it silently — if you want it, the dropped candidate must be re-attempted on resume (which §B's per-candidate skip naturally does: it was never archived). Given the freeze, **prefer relying on §B** (resume is cheap) over widening the catch.

---

### §J — (No code change) Anomalies stay advisory; add an end-of-run integrity banner

Anomalies are intentionally non-halting (R9 — the 64 prototype critic explosions are expected without PopArt). Do **not** make them halt. But the **final summary** should refuse a clean bill of health if any arm has `status in {"no_candidates","winner_not_testable","test_failure_wave","skipped_shutdown","frozen_test_deferred"}`. Add to the end of `run_headline_campaign` before `return summary`:

```python
    _bad = [s for s in summaries if s.get("status") not in ("tested",)]
    summary["all_arms_tested"] = (len(_bad) == 0)
    if _bad:
        print("[run_campaign] INCOMPLETE: arms not fully tested -> "
              + ", ".join(f"{s['arm']}:{s.get('status')}" for s in _bad)
              + "  (re-run with --resume).")
```

---

## 3. OPERATIONAL RUNBOOK (§K) — the non-code mitigations that matter most

These are as important as the code for a *laptop* 27 h run:

1. **Disable sleep/hibernate for the run (R12, the single biggest non-code risk).**
   `powercfg /change standby-timeout-ac 0` and `powercfg /change hibernate-timeout-ac 0` (and monitor-timeout if you want the screen off but the machine awake: `powercfg /change monitor-timeout-ac 0`). Keep the laptop **plugged in** the whole time. A single OS sleep almost always invalidates the CUDA context on wake → cascade of worker failures.
2. **Cap GPU thermals proactively (R4).** Lower the sustained power/clock so the 4050 runs cool over 27 h rather than throttling unpredictably: e.g. `nvidia-smi -pl <watts>` (set a power limit a few W below max) and ensure the laptop is on a hard, elevated surface / cooling pad. Cooler-but-slightly-slower beats thermal-throttle-roulette.
3. **Run detached + logged, watch via the dashboard.** Launch with output redirected to a logfile and watch with `python scripts/monitor.py outputs/campaign --interval 5` from a second terminal. The prototype was babysat by an *ad-hoc external* watcher (`watchdog3.log`) — **there is no committed watchdog**; `monitor.py` is read-only and is the supported tool.
4. **Always pass `--resume`.** Make it muscle memory: `--resume` is idempotent and is the entire recovery story. Combined with §A/§B/§F, a restart re-bills nothing already on disk.
5. **Run the arms in deliberate order and consider one-arm-at-a-time for the paid SEARCH.** `--arms distributional` … then `--arms scalar` … lets you checkpoint between the expensive Opus searches and bound the blast radius of R1 to a single arm. (The H2-family guard at run_campaign.py:896 will reject a *final* run missing family arms, but per-arm staging during search is fine — assemble the full family for the test/analysis pass.)
6. **Pre-flight with the keyless stub.** `--dry-run` (always Pass A / stub / synthetic) exercises the full 4-stage machinery for free; run it after applying the spec to confirm no syntax/wiring regressions before spending a single Opus token.
7. **Recommended invocation for the single-shot headline run (safe-throughput):**
   ```
   python scripts/run_campaign.py --resume --search-gpu 2 --gpu 3 --cpu 0
   ```
   search at the proven-flat n_gpu=2 (§D), test leg at n_gpu=3 with the §C back-off net, never 4 on this laptop.

---

## 4. Apply order & verification checklist

1. **§F** (atomic write) — foundational; makes every resume path robust. Lowest risk.
2. **§A** (signal handler + arm/stage-boundary checks) — the graceful-shutdown core.
3. **§B1** (resume winner from archive) — recovers a completed-but-unfrozen arm. No `loop.py` edit.
4. **§B2** (per-candidate skip in `loop.py`) — the real $-saver; **document the resume policy in PREREGISTRATION before freeze**.
5. **§C** (TEST-leg OOM back-off) + **§G** (fail-loud failure wave) — test-leg resilience.
6. **§E** (GPU-temp anomaly) — observability for the laptop thermal risk.
7. **§H/§J** (preflight + integrity banner) — cheap guards.
8. **§D/§K** — choose the concurrency (search n_gpu=2, test n_gpu=3) and apply the power-settings runbook.

**Verify after applying (no Opus spend):**
- `python scripts/run_campaign.py --dry-run` → completes; `campaign_summary.json` shows `all_arms_tested: true`.
- Run the existing suites that pin the contracts these changes touch:
  `tests/test_run_campaign.py` (resume `done_ids`, freeze, once-only touch), `tests/test_test_leg.py`,
  `tests/test_parallel_recycling.py`, `tests/test_test_leg_equivalence.py` (the byte-identical serial==parallel proof — **must stay green**, it certifies science-neutrality).
- Manual SIGINT test: launch `--dry-run`, press Ctrl-C mid-run → confirm it prints the "finishing in-flight work" message, writes no truncated `record.json` (grep for `.json.tmp` leftovers — there should be none after `os.replace`), and a subsequent `--dry-run --resume` skips the already-archived candidates.
- Add a unit test for §B2 (resume skip): a `run_loop` with `resume_archive_root` pointing at a dir containing one archived candidate must **not** call `llm.complete` for that candidate (assert on a `FakeTransport.calls` count). This guards the $-critical behavior.

---

## Appendix — exact evidence map (so each claim is checkable)

| Claim | Evidence |
|---|---|
| No signal/atexit handler in the runner | `grep signal\|SIGINT\|SIGTERM\|atexit\|KeyboardInterrupt scripts/ src/` → only `monitor.py:168`, `run_prototype.py:653` (`os._exit(0)` success path) |
| SEARCH has no candidate-level resume | `src/llm/loop.py` has no `load_run`/`exists`/skip; `run_loop` loops `range(generations)` from 0 (loop.py:323) and calls `llm.complete` per candidate (loop.py:353) |
| Campaign SEARCH resume is arm-level all-or-nothing | run_campaign.py:641-651 (loads frozen winner or re-runs entire search) |
| TEST resume is per-seed `done_ids` | run_campaign.py:703-705; test_leg.py:289-292; pinned by `test_resume_skips_already_done_records` |
| `n_gpu=4` OOMs SEARCH (measured) | `project-runready-gotchas` item 5 (52 failed at n_gpu=4 transition wave); `project-prototype-complete` (gc fix; flat at n_gpu=2) |
| `auto_n_gpu` never called by campaign | `grep auto_n_gpu scripts/run_campaign.py` → 0 hits; defined `parallel.py:32` |
| SEARCH uses one persistent pool; TEST uses recycling | `run_parallel` → `with DevicePool(...)` parallel.py:686; TEST → `run_recycling` (fresh pool per batch) parallel.py:393 |
| gpu_temp sampled but not thresholded | sampled `monitoring.py:76`; no `gpu_temp` in `_check_training_anomalies` (monitoring.py:320-342) |
| `record.json` non-atomic write | results.py:137 plain `open("w")` + `json.dump`; cf. atomic `progress.json` at monitoring.py:221 |
| Failure-wave `matched_budget_ok` computed but unused at campaign level | test_leg.py:332 computes it; run_campaign.py:732-739 only prints a WARNING |
| `auto_shutdown_on_complete` is a no-op | run_campaign.py:947-948 prints a line; no `os.system`/`shutdown` call anywhere (`grep` → 0 impl hits) |
| Anomalies advisory only (64 in prototype, run continued) | `watchdog3.log` (`anom=64 ... done=239/240 err=0`); `anomaly()` only appends + logs (monitoring.py:344-357) |
| Calibration: 17.9 h at n_gpu=2, search-only, 25k | `project-prototype-complete` |
| `m ≈ 18 min/50k-run` on 4050; 360 core runs | `docs/COMPUTE_AND_TRAINING_TIME.md` §2-3 |
| GPU is real 6141 MiB RTX-4050, idle 41C | `nvidia-smi` on host (this audit) |
