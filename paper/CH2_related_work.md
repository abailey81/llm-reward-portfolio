# Chapter 2 — Literature Review

This chapter situates the dissertation at the intersection of three literatures and shows that, while each is
mature, their conjunction is empty. We organise the review around the manipulated variable — *the feedback shown
to an automated reward-designer* — because that is what the work varies and what every comparison must turn on.
§2.1 reviews language-model reward design and the broader automated-discovery agenda, and extracts a taxonomy of
the feedback such systems are shown. §2.2 places the nearest neighbours on that taxonomy and identifies the empty
cell. §2.3 distinguishes the contribution from risk-sensitive and distributional reinforcement learning, where
risk usually lives in the *critic* rather than the *feedback*. §2.4 reviews the statistics of backtest evaluation
and pre-registration, against which the study's inferential rigour is the principal differentiator. §2.5 states
the positioning.

## 2.1 Language-model reward design and automated discovery of objectives

Building on earlier roles in which the language model itself *was* the reward — emitting a scalar reward from a
natural-language task description [`kwon2023rewarddesignlm`], or proposing exploration goals that shape a
pretraining reward [`du2023ellm`] — the proposition that it can instead author a reward function as executable
code, train an agent on it, and
revise it from feedback was established by Eureka, which matched or beat human-engineered rewards on most of
twenty-nine control tasks through an evolutionary loop with "reward reflection" [`ma2024eureka`]. The line has
since broadened — to dense reward shaping from natural-language task descriptions [`xie2024text2reward`], to
sim-to-real transfer [`ma2024dreureka`], to trajectory-analysing critics [`li2024automc`], and to human-preference
evolution [`hazra2025revolve`] — and a 2024 taxonomy now treats "reward designer" as a standard role for a
language model in reinforcement learning [`cao2024survey`]. Read at a higher altitude, these systems instantiate a
faster agenda: the **automated discovery of objective functions and algorithms** by evolving code against an
evaluator, whose flagships are FunSearch's program-search discoveries in mathematics [`romera2024funsearch`],
AlphaEvolve's algorithmic improvements [`deepmind2025alphaevolve`], and the "AI Scientist" systems that draft
entire papers [`lu2024aiscientist`; `yamada2025aiscientist`]. The agenda's own survey is candid that its systems
are evaluated by demonstration, with "no pre-registered or controlled experimental protocols" in evidence
[`gridach2025agentic`] — they establish that discovery is *possible*, not that a design choice *causes* an
improvement. That methodological gap is the one this dissertation is built to fill.

