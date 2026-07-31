# V2 write-time registry (2026-07-20) — binding checklist; nothing here may be silently dropped

Every v2-created write-time obligation, in one place. Each item names its artifact. Checked off
during the writing month; the pre-submission sweep verifies zero open rows.

## Frozen-design-driven prose (write during build week / week 1 — need no results)
1. **CH3 + CH7: the g(capability) paragraphs** — the envelope–realization gap as a function of
   author capability; the suite traces it; the numeracy bottleneck = its hypothesized shape.
2. **CH4: the model-suite section** — the 10 seats each argued in one sentence; the pins; the
   queue + gates; the diversity unification; the "same exam for every student" prompt principle;
   the cost table WITH the real dollar figures; the three-layer reproducibility statement +
   vendor deprecation policies + the public-deposit anchor.
3. **CH2: the 15/15 model-usage survey table** + the REvolve justification quote + the GEPA
   closed+open precedent + the "field's transition embodied" framing sentence.
4. **00_FRAMING + abstract: the v2 reframe pass** (one frontier + open replication suite + the
   gradient; the title decision re-confirmed).
5. **NOMENCLATURE additions**: legs, g(capability), the synthesis terms, the queue/gate terms.
6. **AI-disclosure (AI-as-object)**: enumerate the FULL 10-model roster + M2's 25 as study
   objects (distinct from the Category-2 assistive-writing disclosure).

## Results-machinery revisions (build week Jul 23–25)
7. **CH6 skeleton v2 revision** — leg-results subsection slots, the synthesis slot, the
   reliability-table slot, achieved-rung/power slots; every number a [FROM CAMPAIGN] tag under
   the rung-freshness convention. **BUILT 2026-07-21 (`e968cdd`): §6.7/§6.8 + §6.1 slots +
   reporting rule 5 defines the tag convention; `scripts/check_rung_freshness.py` = the gate.**
8. **FIGURE_TABLE_MANIFEST v2** + `src/viz/figures.py` additions: the cross-leg forest plot, the
   capability-gradient scatter (anchors on x, responsiveness on y, family pairs highlighted), the
   reliability table/heatmap, and the TEN-WINNERS side-by-side annotated code exhibit.
   **BUILT 2026-07-21 (`e968cdd`): F12–F15 + T6/T7 rows + all four renderers, tested.**
9. **results_walkthrough notebook v2 sections** mirroring 7–8. *(Write-time: needs leg data;
   the renderers + aggregation it mirrors are built.)*
10. **analyze pipeline multi-root aggregation** — 9 leg archives + the core, feeding the
    synthesis module (in the code build; listed here because CH6/notebook depend on its output
    shapes). **BUILT 2026-07-20/21 (`e0380c5` leg_aggregate + `7bf1fa7` the --leg launch path
    producing the per-leg roots it reads).**

## Campaign-window artifacts
11. **The interim report pack (~Aug 6–8)** — floor-tier results (labeled provisional), draft
    mechanism chapter, the design record, 3–4 questions each for Dr Okhrati and the industry
    supervisors. Registered: presentation-only effect (R81).
12. **Per-leg bank-gate logs** archived with each leg's tables.

## Pre-submission gates (unchanged + v2 additions)
13. The mandatory novelty-fence sweep; citations gate; word surgery AFTER the final number
    refresh; the rung-freshness grep gate green; zero [FROM CAMPAIGN] or stale-rung tags;
    license-file glances recorded for every leg cited as open.

## Deep-sweep additions (2026-07-21 — binding; sourced from the pre-freeze design review)
14. **The v2 WORD-BUDGET RE-PLAN (guides: 10k body, weakest-dimension-caps).** The measured body
    was already ~15.5k vs the 10k limit BEFORE v2; v2 adds ~1.5–2k words of new obligations
    (CH4 model-suite + cost + repro; CH6 §6.7–6.8; CH7 checklist + g(capability)). BINDING RULE:
    the v2 additions land APPENDIX-FIRST — the body carries ≈1 tight paragraph per v2 axis
    (why-ten-models; the synthesis verdict + bound; the practitioner takeaway) and every
    mechanism-of-the-suite detail (pins, queue mechanics, reliability tables, synthesis math)
    goes to word-excluded appendices/tables. The surgery pass re-measures AFTER v2 prose lands.
    **⚠ RE-MEASURED 2026-07-26 (deep review, loop 11) — the "~15.5k" above is STALE and the plan is
    sized ~3.6k words too small.** `make wordcount` (`scripts/word_budget.py`, which DOES apply every
    UCL exclusion — display + inline math, code fences, inline code, tables, footnote definitions,
    image lines, word-excluded in-file appendices, and FRONT_MATTER wholesale) now reports:

    | chapter | words |
    |---|---|
    | CH1_introduction | 2,588 |
    | CH2_related_work | 2,748 |
    | 02_CHAPTER_theory | 4,000 |
    | CH4_methods | 4,250 |
    | CH5_prototype | 1,391 |
    | CH6_results | 2,297 |
    | CH7_discussion_limitations_conclusion | 1,855 |
    | **TOTAL (main body)** | **19,129** — vs limit 10,000, PASS ceiling 9,500 |

    So the body is **91 % over a HARD limit**, and the required cut is **~9,600 words (about half the
    document)**, not the ~5.5k the stale figure implies. This is not a rounding matter: communication is
    one of four equally-weighted dimensions, the WEAKEST dimension CAPS the mark, and a marker can
    penalise a hard-limit breach directly regardless of content quality. The four heaviest chapters
    (CH4 4,250 · CH3 4,000 · CH2 2,748 · CH1 2,588 = 13,586, i.e. 71 % of the body) are where the
    surgery has to happen. The levers are the ones `word_budget.py`'s own docstring names — push formal
    apparatus into EXCLUDED math, and move mechanism detail into word-excluded appendices/tables — plus
    the playbook's MOVE 3 distillation. **Re-run `make wordcount` after every writing session**; it
    exits 1 over the limit, so it can be treated as a gate rather than a report.
15. **New-citation evidence grade (strong-evidence standard).** REvolve, GEPA, and METR are
    load-bearing v2 citations (the REvolve "necessary choice" quote is verbatim in the NatWest
    brief and planned for CH2) and are **absent from refs.bib** (verified 2026-07-21, 199
    entries). Before the PDF: add + first-hand-verify (with archived URLs + retrieval dates)
    REvolve (ICLR'25), GEPA (ICLR'26 Oral), the METR GPT-5.6 reward-hacking eval (55.4% —
    currently sweep-agent-sourced), the NeurIPS-checklist hosted-model clause, and Anthropic's
    deprecation/weight-preservation pages. `% VERIFY` discipline until then.
