# RUN 23 — SESSION PROMPT. **READ THIS IN FULL BEFORE YOUR FIRST SUBSTANTIVE ACTION.**

Written 2026-08-05 ~07:25 UTC at Tamer's instruction: *"Ultrathink very deeply and extensively,
document absolutely everything from this session, and write a prompt for the next Claude Code
session, don't forget to also tell it to very deeply and extensively study absolutely all files in
this dissertation so it has the comprehensive knowledge, and zero gaps in knowledge. Also ultrathink
very deeply and extensively, and ensure extremely smooth transition. Make sure you include my
prompts on that everything should be flawless as well. Make sure in addition it also preserves these
loops, but dives much deeper, and checks more extensively, and checks very deeply absolutely
everything, from all dimensions and angles possible, it must not miss anything, and make sure it
ultrathinks, and minimises the ETA to an absolute minimum as well. And make sure absolutely
everything is very logical, meaningful, and absolutely flawless and 1000000% absolutely strictly
correct. Make sure in the prompt you also tell to maximise the cores and minimise the ETA."*

> **You run the live campaign on an irreplaceable MSc dissertation.** RUN 4 has been running since
> 2026-07-28 21:08 UTC — **T+178 h, elapsed 7.43 d**. Real money is spent, the test data is sealed,
> **there is no re-run.** This supersedes `docs/RUN22_SESSION_PROMPT.md`; where they disagree,
> **THIS WINS**, and §6 in particular REVERSES that file's headline recommendation on measurement.
>
> ⚠ **A SEPARATE SESSION OWNS THE WRITE-UP.** `paper/**`, `docs/GRADE_95_MASTER_PLAN.md`,
> `docs/V2_WRITE_TIME_REGISTRY.md`, `docs/CITATION_WORK_MAP.md` are **NOT YOURS.** `CHANGELOG.md` is
> **SHARED** — re-read it immediately before every edit, and never reuse a date label.
>
> ⚠ **THE LANE CLASSIFICATIONS ARE ABANDONED.** Do not register a lane. Reading the board with
> `lanebus.py` STAMPS a heartbeat — it is not read-only. Avoid it.

---

# §0 ★★★★★ TAMER'S STANDING BRIEF — VERBATIM. THIS IS THE OPERATING CONTRACT.

### §0.1 THE FLAWLESSNESS MANDATE

> *"very deeply and strictly monitor everything constantly and ensure absolutely everything is
> strictly absolutely flawless 10000000%. Ultrathink very deeply and extensively. I give you full
> permissions, full freedom, and I ratify the actions. **I give you no permission to stop until
> absolutely everything is strictly absolutely 10000000% absolutely flawless.** Do whatever it
> takes. Very deeply investigate everything, and speed up to an absolute maximum. Please before act,
> make sure you very deeply study this dissertation. Take as much time as you need, as many tokens
> as you need. Make sure you also very deeply and extensively constantly check each record, make
> sure every record individually is very strictly flawless, logical, meaningful. Don't be lazy, I
> give full ratifications, full freedom, full permissions. Please make sure you study every file in
> this project very deeply, all processes, the whole thing going on on Myriad, absolutely
> everything, please don't miss anything. This campaign run is extremely important, and it must be
> absolutely flawless across absolutely all dimensions possible. Dive extremely deep, don't be lazy,
> check absolutely everything very deeply and extensively, make sure you don't miss anything, and
> make sure you always verify, and you are always very precise. Please work very accurately, and
> very surgically, make sure you make no mistakes. Ultrathink 100000 times before doing anything."*

> ★ **2026-08-05:** *"ensure absolutely everything is 100000% correct everywhere without
> exceptions"* · *"make sure absolutely everything is very logical, meaningful, and absolutely
> flawless and 1000000% absolutely strictly correct"*

> ★ **On seeds:** *"we should not have flaws like for example missing seeds or something else."*
> **§4 answers this and the answer is still GOOD. Re-verify it every session; it is one command.**

### §0.2 ★★★★★ THE CORES + ETA DIRECTIVE — A STANDING PRIORITY, AND RUN 22 CHANGED THE ANSWER

> **Tamer, repeatedly:** *"make sure we also get the maximum cores possible, we fell very badly"* ·
> *"minimise the ETA to an absolute minimum, and use the absolute maximum Myriad can offer"* ·
> *"make sure in the prompt you also tell to maximise the cores and minimise the ETA."*

**THIS IS AN ACTIVE DUTY EVERY PASS.** But read §6 before you act on it, because **RUN 22 measured
the question properly for the first time and the previous session's starred recommendation is
REFUTED.** Rolling it would have driven a live campaign into a hard scheduler cap.

**The honest instruction: MEASURE, then act. Never re-argue a closed question — re-measure it — and
never act on a lever without re-reading the constraint that bounds it in the same breath.**

### §0.3 THE LOOP CONTRACT, VERBATIM

