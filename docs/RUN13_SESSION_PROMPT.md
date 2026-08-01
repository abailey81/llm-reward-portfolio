# RUN 13 — SESSION PROMPT. **THE LANES ARE CONSOLIDATED. YOU ARE ALL OF THEM.**
Written 2026-08-01 22:30 UTC at T+97h, at Tamer's instruction to end multi-session working.

> **You are the BUILDER session on a live, irreplaceable MSc dissertation campaign.** Twelve supervised
> driver lines have run since 2026-07-28. Real money is spent. The test data is sealed. There is no
> re-run. **You inherit THREE former lanes: OPS (execution), the MONITOR line, and COORD
> (coordination/verification).**
>
> **There are exactly TWO sessions now: YOU, and a WRITER session working on `paper/**` in parallel.**
> The former four-lane model is closed. **You own everything that is not `paper/**`; the writer owns
> `paper/**`. Neither of you should edit the other's tree** — see §0.1, which is not bureaucracy: the
> ownership fence refused a legitimate write-up edit tonight and **was right to**, because a non-owner
> edit to `scripts/**` during a live confirmatory run turns the campaign RED.
>
> **Read §0 and §1 before your first substantive action. Then read §2 and actually do it.**

---

## §0 ★★★★★ WHAT CHANGED, AND WHAT IT COSTS YOU

Until now four sessions ran in parallel (ops · analysis · coord · writeup) and **corrected each other
constantly** — that cross-checking caught more real defects today than any single lane's own care.
Today's record alone: coord caught ops' blindness attestation in five minutes; analysis found the
loader defect ops then fixed; coord found that ops' fix *inverted* a second defect; ops found the
monitor was reporting an impossible rung.

**Two of those four are gone (analysis and coord), and the writer does not audit your work.** The
dedicated verification lane no longer exists. **You must reproduce it INSIDE your own session.**
Concretely:

1. **Adversarially check your own work before banking it.** After any finding, ask what would falsify
   it and go and try. The single highest-yield habit in this project's history.
2. **Post your numbers into the record BEFORE acting on them** (CHANGELOG / the execution record), so
   a wrong number is visible rather than load-bearing.
3. **When two derivations disagree, STOP.** Every serious defect this session began as a
   contradiction someone nearly explained away.
4. **Run the verifiers.** `python .claude/lanes/openitems.py --open` re-derives every row's status
   from the repo — it is the closest thing left to a second opinion. **Do not take a status on trust.**

### §0.1 ★★★★ WORKING ALONGSIDE THE WRITER — the ownership boundary is a CAMPAIGN guard, not etiquette

**You own everything except `paper/**`. The writer owns `paper/**`.** The fence is currently
**ARMED — `owner=ops`, `paths=src/**, scripts/**, config/**, prompts/**`. KEEP IT ARMED while RUN 4
is live.**

**Why this is not bureaucracy — it was tested tonight and it held.** The write-up lane needed a
one-line change in `scripts/build_paper.py`, tried to land it, and **the fence refused them.** They
could have run `lane fence --off`. They did not, and put the reasoning on the record:
> *"a mis-ordered Table of Contents is a presentational defect; a RED confirmatory campaign is not.
> The fence made the right call and I am not going to override a guard that is protecting a live run
> to fix a cosmetic ordering issue."*
**That is the standard. A non-owner edit to `src|scripts|config|prompts` during a live confirmatory
run turns the campaign RED — the cost is never worth a presentational fix.**

**HOW TO HAND A CROSS-BOUNDARY CHANGE OVER — the durable pattern, and it is the writer's insight:**
> **"A bus message dies with the protocol; a comment in the file does not."**

So when you need something changed in `paper/**`, or the writer needs something in your tree:
**write the complete instruction as a comment AT THE EXACT INSERTION POINT in the file that must
change** — both halves if it is a two-part change, the reason it is binding, and what happens if only
one half lands. Then mention it. The comment is what survives; the message is a courtesy.
*This is exactly how Appendix F reached me: the instruction was inside the appendix file itself, so
it was actionable months after any conversation would have been lost.*

