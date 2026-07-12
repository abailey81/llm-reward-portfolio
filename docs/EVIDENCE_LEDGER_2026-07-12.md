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
| 8 | B\* = 200k is past the eval knee | **A− (UPGRADED 2026-07-12 ~13:00)** | hand-written 25k–350k flat (2 ladders, 3 seeds) **+ AUTHORED 100k–400k complete 3v3 rows, BOTH winners, rule verdict: no CI-separated ascent (dist +8.1e-5 vs bar 1.1e-4; scalar +2.0e-4 vs 3.0e-4)** — failed rungs re-run before the rule fired (no verdict on holes) | Myriad p6ext 800k/1.6M rungs (queued, honest walltimes) extend to 8×B\* → full A |
| 9 | Fed-delta noise floors (marginal ±3.3e-3; paired 1e-4–8e-4) | **C (calibrated proxy)** | EW-30/tilted-book block bootstrap on the univ5 train window — a PROXY for candidate policies | replay-based paired bootstrap on ACTUAL candidate returns at the gate (`fed_delta_snr --paired-se` hook built) |
| 10 | 63–87% of headline fed deltas resolvable; λ_att 0.85–0.98 | **C+ (directional)** | prototype archive (Sonnet, old window) × the C-grade floors of #9 | recompute on the CAMPAIGN archive with #9's exact floors at the gate — the PDF cites only that version |
| 11 | Qwen authors sandbox-rejected code at a nonzero rate | **B** | 2 observed rejects in the rehearsal (small n, uncounted denominator) | count rejects/attempts from the failures ledgers when the rehearsal/prototype complete (M2 capability-floor exhibit) |
| 12 | σ_D = 0.369 / σ_seed = 0.244 / ρ = −0.141; CVaR leg σ_D = 0.0015 | **A− (pre-registered pilot)** | 15 CRN pairs, fixed rewards, clean pilot (the E1 basis) | rung 100 of the ladder tightens σ_D to ±10% in-campaign (designed-in upgrade) |
| 13 | Laptop↔cluster science parity | **B (by construction) → A pending** | same primitives by design (certified); no cross-substrate result pair compared yet | the P6 parity pairs: same (reward, budget, seed) on both substrates — statistical agreement expected (NOT bitwise: different GPU arch/TF32); first pair completes today |
| 14 | The four bug fixes hold (tilde, provider, batch-tag, MSYS) | **A** | each: root-caused, fixed, regression-locked, and the failure mode re-exercised live post-fix (submissions clean) | — |

**Standing procedure from here:** (i) new decision-steering numbers enter THIS ledger with a grade at
birth; (ii) the bank gate re-computes #4/#5/#9/#10 on campaign data before any PDF use; (iii) the PDF's
compute/mechanism sections cite only grade-A entries or state the grade explicitly (honesty register).
