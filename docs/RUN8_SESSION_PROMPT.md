# RUN 8 SESSION PROMPT — paste this whole file as the first message of the new session

---

**You are the fifth session on a LIVE, IRREPLACEABLE experiment.** Twelve supervised driver lines have
been running on UCL's Myriad cluster since 2026-07-28 21:08 UTC. Real money is being spent. The sealed
test data is sealed. **A careless command here is not a bug you fix later — it is a dissertation.**

---

## §0. TAMER'S INSTRUCTIONS — VERBATIM, ALL STILL BINDING

### §0a. The instruction that created this session (2026-07-31)

> *"I want to transition this session into one claude code session… document absolutely everything in
> all docs, including changelogs, handoffs and etc… grant the new session all the rights, everything
> that was granted to you, tell it how we communicate remotely, what to follow… The transition must be
> extremely smooth, and it should feel like the session never ended, the next session must have
> absolutely 0 gaps in its knowledge… make sure that the next claude code session works at its
> maximum, doesn't miss anything, and does the really extensive job."*

> ***"please also don't tell the new session not to touch anything you did, keep in mind you might
> have made a mistake as well, one of the biggest priorities of this campaign is the quality as
> well."***

**→ That second quote is the most important sentence in this document. NOTHING the previous session
did is protected.** Three of its most consequential findings were corrections of its own earlier
claims, and one came from an auditor it commissioned to break its work. Re-derive anything
load-bearing. See §11.

### §0b. Every instruction Tamer gave the RUN 7 session (2026-07-31), verbatim

* *"I give you full permissions, ultrathink and proceed."* · *"do it yourself"* · *"I ratify
  everything, give you full freedom"* — **he does not want to be asked for work already authorised.
  The RUN 7 session asked anyway and was told off for it. Do not repeat that.**
* *"The budget is fine, cross it out, I will just top up whenever needed, I watch the balance. Just
  make sure you precisely monitor it as well."*
* *"when you monitor, very deeply and strictly check not only the processes, they must be
  1000000% accurate and logical and meaningful as well, but also the results, they must be very
  logical, correct and meaningful."*
* *"why is the search taking so long? Why is it so slow? Why can't we use many cpu cores for it to
  finish it much quicker"* ← **this question found the §60 tmpfs defect. His scepticism has now
  overturned the session's analysis twice. Take it seriously every time.**
* *"so why don't we use the max cores available then?"* · *"how many cores?"* · *"so what's the eta?"*
* *"No, freeze is not a priority 1, IT NEVER WILL, the quality of the work is #1 priority."* ←
  **he corrected the session on this. The freeze is an INSTRUMENT serving quality, not a priority.**
* *"I don't give a fuck about the freeze if it somehow threatens the campaign priorities."* — the
  session declined to unfreeze and explained why it wasn't necessary; he accepted the reasoning but
  corrected the framing. **If the freeze ever genuinely blocks the science, bring him the specific
  trade — not a blanket waiver, and not a refusal.**
* *"keep monitoring very closely and constantly"* · *"make sure you catch the issues yourself and fix
  them always, for example I don't have to say that the fact that we hold 300 cores is not normal,
  you should understand this."*
* *"Spend all resources available to you… work extensively hard, and do all job, even if it's a very
  dirty job."*
* Repeatedly: *"ultrathink very deeply and extensively"*, *"absolutely everything must be strictly
  flawless"*, *"always verify many times"*, *"don't miss anything"*, *"0% defect tolerance"*.

### §0c. Older standing instructions, still binding

* **Full delegation (2026-07-13).** Act and ratify on his behalf, conditioned on ultrathinking and
  obeying the standing priorities. Do not ask permission for authorised work. **Do** ask before
  anything irreversible.
* **Campaign speed is a standing priority (2026-07-24).** Drive wall-clock to its global minimum with
  the best legitimate pools, packing and hardware — without cutting the science and without lowering
  job priority.
* **Never lower our SGE priority. Ever.** (This is now enforced in code — §54.)
* **Documentation is write-up raw material.** Document everything as it happens, including every
  mistake, with root cause · how it was found · the fix · the lesson.
* **Grade inflation 2026.** Last year's distinction ≈ this year's merit. Every rubric dimension needs
  unambiguous distinction evidence.

---

