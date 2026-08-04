# RUN 20 — SESSION PROMPT. **READ THIS IN FULL BEFORE YOUR FIRST SUBSTANTIVE ACTION.**

Written 2026-08-04 ~11:10 UTC at Tamer's instruction: *"I want to transition into the next claude
code session. Ultrathink very deeply and extensively, document absolutely everything from this
session, and write a prompt for the next claude code session, don't forget to also tell it to very
deeply and extensively study absolutely all files in this dissertation so it has the comprehensive
knowledge, and zero gaps in knowledge... Make sure you include my prompts on that everything should
be flawless as well. Make sure in addition it also preserves these loops, but dives much deeper, and
checks more extensively, and checks very deeply absolutely everything, from all dimensions and
angles possible, it must not miss anything, and make sure it ultrathinks, and minimises the ETA to
an absolute minimum as well. And make sure absolutely everything is very logical, meaningful, and
absolutely flawless and 1000000% absolutely strictly correct."*

> **You run the live campaign on an irreplaceable MSc dissertation.** RUN 4 has been running since
> 2026-07-28 21:08 UTC. Real money is spent, the test data is sealed, **there is no re-run.**
> This supersedes `docs/RUN19_SESSION_PROMPT.md`; where they disagree, **this wins.**
>
> ⚠ **A SEPARATE SESSION OWNS THE WRITE-UP.** `paper/**`, `docs/GRADE_95_MASTER_PLAN.md`,
> `docs/V2_WRITE_TIME_REGISTRY.md`, `docs/CITATION_WORK_MAP.md` are **NOT YOURS.** `CHANGELOG.md` is
> **SHARED** — re-read it immediately before every edit, and never reuse a date label.
>
> ⚠ **THE LANE CLASSIFICATIONS ARE ABANDONED.** Do not register a lane. Reading the board with
> `lanebus.py` STAMPS a heartbeat — it is not read-only. Avoid it.

---

# §0 ★★★★★ TAMER'S STANDING BRIEF — VERBATIM. THIS IS THE OPERATING CONTRACT.

### §0.1 THE FLAWLESSNESS MANDATE (carried forward every session)

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

### §0.2 THE RUN-19 ADDITIONS, VERBATIM — these created the loop contract

> *"Also every 1 hour I want you to very closely check everything very deeply, check everything, all
> lines, all records, all outputs, all processes, absolutely everything, it all must be
> 1000000000% strictly absolutely flawless."* → later **"change from every 1 hour to every 30 min"**

> *"make sure if something is found, its always fixed, and ensure that absolutely everything is very
> strictly absolutely flawless"*

> *"make sure the checks that are every 30 minutes do not stop until they ensure absolutely
> everything is 10000% absolutely strictly flawless. I give them full permissions, do whatever it
> takes to ensure absolute flawlessness."*

> *"also dont forget to add the speed check component all the time, and its maximisation"*

> ⭐ *"make sure you very deeply and extensively study this whole project, have an extremely
> extensive knowledge and absolutely 0 gaps in knowledge."* — **DO THIS BEFORE ACTING. §2 is the
> reading list; it is not optional and it is not a formality.**

### §0.3 HOW TO READ THAT MANDATE — the single most important paragraph in this file

**Full permission raises the bar on the THINKING; it does not lower the bar on VERIFICATION.**
RUN 19 fixed 28 defects. **Every single one of the most serious was found by an auditor or by
reading my own output back — not one by feeling confident.** Three of my own fixes were themselves
defective (P257 failed OPEN, P258 named no cause, P268 crashed a live cycle). **The author's own
work is the least reliable thing produced.** Nine auditors across nine sessions; all nine found
more than the author did.

---

# §1 YOUR FIRST COMMANDS

```bash
cd /c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
date -u +%Y-%m-%dT%H:%M:%SZ                      # ★ FIRST. See §7 lesson ⑥ — never assume the clock.
python docs/ops/loginnode_guard.py --once        # UCL penalty check
tail -5 docs/ops/watch/CYCLE_LOG.md
python docs/ops/session_preflight.py --full      # ~200 s; 0 clear · 1 ATTENTION · 2 FAIL
.venv/Scripts/python.exe docs/ops/line_balance.py --once
.venv/Scripts/python.exe docs/analysis/record_seed_completeness.py   # THE COMMON BANKED RUNG
bash docs/ops/run_record_layers.sh               # 7 layers + 3 measurements
ssh -o BatchMode=yes myriad "hostname"
```

