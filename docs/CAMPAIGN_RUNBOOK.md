# CAMPAIGN RUNBOOK — the single operational document for run day

**Scope.** This is the *operations* runbook for the HEADLINE single-split campaign: the exact,
ordered sequence from **freeze → keyless dry-run/V-gates → set workers → SEARCH → monitor →
SELECT/FREEZE → TEST → analyze → secondary analyses**, with the exact command, the expected
output, and the **go/no-go gate** at every step. It is not the write-up and contains no
dissertation prose.

**This doc does NOT duplicate** (it references) the sibling specs:
- **Freeze decisions / the freeze act** → `docs/FREEZE_RUNBOOK.md` (Step-0 mismatch resolution,
  `make freeze`, supervisor notification) and `PREREGISTRATION.md` §10/§12 + amendment record.
- **Run robustness / RAM / dry-run / freeze-decisions** → their separate docs and
  `docs/RUN_READINESS_2026-06-19.md` (per-provider diversity, the gc fix, vix-in-points).
- **Compute & cost bands** → `docs/COMPUTE_AND_TRAINING_TIME.md` (per-GPU `m`, GPU-hour tables).
- **The master run plan / V1–V6 protocol / throughput math / risk register** →
  `~/.claude/plans/toasty-crafting-quill.md` (the DEFINITIVE plan this runbook operationalizes).
- **Power / MDE** → `docs/CAMPAIGN_power.md` (regenerate with `make power`).

**Authoritative numbers carried here for run-day convenience (verified against the code):**
the laptop ceiling is **n_gpu = 4** GPU workers (VRAM-bound) + at most 1 CPU worker (RAM-bound);
`auto_n_gpu(50000)` returns **4**. **Compute — authoritative source `docs/COMPUTE_AND_TRAINING_TIME.md`
(post-amendment D2, winner seeds 5→30; 7 arms after R32 added `placebo_shuffled`):** the **7-arm core
≈ 600 runs** (210 search + 210 winner-test + 120 H1 + 60 H3) ≈ **2.6 days on the laptop at n_gpu=4**
(free) / **~13 h on a rented 4090; ~180 GPU-hr** — consistent with the "Estimated wall-clock — core
~600 runs" callout in §4 below. The optional PPO/TD3 algorithm-robustness (~+120 runs) is OPTIONAL on
scope/time grounds (there is **no GPU-hour cap** — `hard_budget_gpu_hours` was removed 2026-06-28; the
GPU-hr figures are estimates, not a limit). The run-count recorded at freeze **is** the DSR trial count, so take it from the COMPUTE doc, not a
round number. `run_campaign.py` writes to `outputs/campaign/{search,frozen,test}` and
`campaign_summary.json`. The campaign reward-author is **Claude Opus 4.8** (`config/campaign.yaml`,
`pass: B`, `provider: anthropic`, `ANTHROPIC_API_KEY`); 7 arms × 30 candidates (search) → 7 winners
× 30 seeds (test).

> **Two confirmatory invariants that dominate the grade (do not violate):**
> 1. **Freeze BEFORE any real result is visible.** A pre-registration frozen after results exist is
>    worthless. The freeze (Step 1) gates everything below it.
> 2. **The TEST leg is touched EXACTLY ONCE per (arm, seed).** This is enforced in code
>    (`build_test_record` once-only touch + the frozen/test desync hash guard); never re-run TEST to
>    "improve" a number, never re-select after seeing test output.

---

## 0. Pre-flight checklist (do these once, before Step 1)

| ☐ | Item | Command / check | Pass condition |
|---|---|---|---|
| ☐ | API key present | key is in the gitignored `.env` as `ANTHROPIC_API_KEY=…` | non-empty; verified LIVE |
| ☐ | SB3 pinned `<2.9` | `python -c "import stable_baselines3 as s; print(s.__version__)"` | `2.8.0` (NOT 2.9.0 — see RUN_READINESS gotcha 6) |
| ☐ | Full suite green | `make test` | all green (skip heavy-dep import-error tests = env, not code) |
| ☐ | Free ~8 GB RAM | close other apps (browsers, IDE extras) | ≥ ~12 GB free → the single biggest practical RAM lever |
| ☐ | Phase-0 `m` measured | `make smoke` (≈30 min; see Step 3a) | GREEN; `m` (min/50k) recorded in `docs/DECISION_LOG.md` |
| ☐ | Amendments ratified | R21–R45 (incl. R21 reflect-on-best, R22 λ=0, R23 TF32, R24 parallel headline, R32 `placebo_shuffled` 5th LLM arm, R44 univ3 panel, R43 single-split, R45 prediction table), + D2/R16–R20 in `PREREGISTRATION.md` + `config/preregistration.yaml`, dated **before** freeze | `make freeze-check` green |
| ☐ | Platform decided | laptop (free; ~2.6 d core, ~180 GPU-hr) **or** rented 4090 (~13 h core, ~$18–35 Opus API) | recorded |
| ☐ | Reflect protocol RECORDED | **parallel reflect-on-best** (`--search-gpu 2`, R24); serial (`--search-gpu 0`) = de-risked fallback | `headline_reflect_protocol: parallel_reflect_on_best` |

