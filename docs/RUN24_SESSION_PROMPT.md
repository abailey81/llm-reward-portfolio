# RUN 24 — SESSION PROMPT. **READ THIS IN FULL BEFORE YOUR FIRST SUBSTANTIVE ACTION.**

Written 2026-08-06 ~04:10 UTC at Tamer's instruction: *"document absolutely everything from this
session, and write a prompt for the next Claude Code session, don't forget to also tell it to very
deeply and extensively study absolutely all files in this dissertation so it has the comprehensive
knowledge, and zero gaps in knowledge … ensure extremely smooth transition … include my prompts on
that everything should be flawless … preserve these loops, but dive much deeper, and check more
extensively, and check very deeply absolutely everything, from all dimensions and angles possible,
it must not miss anything … minimise the ETA to an absolute minimum … maximise the cores … we went
from 2300 cores at our peak to 544 cores now, this is ridiculous. We need to explore absolutely
everything, and maximise the amount of cores, get back to 2k, and minimise the ETA."*

> **You run the live campaign on an irreplaceable MSc dissertation.** RUN 4 has been running since
> 2026-07-28 21:08 UTC — **T+199 h, elapsed 8.3 d**. Real money is spent, the test data is sealed,
> **there is no re-run.** This supersedes `docs/RUN23_SESSION_PROMPT.md`; where they disagree,
> **THIS WINS.** §4 changes the campaign's operating priority and §5 corrects EIGHT things RUN 23
> got wrong before it got them right.
>
> ⚠ **A SEPARATE SESSION OWNS THE WRITE-UP.** `paper/**`, `docs/GRADE_95_MASTER_PLAN.md`,
> `docs/V2_WRITE_TIME_REGISTRY.md`, `docs/CITATION_WORK_MAP.md` are **NOT YOURS.** `CHANGELOG.md` is
> **SHARED** — re-read it immediately before every edit, and never reuse a date label.
>
> ⚠ **DO NOT REGISTER A LANE.** Reading the board with `lanebus.py` STAMPS a heartbeat. Avoid it.

---

# §0 ★★★★★ TAMER'S STANDING BRIEF — VERBATIM. THIS IS THE OPERATING CONTRACT.

### §0.1 THE FLAWLESSNESS MANDATE

> *"very deeply and strictly monitor everything constantly and ensure absolutely everything is
> strictly absolutely flawless 10000000%. Ultrathink very deeply and extensively. I give you full
> permissions, full freedom, and I ratify the actions. **I give you no permission to stop until
> absolutely everything is strictly absolutely 10000000% absolutely flawless.** Do whatever it
> takes. Very deeply investigate everything, and speed up to an absolute maximum. Please before act,
> make sure you very deeply study this dissertation. Take as much time as you need, as many tokens
> as you need. Make sure you also very deeply and extensively constantly check each record, make
> sure every record individually is very strictly flawless, logical, meaningful. Don't be lazy, I
> give full ratifications, full freedom, full permissions. Please make sure you study every file in
> this project very deeply, all processes, the whole thing going on on Myriad, absolutely
> everything, please don't miss anything. This campaign run is extremely important, and it must be
> absolutely flawless across absolutely all dimensions possible. Dive extremely deep, don't be lazy,
> check absolutely everything very deeply and extensively, make sure you don't miss anything, and
> make sure you always verify, and you are always very precise. Please work very accurately, and
> very surgically, make sure you make no mistakes. Ultrathink 100000 times before doing anything."*

> ★ **2026-08-06:** *"make sure absolutely everything is very logical, meaningful, and absolutely
> flawless and 1000000% absolutely strictly correct"* · *"ensure absolutely everything is 100000%
> correct everywhere without exceptions"*

### §0.2 ★★★★★★ THE CORES + ETA DIRECTIVE — TAMER IS ANGRY ABOUT THIS AND HE IS RIGHT

> **Tamer, 2026-08-06, verbatim:** *"we went from 2300 cores at our peak to 544 cores now, this is
> ridiculous. We need to explore absolutely everything, and maximise the amount of cores, get back
> to 2k, and minimise the ETA."* · *"the speed has to be maximised to an absolute maximum, the eta
> has to be minimised to an absolute minimum, we must take as much as we can from Myriad."*

**THIS IS AN ACTIVE DUTY EVERY PASS.** ⚠ **AND RUN 23 SPENT SIX HOURS ON IT AND GOT IT WRONG EIGHT
TIMES BEFORE GETTING IT RIGHT. §5 IS THE MOST IMPORTANT SECTION IN THIS FILE. READ IT BEFORE YOU
MEASURE ANYTHING, OR YOU WILL REPEAT THE SAME ERRORS.**

### §0.3 ★★★★★★★ THE NEW ABSOLUTE PRIORITY — **THE FLOOR FIRST, THE LADDER SECOND**

