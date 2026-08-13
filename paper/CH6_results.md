# Chapter 5 — Results

## Reporting rules (apply throughout this chapter)

Table 5.1 governs every statement below.

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 5.1 — The pre-committed reporting rules.** Rules 1 to 5 were fixed before any sealed number existed and govern every result statement in this chapter. Rule 6 was added at write-up, is marked as such, and is presentational.
```{=latex}
\par\endgroup
```

| # | Rule | What it requires |
|---|---|---|
| 1 | no bare nulls | a TOST bound against the ±0.05-DSR margin, never "$p>0.05$" |
| 2 | equivalence first | the TOST result precedes the one-sided IUT $p$ |
| 3 | controls on the same axes | the placebo and scrambled controls overlaid, not tabulated apart |
| 4 | a null carries its mechanism | reported with the §5.5 evidence, never as a bare absence |
| 5 | rung-freshness tagging | machine-checked; the checker fails on any stale tag |
| 6 | every interval states its unit | coverage and resampling unit named, the wider governing |

Two marks below are disclosures.[^marks] Figures 5.1 and 5.2 are descriptive and neither gives a
decision.[^adds]

Printing those contrasts does not spend the single look. Look-inflation needs the sample
size to become a function of the data, and here it cannot. Stopping is a calendar date fixed in advance, and
every analytic degree of freedom was bound into the hash before any sealed number existed. We would
break this by acting on a look, and no rung, leg, seed or stop moved. A reader cannot verify that
abstention. The hash, the date and the deviations log are verifiable.

