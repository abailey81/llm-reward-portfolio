# Chapter 1 — Introduction

This dissertation asks a mechanism question at the intersection of language models and risk-sensitive control:
**when a language model writes the reward *code* for a trading agent, does showing it the *tail* of the realised
outcome distribution — rather than a single score — change the code it writes, and does any change reach the
agent's realised risk?** We answer on a fixed deep-reinforcement-learning portfolio agent over two decades of
survivorship-free equity data, under a pre-registered, sealed-test design built so that either answer — an
improvement or its calibrated absence — is evidence. The theory of Chapter 3 establishes that an optimal designer
*could* exploit the tail; the experiment measures whether a bounded, real one *does*, and, when it does not,
locates where along the chain from fed signal to authored code to realised behaviour the information is lost.

## 1.1 Reward design is the bottleneck in risk-sensitive financial reinforcement learning

Reinforcement learning offers an appealing template for sequential financial decision-making: an agent observes a
market state, allocates capital, and is reinforced by the consequences of its actions. Yet the template's promise
is gated by a single brittle component — the **reward function**. The reward encodes what the agent is told to
want, and a reward that is well specified in the mean can induce a policy that is profitable on average and
ruinous in the tail. This is not a peripheral concern in finance, where the object of practical interest is rarely
expected return alone but its trade-off against the severity of the worst outcomes. A growing safety literature
documents that the gap between *what we reward* and *what we want* is where learning systems fail: rewards are
routinely "gamed" or "hacked", with more capable agents exploiting misspecification more aggressively and, in some
settings, undergoing phase transitions in which true performance collapses as proxy performance climbs
[`amodei2016concrete`; `krakovna2020specification`; `skalse2022reward`; `pan2022effects`]. Reward design — the
choice and shaping of that signal — is therefore the discipline's central bottleneck, and in a risk-sensitive
setting it is also its central hazard.

Designing a good risk-sensitive reward is hard precisely because the relevant information lives in the *shape* of
the outcome distribution. A practitioner hand-crafting a trading reward weighs realised return against downside
measures — drawdown, semi-deviation, conditional value-at-risk (CVaR), turnover cost — and tunes the weights by
judgement and trial [`moody1998performance`; `sood2023deep`; `orra2025volatility`]. In practice, most
reinforcement-learning trading agents are nonetheless trained on a *scalar* reward — cumulative return, a Sharpe or
Sortino ratio, or profit-and-loss — with the field's own surveys flagging the incorporation of explicit risk
measures as open future work [`hambly2021rlfinancesurvey`]. The process is laborious,
idiosyncratic, and difficult to audit, and it embeds the designer's preferences and the agent's learning dynamics
into a single opaque object. The question this dissertation asks is whether that process can be *automated* and, in
automating it, made *legible* — and, more sharply, whether the **information** supplied to the automating system
governs the quality of the rewards it produces.

## 1.2 Language models can author reward code — but on what feedback?

Large language models have made automating reward design newly plausible. The Eureka line of work shows that a
language model can write reward-function *code*, evaluate it by training an agent, and iteratively improve it from
feedback, matching or exceeding human-engineered rewards across dozens of control tasks
[`ma2024eureka`; `xie2024text2reward`; `ma2024dreureka`]. Viewed more broadly, this is one instance of a fast-moving
agenda in which language models conduct **automated discovery of objective functions and algorithms** — evolving
code against an evaluator in a closed loop — exemplified by FunSearch's mathematical discoveries, AlphaEvolve's
algorithmic improvements, and Sakana's "AI Scientist" [`romera2024funsearch`; `deepmind2025alphaevolve`;
`lu2024aiscientist`]. A recent survey of this line is explicit that its systems are, almost without exception,
evaluated by *demonstration* rather than by controlled, pre-registered inference [`gridach2025agentic`]: they show
that discovery is *possible*, not that a particular design choice *causes* an improvement.

Within that loop, a question has been largely overlooked: *what feedback should the reward-designer be shown?* The
canonical answer is a scalar — a fitness score — or, at most, per-component scalar time-series. Eureka's own
"reward reflection" feeds back "the scalar values of all reward components and the task fitness function at
intermediate policy checkpoints" [`ma2024eureka`, §3.3], and an ablation shows that removing this
structured feedback degrades performance by roughly a third — direct evidence that feedback *content* matters. A
parallel line on language-model optimisers reaches the same conclusion from the other direction: scalar reward
alone is a weak signal, and richer, more *directional* feedback substantially improves an optimiser's search
[`agrawal2026gepa`]. A concurrent workshop study has now given the axis a name — "feedback engineering" — comparing
sparse against dense feedback for language-model-synthesised *policy* code, though without reward authorship,
placebo controls, inferential statistics, or a tail axis [`gallego2026beyondscalar`]. This crystallises the
**mechanistic question at the centre of this
dissertation**: does showing the reward-designer the *downside* — the lower-tail distribution of realised
outcomes, rather than a scalar — change the reward *code* it writes, and does that change propagate to the trained
agent's realised tail behaviour? We cast this as a **three-link causal chain** — fed tail signal → authored reward
code → trained policy → realised tail — and ask, through three sub-questions (does the signal move the code? does
the code move the outcome? is any effect genuine *use* of the tail content or a surface echo?), not merely
*whether* richer feedback helps but *where* the channel acts or breaks. To our knowledge this has not been tested.
Nor is the answer obvious ex ante: language models' risk-taking behaviour is documented to be systematic yet
steered by surface conditioning such as an assigned persona [`hartley2025personality`], so whether a
reward-authoring model genuinely absorbs fed tail information cannot be presumed in either direction.

