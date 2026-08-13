# Chapter 3 — Data

The panel's own tail statistics are why the manipulated variable is a vector rather than a single number.

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 3.1 — The panel, the action space and the splits.** Every field can be diffed against the panel and the configuration file, and the row carrying the most weight is the purge, sized by the feature lookback rather than the nominal embargo.
```{=latex}
\par\endgroup
```

| Field | As executed |
|---|---|
| Source | licensed Refinitiv/LSEG daily total returns, survivorship-free, point-in-time |
| Universe | 963 US-listed securities over 5,406 trading sessions, 2005-01-03 to 2026-06-30 |
| Action space | the top 30 names by point-in-time market capitalisation at the development date, plus cash, held fixed across all three splits |
| Training split | 2005–2016; the agent learns here and the fed tail signal is measured here |
| Validation split | 2017–2019; candidate rewards are selected here |
| Sealed test split | 2020 to end-June 2026; untouched until final inference |
| Purge at every boundary | $\max(\text{embargo}=21,\ \text{lookback}=60)=60$ trading sessions |
| Executed sealed window | opens 2020-03-30, after the test-boundary purge |
| Delisting policy | `liquidate_to_cash` zero-fill at the headline; disclosed sensitivity band $d\in\{0,-30,-55,-100\%\}$, whose −30% and −55% rungs are the Shumway NYSE/AMEX and NASDAQ surcharges. Across that band the pooled test CVaR-5% moves by about two per cent in relative terms, of order a tenth of a percentage point, leaving the hypothesis ordering invariant |

## 3.1 Survivorship-free and point-in-time, by necessity

Survivorship-free, point-in-time construction is what stops the panel fabricating performance, and it
is not a data-quality nicety. Truncating a sample to surviving names induces spurious predictability
strong enough to manufacture a result [`brown1992survivorship`; `kothari1995another`], and
point-in-time membership keeps a security out of the tradable set until it was actually a
constituent. One row of Table 3.1 records a trade-off. Holding the top-thirty cohort fixed from the
development date guarantees a consistent action space, but the sealed leg then trades a
development-era cohort, a composition bias reported rather than inherited (Chapter 6).

## 3.2 The tail reverses across levels, so one number cannot carry it

<!-- THE TAIL-FACTS PARAGRAPH THAT SAT HERE WAS CUT ON 2026-08-11 AS THE THIRD STATEMENT OF THE SAME
     FACTS. Excess kurtosis, the 0.84-to-1.66 crossover and the 19.7% co-crash rate are given in §1.1,
     measured in §3.2, and drawn in Figure 3.1 immediately below this line. Saying them a third time in
     the methodology is the repetition Tamer instructed be removed, and the figure caption carries the
     numbers where a reader meets them. The consequence sentence is kept, because it is what the
     methodology needs and the data chapter does not state. -->

The training window's own distribution is why the fed signal is a *vector* (Figure 3.1). No scalar at one
level represents a tail whose severity against the Gaussian benchmark reverses across quantiles, and a
vector of level-specific conditional shortfalls does. That vector is the manipulated variable.

![**Figure 3.1** — Stylised tail facts of the training window (2005–2016), the empirical motivation for feeding a *multi-level* tail vector rather than a single downside number. Descriptive analysis on the TRAIN window only, development top-30, anonymised, delisted names liquidated to cash; the sealed years are never read. The four numbers the panels are built from, in order: excess kurtosis **15.2** against a Normal's zero, with 26 days below $-3\sigma$ where a matched Normal expects 4.1 and 9 below $-5\sigma$ where it expects 0.0009, a factor of **10,393**; at $\alpha = 0.01$ an empirical shortfall of $-5.58$ per cent a day against the Normal-implied $-3.35$; **19** volatility episodes holding all 301 top-decile days, the longest 90 sessions; and on stress days **19.7** per cent of names sit below their own 5 per cent quantile against 3.3 per cent on calm days, where independence would put both near 5. **What to conclude:** the data motivate the vector rather than a scalar, because the empirical-to-Normal ratio *reverses direction* between moderate and extreme levels, so no single level represents the tail.
](F3_stylised_facts.pdf)


## 3.3 The purge is sized by the feature lookback

The split discipline exists to keep one window genuinely unseen. The 60-session purge in Table 3.1 is not a
nominal embargo: following López de Prado, it must cover
the full *feature lookback*, so no observation's feature window straddles a boundary
[`lopezdeprado2018afml`]. The property is unit-tested adversarially. Corrupting every
row at or after a decision row leaves the constructed observation byte-identical.

![**Figure 3.2** — The Split-C timeline: training (2005–2016), validation (2017–2019) and the sealed test window (2020–2026H1), with the 60-session purge at each boundary. The purge places the COVID crash inside the test-boundary embargo, so sealed execution opens on 30 March 2020. **What to conclude:** The sealed window opens after the COVID drawdown, which bounds every absolute figure taken from it.
](F4_splits_timeline.pdf)

One consequence is disclosed. The COVID crash falls *inside* the test-boundary purge (Figure 3.2), so
the sealed window opens near the trough and captures the recovery rather than the drawdown. Moving
the boundary would trade away the leakage guarantee the purge exists for, and would let one
three-week episode dominate the sealed CVaR estimand. The 2022 bear market stays fully in-window, and
the boundary is shared by all arms, so it cannot confound the between-arm contrast.


