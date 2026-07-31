# RUN 4 -- LIVE STATUS

**Auto-generated 2026-07-31 00:34 UTC -- T+51h25m.** Refreshed every 5 minutes by the live session and pushed to GitHub, so
it is readable from a phone. To send an instruction back, edit
[docs/REMOTE_CONTROL.md](REMOTE_CONTROL.md) -- the session polls it on the same interval and writes
back what it did.

## Health

| | |
|---|---|
| elapsed | **T+51h25m** (launched 2026-07-28 21:08 UTC; exogenous stop 2026-08-27) |
| lines up | **12 / 12**, all five arms submitted on **10 of the 10 leg lines** (h3ss is single-arm by design) |
| freshest driver log | **0 min** old (above ~30 would mean a line has stopped progressing) |
| records archived | **1172** |
| LLM calls / spend | 1681 / **$26.8418** |
| transport timeouts | **0** |
| guards | **RC=2**, not green: truncation  |

## Compute

| | |
|---|---|
| cluster jobs | **197** (94 running, 103 queued) |
| **cores computing** | **724** |

Per-rung ETAs from the registered model at the cores we actually hold:

```
 rung              @724 cores              @830 cores   binding
               makespan / ETA          makespan / ETA
   30            3.3 d  08-01            3.3 d  08-01   critical_chain
  100            4.4 d  08-02            3.8 d  08-01   throughput
  189            7.5 d  08-05            6.5 d  08-04   throughput
  279           10.6 d  08-08            9.3 d  08-07   throughput
  340           12.8 d  08-10           11.1 d  08-09   throughput
  403           15.0 d  08-12           13.0 d  08-10   throughput
  568           20.7 d  08-18           18.1 d  08-15   throughput
```

## Stage -- we are in the SEARCH phase (the LLM writing and rewriting rewards)

Each line's LLM writes 5 reward programs, each is trained once and scored on validation data, the
results are fed back, and it writes 5 more. Six rounds. A line finishes when its SLOWEST arm does.
The seed ladder (30 up to 568 seeds, scored on the SEALED data) is the NEXT phase and has not started
-- that is the phase the experiment's answer comes from, and where thousands of cores get used.

| arm | furthest generation | candidates so far |
|---|---|---|
| distributional | g5 of 5 | 259 |
| scalar | g5 of 5 | 230 |
| placebo | g3 of 5 | 97 |
| scalar_cvar5 | g3 of 5 | 102 |
| placebo_shuffled | g2 of 5 | 88 |

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

## Science watch -- written by the ANALYST session

Two Claude sessions run this campaign as one mechanism: **A** operates it (cluster, budget, docs,
git) and **B** audits what comes out of it (records, construct validity, results). The block below is
B's own words, pasted verbatim (analyst heartbeat 1 min ago). Their full transcript is
[docs/ops/bus/](ops/bus/) -- every decision the pair took, timestamped.

*(Analyst session B has not written a block yet. When B is live this is replaced every cycle and
appears verbatim on the public status page.)*

## Needs Tamer

* **!! ANTHROPIC BUDGET -- PROJECTED SHORTFALL ~$9.** Spent $22.15 of a credited $28.15; the
  authoring still to come (14 arm-generations on the core line, 15 on sonnet, 12 on haiku) projects
  **$15.11 more = $37.27 total**. If the key runs dry the CONFIRMATORY line stops, which is the one
  thing the campaign cannot absorb. **Please check the real console balance and top up.** Our figure is
  a ledger ESTIMATE, not a balance reading -- record section 49.
* **A12 -- the public OSF/Zenodo DOI deposit** (about 10 minutes; everything is staged in
  docs/A12_DEPOSIT_PACKAGE.md). A registered freeze-day obligation that is currently unmet.

## If something looks wrong

The campaign is independent of the Claude session: supervisors relaunch drivers, the watchdog revives
dead lines every 300 s, the sentinel watches health. **Stop lever:** create the file
`outputs\campaign_cluster_run4\STOP_CAMPAIGN` (or just ask via REMOTE_CONTROL.md).

Full narrative: [CAMPAIGN_EXECUTION_RECORD.md](CAMPAIGN_EXECUTION_RECORD.md), newest sections last.