<!-- COMPRESSED 2026-08-11, 213 counted words to 108, with nothing conceded. What went was
     restatement rather than argument: the enumeration of the six bound quantities (already in Table
     4.4 and in the freeze record), the sentence naming freeze.py --check (named twice more in this
     chapter and in the Declaration), and the clause explaining that the seed tier follows throughput
     (stated in Table 5.2's own rung row). Every load-bearing move survives in order: the mechanism of
     look-inflation, why it cannot operate here, what WOULD break it, the honest concession that
     abstention is unverifiable from the artefact, the three things that ARE verifiable, and the
     closing refusal to claim that vigilance is unnecessary.
     WHY IT WAS WORTH DOING RATHER THAN LEAVING. The body stood at 50 words under an 11,000 limit,
     which is no headroom at all, and this was the single largest passage of METHODOLOGY sitting
     inside the results chapter -- Stefan's M8. Compressing it buys the argument room and moves the
     chapter toward reporting what came out rather than re-defending how it was obtained. -->


## 5.1 The campaign that ran is the frozen one, banked at 102 seeds in every cell

The reported campaign is the frozen one and ran without material deviation, so Table 5.2 settles
execution adequacy first.


```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 5.2 — The execution ledger, read from the archive rather than from the plan.** *stop* marks a report-only count read at the exogenous stop of 2026-08-27; *sealed* marks a quantity held closed until the single confirmatory look.
```{=latex}
\par\endgroup
```

| Quantity | Value | Status |
|---|---:|---|
| Arms run | 9 | |
| Cells in the eleven-line grid | 70 | |
| Seeds banked in every cell | <!--RUNG:100-->102 | stop |
| Achieved rung on the E1 ladder | <!--RUNG:100-->100 | stop |
| Candidate budget per arm | 30 | |
| Trainings executed and archived | 25,602 | stop |
| Environment steps | 10.24 billion | stop |
| Task-hours consumed | 36,446 | stop |
| Processor-hours consumed | 288,533 | stop |
| Candidates rejected by the static gate | 193 | stop |
| Replication legs executing, none truncated | 10 of 10 | stop |
| Logged deviations, all ops-only | 1 | |
| Authoring spend on this archive | $45.50 | stop |
| Rung-100 $\sigma_D$ re-estimate at $B^{*}=400$k | — | sealed |
| Per-leg bank-gate verdicts | — | sealed |

The E1 ladder is [30, 100, 189, 279, 340, 403, 568] and the registered target is rung 403. The ten
legs climb it in lockstep, so every number below is tagged at one achieved rung, and five already hold
the 568-seed ceiling. Both compute figures sum per-task durations rather than calendar time, because
tasks run in parallel: the calendar age at the 2026-08-09 read was roughly 280 hours. Both are lower
bounds, since a task counts only once its ledger line returns.

The spend figure needs its account. R81 registered the $30 total as a hard cap in code, and R83
superseded it the next day, still pre-data, leaving a planning ceiling.[^spend] No code here ever
stopped an experiment for cost, and what does stop it is the seed-rung rule and the leg calendar
gate. The two levers that would have held the total under $30, dropping legs or seating a cheaper
model, would both have removed open-weight evidence, so the overrun is its authorised price.

## 5.2 Both co-primary tests, read by a rule fixed in advance

The headline is the pair of co-primary tests, the TOST bound against
the ±0.05-DSR SESOI and then the one-sided IUT *p* per leg. H2-RA (deflated net Sharpe at the
headline 10 bps) and H2-Tail (CVaR-5%) are each an IUT over the same three legs, distributional
against *scalar*, *placebo* and *scalar_cvar5*, one-sided at $\alpha=0.05$. Table 5.3 carries each
co-primary, and Figures 5.1 and 5.2 the per-leg statistics by line and against seed count.

The interval below is a difference between two selected programs, the unit §4.7 registers.[^unit]

[^unit]: The confirmatory unit is the (program, seed) pair, so the paired bootstrap resamples the training seed alone and authoring variance sits outside the interval by construction.

We state the instrument's power before the verdict, not after it. Table A.4 fires it on generated
data whose answer is known, at the banked 102 paired seeds: on a true zero it returns EQUIVALENT in
74.8 per cent of replications, and 43.0 in the algebraic worst pairing case, and never the opposite
verdict.[^powerread] The predicted branch is available at this depth rather than assured, and
INCONCLUSIVE is a likely answer the design names in advance.

[^powerread]: At the pilot pairing correlation of -0.14 the rate is 71.5 per cent, and the median number of lines returning EQUIVALENT on a true zero is 8 of 11 at that correlation and 5 of 11 in the worst case.

<!-- ⛔ NO SPACE RESERVE HERE, AND THAT IS MEASURED RATHER THAN CHOSEN (2026-08-10). A
     \Needspace reserve was added before this caption and before Table 5.8's, and both were
     REMOVED again. Where the reserve fires beside a longtable whose first row is taller than
     the space it leaves, longtable emits its column header ONCE at the top of the new page,
     then the caption, then the header AGAIN above the first row. Measured on the compiled
     artefact: two toprule/midrule pairs on one page with the caption sitting between them, on
     the pages carrying Table 5.3 and Table 5.8. An orphaned header above a caption is a worse
     defect than the one the reserve was added to fix, and both tables sit with their bodies
     without it -- Table 5.8 because it is now set at \footnotesize. The same reserve works
     cleanly at Tables 1.3 and 4.1, where it fires at a plain paragraph boundary with no table
     already in flight. Re-measure before ever reintroducing it here. -->


```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 5.3 — The two co-primary verdicts, sealed until the confirmatory look of 2026-08-27.** How the sealed numbers will be read is committed before either verdict exists. *Observation:* each row will carry the 90 per cent equivalence bound with its EQUIVALENT, INCONCLUSIVE or NON-EQUIVALENT verdict, and the one-sided intersection-union $p$ as the maximum over the scalar, placebo and `scalar_cvar5` legs.
```{=latex}
\par\endgroup
```

<!-- CAPTION, 2026-08-10. It read "The two co-primary verdicts, each with its mechanism, uncertainty
     and counterfactual" — which promised verdicts the exhibit does not yet contain, and spent its
     remaining words restating the four row labels the reader can already see in the stub column.
     The seal is now stated in the caption itself, so a reader meets the reason for the empty cells
     before the cells. Word-neutral: eleven words out, eleven words in. -->


| | H2-RA, Sharpe legs | H2-Tail, CVaR-5% legs |
|---|---|---|
| Observation | sealed | sealed |
| Mechanism, the instrument | SQ1, responsiveness | SQ2, transmission |
| Mechanism, the design fact | tail-blind selection at $\lambda=0$ | fed on training, tested on a sealed CVaR |
| Uncertainty | $\rho\approx-0.14$, so pairing does not help | the lowest-power leg of the family |
| Counterfactual | a tail-rewarded selector, or a responsive designer | a larger fed delta, finer rendering, or a corner-reaching action space |

The depth-matched pool is the better estimate of the selection step. Table A.3 re-selects every winner at
its line's shallowest depth, and the winner changes in 5 of the 55 cells. Repairing our own allowlist gap
returns twelve wrongly rejected candidates to the confirmatory line, whose depths become 29, 30, 29, 28
and 28, moving the deepest pool from the treatment arm to its comparator. Both corrections run against
our own hypothesis. Neither becomes the headline outcome pool, and the archive is the reason. Only
the winners that actually froze were re-run on the sealed leg, so no depth-matched or repaired winner
has a test record at all.[^equalk]


![**Figure 5.1 — The treatment-minus-control contrast, one row per authoring line.** Almost every interval excludes zero and the lines still disagree in SIGN, five of eleven favouring the treatment. Each row is the distributional-minus-scalar difference, paired on the seed index; bars are 95 per cent percentile bootstrap intervals over 102 paired seeds.
](../outputs/figures/F5_cross_line_forest.pdf)

![**Figure 5.2 — The estimator, not just the estimate: how the contrast settled as seeds accumulated.** Seeds enter in the registered order 0, 1, 2 and so on, never sorted. **What to conclude:** no inference was drawn at any prefix, and the curve is a diagnostic of whether the estimate had settled, not a result.
](../outputs/figures/F5_seed_trajectory.pdf)

## 5.3 Nine controls, each answering a threat named before the data were seen

Nine registered controls defend the primary result, all specified in Chapter 4 rather than restated
here, five in Table 4.7 and four in Table E.4. The placebo and scrambled controls are overlaid on the
manipulated arm's own axes under rule 3, the scrambled one entering outside the conjunction.
Figures 5.3 and 5.4 draw the seed clouds beneath.

![**Figure 5.3 — The random object behind the mean: every seed, every arm.** The arms overlap heavily and the within-arm spread is large relative to the distance between arm centres, which is why a table of means alone would overstate how far apart these conditions are.
](../outputs/figures/F5_seed_dispersion.pdf)

![**Figure 5.4 — The same clouds for all eleven lines, so the dispersion claim rests on the panel rather than on one author.** One point per seed, 102 per arm, **all eleven panels sharing one vertical scale**, each printing its own median within-arm interquartile range. **What to conclude:** spreads run 0.15 to 0.40, and the ring marking the best arm moves from panel to panel with no pattern.
](../outputs/figures/F5_dispersion_all_lines.pdf)

## 5.4 The designer is set against the whole hand-written canon, not one incumbent


The designed reward is set against the whole hand-written canon, at node N6. Naming which hand-reward is
best by its sealed-test result would be the comparator data-snoop of White [`white2000reality`], so H1 is
an intersection-union test over all eleven names whose $p$-value is the maximum of the eleven legs.
Nothing is selected. Contesting the entire standard toolkit is, to our knowledge, a first in this lineage,
since Eureka, Text2Reward and REvolve each contest a single hand-written reward [`ma2024eureka`;
`xie2024text2reward`; `hazra2025revolve`].

One asymmetry remains and it favours us. The designed reward is the survivor of a thirty-candidate
search. Each hand-designed reward is a single un-tuned specification, and no deflation counterweight
corrects for that (§B.6.5). Dominating an un-tuned bar is the weaker claim, and we make only the
weaker one.

Two reporting rules follow, both about power. H1 carries $\alpha$ only on upstream rejection, so the
local $\alpha$ it inherits at node N6 is printed beside its verdict, and at zero it is reported as
report-only.[^h1n] The verdict is a dominance profile rather than a binary, because *dominates ten of
eleven, ties one, loses to none* is the more useful statement. Each quantity is sealed until the single
confirmatory look.
H3 and H4 are read by rules fixed in advance, and what a verdict licenses matters more than the
verdict.[^h34] **An H4 non-rejection licenses nothing at all**, because no inferiority test is
registered.

[^h34]: H3 bounds reflection against best-of-$N$ at matched budget by TOST, so a non-rejection there licenses nothing unless the bound clears the margin. H4 is a beat-the-best intersection-union test against the four optimisers at node N4, so a rejection licenses that and nothing else.

## 5.5 What a reward design changes is how heavily the policy trades

Table 5.5 runs the chain from the fed signal to the authored code, the policy and the tail.
Table 5.4 gives each link its instrument. All five are registered report-only, so no cell there is
sealed.[^mechreg] Figures 5.5 and 5.6 draw the sealed-window path and the turnover channel. Table 5.6 carries the two links measured by executing the archived programs.


```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 5.4 — The mechanism instruments, and the limit each one carries.** Five instruments interrogate three links, and each carries a stated limit rather than an implied one.
```{=latex}
\par\endgroup
```

| Instrument | Link | The limit it carries |
|---|---|---|
| Responsiveness | 1, the designer | a break means the channel is unread, not unhelpful |
| Mediation [`imai2010identification`; `mackinnon2000equivalence`] | 1 to 3 jointly | rests on sequential ignorability, so it is descriptive |
| Per-arm fingerprint rows | 1, per arm | the scrambled row is the floor a real effect must clear |
| Reward-program differential | 2, the code | near-zero distance means one objective re-shaped |
| Learning-curve diagnostic | 3, reward to policy | separates mechanism-limited from budget-limited |


```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 5.5 — The chain measured link by link, by executing the archived programs.** Link 1 asks whether a property of the authored code moves with the fed block; link 2 asks whether that property then moves behaviour. **What to conclude:** measured by execution rather than by reading the code, the chain breaks in two places rather than one, and the rival row is the largest effect in the exhibit.[^chaininst]
```{=latex}
\par\endgroup
```

| Link 1, within-chain association | Treatment | Dose | Scrambled | Carries |
|---|---:|---:|---:|---|
| Curvature of the left-tail penalty | 0.016 | 0.008 | 0.098 | no |
| Loss aversion | 0.021 | 0.014 | 0.120 | no |
| Turnover charge | 0.111 | 0.043 | 0.035 | yes |
| Reward range | 0.030 | 0.043 | 0.098 | no |
| Relative tail curvature | 0.061 | 0.031 | 0.053 | yes |
| Relative turnover charge | 0.037 | 0.006 | 0.120 | no |

| Link 2, behaviour to outcome | Correlation | 90% interval | Permutation $p$ |
|---|---:|---|---:|
| Loss aversion against worst-5% loss | +0.430 | [+0.252, +0.648] | 0.020 |
| Relative turnover charge against turnover | −0.262 | [−0.394, −0.214] | 0.058 |
| Relative tail curvature against worst-5% loss | −0.070 | [−0.320, +0.105] | 0.594 |
| Rival: realised turnover against worst-5% loss | −0.749 | [−0.861, −0.528] | <0.001 |

The loss-aversion tie strengthens to +0.539 once realised turnover is partialled out, so it is not
the turnover channel under another name. Figure 5.5 draws the two programs.

[^chaininst]: Link 1 is measured within a candidate chain, so a model's own authoring style differences out; link 2 runs over the 55 cells at 87 paired seeds. The instrument is calibrated against three known answers and recovers 1.000, 3.000 and 2.000 exactly, and 1,479 of 1,494 archived programs re-execute, the failures being three distinct programs by the weakest model.

![**Figure 5.5 — The reward programs the models wrote, executed and plotted as functions.** Each arm's frozen winner is run over two sweeps, as the median over five warm-up seeds, each curve scaled to its own peak. **What to conclude:** the treatment did change the code, penalising a $-4$ per cent day 4.16 times as hard as it rewards a $+4$ per cent day against 1.26 for the scalar control. That asymmetry did not come with a heavier turnover charge.
](../outputs/figures/F5_reward_response.pdf)

**Why the reward's magnitude matters at all, when the environment never sees it.** Authored reward
magnitude spans a factor of 9.8 million, from a root-mean-square of 0.0205 to 201,045, and Soft
Actor-Critic reads reward scale as an inverse temperature. The gear train runs from magnitude to the
value normaliser at $r = +0.937$, from the learned temperature to turnover at $-0.377$, and from
turnover to risk-adjusted return at $-0.992$.[^gears2] Holding magnitude fixed leaves the second link
intact at $-0.439$ and holding temperature fixed leaves the third intact at $-0.991$, so the last
gear is not a restatement of the first. A designer who never intended to set an exploration
temperature sets one anyway, by choosing units.

[^gears2]: Ninety-five per cent intervals, in order: [+0.890, +0.971] for magnitude to normaliser scale, [−0.365, +0.836] for magnitude to temperature, [−0.684, −0.062] and [−0.756, −0.202] for temperature to turnover before and after holding magnitude fixed, and [−0.996, −0.982] and [−0.996, −0.974] for turnover to risk-adjusted return before and after holding temperature fixed. The magnitude-to-temperature interval spans zero, which is why the account runs through the normaliser rather than directly. Every interval is a percentile bootstrap at 10,000 resamples, computed two ways, over the 55 cells and clustered on the 11 authoring lines, the wider governing.



![**Figure 5.6 — The path, not only the endpoint.** A terminal Sharpe is a path functional, and the number the tables report is a late reading of a curve that moved by more than a full Sharpe unit inside the window. The horizontal axis is the end of the expanding window over the sealed test span 2020-03-30 to 2026-06-30, 1,571 sessions; the window opens at 126 sessions, about six months, so the variance estimate exists.
](../outputs/figures/F5_sharpe_trajectory.pdf)

The agent is not overfit, which is the verdict this design was built to test. Three measurements decide
it. Validation fitness transfers positively to the sealed window. The top validation quartile averages
$+1.0644$ test net Sharpe against $+0.6678$ for the bottom. And 53 of the 55 frozen cells are profitable
out of sample. One thing would overturn the verdict: a negative validation-to-test correlation, which is
the signature of selection overfitting.[^o8] The step budget is registered and identical in every arm, so
it cannot tilt a contrast. Figure 5.7 shows what does.

[^o8]: Every figure behind this verdict is report-only and pooled across arms, so none reads the sealed comparison. The Spearman validation-to-test transfer is $+0.2559$ against the Pearson $+0.5627$. On training progress the study reports what it measured and declines the inference the measurement does not carry. The critic loss falls from a median 2.7043 to 0.0032 and is still easing at the registered cap in about three quarters of trainings, at two depths that agree: 76.0 per cent over 5,610 sealed-test trainings at the banked depth and 75.5 per cent over 4,785 at the 87-seed prefix. A soft-actor-critic temporal-difference loss is measured against a moving bootstrapped target, so it descends for as long as the target moves and its slope is not a convergence test. The quantity that would settle the question is the training return curve, and `metrics.train_curve["return"]` is NaN in every archived record, so this study does not claim convergence and does not assert its absence either. The budget itself was set by a registered rule reading a measured knee, and that rule doubled it from 200,000 steps against this project's own standing recommendation before the design was frozen.

![**Figure 5.7 — The mechanism, measured: what a reward design changes is how heavily it trades.** One point per authoring line, at the mean paired change with 95 per cent bootstrap intervals on both axes over 102 paired seeds, Spearman $\rho = -0.982$. **What to conclude:** a reward design acts on performance through the cost of trading, not through the tail-aware behaviour it was meant to induce.
](../outputs/figures/F5_turnover_mechanism.pdf)

![**Figure 5.8 — Seed-to-seed instability by model, ordered.** The lines differ widely in how far a reward design's outcome moves when only the seed changes, which is why no mean is quoted anywhere in this chapter without its dispersion beside it. **What to conclude:** the left-to-right rise is arithmetic, because the axis is sorted by the quantity plotted; what the ordering licenses is the capability reading argued in the text.
](../outputs/figures/F5_capability_gradient.pdf)

### 5.5.1 A specification-gaming mechanism the pre-registration named in advance

Observation. Nine independently authored programs, across four models and three arms, converge on one
construction:

$$\texttt{mean\_ret} \,/\, (\texttt{downside\_vol} + 10^{-8}).$$

Mechanism. The author guarded division by zero. Nothing guards magnitude. The added $10^{-8}$ prevents a
singularity without bounding the quotient. As `downside_vol` falls the reward grows without limit,
reaching order $10^{8}$ and breaching the execution guard. The direction is the interpretive point.
`downside_vol` shrinks as the agent succeeds, so the reward punishes its own success by construction.

Account. The pre-registration named this class before any campaign datum existed, in a forensics
category flagged on code shape independently of fitness.[^r41] The observed instance is literally the
form that amendment names. A registered prediction about the kind of pathology an automated designer
produces was confirmed nine independent times.

Counterfactual. Substitution runs from 4.6% to 6.3% across the five arms, and every Wilson interval
overlaps every other.[^wilson] The guard cannot produce a between-arm effect. The mechanism is a property
of automated reward authorship, not of our instrumentation.

The *phenomenon* is pre-registered, and the *threshold* at which the guard fires is not.[^guard]

## 5.6 The realised results against the branch the theory predicted in advance

Table 5.6 maps the realised results onto the three pre-registered branches of §C.7. The verdict is the
conjunction of its four signature rows, so the outcome is a *decided prediction* of either sign.

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 5.6 — Realised results against the §C.7 pre-registered prediction branches.** The branch is decided by the conjunction of all four signature rows, so the two report-only rows already read here cannot settle it alone.
```{=latex}
\par\endgroup
```

| §C.7 signature | Predicted, null branch | Realised |
|---|---|---|
| H2-RA, net Sharpe legs | tie | sealed |
| H2-Tail, CVaR-5% legs | tie | sealed |
| Responsiveness | $\le 0$ | report-only, read at the stop |
| Reward-program differential | none or reversed | report-only, read at the stop |


The branch verdict itself, and the one-line theory-tied interpretation §C.7 attaches to it, are
*(sealed until the single confirmatory look, 2026-08-27)*.

## 5.7 Ten further models author the identical arms, and none was dropped (report-only)

Ten further models author the identical five language-model arms under byte-identical prompts. Nothing in
this section or §5.8 gates H1 to H4. The roster, the pins and the calendar gate are frozen in `model_suite`,
and every leg's archive passed the same write-then-verify bank gate as the campaign root.
<!--RUNG:100-->All ten legs are executing and none is truncated as at 2026-08-09. Five already hold the
registered 568-seed ceiling. The per-leg headline contrasts, the T0-floor inclusion list and the per-leg
bank-gate verdicts are sealed until the single confirmatory look.

The contamination screen is the one part of this section worth reading before that look, because its
result is not what the flag count says. Every leg was screened before launch and six of ten raised a
canary flag. Human adjudication of those flags recorded four genuine confabulations, in `haiku-4.5`,
`kimi-k3`, `nemotron-3-super` and `qwen3.5-9b`, against two false positives in `qwen3.6-27b` and
`sonnet-5`, both of which correctly identified the canary as synthetic. One leg, `deepseek-v4-pro`, is
unverified rather than flagged, its answers having been truncated by an output cap that amendment R113
later raised. No leg was excluded, downweighted or re-run.

That disposition is structural rather than lenient. The canary is a synthetic arithmetic sequence,
twenty daily returns rising linearly from −0.0917 to +0.0917, corresponding to no market episode at
all, so confabulating a specific crash for it is evidence of confabulation under identification
pressure and not evidence that a model has seen the sealed window. The screen routes to a human and
issues no verdict, which is why the adjudicated split is the measure and the flag count is not.

## 5.8 The capability gradient is readable before any outcome is scored (report-only)

### 5.8.1 Authoring reliability — the one capability measure that needs no sealed outcome

Every other quantity in this section waits on the sealed test. Table 5.7 does not, because it asks a prior
question. Can the model write executable objective code at all? It is read from the complete failure ledger,
which records only whether an authored program cleared static screening and executed, never how it performed.


```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 5.7 — Authoring reliability by model: the share of each line's 150 registered candidate slots lost, with a 95% Wilson interval and the author-side against node-side split.** The loss rate spans two orders of magnitude, so authoring executable objective code is a property of particular models.
```{=latex}
\par\endgroup
```

| Authoring model | Lost / registered slots | Lost (%) | 95% Wilson interval | Failure rows: author-side / node-side |
|-----|---|---|---|---|
| `qwen3.5-9b` | 129 / 150 | **86.0** | [79.5, 90.7] | 35 / 97 |
| `nemotron-3-super` | 36 / 150 | 24.0 | [17.9, 31.4] | 16 / 25 |
| `glm-5.2` | 25 / 150 | 16.7 | [11.6, 23.4] | 8 / 18 |
| **`opus-5` (confirmatory seat)**| 18 / 150 | **12.0** | [7.7, 18.2] | 21 / 1 |
| `qwen3.6-27b` | 16 / 150 | **10.7** | [6.7, 16.6] | 3 / 13 |
| `deepseek-v4-pro` | 12 / 150 | 8.0 | [4.6, 13.5] | 6 / 8 |
| `gemini-2.5-flash` | 10 / 150 | 6.7 | [3.7, 11.8] | 8 / 4 |
| `haiku-4.5` | 6 / 150 | 4.0 | [1.8, 8.5] | 2 / 5 |
| `gpt-5.6-luna` | 4 / 150 | 2.7 | [1.0, 6.7] | 0 / 4 |
| `kimi-k3` | 1 / 150 | 0.7 | [0.1, 3.7] | 0 / 1 |
| `sonnet-5` | 0 / 150 | 0.0 | [0.0, 2.5] | 0 / 0 |

*Measured 2026-08-09 by `docs/ops/authoring_reliability.py`. Closing rates are (to be read at the exogenous stop, 2026-08-27).*

These rates supersede an earlier measurement that counted only node-side rejections, and the
understatement was non-uniform, so it re-ordered the gradient rather than shifting it.[^superseded]
The load-bearing contrast survives the correction. The Qwen pair is a within-family comparison with
the reasoning configuration pinned identically across both members, and 86.0% against 10.7% isolates
capacity from vendor, prompt and harness.[^astsplit] The bottom anchor stands. A model failing
most of its attempts leaves the reflection loop nothing to reflect on, which §6.1 develops as a
threshold rather than a slope.

The legs share the market panel and the common-random-number seed set *by design*, so they are not independent
replications and we never count them as if they were. The synthesis therefore has two tiers. The seven cross-model instruments below set
them beside the two registered capability instruments and the stability ordering of Figure 5.8, which is a
display choice.[^gradient] The
hand-reward canon runs after the headline at the lowest execution priority.[^canonhist]
<!--RUNG:100-->All eleven members have executed and each holds the same contiguous 102-seed prefix as every
other cell as at 2026-08-09 *(to be read at the exogenous stop, 2026-08-27)*.

Table 5.8 is the descriptive eleven-line reading the abstract quotes.[^desc]

[^desc]: No row is a hypothesis test.


```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 5.8 — The eleven-line descriptive reading, at 102 paired seeds.** Read the interval column, not the point estimates.
```{=latex}
\par\endgroup
```

| Quantity | Estimate | Interval |
|---|---:|---|
| Treatment minus `scalar`, net Sharpe | −0.061 | [−0.251, +0.040] |
| Treatment minus `placebo`, net Sharpe | −0.196 | [−0.501, −0.070] |
| Treatment minus `scalar_cvar5`, net Sharpe | −0.171 | [−0.537, −0.001] |
| Treatment minus its scrambled control, net Sharpe | −0.024 | [−0.167, +0.097] |
| Lines where treatment beats all three comparators | 0 of 11 | a count |
| Best arm by line | see caption below | a count |
| Turnover against net Sharpe, across the 11 lines | r = −0.986 | [−0.997, −0.941] |
| Turnover against net Sharpe, across the 55 cells | r = −0.992 | [−0.997, −0.983] |
| Turnover against gross Sharpe, across the 11 lines | r = −0.967 | [−0.992, −0.657] |
| Slope against turnover, net | −1.616 | [−2.068, −1.456] |
| Slope against turnover, gross | −0.341 | [−0.435, −0.184] |
| Share of the turnover damage that is cost | 78.9% | [76.4, 90.3] |
| Turnover span across the 55 cells, per day | 0.603% to 88.83% | a range |
| Variance share, model identity | 27.9% | [11.5, 35.1] |
| Variance share, arm | 14.8% | [7.8, 29.4] |
| Variance share, model by arm interaction | 34.8% | [23.5, 38.2] |
| Variance share, residual | 22.5% | [14.3, 43.8] |
| Shortfall constructs in code, treatment | 16 of 277 | [3.6, 9.2]% |
| Shortfall constructs in code, scrambled control | 17 of 280 | [3.8, 9.5]% |
| Fed statistics named in code, treatment | 4 of 277 | [0.6, 3.7]% |
| Fed statistics named in code, scrambled control | 12 of 280 | [2.5, 7.3]% |

We read four things off that table. No condition wins everywhere. The per-line best arm is `placebo` on
five lines, `scalar_cvar5` on four, `scalar` on one, the scrambled control on one, and the treatment on none.
The fit against turnover is similar before and after costs but the magnitude is not, so four fifths of the
damage is what trading costs.[^twoest] The four variance shares overlap, so the interaction's exclusion of
small values is established and the ordering is not. And the shortfall-construct counts are not separated
from parity. Treatment against the two uninformed controls pooled is +2.6 points on a 95 per cent Newcombe
interval of [−0.3, +6.2], with the scrambled control level or a little above.[^denoms]

[^denoms]: Every denominator is that arm's own eleven-line program count.


```{=latex}
\Needspace{3\baselineskip}
```

Seven cross-model instruments are named and directed before any of them can be read, so the synthesis is a
procedure fixed in advance, and all seven stay sealed until the single confirmatory look.[^sevenins] Every
$p$-value is Benjamini-Hochberg-corrected across the ten-leg report-only family. The suite traces
the envelope-to-realisation gap along the capability axis. The Blackwell envelope of Appendix C binds an
optimal author, and the legs measure the gap a bounded one realises.

[^sevenins]: Two are inferential, the descriptive replication count on the CVaR leg and a per-seed joint-flip permutation test at 10,000 replications. One is the bounded-effect interval on the pooled mean CVaR-5% difference. The remaining four read the capability axis: the three-signature gradient adjudication, whose registered prediction is flat-at-zero, a family-pair difference-in-differences over the open, closed and same-vendor pairs, a capability regression against the pre-declared external anchor, and generation-indexed responsiveness across the loop's six generations.[^unwired]

[^adds]: A descriptive interval says where the contrast lies.

[^marks]: A row marked sealed until 2026-08-27 carries alpha and so carries no number today.

[^mechreg]: The registration states this as configuration, under the `mechanism:` key of `config/preregistration.yaml` as `report_only: true` and `disjoint_from_m6: true`, and in words at `PREREGISTRATION.md` section 2a.

[^unwired]: Three of the seven rows, and the Benjamini-Hochberg correction beneath the table, come from estimators implemented and unit-tested in `src/inference/cross_model.py` but not called by the analysis entrypoint as the code stands on 2026-08-11: `pair_did`, `capability_regression`, `generation_indexed_responsiveness` and `leg_family_bh`.



[^spend]: R81 registered the $30 total as hard-capped in code. R83 kept it as a planning ceiling, so the registered trim order was never exercised. The ledgers read on 2026-08-09 from `outputs//spend_ledger*.jsonl` give Anthropic $53.50 and OpenRouter $10.04. The registered single-look author accounts for $30.10 and the ten legs for $15.40, the largest leg `sonnet-5` at $5.14 and the smallest `qwen3.5-9b` at $0.07.

[^h1n]: An intersection-union $p$-value is the maximum over legs, so a lower-powered leg would disproportionately be that maximum.

[^guard]: The threshold is an implementation guard added by an internal audit on 2026-07-22, pre-data but outside the frozen hash, and absent from both `PREREGISTRATION.md` and `config/preregistration.yaml`.

[^wilson]: Each rate carries a Wilson 95% interval on that arm's own denominator. The five denominators sum to a pooled $n = 1{,}237$ which is not the interval's $n$.

[^r41]: R41 registers the category verbatim as "rewards of the form `return / (variance + eps)`, unbounded above as realized variance goes to 0 (the critic-explosion mechanism)", anchored to the specification-gaming literature.

[^superseded]: The panel quoted until 2026-08-03 read rejections from markers written on the compute node, and the author-side gate is driver-side, so no marker can exist for that class.

[^astsplit]: Author-side means the output never became a runnable reward. The bottom leg is the opposite shape, 97 of 132 rows node-side, which is why the within-family Qwen contrast is the reading our screen cannot have manufactured.


[^twoest]: The second estimator runs on the 55 cells in levels rather than on eleven contrasts, clustered on the authoring line. They agree at $r = -0.986$ against $-0.992$, with slopes $-1.616$ [-2.068, -1.456] and $-1.698$ [-1.825, -1.594], each point estimate inside the other's interval.

[^gradient]: The ordering is a display choice. Regressing dispersion on authoring reliability across the full roster gives a Spearman $\rho$ of $+0.273$ at $p = 0.417$.

[^canonhist]: R105 expanded the H1 comparator to the full eleven-name canon, so the earlier secondary panel described under R97 no longer exists.

