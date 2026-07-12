# Deep per-stage / per-tier upgrade analysis — priorities × guidelines × supervisor feedback (2026-07-12)

> Tamer: *"dive deep into each stage, each tier … analyse the supervisor's feedback and our
> priorities … what could be upgraded and made deeper, strictly by the priorities and the feedback."*
> Sources re-read FIRST-HAND for this analysis: `../00_planning/DISSERTATION_ALIGNMENT_AND_GUIDELINES.md`
> (IFTE0008 rubric + exemplars), `docs/SUPERVISOR_MEETING_BRIEF_2026-07-10.md` (incl. his 3-Jul email's
> content and the meeting asks), `docs/SUPERVISOR_REVIEW_NOTE.md`, `docs/EXAMINER_grade_audit.md`
> (rubric-vs-artifact, the lever table), `docs/EXAMINER_OBJECTIONS_AND_DEFENCES.md`,
> `docs/STAGE2_PUBLISHABILITY_PLAN_2026-07-11.md`, `PREREGISTRATION.md` §2a. Each upgrade below is
> tagged **[NOW-mine]** (I execute), **[TAMER]** (his act), **[WRITE]** (write-time), **[POST-BANK]**
> (after Stage 1 banks). Nothing here touches a frozen decision.

## 0. The governing synthesis (what the feedback + rubric actually reward)

