# MYRIAD EXPERT DOSSIER (2026-07-24) — the scheduling ground truth, live-probed + doc-verified

> Purpose: everything that actually determines how fast our jobs run on UCL Myriad, verified
> against the LIVE scheduler configuration (`qconf -ssconf`, probed 2026-07-24), the official RC
> docs, and the SGE reference manuals — so the campaign's speed decisions rest on the scheduler's
> real arithmetic, never folklore. Standing order: NEVER lower our job priority (CLAUDE.md ★).

## 0-PRE. ★★★★ 2026-07-26 CAPACITY MEASUREMENT — 636 CORES HELD; THE "96-CORE CEILING" WAS AN ARTIFACT

> **Read this BEFORE §0 and §3 — it supersedes their capacity numbers and refutes one of their levers.**
> Method: staged fleets of independent CPU jobs running the REAL campaign-scale trainer
> (`bench_compute.py --n-assets 30 --batch 256`, $0, no API), 2026-07-26 02:30–04:30 UTC, with live
> `qstat`/`qhost`/`qconf` instrumentation. **70 jobs completed OK**; peak concurrency sampled every 45 s.

**M1 — CAPACITY: 636 cores held (1.99× the previous 320 record), and it was NEVER a fair-share cap.**
Three independent ramps settled at **72 / 75 / 76–77 concurrent 8-core jobs (≈590–636 cores)**. The
earlier "96-core concurrency ceiling" came from a probe that **submitted 12 jobs and got 12** — a
fleet-size artifact recorded as a ceiling. Re-verified live: `maxujobs 1000` (max RUNNING/user),
`max_u_jobs 1000` (pending), `job_load_adjustments NONE`, and the single RQS `slowemdown` is
**enabled FALSE** and scoped to another user. **There is no per-user slot cap.**

**M2 — `-pe smp 36` SILENTLY REQUESTS A WHOLE EXCLUSIVE NODE.** UCL's JSV auto-adds an `EXCL`
complex when the core request equals a full node. Binary-searched live:

| request | resulting `hard resource_list` |
|---|---|
| `smp 1/4/8/16/24/28/32/34/35` | `snx=1,memory=2G,batch=true,h_rt=…` — clean, shares nodes |
| **`smp 36`** | `snx=1,`**`exb=true`**`,`**`exd=true`**`,…` — needs an ENTIRELY EMPTY b **or** d node |
| **`smp 64 -ac allow=T`** | `snx=1,`**`ext=true`**`,…` — same, on t |

This is why job `cpucurve_d` (`-pe smp 36`) sat queued for **2+ days**. **§0's "36-core CPU node,
1 training/core" job shape would STARVE.** Use **`-pe smp ≤35`**, and prefer **8** (below).

**M3 — THROUGHPUT IS FLAT IN FOOTPRINT, so choose footprint purely for PLACEABILITY.**
Final dataset: **148 jobs completed OK** (3 failures, all M6), measured under our own ~600-core load.

| pool | workers | n | mean steps/s/core | median |
|---|---|---|---|---|
| d | 8 | 120 | 14.23 | 14.38 |
| d | 16 | 2 | 14.38 | 14.38 |
| b | 8 | 21 | 14.06 | 13.50 |
| b | 1 / 4 / 16 / 24 / 28 | 1 each | 13.00 / 14.25 / 14.12 / 13.08 / 13.11 | |
| **ALL** | | **148** | **14.19** (median 14.25, p10 13.00, p90 15.38) | |

**FLAT from 1 to 28 workers.** Degradation comes from nodes being full of *everyone's* jobs, not
from our packing — so footprint is throughput-neutral and should be chosen **purely for
placeability (8 cores)**. **This supersedes the §0 table's 17.5 / 20.3 / 26–27 steps/s figures**,
measured on quiet nodes by small fleets — the wrong regime for a campaign that itself fills nodes.
**Warmup correction:** `learning_starts: 1000` (`config/algos.yaml`) makes 1,000 of a 12,000-step
bench gradient-free, so the sustained rate is **13.00 steps/s/core = 8.54 core-hours per
400,000-step training.**

**M3b — THE GPU, RECONCILED (and why the answer is a HYBRID, not a choice).** The launcher's own
measured pack curve (`autosize_h_rt::_agg_clean`) is aggregate steps/s **per GPU**:
pack1 **102** · pack2 133 · pack3 220 · pack4 240 · pack5 **253** · pack8 257 — and pack-1 matches
the G1 V100 anchor (102.2 steps/s, real SAC at obs 1893, job 764154) exactly. Therefore:

