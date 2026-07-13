# Front Matter

> **Status: structural scaffold (2026-06-28).** Assembles the submission-required front-matter blocks for the
> UCL MSc dissertation PDF. Voice is the author's to adapt at compile. No campaign numbers appear here.
> The Abstract below IS the ratified v2 (2026-07-01, mechanism-led) text from
> `paper/00_FRAMING_title_abstract_contribution.md` §3 (embedded 2026-07-06; the RESULT slot fills at
> campaign). TITLE: the rendered title is an adapted method-forward variant; `00_FRAMING` v2 recommends
> option (2) ("Does Showing the Model the Downside Change the Reward Code It Writes?").
> PILLAR-ANCHORED ANALYSIS (2026-07-06, per the author's directive): the study's strict inspiration is
> Eureka (Ma et al., 2024 — reward DESIGN via coding LLMs), and its pillars are (i) LLM-authored reward
> CODE, (ii) the FEEDBACK CHANNEL as the sole manipulated variable (multi-level tail vector vs scalar),
> (iii) a pre-registered controlled comparison, (iv) a fixed risk-sensitive portfolio agent. Option (3)
> ("Can Tail-Risk Feedback Improve LLM-Designed Reward Functions? An Off-Critic, Pre-Registered Study in
> Portfolio Reinforcement Learning") carries ALL four pillar terms and the Eureka lineage most explicitly;
> option (2) is the mechanism-catchy alternative that leads with the headline question but drops the
> reward-design lineage keywords. RECOMMENDED = option (3), or the fusion "Tail-Risk Feedback in LLM
> Reward Design: A Pre-Registered, Controlled Study in Risk-Sensitive Portfolio Reinforcement Learning".
> The FINAL title is the author's compile-time decision [TAMER: pick at compile].

---

## Cover Page

> **[INSERT AT SUBMISSION: the official Moodle cover page template — UCL section 1 of 16. Tracked in
> the P8 submission checklist.]**

---

## Title Page

<div style="text-align:center">

**UNIVERSITY COLLEGE LONDON**

**UCL Institute of Finance and Technology**

&nbsp;

**Risk-Sensitive Reward Design for Portfolio Reinforcement Learning:**
**A Controlled, Pre-Registered Test of Multi-Level Tail-Risk Feedback to a Language-Model Reward Designer**

&nbsp;

**Tamer Atesyakar**

&nbsp;

A dissertation submitted in partial fulfilment of the requirements for the degree of

**MSc Banking & Digital Finance**

&nbsp;

UCL Institute of Finance and Technology
University College London

&nbsp;

Supervisor: Dr Ramin Okhrati

&nbsp;

September 2026

</div>

---

## Declaration of Originality

I, Tamer Atesyakar, confirm that the work presented in this dissertation is my own. Where information has been
derived from other sources, I confirm that this has been indicated in the work. Where I have consulted the
published work of others, this is always clearly attributed. Where I have quoted from the work of others, the
source is always given. With the exception of such quotations, this dissertation is entirely my own work. I have
acknowledged all main sources of help. This work has not been submitted, in whole or in part, for any other
degree or qualification at this or any other institution.

**Third-party tools and resources.** I disclose the following third-party tools, services and data used in the
production of this work, all employed under my own direction and with the outputs verified by me:

- **Market data.** A licensed Refinitiv/LSEG point-in-time, survivorship-free US equity panel (the gold panel),
  used under the terms of the applicable institutional licence.
- **Reference data.** FRED (risk-free rate, DGS3MO), an equal-weighted market benchmark, and Fama–French factor
  series, used for evaluation and factor attribution.
- **Large language models in the experimental loop.** The reward-designer under study is a frontier large
  language model (Claude Opus 4.8 in the confirmatory campaign; Claude Sonnet 4.6 in the prototype). These models
  are the *object of study*, not authorship aids; all of their outputs are archived, screened and replayed under
  the pre-registered protocol described in Chapter 4.
- **Software.** Open-source scientific Python (including Stable-Baselines3, NumPy, SciPy, pandas and the `rliable`
  evaluation library), used under their respective open-source licences.
- **AI assistance disclosure.** Generative-AI assistance (Anthropic Claude) was used as a coding and drafting
  aid — code scaffolding and refactoring, literature triage, and prose editing — under my own direction. All
  AI-assisted code was read, tested and verified by me; all AI-assisted prose was checked, rewritten in my own
  words, and fact-checked; and every citation was verified against its primary source. This authorship/coding
  assistance is distinct from the language models studied as the experimental *object* of this dissertation
  (above). Under UCL's three-category framework for generative AI in assessment (Academic Manual §9.2.6a and
  the UCL Generative AI Hub's assessment categorisation), the use disclosed here is of the *assistive* kind
  (Category 2: drafting, coding and proofreading support under the author's direction and verification), while
  the language models analysed in Chapters 4–6 are the *object of study*, archived and reproducible under the
  pre-registered protocol; no generative system authored this dissertation's claims, analyses or conclusions
  on the author's behalf.

I confirm that all reported results, where present, are produced by the frozen, pre-registered pipeline and that
any quantity that depends on the (yet-to-be-run) confirmatory campaign is, in the present version, a clearly
marked placeholder rather than a reported finding.

Signed: ______________________  Date: ______________________

---

## Ethics and Data Protection

This project involved **no human participants, no personal data, and no animal subjects**; it is a low-risk
computational study and did not require UCL research-ethics committee review. The data are **firm-level financial
securities prices** (a licensed Refinitiv/LSEG point-in-time, survivorship-free equity panel), which are **not
personal data** under UK GDPR. They are used under the applicable institutional licence, are **not redistributed**,
and reach the experimental code only as **anonymised, integer-indexed return arrays** — carrying no security
identifiers, issuer names, or calendar dates — which serves simultaneously as a data-licensing safeguard and as a
sandbox-security control on the untrusted LLM-authored reward code (Chapter 4). *(Confirm the IFTE0008 ethics
self-certification and data-protection-form requirements on Moodle, and attach the completed form(s) if required.)*

---

## Abstract

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
block; two non-LLM search baselines bound the procedure. The design is **pre-registered and
cryptographically frozen** before a sealed 2020–2026 test leg, with the signal *fed* on the training split,
candidates *selected* on a tail-blind validation Deflated Sharpe, and the hypothesis *tested* on empirical
conditional value-at-risk over the sealed split — a three-way decoupling so any effect is attributable to
the channel rather than to a self-grading estimator. The performance contrast is decided by co-primary
intersection–union tests against placebo and structure-shuffled controls; the mechanism is read off a
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

*(Compile note: the v2 mechanism-led text is EMBEDDED above (2026-07-06); fill the RESULT slot from the campaign;
swap to the conditional-positive sentence only if the confirmatory campaign rejects on the tail leg and survives
both placebo controls, per the rule in §3 and §6 of that file. The `[RESULT — campaign slot]` sentence in the
abstract must remain a marked placeholder until the campaign is run.)*

---

## Acknowledgements

[Acknowledgements stub — to be completed at compile.] I thank my supervisor, Dr Ramin Okhrati, for his guidance
throughout this project. [Acknowledge any further academic, technical, data-access, computational, and personal
support here. Note any institutional compute used and the data-licence holder, consistent with the Declaration
above.]

---

## Table of Contents

*(Compile note: page numbers and final section numbering are generated at LaTeX compile; the structure below is authoritative.)*

1. **Introduction**
2. **Literature Review**
3. **The Information Value of Tail-Risk Feedback** (Theory)
4. **Methods** — data & stylised facts · the off-critic instrument · the seven arms · pre-registration & freeze · inference plan
5. **Directional Prototype** (pre-registration-time, non-confirmatory)
6. **Results** (confirmatory campaign)
7. **Discussion, Limitations and Conclusion**
- **References**
- **Appendix B — Limitations Register** (§B.1–B.7)

## List of Figures

| # | Title |
|---|---|
| F1 | System / off-critic decoupling diagram |
| F2 | Prediction-branch diagram (Strict / Weak / Null) |
| F3 | Panel stylised facts (heavy tails / CVaR curve / volatility clustering / co-crash) |
| F4 | Data-splits timeline with purge bands and regime markers |
| F5 | rliable headline intervals (per-seed IQM) |
| F6 | TOST equivalence forest vs the ±0.05-DSR SESOI band |
| F7 | Placebo / structure-shuffled controls overlay |
| F8 | Mechanism: fed-tail change vs authored-reward change (responsiveness; reward-code AST distance) |
| F9 | Learning curves / convergence diagnostic |

## List of Tables

| # | Title |
|---|---|
| Table 4.1 | Rigour ledger — threats to H2 validity and the design element guarding each (in-body, CH4 §4.7) |
| T1 | Run ledger (arms × seeds × budget, freeze hash, deviations, compute) |
| T2 | Intersection–union test results (H2-RA, H2-Tail) + ES backtest |
| T3 | Robustness (delisting band, cost sweep, PBO, DSR, factor attribution) |
| T4 | Secondary hypotheses (H1, H3, H4) |
| T5 | Arms specification (the seven arms; single manipulated variable) |

*(Figures F5–F9 and Tables T1–T4 are confirmatory-campaign outputs and remain placeholders until the frozen run completes; F1–F4 and T5 are buildable now from the frozen panel and design files.)*

---

## Glossary of Terms

*For the reader from another discipline; each term is defined the way it is used in this dissertation.*

| Term | Meaning here |
|------|--------------|
| Reinforcement learning (RL) | Training a decision-making program (the *agent*) by trial and error against a numerical reward signal. |
| Reward function | The formula that scores each of the agent's actions during training; here it is *written as Python code by a language model*. |
| Agent / policy | The trained decision-maker; the policy is its rule mapping observations to portfolio weights. |
| SAC (Soft Actor–Critic) | The specific, fixed RL training algorithm used for every arm; only the reward it is trained on varies. |
| Replay buffer | The agent's rolling memory of past experience that training samples from. |
| Large language model (LLM) | The AI text model (here Claude) that authors the reward code and revises it from feedback. |
| Reflection loop | The generate → train → measure → feed-back → revise cycle in which the LLM improves its reward code. |
| Feedback block | The short text of performance numbers shown to the LLM after each attempt; *the only thing that differs between arms*. |
| Arm | One experimental condition (e.g. tail-fed vs scalar-fed); seven arms in the confirmatory study. |
| Placebo / structure-shuffled placebo | Control arms whose feedback carries no genuine information (constants, or real numbers scrambled across labels), isolating information content from format. |
| VaR (Value-at-Risk) | The loss threshold that is exceeded only α% of the time (e.g. the worst-5% cutoff). |
| CVaR / Expected Shortfall | The *average* loss in that worst-α% tail — the study's central risk measure. |
| Coherent risk measure | A risk measure satisfying four standard axioms (incl. rewarding diversification); CVaR is coherent, VaR is not. |
| Elicitability | Whether a risk measure can be validated by scoring point forecasts; ES alone cannot, but (VaR, ES) jointly can — the basis of the tail backtests. |
| Sharpe ratio | Average return divided by its volatility — the standard risk-adjusted performance number. |
| Deflated Sharpe Ratio (DSR) | A Sharpe ratio corrected for how many strategies were tried and for fat tails, so lucky search winners are not mistaken for skill. |
| Pre-registration | The full analysis plan, frozen and hash-stamped *before* the decisive experiment, so results cannot quietly reshape the questions. |
| Sealed test set | The final years of data, untouched during all development and selection, used exactly once for the headline evaluation. |
| Equivalence test (TOST) | A statistical test of "the difference is smaller than a practically relevant margin" — evidence *for* a null, not mere failure to reject. |
| Bootstrap | Estimating uncertainty by resampling the observed data many times. |
| Survivorship bias / point-in-time data | The error of studying only companies that survived; avoided here by using the index membership as it was known on each historical day. |
| Walk-forward backtest | Evaluating a strategy strictly forward in time, so no future information leaks into past decisions. |
| Responsiveness / transmission / specificity | The three mechanism sub-questions: does feedback change the code; do code changes reach realised risk; is the change driven by genuine tail information rather than format. |

---

## Word-Count Statement

**[CONFIRM AT COMPILE — word_budget.py must PASS]:** the main text of this dissertation is within the **10,000-word limit** set by the programme. In accordance with
UCL / Institute of Finance and Technology guidelines, the following are **excluded** from the word count:

- mathematics, equations and displayed code;
- figures, tables and their captions;
- footnotes;
- the reference list / bibliography; and
- appendices (the Limitations appendix). *(The rigour ledger is an in-body table — Table 4.1 — excluded via the figures/tables item above, not an appendix.)*

Main-text word count (excluding the above): **[WORD COUNT: fill at compile]** words.

*(Compile note: reconcile the precise inclusion/exclusion rules and the limit against the current UCL Academic
Manual / programme handbook wording at submission; the figures above reflect the standard guidance as understood
at the time of writing.)*
