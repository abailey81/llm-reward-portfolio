# RUN 4 -- LIVE STATUS

**Auto-generated 2026-08-11 04:34 UTC -- T+319h25m.** Refreshed about every 1-1.5 minutes (measured; the publish itself takes
~60 s, dominated by one ssh for the live core count) and pushed to GitHub, so
it is readable from a phone. To send an instruction back, edit
[docs/REMOTE_CONTROL.md](REMOTE_CONTROL.md) -- the session polls it on the same interval and writes
back what it did.

## Health

| | |
|---|---|
| elapsed | **T+319h25m** (launched 2026-07-28 21:08 UTC; exogenous stop 2026-08-27) |
| lines up | **6 / 12 running; 6 COMPLETE (gemini-2.5-flash, gpt-5.6-luna, h3, haiku-4.5, qwen3.5-9b, sonnet-5)**, all five arms submitted on **10 of the 10 leg lines** (h3ss is single-arm by design) |
| stalest driver log | **2 min (kimi-k3)** old (P218: the STALEST of the still-running lines, completed ladders excluded; above ~30 means that line has stopped progressing) |
| records archived | **29506** |
| **Myriad maintenance** | **2026-08-12 from 08:00 UTC, at risk all day** (in 1.1 days). Delayed from Aug 11. Jobs may die and REQUEUE idempotently; the supervisors ride it. Playbook: docs/ops/MAINTENANCE_2026-08-12.md |
| LLM calls / spend | 2956 / **$45.5021** |
| transport health | **timeouts 6h=0; worst streak 0/240 (0.0% to fatal), - on -, age UNKNOWN; none live, newest failure 17.8 h ago** |
| transport timeouts (cumulative, ever) | 354 -- a level with no rate; read the row above |
| guards | **RC=2**, not green: truncation transport  |

## Compute

| | |
|---|---|
| cluster jobs | **674** = 137 running + **183 ELIGIBLE** + 354 held by us + 0 held only by the site |
| | *These four ADD to the total, by construction. "queued" used to lump the last three together and overstated the ready backlog by ~62% (762 shown against 470 actually dispatchable). Only ELIGIBLE can be dispatched. **held by us** is the LADDER LOCK, ours to lift. **held only by the site** is the policyjsv throttle, which drains itself at ~700-1,000 jobs/h and is NOT ours to lift -- counted EXCLUSIVE of our own holds, because a job commonly carries both.* |
| **cores computing** | **1096** |
| **cores doing RUNG-RAISING work** | **100.0%** -- 1144 of 1144 cores (61 min old) |

A core counts as USEFUL only if its job fills the assurance block that LIFTS its line's banked rung. The rest is real work whose records raise the reported result by ZERO until every block below them lands. Cause: the C4 ladder lost its ordering mechanism (D73) -- `campaign.PRIORITY_RUNG_BASE = 0` and all six blocks are submitted concurrently, so nothing orders them. THE COMPENSATING CONTROL IS THE LADDER LOCK (`job_rank_governor.py`), which holds ABOVE-BLOCK work so every freed slot goes to a line that actually gates the rung; the `held by us` figure in the jobs row above is how much of it is applied RIGHT NOW. !! IT CANNOT MOVE A RUNNING JOB, so after it is applied this percentage improves only as the over-served line's jobs EXPIRE -- about one job duration. A flat reading minutes after applying it is expected, not a failure.

Per-rung ETAs. **The EMPIRICAL block is the one to read**: it is remaining work divided by the rate
we are actually achieving, anchored at the moment this page was generated. The registered model is
kept beneath it as a **duration** and to name the binding constraint. *(Until 2026-08-03 this panel
anchored the model's makespan to LAUNCH rather than to now, so it printed dates in the PAST -- it
showed 08-02 on a page generated 08-03. Fixed; an ETA is now never a past date.)*

