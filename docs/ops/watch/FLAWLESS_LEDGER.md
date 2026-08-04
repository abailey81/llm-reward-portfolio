# FLAWLESS LEDGER — the standing open-items register for the 30-minute deep check

**Tamer, 2026-08-04:** *"make sure the checks that are every 30 minutes do not stop until they ensure
absolutely everything is 10000% absolutely strictly flawless. I give them full permissions, do
whatever it takes to ensure absolute flawlessness."*

---

## THE CONTRACT — READ THIS BEFORE TOUCHING A ROW

**★★★ TAMER, 2026-08-04: *"make sure if something is found, it's ALWAYS FIXED, and ensure that
absolutely everything is very strictly absolutely flawless."*** So the contract is not "triage into
three buckets". It is:

> ## ⇒ EVERY FINDING IS **FIXED**. FIXING IS THE DEFAULT AND THE REQUIREMENT.
> **A pass does NOT end while a fixable row remains open.** Not "advance one row" — clear them.
> The other two states are NARROW, JUSTIFIED EXCEPTIONS, never a resting place and never a way to
> avoid work. If you can fix it, you fix it, this pass.

| state | when it is allowed | what it requires |
|---|---|---|
| **FIXED** | **ALWAYS, unless one of the two exceptions below is PROVEN to apply** | the defect is gone AND the fix was FALSIFIED — the new assertion must fail against the pre-fix behaviour. A passing test proves nothing on its own (RUN 18 reported a file "verified byte-identical" that had never been modified). |
| **PROVEN-BENIGN** | only when there is NOTHING to fix because the underlying state is correct | a MEASUREMENT with its command and output. ⚠ **AND IF AN INSTRUMENT MISLED US, THE INSTRUMENT IS STILL FIXED.** A false alarm is itself a defect. "The campaign was fine" never closes a row about a check that said otherwise — both halves get answered. |
| **ESCALATED** | only when the fix is *outside this session's authority* — UCL fair-share, a frozen pre-registered value, a Tamer decision | the precise reason it cannot be actioned, a specific ask for Tamer, **and every fixable thing AROUND it fixed anyway.** Escalating the un-actionable half never excuses leaving the actionable half. |

### NO ROW MAY AGE

A row that survives **three consecutive passes** without reaching a terminal state is itself a
finding: say so to Tamer by name, with what is blocking it. Silent aging is how an open defect
becomes a permanent one.

### "FLAWLESS" IS A CHECKABLE STATE, NOT A FEELING

The board is flawless when **every row in OPEN is empty**, every gate reads its green
(preflight 17/17, seven layers RC=0, drift 0, freeze MATCHES, repro 8/0/0, line_balance CLEAN), and
every remaining entry is either a permanent DISCLOSURE or an ESCALATED item carrying Tamer's name.
Anything else means the pass is not finished.

### ⛔ THE ONE RULE THAT OUTRANKS "MAKE IT GREEN"

**NEVER make a check pass by weakening the check.** No raised threshold, no widened tolerance, no
skipped assertion, no suppressed alarm, no `continue` past an error, no frozen value edited. On this
campaign the fastest route to a green board is to break the instrument, and that is the one outcome
worse than a red board. If a check is genuinely wrong, fix the CHECK and prove the fix falsifies —
then say so in the row. Fix causes, never symptoms.

### WHAT IS NOT A DEFECT, AND MUST NOT BE "FIXED"

A check that never stops needs to know where the floor is, or it will chase honest states forever.

* **The common rung being 0.** That is the campaign's true current state under R101, not a fault.
* **Holes below an arm's frontier while jobs are running or queued.** Normal during pipelined C4.
  Actionable ONLY on hole + ZERO running AND ZERO queued.
* **`RED` on the cycle line, `guards=2`, `seed_alignment:CRITICAL`, `silent_hang:UNKNOWN`, the
  truncation and transport entries.** Acknowledged in `docs/ops/acknowledged_alarms.txt`; each
  carries its own re-triage trigger. Re-read the trigger, do not re-litigate the alarm.
* **`M2_r115_threshold` exiting 1.** By design. The registered insensitivity claim IS falsified and
  that is the disclosed state; it cannot return to 0 without editing a frozen value, which is
  forbidden.