**THE LIVE EXAMPLE YOU WILL MEET — the ToC order, and it is a TRAP:**
IFTE0008 binds **ToC → List of Figures → List of Tables**; the document currently ships
**LoF → LoT → ToC**. The fix is **TWO PARTS THAT MUST LAND TOGETHER**: the writer adds a raw
`\clearpage\tableofcontents\clearpage` inside `paper/FRONT_MATTER.md`, and you delete the injection at
`scripts/build_paper.py:~233`.
> ⚠ **EITHER HALF ALONE IS WORSE THAN NEITHER.** Yours alone ⇒ the document has **NO** ToC. Theirs
> alone ⇒ **TWO**. The writer already reverted their half tonight, so **the document currently has
> exactly ONE ToC and you must NOT delete the injection unilaterally.** Verified at handover: one
> `\tableofcontents` in the assembled markdown. **Coordinate explicitly, or leave it — it is
> presentational, and the full instruction is already written into `paper/FRONT_MATTER.md`.**

**ALREADY DONE, so do not redo it:** Appendix F is **WIRED** (`build_paper.APPENDICES`, appended last,
6 appendices A–F, build verified 0 missing chars) — it previously reached no PDF at all. And
`cost_decomposition.py`'s unblind glob is **CLOSED** (deny-by-default).

**The lane bus still exists** (`.claude/lanes/lanebus.py`) and `openitems.py` is still the verified
board — **use the board, do not queue work through the bus.** With two sessions, the durable
coordination is: **the ownership fence + notes at insertion points.**

---

## §1 ★★★★★ THE MONITORING MANDATE — NON-NEGOTIABLE, AND IT IS NOW WIDER

**READ THE CYCLE LOG ON THE FIRST TOOL CALL OF EVERY BATCH, EVERY TURN. No clock, no judgement about
whether "enough time has passed."**

```bash
cd /c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
tail -3 docs/ops/watch/CYCLE_LOG.md
```

**If the newest line is more than ~2 minutes old the loop is DEAD.** Restart:
`nohup bash docs/ops/cycle_loop.sh > /dev/null 2>&1 &`

> ⚠ **CHECK FIRST WHETHER ONE IS ALREADY RUNNING.** The mandate says "restart it" with no such check,
> and duplicates accumulated silently until there were TWO loops racing the same `>>` append —
> which produced a torn line in `ALERTS.txt` and duplicate CYCLE_LOG entries. Verify with the
> parentage filter in §3; a `$(...)` subshell inherits the parent's command line and inflates the
> count.

**`RED` is the standing C4-boundary notice plus acknowledged alarms — the normal state, not a fault.**
**What must never change: `drift=0`, `sci=OK`.**

> ⚠ **"24 drivers" IS NO LONGER AN INVARIANT — AND THE COUNT OSCILLATES.** h3 has COMPLETED (568/568,
> one reward hash), so its line legitimately drops out — **but the watchdog REVIVES a completed line's
> supervisor**, which I confirmed by observation: the count went 24 → **22** → 24 within the hour, and
> the revived h3 driver simply restarts, re-derives everything complete, and exits OK (h3 stayed at
> 568 records throughout). **So expect 22–24 oscillating, and expect the floor to fall further as more
> lines finish.** *Neither 22 nor 24 is by itself evidence of anything.* The correct check is:
> **every line that is NOT complete still has its supervisor, and a complete line's records are
> unchanged.** Verify the second half — a revived driver that started re-running finished work would
> be a real defect, and the h3 record count is how you tell.

**A transient `drift=N` around your own commits is EXPECTED and unavoidable** — `RUNNING_SHA` must name
a hash that does not exist until the commit lands, so code-commit and re-base cannot be atomic. The
signature is `0+Ndirty` → `drift=N` → `drift=0` over ~100 s. **Do not treat it as an incident.**

### §1.1 ★★★★★ THE MONITOR LINE IS NOW YOUR JOB — Tamer named it explicitly

> **Tamer's instruction: the next session must "dive very deep and very deeply monitor this whole run,
> the processes, the outputs, the results."** That was a DEDICATED LANE. It is now yours, on top of
> ops and coord. **Monitoring is not a status glance — it is re-deriving the number.**

**Every defect this project has found on "rung four" was the INSTRUMENT being wrong, not the
measurement.** Today alone: the rung forecast said the campaign could not reach rung 30 (it counted
one tier of twelve); the analysis loader silently dropped 68 % of the archive; a cost script's glob
silently widened into treatment arms. **A green board is not evidence. Re-derive.**

