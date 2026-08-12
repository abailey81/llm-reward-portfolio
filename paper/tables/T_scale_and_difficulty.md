# Appendix E — What was built, and the specification in full

Criterion 3 scores an outcome against the difficulty of obtaining it, and difficulty is the one property
of a computational study that leaves no trace in its prose. **Table 1.2 supplies the counts.** This
appendix carries the two things a count cannot convey: which parts of the system were taken off the shelf
and which had to be built, and what the hard part actually was. It then prints the full specification,
so every parameter the body states can be diffed against the frozen configuration it was read from.
Table E.1 begins with the division of labour between what was imported and what was written.

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table E.1 — Off the shelf against written for this study.** The standard machine-learning components were imported, and everything that carries the identification claim had to be built.
```{=latex}
\par\endgroup
```

| Off the shelf, used as published | Written for this study |
|---|---|
| Stable-Baselines3 SAC, and sb3-contrib TQC for the secondary critic experiment | the long-only 31-weight portfolio environment, with half-$L_1$ drifted turnover accounting |
| PyTorch, NumPy, pandas, SciPy | the reward contract and AST-gated sandbox for executing untrusted model-authored code |
| provider SDKs and a retry layer | the tail-measurement and feedback stack, empirical and extreme-value, read off the critic |
| licensed Refinitiv/LSEG market data | the reflection loop, the nine arms, and the two placebo controls |
| — | the inference stack: Deflated Sharpe, PBO, TOST equivalence, `rliable` per-seed aggregation, BH-FDR |
| — | the cluster orchestration layer, with archive-truth resume, per-batch driver locks and a 17-check live sentinel |
| — | the survivorship-free point-in-time data pipeline, and the figure engine |

**What the difficulty consisted of.** Three things, stated plainly because no count conveys them.

Executing untrusted generated code safely, 25,602 times as at 2026-08-09 and 42,128 times over the full
registered ladder. Every reward is model-authored Python, compiled and run inside the training loop. It
is AST-gated once, then executed in-process on anonymised arrays. A single unguarded construct is a
remote-code-execution path.

**Holding an identification claim across twelve concurrent execution lines.** Only the fed feedback block
may vary. Three separate defects in this campaign were the same shape, a resource shared across
concurrent lines but keyed by an identifier unique only within one line. None was caught by the test
suite as it stood when it was introduced, because those tests construct one line at a time and a
single-process test has no representation of a cross-line collision. All three were found by live
invariants over the running system, and the suite now carries explicit two-line and twelve-line
regression tests for the class.

**Bit-exact determinism as a design constraint rather than an aspiration.** Common random numbers underpin
every paired contrast, so the CPU model, the thread count, BLAS parallelism, `tf32` and every provider pin
are part of the frozen design. One host with a different Xeon generation was enough to raise a validity
alarm and required fencing, and Appendix A records what that cost.

## E.1 The learner and the environment, as frozen

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table E.2 — The fixed learner.** Every row is byte-identical across arms, so the learner cannot be a source of between-arm difference.
```{=latex}
\par\endgroup
```

| Component | As executed |
|---|---|
| Learner | Soft Actor-Critic [`haarnoja2018sac`; `haarnoja2019applications`], clipped double-Q [`fujimoto2018td3`], in Stable-Baselines3 [`raffin2021sb3`] |
| Hyperparameters | read from the frozen `config/` files, identical in every arm |
| Observation | 60-session return window, realised volatility at 20 and 60 sessions, the $t{-}1$ VIX close, a cash marker, the previous weights |
| Action | softmax simplex over 30 assets plus cash, long-only, fully invested |
| Transaction cost | 10 bps one-way on drifted half-$L_1$ turnover; grid 0 / 5 / 10 / 25 / 50 |
| Value-target normaliser | PopArt [`vanhasselt2016popart`], applied uniformly, scale logged per candidate |
| Training budget | 400,000 environment steps per candidate |
| Evaluation | one deterministic walk-forward rollout [`sood2023deep`], truncated at the window edge |
| Secondary critic | truncated-quantile critic [`kuznetsov2020tqc`], a named secondary experiment |

