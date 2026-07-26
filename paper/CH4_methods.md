# Chapter 4 — Methods

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
(PIT) universe of US-listed equities (963 securities over 5,406 trading days, 2005 to end-June 2026). Survivorship-free
construction is essential: truncating a sample to surviving names induces spurious predictability strong enough to
fabricate performance [`brown1992survivorship`; `kothari1995another`], and PIT membership ensures no security
enters the tradable set before it was actually constituent. From this universe we select the top thirty names by
PIT market capitalisation as of the development date and hold that action space fixed across train, validation and
test. Fixing the cohort is a deliberate, disclosed trade-off (Chapter 7): it guarantees a consistent action space
but means the sealed leg trades a development-era cohort, a composition bias we report rather than inherit.

**Stylised tail facts.** The training-window distribution is itself the motivation for a *multi-level* tail signal
(Figure 4.1). The cross-section is strongly leptokurtic (excess kurtosis $\approx 15$), and its tail heaviness is
not uniform across levels: the ratio of empirical to Gaussian conditional shortfall crosses over from $0.84$ at
moderate levels, where a Gaussian *over*-states the loss, to $1.66$ deep in the tail, where it *under*-states it.
Co-movement compounds the danger — on the worst days close to one name in five crashes with the rest
($\approx 19.7\%$). A scalar measured at a single level cannot represent a tail whose severity relative to the
Gaussian benchmark reverses across quantiles; a vector of level-specific conditional shortfalls can — which is the
manipulated variable this study feeds its reward designer.

**Splits and leakage control.** The panel is partitioned into a training split (2005–2016, on which the agent
learns and the fed tail signal is measured), a validation split (2017–2019, on which candidate rewards are
selected), and a **sealed test split (2020 to end-June 2026)**, which is untouched until final inference and spans
a genuine regime set (the post-COVID-crash recovery and its elevated-volatility regime; the 2022 bear market and
rate shock; the 2023–25 rally and the settled first half of 2026). At every split boundary we apply a
purge of $\max(\text{embargo}=21,\ \text{lookback}=60)=60$ trading sessions, following the purged/embargoed
cross-validation discipline of López de Prado: the purge must cover the *feature lookback*, not merely a nominal
embargo, so that no observation's feature window straddles a boundary [`lopezdeprado2018afml`]. The
no-look-ahead property is unit-tested adversarially — corrupting all rows at or after a decision row leaves the
constructed observation byte-identical — rather than merely asserted. One boundary consequence is stated plainly:
the COVID crash itself (19 February–23 March 2020) falls *inside* the test-boundary purge, so the executed sealed
window opens on 30 March 2020, near the trough — capturing the recovery and its elevated-volatility regime, not
the drawdown episode. We disclose rather than engineer this: shifting the boundary to capture the crash would
trade away the leakage guarantee the purge exists for, and would let a single three-week episode dominate the
sealed CVaR estimand; the 2022 bear market — a slower, rate-driven left tail — remains fully in-window, and the
boundary is shared by all arms, so it cannot confound the between-arm contrast.

**Delisting returns.** Delisted names are handled by a `liquidate_to_cash` (zero-fill) policy, the **headline
panel**, which *understates* rather than *invents* the delisting tail and is therefore the conservative, honest
choice for a tail-risk study. We deliberately do **not** headline the survivorship-corrected variant that books
Shumway delisting returns (−30% NYSE/AMEX, −55% NASDAQ) [`shumway1997delisting`; `shumway1999delisting`], because
the corpus carries no delisting *reason* and the surcharge is therefore applied indiscriminately — including to
premium merger-and-acquisition exits, which the source authors explicitly exclude from performance-related
delistings [`shumway1999delisting`]. Booking fabricated left-tail losses on M&A exits in a study whose object is
the left tail would be indefensible. Instead, the Shumway surcharge is retained as the heavy end of a disclosed
**delisting-return sensitivity band** $d\in\{0,-30,-55,-100\%\}$ over the affected cells; across the full band the
pooled test CVaR-5% moves by only about two percent in relative terms (of order a tenth of a percentage point),
leaving the hypothesis ordering invariant.

