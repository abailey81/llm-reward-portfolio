# ★★★ THE 95%+ MASTER PLAN — every criterion, every action, every gate

> **Purpose.** One document that consolidates the marking criteria, the IFTE0008 guidelines, every
> supervisor feedback strand, the exemplar calibration, and the live state of the artefact into a
> single executable plan whose target is **95%+ on each of the four criteria independently**.
>
> **Created** 2026-07-31. **Owner:** Tamer. **Status:** ACTIVE — this supersedes ad-hoc grade planning
> and is checked at every write-time step alongside the four authorities in `CLAUDE.md`.
>
> **Sources read first-hand for this plan:** `02_guidelines_and_examples/guidelines/MSc_Project_Marking_Criteria_2019-20.pdf`
> (verbatim) · `MSc_Project_Guidelines_2025-2026.pdf` (13 pp, verbatim) · all four
> `2022-23_Dissertation_Example_*.pdf` (profiled) · `paper/` tree · `docs/V2_WRITE_TIME_REGISTRY.md`
> (43 rows) · `paper/PRESENTATION_CHECKLIST.md` · `scripts/build_paper.py` · `scripts/word_budget.py`
> · Dr Okhrati's 2026-07-31 supervision feedback · the industry-supervisor feedback (Raad, Stefan) ·
> the 2026-07-29 route-to-top-band analysis.

---

## §0 THREE CORRECTIONS TO PREMISES WE HAD BEEN TREATING AS FACT

**0.1 — We do not know how the four criteria are aggregated.** Neither the marking-criteria PDF nor the
guidelines states a weighting or an aggregation rule; the criteria document is a bare 4×9 grid and the
guidelines say only *"the marking scheme for dissertations is available on Moodle."* Our own two
internal documents **contradict each other** — `CLAUDE.md` asserts *"four equally-weighted dimensions
where the weakest caps the mark"*, while `00_planning/DISSERTATION_ALIGNMENT_AND_GUIDELINES.md` asserts
*"the two highest-weight intellectual dimensions"*. **Neither cites a source.**
→ **Operative posture: assume the harshest plausible rule — all four must independently reach the
target.** This costs nothing if we are wrong and saves everything if we are right.

**0.2 — Four required artefacts are written but UNWIRED.** `paper/sections/` contains
`RQ_canonical_and_framing.md` (1,053 w), `CH7_wider_context.md` (756 w), `CH1_contributions.md`
(951 w) and `CH3_severity_paragraph.md` (757 w). None of them appears in `scripts/build_paper.py::ASSEMBLY`.
→ **The dominant remaining work is assembly, restructuring and presentation — not authoring.**

**0.3 — Two of our chapters are not sections the guidelines permit.** The required structure has
**no Theory section and no Prototype section**. `02_CHAPTER_theory.md` (4,000 counted words) and
`CH5_prototype.md` (1,402) are both in `ASSEMBLY`.
→ Relocating them is required for conformance **and** delivers 5,002 of the ~10,177 words we must cut.

---

## §1 THE RUBRIC, READ EXACTLY

Four criteria. Bands: **90–100 (A+) · 80–89 (A) · 70–79 (A−) · 60–69 (B) · 50–59 (C) · <50 fail.**

### The four discriminators — each turns on a single word

| | 80–89 band says | 90–100 band ADDS | Discriminator |
|---|---|---|---|
| **C1** Breadth & independence | "extra-curricular academic reading, critical thought and original interpretation" | "…Exceptional insight into the problem **and its wider context**" | **wider context** — appears in NO other band |
| **C2** Research design | "**only very minor faults** in execution… **clearly** original thought" | "**Faultless** execution, exemplary analysis with **entirely** appropriate methods, **unquestionable** originality" | **zero visible faults** |
| **C3** Novelty & significance | "**Challenging** project → **significant** contribution (e.g. **international conference**)" | "**Extremely challenging** project → **outstanding** contribution (e.g. **peer-reviewed journal**)" | **outstanding, not significant** |
| **C4** Communication | "Excellent write up **with only minor faults**, highly readable, extremely clear with excellent structure" | "Excellent write up both in terms of readability, clarity and structure, **with faultless presentation of data**" | **faultless presentation of data** |

### ★ The single most important reading in the whole rubric

**Both C4 bands say "excellent write up."** The 80–89 band **never mentions data presentation at all.**
The only thing the top band adds is **"faultless presentation of data."**

> **Criterion 4's top band is gated on a mechanical, checkable, fully controllable property — not on
> writing talent.** It is therefore the most reliably winnable quarter of the mark, and it is currently
> our weakest. This inverts the usual assumption that communication is the "soft" axis.

### Second-order rubric facts that shape strategy

- **"given difficulty of the problem"** is in C3's row *title* — a normalising clause, and the most
  favourable wording in the rubric for this project. **But a marker cannot weight difficulty they
  cannot see.**
- **"containing irrelevant material"** is a 50–59 band descriptor for C4. **Breadth without purpose
  actively costs marks.** This constrains the appendix strategy (see §6.3).
- C3's "publishable in peer-reviewed journal" is prefixed **"e.g."** — journal publishability is an
  *example* of an outstanding contribution, not its definition.

---

## §2 THE GUIDELINES — BINDING REQUIREMENTS AND OUR CONFORMANCE

| Requirement (verbatim) | Status |
|---|---|
| **"must not exceed 10,000 words"** — excludes title page, ToC/lists/glossary, **the abstract**, **mathematical content (formulas and equations) and coding**, **diagrams, tables, figures and graphs**, **footnotes**, references, **appendices**. *"Penalties will apply for exceeding the word limit."* | ❌ **20,177** |
| Escape hatch: *"If you believe that exceeding the limit is necessary, discuss this with your supervisor first, followed by the Programme Director for approval."* | ⚠ available, unused |
| **16 sections in the prescribed order** (Cover · Title · Abstract · Acknowledgements · ToC · List of Figures · List of Tables · Introduction · Literature Review · **Data (if applicable)** · Methodology & Analysis · Results · Discussion · Conclusions & Recommendations · References · Appendices) | ❌ non-conformant |
| **Core (Methodology + Results + Discussion) ≈ 60%** | ❌ **46.8%** (9,439 / 20,177) |
| *"Avoid simply presenting a chronological account of your work — guide the reader through your research journey in a structured and analytical way."* | ⚠ the four-run history must be **analytical**, never chronological |
| *"The second marker… may come from any discipline and will only assess your submitted report."* | ⚠ **de-jargonising is mandatory** (§6.4) |
| *"A quantitative component is strongly encouraged, particularly for those aiming for high-grade classifications."* | ✅ overwhelmingly |
| Abstract *"self-contained and readable as a standalone document. Avoid merely summarising your conclusions or objectives."* | ⚠ exists; result slot pending |
| **Acknowledgements** — *"sponsors, industry partners, data providers"* | ❌ **STUB** — we use licensed Refinitiv/LSEG data and UCL Myriad compute |
| Arial/Helvetica **≥10 pt**; **1.5** line spacing; pages numbered consecutively **from the title page** incl. appendices | ✅ build sets 12 pt, linestretch 1.5, Helvetica family — **verify pagination** |
| **Harvard** referencing | ✅ Cite-Them-Right CSL wired |
| **Ethics Assessment Form / Data Protection Form** — *"It is your responsibility to ensure that any necessary forms are submitted and approved on time."* | ⚠ **UNVERIFIED — see §7 R-1** |
| Deadline **1 Sep 2026**; Turnitin PDF | ✅ |
| Dissertations ≥70% are **published on the departmental website** | note: the PDF will be public |