> **Tamer, 2026-08-06, and this CHANGES THE CAMPAIGN'S OPERATING PRIORITY:** *"our main priority is
> to bank all the results for absolutely all arms at 30 seeds first, the ladder is optional
> comparing to that. We need the results to write the dissertation now, and we need them fast."* ·
> *"that's the absolute priority, to get all results for the floor first, and then progress."*

**⇒ EVERY ALLOCATION DECISION IS NOW JUDGED AGAINST: does it complete the rung-30 bank?** Work that
climbs any line above 30 is EXPLICITLY OPTIONAL until the floor is complete. §4 says exactly what
is missing, and it is small.

### §0.4 THE LOOP CONTRACT, VERBATIM

> *"Also every 30 min I want you to very closely check everything very deeply, check everything, all
> lines, all records, all outputs, all processes, absolutely everything, it all must be
> 1000000000% strictly absolutely flawless."*
> *"make sure if something is found, its always fixed, and ensure that absolutely everything is very
> strictly absolutely flawless"*
> *"make sure the checks that are every 30 minutes do not stop until they ensure absolutely
> everything is 10000% absolutely strictly flawless. I give them full permissions, do whatever it
> takes to ensure absolute flawlessness."*
> *"also dont forget to add the speed check component all the time, and its maximisation"*
> ⭐ *"make sure you very deeply and extensively study this whole project, have an extremely
> extensive knowledge and absolutely 0 gaps in knowledge."*

⚠ **THE 30-MIN CRON IS CURRENTLY STOPPED.** Tamer cancelled it at 2026-08-06 01:30Z during the cores
investigation. **RE-ARM IT** at `7,37 * * * *` with the STEP 0–6 contract in §9 — *unless* Tamer says
otherwise. The campaign's OWN monitoring cycle (`cycle.py`, every ~5 min) never stopped and is green.

### §0.5 HOW TO READ THAT MANDATE — the most important paragraph in this file

**Full permission raises the bar on the THINKING; it does not lower the bar on VERIFICATION.**

**RUN 23 published EIGHT wrong conclusions to Tamer before arriving at the right one, and every
single one came from banking a measurement without a second, independent route.** The one that
nearly did damage was a lever that a July dossier had already tested and refuted — and searching the
record is what stopped it. **SEARCH THE RECORD BEFORE BELIEVING YOUR OWN SCRIPT. RUN A SECOND
INDEPENDENT DERIVATION BEFORE TELLING TAMER ANYTHING.**

---

# §1 YOUR FIRST COMMANDS

```bash
cd /c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
date -u +%Y-%m-%dT%H:%M:%SZ                      # ★ FIRST. Never assume the clock.
python docs/ops/loginnode_guard.py --once
tail -5 docs/ops/watch/CYCLE_LOG.md
.venv/Scripts/python.exe docs/ops/remote_inbox.py --status   # is Tamer waiting on you?
powershell -File "docs/ops/remote_inbox_launch.ps1" -Status
.venv/Scripts/python.exe docs/ops/line_balance.py --once
.venv/Scripts/python.exe docs/ops/arm_jobs.py
.venv/Scripts/python.exe docs/ops/occupancy_watch.py
.venv/Scripts/python.exe docs/analysis/record_seed_completeness.py     # ★ THE FLOOR CHECK — §4
.venv/Scripts/python.exe docs/analysis/loader_collision_watch.py
ls outputs/campaign_cluster_run4/batches/*.permanent.jsonl | grep -icE "sweep|_test"   # MUST be 0
ssh -o BatchMode=yes myriad "hostname"
```
Then say **"Resuming from: … — next: …"** and CONTINUE. **Never ask "what now".**

⚠ **THE SEVEN RECORD LAYERS (`bash docs/ops/run_record_layers.sh`) COST ~1,342 s OF FULL-ARCHIVE
SCANNING AND CAN PUSH THE CYCLE SWEEP PAST THE 900 s FALSE-DEAD CAP.** Run them when the archive has
grown ≥500 records or hourly, NOT every pass. They returned **ALL RC=0** at 2026-08-06 01:26Z.

---

# §2 ⛔ MANDATORY READING — ZERO GAPS IN KNOWLEDGE IS A REQUIREMENT