## 3.4 Delisting is zero-filled, because a surcharge fabricates M&A losses

Zero-filling delisted names understates the delisting tail and never invents it, which is the
conservative choice for a tail-risk study. The survivorship-corrected variant that books Shumway
delisting returns is deliberately not the headline [`shumway1997delisting`; `shumway1999delisting`],
because the corpus carries no delisting *reason*, so the surcharge would be applied indiscriminately,
including to premium merger-and-acquisition exits that the source authors themselves exclude from
performance-related delistings. Fabricating left-tail losses on those exits, in a study whose object
is the left tail, would be indefensible. The surcharge is retained as the heavy end of the band in
Table 3.1, which the hypothesis ordering survives.

\newpage

# Chapter 4 — Methodology and Analysis

## 4.1 One manipulated variable, and what identifies it

This chapter specifies the experiment that answers one question. *Does showing a language-model
reward-designer the lower tail of the realised outcome distribution, instead of a single score, change
the reward code it writes, and does that change propagate to the trained agent's realised tail
behaviour?* Three commitments answer it, and Figure 4.1 draws them together. Only the feedback block
varies, and we hold everything else in the loop byte-identical across the language-model arms (§4.5). The
feeding, the selecting and the testing are done by three different estimators on three different splits,
so a between-arm tail effect cannot be an artefact of a tail-favouring selector or a self-grading metric
(§4.6). And the plan is hash-frozen before the sealed leg is touched (§4.8).

![**Figure 4.1** — The experimental loop and the off-critic decoupling. **What to conclude:** Three different estimators do the feeding, the selecting and the testing, so a tail effect cannot be an artefact of a tail-favouring selector or a self-grading metric.
](F1_system_diagram.pdf)


## 4.2 No feature at a decision can see the future

Every feature at a decision is a function of strictly prior information. The observation is the flat
concatenation
$[\,r_{t-60:t-1}\ \|\ \sigma^{(20)}_t\ \|\ \sigma^{(60)}_t\ \|\ \mathrm{VIX}_{t-1}\ \|\ 1\ \|\ w_{t-1}\,]$,
in which $\sigma^{(k)}_t$ is the $k$-session realised volatility and the return block spans $t{-}60$
through $t{-}1$ inclusive, so the traded session's own return never enters. That is
$60N + 2N + 1 + 1 + (N{+}1) = 1{,}893$ features at $N=30$, and Table E.2 names and sources each
block. Rolling statistics use an explicit one-step shift and the VIX value at row $t$ is the $t{-}1$
close. No security identifier or calendar date ever reaches the observation or any reward, because
the arrays are anonymised to integer indices, which prevents date and ticker leakage and is a
precondition of the untrusted-code sandbox (§4.5).

## 4.3 The learner is fixed, so only the reward varies

The agent is the constant against which the feedback channel is varied, so it is byte-identically fixed
across every arm. It is Soft Actor-Critic in Stable-Baselines3, with every hyperparameter read from the
frozen configuration rather than tuned per arm. Tables E.2 and E.3 print the learner and the environment
field by field. Two choices are argued here rather than listed, because they are the two that could have
broken the identification.

Two nested decision problems sit inside this study, and naming both is what identifies the effect.
We hold the inner one, the trading agent, fixed. The outer one searches over reward programs. Figure 4.2
draws them.

![**Figure 4.2** — The two nested decision problems. **What to conclude:** every edge in this figure is common to all nine arms except one.
](F0_rl_loop.pdf)

$$\mathcal{M}(\varphi)=(\mathcal S,\mathcal A,\mathcal P,r_\varphi,\mu_0,\gamma),\qquad
a_t=w_t\in\Delta^{30},\qquad \gamma=0.99$$

$$s_t=\big[\,r_{t-60:t-1}\,\|\,\sigma^{(20)}_t\,\|\,\sigma^{(60)}_t\,\|\,\mathrm{VIX}_{t-1}\,\|\,1\,\|\,w_{t-1}\big]\in\mathbb R^{1893}$$

$$\pi_\theta=\arg\max_{\pi}\ \mathbb E_{\pi}\Big[\textstyle\sum_t \gamma^{t}\big(r_\varphi(s_t,a_t)+\alpha\,\mathcal H(\pi(\cdot\mid s_t))\big)\Big]$$

Only $r_\varphi$ varies, and the designer writes it. Nothing evolves between candidates, so the outer
problem is a bandit whose actions are candidate reward programs $\varphi\in\Phi$, whose payoff is the
tail-blind validation fitness of §4.6, and whose budget is thirty pulls per arm.

$$\varphi\sim q\big(\cdot\mid u\oplus b_a\big),\qquad
b_{\mathrm{scalar}}=\Pi\circ b_{\mathrm{dist}},\qquad \hat{\mathbf c}\in\mathbb R^{6}$$

That identity is the whole manipulation. The scalar block is the tail block with six coordinates deleted,
which is why §1.3's dominance argument applies to these two prompts and to no others.

