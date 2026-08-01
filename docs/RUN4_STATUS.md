# RUN 4 -- LIVE STATUS

**Auto-generated 2026-08-01 14:10 UTC -- T+89h01m.** Refreshed every 5 minutes by the live session and pushed to GitHub, so
it is readable from a phone. To send an instruction back, edit
[docs/REMOTE_CONTROL.md](REMOTE_CONTROL.md) -- the session polls it on the same interval and writes
back what it did.

## Health

| | |
|---|---|
| elapsed | **T+89h01m** (launched 2026-07-28 21:08 UTC; exogenous stop 2026-08-27) |
| lines up | **12 / 12**, all five arms submitted on **10 of the 10 leg lines** (h3ss is single-arm by design) |
| freshest driver log | **0 min** old (above ~30 would mean a line has stopped progressing) |
| records archived | **2472** |
| LLM calls / spend | 2868 / **$44.9676** |
| transport timeouts | **0** |
| guards | **RC=2**, not green: truncation  |

## Compute

| | |
|---|---|
| cluster jobs | **104** (103 running, 0 queued) |
| **cores computing** | **824** |

Per-rung ETAs from the registered model at the cores we actually hold:

```
 rung              @824 cores              @830 cores   binding
               makespan / ETA          makespan / ETA
   30            4.6 d  08-02            4.6 d  08-02   critical_chain
  100            4.6 d  08-02            4.6 d  08-02   critical_chain
  189            6.6 d  08-04            6.5 d  08-04   throughput
  279            9.3 d  08-07            9.3 d  08-07   throughput
  340           11.2 d  08-09           11.1 d  08-09   throughput
  403           13.1 d  08-11           13.0 d  08-10   throughput
  568           18.2 d  08-16           18.1 d  08-15   throughput
```

### Are we using the maximum Myriad can give us? Measured 2026-07-31 (record section 70)

**Yes, and the limit is our own experiment, not the cluster.** Checked at every layer:

* **Right now (search phase):** there is room on pool d for **303 more of our jobs**, and we only have
  about **100 waiting**. We are not being held back - we have nothing more to submit. During the search
  each arm must wait for all 5 of its candidates to finish before it can write the next 5, so the
  ceiling is the 6-round chain, not the hardware.
* **Memory and disk block ZERO hosts.** Both were fixed/checked; neither costs us anything now.
* **At the seed-ladder phase (where cores really matter):** we could place about **900 jobs (~7,200
  cores)**, and the timing model stops improving past **~4,600 cores** - so we will have about **1.6x
  more capacity than we can even use**.
* **We have already proved it:** we held **over 1,000 cores for ~14 hours straight, peaking at 1,664** -
  and that was while still carrying two problems that have since been fixed (a 19.5x oversized memory
  request, and a priority setting that put us below every other user). Both are gone, so the ladder
  should do better than that.
* **Everything else has been tried and measured:** more threads makes it SLOWER (and would break
  reproducibility), a wider pool buys 4% but reintroduces a hardware-mixing problem, and priority is
  already fixed and now above the cluster average.

**Bottom line: buying more hardware cannot make this finish sooner.** The remaining wait is the
experiment's own serial structure. The seed ladder is tiered (30 -> 189 -> ... -> 568) and the stop date
is fixed, so if capacity ever fell short we would simply report at a lower rung - a valid, pre-registered
result, never a failure.

## Stage -- we are in the SEARCH phase (the LLM writing and rewriting rewards)

Each line's LLM writes 5 reward programs, each is trained once and scored on validation data, the
results are fed back, and it writes 5 more. Six rounds. A line finishes when its SLOWEST arm does.
The seed ladder (30 up to 568 seeds, scored on the SEALED data) is the NEXT phase and has not started
-- that is the phase the experiment's answer comes from, and where thousands of cores get used.

| arm | furthest generation | candidates so far |
|---|---|---|
| distributional | g5 of 5 | 909 |
| scalar | g5 of 5 | 326 |
| placebo | g5 of 5 | 299 |
| scalar_cvar5 | g5 of 5 | 278 |
| placebo_shuffled | g5 of 5 | 268 |

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

## Monitoring -- the 30-second cycle (last monitoring cycle 0 min ago)

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
2026-08-01T14:06:29Z  RED  records=2472 (+0)  spend=$44.9675  guards=2  arms_full=10/10  budget=2  stalest=1.2m  drift=5  sci=OK  r115=17B  sweep=16.7s  auto-cycle
2026-08-01T14:07:16Z  RED  records=2472 (+0)  spend=$44.9675  guards=2  arms_full=10/10  budget=2  stalest=2.1m  drift=0  sci=OK  r115=17B  sweep=23.5s  auto-cycle
2026-08-01T14:08:10Z  RED  records=2472 (+0)  spend=$44.9675  guards=2  arms_full=10/10  budget=2  stalest=2.9m  drift=0  sci=OK  r115=17B  sweep=17.3s  auto-cycle
2026-08-01T14:08:57Z  RED  records=2472 (+0)  spend=$44.9675  guards=2  arms_full=10/10  budget=2  stalest=0.7m  drift=0  sci=OK  r115=17B  sweep=22.6s  auto-cycle
2026-08-01T14:09:50Z  RED  records=2472 (+0)  spend=$44.9675  guards=2  arms_full=10/10  budget=2  stalest=1.4m  drift=0  sci=OK  r115=17B  sweep=14.8s  auto-cycle
2026-08-01T14:10:35Z  RED  records=2472 (+0)  spend=$44.9675  guards=2  arms_full=10/10  budget=2  stalest=2.2m  drift=0  sci=OK  r115=17B  sweep=16.0s  auto-cycle
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
  anthropic   spent $ 36.5750  + still to author $  1.0388  = $ 37.6138   credited $ 28.1500   margin $  -9.4638 (-34%)  over the credit ESTIMATE (owner-watched)
  openrouter  spent $  8.3953  + still to author $  0.5646  = $  8.9599   credited $ 19.3100   margin $ +10.3501 (+54%)  comfortable
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