16. **Novelty-fence SCOPE EXTENSION + due date.** The fence sweep now also verifies the NEW
    claim "first systematic open-weight replication suite in this lineage" (currently hedged
    "to our knowledge" — keep the hedge unless the sweep confirms) alongside the main cell and
    the ELfolio scoop-watch. The last full novelty sweep was 2026-06-28; a cadence sweep was RUN 2026-07-30 (record §41) and found the new nearest neighbour GIFT (arXiv 2606.08450) — cell SURVIVES, GIFT must be cited in CH2. Next due ~2026-08-20; the ~2–3-week cadence
    makes one DUE at freeze (and the pre-submission sweep remains mandatory).
17. **Limitations register additions (APPENDIX_B; the guides' exemplar subsection).** (a) legs
    at floor-30 = per-leg TOSTs inconclusive by construction (the pooled R86 bound is the
    informative statement); (b) open legs are served fp8 via a pinned provider — the executed
    author is the served variant of the hash-pinned weights (one sentence, per R85); (c) no
    self-hosted leg (scope decision, disclosed); (d) three closed legs lack dated snapshots
    (Luna/Gemini/Sonnet-id-convention — disclosed); (e) the M2 secondary anchor shares method
    variance with the outcome (why it is secondary); (f) the calendar gate may truncate
    back-of-queue legs (pre-declared, reported).
18. **[DRAFTED D10, 2026-07-21]** **The any-discipline plain-language paragraph for the model suite** (communication
    dimension): one jargon-free paragraph — why ten models, what a "leg" is, what the reader
    should look at (the forest plot + the bound) — placed with the CH6 §6.7 opening; the
    capability-gradient figure caption readable without knowing what fp8 or BH means.

## GRADE-INFLATION rows (2026-07-21 — supervisor-confirmed raised bar; binding; see the memory
## note: last year's distinction ≈ this year's merit — borderline evidence rounds DOWN)
19. **[DRAFTED D6, 2026-07-21]** **SESOI justification paragraph (CH4):** the ±0.05-DSR margin argued from DECISION-RELEVANCE
    (what effect size would justify building a distributional-feedback pipeline), not asserted —
    an unjustified SESOI is exactly the borderline item a harsh marker rounds down.
20. **[DRAFTED D7, 2026-07-21]** **H4 prominence upgrade:** the guides' own methodology validation (§8) flags that NO
    literature shows an LLM designer beating matched-compute non-LLM search — "demonstrating (or
    honestly not) that edge is itself the contribution." Under the raised bar H4 moves from
    afterthought to a NAMED result with its own paragraph + table row; the Coache–Jaimungal
    differentiation (guides §5 caveat) becomes an explicit CH2 paragraph.
21. **The 60%-core ratio re-check post-v2:** the pre-v2 budget was ~51% core (guides §1); v2
    prose lands appendix-first but CH4/CH6 grow — re-measure Methodology+Results+Discussion ≥60%
    at surgery and nudge Discussion UP (it was the thinnest at ~700 words).
22. **[DRAFTED D8, 2026-07-21]** **The independence narrative:** a short research-journey thread (Feb proposal → disciplined
    pivot → v1 freeze → industry feedback → documented pre-data v2 revision) told as TAMER'S
    decisions — under heavy-AI-assistance disclosure this is the auditable evidence of
    "independence of thought", and the guides sanction the pivot explicitly (§5).
23. **[DRAFTED D9, 2026-07-21]** **Publishability made DEMONSTRABLE, not asserted:** cite the public prereg DOI in the PDF,
    the 4-paper map, and the NatWest interim pack as artifacts; frame vs the 90–100 descriptor
    ("publishable in a peer-reviewed journal") with TMLR named.
24. **The any-discipline reader gate (pre-submission):** a genuine non-specialist reads CH1 +
    the plain-language paragraphs + every figure caption cold; anything they stumble on gets
    rewritten. Cheap, and directly targets the guidelines' named "single biggest risk" under
    the harshest-grading year. Front-matter exactness (Moodle cover, exact title wording,
    Arial ≥10 / 1.5 spacing template SET BEFORE writing) rides with this row.