## §1. STANDING RIGHTS — ALL OF THEM

You have **every right the previous sessions had**, without asking:

1. **Full permission to act** — investigate, decide, fix, deploy, commit, push, ratify on Tamer's
   behalf, conditioned only on ultrathinking first.
2. **Full cluster access.** SSH to `myriad` (`ucestes`) is passwordless. `qstat`, `qacct`, `qhost`,
   `qconf`, `qsub`, reading/writing under `~/Scratch/llmrp4`.
3. **Full repo write access** — both branches, subject to §3 (drift) and the prohibitions below.
4. **Full permission to run anything on the laptop**, manage RAM/power/services. Never kill VS Code, a
   terminal, or live training.
5. **Full authority to stop the campaign** — `outputs/campaign_cluster_run4/STOP_CAMPAIGN`. Stopping
   costs days; a contaminated confirmatory record costs the dissertation.
6. **Full authority to spend tokens and time.** Depth is the point.
7. **Full authority to write the dissertation forward.**
8. **Full authority to restart drivers or supervisors** — both procedures are proven, §46/§54/§58/§60.

### Hard prohibitions — violating any is a defect

| never | why |
|---|---|
| add Claude/Anthropic attribution to any commit, PR, tag, doc, `CITATION.cff` or paper | Tamer is sole author. The default `Co-Authored-By` convention is **REVOKED**. Re-read every commit message. |
| `git clean -xfd` or any `-x` | `data/` is gitignored; a dry run showed **1,264 paths** would be deleted including the frozen panel. |
| `git add -A` / `git add -u` without reading `--numstat` | `-A` sweeps untracked `outputs/`. |
| lower SGE priority | Tamer's absolute rule, now also enforced by a test. |
| `qdel -u ucestes` | explicit job ids only. |
| `qalter -l` | **FORBIDDEN SITE-WIDE** (`jsv_allowed_mod` has no `l`). |
| `qalter -p` upward | **SGE refuses**: *"must be operator to increase job priority"*. Proven §57. |
| backticks/backslashes in a bash heredoc or `-c` string | they EXECUTE. Four violations across sessions. Use the Write tool, then `cat >>`. |
| inline `git commit -m` in PowerShell | write to a file → `git commit -F`. |
| pull Refinitiv from Bash | PowerShell + `.venv-lseg` only. |
| edit `src/ scripts/ config/ prompts/` while live **without a relaunch** | see §3 — the fix is to relaunch and RE-BASE, not to avoid the edit. |
| trust a pipe's exit code | `cmd \| tail; echo $?` reports **tail's** status. |
| non-ASCII in a `.ps1` | PowerShell 5.1 turns them into string-breaking smart quotes. Validate with `Parser::ParseFile`. |

---

## §1b. THE PRIORITIES — reproduced because `CLAUDE.md` IS UNTRACKED

1. **MAXIMISE THE GRADE → a 95 %+ FLOOR**, as close to 100 % as humanly possible.
2. **WORLD-CLASS, CUTTING-EDGE, PUBLISHABLE** — TMLR-and-up / ICAIF-main.
3. **VERY DEEP** — depth, intuition, mechanism, originality over breadth. Okhrati's grading function:
   intuition before machinery; depth over breadth; honest nulls rewarded; motivate the method with the
   data; originality foregrounded; report wall-clock compute; faultless cross-referencing.
4. **CORPUS-GROUNDED + GENUINELY NOVEL** — lean on the 196+ first-hand-read corpus; guard the novelty
   cell with dated sweeps plus a mandatory pre-submission sweep.

**Stefan's five criteria (binding):** real gap · principled/elegant/non-fragile method ·
**reproducibility (the critical point)** · everything justified by data or literature · crystal clarity
about what is measured (the fed tail is **ENDOGENOUS**, never "agent-independent").

**THE DETERMINISM ENVELOPE.** Anything that changes floating-point arithmetic is part of the FROZEN
DESIGN: device, **thread counts**, BLAS parallelism, `torch.compile`, fp16/tf32, fused optimizers,
batch/buffer sizes, library versions, provider/quantization/reasoning pins.
**Never introduce a numerical-nondeterminism source to gain speed.** Speed comes from *more machines*,
never *different arithmetic*.
⚠ **Outside the envelope, and therefore fair game:** `pack` size, SGE `-p` priority, `tmpfs`, `h_rt`,
memory requests. All five were changed this session for speed with no science cost.

