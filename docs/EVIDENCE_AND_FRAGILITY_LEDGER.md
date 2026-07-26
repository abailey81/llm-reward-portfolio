# Evidence-and-Fragility Ledger — the non-fragile backbone (2026-07-25)

**Standard (Tamer, 2026-07-25; `CLAUDE.md` → EVIDENCE-BACKED, NON-FRAGILE BACKBONE):** every load-bearing
decision carries a stated RATIONALE + GRADE-A evidence; the backbone must have no weak link a skeptical
expert can snap; **the grade is capped by the weakest link.** This ledger maps every load-bearing decision
→ rationale · evidence+grade · fragility · status/fix, and is maintained continuously. A decision is not
"done" until its row is **grade-A + low-fragility**, OR its residual fragility is a disclosed Limitation.

- **Evidence grade:** **A** = first-hand-verified data/measurement in-repo · **B** = first-hand-read
  literature · **C** = asserted / no derivation (a fragility to close).
- **Fragility:** low · med · **HIGH** (can a skeptical Okhrati/Stefan read snap this link?).
- **Status:** ✅ strong · 🔧 fix-in-flight (with the amendment) · ⏳ pending the 2026-07-25 backbone audit.

> This is the SEED (spine decisions I can grade first-hand from the 5-criterion audit + the design
> record + the live verifications). The two-auditor exhaustive backbone map (launched 2026-07-25) will
> COMPLETE it (every remaining decision) and CALIBRATE these grades. Rows here are conservative/honest.

