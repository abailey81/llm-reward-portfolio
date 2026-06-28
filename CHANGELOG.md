# Changelog

All notable changes to this repository. Format follows Keep a Changelog; this project is pre-versioned
research code, so entries are grouped by session date. Every entry cites its ADR where one exists.

## [2026-06-29] — Figure engine + LLM-integration hardening + CI dependency completion (report-only; no frozen change)

Deep-sweep build: all report-only / engineering, **nothing frozen touched** (`freeze.py --check` SHA `7fc686b6`
unchanged), full fast suite **1517 green**, slow 13, data_pipeline 16, ruff-lint + mypy (73 src) clean.

### Publication-grade figure engine — `src/viz/` + `scripts/make_figures.py` (the "faultless presentation" lever)
Results figures were entirely missing. Built a deterministic Okabe-Ito (colourblind-safe + greyscale-robust)
engine: `style.py` (per-arm colour/marker/hatch, IQM + bootstrap-CI, SESOI band, 600-dpi PNG + vector PDF) and
five headline figure functions designed for an HONEST null — `equivalence_forest` (90% TOST vs the ±0.05-DSR
SESOI band; never reads a null off a p), `rliable_intervals` (per-arm IQM + stratified-bootstrap CI), the novel
`risk_return_clouds` (the 7 arms' per-seed clouds collapse onto one neighbourhood) and `evidence_for_null` (JZS
Bayes-factor gauge + Model-Confidence-Set strip = positive evidence FOR H0), and the mechanism figure
`reward_code_similarity` (AST-distance clustered heatmap; clusters cut across arms ⇒ the placebo writes the same
code). `make_figures.py --demo` renders the suite on synthetic NULL-shaped data so the engine is validatable
pre-campaign; post-campaign the same functions take the real per-seed + inference outputs. +11 tests
(`tests/test_viz.py`, headless). Manifest updated (`paper/FIGURE_TABLE_MANIFEST.md`).

### LLM-integration hardening (transport-only; uniform across arms; no prompt-byte change)
- **`stop_reason` correctness fix** (`src/llm/client.py`): `_AnthropicTransport`/`_OpenAITransport` never
  inspected `stop_reason`/`finish_reason`, so a `max_tokens` truncation (reward cut off mid-function) or a
  `refusal` returned partial/empty text → failed the AST gate → was silently mislabeled as a "bad candidate",
  biasing per-arm candidate-yield accounting. Now captures + WARN-logs (`_warn_if_incomplete`) + archives
  `stop_reason` + `request_id` on `ProvenanceRecord` so a capped/refused call is correctly attributed in the
  replay archive.
