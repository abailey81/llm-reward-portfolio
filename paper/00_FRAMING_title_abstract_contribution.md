# Dissertation front matter — title, abstract, contribution, framing (DRAFT v1, 2026-06-26)

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

*Recommendation:* (1) for the submitted title (precise, method-forward, no overclaim); (2) as the
intro hook. Avoid "distributional feedback" in the title — it is the construct overclaim the framing
discipline forbids.

---

## 2. Contribution statement (the three things you actually contribute)

This dissertation makes three contributions, none of which is contingent on a positive result:

- **C1 — An off-critic feedback instrument that isolates the channel.** A method for feeding an LLM
  reward-designer the *realized-return lower tail* (CVaR at 5/10/25%, a high-variance 1% level, left-
  tail mass and robust skew) measured **off the critic** from realized returns, while the RL agent is
  held byte-identically fixed across arms. The instrument is **three-way decoupled**: the tail is
  *fed* on the training split, candidates are *selected* on a tail-blind validation Deflated Sharpe
  (λ=0), and the hypothesis is *tested* on empirical CVaR over a sealed test split — three different
  estimators on three different data partitions, so a tail effect is attributable to the feedback
  channel and cannot be a self-grading artefact. To our knowledge this three-way separation is novel
  in LLM-reward-design and in RL-for-finance, where prior work conflates at least two of the three.

- **C2 — A pre-registered comparative-inference protocol that yields a bankable result of either
  sign.** A cryptographically frozen design (hypotheses, arms, budget, seeds, splits, embargo,
  tail-diagnostic set, and analysis plan fixed before the sealed test leg) with intersection–union
  tests, a placebo and a structure-shuffled ("deranged-tail") control, deflated Sharpe ratios, and
  combinatorial probability-of-backtest-overfitting. A non-rejection is reported as a bounded,
  pre-registered equivalence, not an underpowered failure.

- **C3 — A decision-theoretic envelope delimiting when distributional feedback can help.** A short
  theory (Blackwell sufficiency / garbling; Kusuoka–Acerbi coherent-risk spanning; off-critic
  non-closedness) establishing that an *optimal* user of the lower-tail statistics weakly dominates an
  optimal user of a scalar risk summary, and the conditions (λ>0 selection, responsive designer) under
  which the bound is strict vs vacuous — turning the empirical question into a falsifiable prediction
  (the §1a prediction table), so a result of either sign is a *confirmed or refuted prediction* rather
  than a bare measurement.

---

## 3. Abstract (DRAFT, ~290 words; bankable-null variant)

Reward design is the central bottleneck in applying reinforcement learning to risk-sensitive
financial control: a reward that is well specified in the mean can yield a policy that is profitable
on average yet ruinous in the tail. Large language models can now author reward-function *code* and
refine it from feedback, but that feedback is typically a scalar score or a per-component point
statistic — it conveys little about the *shape* of the outcome distribution the reward implicitly
selects. We ask whether feeding the LLM reward-designer **multi-level tail-risk feedback** — the
realized-return lower tail (conditional value-at-risk at several levels, left-tail mass and skew),
measured *off the critic* from realized returns — leads it to write better risk-sensitive reward code
than a scalar risk-adjusted summary.

We isolate the feedback channel as the sole manipulated variable: five LLM arms share one fixed
soft actor–critic agent, one matched candidate budget, and identical prompts, differing *only* in the
feedback block; two non-LLM search baselines bound the search procedure. The design is **pre-registered
and cryptographically frozen** before a sealed 2018–2025 test leg. The feedback signal is *fed* on the
training split, candidates are *selected* on a tail-blind validation Deflated Sharpe, and the
hypothesis is *tested* on empirical conditional value-at-risk over the sealed split — so any tail
effect is attributable to the feedback channel rather than to a self-grading estimator. Inference uses
intersection–union tests with placebo and structure-shuffled controls, deflated Sharpe ratios, and
combinatorial backtest-overfitting probabilities.

