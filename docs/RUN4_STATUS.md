# RUN 4 -- LIVE STATUS

**Auto-generated 2026-08-03 15:11 UTC -- T+138h02m.** Refreshed every 5 minutes by the live session and pushed to GitHub, so
it is readable from a phone. To send an instruction back, edit
[docs/REMOTE_CONTROL.md](REMOTE_CONTROL.md) -- the session polls it on the same interval and writes
back what it did.

## Health

| | |
|---|---|
| elapsed | **T+138h02m** (launched 2026-07-28 21:08 UTC; exogenous stop 2026-08-27) |
| lines up | **10 / 12 running; 2 COMPLETE (gemini-2.5-flash, h3)**, all five arms submitted on **10 of the 10 leg lines** (h3ss is single-arm by design) |
| stalest driver log | **2 min (qwen3_6-27b)** old (P218: the STALEST of the still-running lines, completed ladders excluded; above ~30 means that line has stopped progressing) |
| records archived | **9285** |
| LLM calls / spend | 2951 / **$45.4853** |
| transport health | **timeouts 6h=81; worst streak 3/240 (1.2% to fatal), ops on core** |
| transport timeouts (cumulative, ever) | 116 -- a level with no rate; read the row above |
| guards | **RC=2**, not green: truncation transport  |

## Compute

| | |
|---|---|
| cluster jobs | **662** (199 running, 463 queued) |
| **cores computing** | **1592** |

Per-rung ETAs from the registered model at the cores we actually hold:

```
 rung             @1592 cores              @830 cores   binding
               makespan / ETA          makespan / ETA
   30            4.6 d  08-02            4.6 d  08-02   critical_chain
  100            4.6 d  08-02            4.6 d  08-02   critical_chain
  189            4.6 d  08-02            6.5 d  08-04   throughput
  279            4.8 d  08-02            9.3 d  08-07   throughput
  340            5.8 d  08-03           11.1 d  08-09   throughput
  403            6.8 d  08-04           13.0 d  08-10   throughput
  568            9.4 d  08-07           18.1 d  08-15   throughput
```

### Are we using the maximum Myriad can give us? Re-derived from SGE itself, 2026-08-03 (record sections 120, 121, 122, 123)

**Yes, and the reason changed.** This block used to say the limit was our own experiment having
nothing more to submit. **That is no longer true and has been replaced with what was measured** -- we
now hold a deep backlog we cannot place, and the binding constraint is UCL's fair-share policy, which
is not ours to change.

* **The jobs ARE assignable and we still do not get the slots.** `qalter -w p` on a real pending job
  returns *"found possible assignment with 8 slots"*; `qquota -u ucestes` is EMPTY, so no quota caps
  us; every host has 105-167 GB free; **2,576 cores are placeable** -- and our core count stays
  pinned. That combination has exactly one explanation: **functional fair-share by user**
  (`policy_hierarchy OSF`, `weight_tickets_functional 500000000` against `share 10000`, 6+ active
  users). More users on the cluster means a smaller share each, and that is the whole story.
* **Every other lever has been individually EXCLUDED BY MEASUREMENT, not by argument.** `qdel` on our
  own running jobs would destroy up to 15 h of irreplaceable work each; `qalter` on the parallel
  environment is refused site-wide by the JSV; raising priority is operator-only; and **lowering our
  own priority is permitted but INERT** (`npprior` is 0.500 for every job on the cluster, so the
  weight cancels out) **and ONE-WAY** -- `qalter -p 0` is denied, so it cannot be undone. Widening the
  pool buys 2-4% and memory 0.7%, and both need a twelve-line relaunch of a live campaign.
* **And there is no waste to reclaim on the other side of the equation.** The 8.8% gate-failure rate
  counts candidates rejected BEFORE any training is submitted (one LLM call, not a 15 h training),
  and **zero trainings have been lost**: every completed ladder -- gemini's five arms and h3 -- has
  568 seeds with **ZERO holes**, as does every 30-seed line.
* **Memory and disk block ZERO hosts.** Memory was never scarce at all (160 GB free per host); the
  three separate investigations that "fixed" it were fixing a non-problem.

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
and two lines have already finished the whole thing.**

| arm | furthest generation | search candidates so far |
|---|---|---|
| distributional | g5 of 5 | 307 |
| scalar | g5 of 5 | 284 |
| placebo | g5 of 5 | 277 |
| scalar_cvar5 | g5 of 5 | 272 |
| placebo_shuffled | g5 of 5 | 280 |

### The seed ladder, live -- and the top row IS the reported result

Under the registered rule (R101) every model climbs ONE ladder together and the result is the
**COMMON RUNG: the MINIMUM over every frozen arm of every line.** So work done by the deepest line
adds NOTHING to the headline until the shallowest catches up, and the top row of this table is the
number the dissertation reports.

