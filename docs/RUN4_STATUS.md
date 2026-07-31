# RUN 4 -- LIVE STATUS

**Auto-generated 2026-07-31 16:44 UTC -- T+67h35m.** Refreshed every 5 minutes by the live session and pushed to GitHub, so
it is readable from a phone. To send an instruction back, edit
[docs/REMOTE_CONTROL.md](REMOTE_CONTROL.md) -- the session polls it on the same interval and writes
back what it did.

## Health

| | |
|---|---|
| elapsed | **T+67h35m** (launched 2026-07-28 21:08 UTC; exogenous stop 2026-08-27) |
| lines up | **12 / 12**, all five arms submitted on **10 of the 10 leg lines** (h3ss is single-arm by design) |
| freshest driver log | **0 min** old (above ~30 would mean a line has stopped progressing) |
| records archived | **1470** |
| LLM calls / spend | 2359 / **$37.4921** |
| transport timeouts | **0** |
| guards | **RC=2**, not green: truncation  |

## Compute

| | |
|---|---|
| cluster jobs | **187** (79 running, 108 queued) |
| **cores computing** | **632** |

Per-rung ETAs from the registered model at the cores we actually hold:

```
 rung              @632 cores              @830 cores   binding
               makespan / ETA          makespan / ETA
   30            3.3 d  08-01            3.3 d  08-01   critical_chain
  100            5.0 d  08-02            3.8 d  08-01   throughput
  189            8.6 d  08-06            6.5 d  08-04   throughput
  279           12.2 d  08-10            9.3 d  08-07   throughput
  340           14.6 d  08-12           11.1 d  08-09   throughput
  403           17.1 d  08-15           13.0 d  08-10   throughput
  568           23.7 d  08-21           18.1 d  08-15   throughput
```

## Stage -- we are in the SEARCH phase (the LLM writing and rewriting rewards)

Each line's LLM writes 5 reward programs, each is trained once and scored on validation data, the
results are fed back, and it writes 5 more. Six rounds. A line finishes when its SLOWEST arm does.
The seed ladder (30 up to 568 seeds, scored on the SEALED data) is the NEXT phase and has not started
-- that is the phase the experiment's answer comes from, and where thousands of cores get used.

| arm | furthest generation | candidates so far |
|---|---|---|
| distributional | g5 of 5 | 319 |
| scalar | g5 of 5 | 286 |
| placebo | g5 of 5 | 163 |
| scalar_cvar5 | g5 of 5 | 143 |
| placebo_shuffled | g5 of 5 | 137 |

## Results so far

Only the 11 hand-written comparison rewards have been scored on sealed data (30 seeds each). **The
LLM-written rewards have not been tested yet** -- that is the next phase, and it is the actual
experiment. No hypothesis has been looked at.

| | Sharpe | note |
|---|---|---|
| return_minus_turnover | **+1.16** | the only positive one; it is the one that prices trading |
| the other ten | -0.17 to -0.39 | they rebalance 78-91 pct of the book EVERY day = ~22 pct/yr in costs |
| S&P 500 total return | +1.13 | cap-weighted, same 1571 sealed sessions |
| equal-weight universe | +1.17 | |
| EW-30, same assets | +1.28 | |

Across-seed sd is 0.25 against the 0.244 the seed ladder was powered on, so the plan's core
statistical assumption is confirmed by live data.

## Monitoring -- the 2-minute cycle (last monitoring cycle 1 min ago)

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
2026-07-31T16:34:29Z  ATTN  records=1443 (+0)  spend=$37.4758  guards=2  arms_full=10/10  budget=2  stalest=1.2m  drift=0  sci=OK  r115=12B  auto-cycle
2026-07-31T16:34:45Z  ATTN  records=1443 (+0)  spend=$37.4758  guards=2  arms_full=10/10  budget=2  stalest=1.4m  drift=0  sci=OK  r115=12B
2026-07-31T16:36:44Z  ATTN  records=1443 (+0)  spend=$37.4758  guards=2  arms_full=10/10  budget=2  stalest=0.8m  drift=0  sci=OK  r115=12B  auto-cycle
2026-07-31T16:38:57Z  ATTN  records=1445 (+2)  spend=$37.4881  guards=2  arms_full=10/10  budget=2  stalest=2.6m  drift=0  sci=OK  r115=12B  auto-cycle
2026-07-31T16:41:09Z  ATTN  records=1445 (+0)  spend=$37.4921  guards=2  arms_full=10/10  budget=2  stalest=1.6m  drift=0  sci=OK  r115=12B  auto-cycle
2026-07-31T16:43:21Z  ATTN  records=1445 (+0)  spend=$37.4921  guards=2  arms_full=10/10  budget=2  stalest=0.8m  drift=0  sci=OK  r115=12B  cores=632  auto-cycle
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
  anthropic   spent $ 30.7136  + still to author $ 10.2575  = $ 40.9711   credited $ 28.1500   margin $ -12.8211 (-46%)  over the credit ESTIMATE (owner-watched)
  openrouter  spent $  6.7786  + still to author $  3.0768  = $  9.8554   credited $ 19.3100   margin $  +9.4546 (+49%)  comfortable
```

The **credited** column is a ledger ESTIMATE carried from the 2026-07-28 console quote, not a balance
reading -- only your console knows the truth, which is exactly why this no longer raises an alarm.
The number to watch is **still to author** on `anthropic`: that is the confirmatory line's remaining
exposure. Detail: record section 49.

## Needs Tamer

* **A12 -- the public OSF/Zenodo DOI deposit** (about 10 minutes; everything is staged in
  docs/A12_DEPOSIT_PACKAGE.md). A registered freeze-day obligation that is currently unmet.

## If something looks wrong

The campaign is independent of the Claude session: supervisors relaunch drivers, the watchdog revives
dead lines every 300 s, the sentinel watches health. **Stop lever:** create the file
`outputs\campaign_cluster_run4\STOP_CAMPAIGN` (or just ask via REMOTE_CONTROL.md).

Full narrative: [CAMPAIGN_EXECUTION_RECORD.md](CAMPAIGN_EXECUTION_RECORD.md), newest sections last.
