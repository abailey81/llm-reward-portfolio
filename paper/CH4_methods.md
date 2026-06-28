# Chapter 4 — Methods

> **Status: DRAFT v1 (2026-06-27), publication-standard.** Describes the *frozen confirmatory* design (the
> directional prototype that motivated it is Chapter 5). Each design element is paired with the failure mode it
> guards, because under PDF-only assessment the rigour must be made legible rather than left implicit. Numerical
> parameters reflect the pre-registered configuration; citation keys are in the verified backbone
> (`01_LITERATURE_DOSSIER.md`).

## 4.1 Design logic

The experiment is engineered so that one causal claim can be cleanly identified: *does the content of the feedback
shown to an automated reward-designer change the rewards it writes, and the behaviour they induce?* Everything in
this chapter follows from three commitments. First, a **single manipulated variable**: across the language-model
arms, the agent, the data, the candidate budget, the prompts, the selection rule and the evaluation are held
byte-identical, and *only the feedback block* differs (§4.5). Second, a **three-way estimator decoupling**: the
tail signal is *fed* on the training split, candidates are *selected* on a tail-blind validation criterion, and the
hypothesis is *tested* on a sealed split with a different estimator (§4.6), so a tail effect cannot be an artefact
of a tail-favouring selector or a self-grading metric. Third, **pre-commitment**: the hypotheses, family, splits,
budget, controls and analysis plan are frozen by a cryptographic hash before the sealed leg is touched (§4.8).
Together these convert the study from a demonstration into a controlled, falsifiable test.

## 4.2 Data: a survivorship-free, point-in-time equity panel

The market data are a licensed Refinitiv/LSEG panel of daily total returns for a survivorship-free, point-in-time
(PIT) universe of US-listed equities (953 securities over 5,283 trading days, 2005–2025). Survivorship-free
construction is essential: truncating a sample to surviving names induces spurious predictability strong enough to
fabricate performance [`brown1992survivorship`; `kothari1995another`], and PIT membership ensures no security
enters the tradable set before it was actually constituent. From this universe we select the top thirty names by
PIT market capitalisation as of the development date and hold that action space fixed across train, validation and
test. Fixing the cohort is a deliberate, disclosed trade-off (Chapter 7): it guarantees a consistent action space
but means the sealed leg trades a development-era cohort, a composition bias we report rather than inherit.

**Splits and leakage control.** The panel is partitioned into a training split (2005–2014, on which the agent
learns and the fed tail signal is measured), a validation split (2015–2017, on which candidate rewards are
selected), and a **sealed test split (2018–2025)**, which is untouched until final inference and spans a genuine
regime shift (the 2020 COVID drawdown; the 2022 bear market and rate shock). At every split boundary we apply a
purge of $\max(\text{embargo}=21,\ \text{lookback}=60)=60$ trading sessions, following the purged/embargoed
cross-validation discipline of López de Prado: the purge must cover the *feature lookback*, not merely a nominal
embargo, so that no observation's feature window straddles a boundary [`lopezdeprado2018afml`]. The
no-look-ahead property is unit-tested adversarially — corrupting all rows at or after a decision row leaves the
constructed observation byte-identical — rather than merely asserted.

**Delisting returns.** Delisted names are handled by a `liquidate_to_cash` (zero-fill) policy, the **headline
panel**, which *understates* rather than *invents* the delisting tail and is therefore the conservative, honest
choice for a tail-risk study. We deliberately do **not** headline the survivorship-corrected variant that books
Shumway delisting returns (−30% NYSE/AMEX, −55% NASDAQ) [`shumway1997delisting`; `shumway1999delisting`], because
the corpus carries no delisting *reason* and the surcharge is therefore applied indiscriminately — including to
premium merger-and-acquisition exits, which the source authors explicitly exclude from performance-related
delistings [`shumway1999delisting`]. Booking fabricated left-tail losses on M&A exits in a study whose object is
the left tail would be indefensible. Instead, the Shumway surcharge is retained as the heavy end of a disclosed
**delisting-return sensitivity band** $d\in\{0,-30,-55,-100\%\}$ over the affected cells; the band moves the pooled
test CVaR-5% by approximately two percentage points, leaving the hypothesis ordering invariant.