* **`M3_seed_completeness` exiting 1** while lines are climbing. Same reason.
* **Core count / fair share.** Closed by fourteen independent measurements. The only remaining lever
  is a human request to UCL RC, which is Tamer's decision. Do not re-open it.
* **Lines idle on the test tier with work queued.** Fair-share, not a fault. `line_balance` is the
  arbiter.
* **The 2026-08-12 Myriad maintenance.** A planned at-risk day with a playbook.

---

## ★★★ THE SPEED COMPONENT — MEASURED EVERY PASS, AND ACTIVELY MAXIMISED

**Tamer, standing priority (2026-07-24, re-stated 2026-08-04):** *"don't forget to add the speed
check component all the time, and its maximisation."* Under R101 the rung reached by the Aug-27
exogenous stop is set by THROUGHPUT, so throughput is the seed rung is the grade. Every pass
measures it, records it, and compares it to the previous pass.

### WHAT TO MEASURE EVERY PASS (append the row to the SPEED LOG below)

`rec/h (12 h and 24 h)` · `slots held` · `running / queued jobs` · `% of the rate from ONE line`
· `critical-chain remaining (tpe / bayes_opt candidates owed)` · `ETA to rung 30 / 403 / 568`
· `days to the Aug-27 stop`. Source: `docs/ops/stage_eta.py` plus a qstat census.

### A THROUGHPUT REGRESSION IS A FINDING, AND FINDINGS GET FIXED

If `rec/h` or `slots held` drops materially against the previous pass, that is an OPEN row and it is
worked to a cause, not noted. The live causes worth checking, in order of how often they have
actually bitten this campaign:

1. **Jobs holding slots without producing** — a driver crash-looping, a stalled chain, a hung pull.
2. **`Eqw` / `hqw` jobs** — zero is the expected count; any is a finding.
3. **Jobs unschedulable BY CONSTRUCTION** — RUN 17 found eight requesting a PE (`smp-[TBD]*`) that
   does not exist, holding queue slots forever. `qalter -w p` is the probe; `qconf -spl` is the truth.
4. **A line idle with NO work queued** — that is a genuine fault, unlike idle-with-work-queued.
5. **Drivers/supervisors below roster** (10/10 while 2 lines are COMPLETE).
6. **Disk approaching the floor**, which stops archiving before it stops training.
7. **Transport failures eating cycles** — each failing pull pays its own latency and walks the
   death clock (TEST 12.0 h, SEARCH 3.0 h, both LOWER bounds).

### ⛔ WHAT IS CLOSED, AND MUST NOT BE RE-LITIGATED EVERY THIRTY MINUTES

The cores question is **closed by fourteen independent measurements** (no quota, no job cap, no PE
cap, no memory constraint, no `snx` constraint, zero `Eqw`, one host group, jobs schedulable,
`qalter -p` up is operator-only, `js` refused). It is **functional fair-share by user, and nothing we
control changes it.** The only remaining lever is a human request to UCL RC, which is Tamer's call.
**Re-open it ONLY if a measurement changes** — a new `Eqw`, a quota appearing, a PE change. Do not
re-run the closed fourteen every pass; that burns the very wall-clock this section exists to protect.

Likewise closed: 400k steps is FROZEN, warm-start breaks determinism, more threads change FP
reduction order and corrupt H4 mid-chain, and re-packing needs a twelve-line teardown that costs
more than it saves. **Never trade correctness, CRN determinism or the frozen design for speed.**

### SPEED LOG (append one row per pass, newest last)

| when (UTC) | rec/h 12h | rec/h 24h | slots | run/queue | 1-line % | chain owed | rung 30 | rung 403 | rung 568 |
|---|---:|---:|---:|---|---:|---|---|---|---|
| 2026-08-04 00:10 | 153 | 195.8 | 1,632 | 204/314 | 82% (qwen3.5-9b) | tpe 5, bayes_opt 4 | 08-04 02:46 | 08-09 18:59 | 08-12 11:38 |
| 2026-08-04 00:50 | 150.2 | 191.0 | 1,600 | 200/288 | 90% (qwen3.5-9b) | tpe 5, bayes_opt 3, **cma_es DONE** | 08-04 23:01 | 08-09 23:48 | 08-12 18:37 |
| 2026-08-04 01:15 | 145.4 | 187.5 | **1,712** | 214/265 | 93% (qwen3.5-9b) | tpe 5, bayes_opt 3 | 08-04 23:25 | 08-10 02:44 | 08-12 22:52 |

