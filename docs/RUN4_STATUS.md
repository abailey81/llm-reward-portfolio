# RUN 4 -- LIVE STATUS

**Auto-generated 2026-07-30 18:13 UTC -- T+45h04m.** Refreshed every 5 minutes by the live session and pushed to GitHub, so
it is readable from a phone. To send an instruction back, edit
[docs/REMOTE_CONTROL.md](REMOTE_CONTROL.md) -- the session polls it on the same interval and writes
back what it did.

## Health

| | |
|---|---|
| elapsed | **T+45h04m** (launched 2026-07-28 21:08 UTC; exogenous stop 2026-08-27) |
| lines up | **12 / 12**, with all five arms submitted on **10** lines |
| freshest driver log | **0 min** old (above ~30 would mean a line has stopped progressing) |
| records archived | **1060** |
| LLM calls / spend | 1566 / **$25.5625** |
| transport timeouts | **0** |
| guards | **RC=2**, not green: truncation  |

## Compute

| | |
|---|---|
| cluster jobs | **194** (76 running, 118 queued) |
| **cores computing** | **576** |

Per-rung ETAs from the registered model at the cores we actually hold:

```
 rung              @576 cores              @830 cores   binding
               makespan / ETA          makespan / ETA
   30            3.3 d  08-01            3.3 d  08-01   critical_chain
  100            5.5 d  08-03            3.8 d  08-01   throughput
  189            9.4 d  08-07            6.5 d  08-04   throughput
  279           13.4 d  08-11            9.3 d  08-07   throughput
  340           16.0 d  08-13           11.1 d  08-09   throughput
  403           18.8 d  08-16           13.0 d  08-10   throughput
  568           26.0 d  08-23           18.1 d  08-15   throughput
```

## Stage -- we are in the SEARCH phase (the LLM writing and rewriting rewards)

Each line's LLM writes 5 reward programs, each is trained once and scored on validation data, the
results are fed back, and it writes 5 more. Six rounds. A line finishes when its SLOWEST arm does.
The seed ladder (30 up to 568 seeds, scored on the SEALED data) is the NEXT phase and has not started
-- that is the phase the experiment's answer comes from, and where thousands of cores get used.

| arm | furthest generation | candidates so far |
|---|---|---|
| distributional | g5 of 5 | 213 |
| scalar | g5 of 5 | 188 |
| placebo | g3 of 5 | 89 |
| scalar_cvar5 | g3 of 5 | 97 |
| placebo_shuffled | g1 of 5 | 86 |

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

## Needs Tamer

* **A12 -- the public OSF/Zenodo DOI deposit** (about 10 minutes; everything is staged in
  docs/A12_DEPOSIT_PACKAGE.md). A registered freeze-day obligation that is currently unmet.

## If something looks wrong

The campaign is independent of the Claude session: supervisors relaunch drivers, the watchdog revives
dead lines every 300 s, the sentinel watches health. **Stop lever:** create the file
`outputs\campaign_cluster_run4\STOP_CAMPAIGN` (or just ask via REMOTE_CONTROL.md).

Full narrative: [CAMPAIGN_EXECUTION_RECORD.md](CAMPAIGN_EXECUTION_RECORD.md), newest sections last.
