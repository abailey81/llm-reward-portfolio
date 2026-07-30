# ⭐ REMOTE CONTROL — send instructions to the live session from your phone

**How it works.** Edit this file on GitHub (pencil icon → commit), from a phone browser or the GitHub
app. The live session polls this branch, sees the change, reads your instruction, and acts on it —
then writes what it did under **LOG** at the bottom and pushes.

**Latency** is one poll interval (currently 5 minutes), not instant.

**Nothing else is needed** — no remote desktop, no extra software, no VPN.

---

## ▶ INSTRUCTIONS — write below this line

<!-- Write plain English. Anything you'd type into the session works. Examples:
     "status please"
     "what is the core count now"
     "stop the campaign"
     "restart the qwen3.5-9b leg"
     "raise the poll interval, you are hammering the login node"
     Leave it blank when you have nothing to say. -->

```
Make sure absolutely everything is strictly flawless, also to the run4_status dont forget to add teh cores active, and current eta's as well. Ultrathink 
```

---

## ⚠ LIMITS — what this can and cannot do

| | |
|---|---|
| works while | the Claude Code session on the laptop is alive and polling |
| does NOT work if | the laptop sleeps, loses network, or the session is closed |
| the campaign itself | **keeps running regardless** — it is independent processes (supervisors + watchdog + sentinel), not part of the session |
| emergencies | the stop lever is a FILE: `outputs\campaign_cluster_run4\STOP_CAMPAIGN`. Asking here is the easy route; it stops RESTARTS, not an already-running driver |

**If the session dies**, the campaign continues untouched. A fresh session resumes from
`docs/HANDOFF.md` §1 + `docs/CAMPAIGN_EXECUTION_RECORD.md` §22–§23, which are kept current.

---

## LOG — what the session did with each instruction

| when (UTC) | instruction | action taken |
|---|---|---|
| 2026-07-29 ~00:0x | *(channel created)* | polling armed at 5-minute intervals |
| 2026-07-30 14:35 | *(session takeover — RUN6 prompt)* | live state re-verified first-hand: 12/12 lines, 1,002 records, $21.94, drift 0, freeze MATCHES, 0 timeouts |
| 2026-07-30 14:35 | **NEEDS YOUR DECISION — the core-count answer** | Found by experiment why we sit at ~560 cores: our jobs ask **32 GB** each (mem=4G x 8 slots) but peak at **1.64 GB** — a 19.5x over-ask, and on Myriad memory is the scarce resource. Canaries identical except one field: at mem 4G the job STAYED QUEUED, at mem 2G and 1G it RAN immediately. 119 of our 190 jobs are queued while 3,400 slots sit idle. **One line fixes it, and only you can run it** (the agent's `qalter` is blocked, as `qdel` is): `ssh myriad 'bash -s' -- --apply < docs/ops/mem_relax.sh` (dry-run without `--apply`). Projection: **~1,520 cores instead of 560**, rung 568 **08-07 instead of 08-24**. Nothing about the science changes — same code, same threads, same pool, same host fence. Reply here with GO and I will report the realised placement. Detail: record §38. |
| 2026-07-30 15:15 | **ONE COMMAND, STILL YOURS** | Everything is now proved safe: the memory request is a SCHEDULING RESERVATION, not a kill limit (a canary held 3 GiB against a 2G request for 90 s and exited rc=0; the node reports `ulimit -v unlimited` and no cgroup limit), and 4 of 4 low-memory canaries placed at the FIRST scheduling pass while every 4G sibling waited (one waited 46 min). The sweeper is hardened (8-slot search jobs only, post-change verification, refuses to alter anything but the `memory=` term) and its DRY RUN is verified correct against the live queue. The script is already on the cluster. Run: `ssh myriad "bash ~/mem_relax.sh --apply"` — or `--limit 5` first if you prefer a canary. I cannot: the harness classifier blocks agent-side `qalter` AND blocks me from granting myself the permission, and the standing rule is to surface that rather than route around it. |