<!-- S3 CLOSED HERE ON 2026-08-11. Stefan's highest-leverage ask was that states, actions and rewards be
     given formally in the body, with SAC in notation, because a reader who does not meet the standard
     formalism pattern-matches the work to "someone applied SAC to a portfolio" and reads everything
     after that through the wrong frame. MEASURED before writing: the ONLY MDP tuple in the whole
     316-page document sat at Appendix C, i.e. the word-budget relocation had moved the exact thing he
     asked for out of the body.
     THE NOTATION MATCHES APPENDIX C EXACTLY, including the six-tuple with mu_0, because one object may
     carry only one name in this document. The word "arm" is reserved for the experimental condition and
     the outer problem's actions are called candidate reward programs, which is the C1 distinction
     Stefan himself tripped over when he read "arm" and inferred a bandit.
     COST: display mathematics is word-excluded, so only the three short prose lead-ins are counted.
     Verified from the artefacts rather than recalled: 1,893 features (CH4 s4.2), the simplex over
     thirty assets plus cash (Table 4.1), thirty candidates per arm (Algorithm 4.1), and gamma = 0.99,
     which config/algos.yaml:30 leaves as `gamma: null` with the comment "SB3 default 0.99". -->


Reward-scale heterogeneity is a genuine confound rather than a nuisance. In Soft Actor-Critic the
reward scale acts as an inverse temperature and governs exploration [`haarnoja2018sac`], so arms
whose authored rewards differ in natural magnitude would receive different *effective* entropy
regularisation. The uniform PopArt normaliser in Table E.2 removes that asymmetry without touching
the realised-return series, which is byte-identical with and without it.

The training budget was measured, and the measurement overruled its own authors. A pre-committed
extension rule carried the ladder to 1,600,000 steps, and the curve rises decisively from 200,000 to
400,000 and flattens beyond. The evidence that the protocol binds is what it cost. Our own standing
recommendation was 200,000, and the rule carried an explicit keep-200,000 branch, so it could have
confirmed us. It did not. It doubled the compute budget of every training in the study, before the
design was frozen. Exhibits 1 and 2 of Appendix A carry the ladder and the limit of that evidence.

One positioning note prevents a misreading. This is simulated-online, not offline, reinforcement
learning, despite the fixed historical panel. The agent collects its *own* transitions
off-policy against a replay simulator, so there is no behaviour dataset logged by an unknown policy, and the
distributional-shift pathology that offline methods [`levine2020offline`; `kumar2020cql`;
`khraishi2022offline`] exist to control does not arise[^offlinebridge].

[^offlinebridge]: Relabelling those transitions and re-learning under a conservatism penalty is the natural offline bridge. It is named as future work, because the relabelled dataset would no longer hold the agent byte-identically fixed across arms.

<!-- THE FIXED-LEARNER TABLE MOVED TO APPENDIX E (Table E.2) ON 2026-08-12. It is a specification a
     marker may CONSULT to verify a claim, not one they MUST read to award a band, which is the
     placement test in the 95+ doctrine section 2. The claim it supports, that the learner cannot be
     a source of between-arm difference, is now stated in the prose above and the two rows that carry
     an argument are argued below. Its citations travel with it and still resolve. -->

## 4.4 The fed signal is measured off-critic, from realised returns

The instrument that produces the fed signal touches no value network, which is the precise sense of
off-critic and makes it agnostic to the agent's architecture. It reads only the *realised
returns* of the policy on the training split, and returns the six-component tail vector printed in full in
Listing 1.1.[^fedvector]

