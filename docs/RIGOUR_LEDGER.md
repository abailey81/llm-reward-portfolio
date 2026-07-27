# RIGOUR LEDGER — defended threats → one-line resolutions → pointers

**Status.** Reference table (no code / config / pre-registration edited). **Date:** 2026-06-26
(extended through R60 on 2026-06-26; A-bis addendum 2026-07-01; A-ter addendum 2026-07-02 — the
executed Split-C/univ5 rebuild, ADR-044/051, R73).
**Repo:** `llm-reward-portfolio`. **Purpose.** Make the in-code rigour *legible*: one row per
methodological / security / statistical threat that the design defends against, its one-line
resolution as actually implemented or decided, and the canonical pointer (amendment R-number, ADR,
or `file:section`). This is a navigation aid, **not** dissertation prose and **not** a substitute for
the authoritative records. Each row is quote-grounded against the source named in its pointer.

**Authoritative sources this indexes.** The machine-readable amendment ledger is the table at
`PREREGISTRATION.md` (the "Amendment record", R11–R60), with each amendment's body in §1–§12 of the
same file. ADRs live in `DECISIONS.md`. The adversarial audits that surfaced several threats are the
`docs/DEEP_*.md` dossiers and `docs/DEEP_AUDIT_2026-06-25_13agent.md`.

