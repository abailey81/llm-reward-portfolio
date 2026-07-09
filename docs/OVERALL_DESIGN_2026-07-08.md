# The overall design — the whole system on one page (2026-07-08)

> Tamer, 2026-07-08: *"ultrathink the overall design, all stages, all tiers, everything."* This is the
> single source of truth that ties every axis together, disambiguates the tier concepts (the thing that
> has caused confusion before), and stress-tests the whole for coherence. It changes no science
> (canonical hash `1c6b76b6`); it is the map, plus one reconciliation, one refinement, and the honest
> bottom line. Companions: `GRADE_SECURITY_AND_TIER_DESIGN_2026-07-08.md` (tiers + run times),
> `MYRIAD_DEEP_RESEARCH_2026-07-08.md` (the platform), `PLAN_IF_WE_USE_UCL_MYRIAD.md` (operational master).

## 0. The one-sentence architecture

**A set of NESTED value-ladders — each rung a complete, defensible deliverable — indexed by an
orthogonal identity axis (which arm tests which hypothesis), banked by an archive-as-truth value
cascade, executed by an adversity-proof machinery layer, all under one meta-principle: GRADE SECURITY
(a distinction is guaranteed by construction, and every rung beyond the first is pure upside).**

Everything below is a facet of that sentence.

## 1. The unifying principle: complete-at-every-boundary

The design has ONE recurring shape at every scale: an ordered ladder where **stopping at any rung leaves
a complete, honest, pre-registered result** — cheapest-strongest rung first, so value accrues
monotonically and adversity can only cost the *marginal* rung, never the study. This shape repeats
fractally: across the program (stages), within Stage 1 (the C-ladder), within the sweep (assurance
ladder), and within Stage 2 (armor tiers). That is why the design is robust — there is no single point
whose failure is uncontained.

## 2. THE AXIS MAP (every structural concept, named once — do not conflate)

There are **five value-ladders** + **one identity axis** + **one machinery layer**. They are ORTHOGONAL;
a unit is located by picking a coordinate on each.

| # | Axis | What it orders | Rungs (cheapest-strongest first) | "Complete at each rung" means | Coded in |
|---|---|---|---|---|---|
| 1 | **STAGES** (security doctrine) | program phases | Stage 0 de-risk (G0→G1→freeze) · **Stage 1 SECURE** · Stage 2 ADVANCE | Stage 1 done ⇒ **grade secured**; Stage 2 is armor | `run_campaign_cluster.py`, the plan |
| 2 | **C-LADDER** (execution order in Stage 1) | when each unit runs | C0 canary · C1 H2 search · C2 H2 test-n30 · C3 all-arms floor-n30 · **[effect-blind GATE]** · C4 sweep | C3 ⇒ complete 7-arm study at **n=30** (the distinction floor) | `campaign.run_campaign_tiered` |
| 3 | **ASSURANCE LADDER** (power, inside C4) | how many seeds | n=30 floor · 340 = 90% · 403 = 95% · 568 = 99% | each ⇒ a complete uniform-n design at that **equivalence power** | `power_analysis` (`ASSURANCE_TIER_BOUNDS`, `recommend_assurance_target`) |
| 4 | **VALUE-CASCADE** (banking granularity) | what's durably saved | training → pair → block → contrast → checkpoint → stage → program | the archive-truth resume unit + the gate | the driver + archive |
| 5 | **STAGE-2 ARMOR** (value×dependency) | which add-on runs | 2.A free depth · 2.B nearly-free · 2.C laptop calibration · 2.D premium shelf | each ⇒ +1 appendix table, **prunable to 0** | config-only reuse of the orchestrator |
| — | **ARM TIERS** (identity, NOT a ladder) | which arm → which test | H2 info-channel {scalar, scalar_cvar5, distributional} · search-baseline {random_search, bayes_opt} = H4 · controls {placebo, placebo_shuffled} · H1 {4 fixed rewards} | defines the multiplicity family + the mechanism contrasts | `arms.yaml` + inference config (frozen) |
| — | **MACHINERY** (substrate, NOT a ladder) | keeps ladders advancing | resume (archive-truth + supervisor + boot + mirror + 12 h transport tolerance + `resume_audit`) · monitoring (sentinel + driver-lease + queue panel + OOD) · the cluster orchestrator | — | `src/cluster/*`, `scripts/sentinel.py`, … |

**How they NEST (the composition):**
```
PROGRAM
 └─ Stage 0 (de-risk)  →  Stage 1 (SECURE)  →  Stage 2 (ADVANCE)                      ← axis 1
                            └─ C0 · C1 · C2 · C3 ─[GATE]─ C4                            ← axis 2
                                                          └─ 30 → 340 → 403 → 568       ← axis 3
                                                     Stage 2 └─ 2.A · 2.B · 2.C · 2.D    ← axis 5
   every unit is ALSO tagged by an ARM TIER (identity, axis —) and banked by the VALUE-CASCADE (axis 4),
   the whole run kept alive by MACHINERY, all under GRADE SECURITY.
```
The two axes people conflate are **2 (C-ladder = execution ORDER)** and **3 (assurance ladder =
statistical POWER)**: C0–C3 bank the n=30 floor; C4 then climbs the assurance ladder. Different
questions ("when does it run?" vs "how many seeds?"), composed cleanly.

## 3. The identity axis (arms → hypotheses → tests)