```
generated 2026-08-11 04:35 UTC | elapsed 13.31 d | 15.8 d to the Aug-27 stop
test tier: 27,963 records over 71 of the 71 registered units (lanes.py _TEST_UNITS_PER_RUNG)

MEASURED test-tier throughput (record mtimes; an observation, not a model):
    => OPERATIVE RATE 88.4 rec/h  (the 12 h window; the shortest one an ETA may be priced from)
    last  1 h     148 records     148.0 rec/h   NOISE, not a rate: shorter than one job's 15.0 h quantum, so it samples the gaps between 8-record bursts
    last  3 h     289 records      96.3 rec/h   NOISE, not a rate: shorter than one job's 15.0 h quantum, so it samples the gaps between 8-record bursts
    last 12 h    1061 records      88.4 rec/h   usable
    last 24 h    2314 records      96.4 rec/h   usable
    12 h rate is 28% from ONE line (test_leg_deepseek_v4_pro); 5 line(s) contributed at all
    (windows under 12 h are a STALL INDICATOR ONLY and do not price the ETA -- the arrival quantum is a 15 h pack-8 job)

EMPIRICAL ETA -- BOTH columns divide total remaining by a FLEET-WIDE rate, so both
    assume freed slots are REDIRECTED to whatever still owes work. earliest uses
    the whole fleet (88 rec/h); latest excludes cells already within
    8 of the ceiling (88 rec/h). Window 12 h.
    !! NEITHER IS AN UPPER BOUND. Without redirection the true bound is the
    slowest owing cell, which is INFINITE for every rung while most owing cells
    produce nothing -- see the stage-barrier line below. Read 'Aug-27?' as
    'is this plausible on current throughput', NOT as an assurance verdict.
    !! `remaining` IS A RECORD COUNT AND `REACHED` MEANS *THE COUNT IS MET* --
       IT IS **NOT** THE BANKED RUNG. One missing seed below an arm's frontier pins
       its whole line. For the TRUE bank run `docs/analysis/record_seed_completeness.py`.
     rung  rec-count left     -1h  earliest (UTC)    latest (UTC)      Aug-27?
       30           0       0  REACHED           REACHED           yes
      100           0       0  REACHED           REACHED           yes
      189           0       0  REACHED           REACHED           yes
      279       1,501     148  2026-08-11 21:33  2026-08-11 21:33  yes
      340       3,636     148  2026-08-12 21:42  2026-08-12 21:42  yes
      403       5,841     148  2026-08-13 22:38  2026-08-13 22:38  yes
      568      12,365     148  2026-08-17 00:26  2026-08-17 00:26  yes
    GATED = the relevant rate is zero, so no throughput number can date that row -- it is
    waiting on a stage barrier (C1 chain / C3 gate), not on cores.
    !! 4% of the rung-568 backlog (476 records) sits on cells that produced NOTHING in the 12 h window -- work behind a stage barrier (C1 chain / C3 gate) is not accelerated by redirected cores. Neither column models when it starts.

REGISTERED MODEL (src/cluster/lanes.py) -- a DURATION from a standing start, not a date:
     rung     @1096 cores      @830 cores   binding
       30           4.6 d           4.6 d   critical_chain
      100           4.6 d           4.6 d   critical_chain
      189           4.9 d           6.5 d   throughput
      279           7.0 d           9.3 d   throughput
      340           8.4 d          11.1 d   throughput
      403           9.9 d          13.0 d   throughput
      568          13.7 d          18.1 d   throughput

    saturation: more than ~3235 cores buy NOTHING at rung 568
    critical-chain floor: 4.64 d total, 0.00 d still to run   (every DFO arm has spent its full candidate budget)
    (measured from candidate RECORDS on disk, never from elapsed wall-clock -- P245)
    (serial by design, immune to more cores; every ETA above is clamped to it)

    NOTE: 'remaining' is a RECORD COUNT, not a banked rung -- an arm can hold n records
    and still bank lower if a seed below its frontier is missing (S15). And the range
    assumes the measured rate survives the line-major handover, which is an assumption.
```

### Are we using the maximum Myriad can give us? Re-derived from SGE itself, 2026-08-03 (record sections 120, 121, 122, 123)

**Yes, and the reason changed.** This block used to say the limit was our own experiment having
nothing more to submit. **That is no longer true and has been replaced with what was measured** -- we
now hold a deep backlog we cannot place, and the binding constraint is UCL's fair-share policy, which
is not ours to change.