**State features.** The agent's cash-row state carries three leakage-safe volatility/regime features — 20-day
realised volatility, the 20-day/60-day volatility ratio, and the VIX close — following the tail-feature
construction of Sood et al. [`sood2023deep`]. All rolling statistics are computed on returns through $t{-}1$ (an
explicit one-step shift), and the VIX value at row $t$ is the $t{-}1$ close, so every feature at a decision is a
function of strictly prior information. No security identifiers or calendar dates ever enter the agent's
observation or any reward (the arrays are anonymised to integer indices), which both prevents date/ticker leakage
and is a precondition of the untrusted-code sandbox (§4.5).

## 4.3 The fixed reinforcement-learning agent

The agent is a Soft Actor–Critic learner [`haarnoja2018sac`; `haarnoja2019applications`] — which curbs value
overestimation with the clipped double-Q (twin-critic minimum) introduced by TD3 [`fujimoto2018td3`] — implemented in
Stable-Baselines3 [`raffin2021sb3`], held byte-identically fixed across all arms — it is the constant against which
the feedback channel is varied. It observes the lookback window of asset returns plus the cash-row regime features
and outputs portfolio weights over the thirty assets and a cash position via a softmax simplex parameterisation
(long-only, fully invested). The softmax image is the *open* simplex, so an exact all-cash corner is provably
unreachable [`gaopavel2017softmax`]; we adopt this conventional parameterisation [`jiang2017eiie`] and treat the
unreachable corner as a disclosed limitation, reporting how close the trained policy approaches cash in stress
states and citing the corner-reaching alternatives (Dirichlet policies, simplex decomposition) as future work
[`andre2020dirichlet`; `winkel2024simplex`]. Each candidate reward trains the agent for a fixed budget of 400,000
environment steps, and evaluation is a single deterministic walk-forward rollout over the relevant split, the
standard backtest protocol [`sood2023deep`]. The window edge is treated as a time-limit *truncation* rather than an
absorbing *termination*, so the critic's value bootstrap is not spuriously zeroed once per episode. The replay
buffer is capped at 50,000 transitions for memory safety on the study's single-GPU hardware — well below the
canonical million-transition default [`haarnoja2018sac`]. Buffer size is a genuinely two-sided hyperparameter —
too small a buffer loses sample diversity, too large over-weights stale off-policy data [`zhang2017deeper`;
`fedus2020revisiting`] — but two properties make the cap benign here. Because every episode replays the same fixed
training calendar, a 50,000-transition window always retains roughly seventeen complete passes over the *entire*
training period, so the buffer never loses coverage of any region of the return history — only the oldest
policies' transitions age out; and the agent trains at the default replay ratio of one gradient step per
environment step, the conservative corner of the capacity–replay-ratio grid at which small buffers are least
harmful [`fedus2020revisiting`]. The cap is applied identically to every arm, so any residual effect is
common-mode rather than a channel confound.

Two features manage reward-scale heterogeneity, which is a genuine confound because in SAC the reward scale plays
the role of the inverse temperature and thus governs exploration [`haarnoja2018sac`, §5]: arms whose
language-model-authored rewards differ in natural magnitude would otherwise receive different *effective* entropy
regularisation under automatic temperature tuning. We therefore apply a PopArt value-target normaliser uniformly
across arms [`vanhasselt2016popart`] — which preserves the realised-return series exactly, so the analysed
quantities are byte-identical with and without it — and log the realised per-candidate normalisation scale; a
one-seed `popart`-disabled ablation of the frozen winners is reported in Chapter 6 [FROM CAMPAIGN: ordering verdict]. A truncated-quantile critic
[`kuznetsov2020tqc`] is run as a *named secondary* experiment (mean critic vs. quantile critic), not as the
contribution, which lives in the off-critic feedback channel. We set the training budget by measurement in two
pre-registered stages rather than asserting it. An initial pilot found the critic's steep descent complete near
100,000 steps and held-out performance flat within seed noise to its 350,000-step ceiling; because a ceiling is a
range limit and not a verdict, a pre-committed extension rule — registered before the extension data existed —
then carried the ladder to 1,600,000 steps (a 16× range) on both archived designer-authored rewards, three
common-random-number seeds each. The extended curve rises decisively from 200,000 to 400,000 steps (paired
seed-mean gains of two to five standard errors on both rewards) and flattens beyond it, with residual gains an
order of magnitude smaller: **the measured knee is 400,000 steps, and that is the campaign budget**, applied
identically across arms so that arm differences are read *at a fixed, matched budget at the knee of the measured
learning curve*; the full curve is reported as an exhibit with the results (Chapter 6), and the budget's residual
limits are disclosed in Chapter 7. The confirmatory campaign
runs on the UCL Myriad HPC cluster (SGE batch arrays; device-homogeneous V100/A100 pools, with every
common-random-number seed pair kept device-consistent): a candidate trains in roughly 65 minutes on a dedicated
V100 at this budget, five candidates share each GPU at a measured aggregate 2.05 trainings per GPU-hour, and the
realised total wall-clock, concurrency, and API cost of the campaign are reported in Chapter 6.

