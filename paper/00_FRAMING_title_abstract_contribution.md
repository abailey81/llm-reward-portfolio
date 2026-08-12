# Dissertation front matter — title, abstract, contribution, framing (DRAFT v2 — mechanism-led, 2026-07-01)

**Status.** Bankable draft — written to be robust to the campaign outcome (null / mixed / positive).
Uses the *retitled* construct ("multi-level tail-risk feedback", NOT "the distribution"), the
off-critic 3-way decoupling as the method contribution, the DLM/Eureka-distinguished novelty, and the
pre-registered (Mayoian-severity) null framing. Every result sentence is marked `[RESULT]` with the honest
current (directional-prototype) fill + a campaign-upgrade slot. Adapt voice; do not let any sentence
drift to an unqualified "distribution" or "the LLM is a better optimiser."

---

## 1. Title (pick one; all are method/question-framed, none claims a win)

1. **Multi-Level Tail-Risk Feedback for LLM Reward Design: A Pre-Registered Study in Risk-Sensitive
   Portfolio Reinforcement Learning**
2. **Does Showing a Language Model the Downside Change the Reward Code It Writes? A Pre-Registered,
   Off-Critic Test in Risk-Sensitive Portfolio RL**
3. **Can Tail-Risk Feedback Improve LLM-Designed Reward Functions? An Off-Critic, Pre-Registered Study
   in Portfolio Reinforcement Learning**

*Recommendation (v2, mechanism-led):* with the mechanism now the headline, **title (2) — the
"does showing the model the downside change the reward code it writes?" question — is the recommended
submitted title**, since it leads with the mechanism the dissertation is built around; (1) is the precise,
more conventional method-forward alternative. Avoid "distributional feedback" in the title — it is the
construct overclaim the framing discipline forbids.

---

## 2. Contribution statement (the four things you actually contribute)

This dissertation makes four contributions, none of which is contingent on a positive result; the mechanism
characterization (C4) is the foregrounded headline, with the comparative-performance machinery (C1–C3) as
the rigorous backdrop that makes it credible:

- **C1 — An off-critic feedback instrument that isolates the feedback content.** A method for feeding an LLM
  reward-designer the *realized-return lower tail* (CVaR at 5/10/25%, a high-variance 1% level, left-
  tail mass and robust skew) measured **off the critic** from realized returns, while the RL agent is
  held byte-identically fixed across arms. It isolates the feedback *content* as the manipulated variable,
  **not** an exogenous measurement: the fed tail is *endogenous* to the policy it steers (two coupled
  reward→policy→measurement loops), so the comparison is between coupled loops — the legitimate object of
  study, honestly disclosed. The instrument is **three-way decoupled**: the tail is
  *fed* on the training split, candidates are *selected* on a tail-blind validation Deflated Sharpe
  (λ=0), and the hypothesis is *tested* on empirical CVaR over a sealed test split — three different
  estimators on three different data partitions, so a tail effect is attributable to the feedback
  channel and cannot be a self-grading artefact. To our knowledge this three-way separation is novel
  in LLM-reward-design and in RL-for-finance, where prior work conflates at least two of the three.

- **C2 — A pre-registered comparative-inference protocol that yields a bankable result of either
  sign.**A cryptographically frozen design (hypotheses, arms, budget, seeds, splits, embargo,
  tail-diagnostic set, and analysis plan fixed before the sealed test leg) with intersection–union
  tests, a placebo and a structure-shuffled ("deranged-tail") control, deflated Sharpe ratios, and
  combinatorial probability-of-backtest-overfitting. A non-rejection is reported as a bounded,
  pre-registered equivalence — or, when the minimum detectable effect exceeds the pre-registered SESOI,
  as a calibrated **INCONCLUSIVE** verdict (Lakens) — never as an underpowered failure.

- **C3 — A decision-theoretic envelope delimiting when distributional feedback can help.** A short
  theory (Blackwell sufficiency / garbling; Kusuoka coherent-risk spanning; CVaR distributional-robustness
  duality) establishing that an *optimal* user of the lower-tail statistics weakly dominates an
  optimal user of a scalar risk summary — an *envelope* an optimal user attains, which a bounded language
  model coupled to a fixed agent may not realise — and the conditions (λ>0 selection, responsive designer)
  under which the bound is strict vs vacuous — turning the empirical question into a falsifiable prediction
  (the §1a prediction table), so a result of either sign is a *confirmed or refuted prediction* rather
  than a bare measurement.

