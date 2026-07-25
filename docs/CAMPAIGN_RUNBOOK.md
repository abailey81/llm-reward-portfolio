# CAMPAIGN RUNBOOK — the single operational document for run day

> ⚠ **SUPERSEDED (2026-07-22, row 30k): the operative runbook is `docs/CAMPAIGN_DAY_RUNBOOK_2026-07-13.md`.**
> Numbers below are v1-era: B\* is now **400,000** (R77, not 200k) and the seed plan is the E1 tiered
> ladder [30..568] (not the fixed sets below). Do NOT use this file's GO/NO-GO banner values —
> an operator checking `steps=200000` here would KILL a correct 400k launch (the M05 class).


> **⚠ CURRENT SUBSTRATE (2026-07-13, ADR-053).** The confirmatory campaign runs on the **UCL Myriad HPC
> cluster** (SGE arrays; `scripts/run_campaign_cluster.py`) — this is the PRIMARY venue. The laptop path
> described in this runbook is the **CERTIFIED FALLBACK**, not the primary substrate (cross-substrate
> science parity is certified — same primitives, `src/cluster/`). **Run-day operators should use
> `docs/CAMPAIGN_DAY_RUNBOOK_2026-07-13.md`** as the operative launch document; this file's laptop
> sequence applies only when training on the fallback box.
>
> **⚠ SUPERSEDED COMPUTE FRAMING (2026-07-01, ADR-040).** The campaign runs **LAPTOP-ONLY on the owned RTX 4050**
> — no rented RTX 4090 / cloud (**no cloud-compute budget**; a WSL2/GPU speed path was also probed and rejected
> after systematic install failure). Wherever this runbook says "rented 4090", "`--gpu 8`",
> "n_gpu=4", or `auto_shutdown_on_complete`, use the **laptop path: n_gpu 2–3, capped buffer, ~2–3 weeks**
> (see `docs/CAMPAIGN_DESIGN_AND_EXECUTION_PLAN.md` + ADR-040). The ordered freeze→search→test→analyze sequence
> below is otherwise current.

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
the laptop TEST-leg ceiling is **n_gpu = 3** GPU workers (proven-safe 2–3; VRAM-bound) + at most 1 CPU
worker (RAM-bound); **`--gpu` and `--search-gpu` ≥ 4 are REFUSED by the CLI** (`run_campaign.py` raises
`SystemExit`; `preflight.check_vram` FAILs it) because n_gpu=4 OOMs the 6 GiB RTX-4050 VRAM ceiling.
**Compute — authoritative source `docs/COMPUTE_AND_TRAINING_TIME.md`
(post-amendment D2, winner seeds 5→30; 7 arms after R32 added `placebo_shuffled`):** the **7-arm core
≈ 600 runs** (210 search + 210 winner-test + 120 H1 + 60 H3) ≈ **2.6 days on the laptop at n_gpu=3**
(⚠ HISTORICAL 50k/30-seed estimate — the real campaign is **~23 days** at B\*=200k + the ~350-seed
σ_D-driven amendment; see the superseded-wall-clock note in §4 below) / **~13 h on a rented 4090; ~180 GPU-hr** — consistent with the "Estimated wall-clock — core
~600 runs" callout in §4 below. The optional PPO/TD3 algorithm-robustness (~+120 runs) is OPTIONAL on
scope/time grounds (there is **no GPU-hour cap** — `hard_budget_gpu_hours` was removed 2026-06-28; the
GPU-hr figures are estimates, not a limit). The run-count recorded at freeze **is** the DSR trial count, so take it from the COMPUTE doc, not a
round number. `run_campaign.py` writes to `outputs/campaign/{search,frozen,test}` and
`campaign_summary.json`. The campaign reward-author is **Claude Opus 5** (`config/campaign.yaml`,
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
| ☐ | Amendments ratified | R21–**R73** (incl. R21 reflect-on-best, R22 λ=0, R23 TF32, R24 parallel headline, R32 `placebo_shuffled` 5th LLM arm, R43 single-split, R44 univ3 panel — superseded by **R73 Split C + univ5**, 2026-07-02 — R45 prediction table), + D2/R16–R20 in `PREREGISTRATION.md` + `config/preregistration.yaml`, dated **before** freeze | `make freeze-check` green |
| ☐ | Platform decided | **laptop-only (ADR-040, 2026-06-30/07-01)** — the "rented 4090" option is SUPERSEDED | recorded |
| ☐ | Reflect protocol RECORDED | **SERIAL reflect-on-best** (`--search-gpu 0`, the default; ratified 2026-07-01 superseding R24, label corrected 2026-07-02 — the serial loop's M5 reflection seed IS the generation's best) ; parallel best-of-generation (`--search-gpu 2`) = robustness variant | `headline_reflect_protocol: serial_reflect_on_best` |

> On the **rented 4090**, set `auto_shutdown_on_complete: true` (already in `config/campaign.yaml`)
> and use a spot/interruptible instance; the campaign is `--resume`-safe so an interruption is
> harmless and you never pay for idle time. On the **laptop**, pass `--no-shutdown`.

### 0b. RUN-DAY machine checklist (ops audit 2026-07-02 — the unattended-Windows-laptop hardening)

Do these **on run day, in order**, before Step 1. They close the operational gaps that kill a 2-3-week
unattended run from OUTSIDE the code (OS reboots, thermals, power policy, disk, dead alerting).

| ☐ | Item | Command / where | Why / pass condition |
|---|---|---|---|
| ☐ | **Pause Windows Updates ~5 weeks** (m13/C2) | Settings → Windows Update → Pause updates → pick the max horizon covering the whole run + analysis buffer | a forced patch reboot is the single most likely exogenous interrupt; `preflight` WARNs if not paused and **FAILs on a pending reboot** (reboot first, then re-run preflight) |
| ☐ | **Register the ONSTART re-entry task** (C2) | `powershell -ExecutionPolicy Bypass -File scripts\install_onstart_task.ps1` (elevated, once; remove post-run with `scripts\uninstall_onstart_task.ps1`) | any reboot that DOES happen re-enters `supervisor.py → run_campaign --resume` automatically instead of staying down until a human notices; log at `outputs\campaign\onstart_task.log` |
| ☐ | **P-core placement active** (ADR-052) | `config/campaign.yaml compute.worker_cpu_affinity: "0-11"` (ON) — the driver + every worker pin to the i7-13620H's P-cores, ABOVE_NORMAL, EcoQoS off | result-neutral placement; E-cores 12-15 absorb the OS/monitors; verify with Task Manager > Details > python.exe affinity once the run starts |
| ☐ | **Verify the Turbo power limit after EVERY reboot** (m15) | `nvidia-smi -q -d POWER` → check the enforced limit is the Turbo ~140 W (not the ~95 W Performance-mode cap) | **Armoury Crate INSTALLED 2026-07-02** (was missing — Fn+F5 did nothing and the firmware exposes no public WMI path for modes; two burn probes proved the ~95 W Performance cap). Observed 2026-07-02: the app **re-applies Turbo automatically at boot** (survived a reboot at 140 W) — so this row is now VERIFY-only; if it ever reads ~95 W, open Armoury Crate → Turbo. Note the app also installs its own "Turbo" power scheme — re-check AC-sleep=Never on it (§K) after ASUS updates |
| ☐ | **High-Performance power plan + GPU clock lock after EVERY reboot** (perf audit 2026-07-02) | `powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c` then `nvidia-smi -lgc 2200,2560`; verify with `nvidia-smi --query-gpu=clocks.sm --format=csv` (~2205 MHz under load) | the SAC step is overhead-bound (~58% dead time between kernel bursts) so the GPU P-state hunts down between bursts — the Balanced plan was observed training at 675 MHz/10.9 W. The lock kills P-state hunting (+20-28% single-stream); **resets on reboot** like Turbo. Post-run revert: `nvidia-smi -rgc` + Balanced plan |
| ☐ | **Lid-close action = Do Nothing (plugged in)** (M8) | `powercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 0 ; powercfg /SetActive SCHEME_CURRENT` (or Control Panel → Power Options → lid settings) | closing the lid must not sleep the host; pair with the §K sleep/hibernate disables (`powercfg /change standby-timeout-ac 0` etc.) and keep it on AC |
| ☐ | **Defender stays off / excluded for the repo** (m14) | verified 2026-07-02: the WinDefend service is **Stopped (Disabled)** on this box (real-time protection off, no other AV registered) → no scan tax, nothing to do. `Get-Service WinDefend` to re-check | IF Defender is ever re-enabled (a major Windows upgrade can do this): `Add-MpPreference -ExclusionPath "c:\Users\User\Desktop\dissertation_papers","D:\tmp"` from an ADMIN shell — real-time scanning taxes the thousands of archive writes and can transiently lock files mid-rename (the `0x800106ba` error from Add-MpPreference just means the service is down = nothing to exclude) |
| ☐ | **Free ≥ 20 GB on C: and gate on it** (m14) | free the space, then `python scripts/preflight.py --gpu 2 --min-disk-gb 20 --probe` | C: also hosts the pagefile — a nearly-full system drive stalls/OOMs the whole host, not just the archive; 20 GB covers archive growth + pagefile headroom. `--probe` makes the REAL 1-token key/credit check (M9) |
| ☐ | **tenacity present** (C1) | covered by the same preflight run — the `retry_layer` line must be `[ OK ]` | without tenacity every Anthropic call is single-attempt (no 429/5xx backoff): the #1 run-killer; the gauntlet hard-FAILs it |
| ☐ | **Register the dead-man heartbeat** (M5b) | create a free check (period 15 min) at a healthchecks-style service, then run `powershell -ExecutionPolicy Bypass -File scripts\deadman_ping.ps1 -Url https://hc-ping.com/<uuid>` alongside the run (or schedule `-Once` every 15 min) | the ONLY alert that survives host death: `--notify` and the console die WITH the laptop; the external service pages when pings STOP (power/network/hard-hang) |
| ☐ | **Know the real progress path** (M5c) | live search telemetry = `outputs/campaign/search/progress.json` — watch with `python scripts/monitor.py outputs/campaign/search --follow-campaign` | `progress.json` is written by the SEARCH leg's monitor under `search/`, NOT at `outputs/campaign` (§5); `--follow-campaign` keeps watching across arms until `campaign_summary.json` is written |
| ☐ | **VS Code during the run: TRIMMED + agent-monitored** (2026-07-02; user decision — stays OPEN) | `.vscode/settings.json` carries the minimal-footprint config (watcher/search excludes on `outputs\`+data+venvs, Pylance indexing OFF, git autorefresh OFF, editor-tab limit 5, update churn OFF). On run day: ONE VS Code window, run "Developer: Reload Window" once so all trims take effect, keep only the agent session open | trimmed VS Code + one agent session ≈ ~2 GB — the RAM budget then reads: 15.6 total − OS ~4.2 − VS Code+agent ~2 − 3 workers ~6.3-7.5 steady ⇒ ~2-3 GB wave margin (preflight still gates ≥7.5 GB free BEFORE launch). The agent watches `search/progress.json` + supervisor log + GPU/RAM/disk and intervenes; the machine-level stack (supervisor auto-restart, ONSTART, deadman/ntfy) covers 24/7 with no session open |
| ☐ | **⚠ EXCLUSIVE-PHASE RULE during ANY farmed leg** (incident 2026-07-02: MANDATORY) | while a 3-worker farm (σ_D pilot or the campaign TEST leg) runs: **NO concurrent agent fleets, NO test-suite runs, NO parallel review workflows, NO torch-importing side processes** on this box — light reads/greps only | the 2026-07-02 σ_D crash: two review workflows (~20 concurrent agents running pytest) alongside the 3-worker farm exhausted RAM+VRAM → all 15 cells of one arm OOM-failed (MemoryError / CUDA-OOM / WinError 1450) and the IDE session died with them. The launch-time RAM gate protects LAUNCH only — nothing polices resources DURING the run; the ~2-3 GB margin belongs to the recycle waves, not to side work. `--resume` made it recoverable (6 done cells skipped, 24 re-farmed); the rule makes it not happen again |

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
make smoke                         # python scripts/smoke_test.py  (real active-suffix slice — univ5, SAC+TQC)
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
**GO/NO-GO:** exits 0, `outputs/campaign_dryrun/campaign_summary.json` written, status `tested`
(the summary now also carries `all_arms_tested: true` / `exit_code: 0` — the C3a integrity gate).
A `winner_not_testable` here = a stub producing a comment-only reward (expected for some stubs): the
gate then exits **3** with a loud INCOMPLETE table — for the DRY-RUN that specific status is
acceptable (investigate the stub, not the pipeline); a crash/traceback, or exit 3 on the REAL run,
is **NO-GO** (the supervisor treats exit 3 as a resumable failure and relaunches with `--resume`).

### 3d. V3 — live parallel smoke / load test (the "3 workers is safe" proof)
```bash
python scripts/run_prototype.py --parallel --synthetic --gpu 3 --pass A --arms distributional
```
**Expected:** 3 workers spawn, train, and archive on the synthetic panel with **no OOM / no CUDA
error**; the `--parallel` scheduler's `ParallelMonitor` streams per-step events. Watch peak RAM/VRAM
in a second terminal (Step 5).
**GO/NO-GO:** all candidates complete, **no `failure_wave` anomaly**, peak RAM well under 100%. If
n_gpu=3 OOMs here it will OOM the real run → drop to `--gpu 2` (the proven-flat count) or free more
RAM. (`--gpu 4` is not a smoke option — it OOMs the 6 GiB RTX-4050 VRAM ceiling and `run_campaign.py`
refuses it; historical note: a pre-ceiling-decision n_gpu=4 GPU smoke ran 8/8 seeds, 0 failed, peak
RAM 51.7%, VRAM reclaimed to 220 MiB, but the measured VRAM ceiling since caps the run at n_gpu 3.)

### 3e. V4 — manual-recycle soak (proves no RSS creep across batches)
Run ~24 synthetic candidates at n_gpu=3 and watch RSS stay flat across pool batches (the manual
`run_recycling` tears down + recreates the `DevicePool` every `recycle_every` tasks so the OS
reclaims fragmented heap). Use the `--parallel --synthetic` path with enough candidates to cross ≥2
batches; monitor RSS for ~20 min.
**GO/NO-GO:** RSS oscillates **flat** (drops one buffer at each completion), no monotonic climb to
~90%. The in-process `del+gc` fix in `train_candidate` is the primary reclaim; manual pool recycling
is the cross-batch backstop (`max_tasks_per_child` is **disabled** — it DEADLOCKS on Windows spawn
across all Pythons 3.11–3.14).

### 3e-bis. V4b — CRASH-INJECTION rehearsal (certify resume before the real run; AUTOMATED 2026-07-06)

The rehearsal is now ONE COMMAND (`scripts/crash_rehearsal.py`): reference run → determinism-control
run → hard TREE-kill (`taskkill /T`, pool workers included, like a real power event) at the first
archived record → `--resume` → canonical byte-compare of the resumed tree against the uninterrupted
reference (volatile fields only — wall_clock/env_fingerprint — excluded):
```bash
.venv/Scripts/python.exe scripts/crash_rehearsal.py          # exit 0 = crash-resume CERTIFIED
```
**Proof it earns its keep:** on its first real execution (2026-07-06) the rehearsal CAUGHT a genuine
resume infidelity — the Pass-A stub author drew from one sequential RNG stream, so a resume that
replayed archived candidates without consuming their draws shifted every later candidate — fixed by
making the stub a pure function of ``(seed, call_index)`` + stream-faithful ``advance()`` on replay
(real-LLM transports no-op: paid non-deterministic calls cannot be replayed by position; their
resume contract stays "archived work replays identically, un-run slots are fresh draws").
Re-certified PASS: killed at 1/6 records → resume → byte-identical archive. Also still unit-certified:
`tests/test_search.py::test_random_search_resume_reproduces_trajectory_and_skips_training` +
`::test_bayes_opt_resume_reproduces_gp_trajectory`. For extra confidence before the freeze, the
manual multi-point kill-storm under the supervisor (kill mid-search-arm / mid-generation /
mid-test-batch, verify the sentinel stays GREEN through relaunches) remains a worthwhile V4b-plus.

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

**V-GATE SUMMARY — proceed to Step 4 only when V1–V6 are all green.** Any OOM at n_gpu=3 → the plan
degrades gracefully to n_gpu=2; it never crashes. (n_gpu=4 is not on the table — the CLI refuses it.)

---

## 4. Set workers (n_gpu / search-gpu) and launch the real SEARCH+TEST campaign

### 4a. Decide the worker counts (the resource knobs)
- **TEST leg parallelism — `--gpu N` (science-neutral, the clean win).** The 7×30 = 210 winner
  re-runs are embarrassingly parallel with zero reflection coupling. Laptop: `--gpu 3` (proven-safe
  2–3; **`--gpu 4` is REFUSED by the CLI** — it OOMs the 6 GiB RTX-4050 VRAM ceiling). **`--cpu N>0`
  is REFUSED on a REAL run (S6, 2026-07-06)**: CPU≠CUDA bit-for-bit and the device pool assigns
  seeds by a timing race, so a mixed pool makes the SEALED leg device-heterogeneous and
  irreproducible, and degrades the paired-seed CRN design. This costs no speed — the GPU is the
  binding resource and `--gpu 3` keeps it saturated; `--cpu` remains available for
  `--synthetic`/`--dry-run` dev throughput. Each test record now carries `metrics.device` so
  homogeneity is auditable from the archive.
- **SEARCH leg — SERIAL is the ratified HEADLINE (`--search-gpu 0`, the default; 2026-07-01 amendment
  supersedes R24, label corrected 2026-07-02).** The recorded headline
  (`headline_reflect_protocol: serial_reflect_on_best`) runs arms one candidate at a time through the
  prototype-validated serial loop, whose reflection seed is the generation's **BEST** candidate
  (M5/R32 — Eureka-faithful; the old "serial = reflect-on-last" wording was a stale premise, corrected
  2026-07-02 against `src/llm/loop.py:604-615`). Rationale: smallest concurrency surface for a 2–3-week
  unattended run; ADR-040's deadline math absorbs the longer wall-clock; reproducibility now EQUAL on
  both paths. The **parallel best-of-generation** path (`--search-gpu 2`) is the documented,
  now-resume-safe ROBUSTNESS VARIANT — not the headline.

### 4b. Launch (one authoritative command)
```bash
# HEADLINE DATA PANEL (R73, 2026-07-02, supersedes R44's univ3): the headline is **univ5** (Split C,
# 5,406×963 to the settled 2026-06-30 cutoff; zero-fill / liquidate_to_cash, NO fabricated losses;
# byte-diff vs frozen univ3 = 0 changed overlap cells). univ5 is the loader's LIVE DEFAULT
# (config/data.yaml gold.suffix, hash-bound), so SEARCH, SELECT, FREEZE, and TEST
# all train/evaluate on the same frozen headline panel with NO env-var override — leave the bare command.
#
# ⚠ univ4 is NOT "the tail": it is the M&A-CONTAMINATED HEAVY END of the delisting band (data-integrity
# audit 2026-06-25, ratified R44) — and, per ADR-051 (2026-07-02), ALSO a TERMINAL DOUBLE-COUNT: the
# OBSERVED-terminal recovery found the realised terminal already present in the vendor daily series for
# ALL 333 dead names (univ5s shumway audit: vendor_terminal_kept=333, ZERO surcharges), so univ4's flat
# −30/−55% surcharge stacked a fabricated loss on top of an already-booked real one (DELL buyout,
# TWX→AT&T, ABMD→J&J; 3 of the 30 headline-cohort names). The HONEST tail instrument stays the
# pre-registered delisting-return sensitivity BAND d∈{0,−30,−55,−100%}
# (analyze_campaign.delisting_band): univ5/univ3 (zero-fill) anchor the 0% end, univ4 the contaminated
# heavy end, and the truth sits AT the zero-fill end (the corrected univ5s equals it) — the full sweep
# moves pooled test CVaR-5% only ~2%, so the H2 tail ORDERING is invariant across it. Report the band;
# do NOT present univ4 alone as the tail. The CORRECT panel was EXECUTED 2026-07-02 as **univ5s**
# (observed-terminal route; supersedes the planned univ4r — the reason mnemonics do not resolve).
# univ3 is integrity-screened via univ3s (a screening SIDECAR — different artifact class from univ5s).
#
# LAPTOP HEADLINE (RATIFIED 2026-07-01, corrected 2026-07-02: SERIAL reflect-on-best search
# [--search-gpu 0 = the default] + 3-way recycled TEST leg).
# PREREQUISITE: the single-arm 50k GPU-smoke (Step 3d) is GREEN. --resume makes it crash-safe.
python scripts/run_campaign.py --gpu 3 --h3-singleshot --resume --no-shutdown
#   --h3-singleshot appends the H3 single-shot control (R30); H1 baselines run automatically (config h1_baselines).
#   --cpu is REFUSED on a real run (S6: the sealed leg must be device-homogeneous; GPU-only at --gpu 3
#   is already the throughput ceiling — the GPU is the binding resource).

# ROBUSTNESS VARIANT (parallel best-of-generation search; documented, resume-safe; NOT the headline):
python scripts/run_campaign.py --search-gpu 2 --gpu 3 --h3-singleshot --resume --no-shutdown

# (The old "rented 4090" block is SUPERSEDED: laptop-only per ADR-040, and its --search-gpu 8 would be
# refused by the ≥4 CLI guard anyway.)
```

> **⚠ SUPERSEDED wall-clock (2026-07-05).** The figures in this block were computed at the legacy
> **50k** budget and the pre-pilot **30-seed** count. Both moved: B\* = **200,000** (R74) and the σ_D
> verdict (σ_D=0.369 > 0.10) triggers an **arm-adaptive ~350-seed** amendment (H2 arms ~350, controls 30 —
> pending Tamer's ratification). The realistic laptop campaign is now **~23 days** at ~350 seeds (median
> ~85 min/candidate measured in the σ_D farm), NOT 2.6 days. Recompute the exact number at seed
> ratification; the "rented 4090" rows are dead (ADR-040, laptop-only). Kept below only as the historical
> 50k/30-seed estimate.

**Estimated wall-clock (HISTORICAL 50k/30-seed — see the superseded note above) — core ~600 runs** (210 search + 210 winner-test + 120 H1 + 60 H3 — the 7th arm `placebo_shuffled` (R32) adds +60 over the prior 540; per-run `m`≈**18 min**/50k on the 4050, **11 min** on a 4090 — the Step-3d GPU-smoke confirms `m`):
- **Laptop** (search n_gpu=2 / test n_gpu=3): ~31.5 h search + ~25 h test + ~6.75 h H3 = **≈ 2.6 days** (≈ 3–3.5 d under thermal throttle) — *estimate*, the test hours were originally figured at n_gpu=4 so treat them as an upper-bound-favourable estimate; **~180 GPU-hr**.
- **Rented 4090** (n_gpu=8): **≈ 13 h (½ day)**; **~110 GPU-hr**.
- **No GPU-hour cap** (the `hard_budget_gpu_hours` limit was removed 2026-06-28 — never code-enforced). The ~110–180 GPU-hr above are *estimates*, not a budget. The optional PPO/TD3 algo-robustness (~+120 runs) can be INCLUDED if wanted — it is now a scope/time choice, not a budget constraint. Opus API ≈ **$18–35** (~150 reward-design authorings: 5 LLM arms × 30, plus reflection turns). The campaign runs on the loader default **univ5** (the headline panel, R73/Split C — zero-fill, no fabricated losses; no env override needed).
Run it **backgrounded** (e.g. detached / `nohup`-style) so you can monitor in another terminal. The
driver `preload()`s pyarrow before torch (gold-parquet ABI guard) and `load_env()`s the key.

**Expected banner:**
```
[run_campaign] HEADLINE single-split: arms=[distributional, scalar, placebo, scalar_cvar5,
  placebo_shuffled, random_search, bayes_opt] seeds=[0..29] search_seed=0 candidates=30 steps=200000
  gens=6 pass=B provider=anthropic embargo=21 resume=False -> outputs/campaign
```
**GO/NO-GO (launch sanity, first ~2 min):** the banner shows `steps=200000` (the frozen B\*, R74 — NOT
the legacy 50k; a `steps=50000` banner is the mis-configuration to catch), `provider=anthropic`,
`candidates=30`, all 7 arms (the **frozen H2-family guard** raises `SystemExit` if the arms drift from
the pre-registered contrast family — that is a hard stop, fix `config/campaign.yaml` arms). The
`outputs/campaign/{search,frozen,test}` dirs are created and `progress.json` appears. If the banner
prints the wrong steps/provider/arms, **kill it immediately** — do not let a mis-configured paid run
proceed.

---

## 5. MONITOR the run (continuous, through transitions)

In a second terminal — **NB the campaign's `progress.json` lives under `outputs/campaign/search/`**
(the SEARCH leg's `ParallelMonitor` writes it there, one file rewritten per arm), NOT at
`outputs/campaign` (M5c correction, ops audit 2026-07-02):
```bash
python scripts/monitor.py outputs/campaign/search --follow-campaign   # live dashboard across ALL arms
python scripts/monitor.py outputs/campaign/search --once              # one scriptable text snapshot
python scripts/monitor.py outputs/campaign/search --stale-secs 600    # tune the silent-hang threshold (default 300 s)
# Remote/unattended: push a phone alert on done/error/stall. OFF by default, stdlib-only, READ-ONLY
# side-channel (sends run STATUS, never data). Use a PRIVATE ntfy topic.
python scripts/monitor.py outputs/campaign/search --follow-campaign --notify https://ntfy.sh/<your-private-topic>
```
`--follow-campaign` (M5a) keeps the watcher alive across per-arm `done` transitions (each arm rewrites
the SAME `progress.json`, so a plain watch exits after the FIRST arm) and re-arms the done/error/stall
alerts between arms; it exits when `outputs/campaign/campaign_summary.json` is (re)written — the
overall-campaign sentinel — or on Ctrl-C.

> **Known limitation (M5, deliberate):** the **TEST leg** (winner re-runs via
> `evaluate_winners_on_test_parallel`) writes **no `progress.json`** — it has no RunMonitor, and wiring
> one requires threading a Manager queue through the tested test-leg driver (not the clean ~30-line
> reuse the audit budgeted; destabilizing the tested driver for telemetry was rejected). During the TEST
> leg, watch the driver's console/log (per-arm `WARNING: … failed seed(s)` lines) and the growth of
> `outputs/campaign/test/<arm>/` record dirs; the dead-man ping (§0b) still covers host death. The
> serial-search fallback (`--search-gpu 0`) also runs monitor-less unless `run_arm` is given one — the
> parallel search is the recorded headline path. (If you use the serial fallback, note its trainer reads
> `config/prototype.yaml`'s agent block, so add the same `thermal_guardian:` key there for M6 coverage.)
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
| **ANOMALIES** | 0 | `failure_wave` / `critic_explosion` → investigate (PopArt value-target normalisation is ON since R42 — config-gated `agent.popart: true` in prototype.yaml/algos.yaml — so the prototype-era critic explosions should now be RARE; a recurring `critic_explosion` under PopArt points at a genuinely mis-scaled candidate reward — record it, the run is not aborted, and `analyze_campaign.divergence_report` clusters + reports it; a diverged candidate loses selection); a parallel TEST `WARNING: … failed seed(s)` is surfaced in the driver log |
| **GPU temp** | within thermal limits | sustained throttling over the ~2.6-day laptop core → §6 thermal |
| **fps / ETA** | stable | collapsing fps → thermal throttle or swapping (RAM) |

Anomaly/event detail is also in `outputs/campaign/{events.jsonl,anomalies.jsonl}` (tailed by the
dashboard). **Monitor THROUGH candidate transitions**, not just the clean start — the transition-wave OOM
risk (the reason n_gpu is capped at 3 and n_gpu=4 is refused) is the simultaneous fresh-buffer allocation
when a generation's candidates finish together (steady-state probes miss it).

**Watcher alert rules (2026-07-05):** the ntfy watcher now pushes on `error` / `done` / `stall` **plus**
`disk_low` (run-drive free space under 10 GB — the pagefile + Windows Update live on C:) and
`anomaly_surge` (anomalies.jsonl growing ≥20 lines within one poll tick — a cascade alerts the moment it
starts). The watcher also now SURVIVES exit-3 resumable passes (it exits only on a terminal
`exit_code == 0` summary), so one launch covers the whole multi-pass run.

**The SENTINEL — the "catch absolutely anything early" invariant monitor (2026-07-05, `scripts/sentinel.py`).**
The dashboard shows what is HAPPENING; the sentinel decides whether it is HEALTHY. Run it beside the
dashboard, in a third terminal, for the whole campaign:
```bash
python scripts/sentinel.py outputs/campaign --watch --interval 120   # continuous, severity-graded
python scripts/sentinel.py outputs/campaign                          # one shot (exit 1 on CRITICAL — cron/CI-friendly)
```
It runs, READ-ONLY, a battery of invariant checks every tick and raises the moment ANY deviates —
disk/RAM/GPU-temp, silent-hang, **gate-failure rate**, **NaN rate in the archive** (the "surfaces at the
end" corruption class), **critic-explosion clustering** (diverged-RUN rate + a CRITICAL if a FROZEN WINNER
diverged), **cross-arm reward-scale drift** (the P5 confound made live-auditable via PopArt `raw_rms`),
**API error rate**, exit-code, and archive-mirror freshness. Every check TRANSITION is PERSISTED
severity-tagged to the sentinel-owned sidecar `<run_dir>/sentinel_events.jsonl` (S18, 2026-07-06: the
sentinel is a separate process, so the run's own events.jsonl handler never sees it; a sidecar also
avoids concurrent-append interleaving and error-taxonomy self-feedback) — the precise, machine-parseable
health history: grep it, or replay it after the run. A CRITICAL exit code lets you wire it into a cron push. This is the layer that means
nothing about a bad result waits until analysis time to be seen. The sentinel also runs a **CUSUM
change-point detector** (statistical process control) on the streaming gate-failure and NaN rates, so a
slow upward DRIFT is flagged before it ever crosses a hard threshold.

**The 2026-07-06 deep-monitoring layer (detect-EVERYTHING):**
- **completion_stall** — PRODUCTIVITY, not just liveness: the journal's per-unit completion stream
  (`seed_done`/`candidate_done` events) yields the run's OWN median cadence; silence > 3x it = WARN,
  > 8x = CRITICAL. Catches the wedged-CUDA-training-with-a-happily-alive-driver hang that mtime checks
  cannot see. Corroborated in-driver: `run_recycling` itself fires a WARNING `test_leg_stall` event
  (naming the pending arm/seed identities) when NO training completes for
  `config/campaign.yaml monitoring.test_stall_after_s` (default 5400 s ≈ 3x the expected ~28-min
  inter-completion cadence at n_gpu=3).
- **coverage_search / coverage_test** — the expected-vs-done UNIT ledger (config is the frozen truth:
  7x30 search, 11x30 test) with a data-driven ETA; a summary that claims completeness while units are
  missing = CRITICAL (the anti-husk guarantee at unit granularity); MORE units than the design = WARN
  (duplicates / config drift).
- **error_taxonomy** — failures clustered by kind (oom / cuda / sandbox / api / timeout / divergence /
  nan / stall) with counts + affected arms; a single kind reaching ~10 = WARN (a systematic wave).
- **disk_forecast** — PREDICTIVE exhaustion: the fill rate over the watch history → "hits the 20 GB
  floor in ~N h" (WARN ≤ 48 h, CRITICAL ≤ 12 h) — lead time instead of a surprise.
- **fps drift** — a direction-down CUSUM against the run's own early-baseline median fps: thermal
  creep / swap degradation surfaces in hours.
- **B7 unified view** — `scripts/monitor.py` now renders the sentinel's one-line verdict inside the
  dashboard (and `--once` snapshots), refreshed every ~15 ticks.
- **B6 DEADMAN heartbeat** — `monitor.py --heartbeat <url> [--heartbeat-every 600]` POSTs a compact
  health snapshot UNCONDITIONALLY on the interval; point it at a healthchecks.io-style service whose
  alarm fires on the ABSENCE of pings — the only way to detect host death (power loss, kernel panic)
  that no on-host monitor can report. Set the service's grace period to ~2-3x the interval.

**Result-archive integrity seal (2026-07-05, `scripts/archive_integrity.py`).** The archive is the one
irreplaceable artifact (results replay from it). At campaign end the driver auto-writes
`outputs/campaign/archive_integrity.json` — a content-addressed manifest with a single verifiable **root**
over every `record.json` (the "results fingerprint", stamped into `campaign_summary.json`). `analyze()`
**re-verifies the live archive against that seal before trusting any number** and reports the verdict under
`out["archive_integrity"]` — a MISMATCH (a modified / dropped / added record between the run and analysis)
is surfaced loudly, never silently averaged in. Check by hand any time:
```bash
python scripts/archive_integrity.py verify outputs/campaign    # exit 0 = intact; 1 = tamper/corruption
``` **After ANY reboot, restart the
watcher by hand** (the ONSTART task re-enters the supervisor + re-applies the GPU clock lock, but not the
dashboard): `python scripts/monitor.py outputs/campaign/search --follow-campaign --notify <topic>`.

### 5b. PRE-COMMITTED run protocols (2026-07-05 — treatment-blind by construction; do not improvise)

**(i) DAY-2 GO/RECHECK gate** (~48 h after launch, while stopping still costs 2 days, not 23):
- [ ] every LLM arm shows plausible ACCEPTED-candidate counts (dashboard / `compute_accounting` inputs);
      gate-failure burn within the prototype's band (~1 failure / 40 calls);
- [ ] open 2–3 archived `prompt.txt` sidecars PER ARM and verify the rendered feedback block is EXACTLY
      the arm's design (distributional = six tail lines; scalar = one DSR line; placebo = inert
      constants; placebo_shuffled = deranged values, same labels; scalar_cvar5 = the single CVaR line)
      — this checks the MANIPULATION itself and reads ZERO outcomes;
- [ ] anomalies: no `failure_wave`; `critic_explosion` clusters ≤ the prototype's ~2.5%/candidate;
- [ ] verdict recorded here: GO / STOP-FIX-RELAUNCH (a day-2 relaunch = 2 lost days + one dated
      amendment if a hash-bound prompt must change — survivable by design).

**(ii) FIRST-ARM INTEGRITY REHEARSAL** (the moment the first arm's TEST leg completes, ~day 6–8): run the
FULL analyze→figures→build pipeline on the partial archive with the hard rule that only **mechanical
integrity** is read — records parse, schemas complete, seed counts, NaN rates, series lengths, figures
render, PDF compiles. **Suppress/ignore every cross-arm effect estimate** (severity discipline: no
outcome peeking mid-run). Purpose: the pipeline's first contact with real campaign data happens with
2+ weeks of fix-time left, not in August.

**(iii) ANOMALY-TRIAGE protocol (pre-registered; an alarming number triggers this checklist, never a
re-run):**
1. INTEGRITY first — replay ONE affected cell from the archive and byte-compare
   (`metrics.test_returns`, the proven M7-b5 pattern); verify checksums/windows/seeds.
2. FALSIFY the analysis — run the identical stack on shuffled labels / the synthetic null
   (`null_calibration` machinery); it must return null.
3. Only then accept the number as REAL and report it under the pre-registered branch it falls in.
**Iron rule: NO arm is ever re-run because a result "looks wrong"** — outcome-contingent re-runs are the
forking-paths sin the whole pre-registration exists to prevent.

**(iv) ARCHIVE MIRROR task** (register at launch, run-day checklist): every 6 h,
`schtasks /Create /SC HOURLY /MO 6 /TN LLMRewardArchiveMirror /TR "powershell -ExecutionPolicy Bypass -File <repo>\scripts\mirror_archive.ps1"`
(the script exits 0 on success since 2026-07-05; 8 = a real robocopy failure; 9 = the 2026-07-06
**backup-integrity verify** failed). The mirror is now VERIFIED, not just copied: after each pass the
script re-hashes every mirrored tree that carries a sealed `archive_integrity.json` via
`scripts/archive_integrity.py verify-mirror` — sealed records must be byte-intact (removed/changed →
exit 9), while records ADDED after the seal are tolerated (a mid-campaign mirror lawfully carries
newer work than the last sealed manifest). A silently-rotting backup is caught at mirror time, not at
the disaster-recovery moment.

**(v) SUBMISSION LINT (P8; 2026-07-06):** before the final upload run
`python scripts/build_paper.py --final` — it FAILS while any editorial placeholder (`[FROM CAMPAIGN: ...]`, compile notes, fill slots, the scaffold banner) survives in the assembled deliverable; ~59 legitimate fill-at-campaign slots live in the chapters today, so the gate MUST fail until the results are written in.


---

## 6. CONTINGENCY playbook (run-day failures → recovery)

Every contingency below is **resume-safe**: re-launch with `--resume` and completed `(arm, seed)`
test ids + frozen winners are skipped, so no work is redone and no paid SEARCH budget is re-burned.

| Failure | Symptom | Recovery |
|---|---|---|
| **UNRECOVERABLE host failure** (hardware death / repair > ~4 days) | the deadman heartbeat alarm fires; the host will not boot | **PLAN B — `docs/PLAN_B_FALLBACK_HOST.md`**: verify the mirror (`archive_integrity.py verify-mirror`), continue on the prepared fallback Mac (Docker, exact pinned stack in CPU build), migrating at a SEED boundary across all arms (CRN pairs stay device-homogeneous; `metrics.device` records the split); the pre-declared contingency clause ships in the seed-ratification amendment |
| **OOM (RAM) at n_gpu=4** | RAM → ~92%, `MemoryError` cascade / `failure_wave` anomaly | Kill; re-launch with **`--gpu 3`** (the measured-safe count) `--resume`; close more apps; drop `--cpu 1` if set. Root cause is the transition wave, not steady state. |
| **OOM (VRAM)** | CUDA out-of-memory on a 4th worker | You exceeded the VRAM ceiling — n_gpu **must be ≤ 3** on the 4050 (n_gpu=4 is refused by the CLI). Re-launch `--gpu 3 --resume`. |
| **Thermal throttle** | GPU temp pinned, fps collapses over hours | Run on a cooling stand / cooler ambient; or move the campaign to the **rented 4090** (much faster + avoids the laptop thermal soak) — same frozen config, `--resume` from the partial archive. |
| **Crash / interruption / spot reclaim** | process dies, machine reboots | Re-launch the **identical** command `+ --resume`. Idempotent: skips done test ids, loads existing frozen winners (never re-searches them), preserves the select→freeze→test chain. |
| **A single worker dies mid-run** | one candidate/seed errors | `train_candidate` catches per-candidate exceptions (the pool survives); the parallel TEST driver surfaces `n_failed` + the first error in the log. The desync guard prevents a silent winner swap. Finish the run, then `--resume` to fill the failed seeds. |
| **Slow RSS creep** | RSS climbs over tens of minutes at any n_gpu | The in-process `del+gc` fix should hold it flat; if it still creeps, the manual pool-recycling (`recycle_every`) is the backstop. Do **not** enable `max_tasks_per_child` (deadlocks on Windows spawn). |
| **Opus rate-limit / 429** | SEARCH stalls on LLM calls; events log shows API errors | The author calls are in the SEARCH stage only (~150 LLM candidate authorings: 5 LLM arms × 30); transient 429s back off. If sustained, pause and resume later (SEARCH archives per candidate; `--resume` continues). The TEST leg uses no API. |
| **Cost / GPU-hour** | informational only — **NO cap** | There is **no GPU-hour budget** (`hard_budget_gpu_hours` removed 2026-06-28; never code-enforced, and `auto_shutdown_on_complete` is a verified no-op — it does NOT power off). The ≈110 GPU-hr (4090) figure is an *estimate*. To stop early, kill + `--resume` later — no idle spend. |
| **`winner_not_testable` for an arm** | summary status, not a crash | The SELECTED winner's `reward_source` was a non-executable comment stub (e.g. a `random_search`/`bayes_opt` coeff-comment). It is FLAGGED, not fabricated; the other arms still test. Investigate that arm's archive; it does not block the headline H2 family if the H2 arms tested. |
| **Frozen/test desync error** | `ValueError: frozen winner hash mismatch … (frozen/test desync guard)` | A re-searched resume swapped the winner. **STOP** — do not bypass. Restore the frozen record or re-run that arm cleanly so frozen and test describe the same reward. This guard is protecting headline integrity. |
| **Hung candidate (in-process reward)** | one worker's steps/s → 0 with NO crash; watcher STALL alert; GPU util sags; the arm stops advancing | The in-process reward path has NO per-step timeout by design (containment boundary, `src/sandbox/executor.py::safe_call`): a reward whose cost depends on input VALUES (cheap on the validation fixture, explosive on a real return) can hang its worker mid-training. Kill the campaign process, re-launch the identical command `+ --resume`. The hung candidate has NO archived record, so its slot regenerates against the author (fresh call) while every archived candidate replays — the matched budget still holds. The stall alert is the watcher's job; the supervisor only restarts on process EXIT, so the operator (or a deadman-page) closes this loop. |
| **Corrupt archive dir → restart loop** | `load_all`/`load_run` raises (`ValueError`/`KeyError` — bad JSON, truncated record, env.json hash guard) at analysis or on resume; under the supervisor the same failure re-fires every restart until `--max-total-restarts` trips | `src/io/results.py::load_all` fails LOUD on ANY unreadable run dir BY DESIGN (never silently drops a record from the analysed set — batch-5 m4). The offending dir is named in the traceback. **Triage, do not bypass:** inspect that one dir under `outputs/campaign/…`; a torn write (record.json present but a sidecar missing, or vice-versa — should be impossible after the sidecars-first+`os.replace` commit fix, but a disk fault can still do it) is quarantined by MOVING the dir out of the archive tree (e.g. to `outputs/quarantine/`) and re-launching `+ --resume` — the slot then regenerates like any un-archived candidate, matched budget preserved. Do NOT hand-edit a record to make it parse (that fabricates data). If many dirs are corrupt, suspect the disk, not the code. |

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
python scripts/monitor.py outputs/campaign/search --once   # phase=done, anomalies summary (M5c path)
cat outputs/campaign/campaign_summary.json                 # per-arm status + windows + all_arms_tested/exit_code
```
**Expected:** `campaign_summary.json` lists every arm as `tested` with `n_seeds_written: 30` (or the
resumed remainder), plus the resolved `train_window`/`val_window`/`test_window`. The leakage-safe
purge is `max(embargo=21, lookback=60) = 60` sessions at each boundary (R18). **GO/NO-GO:** all H2
arms (`distributional`, `scalar`, `placebo`, `scalar_cvar5`) `tested` with the full seed count.

---

## 8. ANALYZE — the headline report

```bash
# R73: analyze on the SAME headline panel the campaign trained on — univ5, the loader default (Split C,
# zero-fill, no fabricated losses). The panel-dependent floor + the delisting-return band both load via
# gold_suffix(), which already defaults to univ5, so NO env override is needed here.
python scripts/analyze_campaign.py --root outputs/campaign --single-shot-root outputs/campaign/test_h3_singleshot/distributional
#   (--root defaults to outputs/campaign; --single-shot-root feeds the H3 single-shot test leg into the H3 difference test.
#    Emits: PBO/DSR, the H2-RA + H2-Tail two-tier verdict, H1/H3/H4, the secondaries, the floor + R20 rf-robustness,
#    and the R44 delisting-return sensitivity band (out["delisting_band"]) — univ3 is the 0% end, univ4 the
#    disclosed M&A-contaminated heavy end; the univ5s observed-terminal recovery (R73, executed 2026-07-02)
#    superseded the planned univ4r re-pull and proved byte-identical to the univ5 zero-fill headline.)
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
| ☐ | Anomalies reviewed | `anomalies.jsonl` (PopArt value-target normalisation is **ON** since R42, so critic explosions should be RARE — a recurring one flags a genuinely mis-scaled candidate reward, recorded not aborted; `analyze_campaign.divergence_report` clusters them) |
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
python scripts/run_prototype.py --parallel --synthetic --gpu 3 --pass A --arms distributional  # 3d (V3)
# ... V4 soak / V5 resume / V6 determinism on the synthetic path ...
# R73: headline = univ5 (loader DEFAULT — Split C, zero-fill, no fabricated losses); NO env override (search+test+analyze).
python scripts/run_campaign.py --gpu 3 --h3-singleshot --resume --no-shutdown  # 4  (REAL run — SERIAL reflect-on-best headline [--search-gpu 0 default, ratified 07-01/corrected 07-03] + H3; --cpu REFUSED on real runs — S6 device homogeneity)
python scripts/monitor.py outputs/campaign/search --follow-campaign  # 5  (second terminal; progress.json lives under search/ — M5c)
python scripts/analyze_campaign.py --root outputs/campaign --single-shot-root outputs/campaign/test_h3_singleshot/distributional  # 8  (PBO + DSR + H2-RA/Tail + H1/H3/H4 + floor + rf + R44 delisting band) — NOT `make analyze`
python scripts/cost_sweep.py --root outputs/campaign/test   # 9a
make power                                               # 9b
```