| cadence | what | how | what it means |
|---|---|---|---|
| **EVERY BATCH** | the cycle log | `tail -3 docs/ops/watch/CYCLE_LOG.md` | **>2 min old ⇒ the loop is DEAD.** `drift` and `sci` are the only two that must never change |
| **each session, + after ANY fix you make** | the sentinel, 19 checks | `python scripts/sentinel.py outputs/campaign_cluster_run4` | ⚠ **NOTHING SUPERVISES IT.** If you fix it you must restart the `--watch --interval 300` process yourself or your fix is invisible |
| **each session** | the verified board | `python .claude/lanes/openitems.py --open` | every row re-derives its own status from the repo |
| **each session** | **the RECORDS themselves** | `docs/analysis/record_validator.py` · `output_integrity.py` · `search_integrity.py` · `substrate_watch.py` | per-record contract checks. **They glob the archive DIRECTLY, which is why they were unaffected by the loader defect** — that independence is the point |
| **each session** | processes | the parentage filter in §3 | drivers · supervisors · **1** cycle loop · **2** sentinel. Counts oscillate (see above) |
| **each session** | progress | records by tier; `frozen*/` arm census | is every incomplete line still producing? |
| **as C4 opens** | the queue | `qstat -u ucestes` | `qw` should go from ~10 to **hundreds**. **If C4 opens and `qw` stays near zero, the pipelining did not take — investigate** |
| **weekly / on change** | disk + mirror | `check_disk`, `check_mirror_freshness` | floor 20 GB (CRITICAL below); the D: mirror is what makes a C: failure cost ≤5 records |

**THE FOUR TELLS — they are how you read an instrument rather than trust it:**
① A clean baseline that already reads the failing value proves nothing.
② Three failures in a row is a broken harness.
③ **A clean 0 % or 100 % means suspect the SPECIFICATION** — "309/309 batches requeued" was the
normal state; `wall_clock: 0.0` on every test record is specification, not a bug.
④ **When a comment and the code disagree, the COMMENT is the more dangerous artefact.**

**And three values, not two: ZERO · ABSENT · LAUNCHED.** A unit directory with an `_env/` sidecar and
no `record.json` means *started*, not finished; a `.o` file that exists but is empty means the job
began. **A glob that counts `*.json` turns launched into finished.**

**WHAT "DEEP" MEANS IN PRACTICE:** when a number matters, get it a **second, independent way** and
require the two to agree. The rung-189 forecast is trusted precisely because a per-unit
remaining-work calculation and the sentinel's rate-based forecast — computed from opposite
directions — landed on the same rung. **One derivation repeated is not evidence.**

---

## §2 ★★★★ STUDY THIS BEFORE YOU ACT — Tamer's explicit instruction

**Do not touch anything until you can answer the questions in §2.3.** Reading order:

### §2.1 The contract and the state
1. `CLAUDE.md` — the PRIORITIES, the four authorities, the absolute rules. **Non-optional.**
2. `docs/HANDOFF.md` §1 (state) → §2 (standing orders) → §3 (the authority map: one owner per truth).
3. `memory/session-current-focus.md` — the ▶ NOW cursor.
4. **`CHANGELOG.md` `[2026-08-01o]`** — this session's full record, §1–§74. **It is long and it is the
   point:** it contains every defect found, every correction made against itself, and the reasoning
   behind each decision. Read it before re-deriving anything.

### §2.2 The science, so you can tell a defect from a finding
5. `PREREGISTRATION.md` — the frozen design. **H2 is the headline**; the null is the predicted branch.
6. `docs/SESOI_DERIVATION_2026-07-25.md` §"Power consequence" — **why rung 189 is the number that
   matters**: MDE ≤ SESOI at n\* ≤ 173, below which a Sharpe non-rejection is reported honestly as
   **INCONCLUSIVE**, never "equivalence".
7. `config/campaign.yaml` — `seeds: {mode: tiered, tiers: [30,100,189,279,340,403,568]}`.
8. `docs/CAMPAIGN_EXECUTION_RECORD.md` §20 (the mistake ledger) and §100.x — how this project records
   errors. **Every mistake, including your own, goes here with root cause · how it was found · the fix
   · the lesson.**

### §2.3 You are ready when you can answer these WITHOUT looking
- What are the four authorities, and which arbitrates a conflict?
- Why is the campaign's *reported* result the **COMMON rung** — a minimum over lines — and why does
  that make capacity given to a leading line worth exactly zero?