**[RESULT — campaign slot.]** *Current honest fill:* in a directional single-seed prototype the
apparent tail advantage did not survive its own zero-information placebo control, consistent with the
pre-registered null; the confirmatory campaign tests whether this holds at full power. We therefore
report a bounded, pre-registered comparison rather than a performance claim, and contribute an
off-critic feedback instrument, a pre-registered inference protocol, and a decision-theoretic envelope
delimiting when distributional feedback can and cannot help an LLM reward-designer. The null is credited
on error-statistical severity (the frozen, deviation-free protocol; Mayo; Rubin 2025) and forking-paths
avoidance (Gelman & Loken 2014), and is reported as a TOST equivalence against the pre-registered SESOI
rather than as a bare *p* > 0.05.

> **Conditional-positive result sentence** (swap in iff the campaign IUT rejects on the tail leg and
> survives placebo + shuffled-placebo): "In the confirmatory campaign, multi-level tail-risk feedback
> improved the sealed-test left tail (CVaR-5%, intersection–union across three controls) at parity of
> risk-adjusted mean return (Sharpe leg non-significant) — the channel acted on the dimension it
> informs — while the structure-shuffled control ruled out a format artefact."

---

## 4. Novelty / positioning paragraph (DLM- and Eureka-distinguished — keep this exact altitude)

The contribution is *not* "an LLM can design reward code" (Eureka, Text2Reward, DrEureka) nor
"distribution beats scalar" stated loosely — Eureka already feeds per-component scalar *trajectories*,
and CARD (2026) reports beating a human reward oracle without any distribution. The empty cell this
work occupies is the *conjunction*: (i) the LLM authors reward **code**, (ii) the iteration signal is
the realized-return **lower-tail distribution of outcomes** (not point statistics of reward
components), (iii) in a **risk-sensitive financial, no-oracle** domain, (iv) under **pre-registered
comparative inference** with the off-critic three-way decoupling. The nearest neighbour is the
Decision-Language Model (Behari et al., NeurIPS 2024), which also proposes reward code and iterates on
a simulated *distribution* — but its distribution is a population-across-states spread in public-health
resource allocation, the agent is not held fixed off-critic, and there is no pre-registered tail
inference. State the delta in one sentence and cite-and-distinguish DLM, Eureka, and CARD explicitly;
never let the abstract elevate the (descriptive, comparator-snooped) "beat-the-human" H1 to the
novelty axis.

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
| Related work | 1,200 | **[NOW]** | refs.bib is clean + %VERIFY-disciplined; DLM in core bib |
| Theory (Blackwell/Kusuoka envelope + §1a prediction table) | 1,400 | **[NOW]** | C3; the rigour that is currently invisible — surface it |
| Data + EDA | 1,000 | **[NOW]*** | regenerate stylised facts from the frozen univ3 panel |
| Methods (instrument, arms, off-critic decoupling, freeze, inference) | 2,600 | **[NOW]** | add the system diagram + the rigour ledger as a table |
| Results | 1,500 | **[CAMPAIGN]** | structure now (tables/figs as placeholders); fill on the run |
| Discussion | 1,000 | **[NOW]** | lift from 700; lead with the bankable-null + mechanism |
| Conclusion | 250 | **[NOW]** | |
| Limitations appendix (word-excluded) | — | **[NOW]** | L1–L19 + endogeneity (V6), single-Claude (V10), softmax-cash (V14), undertraining |
| Rigour-ledger appendix (word-excluded) | — | **[NOW]** | docs/RIGOUR_LEDGER.md → examiner-facing table |

\* Data chapter: regenerate the kurtosis/Hill figures from the frozen univ3 panel (the old EDA numbers
are from a superseded IQN brief).

**Gated on you (cannot be done from here):** run `freeze.py` (1 command → makes the pre-registered-null
claim literally true; the freeze hash recorded by `scripts/freeze.py` at freeze time); run the confirmatory campaign on the GPU (with the 7 arms
incl. `placebo_shuffled`, σ_max logging, the learning-curve convergence ladder, and the delisting band
reported); obtain the supervisor's written sign-off on the proposal-pivot disclosure before the
"with my supervisor's agreement" sentence enters the PDF.

**Highest-leverage next writing targets (I can draft each now):** (a) the Theory chapter + §1a
prediction table prose [C3 — the invisible rigour]; (b) the Methods chapter with the system diagram +
rigour-ledger table; (c) the Limitations appendix [the dominant no-viva grade lever]; (d) the
Introduction + positioning. Any of these is bankable today.
