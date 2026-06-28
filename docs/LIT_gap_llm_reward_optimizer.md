# LIT_gap_llm_reward_optimizer — positioning against the LLM-reward-design + LLM-as-optimizer / program-search literature

**Status.** Read-only research-positioning dossier (no code, config, or pre-registration edited). **Date:** 2026-06-25.
**Repo:** `llm-reward-portfolio`. **Grade context:** PDF-only, no viva (supervisor Dr Ramin Okhrati, who co-authored
backtest-statistics and RL-finance corpus papers; citation integrity is load-bearing). **Companion docs:**
`00_planning/LITERATURE_AND_DEFENSE_COMPANION.md` (the canonical paper-by-paper map), `docs/DEEP_H1.md`,
`docs/DEEP_H2.md`, `docs/DEEP_H4.md`, `docs/DEEP_FRAMING_discipline.md` (governance), `RELATED_WORK_WATCH.md`
(novelty surveillance). **Eureka** has its own dossier (referenced throughout, not duplicated here).

**Scope.** This document covers three literatures the dissertation must position against precisely, because they are
where a knowledgeable referee will look first: (A) **LLM reward design / reward-as-code**; (B) **LLM-as-optimizer /
program search**; (C) **reward-shaping / specification classics**. For each: the SOTA and what it does; what THIS
dissertation adds; the gaps a top dissertation would close; the strongest defensible framing; then a prioritized,
conservative list of implementable improvements with grade-ROI and pre-freeze risk.

**Grounding note.** Every primary paper below was read first-hand from the local cache (`D:\tmp\littxt\…`) or verified
this session via web (URLs in §6). 2024–2026 sweep-surfaced items are marked `% VERIFY` until the primary PDF is
confirmed in `paper/refs.bib`, per CLAUDE.md prime directive 4. Two corrections banked this session are flagged ⚠.

---

## 0. Bottom line up front

The dissertation sits in a cell that is **empty on two axes simultaneously**, and the deep web sweep (mid-2026)
confirms it remains empty: **(LLM authors reward *code*) × (the optimization/reflection signal is a realized-return
*distribution*: a multi-level CVaR profile + left-tail mass + robust skew) × (risk-sensitive *portfolio* RL, fixed
SAC agent)**. Across the entire LLM-reward-design and LLM-as-optimizer literature, the feedback that drives the search
is one of **{scalar fitness, per-component scalar time-series, preference/ranking, natural-language critique,
execution-trace text, epistemic self-consistency}** — **never a distribution of realized outcomes**. That is the
genuine, defensible contribution (H2).

Three disciplines govern how the contribution may be *claimed* (from `DEEP_FRAMING_discipline.md`), and this dossier
respects them throughout: (i) **no SOTA claim** — "it works" is established only on the internal matched ladder, never
against the FinRL band as a ranking; (ii) **construct retitle** — "distribution" → **"multi-level tail-risk feedback"**,
because the operationalization is six left-tail scalars, defended as a coherent-risk-principled descriptor; (iii) **H1
is a descriptive Eureka-style panel subordinate to the comparative H2**.

The single most important novelty refinement surfaced this session: **the delta to Eureka is narrower than "scalar vs
rich feedback" and must be stated as such.** Eureka already feeds *per-component scalar statistics over a training
trajectory* (max/mean/min of each reward term at checkpoints) — its scalar-fitness-only ablation costs 28.6%. So the
honest delta is **"the empirical distribution of realized *outcomes* (return tail/quantile structure), not point
statistics of reward *components*."** Framed precisely it is a real contribution; framed loosely it collapses into
Eureka. (§1.A novelty map; §4 framing.)

---
---

# PART A — LLM REWARD DESIGN / REWARD-AS-CODE

## A.0 The feedback-signal taxonomy (the organizing lens)

This is the spine of the entire positioning. Order the prior art by **what signal feeds the reward designer**, and the
empty cell is self-evident:

| Feedback signal class | Representative systems | Domain | Object the LLM produces |
|---|---|---|---|
| **Human natural-language** | Text2Reward (Xie 2024), Language-to-Rewards (Yu 2023) | robotics/control | dense reward *code* / reward *parameters* |
| **Scalar fitness / self-derived metric** | Eureka (scalar-fitness ablation), LEARN-Opt (2025) | robotics/control | reward code |
| **Per-component scalar time-series** | **Eureka** (the actual reward-reflection) | robotics/control | reward code |
| **Preference / ranking** | CARD (TPE, 2025), PROF (RPR, 2025) | robotics/control | reward code |
| **Diagnostic / failure-mode text** | "When LLM Reward Design Fails" (2026) | sparse-RL grids | reward code |
| **Epistemic self-consistency** | URDP (2025) ⚠ *not* CVaR | robotics/control | reward code + intensities |
| **Distribution / population spread** | Decision-Language Model (Behari 2024) — *but* spread of population groups across states, not returns | public-health RMAB | reward code |
| **➜ Realized-return DISTRIBUTION (tail/quantile)** | **THIS dissertation** | **risk-sensitive portfolio RL** | **reward code** |

The bottom row is unoccupied. Every other row is robotics/control or a non-return distribution.

## A.1 Text2Reward (Xie, Zhao, Wu, Liu, et al. — arXiv:2309.11489, ICLR 2024) [read first-hand]

**SOTA / what it does.** Data-free framework that generates *shaped, dense* reward functions as executable Python,
grounded in a compact "expert-abstraction" (Pythonic class hierarchy) of the environment, from a natural-language goal.
The reward trains PPO/SAC; the policy is rolled out; **human natural-language feedback** ("keep the chair standing")
summarizes failure modes and drives iterative refinement of the reward code. Evaluated on ManiSkill2, MetaWorld, and
two MuJoCo locomotion tasks; on 13/17 manipulation tasks it matches or beats expert-written rewards, and a sim-trained
policy transfers to a real Franka arm. Explicitly positions against IRL (data-hungry, uninterpretable) and against
earlier LLM-reward work (Yu 2023) that wrote *unshaped* reward with hand-designed APIs.