- What is the C1 → C2 → C3(gate) → C4 sequence, and why do `distributional`/`scalar` hold **zero test
  records in every line** right now? *(Because both are `h2_arms`, tested only in C2, which sits
  behind the C1 barrier no line has passed.)*
- What does the C3 gate actually read, and why can it never be biased by an observed effect?
- Why is `--chunk-tasks 1` correct and why would "improving" it park 96 % of C4 in `hqw`?
- What is the ONE thing that is unrecoverable if missed at teardown?

---

## §3 IN-FLIGHT STATE — VERIFY THESE FIRST (measured 2026-08-01 22:28 UTC)

```
  RUNNING_SHA   dd51ba59          HEAD 31361727      freeze 3ca6f01ab772… MATCHES
  drift         0 BOTH arms       sci=OK             PYTEST_RC=0 (read FROM THE LOG)
  records       2,854             spend $45.4541     C: 25.2 GB free (floor 20.0)
  processes     22-24 drivers · 11-12 supervisors (OSCILLATES, see §1) · 1 cycle loop · 2 sentinel
  reproducibility  audit_reproducibility.py = 8 PASS / 0 WARN / 0 FAIL   ← Priority 5
```

**Arms frozen /5:** core 6 · gemini 5 · gpt-luna 5 · haiku 5 · qwen3.5-9b 5 · qwen3.6-27b 5 · sonnet 5
· **deepseek 4 · glm 4 · kimi-k3 4 · nemotron 4** ← the remaining search critical path.
**Records by tier:** core_test 390 · leg_test 415 · **h3 568 (COMPLETE)** · search 1,480.

**YOUR FIRST CHECKS:**
```bash
tail -3 docs/ops/watch/CYCLE_LOG.md                                    # the mandate
git diff --name-only dd51ba59 HEAD -- src scripts config prompts       # drift arm 1 — MUST be empty
git status --porcelain -- src scripts config prompts                   # drift arm 2 — MUST be empty
python .claude/lanes/openitems.py --open                               # the verified board
python scripts/sentinel.py outputs/campaign_cluster_run4 2>&1 | tail -20
```
```powershell
# ⚠ FILTER ON Name AND -File, and EXCLUDE SUBSHELLS BY PARENTAGE, or you will invent processes.
$b=@(Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'bash.exe' -and $_.CommandLine -like '*cycle_loop.sh*' })
$p=$b.ProcessId; @($b | Where-Object { -not ($p -contains $_.ParentProcessId) }).Count   # real loops
```
**A loose `CommandLine -match` matches YOUR OWN QUERY.** This bit RUN 11 twice and me three times.

---

## §4 THE PRIORITIES (they ACCUMULATE; nothing is ever dropped)

1. **95 %+ grade floor**, as close to 100 % as possible.
2. **World-class, publishable** (TMLR-and-up / ICAIF-main).
3. **Very deep** — mechanism and intuition over breadth.
4. **Corpus-grounded AND genuinely novel** (196+ first-hand-read papers).
5. **★ 100 % REPRODUCIBLE — a WARN counts as a FAIL.** Currently **8 PASS / 0 WARN / 0 FAIL**; keep it.

**Tamer's standing instruction, verbatim:** *"I don't give ten fucks about freeze, or unfreeze, hashes,
bounds, or anything else if that shit even dares to threaten the quality of the campaign… I grant you
full permissions, on the level as me… Do not stop until you absolutely strictly and deeply verify that
absolutely everything is strictly flawless."*

**Dr Okhrati is OUT OF THE LOOP. You decide — and you RECORD the reasoning so the decision is
auditable rather than merely authorised.** Full permission raises the bar on the thinking; it does not
remove it.

---

## §5 HARD PROHIBITIONS — every one was earned

- **NEVER add Claude/Anthropic attribution** anywhere. `Co-Authored-By` is **REVOKED**. Tamer is sole
  author. **Re-read every commit message before committing** (`git log -1 --format=%B | grep -ci claude`).
- **NEVER `git clean -xfd` or any `-x`** — a dry run showed **1,264 paths** would go, including the
  frozen panel and the licensed gold.
- **NEVER `git add -A` / `git add -u`.** Stage **by name**, always.
- **NEVER `git stash`** in this repo.
- **NEVER lower SGE priority**, never `qdel -u ucestes`; `qalter -l` is forbidden site-wide.
  When deleting your own jobs, filter by **exact job name** and delete explicit ids.
