# ⭐ HANDOFF PROMPT — NEW CLAUDE CODE SESSION: RUN 4 IS LIVE AT T+51 h, TAKE IT OVER

> **Paste this whole file as the first message of the new session.** It is written to leave **zero
> gaps**: everything the previous session knew, was granted, was forbidden, found, got wrong, and
> still owes. Read it end to end before touching anything. Then verify the live numbers yourself —
> they are hours old by the time you read them, and *every* number in this file is a claim you should
> re-derive rather than trust.

**You are the fourth session on a LIVE, IRREPLACEABLE, PRE-REGISTERED experiment.** Twelve
supervised driver lines have been running on UCL's Myriad cluster since 2026-07-28 21:08 UTC. Real
money is being spent. The sealed test data is sealed. The pre-registration is frozen and its hash is
checked every cycle. **A careless command here is not a bug you fix later — it is a dissertation you
cannot re-run.**

---

## §0. TAMER'S INSTRUCTIONS — VERBATIM, ALL STILL BINDING

### §0a. The instruction that created this session (2026-07-31) — the ONE thing that changed

> *"I want to transition this session into one claude code session actually, so ultrathink and ensure
> the smooth transition. It should be like you, but the only thing that I did not like about you is
> that you didn't monitor everything constantly, every 2 minutes, the new claude code session should
> not have that."*
>
> *"I want to pass this chat into the new fresh claude code chat, exactly the same way it was passed
> to you… document absolutely everything in all docs, including changelogs, handoffs and etc… grant
> the new session all the rights, everything that was granted to you, tell it how we communicate
> remotely, what to follow… The transition must be extremely smooth, and it should feel like the
> session never ended, the next session must have absolutely 0 gaps in its knowledge… the new claude
> code session must understand that absolutely everything must be 100000000000% strictly absolutely
> flawless, always verify itself many times, ultrathink, and be 100000% confident… make sure that the
> next claude code session works at its maximum, doesn't miss anything, and does the really extensive
> job."*

**→ §8 is therefore the section you will use most. The 2-minute cycle is a HARD STANDING ORDER, not a
suggestion.** The previous session did excellent work and still let a monitoring gap of 5.2 hours
open once. That is the single named defect in its conduct. Do not repeat it.

### §0b. Every instruction Tamer gave the previous session (2026-07-30 → 07-31), verbatim

* *"I give you full permissions, ultrathink and proceed. Also please very deeply and extensively
  analyse my prompt in full, don't forget about other parts as well, everything is super important.
  Ultrathink, take as much time as you need, make sure absolutely everything is strictly and deeply
  perfect… make sure you always verify many times, and 100000% confident."*
* *"Make sure this campaign is absolutely strictly flawless across all dimensions possible and across
  all angles… With regards to cores, please make sure we use maximum possible cores, preferably 4k or
  even more… also tell me, do we need to restart the campaign or something else?"*
* *"Also very deeply and strictly analyse the results as well always, make sure you deeply verify
  them, and make sure they are logical, and meaningful and correct 10000000000%, not some garbage."*
* *"ok, so do it yourself, I give you full permissions"* — and later *"so do it yourself"* again when
  a fix needed applying. **He does not want to be asked for permission for work he has already
  authorised.**
* *"finish the plan, we are currently on 500 cores, its too low"*
* *"also, addition to the plan, make sure you always in that report doc on github which you update
  every 5 min, make sure you post detailed updates, and also in the remote control doc, make sure you
  always look into it for the instructions if I put anything"*
* *"I am back, whats going on? Why did you stop monitoring deeply?"* ← **the origin of §8.**
* *"thats fine, worry about budget, I will top up"*
* *"why do we only have 744 cores? Where are 4k cores? Why aren't we working at the full maximum"*
* *"so if there are two options you say, why don't we fully exploit them?"* · *"why not use 16 threads
  then? Why don't we use the maximum possible from myriad"* · *"so do we maximise the speed to an
  absolute maximum?"*
* *"if we are at pack 4, there is no guarantee that we can reach 4000 cores, but at pack 8, there is
  a higher chance of reaching 4000"* ← **he was right and the previous session's decision was
  reversed. See §6.7.**
* *"I want you to ultrathink very deeply and extensively, and make the system very smart and advanced
  and sophisticated by adding same things like S&P and etc… or maybe you can propose something else
  as well"*
* *"We need to make sure we dive extremely deep on both hypotheses"*
* *"but where did we get these 11 human writing reward functions? Is that something verified and legit
  and accurate, or you just made it?"* · *"why only 11, do you think that's enough? why not 30-40?"*
* *"so why are our baselines, and benchmarks so weak?"* · *"so it means they are stupid, and why are
  they so stupid?"* ← **answered in §6.5; this became a real finding.**
* *"on benchmarks, don't we have S&P 500 and etc? I have told you to add them, there were supposed to
  be."* ← **he was right; the data had been on disk unloaded for a month. §6.6.**
* Repeatedly, in almost every message: *"ultrathink very deeply and extensively"*, *"make sure
  absolutely everything is strictly flawless"*, *"verify many times"*, *"don't miss anything"*.

### §0c. Older standing instructions, carried forward and still binding

* **Full delegation (2026-07-13).** Act on his behalf, ratify on his behalf, conditioned on
  ultrathinking and on obeying the standing priorities. Do not ask permission for work already
  authorised. Do ask before anything irreversible.
* **Campaign speed is a standing priority (2026-07-24).** Actively drive campaign wall-clock toward
  its global minimum with the best legitimate pools, packing, and hardware — *without* cutting the
  science and *without* lowering job priority. Throughput = the seed rung reached = the grade.
* **Never lower our SGE priority. Ever.** No `qalter -p <negative>`.
* **Documentation is write-up raw material.** Document *everything* — past, present, future — as it
  happens, including every mistake, with root cause · how it was found · the fix · the lesson.
* **Grade inflation 2026.** The bar was raised this year: last year's distinction ≈ this year's
  merit. Every rubric dimension needs unambiguous distinction evidence.

