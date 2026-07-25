# The Dissertation — Complete Reference Brief

**For:** the supervision meeting with Dr Ramin Okhrati (and any cold reader) · **Regenerated:** 2026-07-23 · **Status:** design **v2, UNFROZEN by standing policy (R94)** — the freeze executes together with the full-campaign approval (GO step 1), never before; campaign **not launched**; pre-launch gates **not run**.

> **Currency banner (2026-07-23).** This text was **regenerated on 2026-07-23 and supersedes the
> 2026-07-21 version**; every load-bearing fact below was re-verified against the live repo files
> (`PREREGISTRATION.md` incl. rows R78–R99 · `config/preregistration.yaml` / `legs.yaml` /
> `m2_models.yaml` · `docs/HANDOFF.md` · `docs/MODEL_ROSTER_2026-07-22.md` ·
> `docs/CAMPAIGN_DAY_RUNBOOK_2026-07-13.md` §2.0/§9/§10 · `docs/V2_WRITE_TIME_REGISTRY.md` rows
> 1–32 · `paper/APPENDIX_B_limitations.md` · `CHANGELOG.md`). Headline deltas since 07-21:
> **TEN replication legs / 11 full-loop models** (R95 seated Kimi K3), amendments through **R99**,
> the hand-written reward canon is **ten names** (R97), the M2 survey is **26 core + 9 extras = 35
> models** (R99 seated GPT-5.6 Terra), the canonical hash is **recomputed at the GO-day freeze**
> (the R93 `ccf2e76f` stamp is history), and execution is **mode D** (12 supervised launch lines).

> **What this document is.** A single, faithful, end-to-end reference to *everything* in the dissertation — the question, the theory, the experiment, every arm, every hypothesis, the statistics, the seed/tier ladder, the v2 multi-model design, the mechanism study, the execution design, the money, the timeline, the limitations, and the grade strategy. Every load-bearing statement is drawn verbatim from the configs, the pre-registration, and the paper chapters; anything the campaign must supply is marked **[FROM CAMPAIGN]**, never invented. Where two source docs disagree, the disagreement is flagged, not hidden.
>
> It is written *intuition-first, machinery-second* on purpose — that is both how Dr Okhrati grades and the fastest way to talk through it in a meeting.

---

> **Model-currency note.** The confirmatory author is **Claude Opus 5** (dateless-immutable id,
> retirement floor + Anthropic's weight-preservation commitment — the best deprecation posture in
> the roster). It succeeded **Claude Opus 4.8** in this seat pre-launch under amendment **R102**
> (2026-07-25), when Opus 5 reached GA: same safety classifiers, tokenizer and $5/$25 price as 4.8,
> so no new identification threat and the budget is unchanged; Opus 4.8 is retained as the M2
> generation-pair partner. Separately, Anthropic's **Fable 5** (9 June 2026) — a different model —
> was analysed as an author and **declined** (its dual-use classifiers with mid-response fallback
> are a treatment-correlated interference channel, and the June government-directive suspension
> contradicts the permanence claim); Fable 5 sits in the M2 reading survey only, where refusals are
> data. Disclosed in CH4.

## Table of contents

