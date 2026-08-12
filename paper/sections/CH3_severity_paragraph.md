# CH3 (Theory) — insert: what pre-registration does and does not buy

**Placement.** Immediately before the hypothesis statements, where the epistemic status of a predicted
null is first asserted. **Why it belongs in the theory chapter and not only in the protocol:** it is a
claim about *what kind of evidence a null is*, and Criterion 1 marks original interpretation from the
literature review, the reference list and the discussion — not from a pre-registration appendix.

**Provenance.** Registered as amendment **R61** (2026-06-28), which re-based the epistemic claim
*before* any confirmatory data existed. This section is the prose form of that amendment.

---

## The paragraph

> It is tempting to argue that because this study was pre-registered, its predicted null is a *severe*
> test in Popper's sense. That argument is wrong, and the reason it is wrong shapes how the result below
> should be read. Severity, in the sense that licenses inference from a passed test, is a property of the
> test's **capacity to have detected the error had it been present** — it is an error-statistical notion
> (Mayo, 1996; Mayo & Spanos, 2006), not a corollary of having written the prediction down first.
> Pre-registration does not raise the probability that a false hypothesis would have been caught; a
> pre-registered study can be underpowered, and an underpowered pre-registered null is exactly as
> uninformative as an underpowered exploratory one (Rubin, 2025). What pre-registration *does* buy is
> different and narrower: with a frozen, deviation-free protocol there are no sample-dependent analytic
> choices, so there is no unknown Type-I inflation to discount (Rubin, 2025), and the garden of forking
> paths is closed by construction rather than by assertion (Gelman & Loken, 2014). Those are real goods,
> but they are goods about the *absence of an inflation*, not about the *presence of severity*.
>
> The distinction has a direct methodological consequence, and it is why this study does not report its
> null as `p > 0.05`. A non-significant result is compatible with both "the effect is absent" and "the
> test could not have seen it", and only the first is a finding. Severity therefore has to be
> **supplied**, not inherited: by a smallest effect size of interest fixed in advance, by an equivalence
> test that can *reject* the presence of an effect larger than that bound (Lakens, Scheel & Isager, 2018;
> Campbell & Gustafson, 2018), and by a severity assessment evaluated at that bound for each co-primary
> leg. Read that way, the pre-registration is not the source of the epistemic credit; it is the reason
> the severity calculation is *interpretable*, because nothing in the analysis path was chosen after
> seeing the data. The claim this study is entitled to make about a null is consequently precise and
> bounded: not "the mechanism does not exist", but "an effect larger than the pre-specified bound is
> rejected at the stated assurance, on a protocol whose analytic path could not have been tuned to
> produce that answer."

---

## Why this is the strongest available evidence of original interpretation

Stated plainly, because Criterion 1 rewards it and a marker will not infer it:

*The **standard** move in an applied pre-registered study is to treat registration as conferring
  severity. It is extremely common and it is incorrect.
*Noticing the error requires holding two literatures at once — the philosophy of statistics (Popper vs
  Mayo on what makes a test severe) and the applied replication literature (what registration actually
  controls) — and the correction was made **against our own interest**, since the weaker, correct claim
  is harder to defend than the stronger, wrong one.
*It was corrected **pre-data** and recorded as a dated amendment, so it is verifiable rather than
  asserted: `R61`, 2026-06-28, superseding the earlier "corroborated Popperian prediction" label.

## Citations required in `refs.bib`

| Claim | Source |
|---|---|
| severity as error-statistical capacity to detect | Mayo (1996); Mayo & Spanos (2006) |
| pre-registration does not improve Popperian severity; it removes unknown Type-I inflation | Rubin (2025), *Synthese* (arXiv:2408.12347) |
| garden of forking paths | Gelman & Loken (2014) |
| equivalence testing / TOST against a SESOI | Lakens, Scheel & Isager (2018); Campbell & Gustafson (2018) |

**⚠ Pre-compile check.** Run `/verifying-citations` — Mayo (1996) and Mayo & Spanos (2006) must be
present and not marked `% VERIFY`; the examiner is a measure-theoretic probabilist and this is exactly
the citation chain he would check first.
