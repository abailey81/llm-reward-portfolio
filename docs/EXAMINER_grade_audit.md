# EXAMINER_grade_audit — a strict assessment against a 90–100% bar

**Role.** Hostile, expert MSc examiner (LLM-for-RL + stochastic-control/quant-finance; the marker co-authored
backtest-statistics and RL-finance papers in this project's own corpus). **Grade frame:** UK MSc Distinction
is 70+; this audit asks what stands between the present state and **90–100% (exceptional / publishable-quality)**.
**Mode:** read-only on code/config/prereg; grounded first-hand in `PREREGISTRATION.md` (incl. amendments
R11–R31), `00_planning/LIMITATIONS_REGISTER.md` (L1–L19), the `docs/DEEP_*.md` scrutiny set, the
`00_planning` theory-spine + alignment docs, and a first-hand wiring check of `scripts/analyze_campaign.py`,
`src/inference/`, `src/search/`, `config/`. **Date:** 2026-06-25. **Not dissertation prose.**

> **One-line verdict.** The *science, inference, and self-disclosure are already at the 90–100% conception
> bar* — and unusually, the deep-scrutiny recommendations (R25 two co-primary IUTs, R30 H3/H4 sealed-leg
> tests, R31 cross-hypothesis stance, R26 factor attribution, R27 honest-EVT) are **wired in code, not just
> promised in prose** (verified below). The gap to 90–100% is therefore **almost entirely the artefact that
> does not yet exist: the written dissertation and its figures**, plus **two small pre-freeze integrity
> closures** (pre-register the attribution family in the YAML; decide the `placebo_shuffled` arm). For a
> no-viva, PDF-only grade, **the write-up quality IS the remaining 20 marks.** This is good news: the highest
> grade-ROI work is the work the user controls completely and that no campaign outcome can take away.

---

## 0. Calibration — what "90–100%" demands that "70%" does not

A UK MSc Distinction (70+) is *faultless execution of appropriate methods on a real question*. The
**90–100% band is reserved for work an examiner would call publishable in a strong venue without
condescension** — i.e. all of the following simultaneously:

1. a contribution that is **not just novel but clearly *significant*** — it changes how a competent reader
   thinks about the problem, and the significance is *argued*, not asserted;
2. methodology that is **not just correct but exemplary and self-aware** — the author anticipates the
   expert's objections and has already answered them in the design;
3. a results plan that is **compelling under *every* outcome branch**, with the negative branches as
   carefully built as the positive one;
4. **publishable-grade reproducibility/open-science** (freeze hash, seeds, provenance, archive, synthetic
   data, a pre-registration a third party could audit);
5. **communication that is itself a contribution** — the prose, figures, and structure make a hard idea
   feel inevitable to a second marker *from another discipline*.

Against that bar: this project scores **exceptional on (1)–(4) at the design/plan level** and is currently
**unscored on (5)** because the document does not exist. The audit's job is to be precise about the residual
on (1)–(4) and brutally honest that (5) is the dominant lever.

---

## 1. Contribution — is it 90–100%-significant, or "a competent study"?

**Verdict: genuinely novel and, with the feedback-channel framing, *significant* — but the significance is
currently load-bearing on framing discipline the document has not yet executed.**

### What is strong (and rare at MSc)
- **The empty-cell is real and defensible.** The novelty claim is not "distributional RL on portfolios"
  (Coache–Jaimungal own that) but *an LLM designing reward **code** that is fed the realized-return
  **distribution** as the reflection signal* — the (who-designs-the-objective × what-signal × domain) cell
  is empty in the corpus (`LITERATURE_AND_DEFENSE_COMPANION`; `DEEP_H2` §9). That is a publishable framing.
- **The feedback-channel framing is the project's single best idea and it is compelling.** Holding the agent
  fixed (SB3-SAC) and measuring the tail **off-critic** turns a vague "distributional RL is good" into a
  *clean instrument*: the only thing that varies is what the designer is shown. `DEEP_H2` §1.2 is right to
  call this "a genuinely clean instrument" — it is the methodological core that lifts the work above a
  competent application study.
- **The theory spine is PhD-grade and is the strongest single significance lever you are under-using.**
  `H2_THEORY_SPINE_2026-06-21.md` proves: Sharpe is a *deterministic Blackwell garbling* of the
  distribution (weak dominance for every objective, Blackwell–Sherman–Stein); the CVaR profile is a
  *sufficient coordinate basis* for the law-invariant coherent-risk class (Kusuoka/Acerbi) while Sharpe is a
  strictly lossy, *non-coherent* projection; the tail is *provably off-critic* (Rowland, Bellman
  non-closedness); the risk objective is *not Markov-reward-expressible* (Skalse–Abate Thm 2 / Cor 6–9), so
  the distribution **must** enter via the feedback channel; and the whole enterprise is licensed only
  because the agent is **bounded** (Sorg–Singh–Lewis). With a fully-worked toy proof. **This converts the
  paper from "we tried feeding more info and measured it" to "we predict, from first principles, an upper
  envelope and a mechanism, then test whether a real LLM attains it."** That is the difference between
  competent and exceptional — *if the write-up foregrounds it as the spine and not an appendix*.

### What would make it *more* significant (the gap to a clear 90+)
- **The "so what for the field" sentence is not yet sharp.** The contribution is currently framed inward
  (a clean comparison). The 90+ framing is outward: *"we give the first theory-grounded, pre-registered
  test of whether an LLM reward-designer is a Bayes-responsive user of risk information — a question that
  generalizes far beyond portfolios (it is the Gupta–Hartford 'do LLM optimizers use feedback content'
  question, instantiated where the answer is checkable against decision theory)."* The system red-team
  reaches exactly this (`DEEP_SYSTEM_redteam` §7). **Action: write the contribution as a claim about
  LLM-optimizer responsiveness, theory-anchored, with portfolios as the testbed — not as a portfolio
  result.** That single reframing is worth real marks because it makes a null *interesting to a general
  reader*, not just to a quant.
- **The strongest defensible thesis claim is already written** (`DEEP_SYSTEM_redteam` §7) — it is bankable
  regardless of campaign outcome. It is currently buried in a scrutiny doc. **It belongs in the abstract.**

**Grade-ROI on contribution: LOW remaining effort, HIGH payoff.** The intellectual contribution is already
at the bar; the lever is *positioning prose*, covered in §5/§6.

---

## 2. Methodology rigor — exemplary; the residual dings

**Verdict: this is the project's strongest dimension and is already at the 90–100% level. The deep audits
found real issues and *they have been fixed in code*, which is itself the rigor signal an examiner rewards.**

First-hand wiring confirmation (the part that matters — prose-claims vs code-reality):

| Pre-reg claim (R-id) | Status in code (verified `scripts/analyze_campaign.py` + `src/`) |
|---|---|
| **R25** H2 = two co-primary IUTs (H2-RA Sharpe, H2-Tail CVaR-5%), one-sided α=0.05, BH-over-6 demoted to sensitivity | **WIRED.** `_one_sided` `p_one=p/2` + per-family `_iut_supported`; partition assert in code **and** `freeze.py`; `config/preregistration.yaml: structure: two_co_primary_iut`. |
| **R26** factor attribution (CAPM→FF6+BAB/QMJ, Newey-West HAC, diff-in-α, paired) | **WIRED in code** (`src/inference/attribution.py`, called → `out["attribution"]`) **but NOT declared as a family in `config/preregistration.yaml`** — the one real residual (see §6, the BAB gap). |
| **R27** EVT = plain GPD MLE, Troop(2021) = future work | **WIRED, honest.** `genpareto.fit` MLE; `EVT_ESTIMATOR_NOTE` documents Troop as future work; no bias-corrected estimator shipped (so no docstring-over-code mismatch — the `DEEP_H2` §6.2 [S1] flag is closed). |
| **R28** H4a widened to the shared six-term reward family | **WIRED.** `random_search.py` samples the six-primitive family via `params_to_source`. |
| **R29** H4b = sklearn GP-EI (Matérn-2.5), not Optuna-TPE | **WIRED.** GP+EI present; `bayesopt_tpe` label removed; **Optuna is not a dependency** (grep-clean). |
| **R30** H3/H4 sealed-leg tests + TOST + DSR-eff-N | **WIRED.** `out["h3"]`, `out["h4"]`, `out["h2_tost"]`, `out["dsr_effective_n"]`, `out["evt_consistency"]`, `out["benchmark_floor"]`; `run_h3_singleshot` + `--h3-singleshot`. |
| **R31** cross-hypothesis Bonferroni-across-4 sensitivity | **WIRED.** `out["cross_hypothesis_multiplicity"]`, report-only. |
| `freeze.py` checks prose↔YAML and emits a SHA-256 | **PRESENT**, R25-aware partition check; `frozen: false` (correctly, pre-freeze). |

This closes the **asymmetric-rigor** wound (G1/S2 in `DEEP_SYSTEM_redteam`: H3/H4 were numbered but untested)
and the **conjunction×BH double-correction** ([S1] in `DEEP_STATS`/`DEEP_H2`). An examiner who reads the code
finds the documented fixes *actually performed* — that is the single most credibility-positive thing a
careful marker can find, and most MSc (and many published) projects fail it.

### The residual methodology dings a hard marker still raises (none fatal; all closable in prose)
1. **The `placebo` is still the inert `+0.000`×6 block; `placebo_shuffled` is unbuilt** (verified: only in
   docs, not in `config/arms.yaml`). `placebo_shuffled` is **pre-registered (R32/R38) and runs in the
   CAMPAIGN; it is absent from the prototype, which predates R32** — so it has produced **no results yet**
   and "closes the format-vs-content threat" only as a *pre-committed plan*, not an executed fact. The inert
   placebo controls *token count* but **not structure** — it
   cannot distinguish "the LLM used the numbers" from "the LLM responded to a plausible-looking table." This
   is the **Gupta–Hartford–Liu (2025) existential threat** (`DEEP_SYSTEM_redteam` G3/S4): if LLM optimizers
   are insensitive to feedback *content*, the H2 gap is a prompt-*format* artefact and the shuffled-label
   arm is *the only experiment that identifies against it*. **This is the highest-value remaining
   methodological lever** (§6).
2. **The factor-attribution family is wired but un-pre-registered** (R26 residual). For a vol-lowering
   long-only agent the BAB/low-vol recast ("your edge is a known priced tilt, not RL skill") is the single
   attack that can reframe the *entire* headline. The defence (the contrast is common-mode; report
   difference-in-α) is strong **only if pre-committed**. Code exists; the freeze-mirror does not name it.
3. **Power analysis σ is still a placeholder (0.300)** and the MDE table is computed on a *mean*-based test
   while the headline runs the IQM paired bootstrap (`POWER_ANALYSIS.md`; `DEEP_H2` §5.2 [S2]). The doc
   itself flags this. A 90+ marker wants the MDE of *the test you actually run*, at the *pilot* σ. Mechanical
   once the pilot lands.
4. **A cluster of stated-judgement-calls** the stats backbone enumerates (`DEEP_STATS` C1/C3/C5/C6): the
   effective DSR trial count under guided search (report N and N_eff, note the benign direction for the
   floor/H1 gates); PBO ranks on *mean-return* while selection used *DSR* (state the proxy, ideally add a
   DSR-ranked robustness PBO); the BH leg consumes two-sided p + post-hoc sign while Romano–Wolf is
   one-sided (unify or document). **None is a code bug; all are one-paragraph disclosures.** A 90+ examiner
   does not penalise a stated judgement call — they penalise a *silent* one.

**Grade-ROI on methodology: the design is done. The residual is (a) one frozen arm [P0], (b) one YAML
declaration [P0], (c) a handful of disclosure paragraphs that belong in the write-up anyway.**

---

## 3. Results plan — compelling under *every* outcome?

**Verdict: yes — the bankability matrix (`DEEP_SYSTEM_redteam` §5) is genuine, and the two-tier H2 (R25) is
exactly the structure that makes the most-likely outcome a *positive* finding rather than a null. This is
already at the 90+ bar. One outcome branch needs a sharper pre-built narrative.**

- **The R25 two co-primary split is the decisive results-plan move.** Before R25, the headline gated on the
  *Sharpe* leg — the dimension the distributional channel helps **least** (the selection is λ=0, tail-blind),
  with the tail (where it helps most, prototype CVaR p≈0.004 — *1-seed prototype, DIRECTIONAL; does not
  enter the inferential result, and in fact REVERSES under the zero-info placebo: the distributional tail is
  significantly WORSE than placebo, `distributional_vs_placebo` p=0.0005, responsiveness −0.053 ⇒ a directional
  null, not a win*) relegated to a non-gating secondary. R25 elevates **CVaR-5% to
  co-primary**, so the *structure* that would let the campaign bank such a tail signal as a primary result
  is now in place (the prototype number itself remains a placebo-reversed directional null and is not evidence
  of the campaign outcome). The most likely empirical outcome — "tail improved at parity of risk-adjusted mean" — is now a
  **publishable positive**, not a Sharpe-gate null. This is the single best results-plan decision in the
  project and it is wired.
- **The pre-registered null is genuinely bankable.** The verbatim null statement (`PREREGISTRATION` §10,
  R25) names the estimand, carries a TOST equivalence bound (±0.05), is hash-frozen, scopes to the
  operationalisation, and ties the common-mode-confound argument to the comparative claim. A null here reads
  as *a calibrated ceiling on the channel*, which the marking criteria explicitly reward. The five
  **principled-null conditions** (`H2_THEORY_SPINE` §5 — tail-indifferent objective / unbounded agent /
  optimizer-ignores-info / unmeasurable-at-n / acceleration-erased-by-matched-compute) make a null
  *mechanistic and informative*. This is the rare project where the null is not a fallback but a designed,
  theory-backed outcome.
- **Every cell of the H2×H1×H4 matrix is a Distinction story (A–E)**, and the only non-Distinction route
  (F) is self-inflicted over-claiming. That is the correct state.

### The one results branch still thin
- **"Only H2-RA rejects, or the all-positive A-cell" risks an over-claim trap.** The discipline that the
  abstract must never claim a *tail/market* win off the Sharpe gate alone is documented
  (`DEEP_FRAMING_discipline` §1; `DEEP_BENCH_T4` no-SOTA discipline incl. the **negative-prototype-Sharpe
  display landmine** — arms may land *below* the FinRL ribbon; do not plot them under a "SOTA" line). The
  results *plan* is right; the *exhibits that enforce it do not exist yet* (no results-figure generator —
  §4). The risk is that under time pressure a naive cumulative-returns plot ships without the framing.
  **Action: build the figure generators *with the framing baked in* (conditional band, undeflated-DSR
  column, per-benchmark cost table) before results land, not after.**

**Grade-ROI on results plan: the plan is exemplary and wired. The residual is figure *production* (§4), not
plan design.**

---

## 4. Reproducibility / open-science — publishable-grade, with two gaps to a top mark

**Verdict: the *machinery* is publishable-grade; two artefacts are missing for the full open-science mark.**

Present and strong: the **freeze-hash** (`freeze.py`, SHA-256 over prose + YAML + bound configs, with a
`--check` drift guard); **replay-not-regenerate** with archived prompts/rewards (content-addressed) /
feedback / token usage (L9); **pinned immutable model snapshots**; **synthetic panel of identical shape** to
ship alongside SHA-256-checksummed gold (licensed Refinitiv, non-redistributable); **PBO full enumeration**
(12,870 splits → deterministic, not seed-dependent — a real reproducibility win); a **machine-readable
pre-registration mirror** that `freeze.py` enforces against the prose. This is better than most published
quant-ML.

**The two gaps to a top open-science mark:**
1. **The freeze has not been executed** (`config/preregistration.yaml: frozen: false`). The entire
   pre-registration value — "we fixed this *before* the sealed test leg" — is only bankable *once the hash
   is emitted and recorded in `DECISION_LOG` with a date*. This is the **single most time-sensitive item in
   the whole project**: every day unfrozen is a day the "pre-registered" claim weakens. It must happen
   before any sealed-test number is computed. (Pending only the user's ratification of the PROPOSED λ=0
   amendment, the R24 reflect-protocol record, and the two §6 P0 closures.)
2. **No public artefact plan / DOI / archive snapshot.** For *publishable* open-science the examiner expects
   a statement of where the frozen artefact, synthetic data, and replay archive will live (an OSF/Zenodo DOI
   for the pre-registration + a code archive). Currently implicit. **Action: a one-paragraph "Reproducibility
   & artefact availability" statement** naming the freeze hash, the synthetic-panel path, the replay
   protocol, and an archival DOI plan. Cheap; expected at 90+.

**Grade-ROI: freeze NOW (highest urgency, low effort); add the artefact-availability statement (low effort).**

---

## 5. Write-up readiness — the dominant lever, and the scaffold the document needs

**Verdict: the *intellectual* scaffold is exceptionally rich; the *document-production* scaffold barely
exists. For a no-viva grade, this is where 90–100% is won or lost, and it is ~80% unbuilt.**

### What exists (and is a genuine head-start most students never have)
- A **word-budgeted, guideline-compliant chapter plan** (FINAL_PLAN Part J: 7 chapters → the UCL 16-section
  structure, 10,000 words with maths/tables/figures/appendices excluded; `DISSERTATION_ALIGNMENT` maps the
  ≈60%-core requirement). Strategically optimal (formalism pushed into non-counting maths blocks).
- A **critical literature synthesis**, not a catalogue (`LITERATURE_AND_DEFENSE_COMPANION`: 6 families +
  3 deep pillars + the empty-cell argument + a paper→design-decision map). This is the strongest single raw
  material for the Lit Review and Methodology and is largely *write-up-ready*.
- A **PhD-grade theory chapter waiting to be transcribed** (`H2_THEORY_SPINE` — exact theorem statements,
  the worked toy proof, the rigorous/hand-wavy ledger, the one-paragraph spine for the abstract).
- A **19-entry limitations register** (`LIMITATIONS_REGISTER` L1–L19) where **each entry already contains a
  prose-ready Discussion paragraph** — the Limitations chapter is effectively pre-drafted (this is, per the
  no-viva strategy, one of the two highest-weighted controllable levers, and it is *done*).
- The **results-table generators** (`analyze_campaign.py` emits markdown tables for H1–H4, the benchmark
  floor, PBO/DSR, attribution, cross-hypothesis) — the tables fill mechanically from the campaign.
- **EDA figures already produced** (`reports/figures/eda_*.png`).

### What is MISSING (the document-production gap — every item below is a 90+ requirement)
| # | Missing artefact | Why it gates a top mark |
|---|---|---|
| 1 | **The thesis document itself** (no `.tex`/`.docx` skeleton; `paper/` holds only `refs.bib`) | There is nothing to grade yet; communication is 1 of 4 equally-weighted criteria. |
| 2 | **The one-page system diagram** (no mermaid/tikz/drawio/png source *anywhere*) | Flagged *mandatory* (D-2) for the any-discipline second marker; the single highest-leverage communication artefact for a hard idea. |
| 3 | **Results figures** (no generator for cumulative-returns / learning curves / **ablation bar** — `analyze_campaign.py` is table-only, no `savefig`) | "Faultless presentation of data" is the 90+ communication descriptor; the ablation figure *is* the contribution visual. Must embed the no-SOTA / negative-Sharpe framing. |
| 4 | **A self-contained abstract** (only a 1-sentence contribution + the theory-spine paragraph exist) | The abstract is the most-read, most-weighted paragraph; a second marker forms the grade here. |
| 5 | **Front matter** (Moodle cover page, title page exact wording, ToC, List of Figures, List of Tables) | Binding format requirements; trivially gradeable; their absence reads as carelessness. |
| 6 | **`refs.bib` is a ~40-entry core, not the ~90 the lit synthesis needs**; many `% VERIFY` flags unresolved | Citation integrity is *the* avoidable mark-loss with a co-author supervisor (see §6); ~6 prereg-named refs are on disk but unpromoted. |
| 7 | **The plain-language contribution paragraph + the worked feedback-block micro-example** (D-2) | Specified, not written; the two devices that make the idea legible to a non-specialist marker. |

### The scaffold that would make an exceptional write-up easy (recommended build order, all NOW — none blocked on the campaign)
1. **The thesis skeleton** (LaTeX strongly preferred: Arial/Helvetica ≥10pt, 1.5 spacing, the 16-section
   front matter, the 7 chapters as empty sections with the Part-J word budgets as comments, `refs.bib`
   wired). One afternoon; unblocks all prose.
2. **The system diagram** — one page: data → env(fixed SAC) → reward-slot ← LLM-designer ← feedback block
   (the *only* arm-varying element, with the off-critic measurement called out) → fitness(val-DSR, λ=0) →
   winner → sealed test → inference. This diagram *is* the methods chapter's anchor and the second-marker's
   mental model.
3. **A `make_figures.py`** producing the four results exhibits with the framing pre-baked: (a) the
   **ablation bar** (the seven arms on the headline metric with rliable CIs — the contribution visual);
   (b) **cumulative returns** with the *conditional* FinRL band (omit if arms < ~0.85) and the DeMiguel-1/N
   framing; (c) **learning curves**; (d) the **per-benchmark turnover/cost table** + the **undeflated-DSR
   column** (the two `DEEP_BENCH_T0` fairness exhibits). Build the shells against the prototype/synthetic so
   the campaign fills them mechanically.
4. **Transcribe, don't re-derive:** the theory chapter from `H2_THEORY_SPINE`; the Limitations chapter from
   `LIMITATIONS_REGISTER` (lightly edited); the framing rules from `DEEP_FRAMING_discipline` (construct
   retitle "distribution"→**"multi-level tail-risk feedback"**; the struck/safe phrase lists). These are the
   sections most students agonise over and here they are *already written as scaffolds*.
5. **Finish `refs.bib`** to ~90, resolve every `% VERIFY`, and apply the citation-integrity fixes
   (Refinitiv-not-CRSP everywhere; FZ0→Patton-Ziegel-Chen 2019 where appropriate; Skalse-**Abate UAI 2023**;
   the author-list flags). With a co-author marker this is non-negotiable for 90+.

**Bottom line on §5: the user is *set up* to write a 90–100% dissertation — the hard intellectual scaffolding
is exceptional and largely transcribable — but is *not yet writing one*, and the gap is entirely
document-production. The materials that would make the write-up easy are (1) the skeleton, (2) the diagram,
(3) the figure generators, (4) a disciplined transcription pass — not more research.**

---

## 6. The single BIGGEST lever to 90–100% — brutally honest

> **The dominant lever is the WRITE-UP, executed with the framing discipline already specified — because
> the grade is the PDF and the PDF does not yet exist.** Everything else (the science, the inference, the
> theory, the limitations register) is already at the exceptional bar; none of it earns a single mark until
> it is *communicated* in a faultless, well-figured, citation-clean document that a second marker from
> another discipline finds inevitable. For a no-viva grade, **communication is not the soft criterion — it
> is the unrealised 20%.**

That is the honest top lever. Underneath it sit **two small, time-sensitive integrity closures** that are
cheap, must precede the freeze, and protect the headline from the two attacks an expert marker is *most*
likely to land — so they are the highest-ROI *non-writing* actions:

- **P0-a — Pre-register the BAB/low-vol factor-attribution family in `config/preregistration.yaml` (and add
  it to `LIMITATIONS_REGISTER` as L15 — already drafted there).** The code is wired (`attribution.py` →
  `out["attribution"]`); only the freeze-mirror declaration is missing. This is the one control that
  neutralises *"your whole edge is Betting-Against-Beta, not RL skill"* — the single attack that can recast
  the entire headline. Closing it is a YAML edit + a freeze. **(Highest-value non-writing action.)**
- **P0-b — Decide the `placebo_shuffled` arm and record it at freeze.** The inert placebo controls token
  count but not structure; only a shuffled-label arm identifies H2 against the Gupta–Hartford
  "LLMs-ignore-feedback-content" threat — described in the master findings as "the single most
  reviewer-convincing experiment." If a confirmatory re-run is feasible, **build and freeze it** (m=6→m=8,
  BH re-applied, candidate-seeded/replayable); if not, **explicitly scope H2 to "content beyond token-count"
  and name the structural-placebo gap as a stated limitation.** Either is defensible; *silence is not*.