| line | **deepest rung ALL its arms have reached** | its best arm | frozen arms | note |
|---|---|---|---|---|
| test | **0** | 30 | 6 | 2 arm(s) still at zero |
| deepseek_v4_pro | **0** | 30 | 5 | 2 arm(s) still at zero |
| glm_5_2 | **0** | 30 | 5 | 2 arm(s) still at zero |
| kimi_k3 | **0** | 30 | 5 | 2 arm(s) still at zero |
| nemotron_3_super | **0** | 30 | 4 | 2 arm(s) still at zero |
| haiku_4_5 | **30** | 30 | 5 |  |
| qwen3_6_27b | **30** | 30 | 5 |  |
| sonnet_5 | **30** | 30 | 5 |  |
| qwen3_5_9b | **53** | 69 | 5 |  |
| gpt_5_6_luna | **566** | 567 | 5 |  |
| test_h3_singleshot | **568** | 568 | 1 | COMPLETE |
| gemini_2_5_flash | **568** | 568 | 5 | COMPLETE |

A line reading **0** is MID-FILL, not stuck: its `distributional` and `scalar` arms are tested last,
behind the C1 barrier, so they sit at zero until their block runs. The check that would matter is a
line with zero jobs RUNNING **and** zero QUEUED -- `docs/ops/line_balance.py` watches exactly that
and currently reads CLEAN.

## Results so far

**No treatment outcome has been looked at, and none may be** -- the confirmatory analysis is
pre-registered to run ONCE, at the end, at whatever rung is reached. Every monitoring instrument is
effect-blind by construction.

What IS reported below is the **hand-written comparison canon (H1)** -- 11 human-designed rewards,
30 seeds each. These are the BASELINES the LLM is measured against, not the experiment. (LLM-arm
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

## Monitoring -- the cycle (last monitoring cycle 3 min ago)

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
2026-08-03T14:43:55Z  RED  records=9257 (+2)  spend=$45.4852  guards=2  arms_full=10/10  budget=2  stalest=3.2m  drift=0  sci=OK  r115=21B  sweep=179.6s(SWEEP-BOUND: >30s sleep)  auto-cycle
2026-08-03T14:47:25Z  RED  records=9263 (+6)  spend=$45.4852  guards=2  arms_full=10/10  budget=2  stalest=6.6m  drift=0  sci=OK  r115=21B  sweep=174.8s(SWEEP-BOUND: >30s sleep)  auto-cycle
2026-08-03T14:50:50Z  RED  records=9274 (+11)  spend=$45.4852  guards=2  arms_full=10/10  budget=2  stalest=14.3m  drift=0  sci=OK  r115=21B  sweep=398.3s(SWEEP-BOUND: >30s sleep)  auto-cycle
2026-08-03T14:57:59Z  RED  records=9274 (+0)  spend=$45.4852  guards=2  arms_full=10/10  budget=2  stalest=17.3m  drift=0  sci=OK  r115=21B  sweep=162.7s(SWEEP-BOUND: >30s sleep)  auto-cycle
2026-08-03T15:01:12Z  RED  records=9277 (+3)  spend=$45.4852  guards=2  arms_full=10/10  budget=2  stalest=2.7m  drift=0  sci=OK  r115=21B  sweep=234.0s(SWEEP-BOUND: >30s sleep)  auto-cycle
2026-08-03T15:05:36Z  RED  records=9280 (+3)  spend=$45.4852  guards=2  arms_full=10/10  budget=2  stalest=2.8m  drift=0  sci=OK  r115=21B  sweep=248.0s(SWEEP-BOUND: >30s sleep)  auto-cycle
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
  openrouter  spent $  8.7435  + still to author $  0.0101  = $  8.7536   credited $ 19.3100   margin $ +10.5564 (+55%)  comfortable
```

The **credited** column is a ledger ESTIMATE carried from the 2026-07-28 console quote, not a balance
reading -- only your console knows the truth, which is exactly why this no longer raises an alarm.
The number to watch is **still to author** on `anthropic`: that is the confirmatory line's remaining
exposure. Detail: record section 49.

## Needs Tamer

* **`qdel 66103 66104 66105 66106 66107 66108 73026 73027`** -- eight dead jobs (6 `sshorig`, 2
  `cpuprobe13`) that sit at the very TOP of our pending queue (priority 2.00440 against every real
  job at 2.00430), each holding a scheduler RESERVATION, each demanding a host that is unavailable or
  refuses us. **None can ever run**, and they occupy 8 of our 1,000-job cap. `qdel` is blocked for
  the agent, so only you can clear them. Priced honestly: this buys **no ETA** while we are
  core-limited rather than job-limited -- it removes a crash-loop risk if we approach the cap again.
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
