# RUN 12 — SESSION PROMPT (OPS lane). Written 2026-08-01 16:10 UTC at T+91h.

> **You are the OPS lane of a live, irreplaceable MSc dissertation campaign.** Twelve supervised
> driver lines have been running since 2026-07-28. Real money is spent. The test data is sealed.
> There is no re-run. **Read §0.1 and §0.3 before your first substantive action.**

---

## §0.1 ★★★★★ THE MONITORING MANDATE — NON-NEGOTIABLE

**READ THE CYCLE LOG ON THE FIRST TOOL CALL OF EVERY BATCH, EVERY TURN. No clock. No judgement about
whether "enough time has passed."**

```bash
cd /c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
tail -3 docs/ops/watch/CYCLE_LOG.md
```

**If the newest line is more than ~2 minutes old the loop is DEAD.** Restart it:

```bash
nohup bash docs/ops/cycle_loop.sh > /dev/null 2>&1 &
```

Five sessions before RUN 11 failed at this; **RUN 11 held it without exception** — observed ages 20 s,
21 s, 43 s, 45 s, 69 s, never near the threshold, no restart needed. Report the cadence in your
messages so a lapse is visible.

`RED` is the **standing C4-boundary notice plus two ACKNOWLEDGED alarms** — the normal state, not a
fault. What must never change: **`drift=0`**, **`sci=OK`**, **24 drivers**.

---

## §0.2 OPERATING DOCTRINE

**FOUR RUNGS OF DEPTH.** Execution → structure → meaning → **the instrument**. Most defects this
project finds live on rung four: the measuring device was wrong, not the measurement.

**SIX VERIFICATION TECHNIQUES.**
1. A positive control in every test — **prove a new test can FAIL against the pre-fix code.**
2. **Say the denominator out loud.**
3. **Cross-check by an independent route.** Two derivations agreeing is evidence; one repeated is not.
4. **On a surprising result, suspect YOUR OWN SCRIPT first.**
5. **Read the PREDICATE before planting the violation.**
6. **The author must not grade their own work.**

**THE FOUR TELLS.** ① A clean baseline that already reads the failing value proves nothing.
② Three failures in a row is a broken harness. ③ **A clean 0 % or 100 % means suspect the
SPECIFICATION.** ④ **THE REASSURING COMMENT — when a comment and the code disagree, the comment is
the more dangerous artefact.**

**★ ZERO AND ABSENT ARE DIFFERENT VALUES.** RUN 11 added a third: **LAUNCHED**. A unit directory with
an `_env/` sidecar and no `record.json` means *started*, not *finished*; a glob that counts `*.json`
turns launched into finished. **Absent, launched and finished are three values.**

### ★★★ THE FIVE LESSONS RUN 11 PAID FOR — READ THESE, THEY ARE THE SESSION'S REAL OUTPUT

1. **A STRIKING ROUND NUMBER IS THE SIGNAL TO RE-DERIVE, NOT TO PUBLISH.** I broadcast *"Myriad is
   100 % full, 0.0 % free, every family"* to three lanes. I had measured `NCPU − LOAD`. **SGE
   schedules on SLOTS, not load.** The truth was **35.4 % free**. Withdrawn as M203, corrected in
   M210. *I had written "one derivation repeated is not evidence" into the record hours earlier.*
2. **I MADE THE ONE-SAMPLE-READ-AS-THE-POPULATION ERROR FOUR TIMES IN ONE SESSION.** One node's
   status read as a family's; `*.json` counted as records; a self-matching process query read twice
   as a real process; a lifetime error-grep read as "since the restart". **Every one was caught by
   counting the whole population instead.**
3. **THE REPO IS USUALLY AHEAD OF YOU.** Three of my hypotheses died on contact with a comment
   someone had already written: `h_rt` (measured max 12.70 h vs a 15 h request — correctly sized),
   `snx` (10,000/node, not a fence), and chunking (**`mode_d_supervisor.ps1:119`: Myriad SERIALISES
   array tasks, `tasks 2..n sit in hqw`** — `--chunk-tasks 25` would have parked 96 % of tasks in
   hold). **Grep the file before you improve it.**
4. **OVERSTATING A RISK IS AS INACCURATE AS UNDERSTATING ONE.** I raised D23 as a hazard and resolved
   it the same hour; I nearly broadcast a family-wide RHEL9 fence off one node. **Downgrade loudly
   when the evidence says so — a phantom in a register costs the next reader real attention.**