<!-- THE FOOTNOTE MARKER MOVED TO AFTER THE FULL STOP ON 2026-08-11. It sat directly against the
     exhibit number, so the page rendered "Listing 1.1" with a superscript welded to it and a text
     extractor read the reference as "Listing 1.124". A human sees a superscript and is not misled, but
     the ambiguity is real and the fix is one character. Found by the presentation sweep's dangling-
     reference check, which is the only instrument in the toolchain that would ever have seen it.
     It is the ONLY occurrence in the body: the pattern `\d\[\^` matches once across paper/*.md. -->

[^fedvector]: The components are conditional value-at-risk at the 5%, 10%, 25% and 1% levels, the left-tail mass beyond $-2\sigma$, and a robust left-tail skew. The 5% and 1% levels are fitted by generalised-Pareto peaks-over-threshold [`pickands1975statistical`; `balkema1974residual`; `smith1987estimating`; `mcneil2000estimation`], the inner levels are empirical, and a guard falls back to the empirical estimate where maximum likelihood is unreliable [`smith1985maximum`].

One limit of that instrument is disclosed. An extreme-value tail fitted on a few
hundred observations is finite-sample fragile [`belzile2020improved`; `cont2010robustness`]. The fed CVaR is
therefore treated as a noisy signal, whose noise biases *against* detecting a channel effect, and the
closest precedent in the literature transfers only in part[^precedent]. Appendix C develops why this vector
is nonetheless the right object to feed.

[^precedent]: McNeil and Frey validated a peaks-over-threshold shortfall estimator at a comparable sample size [`mcneil2000estimation`], but fitted the tail to pre-whitened residuals rather than raw realised returns, so their window-size precedent carries and their absolute precision does not. A bias-corrected estimator [`troop2021biascorrected`] is ill-conditioned at a few hundred observations and is recorded as future work.

## 4.5 Nine arms, and the controls that make a null informative

The reward-designer operates in an Eureka-style reflect-and-improve loop [`ma2024eureka`], stated as
executed in Algorithm 4.1. It authors a reward function as Python code, the agent is trained and evaluated,
a feedback block is composed, and the model revises the code.

One property of the designer's seat is a validity requirement. A safety classifier that refused the
risk-heavy distributional prompt but not its controls would break arm symmetry outright, so the seat is
checked for an arm-asymmetric refusal channel.[^seat] The identical loop is re-run across ten further
models, five of them open-weight (Chapter 5).

[^seat]: The model the frozen plan seats for the single hash-bound look carries the same classifier posture as the incumbent it superseded.

```{=latex}
\begingroup\tabcaptionstyle
```
**Algorithm 4.1 — The reward-design loop, as executed.** The budget, the prompts, the trainer and the eligibility floor are all fixed in the preamble, so a reader audits one composed line, not the whole procedure.
```{=latex}
\par\endgroup
```

```text
Require: arm a in {distributional, scalar, placebo,
                   scalar_cvar5, placebo_shuffled}
Require: budget B = 30, generations G = 6, per generation K = 5
Require: frozen prompts S, P0, P+           (all hash-bound)
Require: fixed SAC trainer T; splits Dtr, Dval
Require: execution floor phi = 0.10          (amendment R115)

 1: block <- none
 2: A <- empty archive
 3: for g = 0 .. G-1 do
 4:     best_g <- none
 5:     for k = 1 .. K do
 6:         u <- (g = 0) ? P0 : P+ with block substituted
 7:         u <- u + diversity directive k of K
 8:         src <- LLM(S, u)
 9:         if AST gate rejects src then log, skip, continue
10:         r  <- instantiate(src)
11:         pi <- T(env(r), Dtr)
12:         v  <- realised returns of pi on Dval
13:         f  <- DeflatedSharpe(v)
14:         d  <- tail statistics of pi's TRAINING returns
15:         block_k <- build_block(a, f, d)   # ARM ENTERS HERE
16:         archive src, prompt, f, block_k, counters
17:         if f > fitness(best_g) then best_g <- (f, block_k)
18:     end for
19:     block <- block_of(best_g)
20: end for
21: E <- { c in A : safe_default_frac(c) < phi }
22: if E is empty then FAIL LOUDLY
23: return argmax_{c in E} f(c)
```

Four lines of Algorithm 4.1 carry the identification argument, and Table 4.1 names them. Two more are
guards, not steps: line 9 refuses
authored code that fails a static allowlist gate, and lines 21 to 22 refuse to promote any candidate whose
reward fell back to the harness default on 10% or more of its training calls[^floor].

[^floor]: The one candidate this threshold excluded had fallen back on 49.98% of calls, so it did execute for most of its training, and it still held the highest fitness in its arm (section 6.1).


```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 4.1 — The four lines that carry the identification.** Only one line of the procedure depends on the arm, and the line that scores a candidate is computed without the tail, so a tail-aware reward earns no selection advantage.
```{=latex}
\par\endgroup
```

| Line | What it does | Why it carries the identification |
|---|---|---|
| **15** | composes the feedback block from the arm | the only arm-dependent statement in the whole procedure, so any between-arm difference must be traceable to the feedback block |
| **13** | scores the candidate on a criterion computed without the tail | a tail-aware reward earns no selection advantage |
| **14** | measures the tail from realised returns rather than from the value network | the instrument is portable across critic architectures, though not independent of the agent, since the returns are the trained policy's own |
| **19** | reflects on the generation's best candidate, not its last | the Eureka-faithful choice, and the reason a weak draw cannot poison the next prompt |

Table 4.2 states the nine arms. Five differ in one thing only, the feedback block the designer is shown,
and four replace the designer with a derivative-free optimiser over a shared parametric reward family,
which is what makes "did the designer help?" answerable at all.

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 4.2 — The nine arms (`config/arms.yaml`).** Rows 1 to 5 differ in one thing only, the feedback block the reward-designing model is shown, and rows 6 to 9 replace the model with a derivative-free optimiser, which is what makes "did the language model help?" answerable.
```{=latex}
\par\endgroup
```

| Arm | Feedback the designer receives | Role |
|---|---|---|
| `distributional` | six tail statistics | treatment |
| `scalar` | the validation fitness alone | primary control, the field's practice |
| `scalar_cvar5` | the scalar plus CVaR 5% | dose: is one number enough? |
| `placebo` | six inert constants under neutral labels | format control |
| `placebo_shuffled` | the six real values on deranged labels | structure control |
| `random_search` | none, searches code | comparator [`bergstra2012randomsearch`] |
| `bayes_opt` | none, searches a template | comparator [`snoek2012practical`; `shahriari2016bo`] |
| `cma_es` | none, template | comparator [`hansen2001cmaes`; `hansen2016cmatutorial`] |
| `tpe` | none, template | comparator [`bergstra2011tpe`] |

There are two placebos because they isolate different things, and Table 4.8 row 10 says which.

That optimiser side is a portfolio rather than an opponent, because no single black-box method
dominates across evaluation budgets. Bayesian methods lead at small budgets and evolution strategies
overtake them only after hundreds [`raponi2024lowbudget`; `shahriari2016bo`], so naming one would be
a cherry-pick. All four principal paradigms search the identical family at the same budget and
shared seed [`bergstra2012randomsearch`; `snoek2012practical`; `hansen2001cmaes`; `bergstra2011tpe`;
`akiba2019optuna`], budget-inappropriate methods are excluded with cause [`storn1997de`;
`kirkpatrick1983sa`; `kennedy1995pso`; `li2018hyperband`], and the comparator is the pointwise
*maximum* over the portfolio.

The manipulation is verified in the executed archive, without keyword search. Searching
prompts for tail vocabulary would presuppose what the manipulation is, so the feedback block is isolated
structurally instead. One archived prompt per arm is diffed against the other four, so whatever differs
*is* the manipulated variable by construction. Table 4.3 is that residual,[^blocklen] which puts all four
identification contrasts in the live prompts, never in configuration.


```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 4.3 — Each arm's fed block, and the contrast it establishes.** The manipulation is a difference of a few hundred characters inside an otherwise byte-identical prompt, and each control differs from the treatment on exactly one property.
```{=latex}
\par\endgroup
```

| Arm | Residual | Decimal values in it | Tail vocabulary | The contrast it establishes |
|:--------------------------|:-----------------|:---------|:-------------|:--------------------|
| `distributional` | 270 | **6** | present | the treatment: a multi-level tail profile |
| `scalar` | 62 | **0** beyond the header | absent | tail information vs none |
| `placebo` | 288 | **6** | **absent** | **information $\neq$ token count** — the same six fields and 18 characters *more* than the treatment, inert in content |
| `scalar_cvar5` | 81 | **1** | present | **tail *shape* $\neq$ any single downside number** |
| `placebo_shuffled` | 270 | **6** | present | **content $\neq$ format** — the treatment's exact structure and vocabulary, values deranged |
| *Shared by all five* | a 154-character common prefix and a 240-character common suffix, byte-identical across arms | n/a | n/a | verified in the executed archive, three ways[^armverify] |

Because the reward code is authored by an untrusted model it is treated as untrusted input, gated at
line 9 and then executed in-process on anonymised, read-only arrays. That same construction disposes
of the profit-mirage threat.[^mirage] A date-blind function over anonymised indices has no route to
era knowledge. An era-nonspecific prior about which reward *shapes* work survives, and it is
arm-identical and cancels in the contrast. Absolute performance levels remain prior-laden and are
disclosed as such (Chapter 6).

[^armverify]: Verified in the executed archive rather than asserted from the code.

[^blocklen]: The Residual column is the cross-arm residual: one archived reflection prompt with the byte-identical 154-character common prefix and 240-character common suffix removed.

[^mirage]: The profit-mirage threat is that impressive backtests evaporate beyond a model's knowledge cutoff, because the model memorised the era it appears to predict [`li2025profitmirage`].

## 4.6 Fed, selected and tested by three different estimators

Candidates are selected on a validation Deflated Sharpe ratio at risk-aversion weight $\lambda=0$
[`bailey2014deflated`], a net-of-cost criterion with no explicit tail term, applied identically to
every arm. It therefore gives no *between-arm* advantage to tail-aware rewards, and any tail effect
downstream must arise from the designer's *use* of the fed signal rather than from selection
pressure. Calling it tail-blind is a shorthand. Its one tail sensitivity, the Deflated net Sharpe's
second-order skew and kurtosis correction (§C.4), is common-mode, so the selector is arm-invariant
rather than literally tail-insensitive (§C.7)[^dsrform].

[^dsrform]: During the search the deflation is evaluated in its within-series form, the only dispersion available before an arm's candidate population is complete.

The three-way decoupling that results is the methodological core. The extreme-value estimator feeds on
*training*, the Deflated net Sharpe selects on *validation*, and the empirical CVaR tests on the *sealed*
split. Because the object fed is neither the object selected on nor the estimator graded by, a tail effect
is attributable to the feedback channel and cannot be a self-grading artefact. The decoupling is unit-tested
at the split boundaries.

## 4.7 What each hypothesis must beat, decided in advance

Four hypotheses are pre-registered, and Table 4.4 states each as an executable decision rule with the
direction that would count as support. Two ask whether the designer helps at all, against the
*best* hand-designed reward (H1) and against numerical search over the identical family (H4). A third asks
whether reflection beats single-shot generation at matched budget (H3), and the registered headline is the
feedback contrast (H2).

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 4.4 — The confirmatory decision rules, fixed in advance.** Each row states a test and the direction that would count as support, written before any sealed data was seen. Node N2 is a one-sided non-inferiority test at the registered margin, and the two-sided interval a reader wants for interpretation is reported separately at §B.8.15, because the node test and the reporting test are different objects.
```{=latex}
\par\endgroup
```

| Node | Hypothesis | Endpoint | Direction |
|---|---|---|---|
| N1 | H2-Tail | CVaR at 5% | one-sided, treatment better |
| N2 | H2-RA | net Sharpe | one-sided non-inferiority at $\delta = 0.0756$ |
| N3 | H3 | per-seed interquartile mean | one-sided |
| N4 | H4 | against all four optimisers | one-sided, over all four |
| N5 | structure | CVaR at 5% | one-sided, content over format |
| N6 | H1 | annualised net Sharpe | one-sided, over the full eleven-name canon |

What H1 must beat is a canon rather than an incumbent, and Table 4.5 prints it. A single comparator would
be a straw man, so the bar is the pointwise maximum over all eleven published objectives with no selection
step, which is the hardest bar the literature offers.

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 4.5 — The eleven-reward canon: the human bar.** Each is a published objective and not an invention of this study, and the champion is the maximum over all eleven with no selection step.
```{=latex}
\par\endgroup
```

| Reward | What it optimises | Source |
|---|---|---|
| `raw_return` | the bare portfolio return, a myopic risk-**neutral** floor | the field-standard default (no single canonical source) |
| `return_minus_variance` | return penalised by a variance proxy | [`markowitz1952portfolio`] |
| `return_minus_cvar` | return penalised by tail risk (CVaR) | [`rockafellar2002general`; `acerbi2002coherence`] |
| `differential_sharpe` | differential (online) Sharpe, **stateful** | [`moody1998performance`; `moody2001directrl`] |
| `differential_`\allowbreak`downside_ratio` | the downside companion of the above | [`moody2001directrl`] |
| `mean_variance_utility` | Markowitz quadratic utility `r − 1/2lambda·var` | [`markowitz1952portfolio`] |
| `return_minus_drawdown` | running log-wealth drawdown penalty, **stateful** | [`chekhlov2005drawdown`] |
| `return_minus_downside` | Sortino downside semi-deviation | [`sortino1991downside`] |
| **`return_minus_turnover`**| transaction-cost / turnover penalty | [`garleanu2013dynamic`] |
| `log_growth` | growth-optimal Kelly log return | [`kelly1956information`] |
| `volatility_scaled_return` | a volatility-**targeted** return | [`zhang2020drltrading`] |

Two conventions travel with every number taken from that canon, and both have cost a retraction
here.[^conventions]

[^conventions]: Every Sharpe is the raw annualised ratio, `sharpe_ratio(returns, periods_per_year=252)`, which takes no risk-free argument, and each is labelled gross or net. And the evaluation window is the archive's own 1,571 traded sessions: the 60-session lookback purge means it is *not* every session after 2020-01-01, and conflating the two understates every benchmark by roughly 0.47 net Sharpe.

Three of the four share one construction that carries the whole inference plan. H1, H2 and H4 are
each an intersection-union test [`berger1982iut`]. Naming a champion by its sealed-leg performance
would data-snoop the comparator, so the claim must instead hold against *every* member of the
comparator set at once, which is exactly "beats the best" and selects nothing. The headline contrast
runs the construction twice, as two co-primaries, over the *scalar*, *placebo* and *scalar_cvar5*
legs, one-sided at $\alpha=0.05$. The scrambled control enters as a disjoint control, never as a
fourth leg of a conjunction.

**The unit of analysis is the program, not the condition.** One selected program per arm is re-run
across the seed battery, so the interval generalises to the *selected programs*. The condition-level
claim is carried instead by the report-only mechanism kernel of Chapter 5, which does sample the
authoring step.[^unitb]

[^unitb]: The confirmatory unit is the (program, seed) pair, so authoring variance sits outside the interval by construction.

The contest against numerical search is hard, and its verdict is asymmetric. The designer authors
free-form code, a strict superset of the family the optimisers search, so at matched budget it
navigates a far larger space with a semantic prior as its only advantage. The registered node carries
a one-sided superiority test, which certifies one reading. It either rejects, licensing "the designer
beats the pointwise maximum", or it does not, which licenses nothing. "Matches to within the SESOI"
and "is beaten by" are *descriptions* placed on a non-rejection, never conclusions.

The rest of the plan sits in Table 4.6, two of whose rows are arguments, and the five
report-only exhibits, which cannot propagate $\alpha$, sit in Table E.4.


```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 4.6 — The inference plan as registered.** The plan was fixed with its own weak points named.
```{=latex}
\par\endgroup
```

| Element | As registered |
|---|---|
| Multiplicity | none per leg; the conjunction is the correction |
| Mechanism decomposition | report-only, and never allowed to answer the contest |
| Aggregation | per-seed interquartile mean, paired stratified bootstrap [`agarwal2021rliable`] |
| Seed pairing | common random numbers, identical battery in every arm [`glasserman2004monte`; `glasserman1992guidelines`] |
| Pairing correlation | pilot $\rho\approx+0.47$ on the tail leg, $\rho\approx-0.14$ on net Sharpe |
| Seed ladder | cumulative to $n=568$, primary target 403, stopping fixed exogenously |
| Running-estimate exhibit | every headline statistic against $n$, with its band |
| Smallest effect of interest | 0.05 Deflated net-Sharpe units, symmetric TOST [`lakens2017equivalence`] |
| Equivalence power | tier-conditional, reported at the achieved rung |
| Tail-leg bound | on the CVaR scale, and as a fraction of the baseline arm's CVaR |
| Overfitting guard | PBO by combinatorially symmetric cross-validation [`bailey2017pbo`], biased near zero mean return [`witzany2021bayesian`] |
| Estimator provenance | Table E.5 attributes every estimator; §A.6 works the margin |


```{=latex}
\Needspace{3\baselineskip}
```

Cross-hypothesis multiplicity forces a reporting consequence, stated before any result is seen. Under
the registered graphical validity tier [`bretz2009graphical`] the entire $\alpha$ sits on the two
co-primaries, and H3, H4, the structure control and H1 begin at weight zero, becoming testable only if a
co-primary rejects. If the tier never activates, those four are never tested and no evidence however strong
could reject them, so they are reported as report-only. A reader cannot otherwise tell a hypothesis that
survived a test from one that was never testable. Chapter 5 prints each node's local $\alpha$ beside its
verdict.

One post-freeze correction to the risk-adjusted node is reported with its forensics[^correction].

[^correction]: The registration makes the risk-adjusted node a disjunction, so an equivalence result can supply its $p$-value [`bergerhsu1996equivalence`], and the executed code implemented the superiority half alone.

Every named threat to construct validity [`shadish2002experimental`] is paired in Table 4.7 with the
pre-registered feature that neutralises it, which is what makes a null informative.


```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 4.7 — Each threat to the headline inference, and its defence.** No threat on this list is answered after the fact, since every defence is a design feature registered before the sealed window was opened, which is what makes a null informative.
```{=latex}
\par\endgroup
```

| Threat to validity | The registered feature that defends against it |
|---|---|
| receiving feedback at all, confounded with its content | the `placebo` arm, inert and matched in length and field count |
| multi-level tail shape, confounded with one downside number | the `scalar_cvar5` arm, the score plus one CVaR-5% value |
| the tail's information, confounded with its format | the scrambled control, same structure, values deranged |
| a tail effect arising from selection pressure | arm-invariant selection at $\lambda=0$, so tail sensitivity is common-mode |
| a self-grading artefact | three-way decoupling: fed, selected and tested on three splits |
| multiplicity across the contrast legs | the intersection-union construction, which is itself the correction |
| backtest overfitting of the selected winner | PBO over the full block-partition enumeration, trial-count-free |
| multiplicity and non-normality inflating the selected Sharpe | the Deflated Sharpe selection criterion |
| the headline being a disguised low-volatility or factor beta | a registered six-factor attribution with Newey-West errors |
| leakage across the split boundary | a 60-session purge covering the full feature lookback |
| authored code exfiltrating or corrupting shared state | an AST allowlist gate, on anonymised read-only arrays |
| memorised knowledge of the test era [`li2025profitmirage`] | date-blind authorship, and any residual prior is arm-identical |
| within-path variance understating uncertainty | the winner-seed ladder with a paired stratified bootstrap |
| a non-rejection misread as a failure | a registered TOST margin of $\pm0.05$ Deflated-Sharpe units |
| **Forking paths** / post-hoc goalpost-moving | A **SHA-256 freeze** of the full design before the sealed leg, plus an append-only deviations log |
| **Cross-hypothesis** multiplicity (H1–H4) | Separate pre-registered estimands + a reported **Bonferroni** sensitivity (operative default); a registered graphical **validity tier** supersedes on ratification |

Ten choices carry the design, and each was made against a named alternative at a stated cost. Table 4.8
puts all three columns beside each other, because a method that is merely stated cannot be judged
appropriate and one that is justified can. Three of the ten cost us something the study would rather have
had, and those rows say so.

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 4.8 — The ten load-bearing design decisions.** Panel A gives the choice and what it was chosen over, Panel B the reason and the price, and the rows marked **against us** are the two whose cost runs against the hypothesis under test. Three prices are worth the arithmetic. The step budget cost 288,533 processor-hours, and unequal budgets were refused because they confound reward quality with compute. The transaction cost, at 79 per cent daily turnover, is a 20 per cent annual drag and a 1.07 Sharpe wedge, which is why every figure in this document is reported gross and net. And the sealed split's 60-session purge removes the COVID crash, so benchmarks run on the agents' own 1,571 sessions rather than the panel's 1,631, an error that cost a retraction here.
```{=latex}
\par\endgroup
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Panel A — the choice, and what it was chosen over.**
```{=latex}
\par\endgroup
```

\begingroup\footnotesize

| # · decision | Chosen | Instead of |
|---|----------|--------|
| 1 · pre-registration | frozen before the sealed window opened, tag `prereg-v2.1` | registering after the first look; not registering |
| 2 · long-only simplex | simplex over 30 risky assets plus cash | long-short with a gross cap; market-neutral |
| 3 · fixed PIT universe | top-30 fixed at the development-window start | rotating per period; walk-forward re-selection |
| 4 · SAC held fixed | SAC as the sole headline agent | TQC; PPO; an ensemble |
| 5 · step budget | $B^{*}$ = 400,000 steps, identical across arms | 200,000; train-to-convergence per candidate |
| 6 · transaction cost | 10 bps one-way on half-L1 turnover | 0, 5, 25, 50 bps, all registered report-only |
| 7 · selection rule | validation Deflated Sharpe, `max(val_DSR)` | CVaR; a tail-weighted composite; raw Sharpe |
| 8 · execution floor | R115, eligible below 10% safe-default calls | no floor; a 1% floor; excluding on performance |
| 9 · sealed split | train 2005–2016, validate 2017–2019, test 2020–2026 | one train/test cut; k-fold; a shorter embargo |
| 10 · two placebos | inert constants, and real values on deranged labels | a single placebo; no placebo |

\endgroup

```{=latex}
\begingroup\tabcaptionstyle
```
**Panel B — why that choice, and what it cost.**
```{=latex}
\par\endgroup
```

\begingroup\footnotesize

| # · decision | Why this one | What it costs |
|---|--------|----------|
| 1 · pre-registration | every threshold fixed before the data could shape it | nothing learned after the freeze may join the confirmatory family |
| 2 · long-only simplex | feasible without a projection, leverage removed as a confound | **against us:** reallocation is the only tail lever |
| 3 · fixed PIT universe | only what was knowable at the window start | stale by 2026, but 1/N on those 30 names returns +1.2825 gross Sharpe |
| 4 · SAC held fixed | the identification principle: the reward is manipulated, so the agent must not vary | the measured effect is a lower bound, conditional on SAC |
| 5 · step budget | the measured critic knee, by a rule fixed beforehand | 288,533 processor-hours |
| 6 · transaction cost | linear, so the whole grid reprices without retraining | a 20% annual drag at 79% daily turnover |
| 7 · selection rule | one selector, identical across arms | **against us:** Deflated Sharpe embeds skew, so the scalar carries part of the tail |
| 8 · execution floor | fitness alone could freeze a reward that never ran | binding once, on a candidate at 49.98% fallback holding its arm's best fitness |
| 9 · sealed split | one look, at a pre-declared date, behind a 60-session purge | the purge removes the COVID crash |
| 10 · two placebos | one removes the hint, the other destroys only the correspondence | two extra arms, about 20% more compute[^blockcheck] |

\endgroup

[^blockcheck]: Both placebo blocks are rendered by the same hash-bound `src/feedback/schema.py::build_block` as the treatment block. The derangement is verified rather than assumed: the CVaR ladder is monotone in 226 of 226 distributional blocks against 0 of 229 shuffled ones.

## 4.8 Frozen before the sealed leg, replayed not regenerated

The full design is frozen by a SHA-256 hash over the declaration files before the sealed leg is evaluated,
and the campaign driver refuses to run against an unfrozen or drifted design. Any post-freeze departure goes
into an append-only deviations log, so the frozen document stays a true record of what was committed and the
log of what happened (§5.1 and Appendix A).

One consequence is visible to anyone who opens the registration. Its prose record still carries a
status line reading *pre-freeze, awaiting pilots*, and that line cannot be corrected, because the hash
is taken over the file whole and editing the sentence describing the seal would break the seal it
describes (§B.8.11). A record that cannot rewrite its own history is doing the job a registration exists
to do.

<!-- THIS PARAGRAPH IS THE REGISTERED REMEDY FOR A KNOWN CONTRADICTION AND IT WAS ABSENT UNTIL 2026-08-11.
     Verified first-hand:
       PREREGISTRATION.md:3        "**Status:** PRE-FREEZE (as of 2026-07-01) - design content RATIFIED; awaiting pilots"
       config/preregistration.yaml:4  frozen: true
       config/preregistration.yaml:5  freeze_hash: 3ca6f01a...
       scripts/freeze.py:258-269   canonical_bytes = norm(PREREGISTRATION.md) + _strip_freeze_state(yaml)
     The prose file is hashed WHOLE; only the yaml is stripped. So the stale header is structural rather
     than an oversight, and the remedy is a sentence in the body rather than an edit to the hash-bound
     file. Without it, an examiner who opens the registration bundle meets a status line contradicting
     the dissertation's central integrity claim and has no way to tell which is true. -->


Reproducibility is treated in two regimes, because conflating them is the usual error. The analysis is
computationally reproducible and the language-model generation is *provably not*, since model behaviour
drifts across versions and floating-point non-associativity makes inference non-deterministic even at a
fixed version and temperature [`yuan2025nondeterminism`]. The contract is therefore *replay from archive*
rather than regeneration, which converts the loop's least reproducible component into a documented design
decision.[^standards] Table E.7 states what each of the three layers claims and what evidences it.

[^standards]: The data carry a datasheet and each model a model card [`gebru2021datasheets`; `mitchell2019modelcards`], and the study is reported against a machine-learning-for-science standard whose central concern, leakage, the design directly addresses [`kapoor2023leakage`].

## 4.9 What the richer signal could buy, and the assumption under which it bounds this designer

Our design rests on a claim about information rather than about performance. The two feedback blocks
are *nested*. The scalar block is the coordinate projection of the tail block, so the tail-fed designer
sees everything the scalar-fed one sees and six coordinates more. That identity is a property of how the
prompts are assembled and can be checked by reading the block renderer.[^nested] Because the projection is
a Markov kernel, the Blackwell comparison of experiments applies in one direction
[`blackwell1951comparison`]: at every bounded loss and prior, the tail-fed experiment carries no more Bayes
risk than the scalar-fed one. A designer free to ignore part of what it is shown cannot be made worse off
by seeing more. The intermediate arm sits between the two, so the design tests a monotone dose.

**That proposition orders Bayes risks, and this study does not run a Bayes designer.** Reading it as an
envelope for the measured effect requires (NI): that the designer's excess over Bayes is no larger in the
scalar arm than in the tail-fed one. **(NI) is an assumption of this document and not a result of it.** It
holds automatically at zero responsiveness, which is the regime measured here. Appendix C carries the
statement, the proof and the derivation of (NI), and §2.3 gives the separate Kusuoka argument for why the
richer block is a vector of levels rather than one number.

Measured on the designer's own decision problem, the envelope returns nothing. Predicting the next
generation's validation fitness from what it was shown, the risk gap between the two experiments is
$-0.0037$ against a permutation null of $[-0.0085, +0.0058]$, at a referral probability of $0.756$. A
regularised linear user of the six tail statistics predicts no better than one given the score alone.
That is an estimate about one bounded predictor class, not a bound on the information gap (§C.4.1).

[^nested]: Writing the scalar as a measurable function of the tail vector would be false here, because the header is a validation-split number while the tail vector is measured on the training split.
