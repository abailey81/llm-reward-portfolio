# V2 MASTER PLAN — 2026-07-20 → submission (the ultraplan)

> The complete execution plan for the v2 design (post-UNFREEZE, ADR-059/R78), integrating: the
> locked 7-model roster (`MODEL_SWEEP_2026-07-20_v2.md` + addendum), the NatWest + Okhrati
> feedback (CLAUDE.md, both blocks), the $30 spend ceiling, the pipelined write-while-rungs-land
> strategy (Tamer's plan), and every gate/fallback decided in the 2026-07-20 design session.
> Deadline: **1 Sep 2026**; submission target **Aug 28–29**.

> **⚠ LIVING-PLAN STATUS (2026-07-21):** build steps 1–5 are DONE + committed (legs.yaml
> `ceadd54` · advisory ledger `41e9a1e` · leg transport `99d2901` · 21-check gate w/ leg-roster
> guard `aa910eb` · synthesis module w/ the pooled-mean refinement `0464b4f`). SUPERSESSIONS by
> Tamer's instructions: the spend ceiling is ADVISORY (R83 — tracked+warned, never refused); the
> FREEZE + LAUNCH have NO scheduled date — they happen ONLY on his explicit word (dates below are
> planning references, not triggers); the final roster is 9 legs + Opus incl. SONNET 4.6 (replaced
> Hy3; the closed 3-ladder + pilot bridge) and GEMINI 3.5 FLASH (seat-10 stretch). The executed
> truth for the roster is `config/legs.yaml` == `model_suite` (gate-verified, n=9).

## 0. The design being executed (one paragraph of record)

One frozen question (does feedback content change the reward code an LLM writes, and does it
transmit?); ONE frontier confirmatory author (Opus 4.8) under the full v1 rigor (7 arms, m=6,
co-primary IUTs, SESOI ±0.05, floor-30 → rung-279 expectation, exogenous stop); NINE replication
legs (FINAL roster, gate-verified vs `config/legs.yaml`): five open-weight — DeepSeek V4-Pro·MIT
[contamination gate; GLM absorbs on failure], GLM-5.2·MIT, Qwen3.6-27B + Qwen3.5-9B·Apache [the
open capability pair — SiliconFlow fp8, same provider+quant], Nemotron-3-Super·NVIDIA-OML
[data-transparency seat] — plus four closed tiers: Haiku 4.5 + **Sonnet 4.6** [the closed family
LADDER with Opus — 3 points; Sonnet = the PILOT BRIDGE (the prototype's author re-tested under
the frozen design; replaced Hy3, which moved to M2)], GPT-5.6 Luna [effort-low + 2k cap], and
**Gemini 3.5 Flash** [seat-10 stretch, FIRST-TO-TRUNCATE — completes big-three closed coverage]
— 10 full-loop models total; floor-30 seeds each, byte-identical prompts, unified
prompt-variation diversity, pinned providers/quant/reasoning-modes, priority-queued behind the
core (DeepSeek → GLM → Qwen27 → Qwen9 → Haiku → Sonnet → Luna → Nemotron → Gemini),
calendar-gated **2026-08-14T23:59Z**; the M2 reading-link survey (25 exact models incl. both
within-family ladders) post-headline; a dependence-aware pre-registered synthesis (descriptive
sign count + seed-block permutation test + capability regression on a pre-declared external
anchor, M2 score secondary); per-model authoring-reliability + code-taxonomy outputs; study-level
success metrics; a **$30 ADVISORY planning ceiling** (R83: per-call ledger, warned, never refused — reported in full); two keys
only (Anthropic + OpenRouter). All extensions truncation-safe behind the core; the tier-30 floor
banks the degree regardless.

## 1. Phase plan (day-by-day, with owners)

### Phase 0 — TONIGHT (Jul 20): sign-off + drafts  [Tamer + me]
- **Tamer: sign off the package** — DONE 2026-07-20 ("implement everything"): roster 10 + M2 25 + full ladder under the exogenous rule + advisory $30 + Aug-14 leg gate.
- Me: draft (a) the Okhrati email (pre-data revision, v2 shape, sign-off request, time-box
  noted, default-proceed offered under his standing full-permissions grant — Tamer edits/sends);
  (b) the NatWest response brief (point-by-point: adopted/answered/declined-with-reason + the
  15/15 survey table + the success-metrics page + the $30 line); (c) playbook + cursor updates.

### Phase 1 — Jul 21–22: gates closed + prereg-v2 drafted + build starts  [me; 2 Tamer items]
- **Tamer (5 min each): send the Okhrati email; top up OpenRouter ~$25** (Anthropic balance
  ≥$30 confirmed at freeze).
- Run ALL pre-freeze gates so the frozen roster is settled, not conditional:
  6× behavioural contamination screens + 6× author smokes (~$1 total) + license-file glances
  (Hy3 LICENSE; Nemotron OML text archived) + the 10-call format-compliance baseline per model.
  Verdicts archived; DeepSeek fail ⇒ GLM absorbs seat 1 (6 legs, pre-declared).
- **R79**: the conservative format-robustness micro-pass on the two prompt files (output-format
  instruction made maximally model-agnostic; NO semantic/tail change; tail-neutrality gate
  re-run).
- Draft prereg-v2: PREREGISTRATION.md v2 sections (model suite + pins; synthesis spec incl. the
  permutation test and its dependence rationale; success metrics; spend ceiling + queue + leg
  gate; capability anchors) + yaml mirrors (**R80/R81**) + ADR-060 (the v2 design record) +
  `config/m2_models.yaml` rewrite (25 exact + extras + inclusion rule).
- Build start: per-leg llm config blocks; OpenRouter transport params (provider `only` +
  `allow_fallbacks:false`, `quantizations`, reasoning-mode pin, seed param where supported;
  `~latest` hard-reject); per-leg root-suffix namespacing + ledger/resume.

### Phase 2 — Jul 23–25: build complete + green + dry-runs  [me]
- Cross-leg synthesis module (seed-block permutation test) + reliability-metrics extraction +
  per-model taxonomy grouping — with tests.
- Fallback provider orders per leg (catalog-churn insurance) recorded in config.
- Runbook v2 (leg queue §, gates, monitoring per leg, spend tracking vs the ceiling).
- Full suite green; ruff clean; EXACT launch lines dry-run on real gold (Opus core + one leg);
  cluster code sync + marker verified.

### Phase 3 — FREEZE v2 + LAUNCH — ONLY on Tamer's explicit word (NO scheduled date; his 2026-07-21 instruction)
- Okhrati response in hand (or Tamer invokes default-proceed).
- `freeze.py` → v2 canonical hash; tag `prereg-v2.0`; bundle; gate re-verified green; DECISION_LOG.
- Balances confirmed; supervisor + campaign monitor + sentinel armed; **C0 canary** (hard-stops
  pre-spend); **LAUNCH the Opus core** per runbook. Legs' authoring begins interleaved
  (cheap, generation-by-generation) behind the core's cluster priority.

### Phase 4 — Jul 28 → Aug 14: campaign + pipelined writing  [cluster + me + Tamer]
- **Writing starts immediately** (needs no results): CH1–CH5 depth-pass; the two deferred
  write-time items — theory §3.3 nested-garbling rewrite + the Mayo/severity CH1→CH7 move; CH2
  gains the 15/15 survey table; CH4 gains the model-suite + cost + reproducibility sections.
- ~Aug 3: Opus search complete ⇒ **mechanism data complete** ⇒ CH6 mechanism sections draft.
- ~Aug 8: Opus floor-30 banks (bank gate) ⇒ first full CH6 draft (tail verdict + mechanism +
  reliability table); legs complete in queue order; per-leg tables auto-generate.
- Background: Opus ladder 100 → 189 → 279; numbers refresh per rung via the pipeline
  (provisional-labelled; NO confirmatory look).
- **Aug 14 — THE LEG GATE**: completed legs reported; incomplete = truncated-by-calendar;
  synthesis computed. **M2 (25 models, ~$10, ~1 day) runs post-headline.**
- Jul 27 watch: Kimi K3 weights (Stage-2 note only — never mid-flight).

### Phase 5 — Aug 14–22: the single confirmatory look + final writing  [me + Tamer]
- Final rung banks (~Aug 18–20) → **the ONE confirmatory look** (gate + IUTs + TOST + Bayes) →
  final number refresh.
- CH6/CH7 completed (incl. the practitioner checklist + measurement→decision map); word surgery
  to the 10k body (suite detail → appendices); figure/table cross-ref pass; citations gate;
  **mandatory pre-submission novelty-fence sweep**; ethics + AI-disclosure finalized.

### Phase 6 — Aug 22–29: polish + submit  [Tamer]
- 0-warning PDF compile; fresh-agent rubric read-through (author≠reviewer); Okhrati courtesy
  copy; **submit Aug 28–29** (buffer to Sep 1).
- Post-submission: P2 (numeracy/legibility) + P3 (the $30 open suite) paper drafts from
  campaign artifacts; K3/KAT Stage-2 legs if their gates opened.

## 1b. The unified TIER × STAGE × LEG queue (precise compute; added 2026-07-20 night)

**Tiers (E1 ladder, cumulative; marginal cost = 12 units × Δn [7 arms + 4 baselines + H3]):**
30 = distinction floor (600 tr incl. search) · 100 = σ_D re-estimate at 400k (+840) · 189 = MC
power rung (+1,068) · 279 = 80% assurance, v2 central target (+1,080) · 340/403/568 =
90/95/99% (+732/+756/+1,980). **Stages:** S1 = frozen confirmatory (the dissertation's
verdicts); S2 = post-headline report-only (M2 25-model ~$10 no-GPU; R77-ii dose-response
{B*/2,B*,2B*}×10 CRN seeds ≈50 tr-equiv; FTSE-lite ADR-047; D6/U5; trigger legs K3/KAT —
dissertation-optional, Papers-2/3-bound).

**Unified priority queue:** Opus search → TIER-30 floor → tier-100 (σ recalibration EARLY so
the exogenous stop uses updated σ) → legs 1–9 (tier-30 each) → tier-189 → tier-279 → Gemini
seat-10 → tier-340 → tier-403 → [calendar cuts here] → S2.

**Milestones from Jul 28 launch (39.4×C tr/day; 10-model design = 6,288 tr core+legs):**
mechanism +0.4d C12 · floor +1.3d (~Jul 29) · tier-100 +3.0d · 9 legs +8.8d (~Aug 6) ·
tier-189 +11.0d · tier-279 +13.3d (~Aug 10) · Gemini +14.0d · tier-340 +15.5d (~Aug 13) —
then the Aug-14 gate + S2 window + bank ~Aug 18. C=20: all by ~Aug 5 + tier-403 reachable.
C=8: tier-279 lands Aug 17; Gemini/340 truncate by rule. C=4: floor banks day ~4; achieved-rung
honesty carries the write-up. Every speed outcome is a pre-named branch: tiers absorb speed on
the DEPTH axis, the leg queue on the BREADTH axis, stages keep the confirmatory core sealed off
from everything exploratory.

## 2. Gate table

| Gate | When | Rule | Failure path |
|---|---|---|---|
| Package sign-off | tonight | Tamer approves roster/rung/ceiling | iterate tonight only |
| Contamination×6 + smokes | Jul 21–22 | pre-declared screens pass | DeepSeek→GLM absorbs; any other leg → next in queue |
| Okhrati sign-off | by Jul 26 | email reply or default-proceed | Tamer's call, documented |
| FREEZE v2 | ON TAMER'S EXPLICIT WORD ONLY (no scheduled date, his 2026-07-21 instruction) | gate green + hash stamped + sync verified + PUBLIC deposit | schedule shifts accordingly; the core is always protected |
| C0 canary | launch | hard-stop pre-spend | fix → relaunch |
| Leg calendar gate | **Aug 14** | completed legs report; rest truncate | pre-registered wording |
| $30 spend ceiling (ADVISORY, R83) | continuous | tracked per-call; WARNS at 80/100%; never refuses | spend decisions are Tamer's |
| Rung stop | ~Aug 18–20 | exogenous (throughput+calendar) | largest completed rung banks |
| The confirmatory look | once, at bank | single look; bank-gate logged | — |
| Novelty sweep | pre-submission | mandatory | wording tightened to the cell |

## 2b. Final deep-pass additions (2026-07-20, late night)

- **⚠ Myriad maintenance Aug 11 (2nd Tuesday) falls MID-CAMPAIGN** under the Jul-28 launch:
  budget +1 day (rung-403 lands ~Aug 14 at C=12); resume machinery absorbs it; runbook treats it
  as an EXPECTED event.
- **Permutation synthesis spec (exact, for R80):** per shared CRN seed, flip the
  (distributional↔scalar) assignment with p=½ SIMULTANEOUSLY across all legs; recompute the
  cross-leg sign statistic; 10,000 reps — shared-seed/panel dependence lives inside the null.
- **Build-spec additions:** (1) the $30 spend gate as CODE (live cross-provider ledger + hard
  refuse in priority order); (2) NEW freeze guard `assert_leg_roster_match` — leg roster + pins
  (provider/quant/mode/caps) go INTO preregistration.yaml (hash-bound) with an executed↔frozen
  cross-check; (3) contamination screens for the CLOSED legs too (Haiku/Sonnet/Luna/Gemini —
  screen is model-agnostic); (4) launch-day per-leg re-smoke inside the C0 canary; (5) the
  rung-freshness compile gate (grep-fails on stale number tags).
- **Entitlement extension:** fed blocks to OpenRouter-routed hosts = six derived aggregate
  statistics + a score, no raw licensed series — the recorded Anthropic-case reasoning extends;
  one paragraph in the decision note.
- **Okhrati framing win:** with the full-ladder math, **rung 403 (95%) remains the LIKELY
  landing even with 10 models** (~Aug 14 at C=12 incl. maintenance) — the email asks him to
  approve the SAME ladder/rung he already approved, plus report-only legs. Easier sign-off.

## 3. Top risks + standing mitigations

1. **Myriad throughput below plan** → queue order guarantees the floor banks first; legs and
   upper rungs truncate in declared order; the dissertation exists at every stopping point.
2. **OpenRouter outage / provider churn mid-campaign** → per-leg fallback provider orders;
   authoring staggered per generation; retries + resume; catalog snapshot archived.
3. **Okhrati latency** → email sent day 1; default-proceed option under the standing
   full-permissions grant; his objections absorbable pre-freeze until Jul 27.
4. **A leg model authors garbage** → reliability-as-finding semantics + selection floor;
   the leg still reports.
5. **Writing-month squeeze** → writing starts Jul 28 (needs no results); mechanism lands ~Aug 3;
   the CH6 skeleton + templates make number-refresh mechanical; word surgery is a planned pass.

## 4. What Tamer personally does (complete list)

1. Tonight: sign off the package.
2. Jul 21: send the Okhrati email (I draft).
3. Jul 21: OpenRouter top-up ~$25; confirm Anthropic ≥$30.
4. Jul 26–28: the freeze GO + launch GO (one word each).
5. Aug: co-write / review chapters as they land; final read.
6. Aug 28–29: submit.

Everything else is mine, on this schedule.