**What THIS dissertation adds vs Text2Reward.** (1) **Feedback object:** Text2Reward refines on *human* NL feedback;
this work refines on an *automated, quantitative* signal — the realized-return tail distribution — with no human in the
loop. (2) **Fitness has no ground truth:** Text2Reward's robotics tasks have a simulator success metric; finance has
none, so the fitness is a **held-out validation Deflated Sharpe** decoupled from the candidate reward
(`src/selection/fitness.py`). (3) **Domain:** robotics manipulation vs risk-sensitive portfolio allocation, which forces
the contamination defense and the coherent-risk feedback schema neither robotics paper needed. (4) **Comparative
inference:** Text2Reward reports task success; this work pre-registers a falsifiable comparison of *feedback channels* at
matched compute.

**Strongest framing.** *"Text2Reward established that an LLM can write shaped dense reward code that rivals expert
rewards, refined by human language feedback. We retain the reward-as-code synthesis but replace the human feedback loop
with an automated, quantitative, distribution-valued one, and move from a ground-truth-rich simulator to a
ground-truth-absent financial market."* Cite Text2Reward as a primary ancestor of reward-as-code in the lit-review
lineage and as evidence the method works (in robotics) and has never touched finance.

## A.2 Language-to-Rewards / L2R (Yu, Gileadi, Fu, et al., Google DeepMind — arXiv:2306.08647, CoRL 2023) [read first-hand]

**SOTA / what it does.** Two-stage system: a "Reward Translator" LLM maps NL instructions to **reward *parameters***
(height, pitch, foot targets) of a *fixed reward template*; a "Motion Controller" (MuJoCo MPC, a real-time optimizer)
solves them online. Interactive human NL corrections in the loop. 17 tasks on a simulated quadruped + dexterous
manipulator; 90% task success vs 50% for a Code-as-Policies primitive-skill baseline; deployed on a real arm.

**What THIS dissertation adds vs L2R.** The key structural distinction is **reward *parameters* vs reward *code*.** L2R
fills slots in a human-authored template; this work (like Eureka/Text2Reward) authors free-form reward *code* — a
strictly richer hypothesis space (the same richness axis that powers H4b, §B). L2R is also human-feedback-driven, online
MPC, robotics; this work is automated-feedback-driven, off-policy SAC, finance. Use L2R as the "parameters-not-code"
boundary marker — it is the milder form of LLM reward specification, and naming it sharpens the "we author code" claim.

## A.3 Eureka (Ma et al. — arXiv:2310.12931, ICLR 2024) — referenced, covered by separate dossier [read first-hand]

Covered in depth by its own agent and `LITERATURE_AND_DEFENSE_COMPANION.md` §2.1. The points load-bearing **for this
dossier's positioning**, verified first-hand this session:

- **Eureka's reflection is NOT scalar-only.** It serializes "the scalar values of all reward components and the task
  fitness function at intermediate policy checkpoints" — per-component **max/mean/min over training**. The
  scalar-fitness-only ablation costs **28.6%** normalized score. **Consequence for novelty (critical):** the delta to
  Eureka cannot be sold as "scalar → rich feedback." It must be sold as **"point statistics of reward *components* →
  empirical distribution of realized *outcomes* (return tail/quantile structure)."** This is the most important single
  sentence in the whole positioning; get it precise (it is already correctly framed in `DEEP_H2.md` §2 and in
  `DEEP_FRAMING_discipline.md` §2 — keep the wording aligned).
