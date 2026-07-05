# MAX-THROUGHPUT run plan (2026-07-06) — exploit the hardware fully; cut ZERO science

**Tamer's directive.** Everything connected with the laptop run must use the machine's full power —
absolute maximum parallelisation — with speed-ups achieved ONLY by hardware exploitation and
scheduling, never by making the dissertation less advanced (B\*, seeds, candidates, arms, analyses,
instruments: all untouchable).

**The measured constants** (σ_D farm + solo bench, RTX 4050 @ Turbo 140 W + clock lock):
one 200k-step training ≈ **61 min solo** (n=1) or ≈ **85 min/cell at 3 concurrent** (the proven
throughput ceiling ⇒ ~28.3 min/training effective; n_gpu=4 is a measured OOM and is CLI-refused).

## Where every stage stands (after the 2026-07-06 hardening)

| Stage | Units | Execution today | Wall @ ceiling | Status |
|---|---|---|---|---|
| SEARCH (7 arms × 30) | 210 trainings | **SERIAL headline** (`--search-gpu 0`, ratified 2026-07-01) | ~8.9 d serial vs **~4.1 d at 3 workers** | the ONE big lever — see L1 |
| TEST (7 arms + 4 baselines) × seeds | 330 @ n=30; ~850 @ the 350-seed amendment | `run_recycling`, **3 GPU workers, saturated continuously** (as-completed archival keeps slots hot) | ~6.5 d @330; ~16.7 d @850 | **already maximal** ✓ |
| H3 single-shot (search 30 + test 30) | 60 | search currently SERIAL via `run_winner_search` | ~1.3 d serial search vs ~0.4 d parallel | L2 |
| Sub-experiments (SQ3b legible/raw) | ~2×5×K | pooled trainings | hours | runs in the GPU-busy window ✓ |
| Analysis/figures/PDF | — | CPU-only | hours | overlaps the run ✓ |

## The levers (all pure scheduling — identical science, byte-equivalent per-unit results)

**L1 — SEARCH-stage 3-way parallelism (the ~5-day lever) — APPROVED by Tamer 2026-07-06 (ADR-052);
the mechanical label change lands in the batched seed-ratification amendment.** The frozen headline protocol is `serial_reflect_on_best`. The parallel driver
(`--search-gpu 3`) implements the SAME reflect-on-generation-BEST semantics and, as of today
(S21/S15 fixes), is fully **resume-safe for all 7 arms** (hash-verified replay; as-completed
archival; zero re-billing). Within a generation the cpg=5 candidates train concurrently — each
candidate's training is seeded-deterministic and device-fixed, so per-candidate results are the
same numbers the serial loop would produce; what changes is the RUN-ID/ledger layout and the
executed-protocol label (why it is amendment-gated, not ops-free). **Effect: search ~8.9 d → ~4.1 d
(≈ −5 days).** NB the ~23-day plan quoted at the seed decision already ASSUMES 3-worker search —
without this amendment the serial-headline total is ~5 days LONGER than that plan. Decide at seed
ratification (one dated amendment covers both).

**L2 — H3 single-shot search parallelism (~−0.9 day) — small build, science-clean.** The H3
control is best-of-30 at generations=1: NO reflection chain exists, so its 30 candidates are
embarrassingly parallel by construction (the same argument that makes the TEST leg science-neutral).
Route the H3 search through the device pool (author all 30 prompts up front — authoring is
minutes — then pool-train). BUILT 2026-07-06 (ADR-052): `--search-gpu N` now routes the H3 single-shot search through the
parallel driver too.

**L3 — already banked this session (no decision needed):** as-completed streaming keeps all 3
slots continuously hot across batch boundaries (S15); resume never re-trains completed work on ANY
path (serial + parallel, search + test + H3 + sub-experiments); the wedge detector + sentinel mean
a stall costs minutes-to-alarm, not silent days — over a 23-day run, recovered-time is a real
throughput term.

**L4 — run-day machine levers (runbook §0b, unchanged):** Turbo 140 W auto-applies at boot; the
GPU clock lock must be re-applied after EVERY reboot; free-at-launch RAM sweep (≥ ~12 GB free);
Windows-Update pause; ONSTART re-entry. `--cpu` on the REAL run is REFUSED by design (S6): CPU≠CUDA
bit-for-bit on the sealed leg — and it costs nothing, the GPU is the binding resource.

