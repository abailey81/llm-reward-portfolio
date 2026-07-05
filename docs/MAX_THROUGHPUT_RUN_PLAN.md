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

**L1 — SEARCH-stage 3-way parallelism (the ~5-day lever) — AMENDMENT-GATED (Tamer + a dated
amendment).** The frozen headline protocol is `serial_reflect_on_best`. The parallel driver
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
minutes — then pool-train). Worth building iff L1 is declined (L1's amendment covers H3 anyway);
flagged, not built, to avoid two mechanisms for one job.

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

## Decision summary for Tamer
1. **L1 at seed ratification**: amend the executed search mode to the (resume-safe, reflect-on-best)
   3-worker parallel driver → **≈ −5 days** on the campaign. My recommendation: YES — the per-unit
   numbers are the same; the amendment is a scheduling label, and it is exactly what the ~23-day
   plan already assumed.
2. **L2 only if L1 is declined.**
3. Everything else is already at the hardware ceiling.
