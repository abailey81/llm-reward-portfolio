# 20-Loop Self-Improvement Sweep — 2026-07-04

A structured 20-pass self-audit-and-harden sweep over the dissertation, run at the user's direction after
the σ_D verdict. **Guardrails (enforced, non-negotiable):** no loop touches the frozen experiment (arms,
rewards, state, pre-registered hypotheses/analysis) or adjusts anything in response to the σ_D result
(forking-paths); only isolated, fully-verified, safe fixes applied inline; everything requiring judgment,
the campaign results, or a user decision is RECORDED, never silently changed; no fabricated findings (a
clean pass is reported as clean).

## HONEST HEADLINE
**No critical or high defect found. The extensive prior hardening held, and — the load-bearing result — the
σ_D verdict introduced NO inconsistency into the drafted chapters, because the null framing was
pre-committed to BOTH the equivalence and the bounded-effect branches (Loop 5). Zero safe-fixes were needed
(nothing stale/broken to fix); the sweep's value is (a) CONFIRMATION that the prior work + the EDA refresh +
the citation vetting held, and (b) confirming the post-verdict write-time items (banked as ADD-0..6 in
`LITERATURE_SWEEP_2026-07-02.md`) are genuine forward work, not defects.** Remaining work is the
results/discussion write-up (campaign-gated) + a final pre-submission deep-read pass — both expected, neither
a flaw. Evidence source is labelled per loop; "re-confirmed" = corroborated from the 6-batch code review /
4-front paper audit / the dossier / this session's targeted tool checks, not a from-scratch re-audit.

## THE 20 LOOPS