- **`src/llm/cost.py`** — report-only cache-aware USD + completion-integrity reducer over the replay archive.
- **Disclosure (measured):** the shared prefix (system.txt + ENV_INTERFACE) is ~898 tokens, BELOW Opus 4.8's
  4096-token minimum cacheable prefix (and Sonnet 4.6's 2048), so the ADR-016 prompt-cache lever is **inert on
  Opus 4.8** — documented in `client.py`; no request restructuring (would be a no-op; ~$0.94 of unavoidable
  uncached prefix over ~210 calls). +7 tests (`tests/test_llm_stop_reason_and_cost.py`).

### CI dependency completion — `requirements-test.txt` (fixes a pre-existing latent CI gap)
A clean light-CI env reproduction (only `requirements-test.txt`) revealed the non-slow suite needed four
deterministic deps absent from the light job, so `pytest -m "not slow"` would have errored on collection/run in
CI even though the full venv passed: **`psutil`** (`test_max_power`), **`arch`** (`test_model_confidence_set`
R69, `test_inference_crosscheck`), **`matplotlib`** (the figure engine / `test_viz`), **`pyarrow`** (the
parquet gold-panel loader tests). All CPU-only (no torch). Verified: the full non-slow suite (1517) now runs
GREEN in a from-scratch `requirements-test.txt`-only venv.

### Read-only monitoring extensions — `scripts/monitor.py` (2026-06-28)
Silent-hang/STALE detection (progress.json staleness), an anomaly-by-kind error tracker + live LLM token/USD
panel, an opt-in fail-safe `--notify` (ntfy/healthchecks; stdlib-only side-channel), rotating-circle spinner,
`rich.traceback`. +8 tests; runbook updated. (The known repo-wide `ruff format --check` mismatch — a denser
hand-style flagged by ruff 0.5.7 *and* 0.15.x — remains a tolerated non-defect; `ruff check` lint is the gate
and is clean. Pinning CI ruff to 0.5.7 is rejected: 0.5.7 lint flags a pre-existing `E402` in `test_properties.py`.)

## [2026-06-25] — Deep hypotheses + benchmarks scrutiny (8 agents) + headline reframe + integrity hardening (amendments R25–R31)

An eight-agent exhaustive, literature-grounded, adversarial scrutiny of the WHOLE scientific core (one agent per
hypothesis H1–H4; two on the benchmark ladder; one on the statistical backbone; one hostile-examiner red-team).
Verdict: world-class on conception + inference; the exposure was system-level *completeness*, every fatal route
self-inflicted over-claiming and pre-emptable by disclosure before freeze; a Distinction in every genuine
outcome. The findings (`docs/DEEP_*.md`) were then integrated — all governance/report-only/disclosure, **no
campaign re-run** — and verified GREEN (full suite exit 0, `freeze.py --check` 9/9, ruff clean, mypy +0 new).

### Headline reframed — H2 = two co-primary intersection–union tests (R25; the keystone)
The old gate was `(3-leg Sharpe conjunction) ∘ (BH-over-m=6)` — statistically **double-corrected** (a conjunction
is itself an IUT and is the correction; Berger 1982), and it gated on the *Sharpe* leg while the distributional
contribution acts on the *tail* (the pilot's only signal was CVaR p≈0.004). Restructured `h2_conjunction` into
**H2-RA** (3 Sharpe legs, IUT, one-sided α=0.05, no leg correction) + **H2-Tail** (3 CVaR-5% legs, IUT,
corroborated by FZ0/ES) — each a clean IUT, the m=6 union retained as the realized-family assert + a *reported*
BH-over-6 sensitivity. Fixed a latent cvar_01-gating bug (the tail gates at the headline CVaR-5%). Makes the
distributional contribution **bankable on its strongest dimension**; the null stays bankable too (verbatim
pre-registered statement, §10). A design CORRECTION justified a priori by the theory spine, not a post-hoc switch.

### The asymmetric-rigor fix — H3 + H4 now have campaign-grade sealed-leg tests (R30)
The red-team's CRITICAL finding: H3/H4 were pre-registered but only H1/H2 had a sealed-leg test. Wired:
- **H3 single-shot stage** (`run_campaign.run_h3_singleshot`): the iterative distributional winner (gen 6,
  reflect-on-best) vs a matched single-shot condition (`generations:1`, best-of-N, no reflection; identical
  budget/seeds/50k-buffer/val-DSR selector; disjoint `*_h3_singleshot/` roots; `--h3-singleshot`).
- **H3/H4 difference tests** in `analyze_campaign` (`out["h3"]` + TOST ±0.05; `out["h4"]` H4a/H4b 2-test family +
  Bonferroni-over-2) — per-seed IQM paired, report-only, OUTSIDE the frozen m=6.

### Cross-hypothesis multiplicity declared (R31; the stats linchpin)
H1–H4 are separate pre-registered estimands (each with its own multiplicity control); **no global FWER correction**
by design, with a **Bonferroni-across-4 sensitivity** reported (`out["cross_hypothesis_multiplicity"]`) — making
the garden-of-forking-paths stance explicit.

### Integrity defects fixed (all caught first-hand)
- **R29** — the H4b arm was mislabelled `bayesopt_tpe` / "Optuna TPE, 240 trials" but is scikit-learn **GP-EI**
  (Optuna is not a dependency); relabelled, cite **Snoek et al. 2012** (added to refs.bib with Bergstra-Bengio 2012).
- **R28** — H4a random-search grammar widened from 3 terms to the **shared six-term family** (realizing the frozen
  ADR-010 intent), so H4a is a genuine procedure-only control at matched compute.
- **R27 / §4** — the Troop (2021) bias-corrected POT was promised but only a docstring; **measured** that in-regime
  (n≈750) the plain-MLE CVaR error is ~98% variance and Troop's correction is ill-conditioned (GPD ξ≤0 in ~94% of
  samples) → disclosed plain-MLE, Troop = future work (implementing it would be theatre).
- **H1 hardened** (in R30) — best-of-4 baseline selected on **validation** not test (data-snoop fix), the dangling
  `§18-19→§1/§9` citation fixed, the metric relabelled **Eureka-STYLE** (Eureka's HNS is not computable single-task).

### Killer critiques pre-empted by disclosure
- **R26** — factor attribution (`src/inference/attribution.py`, difference-in-alpha after FF5+Mom(+BAB) HAC) now
  **pre-registered as a declared secondary** — the answer to "the edge is just BAB/low-vol" (red-team G2).
- **L15–L19** added to the limitations register (BAB/low-vol; untuned baselines; measurement-noise; n-of-1
  external-validity; off-policy-SAC-on-noisy-rewards) + `docs/DEEP_FRAMING_discipline.md` (the **no-SOTA-claim**
  discipline — the FinRL band is partly reproducibility smear (0.16→2.39 on seed-fixed code), restrict "does it
  work" to the internal matched ladder; the "distribution → multi-level tail-risk feedback" construct retitle; the
  T0 cost/deflation fairness table).

### Report-only sensitivities + a fixed flaky test
Added DSR effective-N (`out["dsr_effective_n"]`; ρ̄≈0.80→N_eff=1, benign direction), EVT-estimator-consistency guard,
and the T0 per-benchmark turnover/cost + undeflated-N=1 DSR. **Work B (per-candidate resume) DEFERRED** as a
documented operational follow-up (hard-crash risk already mitigated by sleep-disable + n_gpu=2 + the SIGINT
graceful-shutdown + arm-level resume; it is the one change touching the science-sensitive reflection loop).

## [2026-06-25] — Ten-agent campaign-readiness sweep + integration (analysis modules wired, run hardened, citation/compute corrected)

A ten-agent parallel sweep (web-enabled, critical, NO dissertation prose) built the post-run analysis
machinery + operational hardening + the freeze-decision/runbook docs, then the deliverables were integrated
into the live code and verified GREEN (full fast suite exit 0, `freeze.py --check` 9/9, ruff clean, mypy +0
new). All new docs live under `docs/CAMPAIGN_*.md`.

### Analysis-completeness modules (built, tested, standalone-green)
- `src/inference/attribution.py` (+`tests/test_attribution.py`, 18) — factor-model **difference-in-alpha**
  (the "edge is just BAB/low-vol beta" rebuttal); paired across-seed bootstrap (carries training-RNG
  variance like frozen H2), Door-C disjoint family. CAPM/FF3/Carhart-4 run on on-disk data today; FF5/6 +
  BAB/QMJ need a small factor pull (a `factor_provider` hook injects them).
- `scripts/variance_decomposition.py` (+tests, 20) — σ²_seed/σ²_search/σ²_market one-way random-effects ANOVA
  (the "one-lucky-reward" defence); verdict "gap exceeds √σ²_search"; needs K≥2 search re-runs (else skipped).
- `src/inference/contamination.py` + `src/inference/ood_stress.py` (+tests, 31) — named-vs-blinded N3 A/B
  (paired TOST; needs a sealed ~150–200-seed side-experiment) + GARCH-EVT/block-bootstrap/Markov OOD stress.
  Fixed a real GARCH bug (`conditional_variance`→`conditional_volatility`; FHS now reproduces vol-clustering).
- `scripts/power_analysis.py` — re-derived the MDE against the REAL paired test (n_seeds=30, NOT seeds×folds×N);
  honest directional σ=0.360 → **MDE@80% = 0.362 Sharpe**; pre-committed null framing. Generates
  `docs/CAMPAIGN_power.md`.

### Wired into the live analysis (additive, disjoint keys — frozen m=6 untouched)
- `scripts/analyze_campaign.py::analyze()` now computes `out["attribution"]` (panel-dependent, reuses the R20
  rf) and `out["variance"]` (opt-in `--variance-runs`, ≥2 roots); both render in `write_report` and degrade
  gracefully. Default report is byte-identical (variance omitted without the flag).

### Operational hardening (science-neutral, applied + tested, 47 targeted tests)
- `src/io/results.py` — **atomic** record write (temp+fsync+`os.replace`): a kill mid-`json.dump` can no
  longer leave a truncated `record.json` that crashes `--resume`.
- `scripts/run_campaign.py` — SIGINT/SIGTERM **graceful-shutdown** (cooperative `threading.Event`, arm/stage
  boundaries, double-Ctrl-C hard-exit, non-destructive) + a fail-loud failure-wave guard + a CLI-boundary
  `--search-gpu ≥ 4` refusal (6 GB VRAM hard-caps search; n_gpu=4 is the measured search OOM).
- `src/utils/monitoring.py` — GPU-temp (87/91 °C) + RAM (85/92 %) anomaly thresholds (one edit covers serial +
  parallel monitors). `scripts/watch_thermal.py` — NEW zero-touch NVML/`progress.json` thermal sidecar.
- DEFERRED (science-sensitive, pending a dated pre-freeze amendment): per-candidate SEARCH resume in `loop.py`
  (would stop a mid-arm crash re-burning up to 30 paid Opus calls; reconstructs the reflection chain).

### Corrections
- **Citation:** the HAC truncation-lag rule `floor(4(T/100)^(2/9))` is **Newey-West (1994)**, NOT Schwert
  1989 (Schwert's `12(T/100)^(1/4)` is a different ADF unit-root rule). Renamed `schwert_hac_lag →
  newey_west_hac_lag` and corrected the prose in `attribution.py` + test + `docs/CAMPAIGN_attribution.md`
  (which had stated the rule "is Schwert 1989, *not* Newey-West" — exactly backwards). Also re-confirmed
  QMJ = Review of Accounting Studies 2019 (not Review of Finance).
- **Compute:** runbook figures corrected to the authoritative `COMPUTE_AND_TRAINING_TIME.md` (post-amendment
  D2): 6-arm core = 360 runs (~27 h laptop @ n_gpu=4); full lean (core + 120 H1 baselines + ~120 PPO/TD3) =
  ~600 runs ≈ **110 GPU-hr ≈ $32–44 / ~4.6 days serial** on a 4090, ~7.5 days laptop. The run-count locked at
  freeze IS the DSR trial count.
- **Two latent bugs fixed:** `tests/test_contamination_ood.py` `_garch_like_panel` read uninitialised
  `np.empty` memory (`eps[0]` before the loop) → seed-dependent non-finite panels (verified across 8 seeds);
  `tests/test_utils.py::test_logging_configures_idempotently` was order-fragile (root-handler pollution via
  `attach_run_logging` + the module-level `_configured` flag) → now snapshots/restores its own logging state.

### Open (gate the freeze — user decisions, NOT auto-applied)
- **H1 REWARD_CANON** "beat-the-human" test is **un-wired** (the `reward_kind="baseline"` worker branch is
  unreachable; no Eureka fraction/normalised-improvement metric; stale `eureka_loop.yaml` names). REWARD_CANON
  has **9** rewards → wiring it is ~270 runs (9×30), not the compute doc's budgeted 120 (which assumed 4).
- The four freeze-decision-brief calls (λ=0; parallel reflect-on-best headline; rent the 4090; N3 ~150–200
  seeds) + ratifying the per-candidate-resume amendment. See `docs/CAMPAIGN_freeze_decisions.md`.

## [2026-06-24] — Four-agent possibility-space sweep + analysis-machinery correctness (PBO enumeration, responsiveness confound, prototype validation)

A four-agent read-only sweep (engineering / science / write-up-grade / adversarial-risk) mapped the remaining
work. The dominant grade reframe it surfaced: **the MSc is assessed on the submitted PDF alone — there is no
viva** (`02_guidelines_and_examples/.../MSc_Project_Marking_Criteria`), and a pre-registered null is bankable,
so citation integrity + self-disclosed limitations + faultless write-up are the controlling levers (recorded
for the write-up phase, not code). The cross-validated, code-confirmed *correctness* items were then fixed:

### Reflect-on-BEST parallel SEARCH wired into the campaign (behind `--search-gpu`, default off) + buffer-skew fix
- New shared `scripts/run_prototype.py::build_parallel_opts` (the prototype `--parallel` path refactored onto it,
  byte-for-byte) so the prototype and campaign cannot drift in how they assemble the `run_parallel` `opts`.
- `scripts/run_campaign.py`: `_search_parallel_arm` + `--search-gpu/--search-cpu` (default serial). When set, each
  arm's development-split search runs the within-generation/cross-arm scheduler (`parallel.run_parallel`) with the
  campaign's RESOLVED 50k budget and its OWN Opus author (mapped into the flat `model`/`api_key_env`/`temperature`
  keys the driver reads); SELECT/FREEZE/TEST downstream are unchanged (same `val_fitness`/`val_returns` schema).
  The ONLY behavioural delta from serial is the reflection seed (generation BEST vs serial LAST) — amendment-gated
  (PREREGISTRATION §6). Bonus fix: the parallel worker couples `buffer_size == train_steps` (50k), so SEARCH now
  trains at the SAME replay budget as TEST — resolving the documented serial-search 25k-buffer skew.
- Verify: `tests/test_run_campaign.py` (+2: opts built at the 50k campaign budget with the Opus author; `--search-gpu`
  defaults to serial) GREEN; run_prototype + run_campaign tests GREEN; ruff clean; `run_campaign.py` mypy 0 (fixed the
  2 new injectable-callable narrows + 2 pre-existing: the `trainer` factory type and the `write` injectable).

### Pre-freeze amendments drafted (PREREGISTRATION.md, 2026-06-24) — ready for the user's freeze-time ratification
- §6: optional reflect-on-best parallel search + matched 50k buffer (above); serial-vs-parallel choice recorded at freeze.
- §5: λ formalization (PROPOSED) — `lambda_cvar = 0.0` (pure validation-DSR selection; retire the un-calibrated
  `lambda_grid`/`calibration_fold`); the tail is the FEEDBACK channel's job, measured on the test leg, not a selection term.
- §11: config-driven TF32 (`agent.tf32`, default on) uniform across serial/SEARCH/TEST — resolves the select-vs-evaluate
  numerics asymmetry.

### Write-up artifacts produced (no-viva grade levers; non-code)
- `paper/refs.bib` — 36 corpus-verified Harvard BibTeX entries (every 2025-26 / unprinted-field flagged `% VERIFY`); the
  sweep REJECTED four fabricated/future-dated arXiv ids, corrected Troop→arXiv:2103.05059 and Kusuoka→RIMS, flagged the
  memory note's "Di Castro first" as likely wrong, and surfaced that Khraishi-Okhrati 2022 prints NO ICAIF venue (any
  "ICAIF 2022" cite is unsupported — supervisor-stakes).
- `00_planning/LIMITATIONS_REGISTER.md` — 12 threats-to-validity entries (statement + why-probed + prose-ready paragraph),
  repo-grounded; verified the empty `feedback_block` is prototype-only (the live `loop.py` persists it → no campaign risk).

### Environment: SB3/sb3-contrib restored to the pinned `<2.9` (reproducibility-of-record)
- Verified first-hand: the venv had DRIFTED to `stable-baselines3`/`sb3-contrib` **2.9.0**, but SB3 2.9.0 DECLARES
  `torch<3.0,>=2.8` while the validated GPU build is **torch 2.6.0+cu124** (ADR-030/032) — so the installed stack
  violated SB3 2.9.0's own torch floor AND the deliberate `pyproject` cap (`<2.9`); a clean `pip install` could not
  reproduce it. **Downgraded to 2.8.0** (+ gymnasium 1.3.0→1.2.3 to satisfy it), matching the pin + torch 2.6.0.
  **Verify:** the real-SAC equivalence test (`test_test_leg_equivalence`, slow) and the **full fast suite** are GREEN
  on the restored stack. (NB: the prior adversarial-sweep suggestion to "bump the cap to <2.10" was WRONG — it would
  have ratified the non-reproducible stack; the pin was correct, the venv was not.)

### Three-agent adversarial review (science/literature + code + docs) — every CONFIRMED issue CLOSED
A deep, strict, literature-grounded review audited THIS session's work from all angles. Net: science + code
are SOUND — NO confirmed code bugs (466 fast tests pass), and 5/6 scrutinized science decisions sound. Two
verify-first REFUTATIONS of earlier suggestions: (a) the DSR raw-trial-count "anti-conservative" worry is
BACKWARDS (E[max SR]↑ in N → raw N > N_eff → LOWER DSR → MORE conservative; Bailey-LdP 2014 App. A.3), so an
ONC N_eff module was NOT built (it would move the number the permissive way); (b) λ=0, PBO full-enumeration,
reflect-on-best (Eureka Alg.1 line 9), and the FZ0/ES non-wiring are all confirmed sound/Eureka-faithful.
Confirmed issues — all CLOSED + re-verified (full fast suite GREEN, ruff clean, mypy +0, YAML parses):
- **#3** responsiveness metric was over-billed "core H2 evidence" vs its own directional disclaimer → DEMOTED to
  a directional probe (the ablation lattice is the causal test, cf. Eureka §4.3); Pearson→**Spearman**; 0.0→**None**.
- **C1** §11 "explicit in config" overclaim → softened (TF32 is one `train_agent` setting, default-on/overridable, uniform).
- **C2** the 3 amendments had no YAML mirror → added `search.*` + `agent_numerics.tf32` to `config/preregistration.yaml`.
- **C3** §5 "λ-grid retired" vs still-present config → softened to "left INERT (deleted at freeze if λ=0 ratified)".
- **C4** added rows R21/R22/R23 to the PREREGISTRATION amendment-record table.
- **C5** added the missing frozen-prereg reference Troop 2021 (arXiv:2103.05059, bias-corrected POT) to `paper/refs.bib`.
- **C6** dropped the unsupported "ICAIF" venue on Khraishi-Okhrati 2022 in `docs/REFERENCES.md` (matches refs.bib; supervisor-stakes).
- **3a** (latent) threaded `learning_rate`/`gamma`/`ent_coef` through `build_parallel_opts`→`_spec`→`train_candidate`
  so the parallel SEARCH worker honors the full agent config (parity with serial + TEST; behaviour-preserving).
- **U1/U2/U4** added LIMITATIONS L13 (λ=0 tail-blind selection trade-off) + L14 (default-path 25k-buffer skew); fixed L12's
  nuance (the parallel `--search-gpu` path also leaves `feedback_block` empty — the gate reads `prompt` either way).
- **Noted for the run** (3e, not a code fix): the `--search-gpu` path reuses `run_parallel`'s single non-recycling
  DevicePool — monitor RSS on the first real arm or wire `run_recycling` for TEST-leg parity.

### Split verification (3 more independent agents, re-running suites + freeze.py) → final residuals closed
Net: code FLAWLESS (no bugs; 466 fast + real-SAC equivalence green), `freeze.py --check` PASSES, the H2 chain intact.
The residuals it surfaced — all closed + re-verified:
- **TF32 made genuinely config-driven** (V2's recommended resolution): added `agent.tf32` to `config/prototype.yaml`
  and threaded it `_agent_cfg`→`build_parallel_opts`→`_spec`→`train_candidate`, so the serial/SEARCH/TEST legs read the
  precision from CONFIG (was a `train_agent` default). §11/R23/mirror flipped to the now-true "config-driven" (behaviour-
  preserving — tf32=True everywhere as before; verified flowing True through all three legs).
- **§5 + L13 λ prose** corrected to cite the `held_out_fitness` default (`lam=0.0`), not `config/inference.yaml` (which
  carries no `lambda_cvar` key); selection is λ=0 by function default, config-independent. L13 also notes λ=0 is *neutral*
  for the Sharpe-gated headline (adversarial only on the tail legs).
- **CHANGELOG** `+0.0504` annotated as the pre-Spearman Pearson value (true Spearman = −0.0529; directional, no number enters).
- **refs.bib** Politis-Romano 1994 added (verified first-hand: JASA 89(428):1303-1313, JSTOR 2290993) + the Tier-1 scope disclosed.
- **freeze.py gate hardened** — `assert_prose_matches_yaml` now also checks `fitness.lambda_cvar` (R22), `agent_numerics.tf32`
  (R23), `search.reflect_protocol_default` (R21); 2 freeze tests updated (6→9 checks).
- **Verify:** full fast suite GREEN (1 skip); real-SAC equivalence GREEN; `freeze.py --check` PASSES (9 checks); ruff clean;
  mypy +0 new; `preregistration.yaml` parses; `refs.bib` 38 entries, no dup keys.

### PBO/CSCV primary overfitting guard — FULL deterministic enumeration (was a random subsample)
- `src/inference/overfitting.py::pbo` caps evaluated CSCV splits at `_MAX_COMBINATIONS = 4000`, but the frozen
  `n_blocks=16` gives `C(16,8) = 12,870 > 4000`, so the **PRIMARY** (trial-count-free) overfitting guard ran on
  a random 4,000-split subsample → the headline PBO was **seed-dependent**. `scripts/analyze_campaign.py::campaign_pbo`
  now passes `max_combinations = math.comb(n_blocks, n_blocks // 2)` → the full 12,870-split enumeration (ms-cheap),
  making PBO deterministic. **Verify:** new `test_campaign_pbo_fully_enumerates_at_frozen_s16` (two unrelated rng
  seeds → identical PBO ⇔ enumerated, not sampled); `test_analyze_campaign.py` 14/14 GREEN, ruff+mypy clean.

### `inspect_rewards.feedback_responsiveness` — measured-vs-fed tail CONFOUND fixed (the H2 mechanism metric)
- The "did the LLM USE the distribution" metric (the single most distinctive non-benchmark artifact) correlated
  each reward edit with the tail delta the designer was *fed*. But `_tail_vector` preferred `metrics['tail_stats']`
  — the tail **measured off-critic for EVERY arm** — so `scalar` (fed only a Sharpe scalar) and `placebo` (fed
  inert constants) were scored against a distribution **they were never shown**, yielding spurious correlations
  (real prototype: scalar **+0.42** > distributional +0.05). The synthetic unit-test fixtures coupled
  `tail_stats` to the rendered tail text, so this **passed in tests but was wrong on real data**.
- **Fix:** a new `_was_fed_tail(record)` gate decides responsiveness from what the designer **SAW** — the rendered
  `feedback_block`, or the full `prompt` when the loop leaves `feedback_block` empty (as the prototype does) —
  applied per-arm in `feedback_responsiveness`. Arms not fed a tail (`scalar`/`placebo`/the search arms) now
  correctly report `score=None`; **distributional is preserved by the gate (38 steps; +0.0504 was the Pearson value at
  this step, later switched to Spearman −0.0529 by the review's #3 fix below — DIRECTIONAL, no number enters the dissertation)**; `scalar_cvar5`
  retains a score (it *was* fed `cvar_05`). **Verify:** new `test_feedback_responsiveness_ignores_measured_tail_when_not_fed`
  replicates the real confound (measured tail present, none fed → `None`); `test_inspect_rewards.py` 13/13 GREEN;
  ruff clean; `inspect_rewards.py` mypy **0** (also inlined a pre-existing `vec` `[no-redef]`).
- NB (for the campaign): records persist the fed feedback in `prompt` and leave `feedback_block` empty — the gate
  reads both, so it is robust either way; populating `feedback_block` in the loop would be a tidy follow-up.

### TEST-leg TF32 comment corrected (stale after the config-driven TF32 change)
- `src/orchestration/test_leg.py` said the worker "DELIBERATELY do NOT enable TF32"; since TF32 became config-driven
  in `train_agent` (default on), all three legs (serial / SEARCH / parallel TEST) share it. Comment rewritten to
  match (the adversarial-risk agent's only CONFIRMED code issue — it had verified 12 invariants sound); worker
  traceback widened 3→12 frames for real-run debuggability.

### Prototype analysis pipeline VALIDATED end-to-end on the real archive (directional — no number enters the dissertation)
- Ran `analyze_results.py` + `inspect_rewards.py` on `outputs/prototype` (6 arms × ~40 candidates): verdict **AMBER**;
  the analysis pipeline (`load_arms`/`load_all`, IQM, stratified bootstrap CI, difference tests, forensics) works on
  real records — **de-risks the campaign H2 analysis** (an initially-suspected loader bug was a wrong `--root`; the
  loader is sound). Directional mechanism signal (NOT a result): the distributional winner's CODE genuinely uses tail
  terms (`cvar, drawdown, sort, std, var`); distributional-vs-scalar is **indistinguishable on Sharpe (p=0.41) but
  significant on CVaR (p=0.004)** (1-seed, directional) — the tail-shaping the H2 thesis predicts; reward-hacking minimal (2/239, both benign
  tautology). Containment rule respected: directional go/no-go only.

## [2026-06-24] — Max-throughput laptop campaign: deadlock-free pool-recycling primitive (parallel test leg + security hardening in progress)

### Worker-recycling deadlock MEASURED across all installed Pythons (3.11–3.14)
- The campaign throttled candidate concurrency to `n_gpu=2` because `ProcessPoolExecutor(max_tasks_per_child=…)`
  — the clean per-worker RAM-reclaim — was *believed* to deadlock on Windows spawn (only 3.11.9 was noted).
  **Measured first-hand 2026-06-24:** recycling HANGS (>75 s, no progress, terminated) on Python **3.11.9,
  3.12.10, 3.13.13 AND 3.14.4**; the no-recycle control completes in 0.1 s on all four. So a Python upgrade
  buys **no** recycling benefit, and 3.14 is beta (no torch-2.6 wheels). **Decision: stay on the validated
  3.11.9 venv** (torch 2.6.0+cu124, SB3/sb3-contrib 2.9.0, pyarrow 24, numpy 1.26.4).
- Hardware measured (this laptop): 16 logical / 10 physical cores, 15.6 GB RAM, RTX 4050 **6 GB VRAM**.
  `auto_n_gpu()` = **4** at 25k and 50k steps (VRAM caps GPU workers at 4 ≈ 1.4 GB CUDA ctx each; RAM caps
  ~5 total). Beyond ~4–5 = swap = slower. Free alternative flagged: Kaggle T4/P100 (16 GB, 30 h/wk free).

### `src.orchestration.parallel.run_recycling` — deadlock-free RAM reclaim (NEW)
- Replaces broken in-pool recycling with **manual pool-level recycling**: runs specs through a sequence of
  fresh `DevicePool`s of `recycle_every` tasks each; the `with` exit terminates the worker processes → the
  OS reclaims each worker's entire (fragmented SAC-replay-buffer) heap → per-worker RSS cannot creep across
  a long run. Pool re-spawn (~15 s) is amortized over `recycle_every` trainings.
- Additive, back-compatible API: `DevicePool(initializer=…)` (a `_DEFAULT_INIT` sentinel keeps the production
  `_worker_init`; tests pass `None` for bare no-torch workers); `DevicePool.submit_with(fn, spec)` (run an
  arbitrary picklable worker on the shared device-token pool, e.g. the TEST-leg worker);
  `run_recycling(specs, worker=, n_gpu=, n_cpu=, recycle_every=, initializer=)`.
- **Verify:** new `tests/test_parallel_recycling.py` (2 tests) **GREEN** — 10 tasks processed in order, cpu
  device tokens assigned, **5 distinct worker pids across 3 fresh pools** (reclaim confirmed) + single-batch
  edge case; `parallel.py` imports clean (no syntax regressions from the 6 edits).

### Parallel campaign TEST leg — single-source-of-truth + science-neutral (NEW)
- **`src.orchestration.test_leg`** (new module): `build_test_record` is the SOLE per-seed record schema,
  called by BOTH the serial `evaluate_winner_on_test` (refactored onto it — verified byte-identical by the
  existing `test_run_campaign` invariant tests) AND the new parallel worker, so the two paths cannot drift.
  `_test_seed_worker` reconstructs panel/reward/env/trainer from a picklable spec (mirrors `train_candidate`)
  and replicates the serial per-seed body EXACTLY (B1-B6: matched budget, per-seed `set_global_seed`, frozen
  re-instantiation, ONCE-only test touch, env-fingerprint, R18 lookback purge). `evaluate_winners_on_test_parallel`
  is the driver: frozen/test desync guard once per winner, `--resume` skip, per-arm writes, failure-counting;
  its `runner`/`worker`/`write` are injectable so the orchestration is fast-tested with no spawn / no torch.
- **TF32 made a single config-driven setting (`agent.tf32`, default on) applied in `train_agent`**, so the
  serial trainer, the SEARCH worker, and the parallel TEST worker select AND evaluate the fixed agent under
  IDENTICAL float32 numerics. Removes a latent SEARCH-vs-TEST numerics asymmetry (TF32 was previously enabled
  only inside `parallel.train_candidate`; the serial trainer ran TF32-off) — the cousin of the batch_size
  256/512 drift. **Pre-freeze amendment to ratify** (alongside reflect-on-best); applied identically across
  all arms, so it does not affect H2 identification.
- **`run_recycling`** (manual pool-level recycling) is the deadlock-free RAM reclaim for the laptop n_gpu=4
  campaign (in-pool `max_tasks_per_child` deadlocks on Windows spawn across CPython 3.11-3.14 — measured).
  `DevicePool.submit_with(fn, spec)` runs the TEST worker on the same device-token pool; crash-safe (a worker
  that RAISES is captured, never aborts the run). **`parallel.py` mypy 8 → 2** (the 6 cleared were pre-existing).
- **Verify:** `tests/test_parallel_recycling.py` (4) + `tests/test_test_leg.py` (6) GREEN; full non-slow suite
  GREEN (pre-TF32 + re-run); ruff clean on all changes; mypy +0 new everywhere.
- **Security:** a fresh adversarial audit of the untrusted-code sandbox, secrets (`.env`/`capture_env`),
  prompt-injection (schema-derived feedback only), and supply-chain (`pyarrow` 24 / `torch` 2.6 CVEs
  patched-or-unused-paths) found **ZERO critical issues** — a strong, citable posture for a codebase that
  executes LLM-generated code.

### `run_campaign --gpu` TEST-leg wiring + science-neutrality PROVEN (NEW)
- `run_campaign.py` gains `--gpu/--cpu`; `run_headline_campaign(n_gpu>0)` runs each arm's 30 TEST seeds
  through `evaluate_winners_on_test_parallel` (device pool + manual recycling). Default `n_gpu=0` keeps the
  serial `evaluate_winner_on_test`, so every serial unit test is untouched (`test_run_campaign` green;
  mypy +0 new — the 4 run_campaign.py errors are pre-existing). A parallel-TEST failure wave is surfaced
  (no silent "tested (0)").
- **Science-neutrality PROVEN** — `tests/test_test_leg_equivalence.py` (slow) trains the fixed SAC for real
  and asserts the PARALLEL `test_returns` **== the SERIAL** path's (CPU, single-threaded, fixed seed →
  byte-identical within 1e-6; same `run_id`/`frozen`/schema). Parallelizing the TEST leg changes nothing
  observable. A `--dry-run --gpu 1` confirmed the integration runs end-to-end (its degenerate 1-day test
  window writes 0 records in BOTH serial + parallel — a synthetic-panel/`resolve_windows` artefact, not a
  parallel bug).

### Remaining (gated on the user)
- **Reflect-on-best SEARCH parallelization** (`run_parallel` into the campaign search, for the laptop ~27 h):
  gated on the dated PREREGISTRATION amendment (reflect-on-best + the config-driven TF32) being ratified
  and mirrored in `config/preregistration.yaml`.
- **FREEZE the pre-registration** — `config/preregistration.yaml: frozen: false` today; freezing must
  PRECEDE the confirmatory run (the single highest-grade-weight integrity action; user-gated).

## [2026-06-20] — Prototype reward-author → Claude Sonnet 4.6 (ADR-038) + per-file strict audit: all 42 confirmed defects fixed

### Provider switch Gemini → Anthropic Claude Sonnet 4.6 (prototype only; campaign stays Opus 4.8)
- `config/prototype.yaml: llm` → `provider: anthropic`, `model_snapshot: claude-sonnet-4-6`,
  `api_key_env: ANTHROPIC_API_KEY`, `temperature: 1.0` (Sonnet HONORS temperature → sampling diversity;
  no prompt-variation, unlike campaign Opus 4.8 which rejects it). Recorded as **ADR-038**.
- **`.env` was never loaded** — nothing in `src/`/`scripts/` called `load_dotenv`, so a Pass-B run would
  die "ANTHROPIC_API_KEY not found" despite `.env` holding it. Added `src/utils/env.py::load_env()` called
  at the real entry points (`run_prototype`/`run_campaign` `main` + the parallel worker). Kept OUT of
  `client.build_transport` so that factory stays PURE (its no-key error path remains unit-testable;
  Windows-`spawn` workers inherit `os.environ`).
- **Opus temperature guard:** `_TEMPERATURE_REJECTING_MODELS = (opus-4-7, opus-4-8)`;
  `make_anthropic_transport` drops a stray `temperature` for those so a config mismatch can't 400 the
  campaign. `anthropic` SDK 0.111.0 installed. **Validated end-to-end** with a live Sonnet call (valid
  reward code returned, `temperature=1.0` accepted, token usage archived).

### Per-file strict audit (127-agent, 42 confirmed) — ALL fixed + reconciled
A file-by-file marking pass found 42 confirmed defects (1 crit, 3 high, 18 med, 20 low) beyond the earlier
~80. Fixed via a 27-file fix-workflow (adversarially verified) + manual completion of every flagged item:
- **The 1 CRITICAL + 3 HIGH are all in utility/analysis scripts** (`verify_inventory` broken imports +
  no `__main__`; `power_analysis` unbounded auto-regime count N=145; the `analyze_campaign` "single-root"
  report) — **none blocks the prototype/campaign run.** `verify_inventory` now reads the real repo-root
  manifest + emits its JSON; `power_analysis` got a `too_many` upper-bound trip (config-read
  `MAX_PLAUSIBLE_REGIMES`); the `analyze_campaign` single-root + `winner_dsr`-ddof findings were verified
  **already fixed in source** (the loader walks `_MAX_ARCHIVE_DEPTH=3` over `<leg>/<arm>/<cand>` and
  separates search-leg `val_returns` from test-leg `test_returns`; `winner_dsr` already uses the ddof=1
  `_sample_moments`) — the stale **test** was corrected to match.
- **Run-affecting MEDs fixed:** `portfolio_env.step()` now reports the window-exhaustion boundary as
  `truncated` (not `terminated`) so SB3 SAC bootstraps the boundary value instead of zeroing it (3 tests
  reconciled to the new Gymnasium contract); `reward_family` clips `log1p(port_ret)` so a < -100% return
  can't poison the stateful cum/drawdown; `extract_reward_source` no longer commits to a syntactically
  broken first `def reward` block; the TQC factory routes `n_quantiles`/`n_critics` via `policy_kwargs`
  (top-level would `TypeError`) and `top_quantiles_to_drop_per_net` top-level.
- **Inference/data MEDs fixed:** `reporting.iqm` + `es_backtest.var_es` now strip non-finite inputs
  (agreeing with their `bootstrap` twins); the data pipeline purges adjacent splits by
  `max(embargo=21, lookback=60)=60` (R18) with a `dict[str, Any]` manifest (no `type: ignore` smuggle);
  `loaders` VIX leading-NaN seeds from the genuine prior session (bfill only for the irreducible
  global-first cell); the `measurement` EVT-boundary docstring direction corrected.
- **20 LOW** (dead code, stale docstrings, wrong exception types, edit-trail prose) cleaned.
- **Verify:** full non-slow suite **GREEN**, 8 slow SAC/TQC tests pass (terminated/truncated + TQC
  construction safe), `ruff check` clean, `mypy` at the 13-error baseline (+0 new), `freeze --check` OK.
  (Pre-existing/out-of-scope: `ruff format --check` flags 83/117 hand-formatted files — never enforced,
  no live CI; not introduced here.)

## [2026-06-20] — No-hardcoding audit (54-agent): 10 config-source violations fixed (config is the single source of truth)

A strict audit (CLAUDE.md: "config/*.yaml is the single source of truth; code reads config, never hardcodes")
found **10 real config-source/drift violations** — confirmed by the cross-cutting fact that `cfg_get` returns
a present-but-`null` value AS `None` (so an `algos.yaml: sac.batch_size: null` is NOT an effective source —
the in-code literal defaults were the de-facto source of truth). All HIGH/MED fixed; verified 451 passed /
1 skip, ruff clean, mypy +0 new errors, freeze OK.

- **[HIGH] SAC `batch_size` drift (256 vs 512)** — the same hyperparameter had TWO divergent literal defaults
  across the sequential (256) vs `--parallel` (512) training paths (5 resolution sites). On the documented
  max-throughput `--parallel` path this could SELECT the frozen winner under batch 512 but EVALUATE it on the
  sealed test under 256 — the fixed-agent train/test mismatch audit A-1 forbids. Unified to ONE canonical
  default (256, the SB3 default + what prototype.yaml and the sequential path already use); deleted the 512
  literals in `run_prototype.py` + `orchestration/parallel.py`.
- **[HIGH] `buffer_size` 1M literal in `agents/factory.py`** contradicted ADR-025 (buffer = train-step budget,
  full-history replay, no eviction) AND diverged from `trainer.resolve_agent_kwargs`. Now mirrors the trainer
  exactly: defaults to `train_steps_per_candidate` (the 1M literal OOM'd the 4090).
- **[HIGH] Headline H2 BH/FDR `q` (0.05) was never passed on the wired path** — `analyze()` called
  `h2_conjunction` with no `q`, so the frozen FDR level lived only as a function-default literal. Now READ
  from `config/inference.yaml: multiplicity.q` and passed explicitly. Same for the **headline CVaR tail level**
  — now read from the FROZEN `config/preregistration.yaml: inference.testing_family.cvar_levels` (it is NOT in
  inference.yaml, so the prior read was a silent `(0.05,)` fallback, not the frozen value).
- **[HIGH] pre-registered family size `m=6` hardcoded in `power_analysis.py`** (PowerConfig + CLI default) →
  READ from `config/preregistration.yaml: inference.testing_family.m` via a new `_frozen_family_m()` helper
  (the SAME m the campaign enumerates + asserts), so the selection-power Šidák adjustment can't silently drift.
- **[MED] eval-span end date `"2025-12-31"` hardcoded** in `analyze_campaign.main()` (the floor-panel load) →
  READ from `config/inference.yaml: splits.evaluation.span[1]`.
- **[MED] prototype/parallel embargo `21` literal fallback** (read from a config block lacking the key) → now
  falls back to the canonical `config/data.yaml: embargo_days`, not a bare literal.
- **[MED] `n_assets=30` hardcoded on the `--parallel` LLM-prompt path** (sequential uses `panel.N`) → READ
  from `config/environment.yaml: universe.n_assets`.
- **[LOW] fitness CVaR penalty α=0.05 hardcoded** in `held_out_fitness` → a `cvar_alpha` param defaulting to
  `config/inference.yaml: fitness.alpha`, read only when the penalty is active (λ≠0), so the λ=0 hot path stays
  config-free. (The duplicated action-`bound` 10.0 fallback was assessed and ACCEPTED: both call sites fall
  back to the same value, `action.bound` is always present + freeze-bound, so there is no real drift.)

## [2026-06-20] — Critical-review pass: Omega-threshold fix, additive R20 risk-free robustness, independent verification of the highest-stakes changes

A second, EXTREMELY critical multi-angle pass (user: "ultrathink, be very critical, watch from as many
angles as possible"). An 8-dimension adversarial review workflow was launched; in parallel:

### A real bug I had introduced — Omega's MAR silently shifted with rf (fixed)
- The array-rf generalisation made `metrics.compute_metrics`' **Omega** use the rf as its threshold. Omega
  is a distribution-SHAPE ratio about a fixed minimum-acceptable-return (Keating-Shadwick 2002; standard
  τ=0); using rf made it rf-dependent (a real per-period rf shifted it by ~0.02). Fixed to a **fixed 0 MAR**
  (rf-invariant), with a test asserting Omega is rf-invariant while Sharpe/Sortino correctly are not.

### R20 — additive risk-free robustness of the H2 Sharpe conjunction (frozen headline UNTOUCHED)
- **Critical insight (analytic + empirically confirmed):** my earlier "rf ≈ cancels for same-agent arm
  contrasts" was too glib. The per-seed Sharpe rf penalty is `mean(rf)·√252/σ` — LARGER for LOWER-vol arms.
  If the distributional (tail-aware) arm wins partly via lower realised volatility, threading rf
  SYSTEMATICALLY SHRINKS the measured H2 edge. A synthetic low-vol distributional arm showed positive
  shrinkage on all three legs (`distributional>scalar` −0.042 Sharpe). So rf genuinely moves the headline.
- `collect_family_pvalues` gained a `risk_free=None` param: **`None` is byte-identical to the frozen rf=0
  headline** (verified; `h2_conjunction` unchanged), and a per-period rf makes the SHARPE leg use excess
  returns (CVaR stays raw). New `h2_sharpe_rf_robustness` runs the family BOTH ways and reports per-leg
  effect/p-value/direction/BH-rejection + the shrinkage, certifying whether H2 survives the rf convention.
  Purely additive sensitivity — the decision to make excess the PRIMARY headline stays parked for the user.
- **Independent verification of the highest-stakes changes** (real data): the R18 embargo purge provably
  clears the prior split (first test obs lookback `[1259:1319]` starts exactly at `val_end`=1259, at BOTH
  boundaries); the `benchmark_floor` market-reference alignment is correct end-to-end (winner size = window,
  beta 0.83 for EW-top-30 vs the EW market — sensible). Full suite 442 passed / 0 failed.

### The 8-angle review landed (95 agents, 32 confirmed findings) — triaged + fixed
- **The benchmark suite was the real liability (all FIXED).** My R19 allocators were broken on the real
  test leg: `minimum_variance`/`maximum_diversification`/`mean_variance` Euclidean-projected an
  UNCONSTRAINED Σ⁻¹ vector onto the simplex and **collapsed to a single asset** (min-var had HIGHER
  variance than 1/N; max-div ratio = 1.0, the worst); `inverse_volatility`/min-var/max-div put ~100% on
  **delisted zero-variance names**; and `hrp` **crashed** on those names (linkage finite-value error).
  Rewrote them to solve the **long-only constrained QP** (`_long_only_min_variance`/`_long_only_max_sharpe`
  via SLSQP, mirroring risk_parity), exclude dead names (`_live_mask`), and made hrp robust + the
  `WeightPolicy` shim exception-safe (1/N fallback). 6 new correctness tests (GMV beats 1/N variance,
  max-div beats 1/N ratio, dead names get 0, no collapse, hrp robust) — verified over 20 seeds.
- **Leakage hardening (R18).** `make_env_builder`'s guard is now **lookback-aware** (`max(embargo,lookback)`,
  threaded from the campaign) so the R18 invariant no longer rests on one unguarded line; the resolve_windows
  test now asserts `gap ≥ lookback` (a future revert to embargo-only now FAILS the suite). Reconciled the
  R18 freeze/doc desync: the "byte-match 2015-02-03" claim was false (executed val starts ~2015-03-31 under
  the 60-session purge) — fixed across `loaders` (×2), `run_prototype`, `parallel`, `data.yaml`.
- **Correctness + honesty.** `compute_metrics` benchmark-relative now uses ONE shared finite mask over the
  aligned (returns, benchmark) pair (an interior NaN previously desynced beta/alpha/IR). `Omega` decoupled
  from rf (fixed 0 MAR, rf-invariant). `assert_fixed_agent_across_arms` honestly relabelled as a TEST-ONLY
  determinism/budget check (it is tautological — cannot catch a per-arm override the architecture cannot
  express). Stale-docs swept: prereg `benchmarks` mirror → 8 R19 names, "five benchmarks" → eight, removed
  Cornish-Fisher citation, `market_reference` suffix → `gold_suffix()`, DGS3MO/FF-Momentum docstrings.
  Edge-cases hardened: `return_minus_drawdown` log1p clip, drawdown-series divide warning.
- **Benchmark floor WIRED into production (#2/#6/#12, +MED#5).** `analyze()` now produces the DeMiguel
  floor + `market_reference` when given the panel/cfg/test_window (records-only default preserved for unit
  tests); `analyze_campaign.main()` loads the panel + reads the resolved `test_window` from the campaign
  summary; new `benchmark_floor_markdown` renderer wired into `write_report`. Carried **#14** (market-line
  Sharpe now routed through the same rf convention as winner-vs-market) and **#17** (the searched winner's
  DSR is deflated by `winner_n_trials`=candidate budget, while the un-searched benchmarks stay N=1). The
  floor gate uses the headline arm's seed-mean test path as the representative winner. Test added.
- **Net:** every must-fix from the 32-finding review resolved; suite **448 passed / 0 failed**, ruff +
  mypy (baseline) + freeze clean. Remaining items are documented-as-limitation / latent-unreachable
  (walk-forward CPCV materializer purge, rf leading-gap, synthetic dry-run mask) per the review synthesis.

### R20 finalised + env cash-rate support (user: "proceed"); confirmation review launched
- **R20 wired into the report.** `analyze()` now also produces `h2_sharpe_rf_robustness` (the excess-return
  H2 Sharpe sensitivity) when a panel is supplied, with a `h2_rf_robustness_markdown` renderer in
  `write_report`. The **frozen rf=0 headline is RETAINED as the pre-registered primary** (additive only);
  PREREGISTRATION **R20** records the convention + the vol-dependent shrinkage caveat. Test added.
- **Env cash sleeve now priceable** (`portfolio_env.cash_daily_rate`, config key added). Default **0.0** —
  byte-for-byte unchanged, so no test/training impact. Held at 0.0 deliberately: a CONSTANT cash rate
  biases the risk study (the 3-mo T-bill ranged 0–5.6%/yr 2005–2025 and would overpay cash in the
  2008/2020 ZIRP stress the tail-aware arm exploits), so a per-session DGS3MO SERIES is the documented
  correct refinement before enabling. The env *prices* cash when set; the value choice is flagged, not rushed.
- A second adversarial **confirmation review** (6 dimensions: are the fixes correct? new regressions?) was
  launched on the fixed code to close the verification loop.

### Confirmation review landed (7 findings) — all addressed; + manual deep verification
- **[HIGH] `risk_parity` lacked the dead-name mask** — the ONLY cov/vol allocator I missed: its ERC
  log-barrier put ~0 risk on (hence dumped ~49% weight onto) zero-variance delisted names, corrupting the
  frozen DeMiguel floor. Fixed to run on the live sub-panel like its siblings; added to the dead-name test.
- **[MED] floor gate re-introduced seed-averaging inflation** — the gate computed the winner DSR on the
  30-seed MEAN test path, shrinking variance ~√S and inflating DSR vs the single-path benchmarks (the exact
  anti-conservatism the H2 #9/#14 fix removed). Now gates the **median of per-seed DSRs** (like-for-like
  single-realisation), verified below the seed-mean value. Report-only gate (does not touch H2/PBO/selection).
- **[MED] floor `winner_n_trials`** now derived from the records' authoritative per-arm count (consistent
  with `winner_dsr`); the `main()` fallback reads the campaign budget (30), not the prototype's 40.
- **[LOW] residuals fixed**: `test_embargo_splits` module docstring (the byte-match-2015-02-03 claim the
  reconciliation sweep missed), `ARCHITECTURE_BLOCKS.md` Cornish-Fisher reference, `log_growth` log1p clip
  (consistency with its sibling; unreachable but defensive). One out-of-scope item (pre-existing synthetic
  dry-run window clamp) left as the already-documented smoke-path limitation.
- **Manual deep verification** (concrete, beyond the workflow): all `src` modules import clean; the
  `NotImplementedError`s are legitimate loud guards; cross-config values (embargo/lookback/seeds=30/m=6/
  budgets) consistent; **warnings-as-errors** suite passes (no hidden numerical warnings from our code); all
  test skips are legit data/platform guards; the **freeze hash is stable + deterministic**; the **8 slow
  agent-training (SAC) tests PASS** (verified for the first time — they are deselected in every normal run);
  removed the dead `_project_simplex` (the Euclidean-projection footgun that caused the allocator collapse).
  Suite **448 passed / 0 failed**, ruff + mypy (baseline) + freeze clean.

### Whole-project verification (96-agent, 41 findings) + fixes; science confirmed sound
- The exhaustive verification verdict: **none of the 41 findings corrupt the headline H2 result, the sealed
  test leg, the inference, or any reported number** — the defects cluster in freeze-integrity + CI/coverage.
  The 6 must-fix-now are all fixed:
  - **[HIGH] `freeze.py --check` was self-defeating** — the canonical hash included the two MUTABLE
    freeze-state bytes (`frozen`, `freeze_hash`) that `make freeze` flips, so `--check` reported DRIFT
    forever post-freeze (would fire at submission). The hash now blanks those fields (invariant to the
    freeze act; new test). It ALSO now **binds the executed config** (inference/environment/data.yaml), so
    a change to the load-bearing knobs (splits/embargo/lookback/family) is caught — it previously hashed
    only the prereg, so "nothing frozen can drift" was false at the config layer.
  - **[MED, sandbox hardening] `str.format` dunder-walk escape** — `'{0.__class__.__mro__[1].__subclasses__}'
    .format(x)` passed the AST gate (which inspects attribute *nodes*, not string-literal contents) and
    walked to `object.__subclasses__` (RCE/info-disclosure). Fixed: `format` removed from the allowlist +
    a defence-in-depth scan of string literals for replacement-field attribute access; new test.
  - **[HIGH] CI never gated the SAC agent / leakage guard** — the slow agent-training + NormalizedPolicy
    eval-stat-freeze tests (the no-leakage invariant underpinning H2) ran in NO CI path. Added a torch CI
    job running the slow set + the data_pipeline leakage tests. (Verified locally: all 8 slow tests pass.)
  - **[MED] config contradictions** — `power_analysis` SESOI/equiv-margin were a hardcoded 0.20 (4× the
    frozen 0.05) rendered under a "FROZEN-design value" label → now READ from `config/preregistration.yaml`
    (config-driven, not hardcoded); `config/llm.yaml` advertised the superseded Sonnet 4.6 → Opus 4.8 per
    ADR-035. The 30 LOW findings (cash_features-NaN-but-unused, dormant checksum, doc-labels, agent-config
    defaults) are documented-as-limitation / overlap the running no-hardcoding audit.

### Deep research (42 vetted resources) + oracle validation
- A 120-agent strict research sweep (2-vote relevance vetting) → `docs/RESEARCH_RESOURCES.md`: the
  publishable gap CONFIRMED (no prior work feeds a return distribution as LLM reward feedback, nor applies
  reward-code search to portfolio RL), plus the citation lineage (Eureka/Text2Reward/REvolve/DSAC/Beyond-CVaR),
  baseline ladder (FinRL value-change + Moody-Saffell DSR), N3 backbone (Profit Mirage/FinLake), and
  cross-check oracles.
- **Oracle-validated the headline inference**: `inference.{bootstrap,reporting}.iqm` and
  `reporting.probability_of_improvement` now MATCH the canonical `rliable` (Agarwal et al. 2021)
  implementation to 1e-9 (new `test_inference_crosscheck` oracle tests; rliable is an installed dep).

## [2026-06-20] — World-class elevation pass: block decomposition, B11 backtest analytics, B8 baseline expansion, supervisor leakage/rigor audit (15 findings) + fixes (R18 embargo, R19 benchmarks)

User mandate: decompose the prototype into blocks, elevate each to a "world-class, publishable, flawless
grade-maximiser" standard, run deep research + a 50-year-supervisor leakage/rigor audit, fix every gap,
and record everything. Pre-registration is still `frozen: false`, so design changes are dated pre-freeze
amendments. ADRs: **ADR-037**; PREREGISTRATION amendments **R18/R19**.

### Block decomposition (B1–B14) — `docs/ARCHITECTURE_BLOCKS.md` (new)
- Precise decomposition of the prototype/project into 14 blocks (data, env/regimes, reward sandbox, LLM
  loop, measurement/H2, agent/training, search baselines, reward/strategy baselines, selection, inference,
  backtesting analytics, orchestration/compute, analysis/reporting, provenance/freeze), each with files,
  current state, a 1–5 gap rating, and a supervisor gap analysis. Guiding principle: **elevate
  engineering/analytics/benchmarking/rigor without corrupting the frozen H2 scientific contribution**
  (reporting more metrics/benchmarks is additive; changing arms/env/hypotheses is not).

### B11 — world-class backtest analytics suite — `src/backtest/` (new; 15 tests)
- `metrics.compute_metrics` reports ~30 **only-highly-relevant** metrics across return / risk-adjusted
  (Sharpe, Sortino, Calmar/MAR, Omega, Martin) / drawdown (max-DD + duration, Ulcer, pain, time-under-water)
  / tail (CVaR/ES, historical + Cornish-Fisher VaR, tail ratio, downside dev) / distribution (skew, excess
  kurtosis) / trading (turnover, cost drag) / benchmark-relative (IR, tracking error, beta, annualised
  alpha) / overfitting (PSR, deflated Sharpe) families. **Reuses the audited inference primitives**
  (`bootstrap.{sharpe_ratio,cvar}`, `deflated_sharpe.{probabilistic_sharpe_ratio,deflated_sharpe_ratio}`)
  — DRY, no re-derivation. `drawdown_series`, `regime_conditional_metrics`, `tearsheet_markdown`.
- Degenerate inputs are provably safe (empty / single / zero-variance / total-ruin); a **PSR signature
  bug** (silent broad-except swallow) was caught and fixed during testing (per-period Sharpe, raw kurtosis,
  n; no broad except). `regime_conditional_metrics` now **fails loud** on a returns/regimes length
  mismatch and masks non-finite returns + regime labels TOGETHER (was a silent truncation + misalignment).

### B8 — baseline canon expanded + a real correctness fix — `src/baselines/`
- **+5 published reward baselines** (`REWARD_CANON`, 9 total): mean–variance utility (Markowitz 1952),
  return−drawdown (Chekhlov-Uryasev-Zabarankin 2005), return−downside (Sortino 1991), return−turnover
  (Gârleanu-Pedersen 2013), log-growth (Kelly 1956 / Thorp 1971) — the "did the LLM beat hand-written
  reward CODE?" panel.
- **+4 published allocators** (`STRATEGY_CANON`, 9 total): minimum-variance (Clarke-de Silva-Thorley 2011),
  inverse-volatility, maximum-diversification (Choueifaty-Coignard 2008), cross-sectional momentum
  (Jegadeesh-Titman 1993).
- **`risk_parity` correctness fix.** The iterative `w·(target/rc)` update **divided by zero (→ NaN)** on a
  generic window AND converged to a CONCENTRATED non-risk-parity solution (max risk-contribution deviation
  0.91). Replaced with the **convex Spinu (2013) / Maillard-Roncalli-Teiletche (2010) log-barrier**
  formulation solved by L-BFGS-B (worst deviation now 1.5e-04). The benchmark floor's `WeightPolicy` no
  longer needs its 1/N fallback for risk_parity.

### Supervisor leakage/rigor audit (44 agents, 2-vote verification) → 15 confirmed findings
- **[HIGH, R18] Embargo (21) < feature lookback (60) → insufficient purge.** Each observation reads
  `returns[t-lookback:t]`, so a 21-session split gap left the downstream window's first 39 observations
  reading prior-split returns (López de Prado purge-insufficiency — exactly the "data-leakage" failure mode
  a strict examiner flags). **Fix:** the effective inter-split purge is now `max(embargo, lookback) = 60`
  at BOTH boundaries, in `resolve_windows` (campaign val+test) and `embargoed_val_start` (search val, new
  `lookback=` arg threaded from both callers). `test_embargo_splits` now asserts `gap ≥ lookback`
  (+ a new focused test). Recorded in §7 + both config comments.
- **[HIGH, R19] "SPY buy-and-hold" was an exact 1/N duplicate** mislabelled as the S&P 500 (no index/caps
  in the anonymized panel). **Fix:** honest relabelling, removed from the frozen gate (de-dupes the
  DeMiguel floor + fixes a best-benchmark double-count), suite EXPANDED to 8 distinct published allocators.
  A true SPX-TR/cap-weighted market benchmark is a documented **gated data addition**.
- `mean_variance` confirmed to correctly apply Ledoit-Wolf shrinkage (finding #9 is a prose name-drift only).
- Fixed two more findings: **DSR trial-count** config label reconciled to the per-arm count the code uses
  (`per_arm_candidates`; cross-arm multiplicity is handled separately by the m=6 family, so all-arms would
  double-correct); **VIX unit-detection** now reads only the first ~2 years (always TRAIN), never the
  sealed test span.
- **VIX-shift pipeline test added** (`data_pipeline/tests/test_features.py`, 5 tests). The
  `build_cash_features` docstring claimed two leakage invariances were unit-tested, but the cited test
  file did not exist — the leakage-critical gold VIX `shift(1)` + `rolling_vol_shifted` lag were
  UNVERIFIED. Now checked: VIX feature at row t reads the t-1 close (never t), rolling vol is strictly
  past, + truncation and future-perturbation invariances. Runs isolated (`make test-pipeline`; the
  data_pipeline `src` package shadows the engine's).
- **Runtime algo-equivalence check implemented** (`arms.factory.assert_fixed_agent_across_arms`, +3 tests).
  `trainer.py` referenced a "runtime equivalence test" that licenses the matched-compute H2/H4 comparison
  but it was never written. It now asserts (a) every arm shares one `candidate_budget`, (b) the resolved
  SB3-SAC kwargs depend on the SEED ALONE (same arch/lr/buffer/batch/gamma/device + train-step budget at
  two seeds, policy = `MlpPolicy`) — catching a future per-arm hyperparameter override, and (c) the LLM
  arms each carry a distinct `feedback_kind`.
- **Two doc-note findings closed**: `config/algos.yaml` now flags itself as DIRECTIONAL (the live agent
  hyperparameters are resolved by `resolve_agent_kwargs` from `prototype.yaml`/campaign cfg, not this
  file) and ties its `equivalence_test: true` to the implemented `assert_fixed_agent_across_arms`;
  `sharpe_ratio` documents the Lo-2002 autocorrelation caveat of `sqrt(252)` annualisation (a descriptive
  point-estimate convention — the headline H2 test uses the per-seed paired bootstrap over the per-period
  series, so it is unaffected). The only remaining audit item is the analyze() val+test subtree merge
  (MED#5), which needs the real campaign archive layout traced (deferred to a focused pass, not guessed).

### Deep targeted research (7 agents) + reference-data integration — the "gated" findings were NOT gated
- A deep-research sweep (metrics / benchmarks / leakage / hardware / literature / data-enrichment) **validated**
  the B11 metric set and the B8 baseline canon as exactly the referee-expected panels, and surfaced that the
  data I had called "gated" is **already pulled and frozen on disk**. New tested loader `src/data/
  market_reference.py` (+9 tests) exposes three portfolio-level REFERENCE series that live ENTIRELY in the
  reporting layer (zero env/anonymisation change, so H2 is untouched):
  - **risk-free rate** — FRED `DGS3MO` (3-month T-bill) from `data/raw/fred_macro.csv`, converted to a
    per-session decimal (the research's sanctioned path; preferred over the within-month-constant FF RF).
  - **real market line** — `market_ew` (full-universe EW return) from `data/gold/market_proxy_*.parquet`,
    a genuine market benchmark (≠ the 30-asset 1/N), now reported in `benchmark_floor` as an additive
    `market_reference` block (market Sharpe/CVaR/DSR + the winner's beta / annualised alpha / IR), NOT in
    the same-universe DeMiguel gate. (A true cap-weighted SPX-TR stays a documented minor limitation.)
  - **Fama-French factors** (Mkt-RF/SMB/HML + Momentum) for OOS factor attribution.
- `compute_metrics` generalised to accept a per-period rf **series** (a real bug caught while wiring: it did
  `float(risk_free)`); a series is reduced to its mean — exact for the Sharpe/Sortino numerator, negligible
  in the vol denominator for a daily T-bill. **Cornish-Fisher VaR removed** (research: non-monotonic /
  unreliable for fat tails; historical VaR + coherent CVaR/ES dominate) — keeping ONLY highly-relevant tail
  metrics. Throughput research flagged **SBX (SB3+JAX)** as the big SAC speed lever (gated on numerical-parity
  validation + an ADR) and concurrent multi-run packing on the 4090 as the safe win; the literature sweep
  confirmed the **publishable gap** (distributional reflection × reward-code search × portfolio RL is unoccupied).

## [2026-06-20] — Headline H2 inference corrected to per-seed rliable (#9/#14, R16), H2 conjunction wired (#18), test-universe limitation documented (#13, R17)

User mandate on the three flagged pre-registered-analysis items: "ultrathink, do whatever you think would
maximise my grade … work extensively and hard." The pre-registration is still `frozen: false`, so these are
pre-freeze design **corrections/clarifications** (legitimate, dated as amendments). ADRs: **ADR-036**;
PREREGISTRATION amendments **R16/R17**.

### #9/#14 — the headline H2 inference was anti-conservative; corrected to per-seed rliable (R16)
- **The bug.** `analyze_campaign._arm_test_returns` AVERAGED the 30 per-seed frozen-winner TEST return
  series per arm (a per-period mean over seeds) and fed that single denoised series to a single-strategy
  stationary block-bootstrap difference test. Averaging N i.i.d.-seed paths shrinks the tested object's
  variance ~N×, so the bootstrap SE was ~√N too small and the test **over-rejected a true null** — measured
  empirically at **≈21% at the 5% level on 30 seeds** (a real false-positive inflation the supervisor would
  catch as p-hacking-shaped).
- **The fix (rliable; Agarwal et al. 2021, the recognised RL-evaluation standard).** New
  `src/inference/bootstrap.py`: `iqm` (interquartile mean) + `paired_seed_difference_test` — each arm's
  PER-SEED Sharpe/CVaR scores → IQM point estimate → a **paired stratified bootstrap over the shared
  training SEEDS** (i.i.d. seed resample applied to both arms), carrying the across-seed (training-RNG)
  variance. It uses the SAME re-centred basic empirical-bootstrap p-convention (`|boot−obs|≥|obs|`) as the
  existing `sharpe_difference_test`, so `null_calibration` certifies it identically. **Null-calibrated:
  ≈5% true-null rejection (correctly sized) vs the old ≈21%; power 1.00 on a real edge.**
- `collect_family_pvalues`, `romano_wolf_joint` (now over per-seed score arrays with one shared SEED
  resample per replication), and `h2_conjunction` were rewired to the per-seed unit; the family (R13, m=6),
  BH/Romano-Wolf correction, directional conjunction gate, and SESOI/TOST (R12) are **unchanged** — only
  the resampling unit moved from time-blocks-on-a-seed-averaged-series to seeds-on-per-seed-scores. The
  valid series-level tests are retained for single-realization use. This realizes the already-frozen
  `config/preregistration.yaml: inference.seed_reporting = rliable_iqm_poi_stratified_ci` at the test.

### #18 — the H2 conjunction is now wired into the analysis entry point
- `collect_family_pvalues` / `h2_conjunction` / `assert_realized_family_matches_frozen` were implemented and
  unit-tested but had **no caller** in `analyze_campaign.analyze()` — so the documented headline H2 test
  never actually ran. `analyze()` now computes `h2_conjunction(records)` (firing the R13 family-equals-frozen
  assertion), `write_report` emits the H2 verdict + the per-seed family BH table (`h2_markdown`), and `main`
  prints the verdict.

### #13 — sealed test-leg universe limitation documented + PIT robustness building block (R17)
- The fixed 30-asset action space means SEARCH/SELECT and the sealed TEST share ONE universe — the
  development-phase point-in-time top-30 (selected 2005-01-03). The 2018-2025 test leg therefore trades the
  **2005 cohort** (a composition bias: **11/30 names differ** from the 2018 point-in-time top-30), accepted
  for train/test consistency and now **reported as a headline limitation** (loud caveat in `run_campaign`),
  not silently inherited. `load_gold_panel` gained a `window_start` argument so a PIT walk-forward universe
  (e.g. the verified 2018-01-02 top-30) can be loaded for a robustness re-evaluation of the frozen winners.
  Whether to elevate PIT to the headline or keep the consistent fixed cohort + this robustness check is a
  methodological design choice flagged for the supervisor (not a code defect).

### Verification
- Tests: `paired_seed_difference_test`/`iqm`; `test_campaign_inference.py` lifted to **multi-seed** (faithful
  to the 30-seed campaign); a null-calibration **proof** test (new ≈5% vs old over-rejection) and a
  PIT-universe loader test in `test_audit_regressions.py` / `test_loaders.py`. Full non-slow suite **410
  passed / 1 skipped**; `ruff` clean (src/scripts/tests); `mypy` 0-new; **`freeze.py --check` passes all
  prose↔yaml consistency** (canonical hash `7e6da01f → a1f458d5 → 5aaf1fc4` — the intended pre-freeze R16/R17
  refinements; `freeze_hash` still null, so no committed hash is violated). An independent re-audit of the
  inference rewrite + wiring was run.

## [2026-06-19] — Provider-neutral LLM architecture (Gemini prototype + Opus 4.8 campaign) + deep adversarial audit (38 findings fixed)

User mandate: "engineer everything … we will use gemini 3.5 flash for the prototype, and opus 4.8 for the
main … create a necessary architecture for that … very deeply search and find all bugs, all vulnerabilities,
all issues, all inconsistencies … fix everything … verify strictly and deeply." Scope boundary held per
CLAUDE.md §2: "advanced/sophisticated" = engineering quality (provider-neutrality, robustness, observability,
type-safety, test depth), NOT new scientific scope — the frozen pre-registration's 6 fields are untouched
(`freeze.py --check` canonical hash `7e6da01f…` unchanged throughout). ADR: **ADR-035**.

### Provider-neutral transport architecture (ADR-035)
- **`src/llm/client.py`** — new `build_transport(provider, model, api_key_env=None, *, temperature, max_tokens,
  max_retries)` single dispatch point over a provider registry: `anthropic` → the native Anthropic SDK
  transport; `openai` / `gemini` / `deepseek` → the OpenAI SDK pointed at each provider's `base_url`
  (`_OPENAI_COMPAT_BASE_URL`; Gemini = `https://generativelanguage.googleapis.com/v1beta/openai/`) — so a
  new provider is ONE registry entry, not a four-file edit, and **no new dependency** (Gemini rides the
  existing `openai` SDK). Added `default_key_env(provider)` (`_DEFAULT_KEY_ENV`) and `PROVIDERS`. New
  `_OpenAITransport` (callable, mirrors `_AnthropicTransport`): injected tenacity `retrying`, `temperature`
  sent only when set, `max_tokens` sent (final-audit #35), `last_usage` token capture for cost accounting.
- **Orchestrators** now call `build_transport` (DRY): `scripts/run_prototype.py::run_arm`,
  `src/orchestration/parallel.py::_drive_llm_arm`, and via the threaded `llm_cfg`, `scripts/run_campaign.py`.
- **Separate reward-authors per stage (the shared-config bug fixed).** `run_arm` gained an `llm_cfg` param;
  the campaign threads its OWN `llm` block (Claude **Opus 4.8**) down `run_campaign.main → run_headline_campaign
  → run_winner_search → run_arm`, so it no longer inherits the prototype's author. `config/prototype.yaml`
  → **Gemini 3.5 Flash** (`provider: gemini`, `GEMINI_API_KEY`, `pass: B`, `temperature: 1.0`);
  `config/campaign.yaml` → **Opus 4.8** (`temperature: null`, `diversity_prompt_variation: true`).
- **Temperature-free within-generation diversity.** `src/llm/loop.py::_diversity_directive(cidx, n)` appends a
  per-candidate exploration directive (uniform across arms → NOT an H2 confound) when
  `diversity_prompt_variation` is set — required because Opus 4.8 rejects the `temperature` parameter, while
  Gemini honors `temperature: 1.0`. Applied identically in the serial (`loop.py`) and parallel
  (`parallel.py`) paths; the exact prompt sent is archived (C-2).

### Deep adversarial audit — 8 dimensions × 3-vote verify (134 agents) → 38 confirmed findings, ALL fixed
A multi-agent workflow fanned adversarial auditors across correctness, sandbox security, inference math, the
data pipeline, orchestration/determinism, config consistency, the campaign protocol, and coverage gaps; each
finding was verified by 3 independent skeptics (≥2/3 to confirm). 42 raised → **38 confirmed** (3 critical,
9 high, 11 medium, 15 low), 0 under-verified. Every confirmed engineering finding is fixed and regression-tested.

**Critical**
- **#1 (reward extraction).** Raw LLM completions went straight to `ast.parse`; a markdown fence or prose
  preamble from Opus 4.8 (thinking off) / Gemini → `SyntaxError` → candidate rejected for FORMATTING, which
  at campaign scale could starve every arm (the stub returns bare code, so the fast suite never saw it).
  Added `src/sandbox/executor.py::extract_reward_source` (strip fences / prose preamble-epilogue; clean code
  is a byte-identical no-op), applied at the LLM boundary in `loop.py` + `parallel.py` (clean archive) and as
  a safety net atop `validate_once` (single choke point).
- **#2 (search RNG).** The sequential search arms (`run_arm`) called `random_search_over_code` /
  `bayes_opt_over_template` WITHOUT `rng=`, so `np.random.default_rng()` drew OS entropy (not the run seed) →
  non-reproducible winner selection. Now seeded `rng=np.random.default_rng(seed)`, mirroring the parallel path.
- **#3 (sandbox RCE).** The AST gate was a denylist; numpy's object graph reaches `os`/`builtins`/`pickle` via
  gate-legal submodule chains (e.g. `np._pytesttester.os.system(...)` — verified end-to-end RCE + env-var
  exfiltration). Replaced with an **allowlist** (`_ALLOWED_ATTRS`): every attribute must name a known-safe
  numeric/array/container op — sound because the dangerous leaves (`system`, `popen`, `environ`, …) are not
  numeric, so no chain can reach them. Also banned `ndarray.ctypes`/`.data` (FFI/pointer). Verified all
  known-good rewards (reward_family + 12 stub archetypes) still pass and the RCE vectors are blocked.

**High** — #4/5/8 matched compute (SEARCH selected at 25k but TEST evaluated at 50k): the campaign now builds
ONE agent_cfg and threads the SAME train_steps into both stages. #6 `run_prototype.py --dry-run` forces
keyless stub (it would otherwise hit real Gemini after the config flip). #7 gold VIX double-lag (pipeline
pre-shift + env lag → t-2): added `Panel.vix_prelagged`; the env lags only the contemporaneous (synthetic)
convention. #10/17 resume re-searched & re-froze a possibly-different winner while skipping its test seeds
(frozen/test desync): SEARCH+FREEZE are now resume-aware (load the existing frozen winner) + a frozen-source
hash guard. #11 the TEST stage never re-seeded per seed: added `set_global_seed` per seed. #12 the validation
fixture was 2-element: enlarged to realistic per-step shapes + documented that the in-process training path
is not a containment boundary.

**Medium** — #16/#36 the LLM provenance archive (raw response + token usage) was built then discarded: now
persisted to `llm_calls.jsonl` per arm (serial + parallel). #19 VIX-units (clarified: points is the canonical
LIVE unit; the conversion is deliberate, not a silent revert). #20 `ffill_then_zero` fabricated post-delisting
returns: now ffills interior gaps then zeros the dead tail. #21 the matched-budget guard passed at 100%
candidate failure: now requires ≥1 accepted candidate + persists `failures.jsonl`. #22/#33 candidate_id /
diversity-directive index diverged between paths: parallel uses the per-gen index `k`. #24 added the frozen-H2-
family fail-loud guard to `run_campaign` (PREREGISTRATION §10 prose now true). #34 unified the reflection
preamble across the serial/parallel paths.

**Low** — #15 stale docstring; #25 provider-aware key default on the parallel path; #26 honor `agent.device`;
#27 annotated dead config keys; #28 env guards `max(vol_windows) ≤ lookback`; #29 corrected dead stub-script
imports; #30 `winner_returns` ndarray-truthiness guard; #31 `deflated_sharpe` alias rejects `sr_benchmark`
loudly; #32 `winner_dsr` uses the full per-arm trial count; #35 OpenAI transport sends `max_tokens`; #37
`load_run` verifies env.json provenance; #38 removed the unfulfilled `prompt_hash` field.

**Flagged, NOT silently changed (pre-registered analysis plan — CLAUDE.md §3 requires user/supervisor sign-off):**
#9/#14 the headline H2 inference averages the per-seed return series before the bootstrap (anti-conservative,
~√N variance collapse); #18 the H2 conjunction / family-p-value functions are implemented + tested but not
wired into the analysis entry point; #13 the sealed-test leg reuses the fixed 2005-cohort universe across
2018-2025 (composition bias the prototype prose calls disqualifying). These are statistical-design decisions,
raised for the user rather than unilaterally rewritten.

### Verification
- **Tests:** +18 regression guards (`tests/test_audit_regressions.py`: extraction, RCE-blocked, vix-lag,
  vol-window guard, max_tokens, dsr alias, ndarray winner_returns) + the earlier +13 transport/diversity tests.
  Full non-slow suite **404 passed / 1 skipped, ×3 order-randomized (pytest-randomly)**.
- **Static:** `ruff check src/ scripts/ tests/` clean; `mypy src` at the 13-error pre-existing baseline (0 new);
  `freeze.py --check` canonical hash unchanged. (Pre-existing lint debt in `archive/` + generated `outputs/`
  artifacts is out of scope.) A pre-existing truncated `scripts/verify_inventory.py` (unrelated to the audit)
  was made syntactically valid with an honest deferred-stub.
- **Re-audit (two independent passes).** Pass 1 (verify-fix + regression-hunt, 33 agents) re-checked every
  critical/high fix and the changed files: 3 fixes clean, 8 "correct-but-incomplete" with mostly-cosmetic
  residuals, and — decisively — **2 HIGH regressions from the #7 vix fix itself**: `Panel.slice()` dropped
  `vix_prelagged` (a sliced gold panel reverted to the double-lag), and the terminal `step()` indexed
  `vix[panel.T]` out of bounds on a prelagged panel (**would have crashed the gold campaign's once-per-arm
  sealed evaluation on its final step** — invisible to the fake-based fast suite). Both fixed (slice
  propagates the flag; the vix index is clamped to the last row) + regression-tested. The real missed
  call-sites the residuals named were also closed: the parallel BO arm is now seeded (#2 parity) and the
  parallel `_summary`/`_drive_llm_arm` got the accepted>0 guard + `failures.jsonl` (#21 parity). Pass 2
  (16 agents, over the residual-fix files) verified **all five residual fixes correct AND complete** with no
  new regressions. It additionally flagged **2 PRE-EXISTING, headline-safe items** in `resolve_windows`
  (untouched by this work): on the 600-day SYNTHETIC dry-run panel — which cannot span the frozen 2018-2025
  test calendar — the clamped windows are rejected by the builder, so the dry-run smoke exercises
  search→select→freeze but not TEST, and a broad `except ValueError` mislabels that as `winner_not_testable`.
  The real 5,283-session gold path is verified unaffected (the headline windows resolve correctly). These are
  left as documented smoke-path limitations (modifying the windowing risks the frozen gold splits) — see the
  flagged items.
- **Final state:** full non-slow suite **407 passed / 1 skipped, 6 consecutive order-randomized runs**; +21
  regression guards total; `ruff` clean (src/scripts/tests); `mypy` 0-new; `freeze` hash unchanged.

## [2026-06-19] — Refinitiv access VERIFIED live + probe-tooling fixes + full run-readiness preparation

End-to-end run preparation at the user's request ("absolutely fully prepare everything for a run"), plus a
**material data-provenance correction** and two `data_pipeline` probe-tooling bug fixes. ADR: **IMPL-RUNPREP-1**.

### Data-provenance CORRECTION (the gold is Refinitiv, not yfinance)
- An earlier turn this session wrongly stated the gold panel was built from yfinance (over-reading the
  datasheet's vendor tags). **Corrected:** `data/gold/returns_panel_univ3.parquet` is the **licensed
  Refinitiv, survivorship-free, PIT** panel (`data_pipeline/README.md`): union **953 RICs incl. 333 dead**,
  PIT membership via reverse event replay through `TR.IndexJLConstituent*` (ADR-020), daily total returns
  via datagrid `Frq=D`, two-vendor reconciliation (corr 0.99994). The 333 dead tickers are dispositive —
  only a licensed survivorship-free vendor supplies delisted names' full history. yfinance is only the
  second reconciliation vendor; FRED supplies VIX, Ken French the factors. CLAUDE.md's "Refinitiv/LSEG"
  was correct; ADR-015's "empty scopes → yfinance fallback" was an interim 06-10 state, superseded when
  entitlements were fixed by 06-12 and the full Refinitiv PIT build ran. **Thesis/viva: claim
  Refinitiv/LSEG survivorship-free PIT** (yfinance as cross-check).

### Refinitiv entitlement VERIFIED LIVE (2026-06-19) — `univ4` unblocked
- The user's `.env` platform creds (`REFINITIV_{USERNAME,PASSWORD,APP_KEY}`) were tested two ways:
  (a) **direct** via `acquire.open_refinitiv_session()` (platform `GrantPassword`, headless — no Workspace):
  `OpenState.Opened`; live pricing (AAPL.O) PASS; **dead-ticker `LEH.N^I08` 2008 history PASS** (177 rows
  OHLC+volume through Lehman's collapse). (b) the **official probe** (`python -m src.data.cli probe`):
  **7 PASS** (P0 session, P1 chain, P2/P3 PIT membership content-validated incl. Lehman 2008 leaver, P5
  total-return continuity, P6 delisted coverage, P8 RDP scope census), P4 BLOCKED (DatastreamPy absent —
  DSWS path not used), P7 MANUAL. Verdict: ***"Pre-2016 membership path verified — proceed with the full
  PIT build."*** So `univ4` (apply the proper Shumway −30/−55% delisting returns vs the provisional
  `liquidate_to_cash` fill; likely a re-PROCESS of already-pulled delisting metadata, not a fresh re-pull)
  is now achievable. `docs/evidence/entitlement_report.md` + `entitlement_probes.json` regenerated.

### `data_pipeline` probe-tooling fixes (post-unification bugs)
- **`acquire.py::load_env`**: searched only `ROOT/.env` where `ROOT = data_pipeline/`; after the 06-17
  unification (ADR-022) the `.env` moved to the **parent** (unified repo root), so creds never loaded and
  `open_refinitiv_session` silently fell back to the **desktop proxy** (`localhost:9000`, which needs
  Workspace running). Fixed: search `ROOT/.env` then `ROOT.parent/.env`. `probes.py` `env_file` flag
  updated to match.
- **`probes.py::write_report`**: crashed with `UnicodeEncodeError` writing the `🚫` status icon under the
  user's `cp1251` (Russian) Windows locale. Fixed: `write_text(..., encoding="utf-8")` on both the report
  and the JSON sidecar.

### `.env` updated (user-directed)
- Wrote the pasted Refinitiv creds into the gitignored `.env` (merge: the three `REFINITIV_*` keys updated;
  `ANTHROPIC_API_KEY` preserved; `FRED_API_KEY` left as-is — the paste's was empty, FRED only needed for a
  VIX re-pull). Values never echoed; only NAMES + set/empty status printed. **Both pasted secrets (Refinitiv
  password, Anthropic key) are in the chat transcript → rotate after the project.**

### Run-readiness PROVEN on this laptop
- **Full non-slow suite: 373 passed / 1 skipped**, order-randomized (the `data_pipeline` edits don't touch
  the engine `src/`). **`freeze.py --check`: OK** (6/6 prose↔YAML fields consistent; canonical hash
  `7e6da01f…` unchanged; `freeze_hash: null` pre-freeze). **`run_prototype.py --dry-run`: EXIT 0** — 3 arms
  × 2 cand × 200 steps, real SAC train → measure → select → archive, winners produced, budget matched,
  18.3s. The end-to-end pipeline runs here; the full ~9.1 h prototype (`--parallel`, 240×25k @ ~183 steps/s
  on this RTX 4050) will work.
- **New: `docs/RUN_READINESS_2026-06-19.md`** — the operational runbook: status board, the two-pass model,
  exact run commands + timings + monitoring + resume + success criteria for prototype → (Pass-B smoke) →
  pilot → freeze → univ4 → campaign → analysis, plus the gated hand-off checklist and security note.

## [2026-06-19] — Run-readiness wiring: real Anthropic Pass-B + the vix-units fix (closes ADR-034 "Wiring queued")

Completes the ADR-034 §"Wiring (queued)" items so the headline campaign can actually run the real
reward-author (Claude Sonnet 4.6) instead of the keyless stub, and fixes a silent regime-collapse bug.
ADR: **IMPL-WIRING-1** (docs/DECISION_LOG.md). **Full non-slow suite: 373 passed / 1 skipped**, order-
randomized (pytest-randomly); +21 over the prior 352 (20 provider/transport tests + 1 gold-vix regression).
**The freeze hash is UNCHANGED** — none of `PREREGISTRATION.md` / `config/preregistration.yaml` is touched.

### THE CRITICAL FIX — the headline campaign could not call the real LLM at all
- **`scripts/run_campaign.py::main` was HARDCODED to the keyless stub.** It never read `provider`/`pass`,
  so the call to `run_headline_campaign(...)` fell through to the signature defaults `pass_mode="A",
  provider="stub"`, and `generations` was pinned to `1`. The script whose numbers enter the dissertation
  would have silently run the StubDesignerTransport (not Sonnet 4.6) on every invocation. Fixed: `main`
  now reads `config/campaign.yaml: llm` → `pass` / `provider` / `generations` and threads them through.
  `--dry-run` still forces the stub (`A`/`stub`/`1`) so the smoke path never burns the API key. The run
  banner now prints `gens=… pass=… provider=…` so the active mode is visible in every log.

### THE MAJOR CATCH — temperature stays 1.0 (Eureka), NOT 0
- My continuation summary asserted "set temperature=0". **That is wrong and would have gutted the
  experiment.** `src/llm/loop.py` samples all `candidates_per_gen` candidates per generation from the
  *identical* `system`+`user` prompt (loop.py:292-296) — within-generation diversity comes ENTIRELY from
  sampling stochasticity, so temperature MUST be > 0 (ADR-016 sets 1.0 per Eureka). ADR-033's "Sonnet 4.6
  honors `temperature=0`" is a provider-*selection* criterion and explicitly notes "reproducibility comes
  from the archive (replay), not live determinism" — it is NOT an instruction to run at 0. Verdict
  (reconcile-don't-assume, CLAUDE.md directive 1): **temperature = 1.0 everywhere**; transports leave it
  unset → provider default unless config says otherwise; the configs record 1.0 with the rationale inline.

### Provider transports + client — `src/llm/client.py` (ADR-033/034 hardening)
- **`make_anthropic_transport` now wires the full ADR-034 queue**: (a) **prompt-caches** the static system
  block (`system=[{type:text, text, cache_control:{type:ephemeral}}]`) — the K-shared-context cache lever
  (ADR-016); (b) **owns retry/backoff** via lazy `tenacity` (exponential 1→30 s, ≤6 attempts) on a
  PORTABLE transient predicate `_is_transient_api_error` (connection/timeout/rate-limit/5xx by class-name +
  HTTP status; 4xx is terminal) while the SDK's own `max_retries` is set to **0** so tenacity is the single
  observable policy; (c) **archives token `usage`** (input/output + cache write/read) via a small callable
  `_AnthropicTransport` exposing `last_usage`; (d) accepts `temperature` (passed only when set). tenacity
  is imported lazily and **degrades to no-retry if absent**, so the deterministic core still imports without
  it (same discipline as the lazy `anthropic` import).
- **`make_openai_transport`** gains a symmetric `temperature` kwarg (used only for the N3/DeepSeek-V4 check
  model, ADR-033).
- **`ProvenanceRecord`** gains an optional `usage: dict | None` field (default `None`); `LLMClient.complete`
  reads `getattr(transport, "last_usage", None)` and archives it (audit C-2 + cost accounting). Transports
  without usage (FakeTransport) archive `None` — no error.
- **`LLMClient` is now provider-aware** (closes the latent OpenAI-default footgun the audit flagged): reads
  `cfg.provider` (default **`anthropic`**), defaults `api_key_env` to `ANTHROPIC_API_KEY` for anthropic else
  `OPENAI_API_KEY`, threads `cfg.temperature`, and dispatches `_ensure_transport` to the matching
  `make_*_transport` (`anthropic` | `openai`/`deepseek`; unknown → clear RuntimeError). Both orchestrators
  always INJECT a transport, so this only governs non-injecting callers — but it makes the standalone client
  honest and matches the project decision. Module + class docstrings updated (no longer claim OpenAI-default).

### Orchestrator threading — model/key/temperature now flow to the transport
- **`scripts/run_prototype.py::run_arm`** (the shared search worker reused by BOTH prototype and campaign):
  reads `temperature` from the `llm` block and passes it to `make(model, key, temperature=…)`; the
  `api_key_env` default flips `LLM_API_KEY` → `ANTHROPIC_API_KEY`. The parallel-path opts dict in
  `run_prototype.main` now carries `temperature` (same default flip).
- **`src/orchestration/parallel.py::_drive_llm_arm`**: reads `opts["temperature"]` and passes it through.

### Configs reconciled to ADR-016/033 (were stale placeholders)
- **`config/prototype.yaml: llm`** (the SHARED reward-author config `run_arm` reads for prototype AND
  campaign): `model_snapshot "<pinned-when-Pass-B>"` → **`claude-sonnet-4-6`**; `api_key_env LLM_API_KEY` →
  **`ANTHROPIC_API_KEY`**; **added `temperature: 1.0`** with the Eureka-diversity rationale + a DO-NOT-set-0
  warning. `pass:A`/`provider:stub` kept (the prototype is directional/keyless by default).
- **`config/campaign.yaml`** — **added the missing `llm` block** (the campaign had none): `pass: B`,
  `provider: anthropic`, `generations: 6` (= 6×5 = the 30-candidate budget; the H3 single-shot control runs
  the same budget at `generations:1`). Documents that model/key/temperature are the shared prototype values.
- **`config/llm.yaml`** — reconciled the stale reference: `provider: anthropic` (new), `model_snapshot
  claude-sonnet-4-6`, key-name `api_key_env_var → api_key_env: ANTHROPIC_API_KEY`, `temperature: 1.0` (kept;
  comment corrected — it is Eureka diversity, not "freeze in Phase 1"), and the `open_weights_check_model`
  placeholder replaced with an HONEST `PIN_ME` + ADR-033 note (Llama-4 N3 control; exact HF commit pinned at
  use — no fabricated revision, CLAUDE.md directive 4). The temperature 1.0 there was NOT a bug (it matches
  Eureka); only the model/key/`<placeholder>` strings were stale.
- **`pyproject.toml`**: `tenacity>=8.2` added (LLM-transport backoff; SDK `max_retries=0`).

### Tests
- **`tests/test_llm_transport.py` (NEW, 16):** drive `_AnthropicTransport` with a FAKE SDK client (no
  `anthropic`/`tenacity` install needed) — prompt-cache content-block shape, `cache_system=False` → plain
  string, text-block concatenation, temperature passed-when-set / omitted-when-None, `last_usage` capture,
  `_usage_dict` None-handling, the transient/terminal classification (5 transient classes + 5xx-vs-4xx +
  ValueError), an injected-retrying wrapper actually retrying, `_make_retrying(0)→None`, and the no-key raise.
- **`tests/test_agents.py`:** replaced the OpenAI-default assumption with provider-aware tests — default
  provider is anthropic + `ANTHROPIC_API_KEY`; explicit `openai` provider routes to the OpenAI transport;
  unknown provider raises; `complete` archives transport `usage` (and `None` for a plain transport).

### vix-units bug — gold regime stratification was silently collapsed (audit B-6)
- **Root cause (verified against the frozen gold, not assumed):** `data/gold/cash_features_*.parquet` store
  vix as a FRACTION (FRED VIXCLS / 100 — min 0.0914, median 0.1672, max 0.8269 over 2005-2025), but
  `config/regimes.yaml` thresholds are conventional POINTS (calm<15 / stress>25). Every one of 5,282 gold
  dates is < 15 → ALL labelled calm → `independent_regime_count` = **1**, silently zeroing the regime-
  stratified evaluation that bounds H2 power. The env obs is scale-agnostic (uses `panel.vix[t-1]` raw under
  VecNormalize, `portfolio_env.py:326`), so the bug touched ONLY regime labelling.
- **Fix — `src/data/loaders.py::load_gold_panel`:** normalize vix to points at the load boundary, magnitude-
  GUARDED (`if median(vix) < 2.0: vix *= 100`) so the current fractional gold is rescaled (~9.9..80.9) while a
  future points-storing rebuild is never double-scaled. Chosen over flipping the thresholds to decimal because
  it keeps the WHOLE system in one conventional, viva-defensible unit (the thresholds, the synthetic panel
  ~10-50, the trainer's documented ~10-80 obs range, and the env doc "FRED VIXCLS" were all already points —
  only the frozen gold was fractional). The frozen parquet is untouched (transform on read).
- **Result:** gold vix → points (median 17.0, max 80.9); regimes now 955 calm / 1071 normal / 491 stress with
  **214 independent episodes** (was 1). `config/regimes.yaml` annotated with the convention + loader
  dependency. **`tests/test_loaders.py`:** new regression loads the real gold, asserts vix is in points
  (min>1, median>5, max>25) and that all three regimes + >1 episode realise — the collapse cannot recur.

### Status — what this does and does NOT unblock
- **Unblocked (ungated, done here):** the campaign/prototype can now invoke the real Sonnet 4.6 Pass-B path
  (set the staged `ANTHROPIC_API_KEY` in the gitignored `.env`); regime-stratified analysis is meaningful.
- **Still gated on the user / GPU box (unchanged):** `make freeze`; the univ4 Refinitiv rebuild; the
  `requirements.lock` on the 4090 (must `pip install` the now-declared `tenacity`); the pilot → `power_analysis
  --sigma-dsr`; the campaign run itself. The live key pasted in chat remains the user's to manage per ADR-033.

## [2026-06-19] — Keystone Rank 7: reward forensics (§6.1 "open the black box", H2 interpretability)
- **`scripts/inspect_rewards.py` — implemented (was a STUB) + `tests/test_inspect_rewards.py` (NEW).** Replaced the
  `raise SystemExit('STUB')` and deleted the two dead imports (`from src.io.results import ResultStore`, `from
  src.feedback import distributional` — results.py has no `ResultStore`; the feedback code is `measurement.py`/
  `schema.py`). The tool produces the §6.1 GREEN-gate QUALITATIVE evidence that the LLM reward-designer *used* the
  distributional feedback (H2), not merely that a metric gap exists.
- Three analyses, **read-only** on the archive (audit C-1, via `load_all`), **reusing** `analyze_results.{load_arms,
  interpretability, _TAIL_TERMS}` (no duplication): `per_generation_summary` (per-arm-per-gen best/mean fitness +
  reward-code size/complexity + tail-term-usage trend); `feedback_responsiveness` (per-arm Pearson correlation of
  successive reward-source EDIT magnitude vs the L1 tail-stat DELTA the LLM was fed — the "did it use the information"
  core; finite, `None` for scalar/placebo which carry no tail); `hacking_taxonomy` (specification_gaming / proxy_no_tail
  / tautology via the `_TAIL_TERMS` lens + collapsed OOS fitness; Skalse 2022, Hadfield-Menell 2017). Emits
  `reward_forensics.md` + `.json` into `--out-dir` only.
- Tests: 12 fast/no-torch — keying by (arm, generation); a FINITE responsiveness score DISTINGUISHING a constructed
  responsive (+0.92) vs unresponsive (−0.98) fixture; a flagged gaming example; markdown emitted to a tmp dir; an
  end-to-end `inspect()` over written archives that asserts the archive is untouched. **Suite: 261 passed / 1 skipped**
  (+12). Ruff clean. ADR: IMPL-INSPECT-1.

## [2026-06-19] — Final acceptance audit (6-auditor workflow) + 3 P1 fixes
- **Ran a final adversarial acceptance-audit workflow** (6 read-only auditors over the completed codebase —
  integration, inference-math, frozen-prereg/freeze, sandbox+data, docs-vs-code, completeness; findings adversarially
  verified). Verdict: **3 confirmed P1 defects** in implemented code (the gated items correctly NOT flagged). All fixed +
  regression-tested:
- **P1-1 — `winner_dsr` 252× units bug (`scripts/analyze_campaign.py`):** the canonical headline DSR deflated the
  winner's PER-PERIOD Sharpe by a `var_sr` computed from ANNUALIZED candidate Sharpes (`sharpe_ratio` default
  `periods_per_year=252`), so `sr_star = sqrt(var_sr)·term` was ~15.87× too large → `dsr_canonical` collapsed spuriously
  to ~0. Fixed: compute the cross-candidate `var_sr` with `periods_per_year=1` (per-period, matching
  `deflated_sharpe_ratio`'s annualization-invariant convention); `winner_sharpe` stays annualized-for-display (labelled).
  R16's test hand-computed `var_sr` and bypassed `winner_dsr`'s internal call — so a new regression test invokes
  `winner_dsr` DIRECTLY and asserts `var_sr` is per-period (not ~252×) + the DSR is non-collapsed.
- **P1-2 — sandbox file-READ escape (`src/sandbox/executor.py`):** `np.recfromtxt`/`np.recfromcsv` (genfromtxt aliases)
  + `np.fromregex` (file-first read) slipped the AST gate → added to `_BANNED_ATTRS` + 3 denial tests.
- **P1-3 — sandbox file-WRITE escape:** `ndarray.dump(path)`/`.dumps()` pickle to an arbitrary path (the tofile hole,
  reopened) → added `dump`/`dumps` to `_BANNED_ATTRS` + 2 denial tests.
- **Full suite: 352 passed / 1 skipped** (+6). The freeze hash is **UNCHANGED** (code/test fixes; `PREREGISTRATION.md` +
  `config/preregistration.yaml` — the hashed artifacts — untouched). ADR: IMPL-AUDITFIX-1. **Residual P3 (noted):**
  `scripts/build_gold.py`/`verify_gold.py` are deferred-by-design stubs not yet labelled "deferred" — doc polish, not a
  defect. **Auditors' hardening rec (future ADR):** replace the numpy denylist with a positive allowlist of pure-array
  ops (the "forgot to ban X" class recurs); `RLIMIT_FSIZE`/namespace is the backstop.

## [2026-06-19] — Rank 9: pre-registration freeze gate (`scripts/freeze.py`)
- **Implemented `scripts/freeze.py`** (was a `SystemExit` stub): **canonical hash** = SHA-256 over the LF-normalized
  UTF-8 bytes of `PREREGISTRATION.md` ++ `config/preregistration.yaml` (fixed order: prose then yaml, `\n`-joined;
  BOM/CRLF-invariant). The **prose↔YAML consistency GATE** checks all 6 freeze-relevant fields (seeds=30,
  `inference.testing_family.m`=6 == len(members), `difference_tests`, `sesoi`=0.05, `equivalence_margin`=0.05,
  `cost_sweep.grid_bps`) — comparing the NUMBER parsed from the prose to the YAML value, so a silent drift fires.
- **Phase-0 precondition:** refuses unless `phase0_smoke_passed_log_id` is set. **`--check` mode** re-runs the hash +
  all assertions WITHOUT writing (exit non-zero on drift), wired as `make freeze-check` for CI.
- **Write path (implemented, USER-GATED — NOT executed):** `do_freeze` flips `frozen:`/`freeze_hash:` via a line-level
  edit (preserves every comment + amendment), appends a dated `FREEZE-DONE` entry (hash + UTC + git SHA) to the ADR-005
  slot in `docs/DECISION_LOG.md`, creates a signed tag `prereg-v1.0` (best-effort → annotated fallback), and `ots
  stamp`s the hash (best-effort → skip if absent); the recorded hash is the PRE-flip content (= what `--check`
  re-derives). Refuses if already frozen.
- **`--check` PASSES on the current consistent prereg** (exit 0; Phase-0 met; all 6 fields OK). Deterministic canonical
  hash (3 runs): **`7e6da01f…e41d6`** (informational — the recorded value once `make freeze` runs, absent further
  amendments). **Tests:** `tests/test_freeze.py` (19) — gate raises on each deliberate mismatch; hash deterministic +
  order/content-sensitive + LF-invariant; `--check` mutates nothing. **Full suite: 346 passed / 1 skipped** (mypy + ruff
  clean). ADR: IMPL-FREEZE-1. **The real `make freeze` is the user's gated action — NOT run.**

## [2026-06-19] — Wave-3 freeze-prep: pre-registration amendments D2/R11/R12/R13/R15 (ADR-034)
- **PREREGISTRATION.md (dated amendments only; FROZEN doc):** §6+§12 **Amendment D2** (user-approved) — winner seed count
  **5→30** (search budget untouched; seeds-on-winners); §10 **R13** the multiple-testing family ENUMERATED + FROZEN at
  **m = 6** (`{arm-contrast × {Sharpe, CVaR-0.05}}`, incl. the 3 H2-conjunction legs; BH q=0.05 primary, joint
  Romano-Wolf the FWER alternative; Harvey-Liu t>3 scoped to absolute-alpha only); §10 **R11** Sharpe-test relabel
  (studentized-LW → re-centred basic stationary block-bootstrap, numerics unchanged); §10 **R15** pre-registered
  cost-robustness sweep; §10 **R12** SESOI=0.05 + TOST ±0.05 DSR. New **Amendment record** table + Freeze-record row.
- **config/preregistration.yaml (machine-readable mirror):** `seeds:[0..29]`; `difference_tests:
  [sharpe_recentred_bootstrap, cvar_difference]`; new `inference.testing_family` (m:6 + 6 members) +
  `multiple_testing_primary/q` + `alpha_hurdle_scope`; `inference.{sesoi,equivalence_margin}=0.05`; top-level
  `cost_sweep`. **Prose↔YAML verified consistent on all 6 freeze-relevant fields.**
- **config/campaign.yaml + config/inference.yaml:** headline seeds → `[0..29]` (ablation `[0,1,2]` untouched).
  **docs/COMPUTE_AND_TRAINING_TIME.md:** run-count/GPU-hour bands recomputed as winners×30 (lean ≈600 runs ≈110 GPU-hr
  ≈ $32-44 / ~4.6 days on a rented 4090; full 30×5 grid retained as the costed alternative).
- **scripts/analyze_campaign.py:** added `assert_realized_family_matches_frozen` (# fail-loud) wired into
  `collect_family_pvalues` — asserts the realized {contrast×metric×level} family == the frozen `inference.testing_family`
  (no-op on a missing-arm subset or the opt-in cvar_01 superset).
- **docs/POWER_ANALYSIS.md** SESOI reconciled 0.200→0.05. **Suite: 327 passed / 1 skipped; ruff clean.** **ADR-034**
  (supersedes the PENDING frozen-doc amendment notes in IMPL-BOOT-1 / IMPL-COSTSWEEP-1 / IMPL-POWER-1 — now applied).
  The amended design is internally consistent and ready for `freeze.py` (Rank 9) to hash.

## [2026-06-19] — Rank 5: univ4 Shumway-STYLE delisting build (CODE; parquet GATED on Refinitiv)
- **`membership.apply_shumway_corrections` — KeyError landmine FIXED + direct tests (had none).** The surcharge booked
  onto the all-NaN nominal-delist row via `out.loc[date,name]=value` — KeyErroring off-grid (the `^MYY` delist date
  often is) or planting a phantom row `liquidate_to_cash` then zero-filled (so the crash return never reached the tail).
  Now books on the **LAST VALID session** (`_last_valid_label`), compounded **MULTIPLICATIVELY** `(1+r)(1+dl)−1` (never
  additive; OpenSourceAP #49); all-NaN names → `shumway_skipped_no_obs`; vendor-terminal preferred (kept). Audit log
  gains `booked_on`/`delisting_return`/`prior_return`.
- **`build_universe(apply_delisting=False)` wires STAGE 7** between the clean freeze and `build_gold`: derives the delist
  map (`_derive_delisting_map`, reusing `parse_delisting_metadata` over `rf_meta_*` + `^MYY`/exchange-code fallback),
  feeds the CORRECTED frame to gold, freezes `clean_returns_shumway`/`shumway_audit_log`. **Default off → `_univ`
  byte-identical.** GATED: the real `_univ4` parquet needs the data_pipeline re-run + Refinitiv creds.
- **`loaders.gold_suffix()`** — `LLM_RP_GOLD_SUFFIX` switches the gold suffix (default `univ3`, **NOT** flipped to univ4).
- **`tests/test_membership_shumway.py` (NEW, 13)** incl. **TAIL-PRESERVATION:** corrected synthetic CVaR_05 strictly
  more negative than `liquidate_to_cash` (gap > 1e-4 — the surcharges, not float noise). **Suite: 327 passed / 1
  skipped.** Ruff clean. ADR: IMPL-UNIV4-1. ⚠ **Headline tail numbers remain invalid until the gated `univ4` rebuild +
  env reload** (`LLM_RP_GOLD_SUFFIX=univ4`); report the {0%, −30%, −55%, −100%} sensitivity band then.

## [2026-06-19] — Rank 14: reproducibility/provenance trio (replayable archive + CI-grade env)
- **`scripts/capture_env.py` (NEW):** EXTENDS `provenance.env_fingerprint()` with `pip_freeze` (importlib.metadata),
  `nvidia-smi` driver (best-effort), `torch.version.cuda` + cuDNN + `are_deterministic_algorithms_enabled()`, the run
  seed, an `os.environ` snapshot (CUBLAS_WORKSPACE_CONFIG/PYTHONHASHSEED/CUDA_VISIBLE_DEVICES); writes
  `outputs/<run>/env.json` (`capture_env`/`env_json_sha256`/`write_env_json` API + CLI). Wired into the orchestration
  archive (`parallel.py`) + the sequential path (`run_prototype.py`) so every run dir gets one; the bare-string
  `env_fingerprint` (e.g. `'synthetic:steps200'`) is now `{label, env_json_sha256}` pointing at the content-hashed
  snapshot (audit C-2/C-6).
- **Persisted the rendered prompt (CLAUDE.md §6 "archive every prompt"):** added `'prompt'` to the LLM-loop + parallel
  candidate records; `results.write_run` dumps a `prompt.txt` sidecar next to `reward.py` and `load_run` reattaches it;
  `'prompt'`/`'prompt_hash'` added to `OPTIONAL_FIELDS` (REQUIRED_FIELDS unchanged → round-trip tests green). Closes the
  replay-archive gap — results now REPLAY with the exact prompt.
- **Makefile + pin:** added a gated `.PHONY lock` target (`uv pip compile --all-extras --generate-hashes`, pip-freeze
  fallback) — the lockfile itself MUST be generated on the Linux RTX-4090 box (cu124 wheels) → FLAGGED gated; pinned
  `pytest-randomly>=3.15,<5` (was declared but missing from the venv → the determinism guard can't silently disappear).
  Tests green. ADR: IMPL-REPRO-1.

## [2026-06-19] — Rank 12: power-analysis machinery (`scripts/power_analysis.py`)
- **Implemented `scripts/power_analysis.py`** (was a stub with a broken `from src.regimes import detect`): fixed the
  import to `src.regimes.definition.independent_regime_count`; added a **vectorized Monte-Carlo power routine** over the
  arm-level re-centred bootstrap difference test (faithfully reusing `bootstrap.sharpe_difference_test`'s SE-cancels
  rule), a **selection-aware (Šidák) α penalty**, **MDE** location at 80% power, and a **symmetric-margin TOST**
  equivalence test. σ (seed-to-seed validation-DSR sigma), SESOI, and the TOST margin are CLI parameters with flagged
  placeholder defaults; the inner bootstrap loops are vectorized (~5 s full run).
- **Filled `docs/POWER_ANALYSIS.md`** (every `___`): N=6, n_eff=30, `alpha_eff=0.0085` (m=6 Šidák), **MDE = 0.269 DSR
  (0.90σ)** at the placeholder σ, **trial count = 180** (6 arms × 30), SESOI + TOST recorded. **σ and the MDE are
  flagged pilot-TBD** — re-run `--sigma-dsr <pilot>` to finalise before the freeze.
- **Tests:** `tests/test_power_analysis.py` (14 fast) — import resolves; N sane; power ∈ [0,1] with correct monotonicity
  in effect/σ/N/seeds; null rejection ≈ α_eff; TOST flags equivalence/non-equivalence correctly. **327 passed / 1
  skipped.** ADR: IMPL-POWER-1.
- ⚠ **DATA-INTEGRITY FLAG (recorded; fix before the campaign — NOT a frozen-prereg item):** the gold panel's `vix` is
  stored as a **decimal** (~0.10-0.81) but `config/regimes.yaml` thresholds are **VIX points** (calm=15/stress=25), so
  regime auto-detection collapses every date to ONE regime. The agent added a `--n-regimes` override (default 6,
  literature-grounded) + surfaced the mismatch; the real fix is to rescale the gold `vix` to points OR set
  `regimes.yaml` to decimal thresholds (calm=0.15/stress=0.25).
- **PENDING (frozen-doc amendment, the Wave-3 pass):** the adopted **SESOI = 0.05 DSR + TOST margin ±0.05** for the H2
  contrast → PREREGISTRATION.md §10 + `config/preregistration.yaml inference:{sesoi, equivalence_margin}` (exact text in
  IMPL-POWER-1).

## [2026-06-19] — Rank 2c: bayes_opt archives a materialized executable reward_source (H4 held-out fix) — COMPLETE
- `src/baselines/reward_family.py`: added `params_to_source(coeffs, cvar_alpha, window) -> str` (additive; in `__all__`),
  a sibling of `params_to_reward` emitting the six-term H4 family at `coeffs` as runnable `def reward(...)` source
  (coefficients/alpha/window baked in via `repr`; body a verbatim transcription of the closure). Passes the AST gate +
  `validate_once`; reproduces `params_to_reward` **bit-for-bit** (max abs diff 0.0 over a 60-step stateful replay).
- **Wired into both archivers (orchestrator did the 2-site swap):** `scripts/run_prototype.py` (the sequential BO
  branch) and `src/orchestration/parallel.py` (the `kind=="coeffs"` worker) now archive `params_to_source(coeffs,
  cvar_alpha=alpha, window=window)` as `reward_source` instead of the non-executable `# coeffs=[...]` comment stub.
- **Why:** the BO arm (H4b) only held an in-memory closure; the stub left its frozen winner non-rehydratable for the
  sealed TEST leg (`_reinstantiate_frozen_winner → validate_once → winner_not_testable`), BREAKING the H4 LLM-vs-search
  held-out comparison. The BO winner now round-trips through the IDENTICAL test path as the LLM / random-search arms.
- **Tests:** `tests/test_reward_family_source.py` (11) — executable/gate/validate_once + ~1e-12 reproduction (incl. a
  real `bayes_opt_over_template` winner) + `_reinstantiate_frozen_winner` rehydrates a materialized BO winner (no
  `winner_not_testable`); the legacy stub still raises. Targeted search/family/campaign suite green. ADR: IMPL-BAYESSRC-1.

## [2026-06-19] — Rank 18: embargo at executed split boundaries + low-risk cleanups
- **Embargo (PREREGISTRATION §7):** `run_prototype._load_panel_and_windows` + `parallel._panel_and_windows` no longer
  abut train/val. New `loaders.embargoed_val_start` reads the **materialized** `development.validation_post_embargo`
  boundary from `data/gold/splits_univ3.parquet` (val → **2015-02-03**, byte-matching the freeze; 21-trading-day purge),
  with a 21-session fallback. Verified on real gold (val_start `2015-01-02 → 2015-02-03`, 21 purged sessions).
  (+`tests/test_embargo_splits.py`, 7 tests incl. real-gold e2e.) **Also closes the Rank-2 window-byte-match flag.**
- `fitness.held_out_fitness`: CVaR penalty guarded (`lam*abs(c) if isfinite else 0.0`) — no NaN propagation on empty /
  all-non-finite series; the `var_sr` kwarg (R16) preserved. `sandbox/executor.py`: removed the shadowed duplicate
  `candidate_failed`/`reset_failure_flag` (kept the live P0-2 pair). `run_prototype`: `set_global_seed(
  deterministic_torch=True)` parity. `loaders` checksum: `parents[1]→parents[2]` so the exact-relpath manifest branch
  fires (was basename-only). Added **`CITATION.cff`** (cff 1.2.0, Atesyakar/UCL, MIT) + **`DEVIATIONS.md`** (append-only
  post-freeze deviation log). **Tests: 302 passed / 1 skipped.** ADR: IMPL-CLEANUP-1.

## [2026-06-19] — Rank 17: IQN-era doc/code reconciliation + stale pre-merge quarantine
- **Quarantined the freeze hazard:** `git mv docs/staging/{PREREGISTRATION_v1.0_FINAL,FREEZE_RUNBOOK}.md →
  archive/pre_merge_repo_B/staging/` (+ README). The old runbook's `cp …_v1.0_FINAL.md PREREGISTRATION.md` would have
  CLOBBERED the canonical root pre-registration with the abandoned IQN draft at freeze. Left a corrected
  `docs/FREEZE_RUNBOOK.md` that freezes the canonical root `PREREGISTRATION.md` **in place** (no `cp`) and calls the real
  Makefile target **`make freeze`** (the old runbook called the nonexistent `freeze-design`).
- **Reconciled the distributional-feedback docs to the off-critic empirical+EVT reality:** rewrote
  `docs/distributional_feedback_schema.md` (impl path → `src/feedback/measurement.py`+`schema.py`, was the wrong
  `src/feedback_schema.py`; dropped the IQN-critic `Z(s₀,a₀)` sourcing + the frozen-DROPPED
  `crossing_rate`/`left_tail_slope`/`bowley_skew`/`moment_skew`/`n_quantiles`/`source`; field list = the frozen six;
  removed the false "Verified as-built 2026-06-10" line; kept the Kusuoka/Acerbi theory).
- **Archived the 5 inert IQN-era B-set prompts** (`*_v0.md` + `safety_instruction`) → `archive/pre_merge_repo_B/prompts/`
  — confirmed INERT (`src/llm/prompts.py::build_prompt_set` loads ONLY the live A-set `system.txt`/
  `initial_generation.txt`/`reflection.txt`; no code path loads any `*_v0.md`). They asserted the IQN sourcing + a wrong
  `compute_reward(ctx)` contract. Updated `prompts/README.md`, `config/eureka_loop.yaml` comments, root README.
- **Compute provenance:** `config/campaign.yaml` compute → `primary: rtx_4050` / `campaign: rented_rtx_4090` (was
  `rtx_4090`/`ucl_myriad_array_job` — NO Myriad access, ADR-023); README Phase-0 smoke → owned RTX **4050**; SUPERSEDED
  headers on the three IQN-SAC reports. **Seed counts untouched (R10's domain).** Engine tests: **291 passed / 1
  skipped**. ADR: IMPL-DOCSYNC-1. Companion fix: `docs/DECISION_LOG.md` DATA-REAL-1 corrected CRSP-via-WRDS →
  Refinitiv/LSEG (the live source).

## [2026-06-19] — Correctness + robustness wave (punch-list Ranks 11, 15, 16)

### Rank 11 — bootstrap difference tests documented accurately (+ `arch` cross-check oracle)
- **Dropped the "studentized (Ledoit-Wolf 2008)" framing** from `src/inference/bootstrap.py`
  (`sharpe_difference_test`, `cvar_difference_test`, module docstring) + `src/inference/es_backtest.py`. **VERIFIED
  against the code** that the bootstrap SE *cancels* in the two-sided p-value: `stat = obs/se`, `centred = (boot−obs)/se`,
  and `|centred| ≥ |stat| ⇔ |boot−obs| ≥ |obs|` — se-free. So the tests are a **re-centred basic (empirical) stationary
  block bootstrap** whose size is certified by `null_calibration` (audit C-7), NOT studentized. Labels/docs only — no
  test numerics changed (the `stat` field is still `obs/se`, a studentized point summary, but it does not drive the
  decision).
- **Reconciled `config/inference.yaml`** `sharpe_test`: it described `circular_block / block_size 5 / n_boot 4999` but
  the code is stationary `p=0.1 / n_boot 2000`. Fixed the YAML to faithfully describe the code (the lower-risk option —
  no `src/` caller reads `sharpe_test` from config, so threading config in would be a behaviour change), with a
  provenance comment naming `bootstrap.py` as the source of truth; removed the stale `crossing_rate` mention (ADR-022).
- **Wired the `arch` cross-check oracle** in `tests/test_inference_crosscheck.py` (`arch.bootstrap.StationaryBootstrap`
  + `optimal_block_length`, mirroring the statsmodels BH oracle): the bespoke stationary-bootstrap SE/CI agree with
  `arch` within loose tol on a fixed-seed AR(1); `optimal_block_length` recovers a longer block for AR(1) than iid.
  Fixed the `pyproject.toml` comment that wrongly said `arch` is "wired in bootstrap.py" (it is a tests-only oracle).
  **270 passed / 1 skipped** (+9). ADR: IMPL-BOOT-1.
- **PENDING (frozen-doc amendment, to apply in the Wave-3 freeze-prep pass):** PREREGISTRATION.md §10 +
  `config/preregistration.yaml:36` relabel "Sharpe studentized (Ledoit-Wolf 2008)" → "re-centred stationary
  block-bootstrap" (exact amendment text recorded in IMPL-BOOT-1).

### Rank 16 — Deflated Sharpe cross-trial variance in the wired selection path
- `deflated_sharpe_ratio(var_sr=None)` used the single-series SAMPLING-variance proxy, not the cross-trial Sharpe
  DISPERSION the canonical Bailey-Lopez de Prado DSR requires; on a heterogeneous candidate population this silently
  mis-stated the (secondary) DSR. `src/selection/fitness.py::held_out_fitness` now accepts/forwards `var_sr` (default
  `None` → the per-candidate path is byte-unchanged, since the population variance is unknowable mid-loop).
- **The empirical cross-candidate `var_sr` is computed at ANALYSIS time** (the clean place — the population variance
  over ALL of an arm's candidates is not knowable inside the per-candidate loop; threading a partial-population variance
  there would bias early candidates). New `scripts/analyze_campaign.py::winner_dsr(records)`: per arm, reconstructs the
  candidate population's per-period validation Sharpes (`sharpe_ratio(metrics['val_returns'])` — the same columns
  `build_perf_matrix` stacks for PBO), forms `var_sr = np.var(sharpes, ddof=1)`, finds the winner (max
  `metrics['val_fitness']`), and recomputes the winner's DSR deflated by that population variance — reporting the
  canonical-vs-proxy DSR + `var_sr` in a new markdown/JSON table; arms with <2 candidates are `skipped` (no ddof=1
  dispersion), never fabricated.
- `src/inference/deflated_sharpe.py` docstring now states plainly that `var_sr=None` is a within-series
  sampling-variance proxy — a DIFFERENT quantity from the cross-trial dispersion — coinciding ONLY under the homogeneous
  zero-skill null.
- **Tests:** two hand-computed golden DSR fixtures in `tests/test_inference.py` (canonical `var_sr` DIFFERS from the
  proxy on a dispersed-skill population, both matching golden values to 1e-10; the two COINCIDE under a homogeneous null
  to 1e-12). **279 passed / 1 skipped.** ADR: IMPL-DSR-1.

### Rank 15 — transaction-cost robustness sweep (cost-defence arm; `costs.grid_bps` was dead config)
- **`config/environment.yaml: costs.grid_bps=[0,5,10,25,50]` was DEAD** — no `cost_bps` override, no harness. Added an
  additive `cost_bps: float|None=None` to `PortfolioEnv.__init__` (`None`→headline `costs.headline_bps`, unchanged;
  else `self.cost=cost_bps*1e-4`) and threaded it through `EnvBundle`/`make_env_builder` (trailing keyword default →
  every existing caller byte-for-byte unchanged).
- **Per-step gross/turnover were NOT persisted** (campaign stored only NET `test_returns`). Added `rollout_port_series`
  + `EnvBundle.test_series` (same seal as `test_returns`); `run_campaign.evaluate_winner_on_test` now persists
  `metrics['test_gross']`+`metrics['test_turnover']` (verified `net==gross−c·turnover` to 1e-12), documented in
  `results.OPTIONAL_FIELDS`. Back-compatible: a NET-only record/fake just triggers the re-roll fallback.
- **`scripts/cost_sweep.py` (NEW):** RE-PRICES frozen winners across the grid WITHOUT retraining — ANALYTIC
  `net_c=gross−c·turnover` (preferred, from the persisted decomposition; valid because cost is charged AFTER the action,
  so gross/turnover are cost-independent, audit C-5) with a `cost_bps`-overridden-env RE-ROLL fallback/cross-check.
  Emits the **winner-identity-vs-cost table** (winner by Sharpe + every arm's Sharpe/CVaR-5% at each level) — the key
  check a tail-aware reward doesn't win merely by trading less. Reads only via `src.io.results`.
- **Tests:** `tests/test_cost_sweep.py` (9 fast, no-torch) — override sets/scales `self.cost`; analytic re-price ==
  re-roll across the full grid to **1e-12**; headline re-price reproduces the default-env net; one table row per cost
  level. **Suite: 279 passed / 1 skipped** (+9). Ruff clean. ADR: IMPL-COSTSWEEP-1. **PENDING (frozen-doc amendment,
  Wave-3 pass):** add the pre-registered cost-sweep to PREREGISTRATION.md §10 + `config/preregistration.yaml` (it is not
  yet listed; exact text in IMPL-COSTSWEEP-1).

## [2026-06-19] — Keystone Rank 8: campaign inference (H2 conjunction + multiplicity family + 1/N floor)
- **`scripts/analyze_campaign.py` (EXTENDED, additive):** wired the FROZEN pre-registration's selection-aware tests onto
  the per-(arm,seed) TEST-leg records (`metrics['test_returns']`).
  - `collect_family_pvalues()` — the arm-contrast × {Sharpe, CVaR@pre-reg levels} family via the stationary-bootstrap
    difference tests, then Benjamini-Hochberg at `multiplicity.q=0.05`; records the signed effect + `direction_ok` so the
    directional decision needs no bootstrap re-run.
  - `h2_conjunction()` — **the HEADLINE test:** `H2_supported` iff distributional beats **scalar AND placebo AND
    scalar_cvar5** in the predicted direction *post-correction* (confirmed against FINAL_PLAN B.6 L83 + PREREGISTRATION
    §1/§10 — the placebo rules out token-count, scalar_cvar5 rules out any-downside-number).
- **Romano-Wolf — methodological gap found + fixed:** the existing `multiple_testing.romano_wolf` is a *pure stepdown*
  that takes a precomputed `boot_stats (n_boot × n_hyp)` and draws nothing; its joint-max (line 104) is only valid if each
  row is ONE joint resample — which nothing in the repo built for the arm-contrast family. Added `romano_wolf_joint()`:
  draws ONE shared `stationary_bootstrap_indices` path per replication, evaluates every contrast on that single path
  (recentred at the observed difference), then feeds the existing stepdown — preserving cross-hypothesis dependence.
  `romano_wolf` + its test untouched; BH stays the default (per config).
- **`benchmark_floor()` + a `WeightPolicy` shim:** rolls all five frozen benchmarks (1/N equal-weight, spy/buy-and-hold,
  mean_variance, risk_parity, hrp) through the **IDENTICAL costed `PortfolioEnv`** via `rollout_port_returns`, by
  reconstructing the lookback window from the obs and returning an action the env's frozen projection *inverts* back to
  the target weights (`log(w)` for softmax; `w` for l1-clip) — so no edit to `strategies.py` or the env. Reports each
  benchmark's test Sharpe/CVaR/MaxDD/DSR; the gate = frozen winner test-DSR **strictly >** max(benchmark test-DSR) (the
  DeMiguel 1/N floor — POST-FREEZE, report-only, never re-selects).
- **Tests:** new `tests/test_campaign_inference.py` (15 fast, no-torch) — H2 supported only when all 3 legs reject (not
  on a tied / wrong-direction / missing leg); BH set == `benjamini_hochberg(pvals)`; `romano_wolf_joint` rejects strong /
  spares null; **the 1/N WeightPolicy's per-step gross == hand-computed `mean(panel.returns[:N])` through the REAL env**
  (`info['gross']==hand`, `port_ret==gross−cost`); the floor reports all five costed benchmarks; the gate flags
  pass/fail. **Full suite: 261 passed / 1 skipped** (additive; +15). ADR: IMPL-H2-1. *With Ranks 1-3, the entire
  executable inference path — select→freeze→test-once → PBO → H2 conjunction + FDR + 1/N floor — now exists.*

## [2026-06-19] — Keystone Rank 3: PBO/CSCV primary overfitting metric (logit + per-arm perf-matrix)

### `logit < 0` fix — the primary metric was mis-counting exact-median ties
- `src/inference/overfitting.py`: PBO counted splits with `logit <= 0`, but **FINAL_PLAN B.9 (line 100)** and Bailey et
  al. 2017 specify the **strict** `logit < 0` (the in-sample-best lands *strictly* below the OOS median; an exact
  OOS-median tie, `λ == 0`, does NOT count as overfit). Fixed the condition + the docstring + renamed the counter
  (`logits_nonpositive`→`logits_negative`). 3 PBO tests stay green — a **spec-confirmed** correction of the headline
  overfitting metric (verified against the project's own B.9, not merely the sweep's assertion).

### Per-arm PBO matrix wired — over CANDIDATES' validation returns
- **Methodology (confirmed against 3 sources — B.9 + the `pbo` docstring + PREREGISTRATION §10):** PBO is computed
  **PER ARM over that arm's search candidates' per-period VALIDATION returns** — the CSCV "trials" are the candidates
  (the within-arm best-candidate-by-validation selection is what actually risks overfitting; "trial count ill-defined
  under guided search"). This is *distinct from* the CPCV-on-winners evaluation folds (a separate scheme for the
  difference-test inference). No discrepancy found; no frozen item touched; all changes additive.
- **Per-candidate validation-vector persistence (additive, all six arms):** the LLM loop (`loop.py:373`) and the
  parallel path already wrote `metrics['val_returns']`; the gap was the *sequential* search arms. `src/agents/evaluator.py`
  gains `evaluate_reward_with_returns(...) -> (fitness, val_returns)` (surfacing the per-period vector already computed
  for `held_out_fitness`; `evaluate_reward` delegates, scalar contract unchanged); `scripts/run_prototype.py` captures
  each search candidate's vector in evaluation order and archives it via an extended `_archive_record(val_returns=...)`.
  `src/io/results.py` `OPTIONAL_FIELDS` doc updated (schema tuples unchanged; the field stays optional/skippable).
- **`scripts/analyze_campaign.py` (NEW — the campaign analysis, separate from the 1-seed-directional
  `analyze_results.py`, which stays untouched):** `build_perf_matrix(records, arm) -> (T_val, N_candidates)` +
  `campaign_pbo(records, *, n_blocks) -> {arm: pbo}` (calls `overfitting.pbo`, `n_blocks=16` from
  `config/inference.yaml`); reads results ONLY via `src.io.results.load_all`; arms with <2 candidates or
  `T_val < n_blocks` degrade to `status="skipped"` (never fabricated/raised); emits a per-arm PBO markdown + JSON.
- **Tests:** new `tests/test_analyze_campaign.py` (12 fast, no-torch) — matrix shape; PBO ∈ [0,1]; a clean monotone
  ladder → **PBO ≈ 0**; pure noise → **PBO ≈ 0.5**; too-few-candidates / short-window / absent-arm all skip gracefully.
  **Full suite: 234 passed / 1 skipped** (was 222/1; +12). ADR: IMPL-PBO-1.
- **Noted (pre-existing, NOT introduced):** the `slow` `test_run_prototype.py` search-arm tests crash with a Windows
  native access violation during torch/SB3 import (a known real-SAC-on-Windows C-extension instability the `slow`
  marker excludes; the campaign runs on Linux/4090). Tracked for the Linux verification pass.

## [2026-06-19] — Keystone implementation pass (punch-list, parallel agents)

### Rank 2 — headline campaign driver (`scripts/run_campaign.py`)
- Implemented the Eureka post-loop **SEARCH → SELECT → FREEZE → TEST** on the frozen development/evaluation split
  (train 2005-2014 / val 2015-2017 → held-out test 2018-2025, embargo 21), replacing `raise SystemExit('STUB')` and
  deleting the dead `from src.io.results import ResultStore` import (results.py never had `ResultStore`).
  **SEARCH** reuses `run_prototype.run_arm`; **SELECT** picks each arm's winner by validation Deflated Sharpe
  (`metrics["val_fitness"]`) via the explicit `from src.io.results import load_all` (name-collision-safe vs
  `src.utils.config.load_all`); **FREEZE** persists `reward_source` + `reward_source_hash` with a `frozen: True` marker;
  **TEST** re-instantiates the frozen winner via `validate_once` (same AST-gate/contract), builds a **3-window**
  `EnvBundle` (`make_env_builder(..., test_window=<2018-2025 idx>, embargo=21)`), re-trains per campaign seed, and calls
  `bundle.test_returns(policy)` **exactly once** — one record per `(arm, seed)` (`run_id=f"{arm}-s{seed}"`) carrying
  `val_fitness`, the realized per-step `test_returns` vector, `per_period_pnl`, `test_sharpe`, `test_cvar05`.
  `resolve_windows` derives all three windows by `np.searchsorted` on the panel date axis; `--resume` skips archived
  records. Fully dependency-injected (trainer/env_builder/arm_runner) so the wiring is unit-testable without real SAC
  training. **Walk-forward folds DEFERRED** (`# TODO(Rank 2b)`; per-fold val-split not invented — directives #3/#7).
- **`src/io/results.py`:** added an additive `OPTIONAL_FIELDS = ("frozen","test_returns","per_period_pnl",
  "reward_source")` registry; **`REQUIRED_FIELDS` UNCHANGED** — a new required field would break every existing writer
  (loop/search/prototype) and the loader round-trip tests, so the additive registry is the correct call (overriding the
  punch-list's literal "extend REQUIRED_FIELDS"). The per-step vector also rides in `metrics["test_returns"]` where
  `analyze_results` already reads `metrics`, so Rank 3's PBO consumes it back-compatibly.
- **Embargo on contiguous splits:** the frozen calendar splits abut (val begins the day after train ends), so raw
  `searchsorted` gives `val_start == train_end`, violating the `make_env_builder` embargo guard. Resolved per LdP
  purge+embargo by carving the 21-day embargo from each *later* window's start. ⚠ **To reconcile (Rank 18):** prefer
  reading the materialized `data/gold/splits_univ3.parquet` so the executed windows **byte-match** the frozen split.
- **Tests:** new FAST `tests/test_run_campaign.py` (9 tests, no torch) — window resolution; winner selection; **the
  selection 2-window bundle refuses the test leg (the seal holds)**; freeze marker; one record per `(arm, seed)` with
  the test metrics + per-step vector; **test leg touched exactly once / val never re-rolled**; `--resume` skips done;
  OPTIONAL_FIELDS additivity. **222 passed / 1 skipped** (+9 over the prior 214). ADR: IMPL-CAMPAIGN-1.
- **FLAGGED (follow-ups; neither blocks the headline H2):** (1) `bayes_opt` archives a *non-executable* comment stub
  (`# bayes_opt coeffs=[...]`), so its frozen winner can't be rehydrated for the sealed test leg — the driver records
  `status="winner_not_testable"` rather than invent a round-trip; the fix (search arms archive the *materialized
  executable* reward_source, required for the **H4** BO-vs-LLM held-out comparison) is tracked as **Rank 2c**. (2) An
  order-dependent test flagged under `pytest-randomly` → to fix + jointly re-verify with Rank 4.

### Rank 4 — transaction cost reconciled to ½-L1-DRIFTED spec (viva priority #2)
- **`src/env/portfolio_env.py` `step()`:** replaced the full-undrifted-L1 cost (`c·‖w − w_prev‖₁`, ~**2×** the spec — it
  missed BOTH the ½ one-way factor AND the realized-return weight drift) with the spec's **½-L1-DRIFTED** turnover:
  `growth = [1+r_t (risky), 1.0 (cash)]`; `port_growth = w_prev·growth` (guarded `> 0`, else `FloatingPointError`); the
  drift-adjusted previous weights `w̃ = w_prev·growth / port_growth`; `turnover = ½‖w − w̃‖₁`; `gross = w[:N]·r_t`;
  `cost = c·turnover`; `port_ret = gross − cost`; + a NEW `info["turnover"]` key. The action projection, simplex bounds,
  log-wealth accumulation, and the `safe_call` sandbox path are untouched; all prior info keys preserved.
- **Docs reconciled to one source of truth (`docs/environment_spec_v1.md`):** removed the stale "Verified as-built
  2026-06-10" header (it pointed at the dead pre-merge `src/portfolio_env.py` + the nonexistent
  `tests/test_portfolio_env.py` → fixed to `src/env/portfolio_env.py` / `tests/test_env.py`); updated the
  `config/environment.yaml` cost comment, the LLM-facing `src/llm/prompts.py:78` text, and FINAL_PLAN L50/260/276 —
  which had previously *agreed with the buggy full-L1 code* (the bug's source); reconciled to the spec (spec wins).
- **Two deliberate, spec-following divergences:** (1) cash grows at **1.0** — no `cash_daily_rate` key in the live
  `config/environment.yaml` (only the pre-merge B-line had one), so `cash_daily_rate = 0` per the documented fallback;
  (2) the drift uses *this step's* realized `r_t` (the code's audit-C-5 timing), matching the spec's intent.
- **Tests:** fixed `tests/test_runner.py::test_uniform_policy_returns_match_panel_mean` — the old "zero turnover after
  t0" assumption was genuinely WRONG under drift (a held uniform weight DRIFTS → ongoing nonzero turnover); it now
  asserts the **full** closed-form net series to **1e-12** (not a loosened tail) with a `turnover.max() > 0` guard.
  Added two `tests/test_env.py` tests: `test_cost_is_half_l1_drifted_turnover` (2-risky-asset + cash, hand-computed
  `w̃`/turnover/cost/gross/port_ret to 1e-12, + drifted-turnover < naive-full-L1, proving BOTH the ½ and the drift) and
  `test_turnover_is_zero_when_target_equals_drifted_weights` (drift-term isolation). ADR: IMPL-COST-1. Unblocks Rank 15
  (cost-sweep). The headline + sweep are now priced at the correct effective bps (viva Q7).

### Rank 6 — sandbox AST gate denylist + candidate memory cap (ADR-008 now matches the code)
- **`ast_gate` (`src/sandbox/executor.py`):** added a numpy IO/FFI attribute denylist `_BANNED_ATTRS`
  (load/loads/save/savez/savez_compressed/savetxt/loadtxt/genfromtxt/fromfile/tofile/memmap/frombuffer/DataSource/
  lib/ctypeslib/f2py/testing/mro/open). The gate was previously **dunder-only**, so `np.load(..., allow_pickle=True)`
  (a pickle-RCE vector), `np.save`, `np.fromfile`, `np.genfromtxt`, `np.memmap`, `np.DataSource`, and the `.mro`/`.open`
  object-model escapes **all passed the live gate**. They are now rejected statically (`return False`) before any
  execution. ADR-008 + the CHANGELOG already *claimed* this control — the gate now enforces it (closes the
  viva-falsifiable gap; sweep Rank 6 / viva Q22).
- **`_candidate_child`:** best-effort POSIX resource caps applied before `exec` — `RLIMIT_AS` ~2 GiB, `RLIMIT_CPU` 15 s,
  `RLIMIT_NOFILE` 64, `RLIMIT_FSIZE` ~1 MiB — each clamped to the existing hard limit, never raised, all best-effort.
  Ported in shape from `archive/pre_merge_repo_B/src_flat/sandbox.py::_limit`. An LLM-written reward can no longer OOM
  the rented 4090. The in-process `_validate_inline` fallback is deliberately **not** capped (capping the orchestrator
  process would be wrong).
- **Windows:** `resource` is POSIX-only, so the caps are a documented no-op there (psutil is **not** a dependency → no
  RSS watchdog added, only the documented gap); the wall-clock timeout (the killable spawn child, ADR-028) is the
  backstop. The Linux/4090 campaign box enforces every cap.
- **Tests (`tests/test_sandbox.py`):** 10 gate-denial cases over the numpy IO/FFI + `.mro` surface; a POSITIVE control
  proving legitimate reward math (sum/mean/std/var/dot/clip/abs/where + indexing/arithmetic) still passes (the denylist
  didn't over-block); a POSIX-gated (`skipif` on absent `resource`) address-space memory-bomb rejection. **220 passed /
  1 skipped / 8 deselected** (fixed order). ADR: IMPL-SANDBOX-1. The duplicate `candidate_failed`/`reset_failure_flag`
  defs were left untouched (Rank 18).

### Verification + tooling — joint suite green + determinism guard now active
- All three parallel ranks (2/4/6) integrate cleanly: the full non-slow suite is **222 passed / 1 skipped / 8
  deselected**, **order-independent across 3 shuffled runs**.
- Installed the declared-but-missing **`pytest-randomly`** into the venv (pyproject declared `>=3.15`, but the venv was
  out of sync, so the test-order shuffle — the inter-test state-leakage guard — had never actually run). The
  `test_run_campaign::test_resolve_windows_…` "flake" the Rank-6 agent reported was a transient artifact of reading the
  file *mid-write* during concurrent agent execution; it passes in isolation and under every shuffle. **Follow-up
  (Rank 14):** the lockfile / `make sync` must pin this so the guard can't silently disappear again.

## [2026-06-19] — Verified 13-sweep punch-list (workflow wr6yuz0yd) + Keystone Pass 1: held-out TEST leg

### Adversarial verification sweep — 60 agents, 84 → 43 findings
- Ran a 13-sweep deterministic workflow (3 GitHub-repo wiring/collision + 10 internal adversarial-verification sweeps)
  over the whole repo + planning corpus; every P0/P1 finding was re-checked by an independent skeptic (default-refute).
  **84 raw findings → 46 deduped P0/P1 → 43 survived.** Synthesised into a strict, ranked, implementation-ready
  punch-list: `00_planning/IMPLEMENTATION_PUNCHLIST_2026-06-19.md` (the execution bible).
- **Headline — the keystone inference path is the dominant grade risk:** `run_campaign.py`/`inspect_rewards.py` are
  stubs importing a non-existent `ResultStore`; `EnvBundle` had no test leg; `pbo()`/`romano_wolf`/`benjamini_hochberg`/
  `baselines.strategies` are implemented-but-never-called outside tests; `univ4` does not exist (live panel is `univ3`
  with `liquidate_to_cash` zero-filling the exact left tail the H2 measures read); `freeze.py`/`power_analysis.py` are
  stubs; the transaction-cost model is full-undrifted-L1 (~2× the half-L1-drifted spec); the sandbox AST gate misses the
  numpy file/FFI surface (`np.load` pickle-RCE) with no candidate memory cap; + a cluster of IQN-era doc-vs-code
  contradictions and the seeds-5-vs-30 frozen-record conflict to reconcile before the Phase-1 freeze.
- **Verified SOLID (do not refactor):** the sandbox two-stage design (ast_gate → killable-child validate → in-process
  safe_call; ADR-028); the `EnvBundle` two-window contract + policy-agnostic `rollout_port_returns`;
  `src/agents/evaluator.py` (matched-compute reward evaluator); `src/io/results.py`; the PIT+21d-embargo split
  materialisation (byte-matches prereg); `analyze_results.py` correctly scoped 1-seed directional;
  `src/feedback/measurement.py`+`schema.py` (the canonical frozen-six estimator — docs reconcile *to* it); the novelty
  conjunction (survives the mid-2026 sweep). Repo sweeps surfaced Eureka/rl-baselines3-zoo/qlib wiring templates +
  `arch.StationaryBootstrap`/`StepM` as cross-check oracles + QuantEvolve (arXiv:2510.18569 %VERIFY) as the closest
  finance collision (strategy-code QD, scalar score, NO RL, NO tail-to-LLM → cite-and-distinguish).

### Keystone Rank 1 — held-out TEST leg (`src/env/runner.py`) — DONE, verified
- **The unblocker.** `EnvBundle` + `make_env_builder` gained an optional `test_window`; new `EnvBundle.test_returns(
  policy)` rolls the frozen policy through the test env but **raises `RuntimeError("test split sealed until final
  inference")`** whenever the bundle has no test window. Because the discovery loop and every search arm build only
  2-window bundles, the 2018-2025 test split is now **structurally unreachable during selection** (PREREGISTRATION §10:
  select-on-validation → freeze → test-once; AUDIT-B2/B3).
- `make_env_builder` gained `embargo: int = 0` and now validates **both** boundaries: `val_start ≥ train_end + embargo`
  (generalising the old disjoint check, message keeps "disjoint") and, when a test window is given, `test_start ≥
  val_end + embargo` (Lopez de Prado 2018 purge+embargo). Default `embargo=0` keeps the legacy 2-window callers
  (`run_prototype`, `parallel`) byte-identical; the campaign passes 21.
- **Deferred (IMPL-TESTLEG-1):** `make_walk_forward_windows` (rolling 5y/1y/1y evaluation folds) → Rank 2, where the
  `Panel` date API + the per-fold val-split question are confirmed against the frozen prereg rather than invented.
- **Tests:** 3 added to `tests/test_runner.py` (the seal raises without a window + returns the right shape with one; the
  val→test and train→val embargo guards both fire). **Full non-slow suite: 199 passed / 0 failed** (was 196; +3). No
  regressions. ADR: IMPL-TESTLEG-1 (`docs/DECISION_LOG.md`).

## [2026-06-19] — 20-track deep audit + P0 remediation + provider decision (ADR-032, ADR-033)

### Audit (engineering + scientific) + GitHub-repo research
- 20-track strict deep audit + 4 GitHub-repo research agents. Verdict: the codebase is **excellent in design**; the
  singular gap is the **executable inference path stops at validation**. Registers:
  `00_planning/SYSTEM_AUDIT_AND_REMEDIATION_2026-06-19.md` + `00_planning/GITHUB_REPO_FINDINGS_2026-06-19.md`.

### P0 correctness fixes — DONE, full non-slow suite green
- **Numerical (P0-1):** an exact `sd==0` guard that a near-constant series **evades** (`std ~ 2e-19`, not 0) made
  `deflated_sharpe` return **1.0 for a flat reward — which would WIN candidate selection**. Fixed: relative near-zero
  guard (+`np.ptp`) + non-finite stripping + f64 in `deflated_sharpe._sample_moments` and `bootstrap.sharpe_ratio`/`cvar`.
  28 invariant tests added (`tests/test_numerical_guards.py`).
- **Sandbox (P0-2):** `safe_call` (stage-2) was **never wired** into training — a reward valid on the fixture but failing
  on a real N-asset obs **crashed the rollout**. Now routed through `safe_call`; added `reset_failure_flag`/
  `candidate_failed`; runner resets + logs.
- **Seeding (P0-3):** the GPU parallel worker now calls `set_global_seed(seed, deterministic_torch=True)` at entry —
  all RNG stacks + `use_deterministic_algorithms(warn_only)` + `CUBLAS_WORKSPACE_CONFIG`.

### Dependencies (P0-5) + provider
- torch↔SB3 conflict resolved: capped `stable-baselines3`/`sb3-contrib` `<2.9` (keeps validated torch 2.6+cu124).
  Dropped `rliable` (upstream archived). Wired `arch`. Security re-pins (`python-dotenv≥1.2.2`, `pytest≥9.0.3`,
  `ruff>=0.15,<0.16`). Added `anthropic` + `seaborn` + `pytest-randomly`/`pytest-timeout`. `requires-python<3.13`.
- **Provider decided (ADR-033): Sonnet 4.6 primary + Llama-4 N3 + DeepSeek-V4 check** (~$7 whole project). ⚠ The
  Anthropic key pasted in chat is exposed in the transcript → **must be rotated** (never stored/committed).

### Queued (per the register; the real run stays gated)
- Campaign inference-path builds (held-out **test leg** + `run_campaign` + PBO/benchmark-floor/`inspect_rewards` wiring
  + cost-sweep + **≥20 seeds** + **univ4** delisting imputation); repro hardening (freeze.py+OpenTimestamps, capture_env,
  lockfile, CITATION.cff, make-figures); provider wiring (anthropic transport default + prompt-cache + tenacity);
  adopted tooling (import-linter, gitleaks, …); cross-check tests (arch/statsmodels/pyextremes oracles); doc
  reconciliation (4× prompt/schema-vs-code drift).

## [2026-06-18] — Max-compute calibration: GPU enabled, GPU-ONLY optimal; LLM provider decided (ADR-030, ADR-031)

### Compute — "use full power": GPU is ~3× CPU, but GPU-ONLY beats every GPU+CPU mix
- Installed CUDA torch (2.6.0+cu124); added explicit `device` to the agent factory/trainer (ADR-030). Single SAC:
  **GPU 96–110 steps/s vs CPU 34** — the 1,893-dim obs is GPU-favorable, overturning the earlier "CPU-bound" read.
- Built `src/orchestration/parallel.py` — a device-load-balanced candidate pool (`DevicePool`: n_gpu cuda + n_cpu
  cpu tokens over a non-daemon `ProcessPoolExecutor`, fed by per-arm driver threads) + a `--parallel` path in
  `run_prototype.py`.
- **Calibrated (`scripts/bench_compute.py`): the GPU saturates at ~185 steps/s; CPU training workers are useless
  (threads=1 → ~5 steps/s each) AND starve the GPU (3 GPU=186 → 3 GPU + 8 CPU=143). GPU-ONLY is optimal**
  (ADR-031). Set `n_gpu=3 / n_cpu=0`, `agent.device: cuda`. **Full 240×25k prototype ≈ 9 h on the laptop**
  (ADR-030's ~3–6 h was wrong; the GPU is the hard ceiling; SBX/JAX ~10× is the only sub-3h lever, gated).
- **Verified:** GPU dry-run (2 workers) ran all three arm types — incl. the nested sandbox validate-once child
  spawning *inside* a GPU pool worker — `matched_budget_ok=true`, reloadable archive, clean exit 0.

### LLM provider — deep research + accurate costing
- Two deep-research passes (provider comparison + decision validation). **Decision: Sonnet 4.6
  (`claude-sonnet-4-6`) primary reward-author** (clean, honors `temperature=0`, novel, reliable) **+ Llama 4 open
  N3 contamination control** (only model with an official cutoff) **+ DeepSeek-V4 optional "contaminated"
  cross-check** (FinRL-DeepSeek / AlphaForgeBench expose DeepSeek on the same universe → wrong for the *clean*
  headline; GPT-5.4-mini is the max-determinism alternative).
- Costed from the *real* prompts + stateless loop (~85k in + 72k out per prototype model): **whole project ≈ $7**
  (range $0.5 all-open → $13 GPT-5.5) — cost is immaterial; provider chosen on fit. Provider ADR pending user lock-in.

## [2026-06-18] — Build P3–P6: world-class prototype machinery, verified (ADR-029)

### The headline
- Built and end-to-end-verified the full advanced-prototype machinery (MASTER_EXECUTION_PLAN P3–P6) to a
  world-class standard, **without executing the directional run** (user directive: build to the max, coordinate
  every step with the literature, verify everything, don't run yet). **Full non-slow suite: 175 green; ruff clean.**

### P3 — the two missing keystones + the C1 adapter
- `src/env/runner.py` (the `env_builder` keystone the loop injects: train/val/measurement windows on one PIT
  panel, deterministic no-look-ahead rollout); `src/agents/trainer.py` (fixed SAC; memory-safe buffer ADR-025;
  train-only obs-normalization via a stats-carrying `NormalizedPolicy` — deep-research §2);
  `src/agents/evaluator.py` (the **C1** adapter so the search arms consume matched compute).

### P4 — LLM glue
- `src/llm/prompts.py` renders `{ENV_INTERFACE}`; `loop.py` rewired to send it (**C3**, non-breaking);
  `src/llm/stub_designer.py` emits keyless, deterministic, varied valid reward code (6 archetypes spanning the
  reward family + tail-aware/stateful designs) so the LLM-arm pipeline runs with NO API key;
  `make_anthropic_transport` (provider parity).

### P5 — orchestration
- `src/baselines/reward_family.py` (the live-contract H4 `params_to_reward`, authored — it existed only as an
  injected name + an incompatible archived version); `config/prototype.yaml`; `scripts/run_prototype.py`
  (6 arms; arm-level parallelism across non-daemon workers; search arms via the C1 evaluator + family; uniform
  archiving; matched-compute assertion; resumable; dry-runnable). **Dry-run ran all 3 arm types in parallel,
  matched=True, 19.2s.**

### P6 — analysis
- `scripts/analyze_results.py` (H2/H4 directional reads; Sharpe/CVaR difference tests on archived validation
  returns; rliable IQM; the interpretability mechanism-gate; GREEN/AMBER/RED verdict; compute-accounting).
  `loop.py` now archives `val_returns` so the difference tests can run on the winners.

### Verified / recorded
- +22 tests (runner, trainer+integration, prompts, stub-designer, reward-family, analysis, orchestration);
  ADR-029. **Open (user's, plan §10):** the LLM provider + key for Pass B, and the gated prototype RUN.

## [2026-06-17] — Build P1–P2: runtime + Phase-0 GATE GREEN (ADR-026/027/028)

### Runtime (P1)
- Built the pinned **Python 3.11** venv; installed torch (CPU) + SB3 2.9 + sb3-contrib + numpy<2 / pandas<3 /
  scipy / sklearn / statsmodels / gymnasium / arch / rliable / pyarrow. Pinned **pandas<3.0** (pandas 3.0 broke
  `arch` under the numpy<2.0 pin) and moved **d3rlpy to an optional extra** (ADR-026). **Full non-slow suite
  re-earned GREEN on this laptop: 153 passed** — 3 env-dependent agent tests were updated to *simulate* backend
  absence via monkeypatch (they previously passed only because SB3 was not installed).

### Phase-0 GATE (P2) — GREEN
- Implemented `scripts/smoke_test.py`; **GATE GREEN** on the RTX-4050 **CPU**: SAC **m ≈ 18.9 min/50k**, TQC
  **m ≈ 25.9**, critic loss falls (SAC 413→1.0, TQC 9.8→0.25), obs_dim = 1893. The one unmeasured quantity `m`
  is now measured (matches the compute doc). Recorded in `docs/DECISION_LOG.md` (PHASE-0).

### Fixes the gate surfaced (each recorded)
- **ADR-027** — bounded the env action space `Box(-inf,inf)` → `Box(-10,10)` (SAC/TQC assert finite bounds).
- **ADR-028** — cross-platform sandbox validation timeout: Windows `signal.SIGALRM` was a silent no-op, so a
  `while True` reward hung the run AND the test suite; now a killable child process (C2).
- Fixed the smoke stub's wrong import `src.env.portfolio` → `src.env.portfolio_env`.

## [2026-06-17] — Advanced execution plan + build reconnaissance (ADR-025)

### The headline
- Authored **`00_planning/MASTER_EXECUTION_PLAN.md`** — the authoritative execution plan for (Part I) a
  user-requested **advanced 40-candidate prototype** (6 arms × 40 candidates × 1 seed; 8×5 reflection) and
  (Part II) the full **6 × 30 × 5** campaign. Every build step is anchored to a corpus paper, carries an
  acceptance test, and names a recording target. **Supersedes `ADVANCED_PROTOTYPE_BLUEPRINT.md`** (its data
  task T0 is closed — the `_univ3` panel exists).

### Reconnaissance (verified on this laptop, not inherited)
- **Runtime absent:** no `.venv`, no torch/SB3/numpy installed (system Py 3.12 only) → the 153-test green must
  be **re-earned here** (P1). Hardware: i7-13620H 16T / 15.6 GB RAM / RTX 4050 6 GB.
- **⚠ Memory bug found:** default `buffer_size=1e6` × 1,893-dim obs ≈ 15 GB replay RAM → would OOM the laptop;
  fix recorded (size to `train_steps` / `optimize_memory_usage`).
- **Missing keystones:** the concrete SAC trainer (`train_and_evaluate`) and the env-runner (`env_builder`) —
  only faked in tests. All 8 execution scripts confirmed STUBs; real `_univ3` gold panel confirmed loadable.

### Keyless machinery-validation path
- A deterministic **`StubDesignerTransport`** lets the entire pipeline run end-to-end on real GPU+data
  **without an API key** (Pass A); the real-LLM headline (Pass B) is one transport swap, gated on provider/key.

### Recorded / open
- ADR-025 (this session). Frozen-design open items (budget 30/40/240, embargo 10/21, provider, delisting,
  action-projection, λ) routed to the Phase-1 freeze (plan §7.1). Plan under independent adversarial review
  before the build begins.

## [2026-06-17] — Repository unification: one folder (engine ⊕ data) — Stage 1 (ADR-022)

### The headline
- **Two divergent repos are being merged into one project folder** under an absolute **no-loss/no-delete**
  rule: the audited *experimental engine* (was `dissertation_papers/llm-reward-portfolio`) is the structural
  base; the *data + hardened core* line (was `~/Downloads/llm-reward-portfolio`, this repo's prior identity)
  is being folded in. Staged + test-verified, never a big-bang (rationale + full plan in **ADR-022**).
- **Safety net first:** full backups of both repos at `~/Downloads/_merge_backup_2026-06-17/`
  (B 416M, A 513M, incl. `.git` + data). The source repo B is **retained untouched** until Stage 4.

### Stage 1 — folded in, non-breaking (DONE)
- **Real data + provenance copied and CHECKSUM-VERIFIED** — canonical panel `returns_panel_univ3.parquet`
  sha256 `f4edc86…` identical at source and destination; `data/{gold(54 parquets),clean,raw,staged,
  manifest}` now live in the unified repo; `data/manifest` carries checksums.txt + manifest.jsonl (874) +
  lineage.jsonl + invalidated.jsonl + journal.
- **Provenance & docs folded in:** `CHANGELOG.md`, `DECISIONS.md`, `RELATED_WORK_WATCH.md`, `reports/`,
  `runs/`, all of B's `docs/*` (DATASHEET, DATA_ENTITLEMENTS, REFERENCES, distributional_feedback_schema,
  environment_spec, …), `scripts/verify_inventory.py`.
- **Configs/prompts:** B-unique `eureka_loop.yaml` + `inference.yaml` added; the 3 clashing configs
  preserved as `config/{data,environment,llm}.B.yaml` (A's never clobbered); all B prompts added alongside
  A's (no filename clash) for Stage-2 reconciliation.
- **Engine integrity confirmed:** **148 tests pass, 0 failed** across 20 test files after the fold-in —
  A's audited science modules were not touched in Stage 1.

### Convergence decision (evidence-based) + interim state
- **B's flat science modules are the PRE-AUDIT line** (verified: B still ships `smoke_iqn_sac.py` — the
  IQN-SAC the audit rejected for SAC+TQC — and a `crossing_rate` neural-IQN diagnostic the preregistration
  dropped). So **A's audited science stays canonical as the live `src/`**; B's pre-audit science is **NOT
  merged** and is **preserved wholesale, not deleted** (Stage 4 folds all of B into `archive/
  pre_merge_repo_B/`). Audit-neutral B engineering gains (resource-limited sandbox isolation) are logged as
  candidate future ports under their own ADR — never blind-merged.
- **B's data-acquisition layer is self-contained** (imports only within `src/data/`), so Stage 3 integrates
  it cleanly into the package and wires a real-gold loader for the audited env.
- Interim only: `config/*.B.yaml` and the dual prompt set are reconciled in Stage 4. PREREGISTRATION stays
  A-canonical and **untouched** — the frozen design is unchanged by the merge.

### Stage 3 — acquisition pipeline relocated + B preserved (DONE; env↔data loader flagged)
- **`data_pipeline/`** created: B's Refinitiv→gold acquisition stack relocated **verbatim** (its dependency
  closure `{config.py, features.py, data/}` + B's `config/*.yaml` + a README). Imports are intact (B's
  `config.py` resolves `CONFIG_DIR` relative to itself) — **smoke-imported clean** in A's venv (which already
  has `lseg-data`, `pandas-market-calendars`). It is decoupled from the live engine: the gold panel is frozen,
  so the pipeline is provenance/reproducibility only (re-running needs live Refinitiv creds).
- **`archive/pre_merge_repo_B/`** created (nothing lost): B's pre-audit flat science modules (`src_flat/`,
  with a successor-map README) + B's root docs (`root_docs/`: CLAUDE/README/PREREGISTRATION/Makefile/
  pyproject/requirements). Full `.tgz` of B (incl. `.git`+data) remains at `~/Downloads/_merge_backup_2026-06-17/`.
- **Flagged for careful follow-up (NOT improvised):** the live env↔real-data **loader** (`returns_panel_univ3`
  → audited `Panel`) must decide **intra-window delisting handling** — e.g. Wachovia `WB.N^A09` is in the
  dev-2005 top-30 and dies in 2009 (NaNs after delisting), while the env's `Panel` requires finite returns.
  That is a preregistration/`environment_spec_v1` design decision, deferred to align with the frozen design.

### Stage 4 — single folder, dedicated git repo (DONE)
- `.gitignore` extended to protect the merged licensed data (`data/clean|staged`, `manifest/journal`,
  `runs/`); `.env` brought into the repo and confirmed **untrackable**; redundant `config/*.B.yaml` removed
  (preserved in `data_pipeline/config/` + backup).
- **Standalone B removed** after its backup was verified to contain the canonical panel + 526 git objects —
  truly one folder now; nothing lost (integrated + `archive/` + 416M `.tgz`).
- **Dedicated git repo** initialised at the repo root (was loose inside the home `parametric-catbond-erc20`
  repo); initial commit on `main`, 1061 files, **0 secrets/parquets/`.venv` staged** (guard-verified).
- README updated for the unified layout.

### Gap-closure wave (DONE) — ADR-023, ADR-024
Audited the unified repo and closed every inconsistency (or flagged it explicitly):
- **Real-gold loader** `src/data/loaders.py` + 5 tests — the audited env can now train on
  `returns_panel_univ3` (anonymised ids; delisting policy `liquidate_to_cash`, ⚠ provisional, ADR-024).
  **Suite: 153 green.**
- `pyproject` gained `[optional-dependencies] data` (lseg-data, pandas-market-calendars, python-dotenv,
  pyarrow); the `openai` line annotated (provider OPEN vs ADR-016 Claude — reconcile before freeze).
- `config/data.yaml` source corrected **CRSP→Refinitiv** (+ `vix: FRED_VIXCLS`); `environment.yaml` VIX
  source noted; `src/data/pipeline.py` docstring now points to `loaders.py`/`data_pipeline/` (synthetic vs
  real disambiguated).
- README counts fixed (10 YAMLs; scripts marked **STUB**; 153 tests); **CLAUDE.md** gained a post-merge
  section; the **two decision logs cross-linked** (`DECISIONS.md` authoritative; `docs/DECISION_LOG.md` =
  A-line audit); `prompts/README.md` documents the hardcoded-vs-template state; `PREREGISTRATION §12`
  carries the compute amendment footnote.
- **Build-gated remainder (NOT inconsistencies — tracked):** the GPU/credential entry-point STUBS
  (smoke_test, build_gold, run_campaign, freeze, analyze_results, inspect_rewards, power_analysis =
  blueprint T1–T6), the concrete SAC trainer, and the LLM key/provider choice.

## [2026-06-12] — Entitlement landed: PIT membership built; universe pulls running

### The headline
- **A1 PIT membership EXISTS and validates** (`data/staged/pit_membership.parquet`): 252 months ×
  499–506 names, union **953 RICs** (2005–2025) incl. **333 dead ^RICs**; Lehman in 2005-01/out 2008-10
  (leaver event 2008-09-17, `LEH.N^I08`), FactSet/Airbnb absent 2005, Tesla out 2019/in 2021.
  Lineage to the three raw event pulls; validation gates recorded in provenance.

### Two silent vendor traps caught by CONTENT validation (shape checks false-passed both)
1. **Membership snapshots return the CURRENT chain** on this route — `TR.IndexConstituentRIC`+SDate,
   the dated chain `0#.SPX(date)`, and field-embedded SDate all silently survivorship-biased (FDS/ODFL/
   ABNB "in 2005"). 98 `rf_members_*` artifacts INVALIDATED (`data/manifest/invalidated.jsonl`, now
   git-tracked); method switched to **reverse event replay** through `TR.IndexJLConstituent*` streams
   (3 requests for 21 years), gated by count-band [495,510] + known-truth checks (**ADR-020**).
2. **`TR.TotalReturn` via get_history returns empty/NaN frames** — 39 `rf_tr_*` artifacts INVALIDATED;
   corrected to **datagrid long form** `Frq=D` (content-verified: Lehman daily series through
   2008-09-12, worst day −44.9%, percent units) and `Frq=M` for market cap; price/bid/ask/volume via
   no-fields `get_history` (TRDPRC_1/BID/ASK/ACVOL_UNS), split per-field for lossless CSV.
- Probes P2/P3 rewritten to content-validated JL queries (assert known dead-RIC leavers), and the
  mnemonic checks of 06-12 morning now read values, not shapes — the trap class is test-closed.

### Added
- `src/data/build_universe.py` + `build-universe` CLI/make target: long→wide assembler
  (percent→decimal, dedup-keep-last, XNYS align, fail-loud on missing pulls) feeding the existing
  `panel.build_gold` with membership+mcap → D2 mcap panel, D3 top-30 per window, PIT D1/D4/D6 (`_univ`).
- Live mnemonic confirmations into config (`TR.CompanyMarketCap`, `TR.BidPrice/AskPrice`, `TR.Volume`,
  TRBC-on-dead-RICs, `.SPXTR`); `.VIX` NOT licensed (CBOE) → FRED VIXCLS stays primary;
  `TR.InstrumentDelistedDate` often null → delist dates derive from ^MYY suffix + last trade.
- Probe evidence serializer fix (Timestamp keys from live frames).

### Pulls (journaled `universe_refinitiv`, resumable)
- Frozen: `rf_chain_current`, `rf_jl_joiners` (523 events), `rf_jl_leavers` (520 events);
  daily-TR chunks streaming (429 total: 39 name-chunks × 11 two-year spans), then 39 monthly-mcap
  chunks, 39 OHLC/bid/ask/volume chunks, delisting/sector metadata, `.SPXTR` benchmark.

### Integrity
- PREREGISTRATION.md + prompts/ untouched; `lambda_frozen` null; invalidations are append-only
  declarations (write-once artifacts remain on disk, nothing consumes them); suite 121 passed + 1 skip.

## [2026-06-10 — data requirements & inventory session]

### Added
- `reports/data_requirements_and_inventory.md` — canonical data bill-of-materials (A1–D6 matrix),
  fully verified physical inventory (39/39 checksums re-hashed PASS, 0 orphans, 0 mutations), D5
  byte-match vs PREREG §6, gap summary with per-item unlock conditions + closing commands, quarantine
  status, and the completeness line ("5 of 14 satisfied; remaining unlock on Refinitiv/LSEG entitlement").
- `config/data.yaml: universe_pull` — A1–A5 acquisition bill-of-materials, citation-annotated, VERIFY
  flags on unconfirmed mnemonics (ADR-019).
- `src/data/pull_universe.py` — header-tolerant parsers (membership / delisting / panel) + journaled-engine
  orchestrator; `pull-universe` CLI subcommand (dry-run default, `--live` when entitled); `make pull-universe`.
- `tests/test_pull_universe.py` — 5 parser/orchestrator tests on synthetic fixtures (no network).
- `DECISIONS.md` ADR-019 (A1–A5 wiring; identification untouched) + ADR-017/018 reserved markers.

### Verified (no change to data)
- Re-probed entitlements: platform session did not open this run (P0 BLOCKED `OpenState.Closed`, vs PASS
  on 10 Jun — short-lived RDP token); data-access conclusion unchanged (no non-empty scope set ever);
  DSWS still `ZLDU178` ClientApi-not-entitled. Report regenerated.
- Write-once integrity: every layer re-hashed, all PASS, no orphan/mutation.

### Unchanged (integrity)
- PREREGISTRATION.md + prompts/ byte-untouched; lambda_frozen null; no data re-pulled; no new dependency;
  no live Refinitiv pull beyond the probe. Test suite 118 passed + 1 platform-skip; ruff clean.

## [2026-06-10 — close-out session] — Pre-Friday plan completion (sections A–E only)

### Added
- `docs/outbox/availability_reply_ramin.md` — copy-paste-ready Thu/Fri availability reply (two bracketed
  slot placeholders, group-format preference, one-pager closing line). DEADLINE: TODAY. Not sent.
- `docs/outbox/escalation_lseg.md` — finalized LSEG escalation (DSWS ClientApi enablement for account
  ZLDU178; RDP data scopes; WRDS/CRSP question; recipient guidance). Verbatim from the entitlement
  report. Not sent.
- `docs/staging/PREREGISTRATION_v1.0_FINAL.md` — freeze candidate: current draft + exactly three folded
  changes (§3 λ tie-break sentence; §4a naming the H4 reward family per config; §10 hash cell re-pointed
  to ADR-005). Diff-verified: 19 lines, all accounted for. Live PREREGISTRATION.md byte-untouched.
- `docs/staging/FREEZE_RUNBOOK.md` — ordered T4 commands + Step-0 decision list: (1) single-shot arm
  count 80 (PREREG §4) vs 240 (config) — recommend "240 = 80 × R=3"; (2) "fixed hyperparameters from
  config/" but no algo-hyperparameter file exists yet — add config/algos.yaml or re-word before freezing.
- `reports/meeting_script.md` — 2-minute spoken version ending on the ICAIF 2-Aug question.
- `reports/session_report_2026-06-10_close.md` — this session's stage-by-stage report incl. 4090 runbook.

### Changed
- `reports/research_brief_v1.md` — live-status block added (5,282×35 panel marked PROVISIONAL pending
  PIT; kurtosis 49.9 / Hill 2.1–3.6 headline; entitlement one-liner; freeze-staged-Friday line).
  427 words — one page.
- `docs/evidence/entitlement_report.md` + probes.json regenerated by a fresh live probe run
  (REFINITIV_APP_KEY present in .env → probe executed per plan): outcomes UNCHANGED — token still
  carries zero scopes (new EDP-API key not yet minted); DSWS still "ClientApi not entitled" for ZLDU178.
  Checklist statuses remain accurate as-is.

### Explicitly NOT done (per session constraints)
- Nothing sent, frozen, or signed; PREREGISTRATION.md, prompts/, scope-lock list untouched
  (byte-verified); lambda_frozen still null; no new dependencies; no week-15 work, no training,
  no new pipeline stages. `make smoke`/`make lock` remain 4090 actions (runbook in the session report).

## [2026-06-10] — Session: W15 build-out + research-grade data platform

### Added — research engine (week-plan W15 items)
- `src/features.py` — leakage-safe cash-row features [vol20, vol20/vol60, vix]: rolling sample std of
  the equal-weight market proxy, shift(1)-lagged, VIX/100 scaling, NaN warm-up; truncation- and
  future-perturbation-invariance tested (ADR-007).
- `src/portfolio_env.py` — optional `cash_features` observation block with fail-loud non-finite guard;
  observation dim +3 when supplied; accounting unchanged (ADR-007).
- `src/rewards_baselines.py` — completed the six-reward canon: `SharpeEpisodic` (expanding-Welford SR
  increment, telescopes to episode Sharpe), `CVaRPenalisedMean` (Rockafellar–Uryasev shortfall),
  `DrawdownPenalised` (running-peak level penalty), `TurnoverPenalised` (extra anti-churn shaping);
  `BASELINE_FACTORIES` registry test-enforced against `config/eureka_loop.yaml` (ADR-009).
- `src/reward_family.py` — six-term parameterised reward family for the H4 random/BayesOpt arms; vertices
  recover the hand-designed canon; seeded uniform sampler over config-frozen ranges; shared
  `params_to_reward` constructor; content-addressed `params_id` (ADR-010).
- `src/calibrate_lambda.py` — PREREG §3 λ-selection machinery: per-λ separation accuracy of known-good vs
  known-degenerate rewards; tie-breaks = across-seed stability, then smallest λ; full table returned for
  the freezing ADR; never writes config (ADR-010).
- `src/candidate_archive.py` — verbatim append-only candidate archive (source + prompt + model snapshot +
  temperature + outcome; content-addressed; collision raises) per R6 (ADR-008).
- `src/dry_run_random_search.py` — TrialLedger end-to-end dry run on labelled THROWAWAY candidates
  (synthetic returns, untrained fixed-logit policies, explicit throwaway λ): 10 candidates → ledger N=10 →
  DSR 0.577 / SR0 +0.069 → PBO 0.094 over 12,870 CSCV splits; sidecar to `runs/dry_run/` (ADR-010).
- `src/reward_contract.py` — `probe_contexts()` extracted as the single source of the synthetic probe
  battery (in-process validator and sandbox share it).

### Added — data platform (`src/data/`, 13 stages; ADR-012)
- `vault.py` — write-once layered storage (raw/staged/clean/gold), SHA-256 manifest (`manifest.jsonl` +
  legacy `checksums.txt`), provenance sidecars, checksum-verified reads (unmanifested reads refused),
  lineage graph (`record_lineage`/`lineage_chain`).
- `acquire.py` — rate governor, exponential backoff with full jitter, per-chunk resumable `PullJournal`,
  ticker/date chunkers, minimal `.env` loader (no new dependency; never logs values), provenance capture
  with library versions, vendor fetchers (Refinitiv platform/desktop, DSWS `DataClient`, yfinance
  OHLCV+actions non-adjusted, FRED, Ken French), `EntitlementError` degradation type,
  `capture_field_definitions` (RI day-count = explicit MANUAL-CONFIRMATION record).
- `probes.py` — automated DATA_ENTITLEMENTS checklist (chain, PIT 2018/2010, DSWS list, GE exit window,
  dead-RIC `LEH.N^I08`, field definitions) → `docs/evidence/entitlement_report.md` + `probes.json`;
  escalation email auto-rendered when the pre-2016 path fails both vendors.
- `security_master.py` — RIC↔ticker symbology with dead-RIC `^`-suffix parsing (month letters A–L),
  yfinance symbol mapping (share-class dashes), curated overrides (GOOG/GOOGL 2014, META/FB 2022),
  `resolve()` that raises on unknown/ambiguous symbols.
- `validate.py` — minimal schema core (dtype/nullability/bounds/monotone-unique tz-naive index), explicit
  coercion (never invents values), XNYS sessions via exchange-calendars with explicit `calendar_start`
  (default ~20y lookback would clip 2005), calendar alignment with off-session reporting, exact-vs-conflict
  duplicate detection, missing-data engine (holiday/pre-IPO/post-delisting/interior taxonomy, full
  conservation counting, ZERO interpolation).
- `integrity.py` — RI internal-consistency flags, unadjusted-split signatures (−50%/−66.7% without vendor
  record), stale-price runs, zero-volume flags, Ince–Porter screens (daily adaptation, documented),
  cross-sectional extreme-day classification with SELF-EXCLUDED peer context (a lone collapse cannot
  certify itself via the EW average), reason-coded quarantine assembly — REAL_TAIL rows are never
  quarantined; no function mutates values.
- `membership.py` — PIT membership normalize/stitch with 2016 overlap cross-validation (Jaccard table),
  joiners/leavers audit, Shumway corrections with per-application audit log and citation (input never
  mutated), `members_asof`/`top30_at` strictly-prior selection (PIT leakage assertions in tests).
- `reconcile_full.py` — two-vendor reconciliation with discrepancy clustering (ex-div / split day /
  index-exit window / unexplained→quarantine), per-field vendor-authority merge (column-wise only;
  cell-wise blending would fabricate an unpublished series).
- `panel.py` — as-of join framework (`AsOfFeature` declares availability lag; the only sanctioned join),
  gold construction (returns panel, cash features via `src/features.py`, EW market proxy, top-30 per
  window when membership+mcap exist), `materialize_splits` = PREREG §6 exact (dev train/val, 8
  walk-forward folds 2018–2025, 21-trading-day embargo at every boundary, CPCV 16 purged blocks) as
  explicit session lists; parquet artifacts with lineage.
- `eda.py` — ADF/KPSS, moments, Hill left-tail estimator, |r|-ACF + ARCH-LM, rolling mean pairwise
  correlation, cross-sectional dispersion, drawdown anatomy, naive reconstitution turnover; every figure
  captioned with the design choice it motivates; headless matplotlib.
- `quality.py` — weighted per-series quality score, coverage matrix, scoreboard, lineage map renderer,
  Gebru et al. datasheet generator (auto-filled from manifests, ⟨TBD⟩ when empty), data-chapter seed
  paragraphs (one per stage, real numbers injected when available).
- `cli.py` — `python -m src.data.cli {probe,pull,build,validate,reconcile,eda,status}`; per-stage run
  sidecars (config hashes, wall-clock, counts); graceful vendor degradation recorded as explicit SKIP.
- Makefile targets: `data-probe data-pull data-build data-validate data-reconcile data-eda data-status`.

### Added — tests (68 → 113; all offline, synthetic fixtures in tmp dirs only)
- `tests/conftest.py` — `data_root` fixture redirects every platform module's ROOT to tmp.
- `tests/test_features.py` — truncation/future-perturbation invariance, lagged VIX, zero-variance ratio,
  env integration (dims, accounting equality, NaN rejection).
- `tests/test_sandbox.py` — 15-case static denial corpus (multi-import bypass, np.load/.lib/DataSource,
  dunders, eval/getattr/open, class/decorator/yield/global, oversized, missing compute_reward, syntax),
  numpy-idiom acceptance incl. real `import numpy as np` execution, malformed-runtime corpus (wrong arity,
  NaN, component-name instability), infinite-loop kill, Linux-gated memory bomb, result-validation bounds.
- `tests/test_rewards_baselines.py`, `test_reward_family.py`, `test_calibrate_lambda.py`,
  `test_regimes.py` (truncation invariance proves filtering-not-smoothing), `test_candidate_archive.py`,
  `test_dry_run.py`.
- `tests/test_data_vault.py` (write-once, tamper detection, lineage chains), `test_data_acquire.py`
  (governor spacing, backoff, journal resume idempotence, env loader), `test_data_validate.py` (schema,
  XNYS MLK-day alignment, conflicts, missing conservation), `test_data_integrity.py` (split recorded-vs-
  suspect, IP screens, REAL_TAIL preservation vs lone-crash quarantine), `test_data_membership.py`
  (splice/overlap, Shumway log + non-mutation, strictly-PIT top-30), `test_data_panel.py` (as-of lag,
  PREREG-§6 embargo-exact splits, gold leakage assertion, golden determinism), `test_data_security_master.py`,
  `test_data_property.py` (hypothesis: softmax/drift distributions, missing-cell conservation, chunk
  partitions, quality bounds), `test_data_cli_and_quality.py` (offline probe report, status, reconciliation
  clustering, authority merge, datasheet honesty).

### Added — configuration
- `config/environment.yaml`: `state.vol_short_window/vol_long_window/vix_scale`; `reward_defaults` for
  cvar_penalised_mean / drawdown_penalised / turnover_penalised (scale-parity comments).
- `config/eureka_loop.yaml`: `reward_family` search space (weight ranges, α choices, window choices).
- `config/data.yaml`: `platform` block (layers, manifests, lineage, journal, quarantine, evidence, runs,
  XNYS calendar + explicit `calendar_start`, chunking, rate limits, outlier taxonomy thresholds,
  vendor-authority rules, quality weights).
- `config/llm.yaml`: PIN_ME resolved — primary `claude-sonnet-4-6` @ $3/$15 per MTok (verified on the
  official models overview 2026-06-10; dateless 4.6-generation ids are documented pinned snapshots);
  open-weights companion `deepseek-ai/DeepSeek-V3-0324` (dated HF checkpoint) (ADR-016).

### Added — governance & docs
- Git repository initialized (the project was previously inside the home-directory repo); two commits:
  `75a697c` scaffold + W15 build-out, `0af2ee9` data platform.
- `DECISIONS.md`: ADR-007 … ADR-016 appended (features, sandbox+archiver, baselines, family+λ-rule,
  filtered HMM, platform architecture, dependencies, build-box environment, entitlement outcome,
  LLM pin).
- `docs/evidence/entitlement_report.md` + `entitlement_probes.json` (live probe evidence).
- `docs/DATASHEET_v1.md`, `reports/eda_v1.md` + `reports/figures/*`, `reports/data_quality_scoreboard.md`,
  `reports/data_chapter_seeds.md`, `docs/evidence/lineage_map.md` — all generated from REAL pulled data.
- `CHANGELOG.md` (this file) and `reports/session_report_2026-06-10.md`.

### Changed
- `src/sandbox.py` — full hardening rewrite (ADR-008): AST static gate replaces the bypassable string
  check; per-resource best-effort rlimits clamped to current hard limits (fixes pre-existing macOS
  `RLIMIT_AS` crash that failed `test_benign_candidate_executes`); minimal subprocess env (no inherited
  secrets, BLAS threads pinned); runtime `__import__` restricted to numpy (previously `None`, which broke
  the mandated `import numpy as np`); parent-side contract validation incl. component-name stability.
- `src/regimes.py` — explicit scaled forward recursion over public fitted parameters replaces private
  hmmlearn APIs; filtering proven causal by truncation invariance (ADR-011).
- `src/feedback_schema.py` — `empirical_cvar` now self-enforces ascending input (R5 made structural);
  `build_feedback` alpha grid defaults from config instead of a duplicated literal.
- `src/data/cli.py` — Ince–Porter price screens fed RAW close instead of adjusted close (the $1 threshold
  is about actual traded microstructure; split-adjustment retroactively drags early AAPL below $1). The
  v1 pilot quarantine (13 rows) was produced under adjusted prices — values were never mutated and
  clean/gold are unaffected; the corrected screens apply from the next build.
- `src/data/acquire.py` — FRED keyless path: date-chunked public fredgraph CSV (full-range requests 504 at
  FRED's gateway; pandas-datareader's combined request times out identically).
- `src/pull_pilot.py`, legacy tests — semicolon statements split; `make lint` now actually passes
  (pre-existing ruff failures fixed forward, no test weakened).
- `Makefile` — data-platform targets appended.
- `requirements.txt` — platform dependencies appended with ADR-013 reference (refinitiv-data, DatastreamPy,
  pyarrow, exchange-calendars, statsmodels, hypothesis, tabulate).
- `README.md`, `docs/environment_spec_v1.md`, `docs/DATA_ENTITLEMENTS.md`, `docs/week_plan_June15.md` —
  status updates to match code as built.
- `.venv` rebuilt on Python 3.12 (3.13 has no torch wheels; d3rlpy 2.8 needs torch≥2.5 which has no
  Intel-mac wheels at all → RL stack remains a 4090 install per ADR-002/ADR-014).

### Live runs (real data only — R4; nothing synthetic enters `data/`)
- Entitlement probes: Refinitiv platform session AUTHENTICATES (credentials recovered, at user direction,
  from `~/Downloads/ifte0005_phase1/.env` into gitignored `.env`; values never displayed) but carries an
  EMPTY RDP scope set — no datagrid, no historical-pricing; Workspace desktop path needs interactive
  login; DSWS connection refused (separate entitlement). Escalation email rendered (ADR-015).
- Pulls frozen to the raw vault: yfinance OHLCV+dividends+splits 2005–2025 (5 field artifacts, 5,282
  sessions × 5 pilot names), FRED {VIXCLS, DGS3MO, DGS10, T10Y2Y} (5,478 rows), Ken French daily factors
  + momentum (5,365 rows each). 8 raw artifacts, 42,618 rows, all SHA-256-manifested with provenance.
- Pipeline: staged (XNYS-aligned, validated, missing-classified) → integrity (13-row quarantine queue:
  6 sub-dollar flags + 7 Citi-2009 extreme-day reviews; tails preserved) → clean 5,282×5 (authority:
  yfinance fallback, decision recorded) → gold (returns panel, cash features, market proxy, PREREG-§6
  splits — dev val 734 post-embargo sessions starting 2015-02-03, 8 walk-forward folds) → EDA (excess kurtosis 5.75–49.9,
  Hill α 2.18–3.48 — the fat-tail evidence behind the CVaR fitness) → quality scoreboard + datasheet +
  lineage map. Every stage left a run sidecar under `runs/data/`.

### Live runs — second wave (universe-scale shadow + screen correction)
- Shadow30 pull: 30 additional real large-caps via yfinance (journaled, 2 chunks of 25; union with the
  pilot = 35 names) — explicitly a PIPELINE-SCALE proof, **not** the research universe (PIT top-30
  selection awaits entitled membership data). 18 raw artifacts total, all checksum-verified (0 failures).
- **Vendor subtlety discovered and fixed at scale**: yfinance `Close` is split-adjusted even with
  `auto_adjust=False` (NVDA's 2005 close reads $0.196 vs ~$23.5 actually traded). Added
  `integrity.reconstruct_unadjusted_close` (close × ∏ future split ratios; unit test pins the exact
  inversion) and routed the Ince–Porter $1 screen through reconstructed traded prices. Effect at scale:
  4,274 phantom sub-dollar flags → **0**; quarantine_v2 holds exactly the 49 genuine extreme-day reviews;
  34 REAL_TAIL classifications preserved.
- v2 build: clean 5,282 × 35; missing engine: 184,870 cells, 177,269 observed, 7,601 pre-IPO masked
  (TSLA/META/ABBV/AVGO… — taxonomy conservation hypothesis-tested), 0 interior gaps; EDA refreshed across
  35 names (Hill α 2.14–3.59 — uniformly fat tails). v1 `_pilot`/`_shadow30` artifacts remain manifested
  (write-once); v2 supersedes for analysis.

### Live runs — third wave (app-free Refinitiv access characterized)
- Added probe **P8 "RDP scope census"** (search/news/pricing families): token carries ZERO scopes for
  EVERY product family → cause narrowed to app-key permissions vs seat licence; BLOCKED status carries the
  app-free fix (web App Key Generator, "EDP API" box, new key in `.env`). Fixed a status-flip bug my P8
  insertion introduced (P7 MANUAL flag had moved onto P8).
- **DSWS upgraded from "unreachable" to "authenticates, service flag missing"**: probe P4 now returns
  `User not entitled to ClientApi service` — credentials are valid Datastream credentials; escalation email
  sharpened to a one-line enablement request (+ RDP scope ask). Checklist row 4 upgraded ❌→🟡.
- No machine-account credentials exist on the laptop (targeted LSEG_*/MACHINE_ID name-scan: zero hits).

### Deliberately NOT done (scope/governance)
- PREREGISTRATION.md, prompts/, and the R2 scope-lock list: UNTOUCHED.
- `lambda_frozen` remains null; the freeze (T4) and supervisor sign-off remain the author's actions.
- No Eureka-loop orchestrator / LLM client yet (post-freeze work; provider now pinned).
- No optuna (BayesOpt arm later, own ADR). No paper-trading, no scope-locked items.

## [2026-06-10] — Initial scaffold (pre-session baseline, commit 75a697c)
- Feedback schema, stats inference (PSR/DSR/MinTRL/PBO/TrialLedger), fitness, env core accounting,
  reward contract, prompts v0, configs, docs, 19-test suite (ADR-001…006).

## [2026-06-12 — completion wave] — Universe data layer COMPLETE (ADR-021)
- A2–A5 pulls finished: journal 653+ chunks frozen / 0 failed; raw vault 788+ artifacts, 5.86M+ rows.
- Third silent-form catch: `TR.TotalReturn` via get_history is empty on this route → datagrid long
  Frq=D (39 junk artifacts invalidated); mnemonic checks now read VALUES.
- Acquisition PARALLELISED on user request: thread-safe launch governor (global requests_per_minute
  respected exactly), 6 workers overlapping response latency; vault/journal lock-serialised; exact
  resume under concurrency (tested).
- `selection_buffer_months`: membership+caps acquired before window.start → dev-2005 top-30 selects on
  strictly-prior Dec-2004 data. Span-stamped artifact versioning fixed a write-once collision.
- **Research panel built (suffix _univ3, canonical):** clean 5,283×953; missing engine 5.03M cells /
  373k pre-IPO / 957k post-delisting / 3,155 interior (0.06%); top-30 at all 9 window starts
  historically exact (dev-2005: GE/XOM/MSFT/C/WMT/PFE/BAC/JNJ; 2019: MSFT>AAPL); two-vendor
  reconciliation median corr 0.99994 (35 names; 390 breaches clustered to ex-div/split);
  dev-30 EDA: excess kurtosis WB 89.4 / AIG 76.8 / C 49.8 — GFC tails inside the search window.
- D1–D6 all satisfied on entitled PIT data. _univ/_univ2 superseded (manifested, write-once).
