# COORD LANE — findings, 2026-08-01 (overnight)

**Who wrote this.** The third concurrent Claude Code session, registered on the lane bus as `coord`.
Its remit, set by Tamer at ~01:20 UTC: link the concurrent sessions, then watch continuously and
verify independently. It owns `.claude/lanes/**` and this file. **It holds no lock on `src/`,
`scripts/`, `config/`, `prompts/`, `outputs/` or `docs/ops/` and has not written to any of them.**

**Why a separate file.** `CLAUDE.md` requires that the author not grade their own work. These are
findings *about* the ops lane's instruments, produced by a lane that did not build them. They are
routed to ops as bus threads (`M6`, `M7`) and recorded here so they cannot rot in a chat transcript.

---

## F-1 ⚠⚠ CRITICAL, LIVE — leg4's H2 primary contrast has been dead for ~10.8 h and is unattended

`leg4` = `qwen3.5-9b`, **the first line to reach C4**, all five arms frozen.

| evidence | value |
|---|---|
| last `h2_pair_test` line in `driver_qwen3_5-9b.log` | **2026-07-31 15:44:30 local**, `0/60 done, 60 pending, round 1` |
| `test_leg_qwen3_5_9b/distributional` records | **0** |
| `test_leg_qwen3_5_9b/scalar` records | **0** |
| `test_leg_qwen3_5_9b/placebo` records | 24 |
| `test_leg_qwen3_5_9b/scalar_cvar5` records | 2 |
| the refusal, `2026-08-01 01:55:42` | `RuntimeError: another driver (pid 34216) is already running batch 'leg4_leg_qwen3_5_9b_h2_pair_test.driver.lock'` |
| locks held now (live pid 30516, started 02:05:46) | `placebo_test`, `placebo_shuffled_test`, `scalar_cvar5_test` — **no `h2_pair_test`** |
| leg9 (`gemini-2.5-flash`), the healthy comparison | **holds** `leg9_..._h2_pair_test.driver.lock`; its pack dirs written `2026-08-01 01:56` |
| leg4's `h2_pair_test_p01..p08` pack dirs | untouched since **2026-07-31 12:12** |

> ### ⚠ CORRECTION, 02:10Z — I OVERSTATED THIS, AND THE CORRECTED VERSION IS SHARPER
>
> I originally wrote that the batch "is not blocked — it is simply no longer being driven." **That
> was an inference from two absences (no lock, no log lines) stated as an observation, and it is not
> established.** Read first-hand afterwards, `src/cluster/campaign.py:1832–1846` builds the H2 pair
> test from the arms' winners **after** the concurrent per-arm block drains — so `h2_pair` is
> *sequenced behind* the per-arm test legs, and leg4's are demonstrably still running (`placebo_test`
> 0/6, `placebo_shuffled_test` 0/30, `scalar_cvar5_test` 2/30, locks held by live pid 30516 since
> 02:05:46). **A re-attempt may therefore happen on its own.** I have no evidence either way, and
> saying so is the accurate position. Everything in the table above is unchanged — it was measured.
> The finding that replaces the overstatement is **F-4**, and it is worse.

**Reading of it.** The batch was submitted (8 packs), then the driver was refused by a stale lock
whose pid had been **recycled** onto an unrelated process — the exact failure the ops lane's
in-flight **D20** fix addresses, and pid 34216 is the very pid named in that fix's own docstring.

**The shape that makes it dangerous: the controls raced ahead while the treatment contrast produced
nothing.** A line that dies is loud and self-heals; a line that loses *one batch* stays alive on its
survivors and is silent. That is the leg7 asymmetry (`docs/ops/arm_coverage.py` header) recurring at
the *batch* level rather than the *arm* level.

**Scope, stated in both directions.** leg4 is a **report-only replication leg (R80)** — the
**confirmatory H2 is NOT affected**. But (a) the open-weight replication suite is what answers the
industry supervisors' criterion #1, and a leg whose H2 pair never ran contributes nothing to it; and
(b) **leg4 is the canary for the CORE line's own C4, ~16–26 h out.** The same class of event on the
core line would hit the confirmatory result itself.

**Not actioned by this lane.** Re-adopting the batch is a live-campaign operation in ops territory.
Handed over as bus thread `M7` with a recommendation, not a change.

## F-2 THE DETECTOR GAP — nothing watches per-`(line, batch)` PROGRESS

This is worth more than the single line above, because it is what turned a 20-minute problem into
10.8 hours — and 8 h 29 m for leg7 before it.

| instrument | what it actually measures | why F-1 is invisible to it |
|---|---|---|
| `stalest` (cycle line) | driver **heartbeat** age | the driver is alive and logging every 3 s; `stalest = 2.9 m` |
| `arm_coverage.py` | batch **submission** per `(line, arm)` from `batches/` | the packs *were* submitted; the registry entry exists |
| `science_watch` / `results_audit` | invariants over records that **exist** | a record that was never produced violates nothing |
| `campaign_watch` | a state **signature** keyed on kinds | a batch quietly leaving the driven set changes no kind |

So `arms_full=10/10` is simultaneously **true and wrong**. The missing predicate is one sentence:
*"this batch's `done/pending/round` tuple has not moved in N hours while its siblings advanced."*

⚠ **Any such detector must key on progress, not on record arrival.** Record file mtimes are **pull**
times, not production times, and trainings run for hours, so multi-hour record silence is normal and
would produce constant false alarms (see N-2 below — exactly the mistake this lane nearly made).

> **⚠ CORRECTION to my own figure, and it is the same error twice.** I first wrote "a training is
> 4.2 h" from **one** record's `wall_clock` of 15,254 s and then repeated it as a constant in three
> documents. Measured over **every** record in the archive (n = 1,220):
> **MIN 2.79 h · p05 3.05 · MEDIAN 4.21 · p95 7.61 · MAX 14.31 h.**
> The median vindicates the number but not the claim: the spread is a factor of five, and I had been
> warning other lanes about single-sample reasoning while doing it myself.

## F-4 ⚠⚠ THE H2 PAIR TEST IS THE ONE STAGE WITH NO EXCEPTION CONTAINMENT — and it is the confirmatory contrast

This replaces the overstatement corrected above, and it is the more serious finding.

From the traceback at `driver_qwen3_5-9b.log:27084–27125`, read in full:

```
run_campaign_tiered      campaign.py:1836
  run_test_leg           campaign.py:1270
    run_batch            campaign.py:356
      driver.run_batch   driver.py:267
        _acquire_driver_lock  driver.py:248  -> RuntimeError
...propagates to  sys.exit(main())  run_campaign_cluster.py:1464
```

**The per-arm handler does not cover it.** `campaign.py:1821`'s
`except Exception ... # one unit must not sink the ladder` sits **inside** the `as_completed` loop
over the arm futures. The pair test runs **after** that block closes, so it is outside every handler.

**Consequence: one stale lock on one batch does not fail that batch — it kills the entire driver
process.** That is exactly the *"dying 12 s into every relaunch"* crash-loop the D20 docstring
describes; the mechanism is this missing handler, not the lock itself.

**Why it matters far beyond leg4.** The **core line reaches C4 in ~16–26 h and builds the same
`h2_pair` array for the CONFIRMATORY contrast.** A single recycled-pid lock there would kill the core
driver on every relaunch, and the C4 seed ladder is the confirmatory result.

**The D20 self-heal is good, and verified — but it is a different guarantee.** `cycle.py:529–565`
reaps only on a predicate strictly narrower than unsafe (pid exists · cmdline read OK · non-empty ·
lacks `run_campaign_cluster` · lock ≥ 60 s old), and ops positive-controlled it at 01:14/01:15Z —
`REAPED_LOCKS.log` holds exactly two entries, both `explorer.exe` test locks. **It never fired on the
real leg4 lock.** Reaping removes the *blocker*; nothing re-drives a pipeline whose process has died.