One positioning note prevents a natural misreading: although every experiment runs on a fixed historical panel,
this is **simulated-online, not offline, reinforcement learning**. The agent runs off-policy SAC against a
historical-replay simulator and collects its *own* transitions under each candidate reward; there is no fixed
behaviour dataset logged by an unknown policy, so the distributional-shift pathology that offline methods —
surveyed in [`levine2020offline`] and addressed in finance by CQL-style conservative value estimation
[`kumar2020cql`; `khraishi2022offline`] — are built to control does not arise here. Relabelling the archived
transitions under new candidate rewards into a fixed dataset, and re-learning under a conservatism penalty, is
the natural offline bridge from this design and is noted as future work.

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
effect. We flag one precedent boundary explicitly: McNeil and Frey validated a peaks-over-threshold
shortfall estimator at a comparable sample size [`mcneil2000estimation`], but fit the generalised-Pareto
tail to pre-whitened AR(1)–GARCH residuals rather than the raw realised returns we use, so their
window-size precedent transfers while the absolute precision at the deepest levels does not. A
bias-corrected peaks-over-threshold estimator [`troop2021biascorrected`] would in principle sharpen
the extreme levels, but its second-order regular-variation correction is validated for heavy tails at large
samples and is ill-conditioned in our regime (a few hundred observations at the 5%/1% levels), so we retain
the plain maximum-likelihood fit and record the correction as future work. The theoretical justification for
feeding this particular vector — that it is a sufficient, jointly elicitable representation of the
coherent-risk class — is developed in Chapter 3.

## 4.5 The reward-designer and the experimental arms