---

## §3 CALIBRATION — WHAT A DISTINCTION LOOKS LIKE IN THIS DEPARTMENT

Profiled from the four exemplar dissertations on disk:

| | Pages | Raw words (whole PDF) | Figures | Tables | References |
|---|---|---|---|---|---|
| Example 1 | 52 | ~11,242 | 7 | 7 | ~25 |
| Example 2 | 41 | ~11,360 | 4 | 14 | — |
| Example 3 | 46 | ~11,566 | 14 | 4 | — |
| Example 4 | 64 | ~12,073 | 2 | 12 | — |

**Three calibration facts that matter:**

1. **Our 20,177 counted body words exceed an entire exemplar PDF — front matter, references and
   appendices included — by roughly 2×.** We are currently submitting two dissertations.
2. **Exemplars carry 2–14 figures and 4–14 tables.** We plan **21 figures and 17 tables**. More
   artefacts means more opportunities to be *non*-faultless, on a criterion whose top band requires
   zero defects. → **§6.3: cut the body figure set to ~10.**
3. **Exemplar 1 cites ~25 references; our `refs.bib` holds 274 entries.** That ratio *is* the
   "considerable extra-curricular reading" evidence — but only if the rendered reference list and the
   positioning matrix make it visible.
4. **Exemplar structure is instructive:** Example 1 devotes a full six-subsection chapter to Data
   (collection · cleaning · summary statistics · **visualisation** · stationarity · splitting). A
   dedicated, EDA-rich Data section is *expected* here — and it is exactly where Dr Okhrati's
   "motivate the method with the data" is satisfied.

---

## §4 CURRENT STATE OF THE ARTEFACT

| Component | State |
|---|---|
| Body chapters | 7 files, **20,177 counted words** (CH1 2,588 · CH2 2,748 · Theory 4,000 · CH4 5,125 · Prototype 1,402 · CH6 2,422 · CH7 1,892) |
| `paper/sections/` | **4 files written, none in ASSEMBLY** (canonical RQ · wider context · numbered contributions · severity paragraph) |
| `paper/tables/` | **8 tables built** across 5 files — T10 positioning matrix · T11 design decisions · T12 scale & difficulty · T13 arms · T14 environment · T15 decision rules · T16 models+pins · T17 reward canon |
| `paper/appendices/` | A — quality-control record |
| `APPENDIX_B_limitations.md` | 3,805 w — 8 categories, word-excluded |
| `outputs/figures/` | **43 files** (~21 figures × PDF+PNG) |
| `paper/PRESENTATION_CHECKLIST.md` | ✅ **written and excellent — never run** |
| `paper/NOMENCLATURE.md` | ✅ notation table |
| `docs/V2_WRITE_TIME_REGISTRY.md` | **43 rows**, 5 marked DRAFTED |
| Build | pandoc 3.10 + Tectonic, Harvard CSL, 12 pt, 1.5 spacing, ASSEMBLY = 7 chapters + appendices |

---

## §5 THE ACTION REGISTER — every action that moves a criterion

Legend: **[W]** written/built, needs wiring · **[N]** new · **[F]** framing/prose · **[X]** external/procedural

### C1 — Breadth of background knowledge and independence of thought

| # | Action | Clause served | State |
|---|---|---|---|
| C1-1 | Wire **T10 positioning matrix** into the Literature Review | considerable reading; makes the gap legible in 3 seconds | **[W]** |
| C1-2 | Restructure the Literature Review as a **converging argument in five moves** — reward design is the bottleneck → automated reward design exists and works → its feedback is universally scalar → in this domain shape is what matters → nobody has tested whether shape is usable | original interpretation; *a survey scores in the seventies, an argument that arrives somewhere scores in the nineties* | **[F]** |
| C1-3 | **Wire `CH7_wider_context.md`** into the Discussion | **the wider-context clause — 90–100 ONLY** | **[W]** |
| C1-4 | **Re-spine the wider-context section on the four-noise-barrier account** — every automated design loop that feeds a model numbers faces serial signal-to-noise barriers; here is a method for locating the binding one | *exceptional* insight into the **wider context** — it must leave finance entirely and reframe a problem class | **[N]** |
| C1-5 | Wire **`CH3_severity_paragraph.md`** (Mayoian error-statistical severity; amendment R61) into Methodology, before the hypotheses | original interpretation — the strongest single piece of evidence for it in the project | **[W]** |
| C1-6 | Build the **"reading that changed the design" table** — which papers actually altered a decision | turns *original interpretation* from an assertion into something checkable; word-excluded | **[N]** |
| C1-7 | Add a **"what each neighbour would predict"** column to T10 | converts a descriptive matrix into an argumentative one | **[N]** |
| C1-8 | State explicitly that the corpus spans **six fields that rarely co-occur** (decision theory · coherent risk measures · backtest statistics · equivalence testing · empirical asset pricing · LM interpretability) | this *is* the "considerable extra-curricular reading" evidence and it is currently implicit | **[F]** |
| C1-9 | Verify every rendered reference is cited, real and Harvard-consistent (`scripts/check_citations.py`) | referencing is named in every band | **[X]** |

### C2 — Research design

| # | Action | Clause served | State |
|---|---|---|---|
| C2-1 | Wire **`RQ_canonical_and_framing.md`** — the identical research question, verbatim, in **three places**: boxed on page 1 of the Introduction, at the head of Methodology, answered in the Conclusion | the row title puts *"clear statement of objectives or research questions"* **first** — this criterion is partly marked on legibility of purpose | **[W]** |
| C2-2 | ★ **THE DEVIATION REFRAME.** Present **RUN 4 as the executed study**, cleanly. The four launches, 115 amendments and defect log go to the **quality-control appendix**, framed **analytically** as the machinery that caught errors before they reached confirmatory data | **"faultless execution"** — the single highest-leverage framing decision in the dissertation. *Same facts, opposite effect.* The guidelines explicitly warn against chronological accounts | **[F]** |
| C2-3 | Build the **"faults our own machinery caught"** table — defect → how found → fix → what it would have cost | converts the four-run history into evidence **for** faultlessness | **[N]** |
| C2-4 | Add a **"what would overturn this choice"** column to T11 design decisions | *reasoning to answer them* — the counterfactual duty applied to design; reads as exceptional rigour | **[N]** |
| C2-5 | **Lead the novelty claim with the pre-registration-absence limb**, not the empty cell | **"unquestionable"** originality. The empty cell is *questionable by construction* — anyone can name a neighbour. *Pre-registration being absent from the entire automated-reward-design literature* is a claim about a **practice**: verifiable, and undefeatable by pointing at a similar study | **[F]** |
| C2-6 | Run the **"entirely appropriate methods" audit** — every method in the stack, is it the right tool? Demote or remove any that is not | **"entirely"**. One inappropriate method costs the band. Precedent: the FZ0/Diebold–Mariano backtest was demoted to a calibration diagnostic when we established it could not corroborate the tail hypothesis | **[N]** |
| C2-7 | **Foreground the positive controls** — we built stimuli where the responsiveness metric *must* fire, so a null cannot be dismissed as a broken instrument | exemplary analysis; this is a genuinely sophisticated methodological move currently buried | **[F]** |
| C2-8 | **Foreground the falsify-both-ways discipline** — every new test was proven to FAIL against the pre-fix code before being trusted | faultless execution, made checkable | **[F]** |
| C2-9 | **Pre-write objection 3 into Methodology** (see §7 A-3): *"your agent churns 90% of the book daily — was your environment capable of showing the effect?"* | there is no viva; every objection must be answered in the text before it is asked | **[N]** |
| C2-10 | Deposit the frozen pre-registration publicly with a DOI (**A12**, staged, ~10 min) | a public, timestamped, hash-bound protocol is extraordinary at MSc level and is *checkable* | **[X]** |

