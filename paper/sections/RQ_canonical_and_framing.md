# The canonical research question (stated three times, identically) + the page-one framing

**Why identical wording matters.** Criterion 2's title puts *"clear statement of objectives or research
questions"* **before** methods, so this criterion is partly marked on legibility of purpose. Stating the
question in three places in three different phrasings reads as three different questions. Stating it
identically makes a marker recognise it and tick the box. This is not repetition; it is the criterion
being satisfied.

**⚠ Sourcing.** The canonical form below is taken **verbatim** from the existing `paper/CH1_introduction.md`
§1.2 (the "mechanistic question at the centre of this dissertation"). It is **not** a new formulation —
re-wording it now would create exactly the inconsistency this action exists to remove.

---

## THE CANONICAL FORM — copy this text, character for character, into all three places

> **Research question.** Does showing the reward-designer the *downside* — the lower-tail distribution of
> realised outcomes, rather than a scalar — change the reward *code* it writes, and does that change
> propagate to the trained agent's realised tail behaviour?

With its decomposition, which may accompany the question but must not replace it:

> We cast this as a **three-link causal chain** — fed tail signal → authored reward code → trained policy
> → realised tail — and ask, through three sub-questions: **(SQ1)** does the signal move the code?
> **(SQ2)** does the code move the outcome? **(SQ3)** is any effect genuine *use* of the tail content, or a
> surface echo? The object is not merely *whether* richer feedback helps, but **where the channel acts or
> breaks**.

### Placement 1 — boxed, first page of the Introduction
Immediately after the opening context paragraph, before §1.2's literature framing. Boxed or block-quoted
so the eye lands on it. Followed by the numbered contributions C1–C5.

### Placement 2 — at the head of the Methodology chapter
The first thing in CH4, before the design description, in the **same words**. One sentence may precede
it: *"The design below exists to answer one question, restated here so it can be checked against the
method that follows."*

### Placement 3 — answered in the Conclusion, in its original words
The Conclusion opens by restating the question verbatim and then answering it in the same vocabulary —
`code`, `propagate`, `realised tail behaviour` — so the answer is visibly an answer to *that* question.
Template, to be completed with the sealed result:

> Does showing the reward-designer the downside change the reward code it writes, and does that change
> propagate to the trained agent's realised tail behaviour? **[Link 1: it does / does not move the code,
> by …]** **[Link 2: the change does / does not propagate, by …]** **[Link 3: the effect is genuine use /
> a surface echo, because …]** The chain therefore **[holds / breaks at link N]**, and the study's
> contribution is to have **located** that, rather than to have observed only that richer feedback did or
> did not help.

---

## The page-one null framing (A8)

**Why it must be on page one and not in the discussion.** A marker who reaches the discussion still
believing the project failed has already formed a view and will not revise it. The frame has to arrive
**before** the result does.

**Insert in the Introduction, immediately after the boxed question:**

> **A note on what counts as a result here.** This study pre-registered its predictions, including the
> prediction that the two feedback conditions would perform **equivalently** on risk-adjusted return. A
> confirmed equivalence is therefore a *result*, not an absence of one: the analysis is built to
> **reject** the presence of an effect larger than a pre-specified bound, rather than merely to fail to
> reject zero. Where the chain does break, the design is built to say **which link** broke. A reader
> looking for "the treatment won" will not find it framed that way, and should not: the finding is the
> *location* of the mechanism's boundary, not a victory for one arm.

**Teach the three unfamiliar ideas in one sentence each, here, because the second marker may be a
structural engineer** — briefly, without condescension:

* **Pre-registration** — the design, hypotheses, and analysis were fixed and hash-frozen before the test
  data was examined, so no analytic choice could be made after seeing the outcome.
* **Equivalence testing** — a test that can conclude "no effect larger than *x*", which ordinary
  significance testing cannot; it is what turns a predicted null into evidence.
* **Intersection–union test** — a claim required to hold against *every* comparator at once; because the
  composite null is only rejected when each component is, it needs no multiplicity correction.

---

## The Results-chapter orientation paragraph (A8, continued)

**Why this is free.** The registered analysis order puts the mechanism decomposition late, which is
correct and must not change. But an orientation paragraph is *presentation*, not analysis, so it costs
nothing in registered terms.

**Insert as the first paragraph of CH6, before the first table:**

> **How to read this chapter.** The order below is the pre-registered analysis order and is deliberately
> not the order of interest. It opens with **execution integrity** — evidence that the run is fit to be
> interpreted at all — because every later number depends on it. It then reports the **co-primary
> confirmatory tests** with their equivalence bounds, then the **controls** that separate content from
> format, and only then the **mechanism decomposition** that explains *why* the confirmatory result came
> out as it did. Reading the mechanism section first would be reading an explanation before the thing it
> explains. Each section states its decision rule before its numbers, and every rule was fixed before the
> sealed data was examined.

---

## Verification before submission

- [ ] `grep` the three placements and confirm the question is **byte-identical** in all three.
- [ ] Confirm the Conclusion's answer uses the question's own vocabulary (`code`, `propagate`, `realised
      tail behaviour`) rather than paraphrase.
- [ ] Confirm the null framing appears on page one, *before* any result is stated.
- [ ] Confirm the three taught concepts appear once each, in the Introduction, and are not re-explained
      later (repetition reads as padding to a marker who has already understood).