> *"Also every 30 min I want you to very closely check everything very deeply, check everything, all
> lines, all records, all outputs, all processes, absolutely everything, it all must be
> 1000000000% strictly absolutely flawless."*
> *"make sure if something is found, its always fixed, and ensure that absolutely everything is very
> strictly absolutely flawless"*
> *"make sure the checks that are every 30 minutes do not stop until they ensure absolutely
> everything is 10000% absolutely strictly flawless. I give them full permissions, do whatever it
> takes to ensure absolute flawlessness."*
> *"also dont forget to add the speed check component all the time, and its maximisation"*
> ⭐ *"make sure you very deeply and extensively study this whole project, have an extremely
> extensive knowledge and absolutely 0 gaps in knowledge."* — **DO THIS BEFORE ACTING. §2 is the
> reading list; it is not optional and it is not a formality.**

### §0.4 HOW TO READ THAT MANDATE — the most important paragraph in this file

**Full permission raises the bar on the THINKING; it does not lower the bar on VERIFICATION.**

**RUN 22 sent THREE auditors at its own same-day fixes. Every one came back with findings, and the
worst were mine:**

* I fixed a log-parsing blind spot and **installed a fail-open on the ERROR channel**: my "a record
  starts with a date" premise silently swallowed **554 records, all carrying a level token**, and a
  driver dying at start-up would have vanished from the census entirely. **My own comment beside it
  said "level counting is unaffected" and was empirically false.**
* I added a per-line reflection floor **that was anti-correlated with the science and sat ONE record
  from firing on the campaign's registered capability anchor.**
* I added a reject backstop and put it in the `else` branch, leaving **the single most
  collapse-prone leg with no reachable threshold at all** — it printed `ok` at 100% reject.
* I "fixed" a false alarm in `vanished_array_watch` and **uncovered a fail-open underneath it** that
  had been reporting an untested block as all-clear.
* **All four shipped with ZERO regression coverage**, against this repo's own rule, and the worst
  was three lines of test away from being caught.

> **⇒ SEND AN AUDITOR AT YOUR OWN FIXES BEFORE YOU BANK THEM — AND MAKE IT RUN THE ENTRY POINT, NOT
> THE HELPER. "Verify the artefact" means the thing a user invokes. AND WRITE THE TEST FIRST: every
> fix this session that had a test survived its audit; every fix that did not, did not.**

---

# §1 YOUR FIRST COMMANDS

```bash
cd /c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
date -u +%Y-%m-%dT%H:%M:%SZ                      # ★ FIRST. Never assume the clock.
python docs/ops/loginnode_guard.py --once
tail -5 docs/ops/watch/CYCLE_LOG.md
python docs/ops/session_preflight.py --full      # ~200 s; 0 clear · 1 ATTENTION · 2 FAIL
.venv/Scripts/python.exe docs/ops/remote_inbox.py --status   # ★ NEW — is Tamer waiting on you?
.venv/Scripts/python.exe docs/ops/line_balance.py --once
.venv/Scripts/python.exe docs/ops/arm_jobs.py
.venv/Scripts/python.exe docs/ops/occupancy_watch.py
.venv/Scripts/python.exe docs/analysis/record_seed_completeness.py
.venv/Scripts/python.exe docs/analysis/instrument_agreement.py --deep
.venv/Scripts/python.exe docs/analysis/science_plausibility.py
.venv/Scripts/python.exe docs/analysis/loader_collision_watch.py
.venv/Scripts/python.exe docs/ops/run4_watch.py outputs/campaign_cluster_run4 all
bash docs/ops/run_record_layers.sh
ssh -o BatchMode=yes myriad "hostname"
```

**⇒ RE-ARM THE 30-MIN LOOP IMMEDIATELY.** It is session-scoped and died with RUN 22. Harness cron at
`7,37 * * * *`, prompt = the STEP 0–6 contract in §11.

**⇒ AND CHECK THE INBOX FIRST.** `remote_inbox.py --status`. If it says PENDING, **Tamer is waiting
and has been since that timestamp.** Act on it, then `--ack` what you did. See §14.

Then say **"Resuming from: … — next: …"** and CONTINUE. **Never ask "what now".**

---

# §2 ⛔ MANDATORY READING — ZERO GAPS IN KNOWLEDGE IS A REQUIREMENT

| file | why |
|---|---|
| **this file** | the brief |
| **`docs/ops/watch/FLAWLESS_LEDGER.md`** | ⭐ **THE CONTRACT FOR THE LOOP.** Three terminal states · what is NOT a defect · the SPEED component · **the 2026-08-04 job-cap and fair-share measurements (§6)** · every OPEN row. **READ IN FULL BEFORE EVERY PASS.** |
| **`CLAUDE.md`** | LAW. the ★ PRIORITIES, the four authorities, Okhrati's D1–D6, Stefan's S1–S11, the 95+ doctrine, the human register |
| **`PREREGISTRATION.md`** | THE FROZEN CONTRACT. **R101** (read the amendment row IN FULL — point (4) licenses interim rungs as draft-filling), **R111**, **R115**, **Amendment E1** |
| **`docs/HANDOFF.md`** §1–§3 | current state + the authority map |
| **`CHANGELOG.md` `[2026-08-04i]`** | RUN 22 in full — five passes, twelve fixes, three auditor rounds |
| **`docs/DEFERRED_FIXES_RUN4.md`** | every known-open defect, D1–D72 |
| **`docs/analysis/EXCESS_AND_BENCHMARK_2026-08-04.md`** | ★ **THE BENCHMARK RESULT.** 0 of 59 cells beat a costed equal-weight 1/N on excess Sharpe; 25 of 59 have a shallower tail |
| **`docs/ops/MAINTENANCE_2026-08-12.md`** | ⚠ **UCL OFFICIAL — WED 12 AUG, MAY RUN INTO THU 13.** |
| **`docs/REMOTE_CONTROL.md`** | ★ **Tamer's inbound channel. IT WORKS NOW (§14). The LOG carries your predecessor's reply.** |
| **`memory/session-current-focus.md`** ▶ NOW | the live cursor |
| **the newest instruments** | `docs/ops/remote_inbox.py` · `docs/ops/occupancy_watch.py` · `docs/analysis/loader_collision_watch.py` · `docs/analysis/blind_quality_report.py` — read each docstring; **each exists because something was invisible** |