And **one item that gates the entire pre-registration value and is the most urgent thing on the board:**

- **P0-0 — EXECUTE THE FREEZE.** `frozen: false` today. The "we fixed the design before the sealed leg"
  claim — the spine of a bankable null and a large part of the research-design mark — is worth *nothing* until
  `freeze.py` emits the hash and it is dated into `DECISION_LOG`, and it must happen *before* any sealed-test
  number exists. Do P0-a and P0-b first (they touch frozen quantities), ratify the PROPOSED λ=0 and the R24
  reflect-protocol record, then freeze. **This is hours of work and it is the difference between a
  pre-registered study and a post-hoc one.**

### Prioritised lever table (honest grade-ROI)

| Pri | Lever | Effort | Grade-ROI | Why |
|---|---|---|---|---|
| **0** | **Execute the freeze** (after P0-a/b + λ/R24 ratification) | hours | **Decisive** | Without it the entire pre-registration/null value evaporates; time-sensitive. |
| **0** | **Pre-register the FF6+BAB attribution family in the YAML; add L15** | hours | **High** | Closes the one attack that recasts the whole headline; code already wired. |
| **0** | **Decide + record `placebo_shuffled`** (build, or scope-and-disclose) | low–med | **High** | The only identification against the LLM-ignores-content existential threat. |
| **1** | **Build the thesis skeleton + start transcribing** (theory, limitations, lit synthesis) | days | **Decisive** | The grade is the document; these chapters are pre-scaffolded — fastest marks on the board. |
| **1** | **The one-page system diagram** | hours | **High** | Mandatory D-2; the second-marker's mental model of a hard idea. |
| **1** | **`make_figures.py` with the framing baked in** (ablation bar, conditional band, cost table, undeflated DSR) | 1–2 days | **High** | "Faultless data presentation" is the 90+ communication descriptor; pre-empts the negative-Sharpe display landmine. |
| **1** | **Write a self-contained abstract** from the `DEEP_SYSTEM_redteam` §7 strongest-claim + theory-spine §7 | hours | **High** | Most-weighted paragraph; bankable regardless of outcome. |
| **2** | **Finish `refs.bib` to ~90 + resolve every `% VERIFY` + citation-integrity fixes** (Refinitiv-not-CRSP; FZ0/Skalse/author-lists) | days | **High** | The avoidable mark-loss with a co-author marker; pure downside-protection. |
| **2** | **Fold the stated-judgement-call disclosures** (DSR N_eff; PBO mean-vs-DSR proxy; one-sided-BH; CVaR sign/power; pairing assumption) into Methods | low | **Medium** | Converts every `DEEP_STATS` C-item from a silent call into stated rigor. |
| **2** | **Re-run `power_analysis.py` at the pilot σ on the IQM test; wire/units-check TOST** | low (post-pilot) | **Medium** | Reports the MDE of the test actually run; upgrades a null to a *bounded* null. |
| **3** | **Reproducibility/artefact-availability statement + DOI plan** | low | **Medium** | Expected for publishable-grade open science. |
| **3** | **Plain-language contribution paragraph + worked feedback-block micro-example** (D-2) | low | **Medium** | Legibility for the any-discipline second marker. |

