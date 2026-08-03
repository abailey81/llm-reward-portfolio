# LANE PROTOCOL — how the concurrent Claude Code sessions on this repo stay out of each other's way

**Status:** live from 2026-08-01, built by the `coord` lane at Tamer's instruction
(*"3 claude code sessions working together in parallel — establish a very advanced and sophisticated
communication and connection between them"*).

**Relationship to the earlier documents.** `docs/LANE_COORDINATION_2026-07-27.md` and
`docs/LANE_COORDINATION_2026-07-31.md` remain the **narrative record** — who did what, and the
incident evidence. **They are not superseded.** This file is the **operating protocol** and the
machinery that enforces it. Where the 07-31 file states ownership, this file encodes that same
ownership in a form a hook can check.

---

## 1. Why machinery, and not another rule

Every rule in the 07-31 file is correct and was still violated, because a rule only binds a session
that remembers to re-read it. The measured cost, from the record:

| # | what happened | why a rule did not stop it |
|---|---|---|
| 1 | an Edit to `CHANGELOG.md` hit *"the file had been modified on disk since you last read it"* | nothing made staleness visible before the write |
| 2 | both lanes independently found and fixed the same false *"the sweep missed RDA"* claim | neither could see the other was already on it |
| 3 | ops used P31–P41 while the grade lane also started at P31 | two allocators, one namespace, no arbiter |
| 4 | one lane's `git add` + bare `git commit` swept 14 files another lane had staged | the git index is shared state and looks private |
| 5 | both lanes launched `leg_gates --all`, each billing OpenRouter for the same 10 legs | no one declared before spending |
| 6 | an edit under `src/` turns the ops monitor RED within ~42 s on a live confirmatory campaign | the fence was documented, not enforced |

So: **append-only state, machine-checked ownership, and identity that costs nothing to establish.**

## 2. The bus, in one minute

Everything lives in `<project>/.claude/lanes/` — deliberately **outside the git repo**, so bus
traffic can never be swept into a commit, never appears in `git status`, and can never trip the
drift monitor.

```bash
# from llm-reward-portfolio/ — join once per session, then use freely
L=".venv/Scripts/python.exe ../.claude/lanes/lanebus.py"

$L join ops                     # or writeup / coord — identity comes from CLAUDE_CODE_SESSION_ID
$L board                        # who is live, what is held, open threads, the live campaign line
$L inbox                        # messages addressed to me since I last looked
$L msg writeup "..." --needs action     # a directed request that cannot rot in prose
$L say "..."                    # broadcast
$L alert "..."                  # high-priority broadcast
$L ack M7 "on it"  |  $L done M7 "landed in 15e"
$L claim "paper/CH6_results.md" --ttl 60 --why "results pass"
$L release "paper/CH6_results.md"
$L next P                       # atomic id from a shared series — ends the P-collision
$L spend "leg_gates --all, ~$0.40, starting now"   # declare BEFORE anything paid or slow
```

**Identity is free.** `CLAUDE_CODE_SESSION_ID` is exported into every session's shell and is present
in every hook payload, so a session never has to be told who it is; `join` binds it once.

**Presence is free.** The `PreToolUse` hook heartbeats on every tool call, so liveness needs no
discipline and a stalled session is visible within one cycle.

## 3. What is enforced, and the deliberate limits

`.claude/hooks/lane_guard.py` runs on `PreToolUse` and enforces three things:

1. **The drift fence.** An edit to `src/`, `scripts/`, `config/`, `prompts/` by a lane that is not
   the fence owner (`ops`) is **denied**, with the reason and the escape hatch in the message.
2. **Another live lane's claim.** An edit to a path another *live* lane holds is **denied**, naming
   the holder, the reason and the expiry.
3. **Bulk git staging while more than one lane is live** — `git add -A|-u|.`, `git checkout -- .`,
   `git restore .` — **denied**, because the index is shared. Use
   `git add -- <paths> && git commit -F <msg> -- <paths>`.

Four limits, each chosen on purpose:

* **FAIL-OPEN.** Any exception, missing file or unparseable payload allows the tool, silently.
  A broken guard must never block real work.
* **NEVER `ask`.** An `ask` waits for a human; these sessions run unattended overnight, so an `ask`
  is a stall. Every enforcement is a `deny` the model can resolve in one step, or nothing.
* **An unregistered session is NEVER blocked.** Enforcement requires a positively identified
  non-owner. A wrongly blocked live campaign is far worse than an unfenced edit, which the ops
  monitor catches within ~42 s anyway.
  > ⚠ **This was TRUE of the fence and FALSE of claims for about an hour on 2026-08-01, and the
  > selftest caught it in production.** The claim branch had no `if not lane` guard, so the moment
  > the ops lane joined and its `src/**` hold went live, an unregistered session was denied by every
  > active claim — across `src/`, `scripts/`, `paper/` and `outputs/` at once, for no reason it could
  > see. The case *"an unregistered session is NEVER blocked"* passed all night and began failing the
  > instant a real lane took a real hold. **Fixed, and now pinned by two cases** (a fenced target and
  > a merely-claimed one — they fail independently). Recorded because the lesson is not "add a guard"
  > but *a documented safety property that no test exercises against live state is a claim, not a
  > guarantee.*
* **Kill switch:** `touch .claude/lanes/DISABLED` makes the hook a no-op immediately.

Verify either half at any time:
`python .claude/lanes/lanebus.py selftest` · `python .claude/hooks/lane_guard.py --selftest`.

**Verified end-to-end against live state, 01:58Z** — `check Edit src/cluster/driver.py` → DENY (fence),
`paper/CH6_results.md` → DENY (write-up's claim), `docs/ops/cycle.py`, `CHANGELOG.md`,
`docs/LANE_PROTOCOL.md` → ALLOW.

**Two honest limitations, both found by testing this on myself:**

* **The bulk-git rule matches the command STRING, not a parsed shell command.** A command that merely
  *mentions* `git add -A` — including inside a quoted argument — is denied. It fired on the coord
  lane's own probe. This errs in the safe direction (deny, with the reason stated) and is left as-is
  rather than fixed with fragile shell parsing; if you hit it, rephrase the argument.
* **Claim-based protection is inert for a lane that has not joined.** A claim only blocks while its
  holder is *live*, so `docs/ops/**` is unprotected until ops registers. **The drift fence is not
  affected** — it is owner-based, not liveness-based, and denies a non-`ops` edit under
  `src|scripts|config|prompts` whether or not ops is on the bus. Verified above.

**Delivery is PULL, by design.** Mail reaches a session through `inbox`, through the `SessionStart`
board, and through the `UserPromptSubmit` digest. It is deliberately *not* pushed into a peer
session's reasoning mid-turn: one agent steering another's context is a boundary this protocol does
not cross. **So check `inbox` when you start, and after any long stretch of autonomous work.**

## 4. Ownership as encoded (from `LANE_COORDINATION_2026-07-31.md` §1)

| lane | holds |
|---|---|
| **ops** | `src/**` `scripts/**` `config/**` `prompts/**` `docs/ops/**` `docs/DEFERRED_FIXES_RUN4.md` `docs/CAMPAIGN_EXECUTION_RECORD.md` `outputs/**` |
| **writeup** | `paper/**` `docs/GRADE_95_MASTER_PLAN.md` `docs/V2_WRITE_TIME_REGISTRY.md` `docs/CITATION_WORK_MAP.md` |
| **coord** | `.claude/lanes/**` `docs/LANE_PROTOCOL.md` `docs/COORD_LANE_FINDINGS_2026-08-01.md` |
| **shared — coordinate, never assume** | `CHANGELOG.md` · `memory/session-current-focus.md` · `docs/HANDOFF.md` |

Shared files are **append/prepend by convention and unclaimed**. Re-read immediately before editing,
or take a short claim (`--ttl 15`) while you write.

**The standing exception, unchanged:** a lane MAY always correct its own false claim wherever that
claim propagated, including into another lane's files — but it must confine the edit to the
retraction, change nothing else in that file, and announce it. Silence is the defect, not the
crossing.

## 4d. ★ ESTABLISH THE ANSWERING INSTRUMENT BEFORE YOU ANALYSE (added 2026-08-01, with its cost measured)

**Proposed by the analysis lane after the leg4/leg9 episode, and adopted here because the cost is
measured rather than argued.**

> **Before a lane invests in a cross-lane question, state WHICH ARTEFACT WOULD SETTLE IT AND WHO
> HOLDS THAT ARTEFACT. If the answer is another lane, ASK FIRST AND ANALYSE SECOND.**

**What it cost not to do this, once, in one night.** The question was *"is leg4's `h2_pair` batch
lost or merely waiting?"* Two lanes spent roughly **four hours and fifteen bus messages** on it:
`driver_status` forensics, epilogue-ledger comparisons, blob diffs, an arrival-rate proxy, a dated
falsifier with a stated refutation time, a Wilson interval, **two retractions and a recalibration.**
**The ops lane answered it with one `qstat`** — leg9's packs alive on the cluster, leg4's gone.

Everything produced along the way was individually sound, and the *lost-not-failed* conclusion did
survive. **The routing was wrong from the first message: nobody asked which lane could even answer
it.** The analysis lane's own quantified-causal error existed *only* because it was reasoning around
missing evidence instead of requesting it.

**And the negative result is load-bearing, so it is recorded rather than assumed.** The analysis lane
then checked exhaustively whether any laptop-side signal distinguishes *array alive on Myriad* from
*array gone*: pack directory contents (identical — three files each, no submission marker, no job-id
file), job ids (not recorded laptop-side at all; `driver_status` carries ten keys and none is a job
id), status blobs (identical in every substantive field), 24-hour file-activity counts (17 vs 17),
epilogue ledgers (already known non-discriminating). **There is no such signal. Not a weak one —
none.**

Two consequences that follow from the negative, not from preference:

1. **A periodic ops-side dump of live array names** into `docs/ops/watch/` is not a convenience, it
   is **the only available mechanism** by which any laptop-side lane can ever distinguish those two
   states — tonight, or at the core line's C4.
2. **An alarm that cannot distinguish two states must say so.** `batch_progress`/W2 keeps its
   limitation clause even if a dump arrives, because **a dump can go stale and the clause is what
   makes that visible.**

## 4e. ★ ENUMERATE THE RECORD TYPES BEFORE YOU PARSE — do not infer the grammar from the tail

**Contributed by the ops lane on 2026-08-01, correcting a weaker lesson of mine, and it is the better
rule.** I reported that a new `[STILL PRESENT (hourly heartbeat)]` block in `ALERTS.txt` had broken my
W4 detector, and framed it as *"another lane's format change is a dependency you did not know you
had."* **Ops checked before replying and the attribution was wrong** — verified here first-hand:

* the block is written by `docs/ops/cycle_loop.sh`, **not** `cycle.py` (`grep -c`: 1 vs 0);
* it was introduced by a **previous session** on 07-31, not by anyone working that night;
* **the first one is timestamped `2026-07-31T15:50:29Z` — fourteen hours before I built W4.**

**So nothing changed. My parser was validated against a corpus that did not contain a record type
which had been sitting in the same file all along.** That is not a cross-lane dependency — **it would
have bitten me with no other lane in existence.**

> **THE RULE: when you build a parser for an existing artefact, ENUMERATE THE DISTINCT RECORD TYPES
> ALREADY IN IT AND ASSERT YOUR PARSER HANDLES EACH. Do not infer the grammar from the tail.**

**One command would have shown it in a second** — and now does:
`grep -oE "^===== \S+ +rc=[0-9]+ +\[[^]]+\]" ALERTS.txt | ...| sort | uniq -c`
→ `98 [CHANGED]` · `6 [STILL PRESENT (hourly heartbeat)]`.

**This is the third instance of one class across two lanes in a single night**, which is why it earns
a rule rather than a note:

| instance | the member class the instrument had never been shown |
|---|---|
| coord, substrate check | the `_env/` launcher sidecar, which carries no `cpu.model_name` → `MIXED` on 12/12 units |
| coord, W4 | the `[STILL PRESENT]` block, present for 14 h → hourly false alarm, for ever |
| analysis, R115 winners | the frozen **marker**, which carries no R115 fields at all → 27 fabricated `0.0000`s |

**And the reciprocal obligation, which ops then discharged unprompted:** they flagged that
`results_audit.py` gained a new section *3b. E[max] ARM POOLS* and that `cycle.py` now reads arm
counts from it — *"if anything of yours parses results_audit §3, that is a real format change and it
IS mine."* **Announcing a format change before anyone trips on it is the habit; enumerating the
existing types is the defence when nobody does.**

## 5. The rules the machinery does not cover

1. **NEVER `git clean -xfd`** — measured 1,264 paths removed including the licensed frozen panel.
2. **Declare before you spend or before anything slow** (`lane spend "..."`) — the double-billed
   `leg_gates` run is the precedent.
3. **Never snapshot another lane's live buffer** — check mtime first.
4. **Announce a correction before fanning out to fix it**, or two lanes do the same work.
5. **THE FREEZE IS TAMER'S ALONE** (R94). No lane freezes.
6. **NEVER lower a Myriad job priority.** Absolute.
7. **Effect-blindness** — no lane reads a treatment arm's sealed-test outcome before the ladder
   completes and the registered analysis runs.

## 5b. ★ THE OPEN-ITEMS BOARD — and the coord failure that forced it (added 2026-08-01)

```
python .claude/lanes/openitems.py            # every cross-lane commitment + its status
python .claude/lanes/openitems.py --open     # only what is not DONE
python .claude/lanes/openitems.py --selftest # prove the verifiers can return both answers
```

**Why it exists, stated as the failure it was.** Between 12:15 and 14:45 the **coord** lane emitted
**23 messages / 99,117 characters** — *more volume than ops (12/55k), analysis (20/79k) or write-up
(10/39k)* — opened **8 `needs=action` items**, and closed **none**. Across the bus's whole life there
are **10** `ack`/`done` events. **Coordination is not sending; it is knowing what is open, who owns
it, and whether it is done.** Measured afterwards, of four routed items **one had landed and three
had not, and nobody knew** — the only record was prose scattered over 200 threads.

**The design rule, the same one the rest of this machinery follows: a status nobody can re-derive is
a rumour.** A row carries no hand-typed status — it carries a **verifier** that inspects the real
artefact and returns `DONE` / `OPEN` / `UNKNOWN`. Running the file re-derives everything from the
repo as it is now. **A lane that disagrees with a row runs its verifier instead of arguing.**

> **⚠ AND THE BOARD'S FIRST RUN CONTAINED A FALSE `DONE` — logged as P157, fixed, and left in the
> file as a comment.** `F-18`'s verifier pattern-matched the *source* for something guard-shaped and
> reported a guard that does not exist; an execution test in the same minute returned `rc=0` having
> reached no compile path. **A false DONE is the most dangerous direction a status board can fail
> in** — it tells an owner their open item is closed. That verifier now **runs the thing** (stubbed,
> writing nothing) rather than reading it. **Every verifier here should be judged by whether it
> could have said the other answer.**

**Adding a row:** append an `Item(...)` to `REGISTRY` with a *cheap* verifier — no cluster calls, no
builds; it must stay runnable in seconds by any lane at any time. `raised_by` is recorded so credit
does not drift, which has already cost two lanes a re-discovery today.

> ### ★★ ASSERT THE PROPERTY, NOT THE FIX YOU IMAGINED — the board's own worst defect, three times
>
> **Three of the first eight verifiers were wrong, and all three failed the same way.**
> **P157** — a **false DONE**: pattern-matched the source for something guard-shaped and reported a
> guard that did not exist. **P160** — a **false OPEN**: searched for a hardcoded digest string, but
> ops had *derived and checked* the bundle at build time instead, which is strictly better and
> contains no such string. **P164** — a **false OPEN**: treated any occurrence of
> `h2_ra_iut_or_tost` as staleness, but the correct fix **requires naming it** to separate the
> REGISTERED field from the EXECUTED rule; the check would have read OPEN forever against a perfect
> fix while its author told four lanes the item was outstanding.
>
> **THE COMMON CAUSE: a verifier written by the person who RAISED an item inherits that person's
> assumption about how it will be SOLVED — and owners keep solving things better than the raiser
> imagined.** That is exactly what you want from an owner and exactly what breaks the check.
>
> **So: assert the PROPERTY that matters, never the artefact you expect to see.** Not *"the old
> string is gone"* but *"the row states the executed rule and makes no overclaim"*. Not *"the digest
> constant is present"* but *"the provenance helper is defined and called"*. **And judge every
> verifier by whether it could return the OTHER answer** — a false DONE tells an owner their open
> item is closed, and a false OPEN tells them their finished work is unfinished; both erode the one
> thing the board is for, which is not having to take another lane's word for a status.

## 6. Superseded when

RUN 4 stops (2026-08-27) and only one lane remains. Until then this file, not memory, is the
protocol; `docs/COORD_LANE_FINDINGS_2026-08-01.md` carries what the coord lane has found.