**Rejected as speed levers (they would touch the science):** trimming B\*/seeds/candidates; mixing
CPU workers into the sealed leg; overlapping one arm's SEARCH with another's TEST under the serial
protocol (the serial search occupies one slot; the overlap would starve the test pool below 3 and
complicate the RAM envelope for zero net gain at the same total GPU-hours).

## The 2026-07-06 DEEP DIVE — the full option space (Tamer: "push training time to the absolute
## global minimum; hardware only")

**E — IDLE-SLOT BACKFILL (BUILT TODAY; ops-safe, NO amendment; ≈ −2.3 to −3 days).** During the
serial headline search only 1 of the 3 proven GPU slots trains — 2 slots idle for ~9 days. The H1
baselines (120 trainings) depend on NOTHING the search produces (hand rewards, matched seeds); the
new **`run_campaign.py --baselines-only --gpu 2`** runs exactly that stage as a SECOND process
beside the serial search (1 + 2 = the proven 3-concurrent envelope; ~3 replay buffers ≈ the same
RAM). Science-neutral: every training is seeded-deterministic regardless of co-scheduling; archives
are run-id-keyed + resume-safe; it writes its OWN `baselines_summary.json` + `baselines/` journal
(the campaign's sentinel files untouched; the sentinel unions the extra journal). With E, the H1
tail vanishes INTO the search window. E is the no-amendment fallback that captures most of L1's
value; with L1 approved there are no idle slots and E is unnecessary — pick ONE.

**HAGS — Hardware-Accelerated GPU Scheduling A/B (bench at launch; potential single-digit %).**
The 07-02 perf audit measured ~58% per-step dead time from WDDM submission overhead + P-state
hunting; the clock lock fixed P-states, HAGS is the remaining Windows-level submission-latency
lever. Result-neutral (scheduling only — identical kernels/numerics). Needs a reboot; bench the
single-arm 50k smoke ON vs OFF on run day (runbook §0b candidate row).

**OMP threads 1→4 per worker (BENCH-then-RATIFY; numerics caveat).** Workers pin BLAS/torch to 1
thread (the anti-oversubscription decision); at 3 workers on 14 physical cores, ~11 cores idle
while the env/obs numpy math runs single-threaded. 3×4 threads ≤ 14 cores = no oversubscription →
a real candidate for the CPU-bound step fraction. CAVEAT: BLAS reduction order changes float sums →
NOT byte-identical to the 1-thread config; legitimate ONLY as a pre-freeze ratified executed-config
(thread count is part of the determinism envelope) after an A/B bench shows a material win.

**REJECTED (each violates determinism, physics, or the frozen science — documented so they are not
re-proposed):** a 4th training slot (RAM transition-wave OOM measured at n_gpu=4 + VRAM ceiling;
CPU 4th lane breaks archive-replay determinism via token-race device assignment); batch-size /
buffer / B* / gradient-step changes (frozen agent config = the science); CUDA Graphs / torch.compile
(no Triton on native Windows — ADR-040; manual graph capture = deep SB3 surgery for a bounded gain);
detaching the end-of-training CPU rollout to free the CUDA slot (~5%-class gain, high-risk SB3
surgery); MPS/TCC (Linux/Quadro-only); the iGPU (no CUDA). Authoring latency is <1% (already
overlapped by the pool).

## Decision summary for Tamer
1. **L1 at seed ratification**: amend the executed search mode to the (resume-safe, reflect-on-best)
   3-worker parallel driver → **≈ −5 days**. Recommendation: YES — per-unit numbers identical; it is
   what the ~23-day plan already assumed.
2. **If L1 is declined: E (BUILT — `--baselines-only` backfill, ≈ −2.3 to −3 days, zero amendment)**
   + L2 (H3-parallel) as the remaining fallbacks.
3. **Run-day benches**: HAGS A/B (reboot + 50k smoke); OMP 1→4 A/B (ratify the thread count into the
   executed config ONLY if the win is material — numerics-envelope caveat above).
4. Everything else is at the hardware ceiling; every rejection above is deliberate and documented.
