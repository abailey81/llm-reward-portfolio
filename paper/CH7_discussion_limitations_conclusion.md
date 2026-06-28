# Chapter 7 — Discussion, Limitations, and Conclusion

> **Status: DRAFT v1 (2026-06-27), publication-standard.** §7.1 (Discussion) and §7.3 (Conclusion) are in-body
> (~1,000 + ~250 words); §7.2 foregrounds the four load-bearing limitations in-body and refers to the
> **Limitations Register (Appendix B)**, reproduced in full below the in-body chapter and marked *word-excluded*
> so the disclosure strategy survives the 10,000-word limit. The result is framed as a pre-registered boundary
> condition; finalise the one bracketed sentence in §7.1 from the confirmatory campaign.

---

## 7.1 Discussion

This dissertation set out to test whether the *content* of the feedback shown to an automated reward-designer —
specifically, the realised-return lower tail rather than a scalar summary — changes the risk-sensitive reward code
a language model writes and the behaviour it induces. The theory of Chapter 3 establishes the strongest claim that
is honestly available: an *optimal* user of the multi-level tail vector weakly dominates an optimal user of the
scalar, for every loss and prior, because the scalar is a measurable garbling of the vector. That dominance is an
*envelope*, not a guarantee, and the empirical contribution is to measure how much of it a *bounded* realisation —
a finite-capacity language model coupled to a fixed, capacity-limited agent under tail-blind selection — actually
attains.

**[Result — finalise from the confirmatory campaign.]** The directional prototype, read through the theory,
locates the realised system on the *Null* branch of the pre-registered prediction table: the apparent tail
advantage did not survive its own zero-information placebo control, and the model's authored reward code was, if
anything, *less* responsive to larger movements in the fed tail. We therefore report a pre-registered boundary
condition rather than a performance claim. Three readings make this a positive scientific result rather than an
absence of evidence.

First, it is a *corroborated prediction about the envelope–realisation gap*. The theory predicts exactly this
outcome under the study's two design facts — a tail-blind selector ($\lambda=0$) gives the channel no exogenous
help, and a non-responsive designer supplies none endogenously — so the null confirms the mechanism account of
§3.7 rather than contradicting the dominance result of §3.4. The information an optimal user could exploit exists;
the tested system does not exploit it. Second, by the CVaR–robustness duality of §3.6, the finding is a statement
about *distributional-robustness information*: feeding the lower tail is feeding a robustness signal, and the null
says this particular automated designer does not convert that signal into more robust reward code at the studied
budget. Third — and most useful to the field — the result is a *boundary condition for the automated-discovery
agenda*. That agenda has shown, by demonstration, that language models can discover objectives; this study shows,
under controlled and pre-registered conditions, that *which information they are shown* did not, here, change what
they discovered. The contribution is not the sign of an effect but a calibrated, falsifiable instrument for asking
the question — and the discovery that, on a clean test, the optimistic reading does not hold.

The mechanism analyses sharpen the interpretation rather than merely supporting it. The reward-program differential
(Chapter 6) measures, using the regret-bounded EPIC/STARC pseudometrics, whether the authored rewards genuinely
differ across feedback arms or are near-policy-invariant re-shapings of one objective; the mediation analysis
estimates responsiveness as the indirect effect of the feedback arm through the authored code and interprets a
negative estimate as *inconsistent mediation (suppression)* — a recognised, identifiable quantity, not a failed
manipulation. Read together, they convert "we observed no headline effect" into a mechanistic statement: the
channel is present, the selector is deliberately blind to it, and the designer does not route it into the reward
code in the value-adding direction. For practitioners of automated reward design the implication is concrete:
richer feedback is not self-acting. Realising the dominance envelope requires *both* a selection objective that
rewards the fed dimension and a designer that demonstrably conditions on its content — neither of which a default
Eureka-style loop with a tail-blind fitness supplies.

## 7.2 Limitations

We foreground the four limitations most likely to bound the result's interpretation; the full register is
Appendix B. **(i) Construct.** The fed signal is six left-tail scalars, not the full return distribution; we name
it *multi-level tail-risk feedback* throughout and claim only that it spans the coherent-risk class (Chapter 3),
making no claim about upside or non-coherent features. **(ii) Training adequacy.** The fixed agent is trained for
50,000 steps, well below SAC's convergence regime on comparable problems; arm differences are therefore differences
*at a matched budget*, and we present a learning-curve diagnostic rather than asserting convergence. **(iii)
Selection blindness.** The selector is deliberately tail-blind ($\lambda=0$); this is what makes a tail effect
attributable to the channel, but it also places the study on the boundary of the Null branch, so the result speaks
to *this* (conservative, identifiable) configuration and not to a tail-rewarded selector. **(iv) External
validity.** One universe of US large-cap equities, one historical window, and one language-model family: the study
claims a boundary condition for that instance and, in particular, cannot earn the plural "language models" — every
quantitative claim is scoped to the single tested family. Each of these is a deliberate, disclosed design decision
with a documented rationale, not a hidden assumption; the register below records the remainder with the same
candour.