- **Three finance-forced adaptations (the defensible deltas):** (i) fitness = held-out financial metric decoupled from
  the candidate reward (Eureka's fitness is the simulator's ground-truth task score); (ii) feedback = realized-return
  distribution (Eureka's is reward-component statistics); (iii) environment = point-in-time market → contamination
  defense Eureka never needed.
- **Eureka's H1 protocol is *weaker* than this work's.** Eureka compares against **one** human reward per task with no
  multiple-testing correction; this work compares against the **max of four** hand-rewards on a sealed test leg
  (`DEEP_H1.md` §2.1). State this — it is a citable defensibility point that the H1 bar here is harder than the field's
  headline beat-the-human result.

## A.4 The recent reward-as-code wave (2024–2026): LEARN-Opt, CARD, URDP, PROF, "When LLM Reward Design Fails"

All control/robotics; **none distributional**; each is a one-line cite-and-distinguish. Verified this session.

- **LEARN-Opt** (Cardenoso & Caarls, arXiv:2511.19355, Nov 2025) [read first-hand]. The newest Eureka successor:
  fully autonomous, model-agnostic, **self-derives its own evaluation metric** from the text task description (no
  preliminary metric, no env source code). Signal = self-derived **scalar**. **The load-bearing finding for THIS work:**
  *"automated reward design is a high-variance problem, where the average-case candidate fails, requiring a multi-run
  approach to find the best candidates."* This is an **independent, same-year validation of the dissertation's
  methodological core** — the matched-budget, multi-seed, selection-aware inference (`DEEP_H2.md`; `DEEP_H4.md`) is the
  correct response to exactly the variance LEARN-Opt documents. Cite it as a methodological ally for "why multi-run +
  selection-aware statistics," not a competitor.
- **CARD** (Sun et al., arXiv:2410.14660; **Knowledge-Based Systems 2025, Vol 326, Art 114065** ⚠ confirm DOI
  10.1016/j.knosys.2025.114065 before citing the venue). Coder+Evaluator reward-code loop; feedback = **Trajectory
  Preference Evaluation (TPE)** — *preference*, not distribution; evaluates without running RL every iteration. Distinguish
  on object (preference) and domain (control).
- **URDP** (Yang et al., arXiv:2507.02256, Jul 2025). Uncertainty-aware reward design; "uncertainty" = **LLM
  self-consistency** across samples (epistemic), used to prune redundant candidates + steer Bayesian optimization of
  reward intensities. ⚠ **Correction banked:** an earlier project summary falsely claimed URDP "feeds CVaR to the LLM" —
  **verified FALSE; the word CVaR does not appear**. URDP is the closest *mechanism* (uncertainty → reward design) but it
  is epistemic-uncertainty-over-LLM-outputs, not a realized-return tail. Do not repeat the CVaR phrasing.
- **PROF** (arXiv:2511.13765, Nov 2025 % VERIFY). LLM reward-code + offline imitation; feedback = **Reward Preference
  Ranking + TextGrad** (textual-gradient suggestions). Another preference-not-distribution data point; D4RL MuJoCo domain.
- **"When LLM Reward Design Fails: Diagnostic-Driven Refinement for Sparse Structured RL"** (arXiv:2605.28918, 2026
  % VERIFY authors). Reframes reward design as **debugging not one-shot**; failure taxonomy {reward flooding,
  semantic/API misunderstanding, weak shaping}; finds LLM-reward variance dominates with wide bootstrap intervals.
  Methodological ally for the forensics chapter and the variance-decomposition appendix — cite alongside LEARN-Opt as the
  "LLM rewards are high-variance, so the inference must be variance-aware" evidence base.

## A.5 The nearest neighbours on the distribution / finance axes (the two most important distinctions)

These are the two prior works that touch *one* of the dissertation's two axes; naming the precise distinction is what
secures the novelty claim.

- **Decision-Language Model (Behari, Zhang, Zhao, et al. — arXiv:2402.14807, NeurIPS 2024)** [read first-hand]. The
  **only** prior case of an LLM (1) proposing reward functions **as code** and (2) iterating on them via **simulation
  feedback** *and* being shown a **distribution** — for restless multi-armed bandits in public health (ARMMAN maternal
  care). **The distinction is the *object* of the distribution:** DLM's distribution is the spread of **population groups
  across states** in a resource-allocation problem; this work's is what is predicted about **portfolio returns**,
  specifically the lower tail. The settings share the reward-as-code-plus-simulation-feedback loop but the *signal* is a
  different kind of distribution over a different kind of object. This is the single most important comparison in the
  dissertation and the one to state most carefully: *"DLM shows an LLM can author reward code refined by grounded
  simulation; we differ in feeding a realized-return tail distribution as the refinement signal, in a risk-sensitive
  financial domain rather than population resource allocation."*
- **Qu et al., "LLM-Enhanced Self-Evolving RL for E-Commerce Payment-Fraud Detection" (arXiv:2509.18719, ACL 2025
  Industry)** [read first-hand]. The **only** reward-*code* evolution in a finance-*adjacent* domain: LLMs iteratively
  enhance the reward function of a multi-step fraud-detection MDP. **The distinction is domain + object:** fraud
  detection (a classification/alerting MDP), not portfolio allocation; reward refined on detection-accuracy/business
  metrics, no return distribution. This is exactly why the novelty claim is worded **"first for a *trading/portfolio
  agent*," not "first in finance."** Qu protects you from the over-claim and must be cited as the reason for the careful
  wording.

## A.6 Surveys — and the useful absence

There is **no dedicated survey of "LLM reward-as-code design."** The topic appears only as one branch of broader
LLM-for-RL surveys: **"Survey on LLM-Enhanced Reinforcement Learning: Concept, Taxonomy, and Methods"**
(arXiv:2404.00282, 2024 % VERIFY internal taxonomy — PDF was unparseable, title/scope from metadata) and **"RL Meets
LLMs: A Survey across the LLM Lifecycle"** (arXiv:2509.16679, 2025 % VERIFY depth). ⚠ Do **not** miscite the *reward-model*
surveys (arXiv:2504.12328; 2505.02686 "Sailing by the Stars") — they are about reward **models for LLM alignment**, a
different object. The absence of a dedicated survey is itself a positioning asset: it lets the dissertation claim the
sub-area is nascent and that its taxonomy-of-feedback-signals (§A.0) is a small contribution to organizing it.

## A.7 Gaps a top (90–100) dissertation would address — Part A

1. **The "distribution vs Eureka's component statistics" delta must be airtight (CRITICAL).** Without the precise
   wording, the easiest referee kill is "this is Eureka with a different print statement." → §4.1; cheap, pure framing.
2. **Attribution within the tail vector.** A positive H2 says "tail-shape information helps," not "CVaR-5% specifically
   helps." Disclosed in `DEEP_H2.md` §2.2 as an interpretability limit; a field-ablation is out of frozen scope and
   should be named as future work, not attempted.
3. **No human-feedback arm.** Text2Reward/L2R/REvolve/ICPL refine on human/preference feedback; this work has no such
   arm. That is a deliberate scope choice (the contribution is the *automated quantitative* channel), but the lit review
   should state that the human-feedback branch of reward-as-code is a *different* lineage it does not contest.
4. **External validity is single-instance** (one market, one universe, one period). Named in L18; scope the abstract to
   *mechanism + method*, not a universal claim about reward design.

---
---

# PART B — LLM-AS-OPTIMIZER / PROGRAM SEARCH

This literature is where the dissertation's **H4** lives (LLM reward-designer vs uninformed search at matched budget),
and where the most disciplined framing is required, because the OPRO-critique literature is precisely about *not*
over-claiming that an LLM is a superior optimizer.

## B.1 OPRO — "Large Language Models as Optimizers" (Yang, Wang, Lu, et al., Google DeepMind — arXiv:2309.03409, ICLR 2024) [read first-hand]

**SOTA / what it does.** Optimization-by-Prompting: the meta-prompt holds previously generated solutions **paired with
their scalar objective values**, sorted; the LLM proposes new solutions; they are scored and appended. Demonstrated on
toy linear regression / TSP and, mainly, prompt optimization (GSM8K +up to 8%, Big-Bench Hard up to +50%). **Signal =
scalar objective values.**

**What THIS dissertation adds / how it relates.** OPRO is the canonical "LLM iteratively proposes, sees the score,
proposes again" pattern — the abstract skeleton the Eureka reward loop instantiates. The dissertation's contribution is
orthogonal to OPRO's *mechanism*: it is about **what the LLM sees between rounds**. Where OPRO (and every descendant)
shows the LLM a **scalar value**, this work shows it a **distribution**. Cite OPRO as the ancestor of the iterate-on-
feedback paradigm and as the canonical instance of the **scalar-feedback** convention the dissertation breaks from.

## B.2 "Revisiting OPRO: The Limitations of Small-Scale LLMs as Optimizers" (Zhang, Yuan, Avestimehr — arXiv:2405.10276, ACL Findings 2024) [verified this session]

**The critique.** With small optimizer models (LLaMa-2, Mistral-7B), OPRO **underperforms even plain Zero-shot-CoT /
Few-shot-CoT baselines**; "limited inference capabilities constrain optimization ability." Recommendation: for weaker
models, prefer **direct, well-specified instruction baselines** over automated optimization. A second, corroborated
limitation (from OPRO's own framing): the optimality gap **widens as problem size grows** (it is not meant to beat
gradient/specialized solvers).

**Why this matters enormously for the dissertation's H4 framing.** This is the literature's own warning that
**"LLM-as-optimizer" is capability-contingent and not a universal win.** The dissertation's H4 design *already* respects
this (`DEEP_H4.md` §1): it does **not** claim "the LLM is a better black-box optimizer than Bayesian optimization." It
claims (H4a) better *proposal quality* against random-search-over-code at comparable expressive power, and (H4b) that an
**open-ended reward language** beats tuning a fixed parametric one. **Strongest framing move:** cite Revisiting-OPRO as
the reason the H4 claim is *deliberately scoped narrowly* — "we do not assert general optimizer superiority (which the
literature shows is model- and scale-dependent); we test a specific, matched-budget question about reward-search
quality and reward-language richness." This converts a potential vulnerability (the procedure-vs-richness confound,
`DEEP_H4.md` §1.1) into a demonstration of methodological maturity.