| file | why |
|---|---|
| **this file** | the brief |
| **`docs/ops/watch/FLAWLESS_LEDGER.md`** | ⭐ **THE CONTRACT FOR THE LOOP.** Three terminal states · what is NOT a defect · the SPEED component · **every RUN 23 finding and retraction** · every OPEN row. **READ IN FULL BEFORE EVERY PASS.** |
| **`CLAUDE.md`** | LAW. the ★ PRIORITIES, the four authorities, Okhrati's D1–D6, Stefan's S1–S11, the 95+ doctrine, the human register |
| **`PREREGISTRATION.md`** | THE FROZEN CONTRACT. **R101** (read the amendment row IN FULL — point (4) licenses interim rungs as draft-filling), **R111**, **R115**, **Amendment E1** |
| **`docs/MYRIAD_EXPERT_DOSSIER_2026-07-24.md`** | ⭐⭐ **§0-PRE M5 REFUTES TICKET CONCENTRATION WITH A CONTROLLED TEST THAT STARVED US 44→9 RUNNING JOBS. DO NOT RE-PROPOSE IT.** Also M6 (apptainer), M7 (the work model). |
| **`docs/CAMPAIGN_DAY_RUNBOOK_2026-07-13.md`** §10 | the lever list and what was already taken (tmpfs 15G→1G, `reserve: y`, h_rt sizing) |
| **`docs/HANDOFF.md`** §1–§3 | current state + the authority map |
| **`CHANGELOG.md` `[2026-08-05a]` and `[2026-08-06a]`** | RUN 23 in full |
| **`docs/DEFERRED_FIXES_RUN4.md`** | every known-open defect, D1–D72 |
| **`docs/analysis/EXCESS_AND_BENCHMARK_2026-08-04.md`** | ★ **THE BENCHMARK RESULT.** 0 of 59 cells beat a costed equal-weight 1/N on excess Sharpe |
| **`docs/ops/MAINTENANCE_2026-08-12.md`** | ⚠ **UCL OFFICIAL — WED 12 AUG, MAY RUN INTO THU 13.** |
| **`docs/REMOTE_CONTROL.md`** | ★ Tamer's inbound channel. Works. `remote_inbox.py --status` is a STEP-1 board item. |
| **`memory/session-current-focus.md`** ▶ NOW | the live cursor |
| **the newest instruments** | `docs/ops/record_shrink_cache.py` · `docs/ops/falsify_record_shrink_cache.py` · `docs/ops/remote_inbox.py` · `docs/ops/occupancy_watch.py` · `docs/analysis/loader_collision_watch.py` — read each docstring |

### ⛔ THE READING GATE — answer these FROM THE SOURCES before acting
1. What are the **four authorities**, and what happens when they conflict?
2. What is **H2**, and why is the fed tail **ENDOGENOUS**?
3. **What EXACTLY is missing for a complete rung-30 bank, and why can it not be done in one round?** (§4)
4. **Why does `smp-D`'s allocation rule mean we can only reach 10 % of the free capacity?** (§5)
5. **What did M5 test in July, what happened, and why must you not repeat it?** (§5)
6. **Which paths are drift-fenced, and what does editing one cost?**
7. **What does `analyze_campaign.py` do today if you run it, and why must you NEVER "deduplicate the archive"?** (§7)
8. **Which way does the driver log's clock run?** (host-local **+0100**, NOT UTC — convert before writing any timestamp down.)

---

# §3 STATE AT HANDOVER (2026-08-06 04:05 UTC, T+199 h)

```
records 18,637 · spend $45.5019 · drift 0 · freeze MATCHES · repro 8/0/0 · sci OK · board OK
7 record layers ALL RC=0 (01:26Z, 17,988 records) · line_balance CLEAN · seed loss ZERO
CPU cores 536 · 961 jobs · Eqw/hqw 0 · qquota empty · cluster 8,541 running slots
cycle sweep 27.8 s (was 903.5 s before the SWEEP-1 fix) · budget=2 OK (was 99)
exogenous stop 2026-08-27 (21.0 d) · dissertation due 2026-09-01
backup branch: backup-2026-08-05-run23 (pushed, current) · 0 unpushed
```

### THE LADDER — banked rungs (S15)
| line | rung | note |
|---|---:|---|
| gemini-2.5-flash · gpt-5.6-luna · h3 · qwen3.5-9b · sonnet-5 | **568** | COMPLETE |
| haiku-4.5 | 189 | |
| qwen3.6-27b | 100 | |
| deepseek · glm-5.2 · kimi-k3 · nemotron-3-super | **30** | ✔ FLOOR BANKED |
| **core (`c1`, the CONFIRMATORY Opus 5 line)** | **0** | ⛔ **THE ONLY GAP — see §4** |

⚠⚠ **NAMING, BECAUSE TAMER WAS RIGHTLY CONFUSED BY IT.** *"core"* means the **CONFIRMATORY LINE**,
batch tag **`c1`**, model Claude Opus 5, archive dirs `search/` and `test/`, log `driver_core.log`.
**"CPU cores"** means physical cores on Myriad. **NEVER WRITE "core" UNQUALIFIED.** Say *"the
confirmatory line (`c1`)"* or *"CPU cores"*.

---

# §4 ★★★★★★★ THE ABSOLUTE PRIORITY — THE RUNG-30 FLOOR. **IT IS 120 RECORDS.**

**ELEVEN OF THE TWELVE LINES ALREADY HAVE RUNG 30 BANKED.** The entire remaining requirement for a
complete, writable, registered result is **four arms on the confirmatory line**:

```
c1 bayes_opt        0 / 30      c1 cma_es           30 / 30  ✔
c1 tpe              0 / 30      c1 random_search    30 / 30  ✔
c1 distributional   0 / 30      c1 scalar_cvar5     30 / 30  ✔
c1 scalar           0 / 30      c1 placebo          30 / 30  ✔
                                c1 placebo_shuffled 30 / 30  ✔
```

