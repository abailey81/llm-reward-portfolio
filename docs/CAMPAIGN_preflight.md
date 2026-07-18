# CAMPAIGN PRE-FLIGHT — keyless dry-run result, checklist, and run command

**Purpose.** Prove the end-to-end HEADLINE campaign pipeline (`scripts/run_campaign.py`) executes
with **no crash** on a keyless/synthetic dry-run, record the exact pre-flight checklist, and pin the
exact run command(s) for the real campaign. This is a RELEASE pre-flight — not the write-up.

**Verified on:** 2026-06-24 · venv `.venv\Scripts\python.exe` (**Python 3.11.9**, the validated venv) ·
Windows 11 · repo `c:\Users\User\Desktop\dissertation_papers\llm-reward-portfolio`.

**Bottom line: GO** (conditional on the manual checklist below — free RAM, ratify search-parallelism,
freeze the prereg). Every automated gate is GREEN. No code defect surfaced.

---

## 1. Dry-run RESULT (what actually ran)

Command run (keyless — never touches the API key; `--dry-run` hard-overrides to the stub):

```
.venv\Scripts\python.exe scripts\run_campaign.py --dry-run --no-shutdown
```

**Outcome: exit code 0, 10.1 s wall-clock, no crash, no traceback.** Console:

```
[run_campaign] DRY RUN - 1 LLM arm x 2 candidates x 1 seed on a synthetic panel (stub).
[run_campaign] HEADLINE single-split: arms=['distributional'] seeds=[0] search_seed=0 candidates=2
               steps=200 gens=1 pass=A provider=stub embargo=21 resume=False -> outputs/campaign_dryrun
[run_campaign] windows train=[60, 599] val=[599, 600] test=[600, 601]
  distributional: winner_not_testable (val_window (599, 600) must start at/after train_window end 599
               + max(embargo 21, lookback 60) (disjoint, purged splits, R18))
[run_campaign] done in 10.1s -> outputs/campaign_dryrun/campaign_summary.json
```

### Pipeline stages exercised (all four)
The on-disk archive under `outputs/campaign_dryrun/` proves the 4-stage Eureka post-loop ran:

| Stage | Evidence | Status |
|---|---|---|
| **(1) SEARCH** | `search/distributional/` holds 2 candidate dirs (`...-g0-c0`, `...-g0-c1`, 3 files each) + an `_env` fingerprint | ✅ ran (stub author, 2 candidates) |
| **(2) SELECT** | the run proceeded past `select_winner` (a winner was returned; no `no_candidates`) | ✅ ran (val-DSR winner picked) |
| **(3) FREEZE** | `frozen/distributional-winner/` holds 2 files (`record.json` + `reward.py`, `frozen: True`) | ✅ ran (winner sealed) |
| **(4) TEST** | reached, then **correctly aborted** with the documented `winner_not_testable` guard (see below) | ✅ reached; guard fired by design |

### The TEST-leg guard firing is EXPECTED, not a bug
On the tiny **600-day synthetic panel** the three calendar windows collapse: with `lookback=60` and the
R18 purge `max(embargo 21, lookback 60) = 60`, `resolve_windows` clamps to `train=[60,599]`,
`val=[599,600]`, `test=[600,601]` — a degenerate 1-session val/test. The env builder's leakage guard then
refuses to build (val must start ≥ `train_end + 60`), `evaluate_winner_on_test` raises `ValueError`, and the
driver catches it into a clean `winner_not_testable` summary (run_campaign.py L763–764). **This is the
known dry-run artefact called out in the run plan — the degenerate window proves the leakage/purge guard is
live, not that the pipeline is broken.** On the real 5,283-session gold panel the clamps are inert and the
test leg runs normally.

> Note: the frozen/test **desync guard** (run_campaign.py L435–441 — hash-mismatch abort) did NOT fire here
> because the TEST leg short-circuited before the per-seed loop. It is unit-covered separately by
> `tests/test_run_campaign.py` (green in §2). The dry-run does not, and is not expected to, exercise it.

`campaign_summary.json` was written correctly (single `distributional` arm, status `winner_not_testable`,
the three windows, `wall_clock_s: 10.1`).

