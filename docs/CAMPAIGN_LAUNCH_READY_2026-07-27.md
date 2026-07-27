# CAMPAIGN LAUNCH — READY. Read this first, then launch.

**Written 2026-07-27 ~21:00 BST at the end of the launch-gate session. Everything below was
MEASURED or OBSERVED first-hand on that date; nothing here is inferred unless it says so.**

> # ⛔ §1 BELOW WAS WRONG. CORRECTED 2026-07-27 ~23:30.
>
> **The command this document called "THE LAUNCH COMMAND" would not have run the confirmatory
> campaign, and four separate defects behind it would each have destroyed the run.** They were found
> by dry-running and executing the very things this document asserted, hours after it was written.
> Read **§0 THE CORRECTED LAUNCH** below and ignore the original §1 command; everything else in this
> document (§2–§9) remains accurate and is still the right briefing.
>
> **What was wrong, each verified by execution rather than reading:**
>
> 1. **The command was a SUBSTRATE FRAGMENT, not a launch command.** It carried every *machine* flag
>    and no *science* flag, so argparse defaults took over: `--arms` defaulted to **2** of the frozen
>    **9** arms, `--pass-mode` to `A` and `--provider` to `stub` (**the keyless stub designer would
>    have authored every reward — no LLM call at all**), and without `--tiered` there is no C0
>    canary, no C-ladder, no review gate, and `resolve_cluster_baselines` returns `None`, so the
>    entire 11-name H1 canon is skipped and node N6 is unsatisfiable. Proven by dry-run:
>    `[dry-run] wiring valid — 2 arms, 568 seeds`.
> 2. **Every training would have been walltime-killed inside 6 hours.** `autosize_h_rt` took no
>    `device` and priced everything off a GPU aggregate-throughput curve:
>    `autosize_h_rt(4, 400_000) == "6:0:0"`, against **8.55 h** needed at the registered 13.0
>    steps/s/core and **6.11 h** even at the fastest rate ever observed. §8 of this document asserts
>    "`_auto_h_rt` is lane-aware now" — that fix had landed in `p6_authored_ladder.py` only.
> 3. **The gold panel is not where the launcher looks.** `--gold-dir` defaults to
>    `~/Scratch/llmrp/inputs`, which exists on Myriad and is **EMPTY**; the licensed panel lives on
>    ACFS at `/acfs/users/ucestes/gold` (verified `returns_panel_univ5.parquet` sha256
>    `7cf5d988…` = byte-identical to the frozen manifest). The jobscript deliberately `mkdir -p`s
>    the bind source, so the container starts happily and every task then dies in the loader.
> 4. **Those mass walltime kills would then have HALTED the campaign.**
>    `campaign._enforce_kill_switch` called `classify_task_deaths` **without `h_rt_secs`**, and that
>    function applies its walltime discriminator only `if h_rt_secs:` — so every walltime kill
>    counted as *administrative-kill* evidence. ~142 concurrently-dispatched tasks dying at their
>    limit on distinct hosts within minutes is exactly the ≥8-deaths/≥4-hosts/≤300 s shape that
>    writes `MYRIAD_KILL_INCIDENT.json` and blocks **every** subsequent submission until a human
>    clears it by hand. Demonstrated: 12 walltime kills classified `admin_kill`/**retreat** before
>    the fix, `walltime`/`requeue` after, with a genuine `qdel` still retreating.
>
> Also corrected: the ratified `mode_d_supervisor.ps1` was GPU-only and its ten leg lines each
> passed `--priority -200…-290`, which finding #96 had already made a hard `SystemExit` — all ten
> would have died at argv parsing and been relaunched forever at 600 s backoff. R101's lockstep was
> never implemented (legs were pinned at `--seeds 0-29`). The arm roster was hand-typed as **7** in
> four separate launch paths after R108 took it to **9**, dropping `cma_es` and `tpe`.
>
> **The `--search-threads 1` recommendation is also withdrawn** — see §0.3. It was chosen because
> `threads × pack` made an unplaceable 32-core request, but that arithmetic assumed a *uniform*
> pack. Running the search lane at `--search-pack 1` makes the same 8 threads an **8-core** job,
> which places in ~19 min, honours the registered `chain_thread_count: 8` with no amendment, and
> cuts the two serial chains that gate everything by the measured 2.72×.

---

## 0. THE CORRECTED LAUNCH (2026-07-27, supersedes §1)

### 0.1 Do not launch by hand. Use the launcher.

The campaign is **twelve** driver lines (the Opus core + the H3 floor unit + 10 replication legs),
each self-healing under its own supervisor. A single bare `python …` invocation runs one of them.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\mode_d_launch.ps1
```

`scripts\mode_d_supervisor.ps1` is now the single source of the exact argument lists, and its
`$cpuLane` array is shared by every line so no line can drift from another. Stop everything by
creating `outputs\campaign_cluster\STOP_CAMPAIGN`.

### 0.2 What each line actually runs (extracted from the launcher, not retyped)

```
core   run_campaign_cluster.py --tiered --pass-mode B --llm-from campaign --pipeline-rungs
                               --batch-tag c1   + $cpuLane
h3     run_campaign_cluster.py --h3-singleshot --seeds 0-567 --pass-mode B --llm-from campaign
                               --batch-tag h3ss + $cpuLane
leg N  run_campaign_cluster.py --leg <label> --tiered --pass-mode B
                               --batch-tag legN + $cpuLane

$cpuLane = --device cpu --pool d --pack 4 --cores-per-training 1
           --search-pack 1 --search-threads 8 --chunk-tasks 1
           --exclude-hosts node-d00a-230 --gold-dir /acfs/users/ucestes/gold
           --poll-secs 180 --search-poll-secs 45
           --output-dir outputs\campaign_cluster --resume
```

**No `--arms`, no `--baselines`, no `--priority`, no `--seed-pool-blocks` — deliberately.** The
roster and the H1 canon are RESOLVED from the frozen config (`resolve_cluster_arms` /
`resolve_cluster_baselines`) and a partial list is refused before ssh; priority defaults to 0, which
is full fair-share standing and what R101 requires; the GPU seed stripe is refused on the CPU lane.

Verified by dry-run, from PowerShell, on the exact extracted arguments:

| line | resolves to | tiers |
| --- | --- | --- |
| core | **9 arms**, 568 seeds, 5 candidates/gen, `h_rt 15:0:0` | 7 tiers, sizes `[30,70,89,90,61,63,165]` |
| h3 | 1 arm (forced `distributional`), 568 seeds, 30 candidates/gen | — |
| leg | **5 LLM arms**, 568 seeds, no H1 canon | 7 tiers |

### 0.3 The flag table, corrected

| flag | why | evidence |
| --- | --- | --- |
| `--device cpu` | the confirmatory lane (R107/R108) | §4.6 — GPU is unreachable at our priority floor |
| `--pool d` | **VERIFIED 2026-07-27 by A/B probe**: with `-ac allow=d` both tasks landed on `node-d00a-155/156`; the control without it landed on `node-b00a-011`. The token genuinely confines placement — and without it nothing keeps us off the AMD `t` pool, whose different oneDNN kernels break CRN bit-exactness | §4.5 + the probe |
| `--pack 4` | 4 INDEPENDENT trainings per job, one core each, ~100 % efficient. 4-core jobs place in ~6 min; 1,000 × 4 = the 4,000-core ceiling | §4.2 |
| `--cores-per-training 1` | the test flood is throughput work: 8 × 1-thread ≈ 104 steps/s aggregate vs ~35 for one 8-thread training | §4.1 |
| **`--search-pack 1` + `--search-threads 8`** | **REPLACES `--search-threads 1`.** Job cores are `max(cores_per_training, threads) × pack`, so 8 threads at the test flood's pack is 32 cores (past the placement cliff) but at search-pack 1 it is **8 cores**, which places in ~19 min. Honours the registered `chain_thread_count: 8` (R107, ratified — and its "refutation" was retracted), and 2.72× on the 6-step reflection chain and the 25-step `bayes_opt` chain, the two things that gate everything | §3.1, §4.3 |
| `--chunk-tasks 1` | arrays are SERIALISED and tails have twice been PURGED. **Reproduced again 2026-07-27**: a 6-task probe array came back `qw` on task 1 and `hqw` on 2–6 | §4.4 |
| `--exclude-hosts node-d00a-230` | no apptainer; fails in seconds, so it is always free and the scheduler keeps feeding it. Extend this list if the sentinel's `host_failure_concentration` fires | §4.6 |
| **`--gold-dir /acfs/users/ucestes/gold`** | **NEW AND REQUIRED.** The default points at an empty directory. The launcher now verifies the remote panel's sha256 against the frozen manifest before submitting anything | §0 item 3 |

### 0.4 New guards, so none of this can recur silently

`resolve_cluster_arms()` (frozen roster or refusal) · `assert_remote_gold()` (present **and**
sha256-matched, at t0 on the laptop) · `autosize_h_rt(..., device=)` sourced from a single
`lanes.CPU_PLANNING_STEPS_PER_SEC` shared with the ladder · `_enforce_kill_switch(..., h_rt_secs)` ·
`FREEZE_TAG` moved to `prereg-v2.0` (the v1.0 tag already existed, so the freeze would have produced
**no** provenance anchor and would have overwritten `docs/prereg-v1.0.sha256` with the v2 digest) ·
`capture_env` schema **/4** now records the CPU vendor/model, so a microarchitecture mix is
detectable by audit instead of invisible · `campaign_monitor.sh` watches all twelve lines, not two.
Locked by `tests/test_launch_gate_regressions.py`, `tests/test_fed_rendering_pin.py` and new cases
in `tests/test_run_campaign_cluster.py` / `tests/test_mode_d.py`.