The decisive question for our purposes is *what these systems feed back to the designer*, and a clear taxonomy
emerges. Eureka and its descendants feed **per-component scalar time-series plus aggregate task fitness** — its
reward reflection "tracks the scalar values of all reward components and the task fitness function at intermediate
policy checkpoints" [`ma2024eureka`, §3.3]; the same evolutionary-code-search frameworks feed
**scalar fitness** with, at most, textual or debug side-channels (FunSearch's best-shot programs, OpenEvolve's
string artifacts, ShinkaEvolve's metrics-plus-text) [`romera2024funsearch`; `deepmind2025alphaevolve`]. A second
family feeds **human or preference signals** — direct natural-language critique [`xie2024text2reward`] or Elo
preferences over watched behaviour [`hazra2025revolve`]. The dynamic-feedback framework CARD is the closest the
literature comes to a "distribution", but its distributional signal is a *binary order-preservation check* on
trajectory returns, not a multi-level tail [`sun2024card`]. Crucially, that feedback *content matters* is itself
established: Eureka's own ablation shows that removing structured reward reflection costs roughly a third of
performance, and an independent line on language-model optimisers shows scalar reward is a weak signal that richer,
*directional* feedback substantially improves [`agrawal2026gepa`; `nie2024importance`] — or can be dispensed with
altogether, verbal feedback serving directly as the conditioning signal [`luo2025fcp`]. What no surveyed system
feeds is the **realised-return lower-tail distribution** — the content a risk-sensitive designer most needs. The
present work occupies exactly that omission.

Nor do these systems' own ablations amount to a test of feedback content. Where prior work varies its reflection
signal at all, it does so to justify its own components: Eureka's ablation reduces the feedback prompt to snapshot
task-metric values, CARD removes each of its three feedback types in turn, and RDA progressively adds
vision-language trajectory analysis [`ma2024eureka`; `sun2024card`; `lee2026rda`] — engineering ablations on two or
three tasks, without controls or inferential statistics, in which feedback informativeness is never itself the
hypothesis. A concurrent workshop study is, to our knowledge, the first to make the axis explicit — naming it
"feedback engineering" and comparing sparse against dense feedback for language-model-synthesised *policy* code in
sequential social dilemmas, with matched iterations and prompts identical except for the feedback block
[`gallego2026beyondscalar`] — but its object is policy code rather than the reward of a fixed agent, its domain is
social dilemmas rather than finance, and it carries no placebo or structure controls, no inferential statistics,
and no tail axis. To our knowledge, no prior work treats the informational content of the reflection signal shown
to a reward-code-authoring language model as the manipulated variable of a pre-registered, placebo-controlled
experiment — holding the agent, environment, prompts and search budget fixed across arms — and none manipulates
distributional (tail-risk) versus scalar content or applies equivalence-capable inference to the contrast.
In the terms the axis has now acquired, this study is therefore, to our knowledge, the first pre-registered,
controlled, inferentially *decided* instance of feedback engineering for reward design.
The line's newest entry is candid, finally, that automated reward design is *high-variance* — the average
LLM-authored candidate fails outright, and only a multi-run search surfaces good ones [`cardenoso2025learnopt`]
— which independently licenses both the matched thirty-candidate budget and the per-seed, thirty-seed inference
of Chapter 4.

It is equally important to acknowledge the strongest *counter*-claim: that scalar reward suffices for in-context
self-improvement [`song2025reward`]. That result concerns short-horizon reasoning with accumulated multi-round
reward, not the authoring of reward *code* from a single fed distribution; and even there it argues only that
scalar reward is *enough to improve*, not that it is *as good as richer feedback* — the margin our hypothesis
tests, which Eureka's −28.6% ablation and the directional-feedback line both indicate is large. We cite and rebut
it explicitly because an informed reader will raise it.

## 2.2 The nearest neighbours and the empty cell

Locating the contribution requires triangulating the works that share *some* of its axes. The **structural twin**
is the Decision-Language Model, in which a language model proposes reward *code* and iterates on it using a
*distribution* surfaced from grounded simulation [`behari2024dlm`]; it is, however, set in public-health resource
allocation, carries no risk or tail sensitivity, does not hold a single agent fixed off-critic, and is not
pre-registered. The **nearest finance work**, FinRL-DeepSeek, is frequently conflated with our setting because it
combines a language model, trading, and the word "risk-sensitive" — but the language model there is a
*sentiment-and-risk-score encoder* whose outputs scale actions and penalise a *fixed, human-written* CVaR-PPO
[`schulman2017ppo`] objective; the model never authors the reward, and no return distribution is fed back to it
[`benhenda2025finrldeepseek`]. The **freshest finance neighbour**, GIFT, does move the language model into the
reward channel — but its reward authorship is *constrained*, not open-ended: beyond an intrinsic reward term, the
model may only select, transform and compose penalties from a *registered library of portfolio-risk rules*, its
parameters clipped to safe ranges before execution — a bounded interface, not free reward-code authorship.
It moreover redesigns the *state jointly with* the reward (where our identification varies the
reward alone against a fixed interface), its refinement loop feeds generic rollout diagnostics (information
coefficients, reward trend and variability, drawdown) rather than any multi-level realised-return tail vector,
and it is a framework demonstrated against baselines, not a controlled manipulation of feedback content
[`wu2026gift`]. The works **closest in mechanism** — Eureka itself, and CARD, which beats a human
reward oracle on a minority of robotics tasks — author reward code but feed scalar, process or
order-preservation signals in non-financial domains [`ma2024eureka`; `sun2024card`]. The one reward-*code*
evolver in a finance-*adjacent* domain — a self-evolving loop that rewrites the reward of an e-commerce
payment-fraud detector — refines it on scalar dollar-precision business metrics rather than any return
distribution, and is neither a portfolio agent nor pre-registered [`qu2025selfevolving`]. The freshest look-alikes,
evolving finance code in an Eureka-style loop, evolve *whole trading-strategy* code scored on summary statistics —
MadEvolve on impact-adjusted profit, and AlgoEvolve (June 2026) on a blend of total return and consistency, with
no reinforcement-learning agent and no reward function anywhere in its loop — not the reward of a fixed
reinforcement-learning agent, and neither is pre-registered [`kvasiuk2026madevolve`; `sharma2026algoevolve`].
The **closest portfolio system**, ELfolio, likewise evolves language-model-written strategy code — its "RL path"
template even lets the model rewrite state–action rules and reward functions — but selection is driven by a
*scalar Sharpe-ratio fitness function*, with tail measures appearing only in its evaluation tables and never in
the feedback to the model; it thereby instantiates precisely the scalar-feedback *control* condition of our
design, not its treatment [`zeng2025elfolio`].

What the wider field *feeds its designers* is, in one case, stated outright: RD-Agent(Q), the most explicit of the
quant research loops, hands its language model an eight-component feedback vector,
$x_t = [\mathrm{IC}, \mathrm{ICIR}, \mathrm{Rank(IC)}, \mathrm{Rank(ICIR)}, \mathrm{ARR}, \mathrm{IR},
-\mathrm{MDD}, \mathrm{SR}] \in \mathbb{R}^8$ — whose deepest risk statistic is a maximum drawdown; conditional
value-at-risk, expected shortfall and tail quantiles are absent [`li2025rdagentq`]. The alpha-expression evolution
loops that surround it feed the same information-coefficient/return/drawdown family [`han2026quantaalpha`;
`tang2025alphaagent`], and where a language model does meet a reinforcement-learning trader, it either *guides*
the agent's strategy rather than authoring its reward [`darmanin2025lmguided`], or acts as a judge whose scores
are converted into penalties added to a *fixed, human-written* soft actor–critic reward — a score-*emitter*
inside someone else's objective, not a reward-code author [`alridhawi2026llmjudge`].

These neighbours partition cleanly along the feedback axis: the finance systems either use the language model as
a *signal* over a *human-written* reward (FinRL-DeepSeek), confine it to a fixed risk-rule library refined on
generic scalar diagnostics while co-varying the state (GIFT), evolve strategy code under scalar
return-family fitness (ELfolio, MadEvolve, AlgoEvolve), or feed IC/return/drawdown vectors to a factor-and-model
designer (RD-Agent(Q), the alpha miners); the unconstrained reward-*code* authors operate in robotics with
scalar-flavoured feedback. No
single work occupies the conjunction at which this dissertation sits — *(LLM authors reward code) × (multi-level
realised-return tail fed as off-critic feedback) × (fixed risk-sensitive portfolio agent) × (pre-registered
comparative inference)* — and the fourth axis, pre-registration, appears absent from the entire LLM-reward-design
literature. The empty cell is therefore not a gap in coverage but a gap in *kind*: to our knowledge it is the only
design that isolates the feedback content (endogenous to the policy it steers) shown to a reward-code-authoring
designer as a single manipulated variable and submits the comparison to a frozen, placebo-controlled,
equivalence-capable test.

## 2.3 Risk-sensitive and distributional reinforcement learning: risk in the critic vs. risk in the feedback

A natural objection is that risk-sensitive reinforcement learning already exists, and that one should simply use a
distributional critic. The distributional line — categorical, quantile and implicit-quantile value learning
[`bellemare2017distributional`; `dabney2018qrdqn`; `dabney2018iqn`] — and its risk-sensitive descendants —
distributional soft actor–critic, worst-case SAC, and risk-sensitive *portfolio* policies derived from a learned
return distribution [`ma2020dsac`; `yang2021wcsac`; `theate2023risksensitive`] — obtain tail-aware *behaviour* by
shaping risk *inside the agent's critic*. A parallel family instead builds risk into the *objective* the agent
optimises — actor and policy-gradient methods that maximise a CVaR or worst-case criterion directly
[`tang2019worstcases`], robust risk-aware portfolio policies [`jaimungal2021robustriskaware`], and convex-risk
deep hedging that minimises a coherent risk of the terminal position [`buehler2019deephedging`]. Both routes put
risk *inside the agent*; our contribution is on a different and complementary axis. The risk
signal here is measured **off the critic**, from realised returns, by a separate estimator, and is fed to the
*reward-designer*; the agent's critic remains risk-neutral and, indeed, fixed across arms. This matters for three
reasons. It isolates the feedback content (endogenous to the policy it steers) as the manipulated variable, which a distributional-critic comparison
cannot. It avoids the critic-architecture confounds — including the divergence pathologies documented in Chapter
4 — that would otherwise be entangled with the feedback manipulation. And it is licensed by a small literature
showing that a *scalar reward signal* can carry CVaR/tail sensitivity without a distributional critic, via
a scalar risk-sensitive objective — e.g. a CVaR penalty optimised by a standard, non-distributional agent
[`prashanth2018risk`], so that "off-critic" is a recognised
category rather than an ad-hoc choice; and because a native CVaR optimiser is itself sample-inefficient and can
stall at a local optimum that is *blind to success* [`greenberg2022efficientriskaverse`], keeping the agent's
objective risk-neutral and routing the tail to the *designer* is a positive design choice, not merely an
available one. We therefore cite the distributional-critic canon as related-but-orthogonal
and lead the comparison on the feedback channel, not on risk-sensitivity per se.

The risk measure itself — CVaR at multiple levels — is grounded in the coherent-risk literature, whose axioms,
spectral representation and CVaR-spanning theorem we invoke in Chapter 3 [`artzner1999coherent`;
`acerbi2002spectral`; `kusuoka2001law`; `rockafellar2000cvar`]. Two facts from that literature motivate our
choices and are developed formally in Chapter 3. First, value-at-risk fails the *subadditivity* axiom of coherence
(it can penalise diversification), whereas CVaR is coherent [`artzner1999coherent`; `rockafellar2000cvar`], which
is why the fed vector is built from CVaR rather than VaR. Second, the choice of a *vector* of CVaR levels rather
than a single coherent number is forced, not stylistic — but for a precise reason worth stating here rather than
deferring entirely: CVaR (equivalently ES) is *not elicitable on its own* [`gneiting2011making`], and expectiles
are the only law-invariant coherent risk measures that are elicitable as scalars [`ziegel2016coherence`;
`bellini2015elicitable`]; the escape is *joint* elicitability, the pair (VaR, CVaR) being jointly elicitable of
higher order [`fissler2016higherorder`]. Elicitability here concerns the existence of a strictly consistent scoring
function — i.e. whether the statistic is the unique minimiser of some expected loss, and hence a well-posed
M-estimation / calibration-testable forecasting target — not learnability *per se*; the consequence for us is that
no single coherent tail number admits a clean strictly-consistent learning target, which is why the fed statistic
is a jointly elicitable *vector*.

## 2.4 The statistics of backtest evaluation, and pre-registration as the differentiator

Strategy backtests are notoriously prone to over-optimism: a sufficiently large search over configurations will
surface a spuriously profitable one even when none exists, and the field's own benchmark papers name overfitting,
survivorship bias and multiple testing as the dominant failure modes [`bailey2014pseudomath`;
`liu2022finrlmeta`]. The corrective machinery is well developed — the deflated Sharpe ratio and the probability of
backtest overfitting via combinatorially symmetric cross-validation [`bailey2014deflated`; `bailey2017pbo`], the
reality-check and superior-predictive-ability tests for data snooping [`white2000reality`; `hansen2005spa`], and
the multiple-testing hurdles imported into finance [`harvey2016cross`; `harvey2015backtesting`] — and the
reinforcement-learning community has, in parallel, established that single-seed point-estimate comparisons are
unreliable and must be replaced by interquartile-mean aggregation with stratified bootstrap intervals over many
seeds [`agarwal2021rliable`; `henderson2018matters`; `colas2018seeds`]. This dissertation adopts that machinery in
full (Chapter 4).

The strategy-evaluation literature attacks the disease *post hoc*; it does not prevent it *ex
ante*. Explicit **pre-registration** of a trading-strategy study — freezing the hypotheses, family, splits and
analysis plan before the sealed leg — is, to our knowledge, absent in this domain; the nearest precedents are
pre-analysis plans in empirical economics [`olken2015promises`] and the still-nascent pre-registration of machine
learning [`bertinetto2021preregml`]. Pre-registration is also the cleaner answer to the multiplicity that an
unbounded language-model reward search creates: a frozen analysis path defeats the "garden of forking paths"
[`gelman2014forking`], and — anticipating the objection that pre-registration alone is insufficient against
forking paths [`rubin2017forking`] — the design pairs it with explicit family-wise control, so that it satisfies
*both* of the remedies that critique identifies as effective. The frontier of selective inference offers still
stronger instruments — e-value-based false-discovery control under arbitrary dependence, derandomised knockoffs,
and inference-on-winners, the last of which formalises exactly the "select the best reward then report it" problem
and certifies sample-splitting as its remedy [`wang2022ebh`; `ren2024derandomized`; `andrews2024winners`] — which
we discuss as documented strengthenings of, not replacements for, the pre-registered choice. It is this
combination — backtest-overfitting discipline, reinforcement-learning evaluation rigour, and *ex ante*
pre-registration with family-wise control — that constitutes the study's principal methodological contribution,
and the axis on which it most clearly exceeds the automated-discovery work reviewed in §2.1.

## 2.5 Positioning

The three literatures are individually mature and jointly silent on the present question. Language-model reward
design has shown that objectives can be discovered but evaluates by demonstration and feeds scalar-flavoured
signals; risk-sensitive reinforcement learning obtains tail-aware behaviour but locates risk in the critic, not in
the feedback to a designer; and backtest statistics correct over-optimism after the fact but do not pre-commit.
This dissertation joins them: it feeds an automated reward-*code* designer the realised-return lower tail,
off-critic, while holding the agent fixed, and submits the resulting comparison to a frozen, family-wise-controlled,
pre-registered test. The contribution is the instrument and the protocol — and, through them, a controlled answer
to a question the discovery agenda has been unable to ask: *does the information content of the feedback to an
automated objective-designer change the objectives it discovers, and the behaviour they induce?*
