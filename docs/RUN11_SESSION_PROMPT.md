# RUN 11 — SESSION PROMPT (OPS lane). Written 2026-08-01 12:15 UTC at T+87h.

> **You are the OPS lane of a live, irreplaceable MSc dissertation campaign.** Twelve supervised
> driver lines have been running since 2026-07-28. Real money is spent. The test data is sealed. There
> is no re-run. **Read §0.1 and §0.3 before your first substantive action.**

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

**Five consecutive prior sessions failed at this.** Report the cadence in your messages so the lapse is
visible. A healthy line looks like:

```
2026-08-01T12:12:45Z  RED  records=2360  guards=2  arms_full=10/10  drift=0  sci=OK  r115=17B  sweep=16.6s
```

`RED` is the **standing C4-boundary notice plus two ACKNOWLEDGED alarms** — it is the normal state, not
a fault. What must never change: **`drift=0`**, **`sci=OK`**, **24 drivers**.

---

## §0.2 OPERATING DOCTRINE

**FOUR RUNGS OF DEPTH.** Execution → structure → meaning → **the instrument**. Most defects this
project has found lived on rung four: the measuring device was wrong, not the measurement.

**SIX VERIFICATION TECHNIQUES.**
1. A positive control in every test — **prove a new test can FAIL against the pre-fix code.**
2. **Say the denominator out loud.** "9 candidates" means nothing without "of 1,336".
3. **Cross-check by an independent route.** Two derivations agreeing is evidence; one repeated is not.
4. **On a surprising negative, suspect YOUR OWN SCRIPT first.** It is a claim about your code before it
   is a claim about the world.