* **LATENCY: one GPU is 4–8× a CPU core-set per training.** pack-1 → 400k in **1.09 h** vs
  **8.54 h** on a CPU core (7.8×); even at pack-5 it is 2.20 h (3.9×).
* **THROUGHPUT: the GPU fleet cannot be had.** One V100 at pack-5 = 253 steps/s ≈ **19 CPU cores**.
  To match the 636 CPU cores we measured (≈8,270 steps/s) we would need **~33 GPUs at pack-5 — 45%
  of every GPU on Myriad.** We obtained **zero** in three days of queueing.
* **⇒ Use the GPU exactly where volume is tiny and latency is everything: THE SEQUENTIAL CHAINS.**
  `bayes_opt` is 25 strictly-sequential GP-EI iterations = **8.9 days on CPU** (the campaign's
  longest pole) but **~27 h on ONE V100 at pack-1**. The 55 LLM reflection chains (6 sequential
  generations each) go 2.1 days → ~13 h. **1–2 GPUs remove the critical path** — and 1–2 is a
  plausible ask (the U/V probes placed within ~30 min on 2026-07-24), where 33 is not.
* **Science check (why the split is legitimate).** Device homogeneity is required **per CONTRAST**.
  Every *scored* comparison (H4b bayes_opt-vs-LLM, H2, H1) happens on the **test leg**, which is
  all-CPU and therefore homogeneous by construction. The search leg only selects a reward
  *program*, which is then **re-trained from scratch at n seeds on CPU**; the search substrate
  changes *which program wins*, not any measured number. The fed tail and the authored code both
  come from the same search leg, so SQ1–SQ3 stay internally consistent. **This is a declarable
  design choice needing Ramin's nod, NOT a necessity** — an all-CPU campaign still completes the
  full ladder in 23.4 days, inside the window. Disclose the split; never hide it.

**M3c — ★★★★ THE THREAD SWEEP: 8 THREADS = 2.72× ON ONE TRAINING, AND IT REMOVES THE GPU DEPENDENCY.**
Every campaign training is pinned to ONE thread — right for the test flood, but a SEQUENTIAL CHAIN's
cost is pure LATENCY, where aggregate throughput is worthless. Nobody had measured the thread curve
(`bench_compute` hardcodes `threads=1`). Two independent jobs (17784 `smp 16`, 17836 `smp 8`,
b-pool, campaign profile) agree closely:

| threads | 1 | 2 | 4 | **8** | 16 |
|---|---|---|---|---|---|
| 16-core node (steps/s) | 20.9 | 32.9 | 46.4 | **55.1** | 44.0 |
| 8-core node (steps/s) | 21.5 | 33.7 | 48.1 | **60.0** | — |
| speedup | 1.00 | 1.57 | 2.23 | **2.72** | **2.11 ← REGRESSES** |

**8 threads is the optimum; 16 is measurably SLOWER** (small-matmul oversubscription — 256×256 nets
at batch 256, so each parallel region is tiny beside its launch overhead). Never go past 8.

**CONSEQUENCE.** At the contended campaign rate (13.0 steps/s), 8 threads ⇒ ~35 steps/s ⇒ the
`bayes_opt` chain falls from **8.9 d to ~3.3 d**, BELOW the throughput term at any realistic core
count. **The campaign becomes throughput-bound on PURE CPU, so the GPU is no longer needed** — adding
one leaves the makespan unchanged. CPU scaling now pays out to **~4,460 cores** (was ~1,640).

**THE RULE (measured both ways, same hardware): THREADS WHERE LATENCY BINDS, CORES WHERE THROUGHPUT
BINDS.** 8 cores as 8× 1-thread trainings = ~104 steps/s aggregate vs ~35 for one 8-thread training
— 1 thread is ~3× better for the FLOOD, 8 threads ~2.7× better for a CHAIN.

✅ **RATIFIED 2026-07-26 (Tamer) → amendment R107**, mirrored in `config/preregistration.yaml:
execution` (`chain_thread_count: 8`, `test_leg_thread_count: 1`, `chain_thread_count_max: 8`) and
BOUND to `lanes.CPU_CHAIN_THREADS` by a test so the code cannot drift from the registered value.
**NOT frozen** — Tamer's standing instruction. The rationale below stands as the evidence.