### C3 — Novelty and significance of research outcomes given difficulty

| # | Action | Clause served | State |
|---|---|---|---|
| C3-1 | Wire **`CH1_contributions.md`** — numbered claims, each with the specific result that supports it and the section where it lives | *"markers assessing significance are looking for something to point at"* | **[W]** |
| C3-2 | ★ **Promote the turnover finding to a numbered contribution with its own Results subsection.** Ten of eleven expert-designed rewards lose money risk-adjusted on sealed data; the one that prices trading returns **+1.154 Sharpe [1.115, 1.196]**; the losers churn **78–91%** of the book daily against **0.8%**; mechanism measured (near-argmax chasing; HHI 0.33 / eff-N 4.2 vs 0.074 / 13.5) | **outstanding contribution** — a *positive*, counterintuitive, reproducible result on a sealed test set, independently demonstrating the premise of the whole dissertation. Currently filed as comparator work | **[N]** |
| C3-3 | Report the **estimation dose–response**: `min_cvar` (optimises the mean of 3 of 60 observations) degrades **88%** in→out-of-sample; `minimum_variance` 30%; `risk_parity` 10%; `equal_weight` (estimates nothing) **4%** — monotone in estimation intensity | a second positive, measured, mechanistic finding; the optimiser's curse specialised to tail functionals | **[N]** |
| C3-4 | ★ **Write the four-noise-barrier account as the Discussion spine.** Estimation ≈1:1 · **Perception — unmeasured (R96)** · Optimisation 1:15 · Measurement 1:5. *Every link in this pipeline is noise-limited; here is the measured SNR at each and which binds first* | reframes the paper from *"does tail feedback help?"* to *"we instrumented a four-link automated-design pipeline end to end"* — a **positive quantitative claim**, not a null | **[N]** |
| C3-5 | Add a **lineage-comparison column** to T12 (our trainings / cost / models vs Eureka, RD-Agent, REvolve) | **"extremely challenging"** is normalised and invisible; difficulty is relative, so make it checkable | **[N]** |
| C3-6 | **Dated arXiv preprint** before submission | the rubric's own yardstick is publishability; a timestamped link a marker can check in ten seconds beats an assertion | **[X]** |
| C3-7 | **"What a practitioner can now decide" box** — the responsiveness audit, the bounded-equivalence verdict as a costed basis for *not* building a feature, the legibility lever, the authoring-reliability table | what makes a contribution **significant** rather than merely novel (Raad/Stefan's success-metrics point) | **[N]** |
| C3-8 | **Activate R96** (psychometric module), dated | the pre-written answer to objection 8 — see §7 A-8. Decide **now**, because no confirmatory datum exists yet, which makes the decision provably outcome-independent | **[X]** |
| C3-9 | Name the study as a **Registered Report** in form | a recognised, prestigious format that markers and reviewers recognise instantly | **[F]** |
| C3-10 | List the **public artefact set** as checkable publishability evidence: repo, model card, datasheet, CITATION.cff, reproducibility checklist, DOI'd protocol, preprint | converts "publishable" from a claim into an inventory | **[F]** |
| C3-11 | **Kimi K3 open-weights rule (R95) fired 27 Jul** — verify licence permissiveness and checkpoint↔snapshot correspondence, then amend at the C4 restart. Takes the roster to **6 of 11 authors open-weight** | strengthens the reproducibility contribution on exactly the axis the industry supervisors pressed | **[X]** |

### C4 — Communication

| # | Action | Clause served | State |
|---|---|---|---|
| C4-1 | ★ **PHASE 1 RESTRUCTURE** — Theory → Appendix C (intuition ~400 w retained in Methodology); Prototype → Appendix D; create **§10 Data (~700 w)**; split CH7 into **§13 Discussion** + **§14 Conclusions**; wire the four orphan sections; update `ASSEMBLY` to the 16-section order | structure; conformance; **−5,002 words** | **[N]** |
| C4-2 | ★ **PHASE 2 COMPRESSION to ≤9,500** (a deliberate margin below 10,000, since our word-count method is our own interpretation) | readability, clarity, and the explicit over-length penalty | **[N]** |
| C4-3 | ★ Build **`scripts/presentation_lint.py`** — machine-gate the checklist; exit non-zero on any failure | **makes "faultless presentation of data" a gate rather than an eyeball pass** | **[N]** |
| C4-4 | **Run `paper/PRESENTATION_CHECKLIST.md`** item by item against the final document | it is already written and excellent; it has never been run | **[W]** |
| C4-5 | ★ **THE DE-JARGONISING PASS** — every term defined in plain language on first use or replaced. *3-leg IUT · rung 403 · the C3 gate · mode D · R115 execution floor · arms / legs / lines / candidates / generations* | *"The second marker may come from any discipline"* — this is the guidelines' own named risk and our densest liability | **[N]** |
| C4-6 | **Fill the Acknowledgements** — Refinitiv/LSEG (data licence), UCL Myriad (compute), Dr Okhrati, Raad and Stefan (industry engagement — also a stated learning outcome) | a stub in section 4 of 16 is a visible fault on a criterion requiring zero | **[N]** |
| C4-7 | **Decide the single figure.** Candidate: the psychometric threshold overlay if R96 fires; otherwise the four-barrier SNR exhibit or the turnover/Sharpe distribution | every strong paper has one image that carries it, legible to someone who knows no finance | **[N]** |
| C4-8 | **Cut the body figure set to ~10** carrying the argument; the rest to appendices, still lint-clean | exemplars carry 2–14; 21 body figures is 21 chances to be non-faultless | **[N]** |
| C4-9 | **One-page "How to read this dissertation"** | for the any-discipline second marker | **[N]** |
| C4-10 | **Interpretive summary at the head of Results** — what the reader is about to see and why the order is what it is | presentation, not analysis, so it costs nothing in registered terms | **[N]** |
| C4-11 | **Say on page one that the null is the finding** | a marker who reaches the Discussion still believing the project failed has already formed their view | **[F]** |
| C4-12 | **Abstract rewritten LAST** — ~300 words, self-contained, *not* merely summarising conclusions; states: we predicted a tie, found it, located where the chain breaks, identified the fix | word-excluded, read first by both markers, sets the frame for everything else | **[F]** |
| C4-13 | Verify PDF compliance: font ≥10 pt (build sets 12) · 1.5 spacing (set) · **pages numbered consecutively from the title page including appendices** · Harvard throughout | free marks, conspicuous when absent | **[X]** |
| C4-14 | **Curate the appendix set** — each appendix has a stated purpose and is referenced from the body | the 50–59 band penalises *"irrelevant material"*; an uncurated appendix dump reads as padding | **[N]** |
| C4-15 | **Any-discipline reader gate** — a genuine non-specialist reads the Introduction and Results and reports back (registry row 24) | the only real test of the criterion | **[X]** |

### Cross-cutting

| # | Action | Why |
|---|---|---|
| X-1 | **Verify the Ethics / Data Protection forms were submitted and approved** | the guidelines make it the student's responsibility; we use licensed third-party financial data. **Unverified — potentially serious** |
| X-2 | **Dr Okhrati's written sign-off on `PROPOSAL_PIVOT_DISCLOSURE.md`** | still DRAFT; the one external procedural blocker |
| X-3 | **Interim report pack to all three supervisors, 6–8 Aug** | pre-registered obligation (R81); presentation-only effect |
| X-4 | **Mandatory pre-submission novelty sweep (~20 Aug)** | our own standing rule; the fence discipline |
| X-5 | **`docs/RUBRIC_CONFORMANCE.md`** — every top-band clause → its artefact → its state; fails on any unsatisfied clause | the closest thing to verification that honestly exists |
| X-6 | **`docs/WHY_REGISTER.md`** — Dr Okhrati's D1–D6 applied campaign-wide: every quantity carries OBSERVATION · MECHANISM · UNCERTAINTY · COUNTERFACTUAL, generated from the 35 `out[...]` analysis keys | his 2026-07-31 feedback, scoped to the whole campaign |
| X-7 | **Seed-trajectory panel** — his explicit #1 request; small multiples over every seeded unit, plus the per-seed-block heterogeneity variant | see §7 A-9 for the discipline it must carry |
| X-8 | **Turnitin similarity check** well before the deadline | we quote our own protocol extensively |

---

## §6 THE STRUCTURAL OPERATION — EXACT ARITHMETIC

### 6.1 Phase 1 — restructure (relocation only, no rewriting)

| Move | Rationale | Δ counted words |
|---|---|---|
| **Theory (4,000) dissolved** — ~400 w of intuition + the dominance statement into Methodology; the severity paragraph into Methodology; **all theorems, proofs and formal apparatus → Appendix C** | no Theory section exists in the required structure, and *"mathematical content (formulas and equations)"* is **explicitly word-excluded** | **−3,600** |
| **Prototype (1,402) → Appendix D** | not a permitted section, and **no prototype number enters the dissertation** | **−1,402** |
| **Create §10 Data (~700)** from Methods §4.2 — the home for the stylised-facts EDA (F3) | required by the structure; the exemplars devote a full chapter to it; and it is where *"motivate the method with the data"* is satisfied | 0 |
| **Split CH7 → §13 Discussion + §14 Conclusions & Recommendations** | required by the structure | 0 |
| **Wire the four orphan section files**; update `ASSEMBLY` | they are written | 0 |

**→ 15,175 words.**

### 6.2 Phase 2 — compression (−5,175 exactly; target ≤9,500 with margin)

| Section | Now | Target | Cut | Method |
|---|---|---|---|---|
| Introduction | 2,588 | 1,100 | −1,488 | contributions become a **table** (excluded); roadmap → the ToC does that job; scope-and-limits → footnotes (excluded) |
| Literature Review | 2,748 | 1,700 | −1,048 | **T10 carries the comparison**; prose becomes only the five-move converging argument |
| Data | — | 700 | 0 | new section |
| **Methodology & Analysis** | 4,825 | **2,400** | **−2,425** | **every specification sentence becomes a table row** — T13/T14/T15/T16/T17 are already built and unused |
| Results | 2,422 | 2,300 | −122 | trim |
| Discussion + Conclusions | 1,892 | 1,800 | −92 | trim |

**→ exactly 10,000; then trim to ≤9,500 for margin. Core = 6,100 = 61%** against the guidelines'
*"approximately 60%"*.

### 6.3 ⚠ The word-excluded carriers — and the trap in using them

**Unambiguously excluded (verbatim from the guidelines):** appendices · tables · equations and
mathematical content · **footnotes** · references · the abstract · ToC/lists/glossary.

⚠ **Captions are NOT named in the exclusion list.** Do **not** load explanation into figure captions —
load it into appendices, table cells, equations and footnotes. **Footnotes are an explicitly sanctioned
lever we are not using at all.**

⚠ **The appendix trap.** The rubric's 50–59 band penalises *"containing irrelevant material."* Pushing
10,000 words into appendices to dodge the count **will backfire if the appendices read as a dump**.
Every appendix must have a stated purpose and be referenced from the body (**C4-14**).

### 6.4 ⚠ The jargon liability — our densest C4 risk

The guidelines name the any-discipline second marker as a specific hazard. Our internal vocabulary is
extreme: *arms · legs · lines · rungs · candidates · generations · the 3-leg IUT · R115 execution floor ·
mode D · the C3 gate · CRN pairing · SESOI · TOST · PBO/CSCV · IQM.* A structural engineer will drown.

**Rule for the writing pass: every term is defined in plain language at first use, or replaced.** The
`NOMENCLATURE` table is a backstop, not a substitute. This is **C4-5** and it is a full pass over the
document, not a spot fix.

---

## §7 THE ADVERSARIAL AUDIT — there is no viva, so every answer is pre-written

| # | Objection a hostile examiner would raise | Pre-written answer |
|---|---|---|
| A-1 | *"Your body is twice the word limit."* | ❌ → §6 |
| A-2 | *"You have chapters the required structure does not permit."* | ❌ → §6.1 |
| A-3 | ★ *"Your agent rebalances 90% of the book daily. Was your environment even capable of showing the effect you were testing for?"* | ⚠ **the sharpest objection.** Answer: the arms are identical, so the contrast remains identified; churn is a **common** shift, not a confound. What it does is inflate σ_D and cost power — which we **measured** (σ_seed 0.244) and compensated for with the assurance ladder. **Must be written into Methodology (C2-9), not discovered by a referee.** |
| A-4 | *"Your control arms had half the candidate pool."* | ✅ the deviation is disclosed; bias direction is stated (**toward** a false positive for our own hypothesis); the equal-*k* sensitivity was registered **pre-data**; the C3 integrity gate fails closed on exactly this condition |
| A-5 | *"PopArt was inert on half your archive."* | ✅ arm-symmetric across the five LLM arms (62–67%), so H2 is protected; asymmetric on H1, disclosed with the mechanism (reward magnitudes span **five orders of magnitude**, 0.027 → 5,827; PopArt engages iff RMS > 1) |
| A-6 | *"GIFT, ELfolio and AlgoEvolve exist — where is the novelty?"* | ✅ T10 positioning matrix + the pre-registration-absence limb |
| A-7 | *"Your best reward loses to equal weight."* | ✅ stated plainly; it is a finding, and the honest phrasing is *"ties the cap-weighted index, loses to equal weight"* — never *"beats the S&P"* |
| A-8 | ★ *"You never verified the models could read the numbers you fed them."* | ❌ **unanswerable without R96.** This — not marginal marks — is what should decide activation |
| A-9 | *"Your seed-trajectory plot shows the estimate settling; did you stop when it suited you?"* | ⚠ **the trap in Dr Okhrati's own request.** Answer requires all three: seeds in **registered order, never sorted**; the **exogenous stopping rule stated in the caption** with the terminal rung marked; an explicit statement that **no inference was drawn at any prefix** |
| A-10 | *"Ten of your eleven human baselines lose money — is your environment realistic?"* | ✅ mechanism measured (§C3-2/C3-3); the classical allocators all clear +0.60 on the same environment, so the environment is not the problem — the reward's blindness to movement is |

---

## §8 RISKS IN THIS PLAN ITSELF

| # | Risk | Mitigation |
|---|---|---|
| R-1 | **Ethics / Data Protection forms may not have been submitted.** The guidelines make this the student's responsibility and we use licensed third-party data | **Verify immediately (X-1).** Potentially serious and entirely outside the writing plan |
| R-2 | **The appendix strategy reads as a dump** and triggers the *"irrelevant material"* descriptor | C4-14 — every appendix earns its place and is referenced |
| R-3 | **Cross-reference soup** — a body that is mostly pointers reads worse, not better | the prose spine must remain **self-contained**; appendices add depth, they do not carry the argument |
| R-4 | **Our word-count method is our own interpretation**; a marker may count differently | target **≤9,500**, not 10,000 |
| R-5 | **August is consumed by the campaign** and the write-up compresses into the final week | **this is the largest single threat to the target.** The schedule (§10) front-loads everything that needs no results (~5,900 words) |
| R-6 | **The campaign truncates and H2 lands INCONCLUSIVE** | materially de-risked: three contributions (C3-2, C3-3, C3-4) are **measured and outcome-independent** |
| R-7 | **"Faultless execution" is a judgement call** and we have a real documented deviation | C2-2 moves it from likely-fault to likely-strength, but it is not fully controllable |

---

## §9 VERIFICATION GATES

Three machine-checkable gates, run before submission; any failure blocks:

1. **`scripts/presentation_lint.py`** (C4-3) — axes+units · decimal consistency within columns · every
   figure and table cross-referenced · standalone captions · every symbol in NOMENCLATURE · zero
   dangling citation keys.
2. **`scripts/word_budget.py`** — ≤9,500 with the PASS ceiling; core ratio ≈60%.
3. **`docs/RUBRIC_CONFORMANCE.md`** (X-5) — every top-band clause mapped to its artefact and its state;
   fails on any unsatisfied clause.

Plus the existing: `scripts/check_citations.py` · `scripts/audit_reproducibility.py` ·
`docs/V2_WRITE_TIME_REGISTRY.md` zero-open-rows sweep.

---

## §10 SCHEDULE

| Window | Work |
|---|---|
| **Now → 8 Aug** | **Phase 1 + Phase 2** (restructure + compress). Wire the four orphan sections. Build `presentation_lint.py`. Fill Acknowledgements. A12 DOI deposit. **Verify the ethics forms.** Decide and date R96. |
| **6–8 Aug** | Floor-tier results land. Draft the Results chapter against real numbers and **build every figure script now against rung-30 data**, so the final run is a *regeneration*, not a build. **Interim report pack to all three supervisors.** |
| **8–20 Aug** | Discussion · the wider-context subsection · limitations. The C1/C2/C3 upgrade actions. Preprint prepared. Adversarial pass (§7) written into the text. **Complete draft to Dr Okhrati with provisional numbers.** |
| **20–27 Aug** | Campaign completes. **Regenerate every figure and table from final data. No new writing — substitution only.** Pre-submission novelty sweep. |
| **27–31 Aug** | Abstract rewritten last. De-jargonising pass. All three gates. Turnitin. **Submit with days in hand, not hours.** |

---

## §11 HONEST CONFIDENCE STATEMENT

**No plan can guarantee a mark** — it is a human judgement on a document, and claiming otherwise would
violate this project's own evidence standard. The strongest honest claim is:

> **After this plan, every clause of every top band is satisfied by a named artefact, and two of the
> four criteria are gated by machine checks rather than by judgement.**

| Criterion | Confidence at 95 | Residual risk |
|---|---|---|
| **C1** Breadth & independence | **High** | none material once the wider-context section is wired; the reading is genuinely exceptional |
| **C2** Research design | **Medium-high** | *"faultless execution"* is a judgement call and a real deviation exists; C2-2 moves it decisively but a marker could still read it either way |
| **C3** Novelty & significance | **Medium-high** | the campaign outcome. **Materially de-risked** — three contributions are now measured and outcome-independent |
| **C4** Communication | **High, conditional on starting now** | purely mechanical; the only genuine risk is R-5 |

**The largest single threat to the target is not scientific. It is that the write-up is compressed into
the final week — which would cap Criterion 4, the one criterion entirely within our control.**

---
---

# §12 THE SUPERVISOR RESEARCH PROGRAMME — RESEARCHED FIRST-HAND, 2026-07-31

> **Why this section exists.** Criterion-alignment is not sycophancy: the first marker's own research
> programme determines which arguments he finds *legible*, which claims he will *check*, and which
> objections he will *raise from expertise*. All facts below were retrieved first-hand from UCL
> profiles, the ACL Anthology and the ACM DL — not from memory.

## 12.1 Who the first marker actually is

| Fact | Source |
|---|---|
| **Dr** Ramin Okhrati (never "Prof") — BSc, MSc Mathematics, **PhD in Applied Probability** (actuarial/finance concentration) | UCL profile |
| **Head of AIRiskLab**, UCL Institute of Finance & Technology | UCL IFT |
| **Programme Director, MSc Banking and Digital Finance** — i.e. he owns the programme this dissertation is submitted to | UCL IFT |
| **Senior researcher collaborating with the Bank of England** | UCL IFT |
| AIRiskLab mission: *"an intellectual hub of innovative ideas and critical analysis of AI modelling in risk management"*, studying *"long- and medium-term impacts on financial stability and sustainability, based on a broad interpretation of risk in finance"* | UCL IFT |
| Lab's current projects include **offline reinforcement learning for pricing, sponsored by NatWest Group** | UCL IFT |

**Consequence of the Programme Director fact:** the IFTE0008 guidelines are, in a meaningful sense,
*his* programme's standard. **Non-conformance to the 16-section structure or the 10,000-word limit
reads worse from him than it would from an arbitrary marker.** This raises the priority of C4-1.

## 12.2 His three research lines — and our exact intersection with them

| Line | Anchor work | Our contact point |
|---|---|---|
| **1. Stochastic analysis & risk measures** (his PhD roots) | **Assa & Okhrati (2017)**, *Representation and approximation of convex dynamic risk measures with respect to strong-weak topologies*, *Stochastic Analysis and Applications*; local risk minimisation in Lévy and defaultable markets | our **theory chapter** — coherence, CVaR, the Artzner axioms, elicitability. **This is his mathematical home territory** |
| **2. RL for financial decisions on a fixed dataset** | **Khraishi & Okhrati (2022)**, *Offline Deep Reinforcement Learning for Dynamic Pricing of Consumer Credit*, **ICAIF '22**, arXiv:2203.03003 — **Conservative Q-Learning**, static dataset, no online interaction, +21% expected profit at <15% price change | our **simulated-online off-policy SAC on a historical-replay simulator** — the nearest methodological neighbour, and one he wrote |
| **3. LLM risk behaviour** (current, with the NatWest team) | **Hartley, Hamill, Seddon, Batra, Okhrati & Khraishi (2025)**, *How Personality Traits Shape LLM Risk-Taking Behaviour*, **Findings of ACL 2025**, pp. 21068–21092, arXiv:2503.04735 | our **manipulation is risk information fed to an LLM** — the direct successor question |

> **This dissertation sits at the intersection of all three of his active lines. That is currently
> nowhere stated in the paper, and it is the single strongest positioning move available.**

## 12.3 ★ THE HARTLEY ET AL. BRIDGE — the sharpest positioning move we have

**Verified findings of the ACL 2025 paper** (fetched first-hand from the ACL Anthology):

1. *"The majority of the models investigated are **risk-neutral rational agents**, whilst displaying
   higher Conscientiousness and Agreeableness traits, coupled with lower Neuroticism."*
2. *"Interventions on Big Five traits, particularly **Openness**, influence the risk-propensity of
   several LLMs… Openness emerges as the most influential factor to risk-propensity, **aligning with
   human baselines**."*
3. *"**Advanced models exhibited human-like cognitive bias patterns through targeted prompting, but
   their distilled variants showed no such bias**, indicating knowledge transfer limitations. **Less
   advanced models demonstrated inconsistent personality–risk relationships.**"*

### Three consequences, each a distinct upgrade

**(a) His paper's finding independently supports our A4 "prior dominance" account.** If an LLM's
revealed disposition is **risk-neutral**, then feeding it tail statistics asks a dispositionally
risk-neutral agent to author a risk-averse objective. Our registered null has empirical support in the
first marker's own paper — and we can say so without any circularity, because it was published before
our data existed.

**(b) The channel contrast is razor-sharp, and it is the natural next question.**

> *Hartley et al. (2025) establish that LLMs behave as risk-neutral rational agents whose
> risk-propensity responds to **personality** interventions. This dissertation asks the successor
> question: does it respond to **risk information** — and does any response reach the **objective the
> model writes** rather than the **choice it makes**?*

That single sentence positions the entire study inside his programme, and it is a genuine extension,
not a courtesy citation.

**(c) ★ Their finding 3 is a capability gradient — and it CONTRADICTS our registered prediction.**
Their result (advanced models show the pattern, distilled/weaker ones do not) supports the **capacity**
account. **Our pre-registered prediction (R87) is the *representational* account — responsiveness flat
at ≈0 across capability.** We registered a prediction that differs from the nearest prior result, in
the first marker's own paper, **before seeing our data**.

This is enormously valuable and must be foregrounded:
- it makes our prediction **non-trivial and falsifiable against a named prior**;
- if our gradient is flat, we have a result that *contrasts* with his paper and demands the explanation
  we have ready — **the channels differ**: theirs manipulates *disposition* via personality prompting,
  ours manipulates *information* via numeric feedback;
- if our gradient rises, we **corroborate and extend** his result to the objective-writing task.
- **Either outcome is a result.** Our measured authoring-reliability gradient (qwen3.5-9b ~17% ·
  qwen3.6-27b and gemini-2.5-flash 83% · deepseek 100%) is already consistent with their
  "less advanced models demonstrated inconsistent relationships."

**(d) A bridge that is genuine original interpretation (C1).** Their paper measures LLM risk behaviour
in the **descriptive/behavioural** frame (Cumulative Prospect Theory). Ours manipulates risk
information in the **normative/axiomatic** frame (coherent risk measures, CVaR, the Artzner axioms).
**Naming that bridge — behavioural risk preference meeting axiomatic risk measurement, through the LLM
as objective-designer — is original interpretation of exactly the kind Criterion 1's top band rewards.**

## 12.4 Raad is not an independent authority — the two feedback streams are one programme

**Raad Khraishi is a researcher in Okhrati's own AIRiskLab**, co-author on **both** anchor papers
(Khraishi & Okhrati 2022; Hartley et al. 2025), and the NatWest-sponsored offline-RL-for-pricing project
is **the lab's own project**.

**Consequences:**
1. Raad's six industry points are **the research programme's own methodological commitments**, not an
   external pragmatic overlay. Satisfying them *is* satisfying part of the first marker's expectations.
2. `CLAUDE.md`'s conflict-resolution rule (arbitrating between authorities #2 and #3) is **largely
   moot** — they are intellectually coupled. The only genuine tension is §12.6.
3. ★ **Recalibrate the publication claim to ICAIF.** His group publishes at **ICAIF** (Khraishi &
   Okhrati, ICAIF '22; the LLM-agents-for-investment-management paper at ICAIF '25). Claiming
   **ICAIF-main + TMLR** is calibrated to *his own venue*, which makes the Criterion-3 "publishable in
   a peer-reviewed venue" claim far more credible **to him specifically** than an unfamiliar target.

## 12.5 What he will be sceptical of — objections from his exact expertise

| # | Objection | Pre-written answer? |
|---|---|---|
| **A-11** ★ NEW | *"Your fed vector is a **static** risk measure; the control problem is **dynamic**. Where is time-consistency?"* — from **Assa & Okhrati (2017)** on convex **dynamic** risk measures. He will see this instantly | ❌ **NOT WRITTEN.** Answer: the fed vector is a **diagnostic summary supplied to a designer**, not a dynamic risk functional being optimised; the agent optimises the authored **per-step** reward, and time-consistency is a property we neither claim nor require. **Must be stated explicitly in the theory/methods** |
| **A-12** ★ NEW | *"How is this not offline RL?"* — **he wrote the CQL paper.** He knows precisely where the line sits | ⚠ exists in planning (harm-criterion + relabel→CQL bridge) but must be made **exact**, not hand-waved, in the methods |
| A-13 | *"CVaR at α=0.05 on a 60-day window is the mean of three observations — is that meaningful?"* | ✅ **now measured**: the `min_cvar` in→out-of-sample degradation dose–response (88% vs 4%). **This will land extremely well with a probabilist** |
| A-14 | The elicitability chain: ES not elicitable alone (Gneiting 2011); **(VaR, ES) jointly elicitable** (Fissler–Ziegel); **VaR fails subadditivity specifically** (Artzner et al.) | ✅ correct in the theory chapter — and **must stay correct**; a slip here is catastrophic with this marker |
| A-15 | *"Is SESOI = 0.05 DSR principled or fiat?"* | ⚠ drafted (registry row 19) — must land, because a fiat linchpin is exactly the fragility he'd probe |

## 12.6 ★ THE ONE GENUINE CONFLICT — depth versus breadth — and its resolution

**Okhrati's clearest stated instruction is *"do less, go more in depth."*** The rubric penalises
*"containing irrelevant material."* The exemplars carry 2–14 figures.

**Against that we hold:** 11 authoring models · a 35-model reading survey · 9 arms · 11 human rewards ·
9 allocators · 43 figure files · 274 bibliography entries · 43 write-time registry rows.

**This is the most uncomfortable finding in this analysis and it must be said plainly: our breadth is
in direct tension with the first marker's single clearest instruction, and it is a liability unless
subordinated.**

**Resolution (binding for the writing pass):**
- **The BODY carries the depth**: the mechanism, the four-noise-barrier account, the turnover finding,
  the estimation dose–response, the co-primary verdicts. Roughly ten figures.
- **The BREADTH is compressed into tables and appendices**: the 10 replication legs, the 35-model
  survey, the leg-by-leg contrasts, the cross-model synthesis. Present as *evidence of generality*, in
  a small number of dense, word-excluded artefacts — never as body prose.
- **State the subordination explicitly** in one sentence: the breadth layer exists to test whether the
  mechanism findings generalise; it gates nothing.

This resolves Raad's breadth push against Okhrati's depth instruction **in the document's layout**
rather than in the science.

## 12.7 NEW ACTIONS — E-series (added to the §5 register)

| # | Action | Criterion | State |
|---|---|---|---|
| **E-1** | **The programme-positioning paragraph** (CH1 + CH2): this study sits at the intersection of coherent risk measures, RL on fixed financial datasets, and LLM risk behaviour — with the Hartley et al. successor-question sentence (§12.3b) | C1, C3 | **[N]** |
| **E-2** | **The CPT ↔ coherent-risk bridge** (CH2 or CH7): behavioural risk preference meets axiomatic risk measurement through the LLM-as-designer | C1 *original interpretation* | **[N]** |
| **E-3** | ★ **Foreground the registered-prediction contrast** — our representational-account prediction (R87) differs from Hartley et al.'s capacity-account finding, registered before our data. Explain the channel difference (disposition vs information) | C2 *unquestionable originality*, C3 | **[N]** |
| **E-4** | **Pre-write A-11 (time-consistency)** into the theory/methods | C2 *faultless* | **[N]** |
| **E-5** | **Sharpen A-12 (offline-RL demarcation)** to exact, not hand-waved | C2 | **[F]** |
| **E-6** | **Recalibrate the publication target to ICAIF-main + TMLR**, and say so | C3 | **[F]** |
| **E-7** | **Re-spine the wider-context section on systemic risk in AIRiskLab's own terms** — automated objective design deployed at scale, with a silently failing numeric interface, means institutions run agents whose objectives were never actually shaped by the risk information their designers believed they supplied. **Unverifiable objectives as a financial-stability concern** (he collaborates with the Bank of England) | C1 **wider context** | **[N]** |
| **E-8** | ★ **Execute the §12.6 depth/breadth subordination** across the whole document | C1 *depth*, C4 *irrelevant material* | **[N]** |
| **E-9** | **Verify and lock the exact citations** (§12.8); never misattribute | C1, C2 | **[X]** |

## 12.8 THE EXACT CITATIONS — verified first-hand 2026-07-31, use these forms

- **Khraishi, R. and Okhrati, R. (2022)** 'Offline Deep Reinforcement Learning for Dynamic Pricing of
  Consumer Credit', in *Proceedings of the Third ACM International Conference on AI in Finance
  (ICAIF '22)*. arXiv:2203.03003. doi:10.1145/3533271.3561682.
- **Hartley, J., Hamill, C.B., Seddon, D., Batra, D., Okhrati, R. and Khraishi, R. (2025)** 'How
  Personality Traits Shape LLM Risk-Taking Behaviour', in *Findings of the Association for
  Computational Linguistics: ACL 2025*, Vienna, pp. 21068–21092. arXiv:2503.04735.
- **Assa, H. and Okhrati, R. (2017)** 'Representation and approximation of convex dynamic risk measures
  with respect to strong-weak topologies', *Stochastic Analysis and Applications*.
- **Batra, D., Hamill, C., Hartley, J., Okhrati, R., Seddon, D., Miller, H., Khraishi, R. and Cowan, G.
  (2025)** 'A Review of LLM Agent Applications in Finance and Banking'. SSRN 5381584.

⚠ **Standing prohibition retained:** never attribute CVaR-elicitability, *Deep Hedging across Risk
Aversions*, *Hedging Beyond the Mean*, or Capiński to him. He co-authored two of the papers in our
corpus — a bad citation gets caught.

---

# §13 THE DEEP SYNTHESIS OF ALL SUPERVISOR FEEDBACK

Four streams — Dr Okhrati's revealed grading function, his 2026-07-31 live feedback, Stefan's five
criteria, Raad's six points. Stripped of vocabulary, they converge on four invariants.

| Invariant | Okhrati (grading fn) | Okhrati (07-31) | Stefan | Raad |
|---|---|---|---|---|
| **1. The explanation is the deliverable, not the number** | intuition > technical correctness | *"you get the output, and you can explain the output that you got, and why it happened"* | clarity of what is measured | the story; success metrics |
| **2. No fragile link, and rigour must be VISIBLE** | docks missing compute, untidy cross-refs | *"the experimental setup must be very rigorous"* | principled, elegant, **non-fragile**; everything justified | **"amazing reproducibility"** — the critical point |
| **3. Honesty is an asset, not a cost** | mature non-overselling = his 5/5 | comprehensive understanding of what happened | actively hunt fragility | good vs bad approaches |
| **4. Depth over breadth** | *"do less, go more in depth"* | why this or that happened | the arms must each earn their place | *(pulls the other way — §12.6)* |

**The one sentence:**

> **Every supervisor is asking for the same thing in different vocabularies: a small number of claims,
> each explained mechanistically, each with visible evidence, each honestly bounded — and the breadth
> exists only to make those claims general, never to be the claims.**

**What follows operationally:**
1. **Invariant 1** is already binding as duties D1–D6 in `CLAUDE.md` and rows 38–41 of the registry.
2. **Invariant 2** means every rigour claim must land as a *scannable artefact*, because rigour buried
   in a 6,700-line execution record earns nothing (C2-2, C2-3, C4-3).
3. **Invariant 3** means the disclosed deviation, the ten losing baselines and *"ties the index, loses
   to equal weight"* are **assets** — provided they are framed as discipline (C2-2, A-7, A-10).
4. **Invariant 4** is the only conflict, and §12.6 resolves it **in the document's layout**, not in the
   science.

---
---

# §14 NOVELTY — A STRICT, ADVERSARIAL ASSESSMENT (2026-07-31)

> **Method.** This section was written by trying to **break** our novelty claim, not to confirm it.
> Six targeted searches were run against the 2025–2026 literature on LLM reward design, risk-sensitive
> portfolio RL, distributional reward feedback, and pre-registration in this lineage. Two candidate
> neighbours were fetched and read. Findings below are stated against us wherever they run that way.

## 14.1 ⚠ THE SWEEP MISSED A NEIGHBOUR — and it is the closest structural one

**RDA — "Reward Design Agent for Reinforcement Learning"** (Lee, Subramanian, Abbatematteo et al.,
**arXiv:2606.01672, June 2026**). Verified first-hand:

- an LLM (**GPT-5**) **generates executable reward code**;
- the agent is **Soft Actor-Critic** — *the same algorithm family we hold fixed*;
- feedback is **multi-modal**: a VLM performs visual trajectory analysis producing subtask-wise scores
  and evaluation rationales, **supplemented by numerical reward statistics**;
- domain: **robotics only** (ManiSkill, HumanoidBench). **Not risk-sensitive. Not finance. Not
  pre-registered.**
- **Their stated contribution:** unlike Eureka, RDA *"injects semantic understanding into reward design"*
  rather than *"relying solely on coarse numerical metrics."*

**Why this matters, stated honestly: RDA's argument has the same shape as ours.** *The feedback channel
in Eureka-style loops is impoverished; enrich it.* They enrich along the **semantic/visual** axis; we
enrich along the **distributional/tail** axis.

**Consequences — two, and they run in opposite directions:**
1. **It strengthens our framing.** An independent group at the frontier of this lineage reached the same
   diagnosis — *the channel, not the method, is the bottleneck* — which corroborates that we are
   manipulating the right variable. That is a citable external endorsement of our premise.
2. **It narrows our novelty claim, and we must narrow it ourselves before a referee does.** We can no
   longer claim novelty for *"enriching the feedback channel"* as an idea. **Our novelty is the specific
   axis (a multi-quantile realised-return lower-tail profile), the controlled test of whether it works,
   and the pre-registration — not the idea of enrichment.**

**⚠ PROCESS FINDING.** Our 2026-07-30 novelty sweep found **GIFT** (finance) but **missed RDA**
(robotics, June 2026) — because the sweep was **finance-weighted**. RDA is not a finance paper, but it
is structurally the closest work to our core argument. **The sweep's scope is a defect: it must cover
the reward-design lineage on arXiv *by date*, not only the finance neighbours.** Fix before the
mandatory pre-submission sweep (~20 Aug).

## 14.2 Other 2025–26 works that must enter the matrix

| Work | What it is | Does it close our cell? |
|---|---|---|
| **RDA** (arXiv:2606.01672, Jun 2026) | LLM writes reward code; VLM visual+semantic feedback; SAC; robotics | **No** — different axis, no risk-sensitivity, no finance, no pre-registration. **But it must be cited and distinguished** (§14.1) |
| **LEARN-Opt** | fully autonomous, model-agnostic reward-function generation; derives its own metrics; multi-run evolutionary search; continuous control / robotics | **No.** ★ **But quote its finding:** *"automated reward design is a high-variance problem, where the average-case candidate fails, requiring a multi-run approach"* — **direct external corroboration of our search-variance limitation (B.2.6) and of why the candidate budget and seed ladder are necessary** |
| **RF-Agent** (arXiv:2602.23876) | reward design via Language Agent Tree Search | No — robotics/control |
| **URDP — Uncertainty-aware Reward Design Process** (arXiv:2507.02256) | LLM reward logic + Bayesian optimisation; self-consistency uncertainty; 35 tasks, 3 benchmark envs | No — verified first-hand: no risk-sensitivity, no finance, no pre-registration. *(Previously assessed and rejected as a neighbour; the assessment holds)* |
| **QRM — Quantile Regression for Distributional Reward Models in RLHF** (arXiv:2409.10164) | reward **model** outputs a distribution over rewards; used downstream for risk-aware RL | **No, and the distinction is sharp:** their distribution is the reward model's **output**; our distribution is the **input to a reward author**. Adjacent enough that a referee may raise it — **cite and distinguish in one sentence** |
| **CVaR-PPO / risk-sensitive portfolio RL** (multiple, incl. MDPI 2026) | fixed hand-written CVaR objectives | No — the objective is not authored by an LLM |

## 14.3 ★ THE HONEST VERDICT — where the novelty actually lives

**Our topical novelty is real but fragile. Our methodological novelty is durable. We have been leading
with the fragile one.**

### Tier 1 — DURABLE (survives even if someone publishes our exact topic next month)

| # | Claim | Why it is durable | Evidence |
|---|---|---|---|
| **N-1** | **No pre-registration anywhere in the automated-reward-design lineage.** | A claim about a **practice**, not a paper. Verifiable in an afternoon; **cannot be defeated by naming an adjacent study.** An adversarial search for pre-registered/registered-report work in this lineage returned **nothing** — only a general ML methods paper (arXiv:2311.18807) unrelated to reward design | frozen hash `3ca6f01a…`, tag `prereg-v2.1`, DOI deposit pending |
| **N-2** ★ | **The placebo-controlled identification design.** Only the fed block varies, against a **length-matched neutral placebo**, a **deranged-content placebo**, and a **dose-intermediate** control | **Nobody in this lineage runs controls.** Eureka, Text2Reward, REvolve, CARD, LEARN-Opt, RDA, RF-Agent all compare **methods**; none isolates **feedback content under a fixed method**. This is arguably **more novel than our topic**, and it is currently framed as a design detail rather than a contribution | the 9-arm roster; construct validity verified over all 643 prompts |
| **N-3** | **The mechanism decomposition with positive controls.** SQ1/SQ2/SQ3, five rival accounts with distinct predicted fingerprints, and an instrument-sensitivity control | Nobody instruments **why** reward design works or fails. The positive control — stimuli where the metric *must* fire — is what makes a null falsifiable rather than dismissible | built and wired |
| **N-4** | **The measured results themselves** — the turnover/argmax mechanism, the estimation dose–response, the four-noise-barrier account | Results, not designs. They cannot be scooped by a design | measured 2026-07-31 |
| **N-5** | **The systematic open-weight replication suite** (6 of 11 authors open since Kimi K3, 27 Jul) | the 15/15 survey established the lineage uses closed primaries | hedged pending the final sweep |

### Tier 2 — REAL BUT DISPUTABLE

| # | Claim | The honest caveat |
|---|---|---|
| **N-6** | The **conjunctive cell** — LLM-authored reward *code* + multi-level tail feedback as the *manipulated variable* + fixed agent + risk-sensitive portfolio RL | Empty today; every neighbour fails ≥1 column **structurally**. But it is *disputable by construction* — a referee can always name an adjacent paper — and the field is **crowding fast** (RDA and GIFT both landed in 2026). Relying on this alone would be fragile |

### Tier 3 — NOT NOVEL, and we must never imply otherwise

| Claim | Who already owns it |
|---|---|
| "An LLM can write reward code" | Eureka (ICLR 2024) — and by now Text2Reward, REvolve, CARD, DLM, LEARN-Opt, RF-Agent, URDP, **RDA** |
| "Risk-sensitive RL for portfolios using CVaR" | an extensive literature (Coache & Jaimungal; CVaR-PPO; MDPI 2026) |
| "LLMs combined with financial RL" | FinRL-DeepSeek, GIFT, ELfolio, FINCON |
| **"Enriching the feedback channel beyond scalars"** | ★ **RDA (June 2026) now independently holds this** — see §14.1 |

## 14.4 What this changes — four actions

| # | Action | Criterion |
|---|---|---|
| **N-A1** ★ | **Reorder the contribution hierarchy by DURABILITY, not by topical appeal:** (1) pre-registration absent from the practice · (2) the placebo-controlled identification design · (3) the mechanism decomposition with positive controls · (4) the measured findings · (5) *then* the conjunctive cell. The rubric asks for **"unquestionable"** originality — lead with the claims that cannot be argued with | C2, C3 |
| **N-A2** ★ | **Promote the identification design (N-2) to a named, numbered contribution.** It is currently buried as methodology. *"No prior work in this lineage runs a placebo"* is a stronger, more checkable sentence than *"the cell is empty"* | C3 |
| **N-A3** | **Add RDA, LEARN-Opt, RF-Agent and QRM to T10**, each with a cite-and-distinguish sentence. **Quote LEARN-Opt's high-variance finding** as external corroboration of our search-variance limitation | C1, C2 |
| **N-A4** | **Fix the sweep scope** — cover the reward-design lineage on arXiv **by date**, not only finance neighbours, before the mandatory pre-submission sweep | process |

## 14.5 The one-paragraph answer to *"how novel is this?"*

> **The topic is in a crowding field; the method is not.** That an LLM can author reward code is
> established (Eureka, 2024) and now busy — RDA reached the same diagnosis we did in June 2026, that
> the feedback channel rather than the search method is the bottleneck, and enriched it along a
> semantic axis. What no one in this lineage has done is **run a control**: every published system
> compares *methods*, none isolates *feedback content under a fixed agent* against a length-matched
> placebo and a deranged-content placebo. And no one has **pre-registered** — an adversarial search of
> the lineage returns nothing. So the durable contribution is not *"we fed a model tail statistics"*;
> it is **a pre-registered, placebo-controlled, mechanism-instrumented protocol for deciding whether a
> feedback channel carries usable information at all — applied to the tail-risk channel, and delivering
> a bankable verdict of either sign.** That claim survives being scooped on the topic, because a
> scooping paper would arrive without the pre-registration, without the placebos, and without the
> mechanism instrumentation.