**Before launching, `python scripts/freeze.py` (R94).** As of this writing: `frozen: false`,
`freeze_hash: null`, `freeze.py --check` **RC=0**.

### 0.5 THE GO SEQUENCE, in order, with what each step must show

| # | step | pass condition |
| --- | --- | --- |
| 1 | full suite, UNPIPED, verdict read from pytest's OWN exit code | `PYTEST_RC=0` — never trust a pipe's status; a `\| tail` once produced a false green here, and on 2026-07-27 a background wrapper reported "exit code 0" over a real `PYTEST_RC=1` |
| 2 | `freeze.py --check` · `pretrain_validate` · `ruff` · `check_citations` | RC=0 · FAIL=0 (one WARN, `executable_yield`, is a CAPABILITY FINDING — do NOT "fix" it) · clean · clean |
| 3 | `author_smoke.py` | live call on `claude-opus-5` — proves key, model and BALANCE at t0 rather than at hour 3 |
| 4 | sweep the remote archive roots | zero records under any of the 36 roots the twelve lines write to; MOVE anything found, never delete |
| 5 | **`python scripts/freeze.py`** (R94), then `--check` again | `frozen: true`, `freeze_hash` == the freshly recomputed canonical hash, tag `prereg-v2.0` created |
| 6 | commit the freeze, then DEPLOY that commit | file-based tar + scp + sha256 compared BOTH ends; never the `git archive \| ssh` pipe from PowerShell — it corrupts the stream |
| 7 | PROVE the deployed tree | `git ls-tree` vs remote `find`, both `LC_ALL=C sort`ed, diffed in BOTH directions; `GIT_COMMIT` marker written |
| 8 | `powershell -File scripts\mode_d_launch.ps1` | 12 supervised lines start; the core first, legs staggered ~1 h behind (the canary shield) |
| 9 | arm monitoring in the same step | see the table below — a campaign nobody is watching is a campaign whose failures are discovered at the stop date |

