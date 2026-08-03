# RUN 18 — SESSION PROMPT. **READ THIS BEFORE YOUR FIRST SUBSTANTIVE ACTION.**

Written 2026-08-03 ~16:30 UTC, at Tamer's instruction: *"I want to transition this session into a new
claude code session. Ultrathink very deeply and extensively, document absolutely everything, and write
a prompt that I will put into the new claude code session. Please make sure you include my very first
prompt inside as well."* and then, minutes later, after the laptop crashed and rebooted:
*"please stop, let the next session handle everything. Thats critical, make sure it has a
comprehensive knowledge."*

> **You run the live campaign on an irreplaceable MSc dissertation.** RUN 4 has been running since
> 2026-07-28 21:08 UTC. Real money is spent, the test data is sealed, **there is no re-run.** This
> supersedes `docs/RUN17_SESSION_PROMPT.md`; where they disagree, **this wins.**
>
> ⚠ **A SEPARATE SESSION OWNS THE WRITE-UP.** `paper/**`, `docs/GRADE_95_MASTER_PLAN.md`,
> `docs/V2_WRITE_TIME_REGISTRY.md` and `docs/CITATION_WORK_MAP.md` are **NOT YOURS.** It was LIVE at
> handover (lane id `8bee7914`) and is editing `CHANGELOG.md`, which is SHARED — **re-read CHANGELOG
> immediately before every edit to it.**
>
> ⚠ **THE LANE CLASSIFICATIONS ARE ABANDONED.** Do not register a lane, do not honour
> `docs/LANE_PROTOCOL.md`'s holds. (Reading the board with `lanebus.py --as ops board` STAMPS a
> heartbeat — it is not read-only. Avoid it.)

---

# §0 ⛔⛔⛔ THE REBOOT — READ THIS SECTION FIRST, BEFORE ANY OTHER ACTION

**THE LAPTOP CRASHED AND REBOOTED AT 2026-08-03 16:23:35Z.** Tamer's words: *"My laptop crashed and
got restarted. … If you do relaunches and etc, be very careful not to get the penalty as before."*

### §0.1 EXACTLY WHAT WAS MEASURED AT HANDOVER (16:25–16:30Z), all local, no ssh

```
boot                         2026-08-03 16:23:35Z   (17:23:35 local; local clock = UTC+1)
last monitoring cycle BEFORE 2026-08-03 16:11:20Z   -> ~12 min blind window across the crash
the boot task FIRED at       2026-08-03 16:25:48-51Z (~2 min after boot)
RAM free                     4,270 MB of 16,011 MB  (was 7,182 MB free before the crash)
```

**THE BOOT TASK RELAUNCHED ALL TWELVE LINES INSIDE ONE SECOND (16:25:49Z).** Twelve
`mode_d_supervisor` processes, all stamped 17:25:49 local, plus `mode_d_launch`.

### §0.2 ⚠⚠⚠ THIS IS THE STAMPEDE CONDITION THAT CAUSED THE UCL PENALTY

The 2026-08-03 **00:33:47Z** penalty (`penalty1`: CPU/memory capped at 80 % of 6 cores / 30 GB for
30 min) was diagnosed to **exactly this**: *all twelve lines resuming at once* after the VPN outage.
A reboot recovery is that event by construction. **Tamer named this risk explicitly.**

**⇒ YOUR VERY FIRST ACTION IS TO FIND OUT WHETHER WE ARE PENALISED RIGHT NOW.** I deliberately did
**not** ssh during the handover, so as not to add one more session to a possible stampede — that
check is yours, and it is one cheap command:

```bash
python docs/ops/loginnode_guard.py --once      # probes UNGATED via myriad13; OK / WARN / OVER
```

### §0.3 WHAT IS MISSING AFTER THE REBOOT — SIX COMPONENTS, AND ONE OF THEM IS THE PENALTY GUARD

Measured from a full `Win32_Process` dump at 16:28Z. `mode_d_launch.ps1` does **not** restore these:

```
crash_watchdog     ABSENT      loginnode_guard  ABSENT   <-- THE UCL-PENALTY EARLY WARNING
myriad_watch       ABSENT      line_balance     ABSENT   <-- the STUCK alarm
sentinel           ABSENT      campaign_backup  ABSENT
```

Relaunch commands (from a Git-Bash shell at the repo root). **STAGGER THEM — do not fire all at
once, and check `loginnode_guard` between each.** Start `loginnode_guard` FIRST so it is watching
while you start the rest:

```bash
nohup .venv/Scripts/python.exe -u docs/ops/loginnode_guard.py --interval-secs 120  --quiet >/dev/null 2>&1 &
nohup .venv/Scripts/python.exe -u docs/ops/crash_watchdog.py  --interval-secs 300  --quiet >/dev/null 2>&1 &
nohup .venv/Scripts/python.exe -u docs/ops/myriad_watch.py    --interval-secs 1200 --quiet >/dev/null 2>&1 &
nohup .venv/Scripts/python.exe -u docs/ops/line_balance.py    --watch 1800 > docs/ops/watch/LINE_BALANCE.log 2>&1 &
```