**State features.** The agent's cash-row state carries three leakage-safe volatility/regime features — 20-day
realised volatility, the 20-day/60-day volatility ratio, and the VIX close — following the tail-feature
construction of Sood et al. [`sood2023deep`]. All rolling statistics are computed on returns through $t{-}1$ (an
explicit one-step shift), and the VIX value at row $t$ is the $t{-}1$ close, so every feature at a decision is a
function of strictly prior information. No security identifiers or calendar dates ever enter the agent's
observation or any reward (the arrays are anonymised to integer indices), which both prevents date/ticker leakage
and is a precondition of the untrusted-code sandbox (§4.5).

## 4.3 The fixed reinforcement-learning agent

The agent is a Soft Actor–Critic learner [`haarnoja2018sac`; `haarnoja2019applications`], implemented in
Stable-Baselines3 [`raffin2021sb3`], held byte-identically fixed across all arms — it is the constant against which
the feedback channel is varied. It observes the lookback window of asset returns plus the cash-row regime features
and outputs portfolio weights over the thirty assets and a cash position via a softmax simplex parameterisation
(long-only, fully invested). The softmax image is the *open* simplex, so an exact all-cash corner is provably
unreachable [`gaopavel2017softmax`]; we adopt this conventional parameterisation [`jiang2017eiie`] and treat the
unreachable corner as a disclosed limitation, reporting how close the trained policy approaches cash in stress
states and citing the corner-reaching alternatives (Dirichlet policies, simplex decomposition) as future work
[`andre2020dirichlet`; `winkel2024simplex`]. Each candidate reward trains the agent for a fixed budget of 50,000
environment steps, and evaluation is a single deterministic walk-forward rollout over the relevant split, the
standard backtest protocol [`sood2023deep`]. The window edge is treated as a time-limit *truncation* rather than an
absorbing *termination*, so the critic's value bootstrap is not spuriously zeroed once per episode.

Two features manage reward-scale heterogeneity, which is a genuine confound because in SAC the reward scale plays
the role of the inverse temperature and thus governs exploration [`haarnoja2018sac`, §5]: arms whose
language-model-authored rewards differ in natural magnitude would otherwise receive different *effective* entropy
regularisation under automatic temperature tuning. We therefore apply a PopArt value-target normaliser uniformly
across arms [`vanhasselt2016popart`] — which preserves the realised-return series exactly, so the analysed
quantities are byte-identical with and without it — and log the realised per-candidate normalisation scale, with a
one-seed `popart`-disabled ablation confirming the hypothesis ordering is preserved. A truncated-quantile critic
[`kuznetsov2020tqc`] is run as a *named secondary* experiment (mean critic vs. quantile critic), not as the
contribution, which lives in the off-critic feedback channel. We disclose, rather than conceal, a training-adequacy
limitation: 50,000 steps is well below the budgets at which SAC converges on comparable continuous-control problems
(Chapter 7), and we therefore present a convergence/learning-curve diagnostic and interpret arm differences as
differences *at a fixed, matched budget*.

## 4.4 The off-critic measurement instrument

The fed signal is produced by a separate estimator that reads only the *realised returns* of the policy on the
training split — it touches no value network, which is the precise sense of **off-critic**, and is what makes the
instrument agnostic to the agent's architecture. The estimator returns a six-component vector: conditional
value-at-risk at the 5%, 10%, 25% and 1% levels, the left-tail mass beyond −2σ, and a robust left-tail skew. The
5% and 1% levels are estimated with an extreme-value (generalised-Pareto) peaks-over-threshold fit
[`pickands1975statistical`; `balkema1974residual`; `smith1987estimating`; `mcneil2000estimation`], with the inner
levels taken empirically; a guard falls back to the empirical estimate in the non-regular shape region
$\xi\le-0.5$ where the maximum-likelihood estimator is unreliable [`smith1985maximum`]. We disclose the
finite-sample fragility of an extreme-value tail on a few hundred observations [`belzile2020improved`;
`cont2010robustness`] and treat the fed CVaR as a noisy signal whose noise biases *against* detecting a channel
effect. The theoretical justification for feeding this particular vector — that it is a sufficient, jointly
elicitable representation of the coherent-risk class — is developed in Chapter 3.

## 4.5 The reward-designer and the experimental arms

The reward-designer is a frontier language model (Claude Opus 4.8 in the confirmatory campaign; Claude Sonnet 4.6
in the prototype) operating in an Eureka-style reflect-and-improve loop [`ma2024eureka`]: it authors a
reward-function as Python code, the agent is trained and evaluated, a feedback block is composed, and the model
revises the code. The loop runs six generations of five candidates under a matched budget of thirty candidates per
arm, reflecting on the generation's best candidate. The study uses a single model family throughout, so claims are
scoped to that family rather than to "language models" in general (Chapter 7).

