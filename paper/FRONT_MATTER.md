# Front Matter

> **Status: structural scaffold (2026-06-28).** Assembles the submission-required front-matter blocks for the
> UCL MSc dissertation PDF. Voice is the author's to adapt at compile. No campaign numbers appear here.
> The Abstract is assembled from `paper/00_FRAMING_title_abstract_contribution.md` §3 at compile (see the
> placeholder below); the title is the recommended option (1) from `00_FRAMING` §1.

---

## Title Page

<div style="text-align:center">

**UNIVERSITY COLLEGE LONDON**

**UCL Institute of Finance and Technology**

&nbsp;

**Risk-Sensitive Reward Design for Portfolio Reinforcement Learning:**
**A Controlled Test of Multi-Level Tail-Risk Feedback to an LLM Reward Designer**

*(Submitted title — Multi-Level Tail-Risk Feedback for LLM Reward Design: A Pre-Registered Study in*
*Risk-Sensitive Portfolio Reinforcement Learning; reconcile the two title strings to a single string at compile.)*

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
- **AI assistance disclosure.** [State here, per UCL's generative-AI-use policy at the time of submission, the
  nature and extent of any generative-AI assistance used in drafting or coding, consistent with the programme's
  declared permitted-use category. Reconcile against the current UCL Academic Manual wording at compile.]

I confirm that all reported results, where present, are produced by the frozen, pre-registered pipeline and that
any quantity that depends on the (yet-to-be-run) confirmatory campaign is, in the present version, a clearly
marked placeholder rather than a reported finding.

Signed: ______________________  Date: ______________________

---

## Acknowledgements

[Acknowledgements stub — to be completed at compile.] I thank my supervisor, Dr Ramin Okhrati, for his guidance
throughout this project. [Acknowledge any further academic, technical, data-access, computational, and personal
support here. Note any institutional compute used and the data-licence holder, consistent with the Declaration
above.]

---

## Abstract

[abstract assembled from paper/00_FRAMING §3 at compile]

*(Compile note: use the ~290-word bankable-null variant in `00_FRAMING_title_abstract_contribution.md` §3;
swap to the conditional-positive sentence only if the confirmatory campaign rejects on the tail leg and survives
both placebo controls, per the rule in §3 and §6 of that file. The `[RESULT — campaign slot]` sentence in the
abstract must remain a marked placeholder until the campaign is run.)*

---

## Word-Count Statement

The main text of this dissertation is within the **10,000-word limit** set by the programme. In accordance with
UCL / Institute of Finance and Technology guidelines, the following are **excluded** from the word count:

- mathematics, equations and displayed code;
- figures, tables and their captions;
- footnotes;
- the reference list / bibliography; and
- appendices (including the Limitations appendix and the Rigour-Ledger appendix).

Main-text word count (excluding the above): **[WORD COUNT: fill at compile]** words.

*(Compile note: reconcile the precise inclusion/exclusion rules and the limit against the current UCL Academic
Manual / programme handbook wording at submission; the figures above reflect the standard guidance as understood
at the time of writing.)*
