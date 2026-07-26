# EUREKA gap analysis — the "vs Eureka" map for the dissertation

**Purpose.** A deep, strict, first-hand comparison of **Eureka** (Ma et al., *Human-Level Reward Design via
Coding Large Language Models*, ICLR 2024, arXiv:2310.12931) against **this dissertation's** pre-registered
design (LLM authors reward-function *code* for a risk-sensitive long-only portfolio RL agent, with a
**multi-level tail-risk feedback channel** as the contribution). It states the genuine novelty/differentiators,
the gaps (what Eureka has that this lacks) with a per-gap *adopt / disclose / irrelevant* verdict, the strongest
defensible "vs Eureka" positioning, and the **prioritized implementable Eureka mechanisms** with grade-ROI +
pre-freeze risk + a strict worth-it verdict.

**Status.** Read-only on code/config. The design is **freeze-ready and verified-green**; this document recommends
adoptions *conservatively* — most Eureka features are correctly NOT for this thesis. **Date:** 2026-06-25.
**Audience:** the PDF-only MSc grade (no viva; supervisor Dr Ramin Okhrati, stochastic-control/RL/finance).

**Provenance.** Eureka details below are verified **first-hand** from the local PDF text cache
(`D:\tmp\littxt\00_core_pillars__Eureka__2310.12931.txt`, the full paper + appendices A–H incl. the verbatim
prompts, reflection examples G.1, correlation analysis, ablations, compute). The dissertation design is read
first-hand from `PREREGISTRATION.md`, `00_planning/FINAL_PLAN_FOR_CLAUDE_CODE_DETAILED.md` §B, the docs suite
(`docs/DEEP_H2.md`, `docs/DEEP_H3.md`, `docs/distributional_feedback_schema.md`, `docs/DEEP_FRAMING_discipline.md`),
and the live code (`src/llm/loop.py`, `prompts/{system,reflection}.txt`, `src/feedback/{measurement,schema}.py`,
`scripts/inspect_rewards.py`). Any claim not verified first-hand is marked `% VERIFY`.

---

## 0. Bottom line up front

1. **The machinery is Eureka; the contribution is not.** This dissertation runs an Eureka-style loop
   (environment-as-context → LLM authors reward *code* → train → reflect → revise → evolutionary selection on a
   scalar fitness). The genuine novelty is the **distributional/tail-statistics feedback channel** (six coherent-
   risk tail scalars measured *off-critic* from realized returns), the **held-out financial fitness** that
   replaces Eureka's simulator oracle, the **finance domain** (first for a *trading* agent), and an **inference
   stack** (rliable per-seed IQM paired bootstrap, PBO/CSCV, two co-primary IUTs, FZ0/ES tail backtest,
   pre-registered TOST null) that **exceeds Eureka's own** statistical rigour.

2. **Three differences are load-bearing and defensible** (§3): (i) **feedback object** — Eureka reflects on the
   reward's *own per-component scalar trajectories*; this reflects on the *realized-return tail distribution*
   measured independently of the reward; (ii) **fitness** — ground-truth simulator oracle (Eureka) vs **held-out
   validation Deflated Sharpe** decoupled from the candidate reward (finance has no oracle); (iii) **evaluation
   rigour** — Eureka's human-normalized score over 29 envs vs a **single-task, pre-registered, per-seed IUT**
   with a bankable null.

3. **The gaps that matter are three, and all three are already handled** (§4): many-envs breadth (→ disclosed as
   external-validity scope, the correct call), the **per-component reward reflection** (→ a real, partial, safe
   *adoptable* upgrade — see §6 P-A), and the curriculum/GPT-4-scale/HNS (→ irrelevant or already mapped). The
   dissertation has already, as of the 2026-06-25 amendments (R25/R30/R31), mapped **Eureka's two ablations onto
   its arms** (`w/o Reward Reflection` ↔ scalar arm = H2; `w/o Evolution` ↔ single-shot = H3) — this is the single
   most valuable Eureka-derived framing and it is **already in place**.

4. **Only one Eureka mechanism is worth implementing pre-freeze, and only in a narrow, additive form**
   (§6 P-A): **logging the reward's per-component values and surfacing a one-line "which components were active /
   flat / dominant" diagnostic** — because the reward contract *already returns a `components` dict* that is
   currently logged-but-never-reflected-upon. Verdict: **worth it as a report-only forensic exhibit; NOT worth it
   as a change to the H2 feedback block** (that would break the frozen arm-isolation). Everything else (curriculum,
   GPT-4 swap, HNS, many envs, human-init RLHF, neural critic) is **not worth it** for this thesis.

---

## 1. Eureka, verified first-hand (the reference the write-up needs)