### §0.4 ⚠ AND THERE ARE DUPLICATE LOOPS — FIX BEFORE THEY CORRUPT THE LOGS

```
cycle_loop        5 processes   (should be 1)
publish_* .       6 processes   (should be ~2: the loop plus its child)
watchdog_fenced   2 processes   (should be 1)
```

**Why this matters, measured previously:** two concurrent cycle loops race on `CYCLE_LOG.md` and
produce a torn `sweep=1.23.4s` (§124.5), and `session_preflight` used to die on an unguarded
`float()` of it. Two publish loops race on `git commit`/`push`. **⛔ NEVER run two watchdogs** — they
fight to revive the same line (§115/D31).

⚠ **Kill them by PPID/creation time, and put the match pattern in a FILE, never on the command
line** — a `Win32_Process` filter MATCHES ITS OWN QUERY. I committed that error twice in one session
(P224, P229) and the second time `Stop-Process` killed its own shell. Use
`docs/ops/session_preflight.py` as the authority; when a hand-rolled count disagrees with it, yours
is wrong.

### §0.45 ⚠ THE MONITORING LOOP HAD NOT PRODUCED A SINGLE LINE 8 MINUTES AFTER RESTART

**Measured at 16:34:14Z: the last `CYCLE_LOG.md` line is still 16:11:20Z — 23 minutes old, and
~8 minutes after five `cycle_loop` processes were started at 16:25:51Z.**

Two readings, and **you must distinguish them before doing anything**:
* **BENIGN** — the sweep is SWEEP-BOUND and was measured at **333.8 s** on the last pre-crash cycle,
  so the first post-restart line is not due until roughly 16:31–16:33Z plus start-up. It may simply
  be mid-sweep, and five loops racing makes each one slower.
* **NOT BENIGN** — five concurrent loops are a known corruption source for this exact file (§124.5's
  torn `sweep=1.23.4s` two-writer race), and a loop that is wedged writes nothing at all.

**HOW TO TELL, cheaply and without ssh:** wait for one more minute and re-`tail`; if still nothing,
check whether the `cycle.py` child processes are alive and burning CPU (mid-sweep) or idle (wedged).
`session_preflight`'s `cycle_log` row computes its own adaptive dead-budget — **trust that row over
any hand-rolled judgement**, and note it will read `dead > ~900s` because the pre-crash sweeps were
long. **Reduce to ONE cycle loop either way.**

### §0.5 THE CAMPAIGN ITSELF WAS NEVER AT RISK, AND THIS IS THE REASSURING HALF

**Myriad jobs run on COMPUTE NODES, not on this laptop.** A reboot kills the local drivers and
supervisors; it does not touch a single queued or running array job, the remote Scratch archive, or
anything already pulled. The 12-minute blind window cost **monitoring**, not work. At 16:30Z only
`driver_core.log` had been re-written and only 2 of 24 drivers had spawned — **that is normal
staggered start-up, not a fault. Give it time before concluding anything.**

**⇒ THE RIGHT POSTURE: verify, then let it settle. Do NOT relaunch lines by hand.** The supervisors
are already up and will spawn their own drivers. The one thing to watch is the login-node penalty.

---

# §1 ★★★★★ TAMER'S STANDING BRIEF — VERBATIM. THIS IS THE OPERATING CONTRACT.

### §1.1 HIS VERY FIRST PROMPT OF RUN 17 (verbatim, unedited — he asks that this be carried forward every time)