**120 trainings ≈ 1,128 CPU-core-hours ≈ TWO HOURS of the 536 cores we already hold.**

### ⛔ IT MUST GO IN TWO ROUNDS, AND THAT IS A SCIENCE PROTECTION, NOT AN ORDERING WHIM
`campaign.py:1904-1910` builds the H2 pair as **ONE `interleave=True` CRN-paired array** holding
`distributional` AND `scalar` together, and the comment says why: *"A crashed arm has no winner, so
it is silently ABSENT from that array — the pair test would run with four of five arms, and every
seed in it would be paired against a comparator set that is not the registered one."*
⇒ **Round 1 = `bayes_opt` + `tpe` test legs (8 jobs, ALREADY QUEUED). Round 2 = the `h2_pair`, which
is only submitted after Round 1 completes.** All nine confirmatory arms already have frozen winners,
so nothing else gates it. **DO NOT try to split or reorder the pair.**

### THE COST OF DOING NOTHING, AND THE COST OF ACTING
```
NO INTERVENTION   R1: 235 jobs ahead at ~6.4 jobs/h = 37 h wait + 9.4 h run
                  R2: submits after, back of the queue again, ~30 h + 9.4 h
                  => complete rung-30 bank about 9 AUGUST
WITH INTERVENTION R1: hold kimi's pending briefly -> c1 dispatches in 1-2 h -> done same day
                  R2: h2_pair submits, hold again -> done next morning
                  => complete rung-30 bank about 7 AUGUST.   TWO TO THREE DAYS SAVED.
```

### ⭐ THE INTERVENTION, AND IT IS SMALL — **AWAITING TAMER'S EXPLICIT GO**
**`c1` needs 64 of our 536 CPU cores, not all of them.** It has 8 jobs. So the action is NOT to
starve the fleet (that is the M5 failure that took us 44→9 running jobs). It is:

1. `qhold` **just enough** of kimi's pending jobs that `c1`'s 8 rise to the top of OUR pending set.
2. Watch for `c1`'s jobs to start (one `schedule_interval` is 10 min).
3. `qrls` kimi **immediately** — hard limit 90 minutes, release regardless of outcome.
4. Kimi's ~68 RUNNING jobs are never touched.
5. Repeat once when the `h2_pair` submits.

⚠ **THIS CROSSES TAMER'S STANDING RULE** ("never lower the priority of any of our jobs, EVER",
2026-07-24). `qhold`/`qrls` is chosen over `qalter -p` precisely because it is **reversible** — a
non-operator can only DECREASE POSIX priority and probably cannot restore it. **Tamer was asked
twice and had not given an explicit go when this session closed. ASK AGAIN, SHOW HIM §4's
arithmetic, AND DO NOT ACT WITHOUT IT.**

---

# §5 ★★★★★★★ THE CORES QUESTION — **THE ANSWER, AND THE EIGHT WRONG TURNS. READ BEFORE MEASURING.**

## 5.1 THE ANSWER, AND IT IS STRUCTURAL

```
qconf -sp smp-D   ->   allocation_rule   $pe_slots
```
**`$pe_slots` means every slot of a job must land on ONE host.** Our jobs are `--pack 8
--cores-per-training 1`, so they need **8 free CPU cores on a single node**.

**MEASURED 2026-08-06 03:00Z, on the d00 hosts that are open to us and not disabled:**
```
8+ free :   5 nodes            TOTAL FREE AND OPEN TO US: 383 CPU cores
4-7 free:  28 nodes
2-3 free:  60 nodes            what each job width could claim from those same 383:
1 free  :  43 nodes              width 8 (ours)   5 jobs =  40 cores  <- 10 %
0 free  :  58 nodes              width 4         39 jobs = 156 cores  <- 4x
                                 width 2        150 jobs = 300 cores  <- 7.5x
                                 width 1        383 jobs = 383 cores  <- 100 %
```
⇒ **AT OUR CURRENT SHAPE WE CAN REACH ONE TENTH OF THE CAPACITY THAT IS OPEN TO US.** The free cores
are real; they are shattered into fragments of 1–7 and our 8-wide shape cannot use them.

**IT EXPLAINS EVERY OBSERVATION:** `ucecgwh` (1-wide) has **zero** backlog · `uccaewo` (4-wide) has
**zero** backlog · all three 8-wide users on our tier (us, `ucaqcsu`, `ucaqanw`) sit pinned at
**504–536** · and we surge to 2,300 overnight because that is when whole nodes empty.

**Myriad is 13,048 CPU cores over 355 hosts; the d00 pool is 9,432 over 262 = 72 % of the machine.
We are not locked out of anything.** Our eight trainings are INDEPENDENT processes that do not share
memory and do not need the same node — `$pe_slots` forces them together for no reason our workload
requires.

## 5.2 ⛔⛔ THE EIGHT THINGS RUN 23 GOT WRONG. **DO NOT REPEAT THESE.**