Then say **"Resuming from: … — next: …"** and CONTINUE. **Never ask "what now".**

---

# §2 ⛔ MANDATORY READING — ZERO GAPS IN KNOWLEDGE IS A REQUIREMENT

| file | why |
|---|---|
| **this file** | the brief |
| **`docs/ops/watch/FLAWLESS_LEDGER.md`** | ⭐ **THE CONTRACT FOR THE 30-MIN LOOP.** Fixing is mandatory; the three terminal states; what is NOT a defect; the SPEED component; every OPEN row. **READ IT IN FULL BEFORE EVERY PASS.** |
| **`CLAUDE.md`** | LAW. the ★ PRIORITIES, the four authorities, Okhrati's D1–D6, Stefan's S1–S8, the 95+ doctrine |
| **`PREREGISTRATION.md`** | THE FROZEN CONTRACT. **R101** (common rung, seed parity), **R111** (the H1 canon CLIMBS), **R115**, **Amendment E1** |
| **`docs/HANDOFF.md`** §1–§3 | current state + the authority map |
| **`docs/CAMPAIGN_EXECUTION_RECORD.md` §132–§133** | **§133 is RUN 19.** §132 is RUN 19's first pass. |
| **`CHANGELOG.md` `[2026-08-04b]`** | the same, narrative, with all eleven passes |
| **`docs/ops/MAINTENANCE_2026-08-12.md`** | ⚠ **UPDATED WITH UCL'S OFFICIAL NOTICE — MAY RUN TWO DAYS. READ EARLY.** |
| **`docs/DEFERRED_FIXES_RUN4.md`** | every known-open defect incl. **D36** |
| **`memory/session-current-focus.md`** ▶ NOW | the live cursor |
| **`docs/ops/cycle.py`** | ⚠ **RUN 19 changed 10 things in it.** Read the P259–P271 comment blocks; they are the map of how this instrument used to lie. |
| **`docs/analysis/record_seed_completeness.py`** | S15/C6 — the instrument that reports THE RESULT |
| **`src/cluster/lanes.py`** | `_TEST_UNITS_PER_RUNG = 71`, `SERIAL_CHAIN_BUDGET`, the makespan model |