Orthogonal to every ladder: the 7 frozen arms map to the hypotheses. **H2** (the headline) compares the
info-channel tier in a two-one-sided-tests IUT (Sharpe + CVaR co-primary); **H4** compares the LLM arms
to the search baselines; the **controls** (placebo / placebo_shuffled) anchor the mechanism (SQ1–SQ3);
**H1** is the fixed-reward baseline family; **H3** is the reflection dose-response. The uniform-n sweep
runs *all* arms to the same n (defensible; kills the asymmetric-leg objection) even though only the H2
tier carries the equivalence claim — identity (analysis) and execution (uniform n) are deliberately
separate.

## 4. The end-to-end lifecycle + what's built

| Phase | What happens | Status |
|---|---|---|
| Access (G0) | VPN + key → `g0_probe.sh` confirms cgroup isolation, quotas, apptainer | BUILT; Tamer-gated on UCL access |
| Cert (G1) | fps benchmark + queue-wait + crash/VPN/determinism rehearsals; MEASURE per-training wall, sustained C, packing F | rehearsals + tests BUILT; live run Tamer-gated |
| Freeze | pre-freeze edits land → `freeze.py` → hash bound | BUILT; **Tamer's act alone** |
| Stage 1 run | the C-ladder (C0→C3→gate→C4), packed, on the V100 pool | BUILT (`run_campaign_tiered`), 90+ tests green |
| Bank gate | verify-mirror → confirmatory analysis + D3/D4/D9 depth bundle → prereg-results bundle → Results drafted | components exist (`analyze_campaign`, the analysis scripts, `make_prereg_bundle`); **crisp-up: one runsheet** (§7) |
| Stage 2 | armor tiers 2.A→2.D, config-only, both pools, overlaps the write-up | config + analysis scripts exist |
| Write | word surgery (17k→9.5k) + depth pass on the mechanism chapter | drafted; the dominant remaining lever (§7) |
| Submit | pre-submission fence + citation sweep → submit Aug 28–29 | tooling built |

## 5. Grade security (the meta-principle over all axes)

The seven guarantees (full detail in `GRADE_SECURITY_AND_TIER_DESIGN §1`): floor-first ordering ·
every-stop-a-complete-design · exogenous stopping ⇒ valid single-look · dual-track laptop fallback ·
bulletproof resume · deadline buffer · procedural hygiene (acknowledgment + compute-reporting +
frozen prereg). Net effect: **after ~day 1–2 (the n=30 floor), the grade is not at risk from anything
the machinery can suffer.**

## 6. Coherence + gap review (adversarial self-check — the "ultrathink")

**CONSISTENT.** The five ladders compose without conflict (each answers a different question); the arm
roster (7), the assurance bounds (30/340/403/568), and the C-ladder order are the same in the code,
the config, and these docs (freeze `--check` green; the assurance + C-ladder + driver tests green; hash
unchanged all session).

**RECONCILED (a number the research moved).** `PLAN §3` quotes Stage-1 durations UNPACKED
(3,580 GPU-h ÷ 24C → 12.4 d @ C=12). The 2026-07-08 research **validated GPU packing** (device cgroups),
so the current central figure applies F≈1.75 → **Stage-1-to-403 ≈ 7 d, floor ≈ 1.3 d**
(`GRADE_SECURITY §3`). The plan's table is not wrong — it is the conservative unpacked bound; the packed
figures supersede it now that packing is confirmed. (Both survive the deadline with weeks to spare.)

**REFINEMENT (a way the design gets smarter, cleanly).** The assurance TARGET is provisionally chosen
at freeze from the G1 estimate, but the **C3→C4 gate can re-confirm it from the run's OWN measured
cadence** (the journal already computes completions/hour): feed that into `recommend_assurance_target`
→ the deadline-safe target is set on *observed* throughput, not a forecast. This is still exogenous
(throughput + calendar, never the effect), so it stays a valid single-look — it just makes "never
overcommit past the deadline" self-correcting. The hook exists (cadence measured, selector built);
activate it live at the gate.

**CRISP-UP (the one thing to make executable, not just described).** The **bank gate** is a sequence
of existing tools (`verify-mirror` → `analyze_campaign` → the D3/D4/D9 scripts → `make_prereg_bundle`);
it deserves one short runsheet/wrapper so the "Stage-1-compute-done → dissertation-complete" transition
is a single documented command, not tribal knowledge. Small, do at G1.

**THE HONEST DOMINANT LEVER (the most important sentence here).** All of this machinery — Myriad, the
tiers, resume, monitoring — **secures the RESULT with near-certainty. It does not, by itself, win the
grade.** The grade is graded on the PDF, and Okhrati's revealed function rewards *intuition over
machinery, depth over breadth, honest nulls, and data-motivated method*. So the machinery is necessary
(no reliable results → no dissertation) and it demonstrates "faultless execution" — but it appears in
the PDF as one methods paragraph, one compute-reporting line, and one acknowledgment. **The grade is
WON in the mechanism chapter** (SQ1–SQ3: does the fed tail change the authored code? the causal chain,
the reward-code taxonomy, responsiveness/mediation/specificity), **in the honest framing of the null**
(equivalence as a boundary condition, not a failure), and **in the motivating EDA** (the tail facts →
why a scalar cannot carry them). The impressive infrastructure must not distract from the fact that,
after the freeze, the dominant remaining grade lever is the **write-up depth**, which is drafted but
needs the depth pass + the 17k→9.5k surgery. Priorities #2–#4 (world-class / deep / corpus-grounded)
are won there, not on the cluster.

## 7. The single mental model

> **Build one complete study fast, bank it, then keep tightening and armoring it — never risking the
> banked core — while the real grade work (the mechanism write-up) proceeds in parallel.** The stages,
> the tiers, the ladders, the resume, and the monitoring are all in service of that one behaviour; grade
> security is the guarantee that it holds under any adversity; and the mechanism chapter is where the
> distinction is actually earned.
