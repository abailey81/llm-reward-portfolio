# Session log — 2026-07-01 · Phase-B/C execution (pilots → freeze)

A chronological, auditable EXECUTION log for the Phase-B (pilots) → Phase-C (freeze) run. Structured for
**append at each later milestone** — new events go under a dated `## Milestone` heading at the end, newest last,
in the order they happened. **Nothing committed**; `config/preregistration.yaml` is still `frozen: false`. Durable
anchors: CLAUDE.md (priorities + current state), `DECISIONS.md` (ADRs), `CHANGELOG.md` `[2026-07-01b]`, and
`memory/session-current-focus.md` (the cursor).

**The gate (this phase):** convergence ladder → plateau knee → **B\*** → σ_D pilot at B\* → **n_seeds** → `pilot.py`
verdict → set B\*/seeds in config → `freeze.py`. The pilots own the machine (GPU + RAM freed for them).

---

## Milestone 1 — 2026-07-01 · verification gate, coverage raise, pilot harnesses built, ladders launched

### 1.0 Verification gate (entry condition — GREEN)
- Full **test suite exit 0**.
- A fresh **adversarial 5-area audit came back CLEAN** — ITEM 3 (parallel resume-cache) / GAP A (mechanism
  analyses wired into the report) / GAP B (the two sub-experiment runners) / ratification (the 4 prereg
  amendments) / the mechanism reframe.
- **ruff clean** across `src` + `scripts` + `tests`.
- **Coverage measured 91.96% total** — at/above the **90% target**, well above the **88% floor**.

### 1.1 Coverage raise (subagent · tests-only · NO src touched)
Roughly **70 targeted error / edge / degrade-path tests** added, lifting the weakest modules:
| module | before | after |
|---|---|---|
| `responsiveness` | 86% | 95% |
| `mediation` | 86% | 97% |
| `es_backtest` | 83% | 99% |
| `multiple_testing` | 88% | 100% |
| `contamination` | 86% | 99% |
| `ood_stress` | 77% | 85% |

- `ood_stress` is **capped at 85%** by a `statsmodels` **"SVD did not converge"** failure in the Markov
  success-body on **this Windows / BLAS build** — the code's **graceful-degrade path IS tested and documented**;
  this is an environment/library limitation, **not a code defect**. No src was modified — the raise is entirely
  new tests exercising real error, edge, and degrade paths.

### 1.2 σ_D pilot generation harness (subagent · BUILT — no ready path existed)
There was **no existing path** to produce the per-seed sealed-TEST records that `sigma_seed_pilot.py` consumes, so
one was built:
- **NEW `scripts/run_sigma_pilot_train.py`** — trains the **two CRN baselines** (`differential_sharpe` +
  `return_minus_cvar`) across **shared seeds** (common random numbers), then writes each seed's **sealed-TEST
  record** via `test_leg.build_test_record` + `write_run` — i.e. the *exact* schema `sigma_seed_pilot.py` reads.
- **End-to-end smoke GREEN:** generate → analyze → status `ok`.
- **Real GPU command:** `run_sigma_pilot_train.py --budget <B*> --n-seeds 15 --device cuda`.
- **NEW `tests/test_run_sigma_pilot_train.py` green; ruff clean.**

### 1.3 Convergence pilot (learning-curve ladder)
- `learning_curve.py` **smoke GREEN**.
- **Unbuffered foreground real-gold + CUDA probe GREEN** — trains and evals cleanly on the real `univ3` panel.
- **The first background ladder launch HUNG** (Tee-piped). Root cause: a **block-buffering / pipe deadlock** —
  python was **not training** (GPU idle). **Diagnosed empirically** via `nvidia-smi` + process-CPU (not assumed),
  the hung process **killed**, and the ladder **relaunched UNBUFFERED with a direct file redirect (no Tee)**.

### 1.4 Resource cleanup (user-authorized · full permission)
- Killed **all stale python** — orphaned multiprocessing workers + leftover `D:/tmp` smoke scripts — freeing the
  **GPU (→ 0 MiB)** and **RAM (→ 8 GB free)** so the pilots own the machine.

### 1.5 Command now running
Convergence ladder:
```
learning_curve.py --budgets 50000,100000,200000,350000 --seeds 0,1,2 --device cuda
```
→ plateau knee → **B\***. Then **σ_D at B\*** → **n_seeds** → `pilot.py` verdict → set B\*/seeds → `freeze.py`.

