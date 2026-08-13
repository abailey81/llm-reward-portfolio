# Chapter 2 — Literature Review

Three literatures meet in this dissertation, and the claim is not that each is incomplete but that a single
question falls between them. The review is therefore organised around the manipulated variable, *the
feedback shown to an automated reward-designer*.

## 2.1 The objective is the bottleneck

Reinforcement learning is presented as an algorithms problem, but its characteristic failures are
objective failures. The specification-gaming catalogue collects dozens of cases where a *correct*
optimiser faithfully satisfied an *incorrect* objective [`krakovna2020specification`], and two of the
safety agenda's five canonical accident risks are a wrong objective rather than a failure of learning
[`amodei2016concrete`; `strathern1997improving`; `manheim2018categorizing`]. The difficulty is formal
as well as practical. There is an *optimal reward problem* [`sorg2010orp`], Markov reward provably
cannot express whole classes of task [`abel2021expressivity`], and the gap between the objective
written and the objective intended sustains an inverse-reward-design literature
[`hadfieldmenell2017ird`].

Finance sharpens the problem. Once the agent is fixed, the objective is the only
place a risk preference *can* enter, and the domain's own methodology literature is candid that a backtest
cannot adjudicate between an objective that captured something real and one fitted to the sample
[`bailey2014pseudomath`]. If the objective is the binding constraint, whoever writes it is the true
designer. Since 2023 that designer is increasingly not a person.

## 2.2 The bottleneck moves: from designing rewards to designing the designer's evidence

Earlier roles made the language model itself the reward [`kwon2023rewarddesignlm`; `du2023ellm`].
Eureka established the stronger proposition that it can instead author the reward as executable code,
train an agent on it and revise it from feedback, matching or beating human-engineered rewards on
most of twenty-nine control tasks [`ma2024eureka`]. The line has since broadened enough[^broadened]
that a 2024 taxonomy treats "reward designer" as a standard role [`cao2024survey`]. These systems
instantiate a faster agenda, the automated discovery of objective functions and
algorithms[^discovery2] by evolving code against an evaluator.

[^broadened]: To dense reward shaping from task descriptions [`xie2024text2reward`], sim-to-real transfer [`ma2024dreureka`], trajectory-analysing critics [`li2024automc`], and human-preference evolution [`hazra2025revolve`].

[^discovery2]: The flagships are FunSearch [`romera2024funsearch`], AlphaEvolve [`deepmind2025alphaevolve`], and the AI Scientist systems that draft entire papers [`lu2024aiscientist`; `yamada2025aiscientist`].

This capability does not dissolve the design problem. **It relocates it.** The lever moves from writing the
objective to designing the designer's evidence, the last human-controlled input to an otherwise
automated loop. That relocation is our premise, and it carries a claim about the field.
Innovation has been vigorous on every element of that loop except the evidence flowing through it.

Table 2.1 records what these systems actually feed back, work by work, and the pattern is scalar.
Eureka and its descendants feed per-component scalar time-series with aggregate task fitness
[`ma2024eureka`, §3.3], and the rest of the lineage feeds scalar fitness with at most textual
side-channels or human preference signals [`romera2024funsearch`; `deepmind2025alphaevolve`;
`xie2024text2reward`; `hazra2025revolve`]. The closest thing to a *distribution* anywhere in it is
DLM's demographic state-feature profile or CARD's binary order-preservation check, and neither is a
tail of the agent's own returns [`behari2024dlm`; `sun2024card`]. Innovation elsewhere in the loop
has been continuous, on search method, modality, autonomy and the object designed [`rfagent2026`;
`yang2025urdp`; `liu2024eoh`; `yang2024opro`; `lares2025adaptive`; `lee2026rda`;
`cardenoso2025learnopt`; `su2026endrewardengineering`; `yuksel2025alphasharpe`; `dorka2024quantile`],
and Table E.8 sets those four axes against the fifth, which is empty. That the channel's *content*
matters is not in doubt, since Eureka's own ablation shows removing structured reward reflection
costs 28.6% of the average normalised score [`agrawal2026gepa`; `nie2024importance`; `luo2025fcp`].
What no surveyed system feeds is the realised-return lower tail.

Nor do these systems' own ablations test feedback content. Where prior work varies its reflection
signal it does so to justify its own components [`ma2024eureka`; `sun2024card`; `lee2026rda`], and
across the wider discovery agenda evaluation is by demonstration [`gridach2025agentic`], which
establishes that discovery is possible rather than that a design choice causes an improvement. The
one concurrent study to make the axis explicit compares sparse against dense feedback for
model-synthesised *policy* code in social dilemmas, with no placebo or structure control and no tail
axis [`gallego2026beyondscalar`]. To our knowledge no prior work treats the content of the reflection
signal shown to a reward-code-authoring model as the manipulated variable of a pre-registered,
placebo-controlled experiment[^variance] holding agent, environment, prompts and budget fixed.