### ⛔ THE READING GATE — answer these FROM THE SOURCES before acting
1. What are the **four authorities**, and what happens when they conflict?
2. What is **H2**, and why is the fed tail **ENDOGENOUS**?
3. What is the **COMMON RUNG**, over exactly which units, and why is it **0** while FIVE lines hold 568?
4. Why must you NEVER read a treatment arm's sealed-test outcome for INFERENCE — **and what does
   R101 point (4) explicitly PERMIT?**
5. Which paths are **drift-fenced**, and what does editing one cost?
6. **What does `analyze_campaign.py` do today if you run it, and why must you NEVER "deduplicate the
   archive" to fix it?** (§5)
7. **Why is a Sharpe from this campaign meaningless without two other numbers beside it?** (§7)
8. **What actually limits our core count, and why is narrowing the pack the WRONG answer?** (§6)
9. **Which way does the driver log's clock run, and what did RUN 22 get wrong because of it?** (§13)

---

# §3 STATE AT HANDOVER (2026-08-05 07:25 UTC, T+178 h)

```
records 15,657 · test tier 14,146 over 69 of 71 units · spend $45.5019 · drift 0 · sci OK
board OK · 7 record layers RC=0 · line_balance CLEAN · occupancy proportionate on every line
slots 1,608 (SESSION HIGH) · 926 jobs · Eqw/hqw 0 · 19.0% of the cluster's 8,446 running slots
disk 38.5 GB · 6 lines have entered C4 · exogenous stop 2026-08-27 (21.7 d)
backup branch: backup-2026-08-04-run22 (pushed, current) · 0 unpushed
```

### THE LADDER — banked rungs (S15). **THE COMMON RUNG IS 0.**
| line | rung | what caps it |
|---|---:|---|
| **gemini-2.5-flash · gpt-5.6-luna · h3 · qwen3.5-9b · sonnet-5** | **568** | ⭐ **COMPLETE — qwen3.5-9b and sonnet-5 both finished overnight** |
| glm-5.2 · kimi-k3 | 30 | `distributional` holds 30 contiguous seeds; simply has not climbed |
| haiku-4.5 | 30 | `placebo_shuffled` 226 holes below frontier 408 — mid-sweep, 1,200 in flight |
| qwen3.6-27b | 30 | `placebo_shuffled` 350 holes below frontier 408 — mid-sweep, 344 in flight |
| **core · deepseek · nemotron** | **0** | the `h2_pair` every line tests LAST |

⭐⭐ **THE C1 BARRIER IS CLOSED.** At **2026-08-04 23:00:55Z** `c1_tpe_c29` reported
`batch complete … exhausted: []`, and `stage_eta` now reads **`critical-chain floor: 4.64 d total,
0.00 d still to run (every DFO arm has spent its full candidate budget)`**. Every ETA this ledger
printed for a week was clamped to that floor. **It is gone.** Core's remaining path is the two DFO
test legs, then its C2 `h2_pair` (`distributional` + `scalar`, both still at ZERO records), the C3
gate, and C4 — a sealed TEST at 9.39 h mean, not a 30-link chain.

⚠ **THE 12 h RATE HAS FALLEN TO 138.1 rec/h AND THAT IS EXPECTED, NOT A FAULT.** sonnet-5 and
qwen3.5-9b both COMPLETED, so their output is ageing out of the window; the leading contributor is
now haiku at **43%** (concentration has fallen 74 → 69 → 65 → 62 → 58 → 43 across six passes as the
laggards took over). **Check `line_balance` CLEAN and `occupancy_watch` before ever calling a rate
drop a fault.** 1 h reads 207 and 24 h reads 168.9.

---

# §4 ★★★ THE SEED QUESTION — TAMER ASKED DIRECTLY, AND THE ANSWER IS GOOD. KEEP IT THAT WAY.

**ZERO sealed-test seeds are permanently lost.** Re-verify EVERY session — it is one command:
```bash
ls outputs/campaign_cluster_run4/batches/*.permanent.jsonl | grep -icE "sweep|_test"   # must be 0
```
RUN 22 measured **90 permanent-retry ledgers, ZERO matching `sweep|_test`** — every one is a `_g<N>`
SEARCH generation. And the repair mechanism is proven end to end: `gpt-5.6-luna` was capped at rung
189 by exactly two missing seeds and the driver's own repair round filled them to 568.

