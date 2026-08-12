# Chapter 6 — Discussion and Limitations

## 6.1 A null that locates where the chain breaks is a boundary condition, not an absence

The dominance envelope of §1.3 bounds what an *optimal* user of the fuller feedback block could extract. This
chapter reports what a bounded one attained, and where the chain between them gave way. The three
pre-registered sub-questions each interrogate one link, so a break locates the failure (Table 5.4), and Table 6.1 grades every registered question against its own prediction. The
performance equivalence is the backdrop against which the break is read, not the discovery itself.

<!-- COMPRESSED 2026-08-11: 145 counted words to 75. What went was a restatement of the research
     question and of the Blackwell dominance result, both of which Chapter 1 s1.3 already states, with
     the equations, on the reader's path. This is Mensh and Kording's Rule 4 (cover each subject once)
     and the zig-zag defect the project's own measurement recorded. What survives is the one thing the
     Discussion actually needs from that material -- envelope above, bounded realisation below, and the
     break between them -- plus both exhibit pointers. The body stood 3 words under an 11,000 limit
     when this was cut. -->



```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 6.1 — The pre-registered questions, their predictions, and where each verdict is finalised.** Every prediction was written before the sealed window opened, and three of the four hypotheses predict a tie or carry no directional prediction at all.
```{=latex}
\par\endgroup
```

| Question | Prediction | Verdict in |
|---|---|---|
| H1, dominate the hand-reward canon | confirmatory, node N6 | §5.4 |
| H2-RA, risk-adjusted net Sharpe | tie | §5.2 |
| H2-Tail, CVaR-5% | tie, or a TOST-bounded interval | §5.2 |
| H3, iterative against single-shot | no directional prediction | §5.4 |
| H4, designer against the optimisers | confirmatory, node N4 | §5.4 |
| SQ1, does the authored code move? | weakly or negatively, $\le 0$ | §5.5 |
| SQ2, does the realised tail follow? | little movement, severed upstream | §5.5 |
| SQ3, is any response tail-specific? | not specific, placebo-matched | §5.5 |

The directional prototype locates the realised system on the *Null* branch of that table. Its apparent tail
advantage did not survive its own zero-information placebo control, and its authored reward code was, if
anything, *less* responsive to larger movements in the fed tail.

The distinction rests on the severity requirement of error statistics [`mayo2018severetesting`;
`altman1995absence`]. A non-rejection is evidence of absence, and not mere absence of evidence, precisely
when the design would have detected a genuine effect with high probability. That probability decomposes
into three legs and the design instruments each: responsiveness power, search adequacy and equivalence
power.[^severity] A reviewer's "you did not search hard enough" lands on one instrumented leg, never on
the null itself.

[^envelope]: This is not a lower bound on the Le Cam deficiency.

[^severity]: Responsiveness power comes from the dose-response sub-experiment and its positive control, which sit upstream of the candidate search.

Three readings make this a positive scientific result. The first is a corroborated prediction about the
gap between the envelope and its realisation, which the theory predicts from a tail-blind selector and a
non-responsive designer. On the designer's own decision problem the risk gap
between seeing the score alone and seeing it with the six lower-tail statistics is $-0.0037$, inside its
own permutation null. A bounded predictor realises no gap, so nothing of the envelope is demonstrated
here (§C.4.1).[^envelope] The second is about robustness. By the duality of §C.6 the lower tail is a
distributional-robustness signal, and the null says this designer does not convert it into more robust
reward code at this budget. The third is a boundary condition for the automated-discovery agenda.
Language models can discover objectives. Which information they are shown did not, here, change what they
discovered.

Two mechanism analyses sharpen that interpretation. One asks whether the arms authored genuinely
different objectives, or near-policy-invariant re-shapings of a single one.[^probe] The other decomposes
the arm's effect into an indirect path through the authored code, under a sequential-ignorability
assumption that is strong and untestable [`imai2010identification`].[^suppression] Two findings from the
literature agree with what they return. Models' risk attitudes are real but steered by surface
conditioning [`hartley2025personality`], and where an agent merely consumes CVaR estimates computed for
it, tail-aware behaviour is readily obtained [`chergui2025uncertainty`]. The break is therefore in the
authorship of tail-risk information, not in its consumption. Richer feedback is not self-acting.

[^probe]: The probe counts the declared tail constructs each authored reward uses and compares them through an identifier-invariant structural comparison built on the regret-bounded EPIC/STARC pseudometrics.

[^suppression]: An indirect effect reliably non-zero yet opposite in sign to the direct effect is inconsistent mediation, or suppression, a recognised identifiable quantity rather than a failed manipulation [`mackinnon2000equivalence`; `orourke2018suppression`].

The mechanism layer has several legs, so its multiplicity stance is stated explicitly. No mechanism
statistic gates H2 or can convert the pre-registered null into a performance claim, and the reading is the
Benjamini-Hochberg-corrected picture rather than a single uncorrected leg.

### Aliasing, and the layer at which it bites

The concurrent study that named this axis also named its failure mode. Aliasing occurs *"when
the scalar reward maps distinct failure modes into the same value"* [`gallego2026beyondscalar`], so richer
metrics disambiguate, which is the informational case this study tests.

**On that axis their finding and ours disagree.** They report denser feedback improving
model-synthesised code. We widen the same channel and find the effect bounded against its own scrambled
twin. Either the object differs, theirs being policy code and ours a fixed agent's reward, or the
enrichment was real and something downstream discarded it. Our own formatter did exactly that, so their
result is not refuted here. What this study adds is the layer at which it can be undone.

A second layer of aliasing exists that enrichment alone does not fix. Gallego's aliasing is a property of
the *statistic*, in that the scalar genuinely lacks the distinguishing information. Ours was a property of
the *rendering*: the fed vector carried the information and the number formatter threw it away.[^render]
The designer never sees a float. It sees characters, and two candidates whose tails genuinely differed
were identical at the page. External work on numeric representation cannot establish this, because the
collapsed values reached the tokeniser already identical.[^numeracy]

[^render]: At the original two-decimal header precision, 229 of 240 real fitness values rendered literally as `0.00`, and 240 candidates produced four distinct strings. At the original three-decimal tail precision, 90.1% of pairs separated by $10^{-4}$ rendered as the same string, against 0.0% at four decimals.

[^numeracy]: Magnitude is broadly recoverable from embeddings, with the exception that sub-word models struggle because two numbers similar in value can divide very differently [`wallace2019numbers`]. The rest of the family shows the value-to-token map is causal rather than incidental [`zhang2024counting`; `baeumel2025digitwise`; `zausinger2025ntl`; `dutulescu2026valueaware`]. And the same literature reports that comparison of distinctly printed numbers is effectively solved in frontier models [`kreitner2026bittokens`].

The generalisation transfers. Enriching a feedback channel does not defeat aliasing if the
presentation layer re-aliases it downstream, and because the enrichment is visible in the design while the
quantisation is not, this failure is *invisible in exactly the systems that have tried hardest to avoid it*.
The danger has a direction. A study whose channel is silently re-aliased observes no effect of channel
content and concludes that richer feedback does not help, when it has measured its own formatter. Rendering
precision was therefore promoted to a registered design parameter before any confirmatory datum existed,
which is why a null here reads as a statement about the designer, not the renderer.

### Beyond portfolios: three findings that constrain any automated design loop

Three of this study's findings are not about asset allocation. Each constrains automated design loops
generally.

The first concerns how generated artefacts should be scored. The danger is not the artefact that fails. A
candidate that fell back to the harness default on 99.98% of its 400,000 calls scored $7.8	imes10^{-6}$
and eliminated itself, because total failure is self-limiting. A candidate that fell back on 49.98% held
the highest fitness in its arm, at $+0.2336$ against a best eligible $+0.000124$, and was removed only by
the execution floor. The fallback had silently supplied what the authored code did not. Outcome quality
cannot separate those cases, because the blend optimises exactly the quantity being scored. Any pipeline
that accepts machine-generated code on the strength of its results, and that has a fallback path, is blind
where contamination pays best. It needs an execution audit.

The second concerns iterative self-improvement. A reflection loop requires a prior success to reflect on, so
below some authoring reliability it never starts, no accepted artefact existing to critique. The capability threshold for self-improvement is therefore not "good enough to improve" but
"good enough to succeed once", a bar invisible to any evaluation that reports mean quality in place of the rate
of usable output.

The third concerns objective specification. Of the eleven expert-designed objectives in the comparison
set,[^canon] ten carried genuine signal and then surrendered it to a single unpriced friction, and the one that
retained it charged for that friction directly. This is not naive designs being caught out. Eight of the ten losers penalise risk
explicitly, and every one of them computes its penalty on the environment's net-of-cost return
series.[^measures] The exception trades roughly a hundredth of the turnover of
the other ten, at $0.0084$ against $0.873$, and is net-positive on all 102 of its seeds.

[^canon]: Re-derived first-hand from 1,122 archived sealed-window records, the eleven canon members at 102 contiguous seeds over 1,571 trading sessions each. Pooled, the mean gross Sharpe is $+0.9640$ against a mean net of $-0.1056$, a wedge of $1.0696$. The intervals travel from the earlier 30-seed measurement: gross $+0.934$ to $+0.992$, net $-0.134$ to $-0.080$, wedge $1.065$ to $1.076$.

[^measures]: The eight are variance, conditional value-at-risk, drawdown, downside deviation, an online Sharpe ratio and its downside companion, quadratic utility and volatility scaling.

Sophistication in the *modelled* quantity did not substitute for pricing the dominant *real* cost, a
failure mode available to any deployed optimisation whose objective omits a constraint the environment
enforces anyway.

## 6.2 The arm that wins, wins on what it pays to trade

An arm's advantage over its rivals is bought at the trading desk and not at the drawing board, and
one ablation shows it. Removing the transaction cost needs no retraining, because the environment
charges cost after the action and the gross series is already archived, so the same eleven lines can
be read twice. Before costs the five reward designs are almost indistinguishable: the between-arm
spread in terminal GROSS Sharpe has an interquartile mean of 0.067, close to the 0.05 margin
registered as the smallest difference worth caring about. NET of costs it is 0.302, and the net
spread is wider on 11 of 11 lines. Figure 6.1 draws both, and Figure 6.2 the registered cost grid.

The cost channel also accounts for the placebo result, otherwise the most awkward number in the study.
An inert block of constants is the best arm on five of the eleven lines, and it is also the arm that
trades least: its turnover is 0.242 of the treatment's at the median line, and lower on 8 of 11. A
reward that provokes less trading keeps more of a gross return that barely differs. Three lines run
against that reading and are named rather than set aside. On `qwen3.6-27b`, `haiku-4.5` and
`kimi-k3` the placebo arm trades slightly *more* than the treatment, at 1.12, 1.16 and 1.24 times,
and still wins. All three sit near one per cent of the book traded per session, where the cost
channel is almost shut, so something else decides them.

**One link in that chain stays open, and it is the interesting one.** Why an information-free block
should yield lower-turnover programs at all is not established here, and the program forensics do not
support a clean "less information yields simpler code" story. The honest statement is that placebo
leads to less trading, that less trading wins, and that the first link is unexplained.

![**Figure 6.1** — The same arms, priced twice: gross of transaction costs and net of them. One row per authoring line, ordered by how much the costs took from it. Each row carries two bars on one shared horizontal scale: the upper, thin bar is the spread across the five arms before costs, the lower, thick bar the same spread after them, with each arm's marker on both. **What to conclude:** the reward designs agree about what to hold and disagree about how often to move, and only the second survives into the outcome. The between-arm spread is 0.067 gross against 0.302 net, and the net bar is the longer one on every one of the eleven lines. Where the upper bar is a stub and the lower one crosses half the panel, the whole difference between those designs was paid at the trading desk.
](../outputs/figures/F5_gross_vs_net.png)

![**Figure 6.2 — The same result as a response surface: what a cell earns at every price of trading.** The surface is the mechanism written down rather than a smoother. Charging cost after the action makes the Sharpe at any price exactly the gross Sharpe less the drag, and both are functions of one number, so the surface is generated by fitting those two functions of turnover: the drag at $R^2 = 0.99$, the gross at $R^2 = 0.38$ and over a range of only 0.33. The 55 measured cells are drawn on it at the two prices the archive holds, 0 and 10 bps, so the residuals are visible rather than asserted. The two-point repricing reproduces an independent series-by-series sweep to 0.0018 Sharpe across the whole grid, and the module refuses to draw at all beyond 0.01. **What to conclude:** the surface is nearly flat where turnover is low and falls away where it is high, so a design's fate at any price is set almost entirely by one number, and the arms are ordered by that number rather than by what their designer was shown.
](../outputs/figures/F5_cost_surface.png)

`scalar_cvar5` is the exception that sharpens the rule. It takes four of the eleven lines, and on
three of those four it is also the best arm *before* costs. A single conditional value-at-risk
number added to the score is the only feedback change in this study that shows up in gross terms. It
carries no registered test, so it is offered as the most promising thread for the next study rather
than as a finding.

**The same channel decides the human-written objectives, which is what makes this a property of reward
design rather than of language models.** Of the eleven published rewards in the canon of Table 4.5,
exactly one is net-positive over the sealed window: `return_minus_turnover`, at a mean net Sharpe of
$+1.1957$ against a range of $-0.1263$ to $-0.3186$ for the other ten. It is also the only one that
prices trading in its own objective, and the turnover column says so plainly. The survivor moves 0.86 per
cent of the book per session and the ten losers move between 77 and 91 per cent, a factor of about a
hundred.[^canonn] Eight of those ten penalise risk explicitly, several of them by exactly the coherent
tail measure this study feeds. Figure 6.3 puts all twenty on one axis and Figure 6.4 draws the paths.
Sophistication about risk did not substitute for pricing trading, for a
model or for a person.

[^canonn]: Means over the sealed baseline records, 305 or 306 per reward name, read from `outputs/campaign_cluster_run4`. The net-positive count of one, and the survivor's rank, are invariant across the mean, the median and the interquartile mean the confirmatory family uses. The ordering *within* the ten losers is not: two adjacent pairs exchange places between estimators, over a range of 0.20 net Sharpe, which is why nothing here rests on their order.


![**Figure 6.3 — The whole ladder on one axis: eleven hand-written objectives, four numerical optimisers and the five authored arms.** Points are the interquartile mean of the terminal net Sharpe over every sealed record of that arm, 305 to 308 per row, with 95 per cent bootstrap intervals. The shaded band is loss. **What to conclude:** the ordering is not by sophistication and it is not by who wrote the objective. Ten of the eleven published rewards sit inside the loss band, eight of them penalising risk explicitly, and the one that clears it is the one that charges for trading. Every automated arm clears it too, and they cluster: the treatment, its three comparators and Bayesian optimisation all land within 0.10 Sharpe of one another, which is the separation the registered test was built to resolve.
](../outputs/figures/F5_benchmark_ladder.png)

![**Figure 6.4 — The path, not the endpoint: what one pound did over the sealed window, and the worst it felt on the way.** Upper panel, compounded wealth from 1.00 invested at the window's open, net of costs, on a log scale; the faint lines are the eleven authoring lines and the heavy line each arm's median across them. Lower panel, the fall from the running peak of the same paths. **What to conclude:** the five conditions are not separated by where they end but by how much they gave back to reach it. The drawdown panel is nearly one curve, because it is dominated by an event common to all of them, the 2022 rate shock, which reaches roughly a fifth of capital; on that dimension the choice of reward design barely registers. The exception is worth naming rather than smoothing: the worst single line under the tail-fed condition falls 48.2 per cent from its peak, against 21.5 per cent for the deepest fall under `scalar_cvar5`. A terminal Sharpe near 1.0 is compatible with both.
](../outputs/figures/F5_wealth_drawdown.png)

## 6.3 Why the richer signal cost something, rather than merely failing to help

A null needs no account beyond an inert channel. This is not a null. The tail-fed condition sits
*behind* all three registered comparators, by 0.061 to 0.196 in net Sharpe, and the envelope of §1.3
says a richer signal cannot leave an optimal user worse off. A reader who took that envelope
seriously arrives here holding an objection. Four accounts are available and Table 6.2 sets them
against the evidence: two are supported, one is untested and one is not a rival at all.

The one that is not a rival is the reconciliation. Blackwell's ordering bounds what a decision-maker
who uses the evidence *optimally* could extract, and a language model asked to write a hundred lines
of Python from six numbers is not that decision-maker. The negative sign contradicts no theorem. What
it measures is how far a real designer sits below the envelope, a quantity the theorem cannot supply
and an experiment can.

Of the three rivals the strongest is that the vocabulary crosses and the values do not. Six numbers
change what a designer writes *about* without changing what it writes, measured at the level of the
code rather than of the outcome, under a control whose values have been destroyed. The second
explains the sign rather than the size: a risk vocabulary buys a more *active* program, the tail-fed
condition trades more than `scalar` on 7 of the 11 lines, and §6.2 has shown that trading more is
what loses. A designer told to attend to the downside writes something that responds to it, and
responding costs. The third, that the fed deltas sit below the designer's own numerical resolution,
is untested at this rendering, which is why it heads Table 7.1 rather than being asserted here.

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 6.2 — Four accounts of a negative sign, and what separates them.** The first is not a rival to the other three: it is the reason a negative sign is permitted at all, because the dominance envelope binds an optimal user and these designers are not one. Of the three that are rivals, two are measured here and agree, and the third is untested at the rendering precision this study happened to fix. No account is offered as settled, and the one with no evidence for it is named as such.
```{=latex}
\par\endgroup
```

| Account | Evidence for | Evidence against | What would settle it |
|---|---|---|---|
| **The envelope binds an optimal user, and this one is bounded** | the envelope is a bound, never a prediction | none: it is not a rival account | nothing; it is the reconciliation |
| **Format crosses, content does not** | 16 of 277 against 18 of 561 at parity; scrambled twin undiminished at 17 of 280 | the reach is not zero, so some transmission occurs | a guided-compare instruction in the prompt |
| **A risk vocabulary buys a more active program** | trades more than `scalar` on 7 of 11 lines, median ratio 1.60 | it trades *less* on the other 4 | a turnover-constrained agent |
| **The fed deltas sit below the designer's resolution** | none measured here | none measured here | a precision ladder on the rendering |

## 6.4 Five faults touched the confirmatory arm, and every one favours this study

Execution faults come before design limitations. Five faults in the executed run touched the
confirmatory arm, and Appendix B.8 carries each with its measured size.[^fivefaults] Three widened
the candidate pool in the treatment's favour, and by completion the pools stood at 28 / 27 / 25 / 26
/ 26. The fourth is undertraining, the critic loss still descending at the step cap in 76.0 per cent
of trainings. Only the fifth put records into the confirmatory data, four trainings of one canon
reward on the wrong processor, caught before scoring. The bound that follows is one-sided and was
knowable before the verdict: every asymmetry that is ours favours this study's own hypothesis, so a
measured effect must be discounted against it and a measured null strengthened by it.

[^fivefaults]: Their register entries carry the measured size of each: B.8.15 the extractor, B.8.10 the allowlist gap, B.8.9 the scheduling defect, B.8.12 the step cap, and B.8.1 the substrate inhomogeneity.

Table 6.3 foregrounds the five limitations most likely to bound the interpretation, and the full
register is Appendix B. Every one is a disclosed design decision, never a hidden assumption.


```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 6.3 — The five foregrounded limitations, and the claim each one blocks.** Every one is a disclosed design decision rather than a hidden assumption. Two of them cut deeper than the rest: the tail-blind selector is what makes a tail effect attributable to the channel and simultaneously places the study on the boundary of the null branch, and a single model family means the study cannot earn the plural *language models*. Search width is the mildest, because it is common-mode across arms and therefore conservative for the direction of any difference, and because the responsiveness it might otherwise bound is measured upstream of the search. Appendix B carries all thirty-one.
```{=latex}
\par\endgroup
```

