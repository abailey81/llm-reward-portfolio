# MYRIAD MAINTENANCE — WEDNESDAY 2026-08-12, AT RISK ALL DAY FROM 08:00

**Confirmed by Tamer 2026-08-03: DELAYED from the usual second Tuesday (Aug 11) to WEDNESDAY AUG 12.**

---

## ★★★ OFFICIAL UCL NOTICE (relayed by Tamer, 2026-08-04) — THIS SUPERSEDES ANY INFERENCE BELOW

> *"The Network Modernisation outage to replace central UCL switches that was previously postponed
> has now been rescheduled for **Wednesday 12 August**. The outage is expected to be completed
> within that day, but **if anything goes wrong it may extend into Thursday 13 August**. We will be
> **draining jobs on Myriad so that they will only start if they can complete before the outage**,
> or else they will wait in the queue until it is over and they can be scheduled again. You do not
> need to take any action. **There will be no access to Myriad when the switches are being swapped
> out.**"*

**THREE THINGS THIS CHANGES, and one of them is material:**

1. ⚠⚠ **IT MAY RUN TWO DAYS, NOT ONE.** Everything below was written for a single at-risk day. Plan
   for **Wed 12 AND Thu 13 August**. Section 7's slack calculation still absorbs it (rung 403
   projected 08-09 against an 08-27 stop), but the alarm window doubles.
2. ✅ **THE DISPATCH CLIFF IS OFFICIAL, NOT OUR INFERENCE.** Effect **E4** below predicted UCL would
   refuse jobs whose `h_rt=15 h` would overrun the window. The notice confirms UCL is doing exactly
   that deliberately. **So expect our queue to stop dispatching roughly 15 h before the outage,
   i.e. from around 17:00 on Tue 11 August**, and expect `records=` to flatten well BEFORE the 12th.
   That flattening is CORRECT BEHAVIOUR and must not be diagnosed as a stall.
3. ✅ **"NO ACCESS" MEANS THE LOGIN-NODE PENALTY HAZARD IS OFF DURING THE WINDOW.** Section 2 names
   the UCL penalty as the one genuine hazard, on the reasoning that every driver relaunch
   sha256-verifies ~36.8 MB of remote gold on a SHARED login node. With no access at all, those ssh
   calls fail immediately and cheaply. **The hazard returns the moment access does** -- twelve lines
   resuming together is the stampede condition that earned the 2026-08-03 00:33:47Z penalty. The
   supervisors' 3620-3820 s stagger is what protects us; do NOT relaunch by hand.

**"You do not need to take any action" is UCL's advice about THEIR drain, and it is consistent with
our registered position of RIDE IT.** It does not remove the Aug-11 pre-window checks in section 3,
which exist to certify our own state, not theirs.


The cluster MOTD states the standing rule — *"The second Tuesday of every month is a maintenance day,
when Myriad should be considered at risk all day from 08:00"* — and `docs/CAMPAIGN_DAY_RUNBOOK` §8
recorded it as **Aug 11**. **THAT DATE IS NOW WRONG. The window is AUG 12.** Anyone reading the
runbook must apply this correction.

> **THE ONE-LINE POSITION: this is a PLANNED AT-RISK DAY, not an incident. Jobs may die and REQUEUE
> idempotently; no data is lost by design; the supervisors ride it.** The danger is not the outage —
> it is (a) mistaking the day's expected alarms for a real fault, and (b) a crash-loop hammering the
> shared login node into another UCL penalty.

---

## 1. WHAT WILL HAPPEN, AND IT IS ALL EXPECTED

| # | Effect | Why | Expected? |
|---|---|---|---|
| E1 | **Drivers die** after 240 consecutive pull failures | `max_consecutive_errors=240` × poll interval | YES |
| E2 | Supervisors relaunch each driver ~600 s later, which dies again | designed backoff | YES |
| E3 | Running jobs killed at node drain; up to 8 trainings per pack-8 job lost | maintenance drains nodes | YES — **repair rounds self-heal** |
| E4 | **A dispatch cliff BEFORE 08:00** — nothing new starts | SGE refuses jobs whose `h_rt=15 h` would overrun the window | YES, from ~17:00 on **Aug 11** |
| E5 | `sci`, `stalest`, `line_balance`, `transport_health` all go red | the cluster is unreachable | YES |
| E6 | `records=` flat all day | nothing is being produced | YES |

**THE MEASURED DEATH CLOCKS — memorise these two numbers:**

```
TEST   lane: 240 x 180 s = 12.0 h   <- where every line should be by Aug 12
  ⚠ A TWO-DAY OUTAGE EXCEEDS EVERY DEATH CLOCK. Drivers WILL die and supervisors WILL
  relaunch them into a dead cluster for the duration. That is E1/E2 and it is expected;
  no data is lost, because jobs requeue idempotently and the repair rounds self-heal.
SEARCH lane: 240 x  45 s =  3.0 h   <- fragile; core/nemotron died here in the 7h24m outage of Aug 3
```

⚠ **VERIFY BEFORE THE WINDOW that no line is still in the SEARCH lane.** On 2026-08-03 core's C1
chain (`tpe`, 6 candidates × ~7.24 h) was projected to finish ~Aug 5, so by Aug 12 every line
*should* be in the 12 h test lane. **Confirm it rather than assume it** — `line_balance.py --once`
plus `search_leg_*` rows in the funnel.

---

## 2. WHAT WOULD BE A **REAL** FAULT (the only things worth waking up for)

Everything in §1 is noise on the day. These are not:

* **The UCL login-node penalty fires** (`loginnode_guard` → `OVER`). This is the one live hazard:
  every driver relaunch sha256-verifies **~36.8 MB of remote gold on the SHARED login node** (P202),
  and 12 lines looping is precisely the pattern that earned the 2026-08-03 00:33:47Z penalty.
  **If the login nodes stay UP while the scheduler is down, this is a genuine risk.** Action: apply
  §4's STOP lever immediately.
* **`drift` != 0** — a fenced file changed. Nothing about maintenance should touch `src|scripts|config|prompts`.
* **The freeze hash stops matching.**
* **Disk falls under the 20 GB floor** (38.9 GB free / 18.9 GB headroom as of Aug 3).
* **The local machine reboots.** Windows Update is paused to **2026-09-10**, verified 2026-08-03, so
  this should not happen — but the boot task will recover it if it does.
* **After the window: a line that does NOT resume** within ~1 h of the cluster returning.

---

## 3. BEFORE THE WINDOW — run on **Aug 11**

```bash
cd /c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
python docs/ops/loginnode_guard.py --once           # baseline: must read OK
.venv/Scripts/python.exe docs/ops/line_balance.py --once   # confirm NO line in the search lane
bash docs/ops/run_record_layers.sh                  # the pre-outage certification
python docs/ops/session_preflight.py --full
git push origin HEAD:refs/heads/backup-2026-08-11-premaintenance
```

**AND CONFIRM THE OFF-MACHINE BACKUP IS CURRENT** — `campaign_backup` mirrors to
`D:\llm_rp_archive_mirror` (10,191 records, 0.1 h old on Aug 3). Preflight's `mirror` row must read
well under 1 h. **This is the only copy that survives a local disk event.**

**Record the pre-outage state** (records, spend, per-line depths) so the post-window comparison is
against a measurement rather than a memory.

---

## 4. THE STOP LEVER — Tamer's call, and here is the honest trade

**DEFAULT POSITION: RIDE IT.** `CAMPAIGN_DAY_RUNBOOK` §8 registered this as absorbed by design, and
the machinery has now proven itself twice in five days — a **7 h 24 m VPN outage** and a **full
laptop reboot**, both recovered without data loss.

**USE THE STOP LEVER IF** the login-node penalty fires, or pre-emptively if you want zero risk of it:

```bash
# QUIESCE (supervisors AND watchdog both exit cleanly on this file)
touch outputs/campaign_cluster_run4/STOP_CAMPAIGN

# RESUME (nothing auto-restarts -- this is the cost of stopping)
rm outputs/campaign_cluster_run4/STOP_CAMPAIGN
powershell -ExecutionPolicy Bypass -File scripts\mode_d_launch.ps1     # staggers 3620-3820 s, no stampede
```

| | RIDE IT | STOP IT |
|---|---|---|
| login-node penalty risk | **real** if login nodes stay up | **none** |
| auto-resumes when cluster returns | **yes** | **no — needs a human** |
| alarm noise | a full day of it | none |
| work lost | none beyond in-flight jobs | none beyond in-flight jobs |

⚠ **The decisive asymmetry: stopping costs nothing if someone is available to restart, and costs
MORE THAN A DAY if nobody is.** Only stop if a human will be at the keyboard when Myriad returns.

---

## 5. DURING THE WINDOW

**Check `loginnode_guard` and nothing else.** It is the only instrument whose verdict should change
your behaviour on the day:

```bash
python docs/ops/loginnode_guard.py --once
```

Everything else will be red and is supposed to be. **Do NOT relaunch lines by hand** — that is the
stampede condition, and it is what caused the 00:33:47Z penalty.

---

## 6. AFTER THE WINDOW — the recovery certification

```bash
python docs/ops/loginnode_guard.py --once                  # FIRST: are we penalised?
tail -5 docs/ops/watch/CYCLE_LOG.md                        # has the loop resumed?
.venv/Scripts/python.exe docs/ops/line_balance.py --once   # every line WAITING or running, none STUCK
timeout 600 .venv/Scripts/python.exe docs/analysis/record_seed_completeness.py   # S15: holes from killed jobs
bash docs/ops/run_record_layers.sh                         # full certification
python docs/ops/session_preflight.py --full
```

**⚠ S15 IS THE ONE THAT MATTERS MOST AFTERWARDS.** Jobs killed mid-pack leave **holes below an arm's
frontier**, and a single hole DEMOTES that arm's banked rung — the common rung is a MINIMUM, so one
hole can cap the entire campaign's reported result. The drivers detect and repair holes on their own
(proven twice: gpt job 83464, deepseek job 85065), so:

```
hole + jobs running/queued          -> MID-FILL, benign, do nothing
hole + ZERO running AND ZERO queued -> ACTIONABLE: check the driver log for a repair round
```

**Expect every line to have resumed within ~1 h of the cluster returning** (600 s supervisor backoff
plus the driver's own start-up). A line still absent after that is the one thing to chase.

---

## 7. WHY THE TIMELINE ABSORBS THIS

As measured 2026-08-03: rung **403** — the registered PRIMARY target — projects **08-08 to 08-18**
against the exogenous stop of **08-27**, i.e. **9 to 19 days of slack**. A lost day sits inside the
margin with room to spare. Under Amendment E1 the cumulative-tier rule also means truncation falls
back to the largest COMPLETED rung, so even a worse-than-expected outage degrades gracefully into a
valid pre-registered result rather than a failure.

**⇒ The correct posture on 2026-08-12 is patience, one instrument, and no hand relaunches.**