5. **ANOTHER LANE CHECKING IS THE COUNTERMEASURE THAT ACTUALLY WORKS.** Coord corrected my blindness
   attestation within five minutes; analysis corrected my "same CPU family" premise; coord found the
   `PREREGISTRATION.md:1051` line four lanes had argued around for six hours. **Post early, post the
   numbers, invite the attack.**

---

## §0.3 IN-FLIGHT STATE — VERIFY THESE FIRST

```
  RUNNING_SHA   58b388f2     (docs/ops/cycle.py:120)
  HEAD          9f60a18a
  drivers       24           supervisors 12 + 1 fenced watchdog (pid was 25208)
  records       ~2,624       spend ~$45.44      slots ~848
  drift         0 BOTH arms  freeze 3ca6f01ab772… MATCHES   repro audit 8 PASS / 0 WARN / 0 FAIL
  PIPELINED     11 of 12 lines (h3 correctly sequential — --h3-singleshot refuses --tiered)
```

**YOUR FIRST FIVE CHECKS:**

```bash
tail -3 docs/ops/watch/CYCLE_LOG.md                                    # the mandate
git diff --name-only 58b388f2 HEAD -- src scripts config prompts       # drift arm 1 — MUST be empty
git status --porcelain -- src scripts config prompts                   # drift arm 2 — MUST be empty
powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { \$_.Name -eq 'python.exe' -and \$_.CommandLine -like '*run_campaign_cluster*' }).Count"   # MUST be 24
powershell -NoProfile -Command "@(Get-CimInstance Win32_Process | Where-Object { \$_.Name -eq 'python.exe' -and \$_.CommandLine -like '*pipeline-rungs*' }).Count"         # MUST be 22 (11 lines x 2 procs)
```

**⚠ WHEN YOU ENUMERATE PROCESSES, FILTER ON `Name -eq 'powershell.exe'` AND `-File .*mode_d_supervisor\.ps1`.**
A loose `CommandLine -match 'mode_d_supervisor'` **matches your own query** and invents processes.
This bit RUN 11 twice. Line names contain dots and hyphens (`qwen3.5-9b`, `glm-5.2`), so an
alphanumeric-only capture silently merges two lines into one (analysis hit this too).

**TWO STANDING GATES RUN THEMSELVES — do not re-implement:** cycle check **4b**
`docs/ops/sandbox_gap_watch.py` and **4c** `docs/ops/integrity_gate.py`. Both 600 s time-guarded and
hard-wrapped; verdicts cache in `docs/ops/watch/.sandbox_gap_last` / `.integrity_gate_last`; **`0` is
clean.**

---

## §1 THE PRIORITIES (they ACCUMULATE; nothing is ever dropped)

1. **95 %+ grade floor**, as close to 100 % as possible.
2. **World-class, publishable** (TMLR-and-up / ICAIF-main).
3. **Very deep** — mechanism and intuition over breadth.
4. **Corpus-grounded AND genuinely novel** (196+ first-hand-read papers).
5. **★ 100 % REPRODUCIBLE — a WARN counts as a FAIL.**

**Tamer's standing instruction, verbatim:** *"I don't give ten fucks about freeze, or unfreeze,
hashes, bounds, or anything else if that shit even dares to threaten the quality of the campaign… I
grant you full permissions, on the level as me… Do not stop until you absolutely strictly and deeply
verify that absolutely everything is strictly flawless."*