* **The jobs ARE assignable, `qquota -u ucestes` is EMPTY, and fair share is real -- but it is NOT
  "the whole story", and the two numbers this bullet used to quote were both WRONG (corrected
  2026-08-06, RUN 24).** It said *"every host has 105-167 GB free"* and *"2,576 cores are
  placeable"*. **Neither survives measurement.** (i) The memory figure read `hl:mem_free`, the OS
  free pool, when the scheduler gates on the `hc:memory` CONSUMABLE (`qconf -sc`: `memory` is
  requestable AND consumable). On `node-d00a-218`: `hl:mem_free=120.8G` but **`hc:memory=16.0G`** --
  144 G of a 160 G capacity already RESERVED while only 67 G is USED. (ii) The 2,576 figure is ~5x
  the truth, the signature of the `qstat -f` hostname-truncation double count already retracted in
  RUN 23 section 5.2. **The audited instrument (`docs/ops/placeable_capacity.py`, which takes queue state
  from `qstat -f`, slots from `hc:slots`, and gates on memory and tmpfs) measured on one snapshot:
  pool d = 24 placeable cores, pool b = 24, and 324 of d00a's 412 free slots (79%) are STRANDED on
  hosts holding fewer than one pack-8 job.** So the ceiling is fragmentation AND the memory
  consumable AND fair share together -- and the honest statement is that on a busy day there is
  almost nothing to place, which is why the 2,320-core peak of 2026-08-03 was an emptier cluster
  rather than a setting we lost.
* **Every other lever has been individually EXCLUDED BY MEASUREMENT, not by argument.** `qdel` on our
  own running jobs would destroy up to 15 h of irreplaceable work each; `qalter` on the parallel
  environment is refused site-wide by the JSV; raising priority is operator-only; and **lowering our
  own priority is permitted but INERT** (`npprior` is 0.500 for every job on the cluster, so the
  weight cancels out) **and ONE-WAY** -- `qalter -p 0` is denied, so it cannot be undone. Widening the
  pool buys 2-4% and memory 0.7%, and both need a twelve-line relaunch of a live campaign.
* **And there is no waste to reclaim on the other side of the equation.** The 8.8% gate-failure rate
  counts candidates rejected BEFORE any training is submitted (one LLM call, not a 15 h training),
  and **zero trainings have been lost**: all **6** completed ladders hold 568 seeds with
  **ZERO holes** (counted live from S15; this used to name "gemini's five arms and h3" and went stale
  the moment a third line finished).
* **DISK blocks zero hosts. MEMORY DOES NOT -- this bullet was wrong and is corrected (2026-08-06,
  RUN 24).** It claimed *"Memory was never scarce at all (160 GB free per host); the three separate
  investigations that 'fixed' it were fixing a non-problem."* **The three investigations were right
  and this sentence was the non-problem.** Measured: of the 21 d-pool hosts open to us holding >= 8
  free slots, **8 cannot take a pack-8 job because `hc:memory` is under the 16 G it requests**
  (2 G/slot x 8). `docs/DEFERRED_FIXES_RUN4.md:1757` had already measured the same effect at 82 % on
  2026-08-02 and this file contradicted it for three days. 160 GB is the host's memory CAPACITY, not
  its free consumable.

**Bottom line: buying more hardware cannot make this finish sooner, and neither can any setting we
control.** The seed ladder is tiered (30 -> 189 -> ... -> 568), a truncated run banks the largest
COMPLETED rung, and the stop date is fixed -- so if capacity ever fell short we would simply report at
a lower rung, which is a valid pre-registered result, never a failure.

**Why the cores figure sometimes FALLS while everything is healthy.** Two effects superimpose. A
**completion wave**: every pack-8 job that exits releases 8 slots AND delivers 8 records at once, so
*cores down with records up is throughput ARRIVING*, not leaving (measured 309 -> 437 -> 469 records/h
while cores fell 2,320 -> 1,776). And **rising competition**: other users appearing takes share from
us. A level read without its rate tells the opposite story, which is why the record count and its
delta sit on every monitoring line below.

## Stage -- BOTH phases are running at once