## B.3 FunSearch (Romera-Paredes et al. — *Nature* 625, 468–475, 2024; DOI 10.1038/s41586-023-06924-6) [read first-hand]

**SOTA / what it does.** Pairs a frozen pretrained LLM with an **automated evaluator**; evolves a small "priority"
function inside a fixed program skeleton using **island-based evolution** + **best-shot prompting** (feeds the best
prior *programs* back into the prompt). Highly parallel/asynchronous. Beat SOTA on the cap-set problem and found better
online-bin-packing heuristics. **Signal = scalar score from the `evaluate` function; the LLM sees prior programs (and
their scores), not raw evaluation data.**

**What THIS dissertation adds / how it relates.** FunSearch is the canonical "LLM + evaluator evolves a program"
method, and the dissertation's reward-code search is in this family (it is what Eureka specializes). FunSearch's key
design lessons are *adopted* (evolve code not solutions; best-shot prompting; an archive of candidates). The
contribution is again the **signal**: FunSearch collapses the evaluator to a scalar score; this work passes a
distribution. **One precise distinction to pre-empt a referee:** FunSearch's "evaluate" can be multi-objective, but a
vector of summary scalars is *not* an empirical return distribution. Make that explicit (§B.6). Also use FunSearch's own
discipline — it *isolates the contribution of the search method from the search space* — as the citation for why H4
must control space-vs-procedure (`DEEP_H4.md` §1).

## B.4 EvoPrompt, ELM, EvoLLM, ShinkaEvolve, Darwin-Gödel-Machine, TextGrad, Trace/OptoPrime [verified this session]

The broad LLM-evolutionary-search lineage. Each is a one-line cite for the related-work "LLM-as-optimizer" paragraph;
the through-line is **the signal**, and **none uses a distribution**:

| System | arXiv / venue | Mechanism (one line) | Feedback signal |
|---|---|---|---|
| **EvoPrompt** | 2309.08532, ICLR 2024 | GA/DE over a population of *prompts*, EA operators realized by LLM prompting | scalar dev-set accuracy |
| **ELM** (Evolution through Large Models) | 2206.08896, 2022 | LLM as intelligent mutation operator inside MAP-Elites | scalar fitness + QD descriptor |
| **EvoLLM** | 2402.18381, Sakana 2024 | LLM as zero-shot Evolution Strategy (sort population, propose improved mean) | scalar fitness of population |
| **ShinkaEvolve** | 2509.19349, ICLR 2026 % VERIFY | sample-efficient AlphaEvolve-style program evolution | scalar fitness + code-novelty |
| **Darwin-Gödel-Machine** | 2505.22954, ICLR 2026 % VERIFY | agents rewrite own code, empirically validated | scalar benchmark scores |
| **TextGrad** | 2406.07496, *Nature* 2025 % VERIFY | backprop natural-language "textual gradients" through LLM-call graph | NL critique text |
| **Trace / OptoPrime** | 2406.16218, NeurIPS 2024 | OPTO: optimizer consumes the workflow's *execution trace* | execution-trace text + feedback |

The axis these span is **scalar → execution-trace text → NL critique → quality-diversity descriptor**. A realized-
outcome *distribution* as the optimization signal is absent from all of them. TextGrad and Trace are the closest to
"richer than scalar," but their richness is *prose/program-structure*, not a *statistical distribution of outcomes* —
a distinction the dissertation should state once, crisply.

## B.5 AlphaEvolve + OpenEvolve (the 2025–2026 frontier, and the implementation precedent for richer feedback)