---

## THE HARD PROHIBITIONS (a check with full permissions still may not do these)

* **NEVER read a treatment arm's SEALED-TEST outcome.** Single confirmatory look; reading it is a
  forking path on a frozen pre-registration.
* **NEVER edit `src/`, `scripts/`, `config/`, `prompts/` while the campaign is live** — drift-fenced,
  `drift` must stay 0. `docs/**` is safe. `paper/**` belongs to the write-up session.
* **NEVER change a frozen threshold or `PREREGISTRATION.md`.**
* **NEVER lower SGE priority** (prohibited, one-way); never `qdel -u`; explicit job ids only.
* **NEVER junction the archive** (`poll.py:305` renames; cross-volume it rmtrees the record).
* **NEVER `git clean -x`, `git add -A`/`-u`, or `git stash`.** Stage BY NAME.
* **NEVER put backticks, `$(...)` or heredocs in a `bash -c` string or a `-m` commit message.**
  Write to a FILE and use `-F`. Broken seven times; it is the single most repeated error here.
* **Printed output is ASCII-ONLY** (the console is cp1251 and the status page publisher REFUSES
  non-ASCII, so one bad character silently freezes Tamer's page).
* **NEVER add Claude/Anthropic attribution anywhere.** Tamer is sole author.
* **Editing a running loop is INERT** — `cycle_loop.sh` / `publish_loop.sh` need a RESTART;
  `cycle.py` / `publish_status.sh` are re-invoked each iteration and do not.

---

## OPEN — every row must move to a terminal state

Rows carry: `id · found · what · evidence needed · owner-action`. Work the **BLOCKING** rows first;
they are the ones that can cost the campaign or the grade. Add every new finding here the moment it
is found, including findings about this ledger.

### BLOCKING — can cost records, the result, or the grade

*(none open as of 2026-08-04 00:20 UTC — the two P244/P245 defects were FIXED and falsified this
session; see CHANGELOG `[2026-08-04b]` and execution record §132)*

### MAJOR — an instrument can mislead a future session

*(none open as of 2026-08-04 00:55 UTC — F1, F2, F3, F4, F5, F6 all cleared, every behaviour
change mutation-proven; see RESOLVED)*

### MINOR — correctness or hygiene, no campaign exposure

*(none open as of 2026-08-04 01:25 UTC — F14 cleared, see RESOLVED)*

### DISCLOSURES — true, permanent, and must reach the write-up rather than be "fixed"

| id | what |
|---|---|
| D-a | `metrics.train_curve.return` is 100% NaN on every test record (SB3 logs `ep_rew_mean`; no episode closes in the logging window). A disclosure, NEVER an exhibit. |
| D-b | A62: `per_period_pnl` is byte-identical to `test_returns` on 9,065/9,065 records. No consumer reads it; no result affected. |
| D-c | **S4 determinism is VACUOUS in this archive** — 0 replicate `(arm, seed, reward_hash)` keys exist, so "0 disagree" tests NOTHING. Determinism must be evidenced from the 30/30 bit-identical farm, never from here. |
| D-d | S5: the sealed test's worst safe-default fallback is 9.0847%, INSIDE the registered R115 10% floor with 0.9153% margin. The phenomenon the campaign measures, not a defect. |
| D-e | **R115 is a stated Limitation, threshold UNCHANGED, and is PROVISIONAL for 3 of 10 core groups — RE-RUN BEFORE SUBMISSION.** |
| D-f | D34: the authoring-reliability marker set structurally cannot hold an author-side reject. D35: `n_attempted` publishes `placebo = 33` against a registered budget of 30. |
| D-g | `campaign_summary.json` at teardown remains the only UNRECOVERABLE item. |

### WATCH — not yet a finding, but trending

| id | what | trigger |
|---|---|---|
| W1 | `gate_failure_drift` CUSUM rising (0.99 → 2.56) | investigate to a cause if it keeps climbing |
| W2 | anthropic spend 31% over the credit ESTIMATE, but `still to author $0.0000` | cannot halt anything; note only |
| W3 | disk forecast to the 20 GB floor | preflight `disk` row; full ladder fits with ~6 GB |
| W4 | repair jobs 83464 / 85065, ranked 309/314 and 314/314 of 314 pending | measured drain 9-18 h; escalate only if still queued after ~24 h |
| W5 | core line C1 chain: `tpe` owes 5 of 30, `bayes_opt` 4 of 30 | this gates the common rung leaving 0 |

---

## RESOLVED — append-only, never deleted

| id | resolved | state | evidence |
|---|---|---|---|
| P244 | 2026-08-04 RUN19 | **FIXED** | S15 took each line's rung as a minimum over STARTED arms, so core/glm/kimi/nemotron printed 30 while banking 0. New check C6 reads the roster from `frozen*/`. Selftest 9→16; the four new cases were run against a verbatim reconstruction of the pre-fix `scan()` and each reads TRUE after / **FALSE before**. Case M is a regression guard reading 30 on both sides. |
| P245 | 2026-08-04 RUN19 | **FIXED** | `stage_eta` priced the serial chain as elapsed wall-clock and printed "0.00 d still to run" while `bayes_opt` held 26/30 and `tpe` 25/30. Now measured from candidate RECORDS against `lanes.SERIAL_CHAIN_BUDGET`; unreadable tree returns UNKNOWN, never 0. Selftest 38→42, ruff clean, page rc=0 with 0 non-ASCII, live on the page. |
| A-1 | 2026-08-04 RUN19 | **PROVEN-BENIGN** | Apparent duplicate monitor/driver processes. Resolved by ANCESTRY: each `.venv` launcher is the PARENT of its base-interpreter child (`ParentProcessId` chains verified). A pattern census counts CHAINS, not instances. |
| A-2 | 2026-08-04 RUN19 | **PROVEN-BENIGN** | Repair jobs 83464/85065 feared stuck. `qalter -w p` → *"found possible assignment with 8 slots"*; real PE `smp-[D]*`, `reserve: y`. Ranked last because SGE priority is monotone in submit time (verified across the whole pending set). Measured drain 9-18 h. |
| A-3 | 2026-08-04 RUN19 | **PROVEN-BENIGN** | RUN 18 §10 alleged the `-1h` predicate `max(0, min(k, rung-(len-k)))` was untested and possibly wrong. It is CORRECT in all three regimes (`L<=R`, crossing, `L-k>=R`), and deleting the column IS caught by the J3 parser. A disclosed defect that was not one. |
| A-4 | 2026-08-04 RUN19 | **PROVEN-BENIGN** | Auditor reported as MAJOR that the ETA table is printing GATED for low rungs while dating higher ones. Refuted by running it: every row is dated, none GATED. The structural half survives as F1. |
| P246 | 2026-08-04 RUN19 | **FIXED** | Mine: a heredoc inside a `bash -c` string, seventh occurrence. Blast radius NIL. Both documents were then written with the Write tool and appended by a script doing no shell quoting. |
| **F14** | 2026-08-04 pass 3 | **FIXED** | The last inherited row, and it had survived THREE passes on a justification that did not survive checking. It was recorded as *"renaming variables inside live instruments is risk for no gain"* — but **all 12 of `record_validator.py`'s items are inside `_selftest()`, not the production validation path**, and the file has a `--selftest` that makes the change verifiable. The stated risk did not apply and the stated impossibility of verifying was false. All 18 cleared (E702 x14 by splitting statements, E741 x4 by renaming `l` to `ln`), across `record_validator.py`, `analysis_obligations.py`, `falsify_arm_coverage.py`, `json_standards_check.py`. ⚠ My own regex missed one f-string with a single-quoted inner literal and introduced an **F821 undefined name** — caught by re-running ruff rather than by reading the diff. **VERIFIED THE WAY RUN 18 ONLY CLAIMED TO:** selftest **ALL PASS**, all four files compile, ruff **fully clean**, and the live archive re-validated with the pre-edit output diffed line by line — **the only difference is the record count (10,846 -> 10,855, the archive grew by 9 in the interval) and the VERDICT is unchanged.** Not "byte-identical", which is impossible on a live archive; claiming that is precisely RUN 18's error. |
| **SPEED-2** | 2026-08-04 pass 3 | **PROVEN-BENIGN (and it looked like the opposite)** | Measured queue composition: **`leg8` (sonnet) holds 195 of 265 queued jobs = 74%**, submitted 08/03 02:41 which is the OLDEST and therefore the HIGHEST priority, while the five lines that actually CAP the common rung hold **17 jobs between them = 6%** (glm 8, core-C1 4, nemotron 4, deepseek 1), every one submitted later and therefore queued BEHIND all 195. That reads like the fleet starving the lines that matter. **It is not, and the reason is the part worth keeping:** the capping lines are blocked UPSTREAM at their C1/C2/C3 gates, not starved of slots -- they hold few queued jobs because they have not GENERATED more test work yet, and dispatching all 17 instantly would still leave the common rung at 0, because deepseek's repair only lifts `placebo_shuffled` while `distributional`/`scalar` hold no records at all. **A queue-position problem and a pipeline-stage problem look identical from the queue.** Consistent with s.6.2: the critical path is the serial C1 chain, not cores. No lever exists, and every mechanism that could create one is prohibited anyway (raising priority is operator-only, lowering ours is a standing prohibition and one-way, and killing reserved queued jobs forfeits the reservation). |
| **SPEED-1** | 2026-08-04 pass 3 | **PROVEN-BENIGN (measured, not assumed)** | The 12 h rate fell for a third pass running (153 -> 150.2 -> **145.4**) while slots ROSE (1,632 -> 1,600 -> **1,712**). Those point opposite ways, so it was worked to a cause. Per-10-minute arrivals over 2 h decline monotonically: 47, 42, 37, 32, 32, 29, 25, 22, 18, 13, 12, 13. Cause found in the per-line job split: **`leg8` (sonnet-5) now holds 145 running jobs, up from 92, with 82 dispatched in the last two hours, while `leg4` (qwen3.5) fell 106 -> 64.** A newly dispatched pack-8 job consumes slots for 8-15 h before its first record lands, so a LINE HANDOVER shows up as rising slots and a falling trailing rate. Corroborated: Eqw/hqw **0**, queue draining 314 -> 288 -> 265, `line_balance` CLEAN, drivers 10/10, disk fine. This is s.4(2) and s.4(5) of the brief and the composition caveat `stage_eta` already discloses. **Not a regression; the fleet is rebalancing onto a second producer.** |
| **P252** | 2026-08-04 pass 3 | **FIXED (estimate corrected)** | Mine: in pass 1 I priced the repair jobs' wait at **9-18 h** from "199 job starts in 11 h" = 18/h. That estimator is **biased low by construction** -- it counts start times of jobs STILL RUNNING, so every job that started AND FINISHED inside the window is invisible. Measured against queue DEPTH instead: 314 -> 265 in ~65 min = **~45/h net**, which puts ~264 jobs ahead of `85065` at **roughly 6 h, not 9-18**. Both estimators are biased in opposite directions (depth is net of new submissions), so the honest statement is hours, not days. **The same error family as P239: a rate whose numerator and denominator come from different populations.** |
| **P249b** | 2026-08-04 pass 3 | **FIXED** | The P249 census was still reporting `cycle_loop logical=2` every pass, and I was mentally discounting it -- which is exactly how a known-false alarm becomes permanent. Fixed rather than tolerated: a process now counts only if it names EXACTLY ONE known script (which excludes the boot task's shared `cmd.exe` launcher, the half of the lesson RUN 18 never recorded) and its parent does not also match (which excludes Git-bash and venv re-exec chains, the half it did). All six roster rows now read `ok` and agree with preflight's own `processes` row. |
| **P251** | 2026-08-04 pass 2 | **FIXED + FALSIFIED** | **AN AUTOMATED COMMITTER WAS ABSORBING HUMAN WORK.** `docs/ops/publish_status.sh:511` ran a BARE `git commit`, which commits THE WHOLE INDEX -- and that loop fires every ~2 minutes. Anything `git add`ed and not yet committed was swept into the next status commit. MEASURED: `d7b85965`, labelled *"status: T+147h38m"*, carries **366 insertions** of this session's `stage_eta` / `session_preflight` / ledger / CHANGELOG work. Nothing was lost (verified present at HEAD), but the commit log is a PRIMARY SOURCE for the write-up timeline, and it would just as happily have committed a HALF-FINISHED edit. It is the mirror image of P242, where a directory-level `git add` swept 17 runtime logs into an unrelated commit. Fixed to `git commit --only docs/RUN4_STATUS.md`, falsified in a throwaway repo: with an unrelated file staged, the status commit took only the status file and left the other staged. The publisher is re-invoked each iteration, so the fix is live without a restart. **⇒ TWO RULES: an automated committer must name its paths, and never leave files staged on this repo.** |
| **P250** | 2026-08-04 pass 2 | **FIXED + FALSIFIED** | **THE HIGHEST-VALUE FINDING OF THE PASS, and it was mine.** I edited `run_record_layers.sh` (the F13 wording fix) while a background instance of it was RUNNING. Bash reads a script INCREMENTALLY BY BYTE OFFSET, so the live instance resumed at the same offset in the new bytes, landed mid-token (`cord_science_audit.py: command not found`) and **re-executed two layers**. It then printed **`ALL SEVEN LAYERS RC=0`** anyway — because that banner asserted only `fail==0` and **counted nothing**, so it was equally true of a run that executed three layers, or none. Every layer happened to pass, so the certification of an irreplaceable archive was substantively true **by luck**. THREE fixes: (1) `layers_run` is now part of the verdict and a short count prints `ONLY n OF 7 LAYERS RAN. THIS IS NOT A CERTIFICATION.` and exits 1 — falsified on a 2-layer copy, which the old code would have passed at rc=0; (2) per-run `OUTDIR` keyed on `$$`, because two concurrent runs previously shared `/tmp/layer_<name>.out` and each printed an RC pointing at a file the other could overwrite; (3) the whole body is wrapped in one compound command, forcing bash to parse to the closing brace before executing, so a mid-run edit can no longer scramble control flow. **⇒ NEVER EDIT A SHELL SCRIPT WHILE AN INSTANCE IS RUNNING — and a banner that names a count must COUNT.** |
| **F3** | 2026-08-04 pass 2 | **FIXED + MUTATION-PROVEN** | The `-1h` VALUE had no assertion: both fixtures had an empty 1 h window by construction, so `d1` was identically 0 and `d1 = 0` scored full marks. New M11/M12 fixture: a cell at 32 records with 5 inside the hour was at 27 an hour ago, so rung 30 fell by **3** (the crossing part) and rung 100 by the full **5**. Mutants `d1 += 0` and the pre-fix whole-cell rule both fail. |
| **F4** | 2026-08-04 pass 2 | **FIXED + MUTATION-PROVEN** | `_parse_cores` and `concentration` were reachable-but-unasserted. `_parse_cores` carries a PRODUCTION contract (`publish_status.sh` passes `?` on ssh failure and `0` when everything is queued, and neither may crash the empirical block). M1-M8 pin both; letting a non-positive core count through fails M2/M3. |
| **F6** | 2026-08-04 pass 2 | **FIXED (as a stated bound)** | A missing unit is not in `cells`, contributes its FULL rung to `remaining`, and can NEVER contribute to `owing_rate` — so the gate cannot see it. Gating on it was considered and **rejected**: with 8 units missing it would gate every rung at every hour and the table would carry no information, the same degeneracy that killed the per-cell max. The page now states the asymmetry and its DIRECTION explicitly: *"those 8 units are NOT in the rate's denominator and CANNOT be ... Both columns are OPTIMISTIC by that share until those units start."* |
| **F8** | 2026-08-04 pass 2 | **FIXED + MUTATION-PROVEN** | The composition warning hardcoded a 12 h window while `eh2` falls back to 24 h when the 12 h window is empty — so it went SILENT in exactly the state where one line's dominance matters most. Window resolved once and shared. M13-M15 use a 13-23 h-old fixture; hardcoding 12 back fails M14. |
| **F11** | 2026-08-04 pass 2 | **FIXED + MUTATION-PROVEN** | Any stray subdirectory under a `test*` root became a registered unit owing a full rung. Now an arm must HOLD RECORDS or be a REGISTERED frozen winner — the same two-signal rule as S15's C6, so the two instruments cannot disagree about what an arm is. M9/M10. ⚠ My first version tested the directory NAME (`-s<N>`) and dropped every selftest fixture, failing six assertions at once: **a rule that reads the payload survives a layout it did not anticipate; a rule that reads the filename does not.** |
| F12 | 2026-08-04 pass 2 | **FIXED** | `session_preflight --full` advertised "~60 s" against a measured ~200 s. A session budgeting 60 s either kills it or concludes it hung. Corrected, with an instruction to re-measure rather than let it drift again. |
| F13 | 2026-08-04 pass 2 | **FIXED** | `run_record_layers.sh` called itself SEVEN in the banner and EIGHT in a comment. Reconciled: seven GATED layers plus three ungated MEASUREMENTS (S15 is a measurement, not a gate). |
| **P249** | 2026-08-04 pass 2 | **FIXED** | Mine: an ad-hoc process census reported `cycle_loop logical=2` and `publish_loop logical=2` against preflight's correct 1. Cause: the boot task's shared `cmd.exe` launcher names EVERY loop on its command line, so it matched each pattern and was counted as a separate root each time. Resolved by parent PID (12640 -> 25064 -> 25084 is ONE chain). **A pattern census counts CHAINS *and* LAUNCHERS** — RUN 18 recorded the first half of that lesson and I re-created it with the second. Preflight was right; my throwaway was wrong. |
| F5 | 2026-08-04 RUN19 | **FIXED** | `CEILING = RUNGS[-1]`; all **8 executable** `568` sites now derive from it (historical numbers in comments deliberately left, they record what was true then). |
| F9 | 2026-08-04 RUN19 | **FIXED** | The archive walk now precedes the clock sample, so every mtime held is <= the clock it is compared against. |
| F10 | 2026-08-04 RUN19 | **FIXED** | Selftest section J gained the `except` it lacked; an exception there is now a recorded FAIL rather than a traceback that suppresses every other result. |
| F7 | 2026-08-04 RUN19 | **FIXED** | E1 no longer asserts a host-dependent skew (it would FAIL on any UTC host, i.e. exactly where the defect is impossible). It reports the observation, and **E1b** asserts the portable invariant: no window bound in the file is built from `utcnow()`. ⚠ My first E1b was itself wrong — it matched the module docstring that DOCUMENTS the trap and its own source line. Narrowed to assignment targets. |
| **F2** | 2026-08-04 RUN19 | **FIXED + MUTATION-PROVEN** | The go-forward exclusion had NO coverage and both deleting and inverting it scored full marks. New **K** fixture: a near-ceiling HIGH producer (560 records, excluded), a mid cell (300, included) and a sub-rung-30 cell so the ladder dates. **K4 is a RATIO, not a gap** — the first version asserted "gap > 24 h" and the INVERTED mutant still cleared it on a 90-day horizon. Fixture rates 44 / 4 / 40 give ratios 11 / 1.1 / 1.0. Mutation proof: delete → K3+K4 fail; invert → K4 fails. |
| **F1** | 2026-08-04 RUN19 | **FIXED + MUTATION-PROVEN** | `GATED` is now **absorbing upward**: once a rung gates, every higher rung gates and is tagged `barrier>=R`. Reaching 568 requires reaching 279, so a low barrier cannot coexist with a high date. New **L** fixture reproduces the shape; removing absorption makes L2 fail. |
| **F15** | 2026-08-04 RUN19 | **FIXED** | **Found by the selftest failing to report its own failure.** A `ck` value can carry rendered page text, rendered text carries non-ASCII, and the console is cp1251 — so printing a FAIL line raised `UnicodeEncodeError` INSIDE the reporter. The run died with a traceback and **not one pass/fail line**. A reporter that crashes on the content it exists to report is the worst failure mode available; it is why F2/F1/E1b were invisible for one cycle. Now `backslashreplace`-sanitised. |
| **P247** | 2026-08-04 RUN19 | **FIXED** | Mine: **my A0a-A0d cases tested the FUNCTION but not that `render()` USES it.** The mutation proof reverted only the CALL SITE to the elapsed-wall-clock formula and every A0 case still passed. Added **A0e**, which asserts render's own output says `UNKNOWN still to run` on a fixture with no search tree. Caught by the proof, not by review. |
| **P248** | 2026-08-04 RUN19 | **FIXED** | Mine: F1's absorption silently made three existing fixtures gate every rung, so **J1/J2 began comparing empty lists** — vacuous passes created by my own fix, the precise class this campaign keeps finding. Caught because J3 (`rows >= 3`) failed. Fixtures gained a sub-rung-30 producer; J1 now exercises **seven** dated rows, up from four before the change. |
