# Chapter 1 — Introduction

Reinforcement learning works well where the reward function is well defined, and in finance it is
not. An agent trained to maximise average return can perform for years and then lose much of its
value in days. What matters to an investor is rarely the mean of the return distribution but the
severity of its left tail. Someone must decide what the agent is told to want, and until recently
that someone was always a person.

A language model can now decide it instead. It writes a reward function as code, an agent trains on it, the
model reads back how the agent did, and revises the code. Every element of that loop has improved since the
method was demonstrated, except one. What the model is shown between rounds is a performance score, never the
shape of the distribution its own reward produced. This dissertation asks what happens when it is shown that
shape.

**Research question.** *Does showing a language-model reward-designer the lower tail of the realised
outcome distribution, rather than a single score, change the reward code it writes, and does that change
propagate to the trained agent's realised tail behaviour?*

Two questions follow, and only the second carries the registered headline. The first is whether a language
model can write an effective objective at all. The bar is eleven hand-written objectives from the literature
and four numerical optimisers at matched budget. The second is whether the evidence the model is shown
changes what it writes. Figure 1.1 draws the loop and Listing 1.1 gives the whole manipulation. Terms are
defined in the Glossary.

![**Figure 1.1 — The experiment on one page.** Only one edge of the loop differs between conditions, and the quantity shown to the designer is never the one that grades it, so a difference has a single possible source.
](docs/figures/F_ch1_design.pdf)

```{=latex}
\begingroup\tabcaptionstyle
```
**Listing 1.1 — The entire manipulation, reproduced from the executed campaign archive.** What separates the five conditions is a few lines of rendered text, so a reader can check the manipulation directly rather than take its description on trust.
```{=latex}
\par\endgroup
```

```text
Every arm's block opens with the same line, carrying its own score:

  Your previous reward scored: <score> (validation Deflated Sharpe).

What may follow that line is the whole of what this study varies.

scalar
  (the block ends at the score line)

scalar_cvar5
  CVaR 5%: -0.0233

placebo
  Reference constants (inert; no diagnostic content):
    reference value 1: +0.0000
    reference value 2: +0.0000
    reference value 3: +0.0000
    reference value 4: +0.0000
    reference value 5: +0.0000
    reference value 6: +0.0000

distributional
  Realized-return tail diagnostics (training period):
    CVaR 5%:        -0.0268
    CVaR 10%:       -0.0198
    CVaR 25%:       -0.0118
    CVaR 1%:        -0.0467  (high-variance estimate)
    left-tail mass: +0.0223
    left-tail skew: -0.0457

placebo_shuffled
  the six lines above, values deranged across their labels
```

At the same candidate slot, everything outside this block is byte-identical across the arms of a given
model. The two placebo arms make the comparison interpretable.[^blocks] One carries no information in the
same shape. The other carries the same six numbers with the mapping from value to label destroyed.

## 1.1 Reward design is the bottleneck

The reward function encodes what a trading agent is told to want, and specifying it badly is not a peripheral
risk. A safety literature
documents that the gap between what we reward and what we want is where learning systems fail.[^specification]
An older observation takes this optimisation form. A measure adopted as a target stops being a good measure
[`strathern1997improving`; `manheim2018categorizing`].

Risk-sensitive rewards are harder, because what matters lives in the shape of the outcome distribution and
not its mean. The training window shows why. The ratio of the actual average loss on the worst days to the
loss a bell curve predicts crosses over from 0.84 at moderate levels to 1.66 deep in the tail (§3.2). One
downside number cannot represent a tail whose severity reverses across levels, and a vector of
level-specific averages can. That is what this study varies, and most trading agents are trained on a
scalar anyway [`hambly2023advances`].[^byhand]

## 1.2 Language models can author reward code, but on what feedback?

The Eureka line of work showed that a language model can write reward-function code, train an agent
on it and improve it from feedback, matching or beating human-engineered rewards on dozens of control
tasks [`ma2024eureka`; `xie2024text2reward`; `ma2024dreureka`], and it belongs to a wider
agenda[^discovery] in which models evolve code against an evaluator. Those systems are evaluated by
demonstration rather than by controlled inference [`gridach2025agentic`], which shows discovery is
possible without showing what caused it.

One question inside the loop has never been the manipulated variable. What should the designer be shown? Two
directions establish that it matters, an ablation inside the lineage and an independent line on
language-model optimisers.[^feedbackmatters]