Two things happen per line. **SEARCH:** the LLM writes 5 reward programs, each is trained once and
scored on validation data, the results are fed back, and it writes 5 more -- six rounds. **SEED
LADDER:** once a line's five winners are frozen, they are re-trained on the SEALED data at 30, 100,
189, 279, 340, 403 and finally 568 seeds. **The ladder is NOT a future phase -- it is running now,
and **6 of the 12 lines have already finished the whole thing** (counted live from S15 this
publish; this sentence read a hardcoded "two" until 2026-08-09, by which time six were complete --
the page contradicted its own Health row and its own ladder table).**

| arm | furthest generation | search candidates so far |
|---|---|---|
| distributional | g5 of 5 | 307 |
| scalar | g5 of 5 | 284 |
| placebo | g5 of 5 | 277 |
| scalar_cvar5 | g5 of 5 | 275 |
| placebo_shuffled | g5 of 5 | 280 |

### The seed ladder, live

> ## ==> BANKED COMMON RUNG = 189 <==
>
> **THIS IS THE NUMBER THE DISSERTATION REPORTS.** Read live this publish from
> `docs/analysis/record_seed_completeness.py` (S15), which is the ONLY authority on it.
> **What is holding it right now: test -- baseline_volatility_scaled_return has 198 HOLE(S) below its frontier 406 -- that is what caps this line**

!! **THE TABLE BELOW IS NOT THAT NUMBER.** Its columns are RECORD COUNTS. A line can hold hundreds of
records and still bank 30, because an arm banks the largest rung whose WHOLE seed prefix it holds --
one missing seed at 99 pins the entire line. **Read the banked rung above; read the table for
progress.** (This heading used to say "the top row IS the reported result", and the top row is a
record count -- so the page named a count as the result and never printed the result at all.
Corrected 2026-08-09, after Tamer read `rung 100 ... REACHED` in the ETA panel and asked why the
rung-100 results were not in. He was right and the page was wrong.)

Under the registered rule (R101) every model climbs ONE ladder together and the result is the
**COMMON RUNG: the MINIMUM over every frozen arm of every line.** So work done by the deepest line
adds NOTHING to the headline until the shallowest catches up.

!! **THE TWO NUMBER COLUMNS ARE RECORD COUNTS, NOT REGISTERED RUNGS** (corrected 2026-08-03; the
header used to say "rung" and it was wrong). A count can OVERSTATE the rung an arm actually banks,
because an arm banks the largest rung whose WHOLE seed prefix it holds: `gpt-5.6-luna` held 567
records with a frontier at seed 567 and banked **189**, not 568, because seeds 192 and 193 were
missing. For the TRUE banked rung run `docs/analysis/record_seed_completeness.py` (S15).

| line | **fewest records on any arm** | most on any arm | frozen arms | note |
|---|---|---|---|---|
| test | **214** | 215 | 9 |  |
| glm_5_2 | **259** | 263 | 5 |  |
| nemotron_3_super | **264** | 265 | 5 |  |
| deepseek_v4_pro | **272** | 273 | 5 |  |
| kimi_k3 | **471** | 474 | 5 |  |
| qwen3_6_27b | **513** | 514 | 5 |  |
| test_h3_singleshot | **568** | 568 | 1 | COMPLETE |
| gemini_2_5_flash | **568** | 568 | 5 | COMPLETE |
| gpt_5_6_luna | **568** | 568 | 5 | COMPLETE |
| haiku_4_5 | **568** | 568 | 5 | COMPLETE |
| qwen3_5_9b | **568** | 568 | 5 | COMPLETE |
| sonnet_5 | **568** | 568 | 5 | COMPLETE |

A line reading **0** is MID-FILL, not stuck: its `distributional` and `scalar` arms are tested last,
behind the C1 barrier, so they sit at zero until their block runs. The check that would matter is a
line with zero jobs RUNNING **and** zero QUEUED, continuously for 45 minutes --
`docs/ops/line_balance.py` watches exactly that, and its live verdict is:

```
CLEAN -- every line below the deepest rung has work in flight or queued.
```

!! That line is now **read from the instrument on every publish**. It used to be the fixed sentence
"and currently reads CLEAN" hardcoded in this script, which would have kept telling you CLEAN with a
line genuinely stuck -- the same shape as the log-file counter P210 replaced. (Corrected 2026-08-03
after an auditor found it; the alarm also gained a 45-minute dwell requirement that day, because a
healthy line is legitimately job-less BETWEEN BATCHES for about 20 minutes.)