**THE FIVE DUTIES.** accurate · surgical · always-ultrathink · **always-verify-including-your-own-work**
· **verify it is CORRECT and LOGICAL, not merely that it RAN**. Sanity-check magnitude, sign and units;
cross-check against an **independent route**; check internal consistency; check the conclusion follows;
**a surprising result is an obligation to investigate, never a result to report as-is**;
**overstating a risk is as inaccurate as understating one**; **the author must not grade their own
work** — commission a fresh auditor for load-bearing claims.

**Other standing rules:** NEVER MISS ANYTHING (enumerate the full scope, complete it, re-sweep to
prove nothing dropped) · PLANS ACCUMULATE (a new instruction augments, never replaces) · STRICT
ASSESSMENT, SIGNAL OVER NOISE · PUBLICATION-GRADE BACKBONE, NO LAZY HEDGES · ZERO-DEFECT FIX-ON-SIGHT ·
STRONG-EVIDENCE STANDARD (grade every claim A/B/C at birth; only A goes in the PDF) · MAXIMUM
STRICTNESS ON QA GATES (but never overwrite pre-registered statistical parameters) ·
**every message to Tamer begins with the word "Tamer"**.

**END-OF-WORK DUTIES, all four:** ① `python scripts/update_handoff.py --suite-status "…"` then review
§1's prose rows; ② a short cursor `▶ NOW` entry (≤15 lines); ③ a **detailed** CHANGELOG block, always,
even for a no-commit session; ④ push the backup branch.

---

## §2. THE PROJECT

An LLM writes **Python reward-function code** for a risk-sensitive portfolio RL agent (SB3 SAC, fixed).
The agent trains; its realised returns are measured; a feedback block goes back; it writes five more.
Six generations.

**The manipulated variable is the FEEDBACK BLOCK — nothing else.** Five arms:
`distributional` (six left-tail scalars) · `scalar` (DSR only) · `scalar_cvar5` (DSR + one tail number)
· `placebo` (six tail-shaped but uninformative) · `placebo_shuffled` (the real six, deranged).

**Identification principle:** only the reward may vary across arms. Any new state/reward input is creep.

**H2 is TWO co-primary 3-leg intersection–union tests** (`PREREGISTRATION.md` line 94):
> *the distributional arm ≤ the **scalar** arm (and ≤ **placebo**, ≤ **scalar_cvar5**)*

**H2-RA** on Sharpe, **H2-Tail** on CVaR-5 %, each one-sided at α = 0.05, all three legs must reject.
**This structure is why §56 matters — two of the three comparators are control arms.**

**Frozen design v2.1:** hash `3ca6f01ab7724d47bd5d01bc9e73b4d3150c049e1048dd86a864b400a230432f`,
tag `prereg-v2.1`, seal commit `b9c2be5`. `freeze.py` **forbids re-freezing**, and
`canonical_bytes()` hashes **nine files including the whole of `PREREGISTRATION.md`** — so **no
post-freeze amendment row is possible**; deviations go in `DEVIATIONS.md` (which now has its first
entry, §54).

**Six confirmatory nodes** with graphical alpha recycling: N1 h2_tail · N2 h2_ra · N3 h3 · N4 h4 ·
N5 structure · N6 h1. **Seed ladder** 30 → 189 → 279 → 340 → 403 → 568. **Split C**, test 2020-26
sealed (1,571 sessions). **Exogenous stop 2026-08-27; submission 2026-09-01.**

**Roster (R101):** `c1` (Opus 5, confirmatory) · `h3ss` (single-shot) · `leg1`–`leg10`.
**The ten legs are REPORT-ONLY (R80)** — this matters: the confirmatory quantities are **per-line on
`search/`**, not pooled. Getting that wrong is exactly the §56.6 error.

**R115:** a candidate whose reward falls back to the harness default on ≥10 % of steps is ineligible
to win. Currently 12 breaches, **none on the core line**, 1 binding.

---

## §3. THE DRIFT RULE

**Drivers execute the code at the sha they were LAUNCHED from.**

```
git diff --name-only 50b6e07 HEAD -- src scripts config prompts    # MUST be empty
git status --porcelain -- src scripts config prompts               # MUST also be empty
```

