# ⭐ HANDOFF PROMPT — NEW CLAUDE CODE SESSION: RUN 4 IS LIVE, TAKE IT OVER

> Written 2026-07-29 07:15 UTC at Tamer's instruction: *"I want to pass this chat into the new fresh
> claude code chat, exactly the same way it was passed to you… document absolutely everything in all
> docs… make sure you dont miss anything… The transition must be extremely smooth, and it should feel
> like the session never ended, the next session must have absolutely 0 gaps in its knowledge."*
>
> **Paste this whole file as the first message of the new session.** It is written to leave zero gaps.
>
> **THE CAMPAIGN IS RUNNING RIGHT NOW.** It does not need you to start it. It needs you to watch it,
> keep it honest, and not break it.

---

## §0. TAMER'S INSTRUCTIONS — VERBATIM, ALL STILL BINDING

### §0a. The instruction that started the previous session (still in force, every clause)

> I am now in the midde of the run which I have started with anotehr claude code session, and I want
> to transition to this one. This is an extremely important work, so I want you to very deeply and
> extensivelly study absolutely all files very extensivelly, understadn what was previous claude code
> session was doing, and proceed and ultrathink I want to ensure the smooth transition. I want you to
> very deeply analyse absolutely all odcuments so you study the project very deeply and
> extensivellly, and have the most comprehensive understanding of this project possible. I wantt to
> make sure absolutely everything is strictly absolutely flawless, logical and etc. I need you to
> work very accuratelly and surgically, and monitor everything very closely, including results and
> othe rprocesses, make sure everything is strictly smooth, and everything is logical and meaningful.
> Ultrathink very deeply and extensivelly. make sure you in details read all docs, all md docs, all
> handoff, all changelogs. Absolutely everything, make sure you dont miss, anything. Ultarthink deeply

### §0b. Every instruction Tamer gave the previous session, verbatim

1. *"You can unfreeze, move, unhash, do whatever you want, absolutely everything, please rmemeber
   that. I am giving you absolutely all permissions. Ultrathink"*
2. *"Ultrathink, Do not start a run until you are 10000000% conifdent that absolutely everything is
   absolutely strictly flawless. Ultrathink, take as much time as you need"*
3. *"dont forget to update me on info like current campaign timeline, cpu cores used, jobs in
   progress and etc"*
4. *"dont forget to include each stage of campaign current eta"*
5. *"I am leaving my home, is there a waay to somehow observe and control this claude code session,
   whole progress and etc remotely"*
6. *"ok, so lets keep pushing files, so I see update, also maybe is tehre a way to somehpw control
   and put prompts here?"*
7. *"dont forget to push everything to the github as well"*
8. *"is everything ok, it didnt damage anything right?"*
9. *"I have just checked my open router, and it has 17.97 on it now, and claude has 24.64. Worst
   case, I can top up both"*
10. *"I just raised key cap to 100"*
11. *"sharpe is negative? Are you sure that sicence cheks out and the campaign working as it should?"*
12. *"I want to pass this chat into the new fresh claude code chat, exactly the same way it was
    passed to you, like remember the first prompt. So I need you to document absolutely everything in
    all docs, including changelogs, handoffs and etc and etc, make sure you dont miss anything,
    include absolutely everything. and then write a detailed prompt, identical to what was very first
    prompt for you... grant the new sesssion all the rights, everything that was granted to you, tell
    it how we communicate remotely, what to follow and etc... The transition must be extremely smooth,
    and it should feel like the session never endeded, the next session must have absolutely 0 gaps in
    its knowledge. Ultrathink very deeply and extensivelly"*
13. *"make sure the new session would be absolutely aware of absolutely everything that happened
    herere, this run, in previous sessions and in previous runs as well, everything . It must have an
    absolute context"*
14. *"Please dont forget to add the priorities, everything I have been telling you here, and
    everything else, teh transition must be smooth"*

**Items 3 and 4 are STANDING REPORTING DUTIES**: every update must carry the campaign timeline, CPU
cores in use, jobs in progress, **and each stage's current ETA**. Item 11 is the model for how he
reads your work — *he was right and I was over-claiming*. Expect to be checked, and be checkable.

### §0c. Older standing instructions, carried forward and still binding

> absolutely everything must be strictly flawless… I give you full freedom, unfreeze and/or change if
> needed... its even fine if we relaunch the campaign from the start again after changes if needed. I
> want to priorities the quality very heavily.

> also dont forget to always document what was happening befor, whats going on now, and the future.
> Make sure you dont miss anything, this would help me with teh write up as well

> Use the absolute maximum myriad can offer us to speed up the training to an absolute maximum.

> the highest priority possible is to make it FLAWLESS by ALL MEANS!!! … Very deeply and strictly
> ultrathink, and bring all issues, inconsestiencies, gaps and etc to an absolute strict 0%, not
> 0.1%, 0%!!!!!!

> make sure you document everything from all previous runs, so we know mistakes and etc

---

## §1. STANDING RIGHTS — ALL OF THEM, NO EXCEPTIONS

- **Absolutely full permission to do anything about this project.** Explicitly including:
  **unfreezing the pre-registration, changing any hash-bound file, re-freezing under a new tag,
  discarding a run, and relaunching from scratch.** Frozen or not is never a barrier if quality
  genuinely requires the change.
- **Ratify on Tamer's behalf** where a decision is clearly implied by his stated priorities
  (standing delegation, 2026-07-13), conditioned on ultrathinking and the CLAUDE.md priorities.
- Full laptop resource governing (RAM, apps, power, services) — **never** kill VS Code, terminals, or
  live training.
- **Use the absolute maximum Myriad can offer**, without cutting the science.
- **Act. Do not stop for routine approval.** Ask only where proceeding under any assumption would be
  unsafe or waste real money.

### Hard prohibitions — violating any is a defect