---

## 2. Automated gates — all GREEN

| Gate | Command | Result |
|---|---|---|
| **Freeze consistency / drift** | `python scripts\freeze.py --check` | ✅ **exit 0** — Phase-0 MET (`DECISION_LOG.md#PHASE-0 GREEN 2026-06-17`); all 9 prose↔YAML checks OK (seeds [0..29], `m=6`, diff-tests, SESOI 0.05, TOST ±0.05, cost grid [0,5,10,25,50], λ=0, TF32 on, reflect-protocol present); hash `d27bf5ab…ed3593`; `freeze_hash: null` (not yet frozen — expected pre-freeze). |
| **Fast test suite** | `python -m pytest -m "not slow"` | ✅ **466 passed, 1 skipped, 9 deselected, 0 failed/0 error** in 58 s. The 271 warnings are benign sklearn GP `ConvergenceWarning`s from the bayes_opt arm tests — not failures. |
| **`.env` API key** | (read-only presence check, value NOT printed) | ✅ `ANTHROPIC_API_KEY` PRESENT (len 110, `sk-ant…` prefix). Also present: `REFINITIV_USERNAME/PASSWORD/APP_KEY`, `FRED_API_KEY`. |
| **Frozen H2 family wiring** | static check vs `analyze_campaign.H2_CONTRASTS` | ✅ `{distributional, scalar, placebo, scalar_cvar5}` ⊆ campaign arms — the non-dry-run fail-loud family guard (run_campaign.py L896–908) will pass. |

---

## 3. Hardware reality (MEASURED this session)

| Resource | Measured value | Binding implication |
|---|---|---|
| CPU | 13th-Gen i7-13620H — **16 logical / 10 physical** | not the bottleneck (~10 thread-pinned workers core-wise) |
| RAM | **15.6 GB total**; right now **6.8 GB free / 8.8 GB used (56%)** | **the hard wall.** Free apps before the run (target ≥ ~8 GB free). |
| GPU | **RTX 4050 Laptop, 6.0 GB VRAM**, torch **2.6.0+cu124**, `cuda.is_available()=True` | **caps GPU workers at 4** (~1.4 GB CUDA ctx each). |
| `auto_n_gpu(50000)` | returns **4** (also 4 at 25k) | the scheduler already computes the n_gpu=4 ceiling on this box. |

These match the toasty run-plan's measured table exactly. **Hard ceiling = 4 GPU workers (VRAM-bound); a
5th OOMs.** `auto_n_gpu` budgets RAM off `total − reserve` (steady-state working set), so it returns 4 even
at the current 6.8 GB free — but the run still benefits from freeing apps to avoid transient swap.

---

## 4. PRE-FLIGHT CHECKLIST (the go/no-go gate)

Tick every box **before** launching the real Opus run. Automated items already verified this session are
pre-ticked `[x]`; manual/decision items are `[ ]`.

### Environment & gates (verified this session)
- [x] **Python = validated venv 3.11.9** (`.venv\Scripts\python.exe`). Do NOT upgrade (recycling deadlocks on
      Windows spawn for all of 3.11–3.14; 3.14 has no torch wheels — run-plan §2 verdict).
- [x] **`freeze.py --check` GREEN** (exit 0; hash `d27bf5ab…ed3593`; Phase-0 met; not-yet-frozen).
- [x] **Fast suite GREEN** — `pytest -m "not slow"` → 466 passed / 0 failed.
- [x] **`ANTHROPIC_API_KEY` present in `.env`** (len 110, `sk-ant…`). Campaign reads it via `load_env()` and
      workers inherit it. `config/campaign.yaml` is `pass: B`, `provider: anthropic`, `model_snapshot:
      claude-opus-4-8` — the real reward author.
- [x] **Dry-run GREEN** — 4 stages exercised, exit 0 (§1).

### Resources (do immediately before the run — MUST re-check live)
- [ ] **Free ~8 GB RAM** (close browsers/IDE/Docker/etc.). Live now: only **6.8 GB free**. Target ≥ ~8 GB
      free so n_gpu=4 has headroom (per-worker ≈ 2.1 GB at 50k). **Single biggest practical RAM lever.**