### 1.1 The method — three components (paper §3, Alg. 1)
- **Environment as context (§3.1).** The raw environment **source code** (observation/state variables, *without*
  the reward) is fed to the coding LLM (GPT-4) as context; the LLM zero-shot returns **executable Python reward
  code**. Only generic formatting tips are given (no task-specific templates, no few-shot) — this is the headline
  contrast vs L2R (which needs hand-built motion templates + reward-API primitives). A script trims the env code
  to just the observation block to fit context and avoid leaking simulator internals.
- **Evolutionary search (§3.2).** Per iteration, sample **K i.i.d.** reward candidates from the LLM (K=16). Since
  draws are i.i.d., the probability that *all* are buggy decays exponentially, so K=16 yields ≥1 executable reward
  in iteration 1. The **best** candidate (by fitness) + its reward reflection + a mutation prompt seed the next
  iteration's K draws. **N=5 iterations, 5 independent restarts** per env. History is **Markovian** — only the
  *last reward + its reflection* (plus the system prompt) are kept in context (App. D).
- **Reward reflection (§3.3).** The reward code is *required to expose its individual components in a dictionary*
  (Prompt 3). Reflection is an **automated textual summary of policy training dynamics**: it tracks **the scalar
  values of every reward component AND the task fitness F at intermediate policy checkpoints** throughout training
  — serialized as per-component time-series lists with max/mean/min (verbatim example, App. G.1: e.g.
  `rotation_reward: ['0.03','0.31',...], Max:0.36, Mean:0.32, Min:0.03` + `success_rate: [...]`). The mutation
  prompt (Prompt 2) instructs the LLM to diagnose each component: *near-constant component ⇒ RL can't optimize it
  as written (rescale / rewrite / discard); over-large magnitude ⇒ rescale*. This is what enables **targeted,
  per-component reward editing** rather than blind resampling.

### 1.2 The problem setting and fitness
- Reward design as the **Singh et al. (2010) Reward Design Problem (RDP)** `⟨M, R, π_M, F⟩` specialized to **program
  synthesis** ("reward generation"): output reward *code* `R` maximizing `F(A_M(R))`, the fitness of the policy that
  optimizes `R`. **F is the ground-truth task metric from the simulator** (e.g. duration, distance, success
  indicator) — see the per-env F table (App. B). Crucially, the paper states F **lacks credit assignment as a
  *training* signal** ("provides no useful information on why a reward function works or not") — which is *exactly
  why* reflection feeds component-level dynamics, not just F.

### 1.3 Evaluation, results, ablations
- **Suite:** 29 IsaacGym tasks across 10 robot morphologies (9 Isaac + 20 Bidexterous-Manipulation). Both released
  at/after GPT-4's Sept-2021 cutoff (a deliberate **contamination control** — GPT-4 is "unlikely to have
  accumulated extensive internet knowledge").
- **Metric:** **human-normalized score** `(Method − Sparse) / |Human − Sparse|` for Isaac (clipped to [0,3] before
  averaging); success rate for Dexterity. Each final reward = 5 PPO runs, max over 10 checkpoints; intermediate
  rewards = 1 PPO run.
- **Headline:** beats human experts on **83%** of 29 tasks; **+52%** average normalized improvement. App. F reports
  **IQM, probability-of-improvement, stratified-bootstrap 95% CIs (rliable; Agarwal et al. 2021)** — Eureka itself
  used rliable.
- **Ablation 1 — w/o Evolution (32 samples).** Sample 2 iterations' worth of rewards in *one* generation, no
  iteration. Result: does **not** match Eureka-after-2-iterations → evolution is indispensable (not replaceable by
  more first-shot samples).
- **Ablation 2 — w/o Reward Reflection.** Reduce feedback to **only the task-metric F snapshots** (no per-component
  trajectories). Result: **−28.6%** average normalized score, with *greater* loss on high-dimensional tasks → the
  *component-level* reflection is the driver, not the bare fitness number.
- **Novelty / reward-correlation analysis (§4.3, App. F).** Pearson correlation between Eureka and human reward
  *values* over training transitions, plotted vs human-normalized score: Eureka rewards are **weakly (often
  negatively) correlated** with human rewards yet **outperform** them; harder/higher-dim tasks → *lower*
  correlation (more room to differ). This is Eureka's evidence that the LLM finds *novel* reward principles.
- **Extensions (not core):** GPT-3.5 still ≥ human on most Isaac (principle is model-general); **RLHF** via
  human-init (substitute a human reward as iteration-0) and human *textual* reflection; **curriculum learning** for
  pen spinning (pre-train re-orientation → fine-tune waypoint sequence).
- **Compute:** single 8×A100 station; **< 1 day** wall-clock per Eureka run; ≤8GB/RL-run → runnable on 4×V100
  ("readily accessible on an academic compute budget").

---

## 2. This dissertation, mapped onto the Eureka skeleton