## Results so far

**No treatment outcome has been looked at, and none may be** -- the confirmatory analysis is
pre-registered to run ONCE, at the end, at whatever rung is reached. Every monitoring instrument is
effect-blind by construction.

What IS reported below is the **hand-written comparison canon (H1)** -- 11 human-designed rewards,
currently at **209 seeds each** (read live from the archive on this publish). !! THE
CANON IS NOT PINNED AT 30: amendment **R111** registered that it **CLIMBS THE SEED LADDER** with
everything else, so its depth is a LIVE quantity and `_TEST_UNITS_PER_RUNG = 71` carries all 11 in
the per-rung denominator. This line used to read "30 seeds each" as a flat design claim -- true as a
count while the core line sits in C1, but wrong as a statement of the design, and it would have gone
silently stale the moment that line enters C4.
**=> THE SHARPE TABLE BELOW WAS MEASURED AT 30 SEEDS.** It is hand-carried prose, not recomputed on
each publish, so once the number above moves past 30 the table is STALE until re-derived. These are
the BASELINES the LLM is measured against, not the experiment. (LLM-arm
sealed-test records also exist and are counted in the ladder above; their SCORES have not been read.)

| | Sharpe | note |
|---|---|---|
| return_minus_turnover | **+1.16** | the only positive one; it is the one that prices trading |
| the other ten | -0.17 to -0.39 | they rebalance 78-91 pct of the book EVERY day = ~22 pct/yr in costs |
| S&P 500 total return | +1.13 | cap-weighted, same 1571 sealed sessions |
| equal-weight universe | +1.17 | |
| EW-30, same assets | +1.28 | |

Across-seed sd is 0.25 against the 0.244 the seed ladder was powered on, so the plan's core
statistical assumption is confirmed by live data.

## Monitoring -- the cycle (last monitoring cycle 5 min ago)

Every cycle runs the six repo guards, the arm-coverage check the guards cannot do, the budget
projection, driver-log freshness, the drift check against the sha the live drivers were launched
from, and your instruction channel.

**Since 2026-07-31 it also checks the RESULTS, not just the processes** (your instruction). Every
cycle opens the archive: the fed block is re-derived from every LLM-arm prompt (a scalar-arm prompt
carrying a tail number would mean the manipulation had leaked), authored programs are checked for
duplication across arms, every reward's source hash is re-computed, and the scored-record invariants
(400,000 steps, the R115 execution floor, no impossible numbers) are re-tested. Four of those are
hard validity invariants and turn the cycle RED on any non-zero reading; the rest are reported with
their movement since the previous cycle. The `sci=` token on each line below is that verdict, and
`r115=` is the execution-floor breach count (`B` = a contaminated candidate currently tops its arm,
which is the floor doing its job). One line is written per cycle; the last six:

```
2026-08-11T04:03:52Z  OK  records=29428 (+1)  spend=$45.5019  guards=0n/2k  arms_full=10/10legs-ever  budget=2  stalest=3.4m  drift=0  sci=OK  r115=22B  sweep=51.9s(SWEEP-BOUND: >30s sleep)  auto-cycle
2026-08-11T04:05:23Z  OK  records=29428 (+0)  spend=$45.5019  guards=0n/2k  arms_full=10/10legs-ever  budget=2  stalest=2.4m  drift=0  sci=OK  r115=22B  cores=1104  sweep=60.1s(SWEEP-BOUND: >30s sleep)  auto-cycle
2026-08-11T04:06:47Z  OK  records=29430 (+2)  spend=$45.5019  guards=0n/2k  arms_full=10/10legs-ever  budget=2  stalest=2.7m  drift=0  sci=OK  r115=22B  sweep=54.5s(SWEEP-BOUND: >30s sleep)  auto-cycle
2026-08-11T04:08:09Z  OK  records=29432 (+2)  spend=$45.5019  guards=0n/2k  arms_full=10/10legs-ever  budget=2  stalest=2.2m  drift=0  sci=OK  r115=22B  sweep=51.3s(SWEEP-BOUND: >30s sleep)  auto-cycle
2026-08-11T04:09:31Z  OK  records=29435 (+3)  spend=$45.5019  guards=0n/2k  arms_full=10/10legs-ever  budget=2  stalest=3.0m  drift=0  sci=OK  r115=22B  sweep=52.0s(SWEEP-BOUND: >30s sleep)  auto-cycle
2026-08-11T04:29:57Z  OK  records=29463 (+28)  spend=$45.5019  guards=0n/2k  arms_full=10/10legs-ever  budget=2  stalest=2.6m  drift=0  sci=OK  r115=22B  sweep=1195.4s(SWEEP-BOUND: >30s sleep)  auto-cycle
```