Whether a richer signal reaches this reader is a different question, and the reason is architectural.
A language model never receives a number. It receives characters, at whatever precision the numbers
were rendered into text, and its risk behaviour moves with conditioning as slight as a persona
[`hartley2025personality`]. The question generalises. Wherever an automated designer is improved
against a summary of its own output, whether widening that summary changes what it writes is a
property of the designer rather than of the summary.

## 1.3 No language model has written the reward function for a portfolio agent before

Two mature literatures are jointly silent here. Reward design by language model is a robotics and
control literature with no risk-sensitive objective in it, and the finance systems that put a model
inside a trading loop all stop short of the reward itself (§2.2). So this study appears to be the first
in which a language model writes the reward function for a risk-sensitive portfolio agent.[^finance]
Table 2.1 sets the nine nearest systems against seven columns, so the claim is checked cell by cell
rather than believed.

Two further claims stand on their own evidence. Across fifteen systems and 446 pages the lineage's count
is fifty-six ablations and no placebo, and the analysis plan here was hash-stamped before the sealed window
opened, which appears to be the only such instance in this literature.[^fence]

A designer free to ignore part of what it is shown cannot be made worse off by seeing more, so an
optimal user of the fuller block can never be beaten by an optimal user of the score. That is a
theorem, because the two prompts are nested and deleting coordinates is a valid post-processing
[`blackwell1953equivalent`].[^dominance] Section 4.9 states it formally and names the assumption
under which it also bounds a designer that is not optimal. Dominance is an envelope for a perfect
user, and this study measures what a bounded one attains.[^estimation]

Difficulty is stated in counts, not adjectives (Table 1.1).[^scale]


```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 1.1 — The scale of the executed system.** Read down the right-hand column. Every figure is read from an executed artefact, and the three that are lower bounds are marked.
```{=latex}
\par\endgroup
```

| Quantity | As executed |
|---|---:|
| Language models authoring objectives | 11 |
| Experimental conditions | 9 arms, 70 cells |
| Candidates authored per arm | 30 |
| Environment steps per training | 400,000 |
| Seeds per condition | 102 |
| Sealed-window trainings at that depth | 7,242 |
| Trainings executed and archived | 25,602 |
| Processor-hours consumed | 288,533 |
| Peak cores held concurrently | 2,328 |
| Concurrent supervised execution lines | 12 |
| Python modules written for this study | 111 |
| Lines of code under `src/` | 34,452 |
| Automated tests passing at the launch gate | 2,875 |
| Registered pre-analysis amendments | 105 |
| Model-written programs executed in the training loop | every one |

Seven contributions follow, and they are facets of one. We make the feedback channel of automated
reward design measurable. Table 1.2 states the hypotheses, Table 1.3 the contributions.

```{=latex}
\Needspace{6cm}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 1.2 — The four pre-registered hypotheses.** Each was given its decision rule before the data were seen. Three of the four require the claim to hold against every comparator at once, which is a harder bar than any single comparison.
```{=latex}
\par\endgroup
```

| | Question | Decided by |
|---|---|---|
| H1 | does the model-written reward beat the best hand-designed one? | dominance over an eleven-reward canon |
| H2 | does tail feedback beat scalar feedback? (the headline) | two co-primary tests against three comparators |
| H3 | does iterative reflection beat single-shot generation? | equal budget, spent iteratively or at once |
| H4 | does the model beat numerical search? | dominance over four standard optimisers |

The registered H2 contrast estimates a difference between two selected programs, not between two
feedback conditions, and §4.7 states why.

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 1.3 — The seven contributions, the evidence for each, and where it is established.** Six are settled by artefacts that exist now, and only C7 waits on the sealed verdict. C6's gross-against-net figures are $+0.964$ and $-0.106$, a paired cost wedge of $1.070$, and no canon member beats a costless equal-weighted portfolio even gross.
```{=latex}
\par\endgroup
```

| # | Contribution | The evidence | Where |
|---|---|---|---|
| C1 | the pre-registered protocol, and the identification design inside it | a hash over nine files, and a dated amendment log | §4.8, App. A |
| C2 | the off-critic instrument, read from returns and not from the critic | zero tail vocabulary reaches `scalar` or `placebo` | §4.5 |
| C3 | the decision-theoretic envelope for an optimal user, and its limit | dominance proved on the exact nested reduction | §4.9, App. C |
| C4 | the mechanism characterisation: responsiveness, transmission, specificity | five rival accounts, each with its own fingerprint | §5.5 |
| C5 | the measured authoring-capability gradient across eleven models | read from the executed ledgers, as a lower bound | §5.8 |
| C6 | ten of eleven expert rewards surrender their gross return to one friction | 1,122 archived sealed-window records | §6.2 |
| C7 | the confirmatory verdict on the performance contrast | sealed until the single look | §5.2 |