> *"Read docs/RUN17_SESSION_PROMPT.md in full before your first substantive action — including the
> §0.5 mandatory reading and its nine gate questions. Then run §1's commands, say "Resuming from: …
> — next: …", and continue. Never ask "what now".*
>
> *You run the live campaign. A separate session owns the write-up — paper/** is not yours. The lane
> classifications are abandoned: don't register a lane or honour the lane-bus holds. If you detect
> another session live on the campaign, say so immediately.*
>
> *nemotron is the critical path — 4 of 5 arms frozen, and under R101 it pins the common rung for all
> twelve lines. Do not re-litigate the ETA; §5 closes it from SGE itself.*
>
> *very deeply and strictly monitor everything constantly and ensure absolutely everything is strictly
> absolutely flawless. I give you full permissions, full freedom, and I ratify the actions. Ultrathink
> very deeply and extensively before acting; work accurately and surgically; make no mistakes.
> Constantly check each record — every record individually must be strictly flawless, logical,
> meaningful. Study every file in this project very deeply, all processes, the whole thing going on on
> Myriad — don't miss anything. Take as much time and as many tokens as you need. Don't be lazy,
> always verify, and always be precise.*
>
> *very deeply and strictly monitor everything constantly and ensure absolutely everything is strictly
> absolitely flalwess 10000000% Ultarthink very deeply and extensivelly . pelase abbsolutely always
> monitor absolutely everything in this campaign very depely and strictly. I give you full pemrissions
> I give you full permission, and ratify the actions. I give you no permission to stop until
> absolutely everyhting is strictly absolutely 10000000% absolutely flawless Ultarthink veyry deeply
> and extneisvelly, I give you full permissiosn,a nd full freedom, do whatever it takes, ultaryhink
> very deeply and extenisvelly. Eveeyrhtinhg must be absolutely strictly absolutely 10000000%
> flawless. . I need you to ultrathink very deeply and very extenisvelly. Very deeply investigate
> everything, and speed up to an absolute maximum. please before act, make sure you evry deeply study
> this disserattion. Take as much time as you need, as many tokens as you nee . I give you no
> permission to stop until absolutely everything is strictly 10000000% absolutely stricrly flawless.
> make sure you also very deeplya dn extneisvelly constantly check each record, make sure veery record
> individually is vey stricrlt flawless, logical, meaningful. Take as much time as you need, dont be
> lazy, I give full ratifications, full freedom, full permissions. Please make sure you study every
> file in thsi project very deeply, all processes, the whole thing going on on myriad, absolutely
> everything, please dont miss anything. Ultarthink evry deeply adn extenisvelly, take as much time as
> you need, as many tokens as you need, this campaign run is extremely important, and it must be
> absoliutely flawless across absolutely all dimensions possible. Ultrathink very depely and
> extenisvelly . Dive extremnely deep, dont be lazy, check absolutely everyhting, check absolutely
> everything very deeply and extenisvelly, make sure you dont miss anything, and make sure you always
> verify, and you always very precise. also very deeply and strictly cehck fi this is correct and
> ensure fixed, also make sur eyou dive very deep if you find anything else. Ultrathink very deply and
> extenisvelly tale. Please work very accuratelly, anbd very surgically, make sure you make no
> mistakes. Ultrahink 100000 tiems befor edoing anything*
>
> *Plesae ultrathink very deeply and extenisvelly, dive very deep, and bring teh eta to global
> minimum. And also please make sur eyou dive very deep and check all records, individually, and check
> all processes, PLease make sur eyou dont miss anything, I dont want to have another unnoticed for 48
> hours crash. Ultrathink very deeply adn extenisvelly, taek as much time as you need. I give you full
> permissions and rights, and ratify your decisions. Please make sure absolutely everything is
> absolutely strictly flawless, tahts extremley important."*

### §1.2 HIS OTHER RUN-17 INSTRUCTIONS (verbatim, in order)

1. *"Ultratgink, i ratify you do it on my behalf"* — the ratification under which the eight junk jobs
   were `qdel`'d and the R115 disclosure decision was taken (§5, §6).
2. *"Just an addition to the plan after you finish and verify deeply, I think there might be a time
   outs issue, and some otehr issues. Please very deeply investigate, and ensure absolutely
   everything is 1000000% absolutely strictly flalwess"*
3. *"ok, if eta is perfect, focus on veryfying tahts absolutely everuthing is strictly flawles snow.
   Ultarthink"*
4. *"My laptop crashed and got restarted. Ultrathink very deeply and proceed. Make sure absolutely
   everyhting is absolutely strictly flawless 1000000%. If you do relaunches and etc, be very careful
   not to get the penalty as befor . Ultrathink very deeply and strictly, and verify absolutely
   everyhting. Be very carefull and accurate, check absolutely everyhting, make sure you dont miss
   anything"*
5. *"please stop, let the next session handle everything. Thats critical, make sure it has a
   comprehensive knwodlegde"*

### §1.3 THE THREE STANDING WORK ITEMS, IN HIS ORDER

> **(1) THE RECORDS — FIRST.** *"constantly check each record, make sure every record individually is
> very strictly flawless, logical, meaningful."* → **`bash docs/ops/run_record_layers.sh`** runs
> **EIGHT** layers plus **THREE** campaign measurements in one command. **Run it every session.**
> **(2) MONITOR EVERYTHING, CONSTANTLY AND DEEPLY.** Read the cycle log on the FIRST TOOL CALL OF
> EVERY BATCH. `drift=0` and `sci=OK` are the only two that must never change.
> **(3) THE ETA.** ⚠ **CLOSED TWICE. DO NOT RE-LITIGATE — §7 gives both closures.**

**HOW TO READ THIS.** Full permission raises the bar on the THINKING; it does not lower the bar on
verification. Every claim here was measured. Where a previous run was wrong, it says so.

---

# §2 ⛔ MANDATORY READING — DO NOT TAKE A SUBSTANTIVE ACTION UNTIL YOU HAVE READ THESE

Almost every error in §11 was committed by someone acting on an inherited summary instead of the
source. **Reading is cheaper than a mistake on data that cannot be re-created.**

| file | why |
|---|---|
| **this file** | the brief; §0 is the reboot, §7 the ETA, §11 the errors |
| **`CLAUDE.md`** | LAW. the ★ PRIORITIES, the four authorities, Okhrati's six duties |
| **`docs/HANDOFF.md`** §1–§3 | current state, standing orders, **the authority map (one owner per truth)** |
| **`memory/session-current-focus.md`** ▶ NOW | the live cursor (four RUN-17 entries at the top) |
| **`PREREGISTRATION.md`** | THE FROZEN CONTRACT. **Amendment E1 (~385-405)** is what makes §7 legitimate; **R101** defines the COMMON RUNG; **R115** is the open disclosure |
| **`docs/DEFERRED_FIXES_RUN4.md`** | every known-open defect **and the standing PROHIBITION** (never junction the archive) |
| **`docs/CAMPAIGN_EXECUTION_RECORD.md` §125–§130** | everything RUN 17 did, including §127.6 (a correction to its own §127.3) and §130.8 (an auditor's ten findings in my work) |
| **`CHANGELOG.md` `[2026-08-03c]` + `[2026-08-03d]`** | the same, narrative |
| **`docs/R115_DISCLOSURE_2026-08-03.md`** | the R115 decision, evidence and publication-ready prose |

### ⛔ THE READING GATE — ANSWER THESE FROM THE SOURCES BEFORE ACTING
1. What are the **four authorities**, and what happens when they conflict?
2. What is **H2**, and why is the fed tail **ENDOGENOUS** rather than an exogenous measurement?
3. What does rung **30** already bank, and why is **403** the registered PRIMARY target?
4. Why is **R115's registered justification false**, and why must the threshold NOT be changed?
5. What does `poll.py:305` rely on, and what happens if the archive is junctioned?
6. Why is `guards=2` **not** a live signal?
7. What is the **common rung**, and why does gemini's completed 568-seed ladder not raise the result?
8. **Why can an arm hold 567 perfect records and still bank rung 189?** (the S15 question)
9. Which paths are **drift-fenced**, and what does editing one cost?
10. Why must you **never** read a treatment arm's sealed-test outcome?

---

# §3 YOUR FIRST COMMANDS (post-reboot order)

```bash
cd /c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
python docs/ops/loginnode_guard.py --once        # ★ FIRST. Are we penalised after the stampede?
tail -3 docs/ops/watch/CYCLE_LOG.md              # has the loop resumed since 16:11:20Z?
python docs/ops/session_preflight.py --full      # 0 clear · 1 ATTENTION · 2 FAIL
python docs/ops/crash_watchdog.py --once
.venv/Scripts/python.exe docs/ops/line_balance.py --once
bash docs/ops/run_record_layers.sh               # ★ 8 layers + 3 measurements (Tamer's item 1)
ssh -o BatchMode=yes myriad "hostname"           # transport (goes through the SSH GATE)
```

Then say **"Resuming from: … — next: …"** and CONTINUE. **Never ask "what now".**

---

# §4 STATE AT HANDOVER (2026-08-03 16:30 UTC, T+139h)

```
records 9,386  ·  spend $45.4853  ·  drift 0  ·  sci OK  ·  freeze 3ca6f01ab772 MATCHES
repro 8 pass / 0 warn / 0 fail   ·  C: 43.0 GB free   ·  full suite PYTEST_RC=0
HEAD 6f9a4cbf (mine) then publisher status commits · 0 unpushed · backup-2026-08-03-run17 pushed
10/12 lines running before the crash · 2 COMPLETE · exogenous stop 2026-08-27
```

### THE LADDER — the campaign's real state
| line | banked rung (S15) | note |
|---|---|---|
| **gemini-2.5-flash** | **568** | **COMPLETE, zero holes** |
| **h3_singleshot** | **568** | **COMPLETE** |
| gpt-5.6-luna | **189** | ⚠ 2,832 records, frontier 567, **missing seeds 192/193** — see §8 |
| haiku · qwen3.6-27b · sonnet-5 · qwen3.5-9b | 30 | climbing |
| core · glm · kimi · nemotron | 30 / 0 | `distributional`+`scalar` tested last, behind the C1 barrier |
| deepseek-v4-pro | **0** | `placebo_shuffled` missing seeds 16–23 (one pack-8 job, in flight) |

---

# §5 ⚠⚠ THE ONE OPEN CAMPAIGN ITEM — nemotron IS STILL THE CRITICAL PATH

`test_leg_nemotron_3_super` has **4 of 5 arms frozen**. Its `scalar_cvar5` search reached
**g5 — the LAST generation of the registered K=5 × 6** — at 12:59:15Z, submitted as 5 arrays; **2
were gate-rejected** (`scalar_cvar5-g5-c2`, `-c4`, markers on disk, killswitch correctly classified
them as application exits), leaving 3. Per-generation wall-clock measured: **g3 25.30 h, g4 12.27 h**,
both QUEUE-dominated.

**When g5 returns, `scalar_cvar5` freezes, nemotron's fifth arm exists, and the line that pins the
COMMON RUNG for all twelve clears C2.** ⚠ **The reboot killed its driver; its supervisor was
relaunched at 16:25:49Z. VERIFY the g5 jobs are still on the cluster and that the driver re-attached
to them** — the jobs themselves are unaffected by the reboot.

⚠ A **D14 `ARM_CRASH_leg_nemotron_3_super.json` marker is on disk** (ts 2026-08-02 20:06:45Z, from
the resolved VPN outage). `cycle.py` reports it as ATTENTION because **every crashed arm has archived
a new record since the marker** — it clears only on a complete clean pass. **Do not treat the
marker's presence as a crash.**

---

# §6 ★★★★★ THE SESSION'S ONE LESSON — AND IT IS ABOUT THE INSTRUMENTS, NOT THE CAMPAIGN

RUN 16's lesson was *absent data silently becoming a definite verdict*. **RUN 17's is its sibling and
it is worse, because I committed it ten times in one session while writing the sections that name it:**

> ### AN INSTRUMENT THAT FAILS SILENTLY IN THE DIRECTION OF REASSURANCE.

A cleared streak · a NaN timestamp · a discarded stdout · a hardcoded "CLEAN" · an ignored `--root` ·
a tautological test · a regex that matched less than the `grep` it replaced. **Not one would have
shown up as an error. All of them would have shown up as GOOD NEWS.**

**THE RULES THIS EARNS — apply them to your own work first:**
1. **A measurement of the WRONG POPULATION is indistinguishable from a correct answer.** It does not
   even look like a bug. Always print the tier/scope beside the number.
2. **`x=$(cmd) || x=""` DISCARDS THE OUTPUT WHENEVER cmd EXITS NON-ZERO** — i.e. exactly when an
   instrument has something to say. Capture first, judge after. (Two live sites, both fixed.)
3. **A PARSER IS A CLAIM ABOUT A FORMAT.** Verify it against the real file. My replacement for a
   "naive grep" found **less** than the grep did, for half the fleet.
4. **A TEST THAT RE-IMPLEMENTS THE PREDICATE TESTS NOTHING.** Extract the production rule and call it
   from both. `(now - (now - x)) >= BOUND` is `x >= BOUND`.
5. **AN ALARM'S CLEAR-CONDITION IS ITS SAFETY PROPERTY.** Mine cleared on UNKNOWN, so one failed
   `qstat` suppressed it — and failed qstats are *correlated with* the fault it watches for.
6. **A SELFTEST MUST NOT WRITE TO PRODUCTION STATE.** Mine wiped the live alarm's memory.
7. **THE AUTHOR MUST NOT GRADE THEIR OWN WORK.** Four auditors ran across four sessions; **all four
   found more in my work than I did.** Send one at anything substantial before banking it.

---

# §7 ★★★★★ THE ETA — CLOSED TWICE. RE-READ, DO NOT RE-LITIGATE.

Full derivation: execution record **§117, §120–§123, §126.2, §129.1**.

**(a) THROUGHPUT IS FAIR-SHARE BOUND, PROVEN FROM SGE ITSELF.** `qalter -w p` on a real pending job
returns *"found possible assignment with 8 slots"*; `qquota` is EMPTY; hosts have 105–167 GB free;
**2,576 cores are placeable** — and our count stays pinned. That is functional fair-share by user
(`policy_hierarchy OSF`, `weight_tickets_functional 500000000` vs `share 10000`, 6+ users). Not ours
to change.

**(b) AND THE ONE LEVER THAT RE-OPENED IS MEASURABLY POINTLESS.** §121 had concluded `qalter -p` is
"permitted but INERT" — **that is WRONG; §126.2 measured the demoted job at `prior 1.81126` against
untouched siblings at `2.00640+`, i.e. it lands with a DELAY.** So the queue-reordering lever §117
priced at ~25 h was, in principle, live again. **Measured: there is nothing to reorder** — all core
and nemotron jobs were RUNNING at the top priority we hold (2.00746), and all 462 queued jobs were on
non-critical lines already below them. **Zero critical-path jobs queued.**

**EVERY OTHER LEVER, INDIVIDUALLY EXCLUDED BY MEASUREMENT:** `qdel` on running jobs destroys up to
15 h each · `qalter` on the PE is JSV-refused · priority elevation is operator-only · priority
demotion is prohibited AND one-way · pool widening +2–4 % · memory +0.7 % · pack 8→4 negative ·
stopping at 403 unnecessary (the cumulative-tier rule banks 568 free).

**AND THERE IS NO WASTE:** the 8.8 % gate-failure rate counts candidates rejected **before any
training is submitted**; every COMPLETED ladder has **zero holes**.

**⇒ ~6–7 days to the full ladder against ~24 remaining. THE DEADLINE BINDS NO RUNG.**

---

# §8 ★★ THE FINDING THAT WOULD HAVE COST THE RESULT — AND THE 8th RECORD LAYER

**An arm banks the largest registered rung whose WHOLE seed prefix it holds.** The reported result is
the COMMON RUNG, a **MINIMUM** over every arm of every line. **So one missing seed below the frontier
silently demotes an arm — and can cap the entire campaign.**

**IT HAPPENED, AND ALL SEVEN LAYERS WERE CLEAN THROUGHOUT.** `test_leg_gpt_5_6_luna` held **2,832
individually perfect records**, frontier at seed 567, missing exactly **192 and 193**. Bankable rung
**189, not 568**. `len(seeds)=566` and `max(seeds)=567` are both consistent with a complete ladder —
which is why nothing saw it. It surfaced only because the line was momentarily job-less.

**BUILT: `docs/analysis/record_seed_completeness.py` (S15)** — selftest 9/9; case H punches one hole
in a clean fixture and asserts the verdict FLIPS. **It found a third case on its first run**:
`deepseek/placebo_shuffled` missing seeds **16–23** — exactly one pack-8 job.

**⚠ S15 IS A MEASUREMENT, NOT AN ALARM.** During pipelined C4 a healthy line ALWAYS shows holes
(seeds land out of order). **The discriminator is whether work is in flight:**
```
hole + jobs running/queued          -> MID-FILL. Benign. Do nothing.
hole + ZERO running AND ZERO queued -> the actionable case  (check line_balance + the driver log)
```

### ⚠ TWO OPEN REPAIRS TO WATCH (both were in flight at handover; the reboot did not touch the jobs)
* **gpt-5.6-luna seeds 192/193** — the driver itself detected the hole 20 min after finishing a block
  and requeued exactly those 8 seeds as **round 2, job 83464**. **Verify it ran.** Until it does, gpt
  banks 189.
* **deepseek `placebo_shuffled` seeds 16–23** — job **72732**, 8 slots, was at **11.2 h of a 15.0 h
  `h_rt` wall** at 15:40Z. **Inside D19's band.** If it hit the wall the 8 records are lost and the
  driver must repair-round them. **Check; do not kill it.**

---

# §9 THE INSTRUMENTS — READ THE DOCSTRING BEFORE YOU TRUST THE OUTPUT

`bash docs/ops/run_record_layers.sh` runs **all of it in one command**:

```
EIGHT RECORD LAYERS (these GATE the exit code)
  R1-R9   record_validator.py            the record's CONTRACT
  P1-P4   record_provenance_seal.py      the record vs the FILES beside it
  S1-S10  record_science_audit.py        scientific soundness + the banked rung
  S11     fed_text_identification.py     is each arm FED what the design registers
  S12     reward_code_audit.py           authored code vs the LIVE sandbox gate
  S13     fed_value_coherence.py         fed VALUES coherent + pipeline exact
  S14     record_window_identity.py      same WINDOW, same device, arm agreement
  S15     record_seed_completeness.py    <- NEW: is the SET complete, and what rung is BANKED

THREE CAMPAIGN MEASUREMENTS (REPORTED, deliberately NOT gated)
  M1  authoring_reliability.py           the CORRECTED per-model reject table (D34)
  M2  r115_threshold_sensitivity.py      RC=1 BY DESIGN — the disclosed state, not a regression
  M3  record_seed_completeness.py        RC=1 during pipelined C4 is NORMAL
```

**Others:** `docs/ops/transport_health.py` (streak vs the fatal bound) · `docs/ops/line_balance.py`
(STUCK vs WAITING, 45-min dwell) · `docs/ops/status_stage.py` (the status page's stage + ladder).

⚠ **S10 reporting "common prefix 0 / banked rung 0" is a MID-FILL ARTEFACT, not a regression.**
⚠ **`guards=2` is PERMANENTLY RED and is NOT a live signal.** Both contributors are acknowledged in
`docs/ops/acknowledged_alarms.txt` with measurements and RE-TRIAGE TRIGGERS. `seed_alignment:CRITICAL`
is the R101 design, not damage.

---

# §10 STANDING RULES THAT MUST SURVIVE THIS HANDOVER

- **NEVER** add Claude/Anthropic attribution. `Co-Authored-By` is REVOKED. **Tamer is sole author.**
- **NEVER** `git clean -x`, `git add -A`/`-u`, or `git stash`. Stage **by name**.
- **NEVER** lower SGE priority (prohibited, one-way); never `qdel -u`. **Explicit ids only.**
- **NEVER** read a treatment arm's SEALED-TEST outcome. **NEVER** change a frozen threshold.
- **NEVER** edit `src|scripts|config|prompts` while live (drift-fenced; `drift` must stay 0).
  `docs/**` is safe. **`paper/**` belongs to the WRITE-UP SESSION.**
- **NEVER** put backticks/`$(…)` in a bash `-c` string, heredoc, **or a long `--flag "…"` argument**.
  ⚠ **This bit FOUR times across two sessions** (P226, P228). The rule is about ANY shell-quoted
  string, not just heredocs. **The countermeasure is mechanical: write to a FILE.**
- **NEVER** put a process-match pattern in the command that performs the match (P207, five
  occurrences). Patterns go in a file; the query excludes `$PID`.
- **⚠ CRLF:** this repo's files are CRLF. Use the Edit tool; append via Python preserving endings.
- **NEVER** trust a wrapper's exit code — read `PYTEST_RC` from the LOG, and **never read an exit
  code through `| tail`** (that reports `tail`'s status).
- **PowerShell console is cp1251:** a `★` or `⚠` inside a `print()` CRASHES. Printed output ASCII.
- **⚠ Editing a running loop is INERT** — bash parses `while…done` once; **Python parses at import**,
  so a `--watch` daemon keeps the old code until restarted.
- **⛔ NEVER JUNCTION THE ARCHIVE.** `poll.py:305` commits with `os.rename` ("same filesystem by
  construction"); cross-volume it raises and `:306` `rmtree`s the record — **silent data loss.**
- **END-OF-WORK, all four:** `python scripts/update_handoff.py` · a SHORT cursor ▶ NOW entry · a
  DETAILED CHANGELOG block even with no commits · push the backup branch.

### ★★★ THE DOCUMENTATION DUTY
Tamer's stated reason: ***"document absolutely everything as this would help me for the write up."***
`docs/CAMPAIGN_EXECUTION_RECORD.md` and `CHANGELOG.md` are the PRIMARY SOURCES CH4/CH6/CH7 are written
from **by the other session**. **PAST · PRESENT · FUTURE, every time. EVERY MISTAKE RECORDED,
INCLUDING YOUR OWN**, in the §20 P-number form (**RUN 17 ended at P229 — allocate P230 next**).
**Write it AS IT HAPPENS.**

---

# §11 WHAT RUN 17 DID, AND EVERY ERROR IT MADE

### §11.1 The four things that matter most
1. **D34** — the per-model authoring-reliability table (a NAMED deliverable) is computed by
   `campaign_guards.rejects_guard` from `_rejects/` markers, and **`_write_reject_marker` runs ON THE
   NODE while the author-side gate `continue`s DRIVER-side, so a marker for an author-side rejection
   is STRUCTURALLY IMPOSSIBLE** (97 of 272 failures). It also omits the CONFIRMATORY line entirely.
   The corrected per-slot table is in `docs/ops/authoring_reliability.py`. **No confirmatory result is
   affected** — `analyze_campaign` reads `failures.jsonl` (zero `_rejects` hits).
2. **D35** — `compute_accounting`'s `n_attempted` double-counts 17 re-authored slots and publishes
   `placebo = 33` against a **registered budget of 30**. Fix with D32 before the headline analysis.
3. **R115 DECIDED** — a **stated Limitation**, not an amendment, **threshold UNCHANGED**. The
   amendment route is mechanically unavailable (both files inside the freeze hash; ADR-058b/§90 is
   the precedent). Re-derived first-hand: **2 of 60 groups change WINNER inside the "empty" band, and
   one is `distributional` — an H2 TREATMENT arm.** ★ **The confirmatory core line is untouched** (10
   groups, 262 candidates, zero fallback). Prose ready in `docs/R115_DISCLOSURE_2026-08-03.md`.
   ⚠ **FINAL for 7 of 10 core groups, PROVISIONAL for 3 still writing — re-run before submission.**
4. **THE TRANSPORT LANE FINDING** — `core` and `nemotron` both hit **240/240** and DIED at **3.0 h**;
   **ten** other lines survived the same 7 h 24 m outage at 140–149/240. **The SEARCH lane dies at
   3.0 h (240 × 45 s); the TEST lane at 12.0 h (240 × 180 s).** One outage, one lane, a clean 2-of-12
   partition. That is **D24 quantified from two deaths**, and the risk is live whenever a line is in
   search.

### §11.2 Tamer's items — BOTH DONE on his ratification
* **`qdel`** the eight junk jobs: **DONE**, rc=0. **And `qdel` was never blocked** — three sessions
  inherited that claim untested. Proof they could never run: PE `smp-[TBD]` does not exist.
  **ETA gain zero** (we were far under the 1,000-job cap); the value is crash-loop margin.
* **The R115 disclosure**: **DECIDED** (above). **Still needs Tamer only if he wants a different
  route** — the default is the stated Limitation, and the write-up session has the prose.

### §11.3 MY OWN ERRORS — P221 … P229, plus ten auditor findings (§130.8)
**P221** a re-measured quantity re-arms its acknowledgement's trigger, and it went unevaluated ·
**P222** measured truncation from a sibling directory whose name is a PREFIX of the real root; caught
by the SCHEMA, not the value · **P223** joined two disjoint sets that both had SEVEN members ·
**P224** a `Win32_Process` census whose pattern list was on its own command line · **P225** then read
the corrected census as a duplicate-monitor alarm (it is `nohup → venv stub → base interpreter`) ·
**P226** unescaped backticks in an unquoted heredoc **published a page with four mangled sentences** ·
**P227** my instrument's docstring claimed `failures.jsonl` was "the COMPLETE failure record" (≥16
node-reject events exist only as markers) · **P228** backticks in a `--flag` argument silently deleted
a word from the handoff · **P229** repeated P207 and `Stop-Process` killed its own shell (blast radius
NIL, verified immediately).

**AND §130.8 — an auditor found SEVEN MAJOR/CRITICAL in my own work**, the worst being that my own
STUCK-dwell fix **cleared the streak whenever `qstat` failed**, so one ssh failure per hour suppressed
the alarm indefinitely — *correlated with the very fault it watches for*. All fixed, mutation-proven,
every instrument re-selftested (16 / 10 / 10 / 10 / 10 / 9) and ruff clean.

---

# §12 STILL-LIVE FINDINGS INHERITED — NOT SUPERSEDED

* **`metrics.train_curve.return` is 100 % NaN** on every record (SB3 `ep_rew_mean`). A disclosure —
  never build a convergence exhibit from it.
* **The reflection source is STICKY** (`src/llm/loop.py:728-729`) — a fed vector can come from ANY
  earlier generation.
* **The no-feedback fallback is BY DESIGN** (`loop.py:406-409`). Three records do this, **all in
  `qwen3_5_9b`** (verified first-hand).
* **DETERMINISM IS NOT EVIDENCED BY THIS ARCHIVE** — RUN 4 contains NO REPLICATES, so S4 compares
  nothing. Evidence it from the 30/30 bit-identical farm, never from here. (**P197.**)
* **Sealed-test fallback**: the only MATERIAL case is `test_leg_qwen3_5_9b` (137 records, worst
  9.08475 %). The core line's 9 `baseline_differential_*` records at 0.00025–0.00050 % are the
  documented DSR warm-up, **20,000× below the floor**, and are hand-written comparators R115 does not
  govern.
* **THE RENDER ORDER IS NOT THE LEVEL ORDER** — the prompt emits CVaR 5 %, 10 %, 25 %, **then** 1 %.
  **PARSE BY LABEL.**
* **e00a is UNREACHABLE; f00a offers 0 slots; the MEMORY lever was refused three times** (memory was
  never scarce — 160 G free/host). Do not re-litigate.
* **3 records sit in 2 stale `.pull_tmp` dirs — NO DATA LOSS**, md5-identical to their committed
  copies. Left in place; **never delete from the archive.**
* **Two 0-byte strays at the repo root** (`driver` and a file named `You` prefixed by two
  Private-Use-Area glyphs) — one paste accident at 2026-08-01 17:14:04, referenced nowhere, untracked
  so they cannot reach a deposit. Recorded, deliberately not deleted.
* **⚠ THE WRITE-UP SESSION'S WORK IS PARTLY UNTRACKED** — `paper/appendices/F_*`, `gen_F_*.py`, two
  new `paper/tables/*.md`, `docs/WRITEUP_SESSION_PROMPT_2026-08-03.md`. One permitted `git clean -fd`
  from gone. **NOT yours to commit — flag it to them.**
* **⚠ `docs/CITATION_WORK_MAP.md`** was untracked and is now committed unchanged (protecting it is not
  editing it; RUN 16 set the precedent with `GRADE_95_MASTER_PLAN.md`).
* **⚠ CHANGELOG has a DUPLICATE `[2026-08-03a]` label** — the write-up session's new block collides
  with RUN 15's. Flagged, deliberately not renumbered (their lane).
* **⚠ `campaign_summary.json` AT TEARDOWN — still the only UNRECOVERABLE item.**

---

# §13 HARNESS LIMITS — MEASURED, NOT ASSUMED

```
qdel <explicit ids>                  ✅ WORKS (measured 2026-08-03; three sessions said BLOCKED)
Stop-Process -Id <pid> -Force        WORKS      New-Item -ItemType Junction   WORKS
compact.exe                          WORKS      Dism.exe                      WORKS (elevated)
Set-ScheduledTask                    WORKS
qalter -p <negative>                 PERMITTED, DELAYED (not inert — §126.2), and ONE-WAY
qalter -l                            REFUSED SITE-WIDE (jsv_allowed_mod has no `l`)
taskkill /PID                        BLOCKED    HKLM registry write           BLOCKED
bash `kill <windows-pid>`            NO-OP (Git Bash has its own pid namespace)
```

**⇒ THE STANDING RULE: TEST THE SPECIFIC COMMAND. Three "BLOCKED" claims have now been disproved.**

---

# §14 AUDIT THIS SESSION'S WORK — the ten things to re-check

Per Tamer's standing instruction that each session audits the last: **(1)** the S15 layer's own
correctness, **(2)** the dwell fix's clear-condition, **(3)** the `transport_health` regexes against
the real logs, **(4)** both `||`-suppression fixes in `publish_status.sh`, **(5)** the corrected
`§127.6` table, **(6)** the R115 re-derivation's positive control (must read 56/56), **(7)** the
D34/D35 numbers, **(8)** the status page end-to-end, **(9)** the `run_record_layers.sh` M-section's
exit-code semantics, **(10)** everything in §0 about the reboot.

**Send a fresh read-only auditor. Four ran across four sessions and all four found more in the
author's work than the author did.**