## 7.3 Conclusion

The dissertation contributes an instrument, a protocol, and a theory for a question the automated-discovery agenda
has been unable to ask cleanly: does the information content of the feedback to an automated objective-designer
change the objectives it discovers? The instrument feeds a language-model reward-designer the realised-return lower
tail off-critic while holding the agent fixed; the protocol submits the resulting comparison to a frozen,
family-wise-controlled, pre-registered test with placebo and structure-shuffled controls; and the theory bounds
what an optimal user of that feedback could achieve and states the conditions under which a bounded realisation
attains it. The empirical finding is a pre-registered boundary condition — that, under tail-blind selection and at
the studied budget, multi-level tail-risk feedback did not change the tested model's risk-sensitive reward code in
the value-adding direction — which the theory predicts and the mechanism analyses localise. A clean, controlled
null on a question the field has answered only by optimistic demonstration is the contribution: it replaces a
plausible intuition with a calibrated measurement, and it leaves a reusable, pre-registered instrument with which
the conditions identified here — a tail-rewarded selector, a demonstrably responsive designer, a converged agent,
and a second model family — can each be tested in turn.

---
---

# Appendix B — Limitations Register *(word-excluded)*

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
  the $\xi\le-0.5$ guard; a bootstrap error bound on the fitted tail is reported.

## B.2 Internal validity (whether the comparison is clean)
- **B.2.1 Training adequacy / undertraining.** 50,000 steps is ~20–60× below SAC's reported convergence budgets on
  comparable continuous control. *Mitigation:* a learning-curve diagnostic; results framed as matched-budget;
  disclosed, not asserted-away.
- **B.2.2 Reward-scale → effective-entropy confound.** In SAC the reward scale acts as inverse temperature
  [`haarnoja2018sac`], and `ent_coef="auto"` re-adapts to the normalised scale, so arms whose authored rewards
  differ in magnitude receive different effective entropy regularisation. *Mitigation:* uniform PopArt normaliser
  with realised-scale logging and a `popart`-disabled ablation showing the ordering is preserved; residual
  disclosed.
- **B.2.3 Critic divergence.** A minority of candidate trainings exhibited critic-loss explosions. *Mitigation:*
  PopArt; a divergence diagnostic; the analysis is robust to excluding diverged candidates, which score poorly and
  lose selection regardless.
- **B.2.4 Single deterministic validation path.** Selection rests on one deterministic walk-forward path per
  (candidate, seed). *Mitigation:* the 30-seed winner re-evaluation and PBO/DSR machinery; selection-stability
  reported.

## B.3 The manipulation and the designer
- **B.3.1 Single model family.** One Claude family (Sonnet 4.6 → Opus 4.8); the pre-registered open-weights
  second-model cross-check is *specified but unexecuted*. *Direction:* no plural "language models" claim is earned;
  scoped to the tested family. *Disclosure:* logged as a deviation.
- **B.3.2 Designer numeracy / responsiveness.** A negative responsiveness may reflect the documented weakness of
  language models on raw numerical magnitudes [`numeracy_cluster` `% VERIFY`]; the negative sign is interpreted as
  the model editing on semantic/format cues rather than fed magnitudes, scoped to a frontier model so the null is
  not a small-model artefact.
- **B.3.3 Within-generation diversity.** Campaign diversity rests on prompt-variation (temperature rejected for the
  campaign provider); if K-sampling collapses, the matched 30-candidate budget overstates effective search.
  *Mitigation:* a pairwise reward-source diversity / Quality-Diversity coverage report.

## B.4 External validity and data realism
- **B.4.1 Single universe / period / cohort.** US large-cap equities, 2018–2025 sealed leg, fixed 2005-cohort
  top-30 (a composition bias on the sealed leg). *Mitigation:* point-in-time walk-forward universe selections ship
  for a robustness re-evaluation; the bias is reported, not inherited.
- **B.4.2 Delisting surcharge (univ4).** The survivorship-corrected panel surcharges all delistings including M&A
  exits, contrary to the source authors [`shumway1999delisting`]. *Mitigation:* the headline panel is the
  conservative zero-fill (univ3); univ4 is the heavy end of a disclosed sensitivity band; the reason-gated re-pull
  (univ4r) is identified as the correct-on-re-pull ideal and named as future work.
