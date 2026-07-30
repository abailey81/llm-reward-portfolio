# RUN 4 -- LIVE STATUS

**Auto-generated 2026-07-30 06:29 UTC -- T+33h20m.** Refreshed by the live session and
pushed to GitHub, so it is readable from a phone. To send an instruction back, edit
[docs/REMOTE_CONTROL.md](REMOTE_CONTROL.md).

| | |
|---|---|
| elapsed | **T+33h20m** (launched 2026-07-28 21:08 UTC) |
| lines up | **12 / 12** |
| cluster jobs | **174** (169 running) |
| **cores computing** | **1352** |
| records archived | **766** |
| LLM calls | 1031 |
| spend (ledger estimate) | **$16.0229** |
| transport timeouts | **0** |
| guards | **all green** |

## What to expect next

* first records land when the C0 canary's ~8 h trainings finish (**~05:08-07:08 UTC, 29 Jul**)
* the canary clearing is what releases the core line's Opus authoring -- core spend stays $0 until then
* exogenous stop **2026-08-27**

## If something looks wrong

The campaign is independent of the Claude session: supervisors relaunch, the watchdog revives dead
lines every 300 s, the sentinel watches health. **Stop lever:** create the file
`outputs\campaign_cluster_run4\STOP_CAMPAIGN` (or ask via REMOTE_CONTROL.md).

Full narrative: [CAMPAIGN_EXECUTION_RECORD.md](CAMPAIGN_EXECUTION_RECORD.md) section 22-section 23.
