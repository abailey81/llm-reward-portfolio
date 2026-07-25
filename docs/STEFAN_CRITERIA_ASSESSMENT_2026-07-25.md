# Stefan's 5 success criteria — unbiased assessment + fix plan (2026-07-25)

**Trigger:** Stefan (industrial supervisor) named five criteria for a successful paper and asked for a
deep, strict, *unbiased* assessment of whether the dissertation addresses all of them. Five independent
skeptical auditors (one per criterion, instructed adversarially — "assume we FAIL until proven") read
the actual paper/config/code first-hand; every finding below cites a file:line an auditor opened. The
criteria are now codified as a binding evaluation lens in `CLAUDE.md` (★★★ STEFAN'S 5 SUCCESS CRITERIA).

## Bottom line (honest)
The **substance, identification, and honesty are genuinely distinction-grade** — the core idea is sound,
the endogeneity is disclosed not hidden, and the arms cleanly isolate the feedback content. But we are
**not yet at the 95% "unquestionable" standard**, and the UCL rubric caps the mark at the *weakest*
dimension. The two weakest are exactly the two Stefan weights most: **reproducibility (his "critical"
one — experiment layer WEAK)** and **non-fragility (both load-bearing legs are power-soft)**. Every gap
is addressable **without changing the science** — framing, disclosure, a handful of code fixes (mostly
DONE below), and a few justifications we simply have not written down yet.

## Scorecard

| # | Stefan criterion | verdict | biggest gap(s) |
|---|---|---|---|
| 1 | Real gap | **STRONG** | concurrent `gallego2026beyondscalar` coined "feedback engineering"; novelty≠significance; the 2 control arms Stefan flagged (H1, H4) are inferentially demoted to report-only |
| 2 | Principled / elegant / non-fragile | **ADEQUATE — fragile headline** | both load-bearing legs power-soft; apparatus too complex for a non-specialist 2nd marker |
| 3 | Reproducibility (CRITICAL) | analysis STRONG · protocol ADEQUATE · **experiment WEAK** | "self-hosted leg" doesn't exist; R85 round-trip evidence was fictional (**FIXED**); pins not round-trip-verified (**FIXED**); freeze didn't bind leg pin values (**hf_pin FIXED**) |
| 4 | Sound ideas + justify everything | idea STRONG · **justification ADEQUATE** | SESOI set by fiat; K=5 below Eureka's floor; 2/6 tail components asserted; the freeze protects the backdrop, not the headline |
| 5 | Clarity of what's measured | **ADEQUATE → WEAK** | "CVaR-5%"=3 estimators; robust_skew mislabeled; selection DSR is a proxy not the canonical DSR; mechanism X/M unpinned |

---

## Criterion 1 — Real gap (STRONG, with flanks)
Confirmed strengths: the nearest-neighbour map is exhaustive and each neighbour distinguished by a
broken conjunct (`paper/CH2_related_work.md:78-135`; `docs/LITERATURE_INTEGRATION_MAP.md:304-328`); the
gap is data-motivated (the tail EDA crossover, `paper/CH4_methods.md:27-34`); the arms bind each control
to a named threat (`paper/CH4_methods.md:282-290`). Gaps:
- **[MAJOR] `gallego2026beyondscalar` (concurrent) coined "feedback engineering"** and ran the same
  sparse-vs-dense feedback manipulation (`paper/CH2_related_work.md:55-65`; `paper/refs.bib:851-868`).
  Our deltas are real (reward-of-a-fixed-agent, tail axis, placebo/structure controls, equivalence
  inference) but the headline leans on a concurrently-coined axis → lead with the deltas, cite gallego
  as the concurrent namer, in the abstract.
- **[MAJOR] novelty ≠ significance** — the four-way conjunction is "open" partly by specificity; the
  *significance* case (why the empty cell matters) is softer than the novelty case.
- **[MAJOR — the direct Stefan hit] the 2 arms he called critical are demoted** — H1 (LLM vs
  hand-designed) is report-only/"snooped-descriptive" (`PREREGISTRATION.md:26-36`); H4 (vs
  random/bayes) is secondary (`config/preregistration.yaml:139-140`). The comparison that most
  literally shows the reward-function effect is the weakest-inferential leg.
- [MINOR] "first factorial dissection" over-reaches (encoding axis is report-only, `CH1:143-145`).
- [MINOR] `docs/MODEL_SWEEP_2026-07-20_v2.md` stale (says Opus 4.8 / 9 models; actual Opus 5 / 11) —
  mark SUPERSEDED-by-R95/R101/R102.

Arms vs Stefan's advice: the **5 LLM/design arms are genuinely differentiated (SATISFIED)**; the 2
control arms are structurally present but demoted → **re-elevate H1 to a validation-selected winner, or
explicitly defend the "mechanism supersedes effect" prioritization in CH4/CH7.**

## Criterion 2 — Principled / elegant / non-fragile (ADEQUATE, fragile headline)
Confirmed strengths: endogeneity disclosed everywhere (`src/feedback/measurement.py:16-26`); the
three-way fed/select/test decoupling (`paper/CH4_methods.md:204-216`); the Blackwell-envelope +
threat→defence matrix (`paper/02_CHAPTER_theory.md:83-108`). Ranked fragilities:
- **[F1 MAJOR] the equivalence headline is likely unreachable** — σ_D=0.369 vs SESOI=0.05; MDE@30≈0.120;
  Sharpe-leg TOST needs n≈403 but the common reachable rung is ~100-189 (`docs/SEED_DECISION_2026-07-05.md:32-38`;
  `config/preregistration.yaml:281,290`) → degrades to "absence of evidence." Disclosed (`CH4:258-273`).
- **[F2 MAJOR] the mechanism study (the real originality) carries zero confirmatory severity + is
  under-powered** — SQ1-3 report-only (`PREREGISTRATION.md:119`); SQ1 is a Spearman over n=30
  (`src/inference/responsiveness.py:76-127`); the positive-control is an optional ~$3 probe
  (`config/preregistration.yaml:354`).
- **[F3 MAJOR, suspected] the gating tail test carries seed variance only** — σ_D(cvar_05)=0.0015 is
  tiny because every seed trades the ONE 2020-2026 path (`APPENDIX_B:51`); the path-aware FZ0/DM
  backtest is non-gating (`CH4:248-273`). **VERIFY** whether any gating tail statistic resamples
  time-blocks.
- **[F4 MAJOR, communication] the elegant core is wrapped in an apparatus a non-specialist marker will
  struggle with** (7 arms, 2 IUTs, m=6, 3 SQs, 5 fingerprints×8 instruments, 7-rung ladder, 10 legs,
  R11-R103); the A1-A5 fingerprint lacks a sharp decision threshold (`PREREGISTRATION.md:200-201`) →
  "storytelling dressed as pre-registration" risk. Give it R87's falsifiable-signature standard.
- [F5 MED, suspected] SQ1 responsiveness may have a shared-driver/autocorrelation confound — **VERIFY**
  the X↔M pairing before banking.
- [F6 MINOR] `assert_fixed_agent_across_arms` is test-only, not a runtime detector (`src/arms/factory.py:259-274`).
- [F7 MINOR] symbol collision on "K" (search width 5 vs a decoding knob 16 in `docs/DESIGN_DETERMINATION.md:18`).

## Criterion 3 — Reproducibility (analysis STRONG · protocol ADEQUATE · experiment WEAK) — the critical one
Confirmed guarantees: exact-pin `requirements.lock`; determinism knobs (`src/utils/seeding.py:38-63`);
CI freeze-drift guard (`.github/workflows/ci.yml:22-27`); replay-from-archive (`src/llm/client.py`).
Ranked holes (★ = FIXED this session under R103):
- **[HOLE 1 CRITICAL] the "self-hosted leg" that Layer 3 rests on does not exist** —
  `docs/V2_WRITE_TIME_REGISTRY.md:72` records "(c) no self-hosted leg." Every open leg routes through
  OpenRouter fp8 (transient). → **Part B decision:** restore one self-hosted leg OR strike "self-hosted"
  from the three-layer claim everywhere and reframe Layer 3 as "re-hostable weights, replication not
  bit-reproduction."
- **★ [HOLE 2 CRITICAL] the R85 reasoning-pin round-trip evidence was FICTIONAL** — `client.py` never
  captured `reasoning_tokens`, so a silently-ignored pin was indistinguishable from a live one (this is
  *why* the thinking-mode bug was invisible). **FIXED:** client.py now captures
  `usage.completion_tokens_details.reasoning_tokens`; leg_gates computes a direction-aware verdict.
- **[HOLE 3 MAJOR] unpinned thinking + low max_tokens on gemini/kimi → EMPTY authored code.** **FIXED**
  (R103): qwen `reasoning:{enabled:false}` (0.0/0.4→1.0), gemini cap 2048→8192 (0.1→1.0); kimi held.
- **★ [HOLE 4 MAJOR] provider/quant pins not round-trip verified** — **FIXED:** client.py now archives
  `response.provider` per call.
- **★ [HOLE 5 MAJOR] the freeze didn't bind the executed leg-pin values** — **FIXED (hf_pin):**
  `assert_leg_roster_match` now binds the hf_pin COMMIT (the permanence anchor) + a drift test. (The
  reasoning *value* is deliberately not static-bound — the runtime round-trip is a stronger guarantee.)
- **[HOLE 6 MAJOR, suspected] the confirmatory author is a dateless closed snapshot** (`claude-opus-5`).
  → **Part B:** pin a dated snapshot if one exists, else archive served_model+request_id at first call
  and disclose deprecation exposure.
- **[HOLE 7 MAJOR] the paper's reproducibility limitations are v1-era** (`APPENDIX_B §B.6/B.7`) — omit
  every v2 hole. → **Part B:** add a v2 repro-limitations block.
- [HOLE 8 MINOR] compute-substrate disclosure self-contradicts (README Myriad vs MODEL_CARD/CHECKLIST
  "laptop-only") — reconcile to Myriad-primary/laptop-fallback.
- [HOLE 9 MINOR] "byte-level tamper-evidence" overclaims (plain JSONL append) — soften or add a manifest.
- [HOLE 10] everything is currently UNFROZEN (legitimate pre-data; the anchor doesn't exist until GO).

## Criterion 4 — Sound ideas + everything justified (idea STRONG · justification ADEQUATE)
Well-justified: B*=400k (measured knee, `CH4:107-117`); the seed ladder (σ_D pilot fired the >0.10
trigger, `PREREGISTRATION.md:346-367`); DSR tail-blind selection (`CH4:206-216`); SAC-fixed/TQC-secondary
(structural argument, `02_CHAPTER_theory.md:256-270`); construct validity (prompts verified tail-neutral
first-hand). Under-justified (the gaps):
- **[MAJOR] SESOI=0.05 set by FIAT** — the equivalence linchpin, no economic/decision-theoretic
  derivation (`DESIGN_DETERMINATION.md:15`; `PREREGISTRATION.md:671-677`). → **Part B:** anchor it to a
  transaction-cost breakeven at the 10bps headline cost.
- **[MAJOR] K=5 below Eureka's K=16 executability floor** — budget arithmetic, not a search-adequacy
  argument (`CAMPAIGN_DESIGN…:162-163`). → report the first-gen executable rate as a pre-registered
  adequacy check.
- **[MAJOR] 2 of 6 fed tail components asserted** — `left_tail_mass` k=2.0σ and the Bowley-skew anchors
  have no derivation (`02_CHAPTER_theory.md:202-203`; `PREREGISTRATION.md:305`). → justify or label
  "engineering summary statistics."
- [MAJOR/MINOR] the α-grid {1,5,10,25}% is acknowledged-arbitrary with no sensitivity run
  (`distributional_feedback_schema.md:61`) → add a cheap grid-robustness exhibit.
- [MAJOR sub-claim] the capability gradient rests on 2 of 10 SWE-bench anchors (`PREREGISTRATION.md:308,320`)
  → foreground the within-family pair DiDs; label the cross-family gradient descriptive.
- **[conceptual MAJOR] the freeze protects the backdrop, not the headline** — H2-RA is a predicted TIE
  under λ=0 (`PREREGISTRATION.md:79-81`); the mechanism instruments are report-only. → own it in one
  paragraph.

## Criterion 5 — Clarity of what's measured (ADEQUATE → WEAK)
Well-defined: CVaR sign convention (`02_CHAPTER_theory.md:165-169`); endogeneity of the fed tail;
FZ0 loss (`es_backtest.py:86`). Ambiguities:
- **[MAJOR] `robust_skew`** — 4 names, mislabeled "left-tail skew" (it's symmetric Bowley), sign only in
  code (`measurement.py:452-467`; the `NOMENCLATURE.md:51-52` TODO is open) → rename + add to a
  Conventions box.
- **[MAJOR] "CVaR-5%" denotes 3 estimators** (fed EVT/GPD vs tested empirical vs FZ0's different
  empirical) → one estimator table.
- **[MAJOR] the fed cvar_05 silently switches EVT↔empirical per candidate** and the methods omit the
  `α>F_u` trigger (`measurement.py:340-363` vs `CH4:140-142`) → disclose + count the paths.
- **[MAJOR] the selection fitness is a within-series-variance DSR PROXY, not the canonical DSR the paper
  cites** (`deflated_sharpe.py:180-192`; `fitness.py:59-66`) → state it in §4.6.
- **[MAJOR] the mechanism X and M are never pinned** (only "e.g.", `responsiveness.py:3-6`) → freeze the
  exact scalars in the prereg.
- [MAJOR] the equivalence machinery spans DSR/Sharpe/CVaR units in one paragraph → an
  estimand→statistic→unit→margin table.
- [MINOR] left_tail_mass threshold; H2-RA Sharpe def; λ-penalty sign; DSR=0.83 is a probability; "AST"
  count is regex; EVT sample-size wording.

---

## What was DONE this session (R103 — dated pre-freeze amendment, fully verified)
Part A code/repro fixes (Tamer's chosen priority), all VERIFIED (freeze --check green + tests green):
1. **client.py** — captures `reasoning_tokens` + `response.provider` into every provenance record
   (HOLE 2/4). 121 client tests green.
2. **leg_gates.py** — direction-aware pin round-trip verdict (ENABLE+0 tokens = FICTIONAL; DISABLE+>0 =
   IGNORED) + a 0.5 compliance floor (0.0 can no longer be stamped "pass"). +3 tests.
3. **legs.yaml + preregistration.yaml + PREREGISTRATION.md** — R103: qwen `reasoning:{enabled:false}`
   (0.0/0.4→1.0), gemini cap 2048→8192 (0.1→1.0); registered `output_cap_tokens`/`reasoning_pin`
   reconciled; `assert_leg_roster_match` passes.
4. **freeze.py** — binds the hf_pin COMMIT (the permanence anchor, HOLE 5) + a drift unit test.
- **All legs verified fixable to 1.0:** qwen9 0.0→1.0, qwen27 0.4→1.0, gemini 0.1→1.0, kimi 0.5→1.0.

## Part B — open decisions for Tamer (framing/design, not code)
- **kimi-k3 cost:** 0.5 (8192) → 1.0 (16384) but doubles the priciest leg's cost (~$10-22) against the
  $30 advisory ceiling. Decision: bump / keep 0.5 / middle budget.
- **Headline reframe:** lead with the tail leg + mechanism + bounded-effect CI; state the Sharpe leg as
  conditionally inconclusive (F1, conceptual-4).
- **Demoted arms:** re-elevate H1 to a validation-selected winner OR explicitly defend the prioritization
  (Criterion-1 Stefan hit).
- **SESOI:** derive it from a transaction-cost breakeven instead of asserting it (Criterion-4).
- **Self-hosted leg:** restore one OR strike "self-hosted" from the reproducibility claim (HOLE 1).
- **v2 repro-limitations block + doc reconciliations** (HOLE 7/8; MODEL_SWEEP superseded).

## Part C — verify before banking (suspected findings)
- F3: does ANY gating tail statistic resample time-blocks, or only seeds?
- F5: is SQ1 responsiveness confounded by a shared driver / autocorrelation (the X↔M pairing)?
- Criterion-5: the real-data `robust_skew` sign (≈+0.21 per project notes — re-measure).