## The optional M2 psychometric module (R96 — 2026-07-22; DECIDE AT THE WRITE-TIME FORK)
25. **The M2 extension activation decision (Tamer's, dated).** The full pre-specification lives
    in `docs/M2_EXTENSION_OPTIONAL_SPEC_2026-07-22.md` (Axis A: per-model JND thresholds + the
    fed-delta overlay = the mechanism closure figure; Axis B: the ~100-130-base ecosystem map).
    IF activated: all estimands report in full (the all-or-nothing clause); the stimulus builder
    rides scripts/m2_survey.py; ~$25-35 as a separate P2-module budget line; zero GPU. IF not:
    the registered v1 M2 probes still run (~$10, 35 rows since R99). Either way this row must be CLOSED
    with a dated decision before the pre-submission sweep.

## Universe-size defense (2026-07-22; Tamer's "is 30 stocks enough?" review — assessment: YES, defend in prose, do NOT widen)
26. **The "why thirty" paragraph (CH4 §4.2, one paragraph).** The choice is currently stated,
    not argued. Argue it on four grounds: (i) TRAINABILITY AT MATCHED COMPUTE — the identification
    principle fixes the agent + budget across arms; a wider action space at the frozen 400k-step (R77)
    budget resurrects the undertraining threat and inflates seed variance (σ_seed already dominates,
    0.244), i.e. MORE assets = LESS power for the arm contrast, the thing actually under test;
    (ii) DIVERSIFICATION SATURATION — the classical result that 20–40 names capture most
    diversifiable-risk reduction (Statman 1987 / Elton–Gruber — NOT yet in refs.bib: verify
    first-hand at wiring per the strong-evidence standard, else lean on demiguel2009naive alone);
    (iii) COMPARABILITY — DJIA-30 is the de-facto universe of the deep-RL portfolio literature,
    and ours STRICTLY DOMINATES the common practice of using today's constituent list: PIT top-30
    from a 953-name survivorship-free parent with delisting terminals retained (brown1992survivorship
    already cited); (iv) BENCHMARK STRENGTH — at n=30 with ~3,000 train days the covariance-based
    baselines (Ledoit–Wolf, min-var, HRP) are well-estimated, so the comparative claim faces
    strong, not straw, baselines. Prose-only; zero design change; identification-safe.
27. **Pre-empt the "null-by-design universe" objection (CH7 Discussion, 2–3 sentences).** The
    strongest examiner attack on a bounded-effect null is "your 30 large-caps in one market are
    too internally correlated / tail-poor for tail-specific feedback to matter — the universe
    stacked the deck." Answer with evidence already in hand: the F3 stylized facts measured ON
    this panel (excess kurtosis 15.25, deep-tail Gaussian understatement ×1.66, co-crash 19.7%)
    show the multi-level tail structure was demonstrably present to exploit; the Sharpe co-primary
    is not tail-dependent at all; and the mechanism kernel supplies an independent causal account
    (the numeracy bottleneck) for WHY the informational margin fails to convert. Close with the
    registered external-validity scope: B.4.1 + the shipped PIT walk-forward re-evaluation
    capability (R17) + the ADR-047 FTSE-100-lite replication (S2, report-only, Papers-2/3-bound).
28. **Benchmark-canon citation completion (rides the CH4/CH6 benchmark-suite paragraphs).** Every
    allocator and hand-written reward carries its literature anchor in the CODE docstring, but
    several are not yet promoted to refs.bib (Tier-1 currently covers demiguel2009naive,
    ledoit2004honey, lopezdeprado2018afml, jiang2017eiie, moody1998performance, moody2001directrl,
    rockafellar2000cvar, artzner1999coherent). MISSING at PDF-cite level, to be first-hand
    verified per the strong-evidence standard when the prose wires them: Markowitz 1952 (mean-
    variance/quadratic utility), Jegadeesh & Titman 1993 (cross-sectional momentum), Choueifaty
    & Coignard 2008 (maximum diversification), Maillard, Roncalli & Teiletche 2010 (equal-risk-
    contribution), Clarke, de Silva & Thorley 2011 (long-only min-variance), Kelly 1956 + Thorp
    1971 (log-growth), Sortino/downside-deviation anchor (return_minus_downside). Rule: cite only
    what the prose names; verify each against the publisher record; no orphan bib entries.

## The hand-written reward panel review (2026-07-22; Tamer's "make the human-written very smart" sweep — R97 executed same-day)
29. **The 2026-07-22 dated reward-literature sweep: CH2 wiring + fence entries (verify each
    first-hand at wiring; none may silently drop).** (a) ⚠ **GIFT (arXiv 2606.08450, 7 Jun 2026,
    "LLM-Guided State-Reward Interface for Financial RL") — the NEWEST adjacent paper; MUST be
    cited + differentiated in CH2.** Read first-hand today (PDF on disk in the session scratch):
    the LLM generates state features from a factor library AND auxiliary rewards from a 7-rule
    risk library under PPO, on 5-stock S&P panels, 3 seeds, win-rate counting — no pre-registration,
    no hypothesis tests, no scalar-vs-distributional contrast, and it varies STATE and REWARD
    JOINTLY (exactly what our identification principle forbids). It does NOT occupy our cell;
    it STRENGTHENS the motivation (its own diagnostic finds free-form LLM generation unstable in
    finance — convergent with our numeracy-bottleneck mechanism). Scoop-watch: joins ELfolio;
    the freeze-due novelty sweep (row 16) must re-verify against it. (b) CH2's reward-canon
    paragraph gains its literature spine: the ACM Computing Surveys taxonomy (arXiv 2408.10932 —
    profit/utility/composite reward classes), Almahdi & Yang 2017 (Calmar/E(MDD) RRL objective;
    covered in-panel by the drawdown penalty + the DDR's Sterling-tracking DD, Moody & Saffell
    2001 fn. 7), the 2025 composite risk-aware reward line (arXiv 2506.04358 — Treynor/benchmark-
    relative terms are STRUCTURALLY EXCLUDED here: the anonymized panel has no market index, R19),
    and behavioral/prospect-theory rewards (named as a distinct un-fielded axis, future work —
    not canon). (c) The panel-coverage claim CH2 can now make, evidence-backed: the ten-name canon
    + the BO-tuned six-term family jointly span location/scale/tail/path/asymmetry/cost/growth +
    online-ratio (symmetric DSR AND downside DDR) + the optimized-composite class — the strongest
    published-canon steelman the identification principle permits.

## 5-auditor final sweep — REMAINING VERIFIED MINORS (2026-07-22; fix before/at write time; sources = the audit reports in CHANGELOG [2026-07-22])
30. **Open minor fixes from the 5-auditor sweep (all verified, none campaign-blocking):**
    (a) analyze_campaign.py: shared `headline_cvar_level()` helper — the superset early-return at
    ~1151 skips membership checks (restrict-and-continue instead) + `max(cvar_levels)` at ~1691 and
    `cvar_levels[0]` at 4804/4825/4835/4846/4856/5096 should all resolve the frozen 0.05 via one
    helper; (b) cross_model.pooled_bound/pair_did: n>=2 fail-loud + vstack length assert + NaN
    scalar_level guard; (c) leg_aggregate.py:33-37 + regime_analysis.py:29-35: add bootstrap.cvar's
    non-finite strip; (d) es_backtest.py:92-94 stale docstring (code is the documented interpolated
    convention; fix the words); (e) magnitude guard: |total|>1e6 → SAFE_DEFAULT in
    sandbox/executor.py::safe_call + portfolio_env substitution site (protects the popart=False
    ablation; identification-neutral) + test; (f) leg_gates.py: assert every leg model id resolves
    in planning_prices (the $0-booking drift guard); (g) client.py JsonlArchiveSink: escalate
    persistent write-failures to always-ERROR + marker file; (h) resume_brief.py: legs regex
    `^\s*-\s*label:`, frozen probe case-insensitive, fix the "HEAD or HEAD~1" comment (code = last-3);
    (i) portfolio_env.py:317 stale rewards.py line refs (drop numbers); (j) CH6 §6.7 needs the R97
    ten-name-panel landing slot sentence; (k) docs/CAMPAIGN_RUNBOOK.md needs a SUPERSEDED banner
    (stale 200k GO/NO-GO would kill a correct 400k launch); (l) regression tests for the three R97
    SystemExit guards (currently manually verified only); (m) launch-day: verify Myriad max_u_jobs
    vs ~1,200 pipelined arrays (runbook §10 note); (n) C6 non-pipelined sweep blocks at -p 0
    (latent inversion) + C7 tiered summary not root-suffix-namespaced (latent clobber); (o) h3
    line bills ~30 authorings unshielded by the canary (design drift, bounded — disclose or gate).

## LLM-layer deep review (2026-07-23; Tamer's "dive deep into models/prompts/loops" order — verdict: KEEP the layer, bank the literature)
31. **The 2026-07-23 LLM-practice sweep: citations + the considered-and-rejected record.**
    (a) ⚠ **"LLMs Know More About Numbers than They Can Say" (arXiv 2602.07812)** — models decode
    log-magnitudes internally at >90% (linear probes) yet VERBALIZE cross-notation comparisons at
    only 50–70%: the strongest external corroboration yet of THE numeracy-bottleneck mechanism
    (the say–know gap IS our A1–A5 story) and it reports NO format fix — validating both the raw
    small-float default and the registered legible-mode/R96 JND probes as open science. Wire into
    CH2 (mechanism lineage after wallace2019numbers) + CH7; verify first-hand at wiring.
    (b) The 2025–26 numeric-tokenization line (TST arXiv 2604.11582; xVal 2310.02989; single-token
    encodings 2510.06824) = CH2 one-sentence context for WHY digit fragmentation breaks numeracy.
    (c) **RDA (arXiv 2606.01672)** — the Eureka successor: VLM visual-trajectory diagnostics +
    subtask decomposition. Cite in CH2; DIFFERENTIATE: RDA enriches the feedback channel for
    performance, we CONTROL it for identification — rich diagnostics would break the
    single-varying-factor design; our "coarse numerical reflection" is the manipulated variable,
    not a limitation. Fence entry alongside GIFT/ELfolio.
    (d) **CONSIDERED AND REJECTED (dated, pre-freeze — record so the fence shows conscious
    decisions):** (i) XML-tagging the prompts (Anthropic 2026 guidance: 20–40% consistency gain on
    LONG prompts) — ours are short, the executable-rate is already high, and restructuring would
    invalidate the tail-neutrality verification + the σ pilots calibrated under these exact bytes;
    (ii) assistant-prefill ("```python") to force code-only output — provider-ASYMMETRIC (Anthropic
    supports it, OpenRouter legs vary) → a format confound across legs; the fence-parser already
    handles the residual prose rate. Both re-openable for Papers 2/3, never mid-campaign.
    (e) DEEPER SWEEP (same day): OPRO/TextGrad/CodeGrad = the textual-gradient lineage — CH2 one-liner
    differentiating our CONTROLLED-feedback loop from optimization-maximal loops; execution-error
    traces in reflection (ReflectionCoder-style) = a known loop upgrade, CONSIDERED-REJECTED
    mid-campaign (arm-identical hence identification-safe, but it changes the pilot-validated loop
    behavior days before GO; Papers 2/3). (f) PROMPT-PORTABILITY: industrial studies show 20-30%
    cross-model prompt degradation -> B.3.4 NOW ADDED to APPENDIX_B (same-prompt = the replication
    design; gates + anchor = the defense); find + verify the exact citation at wiring (the
    meta-prompting industrial paper, arXiv 2508.01443 candidate).
    **[ROW 30 CLOSED 2026-07-23 — wave 2 executed]:** (a) headline_cvar_level() shared helper wired
    at the gate + all 6 report sites + the superset branch now restricts-and-continues; (b) pooled_bound/
    pair_did n>=2 fail-loud + length + NaN guards; (c) non-finite strips added (leg_aggregate,
    regime_analysis); (d) es_backtest docstring now matches the A-L1 code; (e) |total|>1e6 ->
    SAFE_DEFAULT in safe_call (+ inclusive-bound test; covers the popart=False ablation);
    (f) leg_gates price_key check (all 10 legs live-verified resolving); (g) archive-sink persistent
    failures escalate to always-ERROR + ARCHIVE_WRITE_FAILURES marker at >=3; (h) resume_brief
    parsers hardened (indent/case-tolerant) + comment fixed; (i) portfolio_env stale line refs
    dropped; (j) CH6 §6.7 R97 slot added; (k) CAMPAIGN_RUNBOOK superseded banner (the M05-class
    trap defused); (l) 4 guard regression tests (dry-run placement LOCKED; laptop-side guard
    EXTRACTED to resolve_baseline_names + directly tested 2026-07-23 — residual CLOSED); (m)+(o) runbook launch-day
    pre-checks (SGE job-cap qconf commands; h3 canary exposure disclosed w/ the STOP file
    mitigation); (n) C6 sequential sweep blocks now mirror the pipelined ladder priorities
    (test updated to the registered-queue invariant) + C7 tiered summary root-suffix-namespaced.

## World-models assessment (2026-07-23; Tamer's "adding world models" review — verdict: a FRAMING win now, machinery = Papers 2/3)
32. **The world-model FRAMING paragraph (CH7, one paragraph — the cheap win; wire at write time).**
    Position the reward designer AS a prior-laden world model with a narrow numeric interface:
    the LLM carries a rich implicit model of market behavior (the contamination/H4 priors — the
    OBJECT of study), and the fed tail vector is an attempt to UPDATE that world model with
    measured state; the numeracy bottleneck (B.3.2 + the say–know gap, 2602.07812) is then an
    INTERFACE failure between explicit measurement and the implicit world model — which is why
    format probes (legible mode, R96 JND) are the right instruments. Cite the LLM-as-world-model
    line (arXiv 2411.08794, verify first-hand) + DreamerV3 (Nature 2025) as the agent-side
    contrast. One sentence in CH4 §4.2 completes it: the historical-replay simulator is the
    REALIZED world, deliberately preferred to a LEARNED one (a generative simulator would let
    authored rewards exploit simulator artifacts — reward hacking against the world model — and
    would trade the study's strongest asset, licensed PIT data, for a sim-to-real validity gap).
    **CONSIDERED AND REJECTED for this cycle (dated):** (i) swapping SAC for a Dreamer-class
    agent — invalidates every pilot/calibration/certification, months of work, muddies the
    deliberate simulated-online-vs-offline-RL positioning (Okhrati bridge), and near-martingale
    daily returns are the worst case for learned-dynamics overfitting; (ii) training inside a
    generative market simulator (MarS/LMM class) — the artifact-exploitation + data-asset
    trade above; (iii) a queryable simulator for the DESIGNER — enriches the feedback channel =
    the registered identification-breaker class (row 31). **Papers-2/3 extensions (named):**
    (a) the tail-feedback contrast replicated under a DreamerV3-class agent (does the null
    persist when reward shaping interacts with imagination rollouts?); (b) generative
    tail-stress — synthetic crisis world models extending the EXISTING ood_stress module for
    counterfactual evaluation of the frozen winners.

## The two-tier verdict framing (2026-07-23; Tamer's "let's listen to all 11" — verdict: the design already does; make the prose SAY it)
33. **The two-tier-verdict paragraph (CH6 §6.8 lead-in + one CH7 sentence).** State explicitly:
    the verdict architecture is TWO-TIER BY DESIGN — (i) confirmatory PRECISION from one named
    instrument (Opus 5 at ladder depth, where TOST power exists against the SESOI), and
    (ii) generalization BREADTH from all eleven full-loop models read JOINTLY through the
    registered synthesis (sign pattern · joint per-seed flip permutation · the pooled R86 bound —
    built precisely because per-leg floor verdicts are inconclusive by construction · pair DiD ·
    the R87 gradient). Say plainly: the MECHANISM conclusion (the numeracy bottleneck) rests on
    the full 11-model gradient + the 35-model M2 axis, not on Opus alone; and the asymmetry is
    epistemic honesty (no defined "population of LLMs" exists to sample, so breadth is pooled
    descriptive evidence, never overclaimed as confirmatory) — B.3.1's registered design choice,
    argued in one paragraph instead of left implicit. Anticipated-question fodder: "why not make
    all 11 confirmatory?" -> m=6 × 11 ≈ 66-test multiplicity burn + ladder-depth compute ×20 +
    the undefined inference target. Wire beside D10 (the why-ten-models plain para).

## The registered cross-model synthesis is BUILT BUT UNWIRED (2026-07-26 deep review, loop 4 — verified first-hand; MUST close before the headline is written)
34. **Wire `src/inference/cross_model.py` + `src/inference/leg_aggregate.py` into the analysis, or
    withdraw the registered claim.**
    > ✅ **CLOSED BY ROUTE (a) — WIRED. This row's blocker text below is STALE (verified first-hand,
    > deep review loop 114, 2026-07-27).** Re-running this row's own stated import search now returns
    > production hits, not zero: `scripts/analyze_campaign.py` (in `analyze()`, the block commented
    > "WIRED 2026-07-26" — cited by SYMBOL not line number, which had already drifted from
    > `4873-4875` to `4900-4902` as later review loops added lines above it) does
    > `from src.inference.leg_aggregate import cross_model_synthesis` and **calls** it
    > (`out["cross_model"] = cross_model_synthesis(root)`), which chains to `cross_model`'s
    > `permutation_test` / `pooled_bound` / `sign_count` (`leg_aggregate.py:219`). The row's required
    > end-to-end test exists and is stronger than asked: `tests/test_leg_aggregate.py:202+` ("the
    > production wiring (row 34)") locks the caller **and its anti-fabrication states** —
    > `test_no_leg_archives_is_MISSING_DATA_not_a_null_effect` and
    > `test_a_missing_T0_floor_is_a_MISSING_INPUT_not_a_result`.
    > **The "also check when closing" unit trap was ALSO fixed in the same change**: `leg_aggregate`
    > now delegates to the canonical `bootstrap.sharpe_ratio`, removing the annualisation AND ddof
    > discrepancies at once; the in-code comment records that the old per-period/ddof=1 form would have
    > compared ~0.04 against a ~0.6 floor, failing EVERY leg and yielding "a plausible-looking, wholly
    > fabricated scientific outcome". **53 passed, `PYTEST_RC=0`** (`test_leg_aggregate` +
    > `test_cross_model` + `test_analyze_mechanism_wiring`) at pinned `--randomly-seed=22`.
    > **Left OPEN rather than ticked — recording an obligation as discharged is Tamer's call.**
    VERIFIED by a repo-wide import search (`src/` + `scripts/`,
    excluding `tests/`): **no production code imports either module [AS OF THE ROW'S WRITING — see the
    box above].** The only hits are
    `src/inference/contamination.py`'s own, unrelated `cross_model_disagreement` (same word,
    different function), a docstring in `src/viz/figures.py:536`, a comment in
    `scripts/analyze_campaign.py:4996`, and a docstring in `scripts/run_campaign_cluster.py:337`.
    The modules and their unit tests are real and pass; nothing calls them.
    **Why this is load-bearing, not housekeeping:** `config/preregistration.yaml`
    `synthesis_exactness.pooled_bound` registers the 90 % seed-block-bootstrap CI on the pooled
    (dist − scalar) CVaR-5% difference as *"the registered cross-model bounded-effect statement"*
    (R86); `synthesis.permutation_test` registers the joint per-seed sign-flip test; and **R101
    reframed the headline itself around "the POOLED cross-model bounded effect"**, with registry
    row 33 above resting the generalization tier on exactly these statistics. So the pipeline as it
    stands cannot produce a registered headline component.
    **Precedent — this is a repeat of a known failure mode:** Amendment R16 fixed precisely this for
    `h2_conjunction` ("implemented and unit-tested but previously unwired, so the documented headline
    test never actually ran"). A unit-tested module is not a wired one.
    **Close it one of two ways, and record which:** (a) wire the synthesis into
    `scripts/analyze_campaign.py` (assemble per-leg results via
    `leg_aggregate.leg_results_for_synthesis`, then `sign_count` / `permutation_test` /
    `pooled_bound` / `pair_did` / `leg_family_bh`) and add an end-to-end test that FAILS if the call
    is removed; or (b) amend the register to withdraw the pooled-bound claim and restate the
    generalization tier in terms of what is actually computed. Silently shipping neither is the one
    unacceptable outcome.
    **Also check when closing:** `leg_aggregate.py:57-58,91` builds a **per-period, ddof=1** Sharpe
    and compares its mean to `floor_sharpe`, while the T0 floor used elsewhere
    (`src/inference/bootstrap.py:309-314`, `benchmark_floor`) is **annualised, ddof=0**. If the real
    T0 floor is passed in at wiring time, every leg would fail by a factor of about √252. This is a
    latent unit trap that only bites on wiring — fix it in the same change.

## The FZ0/DM backtest does not corroborate H2-Tail (2026-07-26 deep review, loop 4 — verified; PREREGISTRATION §1 H2 already corrected)
35. **Rename `corroborates_h2_tail` and restate the exhibit as a calibration diagnostic.**
    > ✅ **DONE — the rename has landed, with a regression guard (verified first-hand, deep review loop
    > 114, 2026-07-27).** `scripts/analyze_campaign.py:2754` carries the in-place note *"⚠ RENAMED
    > 2026-07-26 (deep review row 35): this was `corroborates_h2_tail`"*, and
    > `tests/test_analyze_mechanism_wiring.py:338-341` asserts `"corroborates_h2_tail" not in leg` — so
    > the misleading key cannot silently return. A repo-wide search over `src/` + `scripts/` finds the
    > old name ONLY in that explanatory comment and that guard. **Left OPEN rather than ticked** (the
    > row also asks that the EXHIBIT be restated as a calibration diagnostic in the write-up, which is
    > prose and therefore Tamer's; the code half is complete). Original analysis preserved below.
    As wired in
    `scripts/analyze_campaign.py`, both (VaR, ES) forecasts are FZ0-scored against ONE series — the
    distributional arm's own test path — while forecast 1 comes from that same arm's pooled
    validation returns and forecast 2 from the comparator's. A strictly consistent scoring rule then
    favours forecast 1 close to automatically: the flag measures **self-prediction across the
    val→test split**, not which arm's tail is less severe, so it can show the arms' distributions
    DIFFER but says nothing about the DIRECTION H2-Tail asserts. `src/inference/es_backtest.py`
    already warns against this exact use in its scope note and points to
    `src.inference.bootstrap.cvar_difference_test` — which the 3-leg CVaR IUT already uses, so the
    tail claim loses nothing by the correction.
    **To close:** (a) rename the key (e.g. `forecast_calibration_favours_dist`) and update every
    reader/renderer; (b) make sure no CH6/CH7 sentence presents it as corroboration of the tail
    result; and (c) if genuine corroboration is wanted, score BOTH forecasts on a neutral common
    series instead. `PREREGISTRATION.md` §1 H2 already carries the dated correction.

## ⛔ THE RATIFIED PRIMARY DECISION RULE HAS NO IMPLEMENTATION (2026-07-26 deep review — top pre-results blocker)
36. **Implement the graphical (Bretz–Maurer–Brannath–Posch 2009) α-propagation, or the confirmatory
    inference cannot be computed as registered.**
    > ✅ **NOW IMPLEMENTED — this row's BLOCKER text below is STALE (verified first-hand, deep review
    > loop 113, 2026-07-27).** Re-running this row's own stated search over `src/` + `scripts/` now
    > returns **many** hits, not zero: `src/inference/multiple_testing.py:128
    > graphical_alpha_propagation()` (full sequentially-rejective loop, documented as a shortcut for the
    > closed test, Marcus–Peritz–Gabriel 1976) + `:254 registered_alpha_graph()`;
    > `src/inference/validity_tier.py` assembles the six confirmatory node p-values and runs the ratified
    > rule, stamping `method: graphical_bretz_maurer_brannath_posch_2009` /
    > `registered_rule: bonferroni_weighted_graph`; and `scripts/analyze_campaign.py:5357` wires it as
    > "★ THE RATIFIED PRIMARY DECISION RULE (R108)". It is genuinely tested, not a stub:
    > `tests/test_graphical_alpha.py` (8 tests, incl. order-invariance of the rejected set) —
    > **`test_graphical_alpha` + `test_validity_tier` = 14 passed, `PYTEST_RC=0`** at pinned
    > `--randomly-seed=22`. Leaving the "zero hits / cannot be computed" text uncorrected would tell a
    > reader the registered primary inference is unavailable, which is no longer true and could prompt
    > duplicated work or a needless campaign delay. **Left OPEN rather than marked CLOSED: declaring a
    > binding obligation discharged is Tamer's call, not a reviewer's.** The original assessment is kept
    > verbatim below as the historical record of why the row was raised.
    VERIFIED by repo-wide search over `src/` + `scripts/`
    (excluding tests) for `bretz|graphical|weighted_graph|alpha_graph|alpha_propagat|alpha_recycl`:
    **zero hits [AS OF THE ROW'S WRITING — see the box above].** `src/inference/multiple_testing.py` provides only `benjamini_hochberg` and
    `romano_wolf`. `tests/test_validity_tier.py` only YAML-lints the graph (weights sum, edge sums,
    reachability) — it executes nothing.
    **Why this is now a BLOCKER when it previously was not.** Until 2026-07-26 the tier was
    `registered_pending_supervisor_ratification`, R31 (separate estimands + a reported Bonferroni-over-4
    sensitivity) was the OPERATIVE default, and `analyze_campaign`'s `reject_one_sided_bonferroni` at
    α/4 — described in-code as *"the separate-estimands mirror"* — was exactly right. **Ratification
    (R108) flipped that**: `primary_rule: bonferroni_weighted_graph` is now the PRIMARY confirmatory
    rule and R31 is SUPERSEDED, so the analysis currently implements the superseded stance and cannot
    execute the ratified one. The campaign will run and produce data; the registered primary inference
    could not be computed from it.
    **Ready-to-apply spec.** Add `graphical_alpha_propagation(p, weights, edges, alpha)` to
    `src/inference/multiple_testing.py` implementing the standard sequentially-rejective loop: test each
    node at `w_i·α`; on rejecting node `i`, remove it and propagate its weight along its out-edges
    (`w_j += w_i·g_ij`), re-normalising the surviving graph per Bretz et al. (2009) eq. (2)–(3); repeat
    until no further rejection. Feed it the six node p-values already produced (N1/N2 = the H2 IUT max-p
    per family; N3 = h3; N4 = the 4-comparator IUT max-p; N5 = the structure test; N6 = the 11-leg canon
    IUT max-p) with `initial_weights` and `edges` read from
    `config/preregistration.yaml: inference.validity_tier`. **Do NOT hardcode the graph** — read it, so
    the executed rule cannot drift from the registered one (the same not-in-the-hash-so-assert lesson as
    the arm roster / h1_baselines / confirmatory_author guards).
    **Tests that would have caught this:** (a) an end-to-end test asserting the confirmatory verdict is
    produced BY the graph (fails if the call is removed); (b) a known-answer test against a hand-worked
    2–3 node example; (c) a test that the executed graph equals the registered one.
    **Also unimplemented:** `sensitivity: [romano_wolf_graph, bh_fdr_over_m6]` — plain `romano_wolf`
    exists (a stepdown), but not its GRAPH variant. Lower priority: it is a sensitivity, not the gate.
    **Keep** the Bonferroni-over-4 computation — as a *disclosed sensitivity* it is still valuable, and
    the ratification pack notes Bonferroni is the weakest member of the family the graph generalises.

## ⛔ THE PRE-COMMITTED EQUAL-*k* SENSITIVITY HAS NO IMPLEMENTATION — and §56 just made it load-bearing (2026-07-31)

37. **Implement the equal-*k* sensitivity analysis, and report per-arm accepted-candidate counts
    beside every H2 contrast.**

    **Registered** at §9 item 4, reaffirmed at **§26.3** and again at **§42** — *"the equal-*k*
    sensitivity analysis registered at §9 item 4 is not a formality — it will carry real weight."*
    **Verified 2026-07-31: it exists in NO code.** `grep -rniE "equal.k" src/ scripts/ tests/`
    returns nothing; it is not in `PREREGISTRATION.md`; and it was **not in this registry**, so the
    pre-submission sweep that "verifies zero open rows" could never have caught it. That is exactly
    the **R106 failure mode** — a ratified decision recorded as neither done nor pending, invisible to
    every gate — and the same shape as row 36 above.

    **Why it is now load-bearing rather than a formality (record §56).** The `-p` ladder (§54) starved
    the three CONTROL arms, and `PREREGISTRATION.md` line 94 makes each H2 co-primary a **3-leg
    intersection–union test** whose comparators are `scalar`, **`placebo`** and **`scalar_cvar5`** —
    two of the three are the starved arms. Measured against the registered 30-candidate budget:

    | arm | role | % of budget | pool vs `distributional` |
    |---|---|---|---|
    | `distributional` | treatment | 82 % | — |
    | `scalar` | treatment | 79 % | 1.04× |
    | `placebo` | **CONTROL** | **40 %** | **2.08× smaller** |
    | `scalar_cvar5` | **CONTROL** | **36 %** | **2.27× smaller** |

    Each arm fields `max(val_fitness)` over its accepted candidates and **E[max] rises with n**, so a
    halved pool fields a systematically weaker comparator and makes that IUT leg **easier to reject
    than the design intends — biased TOWARD a false positive for our own hypothesis.** If the controls
    do not fully catch up before the exogenous stop, **this sensitivity is the ONLY pre-registered
    defence against that criticism**, and a reviewer will ask for it by name.

    **What it must do, minimally:** truncate every arm to a common *k* (the smallest arm's accepted
    count, and a small ladder of *k* values around it), re-select each arm's winner by
    `max(val_fitness)` within the truncated pool, re-run both co-primary IUTs, and report the verdict
    alongside the headline — not in an appendix. Truncation must be **pre-committed and
    effect-blind**: take the FIRST *k* accepted candidates in generation order, never the best *k*,
    which would be selection on the outcome.

    **Also required by the same obligation and equally unimplemented:** the per-arm accepted-candidate
    counts must appear **beside every H2 contrast** in the results, so a reader sees the pool each
    maximum was taken over without having to ask.

    **Live monitoring is in place meanwhile:** `docs/ops/cycle.py` now reports the per-arm pools and
    raises attention past a 1.5× spread (live 2.56×, an upper bound — see the denominator note in the
    code), and `docs/ops/watch/ARM_BASELINE.json` snapshots the 2026-07-31 counts so the controls'
    catch-up can be measured rather than assumed.

## Dr Okhrati's supervision feedback, 2026-07-31 (verbatim asks, recorded same day)

> Tamer's report of the conversation: *"it would be important to see the details, like graphs and
> etc to show how the results change with increasing seeds, so for example 1,2,3,4,5,6,7,8,9 and
> etc up to the final seed"* · *"logic and reasoning of the results, how we got them, why this or
> that happened"* · *"explaining final output, what could be done in future to get more expected
> result"* · *"it's far more interesting to get a very good comprehensive understanding of what
> happened"* · *"the experimental setup must be very rigorous"* · *"you get the output, and you can
> explain the output that you got, and why it happened"*.

38. **★ THE SEED-TRAJECTORY EXHIBIT (new; NO existing figure covers it).** A running-estimate curve
    per unit: the statistic (Sharpe IQM, CVaR-5% IQM, and the H2 paired difference) recomputed on
    the first n seeds for n = 1..N, with a widening/narrowing CI band, plotted against n. One panel
    per co-primary; the H2 contrast panel carries the SESOI band so a reader sees the estimate
    entering (or not entering) the equivalence margin as n grows.

    **Why it is cheap and exact:** the ladder is CUMULATIVE and CRN-paired, so every prefix
    [0..n) is a valid complete study; the curve is a pure post-hoc recomputation over records that
    already exist. No extra compute, no extra spend, no design change.

    **Why it is scientifically load-bearing, not decoration — MEASURED 2026-07-31 on the 11-member
    canon at n=30:** `return_minus_cvar` reads **-0.215 at n=10** and **-0.364 at n=30** (a ~3-SE
    move), and `raw_return` is the BEST of the ten losers at n=5 (-0.108) but third-WORST at n=30
    (-0.289). **The rank order is not stable at small n.** The curve is therefore the direct visual
    justification of the whole assurance ladder and of sigma_seed = 0.244 dominating the effect
    we are trying to resolve — i.e. it answers "why so many seeds?" with a picture instead of an
    assertion. Ordering must follow the REGISTERED seed order (never sorted), or the curve becomes
    a selection artifact.

    Lands as: `src/viz/figures.py::seed_trajectory` + a CH6 figure + one CH4 sentence.

39. **THE "WHY IT HAPPENED" NARRATIVE SPINE (CH6/CH7).** Okhrati's central ask: the output is not
    the deliverable, the EXPLANATION of the output is. Every headline number gets: what we
    observed -> the mechanism instrument that speaks to it (SQ1 responsiveness / SQ2 mediation /
    SQ3 specificity) -> which of the five rival accounts A1-A5 it supports -> what would have to
    be true for the alternative reading. Much of this exists in the kernel; the obligation is that
    it is written as a CONTINUOUS ARGUMENT in the body, not as separate report-only exhibits.

40. **"WHAT WOULD GET A MORE EXPECTED RESULT" (CH7, named subsection).** Not generic future work:
    a costed, prioritised list of the specific interventions the mechanism analysis implies -
    legible re-rendering, the guided-compare instruction, the R96 threshold measurement, a
    turnover-constrained agent, a larger fed-delta regime - each stated with the account it would
    discriminate and the evidence that motivates it.

41. **THE TURNOVER FINDING AS A WORKED "WHY" EXAMPLE (CH6).** The 2026-07-31 canon result is the
    template Okhrati is asking for: ten of eleven human rewards LOSE money, the one that prices
    trading returns +1.154 Sharpe, and the mechanism is measured (78-91% of book/day vs 0.8%),
    not inferred. Write it as the worked example of output -> explanation.

42. **RFC-8259-COMPLIANT JSON IN THE PUBLIC DEPOSIT (A12 / the reproducibility layer).**
    *Found 2026-07-31 by independent invariant verification; record §69.* **360 archive
    `record.json` files contain a bare `NaN` token, which is NOT valid JSON** (RFC 8259 admits no
    `NaN`/`Infinity`). Python's `json.load` accepts it by default, so our own pipeline never
    notices — but a STRICT parser rejects the file outright, verified with
    `json.loads(..., parse_constant=raise)`. Go's `encoding/json`, Rust `serde_json`, JavaScript
    `JSON.parse` and R `jsonlite` all refuse a bare `NaN`.

    **Scope, measured exactly:** **29,130 individual non-finite tokens** across **690 field-sites**, in **two fields only** —
    `metrics.train_curve.return[]` (360 files) and `metrics.val_fitness` (330 files, the 11
    baselines x 30 seeds where a *validation* fitness is simply inapplicable on the sealed-test
    lane). **All 360 are on the TEST lane; ZERO on `search/` and ZERO on `frozen/`, so the
    confirmatory search archive is already standards-compliant.** No `Infinity` anywhere.

    **This is NOT a science defect** — no reported number is wrong; both fields are
    inapplicable-or-diagnostic. **It IS a reproducibility defect**, and reproducibility is
    Stefan's criterion #3 ("THE critical point") and Tamer's #1: the artifact is meant to be
    re-analysable BY ANYONE, and a replicator working in R, Go, Rust or JavaScript hits a hard
    parse failure on 360 files before reaching any science.

    **Obligation:** the public deposit and the reproducibility layer must emit RFC-8259-compliant
    JSON — `null` for an inapplicable or non-finite value — and the repro checklist must state the
    convention so a consumer knows `null` means "not applicable / not finite" rather than zero.
    **Do NOT fix this by relaunching drivers** (disproportionate, and `pull_archive` re-mirrors the
    remote copy anyway): it is a PACKAGING-time transformation, applied where the archive is
    exported. Validator kept at `docs/ops/json_standards_check.py`.

43. **PARTITION HIGH-FALLBACK RECORDS BEFORE REPORTING ANY PER-MODEL RELIABILITY NUMBER.**
    *Found 2026-07-31 by the deep results audit; record §71.5.* Of the **18** records with a
    safe-default fallback >= 5 %, **11 are the D17 RECIPROCAL class** (8 x **49.983 % = 1/2**,
    1 x 33.333 % = 1/3, 1 x 9.997 % = 1/10) and only **7 are genuinely broken rewards**. §37
    established that a D17 record is our HARNESS trapping an otherwise-working reward — the
    safe-default clears the reward's own state, pinning a stateful reward with a cold-start branch
    into a limit cycle of period *(calls to leave cold start) + 1*, which is why the fraction lands
    on a reciprocal — and that such a record is **biased AGAINST its own model**.

    **Consequence: 61 % of "this model wrote a broken reward" evidence is our instrument, not the
    model.** §51's capability gradient and the R115 breach counts are therefore contaminated in the
    majority of cases, and **qwen3.6-27b is the most affected (4 of the 8 reciprocal records)** —
    the model whose measured reject rate (8.8 %) is already well BELOW its registered ~17 % baseline.

    **Obligation:** before any per-model authoring-reliability figure is written, classify each
    high-fallback record as **D17-reciprocal** (fallback within 5e-4 of 1/k for small k) or
    **genuinely broken**, report the split, and exclude the D17 class from claims about model
    capability. The test is exact, mechanical and cheap. Without it the gradient OVERSTATES the
    weakness of every model the harness happened to trap. Tool: `docs/ops/deep_results_3.py`.

44. **REPORT THE WINNER-SEPARATION DISTRIBUTION AS THE QUANTITATIVE ANSWER TO "WHY SO MANY SEEDS?"**
    *Found 2026-07-31; record §71.4.* Across 54 line-arm pools, the ratio of the best candidate's
    validation fitness to the second best ranges from **1.00 to 396**, median **1.41**. In the
    tightest pools the top two differ by **0.3 %** (`haiku/scalar`: 0.27769 vs 0.27686) — far inside
    sigma_seed = 0.244 (confirmed live at 0.25). **Which candidate is "the winner" is, in those
    pools, effectively arbitrary.**

    This is NOT a defect; it is the empirical justification for the design. It is exactly why the
    confirmatory comparison does not rest on the single-seed validation winner but re-scores winners
    across the **30 -> 568 seed ladder on sealed data**. Reported as a distribution it becomes a
    measured answer to the question a referee will ask, sitting alongside row 38's seed-trajectory
    exhibit (Okhrati's D2). Discovered by us and reported is a rigour exhibit; discovered by a
    referee is a wound. Tool: `docs/ops/deep_results_3.py`.

    **⚠ THRESHOLD CLARIFICATION (2026-07-31, record 73.6).** The 61 % figure above uses a **>= 5 %**
    fallback screen. **R115's actual eligibility floor is >= 10 %**, and at that floor the split is
    **10 reciprocal / 3 genuinely broken = 13 total, i.e. 77 % harness-trapped**. Both are correct
    answers to different questions; **the one that governs eligibility is the 10 % screen**. So the
    obligation is STRONGER than first stated: of the breaches R115 actually acts on, **roughly three
    quarters are our own harness**, and only **three records in the entire campaign** are genuinely
    broken rewards. State the screen explicitly whenever either figure is quoted.