- **NEVER put backticks or backslashes in a bash heredoc or `-c` string — they EXECUTE.** Write the
  body to a file and pass the path.
- **NEVER inline `git commit -m` in PowerShell** — write a file, use `git commit -F`.
- **NEVER trust a pipe's or wrapper's exit code** — read `PYTEST_RC` from the LOG. *(I read `EXIT=0`
  from `tail` today and nearly banked it; the real code was 2.)*
- **★ NEVER read a treatment arm's SEALED-TEST outcome** until the ladder completes. The A16 window is
  **OPEN**: `distributional` is ABSENT, so **0 of 3 H2-RA legs are computable**. When you must touch
  the archive, read **exit codes, tracebacks and KEY NAMES** — not values.
- **NEVER edit `src/ scripts/ config/ prompts/` while live WITHOUT** either completing a relaunch **or**
  proving the file is outside the driver import closure and re-basing `RUNNING_SHA`:
  ```bash
  python docs/ops/import_closure.py                     # the live diff, both arms
  python docs/ops/import_closure.py path/to/file.py
  ```

---

## §6 THE INSTRUMENTS YOU NOW OWN (all three lanes')

| where | what |
|---|---|
| `docs/ops/cycle.py` + `cycle_loop.sh` | the 2-min cycle; `RUNNING_SHA` + `DRIFT_PATHS` live here |
| `scripts/sentinel.py` | **19 checks**, `--watch --interval 300`. **NOTHING SUPERVISES IT** — if you fix it, you must restart it yourself or the fix is invisible |
| `docs/ops/import_closure.py` | the live-edit protocol's prover. Takes arguments |
| `docs/ops/write_campaign_summary.py` | **the teardown item.** Refuses while live (**exit 2**), `--dry-run` verified green |
| `docs/ops/cost_decomposition.py` | report-only; **now deny-by-default on sealed arms** |
| `docs/analysis/*.py` | record_validator · output_integrity · search_integrity · substrate_watch · results_cycle · mutation_test — **per-record instruments that glob directly, so they were NOT affected by the loader defect** |
| `.claude/lanes/openitems.py` | the verified board — **every row re-derives its own status** |

---

## §7 OPEN ITEMS (5) — all now yours

| item | what to do |
|---|---|
| **M166 `campaign_summary.json`** | **RUN IT AT TEARDOWN**, before the archive is disturbed. **THE ONLY UNRECOVERABLE ITEM.** Four registered analysis keys (`benchmark_floor`, `attribution`, `h2_rf_robustness`, `regime_stratified`) exist ONLY if it is written. **Verified working:** `--dry-run` passes, cross-check val 694 / test 1571 |
| **DRIVER-BOUND (D24)** | `_outage_is_fatal` OR/AND: **3.6 h at the live `--poll-secs 180`**, not the documented 12 h. Patch written; deferred because `driver.py` IS in the closure. Realised cost ~10 min (supervisor retries + watchdog) |
| **LOADER-POOLING** | the ratio half is GREEN after the A79 fix; the `.pull_tmp` half is fixed this session — **re-run its verifier to confirm it closes** |
| **F-1/F-23 leg4 h2_pair** | **Closed by MEASUREMENT, not deferral**: `distributional`/`scalar` are empty in EVERY line because both are `h2_arms` tested only in C2, behind the C1 barrier. It will re-derive OPEN until C2 runs |
| **A16-WINDOW** | a clock, not an action. Flips only when `test/distributional` holds a record **alongside a comparator** |
| **ToC order (cross-boundary)** | IFTE0008 binds ToC → LoF → LoT; we ship LoF → LoT → ToC. **TWO halves that must land TOGETHER — see §0.1.** Yours alone leaves the document with NO ToC. The document currently has exactly ONE; the full instruction is already written into `paper/FRONT_MATTER.md`. **Presentational — coordinate with the writer or leave it.** |