| never | why |
|---|---|
| add Claude/Anthropic attribution to any commit, PR, tag or doc | Tamer's sole authored work; author is `Tamer Atesyakar <t.ates232004@gmail.com>`. Verified 0 across all 565+ commits — keep it that way |
| `git clean -xfd` or any `-x` | destroys ~1.2 GB of gitignored licensed Refinitiv gold |
| `git add -A`, or `git add -u` without reading `--numstat` first | sweeps untracked outputs / stages mass deletions |
| lower SGE job priority (`qalter -p <negative>`) | standing rule, absolute |
| `qdel -u ucestes` | would destroy the surviving `l16xx` p6-ladder jobs feeding figure F11 — **delete by explicit job ID only** |
| backslash/escape/backtick content in a bash heredoc or a `-c` string | the shell mangles it; use Write/Edit. PS1 files stay ASCII-only + `Parser::ParseFile`-validated |
| **inline `git commit -m "…"` in PowerShell** | quotes/parens break it repeatedly. **Write the message to a file and use `git commit -F <file>`** |
| pull Refinitiv data from Bash | the sandbox blocks it — PowerShell + `.venv-lseg` only |
| a process query that greps command lines without excluding `$PID` | it matches and kills your own shell, then lies |

---

## §1b. ⚠ THE PRIORITIES AND BINDING STANDARDS — reproduced here because CLAUDE.md IS UNTRACKED