⇒ **A HOLE IS TRANSIENT BY CONSTRUCTION.** The discriminator: *hole + jobs running/queued = mid-fill,
benign · hole + ZERO running AND ZERO queued = actionable.* haiku's 226 holes and qwen3.6-27b's 350
are the benign case today, with 1,200 and 344 units in flight respectively.

---

# §5 ⛔⛔ THE BIGGEST OPEN ITEM — `analyze_campaign.py` CANNOT RUN, AND THE OBVIOUS FIX IS A TRAP

**D49–D51, UNCHANGED.** The loader admits every `test_leg_*` line into one flat record list under
the SAME arm labels, and `_seed_scores` groups on `(arm, seed)` with no line term. **2,145 of 2,145
`distributional` and 2,137 of 2,137 `scalar` H2 test records are from LEG lines; core contributes
ZERO.** `loader_collision_watch.py` re-measures it in 4 s on every pass.

✔ **IT FAILS LOUD** — `_seed_scores` raises `ValueError` and `analyze()` guards only `AssertionError`.

⚠⚠ **THE TRAP: the guard's own message says "Deduplicate the run archive". FOLLOWING THAT ADVICE
CONVERTS THE LOUD FAILURE INTO A SILENT ONE.** ⛔ **DO NOT DEDUPLICATE THE ARCHIVE.** The repair is
prototyped at `docs/analysis/a79_fix_proof.py:60-84`; `scripts/**` is fenced, so it applies at
teardown, BEFORE `bank_gate`.

★ **AND RUN 22 ADDED A SECOND ITEM TO DO IN THE SAME EDIT (CRN-1).** `analyze_campaign._paired`
(`:1553-1557`) forms the headline paired contrast on the **seed number ALONE** — the file contains
**zero** references to `env_fp`, `env_fingerprint`, `device`, `threads` or `train_steps`. Exposure
today is **ZERO, measured**: 2,416 `(line, seed)` cells hold both H2 arms and **all 2,416 are
identical on window + device**, with all 2,416 vector lengths 1571. **Add the assertion when you
touch the file for D49**, so the analysis defends its own premise instead of inheriting it.

---

# §6 ★★★ THE CORES AND THE ETA — RUN 22 MEASURED IT PROPERLY AND **REFUTED** THE PREVIOUS ANSWER

**RUN 22's brief handed the session a starred, executable procedure to roll the campaign from
`--pack 8` to `--pack 4` for "+17% placeable cores". IT WAS NOT ROLLED, AND THAT WAS RIGHT.
Three independent measurements kill it. DO NOT RE-OPEN IT WITHOUT REFUTING ALL THREE.**

**(1) THE JOB CAP IS HARD AND WE ARE AGAINST IT.**
```
qconf -sconf global -> max_u_jobs  1000        qconf -ssconf -> maxujobs  1000
our live job count  -> 994 at the peak, 926 now
994 jobs x 8 slots  = 7,952 slots  ==  1,296 running + 6,656 queued   (exact)
```
At pack 4 the same work needs **~1,988 jobs — DOUBLE a hard cap** — and drivers submit whole tiers,
not a metered buffer. **It was already firing:** `glm-5_2` entered C4 at 22:24:35Z and had **six
`qsub` submissions rejected with exit status 25** minutes later. Benign and bounded (`driver.py`
treats it as a transport blip; fatal only after 240 consecutive failures at 180 s = 12 h, and the
counter resets on the first success while ~17 job-slots free per hour) — **but it proves the cap
binds.**

**(2) IT INVERTS THE RECOMMENDATION.** `src/cluster/lanes.py:290` already says
*"`maxujobs = 1000` at 8 cores/job structurally permits ~**8,000** cores"*. **At pack 4 that ceiling
HALVES to 4,000 — less than the work we are holding right now.**

**(3) WE CANNOT TAKE THE CORES WE ALREADY HAVE, SO RECOVERING MORE BUYS NOTHING.** Measured with a
15-sample, 42-minute, 4.2-scheduling-interval series:
```
running slots  1,144 -> 1,232   sd 28.3   full range 8.0% of the mean   =   +126 slots/h
queued  slots  2,800 -> 5,384                                          = +3,691 slots/h
placeable in smp-D at pack 8 .. 1,552 FREE   Eqw 0   qquota EMPTY
```
**We present work 29x faster than we are given it and our held total does not move.** That is fair
share. **`placeable_capacity` measures what the CLUSTER CAN ACCEPT and is silent on what FAIR SHARE
WILL GIVE US** — RUN 21 read the first as the second, and that is the whole error.

### ⭐ AND THE "WE FELL VERY BADLY" QUESTION IS ANSWERED, WITH A MECHANISM
Our share read 2,018 slots at 12:00Z and 1,232 at 22:00Z. Measured per user:
`cluster running 8,238 · ucbtjji 1,408 · **ucestes 1,232** · uctpec1 1,020`.
⇒ **WE DID NOT FALL THROUGH ANY MISCONFIGURATION. Other large users arrived and fair share
redistributed — the mechanism working as designed.** We were and are the **second-largest consumer
on Myriad**; at handover we hold **1,608 of 8,446 running slots = 19.0%**, with a deep queue ready to
take anything that frees.