## 1.3 The gap, and the contribution

We can locate the precise gap by triangulating the nearest prior work. The structural twin of our design — a
language model that proposes reward *code* and iterates on it using a *distribution* surfaced from simulation — is
the Decision-Language Model [`behari2024dlm`], but it operates in public-health resource allocation with no
risk/tail sensitivity, no fixed-agent isolation, and no pre-registration. In finance, to our knowledge, no system
yet gives the language model open-ended reward authorship with tail-distributional feedback: FinRL-DeepSeek uses it as a
*sentiment-and-risk signal encoder* feeding a *fixed, human-written* CVaR-sensitive objective — the model never
authors the reward [`benhenda2025finrldeepseek`]; GIFT lets it select reward terms from a *fixed risk-rule
library*, but jointly with the state and refined on generic scalar diagnostics rather than any return-tail
distribution [`wu2026gift`]; and ELfolio evolves whole strategy code under a *scalar Sharpe fitness*
[`zeng2025elfolio`]. The reward-code designers closest in
*mechanism* — Eureka, and the dynamic-feedback framework CARD — operate in robotics with scalar or
order-preservation feedback, not a multi-level financial tail [`ma2024eureka`; `sun2024card`]. None occupies the
conjunction at which this dissertation sits:

> an LLM authors reward-function **code**, iterating on the **multi-level lower-tail distribution** of realised
> returns (measured off-critic), for a **fixed risk-sensitive portfolio RL agent**, under a **pre-registered,
> controlled comparative protocol**.

The fourth element — pre-registration — appears to be unique to this work across the entire LLM-reward-design
literature, and it is the element the automated-discovery agenda most conspicuously lacks. We therefore frame the
contribution not as "reward engineering" but as a *controlled, pre-registered evaluation of automated
objective-function discovery* — supplying the rigour the discovery line omits.

Concretely, the dissertation makes four contributions, none contingent on a positive empirical result; the fourth
— a mechanism characterisation — is the foregrounded headline, and the first three are the machinery that makes it
credible:

- **C1 — An off-critic feedback instrument that isolates the feedback content.** A method for feeding a language-model
  reward-designer the realised-return lower tail (CVaR at multiple levels, left-tail mass, robust skew), measured
  *off the critic* from realised returns, while the reinforcement-learning agent is held byte-identically fixed
  across experimental arms. It isolates the feedback *content* as the manipulated variable — not an exogenous
  measurement: the fed tail is *endogenous* to the policy it steers (coupled reward→policy→measurement loops), so
  the comparison is honestly one between two coupled loops. The instrument is *three-way decoupled* — the tail is **fed** on the training split,
  candidates are **selected** on a tail-blind validation criterion, and the hypothesis is **tested** on empirical
  CVaR over a sealed test split — so that any tail effect is attributable to the feedback channel rather than to a
  self-grading estimator. To our knowledge this separation is novel in both LLM-reward-design and
  reinforcement-learning-for-finance, where prior work conflates at least two of the three roles.
- **C2 — A pre-registered comparative protocol yielding a bankable result of either sign.** A cryptographically
  frozen design — hypotheses, arms, budget, seeds, splits, embargo, tail-diagnostic set and analysis plan fixed
  before the sealed leg — with intersection–union testing, placebo and structure-shuffled controls, deflated
  Sharpe ratios and combinatorial backtest-overfitting probabilities. A non-rejection is reported as a bounded,
  pre-registered equivalence — or, when the minimum detectable effect exceeds the pre-registered SESOI, as a
  calibrated *inconclusive* verdict — never as an underpowered failure.
- **C3 — A decision-theoretic envelope delimiting when richer feedback can help.** A theory (Chapter 3)
  establishing that an optimal user of the tail vector weakly dominates an optimal user of a scalar summary
  (Blackwell sufficiency, with a Le Cam-deficiency bound), that the fed vector is a sufficient and jointly
  elicitable representation of the coherent-risk class, and that feeding the tail is — by a duality — feeding a
  distributional-robustness signal; together with the conditions under which a *bounded* realisation attains the
  envelope, this turns the empirical question into a falsifiable prediction.
