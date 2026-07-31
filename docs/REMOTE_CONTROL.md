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
| 2026-07-30 16:10 | ⚠ **CORRECTION TO MY OWN INSTRUCTION — DISREGARD THE TWO ROWS ABOVE** | **That command cannot work, and it is my error.** You gave permission, the harness allowed it, it ran, and all five `qalter` calls failed: *"rejected due to jsv_allowed_mod configuration which does not allow: l_hard"*. UCL forbids changing a queued job's resources **site-wide** — `qconf -sconf` gives `jsv_allowed_mod  ac,h,i,e,o,j,M,N,p,w`, with **no `l`**. The control proves only `-l` is forbidden: `qalter -N` on the same job returned rc=0. **Nothing is wrong with the diagnosis** — the 19.5× over-request, the eight-canary dispatch experiment, the absent enforcement and the 1,000-job × 16 TB arithmetic all stand — **only the delivery mechanism was wrong**, and the check that would have caught it was one line I did not run (`qconf -sconf \| grep jsv_allowed_mod`) before building tooling around the idea. **The fix now lives where it always should have:** `src/cluster/jobscript.py` renders `mem=1G` for the search lane and `mem=2G` for the packed lane, sized from the measured 1.64 GB per-training peak, with a test falsified against the pre-fix code. It reaches the cluster through a **driver relaunch**, which I am carrying out end-to-end: full suite → ruff → `freeze --check` (hash **UNMOVED**) → deploy → kill the twelve drivers so their own supervisors relaunch them with the new code. Nothing else changes. Record §45. |
| 2026-07-31 00:52 | *(session takeover — RUN 7)* | Live state re-verified FIRST-HAND before anything else: 12/12 lines, ALL ARMS FULL, freeze `3ca6f01a…` MATCHES, 0 transport timeouts, ~700–730 cores, drift = the same 2 analysis-layer files. Your standing entry (cores + ETAs on the status page) is implemented and still true. |
| 2026-07-31 01:15 | **"The budget is fine, cross it out, I will just top up whenever needed, I watch the balance. Just make sure you precisely monitor it as well."** | **Done — and it made the measurement BETTER, not weaker.** The budget no longer turns the cycle RED: it was comparing a projection we can measure against a credit we *cannot see* (`$28.15` is a 2026-07-28 console ESTIMATE, and you top up ad hoc), and a permanent RED that can never clear is exactly what trained the last session to ignore RED. It is now reported every cycle instead. **Precision raised where it counts:** the per-provider print went 2 dp → **4 dp**, because at 2 dp a single cycle's spend rounds to zero and the per-cycle delta was structurally blind — the first cycle after the change read `anthropic +$0.0992`. The status page's hand-typed "SHORTFALL ~$9 — please top up" bullet is replaced by a **generated** Budget section (it was still quoting `$15.11` of remaining authoring after the real figure had moved to `$13.47`). ⚠ I also found the credit constant itself is imprecise: it subtracts RUN 3's *whole* `$3.8136` from Anthropic, but RUN 3 predates the D10 fix so its OpenRouter legs are all mis-stamped `anthropic` — the true Anthropic portion is **`$3.1023`**. I did NOT "correct" it, because whether the `$31.96` quote predates RUN 3 is recorded nowhere and I will not swap a documented imprecision for an undocumented guess. **Tell me the real console number any time and I will set it exactly.** Record §53.2–53.3. |
| 2026-07-31 01:15 | **"check not only the processes … but also the RESULTS, they must be very logical, correct and meaningful"** | **Done — the 2-minute cycle now opens the archive, every cycle.** You named a real structural gap: checks 1–8 were *all process* (running / placing / spending / drifting), and every one can be green while the numbers inside are meaningless. I MEASURED both science tools first — `science_watch.py` **1.79 s**, `results_audit.py` **1.84 s** — so there is no case for sampling or "a few times a day": **both now run on every cycle**, taking the sweep from ~7 s to ~11 s. Fourteen quantities are extracted and diffed against the previous cycle. **Eight are hard validity invariants that turn the cycle RED**, each tied to the hypothesis it would destroy — a scalar-arm prompt carrying a tail number (H2's manipulation leaking), a program identical across two arms, a reward whose archived hash no longer matches its source, a non-finite metric, an out-of-range seed, an impossible score, a training that did not run the registered 400,000 steps, a broken PopArt invariant. The rest escalate on *movement*. **I falsified all of them before trusting any of them**: stubbed output proves the clean control stays silent and each failure fires exactly one correctly-worded alarm — a check that cannot fail verifies nothing. Extraction also **fails LOUD** if a tool's output format ever changes, because "absent" and "zero" are different facts. The verdict is now on every cycle line and on your status page as `sci=` and `r115=`, so "the results were monitored" is checkable rather than asserted. **First reading is clean:** 0 tail leaks over 1,196 records, 0 programs shared across arms, 0 hash mismatches, 0 non-finite metrics. Record §53.4–53.6. |