```{=latex}
\Needspace{4\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table E.3 — Environment specification (`config/environment.yaml`).** The environment makes turnover a decision and not a by-product: the agent sees its own previous weights and pays ten basis points on every unit it moves.
```{=latex}
\par\endgroup
```

| Field | Value |
|---|---|
| Risky assets | 30 plus cash, 31 weights summing to 1 |
| Universe selection | top market capitalisation, point-in-time at the window start |
| Observation lookback | 60 sessions, which is also the purge |
| Realised-volatility windows | 20 and 60 sessions |
| VIX in state | yes, pre-lagged |
| Previous weights in state | yes |
| Action space | simplex, softmax projection, long-only by construction |
| Transaction cost | 10 bps one-way; grid 0 / 5 / 10 / 25 / 50 registered report-only |
| Timing | the trade settles before the return is earned |
| Cash rate | 0.0; the risk-free series enters the reported Sharpe, not the environment |

## E.2 The report-only exhibits and the estimators behind them

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table E.4 — The report-only exhibits, and what each guards.** Five separate threats to the headline reading each carry a named check, and none of those checks can spend alpha or move a registered verdict.
```{=latex}
\par\endgroup
```

| Exhibit | The threat it is aimed at | Construction |
|---|---|---|
| Fed-vector ablation | the tail effect resting on the two coordinates outside the coherent-risk sub-vector | re-estimate H2-Tail on the four CVaR levels alone (§C.5) |
| CVaR-grid robustness | the fed profile being an artefact of the chosen $\alpha$-grid | recompute at a denser and a sparser grid; report whether responsiveness and the H2 ordering are grid-invariant |
| Regime concentration | a benefit that exists only where the distribution shifts most, unreported | the directional prediction of §C.6, with full walk-forward re-estimation carried as a disclosed deferred limitation (§6.2) |
| Expected-Shortfall scoring | crediting the treatment arm for a directional advantage | **two-sided** Diebold–Mariano equal-accuracy test on the jointly-elicitable Fissler–Ziegel loss [`fisslerziegelgneiting2015`; `patton2019dynamic`], deliberately not Nolde–Ziegel's one-sided comparative backtest |
| Factor attribution | the headline being a disguised low-volatility beta | CAPM through a six-factor model with Betting-Against-Beta and Quality-Minus-Junk, Newey–West errors [`frazzini2014bab`; `asness2019qmj`; `newey1987simple`] |

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table E.5 — The inference machinery, and where each piece comes from.** Every technique below is a published estimator used as its authors intended, and none is an ad-hoc construction, so a reader can check each against its published source instead of against our description of it.
```{=latex}
\par\endgroup
```

| Component | The job it does here | Source |
|---|---|---|
| Per-seed IQM, paired stratified bootstrap | the unit is a seed, not a day | [`agarwal2021rliable`] |
| Common random numbers | arms see the same market draws | [`lecuyer1994efficiency`; `law2015simulation`] |
| Stationary block bootstrap | difference tests without assuming independence | [`politis1994stationary`] |
| TOST equivalence | makes a non-rejection a bounded claim | [`lakens2018tost`] |
| TOST as an intersection-union test | why equivalence may propagate $\alpha$ | [`bergerhsu1996equivalence`] |
| Intersection-union tests | the conjunction is the multiplicity correction | [`berger1982iut`] |
| Graphical $\alpha$-propagation | four nodes made confirmatory at zero cost | [`bretz2009graphical`] |
| Closed testing | why strong family-wise control holds | [`marcus1976closed`] |
| Gatekeeping | downstream nodes open only on upstream rejection | [`dmitrienko2003gatekeeping`; `dmitrienko2009mtp`; `bretz2010mcr`] |
| Benjamini-Hochberg at q = 0.05 | the cross-family sensitivity, not the primary control | [`benjamini1995fdr`] |
| Romano-Wolf stepwise | the family-wise alternative, a robustness check | [`romanowolf2005stepwise`] |
| Conditional equivalence testing | the registered alternative framing | [`campbell2018cet`] |
| PBO via CSCV | the primary overfitting guard, trial-count free | [`bailey2017pbo`] |
| Deflated Sharpe | the selection metric and secondary cross-check | [`bailey2014deflated`] |
| Joint (VaR, ES) elicitability | why a vector target is scorable | [`fissler2016higherorder`; `gneiting2011making`; `nolde2017elicitability`] |

## E.3 Who wrote the rewards, and what makes the study reproducible

Table E.6 pins the eleven authoring models and Table E.7 states what each reproducibility layer claims.

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table E.6 — The eleven reward-authoring models, with reproducibility pins (`config/legs.yaml`).** Reasoning is off and the output cap identical in every row, so a difference between these lines is a difference between models and not between the settings they were run at.
```{=latex}
\par\endgroup
```

| # | Model | Provider | Weight pin (HF commit) | Reasoning | Output cap |
|----|----------------|--------------|--------------------|--------------|------------|
| — | **`claude-opus-5`**| Anthropic | closed (vendor weight-preservation commitment cited) | off | 16,384 |
| 1 | `deepseek/`\allowbreak`deepseek-`\allowbreak`v4-pro` | OpenRouter | `deepseek-ai/`\allowbreak`DeepSeek-`\allowbreak`V4-Pro` @ `b5968e91…` | off | 16,384 |
| 2 | `z-ai/glm-5.2` | OpenRouter | `zai-org/GLM-5.2` @ `b4734de4…` | off | 16,384 |
| 3 | `qwen/`\allowbreak`qwen3.6-27b` | OpenRouter | `Qwen/Qwen3.6-27B` @ `6a9e13bd…` | off | 16,384 |
| 4 | `qwen/`\allowbreak`qwen3.5-9b` | OpenRouter | `Qwen/Qwen3.5-9B` @ `c2022362…` | off | 16,384 |
| 5 | `claude-haiku-`\allowbreak`4-5-20251001` | Anthropic | closed, dated snapshot | off | 16,384 |
| 6 | `openai/`\allowbreak`gpt-5.6-luna` | OpenRouter | closed | off | 16,384 |
| 7 | `nvidia/`\allowbreak`nemotron-3-`\allowbreak`super-120b-`\allowbreak`a12b` | OpenRouter | `nvidia/…-`\allowbreak`Super-120B-`\allowbreak`A12B-BF16` @ `d51eab0d…` | off | 16,384 |
| 8 | `claude-`\allowbreak`sonnet-5` | Anthropic | closed | off | 16,384 |
| 9 | `google/`\allowbreak`gemini-2.5-`\allowbreak`flash` | OpenRouter | closed | off | 16,384 |
| 10 | `moonshotai/`\allowbreak`kimi-k3-`\allowbreak`20260715` | OpenRouter | closed, dated snapshot | off | 16,384 |

Output caps are matched at 16,384 under amendment R106, which is what makes the cross-model comparison
fair and why the cap was not raised mid-run even where a model truncates against it. The weakest line,
`qwen3.5-9b`, is the one that truncates most often. Its rejects are a registered finding and not a fault,
and its failures are overwhelmingly node-side, meaning its authored code crashed when executed rather
than being turned away by our screen.

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table E.7 — The three-layer reproducibility statement.** The first two layers cover the whole study and the third only five of the eleven authors, so the limit of the claim is visible in the table rather than in a caveat.
```{=latex}
\par\endgroup
```

| Layer | The claim | Evidence | Standard |
|---|---|---|---|
| Protocol | anyone can re-run it without our keys | the keyless golden path, frozen configs and the design hash | [`kapoor2024reforms`] |
| Analysis | results are replayed, never regenerated | every prompt, program, block and metric archived; `audit_reproducibility.py` reports 8 pass, 0 warn, 0 fail | [`pineau2021reproducibility`; `gundersen2018reproducibility`] |
| Experiment | the generative step is itself reproducible | five of eleven authors carry a repository and commit hash. Six, including the registered node, are vendor-only | [`spirling2023opensource`] |

Replay was demonstrated stage by stage rather than claimed for the archive as a whole. On the test stage
every stored endpoint is recomputed from its stored return series, bit-exactly under this repository's own
estimator and to a floating-point tolerance under an independent re-implementation, over 23,734 records
across 71 of 71 comparison units. On the search stage 1,483 of 1,494 units carry archived source and 1,479
re-execute through the same static gate. The eleven canon rewards resolve by name rather than from
archived source.

Replay is the only honest analysis claim here. Hosted models are not deterministic even at fixed settings [`fu2026beyond`; `he2025defeating`], so bit-exact regeneration would be a false claim while bit-exact replay from the archive is true and checkable. The pins exist for the same reason: closed models change under a fixed name [`chen2023chatgptdrift`; `chen2021codex`], so an unpinned model is not a specification. A survey of 1,500 scientists found a majority had failed to reproduce another group's results and more than half their own [`baker2016reproducibility`], and an audit of thirty language-model trading studies found execution assumptions routinely undocumented [`yao2026execution`].

The mechanism analysis rests on published method rather than on invented machinery. The mediator-moderator
distinction the decomposition depends on is [`baron1986moderator`], the identification conditions and
estimator are [`imai2010general`], the direct-against-indirect framework that makes "the chain is severed
at link 1" statable is [`vanderweele2015explanation`], and the structural and counterfactual languages are
[`pearl2009causality`] and [`imbens2015causal`; `holland1986statistics`]. The numeracy hypothesis is
anchored the same way: magnitude is encoded internally yet used unreliably [`yuchi2026numbers`], numerical
ability is uneven across models [`li2025numeracygaps`], small perturbations flip numerical reasoning
[`sun2025numericalsensitivity`], authoring reliability falls at the capability floor
[`hasan2025smallcode`; `souza2025codeforces`], generated code reproduces known bug patterns
[`guo2025bugreplicators`], capability benchmarks over-report through contamination
[`liang2025swebench`], and repeated sampling materially changes what a model achieves
[`brown2024monkeys`], which is why a matched candidate budget and a seed ladder are necessary.

One condition is named rather than assumed. The fed tail is endogenous, because it is measured on the
policy trained under the reward being designed. The decomposition therefore has a causal reading only
under sequential ignorability, and it is reported descriptively.

## E.4 The axis the lineage leaves empty

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table E.8 — The four axes the lineage innovates on, and the fifth it leaves empty.** Innovation in the 2024 to 2026 literature clusters on four axes and leaves a fifth unoccupied. **What to conclude:** the empty axis is empty for a structural reason, because occupying it requires a control condition and no system the sweep surfaced runs one.
```{=latex}
\par\endgroup
```

<!-- Same arithmetic as Table 2.1, different answer, because nothing here is starved. Measured
     demand is 62.1 · 96.3 ("vision/semantics", no break at the slash) · 60.6 pt against 429.54pt
     available, so the binding consideration is CONTENT rather than fit: the middle column carries
     1,248 of the 1,797 set characters and the equal thirds gave it 143.2pt, which set the whole
     exhibit over three pages while the outer two columns ran mostly white. The counts 3/10/4 set
     75.8 · 252.7 · 101.1 pt, all above demand, and the table then sets in one page. -->

| Axis — what the work varies | Representative work | Our relation |
|---|----------|----|
| **1. The search method** | evolutionary refinement (Eureka); **Monte-Carlo tree search** [`rfagent2026`]; **Bayesian optimisation with self-consistency pruning** [`yang2025urdp`]; **evolution of heuristics** [`liu2024eoh`]; **the model as optimiser** [`yang2024opro`]; **LLM-based adaptive reward search** [`lares2025adaptive`] | held **fixed** — reflect-on-best, 6 generations × 5 candidates, identical for every arm |
| **1a. The comparator roster's coverage, stated** | our four derivative-free arms span the **random**, **model-based**, **evolutionary** and **density-estimator** families. Two further families are deliberately absent and named rather than silently omitted: **simplex/direct-search** [`nelder1965simplex`], excluded because it is a local method on a non-smooth, stochastic objective; and **multi-fidelity bandit** hyper-parameter search [`falkner2018bohb`], excluded because our budget is fixed at B\* by pre-registration, so there is no fidelity ladder to exploit | the roster is chosen for **family coverage**, not count |
| **2. The feedback modality** | scalar component series (Eureka); human prose (Text2Reward); Elo preferences (REvolve); trajectory orderings (CARD); **vision/semantics** [`lee2026rda`] | held **fixed** — a rendered numeric block, identical in shape across arms |
| **3. Autonomy / context reduction** | metrics derived from the task description alone, no environment source [`cardenoso2025learnopt`]; multi-agent coordination replacing reward engineering [`su2026endrewardengineering`] | not our axis |
| **4. The object being designed** | the *metric* rather than the reward [`yuksel2025alphasharpe`]; the reward **model's output distribution** rather than its input [`dorka2024quantile`] | we vary neither — the reward **code** is authored, the metric is frozen |
| **5. The feedback CONTENT, under a fixed method and modality, WITH CONTROLS** | **none found**, and the two nearest misses are named rather than a void asserted: sparse against dense feedback for model-synthesised **policy** code in social dilemmas [`gallego2026beyondscalar`], which varies content but not for a reward and runs no control; and a placebo-controlled study of risk feedback to trading agents [`xue2026riskfeedback`], which runs the control but in which the model **is** the agent. Fifty-six ablations and zero placebos across the fifteen papers searched | **this study** |

**The distinction that matters most is axis 4.** [`dorka2024quantile`] also puts a *distribution* into a
reward pipeline, but it is the reward model's output, consumed by an optimiser, and it demonstrably helps.
Ours is an input to a language model acting as reward author, so the contrast is not "does distributional
information help?", which is settled, but "is it usable by this consumer?", which localises any failure to
the interface rather than to the information.

**Adjacent but off-axis: risk in the *critic*.** A parallel literature makes the *agent* risk-sensitive,
through dynamic convex risk measures [`coache2024dynamicrisk`], conditionally elicitable dynamic risk
[`coache2023elicitable`] and distributional Soft Actor-Critic [`duan2021dsac`]. Those are the closest work
in *spirit* and furthest in *mechanism*: they change what the agent optimises, this study does not, and
conflating them is the likeliest misreading of this dissertation (§2.3).