1. **"12,044 free CPU cores on 518 nodes"** (then 10,499, then 8,863). **ALL RETRACTED.**
   `qstat -f` **TRUNCATES the queue-instance name**, so one host appears as both `node-d00a-005` and
   `node-d00a-005.myria` and a `sub(/\.myriad.*/,"",h)` does not match the truncated form. **Every
   host was counted twice; the figures were ~5× inflated.** ⇒ **ALWAYS strip with `sub(/\.myria.*/`
   and verify the distinct-host count against ~259 for d00.**
2. **Publishing free capacity WITHOUT applying access control.** Of 56 clear hosts with ≥8 free,
   **47 are PAID/private and only 9 are open to us.** ⚠ **This repository has already WITHDRAWN this
   exact claim twice — lane messages M203 and M239.** Build the PAID host list first
   (`qconf -shgrp @PAID_*`) and subtract it before quoting any number.
3. **"14.2 jobs/h queue drain."** Fitted to ONE 38-minute window. **The real figure over a 6-hour
   baseline is 6.4–6.8 jobs/h**, confirmed four times. ⇒ **Never fit a rate to less than several
   hours.**
4. **"The confirmatory line starts in ~19 h."** Wrong twice (then ~35 h, now ~37 h). Each revision
   came from discovering another queue term. ⇒ **Give the MECHANISM and a RANGE, never a point
   estimate from a short window.**
5. **"Pack 4 gives 18× more placeable capacity."** One volatile snapshot; forty minutes later the
   same measurement read 4 vs 10. ⇒ **The DIRECTION is robust and structural (§5.1); the MAGNITUDE
   swings minute to minute. Quote the histogram, never an instantaneous count.**
6. **"Concentrate our tickets by holding jobs."** ⛔ **ALREADY TESTED AND REFUTED — dossier §0-PRE
   M5, 2026-07-26.** They held 228 of 309 pending jobs; priority moved 2.0165→2.0413 (waiting-time
   accrual, which happens anyway), **zero** wide jobs placed, and **our running count decayed 44→9.
   We starved ourselves.** ⇒ **DO NOT PROPOSE IT. Read M5 first.**
7. **"Our share is in a structural monotone decline."** The status-commit history shows it has
   oscillated **336 ↔ 2,320 for the entire campaign**, with a measured diurnal shape: **best
   03:00–08:00Z (mean 1,524), worst 19:00–00:00Z (mean ~950)**. The 2,320 peak was **2026-08-03
   02:21Z**, a Sunday night. ⇒ **Any claim about a trend needs the whole series, not 18 hours.**
8. **"Gold projects / override tickets are the answer."** `Gold*` carries `oticket 400000` and
   `AllUsers` carries 0 — **but every user beating us has `otckt = 0` too**, and `Gold`'s `acl Open`
   is a named list of teaching accounts, not everyone. Refuted within minutes of proposing it.

**ALSO REFUTED BY MEASUREMENT, so you do not have to redo them:**
* **`h_rt` reduction** — 3,987 task epilogues: median 8.64 h, p99 11.71 h, **p999 and max both
  15.01 h against a 15.00 h request.** No slack. And a SHORTER request is BETTER for backfill, so our
  15 h is an advantage, not a liability.
* **`snx`** — capacity ~9,990 per host. Not a throttle.
* **A per-user slot RQS** — the only rule set (`slowemdown`) is DISABLED and targets another user.
* **Memory over-request** — `qacct maxvmem` on our own jobs is **11.3–11.9 GB against a 16 GB
  request (2 GB × 8)**, so we over-ask ~26 %. Trimming to 13 GB unlocks 92→106 hosts on memory —
  **but memory is NOT the binding dimension** (92 hosts already qualify on memory, only 9 on cores).
* **"We were drained/throttled/killed"** — **263 of 263 jobs that ended in the last 24 h exited
  `failed 0, exit_status 0`.** Nothing was killed.
* **Other CPU pools (@b/@e/@f/@l/@u)** — outside `smp-D`, excluded by the determinism envelope.
* **Raising our own priority** — impossible; a non-operator can only DECREASE POSIX priority.
* **Priority creep** — measured on `c1` job 91237 over 6.4 h: 2.00295 → 2.00394 = **+0.00015/h**.
  Real but far too slow to matter before 27 August.

## 5.3 ⭐ WHAT IS ACTUALLY LEFT ON THE CORES QUESTION — Tamer wants 2,000 back

1. ⭐⭐⭐ **NARROW THE JOB WIDTH.** `--pack 8 --cores-per-training 1` is a **LIVE COMMAND-LINE
   ARGUMENT on all 14 drivers** (verified), so it changes by supervisor restart with **no fenced code
   edit**, and pack was already changed 5→8 mid-campaign on 2026-07-31. **No scientific cost** —
   each training is its own process with its own seed. **THE SMART VERSION: narrow ONLY the line that
   matters.** `c1` currently has **zero running jobs**, so restarting its supervisor risks nothing in
   flight — no other line can say that. ⚠ **A restarted driver ADOPTS its existing jobs (P305), so
   this will NOT re-shape work already queued; it pays off from the NEXT stage onward.**
   ⚠ **Job cap `max_u_jobs = 1000` and we sit at 961** — narrowing everything doubles the job count
   and will not fit. Narrowing `c1` alone costs ~+22 jobs and does.