| Eureka component | This dissertation (verified) | Where |
|---|---|---|
| Environment as context | System prompt gives the **reward contract** (`reward(weights, returns, prev_weights, port_ret, info) → (total, components, reward_state)`) over **anonymized arrays** — no env source dump, no tickers/dates (structural blinding, N3). | `prompts/system.txt`; `src/llm/loop.py:90` |
| LLM authors reward *code* | Yes — Python source, numpy-only, AST-gated once then run in-process. Author = **Claude Opus 5** (campaign) / Sonnet 4.6 (prototype). | `src/sandbox/executor.py`; `src/llm/loop.py:353,361` |
| Evolutionary search (K i.i.d. per gen, reflect on best, N gens, restarts) | Yes — `generations × candidates_per_gen` (campaign 6×5=30); **reflect-on-best** is the headline protocol (R24); within-gen diversity via per-candidate **prompt-variation directive** (Opus rejects `temperature`). | `src/llm/loop.py:323-348`; `parallel._drive_llm_arm`; PREREG §6/R24 |
| Reward reflection | **Different object (the contribution).** Reflection feeds the **scalar fitness + an off-critic tail block**, NOT the reward's component trajectories. | `src/llm/loop.py::_REFLECTION_PREAMBLE`; `src/feedback/schema.py::build_block` (NOT `prompts/reflection.txt` — dead, never loaded; corrected 2026-07-26, #54) |
| Fitness F | **Held-out validation Deflated Sharpe**, reward-independent (selection cannot be reward-hacked); λ=0 (tail-blind, conservative, Eureka-faithful). | `src/selection/fitness.py::held_out_fitness`; PREREG §5/R22 |
| Many-env eval | **One task** (long-only 30-asset PIT US-equity allocation), 2005–2025, sealed 2018–2025 test leg. | PREREG §7 |
| Reporting | **rliable per-seed IQM paired bootstrap (30 winner seeds) + PBO/CSCV + two co-primary IUTs + FZ0/ES + pre-registered TOST**. | PREREG §10/R16/R25 |
| Reward-correlation novelty probe | **`feedback_responsiveness`** (Spearman: reward-source edit magnitude vs fed tail-stat delta) + **`specification_gaming`** inspector — the off-critic analogue of Eureka's correlation analysis. | `scripts/inspect_rewards.py:246,334` |
| Ablations | **Mapped onto the arms:** `w/o Reward Reflection` ↔ **scalar arm (H2)**; `w/o Evolution (32 samples)` ↔ **single-shot (H3)**. | `docs/DEEP_H3.md` §5.1; FINAL_PLAN §B header |

**The contribution axis (PREREG §2, audit A-1).** All five LLM arms run the **same fixed SB3-SAC agent** and the
same loop machinery; the **only** thing that varies is the serialized feedback block. The tail statistics are
**measured off-critic** from realized portfolio returns by a separate estimator (`measurement.py`), so the channel
is **critic-agnostic** (it reads no Q-network — NOT "agent-independent": the tail is fit on the policy's OWN realized returns under the candidate reward, so H2 compares coupled reward→policy→measurement loops). This is a *cleaner instrument than Eureka's*: Eureka changes the whole reward-design loop
between conditions; this isolates a single text block.

---

## 3. The genuine NOVELTY / differentiators (what this has that Eureka does not)

> These are the claims the write-up should *lead* with. Each is real and first-hand-verifiable on both sides.

**D1 — The feedback OBJECT: realized-return *distribution* vs the reward's own *component* trajectories
(the headline novelty).**
Eureka's reflection is **introspective on the reward**: it reports the scalar time-series of the reward's *own
components* (and F) so the LLM can rescale/rewrite/discard components. This dissertation's reflection is
**extrospective on the outcome**: it reports the **tail of the realized-return distribution** the policy produced
(CVaR at 5/10/25/1%, left-tail mass, robust skew), measured by an **estimator decoupled from the reward's units**.
These are *different kinds of signal*: Eureka closes the loop on "is this reward *trainable* / well-scaled?"; this
closes it on "what *risk shape* did this reward induce?" No Eureka variant (incl. DrEureka, Text2Reward, REvolve)
feeds a return-*distribution* / tail summary. This is N1, and it is the empty cell. *(Framing discipline: call it
**"multi-level tail-risk feedback"**, not "the distribution" — six left-tail scalars, defended as a coherent-risk
spanning basis via Artzner/Acerbi/Kusuoka; `docs/DEEP_FRAMING_discipline.md` §2.)*

**D2 — Fitness with NO oracle: held-out financial metric vs simulator ground-truth.**
Eureka's `F` is the simulator's ground-truth task score — it *exists* and is queryable. Finance has **no such
oracle** (there is no "true" reward for "trade well"). This dissertation replaces F with a **held-out validation
Deflated Sharpe** (Bailey–López de Prado 2014), computed on a *different split* from the fed-back signal and
*independent of the candidate reward's units* so selection cannot be reward-hacked. This is a non-trivial
methodological adaptation — it is what makes the loop *run at all* in a domain without ground truth, and it forces
the entire backtest-overfitting apparatus (PBO/CSCV, DSR, FDR, Harvey-Liu) that Eureka never needed.

**D3 — Inference rigour and a bankable pre-registered null.**
Eureka reports rliable aggregates over 29 envs and declares success at 83%/+52%. This dissertation pre-registers
(before the sealed leg) **two co-primary intersection–union tests** (H2-RA on Sharpe, H2-Tail on CVaR-5%), each
one-sided at α=0.05 with the conjunction *as* the multiplicity correction (Berger 1982), corroborated by an
**FZ0/(VaR,ES) Diebold–Mariano tail backtest** (Fissler–Ziegel 2016; Nolde–Ziegel 2017), with **PBO/CSCV** as the
primary overfitting guard and a **TOST equivalence margin** that turns a non-result into a *bounded, bankable
null*. This is materially more careful than Eureka's evaluation and is itself a contribution (a controlled,
pre-registered study of the reflection mechanism). *In a no-viva, PDF-graded MSc, this is the dominant grade lever.*