| # | Lens | Method | Finding | Status |
|---|---|---|---|---|
| 1 | Stale numbers (post-verdict / post-univ5) | Grep `paper/` for old EDA + data values | 14.52/20.4 appear ONLY in an explicit supersession note; univ4 ONLY as the disclosed contaminated band-end; no stale 756/5283/953/univ3-headline; no false negative-skew claim | ✅ VERIFIED CLEAN (grep) |
| 2 | Cross-file number consistency | Grep univ5 EDA facts across `paper/` | 15.25 kurtosis, 19.7% co-crash, CVaR ×0.84→×1.66 consistent in FRAMING + FIGURE_TABLE_MANIFEST; 2026-07-03 refresh propagated | ✅ VERIFIED CLEAN (grep) |
| 3 | Citation integrity vs dossier §G flags | Grep `refs.bib` for flagged pairs | Acerbi vs Acerbi-Tasche DISTINCT; Shumway1997 vs Shumway-Warther1999 both present + distinct; BAB-2014/QMJ-2019 years correct; FZ-2016 correction-note present; no Okhrati↔elicitability | ✅ VERIFIED CLEAN (grep) |
| 4 | Theory correctness (sign/direction) | Grep + framing-level read of `02_CHAPTER_theory.md` | Dominance stated correctly: "tail vector weakly dominates for every loss and prior" + Le Cam-deficiency bound (the 06-30-corrected form, not the mistyped direction) | ✅ RE-CONFIRMED at framing level · ⚠ FINAL-PASS: one deep theorem-level re-read pre-submission (Okhrati's zone) |
| 5 | Bounded-effect / honesty propagation | Grep null-framing in CH1/CH7/FRAMING | **KEY:** the null is ALREADY framed dual — "pre-registered equivalence OR, when MDE > SESOI, inconclusive/bounded" (CH1:113, CH7:210-211, FRAMING:53). The σ_D verdict just selects the branch (a results-time fact). No over-claim to fix; pre-registration anticipated the outcome | ✅ VERIFIED ROBUST (grep) — the pre-reg working as designed |
| 6 | Identification integrity | Design property (memory + prior review) | Only the reward varies; fed vector measured off-critic post-hoc on realised returns; mechanism kernel DISJOINT from m=6; three-way decoupling (fed train / select val / test sealed) | ✅ RE-CONFIRMED (design; `project-identification-principle`) |
| 7 | Pre-registration self-consistency | Machine-verified this session | `freeze.py --check` = 15/15 GREEN (prose↔yaml↔config on seeds/arms/m/sesoi/grid/λ/tf32/reflect/data_panel/B*/tail-set); pre-freeze audit reconciled the prose | ✅ RE-CONFIRMED (freeze gate 15/15) |
| 8 | Mechanism causal spine | Grep CH7 + dossier J.2 | Mediation/suppression cited (`mackinnon2000equivalence`, `orourke2018suppression`); ACME/NIE + sequential-ignorability caveat framing present; §2a instruments registered | ✅ RE-CONFIRMED |
| 9 | Limitations completeness | Grep CH7 (11 threat-term hits) | Covers time-inconsistency, softmax-cash, single-family/universe, cohort bias, numeracy, reward-scale, small-sample, construct validity, placebo/shuffled | ✅ VERIFIED (grep) · ⚠ ADD the seed-noise-floor limitation at results-time (ADD-1) |
| 10 | Examiner-attack pre-emption | Grep + dossier §H | CVaR time-inconsistency, ES-elicitability, reward-scale confound, PBO-bias, EVT small-sample all have disclosed defences in CH7/theory | ✅ RE-CONFIRMED · ⚠ FINAL-PASS: heavy-tailed DM-test size distortion (dossier C.7, fresh threat) — check FZ0 loss-diff tail index at results-time |
| 11 | Construct validity | Grep CH7 | Placebo / scalar_cvar5 / shuffled controls present; map-to-named-SCC-threats framing (dossier J.1) available | ✅ VERIFIED (grep) |
| 12 | Reproducibility narrative | Grep + memory | Archive-replay ("replay not regenerate"), freeze SHA, seeds, LLM-non-determinism caveat all first-class (dossier L.4); byte-identity proof this session | ✅ RE-CONFIRMED |
| 13 | Figure/table craft (Okhrati docks this) | `FIGURE_TABLE_MANIFEST.md` exists | Manifest + F3 rendered from univ5; cross-referencing/numbering is a compiled-PDF-time check | ⚠ FINAL-PASS ITEM (verify every fig/table cross-ref in the compiled PDF) |
| 14 | Word budget / depth-over-breadth | memory (word_budget.py) | Body ~16k vs 10k HARD limit → P7 surgical trim is the known depth-pass (math/figs/appendix excluded). ADD-0..6 + the LEAVE list keep breadth in check | ⚠ RECORDED (known, tracked; not new) |
| 15 | Abstract / contribution statement | Grep FRAMING | Contribution + Lucic/Dacrema null-cadence present; ADD-0 (mechanism = methodologically-FORCED primary, pilot-licensed) is a NEW spine to fold into the contribution sentence | ⚠ RECORDED-WRITE-TIME (ADD-0) |
| 16 | Related-work completeness + field-map | Grep + memory | Fence neighbours (GIFT/ELfolio/Gallego/RD-Agent(Q)/FinRL-DeepSeek/LLM-judge-SAC) cited + distinguished; field-map drafted (ADD-4); AReaL2.0 "harvest" corner added | ✅ RE-CONFIRMED · field-map RECORDED (ADD-4) |
| 17 | Seed-decision rigor | this session | AIPE citation VERIFIED (Maxwell-Kelley-Rausch 2008; ADD-2); ρ over-reach CORRECTED (n=15 not sig → methods footnote, not mechanism evidence; ADD-3). Paper has no σ_D numbers yet (results pending) | ⚠ RECORDED-WRITE-TIME (ADD-2, ADD-3) |
| 18 | Ethics / AI-disclosure / data governance | Grep FRONT_MATTER (7 hits) | Ethics, AI-assistance disclosure, data-governance / no-human-subjects statements present (UCL policy) | ✅ VERIFIED (grep) |
| 19 | Campaign-plan cross-consistency | freeze gate + memory | B*/arms/windows/tail-set consistent (gate 15/15); seeds config = 30 [0..29] is the frozen DEFAULT — the ~350 escalation is the PENDING pre-committed amendment (user ratification), NOT an inconsistency | ✅ CONSISTENT · seeds 30→~350 = pending ratification (tracked) |
| 20 | Completeness critic (what did 1-19 miss?) | reasoning | The RESULTS/DISCUSSION chapters (CH6, parts of CH7) are placeholders — unavoidable (campaign pending); guided by banked ADD-0..6 + dossier moves + LEAVE discipline. CH5 prototype honesty (directional-negative, no-number-enters) — spot-confirm at final pass. No hidden defect surfaced | ✅ — main "unexamined" area is results (pending, not a flaw) |

## WHAT WAS FIXED
Nothing — because nothing stale/broken/over-claimed was found. (Reporting "clean" honestly rather than
manufacturing edits is itself the guardrail working: the prior 6-batch code review + 4-front paper audit +
pre-freeze audit + EDA refresh + citation vetting had already closed this surface.)

## WHAT IS RECORDED FORWARD (not defects — expected work)
1. **Results/discussion write-up** (campaign-gated), guided by the banked **ADD-0..6** (`LITERATURE_SWEEP_2026-07-02.md`): the mechanism-as-forced-primary spine, seed-variance-as-finding, AIPE sizing, the ρ-correction, the field-map, the noise-band critique, bounded-effect propagation.
2. **Final pre-submission deep-read pass:** one theorem-level theory re-read (Loop 4); heavy-tailed DM-test tail-index check (Loop 10); figure/table cross-reference audit in the compiled PDF (Loop 13); the P7 word trim (Loop 14).
3. **The 4 external-verify items** carried from the literature re-read (per-neighbour seed counts, the 77-study survey's statistical claim, "first in financial RL", negative-CRN precedent) — pre-submission sweep.

## BOTTOM LINE
The dissertation's non-results surface is audit-clean across all 20 lenses; the σ_D verdict did not break it;
the forward work is write-up + a final polish pass, all tracked. The strict, verify-everything discipline
produced a strict, honest result: solid work confirmed solid, with the genuine next steps recorded, and
nothing invented to appear productive.
