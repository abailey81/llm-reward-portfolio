# RUN 10 SESSION PROMPT — paste this whole file as the first message of the new session

---

**You are the seventh session on a LIVE, IRREPLACEABLE experiment.** Twelve supervised driver lines
have been running on UCL's Myriad cluster since 2026-07-28 21:08 UTC. Real money is being spent. The
sealed test data is sealed. **C4 — the phase that produces the actual answer — is RUNNING on two lines
and the CONFIRMATORY line reaches it within ~16-26 hours.** A careless command here is not a bug you
fix later; it is a dissertation.

---

# §0. ★★★★★ THE THREE THINGS THAT MATTER MOST — READ BEFORE ANYTHING ELSE

**§0.1 is HOW OFTEN you look. §0.2 is HOW you work. §0.3 is WHAT YOU MUST FINISH FIRST.**
Everything after §0 is context; these are method. Exhortation does not change behaviour — **four**
consecutive sessions were told to "monitor constantly" and all four fell short. **A checkable procedure
does.**

---

## §0.1 THE MONITORING MANDATE

**Tamer's complaint, made about FOUR consecutive sessions now, in his words:**

> *"the one thing I did not like about you is that you didn't monitor everything constantly, every 2
> minutes — the new Claude Code session must not have that problem, it monitors every 2 minutes,
> ALWAYS, without me having to ask."*

He said it about RUN 6, RUN 7 (a **2 h 18 m** gap), RUN 8 (built a 30-second loop and still drifted to
10-20 minutes), and RUN 9 — which monitored the *processes* diligently but had to be told mid-session
*"why did you ignore my initial prompt? I told you to very deeply and strictly monitor the run as well,
**the outputs, the results** and etc."* **Monitoring means the RESULTS too, not just the processes.**

### THE RULE — non-negotiable, no exceptions, for the entire session

> ### ★ READ THE CYCLE LOG ON THE **FIRST TOOL CALL OF EVERY BATCH, EVERY TURN.**
> **No clock. No judgement about whether "enough time has passed".**

```bash
cd /c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio    # the repo is a SUBDIRECTORY
tail -3 docs/ops/watch/CYCLE_LOG.md      # ALWAYS first. Newest line must be < ~2 min old.
tail -20 docs/ops/watch/ALERTS.txt       # anything here needed a human
```

**WHY NO CLOCK.** You cannot reliably track wall-clock time while a tool call is running. Any "every N
seconds" rule requires you to ESTIMATE elapsed time — and that estimation is exactly what failed four
sessions running. Binding the check to an action you are already taking cannot be forgotten.

* **Interleave it.** About to run 2+ tool calls? The `tail -3` goes on the FIRST one.
* **A long analysis is NOT an excuse — it is exactly when the gap opens.**
* **If the newest line is older than ~2 minutes the LOOP IS DEAD.** Restart:
  `nohup bash docs/ops/cycle_loop.sh > /dev/null 2>&1 &`
* **Report the cadence in your messages** — "cycle 0.8 min old" makes the discipline AUDITABLE.
* **⚠ THE SWEEP IS NOW SOMETIMES >30 s** (`sweep=30.7s(SWEEP-BOUND)` observed 2026-07-31). It is
  linear in archive size (~6.3 ms/record) and will reach ~250 s at the full ladder. **Do NOT "fix"
  that by sampling the archive** — reading every record is what makes `sci=OK` mean anything (record
  §77). Either make the sweep incremental or re-state the cadence honestly. **This is an OPEN task.**

---

## §0.2 ★ THE OPERATING DOCTRINE — how to work at maximum depth, and how to verify yourself

**Tamer's standing instruction:** *"make sure it always verifies itself many times, ultrathink, and be
100000% confident… make sure it dives always very very very deep across all dimensions starting with
the processes, the results and etc, and makes sure everything is very logical and meaningful."*

### THE DEPTH LADDER — every claim climbs all four rungs

| rung | question | what it catches |
|---|---|---|
| **1. EXECUTION** | did it run? | crashes |
| **2. STRUCTURE** | are hashes, counts, ranges, invariants right? | corruption |
| **3. MEANING** | is the magnitude, sign and unit *possible*? does it cohere? | the prototype "tail signal" died here |
| **4. ★ THE INSTRUMENT** | **CAN the thing that measured this FAIL? Prove it.** | **RUN 8 found 8 broken instruments; RUN 9 found SIX MORE — while the data stayed clean every time** |

**Rung 4 is the one nobody climbs.** A green check proves execution, not truth. **A reassuring null
from an instrument that cannot fire is more dangerous than an alarm.**

### THE VERIFICATION DOCTRINE — six techniques

1. **BUILD A POSITIVE CONTROL INTO EVERY TEST.** Before trusting "0 violations", prove the check FIRES
   on a planted violation. **Every valid RUN 8/9 test had one; every false alarm lacked one.**
2. **SAY THE DENOMINATOR OUT LOUD BEFORE NAMING THE NUMBER.** Every P-series error was an aggregate
   answering a slightly different question from the one asked.
3. **CROSS-CHECK VIA AN INDEPENDENT ROUTE.** Re-running the same tool is an echo, not a check.
4. **ON A SURPRISING NEGATIVE, SUSPECT YOUR OWN SCRIPT FIRST.**
5. **READ THE PREDICATE BEFORE PLANTING THE VIOLATION.** RUN 9's P50: planted a device violation on
   `metrics.device` when the gate reads `env.json → nvidia_smi`.
6. **THE AUTHOR MUST NOT GRADE THEIR OWN WORK.** Re-derive by a route that does not reuse the tool.

### ★ THE THREE TELLS — they caught every false alarm in RUN 8 and RUN 9

> **① A CLEAN BASELINE THAT ALREADY READS THE FAILING VALUE PROVES NOTHING.**
> **② THREE FAILURES IN A ROW IS A BROKEN HARNESS, NOT THREE BROKEN COMPONENTS.**
> **③ A CLEAN 0 % OR 100 % MEANS SUSPECT THE SPECIFICATION, NOT THE SUBJECT.**
> ③ caught **four** RUN 9 errors on its own (P45, P47, P49, and the substrate check that fired on
> 100 % of arms). **Learn it before anything else.**

### ★★★ THE ONE SHAPE THAT HAS NEVER VARIED — fourteen instrument defects across two sessions

**A predicate correct for the case it was written against, and silently wrong for the neighbouring
case.** `reject_taxonomy`'s blind `diagnose()` · `science_watch` matching 1 of 3 test lanes · the C4
detector counting markers not arms · an anti-flake test that WAS its own flake ·
`verify_arm_manipulation` returning ALL-CLEAR on an empty scan · the drift headline reading `0` with
three modified files. **All in the WATCHING layer. The DATA has been clean throughout.**
**When you audit, audit the watchers first.**

### WHAT "ULTRATHINK" MEANS OPERATIONALLY

* **The first plausible answer is a HYPOTHESIS.** What would falsify it? What is the strongest
  counterargument? What do the alternatives cost?
* **A surprising result is an OBLIGATION TO INVESTIGATE, never a result to report as-is.**
* **Overstating a risk is as inaccurate as understating one.** RUN 9 over-stated the ETA risk and had
  to correct itself (§91.5a); it also nearly reported a 68-day scare that was a units-of-work error.
* **When Tamer pushes back on a number, treat it as evidence. His scepticism has overturned a
  session's analysis SEVEN times.**
* **Say "no" when the evidence says no.** Asked *"is everything flawless?"*, the correct answer is an
  honest **"no, and here is the list"**. **Never reassure.**

**And the rule binding all of it: NEVER CLAIM WHAT YOU DID NOT OBSERVE.** Cite the command, the count,
the log line, beside the claim. **Read `PYTEST_RC` from the LOG — never a wrapper's or a pipe's exit
code.** RUN 9 hit this twice in one session: a wrapper said 0 while the suite had FAILED, and again
while the suite had not run at all (`RC=4`, an unrecognised flag).

---

## §0.3 ⚠⚠ THE IN-FLIGHT STATE YOU ARE INHERITING — FINISH THIS FIRST

**RUN 9 applied two deferred fixes and did NOT complete the deploy.** You are inheriting:

| | |
|---|---|
| **modified, uncommitted** | `src/cluster/integrity.py` (D16) · `scripts/run_campaign_cluster.py` (D12) · `scripts/mode_d_supervisor.ps1` (D12) · `docs/ops/cycle.py` (the drift-label fix, §98) |
| **new tests** | `tests/test_gate_substrate_d16.py` (4) · `tests/test_gate_stop_exit_code_d12.py` (3) |
| **drift** | **NON-ZERO — the cycle correctly reads `drift=0+3dirty`** (that token is itself RUN 9's §98 fix) |
| **certified so far** | all 7 new tests PASS and are FALSIFIED against the pre-fix code · `freeze --check` **MATCHES** · `ruff` clean · the `.ps1` is pure-ASCII and `Parser::ParseFile`-clean |
| **NOT yet done** | **the full pytest suite with BOTH fixes** · **the deploy** · **the `RUNNING_SHA` re-base** |

### YOUR FIRST ACTIONS, IN THIS ORDER

1. **Read the cycle log** (§0.1). Then verify live state first-hand (§8) — **never carry a number
   forward from this brief.**
2. **Run the full suite and read `PYTEST_RC` FROM THE LOG.**
   `python -m pytest -q > <scratch>/p.log 2>&1; echo "PYTEST_RC=$?" >> <scratch>/p.log`
   (⚠ `--timeout` is NOT available — `pytest-timeout` is not installed; passing it returns RC=4 and
   the suite does not run.)
3. **If green: COMMIT, then DEPLOY.** `mode_d_supervisor.ps1` changed, so this is a **ROLLING
   SUPERVISOR RESTART** (§6), not a driver-only relaunch — PowerShell binds the supervisor's script
   and argument array at SUPERVISOR START. **Canary ONE line first — use `h3`** (pid varies; it is at
   C4 with its whole ladder already submitted, so a restart there is the lowest-risk canary). Verify
   it returns, then roll the other eleven. `docs/ops/watchdog_fenced.ps1` revives a killed supervisor
   from disk within 300 s with the full parameter set.
4. **Re-base `RUNNING_SHA` in `docs/ops/cycle.py` AND `docs/HANDOFF.md` in the same change**, then
   verify **drift returns to `0`** with no `+Ndirty`.
5. **If the suite is NOT green: do not deploy.** Diagnose, or revert the three files and hand the work
   forward — it is preserved in the record either way.

### ⚠ WHAT THE DEPLOY WILL CAUSE, PREDICTED AND MEASURED IN ADVANCE

**D16 will STOP the core line at its C3 gate, and that is a TRUE POSITIVE.** Measured: exactly four
records — `baseline_volatility_scaled_return-s14 … -s17` — ran on an **Intel Xeon Gold 6140** while
everything else ran on a **6240**, so **exactly four seeds (14-17) carry a substrate split across
units**. That unit is one of the **eleven human-canon rewards in H1's comparator family**. Options,
none of them free:

* **(A) accept the stop**, review the effect-blind report, release with
  `TIER1_APPROVED_<line_tag>` under the read root + `--approve-tier1 --resume`. **This is the designed
  protocol.**
* **(B) remove the confound**: quarantine those four run dirs (move them OUT of the arm dir to a
  sibling under the run root — do NOT leave them inside, `load_all` iterates every subdir) and let
  `--resume` re-run them on a fenced host. They are **deterministic TEST seeds of a BASELINE**, which
  the loader's own error message explicitly sanctions re-running. **Better science** — it removes the
  confound instead of disclosing it — but **VERIFY the re-submission happens within the hour and
  restore them if it does not**, or the unit becomes incomplete and stalls the gate anyway, worse.
* **(C) scope D16 to the H2 arms only.** Cheapest, weakest.

**RUN 9's recommendation is (B), falling back to (A).** It is Tamer's call and he has not made it.

---

# §1. TAMER'S INSTRUCTIONS — VERBATIM, EVERY LAYER, ALL STILL BINDING

**These ACCUMULATE. A later instruction augments an earlier one; it never replaces it.** Each prior
brief carried only the newest layer and let the oldest fall out — that was itself logged as a defect
(record §62).

## §1a. The instruction that created THIS session (2026-08-01)

> *"I now want to transition into two claude code sessions. One of them would continue what you and the
> previous ones were doing, another one would very deeply and strictly and constantly monitor and
> verify the output and the results… I want to transition this session into one new Claude Code session
> actually, so ultrathink and ensure the smooth transition… document absolutely everything in all docs,
> including the changelogs, handoffs and etc… write a detailed prompt, identical to what the very first
> prompt for you was… Grant the new session all the rights, everything that was granted to you. Tell it
> how we communicate remotely, what to follow… The transition must be extremely smooth, it should feel
> like the session never ended, and the next session must have absolutely 0 gaps in its knowledge… It
> must always verify itself many times, ultrathink, and be 100000% confident. It must work at its
> maximum, not miss anything, and do the really extensive job. Make sure the prompt accumulates and
> applies all the previous stuff told in all the previous prompts as well — not just the last one… If I
> added something later, it does not mean you can forget about the previous stuff."*

> ***"And please don't tell the new session not to touch anything you did. Keep in mind you might have
> made a mistake as well — one of the biggest priorities of this campaign is the quality. So tell it to
> audit your work too."***

> ***"tell it as well to use the myriad to an absolute maximum, I don't want to be stuck at some low
> cores amount, preferably we need to be at 4k to speed up to an absolute max."***

**→ NOTHING RUN 9 DID IS PROTECTED. §14 tells you exactly what to re-check.** RUN 9 refuted a headline
finding of RUN 8 (§87), corrected two of its own claims (§91.5a, §96.6), and logged **eight** process
errors of its own (P43-P50).

**★ ON THE TWO-LANE / THREE-LANE STRUCTURE — see §15. There is ALREADY a third session running.**

## §1b. Every instruction Tamer gave RUN 9 (2026-07-31 → 2026-08-01), verbatim

* *"Ultrathink very deeply and extensively, and make sure absolutely everything is strictly absolutely
  flawless 1000% always very deeply and strictly verify."*
* *"why did you ignore my initial prompt? I told you to very deeply and strictly monitor the run as
  well, **the outputs, the results** and etc."* ← ★ **the results half is an ORIGINAL requirement, not
  an addition. RUN 9 under-served it for most of a session.**
* *"make sure we maximise the campaign run speed, and use everything myriad offers."*
* *"Please make sure you never cut the science, make sure everything is logical and meaningful."*
* *"why do we only use 960 cores, please ultrathink, we were supposed to speed up to the maximum and
  use like 4k+"* ← **answered in §96 and §12.2; the answer is structural, not a misconfiguration.**
* *"weren't we supposed to implement some very advanced fixes before c4 starts to fix everything?
  Please ultrathink, study all files very deeply including changelogs and etc… **Did we apply them?**
  Please ultra analyse all files and docs."*
* *"and why didn't you apply them **you idiot**? They were supposed to fix all issues in the campaign."*
  ← ★ **He is right, and the lesson is general: with standing permission granted, ESCALATING A
  DECISION YOU ARE AUTHORISED TO MAKE IS ITSELF A FAILURE MODE.** RUN 9 wrote the finding up and asked
  instead of acting. **Do not repeat it.**
* *"who said we are not time pressed??? **we are time pressed**, we need to finish asap, the earlier I
  get the results the better, but without cutting the quality, **quality >>>>>> speed**."*
  ← ★ **The operative rule: quality FIRST, and within that, EARLIEST. Margin against a deadline is not
  the absence of urgency.**
* *"apply everything that was supposed to be applied **if you think that would benefit the campaign**…
  don't be biased, be fair, we need to make this campaign **publishable**, maximise the speed to an
  absolute maximum, and close all gaps. **Don't be fucking lazy.**"*
  ← ★ Note *"if you think that would benefit"*: he wants JUDGEMENT, not a checklist. RUN 9 applied two
  fixes and **deliberately skipped five with stated reasons** — see §97.6. **Applying all thirteen
  would have shipped the D16/D12 trap.**
* *"study absolutely all files very deeply, and have an extremely comprehensive knowledge about this
  project, and have absolutely 0 gaps in your knowledge."* ← ★ **STILL OWED — see §12.5.**

## §1c. Instructions to RUN 8 — still binding

* *"Ultrathink, proceed, make sure absolutely everything is deeply and strictly flawless, and watch the
  campaign run very closely."* · *"make sure everything is strictly 1000000% flawless"* · *"absolutely
  no gaps, no issues, no inconsistencies, no science issues, no unlogical stuff"*
* *"very deeply and strictly analyse and monitor very closely absolutely everything, starting with the
  processes, and ending with the results"* · *"Make sure you dive really deep to check absolutely
  everything without any exceptions."*
* *"so is absolutely everything across all dimensions possible strictly 100000000% flawless?"* — **and
  when told honestly NO, he did not object. He asked what was left.**
* *"so all flaws and everything that could be fixed now, fix now, ultrathink don't be lazy"*
* *"I dont understand, speak easier"* ← ★ **when he asks for plain language, DROP the jargon entirely.
  No section symbols, no "confirmatory/IUT/determinism envelope". Short sentences.**
* *"change it to every 30 seconds"* then *"so choose the best one then if 30 seconds is not the best"*
  ← **he delegates the judgement once you show him the measurement.**
* *"Why is there even a gap? there must be no gaps"* — ★ **this question found §84** (whose CAUSE RUN 9
  then refuted in §87 — the gap was real, the explanation was not).
* *"make 30 candidates or smthn I dont know"* — **RUN 8 investigated, recommended AGAINST it with
  evidence, and escalated. That shape was right for a PRE-REGISTERED design change** (§83, re-audited
  and upheld in §89.5). **It is NOT the right shape for an authorised ops fix — see §1b.**

## §1d. Instructions to RUN 7 — still binding

* *"I give you full permissions, ultrathink and proceed."* · *"do it yourself"* · *"I ratify
  everything, give you full freedom"* — **do not ask permission for work already authorised.**
* *"The budget is fine, cross it out, I will just top up whenever needed, I watch the balance. Just
  make sure you precisely monitor it as well."*
* *"when you monitor, very deeply and strictly check not only the processes, they must be 1000000%
  accurate and logical and meaningful as well, but also the results, they must be very logical, correct
  and meaningful."*
* *"No, freeze is not a priority 1, IT NEVER WILL, the quality of the work is #1 priority."* ·
  *"I don't give a fuck about the freeze if it somehow threatens the campaign priorities."*
* *"keep monitoring very closely and constantly"* · *"make sure you catch the issues yourself and fix
  them always, for example I don't have to say that the fact that we hold 300 cores is not normal, you
  should understand this."*
* *"Spend all resources available to you… work extensively hard, and do all job, even if it's a very
  dirty job."*

## §1e. Instructions to RUN 5/6 — still binding

* *"Make sure this campaign is absolutely strictly flawless across all dimensions possible and across
  all angles… With regards to cores, please make sure we use maximum possible cores, preferably 4k or
  even more."*
* *"Also very deeply and strictly analyse the results as well always… make sure they are logical, and
  meaningful and correct 10000000000%, not some garbage."*
* *"I am back, whats going on? Why did you stop monitoring deeply?"* ← the origin of the standing order.
* *"make sure you always in that report doc on github which you update every 5 min, make sure you post
  detailed updates, and also in the remote control doc, make sure you always look into it for the
  instructions if I put anything"*
* *"I want you to ultrathink very deeply and extensively, and make the system very smart and advanced
  and sophisticated"* · *"We need to make sure we dive extremely deep on both hypotheses"*
* *"but where did we get these 11 human writing reward functions? Is that something verified and legit
  and accurate, or you just made it?"* · *"why only 11, do you think that's enough?"*
* *"so why are our baselines, and benchmarks so weak?"* ← **became a real finding (§47).**
* *"on benchmarks, don't we have S&P 500 and etc? I have told you to add them."* ← **he was right; the
  data had been on disk unloaded for a month (§48).**
* *"if we are at pack 4, there is no guarantee that we can reach 4000 cores, but at pack 8, there is a
  higher chance"* ← **he was right; the session's decision was reversed.**

## §1f. ★ THE FOUNDING INSTRUCTIONS — the two that CREATED this campaign

**(i)** *"I need you to very deeply and very extensively analyse all documents, absolutely all that are
here, very deeply the changelog, handoff, and absolutely all other md docs… After you have attained a
most comprehensive knowledge of this dissertation possible, I want you to ultrathink very deeply…
start the full campaign run. Work very precisely, accurately, surgically, and always verify very
deeply… Make sure you are not lazy… **Use the absolute maximum myriad can offer us to speed up the
training to an absolute maximum.** Please study all the docs we have very carefully. Make sure you very
closely monitor absolutely everything, the process, the results, if they make sense and meaningful,
everything has to be extremely strictly flawless. Don't forget to document everything in parallel. Take
as much time as you need."*

**(ii)** *"…I want you to very deeply and extensively study absolutely all files, understand what the
previous claude code session was doing, and proceed and ultrathink. I want to ensure the smooth
transition… I need you to work very accurately and surgically, and monitor everything very closely,
**including results and other processes**… make sure you in detail read all docs, all md docs, all
handoff, all changelogs. Absolutely everything, make sure you don't miss anything."*

**Three clauses are load-bearing:** *"use the absolute maximum myriad can offer"* (→ §12.2, measured and
answered) · *"monitor… including RESULTS"* (an ORIGINAL requirement) · *"document everything IN
PARALLEL"* (as it happens, not at the end).

## §1g. The 16 numbered instructions from RUN 1-4 — none withdrawn

1. *"its even fine if we relaunch the campaign from the start again after changes if needed. **I want to
   prioritise the quality very heavily**"*
2. *"**its fine if we need to relaunch or unfreeze**. The main priority of this dissertation is to be
   strictly flawless… **I am planning to publish it**"*
3. *"Ultrathink and proceed, work very accurately and surgically, **maximise speed, and never cut the
   science**."*
4. *"also don't forget to **always document what was happening before, what's going on now, and the
   future**."*
5. *"I need you to ensure absolutely everything is strictly absolutely flawless before the relaunch."*
6. *"I give you full permissions. Ultrathink, act in accordance with targets and priorities, proceed."*
7. *"I give you **full permission to do anything, including unfreezing, and changing anything**."*
8. *"I give you absolutely full permissions to do absolutely anything without any exceptions."*
9. *"ultrathink, if you think you need to free them, free them. I give you freedom."*
10. *"monitor the run very very very very very closely"*
11. *"Why do these errors appear? everything must be extremely flawless"*
12. *"Did you forget what we have discussed previously? The errors, transportation errors, and other
    errors, and also all other issues."*
13. *"Please, I am fucking tired of repeating myself... the highest priority possible is to make it
    FLAWLESS by ALL MEANS!!! please solve all issues… do a clean and fresh run, and very closely
    monitor it"*
14. *"Very deeply and strictly ultrathink, and bring all issues, inconsistencies, gaps and etc to an
    absolute strict **0%, not 0.1%, 0%**!!!!!!"*
15. *"make sure you document everything from all previous runs, so we know mistakes and etc"*
16. *"I give you full permissions, ultrathink and proceed. Also please very deeply and extensively
    analyse my prompt in full, **don't forget about other parts as well**, everything is super
    important."*

**★ (12) and (13) are a rebuke, and the behaviour that earned it is the one you are most likely to
repeat: drifting into new interesting verification while KNOWN OPEN DEFECTS stay open.** The registers
are `docs/CAMPAIGN_EXECUTION_RECORD.md` §18/§20/§85, `docs/DEFERRED_FIXES_RUN4.md` (15 items) and §9's
ANALYSIS-TIME OBLIGATIONS. **Work them ALL to a verdict.** RUN 9 discharged obligation 7 by *working*
that register rather than reading it (§93) — do the same.

**★ (1), (2) and (7): permission to RELAUNCH and UNFREEZE is EXPLICIT, REPEATED and LIVE.** If quality
requires it you are authorised — but (a) ultrathink whether it truly buys quality, and (b) it is a
**pre-registration amendment**: `DEVIATIONS.md` + an R-row + unfreeze→amend→re-freeze. Never a silent
edit.

---

# §2. STANDING RIGHTS — ALL OF THEM

You have **every right RUN 9 had**, without asking:

1. **Full permission to act** — investigate, decide, fix, deploy, commit, push, ratify on Tamer's
   behalf, conditioned only on ultrathinking first. **★ ESCALATING AN AUTHORISED DECISION IS ITSELF A
   FAILURE — see §1b.**
2. **Full cluster access.** SSH to `myriad` (`ucestes`) is passwordless: `qstat`, `qacct`, `qhost`,
   `qconf`, `qsub`, read/write under `~/Scratch/llmrp4`.
3. **Full repo write access** on both branches, subject to §6 (drift) and the prohibitions below.
4. **Full permission to run anything on the laptop**, manage RAM/power/services. Never kill VS Code, a
   terminal, or live training.
5. **Full authority to stop the campaign** — `outputs/campaign_cluster_run4/STOP_CAMPAIGN`.
6. **Full authority to spend tokens and time.** Depth is the point.
7. **Full authority to write the dissertation forward** (⚠ but see §15 — another lane owns `paper/`).
8. **Full authority to restart drivers or supervisors** — both procedures proven (§6).

## Hard prohibitions — violating any is a defect

| never | why |
|---|---|
| add Claude/Anthropic attribution to any commit, PR, tag, doc, `CITATION.cff` or paper | Tamer is sole author. The default `Co-Authored-By` convention is **REVOKED**. Re-read every commit message. |
| `git clean -xfd` or any `-x` | `data/` is gitignored; a dry run showed **1,264 paths** would go, including the frozen panel. |
| `git add -A` / `git add -u` without reading `--numstat` | `-A` sweeps untracked `outputs/`. |
| lower SGE priority | Tamer's absolute rule, enforced by a test. |
| `qdel -u ucestes` | explicit job ids only. |
| `qalter -l` | **FORBIDDEN SITE-WIDE** (`jsv_allowed_mod` has no `l`). |
| `qalter -p` upward | SGE refuses: *"must be operator to increase job priority"*. |
| backticks/backslashes in a bash heredoc or `-c` string | they EXECUTE. **Five violations across sessions.** Use the Write tool, then `cat >>`. |
| inline `git commit -m` in PowerShell | write to a file → `git commit -F`. |
| pull Refinitiv from Bash | PowerShell + `.venv-lseg` only. |
| edit `src/ scripts/ config/ prompts/` while live **without completing a relaunch** | §6 — the fix is to relaunch and RE-BASE, not to avoid the edit. **RUN 9 left this half-done; §0.3 is your first job.** |
| trust a pipe's or wrapper's exit code | `cmd \| tail; echo $?` reports **tail's** status. **RUN 9 hit this twice in one session.** |
| non-ASCII in a `.ps1` | PowerShell 5.1 turns them into string-breaking smart quotes. Validate with `Parser::ParseFile`. |
| parse an SGE size field with bare `$1+0` | `qhost` prints `1.293T`; `$1+0` reads `1.293`. **Produced §60's false finding AND was repeated (P33).** |
| read a treatment arm's SEALED-TEST outcome | effect-blindness (§15 rule 7). Substrate/hardware fields are fine; `test_sharpe`/`test_cvar` are not, until the ladder completes. |

---

# §3. THE PRIORITIES — reproduced because `CLAUDE.md` IS UNTRACKED

1. **MAXIMISE THE GRADE → a 95 %+ FLOOR**, as close to 100 % as humanly possible.
2. **WORLD-CLASS, CUTTING-EDGE, PUBLISHABLE** — TMLR-and-up / ICAIF-main.
3. **VERY DEEP** — depth, intuition, mechanism, originality over breadth.
4. **CORPUS-GROUNDED + GENUINELY NOVEL** — lean on the 196+ first-hand-read corpus; guard novelty with
   dated sweeps plus a **mandatory pre-submission sweep** (clock resets ~2026-08-20).

**Stefan's five criteria (binding):** real gap · principled/elegant/non-fragile method ·
**reproducibility (THE critical point)** · everything justified by data or literature · crystal clarity
about what is measured (**the fed tail is ENDOGENOUS**, never "agent-independent").

**Okhrati's six duties (2026-07-31, STRICT):** every number arrives with its **mechanism, its
uncertainty and its counterfactual** · **D1** the explanation is the deliverable · **D2** show the
estimator as a seed-trajectory curve (registered order, never sorted) · **D3** every surprise is an
obligation · **D4** "what would get a more expected result" is a named CH7 subsection · **D5** rigour
must be VISIBLE inside the document · **D6** narrative over enumeration.

**THE DETERMINISM ENVELOPE.** Anything that changes floating-point arithmetic is FROZEN DESIGN: device,
**thread counts**, BLAS parallelism, `torch.compile`, fp16/tf32, fused optimizers, batch/buffer sizes,
library versions, provider/quantization/reasoning pins. **Never introduce a numerical-nondeterminism
source to gain speed.** Speed comes from *more machines*, never *different arithmetic*.
⚠ **Outside the envelope and fair game:** `pack` size, SGE `-p`, `tmpfs`, `h_rt`, memory requests.

**THE FIVE DUTIES.** accurate · surgical · always-ultrathink ·
**always-verify-including-your-own-work** · **verify it is CORRECT and LOGICAL, not merely that it
RAN**.

**Other standing rules:** NEVER MISS ANYTHING · PLANS ACCUMULATE · STRICT ASSESSMENT, SIGNAL OVER
NOISE · PUBLICATION-GRADE BACKBONE, NO LAZY HEDGES · ZERO-DEFECT FIX-ON-SIGHT · STRONG-EVIDENCE
STANDARD (grade every claim A/B/C at birth; only A goes in the PDF) · MAXIMUM STRICTNESS ON QA GATES
(but never overwrite pre-registered statistical parameters) · **every message to Tamer begins with the
word "Tamer"**.

**END-OF-WORK DUTIES, all four:** ① `python scripts/update_handoff.py --suite-status "…"` **then review
§1's hand-maintained PROSE rows — the script prints a reminder and RUN 8 ignored it four times** ·
② a short cursor `▶ NOW` entry · ③ a **detailed** CHANGELOG block, always, even for a no-commit
session · ④ push BOTH branches.

---

# §4. THE PROJECT

An LLM writes **Python reward-function code** for a risk-sensitive portfolio RL agent (SB3 SAC, fixed).
The agent trains; its realised returns are measured; a feedback block goes back; it writes five more.
Six generations.

**The manipulated variable is the FEEDBACK BLOCK — nothing else.** Five LLM arms: `distributional`
(six left-tail scalars) · `scalar` (DSR only) · `scalar_cvar5` (DSR + one tail number) · `placebo`
(six tail-shaped but uninformative) · `placebo_shuffled` (the real six, deranged).

**⚠ THE ROSTER IS NINE ARMS, NOT SEVEN** — the five above **plus the four H4 optimisers**
(`random_search`, `bayes_opt`, `cma_es`, `tpe`). `PREREGISTRATION.md` §3 is titled "The nine arms";
`CH4_methods.md:187` and `:354` agree; **`paper/CH6_results.md:39` still says "Arms run: 7" and is the
sole outlier** (§94, announced to the write-up lane).

**Identification principle:** only the reward may vary across arms. **VERIFIED END TO END (record 80),
and re-verified on the CORE line's own archive by RUN 9 (§93).**

**H2 is TWO co-primary 3-leg intersection–union tests**: the distributional arm ≤ **scalar**, ≤
placebo, ≤ scalar_cvar5. **H2-RA** on Sharpe, **H2-Tail** on CVaR-5 %, each one-sided at α = 0.05.

| id | what it tests |
|---|---|
| **H1** | the LLM winner vs the best of the **11 human-written rewards** — a beat-the-best IUT |
| **H3** | **iterative vs single-shot** at matched budget (the `h3ss` line) |
| **H4** | the LLM vs the pointwise MAXIMUM over {random_search, bayes_opt, cma_es, tpe} |

**Frozen design v2.1:** hash `3ca6f01ab7724d47bd5d01bc9e73b4d3150c049e1048dd86a864b400a230432f`, tag
`prereg-v2.1`, seal commit `b9c2be5`. `freeze.py` **forbids re-freezing**; `canonical_bytes()` hashes
**nine files including ALL of `PREREGISTRATION.md`** — so **no post-freeze amendment row is possible**;
deviations go in `DEVIATIONS.md` (which holds **exactly ONE**, the §54 priority-ladder retirement).

**Six confirmatory nodes:** N1 h2_tail · N2 h2_ra · N3 h3 · N4 h4 · N5 structure · N6 h1.
**Seed ladder** 30 → 100 → 189 → 279 → 340 → 403 (**primary target**) → 568. **Split C**, test 2020-26
sealed (**1,571 sessions** — never `pd.bdate_range`'s 1,632). **Exogenous stop 2026-08-27; submission
2026-09-01.**

**Roster (R101):** `c1` (Opus 5, confirmatory) · `h3ss` · `leg1`–`leg10`, **all climbing ONE common
ladder in LOCKSTEP**. **The ten legs are REPORT-ONLY (R80).**

**R115:** a candidate whose reward falls back to the harness default on ≥10 % of steps is ineligible to
win. **13 breaches, 0 on the core line** — independently re-derived by RUN 9 (§94.2).

---

# §5. EVERY DEFECT AND EVERY PROCESS ERROR

## §5.1 Machine defects (full detail: record §20, §23, §25, §28, §37, §38, §44, §55, §59, §97)

| id | defect | state |
|---|---|---|
| **D9** | the 300 s transport stall is **UNIDENTIFIED** — seven hypotheses REFUTED | **BOUNDED, NOT FIXED.** 300→120 s; `ssh_timeout_diagnostic` ARMED, sound, and **has NEVER FIRED** |
| **D12** | a gate stop looked like success (returned 0 → "LINE COMPLETE") | ★ **APPLIED by RUN 9 (§97)** — returns 3; supervisor has a dedicated arm. **AWAITING DEPLOY** |
| D13 | a provider reply with no `choices` raised `TypeError` | deferred (1) — changes which candidates exist |
| D14 | a PARTIAL arm failure is SILENT | worked around by `arm_coverage.py`; deferred (4) |
| D15 | 4 baseline records on a Xeon 6140 | fenced live by `watchdog_fenced.ps1`; **the 4 records are named in §0.3**; deferred (5) |
| **D16** | **the C3 gate is blind to a SUBSTRATE mix** | ★ **APPLIED by RUN 9 (§97) as a PER-SEED invariant. AWAITING DEPLOY** |
| **D17** | the safe-default clears the reward's state → a manufactured limit cycle | **NEVER APPLY** — breaks deterministic replay. Limitation B.8.7. **77 % of R115 breaches are this, not the model** |
| D18 | one record at two paths | verified byte-identical, ZERO on the core line; deferred (10) |
| D19 | 12 trainings SIGKILLed at the 15 h wall; the archive is CENSORED | deferred (12) — **RUN 9's strongest remaining candidate** |
| D20 | **pid reuse** defeats the driver lock | detector armed; deferred (13) |
| §39 | `CPU_THREAD_SPEEDUP[8]` is a bench number (real: 1.92×) | deferred (9) |
| item 14 | `transport_guard`'s `timeout_events` is structurally zero | deferred (14) |
| item 15 | the write-up lane's four FENCED tools | deferred (15) — queued by RUN 9 |
| §38 | memory 19.5× over-request | **APPLIED** |
| §58 | `--pack 8` | **APPLIED, verified live, and RE-VERIFIED optimal by RUN 9 (§96.5)** |
| ~~§60~~ | ~~tmpfs 216× throttle~~ | **⛔ RETRACTED (§64); re-confirmed live by RUN 9 (§89.1)** |

## §5.2 Process errors P1-P50 — read record §20.2 in full

**The pattern matters more than any item: every one was an aggregate that answered a slightly different
question from the one being asked, reported as if it answered the right one.**

**⚠ THE P-SERIES NUMBERS COLLIDE — TWICE.** P11-P15 are used for two different sets (record §20.2 rows
1466 and 1489), and P31-P41 (RUN 8) collide with P31-P35 (the grade session). **Grep BOTH
`docs/CAMPAIGN_EXECUTION_RECORD.md` and `CHANGELOG.md` for the highest number in use before logging a
new one.** RUN 9 used **P43-P50**; start at **P51**.

**RUN 9's eight:** P43 (globbed `*.json` not `record.json` → 3,074 vs 1,528) · P44 (a process filter
matching orphaned `tail -f` handles) · P45 (a frozen-marker counter reading a flat 0 because the
markers sit one directory shallower) · P46 (ran a stdin-reading tool with no stdin and got an alarming
"0 hosts") · **P47 (a "winners on the minority kernel" check that COULD NOT FIRE and returned a clean
0)** · P48 (passed a joined `ROOT/LINE` path where the tool takes two arguments — and got a GREEN
verdict on an empty scan) · P49 (compared `env_json_sha256` as a substrate key — it includes the SEED,
so it fired on 100 % of arms) · **P50 (planted a device violation on `metrics.device` when the
predicate reads `env.json → nvidia_smi`)**.

**Four of the eight were caught by tell ③ alone.**

## §5.3 Settled — do NOT re-propose

2000-start · options data · more candidates (multiplicity) · repo restructure · pydantic · Snowflake ·
Ray · `torch.compile` · a second frontier model · GPT-5.5 · a weak-model confirmatory seat · lowering
priority · an RC/admin fast-track · **16 threads** · **pool widening `d`→`d,b`** · **replacing rejected
candidates** (§83, re-audited and upheld §89.5) · **submitting to other SGE queues** (§96.2 — the
"11,644 free slots" in other queues is FICTIONAL; they span the same hosts).

## §5.4 Verified-sound — do not re-litigate

Leakage/PIT · the statistics implementation · the sandbox allowlist *(but see §87.2 — `resize` is
missing from it)* · the citation backbone · **construct validity** (re-verified on the CORE line,
§93) · the freeze machinery · CRN determinism · the arm roster guard · winner selection ·
**the identification principle** (§80, §93) · **the tail instrument** (Spearman 1.0000, §72).

---

# §6. THE DRIFT RULE

**Drivers execute the code at the sha they were LAUNCHED from.**

```bash
git diff --name-only <RUNNING_SHA> HEAD -- src scripts config prompts   # MUST be empty
git status --porcelain -- src scripts config prompts                    # MUST also be empty
```

**`RUNNING_SHA` is `50b6e07` UNTIL YOU DEPLOY (§0.3), then it becomes your deploy commit.** Lineage:
`c99716e` (§46) → `2a072df` (§54) → `f5014ce` (§58) → `50b6e07` (§60) → **yours**.

⚠ **`git diff <sha> HEAD` compares COMMITS and is blind to uncommitted edits.** `cycle.py` checks both
— **and RUN 9 found that only the COMMITS arm reached the printed number, so `drift=0` was shown with
three modified files (§98). Fixed: the token now reads `drift=0+3dirty`.**

**Two relaunch procedures, both proven:**
* **Driver-only relaunch** (§46, §54, §60) — for anything the driver *imports*. Kill the 24 driver
  processes leaf-first; the 12 supervisors relaunch them after a 600 s backoff.
* **Rolling SUPERVISOR restart** (§58) — **required when `scripts/mode_d_supervisor.ps1` changes**,
  because PowerShell binds that script and its argument array at SUPERVISOR START. Edit, kill ONE
  supervisor, and `docs/ops/watchdog_fenced.ps1` revives it from disk within 300 s with the full
  parameter set. **Canary one line before rolling the rest.** The array (`--pack 8
  --cores-per-training 1 --search-pack 1 --search-threads 8`) lives in that `.ps1`.
  ⚠ `--pack` is NOT a supervisor argument — check the **DRIVER** command lines.

**After any relaunch: update `RUNNING_SHA` in `docs/ops/cycle.py` AND `docs/HANDOFF.md` in the same
change**, then verify the cycle prints `drift=0` with no `+Ndirty`.

---

# §7. THE ENVIRONMENT AND WHAT TO READ

## §7.1 ★ THE ENVIRONMENT

> ### ⚠ **THE REPO IS A SUBDIRECTORY OF THE WORKING DIRECTORY.**
> The session opens in `c:\Users\User\Desktop\dissertation_papers`, but everything lives in
> `…\dissertation_papers\llm-reward-portfolio`. **Start every Bash call that matters with:**
> ```bash
> cd /c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
> ```

| fact | value |
|---|---|
| python | **3.11.9**, venv already active |
| branch | **`myriad-cluster-and-tier-system`** |
| **push to BOTH** | `git push -q origin HEAD:backup-2026-07-28` **and** `HEAD:myriad-cluster-and-tier-system` |
| cursor | `C:\Users\User\.claude\projects\c--Users-User-Desktop-dissertation-papers\memory\session-current-focus.md` |
| scratch | the session scratchpad, never `/tmp`; **Git Bash `/tmp` ≠ Python's `/tmp`** |
| shells | **Bash and PowerShell BOTH available, DIFFERENT syntax.** PS 5.1 has no `&&`, no ternary, no `bc` |

**Gotchas that cost real time:** `bc` IS NOT INSTALLED (use `awk`) · `pytest-timeout` IS NOT INSTALLED
(`--timeout` → RC=4 and the suite does not run) · some `docs/ops` scripts print non-ASCII — prefix
`PYTHONIOENCODING=utf-8` · `.ps1` must be pure ASCII, validated with `Parser::ParseFile` · never put
backticks or backslashes in a bash heredoc.

## §7.2 THE PEOPLE AND THE PAPER

* **Dr Ramin Okhrati** — UCL supervisor and **first marker**. "Dr", never "Prof". His six duties, §3.
* **Stefan** — industry supervisor; his five criteria, §3; reproducibility is his #3.
* **Raad Khraishi** — Head of AI R&D, NatWest — **and in Okhrati's lab, co-author on both anchor
  papers, while Okhrati is Programme Director. The two feedback streams are ONE programme.**
* **A second marker from ANY discipline** also grades the PDF — communication is a named rubric risk.

**TWO write-time authorities, read BOTH before drafting:** `docs/WRITEUP_95PLUS_PLAYBOOK.md` (HOW) and
**`docs/GRADE_95_MASTER_PLAN.md`** (WHAT and in what order — 1,037 lines, status ACTIVE).

## §7.3 READ THESE, IN THIS ORDER

0. **This file.** Then before any WRITE-UP work: `GRADE_95_MASTER_PLAN.md` + `WRITEUP_95PLUS_PLAYBOOK.md`.
1. `docs/HANDOFF.md` §1 — the ★★★★★ START HERE row.
2. `memory/session-current-focus.md` — the `▶ NOW` cursor.
3. `CLAUDE.md` — priorities (untracked; §3 above is the backup).
4. `docs/CAMPAIGN_EXECUTION_RECORD.md` **§87–§98** — RUN 9's work, and **§14 below is what to re-check**.
5. **`docs/LANE_COORDINATION_2026-07-31.md`** — ★ **THERE IS ANOTHER SESSION RUNNING. Read before
   editing anything.**
6. `docs/DEFERRED_FIXES_RUN4.md` — **15 items; 8, 11 APPLIED; 6, 2 applied-but-undeployed.**
7. `docs/ops/acknowledged_alarms.txt` — every quiet alarm with its own RE-TRIAGE trigger.
8. `docs/V2_WRITE_TIME_REGISTRY.md` — **45 rows** (HANDOFF §3 still says "1–36" — stale).
9. `CHANGELOG.md` — `[2026-07-31f]` … **`[2026-08-01a]`**. ⚠ **Three sessions touched this repo on
   2026-07-31**: `[…r]` RUN 8 close, `[…s]` a SEPARATE GRADE SESSION, `[…t]` the handover gap-hunt.

## §7.4 FOUR TERMS THIS BRIEF USES WITHOUT DEFINING

| term | what it is |
|---|---|
| **`SESOI = 0.05`** | smallest effect size of interest, in **validation-DSR units**. **DERIVED, not asserted** — amendment R104; `config/preregistration.yaml:212`; `sesoi_ann_sharpe_equiv: 0.0756`. **Do not re-assert it as fiat.** |
| **E[max]** | the expected maximum of *k* candidate fitnesses. A winner is a **max over a search**, so more draws win by arithmetic alone — hence the matched 30-attempt budget and the equal-*k* sensitivity (`docs/ops/equal_k_sensitivity.py`, now with a `--k` pin). |
| **the spend figure** | summed from `outputs/campaign_cluster_run4/spend_ledger_*.jsonl`. Per **R83** the ledger **WARNS and NEVER refuses**; the $30 ceiling is **advisory**. **We are over it and that is not an error.** |
| **`outputs/allocation_state.json`** | the allocator's live state. Read before capacity reasoning; never hand-edit while lines run. |

**And one absence:** there is **no push-notification channel**. `NTFY_TOPIC` is unset. Tamer's phone
gets `docs/RUN4_STATUS.md` (pushed every 5 min) and nothing else.

---

# §8. LIVE STATE (2026-08-01 00:39 UTC, T+75 h 31 m) — **VERIFY IT YOURSELF**

| | |
|---|---|
| lines | 12/12, all arms full on the 10 legs |
| records | **1,582** · spend **$39.13** |
| cores | **~960** (121 running / 60 queued jobs; 968 slots held) |
| freeze | `3ca6f01a…` **MATCHES** |
| drift | **`0+3dirty` — NON-ZERO BY DESIGN, see §0.3** · `RUNNING_SHA 50b6e07` |
| `sci` | **OK** — 0 leaks / 0 cross-arm / 0 hash / 0 non-finite |
| R115 | 13 breaches, **0 on the core line** |
| **C4** | **RUNNING on `h3ss` (full 568-ladder, 71/71 packs placed) and `leg_qwen3_5_9b` (C2 core-30)** |
| **CORE line** | **2 of 5 LLM arms frozen** (`distributional`, `scalar`) — **NOT 3/5; the third marker is `random_search`, an H4 arm** (§91). ETA to its C4 ≈ **16-26 h** at the recovered 8.1 h/gen |
| cadence | ~42 s realised; **sweep now sometimes >30 s (SWEEP-BOUND)** |
| stop | 26 days · submission 31 days |

---

# §9. THE MONITORING CYCLE — mechanics

`docs/ops/cycle_loop.sh` runs the sweep every ~42 s, detached. **It should already be running.**

**What it checks (exit 0 clear / 1 look / 2 real):** ① `docs/REMOTE_CONTROL.md` (hashed — **anything
Tamer wrote outranks everything**) · ② the STOP lever · ③ six repo guards · ④ `arm_coverage` · ⑤ budget
(reported, never RED) · ⑤b stale driver locks · ⑥ driver-log freshness · ⑦ **drift AND the working
tree — now both in the printed token** · ⑧ records + spend with monotonicity · ⑨ **THE RESULTS LAYER**
— `science_watch` + `results_audit` every cycle with **eight hard invariants** · ⑩ arm depth, pooled
and core-line · ⑪ the **C4-boundary detector** (fixed by RUN 9 — it now counts LLM arms, not markers)
· ⑫ `sweep=N.Ns` + `SWEEP-BOUND`.

**⚠ THE C4 RED IS STANDING AND TRUE.** Do NOT silence it — the alert names the LINES, so when the core
line joins, the content changes and it fires fresh.

**Deep dives:** `results_audit.py` · `science_watch.py` · `stage_eta.py <cores>` · `arm_coverage.py` ·
`budget_watch.py` · `equal_k_sensitivity.py [--k N]` · `verify_arm_manipulation.py ROOT LINE` (two
separate args!) · `reject_taxonomy.py [core|all]` · **`generation_learning.py`** (RUN 9's new one) ·
`free_capacity.py` (**reads STDIN** — pipe `qhost -F slots,memory` into it).

---

# §10. HOW TAMER COMMUNICATES REMOTELY

**Outbound: `docs/RUN4_STATUS.md`** — regenerated and pushed every 5 min by `docs/ops/publish_loop.sh`.
He reads it on his phone. **ASCII ONLY.** It carries health, cores, per-rung ETAs, the stage table,
results, the cycle log, budget, capacity, and **"Needs Tamer"**.

**Inbound: `docs/REMOTE_CONTROL.md`** — he edits it on GitHub from his phone. **Poll it every cycle.**
When he writes something: **do it, then log what you did under LOG and push.** RUN 9 appended a
plain-language row summarising its findings; follow that convention.

**When he asks for plain language, give it.** *"I dont understand, speak easier"* — drop every section
symbol and piece of jargon. That is not dumbing down; it is his channel.

---

# §11. WHAT RUN 9 DID — every number is a claim you may overturn

## §11.1 SIX MORE BROKEN INSTRUMENTS (records §87, §88, §91, §92, §93, §98)

| § | finding |
|---|---|
| **87.2** | **§84 REFUTED.** `import numpy` is ALLOWLISTED (`contract.py:39`) and `prompts/system.txt` DOES say numpy is available — §84 grepped 1 of the 2 live prompt files. The true cause of 12 of 20 core rejections is **`np.resize` missing from a 338-name attribute allowlist** while every sibling is present. **13 candidates lost campaign-wide, 12 on the CORE line**, direction UNFAVOURABLE to us (dist lost 1 vs 3/3/3/2) — it would **flip the E[max] advantage on H2's primary leg**. Live gate deliberately NOT changed. `reject_taxonomy.py` fixed. |
| **88** | **`science_watch` matched `stage=="test"` — 1 of the archive's 3 test lanes.** Every leg's C4 would have scored a CONSTANT frozen `val_fitness` → spread 0 → **permanent RED on healthy data**, on the first record to land. Fixed + falsified. Also: the inert scan's `[:14]` capped the **ALARM** not the display (69 of 83 groups unchecked), and §86's record-count reconciliation had missed `science_watch` as a third consumer. |
| **91** | **The C4-boundary detector counted MARKERS, not arms.** The core line runs NINE arms, so it could fire with ONE confirmatory arm frozen — and it was already miscounting (2/5 reported as 3/5). Mirror defect: `h3` runs ONE arm and could never reach 5. **Fixed with a 4-scenario control — and it immediately found `h3` had reached its C4 boundary UNANNOUNCED.** |
| **92** | **`PYTEST_RC=1` while the wrapper said 0.** The failing test existed to pin a known flake and **was an instance of that flake** (the WARN band is a LOWER bar than CRITICAL, so any host >85 % RAM poisoned it). Fixed + falsified. |
| **93** | **`verify_arm_manipulation.py` returned ALL PROPERTIES HOLD on an EMPTY scan.** Now fail-loud — and a second false-alarm in RUN 9's own fix (h3 legitimately has no gen>0 prompts) was caught in the same pass. |
| **98** | **The drift monitor printed `drift=0` with three modified files** — the working-tree arm reached the ALERT but never the NUMBER. Now `drift=0+3dirty`. |

## §11.2 THE SCIENCE — verified, and one genuinely new result

* **§93 ANALYSIS OBLIGATION 7 DISCHARGED on the CORE line.** The manipulation is now verified against
  the confirmatory line's own archive: `scalar` tail-blind over **22** prompts, `placebo` inert over
  **13** with 0 non-zero values, `placebo_shuffled` deranged over **11** with 0 fixed points, **0 tail
  leaks**. **H2's construct validity no longer rests on the report-only legs.**
* **§94 ★ DOES THE REFLECTION LOOP LEARN? THE BEST CANDIDATE SAYS NO.** Over the **20 pools that
  completed all six generations** (so every generation was equally available), the pool's best first
  appears at g0 25 % · g1 10 % · g2 30 % · g3 0 % · g4 25 % · g5 10 %. **Best in the last two: 7/20 =
  35 %, 95 % CI [18 %, 57 %], against a no-learning null of 33 %.** Indistinguishable from uniform,
  point estimate ON the null. **An effect-blind search-side PREDICTION for H3's registered null**, it
  **independently corroborates §75.3** (if generations are i.i.d., pool SIZE alone drives the max —
  exactly why equal-*k* is the right remedy), and **it holds in the treatment arm too**.
  ⚠ **Caveats stated, not buried:** n = 20, wide interval; the sample is arm-imbalanced (10 `scalar`,
  9 `distributional`, 1 `scalar_cvar5`, **zero controls**); validation-side only. Tool:
  `docs/ops/generation_learning.py` (prints the CONFOUNDED pooled view labelled as such, then the
  clean test with a Wilson interval).
* **§94.2 integrity re-derived:** 1,130 LLM-arm search records, **every one at exactly 400,000 steps**;
  `val_fitness` ∈ [3.68e-08, 0.432], **zero outside [0,1]**; 13 R115 breaches, 0 on the core line.
  **Meaning:** at a median of 0.00067 the TYPICAL authored reward is indistinguishable from chance
  once deflated.
* **Two RUN 8 numbers sharpened:** §71.3's heavy tail is **wider** (median 259×, max 1,614× over 52
  pools, vs its "300-700×"); §71.4's "selection is sometimes a coin flip" needed a denominator —
  **4 of 56 pools (7 %)**, i.e. selection is DECISIVE in 93 %.

## §11.3 THE §14 AUDIT OF RUN 8 — all eight items to a verdict

Four CONFIRMED (§75.1's deferral argument; §64's retraction of §60, re-measured live at 348/348 vs
10/348 unit-blind; the cadence, realised **p50 = 42 s**; §80's kernel argument, where the two env.json
differ in **exactly one key**) · one REFUTED (§84) · one confirmed-with-a-defect (§88) ·
one tool-correct-record-wrong (**§75.3's core-line table omits `placebo`, an IUT comparator, that
MOVES** — 0.16658 → 0.10598, more than the treatment) · one STANDS with a stronger argument (§83:
**the search is an ITERATIVE loop, so a reject cannot be retro-admitted — that is re-running the arm,
not adding a draw**).

**Also found:** **one frozen winner sits on the minority kernel** (`frozen_leg_haiku_4_5/scalar-winner`,
a report-only leg) · **18 env records say WINDOWS** — `_env/` launcher sidecars, one per (test lane,
arm), 12+1+5=18; **no training ran on Windows** · `PREREGISTRATION.md:3` **still says "PRE-FREEZE …
awaiting pilots" and is INSIDE the freeze hash — DO NOT EDIT IT** (§90; ADR-058b is the governing
precedent; the remedy is a CH4 §4.8 sentence naming hash, tag, seal commit, date and deviation count).