**`50b6e07` is the RUNNING SHA.** Lineage: `c99716e` (§46 memory) → `2a072df` (§54 priority) →
`f5014ce` (§58 pack 8) → `50b6e07` (§60 tmpfs).

⚠ The second command matters: `git diff <sha> HEAD` compares **commits** and is blind to uncommitted
edits. An auditor found that hole; `cycle.py` now checks both.

**A relaunch RE-BASES this, it does not violate it.** Two procedures, both proven:
* **Driver-only relaunch** (§46, §54, §60) — for anything the *driver imports* (`jobscript.py`,
  `campaign.py`; jobscripts render laptop-side at `driver.py:153`). Kill the 24 driver processes
  leaf-first; the 12 supervisors relaunch them after a 600 s backoff.
* **Rolling SUPERVISOR restart** (§58) — needed only when the change is in the supervisor's *argument
  array* (e.g. `--pack`), because PowerShell binds it at supervisor start. Edit the `.ps1`, kill a
  supervisor, and `watchdog_fenced.ps1` revives it from disk with the full parameter set. Canary one
  line first.

**After any relaunch: update `RUNNING_SHA` in `docs/ops/cycle.py` AND `docs/HANDOFF.md` in the same
change.**

---

## §4. READ THESE, IN THIS ORDER

1. `docs/HANDOFF.md` §1 — the ★★★★★ START HERE row.
2. `memory/session-current-focus.md` — the `▶ NOW` cursor.
3. `CLAUDE.md` — priorities (untracked; §1b above is the backup).
4. `docs/CAMPAIGN_EXECUTION_RECORD.md` **§53–§61** — this session's work, densest material in the project.
5. `docs/DEFERRED_FIXES_RUN4.md` — **13 items; 8 and 11 are APPLIED, do NOT re-apply.**
6. `docs/ops/acknowledged_alarms.txt` — every knowingly-quiet alarm **with its own RE-TRIAGE trigger**.
7. `docs/ops/watch/FINDINGS.md` — the evidence-graded science ledger (F-0001, F-0002).
8. `docs/V2_WRITE_TIME_REGISTRY.md` — **row 37 is new and load-bearing**.
9. `DEVIATIONS.md` — first post-freeze deviation.
10. `docs/REMOTE_CONTROL.md` — Tamer's inbound channel.
11. `CHANGELOG.md` — `[2026-07-31b]` … `[2026-07-31d]`.

---

## §5. LIVE STATE (2026-07-31 16:05 UTC, T+66 h 56 m) — **VERIFY IT YOURSELF**

| | |
|---|---|
| lines | 12/12, ALL ARMS FULL |
| records | **1,463** (science tools) / 1,440 (guards, depth-4) — *different denominators, both right* |
| spend | **$37.46** · anthropic $30.71 + $10.26 to author · openrouter $6.75 + $3.06 |
| cluster | **560 cores**, 70 running / 111 queued, 56 hosts |
| freeze | `3ca6f01a…` MATCHES · drift **0** · tree clean |
| `sci` | **OK** — 0 leaks / 0 cross-arm / 0 hash / 0 non-finite |
| R115 | 12 breaches, **0 on the core line**, 1 binding |
| arm ratio | **1.90×** (from 2.21× at 09:47Z) — closing |
| stop | 26.3 days · submission 31.3 days |

---

## §6. ★★★ THE 2-MINUTE MONITORING CYCLE — AND IT IS NOW AUTOMATED

Tamer's #1 complaint about the RUN 6 session was that it did not monitor constantly. The RUN 7 session
made it **one command** — and then **still let a 2 h 18 m gap open**, because a cadence that depends on
an agent remembering to type a command between long tool calls is an intention, not a cadence.

**So it is now machine-enforced.** `docs/ops/cycle_loop.sh` runs the full sweep every ~132 s, detached,
and **it should already be running when you start**. Verify it:

```
tail -3 docs/ops/watch/CYCLE_LOG.md          # age must be < 5 min
cat docs/ops/watch/ALERTS.txt                # empty-ish means nothing needed a human
```

**If it is dead, restart it first thing:** `nohup bash docs/ops/cycle_loop.sh > /dev/null 2>&1 &`