- **C4 — A mechanism characterization that *locates* where the feedback channel acts (the headline).** A
  pre-specified, report-only causal decomposition of the chain *fed tail signal → authored reward code →
  trained policy → realized tail*into three sub-questions — **responsiveness** (does the signal move the
  code?), **transmission** (does the code move the outcome?), and **specificity** (is it genuine use of the
  tail content or a surface echo, and is any failure a numeric-legibility bottleneck?) — instrumented by a
  responsiveness statistic, a fed→code→outcome mediation, an identifier-invariant structural test, and a
  legible-format ablation, all disjoint from the confirmatory testing family. This turns a null from an
  absence of evidence into a *located* finding about *where* the channel breaks, which — with the
  performance equivalence as its rigorous backdrop — is the dissertation's headline and originality kernel.

---

## 3. Abstract (DRAFT v2 — mechanism-led, 2026-07-01; ~300 words; bankable-null variant)

Reward design is the central bottleneck in applying reinforcement learning to risk-sensitive financial
control: a reward well specified in the mean can yield a policy that is profitable on average yet ruinous
in the tail. Large language models can now author reward-function *code* and refine it from feedback, but
that feedback is typically a scalar score that conveys little about the *shape* of the outcome distribution
the reward implicitly selects. We ask a **mechanistic** question: does showing the LLM reward-designer the
**downside** — the realized-return lower tail (conditional value-at-risk at several levels, left-tail mass
and skew), measured *off the critic* from realized returns — change the reward *code* it writes, and does
that change propagate to the trained agent's realized tail behaviour? We cast this as a three-link causal
chain — **fed tail signal → authored reward code → trained policy → realized tail** — and ask, through
three pre-specified sub-questions (responsiveness, transmission, specificity), not merely *whether* richer
feedback helps but *where* the channel acts or breaks.

We isolate the feedback channel as the sole manipulated variable: five LLM arms share one fixed soft
actor–critic agent, one matched candidate budget and identical prompts, differing *only* in the feedback
block; four non-LLM search baselines (the H4 optimiser portfolio) bound the procedure. The design is **pre-registered and
cryptographically frozen**before a sealed 2020–2026 test leg, with the signal *fed* on the training split,
candidates *selected* on a tail-blind validation Deflated Sharpe, and the hypothesis *tested* on empirical
conditional value-at-risk over the sealed split — a three-way decoupling so any effect is attributable to
the channel rather than to a self-grading estimator. The performance contrast is decided by co-primary
intersection–union tests against the scalar, placebo and scalar_cvar5 comparators, with a structure-shuffled (deranged-tail) control reported alongside; the mechanism is read off a
responsiveness statistic, a fed→code→outcome mediation, and an identifier-invariant test of whether the
model *uses* the tail content or merely echoes its surface.

**[RESULT — campaign slot.]** *Current honest fill:* in a directional prototype the apparent tail advantage
did not survive its own zero-information placebo, consistent with the pre-registered null. A null here is
not an absence of evidence but a **located** one: the chain's break — predicted at the first link, where a
numeric-legibility bottleneck may stop the model from reading close tail values — is the finding. We report
the performance contrast as a bounded, pre-registered TOST equivalence against the SESOI, credited on
error-statistical severity (the frozen, deviation-free protocol; Mayo; Rubin 2025) and forking-paths
avoidance (Gelman & Loken 2014) rather than a bare *p* > 0.05, and we contribute an off-critic feedback
instrument, a pre-registered comparative-inference protocol, a decision-theoretic envelope delimiting when
tail feedback can help, and a mechanism characterization that *locates* where it acts.

> **Conditional-positive result sentence** (swap in iff the campaign IUT rejects on the tail leg and
> survives placebo + shuffled-placebo): "In the confirmatory campaign, multi-level tail-risk feedback
> improved the sealed-test left tail (CVaR-5%, intersection–union across three controls) at parity of
> risk-adjusted mean return (Sharpe leg non-significant) — the channel acted on the dimension it
> informs — while the structure-shuffled control ruled out a format artefact."

---

## 4. Novelty / positioning paragraph (DLM- and Eureka-distinguished — keep this exact altitude)