## 1.4 A null is the outcome this design was built to make informative

This study registered its predictions before the test data were examined, and one of them is that the
two selected reward programs perform equivalently on risk-adjusted return. A confirmed equivalence is
a result rather than the absence of one, because the analysis rejects any effect larger than a
pre-specified bound instead of failing to reject zero.[^nullcredit] Each of the three outcomes the
test can produce was given its reading in advance (Figure 1.2). What is on offer is the boundary of
the mechanism, not a verdict that one condition won.

![**Figure 1.2 — The three outcomes, and the reading each was given before the data were seen.** The diagram is written in plain words and its registered names are given here, so nothing on the canvas needs decoding and nothing registered is lost. The root is H2, the headline hypothesis, which sets the tail-vector arm against the scalar arm and is decided on two co-primary outcomes at once. **Left branch:** two one-sided tests place the whole interval inside ±SESOI, the smallest effect size of interest, fixed before launch. **Middle branch:** the lower confidence limit sits above 0. **Right branch:** the minimum detectable effect exceeds SESOI, so the study could not have resolved an effect of the registered size whatever the truth, and the registered instruction is then to report the effect with its confidence interval and claim neither verdict. **What to conclude:** no outcome of the test can be reinterpreted after the fact, because each branch already carries its reading, including the one that favours the study least.
](outputs/figures/F2_prediction_branch.pdf)

One reporting standard governs the whole document. Every conclusion is a statement about the eleven
authoring models together, and no single model carries one.[^openweights]

## 1.5 What this study does not claim

The study is narrow by design, so one causal claim can be identified cleanly. It holds the agent
fixed, varies only the feedback block, and proposes no new learning algorithm, over one universe of
United States large-capitalisation equities across one historical window, long only, with no leverage
and no short sales. The claim is a boundary condition for this instance and Chapter 6 discloses its
limits. The fed signal is called multi-level tail-risk feedback throughout, never "the
distribution".[^terminology]

[^blocks]: Both placebo blocks are rendered by `src/feedback/schema.py`, one of the nine files bound by the design freeze.

[^specification]: More capable agents exploit misspecification more aggressively, and true performance can collapse while proxy performance climbs [`amodei2016concrete`; `krakovna2020specification`; `skalse2022reward`; `pan2022effects`].

[^byhand]: The hand-written form weighs return against drawdown, semi-deviation, conditional value-at-risk and turnover cost [`moody1998performance`; `sood2023deep`; `orra2025volatility`].

[^discovery]: FunSearch, AlphaEvolve and the AI Scientist are the prominent instances [`romera2024funsearch`; `deepmind2025alphaevolve`; `lu2024aiscientist`].

[^feedbackmatters]: Eureka feeds back "the scalar values of all reward components and the task fitness function at intermediate policy checkpoints" [`ma2024eureka`, §3.3].

[^fence]: The basis is a sweep of 243 assembled papers, 196 read first-hand, under a dated novelty fence last executed on 2026-08-10. The claim is hedged because absence of evidence in a sweep is not proof of absence.

[^finance]: FinRL-DeepSeek uses the model as a signal encoder over a fixed human-written CVaR-PPO objective [`benhenda2025finrldeepseek`; `schulman2017ppo`].

[^nullcredit]: The strongest re-examination papers in machine learning establish that a demonstrated null is a contribution [`henderson2018matters`; `lucic2018gans`; `dacrema2019progress`; `webson2022prompt`; `schaeffer2023mirage`]. Fixing the plan in advance forecloses the garden of forking paths [`gelman2014forking`; `kerr1998harking`]. Pre-registration alone does not confer severity [`rubin2025preregistration`]; the error-statistical argument that does is [`mayo2018severetesting`], applied in §6.1.

[^terminology]: Appendix C shows the six statistics span the law-invariant coherent-risk class. No claim is made about upside or non-coherent features of the return law.

[^dominance]: The formal statement is the Blackwell–Sherman–Stein theorem, used only in the direction that a garbling cannot raise the attainable objective. Section 4.9 proves it for the exact nested reduction these prompts realise.

[^estimation]: The classical allocator that optimises the worst-5% average degrades 88% from in-sample to out-of-sample. One that estimates nothing degrades 4% (Table 5.9b).

[^scale]: Three figures are lower bounds: processor-hours, peak cores and seed depth. Each is re-derived immediately before submission.

[^openweights]: A sixth model, `kimi-k3`, published weights on 2026-07-27, after the freeze. No commit hash is recorded anywhere, so it is counted as closed throughout. A pin nobody can verify is fictional.