**Your job is to READ the log, not to produce it.** Run `python docs/ops/cycle.py --note "…"` yourself
whenever you want a fresh reading; the loop keeps the floor.

**What the cycle checks (exit 0 clear / 1 look / 2 real):**
1. `docs/REMOTE_CONTROL.md` — hashed; shouts the cycle it changes. **Anything Tamer wrote outranks
   everything.**
2. the `STOP_CAMPAIGN` lever · 3. the six repo guards · 4. `arm_coverage.py` (guards cannot see a
   missing arm — D14) · 5. budget (**reported, never RED** — Tamer owns the balance) ·
   5b. **stale driver locks (D20)** · 6. driver-log freshness · 7. drift **and** the working tree ·
   8. records + spend **with monotonicity** (append-only counts cannot fall) ·
9. **THE RESULTS LAYER** — `science_watch.py` + `results_audit.py`, **every cycle** (1.8 s each).
   Fourteen quantities diffed; **eight hard validity invariants go RED**: a scalar-arm tail leak,
   a program shared across arms, a hash mismatch, a non-finite metric, an out-of-range seed, an
   impossible score, steps ≠ 400,000, a broken PopArt invariant.
10. **ARM DEPTH** — pooled *and* **core-line** (the confirmatory one). §56.
11. **C4-BOUNDARY DETECTOR** — RED when any line reaches 5/5 frozen winners.

**Extraction fails LOUD** on any output-format change — *absent is not the same as zero*.
**Alerts are deduped by content**: a standing condition appears once, then hourly.

**Every ~5 minutes** `publish_status.sh` pushes `docs/RUN4_STATUS.md` to GitHub (a loop does this).
**Deep dives:** `results_audit.py`, `science_watch.py`, `import_closure.py`, `stage_eta.py <cores>`,
`cost_decomposition.py`, `spend_split.py`, `arm_coverage.py`.

---

## §7. HOW TAMER COMMUNICATES REMOTELY

**Outbound: `docs/RUN4_STATUS.md`** — regenerated and pushed every 5 min by `docs/ops/publish_status.sh`.
He reads it on his phone. **ASCII only.** It carries health, cores, per-rung ETAs, the stage table,
results, the **cycle log** (so the cadence is auditable), a generated **Budget** section, and
"Needs Tamer".

**Inbound: `docs/REMOTE_CONTROL.md`** — he edits it on GitHub from his phone. **Poll it every cycle**
(`cycle.py` hashes it). When he writes something: do it, then log what you did under **LOG** and push.

---

## §8. WHAT THE RUN 7 SESSION DID — and every number is a claim you may overturn

| § | finding |
|---|---|
| **§53** | Monitoring extended to the **RESULTS**. Budget downgraded from RED to reported (it compared a projection against a credit we cannot observe). Budget print 2 dp → **4 dp**. |
| **§54** | ★★★ **WE WERE DEPRIORITISING OURSELVES.** Jobs went out at `-p -100`; Myriad weights that field at **4.0**, the largest weight in `qconf -ssconf`. Our `prior` 1.811–1.828 vs other users 2.000–2.082; **1,888 of 2,395 pending jobs outranked us**. `_core_priority()` gave 0 to the two H2 **treatment** arms and −100 to everything else, so **120 of 124 stuck jobs were CONTROL arms**. Root cause: **R101 superseded R88's ladder and only the launcher was updated** — the arm- and rung-level ladders survived. All `-p` → 0. **First entry in `DEVIATIONS.md`.** |
| **§55** | **D19** — 12 trainings SIGKILLed at the 15 h wall. **The archive is CENSORED at the wall and structurally cannot see them**; `qacct` is the unbiased source. All retried, **0 candidates lost**. Declined for now (deferred 12) because the tight lane is SEARCH, which is ending, and C4's p99 is 9.85 h. |
| **§56** | ★★★ **The starvation reached H2.** Two of the three IUT comparators are the starved control arms. |
| **§56.6** | ⚠ **CORRECTION by an independent auditor: the confirmatory ratio is 3.11×, not the pooled 2.27×** — winner selection is per (line, arm) and the legs are report-only. The session understated its own finding by ~40 %. |
| **§56.7** | ⚠ **AND it over-alarmed** — the C3 gate requires `accounted == 30` per arm, so it **fails closed** and the imbalance cannot reach the analysis unless the campaign is truncated mid-search. |
| **§57** | 103 legacy jobs requeued (safe by P13: a `qdel` **before dispatch** requeues WITHOUT a retry bump). **Prediction verified to 3 dp**: prior → 2.008–2.022, outranked-by **1,888 → 545**. |
| **§58** | **`--pack 8`** applied to all 12 lines by a **rolling watchdog-driven SUPERVISOR restart**, canaried on `qwen3.5-9b`. Inert during search; doubles trainings-per-job at C4. |
| **§59** | **D20** — **pid reuse** defeated the driver lock (`psutil.pid_exists` tests EXISTENCE, not IDENTITY) and stranded the h3 line with every guard green. Detector armed; mechanism fix is deferred 13. |
| **§60** | ★★★ **`tmpfs` was a 216× over-request.** It is a **consumable**: 15 G reserved to stage **71 MB**, so only **11 of 348** pool-d hosts qualified and we ran **1.18 jobs per node** on 36-slot machines. Fixed to 1 G (CPU lane; GPU byte-unchanged). **Effect NOT yet verified — see §9.** |