⚠ **WHY IT NEEDED RATIFICATION (not an ops detail).** Multi-threaded BLAS changes float reduction ORDER,
so an 8-thread training is not bit-identical to a 1-thread one. `docs/MAX_THROUGHPUT_RUN_PLAN.md`
already prescribes the exact procedure — **bench, then ratify pre-freeze** — and this is the material
win it required. Sound because (a) it applies to the SEARCH/chain leg ONLY (every scored comparison
lives on the uniformly 1-thread test leg, so no paired contrast is touched — threads change *which
candidate wins*, not any measured number), and (b) `scripts/capture_env.py` now records
`OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS` + `torch.get_num_threads()`, closing a PRE-EXISTING hole that
left the S6 homogeneity audit blind to a heterogeneous thread regime. Model + locks:
`src/cluster/lanes.py` (`CPU_THREAD_SPEEDUP`, `CPU_CHAIN_THREADS=8`), 15 tests.

**M4 — OUR CAPACITY IS BACKFILL FLOW, NOT AN ALLOCATION.** Holding the queue collapsed concurrency
**621 → 92 in ~20 min**; releasing it re-ramped to ~628. Sustained capacity REQUIRES a
continuously-deep queue of SMALL jobs. Dispatch arrives in **bursts at the 10-min
`schedule_interval`** (the `flush_submit_sec 1` micro-cycles did NOT give a continuous cold ramp).

**M4b — ★★★★ THE 636 FIGURE IS A LOWER BOUND, AND THE CAMPAIGN SHOULD BEAT IT SUBSTANTIALLY.**
The ~75-concurrent-job plateau (unchanged from 109 to 448 pending) is NOT a job-count ceiling — it
is a **flow equilibrium**: `concurrent = dispatch_rate × job_duration`. Our probe jobs ran only
~20 min, so they CHURNED — ~72 jobs completing and being replaced every ~22 min ⇒ a measured
**dispatch rate ≈ 3.3 jobs/min** (the 03:48 burst alone placed 67 in one cycle = 6.7/min).
**Campaign tasks are ~8.54 h — about 25× longer — so they ACCUMULATE instead of churning.**
At 3.3 jobs/min × 8 cores, the free d-pool (~3,700–4,000 cores) saturates in **~2.3 hours**, and
the binding constraint becomes FREE CAPACITY, not dispatch. Two independently-verified facts make
this sound rather than hopeful: (a) **an 11-hour `h_rt` request placed exactly as fast as a 50-min
one** — 15/15 vs 15/15 in the 2×2 factorial, so long jobs are NOT penalised at dispatch; and
(b) Myriad's functional tickets are **usage-history-free** (`weight_tickets_share` 1e4 vs
`weight_tickets_functional` 5e8), so our priority does **not** decay as we accumulate.
⇒ **A realistic campaign steady state is ~2,000–3,000 cores, not 636** — putting n=568 at **~5–7
days** rather than 23.4. ⚠ This is a MODEL calibrated on a measured dispatch rate, not a direct
multi-hour measurement; the GO-day canary must watch the accumulation curve over the first ~3 h and
let the advisor re-forecast from it.

**M4c — FOOTPRINT GRADIENT (measured 2×2 factorial + a 60-job 16-core fleet): USE 8 CORES.**
`smp 8` → **30/30 placed instantly** · `smp 16` → **2/60 in 15 min** · `smp 32` → **0/30 over two
full cycles**, despite 69 d-nodes having ≥32 free. Bigger footprints lose far more dispatch rate
than they gain cores per job. **Scale comes from job COUNT × DURATION, never from footprint.**
(And do NOT chase the ~850 idle CPU cores on the GPU nodes: taking them would block GPU jobs, which
request `-pe smp 4` alongside `gpu=1` — that is the one case where we would genuinely impair others.)

**M5 — ⚠ TICKET CONCENTRATION IS REFUTED for our account (contradicts §3 lever 1 + runbook §10 lever 3).**
Controlled test: `qhold` 228 of 309 pending jobs (reversible), leaving 80 eligible incl. 60×32-core.
Across a full scheduler cycle our top eligible priority moved **2.0165 → 2.0413** — that is
waiting-time accrual, which happens anyway — **not** the predicted ~50× ticket gain; **zero**
32-core jobs placed; and our running count decayed **44 → 9** (we starved ourselves). Our jobs sit
at the cluster priority **floor** (2.01 vs cluster median 2.00, p90 2.083, max 3.48) regardless of
how many we have pending. **Do NOT chunk big to buy priority — it does not work here.**

**M6 — node-level defect: `/usr/bin/apptainer` MISSING on some d nodes** (observed on
`node-d00a-230`) → jobs die `rc=127` (the venv python lives INSIDE the `.sif`, so no container = no
run). **Rate: 3 of 151 dispatched tasks = 2.0%.** Now guarded: `render_jobscript` emits a
`command -v apptainer` probe that exits with a NAMED error the ledger can count, instead of a bare
127 after the slot was already granted (`tests/test_cluster_adapter.py`).