**D4 — Domain + contamination mechanism (first for a *trading* agent; N2/N3).**
First Eureka-style reward-code synthesis for a **trading/portfolio** RL agent (narrow wording: a payment-fraud
reward-evolution paper exists, Qu et al. 2025, so the claim is "first for a *trading* agent," not "first in
finance"). And the contamination story is *different from* Eureka's: Eureka relies on a post-cutoff benchmark; this
relies on **structural blinding (anonymized arrays)** + cutoff-stratification + an open-weights second model, plus
the explicit argument that **reward-design contamination ≠ forecasting contamination** (the LLM does not forecast
"2008 crashed"; the risk is rewards implicitly tuned to remembered regimes — and *that* is the object of study,
H4, not a defended weakness).

**D5 — Single-instrument feedback isolation (a methodological upgrade over Eureka's ablation).**
Eureka's `w/o Reward Reflection` ablation changes the feedback *and confounds* it with everything else in that run.
This dissertation isolates the feedback channel to **one text block** at **matched token length** (placebo arm) and
**matched downside-number count** (scalar_cvar5 arm), with the agent, loop, budget, and fitness byte-identical
across arms. The H2 contrast is therefore a *cleaner* test of "does this feedback help" than Eureka's own ablation.

**D6 — A pre-registered controlled counter-point to Eureka's central claim (the H3 result).**
Eureka's headline mechanistic claim is "**evolution / reward-reflection is indispensable**." This dissertation runs
a **matched-budget, identical-selection replication of Eureka's `w/o Evolution` ablation in a new, harder domain**
(sparse financial reward landscape) and pre-commits to the *prediction that reflection will NOT beat best-of-N
here* — grounded in the self-correction-without-a-verifier literature (Huang 2024; Stechly 2023; Olausson 2024) and
test-time-compute scaling (Snell 2024). A confirmed, TOST-bounded **null is a successful risky prediction** and a
rare controlled challenge to the field's dominant narrative — with inference rigour Eureka's ablation lacks
(`docs/DEEP_H3.md` §12).

---

## 4. The GAPS (what Eureka has that this lacks) — with adopt / disclose / irrelevant verdicts

| # | Eureka feature | This dissertation | Verdict | Why |
|---|---|---|---|---|
| **G1** | **29 envs × 10 morphologies** (breadth → external validity) | **1 task** (long-only 30-asset PIT equity) | **DISCLOSE** | Breadth is Eureka's; a single MSc cannot match it, and the contribution is a *mechanism* (feedback channel), not a benchmark sweep. Already scoped as L18 single-instance external-validity (`DEEP_FRAMING` §4; cite Liao 2021 `% VERIFY`). Scope the abstract to *mechanism + method*, not "works on portfolios in general." Adopting more tasks (e.g. a second universe / region) is **future work**, not pre-freeze. |
| **G2** | **Per-component reward reflection** (component scalar trajectories drive targeted edits; the −28.6% ablation shows it is the driver) | Reflection feeds **scalar fitness + off-critic tail block**, NOT component trajectories — even though the reward contract **already returns a `components` dict** that is currently *logged but never reflected upon* | **ADOPT (narrow, additive) + DISCLOSE** | This is the **only substantive, safe Eureka upgrade** (see §6 P-A). It is *deliberately* different on the H2 arms (the contribution is the *outcome-distribution* channel, not Eureka's introspective channel) — so do **not** fold component traces into the H2 feedback block (that breaks arm isolation and the matched-length controls). But (a) **disclose** that this dissertation's reflection is *coarser/terminal* than Eureka's per-component-across-training signal (a design-level reason the H3 null is plausible — `DEEP_H3` §5.2.3), and (b) optionally surface a **report-only** component-activity diagnostic (§6 P-A). |
| **G3** | **Ground-truth fitness F** (simulator oracle) | **Held-out validation DSR** (no oracle) | **IRRELEVANT (it is a differentiator, not a gap)** | Finance has no oracle; the *absence* forced D2, which is a contribution, not a deficiency. Frame as "the finance-forced adaptation," never as "we lack Eureka's F." |
| **G4** | **Curriculum learning** (pen-spinning; task decomposition + pre-train→fine-tune) | None | **IRRELEVANT** | Curriculum is for a *hard motor-skill acquisition* problem; portfolio allocation is a single stationary-ish control task with no natural sub-task decomposition. Out of scope; not a limitation. |
| **G5** | **GPT-4 scale** (gpt-4-0314) + GPT-3.5 robustness check | Claude **Opus 5** (campaign) / Sonnet 4.6 (prototype) | **IRRELEVANT / ALREADY-STRONGER** | Opus 5 is a frontier coding model ≥ GPT-4-0314; the model is a *stronger* author than Eureka's. The "open-weights second model with a different cutoff" (N3) is the analogue of Eureka's GPT-3.5 robustness check, repurposed for *contamination* rather than capability. No gap. |
| **G6** | **Human-normalized score** `(M−Sparse)/|Human−Sparse|` over many tasks | **Eureka-*style* "beat-the-human"** = LLM winner vs best hand-written reward (H1, report-only), on (seed, window) cells | **DISCLOSE (relabel)** | HNS is **not computable single-task** (it needs a cross-task population to normalize/average). H1 is the faithful single-task analogue and is *already* relabelled **"Eureka-style"** (R30; `DEEP_FRAMING` §1.3 safe-phrase: "a direct analogue of Eureka's 83% beat-the-human result"). State explicitly that you report the *analogue*, not HNS. |
| **G7** | **Human-init RLHF + human textual reflection** | None (the reflection is automated only) | **IRRELEVANT** | These are Eureka *extensions* (its §4.4), not its core; they answer "can a human steer it," which is orthogonal to the distributional-feedback question. Out of scope; could be one sentence of future work. |
| **G8** | **GPU-parallel reward evaluation** (IsaacGym, 1000× sim speed; 16 rewards at once) | CPU/single-GPU sequential-ish; parallel SEARCH scheduler added (R21/R24) | **DISCLOSE (it bounds scale, not validity)** | Eureka's GPU sim is *why* it can afford 5×16×5 = 400 evaluations/env across 29 envs. This dissertation's matched-compute is far smaller (30 candidates/arm, seeds-on-winners) — a *scale* limit that bounds breadth (G1), not internal validity. Already handled by the matched-compute design + the rented-4090 plan (ADR-023). No action beyond the compute-accounting table. |
| **G9** | **Component-dict requirement enforced in the prompt** (Prompt 3 mandates the reward expose components) | Contract **requests** `components` (system.txt) but it is **logged-only**, not used | **ADOPT-adjacent (see G2/§6 P-A)** | Same root as G2. The plumbing exists; only the *use* is missing. The minimal adoption is to *use* the already-collected components for a forensic diagnostic, not to mandate anything new of the LLM. |
| **G10** | **Pearson reward-correlation novelty plot** (Eureka vs human reward values; novelty evidence) | `feedback_responsiveness` (edit↔tail-delta) + `specification_gaming`; no reward-vs-baseline correlation plot | **OPTIONAL-ADOPT (low ROI) / DISCLOSE** | A direct analogue — correlating the **LLM winner's per-step reward** with each **hand-written baseline reward** over the test path, plotted vs OOS performance — would be a *novelty exhibit* mirroring Eureka Fig. 6 ("the LLM found a reward weakly/negatively correlated with the hand-designed ones yet superior"). Cheap *if* baseline reward series are already archived. **Verdict: nice-to-have, low grade-ROI, post-freeze report-only** (§6 P-B). |

---

## 5. The strongest defensible "vs Eureka" positioning (the map the write-up needs)

### 5.1 The one-paragraph positioning (drop-in seed for the Introduction / Related Work)
> *Our system adopts the Eureka loop (Ma et al., 2024) — an LLM, given the task interface, authors executable
> reward-function code; a fixed RL agent is trained; the results are summarized back to the LLM, which revises;
> candidates are selected by an evolutionary fitness — but specializes it in three ways that the finance domain
> forces and that constitute our contribution. **First**, Eureka's reward reflection reports the reward's own
> per-component scalar trajectories to diagnose trainability; we instead feed the **realized-return tail
> distribution** (multi-level CVaR, left-tail mass, robust skew), measured by an estimator decoupled from the
> reward, so the loop is closed on the *risk shape the policy induced* rather than on the reward's internal
> scaling. **Second**, Eureka's fitness is a simulator ground-truth oracle, which finance does not provide; ours
> is a **held-out validation Deflated Sharpe**, computed on a separate split and independent of the candidate
> reward's units, so winner selection cannot be reward-hacked. **Third**, where Eureka evaluates breadth (83% of 29
> robotics tasks beat human experts) with rliable aggregates, we evaluate a single task with a **pre-registered,
> per-seed intersection–union inference** (two co-primary tests on risk-adjusted performance and on the realized
> tail, with PBO/CSCV, an FZ0/ES tail backtest, and a TOST equivalence bound), so a null is a calibrated finding
> rather than a failed search. The machinery is Eureka's; the **distributional feedback channel**, the
> **oracle-free held-out fitness**, the **trading domain** (a first for a trading agent), and the **inferential
> discipline** are ours.*

### 5.2 The differentiator / gap table (compress into one Methodology table)

| Axis | Eureka (Ma et al. 2024) | This dissertation | Type |
|---|---|---|---|
| Reward authored as code by an LLM | ✔ (GPT-4) | ✔ (Claude Opus 5) | **shared (lineage)** |
| Environment as context | env source code | reward contract + anonymized arrays (blinded) | shared, adapted (contamination) |
| Evolutionary search, reflect-on-best, restarts | ✔ (N=5, K=16, 5 restarts) | ✔ (6×5; reflect-on-best; matched budget) | **shared** |
| **Feedback object** | reward's per-component scalar trajectories + F | **realized-return tail distribution, off-critic** | **DIFFERENTIATOR (N1)** |
| **Fitness** | simulator ground-truth oracle F | **held-out validation Deflated Sharpe** (no oracle) | **DIFFERENTIATOR** |
| Domain | robotics (dexterity/locomotion) | **risk-sensitive long-only portfolio** | **DIFFERENTIATOR (N2)** |
| Contamination control | post-cutoff benchmark | structural blinding + cutoff-strat + 2nd model | **DIFFERENTIATOR (N3)** |
| Evaluation | 29 envs, human-normalized, rliable | 1 task, **pre-registered 2 co-primary IUTs + PBO + FZ0/ES + TOST** | **DIFFERENTIATOR (rigour)** |
| Reward-reflection ablation | `w/o Reward Reflection` (−28.6%) | **= the scalar arm (H2)**, isolated to one text block | shared idea, **cleaner instrument** |
| Evolution ablation | `w/o Evolution (32 samples)` | **= single-shot (H3)**, matched budget + TOST | shared idea, **+ bankable null** |
| Novelty/correlation analysis | Pearson reward-vs-human plot | `feedback_responsiveness` + `specification_gaming` | shared idea, off-critic analogue |
| Breadth (envs) | ✔✔✔ (GPU sim) | ✘ (single task) | **GAP → disclosed (L18)** |
| Per-component reflection | ✔ (the driver) | ✘ on arms (logged-only) | **GAP → narrow adopt (§6 P-A) + disclose** |
| Curriculum / human-RLHF | ✔ (extensions) | ✘ | **GAP → irrelevant / future work** |

### 5.3 The two anticipated "vs Eureka" examiner questions + the answers
- **"Isn't this just Eureka in a new domain?"** → The *loop* is Eureka; the *contribution* is the **distributional
  feedback channel** (a different feedback object, not in any Eureka variant), the **oracle-free held-out fitness**
  (forced by finance, not present in Eureka), and an **inference stack + pre-registered null** that exceed Eureka's
  rigour. We *also* contribute a **controlled replication of Eureka's evolution ablation** (H3) that does **not**
  reproduce its "evolution is indispensable" finding in this harder domain — a result, not a re-run.
- **"Eureka beats humans 83% of the time — what's your equivalent, and did you?"** → HNS is not single-task
  computable; the faithful analogue is **H1 (Eureka-style beat-the-human)** — LLM winner vs the best hand-written
  reward on (seed, window) cells, reported descriptively (subordinate to H2; `DEEP_FRAMING` §1.3). We report the
  *analogue* and disclose it is not HNS.

---

## 6. PRIORITIZED implementable Eureka mechanisms (grade-ROI · pre-freeze risk · verdict)

> Conservative by mandate: the design is freeze-ready/green. Each item states whether it is genuinely safe and
> high-value. Only **P-A** is recommended for pre-freeze action, and only in its narrow additive form.

### P-A — Surface the reward's per-component activity as a REPORT-ONLY forensic diagnostic  ★ recommended (narrow)
- **What (Eureka §3.3 + Prompt 3).** Eureka's biggest single mechanistic finding is that **per-component reward
  reflection** drives the gains (−28.6% without it). This dissertation's reward contract **already returns a
  `components` dict** (`prompts/system.txt`; FINAL_PLAN §B reward/contract.py "scalar total + components +
  reward_state"), but it is **logged-only and never used** — neither reflected upon nor analyzed. The minimal,
  safe adoption is to **aggregate the already-collected per-component values** for the winner over the test path
  into a short table/figure ("which authored components were *active* / *near-constant* / *magnitude-dominant*"),
  exactly the diagnostic axis Eureka's reflection prompt reasons over — as a **report-only interpretability
  exhibit**, NOT as a change to the H2 feedback block.
- **Grade-ROI:** **Medium-high.** (i) It is a *direct, concrete* Eureka tie ("we instrument the same per-component
  signal Eureka reflects on, and report it") that strengthens the Related-Work positioning and the interpretability
  story; (ii) it **explains the H3 null** mechanistically — a flat/inactive component profile corroborates "the
  feedback left no targeted-edit signature" (`DEEP_H3` §5.2.3 already wants this); (iii) it supports the
  reward-hacking inspection (Skalse/Pan/Hadfield-Menell) the design already promises (`specification_gaming`). Low
  cost: the data is already archived per candidate.
- **Pre-freeze risk:** **Low** — *iff* it stays report-only and does **not** enter the reflection prompt or any
  arm's feedback block. **Hard constraint:** putting component traces into the feedback would (a) break the
  matched-length / matched-downside-number arm-isolation controls (C-a/C-b in `DEEP_H2` §1.3), (b) change a frozen
  pre-registration item (§2 contribution axis), and (c) re-introduce the very Eureka-channel the design
  *deliberately replaced* — so it must be a **post-hoc analysis artifact only**. Confirm the components are
  actually persisted per step at the resolution needed (the contract returns them per call; verify the env/results
  IO retains them — if only the winner's path is needed, this is a small `analyze`/`inspect_rewards` addition, not
  a campaign change).
- **Verdict: WORTH IT** as a report-only diagnostic + a one-paragraph disclosure that this dissertation's
  *reflection* is intentionally outcome-distributional (not Eureka's introspective per-component channel).
  **NOT worth it** — indeed unsafe — to feed components into the loop. *(If retention is not already wired and
  would require a campaign re-run, downgrade to "future work" rather than touch the frozen run.)*

### P-B — Eureka-style reward-vs-baseline correlation novelty plot  ☆ optional, low ROI
- **What (Eureka §4.3 / Fig. 6).** Correlate the **LLM winner's per-step reward** with each **hand-written baseline
  reward** over the (test or train) path and plot vs OOS performance, to evidence that the LLM found a reward
  **weakly/negatively correlated** with the hand-designed ones yet superior — the off-policy analogue of Eureka's
  novelty claim. This complements the existing `feedback_responsiveness` probe (which is about *edit-tracking*, a
  different question).
- **Grade-ROI:** **Low–medium.** A clean, citable "our LLM reward is novel relative to the canon (Eureka-style
  correlation analysis)" exhibit. But it requires relabelling all candidate rewards' per-step values against the 9
  `REWARD_CANON` baselines and is a *secondary novelty* point the thesis can make in prose without the figure.
- **Pre-freeze risk:** **Low** (report-only, post-freeze, no frozen item touched) — *if* the baseline reward
  per-step series are archived; if not, it needs a re-evaluation pass.
- **Verdict: NOT WORTH IT pre-freeze; optional post-freeze report-only.** Make the *claim* in prose ("the winner's
  reward correlates weakly with the hand-designed canon — cf. Eureka §4.3"); produce the figure only if the series
  exist and time permits.

### P-C — Mandate a structured component dict / Eureka-style mutation tips in the prompt  ✗ reject
- **What.** Eureka's Prompt 2 gives explicit per-component mutation heuristics (constant ⇒ rescale/rewrite/discard;
  over-large ⇒ rescale) and Prompt 3 *mandates* the component dict. One could import these verbatim.
- **Verdict: NOT WORTH IT / REJECT.** (i) The reflection prompt is part of the **frozen** arm-isolation design;
  importing component-mutation tips would inject Eureka's *introspective* signal into the loop and confound H2.
  (ii) Opus 5 already authors competent multi-term rewards under the existing contract (prototype ran to
  completion). (iii) This is the exact "urge to add scope = stop and flag" trigger (CLAUDE.md directive 2). Cite
  Eureka's prompts as *prior art the design adapts*, do not adopt them into the live loop.

### P-D — Curriculum learning  ✗ reject (irrelevant)  ·  P-E — neural distributional critic in the loop  ✗ reject
- **Curriculum:** no natural sub-task decomposition for single-task allocation; out of scope (G4).
- **Neural critic in the feedback:** explicitly rejected by the audit (A-1/A-2): the headline feedback is **measured
  off-critic** by an empirical+EVT estimator; the distributional *critic* (TQC) is a **named secondary** experiment,
  not the contribution. Re-introducing an IQN-style critic into the feedback path is the abandoned B-line (ADR-022).
  **REJECT.**

### Summary verdict table

| Mechanism | Grade-ROI | Pre-freeze risk | Verdict |
|---|---|---|---|
| **P-A** per-component activity, **report-only** | Medium-high | Low (iff report-only) | **WORTH IT (narrow)** |
| **P-B** reward-vs-baseline correlation plot | Low–medium | Low | Optional, post-freeze |
| **P-C** component-mandate / mutation tips in prompt | (would confound H2) | **High** (breaks frozen isolation) | **REJECT** |
| **P-D** curriculum learning | n/a | n/a | **REJECT (irrelevant)** |
| **P-E** neural critic in feedback path | n/a | High (re-opens abandoned line) | **REJECT** |

---

## 7. What is ALREADY done well (do not re-litigate)
- **Eureka ablation → arm mapping** is already in place (R25/R30; `DEEP_H3` §5.1): scalar arm = `w/o Reward
  Reflection`; single-shot/H3 = `w/o Evolution`. This is the highest-value Eureka framing and needs no further work.
- **rliable reporting** (Eureka used it too) is the inference backbone (R16) — cite Agarwal et al. 2021 and note
  the shared lineage.
- **Reflect-on-best** (R24) is Eureka-faithful (Eureka reflects on best-so-far, Alg. 1 line 9) — defend λ=0 +
  reflect-on-best as *Eureka-faithful*, not an oversight (`DEEP_H2` §9 makes this point).
- **`feedback_responsiveness` / `specification_gaming`** are the off-critic analogues of Eureka's correlation +
  reward-hacking analyses and are correctly labelled DIRECTIONAL/forensic.
- **Construct retitle** ("multi-level tail-risk feedback") and **no-SOTA discipline** (`DEEP_FRAMING`) already
  pre-empt the two easiest attacks on the contribution.

---

## 8. Action checklist (for the maintainer — minimal, conservative)
1. **[report-only, recommended]** P-A: add a winner per-component activity table/figure to the analysis/inspection
   output; confirm components are persisted per step (if not already, scope as future work — do **not** re-run the
   campaign for it). Add the one-paragraph disclosure that the *reflection* is intentionally outcome-distributional,
   not Eureka's per-component channel.
2. **[prose only]** Insert the §5.1 positioning paragraph and the §5.2 table into Related Work / Methodology; state
   the HNS-vs-H1 relabel (G6) and the breadth disclosure (G1/L18).
3. **[prose only]** In the H3 discussion, cite Eureka's two ablations explicitly as the precedent the arms map onto
   (already supported by `DEEP_H3`), and disclose the *coarser-than-Eureka* (terminal vs per-component-across-
   training) feedback as a design-level reason the H3 null is expected.
4. **[optional, post-freeze]** P-B reward-vs-baseline correlation figure, only if baseline per-step series exist.
5. **[do NOT]** Touch the reflection prompt / feedback block to add components (P-C), add curriculum (P-D), or
   re-introduce a neural critic into the feedback path (P-E).

---

### Appendix — first-hand source index
- **Eureka:** `D:\tmp\littxt\00_core_pillars__Eureka__2310.12931.txt` — method §3 (lines ~117–236), Alg. 1
  (~138–166), reward reflection §3.3 (~216–236), prompts App. A (~740–795), reflection examples App. G.1
  (~1730–1965), ablations §4.3 (~316–364) + App. F (~1687–1722), correlation analysis (~1707–1722), HNS (~290–295,
  ~1235–1238), compute App. D.4 (~1291–1296). Cross-checked against `docs/notes/eureka.md`.
- **Dissertation:** `PREREGISTRATION.md` (§1/§2/§3/§5/§6/§10; amendments R16/R22/R24/R25/R30/R31);
  `00_planning/FINAL_PLAN_FOR_CLAUDE_CODE_DETAILED.md` §B.3–B.10; `prompts/system.txt`, `prompts/reflection.txt`;
  `src/llm/loop.py` (reflection gating 333–336/450; feedback block 400–403; component dict in contract not fed);
  `src/feedback/schema.py`, `src/feedback/measurement.py`; `scripts/inspect_rewards.py`
  (`feedback_responsiveness` 246–320, `specification_gaming` 334–372); `docs/DEEP_H2.md`, `docs/DEEP_H3.md`,
  `docs/distributional_feedback_schema.md`, `docs/DEEP_FRAMING_discipline.md`.
- Literature not re-verified here (Acerbi 2002, Kusuoka 2001, Liao 2021, the H3 self-correction cluster) is marked
  `% VERIFY` per CLAUDE.md directive 4; the Eureka claims above are first-hand.