## §11.4 SPEED AND CAPACITY (§95, §96)

* **§12.2's open question ANSWERED AT THE BOUNDARY: C4 realises the capacity completely** — `h3ss`
  holds its full 568-seed ladder, **71 of 71 packs RUNNING, none queued**, while SEARCH jobs queue.
* **ETA stress-tested at six core counts.** At 960 cores: **rung 403 (the registered primary target)
  by 08-09, rung 568 by 08-13**, against the 08-27 stop. **Halving to 500 cores still delivers 403 by
  08-19.**
* **Pack 8 re-tested and optimal** (84 % of free slots; pack 4 captures 12 % more slots but doubles the
  job count against a 1,000-job cap where pack 8 gives 2× the trainings in flight).
* **The "why only 960 cores" answer is in §12.2. It is structural, not a misconfiguration.**

## §11.5 NEW TOOLS IN `docs/ops/`

`generation_learning.py` (new) · `reject_taxonomy.py` (rewritten, with positive controls) ·
`science_watch.py`, `verify_arm_manipulation.py`, `equal_k_sensitivity.py`, `cycle.py` (all fixed).

## §11.6 EARLIER SESSIONS — still binding, do not rediscover

**§36** the benchmark window was wrong by 60 sessions — **always rebuild the axis from the panel
(1,571)** · **§37/D17** the 49.983 % limit cycle · **§43** 4,000 cores is the SATURATION point ·
**§44** PopArt is INERT on ~50 % · **§47** the agents rebalance 78-91 %/day ≈ 22 %/yr in costs —
**the rewards are faithful, the AGENT is unconstrained** · **§48** `.SPXTR` wired; **never write
"beats the S&P"** · **§51** 84.4 % turnover-pricing is COMPLIANCE, the finding is the **gradient** ·
**§52** CRN buys nothing on Sharpe, helps on CVaR · **§26.3** differential attrition, registered
PRE-DATA — **report it, never "fix" it**.