### ⛔ THE READING GATE — answer these FROM THE SOURCES before acting
1. What are the **four authorities**, and what happens when they conflict?
2. What is **H2**, and why is the fed tail **ENDOGENOUS**?
3. What is the **COMMON RUNG**, and why does gemini's completed 568 raise the result by nothing?
4. **Why can an arm hold 567 perfect records and bank rung 189?** (the S15 question)
5. Why must you NEVER read a treatment arm's sealed-test outcome?
6. Which paths are **drift-fenced**, and what does editing one cost?
7. **Why is `arms_full` labelled `legs-ever`?** (P271 — and what it proves about reading a token's NAME instead of its CODE)
8. **Why did `RED` mean nothing for 4,558 cycles?** (P259)
9. What is the difference between a record COUNT and a BANKED RUNG?
10. **Why is the ETA NOT core-bound?** (§6 — and be able to derive the 21.9 h floor yourself)

---

# §3 STATE AT HANDOVER (2026-08-04 11:07 UTC, T+158h)

```
records 12,490 · spend $45.5019 · drift 0 · sci OK · freeze 3ca6f01ab772 MATCHES
preflight VERDICT OK all 17 · 7 record layers RC=0 · line_balance CLEAN · Eqw/hqw 0
disk 38.7 GB · slots ~1,750 · 219 running / 134 queued · 10/12 lines up, 2 COMPLETE
exogenous stop 2026-08-27 · backup branch: backup-2026-08-04-run19 (pushed, current)
verdict line now VARIES (ATTN) — RED means something again
```

### THE LADDER — banked rungs (S15/C6). **THE COMMON RUNG IS 0.**
| line | rung | what caps it |
|---|---:|---|
| gemini-2.5-flash · h3_singleshot | **568** | COMPLETE |
| gpt-5.6-luna | **189** | `placebo` missing seeds 192/193 |
| qwen3.5-9b | **100** | climbing |
| haiku · qwen3.6 · sonnet | **30** | climbing |
| **core · deepseek · glm · kimi · nemotron** | **0** | **the `h2_pair` (`distributional`+`scalar`) that every line tests LAST** |

**⇒ THE REPORTED RESULT IS 0, and the binding constraint is a SERIAL DEPENDENCY CHAIN, not compute.**

---

# §4 ⚠⚠ THE FIVE THINGS THAT WILL MISLEAD YOU

**① THE COMMON RUNG IS 0 AND THAT IS THE HONEST STATE, not a fault.** Five lines have not begun
their headline arms. Do not "fix" it.

**② A FLAT NUMBER IS NOT A STALLED NUMBER — AND RUN 19 PROVED IT PRECISELY.** Rung-30 remaining sat
at 404. Measured: **15 cells owe it, 10 have NEVER produced, and ZERO produced in the last 2 h**,
while the fleet does ~175 rec/h entirely into cells already ≥30. It moves in jumps of 8/12/30.

**③ 98.9% OF THE FLEET'S OUTPUT CANNOT RAISE THE RESULT.** Measured over 12 h: 2,098 of 2,122
records landed in cells already at or above rung 30. **Doubling the cores doubles that 98.9%.**

**④ `arms_full` DESCRIBES THE LEGS ONLY, AND SAYS SO NOW.** It reads `10/10legs-ever`. The
confirmatory line was invisible to it for the whole campaign via a silent regex failure (P271).

**⑤ SEVEN LINES SHOW A NEWEST RECORD >24 h OLD. THAT IS NOT A STALL.** gemini and h3 are COMPLETE at
568; the rest are between packs or behind gates. **`line_balance` is the arbiter**, and it is CLEAN.

---

# §5 ⛔⛔ MYRIAD MAINTENANCE — **WED 12 AUG, AND IT MAY RUN INTO THU 13 AUG**

**UCL's official notice (relayed by Tamer 2026-08-04) is now in
`docs/ops/MAINTENANCE_2026-08-12.md`.** Three things it changed:

1. ⚠⚠ **IT MAY RUN TWO DAYS.** The playbook was written for one. **A two-day outage exceeds every
   death clock** (TEST 12.0 h, SEARCH 3.0 h) — drivers WILL die and supervisors WILL relaunch into a
   dead cluster. That is E1/E2, expected, and no data is lost.
2. ✅ **THE DISPATCH CLIFF IS OFFICIAL.** UCL is draining jobs so they only start if they can finish
   before the outage. **Expect dispatch to stop ~15 h before, from ~17:00 Tue 11 Aug, and
   `records=` to flatten BEFORE the 12th. That flattening is CORRECT.**
3. ✅ **"No access" means the login-node penalty hazard is OFF during the window** and returns the
   moment access does. The supervisors' 3620–3820 s stagger is the protection. **No hand relaunches.**

**Position: RIDE IT.** Aug-11 pre-window checks are in the playbook §3.

---

# §6 ★★★ THE ETA AND THE CORES — **RE-MEASURED IN RUN 19 ON TAMER'S DIRECT REQUEST. DO NOT RE-LITIGATE; RE-READ.**

RUN 19 re-measured because the fleet had changed materially. **Every constraint re-tested unchanged**
— 357 jobs of a 1,000 cap, `qquota` EMPTY, zero `Eqw`/`hqw`, queued jobs verify schedulable. But the
important answer is not fair-share:

**① CORES CANNOT MOVE THIS RESULT.** 98.9% of output lands above the common rung (§4③).

**② THE FLOOR WITH INFINITE CORES IS ≥ 21.9 h.** `bayes_opt` owes 3 of 30 candidates and `tpe` 3 of
30, **strictly sequential by construction** (each proposal is a function of fitnesses already
observed) = **13.4 h**. Then core still needs C2/C3/C4, and a TEST training is 1-thread = **8.5 h**.
Neither is compressible.

**③ WE ARE ALREADY THE LARGEST CONSUMER ON THE CLUSTER.** 1,768 slots vs 820 and 714 for the next
two users — **19.9% of all 8,886 running slots across 98 users**. There are ~2,900 free slots and
**128 hosts with ≥8 contiguous free** (so fragmentation is NOT the cause — only 8% is stranded), and
we still do not get them. **That is fair-share doing exactly its job.**

**④ QUEUING MORE BUYS NOTHING.** Correlation(queued, slots) = **−0.94** across eight measurements.
We are at our slot ceiling (~1,900 ÷ 8 ≈ 237 job slots; we run 212–238). **357 submitted is not a
choice — it is all the work that exists**, and every blocked line has submitted exactly its packs.

**⇒ THE ONLY LEVER IS HUMAN: ask UCL RC for more allocation. Even that cannot take the common rung
below ~22 h. DO NOT SPEND CAMPAIGN TIME ON CORES.**

---

# §7 ★★★★★ THE LESSONS RUN 19 EARNED — read these before you write any code

> ### ① A MINIMUM IS ONLY AS HONEST AS ITS POPULATION.
> S15 excluded arms that had produced nothing; the chain floor excluded work that had not happened;
> `arms_full` excluded the confirmatory line. **Ask not "is the arithmetic right" but "what is NOT
> in the set, and would including it change the verdict".**

> ### ② AN ALARM THAT CAN NEVER CLEAR CARRIES ZERO BITS.
> `RED` was pinned for **4,558 cycles**; `guards=2` and `arms_full=10/10` were constants on **all
> 5,038 lines**. A cycle carrying `ram:CRITICAL` was byte-identical to its neighbours. **The moment
> RED was unpinned it immediately surfaced a real, escalating memory defect (P270).**

> ### ③ A CHECK THAT FAILS *OPEN* IS WORSE THAN NO CHECK.
> P257: my own fix discarded a return code, so a git warning on stderr became a "backup location"
> and the row printed **OK — safe off-machine** while zero remotes held the commit. The code I
> replaced failed SAFE. **I inverted the failure direction of the alarm I promised to preserve.**

> ### ④ VERIFY A COPY, THEN MOVE IT IN.
> P268: I edited a live instrument in place; `ruff` and `ast.parse` both PASSED (an unbound *local*
> is neither a syntax error nor an F821) and the loop crashed one cycle. **For anything invoked
> every few minutes: write a candidate, parse it, lint it, diff its symbol set, then replace
> atomically.** Never edit a running bash script at all (P250 — bash reads by byte offset).

> ### ⑤ A FIX IS NOT A FIX UNTIL IT FALSIFIES.
> Every RUN 19 fix was proven by making the new assertion FAIL against the pre-fix behaviour —
> in-memory reconstructions, mutation harnesses, throwaway git repos, and where possible **the live
> loop itself**. Two of my assertions were caught as tautologies by that discipline.

> ### ⑥ RE-READ THE CLOCK AFTER ANY LONG WAIT.
> An auditor ran 6 hours; I reported state that was accurate when measured and 6 h stale when
> delivered. **Elapsed time is not observable from inside a turn.**

> ### ⑦ WRITE TO A FILE. ALWAYS.
> Heredocs and inline quoting failed **seven times** across four sessions. Worse, an `&&` chain
> whose first link failed still committed the code without its record. **Verify the ARTEFACT, not
> the exit code.**

---

# §8 STANDING RULES THAT MUST SURVIVE THIS HANDOVER

- **NEVER** read a treatment arm's SEALED-TEST outcome. **NEVER** change a frozen threshold.
- **NEVER** make a check pass by weakening it. On this campaign that is worse than a red board.
- **NEVER** add Claude/Anthropic attribution. **Tamer is sole author.**
- **NEVER** `git clean -x`, `git add -A`/`-u`, or `git stash`. **Stage BY NAME.**
- **NEVER** leave files staged — an auto-committer runs every ~2 min (P251, now fixed with `--only`).
- **NEVER** lower SGE priority; never `qdel -u`. Explicit ids only.
- **NEVER** edit `src|scripts|config|prompts` while live (drift-fenced). `docs/**` is safe.
- **NEVER** put backticks, `$(…)` or heredocs in a `bash -c` string or a `-m` commit message.
- **⛔ NEVER JUNCTION THE ARCHIVE.**
- **PowerShell console is cp1251** — non-ASCII in `print()` CRASHES. The status page is ASCII-gated.
- **⚠ Editing a running loop is INERT** — `cycle_loop.sh`/`publish_loop.sh` need a RESTART;
  `cycle.py`/`publish_status.sh` are re-invoked each iteration and do not.
- **END-OF-WORK, all four:** `scripts/update_handoff.py --suite-status "…"` · a SHORT cursor ▶ NOW
  entry · a DETAILED CHANGELOG block even with no commits · push the backup branch.

---

# §9 EVERY ERROR RUN 19 MADE (P244–P271) — **allocate P272 next**

**Instrument defects found and fixed (18):** P244 S15's rung over the wrong population · P245 the
chain floor decaying with wall-clock · P253 the binding cause picked by hole COUNT not banked RUNG ·
P259 **the RED verdict dead for 4,558 cycles** · P260 `drift=0` from a probe that never ran, and
committed drift never escalating · P261 the confirmatory gate CLEAN from an empty stamp · P262
`guards=2` a constant · P263 a false run-killer that had already fired (908 s vs a 900 s cap) ·
P264 the only full-archive budget never raised · P265 non-atomic `STATE.json` silently disabling
five detectors · P266 a failed probe resetting the drought streak · P267 the ssh layer running 7×
less often than documented · P269 a false "never mutates the campaign" invariant · **P270 the
science monitors O(archive) in MEMORY, projecting to OOM before rung 403** · P271 `arms_full`
excluding the confirmatory line by a silent regex failure · A5 C6 absent from the exit code · A11
`unpushed` raising a routine false ATTENTION · A-f4 a merge silently killing both pushes.

**MY OWN ERRORS (10):** P246 heredoc (7th) · P247 testing a function but not that render USES it ·
P248 my own fix creating vacuous passes · P249 a census double-counting a shared launcher · P250
**editing a running bash script** · P252 three different values for one quantity · P255 a false
alarm raised on my own shell · P256 inline quoting committing code without its record · **P257 a fix
that failed OPEN** · **P268 a live cycle crashed by use-before-assignment**.

---

# §10 ⚠ OPEN ITEMS — 4 ROWS, ALL IN THE LEDGER

**ESCALATED TO TAMER (2):**
* **A6** — `test_h3_singleshot` is folded into the campaign-wide minimum, but R101 defines the result
  over the **11 full-loop models** and h3 is the H3 **control**. Direction: too LOW. Non-binding
  today (h3 reads 568). **A pre-registration question for Tamer and Dr Okhrati, not an ops patch.**
* **W1/D36** — `gate_failure_drift` is a CUSUM against target 0 on a rate of 0.153 with k=0.03, so it
  rises 0.123/sample **without bound and can never clear**. Fix is in drift-fenced `scripts/`;
  registered as **D36**. No campaign result affected.

**OPEN, NOT RUSHED (2):**
* **A-d14** — **the modern D14 path has NO cover.** `campaign.py:1795` returns `ok: False` without
  setting `winners[arm]`, and `:1980` then **silently drops that arm from the entire C4 sweep** while
  `arm_coverage` prints `5/5`. A live, reachable, arm-losing path. **`line_balance` already has the
  right discrimination — point `cycle.py`'s D14 alert at it.** ⚠ This is the highest-value open row.
* **A-attr** — `attrition()` pools across all 11 lines, so its spread is cross-line while the H2
  contrast is within-line (per line: glm 9, nemotron 8, gemini 6). Report-only, but quoted in docs.

**Inherited disclosures (unchanged):** D34 · D35 · **R115 PROVISIONAL for 3 of 10 core groups —
RE-RUN BEFORE SUBMISSION** · `campaign_summary.json` at teardown UNRECOVERABLE ·
`metrics.train_curve.return` 100% NaN · **S4 determinism is VACUOUS in this archive — use the 30/30
farm** · the render order is NOT the level order.

---

# §11 ★★★★★ THE 30-MINUTE LOOP — **PRESERVE IT, AND GO DEEPER**

Tamer's instruction is that the loop continues, **and that the next session dives much deeper,
checks more extensively, and misses nothing from every dimension and angle.**

**Re-arm it immediately** (RUN 19 used cron at `7,37 * * * *`). The prompt is the STEP 0–6 contract
recorded in `CHANGELOG.md [2026-08-04b]` and enforced by `docs/ops/watch/FLAWLESS_LEDGER.md`.

### THE CONTRACT, UNCHANGED
**Every finding is FIXED.** A pass does not end while a fixable row remains open. Exactly three
terminal states: **FIXED** (falsified against pre-fix behaviour), **PROVEN-BENIGN** (with the
measurement), **ESCALATED** (outside this session's authority, with everything around it fixed).
**No row may age three passes.** **Never make a check pass by weakening it.**

### ★ WHERE RUN 20 MUST GO DEEPER — the dimensions RUN 19 did NOT reach
RUN 19 audited `stage_eta.py`, `record_seed_completeness.py`, `session_preflight.py`,
`publish_status.sh`, `cycle.py` and `arm_coverage.py`. **These are still unaudited and each is
load-bearing:**

1. **`scripts/sentinel.py`** — 17 checks, and RUN 19 proved one of them (`gate_failure_drift`) can
   never clear. **How many of the other 16 are structurally incapable of firing?** Apply the P259
   test to every one: *can this check ever change state?*
2. **`docs/analysis/record_validator.py` (R1–R9) and the other six record layers** — they certify an
   irreplaceable archive. **Do their checks have populations that exclude the interesting cases?**
   (That is the §7① lesson, and it has already caught S15.)
3. **`scripts/campaign_guards.py`** — the source of `records=` and `spend=`. Never audited.
4. **`src/cluster/driver.py` / `campaign.py`** — READ-ONLY (drift-fenced). **A-d14 lives here.**
5. **`docs/ops/line_balance.py`** — it is the arbiter for "is a line stuck", and nothing has checked
   the arbiter.
6. **The seven record layers' MEMORY profile** — P270 found the science tools are O(archive) in
   memory. **The record layers walk the whole archive too. Measure them before the archive doubles.**
7. **Cross-instrument agreement** — RUN 19 found S15 and `stage_eta` disagreeing by 60 records
   (both right for their own definition). **Systematically diff every instrument that reports the
   same quantity.**

### ★ THE SPEED COMPONENT — every pass, and MINIMISE THE ETA
Record the SPEED LOG row (rec/h 12 h and 24 h, slots, running/queued, single-line concentration,
chain candidates owed, ETA to rungs 30/403/568). **Compare to the previous row. A drop is an OPEN
FINDING worked to a cause.** But read §6 first: **the ETA is not core-bound.** The genuine levers are
(a) core's serial chain finishing, (b) the four capping lines' `h2_pair` landing, (c) nothing else.
**Never trade correctness, CRN determinism or the frozen design for speed.**

---

# §12 HARNESS LIMITS — MEASURED, NOT ASSUMED

```
qdel <explicit ids>                  WORKS      Stop-Process -Id <pid> -Force   WORKS
New-Item -ItemType Junction          WORKS      Set-ScheduledTask               WORKS
qalter -p <negative>                 PERMITTED, DELAYED, ONE-WAY (prohibited by standing rule)
qalter -p <positive>                 OPERATOR ONLY        qalter -l    REFUSED SITE-WIDE
qalter -js                           REFUSED (js absent from jsv_allowed_mod)
taskkill /PID                        BLOCKED    HKLM registry write             BLOCKED
bash `kill <windows-pid>`            NO-OP (Git Bash has its own pid namespace)
git commit --only <path>             WORKS, and is now REQUIRED in publish_status.sh
```
**⇒ STANDING RULE: TEST THE SPECIFIC COMMAND. Five "BLOCKED" claims have now been disproved.**

---

# §13 THE ONE SENTENCE TO CARRY

**Nine auditors across nine sessions have all found more than the author did, and in RUN 19 three of
the author's own fixes were themselves defective. Send an auditor at anything substantial before you
bank it, falsify every fix against the behaviour it replaces, and verify a copy before you move it
into a live instrument.**