**M7 — THE CONSEQUENCE FOR THE CAMPAIGN.** Work model (verified from `config/preregistration.yaml`):
**total trainings = 1,800 search + 71n test** — ⚠ **UPDATED late 2026-07-26**: the registered roster
grew **7 → 9 arms** (`+cma_es, +tpe`, the H4 optimiser portfolio, **N4 confirmatory**, ratified
R108), so it is now 9 core arms + 10 legs × 5 arms + 11 H1 canon + 1 H3 = **71 test units/rung**;
search = 9×30 + 30 H3 + 10×5×30 = **1,800**. The DFO arms are CORE-only, so the leg total is
unchanged at 50. *(The earlier 1,740 + 69n figures — and the day-counts derived from them — were
~3% optimistic and are superseded here. The old model's validation against the recorded
"48% / 22%" search split remains true of its own era.)*

| rung | 30 | 100 | 189 | 279 | 340 | 403 | **568** |
|---|---|---|---|---|---|---|---|
| trainings | 3,930 | 8,900 | 15,219 | 21,609 | 25,940 | 30,413 | **42,128** |

At the measured 8.54 core-h/training (≈2.81 trainings/day/core):

| sustained cores | rung reachable in the 31 days GO→Aug-27 | n=568 (99%) completes in |
|---|---|---|
| 96 *(the old assumption)* | n ≈ 93 | never |
| 320 *(old peak)* | n ≈ 367 | never |
| **628 (measured, SHORT probe jobs)** | n ≈ 745 → the LADDER TOPS OUT | **23.9 days (~Aug 19–20)** |
| **2,000 (projected, M4b)** | ladder tops out | **7.5 days** |
| **3,000 (projected, M4b)** | ladder tops out | **5.0 days** |

*(9-arm figures. The 1-thread `bayes_opt` chain is 8.9 d, so every row here is throughput-bound;
with the R107 8-thread chains it falls to 3.3 d and CPU scaling pays out to ~4,584 cores.)*

Above ~628 the extra rate buys no additional SCIENCE (the ladder ends at 568) — it buys **schedule
robustness** (23.9 d leaves only ~7 d of slack in the 31-day window; 5–7.5 d leaves ~24 d) and makes
the Stage-2 report-only armor fully affordable.

**=> the achieved seed rung stops being the binding constraint; the registered design can be
COMPLETED at n=568 rather than truncated at n≈142.** Hard floors cores cannot move:
**`bayes_opt` = 25 strictly-sequential GP-EI iterations** (`src/search/bayes_opt.py`) ≈ **8.9 days**;
LLM reflection chains = 6 sequential generations ≈ 2.1 days.

## 0-LIMITS. ★★★ MYRIAD OPERATING LIMITS — THE STOP RULES (Tamer, 2026-07-26: *"I would much rather save my access to Myriad than lose it in trying to find out the maximum possible"*)

**Access preservation OUTRANKS throughput and outranks curiosity. These are hard stop rules.**

1. **NEVER leave a resident process on a login node.** Policy is "<15 min, non-resource-intensive";
   `rogueusers` is literally a queue load-threshold complex. Poll from the laptop over ssh instead.
   *(2026-07-26: a 45-min `qstat` monitor loop was run on login12 and then killed — do not repeat.)*
2. **NEVER loop `qsub` for bulk work** (R3): one array = one job (`-t 1-N -tc K`), ≤10 submits/s.
   *(2026-07-26 used ~470 looped submits to force a capacity measurement — a deliberate one-off,
   not a precedent.)*