1. [The study in one page](#1-the-study-in-one-page)
2. [Numbers cheat-sheet](#2-numbers-cheat-sheet)
3. [Research question and the three sub-questions](#3-research-question-and-the-three-sub-questions)
4. [The four contributions](#4-the-four-contributions)
5. [The theory spine (Chapter 3)](#5-the-theory-spine-chapter-3)
6. [The identification principle](#6-the-identification-principle)
7. [The experiment: agent, environment, data](#7-the-experiment-agent-environment-data)
8. [The seven arms](#8-the-seven-arms)
9. [The fed tail vector — the contribution's core object](#9-the-fed-tail-vector)
10. [The LLM authoring loop, sandbox, and selection](#10-the-llm-authoring-loop-sandbox-and-selection)
11. [The four hypotheses (and the ten-name human reward canon)](#11-the-four-hypotheses)
12. [H2 in depth — the headline test](#12-h2-in-depth-the-headline-test)
13. [Equivalence, TOST, and the "bankable null"](#13-equivalence-tost-and-the-bankable-null)
14. [The seed / assurance-tier ladder](#14-the-seed--assurance-tier-ladder)
15. [The v2 multi-model design (10 legs · 11 full-loop models · the money)](#15-the-v2-multi-model-design)
16. [Tiers · stages · rungs (incl. the R96 optional module)](#16-tiers--stages--rungs)
17. [The mechanism kernel — the intellectual headline](#17-the-mechanism-kernel)
18. [The full statistics stack](#18-the-full-statistics-stack)
19. [Pre-registration, the amendment ledger, and the verification state](#19-pre-registration-and-integrity)
20. [Execution: the GO sequence, mode D, and the timeline](#20-execution-timeline)
21. [The four-paper map](#21-the-four-paper-map)
22. [Limitations and threats to validity](#22-limitations-and-threats-to-validity)
23. [Grade strategy, the raised bar, and examiner alignment](#23-grade-strategy-and-examiner-alignment)
24. [Anticipated questions and how the design answers them](#24-anticipated-questions-and-how-the-design-answers-them)
25. [Glossary](#25-glossary)

---

## 1. The study in one page

**The one-sentence thesis.** *When a language model writes the reward-function **code** for a trading agent, does showing it the **downside** — the lower tail of realized returns (conditional value-at-risk at several levels, left-tail mass, skew), measured off the critic — change the code it writes, and does that change propagate to the trained agent's realized tail behaviour?*

**Why this is the question.** When we ask an AI to write software that pursues a goal, the goal has to be written down as a *score* the software optimises. In investing, the score that matters most captures rare, catastrophic losses — not average performance. The dissertation asks whether **showing the AI detailed information about those rare losses changes the score it writes.** Everything else — the market data, the learning algorithm, the compute budget, the prompts — is held identical across conditions, and every prediction and decision rule was registered in advance, so the result cannot be reshaped after the fact.

**The shape of the finding.** The design is built to deliver a **bankable result of either sign**. The registered *prediction* (from the theory and the directional pilot) is a **null**: at matched compute, with a fixed agent, tail feedback does **not** detectably beat scalar feedback — and, crucially, the mechanism study **locates where the causal chain breaks**. A null here is not a failure to find something; it is a *corroborated prediction about the gap between an information-theoretic ideal and its bounded realisation.* That is the intellectual payoff, and it is what makes the null a Distinction-grade result rather than a dead end.

**The spine is a three-link causal chain:**

```
   fed tail signal  ──(SQ1)──►  authored reward CODE  ──(SQ2)──►  trained policy ──► realized tail outcome
   (does the signal        (does the code                (does the behaviour
    move the code?)         move the outcome?)             show the effect?)
                         SQ3: is any effect genuine use of the tail CONTENT, or a surface echo?
```

**The v2 breadth around the frozen core.** One frontier model (Opus 5) answers the confirmatory question under full rigor; **ten replication legs** (five open-weight with hash-pinned checkpoints, five closed, ≥6 vendors) answer *"is it general?"* at the 30-seed floor; a **35-model M2 reading survey** answers *"can models read the numbers at all?"*; and three controlled instruments (two capability pairs + a generation pair) turn model differences into identified contrasts instead of anecdotes. Nothing in the breadth layer gates the confirmatory verdicts.

**The recommended title.** *"Does Showing a Language Model the Downside Change the Reward Code It Writes? A Pre-Registered, Off-Critic Test in Risk-Sensitive Portfolio RL."*

---

## 2. Numbers cheat-sheet

| Thing | Value |
|---|---|
| **Assets** | Top **30** US large-caps by point-in-time market cap, + cash |
| **Data panel** | Refinitiv/LSEG, survivorship-free, PIT — **963 securities × 5,406 trading days**, 2005-01-03 → 2026-06-30 (`univ5`) |
| **Splits (Split C)** | Train **2005–2016** · Validation **2017–2019** · Test (sealed) **2020–2026 H1** |
| **Purge / embargo** | Effective purge **60 sessions** at each split boundary (embargo floor 21, raised to cover the 60-day lookback) |
| **Agent** | Stable-Baselines3 **SAC**, held byte-identically fixed across arms |
| **Training budget B\*** | **400,000** environment steps per candidate (R77 — the measured learning-curve knee; *never* 200k, which R74 set and R77 superseded) |
| **Arms** | **7** (5 LLM feedback arms + 2 non-LLM search baselines) |
| **Candidate budget** | **30** per arm = **6 generations × 5 candidates**, reflect-on-best |
| **Fed tail vector** | **6** left-tail scalars (CVaR at 1/5/10/25%, left-tail mass, robust skew) |
| **Confirmatory author** | **Claude Opus 5** (the single frontier model; R102, was Opus 4.8) |
| **v2 replication legs** | **10** legs → **11 full-loop models** (R95; queue: deepseek → glm → qwen27 → qwen9 → haiku → luna → nemotron → sonnet-5 → gemini → kimi-k3) |
| **M2 reading survey** | **26 core + 9 extras = 35 models** (R99 seated gpt-5.6-terra; 3 documented config exclusions) |
| **Hand-written reward canon** | **10 names** (H1's four frozen + the six-member secondary panel incl. R97's `differential_downside_ratio`) |
| **SESOI** | **0.05** (validation deflated-Sharpe units); symmetric TOST margin ±0.05 |
| **Seed ladder** | **[30, 100, 189, 279, 340, 403, 568]**; registered primary target **403** (95% equivalence assurance) |
| **Headline pilot dispersion** | σ_seed ≈ **0.244**, σ_D ≈ **0.369**, ρ ≈ **−0.141** (Sharpe/DSR leg) — this is what forces the large seed count |
| **Spend** | **$30 advisory** planning ceiling (R83 — tracked and warned, never refuses) · whole study expected **~$28** |
| **Freeze policy** | **R94**: the freeze executes together with Tamer's full-campaign approval (GO step 1), never before; the hash is **recomputed at GO** (`ccf2e76f` = R93 history) |
| **Execution** | **Mode D** (R88): 12 supervised launch lines; floor ~L+1.5–1.8 · legs ~L+4.5–5.5 · tier-403 ~L+13–14.5 |
| **Leg calendar gate** | **2026-08-14T23:59Z** (exact; legs truncate — never reorder — there) |
| **Verification state** | Freeze gate **21 checks OK** · **15 full-suite certifications exit 0** · 5-auditor final sweep fully discharged (§19c) |
| **Submission** | Target **28–29 Aug**, deadline **1 Sep 2026** |

---

## 3. Research question and the three sub-questions

**Main research question (verbatim, CH1):**
> *"when a language model writes the reward code for a trading agent, does showing it the tail of the realised outcome distribution — rather than a single score — change the code it writes, and does any change reach the agent's realised risk?"*

Rather than ask the blunt "does richer feedback help?", the study decomposes the question into a **three-link causal chain** with three pre-specified sub-questions:

- **SQ1 — Responsiveness:** *does the fed signal move the code?* (fed tail signal → authored reward code)
- **SQ2 — Transmission:** *does the code move the outcome?* (authored code → trained policy → realized tail)
- **SQ3 — Specificity:** *is any effect genuine **use** of the tail content, or a surface echo — and is any failure a numeric-legibility bottleneck?*

This is the design's originality: it does not merely test *whether* the channel works, it instruments *where it acts or breaks*. A null becomes a **located** finding, not an absence of evidence.

---

## 4. The four contributions

None of the four is contingent on a positive empirical result — they stand whichever way the data fall. **C4 (mechanism) is the foregrounded headline; C1–C3 are the machinery that make it credible.** The examiner-shorthand is **instrument / protocol / theory envelope / mechanism audit.**

- **C1 — An off-critic feedback instrument that isolates the feedback *content*.** Feeds the reward-designer the realized-return lower tail (CVaR at multiple levels, left-tail mass, robust skew) measured *off the critic* (reads no value network), while the RL agent is held **byte-identically fixed** across arms. Three-way decoupled: *fed* on the training split, *selected* on a tail-blind validation criterion, *tested* on empirical CVaR over a sealed test split. Honest about endogeneity (below).

- **C2 — A pre-registered comparative protocol yielding a bankable result of either sign.** Cryptographically frozen design; intersection-union testing; placebo and structure-shuffled controls; deflated Sharpe ratios and backtest-overfitting probabilities. A non-rejection is reported as a **bounded equivalence** (or a calibrated **inconclusive** when the minimum detectable effect exceeds the SESOI) — *never as an underpowered failure.*

- **C3 — A decision-theoretic envelope delimiting when richer feedback *can* help.** Proves an optimal user of the tail vector **weakly dominates** an optimal user of the scalar (Blackwell sufficiency + a Le Cam-deficiency bound); that the fed vector is a **sufficient and jointly elicitable** representation of the coherent-risk class; and that feeding the tail is, by duality, feeding a **distributional-robustness** signal. Then states the conditions under which a *bounded* system attains the envelope — and, in v2, extends to the **g(capability)** bridge: the envelope binds *every* author, and the leg suite measures the realized distance to it along the capability axis.

- **C4 — A mechanism characterisation that *locates* where the channel acts (the headline).** A pre-specified, report-only decomposition of *fed tail → authored code → policy → realized tail* into responsiveness / transmission / specificity, plus the first **factorial dissection of the feedback channel** in automated reward design (the main arms vary the feedback *content*; the legibility ablation varies its *encoding*; the leg suite varies the *author*). This turns a null into a *located* finding.

---

## 5. The theory spine (Chapter 3)

The theory chapter is where a probabilist examiner will look hardest. It runs in four steps: (§3.2) the optimal-reward problem; (§3.3–3.4) Blackwell dominance + Le Cam deficiency; (§3.5–3.6) sufficiency / elicitability + CVaR–robustness duality; (§3.7) the conditions under which the realised system attains the envelope, with the pre-registered prediction table.

**Sign convention (used throughout, stated in a Conventions box).** Returns *Z* are **signed** — gains positive, losses negative — so the lower tail is the *adverse* direction and
CVaR_α(Z) = min over ξ ∈ 𝒰_α of E_ξ[Z] is a (low, typically negative) return: **a more negative CVaR is worse.** The mirror loss convention ℓ = −Z (under which CVaR is a positive loss and the Rockafellar–Uryasev dual is a max) is used only in §3.6.

**The garbling fact.** Two experiments are fed to the designer: E_vec emits the multi-level tail vector; E_scalar emits a scalar s = g(vector). The identity **E_scalar = g ∘ E_vec** makes the scalar a *garbling* of the vector — and specifically a **deterministic** one: a noise-free coarsening that collapses the *k* tail coordinates onto one. (This is not "adding noise" — it is the degenerate, noise-free limit of Blackwell post-processing.)

**Theorem 3.1 (Blackwell–Sherman–Stein).** For experiments on the same parameter space, the following are equivalent: (i) E′ is a garbling of E; (ii) Risk(E) ≤ Risk(E′) for *every* bounded loss and prior; (iii) ∫v d(Eπ) ≥ ∫v d(E′π) for every convex v. The decision problem is a (loss, prior) pair with ‖L‖∞ ≤ 1, and the designer maximises the objective U = −L — so "lower Bayes risk" and "higher expected objective" are one statement.

**Proposition 3.2 (Dominance of tail feedback).** For every bounded loss L and prior π,
**Risk(E_vec) ≤ Risk(E_scalar).** An optimal designer given the tail vector attains weakly higher expected objective than one given the scalar, uniformly over losses and priors.

**Corollary 3.3 (Worst-case price of the scalar — Le Cam deficiency).** The excess Bayes risk of the scalar over the vector is at most the deficiency **δ(E_scalar, E_vec)**, which is **strictly positive** whenever the tail levels carry information about the parameter that the scalar does not.
> **⚠ Examiner-critical (and verified correct in the current text):** the operative deficiency is **δ(scalar, vec) > 0** — the deficiency *of the scalar relative to the vector* — with the standard Le Cam/Torgersen orientation in which the *first* argument is the garbled experiment. This is the historically bug-prone line (it was once mistyped as the wrong-direction, identically-zero δ(vec, scalar)); it is now internally consistent. It is the single highest-value spot for a probabilist to re-check.

**Data-processing-inequality form.** Treating g as a channel, D_f(g#P ‖ g#Q) ≤ D_f(P ‖ Q) for every f-divergence, with equality (for *strictly convex* f and finite divergence) iff g is sufficient for the {P, Q} dichotomy. Blackwell dominance ⇔ domination in *every* f-divergence simultaneously. "§3.4 is one theorem told in two languages."

**The load-bearing caveat (why the theory does not over-claim).** Proposition 3.2 concerns *information structures* and *optimal Bayes users*; our realised system is neither. It therefore **upper-bounds the attainable improvement — it does not assert the realised pipeline exhibits any.** Three disclosed gaps: (a) the realised scalar is computed on a *different sample* than the training-split vector (split-mismatch, so the garbling diagram commutes only approximately); (b) the realised comparator is a **Deflated Sharpe ratio**, which embeds skewness/kurtosis and is therefore *not perfectly tail-blind* — biasing **against** a measured distributional advantage; (c) the fed vector is re-measured on the trained policy's own returns each generation (**endogenous**), not a fixed exogenous Blackwell experiment. Conditional-on-parameter dominance survives; only the closedness idealisation is relaxed.

**Sufficiency and elicitability (§3.5).**
- **Kusuoka spanning:** every law-invariant *coherent* risk measure is a supremum over mixtures of CVaR across levels; every *comonotonic* one is a single such mixture (a spectral measure). So a CVaR profile across α is a discretisation of the canonical coordinate system for the whole coherent-risk class — the channel transmits a *basis* sufficient to evaluate any of them, which a scalar Sharpe cannot carry. The discrete spectral estimator is coherent at every sample size (Acerbi 2002).
- **Elicitability:** CVaR alone is **not** elicitable (Gneiting 2011); expectiles are the only elicitable law-invariant coherent measures as scalars. The escape is *higher-order joint* elicitability: the pair **(VaR_α, CVaR_α) is jointly elicitable** (Fissler–Ziegel FZ0, with the published correction), and a multi-level spectral measure *together with its quantiles* is jointly elicitable of finite order.
- **Two properties, kept apart:** the vector is sufficient *relative to the scalar* (the garbling fact) — **not** an absolute sufficiency claim for the full return law (six scalars do not deliver that); and, independently, the CVaR sub-vector with its quantiles is jointly elicitable. "The scalar is neither sufficient relative to the vector nor a coherent elicitable target."

**CVaR as a distributional-robustness signal (§3.6).** Dual representation:
CVaR_α(Z) = min over ξ ∈ 𝒰_α of E_ξ[Z], 𝒰_α = {ξ = dQ/dP ≥ 0 : ξ ≤ 1/α, E_P[ξ] = 1}. The ambiguity set is an L^∞ (sup-norm) constraint on the density — *distinct* from a φ-divergence (KL, χ²) ball. Optimising CVaR = best worst-case expected return under a **budgeted perturbation of the data-generating process**. Testable corollary: if tail feedback helps, its benefit should be **concentrated where the distribution shifts** — which motivates the regime-conditional analysis (the sealed test window 2020–2026 straddles the COVID-era regime change).

**The mechanism conditions (§3.7) and the pre-registered prediction table.** The envelope is realised only if three conditions all hold:
1. **Selection sensitivity** — but the selector is *tail-blind by pre-registration* (validation DSR, λ = 0), so it gives no between-arm advantage to tail-aware rewards; any tail benefit must arise *endogenously* from the designer's use of the fed signal. (A deliberately conservative choice.)
2. **Designer responsiveness** — the LM must actually condition the reward code on the fed tail content.
3. **Agent attainability** — even a tail-aware reward helps only if the bounded SAC agent converts it into tail-protective behaviour. A mean-critic maximises the *expectation* of the reward, and a static CVaR penalty is **time-inconsistent**; static-CVaR optimality requires state augmentation with a running VaR level and the optimal policy is in general **non-Markovian**. So the **null branch is "over-determined"** — it can fail at the agent stage independent of responsiveness.

| Mechanism condition | H2-RA (Sharpe) | H2-Tail (CVaR-5%) | Responsiveness | Reward-program differential | Verdict |
|---|---|---|---|---|---|
| **Strict** — fed tail shapes the code | tie (λ=0 ⇒ no Sharpe edge) | dist > {scalar, placebo, scalar_cvar5} reject | > 0 | dist references tail stats more | H2-Tail supported, H2-RA not |
| **Weak** — helps but not robustly | tie | partial (≤2 legs) | ≈ 0 | weak / mixed | inconclusive (TOST-bounded) |
| **Null** — LLM not a Bayes-responsive user | tie | tie (placebo not beaten) | ≤ 0 | no cross-arm signature | **both null (clean, bankable)** |

**The registered prediction is the Null branch** — the directional prototype showed *negative* responsiveness and a tail differential that reversed under placebo (the Null signature). A confirmed Null is framed as *"a corroborated prediction about the gap between the information-theoretic envelope and its bounded realisation."*

**The v2 theory bridge (registered).** The capability gradient **traces the envelope–realization gap as a function of author capability, g(capability)**: the Blackwell envelope binds every user; the leg suite measures the realized distance to it along the capability axis; the numeracy bottleneck is the registered hypothesized *shape* of g (flat at ≈ 0 — see §15's three rival signatures). CH3/CH7 carry the paragraphs (write-time registry row 1).

---

## 6. The identification principle

**Only the reward may vary across arms.** This is the design's spine and its cleanest defence.

> *"Under the frozen agent and interface of this design — where state augmentation is deliberately excluded so that only the reward may vary across arms — the reward channel is the forced injection point for tail-risk information, a design necessity rather than a convenience."* (Theory §3.7)

Concretely: the five LLM arms share **one fixed SAC agent, one matched candidate budget, and identical prompts**, differing *only* in the feedback block; two non-LLM search baselines bound the procedure. The two experiments "differ in exactly one respect, which is the entire manipulation: the scalar is a fixed measurable function of the vector." The selector is the *same* tail-blind validation DSR for every arm, so it gives no arm an advantage — any tail effect must come from the designer's *use* of the signal.

**The identification litmus (a standing decision rule).** Any proposal that would let a new input reach the STATE or the reward beyond the manipulated feedback block is *creep that breaks identification* and is rejected on sight — which is why the 2026-07 additions (bid-ask, BAB/QMJ, delisting variants, richer diagnostics) are all report-only/data-panel by design, why RDA-style rich visual diagnostics are explicitly *not* adopted (§19d), and why a queryable simulator for the designer was rejected (§17c). The litmus also protects the leg suite: every leg receives the **byte-identical prompts** — the treatment text is one instrument.

**The honesty that protects it (do not equivocate).** The fed tail is measured on the trained policy's *own* realized returns, so it is **endogenous** to the agent it steers. H2 therefore compares two *coupled* reward→policy→measurement loops — the legitimate object of study — not an exogenous risk measurement. "Critic-agnostic" (reads no Q-network) is **not** "agent-independent." The three-way split (fed on train / selected tail-blind on val / tested on sealed test) mitigates selection-overfitting but does not break the endogeneity, and the write-up says so plainly.

---

## 7. The experiment: agent, environment, data

### The agent
A **Soft Actor-Critic** learner (Stable-Baselines3), with the clipped double-Q (twin-critic minimum) from TD3 to curb value overestimation, **held byte-identically fixed across all arms** — it is the constant against which the feedback channel is varied.
- **Training budget:** **400,000** environment steps per candidate (B\*, R77 — the *measured knee* of a two-stage learning curve: the first pilot was flat-within-noise to its 350k ceiling; the pre-committed extended-curve rule, registered 2026-07-13 *before* the extension data existed, fired on the 100k→1.6M cluster ladder — the ascent to 400k is decisive (2.9–5.4× SE) and the increments beyond collapse an order of magnitude. Read "at the measured knee", never "at convergence".)
- **Replay buffer capped at 50,000** transitions (memory safety on a single GPU; ~34 passes over the fixed training calendar at B*=400k (R77; the ~17 figure was R74's 200k-era count)).
- **PopArt** value-target normaliser applied uniformly so reward-scale heterogeneity (which in SAC governs exploration temperature) cannot confound arms; it preserves the realized-return series exactly.
- Evaluation = one **deterministic walk-forward rollout**; the window edge is **time-limit truncation, not absorbing termination** (so the value bootstrap is not spuriously zeroed).
- **Positioning:** this is **simulated-online, not offline, RL** — off-policy SAC collecting its own transitions against a historical-replay simulator under each candidate reward. (TQC, a truncated-quantile critic, is a *named secondary* mean-vs-quantile-critic experiment — not the contribution; PPO/TD3 are post-bank robustness re-runs on frozen winners.)

### The environment (the MDP)
- **Universe:** top **30** names by point-in-time market cap, + cash; fixed action space across train/val/test. *(The "why thirty" defence is a registered write-time obligation — registry row 26: trainability at matched compute; diversification saturation at 20–40 names; DJIA-30 comparability, strictly dominated by our PIT construction; benchmark strength at n=30 with ~3,000 train days.)*
- **State / observation:** a 60-day per-asset return lookback over the 30 assets, plus a cash-row carrying three leakage-safe regime features — 20-day realized volatility, the 20/60-day vol ratio, and the (lagged) VIX close — plus previous weights (for turnover). All rolling statistics are computed through *t−1*; **no security identifiers or dates ever enter the observation or any reward** (anonymised integer indices only).
- **Action:** long-only, fully-invested **softmax simplex** over the 30 assets + cash; the action is pre-softmax logits in [−10, 10]. (The softmax image is the *open* simplex, so an exact all-cash corner is provably unreachable — a disclosed limitation.)
- **Reward:** authored by the LLM (below). The environment's own economics are the return/cost transition, not a fixed reward.
- **Costs:** proportional to turnover, `cost = c · turnover`, `turnover = 0.5·L1(w_t − w̃)` with w̃ = previous weights drifted by realized returns; headline **10 bps**, swept over {0, 5, 10, 25, 50} bps.
- **Timing:** the return is realized *after* the action; **walk-forward** horizon terminating at the split boundary.
- **A deliberate world-model stance (one CH4 sentence, registry row 32):** the historical-replay simulator is the *realized* world, deliberately preferred to a *learned* (generative) one — a generative market simulator would let authored rewards exploit simulator artifacts (reward hacking against the world model) and would trade the study's strongest asset, licensed PIT data, for a sim-to-real validity gap.

### The data
- **A licensed Refinitiv/LSEG panel** of daily total returns for a **survivorship-free, point-in-time** universe: **963 securities over 5,406 trading days, 2005 → end-June 2026** (`univ5`). (Not CRSP — that was the originally-planned source.) VIX from FRED; factors from the Kenneth French library. Redistribution is prohibited, so the repo ships checksums + pipeline + a *synthetic* panel, not the data.
- **Split C:** train **2005–2016** (agent learns, feedback measured here), validation **2017–2019** (selection), test **2020–2026 H1** (sealed until final inference).
- **Purge/embargo:** the effective inter-split purge is **max(embargo 21, lookback 60) = 60 sessions** (López de Prado purged/embargoed CV), unit-tested adversarially. Consequence: the COVID crash (19 Feb–23 Mar 2020) falls *inside* the test-boundary purge, so the sealed window opens ~**30 March 2020** — capturing the recovery / elevated-vol regime rather than the drawdown.
- **Delisting:** the headline policy is `liquidate_to_cash` (zero-fill), which *understates* rather than *invents* the delisting tail. A Shumway surcharge (−30% NYSE/AMEX, −55% NASDAQ) is retained only as the heavy end of a sensitivity band d ∈ {0, −30, −55, −100%}; across the whole band pooled test CVaR-5% moves only ~2% relative, so the hypothesis ordering is invariant. (Observed-terminal recovery found the vendor already books all 333 dead names' realized terminals, so the flat surcharge was double-counting + M&A contamination — `univ5s` equals the zero-fill headline byte-identically.)

### The motivating tail facts (the EDA that earns the hypothesis)
The cross-section is strongly **leptokurtic (excess kurtosis 15.25)**; the ratio of empirical to Gaussian conditional shortfall **crosses over from 0.84 at moderate levels to 1.66 deep in the tail**; on the worst days **≈ 19.7%** of names crash together. *"A scalar measured at a single level cannot represent a tail whose severity relative to the Gaussian benchmark reverses across quantiles; a vector of level-specific conditional shortfalls can."* This is the data-motivated "why" behind the whole manipulation — and it is also the registered answer to the "null-by-design universe" objection (registry row 27): the multi-level tail structure was demonstrably *present to exploit* on this very panel.

---

## 8. The seven arms

All arms run the **same fixed SAC agent** and the **same matched candidate budget**. The five LLM arms differ **only** in the feedback block; the two non-LLM baselines bound the search procedure.

| # | Arm | What it feeds / is | Role — what it isolates |
|---|---|---|---|
| 1 | **distributional** | scalar + the full frozen **6-scalar tail set** | **THE contribution** — the tail-shape information |
| 2 | **scalar** | the scalar performance number only | the raw information contrast (confounded with prompt length) |
| 3 | **placebo** | scalar + an inert block matched in length/field-count | removes the **length / token-count** confound (information ≠ tokens) |
| 4 | **scalar_cvar5** | scalar + exactly **one** downside number (CVaR-5%) | removes the **"any-downside-number"** confound (tail *shape* ≠ any one risk number) |
| 5 | **placebo_shuffled** | distributional's *exact* block, values **deranged** | the **structure-vs-content** control (R32) — same format, scrambled numbers; a *disjoint* control, never an IUT leg |
| 6 | **random_search** | search over code, **no LLM** | **H4a** — isolates search quality (proposal quality at comparable expressive power) |
| 7 | **bayes_opt** | Bayesian optimisation over a fixed parametric template, **no LLM** | **H4b** — isolates form-richness (open-ended reward language vs a tuned fixed template) |

The three H2 comparators (scalar / placebo / scalar_cvar5) form a **conjunction**: together they strip length, anchoring, and any-downside confounds, so what survives all three is *tail-shape information specifically*. `placebo_shuffled` (arm 5) is the sharpest control of all — identical structure, scrambled content — and it is deliberately kept **disjoint** from the confirmatory family so it can never inflate or gate the headline.

*(v2 note: each replication leg runs exactly the **five LLM arms** — arms 1–5 — at 30 candidates each; the two search baselines are core-only, as is H1's baseline panel.)*

---

## 9. The fed tail vector

The distributional arm feeds **exactly six** left-tail scalars (returned by `ReturnDistribution.tail_stats`):

| Field | Definition |
|---|---|
| `cvar_01` | CVaR at α = 1% (EVT/GPD for a well-behaved tail, else empirical; **flagged high-variance**) |
| `cvar_05` | CVaR at α = 5% (EVT/GPD for a well-behaved tail, else empirical) |
| `cvar_10` | CVaR at α = 10% (empirical: mean of the worst ⌈αT⌉ returns) |
| `cvar_25` | CVaR at α = 25% (empirical) |
| `left_tail_mass` | mean(returns < −2σ) |
| `robust_skew` | Bowley quantile skew ((Q95−Q50) − (Q50−Q05)) / (Q95−Q05); **negative when the left tail is longer** |

**How it is measured.** Directly from the trained policy's realized per-step portfolio returns — reading **no Q-network** (so it is critic-agnostic and works for the SAC mean critic or the TQC quantile critic). **Empirical** estimator for the body (25%, 10%, left-tail mass, skew); a **Generalized-Pareto / EVT peaks-over-threshold** fit supplies the extreme levels (5%, 1%). A data-dependent guard falls back to empirical when the requested level exceeds the exceedance fraction, or the fitted shape ξ ≤ −0.5 (non-regular region) or ξ ≥ 1 (infinite-mean tail); the routing is per-candidate and **logged**, then reported. Measured on the **training split** (measuring on validation and then selecting on validation would re-introduce overfitting). The serialized block is **matched in line-count / length across arms** so the H2 contrast isolates information content, not token count.

**Why exactly this vector (the theory doing work).** By the Kusuoka representation, every law-invariant coherent risk measure is a supremum of CVaR mixtures; a CVaR profile across α is therefore a *discretisation of the canonical coordinate system* for the whole class of risk-sensitive objectives a designer might want. It is a **profile of the realized-return lower tail — not the full distribution.**

**The resolvability anchor (R76 — why "small decimals" is a live scientific issue, not a nuisance).** Measured on the univ5 train window (equal-weight top-30 proxy, stationary-block bootstrap): the *marginal* sampling SE of a fed CVaR-5% level is ≈ 0.0033, but candidate *differences* are paired on the common market path, so the paired diff-SE is ≈ 1e-4 (sibling-close reward programs) to ≈ 8e-4 (structurally different ones) — typical fed deltas of a few × 1e-4 range from clearly-resolvable signal to borderline. This is what makes the A5 "rational insensitivity" account (§17) a defensible stance that must be named ex-ante, and it is the calibration behind the R96 JND module's stimulus ladder.

---

## 10. The LLM authoring loop, sandbox, and selection

> *Completeness notes (2026-07-23 audit):* the campaign authors under **`--pass-mode B`** (the registered two-pass protocol; pinned in every runbook launch line); model output runs through the **salvage extraction path** (`extract_reward_source` — fenced or prose-wrapped code is recovered, so a well-formed reward is never rejected for formatting; the residual non-compliance rate is itself a reported reliability metric).

**The reward-designer.** A frontier LM — **Claude Opus 5** in the confirmatory campaign (Claude Sonnet 4.6 in the prototype; R102 succeeded Opus 4.8 pre-launch). It operates in an **Eureka-style reflect-and-improve loop**: it authors a reward-function as Python code, the agent is trained and evaluated, a feedback block is composed, and the model revises the code. The loop runs **six generations of five candidates under a matched budget of thirty per arm, reflecting on the generation's best candidate** (serial reflect-on-best; Eureka-faithful). Opus was chosen for strongest benchmarked code generation and because its safety-classifier posture is common-mode across arms — Opus 5 carries the same classifiers as its predecessor, so the succession adds no arm-asymmetric refusal channel (a refusal on one arm but not another would break arm symmetry) — the same reasoning that excludes Fable 5 as an author (whose classifier behaviour differs) and Sakana Fugu entirely (orchestrator → single-author attribution impossible).

**The prompts are one instrument.** The two loaded prompts are tail-**neutral** (verified: no tail/CVaR vocabulary), R79-strengthened for model-agnostic output format ("a single Python code block containing ONLY the function definition"), and **byte-identical across all eleven full-loop models** — the "same exam for every student" principle. A 2026-07-23 deep review *considered and rejected* (dated, pre-freeze) XML-tagging the prompts and assistant-prefill code-forcing — the first would invalidate the tail-neutrality verification and the σ pilots calibrated under these exact bytes; the second is provider-asymmetric and would become a format confound across legs (§19d).

**The sandbox (untrusted-code safety).** The authored reward is untrusted input: each candidate is screened once by an **abstract-syntax-tree allowlist gate** (no imports beyond numerical primitives; no attribute or name reaching the file system, network, or process) and then **executed in-process on anonymised, read-only arrays** — so a candidate can neither exfiltrate information nor corrupt shared state. **No tickers or dates are reachable by construction.** This also closes the "profit mirage" contamination risk: era knowledge is structurally unreachable, and whatever era-nonspecific reward-shape prior survives is *identical across arms* and cancels in the between-arm contrast. (Hardening current to 2026-07-23: a `|total| > 1e6` magnitude clamp to the safe default now also protects the popart-disabled ablation — 5-auditor sweep item (e), fixed.)

**Selection / fitness (frozen, reward-independent, tail-blind).** Candidates are selected on a **validation Deflated Sharpe ratio with risk-aversion weight λ = 0** — a *tail-blind* criterion, applied identically to every arm, computed on realized validation returns and independent of the candidate reward's own units (so selection cannot be reward-hacked). This yields the **three-way decoupling** that is the methodological core: the tail is *fed* on the training split, candidates are *selected* by a tail-blind DSR on validation, and the hypothesis is *tested* by empirical CVaR on the sealed test split. Because the object fed is neither the object selected on nor the estimator graded by, any tail effect is attributable to the channel and cannot be a self-grading artefact.

**The reproducibility contract.** LLM generation is *provably not* reproducible (version drift + float non-associativity), so the system uses **replay-from-archive**: every prompt, authored reward, and feedback block is archived at generation time with byte-level tamper-evidence, and downstream results are computed by *replaying* the archive, never regenerating it. The *analysis* is the reproducible object. (v2 extends this to a **three-layer statement**: analysis = bit-exact replay; protocol = re-runnable by anyone; experiment = the five hash-pinned open legs close the gap closed models cannot — §15.)

---

## 11. The four hypotheses

| | Statement | Arms / contrast | Metric | Test | Decision |
|---|---|---|---|---|---|
| **H1** | LLM-designed rewards ≤ best hand-designed baseline (beat-the-human) | LLM winner vs **max** of 4 baselines (raw return; return−variance; return−CVaR; differential Sharpe) | annualised OOS Sharpe | **none — descriptive only** | No p-value; excluded from the m=6 family. Reported as context, because it carries a self-declared data-snoop (the comparator max is chosen on the sealed leg) whose net sign is unidentified |
| **H2** | Tail feedback beats scalar at matched compute **(THE HEADLINE)** | distributional vs {scalar, placebo, scalar_cvar5} | per-seed Sharpe IQM **and** CVaR-5% IQM | **two co-primary IUTs** (see §12) + TOST | supported iff all three legs reject one-sided at α=0.05 in the predicted direction; else a bounded equivalence / inconclusive |
| **H3** | Iterative reflection ≤ single-shot at matched budget | within the **distributional** arm: 6×5 iterative vs 1×30 single-shot | per-seed Sharpe (& CVaR) IQM | per-seed paired bootstrap **+ TOST ±0.05** | reported as a TOST-bounded equivalence, outside the m=6 family |
| **H4** | LLM ≤ black-box search at matched budget | LLM winner vs random_search (**H4a**) and vs bayes_opt (**H4b**) | validation DSR / OOS risk-adjusted | 2 separate tests, **Bonferroni-2** | LLM beats each control at matched compute; scoped (H4a = proposal quality; H4b = value of an open-ended reward language) |

**H1 is deliberately not an inferential claim.** Two biases push opposite ways (a sealed-leg-selected comparator max is *conservative* for "the LLM beats the human," while un-tuned baselines *flatter* the LLM), so the net sign is unidentified and H1 is reported descriptively — *"context for the headline mechanism result, not evidence for it."* This is an honesty move Okhrati rewards.

**H4's prominence is raised (registry row 20).** The guides' own methodology review flags that *no* literature shows an LLM designer beating matched-compute non-LLM search — demonstrating (or honestly not demonstrating) that edge is itself a contribution. Under the raised bar H4 is a **named result** with its own paragraph and table row, with the Coache–Jaimungal differentiation as an explicit CH2 paragraph.

### 11a. The ten-name hand-written reward canon (R97 — the steel-manned human panel)

The H1 comparator family is the **frozen four** above (multiplicity untouched). Around it, a **ten-name canon** of hand-written rewards is fielded as a *secondary, report-only* panel — the strongest published-canon steelman the identification principle permits, jointly spanning location / scale / tail / path / asymmetry / cost / growth + the online-ratio class (symmetric *and* downside) + the optimized-composite class (via the BO template arm):

| # | Reward | Class | Status |
|---|---|---|---|
| 1 | `raw_return` | location (the FinRL-default net-wealth reward — the field's most-cited floor) | **H1 four — frozen** |
| 2 | `return_minus_variance` | scale-penalised | **H1 four — frozen** |
| 3 | `return_minus_cvar` | tail-penalised | **H1 four — frozen** |
| 4 | `differential_sharpe` | online ratio, symmetric (Moody & Saffell 2001) | **H1 four — frozen** |
| 5 | `differential_downside_ratio` | online ratio, **downside-asymmetric** (Moody & Saffell 2001 eqs. (19)–(24), **first-hand transcribed off the primary source**; DD tracks Sterling — fn. 7 — proxying the Calmar axis) | **R97 seat** — secondary |
| 6 | `mean_variance_utility` | utility (Markowitz-quadratic) | secondary |
| 7 | `return_minus_drawdown` | path-penalised | secondary |
| 8 | `return_minus_downside` | asymmetry-penalised (Sortino axis) | secondary |
| 9 | `return_minus_turnover` | cost-penalised | secondary |
| 10 | `log_growth` | growth (Kelly axis) | secondary |

**Execution path (made precise by R97; runbook §9(h)):** the six secondary members run **report-only at the tier-30 floor** (seeds 0–29), **post-headline, rock-bottom priority (−310, strictly below every leg and rung line)**, via the existing cluster baselines-flood + resume machinery — 6 rewards × 30 seeds = 180 seeded-deterministic trainings, **zero LLM spend**. A deadline-truncated subset is disclosed in CH6 §6.7, never silently narrowed. The `baseline_rewards == REWARD_CANON.keys()` lock is asserted in both directions, and the laptop `--baselines` override refuses to run without `--baselines-only`, so the frozen H1 path cannot be altered by it.

---

## 12. H2 in depth — the headline test

H2 is decided as **two co-primary intersection-union tests (IUTs)**:

- **H2-RA (risk-adjusted performance).** Tail feedback yields winners with **higher OOS Sharpe IQM** at matched compute, surviving the placebo and scalar_cvar5 controls. Decided by a **3-leg IUT on the Sharpe legs at α = 0.05.**
- **H2-Tail (tail outcome).** The same feedback yields winners with a **less-severe realized left tail (higher CVaR-5%)**, again surviving both controls. Decided by a **parallel 3-leg IUT on the CVaR-5% legs**, corroborated by an FZ0/(VaR, ES) Diebold–Mariano comparative backtest (reported, never gated).

**Why the conjunction *is* the multiplicity correction (Berger 1982).** Each leg is tested one-sided at α = 0.05, and support requires **all three** to reject. An intersection-union test's rejection region has level equal to the *maximum* of its constituent levels, so **a conjunction controls its own type-I error at α with no further leg correction** — requiring all legs to reject is already conservative (joint size ≤ max leg size = α).

**A statistical bug the design *fixed* (worth mentioning — it shows rigor).** An earlier version applied *(conjunction) ∘ (BH-over-6)* — it double-corrected, which is under-powered against H2. The audit caught it; the design was rebuilt as **two co-primary IUTs, each its own correction, with BH-over-six demoted to a reported sensitivity, never the gate.** (The asymmetry is comforting: the bug only made H2 *harder* to support, so any null obtained under the old code remains valid.)

**The m=6 union.** The frozen testing family is m = 6 = {3 contrasts × (Sharpe, CVaR-0.05)}; its integrity is enforced by a fail-loud guard that re-derives the realized family and asserts byte-equality with the frozen config. Under the reframe the union is *partitioned* into the two 3-leg IUTs. The reporting is a **two-tier verdict** (H2-RA and H2-Tail separately); the abstract never claims a tail improvement off the Sharpe gate alone.

---

## 13. Equivalence, TOST, and the "bankable null"

**Why equivalence.** The headline finding is expected to be that the two feedback channels perform **the same**. Proving *sameness* is harder than proving a difference: to claim "different," a confidence interval just has to miss zero; to claim "the same within 0.05," the *whole* interval must fit inside ±0.05. So the study uses **TOST** (two one-sided tests) against a pre-registered **SESOI (smallest effect size of interest) = 0.05** in deflated-Sharpe units, symmetric margin ±0.05. *(The SESOI itself gets a decision-relevance justification paragraph in CH4 — registry row 19, drafted D6: what effect size would justify actually building a distributional-feedback pipeline — because an unjustified SESOI is exactly the borderline item a harsh marker rounds down.)*

**The three verdicts.**
- **Equivalent** — the 90% bootstrap CI on the difference lies *inside* ±0.05 → the two channels are practically equivalent within the smallest effect we deemed worth detecting.
- **Different** — the IUT rejects (all legs, predicted direction).
- **Inconclusive** — the minimum detectable effect is *wider* than the SESOI (this is what "inconclusive" is reserved for — never dressed up as "equivalent").

**The bankable-null statement (verbatim from the pre-registration):**
> *"If neither H2-RA nor H2-Tail rejects, we report a null: at matched compute and with a fixed SB3-SAC agent, multi-level tail-risk feedback to an LLM reward-designer did not produce detectably better out-of-sample risk-adjusted performance or tail outcomes than scalar feedback, and — where the TOST 90% bootstrap CI lies inside ±0.05 — the two feedback channels are practically equivalent within the smallest effect we deemed worth detecting."*

It is *bankable* because it (a) names the estimand, (b) carries an equivalence bound (not just "no effect"), (c) is pre-registered and hashed, and (d) is scoped to the operationalisation so it cannot be over-read. **Reporting rule:** lead with TOST; the equivalence is the headline, the IUT the confirmatory check. The write-up's summary additionally carries a registered **post-data severity assessment** (a Mayo–Spanos severity curve at the SESOI per co-primary leg — §2a(c)), so *how severely* the null passed is a planned presentation, not an afterthought.

**The epistemic basis, named correctly (R61).** The credit for the null rests on **Mayoian error-statistical severity** — licensed by the frozen, deviation-free protocol — plus garden-of-forking-paths avoidance (Gelman & Loken), and is reported via TOST equivalence (Lakens), never a bare p > 0.05. (The earlier "corroborated Popperian prediction" label was superseded: pre-registration does not improve *Popperian* severity — the commitment is unchanged, only its epistemic basis is correctly named.)

---

## 14. The seed / assurance-tier ladder

**Why so many seeds — the intuition.** Each training run (one "seed") is noisy: the same reward design, trained twice with different random seeds, lands on different policies and different Sharpe/CVaR numbers. To average that noise away you need many runs, and *how many* depends on how noisy one run is relative to the effect you're bounding.

**What the pilot measured.** On the Sharpe/DSR leg, the seed-to-seed dispersion of the paired difference is **σ_D ≈ 0.369** (σ_seed ≈ 0.244, ρ ≈ −0.141, not significant). Because we want to bound the effect at **0.05**, and the noise (0.37) is ~7× that, a handful of seeds cannot resolve it: at the 30-seed floor the minimum detectable effect is ≈ 0.181 Sharpe ≈ 0.120 DSR at 80% power — larger than the 0.05 SESOI, so the floor is equivalence-*underpowered* and a non-rejection there reads "inconclusive", never "equivalent". The negative pairing correlation is a small extra penalty — common random numbers were *supposed* to cancel noise, but ρ came out slightly negative, so σ_D ended up a touch *larger* than two independent arms would give. (Note the contrast: on the **CVaR-5% co-primary leg** the pilot dispersion is tiny — σ_D ≈ 0.0015, ρ ≈ +0.47 [VERIFY against the σ_D pilot report before quoting — not located in the audited files] — already conclusive at 30 seeds. It is the Sharpe/DSR equivalence leg that drives the ladder.)

**The ladder (Amendment E1; each rung a complete, CRN-preserving study; truncation falls back to the largest completed rung):**

| Rung | Meaning |
|---|---|
| **30** | Distinction-bankable core (H2 + mechanism + H1 + H3 all complete; the CVaR-5% leg already conclusive) |
| **100** | σ-precision insurance (the σ_D estimate itself tightens to ≈ ±10%; the in-ladder σ_D re-estimate at B\*=400k recalibrates the exogenous stop) |
| **189** | Monte-Carlo point-estimate power |
| **279 / 340 / 403 / 568** | **80% / 90% / 95% (the registered primary target) / 99%** equivalence assurance, powering the ±0.05 SESOI at the χ²-upper confidence bound on σ_D |

**Exogenous stopping (the integrity keystone).** *"The stopping tier is determined exogenously by measured Myriad throughput against the 1 Sep deadline, never by inspecting results — an exogenous truncation that preserves the single confirmatory look."* Every number is rung-freshness-tagged so a stale figure surviving a rung refresh fails a grep gate (`scripts/check_rung_freshness.py`). Because the stop is exogenous, the single-look inference stays valid whatever rung is reached, and the write-up always reports the *achieved-rung* power honestly.

> **Note on "target" wording.** The pre-registration (the authoritative source) names **403 (95%)** the *primary target*. Under mode-D execution the timing picture improved materially: tier-403 lands ~**L+13–14.5 days** from the GO, and **the 99% rung (568) is likely from a ≤ Jul-25 GO** (HANDOFF §1). Worth stating unambiguously to Ramin as "primary target 403; mode-D makes 403 — plausibly 568 — the realistic landing; floor 30 banks the degree at every stop."

---

## 15. The v2 multi-model design

**What changed and why.** v1 used a *single* frontier author (Opus) and spent nearly all compute climbing the seed ladder. After the NatWest call (Raad, Head of AI R&D, + industry supervisor Stefan) pushed back — *why one model? what about open weights and reproducibility? you bought seed-certainty on one statistic for one model and gave the model axis zero* — the design was **unfrozen pre-data** (zero campaign data existed, the sealed leg was untouched, so this is a legitimate pre-data revision, not a forking path) and rebuilt as **v2**.

**The v2 shape.** *One* frozen question, *one* frontier **confirmatory** author (Opus 5, under the full v1 rigor — 7 arms, m=6, co-primary IUTs, SESOI ±0.05, the seed ladder, exogenous stop), plus **ten replication legs — 11 full-loop models total** (R80 established nine; R90/R92 reshaped seat 9; **R95 seated Kimi K3 as leg 10**). Each leg re-runs the **five LLM arms × 30 candidates** at the **30-seed floor** (seeds 0–29 — the core's floor subset, giving the common-30 CRN pairing the pair-DiD estimator requires), with byte-identical prompts, unified prompt-variation diversity, pinned providers/quantisation/reasoning-modes/max-tokens, priority-laddered behind the core, and calendar-gated at **2026-08-14T23:59Z**. The suite is **report-only and disjoint from the m=6 family — it never gates H1–H4.** The confirmatory logic is untouched; the legs add *breadth* (does the choice of author matter?) and *reproducibility* (open-weight legs run the complete experiment for ~$0.1–0.8 each).

### 15a. The full-loop roster of record (11 models; `config/legs.yaml` == `model_suite`, gate-bound)

| # | Model | Open? | Pin (grade) | $/MTok in–out | Leg cost (exp.) | Scientific function |
|---|---|---|---|---|---|---|
| ★ | **Claude Opus 5** | ✗ | `claude-opus-5` (dateless-immutable; **R102 2026-07-25 — was `claude-opus-4-8`**, now vendor-LEGACY; same classifiers/tokenizer/price) | 5.00–25.00 | ~$6 (full ladder) | **CONFIRMATORY** — gates H1–H4; the E1 ladder; the mechanism kernel reads its archives |
| 1 | DeepSeek V4-Pro | ✅ MIT | HF `deepseek-ai/DeepSeek-V4-Pro@b5968e91` (**weights-hash**) + think-high pinned | 0.435–0.87 | ~$0.4 | Open frontier #1; the contamination-gated seat (GLM absorbs on fail) |
| 2 | GLM-5.2 | ✅ MIT | HF `zai-org/GLM-5.2@b4734de4` (**weights-hash**) | 0.97–3.04 | ~$0.8 | Open frontier #2 + DeepSeek's pre-declared fallback |
| 3 | Qwen 3.6-27B | ✅ Apache | HF `Qwen/Qwen3.6-27B@6a9e13bd` + SiliconFlow-fp8 provider-pin | 0.45–2.70 | ~$0.5 | **Open capability pair — TOP** (dense; same provider+quant as its sibling) |
| 4 | Qwen 3.5-9B | ✅ Apache | HF `Qwen/Qwen3.5-9B@c2022362` + SiliconFlow-fp8 provider-pin | 0.10–0.15 | ~$0.1 | **Open capability pair — FLOOR**: where the numeracy bottleneck is predicted to bite; failure-is-a-finding |
| 5 | Haiku 4.5 | ✗ | `claude-haiku-4-5-20251001` (**dated snapshot**) | 1.00–5.00 | ~$1.2 | **Closed capability pair — FLOOR** (vs Opus) |
| 6 | GPT-5.6 Luna | ✗ | `openai/gpt-5.6-luna` (undated; disclosed) + effort-low + 2k cap | 1.00–6.00 | ~$1.4 | The cross-vendor check: "is the null an Anthropic quirk?" |
| 7 | Nemotron 3 Super | ✅ NVIDIA-OML | HF `nvidia/…-A12B-BF16@d51eab0d` (**weights-hash**) | 0.08–0.45 | ~$0.1 | The data-transparency seat ("major portions of training data released, some subsets gated" — phrase exactly) + architecture diversity |
| 8 | Sonnet 5 | ✗ | `claude-sonnet-5` (undated; disclosed) | 2.00–10.00 (introductory through 2026-08-31) | ~$2.9 | The latest-generation seat (released 2026-06-30; R90/R92) |
| 9 | Gemini 3.5 Flash | ✗ | `google/gemini-3.5-flash` (undated; reasoning at provider default, disclosed) + 2k cap | 1.50–9.00 | ~$1.6 | Big-three closed coverage; stretch seat — truncates **second** |
| 10 | **Kimi K3** | closed→open by rule | `moonshotai/kimi-k3-20260715` (**dated snapshot** — the strongest pin among the closed-class legs); weights due 2026-07-27 → HF-hash by the pre-declared `kimi_k3_upgrade_rule` | 3.00–15.00 | ~$4–7 (always-on thinking) | The frontier-class open-upgrade seat (R95); **last in queue — truncates first** |

Queue order (frozen; realized as the mode-D priority ladder −200…−290): **deepseek → glm → qwen27 → qwen9 → haiku → luna → nemotron → sonnet-5 → gemini → kimi-k3.** Under mode-D all ten legs land ~L+4.5–5.5, so calendar truncation is unlikely at any plausible GO date.

### 15b. The three controlled instruments (where model differences become inference)

| Instrument | Members | What it identifies |
|---|---|---|
| **Open capability pair** | Qwen 9B ↔ 27B (one vendor, one provider, one quantization, both dense) | content-effect × capability, open ecosystem |
| **Closed capability pair** | Haiku 4.5 ↔ Opus 5 (one vendor; the Opus-5 confirmatory restricted to the common 30 seeds) | content-effect × capability, closed ecosystem |
| **Generation pair** | Opus 4.8 (M2) ↔ Opus 5 (**confirmatory + M2**) — **REALIZED under R102 (2026-07-25)**: Opus 5 became the confirmatory author, with Opus 4.8 retained in M2 as the pair partner (supersedes the R91-conditional / R98-budget-deferral form) | content-effect × one model generation, vendor+tier fixed |

**The capability-gradient prediction, made falsifiable (R87).** Three *rival, pre-registered* signatures are named ex-ante so the prediction can't be trivially satisfied:
- **Capacity account** — responsiveness *rises* with capability (weak authors fail to use the numbers).
- **Representational account** — responsiveness *flat at ≈ 0* across capability. **This is the registered prediction** of the numeracy-bottleneck headline: the bottleneck is the numeric *representation*, so it binds every author, even the frontier; the *levers* are legibility/guided-comparison probes, not capability.
- **Echo account** — responsiveness *decreasing* in capability (weaker models surface-echo fed numbers without using them).

The decision is read jointly from the capability regression + both family-pair DiDs + the M2 probe grid, adjudicated by the A1–A5 fingerprint. *(The Sonnet-4.6 "pilot bridge" prediction was **withdrawn pre-data by R92** when Sonnet 4.6 was removed — no re-scoping to another model, which would dilute ex-ante falsifiability; the prototype remains engineering-only evidence, as it always formally was.)*

**The capability anchor (R84, discretion-free).** Primary = the model's **SWE-bench-Verified** score from its official card under a discretion-free retrieval rule; a model with no published score is MISSING — excluded from the primary regression, never imputed or benchmark-swapped. At-freeze values: **{qwen3.6-27b: 77.2, haiku-4.5: 73.3}; every other leg = MISSING by rule** (GLM publishes SWE-Pro not SWE-V; DeepSeek's circulating 80.6 is the Max-mode figure while the leg pins think-high — conflation refused; Luna documented ABSENT). Secondary = the M2 reading score (secondary *because* it shares method variance with the outcome — circularity disclosed); tertiary = the within-family ordinal embodied in the pair contrasts.

### 15c. Cross-leg synthesis (all report-only, all pre-registered)

- A **descriptive replication sign count** on the CVaR-leg contrast only (the Sharpe leg is predicted-tie for every model; legs share panel + CRN seeds, so they are not independent votes), restricted to legs whose winners clear the **R84-pinned T0 floor** (the equal-weight benchmark's mean per-seed Sharpe on the common floor seeds 0–29; the filter is arm-symmetric, so it preserves the null's sign-flip symmetry — failing legs report as authoring/search failures, a finding, never a vote).
- The **joint sign-flip permutation test** on the **pooled mean** (dist − scalar) difference — flips applied simultaneously across legs per shared CRN seed, 10,000 reps, one-sided (a sign-*count* statistic is near-powerless under correlated joint flips; shared-seed/panel dependence lives inside the null).
- **The R86 pooled bounded-effect CI** — the 90% seed-block-bootstrap CI on the pooled mean CVaR-5% difference (the same joint-draw scheme, dependence-honest: k perfectly-correlated legs yield one leg's CI, never a fake √k shrink), reported in daily-return units *and* relative to the scalar-arm pooled CVaR level — **the registered cross-model bounded-null statement** (per-leg TOSTs at the floor tier are inconclusive by construction; pooling is where the precision lives).
- The **two family-pair DiDs** (the identified capability estimates, computed on the common floor-30 CRN seed subset with a seed-paired bootstrap CI); the cross-leg capability regression is labeled DESCRIPTIVE (n = 10 legs carries no meaningful test power).
- **BH across the 10-leg report-only CVaR-contrast TOST family** for any starred statement (R95-updated from 9).
- **Per-model authoring-reliability metrics** (format-compliance baseline, sandbox pass rate, violation taxonomy, refusal/truncation rates, code diversity, per-model program taxonomy) and **generation-indexed responsiveness** (does feedback-use strengthen across the loop's generations? — zero new compute), all registered report-only.

### 15d. Reproducibility & pins (the permanence claim, executed)

Every open-weight leg pins the **Hugging Face repo + commit hash of its exact weights release**, retrieved from the official HF card at gate time (never inferred) — **all five filled 2026-07-22 from the official HF API** (R93; licenses independently re-verified MIT / MIT / Apache / Apache / NVIDIA-OML) — plus the provider and served quantization (the Qwen pair is served fp8: the pin + provider + quantization *together* define the executed author; never claim the bf16 weights authored). `freeze.py` refuses the real freeze while any pin placeholder remains. OpenRouter legs pin **temperature = 1.0** (uniform decoding; rejection → provider default, disclosed from the gate smoke); every reasoning pin must **round-trip** (the gate smoke archives reasoning-token usage as evidence the pin functioned — a silently-ignored pass-through is a fictional pin). Rolling `~latest` aliases are hard-rejected at the transport. This is the **three-layer reproducibility statement**: analysis = bit-exact replay; protocol = re-runnable by anyone; experiment = the pinned open legs close the gap closed models cannot (the 2026-07-20 survey found **15/15 direct-lineage papers used a closed primary author** — to our knowledge this is the lineage's first systematic open-weight replication suite; the claim stays hedged until the fence sweep confirms, registry row 16).

### 15e. The money (registered buckets; R83 advisory — realized per-call cost is the authority)

| Bucket | Expected | Worst-at-caps | Funding state (2026-07-23) |
|---|---|---|---|
| **Anthropic key** (Opus + Haiku + Sonnet-5) | **~$10** | **~$27** | **FUNDED: $25.91** (Tamer, 2026-07-22; key verified LIVE via `author_smoke`) — covers the expected ~$10 with 2.6× headroom, sits $1.09 under the ~$27 worst-at-caps; optional +$5–10 buys full margin |
| **OpenRouter key** (7 legs incl. K3 + gates + M2) | **~$18** | **~$30** | Top-up **≥ $25 + the do-not-log/train account toggle STILL PENDING** (the toggle must be enabled BEFORE the gates run — ADR-060) |
| **Whole study** | **~$28** | ~$57 (never realistically reached) | Under-funding **pauses, never wastes** — the advisory ledger warns at 80%/100% and skips-loudly rather than burning; archive-replay resume re-runs exactly the unauthored slots |

The $30 figure is the **advisory planning ceiling** (R83, Tamer's instruction): tracked per-call in a cross-provider ledger (`outputs/spend_ledger.jsonl`; OpenRouter `usage.cost` where returned, tokens × planning-prices for Anthropic), warned at thresholds, **never refuses** — spend decisions rest with the researcher; the exogenous stops that protect the design are the seed-rung rule and the calendar gate. Realized spend is a reported CH4/CH6 number and the NatWest-brief line. The R96 optional module, if activated, is a **separate ~$25–35 P2-module budget line** — the campaign remains the ~$30-class study.

---

## 16. Tiers · stages · rungs

Three orthogonal axes keep the confirmatory core sealed while everything else scales with available compute:

- **Tiers (the seed ladder, §14)** — the *depth* axis: [30, 100, 189, 279, 340, 403, 568], climbed by the exogenous rule.
- **The leg queue** — the *breadth* axis: Opus core → the 10 replication legs. Since R88 the registered queue order is realized as a **scheduler priority ladder, not a serial schedule** (mode D, §20): all lines may execute concurrently, but *completion and calendar-gate truncation order remain exactly the pre-declared queue* — under scarce capacity the scheduler starves back-of-queue work first, reproducing serial semantics; under abundant capacity everything simply finishes sooner. Ops-only: no seed, arm, budget, or stopping-rule change.
- **Stages** — the *sealing* axis:
  - **Stage 1** = the frozen confirmatory campaign (the dissertation's verdicts) + the report-only breadth registered with it (legs, M2, mechanism, the ten-name canon).
  - **Stage 2** = post-headline, **report-only, dissertation-optional** extensions bound to Papers 2/3: the **named first-priority extension is the 3-point GPT-5.6 within-family ladder** (R99 — Luna 82.5 / Terra 84.3 / Sol 88.8 as full legs, ~$9.32, declined this cycle on budget; the M2 reading axis carries all three points now); a training-budget dose-response (campaign winners × {200k, 400k, 800k} × 10 CRN seeds); an FTSE-100-lite zero-shot replication (frozen winners re-tested, no authoring); the **qwen3.5-9b full search replicate** (~150 trainings — the lineage's first direct estimate of authoring-search variance, upgrading limitation B.2.6 from disclosed to quantified); the CI-annotated re-rendering (the A5-vs-A2 adjudicator); alternate-agent robustness (TQC/PPO/TD3 on frozen winners); and the remaining rule-driven trigger (**KAT-Coder** — open weights + verified benchmarks → M2 promotion / Stage-2 candidate). **Kimi-K3 is no longer a Stage-2 trigger — R95 seated it outright as leg 10** (its 2026-07-27 weights release upgrades it to open-class by the pre-declared rule). Nothing Stage-2 is ever injected mid-flight.

**The M2 reading-link survey (Stage-1-registered, post-headline, ~$10, zero GPU).** Now **26 core + 9 budget-permitting extras = 35 models** across ~10+ labs: the Anthropic reading ladder (Haiku 4.5 · Sonnet 4.6 · Opus 4.8 · Opus 5 · Fable 5, + Sonnet 5 extra), the Qwen ladder (5–6 points behind the 2-point full-loop pair), the closed cross-vendor tier (**GPT-5.6 Sol · Terra (R99) · Luna** — the 3-point family ladder — + Gemini 3.5 Flash, Grok 4.5, Nova 2 Lite), the open cross-vendor tier (DeepSeek, GLM, Nemotron, Hy3, MiniMax-M3 (restricted-license, labeled), Kimi K2.7-code, MiMo, North-Mini-Code), and the floor/curiosity rows (Granite 4.1, Gemma 4, **Mercury-2 — the diffusion-architecture row**). Inclusion rule (pre-registered): UK-callable + passes the author smoke + passes the behavioural contamination screen + a distinct base model + not an orchestrator. Leg models double as survey rows at zero marginal design cost. **Three exclusions documented in the executed config** (cite in methods): Sakana Fugu (orchestrator → attribution impossible — the identification principle), Llama 4 (SWE-V ~24 + license friction), and any `~latest` rolling alias (reproducibility poison); the roster doc's fuller excluded-by-design table adds Fable-5-as-author, MiniMax-M3-as-leg, Qwen-4-Coder-as-leg (MoE — would break the dense–dense pair invariant), and Sonnet 4.6 (removed by R92; retained in M2).

### 16a. The R96 optional psychometric module (registered-NOT-activated; Tamer's dated write-time decision)

Fully pre-specified in `docs/M2_EXTENSION_OPTIONAL_SPEC_2026-07-22.md`; mirrored at `model_suite.m2_extension_optional`; registry row 25 holds the decision obligation.

- **Axis A — psychophysics for the 11 full-loop models:** a 2AFC graded-delta ladder (7 log-spaced levels spanning the R76-measured fed-delta range; ecological archive-jittered stimuli; catch trials, positive controls, an adversarial digit-length stratum; the 2×2 format×instruction subsets measured as *threshold shifts*) → each model's numeric **just-noticeable difference (δ75, bootstrap CI)**, and **the overlay estimand: the share of the campaign's realized fed deltas below each model's threshold** — the quantitative closure of the mechanism story ("the designers were shown differences they could not resolve"), deepening the Hartley…Okhrati question to its resolution limit. ~300 calls/model, ~$8–12.
- **Axis B — the ecosystem map:** the full eligible frame of the archived OpenRouter census (~100–130 distinct bases after the registered dedup/inclusion rule — a census, not a sample) on a calibrated 68-call short form, psychometrically linked through the 11 dual-form models; estimands: the threshold CDF, threshold-vs-release-date trend, threshold-vs-price (the practitioner curve), within-family scaling ladders, the n≈100 reading-capability regression. ~$15–25.
- **Governance:** activation is **Tamer's dated write-time decision** (recorded as an amendment). **If activated, ALL pre-specified estimands report in full** — the all-or-nothing clause makes activation timing incapable of biasing publication. Report-only, disjoint keys, zero GPU, post-headline, budgeted as a separate P2-module line. If not activated, the registered v1 M2 probes still run (~$10, 35 rows). Either way registry row 25 must be closed with a dated decision before the pre-submission sweep.

**The unified execution picture** ("bank at 30, then climb", as mode D realizes it): the priority ladder puts core search/floor/tier-100 above everything (bayes_opt hoisted to priority 0 — its 30-step sequential GP chain is the floor's true critical path), the ten legs at −200…−290 in queue order, tier-189+ assurance blocks from −300 below the legs, and the R97 secondary panel at −310, strictly last. The tier-30 floor banks the degree regardless of where the exogenous stop falls; a rung banks only when it and every rung below are complete.

---

## 17. The mechanism kernel

> *Kernel instrument roster note:* alongside responsiveness, mediation, and the AST named-vs-blinded taxonomy, the kernel includes the **regime-conditional exhibit (T3′)** — report-only, disjoint from the m=6 family — evaluating frozen winners within calm/normal/stress regimes.

This is the **intellectual headline** — the part that turns a null into a finding. It is pre-registered, **report-only, and disjoint from the m=6 confirmatory family**, so it never gates H1–H4.

**The causal chain and the three sub-questions:**
- **SQ1 — Responsiveness (does the signal move the code?).** A per-generation **Spearman** of Δ(fed tail) vs Δ(authored-reward feature) with a bootstrap CI, plus a reward-program differential. Registered direction: **> 0** if the channel acts. The Sonnet prototype's *negative* responsiveness predicts the break is **here**, at the first link. (The statistic forces `responsive = False` when too few bootstrap resamples are non-degenerate — an integer-count construct makes many resamples collapse — so it cannot false-positive off numerical fragility. Its *sensitivity* is separately proven by the registered **responsiveness positive control**: ~20 stimuli with overt directive content where the metric MUST fire — sealing a responsiveness null against the broken-instrument critique.)
- **SQ2 — Transmission (does the code move the outcome?).** A single-mediator decomposition of fed → code → outcome (the indirect effect a·b, percentile-bootstrap CI). If SQ1 is null (a ≈ 0), then a·b ≈ 0 for *any* downstream link — the chain is severed at the first hop, which is the predicted outcome.
- **SQ3 — Specificity (genuine use vs surface echo).** An **identifier-invariant AST structural** named-vs-blinded test (a placebo that echoes tail *tokens* yet writes a different *program* is caught) plus a **legible-format responsiveness differential**, extended by the **guided-comparison probe** (identical stimuli + one added instruction sentence — separates *cannot-read* from *will-not-use*; together with the legible probe it forms a 2×2 format × instruction grid).

**The numeracy-bottleneck hypothesis (falsifiable).** Registered before the sealed leg: any SQ1 failure is *in part* a numeric-legibility bottleneck — frontier LLMs compare close small floats at ~50–70% accuracy, and the fed CVaR values (e.g. −0.0577 vs a sibling's −0.0582) sit in exactly that failure regime — **not** evidence that tail information is useless. The **legible-format ablation** (the identical content re-rendered as basis points / rank framing) tests it: a positive, CI-separated legible-minus-raw differential *confirms* the bottleneck; a null *refutes* it.

### 17a. The new external corroboration — the say–know gap (registry row 31, 2026-07-23)

*"LLMs Know More About Numbers than They Can Say"* (**arXiv 2602.07812**) is the strongest external corroboration yet of the mechanism story: linear probes show models **decode numeric log-magnitudes internally at > 90%**, yet they **verbalize cross-notation comparisons at only 50–70%** — the *say–know gap* IS the A2 "readout" account (content encoded but not reliably verbalized/used), and the paper reports **no format fix**, which validates both our raw small-float default and the registered legible-mode + R96 JND probes as open science rather than solved questions. Registered wiring: CH2 (the mechanism lineage after `wallace2019numbers`) + CH7; verify first-hand at wiring. Supporting context registered alongside: the 2025–26 numeric-tokenization line (TST arXiv 2604.11582; xVal 2310.02989; single-token encodings 2510.06824) — one CH2 sentence on *why* digit fragmentation breaks numeracy.

**The five rival accounts (A1–A5), each with a distinct predicted signature across the instrument suite** — so the observed pattern *scores accounts against each other* rather than confirming one:

| Account | Short description | Key discriminating instrument |
|---|---|---|
| **A1 Genuine-use** | the channel works (responsiveness > 0) | SQ1 itself |
| **A2 Readout / numeric illegibility** | content encoded but not verbalised (the say–know gap); legible re-rendering *recovers* responsiveness | the legible-format differential (> 0) |
| **A3 Execution failure** | multi-step numeric comparison fails regardless of format; re-rendering does *not* help | the legible-format differential (≈ 0) |
| **A4 Prior-dominance** | the objective prior overrides all feedback (Hartley et al. ACL 2025 anchors it: LLMs carry measurable risk-preference profiles) | the *scalar* arm ignoring its own fed scalar + taxonomy concentration |
| **A5 Rational insensitivity** | small deltas discounted as probable noise — a *defensible* epistemic stance, not a deficit (R76; the fed block carries point estimates with no uncertainty annotation) | the CI-/significance-annotated re-rendering (Stage-2) + SNR-conditioned responsiveness |

Mixtures are expected and reported as the observed pattern's distance to each registered signature — never forced into one account. The full suite also carries: the **information-utilization gap** (§2a(d) — how much non-redundant signal the designer was *given* vs how much its code *used*, with placebo_shuffled as the calibration floor); the **oracle-selection headroom bound** (§2a(e) — did a better reward even exist in the authored search space? validation data only); the **fed-delta SNR / attenuation exhibit** (§2a(h) — resolvable-signal share, errors-in-variables disattenuation as a sensitivity, SNR-conditioned responsiveness = the A5 row); the **declared-exploratory distance moderator** (§2a(b)); and the **reflection-funnel content analysis** (§2a(g) — QUOTE → COMPARE → CONCLUDE → IMPLEMENT staged coding of every tail-fed reflection, two coders, Cohen's κ; the accounts predict *different drop-off stages*). Registered honesty: the decomposition is observational (the fed tail is endogenous), so SQ2 mediation has a causal reading only under sequential-ignorability and is reported descriptively; at the n=30 floor some sub-tests are underpowered (effect sizes + CIs + achieved power always reported).

### 17b. The designer-as-world-model framing (registry row 32, 2026-07-23 — a CH7 paragraph, the cheap win)

The reward designer is positioned as **a prior-laden world model with a narrow numeric interface**: the LLM carries a rich *implicit* model of market behaviour (the contamination/H4 priors — here the *object of study*, not a nuisance), and the fed tail vector is an attempt to **update that world model with measured state**. The numeracy bottleneck (B.3.2 + the say–know gap) is then an **interface failure between explicit measurement and the implicit world model** — which is exactly why format probes (legible mode, the R96 JND ladder) are the right instruments. Cited contrast: the LLM-as-world-model line (arXiv 2411.08794, verify first-hand) vs DreamerV3 (Nature 2025) on the agent side. One CH4 sentence completes it: the historical-replay simulator is the *realized* world, deliberately preferred to a *learned* one (§7).

### 17c. Considered-and-rejected (dated, pre-freeze — the fence shows conscious decisions)

- **Swapping SAC for a Dreamer-class agent** — invalidates every pilot/calibration/certification, muddies the deliberate simulated-online-vs-offline-RL positioning (the Okhrati bridge), and near-martingale daily returns are the worst case for learned-dynamics overfitting.
- **Training inside a generative market simulator** (MarS/LMM class) — the artifact-exploitation + data-asset trade (§7).
- **A queryable simulator for the designer** — enriches the feedback channel = the registered identification-breaker class.
- **XML-tagging the prompts / assistant-prefill code-forcing / execution-error traces in reflection** — each dated-rejected (§10, §19d); re-openable for Papers 2/3, never mid-campaign.
- **Named Papers-2/3 extensions:** the tail-feedback contrast under a DreamerV3-class agent (does the null persist when reward shaping interacts with imagination rollouts?); generative tail-stress — synthetic crisis world models extending the existing `ood_stress` module for counterfactual evaluation of the frozen winners.

---

## 18. The full statistics stack

- **Unit of analysis:** per-seed **rliable IQM** (interquartile mean) → contrasts by a **paired stratified bootstrap over shared training seeds** (carries the across-seed variance, not a single path's autocorrelated days).
- **Primary overfitting guard:** **PBO via CSCV** (combinatorially-symmetric cross-validation) over the full block-partition enumeration — trial-count-free; **Deflated Sharpe** is the secondary cross-check.
- **Difference tests:** re-centred stationary block bootstrap (Politis–Romano) for single-series Sharpe/CVaR; the arm-contrast family aggregates across seeds via the paired-seed method; the one-sided headline p is the **directly-computed upper-tail bootstrap probability** (R64 — valid under any skew).
- **Multiplicity:** the two co-primary IUTs *are* the correction (Berger); **BH q = 0.05** is the reported cross-family sensitivity; Romano–Wolf is the FWER alternative; an **α-hurdle t = 3.0** (Harvey–Liu–Zhu) applies *only* to absolute-alpha claims (the study's claim is *comparative*, "not beat-the-market").
- **Tail corroboration:** the **FZ0 / (VaR, ES)** Diebold–Mariano comparative backtest supports (does not gate) H2-Tail — with the B.5.2 size caveat handled: the autocorrelation-robust headline is the stationary-bootstrap p; DM-HLN is a companion with a size/power calibration and a Hill tail-index check on the loss differential.
- **Equivalence:** TOST against SESOI = 0.05, symmetric ±0.05 margin; plus the registered severity-curve presentation (§13).
- **Secondary families (all report-only, keys disjoint from m=6):** the factor-attribution ladder (CAPM → FF3 → Carhart → FF5 → FF6 → +BAB → +QMJ; difference-in-alpha paired across seeds, Newey–West HAC, BH within family — the registered "your edge is just low-vol/BAB" pre-empt); H3 TOST; H4 Bonferroni-2; the structure control (placebo_shuffled); DSR effective-n sensitivity; cross-hypothesis Bonferroni-4 sensitivity; the delisting band; the cost sweep; the rf-excess robustness re-run.
- **Cross-model (v2):** pooled-mean joint sign-flip permutation (10k), the R86 pooled bounded-effect CI, the two family-pair DiDs, **BH over the 10-leg TOST family** (R95), the R84 capability anchor discipline — all §15c.
- **Null triangulation (built instruments, results slots):** Model-Confidence-Set membership, a Bayes-factor + ROPE analysis alongside the frequentist verdicts, null-calibration (size certification), and the synthetic-null exhibit.

---

## 19. Pre-registration and integrity

- **The whole design is pre-registered** — hypotheses, arms, candidate budget, seeds, fitness, the tail-diagnostic set, splits, embargo, benchmark suite, model suite, and analysis plan — with a canonical SHA-256 over a bound file-set (the pre-registration, the prompts, `arms.yaml`, the inference family, and the v2 model-suite/legs surfaces). Post-freeze changes require dated, approved **amendments**; a freeze-guard hook protects the bound files; `enforce_freeze` refuses unfrozen real-spend launches throughout.
- **The freeze history, exactly:** v1.0 frozen 2026-07-18 (`ce5db62c`) → **lifted pre-data 2026-07-20** (ADR-059 / R78, after the industry feedback; zero campaign data existed, the sealed leg untouched — a documented pre-data revision, not a forking path) → v2 freeze **executed 2026-07-22** on Tamer's explicit instruction (`ccf2e76f`, R93 — with every freeze-day item resolved with evidence: HF pins filled, anchor values applied discretion-free, conditional windows re-anchored, the Aug-14 gate confirmed, the novelty probe clean) → **lifted the same day (R94)** on Tamer's clarified instruction. **The standing policy is R94: the freeze executes TOGETHER WITH the full-campaign-run approval — GO-sequence step 1 — never before it.**
- **The canonical hash is recomputed at the GO-day freeze.** R95–R99 landed *after* the R93 stamp, so the live would-be hash has **moved off `ccf2e76f`** — that stamp + bundle remain valid *R93 history* (commit `30ae72b`, `outputs/prereg_bundle_ccf2e76f.zip`), and the GO freeze stamps whatever the then-current design hashes to and builds a fresh bundle. **Never quote `ccf2e76f` as the campaign hash.** At the GO freeze the bundle is also **deposited publicly (OSF/Zenodo, DOI)** as the externally verifiable timestamp anchor; the Okhrati sign-off invariant sits before LAUNCH with default-proceed (R93).
- **The integrity frame:** zero campaign data exists and the sealed leg is untouched, so every pre-GO revision is a legitimate pre-data design improvement — and the documented trail is a *strength*, not a liability. Post-launch supervisor/industry feedback informs presentation and interpretation ONLY (R81); data-collection decisions follow the pre-registered exogenous rules exclusively.
- **Data-blind discipline:** no identifiers or dates ever reach a reward; feedback is measured on the training split only; the sealed test window is evaluated **once**, at the achieved rung.

### 19a. The amendment ledger — R78–R99, one line each (full rows in PREREGISTRATION.md; ~99 dated amendments R1–R99 + lettered rows on the record)

| Id | Date | One line |
|---|---|---|
| **R78** | 07-20 | **THE UNFREEZE** — v1.0 (`ce5db62c`) superseded pre-data; v2 redesign opened (ADR-059; NatWest trigger); sealed leg stays sealed; re-freeze required before real spend |
| **R79** | 07-20 | Model-agnostic output-format strengthening of the two prompts (no semantic/risk-vocabulary change; tail-neutrality re-verified green) |
| **R80** | 07-20 | **The v2 model replication suite** — report-only legs at the tier-30 floor; queue + calendar gate; pre-registered synthesis; screens/smokes/licenses pre-launch |
| **R81** | 07-20 | The $30 spend ceiling + the post-launch feedback protocol (feedback informs presentation only; the ~Aug 6–8 interim pack registered) |
| **R82** | 07-20 | The completeness supplement — uniform max-token pins; the gate made exact (2026-08-14T23:59Z); synthesis ambiguities closed; per-leg bank gates; the public deposit |
| **R83** | 07-21 | The spend ceiling made **ADVISORY** (Tamer) — warns at 80%/100%, never refuses; the exogenous stops are the seed rule + the calendar gate |
| **R84** | 07-21 | The two unpinned selection rules **pinned** (forking-path closure): the SWE-bench-Verified capability anchor under a discretion-free retrieval rule; the T0 leg-inclusion floor = equal-weight mean per-seed Sharpe, seeds 0–29, arm-symmetric |
| **R85** | 07-21 | Reproducibility permanence landed: HF repo+commit **weights pins required** per open leg (freeze refuses placeholders); fp8 served-variant disclosure; temperature=1.0 pinned on OpenRouter; reasoning pins round-trip-evidenced |
| **R86** | 07-21 | **The pooled bounded-effect tier** — the 90% seed-block-bootstrap CI on the pooled CVaR-5% difference (dependence-honest) = the cross-model bounded-null statement of record |
| **R87** | 07-21 | The capability-gradient prediction made **falsifiable** — three ex-ante rival signatures (capacity rising / representational flat-at-zero = THE registered prediction / echo decreasing) |
| **R88** | 07-21 | Queue = a **priority ladder**, not a serial schedule (mode D, ops-only): concurrent execution, pre-declared completion/truncation order; phase-adaptive packing + pipelined rungs |
| **R89** | 07-21 | M2 extras +2 from the freshness sweep (sonnet-5; qwen4-coder — MoE, so M2-only); every leg pin re-verified current |
| **R90** | 07-21 | claude-sonnet-5 promoted M2-extra → **leg seat** (latest-generation seat; its generation-pair role later died with R92's removal of Sonnet 4.6) |
| **R91** | 07-21 | The Opus-5 rumor converted into a pre-declared **conditional-seat rule** (GA + public API id + gates + verifiable single-author attribution; silent fallback-routing fails it on the Fugu principle); confirmatory stays Opus 4.8 regardless |
| **R92** | 07-21 | **Sonnet 4.6 removed** from the legs (Tamer) — the pilot-bridge prediction withdrawn pre-data, no re-scoping; retained in M2; the generation pair re-scoped to the conditional Opus pair |
| **R93** | 07-22 | **The v2 freeze executed** (`ccf2e76f`) on Tamer's explicit instruction, every freeze-day item evidence-resolved (HF pins filled; discretion-free anchor table; conditional windows re-anchored; Aug-14 gate confirmed; novelty probe clean); launch expressly NOT authorized |
| **R94** | 07-22 | **The same-day lift** (Tamer's clarified instruction): the freeze now executes together with the full-campaign approval — **GO step 1, never before**; all R93 preparation retained; `ccf2e76f` preserved as history |
| **R95** | 07-22 | **Kimi K3 seated as leg 10** (live on OpenRouter, canonical dated slug `moonshotai/kimi-k3-20260715` — stronger pinning than the undated closed legs; the 07-27 weights upgrade it to open-class by the pre-declared rule) → **10 legs / 11 full-loop models**; K3 last in queue, truncates first |
| **R96** | 07-22 | **The OPTIONAL M2 psychometric module** fully pre-specified, registered-not-activated (Axis A per-model JND + the fed-delta overlay; Axis B the ~100–130-base ecosystem map; Tamer's dated write-time activation; the all-or-nothing reporting clause) |
| **R97** | 07-22 | **The differential downside deviation ratio seated** (Moody & Saffell 2001 eqs. (19)–(24), first-hand transcribed) → the **ten-name** hand-written canon; the secondary panel's execution path made precise (report-only, tier-30 floor, post-headline, priority −310; runbook §9(h)); H1 four frozen-unchanged |
| **R98** | 07-23 | **The Opus-5 full leg NOT exercised this cycle** — Tamer's stated budget decision ("I don't have money for both"), recorded pre-event; maximum footprint = the ~$1 M2 reading seat if R91's conditions fire, else the disclosure sentence; the generation pair → future work (Papers 2/3) |
| **R99** | 07-23 | **GPT-5.6 Sol + Terra full legs considered and DECLINED** (Tamer's budget decision, pre-event); the 3-point ladder (Luna 82.5 / Terra 84.3 / Sol 88.8) = the named FIRST Stage-2/Papers-2/3 extension; **Terra seated in M2** (~$0.30) so the M2 reading axis carries all three GPT-5.6 points; legs stay n=10 |

### 19b. What is and is NOT done (the state of record, 2026-07-23)

| Fact | Value |
|---|---|
| Design state | **UNFROZEN** (`frozen: false`; R94 governs when the freeze fires) |
| Amendments | through **R99** |
| Roster | **11 full-loop** (Opus + 10 legs); ~35 distinct models with M2 |
| **NOT done, by Tamer's order** | **NOT frozen · NOT launched · gates NOT run** (the leg gates need OpenRouter credit; they run pre-launch per R93) |
| Tamer's pending items | ① the Okhrati email (draft + this brief ready) ② the top-ups + the OpenRouter do-not-log toggle ③ the Windows-Update pause ④ UCL password rotation ⑤ the force-push decision (the `backup-2026-07-21` branch protects meanwhile) ⑥ **the full-campaign approval** → fires freeze→gates→launch |
| Next Claude work | **the writing month** (dimension 4 = the binding constraint under the raised bar) — needs no results, no spend |

### 19c. The verification state (as of 2026-07-23 — all first-hand-verified)

- **Freeze gate: 21 checks OK** (`freeze.py --check`; includes the arm-roster guard, the budget-mirror guard, the h1-baselines guard, the leg-roster match, the HF-pin refusal, the R97 canon lock).
- **Fifteen full-suite certifications, all exit 0** — the 15th run after "wave 2" (below); the suite is ~2,100+ tests with only the 3 permanent POSIX-only skips.
- **The 5-auditor final sweep (Tamer: "the deepest code review possible"; 2026-07-22 → wave-2 closure 2026-07-23) — fully discharged.** Five read-only auditors fanned over the R97 seam / stats / cluster / LLM-sandbox / paper-vs-code. **2 CRITICALs fixed:** ① the canary call sat *outside* its try-block — any canary-batch exception would have set neither event and hung the tiered line silently forever; ② the fixed `.pull_tmp` staging path raced across the 12 mode-D *processes* — a torn `record.json` was committable to the mirror (now pid-namespaced + prefix-excluded). **6 MAJORs fixed:** the h3 ladder-rerun priority passthrough (a hardcoded −100 would have jumped all legs); the F2 dirty-dir guard's glob missed `search*/` (dead for 11 of 12 lines); `--canary` names now validated; **the cluster spend ledger was never set on Myriad — R83 would have recorded nothing** (now per-line `spend_ledger_<tag>.jsonl`); `update_handoff` re.sub escaping + backup-branch carry-forward; the nine→ten leg staleness in CH6/PREREG + APPENDIX_B B.3.1 rewritten v2-accurate. **15 verified minors** (registry row 30 (a)–(o): the shared `headline_cvar_level()` helper across all report sites; pooled_bound/pair_did fail-loud guards; non-finite strips; the |total|>1e6 sandbox clamp; the leg-gate planning-price assert; archive-write-failure escalation + marker; resume-brief parser hardening; the CH6 §6.7 R97 slot; the stale-runbook SUPERSEDED banner — a stale 200k GO/NO-GO would have killed a correct 400k launch; 3 guard regression tests; the SGE job-cap launch-day pre-check; the h3 canary-exposure disclosure; the C6 priority inversion + C7 summary-clobber latents) — **all executed in wave 2 (commit `7d6d7a1`), closed 2026-07-23.** Verified-clean under the same sweep: the DDR math (independent re-derivation), the sandbox (escape attempts failed), bootstrap/BH/FZ0/TOST/IUT/CVaR conventions, the PS1s, ssh quoting, the priority ladder.
- **The pre-GO end-to-end audit (2026-07-22):** all four launch lines dry-ran GREEN verbatim (mode-D core with pack-2 + pipelined rungs; a leg line; the h3 line; the §9(h) secondary panel); the launcher spawns 12 lines matching the registered queue; two real defects caught + fixed (the R97 fail-before-ssh guard sat below the dry-run early-exit; runbook §2.0 step 4 still named the legacy single-line supervisor — now `mode_d_launch.ps1`).
- Also green: citations gate clean · rung-freshness gate green · all supervisor PS1s parse 0 · the off-machine backup branch (`backup-2026-07-21`) pushed · the handoff system is self-verifying (a machine-readable `handoff_state` block diffed against live facts at every session boot).

### 19d. The novelty fence (current entries — adjacent works verified first-hand; none occupies the cell)

The conjunctive novelty cell — *LLM authors reward CODE for a portfolio agent + multi-level tail feedback as the manipulated variable + pre-registered controlled comparison* — remains **empty** (triple-confirmed by independent sweeps; a fresh full sweep is DUE at the freeze, registry row 16, and the pre-submission sweep is mandatory). The live fence entries:

- **GIFT (arXiv 2606.08450, 7 Jun 2026 — "LLM-Guided State-Reward Interface for Financial RL"):** the newest adjacent paper, read first-hand and archived. The LLM generates state features *and* auxiliary rewards under PPO on 5-stock S&P panels, 3 seeds, win-rate counting — no pre-registration, no hypothesis tests, no scalar-vs-distributional contrast, and it **varies STATE and REWARD jointly** (exactly what our identification principle forbids). It does not occupy the cell; it *strengthens* the motivation (its own diagnostic finds free-form LLM generation unstable in finance — convergent with the numeracy-bottleneck mechanism). Must be cited + differentiated in CH2 (registry row 29).
- **RDA (arXiv 2606.01672):** the Eureka successor — VLM visual-trajectory diagnostics + subtask decomposition. Cite in CH2; differentiate precisely: **RDA enriches the feedback channel for performance; we CONTROL it for identification** — rich diagnostics would break the single-varying-factor design; our "coarse numerical reflection" is the manipulated variable, not a limitation (registry row 31c).
- **ELfolio (2025):** the standing scoop-watch entry (the one neighbour to manage); re-verified at every sweep.
- Also on the fence's "conscious decisions" record (registered so the fence shows *decisions*, not omissions): the OPRO/TextGrad/CodeGrad textual-gradient lineage (one CH2 line — our controlled-feedback loop vs optimization-maximal loops), and the dated pre-freeze rejections of XML-tagging, assistant-prefill, and execution-error-trace reflection (§10, §17c).
- The new v2 claim under fence protection: *"the first systematic open-weight replication suite in this lineage"* — currently hedged "to our knowledge"; the hedge stays unless the freeze-due sweep confirms.

---

## 20. Execution: the GO sequence, mode D, and the timeline

**Standing rule (R94 + Tamer's standing orders).** Every date below is a *planning reference*. **The freeze executes together with Tamer's full-campaign approval (GO step 1) and launch happens only on his separate explicit word — there is no scheduled trigger date.** The build is complete (all 8 v2 steps, committed, full-suite-green); the gates run pre-launch once OpenRouter credit lands.

### 20a. The GO sequence (runbook §2.0 — executed by Claude on the official GO, in this exact order)

1. **FREEZE** — `python scripts/freeze.py` (the one irreversible act; stamps the *recomputed* canonical hash + fresh bundle) → `freeze.py --check` (recorded == canonical, frozen: true, 21 checks).
2. **Provenance anchors** — tag `prereg-v2.0` + `prereg-freeze-<hash8>`; build the prereg bundle (sha → CHANGELOG); the public OSF/Zenodo deposit.
3. **Cluster sync freshness** — `git archive HEAD` → Myriad + the `GIT_COMMIT` marker (without it every record's code identity is None).
4. **LAUNCH — MODE D** — `powershell -ExecutionPolicy Bypass -File scripts\mode_d_launch.ps1` + `campaign_monitor.sh` (+ the sentinel). The **C0 canary fires first and HARD-STOPS everything before any Opus spend** if the path is unsound. (`campaign_supervisor.ps1` remains the single-line fallback if mode D must be abandoned mid-run.)

### 20b. Mode D — the maximum-parallel execution design (R88; the global-minimum configuration)

- **Twelve supervised launch lines** from one command: the **core** line (the §2 canonical tiered ladder + `--search-pack 2 --search-poll-secs 45 --pipeline-rungs`), the **h3** single-shot floor line (day-0, seeds 0–29 — previously the last *manual* dependency on every rung bank), and the **ten leg lines** (each the §9(b) line + the pack-2 search lane, at its ladder priority). Each line is self-healing (relaunch-on-death), has its own supervisor log, and polls staggered 20 s apart; one `STOP_CAMPAIGN` file stops everything.
- **The priority ladder enforces the registered queue natively:** core search/floor/tier-100 above the legs (bayes_opt hoisted to priority 0 — its 30 inherently-sequential GP proposals are the floor's true critical path; tier-100 at −100); the ten legs at **−200…−290 in queue order**; tier-189+ assurance blocks from −300; the H3 ladder completion at −300 (a follow-up invocation that must never jump the legs); the R97 secondary panel at **−310**, strictly last. Completion and calendar-gate truncation follow the pre-declared queue even though execution overlaps.
- **Pack lanes:** search waves run **pack-2** (the 6-generation reflection chains are latency-critical; pack-2 ≈ halves their wall time, and tight auto-sized walltimes make them prime backfill); winner/rung bursts keep **pack-5** throughput; C4 rungs are **pipelined** (all blocks eligible at once under the descending ladder — no drain bubbles; banking is unaffected: a rung banks only when it and every rung below are complete).
- **Canary-concurrency:** the C0 canary gates only what it protects — **Opus authoring**; the no-spend family arms + baselines start at L+0. The legs start ~**L+1h** behind the core (the canary shield). The h3 line's ~30 Opus authorings run unshielded by the canary — a disclosed, bounded trade (~$1–2; the STOP file is the mitigation).
- **Timings from the GO (R95-updated):** mechanism data ~**L+0.7 d** · the tier-30 floor ~**L+1.5–1.8 d** (BO-chain-bound — the honest estimate, not the throughput-only L+1.3) · **all ten legs ~L+4.5–5.5 d** · **tier-403 ~L+13–14.5 d** · the 99% rung (568) likely from a ≤ Jul-25 GO.
- **Named pre-launch steps:** the **mode-D synthetic mini-rehearsal** (~30 min, `--synthetic`, zero spend — the 12-line *concurrency* is the one unrehearsed surface; core + 2 leg lines, confirm clean supervisor logs, then STOP) and the **SGE job-cap check** (`qconf` for `max_u_jobs` vs the ~1,200 pipelined arrays; raise `--chunk-tasks` or drop `--pipeline-rungs` if capped — both ops-only).

### 20c. The calendar (planning references, not triggers)

| Phase | Window (reference) | What happens |
|---|---|---|
| **Now → GO** | — | **The writing month runs regardless** (CH1–CH5 need no results): the CH2-argument skeleton, CH1/CH4 depth passes, wiring the drafted D1–D10 keystones, the scannable tables. Tamer's items gate the GO: credit + toggle, the Okhrati email, the approval itself |
| **GO day** | on Tamer's word | §2.0: freeze (recomputed hash) → tag/bundle/deposit → sync → mode-D launch; C0 canary hard-stops pre-spend |
| **Campaign** | GO → ~GO+14 | mechanism ~L+0.7 → floor ~L+1.5–1.8 (bank the degree) → legs ~L+4.5–5.5 → rungs climb exogenously; **interim report pack ~Aug 6–8** to Dr Okhrati + the industry supervisors (registered, presentation-only effect); the campaign-window queue (dose-response tier, P3 sub-experiments, FTSE-lite panel build) fills API-quiet days |
| **Aug 11** | fixed | Myriad maintenance (second Tuesday) — jobs may die and requeue; the resume machinery absorbs it as an expected event |
| **Aug 14 (23:59Z)** | fixed, exogenous | **The leg calendar gate** — legs truncate in reverse queue order (K3 first, then Gemini), never reorder |
| **The single look** | at the achieved rung | the bank gate's six-step runsheet (archive integrity → resume audit → analyze → variance → fed-delta SNR → prereg bundle) → **the one confirmatory look** (gate + IUTs + TOST + Bayes) → numbers into the PDF under evidence-ledger grades |
| **Final writing** | → Aug 22 | CH6/CH7 completed; word surgery to the 10k body AFTER the final number refresh; citations + the mandatory novelty-fence sweep; ethics + AI-disclosure |
| **Polish + submit** | Aug 22–29 | zero-warning PDF; the any-discipline reader gate (registry row 24); fresh-agent rubric read-through; **submit 28–29 Aug** (buffer to Sep 1) |

---

## 21. The four-paper map

The one frozen machine is designed to yield four papers (named in v2 so the structure is by design, not salvage):

- **P1 — the main study → TMLR** (the frozen confirmatory study: LLM authors risk-sensitive reward code, multi-level tail feedback, pre-registered controlled comparison).
- **P2 — numeracy / legibility → an NLP venue** (the designer-numeracy / legible-format lever; the R96 psychometric module is budgeted as a P2-module line if activated; the say–know-gap corroboration and JND methodology live here).
- **P3 — the capability-gradient survey** (the 35-model M2 reading-link survey; the g(capability) gradient; the open-weight replication suite; the **R99 GPT-5.6 3-point family ladder is the named first Stage-2 extension**, and the **R98 Opus generation pair** is likewise Papers-2/3-bound).
- **P4 — the evaluation protocol** (the frozen, family-wise-controlled, placebo-controlled test protocol as a reusable instrument).

---

## 22. Limitations and threats to validity

The dissertation carries a *dedicated, exhaustive* limitations register (UCL names this exemplary practice). The four foregrounded in the Discussion:

1. **Construct** — the fed signal is six left-tail scalars, *not* the full return distribution; the claim is only that it spans the coherent-risk class.
2. **Training budget** — one fixed, matched budget at the measured learning-curve knee (400k steps), *not* "at convergence"; every result is read at that budget.
3. **Selection blindness** — the selector is deliberately tail-blind (λ = 0); conservative, and it places the study on the boundary of the Null branch.
4. **External validity** — one universe (US large-caps), one window, one *confirmatory* model — so cross-model claims are made only at the strength the ten descriptive legs support.

The full register (Appendix B), one line each:

- **B.1 Construct:** tail vector not the distribution (B.1.1); tail-blind selection biases *against* an effect (B.1.2); single-estimator fed CVaR with finite-sample bias, guarded, with the fed-signal SNR exhibit quantifying resolvable components (B.1.3).
- **B.2 Internal:** **endogeneity of the fed signal** — two coupled loops; critic-agnostic ≠ agent-independent (B.2.0); fixed 400k budget — matched-compute by construction, "at the measured knee" (B.2.1); reward-scale → entropy confound, neutralised by PopArt + a popart-disabled ablation (B.2.2); occasional critic divergence, diagnosed (B.2.3); single deterministic validation path, mitigated by the seed ladder (B.2.4); pretraining contamination structurally unreachable and arm-cancelling (B.2.5); **authoring variance / unit-of-analysis** — the confirmatory contrast re-runs *one* selected program per arm, so its interval generalises to the *selected programs*; the channel-level claim is carried by the **mechanism kernel across all candidates**, not by H2 — and the Stage-2 qwen-9B search replicate would upgrade this from disclosed to quantified (B.2.6).
- **B.3 The designer:** **single confirmatory author** — the ten replication legs (≥6 vendors, five open-weights with hash-pinned checkpoints) are report-only at the tier-30 floor, so cross-model claims are descriptive, never confirmatory; the asymmetry is a registered design choice (B.3.1, v2-rewritten); designer numeracy / responsiveness as a format-dependent, tokenization-rooted weakness (B.3.2); narrow search width **K = 5** — a disclosed scope choice, not a power claim (B.3.3); **prompt portability across replication legs (B.3.4 — NEW, 2026-07-23):** the ten legs receive the SAME Opus-calibrated prompts; industrial meta-prompting studies find prompts tuned on one model can degrade **20–30%** on another (citation to verify at wiring; arXiv 2508.01443 candidate), so part of any leg's shortfall may reflect instruction-format sensitivity rather than the tail-reading construct. *Mitigations:* the pre-launch compliance gate screens each leg's executable rate BEFORE results (format-incapable legs are excluded and disclosed, never scored); the SWE-bench-Verified anchor absorbs general instruction-following into the capability axis; and identical prompts ARE the replication design — varying them per leg would confound the model axis with prompt tuning.
- **B.4 External / data realism:** single universe/period/cohort, with the PIT walk-forward re-evaluation shipped (B.4.1); delisting surcharge conservative and band-invariant — the measured ADR-051 resolution (B.4.2); flat vs concave (square-root-impact) transaction costs, swept (B.4.3); softmax simplex can't reach exact cash, with an empirical bindingness diagnostic (B.4.4); risk-free rate = 0 headline, common-mode, DGS3MO-excess robustness re-run (B.4.5).
- **B.5 Statistical:** tier-conditional power — floor n=30 MDE ≈ 0.120 DSR ≫ the 0.05 SESOI, so a floor non-rejection reads "inconclusive", with rungs 279/340/403/568 delivering 80/90/95/99% assurance (B.5.1); ES-backtest power under heavy tails, with the stationary-bootstrap headline + a DM size calibration + a Hill-index check (B.5.2); CSCV bias near zero mean, cross-checked by DSR (B.5.3); DSR effective-trials under correlated search (B.5.4); the direct upper-tail one-sided p construction (B.5.5); descriptive Sharpe/ρ conventions (B.5.6); **single-look sealed test** — what makes it a *severe* test rather than a second search space (B.5.7).
- **B.6 Reproducibility:** LM non-determinism → replay-from-archive (B.6.1); fixed-device byte-identity (B.6.2); the proposal re-scoping disclosed, pending written sign-off (B.6.3); pre-registration provenance (B.6.4); H1 descriptive-only (B.6.5); the prototype is not evidence (B.6.6).
- **B.7 Future work:** λ>0 selection variant; reason-gated delisting re-pull; corner-reaching action parameterisation; a second universe/period; reward-distance deep-dive; quality-diversity search; hierarchical-Bayes re-analysis. (MCS, Bayes-null triangulation, mediation, regime-conditional and synthetic-null exhibits are BUILT instruments with CH6 slots — results, not future work.)
- **v2 additions still to land in the register at write time (registry row 17):** per-leg TOSTs at floor-30 inconclusive by construction (the pooled R86 bound is the informative statement); open legs served fp8 via a pinned provider (the executed author = the served variant of the hash-pinned weights); no self-hosted leg (scope decision, disclosed); three closed legs lack dated snapshots (Luna/Gemini/Sonnet-5 id-convention — disclosed; K3 and Haiku are date-pinned); the M2 secondary anchor shares method variance with the outcome; the calendar gate may truncate back-of-queue legs (pre-declared, reported).

---

## 23. Grade strategy and examiner alignment

**The reality.** Graded on the submitted PDF alone (no viva) by **Dr Ramin Okhrati** — a measure-theoretic probabilist working in coherent risk, offline RL (CQL), and AI/LLM-risk — plus a **second marker from any discipline**. The UCL IFTE0008 rubric has **four equally-weighted dimensions where the weakest caps the mark**: (1) background + independence of thought; (2) research design + originality; (3) novelty + significance (90–100 = *journal-publishable*); (4) communication — clear to a non-specialist (the named single biggest risk). Hard limits: **10,000-word main body** (maths, code, figures, tables, footnotes, references, appendices all excluded); the **16-section order**; ~60% core; Harvard referencing; deadline 1 Sep.

### 23a. The grade-inflation adjustment (supervisor-confirmed, 2026-07-21 — binding context)

The bar is **raised this year: last year's distinction ≈ this year's merit**, so every dimension needs *unambiguous* distinction evidence and **borderline evidence rounds DOWN**. **Communication (dimension 4) is the binding constraint** — hence the writing month starts now and needs no results. The operational response is registry rows 19–24, five of which are already **drafted at submission quality (D6–D10)**:
- **Row 19 (D6):** the SESOI argued from *decision-relevance* in CH4, never asserted.
- **Row 20 (D7):** **H4 promoted to a named result** (no literature shows an LLM designer beating matched-compute non-LLM search — demonstrating or honestly not demonstrating that edge is itself the contribution) + the explicit Coache–Jaimungal CH2 differentiation.
- **Row 21:** the ≥60%-core ratio re-measured post-v2 at surgery (Discussion was the thinnest and gets nudged up).
- **Row 22 (D8):** the **independence narrative** — the research journey (Feb proposal → disciplined pivot → v1 freeze → industry feedback → documented pre-data v2 revision) told as *Tamer's decisions*: under heavy-AI-assistance disclosure this is the auditable evidence of independence of thought, and the guidelines sanction the pivot explicitly.
- **Row 23 (D9):** **publishability made demonstrable, not asserted** — the public prereg DOI cited in the PDF, the 4-paper map, the NatWest interim pack as artifacts, framed against the 90–100 descriptor with TMLR named.
- **Row 24:** the **any-discipline reader gate** at pre-submission — a genuine non-specialist reads CH1 + the plain-language paragraphs + every figure caption cold; anything they stumble on gets rewritten; front-matter exactness (Moodle cover, exact title, Arial ≥10 / 1.5 spacing) rides with it.

**Okhrati's revealed grading function (the compass) — and how the design answers each:**
- **Intuition > technical correctness** → every result gets a plain "why should the reader believe this" before the machinery (this whole brief is written that way).
- **Depth > breadth** → the mechanism kernel is developed as a deep causal study, not scattered; v2 breadth lands appendix-first (registry row 14: the body carries ≈1 tight paragraph per v2 axis; pins/queue mechanics/synthesis math go to word-excluded appendices).
- **Honesty rewarded** → the null is the prize; it is stated plainly and bounded, never spun.
- **Motivate the method with the data** → the leptokurtosis / CVaR-crossover / co-crash EDA *earns* the hypothesis.
- **Originality foregrounded** → the empty-cell conjunction + the four affirmative contributions + the fingerprint matrix (to our knowledge the first ex-ante multi-account × multi-instrument registration in LLM-agent studies).
- **Mechanics he docks** → wall-clock compute reported (and now the realized dollar cost, prominently — the NatWest line); faultless figure/table cross-referencing; the exact risk-measure citation chain (Artzner axioms; VaR fails *subadditivity* specifically; CVaR = ES coherent; ES not elicitable alone but (VaR, ES) jointly elicitable — never misattributed; Khraishi & Okhrati 2022 for the CQL bridge; Hartley…Okhrati ACL 2025 as the golden neighbour).

**The four binding authorities** (checked explicitly on every substantive decision): (1) the ★ priorities (95%+ floor, world-class/publishable, deep, corpus-grounded + genuinely novel); (2) Okhrati's grading function; (3) the NatWest/Raad+Stefan industry feedback — all six points adopted structurally, each landing as a named PDF artifact (the open-weight suite, one-frontier + cost discipline, the three-layer reproducibility statement, the empirical 15/15 model-usage survey, the practitioner's checklist, the 4-paper map), with the standing guardrail that industry feedback lands as breadth/communication/publication strategy, never as a reason to weaken the confirmatory logic; (4) the IFTE0008 guidelines. Under the raised bar, conflicts resolve to the priorities, and borderline evidence rounds down.

---

## 24. Anticipated questions and how the design answers them

*Prep for the meeting — the sharp questions a supervisor is likely to raise, and the honest one-line answer each has by construction.*

- **"Isn't a null just an underpowered failure?"** No — it is reported as a *bounded equivalence* (TOST inside ±0.05) or explicitly *inconclusive* when the MDE exceeds the SESOI; the seed ladder is sized to reach 95% (plausibly 99% under mode D) equivalence assurance, and achieved-rung power is always stated, with a registered severity-curve presentation.
- **"Why only one confirmatory model?"** A null on a *weak* model is a capacity artifact; the frontier seat is what makes the null *informative* (REvolve's argument, and the 15/15 survey shows it is the lineage norm). v2 adds ten replication legs (open + closed, ≥6 vendors) as report-only breadth and reproducibility — without weakening the confirmatory logic.
- **"The fed tail is measured on the agent's own returns — isn't that circular?"** It is *endogenous*, and we say so; H2 is honestly a comparison of two coupled reward→policy→measurement loops. The three-way split (fed/selected/tested on different data) is what attributes any effect to the channel.
- **"Isn't the effect just betting-against-beta / low-vol?"** Pre-registered factor-attribution ladder (up to FF6 + BAB + QMJ, Newey–West), computed and reported as a disjoint secondary — the pre-empt is built in.
- **"Why is Sharpe only ~1 — can't you beat the benchmark?"** A sustained Sharpe near 1 is elite; crazy backtest Sharpes signal leakage, which the PIT / survivorship-free / purged design specifically prevents. The study cares about the *difference* between reward designs, not the absolute level (the claim is registered as "comparative, not beats-the-market").
- **"Does the LLM actually use the numbers, or echo them?"** That is exactly SQ3 — the identifier-invariant AST test catches token-echo, the legibility ablation separates "can't read" from the guided-comparison probe's "won't use", and the five-account fingerprint scores the rival explanations against each other — now with external corroboration that the failure mode is real (the say–know gap, arXiv 2602.07812).
- **"Is 30 stocks enough?"** Yes, and it is argued, not asserted (registry rows 26–27): more assets at the frozen matched budget = less power for the arm contrast (the thing under test); 20–40 names capture most diversifiable-risk reduction; DJIA-30 is the field's de-facto universe and our PIT construction strictly dominates the common practice; and the tail structure to exploit is demonstrably present on this panel (kurtosis 15.25, deep-tail ×1.66, co-crash 19.7%).
- **"Same prompts for every model — doesn't that disadvantage some legs?"** Possibly, and it is a registered limitation (B.3.4, 20–30% cross-model prompt degradation in industrial studies) with three mitigations — the pre-results compliance gate, the capability anchor, and the fact that identical prompts *are* the replication design (per-leg tuning would confound the model axis).
- **"K = 5 search width is narrow."** Disclosed as a scope choice, not a power claim; a wider K is named future work, and the Stage-2 qwen-9B search replicate would quantify authoring variance directly.
- **"What does this cost?"** Expected **~$28 all-in** for the whole study (Anthropic ~$10 expected/~$27 worst — funded $25.91; OpenRouter ~$18 expected/~$30 worst — top-up pending), tracked per-call under the advisory R83 ledger and reported prominently — inside the lineage's honest-cost band (RD-Agent <$10, AI-Scientist <$15/paper).
- **"What would make you abandon the numeracy interpretation?"** Its registered falsifiers: a null legible-minus-raw differential refutes the legibility form (A3 wins); recovered responsiveness under CI-annotation with intact raw accuracy in M2 reassigns it to A5 (a stance, not a deficit); a rising capability gradient scores for the rival capacity account. Every branch is named ex-ante.

---

## 25. Glossary

- **Arm** — one experimental condition (a feedback design or a search baseline). Seven total; legs run the five LLM arms only.
- **B\*** — the training budget per candidate: **400,000** environment steps (R77 — the measured learning-curve knee).
- **Blackwell dominance** — an information structure is "at least as informative" as another iff the second is a garbling (post-processing) of the first; then it yields weakly lower Bayes risk for *every* loss and prior.
- **CRN (common random numbers)** — using the same seeds across arms (and legs) so shared noise cancels in the paired contrast.
- **CVaR / ES (conditional value-at-risk / expected shortfall)** — the average return in the worst α-fraction of outcomes; coherent; here signed so *more negative = worse*.
- **DDR (differential downside deviation ratio)** — Moody & Saffell 2001's own downside companion to the DSR (eqs. (19)–(24)); the R97 seat in the ten-name canon.
- **DSR (Deflated Sharpe ratio)** — a Sharpe corrected for multiple trials and non-normality; the selection metric (λ=0).
- **Endogenous fed signal** — the tail is measured on the trained policy's *own* returns, so it depends on the agent it steers.
- **EVT / GPD** — extreme-value theory / generalized Pareto distribution, used (peaks-over-threshold) for the 5% and 1% CVaR levels.
- **g(capability)** — the envelope-realization gap as a function of author capability; the leg suite traces it; flat-at-≈0 is the registered prediction.
- **IUT (intersection-union test)** — a conjunction of one-sided tests; supported iff *all* legs reject; the conjunction is itself the multiplicity correction (Berger 1982).
- **JND (just-noticeable difference, δ75)** — the R96 module's per-model numeric discrimination threshold from a 2AFC psychometric fit; the overlay = the share of realized fed deltas below it.
- **Le Cam deficiency δ(E′, E)** — how far one experiment falls short of another; δ(scalar, vec) > 0 is the "worst-case price of the scalar."
- **Leg (v2)** — one replication model running the 5 LLM arms × 30 candidates at the 30-seed floor. **Ten** legs; report-only; queue-ordered; calendar-gated.
- **Mode D** — the R88 maximum-parallel launch: 12 supervised lines under a priority ladder that natively enforces the registered queue.
- **PBO / CSCV** — probability of backtest overfitting via combinatorially-symmetric cross-validation; the primary overfitting guard.
- **Pooled bound (R86)** — the 90% seed-block-bootstrap CI on the pooled cross-leg CVaR-5% difference; the registered cross-model bounded-null statement.
- **PopArt** — a value-target normaliser that neutralises reward-scale differences across arms.
- **Rung / tier** — a seed count on the assurance ladder [30…568], each a complete study.
- **rliable IQM** — the interquartile mean per-seed aggregation with stratified-bootstrap CIs (Agarwal et al. 2021).
- **SAC (Soft Actor-Critic)** — the fixed off-policy RL agent (with TD3's twin critics).
- **Say–know gap** — models decode numeric magnitudes internally (>90%, linear probes) yet verbalize comparisons at 50–70% (arXiv 2602.07812); the external corroboration of the A2 readout account.
- **SESOI** — smallest effect size of interest = 0.05 (deflated-Sharpe units); the equivalence margin.
- **Simulated-online RL** — off-policy learning that *collects its own transitions* against a historical-replay simulator (not offline RL).
- **σ_D** — the seed-to-seed SD of the paired A−B difference (≈ 0.369 on the Sharpe/DSR leg); what forces the large seed count.
- **T0 floor (R84)** — the leg-inclusion criterion: the equal-weight benchmark's mean per-seed Sharpe on seeds 0–29; arm-symmetric, so it cannot distort the permutation test's size.
- **TOST (two one-sided tests)** — the equivalence test: conclude "same within ±SESOI" iff the whole CI fits inside the margin.
- **Three-way decoupling** — the tail is *fed* on train, *selected* on a tail-blind validation criterion, *tested* on the sealed test split.

---

*Prepared from the live design of record (`PREREGISTRATION.md` + rows R78–R99 · `config/preregistration.yaml` / `legs.yaml` / `m2_models.yaml` · `docs/HANDOFF.md` · `docs/MODEL_ROSTER_2026-07-22.md` · the runbook §2.0/§9/§10 · `docs/V2_WRITE_TIME_REGISTRY.md` rows 1–32 · `paper/APPENDIX_B_limitations.md` · `CHANGELOG.md`), every load-bearing figure verbatim-checked on 2026-07-23. Campaign-dependent values are marked **[FROM CAMPAIGN]** in the paper skeletons and are not invented here. Flag anything you want expanded before the meeting.*