## Research frame
| decision | rationale | evidence + grade | fragility | status / fix |
|---|---|---|---|---|
| The novelty cell (LLM authors reward CODE + multi-level tail feedback as the manipulated variable + pre-registered controlled comparison) | a conjunctive gap unoccupied by any neighbour | 196-paper first-hand sweep; nearest-neighbours distinguished (CH2) — **A** | MED (gallego2026 coined "feedback engineering" concurrently) | 🔧 lead with the deltas; cite gallego as concurrent axis-namer |
| Significance (why the empty cell MATTERS, not just that it's empty) | mechanism generalizes beyond finance | mechanism reframe + EDA — **B** | MED (softer than the novelty case) | 🔧 one-clause "why beyond finance" in CH1 |
| Mechanism-as-headline reframe | Okhrati rewards depth/mechanism; the null is a boundary condition | design choice, pre-freeze | LOW | ✅ |

## Identification
| decision | rationale | evidence + grade | fragility | status / fix |
|---|---|---|---|---|
| Only the reward varies across arms | isolates the feedback-content effect | `src/arms/factory.py` (feedback_kind is the only per-arm variation); test-guarded — **A** | LOW | ✅ (runtime guard is test-only — a future refactor risk, noted) |
| Fixed SB3 SAC agent (TQC secondary) | static-CVaR is time-inconsistent/non-Markovian → the reward channel is the forced injection point | structural argument (`02_CHAPTER_theory.md`) — **A/B** | LOW | ✅ |
| Fed tail is ENDOGENOUS (disclosed, not "agent-independent") | the estimator fits the trained policy's own returns | `src/feedback/measurement.py` docstring — **A** | LOW | ✅ (foregrounded, not hidden) |
| Thinking common-mode within a model → headline thinking-invariant | same model+config authors both arms | empirical per-model verification 2026-07-25 — **A** | LOW | ✅ |

## Arms & baselines
| decision | rationale | evidence + grade | fragility | status / fix |
|---|---|---|---|---|
| 7 arms, each control bound to a named threat | one-to-one threat→control mapping (Table 4.1) | `config/arms.yaml` + CH4 — **A** | LOW | ✅ |
| H1 (LLM vs hand-designed) currently report-only / snooped-descriptive | selection on the sealed leg without archived val fitness | `PREREGISTRATION.md` — **A** (that it's weak) | HIGH→resolving | ✅ **R105 (2026-07-26)**: the graphical validity tier is registered; H1's DE-SNOOP (val-select best-of-4 + score on the sealed test) is candidate node N6 (ratification-pending) |
| H4 (LLM vs random/bayes search) secondary | multiplicity/power at design time | `config/preregistration.yaml` — **A** | HIGH→resolved | ✅ **R105 (2026-07-26)**: promoted to node N4 in the graphical validity tier (`bretz2009graphical`), ratification-pending |

## Feedback vector
| decision | rationale | evidence + grade | fragility | status / fix |
|---|---|---|---|---|
| CVaR sub-vector (cvar_01/05/10/25) | Kusuoka/Acerbi spanning of coherent risk | theory + literature — **B** | LOW | ✅ |
| left_tail_mass (k=2.0σ) | tail-mass summary | **C** (k=2.0 asserted, "frozen", no derivation) | MED | 🔧 justify k or reclassify as engineering stat |
| robust_skew / Bowley | tail-asymmetry summary | **C** (anchors + "not covered by the elicitability theorems") | MED | 🔧 justify anchors or reclassify; fix the mislabel ("left-tail skew" → Bowley) + sign convention |
| α-grid {1,5,10,25}% | a discretisation of the CVaR-level axis | **C** (acknowledged-arbitrary; no sensitivity run) | MED | 🔧 cheap grid-robustness exhibit |

## Parameters
| decision | rationale | evidence + grade | fragility | status / fix |
|---|---|---|---|---|
| B* = 400k steps | measured convergence knee | pre-committed extended-curve rule; paired ascents — **A** | LOW | ✅ |
| Seed ladder (30→…→568) | σ_D pilot fired the >0.10 trigger | σ_D=0.369 measured — **A** | LOW | ✅ |
| K=5 search width | 30 candidates / 6 arms | **C** (budget arithmetic; below Eureka's K=16 executability floor) | MED/HIGH | 🔧 report the first-gen executable rate as a pre-registered adequacy check |
| Fitness = DSR | reward-independent, skew/kurtosis-corrected, un-hackable selection | Bailey-LdP — **B**; BUT selection uses a within-series variance PROXY, not canonical DSR | MED | 🔧 disclose the exact selection estimator |
| **SESOI = 0.05 DSR** | "smallest practically-relevant edge" | **C (fiat — no derivation; the equivalence LINCHPIN)** | **HIGH** | 🔧 **A4**: derive from txn-cost breakeven + portfolio-choice literature + DSR-native |

## Data
| decision | rationale | evidence + grade | fragility | status / fix |
|---|---|---|---|---|
| univ5 panel (Refinitiv, survivorship-free, PIT) | licensed, real, point-in-time | provenance-captured — **A** | LOW | ✅ |
| Split C (2005-16 / 17-19 / 20-25→26) | out-of-sample tail regime in test | design choice — **A/B** | LOW–MED (single macro-regime in test — see F3) | 🔧 disclose; consider a path-aware corroborator |
| Delisting policy (liquidate_to_cash) | conservative, ratified | R44/R73 — **A** | LOW | ✅ |

## Models
| decision | rationale | evidence + grade | fragility | status / fix |
|---|---|---|---|---|
| Confirmatory = Opus 5 | GA, one-frontier, attribution-verified, price-identical | R102 live verification — **A** | LOW | ✅ (thinking now verified off) |
| 10-leg open/closed roster + family pairs | ecosystem diversity + confound-free capability pairs | model sweep — **A/B** | MED (thinking uniformity) | 🔧 **R104** |
| Per-model thinking config | reproducibility + the masking confound + task-fit | empirical per-model verification (only gemini can't disable) + literature — **A/B** | MED→LOW | 🔧 **R104**: uniform reasoning-off + off-vs-high ablation + handle gemini |

## Analysis
| decision | rationale | evidence + grade | fragility | status / fix |
|---|---|---|---|---|
| H2 co-primary IUTs (Sharpe-RA + CVaR-Tail) | two pre-registered performance channels | design — **A** | HIGH (Sharpe leg equivalence power-starved; predicted-tie under λ=0) | 🔧 reframe onto tail+mechanism; A2 drive seeds→~400; A3 add well-powered backbone |
| Multiplicity (IUT + BH-FDR) | error-rate control | design — **A** | LOW→ (strengthens under R105 graphical hierarchy) | 🔧 R105 |
| Mechanism instruments (SQ1-3, report-only) | the actual originality | SQ1 Spearman n=30 — **B**, underpowered | HIGH | 🔧 A3 promote the positive-control into core; pre-commit decision rules |
| Pooled cross-model bounded-effect | where the Sharpe precision now lives (R101) | `src/inference/cross_model.py` — **A** | MED (dependence-honest; seed-limited) | ✅/🔧 |
| Capability gradient g(capability) | the numeracy-bottleneck prediction | 2/10 SWE-bench anchors — **B/C** | MED | 🔧 foreground the pair DiDs; label cross-family descriptive |

## Theory
| decision | rationale | evidence + grade | fragility | status / fix |
|---|---|---|---|---|
| Blackwell garbling → envelope spine | scalar is a garbling of the vector; the envelope gap is the empirical object | proofs (post the M1-M13 fixes) — **A** | LOW | ✅ |
| Risk-measure chain (Artzner / VaR-subadditivity / Gneiting / Fissler-Ziegel) | exactness Okhrati checks | literature, first-hand — **A/B** | LOW | ✅ (verify sign conventions in the Conventions box) |

## Reproducibility
| decision | rationale | evidence + grade | fragility | status / fix |
|---|---|---|---|---|
| Analysis = bit-exact replay | seeded, pinned, parallel==serial byte-identical | `requirements.lock` + seeding + proof — **A** | LOW (device-conditional, disclosed) | ✅ |
| Reasoning-pin round-trip evidence | R85 claim | now IMPLEMENTED + verified (deepseek 145, qwen 650 reasoning tokens captured) — **A** | LOW | ✅ (R103 + audit-fix) |
| "Self-hosted leg" (permanence anchor) | closes the gap closed models can't | **the claim is currently FALSE — no self-hosted leg exists** | MED | 🔧 **A5**: actually self-host Qwen-9B-bf16 on Myriad |

---

## The weakest links (the fragility-ordered close list)
1. **SESOI = 0.05 (C, HIGH)** — the equivalence linchpin, asserted → **A4 derivation.**
2. **H2 equivalence power (HIGH)** + **mechanism instruments underpowered (HIGH)** → **A3 promote H1/H4 to a well-powered backbone** + reframe + drive seeds→~400.
3. **H1/H4 demoted (HIGH)** → ✅ **R105 (2026-07-26): graphical validity tier registered** (H3/H4/N5 confirmatory; H1=N6 de-snoop candidate; ratification-pending).
4. **K=5 (C, MED/HIGH)** → executable-rate adequacy check.
5. **2/6 tail components + α-grid (C, MED)** → justify/reclassify + grid-robustness exhibit.
6. **Self-hosted-leg claim (false, MED)** → **A5.**
7. **Thinking uniformity (MED→LOW)** → **R104.**

Every HIGH-fragility / C-grade linchpin has a concrete fix already scoped. Closing them, in fragility order, IS the path to the non-fragile backbone.

## Exhaustive backbone audit — additions + calibration (2026-07-25, TWO independent auditors)
Both auditors independently confirmed the seed grades AND converged on the SAME grade-capping link (SESOI→equivalence-power). New / refined load-bearing findings (all cite file:line, verified first-hand):

| finding | grade | fragility | fix |
|---|---|---|---|
| **SESOI derivation** — RESOLVED (R104, 2026-07-25). The 0.05-DSR SESOI is now DERIVED from an economic band (cost-breakeven 0.0055 < 0.0756 ann-Sharpe < practitioner 0.10) + registered as FROZEN DATA (`inference.sesoi_derivation`; `tests/test_sesoi_derivation.py`). The Sharpe↔DSR gap is NOT a bug: the TOST is already DSR-native and the T2.5 reconciliation + the INCONCLUSIVE branch already handle it (`CAMPAIGN_power.md`: MDE@80%≈0.120 DSR > 0.05 → a Sharpe-only non-rejection is reported INCONCLUSIVE, never "equivalence"). | A | **LOW** | ✅ done R104 |
| **H2-Tail bounded-effect** — RESOLVED / false-concern (R104 verify, 2026-07-25). The tail bounded-effect IS registered: the R86 pooled 90% seed-block-bootstrap CI on the (dist−scalar) CVaR-5% difference (`preregistration.yaml` synthesis_exactness.pooled_bound), reported in return units AND as a % of scalar CVaR. The "0.25·\|scalar CVaR\| margin" was a first-draft MISREAD (no such number exists in the design) — retracted; no separate tail margin is needed or registered. | A | **LOW** | ✅ verified (no fix) |
| **candidates=30 MISLABELED** — classed MEASURE-saturation but the evidence note admits *"arms still improving… budget too small"* (`DESIGN_DETERMINATION.md:30`) → a mechanism null could be under-search | C | **HIGH** | 🔧 relabel FIX/disclosed-limitation; lean on the oracle-headroom instrument |
| **Capability gradient PRIMARY ANCHOR DEAD** — SWE-bench-Verified published for only 2/10 legs (`preregistration.yaml:308`) → the regression cannot run (`cross_model.py:275`) → "gradient" collapses to 2 pair-DiDs + circular M2 | A (that it's dead) | **HIGH** | 🔧 down-rank "gradient"→"pair contrasts"; add ≥1 card-published-SWE-V leg |
| **Per-model authoring reliability MEASURED (2026-07-25, grade-A)** — sandbox gate-pass over 6 diversity-varied authorings: qwen3.5-9b **1/6 (17%)**, qwen3.6-27b 5/6, gemini-2.5-flash (R105 substitute) 5/6, deepseek-v4-pro 6/6. The 9B floor authors the least-robust reward code (shape 31≠30, None-state, TypeError, ast-gate) = the numeracy-bottleneck thesis + the gradient's BOTTOM ANCHOR. Campaign handles it: a sandbox-reject consumes one author draw + is logged (`loop.py:395,470`), the search continues, a leg failing the T0 floor reports as a finding (never a vote) — NO stall. | A | **LOW** | ✅ measured; feeds the reliability table + capability gradient |
| **Closed capability pair NOT confound-matched** — Haiku (4096, no reasoning) vs Opus-5 (8192) → the DiD conflates capability with token-budget/thinking | A | **HIGH** | 🔧 to RESOLVE by R106 (uniform reasoning-off + matched caps; NB R105 is the A3 validity tier, R104 the SESOI) |
| **Opus-5 thinking record CONTRADICTION** — prereg/llm.yaml assert "adaptive thinking BY DEFAULT" (drives 8192) but the LIVE test shows Opus OFF by default; Anthropic legs never round-trip-gated | C→resolved | MED | 🔧 DONE: the readiness gate confirmed Opus-5 OFF by default + meaningful (2026-07-25); correct the 'adaptive-by-default' claim in R106 |
| **Self-hosted leg ABSENT** — the "self-hosted on Myriad" permanence pitch is unrealized (all hosted API) | A | MED | 🔧 A5: self-host one open leg OR strike "self-hosted" |
| **Stale MODEL_CARD + REPRODUCIBILITY_CHECKLIST** — 30 seeds / 50k steps / laptop-only / old panel, all superseded | A | MED→resolving | 🔧 CHECKLIST regenerated 2026-07-25 (seeds→ladder / steps→400k / buffer-decoupled / compute→Myriad / test-count→2,057); MODEL_CARD + DESIGN_DETERMINATION regenerating |
| **DSR selection = within-series variance PROXY** — not the canonical cross-trial DSR the paper cites (`deflated_sharpe.py:180`; common-mode → not an ID threat) | A | MED | 🔧 one methods sentence disclosing the proxy |
| **`kvasiuk2026madevolve`** — RESOLVED / KEEP (2026-07-25 audit). The cite is VERIFIED REAL: `refs.bib:1857-1861` (arXiv 2605.23007, q-fin.TR, 4 named authors incl. Münchmeyer), first-hand-verified 2026-07-02 (the refs.bib comment clears the old DO-NOT-CITE flag; corroborated by NOVELTY_FENCE_SWEEP + RELATED_WORK_WATCH + CHANGELOG). The DO-NOT-CITE label was STALE, not the citation. | A | **LOW** | ✅ keep; mandatory pre-submission abs-page re-verify |
| **K=16 stale** in `DESIGN_DETERMINATION.md:18` — contradicts the design K=5 | A | MINOR | 🔧 fixing 2026-07-25 (stale-doc sweep) |
| **N6 val-select was DEAD CODE** — RESOLVED (2026-07-26, self-caught in a non-fragility hunt on my own N6 promotion). H1's confirmatory promotion registered a val-select de-snoop, but `run_campaign._baseline_winner_record` archives `val_fitness=NaN` → `beat_human_baseline` ALWAYS falls back to the White-2000 test-snoop → N6 would have been an UNBACKED confirmatory claim. FIX (Tamer "make it smart + sound"): reframe as a snoop-free **IUT** — beat EVERY canon member one-sided at α == beat the best (`berger1982iut`), selecting no comparator (nothing to snoop, no fragile baseline val-roll). Implemented + tested (`beat_human_baseline.iut`; `test_iut_*`; freeze RC=0; 119 tests). | A | ~~HIGH~~→**RESOLVED** | ✅ done c808117 |
| **Regime config contradiction** (audit #10) — RESOLVED (2026-07-26). `power_analysis.py:308` claimed the gold vix is a decimal so regimes thresholds "never trigger → count collapses to 1 (live bug)", but `regimes.yaml:5` said fixed. VERIFIED: `loaders.load_gold_panel` head-detects + rescales vix×100→points (`loaders.py:455-458`) → regimes.yaml correct, the comment STALE. Comment fixed + `max_plausible_independent_regimes:12` registered (was a silent fallback). | A | ~~MINOR~~→**RESOLVED** | ✅ done c4154ef |
| **H4 N4 comparator strawman-risk** (audit #3 + comparator-research A) — the 2 H4 optimizers (random+GP-EI) search ONE fixed 6-primitive family (`cvar_alpha`/`window` FIXED) → "you beat a crippled search; that's search-space richness, not designer quality". FIX registered: expand to the DFO toolkit {random, GP-EI, TPE, CMA-ES} (cites ADDED c808117; multi-fidelity Hyperband/BOHB pruned as inapplicable under matched-candidate-count) + report LLM-vs-max-over-toolkit (parallels N6). | B | MED | 🔧 registered; BUILD-pending (deps `cma`/`optuna` vet+pin; Okhrati on confirmatory-vs-toolkit) |
| **Allocator suite lacks the tail-optimal benchmark** (comparator-research B) — for a TAIL study the min-CVaR (Rockafellar-Uryasev) allocator is the decisive missing benchmark ("beats even the classical tail-optimal allocator on its own turf"). The 8 are otherwise comprehensive (audit LEAVE-ALONE confirms). FIX registered: add `min_cvar` (near-free deterministic backtest, mirror `min_variance`). | B | LOW | 🔧 registered; BUILD-pending |
| **Search-adequacy severity** (audit #1, TOP grade-mover) — K=5/30/6 sits below Eureka's K=16 and weak legs may author <1 executable/gen → a reviewer reads the null as "under-search", not "a boundary". FIX registered: a search-ADEQUACY instrument (declared first-gen executable-rate + an oracle-headroom/saturation exhibit) + lean the null's severity on SQ1 responsiveness (UPSTREAM of search width — if the LLM never conditions on the fed numbers, K is moot). Relabel candidates=30 FIX/disclosed-limitation. | C | **HIGH** | 🔧 registered; design-pending |
| **CH4 prose ↔ config contradiction** (audit #2, communication gate) — CH4:220-222 still "max over FOUR, DESCRIPTIVE-ONLY" + CH4:274/301 "Bonferroni-across-four" while config = 11-canon/N6-confirmatory/graphical-tier. Understates the strongest new result + is an internal contradiction. FIX: rewrite CH4 §4.7+Table 4.1+theory §3.7 to the 11/N6/tier design. | A | MED | 🔧 registered; GATED on R105 ratification (V2 registry) |
| **Fed vector 2/6 components asserted** (audit #5) — `left_tail_mass` (k=2.0σ) + `robust_skew` (Bowley) sit OUTSIDE the §3.5 elicitability theory (which covers only the 4 CVaR levels; theory §3.7 concedes it). FIX: derive-or-reclassify (justify k=2.0/Bowley with a cite OR reclassify as engineering summary stats) + a cheap fed-vector ABLATION (H2-Tail survives dropping the 2) + fix the `robust_skew` "left-tail skew" label/sign. | C | MED | 🔧 registered |
| **α-grid {0.01,0.05,0.10,0.25} arbitrary** (audit #8) — acknowledged-arbitrary, no sensitivity run (`cvar_01` also flagged high-variance). FIX: a report-only grid-robustness exhibit (authored-code responsiveness / H2 ordering invariant under a denser/sparser grid). | C | LOW | 🔧 registered |
| **Single sealed test PATH** (audit #11) — one 2020-2026 realization (walk-forward DEFERRED R43, disclosed CH4:39-51). FIX (optional severity-add): elevate the theory's regime-CONCENTRATION corollary (§3.6) to a report-only DIRECTIONAL exhibit (predicted sign) — free, uses a corollary already derived. | A | MED (disclosed) | 🔧 registered |

**Grade-capping link (both auditors) — NOW STRENGTHENED (2026-07-25):** the SESOI is DERIVED + registered as frozen data (R104), no longer asserted, and the Sharpe↔DSR unit handling was already rigorous (T2.5 reconciliation + INCONCLUSIVE branch). The bounded-equivalence backdrop remains the most CONDITIONAL promise in the PDF (power-limited below n\*≈173 seeds): keep it explicitly conditional/inconclusive; never let a chapter assert "equivalence". The mechanism headline is insulated (it pivots to mechanism + the pooled bounded-effect).
**Strengths confirmed grade-A:** identification (code-enforced `assert_fixed_agent_across_arms`), the fixed-SAC structural argument (Bäuerle-Ott/Lim-Malik), the theory spine (post M-fixes), the endogeneity honesty (exemplary), B*/seeds/delisting/panel (measured in-repo), the multiplicity (IUT ≤ α + BH-FDR).