[^variance]: Automated reward design is high-variance, the average candidate failing outright, so only a multi-run search surfaces good ones [`cardenoso2025learnopt`]. That licenses the matched thirty-candidate budget used here.

<!-- THIS PARAGRAPH WAS DELETED ON 2026-08-11 AS A DUPLICATE, AND THE DUPLICATION WAS THE POINT.
     It walked DLM, GIFT and ELfolio one at a time and said each fails the conjunction on a structural
     axis. §2.4 below now opens by walking the SAME three systems, and the Table 2.1 bullets walk them
     a third time. Three passes over three works is the repetitiveness this pass exists to remove.
     NOTHING IS LOST: every citation key (`behari2024dlm`, `wu2026gift`, `zeng2025elfolio`), both
     footnote anchors, and the ELfolio gross-or-net disclosure are carried into §2.4, which is the one
     place that now makes this argument. -->


[^fence26]: Each 2025–26 arrival is displaced on a structural axis. Systems that evolve finance code evolve whole trading strategies with no reward function in the loop [`kvasiuk2026madevolve`; `sharma2026algoevolve`] or mine alpha expressions [`han2026quantaalpha`; `tang2025alphaagent`]. Where a reward is evolved in a finance-adjacent domain it is refined on scalar business metrics [`qu2025selfevolving`]. Where a language model meets a trading agent it guides strategy [`darmanin2025lmguided`] or scores penalties inside a fixed objective [`alridhawi2026llmjudge`].

[^nbrs]: Every weight-bearing cell of Table 2.1 is sourced from the work itself: 36 verbatim quotations with page and section, 3 page locators, and 15 counted full-text searches, over 54 cells with none unsourced.

The strongest *counter*-claim deserves naming, because an informed reader will raise it. Scalar reward
suffices for in-context self-improvement [`song2025reward`]. That result concerns short-horizon reasoning
with accumulated multi-round reward, not the authoring of reward *code* from a single fed distribution. Even
there it argues only that scalar reward is *enough to improve*, not that it is *as good as* richer feedback,
which is precisely the margin our hypothesis tests.

## 2.3 Why finance: the arena where the evidence itself can be judged

Judging a channel requires a standard for what good evidence about risk is, and here the arena stops
being incidental. Robotics can report whether a reward worked. It cannot say what a designer ought to
have been shown, having no theory of which summaries of a return distribution are admissible. Finance
has one, it is normative, and it is sharp enough to be wrong. Coherent-risk theory fixes the axioms a
risk summary must satisfy [`artzner1999coherent`; `acerbi2002spectral`], and Kusuoka's theorem shows
the law-invariant coherent measures are spanned by conditional value-at-risk at its several levels
[`kusuoka2001law`; `rockafellar2000cvar`], so the answer is a profile rather than a number.
Value-at-risk fails subadditivity and can penalise diversification, while CVaR is coherent, which is
why the fed vector is built from CVaR at several levels and carries no quantiles.[^elicit]

[^elicit]: Two arguments decide the vector's shape and merging them would be an error. How many levels to show is the Kusuoka question settled above. Whether any single level is a well-posed *target* is the separate elicitability question, elicitability meaning the statistic is the unique minimiser of some expected loss and hence a calibration-testable target. CVaR is not elicitable alone [`gneiting2011making`], and expectiles are the only law-invariant coherent measures elicitable as scalars [`ziegel2016coherence`; `bellini2015elicitable`], so the remedy pairs a level with its own quantile [`fissler2016higherorder`] and adds no levels.

A natural objection is that risk-sensitive reinforcement learning already exists, and that one should
simply use a distributional critic. That literature obtains tail-aware behaviour by putting risk
inside the agent.[^inside] This contribution sits on a complementary axis. The risk signal is
measured off the critic and fed to the *reward-designer*, while the agent's critic stays
risk-neutral and fixed across arms. That isolates the feedback content as the manipulated variable,
which a distributional-critic comparison cannot. It is also licensed. A scalar reward can carry CVaR
sensitivity without a distributional critic [`prashanth2018risk`], and a native CVaR optimiser is
sample-inefficient and can stall at a local optimum *blind to success*
[`greenberg2022efficientriskaverse`].