There are **seven arms**. The five language-model arms are identical in every respect — same agent, budget,
prompts, selection and evaluation — and differ *only* in the feedback block: **distributional** receives the full
six-component tail vector; **scalar** receives only the held-out risk-adjusted score; **placebo** receives an inert
block matched to the distributional block in length and field-count; **scalar_cvar5** receives the scalar plus a
single CVaR-5% number; and **placebo_shuffled** receives the distributional block's exact structure with the tail
*values deranged*. Two non-language-model search baselines complete the design: **random_search** samples reward
code from a shared parametric family, and **bayes_opt** performs Gaussian-process expected-improvement optimisation
over the family's coefficients [`snoek2012practical`]. The control ladder is constructed to defend named threats to
construct validity [`shadish2002experimental`]: the placebo isolates the effect of *receiving any feedback* from
the effect of its *content* (a demand/placebo confound); scalar_cvar5 isolates *multi-level tail shape* from *any
single downside number*; and placebo_shuffled — structurally identical, informationally destroyed — isolates the
*information* in the tail from its *format*, defending against confounding the construct with its presentation.

Because the reward code is authored by an untrusted model, it is treated as untrusted input: each candidate is
screened once by an abstract-syntax-tree allowlist gate (no imports beyond numerical primitives; no attribute or
name reaching the file system, network or process) and then executed in-process on anonymised, read-only arrays,
so a candidate can neither exfiltrate information nor corrupt shared state across candidates. No tickers or dates
are reachable by construction.

## 4.6 Selection, fitness, and the three-way decoupling

Candidate rewards are selected on a **validation Deflated Sharpe ratio with risk-aversion weight $\lambda=0$** —
that is, a *tail-blind* risk-adjusted criterion. This is a deliberate, conservative choice: the selector gives no
advantage to tail-aware rewards, so any tail effect observed downstream must arise endogenously from the
designer's *use* of the fed signal rather than from selection pressure. The deflation corrects the selected
Sharpe for the multiplicity and non-normality of the search [`bailey2014deflated`]. The resulting **three-way
decoupling** is the methodological core: the tail is *fed* by the extreme-value estimator on the *training* split;
candidates are *selected* by the tail-blind Deflated Sharpe on the *validation* split; and the hypothesis is
*tested* by the empirical CVaR on the *sealed test* split. Because the object fed is neither the object selected on
nor the estimator graded by, a tail effect is attributable to the feedback channel and cannot be a self-grading
artefact. The decoupling is unit-tested at the split boundaries.

## 4.7 Hypotheses and the pre-registered inference plan

Four hypotheses are pre-registered. **H1** (beat-the-human) asks whether the best language-model reward beats the
maximum over four hand-designed rewards on the sealed leg; because the baselines are selected on the same sealed
leg they are reported on, H1 carries a comparator data-snoop and is reported as **descriptive only**, not as an
inferential claim. **H2**, the headline, is the feedback-channel contrast. **H3** asks whether iterative reflection
beats single-shot best-of-N at matched budget; **H4** asks whether the language-model designer beats the
random-search and Bayesian-optimisation baselines.

**H2 is two co-primary intersection–union tests.** *H2-RA* asks whether the distributional arm matches the
comparison arms on risk-adjusted return (a Sharpe contrast); *H2-Tail* asks whether it improves the realised left
tail (a CVaR-5% contrast). Each is an intersection–union test over three legs — distributional versus *scalar*,
*placebo* and *scalar_cvar5* — one-sided at $\alpha=0.05$. The intersection–union construction *is* the
multiplicity correction (the conjunction has size $\le\alpha$ by the union–intersection principle), which is why no
further per-leg correction is applied and a Benjamini–Hochberg correction over the six legs is demoted to a
reported sensitivity rather than the primary rule. The structure-shuffled arm enters as a **disjoint** control,
never as a fourth leg of the conjunction.