Verdicts: OK nothing needs a human. ATTN something changed. RED a real problem, named on the line.
Acknowledged-and-understood alarms are deliberately kept quiet so a NEW one is loud -- the reasoning
for each is in docs/ops/acknowledged_alarms.txt.

## Budget -- reported, yours to act on

You said you watch the balance and will top up when needed, so this is a report, not a request. Live
figures this publish (spend is measured from the ledgers; "still to author" is projected at each
line's own observed cost per arm-generation; C4 needs no LLM calls, so authoring is the whole
remaining exposure):

```
  anthropic   spent $ 36.7418  + still to author $  0.0000  = $ 36.7418   credited $ 28.1500   margin $  -8.5918 (-31%)  over the credit ESTIMATE (owner-watched)
  openrouter  spent $  8.7603  + still to author $  0.0023  = $  8.7625   credited $ 19.3100   margin $ +10.5475 (+55%)  comfortable
```

The **credited** column is a ledger ESTIMATE carried from the 2026-07-28 console quote, not a balance
reading -- only your console knows the truth, which is exactly why this no longer raises an alarm.
The number to watch is **still to author** on `anthropic`: that is the confirmatory line's remaining
exposure. Detail: record section 49.

## Needs Tamer

* ~~`qdel` the eight dead jobs~~ **DONE 2026-08-03, on your ratification -- nothing needed from you.**
  All eight (6 `sshorig`, 2 `cpuprobe13`) deleted, rc=0. **And `qdel` was never actually blocked** --
  the brief had said so for three sessions and nobody had tested it. The proof they could never run
  turned out to be mechanical rather than circumstantial: they requested parallel environment
  `smp-[TBD]`, and `qconf -spl` has no such PE. Before 689 jobs / 1,480 slots, after 680 / 1,488,
  zero error or held throughout. Priced honestly: **no ETA gain** (we sit well under the 1,000-job
  cap); the value is crash-loop margin. Record section 126.1.
* **The R115 disclosure decision.** The frozen registration defends the 10% winner-eligibility floor
  as *"THRESHOLD-INSENSITIVE ... a 96x EMPTY GAP"*. **That gap has since FILLED**: at the tier where
  the rule acts, 15 of 60 (line, arm) groups now have a DIFFERENT eligible set across the band the
  registration calls identical, and one frozen winner IS the 9.08% candidate. **The VALUE is safe** --
  it was pre-committed before any campaign data existed and the rule never reads a performance number,
  so it is not a forking path. What is wrong is the JUSTIFICATION, and both files are inside the
  freeze hash, so it cannot be edited. **The choice is yours: a dated amendment row, or a stated
  Limitation. The threshold itself must NOT be changed** -- that would turn a presentational fix into
  a post-data forking path.
* **A12 -- the public OSF/Zenodo DOI deposit** (about 10 minutes; everything is staged in
  docs/A12_DEPOSIT_PACKAGE.md). A registered freeze-day obligation that is currently unmet.

## If something looks wrong

The campaign is independent of the Claude session: supervisors relaunch drivers, the watchdog revives
dead lines every 300 s, the sentinel watches health. **Stop lever:** create the file
`outputs\campaign_cluster_run4\STOP_CAMPAIGN` (or just ask via REMOTE_CONTROL.md).

Full narrative: [CAMPAIGN_EXECUTION_RECORD.md](CAMPAIGN_EXECUTION_RECORD.md), newest sections last.
