# Appendix B — Limitations Register
> *Lettering note: this Limitations Register is the dissertation's sole appendix; it is lettered 'B' (not 'A') to mirror the pre-registration's appendix lettering, under which the register is Appendix B — the numbering is intentional, not a missing Appendix A. Word-count status: appendices are excluded from the 10,000-word body count.*

A complete, structured register of the study's limitations, each with its rationale, its direction of bias where
known, and its mitigation or disclosure. Grouped by validity type [`shadish2002experimental`].

## B.1 Construct validity (what the manipulation measures)
- **B.1.1 Tail vector, not the distribution.** Six left-tail scalars; named "multi-level tail-risk feedback".
  *Mitigation:* Chapter 3 shows the vector spans the coherent-risk class; no upside/non-coherent claim is made.
- **B.1.2 Tail-blind selection ($\lambda=0$).** The selector rewards no tail dimension. *Direction:* biases
  *against* a tail effect (conservative). *Rationale:* makes any tail effect channel-attributable, not
  selector-induced. *Future work:* a pre-registered $\lambda>0$ selection variant (B.4).
- **B.1.3 Single-estimator fed CVaR.** The fed 5%/1% CVaR is a generalised-Pareto extreme-value estimate on a few
  hundred training observations, with documented finite-sample bias [`belzile2020improved`; `cont2010robustness`;
  `giles2016biascorrected`]. *Direction:* estimation noise biases *against* detecting a channel effect. *Mitigation:*
  the $\xi\le-0.5$ guard; a bootstrap error bound on the fitted tail is reported, and the fed-signal SNR
  exhibit quantifies which fed components carried resolvable signal at the campaign's horizons.

## B.2 Internal validity (whether the comparison is clean)
- **B.2.0 Endogeneity of the fed signal.** The tail vector is measured on the trained policy's *own* realised
  returns — two coupled reward→policy→measurement loops, never an exogenous measurement; "critic-agnostic" is
  not "agent-independent". *Mitigation:* the fed/selected/tested three-way split keeps the loops from grading
  themselves; the mediation analysis (SQ2) is reported as a descriptive decomposition under
  sequential-ignorability caveats, never as causal proof.