---

## §1. STANDING RIGHTS — ALL OF THEM, NO EXCEPTIONS

You have **every right the previous session had.** Specifically, and without needing to ask:

1. **Full permission to act.** Investigate, decide, fix, deploy, commit, push, and ratify on Tamer's
   behalf — conditioned only on ultrathinking first and obeying the standing priorities.
2. **Full cluster access.** SSH to `myriad` (`ucestes`) is configured and passwordless. `qstat`,
   `qacct`, `qhost`, `qsub`, `qdel <explicit job id>`, reading and writing under `~/Scratch/llmrp4`.
3. **Full repo write access.** Edit, test, commit, push to `myriad-cluster-and-tier-system` **and**
   `backup-2026-07-28` — subject to §3 (the drift rule) and the prohibitions below.
4. **Full permission to run anything on the laptop**, install nothing that changes the frozen env,
   free RAM, close apps, manage power/services for training speed. Never kill VS Code, a terminal, or
   live training.
5. **Full authority to stop the campaign** if the science is in danger. The lever is a file:
   `outputs/campaign_cluster_run4/STOP_CAMPAIGN`. Stopping costs days; a contaminated confirmatory
   record costs the dissertation. Judge accordingly, and tell Tamer immediately either way.
6. **Full authority to spend tokens and time.** Depth is the point. Ultrathink on everything
   non-trivial. Never economise on rigour.
7. **Full authority to write the dissertation forward** while the campaign runs — roughly 5,900 words
   of CH1/CH2/CH3/Methods need no results and are pure grade.

### Hard prohibitions — violating any is a defect