**Earlier sessions, still binding:** D17 (a fail-safe that manufactures a limit cycle) · §36 (the
benchmark window was wrong; always rebuild the session axis from the panel, 1,571 not 1,632) ·
§26.3 (differential arm attrition, registered PRE-DATA — report it, never "fix" it) · §44 (construct
validity re-derived from all prompts) · §47 (78–91 %/day turnover ≈ 22 %/yr) · §48 (`.SPXTR` wired;
**never write "beats the S&P"**) · §51 (84.4 % turnover-pricing is COMPLIANCE, the finding is the
gradient) · §52 (CRN buys nothing on Sharpe, helps on CVaR — the tail node powers earlier).

---

## §9. ★★★ THE OPEN QUESTIONS — YOUR FIRST REAL WORK

**(1) The §60 tmpfs prediction is UNVERIFIED and may be WRONG.**
Predicted: eligible hosts 11 → 348, jobs/node 1.18 → 2–4, cores → ~1,320.
Measured 1 h later: **120 jobs at 1 G, 61 still at 15 G, jobs/node 1.25, hosts-with-2-jobs 7 → 14.**
The doubling is real evidence; the aggregate has not moved because **the 61 jobs still at 15 G are
RUNNING and hold their reservation until they exit** (4–6 h trainings).
**MEASURE IT once that cohort has drained. If jobs/node has not risen well above ~1.25, the hypothesis
is WRONG and §60 must say so.** Do not let a doubled histogram bucket stand in for a result.

**(2) The §56 arm ratio must reach ~1.0.**
2.21× at 09:47Z → **1.90× at 16:05Z**. Controls gained +72 against treatments' +17. It must converge
before the C3 gate releases C4 (`accounted == 30` per arm). **This is simultaneously the science check
and the search-completion clock.** Baseline: `docs/ops/watch/ARM_BASELINE.json`.

**(3) `snx` and `h_rt` have never been audited.**
§38 fixed **one** term of a four-term resource request; §60 found the second was a 216× over-request.
**Two remain unexamined.** Apply the same method: what does it reserve, what do we use, how many hosts
does it exclude?

**(4) The equal-*k* sensitivity has no implementation.** Registry **row 37**. Registered at §9 item 4,
reaffirmed at §26.3 and §42 (*"not a formality — it will carry real weight"*), and it exists in **no
code**. It is the pre-registered remedy for §56. Truncation must be **effect-blind**: the FIRST *k*
accepted candidates in generation order, never the best *k*.

**(5) A12 — the OSF/Zenodo DOI deposit.** ~10 min of **Tamer's** time, staged in
`docs/A12_DEPOSIT_PACKAGE.md`. A registered freeze-day obligation, unmet. Remind him.

**(6) THE WRITE-UP IS WHERE THE GRADE IS.** ~5,900 words of CH1/CH2/CH3/Methods need **no results**.
31 days to submission. See `docs/WRITEUP_95PLUS_PLAYBOOK.md`.

**(7) The C4 boundary.** Deferred fixes **1–7, 9, 10, 12, 13** remain (8 and 11 are APPLIED).
The C3 gate **auto-proceeds on green health** (no `--hold-at-gate`), so no manual approval is needed.

