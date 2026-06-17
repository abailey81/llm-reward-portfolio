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

### PHASE-0 — smoke-test result (TO FILL)
**Decision:** _(GREEN/AMBER/RED)_ · per-run minutes (SAC) _·_ (TQC) _·_ critic-loss start/end ·
4090 confirmed _(y/n)_ · fixes applied. **Status:** _precondition for the freeze._

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
campaign run **only on real, survivorship-bias-free, point-in-time market data** — CRSP via WRDS (UCL
postgraduate access; confirm the CRSP stock module is in UCL's subscription, escalate to the WRDS admin),
with **Norgate Data** as the documented paid fallback. Yahoo/`yfinance` and any source that drops delisted
names are **excluded** (survivorship bias — Brown et al. 1992). **Synthetic data is quarantined to the test
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