2. ⭐⭐ **THE QUEUE ORDER (§4).** Awaiting Tamer.
3. ⭐ **THE EMAIL TO `rc-support@ucl.ac.uk`** — drafted and approved by Tamer, address verified from
   Myriad's own `/etc/motd`. ⚠ **NOT `myriad-users@ucl.ac.uk`, which is the all-user announcement
   list.** Ask: a temporary priority allocation until 27 August. **Check with Tamer whether he sent
   it.** The final text is in the CHANGELOG entry for this session.
4. **WATCH THE DIURNAL WINDOW.** We are strongest 03:00–08:00Z. If we are NOT above ~1,200 cores in
   that window on a given day, that is a finding worth chasing.

---

# §6 ★★★ THE SEED QUESTION — THE ANSWER IS STILL GOOD. KEEP IT THAT WAY.

**ZERO sealed-test seeds are permanently lost.** Re-verify EVERY session — it is one command:
```bash
ls outputs/campaign_cluster_run4/batches/*.permanent.jsonl | grep -icE "sweep|_test"   # must be 0
```
⇒ **A HOLE IS TRANSIENT BY CONSTRUCTION.** The discriminator: *hole + jobs running/queued = mid-fill,
benign · hole + ZERO running AND ZERO queued = actionable.*

---

# §7 ⛔⛔ THE BIGGEST OPEN ITEM — `analyze_campaign.py` CANNOT RUN, AND THE OBVIOUS FIX IS A TRAP

**D49–D51, UNCHANGED.** The loader admits every `test_leg_*` line into one flat record list under the
SAME arm labels, and `_seed_scores` groups on `(arm, seed)` with no line term.
✔ **IT FAILS LOUD** — `_seed_scores` raises `ValueError` and `analyze()` guards only `AssertionError`.
⚠⚠ **THE TRAP: the guard's own message says "Deduplicate the run archive". FOLLOWING THAT ADVICE
CONVERTS THE LOUD FAILURE INTO A SILENT ONE.** ⛔ **DO NOT DEDUPLICATE THE ARCHIVE.** The repair is
prototyped at `docs/analysis/a79_fix_proof.py:60-84`; `scripts/**` is fenced, so it applies at
teardown, BEFORE `bank_gate`. **CRN-1 goes in the same edit** (`analyze_campaign._paired:1553-1557`
pairs on the seed number ALONE; exposure measured ZERO on all 2,416 pairable cells).

---

# §8 EVERYTHING RUN 23 FIXED

| id | what |
|---|---|
| **SWEEP-1** | ⭐⭐⭐ **THE 900 s CAP HAD ALREADY BEEN BREACHED** (2026-08-05T07:39:24Z, sweep 903.5 s, cycle lines 933 s apart — a healthy loop inside the false-DEAD window). Built `docs/ops/record_shrink_cache.py`, memoising the shrunken record on `(path, mtime_ns, size)`. `science_watch` now runs the full archive in **14 s** against a 129 s baseline. **Sweeps 903.5 s → 27.8 s.** |
| **SWEEP-1 defects** | Four of my own, all found by the falsifier: a 439 MB full rewrite every cycle (drove `budget_watch` to 6 timeouts in 4 h) → append-only shards; a single append target that **tore 710 cache lines** under two concurrent writers → one shard per process; a stale-sweep that would have deleted its own shards; and a proof that cleared the LIVE cache and died on a `PermissionError` → private cache dir. |
| **budget_watch / W6** | ⭐⭐ **THE THIRD FULL-ARCHIVE WALKER, AND THE ONE STILL BREAKING THE CYCLE.** W6 had blamed a spend-ledger scan twice; the ledgers are static at 2,956 rows. `_generation_depth` globbed every `record.json` against a 180 s timeout. Fixed with a 2-field PROJECTION (3.3 MB cache vs 459 MB). **Byte-identical to `git show HEAD:`, 97.0 s → 3.8 s. `budget=99` → `budget=2`.** |
| **test_integrity_gate** | A committed test had been **RED since 2026-08-04**: it asserted `gate.check(missing) == []`, pinning the fail-open P286/P294 removed. Corrected to assert `["I0 vacuity"]`, and **falsified** against a stub returning `[]`. ⚠ **Nothing runs the full suite on a cadence** — that is how it survived a day. |
| **guard:truncation** | Re-triaged against its own trigger: 8 of 2,956 rows, three models, **zero on any `distributional` arm and zero on `c1`** — both live triggers CLEAN. Upper bound on cap-induced candidate loss UNCHANGED at 2. |
| **§11.1 item 1 CLOSED** | The standing to-do calls `src/inference/**` *"the largest untouched surface"*. **Measured: 94.25 % line+branch against the repo's own 88 % gate.** Only `ood_stress` at 85 % is soft. **The row's premise is false and it sent four handovers to the wrong place.** |
| **D-j** | R101 says the eleven climb "IN LOCKSTEP"; execution does not (haiku 189 vs `c1` 0). The registered conclusion is unaffected (the result is the MINIMUM) but the write-up must say so. |
| **Verification standard** | The cache ships with `docs/ops/falsify_record_shrink_cache.py`: **12/12 unit cases · mutation control on an EXACT expected set · a STATIC byte-identity proof against `git show HEAD:` on a frozen 400-record slice.** Use that file as the template for any future instrument. |