[^inside]: Three families sit inside the agent. The distributional line [`bellemare2017distributional`; `dabney2018qrdqn`; `dabney2018iqn`] and its risk-sensitive descendants [`ma2020dsac`; `yang2021wcsac`; `theate2023risksensitive`]. The application of reinforcement learning to trading [`deng2017ddr`; `almahdi2017adaptive`; `meng2019rlfinance`]. And the family that builds risk into the objective [`tang2019worstcases`; `jaimungal2021robustriskaware`; `buehler2019deephedging`].

Finance is also the site of an argument this study joins. The canonical comparison
of fourteen optimising rules against equal weighting found none of them consistently better out of sample,
and blamed estimation error [`demiguel2009naive`]. Objectives written by a machine are a new class of rule
for that argument. They lose to equal weighting here as the estimated rules did, and for a reason that is
not estimation error.[^naive]

[^naive]: DeMiguel, Garlappi and Uppal find that a sample-based mean-variance rule on 25 assets needs an estimation window beyond 3,000 months to beat the naive benchmark, against the 120 months practitioners use [`demiguel2009naive`].

The arena supplies one more thing no other does, the strictest available standards for *believing*
the answer. The field names overfitting, survivorship bias and multiple testing as the dominant
failure modes of a backtest [`bailey2014pseudomath`; `liu2022finrlmeta`], the corrective machinery is
well developed,[^machinery] and this study adopts it in full (Table E.5). All of it attacks the
disease *post hoc*. Explicit pre-registration of a trading-strategy study is to our knowledge absent
here, and it is the cleaner answer to the multiplicity an unbounded reward search creates
[`gelman2014forking`].[^preregprec] Because it is insufficient alone [`rubin2017forking`], the design
pairs it with explicit family-wise control, meeting *both* remedies that critique
identifies.[^frontier]

[^preregprec]: Freezing hypotheses, family, splits and the analysis plan before the sealed leg. The nearest precedents are pre-analysis plans in empirical economics [`olken2015promises`] and the still-nascent pre-registration of machine learning [`bertinetto2021preregml`].

[^machinery]: On the backtest side, the Deflated Sharpe ratio, the probability of backtest overfitting, the reality check and the multiple-testing corrections [`bailey2014deflated`; `bailey2017pbo`; `white2000reality`; `hansen2005spa`; `harvey2016cross`; `harvey2015backtesting`]. On the reinforcement-learning side, interquartile-mean aggregation with stratified bootstrap intervals [`agarwal2021rliable`; `henderson2018matters`; `colas2018seeds`].

[^frontier]: Each frontier instrument is displaced by a feature of the design. Inference on winners stays valid for a parameter selected by optimisation [`andrews2024winners`], but the winner's curse is removed here by construction, because candidates are selected on validation and tested on a sealed split. The e-BH procedure controls the false discovery rate under arbitrary dependence [`wang2022ebh`], which this plan has no use for, because its primary tests are intersection–union conjunctions. Derandomised knockoffs [`ren2024derandomized`] require a model of the covariate distribution that a free-form reward search does not possess.

## 2.4 The reward function for a portfolio agent has not been written by a model before

The three literatures are individually mature and jointly silent, and the silence has a shape. The
five systems of Table 2.1 that author reward code all sit outside finance and none carries a
risk-sensitive objective. The four finance systems are the mirror image, each putting a model inside
a trading loop and each stopping short of the reward itself. Two rows carry an argument rather than a
fact. GIFT moves the model into the reward channel but confines it to a fixed library of risk rules
and redesigns the state jointly with the reward, so it cannot identify what varying the reward alone
identifies [`wu2026gift`]. ELfolio, the closest portfolio system, evolves model-written strategy code
under a scalar Sharpe fitness whose gross-or-net status its source never states, and its tail
measures appear in its evaluation tables rather than in the feedback to the model, so it instantiates
this design's control condition rather than its treatment [`zeng2025elfolio`].[^nbrs]<sup>,</sup>[^fence26]

The claim this chapter licenses is therefore about the field rather than about a seven-column cell.
No prior study found here has a language model write the reward function for a risk-sensitive
portfolio agent, and the domain's own survey draws the same boundary from the other side
[`batra2025review`]. The design delivers something narrower: *(a language model authors reward code) ×
(a multi-level realised-return tail fed as off-critic feedback) × (a fixed risk-sensitive portfolio
agent) × (pre-registered comparative inference)*. We source every weight-bearing cell of Table 2.1
inside this document, so a reader disputing either claim has a cell to dispute.

Two neighbours narrow it further. A pre-registered study of frontier-model agent economies exists
[`qian2026infolimits`], so pre-registration is absent from automated reward design rather than from
language-model research at large. A placebo-controlled study of risk-feedback alignment in trading
agents [`xue2026riskfeedback`] is the nearest control design, and it differs on the axis that
matters. There the model *is* the agent. No copy of either is retained, so both distinctions rest on
the reading record.