| Limitation | What it is | The claim it blocks |
|---|---|---|
| **(i) Construct** | six left-tail scalars, not the whole return distribution | anything about upside or non-coherent features |
| **(ii) Training budget** | 400,000 steps, the measured knee | any reading at convergence |
| **(iii) Selection blindness** | the selector is tail-blind, $\lambda=0$ | any reading for a tail-rewarded selector |
| **(iv) External validity** | one universe, one window, one model family | the plural, *language models* |
| **(v) Search width** | $K=5$ over six generations, 30 per arm | that a wider search finds no stronger winner |

## 6.5 What would have to be false for the cost account to fail

The central claim of this chapter is that reward designs are separated by what they pay to trade
rather than by what their designer was shown. A claim that carries a chapter should be attacked
before a reader attacks it, so here are the four attacks worth making.

The first attack is worth answering in prose, because the answer is the difference between an
identity and a measurement. Cost is subtracted from return, so *of course* a policy that trades more
earns less net, and the correlation alone would establish nothing. The evidence is the ablation.
Removing the charge does not remove the relation, it shrinks it: the same regression on gross Sharpe
keeps a slope of $-0.363$ against $-1.583$ net, and across the 55 cells in levels the split reads
$r^2 = 0.44$ gross against $0.98$ net. The claim is not that turnover predicts the outcome. It is
that removing the charge removes most of what separates the arms. Table 6.4 takes the other three.