- **B.2.1 Training budget.** The per-candidate budget is 400,000 steps — the knee of a two-stage measured
  learning curve: an initial pilot (flat within seed noise to its 350,000-step ceiling) extended, under a rule
  pre-committed before the extension data existed, to 1,600,000 steps on both archived authored winners; the
  curve rises decisively to 400,000 and flattens beyond it (residual paired gains an order of magnitude smaller,
  though still statistically resolvable — disclosed, not hidden). *Residual:* a single fixed budget, applied
  identically across arms — matched-compute by construction, read "at the measured knee", not "at convergence";
  the seed-level dispersion of the curve fans out with budget, so the campaign's in-ladder σ_D re-estimate
  recalibrates power expectations at the new budget (the seed ladder's rung structure absorbs any shortfall).
- **B.2.2 Reward-scale → effective-entropy confound.** In SAC the reward scale acts as inverse temperature
  [`haarnoja2018sac`], and `ent_coef="auto"` re-adapts to the normalised scale, so arms whose authored rewards
  differ in magnitude receive different effective entropy regularisation. *Mitigation:* uniform PopArt normaliser
  with realised-scale logging; a `popart`-disabled ablation of the frozen winners is reported in Chapter 6
  [FROM CAMPAIGN: ordering verdict]; residual disclosed.
- **B.2.3 Critic divergence.** A minority of candidate trainings exhibited critic-loss explosions — the
value-overestimation/divergence pathology that motivated the clipped double-Q estimator [`fujimoto2018td3`]. *Mitigation:*
  PopArt; a divergence diagnostic; the analysis is robust to excluding diverged candidates, which score poorly and
  lose selection regardless.
- **B.2.4 Single deterministic validation path.** Selection rests on one deterministic walk-forward path per
  (candidate, seed). *Mitigation:* the winner-seed ladder re-evaluation (up to n = 568) and PBO/DSR machinery; selection-stability
  reported.
- **B.2.5 Pretraining contamination ("profit mirage").** The designer has memorised financial history that
  includes the sealed era [`li2025profitmirage`]. *Mitigation:* date-blind anonymised integer-index arrays, the
  AST gate and train-split-only feedback make test-era knowledge structurally unreachable from the reward
  channel (§4.5). *Direction:* the residual era-nonspecific reward-shape prior is arm-identical and cancels in
  the between-arm contrast; it affects absolute levels only, which carry no inferential claim.
- **B.2.6 Authoring variance / unit of analysis.** The confirmatory contrast re-runs *one* selected reward
  program per arm across the seed set, so the paired-seed bootstrap carries training-seed variance only and
  estimates the difference between two *fixed* programs; strictly, its interval generalises to the selected
  programs rather than to the feedback condition as a whole. A different search draw could author different
  winners, and this authoring step is not resampled at the confirmatory stage, so the variance it contributes is
  not captured by the seed bootstrap. *Direction:* the channel-level claim is therefore carried not by $H_2$ — a
  program-level contrast — but by the report-only mechanism kernel (responsiveness, mediation and the program
  taxonomy, §6.5), which is computed across *all* authored candidates and so does sample the authoring step; the
  two are reported as such.
- **B.2.7 The plain placebo announces its own inertness.** The inert block is introduced to the designer as
  "Reference constants (inert; no diagnostic content):" — it does not merely carry uninformative numbers, it
  *instructs the model to disregard them*. The wording is deliberate: six zero-valued lines without it would read
  as genuine diagnostics reporting a degenerate, riskless return distribution, which is active misinformation
  rather than truthful zero-information. The consequence is directional and is stated on both branches. For the
  registered *null* prediction the tell is conservative — it can only make the control easier to match, never
  manufacture a tie. On the *rejection* branch the sign inverts: an instruction to ignore the block plausibly
  suppresses any format or anchoring response, so part of a distributional-over-placebo win could reflect the
  tell rather than the tail *content*. *Mitigation:* the content claim is carried by `placebo_shuffled` — same
  intro line, real values deranged across their labels, byte-length matched, and carrying no such instruction —
  which is precisely why that arm and not plain placebo is the structure control promoted to node N5. Plain
  placebo is the coarser block-presence control and is never the sole evidence for a content claim.
- **B.2.8 Numeric resolution of the fed signal is a design parameter.** What the designer can perceive is bounded
  not by the measured statistics but by the precision at which they are *rendered into text*, and that rendering
  is part of the manipulation rather than an implementation detail. Both renderings were therefore set against
  the empirical distribution of the quantities they carry rather than by convention: the shared scalar header
  resolves the median observed fitness to three significant figures, and the six-line tail vector resolves better
  than 97% of genuinely-different value pairs on every field. *Residual:* rendering precision is a discrete
  design choice that was fixed pre-registration and not itself varied, so this study cannot separate "the model
  cannot use tail information" from "the model cannot use tail information *at this resolution*"; the legibility
  arm varies the *framing* of the same numbers (units and ordinal deciles) but not their precision, and a
  precision ladder is named as future work (B.7).

## B.3 The manipulation and the designer
- **B.3.1 Single confirmatory author.** The *confirmatory* verdicts rest on one frontier model (Opus 5, which
  superseded Opus 4.8 in this seat pre-launch — R102):
  the ten replication legs (R80/R95; ≥6 vendors, five open-weights with hash-pinned checkpoints) are
  report-only at the tier-30 floor, so cross-model claims are descriptive (the sign pattern, the pooled
  R86 bound, the capability gradient) — never confirmatory. *Direction:* generalisation beyond the
  confirmatory author is claimed only at the strength the legs' evidence class supports. *Disclosure:*
  the asymmetry (one confirmatory author vs ten descriptive legs) is a registered design choice, not a
  deviation.
- **B.3.2 Designer numeracy / responsiveness.** A negative responsiveness may reflect the documented weakness of
  language models on raw numerical magnitudes — a lineage running from embedding-era numeracy probes
  [`wallace2019numbers`] to benchmark-wide number-understanding failures in current frontier models
  [`yang2025cookbook`]. Three facts sharpen the interpretation: the failures are *format-dependent* —
  reformatting the same query alone switches the canonical 9.11 > 9.8 decimal-comparison bug on and off within
  a single model [`sandoval2025evenheads`]; they are mechanistically tied to *number tokenization*, which is why
  a close pair like −0.0577 vs −0.0582 is a worst case and basis-point integers repair it
  [`singh2024tokenization`]; and they dissociate from stated comprehension — models articulate the correct
  comparison rule yet fail to execute it [`zhang2025comprehension`]. Comparison failures that are real,
  format-dependent, and tokenization-rooted are exactly the hypothesis the pre-registered legible-format
  ablation tests. The negative sign is interpreted as the model editing on semantic/format cues rather than fed
  magnitudes, scoped to a frontier model so the null is not a small-model artefact.
- **B.3.3 Within-generation diversity and search width.** The campaign explores a deliberately *narrow* search —
  K=5 candidates per reflective generation across 6 generations (30 total) — and within-generation diversity rests
  on prompt-variation (temperature rejected for the campaign provider); if K-sampling collapses, the matched
  30-candidate budget overstates effective search. A wider K is identified as future work; the narrow width is a
  scope choice, disclosed, not a power claim.
  *Mitigation:* a pairwise reward-source diversity / Quality-Diversity coverage report.
- **B.3.4 Prompt portability across replication legs.** The ten legs receive the SAME
  Opus-calibrated prompts; industrial meta-prompting studies find prompts tuned on one model can
  degrade 20-30% on another [`meta-prompting-industrial` — verify at wiring], so part of any leg's
  shortfall may reflect instruction-format sensitivity rather than the tail-reading construct.
  *Mitigation:* the pre-launch compliance gate screens each leg's executable rate BEFORE results
  (format-incapable legs are excluded and disclosed, never scored); the SWE-bench-Verified anchor
  absorbs general instruction-following into the capability axis; identical prompts are the
  REPLICATION design (varying them per leg would confound the model axis with prompt tuning).

## B.4 External validity and data realism
- **B.4.1 Single universe / period / cohort.** US large-cap equities, 2020–2026H1 sealed leg, fixed 2005-cohort
  top-30 (a composition bias on the sealed leg). *Mitigation:* point-in-time walk-forward universe selections ship
  for a robustness re-evaluation; the bias is reported, not inherited.
- **B.4.2 Delisting surcharge (univ4).** The surcharged panel books a flat loss on all delistings including M&A
  exits, contrary to the source authors [`shumway1999delisting`]. *Mitigation — now MEASURED (ADR-051):* the
  headline panel is the conservative zero-fill (univ5); the executed observed-terminal recovery (univ5s,
  superseding the planned reason-gated re-pull) recovered the realised terminal return for all 333 dead names
  with zero surcharges booked, so the corrected panel is byte-identical to the zero-fill headline — the vendor
  series already carries each terminal, and univ4's flat surcharge was double-counting it on top of the M&A
  contamination. univ4 remains only the disclosed contaminated heavy end of the sensitivity band.
- **B.4.3 Transaction-cost realism.** A flat per-turnover cost understates the concave (square-root) market impact
  a daily-rebalancing agent incurs and ignores the rebalancing-frequency tax relative to monthly baselines
  [`almgren2005direct`; `frazzini2018trading`]. *Mitigation:* a square-root-impact cost-robustness sweep
  ($Y\in\{0.5,0.75,1.0\}$) and a per-benchmark turnover table; if the result survives $Y=1.0$ it is robust on cost
  grounds.
- **B.4.4 Action-space corner.** The softmax simplex cannot reach an exact cash position [`gaopavel2017softmax`].
  *Mitigation:* a diagnostic of how close the trained policy approaches cash in stress states; if it drives risky
  weight toward zero, the limitation is empirically non-binding. *Future work:* Dirichlet / simplex-decomposition
  parameterisations.
- **B.4.5 Risk-free rate.** Cash accrues at a zero rate in the headline — the ratified numeraire convention (rf = 0 is
  common-mode across the arms and cancels to first order in the Sharpe difference); a DGS3MO rf-excess robustness
  re-run of the family is reported to demonstrate, not assert, rf-invariance. *Direction:* under-
  rewards the cash-fleeing tail-aware arm in ZIRP periods — conservative against the hypothesis.

## B.5 Statistical inference
- **B.5.1 Power vs. SESOI (tier-conditional).** Equivalence power is a function of the seed rung the exogenous
  stopping rule (Amendment E1) actually reaches, not a single fixed value. At the tier-0 floor ($n=30$) the minimum
  detectable effect is ≈0.181 Sharpe ≈ 0.120 DSR at 80% power (≈0.141 DSR at 90%) — larger than the smallest effect
  of interest (0.05 DSR), so the floor is equivalence-*underpowered* and a non-rejection there reads "inconclusive"
  rather than "equivalent". The winner-seed ladder is designed to cross that threshold: rungs **279 / 340 / 403 / 568**
  deliver **80% / 90% / 95% (the primary target) / 99%** equivalence assurance, powering the ±0.05 SESOI at the
  χ²-upper confidence bound on σ_D (`power_analysis.ASSURANCE_TIER_BOUNDS`). A truncated run banks the largest
  completed rung, so the reported power is always the achieved-rung power, stated explicitly. Independently of the
  rung, a non-rejection licenses "equivalent" only if the TOST interval lies inside ±0.05, otherwise "inconclusive"
  [`lakens2017equivalence`]; the conservative Šidák ($m=6$, two-sided) sensitivity this rule superseded as the gate
  is higher still (≈0.257 Sharpe). Disclosed; the calibrated, tier-conditional statement is reported.
- **B.5.2 ES-backtest power and heavy tails.** Comparative Expected-Shortfall backtests are low-powered on
  multi-year windows [`du2017backtesting`], and the Diebold–Mariano statistic is oversized under heavy-tailed loss
  differentials irrespective of sample size [`heavytailsDM2026`], which the Harvey–Leybourne–Newbold
  small-sample correction does not fix. *Mitigation:* the autocorrelation-robust headline is the stationary-bootstrap p-value, which does not invoke the
  Diebold–Mariano asymptotics; the DM-HLN test is reported only as a companion with a size/power calibration, and
  the tail-index of the FZ0 loss differential is examined at the results stage to flag any heavy-tailed size
  distortion of that companion.
- **B.5.3 CSCV/PBO bias regimes.** Combinatorially symmetric cross-validation is negatively biased when mean
  returns are near zero [`witzany2021bayesian`] — the regime a near-null channel occupies. *Mitigation:* PBO is
  cross-checked against the Deflated-Sharpe ratio; the regime is disclosed.
- **B.5.4 Deflated-Sharpe effective trials.** The Deflated-Sharpe trial count assumes independent trials; guided
  reflective search produces correlated candidates, so the effective count is smaller and is reported alongside the
  nominal one.
- **B.5.5 One-sided p construction.** The one-sided headline p is the directly-computed upper-tail bootstrap
  probability (R64). The earlier construction — halving a two-sided re-centred bootstrap p — assumed
  bootstrap-null symmetry and departs from the true one-sided tail whenever the CVaR-difference bootstrap is
  asymmetric (over- or under-stating it according to the skew direction, which is unmeasured), so it is
  superseded by the direct upper-tail probability, which is valid under any skew, and retained at most as a
  sensitivity note.
- **B.5.6 Descriptive conventions.** Annualised Sharpe assumes i.i.d. returns [`lo2002statistics`] and is used
  descriptively only — all inference is the per-seed paired bootstrap. The measured seed-pairing correlation
  ($\rho=-0.141$) is not significantly different from zero; it is a methods note on the CRN design's realised
  efficiency, not evidence about the channel.
- **B.5.7 Single-look sealed test.** The sealed 2020–2026H1 window is evaluated once, at the exogenous
  assurance-ladder rung achieved; per-regime slices of that window are reported descriptively and are never
  re-tested. *Rationale:* a single pre-registered look is what makes the sealed leg a severe test rather than a
  second search space.

## B.6 Reproducibility and process
- **B.6.1 Language-model non-determinism.** Generation is non-reproducible (version drift; floating-point
  non-determinism) [`yuan2025nondeterminism`]. *Mitigation:* the replay-from-archive contract;
  the analysis (not the generation) is the reproducible object.
- **B.6.2 Fixed-device byte-identity.** The parallel==serial byte-identity holds on a fixed device, not across
  hardware. Disclosed.
- **B.6.3 Proposal re-scoping.** The submitted research question is a supervisor-approved *change of research
  question* from the approved proposal, not a narrowing; disclosed in full with the proposal's original components
  named as future work, pending the supervisor's written sign-off.
- **B.6.4 Pre-registration provenance.** The frozen design was refined in light of a *directional, non-confirmatory*
  prototype; the sealed leg was never touched in that process. The freeze is timestamped before the confirmatory
  run, and the directional pilot is disclosed as corroborating, not causal, to the design.
- **B.6.5 H1 descriptive-only.** The beat-the-human comparator is selected on the same sealed leg it is reported on
  (a data-snoop); H1 carries no inferential claim and is marked descriptive throughout.
- **B.6.6 The prototype is not evidence.** A single-seed Sonnet prototype (≈18 h) shaped engineering and
  directional expectations only; no prototype number appears anywhere in the results or informs any
  confirmatory conclusion.

## B.7 Future work (from the disclosed limitations)
A tail-rewarded ($\lambda>0$) selection variant (B.1.2); the reason-gated delisting re-pull univ4r (B.4.2); a
corner-reaching action parameterisation (B.4.4); a second, open-weights model family and a second universe/period
(B.3.1, B.4.1); a reward-distance
(EPIC/STARC beyond the reported differential) deep-dive, Quality-Diversity search diversity, and a
hierarchical-Bayesian re-analysis. (The Model-Confidence-Set comparison, the triangulated
Bayesian-and-frequentist null evidence, mediation, and the regime-conditional and synthetic-null exhibits
are BUILT instruments reported in Chapter 6 — they are results slots, not future work.)
