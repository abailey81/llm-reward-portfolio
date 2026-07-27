# CAMPAIGN LAUNCH — READY. Read this first, then launch.

**Written 2026-07-27 ~21:00 BST at the end of the launch-gate session. Everything below was
MEASURED or OBSERVED first-hand on that date; nothing here is inferred unless it says so.**

---

## 1. THE LAUNCH COMMAND

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
| `--search-threads 1` | threads are ~34 % efficient at 8; and `threads x pack` cores made an UNPLACEABLE 64-core request | §4.3 |
| `--chunk-tasks 1` | one job per task. Arrays are SERIALISED (`hqw` on the tail) and tails have twice been PURGED | §4.4 |
| `--exclude-hosts node-d00a-230` | that node has no apptainer and ate 13 jobs in 90 min | §4.6 |

**Before launching, Tamer must run `python scripts/freeze.py` (R94 — HIS action, never a lane's).**
As of this writing: `frozen: false`, `freeze_hash: null`, `freeze.py --check` **RC=0**.

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
