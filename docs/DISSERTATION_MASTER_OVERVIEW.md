# The Dissertation, Explained End-to-End — Master Overview

> **Purpose of this document.** A single, self-contained, faithful explanation of *everything* about this
> MSc dissertation — the question, the theory, the machinery, the statistics, the mechanism story, the
> engineering, and the grade strategy — written to be loaded into NotebookLM (or read cold by anyone)
> and give a complete working understanding of the project. It is generated from the repository's
> authoritative sources (the paper chapters, the frozen pre-registration, the configs, and the code) as of
> **2026-07-19**, with the pre-registration **FROZEN** at canonical hash `ce5db62c`.
>
> **Provenance convention:** claims below trace to the named repo files (e.g. `PREREGISTRATION.md`,
> `paper/CH4_methods.md`, `config/*.yaml`, `src/...`). Where a number is quoted, it is the frozen/verified
> value, not an estimate. No prototype number is presented as a scientific result (see §10.1).

---

## Table of Contents

1. [The dissertation in one page](#1-the-dissertation-in-one-page)
2. [Key facts at a glance](#2-key-facts-at-a-glance)
3. [The research question, motivation, and novelty](#3-the-research-question-motivation-and-novelty)
4. [The theory spine](#4-the-theory-spine)
5. [The experimental machinery: environment, agent, and data](#5-the-experimental-machinery-environment-agent-and-data)
6. [The LLM reward-authoring loop, the seven arms, and the sandbox](#6-the-llm-reward-authoring-loop-the-seven-arms-and-the-sandbox)
7. [The pre-registration, hypotheses, and statistical inference](#7-the-pre-registration-hypotheses-and-statistical-inference)
8. [The mechanism audit — the originality kernel](#8-the-mechanism-audit--the-originality-kernel)
9. [Results framing: why a null is the prize](#9-results-framing-why-a-null-is-the-prize)
10. [Honesty, limitations, and reproducibility](#10-honesty-limitations-and-reproducibility)
11. [The examiner, the rubric, and the grade strategy](#11-the-examiner-the-rubric-and-the-grade-strategy)
12. [Glossary](#12-glossary)

---

## 1. The dissertation in one page

**What it is.** A pre-registered, controlled experiment in which a large language model (Claude Opus 4.8)
**writes the reward-function code** for a risk-sensitive deep-reinforcement-learning portfolio agent, and
the **only thing that varies between experimental arms is what the LLM is shown about its previous
attempt**: either a single scalar performance number, or that same scalar **plus a six-number profile of
the realized return distribution's left tail** (CVaR at four levels, left-tail mass, robust skew). The RL
agent itself (Stable-Baselines3 SAC), the data, the training budget, the prompts' base text, and every
other knob are **held fixed**; only the *feedback content* in the LLM's reflection loop is manipulated.

**The question.** *Does showing the LLM the downside change the reward code it writes — and does that
change propagate through training into the realized tail risk of the resulting trading policy?* This is
a question about the **feedback channel of automated reward design**, not about beating the market.

**The headline is a mechanism story, not a leaderboard.** The dissertation pre-registers the honest
expectation that final *performance* will be **equivalent** across feedback arms (a null), and banks that
equivalence with formal machinery (TOST at a pre-committed smallest-effect-size-of-interest). The
scientific payoff is *where the causal chain breaks*: the fed signal → the authored code → the trained
policy → the realized tail. A null that is *located* — "the LLM changes its code (link 1) but the change
does not transmit to the policy's tail (link 2/3)" — is a boundary condition on what LLM feedback
engineering can do, and that is the contribution.

**Why anyone should care.** The automated-discovery agenda (Eureka, FunSearch, AlphaEvolve, the
"AI Scientist" line) is evaluated almost entirely by demonstration — no pre-registered, controlled
protocols. This dissertation is, to the author's knowledge, the first *pre-registered, controlled,
inferentially decided* instance of **feedback engineering for reward design**: it fills the
methodological gap the agenda's own surveys concede, in a domain (tail-risk-sensitive portfolio choice)
where the fed information is economically meaningful and measure-theoretically ordered (the scalar is a
*garbling* of the tail vector — Blackwell), so "more informative" is a theorem while "more effective"
is exactly the empirical question.

**Status at this writing.** The design is frozen (77 logged amendments; hash `ce5db62c`); the machinery
is built and certified (≈2,140-test suite green); two GPU pilots (learning-curve knee and seed-noise
σ_D) are done and set the training budget B\* = 400,000 steps and the tiered seed ladder; the
confirmatory campaign on the UCL Myriad cluster awaits the author's explicit GO. The dissertation PDF
(deadline 1 Sep 2026, UCL, graded with no viva) is drafted through the methods; Results/Discussion are
written after the campaign.

---

## 2. Key facts at a glance

| Fact | Frozen / verified value |
|---|---|
| Manipulated variable | Feedback content in the LLM's reflection prompt (tail vector vs scalar) |
| Fixed agent | SB3 SAC (TQC = secondary, named critic experiment only) |
| Author LLM (campaign) | Claude Opus 4.8 (single-family confirmatory; 2nd model = secondary panel) |
| Arms (7) | distributional, scalar, placebo, scalar_cvar5, placebo_shuffled, random_search, bayes_opt |
| Fed tail set (6 scalars) | cvar_05, cvar_10, cvar_25, cvar_01 (high-variance-annotated), left_tail_mass, robust_skew |
| Fitness / selection | Validation **Deflated Sharpe Ratio** (DSR) |
| Co-primary H2 tests | Intersection–union: H2-RA (Sharpe) + H2-Tail (CVaR-5%) |
| SESOI / TOST margin | 0.05 (validation-DSR units; symmetric ±0.05) |
| Testing family | m = 6, BH-FDR; report-only diagnostics disjoint |
| Training budget B\* | **400,000 steps/candidate** (R77 — measured knee of a 30-point CRN-paired curve) |
| Candidate budget | 30 candidates/arm (matched across arms) |
| Seeds | Tiered ladder (E1): 30→100→189→279→340→403→568; **primary target 403** (95% assurance); 279/340/403/568 ↦ 80/90/95/99% |
| Data | Refinitiv/LSEG gold panel `univ5`: **5,406 sessions × 963 assets**, 2005-01-03→2026-06-30, survivorship-free, point-in-time, anonymised |
| Splits (Split C) | train 2005–16 / val 2017–19 / test 2020–26, embargoed |
| Delisting policy | `liquidate_to_cash` |
| Replay buffer | Capped 50,000 (RAM-bounded; PopArt reward normalisation on) |
| Compute | UCL Myriad primary (SGE, pack-5, ≈2.05 trainings/GPU-h at B\*); laptop RTX 4050 = certified fallback |
| Freeze | `frozen: true`, canonical SHA-256 `ce5db62c…`, 8 hash-bound files, verify-or-refuse launch gate |
| Test suite | ≈2,140 passed / 3 skipped (POSIX-only), 0 failed |
| Examiner | Dr Ramin Okhrati (UCL IFT) + second marker; PDF-only, no viva; 10,000-word main body; due 1 Sep 2026 |

---

## 3. The research question, motivation, and novelty

### 3.1 The thesis, the title, and what is actually claimed

**Recommended title** (`paper/00_FRAMING…` §1, the v2 mechanism-led framing): **"Does Showing a
Language Model the Downside Change the Reward Code It Writes? A Pre-Registered, Off-Critic Test in
Risk-Sensitive Portfolio RL."** (Method-forward alternative: "Multi-Level Tail-Risk Feedback for LLM
Reward Design: A Pre-Registered Study in Risk-Sensitive Portfolio Reinforcement Learning.") A standing
framing rule: never let a sentence drift to an unqualified "the distribution" — the fed signal is six
left-tail scalars, not the full return distribution ("the construct overclaim the framing discipline
forbids").

**The one-sentence thesis** (CH1, verbatim): *"when a language model writes the reward code for a
trading agent, does showing it the tail of the realised outcome distribution — rather than a single
score — change the code it writes, and does any change reach the agent's realised risk?"*

**The outward positioning sentence** (abstract-grade): *"To our knowledge this is the first
theory-grounded, pre-registered test of whether an LLM reward-designer is a Bayes-responsive user of
risk information: whether the content of distributional feedback — not its format, length, or
vocabulary — changes the reward code the model writes, and whether that change propagates to the
trained agent's realised tail behaviour."* Portfolio construction is **the testbed, not the object**:
it instantiates the general "do LLM optimizers use feedback content?" question in the one arena where
the answer is checkable against decision theory.

**What is claimed.** The headline is a *mechanism characterization*, with the pre-registered
performance comparison as the rigorous backdrop. A null is reported as a **bounded TOST equivalence**
against the pre-registered SESOI — credited on error-statistical severity (Mayo; Rubin 2025) and
forking-paths avoidance (Gelman & Loken 2014), never a bare *p* > 0.05 — or, if the minimum detectable
effect exceeds the SESOI, as a calibrated **INCONCLUSIVE** verdict (Lakens), never an underpowered
failure. Result templates for every sign are pre-written (no viva → nothing improvised).

**Construct disclosure** (inserted verbatim near first use): the fed signal is "a vector of six
left-tail scalars (CVaR-5/10/25%, a high-variance CVaR-1%, left-tail mass beyond −2σ, and a robust
left-tail skew), estimated empirically with an extreme-value (GPD) tail for the 5%/1% levels. It is
**not** the full return distribution: it carries no central moments beyond the mean (supplied
separately as the scalar), no right tail, and no full quantile grid." The defensible theoretical claim
is that these statistics span the law-invariant *coherent-risk* class (Kusuoka).

### 3.2 The research question and the three sub-questions

The RQ is cast as a **three-link causal chain**: *fed tail signal → authored reward code → trained
policy → realised tail*. The mechanism decomposition (pre-specified, report-only, disjoint from the
confirmatory family) asks not merely *whether* richer feedback helps but *where* the channel acts or
breaks:

- **SQ1 — Responsiveness:** *does the fed signal move the code?* Instrumented by a responsiveness
  statistic: does variation in the fed tail vector produce variation in the authored reward program?
- **SQ2 — Transmission:** *does the code move the outcome?* Instrumented by a fed→code→outcome
  **mediation** analysis (the reward code as mediator between arm and realised performance; the
  responsiveness link formalised as the ACME/NIE).
- **SQ3 — Specificity:** *is any effect genuine use of the tail content, or a surface echo — and is
  any failure a numeric-legibility bottleneck?* Instrumented by an identifier-invariant structural
  comparison of authored code (does the model react to "tail/CVaR" *tokens* rather than magnitudes?)
  and a **legible-format ablation** (identical scalars re-rendered as basis points/ranks — information
  content held fixed, encoding varied). The design is thus *factorial in kind*: the main arms
  manipulate the feedback's **content**, the ablation manipulates its **encoding** — to the author's
  knowledge the first factorial dissection of the feedback channel in automated reward design.

This turns a null "from an absence of evidence into a *located* finding about *where* the channel
breaks." The honest directional expectation (from the prototype, which is machinery-only evidence —
§9.2) is a break **at the first link (SQ1)**, where a numeric-legibility bottleneck may stop the model
from reading close tail values.

### 3.3 Motivation: why the tail vs a scalar — and the EDA facts

**The logic.** Reward design is the central bottleneck in applying RL to risk-sensitive financial
control: a reward well specified in the mean can yield a policy profitable on average yet ruinous in
the tail. Most RL trading agents train on a *scalar* reward; the field's surveys flag explicit risk
incorporation as open work. LLMs can now author reward *code* and refine it from feedback (the Eureka
line) — but that feedback is typically a scalar that conveys nothing about the *shape* of the outcome
distribution. That content matters is evidenced: **Eureka's own ablation shows removing its reward
reflection costs ~28.6% of performance** — the single strongest "feedback content matters" citation.
Yet the answer is not obvious ex ante: LLM risk-taking is systematic yet steered by surface
conditioning such as an assigned persona (Hartley et al. 2025, *with Okhrati*), so genuine absorption
of fed tail information "cannot be presumed in either direction."

**The motivating EDA facts** (ACTIVE univ5 panel, Split-C train window 2005–2016; these supersede the
older-window figures):

| Fact | Value | Why it matters |
|---|---|---|
| Excess kurtosis (daily cross-section) | **15.25** | strongly leptokurtic — Gaussian summaries mislead |
| Empirical/Gaussian CVaR ratio across levels | **×0.84 → ×1.66 crossover** | *the sharpest argument*: a scalar at one level cannot represent a tail whose severity **reverses** across quantiles relative to Gaussian; a vector of level-specific shortfalls can — precisely the manipulated variable |
| Stress-day co-crash breadth | **3.3% base → 19.7%** on worst days | diversification evaporates exactly when it matters |
| −5σ daily moves vs Normal | **≈ ×10⁴ more frequent** (×10,393) | the tail is not an epsilon correction |
| Panel skew | **positive +0.21** | never claim negative skew (standing warning) |

### 3.4 The novelty — the conjunctive cell and the four contributions

**The conjunctive novelty cell** (CH1 §1.3, blockquoted): the dissertation occupies the conjunction —
*"an LLM authors reward-function **code**, iterating on the **multi-level lower-tail distribution** of
realised returns (measured off-critic), for a **fixed risk-sensitive portfolio RL agent**, under a
**pre-registered, controlled comparative protocol**."* Every neighbor is scored by which conjunct it
breaks. The cell has been verified **EMPTY** repeatedly: 3 independent scouts + a scoop sweep
(2026-06-26), a 99-agent 3-vote adversarial run (2026-06-28), the full 196-PDF corpus read (0
breaches), and the dated **novelty-fence sweep of 2026-07-13**: "still EMPTY — HIGH confidence."
Pressure converges from two flanks that have not met: the *finance* flank (GIFT, ELfolio, AlgoEvolve —
LLMs author finance artifacts, none authors the reward of a fixed RL agent under a tail-feedback
manipulation) and the *methods* flank (Gallego, RDA — feedback content is now a manipulated variable,
but never tail-risk, never pre-registered). Axis (iv), pre-registration, appears **absent from the
entire LLM-reward-design literature** — arguably the most defensible limb. (A mandatory pre-submission
sweep is scheduled; a standing wording hazard: drawdown IS already fed to LLM designers, so the claim
must always be pinned to "CVaR / tail-quantile vectors," never "risk metrics.")

**The four affirmative contributions** (none contingent on a positive result):

- **C1 — The off-critic feedback instrument.** The realized-return lower tail fed to the designer,
  measured off the critic, agent byte-identically fixed. Honestly disclosed as *endogenous* (§6.4).
  **Three-way decoupled**: the tail is *fed* on the training split; candidates are *selected* on a
  tail-blind validation DSR (λ=0); the hypothesis is *tested* on empirical CVaR over a sealed test
  split — three different estimators on three different partitions, so a tail effect cannot be a
  self-grading artefact.
- **C2 — The pre-registered comparative-inference protocol.** A cryptographically frozen design with
  intersection–union tests, placebo + structure-shuffled controls, deflated Sharpe, combinatorial
  PBO — "a bankable result of either sign."
- **C3 — The decision-theoretic envelope.** Blackwell garbling + Le Cam deficiency bound + Kusuoka
  coherent-risk spanning + CVaR robustness duality: an **optimal** user of the tail weakly dominates
  an optimal user of the scalar — an *envelope* a bounded LLM+agent may not realise, which converts
  the experiment into a falsifiable prediction with Strict/Weak/Null branches.
- **C4 — The mechanism characterization** (§3.2) — the headline and originality kernel.

The contribution is framed **not** as reward engineering but as *"a controlled, pre-registered
evaluation of automated objective-function discovery — supplying the rigour the discovery line
omits"*: that agenda's own survey concedes evaluation is by demonstration, not inference.

### 3.5 Literature positioning — every neighbor distinguished

Organised around the manipulated variable (*what is fed back to an automated reward-designer*), the
feedback taxonomy runs: human NL/preference (Kwon 2023; Text2Reward; REvolve) → per-component
**scalar** series + fitness (**Eureka**; DrEureka) → trajectory analysis (Auto-MC-Reward; CARD) →
coarse distribution *check* (CARD's binary ordering) → sentiment scores into a fixed reward
(FinRL-DeepSeek) → **the empty cell: a multi-level realised-return lower-tail profile fed off-critic
to a code-writing designer, pre-registered.**

Key distinctions (each verified first-hand in the dossier):

- **Eureka** (ICLR 2024) — the method instantiated; its reflection feeds *scalar component values*;
  its −28.6% ablation is the "content matters" anchor; robotics, demonstration-not-inference.
- **DLM / Decision-Language Model** (NeurIPS 2024) — **the structural twin** (LLM proposes reward
  code, iterates on a distribution) — but its distribution is a population-across-states spread in
  public health, no risk/tail axis, no fixed-agent isolation, no prereg. Disclosed prominently.
- **GIFT** (2026) — the freshest finance neighbor; full-text scan: **zero occurrences of "CVaR"**;
  reward authorship is *bounded to a registered penalty library* (not free code), it redesigns state
  jointly with reward (breaking reward-only identification), feeds generic rollout diagnostics, and
  is a demo. (⚠ never conflate with the unrelated robotics "GIFT".)
- **ELfolio** (2025) — the closest portfolio system; candidates selected "with the Sharpe ratio
  serving as the fitness function" (verbatim) — i.e. it operationalises **this study's control arm,
  not its treatment**.
- **FinRL-DeepSeek** — the most-conflated neighbor: the LLM is a sentiment/risk-score *encoder*
  feeding a fixed, human-written CVaR-PPO objective — it never authors the reward.
- **RD-Agent(Q)** (NeurIPS 2025) — the field's most explicit feedback vector, x ∈ ℝ⁸ whose deepest
  risk statistic is max drawdown; CVaR/ES/tail quantiles absent — the best one-line contrast.
- **Gallego 2026 ("Beyond Scalar Rewards")** — the concurrent methods-flank neighbor; coins "feedback
  engineering"; but its object is *policy* code, domain social dilemmas, no placebo/structure
  controls, no inferential statistics, no tail. Hence: *"the first pre-registered, controlled,
  inferentially decided instance of feedback engineering for reward design."* His "feedback aliasing"
  converges with the numeracy-bottleneck mechanism (a write-time engagement item).
- **Cardenoso/LEARN-Opt** — candid that automated reward design is *high-variance* (the average
  candidate fails; only multi-run search surfaces good ones) — independently licenses the matched
  30-candidate budget and per-seed ladder inference, and corroborates the likely null.
- **The strongest counter-claim, cited and rebutted**: "Reward Is Enough: LLMs Are In-Context RL" —
  shows scalar is enough *to improve*, not *as good as richer feedback* — "the margin our hypothesis
  tests."
- **Boundary hazard**: distributional-RLHF (quantile reward models, RiskPO) is the **wrong object** —
  a distribution *inside* a reward model that trains an LLM, not feedback *to a reward-designer*.
- **Orthogonal axes**: risk-sensitive/distributional RL (DSAC, WCSAC, CVaR-PG) puts risk *inside the
  agent* — here risk is measured off-critic and fed to the *designer* while the critic stays
  risk-neutral and fixed. The multi-*level* fed vector is *forced*, not stylistic: **CVaR is not
  elicitable alone (Gneiting 2011); the escape is joint elicitability of (VaR, CVaR) (Fissler–Ziegel
  2016)**. Backtest-statistics machinery (DSR/PBO/SPA/HLZ) attacks overfitting post hoc; explicit
  pre-registration in this domain is, to the author's knowledge, absent — the design pairs *both*
  remedies Rubin's critique identifies.

**Examiner-relevant cites**: Khraishi & Okhrati 2022 (ICAIF, offline RL with CQL — supervisor
lineage, framed as methodology, *not* a portfolio baseline) and Hartley et al. 2025 ACL (with
Okhrati — his own LLM×risk bridge, legitimising the premise). Guardrails: he is "Dr", not "Prof";
never misattribute CVaR-elicitability or deep-hedging papers to him.

---

## 4. The theory spine

**Source of record:** `paper/02_CHAPTER_theory.md` ("The Information Value of Tail-Risk Feedback"),
with the sign/notation contract in `paper/NOMENCLATURE.md`. The chapter was hardened in a dedicated
theory-correctness pass (fix register M1–M7/C2–C3/m13); everything below states it as the chapter now
does.

### 4.0 The one-paragraph intuition

The experiment feeds the LLM designer either a single held-out performance number (*scalar* arm) or
that same number **plus** a six-component readout of the realised return distribution's lower tail
(*distributional* arm). The scalar is literally a sub-part of what the tail arm sees — so,
information-theoretically, the tail arm can only know *more*. Blackwell's theorem turns "can only know
more" into "an optimal user can only do weakly better, for every loss function and every prior." That
is the whole formal engine — and, crucially, it is an **envelope over optimal users**, not a
prediction about a finite-capacity LLM coupled to a bounded SAC agent: *"the bound is an envelope, not
a guarantee. The distance between envelope and realisation is exactly what Chapters 5–6 estimate."*
The theory itself supplies the reason a null is expected — and the null then *locates where
transmission breaks*.

### 4.1 The central object: the scalar as a garbling of the tail vector

Let θ index the features of the realised-return law that bear on how the reward should weight the
downside. The reflection loop supplies one of two **statistical experiments** (Markov kernels
Θ ⇝ 𝒵):

- **E_vec** emits the multi-level tail vector **c**(P_θ) = (CVaR₅, CVaR₁₀, CVaR₂₅, CVaR₁,
  left-tail mass, robust skew), measured on training-split realised returns;
- **E_scalar** emits a scalar summary s = g(**c**(P_θ)).

The single structural fact — the entire manipulation: **E_scalar = g ∘ E_vec**. The scalar experiment
is a **garbling** of the vector experiment; in σ-algebra language, σ(g(**c**)) ⊆ σ(**c**) — a
sub-σ-algebra coarsening. A subtlety a probabilist would probe (M7): the garbling kernel here is
**deterministic** — a noiseless coarsening collapsing the tail coordinates onto one, the degenerate
limit of Blackwell post-processing, *not* added stochastic noise.

**The nesting is literal in code** (`src/feedback/schema.py`): every arm's block begins with the
identical header `"Your previous reward scored: {metric:.2f} (validation Deflated Sharpe)."`; the
scalar arm gets the header **alone**, the distributional arm the *same* header ⊕ the six tail lines.
The scalar arm's information set is byte-level a coordinate projection of the distributional arm's.
(A disclosed refinement: as statistics of a single sample the header scalar is *held-out* while the
tail vector is *training-split*, so the idealised diagram commutes only approximately for the realised
statistics — the block nesting itself is exact. See §4.5.)

**Theorem 3.1 (Blackwell–Sherman–Stein)** — for experiments on a finite parameter space (dominated
case: Torgersen 1991), the following are equivalent: (i) E′ is a garbling of E; (ii)
Risk_L^π(E) ≤ Risk_L^π(E′) for every bounded loss L and prior π; (iii) every convex function of the
posterior integrates higher under E. Only the cheap direction (i)⇒(ii) is used.

**Proposition 3.2 (Dominance of tail feedback):** for every bounded loss and prior,
Risk_L^π(E_vec) ≤ Risk_L^π(E_scalar) — *"an optimal reward-designer supplied with the multi-level tail
vector attains weakly higher expected designer objective than one supplied with the scalar summary,
uniformly over loss functions and priors."* The intuition sentence that precedes it: a designer free
to *ignore* part of what it is shown can never be made worse off by being shown more. Sign hygiene
(C2): losses are bounded ‖L‖_∞ ≤ 1 and the designer equivalently maximises U = −L, so "lower Bayes
risk" and "higher objective" are one statement — no sign trap.

### 4.2 Le Cam deficiency (⚠ direction) and the data-processing inequality

**Deficiency:** δ(E′, E) = inf_K sup_θ ‖(K∘E′)_θ − E_θ‖_TV — how closely E′ can be *post-processed*
to reproduce E; zero exactly when E′ is Blackwell at-least-as-informative. The **first argument is
the garbled experiment** (the standard Le Cam/Torgersen orientation). TV is the [0,2]-normalised L¹
total variation, paired with ‖L‖_∞ ≤ 1 so the risk-transfer bound holds with constant exactly 1.

**Corollary 3.3 (Worst-case price of the scalar):** the excess Bayes risk of the scalar over the
vector is at most **δ(E_scalar, E_vec)** — *strictly positive* whenever the tail levels carry
information the scalar does not.

> **⚠ THE DIRECTION FLAG (fix M3 — the most examiner-dangerous spot, now correct).** The load-bearing,
> positive quantity is **δ(E_scalar, E_vec) > 0**: post-process the *scalar*, try to reproduce the
> *vector* — you cannot. The other direction, **δ(E_vec, E_scalar), is identically zero** (the vector
> *can* be post-processed into the scalar — that is exactly g). Writing the corollary transposed makes
> the bound vacuously 0. Any document quoting this must preserve δ(scalar, vec) as the positive
> quantity.

**The DPI** — the same theorem in a second language: for the reduction g as a channel,
D_f(g\#P ‖ g\#Q) ≤ D_f(P ‖ Q) — post-processing cannot increase statistical separation. Equality —
**for strictly convex f and provided D_f < ∞** — holds iff g is *sufficient* for the dichotomy {P, Q}
(fix C3; both qualifiers load-bearing). And the bridge back (M4): for a dichotomy, Blackwell dominance
⟺ domination in **every** f-divergence *simultaneously* (Raginsky 2011) — one divergence dropping is
not enough. The divergence form is what connects the abstract claim to the concrete fact that a single
CVaR level discards exactly the cross-level tail *shape* a heavy- vs light-tailed market would reveal.

### 4.3 The coherent-risk chain — exactly

1. **Axioms.** A coherent risk measure satisfies Artzner–Delbaen–Eber–Heath's four axioms
   (monotonicity, subadditivity, positive homogeneity, translation invariance). **VaR fails
   SUBADDITIVITY specifically** (it can penalise diversification); **CVaR = Expected Shortfall is
   coherent** (Artzner 1999; Rockafellar–Uryasev 2000) — which is why the fed vector is built from
   CVaR, not VaR.
2. **Kusuoka.** On an atomless space, every law-invariant coherent risk measure is a supremum over
   mixtures of CVaR across confidence levels; every comonotonic one is a single such mixture (a
   spectral risk measure). A finite vector of CVaR levels is therefore *the finite-support basis of
   the entire class*: the scalar collapses the mixing measure to a point mass; the vector retains the
   spectrum. (Probabilist-grade care: on the *atomic* empirical measure, the computed finite-support
   discrete spectral estimator is coherent at every N — Acerbi 2002, Thm 5.3.)
3. **Elicitability — why a *vector* is forced, not stylistic.** **CVaR/ES alone is NOT elicitable**
   (Gneiting 2011). Sharper: **expectiles are the only law-invariant coherent risk measures elicitable
   as scalars** (Ziegel 2016; Bellini–Bignozzi 2015) — the formal reason a single coherent tail number
   cannot serve as a clean target. The escape is **joint elicitability**: the pair (VaR_α, CVaR_α) is
   jointly elicitable, and a finite multi-level spectral measure together with its quantiles is
   jointly elicitable of higher order with an essentially unique identification function (Osband's
   principle) — **Fissler–Ziegel 2016** (with the published correction), Frongillo–Kash 2021.
4. **Two properties kept deliberately apart** (commonly, wrongly welded): (a)
   *sufficiency-relative-to-the-scalar* = the garbling fact — what the value-of-information argument
   rests on (explicitly NOT an absolute-sufficiency claim for the full return law); (b) *joint
   elicitability* — an independent property that makes the fed CVaR sub-vector a legitimate,
   calibration-testable target and licenses the strictly consistent FZ0/(VaR, CVaR) backtest of CH6 —
   and is **not** what establishes dominance. (The −2σ tail-mass and Bowley-skew coordinates are
   identifiable summaries *not covered* by the elicitability theorems — disclosed.) Closing verdict:
   *"The scalar is neither sufficient relative to the vector nor a coherent elicitable target."*
5. **The robustness duality (why the tail should matter out-of-sample specifically).** For Z ∈ L¹,
   CVaR_α(Z) = min over the envelope {ξ = dQ/dP ≥ 0 : ξ ≤ 1/α **P-a.s.**, E_P[ξ] = 1} of E_ξ[Z]
   (the P-a.s. qualifier is fix M2). This is an L^∞ constraint on the density — *not* a
   φ-divergence ball (a different DRO geometry, flagged). Via Chow et al. 2015 it lifts to the
   sequential setting: optimising CVaR = guaranteeing worst-case expected return under a budgeted
   perturbation of the data-generating process. So feeding the designer the realised lower tail is
   feeding it a **distributional-robustness signal** — and since the sealed 2020–2026 test leg is
   precisely a distribution-shift evaluation, the sharper testable corollary follows: *if tail
   feedback helps at all, its benefit should be concentrated where the distribution shifts* —
   motivating CH6's regime-conditional analysis.

### 4.4 DSR, fitness, and the sign-conventions box

**Terminology (do not conflate):** in this dissertation **DSR = Deflated Sharpe Ratio** (Bailey &
López de Prado — Sharpe corrected for search multiplicity and non-normality), the *selection fitness*.
It is **not** Moody's *Differential* Sharpe Ratio (which appears only as a baseline reward in related
work).

**The Conventions box (fix M1), in force throughout:** returns Z are **signed** — gains positive,
losses negative — so the lower tail is the adverse direction and CVaR_α(Z) is a (typically negative)
*return*: **a more negative CVaR is worse**, and the dual is a **min**. The mirror positive-loss
convention (ℓ = −Z; CVaR a positive loss; Rockafellar–Uryasev dual a **max**) is noted once and used
only where the source literature demands it — notably Kusuoka is quoted in the mirror orientation, a
cross-convention splice the chapter flags rather than papers over. Known symbol overloads are tracked
(L = loss in CH3 vs lookback in CH4; ξ = risk-envelope density in §3.6 vs GPD shape in §4.4).

**A self-disclosed subtlety (m13):** the realised scalar comparator is a *Deflated* Sharpe, which
embeds skew/kurtosis and is therefore **not perfectly tail-blind** — the idealised E_scalar is an
approximation, and the realised scalar already carries *part* of the tail information. This
**narrows** the contrast under test — biasing *against* a measured distributional advantage — so the
deviation is conservative. Same logic for the λ=0 selector: its only tail sensitivity (the DSR's
skew/kurtosis term) is common-mode across arms, so it cannot manufacture a between-arm tail effect.

### 4.5 What the theory predicts — why the null is the honest expectation

**The envelope-vs-realisation caveats, named exactly:** (1) *optimality gap* — Prop 3.2 concerns
optimal Bayes users; the realised designer is a finite-capacity LLM feeding a fixed, capacity-limited
SAC agent, so the proposition upper-bounds the attainable improvement and does not assert any will be
realised; (2) *split-mismatch gap* — the realised header scalar (held-out) vs tail vector
(training-split) makes the garbling diagram commute only approximately for realised statistics;
(3) *endogeneity* — θ indexes a return law generated by the policy trained under the very reward
being designed, so E_vec is re-measured each generation rather than being a fixed exogenous
experiment (the conditional-on-θ dominance survives; only the closedness idealisation is relaxed).

**Three mechanism conditions, any of which can break the envelope:**

1. **Selection sensitivity** — the pre-registered λ=0 selector is tail-blind (identical across arms),
   so any tail benefit must arise from the designer's *use* of the fed signal, not selection pressure
   (conservative; makes a tail result channel-attributable).
2. **Designer responsiveness** — the benefit requires the LLM to *condition* the code it writes on
   the fed tail content: "an empirical, not assumed, property," estimated as a mediation quantity.
3. **Agent attainability — the deepest structural point.** A mean-critic SAC maximises the
   *expectation* of its reward, and a static CVaR penalty in a per-step reward is
   **time-inconsistent**: the expectation of a CVaR-penalised reward is not the CVaR of the policy's
   return distribution (Boda–Filar 2006). Sharper: optimising static CVaR in an MDP requires **state
   augmentation** (Bäuerle–Ott 2011) and the optimal policy is in general **non-Markovian**
   (Lim–Malik 2022) — *no per-step reward on a fixed state interface can encode it exactly*. Under
   the frozen identification principle (only the reward may vary across arms; state augmentation
   deliberately excluded), the reward channel is the *forced* injection point for tail information —
   and it is structurally unable to guarantee CVaR-optimality. Hence **the Null branch is
   over-determined**: it can fail at the agent stage for this structural reason, independent of
   designer responsiveness. (The principled remedy — a quantile critic — is exactly the named
   secondary TQC experiment.)

**The pre-registered prediction table (Table 3.1 ≙ prereg §1a), bound before unblinding:**

| Branch | H2-RA (Sharpe IUT) | H2-Tail (CVaR-5% IUT) | Responsiveness | Code differential | Verdict |
|---|---|---|---|---|---|
| **Strict** | tie (λ=0 ⇒ no Sharpe edge for anyone) | dist > all three comparators | > 0 | dist code references tail stats more | H2-Tail supported |
| **Weak** | tie | partial (≤ 2 legs) | ≈ 0 | weak/mixed | inconclusive (TOST-bounded) |
| **Null** | tie | tie (placebo not beaten) | ≤ 0 | no cross-arm signature | clean, bankable null |

Note the theory-derived twist: **even the Strict branch predicts an H2-RA tie** — so the branches
separate only on the tail legs and the code-level instruments, and *designer responsiveness is the
pivotal unknown*. The Null is pre-registered as the predicted outcome: the directional prototype
showed *negative* responsiveness and a tail differential that reversed under the zero-information
placebo — the Null branch's signature — and the theory supplies the reason ("a tail-blind selector
combined with a non-conditioning designer leaves no channel through which the dominance envelope can
be realised"). A confirmed Null is then *"a corroborated prediction about the gap between the
information-theoretic envelope and its bounded realisation"* — and via the duality, a statement that
the tested LLM does not, at this budget, exploit available distributional-robustness information.

**The numeracy-bottleneck mechanism** (limitation B.3.2 — the candidate explanation for *why*): a
documented LLM weakness on raw numerical magnitudes, with three sharpened facts — the failures are
**format-dependent** (reformatting toggles the canonical 9.11 > 9.8 bug within one model),
**mechanistically tied to number tokenization** (why a close pair like −0.0577 vs −0.0582 is a worst
case and basis-point integers repair it), and they **dissociate from stated comprehension** (models
articulate the correct rule yet fail to execute it). The fed CVaR vector occupies exactly this regime
— which is what the pre-registered legible-format ablation tests. The chain the theory hands the
empirics: **information is present (Blackwell) → transmission requires use (responsiveness) → use is
bottlenecked at reading numbers (numeracy) → the agent stage adds a structural CVaR-encoding
obstruction — and the instruments say which link broke.**

### 4.6 Consolidated sign/direction flag list (for any editor)

(1) The positive Le Cam deficiency is **δ(E_scalar, E_vec)**; δ(E_vec, E_scalar) ≡ 0 — first argument
= the garbled experiment. (2) CVaR is a **min** under the governing signed-return convention (more
negative = worse); the R–U **max** belongs to the ℓ = −Z mirror only. (3) TV is [0,2]-normalised L¹,
paired with ‖L‖_∞ ≤ 1 for a constant-1 bound. (4) DPI equality needs **strict** convexity **and**
D_f < ∞; dichotomy Blackwell ⟺ **all** f-divergences. (5) The garbling is **deterministic**
coarsening, not noise. (6) DSR = **Deflated**, not Differential, Sharpe; not perfectly tail-blind —
a disclosed, conservative, common-mode deviation. (7) VaR fails **subadditivity** specifically;
ES/CVaR coherent but not elicitable alone; (VaR, ES) jointly elicitable; expectiles the only
elicitable law-invariant coherent scalars. (8) The chapter never claims absolute sufficiency of the
six-scalar vector — only sufficiency *relative to the scalar*.

---

## 5. The experimental machinery: environment, agent, and data

### 5.1 The portfolio environment

**Universe and action space.** The MDP trades **N = 30 risky assets plus one cash sleeve**
(`config/environment.yaml`: `n_assets: 30`, `include_cash: true`) — the top-30 by point-in-time market
cap, held fixed across train/val/test (a disclosed composition-bias trade-off). The raw action is a
vector of **pre-softmax logits in [−10, +10]** (`action.bound: 10.0`), projected onto the long-only,
fully-invested simplex by a **frozen softmax projection** (ADR-027).

- **The unreachable-corner limitation** (`src/env/portfolio_env.py`, `project_simplex`): softmax maps
  onto the **open interior** of the simplex, so every weight is strictly positive and an exact
  100%-cash allocation is **provably unreachable** — it can only be approached asymptotically. This
  structurally damps the full "flee to cash" response a tail-averse agent most wants in a crisis.
  Crucially it applies **equally to every arm**, so it is a shared limitation of the parameterisation,
  not an H2 confound. Dirichlet policies and simplex decomposition are cited as corner-reaching
  future work.

**State/observation** (`portfolio_env.py::_obs`): a flattened float32 vector of

- the **60-day lookback window** of per-asset returns, strictly past (60×30 = 1,800 dims);
- **realised volatility** over windows {20, 60} per asset (60 dims);
- the **lagged VIX** (1 dim; FRED VIXCLS, pre-lagged on the panel so the env never double-lags);
- a constant **cash-row marker** (1 dim);
- the **previous weights** including cash (31 dims).

Total = **1,893 dims** — the figure behind every RAM calculation. The no-look-ahead invariant is
strict (`_obs` never reads a return row at/after the decision row) and **adversarially unit-tested**:
corrupting all future rows leaves the observation byte-identical. `cash_daily_rate` is held at 0.0
(threading a DGS3MO series is a flagged refinement, R20).

**Transaction costs**: proportional-turnover model, **headline 10 bps**, with a robustness grid
`[0, 5, 10, 25, 50]` bps re-priced *analytically* on frozen gross/turnover series (no retraining).
Turnover is **half-L1 against drifted weights**: `turnover = 0.5·‖w − w̃‖₁` where `w̃` is the prior
weights drifted by realised returns — the agent pays cost only on the gap it actually trades.

**Per-step return and timing** (return-realised-after-action): `r_t` is read *after* the action; then
`gross = w[:N]·r_t + w_cash·cash_daily_rate`, `port_ret = gross − cost`. **`port_ret` is the
SIMPLE/arithmetic per-step return** — the single object every downstream number is computed from. A
*separate* log-wealth accumulator (`log1p(max(port_ret, −0.9999))`) exists as a logging sidecar only.

**Episode structure**: a fixed half-open walk-forward window. The window edge is a Gymnasium
**truncation, never a termination** — verified against SB3 2.8.0 internals so the critic's value
bootstrap `r + γQ(next)` is not spuriously zeroed once per episode. Evaluation is **one deterministic
walk-forward rollout** per split (the standard backtest protocol, Sood 2023). Env bundles built for
search **have no test window** — `test_returns` raises, so the sealed 2020–2026 leg is *physically
unreachable* during selection.

### 5.2 The reward contract

The single signature every reward — LLM-authored, hand-designed baseline, or search-sampled — must
satisfy exactly (`src/reward/contract.py`):

```python
def reward(weights, returns, prev_weights, port_ret, info)
    -> tuple[float, dict[str, float], object]
```

- `weights` — the just-projected simplex weights (N+1,), a **detached read-only copy**;
- `returns` — the realised asset-return row r_t (N,), read-only copy;
- `prev_weights` — the prior weights (N+1,), read-only copy;
- `port_ret` — the realised net portfolio return (float) — the object of study;
- `info` — a shallow-copied dict carrying `reward_state` (and the read-only arrays).

It returns `(total, components, reward_state)`: the agent optimises **`total`**; **`components`** is
logged, never optimised; **`reward_state`** is round-tripped through `info["reward_state"]` so rewards
can be **stateful** (e.g. a Moody–Saffell differential-Sharpe recursion). Signature validation rejects
anything not exactly those five positional parameters.

**Anonymised-arrays invariant:** all arrays are anonymised numpy — **no tickers, no dates ever reach a
reward**. Imports are allowlisted to numpy only. On failure/NaN the sandbox substitutes
**`SAFE_DEFAULT = 0.0`** and *counts* it (substitution counters surface per training window and per
rollout, so a part-failed candidate is visible, never silent). The env hardens the boundary further:
the untrusted reward receives detached read-only copies (`base is None` — no writable parent
reachable) and a shallow-copied info dict, so an in-place write physically cannot corrupt cross-step
or cross-candidate state — preserving the replay-from-archive determinism guarantee.

### 5.3 The fixed agent

**SB3 SAC is the headline agent**, held byte-identically fixed across all seven arms — fixed
architecture and hyperparameters, so performance differences attribute to the reward (a runtime
equivalence assertion, `assert_fixed_agent_across_arms`, enforces this). Live hyperparameters resolve
in `src/agents/trainer.py::resolve_agent_kwargs` (SB3-2.8.0 defaults: lr 3e-4, batch 256, γ 0.99,
τ 0.005, `ent_coef="auto"`, MlpPolicy) with `learning_starts` floored at 1000. Training wraps the env
in `VecNormalize(norm_obs=True, norm_reward=False)` — observation stats freeze post-training and ride
a `NormalizedPolicy` so evaluation uses *train-period* stats (no validation leakage); **reward
normalisation stays off because the reward is the object of study**. (`config/algos.yaml` is a
directional template, NOT the executed-values source.)

**TQC is a named SECONDARY experiment, not the novelty**: sb3-contrib TQC with identical settings, so
that contrast is precisely *mean critic vs truncated-quantile critic*. The contribution lives in the
off-critic feedback channel.

**PopArt reward normalisation** (config-gated on, uniform across arms). Motivation is a *verified*
engine pathology: a prototype LLM reward emitted |total| ≈ 1.1e4, driving the Q-target toward
R/(1−γ) ≈ 1e6 and exploding the critic loss to ~1e7. The fix is **scale-only**: divide only the
learning signal by a running scale σ = √(bias-corrected EMA[r²]) (Adam-style debias so the very first
reward normalises to ±1), clamped at `min_scale = 1.0` so it is a pure *shrink* of supra-unit rewards
and the exact identity for sub-unit ones. At *constant* σ the transform is a positive affine map of
the value function, so the optimal policy is unchanged; the implemented EMA σ drifts, so it is only
**approximately** policy-preserving — honestly scoped and bounded by per-candidate σ logging and a
one-seed `popart=False` ablation on the frozen winners. `info["port_ret"]` is forwarded byte-for-byte,
so every *analysed* number is identical with or without the wrapper. One precise caveat: with
`ent_coef="auto"`, effective entropy regularisation can still vary with authored reward magnitude —
"fixed agent" means fixed architecture+hyperparameters, not a fixed effective regulariser; this is
made auditable, not assumed away.

**Replay buffer cap = 50,000 transitions** (ADR-025/-042). SB3's default 1M buffer at the 1,893-dim
observation would need ≈15 GB CPU RAM (OOMs the 15.6 GB laptop); a full-history buffer at B* = 400k
would need ~5.6 GB. Capped at 50k it is a bounded **~0.76 GB** sliding window. Benign by argument:
every episode replays the same fixed calendar, so a 50k window always retains ~17 complete passes over
the entire training period (coverage is never lost — only old policies' transitions age out), and the
1-gradient-step-per-env-step replay ratio is the conservative corner where small buffers are least
harmful (Fedus et al. 2020). Applied identically to every arm → common-mode, not a channel confound.

### 5.4 The data

**The gold panel.** Licensed **Refinitiv/LSEG** daily total returns, **survivorship-free,
point-in-time** — explicitly **NOT CRSP**. Headline artifact:
`data/gold/returns_panel_univ5.parquet` — **5,406 sessions × 963 RICs, 2005-01-01 → 2026-06-30**
(21.5 years, to the *settled* 2026-06-30 cutoff; ADR-051). Companions: a cash-features panel
(vol20, vol20/vol60, FRED-VIX) and the PIT top-30 selection panel. The panel identity
(`gold.suffix: univ5`) is **bound into the freeze hash** — a rebuild must re-freeze, never silently
swap. Licensing: redistribution prohibited — the repo ships checksums + the acquisition pipeline + a
synthetic panel, never the data.

**Split C** (ADR-044, executed 2026-07-02):

| Split | Window | Role |
|---|---|---|
| Train | 2005-01-01 → 2016-12-31 | agent learns; the fed tail signal is *measured* here |
| Validation | 2017-01-01 → 2019-12-31 | candidate selection (held-out Deflated Sharpe) |
| Test (**sealed**) | 2020-01-01 → 2026-06-30 | untouched until final inference; spans COVID recovery, the 2022 rate-shock bear, the 2023–25 rally |

**Embargo/purge arithmetic:** embargo floor **21** trading days, but the effective inter-split purge is
**max(embargo 21, lookback 60) = 60 sessions** (López de Prado discipline — the purge must cover the
feature lookback). Executed val start = **2017-03-30**; the executed sealed window opens
**2020-03-30**, so the COVID crash itself (19 Feb–23 Mar 2020) falls *inside* the test-boundary purge
— disclosed, not engineered around. Always quote the max() arithmetic, never "21" alone.

**Delisting policy: `liquidate_to_cash`** — post-delisting returns are zero-filled (proceeds held
flat ≈ cash), preserving dead names (e.g. Wachovia 2009, Dell 2013) rather than dropping them (which
would re-introduce survivorship bias). This *understates* rather than *invents* the delisting tail —
the conservative choice for a tail study. The Shumway surcharge is a report-only sensitivity band
d ∈ {0, −30, −55, −100%}, across which pooled test CVaR-5% moves only ~2% relative — the H2 ordering
is invariant.

**`load_gold_panel` mechanics** (`src/data/loaders.py`): reads the three suffix-selected parquets
(SHA-256-verified against the manifest on request — a missing manifest entry fails loud); resolves the
phase's PIT top-30; slices the window; applies the delisting policy; fills VIX gaps leakage-free
(leading gaps seeded only from closes strictly *before* the window); asserts full finiteness; and
emits an **anonymised `Panel`** — `(T,N)` returns, VIX, dates, and integer asset ids 0..N−1. The
RIC↔id mapping is returned *separately* for provenance only and **never reaches a reward or the LLM**
(the contamination defence).

### 5.5 Compute

**Training budget B\* = 400,000 steps per candidate** (R77/ADR-058, superseding R74's 200k). The
**two-stage measured-knee story**: Stage 1 — a pilot found the critic's steep descent complete near
~100k and held-out performance flat to its 350k ceiling; but a ceiling is a range limit, not a
verdict. Stage 2 — a **pre-committed extension rule, registered before the extension data existed**,
carried the ladder to 1.6M steps (16× range) on both archived winner rewards, 3 CRN seeds each (the
30-point curve). The curve rises decisively 200k→400k (distributional +0.145 val-DSR at 400k, paired
SE ≈ 2.9–3.6×; scalar +0.032, 5.4× SE) and **flattens beyond 400k** (increments collapse to
+0.016–0.017). **The measured knee = 400,000** — ~90% of the attainable gain at 2× compute — applied
identically across arms so contrasts read at one fixed, matched budget. Verdict artifact:
`outputs/tables/bstar_rule_verdict.json`; the freeze gate binds algos/campaign to 400,000.

**Substrate — UCL Myriad primary, laptop fallback** (ADR-053): the confirmatory campaign runs via
`scripts/run_campaign_cluster.py` on Myriad SGE arrays, device-homogeneous V100/A100 pools, every CRN
seed pair device-consistent. The RTX 4050 laptop is the **certified fallback** with science parity by
construction (every science primitive reused; cross-substrate parity pairs measured bitwise).

**Throughput:** at B\* a candidate trains in ~65 min on a dedicated V100; **five candidates share each
GPU (pack-5)** at a measured aggregate **2.05 trainings/GPU-hour** (supersedes the 3.74 figure that
was measured at the old 200k budget). Walltimes are sized at a conservative 25 steps/s planning floor
(ADR-055); submissions are chunked into many small arrays (ADR-054) because the scheduler throttles
big pending tails. Realised wall-clock and cost are reported in CH6 (an examiner expectation).

> **Not yet executed** (marked `[FROM CAMPAIGN]` in the paper): the PopArt cross-arm σ tables, the
> popart=False ablation, and the realised compute figures — all await the campaign.

---

## 6. The LLM reward-authoring loop, the seven arms, and the sandbox

### 6.1 The evolutionary discovery loop (`src/llm/loop.py`)

The core cycle runs once per arm; its per-generation algorithm:

1. **Build the prompt** — generation 0 uses the initial prompt (rendered `system.txt` +
   `initial_generation.txt` with the env interface filled); every later generation uses the built-in
   reflection preamble — *"Reflect on the previous candidate's results and propose an improved reward
   function. Feedback from the previous candidate:"* — plus the arm's serialized feedback block.
2. **`llm.complete(system, user)`** — one archival call through the pinned client; the raw completion
   is salvaged by `extract_reward_source` so a markdown-fenced reward is never rejected for
   formatting.
3. **`validate_once` in the sandbox** — AST-gate, then one execution in a killable child on a
   production-shaped fixture. A `SandboxError` → log + skip + a crash-robust failures ledger; it
   never crashes the loop.
4. **Train the fixed agent** on the candidate reward (the realized PopArt scale and training-time
   SAFE_DEFAULT substitution counts are captured for cross-arm auditability).
5. **Evaluate on validation** — fitness = validation Deflated Sharpe.
6. **Measure the TRAINING realized-return distribution** — the six tail scalars.
7. **Build the next feedback block** — `schema.build_block(arm, fitness, tail)`; tail stats pass only
   to the tail-carrying arms (`distributional`, `scalar_cvar5`, `placebo_shuffled`), `None` for
   `scalar`/`placebo`.
8. **Archive** — the exact rendered prompt, reward source + SHA-256, feedback block, metrics, and
   realized validation returns persist, so results **replay rather than regenerate**.
9. **Reflect-on-BEST** — the generation's *best-fitness* candidate's feedback block (not the last
   one) seeds the next generation's prompt, Eureka-faithfully.

**Budget semantics.** A single-shot arm (`generations == 1`) spends the whole matched budget in one
generation; multi-generation arms split the same budget (campaign: 30 candidates = 6 generations × 5).
Every slot — accepted, sandbox-rejected, LLM-error-skipped, or resume-replayed — counts one author
draw. `matched_budget: 30` is asserted identical across every arm: *"the property that licenses the
comparative claim."* **Winner** = the accepted candidate with the highest validation fitness.

**Diversity without temperature.** Opus 4.8 *rejects* the temperature parameter, so within-generation
diversity comes from a per-candidate **prompt-variation directive** — identical across arms and
deliberately naming NO risk statistic (the R38 de-seed: it asks the model to vary *which* statistics
it tracks without ever suggesting CVaR/drawdown, so it cannot pre-seed the tail into non-tail arms).

**Operational robustness** (a two-week unattended run): archived candidates AND ledgered failures
replay byte-faithfully on `--resume` (never re-billing the author); LLM-error skips are counted and
re-attemptable, distinct from sandbox rejects; a starved-environment error aborts loudly for
supervisor relaunch rather than poisoning a paid candidate; sticky API-key failover on
credit-exhaustion with a loud anomaly.

### 6.2 The prompts — tail-neutral by construction

**System prompt** (essence): *"You design REWARD FUNCTIONS (Python) for a reinforcement-learning
portfolio-allocation agent. You receive ANONYMIZED numeric arrays only — no asset names, no dates, no
identifiers."* It states the exact contract and the rules: numpy only; no file/network/OS access;
*"Optimize RISK-ADJUSTED performance — weigh return against its risk. **The feedback after each
attempt tells you HOW to weigh it; do not assume.**"* **Initial prompt**: fills the env interface
(anonymised shapes, the softmax-simplex long-only action, the 10 bps cost, the `port_ret` formula,
the stateful contract), asks for "risk-adjusted return (not raw return alone)," and closes: *"The
feedback you receive after each attempt is what should steer how you shape risk."*

**Why tail-neutrality matters (construct validity).** Neither base prompt contains any
tail/CVaR/drawdown/quantile vocabulary — mechanically **enforced by the freeze gate**
(`assert_prompt_tail_neutrality` fails the freeze if either hash-bound prompt contains any of ~11
tail tokens). Both prompts say "risk-adjusted" — a *general* risk instruction — and explicitly defer
the *how* to the feedback. The measured effect is therefore precisely **the marginal value of
tail-SPECIFICITY over general risk awareness**, delivered exclusively through the feedback channel.
(The pilot's version of this went wrong: the base prompt named "tail" and "CVaR," every arm wrote
tail-aware code, and the manipulation collapsed — the R38 de-seeding fixed it.)

**A precision point:** `prompts/reflection.txt` is deliberately **not loaded** (dead code) — the
reflection turn is composed from the built-in preamble + `build_block`. Describe it that way, never
as a template file.

**The client:** pinned dated snapshot (Opus 4.8 campaign / Sonnet 4.6 prototype); key from env var
(never archived); every call appends a provenance record — model, rendered prompts, raw response,
token usage, `stop_reason` (so a truncation/refusal is attributed correctly, not mislabeled a "bad
candidate"), request id, served model (the reproducibility anchor for the secondary Qwen3-Coder
panel). The JSONL archive sink flushes per call, so a crash loses at most the in-flight call. Prompt
caching is disclosed as **physically inert** on Opus 4.8 (the ~898-token prefix is below the
4096-token cache floor).

### 6.3 The seven arms and the contrast logic

All feedback arms run the same fixed SAC agent and the same matched 30-candidate budget; the five LLM
arms differ **only** in `feedback_kind`:

| Arm | Fed each reflection | What the contrast isolates |
|---|---|---|
| **distributional** | Header (`"Your previous reward scored: {x:.2f} (validation Deflated Sharpe)."`) + intro + the **full six-line tail set** (CVaR 5/10/25/1% — 1% annotated "(high-variance estimate)" — left-tail mass, left-tail skew) | The treatment (H2) |
| **scalar** | Header **only** | Does *any* tail information beat a bare performance number? |
| **placebo** | Header + *"Reference constants (inert; no diagnostic content):"* + six `reference value i: +0.000` lines, matched in line count and ±15% character length | **Tokens/block-presence control**: dist > placebo ⇒ information, not prompt length. The "inert" labelling is a disclosed, deliberate tell — without it, six 0.000 lines would read as *real* diagnostics of a riskless distribution (active misinformation, a worse confound); conservative for the null. |
| **scalar_cvar5** | Header + **exactly one** downside line (`CVaR 5%`) | **Tail-shape vs any-downside-number**: dist > scalar_cvar5 ⇒ the multi-level *shape* matters beyond a single downside statistic. |
| **placebo_shuffled** (R32) | The distributional block's **exact structure** — same header, intro, six labels, the CVaR-1% annotation — but the six real values **candidate-seeded-permuted by a derangement** (no value stays under its own label; replayable seed from the candidate id) | **Structure-vs-content** (the Gupta–Hartford format-vs-content threat): matches the FORMAT and the marginal set of numbers, breaks the coherent label→value tail SHAPE. The tell-free, byte-length-matched structure control. |
| **random_search** (H4a) | No LLM. Uniform sampling over the **same six-primitive linear reward family** as BO (return, log-return, turnover, drawdown, CVaR, vol terms), rendered to gate-clean source, matched budget | **Proposal quality** at comparable (not identical) expressive power. Deliberately strong (Bergstra–Bengio). Honest scope: the LLM writes free-form code the six-term family cannot reach — never claim H4a proves the LLM is a better optimizer over an *identical* space. |
| **bayes_opt** (H4b) | No LLM. GP + Matérn-2.5 + Expected Improvement (Snoek 2012) over the **continuous weights of the same fixed six-term template**, matched budget | **Open-ended reward *language* vs tuning a fixed parametric one.** |

One line each: *dist > scalar* = value of tail information; *> placebo* = information not tokens;
*> scalar_cvar5* = shape not any-downside-scalar; *> placebo_shuffled* = coherent content not format;
*LLM arms vs search arms* = proposal quality / free-form language at matched budget.

### 6.4 The fed block and the six tail scalars — and the endogeneity honesty

**The rendered block is fully deterministic** (identical inputs → byte-identical text). Worked
example:

```
Your previous reward scored: 0.83 (validation Deflated Sharpe).
Realized-return tail diagnostics (training period):
  CVaR 5%:  -0.041
  CVaR 10%: -0.029
  CVaR 25%: -0.016
  CVaR 1%:  -0.067  (high-variance estimate)
  left-tail mass: 0.061
  left-tail skew: -0.38
```

(A report-only **legible rendering** — the same six lines as integer basis points with decile tags —
exists behind a default-off flag, probing whether the bottleneck is *reading* close floats rather
than *using* tail information.)

**The six frozen statistics** (`ReturnDistribution.tail_stats()` — exactly these keys):

- **`cvar_05`** — mean of the worst 5% tail, estimated by the **EVT/GPD peaks-over-threshold** fit
  (EVT routing for α ≤ 0.05). The fed headline level.
- **`cvar_01`** — also EVT; **annotated "(high-variance estimate)" in the block** (~30 tail points on
  the fed window).
- **`cvar_10`, `cvar_25`** — **empirical** CVaR (mean of the worst ⌈αT⌉ returns) — in the
  distribution body the empirical quantile is the efficient estimator.
- **`left_tail_mass`** — `mean(returns < −2σ)`.
- **`robust_skew`** — quantile-based **Bowley skewness** `((Q95−Q50) − (Q50−Q05)) / (Q95−Q05)`,
  NEGATIVE when the left tail is longer.

**How measured:** fit once on the trained policy's **training-period realised simple returns** —
measuring on validation *and* selecting on validation would re-introduce overfitting, so the LLM
shapes the in-sample tail while the agent is judged out-of-sample. EVT machinery: losses L = −returns;
threshold = the 10% loss quantile; GPD(ξ, β) by plain scipy MLE; closed-form VaR/CVaR used only in
the regular MLE region (−0.5 < ξ < 1) with empirical fallback (Smith non-regularity / infinite-mean
guards). The honesty apparatus ships with it: the bias-corrected UPOT estimator is disclosed *future
work* with first-hand measurements of why it would no-op here (~98% of the error is variance; ξ ≤ 0
in ~94% of draws where the correction is undefined); any per-candidate EVT↔empirical switch in the
fed CVaR-5% is logged, never silent; stationary-block-bootstrap CIs, exceedance counts, reliability
tiers, and threshold-sensitivity spreads ship as the uncertainty exhibits.

**THE critical honesty point — endogeneity.** The estimator is **"critic-agnostic" but NOT
"agent-independent."** Critic-agnostic = it reads no Q-network — a post-hoc fit on realised returns
that works for any critic architecture. But the returns it fits are the SAC policy's *own* realised
returns, and that policy was trained under the candidate reward: **the fed tail is ENDOGENOUS**. H2
therefore compares **two coupled reward → policy → measurement loops** (scalar-fed vs tail-fed) — the
legitimate object of study (*does richer tail feedback steer a better loop?*), not an exogenous risk
measurement. The train/val split mitigates selection-overfitting but does **not** break the
endogeneity; no "works on any agent" claim is ever made.

### 6.5 The sandbox — untrusted LLM code (`src/sandbox/executor.py`)

LLM-authored reward code is untrusted. The **two-stage design**:

**Stage 1 — `validate_once` per candidate:** extract source → **AST gate** → exec once in a
restricted namespace `{"np": numpy, "__builtins__": SAFE_BUILTINS}` inside a **killable spawned
child** on the production-shaped fixture, under a wall-clock timeout — the only stage allowed to be
slow. The AST gate statically rejects, before any execution:

- imports outside numpy — and *any* `from … import` entirely (a real RCE fix: `from numpy import
  load` yields a bare name attribute checks never see);
- dunder access anywhere (`x.__class__` object-model walks);
- attribute *mutation* (numpy is a process-global singleton; `np.mean = …` would poison later
  candidates);
- the numpy IO/FFI denylist (`load` = pickle-RCE, `save*`, `fromfile/tofile`, `genfromtxt` + aliases,
  `dump/dumps`, `memmap`, `frombuffer`, `DataSource`, `lib/ctypeslib/f2py/testing`, `mro`, `open`,
  `ctypes`, `data`);
- **PLUS an attribute ALLOWLIST — the load-bearing soundness fix**: the denylist alone is unsound
  (numpy's object graph reaches `os` via gate-legal chains like `np._pytesttester.os.system` —
  verified end-to-end), so *every* attribute must name a known-safe numeric op; dangerous leaves
  (`system`, `popen`, `environ`…) are simply absent, so no chain of any depth can reach them;
- forbidden builtins (`open/exec/eval/__import__/compile/getattr/setattr/input/vars/globals/locals/
  dir/help/breakpoint`) and format-string field access (the `'{0.__class__…}'.format` escape).

`SAFE_BUILTINS` hands the code only arithmetic/container builtins plus a restricted import permitting
numpy-rooted modules only (numpy lazily imports submodules). The child applies best-effort POSIX
rlimits (≈2 GiB address space, 15 CPU-s, 64 fds) — a disclosed no-op on Windows, where the wall-clock
timeout is the backstop.

**The ADR-057 three-phase handshake** (a real forensic fix): the child boots via a stdlib-only shim
and reports (1) `ready` — spawned, before any heavy import (45 s environment grace); (2) `armed` —
numpy/MKL imported + fixture unpickled (120 s grace); (3) verdict — with the strict 2.0 s timeout
clocking **only the candidate's own code**. Previously one clock covered spawn + numpy DLL load, so
on a memory-starved box a *good, paid* candidate was falsely rejected. Grace exhaustion raises a
distinct starved-environment error → abort-and-resume, never a permanent rejection.

**Stage 2 — `safe_call` during training:** the validated callable runs **in-process** (no subprocess,
no per-step timeout — that would dominate training cost) in a cheap try/except; on exception or
non-finite total it substitutes `SAFE_DEFAULT = 0.0` and **counts** it (per-window counters are
archived, so a part-failed candidate is auditable, not invisible). Explicitly documented as *not* the
security boundary — the boundary is the AST allowlist + the killable validate-once child.

---

## 7. The pre-registration, hypotheses, and statistical inference

**Why pre-register — the design's own words** (`PREREGISTRATION.md`): *"The headline H2 can return a
null. Fixing the hypotheses, budgets, metrics, and analysis plan before the campaign makes a null a
credible finding about the question as posed, not a moved goalpost. This document is the spine of that
guarantee."* The unit of inference is **a reward function's out-of-sample risk-adjusted performance**
over the test span, across seeds and the candidate population — NOT the cross-section of assets.

### 7.1 The four hypotheses

**H1 — LLM vs hand-designed rewards (descriptive/report-only).** H0: median OOS risk-adjusted
performance of LLM-designed rewards ≤ the best of the **frozen 4-member hand-designed baseline
family**: `raw_return` (the FinRL-default field-standard floor), `return_minus_variance`,
`return_minus_cvar`, `differential_sharpe`. Deliberately subordinate to H2, no inferential
multiple-comparison claim (R30); baselines disclosed as un-tuned; where a validation fitness is not
archived the executed fallback selects on the sealed leg and this is **disclosed as
snooped-descriptive** (R49). A freeze-gate assert binds the executed family to the frozen one.

**H2 — distributional vs scalar feedback (THE CO-PRIMARY HEADLINE).** Two co-primary
**intersection–union tests** (R25), each pitting `distributional` against the three comparators
{`scalar`, `placebo`, `scalar_cvar5`}, each supported **iff all three legs reject one-sided at
α = 0.05** in the predicted direction — with **no further leg correction**: *"the conjunction IS the
correction"* (Berger 1982; joint size ≤ max leg size = α).

- **H2-RA (risk-adjusted):** tail feedback yields winners with **higher OOS Sharpe IQM** at matched
  compute, surviving both controls. 3 Sharpe legs.
- **H2-Tail:** the same feedback yields a **less-severe realized left tail (higher CVaR-5%)** OOS.
  3 CVaR-5% legs; *corroborated — never gated* — by the FZ0/(VaR, ES) Diebold–Mariano comparative
  backtest (Fissler–Ziegel 2016; Nolde–Ziegel 2017).

Reporting is a **two-tier verdict** — the abstract never claims a tail improvement off the Sharpe
gate alone. The estimand per leg: per-seed Sharpe/CVaR → rliable IQM → **paired stratified bootstrap
over shared training seeds** (CRN pairing cancels seed-level common variance), with the one-sided p
taken directly from the bootstrap upper tail (skew-agnostic, R64). The pre-registered **a-priori
prediction** (§1a): a **tie on the Sharpe legs regardless of channel** (the λ=0 selector is
tail-blind) and separation on the CVaR legs iff the fed tail leaves a code-level signature; the
prototype's negative responsiveness predicts **the Null branch — a clean, bankable result**.

**H3 — iterative vs single-shot (reflection-ablation control).** H0: multi-generation reflection ≤
single-shot at matched candidate budget. Iterative distributional winner (6 generations,
reflect-on-best) vs a matched single-shot condition (generations = 1, best-of-N, no reflection;
identical budget/seeds/selector); per-seed IQM paired difference **plus a ±0.05 TOST** so a null is a
bounded null; R50 adds a placebo-relative uplift difference so a null reads "reflection left no
tracking signature beyond content-free reflection." Report-only, outside the frozen m = 6.

**H4 — LLM vs uninformed search.** (a) vs `random_search` — widened (R28) to sample the *same*
six-primitive reward family as BO, so a positive H4a is not a grammar-richness artefact; (b) vs
`bayes_opt` — GP + Matérn-2.5 Expected Improvement over the fixed template, matched budget.
**Bonferroni-over-2** within the family; each leg has its own ±0.05 TOST bound. Scope disclosure: the
LLM authors strictly-richer free-form code, so a positive H4 = "open-ended language + procedure," not
procedure alone.

**Secondary, un-numbered:** SAC (mean critic) vs TQC (quantile critic) — known in the literature, not
the novelty, reported separately. **Cross-hypothesis stance (R31):** H1–H4 are separate pre-registered
estimands — no global FWER across the four by design, with a Bonferroni-across-4 *sensitivity*
reported.

### 7.2 Fitness: the validation Deflated Sharpe Ratio

Winners are selected on the **validation DSR** of realised validation returns
(`src/selection/fitness.py::held_out_fitness` = `deflated_sharpe_ratio(val_returns, n_trials) −
λ·|CVaR_α|` with frozen **λ = 0**). Three deliberate properties:

1. **Reward-independent** — fitness depends only on realised returns, never the candidate's own
   scalar, so selection **cannot be reward-hacked**; train-split input raises.
2. **What DSR deflates for** (Bailey & López de Prado): the observed Sharpe is discounted for (a) the
   number of trials (the expected max Sharpe of N zero-skill trials), (b) track-record length, and
   (c) non-normality (skew/kurtosis enter the PSR denominator). Trial-count rule = **per-arm
   candidates** (cross-arm multiplicity is the m=6 family's job — counting all arms would
   double-correct).
3. **Tail-blind BY DESIGN**: "a tail-aware selector would confound the H2 feedback channel
   (selection-FOR-the-tail masquerading as feedback-driven tail improvement)." λ is FIX-class — never
   a calibration target. This is also what generates the a-priori Sharpe-tie prediction.

### 7.3 Equivalence machinery: SESOI, TOST, and the inconclusive branch

- **SESOI = 0.05 in validation-DSR units**, symmetric TOST margin **±0.05** (≈ 0.07 annualised
  Sharpe). Decision rule: if the TOST **90% bootstrap CI** for the difference lies inside ±0.05, the
  arms are *practically equivalent within the smallest effect deemed worth detecting*.
- **Units — a subtlety easy to misstate:** the *wired* `h2_tost` applies ±0.05 in the test
  statistic's own units (per-seed Sharpe-IQM / CVaR-IQM difference); the R58 companion `h2_tost_dsr`
  computes the bankable-null TOST **in the SESOI's own validation-DSR units** via a documented
  conservative Sharpe→DSR ceiling (RA legs only). Both coexist; name which is which.
- **TOST never gates** — every equivalence/Bayes/MCS quantity is report-only; the only gates are the
  two IUTs.
- **The INCONCLUSIVE branch (R47):** power analysis put the Sharpe-leg MDE@80% ≈ 0.177 DSR ≫ the
  0.05 SESOI at the seed floor — so **a bare non-rejection licenses only "INCONCLUSIVE"** unless the
  DSR-units TOST CI actually lands inside ±0.05. Registered — the write-up cannot slide p > 0.05 into
  an equivalence claim.
- **Why a null is bankable** — the verbatim pre-committed sentence: a double non-rejection is
  reported as *"multi-level tail-risk feedback … did not produce detectably better OOS risk-adjusted
  performance or tail outcomes than scalar feedback, and — where the TOST 90% bootstrap CI lies
  inside ±0.05 — the two feedback channels are practically equivalent within the smallest effect we
  deemed worth detecting … a calibrated statement about the feedback channel as posed, not a moved
  goalpost."* The σ_D-robustness clause: the mechanism headline is **independent** of whether H2
  lands as equivalence (σ_D small) or non-rejection (σ_D larger) — which is exactly why the thesis is
  decoupled from that one pilot outcome.

### 7.4 The multiple-testing family: m = 6, BH-FDR, disjoint report-only ledger

**The frozen m = 6 enumeration** — the realized family a fail-loud assert checks against the frozen
set:

| # | Contrast (a > b) | Metric |
|---|---|---|
| 1 | distributional > scalar | Sharpe |
| 2 | distributional > scalar | CVaR-5% |
| 3 | distributional > placebo | Sharpe |
| 4 | distributional > placebo | CVaR-5% |
| 5 | distributional > scalar_cvar5 | Sharpe |
| 6 | distributional > scalar_cvar5 | CVaR-5% |

(`cvar_01` is opt-in — would grow m to 9 — and NOT in the frozen family.) **Benjamini–Hochberg at
q = 0.05 is primary** (the BH-over-6 is a *reported sensitivity*, not the gate — the gate partitions
the 6 into the two IUT families); the joint **Romano–Wolf stepdown** (shared stationary-bootstrap
path) is the FWER alternative; the **Harvey–Liu–Zhu t > 3 hurdle is scoped to absolute-alpha claims
only** — never arm contrasts. The headline claim is comparative, never "beats the market."

**Report-only families kept DISJOINT from the gating m = 6** (keys disjoint by construction, each
`gates_h2: false`): factor attribution (difference-in-alpha CAPM→FF6+BAB+QMJ, Newey–West, BH within —
the "your edge is just BAB/low-vol" pre-empt), `h3`, `h4`, `h2_tost`, the `placebo_shuffled`
structure control, `dsr_effective_n`, cross-hypothesis sensitivity, the delisting band d ∈ {0, −30,
−55, −100%} (H2 tail ordering invariant across it), and the entire mechanism instrument suite (§8).

### 7.5 The overfitting / robustness backbone (`src/inference/`)

- **PBO/CSCV — the PRIMARY overfitting guard** (Bailey et al. 2017): partition into S=16 blocks,
  **fully enumerate** all C(S, S/2) IS/OOS splits, rank the IS-best candidate's OOS relative rank →
  logit λ; **PBO = fraction of splits with λ < 0**. Chosen as primary precisely because it is
  rank-based and *trial-count-free* — under a guided sequential LLM search the DSR's independent-trials
  n is ill-defined, so DSR is a secondary diagnostic. A second PBO ranked on the DSR-proxy covers the
  selection rule actually used (R36).
- **The re-centred stationary bootstrap** (Politis–Romano): re-centred, deliberately
  **not studentized** (size certified empirically by null calibration); the arm-contrast unit is the
  **paired seed difference test** — seeds resampled i.i.d., the same draw applied to both arms, IQM
  recomputed — carrying across-seed training-RNG variance a seed-averaged series destroys (the
  superseded construction was anti-conservative ~21% vs 5%); one-sided p skew-agnostic (R64).
- **Model Confidence Set** (Hansen–Lunde–Nason 2011, R69): the set of arms statistically
  indistinguishable from the best at size 0.10, on per-seed scores. For the predicted null this is
  the right *shape* of statement: if no arm dominates, the MCS contains nearly all arms — the honest,
  multiplicity-corrected "indistinguishable."
- **The Bayesian null** (R67): the same paired difference expressed as **positive evidence FOR
  equivalence** — JZS Bayes factor BF01 (Rouder 2009) + BIC cross-check (Wagenmakers 2007) +
  posterior ROPE mass with a **90% HDI ⊂ ROPE** rule mirroring the TOST interval (Kruschke 2018) —
  answering "informative, or merely underpowered?" which TOST alone cannot. The one researcher degree
  of freedom is pinned pre-freeze: Cauchy scale r = √2/2 with a mandatory robustness curve over
  r ∈ {0.5, √2/2, 1, √2} (an un-pinned prior would manufacture null evidence via Jeffreys–Lindley).
- **ES backtesting**: ES alone is not elicitable; the (VaR, ES) pair is jointly elicitable —
  licensing the strictly consistent **FZ0** loss and a **Diebold–Mariano comparative backtest**
  (Nolde–Ziegel 2017) + the Harvey–Leybourne–Newbold small-sample companion + an explicit size/power
  calibration at the realised window length. Corroborates, never gates, H2-Tail; low power at
  CVaR-1% is disclosed.

### 7.6 Freeze mechanics, amendments, the seed ladder, budget, splits

**FROZEN.** `frozen: true`, canonical SHA-256
`ce5db62c97b6f79236e5f827ae7ad2df81d8c9df450757df5f066ba4480c58ba`, executed **2026-07-18**,
git-tagged (`prereg-v1.0`, `prereg-freeze-ce5db62c`), bundled
(`outputs/prereg_bundle_ce5db62c.zip`), and pinned by a regression test. **The 8 hash-bound files**
(canonical SHA-256 over LF-normalised bytes in fixed order): `PREREGISTRATION.md`,
`config/preregistration.yaml` (freeze-state-stripped), `config/inference.yaml`,
`config/environment.yaml`, `config/data.yaml`, `config/arms.yaml` (**the manipulated variable's
wiring**), `prompts/system.txt`, `prompts/initial_generation.txt` (the treatment files bound by R62 —
closing "the unhashed-manipulated-variable gap"). Enforcement is mechanical: `enforce_freeze` refuses
to launch any real run unless frozen AND recorded == recomputed hash; the freeze gate also runs
~20 prose↔yaml↔executed-config asserts (arm roster, m=6, SESOI, margins, B\*, seeds, matched budget,
splits, prompt tail-neutrality, bound-file existence); a PreToolUse hook guards the bound files.
**A deliberate quirk to explain, not "fix":** the frozen `PREREGISTRATION.md` header still reads
"PRE-FREEZE" and its freeze-record table is unfilled — because editing the file would change
`ce5db62c`; the authoritative freeze record lives in `docs/DECISION_LOG.md`.

**Amendment discipline.** Post-freeze changes require an explicit, dated, user-approved amendment —
never a silent edit. The amendment record logs **77 amendments** (ADR-023, D2, E1, R11–R77), each with
its section, summary, and yaml mirror.

**The seed ladder — Amendment E1 (supervisor-approved).** The σ_D pilot measured **σ_D = 0.369**
(σ_seed = 0.244, ρ = −0.141), firing the pre-registered σ_D > 0.10 trigger; the old "30→50" rule was
retired and replaced by the variance-anchored **assurance-tier ladder**
`tiers: [30, 100, 189, 279, 340, 403, 568]` — cumulative, CRN-pairing preserved, each tier a COMPLETE
study, truncation banks the largest completed rung:

| Tier | Meaning |
|---|---|
| 30 | distinction-bankable core (H2 + mechanism + H1 + H3 complete; the CVaR-5% co-primary leg — σ_D = 0.0015, ρ = +0.47 — already conclusive here) |
| 100 | σ-precision insurance (σ_D estimate tightens to ≈ ±10%) |
| 189 | Monte-Carlo point-estimate power rung (Sharpe-leg TOST decisive if σ_D is as measured) |
| 279 / 340 / 403 / 568 | **80% / 90% / 95% (primary target) / 99% equivalence assurance** — powering the SESOI at the χ² upper confidence bound on σ_D |

The **stopping tier is EXOGENOUS** — measured Myriad throughput vs the 1 Sep deadline, never
result-inspection — preserving the single confirmatory look. Search stays 1 seed/candidate; only
winners re-run at the ladder (seeds-on-winners).

**Budget & splits.** `matched_budget: 30` candidates/arm across all 7 arms ("more candidates"
explicitly rejected on multiplicity grounds); B\* = 400,000 steps (R77, the measured knee — raised by
a rule registered *before* the extension data existed); Split C with the 60-session purge and the
resolved integer windows asserted pre-run (train [60,3021] / val [3081,3775] / test [3835,5406] on
univ5). `docs/DESIGN_DETERMINATION.md` classifies every parameter MEASURE/CALIBRATE/FIX/REALISTIC —
"best" means *methodologically-correct and frozen with evidence*, never performance-maximal.

**Historical layering (keep straight when quoting):** panel univ4 → univ3 → **univ5**; B\* 200k →
**400k**; reflect protocol parallel-best → **serial reflect-on-BEST**; compute venue rented-4090 →
laptop-only → **Myriad** (the frozen §12 retains the laptop-only text as trail — recorded, not
re-hashed; ADR-058).

---

## 8. The mechanism audit — the originality kernel

This is the dissertation's claimed original contribution: not "did tail feedback win?" but a
**calibrated instrument for locating where the feedback channel acts or breaks**. Everything in it is
report-only and structurally **disjoint from the frozen m = 6 confirmatory family** — no mechanism
statistic gates H2, and none can convert the pre-registered null into a performance claim (BH is
applied across the mechanism legs anyway, with a Bonferroni sensitivity).

### 8.1 The three-link chain and the null-locating logic

```
fed tail signal --(a)--> authored reward CODE --(b)--> trained policy --> realised tail
       \____________________________(c')_____________________________/
```

- **SQ1 — Responsiveness (link a):** does the fed signal move the code at all?
- **SQ2 — Transmission (link b):** does the changed code move the trained policy's realised outcome?
- **SQ3 — Specificity:** is any effect genuine use of the tail *content* — or a surface echo of
  tokens/format — and is any failure a *numeric-legibility* bottleneck?

The payoff under a null (`src/inference/mediation.py`, verbatim): *"If the fed signal does not change
the program (a ≈ 0 — the responsiveness null this work predicts), then a·b ≈ 0 for ANY b: the chain
is severed at the **first** link, and the equivalence in Y is **explained, not merely observed**."*
CH6's mechanism figure draws the three links with **a cut glyph marking the link the evidence
severs**.

### 8.2 The instruments (each implemented, deterministic, replayable from the archive)

- **Responsiveness (SQ1)** — `src/inference/responsiveness.py`: the association (Spearman rank by
  default — robust to heavy-tailed generation-to-generation deltas) between a fed-signal summary X
  (e.g. the fed CVaR magnitude or its generation-over-generation change) and an authored-code feature
  M (e.g. an AST tail-construct count), over candidates, with a bootstrap CI (integer-valued M gets a
  degenerate-replicate reliability flag).
- **Mediation (SQ2)** — `src/inference/mediation.py`: the standard linear decomposition
  (Baron–Kenny; Preacher–Hayes bootstrap CI on the indirect effect a·b) with X = fed signal,
  M = code feature, Y = realised OOS tail outcome. **Honesty stated in the module itself:**
  observational mediation is associational; a causal reading needs sequential ignorability, and here
  M is endogenous to the agent it steers — so it is reported as *"a descriptive decomposition of the
  mechanism,"* never causal proof, never a gate.
- **The reward-program taxonomy** — `src/inference/reward_taxonomy.py`: a categorical,
  **identifier-invariant** taxonomy of authored programs induced from the campaign archive:
  canonicalise every program's AST *shape-set* (node TYPES only — identifiers and literals never
  enter, so a program that merely *names* variables "cvar" cannot fake structure), build the pairwise
  Jaccard similarity graph, take connected components at a threshold as the program KINDS, label each
  kind by construct prevalence, exemplify by medoid. The scientific read-off is **`taxonomy_by_arm`**:
  do different feedback arms author different *kinds* of programs, or the same kinds reshaped? (A
  search arm sampling one template should collapse to one kind; an LLM arm routing the fed tail into
  program *structure* should shift its kind mixture.) Shannon entropy per arm summarises diversity;
  threshold-sensitivity honesty ships built-in (Rand-index stability across thresholds; n_kinds
  provably non-decreasing in the threshold).
- **The construct-prevalence differential and code distance** — counts of declared tail constructs
  per program (the shared theory→code construct vocabulary) and AST-level structural similarity
  (within-vs-across-condition clustering), feeding the "code differential" column of the §3.7
  prediction table.
- **Surface-echo vs genuine-use (SQ3):** three mutually reinforcing probes. (i) The
  **identifier-invariant / named-vs-blinded structural test**: because the taxonomy and distance
  instruments see only AST shapes, a model that merely *echoes* the fed vocabulary ("cvar_05")
  without changing computation is separable from one that changes program structure. (ii) The
  **placebo_shuffled arm** (§6.3): the distributional block's exact structure with values deranged —
  if the model responds to *a plausible-looking numeric table* rather than the coherent tail shape,
  distributional and placebo_shuffled behave alike. (iii) The **scalar_cvar5 arm**: separates the
  multi-level *shape* from *any single downside number*.
- **The legible-format ablation (the numeracy lever)** —
  `responsiveness.legible_format_responsiveness_differential`: the SAME tail content re-rendered as
  integer basis points / decile ranks. If the channel is silent because the numbers are *illegible*
  (close small floats like −0.0577 vs −0.0582 sit squarely in the documented LLM close-float failure
  regime) rather than because tail information is *useless*, legible rendering should RAISE
  responsiveness — *"a positive, CI-separated differential is a citable mechanism for the predicted
  null AND a concrete scaling hypothesis: legibility, not capacity, is the lever."*
- **Supporting exhibits** (all registered report-only): the fed-signal **SNR/attenuation** analysis
  (prototype validation: 63–87% of fed deltas resolvable; attenuation λ 0.85–0.98 — measurement noise
  cannot explain away an SQ1 null), the five-account fingerprint (A1–A5 rival explanations), the
  reflection funnel, the information-utilization gap, and the oracle-headroom bound.

### 8.3 The dose–response exhibit

The B\* budget curve doubles as a mechanism exhibit: the response to training compute is
**channel-dependent** (the distributional winner's validation-DSR gain over 200k is +0.145 at 400k
then flattens; the scalar winner clears the rule at 400k but keeps rising at 1.6M) — a
budget-dose-response fingerprint measured nowhere in the Eureka lineage, feeding the R77-ii
dose–response tier ({200k, 400k, 800k} × 10 seeds) scheduled in the campaign window.

### 8.4 The numeracy-bottleneck reframe (the interpretation)

The headline interpretation of the predicted null (ADR-039): the break is at SQ1, and its candidate
cause is a **numeracy bottleneck** — frontier LLMs' documented unreliability at comparing close small
floats (50–70% accuracy in the cited probes), which is exactly the regime the fed CVaR vector
occupies. The evidence chain: the failures are format-dependent, tokenization-rooted, and dissociate
from stated comprehension (§4.5) — and the legible-format ablation turns the interpretation into a
testable within-study contrast. The connection to the examiner's own work: Hartley…Okhrati 2025 (ACL)
shows LLM risk-taking is steered by *surface conditioning* (persona) rather than deep risk
computation; this study localises the analogous failure in the *authorship* direction — the model
edits on semantic/format cues rather than fed magnitudes — scoped to a frontier model so the null is
not a small-model artefact.

> **Status note:** the mechanism kernel is implemented and was exercised end-to-end on 239 archived
> prototype records (per-arm SQ1 fingerprint rows render in the results notebook) — but per the
> prototype rule (§9.2) those numbers validate the *instrument*, not the hypothesis; every
> dissertation-grade mechanism number is a `[FROM CAMPAIGN]` slot.

---

## 9. Results framing: why a null is the prize

### 9.1 The architecture of the argument: foreshadow → predict → deliver

The dissertation does not present a null as a disappointment; it presents it as **the pre-registered
Null branch of a three-branch prediction table** (Strict / Weak / Null), decided in advance and then
read off the campaign. The binding write-time directive: *"the MECHANISM — 'does showing the LLM the
downside change the reward CODE it writes?' — is the spine; the performance equivalence is the
rigorous backdrop."*

**CH6's four pre-committed reporting rules (verbatim — they govern everything):**

1. *"Present every null as a bounded equivalence with a confidence interval — never as 'p > 0.05'."*
2. *"Lead with TOST."* Equivalence is the headline; the one-sided IUT p is the confirmatory check.
3. *"Show controls visually."* Placebo and placebo_shuffled overlaid on the same axes as the treatment.
4. *"A null with a mechanism is a finding."* A confirmed null is always reported as a corroborated
   prediction accompanied by the mechanism evidence — never a bare absence of effect.

CH6's running order: **§6.1 execution/integrity FIRST** (freeze-hash match, run ledger, deviations
log, realised wall-clock/cost, serial–parallel byte-equivalence — "so the reader can judge execution
adequacy before interpreting effects"); §6.2 the two co-primary IUTs, equivalence-first; §6.3
controls + robustness (delisting band, cost sweep, PBO/DSR, factor attribution, regime slices,
synthetic-null falsification, MCS + Bayesian evidence); §6.4 secondaries (H1 descriptive-only, H3,
H4); §6.5 mechanism (responsiveness, mediation, reward-program differential, budget diagnostic, the
three-link-chain figure with **the cut glyph marking the link the evidence severs**); §6.6 the
prediction-table mapping so the outcome is *a decided prediction of either sign*. Every number is a
`[FROM CAMPAIGN: …]` slot — **the chapter is a prereg-skeleton awaiting the campaign; no result
exists yet.**

CH7 makes the null a positive result three ways: a *"corroborated prediction about the
envelope–realisation gap"*; via the robustness duality, a statement that this designer *"does not
convert that signal into more robust reward code at the studied budget"*; and *"a boundary condition
for the automated-discovery agenda… The contribution is not the sign of an effect but a calibrated,
falsifiable instrument for asking the question."* The practitioner takeaway is concrete: *"richer
feedback is not self-acting"* — realising the envelope needs both a tail-rewarding selector and a
demonstrably conditioning designer, "neither of which a default Eureka-style loop with a tail-blind
fitness supplies."

### 9.2 THE PROTOTYPE RULE — no Sonnet number is evidence

CH5 is titled "Machinery Validation and Design Hardening." The rule: the prototype *"de-risks the
apparatus and informs the design, but it is **not** evidence for or against the hypotheses"* —
codified as limitation B.6.6: *"no prototype number appears anywhere in the results or informs any
confirmatory conclusion."*

Why the rule exists — **three independent artefact senses**, each dissected honestly:

1. **Wrong inference unit.** The apparently exciting p ≈ 0.004 ("distributional tail beats scalar")
   came from a within-path time bootstrap on a *single* winner's autocorrelated return series —
   market-path error only; the correct unit is the reward population across seeds, which a
   single-seed pilot cannot supply.
2. **Reverses under control.** Against the zero-information placebo, the distributional tail is
   significantly *worse* (p ≈ 0.0005); the CVaR ordering tracks the risk–return frontier, not
   tail-information content — "the placebo — the arm fed *no* tail — has the safest tail of all."
3. **Mechanism points the wrong way.** Responsiveness (rank correlation of fed-tail movements vs
   authored-code changes) is *negative*, and the binary tail-usage gate saturated across all arms —
   including never-fed search baselines.

The integrity twist: the prototype *"must be shown to have shaped the design through what it taught
about the machinery, not through a signal it appeared to find — because, read correctly, it found no
signal to chase."* CH5 §5.4 documents the defect→correction map (wrong unit → per-seed rliable;
double-corrected conjunction → two co-primary IUTs; no format control → placebo_shuffled; prompt
leakage → de-seeded prompts; critic instability → uniform PopArt; saturated gate → reward-program
differential). And one honesty step further: the negative responsiveness *"taken at face value… is a
genuine prior against the study's own now-headline mechanism claim… and we do not explain it away"* —
carried forward as a report-only measure, prejudged in neither direction. What the prototype
legitimately established: the apparatus works end-to-end (17.9 h wall-clock, ~240 candidates, six
arms, ~$3.17 API, one consumer GPU), and the frozen design carries "a documented,
integrity-preserving trail from each defect to its correction."

---

## 10. Honesty, limitations, and reproducibility

### 10.1 The limitations register — honest and complete

CH7 §7.2 foregrounds four in the body — construct (six left-tail scalars, coherent-risk span only,
"no claim about upside or non-coherent features"); training budget (read *"at this fixed, matched
budget at the measured knee"*, never "at convergence"); selection blindness (λ=0 is what makes a tail
effect channel-attributable, but it also places the study on the boundary of the Null branch);
external validity ("the study cannot earn the plural 'language models'"). Each is framed as *"a
deliberate, disclosed design decision with a documented rationale, not a hidden assumption."*
`paper/APPENDIX_B_limitations.md` (the sole appendix, deliberately lettered B to mirror the prereg;
word-excluded) carries the full register, grouped by Shadish–Cook–Campbell validity type, each with
rationale + direction of bias + mitigation. The load-bearing entries:

- **Endogeneity of the fed tail (B.2.0)** — verbatim: *"The tail vector is measured on the trained
  policy's own realised returns — two coupled reward→policy→measurement loops, never an exogenous
  measurement; 'critic-agnostic' is not 'agent-independent'."* Mitigation: the fed/selected/tested
  three-way split "keeps the loops from grading themselves"; the mediation analysis is a descriptive
  decomposition under sequential-ignorability caveats, never causal proof.
- **Single-family confirmatory (B.3.1)** — one Claude family (Sonnet 4.6 → Opus 4.8); the
  open-weights second-model cross-check (Qwen3-Coder) is *specified but unexecuted*, secondary/
  report-only; no plural "language models" claim is earned.
- **Unit-of-analysis (B.2.6)** — the confirmatory contrast re-runs *one* selected reward program per
  arm across seeds, so its interval generalises to the selected programs, not the feedback condition
  as a whole; authoring variance is not resampled at the confirmatory stage. The honest resolution:
  the **channel-level** claim is carried by the report-only mechanism kernel — computed across *all*
  authored candidates, which does sample the authoring step — "the two are reported as such."
- **K = 5 search width (B.3.3)** — 5 candidates per reflective generation × 6 generations; if
  K-sampling collapses, the matched budget overstates effective search — "a scope choice, disclosed,
  not a power claim," with a pairwise reward-source diversity report as mitigation.
- **Bounded realisation** — the theory's dominance is *"an envelope, not a guarantee, and the
  empirical contribution is to measure how much of it a bounded realisation actually attains"* —
  required to sit INSIDE the claim, never detachable.
- **Tail-neutral base prompts (construct validity)** — the pilot's prompt leakage (base prompt named
  "tail"/"CVaR" → every arm wrote tail-aware code → manipulation collapsed) was fixed by R38
  de-seeding and is now *mechanically enforced by the freeze gate*. Consequence: the measured effect
  is the marginal value of tail-specificity over general-risk framing — subtle, null predicted,
  equivalence banked.
- Also carried: tier-conditional power (B.5.1 — the n=30 floor is equivalence-underpowered; the
  ladder rungs 279/340/403/568 power 80/90/95/99%; "the reported power is always the achieved-rung
  power"); pretraining-contamination defence (date-blind anonymised integer-index arrays + AST gate);
  the numeracy interpretation of negative responsiveness (B.3.2); single-look sealed test (B.5.7);
  LLM non-determinism → *"the analysis (not the generation) is the reproducible object"* (B.6.1); the
  supervisor-approved research-question change (B.6.3, sign-off pending); H1's opposing-bias
  disclosure (B.6.5). B.7 converts the register into the future-work list (λ>0 selector, second
  family/universe, corner-reaching action parameterisation, QD diversity, hierarchical Bayes).

### 10.2 Reproducibility, provenance, and engineering

- **The freeze machinery** (§7.6): canonical SHA-256 over the 8 bound files; ~20 prose↔yaml↔executed
  asserts; **verify-or-refuse** on every driver start; dual record (auto DECISION_LOG + human ADR);
  git tag + signed bundle + OpenTimestamps; a PreToolUse hook guards the bound files post-freeze.
- **Determinism & the replay contract:** *"results replay from an on-disk provenance archive rather
  than being regenerated (LLM calls are non-deterministic)."* Every stack seeded from the run seed
  (`CUBLAS_WORKSPACE_CONFIG` + `PYTHONHASHSEED` pinned); every LLM call archives prompt/code/feedback
  /model/usage/stop-reason; crash-consistent atomic writes (temp → fsync → rename) so `--resume`
  never bakes a half-written record into the analysis; a single read path (`src/io/results.py`).
  The philosophy: *"trainings are bitwise-deterministic per device class and archived; LLM
  generations are non-deterministic BY NATURE and archived per-call; analysis is a pure function of
  the archive + pinned deps."*
- **Test suite:** ≈**2,140 passed / 3 skipped (POSIX-only) / 0 failed** — verified first-hand
  2026-07-19 (the count grows; older docs say 2,000+).
- **Licensed-data governance (LSEG/Refinitiv):** the gold panel **cannot be redistributed**. The repo
  ships the *method*: the full acquisition pipeline (an entitled user rebuilds the exact panel),
  SHA-256 checksums for byte-exact verification, and a shape-identical synthetic panel on which the
  entire pipeline and suite run. One open legal question (flagged, not hidden): whether *derived*
  return series in run records may be published needs a licence check before any public data deposit
  — with two TMLR-acceptable fallbacks (aggregate statistics only, or synthetic-panel replication).
  The dissertation itself is unaffected (examiners get the PDF).
- **Run-time provenance:** per-record environment snapshot (python/platform/pip-freeze/CUDA/driver/
  determinism flags/gold manifest hashes); code identity in every record (the GIT_COMMIT marker —
  a real gap caught and fixed); container identity (Apptainer sif sha256); content-addressed
  archive-integrity manifest; per-record wall-clock + scheduler forensics (feeding the examiner's
  compute-reporting expectation directly).
- **Cluster science parity:** the **LAPTOP↔CLUSTER PARITY invariant** — every science primitive
  reused, bitwise-certified cross-substrate — so the laptop is a true fallback and "the cluster is a
  throughput accelerator, never a single point of failure." Serial↔parallel byte-equivalence is
  itself a reported CH6 integrity line.

---

## 11. The examiner, the rubric, and the grade strategy

### 11.1 The setting

Graded on the submitted PDF **alone** (no viva) by **Dr Ramin Okhrati** (UCL IFT — "Dr", NOT "Prof";
a measure-theoretic probabilist, coherent-risk / offline-RL (CQL) / LLM-risk researcher) plus a
second marker from ANY discipline (hence: faultless to a non-specialist). Hard constraints:
**10,000-word main-body prose** (math, code, figures, tables, footnotes, refs, and appendices ALL
excluded — "the escape hatch"), the **16-section structure in order**, ~60% core
(Methods+Results+Discussion), Harvard refs, deadline **1 Sep 2026** (submission targeted Aug 28–29).

### 11.2 Okhrati's revealed grading function (from his real coursework feedback — "the compass")

1. **INTUITION > technical correctness** — every choice needs the "why should the reader believe
   this"; correct-but-textbook math earns little.
2. **DEPTH > breadth** — "do less, go more in depth."
3. **HONESTY rewarded** — mature non-overselling = his 5/5. *The equivalence/null IS this; never spin
   it.*
4. **MOTIVATE the method with the data** — insightful EDA, not standard description (hence the tail
   EDA exhibit: kurtosis 15.25, the CVaR crossover, 19.7% co-crash, −5σ ×10⁴, positive skew — feeding
   "the tail facts → why a scalar cannot convey them → the hypothesis").
5. **ORIGINALITY foregrounded.**
6. **Mechanics he docks:** missing wall-clock COMPUTE reporting, untidy figure/table
   cross-referencing, unconventional section order — each closed by construction (per-record
   wall-clock capture + scheduler ledgers; the figure-manifest cross-referencing discipline; the
   16-section order kept).

Examiner-tailoring: frame the design as **offline RL on a fixed historical panel** (precisely:
simulated-online off-policy SAC on a historical-replay simulator); cite Khraishi & Okhrati 2022 (CQL)
and Hartley…Okhrati 2025 ACL (the golden neighbour — used in CH7 to localise the break in
*authorship*, not consumption, of tail information); get the risk-measure chain exact (§4.3); never
misattribute papers to him.

### 11.3 The UCL rubric and grade security

Four equal dimensions: (1) background + INDEPENDENCE OF THOUGHT; (2) research design +
UNQUESTIONABLE ORIGINALITY; (3) novelty + significance = **journal-publishable** for 90–100%;
(4) communication = faultless + clear to a non-specialist. Gates: ≥70 non-condonable; 86–100 =
publishable. The mapping: faultless execution = the frozen 7-arm design + the tiers; unquestionable
originality = the mechanism instruments + the dose–response curve measured nowhere in the Eureka
lineage; journal-publishable significance = the generalization triad + calibration + one-command
replication; faultless communication = the structure itself.

**Grade security by design:** "the tiers ARE the grade-security mechanism" — floor-first ordering
banks the complete distinction-grade study at n = 30 in ~1.3 days central (~10% of compute); every
tier boundary is a complete design ("adaptive execution, invariant design"); the stopping rule is
**exogenous** (throughput + calendar, never the observed effect — "nothing a probabilist examiner can
attack"); dual-track fallback (the laptop auto-executes the identical study); bulletproof resume.
Cheap procedural points are pre-banked: the verbatim Myriad@UCL acknowledgment, wall-clock compute
from scheduler accounting, the frozen prereg, the Ethics / no-human-subjects / data-governance
statement, and the UCL Category-2 (assistive) AI-disclosure — with AI-as-object (the LLM as study
subject) kept distinct.

**Standing write-time directives (binding):** KEEP BREADTH (run all analyses; foreground the deep
core in the body, push the rest to word-excluded appendices; never silently drop a pre-registered
result); INCREASE DEPTH (theory intuition, the mechanism as a deep causal study, motivating EDA, the
null as a mechanism boundary connected to Okhrati's ACL'25 finding); execute the four fix registers
(theory correctness; writing/communication; integrity/procedural — including Okhrati's written
sign-off on the proposal pivot and stripping any literal `% VERIFY`; honesty/claims — and keep the
"disclosure-as-grade-tactic" reasoning OUT of the PDF prose). **Publication path: workshop → TMLR →
ICAIF** — the release checklist is explicitly built for it.

---

## 12. Glossary

| Term | Meaning in this dissertation |
|---|---|
| **Arm** | One experimental condition (7 total); the five LLM arms differ ONLY in the reflection feedback block |
| **AST gate** | Static analysis of untrusted LLM reward code before any execution (allowlist + denylist + dunder/import bans) |
| **B\*** | The per-candidate training budget: 400,000 env steps (R77 — the measured knee) |
| **Blackwell garbling** | Post-processing of a statistical experiment by a Markov kernel; the scalar feedback is a (deterministic) garbling of the tail vector, hence weakly less informative for every loss and prior |
| **CRN seeds** | Common-random-number pairing: the same seed used across arms so seed-level variance cancels in paired contrasts |
| **CVaR_α / ES** | Conditional value-at-risk = expected shortfall: the mean of the worst α-fraction of returns; coherent; **not elicitable alone** — (VaR, ES) jointly elicitable |
| **DSR** | **Deflated** Sharpe Ratio (Bailey & López de Prado) — Sharpe discounted for trials, track length, non-normality. The selection fitness (λ=0). NOT Moody's Differential Sharpe |
| **Endogeneity (of the fed tail)** | The fed tail is measured on the trained policy's OWN realised returns — two coupled reward→policy→measurement loops; "critic-agnostic" ≠ "agent-independent" |
| **EVT / GPD** | Extreme-value theory / generalised Pareto peaks-over-threshold fit, used for the fed CVaR-5%/1% levels |
| **Freeze / `ce5db62c`** | The pre-registration's frozen state: canonical SHA-256 over 8 bound files; changes only via dated approved amendments; enforced by verify-or-refuse launch gates |
| **H2-RA / H2-Tail** | The two co-primary intersection–union tests: Sharpe legs / CVaR-5% legs, each 3 legs vs {scalar, placebo, scalar_cvar5} |
| **IUT** | Intersection–union test: supported iff ALL legs reject; joint size ≤ max leg size, so "the conjunction is the correction" |
| **IQM** | Interquartile mean (rliable) — the robust per-seed aggregate used in every arm contrast |
| **Identification principle** | ONLY the reward may vary across arms; any new state/reward input is creep that breaks identification |
| **λ = 0 (tail-blind selector)** | The fitness carries no explicit tail term, so any tail effect must come through the feedback channel — selection cannot masquerade as the treatment |
| **m = 6 family** | The frozen confirmatory testing family: {dist>scalar, dist>placebo, dist>scalar_cvar5} × {Sharpe, CVaR-5%}; BH-FDR q=0.05 |
| **Matched budget** | 30 candidates per arm, identical across all 7 arms — the property licensing the comparative claim |
| **Mechanism kernel** | The report-only SQ1/SQ2/SQ3 instrument suite (responsiveness, mediation, taxonomy, format ablation) — the originality headline |
| **Null branch** | The pre-registered predicted outcome: Sharpe tie + tail tie + non-positive responsiveness — a clean, bankable, *located* null |
| **PBO / CSCV** | Probability of backtest overfitting via combinatorially symmetric cross-validation — the primary overfitting guard (rank-based, trial-count-free) |
| **PIT** | Point-in-time: the panel never encodes information unavailable on the decision date (survivorship-free) |
| **placebo_shuffled** | The structure-vs-content control: the distributional block's exact format with tail values deranged across labels |
| **PopArt** | Scale-only reward normalisation of the critic's learning signal (min_scale = 1); analysed returns byte-identical with/without |
| **Prototype rule** | NO number from the Sonnet prototype enters the dissertation as evidence — machinery validation only |
| **Responsiveness** | SQ1: the association between the fed tail signal and features of the authored code |
| **SESOI** | Smallest effect size of interest: 0.05 validation-DSR units — the TOST equivalence margin ±0.05 |
| **Seed ladder (E1)** | Cumulative tiers [30,100,189,279,340,403,568]; 403 = primary target (95% equivalence assurance); stopping tier exogenous |
| **Split C** | train 2005–16 / val 2017–19 / sealed test 2020–2026-06-30, with a 60-session purge at each boundary |
| **TOST** | Two one-sided tests: equivalence is claimed iff the 90% CI for the difference lies inside ±SESOI; otherwise "inconclusive" — never a bare p > 0.05 |
| **univ5** | The frozen headline gold panel: 5,406 sessions × 963 RICs, Refinitiv/LSEG, 2005→2026-06-30 |

---

*End of master overview. Generated 2026-07-19 from the frozen repository state (`ce5db62c`); regenerate
after the campaign fills the `[FROM CAMPAIGN]` slots.*