**What NOT to do** (scope discipline; all explicitly low-value or out-of-scope per the deep docs): no
same-panel SOTA re-run, no QD/OOD-GAN/offline-CQL arm, no second agent/universe/model *for this submission*
(name them as future work). Adding scope to chase marks is negative-ROI here — the marks are in the
*document*, not in more experiments.

---

## 7. Closing assessment

Judged against a **90–100%** bar, this dissertation is in an enviable and unusual position: **the science,
inference stack, theory, and self-disclosure are already at the exceptional level** — and, verified
first-hand, the deep-scrutiny recommendations are *implemented in code*, not merely promised, which is the
strongest credibility signal a careful marker can find. The work is a Distinction in *every* genuine outcome
branch and the pre-registered null is genuinely bankable.

The gap to 90–100% is therefore **not intellectual — it is executional and communicative.** It reduces to:
**(i) freeze the design now** (and, in the same pass, pre-register the BAB attribution family and decide the
shuffled placebo — the two closures that protect the headline from its two most dangerous attacks); and
**(ii) write the document** — a faultless, well-figured, citation-clean PDF that transcribes the
already-exceptional scaffolds (theory spine, limitations register, lit synthesis) and foregrounds the
feedback-channel-responsiveness contribution with the framing discipline the deep docs have already written.

For a no-viva grade, **the write-up quality is the remaining 20 marks.** The single most important sentence
of this audit: *the highest-grade work left is the work the author fully controls and that no campaign result
can take away — so the only route to a sub-Distinction outcome is self-inflicted (an unfrozen design, an
unattributed factor tilt, an over-claimed abstract, or a thin document). Freeze, attribute, and write.*