- **C4 — A mechanism characterisation that *locates* where the feedback channel acts (the headline finding).** A
  pre-specified, report-only decomposition of the causal chain *fed tail signal → authored reward code → trained
  policy → realised tail* into three sub-questions — **responsiveness** (does the signal move the code?),
  **transmission** (does the code move the outcome?), and **specificity** (is the effect genuine use of the tail
  *content* or a surface echo, and is any failure a numeric-legibility bottleneck
  [`wallace2019numbers`; `yang2025cookbook`; `singh2024tokenization`]?) — instrumented by a
  responsiveness statistic, a fed→code→outcome mediation, an identifier-invariant structural comparison of the
  authored code, and a legible-format ablation, all disjoint from the confirmatory testing family. This turns a
  null from an absence of evidence into a *located* finding about *where* the chain breaks; with the pre-registered
  performance comparison (C2) as its rigorous backdrop, it is the dissertation's headline. Jointly, the design is
  factorial in kind: the main arms manipulate the feedback's *content*, while the pre-registered legible-format
  ablation manipulates its *encoding* — together, to our knowledge, the first factorial dissection of the
  feedback channel in automated reward design.

## 1.4 An honest result, framed as a boundary condition

This dissertation commits in advance to a hypothesis it may not confirm, which shapes how the result is
reported. We follow the discipline of the
strongest empirical "re-examination" papers — which establish that a rigorously demonstrated null or
boundary-condition is a contribution, not a disappointment — by leading with the *instrument* and reporting the
*finding* as its output [`henderson2018matters`; `lucic2018gans`; `dacrema2019progress`; `webson2022prompt`;
`schaeffer2023mirage`; `kerr1998harking`].

**[Result — to be finalised from the confirmatory campaign.]** A directional prototype (Chapter 5) provides the
honest interim statement: the apparent tail advantage did **not** survive its own zero-information placebo control,
and the language model's reward code was, if anything, *less* responsive to larger movements in the fed tail —
the signature, under a tail-blind selector, of the "Null" branch of the pre-registered prediction table (Chapter 3,
§3.7). We therefore report a bounded, pre-registered comparison rather than a performance claim. Read through the
theory, this is not an absence of evidence but a *severely tested prediction about the gap between the
information-theoretic envelope and its bounded realisation*: the channel that an optimal user could exploit exists,
and the tested language-model designer — under tail-blind selection and at the studied budget — does not exploit it.
The credit for the null rests not on Popperian corroboration — pre-registration does not, on its own, improve the
severity of a Popperian test (Rubin 2025) — but on error-statistical *severity* (Mayo): the frozen, deviation-free
cryptographic protocol admits no sample-based deviations and so no unknown Type-I inflation, and the whole analysis
plan is fixed in advance, foreclosing the garden of forking paths (Gelman & Loken 2014). Accordingly the null is
reported as a TOST equivalence against the pre-registered smallest effect size of interest, not as a bare *p* > 0.05.

A note on terminology is required for the same reason. The fed signal is a vector of six left-tail scalars (CVaR at
5/10/25/1%, left-tail mass beyond −2σ, and a robust left-tail skew), estimated with an extreme-value tail for the
5% and 1% levels. It is **not** the full return distribution: it carries no central moments beyond the mean
(supplied separately), no right tail, and no full quantile grid. We therefore name the construct **multi-level
tail-risk feedback** throughout, not "the distribution"; the theory of Chapter 3 shows these statistics span the
law-invariant *coherent-risk* class, which is the precise and defensible claim, and we make no claim about
non-coherent or upside features of the return law.

## 1.5 Scope and what this dissertation is *not*

The study is deliberately narrow so that its single causal claim can be cleanly identified. It holds the agent
fixed and varies only the feedback block; it does not propose a new reinforcement-learning algorithm, a new market
model, or a trading system for deployment. It runs one universe of US large-cap equities over one historical
window with one family of language model; it therefore claims a boundary condition for that instance and discloses,
rather than generalises past, the resulting limits to external validity (Chapter 7). Where the design makes a
choice that constrains the result — a tail-blind selection criterion, a softmax action parameterisation that cannot
reach an exact cash position, an extreme-value tail estimator with finite-sample bias on a few hundred observations
— we surface the choice, cite the relevant literature, and record it as a disclosed limitation rather than a hidden
assumption. The dissertation's claim to rigour rests less on the size of its result than on the honesty and
control with which that result is obtained.

## 1.6 Roadmap

Chapter 2 reviews the three literatures the work joins — language-model reward design and automated discovery,
risk-sensitive and distributional reinforcement learning, and the statistics of backtest evaluation — and locates
the empty cell precisely. Chapter 3 develops the theory: the dominance of tail feedback for an optimal designer,
the sufficiency and elicitability of the fed vector, the CVaR–robustness duality, and the pre-registered prediction
table. Chapter 4 specifies the data (a survivorship-free, point-in-time US-equity panel), the fixed agent, the
off-critic measurement instrument, the experimental arms and controls, the frozen pre-registration, and the
inference plan. Chapter 5 reports the directional prototype and the lessons that hardened the confirmatory design.
Chapter 6 reports the confirmatory campaign and its mechanism analyses — the reward-program differential, the
mediation of responsiveness, the model-confidence-set comparison of arms, the synthetic-null falsification, and the
regime-conditional and transaction-cost robustness checks. Chapter 7 discusses what the boundary condition means
for automated reward design, states the limitations in full, and concludes.