- **AlphaEvolve** (Novikov, Vũ, et al., Google DeepMind — arXiv:2506.13131, 2025) [verified this session]. An ensemble
  of Gemini models proposes diffs to whole code files (`EVOLVE-BLOCK` regions); an **evolutionary database + a cascade of
  automated evaluators** selects parents. Achievements: a 4×4 complex-matrix-multiplication algorithm in 48 scalar
  multiplications (beating Strassen's 49); ~0.7% fleet-wide compute recovered via a Borg scheduling heuristic; ~23%
  FlashAttention speedup. **Signal = evaluator feedback (scalar / multi-metric).** The abstract is explicit only that it
  "continuously receiv[es] feedback from one or more evaluators"; it is scalar/vector scores, **not a distribution**.
- **OpenEvolve** (codelion; Apache-2.0) [verified this session]. Faithful AlphaEvolve re-implementation. **Its
  `EvaluationResult` carries `metrics` (numeric, for selection) AND `artifacts` (a free-form dict: `stderr`, `stdout`,
  `profiling_data`, `llm_feedback`, `build_warnings`) that are injected into the next-generation prompt.** This is the
  **implementation precedent** for richer-than-scalar feedback flowing back to the LLM — and it is the honest reference
  point for the dissertation's feedback block. **Crucial framing consequence:** the dissertation's contribution is **not
  the channel** (a richer-feedback side-channel already exists in OpenEvolve) — it is **what is put in the channel** (a
  realized-return tail distribution as the optimization signal for a risk-sensitive agent) and the **controlled,
  pre-registered test** of whether that specific content beats a scalar. State this precisely or a referee who knows
  OpenEvolve will say "the artifacts side-channel already does richer feedback." (This is the program-search analogue of
  the GEPA point in §B.7.)

## B.6 The one distinction that must be airtight: "multi-metric vector ≠ distribution"

AlphaEvolve, OpenEvolve, and FunSearch can all carry **vectors of summary scalars** (multi-objective). A referee will
ask whether "multi-metric is already richer than scalar, so where is the novelty?" The precise, defensible answer:

> A vector of summary scalars (Sharpe, max-drawdown, turnover) is a fixed handful of point statistics. The distributional
> feedback here is a **coherent-risk-principled descriptor of the lower-tail of the realized-return distribution** — a
> CVaR profile at multiple levels (which, by Kusuoka's representation, spans the law-invariant coherent risk measures),
> plus left-tail mass and robust skew. The contribution is not "more numbers"; it is **the kind of object** (a tail/
> quantile structure with a theoretical basis) and the **controlled test** that this object, specifically, changes what
> the reward designer writes. (`DEEP_H2.md` §2.1; `DEEP_FRAMING_discipline.md` §2.3.)

This is also why the **construct retitle to "multi-level tail-risk feedback"** matters: it concedes the object is *not*
"the full distribution" (no mode, no right tail, no vol-of-vol) while defending the specific six scalars as principled.

## B.7 GEPA — the strongest external ally (Agrawal et al. — arXiv:2507.19457, **ICLR 2026 Oral**) [verified this session]

**What it is.** Genetic-Pareto optimizer for compound AI systems; mutates prompts via **natural-language reflection over
rollout traces**, maintains a Pareto front; beats GRPO by ~10% avg (up to 20%) with up to **35× fewer rollouts**.

**Why it is the key methodological anchor for H2.** GEPA's thesis is a near-exact, independently-validated statement of
the dissertation's premise, with a quotable sentence: *"the interpretable nature of language often provides a much
richer learning medium for LLMs, compared to policy gradients derived from sparse, scalar rewards."* The framing —
**don't collapse rollouts into a single numeric value; use the full signal** — is the dissertation's H2 hypothesis at
the prompt-optimization level. **But it is a *neighbour*, not a baseline to beat:** GEPA optimizes prompts (rich *text*
feedback), not portfolio reward code (rich *distributional* feedback). Cite it as the cross-domain endorsement that
"rich signal > scalar collapse," borrow its Pareto-archive and rich-trace framing as design references, and state the
distinction (text-trace vs return-distribution; prompt vs reward code). This is the most valuable citation surfaced for
positioning H2 positively.

## B.8 H4 in this literature — what it legitimately licenses (from `DEEP_H4.md`, first-hand)

The dissertation operationalizes the LLM-as-optimizer comparison as **H4**: LLM reward-designer vs (a) random-search-
over-code (`src/search/random_search.py`, a 3-term grammar) and (b) Bayesian-optimization-over-template
(`src/search/bayes_opt.py`, **GP-EI**, a 6-term linear family). Two governance facts the write-up must honor:

- ⚠ **The BO arm is GP-EI, not TPE, and there is no Optuna** (`DEEP_H4.md` §0.1). The config label `bayesopt_tpe` is a
  misnomer; cite **Snoek et al. 2012** (GP-EI Bayesian optimization), **not** Bergstra 2011 (TPE). A method mislabel is
  trivially caught.
- **The space-vs-procedure confound** (`DEEP_H4.md` §1): the LLM searches a strictly richer space than either baseline,
  so a positive H4 supports "(richer language ∨ smarter procedure)" but cannot separate them. **Scope the claim:** H4a =
  proposal quality at comparable expressive power; H4b = value of an open-ended reward language vs a tuned parametric
  one. **Do not claim "the LLM is a better optimizer than BO."** Revisiting-OPRO (§B.2) is the citation that makes this
  narrow scoping look like rigor, not retreat.

## B.9 Gaps a top dissertation would address — Part B

1. **The "vector ≠ distribution" distinction (CRITICAL, framing).** Pre-empt the multi-metric objection explicitly
   (§B.6). Cheap, high-value.
2. **The TPE→GP-EI label fix (CRITICAL, integrity).** ⚠ Fix every `bayesopt_tpe`/"Optuna"/"TPE" string and cite Snoek
   2012. A factual method error in a no-viva PDF is a pure-downside credibility hit. (`DEEP_H4.md` §0.1.)
2.b **The H4 like-for-like grammar gap.** Random-search's 3-term grammar is poorer than the LLM's free-form space, so
   even H4a is partly a richness comparison until the grammar is widened (`DEEP_H4.md` §2). Either widen the random
   grammar pre-freeze (engineering) **or** scope the H4a claim to "comparable risk-aware grammar" and disclose. The
   strict, conservative move is to **scope, not re-engineer** (see §5).
3. **No space-controlled ablation.** Eureka/FunSearch isolate procedure from space; H4 has no "random sampler over the
   LLM's free-form grammar" arm. This is out of frozen scope — name it as the clean future-work experiment that would
   separate (C-procedure) from (C-richness).
4. **OPRO-critique citation is currently implicit.** The H4 narrow scoping is *de facto* aligned with Revisiting-OPRO
   but the paper is not yet in the cite plan — adding it makes the scoping principled rather than ad hoc (§5).

---
---

# PART C — REWARD-SHAPING / SPECIFICATION CLASSICS

These ground the *legitimacy* of "reward as a designed/searched object" and the *failure modes* the dissertation must
inspect. All read first-hand this session.

## C.1 Ng–Harada–Russell, "Policy invariance under reward transformations" (ICML 1999) [read first-hand]

**What it is.** The theory of **potential-based reward shaping**: which reward transformations preserve the optimal
policy (adding `γΦ(s') − Φ(s)` for any potential Φ leaves the optimal policy invariant). The foundational result on
admissible reward modification.

**How THIS dissertation uses it.** It is the principle the **reward contract** respects (`src/reward/contract.py`): the
LLM may shape, but shaping that changes the optimal policy is the thing to be aware of. Cite NHR as the theoretical
backstop for "the reward family is a shaping space, and we know what shaping does." It also frames a subtle point the
dissertation can make: because finance has no ground-truth optimal policy, NHR-style invariance is *aspirational* here —
the LLM is genuinely *specifying* the objective, not merely shaping a known one, which is part of why the comparative
(channel-vs-channel) framing is the right one.

## C.2 Singh, Lewis & Barto, "Where Do Rewards Come From?" (2009) + the Optimal Reward Problem (Sorg/Singh 2010–2011) [read first-hand]

**What it is.** The pre-LLM formalization that **reward is something to be designed/searched**: an *optimal reward
function* is defined relative to a **fitness function and a distribution of environments**, and — critically — *"the
precise form of the optimal reward functions need not bear a direct relationship to the fitness function, but may
nonetheless confer significant advantages over rewards based only on fitness."* In their experiments rewards are
**discovered by automated search, not crafted by hand.**

**How THIS dissertation uses it — and why it is a powerful framing anchor.** This is the **conceptual root** that places
the contribution in a lineage rather than a vacuum: the idea that a *searched* reward can beat a *fitness-derived* one is
exactly the dissertation's premise, two decades earlier and domain-general. It also *predicts and legitimizes* the
decoupling of fitness from the candidate reward (`src/selection/fitness.py`): Singh's framework formally separates the
**fitness** (what you ultimately care about — here, validation Deflated Sharpe) from the **reward** (what the agent
optimizes — the LLM's code). Lead the introduction with Singh: *"the question 'can a searched reward beat a hand-
specified one?' is Singh's Optimal Reward Problem; we ask it with an LLM as the search operator, a financial fitness,
and a distributional feedback channel."* This single citation converts the work from "an Eureka application" to "a
contemporary instance of a foundational RL question."

## C.3 Reward hacking / Goodhart: Skalse et al. (NeurIPS 2022); Pan et al. (ICLR 2022); Amodei et al. (2016) [Skalse read first-hand]

**What it is.** Skalse gives the first **formal definition of reward hacking** (optimizing a proxy `R̃` degrades the true
`R`) and the "unhackability" conditions (showing they are very restrictive). Pan characterizes reward *misspecification*
empirically; Amodei frames it as a concrete AI-safety problem. Together: **what goes wrong when an agent maximizes a
designed reward.**

**How THIS dissertation uses it.** The whole project is "LLM writes reward → SAC maximizes it," so reward hacking is the
**failure mode inspected in the forensics phase** (Phase 4.C). The reward-hacking literature is also the reason the
fitness is **decoupled** from the fed-back signal and the feedback is **measured off-critic** (`DEEP_H2.md` §1.3 confound
C-c): if the LLM could tune the reward to inflate the *fed-back* statistic, that would be reward-hacking-into-feedback —
the decoupling structurally prevents it. Cite Skalse/Pan as the named risk and the design's response to it; note the
finance-specific analogue (alpha decay / factor crowding as a Goodhart effect) is *your* bridge, stated "to our
knowledge" (`REFERENCES.md`).

## C.4 Hadfield-Menell et al., "Inverse Reward Design" (NeurIPS 2017) [read first-hand]

**What it is.** Treats a designed reward as **an imperfect *observation* about what the designer wants**, to be
interpreted in the context (training MDP) in which it was designed; infers the true objective and **plans risk-averse
behavior in test MDPs** to mitigate misspecification and reward hacking.

**How THIS dissertation uses it — the strongest "reward-design priors as object of study" anchor.** Two precise hooks:
(1) IRD's frame — *the designed reward is a noisy proxy for intent, sensitive to the design context* — is the best
citation for treating the **LLM's reward-design priors as the object of study** (`DEEP_H2.md`; L-register) rather than a
nuisance: the dissertation is, in effect, asking *what objective does the LLM infer about a financial agent, and does a
distributional signal change that inference?* (2) IRD explicitly couples misspecification to **risk-averse behavior under
distribution shift** — a direct conceptual bridge to the dissertation's risk-sensitive, tail-aware setting. Cite IRD to
frame the contamination/over-fitting concern (the LLM's reward priors are tuned to *remembered* regimes — a design-
context dependence exactly of IRD's kind) and to motivate why a *tail*-shaped feedback signal is the natural lever in a
risk-sensitive domain.

## C.5 Inverse RL framing (Ng & Russell 2000; Ziebart MaxEnt 2008; Abbeel-Ng 2004) [read first-hand]

**What it is.** Learn the reward from expert demonstrations/preferences. **How it is used:** the *contrast* lineage —
Text2Reward and this work both define themselves *against* IRL (IRL is data-hungry, needs demonstrations, yields an
uninterpretable neural reward; reward-as-code is data-free and interpretable). One paragraph in the lit review: IRL
*learns* a reward from data; this work has an LLM *write* a reward as code, refined by a distributional signal — no
demonstrations, an interpretable symbolic object.

## C.6 Gaps a top dissertation would address — Part C

1. **State the NHR invariance caveat honestly:** in a ground-truth-free domain, policy-invariance is not verifiable, so
   the LLM is *specifying* not merely *shaping*. This is a strength of the comparative framing, not a weakness — say so.
2. **The reward-hacking inspection must be shown, not asserted** (Phase 4.C). A top dissertation exhibits at least one
   inspected reward and what it does/does not exploit. Already planned; ensure it lands in the PDF.
3. **The IRD "reward-priors-as-object" framing is currently under-exploited.** It is the most elegant way to frame the
   contamination concern as a research *question* rather than a flaw — promote it from a footnote to a paragraph (§5).

---
---

# PART 4 — THE NOVELTY MAP AND THE STRONGEST OVERALL FRAMING

## 4.1 The novelty map (what is genuinely new, stated at the right altitude)

| Claim | Status | The precise, defensible wording |
|---|---|---|
| **N1 (headline) — distributional feedback to an LLM reward designer** | **Genuinely novel** (empty on both axes; mid-2026 sweep confirms) | "We feed the LLM reward-designer the **empirical lower-tail distribution of realized returns** (a coherent-risk-principled CVaR profile + tail mass + robust skew), where all prior reward designers feed scalar fitness, per-component scalar statistics, preference, NL critique, or execution traces. To our knowledge no prior system, in any domain, feeds a realized-**return** distribution to a reward-**code** designer." |
| **N1 delta vs Eureka (the critical sub-claim)** | **Narrow but real** | "Eureka already feeds per-component scalar *time-series*; our delta is the **distribution of realized *outcomes*** (return tail/quantile structure), not point statistics of reward *components*." |
| **N2 — reward-code synthesis for a trading/portfolio agent** | **Novel with careful wording** (Qu = fraud; DLM = public health) | "First Eureka-style reward-**code** synthesis for a **trading/portfolio** RL agent — *not* first in finance (Qu 2025 does fraud; DLM 2024 does public-health resource allocation)." |
| **N3 — contamination-aware evaluation of reward design** | **Adopted method, novel application** | "We adopt structural blinding + cutoff stratification (family G) and articulate why reward-design contamination differs from forecasting contamination." |
| **N4 (implicit) — a feedback-signal taxonomy for LLM reward design** | **Minor organizing contribution** | "We organize the reward-as-code literature by *what signal feeds the designer* (§A.0), locating the empty cell." |

## 4.2 The single strongest framing sentence (for the abstract / introduction)

> *"Singh's Optimal Reward Problem asks whether a searched reward can beat a fitness-derived one; Eureka answered yes in
> robotics with an LLM search operator fed scalar reward-component statistics. We ask the same question in a
> risk-sensitive financial domain, with the LLM fed not point statistics but the **empirical lower-tail distribution of
> realized returns** — and we answer it as a pre-registered, matched-compute, comparative test of the feedback channel
> itself, holding the agent fixed."*

This sentence (i) roots the work in a foundational question (Singh, not just Eureka), (ii) states the exact, narrow
delta to Eureka, (iii) names the domain shift, (iv) foregrounds the *comparative-inference* rigor that — given no viva
and a PDF-only grade — is the dominant grading lever, and (v) is governed by the no-SOTA / construct-retitle disciplines.

## 4.3 The strongest defensible positioning, per literature

- **vs LLM reward design (A):** "We retain reward-as-code; we replace human/preference/scalar feedback with an
  automated, coherent-risk-principled distributional channel, in finance, tested comparatively." Allies: LEARN-Opt +
  "When LLM Reward Design Fails" (variance ⇒ our multi-run inference is the right response); GEPA (rich-signal thesis).
- **vs LLM-as-optimizer (B):** "We do **not** claim general optimizer superiority — the literature (Revisiting-OPRO)
  shows that is capability-contingent. We test a narrow, matched-budget question about reward-search quality and
  reward-language richness (H4), and a feedback-channel question (H2). The novelty is the **content** of the feedback
  (a distribution), not a new channel (OpenEvolve's artifacts side-channel already carries rich feedback)."
- **vs reward-shaping classics (C):** "Reward is a designed/searched object (Singh; Sorg); shaping has known invariances
  (NHR); designed rewards are noisy proxies for intent (IRD) prone to hacking (Skalse/Pan). We study the LLM's
  reward-design *priors* as the object, with a distributional lever, and inspect for hacking."

---
---

# PART 5 — PRIORITIZED IMPLEMENTABLE IMPROVEMENTS (conservative; the design is freeze-ready + verified-green)

**Posture.** The design is freeze-ready. Per CLAUDE.md prime directives, anything touching a frozen artifact
(PREREGISTRATION, configs, the inference family) requires a dated amendment, not a silent edit, and **scope discipline
says prefer framing/scoping over new engineering.** The verdicts below are deliberately conservative: almost everything
high-value here is **pure write-up / citation / labelling** with near-zero pre-freeze risk; the few code-touching items
are explicitly marked **scope-not-engineer** unless trivially safe.

### Tier A — DO (pure framing/integrity; zero or near-zero pre-freeze risk; high grade-ROI)

1. **Bank the precise Eureka delta wording** ("distribution of realized *outcomes*" vs "point statistics of reward
   *components*"). **Grade-ROI: very high** (closes the single easiest referee kill). **Risk: none** (prose). **Verdict:
   DO.** Source: §A.3, §4.1; already correct in `DEEP_H2.md` — propagate to the lit-review + abstract.
2. **Add the "vector ≠ distribution" pre-emption paragraph** (multi-metric AlphaEvolve/FunSearch is still scalars; ours
   is a coherent-risk tail object). **Grade-ROI: high.** **Risk: none.** **Verdict: DO.** Source §B.6.
3. **⚠ Fix the BO method label everywhere: GP-EI, not TPE/Optuna; cite Snoek 2012.** **Grade-ROI: high** (a factual
   method error in a no-viva PDF is pure downside). **Risk: none** if done as a config-comment + prose fix (the wired
   code is already GP-EI; no behavior change). **Verdict: DO.** Source `DEEP_H4.md` §0.1.
4. **Add Revisiting-OPRO (2405.10276) to the cite plan as the principled basis for H4's narrow scoping.** **Grade-ROI:
   high** (turns the procedure-vs-richness confound from a vulnerability into demonstrated rigor). **Risk: none.**
   **Verdict: DO.** Source §B.2, §B.8.
5. **Promote the Singh/Optimal-Reward-Problem and IRD framings** from background to headline framing (the abstract
   sentence in §4.2; the "reward-priors-as-object" paragraph). **Grade-ROI: high** (reframes the work as a foundational
   question, not an Eureka port — exactly the altitude a Distinction wants). **Risk: none.** **Verdict: DO.**
6. **Cite OpenEvolve's artifacts side-channel as the implementation precedent and state the novelty is the *content*,
   not the channel.** **Grade-ROI: medium-high** (pre-empts the "rich-feedback channel already exists" objection).
   **Risk: none** (% VERIFY the repo license/feature line). **Verdict: DO.** Source §B.5.
7. **Cite GEPA (ICLR 2026 Oral) as the rich-signal-vs-scalar ally with its exact quotable sentence.** **Grade-ROI:
   medium-high.** **Risk: none** (verified this session). **Verdict: DO.** Source §B.7.
8. **Add the feedback-signal taxonomy table (§A.0) to the lit review.** **Grade-ROI: medium** (makes the empty cell
   visually undeniable and is a small organizing contribution). **Risk: none.** **Verdict: DO.**
9. **⚠ Confirm CARD's KBS venue/DOI and drop the false URDP-CVaR phrasing** in any draft text. **Grade-ROI: medium**
   (citation integrity). **Risk: none.** **Verdict: DO.** Source §A.4.

### Tier B — CONSIDER (low-cost, contingent; small but real decisions)

10. **Scope (do not re-engineer) the H4a claim** to "comparable risk-aware code grammar" and disclose that the random
    grammar is narrower than the LLM's free-form space, OR widen the random grammar pre-freeze. **Grade-ROI: medium.**
    **Pre-freeze risk: LOW for the scope-only path; MODERATE for the re-engineer path** (changing `random_search.py`
    grammar pre-freeze touches a frozen comparator and risks re-running). **Conservative verdict: SCOPE, don't engineer**
    — disclose the grammar asymmetry and narrow the H4a wording; list "widen the grammar / add a random-sampler-over-LLM-
    grammar arm" as the clean future-work experiment that separates procedure from richness. Source `DEEP_H4.md` §1–§2.
11. **Name the space-controlled ablation as future work** (a random sampler over the LLM's free-form grammar would
    isolate C-procedure from C-richness). **Grade-ROI: medium** (shows you know the FunSearch/Eureka discipline).
    **Risk: none** (it is explicitly future work). **Verdict: DO as future-work text.** Source §B.3, §B.9.
12. **One sentence distinguishing TextGrad/Trace ("rich text/trace, not a distribution") from this work.** **Grade-ROI:
    low-medium.** **Risk: none.** **Verdict: CONSIDER** (nice-to-have precision in related work). Source §B.4.

### Tier C — DO NOT (out of frozen scope; the urge to add is the signal to stop)

13. **A human-feedback / preference arm** (to match Text2Reward/CARD/PROF). **Verdict: DO NOT** — it changes the
    contribution from "automated quantitative channel" to a different study, violates scope discipline, and needs a
    campaign re-run. Name the human-feedback lineage as a *different* branch this work does not contest. Source §A.7.
14. **A per-field tail-vector ablation** (drop one CVaR level at a time). **Verdict: DO NOT** — not in the frozen design;
    name as future work; disclose the bundle-level attribution limit instead. Source `DEEP_H2.md` §2.2.
15. **Re-running H4b as real Optuna-TPE.** **Verdict: DO NOT** — GP-EI is a legitimate, citable BO; fixing the *label*
    (Tier A item 3) is the correct, zero-risk move. Re-engineering to TPE pre-freeze is unnecessary scope. Source
    `DEEP_H4.md` §0.1.
16. **Any benchmark/SOTA comparison against the FinRL band as a ranking.** **Verdict: DO NOT** — governed by the
    no-SOTA-claim discipline; the band is a plausibility ribbon only. Source `DEEP_FRAMING_discipline.md` §1.

**Net.** The strongest-grade levers here are almost entirely **framing, citation, and labelling** (Tier A), all
near-zero pre-freeze risk and directly aligned with the PDF-only / no-viva grading reality where write-up precision and
citation integrity dominate. The one genuine design temptation (widen the H4 grammar) is best handled by **scoping the
claim, not re-engineering a frozen comparator**.

---
---

# PART 6 — SOURCES (verified this session)

**Read first-hand from the local cache (`D:\tmp\littxt\…`):** Text2Reward (2309.11489); Language-to-Rewards
(2306.08647); OPRO (2309.03409); FunSearch (Nature 2024); Decision-Language-Model (2402.14807); Qu fraud
(2509.18719); LEARN-Opt (2511.19355); Ng-Harada-Russell (1999); Singh "Where Do Rewards Come From?" (2009);
Hadfield-Menell IRD (2017); Skalse reward hacking (2209.13085); IRL-Ng-Russell (2000); Eureka (2310.12931, also
its own dossier).

**Verified via web this session:**
- Revisiting OPRO — https://arxiv.org/abs/2405.10276 · https://aclanthology.org/2024.findings-acl.100/ (ACL Findings
  2024; small-scale LLMs fail as optimizers; recommend direct-instruction baselines).
- AlphaEvolve — https://arxiv.org/abs/2506.13131 (Novikov, Vũ et al., DeepMind 2025; evaluator-cascade feedback, scalar/
  vector — not a distribution).
- FunSearch (Nature) — https://www.nature.com/articles/s41586-023-06924-6 (DOI 10.1038/s41586-023-06924-6).
- GEPA — https://arxiv.org/abs/2507.19457 (ICLR 2026 Oral; "richer learning medium than … sparse, scalar rewards").
- OpenEvolve — https://github.com/codelion/openevolve (Apache-2.0; `EvaluationResult` metrics + artifacts side-channel).
- Reward-as-code wave: CARD https://arxiv.org/abs/2410.14660 (KBS 2025 ⚠ confirm DOI); URDP
  https://arxiv.org/abs/2507.02256 (⚠ no CVaR); PROF https://arxiv.org/abs/2511.13765; "When LLM Reward Design Fails"
  https://arxiv.org/abs/2605.28918.
- LLM-evolutionary lineage: EvoPrompt 2309.08532; ELM 2206.08896; EvoLLM 2402.18381; ShinkaEvolve 2509.19349; Darwin-
  Gödel-Machine 2505.22954; TextGrad 2406.07496; Trace/OptoPrime 2406.16218.
- Surveys (no dedicated reward-as-code survey): 2404.00282; 2509.16679 (% VERIFY depth). Do NOT conflate with reward-
  *model* surveys 2504.12328 / 2505.02686.

**Two corrections banked this session (⚠):** (1) **URDP does not use CVaR** — its "uncertainty" is LLM self-consistency;
the earlier project summary was wrong. (2) **The BO arm is GP-EI, not TPE/Optuna** — fix every label and cite Snoek
2012.

**Internal first-hand sources:** `00_planning/LITERATURE_AND_DEFENSE_COMPANION.md`; `docs/DEEP_H1.md`, `docs/DEEP_H2.md`,
`docs/DEEP_H4.md`, `docs/DEEP_FRAMING_discipline.md`; `RELATED_WORK_WATCH.md`; `docs/REFERENCES.md`;
`PREREGISTRATION.md` (§1 hypotheses, §9 hand-reward panel); `src/search/{random_search.py,bayes_opt.py}`,
`src/baselines/reward_family.py`, `src/selection/fitness.py` (paths cited from the deep docs, not re-opened here).

*All 2024–2026 sweep-surfaced references remain `% VERIFY` until checked against the primary PDF in `paper/refs.bib`
(CLAUDE.md prime directive 4). No code, config, or pre-registration was modified by this dossier.*
