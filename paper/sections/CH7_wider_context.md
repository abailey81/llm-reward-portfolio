# CH7 (Discussion) — insert: the wider context beyond portfolios

**Why this exists.** Criterion 1's top band reads *"exceptional insight into the problem **and its wider
context**"*, and that second clause is otherwise unclaimed: everything else in the document is about
portfolios. This subsection leaves finance entirely.

**⚠ A DELIBERATE DEPARTURE FROM THE EXTERNAL RECOMMENDATION.** The feedback proposed writing this
subsection around the claim that *"language models cannot reliably use small numerical differences."*
**That claim is not yet measured and must not be asserted.** The numeracy bottleneck is this study's
registered *hypothesis* about the shape of the capability gradient; the psychometric module that would
supply a measured per-model detection threshold is **specified (R96) but not built**, and H2's
confirmatory contrast is not yet scored. Writing the subsection around it would be asserting a
conclusion from an inference — precisely the move this project's standards forbid, and precisely what a
referee would attack.

So the subsection below is built on three findings that **are** measured, each of which generalises past
finance on its own. The numeracy sentence is pre-written in §2 below and inserted **only if** the
psychometric measurement lands.

---

## The subsection (≈300 words of counted prose)

> **Beyond portfolios.** Three of this study's findings are not really about asset allocation, and each
> constrains automated design loops generally.
>
> The first concerns how generated artefacts should be scored. A reward that failed on essentially every
> call produced a worthless policy and eliminated itself; a reward that failed on *half* its calls
> produced the **best** fitness in its arm, because the harness's fallback silently supplied the
> behaviour the authored code did not. Outcome quality cannot separate those two cases, since the blend
> is optimising exactly the quantity being scored. Any pipeline that accepts machine-generated code on
> the strength of its results — and that has any fallback, default, or exception path — is therefore
> blind in the region where contamination is most attractive, and needs an execution audit rather than a
> better metric.
>
> The second concerns iterative self-improvement. A reflection loop requires a prior success to reflect
> on. Below some authoring reliability the loop does not degrade gracefully; it never starts, because no
> accepted artefact exists to critique. The capability threshold for self-improvement is thus not "good
> enough to improve" but "good enough to succeed once", which is a different and higher bar than a
> smooth performance curve would suggest.
>
> The third concerns objective specification. Ten expert-designed objectives, several explicitly
> risk-aware, all carried genuine signal and all surrendered it to a single unpriced friction; only the
> objective that charged for that friction retained it. Sophistication in the modelled quantity did not
> substitute for pricing the dominant real cost — a failure mode available to any deployed optimisation
> whose objective omits a constraint the environment enforces anyway.

---

## Notes (not counted — appendix/marginal material)

**1. Why these three and not others.** Each is (a) measured in this study rather than inferred, (b)
mechanistically explained rather than merely observed, and (c) statable without any finance vocabulary —
the test for whether a lesson has genuinely left the domain. A second marker from another discipline can
evaluate all three.

**2. The numeracy paragraph, pre-written, to insert ONLY on a measured threshold.** If the psychometric
module (R96 axis A) is activated and yields per-model δ-75 detection thresholds with the share of
realised fed deltas falling below them:

> A fourth finding would then concern the channel itself: if the differences a loop feeds back sit below
> the reader's measured discrimination threshold, the loop is not learning slowly — it is not receiving
> the signal at all. Where that holds, the remedy is representational (re-render the quantity so the
> difference is legible) rather than algorithmic, and no amount of additional iteration recovers it.

**Do not insert this without the measurement.** Without it the honest statement is the *registered
hypothesis*, which belongs in the Limitations register as an open question, not in the Discussion as a
result.

**3. Cross-references.** Finding 1 → the R115 methods row and the results section reporting the binding
case. Finding 2 → the capability-gradient figure across eleven models. Finding 3 → the turnover
contribution and its net/gross table.

**4. Word budget.** The Discussion is allotted 1,400 words; this subsection is ~300 of them, leaving
~1,100 for the located-null interpretation and the limitations register. The notes above are marginal
material and are excluded.