> **Three load-bearing caveats (read before citing a row as "closed").**
> 1. **Provenance / freeze timing.** Several amendments (notably R25, R32, R33) are dated
>    **2026-06-25**, *after* the 2026-06-21 prototype showed the directional CVaR pattern, and the
>    design is **not yet hash-frozen** (`config/preregistration.yaml: frozen: false`,
>    `freeze_hash: null`). When citing these as *pre-committed*, pair each with the provenance defence
>    (theory-driven; pilot disclosed as corroborating, not causal) and run `freeze.py` before the
>    "bankable pre-registered null" claim is literally true (`DEEP_AUDIT` T1.2).
> 1b. **R33 is SUPERSEDED on the headline-panel choice — read the R39/R44 rows.** R33's "adopt `univ4`
>    as the headline panel" was *reversed*: R39 (2026-06-26) showed the Shumway −30/−55% surcharge is
>    un-gated and fabricates M&A losses on 100% of delistings, and R44 (2026-06-26) reverts the frozen
>    headline to `univ3` (zero-fill / `liquidate_to_cash`, no fabrication), with `univ4` re-cast as the
>    M&A-contaminated *heavy end* of the `delisting_band` tail instrument. The loader default is already
>    `univ3` ⇒ the campaign runs with **no** `LLM_RP_GOLD_SUFFIX` override. Wherever an older row or doc
>    says "univ4 = headline," prefer R44. **[Updated 2026-07-02, R73: the ACTIVE headline panel is now
>    `univ5` (the settled-2026 extension of univ3; same zero-fill semantics; byte-identical on the
>    overlap), selected by the hash-bound `config/data.yaml: gold.suffix: univ5` — still no env-var
>    override; `univ3` is the frozen pre-Split-C reference. The observed-terminal audit (A-ter row T3)
>    additionally showed univ4's surcharge DOUBLE-COUNTS vendor-present terminals.]**
> 2. **Some strengths have NO amendment id.** The off-critic 3-way decoupling, the per-seed IUT
>    construction, and the H1 conservatism-vs-Eureka argument are *design properties*, banked in
>    `PREREGISTRATION §2` / the audit's "GENUINELY STRONG" section, not R-numbers. Their rows point at
>    a doc section, by design.
> 3. **One amendment can answer two threats, and one threat can span two pointers.** R27 covers both
>    the EVT small-sample-bias row and the Troop honest-disclosure row; the single-seed-winner row
>    splits into a baseline (H1, R30) facet and a reward-draw-variance (H2, CAMPAIGN_variance) facet.

---

## A. The defended-threat table

| # | Threat (one line) | Resolution (one line) | Pointer |
|---|---|---|---|
| 1 | Conjunction × BH **double-correction**: a 3-leg conjunction is already an IUT (size ≤ α); BH-over-m=6 on top double-corrects and the large CVaR p-values inflate the thresholds the Sharpe legs must clear. | Replaced with **two co-primary IUTs** — H2-RA (3 Sharpe legs, m=3) + H2-Tail (3 CVaR-5% legs, m=3), each one-sided at α=0.05, no further leg correction (the conjunction *is* the correction); CVaR-5% elevated to co-primary; BH-over-6 demoted to a reported sensitivity. | **R25** · `PREREGISTRATION.md` §1/§10 · `docs/DEEP_H2.md` §3.1–3.3 |
| 2 | **EVT small-sample bias**: the fed CVaR-5%/1% is GPD-extrapolated, and GPD-MLE shape on ~75 exceedances is high-variance/biased. | Tail estimator is **plain GPD MLE** (`scipy.stats.genpareto.fit`, no bias correction) + a `threshold_sensitivity` stability exhibit; CVaR-1% retained but flagged high-variance. | **R27** · `PREREGISTRATION.md` §4 · `src/feedback/measurement.py::_evt_cvar` (`EVT_ESTIMATOR_NOTE`) |
| 3 | **Tail-seeding prompt**: the shared base prompts named "tail/CVaR", so even the inert `placebo` arm wrote real CVaR code (~78% of candidates) → the feedback contrast could not isolate its own mechanism (format-vs-content confound). | Tail vocabulary **removed from all four prompt sources** (`prompts/system.txt`, `prompts/initial_generation.txt`, `src/llm/prompts.py`, the diversity directive in `src/llm/loop.py`); only general "risk-adjusted performance" framing kept, so only the distributional arm's *feedback* introduces the tail. | **R38** · `PREREGISTRATION.md` §2/§3 |
| 4 | **Sandbox `np.load` / RCE**: `ImportFrom` checked only the root module, so `from numpy import load` (numpy allowlisted) passed, then `load(...)` is a bare `Name` the attribute denylist never inspects → pickle-RCE; `from numpy import *` was the same hole. | `ast_gate` now **rejects all `from … import` (incl. wildcard)** — reward code only ever needs `import numpy as np` — atop an **AST allowlist** (`_ALLOWED_ATTRS`) + denylist + dunder ban + `_FORBIDDEN_CALLS` + format-field regex scan + restricted `_safe_import`/`SAFE_BUILTINS`. **Regression coverage exists** (`tests/test_audit_regressions.py::test_from_numpy_import_rce_rejected_at_gate`; `tests/test_sandbox.py` RCE-vector parametrization). | **ADR-008** · `src/sandbox/executor.py:469–475` ("SECURITY (RCE fix, 2026-06-25)") · audit `DEEP_AUDIT` T1.3 |
| 5 | **PopArt / reward-scale sensitivity**: (i) LLM rewards dividing return by a ~1e-8-floored variance caused late critic explosions; (ii) arms author rewards of different natural scales, so under PopArt's σ≥1 clamp + `ent_coef=auto` two "fixed-agent" arms get effectively different entropy regularisation (a latent H2 confound). | **PopArt-style value-target normalizer** (`src/agents/popart.py`, positive-affine ⇒ policy-invariant) applied **uniformly across arms**; reward stays the object (`norm_reward=False`, `port_ret`/fitness/tails byte-identical); `learning_starts` floored; both config-gated, default on. Residual scale confound **disclosed + 1-seed `popart=False` ablation on the winners**. | **R42** · `PREREGISTRATION.md` §5/§11 · ablation `DEEP_AUDIT` T2.4 |
| 6a | **Single-seed-winner asymmetry (baseline / H1 side)**: `max` over four noisy baseline Sharpes is biased up (Jensen), and H1 picks `best_name` on the *same* sealed test leg it reports the win on, with no MCB/SPA. | Evaluate the four baselines + LLM winner on the **sealed test leg**; **select the best baseline on validation, not test**, and reframe **H1 as descriptive/report-only**, subordinate to the comparative H2 (so H1 carries no inferential multiple-comparison claim). | **R30** · `docs/DEEP_H1.md` §2.2–2.4 |
| 6b | **Single-seed-winner asymmetry (reward-draw / H2 side)**: the IQM gap could be *one lucky reward* the search drew (K=1 in the prototype ⇒ N_eff≈1), not a channel property. | **Variance-decomposition appendix** partitions a per-seed score into σ²_seed / σ²_search / σ²_market via one-way random-effects ANOVA on a (K≥2, S) table; deliverable: "the IQM gap exceeds √σ²_search ⇒ a channel property, not one lucky reward." | `docs/CAMPAIGN_variance.md` · `scripts/variance_decomposition.py` · finding `DEEP_AUDIT` T0 |
| 7 | **Self-grading / estimator coupling**: if the signal *fed* were also what the arm is *selected* on or *graded* by, any tail effect would be a self-grading artifact, not channel-attributable. | The three are deliberately **decoupled** — **fed** = EVT/GPD on *training* returns; **selected** = tail-blind validation Deflated Sharpe (λ=0, reward-independent); **tested** = empirical CVaR on the *sealed* test split — and the separation is unit-tested. Because the signal is **measured off-critic** it is **critic-agnostic** (reads no Q-network; NOT agent-independent — the fed tail is endogenous to the policy). *(Strength, not an amendment — no R-number.)* | `PREREGISTRATION.md` §2 (audit A-1) · `CLAUDE.md` "two distinct 'distributional' axes" · `DEEP_AUDIT` §"off-critic 3-way decoupling" |
| 8 | **Responsiveness measured-vs-fed confound**: responsiveness must be scored against what was *fed*, not what was later *measured*; the early `specification_gaming` gate (on `val_fitness ≤ 0`) missed the worst offenders (they post positive fitness, computed from `port_ret` not the reward `total`). | Forensics reframe: first-class **`unbounded_magnitude`** class flagged on *code shape* (the `return/(var+ε)` form) independent of fitness; tautology regexes anchored to statement start; the `feedback_responsiveness` measure reads **both** the `feedback_block` *and* the `prompt`. All forensics stays **DIRECTIONAL** (no number enters the inferential result). | **R41** · `PREREGISTRATION.md` §10 · `scripts/inspect_rewards.py` · finding `DEEP_AUDIT` T0 |
| 9 | **Cross-hypothesis multiplicity**: treating H1–H4 as separate families (vs one corrected family) with "many rewards tried" is an unstated researcher degree of freedom (garden of forking paths). | Pre-register the stance: H1–H4 are **separate pre-registered estimands**, each with its own control (H2 = two IUT families; H4 = Bonferroni-over-4 (the family grew 2->4 on 2026-07-26; corrected 2026-07-27, #100); H1 = descriptive; H3 = single contrast + TOST); **no global FWER by design**, plus a report-only **Bonferroni-across-4 sensitivity**. | **R31** · `PREREGISTRATION.md` §10 · `docs/DEEP_STATS_backbone.md` (A4 / fix C4) |
| 10 | **TPE→GP-EI mislabel**: the `eureka_loop.yaml` label `bayesopt_tpe` / "Optuna TPE, 240 trials" was factually false (Optuna is not a dependency; budget is 30/40). | Relabel H4b to its true method — **scikit-learn GP + Matérn-2.5 Expected-Improvement** (n_init=5, matched budget 30); cite **Snoek, Larochelle & Adams 2012**, not Bergstra-2011 TPE. Integrity-only, no science change; frozen arm name `bayes_opt` unchanged. | **R29** · `PREREGISTRATION.md` §3 · `docs/DEEP_H4.md` §0.1 |
| 11 | **H4 grammar richness artefact**: the H4a random-search control sampled a 3-term grammar (return−var−cvar), strictly poorer than the BO family / the LLM, so a positive H4a was partly a richness artefact. | H4a now samples the **same six-primitive family as H4b** (`reward_family.params_to_source`: return/log/turnover/drawdown/cvar/vol) from a coarse grid at fixed α=0.05/window=20 — a genuine procedure-only control at comparable richness; budget unchanged. | **R28** · `PREREGISTRATION.md` §3 · `src/search/random_search.py` |
| 12 | **Troop docstring over-claim (honest-disclosure)**: the prior §4 text promised a "frozen Phase-1 enhancement" (Troop bias-corrected POT) the code never performed — a docstring promising a fix the code does not do. | Same amendment as #2: **demote Troop bias-corrected POT to disclosed FUTURE WORK** (its 2nd-order regular-variation correction is ill-conditioned at n≈750, α≤0.05, ξ≤0 for ~94% of samples ⇒ would not reduce RMSE); docstring no longer promises an unimplemented fix. | **R27** · `PREREGISTRATION.md` §4 · `docs/DEEP_H2.md` §6.2 |
| 13 | **H1 over-bar / data-snoop**: presenting H1 as an inferential claim it cannot support (no MCB for the max-of-4; baseline identity data-snooped on test); Eureka itself compared vs *one* human reward, uncorrected. | H1 requires the LLM winner to beat the **max over four** hand rewards (return; return−var; return−CVaR; differential Sharpe) on the **sealed test leg** (2018–2025 at R30; **2020–2026H1 since Split C, R73** — a strictly higher bar than Eureka's single-human), with a 30-trial DSR deflation; baseline identity **selected on validation**, metric relabelled **Eureka-STYLE**, claim made **descriptive/report-only**. | **R30** · `PREREGISTRATION.md` §1 · `docs/DEEP_H1.md` §2.1, closing statement |
| 14 | **Anomaly-harvest recast (BAB)**: a long-only vol-lowering agent structurally loads on Betting-Against-Beta / low-vol, so the headline could be recast as "just a low-vol/BAB beta," not the reward channel. | **Pre-registered secondary declared family** (`src/inference/attribution.py`): difference-in-alpha (distributional − comparator) across a CAPM/FF3/Carhart-4/FF5/FF6(+BAB,QMJ) ladder with **Newey-West HAC SEs**, fit **per-seed and paired across-seed** into the same per-seed bootstrap as the headline. Disjoint from the frozen m=6; never a gate. | **R26** · `PREREGISTRATION.md` §9 · `docs/CAMPAIGN_attribution.md` · LIMITATION L15 |
| 15 | **Anti-conservative seed-averaging**: the prior test averaged each arm's per-seed return series before one block-bootstrap, shrinking the tested object's variance ~N× (a 30-seed calibration measured true-null rejection ≈21% vs the correct ≈5%). | Difference tests now **aggregate ACROSS SEEDS**: each arm's per-seed Sharpe/CVaR scores reduce to an **IQM**, tested by a **paired stratified bootstrap over shared training seeds** (`src/inference/bootstrap.paired_seed_difference_test`), carrying the across-seed variance at n=30 (rliable). Also wired `h2_conjunction` into the analysis entry point (previously implemented + tested but unwired). | **R16** · `PREREGISTRATION.md` §10 · `docs/DEEP_STATS_backbone.md` (pt. 4); audit confirms ≈21%→≈5% |

---

## A-bis. 2026-07-01 resolution addendum (three limitations UPDATED this session)

Appended (not rewritten) after the exhaustive upgrade-research pass of 2026-07-01. These update the *status*
of three previously-open limitations; the table above is unchanged. Each is marked **DECIDED** (settled plan)
vs **EXECUTED** (already done and verified).

| # | Limitation (one line) | 2026-07-01 status | Pointer |
|---|---|---|---|
| A1 | **Training-adequacy / convergence** — was the SAC agent trained to convergence, or is the null a mere under-training artefact? | **EXECUTED — convergence diagnostic DONE.** The learning-curve ladder gives **B\*=200k** with **eval curves flat within noise** at the knee (plateau reached, not still-rising) → training adequacy demonstrated, not assumed. (Buffer capped 50k, ADR-042, so all budgets survive on the laptop.) | `docs/SESSION_LOG_2026-07-01_phaseBC.md` (Milestones 1–2) · `scripts/learning_curve.py` · ADR-042 |
| A2 | **Cost realism** — a flat per-bps cost sweep (R15) ignores price impact; a reviewer can call the frictions unrealistic. | **DECIDED — implementation plan now exists (report-only, disjoint from frozen m=6).** Add a **bid-ask SQUARE-ROOT impact cost model** driven by the **already-frozen bid-ask spreads** (A5 — no new pull needed). Upgrades R15's flat sweep to a realistic sqrt-impact frictions exhibit. DECIDED, not yet EXECUTED. | R15 (this ledger) · `docs/RIGOUR_LEDGER.md` A-bis · frozen A5 bid-ask |
| A3 | **Single-market generalisation** — US large-cap only; external-validity weakness. | **DECIDED — FTSE-lite replication planned (report-only external-validity leg).** A multi-market "lite" **FTSE 100** replication over the same protocol; needs the entitled pull (now SOLVED + fast: PowerShell + `.venv-lseg`, ~30 min–2 h). Register as a pre-freeze external-validity amendment. DECIDED, not yet EXECUTED. | `docs/LSEG_DATA_STRATEGY.md` §2B (FTSE-lite DECIDED) |

Also settled this session (context, not new rows): the **BAB/QMJ factor attribution** (R26/R14-row) is
confirmed runnable on **free factors** (no pull); the **2nd LLM is Qwen3-Coder** (GPT-5.5 rejected on cost);
**Refinitiv access is SOLVED** (PowerShell + `.venv-lseg`, verified 2026-07-01) and the pull is FAST.

---

## A-ter. 2026-07-02 addendum — the executed Split-C/univ5 rebuild (ADR-044/051, R73)

Appended after the rebuild EXECUTED (2026-07-02). The active panel is now **univ5** (5,406 × 963,
2005-01-03 → 2026-06-30 settled cutoff) under **SPLIT C** (train 2005–2016 / val 2017–2019 / test
2020–2026H1; purge 60 sessions; executed starts 2017-03-30 / 2020-03-30); `univ3` = the frozen
pre-Split-C reference. New defended threats → guards, same format as table A:

| # | Threat (one line) | Resolution (one line) | Pointer |
|---|---|---|---|
| T1 | **Vendor event-history drift**: Refinitiv silently revises past membership events between pulls (observed live: the `EVHC.N^L16` Dec-2016 leaver event was backfilled between 2026-06-12 and 2026-07-02, making reverse replay claim membership back to 2004 — externally verified impossible AND immaterial, never top-30). | Extension pull runs a **hard-fail overlap gate** + the **SPLICE rule**: the frozen membership record stays authoritative through its own last month (2025-12); the fresh replay contributes ONLY the 2026 month-ends; overlap differences must fall in an **enumerated, externally-verified allowlist** ({EVHC.N^L16}) else the rebuild aborts; extension month-ends + member counts themselves gated. Fired + resolved on first live contact. | **ADR-051 addendum** · `data_pipeline/scripts/extend_universe_2026.py` · `docs/DATASHEET_v1.md` §2026-07-02 |
| T2 | **Extension masquerading as revision**: a "forward extension" that silently changes frozen history (different cells on the overlap) would corrupt every pre-registered development-era result. | **Byte-diff gate**: `verify_gold` univ5-vs-univ3 = **0 changed cells** (max \|Δ\| = 0.000e+00) over the full 5,283 × 953 overlap; only +123 appended 2026-H1 sessions and +10 new-member (2026-joiner) columns; re-verified first-hand for the doc sweep. | ADR-051 acceptance gate (2) · CHANGELOG `[2026-07-02c]` · `verify_gold` |
| T3 | **Delisting-surcharge double-counting**: univ4's unconditional −30/−55 % Shumway surcharge books a second terminal loss on names whose realised terminal ALREADY sits in the vendor daily series (on top of the known M&A contamination, row R39/R44). | **Observed-terminal recovery** (`_recover_terminal_from_returns`): the realised terminal recovered for **all 333 dead names** (audit: `vendor_terminal_kept=333`, **zero surcharges**) → corrected Shumway panel `univ5s` **equals the zero-fill headline on returns**; the band d∈{0,−30,−55,−100 %} stays reported with univ4 as its **disclosed contaminated heavy end**. | **ADR-051** · `docs/DATA_REPULL_DELISTING.md` (EXECUTED note) · CHANGELOG `[2026-07-02c]` |
| T4 | **Silent panel swap / resolved-window drift**: a rebuilt panel whose calendar shifts could move the integer train/val/test windows through the `searchsorted` clamps unnoticed (and an env-var could silently swap the panel identity). | Panel identity is **config-primary + hash-bound** (`config/data.yaml: gold.suffix: univ5`; `LLM_RP_GOLD_SUFFIX` demoted to an explicit sensitivity override), and the resolved windows are **fail-loud asserted** per suffix: `expected_windows.univ5 = [60,3021]/[3081,3775]/[3835,5406]`. The sweep also caught + fixed the Saturday-boundary `searchsorted(side)` leak (2016-12-31) with regression tests pinning the ratified 2017-03-30 start. | `config/inference.yaml: expected_windows` · `run_campaign._assert_expected_windows` · CHANGELOG `[2026-07-02c]` |

---

## B. Full amendment ledger (R11–R60)

Source: the Amendment record table in `PREREGISTRATION.md` plus the §-prose. **There is no R14**
(the table runs R11, R12, R13, R15, R16, …). ADR-023 and amendment D2 predate the R-series; included
for completeness. ≤10-word glosses. The **2026-06-26 block (R43–R60)** post-dates the first ledger
build and is where the headline-panel reversal (R44 supersedes R33) lives.

| Id | § | Gloss |
|---|---|---|
| ADR-023 | §12 | Compute venue: rented RTX 4090; no UCL Myriad |
| D2 | §6,§12 | Winner seed count 5→30; search budget untouched |
| R11 | §10 | Sharpe test relabel: re-centred stationary block-bootstrap (numerics unchanged) |
| R12 | §10 | SESOI = 0.05 DSR + symmetric ±0.05 TOST margin |
| R13 | §10 | Multiple-testing family enumerated + frozen, m=6; BH primary |
| R15 | §10 | Cost-robustness sweep over [0,5,10,25,50] bps, report-only |
| R16 | §10 | Per-seed rliable arm-contrast tests; supersede anti-conservative seed-averaging |
| R17 | §10 | Test-universe = 2005-cohort PIT; documented limitation + PIT robustness |
| R18 | §7 | Inter-split purge widened to max(embargo,lookback)=60 sessions |
| R19 | §9 | Benchmark suite de-duped (SPY=1/N) + expanded to 8 allocators |
| R20 | §10 | rf=0 retained primary + excess-return Sharpe robustness sensitivity |
| R21 | §6 | Optional parallel reflect-on-best search + matched 50k buffer |
| R22 | §5 | λ_cvar=0.0 formalized: pure validation-DSR, tail-blind selection |
| R23 | §11 | Config-driven TF32, uniform across serial/SEARCH/TEST trainers |
| R24 | §6 | Headline search protocol RECORDED = parallel reflect-on-best |
| R25 | §1,§10 | H2 = two co-primary IUTs; BH-over-6 demoted to sensitivity |
| R26 | §9 | BAB/factor difference-in-alpha attribution pre-registered (secondary family) |
| R27 | §4 | EVT = plain GPD MLE; Troop bias-correction is FUTURE WORK |
| R28 | §3 | H4a random-search widened to shared six-term reward family |
| R29 | §3 | H4b relabel: GP-EI Bayesian optimisation, not Optuna-TPE |
| R30 | §1,§6 | H3 + H4 sealed-leg tests wired; H1 hardened descriptive |
| R31 | §10 | Cross-hypothesis multiplicity: separate families + Bonferroni-across-4 sensitivity |
| R32 | §1,§10 | `placebo_shuffled` deranged-tail structure-vs-content control (5th LLM arm) |
| R33 | §7 | Survivorship-corrected `univ4` (Shumway) adopted as headline panel — **SUPERSEDED by R44** (univ4 fabricates M&A losses; headline reverts to univ3) |
| R34 | §10 | Training-divergence diagnostic: 64 lines = 6 diverged runs |
| R35 | §10 | Compute-accounting table of matched-budget asymmetries (report-only) |
| R36 | §10 | Second PBO ranked on the DSR-proxy selection statistic |
| R37 | §10 | Power doc regenerated under one-sided-IUT framing; Šidák as sensitivity |
| R38 | §2,§3 | De-seed tail vocabulary from all prompts; `placebo_shuffled` routing fix |
| R39 | §7 | Delisting surcharge un-gated → `univ4` = M&A-contaminated band END |
| R40 | §12 | Mechanical freeze enforcement (`enforce_freeze`) in the campaign driver |
| R41 | §10 | Reward-forensics: `unbounded_magnitude` class + responsiveness headline (directional) |
| R42 | §5,§11 | Engine de-biasing: PopArt value-target normalization + gated learning_starts |
| R43 | §7 | Frozen scheme corrected to executed `single_sealed_split`; walk-forward deferred |
| R44 | §7 | Headline panel reverted univ4→**univ3** (univ4 fabricates M&A losses); supersedes R33 |
| R45 | §1a | Pre-registered prediction table (Strict/Weak/Null); prototype predicts Null branch |
| R46 | §4 | EVT tail-CVaR hardened: `xi ≤ −0.5` non-regular fallback + estimator-switch log |
| R47 | §10 | Power MDE reconciled Sharpe→DSR (0.256→0.177 ≫ 0.05); INCONCLUSIVE branch |
| R48 | §5,§11 | PopArt scale made auditable (`sigma_max`) + `popart=False` robustness ablation |
| R49 | §1,§10 | H1 beat-the-human comparator-snooped → DESCRIPTIVE-ONLY with top warning |
| R50 | §1 | H3/H4 equivalence symmetrised (±0.05 TOST) + H4a/H4b named references |
| R51 | §10 | Reward-program differential forensics (declared tail-construct prevalence) |
| R52 | §2,§12 | Sandbox from-import RCE closed; freeze CR/LF line-ending invariance |
| R53 | §3 | Novelty/citation/proposal honesty: construct retitle, DLM distinguished, pivot disclosure, this ledger |
| R54 | §3,§12 | Frozen arm roster reconciled to seven + fail-loud freeze-roster guard |
| R55 | §3,§5,§7,§11 | Honest-framing reconciliation of the R43–R53 burst (univ3 lead, endogeneity, run-count 210) |
| R56 | §5,§8 | "Fixed agent"→architecture+hyperparams; single-Claude-family §8 disclosure |
| R57 | §7 | delisting_band pinned to univ4 audit (fixes a real R44 skip-regression) |
| R58 | §1,§10 | DSR-units TOST wired; mechanism differential pools LLM arms only |
| R59 | §2 | Untrusted-reward boundary hardened vs cross-candidate state corruption |
| R60 | §4,§10 | FZ0/ES backtest: HLN small-sample correction + size/power calibration |
| R61 | §1a,§4,§10 | Pre-freeze upgrade (deep-research-verified): null re-based Popperian→Mayoian severity + forking-paths (Rubin 2025; Gelman-Loken 2014); tail-uncertainty propagation in measurement.py (block-bootstrap CVaR CIs + bias + reliability tier; additive, deterministic, fed values byte-identical); conditional GARCH-EVT investigated & REJECTED (breaks cross-platform determinism); mutation exhibit extended to measurement.py (100%). Hash recomputed `4d6a43df…` (frozen:false; USER flips) |