```{=latex}
\Needspace{14\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 6.4 — Three further attacks on the cost account, and what each one meets.** None of the three is answered by argument alone. The cost grid was registered before the window opened and is drawn in full at Figure 6.2, the linearity of the charge is disclosed in §4.3 and its error runs in the study's disfavour, and the outlier check was run for this section rather than carried over. The last row is the strongest of the three, because dropping the two lines a sceptic would name makes the relation *steeper* rather than weaker, and because the human canon of §6.2 reproduces it on data this study did not generate.
```{=latex}
\par\endgroup
```

| The attack | What it meets |
|---|---|
| **Ten basis points is an arbitrary price** | the registration priced the whole grid, 0 to 50 bps, and Figure 6.2 draws it: at zero the arms are not separable at all, and the reported ordering appears as the price rises |
| **The cost model is linear and real impact is not** | it is linear and §4.3 says so. A concave impact model charges a high-turnover policy *more*, so every arm the account condemns would be condemned harder. The error is known and conservative |
| **Two extreme lines drive it** | dropping `gemini-2.5-flash` and `qwen3.5-9b` leaves nine, and Spearman moves only from $-0.982$ to $-0.967$ while the slope *steepens* to $-1.912$ |


\newpage

# Chapter 7 — Conclusions and Recommendations

## 7.1 The eleven lines return a count rather than a winner, and the count is the finding

The question was whether showing a language-model reward-designer the lower tail of the realised outcome
distribution, instead of a single score, would change the reward code it writes, and whether that change
would propagate to the trained agent's realised tail behaviour. The eleven authoring lines return a count
rather than a winner, and the count is the answer. In none of
them does the tail-fed condition beat all three registered comparators at once on annualised net
Sharpe, where higher is better, and it is the best arm on no line: `placebo` takes five,
`scalar_cvar5` four, `scalar` one and the structure-destroyed twin one. Pooled by interquartile
mean, that condition sits 0.061 net Sharpe units behind `scalar` and
0.024 behind its own scrambled control, both governing intervals spanning zero, so any advantage of real
tail values over the same values scrambled is bounded above at $+0.097$ and never signed.[^ledger]

What separates the lines is not what they were shown but how heavily they trade. The change in daily
turnover between the tail-fed condition and `scalar` accounts for 97.2 per cent of the variation in their
net Sharpe contrast, and a second estimator over all 55 cells in levels puts it at 98.4 per
cent.[^turnover] Turnover itself runs from 0.603 to 88.83 per cent of the portfolio a day across those
cells, a factor of 147, where lower is better. Although the shared prompt tells every designer to think
about turnover, no arm's feedback block ever reported it (§4.4).

The same friction fixes the human bar, which §6.2 sets out: the eleven expert-written objectives cross
from positive gross to negative net, and the sole survivor is the only one whose formula charges for
turnover directly.[^canonx]

No single line's answer generalises, because the effect of the feedback depends on who is reading it.
Model identity, the arm, their interaction and residual seed noise take 27.9, 14.8, 34.8 and 22.5 per cent
of the variance in terminal net Sharpe, with overlapping intervals, so what is established is not their
ordering but that the model-by-arm interaction is substantial.[^shares] The same feedback does different
things to different authors. The capability gradient behind that is readable before any outcome is scored,
since the share of a line's 150 registered candidate slots lost runs from 0.0 to 86.0 per cent, and a
designer that fails most of its attempts leaves the reflection loop nothing to reflect on.

Eureka, Text2Reward and REvolve each show a language model discovering an objective that beats one
hand-written incumbent [`ma2024eureka`; `xie2024text2reward`; `hazra2025revolve`]. This study contests
eleven at once, under a frozen plan carrying a placebo and a scrambled control, and finds the binding
constraint in a friction ten of the eleven decline to price. The registered prediction remains a boundary
condition: under tail-blind selection and a designer that does not condition on the numbers, widening the
feedback changes little.

[^ledger]: Aggregation is the per-seed interquartile mean prescribed by the reinforcement-learning evaluation standard [`agarwal2021rliable`], with lines as tasks and seeds as runs, at 102 contiguous paired seeds in every one of the 55 cells.

[^canonx]: The depth at which each canon figure was measured is given in section 6.2.

[^turnover]: Three estimates, on three units.

[^shares]: The four shares carry 95 per cent intervals, resampling the eleven authors, of 27.9 [11.5, 35.1], 14.8 [7.8, 29.4], 34.8 [23.5, 38.2] and 22.5 [14.3, 43.8] per cent. They overlap, so only the interaction's exclusion of small values is established.


## 7.2 What to do next, ordered by how directly it attacks the located break

A null is only actionable if it comes with the interventions it implies. Table 7.1 orders them by how directly
they attack the link the mechanism analysis locates, and Table 7.2 reduces the same evidence to the decision a
practitioner faces.

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 7.1 — What to do next, ordered by how directly it attacks the located break.** The two interventions that attack the located link most directly are also the cheapest: a tail-rewarded selector needs one re-run of the search stage, and a responsiveness pre-screen needs no trained agents at all. The register entry in the second column is the evidence that motivates each row. The last row is Dr Okhrati's: showing several information streams at once might let a designer cover one signal's weakness with another's strength, and it is recorded here as future work because adding an arm is a data-collection decision and therefore outside the presentation-and-interpretation licence this study operates under.
```{=latex}
\par\endgroup
```

| Intervention | From | What it would settle | Cost |
|---|---|---|---|
| **Tail-rewarded selection**, $\lambda>0$ | §B.1.2 | the channel does not carry, against the selector discards it | one re-run of the search stage |
| **A responsiveness pre-screen**, before the loop is built | link 1 | whether the designer reads the signal at all | negligible, no trained agents |
| **Training to convergence** | §B.2.1 | mechanism-limited against budget-limited | about ten times the compute per candidate |
| **A precision ladder** on the fed rendering | §B.2.8 | cannot use the information, against cannot use it at this resolution | one re-run of authoring per rung |
| **A second model family and market** | §B.3.1, §B.4.1 | whether the boundary belongs to the channel or to this model | one leg per family, the suite exists |
| **A corner-reaching action space** | §B.4.4 | whether the limit is the reward or the reachable policies | an environment change, so a full re-run |
| **A reason-gated delisting re-pull** | §B.4.2 | whether the band's conservatism moves the tail estimand | a data re-pull under licence |
| **A combined-signal arm** | Table 4.2 | no single stream carries, against no stream carries alone | one arm and its own seed ladder |


<!-- THIS ROW AND ITS PARAGRAPH CLOSE A DUTY THAT WAS ABSENT FROM THE ARTEFACT (added 2026-08-11).
     Dr Okhrati raised the combined-arm hypothesis in the 2026-08-07 review, ruled it out of scope on
     time himself, and asked that the hypothesis, the rationale and the exclusion be recorded "so an
     examiner asking 'why not combine the signals' meets a documented answer rather than a gap".
     MEASURED before writing: zero hits for any combined-arm statement anywhere in the compiled PDF,
     including B.7 (future work from the disclosed limitations) and Table 7.1. The duty was open.
     It sits in Table 7.1 rather than in the limitations register because he framed it as a thing to
     DO next, and because a table row is word-excluded while the answer still reaches a reader who is
     looking for it. Adding an arm is a data-collection decision and therefore outside the
     presentation-and-interpretation licence, which is why this is future work and not a change. -->



```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 7.2 — A practitioner's checklist for language-model-in-the-loop feedback design.** Richer feedback is not self-acting, so the two checks worth running come *before* the loop is built rather than after its output is measured: does the selector reward the dimension being fed, and does the designer's authored code move when that dimension moves. A designer that fails the second cannot transmit content however rich the feedback, and a selector that fails the first discards the candidates that used it. The fourth row is the one most often treated as an implementation detail: this study measured its own channel only at the rendering resolution it happened to fix, and at the original precision 229 of 240 fitness values printed as `0.00`.
```{=latex}
\par\endgroup
```

| Question a practitioner faces | The short answer | Why |
|---|---|---|
| *Will richer feedback help my loop?* | **Not on its own** | the envelope binds an optimal user, not yours |
| *How do I check my model can use it?* | **Run a responsiveness audit first** | code that does not move with the signal transmits nothing |
| *Is my objective actually tail-aware?* | **Check the selector, not the prompt** | a tail-blind fitness discards tail-aware candidates |
| *How should I present numbers?* | **As a design parameter** | rendering precision is part of the manipulation |
| *What does a null buy me?* | **A costed basis for not building it** | a bounded equivalence is a decision, a bare non-rejection is not |