- **B.4.3 Transaction-cost realism.** A flat per-turnover cost understates the concave (square-root) market impact
  a daily-rebalancing agent incurs and ignores the rebalancing-frequency tax relative to monthly baselines
  [`almgren2005direct`; `frazzini2018trading`]. *Mitigation:* a square-root-impact cost-robustness sweep
  ($Y\in\{0.5,0.75,1.0\}$) and a per-benchmark turnover table; if the result survives $Y=1.0$ it is robust on cost
  grounds.
- **B.4.4 Action-space corner.** The softmax simplex cannot reach an exact cash position [`gaopavel2017softmax`].
  *Mitigation:* a diagnostic of how close the trained policy approaches cash in stress states; if it drives risky
  weight toward zero, the limitation is empirically non-binding. *Future work:* Dirichlet / simplex-decomposition
  parameterisations.
- **B.4.5 Risk-free rate.** Cash accrues at a zero rate in the headline (rf threading pending). *Direction:* under-
  rewards the cash-fleeing tail-aware arm in ZIRP periods — conservative against the hypothesis.

## B.5 Statistical inference
- **B.5.1 Power vs. SESOI.** The minimum detectable effect (≈0.177 DSR at 80%) exceeds the smallest effect of
  interest (0.05 DSR); a non-rejection licenses "equivalent" only if the TOST interval lies inside ±0.05,
  otherwise "inconclusive" [`lakens2017equivalence`]. Disclosed; the calibrated statement is reported.
- **B.5.2 ES-backtest power and heavy tails.** Comparative Expected-Shortfall backtests are low-powered on
  multi-year windows [`du2017backtesting`], and the Diebold–Mariano statistic is oversized under heavy-tailed loss
  differentials irrespective of sample size [`heavytailsDM2026` `% VERIFY`], which the Harvey–Leybourne–Newbold
  small-sample correction does not fix. *Mitigation:* the tail-index of the FZ0 loss differential is checked; the
  stationary-bootstrap p-value is the autocorrelation-robust headline and the DM-HLN test is reported as a
  companion with a size/power calibration.
- **B.5.3 CSCV/PBO bias regimes.** Combinatorially symmetric cross-validation is negatively biased when mean
  returns are near zero [`witzany2021bayesian`] — the regime a near-null channel occupies. *Mitigation:* PBO is
  cross-checked against the Deflated-Sharpe ratio; the regime is disclosed.
- **B.5.4 Deflated-Sharpe effective trials.** The Deflated-Sharpe trial count assumes independent trials; guided
  reflective search produces correlated candidates, so the effective count is smaller and is reported alongside the
  nominal one.
- **B.5.5 One-sided p via halving.** The one-sided headline p is obtained by halving a two-sided re-centred
  bootstrap p, which assumes bootstrap-null symmetry; a null-calibration shows the resulting size is ≈0.05–0.06,
  and the directly-computed one-sided tail is reported as a sensitivity.

## B.6 Reproducibility and process
- **B.6.1 Language-model non-determinism.** Generation is non-reproducible (version drift; floating-point
  non-determinism) [`chen2023chatgpt`; `yuan2025nondeterminism`]. *Mitigation:* the replay-from-archive contract;
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

## B.7 Future work (from the disclosed limitations)
A tail-rewarded ($\lambda>0$) selection variant (B.1.2); the reason-gated delisting re-pull univ4r (B.4.2); a
corner-reaching action parameterisation (B.4.4); a second, open-weights model family and a second universe/period
(B.3.1, B.4.1); execution of the buildable mechanism and robustness analyses already specified (reward-distance,
Quality-Diversity diversity, hierarchical-Bayesian re-analysis, Model-Confidence-Set arm comparison, triangulated
Bayesian-and-frequentist null, mediation, regime-conditional and synthetic-null exhibits).

---

### Citation keys introduced in this chapter (add to `refs.bib` from the verified backbone)
`shadish2002experimental`, `belzile2020improved`, `cont2010robustness`, `giles2016biascorrected`, `haarnoja2018sac`,
`shumway1999delisting`, `almgren2005direct`, `frazzini2018trading`, `gaopavel2017softmax`, `lakens2017equivalence`,
`du2017backtesting`, `witzany2021bayesian`, `chen2023chatgpt`, `yuan2025nondeterminism`, `numeracy_cluster`
(`% VERIFY`), `heavytailsDM2026` (`% VERIFY`).