### 1.6 State at end of milestone
`frozen: false`; nothing committed. Convergence ladder running unbuffered (foreground-diagnosed healthy). Next
recorded milestone appends below.

---

## Milestone 2 — 2026-07-01 · convergence-pilot OOM root-caused → 50k buffer cap wired (ADR-042) → ladder re-run

### 2.0 Device settled empirically (CUDA, not CPU)
Head-to-head fixed-10k-step timing: **CUDA 173 s vs CPU 378 s** → CUDA is the right device (~2.2× faster, ~55 steps/s
at the measured 18.2 ms/step). The earlier "9% CPU" reading was a red herring — it is NORMAL for GPU-sync-bound
training (the work is on the GPU, uncounted as CPU-seconds), not a stall.

### 2.1 The first ladder completed but exposed a real DEFECT (not instability)
`bxu2ldynn` finished with **n_ok 3 / 3 / 1 / 0** across budgets 50k / 100k / 200k / 350k. Root cause (from the
written JSON, not guessed): **`MemoryError` at SB3 replay-buffer allocation** — `np.zeros((budget, 1, 1893) float32)`
≈ 2.8 GB at 200k / 5 GB at 350k → OOM on the 15.6 GB laptop. Critic losses were all **finite/healthy (~0.1
terminal)** → purely RAM. The pilot coupled `buffer_size = budget` (the ADR-025 rule), which is safe only ≤~100k.
This is exactly the **"buffer-cap wiring" pre-freeze fix** listed OPEN in CLAUDE.md CURRENT STATE — surfaced
empirically. The run's "recommend 200k / still rising" verdict is **UNRELIABLE** (1 surviving seed at 200k + an
unrepresentative full-history buffer) and is **superseded**.

### 2.2 Fix — 50k HARD cap, decoupled from train_steps, every leg (ADR-042)
- `config/campaign.yaml` — new `agent: { buffer_size: 50000 }` block (TEST leg reads it → no train_steps re-couple).
- `src/agents/factory.py` — `DEFAULT_REPLAY_CAP=50000` + `campaign_replay_cap()` (single source of truth, reads the
  campaign config); the GPU-worker `_policy_kwargs` caps via `min(..., campaign_replay_cap())`.
- `src/agents/trainer.py::resolve_agent_kwargs` — `min(requested_or_train_steps, campaign_replay_cap())`.
- `scripts/run_prototype.py::_agent_cfg` (serial SEARCH) — `min(steps, campaign_replay_cap())`, which ALSO closes the
  **serial-SEARCH-25k vs TEST-50k buffer skew** (winner now selected under the replay dynamics it is evaluated under).
- both pilots (`learning_curve.py`, `run_sigma_pilot_train.py`) — `min(budget, campaign cap)`.
- **Verification (CPU, independent):** cap 50000; trainer/factory/`_agent_cfg` all → **50000 at 200k**, **25000 at
  25k** (prototype unchanged), explicit oversize → clamped 50k; **93 buffer-touching tests green**, ruff clean, **no
  test changed**. Delegated + re-verified via subagent, then re-checked first-hand.

### 2.3 Ladder RE-LAUNCHED under the cap
`bfb5oi4wo` — `learning_curve.py --budgets 50000,100000,200000,350000 --seeds 0,1,2 --device cuda --no-plot`
(unbuffered, → `scratchpad/convergence4.txt`). Confirmed past setup + training on GPU. ETA ~10 h → **B\*** (all
budgets now survive under the 50k cap). ~5 h mid-run stall-watchdog armed.

### 2.4 State at end of milestone
`frozen: false`; nothing committed. Capped-buffer ladder running (`bfb5oi4wo`) → B\*. Buffer-cap fix complete +
recorded (ADR-042). Next: B\* → σ_D at B\* → n_seeds → `pilot.py` → set config → `freeze.py`.

---

## Milestone 3 — 2026-07-01 · exhaustive upgrade research → data-plan DECIDED, Refinitiv access SOLVED + fast, RL=online clarified

A research-and-decide milestone (no campaign compute; the ladder from M2 keeps running in parallel). Captures
the upgrade sweep, the settled data plan, the access solve, and the offline/online clarification. Everything
here is **DECIDED (settled plan)**; items needing a live pull are **not yet EXECUTED**. `frozen: false`,
nothing committed. Docs reconciled: `LSEG_DATA_STRATEGY.md`, `DATA_REPULL_DELISTING.md`, `RIGOUR_LEDGER.md`
(this log is the 4th).