The contribution is *not* "an LLM can design reward code" (Eureka, Text2Reward, DrEureka) nor
"distribution beats scalar" stated loosely — Eureka already feeds per-component scalar *trajectories*,
and CARD (2025) reports beating a human reward oracle without any distribution. The empty cell this
work occupies is the *conjunction*: (i) the LLM authors reward **code**, (ii) the iteration signal is
the realized-return **lower-tail distribution of outcomes** (not point statistics of reward
components), (iii) in a **risk-sensitive financial, no-oracle** domain, (iv) under **pre-registered
comparative inference**with the off-critic three-way decoupling. The nearest neighbour is the
Decision-Language Model (Behari et al., NeurIPS 2024), which also proposes reward code and iterates on
a simulated *distribution* — but its distribution is a spread over demographic state-features in
public-health resource allocation rather than over realised returns, and there is no pre-registered tail
inference. ⛔ **"the agent is not held fixed off-critic" was RETRACTED 2026-08-10 and is deleted here.** DLM
§4.3 p. 5 trains one PPO policy network under each proposed reward, so it *does* hold a learner fixed; the
old claim rested on a quotation taken from DLM's §2 Related Work. See Appendix H.2 item 7. The conjunction
survives on domain, feedback content and risk-sensitivity. In finance the cell stays empty too: GIFT (2026) may only select/transform/compose rewards from
a registered risk-rule library (parameters clipped before execution — constrained, not open-ended,
authorship), jointly with the state, on generic scalar diagnostics; ELfolio (2025) evolves strategy code on
a scalar Sharpe fitness — our control condition; AlgoEvolve (June 2026) meta-evolves trading-strategy
programs on a return-plus-consistency fitness with no RL agent and no reward function; and the field's most
explicit feedback vector — RD-Agent(Q)'s eight scalars — tops out at max-drawdown, with no CVaR/ES/quantile
anywhere. The concurrent "feedback engineering" workshop study (Gallego 2026, ICML NExT-Game) compares
sparse-vs-dense feedback for LLM-synthesised *policy* code — no reward authorship, no placebo/structure
controls, no inferential statistics, no tail axis. State the delta in one sentence and cite-and-distinguish
DLM, Eureka, CARD, GIFT, ELfolio, AlgoEvolve, RD-Agent(Q), and Gallego explicitly;
never let the abstract elevate the (descriptive, comparator-snooped) "beat-the-human" H1 to the
novelty axis.

**The outward one-sentence positioning (D2, integrated 2026-07-13 — abstract-grade; softened per the
honesty register):**To our knowledge this is the first theory-grounded, pre-registered test of whether
an LLM reward-designer is a **Bayes-responsive user of risk information**: whether the *content* of
distributional feedback — not its format, length, or vocabulary — changes the reward code the model
writes, and whether that change propagates to the trained agent's realised tail behaviour. The question
instantiates the general "do LLM optimizers use feedback content?" problem in the one arena where the
answer is checkable against decision theory, with portfolio construction as the testbed rather than the
object: an information-theoretic envelope says the fed tail vector *cannot hurt* and generically helps a
Bayes-responsive designer, so a pre-registered null cleanly localises a failure of responsiveness — which
the mechanism analysis traces ⟨CAMPAIGN: to the measured break in the chain, adjudicated among five
registered rival accounts⟩.

---

## 5. Construct disclosure (insert verbatim near the first use of "tail-risk feedback")

The "multi-level tail-risk feedback" fed to the designer is a vector of six left-tail scalars
(CVaR-5/10/25%, a high-variance CVaR-1%, left-tail mass beyond −2σ, and a robust left-tail skew),
estimated empirically with an extreme-value (GPD) tail for the 5%/1% levels. It is **not** the full
return distribution: it carries no central moments beyond the mean (supplied separately as the scalar),
no right tail, and no full quantile grid. We therefore name the construct "multi-level tail-risk
feedback", not "the distribution" — the theory (§C3) shows these statistics span the law-invariant
*coherent-risk* class (Kusuoka), which is the precise and defensible claim, and we make no claim about
non-coherent or upside features of the law.

---

## 6. Honest result-framing templates (no viva → these must be pre-written, not improvised)