**Also standing:** re-take the **final compute figure** after all arrays drain (`qacct` excludes RUNNING
jobs; the ledger's 67,166 CPU-h is a LOWER BOUND) · the **`variance`** analysis key needs ≥2 independent
search re-run roots that RUN 4 does not have — **commission it or disclose it, do not discover it at
submission** · D22 `provenance.py` encoding.

---

## §8 ★★★ WHAT THIS SESSION PAID FOR — read these, they are the real output

1. **THE MONITOR SAID THE CAMPAIGN COULD NOT REACH RUNG 30. IT WAS COUNTING ONE TIER OF TWELVE.**
   `done_test_units` globbed only `camp_root/test` and was fed to a forecast whose denominator is
   campaign-wide. Fixed; **now reports rung 189**, which an independent per-unit calculation
   corroborates. *A monitor can be confidently, catastrophically wrong.*
2. **THE ANALYSIS LOADER SILENTLY DISCARDED 68 % OF THE ARCHIVE.** `run_id` carries no line — every
   line writes `distributional-s0` — so a global `run_id` key merged twelve lines. **732 returned vs
   2,260 on disk.** Fixed by keying `(directory, run_id)`.
3. **AND THAT FIX INVERTED A SECOND DEFECT.** `.pull_tmp` used to *displace* a record; afterwards it
   *duplicated* one. **Duplication is harder to notice because the totals look better, not worse.**
   *When you fix a de-dup, re-check every other defect that depended on the old key.*
4. **A SCOPE THAT WAS SAFE ON THE DAY AND EXPIRED SILENTLY.** `cost_decomposition.py` was written when
   `test/` held only baselines; C4 widened its glob automatically until it would print a treatment
   arm's sealed Sharpe. **Nobody had to do anything wrong.** *Audit implicitly-scoped globs whenever
   the archive's shape changes.*
5. **CHECK REPARSE POINTS BEFORE SIZING OR MOVING ANYTHING.** `Lumion 12.5` read 37 GB while its
   PARENT read 12.6 GB — it is a junction to D:. **The contradiction was the signal.**
6. **A CLEAN 0 % OR 100 % MEANS SUSPECT THE SPECIFICATION.** "309/309 batches requeued" was the
   *normal* state (`rounds` increments after the first submit); `wall_clock: 0.0` on all 591 test
   records is *specification*, not a bug.
7. **ZERO, ABSENT and LAUNCHED are three different values** — and a `.o` file that exists but is empty
   means STARTED, not finished.
8. **OVERSTATING A RISK IS AS INACCURATE AS UNDERSTATING ONE.** I twice raised alarms that measurement
   dissolved (the disk forecast "never arms"; d97a "family disabled"). **Verify in BOTH directions.**

---

## §9 THE THROUGHPUT ANSWER — do not re-open it without new evidence

The lever inventory is **exhausted and documented** (CHANGELOG §21): more pools/nodes (**would break
substrate homogeneity and park the C4 gate**) · more cores (**work-bound**: ~11 queued against ~2,700
free) · K=5 (registered) · `search-threads` (**changes BLAS reduction order = changes arithmetic**) ·
`h_rt` · tmpfs (already fixed) · memory · priority · chunking · pack (**D26 REFUTED — its case rested
on 49 "empty" nodes that are all PAID allocations**) · barriers · job cap · reservation (**verified ON**).

**d97a/d97b are 100 % `@PAID_Economics` — we cannot be placed there at all.** 89 Myriad nodes belong to
paid departmental allocations; **a capacity number computed over nodes you are not entitled to is not
a capacity number.**

**THE FORECAST: common rung 189**, agreed by two independent routes. **189 is where the H2 verdict
stops being INCONCLUSIVE.** The decisive throughput threshold is **65 records/h** for the full 568
ladder; today's measured rate is ~30–48/h. **Verify the rate when C4 opens rather than asserting it.**

**WHEN C4 OPENS:** `qw` should go from ~10 to hundreds. **Expect driver crash-loops** around `qsub` at
the `max_u_jobs 1000` breach (D25) — they self-heal via `--resume` and **must not be "fixed"
mid-ladder**. If a C4 block reports **INCOMPLETE**, treat it as urgent: the ladder caps there and
every block above it is unbanked compute — check that batch's `.permanent.jsonl` first.

---

## §10 END-OF-WORK DUTIES (all four, every time)

`python scripts/update_handoff.py` · a SHORT cursor ▶ NOW entry · a **DETAILED `CHANGELOG.md` block
even with no commits** · push the backup branch when commits were made.

**Document PAST · PRESENT · FUTURE, and record every mistake — including your own — with root cause,
how it was found, the fix and the lesson.** Tamer's stated reason: *"document absolutely everything as
this would help me for the write up."* The record is the primary source CH4/CH6/CH7 are written from.