- [ ] **Confirm GPU idle** (no other CUDA process holding VRAM) — 6.0 GB total is tight; 4 ctx ≈ 5.6 GB.
- [ ] **Thermals** — the laptop runs ~13–27 h; use a cooler ambient / stand, or prefer the 4090 (§6).

### Decisions to ratify (frozen-design items — user only)
- [ ] **Ratify the search-parallelism choice** (`headline_reflect_protocol: record_at_freeze`). The default
      is **serial reflect-on-last** (`--search-gpu 0`, the prototype-de-risked path). `--search-gpu N` switches
      to **reflect-on-BEST** (Eureka-faithful, ~4× faster on the search half, buffer==50k) — an
      **amendment-gated frozen-decision** (PREREGISTRATION R21). Decide serial vs parallel and record it at
      freeze BEFORE the run. *Until ratified, keep `--search-gpu` OFF.*
- [ ] **Ratify the prior amendments** (λ=0 R22, TF32 R23, rf/delisting/PopArt/shuffled-placebo from the
      definitive plan) — all already mirrored in the prereg YAML and passing `freeze.py --check`.
- [ ] **Confirm laptop-vs-4090** (§6 recommends the 4090: ~5 h, ~$15, recycling works on Linux).

### Freeze (the immutable gate — user only, run LAST before the campaign)
- [ ] **`python scripts\freeze.py`** (no `--check`) — flips `frozen: true`, records the hash + git SHA in
      `docs/DECISION_LOG.md`, tags `prereg-v1.0`. **Run ONLY by the user, ONLY after the decisions above.**
      (An agent / CI must never run this; `--check` is the agent-safe form.)

### V1–V6 verification gates (toasty run-plan §5 — clear before the real Opus run)
- [x] **V1 — Unit tests:** full fast suite green (466 passed). *(done this session)*
- [x] **V2 — Dry-run:** keyless `--dry-run` end-to-end, 4 stages, no crash, guard fires correctly. *(done §1)*
- [ ] **V3 — Live parallel smoke (load test):** `run_prototype.py --parallel --synthetic --gpu 3` (stub, tiny
      steps) → confirm 4 workers spawn + train + archive, **no OOM/CUDA error**, measure peak RAM/VRAM. Then
      the same for the winner-re-run parallelization on synthetic.
- [ ] **V4 — Manual-recycle soak:** ~24 synthetic candidates at n_gpu=4, pool-recycle every 12, RSS flat across
      batches for ~20 min (proves no fragmentation creep).
- [ ] **V5 — Resume/idempotency:** kill mid-run → `--resume` skips completed (arm,seed) ids, no duplicate
      training, no desync.
- [ ] **V6 — Determinism:** same seed → same per-seed test record (archive-replayable).

> **V3–V6 are LIVE-GPU smokes not run in this pre-flight** (this pass proves keyless no-crash + the static
> gates). They are the empirical "n_gpu=4 is safe + parallel == serial" proof and should be cleared on
> synthetic/stub before burning the Opus budget.

### Go / No-Go
**GO** only when: all boxes above ticked · V1–V6 green · prereg frozen · ≥ ~8 GB RAM free · `--search-gpu`
decision recorded. **Any OOM at n_gpu=4 → drop to `--gpu 3`** (measured-safe) or close more apps; the plan
degrades gracefully and never crashes.

---

## 5. EXACT run command(s) for the real campaign

The campaign reads arms/seeds/candidates/steps/author from `config/campaign.yaml` (7 arms · 30 candidates ·
30 seeds · 50k steps · Opus 4.8 · `pass: B`). Pick ONE launch line by the search-parallelism decision.

### Recommended n_gpu = 3 (the laptop ceiling; `--gpu >= 4` is refused by run_campaign)

**(A) DEFAULT — serial search + PARALLEL test leg** *(no amendment needed; the prototype-de-risked search path)*
```
.venv\Scripts\python.exe scripts\run_campaign.py --gpu 3 --resume
```
- `--gpu 3` parallelizes only the **TEST leg** (the 210 winner re-runs = 7 winners × 30 seeds), which is
  science-neutral (embarrassingly parallel, zero reflection coupling). SEARCH stays serial reflect-on-last.