Inference is **per-seed and aggregate-robust**, following the reinforcement-learning evaluation standard
[`agarwal2021rliable`]: each arm is re-run at **thirty random seeds**, each seed's score is reduced to an
interquartile mean, and contrasts are tested by a paired stratified bootstrap over shared seeds, carrying the
across-seed variance rather than the anti-conservative within-path variance. The realised left tail is
corroborated by a comparative Expected-Shortfall backtest using the jointly-elicitable Fissler–Ziegel (FZ0) loss
with a Diebold–Mariano comparison and the Harvey–Leybourne–Newbold small-sample correction
[`fisslerziegelgneiting2015`; `patton2019dynamic`; `harvey1997testing`], reported with a size/power calibration and
the explicit caveat that Expected-Shortfall comparative backtests are low-powered on multi-year windows
[`du2017backtesting`]. Overfitting is bounded by the **probability of backtest overfitting** via combinatorially
symmetric cross-validation over the full enumeration of block partitions, which is trial-count-free and serves as
the primary overfitting guard [`bailey2017pbo`]; we disclose the known regimes in which it is biased
[`witzany2021bayesian`]. A pre-registered factor-attribution (CAPM through a six-factor model with Betting-Against-
Beta and Quality-Minus-Junk, Newey–West standard errors) rules out the headline being a low-volatility beta
[`frazzini2014bab`; `asness2019qmj`; `newey1987simple`].

The smallest effect size of interest is **0.05 Deflated-Sharpe units**, and a symmetric two-one-sided-tests
equivalence margin of $\pm0.05$ is pre-registered so that a non-rejection can be reported as a bounded equivalence
rather than an underpowered failure [`lakens2017equivalence`]. A power analysis places the minimum detectable
effect at 80% power at approximately 0.256 in Sharpe units (≈0.177 in Deflated-Sharpe units after the conservative
delta-method conversion); we disclose honestly that this exceeds the smallest effect of interest, so a clean
equivalence claim rests on the equivalence interval and is otherwise reported as inconclusive — the calibrated, not
the convenient, statement. Cross-hypothesis multiplicity is handled by treating H1–H4 as separate pre-registered
estimands with a reported Bonferroni-across-four sensitivity rather than a single forced family.

## 4.8 Pre-registration, provenance and reproducibility

The full design — hypotheses, the seven arms, the candidate and seed budgets, the splits and embargo, the frozen
tail-diagnostic set, the benchmark suite and the analysis plan — is recorded in a pre-registration document and
frozen by a SHA-256 hash over the declaration files before the sealed leg is evaluated; the campaign driver refuses
to run against an unfrozen or drifted design. Any post-freeze departure is recorded in an append-only deviations
log, so the frozen document remains a true record of what was committed in advance and the log a true record of
what actually happened. This is, to our knowledge, the first explicit pre-registration of a language-model
reward-design study (Chapter 2).

Reproducibility is treated in two distinct regimes, because conflating them is the usual error. The **analysis** is
computationally reproducible: the full stochastic stack is seeded, the parallel and serial execution paths are
proven byte-identical on a fixed device, and every result replays deterministically from the archive. The
**language-model generation** is *provably not* reproducible: model behaviour drifts across versions
[`chen2023chatgpt`], and floating-point non-associativity makes inference non-deterministic even at fixed version
and temperature on commodity hardware [`yuan2025nondeterminism`]. We therefore adopt a *replay-from-archive*
contract: every prompt, authored reward and feedback block is archived at generation time with byte-level
tamper-evidence, and downstream results are computed by *replaying* the archive, never by regenerating it. This
converts the loop's least reproducible component into a documented, literature-grounded design decision. The data
are accompanied by a datasheet and each model in the loop by a model card [`gebru2021datasheets`;
`mitchell2019modelcards`], and the study is reported against a machine-learning-for-science reporting standard
whose central concern — leakage — the design directly addresses [`kapoor2023leakage`].

---

### Citation keys introduced in this chapter (add to `refs.bib` from the verified backbone)
`brown1992survivorship`, `kothari1995another`, `lopezdeprado2018afml`, `shumway1997delisting`,
`shumway1999delisting`, `sood2023deep`, `haarnoja2018sac`, `haarnoja2019applications`, `raffin2021sb3`,
`gaopavel2017softmax`, `jiang2017eiie`, `andre2020dirichlet`, `winkel2024simplex`, `vanhasselt2016popart`,
`kuznetsov2020tqc`, `pickands1975statistical`, `balkema1974residual`, `smith1987estimating`, `mcneil2000estimation`,
`smith1985maximum`, `belzile2020improved`, `cont2010robustness`, `ma2024eureka`, `snoek2012practical`,
`shadish2002experimental`, `bailey2014deflated`, `agarwal2021rliable`, `fisslerziegelgneiting2015`,
`patton2019dynamic`, `harvey1997testing`, `du2017backtesting`, `bailey2017pbo`, `witzany2021bayesian`,
`frazzini2014bab`, `asness2019qmj`, `newey1987simple`, `lakens2017equivalence`, `chen2023chatgpt`,
`yuan2025nondeterminism`, `gebru2021datasheets`, `mitchell2019modelcards`, `kapoor2023leakage`.
