# Decision Log (engine-line audit record — A)

> **Post-merge note (ADR-022, 2026-06-17).** This is the **engine line's** audit/impl/compute record
> (AUDIT-*, IMPL-*, COMPUTE-*, RESEARCH-*). After the repository unification, the **authoritative**
> decision log going forward is the root **`../DECISIONS.md`** (ADRs 001–024). This file is retained,
> append-only, as the A-line audit history; do **not** start new decision threads here — add them to
> `../DECISIONS.md` and cross-reference an entry here only if it amends an A-line audit decision.

Append-only record of architecture decisions, audit corrections, the Phase-0 result, the
freeze hash, and any post-freeze amendments. One entry per decision; newest at the bottom.

Format: `### <id> — <title> (<date>)` then **Decision / Why / Status**.

---

### AUDIT-A1 — Headline is the FEEDBACK CHANNEL, agent fixed (pre-build)
**Decision:** the contribution/H2 is the feedback channel (distributional vs scalar); all feedback
arms run the same fixed SB3 SAC agent. The distributional-critic question (SAC vs TQC) is a separate,
secondary experiment. **Why:** the feedback is measured off-critic from realized returns, so it does
not depend on the agent's critic — removing the project's biggest risk (dependence on the fragile
component). **Status:** adopted; reflected in PREREGISTRATION §2 and config/arms.yaml.

### AUDIT-A2 — Distributional critic = TQC (sb3-contrib), not IQN-SAC; QR-DQN fallback deleted
**Decision:** secondary critic experiment uses TQC (continuous, SB3 family). QR-DQN removed (discrete-
only, incompatible with the simplex action). **Why:** clean same-family SAC-vs-TQC contrast; avoids the
d3rlpy IQN-SAC fragility on the headline path. **Status:** adopted; d3rlpy retained for optional
verification only.

### AUDIT-B1 — Measurement = empirical body + EVT/GPD tails (not a neural IQN)
**Decision:** tail-diagnostic set measured by the empirical estimator for the body and a GPD/EVT fit
for the extreme levels (CVaR-1%, 5%). **Why:** for a 1-D sample the empirical quantile is efficient; a
neural net adds noise; ~750 training points give too few tail observations for the extremes without EVT
(cf. EX-DRL). **Status:** adopted; src/feedback/measurement.py.

### AUDIT-B2 — Feedback measured on TRAINING returns; selection on VALIDATION returns
**Decision:** measure the fed-back distribution on training-period realized returns; select winners on
validation Deflated Sharpe. **Why:** measuring and selecting on the same (validation) split re-introduces
overfitting. **Status:** adopted; PREREGISTRATION §4–5.

### AUDIT-B3 — Loop runs ONCE; CPCV on winners; fitness reward-independent
**Decision:** the reward-design loop runs once with a fixed budget; CPCV applied to the fixed winners
for inference; fitness = validation Deflated Sharpe, independent of the candidate reward's units.
**Why:** CPCV inside each candidate is ~16x compute; reward-dependent fitness is circular and
hack-prone. **Status:** adopted.

### AUDIT-B5 — Fixed per-candidate training-step budget
**Decision:** every candidate trains for the same fixed step budget. **Why:** comparability across
candidates/arms. **Status:** adopted; set the number from the Phase-0 timing.

### AUDIT-B6/B7/B8 — Regime module; CVaR-1% flagged; cross-arm FDR
**Decisions:** build a regime-labelling module whose independent-regime count feeds the power analysis;
retain CVaR-1% but flag it high-variance; apply a cross-arm/metric FDR (Romano-Wolf or BH) correction.
**Status:** adopted; config/regimes.yaml, PREREGISTRATION §10.

### AUDIT-C2/C3 — Replay-not-regenerate; data not redistributable
**Decisions:** results replay from the archive (LLM calls are non-deterministic); ship checksums +
pipeline + a synthetic panel, never the licensed gold data. **Status:** adopted; .gitignore, src/io.

### AUDIT-A6/C4 — Compute = RTX 4090 (dev) + UCL Myriad (campaign array job)
**Decision:** develop on the 4090; run the campaign as a Myriad array job; Colab/Kaggle overflow only.
Supersedes the earlier $50-Colab plan. **Why:** the 4090 + Myriad are free and faster/parallel.
**Status:** adopted; config/campaign.yaml.

---

### PHASE-0 — smoke-test result (GREEN, 2026-06-17)
**Decision: GREEN.** `scripts/smoke_test.py --synthetic --steps 1200` on the **RTX-4050 laptop, CPU**
(torch 2.12.0+cpu). Both fixed agents TRAIN and critic loss FALLS:
- **SAC** — 44.1 steps/s → **m ≈ 18.9 min/50k**; critic_loss 413.2 → 1.01 (n=1099); obs_dim = 1893 (as designed).
- **TQC** — 32.2 steps/s → **m ≈ 25.9 min/50k**; critic_loss 9.82 → 0.25 (n=1099).
**Device:** CPU (not a 4090). Per deep-research §2 the SB3 [256,256] nets are CPU-bound, so the 4050 GPU gives
no speedup (and `pip` only had cu121 torch ≤2.5.1 vs the installed CPU 2.12.0); the GPU build is reserved for
the rented-4090 campaign. Measured CPU `m` matches the compute-doc estimate (~18). **4090 confirmed: n/a (CPU).**
**Fixes to pass the gate:** ADR-027 (action space `Box(-inf,inf)`→`Box(-10,10)`; SAC/TQC need finite bounds),
ADR-028 (cross-platform sandbox timeout; `SIGALRM` was a Windows no-op), stub import fix
`src.env.portfolio`→`src.env.portfolio_env`. Suite re-earned: **153 non-slow tests pass** (P1).
**Status: GATE OPEN** — the freeze precondition is met.

### FREEZE — pre-registration content hash (TO FILL)
**Decision:** PREREGISTRATION.md + config/preregistration.yaml frozen on _(date)_; SHA-256 `<hash>`
(emitted by scripts/freeze.py). **Status:** _frozen; amendments below require user approval._

<!-- amendments appended below this line -->

---

### IMPL-1 — Deterministic core implemented + tested (16 Jun, build session)
**Decision:** the entire deterministic core is now real, not stubs: inference (bootstrap/PBO/DSR/
rliable/FDR), measurement (empirical+EVT), feedback schema, fitness, reward contract + sandbox,
baselines (reward canon + HRP/risk-parity/MV-shrinkage), the Gymnasium environment, regimes, results
IO, the 13-stage pipeline (on synthetic data), arms factory, the two H4 search baselines, the agent
factory (lazy SB3/TQC), the LLM client (injectable transport), and the Eureka loop (dependency-injected).
**Status:** 125 behaviour tests pass on the light scientific stack; torch/SB3/openai paths are real but
require the full GPU/API environment (their tests use fakes / assert a clear RuntimeError).