- **Null / mixed (most likely):** "Consistent with the pre-registered prediction, we find no evidence
  that multi-level tail-risk feedback improves the realized left tail beyond a structure-matched
  placebo at the smallest effect size of interest; the TOST equivalence bound is [X] in validation-DSR
  units (INCONCLUSIVE if wider than ±0.05). We characterise *why* via the reward-program differential:
  the de-seeded designer wrote [more/equally/fewer] tail constructs under tail feedback, with
  responsiveness [sign] — the mechanistic signature the theory predicts for the [Strict/Weak/Null]
  branch." This is a **contribution**, not a failure: a pre-registered null on a clean instrument is
  publishable and bankable for a Distinction.
- **Positive (tail leg only):** use the §3 conditional-positive sentence; immediately bound it with
  "at parity of risk-adjusted mean" and the placebo/shuffled-placebo survival, and never generalise to
  "LLMs use feedback content" beyond the single Claude family run (§ limitations).
- **Negative-but-mechanistic:** if the designer demonstrably ignored the fed tail (responsiveness ≤ 0,
  no code-level signature), report it as the *Null branch confirmed* — the channel exists but this
  designer did not exploit it — which is a clean, citable finding about LLM-optimizer responsiveness.

---

## 7. Full-document plan — what is bankable NOW vs gated on the campaign

UCL ~10,000 words; no viva ⇒ communication + self-disclosure are dominant levers. Write order by
grade-weight; everything marked **[NOW]** is bankable regardless of the campaign.

| Section | ~words | Status | Notes |
|---|---|---|---|
| Title + Abstract + Contribution | 350 | **[NOW]** | this file; highest-leverage paragraph |
| Introduction + the empty-cell positioning | 1,200 | **[NOW]** | §4 here; cite-and-distinguish DLM/Eureka/CARD |
| Related work | 1,200 | **[NOW]** | refs.bib is clean + verification-disciplined; DLM in core bib |
| Theory (Blackwell/Kusuoka envelope + §1a prediction table) | 1,400 | **[NOW]** | C3; the rigour that is currently invisible — surface it |
| Data + EDA | 1,000 | **[NOW]*** | stylised facts regenerated from the ACTIVE univ5 Split-C train window (2026-07-02) |
| Methods (instrument, arms, off-critic decoupling, freeze, inference) | 2,600 | **[NOW]** | add the system diagram + the rigour ledger as a table |
| Results | 1,500 | **[CAMPAIGN]** | structure now (tables/figs as placeholders); fill on the run |
| Discussion | 1,000 | **[NOW]** | lift from 700; lead with the bankable-null + mechanism |
| Conclusion | 250 | **[NOW]** | |
| Limitations appendix (word-excluded) | — | **[NOW]** | L1–L19 + endogeneity (V6), single-Claude (V10), softmax-cash (V14), training adequacy |
| Rigour-ledger table (in-body, CH4 Table 4.1) | — | **[built]** | docs/RIGOUR_LEDGER.md → examiner-facing in-body table (consolidated from the former appendix plan, 2026-07-04) |

\*Data chapter: F3 (stylised facts) regenerates from the ACTIVE univ5 panel's Split-C train window
(2005–2016) via `scripts/make_figures.py` — the Split-C numbers (excess kurtosis 15.25, −5σ ×~10⁴,
CVaR crossover ×0.84→×1.66, co-crash 3.3%→19.7%) supersede any pre-Split-C EDA figures (14.52/20.4%
were the old 2005–2014 window; a superseded IQN brief is older still).

**Gated on you (cannot be done from here):** run `freeze.py` (1 command → makes the pre-registered-null
claim literally true; the freeze hash recorded by `scripts/freeze.py` at freeze time); run the confirmatory campaign on the GPU (with the 9 arms
incl. `placebo_shuffled`, σ_max logging, the learning-curve convergence ladder, and the delisting band
reported); obtain the supervisor's written sign-off on the proposal-pivot disclosure before the
"with my supervisor's agreement" sentence enters the PDF.

**Highest-leverage next writing targets (I can draft each now):** (a) the Theory chapter + §1a
prediction table prose [C3 — the invisible rigour]; (b) the Methods chapter with the system diagram +
rigour-ledger table; (c) the Limitations appendix [the dominant no-viva grade lever]; (d) the
Introduction + positioning. Any of these is bankable today.