### ⛔ CLOSED, AND DO NOT RE-OPEN WITHOUT A NEW MEASUREMENT
pack width (three refutations above) · `e00a`/`t00a` are outside `smp-D` and `t00a` is AMD, both
excluded by the determinism envelope · 15 blocked `d00a` hosts are UCL RC's · self-elevating fair
share is operator-only · lowering our priority is prohibited · 400k steps and thread count are FROZEN
· **an RC allocation request is NOT urgent** — at 1,184 cores rung 568 dates to ~13 August against a
27 August stop, and Tamer's standing "no RC request" holds.

### ⭐ WHAT IS ACTUALLY LEFT ON THE ETA
1. **THE TIER TAIL.** `driver.py:550-553` requeues a tier only when NO job of it is alive, so a
   tier's last few packs hold its whole remainder hostage. Measured: `qwen3_6-27b` held **1,927
   pending units behind EIGHT straggler jobs**. **Drift-fenced — a registered deferred fix, not a
   live patch.** `qdel`-ing a straggler to force the drain is a standing prohibition.
2. **THE ONE NUMBER THAT DECIDES THE LADDER**: the 24 h record rate over a window in which the five
   COMPLETE lines contribute nothing. Near the fleet rate ⇒ ~2 weeks of slack. Near 49 rec/h ⇒ the
   tail is costing the campaign. **Do not re-litigate cores until that number exists.**
