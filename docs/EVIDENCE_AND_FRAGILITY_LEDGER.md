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
| H1 (LLM vs hand-designed) currently report-only / snooped-descriptive | selection on the sealed leg without archived val fitness | `PREREGISTRATION.md` — **A** (that it's weak) | HIGH (the "does the LLM help?" evidence is demoted) | 🔧 **R105**: promote to a validation-selected confirmatory validity tier |
| H4 (LLM vs random/bayes search) secondary | multiplicity/power at design time | `config/preregistration.yaml` — **A** | HIGH | 🔧 **R105**: promote via a graphical multiplicity hierarchy |

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
3. **H1/H4 demoted (HIGH)** → **R105.**
4. **K=5 (C, MED/HIGH)** → executable-rate adequacy check.
5. **2/6 tail components + α-grid (C, MED)** → justify/reclassify + grid-robustness exhibit.
6. **Self-hosted-leg claim (false, MED)** → **A5.**
7. **Thinking uniformity (MED→LOW)** → **R104.**

Every HIGH-fragility / C-grade linchpin has a concrete fix already scoped. Closing them, in fragility order, IS the path to the non-fragile backbone.

## Exhaustive backbone audit — additions + calibration (2026-07-25, TWO independent auditors)
Both auditors independently confirmed the seed grades AND converged on the SAME grade-capping link (SESOI→equivalence-power). New / refined load-bearing findings (all cite file:line, verified first-hand):

| finding | grade | fragility | fix |
|---|---|---|---|
| **SESOI unit-mismatch** — margin is val-DSR but the H2-RA headline test is test-Sharpe → the Sharpe co-primary can only land INCONCLUSIVE (`CH4:263-265`, MDE@80%≈0.120 DSR ≫ 0.05) | C | **HIGH** | 🔧 A4: run TOST natively in DSR units OR register the Sharpe leg bounded-effect-only |
| **H2-Tail margin UNREGISTERED** — the fractional CVaR band (0.25·\|scalar CVaR\|) is prose-only in `CH4:265-270`; no pinned config value (forking-path risk) | C | **HIGH** | 🔧 A4: pin the tail margin as a frozen numeric BEFORE freeze |
| **candidates=30 MISLABELED** — classed MEASURE-saturation but the evidence note admits *"arms still improving… budget too small"* (`DESIGN_DETERMINATION.md:30`) → a mechanism null could be under-search | C | **HIGH** | 🔧 relabel FIX/disclosed-limitation; lean on the oracle-headroom instrument |
| **Capability gradient PRIMARY ANCHOR DEAD** — SWE-bench-Verified published for only 2/10 legs (`preregistration.yaml:308`) → the regression cannot run (`cross_model.py:275`) → "gradient" collapses to 2 pair-DiDs + circular M2 | A (that it's dead) | **HIGH** | 🔧 down-rank "gradient"→"pair contrasts"; add ≥1 card-published-SWE-V leg |
| **Closed capability pair NOT confound-matched** — Haiku (4096, no reasoning) vs Opus-5 (8192) → the DiD conflates capability with token-budget/thinking | A | **HIGH** | 🔧 RESOLVED by R104 (uniform-off + matched caps across the pair) |
| **Opus-5 thinking record CONTRADICTION** — prereg/llm.yaml assert "adaptive thinking BY DEFAULT" (drives 8192) but the LIVE test shows Opus OFF by default; Anthropic legs never round-trip-gated | C→resolved | MED | 🔧 archive the Opus/Haiku/Sonnet smoke (running now) + correct the claim (R104) |
| **Self-hosted leg ABSENT** — the "self-hosted on Myriad" permanence pitch is unrealized (all hosted API) | A | MED | 🔧 A5: self-host one open leg OR strike "self-hosted" |
| **Stale MODEL_CARD + REPRODUCIBILITY_CHECKLIST** — 30 seeds / 50k steps / laptop-only / old panel, all superseded (MODEL_CARD mtime 07-25 but still says laptop-only) | A | MED | 🔧 regenerate before any deposit |
| **DSR selection = within-series variance PROXY** — not the canonical cross-trial DSR the paper cites (`deflated_sharpe.py:180`; common-mode → not an ID threat) | A | MED | 🔧 one methods sentence disclosing the proxy |
| **`kvasiuk2026madevolve` cited while DO-NOT-CITE-flagged** — possible hallucination cited in `CH2:105` (supervisor co-authored corpus papers) | — | **HIGH-if-caught** | 🔧 verify the arXiv id first-hand OR cut the sentence |
| **K=16 stale** in `DESIGN_DETERMINATION.md:18` — contradicts the frozen K=5 | A | MINOR | 🔧 fix |

**CONFIRMED grade-capping link (both auditors):** SESOI (C2) → equivalence-power (A3). The mechanism headline is insulated (it pivots to mechanism + the pooled bounded-effect), but the bounded-equivalence backdrop is the most fragile promise in the PDF — keep it explicitly conditional/inconclusive; never let a chapter assert "equivalence".
**Strengths confirmed grade-A:** identification (code-enforced `assert_fixed_agent_across_arms`), the fixed-SAC structural argument (Bäuerle-Ott/Lim-Malik), the theory spine (post M-fixes), the endogeneity honesty (exemplary), B*/seeds/delisting/panel (measured in-repo), the multiplicity (IUT ≤ α + BH-FDR).
