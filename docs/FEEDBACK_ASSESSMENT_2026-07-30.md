# Assessment of the "Getting every criterion into the top band" feedback (2026-07-30)

**Verdict: high quality, and it should be adopted almost in full.** It reads the IFTE0008 rubric
correctly, identifies communication as the binding axis, and its highest-value recommendations are
free of the word count. Four of its factual claims are wrong or stale and are corrected below; one of
its central premises has been overtaken by events in our favour. Nothing in it conflicts with the
frozen design.

This document is the assessment and the implementation plan. It does not replace
`docs/WRITEUP_95PLUS_PLAYBOOK.md` — it sharpens and extends it.

---

## 1. FOUR MATERIAL CORRECTIONS (verified first-hand, not inferred)

### 1.1 ⚠ "Switch on the psychometric module. Ten dollars, no compute, already specified and built."

**Specified: yes, in full. BUILT: NO.** Verified by search — no source in `src/`, `scripts/` or
`tests/` matches `2afc`, `graded.delta`, `jnd`, `delta_75` or `psychometric`. The only related file is
`scripts/m2_survey.py`, which is the separate ~25-model reading-link survey, not the threshold ladder.

The specification itself says so: *"The stimulus builder rides the existing `scripts/m2_survey.py`
harness (**a gate-week build task if activated**…)"*. So the action is **build the 2AFC ladder harness,
test it, then spend the money** — engineering time plus API cost, not a switch.

**And the cost is probably not \$10.** R96 registers TWO axes — `axis_a` (per-model δ-75 thresholds,
~\$8-12) and `axis_b` (the ecosystem census, ~\$15-25) — under a single `activation` key whose
integrity clause reads *"**If activated, every estimand above reports in full**"*. On the conservative
reading, activation commits us to **both axes, ≈\$23-37**, not \$10. **This must be resolved in
writing before any spend**, because it changes the cost threefold. Options: (a) activate both and
budget for it; (b) amend R96 to make the axes independently activatable, dated and recorded *before*
seeing any result, which preserves the anti-forking guarantee.

**Assessment of the underlying advice: correct and important.** It is the single largest available
move on Criterion 3, for exactly the reason given — it converts the mechanism claim from an inference
("we think the model could not read the numbers") into a measured threshold with the campaign's own
fed deltas overlaid. The spec's own overlay estimand is precisely that. And it is **safely
deferrable**: the spec confirms it is *"equally runnable post-campaign since the module needs no GPU
and no frozen quantity."*

### 1.2 ⚠ "The configuration comment says the universe rotates per date and the code selects once."

**Not reproduced as stated; the code is PIT-clean.** `config/prototype.yaml` reads
`phase: development  # dev top-30 (2005 selection)` — consistent with select-once, not a claim of
rotation. `top30_selection_univ5.parquet` holds *"the point-in-time top-30 RICs"* keyed by window, and
`load_gold_panel` loads *"one window's point-in-time top-30"*. **There is no look-ahead.**

But the instinct is right and there are two real items:
* **A dangling cross-reference** — the comment points at *"the PIT-simplification caveat above"* and no
  such caveat exists in the file. `config/` is inside the live-run drift pathspec, so this is
  registered for the next restart, not edited now.
* **An undisclosed limitation** — the traded universe is a single point-in-time selection held fixed
  across train, validation and the sealed test; it does not rotate. That is legitimate and is what the
  missing caveat was meant to say. **Now bounded empirically** — see §1.3.

### 1.3 ★ The §24 benchmark was not like-for-like — and fixing it STRENGTHENS the result

> **⚠ THE NUMBERS IN THIS SUBSECTION ARE SUPERSEDED BY RECORD §36 AND BY §6 BELOW.** They were
> computed over 1,631 sessions from 2020-01-02; the agents traded only the **1,571** sessions from
> **2020-03-30** (the 60-session production-lookback purge, R18, which silently contains the COVID
> crash). Corrected: EW-30 **+1.2825 / +183.3 %**, market_ew **+1.1656 / +274.1 %**, and **no reward
> beats passive holding even gross**. The *conclusion* of this subsection still stands — universe
> staleness is not the explanation and the over-trading finding survives on a same-universe
> comparator — but every FIGURE here must be read from §6. Do not quote this table.

Auditing the above exposed a confound the feedback did not catch. §24's passive proxy (+0.773 Sharpe,
+166 %) is `market_ew` over the **whole univ5 panel (953 RICs)**, while the agent trades **30** names.
Measured on the same 1,631 sealed sessions:

| benchmark | Sharpe (raw) | Sharpe (excess of rf) | cumulative |
|---|---|---|---|
| **EW buy-and-hold, the SAME 30 traded assets** | **+0.8170** | +0.6473 | +122.01 % |
| `market_ew` proxy, univ5 panel (953) | +0.7732 | +0.6489 | +166.00 % |

The like-for-like line is **stronger**, and risk-adjusted the two are within 0.0016. **Universe
staleness is not the explanation; the over-trading conclusion survives on a same-universe
comparator.** Full detail: record §29. Consequence for the write-up: state the absolute result against
the same-30 benchmark, which pre-empts the objection rather than inviting it.

**Also fixed by that audit:** every reported Sharpe is the **RAW** annualised figure —
`sharpe_ratio(returns, periods_per_year=252)` takes no risk-free argument. The comparison is
convention-consistent, but excess-of-rf differs materially (+0.773 → +0.649), so the convention must be
stated explicitly (Stefan's criterion 5; the standing R20 item).

### 1.4 The schedule premise is superseded — in our favour

The feedback calls the schedule *"the most likely way this ends badly"*, on the premise that the
campaign runs to **27 August** leaving one day of slack. **That premise no longer holds.** Cores have
gone 20 → 208 → 448 → **1,328**, and at that capacity the full registered ladder (n=568) completes
**~9 August** — 18 days inside the stop (record §27). The critical path is now the **document**, not
the compute, which is exactly the conclusion the feedback reaches for other reasons.

Minor arithmetic note: *"score 95 on the three research criteria and 75 on communication and you
average 90"* is right ((95×3+75)/4 = 90). But *"to reach 95 overall, communication has to reach roughly
92"* holds only if the research criteria are ~96; at 95/95/95 communication must itself be **95**. The
practical instruction — communication must reach the top band — is unaffected.

Also imprecise: communication is not *"currently zero"*. CH1-CH3 are drafted to publication standard;
what is unwritten is Results, Discussion, Conclusion and the presentation pass.

---

## 2. AN UNMET REGISTERED OBLIGATION THE FEEDBACK INDEPENDENTLY REDISCOVERED

The feedback recommends a dated preprint and *"depositing the frozen protocol with its hash"*. That is
**already a registered obligation** and it appears **UNMET**:

> `config/preregistration.yaml` → `freeze_day_checklist_additions.public_deposit`: *"at the v2 freeze:
> deposit the prereg bundle PUBLICLY (OSF or Zenodo, DOI'd) — the public timestamp anchor referees can
> verify"*

The v2.1 freeze executed, but open-defect register item **M** still records the external anchor as
only *"the commit + tag on origin"*, with no DOI. I found no evidence of an OSF/Zenodo deposit.
**This is a registered freeze-day item that was silently skipped** — precisely the class CLAUDE.md says
may never be dropped. It is cheap to discharge and it is the strongest available answer to the rubric's
publishability yardstick, because it is a third-party timestamp a marker can verify in seconds.

---

## 3. WHAT THE FEEDBACK GETS RIGHT AND WE SHOULD ADOPT

Ranked by value per unit of effort. Everything marked **free** costs no words (tables, figures,
appendices and the abstract are all excluded from the 10,000).

| # | action | why it earns the band | cost |
|---|---|---|---|
| A1 | ✅ **DELIVERED 2026-07-30 → `paper/tables/T_literature_positioning.md`.** **Literature positioning matrix** — neighbours × dimensions (who authors the reward, what the feedback contains, agent fixed?, risk-sensitive?, preregistered?), our row last with the empty cells filled | converts the novelty claim from prose into a three-second visual; makes the gap undeniable | **free** |
| A2 | ✅ **DELIVERED 2026-07-30 → `paper/tables/T_design_decisions.md`.** **Design decisions table** — choice / alternatives considered / why / what it costs | Criterion 2 is titled *reasoning to answer them*; a justified method with its cost visible is what "exemplary" means | **free** |
| A3 | ✅ **DELIVERED 2026-07-30 → `paper/tables/T_scale_and_difficulty.md`.** **Scale-and-difficulty appendix table** — components, tests, models, trainings, seed re-runs, campaign lines, pipeline stages, off-the-shelf vs written | Criterion 3 is normalised *given difficulty*; a marker cannot weight difficulty they cannot see | **free** |
| A4 | ✅ **DELIVERED 2026-07-30 → `paper/sections/CH1_contributions.md`, written in the §36-CORRECTED form (see §6).** **Numbered contributions with evidence attached**, and the **turnover result promoted to a named contribution** with its own results section | gives the significance marker something to point at; §29 now makes it a like-for-like, positive, counter-intuitive, reproducible sealed-test result | low |
| A5 | **Lead with the preregistration-absence limb** of the originality claim | the band says *unquestionable*; "no preregistration anywhere in the automated-reward-design literature" is a claim about a PRACTICE — verifiable, and undefeatable by naming an adjacent paper. Strictly stronger than the empty-cell claim, which is disputable by construction | low |
| A6 | **Quality-control-record appendix** — the four launches, ~115 amendments and the defect log, framed analytically as the machinery that caught errors *before* they reached confirmatory data | same facts, opposite effect; presented chronologically they read as a troubled project | low |
| A7 | **RQ stated identically three times** (boxed in intro, head of methodology, answered verbatim in conclusion) | Criterion 2 marks legibility of purpose first | trivial |
| A8 | **"The null is the finding" on page one**; **interpretive summary at the head of Results** | a marker who reaches the discussion still thinking it failed will not revise; the orientation paragraph is presentation, so it costs nothing in registered terms | trivial |
| A9 | **Wider-context subsection (~300 words)** — the numeracy bottleneck as a constraint on *any* automated optimisation loop that feeds a model numbers, stated outside finance | Criterion 1's *"and its wider context"* clause is currently unclaimed | low |
| A10 | **Mayoian severity paragraph** into the theory chapter | the amendment where we corrected Popperian → Mayoian error-statistical severity is the best single piece of evidence for original interpretation, and it currently lives in a config comment | low |
| A11 | **Faultless-data pass** — units on axes, standalone captions, consistent decimals, notation table, every figure referenced, no table needing prose to parse | this phrase *is* the 80→90 band boundary on a quarter of the mark | medium |
| A12 | **Public DOI deposit + dated preprint** (§2) | discharges a registered obligation and answers the publishability yardstick with a checkable artefact | low |

**Corroborations — the feedback independently reached conclusions already in our plan**, which is
reassuring rather than new: the literature review as a converging argument rather than a survey (our
playbook's "CH2-as-argument"); the null as a corroborated prediction; depth over breadth; the 16-section
order; reporting wall-clock compute. Where it agrees with Okhrati's revealed grading function, it
agrees for the right reasons.

---

## 4. THE ONE THING TO TREAT WITH CARE

The feedback's closing logic — *"if the format intervention recovers responsiveness, low-to-mid
nineties; if it nulls, high eighties"* — is sound but must not become a reason to prefer one outcome.
Our standing rule is that a predicted null is bankable and must never be spun. The psychometric module
is worth building **because it measures rather than infers**, whichever way it falls; that is exactly
the reason the R96 all-or-nothing clause exists. Build it for the measurement, not for the hoped-for
direction.

---

## 5. IMPLEMENTATION ORDER (respecting the live-run drift invariant)

`paper/` and `docs/` are **outside** the drift pathspec and can be written now.
`src/ scripts/ config/ prompts/` **cannot** be touched while the run is live.

**Now → 8 Aug (writing, no results needed):** A1, A2, A7, A5, A9, A10, and the ~5,900 words of
introduction / literature review / data / methodology. Resolve the R96 activation-scope question in
writing (§1.1) and discharge A12.

**At the next natural restart (deferred, registered):** the `config/prototype.yaml` dangling-caveat fix
(§1.2), plus the four already-registered code items in `docs/DEFERRED_FIXES_RUN4.md` (D12, D13, D14,
preflight headroom).

**6-9 Aug (data lands ~9 Aug, not 27 Aug):** A4, A8, A3, A6; write every figure script against
floor-tier data so the final pass is a regeneration, not a build — the feedback's single best schedule
instruction, and now with three weeks of slack instead of one day.

**Post-headline:** build and run the psychometric module; A11 as the final pass; abstract last.


---

## 6. ⚠ THE FEEDBACK'S NUMBERS PREDATE RECORD §36 — A4 WAS NOT WRITTEN AS SPECIFIED [RESOLVED 2026-07-30]

Added 2026-07-30 after the benchmark-window correction.

The feedback's highest-value contribution action (A4) instructs: *"promote the turnover finding to a
named contribution. Ten of eleven expert designed rewards lose money risk adjusted on a market that
gained **166 per cent** … and the one that charges for trading **wins** on every seed."*

**Both of those are now retracted (record §36).** The benchmarks were computed over 1,631 sessions from
2020-01-02, but the agents traded only the **1,571** sessions from **2020-03-30** — the 60-session
production-lookback purge (R18), which silently contains the COVID crash. Corrected:

| | as the feedback has it | **corrected (agents' own window)** |
|---|---|---|
| market proxy | +166 % | **+274.1 %** (Sharpe +1.1656) |
| EW-30 same assets | (+122 %, Sharpe +0.817) | **+183.3 %** (Sharpe **+1.2825**) |
| does turnover-pricing beat passive? | "wins" | **NO — +1.1606 vs +1.2825** |

**Writing A4 verbatim would have embedded a retracted claim in the dissertation.** The corrected framing
is stronger anyway, and it is what A4 should say:

> Ten of eleven expert-designed rewards return −0.17 … −0.33 net over the sealed window; the eleventh,
> which charges for trading, returns +1.161. **Gross** of transaction costs every design earns +0.82 …
> +1.17, so all carry real signal — but **none beats an equal-weighted buy-and-hold of the same thirty
> assets (+1.283), even before costs**, and all but one surrenders that signal entirely to a 20 %/year
> turnover drag.

That is a **better** contribution claim than "beats the market": it is counter-intuitive, positive
(a mechanism, not just a null), reproducible, computed by a REGISTERED report-only method, and — decisively
— it cannot be overturned by a referee re-deriving the benchmark, which is exactly how the error surfaced.

**Standing lesson for every remaining artefact:** the feedback was written against the pre-correction
record. Any figure it quotes must be re-derived from the records before it enters the PDF, per
analysis-time obligation 8 (windows come from `record.metrics.test_returns`, never a panel date filter).

**RESOLUTION (2026-07-30).** A4 was subsequently written in the corrected form above and delivered as
`paper/sections/CH1_contributions.md`. Verified by grep before marking it delivered: the retracted
figures (`0.817`, `+122`, `0.773`, `+166 per cent`) appear in **none** of the new artefacts except as
explicitly banned strings in the presentation checklist, and C3 states the window as
`2020-03-30 -> 2026-06-30` with the corrected `+1.283` comparator.

---


---

## 7. DELIVERY LOG

| action | status | artefact |
|---|---|---|
| A1 literature positioning matrix | ✅ delivered 2026-07-30 | `paper/tables/T_literature_positioning.md` |
| A2 design decisions with alternatives + cost | ✅ delivered 2026-07-30 | `paper/tables/T_design_decisions.md` |
| A3 scale and difficulty | ✅ delivered 2026-07-30 | `paper/tables/T_scale_and_difficulty.md` |
| A4 numbered contributions | ✅ delivered 2026-07-30 — C1–C4 evidenced, C5 marked PENDING; carries the §36-corrected figures (verified: no retracted number present) | `paper/sections/CH1_contributions.md` |
| A5 lead with the pre-registration limb | ✅ built into A1's "what the matrix shows" §2 | `T_literature_positioning.md` |
| A6 quality-control record appendix | DELIVERED 2026-07-30 | `paper/appendices/A_quality_control_record.md` |
| A7 RQ stated identically 3× | ✅ delivered 2026-07-30 — canonical form taken **verbatim** from the existing CH1 §1.2, not reformulated | `paper/sections/RQ_canonical_and_framing.md` |
| A8 null-is-the-finding p1 + results orientation | ✅ delivered 2026-07-30 — plus the three unfamiliar ideas taught in one sentence each | `paper/sections/RQ_canonical_and_framing.md` |
| A9 wider-context subsection | DELIVERED 2026-07-30 - **rebuilt on MEASURED findings; see the departure note in section 8** | `paper/sections/CH7_wider_context.md` |
| A10 Mayoian severity into the theory chapter | DELIVERED 2026-07-30 | `paper/sections/CH3_severity_paragraph.md` |
| A11 faultless-data presentation pass | ✅ delivered 2026-07-30 — the checklist itself; **walk it once the figures are final** | `paper/PRESENTATION_CHECKLIST.md` |
| A12 public DOI deposit + preprint | pending — **needs Tamer** (an account action) | — |

**Two things A2 and A3 added that the feedback did not ask for, and which are worth more than what it
did ask for:**

1. **A2 makes the SELF-HANDICAPS explicit and bold.** The feedback spotted one (long-only removes the
   natural route from tail-awareness to tail-protection). Auditing the design surfaced a **second**: the
   `max(val_DSR)` selector embeds skew/kurtosis, so it is not perfectly tail-blind and therefore
   **narrows the contrast under test, biasing against a measured distributional advantage** (the m13
   self-disclosure, already written and now surfaced into the table). A design that makes its own
   prediction *harder* to confirm is the strongest rigour signal available, and there are now two of
   them in one scannable column.
2. **A3's difficulty section names what a count cannot convey** — executing untrusted generated code
   42,128 times; holding an identification claim across twelve concurrent lines where three defects
   shared one shape that **no unit test could see** (all 2,875 exercise a single line); and bit-exact
   determinism as a frozen design constraint rather than an aspiration.


---

## 8. TWO PLACES WHERE THE FEEDBACK IS WRONG ON A DETAIL, RECORDED SO THE ERROR IS NOT INHERITED

**(a) A9 as specified would assert an unmeasured claim - DEPARTED FROM DELIBERATELY.** The feedback
proposes building the wider-context subsection around *"language models cannot reliably use small
numerical differences."* That is this study's registered **hypothesis** about the capability gradient, not
a result: the psychometric module that would supply a measured per-model detection threshold is
**specified (R96) but NOT BUILT**, and H2's confirmatory contrast is not yet scored. Writing it as
delivered would assert a conclusion from an inference - the exact move this project's standards forbid,
and the first thing a referee would attack.

The delivered subsection is therefore built on **three findings that ARE measured**, each generalising
past finance on its own: (1) outcome scoring cannot separate a working generated artefact from a
half-broken one propped up by a fallback, so any pipeline accepting machine-generated code on results
alone is blind exactly where contamination is most attractive; (2) a reflection loop needs a prior success
to reflect on, so the capability threshold for self-improvement is "good enough to succeed once", not
"good enough to improve"; (3) ten expert objectives all carried signal and all lost it to one unpriced
friction, so sophistication in the modelled quantity does not substitute for pricing the dominant real
cost. The numeracy paragraph is **pre-written and HELD**, to insert only if the measurement lands.

**(b) A10's source is not "a config comment".** The feedback says the Popperian -> Mayoian correction
*"right now lives in a config comment"*. It is in fact registered amendment **R61** (2026-06-28) with a
full statement in `PREREGISTRATION.md` section 1a, citing Rubin (2025, *Synthese*), Gelman & Loken (2014),
Lakens et al. (2018) and Campbell & Gustafson (2018). The feedback's *instruction* still stands - it
belongs in the **theory chapter**, because Criterion 1 marks original interpretation from the literature
review, references and discussion rather than from a protocol appendix - but the artefact was written from
R61's actual text rather than reconstructed from a comment.

---

## 9. THREE ARTEFACTS THE FEEDBACK ASKED FOR THAT ALREADY EXISTED

Checked before building, which changed the work. **None was rebuilt; two were extended.**

| the feedback asks for | already existed | action taken |
|---|---|---|
| a notation table | `paper/NOMENCLATURE.md` — 52 lines, symbols + definitions + first use + an explicit sign convention | **left alone**; it already satisfies the requirement |
| a limitations register | `paper/APPENDIX_B_limitations.md` — 216 lines, grouped by validity type, each item with direction of bias and mitigation | **extended** with §B.8, the six executed-run limitations it was missing entirely |
| a figure/table manifest | `paper/FIGURE_TABLE_MANIFEST.md` — numbered, with NOW/CAMPAIGN status | **extended** with T10–T17 and S1–S4 |

Rebuilding any of them would have been a defect rather than diligence: expanding what needs no expansion
is precisely the failure the LEAVE-ALONE discipline exists to prevent. The *gaps* in them were real, and
are now closed.

## 10. WHAT REMAINS, AND WHO OWNS IT

| item | owner | note |
|---|---|---|
| **C5 — the confirmatory answer** | the campaign | the slot is intentionally empty until the sealed test is scored; listed so the structure is visible, not to bank a result in advance |
| **A12 — public OSF/Zenodo DOI deposit** | **Tamer** | a *registered* freeze-day obligation (`freeze_day_checklist_additions.public_deposit`) that appears UNMET; an account action, and the cheapest available answer to the rubric's publishability yardstick |
| the psychometric module (R96) | **Tamer's dated decision** | specified but **NOT built**; its all-or-nothing clause may commit BOTH axes (~$23–37, not $10) — resolve in writing before any spend |
| the single carrying figure | contingent | psychometric overlay if the module lands; otherwise the named fallback (baseline Sharpe distribution ordered by turnover), buildable from already-archived data |
| walking the presentation checklist | write-time | once, when the figures are final — an unticked box is a defect, not a preference |
| the ~5,900 words of prose that need no results | write-time | intro / literature / data / methodology; the tables above now carry the comparisons, so the prose does not have to |