### 0.6 MONITORING — arm all four, at launch

| what | command | cadence | what it tells you |
| --- | --- | --- | --- |
| queue + records + heartbeats | `NTFY_URL=... bash scripts/campaign_monitor.sh &` | 300 s, emits only on CHANGE | state-class transitions across all twelve lines, any `Eqw`, driver heartbeat older than 15 min. **Quiet = healthy** |
| the invariant sentinel | `.venv/Scripts/python.exe scripts/sentinel.py --watch outputs/campaign_cluster &` | 120 s | the full check battery incl. `capacity_accumulation`, `chain_progress`, `host_failure_concentration`, `determinism_homogeneity` |
| the live allocation view | `python scripts/allocation_advisor.py --watch 900 --archive-root outputs/campaign_cluster` | 15 min | **must run at least once at launch**, or `capacity_accumulation` has no target to judge against |
| is the output SANE? | `python scripts/first_seed_sanity.py outputs/campaign_cluster` | at the first completed records, then daily | NaN returns, reward fallbacks, a policy parked in cash, an absurd reward scale. **Effect-blind by construction** — it inspects EXECUTION, never outcomes, so it is not a peek |

**The one alert that must stop the lane:** `determinism_homogeneity` CRITICAL — a scored leg on more
than one substrate confounds every paired contrast, and the post-hoc S6 gate would find it far too
late to re-run. Everything else is a "go and look".