Okhrati's revealed function: **intuition > machinery · depth > breadth (docks scatter) · honesty = his
5/5 · motivate-with-data · originality foregrounded · docks: missing wall-clock compute, untidy
cross-referencing, unconventional order.** The rubric's decisive line: **90–100 = journal-publishable;
the four dimensions are equally weighted so the weakest caps the mark; the second marker may be from
any discipline** (the guidelines' named "single biggest risk"). The grade audit's verdict stands:
the science is at the bar; **the unrealised ~20% is communication**, plus a short list of cheap
integrity closures. Every upgrade below is chosen because it deepens ALONG this gradient — nothing
that adds breadth Okhrati would dock.

---

## 1. STAGE 0 (pre-freeze / de-risk) — upgrades

**State:** freeze-ready (`e3a8c880`, 21/21); pilots self-completing (path certified, F curve done,
B\*-ladders due, determinism pending); 4 day-1 breakers killed live.

1. **[NOW-mine] Bank-gate DRESS REHEARSAL on the prototype output.** The single-look moment is the
   highest-stakes hour of the project and has never been executed end-to-end (`analyze_campaign` →
   D3/D4/D9 → `make_prereg_bundle` as one sequence on a REAL cluster archive). When `pm2` completes,
   run the full bank-gate runsheet on it (directional data, no dissertation number) — any analysis-side
   defect surfaces on throwaway data instead of the sealed look. *Feedback link: "faultless execution"
   (dim 2) is won by never improvising at the gate.*
2. **[NOW-mine → TAMER ratify] Pre-register the M2 survey protocol as a dated document BEFORE Stage-1
   unblinding.** The flagship's credibility doubles if its design is demonstrably ex-ante. Contents:
   model roster (incl. deliberately weak models — the gradient IS the evidence), probe families
   (pairwise tail-comparison accuracy; ordering; use-in-authored-code), **difficulty calibrated to the
   EMPIRICAL fed-delta distribution** (instrument (h) ties the survey to the actual campaign stimuli —
   psychophysics-grade anchoring), per-model contamination + capability-floor gates (the Qwen pattern),
   bootstrap-over-items CIs, and the pre-named headline analysis: rank-correlation of per-model
   responsiveness on numeracy accuracy. Cost unchanged (~$5–10). *Feedback link: originality
   foregrounded + his ACL question, made unattackable.*
3. **[NOW-mine] Freeze the funnel-coding rubric prompt (instrument (g)) pre-data.** The reflection
   QUOTE→COMPARE→CONCLUDE→IMPLEMENT coder is an LLM-assisted instrument; dating its rubric prompt
   before any campaign reflection exists removes the "you tuned the coder to the data" attack. Cheap.
4. **[NOW-mine] Implement instrument (h) (fed-delta SNR/attenuation exhibit) as a script now**, so the
   bank gate computes it mechanically. R76 registered it; code should exist before data does.
5. **[TAMER, one email] Convert the meeting's verbal approvals to WRITING**: (i) the proposal-pivot
   sign-off (`SUPERVISOR_REVIEW_NOTE` item (b) — asked 3 Jul, asked again at the meeting, still the
   one open procedural integrity item); (ii) E1 endorsement in a sentence; (iii) the guidelines'
   ethics/data-protection confirmation (secondary financial data, no human subjects; the Refinitiv
   licence position). One email closes three procedural boxes the guidelines explicitly grade.
6. **[NOW-mine, queued] `wall_clock=0.0` record fix + cluster code sync.** Okhrati DOCKS missing
   wall-clock compute; the records must carry it natively (the epilogue ledger is the stopgap).
7. **[TAMER] The freeze itself** — the grade audit's P0-0 stands: pre-registration value is unrealised
   until the hash is stamped, and every sealed-leg number must postdate it.

## 2. STAGE 1 — the C-ladder, rung by rung

- **C0 canary. Upgrade [NOW-mine]:** extend the canary's definition of success from "trainings ran" to
  "the ANALYSIS pipeline parses the canary records" (a 2-minute `load_run`/accounting smoke). Catches
  reader-side breaks on day 0. Also verify compute-accounting fields land (see §1.6).
- **C1 H2 search. Upgrades:** (i) **[NOW-mine]** reflection-archival completeness check — instrument
  (g) needs every reflection verbatim; assert at pull time that each generation's reflection text is
  non-empty and archived (the funnel analysis dies silently otherwise). (ii) **[NOW-mine]** live
  K-sample diversity telemetry (Opus uses prompt-variation, not temperature — the runready gotcha);
  a per-generation duplicate-rate line in the driver log guards degenerate sampling cheaply.
- **C2/C3 floor + gate. Upgrade [NOW-mine, small]:** the per-device D̄ diagnostic promised by the
  device-block ratification (2026-07-11c) is currently a claim, not code — add it to
  `integrity.write_integrity_report` (group per-seed D by recorded GPU model; report means + counts,
  effect-blind by construction since it never sees direction vs the SESOI… it does see D — keep it in
  the SEALED-side report only, not the gate). Also: the gate stays effect-blind auto-proceed (built).
- **C4 sweep. Upgrades:** (i) **[built, activate]** re-confirm the assurance target from the run's OWN
  measured cadence at the gate (`recommend_assurance_target` — exogenous, self-correcting); (ii)
  **[NOW-mine]** chunk the sweep arrays per the serialization-policy mitigation (per-arm × seed-chunk,
  ~pack-5 tasks) — the fleet shape is now a measured requirement, not a preference; (iii) per-rung
  completion manifests (which units at which n) so any truncation is self-documenting.
- **S1.5 D1 dose-response.** Frozen; no upgrade. Reserve its figure slot in the manifest (Okhrati:
  tidy cross-referencing).

## 3. The BANK GATE (the single-look hour)

**Upgrade [NOW-mine]: script it.** `OVERALL_DESIGN §6` already flags this as the one "described, not
executable" transition. One thin wrapper (or a documented one-command runsheet) executing:
`archive_integrity` → verify-mirror → `resume_audit` → `analyze_campaign` (single look) →
D3/D4/D9 → instrument (h) → `make_prereg_bundle`. Then REHEARSE it on the prototype (§1.1). The
combination converts the riskiest hour into a replayed procedure. *This is the highest
execution-risk-per-hour reduction available in the entire plan.*

## 4. STAGE 2 — tier by tier

### TIER M (the contribution — every upgrade lives here by priority-3)
- **M1 locate-the-break. Upgrade [WRITE, prep NOW-mine]:** pre-write the mechanism chapter's TABLE
  SHELLS — the A1–A5 fingerprint scoring table (now five accounts, R76), the funnel drop-off table,
  the responsiveness-CI figure spec — so bank-gate → chapter is transcription, not composition.
  *Okhrati: results he can scan; the ESG exemplar's "systematic scannable tables."*
- **M2 survey (flagship). Upgrades:** the §1.2 protocol pre-registration, PLUS **[free datum, NOW]**:
  tonight's rehearsal measured a live **Qwen sandbox-reject rate** (buggy authored code caught by the
  gate) — a zero-cost capability-gradient observation that motivates the survey's weak-model wing;
  log it into the protocol's motivation. *Motivate-with-data, literally.*