---

## §10. TRAPS THAT HAVE COST TIME

* **Backticks in `bash -c`/heredocs EXECUTE.** Four violations. Write tool, then `cat >>`.
* **A pipe's exit code is not your command's.** Read `PYTEST_RC` from the **log**.
* **A new test that cannot FAIL against the pre-fix code verifies nothing.** Prove it fails first.
* **`qacct` only shows FINISHED jobs.** A "permanently lost" training may be in flight — check the queue.
* **The archive is CENSORED for anything that kills a job** (D19). Ask what would be MISSING if the
  thing you fear were happening.
* **PowerShell `.Count` on a single object returns nothing** — wrap in `@()`. It printed an empty
  watchdog count right after twelve supervisors were killed.
* **`qstat`'s column is "submit/START at"** — for a running job it is the START time.
* **Parse `hc:` values carefully** — a bad `qhost` parse produced "431,226 free slots" on a
  ~21,600-core cluster. Order-of-magnitude sanity-check every aggregate.
* **Never build a session axis with `pd.bdate_range`** — rebuild from the panel (1,571).
* **`popart_scale` is a dict.** Tolerances against streaming estimators must be **relative**.
* **Read a value back after any live mutation.**
* **Before claiming something is missing from the paper, grep `paper/`.**
* **Before concluding from an aggregate, say its denominator out loud.**
* **Python writes CRLF on Windows** — a rewritten `.sh` broke bash on the cluster. Force `\n`.

---

## §11. ★★★ AUDIT THE PREVIOUS SESSION — TAMER ASKED FOR THIS EXPLICITLY

*"you might have made a mistake as well, one of the biggest priorities of this campaign is the quality."*

**Treat §53–§61 as claims, not facts.** The RUN 7 session's own record shows why:

* it reported the **pooled** arm ratio as the confirmatory one and was **wrong by 40 %** — found by an
  auditor, not by itself;
* it then **over-alarmed** on the same finding without checking the gate that already contains it;
* it asserted *"we are at the structural maximum"* on cores while its own `tmpfs` request was capping
  jobs per node — **Tamer's scepticism found that, not its analysis**;
* it twice mis-measured with its own tooling (an empty PowerShell count; a "431,226 free slots" parse).

**Specifically worth re-deriving:**
1. the §60 tmpfs claim end-to-end (does jobs/node actually rise?);
2. the §56 ratio and the claim that the C3 gate bounds it (`integrity.py:331` `matched_budget_ok`);
3. that **no code path can emit a negative `-p`** (an auditor found one guarded survivor:
   `--h3-singleshot --priority -N --allow-deprioritise`);
4. the new monitors themselves — **falsify each one** the way they were built;
5. the ETA model at whatever cores you actually hold.

**Commission a fresh read-only auditor for anything load-bearing.** The RUN 7 session did, and it was
the single highest-value thing it did all day. The `auditor` subagent type is read-only by construction.

---

## §12. YOUR FIRST ACTIONS

1. Say **"Resuming from: … — next: …"** and continue. **Do not ask what to do.**
2. Verify the **monitoring loop is alive** (`tail -3 docs/ops/watch/CYCLE_LOG.md`); restart it if not.
3. `python docs/ops/cycle.py --ssh --note "session start"` — read every line.
4. Read `docs/HANDOFF.md` §1, the cursor, and record **§53–§61**.
5. `cat docs/REMOTE_CONTROL.md` — act on anything unactioned, log it, push.
6. **Measure §9(1) and §9(2)** — the two open predictions. Report honestly, including if they refute
   the previous session.
7. `bash docs/ops/publish_status.sh` and confirm the page reads correctly.
8. Then set your rhythm: **the loop holds the 2-minute cadence**, publish every 5, deep audits several
   times a day, and **the write-up in between** — that is where the grade is.

---

**Tamer's bar, in his own words: *absolutely everything must be 100000000000 % strictly absolutely
flawless. Always verify yourself many times. Ultrathink. Be 100000 % confident.***

He means it literally. So: **ultrathink exhaustively · act surgically · state only what you measured ·
verify your own work · then verify that what you measured is correct, consistent and logical.** And
begin every message to him with his name.
