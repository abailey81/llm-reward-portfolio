# V2 MASTER PLAN — 2026-07-20 → submission (the ultraplan)

> The complete execution plan for the v2 design (post-UNFREEZE, ADR-059/R78), integrating: the
> locked 7-model roster (`MODEL_SWEEP_2026-07-20_v2.md` + addendum), the NatWest + Okhrati
> feedback (CLAUDE.md, both blocks), the $30 spend ceiling, the pipelined write-while-rungs-land
> strategy (Tamer's plan), and every gate/fallback decided in the 2026-07-20 design session.
> Deadline: **1 Sep 2026**; submission target **Aug 28–29**.

## 0. The design being executed (one paragraph of record)

One frozen question (does feedback content change the reward code an LLM writes, and does it
transmit?); ONE frontier confirmatory author (Opus 4.8) under the full v1 rigor (7 arms, m=6,
co-primary IUTs, SESOI ±0.05, floor-30 → rung-279 expectation, exogenous stop); EIGHT replication
legs — six open-weight (DeepSeek V4-Pro·MIT [contamination gate; GLM absorbs on failure],
GLM-5.2·MIT, Qwen3.6-27B·Apache + Qwen3.5-9B·Apache [open capability pair — SiliconFlow fp8,
same provider+quant], Nemotron-3-Super·NVIDIA-OML [data-transparency seat], Hy3·Apache [replaced
MiniMax-M3 on the license gate]) **plus two cheap closed tiers (Tamer's addition, 2026-07-20
night): Claude Haiku 4.5 (`claude-haiku-4-5-20251001`, dated snapshot — the CLOSED within-family
capability pair vs Opus, so the controlled capability contrast runs TWICE, once per ecosystem)
and GPT-5.6 Luna (`openai/gpt-5.6-luna` — restores the cross-vendor closed point at $1/$6;
output capped 4k tokens to bound hidden-reasoning billing ≈$4.50 worst-case; no dated snapshot,
disclosed)** — 9 full-loop models total; floor-30 seeds each, byte-identical prompts, unified
prompt-variation diversity, pinned providers/quant/reasoning-modes, priority-queued behind the
core (DeepSeek → GLM → Qwen27 → Qwen9 → Haiku → Luna → Nemotron → Hy3), calendar-gated
**Aug 14**; the M2 reading-link survey (25 exact models incl. both
within-family ladders) post-headline; a dependence-aware pre-registered synthesis (descriptive
sign count + seed-block permutation test + capability regression on a pre-declared external
anchor, M2 score secondary); per-model authoring-reliability + code-taxonomy outputs; study-level
success metrics; **$30 total LLM ceiling** as a priority-ordered exogenous spend gate; two keys
only (Anthropic + OpenRouter). All extensions truncation-safe behind the core; the tier-30 floor
banks the degree regardless.

## 1. Phase plan (day-by-day, with owners)

### Phase 0 — TONIGHT (Jul 20): sign-off + drafts  [Tamer + me]
- **Tamer: sign off the package** (roster 7 + M2 25 + rung 279 + $30 ceiling + Aug-14 leg gate).
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

### Phase 3 — Jul 26–28: FREEZE v2 + LAUNCH  [Tamer's GO]
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

## 2. Gate table

| Gate | When | Rule | Failure path |
|---|---|---|---|
| Package sign-off | tonight | Tamer approves roster/rung/ceiling | iterate tonight only |
| Contamination×6 + smokes | Jul 21–22 | pre-declared screens pass | DeepSeek→GLM absorbs; any other leg → next in queue |
| Okhrati sign-off | by Jul 26 | email reply or default-proceed | Tamer's call, documented |
| FREEZE v2 | ≤ Jul 28 | gate green + hash stamped + sync verified | slip eats leg-queue tail, never the core |
| C0 canary | launch | hard-stop pre-spend | fix → relaunch |
| Leg calendar gate | **Aug 14** | completed legs report; rest truncate | pre-registered wording |
| $30 spend ceiling | continuous | priority-ordered; hard stop | M2 closed-tier trims first |
| Rung stop | ~Aug 18–20 | exogenous (throughput+calendar) | largest completed rung banks |
| The confirmatory look | once, at bank | single look; bank-gate logged | — |
| Novelty sweep | pre-submission | mandatory | wording tightened to the cell |

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