**HE HAS REMOVED DR OKHRATI FROM THE LOOP** (*"I won't send anything to Okhrati, I give you full
permissions, and ratify your actions"*). **You decide — and you RECORD the reasoning so the decision
is auditable rather than merely authorised.** Full permission raises the bar on the thinking; it does
not remove it.

**AND HE HAS ESCALATED CAMPAIGN SPEED FOUR TIMES.** *"Maximise the speed to an absolute maximum
possible… make sure you use the maximum the Myriad can offer to us."* **§4 has the measured answer;
read it before re-opening the question, because RUN 11 already chased and killed four of the obvious
hypotheses.**

---

## §2 HARD PROHIBITIONS — every one was earned

- **NEVER add Claude/Anthropic attribution** anywhere. The default `Co-Authored-By` convention is
  **REVOKED**. Tamer is sole author. **Re-read every commit message before committing.**
- **NEVER `git clean -xfd` or any `-x`** — a dry run showed **1,264 paths** would go, including the
  frozen panel.
- **NEVER `git add -A` / `git add -u`** without reading `--numstat` first. Other lanes have
  uncommitted work in the same tree at all times — **stage files by name, never by wildcard.**
- **NEVER `git stash`** in this repo (P114).
- **NEVER lower SGE priority**; never `qdel -u ucestes`; `qalter -l` is forbidden site-wide.
  Every job runs at `ppri = 0` and `PRIORITY_RUNG_BASE = 0`. **Verified in RUN 11 — keep it that way.**
- **NEVER put backticks or backslashes in a bash heredoc or `-c` string — they EXECUTE.** RUN 11 sent
  a bus message with three LaTeX macro names eaten by command substitution. **Write the body to a
  file and pass the path.** (`scratchpad/busmsg.py` in RUN 11 did exactly this.)
- **NEVER inline `git commit -m`** in PowerShell — write a file, use `git commit -F`.
- **NEVER pull Refinitiv from Bash** — PowerShell + `.venv-lseg` only.
- **NEVER trust a pipe's or wrapper's exit code** — read `PYTEST_RC` from the LOG.
- **NEVER put non-ASCII in a `.ps1`**, and validate with `Parser::ParseFile` after editing.
- **NEVER read a treatment arm's SEALED-TEST outcome** until the ladder completes.
- **NEVER edit `src/ scripts/ config/ prompts/` while live WITHOUT** either completing a relaunch
  **or** proving the file is outside the driver import closure and re-basing `RUNNING_SHA`.

**THE IMPORT-CLOSURE TOOL IS NOW GENERALISED — USE IT, IT TAKES ARGUMENTS:**
```bash
python docs/ops/import_closure.py                      # the live diff, both arms, automatically
python docs/ops/import_closure.py src/foo.py scripts/bar.py
```
It derives targets from the working tree **plus everything committed since `RUNNING_SHA`**, which it
reads out of `cycle.py`, and reports **NOTHING TO CHECK** on an empty set rather than passing.
*Before RUN 11 it hard-coded two files and printed a clearance about them whatever you asked.*

**⚠ AND THE ONE CASE WHERE RE-BASING IS WRONG:** if you commit a file that **IS** in the closure
without relaunching, re-basing `RUNNING_SHA` asserts that the executing code matches the committed
code **when it does not**. Either relaunch, or do not commit it. See **D24**.

---

## §3 WHAT RUN 11 DID — read the records, do not redo the work

`docs/CAMPAIGN_EXECUTION_RECORD.md` **§100.39 – §100.52**; `CHANGELOG.md` **[2026-08-01l]**.

| § | finding |
|---|---|
| 100.40 | **The build printed "0 pandoc warning(s)" out of a channel it never read.** `subprocess.run(text=True)` decoded with the box's cp1251; the channel came back **`None`** and 40,871 chars of diagnostics vanished. **And fixing the encoding alone would not have helped** — the filter missed tectonic's lowercase `warning:`, 0 of 51 lines. **Two defects, either sufficient.** It had hidden **17 dropped characters on every build for 19 days.** |
| 100.40.4 | **Bold AND italic were flattened document-wide** while the body sat in a SERIF — so the `helvet` line delivered neither the guideline it existed for nor the shapes. **~5,700 bold + ~4,100 italic spans.** Now **TeX Gyre Heros**, loaded BY FILE from the pinned bundle. |
| 100.40.6 | The build now **VERIFIES THE DELIVERABLE IT WROTE**: `rc=3` control byte · `rc=4` un-typesettable character · `rc=5` unmappable glyph. Two **independent** glyph routes, deliberately. |
| 100.41 | **`import_closure.py` was clearing files nobody had asked about** — the reassuring-comment tell in executable form, inside the tool the live-edit protocol depends on. Generalised. |
| 100.42 | **`campaign_summary.json` does not exist for RUN 4** → four registered analysis outputs (incl. the DeMiguel floor already wired into the PDF) would be silently absent and **unrecoverable**. `docs/ops/write_campaign_summary.py` built, rehearsed, four safeguards. |
| 100.43 | **A16 — node N2 implements its registered rule for the first time.** Pre-specified on the bus while **provably blind** (13:01:15Z, 0 of 3 H2-RA legs computable) BEFORE any code was written. Three verdicts, all reported. **TWO test bypasses closed.** Proven against pre-fix code in a detached worktree. |
| 100.44 | The registered analysis key set is **machine-defined: 39 keys**, not the remembered 35. AST-pinned; unexplained absence **exits 4**. |
| 100.46 | **My blindness probe counted a launcher sidecar as a result** — every count doubled. Caught by coord in five minutes. |
| 100.47 | **Theory → Appendix C.** Body now Chapters 1–5, Appendices A–E, no mid-body appendix. |
| 100.49 | **The throughput investigation** — and the retraction of my own "cluster is 100 % full". |
| 100.50 | **The pipelining rollout, executed and verified.** |
| 100.51 | **THE CORES QUESTION, ANSWERED.** |
| 100.52 | Coord's three OPS items closed (F-18, F-19, A16-W13). |

**`docs/ops/WITHDRAWN_CLAIMS.md` — now including a row that withdraws W13 itself.** **GREP IT before
any claim from lane traffic enters `paper/`.** *Retractions travel slower than assertions.*

---

## §4 ★★★★★ THE CORES QUESTION — THE MEASURED ANSWER, SO YOU DO NOT RE-RUN IT

**Tamer has pressed this four times. Everything below is first-hand and read-only.**

### What is NOT the problem — all checked, all clean
| checked | finding |
|---|---|
| free capacity | **4,497 slots free (35.4 %)**, 3,366 in pool D. *Not* full — my "0 % free" was load, not slots. |
| quota | **none applies.** The only RQS is `slowemdown`, **disabled**, targeting another user. |
| job cap | `max_u_jobs = 1000`; **we hold ~109**. |
| priority | `ppri = 0` on every job; `PRIORITY_RUNG_BASE = 0`. Neutral, correct. |
| `h_rt` | 15 h against a measured **p99 9.92 h / max 12.70 h** — a 1.18× margin. **Correctly sized; cutting it kills jobs.** |
| `snx=1` | every node advertises **`snx=10000`**. Not a fence. |
| memory / tmpfs | 2 G/slot vs a 6.2 GB measured peak; tmpfs already 15 G → 1 G. |
| pack | CPU efficiency **7.03 of 8 slots = 88 %**. `smp 36` starves (live-probed, 2+ days). |
| `--chunk-tasks 1` | **CORRECT AND HARD-WON.** Myriad **serialises array tasks** (`2..n sit in hqw`). Do not "improve" it. |

### What the answer actually is
**The campaign is in the SEARCH phase, whose width is bounded by the work itself:**
`12 lines × 2–3 concurrent arms × 5 candidates/generation ≈ 105 tasks × 8 slots ≈ 840 slots.`
Generations are **serial by design**; candidates-per-generation is a **registered quantity**.
**Arms are already concurrent** (gpt-luna runs three at once). **Nothing is stalled** — every line
produced a record within 23 minutes when last checked.

**AND UNDER R101 THE REPORTED RESULT IS THE *COMMON RUNG* — A MINIMUM OVER 11 LINES.**

| line | arms frozen /5 | test records |
|---|---|---|
| core | 5 (of 10 search arms) | 360 |
| qwen3.5-9b · gemini | 5 · 4 | 82 · 60 |
| gpt-luna · nemotron · sonnet · haiku | 5 · 4 · 4 · 4 | **0** |
| deepseek · glm-5.2 | 3 · 3 | **0** |
| **kimi-k3 · qwen3.6-27b** | **2 · 2** | **0** |

**EIGHT OF TEN LEG LINES HOLD ZERO TEST RECORDS. Capacity given to a line already above the minimum
is worth EXACTLY ZERO. The critical path is `kimi-k3` and `qwen3.6-27b` at 2 of 5 arms frozen, and no
number of cores moves it.**

### What RUN 11 changed, and when it pays
`--pipeline-rungs` was on the **core line only**; eleven lines would have entered C4 draining each
assurance block before submitting the next (`campaign.py`: the sequential path *"FORFEITS CAPACITY
during every block's drain"*). **All ten legs now pipeline.** It buys nothing today and everything at
C4 — **40,328 of 42,128 trainings, 2.8 % done, embarrassingly parallel, imminent.**

### ★ THE MEASUREMENT THAT PROVES IT WORKED — DO THIS WHEN THE FIRST LINE REACHES C4
**Today the queue is 0–2 pending against 3,366 free slots.** When a line crosses into C4 the queue
should go to **hundreds**. Sample it:
```bash
ssh myriad 'Q=$(qstat -u ucestes | tail -n +3); echo "r=$(echo "$Q" | awk "\$5 ~ /r/" | grep -c .) qw=$(echo "$Q" | awk "\$5 ~ /qw/" | grep -c .) slots=$(echo "$Q" | awk "\$5 ~ /r/ {s+=\$9} END {print s+0}")"'
```
**If C4 opens and `qw` stays near zero, the fix did not take and that is the thing to investigate.**

### Do NOT chase the 686 unverified slots
`d97a`/`d97b` are inside pool D, admitted by `-ac allow=d`, and **we have never run on them**. The
analysis lane's **187-node empirically-verified 6240 allowlist** (`d00a ×178, d00b ×9`) is the
reference — *not* family-level reasoning, because **d00a is not status-uniform either**. They cannot
move the common rung, so spending them risks RUN 4's **2,488/2,488 single-model homogeneity** — the
strongest determinism evidence in the campaign — for zero gain. Analysis' `substrate_watch.py` C3
alarms on the first task-run outside the allowlist. **If C4 ever makes us capacity-bound, answer it
with a one-core probe job reading `/proc/cpuinfo`, as a measurement, not an inference.**

---

## §5 OPEN — nothing here is blocking, all of it is real

**HIGHEST VALUE, AND UNRECOVERABLE IF MISSED:**
1. **`campaign_summary.json` MUST be written AT TEARDOWN**, before the archive is disturbed, with
   `python docs/ops/write_campaign_summary.py`. It refuses while drivers are live, refuses to
   overwrite, cross-checks the derived windows against the registration, and records
   `all_arms_tested: null`. **Without it, four registered analysis outputs are silently absent and
   cannot be back-computed.**
2. **The final compute figure must be re-taken AFTER all arrays drain** — `qacct` excludes RUNNING
   jobs, so 67,166 CPU-h is a **LOWER BOUND**.

**QUEUED, ALL IN `docs/DEFERRED_FIXES_RUN4.md`:** **D22** `provenance.py` encoding (IN the closure)
· **D23 RESOLVED** (job-cap rejection is graceful) · **D24** the `_outage_is_fatal` OR/AND bound —
**3.6 h not the documented 12 h at the live `--poll-secs 180`**, patch written, deferred because
`driver.py` IS in the closure; **the supervisor's own 1000-attempt retry loop plus the watchdog make
the realised cost ~10 minutes, so it is a real defect and not an emergency**.

**FROM COORD'S BOARD (`python .claude/lanes/openitems.py --open`):** F-1/F-23 leg4 `h2_pair`
`distributional=0 scalar=0` — **a deliberate deferral closes it, just say so.**

**FOR TAMER:** spend ~$81 (2.71× the **advisory** R83 ceiling — recommendation: **do not truncate**;
the low yield IS the capability finding) · amend R106 to what was EXECUTED · correct the kimi
"strongest pin" claim in the Ramin brief.

---

## §6 COORDINATION — Tamer has asked twice that you do this properly

Three peer sessions share this repo. **Join the bus and read your inbox BEFORE acting.**

```bash
python ../.claude/lanes/lanebus.py join ops
python ../.claude/lanes/lanebus.py inbox
python .claude/lanes/openitems.py --open     # coord's verified board; each row re-derives its status
```

`msg <lane>` · `alert` · `ack <id>` · `done <id>` · `withdraw <id> <reason>`.

**They have been right often enough to take seriously and wrong often enough to verify every time.**
In RUN 11 coord corrected my blindness attestation in five minutes, analysis corrected my CPU-family
premise and independently confirmed the rollout mid-flight, and coord found the one hash-bound line
that settled a six-hour four-lane dispute. **Two lanes strengthened findings by arguing against their
own position. Match that standard, and post your numbers early so they can be attacked.**

**⚠ Bus bodies go through a FILE, never a shell string** (backticks execute — RUN 11 lost three LaTeX
macro names that way).

**END-OF-WORK DUTIES (all four, every time):** `python scripts/update_handoff.py` · a short cursor
entry · a DETAILED `CHANGELOG.md` block **even with no commits** · push the backup branch.