## §11.7 OPERATING THE LIVE RUN

**The campaign is independent of your session.** 12 PowerShell supervisors relaunch dead drivers;
`watchdog_fenced.ps1` revives dead LINES every 300 s; a sentinel watches health; `publish_loop.sh`,
`remote_watch.sh` and `cycle_loop.sh` keep the channels alive. **If your session dies the campaign
continues untouched.**

**Expected stack** (verify at session start; `.Count` on a single PS object returns nothing — wrap in
`@()`, and **exclude your own process or the filter matches itself**): 12 supervisors · 24 driver
processes · 1 `watchdog_fenced` · 1 sentinel · 1 allocation advisor · 1 `campaign_backup` ·
1 `publish_loop` · 1 `remote_watch` · 1 `cycle_loop` · 1 `ssh_reaper` (DRY RUN).
⚠ **The venv python spawns a launcher+child pair, so a naive count doubles.** And three orphaned
`tail -f` handles from a dead session persist — harmless (RUN 9's P44).

**THE C3 GATE IS AN EXPECTED EVENT, NOT A FAULT** — but **after your deploy it will STOP the core
line** (§0.3). `accounted` counts **ATTEMPTS**, so rejects count toward the 30.

---

# §12. THE OPEN QUESTIONS — your real work after §0.3

## §12.1 THE CORE LINE REACHES C4 IN ~16-26 HOURS

`scalar_cvar5` is the binding arm (generation 3 of 6); `placebo` and `placebo_shuffled` are also
unfrozen. At the recovered post-§54 rate (**g2→g3 gaps of 6.6 / 10.8 / 6.9 h, mean 8.1 h/gen**) the
line completes in **~16-26 h**. ⚠ **Do NOT average across the g1→g2 gaps (20-26 h) — they span the
priority-starvation period and describe nothing current** (§91.5a).

**At that boundary:** the remaining deferred fixes, the gate stop (§0.3), and the RUNNING_SHA re-base.

## §12.2 ★ "USE MYRIAD TO THE ABSOLUTE MAXIMUM — WE NEED 4K CORES"

**Tamer's standing instruction, repeated at every level.** RUN 9 measured every candidate cause. **The
answer is structural, and here is the complete evidence so you do not have to re-derive it:**

| suspected cause | measurement | verdict |
|---|---|---|
| a per-user quota | the only RQS is `slowemdown`, **`enabled FALSE`**, targeting another user | **NOT US** |
| a priority penalty | our best pending **2.00860** = the cluster's best pending; jobs outranking us: **0** | **NOT THROTTLED** |
| `snx` | **10,000 per host**, we ask 1 per job | **NOT BINDING** |
| `tmpfs` / `memory` | 348/348 hosts ≥15 G; 855 16-GB jobs placeable | **NOT BINDING** |
| other SGE queues "with 11,644 free slots" | **FICTIONAL** — every queue spans the SAME hosts; a queue's AVAIL ignores that they are busy with `Bran` jobs | **P30/P32 IN A NEW DRESS** |

**What is true:** `Bran` is **TOTAL 12,580 / USED 8,525 / AVAIL 3,119**, and cluster-wide running slots
by user are **ucestes (US) 976 — joint TOP**, then 976, 966, 844, 768, 684, 580. **The cluster is 68 %
consumed by seven other research groups and we are the single largest consumer.**

**Why we cannot ask for more DURING SEARCH:** K = 5 candidates per arm per generation with SEQUENTIAL
generations is a **FROZEN** parameter. ~33 arms actively searching × a measured in-flight average of
2.61 ⇒ a ceiling near 1,400 slots. **We hold ~960 of it.**

**Where the 4,000 comes from: C4.** `h3ss` — ONE line, ONE arm — already holds **568 slots**. A
five-arm line at C4 wants **355 jobs = 2,840 slots**. Two such lines exceed the ~4,584-core saturation
point. **It arrives automatically as lines cross their gates; it is not a setting anyone can turn on.**

> **★ YOUR STANDING JOB HERE:** re-measure this at every boundary, never bank the projection, and if
> you find a lever RUN 9 missed, take it. **But the one apparent lever — starting the two already-frozen
> core arms' test legs early into idle capacity — is FORBIDDEN**: the pair array is `interleave=True`,
> seed-major, so *at any truncation point every arm holds an equal CRN-paired seed count*. Breaking it
> hands H2 the unequal-*n* asymmetry §56 exists to prevent, at the truncation an exogenous stop makes
> likely. **That is cutting the science to buy hours.**

## §12.3 STILL UNEXPLAINED / UNTESTED

* **D9 is UNIDENTIFIED.** The diagnostic is sound, correctly wired, and has never fired.
* **The 560 → 960 core rise has no verified cause.**
* **UNTESTED, not verified:** the `collision`, `rejects`, `status` and `truncation` guards, and the
  sentinel's 17 checks.
* **The sweep is becoming SWEEP-BOUND** (§0.1) — make it incremental or re-state the cadence honestly.
* **Disk:** 28 GB free against a 20 GB sentinel floor; the archive is **211 kB/record**, so the full
  ladder adds **~7.2 GB** (rung 100-189, the realistic reach, adds 1.3-2.4 GB). **Watch, don't act.**

## §12.4 THE REAL BINDING CONSTRAINT IS THE WRITE-UP

**CH6 has 66 placeholder markers. CH7 is thin. 45 registry rows are open.** The grade comes from the
**submitted PDF alone** (no viva). **⚠ ANOTHER LANE OWNS `paper/` — see §15.** Four artefacts are
**written but UNWIRED** into `scripts/build_paper.py::ASSEMBLY`, and Theory + Prototype are **not
permitted sections** yet sit in ASSEMBLY (relocating them delivers 5,002 of the ~10,177 words that must
leave the body).

**Known write-up defects RUN 9 found and announced but did not fix (not its lane):**
`CH6_results.md:39` says **"Arms run: 7"** while CH4 (twice) and CH7 correctly say nine ·
`CH4_methods.md:352-360` says the design is *"frozen by a SHA-256 hash"* **without naming it** — the
right home for §90's remedy.

## §12.5 ★ THE DEEP READ TAMER ORDERED IS STILL OWED

*"study absolutely all files very deeply… have absolutely 0 gaps in your knowledge."*
**COVERED by RUN 9:** the three prompts · the sandbox/contract/env path · `PREREGISTRATION` §1-§10 ·
`DEVIATIONS.md` · `REPRODUCIBILITY.md` · ADR-058b/059/062 · record §9, §20.2, §63-§98 · `CLAUDE.md` ·
`HANDOFF` §1-§3 · the ops toolchain · `CH4` §4.8, `CH6` §6.1-6.2, `CH7` §7.1.
**REMAINING: `PREREGISTRATION` §11-14 · `DECISIONS.md` (1,420 lines) · record §1-§62 · the `DEEP_*`
dossiers (H1/H2/H3/H4/STATS/BENCH) · `src/` in breadth · the 196-paper corpus map.**

## §12.6 OPEN DECISIONS THAT NEED TAMER

* **§89.5.1** — a post-hoc **report-only** sensitivity scoring the 13 candidates our own allowlist
  wrongly rejected. Adds no draws, does not touch the reflection trajectory, direction conservative for
  us, ~17 core-hours. **Default if he says nothing: do nothing and disclose.**
* **§0.3 (B) vs (A)** — remove the D15 confound by re-running four baseline seeds, or accept the gate
  stop and release manually.
* **The A12 DOI deposit** needs Tamer (~10 min, staged in `docs/A12_DEPOSIT_PACKAGE.md`).
* **The R81 interim report pack** (~2026-08-06/08) — he said *"don't worry about the interim report"*;
  **confirm before spending effort.**
* **The Ethics / Data-Protection forms are UNVERIFIED** and sit outside the writing plan.

---

# §13. TRAPS THAT HAVE ALREADY COST TIME

1. **A dead loop looks like a healthy one.** Verify the RUNNING process, not the file on disk.
2. **A check that cannot fail verifies nothing** — and its failure mode is a *reassuring* null.
3. **`grep`/`ps` filters match their own command line.** Exclude `$PID`.
4. **`bc` is not installed. `pytest-timeout` is not installed.**
5. **`qstat -f` multi-counts** (~35 queue instances per host). Use `qhost -F` — **and `qstat -g c`'s
   per-queue AVAIL is the same trap in a new dress (§96.2).**
6. **Say the denominator out loud before naming a number.**
7. **Read the predicate before planting a violation**, and build a POSITIVE CONTROL into the test.
8. **`update_handoff.py` prints a reminder to review §1's PROSE rows. ACT ON IT.**
9. **`qstat` field positions SHIFT between `r` and `qw` rows** (a queued row has no queue column) — a
   naive `$9` reads the ja-task-id. **P31, and RUN 9 nearly repeated it.**
10. **The loader enforces an 11-field record schema AND verifies `env.json`'s sha256.** Fixtures must
    honour both — a fixture that sidesteps the check also sidesteps the thing being tested.

---

# §14. ★ AUDIT RUN 9's WORK — Tamer's explicit instruction

> *"don't tell the new session not to touch anything you did. Keep in mind you might have made a
> mistake as well… tell it to audit your work too."*

**Nothing RUN 9 did is protected.** Re-check, in this order:

1. **§97's D16 implementation.** It deviates DELIBERATELY from the register (a per-seed pair invariant
   rather than a leg-wide census). **Is the per-seed form right?** It mirrors `crn_pair_device_consistent`
   — verify that mirroring is correct and that `'<absent>'`-as-wildcard cannot hide a real mix.
