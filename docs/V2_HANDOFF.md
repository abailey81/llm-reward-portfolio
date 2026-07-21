# V2 HANDOFF — read this FIRST to continue losslessly (2026-07-21)

> **Purpose.** A self-contained handoff so the NEXT Claude Code session picks up the v2 build with
> zero loss. Read this, then `memory/session-current-focus.md` (the cursor) + `CLAUDE.md`
> (PRIORITIES + both feedback blocks). Authorities cross-referenced at the end.
>
> **State in one line (updated 2026-07-21e):** the pre-registration is UNFROZEN (`frozen: false`,
> pre-data, legitimate); **ALL 8/8 build steps are done, committed, and full-suite-certified**
> (steps 7–8 landed `e968cdd` + `7bf1fa7` on Tamer's "Build"; suite exit 0); **nothing freezes or
> launches without Tamer's explicit word** (no scheduled date). Remaining: the pre-launch leg
> gates (need ~$5 OpenRouter) + Tamer's items (§6). Cluster sync VPN-blocked; the GO sequence
> re-syncs at launch.

---

## 1. Hard rules (DO NOT violate — these are Tamer's standing instructions this session)

1. **NOTHING is frozen without Tamer's explicit word.** No scheduled freeze date. `freeze.py`'s
   real write path is Tamer-only; `enforce_freeze` refuses real launches while unfrozen. The
   dates in `V2_MASTER_PLAN` are PLANNING REFERENCES, not triggers.
2. **The spend system is ADVISORY (R83).** `src/llm/spend_ledger.py` tracks + warns at 80/100% of
   the $30 planning ceiling and **NEVER refuses** a call. Do not add a hard spend gate.
3. **Sequential-solo, token-lean.** Tamer stopped the parallel build agents and asked for
   hands-on, one-step-at-a-time work, committing each verified piece. No fan-out agents for the
   build.
4. **The sealed test leg stays sealed** (2020–2026); the confirmatory v1 core is UNCHANGED
   (Opus 4.8, 7 arms, m=6, IUTs, SESOI ±0.05, the E1 seed ladder).
5. **Verify then claim.** Run the venv pytest and show real output before saying green. Venv =
   `./.venv/Scripts/python.exe`.
6. **Content with backslashes/escapes → Write/Edit tools, never bash heredocs** (heredoc `\n`
   mangling has bitten repeatedly). Absolute POSIX paths through Git-Bash argv need
   `MSYS_NO_PATHCONV=1` or argparse defaults.

## 2. The v2 design (what we're building)

**One frozen question**, unchanged: does feedback *content* (multi-level tail vs scalar) change
the reward code an LLM writes, and does it transmit? Mechanism headline + pre-registered
equivalence backdrop.

**The 10 full-loop models** (FINAL; the executed truth is `config/legs.yaml`, gate-verified ==
`model_suite`):

| Seat | Model | id | Role / pins |
|---|---|---|---|
| Confirmatory | Opus 4.8 | `claude-opus-4-8` (anthropic) | the ONE frontier; full v1 rigor; rung 403 likely landing @C12 |
| Leg 1 | DeepSeek V4-Pro | `deepseek/deepseek-v4-pro` | MIT; reasoning=think-high pinned; **contamination gate → GLM absorbs on fail** |
| Leg 2 | GLM-5.2 | `z-ai/glm-5.2` | MIT; also DeepSeek's fallback |
| Leg 3 | Qwen3.6-27B | `qwen/qwen3.6-27b` | Apache; **SiliconFlow fp8** |
| Leg 4 | Qwen3.5-9B | `qwen/qwen3.5-9b` | Apache; **SiliconFlow fp8** — same provider+quant as leg 3 (the confound-free OPEN pair) |
| Leg 5 | Haiku 4.5 | `claude-haiku-4-5-20251001` | closed ladder bottom (dated snapshot) |
| Leg 6 | Sonnet 4.6 | `claude-sonnet-4-6` | closed ladder mid + **the PILOT BRIDGE** (prototype author, re-tested under the frozen design) |
| Leg 7 | GPT-5.6 Luna | `openai/gpt-5.6-luna` | cross-vendor closed; effort=low, max_tokens=2048 (bounds hidden-reasoning cost) |
| Leg 8 | Nemotron 3 Super | `nvidia/nemotron-3-super-120b-a12b` | NVIDIA OML (NOT Apache; "major portions of data" — phrase exactly); US-lab + data transparency |
| Leg 9 | Gemini 3.5 Flash | `google/gemini-3.5-flash` | **seat-10 STRETCH, first-to-truncate**; reasoning at provider default DISCLOSED (R85 — the old "budget=default" pin used an undocumented key), max_tokens=2048 |

Queue order (pre-declared, exogenous truncation from the BACK):
`DeepSeek → GLM → Qwen27 → Qwen9 → Haiku → Sonnet → Luna → Nemotron → Gemini`.
All non-Anthropic via **OpenRouter** (two keys total: `ANTHROPIC_API_KEY` + `OPENROUTER_API_KEY`).
Legs run at the **tier-30 floor**; byte-identical prompts; unified prompt-variation diversity;
`~*/-latest` aliases BANNED.

**M2 reading-link survey**: 25 core + 7 extras in `config/m2_models.yaml` (schema-aware loader;
`--include-extras`). Excluded-by-design: Sakana Fugu (orchestrator), Llama 4, `~latest` aliases.

**Tiers × Stages × Queue**: E1 ladder 30→100→189→279→340→403→568 (tier-100 hoisted early so the
exogenous stop uses the UPDATED σ). Stage-1 = frozen confirmatory; Stage-2 = report-only (M2,
dose-response, FTSE-lite, trigger legs K3/KAT). Leg calendar gate = **2026-08-14T23:59Z**.
Aug-11 Myriad maintenance budgeted (+1d). Each leg ≈ 300 trainings ≈ 0.63 d @C12; 10 models +
full 403 ladder ≈ ~Aug 13–14 @C12.

**Cost reality** (for Tamer + the NatWest line): whole study's LLM bill ≈ **$20–26** (worst ≈$30);
GPU is the Myriad allocation (free). Pre-launch gates alone ≈ $1–2. Tamer only needs ~$5 on
OpenRouter to run this week's gates; the rest at launch.

## 3. What's BUILT (ALL 8 steps + the post-build hardening waves, committed + green)

| Step | Commit | Delivered |
|---|---|---|
| Records (wave 1) | `a858b04` | R79 prompt pass · `model_suite` yaml (R80/R81) · R82 supplement · PREREGISTRATION §14 prose + rows R79–R82 · ADR-060 · m2_models.yaml v2 · write-time registry · Okhrati email + NatWest brief drafts |
| 1 | `ceadd54` | `config/legs.yaml` — the executed 9-leg config (pins, reasoning, max-tokens, pair invariant, planning prices) |
| 2 | `41e9a1e` | `src/llm/spend_ledger.py` — ADVISORY ledger (R83) + 7 tests; drafts/yaml softened |
| 3 | `99d2901` | `src/llm/client.py` extra_body passthrough (provider pins/quant/reasoning/usage-cost) + `~latest` ban at `build_transport` + `last_cost_usd`; `src/llm/legs.py` loader; 13 tests |
| 4 | `aa910eb` | `freeze.py::assert_leg_roster_match` — the executed legs bound to `model_suite`; **live gate now = 21 OK checks**; 9 adversarial tests |
| 5 | `0464b4f` | `src/inference/cross_model.py` — synthesis (sign count, permutation, pair DiD, leg-family BH, gen-indexed SQ1, capability regression); 15 tests |
| docs | `4b160e3`, `98f2c38` | CHANGELOG [2026-07-20/21] · master-plan de-stale · v2 banners on both overview docs |
| 6 | `e0380c5` | `scripts/leg_gates.py` (smoke + compliance + contamination screen) + `src/inference/leg_aggregate.py` (multi-root → synthesis input) + 11 tests |
| fix | `5c7f50c` | §14 R83 reconciliation (the "hard-capped/enforced" sentence → advisory wording; gate 21 OK) |
| 7 | `e968cdd` | CH6 skeleton v2 (§6.7 legs + §6.8 synthesis + rung slots) · the CONCRETE rung-freshness convention (rule 5) + `scripts/check_rung_freshness.py` gate · manifest F12–F15/T6–T7 · the four viz renderers (`cross_leg_forest`/`capability_gradient`/`reliability_heatmap`/`ten_winners_exhibit`) · 15 tests |
| 8 | `7bf1fa7` | **the leg-launch wiring gap closed** (`--leg <label>` on the cluster driver; `extra_body` pins survive both author sites; the R83 per-call ledger at `LLMClient.complete` incl. the Opus planning-price row) · runbook §9 (leg queue / monitoring / spend) · dry-runs GREEN on real gold (core + deepseek + qwen lines) · 10 tests + regression sweep |
| brief | `4d233db` | NatWest push-back reframed to the TWO-CREDIBILITIES argument (finding-credibility needs the frontier; reproduction-credibility fully delivered by the pinned open legs + verbatim call archives) |
| R84–R87 | `e16fad2` | deep-sweep amendments: capability anchor PINNED (SWE-V rule) · T0 floor PINNED (equal_weight, seeds 0–29) + arm-symmetry note · HF weights pins REQUIRED (freeze REFUSES placeholders — `pending_hf_pins`) · temp=1.0 OpenRouter pin · reasoning round-trip evidence in leg_gates · `pooled_bound` (the 90% bounded-effect CI, dependence-honest) · the FALSIFIABLE three-signature gradient table + the ex-ante sonnet-bridge ≤0 · ADR-060 entitlement addendum · registry rows 14–18 · Anthropic top-up ≥$35 |
| MODE D | `131a8e2` | R88 max-parallel execution: phase-adaptive packing (`--search-pack 2` latency lane, tight h_rt; bursts pack-5) · pipelined C4 rungs (`--pipeline-rungs`, ladder −100/−300… fixing the rungs-starve-legs wiring) · `mode_d_launch.ps1` = ONE command, 10 self-healing lines · runbook §10 · expected: legs ~L+3–4, tier-403 ~L+12–14 |
| audit | (this commit) | consistency audit: leg/root-suffix `campaign_summary` CLOBBER fixed (namespaced per suffix — the H3-class hazard); both PS1s parse-validated (em-dash/BOM-less-UTF-8 smart-quote breakage + a `$args`-shadow splat bug fixed); citations gate clean; CHANGELOG [2026-07-21c] |

**Two pre-freeze statistical catches (do NOT re-litigate — already fixed + registered):**
(a) the cross-leg sign test's **independence flaw** (legs share panel + CRN seeds) → the
descriptive-count + per-seed joint-flip permutation design; (b) the permutation **sign-COUNT
statistic is near-powerless** under joint flips with correlated legs → the test statistic is the
**POOLED MEAN difference** (multivariate paired sign-flip), sign count kept descriptive. Both are
in `config/preregistration.yaml: model_suite.synthesis*` and §14 prose.

## 4. What's LEFT (steps 7–8 are DONE — see §3; this is the remaining path)

- **Gates (need ~$5 OpenRouter credit; the one build-side item left)** —
  `python scripts/leg_gates.py --all --out outputs/leg_gates` (×9 smoke + compliance baseline +
  contamination screen). DeepSeek fail → GLM absorbs seat 1 (pre-declared). Then license-file
  glances (Nemotron OML text archived).
- **Cluster sync** — VPN-blocked 2026-07-21 (ssh timeout); the GO-sequence step 3 re-syncs +
  writes the GIT_COMMIT marker at launch. The marker is STALE until then.
- **Then (Tamer's word only)**: FREEZE v2 (`freeze.py`; new hash; tag `prereg-v2.0`; bundle;
  **PUBLIC OSF/Zenodo deposit** per the freeze-day checklist) → C0 canary → LAUNCH (runbook §2.0;
  legs per runbook §9) → writing starts same day per `docs/V2_WRITE_TIME_REGISTRY.md`.

## 5. The write-time registry (13 binding items) lives in `docs/V2_WRITE_TIME_REGISTRY.md`
Nothing there may be silently dropped: the g(capability) CH3/CH7 paragraphs, the CH4 model-suite
+ cost + reproducibility sections, the CH2 15/15 survey table, the abstract reframe, NOMENCLATURE
additions, the AI-as-object full roster, CH6/figures/notebook v2, the interim report pack, the
per-leg bank-gate logs, and the pre-submission gates.

## 6. Tamer's pending human items
1. Send the Okhrati email — draft ready at `docs/DRAFT_EMAIL_OKHRATI_2026-07-20.md`.
2. Top up OpenRouter (~$5 unblocks this week's gates; ~$25 covers everything).
3. The freeze GO + the launch GO (one word each, when he's ready).

## 7. Key file map
- Design of record: `config/preregistration.yaml` (`model_suite` + `synthesis*`) · `PREREGISTRATION.md` §14 + rows R78–R83 · `DECISIONS.md` ADR-059/060.
- Plan + evidence: `docs/V2_MASTER_PLAN_2026-07-20.md` · `docs/MODEL_SWEEP_2026-07-20_v2.md` · `CHANGELOG.md` [2026-07-20/21].
- Code: `config/legs.yaml` · `src/llm/{legs,client,spend_ledger}.py` · `scripts/leg_gates.py` · `src/inference/{cross_model,leg_aggregate}.py` · `scripts/freeze.py` (guard) · `config/m2_models.yaml`.
- Comms: `docs/DRAFT_EMAIL_OKHRATI_2026-07-20.md` · `docs/NATWEST_RESPONSE_BRIEF_2026-07-20.md`.
- Overviews (v2-bannered): `docs/DISSERTATION_MASTER_OVERVIEW.md` · `docs/DISSERTATION_EXPLAINED_FOR_BEGINNERS.md`.

## 8. First actions for the next session
1. Read this file + the cursor + CLAUDE.md (incl. the ★★★ FOUR-AUTHORITY COMPLIANCE RULE,
   2026-07-21); say "Resuming from: … — next: …".
2. Run the FULL suite once to confirm the green baseline before touching anything:
   `./.venv/Scripts/python.exe -m pytest -p no:cacheprovider -p no:warnings -q` (expect 0 failed;
   the freeze `--check` should show **21 OK** lines, `frozen: false`).
3. The BUILD is COMPLETE (8/8). Do NOT freeze/launch unless Tamer says so. If OpenRouter credit
   has landed, run the leg gates (§4). If he asks about cost/models/schedule, answer from §2;
   about launch mechanics, runbook §2.0 (core) + §9 (legs).
