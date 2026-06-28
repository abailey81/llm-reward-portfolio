# Chapter 2 — Related Work

> **Status: DRAFT v1 (2026-06-26), publication-standard.** A *critical synthesis* — every paragraph states what
> prior work does, what it omits, and why this design answers the omission — rather than a catalogue. Citation
> keys are in the verified backbone (`01_LITERATURE_DOSSIER.md`); apply the `% VERIFY` discipline to 2025–2026
> preprints before final submission.

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

The proposition that a language model can author a reward function as executable code, train an agent on it, and
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
[`zheng2025survey`] — they establish that discovery is *possible*, not that a design choice *causes* an
improvement. That methodological gap is the one this dissertation is built to fill.

The decisive question for our purposes is *what these systems feed back to the designer*, and a clear taxonomy
emerges. Eureka and its descendants feed **per-component scalar time-series plus aggregate task fitness** — its
reward reflection "tracks the scalar values of all reward components and the task fitness function at intermediate
policy checkpoints" [`ma2024eureka`, §3.3, verified verbatim]; the same evolutionary-code-search frameworks feed
**scalar fitness** with, at most, textual or debug side-channels (FunSearch's best-shot programs, OpenEvolve's
string artifacts, ShinkaEvolve's metrics-plus-text) [`romera2024funsearch`; `deepmind2025alphaevolve`]. A second
family feeds **human or preference signals** — direct natural-language critique [`xie2024text2reward`] or Elo
preferences over watched behaviour [`hazra2025revolve`]. The dynamic-feedback framework CARD is the closest the
literature comes to a "distribution", but its distributional signal is a *binary order-preservation check* on
trajectory returns, not a multi-level tail [`sun2024card`]. Crucially, that feedback *content matters* is itself
established: Eureka's own ablation shows that removing structured reward reflection costs roughly a third of
performance, and an independent line on language-model optimisers shows scalar reward is a weak signal that richer,
*directional* feedback substantially improves [`nie2024directional`; `agrawal2026gepa`]. What no surveyed system
feeds is the **realised-return lower-tail distribution** — the content a risk-sensitive designer most needs. The
present work occupies exactly that omission.

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
objective; the model never authors the reward, and no return distribution is fed back to it
[`benhenda2025finrldeepseek`]. The works **closest in mechanism** — Eureka itself, and CARD, which beats a human
reward oracle on a minority of robotics tasks — author reward code but feed scalar, process or
order-preservation signals in non-financial domains [`ma2024eureka`; `sun2024card`]. The freshest look-alike,
evolving finance code in an Eureka-style loop, evolves *whole trading-strategy* code scored on summary statistics,
not the reward of a fixed reinforcement-learning agent, and is again not pre-registered [`kvasiuk2026madevolve`].

These neighbours partition cleanly: every finance system uses the language model as a *signal* over a
*human-written* reward, and every reward-*code* author operates in robotics with scalar-flavoured feedback. No
single work occupies the conjunction at which this dissertation sits — *(LLM authors reward code) × (multi-level
realised-return tail fed as off-critic feedback) × (fixed risk-sensitive portfolio agent) × (pre-registered
comparative inference)* — and the fourth axis, pre-registration, appears absent from the entire LLM-reward-design
literature. The empty cell is therefore not a gap in coverage but a gap in *kind*: it is the only design that
isolates the feedback channel as a single manipulated variable and submits the comparison to a frozen,
controlled test.

## 2.3 Risk-sensitive and distributional reinforcement learning: risk in the critic vs. risk in the feedback

A natural objection is that risk-sensitive reinforcement learning already exists, and that one should simply use a
distributional critic. The distributional line — categorical, quantile and implicit-quantile value learning
[`bellemare2017distributional`; `dabney2018qrdqn`; `dabney2018iqn`] — and its risk-sensitive descendants —
distributional soft actor–critic, worst-case SAC, and risk-sensitive *portfolio* policies derived from a learned
return distribution [`ma2020dsac`; `yang2021wcsac`; `theate2023risksensitive`] — obtain tail-aware *behaviour* by
shaping risk *inside the agent's critic*. Our contribution is on a different and complementary axis. The risk
signal here is measured **off the critic**, from realised returns, by a separate estimator, and is fed to the
*reward-designer*; the agent's critic remains risk-neutral and, indeed, fixed across arms. This matters for three
reasons. It isolates the feedback channel as the manipulated variable, which a distributional-critic comparison
cannot. It avoids the critic-architecture confounds — including the divergence pathologies documented in Chapter
4 — that would otherwise be entangled with the feedback manipulation. And it is licensed by a small literature
showing that a *scalar reward signal* can carry CVaR/tail sensitivity without a distributional critic, via
risk-sensitive reward shaping [`distributionalrewardshaping2022` `% VERIFY`], so that "off-critic" is a recognised
category rather than an ad-hoc choice. We therefore cite the distributional-critic canon as related-but-orthogonal
and lead the comparison on the feedback channel, not on risk-sensitivity per se.

The risk measure itself — CVaR at multiple levels — is grounded in the coherent-risk literature, whose axioms,
spectral representation and CVaR-spanning theorem we invoke in Chapter 3 [`artzner1999coherent`;
`acerbi2002spectral`; `kusuoka2001law`; `rockafellar2000cvar`]. We defer the theoretical treatment, noting
here only that the choice of a *vector* of CVaR levels rather than a single coherent number is forced, not
stylistic: expectiles are the unique elicitable coherent scalar, so no single coherent tail number is a clean
learning target [`ziegel2016coherence`; `fissler2016higherorder`].

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

---

### Citation keys introduced in this chapter (add to `refs.bib` from the verified backbone)
`ma2024eureka`, `xie2024text2reward`, `ma2024dreureka`, `li2024automc`, `hazra2025revolve`, `cao2024survey`,
`romera2024funsearch`, `deepmind2025alphaevolve`, `lu2024aiscientist`, `yamada2025aiscientist`, `zheng2025survey`,
`nie2024directional`, `agrawal2026gepa`, `song2025reward`, `behari2024dlm`, `benhenda2025finrldeepseek`,
`sun2024card`, `kvasiuk2026madevolve`, `bellemare2017distributional`, `dabney2018qrdqn`, `dabney2018iqn`,
`ma2020dsac`, `yang2021wcsac`, `theate2023risksensitive`, `distributionalrewardshaping2022` (`% VERIFY`),
`artzner1999coherent`, `acerbi2002spectral`, `kusuoka2001law`, `rockafellar2000cvar`, `ziegel2016coherence`,
`fissler2016higherorder`, `bailey2014pseudomath`, `liu2022finrlmeta`, `bailey2014deflated`, `bailey2017pbo`,
`white2000reality`, `hansen2005spa`, `harvey2016cross`, `harvey2015backtesting`, `agarwal2021rliable`,
`henderson2018matters`, `colas2018seeds`, `olken2015promises`, `bertinetto2021preregml`, `gelman2014forking`,
`rubin2017forking`, `wang2022ebh`, `ren2024derandomized`, `andrews2024winners`.