- **M3 legibility lever. Upgrade [NOW-mine]:** implement the re-renderings (basis-points, ordinal
  ranks, CI-annotated) as pure functions NOW and smoke them on archived prototype reflection states —
  zero API cost, and the A5-vs-A2 discriminator (R76) depends on the CI-annotated variant being
  byte-stable before it is used in anger. D2+ authoring sweep stays [POST-BANK].

### TIER R (rigor)
- **D3 variance decomposition. Upgrade [WRITE]:** pre-draft its interpretation paragraph — σ_seed
  dominance as a first-class reproducibility finding, cited INTO the corpus (Henderson 2018, Colas
  2018/2021, Agarwal 2021) rather than reported as a number. *Corpus-grounded (priority 4), depth.*
- **D5 calibration fleet. Upgrade [NOW-mine, schedule]:** the laptop goes idle after the ladders
  (~midday); D5 is keyless — start it TODAY rather than at the bank gate. Zero marginal cost,
  arrives pre-gate as designed (Stage-2.C).
- D4/D9: adequate as specified; no upgrade that isn't churn.

### TIER G (thin shell — the discipline is NOT upgrading it)
- U3 Qwen: gate unchanged; tonight's reject-rate informs the capability floor. D6/U5/U4/FTSE stay
  CH7 future-work BY DESIGN — the feedback explicitly dock scatter; the deepest upgrade to TIER G is
  leaving it thin.

## 5. THE WRITE-UP (the unrealised ~20% — every audit lever folded in)

The §4 communication plan (handoff doc) absorbs the grade-audit's remaining levers, in build order:
1. **[WRITE, first] The outward contribution sentence** — reframe from "a clean portfolio comparison"
   to *"the first theory-grounded, pre-registered test of whether an LLM reward-designer is a
   Bayes-responsive user of risk information — the Gupta–Hartford 'do LLM optimizers use feedback
   content' question, instantiated where the answer is checkable against decision theory"* — into the
   ABSTRACT (the audit: the strongest claim is currently buried in a scrutiny doc). Low effort,
   highest positioning value on the board.
2. **System diagram** (mandatory D-2) + the 3-link mechanism figure (cut at joint 1).
3. **Worked micro-example — now REAL:** use an actual archived prototype fed-block and the actual
   authored diff, not a hypothetical (−0.0577 vs −0.0582 exists in the archive). *Intuition >
   machinery, made concrete.*
4. **Wall-clock compute section — now MEASURED:** 102.2 steps/s, the F-curve (saturation 2.5), 3.74
   trainings/GPU-h, per-stage wall tables, $ costs. What Okhrati docks for absence becomes a strength;
   the packing curve itself is an appendix exhibit of execution rigor.
5. **Judgment-call disclosures into Methods** (DSR N_eff, PBO-proxy, one-sided convention, pairing) —
   converts silent calls into stated rigor.
6. **Limitations subsection** = the §10 volunteer-list from the meeting brief (endogeneity, K=5,
   CVaR-1% variance, i.i.d.-Sharpe caveat, single-market, composition bias) — the exemplar practice
   and his 5/5.
7. **refs.bib to ~90 Harvard + zero `% VERIFY` + figure/table cross-reference pass + 16-section
   order + front matter** (Moodle cover, self-contained abstract, ToC, lists) — the guidelines'
   mechanical compliance items, all docked if sloppy.

## 6. Supervisor-feedback follow-ups still OPEN (small, all his)

- Written pivot sign-off (asked 3 Jul, meeting verbal — **paper trail still missing**).
- His answer to §11-5 (*which deep analyses to expand*) and §11-6 (*his evidential standard for the
  null*) — if the meeting produced answers, record them into the plan; if not, they are the two
  highest-value questions for the next email since they steer the write-up's depth allocation.
- Ethics/data-protection confirmation (guidelines checklist).

## 7. What was deliberately NOT upgraded (scope discipline, stated per the audit's "what NOT to do")

No same-panel SOTA re-run, no new arms/markets/models beyond the frozen+Stage-2 set, no premium-shelf
revival, no intraday, no B\* re-litigation beyond the running ladders, no CRAG (rejected). Adding
scope to chase marks is negative-ROI; the marks are in the document and the mechanism depth.