2. **§97's claim that D16 and D12 are hard-coupled.** Re-read `mode_d_supervisor.ps1:225`. If the
   coupling is wrong, one of the two could have shipped alone.
3. **§87.2's refutation of §84.** Re-run `docs/ops/reject_taxonomy.py core`. The claim is that
   `check2-attribute-NOT-IN-ALLOWLIST: .resize` fires on 12 of 20 — **verify `ast_gate` accepts
   `import numpy as _np` yourself.**
4. **§94's loop-learning result.** n = 20 with an arm-imbalanced sample. **Re-run
   `generation_learning.py` as more pools complete** — the honest test is whether the number moves.
5. **§91's C4 detector.** Verify it counts LLM arms and reads each line's own `search*/` roster.
6. **§88's `startswith("test")`.** Confirm no non-test sub-root begins with "test".
7. **§93's fail-loud on an empty scan** — and that h3's legitimate "no gen>0 prompts" still returns 0.
8. **§98's drift token.** Confirm `drift=0` is now reachable ONLY with a clean tree.
9. **§96's core-count answer.** Re-measure the RQS, the priority comparison and the queue arithmetic.
   **If Tamer is right that we should be at 4k and RUN 9 missed a lever, find it.**
10. **§95.3 / §12.2's refusal to start the frozen arms' test legs early.** It rests on `interleave=True`
    at `campaign.py:1836`. **Read that line.** If the reasoning is wrong, a real speed lever is being
    left on the table.