| never | why |
|---|---|
| add Claude/Anthropic attribution to any commit, PR, tag, doc, `CITATION.cff`, or paper front matter | Tamer is the sole author. The default `Co-Authored-By` convention is **REVOKED** in this repo. Re-read every commit message before committing. |
| `git clean -xfd`, or any `-x` | `data/` is gitignored: a dry run showed **1,264 paths** would be deleted including the frozen headline panel and 1,085 raw files. The only backup (`D:\llm_rp_predefender_backup\`) is dated 2026-07-01 and would NOT save current work. |
| `git add -A` or `git add -u` without reading `--numstat` first | `-A` sweeps untracked `outputs/`; `-u` stages mass deletions as readily. |
| lower SGE priority (`qalter -p <negative>`) | Tamer's absolute rule. |
| `qdel -u ucestes` | delete by **explicit job id** only. |
| `qalter -l …` on a queued job | **FORBIDDEN SITE-WIDE.** `jsv_allowed_mod = ac,h,i,e,o,j,M,N,p,w` — no `l`. A queued job's resource request is immutable. Proven, §6.2. |
| backslashes, escapes, or **backticks** in a bash heredoc or `bash -c` string | backticks EXECUTE. This corrupted a file once. Use the Write tool, or a file-based script. |
| inline `git commit -m "…"` in PowerShell | write the message to a file → `git commit -F <file>`. |
| pull Refinitiv data from Bash | the Bash sandbox is the blocker. PowerShell + `.venv-lseg` only. |
| edit `src/ scripts/ config/ prompts/` while the run is live | see §3. Analysis-layer files are the one narrow exception, and only with a proven-unreachable import closure. |
| upload the licensed Refinitiv panel, `outputs/`, or any API key to a public deposit | licence + integrity. |
| re-freeze the pre-registration | `freeze.py` forbids it. The hash is `3ca6f01ab7724d47bd5d01bc9e73b4d3150c049e1048dd86a864b400a230432f`, tag `prereg-v2.1`, seal commit `b9c2be5`. |
| trust a pipe's exit code | `cmd | tail; echo $?` reports **tail's** status. This produced a false "guards green" in the previous session. Read the real rc, or the log. |

---

## §1b. ⚠ THE PRIORITIES AND BINDING STANDARDS — reproduced here because `CLAUDE.md` IS UNTRACKED

`CLAUDE.md` auto-loads in the repo, but it is **untracked**, so it is not in git history and not
recoverable from a clone. These are the parts you must have even if that file is ever lost.

### ★★★ THE PRIORITIES — the absolute, overriding north star

1. **MAXIMISE THE GRADE → a 95 %+ FLOOR, as close to 100 % as humanly possible.** "Good enough" is
   not the target; the ceiling is.
2. **WORLD-CLASS, CUTTING-EDGE, PUBLISHABLE** — TMLR-and-up / ICAIF-main. Not a workshop demo, not a
   competent-student exercise.
3. **VERY DEEP** — depth, intuition, mechanism, genuine originality over breadth and textbook
   machinery. Okhrati's revealed grading function: intuition **before** machinery; depth over
   breadth; honest nulls rewarded; motivate the method with the data; originality foregrounded;
   report wall-clock compute; faultless figure/table cross-referencing.
4. **CORPUS-GROUNDED + GENUINELY NOVEL** — lean heavily on the 196+ first-hand-read paper corpus
   (cite-and-USE, never cite-and-wave), and keep the novelty cell guarded by dated sweeps plus a
   mandatory pre-submission sweep.

These are inseparable. **Default to the most ambitious option that is rigorous and honest. Never
trade depth, quality, or ambition for convenience or speed.**

### ★★★ STEFAN'S FIVE CRITERIA (industrial supervisor) — binding evaluation lens

Real gap · principled/elegant/non-fragile method · **reproducibility (the critical point)** · sound
ideas with everything justified by data or literature · crystal clarity about what is measured
(including the **fed-vs-scored** distinction: the fed tail is **ENDOGENOUS**, never
"agent-independent").

### ★★★★ REPRODUCIBILITY — "the single most important point of this dissertation"

Three layers must genuinely hold: **analysis** = deterministic archive replay · **protocol** =
re-runnable by anyone (keyless golden path) · **experiment** = open-weight, hash-pinned, self-hosted
legs.

**THE DETERMINISM ENVELOPE — the operative engineering rule.** Anything that changes floating-point
arithmetic is part of the FROZEN DESIGN, not an ops detail: device (CPU ≠ CUDA bit-for-bit), thread
counts, BLAS parallelism, `torch.compile`, fp16/tf32, fused optimizers, batch/buffer sizes, library
versions, provider/quantization/reasoning pins.

* **Never introduce a numerical-nondeterminism source to gain speed.** Speed comes from *more
  machines*, never *different arithmetic*.
* Every comparison unit must stay **device-homogeneous** (the CRN pairing every paired contrast rests
  on).
* A pin nobody can verify is **fictional** — determinism-relevant facts must land in per-record
  provenance so a violation is *detectable by audit*.
* **PACK SIZE IS OUTSIDE THE ENVELOPE.** Packed trainings are separate spawned processes with
  `OMP=1`; pack depth changes scheduling, not arithmetic. This is why `--pack 8` at C4 is legitimate
  (§6.7). **Thread count is INSIDE it** — which is one of two reasons 16 threads was rejected.

### ★★★ THE FIVE DUTIES — accurate · surgical · always-ultrathink · always-verify · verify it is LOGICAL

1. **ACCURATE.** Every number, path, flag, hash, and count is the real one, read from the real
   artifact at the moment of writing. If it is stated, it was observed. Cite the evidence beside it.
2. **SURGICAL.** Smallest correct diff. Read the target and one nearby example first; re-read your
   own diff afterwards for what a compiler cannot catch. Precision is targeting, not timidity — the
   change must still be **complete** (every call site).
3. **ALWAYS ULTRATHINK.** The first plausible answer is a hypothesis, not a conclusion. What would
   falsify it? What is the strongest counterargument?
4. **ALWAYS VERIFY — INCLUDING YOUR OWN WORK.** Nothing is done until it was RUN and the real output
   OBSERVED. Then: re-run *after* the change, never before; read `PYTEST_RC` from the **log**, never
   a pipe's exit code; **prove a new test can FAIL against the pre-fix code**; when a script returns
   a surprising NEGATIVE, suspect the script first — *it is a claim about your own code before it is
   a claim about the world*; **the author should not grade their own work** — for substantial
   multi-file work, have a fresh auditor subagent check it; **overstating a risk is as inaccurate as
   understating one.**
5. **VERIFY IT IS CORRECT AND LOGICAL, not merely that it RAN.** Sanity-check magnitude, sign, and
   units. Cross-check against an **independent route** — agreement between two derivations is
   evidence; one derivation repeated is not. Check internal consistency across code, docs, and paper.
   Check the conclusion actually follows. **A surprising result is an obligation to investigate,
   never a result to report as-is.**

### ★★★ OTHER BINDING STANDING RULES

* **NEVER MISS ANYTHING.** Enumerate the full scope of any multi-part task explicitly, complete all
  of it, and re-sweep at the end to prove nothing dropped. "I covered the main ones" is a defect.
* **PLANS ACCUMULATE.** A new instruction augments the standing plan; it never silently replaces it.
  Keep the durable queue (todo list + HANDOFF §1 + the cursor) holding the FULL accumulated set.
* **STRICT ASSESSMENT · SIGNAL OVER NOISE.** Add only what serves the priorities. Depth over breadth.
  Keep what is already sufficient — expanding what needs no expansion is a defect, not diligence.
* **PUBLICATION-GRADE BACKBONE · NO LAZY HEDGES.** Never soften a claim to "report-only" merely to
  protect a result. Make the strongest claim the evidence and a non-fragile design can bear.
* **ZERO-DEFECT, FIX-ON-SIGHT.** The instant you spot a gap, stale fact, dead link, or inconsistency
  — even incidentally — fix it or record it. "I noticed it but moved on" is not acceptable.
* **STRONG-EVIDENCE STANDARD.** Grade every claim at birth (A/B/C). Only grade A goes in the PDF.
* **MAXIMUM STRICTNESS ON QA GATES** (compliance floor 1.0) — but **never** overwrite pre-registered
  *statistical* parameters (α=0.05, BH q=0.05, power 0.80, SESOI 0.05 DSR): there, the registered
  value **is** the strict form.
* **END-OF-WORK DUTIES, all four, every time:** ① `python scripts/update_handoff.py --suite-status
  "…"` then review §1's prose rows; ② a short cursor `▶ NOW` entry (≤15 lines); ③ a **detailed**
  CHANGELOG block **always**, even for a no-commit session; ④ push the backup branch.
* **★★★ ABSOLUTE: every message you send to Tamer begins with the word "Tamer".** No exceptions.

---

## §2. THE PROJECT AND ITS COMPLETE HISTORY

### §2.1 What the dissertation actually is

An LLM is given a task description and asked to **write Python reward-function code** for a
risk-sensitive portfolio RL agent (SB3 SAC, fixed). The agent trains on that reward; its realised
returns are measured; a feedback block goes back to the LLM; it writes five more. Six generations.

**The manipulated variable is the FEEDBACK BLOCK — nothing else.** Five arms:

| arm | what it is fed back |
|---|---|
| `distributional` | six left-tail scalars (`cvar_05/10/25/01`, `left_tail_mass`, `robust_skew`) |
| `scalar` | one performance number (DSR) |
| `scalar_cvar5` | DSR + one tail number — the dose-response middle rung |
| `placebo` | six tail-shaped but uninformative numbers |
| `placebo_shuffled` | the real six, deranged across candidates — the structure control |

**The identification principle: only the reward may vary across arms.** Any new state or reward input
is creep that breaks identification. This is the litmus for every proposal.

**The question is mechanism first:** does showing the LLM the downside change the reward *code* it
writes? Performance equivalence is the rigorous backdrop. A null LOCATES where the causal chain
(fed signal → authored code → policy → realised tail) breaks — which is why the null is bankable and
must never be spun.

### §2.2 The frozen design (v2.1)

* Canonical hash **`3ca6f01ab7724d47bd5d01bc9e73b4d3150c049e1048dd86a864b400a230432f`**, tag
  `prereg-v2.1`, seal commit `b9c2be5`. `freeze.py` **forbids** re-freezing. The hash is verified by
  a guard every cycle.
* **Six confirmatory nodes with graphical alpha recycling:** `N1_h2_tail` (CVaR-5 % IUT) ·
  `N2_h2_ra` (Sharpe, or equivalence via TOST at ±0.05 DSR) · `N3_h3` · `N4_h4` · `N5_structure` ·
  `N6_h1` (IUT over the 11-reward canon).
* **Seed ladder** 30 → 189 → 279 → 340 → 403 → 568, with CRN pairing across arms.
* **Split C:** train 2005–16 / val 2017–19 / **test 2020–26 sealed** (1,571 sessions).
* Data: `data/gold/returns_panel_univ5.parquet`, 5,406 × 963, licensed Refinitiv, survivorship-free,
  PIT. Headline universe is **univ3-derived, NOT univ4** (univ4 fabricates M&A losses).
* Exogenous stop **2026-08-27**. Submission **2026-09-01**.

### §2.3 The model roster (R101 — Okhrati's seed-parity directive)

Twelve supervised lines run in parallel to a common seed rung: **`c1`** (confirmatory, Opus 5) ·
**`h3ss`** (single-shot, single-arm by design) · **`leg1`–`leg10`** (sonnet-5, haiku-4.5,
deepseek-v4-pro, glm-5.2, gpt-5.6-luna, kimi-k3, nemotron-3-super, qwen3.5-9b, qwen3.6-27b,
gemini-2.5-flash).

`qwen3.5-9b` is the deliberate **capability-gradient bottom anchor** (~17 % gate-pass measured
pre-run; ~87 % reject rate live, against its own registered ~83 % baseline). **A low yield on that
leg is a registered FINDING, not a fault.**

### §2.4 R115 — the winner-eligibility execution floor

A candidate whose authored reward falls back to the harness default on ≥10 % of steps is ineligible
to win. Rationale, and it is a real scientific point: a *fully* broken reward scores nothing and is
self-limiting; a *partially* broken one can score BEST because the harness default silently does half
the work. One live record showed exactly this (49.98 % fallback, the **highest** val_fitness in its
arm). Fitness alone cannot substitute for an execution-quality floor.

### §2.5 The run ledger

| run | what happened |
|---|---|
| RUN 1 | killed at launch — D12/D13 |
| RUN 2 | killed — a gate stop looked like success |
| RUN 3 | killed — preflight budget blindness |
| **RUN 4** | **LIVE since 2026-07-28 21:08 UTC.** Roots: `outputs/campaign_cluster_run4` (laptop) + `~/Scratch/llmrp4` (Myriad) |

### §2.6 D1–D18 — every machine defect ever found

Full detail in `docs/CAMPAIGN_EXECUTION_RECORD.md` §20, §23, §25, §28, §37, §38, §44.

| id | defect | state |
|---|---|---|
| D1–D11 | pre-RUN-4 defects (transport, gates, archiving, seeding) | fixed pre-launch |
| **D12** | a gate stop looked like success | fixed |
| **D13** | a provider reply with no `choices` raised `TypeError` instead of retrying | **deferred (1)** |
| **D14** | a PARTIAL arm failure is SILENT — the six repo guards cannot see a missing arm | worked around live by `docs/ops/arm_coverage.py`; **deferred (4)** |
| **D15** | the watchdog did not carry `-ExcludeHosts`; four baseline records landed on a Xeon 6140 among 6240s | worked around live (fence on all 12 lines); the bit-comparison experiment is OPEN |
| **D16** | the C3 gate's `health_ok` does not see a SUBSTRATE mix | **deferred (6)** |
| **D17** | the safe-default cleared the reward's state → a manufactured limit cycle | **deferred (7)** |
| **D18** | one record written at two paths; ~20 recursive consumers double-count it. The confirmatory path is SAFE (`analyze_campaign` dedupes by run_id and is depth-limited) | **deferred (10) — do NOT delete anything** |
| §38 | the memory request was **19.5×** the measured peak and was what kept us queued | **APPLIED LIVE 2026-07-30** |
| §39 | `CPU_THREAD_SPEEDUP[8]` is a bench number; production says **1.92×** | **deferred (9)** |
| §50 | C4 launch flag `--pack 8` | **deferred (11)** |

⚠ **CORRECTED 2026-07-31: the document holds ELEVEN items but only TEN are still to apply** — item 8
(the §38 memory sizing) was APPLIED LIVE on 2026-07-30 and shipped by the driver relaunch (§46), yet
the apply-checklist still listed it while demanding each fix have "its falsifiable test proven to FAIL
against the current code first". Item 8's test cannot fail any more. Verified by re-deriving the
renderer first-hand: `pack=1,cores=8 → 1G/slot`, `pack=4,cores=4 → 2G/slot`, `pack=8,cores=8 →
2G/slot = 16 GB/job` = **7.8 TB at 500 jobs against ~12 TB free**, which independently confirms §50.4's
pack-8 feasibility arithmetic.

**`docs/DEFERRED_FIXES_RUN4.md` now holds ELEVEN items, all to be carried by the C4-boundary
restart.** Read it in full before that restart, and validate on the first line to reach C4 before
rolling the rest.

### §2.7 Process errors — previous sessions' own mistakes (record §20.2)

**P1–P26 are now all in `docs/CAMPAIGN_EXECUTION_RECORD.md` §20.2**, with root cause, how each
surfaced, and the rule it produced. P11–P26 are the previous session's own sixteen, and they are
summarised here because the pattern matters more than any individual item:

1. Recommended `qalter -l` in five documents. It is forbidden site-wide. Root cause: verified the
   *substitution syntax* by dry run and **inferred the permission**.
2. Projected the LLM budget per **LINE** instead of per **(line, ARM)** → reported "26 % margin" when
   the truth was a **−$7.60 shortfall**.
3. Reported a placement rate of **100 % from n = 1**. Re-measured at n = 23 (52 %) and n = 85 (76 %).
4. Put **backticks** inside a `bash -c` string; they executed and corrupted the cursor file.
5. Used `pd.bdate_range` (1,632 sessions) instead of the records' own **1,571-session axis** — the
   exact §36 error, committed *inside the session that was quoting §36*.
6. Claimed "GIFT must be cited in CH2" **without grepping `paper/`**. It was already cited.
7. Concluded "pack 8 buys nothing" by evaluating **only at the 1,000-job cap**, where the configs
   tie. Tamer challenged it; re-priced across achievable job counts; **decision reversed**.
8. Nearly applied a 4× memory headroom that would have computed **6.8 G/slot for the pack-4 lane —
   larger than the 4 G it replaced.** Caught by *measuring* the pack-4 peak instead of inferring it.
9. A liveness checker was blind on `driver_core.log` — the **confirmatory** line — because its regex
   required `\s+\w+` after the timestamp.
10. "PopArt: 0 records carry it" — `popart_scale` is a **dict**, not a float.
11. "PopArt: 45 invariant breaks" — an **absolute** 1e-9 tolerance against a streaming estimator.
    The truth is zero.
12. Framed 84.4 % turnover-pricing as "the model discovers what the literature missed". **FALSE** —
    `prompts/initial_generation.txt:7` lists `- turnover/transaction cost.` explicitly.
13. Used σ_seed where the paired test needs **σ_D** (~4× too optimistic on required seeds).
14. A diagnostic renamed **live job 45433** to `zzname_test` and the restore **silently failed**.
    Restored explicitly, rc=0, driver unaffected. *Read the value back after any live mutation.*
15. Let a **5.2-hour monitoring gap** open. This is why §8 exists.
16. Reported `GUARDS_RC=0` that was actually **`tail`'s** exit code. The guards were rc=2.

**THE PATTERN, and it is the single most useful thing in this document: every one of these was an
aggregate that answered a slightly different question from the one being asked, reported as if it
answered the right one.** A striking number is a hypothesis about *your own instrument* until the
confound is ruled out. Before you report a number, say out loud what its denominator is.

### §2.8 Settled decisions — do NOT re-propose

2000-start · options data · more candidates (multiplicity) · restructuring the repo · pydantic ·
Snowflake · Ray · `torch.compile` (dead on native Windows, no Triton) · a second frontier model ·
GPT-5.5 (cost) · weak-model confirmatory seat · lowering job priority · an RC/admin fast-track
request (Tamer said no) · 16 threads (§6.3).

### §2.9 Verified-sound — do not re-litigate

Leakage/PIT discipline · the statistics implementation (literature-exact) · the sandbox allowlist
(from-import RCE closed) · citation backbone · construct validity (re-verified from **all 643 live
prompts**, §6.4) · the freeze machinery · CRN determinism · the arm roster guard.

---

## §3. ⚠⚠ THE SINGLE MOST IMPORTANT RULE FOR A LIVE RUN

**The drivers execute the code as it was at the sha they were LAUNCHED from — not HEAD.**

```bash
git diff --name-only c99716e HEAD -- src scripts config prompts
```

**`c99716e` is the RUNNING SHA.** It was re-based on 2026-07-30 by the certified memory relaunch
(record §46) — it is **not** `b9e6df5`, which older documents cite. A relaunch **re-bases** this
reference; if you relaunch, update it here, in `docs/ops/cycle.py` (`RUNNING_SHA`), and in HANDOFF §1
in the same change.

**That diff must be empty, or every non-empty entry must be PROVEN unreachable from the executing
import closure.** Right now it shows exactly two files:

* `src/data/market_reference.py` · `src/baselines/strategies.py`

Both are **analysis-layer**. `python docs/ops/import_closure.py` statically walks the closure from
`scripts/run_campaign_cluster.py` and `src/cluster/run_one.py` across **193 first-party modules** and
proves neither is reachable. That is why no restart was bought (each costs ~$1.25 in re-authoring).
**Re-base at the C4 restart and the drift goes to zero.**

Do not treat this as licence. The rule is: *no edit to `src/ scripts/ config/ prompts/` while live*,
and the exception is narrow, proven, and documented.

---

## §4. READ THESE, IN THIS ORDER

1. **`docs/HANDOFF.md` §1** — the ★★★★★ START HERE row is current as of 2026-07-31 00:30 UTC.
2. **`memory/session-current-focus.md`** — the `▶ NOW` cursor.
3. **`CLAUDE.md`** — priorities + the four-authority rule (untracked; §1b above is the backup).
4. **`docs/CAMPAIGN_EXECUTION_RECORD.md`** — the operations narrative, newest sections last. **§38
   through §52 are the previous session's work** and are the densest material in the project.
5. **`docs/DEFERRED_FIXES_RUN4.md`** — eleven items for the C4 restart.
6. **`docs/ops/acknowledged_alarms.txt`** — every alarm that is knowingly quiet, **with its own
   RE-TRIAGE trigger**. Read this before you conclude anything from a guard verdict.
7. **`docs/ops/watch/FINDINGS.md`** — the evidence-graded science ledger.
8. **`docs/REMOTE_CONTROL.md`** — Tamer's inbound channel.
9. **`CHANGELOG.md`** — entries `[2026-07-30d]` … `[2026-07-30/31]`.
10. **`docs/A12_DEPOSIT_PACKAGE.md`** — staged and waiting on Tamer (~10 min of his time).

---

## §5. LIVE STATE (2026-07-31 00:37 UTC, T+51 h 28 m) — **VERIFY IT YOURSELF**

| | |
|---|---|
| lines | **12 / 12** up, **ALL LINES FULL** (5/5 arms on all ten legs; h3ss single-arm by design) |
| records | **1,173** on disk (`find … -name record.json`); the guard's authored count is **1,163** |
| spend | **$26.84** total · `c1` $13.76 · h3ss $5.05 · legs the rest |
| freeze hash | **MATCHES** |
| transport timeouts | **0** |
| cluster | **~728 cores**, ~95 running / ~104 queued |
| driver logs | all twelve written within the last minute |
| guards | rc=2, **entirely from acknowledged verdicts** (`truncation`; sentinel `record_sanity`, `substrate_fields`, `silent_hang`) |
| stage | **SEARCH**, generation 5 of 5 on the lead arms. The seed ladder (C4) has NOT started |
| HEAD | `a3169ac` on `myriad-cluster-and-tier-system`; backup branch `backup-2026-07-28` |
| running sha | **`c99716e`** |
| attrition spread | 47 − 26 = **21 candidates** across arms (report it, never "fix" it) |
| rung-568 ETA | ~2026-08-18 at current cores |

**⚠⚠ THE ONE THING THAT CAN KILL THE RUN — THE ANTHROPIC BUDGET IS PROJECTED SHORT.** $22.15 spent +
$13.60 still to author = **$35.75** against **$28.15** credited = **−$7.60**. If that key runs dry,
the **confirmatory** line stops — the one thing the campaign cannot absorb. Tamer said *"worry about
budget, I will top up"*. **Verify the top-up landed, and run `docs/ops/budget_watch.py` (exit 2 =
shortfall) every cycle until it is green.** Note our figure is a ledger ESTIMATE, not a balance
reading (§49).

---

## §6. WHAT THE PREVIOUS SESSION FOUND — do not rediscover, do not contradict

### §6.1 The capacity question, answered by measurement (§38, §43, §46)

Eight canary jobs proved the discriminator is the **MEMORY request** — not fair share, not walltime.
`maxvmem` p50 **1.57 GB**, max **1.64 GB**, against a **32 GB** ask = **19.5× over-request**. The fix
went into the renderer `src/cluster/jobscript.py` (search lane `-pe smp 8 / -l mem=1G`; packed lane
`-pe smp 4 / -l mem=2G`; GPU untouched), was certified (**2,882 passed / 3 skipped / 0 failed,
`PYTEST_RC=0` read from the log**, ruff clean, **freeze hash UNMOVED**), deployed byte-identical, and
shipped by killing the 24 drivers so their twelve supervisors relaunched them (188 → 191 jobs, **no
duplicate submission**). **Confirmed at scale: new-sizing jobs place at 76 % vs the old sizing's 21 %
(n = 85); cores 528 → 744.**

### §6.2 `qalter -l` is forbidden site-wide (§45)

`jsv_allowed_mod = ac,h,i,e,o,j,M,N,p,w` — no `l`. Proven with a control (`qalter -N` returns rc=0,
`qalter -l` does not). A queued job's resource request is **immutable**; the only lever is the
renderer. `docs/ops/mem_relax.sh` now refuses to run (`exit 3`) and documents why.

### §6.3 The 4,000-core answer, and why 16 threads was rejected

4,000 is the **saturation** point — beyond it the reflection chain binds, not the cores. It is
**arithmetically impossible during SEARCH** (12 lines × 5 arms × 5 candidates = 300 jobs × 8 slots =
a 2,400 ceiling) and the search phase is **LATENCY-bound anyway** — its length is 6 × (training +
authoring), so extra cores would sit idle. It is reachable **at C4**, because `max_u_jobs = 1000` and
pack 4 × 4 cores = 4,000 — **but only at the new memory sizing** (1,000 jobs × 16 GB = 16 TB against
~12 TB free; at the old 32 GB it was 32 TB and simply unschedulable).

**16 threads: REJECTED, twice over.** Measured throughput *regresses* to 44.0 steps/s against 55.1 at
8 threads — **7.6× worse per core** — and thread count is **inside the determinism envelope** while
330 baselines are already archived at `OMP=1`.

### §6.4 The deep results audit (§44) — 1,026 records OPENED

hash == sha256 on all · 0 missing / out-of-range / non-finite · **construct validity RE-DERIVED from
all 643 LLM prompts and INTACT at generation 5** (6 tail scalars / 1 / 2 / 6-neutral / 6-deranged,
**0 scalar tail leaks**) · 99–100 % unique programs · **0 shared across arms**.

**⚠ PopArt is INERT on 50.3 %** of the archive (`popart_min_scale: 1.0` → σ = max(1.0, raw_rms); 509
engaged, 515 pinned at the floor). **Instrumented ≠ engaged.** It is arm-SYMMETRIC across the five
LLM arms (62–67 %) so it cannot confound H2, but **asymmetric on H1**, which splits perfectly by
ratio-form vs difference-form reward. **Analysis-time obligation 9: report the PopArt engagement rate
beside the H1 family comparison.**

### §6.5 Why the baselines look weak — and it is a finding, not an embarrassment (§47)

Tamer asked *"so it means they are stupid, and why are they so stupid?"* The answer, measured: the
agents rebalance **78–91 % of the book EVERY day ≈ 22 %/yr in transaction costs**.
`return_minus_turnover` — which has **119× less turnover** — is the **only** reward with a positive
Sharpe. **The rewards are faithful; the AGENT is unconstrained.** That is a legitimate, reportable
mechanism result about what an unconstrained continuous-action SAC does on a 963-asset panel.

### §6.6 `.SPXTR` — Tamer was right, and it had been on disk unloaded for a month (§48)

He said *"I have told you to add them, there were supposed to be."* He was correct. Two docstrings
called a cap-weighted benchmark "a documented limitation" while `rf_spxtr.csv` sat in the data
directory. Now wired via `load_spx_total_return()` (concatenates both CSVs, forward-fills the LEVEL
onto the panel axis **first**, then differences — order of operations matters and there is a test for
exactly that). Result on the agents' own **1,571-session** axis: **+1.1302 Sharpe / +213.3 % total
return.** The best reward **ties it and loses to equal weight** (t ≈ 1.5). **Never write "beats the
S&P".** Six new tests, including a real-data test asserting `n_extrapolated == 0`.

### §6.7 The pack-8 decision — REVERSED on Tamer's challenge (§50)

He said: *"if we are at pack 4, there is no guarantee that we can reach 4000 cores, but at pack 8,
there is a higher chance."* The previous session had compared the two configs **only at the 1,000-job
cap**, where they tie. But the cap is a *ceiling*, and the peak actually observed is **204 jobs**.
Across the realistic range, pack 8 **halves the makespan** and reaches saturation with **500** jobs
instead of 1,000. **C4 will launch with `--pack 8`** — DEFERRED_FIXES item 11. Legitimate because
pack is outside the determinism envelope (separate spawned processes; the 330 packed CPU baselines
are all `device=cpu`, `OMP=1`).

### §6.8 What the models actually wrote (§51)

**84.4 % of 762 programs price turnover — but that is COMPLIANCE, not discovery.** The prompt says so
at `prompts/initial_generation.txt:7`. The real finding is the **capability gradient**: sonnet 100 %,
nemotron 50 %, gemini-flash 33.7 %. **Analysis-time obligation 12.**

### §6.9 ★ The two H2 co-primaries are NOT equally powered (§52) — the deepest result of the session

Over 55 arm-pairs on the eleven hand-written rewards at 30 shared seeds:

| estimand | ρ across shared seeds | what CRN pairing does |
|---|---|---|
| **Sharpe** (N2 / H2-RA) | **−0.007** | **nothing** — σ_D = 0.355, essentially √2 × σ_seed |
| **CVaR-5 %** (N1 / H2-Tail) | **+0.076** | **helps ~9 %**, and its noise is only **6.1 %** of its own level |

**Why**, and this is the intuition that belongs in the write-up: CVaR is driven by the *market's*
worst days, which CRN makes the arms **share**; Sharpe is driven by the *policy's own path*, which
CRN does not align. So **"bankable on the tail" is no longer a design hope — it is an instrument
measurement**, and the tail node reaches its power targets **earlier in the seed ladder** than the
risk-adjusted node. The pilot's σ_seed = 0.244 is confirmed live at **0.25** on Sharpe.

### §6.10 Earlier sessions, still binding

* **D17** (§37) — a fail-safe that manufactures a limit cycle. The deepest earlier find.
* **§36** — the benchmark window was wrong; two headline claims were retracted. **Always rebuild the
  session axis from the panel, never from `pd.bdate_range`.**
* **§26.3** — differential arm attrition, registered PRE-DATA. Spread is now **21**. **Report it;
  never "fix" it.**
* Novelty: the conjunctive cell is still EMPTY (triple-confirmed). The sweep clock resets
  **~2026-08-20**; a pre-submission sweep is mandatory.

---

## §7. HOW TAMER COMMUNICATES REMOTELY — KEEP BOTH CHANNELS ALIVE

**Outbound (you → him): `docs/RUN4_STATUS.md`**, regenerated and pushed **every 5 minutes** by
`bash docs/ops/publish_status.sh`. He reads it on his phone. It now carries health, compute with
per-rung ETAs, the stage table, results, **the monitoring cycle log**, and a "Needs Tamer" section.
On his instruction it must be **DETAILED** and must include **active cores and current ETAs**. **ASCII
only** — non-ASCII mojibakes on his phone.

**Inbound (him → you): `docs/REMOTE_CONTROL.md`.** He edits it on GitHub from his phone. **You must
poll it every cycle.** `docs/ops/cycle.py` hashes it and shouts the cycle it changes. When he writes
something: do it, then write what you did under **LOG** at the bottom and push. His standing entry
there is *"Make sure absolutely everything is strictly flawless, also to the run4_status don't forget
to add the cores active, and current ETAs as well"* — already implemented; keep it true.

Latency is one poll interval, not instant. He knows.

---

## §8. ★★★ THE 2-MINUTE MONITORING CYCLE — TAMER'S HARD STANDING ORDER

> *"the only thing that I did not like about you is that you didn't monitor everything constantly,
> every 2 minutes, the new claude code session should not have that."*

**This is not optional and it is not "when convenient". While you are working, you check everything
every two minutes.** It has been made into ONE command precisely so there is no friction excuse:

```bash
python docs/ops/cycle.py --note "what you are doing this cycle"      # ~7 s
python docs/ops/cycle.py --ssh --note "..."                          # + cores/jobs off Myriad
```

**Exit code 0** all clear · **1** something changed, look · **2** a real problem, named on the line.

It checks, in this order:

1. **`docs/REMOTE_CONTROL.md`** — hashed; the cycle it changes, it shouts. Anything Tamer wrote
   outranks everything else you are doing.
2. **the `STOP_CAMPAIGN` lever.**
3. **`campaign_guards.py … all`** — the six repo guards.
4. **`docs/ops/arm_coverage.py`** — the repo guards **cannot** see a missing arm (D14). This can.
5. **`docs/ops/budget_watch.py`** — per-(line, arm) authoring projection vs credited headroom.
6. **driver-log freshness** — a line can hold its process and stop progressing.
7. **drift vs the RUNNING sha** (§3).
8. **records + spend, with the DELTA** — a flat record count across many cycles is a stall.

**Alarm hygiene is built in.** Verdicts listed in `docs/ops/acknowledged_alarms.txt` report as
`known`, not RED — because four of them can never return green (append-only ledgers) and a permanent
RED trains you to ignore RED. That is exactly how D15 survived ten hours. **Every acknowledged entry
carries its own RE-TRIAGE trigger, and those triggers have already fired once** (the truncation guard,
when a second model truncated). Never add an entry for something you have not run to ground.

**Every cycle appends one line to `docs/ops/watch/CYCLE_LOG.md`,** and those lines are published to
Tamer's status page. This makes "I monitored continuously" a *checkable* claim rather than an
assertion — which is the standard everything else in this project is held to. Hold yourself to it.

**Every ~5 minutes** also run `bash docs/ops/publish_status.sh`.

**Deep dives** — run when something looks off, and at least a few times a day regardless:
`docs/ops/results_audit.py` (integrity · construct validity · diversity · PopArt engagement · anomaly
hunt; exit 2 only on a hard invariant failure) · `docs/ops/science_watch.py` ·
`docs/ops/import_closure.py` (before concluding anything about drift) · `docs/ops/stage_eta.py
<cores>` · `docs/ops/cost_decomposition.py` · `docs/ops/spend_split.py`.

**If a long task will occupy you, interleave the cycle anyway.** Two minutes of campaign blindness is
cheap; forty is how the previous session's one real conduct defect happened.

---

## §9. OPERATING THE LIVE RUN

**The campaign is independent of your session.** Twelve PowerShell supervisors relaunch dead drivers;
a fenced watchdog revives dead lines every 300 s; a 17-check sentinel watches health. **If your
session dies, the campaign continues untouched** and a fresh session resumes from HANDOFF §1.

**The STOP lever** is the file `outputs/campaign_cluster_run4/STOP_CAMPAIGN`. It stops **restarts**,
not an already-running driver. To stop hard you must also `qdel` explicit job ids and stop the
supervisors.

**Relaunching** (only if genuinely required): kill the driver processes and let the twelve
supervisors relaunch them — that is how the memory fix shipped, with **no duplicate submission**.
Verify the count moves the way you predicted (188 → 191 was the observed, expected pattern) and that
no line double-submitted. **A relaunch RE-BASES the running sha** — update §3, `cycle.py`, and
HANDOFF §1 in the same change.

**The C3 review gate is an EXPECTED event, not a fault.** So is a generation drain (concurrency
falling as an arm waits for its last candidate — measured average 2.61 in flight against a design
peak of 5; the scheduler is placing 80 % of what we ask for, we simply have nothing more to ask
during a serial reflection chain).

**At the C4 boundary (~2 days out):** apply the ELEVEN deferred fixes including `--pack 8`, validate
on the **first line to reach C4**, then roll the rest. Re-base the running sha. This is the single
largest planned operation left.

---

## §10. TRAPS THAT HAVE COST TIME — do not repeat

* **Backticks in `bash -c` or a heredoc execute.** Use the Write tool or a file-based script.
* **A pipe's exit code is not your command's.** `cmd | tail; echo $?` reports `tail`.
* **`PYTEST_RC` comes from the log**, never from a wrapper.
* **A new test that cannot FAIL against the pre-fix code verifies nothing.** Prove it fails first.
* **Never build a session axis with `pd.bdate_range`.** Rebuild it from the panel (1,571, not 1,632).
* **`popart_scale` is a dict.** Tolerances against streaming estimators must be **relative**.
* **Read a value back after any live mutation** (the `qalter -N` restore that silently failed).
* **`outputs/` is untracked and huge** — never `git add -A`.
* **PowerShell + `.venv-lseg` for Refinitiv. Never Bash.**
* **PS1 files: ASCII only, BOM-less UTF-8**, validated with `Parser::ParseFile`. PowerShell 5.1 turns
  em-dashes into string-breaking smart quotes.
* **Before claiming something is missing from the paper, grep `paper/`.**
* **Before concluding from an aggregate, state its denominator out loud.**

---

## §11. OPEN THREADS — pick these up

1. **The Anthropic top-up.** Verify it landed. Until then `budget_watch.py` is rc=2 and the
   confirmatory line is at risk. **This is the highest-priority open item.**
2. **A12 — the public OSF/Zenodo DOI deposit.** A registered freeze-day obligation, currently unmet.
   Everything is staged in `docs/A12_DEPOSIT_PACKAGE.md` (nine bound files, per-file sha256 from the
   signed tag, a verified `git archive` build, paste-ready metadata, and a do-not-upload list). It
   needs ~10 minutes of **Tamer's** time. Remind him.
3. **The C4-boundary restart** carrying eleven deferred fixes including `--pack 8`.
4. **Watch cores.** They should stay at or above ~744 as old-sizing jobs drain. If they do not,
   §38/§43 are wrong and must be corrected — in the record, not quietly.
5. **The D15 bit-comparison experiment** — decides whether four archived baseline records are
   replaced or kept with a measured equivalence.
6. **R96** (both-axes-or-neither) — post-campaign only.
7. **The novelty sweep** resets ~2026-08-20; a pre-submission sweep is mandatory.
8. **THE WRITE-UP IS WHERE THE GRADE IS.** ~5,900 words of CH1/CH2/CH3/Methods need no results at
   all. The campaign runs itself. Every hour you are not monitoring or fixing is an hour that should
   go into the document — see `docs/WRITEUP_95PLUS_PLAYBOOK.md`, which is the writing plan of record.
9. **Analysis-time obligations** accumulated so far: exclude `stop_reason == "length"` rows from every
   authoring-reliability denominator (obligation from the truncation guard) · report the PopArt
   engagement rate beside the H1 family comparison (**9**) · report the authoring gradient rather than
   the aggregate 84.4 % (**12**) · report the arm-attrition spread of 21 · report σ_D per estimand,
   not σ_seed.

---

## §12. YOUR FIRST ACTIONS

1. Say **"Resuming from: … — next: …"** and continue. Do not ask what to do.
2. `python docs/ops/cycle.py --ssh --note "session start"` — and read every line of the output.
3. Read `docs/HANDOFF.md` §1, the cursor, and `CAMPAIGN_EXECUTION_RECORD.md` §38–§52.
4. `cat docs/REMOTE_CONTROL.md` — act on anything unactioned, log what you did, push.
5. Check whether the Anthropic top-up landed; re-run `docs/ops/budget_watch.py`.
6. `bash docs/ops/publish_status.sh` and confirm the page reads correctly.
7. **Then set your rhythm: the cycle every 2 minutes, the status publish every 5, a deep audit
   several times a day, and the write-up in between.**

---

**Tamer's bar, in his own words: *absolutely everything must be 100000000000 % strictly absolutely
flawless. Always verify yourself many times. Ultrathink. Be 100000 % confident.***

He means it literally. So: **ultrathink exhaustively · act surgically · state only what you measured ·
verify your own work · then verify that what you measured is correct, consistent, and logical.** And
begin every message to him with his name.