The reward-designer is a frontier language model (Claude Opus 5 in the confirmatory campaign — the frontier Opus
author, which superseded Claude Opus 4.8 in this seat immediately before launch; Claude Sonnet 4.6 in the
prototype). The choice was re-verified against the model landscape immediately before the design freeze: the
confirmatory author is the strongest single-frontier Opus code-author under a single stable model identifier, and
— the identification-critical property — its safety-classifier posture must not introduce an *arm-asymmetric*
refusal channel: a refusal on one arm but not another would break arm symmetry, so freedom from that interference
is treated as a validity requirement, not a convenience. Opus 5 carries the *same* classifier posture as the
incumbent Opus 4.8 (verified against the vendor's migration record and a live authoring smoke), so the succession
introduces no new such channel; by the same criterion a newer-family model whose classifier behaviour *differed*
from that posture — one whose refusal probability could co-vary with the risk-content-heavy distributional arm —
was instead assigned to the descriptive cross-model survey, not the confirmatory seat. It operates
in an Eureka-style reflect-and-improve loop [`ma2024eureka`]: it authors a
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

**The "profit mirage" contamination defence.** A named threat for any language model in a financial loop is that
impressive backtests evaporate beyond the model's knowledge cutoff, because the model has memorised the era it
appears to be predicting [`li2025profitmirage`]. Here that route is structurally unreachable rather than merely
discouraged: the authored reward is a date-blind *function* executed on anonymised integer-index arrays, the AST
gate admits no identifier, date or I/O surface through which era knowledge could be conditioned on, and every
feedback block is computed on the training split alone — so nothing the designer sees, and nothing its code can
touch, identifies the sealed era. What survives is a residual prior — the model's general, era-nonspecific
beliefs about which reward *shapes* work in markets — which is identical across arms by construction and
therefore cancels in the between-arm contrast, the study's inferential object; absolute performance levels
remain prior-laden and are disclosed as such (Chapter 7).

## 4.6 Selection, fitness, and the three-way decoupling

Candidate rewards are selected on a **validation Deflated Sharpe ratio with risk-aversion weight $\lambda=0$** —
that is, a *tail-blind* risk-adjusted criterion. This is a deliberate, conservative choice: the same criterion is applied to every
arm, so it gives no *between-arm* advantage to tail-aware rewards — its only tail sensitivity, the Deflated Sharpe's
second-order skew and kurtosis correction (§3.4), is common-mode — and any tail effect observed downstream must
arise endogenously from the designer's *use* of the fed signal rather than from selection pressure. The deflation corrects the selected
Sharpe for the multiplicity and non-normality of the search [`bailey2014deflated`]. During the search this
deflation is evaluated in its *within-series* form — the sampling variance of a single Sharpe estimator (§3.4),
the only dispersion available before an arm's candidate population is complete; it equals the canonical
*cross-trial* Deflated Sharpe under the homogeneous zero-skill null, is applied identically across arms (so the
no-between-arm-advantage property above is preserved), and is superseded for the *headline* winner, whose
Deflated Sharpe is recomputed post hoc from the empirical cross-trial variance of the realised candidate Sharpes.
The resulting **three-way
decoupling** is the methodological core: the tail is *fed* by the extreme-value estimator on the *training* split;
candidates are *selected* by the tail-blind Deflated Sharpe on the *validation* split; and the hypothesis is
*tested* by the empirical CVaR on the *sealed test* split. Because the object fed is neither the object selected on
nor the estimator graded by, a tail effect is attributable to the feedback channel and cannot be a self-grading
artefact. The decoupling is unit-tested at the split boundaries.

## 4.7 Hypotheses and the pre-registered inference plan

Four hypotheses are pre-registered. **H1** (beat-the-human) asks whether the LLM-designed reward beats the *best*
hand-designed reward — the pointwise maximum over the **eleven-name hand-reward canon** (the full standard
toolkit, not a four-member subset). Naming that maximum by its sealed-leg performance would data-snoop the
comparator, so H1 is formalised *snoop-free* as an **intersection–union test**: the LLM reward *dominates the
canon* — it beats every member one-sided at $\alpha$, which is exactly "beats the best" (the best is the maximum),
while selecting no comparator to snoop. This is registered as a confirmatory node (N6) of the validity tier below
and is **pending supervisor ratification**; until ratified it is reported descriptively. The deflation asymmetry —
the searched LLM winner deflated by its candidate multiplicity versus each un-searched hand reward at $N{=}1$ —
keeps the human bar conservative either way. **H2**, the headline, is the feedback-channel contrast. **H3** asks
whether iterative reflection beats single-shot best-of-N at matched budget; **H4** asks whether the language-model
designer beats the random-search and Bayesian-optimisation baselines.

**H2 is two co-primary intersection–union tests.** *H2-RA* asks whether the distributional arm matches the
comparison arms on risk-adjusted return (a Sharpe contrast); *H2-Tail* asks whether it improves the realised left
tail (a CVaR-5% contrast). Each is an intersection–union test over three legs — distributional versus *scalar*,
*placebo* and *scalar_cvar5* — one-sided at $\alpha=0.05$. The intersection–union construction *is* the
multiplicity correction (the conjunction has size $\le\alpha$ by the intersection–union principle [`berger1982iut`]), which is why no
further per-leg correction is applied and a Benjamini–Hochberg correction over the six legs is demoted to a
reported sensitivity rather than the primary rule. The structure-shuffled arm enters as a **disjoint** control,
never as a fourth leg of the conjunction.

Inference is **per-seed and aggregate-robust**, following the reinforcement-learning evaluation standard
[`agarwal2021rliable`]: each arm is re-run at the pre-registered **winner-seed ladder** (Amendment E1; a
cumulative tiered schedule up to n = 568, primary target 403, with an exogenous stopping tier), each seed's score is reduced to an
interquartile mean, and contrasts are tested by a paired stratified bootstrap over shared seeds, carrying the
across-seed variance rather than the anti-conservative within-path variance. The shared seeds are a
common-random-number *matching* device [`glasserman2004monte`; `glasserman1992guidelines`]: every arm
trains through the identical seed battery, so a per-seed lucky draw cannot masquerade as a between-arm
effect — a benefit that holds regardless of the pairing correlation's sign. Common random numbers
*additionally* shrink the paired-difference variance only where the arms' per-seed scores are positively
correlated; the $\sigma_D$ pilot measured that correlation at $\rho \approx +0.47$ on the CVaR-5% tail leg
(a realised reduction — the leg is conclusive by $n=30$) but at $\rho \approx -0.14$ on the Sharpe leg (not
distinguishable from zero, a slight inflation). We therefore report the paired variance *as measured* and
power the seed ladder to the realised $\sigma_D$, never to an assumed reduction: the correlation is
exploited where it exists and never over-claimed. The realised left tail is
additionally examined by an Expected-Shortfall scoring comparison on the jointly-elicitable Fissler–Ziegel (FZ0)
loss [`fisslerziegelgneiting2015`; `patton2019dynamic`]. We implement this as a **two-sided Diebold–Mariano
equal-accuracy test** of the FZ0 loss differential (a stationary-bootstrap null with a closed-form
Newey–West/Harvey–Leybourne–Newbold small-sample companion [`harvey1997testing`]), *not* the one-sided comparative
(dominance) backtest of Nolde–Ziegel: the two-sided equal-accuracy null is the more conservative choice, since it
never credits the distributional arm for a directional advantage that a one-sided comparative test would grant it,
and it is reported with a size/power calibration and the explicit caveat that Expected-Shortfall comparative
backtests are low-powered on multi-year windows [`du2017backtesting`; `bauer2025equal`]. This Expected-Shortfall comparison is
**report-only supporting evidence** computed on the campaign and is **disjoint from the confirmatory family of
$m=6$** defined above: it corroborates but never gates H2-Tail. Overfitting is bounded by the **probability of backtest
overfitting** via combinatorially
symmetric cross-validation over the full enumeration of block partitions, which is trial-count-free and serves as
the primary overfitting guard [`bailey2017pbo`]; we disclose the known regimes in which it is biased
[`witzany2021bayesian`]. A pre-registered factor-attribution (CAPM through a six-factor model with Betting-Against-
Beta and Quality-Minus-Junk, Newey–West standard errors) rules out the headline being a low-volatility beta
[`frazzini2014bab`; `asness2019qmj`; `newey1987simple`].

The smallest effect size of interest is **0.05 Deflated-Sharpe units**, and a symmetric two-one-sided-tests
equivalence margin of $\pm0.05$ is pre-registered so that a non-rejection can be reported as a bounded equivalence
rather than an underpowered failure [`lakens2017equivalence`]. A power analysis places the minimum detectable
effect at 80% power, under the primary one-sided intersection–union rule, at approximately 0.181 in Sharpe units
(≈0.120 in Deflated-Sharpe units after the conservative delta-method conversion, ≈0.141 at 90% power); the
conservative Šidák two-sided sensitivity this rule superseded as the gate is higher, at ≈0.257 Sharpe. We disclose
honestly that even the primary effect exceeds the smallest effect of interest, so a clean equivalence claim rests on
the equivalence interval and is otherwise reported as inconclusive — the calibrated, not the convenient, statement. The equivalence margin above is set in Deflated-Sharpe units for the *H2-RA* leg; the
*H2-Tail* equivalence bound is applied on the daily CVaR-5% difference, where a raw $\pm0.05$ would be far too
permissive — the sealed-leg CVaR-5% magnitude is on the order of a few percent per day, so an absolute band of five
percentage points would declare tail-equivalence almost by construction. We therefore justify the tail band on the
CVaR scale directly and additionally report the H2-Tail difference as a *fraction of the baseline (scalar-arm)
CVaR*, so equivalence is judged against the effect's own tail magnitude rather than against a Sharpe-scale number.
We further flag the CVaR leg as the **lowest-power member** of the H2 family: tail statistics estimated on
multi-year windows carry the widest sampling variance, so the H2-Tail intersection–union test is the most likely to
land in the inconclusive region, and we read a tail non-rejection as bounded equivalence only when it clears the
CVaR-scaled margin [`du2017backtesting`; `bauer2025equal`]. Cross-hypothesis multiplicity is handled, in the operative default, by treating the four hypotheses as separate
pre-registered estimands with a reported Bonferroni sensitivity rather than a single forced family; a registered
candidate — a graphical-multiplicity **validity tier** [`bretz2009graphical`] that promotes H3, H4, the structure
control, and H1-as-N6 above the H2 co-primaries under strong family-wise control, activated only on upstream
rejection — supersedes this default on supervisor ratification, at a disclosed α-split cost to the headline (the
full weighted graph is registered in the pre-registration).

The design's defensive logic, distributed across §§4.5–4.7, is consolidated in Table 4.1: each row names a
threat to the validity of the headline (H2) inference and the specific, pre-registered design feature that
neutralises it. Read together, these controls are what convert the comparison from a demonstration into a
falsifiable test in which a *null* is informative rather than uninterpretable.

**Table 4.1 — Threats to the validity of the H2 inference and the design feature that defends against each.**

| Threat to validity | Pre-registered design feature that defends against it |
|---|---|
| The effect of *receiving feedback at all* confounded with the effect of its *content* (a demand/placebo effect) | The **placebo** arm — an inert feedback block matched to the distributional block in length and field-count |
| *Multi-level tail shape* confounded with *any single downside number* | The **scalar_cvar5** arm — the scalar score plus one CVaR-5% value |
| The *information* in the tail confounded with its *format/presentation* | The **placebo_shuffled** arm — identical block structure with the tail values deranged (a *disjoint* control, never a fourth conjunction leg) |
| A tail effect arising from *selection pressure* rather than from the feedback channel | **Tail-blind selection** — validation Deflated Sharpe at $\lambda=0$, which gives no advantage to tail-aware rewards |
| A *self-grading* artefact (the quantity fed being the quantity tested) | The **three-way decoupling** — fed on the training split, selected on validation, tested on the sealed split |
| **Multiplicity** across the contrast legs | The **intersection–union** construction (the conjunction *is* the correction; Benjamini–Hochberg over the six legs is demoted to a reported sensitivity) |
| **Backtest overfitting** of the selected winner | **PBO / CSCV** over the full block-partition enumeration — trial-count-free, the primary overfitting guard |
| Multiplicity and non-normality inflating the *selected* Sharpe | The **Deflated Sharpe** selection criterion |
| The headline being a disguised **low-volatility or factor beta** | A pre-registered **six-factor attribution** (CAPM through BAB and QMJ, Newey–West errors) |
| Train/test **leakage** across the split boundary | A **60-session purge and embargo** covering the full feature lookback |
| Untrusted model-authored code **exfiltrating or corrupting** shared state | An **AST allowlist gate** plus in-process execution on anonymised, read-only arrays |
| The designer's memorised knowledge of the test era inflating results ("profit-mirage" contamination [`li2025profitmirage`]) | **Date-blind authorship** — anonymised integer-index arrays, the AST gate, train-split-only feedback; residual era-nonspecific reward-shape priors are arm-identical and cancel in the contrast |
| *Within-path* variance understating uncertainty (anti-conservative inference) | The **winner-seed ladder** (up to n = 568) with a per-seed rliable interquartile mean and a paired stratified bootstrap |
| A non-rejection misread as a *failure* rather than a bounded *equivalence* | A pre-registered **TOST equivalence** margin ($\pm0.05$ Deflated-Sharpe units) against the SESOI |
| **Forking paths** / post-hoc goalpost-moving | A **SHA-256 freeze** of the full design before the sealed leg, plus an append-only deviations log |
| **Cross-hypothesis** multiplicity (H1–H4) | Separate pre-registered estimands + a reported **Bonferroni** sensitivity (operative default); a registered graphical **validity tier** supersedes on ratification |

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
**language-model generation** is *provably not* reproducible: model behaviour drifts across versions,
and floating-point non-associativity makes inference non-deterministic even at fixed version
and temperature on commodity hardware [`yuan2025nondeterminism`]. We therefore adopt a *replay-from-archive*
contract: every prompt, authored reward and feedback block is archived at generation time with byte-level
tamper-evidence, and downstream results are computed by *replaying* the archive, never by regenerating it. This
converts the loop's least reproducible component into a documented, literature-grounded design decision. The data
are accompanied by a datasheet and each model in the loop by a model card [`gebru2021datasheets`;
`mitchell2019modelcards`], and the study is reported against a machine-learning-for-science reporting standard
whose central concern — leakage — the design directly addresses [`kapoor2023leakage`].