**`rung_forecast` is a planning readout only.** The stop is EXOGENOUS (calendar, 2026-08-27). Never
stop or continue because of that number — doing so would be optional stopping and would invalidate
every p-value in the dissertation.

**Watch in the first hours** (§5b is honest that this is the biggest unknown): concurrency
accumulation — 1,000 jobs / 4,000 cores has never been observed. Log jobs and cores every ~5 min
for the first ~3 h and re-forecast from the OBSERVED plateau, not from the 636-core ceiling figure.

### 0.7 WHAT THE FIRST HOURS SHOULD LOOK LIKE — so a stall is distinguishable from the design

Knowing the expected shape matters: the campaign is *designed* to look quiet for its first several
hours, and mistaking that for a hang is how an operator "fixes" a healthy run.

| when | expected |
| --- | --- |
| T+0 to ~20 min | the core line's three preconditions pass (roots ensured · **gold sha256 == frozen manifest** · no foreign records), `arms RESOLVED (9)`, `h_rt 15:0:0`. First qsubs: the **C0 canary** (3 H1 units × 30 seeds), the rest of the 11-name H1 canon, and the four DFO arms' searches — all of which author NOTHING, so they start at L+0. Expect **~100+ jobs**. 4-core jobs place in ~6 min, 8-core search jobs in ~19 |
| T+1 h | the ten leg lines wake (the staggered canary shield) and begin authoring immediately — legs carry no canary because they carry no H1 canon. Total leg authoring spend is ~**$1.38** |
| T+~6–11 h | the canary completes (its trainings are full B\* = 400k). **Only now does Opus authoring begin** — that is the entire point of the shield: prove the production path end-to-end before the expensive author is billed |
| at the first records | run `first_seed_sanity.py`. Expect zero NaNs, zero reward fallbacks, a non-flat policy, `env_fingerprint.label` containing `\|dev=cpu`, `env.json → determinism_env.OMP_NUM_THREADS` = **1** on TEST-leg records and **8** on SEARCH-leg records (R107's registered scope), and a populated `cpu` block (schema `capture_env/4`) |

**The single best early failure signal** is a supervisor log that says `driver exited N - relaunching
in 600s` within the first minutes. A healthy line logs `attempt 1` once and then stays quiet:

```bash
grep -l "driver exited" outputs/campaign_cluster/supervisor_*.log   # any hit = investigate NOW
```

**If the killswitch ever retreats** (`MYRIAD_KILL_INCIDENT.json` appears and all submission blocks),
FIRST check for mail from `rc-support@ucl.ac.uk` — the guard exists because blind resubmission after
an administrative `qdel` is what turns "your jobs were killed" into "your account was suspended".
Only once it is genuinely a false positive, clear it (there is no CLI):

```bash
.venv/Scripts/python.exe -c "from src.cluster.killswitch import clear_incident; \
    print(clear_incident('outputs/campaign_cluster', who='tamer', note='<why it was a false positive>'))"
```

⚠ `who` is a REQUIRED keyword-only argument and is recorded in the file — the release is auditable
on purpose. (Verified against `killswitch.py:401` rather than written from memory; the obvious
one-argument form fails, which is not something to discover during an incident.)

---

## 1. THE ORIGINAL LAUNCH COMMAND — ⛔ SUPERSEDED, DO NOT RUN (kept as the record)

```bash
python scripts/run_campaign_cluster.py \
  --device cpu --pool d --pack 4 --cores-per-training 1 \
  --search-threads 1 --chunk-tasks 1 --exclude-hosts node-d00a-230
```

**Every flag is backed by a measurement taken 2026-07-27. Do not change one without reading §4.**

| flag | why | evidence |
| --- | --- | --- |
| `--device cpu` | the confirmatory lane (R107/R108 CPU lane) | — |
| `--pool d` | 294 nodes x 36 = 10,584 cores. `b` is only 16 high-memory nodes; `t` (AMD) breaks CRN bit-exactness and was measured only 3.9 % faster | §4.5 |
| `--pack 4` | 4 independent trainings per job, ONE CORE EACH. 4-core jobs place in ~6 min; gives 1,000 x 4 = 4,000 cores | §4.2 |
| `--cores-per-training 1` | the default is **2**, which makes every 1-thread training hold TWO cores — half of every core-hour wasted | §4.1 |
| `--search-threads 1` | ⛔ WITHDRAWN — see §0.3 | §4.3 |
| `--chunk-tasks 1` | one job per task. Arrays are SERIALISED (`hqw` on the tail) and tails have twice been PURGED | §4.4 |
| `--exclude-hosts node-d00a-230` | that node has no apptainer and ate 13 jobs in 90 min | §4.6 |

---

## 2. WHAT YOU GET, AND WHEN

Measured rate **~18.2 steps/s** per 1-thread training on the real `univ5` panel (100k ladder cells,
startup amortised) => a 400k training is **~6.1 h**. That is ~40 % FASTER than the registered
13.0 steps/s planning constant, so the design's own timeline is CONSERVATIVE.

| result | gated by | lands |
| --- | --- | --- |
| **H1/H2 — the mechanism headline** | the 6-step LLM reflection chain | **~1.5 days** |
| **Full 568 ladder, every arm except H4** | throughput at 4,000 cores | **~2.7 days** |
| H4 (optimiser comparison) | `bayes_opt`'s 25-step serial chain | ~6.4 days |

**Each rung is a COMPLETE study** (prereg: cumulative, order-only tiers; truncation falls back to
the largest COMPLETED rung), so writing can start from the first rung. Tamer has explicitly accepted
H4 arriving late.

**Ceiling analysis.** `cores = jobs x pack`, and `max_u_jobs = max_aj_instances = 1000`.
pack 4 -> 4,000 (job-capped); pack 8 -> 4,800 (cluster-capped: ~5,800 free minus the 1,000-core
courtesy reserve). Throughput stops binding at **7,021 cores**, above which the 6-step LLM chain
floors everything at 1.53 d. **pack 8 buys only ~0.45 d and places 3x slower (19 min vs 6), which
degrades as the cluster fills — pack 4 is the recommendation.**

---

## 3. ⚠ TWO CLAIMS I MADE AND RETRACTED. DO NOT REBUILD ON THEM.

Both retractions are in the committed history (`f443442`) and in
`docs/EVIDENCE_AND_FRAGILITY_LEDGER.md`.

### 3.1 R107 is UNTESTED, not refuted. DO NOT AMEND IT.

I reported that the CPU gate refuted R107's 2.72x thread speed-up and measured ~1.18x. **Withdrawn.**
The "8-thread" arm was submitted at 16:58 against cluster code `a4f903c`, whose `_worker_init()`
takes **no thread argument** and hardcodes 1 (`git show a4f903c:src/orchestration/parallel.py`); the
wiring was committed 16:43 but DEPLOYED only ~18:55. **That arm ran at one thread.**

My corroboration was also wrong: I said `qstat` proved 8.06x parallelism. SGE's `cpu` field on an
`smp` PE reports **SLOT-seconds, not CPU consumption** — 8 slots x 46 min = 6:08 against the observed
`cpu=06:10:56`. I read an ALLOCATION figure as a UTILISATION figure.

**"Untested" is not grounds for amending a registered value.** Tamer's blanket ratification
permission was explicitly declined on this point.

### 3.2 Packing is NOT threading (Tamer caught this)

I rejected packing using the threading efficiency penalty. They are different operations:

* **8 threads on ONE training** -> 34 % efficient (the nets are 256x256 at batch 256; 16 threads is
  measurably SLOWER than 8). Correctly rejected.
* **`pack N` + `cores_per_training 1`** -> N INDEPENDENT trainings, one core each -> **100 %
  efficient**, identical to N separate jobs. This is the ONLY route past the 1,000-job cap.

I also twice declared a job shape "does not place" after watching only ~5 and ~12 minutes. **8-core
jobs DO place — they take ~19 minutes.** Give placement 30 min before concluding.

---

## 4. WHAT WAS MEASURED (the basis for every flag)

### 4.1 `--cores-per-task` defaults to 2
A 1-thread training requested TWO cores. Found via a `policyjsv` rejection message. Halves effective
capacity. Also: **the 72 h walltime cap applies to 1-core jobs only**; at 2+ cores the limit is 48 h.

### 4.2 Placement vs job shape (controlled, simultaneous submission, fenced)
| shape | time to place |
| --- | --- |
| 1-core | ~2 min |
| 2-core | ~2 min |
| 4-core | ~6 min |
| 8-core | ~19 min |
| 16-core | **never placed in 28 min** |

Pure latency, no cliff until 16. Mechanism: our jobs sit at the cluster **priority floor**, so we
live on **backfill**, which slots small jobs into gaps while larger ones need a reservation.

### 4.3 Threads x pack = an unplaceable job
`cores = max(cores_per_training, threads) x pack`. With `--pack 8` and R107's 8 threads that is
**64 cores** — UCL's JSV then adds the exclusive complexes, so the job needs an ENTIRELY EMPTY node
and starves (this is what left job `cpucurve_d` queued 2+ days). The render-time guard refuses it.

### 4.4 Arrays are serialised
A 6-task array came back `qw` on task 1 and **`hqw` on tasks 2-6**. `submit_singles`' docstring
records that the policy has **twice PURGED pending tails outright**. Always `--chunk-tasks 1`.

### 4.5 Pools
`d` = 294 nodes x 36 = 10,584 cores (the workhorse). `b` = 16 high-memory nodes (1.5 T RAM) — wrong
tool and tiny. `t` (AMD EPYC) breaks CRN bit-exactness via different oneDNN kernels and was measured
only 3.9 % faster (14.75 vs 14.2) — correctly excluded. GPU-node CPUs are excluded on courtesy
grounds (harvesting them blocks GPU jobs).

### 4.6 GPU is NOT practically available to us
A GPU probe sat **queued 42 minutes with 24 GPUs advertised free**, while CPU jobs placed in 2. At
the priority floor we get backfill, and GPUs are not reachable that way. **H4 therefore stays on CPU
at ~6.4 d.** A GPU route would also need `bayes_chain` wired (built but NOT wired — nothing selects
`entry_module="src.cluster.bayes_chain"`), else the chain pays 25 separate queue waits.

### 4.7 The 636-core figure is a CEILING, not a sustained rate
It was measured 02:30–04:30 UTC with `bench_compute.py` (SYNTHETIC panel, 2,500 steps, no
archiving). The campaign runs 6.1 h jobs at all hours. **Never re-quote 636 as sustained.**

---

## 5. WHAT IS VERIFIED (evidence, not assertion)

* **Full suite: 2,779 passed / 3 skipped / 0 failed / RC=0** on `3e2e9b1` (re-run after the
  `--help` fixes; **cluster re-synced to the same commit and the tree diff PROVED clean**, §8).
  Reconciles exactly against the earlier 2,775: `+2` from `1b8aec5` (packed provenance) `+2` from
  the new `tests/test_cli_help_strings.py`. No unexplained delta.
* **`freeze.py --check` RC=0**, `freeze_hash: null` — nothing frozen.
* **Golden reproduction RC=0** after the training path was touched (heartbeat) — determinism intact.
* **Full campaign path on CPU: rehearsal RC=0** — search leg -> winner selection -> **TEST LEG** ->
  archive. 12 records (4 search + 8 test), valid science, `env label 'campaign:...|dev=cpu'`,
  sealed window `[5536,7800)` correct.
* **Packed execution (pack 4 AND pack 8) completed**, two concurrent trainings per job proven by
  162 interleaved heartbeat lines (2 x 81).
* **Packed provenance FIXED and verified on a real cluster record**: `OMP_NUM_THREADS: 1`,
  `torch num_threads: 1`.
* **Graceful degradation**: when jobs were killed mid-run the campaign marked those specs
  `exhausted`, continued, selected winners, and reported the shortfall via exit code.
* **The CPU lane produces valid science** — the first full trainings ever run there corroborate the
  GPU-era archive both quantitatively (p6dist brackets its 0.0601 original) and qualitatively (the
  scalar winner's budget-hunger, exactly as R77 recorded). 694 val-returns per cell, matching the
  registered `track_length`; zero NaNs; 60,000 reward calls with **0 fallbacks**.

## 5b. WHAT IS **NOT** VERIFIED

* **Sustained capacity at scale.** We reached ~230 cores on ~170 jobs. **1,000 jobs / 4,000 cores
  has never been observed.** This is the single biggest open unknown — watch it in the first hours.
* **The `max_u_jobs` cap under real load.** A cap hit surfaces as `CalledProcessError` ->
  `SubprocessError`, which IS in `driver._TRANSPORT_ERRORS`, so it is retried next cycle and the
  driver rides out up to 12 h of it. Verified by code reading, NOT by hitting the cap.
* **R107's 2.72x** — untested (§3.1).

---

## 6. LIVE ON THE CLUSTER AT HANDOVER (~21:00, 2026-07-27)

~155 jobs, all MY side-work — **none of it gates the launch**:

| root | what | note |
| --- | --- | --- |
| `~/Scratch/p6cpu` | the **p6 ladder** (5 budgets x 10 seeds x 2 winners) | restores **F11** + gives B\* substrate evidence at n=10. Runs ~30 h (the 1.6M rung). Pull with `p6_authored_ladder.py --pull --remote-root '~/Scratch/p6cpu' --output-dir outputs/p6cpu` |
| `~/Scratch/cpugate` | the CPU gate (done, 5 records) | ⚠ the 1-thread control OVERWROTE the 8-thread records here — do not treat these as two arms |
| `~/Scratch/rehearse3/4/5` | rehearsals (done) | synthetic, no spend |
| `~/Scratch/ctl1thr` | redundant 1-thread control | superseded by n=9; safe to cancel |

The ladder costs ~145 of 1,000 job slots and ~170 cores. **Leave it running** — it is work the
write-up needs, and it is ~4 % of a 4,000-core campaign.

---

## 7. OUTSTANDING TASKS (none block the launch)

1. **Recover 13 ladder cells** eaten by `node-d00a-230` before the fence existed. Once the wave
   drains: pull, then resubmit with `--skip-done --exclude-hosts node-d00a-230`. The ladder has NO
   driver loop, so a failed cell is LOST unless resubmitted (unlike the campaign, which resumes by
   archive replay).
2. **Rebuild F11** from the ladder records when they land (`budget_curve_exhibit`); the
   `budget_ascent_exhibit` fallback is in place meanwhile.
3. **`bayes_chain` is built but NOT WIRED** (R16 class). Only worth doing if the GPU route is ever
   revisited.

---

## 8. OPERATIONAL GOTCHAS LEARNED THE HARD WAY (2026-07-27)

* **Deploy to the cluster with a FILE, not the runbook's pipe.** `git archive HEAD | ssh myriad tar -x`
  is corrupted by PowerShell (binary stream). The cluster was found **437 commits stale** at the start
  of this session. ⚠ **I hit this AGAIN at 22:0x after writing this bullet** — running the runbook's
  pipe from PowerShell produced `tar: This does not look like a tar archive` and a dozen
  `Skipping to next header`. **Verified recovery, and the recipe to use instead** (Bash tool, never
  PowerShell):

  ```bash
  git archive --format=tar HEAD -o /tmp/deploy.tar
  sha256sum /tmp/deploy.tar                       # compare with the remote one below
  scp /tmp/deploy.tar myriad:~/deploy.tar
  ssh myriad "sha256sum ~/deploy.tar"             # MUST match, byte-for-byte
  ssh myriad "tar -xf ~/deploy.tar -C ~/llmrp && rm -f ~/deploy.tar"
  git rev-parse HEAD | ssh myriad "cat > ~/llmrp/GIT_COMMIT"
  ```

  **Then PROVE the tree is right rather than assuming** — a corrupt extract can leave residue:
  compare `git ls-tree -r --name-only HEAD` against a remote `find` (exclude `outputs/ data/ .venv/
  archive/ __pycache__ GIT_COMMIT`), `LC_ALL=C sort` **both** sides (the remote locale collates
  differently and `comm` silently misreports otherwise), and diff in **both** directions. Done at
  `3e2e9b1`: **627/627 present, zero missing, zero extra**, and `src/cluster/run_one.py` deployed
  sha256 == HEAD's. The failed pipe left no residue.
* **Do not compile-check the deployed tree with the login node's `python3` — it is 3.6.8** and dies on
  a walrus operator in `src/cluster/telemetry.py:390` that is perfectly valid. The jobs run 3.11
  inside the container, and `~/venvs/llmrp/bin/python` is NOT executable from the login node by design
  (the venv is built inside the image because RHEL7 glibc is too old for the cu124 wheels). A
  `SyntaxError` from that interpreter is an artifact, not a defect.
* **`_auto_h_rt` is lane-aware now.** The old 25 steps/s floor was a GPU-era constant and would have
  **SIGKILLed every CPU rung above 100k** (400k needed 8.5 h, was granted 7 h).
* **A training used to be a BLACK BOX** — `verbose: 0` and 0-byte logs until completion. A heartbeat
  now prints `[train] step N/M ... rate X steps/s` from the existing read-only curve recorder at its
  existing cadence, with `flush=True` (stdout is block-buffered into the log file).
* **A bad node is a JOB VACUUM** — it fails in seconds, so it is always free and the scheduler keeps
  feeding it. Fence with `--exclude-hosts`.
* **Don't conclude placement from a short window.** I was wrong twice doing exactly that.

---

## 9. FOR TAMER (the only human-gated items)

1. **`python scripts/freeze.py`** — R94. Never a lane's action.
2. **Say GO** — then launch §1.
3. **Do NOT amend R107** (§3.1).
4. Optional and currently NOT recommended: GPU for the DFO chains (§4.6).
