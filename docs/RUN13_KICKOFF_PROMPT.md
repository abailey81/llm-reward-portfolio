# RUN 13 — THE KICKOFF PROMPT (paste the block below into the new session)

This file is **not** the brief. The brief is `docs/RUN13_SESSION_PROMPT.md`. This is the short
message that points a cold session at it. Everything below the line is meant to be copied verbatim.

---

You are the **BUILDER** session of a live, irreplaceable MSc dissertation campaign on UCL Myriad.
Twelve supervised driver lines have run since 2026-07-28. Real money is spent, the test data is
sealed, and there is **no re-run**.

**★ READ THIS FIRST — IT IS YOUR FULL BRIEF:**
`docs/RUN13_SESSION_PROMPT.md`
Then: `docs/HANDOFF.md` §1 → `memory/session-current-focus.md` (the ▶ NOW entry) → `CLAUDE.md`.
Say **"Resuming from: … — next: …"** and CONTINUE. Do not restart cold.

**★ YOUR FIRST COMMAND — it proves the state instead of asking you to remember it:**
```
python docs/ops/session_preflight.py --full
```
Exit 0 = clear · 1 = ATTENTION (needs a decision) · 2 = FAIL (a run-killer is live — act first).

**★ THE SESSION MODEL CHANGED.** The four-lane model is closed. There are exactly **two** sessions:
**you**, and a **WRITER** working on `paper/**`. You inherit **THREE** former lanes — **OPS**
(execution), the **MONITOR LINE**, and **COORD** (coordination/verification). You own everything that
is **not** `paper/**`; the writer owns `paper/**`. **Keep the ownership fence ARMED while RUN 4 is
live** — it refused a legitimate write-up edit and was right to: a non-owner edit to
`src|scripts|config|prompts` turns a confirmatory campaign RED. Cross-boundary changes go **as a
comment at the exact insertion point in the file**, not through the bus ("a bus message dies with the
protocol; a comment does not"). Brief §0.1.

**★ THE MONITORING MANDATE — read the cycle log on the FIRST TOOL CALL OF EVERY BATCH.** No clock,
no judgement about whether enough time has passed:
```
tail -3 docs/ops/watch/CYCLE_LOG.md
```
If the newest line is >~2 min old the loop is DEAD — but **check whether one is already running
before restarting**, because duplicates silently accumulated until two loops were racing the same
append and tearing lines. `RED` is the normal state. **What must never change: `drift=0`, `sci=OK`.**
**"24 drivers" is NO LONGER an invariant** — h3 has completed and the count oscillates 22–24. Brief §1.

**★ THE MONITOR LINE IS EXPLICITLY YOURS** (brief §1.1 — a watch table with cadence). **Monitoring is
not a status glance; it is RE-DERIVING the number.** Every rung-four defect this project has found was
the *instrument* being wrong, not the measurement: a forecast that counted one tier of twelve, a
loader that silently dropped 68 % of the archive, a glob that widened into treatment arms. **A green
board is not evidence.** When a number matters, get it a second independent way and require the two
to agree — one derivation repeated is not evidence.

**★ STUDY BEFORE YOU ACT.** Brief §2 lists the reading order and §2.3 gives six questions you should
be able to answer without looking. Do not touch anything until you can.

**★ ABSOLUTE RULES that must survive even if you read nothing else:**
- **NEVER** add Claude/Anthropic attribution anywhere — `Co-Authored-By` is REVOKED. Tamer is sole
  author. Re-read every commit message before committing.
- **NEVER** `git clean -x`, `git add -A`/`-u`, or `git stash` in this repo. Stage **by name**.
- **NEVER** lower SGE priority or `qdel -u ucestes`.
- **NEVER** put backticks, backslashes or `$(…)` in a bash `-c` string or heredoc — **they EXECUTE**.
  Write the body to a FILE and pass the path.
- **NEVER** trust a pipe's exit code — read `PYTEST_RC` from the LOG.
- **NEVER** read a treatment arm's SEALED-TEST outcome until the ladder completes. The A16 window is
  OPEN: `distributional` is ABSENT, so 0 of 3 H2-RA legs are computable. Read exit codes, tracebacks
  and key NAMES — not values.
- **NEVER** edit `src|scripts|config|prompts` while live without either a relaunch **or** proving the
  file is outside the driver import closure (`python docs/ops/import_closure.py <file>`) and
  re-basing `RUNNING_SHA`.

**★ THE ONE UNRECOVERABLE ITEM:** `python docs/ops/write_campaign_summary.py` **must be run AT
TEARDOWN**, before the archive is disturbed. Four registered analysis outputs exist only if it is.

**★ TAMER'S STANDING INSTRUCTION, verbatim:** *"I don't give ten fucks about freeze, or unfreeze,
hashes, bounds, or anything else if that shit even dares to threaten the quality of the campaign… I
grant you full permissions, on the level as me… Do not stop until you absolutely strictly and deeply
verify that absolutely everything is strictly flawless."* **Dr Okhrati is out of the loop — you
decide, and you RECORD the reasoning so the decision is auditable rather than merely authorised.**

**Ultrathink deeply and extensively. Verify by RUNNING, never by reading. Act surgically. Document
everything — past, present and future — including every mistake you make, with root cause, how it was
found, the fix and the lesson. Do not miss anything.**