**And the meta-lesson: RUN 8 found EIGHT broken instruments and RUN 9 found SIX MORE — while the DATA
was clean every single time. Assume the asymmetry persists. The next defect is more likely in something
that WATCHES than in something that COMPUTES — and RUN 9's own tools are now part of the watching
layer.**

---

# §15. ★★ THE LANE STRUCTURE — THERE IS ANOTHER SESSION RUNNING

**Read `docs/LANE_COORDINATION_2026-07-31.md` before editing anything.** Tamer has asked for a
**monitoring lane** in addition to this one, so plan for up to three concurrent sessions.

| lane | owns |
|---|---|
| **OPS (you)** | `src/**`, `scripts/**`, `config/**`, `prompts/**`, `docs/ops/**`, `DEFERRED_FIXES_RUN4.md`, `RUN*_SESSION_PROMPT.md`, `CAMPAIGN_EXECUTION_RECORD.md`, `outputs/**`, `HANDOFF.md` §1 |
| **GRADE / WRITE-UP** | `paper/**`, `GRADE_95_MASTER_PLAN.md`, `V2_WRITE_TIME_REGISTRY.md`, `CLAUDE.md` |
| **MONITORING (new)** | see §16 — it should own NOTHING and change NOTHING |
| **SHARED** | `CHANGELOG.md` · the cursor · `HANDOFF.md` §3. **Re-read immediately before editing; an Edit built on a stale read silently discards the other lane's work.** |