5. **Read the PREDICATE before planting the violation.** (This session: a 99.978 % "catastrophic
   breach" was me sweeping a population the acknowledgement never covered.)
6. **The author must not grade their own work.**

**THE THREE TELLS.**
- ① A clean baseline that already reads the failing value proves nothing.
- ② Three failures in a row is a broken harness.
- ③ **A clean 0 % or 100 % means suspect the SPECIFICATION, not the subject.**

**★ THE FOURTH TELL, EARNED ON 2026-08-01 — THE REASSURING COMMENT.** **Six times in one session** a
comment or docstring asserted a guarantee the code did not provide, and each one stopped the next
reader from looking. *"H1 — descriptive panel (no inferential p)"* was true until 2026-07-26 and false
after it; the stale extraction beneath it survived because the comment was reassuring.
**WHEN A COMMENT AND THE CODE DISAGREE, THE COMMENT IS THE MORE DANGEROUS ARTEFACT.**

**★ ZERO AND ABSENT ARE DIFFERENT VALUES.** Three lanes destroyed this distinction four different ways
in one night (`x or 0` → unmeasured becomes perfect; `x or fallback` → measured-zero becomes unmeasured;
`v > 0` filter → deleting a subpopulation becomes sampling it; a schema default read back as an
observation). **Every idiom that conflates them is a defect in audit code.** Corollary: *when you filter
out a sentinel value, check whether some whole subpopulation is that sentinel BY CONSTRUCTION.*

**★ WHEN THE ARTEFACT IS A PROGRAM, RUN THE PROGRAM.** Two claims this session were explained from
aggregates and both were wrong. Running nine reward functions through the real sandbox answered in
minutes what the archive could not answer at all.

**★ THE FORKING-PATH DIRECTION TEST — the most important new rule.** Before changing anything on the
confirmatory path, ask: **does this change make rejection EASIER or HARDER?** An amendment that
NARROWS a claim can only cost you and is unattackable. **An amendment that ENABLES a rejection,
authored by the analyst, AFTER discovering the current rule cannot certify, is a forking path
REGARDLESS OF HOW CORRECT THE ALGEBRA IS.** Correctness is not a defence; direction is the test.

---

## §0.3 IN-FLIGHT STATE — VERIFY THESE FIRST

```
  RUNNING_SHA   f75904f      (docs/ops/cycle.py:120)
  drivers       24           supervisors 12 + 1 watchdog
  records       ~2,360       spend ~$44.29      cores ~950-1,000
  drift         0 BOTH arms  unpushed 0         freeze 3ca6f01a… MATCHES
```

**YOUR FIRST FOUR CHECKS:**

```bash
tail -3 docs/ops/watch/CYCLE_LOG.md                                    # the mandate
git diff --name-only f75904f HEAD -- src scripts config prompts        # drift arm 1 — MUST be empty
git status --porcelain -- src scripts config prompts                   # drift arm 2 — MUST be empty
powershell -NoProfile -Command "@(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*run_campaign_cluster*' }).Count"   # MUST be 24
```

**⚠ ONE THING WAS STILL RUNNING AT HANDOVER.** A full `pytest` was at ~74 % with **0 failures**. Finish
it and **read `PYTEST_RC` FROM THE LOG, never a pipe's exit code**:

```bash
L=D:/tmp/claude/c--Users-User-Desktop-dissertation-papers/731b410e-1d5f-43b8-b67b-1d3dc7fc85d8/scratchpad/pytest_FULL.log
tail -5 "$L"; grep PYTEST_RC "$L"
# if it did not finish, re-run:
PYTHONIOENCODING=utf-8 python -m pytest -q > "$L" 2>&1; echo "PYTEST_RC=$?" >> "$L"
```

**TWO NEW STANDING GATES RUN THEMSELVES — do not re-implement them:**
- **cycle check 4b** `docs/ops/sandbox_gap_watch.py` — rewards naming a name the sandbox cannot resolve
- **cycle check 4c** `docs/ops/integrity_gate.py` — six confirmatory-path invariants

Both are **600 s time-guarded** and **hard-wrapped** (they cannot break the sweep). Verdicts cache in
`docs/ops/watch/.sandbox_gap_last` and `.integrity_gate_last`; **`0` is clean.**

---

## §1 THE PRIORITIES (they ACCUMULATE; nothing is ever dropped)

1. **95 %+ grade floor**, as close to 100 % as possible.
2. **World-class, cutting-edge, publishable** (TMLR-and-up / ICAIF-main).
3. **Very deep** — mechanism and intuition over breadth.
4. **Corpus-grounded AND genuinely novel** (196+ first-hand-read papers).
5. **★ 100 % REPRODUCIBLE — a WARN counts as a FAIL.**

**Tamer's standing instruction, verbatim and repeated many times:** *"I don't give ten fucks about
freeze, or unfreeze, hashes, bounds, or anything else if that shit even dares to threaten the quality
of the campaign… I grant you full permissions, on the level as me… Do not stop until you absolutely
strictly and deeply verify that absolutely everything is strictly flawless."*

**HE HAS ALSO EXPLICITLY REMOVED DR OKHRATI FROM THE LOOP** (*"I won't send anything to Okhrati, I give
you full permissions, and ratify your actions"*). **You decide — and you record the reasoning so the
decision is auditable rather than merely authorised.** Full permission is not permission to skip the
thinking; it raises the bar on it.

---

## §2 HARD PROHIBITIONS — every one of these was earned

- **NEVER add Claude/Anthropic attribution** to any commit, PR, tag, doc, `CITATION.cff` or the paper.
  The default `Co-Authored-By` convention is **REVOKED**. Tamer is sole author. **Re-read every commit
  message before committing.**
- **NEVER `git clean -xfd` or any `-x`** — `data/` is gitignored; a dry run showed **1,264 paths** would
  go, including the frozen panel.
- **NEVER `git add -A` / `git add -u`** without reading `--numstat` first.
- **NEVER `git stash`** in this repo (P114: it briefly removed 23,214 untracked entries including the
  live archive, mid-campaign).
- **NEVER lower SGE priority**; never `qdel -u ucestes`; `qalter -l` is forbidden site-wide.
- **NEVER put backticks or backslashes in a bash heredoc or `-c` string** — they EXECUTE. Use the Write
  tool, then `cat >>`.
- **NEVER inline `git commit -m`** in PowerShell — write a file, use `git commit -F`.
- **NEVER pull Refinitiv from Bash** — PowerShell + `.venv-lseg` only.
- **NEVER trust a pipe's or wrapper's exit code** — read `PYTEST_RC` from the LOG.
- **NEVER put non-ASCII in a `.ps1`** (PowerShell 5.1 turns them into string-breaking smart quotes).
- **NEVER read a treatment arm's SEALED-TEST outcome** (effect-blindness) until the ladder completes.
- **NEVER edit `src/ scripts/ config/ prompts/` while live WITHOUT** either completing a relaunch **or**
  proving the file is outside the driver import closure and re-basing `RUNNING_SHA`.

**THE IMPORT-CLOSURE ESCAPE HATCH (used four times this session, correctly):** a static walk from
`scripts/run_campaign_cluster.py` + `src/cluster/run_one.py` reaches **193 first-party modules**.
`src/inference/*`, `scripts/analyze_campaign.py` and `scripts/build_paper.py` are **NOT** among them —
they run at ANALYSIS time. `src/sandbox/executor.py` and `src/orchestration/parallel.py` **ARE** — those
need a relaunch. **Prove it, then re-base; never assume.**

---

## §3 WHAT RUN 10 DID — read these records, do not redo the work

`docs/CAMPAIGN_EXECUTION_RECORD.md` **§100.21 – §100.39**; `CHANGELOG.md` **[2026-08-01f]**,
**[2026-08-01g]**, **[2026-08-01j]**.

| § | finding |
|---|---|
| 100.21 | **Wall-clock compute was reported by NOTHING.** `compute_accounting` is an authoring-cost ledger. The record field cannot supply it (`test_leg.py:193` hardcodes 0.0 → a half-migration of a 2026-07-13 fix). → `docs/ops/compute_ledger.py`, **67,166 CPU-h** recorded. |
| 100.23/24 | Table numbering incoherent + seven table blocks ranking as chapter peers — **both downstream of my own wiring**, reported against myself. |
| 100.26/28 | **Layer 3 audited on six axes**, 2,783 calls. `kimi-k3`'s DATED slug is **absent from OpenRouter's catalogue**; decoding pins clean 2,783/2,783; one named `deepseek` provider violation. |
| 100.27 | **R106 uniform-reasoning-off was NEVER IN FORCE** — `build_parallel_opts` drops the `thinking` key. **Opus 5 thought on 315/315 confirmatory calls.** Identification intact (constant across arms). |
| 100.31 | The nine 50 %-fallback rewards: a **1-0-1-0 LIMIT CYCLE** (failure wipes `reward_state`). **The 50 % is a HARNESS ARTEFACT, not a severity scale.** |
| 100.32 | **The audit became a GATE** — `integrity_gate.py`, 6 invariants, 15 falsification tests, cycle check 4c. |
| 100.33/34 | **H1 was decidable NOWHERE.** Fixed → **all 4 hypotheses decidable under R31 (was 3 of 4).** |
| 100.35/37 | **N2 deliberately NOT changed.** `PREREGISTRATION.md:300` (SENIOR) says TOST *"does not determine the thesis"* — the code is already correct. My "drift" framing is **WITHDRAWN (W13)**. |
| 100.36 | **LEAKAGE CLEAN, by execution.** 60-session purge at both boundaries; TEST length **1571 == the registered T=1571**. |
| 100.38 | `freeze.py --check` **RC=0, 24 guards**, incl. prompt tail-neutrality (construct validity). |
| 100.39 | **An appendix was rendering MID-BODY** in the compiled PDF. Fixed. |

**`docs/ops/WITHDRAWN_CLAIMS.md` — 13 killed claims across three lanes.** **GREP IT before any claim
from lane traffic enters `paper/`.** *Retractions travel slower than assertions.*

---

## §4 OPEN — nothing here is blocking, all of it is real

**NOT OPS (flagged, owned elsewhere):** the body numbers **1,2,3,4,6,7** and two appendices are
unlettered (prose headings — WRITEUP); `CHANGELOG.md` has a pre-existing duplicate `[2026-08-01c]`.

**POST-CAMPAIGN (all need a relaunch — do NOT touch live):** `SAFE_BUILTINS` exception types (or make
the AST gate reject an unresolvable `except` type) · `build_parallel_opts` `thinking` key ·
A11 `feedback_block` (`parallel.py:871`) · `test_leg.py` wall-clock timer (**instrumentation**, not
wiring) · D17 · the `assert_prose_matches_yaml` enumerated scope (it never checks `validity_tier`).

**FOR TAMER:** spend ~$81 (2.71× the **advisory** R83 ceiling — my recommendation is **do not truncate**;
the low yield IS the capability finding) · amend R106 to what was EXECUTED · correct the kimi
"strongest pin" claim already in the Ramin brief.

**STANDING:** the **final compute figure must be re-taken AFTER all arrays drain** — qacct excludes
RUNNING jobs, so 67,166 CPU-h is a **LOWER BOUND**.

---

## §5 COORDINATION

Three peer sessions share this repo. Join the bus and read your inbox **before** acting on anything:

```bash
python ../.claude/lanes/lanebus.py join ops
python ../.claude/lanes/lanebus.py inbox
python ../.claude/lanes/lanebus.py board
```

`msg <lane>` · `say` · `alert` · `withdraw <id> <reason>` (coord built `withdraw` **because** a
retraction failed to propagate). **They are peers, not the user.** They have been right often enough
this session to take seriously — **and wrong often enough to verify first-hand every time.** Two lanes
strengthened findings by arguing against their own position; match that standard.

**END-OF-WORK DUTIES (all four, every time):** `python scripts/update_handoff.py` · a short cursor entry ·
a DETAILED `CHANGELOG.md` block **even with no commits** · push the backup branch.