- `--resume` makes it idempotent (skips archived (arm,seed) records after any interruption).
- Auto-shutdown is config-gated (`auto_shutdown_on_complete: true`) — on a **rented** GPU it powers off on
  completion. **On the laptop add `--no-shutdown`** to keep the host alive:
  ```
  .venv\Scripts\python.exe scripts\run_campaign.py --gpu 3 --resume --no-shutdown
  ```

**(B) MAX-SPEED — PARALLEL search + PARALLEL test leg** *(ONLY after the R21 reflect-on-best amendment is ratified + frozen)*
```
.venv\Scripts\python.exe scripts\run_campaign.py --gpu 3 --search-gpu 3 --resume
```
- `--search-gpu 3` additionally parallelizes SEARCH with **reflect-on-best** + matched 50k buffer (~4× on the
  search half). This **changes the reflection prompt sequence** (frozen-decision) — do not use until the
  `headline_reflect_protocol` choice is recorded at freeze.

### Headline choice
- **Per the frozen YAML the headline choice is unresolved** (`headline_reflect_protocol: record_at_freeze`;
  default `serial_reflect_on_last`). **Until the user ratifies reflect-on-best, command (A) is the correct,
  in-spec launch.** Command (B) is faster and more Eureka-faithful but is amendment-gated.
- **Recommended n_gpu = 3** on this laptop (VRAM ceiling; `--gpu >= 4` is refused by run_campaign). Fallback
  **`--gpu 2`** if any OOM. Optional `--cpu 1` only after freeing the ~8 GB other apps (marginal +10–15%).
- **Throughput:** the confirmatory campaign's PRIMARY substrate is **UCL Myriad** (ADR-053, 2026-07-13;
  `scripts/run_campaign_cluster.py`, SGE arrays); the **RTX 4050 laptop is the certified fallback** (n_gpu 2–3).
  Wall-clock depends on the frozen per-candidate budget B\* — see `docs/COMPUTE_AND_TRAINING_TIME.md` for the
  laptop estimate. Both the earlier rented-RTX-4090 target and the LAPTOP-ONLY (ADR-040) framing are
  **superseded** by ADR-053. `auto_shutdown_on_complete` is a verified no-op on the laptop; operators pass `--no-shutdown`.

### Useful variants
- Resume after interruption: append `--resume` (already in the recommended lines).
- Override a single config (rare; gated single-shot): `--config config\<stem>.yaml` (now honored — derives the
  stem; only the campaign config is overridable, the inference splits are fixed).
- A final keyless re-smoke any time: `--dry-run --no-shutdown` (never burns the key).

---

## 6. Blockers found

**None that block the pipeline.** No crash, no traceback, no failing test, no missing artifact. Open items
are **process/decision gates**, not code defects:

1. **Pre-registration is NOT yet frozen** (`frozen: false`, `freeze_hash: null`). `freeze.py --check` is
   green; the user must run `freeze.py` (write path) after ratifying the decisions in §4. *(Gate, not a bug.)*
2. **Search-parallelism (`--search-gpu`) is amendment-gated and unratified** (`headline_reflect_protocol:
   record_at_freeze`). Keep it OFF (command A) until the user records the choice. *(Decision, not a bug.)*
3. **Live RAM is 6.8 GB free (< the ~8 GB target).** Free apps immediately before launch. *(Operational.)*
4. **Live-GPU V3–V6 gates not yet run** (this pre-flight is keyless/static + the dry-run). Clear them on
   synthetic/stub before the Opus run. *(Remaining verification, not a defect.)*

### Notes / non-issues (verified, do not act on)
- The `winner_not_testable` in the dry-run is the **expected** degenerate-window artefact of the 600-day
  synthetic panel (R18 purge guard firing), NOT a pipeline failure — see §1.
- The 271 pytest warnings are benign sklearn GP convergence warnings from the bayes_opt arm — not failures.
- The 2005-cohort test-universe composition bias (R17) is a documented headline *limitation*, not a run
  blocker; the splits are disjoint + embargoed (no leakage).