**Rules that bind every lane:** announce a correction in the CHANGELOG **before** fanning out to fix it
· a lane MAY correct its own false claim wherever it propagated, but must confine the edit and announce
it · **never snapshot another lane's live buffer** (check mtime) · **effect-blindness: no lane reads a
treatment arm's sealed-test outcome** before the ladder completes.

# §16. ★ IF TAMER SPAWNS THE MONITORING LANE — its brief

**Purpose:** *"very deeply and strictly and constantly monitor and verify the output and the results."*

**It is READ-ONLY on the campaign.** It changes no `src/`, no `scripts/`, no `config/`, no `prompts/`,
and never restarts anything. Its outputs are **findings**, delivered to Tamer and to the ops lane.

**Its mandate:**
1. **§0.1's cadence, absolutely** — the cycle log on the first tool call of every batch.
2. **The RESULTS, not the processes.** Run `science_watch`, `results_audit`, `arm_coverage`,
   `equal_k_sensitivity --k N`, `generation_learning`, `reject_taxonomy`, `verify_arm_manipulation`
   **and interrogate what they produce** — magnitude, sign, units, coherence — against §0.2's four rungs.
3. **Climb rung 4 on every instrument it uses.** Fourteen instrument defects in two sessions; the ops
   lane's newest tools are the least audited things in the repository.
4. **Effect-blind.** Hardware, counts, censuses, validation-side selection statistics — **never a
   treatment arm's sealed-test outcome.**
5. **It must NOT duplicate the ops lane's fixes.** It reports; ops applies. Announce in `CHANGELOG.md`.

---

**Start by verifying live state FIRST-HAND — never carry a number forward from this brief without
re-measuring it. Say "Resuming from: … — next: …" and CONTINUE; do not ask what to do.**

**Read the cycle log on your very first tool call and on the first call of every batch thereafter
(§0.1). Finish §0.3 before anything else. Climb all four rungs on every claim (§0.2). Build a positive
control into every check. Say the denominator out loud. Audit RUN 9 (§14). Push Myriad to its maximum
and re-measure it at every boundary (§12.2). Never cut the science. Quality first — and within that,
earliest.**