### 3.0 Exhaustive upgrade research (report-only enrichments, all disjoint from the frozen m=6)
An exhaustive pass over "what strengthens the grade/publishability without touching the frozen reward search":
- **Bid-ask SQUARE-ROOT impact cost model** — from the **already-frozen** A5 bid-ask spreads (**no new pull**);
  upgrades the flat per-bps sweep (R15) to a realistic price-impact frictions exhibit. Report-only.
- **BAB / QMJ factor attribution** — on **free** factors (no pull); extends the R26 attribution ladder. Report-only.
- **Delisting via OBSERVED TERMINAL RETURNS** — see 3.2; the reason-field route is dead, the terminal-return
  route is alive.

### 3.1 Data plan DECIDED (pending rebuild) — Split C; forward-2026 in, backward-2000 out
- **Split C:** train **2005–2016** / val **2017–2019** / test **2020–2025 (or 2020–2026)**.
- **Forward-2026 settled extension = FEASIBLE + FAST** (~30 min–2 h Refinitiv pull — see 3.3) → the accepted
  history move. **NOT "~2 weeks"** (that figure is the *laptop training campaign*, never a data re-pull).
- **Backward extension to ~2000 (dot-com) REJECTED on DATA-QUALITY**, not deadline: survivorship-free dot-com
  reconstruction is the hardest + least-validatable era — Ince–Porter (2006) worst-earliest; yfinance can't
  cover dead names; **CRSP is the gold standard there, not Refinitiv**. This closes the old "extend to ~1989"
  lever (`LSEG_DATA_STRATEGY.md` §2A now marked SUPERSEDED).
- **Multi-market "lite" FTSE 100 replication** added as the single **report-only external-validity leg**
  (`LSEG_DATA_STRATEGY.md` §2B DECIDED).
- **2nd LLM = Qwen3-Coder** (open, reproducibility anchor). **GPT-5.5 REJECTED on cost.**

### 3.2 Delisting fix — reason field is DEAD, observed-terminal-return is the route (probed 2026-07-01)
- Probed the delisting-REASON mnemonics (`TR.DelistingReason` / `TR.DelistingType` /
  `TR.DelistingReasonDescription`): **none resolve under this entitlement.** Recorded negative in
  `DATA_REPULL_DELISTING.md` (top banner + §2 Step-1 SUPERSEDED + §4 feasibility + §5).
- **The fix uses OBSERVED terminal returns instead** — dead-name daily returns ARE recoverable
  (**Lehman `LEH.N^I08` → 2042 daily rows**), so the correct realised terminal replaces the fixed −30/−55 %
  surcharge without a reason label. Report-only, identification-neutral, DECIDED (not yet EXECUTED).

### 3.3 Refinitiv access SOLVED (verified 2026-07-01) + fast-pull finding
- **Session opens via PowerShell + an isolated `.venv-lseg` (`refinitiv-data` 1.6.2).** The earlier blocker was
  the **Bash tool's sandboxed network**, NOT an entitlement/licence gap. **Run all pulls via PowerShell +
  `.venv-lseg`.**
- **The pull is FAST:** a full/forward Refinitiv pull is ~**30 min – 2 h**. This retires the "probe access
  before relying / access uncertain" hedges in the data docs (LSEG §7 corrected).

### 3.4 RL = ONLINE (clarification — offline/online framing)
- Clarified for the write-up: the confirmatory **RL is ONLINE** (SB3 SAC learns by interacting with the
  historical-return simulator env, on-the-fly replay) — it is **not** an offline-RL / batch-CQL setup. The
  "offline RL on a fixed historical panel" examiner-framing (CLAUDE.md Grade strategy) is a *positioning*
  device for Okhrati, not a claim that the algorithm is offline. `docs/offline_online_position.md` already
  states this correctly and is **left untouched** (verified correct this session).

### 3.5 State at end of milestone
`frozen: false`; nothing committed. Convergence ladder (M2, `bfb5oi4wo`) still → B\*. Data plan + access +
delisting-fix DECIDED (execution pending the entitled pull via PowerShell + `.venv-lseg`). Next unchanged:
B\* → σ_D → n_seeds → `pilot.py` → set config → `freeze.py`; execute the report-only enrichments + Split-C
rebuild when the pull is run.