3. **SATURATION IS ~3,235 CORES** (`lanes.py`, *"PUSH FOR IT: every core up to ~3,235 shortens the
   campaign"*). We hold 1,608. **Cores still help — we simply cannot buy more with pack width.**

---

# §7 ★★★ THE RESULTS — WHAT MAY AND MAY NOT BE SAID

⛔ **DISCLOSURE D-h IS BINDING: NO SHARPE FROM THIS CAMPAIGN MAY BE QUOTED WITHOUT BEING
EXCESS-OF-RISK-FREE AND WITHOUT THE EQUAL-WEIGHT BENCHMARK ON THE SAME LINE.**
The archived `metrics.test_sharpe` is **RAW**; subtracting the risk-free rate costs every cell
**0.14–0.27 units, median 0.21**. Against a costed equal-weight 1/N at **+1.0617 excess**: **0 of 59
model-arm cells beat it** (best +1.0173, median +0.8549) — while **25 of 59 have a SHALLOWER CVaR-5%
tail**. Full derivation: `docs/analysis/EXCESS_AND_BENCHMARK_2026-08-04.md`.

**The confirmatory H2 contrast still does not exist** — core holds ZERO records on both headline arms.

★ **AND A NEW WRITE-UP OBLIGATION FROM RUN 22 (P307).** `analysis_obligations.py` printed, as a
HARDCODED string, *"Across the five LLM arms it is symmetric at ~3pp spread, so H2 is unaffected."*
**Measured three independent ways and all three agree: SEARCH spread 6.8 pp, TEST spread 67.2 pp,
and on the sealed tier `distributional` 39.8% engaged against `scalar` 74.2% — 34.4 pp apart on the
two arms of the headline contrast.** The tool now computes it. ⚠ **Read it as a MEDIATOR, not a
confound**: only the reward program varies across arms and PopArt engages on that program's
magnitude, so the gap is a link in the fed → code → policy chain (SQ2), not a threat to
identification. **It must be REPORTED beside H2.**

---

# §8 STANDING RULES THAT MUST SURVIVE THIS HANDOVER

- **NEVER** read a treatment arm's SEALED-TEST outcome for INFERENCE. Know what R101 (4) permits.
- **NEVER** change a frozen threshold. **NEVER** make a check pass by weakening it.
- **NEVER** raise the 900 s sweep cap — it is what makes a genuinely dead loop visible.
- **NEVER** add Claude/Anthropic attribution. **Tamer is sole author.**
- **NEVER** `git clean -x`, `git add -A`/`-u`, or `git stash`. **Stage BY NAME.**
- **NEVER** leave files staged — an auto-committer runs every ~2 min.
- **NEVER** lower SGE priority; never `qdel -u`; never `qdel` a straggler to force a drain.
- **NEVER** edit `src|scripts|config|prompts` while live (drift-fenced). `docs/**` is safe.
- **NEVER** put backticks, `$(…)` or heredocs in a `bash -c` string or a `-m` commit message.
  ⛔ **AND NOT IN A `Bash` HEREDOC EITHER WHEN THE PAYLOAD CONTAINS AN f-STRING — RUN 22 BROKE THE
  SAME FILE TWICE THAT WAY.** Use `Edit`, or write the patch to a file and run the file.
- **⛔ NEVER JUNCTION THE ARCHIVE.**
- **PowerShell console is cp1251.** `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`.
  ⚠⚠ **AND THE SAME RULE APPLIES TO DECODING SUBPROCESS OUTPUT — this half was never written down
  and cost RUN 22 a live failure.** `subprocess.run(..., text=True)` decodes with the SYSTEM
  codepage; use `encoding="utf-8", errors="replace"` explicitly. A `git show` of a UTF-8 file died
  with `UnicodeDecodeError` inside subprocess's own reader THREAD, and the tool then reported
  "no fence in that copy" for a file whose fence was intact.
- **⚠ `.ps1` FILES ARE ASCII-ONLY** and must pass `Parser::ParseFile`. RUN 22 shipped one with 3
  non-ASCII bytes and caught it only by counting them.
- **⚠ Editing a running loop is INERT** — `cycle_loop.sh`/`publish_loop.sh` need a RESTART;
  `cycle.py`/`publish_status.sh` are re-invoked each iteration and do not.
- **END-OF-WORK, all four:** `scripts/update_handoff.py --suite-status "…"` · a SHORT cursor ▶ NOW
  entry · a DETAILED CHANGELOG block even with no commits · push the backup branch.

---

# §9 EVERYTHING RUN 22 FIXED — **allocate P313 next**

| id | what |
|---|---|
| **P305 + P305-b** | `vanished_array_watch` resolves blocks by job **NAME** from `qstat -xml`, because a restarted driver **ADOPTS** its jobs and never re-logs a submission — the log route is blind after every restart **by construction**. Then an auditor found the fail-open underneath: `qacct unreachable` and `unparsed ts` fell through to `exit 0` under *"no vanished arrays detected"*, with a live instance at **17.5 h**. Also: a failed `qstat` read as "nothing alive"; the new test hook could fire a real `qacct` ssh. **10/10 selftest, 4 mutants caught, 3 error paths proven by execution.** |
| **P306 + P306-b** | `occupancy_watch`'s `owed` was wrong on **four of nine lines**. Completed batches owed work forever (sonnet read 63 against 10 truly pending), and a **literal space** in the `PROGRESS` pattern hid **13.8% of all records** — `glm` read `owed=1` against **2,691**, `kimi` `2` against **2,692**. It had raised its own flagship alarm on a healthy line. **Module had NO test; now 3/3 with 4 mutants including an over-correction control.** |
| **P307** | `analysis_obligations` printed a hardcoded false reassurance about the H2 PopArt confound. Now computed. See §7. |
| **P308** | `campaign_watch` computed a guard failure and **left `rc` out of the alert expression**; the guards path was cwd-relative so a real CRITICAL and a missing file were indistinguishable; and `sups >= 0` suppressed the alarm on the probe's own "could not measure" value. |
| **P309 / P309-b / P309-c** | `run4_watch`'s D9 diagnostic **had matched nothing for the whole campaign** (0 of 173). Now prints `child_already_exited={'False': 164, 'True': 9}` — **and that answer is itself a finding: the ssh timeouts are cluster-side, not a local pipe-handle race.** Then the fix's own defects: the record-start premise swallowed 554 records; `timeout_events` was over-widened to 351 then corrected to the true 173; the pull path lost coverage and is now counted separately. |
| **P310 / P310-b** | `rejects_guard` could only fire on **4 of 10 legs**; the backstop then covered only the un-keyed ones, leaving `qwen3_5_9b` (112 of 193 reject markers) **with no reachable threshold** — it printed `ok` at 100% reject. |
| **P311 / P311-b** | `compute_ledger --report` printed a **headline dissertation number with no age**, from a snapshot **87.7 h old**. Now dated with a STALE banner. `_EXPECTED_PACK = 8` was wrong for a window that ran `--pack 4` for ~2.5 of its 3.4 days; only the meaningful floor is kept. |
| **P312** | ⭐⭐⭐ **THE REMOTE-CONTROL CHANNEL WAS A ONE-WAY PIPE FOR THE WHOLE CAMPAIGN.** See §14. |
| **CRN-1** | H2 pairing + CRN audited end to end; premise **HOLDS on all 2,416 pairable cells**. See §5. |
| **W6** | `budget_watch` timed out (`budget=99`, 3rd time in 5,195 cycles). Measured at **70 s against a 180 s cap** — a 2.6x margin on a probe that grows with the ledgers. |

---

# §10 ⚠ OPEN ITEMS

**BLOCKING:** D49–D51 + CRN-1 (§5), fenced, apply at teardown before `bank_gate`.
**HIGHEST OPS ITEM:** **SWEEP-1** — the three in-cycle full-archive layers are ~22.3 ms/record; the
900 s cap is crossed at **~30,000 records on a busy cycle, about 8 August**. **Make them INCREMENTAL
(`--since-state`, the pattern `record_provenance_seal` already proves). DO NOT RAISE THE CAP.**
**MAJOR:** A6 (h3 in the R101 population — a pre-registration question for Tamer + Okhrati) ·
E-sent (sentinel blind spots, fenced) · E-spend (`$45.50` is **$8.76 realized + $36.74 estimated**;
the dissertation must state the split) · E-wc (`wall_clock` 0 on the whole sealed tier; recover from
`ledger/*.epilogue.jsonl`) · W1 (`gate_failure_drift` CUSUM, structurally permanent, fenced) ·
**`scripts/campaign_guards.py` carries the same D9 wrapped-line defect and is FENCED.**
**MINOR:** ETA-1 · **W6** (§9) · the `reflection_guard`/`rejects_guard` fixes exist only in the
`docs/ops` copy; the fenced sibling is stale.
**DISCLOSURES D-a…D-i**, including **D-h** (no raw Sharpe) and **D-i** (`strategies.py` docstring
records 1.1656/1.1302; correct is 1.1659/1.1305 — a `ddof` mismatch, fix before the PDF).

---

# §11 ★★★★★ THE 30-MINUTE LOOP — PRESERVE IT, AND GO DEEPER

**Re-arm immediately** at `7,37 * * * *`, session-scoped.

**STEP 0 CLOCK** · **1 BOARD** (every tool in §1 — **including `remote_inbox.py --status`**; read
each tool's OWN verdict, never a pipe's exit code) · **2 DEEP DIVE** (§11.1) · **3 EVERY RECORD**
(seven layers + the science audit) · **4 SPEED** (§11.2) · **5 FIX** (falsify each fix against the
ENTRY POINT; **write the test FIRST**; send an auditor) · **6 RECORD**.

**Every finding is FIXED.** Three terminal states only: **FIXED** (falsified against pre-fix
behaviour), **PROVEN-BENIGN** (with the measurement), **ESCALATED** (with everything around it
fixed). **No row may age three passes.**

### §11.1 WHERE RUN 23 MUST GO DEEPER — these are STILL UNSTARTED
1. **`src/inference/**` coverage gap** — `ood_stress.py`, `reward_taxonomy.py`, `attribution.py`'s BH
   family at `:510`/`:655`, `information_gap.py`'s outer functions, `contamination.py`'s
   `named_vs_blinded_structural` / `cross_model_disagreement` / `contamination_report`,
   `es_backtest.dm_size_power_calibration`, `reward_code_distance.reward_code_structure_report`.
   **This is the largest untouched surface in the project.**
2. **SWEEP-1 IMPLEMENTATION** — the dated one. ~8 August.
3. **`scripts/analyze_campaign.py`'s remaining keys** — 39 registered outputs; D49–D72 cover the
   register, CRN-1 covers the pairing, the rest have never been read.
4. **The ops monitors RUN 22 audited but did not exhaust** — `stage_eta.py` (67 KB, ~470-line
   selftest unread), `transport_health.py`, `retriage_alarms.py`, `reject_taxonomy.py`,
   `publish_status.sh` (35 KB — ⚠ a running bash script).
5. **Extended `instrument_agreement` rows** — add the job census and the seed frontier;
   A5/A6/A6b/A7 are the pattern. **A7 must read zero before the cross-model synthesis at teardown.**
6. **⚠ SERIALISE YOUR OWN HEAVY SCANS AGAINST THE CYCLE.** See §13.

### §11.2 THE SPEED COMPONENT — every pass, an ACTIVE HUNT

**RECORD:** `rec/h (12 h and 24 h)` · `slots` · `running/queued` · `concentration` · `chain owed` ·
`ETA` · `days to Aug-27`. **Compare to the previous row.**

**⭐ AND ASK THESE FOUR EVERY PASS — Tamer's §0.2 directive made mechanical:**
1. **Are we holding every core we could hold?** `occupancy_watch` ratio per line. **If placeable
   exceeds what we hold AND our queue is empty, find out why before anything else.** If our queue is
   DEEP and we are still flat, that is fair share and there is nothing to fix — say so with the
   number rather than re-opening §6.
2. **Has anything become schedulable?** `Eqw`/`hqw` must be 0; `qquota` must be empty; and
   **re-read `max_u_jobs` and our live job count IN THE SAME BREATH** — the two are one constraint.
3. **Is any core on work that cannot raise the rung?** Concentration above the common rung is the
   design working — say so with the number, and watch it FALL as laggards take over.
4. **What ladder depth are we on track for by 27 August, and did it move?** That number IS the
   result. **If it has not moved in three passes, that is an OPEN FINDING.**

---

# §12 HARNESS LIMITS — MEASURED, NOT ASSUMED

```
qdel <explicit ids>              WORKS      Stop-Process -Id <pid> -Force   WORKS
qstat -u ucestes -xml            WORKS  <- REQUIRED for names/states; plain qstat TRUNCATES to 10 chars
qstat -f / qhost -F slots,...    WORKS      qconf -sconf global / -ssconf   WORKS  <- the job cap
git commit --only <path>         WORKS, and is REQUIRED wherever the tree is dirty
git pull --rebase                FAILS ALWAYS on this tree -- see §14
Start-Process (detached)         WORKS  <- the pattern for a loop that must outlive the session
qalter -p <negative>             PERMITTED but PROHIBITED by standing rule
taskkill /PID                    BLOCKED    HKLM registry write             BLOCKED
```
**⇒ TEST THE SPECIFIC COMMAND. Five "BLOCKED" claims have been disproved.**

---

# §13 ★★★ THE LESSONS RUN 22 PAID FOR — READ THESE BEFORE YOU TRUST YOUR OWN OUTPUT

1. **A SURPRISING RESULT IS A CLAIM ABOUT YOUR OWN SCRIPT FIRST.** RUN 22 hit this **six times**: a
   probe that read `sigma_max` from the wrong nesting and returned zero records; a CRN comparison
   that flagged **2,412 of 2,416 pairs** because the fingerprint's `label` embeds the arm name by
   design; a mutation runner whose regex could not match its own label; two test fixtures that could
   not move through the mechanism they were named for; and a launcher whose `-Stop` aborted before
   its restart.
2. **SEARCH THE RECORD BEFORE BELIEVING YOUR OWN SCRIPT.** After correcting the CRN probe, exactly
   ONE cell of 2,416 differed and I chased it as a real anomaly. **It is P137, a false-alarm class
   this repository had diagnosed on 2026-08-01 and written down TWICE** (`results_cycle.py:341`:
   *"`env_json_sha256` deliberately VARIES per record"*). The repo had already paid for that mistake
   and I paid again.
3. **THE DRIVER LOG IS IN HOST-LOCAL TIME (+0100), NOT UTC.** `vanished_array_watch.parse_ts` says so
   explicitly. RUN 22 read a local stamp as UTC and **dated a campaign milestone to the wrong day.**
   **Convert every driver-log time before writing it down.**
4. **YOUR OWN DEEP CHECKING IS LOAD ON THE BOX.** A **845.2 s sweep** (55 s from the cap that
   declares the monitoring loop DEAD) and a **`budget=99` timeout** both occurred in the window when
   this session ran whole-archive scans and a mutation suite concurrently, on a 16-core laptop
   already carrying **40 python processes**, 9 drivers, 9 supervisors and the cycle loop.
   **SERIALISE HEAVY SCANS AGAINST THE CYCLE.** Neither event was archive growth, and conflating
   them would have re-dated the SWEEP-1 deadline wrongly.
5. **A FIX WITHOUT A TEST DOES NOT SURVIVE ITS AUDIT.** Every RUN 22 fix that shipped with a
   falsifying test survived. Every fix that shipped without one was found defective within the hour.
6. **`git pull --rebase` IS NOT AVAILABLE ON THIS TREE.** It refuses on unstaged changes and this
   tree always has ~100. Anything that needs remote content must use `git fetch` + `git show`.

---

# §14 ★★★★★ THE REMOTE-CONTROL CHANNEL — IT WORKS NOW, AND TAMER RELIES ON IT

**Tamer, 2026-08-04: *"my issue was that I was typing it there, and you were not responding."***
He was right, and the cause was total. The whole inbound path was `publish_status.sh:34`:
```
git pull --rebase --quiet origin backup-2026-07-28 2>/dev/null || git pull --rebase --quiet 2>/dev/null || true
   -> error: cannot pull with rebase: You have unstaged changes.
```
**`git pull --rebase` refuses on a dirty tree; this tree is ALWAYS dirty** (102 modified paths at
diagnosis, from the churning watch logs). `2>/dev/null` hid it, `|| true` swallowed it. **`git push`
does not care about a dirty tree, so OUTBOUND worked perfectly throughout.** ⇒ **A ONE-WAY PIPE: he
could see everything and reach nobody.** Corroborated independently — that file has never carried a
single acknowledgement from an ops session.

**THE FIX: `docs/ops/remote_inbox.py`, polling every 60 s, LAUNCHED DETACHED so it outlives any
session** (`docs/ops/remote_inbox_launch.ps1`; running at handover, **pid 23768**).
- reads with **`git show origin/<branch>:docs/REMOTE_CONTROL.md`** — read-only, immune to tree
  dirtiness, cannot disturb a live campaign the way a rebase can
- ⚠ **deliberately NOT `git checkout`**, which would have destroyed **227 uncommitted lines** of
  cross-lane messages in that file; it rewrites ONLY the instruction fence
- checks **all** candidate branches, so "which branch was he on" stops being a failure mode
- **fails LOUD** — "could not read" is never rendered as "nothing new"

**YOUR DUTIES ON THIS CHANNEL, AND THEY ARE NOT OPTIONAL:**
1. **`remote_inbox.py --status` IS A STEP-1 BOARD ITEM.** If it reads PENDING, Tamer has been
   waiting since that timestamp.
2. **ACT on the instruction, then `--ack "what I actually did"`.** It writes a timestamped entry
   into the LOG and pushes it to both branches, so a reply appears where he typed.
3. **VERIFY THE LOOP IS ALIVE** each pass: `powershell -File docs\ops\remote_inbox_launch.ps1 -Status`.
   Restart it with the same script if not.
4. **Latency, stated honestly:** detection under a minute, action on the next deep pass — worst case
   about 30 minutes. Tell him if it will be longer.

---

# §15 THE ONE SENTENCE TO CARRY

**RUN 22 sent three auditors at its own same-day work and every one found more than the author did —
two fail-opens installed while closing someone else's, a guard that fired on the campaign's own
registered finding, and a backstop that left the most collapse-prone leg unguarded — while six
separate times a surprising result turned out to be a defect in the measuring script rather than in
the world. Write the test before the fix, run the entry point rather than the helper, convert every
driver-log timestamp before you write it down, search the record before you believe your own script,
serialise your heavy scans against the live cycle, and remember that the instrument is guilty before
the campaign is.**
