# Evidence ledger — every operative claim, its evidence grade, and the upgrade path (2026-07-12)

> Tamer (standing rule, 2026-07-12): *"absolutely everything must have very strong evidence."*
> This ledger grades every claim currently steering decisions. Grades: **A** = replicated,
> direct measurement; **B** = single direct measurement (n=1) or short-horizon extrapolation;
> **C** = calibrated proxy / model-derived. Every B/C carries its named upgrade path — most upgrade
> AUTOMATICALLY as the fleet produces (each task ledger is a new replicate). Maintained forward:
> a claim used in the PDF must be grade A (or its grade stated).

| # | Claim | Grade | Evidence today | Upgrade path (→A) |
|---|---|---|---|---|
| 1 | Apptainer-on-node campaign path works | **A** | 22+ successful node records across 4 batch families, 2 legs (search-spec + packed), real+synthetic gold, 4+ nodes | — |
| 2 | Cross-node bitwise determinism | **B+→A pending** | 1 pair (seed 777, e00a-007 vs e00a-017): val_fitness identical to last digit, val_returns byte-equal | **p4detb queued (774334, seed 778)** → 2 pairs = A |
| 3 | F saturates ≈2.5 at pack-5 | **A (UPGRADED 2026-07-12 ~15:30)** | curve F(1)=1.00/F(2)=1.30/F(3)=2.16/F(5)=2.48/F(8)=2.51 **+ REPLICATE p1pack5b on a different node (e00a-011, 1,571 s vs 1,847 s): F(5) ≈ 2.2–2.6, centered on the original** — the campaign policy (`pack 5, cores 5`, 3.74 tr/GPU-h) rests on replicated measurement | — |
| 4 | Per-task fixed overhead ≈860 s | **B** | derived from ONE solo task (p4det-t1: 1,348−489 s) | auto-upgrades: every completed task ledger adds a point; recompute distribution at gate (p4det-t2 implies ~477 s on e00a-017 → overhead varies with node!) |
| 5 | Campaign throughput 3.74 trainings/GPU-h at B\* | **C+** | pack-5 aggregate (253 st/s, n=1) + amortization MODEL (overhead from #4; B\*-length wall never directly measured packed) | the P6 Myriad tasks measure real 100k–1.6M walls; a pack-5 task at B\* falls out of the campaign's first hours — restate then |
| 6 | Per-training wall varies ±40% with node co-tenancy | **A−** | p4det pair: identical work 1,348 vs 966 s; p6 100k task 2,810 s vs model 1,838 s | accumulates automatically; report as a distribution in the compute section |
| 7 | Hold policy self-releases (~1.5–2 h sweeps) | **B+** | 2 observed release sweeps + tail-holds re-applied to new arrays; not a documented cluster contract | behavioural only — treat as weather, not contract; chunked-fleet shape removes reliance |
| 8 | B\* = 200k is past the eval knee | **⚠ REOPENED 2026-07-13 (was A−): DOWNGRADED to B pending the extended curve** | The 100k–400k verdict stands AS SCOPED (laptop eval-stat units, both winners, 3v3: no CI-separated ascent 200k→400k). **BUT claim 15 (1.6M-s0 val-DSR 0.187 vs 100k-s0 0.041, same frozen source, real return-path gain) contradicts the flat EXTRAPOLATION beyond 400k** — "past the knee" was over-claimed relative to the measured range; Tamer's "find the global minimum" commission is NOT closed. Note the units caveat: the 3v3 verdict is in laptop eval-stat units; the Myriad rows are val-DSR — the decisive comparison is the same-protocol Myriad curve | **In flight: the full 5-budget × 3-seed × 2-winner same-protocol curve** ({100k,200k,400k}×3×2 = 771972; 800k×3×2 = 774923 RUNNING; 1.6M×3×2 = 774924). Apply the PRE-COMMITTED extended rule (below) when complete |
| 9 | Fed-delta noise floors (marginal ±3.3e-3; paired 1e-4–8e-4) | **C (calibrated proxy)** | EW-30/tilted-book block bootstrap on the univ5 train window — a PROXY for candidate policies | replay-based paired bootstrap on ACTUAL candidate returns at the gate (`fed_delta_snr --paired-se` hook built) |
| 10 | 63–87% of headline fed deltas resolvable; λ_att 0.85–0.98 | **C+ (directional)** | prototype archive (Sonnet, old window) × the C-grade floors of #9 | recompute on the CAMPAIGN archive with #9's exact floors at the gate — the PDF cites only that version |
| 11 | Qwen authors sandbox-rejected code at a nonzero rate | **B** | 2 observed rejects in the rehearsal (small n, uncounted denominator) | count rejects/attempts from the failures ledgers when the rehearsal/prototype complete (M2 capability-floor exhibit) |
| 12 | σ_D = 0.369 / σ_seed = 0.244 / ρ = −0.141; CVaR leg σ_D = 0.0015 | **A− (pre-registered pilot)** | 15 CRN pairs, fixed rewards, clean pilot (the E1 basis) | rung 100 of the ladder tightens σ_D to ±10% in-campaign (designed-in upgrade) |
| 13 | Laptop↔cluster science parity | **B (by construction) → A pending** | same primitives by design (certified); no cross-substrate result pair compared yet | the P6 parity pairs: same (reward, budget, seed) on both substrates — statistical agreement expected (NOT bitwise: different GPU arch/TF32); first pair completes today |
| 14 | The four bug fixes hold (tilde, provider, batch-tag, MSYS) | **A** | each: root-caused, fixed, regression-locked, and the failure mode re-exercised live post-fix (submissions clean) | — |
| 15 | Authored dist winner keeps improving val-DSR to 1.6M steps (0.041@100k → 0.187@1.6M, CRN seed 0) | **B (single seed, single winner)** | record verified first-hand 2026-07-13: same reward_source_hash as the 100k siblings, same 694-day val window, mean daily return 3.6e-4 vs 0.99e-4 at equal vol — a REAL training effect, not a metric artifact | seeds 1–2 + the scalar winner + the 200k/400k/800k same-protocol rows (all queued) → grade A either way; feeds the claim-8 rule |

**PRE-COMMITTED EXTENDED B\* RULE (written 2026-07-13 ~11:00, BEFORE the remaining 25 curve points
land — the rule may not be chosen after seeing the numbers).** For each winner separately, on the
same-protocol Myriad val-DSR rows with CRN-paired seeds: if the paired mean ascent
`mean_s[eval(b_hi) − eval(200k)] > 2 × SE_s(paired diff)` for ANY b_hi ∈ {400k, 800k, 1.6M}, then a
**B\* amendment PROPOSAL goes to Tamer pre-freeze** with the two honest options: (a) raise B\* to the
measured knee within compute feasibility (800k ≈ 4× campaign cost; 1.6M ≈ 8× — likely infeasible at
n=403, feasible at reduced n: HIS trade-off to make), or (b) keep B\*=200k matched-compute BY DESIGN
and add the MANDATORY learning-curve exhibit + a reframed training-adequacy limitation (identification
is untouched either way — B\* is identical across arms; what changes is the interpretation scope:
"at matched compute 200k", not "at convergence"). No CI-separated ascent at 3 seeds → claim 8 returns
to A with the extended range measured.

**Standing procedure from here:** (i) new decision-steering numbers enter THIS ledger with a grade at
birth; (ii) the bank gate re-computes #4/#5/#9/#10 on campaign data before any PDF use; (iii) the PDF's
compute/mechanism sections cite only grade-A entries or state the grade explicitly (honesty register).