3. **Footprint is ADAPTIVE, not a fixed number** (revised 2026-07-26 on Tamer's *"for the campaign
   I want to eat the absolute maximum Myriad can offer"*). The self-imposed ceiling is
   `ABSOLUTE_CORE_CEILING = 2560`, but it is reachable **only when the cluster is genuinely idle**,
   because `plan_footprint` claims just 60% / 35% / 15% of FREE cores by live pressure and — the
   binding courtesy rule — **never consumes the last `FREE_CORE_RESERVE = 1000` cores**, so our
   campaign can never be the reason another user waits for a plain CPU slot.
   **Why a higher ceiling is NOT a reversal of this section:** the campaign's total work is fixed,
   so the total core-hours are the SAME concentrated or spread (636 × 23.4 d ≈ 337k core-h vs
   2,560 × 5.8 d ≈ 356k). We are not taking more of Myriad — we are taking it in a shorter window,
   and UCL's criterion explicitly allows impact that is *"not of long duration"*. What the extra
   rate buys is **schedule robustness**: at 636 cores the 31-day window holds only ~7 days of
   slack, which one multi-day jam erases. **Never raise the ceiling without the reserve floor and
   the pressure scaling — they are what make it defensible.**
4. **Never `-pe smp 36`** (M2): it is an exclusive whole-node request and it starves.
5. **Keep pending jobs far below `max_u_jobs` 1000**, and **delete dead/unplaceable jobs promptly**
   rather than leaving hundreds parked in the queue.
6. **Never lower priority; never `qrsub`; no RC/CRAG escalation without Tamer's explicit word.**
7. **If rc-support ever makes contact, stop submitting immediately and escalate to Tamer** — do not
   negotiate. A throttled account costs the campaign; a paused probe costs nothing.
8. **R9 acknowledgment is mandatory** in the dissertation: *"The author acknowledges the use of the
   UCL Myriad High Performance Computing Facility (Myriad@UCL), and associated support services, in
   the completion of this work."*

**THE SYSTEM THAT MAKES "GO FAST" AND "KEEP ACCESS" THE SAME POLICY (`src/cluster/killswitch.py`,
built 2026-07-26; 26 tests).** Rules alone are not enough — they need a mechanism.

* **PROACTIVE — `plan_footprint(free_cores, pending_jobs)`.** The probe's key observation was that
  **~5,000 cores sat FREE while ~2,000 jobs pended** (the queue wants GPUs and memory, not plain
  cores). So the fast move and the courteous move COINCIDE: claim **50%** of free capacity when the
  cluster is quiet, **30%** normal, **15%** when busy — clamped by the absolute self-imposed
  `ABSOLUTE_CORE_CEILING = 640`. We take capacity precisely when nobody else wants it, and stand
  down the moment they do. A fixed footprint cannot do that.
* **REACTIVE — `classify_task_deaths(...)`.** The driver's existing behaviour is *exactly wrong*
  for an administrative kill: it treats task death as node/transport failure and REQUEUES, and
  blind resubmission straight after a `qdel` is what turns "your jobs were killed" into "your
  account was suspended". The detector separates the three fingerprints from the epilogue ledger
  the jobscript already writes: **one host** → node failure (requeue, correct) · **`secs` ≈ h_rt**
  → expected walltime kill (requeue, resize) · **many deaths, many DISTINCT hosts, short window,
  none walltime-proximate** → **ADMIN KILL → RETREAT**: stop submitting, do NOT requeue, halve the
  cap (monotone; never self-raises), write `MYRIAD_KILL_INCIDENT.json`, alert a human.
* **The gate is human-in-the-loop**, like the tier-1 review gate: a machine may stop the campaign,
  only a person may restart it. An unreadable incident file BLOCKS (fail-safe).
* **The detector is deliberately trigger-happy.** False positive = a few hours of a run with ~7
  days of slack. False negative = the account. The asymmetry is the design.
* ⚠ **Retreat is NOT deprioritisation.** It reduces our FOOTPRINT. `qalter -p` remains forbidden,
  always; the module is structurally pure (no `subprocess`/`os` import — test-locked) so it cannot
  touch the scheduler at all.

## 0. ★★★ 2026-07-25 UPDATE — THE CPU LANE IS THE FAST SUBSTRATE FOR THIS WORKLOAD (measured)

> Supersedes the GPU-centric framing below **for the actual campaign training**. Established by a live
> probe fleet (b/d/t CPU pools + a U-pool A100), 2026-07-25. The workload is a TINY MLP (n_assets=30,
> obs 1893-dim, batch 256) — far too small to saturate a datacentre GPU — so per-node THROUGHPUT
> inverts the naive "GPU is fastest".

**Measured aggregate throughput (steps/s), identical training config, `bench_compute.py`:**

| Substrate | Packing | Agg steps/s | Per-training |
|---|---|---|---|
| A100-80GB (U pool) | 8 packed (knee 6–8) | **346** | 43 (65 at 2-pack → contends as it packs) |
| ~~**36-core CPU node**~~ ⚠ **UNPLACEABLE JOB SHAPE — see §0-PRE M2** (`-pe smp 36` = exclusive whole node). Use `smp ≤35`, prefer 8. Rate also superseded by M3 (~14/core, not 16–18). | ~~36~~ | ~~580–620~~ | ~~16–18~~ |
| 24-core CPU node | 24 | **434 (MEASURED)** | ~18 |
| 8-core CPU job | 8 | 177–217 peak / ~112 under dense co-location | 14–27 |

**THE FINDING:** a standard **36-core CPU node beats an A100-80G on aggregate training throughput (~1.7×)**,
and there are **344 of them** vs a handful of perpetually-starved A100/V100 nodes. For THIS workload the fast
substrate is CPU, not GPU. (Per-training *latency* still favours the GPU — one A100 training ~65 steps/s vs
~18 on a CPU core — but the campaign is **throughput-bound, not latency-bound**: the R101 rung reached by the
Aug-27 exogenous stop is set by trainings-COMPLETED, and a CPU node completes more per node-hour.)

**Scheduling reality (live-observed 2026-07-25):** the CPU pools (b/d/t) schedule an 8-slot job in minutes;
the GPU pools + every big-slot job (gpupack 8-slot, packcurve 18/26, cpucurve 36, v100_probe) have sat `qw`
for HOURS-to-DAYS under our ~1/122 fair-share slice. **Smaller-footprint jobs win scheduling** — prefer MANY
modest CPU jobs over few big GPU jobs. (Consistent with §1's "fewer pending tickets per job" arithmetic + the
whole-node-reservation cost of big smp requests.)

**MPS:** feasible (daemon starts on the A100, Default compute mode — `mpsprobe`). Its throughput benefit (can
it push the A100 past the 8-pack knee?) is PENDING — probe `mps_thru` (**job 13138**, queued behind the GPU
starvation). Even a generous MPS gain (~+30% → ~450) stays **below** the 36-core CPU node's ~600, so MPS is
very unlikely to flip the conclusion; measuring to confirm.

**Science (why this is neutral):** a CPU-only campaign is **CRN-HOMOGENEOUS** (PyTorch-CPU is deterministic
under seeding) and cross-substrate parity is already certified (`src/cluster/`, same science primitives).
Device mixing is handled by the existing `--seed-pool-blocks device-stratified` machinery (CPU is just another
homogeneous block). The CPU lane changes the SUBSTRATE, not the science — no identification / CRN / determinism
cost. **Recommend Dr Okhrati/Ramin's courtesy nod** (the CPU lane is now the PRIMARY plan, not insurance), but
**no pre-registration amendment is required** (design / arms / seeds / fitness all unchanged).

**IMPLEMENTATION SPEC (next session — a real multi-file change to tested cluster code; do NOT rush at
transition-close):**
1. `src/cluster/allocation.py` is GPU-only (`usable_pools`=EF/L/U/V; VRAM packing). Extend to a first-class
   CPU lane: add b/d/t pools; "pack" on CPU = cores-per-node (≈36, 1 training/core, NO VRAM gate); weight CPU
   nodes by the measured ~600 steps/s; include them in `stripe()` + the ETA; keep the CRN device-homogeneity
   invariant (CPU blocks are contiguous, like GPU-pool blocks).
2. `src/cluster/telemetry.py`: surface CPU-pool free-slot counts + a CPU `POOL_SPEED` entry.
3. `run_campaign_cluster.py`: confirm/enable a CPU jobscript path (`-pe smp 36`, no `-l gpu`, `-l mem` sized to
   node, tmpfs right-sized) — the probes prove `apptainer` runs the trainer on CPU with no code change.
4. Keep GPU as an OPPORTUNISTIC lane (device-stratified blocks) for whatever A100/V100 we DO win.
5. Regression-test the advisor's new CPU branch before launch. Fold the final `mps_thru` + `cpucurve_d`
   (36-core) numbers in when they land.

## 1. THE PRIORITY FORMULA (decoded from the live config — this IS Myriad)

```
prior = 4.0 * norm(POSIX -p)  +  1.5 * norm(tickets)  +  1.0 * norm(waiting_time)   [urgency 0]
```

- **POSIX term (weight 4.0)**: users can only LOWER -p (forbidden for us, ever). Everyone sane
  sits at 0 → the term cancels among competitors. Ignore.
- **Tickets (weight 1.5), policy O>S>F with functional DOMINANT**:
  `weight_tickets_functional = 5e8` vs `weight_tickets_share = 1e4` → the share-tree (usage
  history) is **negligible: 50,000× smaller**. Myriad priority is effectively usage-history-FREE.
  - **Functional = equal share per USER** (122 users pending at probe time → our slice ≈ 1/122),
    and `share_functional_shares = TRUE` → **our slice is SPLIT ACROSS OUR PENDING JOBS**
    (SGE sched_conf: "shares … shared among all the jobs associated with the object").
    → **THE LEVER: fewer simultaneously-pending jobs = more tickets per job = higher prior.**
  - Myriad overrides the array-consideration defaults (`max_functional_jobs_to_schedule 5000`,
    **`max_pending_tasks_per_job 1`**) — see §3b: big arrays concentrate tickets but ramp at
    1 task/cycle from cold, so chunking is TWO-REGIME, not one-sided.
- **Waiting time (weight 1.0)**: eligible (`qw`) jobs accrue priority while they wait.
  **`hqw` entries show prior 0.000** (live-verified) — these are BOTH genuine dependency holds
  AND each array's throttled tail beyond its one considered task (§3b). Only the eligible front
  tasks age; pipelined-rungs earns concurrency, not waiting-time credit.
- `halftime 604800` (7d) applies to the (negligible) share component. Pilot usage does NOT
  handicap us; the campaign does NOT degrade its own standing as it runs.
- `max_reservation 20` cluster-wide; our jobs carry `reserve: y` (anti-starvation, keep it).

**Live calibration (2026-07-24 04–05 UTC+5):** our eligible jobs prior 2.39–3.19 vs cluster top
3.50 → near the FRONT of the pending band; ~2,990 qw / ~700 hqw cluster-wide; 122 users.

## 2. THE HARDWARE (free-tier GPU pools)

| Pool | Nodes | GPUs | VRAM | Notes |
|---|---|---|---|---|
| **EF** (E-type) | ~19 | 2× V100 each (~38) | 16/32G (verify via the jobscript's archived `nvidia-smi` at canary) | Bigger pool, less contended — our default |
| **L** | 6 | 4× A100-40G each (24) | 40G | ~1.7–2.2× faster/training; more contended |
| U / V | 1 + 2 | 4× A100-80G each (12) | 80G | **U + V BOTH CONFIRMED USABLE (2026-07-24): probe_u ran on node-u00a-001 (qacct smp-U, exit 0) AND probe_v ran on node-v00a-002 (stdout probe_v.o10294 — qacct shows job-ID reuse, so the stdout hostname is the evidence) — BOTH while the EF control (10295) was STILL queued through a ~2.7k-qw jam. The A100-80G pools were LESS contended for us than the default EF pool → the full +12 A100-80G unlock. GPU/VRAM class confirmed by the GO-day canary nvidia-smi before deep striping. Runbook §10 best-hardware protocol has the stripe branch.** |

CPU nodes (D/I/B/T) irrelevant to training. tmpfs per node is large (hundreds of GB) but our
REQUEST size gates node eligibility (see lever 3). GPU job wallclock cap: 48h (2–36 cores).

> **⚠ PER-TRAINING SPEED vs THROUGHPUT — reconcile (2026-07-24, the A100 timing probe):** the
> "1.7–2.2× faster/training" for L and the A100 pools is the **GPU-compute ratio** — it holds only
> for a GPU-BOUND workload. OURS IS NOT: the training is bottlenecked by the single-thread Python
> env loop (pack curve 1→102 / 5→253 agg steps/s; the A100 timing probe measured ~24 steps/s @2
> cores, no GPU benefit visible). So the A100's per-training speedup is MODEST (≈1.0–1.4× at best,
> from faster node CPUs — not 2×). **The A100 pools' RELIABLE value is (a) LESS CONTENTION → more
> sustained GPU slots (proven: our probes ran on U/V while EF jammed for hours) + (b) DEEPER PACKING
> (80G hosts ~10 envs vs V100's ~5) → more concurrent trainings per node.** For time-to-result under
> R101 (all 11 parallel) THROUGHPUT is what sets the achieved seed rung, and the pools help it a lot;
> per-training clock barely moves. The GO-day canary measures the true PACKED multi-core per-node
> trainings/GPU-hour — plan the rung from THAT, not from the GPU-compute ratio or the 2-core probe.

## 3. THE LEVERS (all legitimate; priority never touched)

1. **TICKET CONCENTRATION — ⚠ REFUTED 2026-07-26; see §0-PRE M5. DO NOT USE AS A LEVER.**
   The controlled test (hold 228 of 309 pending jobs, one full scheduler cycle) moved our top
   eligible priority only 2.0165 → 2.0413 — waiting-time accrual, not tickets — and placed ZERO
   32-core jobs while 8-core jobs place 67-at-once. Our jobs sit at the cluster priority FLOOR
   whatever we do. The claim below is retained only as the superseded reasoning.
   *(superseded)* ~~Fewer pending jobs = more
   tickets each (~50× between the 1,200-singleton and dozens-of-arrays extremes), but cold-start
   ramp runs at 1 task/job/cycle — so chunk BIG only under contention; under quiet skies the
   many-array flood ramps faster and tickets barely bind. GO-day congestion read decides
   (`--chunk-tasks`); always < 1000 pending jobs (max_u_jobs).~~
   **What ACTUALLY governs (M1/M4):** a continuously-deep queue of SMALL (≤8-core) jobs; capacity
   is backfill FLOW. Keep `--chunk-tasks` small; never chunk big to buy priority.
2. **Pool selection at GO** (`--pool` → `-ac allow=`): read live free-GPU headroom per pool
   (`qhost -F gpu | grep -B1 'gpu=[1-9]'`) and pin for (availability × speed), CRN-homogeneous
   per comparison unit. Default EF; L for the latency-critical core if it has headroom.
3. **tmpfs right-sizing**: we request 15G; the gold panel is 35 MB. Nodes with a free GPU but
   <15G free tmpfs EXCLUDE us. Measure the true high-water at canary → cut to peak+margin.
4. **Per-VRAM pack calibration**: pack-5 was sized conservatively; A100-40/80G can host more
   concurrent envs per GPU. Measure VRAM headroom at canary (`nvidia-smi` is already archived) →
   raise pack per pool if headroom is 2×. More effective GPUs per granted slot.
5. **Submit early / morning launch / summer window**: eligible waiting-time accrues (weight 1.0);
   late-July–August is the UK academic low season; maintenance = 2nd Tuesday (Aug 11).
6. Already optimal: pack bursts (fewer queue entries), auto-sized short h_rt (backfill-friendly),
   `reserve: y`, 12 concurrent lines, striped pools.

## 3b. THE DISPATCH MECHANICS (probed 2026-07-24 — corrects the naive ticket doctrine)

- `schedule_interval 0:10:0` + `flush_submit_sec/flush_finish_sec 1`: full cycles every 10 min;
  MICRO-CYCLES fire within 1s of any submit/finish -> dispatch is event-driven at churn,
  10-min-granular from COLD (launch, post-maintenance).
- **`max_pending_tasks_per_job 1`** (vanilla default 50): each array job exposes exactly ONE
  pending task per cycle. (This is why qstat shows each array as one qw entry at real priority +
  one hqw bundle at 0.000 — the tail tasks are throttled, not merely dependency-held.)
- `max_functional_jobs_to_schedule 5000`; RQS: one rule, DISABLED, other-user-scoped ->
  **no hidden per-user GPU caps** (the fair-share grant IS the ceiling).
- **THE CHUNKING DOCTRINE (two regimes — replaces one-sided ticket concentration):**
  - CONTENDED (grants scarce): per-job PRIORITY dominates -> chunk BIG (few heavy arrays).
  - QUIET (slots plentiful): RAMP dominates (1 task/job/cycle from cold) -> MORE arrays ramp
    faster in parallel; a monolithic 568-task array would need days just to spin up.
  - STEADY STATE (hundreds running, finishes every few seconds): flush micro-cycles make
    dispatch continuous -> chunking barely matters; the constraint bites at cold-start only.
  - GO-day rule: read live contention (`qstat -u '*' | grep -c ' qw '`); heavy -> raise
    chunk-tasks toward job-count ~dozens; quiet -> keep the mode-D flood (its many arrays are a
    RAMP FEATURE under quiet skies). Never exceed max_u_jobs=1000 pending jobs either way.

## 4. DEAD ENDS (verified — stop revisiting)

- **Self-elevation**: impossible (fair-share allows only self-LOWERING; forbidden for us anyway).
- **Usage-history worry**: a myth on Myriad (share weight 1e4 ≪ functional 5e8).
- **Idle departmental nodes**: owned/paid pools, invisible to free allocation.
- **`qsub -w v` pre-validation**: false-negatives on gpu/allow complexes; don't trust it.
- **RC fast-track**: admin-only; Tamer's standing "no RC request"; surfaced, never actioned.
- **Advance reservations (qrsub)**: `max_advance_reservations 0` + explicit ACL denial
  ("must be manager or in userset arusers") — definitively unavailable (probed 2026-07-24).
- **Hidden per-user quotas**: none (the single RQS is disabled + other-user-scoped).

## 5. THE COMMAND TOOLKIT

```
qstat -u '*' | awk '{print $5}' | sort | uniq -c    # cluster pressure at a glance
qstat -j <jid>                                      # why pending + exact resource request
qhost -F gpu | grep -B1 'gpu=[1-9]'                 # nodes with free GPUs right now
qconf -ssconf                                       # the scheduler policy (this dossier's source)
qquota                                              # resource-quota limits on us
qdel <jid>                                          # remove (never on reserved queued jobs
                                                    #   — kill+resubmit forfeits reservation+age)
```

*Sources: live `qconf -ssconf`/`qstat`/`qhost` probes (2026-07-24); UCL RC docs (Myriad cluster
page; GPU nodes; Experienced Users); SGE sched_conf(5)/sge_priority(5) manuals. UCL is migrating
SGE→Slurm at some future date — this dossier is SGE-era.*