> On the **rented 4090**, set `auto_shutdown_on_complete: true` (already in `config/campaign.yaml`)
> and use a spot/interruptible instance; the campaign is `--resume`-safe so an interruption is
> harmless and you never pay for idle time. On the **laptop**, pass `--no-shutdown`.

---

## 1. FREEZE the pre-registration (the gate for everything below)

**Do this first and do not skip it.** Full procedure is in `docs/FREEZE_RUNBOOK.md`; the operational
summary:

```bash
# 1a. Dry-verify prose<->yaml + Phase-0 marker + recompute the hash (NO writes).
make freeze-check                  # == python scripts/freeze.py --check
```
**Expected:** `Phase-0 precondition MET: …`, a list of `OK  …` consistency lines (seeds [0..29],
testing_family m=6, sesoi, equivalence_margin, grid_bps, λ=0/R22, tf32/R23, reflect_protocol/R21),
and `canonical SHA-256: <hash>` with `recorded freeze_hash: null (not yet frozen — expected)`.
**GO/NO-GO:** exit code **0**. Any `FAILED` (a prose↔yaml mismatch, or a missing Phase-0 marker)
→ **STOP**, fix the named field in `PREREGISTRATION.md` / `config/*.yaml`, re-run. Do not freeze on a
red check.

```bash
# 1b. Review exactly what will be locked, then run the REAL freeze (user-only, once).
git diff PREREGISTRATION.md config/
make test                          # green gate before the freeze commit
git add PREREGISTRATION.md config/ ; git commit -m "Freeze pre-registration v1.0"
make freeze                        # == python scripts/freeze.py  (WRITE path)
```
**Expected:** `[freeze] FROZEN. SHA-256 <hash>`, a UTC + git SHA line, a signed/annotated tag
`prereg-v1.0`, and an OTS line (skipped cleanly if `ots` absent). It flips `frozen: true` +
`freeze_hash: <hash>` in `config/preregistration.yaml` and appends the FREEZE-DONE entry to
`docs/DECISION_LOG.md`.
**GO/NO-GO:** `freeze_hash` is now set and `make freeze-check` reports `MATCHES`. Record the hash in
the `PREREGISTRATION.md` freeze-record table and notify the supervisor (template in FREEZE_RUNBOOK
Step 8). **Abort rule:** if the `git diff` at 1b surprises you, stop — nothing is locked until the
commit.

> After this point, any change to a frozen artifact is a **deviation** requiring a dated amendment +
> supervisor note + dissertation disclosure. `make freeze-check` becomes a permanent CI drift guard
> (it fails if any hashed file changes).

---

## 2. Capture the run environment (provenance)

```bash
python scripts/capture_env.py --run-dir outputs/campaign --seed 0
```
**Expected:** writes `outputs/campaign/env.json` (full `pip freeze`-equiv, nvidia-smi driver line,
`torch.version.cuda`, cuDNN, determinism knobs `CUBLAS_WORKSPACE_CONFIG`/`PYTHONHASHSEED`, seed).
**GO/NO-GO:** file exists and lists `torch 2.6.0+cu124` (GPU box) or the CPU build (laptop dev). This
is the reproducibility anchor for the whole run — capture it **before** training starts.

---

## 3. Keyless dry-run + the V-gates (NO crashes, NO API spend)

Every gate below uses the **stub** author (Pass A) or a synthetic panel — none burns the
`ANTHROPIC_API_KEY`. The full V1–V6 protocol lives in the master plan §5; this is the operational
sequence. **All of V1–V6 must be green before the real Opus run.**