**Suggested (ops' call):** give the pair-test call the same containment the per-arm block already
has, so a lock collision degrades to one failed batch instead of a dead line.

### F-4b — what the 60 stranded units actually are, and one claim I partially refuted

The analysis lane's forensics (M35) hold, and I **verified their linchpin field by field**:
`driver_status/leg4_..._h2_pair_test.json` and the **healthy, currently-running**
`driver_status/leg9_..._h2_pair_test.json` are **identical in all seven substantive fields**
(`done, exhausted, ops_failures, pending, phase, pull_failures, rounds`), differing only in
`base_name`, `queue_names` and `wall_ts` (a gap of 11.74 h). **leg4's status carries no evidence of
failure**; the healthy control is what makes that conclusive rather than suggestive.

**But their timing argument — "the first wave could not possibly have completed" — is too strong.**
leg4's h2_pair had **3.58 h** between pack creation (07-31 11:12:31Z) and driver death (~14:47Z), and
**227 of 1,220 trainings (18.6 %) finished faster than that.** Naively ~11 of the 60 would have
landed. **The caveat cuts the other way and must be stated with it:** elapsed-from-creation includes
cluster **queue wait**, while `wall_clock` measures only the training, so a wait of ≳0.8 h drives the
expectation to zero. **Honest statement: zero completions at 3 h 35 m is *consistent* with normal
operation but is not proof that nothing finished.**

**This raises the value of the decisive test rather than lowering it.** If up to ~11 units completed
on the node after the driver died with nobody left to pull them, this is a **pull gap, not a compute
gap** — recoverable, zero science lost, and leg4's H2 pair is further along than any instrument
believes. `src/cluster/poll.py:remote_completed_dirs()` already does exactly this in one bounded ssh
call. **This lane holds no ssh and will not run it.**

## F-5 D16's EXECUTION, VERIFIED FROM THE ARCHIVE BY A LANE THAT DID NOT PERFORM IT

Ops quarantined the four Xeon-6140 records and reported the unit homogeneous. **Verified
independently, from the records rather than from the operation**: `cpu.model_name` read out of the
sibling `env.json` of every completed record in the core test lane — **368 files, 0.04 s**.

**Twelve units · ZERO with a mixed substrate · one distinct CPU model campaign-wide on that lane
(`Intel(R) Xeon(R) Gold 6240 CPU @ 2.60GHz`).** `baseline_volatility_scaled_return` reads **26
records, all 6240, zero 6140** — the quarantine removed exactly the four intended records and left
the unit substrate-homogeneous.

### …and it exposed a defect in W6 that would have been falsely reassuring

The analysis lane warned ops that *a re-run landing on another 6140 reproduces the original defect*.
**That applied to my own watch and I had the bug.** W6 would have fired `SEED SETS REUNIFIED` the
moment seeds 14–17 returned, **regardless of what they landed on** — but the D16 defect was never
about seed *count*, it was about a unit spanning two CPU models. My recovery message was structurally
capable of being wrong **at exactly the moment someone would rely on it.**

Fixed: the reunification branch now checks substrate homogeneity too, with two distinct outcomes —
`SEED SETS REUNIFIED` naming the single model, or **`REUNIFIED BUT ON A MIXED SUBSTRATE … the seed
count is restored and the D16 defect has RECURRED — do NOT read this as recovery.`** Both branches
positive-controlled against synthetic archives.

**The tell paid a third time.** The first version of the substrate check reported `MIXED SUBSTRATE`
on **12 of 12** units — which is not a finding, it is a spec error: it was counting the `_env/`
launcher sidecar, whose `env.json` carries no `cpu.model_name`. Filtered to `-s<N>` directories
holding a `record.json`, it reads 0/12. Three instances in one session now — `STRANDED=298`,
`MIXED=12/12`, and the analysis lane's flat `0.0 %` PopArt — of *a detector that fires on nearly
everything is making a claim about its own specification first.*

## F-6 MY WATCH'S FIRST REAL ALARM WAS A FALSE POSITIVE — and diagnosing it produced the first proper calibration of this campaign's batch timing

At 03:21Z W2 fired on **the core line**: `c1_cma_es_c5` and `c1_placebo_g4`, both `not-advancing` at
~8.05 h with zero completions, driver alive and polling them every 45 s.

**It was false, established by the control method rather than by argument.** `driver_status` for both
reads `done=0 pending=N exhausted=0 rounds=0 pull_failures=0 ops_failures=0 phase=running` — and
`c1_bayes_opt_c15` and `c1_tpe_c14`, which were **not** flagged, are **identical in every field.** The
only thing separating flagged from unflagged was that the others' clocks started later.

### The calibration nobody had done, and it is useful beyond this watch

Measured from all twelve driver logs:

| distribution | n | p50 | p90 | p95 | p99 | max |
|---|---|---|---|---|---|---|
| healthy gaps **between** completions within a batch | 1,164 | 0.49 h | 7.08 h | 14.68 h | 28.12 h | 62.07 h |
| time to a batch's **first** completion | 254 | 5.36 h | 25.06 h | 27.95 h | 29.95 h | **30.56 h** |

**A healthy batch sits at `done=0` for up to ~30 hours.** My 480-min threshold fires on **8.59 %** of
healthy gaps — wrong by a factor of four. **And my stated justification for it was wrong in a way that
matters more than the number:** I calibrated against training length (the 4.2 h median) when
time-to-first-completion is dominated by **queue wait** — *the one variable I had told every lane I
could not observe from the laptop.* I calibrated against the quantity I could see instead of the one
that governs.

**Corrected to 1800 min = 30 h**, the measured ceiling of both distributions, **with the cost stated
rather than hidden**: that shape is now the *slow* backstop and can take 30 h to fire. The *fast*
detector is the `unmentioned` shape at minutes — and that is the one that actually caught leg4, which
remains flagged at 12.6 h unmentioned.

**And I cleared the watch baseline rather than let it absorb the two false positives.** W2 adds a new
strand to the baseline after reporting it, so leaving them there would have put two **core-line**
batches on a permanent allow-list — if either ever stranded for real it would never fire again.
**A baseline built by a mis-calibrated instrument must not outlive the calibration.** Re-derived: 6
known-benign, unchanged otherwise.

> **For the QC appendix, independent of this watch:** *"the median batch waits 5.4 h for its first
> completion and the 90th percentile waits 25 h"* is a concrete, measured statement about cluster
> contention that the campaign has never quantified, and it is the honest backdrop to any wall-clock
> or ETA claim in CH6.

## F-7 ⚠⚠ A CHECK OF MINE THAT COULD NOT FIRE — retracted, and it is the worst error of this lane's night

I reported *"no frozen winner is R115-contaminated, including all three core-line winners
(frac = 0.0000)."* **That was derived from zero measurements.**

I read `train_safe_call_count` / `train_safe_default_count` off each **frozen marker's**
`record.json` and computed `frac = (s/c if c else 0)`. **All 27 frozen markers carry neither field —
both are `None` on 27 of 27, and 0 of 27 have them.** So the fallback rendered *missing data* as
`0.0000` and printed it for every winner in the campaign. I then reported my own default value,
echoed back 27 times, as evidence of cleanliness.

**The tell was in my own output and I walked past it.** Twenty-seven values reading *exactly*
`0.0000` is a clean-100 % — the precise tell I had cited three times that same night and quoted at
two other lanes. I read uniform zeros as reassurance instead of as suspicious uniformity, because it
was the answer I wanted. **And it is a near-verbatim repeat of P47 in the execution record** — *"a
check that globbed env.json under `frozen*/` and returned a clean 0; a check that could not fire."*
I reproduced a documented past defect of this project, in my own audit of it, having read the
document that describes it.

**What is true** (analysis lane's method — resolve each marker's `candidate_id` back to its own
line's search tree on the **composite `(line, candidate_id)`** key, which is *my own P120 lesson,
applied by them and not by me — re-run and confirmed here):

| winner | frac | steps on the safe default |
|---|---|---|
| `frozen_leg_qwen3_5_9b/distributional-winner` (`distributional-g5-c0`) | **0.078535** | 31,414 / 400,000 |
| `frozen_leg_qwen3_5_9b/placebo_shuffled-winner` (`placebo_shuffled-g0-c3`) | **0.090847** | 36,339 / 400,000 |
| all 25 others, incl. the three core-line winners | **0.000000** | 0 |

Both contaminated winners sit **below** the 0.10 floor, so R115 admitted them correctly — **not a
gate failure.**

**The claim that survives, narrowed and now actually measured:** *all three core-line frozen winners
are exactly 0.000000 — the confirmatory line's selected objects are entirely uncontaminated.*

> **Note the shape, because it is why this is logged loudly rather than quietly narrowed:** my
> conclusion was **right for the core line and wrong as a generalisation**, reached by a method that
> could not have distinguished the two. A wrong reason reaching a right action is P41 and it is the
> hardest kind to catch.

**The rule this earns, beside "a value read as if its meaning matched its name":**
**in an audit script, the idioms `x or 0` and `value if denominator else 0` applied to a
possibly-absent metric convert UNMEASURED into PERFECT.** An audit must distinguish *absent* from
*zero* and say **absent** out loud — because zero is the answer that ends the investigation.

## F-8 ⚠⚠ BOTH `h2_pair` BATCHES IN THE CAMPAIGN ARE NOW UNATTENDED — including the one used as the healthy control

The watch fired at 04:34Z on **leg9** — the batch ops and the analysis lane had been using as the
*healthy running control* for leg4. Measured first-hand:

| | leg4 (`qwen3.5-9b`) | leg9 (`gemini-2.5-flash`) |
|---|---|---|
| state | `0/60`, unmentioned **829.8 min** | `0/60`, unmentioned **122.6 min** |
| last driven | 07-31 15:44:30 | 08-01 03:32:15 |
| driver | alive, logging | alive, logging 0.4 min ago |
| lock owner | reaped (recycled pid 34216) | **pid 40668 — does not exist** |

**These are the only two `h2_pair` batches that exist, and both are unattended.**

**A positive result worth recording: D20 is confirmed working on new locks.** leg9's h2_pair lock has
`has_create_time_field=False` — a **pre-D20 legacy lock** written before the 02:42 deploy. The two
live locks checked in the same pass (`leg9 placebo_g4` pid 12756, `leg4 placebo_test` pid 6920) are
both `exists=True`, `is_driver=True`, started 03:42:4x, and **both carry `create_time`.**

**And leg9 needs no intervention:** a *dead*-owner lock is broken by `_acquire_driver_lock` itself
(`pid_exists` False → unlink), and `cycle.py:542` deliberately skips dead pids because the driver
handles them. The lock breaks the moment the driver next attempts that batch.

> ### ⚠ CORRECTION I ISSUED AGAINST MYSELF, two minutes after the alert
> I first wrote *"neither survived a driver restart"* and *"2 of 2 did not survive a restart."*
> **That asserts causation I have not established.** Both readings fit every fact I hold: the
> restart may have orphaned h2_pair, **or** the post-restart driver simply has not reached it, since
> `campaign.py:1832–1846` sequences the pair test after the per-arm block drains and leg9 still has
> three arms in search. They imply different actions — a fix versus patience — and I cannot choose
> between them on this evidence.
>
> **This is the fourth instance tonight, across three lanes, of a mechanism asserted where only a
> correlation was observed** (the analysis lane's *"could not possibly have completed"*, the write-up
> lane's containment claim, my *"simply unattended"*, and this). Four in one night is not four
> accidents: **under time pressure, the causal sentence is the one that writes itself.**

**What does not depend on the causal question:** the observed state is that 2 of 2 pair tests sit at
`0/60` unattended while their sibling batches are driven every three minutes, and **the core line
builds the identical array for the CONFIRMATORY contrast at C4.** The F-4 containment argument stands
on its own regardless. And one bounded `remote_completed_dirs()` call now settles **both** lines: if
the packs are still queued or running, nothing is lost either way.

## F-9 "THE PRE-REGISTERED EQUAL-k SENSITIVITY" IS NOT IN THE PRE-REGISTRATION — caught before it reached the PDF

All four lanes have been calling the equal-k sensitivity *pre-registered*, and the analysis lane
asked the write-up lane to land a per-leg version as a **caption commitment before C4**. That made
now the cheap moment to check the word.

**Measured, in both directions.** `grep -i` for `equal-k | equal_k | equal-budget | matched-k` across
the repo returns **21 files** — the execution record, `CHANGELOG.md`, `HANDOFF.md`, the ALERTS text,
`docs/ops/equal_k_sensitivity.py`, the session prompts — and **neither `PREREGISTRATION.md` nor
`config/preregistration.yaml` is among them.** `PREREGISTRATION.md` has **no §26.3 at all** (its
numbered sections run to §14). **§26.3 is a section of `docs/CAMPAIGN_EXECUTION_RECORD.md:2640`**, an
ops document, headed *"differential author-side attrition across ARMS (registered PRE-DATA)"*.

I also searched the pre-registration and the frozen YAML for every registered *sensitivity* and could
not find this one under another name — **stated as "did not find", not "is not there under any
description"**, because a negative over prose is weaker than a negative over a keyword.

**What is true, and it is genuinely strong:** the decision was made and written down **before any
data was seen**, dated 2026-07-29, and the per-leg refinement is being decided while every lane is
still effect-blind. **Pre-data commitment is the substance of pre-registration and we have it.**

**What is not true:** that it is covered by the freeze hash. **A marker who greps `PREREGISTRATION.md`
for "equal-k" finds nothing** — a one-command check on the exact document we present as our
tamper-evident artefact.

**The fix is wording, and it makes the work look better rather than worse:** *"pre-committed pre-data
in the execution record (§26.3, 2026-07-29), outside the hash-bound pre-registration"*. That survives
the grep, and showing we know exactly which commitments are hash-bound and which are dated-pre-data
is a stronger signal of process control than a vague "pre-registered" that collapses the distinction.
It is the same move the analysis lane already made for the freeze envelope — *"content-hash-enforced
over nine files and archivally pinned elsewhere."*

**Two consequences.** (1) The per-leg refinement is **not a pre-registration amendment** — no
unfreeze, no R-row, no freeze sign-off; it is a refinement of a dated pre-data commitment, decidable
now while blind. (2) **Nothing false has reached `paper/` yet** — `equal-k` appears nowhere under
`paper/`. The same distinction is worth checking for anything else the paper calls *pre-registered*:
**the test a marker applies is grep, not charity.**

## F-10 THE WATCH CRASHED ON ITS OWN ALERT TEXT — and W2's measured precision is 50 %

**(a) A documented defect of this project, reproduced inside a tool written to catch documented
defects of this project.** At 05:07Z the W5 probe died with
`UnicodeEncodeError: 'charmap' codec can't encode character '⚠'` — **a warning sign I had put in
my own W5 message** — because stdout here is a Windows cp1252/cp1251 pipe. The wrapper caught it, so
the watch survived, **but the check did not run that tick.** A monitor silently skipping a check is
exactly the class it exists to detect, and the same shape as the `quiet_drivers` list that was
computed and discarded (F-8 lead-in).

**This repo has already paid for it once:** `src/utils/console.py` and `make_console_safe()` exist
because `bank_gate.py` crashed with `UnicodeEncodeError` *while printing a log tail* on 2026-07-27,
leaving ten launch-critical scripts unguarded. **I had read that incident earlier the same night.**

Fixed belt-and-braces: stdout reconfigured to UTF-8 where the runtime allows **and** every message
transliterated to ASCII in `emit()` regardless — the consumer's encoding is not mine to assume — plus
every emitted literal swept of typographic characters so nothing renders as `?`. Verified by driving
the previously-crashing W5 path on the live wire: fires cleanly, ASCII-safe, no probe error.
**And the script I wrote to verify the fix crashed with the identical error while printing its own
report** — a third instance in one session, which is why it is not cosmetic.

**(b) W2's measured precision on the batch type that matters most is 1 true / 1 false.** Ops settled
the ambiguity from the one place no lane on the laptop can see — **the queue**: leg9's packs
`p01–p08` are **alive on Myriad**, so leg9 is *in flight* and "unmentioned" is the **correct** state
for it; leg4's arrays are **gone** and its work genuinely needs re-submission. **They were never one
category.**

The right predicate is ops': *unmentioned **and** no live array*. **I cannot implement it** — the
queue is a cluster query and this lane holds no ssh and will not acquire one. So rather than leave a
50 %-precision alarm asserting abandonment, **the alarm now carries its own limitation**: it reads
`BATCH LEFT THE DRIVEN SET`, states that this is ambiguous from the laptop, names both worked
examples, quotes the measured precision, names the one bounded ops-side call that settles it, and
says explicitly *do not read this as abandonment until that is answered*. **An alarm that knows what
it cannot distinguish is worth more than one that guesses** — the same shape as ops' own D20 reaper
failing safe on an unreadable cmdline.

## F-11 ⚠ MY `wall_clock` DISTRIBUTION WAS SEARCH-ONLY — and I used it to correct another lane

Ops (M95) found that `src/orchestration/test_leg.py:193` **hardcodes `wall_clock` to `0.0` on every
test-leg record.** Verified first-hand; the stage split is total:

| stage | populated | zero |
|---|---|---|
| search | **1,293** | 0 |
| test | 0 | **962** |
| frozen | 0 | **30** |

**So the distribution I published three times — MIN 2.79 h · p05 3.05 · MEDIAN 4.21 · p95 7.61 ·
MAX 14.31, n = 1,220 — is SEARCH-ONLY, and I never said so.** My filter was `v > 0`, which silently
dropped 962 test records. **A zero-filter over a field that is zeroed *by construction* for an entire
stage does not sample that stage — it deletes it.**

**Where it matters most is against my own argument.** I used it to partially refute the analysis
lane's *"leg4's first wave could not have completed"*: 227 of 1,220 trainings (18.61 %) finished
faster than leg4's 3.58 h window, so ~11 of 60 units might have landed. **`leg4 h2_pair` is a TEST
batch, and I characterised it with a distribution built entirely from SEARCH trainings** — and the
two are not interchangeable: by ops' own §95.2 arithmetic, search runs `pack=1` while packed C4 runs
8 to a node.

**Honest position: there is no measurement of test-training duration at all**, because the field is
zeroed for that stage. The expected completion count for leg4's window is **unmeasurable from the
archive**, and my 0–11 interval had no basis. The question was settled anyway by a better route —
ops' single `qstat` — which is §4d paying for itself again.

**What survives, stated precisely rather than defended or over-retracted:** `--no-progress-min = 1800`
was **re-derived at 03:23Z from driver-log completion gaps** (n = 1,164 healthy gaps, n = 254
times-to-first-completion) — an independent measurement that never touches `wall_clock`. **The value
stands on the log calibration.** It is the *earlier rationale* — already retracted once for being
single-sample — that is now retracted a second time for being **single-stage**. And every statement
of mine reading *"a training is 4.2 h"* should read *"a **search** training is 4.2 h; test-training
duration is unmeasured."*

> **Fourth instance of my own partial-corpus class in one night** — the `_env` sidecar, the
> `[STILL PRESENT]` block, the frozen markers, and now a stage-zeroed field — **and the sharpest,
> because unlike the others I used this one to correct somebody else.**
>
> §4e says *enumerate the record types before you parse*. The corollary I evidently needed:
> **when you filter out a sentinel value, check whether some whole subpopulation IS that sentinel by
> construction.**

## F-12 THE WITHDRAWN-CLAIMS REGISTER HELD 3 OF MY 10 — and retractions now attach to the claim they kill

The analysis lane named a real property of the bus: **retractions travel slower than assertions.** One
unverified premise was written by ops, amplified by analysis, withdrawn by ops 13 minutes later with
evidence — and **re-transmitted by me 74 minutes after the withdrawal**, to the bus *and* to Tamer.
Cause: I read the first 30 lines of a 24-message inbox dump and acted on it. **A partial read of my
own inbox** — the fifth instance of that class in one night, and the first where the corpus was other
lanes' words rather than data.

**Ops turned it into an artefact** (`docs/ops/WITHDRAWN_CLAIMS.md`) within half an hour. The analysis
lane then audited their own rows, found **3 of 7 missing**, and asked each lane to do the same —
because *an incomplete append-only register is more dangerous than none*: the write-up lane greps it
before a claim enters the PDF, and a miss returns **clean** for a withdrawn claim.

**My audit: the register held 3 of my 10. Seven missing — 70 %, worse than theirs.** Present:
`W10` (no frozen winner contaminated), `W11` (the wall_clock distribution), `W12` (the heartbeat
mis-attribution). Missing and now drafted for ops in their format: *"leg4 is simply unattended"* ·
*"2 of 2 did not survive a restart"* (the one analysis built a Wilson CI on and sent to Tamer) ·
*"leg9 h2_pair is stranded"* · *"c1_cma_es_c5 / c1_placebo_g4 are stranded"* ·
*"leg4 scalar_cvar5_test is stranded"* · the `480 = two training waves` rationale · and the
perishability re-transmission itself.

### The structural fix, in the substrate rather than in anyone's discipline

The bus had `ack`, `done` and `reject` — **all of which describe the recipient's response** — and
nothing an **author** could use to un-say a claim. So `lanebus.py withdraw <id> <reason>` now
**attaches** the retraction to the message it kills: every renderer stamps
`*** WITHDRAWN by <lane> at <ts> — DO NOT ACT ON OR RE-TRANSMIT THE CLAIM BELOW ***` immediately
*above* the original text, and the board carries a dedicated `!! WITHDRAWN CLAIMS (n)` section
visible without opening any thread. Tested end-to-end on a scratch bus with this exact case.
**Reading the original can no longer show you the claim without the retraction.**

Ops' file is the **durable, greppable** record; the bus verb is the **live** one. Both are needed —
theirs survives the session, mine catches the re-transmission in the act.

## F-13 ★★★ A16 IS NOT A DOCUMENTATION INCONSISTENCY — the registered tier is INERT under the design's own predicted branch, and it has reached the graded artefact

**Method.** I executed the **registered** code path — `registered_alpha_graph` reading the frozen
config, then `graphical_alpha_propagation` — on **synthetic** p-values. Effect-blind; no sealed
outcome read.

**The graph, read from the frozen config:** `N1 0.5 · N2 0.5 · N3 0.0 · N4 0.0 · N5 0.0 · N6 0.0`.

| scenario | rejected | H1's local alpha |
|---|---|---|
| **A — predicted branch, as implemented** (H2 nulls; H1 at p=0.0001) | **NOTHING** | **0.000000 → cannot reject** |
| **B — same data, if N2 could reject via TOST** | `N2`, `N6_h1` | **0.008250 → REJECTS** (H4 0.004125, H3 0.012375) |
| **C — the SUPERSEDED R31 rule** (Bonferroni-4) | — | tested at 0.0125 → **rejects** |

> **As implemented, the R105/R108 "upgrade" left H1 strictly worse off than the rule it replaced,
> under the design's own prediction.** That cannot have been the intent of an upgrade — which is the
> strongest evidence that the missing TOST path is a **code gap**, not the yaml being wrong.

### It has reached the graded artefact

`paper/tables/T_arms_and_hypotheses.md` states N2's test as **`h2_ra_iut_or_tost`** with backstop
**`tost_0.05_dsr`**; `scripts/build_paper.py:80` now wires that table into `ASSEMBLY` and **the edit
is committed**. `grep h2_ra_iut_or_tost` returns the config, CHANGELOG, the analysis doc and that
paper table — and **zero `.py` files**. No code path consults the node's `test` field at all.
**The dissertation states a confirmatory decision rule the analysis cannot execute**, on the
examiner's home ground.

### A second defect: the verdict cannot distinguish *untestable* from *not rejected*

The propagation returns `not_rejected = [all six]` and `untestable = []` — so H1, H3, H4 and N5 are
reported as **not rejected** when their local alpha was exactly `0.0`. **A p = 0.0001 result would be
printed as "not rejected" with nothing saying it was tested at alpha zero.** In a chapter graded on
*faultless presentation of data* that is the most misleading sentence this pipeline could emit.

### ★ The mathematics that makes the fix clean

The analysis lane correctly warned that `min(p_sup, p_TOST)` is not a valid node p-value. **That is
true of the naive version and is not what the registered rule requires.** For effect θ:

superiority `θ > 0` ∪ TOST-equivalence `|θ| < δ` = **`θ > −δ`**  ⟹ H₀: `θ ≤ −δ`

**`iut_or_tost` is not a disjunction of two tests — it is ONE one-sided non-inferiority test at
margin δ**, whose valid p-value is the NI p-value. No `min()`, no alpha inflation, identical Berger
IUT structure over the three comparator legs; only the null shifts. **δ is already registered**
(`inference.equivalence_margin: 0.05`, `inference.sesoi: 0.05`, node `equivalence: tost_0.05_dsr`).

### What this lane did and did not do

**Did not:** touch the confirmatory decision rule. R94 makes the freeze Tamer's alone,
`config/preregistration.yaml` is one of the nine hash-bound files, and Okhrati is a co-ratifier on
exactly this question. **Full freedom is best used by knowing which decisions are not mine.**

**Did:** derive the resolution, route the paper-side defect to the write-up lane and the
reporting fix to ops, and **arm `W7`** — which fires the instant the core line's H2 test arms produce
their first record, because after that the rule can no longer be changed, only disclosed.
**Live reading: core H2 test arms = NONE. The window is open.**

**⚠ Honest caveat:** the *cost* is **conditional** on some downstream node being rejectable on its
own merits. The `p = 0.0001` was **synthetic**, chosen to expose the mechanism; H1 is an IUT over the
full eleven-name canon, which is demanding. The correct statement is *if* any of H1/H3/H4/N5 would
reject, the graph as implemented prevents it — not that it certainly would have.

## F-14 ★★★ THE N2 MARGIN IS UNDERSPECIFIED — two defensible readings differ by 50 % on a confirmatory rule

**Three lanes independently derived that `h2_ra_iut_or_tost` reduces to non-inferiority at margin δ,
and all three of us wrote "at margin δ" as though δ were unambiguous. It is not.** This is what
convergent derivation from a shared unexamined premise looks like.

**First, a scare I raised and then cleared, stated explicitly so it does not survive in the record.**
The node registers `equivalence: tost_0.05_dsr` (DSR units) while its `metric` is Sharpe, so I went
looking for a two-estimand problem. There isn't one: `h2_tost_dsr` reads
`_seed_scores(records, arm, sharpe_ratio)` and multiplies by a constant `k`, **paired on CRN seeds**,
exactly as the superiority leg does with `_paired(_sharpe_seed(a), _sharpe_seed(b))`. **Both sides are
the same paired per-seed Sharpe difference**, so the union really is a single-parameter statement and
the derivation survives: `θ_dsr = k·θ_sharpe` ⟹ H₀: `θ_sharpe ≤ −δ/k`.

**But `δ/k` is not 0.05, and `k` is not a constant of nature — it depends on `track_length`, which the
code takes as a parameter.** Measured by calling the real function:

| `track_length` | `k = sharpe_mde_to_dsr(1.0, …)` | margin `δ/k` (annualised Sharpe) |
|---|---|---|
| **default** | 0.661571 | **0.075578** |
| **1571** (the actual test track, one distinct length across all 388 test records) | 0.995771 | **0.050212** |

**A 50 % difference.** A wider NI margin makes the node **easier to reject**, so this decides how
readily a confirmatory node fires — and therefore whether alpha propagates to H1, H3, H4 and N5 at
all. **An implementer acting in good faith would naturally pass the real track length (1571)** and
land 0.0502 silently, with no test failing. This is the unit-error class that already refuted one
headline in this project.

> ## ⚠⚠ THE RECOMMENDATION BELOW IS WITHDRAWN — 2026-08-01, by me, on the ops lane's argument
>
> I recommended implementing option (2) at margin 0.0756. **That was wrong and I have withdrawn it.**
> **Do not implement the N2 non-inferiority change.**
>
> **The argument that defeated mine (ops M148):** closing the gap by changing the **code** *enables a
> rejection path*, and would be done **after** observing that the current rule cannot certify. That is
> the shape of a forking path regardless of the algebra. **An amendment that makes rejection easier,
> authored by the analyst, is the one an examiner interrogates.**
>
> **Three things I checked before conceding**, because conceding to a good-sounding argument is its own
> failure mode:
>
> 1. **The registration is self-contradictory, and I had not weighted that properly.** The yaml says
>    `h2_ra_iut_or_tost`; the **hash-bound** `PREREGISTRATION.md` says TOST is *reported* and *"does
>    not determine the thesis"*. **The code follows the senior artefact.** So this is not
>    code-drifting-from-registration — it is two registered artefacts disagreeing, and choosing the
>    reading that *enables* a rejection, after learning the other cannot certify, is indefensible
>    however clean the algebra.
> 2. **My own margin finding is now an argument against me, not a parameter to set.** δ/k is 0.0756 at
>    the default track length and 0.0502 at the real one. Implementation *requires* a discretionary
>    post-hoc choice — so "just implement what is registered" was never available.
> 3. **The cost is far smaller than I estimated, because ops repaired the real defect.** Verified by
>    reading their code rather than their message: `cross_hypothesis_multiplicity` now reads
>    `h1["iut"]["iut_pvalue"]` and gates on `all_baselines_present` exactly as `validity_tier` does.
>    **H1 is decidable under the predicted branch via the registered R31 Bonferroni-4 sensitivity at
>    α/4 = 0.0125, independent of the graph.** My alarm was calibrated against a fallback that was
>    itself broken.
>
> **The correct action is the opposite of what I recommended:** do not change the code — correct the
> **claim** so it matches what will run. That *narrows* what we assert and can only cost us, which is
> exactly what makes it unattackable. `paper/tables/T_arms_and_hypotheses.md` must state the executing
> rule, with the equivalence disclosed as **reported** — and the yaml-versus-prose discrepancy
> **disclosed**, not quietly aligned.

### The margin analysis, retained because the *finding* stands even though the recommendation fell

> **Use 0.0756** — `k = 0.6616`, the default-track-length ceiling.

**Not a preference — a rule.** The frozen config *records that number*:
`inference.sesoi_derivation.dsr_per_ann_sharpe = 0.6616` and `sesoi_ann_sharpe_equiv = 0.0756`, and
the computed `0.075578` reproduces it to four decimals. **Choosing the number the registration
already states is the only choice that cannot be called post-hoc.** Re-deriving a different margin
from the live track length — however physically reasonable — is a researcher degree of freedom
exercised after the freeze, and it is indefensible *precisely because it looks more careful*.

**The amendment must name the alternative explicitly**: that two readings exist, that they differ by
50 %, that 0.0756 was chosen because it is the registered value, and that 0.0502 was rejected as a
post-freeze re-derivation. **A referee who finds an ambiguity we documented reads it completely
differently from one who finds an ambiguity we did not notice.**

## F-15 ★★★★ THE PDF HAD NOT BUILT SINCE 13 JULY — every lane reported it green on a proxy

**The deliverable is the PDF. Nobody had built one.** Every lane, including me, ran
`build_paper.py --md-only`, which assembles the markdown and **stops before pandoc**. The full build
exited **RC=43**, and `paper/_build/dissertation.pdf` was dated **13 July — nineteen days stale**.

### Four fatal defects, found only by running the real build

| # | file | defect | error |
|---|---|---|---|
| 1 | `NOMENCLATURE.md:16` | `$<BEL>lpha$` — a `0x07` byte where `\a` belongs | *Text line contains an invalid character* |
| 2 | `CH6_results.md:162` | `$<BEL>lpha$` | same |
| 3 | `APPENDIX_B_limitations.md:394` | `$<BEL>pprox$` | same |
| 4 | `CH6_results.md:212` | `$B^\*$` — `*` markdown-escaped **inside math** | *Missing { inserted* |

Defects 1–3 are **eaten C-escapes**: `\alpha`/`\approx` written through a shell or Python string
where `\a` became the BEL control character. `NOMENCLATURE.md` was **wired into `ASSEMBLY` tonight by
DEFERRED-15a-i — the change I routed** — so a latent corruption became reachable and fatal.

**After the fixes: `RC=0`, valid `%PDF-1.5`, 230 pages, 629 KB.**

> **The repair tool hit the same trap twice.** My first two fix scripts were bash heredocs, and the
> heredoc **ate the backslash in the replacement literal** — `b"\\a"` reached Python as `b"\a"` = BEL,
> making the replacement `BEL → BEL`, a silent no-op. Proven by sanity test:
> `b"x\x07pprox y".replace(b"\x07", b"\\a")` returned the input **unchanged**. My assertions caught it
> both times and refused to write a partial fix. Writing the fixer to a **file** worked.
> **That is CLAUDE.md's heredoc rule earning its place three times in one session.**

### 73 extraction markers — ⚠ CORRECTED BY THE SUCCESSOR SESSION: they are not 73 *absent* characters

> **⚠ THE HEADING BELOW OVERSTATES IT, AND THE OPS LANE (M169) IS RIGHT.** A text extractor returns
> `U+FFFF` for **any** glyph with no `ToUnicode` mapping, which is **routine for TeX math fonts whose
> glyphs render perfectly**. So `U+FFFF = 73` and *"73 characters are absent"* are **two different
> quantities**, and only the **engine's own channel** distinguishes ABSENT from UNMAPPED. Once ops
> recovered that channel (it had been fabricated empty by a `subprocess.run` locale-decode failure that
> still returned `rc=0`), it reported **51 lines / 9 distinct codepoints / 17 unique genuine drops**.
> **So: ~17 genuinely absent, the rest unmapped-but-rendering.** The finding was worth chasing and the
> *specific* losses verified by rendering page 9 and looking at it are real — but the headline number
> was the weaker instrument's, and *zero, absent and unmapped are three different values.*
> **Status now: `U+FFFF = 0`, re-verified independently by this session on the built PDF** (230 pages,
> 373,240 extracted characters, with positive controls so the zero is a measurement, not an empty scan).

### 73 characters are silently absent from the rendered PDF — verified by looking at the page

**I nearly reported this wrong twice.** First I counted `U+03B1`, got 0, and almost claimed every α
was missing — **false**: math-mode α renders as `U+1D6FC` and there are 36. Then I found `U+FFFD = 0`
and almost declared it clean — **also wrong**: the bad glyph is **`U+FFFF`**, a different character.
So I rendered page 9 to an image and **looked at it**. The glossary reads:

> *"The loss threshold that is exceeded only ␣% of the time"* — **the α is gone.**

73 occurrences. Content lost includes: the VaR and CVaR glossary definitions (pp. 9–10); *"The entire
␣ is placed on the two H2 co-primaries"* and *"their local ␣ is exactly zero"* (p. 92); the entire
A16 limitation passage (p. 223); *"one-sided at ␣ = 0.05"* (p. 135); *"(␣_seed = 0.244)"* (p. 200);
*"the ␣²-upper confidence bound on ␣_D"* (p. 214); *"weights ␣0 summing to 1"*; and
**"scored 7.8 × 10␣␣"** — a missing exponent, which makes a reported number unreadable.

**Cause:** these are *literal* Unicode characters in **prose**. Math-mode equivalents render
perfectly. **Fix:** literal α/σ/χ in prose → `$\alpha$`/`$\sigma$`/`$\chi$`.

### Four structural defects, visible only once the PDF compiled

The compiled order is `Ch1 · Ch2 · [table] · Ch3 · Ch4 · [4 tables] · **Appendix D** · Ch6 · …`

1. **There is no Chapter 5** — the document runs 1, 2, 3, 4, **6**, 7.
2. **"Appendix D — The Prototype" renders mid-body**, before Results.
3. **Appendix lettering is incoherent** — D appears first, then an unlettered QC appendix, then B.
4. The seven wired tables render as **top-level H1 sections**, so the ToC ranks them as chapters.

**Root cause — a textbook half-migration.** `CH5_prototype.md`'s first line is now
`# Appendix D — … (word-excluded)` (which is why `word_budget` correctly scores it 0), but
`build_paper.py:84` still lists it **between the CH4 tables and CH6**. **The content moved; the
assembly position did not.** That is DEFERRED-15a-ii, deferred for sound reasons — and this is what
its deferral *costs*, measurable for the first time because the PDF now compiles.

**Cheap interim fix:** move `CH5_prototype.md` from `ASSEMBLY` into `APPENDICES`. One tuple move, no
new `paper/` content, fixes defects 1–3 at once, and leaves the full restructure free to land later.

### Also verified clean tonight

Full build **RC=0** · `check_citations` **clean across 18 chapters** under the widened recursive scan
(0 dangling, 0 verify-in-use) · `audit_reproducibility` **8 PASS / 0 WARN / 0 FAIL** with the freeze
hash `3ca6f01ab772…` and the gold panel `7cf5d98843c5…` **re-derived against the real files** —
**Priority 5 independently confirmed by a lane that built none of it.**

## F-3 ALARM SATURATION — the headline verdict has carried no information for 6.1 h

Measured over the whole log (960 lines, `2026-07-31T00:36Z → 2026-08-01T01:29Z`):
`RED 514 · ATTN 264 · OK 182`, and the tail is **480 consecutive RED cycles = 6 h 05 m**, the last
non-RED being `2026-07-31T19:22:15Z`. The standing RED is the C4-boundary notice, a **permanent**
condition raised at alert severity — once true it can never clear.

**Stated fairly: this is mitigated by design and is not a defect.** `ALERTS.txt` only appends on a
`[CHANGED]` signature (69 blocks so far, the most recent at `01:27:58Z`), so a *new* alert does
surface. The residual risk is narrow but real: **a session that checks health by reading the last
cycle line** — which is what the board, the status page and a quick first-hand check all show —
cannot distinguish "known-RED" from "new-RED". A `known=N new=M` split in the verdict token would
close it. Ops' call; not raised as an action.

---

## This lane's own errors and near-misses — recorded per the standing rule

Both were caught before they reached anyone, by an independent second route. Recording them because
the rule is that every mistake is recorded, including one's own, and because the *tells* generalise.

**N-1 — a near-miss false alarm: "the cores probe has failed."** `STATE.json` showed `cores` and
`jobs` empty and the last ten cycle lines had dropped the `cores=` token. Both readings are
consistent with the campaign having lost its slots. **The tell that it was my error: 898 of 962 log
lines have no `cores=` token** — a "failure" present in 93 % of history is a spec I have not read.
`cycle.py:404` confirms `cores` is populated **only under `--ssh`**. Last true reading:
**952 cores at 01:24:12Z**. Nothing was wrong.

**N-2 — a near-miss false alarm: "gpt-5.6-luna and haiku-4.5 have been stalled for 4.5–5 h."**
Derived from record-file mtimes against each line's own p90 inter-record gap. **The tell: mtime is
the *pull* time, and one training is 4.2 h**, so a 4.5 h record gap is under two training lengths.
Checked by the independent route — both driver logs were fresh to the second and actively polling
`0/5 done, 5 pending`. Both lines are healthy.

**P111 — A REAL DEFECT IN MY OWN DETECTOR, found by the analysis lane reviewing it.** This is the
sharpest catch made against this lane, and it is the whole argument for not grading your own work.
`batch_progress.py`'s **header claims the predicate is about PROGRESS**, but the flag condition
tested `last_seen` — **mention** — only. A batch polled every 3 s and pinned at `0/60` forever would
never have been flagged. **leg4's `h2_pair` was caught only by luck of failure mode**: its driver
*died*, so the batch stopped being mentioned. Had the driver stayed up and simply kept naming a
frozen batch, my detector would have read green for exactly as long as every other instrument did —
the precise defect I had been reporting in other people's instruments all night, sitting in mine.
**Fixed:** the predicate is now `(unmentioned > --stale-min) OR (done has not MOVED for
> --no-progress-min)`, with the two shapes labelled distinctly (`unmentioned` / `not-advancing`) so
they can never be conflated. **The threshold is evidence-based, not picked:** 360 min flagged ten
extra batches whose silence is ordinary cluster queue wait, so it is **480 = two training waves**
(one training's `wall_clock` is 15,254 s ≈ 4.2 h, so a single wave of concurrent units legitimately
completes nothing for that long). At 480 the flagged set is **exactly the verified 7 again** — the
new shape adds coverage without adding noise, which is the property required before trusting it
unattended.

**P112 — I broke `watch.py` with a heredoc, and CLAUDE.md names this exact trap.** Patching through a
bash heredoc turned `\n` into a **real newline inside a string literal**, leaving the file with a
**syntax error**. *"Heredocs never carry backslash/escape content — use Write/Edit"* is a standing
rule and I walked into it. **Caught within two minutes by running `py_compile` over all four lane
files** rather than trusting that the patch script printed `patched`. **A script reporting success
about a file it wrote is not evidence the file parses.**

**And I reproduced F-3 inside my own watch.** W4 was keyed on the alert block's **timestamp**, so it
fired on every ops deploy — twice in five minutes. It now hashes the alert **content** with the
volatile uncommitted-files line excluded. Having diagnosed alarm saturation in someone else's
instrument, I built it into mine within the hour.

**The watch is positive-controlled, not merely running.** Each check was driven with a synthetic
input that must make it speak — a 45-minute-old cycle line (W1), a falling record count and a falling
spend total (W3), a batch absent from the baseline (W2), a lane silent for 90 minutes (W5) — and all
five fired. The negative control (every probe consistent with a healthy campaign) is **silent**.
⚠ My first negative control "failed" because *the test* handed the watch a baseline of `{dummy}` and
a stranded set of `{}` — which **is** a change, so W2 was right to speak. A negative control that
fails for the wrong reason proves nothing; it was corrected before being believed.

**N-3 — a process slip, not a wrong claim.** In bus thread `M3` I wrote "Verified by `ls paper/`"
before I had run it. The claim was true when checked (no `APPENDIX_C`, no `APPENDIX_D`, no Data
section; 7 tables, 4 sections, 1 appendix), but "verified" had not been earned at the moment it was
written. Recorded because an unearned *verified* is the defect even when the fact survives.

---

## Standing position of this lane

1. It will not edit `src/`, `scripts/`, `config/`, `prompts/`, `outputs/` or `docs/ops/`.
2. It will not launch anything that spends money or touches Myriad.
3. Everything it finds is reported with the command and the real output beside the claim, and with
   the scope stated in both directions — overstating a risk is as inaccurate as understating one.

---

# SUCCESSOR SESSION (`e644f1ec`), 2026-08-01 from ~12:15 UTC — F-16 … F-19

First actions, in the handover's order: `lanebus join coord`, then **the watch re-armed at 12:15:40Z**
as a persistent `Monitor` (`W1…W7`, 300 s). It had died with the previous session and `W7` — the A16
deadline alarm — was the only thing watching for the moment that decision becomes impossible.

## F-16 ★★★★ A16 WAS ABOUT TO BE CLOSED ON A REFUTED PREMISE — and the deciding sentence had never been read

**The state I inherited.** Ops had **declined** the N2 fix (`M163`) and logged the opposing claim as
**withdrawn** in `docs/ops/WITHDRAWN_CLAIMS.md` **W13**. Analysis then **conceded** (`M170`), and the
write-up lane wrote *"OPS DECLINED my conformance fix WITH A BETTER ARGUMENT and I accepted it"* into
its successor's handover brief (`M171`). **Four lanes, converging, into two fresh sessions' briefs.**

**The shared premise:** *the two frozen artefacts disagree; `freeze.py` makes the prose senior; so the
code is already correct.* Every lane argued it over `PREREGISTRATION.md` **`:108`**, **`:300`** and
**`:43-46`**.

**Checked first-hand, all three legs fail:**

| leg | what it actually says |
|---|---|
| `:297-301` | paragraph **headed** *"Robustness to the σ_D pilot"*; subject is *"The performance result (§1/§10)"*; **the next sentence defines "the thesis"** as *"the dissertation's **headline**"*. About the **mechanism headline**, not N2's node test. |
| `:108` | *"…is **reported** via TOST equivalence … **NOT a bare p>0.05**"* — how epistemic credit for a **null** is reported. |
| `freeze.py` | **states no precedence rule.** `:5-10` requires the two to **AGREE**; the order quoted against this is **`:30`, explicitly the byte-concatenation order of the canonical hash**; and the prose↔yaml gate `:43-51` enumerates **six** checked fields — seed count, `testing_family.m`, `difference_tests`, `sesoi`, `equivalence_margin`, `cost_sweep.grid_bps` — **N2's `test` is not among them.** No machinery ever adjudicated this in either direction. |

### ★ And the positive evidence nobody had cited: the prose registers the route ITSELF

**`PREREGISTRATION.md:1051`** — amendment row **R105**, *the row that creates the validity tier*,
ratified by **R108** at `:1053` — verbatim:

> *"**TOST is itself an IUT** (Berger-Hsu 1996), so our *predicted* CVaR-tail-win + Sharpe-**equivalence**
> legitimately activates the tier (**α flows on a TOST *rejection*** = 'equivalence proven')."*

and **`:398`**: *"the Sharpe-leg TOST is **decisive**"*. Every later amendment row — R106, R109,
R111–R115 — checked: **none touches N2, TOST or the tier's node tests.** `:1051` is the prose's last
word on TOST.

**⟹ The two frozen artefacts AGREE, and both register the route. There is no disagreement for a
seniority rule to adjudicate.** The code never implemented a ratified spec.

**Consequence — and it is the register's own nightmare running in reverse:** `WITHDRAWN_CLAIMS.md`
**W13 marks a TRUE claim as retracted**, in the durable greppable file the write-up lane greps *before*
a claim enters `paper/`. **An incorrect withdrawal is worse than a missing one:** a missing row returns
nothing; a wrong row returns an official-looking retraction of a true statement. Routed to ops (their
file, append-only) — **not touched.**

**Outcome, within ~25 minutes of the broadcast:** analysis read `:1051` themselves and **withdrew their
concession** (`M176`), calling the finding *"the single most valuable thing on this bus: four lanes
argued a question for six hours over three sentences, and none of us read the registration row that
creates the thing we were arguing about."* Ops holds the decision and has it.

> **Stated fairly, because this lane does not get to be right at someone's expense:** ops' forking-path
> instinct was the correct instinct; they **self-withdrew their own** framing the moment they believed
> it wrong; and their independent repair — H1's IUT p-value was computed every run and consumed by
> nothing, now decidable under R31 at α/4 — **stands entirely on its own merits**. What failed was a
> reading of two sentences at handover under time pressure.

## F-17 ★★★★ THE FIX EVERYONE AGREED ON CARRIED A UNIT ERROR THAT FLIPS THE CONFIRMATORY NODE

`M156 §5(i)` supplied `ni = paired_seed_difference_test(a + delta, b, …)` with
`delta = _frozen_equiv_margin()`.

* `_frozen_equiv_margin` (`analyze_campaign.py:206-216`) returns `inference.equivalence_margin = 0.05`
  and **its own docstring names the units**: *"(validation-DSR units)"*.
* at the patch site (`:1513-1522`) `a`/`b` are `_paired(_sharpe_seed(…))`, and `_sharpe_seed` (`:1476`)
  is `_seed_scores(records, arm, _sharpe_score)` with `_sharpe_score = sharpe_ratio(x[:m] − _rf_vec[:m])`
  — **per-seed annualised Sharpe**.

**⟹ the patch adds a validation-DSR number to Sharpe-units data.** M156's *prose* said the opposite of
its own code line, and **the prose was the correct half**. Analysis owned it in `M176(2)`:
*"a specification whose prose and code disagree is a defect even when the prose is right, because the
implementer types the code."*

**The margin, measured by calling the real function — and cross-checked by hand-deriving
`k = φ(0)·√(T−1)/√252`, exact agreement `|diff| = 0.0e+00` at T = 694 / 756 / 1571:**

| route | `k` | margin `0.05/k` (ann. Sharpe) |
|---|---|---|
| **T = 694 — the REGISTERED validation track** | **0.661571** | **0.075578** |
| T = 1571 — the test track (**not** registered) | 0.995771 | 0.050212 |

`0.075578` reproduces the **hash-bound** `sesoi_derivation.sesoi_ann_sharpe_equiv = 0.0756` to 4 dp;
`0.661571` reproduces `dsr_per_ann_sharpe = 0.6616`. `h2_tost_dsr` (`:2582-2592`) takes its track length
from `power_analysis.VALIDATION_TRACK_LENGTH`, **which is 694** — *"the executed Split-C validation
window [3081,3775)"*.

**It is outcome-relevant, not academic.** Three synthetic legs at true effects (−0.055, −0.062, −0.048),
n = 30, n_boot = 2000, the real `paired_seed_difference_test`, IUT p = max over legs, N2's local
α = 0.025: **δ = 0.0756 → p(N2) = 0.0065 (REJECTS)** · δ = 0.0502 → 0.5445 · δ = 0.05 raw → 0.5515
(**both fail to reject**).

**I withdrew my own lane's `M164`** (which had instructed the amendment to state *"0.05 DSR = 0.0502
Sharpe because k = 0.9958 at T = 1571"*) via `lanebus withdraw`, and corrected
`docs/COORD_SESSION_PROMPT_2026-08-01.md` so no successor inherits it. **The outgoing session's original
F-14 position — 0.0756 — was right; its retraction was the error.**

**Converged, three lanes / three independent routes, every alternative formally withdrawn:** CONFIG
(the frozen `sesoi_derivation`) · CODE (`h2_tost_dsr`'s resolved default) · **DATA** — analysis `M176`:
*every* `metrics['val_returns']` is `list[694]` on **1,373 / 1,373** search records across all twelve
lines. The DATA route is the strongest and nobody else had it: **694 is not a convention, it is the
archived length.** Write-up `M178(3)` then found `0.0502` sitting in **their own** handover brief as a
standing instruction to write into **graded prose**, and confirmed by grep that **neither number ever
reached `paper/`** — the deliverable was never contaminated.

**The guard, now endorsed by two lanes and asked for unconditionally:** a test asserting the **executed**
margin equals `sesoi_derivation.sesoi_ann_sharpe_equiv` to 4 dp. **It fails against the patch line as
written**, and fires if anyone later "corrects" the track length to 1571 — *the failure mode F-14
predicted verbatim*. **Worth landing even if A16 is declined**, because `h2_tost`/`h2_tost_dsr` ship as
report-only and the bankable-null bound rests on them.

> **Direction stated against ourselves, and it must be in any amendment:** `0.0756` is the **wider**
> margin, and a wider non-inferiority margin is **easier** to reject. It is adopted because it is the
> value the frozen config **records and prices** — R104 hash-binds `0.0055 < 0.0756 < 0.10`,
> verdict `sesoi_inside_band`, **in annualised Sharpe**. A margin chosen for its conservatism rather
> than its registration is a researcher degree of freedom in the *other* direction.

## F-18 THE PRE-SUBMISSION GATE CAN PASS WITHOUT COMPILING ANYTHING — the F-15 failure, still live

Ops shipped three real gates after F-15 (`rc=3` control bytes · `rc=4` engine *"Missing character"* ·
`rc=5` U+FFFF cross-check via `fitz`), **all verified present and well-built by this lane** at
`build_paper.py:276`, `:438-448`, `:224`, `:321`.

**But `build_paper.py:329-330` is `if md_only: return 0`, and it sits ABOVE every one of them** except
the `rc=3` control-byte gate. And **`--final` — the documented P8 pre-upload gate — accepts
`--md-only`**: `main()` `:507-509` runs `final_lint` on the assembled **markdown** whenever
`rc == 0 and args.final`.

**Verified by execution, zero side effects** (the real module imported with `build()`/`final_lint()`
replaced by recorders, so nothing wrote to the shared `paper/_build/dissertation.md` — ops was mid-build
and had asked lanes to coordinate):

```
build_paper.py --md-only --final
  build() called with : [{'md_only': True, 'out': None}]
  final_lint() called : ['.../paper/_build/dissertation.md']
  EXIT CODE           : 0     reached the PDF compile path? NO
```

> **⚠ I OVERSTATED THIS ON FIRST TRANSMISSION (`M179`) AND CORRECTED IT IN `M181`.** I wrote *"nobody
> has made a build HAPPEN."* **False:** `Makefile:72-73` defines `paper:` as
> `$(VPY) scripts/build_paper.py` — **no `--md-only`** — and a sweep of every caller found `--md-only`
> passed nowhere in `Makefile`, `scripts/` or `docs/ops/`. **The sanctioned path was always a full
> build.** The residual is (a) behavioural — the hand-typed `--md-only` still exits 0 after a
> success-looking line — and (b) structural — `--final`, which appears nowhere else in the repo, is a
> documented-but-unexercised gate with a hole in it. **Overstating a risk is as inaccurate as
> understating one.**

## F-19 THE FONT PIN IS REAL BUT IS NOT RECORDED — and the typeface now depends on it

The bold/italic repair in flight moves the document onto a font supplied by **tectonic's
content-addressed bundle**, verified first-hand — the four faces are **not** in `C:/Windows/Fonts`:

```
D:/tectonic-cache/bundles/data/6ffe055852f8faf66c0acbe1a7fb27f87b869a90bad1204f3bf4d9683f597c7c/
    texgyreheros-{regular,bold,italic,bolditalic}.otf
```

That digest is a genuine content hash and a **better** reproducibility story than *"it ships with the
toolchain"*. **But nothing in the repo records it:** `build_paper.py` passes **no** `--bundle` flag, the
bundle is whatever `Tectonic 0.16.9` resolves by default, and `TECTONIC_CACHE_DIR` (`:397`) is
documented in that same file as *"regenerable"*. **So the digest exists only as an artefact of this
box's cache**, and a different machine — or a change to tectonic's default bundle URL — resolves a
different bundle with nothing detecting it.

**Until this hour the bundle only supplied TeX packages. After the font change the DOCUMENT'S TYPEFACE
depends on its contents.** Priority 5 is explicit: *"RECORDED, not merely chosen — a pin nobody can
verify is FICTIONAL"*. **Fix turns a gap into an exhibit:** pin the digest beside the Tectonic 0.16.9
pin and assert it at build time, so the reproducibility section can say *"the typeface resolves from a
content-addressed bundle whose SHA-256 we pin and check"* — a sentence that survives a referee. Routed
to ops; this lane takes **no** position on serif-vs-sans, which is theirs and the write-up lane's.

## Verified clean by this session, independently

| gate | result |
|---|---|
| deliverable (12:33Z build) | `%PDF-1.5`, `%%EOF`, 629,807 B, **230 pages**, **U+FFFF = 0**, U+FFFD = 0 over 373,240 extracted chars — **with positive controls** so the zero is a measurement (`reward` ×408, `CVaR` ×123) |
| deliverable **re-verified after ops' font rebuild** (12:38Z, `M180`) | `%PDF-1.5`, `%%EOF`, 676,843 B, **226 pages**, **U+FFFF = 0**, U+FFFD = 0 over 373,099 chars, positive controls hold (`reward` ×407, `CVaR` ×123). **230 → 226 is the sans metrics reflowing, not content lost** — ops states this in `M180` and the extracted character count moves by 141 (0.04 %), which is consistent with reflow and not with deletion. Ops' own numbers independently confirmed by a lane that built none of it. |
| `paper/**` control bytes | **0** across 28 markdown files |
| citations | 277 entries · 277 cited across 18 chapters · **0 dangling / 0 verify-in-use / 0 literal VERIFY / 0 unused**; one benign advisory (`claude-haiku-4-5-20251001` is a model id in a table, not a cite) |
| **Priority 5** | `audit_reproducibility` **8 PASS / 0 WARN / 0 FAIL**, freeze `3ca6f01ab772…` + gold `7cf5d98843c5…` **re-derived against the real files** |
| campaign | 12/12 lines · `arms_full` 10/10 · `sci=OK` · `drift 0 +1dirty` (ops' declared `build_paper.py` edit) · fence otherwise EMPTY |
| A16 window | **OPEN** — 0 records across 0 of 5 core H2 arms; `test/placebo` unit dir exists (11:24:48Z) holding only `_env/env.json`; **W7 armed and has not fired** |

**One thing deliberately NOT called a defect.** A raw `find outputs/campaign_cluster_run4 -name
record.json | wc -l` reads **2,409** against the cycle's `records=2,369`. `cycle.py:217` describes
`results_audit` as counting *"across ALL roots"*, which would make it a **superset** — yet it is lower.
**So they are different predicates and I did not establish ops'.** Not a miscount claim; flagged for one
authoritative sentence, because after analysis's P134 two lanes reading one archive to two numbers is
worth pinning down.

## This session's own errors — P142 · P143 · P144, all caught before they reached a decision

**P142 — my A16 window census keyed on the wrong predicate and printed `WINDOW: CLOSED`.** It tested
*"does a unit directory exist"*; `test/placebo`'s directory exists holding **only** `_env/env.json` and
**zero** records. Wrong, and alarmist in the direction that would have declared the decision dead.
**The correct predicate was already in my own `W7`** (`watch.py:295-302` — a `-s<N>` directory
*containing* `record.json`) and I wrote a fresh one instead of calling it.

**P143 — my falsification control for the `lanebus` console fix printed `NO CRASH`.** Cause found, not
guessed: I installed the strict `cp1251` stream **before** importing `lanebus`, so lanebus's own
module-level reconfigure ran on **my control stream** and converted it — **my fix defeated the test
written to falsify it.** Re-ordered: ARM A now reproduces the live failure exactly
(`'charmap' codec can't encode character '⚠' in position 3002`) and ARM B completes. *A control that
passes for the wrong reason proves nothing.*

**P144 — my probe for ops' U+FFFF gate reported `ABSENT`.** My regex searched for a literal `uFFFF`;
the gate is present at `:276` and `:438-448`. **I nearly told the bus that ops had shipped two of three
gates** — an accusation, not a caution.

> **All three are one class, and it is the sixth time this lane has paid for it:**
> **a detector that fires — or fails to — is making a claim about its own specification first.**
> **New corollary, adopted by the analysis lane the same hour:** *when a check already exists in the
> watch, CALL it; the ad-hoc re-derivation has not been positive-controlled.*

## F-20 W6 FIRED FOR REAL AND BOTH ITS BRANCHES WERE WRONG FOR THE CASE — one of them could have hidden the failure it exists for

At **13:06:25Z** `W6` fired on `baseline_volatility_scaled_return` — an **N6/H1 canon member, i.e.
confirmatory**. **The news is good and I verified it on the axis that decides it.** The unit went
**26 → 27 → 28 → 29** records in nine minutes (`s14` 13:04:33Z · `s17` 13:07:30Z · `s15` 13:08:29Z),
missing **`[16]` only** — and by F-5's method (`cpu.model_name` from each record's sibling `env.json`,
filtered to `-s<N>` dirs holding a `record.json`, because the `_env/` sidecar carries none and counting
it produced a 12/12 false MIXED once already) there is **ONE distinct CPU model across all 29:
`Intel(R) Xeon(R) Gold 6240`.** All three re-run seeds landed on it. **D16 has not recurred.** Control:
all ten sibling canon units read n = 30, one distinct CPU each.

**But W6 itself was wrong twice:**

1. **Wording.** It emitted *"SEED SETS **DIVERGED** … missing [15,16,17]"* while the missing set had
   just **shrunk** from `[14,15,16,17]`. **A recovering unit fired text identical to a degrading one** —
   good news in an alarm's voice, forcing the reader to do the diff the alarm exists to do.
2. **★ Coverage — and this one could have hidden the failure the check exists for.** **The substrate
   census ran ONLY on the full-reunification branch.** But the D16 defect is a unit spanning two CPU
   models, and that arises **the moment the first re-run lands on the wrong node** — long before the
   seed set is whole. `s14/s15/s17` landing on a 6140 with `s16` outstanding would have emitted a plain
   *"DIVERGED"* and said **nothing about the substrate**, leaving the recurrence unreported until
   reunification — which, at one seed remaining, is exactly when someone reads the unit as healthy.
   **F-5's lesson was that a restored seed COUNT is not recovery; the corollary it missed is that the
   SUBSTRATE must be checked on EVERY tick, not only at the finish line.** I found it only because the
   alarm fired for real and I went to verify by hand what it should have told me.

**Both fixed.** The substrate census now runs on **every** W6 emission and **outranks** the seed-set
state; the short-set branch carries the **direction**. **Positive-controlled — all five branches driven
until they spoke, plus the negative control:** mixed-while-short → `W6 !!! MIXED SUBSTRATE … still
short` (the gap, now covered) · mixed-while-whole · reunified-and-clean · `RECOVERING … count FELL
4 → 3` · `DIVERGED FURTHER … count ROSE 1 → 3` · unchanged → **silent**. **`py_compile` green, and the
watch was RESTARTED at 13:12:54Z so the fix is actually live** — the previous `Monitor` held the pre-fix
code in memory and would have gone on running it. State persisted across the restart
(`watch_state.json` carries the W6 baseline and W7's fired-once flag), so no baseline reset and the
deadline alarm kept its place.

> **P145 — my first positive control errored on all five branches** with `TypeError: unhashable type:
> 'set'`: my fixture used plain `set` where `core_seed_sets` returns **frozensets**, because W6 hashes
> the values to find the modal set. A claim about my control, not the watch — and **a control that
> errors on every branch proves exactly nothing**, the same shape as P143 an hour earlier.

### F-20b ★★★ D16 DISCHARGED at 13:18:07Z — confirmed by a route that does not call this watch

W6 emitted `REUNIFIED`. **That is the most consequence-bearing message this watch produces** — it is
what tells other lanes an N6 IUT leg is back to full power — and F-5 is this lane's own record of that
branch being *"structurally capable of being wrong at exactly the moment someone would rely on it"*. So
it was **re-derived from the archive** rather than relayed:

| measured, all twelve core test units | |
|---|---|
| units found · modal seed set | **12** · **30 seeds** |
| units **not** on the modal set | **NONE** |
| every unit | `n=30`, `distinct_cpus=1` |
| units with a mixed substrate | **NONE** |
| **distinct CPU models lane-wide** | **1 — `Intel(R) Xeon(R) Gold 6240 CPU @ 2.60GHz`** |

And the four quarantined seeds specifically — the actual D16 question: **`s14` 13:04:33Z · `s17`
13:07:30Z · `s15` 13:08:29Z · `s16` 13:16:37Z, every one on the 6240**, unit now `n=30` with nothing
missing from `[0..29]`. **All four re-runs landed on the correct fenced substrate; the defect has not
recurred.**

**What it closes:** ops' D16 option B, on both sides — the unit is whole **and** substrate-homogeneous,
which is the *pair* of conditions the quarantine existed to restore. **Analysis's A12-bis is fully
discharged** (no leg now computes on 26 pairs while its ten siblings use 30, which under the
MAX-over-legs IUT rule would have let the weakest leg decide the node). And the **registered premise is
restored**: `cpu_randomised_device_block` (ratified R108) registers device-homogeneity within every CRN
comparison unit as its premise, and that premise now **holds, measured**, rather than asserted.

> **Stated in both directions:** the seed set and the substrate were verified. **No metric was opened
> and no contrast computed** — this is a validity/provenance confirmation, not a result — and it bounds
> the D16 class only.
>
> **And the honest footnote, because it is the part worth keeping.** This `REUNIFIED` came from the
> branch repaired forty minutes earlier, and was the first real emission after the fix — **but the
> pre-fix W6 would also have reported *this moment* correctly**, since the reunification branch always
> checked the substrate. What the old code would have missed is the window *before* it: between
> 13:04:33Z and 13:16:37Z the unit was short **and being repaired**, and had any of `s14/s15/s17` landed
> on a 6140 the old code would have emitted a bare *"DIVERGED"* saying nothing about the substrate —
> leaving a live recurrence unreported until the moment everyone read the unit as healthy. **It did not
> happen. But the twelve minutes in which it could have were uncovered, and were closed before the
> event finished by luck of timing rather than foresight.** Better written down than claimed as a catch.

## F-21 OPS' A16 BLINDNESS ATTESTATION CONTAINS ONE FALSE OBSERVATION — in the paragraph a referee checks

Ops decided A16 (`M187`) and **the decision is sound** — they read the artefacts themselves, reached the
same reading of `:300`/`:108` this lane reached independently, adopted **δ = 0.0756** as primary with
0.0502 and superiority-only as pre-specified sensitivities, and applied the forking-path direction test
to themselves out loud. **I am not contesting it.**

**But `M187 §1` states: *"placebo … holds 1 test record now."*** Measured at 13:10Z, three ways:
`find test/placebo -name record.json | wc -l` → **0**; W7's exact predicate → **0 matches**; a complete
recursive listing → `test/placebo`, `test/placebo/_env`, `test/placebo/_env/env.json` **and nothing
else**. **`test/placebo` holds zero records.**

> ### ⚠⚠ MY ATTRIBUTED CAUSE WAS WRONG — corrected by ops (M196), verified by me, logged as **P150**
>
> I wrote that the phantom `1` came from a glob sweeping `frozen/placebo-winner/record.json`, and
> called it **"the third frozen-marker miscount in 24 hours."** **That mechanism is not merely
> unproven — it is structurally impossible.** Measured: `frozen/` is a **SIBLING** of `test/`, not a
> descendant, and ops' walk is rooted at `test/`, so it **cannot reach `frozen/` at any depth**.
>
> **The real cause, and it reproduces exactly.** Their probe counted `rglob("*.json")`, which sweeps
> the `_env/` **launcher sidecar**:
>
> | unit | `*.json` | `record.json` | `env.json` |
> |---|---|---|---|
> | `test/placebo` | **1** | **0** | 1 |
> | `test/baseline_raw_return` | **61** | **30** | 31 |
> | `test/random_search` | **61** | **30** | 31 |
>
> The single file under `test/placebo` is `test/placebo/_env/env.json` — so `*.json` returns exactly
> **1**, reproducing the phantom; and each 30-seed unit reads **61** (30 `record.json` + 30 sibling
> `env.json` + 1 `_env/env.json`) against a true 30, which is ops' own report that *every* count in
> that paragraph was roughly doubled.
>
> **Ops' lesson is different from mine and better, and folding it into my class would destroy the
> distinction:** *a **launcher sidecar** is evidence a unit **STARTED**, and counting it as a record
> turns **launched** into **finished**. **Absent, launched and finished are three values**, and the
> glob collapsed the middle one into the third.* Mine was *"frozen markers sit at a different depth
> and keep getting swept"* — a real class (P122/P121/P134 stand) but **not this instance**.
>
> **P150 — the error, stated precisely.** I hedged the mechanism (*"almost certainly"*) and then
> **counted it anyway** — *"the third instance"* — and a count is not hedged. **I built a class around
> a mechanism I had not measured**, in the same message in which I was correcting someone else for an
> unverified observation. Ops' own framing of it applies to me verbatim: *a surprising observation is
> a claim about my own script before it is a claim about the world* — and an attributed **cause** is a
> claim about my own reasoning before it is a claim about someone else's code. **The catch itself was
> right; the diagnosis was fiction.** Reaching a true conclusion through a false mechanism is P41, the
> hardest kind to catch, and I had quoted that lesson at another lane four hours earlier.

**Why it was worth interrupting for.** `§1` is not commentary — it is the **dated evidence that the
decision was made blind**, and it is what will be quoted to justify the pre-specification. A referee who
checks it finds zero and has a reason to doubt an otherwise excellent attestation. **The error runs
toward claiming LESS blindness than they had**, so it is honest — and still wrong, and an unreproducible
observation inside a blindness claim is the worst possible place for one. **The correction makes their
position stronger: zero records on ALL FIVE H2 arms, not four.** Their urgency argument survives intact
and sharper — the `placebo` test unit is **launched** (dir + `_env` sidecar, 11:24:48Z) and is the
**only** core test unit anywhere in that launched-but-empty state.

## F-22 W4 FIRED TWICE IN FIVE MINUTES ON A FLAPPING CONDITION — the saturation failure, recurring inside the check built to detect it

**The trigger was real and ops' own instrument was honest about it.** Their archive sweep crossed its
30 s sleep and back — measured from the cycle log: **31.5 · 35.4 · 31.7 · 40.7 · 18.8 · 17.4 · 18.7 · 24.0
· 18.6 · 17.5 · 12.0 s** — so a `SWEEP-BOUND` ATTN line appeared, cleared, and will reappear as the
archive grows. W4's content signature oscillated between exactly two values and **announced each
crossing as "a genuinely new or cleared alert."**

**Two defects, and the second is the one that costs more:**

1. **No memory.** A return to an already-reported state is not news. **This is the SECOND instance of
   alarm saturation inside W4 itself**, after the timestamp-keying one the previous session fixed —
   in the check whose whole purpose is to surface signal through a permanently-RED verdict.
2. **It named only a hash.** *"the signature moved X → Y … Read `ALERTS.txt`"* sends the reader to
   hand-diff two blocks inside a **282 KB** file. **That is exactly the work the alarm exists to do
   for them, and an alarm that costs more to act on than to ignore gets ignored.**

**Fixed:** `alert_lines()` split out of `alert_signature()` so W4 reports **what** changed — it now
names the **ADDED** and **CLEARED** lines inline — and a bounded memory of observed signatures turns a
flap into `W4 ALERT SET REVERTED (FLAPPING) … this condition has now oscillated Nx. A flapping alert is
ONE standing condition, not N separate events.`

> **⚠ AND THE CONTROL CAUGHT AN OFF-BY-ONE IN MY OWN FIX, which is the reason branches get driven
> rather than read.** My first version appended to `alert_sigs_seen` **only when W4 spoke**, so the
> **baseline** signature — observed silently on the first tick — was never recorded, and **the first
> return to it was reported as a fresh CHANGE.** The revert detector was one crossing late, i.e. it
> missed **exactly the first flap — the one that tells you a condition is oscillating at all.** The
> control fired `CHANGED` where it had to say `REVERTED`. Corrected to accumulate on **every
> observation**; re-driven, and branch B now reports the first revert correctly.

**Positive-controlled, all branches, plus the negative:** baseline → **silent** · genuine new line →
`CHANGED` naming the added line · line clears → `REVERTED … oscillated 1x` naming the cleared line ·
line returns → `oscillated 2x` (the counter is real, not decorative) · no change → **silent**.
**W6's control re-run afterwards as a regression check: all five branches still correct.** All four lane
files `py_compile` clean; `lanebus selftest` and `lane_guard --selftest` both green. **Watch restarted so
W4 is actually live** — a behaviour change does not reach a running `Monitor`.

### …and the same tick produced a stale-comment fix in W1

Ops' ATTN line is also a fact about **my** calibration. `CYCLE_STALL_MIN`'s comment read *"the loop runs
at ~42 s; 6 min is ~8 missed cycles"* — **the real cadence is now ~62 s and grows linearly with the
archive (~6.3 ms/record).** I checked the behaviour before touching it: W1 **is** genuinely
self-calibrating (`max(floor, 5 × median observed gap)`) and degrades correctly — verified by
computation at four cadences: 42 s → 8.6 missed cycles, 62 s → 5.8, **90 s → the calibrating arm takes
over (7.5 min) = 5.0**, 150 s → 12.5 min = **5.0**. It never drops below five missed cycles. **The code
was right; only the justification printed beside it had gone stale** — the reassuring-comment class this
project has now caught seven times in a day. Comment corrected to state the floor-versus-calibrated
split and the measured cadence; **no restart needed, because the diff is a comment.**

## F-23 ★★ F-1 IS STILL OPEN 23 h 14 m ON — and leg9's recovery has just made it unambiguous

**The good news first, and it vindicates the earlier diagnosis.** W2 fired `RECOVERED` on
`leg9_..._h2_pair_test` at 13:58:19Z. Verified rather than relayed — W2's measured precision on this
batch type was **1 true / 1 false** (F-10), which is exactly why: `test_leg_gemini_2_5_flash/`
**`distributional` = 30, `scalar` = 30. leg9's H2-RA pair is complete.** That settles F-8 in leg9's
favour and confirms ops' `qstat` call — leg9's packs were alive, *"unmentioned"* was the correct state,
and it needed no intervention. **The prediction was right and the batch healed itself.**

**And confirming it exposed that the other one did not.** Classified with **ops' own M196 trichotomy**,
which is the right tool here:

| | leg4 (`qwen3.5-9b`) | leg9 (`gemini-2.5-flash`) |
|---|---|---|
| `distributional` | **LAUNCHED-BUT-EMPTY** | **FINISHED** (30) |
| `scalar` | **LAUNCHED-BUT-EMPTY** | **FINISHED** (30) |

**`_env/env.json` sidecars are present on all four units** — so leg4's two units *started* and *nothing
finished*. That is the **middle value**, and it has been the middle value for a day.

**The clock, from leg4's own driver log:** last `h2_pair` mention **2026-07-31 15:44:30** local
(`0/60 done, 60 pending, round 1`); the **very next** `h2_pair` line in that file is the
`RuntimeError: another driver (pid 34216) is already running batch …`; the driver's newest line is
**2026-08-01 14:58:29**, currently driving `placebo_test 0/6`. **Elapsed 23 h 14 m with the driver alive
and working other batches throughout**, while leg4's other arms advanced normally (`scalar_cvar5` 30,
`placebo` 24, `placebo_shuffled` 22). **That is the F-1 shape exactly — the controls raced ahead while
the treatment contrast produced nothing — and it is silent because the line is alive on its survivors.**

**Swept all twelve lines: leg4 is the ONLY one in this state.**

> **What is deliberately NOT claimed: the mechanism.** F-8 is this lane's own record of four lanes in
> one night asserting causation where only a correlation was observed, and *"the driver never
> re-attempted it"* is precisely the sentence that writes itself. What I hold is the **observation and
> the asymmetry**. The mechanism was established by **ops**, from the one place no lane on this laptop
> can see — `qstat` showed leg4's arrays **gone** and leg9's **alive**. **leg9 has now completed exactly
> as that call predicted, which independently corroborates the half I could never check, and leaves the
> leg4 half standing and unactioned.**

**Scope, both directions.** **Not affected: the confirmatory H2** — leg4 is a report-only replication
leg (R80). But it is not nothing: **`qwen3.5-9b` is the capability-gradient BOTTOM anchor** (the ~17 %
authoring-gate-pass leg, the numeracy-bottleneck exhibit), so its H2-RA pair is the **lowest rung** of
that gradient; the open-weight suite is what answers industry-supervisor criterion #1; and it is the only
line affected. **Routed to ops as `M202` with the explicit offer that a deliberate deferral is a
legitimate answer** — recorded as deferred-with-a-reason rather than re-surfaced — because it has now
survived two ops sessions and a coord handover, and *the reason it keeps surviving is that a half-dead
line looks alive*.

## F-24 ★★★ OPS ASKED WHETHER MY WATCH WOULD SEE A POOL-CHANGE SUBSTRATE BREAK. THE HONEST ANSWER WAS NO, TWICE — and the second reason was that I had the wrong invariant

**Context.** Tamer escalated campaign throughput; ops measured Myriad **100 % full across every family
(~12,000 cores, 0.0 % free)** with **3 tasks in `qw`**, and identified share-of-turnover as the binding
mechanism. One candidate lever was widening `smp-[D]*` eligibility. **They asked this lane directly
(M203 §7): would my W-checks SEE a mixed substrate arising from a pool change?**

**Answer: NO, on two independent grounds — and giving a confident "yes" here would have been the F-5
failure exactly, an instrument trusted at the moment it could not deliver.**

1. **The census was gated on a seed-set change.** It sat inside `if sig != st["seedset_sig"]` — and
   with all twelve units at **30/30 on one modal set that signature is CONSTANT**, so **it would never
   have re-examined the substrate at all.** I had improved this check at 13:12Z (F-20) but left it
   hanging off the seed-set signature, so the residual gap was mine.
2. **★ And the predicate itself was wrong.** W6 tested **per-UNIT** homogeneity.
   `src/cluster/integrity.py`'s own D16 block says why that is wrong, verbatim: *"under seed-pool
   blocks **A UNIT MAY LEGITIMATELY SPAN SUBSTRATES**, while what the PAIRED inference actually needs
   is that **AT EACH SEED s EVERY UNIT SHARES ONE SUBSTRATE**, so the substrate cancels in the
   difference D_s. A leg-wide census would red-flag a legitimate stratified run and would still miss a
   mix that happened to balance across units."* **So my check would have false-alarmed on exactly the
   striping ops was contemplating, while missing a break that balanced across units.**

### The answer on cross-pool safety, from the registration rather than from instinct

`cpu_randomised_device_block` is in `ratification_completed` — **signed off by Tamer AND Okhrati under
R108** — and registers heterogeneous silicon as a legitimate **BLOCK level**: *"device is a nuisance
factor, every CRN comparison unit stays device-HOMOGENEOUS (seed-pool blocks), so the device cancels in
each paired difference."* **What is registered is the blocking DISCIPLINE, not single-pool operation.**

| | |
|---|---|
| **SAFE** | stripe whole **seed cohorts** to pools. If seed *s* of every unit lands on one family, the substrate cancels in *D_s*. This is the registered mechanism and what the D16 gate checks. |
| **UNSAFE** | **uncontrolled** widening. On a saturated cluster you cannot choose where a task lands; seed 5 of `distributional` on a D node and seed 5 of `scalar` on an E node **breaks the pair**. |
| **EXCLUDED REGARDLESS** | the `t` pool — `EXCLUDED_CPU_POOLS` excludes it because **AMD EPYC (Zen4) selects different oneDNN kernels → different float reduction order → breaks CRN bit-exactness** (`capture_env.py:82-99`). **A different family can be different ARITHMETIC, not just a different clock.** |

**And the risk profile is better than ops feared, which changes the decision:** `integrity.py:427` —
`health_ok = all_complete AND crn_consistent AND substrate_consistent AND not mixed_winner_units` — and
the C3 gate reads **only** `health_ok`. **So a pair-level substrate break is a BLOCKING STOP, not a
silent corruption.** (`device_homogeneous_everywhere` is explicitly *"informational under seed-pool
blocks"*; the per-seed `crn_pair_substrate_consistent` is the load-bearing one.) The cost of getting it
wrong is **wasted compute and a quarantine** in the D16 shape already executed cleanly — **not a
corrupted result that ships.** *But it fires at the C3 boundary, after the work exists* — which is the
argument for a watch.

### W6b — built, positive-controlled, live

A **per-seed pair invariant** with its **own signature, evaluated every tick**, mirroring
`integrity.py` deliberately so the two can never disagree about what *"inhomogeneous"* means.
**Driven until every branch spoke:** a split seed cohort → `W6b !!! CRN PAIR BROKEN`, naming the seed
and each unit's model · it clears → `CRN PAIRS CLEAN AGAIN` · **legitimate seed-pool striping (each
unit spans two substrates, every seed single-family) → SILENT** · no change → silent. **That fourth
case is the point:** the old per-unit predicate would have screamed at exactly the striping under
consideration. **Live archive, with the clean-zero tell guarded:** 12 units, 30 seeds, **360
(unit,seed) cells**, one CPU model, **zero pair violations** — asserted non-empty first, so the zero is
a measurement. Regression-checked against W4's and W6's controls; all four lane files compile; both
selftests green. **Live at the 14:24:09Z restart.**

> **P155 — I added W6b and did not update the ARMED banner**, which announced seven checks while eight
> ran. **The comment directly above that line records the identical slip twice before.** Third
> instance, made while flagging stale self-descriptions in other people's code. Under-stating coverage
> is the benign direction, but a tool describing itself wrongly is how the next reader mis-calibrates.
> Fixed to name all nine. **Deliberately NOT restarting for it** — W6b was already live, the banner
> only prints at arm time, and a cosmetic fix does not justify a coverage gap.
>
> **P156 — and the script I wrote to verify the banner gave a false negative about my own tool.** It
> reported **W3 as listed-but-never-emitting**, which would have meant a dead check. I suspected the
> script before the file, correctly: my regex was `emit\("(W\d+b?)` and **W3 is emitted from an
> f-string** — a syntactic form the pattern was structurally blind to. Corrected to `emit\(f?\"`:
> **nine emit, nine listed, zero missing, zero extra.** **A checker that cannot see a whole syntactic
> form reports its own blind spot as a finding about the code** — the same family as ops'
> `rglob("*.json")` and analysis's fixed-depth globs, with the added hazard that mine would have been
> an **accusation**.
>
> ⚠ **And one internal inconsistency in my own bus message, recorded rather than quietly dropped:**
> `M209`'s header says W6b went live *"as of 14:26Z"* while its own P155 paragraph says **14:24:09Z**.
> **14:24:09Z is the measured value** — the `WATCH ARMED` line. A figure that reads two ways in one
> document is a defect by this project's own standard, and it is the standard I have been applying to
> other lanes all session.

## F-25 ★★ THE A16 WINDOW HAS A NUMBER ON IT FOR THE FIRST TIME — the core line is one arm from C4

**Found because the W4 rewrite made it visible.** The C4 alert's new ADDED/CLEARED diff showed a
**third** line reaching C4 (`frozen_leg_gpt_5_6_luna` joining `h3_singleshot` and `leg_qwen3_5_9b`).
Before this morning that alert read *"the signature moved X → Y, read `ALERTS.txt`"* and nobody would
have looked. **The fix paid for itself inside two hours.**

**The core line is four of five LLM arms frozen** — `distributional` (28), `scalar` (27), `placebo`
(26), **`placebo_shuffled` (26, newly frozen — there were only four markers at 12:53Z)** — with
**`scalar_cvar5` (22) the only arm standing between the core line and the seed ladder.**

**The ETA, built from ONE predicate deliberately.** The cycle's ATTN prints `scalar_cvar5=18 against 28`
while the directory count reads **22**; those may be different quantities, and mixing them to compute a
rate is the two-predicate trap already flagged on the record count. So this is **record.json arrival
times only**:

| | |
|---|---|
| arrivals | 22 records · first `2026-07-30 06:37:49` · last `2026-08-01 13:13:00` |
| inter-arrival gaps | n=21 · min **0.18 h** · median **0.90** · mean **2.60** · max **24.46** |
| last 8 gaps (h) | 0.18, 3.19, 1.08, 6.18, 1.15, 0.50, 0.84, 0.90 → recent median **0.99** |
| target | **26** — the shallowest depth at which any core arm has actually frozen |
| **ETA** | **3.6 – 4.0 hours** |

> **Caveats, because an ETA is the most over-read number a watch can produce.** (a) mtime is the **pull**
> time, not completion — this lane's own N-2. (b) **26 is a LOWER BOUND, not a threshold**: the four
> frozen arms stopped at 26/26/27/28, so freezing needs no fixed depth. (c) the cluster is **saturated**
> with a shallow queue (ops M203), so arrivals are governed by turnover we do not control; max observed
> gap **24.5 h**. (d) `scalar_cvar5`'s last record landed 12:13Z, **1.4 h before this measurement**,
> against a 0.99 h recent median — well inside normal, but the ETA can stretch as easily as hold.
> **An order of magnitude, not a schedule.**

**Why it matters — and it is smaller than it would have been this morning, which is the good news.**
A16 is **already decided and implemented, blind and timestamped** (ops M187 at 13:01:15Z, M195, blindness
re-verified 13:20:47Z). **The expensive thing — choosing the confirmatory rule — is banked.** What
remains is **prose**, and prose written while blind is materially better than prose written after:
N2 must be written as **one-sided non-inferiority at the SESOI**, never *"superior or equivalent"*
(M195 §6(i); A42 §4 — over three legs the intersection is **strictly weaker** than the union of the two
IUTs), and write-up's own M182(1) found `paper/tables/T_arms_and_hypotheses.md` still states
`h2_ra_iut_or_tost` with a *"decisive either way"* claim that contradicts CH6's three-outcome rule.
**That table is wrong under the implemented rule as well as the old one, and it is the one artefact that
states the confirmatory decision rule directly to the examiner.** Routed to write-up as `M212`.

**Window at send: fully open.** `test/{distributional, scalar, scalar_cvar5}` **ABSENT**;
`test/{placebo, placebo_shuffled}` **LAUNCHED-BUT-EMPTY** (a second such unit; there was one at 12:53Z).
**Zero H2 records on all five arms; 0 of 3 H2-RA legs computable.** W7 armed, not fired.

> **And the script that produced this ETA crashed on its own output** with the cp1251
> `UnicodeEncodeError` — **the exact class fixed in `lanebus.py` this morning** — after printing the
> figures but before its caveats. Numbers unaffected (they precede the crash and were read from the
> real output), but it is the **fourth appearance of that class today** and it is **environmental, not
> a one-off**: anything on this box that prints a non-ASCII character to a pipe is one keystroke from
> dying. Disclosed alongside the number rather than quietly re-run.

---

# F-26 … F-30 — THE COORDINATION CORRECTION (Tamer, ~14:45 UTC) AND WHAT CAME OUT OF IT

## F-26 ★★★★ *"You are doing an awful job at coordinating and orchestrating."* — measured, not argued

**The numbers, computed off the bus's own event log:**

| lane | messages | characters |
|---|---|---|
| **coord (this lane)** | **23** | **99,117 (~19,800 words)** |
| analysis | 20 | 78,760 |
| ops | 12 | 55,374 |
| writeup | 10 | 39,388 |

**The lane whose job is to REDUCE coordination overhead emitted more of it than anyone.** Longest
single message **13,151 characters**. I opened **8 `needs=action` items and closed none** — and across
the bus's entire life there are **10** `ack`/`done` events, **two of them mine**, *in the lane that owns
the bus*. `docs/LANE_PROTOCOL.md`, this lane's own shared contract, went **untouched all session**.

**And the substantive cost, measured after the fact:** of four routed items, **one had landed and three
had not, and nobody knew** — the only record was prose scattered over 200 threads. **I was doing
analysis work and calling it coordination.**

## F-27 THE FIX WAS MACHINERY, NOT A RESOLUTION — `.claude/lanes/openitems.py`

Every cross-lane commitment, **status re-derived from the repo on every run**. No hand-typed status
fields: each row carries a **verifier**, so no lane takes coord's word for anything. `--open`,
`--json`, `--selftest`. Documented at `LANE_PROTOCOL.md` §5b. Threads then actually closed with
`done`/`ack`. **Open went 7 → 5**; ops' four closures each **confirmed independently**.

> **★ AND THE BOARD WAS THE DEFECTIVE PARTY TWICE, IN BOTH DIRECTIONS — the most useful thing it
> produced.**
> **P157, a false DONE:** F-18's verifier pattern-matched the source for something guard-shaped and
> reported a guard that did not exist; execution returned `rc=0`. **A false DONE is the most dangerous
> direction a status board can fail in** — it tells an owner their open item is closed.
> **P160, a false OPEN:** F-19's verifier searched for a literal digest string — but ops solved it
> *better than asked*, **deriving and checking** the bundle at build time rather than hardcoding a
> constant that would go stale.
> **THE GENERAL FORM: A VERIFIER ENCODES THE FIX ITS AUTHOR IMAGINED, so when the owner implements
> something better, the verifier reports the difference as failure.** Both now check mechanisms.

## F-28 ★★ W2's FALSE-ALARM FACTORY — 208 batches mis-classified

`c1_baselines` last logged `3/4 done`, then **three minutes later** `batch complete: {'ok': True,
'completed': 4}`. **`batch_progress.py` parsed only progress lines and never read the driver's own
completion line** — so a batch that *finishes* is byte-identical to one *abandoned*: frozen short, then
silent. W2 reported a **successfully completed** batch as *"either ABANDONED or IN FLIGHT"* and pointed
ops at a cluster call to discriminate two states, **neither of which was the answer**.

**Fixed** — the driver's declaration outranks the last progress tuple; `ok` captured explicitly so an
`ok: False` completion is **not** cleared. **Measured: stranded 6 → 1, complete 25 → 233**, with the one
genuine strand (`leg4_..._h2_pair_test`) **preserved**. Proved it is not merely silencing alarms: every
cleared batch carries a real `'ok': True` line (`c1_canary` completed 90); leg4's h2_pair has **zero**.
**Precision 1-of-6 → 1-of-1**, and **C4 is about to complete batches in bulk.** Baseline re-derived so a
mis-calibrated instrument's allow-list could not outlive the calibration (F-6's rule).

## F-29 ANSWERED OPS' DIRECT ASK — the driver's failure accounting at the C4 job cap

Three things hold: a qsub cap-rejection is `CalledProcessError` → `SubprocessError` ∈
`_TRANSPORT_ERRORS`, so **counted and retried, not instantly fatal**; `pending_submit` is consumed
**only on success**, so **no work is lost**; a fatal raise is clean and the supervisor relaunches.

**But `_outage_is_fatal` is an OR while `run_batch`'s docstring says BOTH** — the same function
documents itself both ways. `72 × 600 s = 43,200 s` = the 12 h wall bound **exactly**, so the two
coincide *only at the default poll*. **The live supervisors pass `--poll-secs 180`, making the real
death clock 3.6 h**, shortening proportionally with any poll reduction — *the direction throughput work
pushes*. One-line fix: derive the count bound from `poll_secs`. Board row `DRIVER-BOUND`.

## F-30 ★★★ THE A16 WINDOW HAS TWO THRESHOLDS, HOURS APART — and W7's own message overstates what it detects

| | what it is | when |
|---|---|---|
| **(A) W7's trigger** | a record on **any** of the five H2 arms (`watch.py:352`) | ~2 h (on `placebo`) |
| **(B) blindness actually lost** | an H2-RA leg becomes **computable** | later — *all three* registered contrasts (`analyze_campaign.py:1174`) are `(distributional, X)`, and **`test/distributional` does not exist** |

**W7 fires hours before (B)**, yet its text reads *"FROM THIS MOMENT any change to the confirmatory
decision rule is a POST-HOC FORKING PATH."* Read literally when it fires, **that tells whoever is awake
that a decision is unavailable when it still is.** Conservative-early is the right *trigger* for a
deadline alarm; the *wording* was mine and overstates it. **Flagged before it fires (M246), and the
board row now reports both thresholds.**

**It also reconciles two lanes who both looked right:** analysis' *"minutes-to-hours"* is correct about
(A); ops' *"~18 h"* is correct about (B). **Both measured honestly — the ambiguity was in the phrase
"the window", which this lane introduced and should have disambiguated when it built W7.**

## Verified for ops before C4 — the archive-wide CPU baseline

Ops found `d97a`/`d97b` **match our exact job spec**, so the *scheduler* could place C4 seeds on a
second CPU model without anyone choosing it. Baseline verified independently, **every line and every
stage**: **2,666 record dirs · 2,617 carry `cpu.model_name` · ALL 2,617 are `Intel(R) Xeon(R) Gold
6240` · one model · zero exceptions** across 22 stage roots. The **49** without a CPU model are the
**frozen winner markers** — P122's exact trap, since a check reading CPU off markers gets nothing.

**W6b's coverage stated WITH its limits**, because a watch trusted beyond its scope is worse than none:
it catches a divergence on the **core test lane within 300 s**, but **reads `test/` only — not search,
not the ten leg lines.** *(Ops subsequently withdrew the risk entirely: `d97a`/`d97b` are 100 %
`@PAID_Economics` and unreachable — and the same fact **refuted their own pack-9 finding**, since all 49
"empty" nodes it rested on are paid. **A capacity number computed over nodes you are not entitled to is
not a capacity number.**)*

> **My errors across this segment — P155 · P156 · P157 · P158 · P159 · P160 · P161, all self-caught
> before reaching a decision.** The two that generalise: **P161** — I reported *"the core line has
> reached C4"* when the alert said **"C4 BOUNDARY reached"**; I dropped the word and reported the
> stage, **alarming four lanes about a deadline ~18 h away**, having quoted *overstating a risk is as
> inaccurate as understating one* at two lanes the same day. **And the CPU census** — my first filter
> was `"-s" in name`, which **silently deleted the entire search stage** (search dirs are
> `<arm>-g5-c0`); I was one step from reporting a partial scan as archive-wide and calling the gap
> against ops' count a discrepancy. **F-11 verbatim, mine this time.**
>
> ⚠ **And a process slip worth more than any of them: I wrote "P157" into two documents WITHOUT drawing
> it from the arbiter** — in the lane that *built* the arbiter, whose protocol says always draw from
> it, and which exists because two lanes once both allocated from P31. It happened to be safe. **Safe
> by luck is not safe by process.**

---

# F-31 … F-33 — THE DEEP SWEEP (Tamer: *"everything must be absolutely flawless"*)

## F-31 ★★★ THE CLASS SWEEP I PROMISED THREE TIMES AND NEVER DID — and it found a fourth instance

After W2 mis-classified a completed batch, I wrote *"audit every sibling that keys on absence."*
**I did not.** W2b and W6 were then found the expensive way — each when it fired. So I finally swept
**every** check in `watch.py` against one question: *can a TERMINAL-SUCCESS state produce this alarm?*

| check | fires on | terminal success → false alarm? |
|---|---|---|
| **W1 CYCLE STALLED** | cycle log stops | **YES — the fourth instance, unfixed until now** |
| W2 stranded batch | silence | fixed (driver's `batch complete`) |
| W2b driver down | silence | fixed (`line_declared_complete`) |
| W3 ledger | a **fall** | no — a fall is never success |
| W5 lane silent | no tool calls | yes, but its own text already says *silent ≠ dead* |
| W6 / W6b / W7 | **presence**, not absence | structurally safe |

**W1's version was the worst of the four**: the ops cycle loop stops when the campaign **ends** — at
the 2026-08-27 exogenous stop or when every line completes — so W1 would have announced *"the ops
monitoring loop has STOPPED; every reading after this point is stale"* **at the exact moment the
campaign succeeded**, as the last thing this watch ever said about it.

**Fixed** using the machinery W2b already had: a stopped cycle with **every** line declared complete
is `CYCLE STOPPED — CAMPAIGN COMPLETE (not a fault)`; with lines still running it is the real stall,
now naming the ratio. **Positive-controlled on four branches, including the one that matters most —
`no driver logs found` must report STALLED, never "complete": absence of evidence must not read as
evidence of completion.** Live archive: **1 of 12** lines complete (h3 only), so W1 would correctly
report a stall today.

> **The lesson is the sweep, not the fix.** Four instances of one class, and the first three were
> each discovered by being wrong in production. **When one detector conflates DONE with DEAD, audit
> every sibling that keys on absence — immediately, not after the next one fires.**

## F-32 THE BOARD-VERIFIER AUDIT — and my audit tool was wrong twice about my board

Same discipline applied to the ten board verifiers, after three had already been wrong
(P157/P160/P164). Classified by **how each decides**: EXECUTION (runs the thing) · ARTEFACT
(inspects campaign data) · SOURCE (greps for a construct — *the fragile class*).

**The audit's first output flagged two things, and I checked both before reporting them:**

1. *"Four verifiers can return DONE when the target file is ABSENT."* **FALSE.** All four return
   `UNKNOWN`. My audit tested naive co-occurrence of `not _exists` and `DONE`, not the actual code
   path. **A false finding, from the audit built to catch false findings.**
2. *"DRIVER-BOUND is SOURCE-fragile."* **FALSE.** It reads numeric **values** (both constants and the
   live `--poll-secs`) and computes a comparison, so it detects the fix however ops makes it. My
   classifier conflated *"greps source for a construct"* with *"reads values from source"*.

**Genuine result: one truly fragile verifier — `LOADER-POOLING`** — which I then rewrote as an
EXECUTION check (below). **Six are ARTEFACT/EXECUTION; none returns DONE on absence.**

## F-33 ★★★★ THE LOADER HAS **THREE** CONTAMINATION SOURCES, AND FILLING C4 MAKES IT HARDER TO SEE

Analysis' M259 found the first. Confirmed from source, then extended:

| # | source | measured |
|---|---|---|
| 1 | **leg POOLING** into core arms | analysis: 141 of 142 H2 test records from leg lines |
| 2 | **leg DROPPING** on collision | **732 returned against ~2,168 ELIGIBLE** — nobody had numbered this half |

> ⚠ **CORRECTED, AGAINST MYSELF.** I first wrote *"732 of 2,766 on disk"* here and in the CHANGELOG.
> **2,766 is every `record.json` in the archive, and it includes the 598 `*_h3_singleshot` records the
> loader excludes BY DESIGN.** Charging a deliberate, correct exclusion to the defect **overstates
> it**. The honest denominator is the *eligible* set — 2,766 − 598 ≈ **2,168** — giving ~66 % dropped,
> which agrees with ops' independently measured **1,528 of 2,260 (68 %)** at their measurement time.
> **The defect was enormous either way; that is not a reason to state it larger than it is.**
> *Overstating a risk is as inaccurate as understating one* — my own standing line, applied to my own
> record on the most consequential finding of the day.
| 3 | ★ **`.pull_tmp.*` dirs are inside the walk** | **new** — and they **win every collision** |

**Source 3, verified live.** `_walk` iterates `sorted(...)` with **no filter on hidden/temp
directories**, and `.pull_tmp` begins with `.` (0x2E) — which sorts **before every real subtree**,
while `setdefault` keeps the **first**. So a partially-pulled record **beats the real archived one**.
`.pull_tmp.28884/search/random_search/random_search-c11/record.json` collides with the real record and
**is currently what the loader serves**.
**Severity in both directions: the two files are BYTE-IDENTICAL** (sha `180188cb7508ba2e`, 22,470 B,
all three siblings present) — **no result is wrong today**. The pull completed; only the temp dir was
left behind. **But the mechanism is live: an interrupted pull leaves a truncated record that then
takes precedence, silently.** Same shape as ops' torn `ALERTS.txt` line — harmless instance, real
mechanism. *(The h3 guard does hold inside the temp dirs: `.pull_tmp.34624`'s records are under
`test_h3_singleshot` and are correctly skipped one level down.)*

### ★ The refinement that reverses the urgency argument

Walk order is `sorted()`, so `search` < `search_leg_*` and `test` < `test_leg_*`. **On a collision the
CORE record wins and the leg record is dropped — therefore pooling happens ONLY WHERE THE CORE ARM IS
EMPTY.** That is precisely the H2 test arms *right now*, which is why the arms present as a clean
30/30/30/30/22 built almost entirely from legs.

**Consequence nobody had stated: as the core arms fill during C4, core records begin winning those
collisions and the contamination becomes a MIXED pool rather than an all-leg one. It does not go
away — it becomes harder to detect.** A core arm holding 27 core + 3 leg records is far less visible
than one holding 30 leg records, and every existing tell (the suspiciously exact 30, the uniform
`reward_source_hash`) weakens. **So "it will look fine later" is a false reassurance — the defect is
at its most visible today**, which argues for fixing it *during* C4 rather than at teardown, the
opposite of the "not urgent, nothing has run yet" framing I had accepted.

**Board row rewritten as EXECUTION**: it runs the real loader (~5 s, writes nothing) and asserts the
property, so it flips to DONE **however ops fixes it** — which matters, given the board has already
lost that bet three times. **Suggested to ops: skip any directory whose name starts with `.` — one
line, and it removes source 3 permanently.**

**Also verified rather than assumed: the A16 window check covers BOTH H2 co-primaries.** The tail
(N1) legs are built inside the *same* `for arm_a, arm_b in contrasts` loop as the Sharpe (N2) legs,
so both are gated on the same three `(distributional, X)` pairs.

## F-34 ★★★ THE QUESTION THAT MATTERED MOST — *"can my own fixes now SUPPRESS a true positive?"*

Every false-alarm fix made today traded **noise for quiet**. That is the right trade only if it
cannot also silence a real event, so the last act of the sweep was to attack my own repairs from the
dangerous side.

**It found one, in `batch_progress.py`.** `declared_done` was set on the driver's completion line and
**never cleared**. So a batch that **completed → was RE-SUBMITTED → then STRANDED** would have read
`complete = True` from the stale declaration and **W2 would have said nothing**.

**That is the exact shape of `leg4_..._h2_pair_test`** — 0/60 for over a day on an H2 primary
contrast — which is the failure this detector exists to catch. **A noise fix would have blinded the
one check that caught the real thing.**

**Fixed:** a progress line showing incomplete work proves the batch is live again, so the earlier
declaration no longer describes it. **Falsification-controlled on a synthetic driver log through the
real parser:**

| case | result |
|---|---|
| completes and stays done | `complete=True` — the false-alarm fix is intact |
| **completes → re-submitted → strands** | **`complete=False` — the suppression is gone** |
| completes → re-submitted → completes again | `complete=True` |

**Live archive after the fix: stranded = 1 (`leg4_..._h2_pair_test`), complete = 245.** The one
genuine strand still surfaces and no false alarms returned.

> **The generalisable point, and it is the one I would carry out of this whole day:** after fixing a
> detector for FALSE POSITIVES, attack it from the FALSE NEGATIVE side before trusting it. Noise is
> visible and annoying; suppression is invisible and expensive. **I made four noise fixes today and
> only the fourth prompted me to ask what they cost in the other direction.**

## F-35 ★★ W6, THIRD ATTEMPT — I MOVED THE THRESHOLD TWICE BEFORE FIXING THE PREDICATE (P166)

| attempt | rule | fired wrongly on |
|---|---|---|
| 1 | alarm on **any** subset | `placebo` at **1/30** (P162) |
| 2 | alarm above **half** the modal set | `placebo` at **16/30** (P166) — a healthy unit mid-C4 |
| 3 | **PROGRESS, not size** | correct |

**Both of the first two were SIZE rules.** Every arm crosses half while filling, so attempt 2 would
have flooded during C4 across all five H2 arms and every leg.

**And the correct rule was already in my own findings file.** F-2/P111: *"the predicate is now
`(unmentioned > X) OR (done has not MOVED for Y)`"* — key on **progress**. I wrote that, quoted it at
other lanes, then wrote two size rules.

**Now:** count **decreased** → alarm immediately (*seeds were REMOVED — the D16 shape*); count **grew**
→ quiet however far from modal; count **static** → alarm only after ~2 h **and** only while every
sibling is complete, because a training wave is ~9.24 h and units legitimately sit still between waves.
**The alarm also names its cause** — `[SEEDS REMOVED (30 → 26)]` or `[STATIC at 16/30 for ~120 min
while every sibling is COMPLETE]` — because one that fires correctly but names the wrong reason is what
sent ops to spend a cluster call on a completed batch. Six branches controlled; live now: `placebo`
17/30 and growing → correctly **FILLING**.

## F-36 ★★★★ `watch.py` HAD NO SELFTEST — AND ITS FIRST ONE FOUND A LIVE LATENT DEFECT IN TWO RUNS

**The indictment first.** `watch.py` is 898 lines, was edited **eight times** today, produced **five**
defects, and is the only instrument watching the A16 window and the CRN precondition — **and it was the
only lane file with no selftest.** `lanebus.py`, `lane_guard.py` and `openitems.py` all had one. *The
most-changed, most-defective, most load-bearing file had the least self-verification*, and every defect
was caught by hand-driving branches in scratch scripts that were then discarded.

**P167 — the defect it found, live:**

```python
base = set(st.get("stranded_baseline") or [])
if not base:                      # an EMPTY baseline is indistinguishable from an ABSENT one
    emit("W2 BASELINE", ...)
```

The baseline currently holds leg4's `h2_pair`, so nothing shows. **The moment that strand is resolved
the baseline goes empty and W2 re-emits `BASELINE` every 300 s, forever** — a permanent flood triggered
by the campaign reaching its *healthy* state, starting on the day ops fixes leg4.

**That is the withdrawn-claims register's own standing rule, in my code:** *zero and absent are
different values, and every idiom that conflates them is a defect in audit code.* `x or []` is exactly
that idiom. Fixed by testing key **presence**.

> **And note how it surfaced.** Five cases failed; I assumed my fixtures were wrong, seeded the
> baseline — and **they still failed**. Only then did I read the condition instead of guessing.
> **My diagnosis ran ahead of the evidence for the third time today; the selftest was right and I was
> not.**

**22 cases, every one a defect this file actually shipped tonight**, and **mutation-proven**: breaking
W7 so it can never fire produces exactly *"W7 first core H2 record -> fires: expected a tag containing
'PRE-DATA WINDOW CLOSING', got SILENCE"*; restored, green again. **A test that cannot fail verifies
nothing.** Run it: `python .claude/lanes/watch.py --selftest`.

> **The highest-yield act of the entire day was not any individual catch — it was building the
> selftest for the instrument I had changed most. It found a live defect in two runs that eight hours
> of careful hand-checking had missed.**

## F-37 ★★★★ EVERY INSTRUMENT NOW SELF-VERIFIES — and building the last two found three more live defects

**I left the gap I had just named.** An hour after telling the bus *"if any instrument you rely on
lacks a selftest, that is where the next silent defect is"*, `batch_progress.py` — 413 lines, the file
behind W2, which **mis-classified 208 batches** today and into which I then made a **suppression
fix** — still had none. Built: **15 assertions**, each one a defect this file actually shipped.
**Mutation-proven** (reverting the suppression fix yields *"re-submission REVOKES a stale completion:
got True, want False"*), and the normal `--json` CLI path W2 depends on verified intact.

### Then I mutation-tested the selftests themselves — and my board's could not see a broken verifier

`openitems --selftest` asserted only that DONE and OPEN both appeared **somewhere across** the board —
an aggregate a single flipped verifier survives untouched. **Measured: flipping one `return DONE` to
`return OPEN` left it reporting "all verifiers answered, both values present."** *A status nobody can
re-derive, sitting inside the board's own self-verification.* **P171.**

**Fixed with a general discriminator:** point every verifier at an **empty world**; one that still
answers DONE or OPEN is not reading the repo. It now catches that exact mutation.

### And on its first run the strengthened selftest found two non-discriminating verifiers

| row | behaviour on an empty world | why it matters |
|---|---|---|
| `M166` | returned **OPEN** | a missing *archive* read as a missing *summary* |
| **`A16-WINDOW`** | returned a confident **"window OPEN"** | **if the archive root were ever wrong or missing, the A16 clock would have reported *"the decision is still available"* on the strength of nothing** |

That second one is a **false reassurance on the single most consequential row I maintain**, and it is
the same class as everything else fixed tonight: **the absence of evidence is "I cannot tell", never
"all clear".** Both now return `UNKNOWN`.

> **P172 — and my mutation harness gave a false verdict while doing it.** It decided *caught* via
> `"FAIL" in output`, which matched the word **fail-open** in `lane_guard`'s own success message — so
> it reported a break as caught that was not. **An instrument built to test instruments, wrong about
> an instrument.**

### ★ ALL FIVE ARE NOW MUTATION-PROVEN — the gap above is closed

I first reported `lanebus` and `lane_guard` as *"passes but NOT mutation-proven — I could not construct
a mutation their selftests reach."* **That was a statement about my mutations, not about their
selftests**, so I went back and found reachable targets by reading what each selftest actually
exercises rather than guessing.

| instrument | mutation applied | caught by |
|---|---|---|
| `watch.py` | made W7 unable to fire | *"W7 first core H2 record -> fires: expected … got SILENCE"* |
| `batch_progress.py` | reverted the suppression fix | *"re-submission REVOKES a stale completion: got True, want False"* |
| `openitems.py` | made one verifier a constant | *"A16-GUARD: returns DONE on an EMPTY world"* |
| `lanebus.py` | broke `path_matches`' bare-prefix branch | *"FAIL g9: got False want True"* |
| `lane_guard.py` | made an **unregistered** session resolve to a lane | *"FAIL unregistered blocked → permissionDecision: deny"* — **the fail-open contract itself** |

**Every instrument this lane relies on has now been deliberately broken and seen to fail.**
**Restores verified byte-exact and BEHAVIOURALLY** — not merely by "the selftest passes again":
`path_matches("docs/ops/watch/CYCLE_LOG.md", "docs/ops")` → `True` and
`path_matches("docs/opsx/cycle.py", "docs/ops/**")` → `False`, confirming the mutated branch is
genuinely restored rather than coincidentally green.

> **The correction worth keeping:** *"I could not construct a mutation"* is a fact about the person
> holding the hammer. Twice today I reported a limit of my own effort as a property of the thing
> being examined — here, and in the verifier audit where my classifier called `DRIVER-BOUND`
> fragile. **Say what you did; do not promote it into what is true.**

> **The two highest-yield acts of the entire day were the two I did LAST, and only because Tamer
> pushed: the CLASS SWEEP (a fourth done-vs-dead defect) and the SELFTESTS (three more in four runs).
> Eight hours of careful hand-checking found fewer defects in my own instruments than twenty minutes
> of systematic self-verification. The question worth asking of any instrument is not "does it work"
> but "have I ever seen it FAIL".**

## F-38 ★★★★ A BLINDNESS HAZARD THAT ARMS ITSELF — and a correct fix that INVERTED another defect

### (a) `cost_decomposition.py` would print a TREATMENT arm's sealed Sharpe

Raised by write-up (M281/M283), **verified here by reading — never by running.**
`docs/ops/cost_decomposition.py:55` globs `test/*/*/record.json` — *every* unit — and `:67` prints
each one's net and gross Sharpe. **`test/placebo` now holds 30 records, and `placebo` is an H2
treatment arm.**

**Nobody has to do anything wrong.** Written 2026-07-30, when `test/` held only the eleven H1
baselines and `random_search` — **the glob was implicitly scoped by what existed, and C4 widens it
automatically.** Its docstring's safety line reads *"READ-ONLY. Report-only analysis; changes no
design and no archive"* — **true about WRITES, silent about BLINDNESS**, so a reader who checks
before running finds a reassurance and it is the wrong one. Eighth reassuring-comment instance of the
day; this one costs effect-blindness. Board row **`UNBLIND-GLOB`**, top of the list.

### (b) ★ Ops' A79 fix is correct — and it inverted the `.pull_tmp` failure mode

**Verified independently from a clean loader run:** loaded **2,290**, eligible **2,293**, **dropped 3
— was 1,528 (68 % of the archive)**, and **216 duplicate triples, exactly their figure.** The
`(directory, run_id)` key is right: the directory is the only line-bearing discriminator, since the
record carries none.

**But the `.pull_tmp` source I raised in M267 did not stay independent of the fix:**

| | before A79 fix | after |
|---|---|---|
| key | global `run_id` | `(directory, run_id)` |
| `.pull_tmp` copy | sorts first (`.` = 0x2E) → **DISPLACES** the real record | different directory → **BOTH LOAD** |

**`random_search-c11` is now returned TWICE**, both copies hashing identically
(`3623dac9e0bfb8e1`; on-disk files byte-identical, sha `180188cb7508ba2e`). **So one of the 216
"genuine cross-line duplicates" is an artefact** — 215 are the point, 1 is the same record counted
twice, in `random_search`, an H4 comparator arm (node N4).

> **Magnitude honestly: ONE record in 2,290.** The other two `.pull_tmp` records sit under
> `test_h3_singleshot` and the h3 guard correctly excludes them.
>
> **Why it is worth raising at volume anyway: I treated `.pull_tmp` as an independent one-liner, and
> it was not independent — the fix changed its failure mode. And DUPLICATION is the harder failure to
> notice, because the totals now look BETTER, not worse.** The fix is still the same single line
> (`_walk` skips any child whose name starts with `.`), now with a stronger reason.

**Seconded to ops, because it is the sharpest sentence on the bus today:** withdrawing the implicit
claim that their dress rehearsal validated the *numbers* while keeping what it did validate —
**"it validated the plumbing, not the values."**

> **P173 — and my own verifier for the blindness row failed the same way, seconds after I wrote it.**
> Its first version returned **DONE when the file was absent**, so against an empty world it declared
> the hazard resolved. **A missing repo is not evidence a hazard is gone.** The empty-world
> discriminator built forty minutes earlier caught it immediately — without it, the most consequential
> row on the board would have shipped reading DONE.

## Fixed in this lane's own machinery

**`lanebus.py log` crashed on the bus's own content** — `UnicodeEncodeError: 'charmap' codec can't
encode character '⚠' in position 3002` — the **F-10 class recurring inside the coordination substrate
itself**. The exposure was much wider than that verb: **`board` is printed by the `SessionStart` hook on
every session boot**, and its previews are lane-authored, so one warning sign in the first ~100
characters would take the board down for every new session — **including the withdrawn-claims section a
lane is required to read before a claim enters `paper/`.** Fixed with one `sys.stdout/stderr.reconfigure(
encoding="utf-8", errors="replace")` at import, mirroring `watch.py`'s existing F-10 remedy — chosen at
module level precisely because it fixes **every** print site at once. Verified: `py_compile` on all four
lane files · `lanebus selftest` and `lane_guard --selftest` both green · the previously-crashing `log`
path now exits 0 with empty stderr · and **the falsification control above proves the pre-fix stream
still raises**, so the check can fail.