---

# §9 ★★★★★ THE 30-MINUTE LOOP — RE-ARM IT, PRESERVE IT, AND GO DEEPER

**Re-arm at `7,37 * * * *`, session-scoped, unless Tamer says otherwise.**

**STEP 0 CLOCK** (`date -u`; driver-log stamps are host-local **+0100**) · **1 BOARD** (§1; read each
tool's OWN verdict, never a pipe's exit code) · **2 THE FLOOR** (§4 — has anything landed on `c1`'s
four arms?) · **3 DEEP DIVE** (§10) · **4 EVERY RECORD** (seven layers on the §1 cadence + the
science audit) · **5 SPEED** (§5.3 + the four questions below) · **6 FIX** (falsify against the
ENTRY POINT; **write the test FIRST**; send an auditor) · **7 RECORD**.

**Every finding is FIXED.** Three terminal states only: **FIXED** (falsified against pre-fix
behaviour), **PROVEN-BENIGN** (with the measurement), **ESCALATED** (with everything around it
fixed). **No row may age three passes.**

### THE FOUR SPEED QUESTIONS, EVERY PASS
1. **Are we holding every CPU core we could hold?** Deep queue + flat total = fair share; say so
   with the number. **But re-measure §5.1's fragmentation histogram before concluding anything** —
   that is what actually caps us.
2. **Has anything become schedulable?** `Eqw`/`hqw` must be 0, `qquota` empty, and re-read
   `max_u_jobs` (1000) against our live job count IN THE SAME BREATH.
3. **Is any CPU core on work that cannot complete the FLOOR?** Under §0.3 that now means: is
   anything running that is not `c1`'s four missing arms? Today the answer is *all of it*.
4. **What is the date for the complete rung-30 bank, and did it move?** That number IS the result
   now. **If it has not moved in three passes, that is an OPEN FINDING.**

---

# §10 WHERE RUN 24 MUST GO DEEPER — STILL UNSTARTED

1. **`scripts/analyze_campaign.py`'s 39 registered keys** — D49–D72 cover the register, CRN-1 the
   pairing, the rest have never been read. **This is now the largest genuinely untouched surface**
   (`src/inference` is NOT — see §8).
2. **The ops monitors RUN 22/23 did not exhaust** — `stage_eta.py` (67 KB, ~470-line selftest
   unread), `transport_health.py`, `retriage_alarms.py`, `reject_taxonomy.py`, `publish_status.sh`
   (35 KB, ⚠ a running bash script).
3. **Extend the record cache to the seven record layers.** ⚠ **The blocker is the WALK, not the
   shrink**: nine archive walkers carry **at least five different exclusion rules**, measured. It
   needs `load_shrunken_records` to grow a per-caller `exclude` predicate plus a byte-identity proof
   per layer. Measured today: `_quarantined*` = 0 records · `.pull_tmp*` = 3, all at the first path
   segment · D18-nested = 2. **PROVEN-BENIGN today, latent if a `_quarantined*` tree ever appears.**
4. **Extended `instrument_agreement` rows** — add the job census and the seed frontier. **A7 must
   read zero before the cross-model synthesis at teardown.**
5. **Put the full `pytest` suite on a cadence** (session-start preflight or teardown, NOT the 30-min
   loop). A red test survived a day because nothing ran it.
6. **⚠ SERIALISE YOUR OWN HEAVY SCANS AGAINST THE LIVE CYCLE.** Seven layers ≈ 1,342 s; running them
   beside anything else produced a 1,307 s sweep and a 998.6 s sweep on 2026-08-05.

---

# §11 STANDING RULES THAT MUST SURVIVE THIS HANDOVER

- **NEVER** read a treatment arm's SEALED-TEST outcome for INFERENCE. Know what R101 (4) permits.
- **NEVER** change a frozen threshold. **NEVER** make a check pass by weakening it.
- **NEVER** raise the 900 s sweep cap or the 180 s probe timeouts.
- **NEVER** add Claude/Anthropic attribution. **Tamer is sole author.**
- **NEVER** `git clean -x`, `git add -A`/`-u`, or `git stash`. **Stage BY NAME**, leave nothing staged.
- **NEVER** `qdel` a campaign job. **NEVER** `qalter -p` (irreversible for a non-operator) — use
  `qhold`/`qrls` if Tamer authorises a reordering.