### 3a. Phase-0 smoke (V1 prerequisite — measures `m`, proves training)
```bash
make smoke                         # python scripts/smoke_test.py  (real _univ3 slice, SAC+TQC)
# laptop fast variant if the real slice is slow:  python scripts/smoke_test.py --synthetic
```
**Expected:** `STATUS: GREEN`; `measured m (min/50k-run): <lo>–<hi>` printed; per-algo
`OK obs_dim=1893 … steps/s … ~<m> min/50k … critic_loss …`.
**GO/NO-GO:** **GREEN** (both SAC + TQC train, final critic loss finite). AMBER (one algo / non-finite
loss) → investigate before proceeding. RED (env won't build/step) → **STOP**. Record `m` and the
DECISION_LOG entry id (the freeze precondition reads it).

### 3b. V1 — full test suite
```bash
make test
```
**Expected:** every subsystem green. **GO/NO-GO:** all green (env-only import-error skips are fine).

### 3c. V2 — keyless dry-run of the full 4-stage pipeline
```bash
python scripts/run_campaign.py --dry-run
```
**Expected:** banner `DRY RUN — 1 LLM arm x 2 candidates x 1 seed on a synthetic panel (stub)`;
the SEARCH→SELECT→FREEZE→TEST pipeline runs end-to-end into `outputs/campaign_dryrun/`; prints
`windows train=… val=… test=…` and `distributional: tested (1)`. **The frozen/test desync guard and
the once-only test touch execute on real (fake-trainer-free here is fine) plumbing.**
**GO/NO-GO:** exits 0, `outputs/campaign_dryrun/campaign_summary.json` written, status `tested`.
A `winner_not_testable` here = a stub producing a comment-only reward (expected for some stubs) is
acceptable for the dry-run; a crash/traceback is **NO-GO**.

### 3d. V3 — live parallel smoke / load test (the "4 workers is safe" proof)
```bash
python scripts/run_prototype.py --parallel --synthetic --gpu 4 --pass A --arms distributional
```
**Expected:** 4 workers spawn, train, and archive on the synthetic panel with **no OOM / no CUDA
error**; the `--parallel` scheduler's `ParallelMonitor` streams per-step events. Watch peak RAM/VRAM
in a second terminal (Step 5).
**GO/NO-GO:** all candidates complete, **no `failure_wave` anomaly**, peak RAM well under 100%. If
n_gpu=4 OOMs here it will OOM the real run → drop to `--gpu 3` (the measured-safe count) or free more
RAM. (Reference: a prior n_gpu=4 GPU smoke ran 8/8 seeds, 0 failed, peak RAM 51.7%, VRAM reclaimed to
220 MiB.)

### 3e. V4 — manual-recycle soak (proves no RSS creep across batches)
Run ~24 synthetic candidates at n_gpu=4 and watch RSS stay flat across pool batches (the manual
`run_recycling` tears down + recreates the `DevicePool` every `recycle_every` tasks so the OS
reclaims fragmented heap). Use the `--parallel --synthetic` path with enough candidates to cross ≥2
batches; monitor RSS for ~20 min.
**GO/NO-GO:** RSS oscillates **flat** (drops one buffer at each completion), no monotonic climb to
~90%. The in-process `del+gc` fix in `train_candidate` is the primary reclaim; manual pool recycling
is the cross-batch backstop (`max_tasks_per_child` is **disabled** — it DEADLOCKS on Windows spawn
across all Pythons 3.11–3.14).

### 3f. V5 — resume / idempotency
Kill a `--synthetic` run mid-way, then re-launch with `--resume`.
**Expected:** completed `(arm, seed)` test ids are skipped (loaded from `outputs/.../test/<arm>`);
a frozen winner already on disk is **loaded, not re-searched** (re-search would be non-deterministic
and could swap the winner → the desync guard would then fire). No duplicate training.
**GO/NO-GO:** no re-search of frozen arms, no duplicate seeds, no desync error.

### 3g. V6 — determinism
Re-run the same seed on the synthetic path twice.
**Expected:** the same seed → the same per-seed test record (statistical, archive-replayable; TF32 is
now a single config-driven setting applied identically to serial/SEARCH/TEST per R23).
**GO/NO-GO:** per-seed records match within determinism tolerance.

**V-GATE SUMMARY — proceed to Step 4 only when V1–V6 are all green.** Any OOM at n_gpu=4 → the plan
degrades gracefully to n_gpu=3; it never crashes.

---

## 4. Set workers (n_gpu / search-gpu) and launch the real SEARCH+TEST campaign

### 4a. Decide the worker counts (the resource knobs)
- **TEST leg parallelism — `--gpu N` (science-neutral, the clean win).** The 7×30 = 210 winner
  re-runs are embarrassingly parallel with zero reflection coupling. Laptop: `--gpu 4`. Add `--cpu 1`
  **only if** you freed the ~8 GB of other apps. **Never exceed 5 total workers** (a 5th GPU worker
  OOMs VRAM; a 6th worker OOMs RAM — this is physics, not a config knob).
- **SEARCH leg parallelism — `--search-gpu N` (HEADLINE = parallel reflect-on-best, R24).** The recorded
  headline (`headline_reflect_protocol: parallel_reflect_on_best`) routes SEARCH through the
  within-generation/cross-arm scheduler with **reflect-on-best** (Eureka-faithful) + the matched 50k
  buffer. **Use `--search-gpu 2`** — n_gpu≥4 is the measured search OOM (the CLI now refuses ≥4); 2 is the
  VRAM-safe count on the 6 GB 4050, and the per-arm pool teardown bounds RAM. Serial reflect-on-last
  (`--search-gpu 0`) is the documented de-risked **fallback** if the GPU-smoke (Step 3d) shows
  RAM/thermal trouble.

### 4b. Launch (one authoritative command)
```bash
# HEADLINE DATA PANEL (R44): the headline is univ3 (zero-fill / liquidate_to_cash, NO fabricated losses).
# univ3 is the loader's LIVE DEFAULT (src/data/loaders.gold_suffix), so SEARCH, SELECT, FREEZE, and TEST
# all train/evaluate on the same frozen headline panel with NO env-var override — leave the bare command.
#
# ⚠ univ4 is NOT "the tail": it is the M&A-CONTAMINATED HEAVY END of the delisting band (data-integrity
# audit 2026-06-25, ratified R44). Its frozen rf_meta_* pull carries no delisting reason/terminal, so the
# −30/−55% Shumway surcharge is applied to 100% of delistings — including premium M&A booked at a
# fabricated loss (DELL buyout, TWX→AT&T, ABMD→J&J; 3 of the 30 headline-cohort names). The HONEST tail
# instrument is the pre-registered delisting-return sensitivity BAND d∈{0,−30,−55,−100%}
# (analyze_campaign.delisting_band): univ3 (zero-fill) is the 0% end, univ4 the contaminated heavy end,
# and the truth lies INSIDE — the full sweep moves pooled test CVaR-5% only ~2% (−0.0493→−0.0504), so the
# H2 tail ORDERING is invariant across it. Report the band; do NOT present univ4 alone as the tail. The
# CORRECT panel is univ4r (reason-gated re-pull, docs/DATA_REPULL_DELISTING.md) — recommended/optional.
# univ3 is integrity-screened via univ3s.
#
# LAPTOP HEADLINE (R24: parallel reflect-on-best search @ n_gpu=2 + 4-way recycled TEST leg).
# PREREQUISITE: the single-arm 50k GPU-smoke (Step 3d) is GREEN. --resume makes it crash-safe.
python scripts/run_campaign.py --search-gpu 2 --gpu 4 --h3-singleshot --resume --no-shutdown
#   add --cpu 1 only if other apps are closed (never exceed 5 total workers).
#   --h3-singleshot appends the H3 single-shot control (R30); H1 baselines run automatically (config h1_baselines).

# LAPTOP FALLBACK (serial reflect-on-last search; if the GPU-smoke shows RAM/thermal trouble):
python scripts/run_campaign.py --gpu 4 --resume --no-shutdown

# RENTED 4090 (24 GB VRAM has headroom; auto-shutdown ON via config; spot + checkpoint):
python scripts/run_campaign.py --search-gpu 8 --gpu 8 --h3-singleshot --resume
```

**Estimated wall-clock — core ~600 runs** (210 search + 210 winner-test + 120 H1 + 60 H3 — the 7th arm `placebo_shuffled` (R32) adds +60 over the prior 540; per-run `m`≈**18 min**/50k on the 4050, **11 min** on a 4090 — the Step-3d GPU-smoke confirms `m`):
- **Laptop** (search n_gpu=2 / test n_gpu=4): ~31.5 h search + ~25 h test + ~6.75 h H3 = **≈ 2.6 days** (≈ 3–3.5 d under thermal throttle); **~180 GPU-hr**.
- **Rented 4090** (n_gpu=8): **≈ 13 h (½ day)**; **~110 GPU-hr**.
- **No GPU-hour cap** (the `hard_budget_gpu_hours` limit was removed 2026-06-28 — never code-enforced). The ~110–180 GPU-hr above are *estimates*, not a budget. The optional PPO/TD3 algo-robustness (~+120 runs) can be INCLUDED if wanted — it is now a scope/time choice, not a budget constraint. Opus API ≈ **$18–35** (240 reward-design calls). The campaign runs on the loader default **univ3** (the headline panel, R44 — zero-fill, no fabricated losses; no env override needed).
Run it **backgrounded** (e.g. detached / `nohup`-style) so you can monitor in another terminal. The
driver `preload()`s pyarrow before torch (gold-parquet ABI guard) and `load_env()`s the key.

**Expected banner:**
```
[run_campaign] HEADLINE single-split: arms=[distributional, scalar, placebo, scalar_cvar5,
  placebo_shuffled, random_search, bayes_opt] seeds=[0..29] search_seed=0 candidates=30 steps=50000
  gens=6 pass=B provider=anthropic embargo=21 resume=False -> outputs/campaign
```
**GO/NO-GO (launch sanity, first ~2 min):** the banner shows `steps=50000`, `provider=anthropic`,
`candidates=30`, all 7 arms (the **frozen H2-family guard** raises `SystemExit` if the arms drift from
the pre-registered contrast family — that is a hard stop, fix `config/campaign.yaml` arms). The
`outputs/campaign/{search,frozen,test}` dirs are created and `progress.json` appears. If the banner
prints the wrong steps/provider/arms, **kill it immediately** — do not let a mis-configured paid run
proceed.

---

## 5. MONITOR the run (continuous, through transitions)

In a second terminal:
```bash
python scripts/monitor.py outputs/campaign                 # live dashboard (~2 Hz)
python scripts/monitor.py outputs/campaign --once          # one scriptable text snapshot
python scripts/monitor.py outputs/campaign --stale-secs 600 # tune the silent-hang threshold (default 300 s)
# Remote/unattended (rented GPU over SSH): push a phone alert on done/error/stall. OFF by default,
# stdlib-only, READ-ONLY side-channel (sends run STATUS, never data). Use a PRIVATE ntfy topic.
python scripts/monitor.py outputs/campaign --notify https://ntfy.sh/<your-private-topic>
```
**Expected:** multi-level progress (Arms ▸ Candidates ▸ Training steps), latest train metrics (fps,
critic/actor loss, ent_coef, ep_rew_mean), GPU%/VRAM/temp, CPU%/RAM%/RSS, ETA, an **ANOMALIES**
count grouped by kind (red border if non-zero), and a live **LLM** token-spend + estimated-USD line.
The `--parallel`/`--search-gpu` paths show an `active` row (N candidates training concurrently). If
`progress.json` stops being rewritten while the run is still "running" (deadlock / wedged CUDA / OOM
kill), a loud **STALE** banner fires (silent-hang detection) — the dashboard no longer shows a hung run
as healthy. Run the campaign inside `tmux`/`screen` so an SSH drop doesn't kill it; reattach anytime.

**What to watch + the gates:**
| Signal | Healthy | Action if not |
|---|---|---|
| **RAM %** | flat, < ~90% (laptop) | climbing toward ~92% → **transition-wave OOM risk**; if it crosses, the run will degrade — drop n_gpu next launch (see §6 OOM) |
| **VRAM** | reclaims between batches (recycling holds) | monotonic climb → recycling not firing → restart, drop n_gpu |
| **ANOMALIES** | 0 | `failure_wave` / `critic_explosion` → note it (PopArt is absent; critic explosions are a known prototype phenomenon — record, they do not abort the run); a parallel TEST `WARNING: … failed seed(s)` is surfaced in the driver log |
| **GPU temp** | within thermal limits | sustained throttling over the ~2.6-day laptop core → §6 thermal |
| **fps / ETA** | stable | collapsing fps → thermal throttle or swapping (RAM) |

Anomaly/event detail is also in `outputs/campaign/{events.jsonl,anomalies.jsonl}` (tailed by the
dashboard). **Monitor THROUGH candidate transitions**, not just the clean start — the n_gpu=4 OOM
risk is the simultaneous fresh-buffer allocation when a generation's candidates finish together
(steady-state probes miss it).

---

## 6. CONTINGENCY playbook (run-day failures → recovery)

Every contingency below is **resume-safe**: re-launch with `--resume` and completed `(arm, seed)`
test ids + frozen winners are skipped, so no work is redone and no paid SEARCH budget is re-burned.

| Failure | Symptom | Recovery |
|---|---|---|
| **OOM (RAM) at n_gpu=4** | RAM → ~92%, `MemoryError` cascade / `failure_wave` anomaly | Kill; re-launch with **`--gpu 3`** (the measured-safe count) `--resume`; close more apps; drop `--cpu 1` if set. Root cause is the transition wave, not steady state. |
| **OOM (VRAM)** | CUDA out-of-memory on a 5th worker | You exceeded the VRAM ceiling — n_gpu **must be ≤ 4** on the 4050. Re-launch `--gpu 4 --resume`. |
| **Thermal throttle** | GPU temp pinned, fps collapses over hours | Run on a cooling stand / cooler ambient; or move the campaign to the **rented 4090** (much faster + avoids the laptop thermal soak) — same frozen config, `--resume` from the partial archive. |
| **Crash / interruption / spot reclaim** | process dies, machine reboots | Re-launch the **identical** command `+ --resume`. Idempotent: skips done test ids, loads existing frozen winners (never re-searches them), preserves the select→freeze→test chain. |
| **A single worker dies mid-run** | one candidate/seed errors | `train_candidate` catches per-candidate exceptions (the pool survives); the parallel TEST driver surfaces `n_failed` + the first error in the log. The desync guard prevents a silent winner swap. Finish the run, then `--resume` to fill the failed seeds. |
| **Slow RSS creep** | RSS climbs over tens of minutes at any n_gpu | The in-process `del+gc` fix should hold it flat; if it still creeps, the manual pool-recycling (`recycle_every`) is the backstop. Do **not** enable `max_tasks_per_child` (deadlocks on Windows spawn). |
| **Opus rate-limit / 429** | SEARCH stalls on LLM calls; events log shows API errors | The author calls are in the SEARCH stage only (180 candidate authorings); transient 429s back off. If sustained, pause and resume later (SEARCH archives per candidate; `--resume` continues). The TEST leg uses no API. |
| **Cost / GPU-hour** | informational only — **NO cap** | There is **no GPU-hour budget** (`hard_budget_gpu_hours` removed 2026-06-28; never code-enforced, and `auto_shutdown_on_complete` is a verified no-op — it does NOT power off). The ≈110 GPU-hr (4090) figure is an *estimate*. To stop early, kill + `--resume` later — no idle spend. |
| **`winner_not_testable` for an arm** | summary status, not a crash | The SELECTED winner's `reward_source` was a non-executable comment stub (e.g. a `random_search`/`bayes_opt` coeff-comment). It is FLAGGED, not fabricated; the other arms still test. Investigate that arm's archive; it does not block the headline H2 family if the H2 arms tested. |
| **Frozen/test desync error** | `ValueError: frozen winner hash mismatch … (frozen/test desync guard)` | A re-searched resume swapped the winner. **STOP** — do not bypass. Restore the frozen record or re-run that arm cleanly so frozen and test describe the same reward. This guard is protecting headline integrity. |

---

## 7. SELECT / FREEZE / TEST — what the driver does (no manual step)

These three stages are **internal** to `run_campaign.py` (no separate command); this section is the
operator's mental model + the verification.

- **SELECT** — per arm, the winner is the candidate with max **validation Deflated Sharpe**
  (`metrics['val_fitness']`, via `select_winner` → the same rule as `analyze_results._winner`).
  Selection **never** builds a test-window bundle (the seal holds structurally). λ=0 (R22): pure
  validation-DSR, no tail penalty in selection — the tail is the feedback channel's job, measured on
  the sealed leg.
- **FREEZE** — the winner's `reward_source` + `reward_source_hash` are persisted with a `frozen: True`
  marker to `outputs/campaign/frozen/<arm>-winner/` (replay-from-archive).
- **TEST** — the FROZEN winner reward is re-instantiated through the sandbox (`validate_once`, same
  AST allowlist gate), a **3-window** bundle is built (the only place a `test_window` exists), the
  fixed agent is re-trained per seed at the **matched 50k budget**, and `bundle.test_series(policy)` is
  touched **EXACTLY ONCE** per (arm, seed). Each record carries `val_fitness`, the NET
  `test_returns` + its GROSS/TURNOVER decomposition (for the cost sweep), `test_sharpe`, `test_cvar05`.

**Verification after the run completes:**
```bash
python scripts/monitor.py outputs/campaign --once          # phase=done, anomalies summary
cat outputs/campaign/campaign_summary.json                 # per-arm status + windows
```
**Expected:** `campaign_summary.json` lists every arm as `tested` with `n_seeds_written: 30` (or the
resumed remainder), plus the resolved `train_window`/`val_window`/`test_window`. The leakage-safe
purge is `max(embargo=21, lookback=60) = 60` sessions at each boundary (R18). **GO/NO-GO:** all H2
arms (`distributional`, `scalar`, `placebo`, `scalar_cvar5`) `tested` with the full seed count.

---

## 8. ANALYZE — the headline report

```bash
# R44: analyze on the SAME headline panel the campaign trained on — univ3, the loader default (zero-fill,
# no fabricated losses). The panel-dependent floor + the delisting-return band both load via gold_suffix(),
# which already defaults to univ3, so NO env override is needed here.
python scripts/analyze_campaign.py --root outputs/campaign --single-shot-root outputs/campaign/test_h3_singleshot/distributional
#   (--root defaults to outputs/campaign; --single-shot-root feeds the H3 single-shot test leg into the H3 difference test.
#    Emits: PBO/DSR, the H2-RA + H2-Tail two-tier verdict, H1/H3/H4, the secondaries, the floor + R20 rf-robustness,
#    and the R44 delisting-return sensitivity band (out["delisting_band"]) — univ3 is the 0% end, univ4r the correct re-pull.)
```
> **Note:** `make analyze` runs `scripts/analyze_results.py` — the **1-seed DIRECTIONAL prototype**
> go/no-go, NOT the campaign headline. For the campaign you must call `scripts/analyze_campaign.py`
> directly (as above). Do not substitute `make analyze` here.
This loads the WHOLE campaign tree (search + test + frozen legs from the one root) and writes
`outputs/campaign/campaign_overfitting.{md,json}`. It computes, in one pass:

1. **PBO / CSCV per arm** (the PRIMARY overfitting guard, `var`-free) — full enumeration C(16,8) =
   12,870 splits at the frozen `n_blocks=16` (deterministic, not a random subsample). PBO near 0 =
   in-sample-best stays good OOS; near/above 0.5 = severe overfitting.
2. **Winner Deflated Sharpe** (SECONDARY) — canonical cross-trial variance vs the proxy.
3. **H2 conjunction (the HEADLINE)** — distributional must beat **scalar AND placebo AND
   scalar_cvar5** on the held-out Sharpe leg, per-seed **rliable** inference (per-seed Sharpe/CVaR →
   IQM → paired stratified bootstrap over the shared training seeds), **BH-corrected** at q=0.05
   across the frozen m=6 family. A **fail-loud assert** fires if the realized family ≠ the frozen one
   (R13). `H2_supported` is `True` iff all three legs reject in the predicted direction after
   correction.
4. **DeMiguel benchmark floor** — 8 published allocators (1/N + 7) rolled through the IDENTICAL costed
   test env; the winner's test-DSR (median-per-seed) must strictly beat the best benchmark's. Report-
   only; never re-selects. Plus the market reference (EW universe, FRED DGS3MO rf) and the winner's
   beta/alpha/IR.
5. **R20 rf robustness** — does the H2 Sharpe conjunction survive on EXCESS returns (r − DGS3MO)? The
   frozen rf=0 headline is unchanged; this is the additive sensitivity.

**Expected stdout:** per-arm `PBO=… (n=30, T=…, ok)`, per-arm `DSR canonical=… vs proxy=…`, and
`H2 (distributional feedback, BH): SUPPORTED | NOT supported` with per-leg `leg_supported=… p=…`.
**GO/NO-GO:** the report is produced and the H2 verdict prints. **Both outcomes are publishable** —
the pre-registered null is bankable. Do **not** tweak anything to change the verdict; record it.

> **Headline inference is PER-SEED rliable — never revert to seed-averaging** (it collapses the
> across-seed variance ~N× and is anti-conservative, ~21% true-null rejection; this was the #18 audit
> fix, R16). The seed-averaged path survives only for descriptive display / the cost-sweep parallel.

---

## 9. SECONDARY analyses (run after the headline)

### 9a. Cost-robustness sweep (WIRED — `scripts/cost_sweep.py`, R15)
```bash
python scripts/cost_sweep.py --root outputs/campaign/test
#   --grid-bps 0,5,10,25,50   (default reads config/environment.yaml costs.grid_bps)
```
Re-prices the FROZEN winners across the bps grid **without retraining** (analytic
`net_c = gross − c·turnover` from the persisted decomposition; the test leg stays touched once).
Writes the winner-identity-vs-cost table to `outputs/campaign/cost_sweep/`. **Question it answers:**
does the tail-aware arm still win when charged more to trade, or does it win merely by trading less?
**GO/NO-GO:** a table with one row per cost level; the headline arm's win is not knocked out by higher
costs (or, if it is, that is the reported finding).

### 9b. Power analysis (WIRED — `scripts/power_analysis.py`)
```bash
make power                         # python scripts/power_analysis.py  -> docs/POWER_ANALYSIS.md
```
Recompute power for the frozen family (m=6) at the realized seed count and SESOI/equivalence margins.
Run for the write-up's power statement; not a go/no-go.

### 9c. PPO/TD3 algorithm-robustness on the winners (frozen design, manual)
The frozen plan includes re-running the winners under PPO/TD3 (2 algos × winners × 30 seeds) as an
algorithm-robustness check. This reuses the winner-re-run machinery on the frozen rewards; schedule
it after the headline if the algorithm-sensitivity claim is needed. (Small models, but ×30 seeds.)

### 9d. Secondary families NOT YET WIRED — attribution / variance / contamination
These three secondary families are **planned but have no entry-point script yet** (no
`attribution`/`variance`/`contamination` script exists in `scripts/` — verified). They are
**to be wired** before they can be run:
- **Attribution** — decomposing the H2 edge into its drivers (e.g. turnover/vol/tail contribution to
  the realized Sharpe gap). Consumes the per-(arm, seed) test records + the gross/turnover
  decomposition already persisted.
- **Variance decomposition** — across-seed vs across-candidate variance of the headline metric (the
  rliable across-seed variance is already carried by the per-seed bootstrap; this would report it
  explicitly).
- **Contamination** — LLM training-data contamination checks on the authored rewards (e.g. are the
  Opus-authored reward bodies near-duplicates of known published reward code?).

**Action:** treat these as a post-run wiring task. Each must read results ONLY through
`src.io.results` (audit C-1), operate on the existing archive (no retraining, no second test touch),
and — if it touches the frozen family — carry the same fail-loud family-equals-frozen guard. Until
wired, they are explicitly out of scope for run day; do not block the headline on them.

---

## 10. Post-run wrap-up checklist

| ☐ | Item | Check |
|---|---|---|
| ☐ | `make freeze-check` still `MATCHES` | the frozen artifacts were not mutated during the run |
| ☐ | `campaign_summary.json` complete | all H2 arms `tested`, full seed count |
| ☐ | `env.json` captured | provenance anchored to the run dir |
| ☐ | Headline report written | `campaign_overfitting.{md,json}` (PBO + DSR + H2 + floor + rf) |
| ☐ | Cost sweep written | `cost_sweep/` table |
| ☐ | Anomalies reviewed | `anomalies.jsonl` (critic explosions noted as a known limitation; PopArt absent) |
| ☐ | Rented GPU shut down | auto-shutdown fired (or manually stopped) — no idle spend |
| ☐ | Verdict recorded | H2 supported/null + the per-leg p-values, into the DECISION_LOG / write-up notes |

---

### One-screen run-day sequence (copy/paste order)
```bash
# 0. Pre-flight: key present, SB3==2.8.0, free RAM, make test green.
make freeze-check                                   # 1a  (must be exit 0)
git diff PREREGISTRATION.md config/ ; make test
git add PREREGISTRATION.md config/ ; git commit -m "Freeze pre-registration v1.0"
make freeze                                         # 1b  (THE freeze — user, once)
python scripts/capture_env.py --run-dir outputs/campaign --seed 0   # 2
make smoke                                          # 3a  (GREEN; record m)
make test                                           # 3b
python scripts/run_campaign.py --dry-run            # 3c  (V2, keyless)
python scripts/run_prototype.py --parallel --synthetic --gpu 4 --pass A --arms distributional  # 3d (V3)
# ... V4 soak / V5 resume / V6 determinism on the synthetic path ...
# R44: headline = univ3 (loader DEFAULT — zero-fill, no fabricated losses); NO env override (search+test+analyze).
python scripts/run_campaign.py --search-gpu 2 --gpu 4 --h3-singleshot --resume --no-shutdown  # 4  (REAL run, R24 parallel headline + H3; +--cpu 1 if apps closed)
python scripts/monitor.py outputs/campaign              # 5  (second terminal; watch RAM through transitions)
python scripts/analyze_campaign.py --root outputs/campaign --single-shot-root outputs/campaign/test_h3_singleshot/distributional  # 8  (PBO + DSR + H2-RA/Tail + H1/H3/H4 + floor + rf + R44 delisting band) — NOT `make analyze`
python scripts/cost_sweep.py --root outputs/campaign/test   # 9a
make power                                               # 9b
```
