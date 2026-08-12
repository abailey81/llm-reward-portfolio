# CH1 (Introduction) — the numbered contributions, each with its evidence attached

**Why numbered claims and not a paragraph.** Criterion 3 marks significance, and *"markers assessing
significance are looking for something to point at."*A paragraph saying the work "contributes to
understanding" gives them nothing. Each claim below is followed by **the specific result that supports
it**and **the section where that result lives**, so the claim can be checked rather than believed.

**Status discipline.** Contributions 1–4 are **evidenced now**. Contribution 5 is the confirmatory
hypothesis and is **marked pending until the sealed test is scored** — it is listed so the structure is
visible, not to bank a result in advance. Nothing here is asserted from an inference.

---

## C1 — An instrument: multi-level tail feedback as a manipulable variable

**The claim.** A reward-designing loop can be fed a *coherent-risk profile of the realized-return lower
tail*— CVaR at 5/10/25/1 %, left-tail mass, robust skew — rather than a scalar, and that channel can be
manipulated while everything else is held fixed. The estimator is **critic-agnostic and off-critic**: it
reads no Q-network and fits only on realized returns.

**Evidence.** The manipulation is verified *in the executed archive*, not merely in the code: across 273
archived reflection prompts spanning all twelve execution lines, the fed block carries exactly the
registered content per arm — 0 tail labels for `scalar`, 1 for `scalar_cvar5`, 6 for `distributional` —
with **zero violations** and **zero tail leakage into `scalar`**. Block lengths are byte-exact at
67/86/275/293/275 characters, so token count cannot confound the contrast. → **CH4 Methods; the arm
specification and construct-validity tables.**

**Honesty clause.** The fed tail is **endogenous**: it is measured on the trained policy's *own* realized
returns under the candidate reward, so this compares two coupled reward → policy → measurement loops.
It is not an exogenous risk measurement, and the document never claims agent-independence.

## C2 — A protocol: a pre-registered, deviation-free controlled comparison in this literature

**The claim.** To our knowledge this is the first **pre-registered** study in the automated
reward-design literature. This is deliberately stated as a claim about a *practice*, not about an empty
cell: it is verifiable in an afternoon and cannot be defeated by naming an adjacent paper.

**Evidence.** A frozen design hash (`3ca6f01ab7724d47…`, tag `prereg-v2.1`) binding nine files including
the prompts and the arm specification, so the manipulated variable cannot change post-freeze; 105 dated
amendments, every one pre-data; and the epistemic basis correctly named — Mayoian error-statistical
severity rather than Popperian corroboration, re-based *pre-data* by amendment R61. → **CH2 positioning
matrix (pre-registration column); CH3 severity paragraph; Quality-control appendix.**

## C3 — A negative result with a mechanism: expert risk-aware objectives lose to an unpriced friction

**The claim.** Over the sealed 2020-03-30 → 2026-06-30 window, ten of eleven expert-designed reward
functions are **net-negative** risk-adjusted, **eight of the ten losers penalising risk explicitly**; the
eleventh — the one that charges for trading — is the only positive. **Gross** of transaction costs every
design earns +0.82 … +1.18 Sharpe, so all carry real signal; **none beats a costless, daily-rebalanced
equal-weighted portfolio of the same thirty assets (+1.283) even before costs** — the drifting
buy-and-hold variant (+1.258) also dominates, so the comparison does not turn on the rebalancing
convention — and all but one surrender that signal entirely to a
20 %/year turnover drag.

**Evidence.** Mean net Sharpe **−0.1071** against mean gross **+0.9628** — a **1.07 Sharpe** cost wedge —
computed by the *registered* analytic repricing identity and cross-validated against the environment's own
archived gross series to **1.4 × 10⁻¹⁷**. `return_minus_turnover` runs at 0.0077 turnover against ~0.89
and retains 98.8 % of its gross Sharpe. → **CH6 Results, its own section.**

**Why it is a contribution and not comparator housekeeping.** It independently demonstrates this
dissertation's premise on the *hand-written* canon: same agent, data, 400,000-step budget, seeds and
sealed window; changing only the reward's content moves the outcome from −0.31 to +1.16. And it is
practitioner-usable: *pricing risk is not pricing trading.*

## C4 — An evaluation lesson: outcome scoring cannot audit generated code

**The claim.** When a machine-authored artefact is scored on results, a *partially* broken artefact is
more dangerous than a fully broken one. Full failure is self-limiting; partial failure lets a fallback
path silently supply the missing behaviour, and the blend can outscore every honestly-authored
candidate — because the blend optimises precisely the quantity being scored.

**Evidence.** Observed in the executed run: a candidate whose authored reward fell back to the harness
default on **49.98 %** of 400,000 calls held the **highest** fitness in its arm (+0.2336 against a best
eligible +0.000124) and was excluded only by the pre-registered execution floor (R115). By contrast a
candidate at **99.98 %** fallback scored 7.8 × 10⁻⁶ and eliminated itself. → **CH4 (R115 rationale);
CH6 (the binding case); Quality-control appendix §A.3 Class 4.**

## C5 — *(PENDING — do not state as a result until the sealed test is scored)* the confirmatory answer

**The claim, when available.** Whether multi-level tail feedback changes the reward code an LLM writes,
and whether any change survives to realized tail outcomes — a three-link chain (fed signal → authored
code → policy → realized tail) in which a null *locates* where transmission breaks rather than merely
failing to reject.

**Status.** The sealed test is looked at **once**, at the pre-declared date. Decision rules for all six
confirmatory nodes are fixed in advance and tabulated in CH4. **This slot is intentionally empty.**

---

## Placement and cross-references

*All five appear in the Introduction as a numbered list (~180 words), each with a forward reference.
*C5's pending status is stated in the Introduction too — a reader must not infer that the confirmatory
  result is being withheld or hedged.
*The Conclusion answers the research question in its **original words** and then re-states C1–C4 with
  their final numbers.