- **NEVER** edit `src|scripts|config|prompts` while live (drift-fenced). `docs/**` and `tests/**` are safe.
- **NEVER** deduplicate the archive. **NEVER** junction the archive.
- **NEVER** put backticks, `$(…)` or heredocs in a `bash -c` string or a `-m` commit message.
- **PowerShell console is cp1251.** `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`,
  and `subprocess.run(..., encoding="utf-8", errors="replace")` — `text=True` uses the system codepage.
- **⚠ `.ps1` FILES ARE ASCII-ONLY** and must pass `Parser::ParseFile`.
- **⚠ Editing a running loop is INERT** — `cycle_loop.sh`/`publish_loop.sh` need a RESTART;
  `cycle.py`/`publish_status.sh` are re-invoked each iteration and do not.
- **END-OF-WORK, all four:** `scripts/update_handoff.py --suite-status "…"` · a SHORT cursor ▶ NOW
  entry · a DETAILED CHANGELOG block even with no commits · push the backup branch.

---

# §12 HARNESS LIMITS — MEASURED, NOT ASSUMED

```
qhold / qrls <ids>               WORKS, REVERSIBLE  <- the ONLY sanctioned reordering mechanism
qalter -p <negative>             PERMITTED but ONE-WAY for a non-operator -- treat as PROHIBITED
qdel <explicit ids>              WORKS but PROHIBITED on campaign jobs
qstat -u ucestes -xml            REQUIRED for names/states; plain qstat TRUNCATES to 10 chars
qstat -f                         ⚠ TRUNCATES the queue-instance hostname -- strip with /\.myria.*/
qconf -sconf|-ssconf|-sp|-sq|-sprj|-shgrp|-suser   ALL WORK  <- the whole scheduler surface
qacct -o ucestes -d 1 -j         WORKS  <- exit statuses; 263/263 clean on 2026-08-06
git commit --only <path>         WORKS, and is REQUIRED wherever the tree is dirty
git pull --rebase                FAILS ALWAYS on this tree -- use git fetch + git show
Start-Process (detached)         WORKS  <- the pattern for a loop that must outlive the session
taskkill /PID                    BLOCKED    HKLM registry write   BLOCKED
```
**⇒ TEST THE SPECIFIC COMMAND. Several "BLOCKED" claims have been disproved.**

---

# §13 ★★★ THE LESSONS RUN 23 PAID FOR

1. **A SURPRISING RESULT IS A CLAIM ABOUT YOUR OWN SCRIPT FIRST — RUN 23 HIT THIS EIGHT TIMES IN
   SIX HOURS.** A truncated hostname inflated a headline number 5×. A rate fitted to 38 minutes was
   double the truth. A placement count swung 5× in forty minutes. **Two independent derivations, or
   it is not a finding.**
2. **SEARCH THE RECORD BEFORE BELIEVING YOUR OWN SCRIPT.** The single most damaging idea of the
   night — concentrate tickets by holding jobs — had already been tested in July and had starved us
   44→9 running jobs. **Reading `MYRIAD_EXPERT_DOSSIER §0-PRE M5` is what stopped it.**
3. **A CONTROLLED COMPARISON BEATS YOUR OWN ARITHMETIC.** Every snapshot-based conclusion collapsed.
   What survived was seven independent users compared on project, job width, wall-clock request and
   backlog. **Look for the natural experiment before you build a model.**
4. **THE INSTRUMENT IS GUILTY BEFORE THE CAMPAIGN IS.** `budget=99` was blamed on the spend ledgers
   twice; it was a full-archive walk. `src/inference` was called untested for four handovers; it is
   at 94 %.
5. **A FIX WITHOUT A TEST DOES NOT SURVIVE ITS AUDIT.** Every RUN 23 fix that shipped with a
   falsifying test survived. The four defects in the cache were all found by its own falsifier.
6. **YOUR OWN DEEP CHECKING IS LOAD ON THE BOX.** A 1,307 s sweep and a 998.6 s sweep both landed in
   windows where this session ran whole-archive scans beside the live cycle.
7. **ONE NAME PER OBJECT.** "core" meant both a CPU core and the confirmatory line in the same
   sentences, and it genuinely confused Tamer. `CLAUDE.md` §C1 mandates this and it was ignored.

---

# §14 THE ONE PARAGRAPH TO CARRY

**Eleven of the twelve lines already hold rung 30. The entire remaining requirement for a complete,
writable, registered result is 120 trainings on four arms of the confirmatory line — about two hours
of the CPU cores we already hold — and it is blocked not by Myriad but by our own queue order and by
a job shape that can reach only a tenth of the free capacity. Tamer's priority is now the FLOOR, not
the ladder. Maximise the CPU cores and minimise the ETA, but measure twice and search the record
before you believe anything: RUN 23 published eight wrong answers on exactly this question before it
found the right one, and the worst of them had already been refuted in July by a controlled test
that starved the campaign.**