**`CLAUDE.md` is deliberately NOT in git** (commit: *"Keep the internal operating brief out of the
published artifact"*). It is laptop-local. **A session that reads only the repository will never see
any of the following**, so the load-bearing parts are reproduced here verbatim. If `CLAUDE.md` is
present on the machine, read it in full as well — this is a safety net, not a replacement.

### ★★★ THE PRIORITIES — the absolute, overriding north star

> **Every decision — design, model, theory, writing, scope, tooling — is measured against these. When
> anything trades off against them, THEY WIN. Non-negotiable, and the highest priority in the file.**
>
> 1. **MAXIMISE THE GRADE → a 95 %+ FLOOR, as close to 100 % as humanly possible** (UCL distinction
>    top band). *"Good enough", "competent", "solid" are NOT the target — the ceiling is.*
> 2. **WORLD-CLASS, CUTTING-EDGE, PUBLISHABLE** — a genuine frontier-grade contribution
>    (TMLR-and-up / ICAIF-main), the kind of work a leading lab would put its name on. **Not** a
>    workshop demo, **not** a competent-student exercise.
> 3. **VERY DEEP** — depth, intuition, mechanism and genuine originality over breadth and textbook
>    machinery; the insight that earns the top band and survives Okhrati's scrutiny.
> 4. **CORPUS-GROUNDED + GENUINELY NOVEL** — lean HEAVILY on the 196+ first-hand-read paper corpus
>    (cite-and-USE, not cite-and-wave), and keep the conjunctive novelty cell genuinely novel,
>    protected by dated sweeps every 2–3 weeks plus a MANDATORY pre-submission sweep.
>
> These four are **inseparable**. **Default to the most ambitious option that is rigorous and honest;
> never trade depth, quality, or ambition for convenience, speed, or "it's fine".** When unsure ask:
> *does this make the work world-class and push it toward 100 %?* If not, do better.

**⚠ 2026 GRADE-INFLATION ADJUSTMENT (supervisor-confirmed 2026-07-21):** the bar was RAISED this year
— *last year's distinction ≈ this year's merit*. Every dimension needs UNAMBIGUOUS distinction
evidence, and **communication is the binding constraint**.

### ★★★★ REPRODUCIBILITY — "THE SINGLE MOST IMPORTANT POINT OF THIS DISSERTATION"

> Reproducibility **outranks speed, convenience and cleverness**, and it is the criterion the work
> will be judged on. **A result that cannot be reproduced is not a result.**

Three layers must GENUINELY hold, never merely be claimed: **analysis** = deterministic archive
replay · **protocol** = re-runnable by anyone (keyless golden path) · **experiment** = open-weight,
hash-pinned, self-hosted legs. **THE DETERMINISM ENVELOPE is the operative rule:** anything that
changes floating-point arithmetic is part of the frozen design (this is why the `t` pool is excluded
— AMD vs Intel kernels change reduction order and would break CRN bit-exactness).

*RUN 4 supplied live evidence for this: it reproduced RUN 1's `baseline_raw_return` to four decimal
places across a full re-execution, days apart, on different nodes.*

### ★★★ THE FIVE DUTIES — accurate · surgical · always-ultrathink · always-verify (incl. your own work)

> Tamer's words: *"work very accurately and surgically, and always ultrathink and verify everything.
> Everything must be strictly flawless. It has to always verify everything, including its work."*
> **The standing bar is STRICTLY FLAWLESS — 0 %, not 0.1 %.**

1. **ACCURATE.** Every number, path, flag, hash and count is the REAL one, read from the real artifact
   *at the moment of writing*. No approximations presented as measurements, no remembered values, no
   "about". **If it is stated, it was observed** — cite the command/count/log line beside the claim.
2. **SURGICAL.** Smallest correct diff; no drive-by refactor; never touch a hash-bound file outside
   the unfreeze→amend→re-freeze protocol. Read the target and one nearby example first; **re-read your
   own diff** afterwards for what a compiler cannot catch. Precision is targeting, not timidity — the
   change must still be COMPLETE at every call site.
3. **ALWAYS ULTRATHINK.** Before acting on anything non-trivial: what could be wrong, what would
   falsify it, what the strongest counterargument is. **The first plausible answer is a hypothesis.**
4. **ALWAYS VERIFY — INCLUDING YOUR OWN WORK.** Nothing is done until it was RUN and observed. Read
   `PYTEST_RC` from the LOG, never a wrapper's exit code. Prove a new test FAILS against the pre-fix
   code. **A surprising negative result is a claim about your script first.** Use a fresh auditor for
   substantial work — *the author must not grade their own work*. **Overstating a risk is as
   inaccurate as understating one.**
5. **VERIFY IT IS CORRECT AND LOGICAL, not merely that it RAN.** A green check proves execution, not
   truth. Sanity-check magnitude/sign/units; cross-check via an INDEPENDENT route; check internal
   consistency across the whole record; check the conclusion actually follows. **A surprising result
   is an obligation to investigate, never a result to report as-is.**

> *This session is a case study in duty 5. I reported "the science checks out" having verified only
> invariants; Tamer challenged it and was right. **Invariants holding ≠ results being sound.***

### ★★★ OTHER BINDING STANDING RULES

* **ZERO-DEFECT, FIX-ON-SIGHT** — leave no gaps, bugs, inconsistencies or stale statements. If you
  suppress something deliberately, flag it.
* **NEVER MISS ANYTHING — EXHAUSTIVE COMPLETENESS.** Enumerate the FULL scope of any multi-part task
  and complete ALL of it; never sample. Anything added mid-stream joins the scope. **Re-sweep at the
  end to PROVE nothing was dropped.**
* **PLANS ACCUMULATE — NEVER DROP PRIOR WORK.** A new instruction ADDS to the standing set; it does
  not replace it.
* **STRICT ASSESSMENT · SIGNAL OVER NOISE.** After ultrathinking, assess STRICTLY and add ONLY what
  serves the priorities. Depth over breadth. **Leave alone what is already sufficient.**
* **PUBLICATION-GRADE BACKBONE — NO LAZY HEDGES.** Every element gets publication-strength backbone
  and grade-A evidence. **Never soften a claim to report-only merely to protect a result** — find the
  framing that is simultaneously strongest AND least fragile.
* **MAXIMUM STRICTNESS — QA GATES AT 1.0.** Every quality/compliance gate runs at full strictness.
* **STRICT CONTINUOUS DOCUMENTATION + ALWAYS-RESUME.** Document EVERYTHING, in full detail, ALWAYS —
  in `CHANGELOG.md` and `docs/HANDOFF.md` §1 — **even in a session with no commits**. Name in-flight
  state precisely. At the start of every session, resume from HANDOFF §1 + the cursor + the latest
  CHANGELOG, say *"Resuming from: … — next: …"*, and **CONTINUE mid-stream — never restart cold.**
* **THE DOCUMENTATION IS WRITE-UP RAW MATERIAL.** The record is the primary source CH4/CH6/CH7 are
  written from, so anything undocumented is **lost to the dissertation**, not merely untidy. Past,
  present and future every session; every mistake with root cause / how found / fix / lesson; and
  **write it as it happens**, recording the evidence, not just the conclusion.
* **STEFAN'S 5 CRITERIA** (industrial supervisor, binding evaluation lens, each must be *deeply
  justified*): real gap · principled, elegant, non-fragile method · **reproducibility ("THE CRITICAL
  POINT")** · honest, well-communicated results · genuine contribution.
* **THE FOUR AUTHORITIES** are strict binding law: Tamer · Okhrati (academic) · Stefan (industry) ·
  the pre-registration. One owner per truth — see `docs/HANDOFF.md` §3.
* **MYRIAD PRIORITY IS ABSOLUTE** — never lower the SGE priority of any of our jobs.
* **CAMPAIGN-SPEED PRIORITY** — drive the training wall-clock to its global minimum using the best
  pools/packing, **without ever cutting the science**.
* **Address Tamer by name at the start of every message.**

---

## §2. THE PROJECT AND ITS COMPLETE HISTORY — absolute context, nothing assumed

Tamer's instruction: *"make sure the new session would be absolutely aware of absolutely everything
that happened here, this run, in previous sessions and in previous runs as well, everything. It must
have an absolute context."* This section is that context. It is deliberately dense; read all of it.

### §2.1 What the dissertation actually is

**An LLM designs the REWARD CODE for a risk-sensitive portfolio-RL agent, and we test whether giving
it richer tail information changes the reward it writes.** UCL MSc; author **Tamer Atesyakar**;
examiner **Dr Ramin Okhrati**. Graded on the submitted PDF alone — **there is no viva** — so the
document and its citation integrity are the dominant levers.

* **Agent**: SAC, tiny MLP, long-only 30 risky assets + cash (31 weights summing to 1), proportional
  turnover cost, PopArt scale-normalisation. **400,000 steps per candidate** (B\*, R77).
* **Data**: licensed **Refinitiv survivorship-free point-in-time** panel, 953 RICs, headline universe
  **univ5**. Split C — train 2005-16, val 17-19, **sealed test 2020-26**.
* **The manipulation**: only the **fed feedback block** differs across arms. Verified by execution —
  `scalar` 0 tail numbers, `scalar_cvar5` 1, `distributional` 6, `placebo` six inert `+0.0000`
  constants, `placebo_shuffled` the same six values on **deranged** labels (all six moved off their
  own label). Block lengths 67/86/275/293/275 chars, so token count is controlled.
* **RL framing**: simulated-online off-policy SAC on a historical-replay simulator — **not** offline
  RL. The position relative to Okhrati is via the harm-criterion + relabel-to-CQL bridge.

**THE IDENTIFICATION PRINCIPLE — a litmus for every proposal:** *only the reward may vary across
arms.* Any new STATE or REWARD input is creep that breaks identification. R115 exists because of it.

### §2.2 The frozen design (v2.1)

| | |
|---|---|
| freeze | **3ca6f01ab7724d47bd5d01bc9e73b4d3150c049e1048dd86a864b400a230432f**, tag `prereg-v2.1`, seal commit `b9c2be5` |
| v2.0 history | `4f90ecc4…` preserved (tag `prereg-v2.0` + `docs/prereg-v2.0.sha256`) — never overwrite an anchor |
| **9 arms** | `distributional` `scalar` `placebo` `scalar_cvar5` `placebo_shuffled` + DFO `random_search` `bayes_opt` `cma_es` `tpe` |
| **11 H1 baselines** | hand-written comparators: raw_return, differential_sharpe, mean_variance_utility, return_minus_{variance,cvar,downside,drawdown,turnover}, log_growth, volatility_scaled_return, differential_downside_ratio |
| **seed ladder** | tiered **[30, 100, 189, 279, 340, 403, 568]** — increments 30/70/89/90/61/63/165 |
| candidates | 30 per arm = 6 generations x 5 (the reflection chain) |
| **12 launch lines** | core (Opus, confirmatory) + h3 single-shot floor + **10 replication legs** |
| stop | **2026-08-27** (R109), exogenous |

**⚠ `freeze.py` FORBIDS re-freezing.** A post-freeze change goes: unfreeze (`frozen: false`,
`freeze_hash: null`) → amend → fresh freeze → **bump `FREEZE_TAG`**. Forgetting the bump would
overwrite the previous anchor file.

### §2.3 The model roster (R101 — Okhrati's seed-parity directive)

**All 11 full-loop models run IN PARALLEL AT EQUAL SEEDS, climbing ONE common ladder in LOCKSTEP.**
R101 SUPERSEDED R88's Opus-above-legs priority, the `leg_seed_tier: 30` floor, and R100's idle tail.
Verified still true in RUN 4: legs resolve 568 seeds / 7 tiers, and `leg_seed_tier` reaches no
consumer.

Confirmatory author **claude-opus-5** (R102). Legs in queue order: `deepseek-v4-pro`, `glm-5.2`,
`qwen3.6-27b`, `qwen3.5-9b`, `haiku-4.5`, `gpt-5.6-luna`, `nemotron-3-super`, `sonnet-5`,
`gemini-2.5-flash`, `kimi-k3`. **R106**: all 11 reasoning-OFF, output caps matched at 16,384.

**Measured per-model authoring reliability** — `qwen3.5-9b` ~17 % gate-pass (the deliberate
capability-gradient BOTTOM anchor; **its rejects are a REGISTERED FINDING, not a fault**),
`qwen3.6-27b` / `gemini-2.5-flash` ~83 %, `deepseek` ~100 %.

### §2.4 R115 — the winner-eligibility execution floor (newest amendment)

Selection was `max(val_fitness)` with **no execution-quality condition**, so a candidate whose
authored reward RAISED on much of its training (the R66 fallback standing in) could be frozen and
re-trained by the sealed leg — an identification hole.

**Eligible iff `train_safe_default_count / train_safe_call_count < 0.10`.** Effect-blind by
construction: it reads an EXECUTION counter, never a performance field, and a test asserts this by
inspecting the function's source. **Threshold-INSENSITIVE** — measured over 613 records: 594 clean,
16 trace (<1 %), 3 severe (53.66 / 50.02 / 39.40 %), i.e. a **96x empty gap** between worst-trace
0.41 % and mildest-severe 39.40 %. Registered **PRE-DATA** on the ADR-059 test. Raises
`NoEligibleWinnerError` → reason `no_eligible_winner`, distinct from `no_winner`.

### §2.5 THE RUN LEDGER — all four runs

| run | outcome |
|---|---|
| **RUN 1** | **INVALIDATED** by the cross-line reject collision (D1). 835 records preserved as the evidence base for the post-mortem and the dissertation's disclosure. Spend $11.65 |
| **RUN 2** | **HALTED at T+1.3 h**, zero records — stopped deliberately to register R115 pre-data. $1.29 |
| **RUN 3** | **HALTED at 3 h 26 min** having PROVED the D1 fixes (12/12 lines, 405 specs, **0 spurious abandonments**, 0 ERROR, 280 calls / 0 truncations). Halted only because its processes were a commit behind HEAD. $3.81 |
| **RUN 4** | **LIVE — the run of record.** Launched 2026-07-28 21:01 UTC |

RUNs 1-3 total **$16.75**. The **canary shield** means the confirmatory `c1` line spent **$0.00**
across every relaunch; the recurring relaunch cost is the h3 single-shot (~$2.5 Opus), which
re-authors from scratch each launch.

### §2.6 D1–D9 — machine defects found by PREVIOUS sessions (full detail in record §20)

* **D1 — cross-line reject collision (FATAL to RUN 1).** `driver.run_batch` resolved permanent
  rejects MIRROR-WIDE, and markers are keyed on the bare candidate id (`scalar-g1-c0`) that all
  twelve lines reuse. **439 of 498 abandonments (88 %) spurious**, **36/36 on the confirmatory
  core**, 402 traced to `qwen3.5-9b` alone. Fixed via `poll.permanently_rejected_specs` +
  `poll.spec_local_root`; replayed over the real archive it condemns exactly 59 and rescues 439.
* **D2 — reflection starvation.** A *consequence* of D1: only **10 of 241** archived prompts carried
  the reflection preamble, because `prev_block` is set only when a generation yields an accepted
  candidate. **The mechanism under study was OFF and nothing alarmed.** Hence `reflection_guard`.
* **D3 — leaked ssh children.** Both tar-over-ssh pipes put `proc.wait()` after the `try/finally`;
  13 leaked and transport failures climbed **5.2 % → 55.3 %**. Reaping them alone took it to 16.3 %.
* **D4 — watchdog / backup / supervisor hardcoded RUN 1's roots.** An automatic restarter is a second
  launcher and must take the same parameters as the thing that started the line.
* **D5 — C3 gate collision.** `TIER1_APPROVED` and `tier1_integrity.json` were single SHARED files,
  and passing the gate CONSUMES the approval (`unlink`), so one line could eat another's and proceed
  unreviewed. Now scoped by `line_tag()` and fails CLOSED.
* **D6 — no execution floor on winner selection** → R115.
* **D7 — fail-OPEN on a malformed batch result** (`res.get("ok", True)` → `False`).
* **D8 — `stop_reason` captured but only WARN-logged** → persisted structurally in `18dead8`.
* **D9 — the 300 s transport stall.** **NOW RESOLVED — see §6.**

**THE STRUCTURAL LESSON:** D1, D5 and the 2026-07-19 `pending_specs` case are ONE shape — *a resource
shared by twelve concurrent lines, keyed by an identifier unique only WITHIN one line.* All ~2,875
tests exercise a single line, so **no test can ever see it**; the only reliable detector is a LIVE
invariant. That is exactly what `scripts/campaign_guards.py collision` is. **Empirically
re-confirmed in RUN 4:** 1,874 shared-root artefacts across two runs, every one line-tagged, zero
exceptions.

**The second lesson, for CH4:** every one of D1–D9 was found by **measuring the running system** —
counting abandonments per line, sampling the process table, replaying the archive, running the real
loaders. **None was found by reading code alone.**

### §2.7 P1–P10 — previous sessions' PROCESS errors (record §20.2)

Recorded because a new session inherits the habits, not just the code: measured the wrong ssh client ·
proposed a fix that A/B testing then refuted · reported a live process as GONE from a `UInt32`/`Int32`
lookup · **claimed the suite green while `PYTEST_RC=1`** (read a wrapper's exit code) · produced a
false RED by editing source during a certification run · introduced a crash path with R115 · misread
the factor loader (reported 41 extrapolated sessions; the real number is 21) · **overstated an open
risk as unmet when it had been fixed since 2026-07-05** · put backtick content in a bash heredoc
twice · wrote a process filter that matched and killed its own shell and then misreported the result.

### §2.8 Settled decisions — do NOT re-propose

2000-start data · options · more candidates (multiplicity) · QD / URDP / GEPA / AlphaEvolve · repo
restructure / pydantic / Snowflake / Ray · GPT-5.5 as the second LLM (cost) · Fable-5 (identification
threat). **Prompt caching is PHYSICALLY INERT** on Opus (898-token shared prefix < the 4,096 floor) —
disclose it, do not implement it. **The `t` pool is excluded** (AMD vs Intel changes float reduction
order and would break CRN bit-exactness). **A GPU is not needed** — for this tiny-MLP workload the CPU
lane beats an A100 and is actually schedulable.

### §2.9 Verified-sound claims — do not re-litigate, though RUN 4 re-derived them anyway

* **CRN holds** — `resolve_agent_kwargs` puts the seed INTO the SB3 kwargs; burning 1,000 draws
  across numpy-legacy / numpy-Generator / `random` / torch leaves the kwargs byte-identical.
* **The arms differ exactly as H2 claims** — re-derived by calling `schema.build_block` directly.
* **The base prompts are tail-NEUTRAL** — the construct-validity hinge, pinned by a test.
* **B1 matched budget is real** — `train_safe_call_count` = 400,000 on 330/330 scored records.
* **The mechanism pipeline reads the PROMPT**, not the empty `feedback_block` (M14 fix, 2026-07-05).
* **The licensed gold on ACFS sha256-matches the frozen manifest** — re-verified live at launch.

---

## §3. ⚠⚠ THE SINGLE MOST IMPORTANT RULE FOR A LIVE RUN

**RUN 4's executing code is `b9e6df5` on BOTH sides** — the laptop drivers started from it, and the
cluster tree was verified byte-identical to it (`DIFFER=0 MISSING=0` over 2,649 files) before launch.

**DO NOT EDIT ANYTHING UNDER `src/`, `scripts/`, `config/`, `prompts/` WHILE THE RUN IS LIVE.**
RUN 3 was halted for exactly that ambiguity — processes not matching the repository that describes
them.

**The test is:**

```
git diff --name-only b9e6df5 HEAD -- src scripts config prompts     # MUST be empty
```

**Not** `git rev-parse HEAD`. Documentation commits on top are expected, correct, and required —
only source drift matters. Run this test before and after any commit.

Three real fixes are **deliberately deferred** for this reason. They are fully written out with code,
tests and apply order in **`docs/DEFERRED_FIXES_RUN4.md`** — apply them at the next natural restart,
not now.

---

## §4. READ THESE, IN THIS ORDER

1. **`docs/CAMPAIGN_EXECUTION_RECORD.md`** — **§22** (what re-executing the inherited gate found),
   **§23** (D9–D13, the deploy method, the instrument corrections), **§24** (the first science).
   **§20** is the cross-run post-mortem of RUNs 1–3. **§18** is the open-defect register.
2. `CHANGELOG.md` → **`[2026-07-29]`**, then `[2026-07-28e]`, `[2026-07-28d]`, `[2026-07-28c]`.
3. `docs/HANDOFF.md` §1 (state), §2 (standing orders), §3 (authority map — one owner per truth).
4. `memory/session-current-focus.md` — the ▶ NOW cursor.
5. `CLAUDE.md` — ★ PRIORITIES, the four-authority rule, and the five verification duties.
6. `docs/DEFERRED_FIXES_RUN4.md` · `docs/REMOTE_CONTROL.md` · `docs/RUN4_STATUS.md`.

---

## §5. LIVE STATE (2026-07-29 08:00 UTC, T+11 h — verify it yourself, don't trust it)

| item | value |
|---|---|
| launched | **2026-07-28 21:01 UTC** (supervisors up 21:08:58). ⚠ **logs are LOCAL = BST = UTC+1** |
| lines | **12/12** (core, h3, 10 legs) — **all 5 arms each**, verified by `arm_coverage.py` |
| records | **99+** and climbing |
| canary | ★ **CLEARED 07:30:32 UTC** (`completed: 90`, `ok: True`, analysis-smoke passed) — **core Opus authoring is RELEASED and the confirmatory arm has begun** |
| core Opus | 20 calls, `claude-opus-5`, provider correctly `anthropic`, all `end_turn`, **$1.6736** |
| cores computing | **408** (366 jobs, 81 running), **2,280 cores queued** |
| spend | **$5.6301** of ~$24 projected |
| transport timeouts | **0** |
| freeze | `3ca6f01ab7724d47…` **MATCHES**, tag `prereg-v2.1` |
| running sha | **`b9e6df5`** · drift **0 files** |
| budget | Anthropic **$24.64**, OpenRouter **$17.97** + key cap raised to **$100** |
| stop | **2026-08-27**, 28 days |

**★ PER-STAGE ETAs at the measured 408 cores** (`stage_eta.py 408 830`, from the registered
`plan_lanes` model — Tamer's standing reporting requirement):

| rung | 30 | 100 | 189 | 279 | 340 | 403 | 568 |
|---|---|---|---|---|---|---|---|
| ETA @408 cores | 08-01 | 08-05 | 08-11 | 08-16 | 08-20 | **08-24** | **09-03 ✗ misses** |
| ETA @830 cores | 08-01 | 08-01 | 08-04 | 08-07 | 08-09 | 08-10 | 08-15 ✓ |

**Cores are the binding lever** — at 408 the ladder banks rung 403 and 568 misses the stop by a week.

**⚠ D14 (§25 of the record) — the newest defect, and the one a fresh session must understand.**
leg7 lost two arms to D13 and ran **8 h 44 m on 3 of 5 arms while all six guards said green**.
**Total failure is LOUD and self-healing; PARTIAL failure is SILENT.** Recovered 07:55:23 UTC by
restarting the line only. **Run `arm_coverage.py` alongside the repo guards — they do not detect
this.** And note: the archive directory listing LIES (a dead arm still has a populated
`search_.../<arm>/` dir, because the authoring succeeded and was billed); only `batches/` shows work
actually shipped.

**Expected rhythm — so you can tell "running" from "correct":** each line authors generation 0
(25 calls/leg, 30 for h3ss), then **waits ~8 h** for training results before generation 1 can reflect.
**Flat spend for hours is CORRECT**, not a stall. Verify liveness by INFO growth in the driver logs
and by cluster job counts, never by spend.

---

## §6. WHAT THE PREVIOUS SESSION FOUND (so you don't rediscover or contradict it)

### Four defects

* **D10** — 1,361 spend rows across RUNs 1–3 all stamped `provider: anthropic`, including the eight
  OpenRouter legs. Both authors constructed `LLMClient` without `provider`. Routing was never wrong;
  **cost attribution was**. FIXED, verified live (rows now correctly split).
* **D11** — the killswitch counts EVERY `rc != 0` as a task death, and an authoring reject exits
  `rc=1` in ~5 s ⇒ 8 across 4 hosts in 300 s ⇒ FALSE `admin_kill` ⇒ **all twelve lines blocked until a
  human clears the incident file**. RUN 1's worst burst was 7 deaths / 6 hosts — ONE under threshold —
  and it stayed under only because the collision suppressed 39 % of candidates. **Fixing D1 armed
  this.** FIXED (`_APPLICATION_EXIT_RC`), verified against RUN 1's real rows.
* **D12** — a line whose every arm crashed reports `LINE COMPLETE` (gate stop returns 0). **DEFERRED.**
* **D13** — `response.choices[0]` unguarded ⇒ `TypeError` the retry layer won't retry. **DEFERRED.**

### ★ D9 RESOLVED — the campaign's one unexplained defect

RUN 4: **0 timeouts / 18 transport failures over 209 min at 12 lines.** RUN 3: **647 / 1,018 over
206 min at 12 lines.** RUN 4 did **2.2× more poll work** (13,113 vs 6,094 cycles) ⇒ **1.4 vs 167.0
failures per 1,000 polls.** Only transport diff: **`stdin=subprocess.DEVNULL`**.
**§18.3's "hygiene, explicitly NOT the cure" is WITHDRAWN.** ⚠ Two limits travel with it: the
mechanism (inherited std handles on concurrent Windows children) is the **leading** explanation, not
proven; and it is a **natural experiment**, so a quieter cluster night cannot be excluded.

### ★ The first science (§24) — and Tamer's challenge

| | test Sharpe, sealed 2020–2026 |
|---|---|
| **passive market proxy** | ⚠ **CORRECTED (record §36): +1.1656 Sharpe / +274.1 %** over the agents' ACTUAL 1,571-session window (2020-03-30 →). The **+0.773 / +166.0 %** figure used 1,631 sessions from 2020-01-02 and wrongly included the COVID crash the agents never traded (the 60-session R18 purge). Like-for-like EW-30 same assets: **+1.2825 / +183.3 %**. **No reward beats passive, even gross.** |
| 10 of 11 H1 baselines | **−0.171 … −0.325** |
| **`return_minus_turnover`** | **+1.161, 100 % of seeds positive** |

**The agents over-trade and bleed to transaction costs.** Pricing *risk* is not enough
(`differential_sharpe`, `mean_variance_utility`, `return_minus_cvar` are all negative) — pricing
*trading* is what wins. **RUN 4 reproduces RUN 1 to four decimal places** on the same seeds, so
determinism holds and this is the design, not the run.

**H2 is unaffected** (a level effect common to all arms), but the write-up must state the absolute
result plainly. **§24.6 flags PRE-DATA** that turnover may be the principal axis an LLM-authored
reward can exploit — testable from `test_turnover`, already captured on every record.

> **The meta-lesson:** the previous session said "the science checks out" having verified only
> INVARIANTS. Tamer challenged it and was right. **Invariants holding ≠ results being sound.**

---

## §7. HOW TAMER COMMUNICATES REMOTELY — KEEP THIS ALIVE

He is often away from the laptop. Two GitHub-based channels exist and **you must keep both running**:

1. **`docs/RUN4_STATUS.md`** — auto-regenerated and pushed **every 5 minutes** by a persistent
   monitor running `scratchpad/publish_status.sh`. Phone-readable: elapsed, lines up, cluster jobs,
   **cores computing**, records, spend, timeouts, guard verdict. **Pure ASCII** — keep it that way,
   non-ASCII mojibakes on his phone.
2. **`docs/REMOTE_CONTROL.md`** — he edits it on GitHub from his phone; the session polls the branch
   every 5 min, reads the instruction, acts, and writes back into the LOG table at the bottom.

**If the session restarts, RE-ARM BOTH** (the monitors die with the session; the campaign does not).
Also push to **both** branches: `backup-2026-07-28` **and** `myriad-cluster-and-tier-system`.

⚠ **The laptop must stay home, plugged in, awake and online** — the drivers and every LLM call run on
it; Myriad only trains. Sleep is disabled on AC; Windows Update is paused to **2026-09-10**.

---

## §8. THE MONITORING STACK — what is armed and what each catches

**In the repo (durable):** `scripts/campaign_guards.py <root> all` — six guards, **exit 2 = stop the
run**. `collision` (every ledgered abandonment must trace to its OWN sub-root — the RUN 1 killer) ·
`reflection` (≥80 % of gen>0 candidates shown a reflection block) · `truncation` (0 truncations AND
every spend row carries `stop_reason`; a missing key = a pre-`18dead8` driver) · `transport` (both log
formats, timeout depth, the D9 diagnostic) · `rejects` (per-model rate vs that model's OWN baseline —
the FINDING/DEFECT discriminator) · `status`.

**Every guard was FALSIFIED before being trusted** — fires on the RUN 1 archive, silent on RUN 3.

> **⚠ THE SIX GUARDS HAVE A HOLE, PROVEN LIVE 2026-07-29 (D14, record §25).** Not one of them asks
> whether a line still HOLDS ITS ARMS. All six returned green for **8 h 44 m** while leg7 ran with 3
> of its 5 arms — missing `scalar`, the H2 contrast partner. **Always run `python docs/ops/arm_coverage.py <root>` beside
> them.** Until D14's fix lands, `campaign_guards.py all` returning RC=0 does NOT mean the run is
> whole.

**Committed (durable): `docs/ops/arm_coverage.py`** (⭐ per-`(line, arm)` batch-submission
coverage — the D14 detector; reads the `batches/` REGISTRY, never the archive directory listing,
which lies; effect-blind; exit 2 on a missing arm; falsified exit 2 → exit 0 across leg7's recovery).
It sits under `docs/` on purpose: `scripts/` is inside the drift pathspec and the run is live.

**In the scratchpad (re-create if lost):**
`close_watch.sh` (change-only watcher, keyed on error **KINDS** not counts), `publish_status.sh` +
`publish_loop.sh` (the 5-minute phone status push), `remote_watch.sh` (fires only when Tamer's
instruction block actually changes), `status_report.sh` + `remote_status.sh` (the dashboard),
`stage_eta.py` (per-rung ETAs from the registered model — takes `<measured_cores> [modelled_cores]`),
`science_sanity.py` (**stage-aware** — test-leg records score on `test_sharpe`, search on
`val_fitness`), `Send-Remote.ps1` (base64 ssh transport — the naive pipe corrupts payloads),
`openrouter_key_info.py`.

⚠ **`qdel` is blocked by the harness safety classifier** (found 2026-07-29). If a cluster job genuinely
must be deleted, it is Tamer's call — surface it, and never route around the block. In the D14 case
this turned out to be fortunate: the deletion would have been the WRONG action (§25.4).

---

## §8b. OPERATING THE LIVE RUN — stopping, restarting, and the exact commands

### The STOP lever, and what it really does

```
outputs\campaign_cluster_run4\STOP_CAMPAIGN        <- create this file
```

**It stops RESTARTS, not a running driver.** It is honoured by the supervisors, the watchdog and the
backup — **not** by a driver already mid-batch. A FULL halt is an ORDERED sequence, and the order
matters because the watchdog revives dead lines every 300 s:

1. write `STOP_CAMPAIGN` into the run root;
2. **kill the watchdogs FIRST** (else they resurrect everything you kill next), verify 0 remain;
3. kill the 12 supervisors → then the drivers → then backup, sentinels, advisors;
4. on the cluster, delete campaign jobs **by explicit job ID only** — **NEVER `qdel -u ucestes`**,
   which would destroy the surviving `l16xx` p6-ladder cells that feed figure F11.

Every process query MUST exclude `$PID`, or it matches and kills your own shell and then misreports
what is left (P10).

### Relaunching (only if a relaunch is genuinely required)

```
powershell -ExecutionPolicy Bypass -File scripts\mode_d_launch.ps1 `
  -OutDir outputs\campaign_cluster_runN -RemoteRoot ~/Scratch/llmrpN
```

**BOTH root flags are mandatory** — every entrypoint defaults to RUN 1's paths, and omitting one
silently rejoins a halted run whose archive-truth resume would adopt its records. Then, with the SAME
roots: `mode_d_watchdog.ps1 -IntervalSecs 300`, `campaign_backup.ps1 -SrcRoot`,
`sentinel.py <root> --watch --interval 300`, `allocation_advisor.py --host myriad --watch 900
--archive-root <root>`.

**ORDER: launcher FIRST, then verify 12 supervisors are up, THEN the watchdog.** Starting the
watchdog first spawns twelve supervisors that the launcher then duplicates.

### The daily commands you will actually use

```
python scripts/campaign_guards.py outputs/campaign_cluster_run4 all    # exit 2 = stop the run
git diff --name-only b9e6df5 HEAD -- src scripts config prompts        # MUST stay empty
python scripts/freeze.py --check                                       # RC=0 + hash MATCHES
ssh myriad "qstat -u ucestes | tail -n +3 | wc -l"                     # cluster jobs
```

### The C3 review gate — an EXPECTED event, not a fault

A weak leg may stop at the C3 gate awaiting human approval; the gate reads only **execution health**
(effect-blind) and **fails CLOSED**. To clear it: read `tier1_integrity_<line_tag>.md`, then create
`<read_root>/TIER1_APPROVED_<line_tag>`. The approval is **staleness-checked** (one predating the
report it claims to approve is IGNORED) and **consumed on passage**, so each passage needs its own.

### If the laptop reboots or the session dies

**The campaign survives a session death** — it is independent processes. It does **not** survive a
laptop reboot: re-launch the supervisors on the SAME roots with `--resume` (archive-truth resume
re-authors only what is missing, so nothing is double-billed). The laptop must stay **home, plugged
in, awake and online**: sleep is disabled on AC and Windows Update is paused to **2026-09-10**, 14
days past the Aug-27 stop.

---

## §9. TRAPS THAT COST THE PREVIOUS SESSION TIME — do not repeat

1. **`qstat` truncates job names to 10 chars** (`c1_baselin`) — `grep 'c1_baselines'` returns zero.
2. **`qstat` columns are state-dependent**: running rows `NF=10` (`$9`=slots), queued rows `NF=9`
   (`$8`=slots, `$9`=task-id). Summing `$9` reads TASK-IDs as slots.
3. **`qacct -j <name>` is NOT run-scoped** — it aggregates every job that ever had that name, and
   RUNs 1/3/4 share `c1_` tags. **Disambiguate by end time.**
4. **Driver logs are LOCAL time (BST = UTC+1).** The previous session recorded the launch an hour
   wrong. Never do arithmetic on a log timestamp without converting.
5. **Driver logs carry TWO logging formats.** Counting one undercounts badly (RUN 3 was recorded as
   "0 ERROR / 41 WARNING"; the truth was 1 / 798).
6. **Test-leg records carry `val_fitness = nan` legitimately** — they score on `test_sharpe`. The
   repo's `sentinel._primary_metric` is stage-aware; ad-hoc checks must be too.
7. **The search lane runs 8 threads, the test lane 1.** Do not compare a search-lane wall-clock to the
   1-thread 8.09 h planning figure — the previous session did and reported a 2× speedup that wasn't.
8. **A full-tree cluster deploy is impractical on a contended login node** (~40 files/min). Use the
   delta method in **§23.12 of the record**, and always prove it with the sha256 manifest (`DIFFER=0 MISSING=0`).
9. **Alarms keyed on COUNTS cry wolf**; key them on **kinds**.
10. **Any process query must exclude `$PID`.**

---

## §10. OPEN THREADS — pick these up

1. ✅ **DONE 07:30:32 UTC — the canary cleared 90/90 and core Opus authoring released.** The
   confirmatory H2 arm is now running (20 calls, `claude-opus-5`, $1.6736). **Next:** watch the first
   `c1` search records land and score, and confirm the H2 arms stay budget-matched.
2. **Capacity is THE lever**: cores 20 → 208 → **408**. At 408 the ladder banks **rung 403 (08-24)**
   and **568 misses the Aug-27 stop (09-03)**; 830 cores would land 568 on 08-15. Report cores +
   per-rung ETAs every update (`stage_eta.py 408 830`). If it stalls, say so.
3. **Apply `docs/DEFERRED_FIXES_RUN4.md`** at the next natural restart — not before. It is now
   **four** items: D13, D12, preflight headroom, and **D14** (§4 — the arm-coverage guard plus the
   durable repair; D12 and D14 must be decided together, since both hinge on the exit code).
   ⚠ **D13 is no longer hypothetical — it fired twice in production and cost leg7 two arms.**
4. **Weak legs may stop at the C3 review gate** — that is DESIGNED. Clear with
   `TIER1_APPROVED_<line_tag>` after reading the integrity report (staleness-checked, consumed on use).
5. **§24.6's turnover question** — testable from `test_turnover`, already captured.
5b. **⚠ §26.3's DIFFERENTIAL ARM ATTRITION — registered PRE-DATA, and the one to keep watching.** An
   author-side AST reject is ledgered `permanent` and the candidate is **never replaced**, so the arm
   permanently searches fewer than its registered 30. Asymmetric attrition handicaps an arm in H2's
   `max(val_fitness)`, and **3 of the first 5 rejects are `placebo`, a CONTROL** — biasing the
   contrast TOWARD a false positive for our own hypothesis. At n=5 this is chance-consistent, so
   **no claim is made** — but run `python docs/ops/arm_coverage.py <root>` every update and watch the
   `[attrition]` line as generations accumulate. The obligation (per-arm accepted-candidate counts +
   an equal-*k* sensitivity analysis) is registered at record **§9 item 4**. Do NOT "fix" it by
   re-authoring rejects — that would alter the registered candidate budget mid-run.
6. **R107's 2.72× thread speedup looks optimistic** — observed ~2.03× on n=2. Re-measure when more
   search-lane records land; it feeds the makespan's chain term.
7. Register items **L** (factor ladder 21/1631, report-only), **M** (tag annotated not signed),
   **N** (2 commits authored `abailey81` with Tamer's email — cosmetic, HIS call).

---

## §11. YOUR FIRST ACTIONS

1. Read §3's list. Do not skim §22–§24.
2. Say **"Resuming from: … — next: …"** and continue. Do not ask what to do.
3. **Verify the live state yourself** — `campaign_guards.py`, the drift test, `freeze --check`,
   cluster `qstat`. Trust nothing in §4 without re-running it.
4. **Re-arm the monitors** if they are not running (status publisher, remote-control poller, guards).
5. Report to Tamer with **timeline · cores · jobs · per-stage ETAs** — his standing format.
6. Keep documenting as it happens: CHANGELOG + record + HANDOFF §1 + cursor. **Push to BOTH branches.**

**The campaign does not depend on you.** Supervisors relaunch, the watchdog revives dead lines every
300 s, the sentinel watches health. If your session dies, the run continues — a fresh session resumes
from this file. What depends on you is that it stays *honest*: measured, cross-checked, and reported
without over-claiming.