### IMPL-2 — robust_skew sign convention (reconcile before freeze)
**Decision:** `measurement.tail_stats()['robust_skew']` uses the Bowley ordering that is **negative when
the left tail is longer** (matching the design's stated semantic), which is the negation of the literal
formula written in `FINAL_PLAN` B.10. **Why:** the prose binds ("negative when the left tail is longer");
the literal formula's sign was inconsistent with it. **Status:** flagged — confirm the intended sign in
`PREREGISTRATION.md` §4 at the Phase-1 freeze.

### IMPL-3 — minor signature reconciliations vs the scaffold stubs
**Decision:** a few public signatures were tightened during implementation (e.g.
`stationary_bootstrap_indices(n, p, rng)`; results-IO `REQUIRED_FIELDS` includes `env_fingerprint`;
`GoldPipeline` class name). Legacy aliases retained where cheap. **Status:** these are the real
signatures now; the scaffold docstrings/`FINAL_PLAN` F-refs should be read as intent, not literal API.

### INFRA-1 — engineering additions (not research scope)
**Decision:** added infra modules not in the original tree — `src/utils/{config,logging,provenance}`,
`src/data/{panel,synthetic}` — plus Makefile, pre-commit, CI, requirements-test, conftest fixtures.
**Why:** professional reproducibility; none changes the research design (scope discipline is about the
experiment, not the engineering). **Status:** adopted.

### RESEARCH-2 — Methodology validation (deep-research #2, 16 Jun)
**Decision:** methodology confirmed literature-sound (EVT/POT-GPD, PBO/CSCV-primary), with four corrections
to apply during the build:
- **EVT:** adopt bias-corrected POT (Troop et al. 2021, arXiv:2103.05059) for CVaR-1%/5%; report
  threshold-sensitivity diagnostics. → `src/feedback/measurement.py`.
- **DSR secondary, ill-defined N (confirms audit B-5/critique):** DSR's trial count N and Sharpe-variance
  are derived under iid trials → ill-defined under LLM-guided search; keep DSR secondary with a
  clustering-estimated, conservatively-bounded effective N.
- **TERMINOLOGY FIX:** Ledoit-Wolf (2008) uses the *circular* block bootstrap (Politis-Romano 1992), NOT
  the stationary bootstrap (PR 1994), and is a *Sharpe*-difference test. Correct `src/inference/bootstrap.py`
  docstrings + the methodology chapter: cite the stationary bootstrap on its own merits, do not attribute it
  to Ledoit-Wolf.
- **CVaR-difference test gap:** no published studentized difference-in-CVaR test exists → the bespoke
  bootstrap test + null-calibration (audit C-7) is the right approach; frame as a minor methodological contribution.
- **H4:** matched-compute random-search + BO arms are mandatory (no literature shows an LLM-reward edge over
  non-LLM search). **Status:** logged; corrections to apply in Phase 1–2.

### RESEARCH-2b — corpus additions + refuted claims
**Added:** `J_additional_relevant/BiasCorrectedPOT-CVaR-Troop__2021.pdf` (2103.05059);
`G_contamination_lookahead/ProfitMirage-LLMAgentLeakage__2025.pdf` (2510.07920).
**Do NOT cite as support (refuted 0-3 / 1-2):** GARCH-EVT as "the canonical" CVaR method; "out-of-cutoff
agents fail to beat random"; "contamination disappears after cutoff"; Profit-Mirage's code-generator
mitigation framing; "no automatic POT threshold-selection exists".

### AUDIT-1 — full correctness audit & fixes (16 Jun)
**Decision:** ran a strict audit (pytest + ruff + mypy + coverage + targeted probes) and fixed every
issue found:
- **CRITICAL sandbox bug:** the restricted `__builtins__` lacked `__import__`, so legitimate numpy
  reward code (`returns.mean()` / `.var()`, numpy lazy submodule loads) crashed with
  `KeyError('__import__')` — and worse, was **silently flagged "failed" during training** via
  `safe_call`, which would have corrupted the campaign. Fixed with a controlled `_safe_import`
  (numpy-rooted + already-loaded only) plus the missing safe builtins; the AST gate remains the
  security boundary. Added parametrized regression tests + a defence-in-depth test.
- **30 modules** had `from __future__ import annotations` *before* the module docstring → `__doc__`
  silently `None`. Reordered so every module/test docstring is restored.
- **7 mypy errors → 0/44:** measurement `Optional` narrowing (`_check_fitted` now returns the array);
  `synthetic._garch_sigma` tuple return annotation; `pipeline`/`loop` variable annotations.
- **Inference docstring accuracy (RESEARCH-2):** corrected the Ledoit-Wolf attribution (LW = *circular*
  block bootstrap, PR **1992**, *Sharpe*; ours = *stationary* PR **1994**), documented the CVaR-difference
  test as bespoke + null-calibrated, and added the DSR effective-N caveat.
- **PREREG flags resolved:** robust_skew sign frozen NEGATIVE-for-longer-left-tail (resolves IMPL-2);
  crossing-rate dropped; implemented `ReturnDistribution.threshold_sensitivity` (+ test); bias-corrected
  POT marked the frozen Phase-1 enhancement.
- **ruff clean:** removed a dead PBO variable and 2 unused test imports.
**Status:** **143 tests pass, ruff clean, mypy clean (44 files), coverage 89%.**

### RESEARCH-3 / GAP-CLOSURE — comparative ES test implemented; H4 confirmed a first (16 Jun)
**Decision (full report: ../../00_planning/research/GAP_CLOSURE.md):**
- **CVaR comparison gap CLOSED with a citable method, implemented + tested.** (VaR, ES) is *jointly*
  elicitable (Fissler-Ziegel 2016) → strictly consistent FZ0 score → DM comparative backtest
  (Nolde-Ziegel 2017). Implemented `src/inference/es_backtest.py` (`fz0_loss`, `comparative_es_backtest`),
  gated by a STRICT-CONSISTENCY test (FZ0 minimized at true VaR/ES). Kept the two-sample
  `cvar_difference_test` (bespoke bootstrap, Ledoit-Wolf-for-Sharpe analogue) for arm-vs-arm *realized*
  CVaR; docstrings now state the two-question distinction. Bauer (2025) low-power-at-extreme-quantiles
  caveat documented.
- **H4 is a genuine first (strength, not just risk):** no Eureka-lineage paper (Eureka/Text2Reward/
  DrEureka) benchmarked LLM reward design vs uninformed non-LLM search over the same reward space at
  matched compute → the dissertation's H4 (vs random-search-over-code + BO-over-template) fills that gap.
- **Reward hacking (D)** grounded by held papers (Skalse, Pan, Hadfield-Menell IRD, Ng-Harada-Russell);
  no finance-specific case found. **Bias-corrected POT (E)** confirmed (Troop 2021; ref impl on GitHub) —
  Phase-1; threshold-sensitivity diagnostic shipped. **Grey-lit (B):** no prior art found (re-sweep pre-submission).
- **Citation integrity:** a wrong guessed id (1607.05129 = loop quantum gravity) was caught by
  title-verification and the file deleted; Patton-Ziegel-Chen cited by venue only.
- **Papers added:** Fissler-Ziegel 2016, Nolde-Ziegel 2017, Bayer-Dimitriadis 2022, Bauer 2025.
**Status:** 148 tests pass, ruff clean, mypy clean (45 files).

### AMEND-ORIG-1 — campaign budget set to the original 30 candidates × 5 seeds (16 Jun, user-authorized)
**Decision:** per explicit user instruction, set the campaign to the original ("scoped" MASTER_PLAN branch)
budget — **candidate_budget_total = 30** (6 generations × 5 candidates/gen), **seeds = [0,1,2,3,4]** (5),
matched across all six arms. Reverts the lean 25×3. Updated: config/{llm,arms,campaign,preregistration}.yaml.
**Why:** user choice to run the richer original design; compute now allows it (Myriad/Azure-parallel, or an
accepted multi-day RTX-4050 run).
**Cost implication:** campaign ≈ 6 arms × 30 × 5 = **900 candidate trainings** (+~20 baselines ≈ ~920 runs)
≈ **~180–375 GPU-hours**; ~8–16 days serial on the RTX 4050, ~½–1 day parallel. Phase-0 smoke still pins
per-run. **Seeds-on-winners** remains an option to cut ~900 → ~205.
**NOT changed:** the audit-corrected methodology (fixed SB3 SAC + TQC secondary, empirical+EVT measurement,
loop-once, held-out fitness, FZ comparative ES test) — those fixed real issues and stand.
**Status:** PREREGISTRATION is still pre-freeze (draft), so this is a design-draft change, not a post-freeze
amendment; logged for provenance. Internal consistency verified (6×5=30; arms=llm=campaign=30).

### COMPUTE-1 — compute plan finalized (no Myriad; rented 4090 + seeds-on-winners) (16 Jun)
**Decision:** full compute/training-time analysis captured in `docs/COMPUTE_AND_TRAINING_TIME.md`. No UCL
Myriad access; owned machine is an RTX 4050 laptop; Azure-for-Students/GCP GPU is quota-blocked. **Plan:**
(1) Phase-0 prototype on the 4050 (~30 min) to measure `m`; (2) campaign on a **rented RTX 4090
(RunPod/Vast.ai) with seeds-on-winners** ≈ **$13–16, ~1.5 days** (or ~2–3 h across several GPUs); free
fallback = Kaggle+Lightning+Colab+laptop stack (~1.5–2 weeks, $0). Supersedes the earlier "$50 Colab" and
"4090+Myriad" compute assumptions. All figures scale with the Phase-0-measured `m`.

### DATA-REAL-1 — advanced prototype is REAL-DATA-ONLY; data acquisition is the critical path (17 Jun)
**Decision:** per explicit user instruction ("real data only, no synthetic"), the advanced prototype and the
campaign run **only on real, survivorship-bias-free, point-in-time market data** — **Refinitiv/LSEG**
(Datastream/RDP via UCL entitlements): the survivorship-free PIT gold panel
`data/gold/returns_panel_univ3.parquet` (5,283×953), loaded by `src/data/loaders.py::load_gold_panel`;
acquisition stack in `data_pipeline/`. Yahoo/`yfinance` and any source that drops delisted
names are **excluded** (survivorship bias — Brown et al. 1992).
**Correction (2026-06-19, R17):** this entry originally named *CRSP via WRDS* (with Norgate as the paid fallback) —
that was the *original intent*; the **realised** source is **Refinitiv/LSEG** (ADR-022/ADR-024, which already corrected
`config/data.yaml`). Prose updated to match the live panel. **Synthetic data is quarantined to the test
suite/CI and the shippable placeholder; it never enters the experiment.**
**Consequence:** data acquisition (WRDS access -> real ingest connectors in `src/data/pipeline.py` ->
two-vendor reconciliation -> delisting-return correction -> PIT top-30 -> freeze+checksum) becomes the
**critical-path blocker (task T0)**, ahead of the GPU/LLM execution layer. Compute cost (~$10, ~1/2 day) is
unchanged; the calendar is now gated by data, not GPU.
**Upside:** real data makes the N3 contamination controls (structural blinding + cutoff-stratified eval)
*live*, so even the single-seed prototype is a genuine real-data signal (directional — Henderson 1709.06560),
not a simulation artefact.
**Recorded in:** `00_planning/ADVANCED_PROTOTYPE_BLUEPRINT.md` (§0, §2, §4.1, §4.10, §7 task T0, §8).
Pre-freeze design clarification, not a post-freeze amendment. The preregistration already specified real
splits {train 2005-2014, val 2015-2017, test 2018-2025} and survivorship-free data — this makes "no synthetic
in the experiment" explicit and binding.

---

### IMPL-TESTLEG-1 — Held-out TEST leg wired into EnvBundle (punch-list Rank 1) (19 Jun)
**Decision:** implement the keystone unblocker. `EnvBundle` + `make_env_builder` (`src/env/runner.py`) gain an
optional `test_window: Window | None = None`, and `EnvBundle.test_returns(policy)` rolls the policy through the
test env but **raises `RuntimeError("test split sealed until final inference")`** whenever the bundle has no test
window. `make_env_builder` gains `embargo: int = 0` and validates *both* boundaries (`val_start ≥ train_end +
embargo`, and `test_start ≥ val_end + embargo` when a test window is given). Implements AUDIT-B2/B3 + PREREGISTRATION
§10 (select-on-validation → freeze → test-once).
**Why:** the live `EnvBundle` exposed only train+val, so nothing downstream (run_campaign, PBO, the H2 conjunction,
val→test decay, ≥20-seeds) could exist; the adversarially-verified 13-sweep punch-list (workflow `wr6yuz0yd`, 43/84
findings) ranked it #1. Sealing the test leg behind an explicit `test_window` (default `None`) makes it *structurally
impossible* for the discovery loop / search arms — which only ever build 2-window bundles — to read the 2018-2025
test split, even by accident.
**Design choices noted (directive #1):** (a) `embargo` defaults to **0** so the legacy 2-window callers
(`run_prototype.py`, `parallel.py`) are byte-unchanged; the campaign passes 21 (`config/inference.yaml`
`embargo_trading_days`). Applying the embargo at *those callers'* executed boundaries is a separate punch-list item
(Rank 18). (b) `make_walk_forward_windows` (the rolling 5y/1y/1y evaluation-fold generator the sweep bundled into
Rank 1) is **deferred to Rank 2** (run_campaign), where the `Panel` date API is read and the per-fold validation-split
question is confirmed against the frozen prereg rather than invented (directives #3/#7).
**Status:** adopted; `src/env/runner.py` + 3 new tests in `tests/test_runner.py`; full non-slow suite **199 passed /
0 failed** (was 196). Recorded in CHANGELOG [2026-06-19] + `00_planning/IMPLEMENTATION_PUNCHLIST_2026-06-19.md`
(Rank 1 ✅). Cross-ref root `DECISIONS.md` (keystone) — no new architectural thread, this implements the frozen design.

---

### IMPL-SANDBOX-1 — Sandbox AST gate denylist + candidate RLIMIT memory cap (punch-list Rank 6) (19 Jun)
**Decision:** harden `src/sandbox/executor.py`. `ast_gate` now rejects a numpy IO/FFI **attribute** denylist
(`_BANNED_ATTRS`: load/loads/save/savez/savez_compressed/savetxt/loadtxt/genfromtxt/fromfile/tofile/memmap/frombuffer/
DataSource/lib/ctypeslib/f2py/testing/mro/open) in addition to the existing dunder block; `_candidate_child` applies
best-effort POSIX `RLIMIT_AS`(~2 GiB)/`CPU`(15 s)/`NOFILE`(64)/`FSIZE`(~1 MiB) caps before `exec`, each clamped to the
hard limit.
**Why:** the live gate was dunder-only, so `np.load` (pickle-RCE) + `np.save`/`np.fromfile`/`np.genfromtxt`/`np.memmap`
passed, and the candidate child had **no** memory cap — both confirmed P0/P1 by the verified 13-sweep punch-list
(Rank 6) and by the adversarial viva (Q22). **ADR-008 (root `DECISIONS.md`) + the CHANGELOG already claimed these
controls existed**, so the code was a *falsifiable over-claim* until now; this makes ADR-008 truthful.
**Design notes (directive #1):** psutil is not a dependency → no Windows RSS watchdog (documented no-op on Windows; the
spawn-child wall-clock timeout — ADR-028 — is the backstop; the Linux/4090 campaign box enforces the caps). The
in-process `_validate_inline` fallback is intentionally uncapped. The duplicate `candidate_failed`/`reset_failure_flag`
definitions were left for Rank 18. RLIMIT pattern ported from `archive/pre_merge_repo_B/src_flat/sandbox.py::_limit`.
**Status:** adopted; `src/sandbox/executor.py` + `tests/test_sandbox.py` (10 denial cases + positive control +
POSIX-gated memory-bomb); 220 passed / 1 skipped. Recorded in CHANGELOG [2026-06-19] + punch-list Rank 6 ✅. Amends
the *implementation* of root ADR-008 (no new architectural thread).

---

### IMPL-CAMPAIGN-1 — Headline campaign driver: SEARCH→SELECT→FREEZE→TEST-once (punch-list Rank 2) (19 Jun)
**Decision:** implement `scripts/run_campaign.py` (was a STUB) as the Eureka post-loop driver that selects each arm's
winner on validation Deflated Sharpe, freezes it (`reward_source`+hash, `frozen` marker), and evaluates the frozen
winner on the held-out 2018-2025 test leg **exactly once per campaign seed** via the 3-window `EnvBundle` — one record
per (arm, seed), each carrying the realized per-step test-return vector that Rank 3's PBO consumes. Implements
PREREGISTRATION §10 (select-on-val → freeze → test-once) + AUDIT-B2/B3.
**Why:** the campaign was a stub — there was NO executable experiment; the verified sweep ranked it #2 (the spine that
turns the prototype into the H2 result; `analyze_results.py` even states "no number here enters the dissertation").
**Design decisions noted (directive #1):** (a) the `frozen`/`test_returns`/`per_period_pnl`/`reward_source` fields are
ADDITIVE (`src/io/results.py::OPTIONAL_FIELDS`), NOT new `REQUIRED_FIELDS`, because a required field breaks every
existing writer/reader — the "do not break" constraint overrode the punch-list's literal wording. (b) The contiguous
frozen splits → the 21-day embargo is carved from each later window's start; **to reconcile against the materialized
`data/gold/splits_univ3.parquet` in Rank 18** so the executed windows byte-match the frozen split. (c) Walk-forward
folds DEFERRED (Rank 2b) — no per-fold val-split invented (directives #3/#7).
**OPEN (flagged → Rank 2c):** `bayes_opt`'s archived winner is a non-executable comment stub (`# bayes_opt coeffs=…`),
so it cannot be re-instantiated for the sealed test leg; the driver records `winner_not_testable` rather than invent a
round-trip. The fix — the search arms (random_search/bayes_opt) archive the *materialized executable* reward_source so
their winners round-trip through the identical test path as the LLM arms (required for the **H4** LLM-vs-search
comparison on the held-out leg) — is tracked as punch-list **Rank 2c**.
**Status:** adopted; `scripts/run_campaign.py` + `src/io/results.py` (OPTIONAL_FIELDS) + new `tests/test_run_campaign.py`
(9 fast tests: the seal, test-once, --resume, additivity); 222 passed / 1 skipped. An order-dependent test flagged
under `pytest-randomly` — fix + joint re-verify with Rank 4 pending. CHANGELOG [2026-06-19] + punch-list Rank 2 ✅
(+ Rank 2c). Cross-ref root `DECISIONS.md` (keystone).
**Update (same day):** the reported flake was a CONCURRENT-WRITE artifact (the Rank-6 agent read `test_run_campaign.py`
while the Rank-2 agent was mid-write) — NOT a real order dependence. Confirmed: the test passes in isolation and the
full suite is order-independent across 3 shuffled runs once `pytest-randomly` is actually installed (it was declared in
pyproject but missing from the venv — now installed; the determinism guard is active for the first time).

---

### IMPL-COST-1 — Transaction cost reconciled to ½-L1-DRIFTED spec (punch-list Rank 4) (19 Jun)
**Decision:** `src/env/portfolio_env.py::step()` now computes turnover as the spec's **½-L1-DRIFTED** form — drift the
previous weights by realized returns (`w̃ = w_prev·growth / (w_prev·growth)`, cash growth 1.0), `turnover = ½‖w − w̃‖₁`,
`cost = c·turnover`, emit `info["turnover"]` — replacing the full-undrifted-L1 charge that was ~2× the spec.
**Why:** the live env charged `c·‖w − w_prev‖₁` (no ½, no drift), so every realized net return + the entire cost-sweep
+ the viva cost defence were mispriced at ~2× the nominal bps (verified sweep Rank 4 / viva Q7). The spec
(`docs/environment_spec_v1.md`) is the documented intent → this is a code-vs-spec BUG fix (spec wins), landed
pre-campaign so no reported results are invalidated.
**Reconciliation:** removed the false "Verified as-built 2026-06-10" header on the env spec (pointed at the dead
pre-merge env + a nonexistent `tests/test_portfolio_env.py`); aligned `config/environment.yaml`, `src/llm/prompts.py`,
and FINAL_PLAN L50/260/276 (the last had agreed with the buggy code — the bug's source) to the spec.
**Divergences (spec-following, directive #1):** cash growth = 1.0 (no `cash_daily_rate` key in the live config → 0);
the drift uses this step's realized `r_t` (audit-C-5 timing), matching the spec's intent.
**Status:** adopted; `src/env/portfolio_env.py` + reconciled docs + `tests/test_runner.py` (closed-form to 1e-12) + 2
new `tests/test_env.py` cost/drift tests; full suite **222 passed / 1 skipped**, order-independent. Unblocks Rank 15
(cost-sweep). CHANGELOG [2026-06-19] + punch-list Rank 4 ✅. Cross-ref root `DECISIONS.md`.

---

### IMPL-PBO-1 — PBO/CSCV primary overfitting metric wired (logit<0 + per-arm candidate matrix) (punch-list Rank 3) (19 Jun)
**Decision:** (a) corrected `src/inference/overfitting.py` to count the STRICT `logit < 0` per FINAL_PLAN B.9 + Bailey
2017 (was `<= 0`); (b) wired PBO as the primary overfitting guard via a new `scripts/analyze_campaign.py` —
`build_perf_matrix` + `campaign_pbo` computing PBO **per arm over that arm's candidates' per-period VALIDATION returns**
(`n_blocks=16` from `config/inference.yaml`), reading via `load_all`; (c) persisted per-candidate `metrics['val_returns']`
for all six arms (additive — the LLM loop + parallel path already had it; added the sequential search arms via
`evaluator.evaluate_reward_with_returns` + `run_prototype._archive_record(val_returns=)`).
**Why:** PBO/CSCV is the pre-registered PRIMARY overfitting guard (rank-based, trial-count-free — robust to guided
search where the DSR trial count is ill-defined, B.9), but `pbo()` was called only in tests and its input (per-candidate
validation vectors) was unpersisted for the search arms. This is the headline defence against "your search overfit." The
`logit<=0` vs `<0` discrepancy mis-counted exact-OOS-median ties as overfit.
**Methodology (confirmed, directive #3):** the CSCV "configs/trials" are the search CANDIDATES, PBO surfaced per arm —
independently confirmed against B.9 + the `pbo` docstring + PREREGISTRATION §10; distinct from the CPCV-on-winners
evaluation-fold scheme (`config/inference.yaml splits.cpcv`). No frozen item touched; all additive.
**Status:** adopted; `src/inference/overfitting.py` (logit) + `scripts/analyze_campaign.py` + `src/agents/evaluator.py`
+ `scripts/run_prototype.py` + `src/io/results.py` (doc) + `tests/test_analyze_campaign.py` (12 tests); full suite
**234 passed / 1 skipped**, order-independent. Unblocks Rank 8 (the difference-test family reads the same campaign
records). CHANGELOG [2026-06-19] + punch-list Rank 3 ✅. Cross-ref root `DECISIONS.md`.
**Open (Windows):** the `slow` real-SAC `test_run_prototype.py` search tests crash on a Windows torch/SB3 C-extension
access violation (the campaign runs on Linux/4090) — verify on the Linux box.

---

### IMPL-H2-1 — Campaign inference: H2 conjunction + multiplicity family + 1/N floor (punch-list Rank 8) (19 Jun)
**Decision:** extend `scripts/analyze_campaign.py` (additive) with the pre-registered selection-aware tests on the
TEST-leg records: `collect_family_pvalues` (arm-contrast × {Sharpe, CVaR} family + Benjamini-Hochberg @ q=0.05),
`h2_conjunction` (the HEADLINE test — distributional > scalar ∧ placebo ∧ scalar_cvar5, post-correction, predicted
direction), `romano_wolf_joint` (a correct JOINT stepdown), and `benchmark_floor` (the 5 benchmarks rolled through the
identical costed env; gate = winner test-DSR > best benchmark).
**Why:** PBO (Rank 3) guards overfitting, but the actual H2 hypothesis test + its multiplicity correction + the DeMiguel
1/N floor were implemented-but-never-wired (verified sweep Rank 8; PREREG §9/§10). This is the headline H2 result
machinery.
**Methodological findings (directive #1):** (1) `multiple_testing.romano_wolf` draws NO bootstrap paths (a pure
stepdown over a precomputed `(n_boot × n_hyp)` matrix); its joint-max is valid only on jointly-resampled rows, which
nothing built — so `romano_wolf_joint` now draws ONE shared stationary-bootstrap path per replication and evaluates all
contrasts on it (preserves cross-hypothesis dependence). (2) The benchmark floor uses a `WeightPolicy` shim returning an
action the env's frozen projection inverts to the target weights, so benchmarks roll through the IDENTICAL cost env
without touching `strategies.py`. H2's 3 legs confirmed vs FINAL_PLAN B.6 L83 + PREREG §1/§10.
**Status:** adopted; `scripts/analyze_campaign.py` + `tests/test_campaign_inference.py` (15 tests, incl. the 1/N
per-step gross == hand-computed equal-weight mean through the real env); full suite **261 passed / 1 skipped**. With
Ranks 1-3, the entire executable inference path (select→freeze→test-once → PBO → H2 conjunction + FDR + 1/N floor) now
exists. CHANGELOG [2026-06-19] + punch-list Rank 8 ✅. Cross-ref root `DECISIONS.md`.

### IMPL-INSPECT-1 — Reward forensics tool (§6.1 "open the black box", H2 interpretability) (punch-list Rank 7) (19 Jun)
**Decision:** implement `scripts/inspect_rewards.py` (was a STUB) — `per_generation_summary` (per-arm-per-gen fitness +
reward-code complexity + tail-term-usage trend), `feedback_responsiveness` (per-arm Pearson correlation of reward-source
EDIT magnitude vs the L1 tail-stat DELTA the LLM was fed — the "did it use the information" H2 evidence; `None` for
scalar/placebo), `hacking_taxonomy` (specification_gaming / proxy_no_tail / tautology). Read-only on the archive (via
`load_all`); reuses `analyze_results.{load_arms, interpretability, _TAIL_TERMS}` (no duplication).
**Why:** §6.1 / Phase-4.C requires QUALITATIVE evidence that the LLM reward-designer *used* the distributional feedback
(the H2 interpretability backbone that distinguishes this from a benchmark paper), but the script was a stub importing
non-existent modules (`ResultStore`, `feedback.distributional`).
**Status:** adopted; `scripts/inspect_rewards.py` + `tests/test_inspect_rewards.py` (12 tests: a finite responsiveness
score distinguishing responsive +0.92 vs unresponsive −0.98; a flagged gaming example; an archive-unchanged assertion);
full suite **261 passed / 1 skipped**. CHANGELOG [2026-06-19] + punch-list Rank 7 ✅. Cross-ref root `DECISIONS.md`.

---

### IMPL-BOOT-1 — Bootstrap difference tests relabeled (un-studentized) + arch oracle (punch-list Rank 11) (19 Jun)
**Decision:** correct the documentation of `src/inference/bootstrap.py`'s Sharpe/CVaR difference tests + `es_backtest.py`
from "studentized (Ledoit-Wolf 2008)" to a **re-centred basic (empirical) stationary block bootstrap** (size certified
by `null_calibration`); reconcile `config/inference.yaml sharpe_test` to the code; wire an
`arch.StationaryBootstrap`/`optimal_block_length` cross-check oracle in tests.
**Why:** VERIFIED against the code that the bootstrap SE *cancels* in the p-value (`|(boot−obs)/se| ≥ |obs/se| ⇔
|boot−obs| ≥ |obs|`, bootstrap.py:255-259), so the "studentized" label was a false claim an examiner would catch
(viva-falsifiable; verified sweep Rank 11). Option B (make the docs true) — near-zero risk, no numeric change.
**Reconciliation note (directive #1):** chose to fix the YAML to match the code (no `src/` caller reads `sharpe_test`
from config, so threading config in would be a real behaviour change) — config now faithfully describes `bootstrap.py`.
**Status:** adopted; `src/inference/bootstrap.py` + `es_backtest.py` (docstrings) + `config/inference.yaml` +
`tests/test_inference_crosscheck.py` (3 arch-oracle tests) + `pyproject.toml` (comment); full suite **270 passed /
1 skipped**. CHANGELOG [2026-06-19] + punch-list Rank 11 ✅ (code). Cross-ref root `DECISIONS.md`.
**PENDING frozen-doc amendment (apply in the Wave-3 freeze-prep pass, BEFORE the R9 freeze hash):**
- PREREGISTRATION.md §10 — replace "Sharpe (studentized, Ledoit-Wolf 2008 in spirit)" with: *"a re-centred basic
  (empirical) stationary block-bootstrap test; the bootstrap SE cancels in the two-sided p-value (`|boot−obs| ≥ |obs|`),
  so size is empirically certified by `null_calibration` (audit C-7), not studentized; the bootstrap (Politis-Romano
  1994 stationary) and all numerics are unchanged — label correction only (Amendment 2026-06-19, Rank 11)."*
- `config/preregistration.yaml:36` — `difference_tests: [sharpe_ledoit_wolf, cvar_difference]` →
  `[sharpe_recentred_bootstrap, cvar_difference]`.

---

### IMPL-DSR-1 — Deflated Sharpe cross-trial variance in the wired selection path (punch-list Rank 16) (19 Jun)
**Decision:** `held_out_fitness` gains `var_sr: float|None=None` (forwarded to `deflated_sharpe_ratio`); the empirical
cross-candidate Sharpe variance is computed at ANALYSIS time in a new `scripts/analyze_campaign.py::winner_dsr` (per
arm: `var_sr = np.var(per-candidate val-Sharpes, ddof=1)`; recompute the winner's DSR deflated by it, alongside the
proxy). The `deflated_sharpe.py` docstring now states `var_sr=None` is a within-series sampling-variance proxy
coinciding with the cross-trial dispersion ONLY under the homogeneous zero-skill null.
**Why:** the wired DSR used `var_sr=None` (the single-series sampling-variance proxy), not the cross-trial Sharpe
dispersion the canonical Bailey-LdP DSR requires — on a heterogeneous candidate population it silently mis-states the
(secondary) DSR (verified sweep Rank 16; DSR is secondary to PBO, but a correctness bug on a reportable number).
**Design (directive #7 — the flagged chicken-and-egg):** the population variance over ALL of an arm's candidates is NOT
knowable inside the per-candidate loop, so the per-candidate `held_out_fitness` deliberately keeps `var_sr=None` (the
wired selection statistic stays well-defined); the canonical headline DSR is recomputed downstream from the recorded
per-candidate `val_returns`. No partial-population variance is injected mid-loop.
**Status:** adopted; `src/selection/fitness.py` + `src/inference/deflated_sharpe.py` (docstring) +
`scripts/analyze_campaign.py` (`winner_dsr`) + `tests/test_inference.py` (2 golden fixtures); full suite **279 passed /
1 skipped**. CHANGELOG [2026-06-19] + punch-list Rank 16 ✅. Cross-ref root `DECISIONS.md`.

---

### IMPL-COSTSWEEP-1 — Transaction-cost robustness sweep (punch-list Rank 15) (19 Jun)
**Decision:** add a `cost_bps: float|None=None` override to `PortfolioEnv` (threaded through `EnvBundle`/
`make_env_builder`); persist per-step `metrics['test_gross']`+`metrics['test_turnover']` (via new `rollout_port_series`/
`EnvBundle.test_series`); new `scripts/cost_sweep.py` re-prices the FROZEN winners across `costs.grid_bps=[0,5,10,25,50]`
WITHOUT retraining — analytically `net_c = gross − c·turnover` (cost is charged AFTER the action, so gross/turnover are
cost-independent; audit C-5), with a `cost_bps`-overridden-env re-roll as fallback/cross-check — emitting the
winner-identity-vs-cost table.
**Why:** `costs.grid_bps` was DEAD config (no override, no harness), so the cost-robustness arm — which substitutes for
the absent market-impact model + is the viva cost defence (Q7) — could not be produced. R4's ½-L1-drifted cost +
`info['gross']`/`info['turnover']` make the analytic re-pricing exact (verified 1e-12).
**Status:** adopted; `src/env/portfolio_env.py` + `src/env/runner.py` + `scripts/run_campaign.py` (persist
gross/turnover) + `scripts/cost_sweep.py` (NEW) + `src/io/results.py` (doc) + `tests/test_cost_sweep.py` (9 tests); full
suite **279 passed / 1 skipped**. CHANGELOG [2026-06-19] + punch-list Rank 15 ✅. Cross-ref root `DECISIONS.md`.
**PENDING frozen-doc amendment (apply in the Wave-3 freeze-prep pass):** PREREGISTRATION.md §10 — add: *"Cost-robustness
sweep (pre-registered): the frozen winners are RE-PRICED across `costs.grid_bps=[0,5,10,25,50]` bps WITHOUT retraining
(`net_c = gross − bps·1e-4·turnover`, exact because cost is charged after the action), report-only/post-freeze, never
re-selecting; the winner-identity-vs-cost table confirms the distributional edge is a risk-shape effect, not a
trade-less artefact (Amendment 2026-06-19, Rank 15)."* + `config/preregistration.yaml`: `cost_sweep: {grid_bps:
[0,5,10,25,50], metric: [sharpe, cvar_05], method: analytic_reprice, report_only: true}`.

---

### IMPL-DOCSYNC-1 — IQN-era doc/prompt reconciliation + pre-merge staging quarantined (punch-list Rank 17) (19 Jun)
**Decision:** (1) quarantine `docs/staging/` → `archive/pre_merge_repo_B/staging/` (git mv, history preserved) + a
corrected `docs/FREEZE_RUNBOOK.md` that freezes the canonical root `PREREGISTRATION.md` IN PLACE (no `cp`) and calls
`make freeze` (not the nonexistent `freeze-design`); (2) rewrite `docs/distributional_feedback_schema.md` to the
off-critic empirical+EVT reality (frozen six fields; drop the IQN-critic sourcing + the dropped fields + the false
"Verified as-built" line); (3) archive the 5 inert IQN-era B-set `*_v0.md` prompts (no live code loads them — `prompts.py`
loads only the A-set; they carried IQN sourcing + a wrong `compute_reward(ctx)` contract); (4) correct compute provenance
(campaign.yaml → rtx_4050 dev / rented rtx_4090 campaign; README Phase-0 → 4050; SUPERSEDED headers on the 3 IQN-SAC reports).
**Why:** post-merge (ADR-022) the live feedback estimator is off-critic empirical+EVT, but several LIVE docs/prompts still
asserted an IQN-critic schema + IQN-SAC method — an internal contradiction undercutting H2's novelty (viva Q19) AND a
freeze hazard (the staging prereg's `cp` would have clobbered the canonical one). Docs reconcile TO the code.
**Status:** adopted; docs/config/prompt/markdown only (no importable Python touched); 7 git renames (history preserved);
engine tests **291 passed / 1 skipped**. CHANGELOG [2026-06-19] + punch-list Rank 17 ✅. Extends root ADR-022.
**Companion fix applied:** DATA-REAL-1 (below) corrected CRSP-via-WRDS → Refinitiv/LSEG. **Still to fix in the Wave-3
consistency pass:** DECISIONS.md ADR-005 freeze-hash placeholder (`make freeze-design` → `make freeze`); CLAUDE.md
keystone (Phase-0 smoke "RTX 4090" → "RTX 4050").

### IMPL-BAYESSRC-1 — bayes_opt archives a materialized executable reward_source (punch-list Rank 2c) (19 Jun)
**Decision:** add `src/baselines/reward_family.py::params_to_source(coeffs, cvar_alpha, window) -> str` (sibling of
`params_to_reward`) that emits the six-term H4 reward family at `coeffs` as runnable `def reward(...)` source matching
the canonical contract — so the BO (H4b) arm's frozen winner can be REHYDRATED for the sealed test leg (round-trips
through `validate_once` exactly like the LLM / random-search arms). Verified: bit-for-bit reproduction of the in-memory
closure (max abs diff 0.0 over a 60-step stateful replay); passes ast_gate + validate_once; `_reinstantiate_frozen_winner`
rehydrates a materialized BO winner without `winner_not_testable`.
**Why:** the BO arm only held an in-memory closure; archiving `# coeffs=[...]` left its winner non-rehydratable →
`winner_not_testable`, BREAKING the H4 LLM-vs-search held-out comparison (flagged at Rank 2).
**Status:** PRIMITIVE adopted + verified; `src/baselines/reward_family.py` + `tests/test_reward_family_source.py` (11
tests); fast suite green. ⚠ **WIRING PENDING (Rank 2c-wire):** the 2 stub call sites — `scripts/run_prototype.py:240` +
`src/orchestration/parallel.py:141` — must swap `# coeffs=...` → `params_to_source(coeffs, cvar_alpha=alpha,
window=window)`. Those files were owned by the concurrent Rank 18; once R18 landed the orchestrator applied the 2-site swap
(`scripts/run_prototype.py` BO branch + `src/orchestration/parallel.py` `kind=='coeffs'` worker → `params_to_source`);
targeted search/family/campaign suite green. **Rank 2c COMPLETE end-to-end.** CHANGELOG [2026-06-19] + punch-list Rank
2c ✅. Cross-ref root `DECISIONS.md`.

---

### IMPL-CLEANUP-1 — Embargo at executed split boundaries + low-risk cleanups (punch-list Rank 18) (19 Jun)
**Decision:** (1) the executed search splits now read the MATERIALIZED `development.validation_post_embargo` boundary
from `data/gold/splits_univ3.parquet` (`loaders.embargoed_val_start`, 21-session fallback) so both executed paths
(run_prototype + parallel) byte-match the frozen materialization (val→2015-02-03) instead of abutting train/val with no
embargo (PREREGISTRATION §7); (2) removed the shadowed duplicate `candidate_failed`/`reset_failure_flag` in
`executor.py`; (3) guarded the CVaR penalty in `held_out_fitness` against NaN on empty/non-finite series; (4)
`set_global_seed(deterministic_torch=True)` parity in run_prototype; (5) created `CITATION.cff` + `DEVIATIONS.md`; (6)
fixed the checksum exact-relpath branch (`parents[1]→parents[2]`).
**Why:** the executed search windows abutted with NO embargo (violating §7), the executor had genuine dead duplicate
functions, and the rest is correctness/provenance hygiene removing latent foot-guns before the campaign (verified sweep
Rank 18). Reading the materialized splits also resolves the Rank-2 window-byte-match flag.
**Status:** adopted; `src/data/loaders.py` + `scripts/run_prototype.py` + `src/orchestration/parallel.py` +
`src/sandbox/executor.py` + `src/selection/fitness.py` + new `CITATION.cff`/`DEVIATIONS.md` + tests (test_embargo_splits
7 + fitness/checksum); full suite **302 passed / 1 skipped**. CHANGELOG [2026-06-19] + punch-list Rank 18 ✅. Cross-ref
root `DECISIONS.md`.

---

### IMPL-POWER-1 — Power-analysis machinery + SESOI/TOST (punch-list Rank 12) (19 Jun)
**Decision:** implement `scripts/power_analysis.py` (fix the broken `src.regimes` import → `independent_regime_count`):
a vectorized MC power routine over the arm-level re-centred bootstrap difference test, a Šidák selection-aware α, MDE at
80% power, and a symmetric-margin TOST equivalence test; σ/SESOI/TOST as CLI params; fill `docs/POWER_ANALYSIS.md` with
concrete values (N=6, n_eff=30, α_eff=0.0085, MDE=0.269 DSR, trial count=180); σ flagged pilot-TBD.
**Why:** the script was a stub with a ghost import, yet it must justify the trial count + give a TOST margin so a
non-rejection of H2 is reported as a BOUNDED effect, not an underpowered failure (viva Q21). Pre-freeze blocker.
**Adopted SESOI = 0.05 validation-DSR units (TOST ±0.05):** a ~5pp DSR shift ≈ 0.10-0.15 annualised test-Sharpe — the
smallest gap surviving the Harvey-Liu t>3 hurdle net of turnover costs; stricter than the 0.20 placeholder. (The freeze
is the user's action, so this is the recommended/adjustable pre-freeze setting.)
**Status:** adopted (code); `scripts/power_analysis.py` + `docs/POWER_ANALYSIS.md` + `tests/test_power_analysis.py`
(14); full suite **327 passed / 1 skipped**. CHANGELOG [2026-06-19] + punch-list Rank 12 ✅ (code).
**PENDING frozen-doc amendment (the Wave-3 pass):** PREREGISTRATION.md §10 — *"Pre-freeze amendment (2026-06-19, power
analysis / viva Q21): the analysis plan adds a pre-registered SESOI = 0.05 validation-DSR units + a symmetric TOST
equivalence margin = ±0.05 DSR for the headline H2 (distributional vs scalar) contrast; a non-rejection is reported as a
bounded effect (the MDE at 80% power / Šidák-α, in docs/POWER_ANALYSIS.md), and if the TOST 90% bootstrap CI for the
mean-DSR difference lies inside ±0.05 the arms are practically equivalent within the SESOI; σ filled from the pilot
pre-freeze; hypotheses/arms/seeds/budget/splits unchanged."* + `config/preregistration.yaml inference: {sesoi: 0.05,
equivalence_margin: 0.05}`.
**Flag (data, not prereg):** gold `vix` decimal vs `regimes.yaml` point thresholds → regime auto-detect collapses to
N=1; fix before the campaign (rescale `vix` to points, or set decimal thresholds calm=0.15/stress=0.25).

---

### IMPL-REPRO-1 — Reproducibility/provenance trio: env.json + prompt-archival + lock target (punch-list Rank 14) (19 Jun)
**Decision:** (a) `scripts/capture_env.py` EXTENDS `provenance.env_fingerprint` (pip freeze + nvidia-smi +
torch/cuda/cudnn + determinism env + seed) → `outputs/<run>/env.json`, wired into BOTH executed archive paths; the
bare-string `env_fingerprint` becomes `{label, env_json_sha256}`. (b) Persist the rendered prompt in the LLM-loop +
parallel records + a `prompt.txt` sidecar (round-tripped by `load_run`); `prompt`/`prompt_hash` additive in
OPTIONAL_FIELDS. (c) Makefile gated `lock` target + pin `pytest-randomly>=3.15,<5`.
**Why:** results must REPLAY from the archive (CLAUDE.md prime directive 6 + ADR-002 CI-grade repro), but the archive
DROPPED the prompt and persisted a bare-string env fingerprint, not real provenance; and the declared `pytest-randomly`
determinism guard was missing from the venv (verified sweep Rank 14).
**Status:** adopted; `scripts/capture_env.py` (new) + `src/orchestration/parallel.py` + `src/io/results.py` +
`src/llm/loop.py` + `scripts/run_prototype.py` + `Makefile` + `pyproject.toml`; full suite green. The
`requirements.lock` FILE itself is GATED (generated on the Linux GPU box for the cu124 wheels). CHANGELOG [2026-06-19] +
punch-list Rank 14 ✅. Cross-ref root `DECISIONS.md`.

---

### IMPL-UNIV4-1 — univ4 Shumway-STYLE delisting build (CODE; rebuild gated) (punch-list Rank 5) (19 Jun)
**Decision:** (1) FIX the `apply_shumway_corrections` KeyError landmine — book the surcharge on the LAST VALID session
(`_last_valid_label`), compounded MULTIPLICATIVELY `(1+r)(1+dl)−1` (never additive), all-NaN → `shumway_skipped_no_obs`,
vendor-terminal preferred; (2) wire STAGE-7 into `build_universe(apply_delisting=False)` (default off → byte-identical;
gated on the licensed re-run), feeding the corrected frame to `build_gold` as `_univ4`; (3) `loaders.gold_suffix()`
(`LLM_RP_GOLD_SUFFIX`, default univ3, NOT flipped); (4) 13 tests incl. the tail-preservation invariant.
**Why:** the live `univ3` panel `liquidate_to_cash`-zero-fills dead names INTO the exact left tail H2 reads (M3/M4 review
failure); `apply_shumway_corrections` existed but had ZERO build callers + a KeyError landmine (booking onto an
off-grid/all-NaN row). This delivers the corrected build (Shumway-STYLE transplant per repo-agent G).
**Status:** CODE adopted + verified (327 passed; tail-preservation gap > 1e-4); `data_pipeline/src/data/membership.py` +
`build_universe.py` + `src/data/loaders.py` + `tests/test_membership_shumway.py`. ⚠ **GATED:** the real `_univ4` parquet
needs `make pull-universe LIVE=1` (Refinitiv creds) → `build_universe(suffix="_univ4", apply_delisting=True)` → set
`LLM_RP_GOLD_SUFFIX=univ4` + report the {0,−30,−55,−100}% band. **Headline tail numbers remain invalid until that gated
rebuild + env reload.** Implements the build ADR-024 anticipated. CHANGELOG [2026-06-19] + punch-list Rank 5 ✅ (code).
Cross-ref root `DECISIONS.md`.

---

### IMPL-FREEZE-1 — Pre-registration freeze gate `scripts/freeze.py` (punch-list Rank 9) (19 Jun)
**Decision:** implement `scripts/freeze.py` — canonical SHA-256 over LF-normalized `PREREGISTRATION.md` ++
`config/preregistration.yaml` (prose-then-yaml, fixed order); a prose↔YAML gate over the 6 freeze-relevant fields
(seeds, `testing_family.m`, difference_tests, sesoi, equivalence_margin, cost_sweep.grid_bps); a Phase-0 precondition;
`--check` (CI drift guard, `make freeze-check`); and a user-gated write path (flip frozen/freeze_hash, ADR-005
DECISION_LOG append, signed tag `prereg-v1.0`, `ots stamp` — all best-effort, NOT executed here).
**Why:** the freeze is the legitimacy gate for the whole pre-registration regime (CLAUDE.md directive 3), but
`freeze.py` was a stub — the "frozen design" claim was unenforceable. The canonical hash + prose↔YAML assert now make
the design tamper-evident; `make freeze-check` guards drift in CI.
**Status:** adopted; `scripts/freeze.py` + `tests/test_freeze.py` (19) + `Makefile` (`freeze-check`); full suite **346
passed / 1 skipped**; mypy + ruff clean. `--check` PASSES on the current consistent prereg (canonical hash
`7e6da01f73811e4e92f8b05643b0222170743badcbf7976b1d6879a3193e41d6`, deterministic). **The real `make freeze` (set
frozen=true, write the hash, sign the tag, OTS) is the user's GATED action — NOT run.** Completes the ADR-005 freeze
mechanics. CHANGELOG [2026-06-19] + punch-list Rank 9 ✅. Cross-ref root `DECISIONS.md` (ADR-005).

---

### IMPL-AUDITFIX-1 — Final acceptance-audit P1 fixes: DSR units + 2 sandbox escapes (19 Jun)
**Decision:** fix the 3 confirmed P1 defects the final acceptance-audit workflow (6 auditors) surfaced in IMPLEMENTED
code: (1) `analyze_campaign.winner_dsr` computes the cross-candidate `var_sr` with `periods_per_year=1` (per-period) —
was annualized (×252), collapsing the canonical headline DSR to ~0; (2)+(3) add `recfromtxt`/`recfromcsv`/`fromregex`
(read-escapes) + `dump`/`dumps` (write-escapes) to the sandbox `_BANNED_ATTRS`.
**Why:** the DSR units bug silently mis-stated a REPORTED headline number — it slipped through because R16's test
hand-computed `var_sr` and bypassed `winner_dsr`'s internal `sharpe_ratio(vec)` call (the function was never invoked
under test). The sandbox escapes are the same "forgot to ban X" class ADR-008 chased: `recfromtxt`/`recfromcsv` alias
`genfromtxt`; `dump`/`dumps` mirror the already-banned `tofile`. The auditors verified all 3 against the real code/gate
(the sandbox escapes reproduced empirically via the venv).
**Status:** adopted; `scripts/analyze_campaign.py` + `src/sandbox/executor.py` + `tests/test_analyze_campaign.py`
(`winner_dsr` is now invoked under test) + `tests/test_sandbox.py` (5 new denial cases); full suite **352 passed /
1 skipped**. The **freeze hash is UNCHANGED** (the hashed prereg/yaml are untouched). CHANGELOG [2026-06-19].
**Recommended hardening (noted, future ADR):** replace the numpy denylist with a positive ALLOWLIST of pure-array ops
(the "forgot to ban X" class recurs); `RLIMIT_FSIZE`/namespace is the backstop. **Residual P3:** `scripts/build_gold.py`/
`verify_gold.py` are deferred-by-design stubs not labelled "deferred" — doc polish, not a defect.

---

### IMPL-WIRING-1 — Run-readiness: real Anthropic Pass-B wiring + the vix-units fix (19 Jun)
**Decision:** complete the ADR-034 §"Wiring (queued)" items so the headline campaign can run the real reward-author
(Claude Sonnet 4.6) rather than the keyless stub, and fix a silent regime-collapse data bug. Five threads:
- **(1) The campaign could not call the real LLM — the actual blocker.** `scripts/run_campaign.py::main` never read
  `provider`/`pass`; the `run_headline_campaign(...)` call fell through to its defaults (`pass_mode="A", provider="stub"`)
  with `generations` hardcoded to 1 — so the dissertation's headline script would silently run the StubDesignerTransport
  on every invocation. `main` now reads `config/campaign.yaml: llm.{pass,provider,generations}` and threads them through;
  `--dry-run` still forces the stub so the smoke never burns the key.
- **(2) Temperature stays 1.0 (Eureka), NOT 0.** The continuation summary said "set temperature=0"; that is WRONG and
  would gut the search. `src/llm/loop.py:292-296` samples all `candidates_per_gen` candidates from the SAME prompt, so
  within-generation diversity is entirely sampling-driven → temperature MUST be > 0 (ADR-016 = 1.0 per Eureka). ADR-033's
  "Sonnet honors temperature=0" is a provider-selection criterion ("reproducibility comes from the archive, not live
  determinism") — not a directive to run at 0. Reconcile-don't-assume (CLAUDE.md d.1): temperature = 1.0 everywhere.
- **(3) Provider transports hardened — `src/llm/client.py`.** `make_anthropic_transport` now: prompt-caches the static
  system block (the K-shared-context lever, ADR-016); owns retry/backoff via lazy `tenacity` (exp 1→30 s, ≤6 attempts) on
  a portable `_is_transient_api_error` predicate (connection/timeout/rate-limit/5xx; 4xx terminal) with the SDK
  `max_retries=0`; archives token `usage` via a callable `_AnthropicTransport.last_usage`; accepts `temperature`.
  `make_openai_transport` gains a symmetric `temperature`. `ProvenanceRecord` += optional `usage`; `LLMClient` is
  provider-aware (default `anthropic` + `ANTHROPIC_API_KEY`, dispatch in `_ensure_transport`) — closes the latent
  OpenAI-default footgun. tenacity/anthropic stay LAZY (core imports without them; tenacity-absent → no-retry).
- **(4) Configs reconciled to ADR-016/033** (were placeholders): `config/prototype.yaml: llm` model→`claude-sonnet-4-6`,
  key→`ANTHROPIC_API_KEY`, +`temperature: 1.0`; `config/campaign.yaml` +`llm` block (`pass:B, provider:anthropic,
  generations:6`); `config/llm.yaml` provider/model/key/temperature corrected + `open_weights_check_model` left an HONEST
  `PIN_ME` (ADR-033 Llama-4; no fabricated HF revision). `pyproject.toml` += `tenacity>=8.2`. Orchestrators
  (`run_prototype.run_arm`, `parallel._drive_llm_arm`) thread `temperature`; api_key default flips `LLM_API_KEY` →
  `ANTHROPIC_API_KEY`.
- **(5) vix-units bug (audit B-6).** VERIFIED against the frozen gold (not assumed): `cash_features_*.parquet` store vix
  as a FRACTION (FRED VIXCLS/100 — 0.0914..0.8269), but `config/regimes.yaml` thresholds are POINTS (15/25) → all 5,282
  dates labelled calm → `independent_regime_count` = 1, silently zeroing the regime-stratified H2-power evidence. The env
  obs is scale-agnostic (raw `panel.vix[t-1]` under VecNormalize). Fix: `load_gold_panel` normalizes vix to points at the
  load boundary, magnitude-GUARDED (`median < 2.0 → ×100`) so a future points-storing rebuild is never double-scaled.
  Chosen over decimal thresholds because everything else (thresholds, synthetic ~10-50, trainer "~10-80", env doc "FRED
  VIXCLS") is already points — only the frozen gold was fractional; this keeps one conventional, viva-defensible unit and
  leaves the parquet untouched.
**Why:** ADR-034 left the Anthropic transport "added but not wired"; the campaign driver still pointed at the stub, so
"run the experiment" was impossible. The temperature catch prevents a silent diversity-collapse that would invalidate H3.
The vix fix restores the regime stratification that bounds the H2 power claim.
**Status:** adopted; `src/llm/client.py` + `scripts/run_campaign.py` + `scripts/run_prototype.py` +
`src/orchestration/parallel.py` + `src/data/loaders.py` + `config/{prototype,campaign,llm,regimes}.yaml` +
`pyproject.toml`; `tests/test_llm_transport.py` (NEW, 16) + `tests/test_agents.py` (provider-aware) +
`tests/test_loaders.py` (gold-vix regression). **Full non-slow suite 373 passed / 1 skipped**, order-randomized; gold
regimes 1 → 214 independent episodes. **Freeze hash UNCHANGED** (no prereg/yaml touched). CHANGELOG [2026-06-19].
**Gated (unchanged):** `make freeze`; univ4 rebuild; `requirements.lock` (now must include `tenacity`) on the 4090;
pilot → `power_analysis --sigma-dsr`; the campaign run. Key management per ADR-033 stays the user's.
**Noted for a future ADR:** the campaign reads model/key from `prototype.yaml: llm` (shared search config) rather than
owning its own — documented + consistent, but a cleaner design would let `run_headline_campaign` pass them explicitly.

---

### IMPL-RUNPREP-1 — Refinitiv access verified live + probe fixes + full run-readiness (19 Jun)
**Decision:** at the user's request ("fully prepare everything for a run"), verify all run prerequisites
end-to-end and correct a data-provenance error.
- **Provenance CORRECTION:** the frozen `univ3` gold is **licensed Refinitiv survivorship-free PIT** (953 RICs
  incl. 333 dead; `data_pipeline/README.md`), NOT yfinance as an earlier turn this session wrongly claimed
  (over-read of the datasheet vendor tags). CLAUDE.md's "Refinitiv/LSEG" was right; ADR-015's yfinance
  fallback was an interim 06-10 state superseded by the 06-12 Refinitiv build. Viva claim = Refinitiv/LSEG.
- **Entitlement VERIFIED LIVE (06-19):** the `.env` platform creds open a headless `GrantPassword` session
  (no Workspace) and pull live pricing + the dead-ticker `LEH.N^I08` 2008 history; the official probe returns
  **7 PASS** incl. PIT membership content-validation (Lehman 2008 leaver) and delisted coverage -> verdict
  *"proceed with the full PIT build."* So `univ4` (apply Shumway -30/-55% delisting returns vs the provisional
  `liquidate_to_cash` fill; likely a re-process of already-pulled delisting metadata) is unblocked.
- **`data_pipeline` probe bugs fixed (post-unification):** `acquire.load_env` now searches `ROOT/.env` AND
  `ROOT.parent/.env` (the unified repo root) — it was looking only inside `data_pipeline/`, so creds never
  loaded and the session fell back to the desktop proxy; `probes.write_report` now writes UTF-8 (it crashed on
  the user's cp1251 locale emitting the status icon). `.env` updated with the pasted Refinitiv creds (Anthropic
  key preserved; values never echoed).
**Why:** the run could not be prepared while the Refinitiv probe was silently desktop-only and the data
provenance was mis-stated; both are legitimacy-critical for the dissertation's data chapter + viva.
**Status:** adopted; `data_pipeline/src/data/{acquire,probes}.py`; `.env` (gitignored). Verified: full suite
**373 passed / 1 skipped**; `freeze.py --check` OK (hash `7e6da01f...`, pre-freeze); `run_prototype.py --dry-run`
EXIT 0 (real SAC end-to-end, 18.3s); `docs/evidence/entitlement_report.md` regenerated (7 PASS).
**Deliverable:** `docs/RUN_READINESS_2026-06-19.md` (full operational runbook). **Freeze hash UNCHANGED** (no
prereg/yaml touched). CHANGELOG [2026-06-19]. **Security:** Refinitiv password + Anthropic key are in the chat
transcript -> rotate post-project.
**Gated (unchanged):** pilot -> `power_analysis --sigma-dsr`; `make freeze`; optional `univ4` delisting build;
`requirements.lock` (incl. `tenacity`) on the 4090; the campaign run.

### IMPL-AUDIT2-1 — Provider-neutral LLM architecture + deep adversarial audit (38 findings fixed) (19 Jun)
**Decision (engine-line record for ADR-035; full design rationale there):** at the user's mandate ("engineer
everything … gemini 3.5 flash for the prototype, opus 4.8 for the main … find all bugs/vulnerabilities/issues
… fix everything … verify strictly and deeply"), (1) build the provider-neutral transport (`build_transport`
registry; Gemini via the OpenAI-compatible endpoint, no new dep), thread a per-stage `llm_cfg` so the campaign
(Opus 4.8) and prototype (Gemini 3.5 Flash) own separate authors, and add temperature-free prompt-variation
diversity for the temperature-rejecting Opus; and (2) run an 8-dimension × 3-vote adversarial audit (134
agents) → **38 confirmed findings** (3 critical / 9 high / 11 medium / 15 low), all engineering issues fixed.
- **Critical:** #1 a missing fenced/prose **code-extraction** shim (raw Opus/Gemini output → `ast.parse`
  SyntaxError → every candidate rejected for formatting → a silent zero-candidate campaign); #2 the sequential
  **search arms drew OS entropy** not the run seed (non-reproducible winner); #3 the AST gate was a denylist
  with a **verified numpy-submodule RCE** (`np._pytesttester.os.system`) → replaced with a numeric **allowlist**.
- **High:** #4/5/8 SEARCH-vs-TEST **training-budget mismatch** (25k vs 50k) → one threaded `agent_cfg`; #6
  `--dry-run` now keyless; #7 gold **VIX double-lag** → `Panel.vix_prelagged`; #10/17 resume **frozen/test
  desync** → resume-aware SEARCH/FREEZE + hash guard; #11 TEST **per-seed `set_global_seed`**; #12 real-shaped
  validation fixture + containment-boundary doc.
- **Medium/Low (22):** LLM provenance persistence (#16/#36), `ffill` return-fabrication (#20), budget guard
  requires accepted>0 (#21), candidate_id/reflection parity (#22/#33/#34), frozen-family guard (#24), env
  vol-window guard (#28), `deflated_sharpe` alias (#31), `winner_dsr` trial count (#32), OpenAI `max_tokens`
  (#35), env.json verify (#37), `prompt_hash` removal (#38), and the rest — see CHANGELOG [2026-06-19].
**Why:** the critical findings were legitimacy- and budget-critical (a fenced-output starve would burn the
full GPU+API budget for zero usable results; the RCE defeats the sandbox the untrusted-reward design depends
on). The audit's value is independent adversarial coverage of exactly the real-run paths the fake-based fast
suite never exercises.
**FLAGGED, NOT changed (CLAUDE.md §3 — pre-registered analysis plan needs user/supervisor sign-off):** #9/#14
the headline H2 inference **averages the per-seed return series** before the bootstrap (anti-conservative,
~√N variance collapse); #18 the **H2 conjunction / family-p-value** functions are implemented + unit-tested but
**not wired** into `analyze_campaign`'s entry point; #13 the sealed **test leg reuses the fixed 2005-cohort
universe** across 2018-2025 (composition bias the prototype prose itself calls disqualifying). These are
raised for decision, not silently rewritten.
**Status:** adopted; touched `src/{sandbox/executor,llm/client,llm/loop,orchestration/parallel,data/loaders,
data/panel,env/portfolio_env,io/results,inference/deflated_sharpe}.py` + `scripts/{run_prototype,run_campaign,
analyze_campaign,analyze_results,build_gold,verify_gold}.py` + configs. Verified: full non-slow suite **404
passed / 1 skipped, ×3 order-randomized**; +18 regression guards (`tests/test_audit_regressions.py`); `ruff`
clean (src/scripts/tests); `mypy` 0-new (13 baseline); **freeze hash `7e6da01f…` UNCHANGED** (no frozen field
touched); independent re-audit (verify-fix + regression-hunt) confirms the critical/high fixes. CHANGELOG
[2026-06-19]; design rationale in `../DECISIONS.md` ADR-035. **Gated (unchanged):** the flagged statistical
items + `make freeze` + the campaign run.

### IMPL-AUDIT3-1 — Headline H2 inference corrected to per-seed rliable + conjunction wired + universe limitation (20 Jun)
**Decision (engine-line record for ADR-036; full rationale there):** at the user's direction on the three
flagged pre-registered-analysis items ("do whatever maximises my grade, work hard"; pre-registration still
`frozen: false`), (1) **#9/#14** replace the anti-conservative seed-AVERAGED-series difference test with the
rliable per-seed method — per-seed Sharpe/CVaR -> IQM -> paired stratified bootstrap over the shared training
seeds (`src/inference/bootstrap.{iqm,paired_seed_difference_test}`), carrying the across-seed variance;
null-calibrated to ~5% (correctly sized) vs the old ~21% over-rejection on a true null. `collect_family_pvalues`,
`romano_wolf_joint`, `h2_conjunction` rewired to the per-seed unit; family/correction/conjunction/SESOI
unchanged (PREREGISTRATION R16). (2) **#18** wire `h2_conjunction` (+ the R13 family-equals-frozen assert)
into `analyze_campaign.analyze()`/`write_report`/`main` — it had no caller, so the documented headline test
never ran. (3) **#13** document the 2005-cohort sealed-test-universe as a limitation (loud `run_campaign`
caveat; 11/30 names differ from the 2018 PIT cohort) and add `load_gold_panel(window_start=...)` so a PIT
walk-forward robustness re-evaluation is runnable (PREREGISTRATION R17).
**Why:** the averaging was a genuine, empirically-demonstrated anti-conservative error (a stats-savvy
supervisor would catch it); a correct, conservative, wired headline inference makes a null defensible — the
pre-registration's purpose. The universe is a design choice -> transparent documentation + a runnable
robustness path, not a unilateral change to the frozen experiment.
**Status:** adopted; `src/inference/bootstrap.py`, `scripts/analyze_campaign.py`, `src/data/loaders.py`,
`scripts/run_campaign.py`, `PREREGISTRATION.md` (R16/R17), `config/preregistration.yaml`,
`tests/{test_campaign_inference,test_audit_regressions,test_loaders}.py`. Verified: full non-slow suite **410
passed / 1 skipped**; `ruff` clean; `mypy` 0-new; `freeze.py --check` passes prose<->yaml (canonical hash
`7e6da01f -> a1f458d5 -> 5aaf1fc4`, intended pre-freeze refinement; `freeze_hash` null). CHANGELOG
[2026-06-20]; rationale in `../DECISIONS.md` ADR-036. **Gated/supervisor:** the PIT-universe robustness
re-evaluation (compute) + `make freeze`.
