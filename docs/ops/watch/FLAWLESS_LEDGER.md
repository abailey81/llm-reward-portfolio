# FLAWLESS LEDGER — the standing open-items register for the 30-minute deep check

**Tamer, 2026-08-04:** *"make sure the checks that are every 30 minutes do not stop until they ensure
absolutely everything is 10000% absolutely strictly flawless. I give them full permissions, do
whatever it takes to ensure absolute flawlessness."*

---

## THE CONTRACT — READ THIS BEFORE TOUCHING A ROW

**★★★ TAMER, 2026-08-04: *"make sure if something is found, it's ALWAYS FIXED, and ensure that
absolutely everything is very strictly absolutely flawless."*** So the contract is not "triage into
three buckets". It is:

> ## ⇒ EVERY FINDING IS **FIXED**. FIXING IS THE DEFAULT AND THE REQUIREMENT.
> **A pass does NOT end while a fixable row remains open.** Not "advance one row" — clear them.
> The other two states are NARROW, JUSTIFIED EXCEPTIONS, never a resting place and never a way to
> avoid work. If you can fix it, you fix it, this pass.

| state | when it is allowed | what it requires |
|---|---|---|
| **FIXED** | **ALWAYS, unless one of the two exceptions below is PROVEN to apply** | the defect is gone AND the fix was FALSIFIED — the new assertion must fail against the pre-fix behaviour. A passing test proves nothing on its own (RUN 18 reported a file "verified byte-identical" that had never been modified). |
| **PROVEN-BENIGN** | only when there is NOTHING to fix because the underlying state is correct | a MEASUREMENT with its command and output. ⚠ **AND IF AN INSTRUMENT MISLED US, THE INSTRUMENT IS STILL FIXED.** A false alarm is itself a defect. "The campaign was fine" never closes a row about a check that said otherwise — both halves get answered. |
| **ESCALATED** | only when the fix is *outside this session's authority* — UCL fair-share, a frozen pre-registered value, a Tamer decision | the precise reason it cannot be actioned, a specific ask for Tamer, **and every fixable thing AROUND it fixed anyway.** Escalating the un-actionable half never excuses leaving the actionable half. |

### NO ROW MAY AGE

A row that survives **three consecutive passes** without reaching a terminal state is itself a
finding: say so to Tamer by name, with what is blocking it. Silent aging is how an open defect
becomes a permanent one.

### "FLAWLESS" IS A CHECKABLE STATE, NOT A FEELING

The board is flawless when **every row in OPEN is empty**, every gate reads its green
(preflight 17/17, seven layers RC=0, drift 0, freeze MATCHES, repro 8/0/0, line_balance CLEAN), and
every remaining entry is either a permanent DISCLOSURE or an ESCALATED item carrying Tamer's name.
Anything else means the pass is not finished.

### ⛔ THE ONE RULE THAT OUTRANKS "MAKE IT GREEN"

**NEVER make a check pass by weakening the check.** No raised threshold, no widened tolerance, no
skipped assertion, no suppressed alarm, no `continue` past an error, no frozen value edited. On this
campaign the fastest route to a green board is to break the instrument, and that is the one outcome
worse than a red board. If a check is genuinely wrong, fix the CHECK and prove the fix falsifies —
then say so in the row. Fix causes, never symptoms.

### WHAT IS NOT A DEFECT, AND MUST NOT BE "FIXED"

A check that never stops needs to know where the floor is, or it will chase honest states forever.

* **The common rung being 0.** That is the campaign's true current state under R101, not a fault.
* **Holes below an arm's frontier while jobs are running or queued.** Normal during pipelined C4.
  Actionable ONLY on hole + ZERO running AND ZERO queued.
* **`RED` on the cycle line, `guards=2`, `seed_alignment:CRITICAL`, `silent_hang:UNKNOWN`, the
  truncation and transport entries.** Acknowledged in `docs/ops/acknowledged_alarms.txt`; each
  carries its own re-triage trigger. Re-read the trigger, do not re-litigate the alarm.
* **`M2_r115_threshold` exiting 1.** By design. The registered insensitivity claim IS falsified and
  that is the disclosed state; it cannot return to 0 without editing a frozen value, which is
  forbidden.
* **`M3_seed_completeness` exiting 1** while lines are climbing. Same reason.
* **Core count / fair share.** Closed by fourteen independent measurements. The only remaining lever
  is a human request to UCL RC, which is Tamer's decision. Do not re-open it.
* **Lines idle on the test tier with work queued.** Fair-share, not a fault. `line_balance` is the
  arbiter.
* **The 2026-08-12 Myriad maintenance.** A planned at-risk day with a playbook.

---

## ★★★ THE SPEED COMPONENT — MEASURED EVERY PASS, AND ACTIVELY MAXIMISED

**Tamer, standing priority (2026-07-24, re-stated 2026-08-04):** *"don't forget to add the speed
check component all the time, and its maximisation."* Under R101 the rung reached by the Aug-27
exogenous stop is set by THROUGHPUT, so throughput is the seed rung is the grade. Every pass
measures it, records it, and compares it to the previous pass.

### WHAT TO MEASURE EVERY PASS (append the row to the SPEED LOG below)

`rec/h (12 h and 24 h)` · `slots held` · `running / queued jobs` · `% of the rate from ONE line`
· `critical-chain remaining (tpe / bayes_opt candidates owed)` · `ETA to rung 30 / 403 / 568`
· `days to the Aug-27 stop`. Source: `docs/ops/stage_eta.py` plus a qstat census.

### A THROUGHPUT REGRESSION IS A FINDING, AND FINDINGS GET FIXED

If `rec/h` or `slots held` drops materially against the previous pass, that is an OPEN row and it is
worked to a cause, not noted. The live causes worth checking, in order of how often they have
actually bitten this campaign:

1. **Jobs holding slots without producing** — a driver crash-looping, a stalled chain, a hung pull.
2. **`Eqw` / `hqw` jobs** — zero is the expected count; any is a finding.
3. **Jobs unschedulable BY CONSTRUCTION** — RUN 17 found eight requesting a PE (`smp-[TBD]*`) that
   does not exist, holding queue slots forever. `qalter -w p` is the probe; `qconf -spl` is the truth.
4. **A line idle with NO work queued** — that is a genuine fault, unlike idle-with-work-queued.
5. **Drivers/supervisors below roster** (10/10 while 2 lines are COMPLETE).
6. **Disk approaching the floor**, which stops archiving before it stops training.
7. **Transport failures eating cycles** — each failing pull pays its own latency and walks the
   death clock (TEST 12.0 h, SEARCH 3.0 h, both LOWER bounds).

### ★★★ 2026-08-04 10:40 UTC — TAMER ASKED DIRECTLY, SO THE CORES/ETA QUESTION WAS RE-MEASURED

**The re-measurement was warranted:** the fleet had changed materially since the fourteen
measurements (slots 1,600 -> 1,900, concentration 98% -> 51%, queue 314 -> 150). **Every constraint
re-tested unchanged:** 357 jobs against a 1,000 cap, `qquota` EMPTY, **zero** `Eqw`/`hqw`, and
`qalter -w p` verifies queued jobs as schedulable. Still functional fair-share by user.

**BUT THE IMPORTANT ANSWER IS NOT ABOUT FAIR-SHARE. IT IS THAT CORES CANNOT MOVE THIS RESULT.**

**Q1 — where does the fleet's output actually go?** Measured over 12 h: **2,098 of 2,122 records
(98.9%) landed in cells ALREADY AT OR ABOVE rung 30. Only 24 records (1.1%) reduced the rung-30
backlog.** Under R101 the reported result is the COMMON rung, so doubling the cores doubles the
98.9% and raises the reported result by **nothing**.

**Q2 — the floor with INFINITE cores.** `bayes_opt` owes **3 of 30** candidates and `tpe` **3 of
30**, and the DFO chain is strictly sequential by construction (each proposal is a function of the
fitnesses already observed). At 4.5 h per 8-thread step that is **13.4 h** that no hardware
compresses. Core then still needs its C2 `h2_pair`, the C3 gate and the C4 test leg, and a TEST
training is 1-thread, so its wall is the full **8.5 h**. **⇒ FLOOR TO A NON-ZERO COMMON RUNG WITH
INFINITE CORES: >= 21.9 h.**

**Q3 — the one real inefficiency, measured and NOT actionable.** `leg8` (sonnet) holds **202 of 214
running jobs = 94%** of our fair-share allocation, and sonnet **already banks 30** and is climbing
above the common rung. The five lines that CAP the result hold **22 queued jobs and ZERO running**
(glm 8, kimi 5, nemotron 4, core-C1 4, deepseek 1). Three of them -- glm, kimi, nemotron -- are
**QUEUE-blocked, not gate-blocked**: their `h2_pair_test` work is submitted and pending. So more
allocation WOULD help those three. **It would still not move the common rung, because core floors it
at 21.9 h.** Every mechanism is closed anyway: raising priority is operator-only, lowering ours is a
standing prohibition and one-way, and killing reserved queued jobs forfeits the reservation.

**⇒ THE ETA IS NOT CORE-BOUND. It is bound by a SERIAL DEPENDENCY CHAIN.** The only lever that
exists is the human one -- asking UCL RC for a larger allocation -- and even that cannot take the
common rung below ~22 h. **Do not spend campaign time on cores; spend it on the write-up.**

### ★★★ 2026-08-04 12:50 UTC — TAMER ASKED "WHY ARE WE NOT EVEN AT 300 rec/h?", SO THE THROUGHPUT IDENTITY WAS MEASURED END TO END

**THE ANSWER IS ARITHMETIC, NOT POLICY, AND 300 rec/h WAS NEVER PHYSICALLY AVAILABLE.** For a fleet
where every slot runs one 1-thread training at a time:

> **records/hour = slots x utilisation x yield / T_training**

All four terms were MEASURED from artefacts already on disk — `ledger/*.epilogue.jsonl` (3,235
tasks carrying `secs` and `rc`) and the cycle log's `cores=` history (194 stamps) — not assumed.

**T IS NOT ONE NUMBER, AND POOLING IT WAS MY FIRST ERROR.** Split by phase, successful tasks only:

| phase | n | p10 h | median | **mean** | p90 |
|---|---:|---:|---:|---:|---:|
| SEARCH (DFO / generation), 8-thread | 1,580 | 3.18 | 4.24 | **4.64** | 6.68 |
| **TEST / sweep (C4)** | 1,123 | 8.82 | 9.45 | **9.52** | 10.24 |
| TEST / per-arm | 206 | 8.45 | 8.98 | **9.04** | 9.76 |
| TEST / baselines | 61 | 7.89 | 8.31 | **8.39** | 9.11 |
| TEST / h2_pair (C2) | 51 | 8.35 | 8.96 | **9.05** | 9.82 |

A pooled mean reads **6.54 h** and is meaningless: it mixes 8-thread SEARCH with 1-thread sealed
TEST, and the campaign is now almost entirely TEST. **The number that governs the record rate is the
TEST-phase mean, 9.39 h over n = 1,441.**

**THE CEILING, AND IT IS HARD:**

```
S = 1,879 slots (recent mean of the cores= stamps)   y = 0.9972 (TEST-phase yield)   T = 9.39 h
CEILING  = S * y / T = 199.6 rec/h
MEASURED (12 h)      = ~165 rec/h      =>  UTILISATION 83%
SLOTS NEEDED FOR 300 = 2,824           =>  1.50x what we hold
```

**⇒ 300 rec/h REQUIRES HALF AGAIN AS MANY SLOTS, ON A CLUSTER WHERE WE ALREADY HOLD ~20% OF ALL
RUNNING SLOTS ACROSS 98 USERS.** At 1,879 slots the arithmetic ceiling is 200, and we are at 83% of
it. The residual 17% is dispatch gaps — jobs finishing while their replacements sit `qw` (69 right
now) — plus the 32-minute transport outage that falls inside the same 12 h window.

**AND T IS FROZEN DESIGN, NOT AN OPS DIAL.** 400,000 steps at the measured ~13 steps/s/core is
8.55 h of pure compute; the observed 9.39 h is that plus ~10% for start-up, the gold sha256
verification and archiving. **There is no hidden waste in it, and it cannot be reduced without
changing the step budget or the thread count — the first is a frozen pre-registered value and the
second breaks CRN determinism by changing floating-point reduction order.**

**YIELD IS NOT THE PROBLEM, AND THE APPARENT FAILURES ARE THE SCIENCE.** TEST-phase yield is
**99.72%**. The 194 `rc=1` tasks (6.0% of the ledger) sit **entirely in SEARCH** and complete in
**0.00 h** — they are the sandbox rejects that per-model authoring reliability MEASURES. The one
genuinely expensive failure mode is **`rc=126` at exactly 15.00 h**, the `h_rt` wall: only 20 tasks,
but each burns a full 15 slot-hours, ~300 in total.

**⚠ TWO HYPOTHESES I TESTED AND HAD TO DISCARD, recorded because discarding them is the finding.**
(1) *The pack-8 tail*: a pack holding 8 slots until its slowest task finishes would waste ~38%, and
that matched the residual almost exactly — **REFUTED by measurement**: slot-hour-weighted fleet
utilisation from the tail is **0.9979**, because 3,209 of 3,222 epilogue ledgers hold exactly ONE
task, so my "one ledger = one pack" mapping was simply wrong. (2) *A pooled T*: see above.
**Both looked right and both were wrong, and only measuring told the difference.**

**⚠ A POPULATION CAVEAT THAT MUST TRAVEL WITH THESE NUMBERS:** the ledger holds **3,235 tasks**
while the archive holds **~12,700 records**, so it is NOT a complete census of trainings. Every
figure above describes the tasks that wrote an epilogue. State that whenever they are quoted.

**⇒ AND THE REFRAME THAT OUTRANKS ALL OF IT: even at 300 rec/h the REPORTED RESULT WOULD NOT MOVE.**
90% of the rung-568 backlog sits on cells that produced nothing in the last 12 h, behind stage
barriers — core's serial C1 chain and the four lines that have not begun their `h2_pair`. Extra
throughput lands in cells already above the common rung, which is the 98.9% measurement this ledger
already records. **Throughput is at 83% of a hard physical ceiling; the result is bound by a serial
dependency chain, and those are different constraints.**

**★ AND THIS CLOSES THE PRACTICAL HALF OF E-wc.** P277 established that `wall_clock` is 0 on every
sealed-test record and that the compute is recoverable from `ledger/*.epilogue.jsonl`. **The table
above IS that recovery**: the sealed-test tier's per-training wall is 9.39 h mean / 9.45 h median,
measured, with its own distribution. The write-up's compute accounting can be built from it.

### ★★★★★ 2026-08-04 13:00 UTC — "BRING THE ETA TO ITS GLOBAL MINIMUM" (Tamer). IT IS ALREADY THERE, AND THIS IS THE FIRST TIME THAT HAS BEEN PROVEN **PER JOB** RATHER THAN ARGUED

Every previous statement of this rested on aggregates (98.9% of output lands above the common rung;
the chain floor is 21.9 h). **This one resolves the queue job by job**, using `qstat -xml` for
untruncated names (P276) joined to the per-arm seed census, and it settles the question.

**STEP 1 — WHICH ARMS ACTUALLY CAP THE RESULT.** Arms below rung 30, i.e. the only work whose
completion can move the common rung off 0:

| line | tag | capping arms (current seeds) |
|---|---|---|
| `test` (core) | `c1` | cma_es(0), **distributional(0), scalar(0)** |
| `test_leg_deepseek_v4_pro` | `leg1` | distributional(0), placebo_shuffled(22), scalar(0) |
| `test_leg_glm_5_2` | `leg2` | **distributional(0), scalar(0)** |
| `test_leg_kimi_k3` | `leg10` | distributional(12), scalar(12) |
| `test_leg_nemotron_3_super` | `leg7` | distributional(0), scalar(0), scalar_cvar5(0) |

**STEP 2 — WHERE THE FLEET ACTUALLY IS.**

```
CRITICAL   running  24 jobs /   192 slots      queued   0 jobs /     0 slots
NON-CRIT   running 218 jobs / 1,744 slots      queued  70 jobs /   560 slots
=> 90% of the slots we are running are on work that CANNOT raise the result
=> and ZERO critical jobs are queued
```

**STEP 3 — THE ANSWER, AND IT FOLLOWS DIRECTLY.** **Not one job on the critical path is waiting for
a slot.** Every capping arm's work is executing right now. **Therefore no reallocation of slots can
shorten the ETA**: adding capacity to a path with nothing queued on it does nothing, and the 1,744
non-critical slots could be freed entirely without moving the result by a minute. The
earliest-submitted critical queued job does not exist, so the "our own jobs are blocking our
critical path" hypothesis is **REFUTED by measurement**, not assumed away.

**STEP 4 — WHAT THE REMAINING TIME IS MADE OF, and every term is frozen.**

| line | what is running now | then | ETA to rung 30 |
|---|---|---|---|
| glm (`leg2`) | **h2_pair, 8 jobs** — the capping work itself | — | **~9.4 h** |
| kimi (`leg10`) | **h2_pair, 5 jobs** — the capping work itself | — | **~9.4 h** |
| nemotron (`leg7`) | `scalar_cvar5_test`, 4 jobs | then submit h2_pair | ~19 h |
| deepseek (`leg1`) | `placebo_shuffled_test`, 1 job | then submit h2_pair | ~19 h |
| **core (`c1`)** | **the serial C1 DFO chain** (`bayes_opt` owes 3 of 30) | then C2 `h2_pair` | **~23 h** |

**⇒ THE COMMON RUNG REACHES 30 IN ROUGHLY 23 HOURS, AND CORE IS THE BINDING TERM.** Both components
are immovable: the DFO chain is serial **by construction** (each proposal is a function of fitnesses
already observed), and the sealed-test training wall is **9.39 h measured**, being 400,000 frozen
steps at ~13 steps/s on one thread. Cutting either means changing a pre-registered value or the
thread count, and the second changes floating-point reduction order and destroys CRN determinism.

**⚠ ONE FUTURE DELAY WAS CHECKED AND IS NOT REAL.** When core finishes C1 it will SUBMIT its
`h2_pair`, and that job will be newer than `leg4`'s **68 queued jobs / 544 slots** — which are
non-critical (qwen3.5-9b already banks 100). Since SGE orders one user's jobs by submit time, that
looked like a foreseeable self-inflicted delay on the critical path. **Measured instead of assumed:
243 jobs are running at a 9.4 h mean wall, so jobs complete at ~26/h and the 68-job queue drains in
~2.6 h — roughly ten times sooner than core needs the slots.** No action is owed, and taking one
(holding another line's jobs) would cost real science for no gain.

**⇒ THE STANDING CONCLUSION, NOW EVIDENCED AT JOB GRANULARITY: THE ETA IS AT ITS GLOBAL MINIMUM
UNDER THE FROZEN DESIGN. The only remaining lever is the human one — asking UCL RC for a larger
allocation — and even that cannot help, because the critical path is not slot-starved.**

### ⛔ WHAT IS CLOSED, AND MUST NOT BE RE-LITIGATED EVERY THIRTY MINUTES

The cores question is **closed by fourteen independent measurements** (no quota, no job cap, no PE
cap, no memory constraint, no `snx` constraint, zero `Eqw`, one host group, jobs schedulable,
`qalter -p` up is operator-only, `js` refused). It is **functional fair-share by user, and nothing we
control changes it.** The only remaining lever is a human request to UCL RC, which is Tamer's call.
**Re-open it ONLY if a measurement changes** — a new `Eqw`, a quota appearing, a PE change. Do not
re-run the closed fourteen every pass; that burns the very wall-clock this section exists to protect.

Likewise closed: 400k steps is FROZEN, warm-start breaks determinism, more threads change FP
reduction order and corrupt H4 mid-chain, and re-packing needs a twelve-line teardown that costs
more than it saves. **Never trade correctness, CRN determinism or the frozen design for speed.**

### ★★★★★ 2026-08-04 21:04 UTC — TAMER: "MAKE SURE WE GET THE MAXIMUM CORES POSSIBLE, WE FELL VERY
### BADLY". RE-MEASURED FROM THE SCHEDULER RATHER THAN RE-ARGUED, AND IT SUPERSEDES THE OLD POSITION

**THE OLD POSITION WAS "CORES ARE CLOSED BY FOURTEEN MEASUREMENTS". THAT WAS TRUE WHEN OUR QUEUE WAS
EMPTY AND IS NOT THE RIGHT TEST NOW.** With 1,024 slots QUEUED for the first time this session,
placement throughput matters again. So it was measured properly, with the project's own instrument.

**WHAT OUR JOBS ACTUALLY REQUEST** (`qstat -j` on a live queued job, verbatim):
`snx=1, tmpfs=1G, memory=2G, batch=true, h_rt=54000, hostname=!node-d00a-230&!node-d00b-024`,
`parallel environment: smp-[D]* range: 8`, `allocation_rule $pe_slots` (all 8 slots on ONE host),
and `smp-D` is configured with **10,476 slots**.

⚠ **AND A MEASUREMENT I GOT WRONG FIRST AND HAD TO REDO — RECORDED BECAUSE THE ERROR IS INSTRUCTIVE.**
My first `qhost` parse summed columns 5 and 6, which are **NCOR and NTHR — both static hardware
counts** — so every family showed "load == ncpu" and I nearly reported the cluster as 100% full. The
real columns are `$3 = NCPU` and `$7 = LOAD`. Corrected, the D family is **32-92% FREE by load**.
A column index is a measurement, and it deserves the same check as any other.

**THE AUTHORITATIVE FIGURE — `docs/ops/placeable_capacity.py`, fed `qhost -F slots,memory,tmpfs` and
`qstat -f` exactly as the tool instructs** (its own guard refused the first, complex-less input rather
than silently treating unknown as zero, which is the behaviour that file was built for):

| pack width | placeable CORES cluster-wide |
|---|---:|
| **8 (current)** | **2,256** |
| 4 | 2,644 |
| 2 | 2,772 |
| 1 | 2,863 |

**Per pool at pack 8:** `d00a` **1,432** · `e00a` 328 · `d00b` 224 · `t00a` 104 · `l00a` 80 ·
`e96a` 32 · `d97a` 16 · `d97b` 16 · rest 24. **Our reachable `smp-D` pool holds 1,688 of those
2,256 placeable cores**, and we already hold 1,008 running with ~1,024 more queued to take them.

⇒ **WE DID NOT "FALL" THROUGH ANY MISCONFIGURATION. We reach the overwhelming majority of what is
placeable, and the queued work is sized to consume it.** The trough was the sawtooth, and it is
refilling.

### ⭐ THE ONE GENUINE, SCIENCE-SAFE LEVER, AND IT IS TAMER'S DECISION

**PACK WIDTH. Worth +17% at pack 4 (2,256 -> 2,644 cores) or +27% at pack 1 (-> 2,863).**
The mechanism is visible in the same table: **`strand` = 441 free slots on `d00a` alone** — cores
that are free but sit on hosts holding fewer than one full 8-pack, so at our width they are real and
unusable. Narrowing the pack recovers them.

⭐ **AND IT DOES NOT TOUCH THE DETERMINISM ENVELOPE, WHICH IS THE ONLY REASON IT IS EVEN ARGUABLE.**
Every training is **1-thread** whatever the pack width; a pack is a PACKAGING of independent
1-thread trainings onto one host under `allocation_rule $pe_slots`. Reduction order, seeding and CRN
pairing are per `(arm, seed)` and are untouched. This is not the AMD/Intel question and it is not the
thread-count question — **both of those remain firmly closed.**

⛔ **WHAT IT COSTS, STATED SO THE DECISION IS INFORMED RATHER THAN SOLD:**
1. **A rolling supervisor restart across ten live driver lines.** A stale `.driver.lock` from an
   unclean stop has already cost this campaign **4.5 h**.
2. **Job count.** A 2,690-unit tier is ~336 jobs at pack 8 and **2,690 at pack 1**. The registered
   1,000-job working cap makes pack 1 unattractive; **pack 4 is the defensible middle** (~672 jobs).
3. It also **shortens the tail** that caused today's trough, because a tier's last surviving pack
   becomes 4 trainings instead of 8.

**RECOMMENDATION: pack 4, and only at a natural restart boundary — not mid-tier.** +17% placeable
cores, halves the tail, no determinism exposure. **NOT actioned unilaterally**: the ledger's own
standing note says pack 8 was deliberately applied on 2026-07-31 and the supervisors must not be
restarted for it, so reversing that is a decision, not a reflex.

⛔ **AND THE LEVERS THAT REMAIN CLOSED, with the reason restated so nobody re-opens them:**
`e00a` (+328 cores) and `t00a` (+104) are OUTSIDE `smp-D` — a different node family breaks the
CRN homogeneity every paired contrast rests on, and `t00a` is AMD, which the determinism envelope
excludes by name. **15 blocked hosts on `d00a`** are disabled or in alarm and are UCL RC's to clear.
Self-elevating fair share is operator-only; lowering our own priority is a standing prohibition.

### ⛔⛔ 2026-08-04 21:52 UTC (RUN 22 pass 1) — **PACK 4 IS REFUTED AT THE SCHEDULER. DO NOT ROLL IT.**
### AND THE HANDOVER BRIEF'S JOB ARITHMETIC WAS WRONG IN THE DANGEROUS DIRECTION.

**The RUN 22 brief hands this session an executable pack-4 procedure and calls ~672 jobs "the
defensible middle" against "a registered 1,000-job working cap". I went to measure the cap rather
than quote it, and the lever does not survive the measurement.**

| fact | measured value | how |
|---|---|---|
| `max_u_jobs` (global config) | **1000** | `qconf -sconf global` |
| `maxujobs` (scheduler config) | **1000** | `qconf -ssconf` |
| our live job count | **563, and climbing** (546 three minutes earlier) | `qstat -u ucestes -xml` |
| `schedule_interval` | **0:10:0** | `qconf -ssconf` |
| `Eqw` / `hqw` | **0 / 0** | `qstat -u ucestes` census |
| `qquota -u ucestes` | **EMPTY** | no quota applies to us |

**FINDING 1 — THE 672 FIGURE IS PER-TIER; THE CAP IS PER-USER ACROSS EVERY TIER OF EVERY LINE.**
The brief computed ~672 jobs for ONE 2,690-unit tier. The live fleet-wide count at pack 8 is **563**
and rising as drivers submit. The same work at pack 4 is **~1,126 jobs — OVER a HARD 1,000 cap.**
Drivers submit whole tiers rather than a metered buffer, so they would drive us into the cap and
`qsub` would begin FAILING on a live, irreplaceable campaign. That is not a cost to weigh against
+17%; it is a submission-failure mode.

**FINDING 2 — AND IT INVERTS THE RECOMMENDATION. UNDER A PER-*JOB* CAP, A WIDER PACK IS STRICTLY
BETTER.** `src/cluster/lanes.py:290` already states it: *"SGE's `maxujobs = 1000` at 8 cores/job
structurally permits ~**8,000** cores"*. At pack 4 that structural ceiling **HALVES to 4,000**. The
placeable-core table prices only the numerator (what the cluster can accept) and is silent on the
denominator (how many jobs we are allowed to express it in). **Pack 8 is not a legacy setting to be
reversed; it is the setting that maximises slots per unit of the scarce resource.**

**FINDING 3 — PLACEMENT IS NOT WHAT BINDS TONIGHT ANYWAY.** `schedule_interval` is **ten minutes**,
which explains the dispatch curve exactly: held slots rise in bursts (`1,144 → 1,160 → 1,184 → 1,192`
over 9 min) rather than continuously. We were reading a scheduling cadence as a capacity ceiling.

⇒ **THE PACK-WIDTH QUESTION IS CLOSED AGAINST ACTION, ON MEASUREMENT RATHER THAN ON CAUTION.**
`placeable_capacity` at pack 4 shows a real +340 cores in `smp-D` (1,592 → 1,932, re-measured 21:35Z
this session, d00a 1,368→1,680 and d00b 224→252), and that gain is **unreachable**: we cannot express
it in jobs. ⚠ Re-open ONLY if `max_u_jobs` changes or a driver gains metered submission.

### ⭐ WHAT IS ACTUALLY LEFT ON THE ETA, AND IT IS NOT CORES — the falsifiable rule for the next pass

**The ladder is genuinely at RISK and that part of the brief is right.** `stage_eta` 21:40Z: rung 568
`remaining 27,335 · earliest 08-10 20:43 · latest 2026-08-28 06:23 · Aug-27? **risk**`. Making the
stop needs **51.6 rec/h** sustained; the post-handover branch estimates **49**. We hold ~1,190 cores
against `cpu_saturation_cores` **~3,235**, so cores DO still help — `lanes.py` says *"PUSH FOR IT:
every core up to ~3,235 shortens the campaign"*.

**THE BINDING MECHANISM IS THE TIER TAIL, MEASURED PER JOB THIS PASS.** `qwen3_6-27b` owes 2,571
units. Its tiers t2/t3/t4/t6 hold **1,927 pending units behind EIGHT straggler jobs** (t2 3r, t3 1Rr,
t4 1Rr+1r, t6 2r), because `driver.py:550-553` requeues a tier only when NO job of it is alive. That
is 75% of a line's owed work held hostage by 8 packs. The repair is in **drift-fenced** `src/`, and
`qdel`-ing a straggler to force the drain is a standing prohibition.

**⇒ THE DECISION RULE, SO THE NEXT PASS EXECUTES INSTEAD OF RE-ARGUING:**
1. Record held slots every pass. **Three consecutive passes** plateaued below ~1,900 while our own
   queue holds >1,000 slots is the signature that something other than the sawtooth binds → measure
   `placeable_capacity --pack 8` against what we hold and name the gap before proposing anything.
2. If held slots climb past ~2,400 with the queue deep, we are absorbing capacity and there is
   nothing to fix — **say so with the number and close it.**
3. **Never** propose a pack change without re-reading `max_u_jobs` and our live job count in the
   same breath. The two numbers are one constraint and quoting either alone is how this was nearly
   actioned.

### ⛔⛔⛔ 2026-08-04 22:35 UTC (RUN 22 pass 2) — **WE ARE HARD AGAINST `max_u_jobs=1000` AND `qsub`
### IS BEING REJECTED LIVE. IT IS BENIGN, IT IS BOUNDED, AND IT SETTLES THE PACK QUESTION FOR GOOD.**

**MEASURED, not inferred:**
```
our live job count ......... 994        max_u_jobs ......... 1000   (6 jobs of headroom)
994 jobs x 8 slots ......... 7,952      running 1,296 + queued 6,656 = 7,952   <- exactly
```
**AND IT IS ALREADY FIRING.** `glm-5_2` entered C4 at 22:24:35Z and its very next act was six rejected
submissions, one per sweep tier, at 22:30:00-22:30:12Z:
`[leg2_leg_glm_5_2_sweep_t6] queue op failed (1 consecutive, 0 min): ... 'qsub ...' returned non-zero
exit status 25.`

**WHY IT IS BENIGN, AND EVERY TERM WAS READ FROM THE CODE RATHER THAN ASSUMED.** A failed `qsub`
raises `CalledProcessError`, which is inside `_TRANSPORT_ERRORS` (`driver.py:47`), so `driver.py:639`
treats it as a blip and retries on the next poll. Fatal only via `_outage_is_fatal`, whose bounds are
`max_consecutive_errors` = **240** (`campaign.py:183`, overriding the module default of 72) at
`poll_secs` 180 = **12 h**, or `max_transport_outage_secs` = **12 h**. ⭐ **The counter resets to zero
on the FIRST success**, and with ~160 jobs running at a 9.39 h mean wall about **17 job-slots free
every hour**, so a line cannot accumulate 12 continuous hours of rejection. **Nothing dies.**

**AND IT COSTS NO THROUGHPUT AT ALL, WHICH IS THE PART THAT MATTERS.** Fair share holds us at ~1,296
RUNNING slots while 6,656 sit queued — **the queue is already five times deeper than anything we can
run.** Being unable to enqueue MORE work changes our record rate by nothing.

⇒ **⭐⭐ AND THIS IS THE STRONGEST POSSIBLE VINDICATION OF NOT ROLLING PACK 4, MEASURED RATHER THAN
ARGUED.** The structural ceiling is `1,000 jobs x pack`, so:
```
pack 8 (current) ... 1,000 jobs express 8,000 slots   we hold 7,952 of them   <- fits
pack 4 ............. the SAME 7,952 slots need 1,988 jobs   = 2x the HARD cap  <- IMPOSSIBLE
```
**At pack 4 we could express only 4,000 slots — HALF the work we are holding right now.** The RUN 22
brief's starred recommendation would have cut our maximum expressible work in half at the exact hour
we came up against the cap. **Pack width is closed, on a third independent measurement.**

⚠ **THE ONE REAL COST IS ORDERING, AND IT IS A WATCH, NOT A FINDING.** SGE orders one user's jobs by
submit time, so glm's C4 sweep enters behind kimi's 340 and haiku's 228. All three are laggard lines
and the common rung is a MINIMUM, so this changes WHICH laggard climbs first, not whether they climb.
**Record it; do not act on it.** `qdel` to make room is a standing prohibition and would destroy up
to 8 in-flight trainings per job.

### SPEED LOG (append one row per pass, newest last)

| when (UTC) | rec/h 12h | rec/h 24h | slots | run/queue | 1-line % | chain owed | rung 30 | rung 403 | rung 568 |
|---|---:|---:|---:|---|---:|---|---|---|---|
| 2026-08-04 00:10 | 153 | 195.8 | 1,632 | 204/314 | 82% (qwen3.5-9b) | tpe 5, bayes_opt 4 | 08-04 02:46 | 08-09 18:59 | 08-12 11:38 |
| 2026-08-04 00:50 | 150.2 | 191.0 | 1,600 | 200/288 | 90% (qwen3.5-9b) | tpe 5, bayes_opt 3, **cma_es DONE** | 08-04 23:01 | 08-09 23:48 | 08-12 18:37 |
| 2026-08-04 01:15 | 145.4 | 187.5 | **1,712** | 214/265 | 93% (qwen3.5-9b) | tpe 5, bayes_opt 3 | 08-04 23:25 | 08-10 02:44 | 08-12 22:52 |
| 2026-08-04 01:40 | 141.9 | 185.8 | 1,696 | 212/260 | 97% (qwen3.5-9b) | tpe 5, bayes_opt 3 | 08-04 23:56 | 08-10 06:29 | 08-13 04:18 |
| 2026-08-04 02:10 | 141.7 | 182.8 | 1,696 | 212/253 | 98% (qwen3.5-9b) | tpe 5, bayes_opt 3 | 08-05 00:25 | 08-10 06:48 | 08-13 04:44 |
| 2026-08-04 08:20 | **169.4** | 182.0 | **1,904** | 235/199 | **67%** (qwen3.5-9b) | tpe **4**, bayes_opt 3 | 08-05 02:12 | **08-09 08:03** | **08-11 17:15** |
| 2026-08-04 08:40 | **171.2** | 180.8 | 1,896 | 237/185 | **64%** (qwen3.5-9b) | tpe **3**, bayes_opt 3 | 08-04 22:01 | **08-09 06:41** | **08-11 15:18** |
| 2026-08-04 09:20 | **175.8** | 174.8 | **1,904** | 238/159 | **56%** (qwen3.5-9b) | bayes_opt 3 | 08-04 22:44 | **08-09 03:14** | **08-11 10:21** |
| 2026-08-04 09:55 | **179.3** | 172.9 | 1,848 | 231/149 | **51%** (qwen3.5-9b) | bayes_opt 3 | 08-04 22:5x | **08-09 00:44** | **08-11 06:46** |
| 2026-08-04 10:50 | 174.2 | 171.5 | 1,752 | 219/134 | 57% (**sonnet-5** now leads) | bayes_opt 3 | -- | 08-09 04:00 | 08-11 11:39 |
| 2026-08-04 11:20 | 168.1 (2h inst **197.5**) | 170 | 1,768 | 221/128 | 63% (sonnet-5) | bayes_opt 3 | -- | 08-09 08:13 | 08-11 17:52 |
| 2026-08-04 12:00 | 164.7 (3h inst 195.0) | 159.0 | **2,018** | 242/90 | 70% (sonnet-5) | bayes_opt 3 | 08-05 01:19 | 08-09 10:39 | 08-11 21:30 |
| 2026-08-04 12:13 | 161.8 (1h **118**) | 156.9 | n/a OUTAGE | n/a OUTAGE | 71% (sonnet-5) | bayes_opt 3 | 08-05 01:34 | 08-09 13:01 | 08-12 00:56 |
| 2026-08-04 12:41 **POST-RECOVERY** | **165.1** | 157.4 | 2,015 | 243/71 | 75% (sonnet-5) | bayes_opt 3 | -- | -- | -- |
| 2026-08-04 12:52 | **167.1** (1h 153) | 157.7 | 2,014 | 243/68 | 76% (sonnet-5) | bayes_opt 3 | -- | -- | -- |
| 2026-08-04 13:18 | **171.8** (1h **185**) | 158.6 | 1,896 | 228/70 | 78% (sonnet-5) | **bayes_opt 2** | -- | -- | -- |
| 2026-08-04 13:43 | 172.6 | 157.3 | 1,848 | 222/70 | 80% (sonnet-5) | bayes_opt 2 | -- | -- | -- |
| 2026-08-04 14:10 | **174.5** | 158.2 | 1,867 | 226/57 | 83% (sonnet-5) | bayes_opt 2 | -- | -- | -- |
| 2026-08-04 14:43 | **178.8** | 160.3 | **1,925** | 236/35 | 87% (sonnet-5) | bayes_opt 2 | -- | -- | -- |
| 2026-08-04 14:46 | **179.1** | 160.6 | 1,929 | 237/**31** | 87% (sonnet-5) | bayes_opt 2, tpe 2 | -- | -- | -- |
| 2026-08-04 15:09 | **179.7** | **162.7** | 1,864 | 229/30 | 90% (sonnet-5) | bayes_opt 2, tpe 2 | -- | -- | -- |
| 2026-08-04 15:42 | **180.3** | **164.9** | 1,868 | 231/**18** | 94% (sonnet-5) | bayes_opt 2, tpe 2 | -- | -- | -- |
| 2026-08-04 16:14 **RUN 21 pass 1** | **183.2** | **165.6** | 1,848 | 231/**3** | 96% (sonnet-5) | bayes_opt 2, tpe 2 | 08-05 ~11:00 (chain-aware, see below) | 08-09 00:15 | 08-11 03:44 |
| 2026-08-04 17:42 **RUN 21 pass 2** | **191.2** | **171.2** | 1,664 | 210/**0** | **100%** (sonnet-5) | bayes_opt 2, tpe 2 | GATED | GATED | GATED |
| 2026-08-04 19:15 **RUN 21 pass 4** | **200.4** | **180.8** | **1,248** | 158/**0** | 96% (sonnet-5) | bayes_opt 2, tpe 2 | GATED | GATED | GATED |
| 2026-08-04 19:54 **RUN 21 pass 5** | **198.9** | **180.9** | **1,096** | 139/**0** | 92% (sonnet-5) | **bayes_opt 1**, tpe 2 | GATED | GATED | GATED |
| 2026-08-04 20:27 **RUN 21 pass 6** | 193.6 | **182.0** | **984** | 125/**0** | **86%** (sonnet-5) | bayes_opt 1, tpe 1 | GATED | GATED | GATED |
| 2026-08-04 20:55 **RUN 21 pass 7** | 193.6 | 182.0 | 960 | 122/**110** | 86% (sonnet-5) | bayes_opt 1, tpe 1 | GATED | GATED | GATED |
| 2026-08-04 21:56 **RUN 22 pass 1** | **191.1** | **184.8** | **1,184** | 148/**469 (3,752 slots)** | 74% (sonnet-5) | bayes_opt 1, tpe 1 | 08-05 02:07 | 08-08 22:34 | **08-10 20:43 / 08-28 06:23 `risk`** |
| 2026-08-04 22:35 **RUN 22 pass 2** | 182.2 | 179.6 | **1,296** | 162/**832 (6,656 slots)** | 69% (sonnet-5) | ⭐ **bayes_opt DONE, tpe 1** | GATED | GATED | GATED (barrier) |
| 2026-08-04 23:04 **RUN 22 pass 3** | **186.4** | 179.3 | 1,288 | 161/**833 (6,664 slots)** | **65%** (sonnet-5) | ⭐⭐ **ZERO — THE C1 CHAIN IS CLOSED** | GATED | GATED | GATED (barrier) |
| 2026-08-04 23:22 **RUN 22 pass 4** | **188.0** | 178.0 | **1,312** | 989 jobs total | **62%** (sonnet-5) | ZERO (chain closed) | GATED | GATED | GATED (barrier) |
| 2026-08-04 23:54 **RUN 22 pass 5** | 187.6 | 176.5 | **1,376** | 975 jobs total | **58%** (sonnet-5) | ZERO (chain closed) | GATED | GATED | GATED (barrier) |
| 2026-08-05 07:30 **RUN 23 pass 1** | 138.1 (1h 207) | 168.9 | **1,608** | 926 jobs total | **43%** (haiku-4.5) | ZERO (chain closed) | GATED | GATED | GATED (barrier) |
| 2026-08-05 20:15 **RUN 23 pass 2** | **153.5** | 149.8 | **920** | 115/**708 (5,664 slots)** | **81%** (haiku-4.5) | ZERO (chain closed) | ⭐ **08-05 21:26** | ⭐ **08-10 07:34** | ⭐⭐ **08-12 08:58** |
| 2026-08-05 21:30 **RUN 23 pass 3** | 143.8 | 143.0 | **976** | 123/**687 (5,496 slots)** | ⚠ **92%** (haiku-4.5) | ZERO (chain closed) | ⛔ 08-05 22:35 / 23:15 **— SEE BELOW, THIS DATE IS NOT REACHABLE** | 08-10 15:55 / 08-13 10:26 | 08-12 19:52 / 08-16 20:33 |
| 2026-08-05 21:35 **RUN 23 pass 4** | (12 h window unchanged) | — | **984** | 802 jobs, Eqw/hqw **0** | 92% (haiku, **7 records from 568**) | ZERO (chain closed) | ⛔ **08-08 → 08-10, NOT the tool's date** — see the queue-order row | — | — |
| 2026-08-05 22:10 **RUN 23 pass 5** | 146.5 | 145.1 | **928** | 116/**679**, Eqw/hqw **0**, 795 jobs vs cap 1000 | ⚠⚠ **91%** (haiku, and **91% of the window is from cells within 8 of 568 — that rate STOPS**) | ZERO (chain closed) | ⛔ **10-12 Aug** (retracted twice; see the queue row) | — | — |

**⚠ PASS-5 SPEED VERDICT, AND IT CONTAINS A FALSIFIABLE PREDICTION FOR THE NEXT PASS.** The headline
`146.5 rec/h` is **not sustainable and the tool says so**: *"91% of the 12 h window came from cell(s)
now within 8 records of rung 568."* Haiku is finishing within hours. ⚠ **But the naive inference —
that the fleet is about to fall to ~13 rec/h — is almost certainly WRONG, and stating it would be
the same over-reading I have already had to retract once today.** Kimi ramped from 344 to **576
running slots in the last two hours**, and a pack-8 job runs 9-15 h, so **kimi's output has not landed
in the 12 h window yet.** ⇒ **PREDICTION TO CHECK NEXT PASS: haiku's contribution goes to zero and
kimi's arrives in a burst, so the 12 h rate dips and then recovers. If it dips and STAYS down while
kimi holds 576 slots, that is a real finding and not a handover artefact.**

**THE FOUR QUESTIONS.** (1) **Holding every core we could?** `occupancy_watch`: every line
proportionate; 928 running against **679 queued jobs (~5,400 slots)** — a deep queue with a flat
total is fair share, stated with the number, and §6 is not re-opened. (2) **Anything newly
schedulable?** `Eqw` 0 · `hqw` 0 · `qquota` empty · **795 jobs against `max_u_jobs` 1000, so 205 of
headroom and the cap is NOT binding** — read in the same breath, as the contract requires.
(3) **Any core on work that cannot raise the rung?** Yes, and it is the whole story: **91% of
production is haiku, which banks 189 against a common rung of 0.** (4) **Ladder depth by 27 Aug, and
did it move?** It moved, LATER — see the retraction above. Not unmoved, so not an open finding on
that criterion.

**PASS 5 SPEED VERDICT — SLOTS AT A SESSION HIGH AND CONCENTRATION STILL FALLING.** Slots **1,376**
(1,184 -> 1,296 -> 1,312 -> 1,376 across the four passes), **16.7% of the cluster's 8,218 running
slots**, `Eqw`/`hqw` **0**, jobs 975 so the cap has eased further. Concentration on the one line above
the common rung has now fallen **74% -> 69% -> 65% -> 62% -> 58%**. Remaining-to-568 **27,068 ->
26,986**. Chain owed ZERO for a third consecutive pass.

### ⭐⭐ 2026-08-05 20:15 UTC (RUN 23 pass 2) — TAMER ASKED "WHY DID WE DOWNGRADE THE RECORDS AND THE
### CORES SO MUCH". THE RECORDS DID NOT MOVE DOWN AT ALL; THE CORES DID, FOR TWO MEASURED REASONS.

**Answered from the scheduler and the archive, not from this ledger's standing position, because
the question deserves a fresh measurement every time it is asked.**

**(1) RECORDS DID NOT FALL. 15,750 at 07:39Z, 17,780 at 20:03Z — monotone, +2,030 in 12.4 h.** What
fell is the SHORT window and only the short window: 1 h reads **85–105 rec/h** against 207 this
morning, while **12 h reads 153.5 against 138.1 (UP)** and 24 h reads 149.8 against 168.9 (−11%).
The arrival quantum is a 15 h pack-8 job, so the tool's own caption applies: *windows under 12 h are
a STALL INDICATOR ONLY and do not price the ETA.* On the windows that price the ETA we are flat.

**(2) CORES FELL 1,608 → 920, AND IT IS A HANDOVER PLUS FAIR SHARE.**

* **haiku drained.** It climbed **30 → 530-535 of 568** overnight and its queue is down to **ONE
  job**. It was holding ~1,200 slots and producing 43-81% of all records. A line that finishes stops
  consuming, and there is no version of this campaign in which that does not happen to every line.
* **Fair share compressed our share; the CLUSTER DID NOT SHRINK.** Cluster running slots
  **8,446 → 8,321 (−1.5%)**, our share **19.0% → 11.1%**. Per user:
  `ucbtjji 1,208 (was 1,408) · ucestes 920 (was 1,232) · ucecgwh 855 (NEW in the top three) ·
  uctpec1 768 (was 1,020)`, then a long tail at 524, 464, 348, 270, 234, 208, 197, 184. **Every large
  user is down and mid-size users arrived.** Same mechanism as 2026-08-04, re-measured not re-argued.

**(3) NOTHING OF OURS IS STUCK, AND THE TWO IDLE LINES WERE PROBED DIRECTLY RATHER THAN ASSUMED
BENIGN.** `Eqw` 0 · `hqw` 0 · `qquota` EMPTY · 708 jobs queued (~5,664 slots, a deep queue) · 823
jobs against the 1,000 cap, so the cap is NOT binding today. Our 920 slots sit on kimi 344,
qwen3.6-27b 304, haiku 208, nemotron 64, while **glm (157 jobs) and deepseek (165 jobs) hold ZERO
running.** `qalter -w p` on glm job **91245** and deepseek job **94017** both return
**"found possible assignment with 8 slots"** — schedulable, waiting on fair share, not blocked.
⇒ **PREDICTION TO CHECK NEXT PASS: as kimi and haiku jobs end, leg1 and leg2 start.** If they do not,
that IS a finding.

**(4) ⭐ AND THE ANSWER THE QUESTION WAS REALLY ABOUT: THE LADDER MOVED, HARD, IN THE RIGHT
DIRECTION.** Every rung read **GATED (barrier)** this morning. `stage_eta` now dates **rung 30 to
2026-08-05 21:26**, **rung 403 to 08-10 07:34** and **rung 568 to 08-12 08:58** — fifteen days inside
the 27 August stop. ⚠ Carry the tool's own caveats with those dates: **81% of the rung-568 backlog
sits on cells that produced NOTHING in the 12 h window**, so it is behind a stage barrier that cores
do not accelerate, and **2 registered units have no directory yet** and cannot be in the rate's
denominator, which makes both columns optimistic by that share.

⚠ **THE HONEST COST, STATED BECAUSE IT IS THE THING THAT ACTUALLY BINDS THE GRADE.** The reported
result is the COMMON rung, a MINIMUM. haiku going 30 → 535 raised it by **ZERO**. Today's binding
constraints are **core at 0** (its `h2_pair` has not started) and **glm / kimi / deepseek at 30**.
About **81% of the last 12 h of production landed above the common rung.** That is §11.2 question 3
answered with its number, and it is NOT actionable from here: steering which line SGE runs would
need a `qdel` or a held-back submission, and both are standing prohibitions.

### ⭐⭐ 2026-08-05 22:10 UTC (RUN 23 pass 5) — **NINE ARCHIVE WALKERS, AT LEAST FIVE DIFFERENT
### EXCLUSION RULES. PROVEN-BENIGN TODAY BY MEASUREMENT — AND IT KILLS MY OWN PASS-4 PLAN.**

**I set out to extend the record cache to the three layers pass 4 registered as "unambiguously
shrink-safe" and READ THEM FIRST. None of the three is a drop-in, and the blocker is not the shrink
at all — it is the WALK. Every layer carries its own exclusion rule and they do not agree:**

| walker | rule |
|---|---|
| `record_shrink_cache` (+ `science_watch`, `results_audit`) | `.pull_tmp*` **or** `_quarantined*`, per segment, relative to root |
| `record_validator:231` | `.pull_tmp` on the **FIRST segment only**, plus `"_env" in parts`. **No `_quarantined`.** |
| `record_provenance_seal:134` | `".pull_tmp" in s or "_quarantined" in s` — **substring over the whole path** |
| `record_science_audit:344` · `fed_text_identification:109` · `fed_value_coherence:137` · `reward_code_audit:133` | any **dot-prefixed** segment **+ `_is_d18_nested`**. **No `_quarantined`.** |
| `record_window_identity:74` | `".pull_tmp" in dirpath` substring over `os.walk`. **No `_quarantined`, no D18.** |

**MEASURED WHETHER ANY OF IT BITES TODAY, rather than asserting either way:**
```
_quarantined*  : 0 directories, 0 records   -> the four layers omitting the rule are LATENTLY
                                               inconsistent, not wrong. Nothing to exclude.
.pull_tmp*     : 2 directories, 3 records   -> ALL THREE sit at the FIRST segment, so
                                               record_validator's narrower rule excludes them
                                               IDENTICALLY to the any-segment rule. Verified per record.
_env           : 69 directories, 0 records  -> record_validator's unique rule excludes nothing today.
D18-nested     : 2 records  (glm_5_2/placebo_shuffled/...-g3-c4/...-g3-c4/ and
                             haiku_4_5/scalar/scalar-g1-c3/scalar-g1-c3/)
```
⇒ **THE ONLY LIVE DIFFERENCE IS TWO D18-NESTED DUPLICATES**, admitted by `science_watch`,
`results_audit` and the cache, excluded by four layers. **Both admitting tools already KNOW and SAY
so** — `science_watch` prints the term explicitly in its reconciliation line
(*"+ N deeper-nested duplicate(s)"*) and `results_audit`'s duplicate check carries the D18 note. So
this is documented behaviour, not a silent divergence. **TERMINAL STATE: PROVEN-BENIGN, with the
measurement; REGISTERED as latent, because the moment a `_quarantined*` tree appears the four layers
that lack the rule will certify an earlier run's records as part of this campaign.**

⚠ **AND IT CORRECTS MY OWN PASS-4 REGISTRATION.** That row said four layers were "unambiguously
shrink-safe" and implied a drop-in. **Shrink-safety was the wrong question.** The real prerequisite is
that `load_shrunken_records` grow an optional per-caller `exclude` predicate (and preserve each
caller's ordering — two layers use `sorted(root.rglob(...))`, not raw walk order), so every layer
keeps its OWN rule instead of silently inheriting mine. **That is a real API change on the path that
certifies an irreplaceable archive, and it needs its own byte-identity proof per layer.**
⛔ **DELIBERATELY NOT SHIPPED AT THE END OF THIS PASS.** Rushing a third same-day change into a
certification path without its proof is the exact pattern this ledger keeps paying for, and I have
already caught myself doing a version of it twice today.

### ⛔⛔ 2026-08-05 22:05 UTC (RUN 23 pass 5) — **I RETRACT THE "CORE STARTS IN ~19 h" FIGURE. THE
### RATE IT RESTED ON WAS ONE 38-MINUTE WINDOW AND IT DID NOT HOLD. THE HONEST ANSWER IS 2-4 DAYS.**

**MEASURED, three points now instead of two:**
```
jobs ahead of core bayes_opt   276 (20:53Z)  ->  267 (21:32Z)  ->  268 (22:04Z)
jobs ahead of core tpe         445           ->  445           ->  443
kimi pending                   276           ->  268           ->  268   (FLAT for 31 min)
our running slots              976           ->  984           ->  928
core state                     8 qw          ->  8 qw          ->  8 qw
```
**Over the full 71-minute baseline the queue ahead of core fell by 8 jobs = 6.8 jobs/h. Over the most
recent 31 minutes it did not fall at all.** My pass-4 figure of 14.2 jobs/h was fitted to a single
38-minute window and is withdrawn; **6.8 jobs/h is the number with a baseline behind it, and it
roughly doubles every date I have given.**

⚠ **AND THE MECHANISM I HAD NOT SEEN: KIMI'S DRIVER IS ACTIVELY REPLENISHING.** Newest submission
per line, host-local **+0100** (so 22:01:26 local = **21:01:26 UTC**):
```
leg10 kimi   08/05 22:01:26  <-- SUBMITTING RIGHT NOW; pending flat at 268 while jobs START
leg3  qwen   08/05 15:47:38     leg5 haiku 08/05 14:51:33     leg7 nemotron 08/05 14:15:50
leg1  deepseek 08/05 11:49:52   leg2 glm   08/04 23:29:59     c1 core 08/05 00:01:26
```
Kimi's pending set is a ROLLING WINDOW, not a draining stack. ⚠ **It is NOT unbounded, and that is
the reassuring half: `occupancy_watch` puts kimi's total owed at 2,690 units against 268 queued + 72
running jobs, i.e. it is holding essentially its whole remaining tier.** So it drains — at 6.8 jobs/h
that is **~39 h for core's `bayes_opt`** and, adding glm's 157 and qwen3.6's 13 which both outrank
core's `tpe`, **~65 h for `tpe`.** Core's C1 stage therefore completes around **2026-08-08 late**, and
its `h2_pair` pays a further drain after that.

⇒ **HONEST RANGE FOR THE COMMON RUNG TO LEAVE 0: about 10-12 August.** Two routes agree — the
observed 6.8 jobs/h, and kimi+glm's ~5,380 owed units against the fleet's realised throughput.

⚠⚠ **AND THE PATTERN IN MY OWN ESTIMATES IS ITSELF THE FINDING, SO IT IS WRITTEN DOWN RATHER THAN
QUIETLY UPDATED. Across three passes I have said 07 Aug, then 08-10 Aug, then 10-12 Aug — LATER EVERY
TIME, and every revision came from discovering one more queue term I had not counted** (first the
second stage transition, then the per-tier priority split, now the replenishment). **The lesson is
not that the campaign is slipping; it is that a queue-position estimate built from one short window
is worth very little, and I should have given the mechanism and a range from the start instead of a
point estimate.** Future passes: report the OBSERVED ahead-count trend over the longest available
baseline, never a rate fitted to the last half hour.

### ⭐ 2026-08-05 21:35 UTC (RUN 23 pass 4) — **THE QUEUE PREDICTION IS CONFIRMED BY A SECOND,
### INDEPENDENT ROUTE, AND IT CORRECTS A DATE I WROTE ONE PASS AGO**

**BOARD (light checks; the seven layers deliberately NOT re-run — see the interim rule below):**
inbox nothing pending, loop RUNNING · `loginnode_guard` OK · `line_balance` **CLEAN** ·
`occupancy_watch` every line proportionate · `arm_jobs` the same two by-design core arms ·
**seed check 0** · `ssh` OK · **Eqw/hqw 0** · 802 jobs against the 1,000 cap (198 spare, NOT binding) ·
drift 0.

**THE PREDICTION HELD.** Pass 3 said core's first job was 15-21 h away, derived from job duration.
Re-measured 38 minutes later as an OBSERVED RATE:
```
jobs ahead of core   276 -> 267      (-9 in 38 min = 14.2 jobs/h)
kimi pending         276 -> 268      kimi running slots 512 -> 576
haiku running slots  112 ->  56      (draining; 7 records from 568)
```
**14.2 jobs/h against the 13-19 jobs/h derived two other ways. Three routes agree.** At that rate
core's first job dispatches in **18.8 h, about 2026-08-06 16:20 UTC.**

⚠⚠ **AND A REFINEMENT THAT CORRECTS MY OWN PASS-3 DATE. CORE'S TWO TIERS ARE SPLIT IN THE QUEUE:**
```
core bayes_opt  best prio 2.00301  ->  267 jobs ahead   (ALL kimi)
core tpe        worst prio 2.00207 ->  445 jobs ahead   (268 kimi + 157 glm + 13 qwen3.6 + 7 core)
```
C1 needs **BOTH** tiers, so the binding number is 445, not 267: tpe dispatches at ~31 h and runs
~9.4 h ⇒ **core's DFO stage completes about 2026-08-07 14:00 UTC.** Its C2 `h2_pair` then submits
FRESH at the bottom and pays a second drain. ⇒ **the common rung reaches 30 around 8-10 August, NOT
"about 7 August" as I wrote last pass.** That estimate omitted the second stage transition and is
corrected here.

⭐ **AND THE REASSURING HALF, STATED BECAUSE OVERSTATING A RISK IS AS INACCURATE AS UNDERSTATING ONE.**
The drain penalty is a **STAGE-TRANSITION cost, not a permanent starvation.** Core has roughly two or
three transitions left (DFO test → `h2_pair` → C3 gate → C4). **Once it enters C4 it submits whole
tiers exactly like every leg line and stops re-queueing at the bottom.** So the exposure is bounded
at about 2-4 days, after which core climbs on the same terms as everyone else. Nothing here says the
campaign is failing; it says the reported result starts moving in the second week of August.

### ⭐⭐⭐ 2026-08-05 21:37 UTC (RUN 23 pass 4) — **§11.1 ITEM 1 IS STALE, AND IT HAS BEEN SENDING
### SESSIONS AT THE SEVEN BEST-COVERED MODULES IN `src/inference/` WHILE NINE SIT BELOW 40 %.**

**The row has been carried across four handover briefs, worded as *"the largest untouched surface in
the project"*, and it aged three passes of this session. Before starting it I measured whether it was
true. It is not.**

**FIRST MEASUREMENT — every function the row names as untested IS referenced by a committed test:**
`named_vs_blinded_structural` (4 files) · `cross_model_disagreement` · `contamination_report`
(2 files) · `dm_size_power_calibration` (2 files) · `reward_code_structure_report`. And
**`tests/test_inference_coverage.py` exists**, its docstring saying in as many words: *"Coverage tests
for the pure-function inference paths whose dedicated coverage agent did not land:
src/inference/{ood_stress, attribution, contamination}.py."* **A previous session closed most of this
gap and the row was never updated.**

**SECOND MEASUREMENT — actual line+branch coverage** (`pytest --cov=src.inference` over the nine
inference test files, `-p no:randomly`). The modules the row names:
```
contamination 99% · es_backtest 98% · reward_code_distance 98% · reward_taxonomy 96%
information_gap 91% · ood_stress 85% · attribution 77%
```
**Those are among the BEST-covered modules in the package.** The genuinely thin surface is somewhere
else entirely:
```
exposure 0% · regime_analysis 0% · cross_model 10% · bayes_null 14% · model_confidence_set 14%
responsiveness 24% · mediation 27% · leg_aggregate 35% · multiple_testing 63%
```
⚠⚠ **AND SEVERAL OF THOSE ARE LOAD-BEARING FOR THE REGISTERED RESULT, WHICH IS WHY THIS MATTERS
BEYOND TIDINESS:** `mediation` is SQ2, the fed → code → policy link Okhrati's mechanism kernel rests
on; `responsiveness` is SQ1; `cross_model` computes the cross-model synthesis R101 makes the PRIMARY
pooled statistic; **`leg_aggregate` is the very module `instrument_agreement`'s A7 names as the
TEARDOWN PRECONDITION**; `bayes_null` is R67 and `model_confidence_set` is R69; `multiple_testing`
carries the BH-FDR family R101 registers as the secondary analysis.

⛔⛔ **AND THE SECOND ROUTE KILLED MY OWN LIST. I PUBLISHED THAT TABLE AS PROVISIONAL AND IT WAS
WRONG — EVERY ONE OF THOSE NUMBERS WAS AN ARTEFACT OF MY TEST-FILE SELECTION.** The full-suite run
(`pytest tests/ --cov=src.inference -p no:randomly`) returns:
```
exposure   0% -> 100%      leg_aggregate 35% -> 100%     model_confidence_set 14% -> 100%
mediation 27% ->  95%      responsiveness 24% ->  96%    regime_analysis       0% ->  96%
cross_model 10% -> 90%     bayes_null    14% ->  92%     multiple_testing     63% ->  97%
attribution 77% -> 91%
TOTAL src/inference = 94.25%   (2,469 statements, 109 missed; 838 branches, 69 partial)
```
**The suite even enforces a floor and reports it: *"Required test coverage of 88.0% reached. Total
coverage: 94.25%."*** ⇒ **§11.1 ITEM 1 IS NOT STALE IN ITS DETAILS — ITS PREMISE IS FALSE. There is
no "largest untouched surface" here; `src/inference/**` is at 94 % and above the repository's own
gate.** The ONLY honest residue is **`ood_stress.py` at 85 %**, whose misses are one contiguous block
(461-511) plus a few branches.

⭐ **THE PROCESS POINT IS THE ONE TO KEEP.** I flagged that list as provisional *precisely because*
nine test files is not the suite, ran the second route, and the second route refuted me. Had I banked
it, this ledger would now carry a fabricated nine-module defect list with real-sounding numbers
against modules that carry the registered result. **A surprising result is a claim about your own
script first — and the first attempt at the confirming run returned RC=4 on my own bad flag
(`--timeout` is not installed here), which is the same rule catching the same class twice in five
minutes.**

⇒ **ACTION: the §11.1 row is REWRITTEN, not worked as given.** It should read: *`src/inference/**` is
at 94 % line+branch and passes the repo's 88 % gate; the only soft spot is `ood_stress` at 85 %.*
And it should record that the original wording sent four consecutive handovers at the seven
best-covered modules in the package.

### ⭐⭐ AND THE FULL-SUITE RUN FOUND A RED TEST THAT HAD BEEN COMMITTED FOR OVER A DAY — **FIXED**

`FULL_PYTEST_RC=1`, one failure:
**`tests/test_integrity_gate.py::TestRobustness::test_missing_archive_does_not_raise`.**

It asserted `gate.check(missing_path) == []` — **it PINNED the fail-open that P286/P294 removed from
every archive walker in this repository on 2026-08-04.** `integrity_gate.py:176-180` now returns
`I0 vacuity — "ZERO records found under the archive root: I1-I6 were NEVER EVALUATED. This is NOT a
clean result."` The code got safer and the test was left asserting the old, weaker contract, so it
has been RED since the guard landed. **Nothing runs the full suite on a cadence — the cycle runs the
campaign's guards, not `pytest` — which is why a red test sat in the repo for a day against this
repository's own "never commit failing tests" rule.**

**FIXED, and in the correct direction: the TEST was corrected to the stronger contract, the code was
not reverted to the weaker one.** It now asserts the breach list is non-empty, that it is exactly
`["I0 vacuity"]`, that the detail carries `NEVER EVALUATED`, and that `confirmatory is False`.
**FALSIFIED, not merely passed:** the new body was run against a stub whose `check()` returns `[]` —
exactly the pre-guard behaviour and exactly what the old assertion demanded — and it FAILS there
while passing against the real gate. `tests/test_integrity_gate.py` is 15/15, and `tests/**` is not
drift-fenced, so this was in scope.

⚠ **REGISTERED CONSEQUENCE: the full suite is not run on any cadence.** That is how this survived a
day. It is not something to bolt onto the 30-minute loop — `pytest tests/` is minutes of CPU on a box
already carrying the campaign — but it belongs in the session-start preflight or at teardown, and it
must run before anything is banked from the analysis path.

### ⭐ NEXT REGISTERED PIECE OF WORK, SCOPED BY MEASUREMENT: EXTEND THE CACHE TO THE SEVEN RECORD LAYERS

The loop contract says run the seven layers every pass; they cost **~1,342 s of full-archive scanning**
(217+257+236+15+192+219+206) and are enough on their own to push the cycle sweep to 620-1,300 s and
trip `budget_watch`. **Two of my own duties are in structural conflict, and the conflict grows with
the archive.** The resolution is the same cache SWEEP-1 already proved. Measured which layers can
take it:
* **UNAMBIGUOUSLY SHRINK-SAFE — reference NO big-array field at all:** `fed_text_identification`,
  `reward_code_audit`, `fed_value_coherence`, `record_window_identity`.
* **REFERENCE THE FIELDS BUT WITH NO INDEXING OR `len()` PATTERN** (so probably truthiness-only, the
  same shape `science_watch` and `results_audit` turned out to have): `record_validator`,
  `record_provenance_seal`, `record_science_audit`. ⚠ **"Probably" is not good enough for a layer
  that certifies an irreplaceable archive — each needs the read-and-verify plus the byte-identity
  proof `science_watch` got, not a regex.**
**INTERIM RULE, AND IT IS NOT A WEAKENED CHECK:** run the seven layers when the archive has grown
materially (≥500 records) or hourly, not every 30 minutes. The cycle already re-reads the WHOLE
archive every sweep through `science_watch` + `results_audit` + `integrity_gate`, the layers returned
**ALL RC=0 at 21:04 on 17,988 records**, and re-running 1,342 s of scanning for ~60 new records
**causes** the false-DEAD condition the layers exist to protect against.

### RUN 23 PASS 3 — BOARD, 2026-08-05 21:30 UTC. EVERY TOOL'S OWN VERDICT, READ NOT INFERRED.

`remote_inbox --status` nothing pending, loop RUNNING · `loginnode_guard` OK comfortable ·
`line_balance` **CLEAN** · `arm_jobs` flags core `distributional`/`scalar` with no covering job (the
by-design h2_pair case, discriminated from the driver log below) · `occupancy_watch` **every line's
fleet proportionate**, 976 running / 5,496 queued slots · `record_seed_completeness` rc=1 EXPECTED
(holes + C6 arms, both normal mid-campaign) · `science_plausibility` **PLAUSIBLE** ·
`loader_collision_watch` unchanged, D49-D51 registered · `instrument_agreement --deep` **7 of 8, A7
INFO** (the teardown precondition, not yet met, which is normal) · `run4_watch` rc=2 = the two
ACKNOWLEDGED criticals only, both triggers re-read and NEGATIVE this pass (see below) ·
**seven record layers ALL RC=0 on 17,988 records** (L1 217 s · L2 257 s · L3 236 s · L4 15 s ·
L5 192 s · L6 219 s · L7 206 s) · `crash_watchdog` **CLEAN** · `ssh myriad` OK ·
**seed check 0 — ZERO sealed-test seeds permanently lost.** Drift 0.

**THE TWO ACKNOWLEDGED CRITICALS, RE-READ AGAINST THEIR OWN TRIGGERS RATHER THAN RE-LITIGATED:**
* **`guard:truncation` — PROVEN-BENIGN.** `truncated=8` of 2,956, unchanged since this session's
  dated re-triage. Three models, ZERO on any `distributional` arm, ZERO on `c1`. Both live triggers
  (a `length` row on `distributional` or on `c1`; a FOURTH model) NEGATIVE.
* **`guard:transport` — PROVEN-BENIGN, all four trigger conditions NEGATIVE.** (1) no NEW
  ERROR/CRITICAL: the count is **465, identical to the 07:40Z reading 13.7 h earlier**; (2) timeout
  events 173 → 180 in 13.7 h = **0.5/h against a trigger of 60 in any rolling hour**; (3) no streak
  of 5+ — `transport_health` reads **HEALTHY, every streak recovered far below the bound**, and the
  `240/240` figures are the historical high-water marks of the 2026-08-03 01:29 outage, not a live
  state; (4) `crash_watchdog` CLEAN. **The guard reports a CUMULATIVE LIFETIME total, which is why it
  cannot return to green — that is the known shape, not a new event.**

### ⛔⛔⛔ 2026-08-05 20:55 UTC (RUN 23 pass 3) — **THE COMMON RUNG IS CAPPED BY CORE, CORE HAS RUN
### NOTHING FOR 21.6 HOURS, AND THE CAUSE IS OUR OWN QUEUE ORDER. ESCALATED TO TAMER.**

**This is the most consequential thing measured this session, and no instrument on the board reports
it, because every one of them is per-LINE and this is a cross-line ORDERING fact.**

**THE STATE.** Banked rungs (S15, 20:55Z): **core 0** · nemotron 0 (8 contiguous seeds, 48 in flight,
about to pass 30) · deepseek 30 · glm 30 · kimi 30 · **qwen3.6-27b 100** · **haiku 189** · h3,
gemini, gpt-5.6-luna, qwen3.5-9b, sonnet-5 all 568. **THE COMMON RUNG IS 0 AND CORE ALONE WILL CAP IT
ONCE NEMOTRON PASSES 30.**

**THE MEASUREMENT.** Core holds **8 jobs and every one is `qw`**:
```
91237-91240  c1_bayes_opt_test  prio 2.00293-2.00295  submitted 2026-08-04 23:19:34   -> 21.6 h queued
91449-91452  c1_tpe_test        prio 2.00204-2.00206  submitted 2026-08-05 00:01:12   -> 20.9 h queued
```
Its driver is ALIVE and polling (`driver_core.log` 21:51:15 host-local **= 20:51:15 UTC**, two minutes
old) and correctly reports `0/30 done, 30 pending, round 1` — it has submitted and is waiting, which
is exactly what `driver.py:550-553` prescribes while jobs are alive.

**THREE THINGS RULED OUT BY MEASUREMENT, NOT BY ASSUMPTION:**
1. **NOT unschedulable.** `qalter -w p 91449` → *"verification: found possible assignment with 8
   slots"*.
2. **NOT a different resource request.** `qstat -j` on core 91449 and on a RUNNING kimi job 90887
   returns **byte-identical requests**: `snx=1,tmpfs=1G,memory=2G,batch=true,h_rt=54000,
   hostname=!node-d00a-230&!node-d00b-024`, PE `smp-[D]* range: 8`, array `1-1:1`. No GPU, no
   special queue, nothing scarce.
3. **NOT `Eqw`/`hqw`/`qquota`.** All zero and empty.

**THE CAUSE, AND IT IS OUR OWN PENDING SET.** Dispatch order inside our fair share is by priority, and
priority tracks SUBMISSION TIME:
```
leg10 kimi      n=276   prio 2.00296 .. 2.00953    <-- EVERY ONE ABOVE CORE'S BEST
c1    core      n=8     prio 2.00205 .. 2.00295
leg2  glm       n=157   prio 2.00206 .. 2.00293
leg3  qwen3.6   n=80    prio 2.00184 .. 2.00237
leg1  deepseek  n=165   prio 2.00146 .. 2.00183
```
**276 of our pending jobs outrank core; 411 sit below it.** We run 123 jobs / 976 slots, `h_rt` is
54,000 s and the measured sealed-test mean is 9.39 h, so dispatch turnover is roughly **13 jobs/h**
⇒ **core's first job starts in about 21 hours**, on today's fleet.

⚠⚠ **AND THE STRUCTURAL PART IS WORSE THAN THE ONE-OFF WAIT. CORE PAYS A FULL QUEUE DRAIN AT EVERY
STAGE TRANSITION.** Priority tracks submission time, and core is SERIAL BY DESIGN: its C2 `h2_pair`
cannot be submitted until these DFO test legs finish, so it will enter the queue at a NEW, LATE
timestamp and rank BELOW everything then pending — exactly as it does now. The leg lines submitted
their whole tiers once and never re-queue. **That is why core has been the binding constraint for the
entire campaign, and it is a mechanism, not bad luck.**

**WHY IT MATTERS MORE THAN THE CORE COUNT.** Under R101 the reported result is the **MINIMUM** over
all eleven. **No amount of progress on any other line can raise it while core is 0.** Kimi's work is
not worthless — kimi is itself at rung 30, and a common rung above 30 needs it — but the ordering
that maximises the REPORTED result is laggard-first, and submission-time ordering is the exact
opposite. Moving core from 0 to 30 turns "no complete study at any rung" into "a complete 30-seed
study across all eleven models"; moving kimi from 30 to 60 changes the reported result by nothing.

⭐⭐ **AND IT FALSIFIES A NUMBER THIS LEDGER PRINTED TWICE TODAY. `stage_eta` dates rung 30 to
2026-08-05 22:35 / 23:15 — TONIGHT. IT CANNOT HAPPEN.** Of the 162 records the tool counts as
remaining for rung 30, **120 are core's** (4 registered arms × 30 seeds, all holding ZERO), and core
cannot start a job for another 15-21 h. The tool is not lying: it prints *"BOTH columns divide total
remaining by a FLEET-WIDE rate … NEITHER IS AN UPPER BOUND … the true bound is the slowest owing
cell"*, and this pass identifies that cell and prices it. **The honest rung-30 date is set by core's
queue position, not by the fleet rate: core starts in ~15-21 h, its two DFO test tiers then run
~9.4-15 h, so rung 30 is reachable no earlier than about 2026-08-07, and only if nemotron also
clears 30 (it is at 8 with 48 units in flight, so it will).** ⇒ **STANDING INSTRUCTION FOR EVERY
FUTURE PASS: never quote a `stage_eta` rung date without checking whether the BINDING cell has a
running job.**

⇒ **ESCALATED, WITH EVERYTHING AROUND IT MEASURED. THE ONLY LEVER IS TAMER'S OWN STANDING RULE.**
* Raising core's priority is **impossible**: SGE lets a non-operator only DECREASE priority; elevation
  is operator-only, and an RC request is Tamer's standing "no".
* Lowering the priority of kimi's 276 pending jobs (`qalter -p <negative>`) would let core's **8**
  jobs dispatch roughly a day sooner. The harness permits it. **Tamer's standing rule of 2026-07-24
  prohibits it: *"NEVER lower the SGE/queue priority of any of our jobs, EVER."*** That rule is his,
  it was set to protect our fair-share standing, and only he can relax it.
* ⚠ **STATE THE RISK HONESTLY IF HE ASKS: it may be ONE-WAY.** A non-operator can only decrease, so
  restoring the original priority is likely to be refused, and the effect on the existing scheduler
  RESERVATION is unverified. It should be proven on a disposable job before being applied to 276 live
  ones. **Do not test it on campaign jobs.**
* `qdel` is prohibited and would forfeit queue position and the reservation, which is worse.

**⚠ AND IT QUALIFIES THE ETA THIS LEDGER PRINTED AN HOUR AGO.** `stage_eta` dated rung 30 to
2026-08-05 21:26 and rung 568 to 08-12. Those divide remaining work by a FLEET-WIDE rate and the tool
says so itself — *"NEITHER IS AN UPPER BOUND … the true bound is the slowest owing cell"* and
*"81% of the rung-568 backlog sits on cells that produced NOTHING in the 12 h window."* **This
measurement is that caveat, quantified: the slowest owing cell is core, and it is 276 jobs deep in
our own queue.** Quote the rung dates only with this beside them.

### ⭐⭐⭐ 2026-08-05 (RUN 23) — SWEEP-1 IS FIXED. THE CAP HAD ALREADY BEEN BREACHED, AND MY FIRST
### VERSION OF THE FIX DID MEASURABLE HARM BEFORE THE SECOND ONE UNDID IT.

**THE TRIGGER HAD FIRED AND NOBODY HAD SEEN IT.** `cycle.py:478-487` pre-committed the condition for
building the incremental cache: *"TRIGGER: a `cycle_log` FAIL on a loop that is demonstrably alive."*
**At 2026-08-05T07:39:24Z the sweep read 903.5 s and consecutive `CYCLE_LOG.md` lines were 933 s
apart, against a 900 s staleness cap.** A perfectly healthy loop was inside the window where
`session_preflight` reports a run-killer. Measured over all 4,747 logged sweeps: the 14,000-15,000
band ran p95 **654.7 s** and max 845.2 s, so this was the trend arriving, not one spike.

**WHAT WAS BUILT:** `docs/ops/record_shrink_cache.py`, memoising `_shrink(json.load(path))` on
`(path, mtime_ns, size)`, wired into `science_watch._records` and `results_audit`'s load loop.
Both tools discard >94% of every byte they parse — **23.0 KB shrunken against a 416.7 KB raw record,
measured on a 120-record sample** — so the re-parse was pure waste. A cache HIT returns exactly the
object a full parse produces, so every aggregate downstream is bit-identical. **This is memoisation,
not sampling: nothing is skipped, no threshold moves, and the 900 s cap is UNTOUCHED.**

**RESULT, LIVE: sweeps 260-620 s at 17,780 records, against 714.6-903.5 s at 15,700.**

⚠⚠ **AND THE PART THAT MATTERS MORE: MY FIRST VERSION REWROTE THE WHOLE 439 MB CACHE EVERY CYCLE,
AND IT DID MEASURABLE HARM.** Both tools run every sweep, so that is ~0.9 GB of disk writes every
five minutes on the box that hosts every driver and supervisor. `budget_watch` had timed out
**3 times in 5,195 cycles** before this change and **6 times in the four hours after it** — the W6
trigger firing on my own edit. **Trading 340 s of CPU for 0.9 GB of writes is not an optimisation,
it is moving the cost.** Now APPEND-ONLY with ratio-based compaction: a steady sweep writes the
handful of new records (~23 KB each) instead of the file.

**THREE FURTHER DEFECTS IN MY OWN WORK, ALL FOUND BY THE FALSIFIER RATHER THAN BY ME:**
1. **The mutation control lied three times before it worked.** Replacing `os.stat` wholesale broke
   `Path.resolve()` and the run died on a TypeError with NO red case; patching only around the
   target case made the mutant MISS everything instead of serving stale, so it proved the opposite
   of its label; freezing stat for the whole sequence turned the target red but took five other
   cases with it. The shipped mutant rewrites the cached key and nothing else, and the control is an
   EXACT EXPECTED SET rather than a count, so it fails if the blast radius grows OR shrinks.
2. **Owner-scoped cache cleanup deleted the wrong file.** With the MODULE as the owner, two reducers
   in one file share a namespace and the second one's stale-sweep removes the first one's cache. The
   two production tools live in different files and would never have shown it; the falsifier, which
   defines two reducers side by side, went red immediately. Identity is now (module, function name);
   VERSION is the source hash.
3. **The cache files were not gitignored.** Never committed (`git log --all -- .record_shrink_cache*`
   is empty, `.git` is 148 MB) because the auto-committer stages BY NAME — but one `git add -A` would
   have put ~0.9 GB of derived data into history permanently. Added to `.gitignore`.

⭐⭐⭐ **AND THE PROOF FOUND THREE MORE DEFECTS OF MINE BEFORE ANY OF THIS WAS BANKED. THIS IS THE
ENTIRE ARGUMENT FOR WRITING THE FALSIFIER FIRST.** The first live run did not pass; it FAILED, and
each failure was real:

* **A SINGLE APPEND TARGET IS NOT CONCURRENCY-SAFE.** `cycle.py` runs these tools every sweep while a
  session may run them by hand, and two processes appending ~23 KB lines to ONE file interleave
  mid-line. The proof's warm run reported **710 unparseable cache line(s)**. It was FAIL-SAFE — torn
  lines are ignored and those records re-parsed, exactly as unit case F asserts — but a cache that
  shreds itself whenever two instances overlap does not work. **FIXED: one append shard per PROCESS
  (`…​.shard<pid>.jsonl`), merged on read, folded into the base on compaction. No lock, no retry.**
* **THE STALE-SWEEP WOULD HAVE EATEN THE CURRENT SIGNATURE'S OWN SHARDS.** They match the same glob,
  and a bare `!= cache_file` test deletes them — a cache erasing its own pending appends on every
  run while looking tidy. **FIXED with a prefix test, and unit case K now asserts it.**
* **THE PROOF ITSELF CLEARED THE LIVE CACHE AND THEN DIED ON A `PermissionError`** when the running
  cycle held a part open mid-`unlink`. A verification step that degrades the thing it verifies is not
  a verification step. **FIXED: the proof runs against a PRIVATE cache directory
  (`RECORD_SHRINK_CACHE_DIR`) and never touches the live one.**

**VERIFICATION AS IT NOW STANDS:**
* unit falsifier **11/11** (two new cases: J two writers get separate append targets · K the current
  signature's shards survive the sweep and are read)
* mutation control **PASS on the EXACT expected set** — a set, not a count, so it fails if the
  mutant's blast radius grows OR shrinks
* ruff clean on all four files
* walk order proven identical: `glob.glob(**, recursive=True)` and `Path.rglob` return the same
  **15,902** paths in the SAME ORDER — which matters because several printed lines are
  encounter-ordered example slices (`bad[:3]`, `oor[:3]`, `list(dupes)[:3]`)
* ⭐⭐ **STATIC BYTE-IDENTITY PROOF: PASS.** On a FROZEN 400-record copy of `test_leg_sonnet_5` (a
  COMPLETE line, so nothing can write to it mid-run), both tools are **byte-identical to
  `git show HEAD:` of their pre-change selves, cold AND warm** — `science_watch` 886 B, 7.7 s → 0.3 s
  (**25x**); `results_audit` 1,181 B, 1.7 s → 0.3 s (**5.7x**).
* **sci=OK on all 157 live cycles since the edit went in.**
* ⭐⭐⭐ **AND THE FINAL LIVE MEASUREMENT, ON THE REAL ARCHIVE, AFTER THE SHARD FIX: `science_watch`
  ran the FULL 17,935-record archive in 14 SECONDS with EMPTY stderr, writing a 792 KB shard instead
  of a 440 MB file.** Against the pre-change baseline of 129 s uncontended (and 340 s+ under the
  contention that produced the 903.5 s sweep), that is the whole of SWEEP-1 closed: **~9x on the
  uncontended baseline, and the disk cost per sweep fell from 0.9 GB to under 1 MB.** Compaction now
  fires roughly every ~150 cycles rather than every cycle.

⚠ **ONE HONEST COST, AND IT WAS MINE.** The `2026-08-05T20:35:14Z` cycle read **sweep=1307.1 s**, the
worst of the campaign. That is not the trend and not the fix failing: I had deleted BOTH live caches
minutes earlier to force the new owner identity, so that cycle ran fully cold on 17,836 records
**while my static proof and a full-archive proof ran beside it.** RUN 22's lesson 4 exactly — my own
deep checking is load on the box — and the reason the falsifier now runs against a PRIVATE cache
directory and the full-archive mode was STOPPED once the static proof had settled the question.
**The very next hand-run read 14 s.** `budget_watch` also went `budget=99` on those contended cycles;
expect it to clear, and if it does not, that is a new finding rather than this one.

⚠ **WHY A STATIC ROOT WAS NEEDED, STATED RATHER THAN GLOSSED.** The full-archive comparison is
structurally INCONCLUSIVE and calling it a pass would be the "0 means no defects" mistake: the
archive gains a record every ~24 s while each tool takes 130-200 s, so the baseline and the cached
run never see the same record set. The first live run differed on exactly **three lines and all three
were record COUNTS** (17,893 → 17,898 → 17,906), with every other line identical — honest corroboration,
not a proof. The frozen copy is what makes the claim exact. ⚠ The comparison is deliberately against
the ORIGINAL code rather than the new code with caching disabled: only the former can catch a
walk-ORDER change, because the latter would use the new walk on both sides.

⚠ **`integrity_gate.py`, the third layer this row names, is NOT converted.** It is cadence-gated
rather than every-sweep and RUN 22 timed it at 51 s, so it is not what breached the cap. Stated
rather than quietly dropped.

### ⚠ SWEEP-1 UPDATE — AN 845.2 s CYCLE, 55 s FROM THE CAP, AND I AM THE LIKELIEST CAUSE

`2026-08-04T23:39:37Z sweep=845.2s` against the 900 s staleness cap, at 14,834 records. **My pass-1
regression predicts ~291 s at that archive size**, so ~554 s is unexplained by growth — and the
cycles either side of it read 276.9 s and 490.1 s, so it is a SPIKE, not the trend arriving early.

⚠ **THE HONEST SUSPECT IS MY OWN TOOLING.** That cycle spanned ~23:25:32-23:39:37Z, during which
this session ran `run4_watch ... all` over twelve driver logs (~380k lines), `analysis_obligations`
over the whole archive, `compute_ledger`, a 6-case selftest and a 4-mutant control **each spawning
its own subprocess tree** — on a 16-core laptop already hosting 9 drivers, 9 supervisors, the cycle
loop and **40 live python processes**. That is the candidate this row has listed since pass 1 and
could not discriminate: *"my own instrument runs during the same window."*

**⇒ IT IS NOT A NEW DEFECT, IT IS AN OPERATING DISCIPLINE ITEM, AND IT IS MINE:** the deep checking
is itself pushing the monitoring loop toward the threshold that declares it DEAD. **Serialise heavy
scans against the cycle rather than running them concurrently**, and land the registered incremental
fix. The dated forecast (~30,000 records / ~8 August on busy cycles) is UNCHANGED — this spike is
contention, not growth, and conflating the two would have re-dated the deadline wrongly.

**PASS 4 SPEED VERDICT — EVERYTHING MOVING THE RIGHT WAY, NOTHING TO FIX.** 12 h **188.0** rec/h
(186.4 -> 188.0), 1 h 200. Slots **1,312**, our share of the cluster's 8,177 running slots = **16.0%**,
`Eqw`/`hqw` **0**, jobs **989** (the cap eased from 994, so submissions are landing again).
**The four questions:** (1) *Holding every core we could?* `occupancy_watch` reports every line
proportionate, no alarm at any pass; fair share, not placement, sets the 1,312. (2) *Newly
schedulable?* No — zero error states, quota still empty, nothing changed. (3) *Cores on work that
cannot raise the rung?* 62% is sonnet-5, above the common rung — and that share is falling steadily
pass over pass, **74% -> 69% -> 65% -> 62%**, which is the laggards taking over exactly as intended.
(4) *Has the projected depth moved?* **Yes**: remaining-to-568 **27,137 -> 27,068**, and the chain
owes ZERO for the second consecutive pass.

### ★★★★★ 2026-08-04 23:00:55 UTC (RUN 22 pass 3) — **THE C1 BARRIER IS CLOSED. THE TERM THAT HAS
### FLOORED THE COMMON RUNG SINCE THIS CAMPAIGN BEGAN IS GONE.**

⚠ **THE TIMESTAMPS BELOW ARE THE DRIVER LOG'S OWN, AND THE DRIVER LOG IS IN HOST-LOCAL TIME (+0100)
— `vanished_array_watch.parse_ts` says so explicitly.** I first recorded this event as "2026-08-05
00:01 UTC", reading the local stamp as UTC and putting a campaign milestone on the wrong DAY. The
UTC time is **2026-08-04 23:00:55Z**, corroborated by `stage_eta`'s own header (`generated 2026-08-04
23:01 UTC`) and by `date -u` in the same minute. **Every driver-log time quoted anywhere must be
converted before it is written down.**

```
2026-08-05 00:00:55 LOCAL (= 2026-08-04 23:00:55Z)  [c1_tpe_c29] batch complete: {'ok': True,
                        'completed': 1, 'total': 1, 'rounds': 1, 'exhausted': [], 'job_ids': ['90130']}
2026-08-05 00:01:26 LOCAL (= 2026-08-04 23:01:26Z)  [c1_tpe_test] submitted c1_tpe_test as 4 array(s)
```
**`stage_eta`: `critical-chain floor: 4.64 d total, 0.00 d still to run (every DFO arm has spent its
full candidate budget)`.** All three DFO arms — `bayes_opt`, `cma_es`, `tpe` — have spent their
registered 30-candidate budgets, and both `c1_bayes_opt_test` and `c1_tpe_test` (30 units each) are
submitted. **Every ETA this ledger has printed since 2026-08-04 00:10 was clamped to that floor.**

**WHAT NOW STANDS BETWEEN CORE AND A NON-ZERO COMMON RUNG**, and it is much shorter than what just
ended: the two DFO test legs now queued, then core's C2 `h2_pair` (`distributional` + `scalar`, both
still at ZERO records — the arms `arm_jobs` correctly reports as below frontier with no covering
job), then the C3 gate, then C4. **The remaining serial term is a sealed TEST at 9.39 h mean, not a
30-link DFO chain.**

⭐ **AND THE OTHER LADDER INDICATORS MOVED THE SAME WAY IN ONE PASS:** registered units with no
directory **3 -> 2**, test-tier units **68 -> 69**, remaining-to-568 **27,242 -> 27,137**,
concentration **69% -> 65%**. Cluster share 1,288 of 8,034 running slots = **16.0%**, still #2 on
Myriad, 994 jobs against the 1,000 cap, `Eqw`/`hqw` **0/0**.

**PASS 2 SPEED VERDICT — THE LADDER MOVED AND THE RATE IS HOLDING.** 12 h 182.2 rec/h, 24 h 179.6,
both essentially flat against pass 1 despite the share falling. ⭐ **`bayes_opt` has FINISHED its
30-candidate C1 chain and submitted `c1_bayes_opt_test` (22:19:44Z); only `tpe` owes 1, floor
0.19 d.** ⭐ **`glm_5_2` PASSED ITS C3 GATE AND ENTERED C4 at 22:24:35Z** (`h2_pair` 60/60,
`exhausted: []`), and registered units with no directory fell **4 -> 3**. Concentration 74% -> 69%.
`stage_eta` now prints **GATED / `barrier`** on every rung rather than a date, which independently
restates pass 1's conclusion from the other side: **the ladder is barrier-bound, not core-bound.**

**THE FOUR QUESTIONS, ANSWERED WITH NUMBERS:** (1) *Holding every core we could?* After the P306
fixes below, **every line's ratio is >= 0.30 and seven of nine are ~1.0**; the tool's own verdict is
*"every line's fleet is proportionate to the work it owes"*. We are also 6 jobs from `max_u_jobs`, so
we are holding the most work the scheduler will let us EXPRESS. (2) *Anything newly schedulable?*
**No** — `Eqw` 0, `hqw` 0, `qquota` empty, unchanged. (3) *Any core on work that cannot raise the
rung?* Yes and it is the design: 69% of the 12 h window is sonnet-5, within 8 records of 568 — and
that share is FALLING (74% -> 69%) as the laggards take over. (4) *Has the projected depth moved?*
**Yes, favourably**: remaining-to-568 27,335 -> 27,242, empty units 4 -> 3, and the C1 barrier went
from two owing arms to one.

### ⛔⛔ 2026-08-04 21:56 UTC (RUN 22 pass 1) — **THE SECOND, INDEPENDENT PROOF THAT CORES ARE NOT
### OURS TO TAKE — AND IT RETIRES "PLACEABLE CAPACITY" AS THE INSTRUMENT FOR THIS QUESTION**

**RUN 21 re-opened the closed cores question on `placeable_capacity`, and this session can now show
that instrument was answering a DIFFERENT QUESTION from the one Tamer asked.** Measured together,
in the same minute, for the first time:

```
placeable cores in smp-D at pack 8 (d00a 1,328 + d00b 224) ......  1,552   FREE, in OUR pool
our RUNNING slots ...............................................  1,184   FLAT for 9 minutes
our QUEUED slots ................................................  3,752   and GROWING (+1,008 in 6 min)
our Eqw / hqw ...................................................    0 / 0
qquota -u ucestes ...............................................  EMPTY
cluster-wide ....................................................  104 users, 2,165 running jobs
```

**⇒ WE HAVE 3,752 SLOTS OF WORK READY, 1,552 FREE PLACEABLE CORES IN OUR OWN POOL, NO ERROR STATE
AND NO QUOTA — AND THE SCHEDULER IS GIVING US NOTHING.** Held slots did not move across a full
`schedule_interval` (0:10:0, read from `qconf -ssconf`).

**THE INSTRUMENT ERROR THIS EXPOSES, AND IT IS THE USEFUL PART.** `placeable_capacity` measures what
the CLUSTER CAN ACCEPT. It is silent on what FAIR SHARE WILL GIVE US, and those are different
quantities. RUN 21 read a rise in the first as a recoverable loss in the second. **Pack 4 recovers
+340 stranded placeable cores — and we are not being given the 1,552 UNSTRANDED ones, so recovering
more of what we cannot take buys nothing.** The fourteen RUN 20 measurements were RIGHT: this is
functional fair-share by user, and nothing we control changes it.

⚠ **A CAVEAT WAS ENTERED HERE AND THE MEASUREMENT HAS NOW DISCHARGED IT.** The first version of this
section rested on NINE MINUTES — roughly one scheduling interval — which is one observation of a flat
line, not a trend, and this ledger has already had to retract one alarm raised on less. **The sampler
ran to completion: 15 samples, 3 minutes apart, 42 minutes, 4.2 scheduling intervals.**

```
running slots  1,144 -> 1,232    sd 28.3    full range 8.0% of the mean    =  +126 slots/h
queued  slots  2,800 -> 5,384                                              = +3,691 slots/h
```

**⇒ WE PRESENT WORK 29 TIMES FASTER THAN WE ARE GIVEN IT, AND OUR HELD SLOTS DO NOT MOVE.** Across
4.2 scheduling intervals the running total is flat to within 8%. This is fair share, measured rather
than inferred, and it closes the question for the conditions it was measured under.

### ⭐ AND THE SHARE DECLINE ITSELF WAS THEN EXPLAINED, WHICH ANSWERS TAMER'S "WE FELL VERY BADLY" DIRECTLY

Our share read **2,018 slots at 12:00Z** and **~1,232 now** — a 39% reduction inside twelve hours,
and NOT the sawtooth (the sawtooth is our own queue emptying, and our queue is 5,384 slots deep). So
it was measured rather than assumed, per user, cluster-wide:

```
cluster-wide RUNNING slots ........ 8,238        ucbtjji  1,408   <- #1
ucestes (us) ...................... 1,232        ucestes  1,232   <- #2, 15.0% of the whole cluster
                                                 uctpec1  1,020   <- #3
```

⇒ **WE DID NOT FALL THROUGH ANY MISCONFIGURATION. OTHER LARGE USERS ARRIVED AND FAIR SHARE
REDISTRIBUTED, WHICH IS THE MECHANISM WORKING AS DESIGNED.** We are the **second-largest consumer on
Myriad and hold 15% of every running slot on the machine**, with zero `Eqw`, no quota, and 5,384
slots queued ready to take anything that frees. **There is no lever here and nothing to fix.**

⚠ **WHAT REMAINS A WATCH, AND IT IS THE ONLY ETA SIGNAL THAT MATTERS NOW:** the forward rate scales
directly with held slots — at 1,232 cores rung 568 lands ~13 August; at ~600 it would not land before
the stop. **Record held slots every pass. A sustained decline is the OPEN finding.** Not the queue
depth, which is now meaningless as a signal, and not the placeable-core count, which measures the
wrong thing entirely.

### ⚠ AND A CORRECTION TO THE PARAGRAPH THAT STOOD HERE FIFTEEN MINUTES AGO — I OVER-WEIGHTED A LABEL

**This section first concluded that the fair-share ceiling made an RC allocation request newly
urgent, citing `stage_eta`'s `Aug-27? risk` on rung 568. THEN I DID THE ARITHMETIC, and it does not
support that.** Overstating a risk is as inaccurate as understating one.

```
remaining test records to rung 568 .... 27,335        hours to the 08-27 stop .... 530 h (22.1 d)
rate REQUIRED to make the stop ........  51.6 rec/h
       cores      rec/h    rung 568 lands
       1,184      125.7    2026-08-13    <- TODAY'S DEPRESSED SHARE, 14 DAYS OF SLACK
       1,900      201.8    2026-08-10
       3,235      343.6    2026-08-08    (the saturation point)
```

**EVERY core count we could plausibly hold makes the stop comfortably.** The only branch that misses
is `stage_eta`'s `latest` at **49 rec/h** — and 49 rec/h implies just **461 producing cores**, which
is not a forecast of the future but a MEASUREMENT of a 12 h window in which every still-owing line
sat in a tier TAIL. Those lines have since submitted six tiers each and now hold 4,632 queued slots.

⇒ **THE LADDER IS NOT MATERIALLY THROUGHPUT-BOUND, AND CORES ARE NOT THE THING TO SPEND THIS
CAMPAIGN'S REMAINING ATTENTION ON.** It is at risk in exactly one scenario: **the owing lines falling
back into simultaneous tier tails and staying there**, which is the sawtooth, whose repair
(`driver.py:550-553`, requeue while a straggler still runs) is DRIFT-FENCED and already registered.

**⇒ WHAT TO WATCH INSTEAD, and this is now the primary ETA signal:** the **24 h record rate measured
over a window in which sonnet-5 and gpt-5.6-luna contribute nothing** — i.e. the rate the OWING lines
actually sustain once they are out of their tails. If that settles near the fleet rate we have ~14
days of slack; if it settles near 49 rec/h the tail is costing us the campaign and the fenced fix
becomes a deploy-window priority. **Do not re-litigate cores until that number exists.**

**RC allocation request: NOT escalated as urgent.** Tamer's standing "no RC request" stands, and on
this arithmetic there is no honest case to re-open it. Recorded so a future pass does not resurrect
the urgency from the `risk` label alone.

### ★★★★★ 2026-08-04 20:55 UTC — TAMER ASKED "WHAT THE HELL IS GOING ON WITH MYRIAD". THE TROUGH IS
### EXPLAINED END TO END, AND I HAD TO RETRACT THE SEVERITY OF MY OWN ALARM

**THE OBSERVATION THAT PROMPTED IT:** slots fell **1,952 -> 984 in three hours**, smoothly at
~245/h since 17:46Z, with the queue at **ZERO** the whole way down.

**WHAT IT WAS NOT — every candidate checked and eliminated by measurement:**
`qquota -u ucestes` **EMPTY**, so no limit applies to us · `qstat -g c` shows **~11,644 FREE slots**
in most cluster queues, so there is no capacity shortage · our state census was **118 `r` + 2 `Rr`,
zero `qw`, zero `Eqw`, zero `hqw`** · all ten active driver logs **0.3-2.3 min fresh** and actively
polling · no line idle with work owed · records still climbing throughout.

**THE MECHANISM, CONFIRMED IN THE FENCED CODE AT `src/cluster/driver.py:550-553`:**
```
if alive_names:          alive_seen = True
else:                    <DRAIN TRANSITION -> requeue the tier's remaining specs>
```
**The requeue branch is reached only when NO job of that batch is alive.** So while even ONE pack of
a tier survives, the tier's several hundred remaining specs are not resubmitted. Each line therefore
runs a SAWTOOTH: submit a tier as ~50-100 arrays, drain it over ~9.4 h, sit at low occupancy through
the tail, then requeue the next tier en masse. **Today several lines' tails aligned, so the whole
fleet troughed at once for the first time.**

⚠⚠ **AND I MUST RECORD A RETRACTION, BECAUSE I RAISED THE ALARM TOO HIGH BEFORE MEASURING PROPERLY.**
I reported "~134 packs vanished" and "~5,000 units held hostage". **That arithmetic mixed
populations** — I counted EVERY haiku batch directory and EVERY haiku ledger, including its search
generations and earlier test stages, against the sweep tiers' pending counts. Redone precisely, the
28 sweep epilogues are all LOW pack numbers (p01-p07) because **those tiers had not been submitted
yet**, not because their packs had disappeared. The mechanism above is real; the "hostage" reading
of it was not. **A surprising negative is a claim about my own script first, and this time it was.**

⭐⭐ **AND THE DECISIVE PROOF ARRIVED WHILE I WAS INVESTIGATING, WHICH IS THE BEST KIND.** The driver
logs show three large tiers submitted in thirty minutes: **sonnet `sweep_t6` (825 units) at 20:22Z,
haiku `sweep_t3` as 51 ARRAYS at 20:47Z, haiku `sweep_t2` as 51 ARRAYS at 20:51Z.** And the queue,
zero for the whole session, now reads **110 `qw`** — roughly 880 slots waiting to dispatch.
**Nothing was stalled. The trough was the bottom of the sawtooth and the recovery is underway.**

⚠ **WHAT REMAINS TRUE AND COSTLY, AND IS THE ONLY REAL FINDING HERE:** during a tail we run at about
HALF capacity, and the tail recurs on every tier of every line. **That is a genuine ETA cost and the
lever is the tail latency, not the core count** — the cluster had 11,644 free slots the entire time
and our queue was empty, so no amount of extra allocation would have placed a single additional job.
Reducing it means letting a tier requeue its lost specs while a straggler still runs, which is a
change to `src/cluster/driver.py` and therefore a **registered deferred fix**, not a live patch.

⚠ **AND THE INSTRUMENT THAT SHOULD HAVE CAUGHT THIS WAS BLIND, WHICH IS WHY NEITHER OF US SAW IT.**
`vanished_array_watch` printed **"no vanished arrays detected"** while reporting
`UNKNOWN (no id parsed)` for **all twelve** of the open haiku and qwen3.6-27b blocks — the twelve
most important on the board, carrying ~5,000 pending units. **FIXED**: unresolved blocks are now
listed with their pending-unit totals and the tool exits 2. Verified: `SCRIPT_RC=2`, twelve blocks
named. An UNKNOWN is not a negative.

**RUN 21 pass 6 (20:27Z) — CORE'S `cma_es` CAME OFF ZERO AND THE FLEET IS NOW GENUINELY BROAD.**
12 h 193.6 rec/h, 24 h **182.0** (a session high). Slots **984**, 125 running, queue **0**.
⭐ **The core line no longer has `cma_es` at zero — only `distributional` and `scalar`, its C2
`h2_pair`, remain.** `c1_cma_es_test` reads **1/30 done** and `c1_tpe_c29` has advanced from c28, so
the C1 chain is actively closing. `bayes_opt` still owes 1 of 30 and the floor holds at **0.19 d**.
⭐ **CONCENTRATION HAS COLLAPSED FROM 100% TO 86%, AND THE NUMBER OF LINES CONTRIBUTING IN THE 12 h
WINDOW HAS GONE 2 -> 5 -> 9.** haiku climbed 55 -> 69, qwen3.6-27b 32 -> 33 with a frontier at 44,
glm 7 -> 14, and sonnet is at 566 of 568.

⚠ **A PREDICTION, RECORDED SO THE NEXT SESSION DOES NOT MISREAD IT AS A FAULT: THE 12 h RATE IS ABOUT
TO FALL, AND THAT WILL BE CORRECT.** sonnet-5's C4 sweep produced the great majority of the last 12
hours' records and is now down to **1 running job** from 83 at pass 1. As its output ages out of the
window the trailing rate must drop toward what the remaining lines actually generate. Slots have
already fallen 1,848 -> 1,664 -> 1,248 -> 1,096 -> **984** across six passes, a 47% decline, while
the 12 h rate went 183 -> 191 -> 200 -> 199 -> 194 — i.e. **throughput per slot rose sharply**,
because the surviving jobs are the ones actually landing records. **A falling rate over the next few
passes is the sweep ending, not the campaign slowing.** The discriminator remains what it has always
been: `line_balance` CLEAN, queue 0, and no line idle with work owed. All three hold now.

**RUN 21 pass 5 (19:54Z) — THE CRITICAL CHAIN IS CLOSING AND THREE CAPPING LINES MOVED OFF ZERO.**
12 h **198.9 rec/h**, 24 h **180.9**, both holding at the session highs. Slots **1,096** (1,848 ->
1,664 -> 1,248 -> 1,096), 139 running, queue **0**. ⭐ **`bayes_opt` now owes 1 of 30, not 2, and the
critical-chain floor has HALVED to 0.19 d — about 4.6 h.** That is the first time this session the
floor has moved materially, and it is the term the whole common rung waits on.

⭐⭐ **AND THE LADDER MOVED ON THREE LINES AT ONCE, WHICH IS WHAT THE LAST THREE PASSES WERE WAITING
FOR.** `glm_5_2` now has **NO arm at zero** (recMin 7) — both halves of its C2 `h2_pair` are landing.
`nemotron_3_super`'s `scalar_cvar5` came off zero, leaving only its `h2_pair`. `haiku_4_5` climbed
30 -> 55 and `qwen3_6_27b` 30 -> 32. **The four lines that cap the common rung are now core,
deepseek, nemotron and kimi — glm has left that set.**

⚠ **THE SLOT DECLINE CONTINUES AND THE CAUSE IS UNCHANGED: sonnet-5's C4 sweep is finishing.** That
line is down to **4 running jobs from 83** at pass 1, with records at 562-567 of 568. Concentration
fell 100% -> 92% and the number of lines contributing at all rose 2 -> 5, which is the same handover
seen from the other side. Queue 0 throughout, `line_balance` CLEAN, no line idle with work owed.
**Nothing to fix.**

**RUN 21 pass 4 (19:15Z) — RATES AT ANOTHER NEW HIGH WHILE SLOTS FELL 32%, AND THE TWO FACTS HAVE
THE SAME CAUSE.** 12 h **200.4 rec/h** (183.2 -> 191.2 -> 200.4 across the three passes), 24 h
**180.8**. Slots **1,848 -> 1,664 -> 1,248**, jobs 231 -> 210 -> 158, queue **0** throughout.

⚠ **A 32% SLOT DROP IS A MATERIAL DROP AND THE CONTRACT SAYS WORK IT TO A CAUSE, SO IT WAS WORKED.
IT IS NOT A FAULT — IT IS sonnet-5's C4 SWEEP DRAINING.** Per-line running jobs on that one line:
**83 -> 71 -> 35 -> 11**, while its records went 454 -> 475 -> 541 -> 565 and its **banked rung moved
30 -> 100**. The fleet shrank because its single largest consumer is FINISHING, and the record rate
hit a new high for exactly the same reason: those completions are landing as records. This is the
line-handover shape recorded as SPEED-1/SPEED-3, seen at the END of a handover rather than the start.
**`line_balance` reads CLEAN, no line is idle with work owed, and the queue is 0 — so nothing of ours
is waiting on the scheduler.** Nothing to fix.

⭐ **AND THE LADDER MOVED, WHICH IS THE FIRST SUCH MOVEMENT SINCE THE COMMON RUNG WAS FIRST MEASURED
AT 0: `glm_5_2` NO LONGER HAS `distributional` AT ZERO.** Its C2 `h2_pair` is landing; only `scalar`
remains, and both arms of a pair test run as one 60-unit stage, so `scalar` follows shortly.
**`sonnet_5` banked 30 -> 100.** `haiku_4_5` and `qwen3_6_27b` are both climbing past 30 with holes
above their banked rung, which is the normal pipelined-C4 shape and self-heals.
**COMMON RUNG STILL 0**, capped by core, deepseek, nemotron and kimi — unchanged and honest.

**RUN 21 pass 2 (17:42Z) — BOTH RATES AT NEW HIGHS, AND `stage_eta` NOW REFUSES TO DATE THE RUNGS.**
12 h **191.2 rec/h** (was 183.2), 24 h **171.2** (was 165.6). Slots fell 1,848 -> **1,664** and the
queue is **0**, with 210 running (`208 r` + `2 Rr`). ⚠ **The slot drop is NOT fair-share and NOT a
fault:** the queue is empty, so nothing of ours is waiting; the lines mid-`h2_pair` have no further
work to submit until that stage returns. Rate UP while slots are DOWN is the line-handover shape
already recorded as SPEED-1/SPEED-3. ⭐ **AND THE ETA COLUMNS NOW READ `GATED` FROM THE TOOL ITSELF**
— `stage_eta` declines to date any rung because the relevant rate is zero, which independently
confirms ETA-1 from the other direction: **rung 30 is barrier-bound, not throughput-bound, and no
number of cores changes it.** Concentration 100% on sonnet-5 is the same fact seen from the fleet
side: every other line is inside a stage that produces nothing until it completes.

**RUN 21 pass 1 (16:14Z) — NO REGRESSION, AND THE 12 h RATE IS THE HIGHEST YET RECORDED HERE.**
183.2 rec/h over 12 h (was 180.3), 24 h 165.6 (was 164.9), slots flat at 1,848. The queue has fallen
to **3 jobs against 231 running** — `qstat -u ucestes -xml` reads `r 231 / qw 1 / Rq 2`, zero `Eqw`,
zero `hqw`. That is the §6.2 finding reaching its endpoint: **the scheduler now takes everything we
submit essentially on arrival, so there is no fair-share wait left to recover, and no lever exists
that adds throughput to the critical path.** Concentration 96% on sonnet-5 is the design working —
94% of the fleet's output lands above the common rung.

⚠ **AND A CORRECTION TO THE RUNG-30 DATE THAT MUST NOT BE QUOTED THE EASY WAY.** `stage_eta` prints
**08-05 01:10** for rung 30. That figure divides remaining records by a fleet-wide rate and clamps to
the **C1** chain floor only; it does not model the **serial C2 `h2_pair` TEST that must follow C1**,
and a sealed TEST training is 9.39 h mean. Dating the four capping lines from their `qstat`
`JAT_start_time` instead: **glm** h2_pair started 12:22–12:34Z (8 packs) → ~22:00Z tonight · **kimi**
13:10–13:19Z (5 packs) → ~22:45Z · **nemotron** is still on `scalar_cvar5` (12:47Z, 4 packs) → ~22:10Z
and only then submits its h2_pair → ~07:40Z · **deepseek** the same shape → ~08:00Z · **core** cannot
start its h2_pair before its C1 chain ends (0.37 d ⇒ ~01:10Z) → **not before ~11:00Z on 05 Aug**.
⇒ **The honest common-rung-30 date is ~2026-08-05 11:00Z, about ten hours later than the tool's
number.** `stage_eta` is not wrong — it says in its own output that neither column is an upper bound
— but the number a reader takes away is the optimistic one. Registered as **ETA-1** below.

**RUN 20 pass 17 speed verdict — EIGHTH CONSECUTIVE IMPROVEMENT, AND THE QUEUE IS ALL BUT EMPTY.**
12 h **180.3 rec/h** and 24 h **164.9**, both session highs again; slots steady at 1,868; the queue
has fallen **70 -> 57 -> 35 -> 31 -> 30 -> 18** with `Eqw`/`hqw` **0**, and the board's verdict has
read **OK** on every cycle since 14:59. **A queue of 18 against 231 running jobs means the scheduler
is taking everything we submit essentially on arrival** -- there is no fair-share wait left to
recover, which is the cleanest possible restatement of the pass-5 finding that the ETA is bound by
the serial chain and by nothing else. Concentration 94% on sonnet-5, still the one line deep in a C4
sweep and still landing above the common rung. **`bayes_opt` and `tpe` each owe 2, chain floor
0.37 d, core reaches rung 30 in ~18 h.** Nothing to fix.

**RUN 20 pass 14 speed verdict — SEVENTH CONSECUTIVE IMPROVEMENT, AND THE BOARD IS GREEN.** 12 h
**179.7 rec/h** and 24 h **162.7**, both session highs; slots 1,864 with the queue at 30 and
`Eqw`/`hqw` **0**. ⭐ **The cycle verdict has now read `OK` on three consecutive lines** (14:59:10Z,
15:02:17Z, 15:06:05Z) after 27 of the previous 30 read `ATTN` -- P293 removed the last unacknowledged
attention row and nothing has replaced it. Concentration 90% on sonnet-5, unchanged in meaning: it is
the only line deep in a C4 sweep and its records land above the common rung.

**★ P293's OWN P259 TEST, RUN ON MY OWN FIX RATHER THAN LEFT TO THE AUDITOR.** A demotion is the shape
most likely to be a weakening, so the three branches were re-read as shipped and each proven still
reachable: the **RED** branch (`_resumed` False -- no crashed arm has archived a record) is **entirely
untouched**; the **ATTENTION** branch is reached whenever `_resumed` is True and `_all_frozen` False,
which is exactly a crash that recovered but has not yet frozen a winner -- the normal mid-search
state; and the seed is `_all_frozen = bool(_arms_map)`, **not `True`**, so an unreadable marker
(`_arms_map == {}`) cannot produce a vacuous demotion and still falls to RED, preserving the original
"unknown is never downgraded" contract. **No branch was made unreachable and no path was weakened.**

**Watch, no action:** `83464` (`gpt-5.6-luna`'s round-2 repair for seeds 192/193) is still RUNNING
after 2.4 h, inside the 9.4 h sealed-test wall. LADDER-1.

**RUN 20 pass 12 speed verdict — SIXTH CONSECUTIVE IMPROVEMENT, AND THE QUEUE IS NEARLY DRY.**
12 h **179.1 rec/h**, 24 h **160.6**, slots **1,929**, and the queue fell **70 -> 57 -> 35 -> 31**
with `Eqw`/`hqw` still **0**. A near-empty queue against a rising slot count means the scheduler is
dispatching everything we submit as fast as we submit it -- **we are no longer waiting on fair-share
at all, which is the strongest possible confirmation of the pass-5 finding that the ETA is not
slot-bound.** ⭐ **AND THE TWO REPAIR JOBS THE BOARD HAS TRACKED SINCE RUN 18 ARE NOW RUNNING**
(83464 at 12:47:20, 85065 at 13:08:40), one of them the round-2 repair for `gpt-5.6-luna`'s seeds
192/193 -- see LADDER-1. **Binding term unchanged: `bayes_opt` and `tpe` each owe 2 serial
candidates, chain floor 0.37 d, core reaches rung 30 in ~18 h.**

**RUN 20 pass 11 speed verdict — FIFTH CONSECUTIVE IMPROVEMENT AND THE HIGHEST OF THE SESSION.**
12 h **178.8 rec/h** (167.1 -> 171.8 -> 172.6 -> 174.5 -> **178.8**), 24 h up to 160.3, slots back to
**1,925**, and the queue drained hard: **70 -> 57 -> 35**, with `Eqw`/`hqw` **0**. A draining queue
against a rising slot count is dispatch keeping up with completion, which is the healthy shape.
Concentration 87% on sonnet-5, for the reason every row this session has recorded: it is the one line
deep in a C4 sweep, and its output lands ABOVE the common rung. **The binding term is unchanged:
`bayes_opt` owes 2 serial candidates, chain floor 0.37 d, core reaches rung 30 in ~18 h.**

⚠ **AND THIS ROW CARRIES A SECOND MEASUREMENT THAT MATTERS MORE THAN THE RATE.** The box's free-RAM
floor during a full preflight moved from **0.14 GB to 6.3 GB** (P289/P290/P291). Until this pass the
campaign was on a trajectory to OOM before its registered primary target, and an OOM on this box
kills DRIVERS. **That was the largest live risk to the campaign and it is now closed.**

**RUN 20 pass 10 speed verdict — A NEW SESSION HIGH, AND THE CONCENTRATION IS THE HEALTHY READING.**
12 h **174.5 rec/h** (167.1 -> 171.8 -> 172.6 -> **174.5**, four consecutive improvements), slots
steady at 1,867, queue drained 70 -> **57**, `Eqw`/`hqw` **0**, `line_balance` **CLEAN**.
Concentration reached **83% on sonnet-5**, and the per-line table says why: sonnet climbed
**284-301 -> 371-383 records in a single session**, because it is the one line deep in a C4 sweep
while five others sit at a pipeline barrier. **That is the design working, not an imbalance** -- and
it is also why the rate cannot move the result: every one of those records lands ABOVE the common
rung. `bayes_opt` still owes 2 and the chain floor holds at **0.37 d**. Nothing to fix.

**RUN 20 pass 8 speed verdict — HOLDING AT THE SESSION HIGH, and the slot drift is worked to a
cause rather than noted.** The 12 h rate is **172.6**, its highest sustained value of the session
(167.1 -> 171.8 -> 172.6), and the chain floor holds at **0.37 d**. Slots eased 2,014 -> 1,896 ->
**1,848** over ninety minutes while the queue held flat at ~70: **jobs are completing faster than
replacements dispatch, which is fair-share churn, not loss** -- `Eqw` and `hqw` are **0**, no line
is idle without work, and `line_balance` reads CLEAN. Concentration rose 76% -> **80%** on sonnet-5
for the same reason the previous rows record: it is the only line deep in a C4 sweep, and its output
lands **above** the common rung, so neither the concentration nor the slot drift touches the ETA.
**The binding term is unchanged and is not throughput: `bayes_opt` owes 2 serial candidates, and
core reaches rung 30 in ~18 h.**

**RUN 20 pass 6 speed verdict — THE BEST ROW OF THE SESSION, AND THE CRITICAL PATH SHORTENED.** The
12 h rate reached **171.8** and the 1 h rate **185**, the highest instantaneous reading of the
session and comfortably the post-outage recovery completing. Slots eased 2,014 -> 1,896 as jobs
completed faster than replacements dispatched (`qw` 68 -> 70), which is churn rather than loss;
`line_balance` reads **CLEAN** and `Eqw`/`hqw` are **0**. **The material change is on the critical
path, not the rate: `c1_bayes_opt_c27` COMPLETED rc=0 in 12.37 h, `bayes_opt` fell from owing 3 to
owing 2, and the critical-chain floor fell 0.56 d -> 0.37 d** (CHAIN-3 RESOLUTION). **Core now
reaches rung 30 in ~18.3 h against the ~23 h stated one pass earlier — the ETA moved, and it moved
for the only reason it can: the serial chain advanced.**

**RUN 20 pass 4 speed verdict — FULLY RECOVERED AND NOW MEASURED AGAINST ITS PHYSICAL CEILING.** The
12 h rate has climbed through the outage and past it (161.8 -> 165.1 -> **167.1**), the 1 h rate is
back to 153, slots hold at 2,014 with `r 243 / qw 68 / Rq 2` and **zero `Eqw`, zero `hqw`**, and
`line_balance` reads **CLEAN**. **167.1 against the measured ceiling of 199.6 rec/h is 84%
utilisation** (see the throughput identity above). Nothing to fix, and nothing further to gain
without more slots, which is fair-share and closed.

**RUN 20 pass 3 speed verdict — THE OUTAGE COST NOTHING MEASURABLE, AND THAT IS A MEASUREMENT, NOT A
HOPE.** Transport was restored at 12:32:19Z after **31 m 50 s** (INC-1 RESOLUTION). Every recovery
indicator was then re-read rather than assumed:

* **the backlog flushed** — test tier **11,096 -> 11,196 records, +100 in 28 minutes**;
* **the 12 h rate came back ABOVE its pre-outage value** — 164.7 -> 161.8 -> **165.1 rec/h**;
* **the fleet never shrank** — 2,018 -> 2,033 (measured DURING the outage) -> **2,015 slots**, with
  `r 243 / qw 69 / Rq 2` and **zero `Eqw`, zero `hqw`**;
* **no driver died** — worst consecutive pull failures peaked at **21** against a SEARCH death clock
  of 240, so not one line came close;
* **`session_preflight --full` reads VERDICT OK, all 17 rows.**

⇒ **The jobs ran on the compute nodes throughout. Only the PULL was blocked, so the cost was
visibility and a queue of unpulled records, not work.** The slot count actually ROSE during the
outage, because SGE kept dispatching our already-queued jobs (`qw` 88 -> 71) entirely independently
of whether we could reach the login node. **That is the single most useful thing to remember from
this incident: a transport outage stops us WATCHING the campaign, not the campaign.**

**RUN 20 pass 2 speed verdict — the drop is the OUTAGE, and it is CORRECT BEHAVIOUR.** The 1 h rate
fell **143 -> 118 rec/h** and `records=` went **`12633 (+0)`** because login13 began refusing SSH at
12:00:29Z (INC-1). **The jobs are still running on the compute nodes; only the PULL is blocked**, so
this is delayed throughput, not lost throughput, and the 12 h/24 h rates barely moved (164.7 -> 161.8,
159.0 -> 156.9) because a 12 h window absorbs a 13-minute stall. ⚠ **The slot and queue columns read
`n/a OUTAGE` deliberately: a `qstat` census is impossible while the node refuses connections, and
recording a guessed number would be worse than recording none.** This is the same reasoning the
maintenance playbook applies to the Aug-12 window — a flat `records=` during a transport event must
never be diagnosed as a stall. **NO SPEED ACTION IS OWED OR POSSIBLE while transport is down**, and
retrying is actively harmful (stampede -> penalty). Re-measure after recovery.

**RUN 20 pass 1 speed verdict — PROVEN-BENIGN, worked to a cause rather than noted.** Slots reached
**2,018, a campaign high** (+250 on the previous pass, +14%), the queue drained **128 -> 90**, and the
state census over `qstat -xml` reads `r 242 / qw 88 / Rq 2` with **zero `Eqw` and zero `hqw`**. The
12 h rate fell 168.1 -> 164.7 and the 24 h rate 170 -> 159 while slots ROSE, which is the same
line-handover shape recorded as SPEED-1 and SPEED-3: a newly dispatched pack-8 job holds slots for
8-15 h before its first record lands, so a handover always reads as rising slots and a falling
trailing rate. Concentration rose 63% -> 70% on sonnet-5 for the same reason. `stage_eta` states the
binding fact directly: **90% of the rung-568 backlog sits on cells that produced NOTHING in the 12 h
window**, i.e. behind a stage barrier, and no redirected core accelerates that. `bayes_opt` still owes
3 of 30 and the critical-chain floor reads **0.56 d still to run**. Nothing to fix.

⚠ **NEW THIS PASS, AND IT MATTERS FOR EVERY FUTURE CENSUS: `qstat` TRUNCATES THE JOB NAME TO TEN
CHARACTERS** (`leg8_leg_s`), and `line_balance.cluster_jobs()` also counts ONLY exact `r` and `qw`, so
the **2 `Rq` jobs live right now are invisible to it**. Use `qstat -u ucestes -xml` for any census that
needs the arm token or a complete state distribution; it is the same scheduler query at the same
login-node cost. See P276.

---

## THE HARD PROHIBITIONS (a check with full permissions still may not do these)

* **NEVER read a treatment arm's SEALED-TEST outcome.** Single confirmatory look; reading it is a
  forking path on a frozen pre-registration.
* **NEVER edit `src/`, `scripts/`, `config/`, `prompts/` while the campaign is live** — drift-fenced,
  `drift` must stay 0. `docs/**` is safe. `paper/**` belongs to the write-up session.
* **NEVER change a frozen threshold or `PREREGISTRATION.md`.**
* **NEVER lower SGE priority** (prohibited, one-way); never `qdel -u`; explicit job ids only.
* **NEVER junction the archive** (`poll.py:305` renames; cross-volume it rmtrees the record).
* **NEVER `git clean -x`, `git add -A`/`-u`, or `git stash`.** Stage BY NAME.
* **NEVER put backticks, `$(...)` or heredocs in a `bash -c` string or a `-m` commit message.**
  Write to a FILE and use `-F`. Broken seven times; it is the single most repeated error here.
* **Printed output is ASCII-ONLY** (the console is cp1251 and the status page publisher REFUSES
  non-ASCII, so one bad character silently freezes Tamer's page).
* **NEVER add Claude/Anthropic attribution anywhere.** Tamer is sole author.
* **Editing a running loop is INERT** — `cycle_loop.sh` / `publish_loop.sh` need a RESTART;
  `cycle.py` / `publish_status.sh` are re-invoked each iteration and do not.

---

## OPEN — every row must move to a terminal state

Rows carry: `id · found · what · evidence needed · owner-action`. Work the **BLOCKING** rows first;
they are the ones that can cost the campaign or the grade. Add every new finding here the moment it
is found, including findings about this ledger.

### BLOCKING — can cost records, the result, or the grade

| id | found | what | to resolve |
|---|---|---|---|
| **D49-D51** | 08-04 RUN21 pass 1 | ⛔⛔ **`scripts/analyze_campaign.py` CANNOT PRODUCE A REPORT ON THIS ARCHIVE TODAY, AND THE BANK GATE STOPS THERE.** Its loader admits every `test_leg_*` line into the same flat record list under the SAME arm labels (`:1179` skips only dot-dirs and `*_h3_singleshot`), and `_seed_scores` groups on `(arm, seed)` with no line term. **MEASURED TWICE INDEPENDENTLY: 2,145 of 2,145 `distributional` and 2,137 of 2,137 `scalar` H2 test records are from LEG lines with ZERO from core; 2,840 (arm, seed) cells are held by more than one line, 568 on each of five arms.** ★ **THE CONSEQUENCE CLAUSE IN THE OLD `LOADER-POOLING` ROW IS REFUTED AND MUST BE RE-WORDED, NOT CLOSED: the H2 path FAILS LOUD** — `_seed_scores` raises `ValueError` and `analyze()` guards only `AssertionError`, so the run aborts rather than reporting a pooled verdict. ⚠⚠ **THE TRAP (D51) IS THE OPERATIONAL RISK: the guard's own message says "deduplicate the run archive", and an operator who does that CONVERTS THE LOUD FAILURE INTO THE SILENT ONE.** ⛔ **DO NOT DEDUPLICATE THE ARCHIVE.** `benchmark_floor`, `h1_beat_human`, PBO and `winner_dsr` have no guard at all and would pool silently. **UNFENCED DETECTOR BUILT AND LIVE: `docs/analysis/loader_collision_watch.py`**, 4 s, directory names only, AST-proven effect-blind, rc=1 today. Full register: `docs/DEFERRED_FIXES_RUN4.md` D49-D60. | `scripts/**` is DRIFT-FENCED while live. The repair is already prototyped at `docs/analysis/a79_fix_proof.py:60-84` (skip `_leg_` exactly as `_h3_singleshot` is skipped) and applies at the next deploy window or at teardown, BEFORE `bank_gate` runs |

### MAJOR — an instrument can mislead a future session

| id | found | what | to resolve |
|---|---|---|---|
| **F1** | 08-04 RUN22 pass 2 auditor | **THE D9 DIAGNOSTIC REGEX MATCHES NOTHING ON THE REAL LOGS.** `run4_watch.py:231-235` (and the identical block in FENCED `scripts/campaign_guards.py`) searches `child_already_exited=(\w+)` on the SAME PHYSICAL line as `ssh_timeout_diagnostic`, but `src/cluster/submit.py:135-140` wraps them onto different lines. `grep -c "ssh_timeout_diagnostic.*child_already_exited"` = **0 across all 12 logs**, while the value is present **173 times (164 False / 9 True)**. The panel prints an EMPTY dict. **164 False is an actionable operational conclusion — the remote command genuinely hung, so the search moves cluster-side — and the instrument has never delivered it.** `docs/ops/transport_health.py` already solves the wrap. Same class as P306-b, found in the same pass. | fix the `docs/ops/` copy with the un-wrap; `scripts/` copy waits for the deploy window |
| **F2** | 08-04 RUN22 pass 2 auditor | **`reflection_guard`'s verdict is a FLEET MEAN, so one line's total failure cannot trip it.** `run4_watch.py:113-141` returns on `shown/total` campaign-wide against an 80% floor. Live: 1141/1144 = 99.7%; the largest single line is 125 of 1,144, so **a line falling to ZERO still reads 88.8% = "ok"** and TWO whole lines must fail to breach the floor. The module's own docstring says the defect class is *"a resource shared by twelve concurrent lines, keyed by an identifier unique only WITHIN one line"* — it then aggregates over exactly those twelve. Per-line numbers are computed and discarded. | add a per-line floor beside the fleet one |
| **F3** | 08-04 RUN22 pass 2 auditor | **`rejects_guard` can only fire on 4 of 10 legs.** `run4_watch.py:276-281`: `EXPECTED_PASS_RATE` has four keys; `exp_pass = ...get(leg)` is `None` for the other six, making the `rc = 2` branch at `:308` unreachable. **glm_5_2 (13% reject), nemotron_3_super (19%), gpt_5_6_luna, haiku_4_5, kimi_k3, sonnet_5 — 60% of the leg population — can never raise this guard**, while the docstring says *"deepseek at 83% reject would be the study broken"*. A collapse on nemotron or glm prints `[rejects] ok`. | populate the table for all ten legs, or fail loud on a missing expectation |
| **F7** | 08-04 RUN22 pass 2 auditor | **`compute_ledger.py --report` prints a HEADLINE DISSERTATION NUMBER with no staleness guard.** `LATEST: 67,166 CPU-hours` comes from a single snapshot **~88 h old** against a `MIN_SNAPSHOT_GAP_S` of 6 h. Its own docstring (`:74-82`) says a mid-campaign reading is a LOWER BOUND over completed jobs only, so "LATEST" understates by roughly the ratio of 4 elapsed campaign-days to 7. `_report` (`:284-299`) prints the timestamp and computes no age. **Okhrati explicitly docks missing/incorrect wall-clock compute reporting**, so this is grade-relevant. Also `mean_slots_per_task` is documented at `:205-213` as a cross-check that "must land near the packing depth we actually requested" and **nothing in the file compares it to anything**. | add an age warning + the packing-depth comparison; re-snapshot before the write-up quotes it |
| A6 | 08-04 pass-3 auditor | **`test_h3_singleshot` is folded into the campaign-wide minimum.** R101 defines the result over the **11 full-loop models**; h3 is the H3 single-shot CONTROL, not a model leg. Direction: too LOW. Non-binding today (h3 reads 568). ⚠ **ESCALATED: changes the definition of the reported scientific result -- a pre-registration question, not an ops patch.** | Tamer + Dr Okhrati |
| **E-sent** | 08-04 RUN20 pass 1 | ⛔ **THE SENTINEL IS BLIND IN WAYS THAT ALL FAIL TOWARD "OK", AND `scripts/` IS DRIFT-FENCED.** A read-only auditor enumerated **40 possible rows across 19 check functions in `sentinel.py` plus 18 lane checks in `campaign_health.py`** and found eighteen defects. **I verified the four load-bearing ones FIRST-HAND against the live archive:** (1) `sentinel.py:1480` globs `*.failures.jsonl` -> **0 files**, while `failures.jsonl` -> **42 files / 275 rows**, so `authoring_health` is structurally dead and has printed "authoring healthy" for four days; (2) `sentinel.py:835` iterates only `("search", "test")`, so the whole NaN / divergence / reward-scale / gate-failure family covers **1 of 12 lines** -- **5 ledgers / 22 rows seen against 42 / 275 campaign-wide**; (3) `anomalies.jsonl`, `events.jsonl`, `progress.json` and `campaign_summary.json` have **zero occurrences** anywhere under the campaign root, so six checks report OK/INFO from an input that does not exist; (4) `winners[leg]` at `:1577` keys **58 frozen winner records** into at most one per leg -- measured 58 on disk against a report of "all 11 frozen winner(s) executed cleanly". ⚠ **ESCALATED, NOT FIXED: `scripts/**` and `src/**` are drift-fenced while the campaign is live and `drift` must stay 0.** **CAMPAIGN EXPOSURE ASSESSED AND IT IS THE REASSURING ANSWER:** every blind spot is covered by an instrument that is NOT fenced -- the seven record layers validate all 12,654 records (`L1` R1-R9 replays the Sharpe endpoint, `L3` S1 the science invariants), `line_balance` and the new `arm_jobs` cover liveness, and S15 covers set completeness. The sentinel is redundant cover that has been silently absent, not the only cover. Registered for the next deploy window. | apply at the next deploy window |
| **E-spend** | 08-04 RUN20 pass 1 | ⚠⚠ **`spend=$45.5019` IS 80.7% A MODEL ESTIMATE, NOT MONEY ANYONE CHARGED -- AND THE CONFIRMATORY LINE IS 100% OF IT.** Auditor measurement over all 12 ledgers, 2,956 rows, 0 unparseable: **realized $8.7603 (2,127 rows) + estimated-from-planning-prices $36.7418 (829 rows)**. `c1`, the confirmatory line, is **$23.6502 and entirely estimated** -- `src/llm/client.py:1139` falls back to `tokens x config/legs.yaml planning_prices` whenever the transport surfaces no `last_cost_usd`. `campaign_guards.py:284` sums the two classes indiscriminately and prints one figure to four decimal places, which reads as measurement precision. **THIS IS A WRITE-UP INTEGRITY ITEM, NOT AN OPS ONE:** Raad's cost-discipline point and Okhrati's compute-reporting mechanic both land on this number, the guard file is drift-fenced, and the split already exists in each row's `note` field. ⚠ **ESCALATED TO TAMER: the dissertation must state $8.76 realized + $36.74 estimated, never the pooled $45.50 alone.** | Tamer -- a write-up decision |
| **E-wc** | 08-04 RUN20 pass 1 | ⚠ **`wall_clock` IS 0.0 ON ALL 11,082 SEALED-TEST RECORDS -- MEASURED EXHAUSTIVELY, NOT SAMPLED.** Also 0 on all 58 frozen markers; the search tier is fine (400/400 sampled non-zero, 10,338-40,584 s). The writer is in drift-fenced `src/`, so the field cannot be repaired for records already written. **THE COMPUTE IS NOT LOST:** `outputs/campaign_cluster_run4/ledger/*.epilogue.jsonl` carries per-task `"secs"` across **3,207 files**, so the sealed-tier wall-clock is recoverable for the write-up from the ledger rather than the record. Okhrati explicitly docks missing wall-clock compute reporting, so this is a grade-relevant provenance gap with a working substitute. P277 makes the layer report it instead of skipping it silently. | Tamer + the write-up session; source the compute from `ledger/*.epilogue.jsonl` |
| W1 | 08-04 pass 5 | **`gate_failure_drift` is a STRUCTURALLY PERMANENT alarm.** `sentinel.py:640` runs a CUSUM against **target 0** with `k=0.03` on the aggregate gate-failure rate, which is **0.1530** (257 lost of 1,680 slots). Per-sample increment `0.1530 - 0 - 0.03 = +0.1230`, strictly positive, so S rises without bound and **can never return below `h=0.15`** -- it crosses after **1.2 samples** and the log says "since sample 2", an exact match. Fifth appearance of the "counter that cannot go down" pathology. Root cause: target 0 encodes "we expect ZERO gate failures", but per-model reliability runs 0-86% and **that variation IS the science**. ⚠ **ESCALATED: `scripts/` is DRIFT-FENCED while live.** No campaign result is affected -- it is a monitor, and the rates themselves are measured correctly by `authoring_reliability.py`. Everything around it IS fixed: `acknowledged_alarms.txt` now carries the structural proof so no session re-triages it, and it is registered as a deferred fix. | apply at the next deploy window: target = each model's own baseline |

### MINOR — correctness or hygiene, no campaign exposure

| id | found | what | to resolve |
|---|---|---|---|
| **SWEEP-1** | 08-04 RUN21 pass 1 | ⚠ **THE SWEEP IS ELEVATED AND P303 DOES NOT EXPLAIN IT.** Measured this hour: 221.9 · 441.3 · 261.0 · **783.5** · **655.0** s. The 783.5 cycle ran all three cadence-gated probes (a one-off: the two new verdict stamps did not yet exist). **The 655.0 cycle ran NONE of them** — STATE ages 822.8 / 820.1 / 685.1 s, every verdict cached — so 655 s is the base sweep plus something this row has not identified. The staleness cap is **900 s** and `session_preflight` reads a breach as "the monitoring loop is DEAD", so the margin is 245 s and the sweep grows linearly with the archive. **Candidates not yet discriminated:** archive growth (13,494 → 13,576 in one cycle, 53 records × ~480 KB), the mirror pull, disk contention from ~30 live campaign processes, and my own instrument runs during the same window. ⭐ **AND THE NEXT CYCLE SETTLES IT: 412.0 s WHILE RUNNING ONE HEAVY PROBE** (STATE 17:31:31Z — `record_seal_age_s = 0.0`, the seal ran; science 1127.2 s and vanished 1261.8 s both cached; all three rc=0, no attention). **So a cycle with ONE scan swept 412 s and a cycle with NONE swept 655 s. The probes are not the driver, and the base sweep itself varies by a factor of two.** That also confirms P303's mechanism on the live board: one probe ran while another was skipped, and both verdicts were still reported. ⚠ The CONTENDED case — both heavy probes due in the same sweep — has NOT yet been observed live; their cadences (1200 s and 1800 s) next coincide about an hour out.  ⭐⭐ **MEASURED IN PASS 2, AND IT TURNS THIS ROW INTO A DATED FORECAST.** The three full-archive layers inside every sweep were timed individually under live load at 13,611 records: `science_watch` **114 s** + `results_audit` **139 s** + `integrity_gate` **51 s** = **304 s**, all rc=0. That accounts for the 412 s cycle almost exactly (304 + the 99 s seal = 403). ⚠⚠ **AND IT DATES THE FAILURE: those three alone are ~22.3 ms/record, so at the registered ~42,128-record end state they are ~940 s — ABOVE the 900 s staleness cap ON THEIR OWN, before anything else in the sweep.** Taking the whole observed sweep as roughly linear, the cap is crossed somewhere between ~18,700 records (on the 655 s cycle) and ~29,700 (on the 412 s one) — at ~180 rec/h the pessimistic branch is about **28 hours away**. When it happens `session_preflight.check_cycle_log` will report **the monitoring loop as DEAD while it is perfectly healthy.** ⛔ **THE FIX IS NOT TO RAISE THE CAP** — the cap is what makes a genuinely dead loop visible, and raising it to make a check pass is the one move this ledger forbids. The principled repairs, in order: make the three layers INCREMENTAL (the seal already is), or scale the cap on the measured archive size rather than a constant. **This is now the highest open ops item after D49.** |

| **SWEEP-1 (RUN 22 pass 1, 2026-08-04 21:58Z)** | ⭐ **THE "UNEXPLAINED 2x" IS EXPLAINED, REGRESSED OVER 4,647 CYCLES RATHER THAN THE FIVE THIS ROW RESTED ON — AND THE FIRST READING OF MY OWN REGRESSION WAS WRONG AND THE CONTROL CAUGHT IT.** Parsed every `sweep=` in `CYCLE_LOG.md` (n=4,647, archive 1,513 -> 14,548). **(1) THE SSH-GATED LAYER IS REFUTED AS THE CAUSE**: median 27.9 s on ssh cycles (n=167) against 20.2 s on non-ssh (n=4,480), a difference of **+7.7 s**, not hundreds. **(2) ARCHIVE SIZE IS THE DOMINANT TERM AND IT IS NOW FITTED**: `sweep ~= -44.2 + 22.65 s per 1,000 records`, **R^2 = 0.722** — and that **22.65 ms/record independently reproduces the 22.3 ms/record this row measured by timing the three layers directly.** Two derivations, different methods, agreeing. **(3) ⚠ THE DELTA SPLIT WAS CONFOUNDED AND I NEARLY BANKED IT.** Univariately, cycles with >=25 new records sweep **328.0 s** against **18.4 s** for cycles with <=5 — an 18x gap that looked decisive. Adding `delta` to a JOINT fit moves **R^2 from 0.722 to 0.725** and prices a new record at **0.29 s**: almost all of that 18x was archive size wearing a different hat, because busy cycles are also late cycles. **(4) THE UNCONFOUNDABLE COMPARISON IS THE ONE THAT SURVIVES**: high-vs-low delta *within* narrow archive bands gives **1.2x (5-8k) -> 1.5x (8-11k) -> 1.6x (11-13k) -> 2.3x (13-15k)**. So the arrival rate DOES matter and its cost GROWS with the archive, which is why an additive term could not see it. ⚠ **THE MECHANISM IS NOT DISCRIMINATED and must not be asserted**: "the layers do per-new-record work" and "producing cycles contend for the same disk as the mirror pull and the drivers" both predict this and the cycle log cannot separate them. ⭐⭐ **AND IT DATES THE FAILURE PROPERLY, WHICH IS THE POINT OF THE ROW.** At the median delta the 900 s cap is crossed at **~42,415 records**; on a BUSY cycle, scaling the 13-15k band's 416.4 s median, it is crossed at **~30,000 records** — and the false "the monitoring loop is DEAD" fires on the WORST cycle, never the median. At ~180 rec/h that is **~3.5 days away (about 8 August)**, not the 28 h this row previously carried on a two-point extrapolation. ⛔ **THE FIX IS STILL NOT TO RAISE THE CAP.** The dominant term is a FULL-ARCHIVE RESCAN EVERY CYCLE, so the principled repair is exactly the registered one: make `science_watch` / `results_audit` / `integrity_gate` incremental, as `record_provenance_seal --since-state` already is. |
| SWEEP-1-fix | | make the three layers incremental (`--since-state`, the pattern the seal already proves); do NOT raise the cap — the cap is what makes a dead loop visible. ⭐⭐ **BUILT AND LIVE 2026-08-05 (RUN 23), PENDING ITS LIVE PROOF — see the RUN 23 SWEEP-1 section in SPEED above.** `docs/ops/record_shrink_cache.py` memoises the shrunken record on `(path, mtime_ns, size)` for `science_watch` and `results_audit`; sweeps fell from 714.6-903.5 s at 15,700 records to **260-620 s at 17,780**. ⚠ **THE DEADLINE IN THIS ROW WAS ALREADY PAST WHEN THE FIX WAS BUILT: the cap was BREACHED at 2026-08-05T07:39:24Z (sweep 903.5 s, 933 s between cycle lines).** ⚠ My first version rewrote the whole 439 MB cache every cycle and drove `budget_watch` to 6 timeouts in 4 h against 3 in 5,195 cycles — fixed to append-only with compaction. `integrity_gate` is NOT converted (cadence-gated, 51 s, not the cause). **The row closes when the byte-identity proof against `git show HEAD:` of both pre-change tools passes.** |
| **ETA-1** | 08-04 RUN21 pass 1 | **`stage_eta`'s rung dates omit the serial C2 `h2_pair` TEST, so the rung-30 figure is ~10 h optimistic.** The clamp applies the C1 chain floor only; a line whose h2_pair has not STARTED still owes a full 9.39 h sealed TEST after its current stage ends. Measured from `qstat JAT_start_time`: tool says 08-05 01:10, the chain says **~08-05 11:00** with core binding. **Not a false statement** — the column is labelled "earliest" and the tool prints "NEITHER IS AN UPPER BOUND" — but it is the number a reader carries away, and the handover brief already quoted a different one. **No campaign exposure: it changes no decision, because nothing can accelerate the chain.** | add a chain-aware column: for each line whose h2_pair arm holds 0 records AND has no covering job, add one T_test (9.39 h) after its current stage. `stage_eta.py` is under `docs/`, so it is editable while live |

### DISCLOSURES — true, permanent, and must reach the write-up rather than be "fixed"

| id | what |
|---|---|
| D-a | `metrics.train_curve.return` is 100% NaN on every test record (SB3 logs `ep_rew_mean`; no episode closes in the logging window). A disclosure, NEVER an exhibit. |
| D-b | A62: `per_period_pnl` is byte-identical to `test_returns` on 9,065/9,065 records. No consumer reads it; no result affected. |
| D-c | **S4 determinism is VACUOUS in this archive** — 0 replicate `(arm, seed, reward_hash)` keys exist, so "0 disagree" tests NOTHING. Determinism must be evidenced from the 30/30 bit-identical farm, never from here. |
| D-d | S5: the sealed test's worst safe-default fallback is 9.0847%, INSIDE the registered R115 10% floor with 0.9153% margin. The phenomenon the campaign measures, not a defect. |
| D-e | **R115 is a stated Limitation, threshold UNCHANGED, and is PROVISIONAL for 3 of 10 core groups — RE-RUN BEFORE SUBMISSION.** |
| D-f | D34: the authoring-reliability marker set structurally cannot hold an author-side reject. D35: `n_attempted` publishes `placebo = 33` against a registered budget of 30. |
| D-g | `campaign_summary.json` at teardown remains the only UNRECOVERABLE item. |
| **D-h** | ⛔ **NO SHARPE FROM THIS CAMPAIGN MAY BE QUOTED WITHOUT BEING EXCESS-OF-RISK-FREE AND WITHOUT THE EQUAL-WEIGHT BENCHMARK ON THE SAME LINE.** The archived `metrics.test_sharpe` is **RAW**; subtracting the risk-free rate on the registered R20 path costs every cell **0.14-0.27 units, median 0.21**. Against a costed equal-weight 1/N at **+1.0617 excess**, the best model-arm cell reaches **+1.0173** and the median **+0.8549** — **0 of 59 cells beat it**, while **25 of 59 have a SHALLOWER CVaR-5% tail** than the benchmark. Costs confirmed four ways including bit-exact against the archive. Full derivation, conventions and the independent re-check: `docs/analysis/EXCESS_AND_BENCHMARK_2026-08-04.md`. ⚠ **This rule was stated to Tamer and recorded only in the cursor until 2026-08-04 21:10Z — it had NO durable home in the repo, which is exactly how a standing rule gets lost.** It is Okhrati's requirement that every number arrives with its comparator, and the first table this session produced broke it. |
| **D-j** | ⚠⚠ **R101 REGISTERS THE ELEVEN MODELS AS CLIMBING "IN LOCKSTEP", AND IN EXECUTION THEY DO NOT. THE WRITE-UP MUST SAY SO PLAINLY RATHER THAN LET A READER ASSUME OTHERWISE.** Measured 2026-08-05 20:15Z: `test_leg_haiku_4_5` holds **530-535** records while `glm-5_2`, `kimi-k3` and `deepseek-v4-pro` hold **30** and the core line's `h2_pair` holds **0** — a 535-to-0 spread on a ladder the pre-registration describes as *"ONE COMMON assurance-tier ladder … IN LOCKSTEP — every model banks the SAME rung at each checkpoint; no model is privileged with more seeds."* ⭐ **THE REGISTERED CONCLUSION IS NOT AFFECTED AND THAT IS THE POINT TO MAKE FIRST:** R101 defines the final result as *"whatever COMMON rung all 11 have COMPLETED by the stop"*, i.e. a MINIMUM, and the pooled bound and the per-model contrasts are all computed AT that common rung — so the surplus depth on one line is simply unused by the primary analysis, exactly as designed. **What is NOT true is the execution sentence.** The asymmetry is a FAIR-SHARE ARTEFACT, not a design privilege: every line's jobs carry equal priority (measured: our pending jobs span 2.00144-2.00155, a submit-order sequence with no per-line difference), each driver submits its whole tier, and SGE decides which tier runs. ⚠ **The honest write-up sentence is therefore: the ladder is banked in lockstep; it is not EXECUTED in lockstep, because the scheduler orders the work and we may not steer it** (`qdel` and held-back submissions are both standing prohibitions). ⚠ **AND R101 ITSELF PREDICTED THE SCALE OF WHAT WOULD BE REACHED**: *"30 GUARANTEED early; fair-share expectation ~100-189; all-11-to-403 unlikely"* — so a common rung well below the deepest line is the registered expectation, not a shortfall. Report the per-line depths as measured, never a single "the campaign reached N". |
| **D-i** | ⚠ **A STALE NUMBER IN `src/baselines/strategies.py`'s DOCSTRING, TO FIX BEFORE ANYTHING REACHES THE PDF.** It records `market_ew` **1.1656** and `.SPXTR` **1.1302**; the correct values under the codebase's own `sharpe_ratio` are **1.1659** and **1.1305** — the docstring used `ddof=1` where the code uses `ddof=0`. `src/**` is drift-fenced, so this applies at the next deploy window. Small, but Criterion 4's top band is the literal word "faultless" and one stale figure forfeits it. |

### WATCH — not yet a finding, but trending

⚠ **EVERY ROW BELOW WAS RE-MEASURED 2026-08-04 14:44 UTC (RUN 20 pass 12). THREE OF THE FIVE WERE
STALE, AND A STALE WATCH ROW IS ITSELF A DEFECT** under this ledger's own no-row-may-age rule: a
number nobody re-reads becomes a number nobody can act on. They are now dated, and any row without a
current measurement should be treated as unverified rather than as evidence.

| id | what | trigger | re-measured 2026-08-04 14:44 UTC |
|---|---|---|---|
| **W6 — RE-DIAGNOSED 2026-08-05 20:51Z (RUN 23), AND THE ROOT CAUSE IN THIS ROW WAS WRONG** | ⭐⭐ **THE TRIGGER HAS FIRED HARD: `budget=99` on EIGHT cycles today against three in the previous 5,195**, and it is still firing on cycles with no session load at all (`20:51:02Z sweep=212.0s budget=99`). ⚠ **THE CAUSE IS NOT WHAT THIS ROW SAYS.** It says the probe *"scans the spend ledgers and therefore GROWS with the campaign"* — **the ledgers are STATIC at 2,956 rows and the spend has not moved since C1 closed.** `docs/ops/budget_watch.py:87` walks **`glob.glob(ROOT/**/record.json, recursive=True)`** in `_generation_depth()`: **it is a THIRD FULL-ARCHIVE LAYER, and W6 is SWEEP-1 wearing a different name** — a fixed 180 s cap over a scan that grows linearly with an archive heading for ~42,128 records. That also explains why the 2026-08-05 00:01Z timing of 70 s looked comfortable and is now over 180 s at 17,894 records. ⭐ **THE FIX IS ALREADY BUILT AND PROVEN: `docs/ops/record_shrink_cache.load_shrunken_records`.** `_generation_depth` reads only `arm` (str) and `generation` (int), both untouched by `_shrink`, so it is a drop-in. ⚠⚠ **ONE THING MUST BE CHECKED FIRST AND IT IS THE REASON THIS WAS NOT SHIPPED IN THE SAME SESSION: `budget_watch` is the ONLY archive walker in this repo that does NOT exclude `.pull_tmp*` / `_quarantined*`.** The cache DOES exclude them, so swapping it in silently changes the record set — those records key into their own `root` bucket, so any consumer iterating roots would see fewer. **It needs its own byte-identity proof against `git show HEAD:` before it goes live, exactly as SWEEP-1 got, and shipping a third same-day fix into a live board tool without one is precisely the pattern this ledger keeps paying for.** **NO CAMPAIGN EXPOSURE MEANWHILE:** `cycle.py` renders the timeout as *"that number is BLIND this cycle, which is not the same as healthy"* rather than as a reassuring value. **DO NOT RAISE THE 180 s TIMEOUT** — same rule as the 900 s cap. | ORIGINAL ROW, KEPT FOR PROVENANCE: **`budget_watch` ran out of its 180 s timeout and the board went `budget=99` — the third time in 5,195 cycles.** `cycle.py:939` runs it with `timeout=180`; `_run` renders a timeout as **rc=99**, and `cycle.py` then correctly raises *"that number is BLIND this cycle, which is not the same as healthy"*. **PROVEN-BENIGN and transient: the very next cycle read `budget=2 OK`.** ⚠ **BUT THE MARGIN IS THE FINDING.** Timed directly this pass: **70 s against a 180 s cap — a 2.6x margin on a probe that scans the spend ledgers and therefore GROWS with the campaign.** It breached only because this session was running whole-archive scans and a mutation suite concurrently on a 16-core box carrying **40 python processes**, which is the same self-inflicted contention as the 845 s sweep in the SPEED section. | a second `budget=99` in any 24 h, or a direct timing above ~120 s | **NEW ROW, 2026-08-05 00:01Z.** Same family as SWEEP-1: a fixed timeout over a linearly-growing scan. Serialise heavy scans against the cycle; do not raise the timeout to make it pass. |
| W1 | `gate_failure_drift` CUSUM | see the ESCALATED W1/D36 row above -- structurally permanent | **CUSUM reads 0.28, LOWER than the 0.99 -> 2.56 this row recorded.** The reason refines D36 rather than contradicting it: `sentinel_events.jsonl` shows **15 sentinel restarts**, and the CUSUM is process-local, so it resets on each one and re-crosses `h=0.15` within ~2 samples. **It is unbounded WITHIN a process and non-monotone ACROSS restarts, so quoting a rising trend was wrong.** The alarm is still permanent; only its magnitude is meaningless. |
| W2 | anthropic spend over the credit ESTIMATE | **SUPERSEDED by E-spend**, which is far more precise | E-spend measures **$8.7603 realized + $36.7418 estimated** across 2,956 ledger rows, with the confirmatory line 100% estimate. This row's "31% over" framing is coarser than the split now available and should not be quoted. |
| W3 | disk forecast to the 20 GB floor | preflight `disk` row | **39.0 GB free** against a CRITICAL floor of 20, i.e. 19.0 GB of headroom, stable at 38.6-39.0 all session while the archive grew ~500 records. Test records are ~480 KB, so the remaining ladder fits with room. **No longer trending; keep the row only as the standing check.** |
| W4 | repair jobs 83464 / 85065, ranked 309/314 and 314/314 | escalate only if still queued after ~24 h | ⭐ **RESOLVED, AND THE PREDICTION HELD.** Both are **RUNNING**: 83464 (`leg6` = gpt-5.6-luna) started 12:47:20, 85065 (`leg1` = deepseek) started 13:08:40 -- inside the 9-18 h drain estimated when the row was opened. **83464 is the repair for gpt-5.6-luna's seeds 192/193**, the two holes that cap that line at banked rung 189 against a frontier of 567. If it lands, gpt's banked rung moves by a very large step. |
| W5 | core line C1 chain | this gates the common rung leaving 0 | ⚠ **THE ROW WAS STALE BY 3 AND 2.** It said *"`tpe` owes 5 of 30, `bayes_opt` 4 of 30"*. **MEASURED: `tpe` holds 28 candidate records and `bayes_opt` 28, so each owes 2.** The chain floor is **0.37 d**, down from 4.64 d total. Still the binding term, and still the reason the common rung is 0. |

---

## RESOLVED — append-only, never deleted

| id | resolved | state | evidence |
|---|---|---|---|
| **P312** | 2026-08-04 RUN22 pass 5 | ⭐⭐⭐ **THE REMOTE-CONTROL CHANNEL HAS BEEN A ONE-WAY PIPE FOR THE WHOLE CAMPAIGN. TAMER COULD SEE EVERYTHING AND BE HEARD BY NOBODY.** FIXED, selftested, and PROVEN by a live round trip. | **HOW IT SURFACED.** Tamer, 2026-08-04: *"my issue was that I was typing it there, and you were not responding."* **THE CAUSE, MEASURED NOT GUESSED.** The entire inbound path is `publish_status.sh:34`: `git pull --rebase --quiet origin backup-2026-07-28 2>/dev/null \|\| git pull --rebase --quiet 2>/dev/null \|\| true`. Run by hand on this tree it returns **`error: cannot pull with rebase: You have unstaged changes.`** ⇒ **`git pull --rebase` REFUSES on a dirty working tree, and this tree is ALWAYS dirty — 102 modified paths at the moment of diagnosis**, because the watch logs churn every cycle. Both fallbacks fail identically, `2>/dev/null` hides the error and `\|\| true` swallows the code. **`git push` does NOT care about a dirty tree, so the OUTBOUND half worked perfectly throughout.** That asymmetry is the whole bug: he could always read the status page and could never reach the session. `cycle.py:740`'s CHANGED detector was never at fault — the file it watches simply never changed. ⚠ **AND THE LOG PROVES IT INDEPENDENTLY: in the whole campaign that file has never carried a single acknowledgement from the ops session** — only write-up and coord lane messages from 2026-08-01. Even a delivered instruction would have left him no evidence it had landed. **A HYPOTHESIS I TESTED FIRST AND DISCARDED**: that his edits went to `main`, GitHub's default branch. `main` is stale since **2026-07-06 and does not contain this file at all**, so that was not it — but it is why the fix reads EVERY candidate branch rather than one. **THE FIX — `docs/ops/remote_inbox.py`, polling every 60 s.** (1) Reads the instruction with **`git show origin/<branch>:docs/REMOTE_CONTROL.md`**, strictly read-only, immune to tree dirtiness, and incapable of disturbing a live campaign the way a rebase is. (2) ⚠ **DELIBERATELY NOT `git checkout origin/<b> -- <file>`, which is the obvious fix and would have DESTROYED 227 UNCOMMITTED LINES** of cross-lane messages sitting in that file. It rewrites ONLY the instruction fence. (3) Checks all candidate branches, so "which branch was he on" stops being a failure mode. (4) **Fails LOUD**: if no branch can be read it prints *"COULD NOT READ ... this is not the same as 'no new instruction'"* and returns non-zero — the exact fail-open it exists to remove. (5) **`--ack` writes a timestamped reply into the LOG and pushes it**, so a response appears where he typed. **VERIFICATION ON THE ARTEFACT, NOT THE HELPER.** ruff clean; **offline selftest 8/8**, including T1b which asserts the 227 unrelated lines SURVIVE and T2 which requires a fence-less document to be REFUSED rather than guessed at. Live `--check` reads both live branches and compares digests. **A REAL ROUND TRIP WAS COMPLETED: the acknowledgement is readable on `origin/myriad-cluster-and-tier-system` at 2026-08-04T23:53:35Z**, pushed to both branches, and `--status` reads `nothing pending`. ⚠⚠ **AND MY OWN FIRST LIVE RUN FAILED, ON A RULE THIS REPO ALREADY CARRIES.** `subprocess.run(..., text=True)` decodes with the SYSTEM codepage — cp1251 here — and `REMOTE_CONTROL.md` is UTF-8, so `git show` died with `UnicodeDecodeError: 'charmap' codec can't decode byte 0x98` **inside subprocess's own reader thread**, surfacing as a traceback plus an empty result: the tool reported *"no fence in that copy"* for a file whose fence was intact. **The standing cp1251 rule here is written about `print()`; it applies just as hard to DECODING SUBPROCESS OUTPUT, and that is the half nobody had written down.** |
| **P309-c + P310-b + P311-b** | 2026-08-04 RUN22 pass 4 | ⭐⭐⭐ **AN AUDITOR SENT AT MY OWN PASS-3 FIXES FOUND SIX DEFECTS, AND TWO WERE FAIL-OPENS I HAD INSTALLED WHILE CLOSING SOMEONE ELSE'S. FIFTH TIME IN THIS PROJECT. ALL FIXED, ALL FALSIFIED, AND THE FILE NOW HAS THE TESTS IT SHOULD HAVE HAD.** | **CRITICAL-1 — MY UN-WRAP SWALLOWED REAL RECORDS, ON THE ERROR CHANNEL.** `_RECORD_START = ^\d{4}-\d\d-\d\d ` assumed every record begins with a date. PowerShell decorates the first stderr write of a RE-LAUNCHED driver as `python.exe : 2026-07-28 23:09:19,022 ERROR ...`, and the rejoin glued each of those to the record above. **VERIFIED FIRST-HAND: 554 such records across the twelve logs, and ALL 554 carry a level token (h3 alone 349).** The auditor's controlled A/B put the cost at **INFO −542**; my own A/B on the corrected pattern recovers **+542**, two derivations agreeing. It proved on a synthetic log that an `ERROR`/`CRITICAL` from **a driver dying at start-up — exactly when that prefix appears — vanished from both the census and the samples.** ⚠ **AND THE COMMENT I WROTE BESIDE IT WAS EMPIRICALLY FALSE**: *"Level counting is unaffected because a continuation line carries no level token and was never counted."* It is preserved in the file as a correction rather than deleted. **CRITICAL-2 — MY PER-LINE REFLECTION FLOOR WAS ANTI-CORRELATED WITH THE SCIENCE AND SAT ONE RECORD FROM FIRING.** A rejected generation legitimately produces no reflection block (`parallel.py:1140` advances `prev_block` only `if best is not None`; `:1046` falls back to the initial prompt), so **the weakest model misses the preamble most — and the weakest model is the registered capability anchor.** Live: ten of eleven lines at 100.0%, `qwen3_5_9b` at **14/17 = 82.4% against an 80% floor**, its three misses all the reject-fallback case, and it carries **112 of the campaign's 193 reject markers by design**. **One more non-preamble candidate would have raised CRITICAL on the finding the campaign exists to produce.** FIXED with a BOUND, not a loosened threshold: each reject can deprive at most one later candidate of its preamble, so `misses <= rejects` is EXPLAINED and only `misses > rejects` is starvation. The floor is untouched. **MAJOR-3 — MY BACKSTOP LEFT THE MOST COLLAPSE-PRONE LEG COMPLETELY UNGUARDED.** It lived in the `else` branch, so KEYED legs kept only `reject_rate > exp_reject + 0.35` — for `qwen3_5_9b` that is **1.18 against a rate that cannot exceed 1.0, UNREACHABLE.** The auditor proved it: that leg at **100% reject over 40 attempts printed `[rejects] ok`, rc=0**, while the same collapse on an un-keyed leg fired correctly. My commit message said the backstop "sits well clear of the science" — true, and it concealed that the science leg had no guard at all. Backstop now applies to every leg. **MAJOR-4 — I NARROWED `timeout_events` INTO A BLIND SPOT ON THE PATH THAT MATTERED IN RUN 1.** `ssh_timeout_diagnostic` is emitted only from `submit.py:135`; the PULL uses its own `Popen` with a 3,600 s budget (`poll.py:185-190`, and `submit.py:57` says so), so a pull timeout emits nothing and became uncounted where the pre-fix test would have caught it. Now counted separately as **failed pull ATTEMPTS**, explicitly labelled as attempts rather than outages because 6,343 retries invite exactly the misreading that "351 timeout events" already caused here once. **AND THE LABEL I WROTE ON THE MENTIONS WAS REFUTED**: I called them *"retry notes, NOT one-per-event"*; measured per log they are **1:1 with the diagnostics on nine of ten legs** — the same events' `TimeoutExpired` repr. Corrected. **MINOR-5 — `_EXPECTED_PACK = 8` WAS THE WRONG CONSTANT AND ITS COMMENT WAS WRONG.** The only ledger row spans a window in which the campaign ran **`--pack 4` until 2026-07-31 ~11:10 UTC**, so ~2.5 of 3.4 days were pack 4; and `mean_slots_per_task` is `cpu_s / wallclock_s`, i.e. CPU-BUSY cores, so the requested width is a CEILING that start-up and idle can only pull below. At 8 ± 2.5 the upper half was physically unreachable. **Only the floor is kept** (`< 1.5`), which is the one failure the cross-check's own docstring names; no upper bound is asserted, because no honest single value exists for a mixed-pack window. **MINOR — the `NOTE:` line preceded the emptiness check**, so a root with leg dirs and zero attempts printed a threshold caveat instead of "no leg candidates resolved yet". Fixed. ⭐⭐⭐ **AND THE AUDITOR'S SHARPEST POINT: ALL FOUR PASS-3 CHANGES SHIPPED WITH ZERO REGRESSION COVERAGE, AGAINST THIS REPO'S OWN "new behaviour ALWAYS gets tests" RULE — and CRITICAL-1 was three lines of test away from being caught.** `run4_watch.py` now has a `--selftest`: **6/6**, on the driver's REAL wrapped grammar including the `python.exe : ` prefix. **FOUR MUTANTS, FOUR CAUGHT BY EXACTLY THEIR OWN CASE** — M1 the exe-less record start → T1+T1b, M2 the else-only backstop → T2, M3 the missing reject bypass → T3+T3b, **M4 a per-line check that can never fire → T4**, the over-correction control. ⚠ **TWO OF MY OWN TEST FIXTURES WERE WRONG FIRST**: T3/T4 used a single line, so the FLEET mean equalled that line's ratio and the fleet floor decided the outcome — a case that could not move through the mechanism it was named for. Both now carry a healthy 100/100 line beside the sick one. And my mutation runner reported M4 as SURVIVED because its own regex `(\w+):` could not match the label `T4 CONTROL:`. |
| **CRN-1** | 2026-08-04 RUN22 pass 4 | ✔ **PROVEN-BENIGN with the measurement — the H2 CRN premise HOLDS across the whole archive — AND I RE-DISCOVERED A KNOWN FALSE-ALARM CLASS ON THE WAY, WHICH IS THE PART WORTH KEEPING.** | **THE AUDIT (§11.1 item 2, previously unstarted).** `scripts/analyze_campaign.py::_paired` (`:1553-1557`) forms the headline paired contrast as `common = sorted(set(sa) & set(sb))` — **on the SEED NUMBER ALONE.** Grepped the whole file: **ZERO references to `env_fp`, `env_fingerprint`, `device`, `substrate`, `threads` or `train_steps`.** The analysis never re-verifies at the moment of pairing that the two records it is about to difference were produced under the same determinism envelope. ✔ **THE MINIMUM-n GUARDS, BY CONTRAST, ARE PRESENT AND CORRECT** — `n_seeds < 2` at `:1579`, `nc < 2` at `:1629`, `len(common) < 2` at `:1865` — so the across-seed bootstrap cannot run on a degenerate pair. **THE MEASUREMENT.** 5,410 H2-arm sealed-test records, **2,416 (line, seed) cells hold BOTH arms and are therefore pairable**, spread over eight leg lines. On the correct homogeneity key — `env_fingerprint.label`, i.e. the evaluation WINDOW and DEVICE, with the arm name excluded because it is SUPPOSED to differ — **all 2,416 pairs are identical**, as are all 2,416 realized-vector lengths (1571). ⇒ **The CRN premise holds; the missing assertion is INSURANCE, and what actually holds the property up is the seven record layers plus `campaign_watch._substrate_mix` (125 units, 0 mixed).** ⚠⚠ **AND TWO OF MY OWN PROBES WERE WRONG BEFORE ONE WAS RIGHT.** (1) My first comparison used the WHOLE `env_fingerprint` dict and reported **2,412 of 2,416 pairs "heterogeneous" — LIVE EXPOSURE**. The `label` field **embeds the arm name by design** (`campaign:distributional:test[3835,5406)` vs `campaign:scalar:...`), so every pair "differed" while the `env_json_sha256` beside it was identical and I printed it without reading it. (2) Corrected, exactly ONE cell of 2,416 differed — `gemini-2.5-flash` seed 175 — on `env_json_sha256` alone, with window, device and vector length identical, and seeds 173/174/176/177 all matching. I chased it as a genuine anomaly. ⭐ **IT IS P137, A FALSE-ALARM CLASS THIS REPOSITORY HAD ALREADY DIAGNOSED ON 2026-08-01 AND WRITTEN DOWN TWICE:** `docs/analysis/results_cycle.py:341` — *"`env_json_sha256` deliberately VARIES per record — keying on it..."* — and `ANALYSIS_LANE_SESSION4_2026-08-01.md:341`, which names it *"my P137 -> FAILS 'clean on a homogeneous unit' (the false alarm it causes)"*. It hashes `env.json`, which carries the SEED and other per-run content, so it is the WRONG key for homogeneity by construction. **The seed-175 finding is WITHDRAWN.** ⇒ **THE LESSON, and it is why this row is long: the repo's own analysis lane had already paid for this mistake, and I paid for it again because I did not search the record before believing my own script.** ⚠ **REGISTERED FOR TEARDOWN, NOT FIXED:** `scripts/**` is drift-fenced, so the CRN assertion cannot be added now. **When the D49 loader fix is applied at teardown, add a same-key assertion in `_paired`** — window+device equality per paired seed — so the analysis defends its own premise instead of inheriting it. Exposure today is ZERO, measured. |
| **P309 + P309-b + P310 + P311** | 2026-08-04 RUN22 pass 3 | ⭐⭐ **ALL FOUR CARRIED-FORWARD AUDITOR FINDINGS FIXED IN THEIR SECOND PASS, SO NO ROW AGED. Every one verified on the live ENTRY POINT, not the helper.** | **P309-b (F1) — THE D9 DIAGNOSTIC HAD MATCHED NOTHING FOR THE WHOLE CAMPAIGN.** `run4_watch.py` searched `child_already_exited=(\w+)` on the same PHYSICAL line as `ssh_timeout_diagnostic`, but the PowerShell host hard-wraps the log and `src/cluster/submit.py:135-140` puts the value on the NEXT line. `grep -c "ssh_timeout_diagnostic.*child_already_exited"` = **0 across all twelve logs** while the value is present **173 times**. Records are now rejoined before matching, the idiom `vanished_array_watch` and `transport_health` already use. **LIVE: `*** D9 EVIDENCE child_already_exited={'False': 164, 'True': 9}`** — an answer this instrument had never once delivered, matching an independent grep exactly. ⭐ **AND THE ANSWER IS ITSELF A FINDING: 164 of 173 say the remote command GENUINELY HUNG, so the ssh timeouts are cluster-side and NOT the parent pipe-handle race — the search moves cluster-side.** ⚠⚠ **MY FIRST VERSION OF THIS FIX WAS WRONG AND I CAUGHT IT ON THE ARTEFACT.** I widened `timeout_events` to the UNION of three phrases, taking it 113 -> **351** and making it LESS accurate: `ssh_timeout_diagnostic` is emitted once per event (ground truth **173**) while the looser phrases also appear in retry notes and the pull's own message. Now `timeout_events=173` exactly, with **+178 MENTIONS counted and labelled separately**. That also closes **F6**, where this file reported 113 against its fenced sibling's 179 from identical inputs. **P309 (F2) — `reflection_guard` VERDICTED ON A FLEET MEAN ONE LINE COULD NOT TRIP.** 1141/1144 = 99.7% against an 80% floor, largest line 125 of 1,144 — **a line falling to ZERO still reads 88.8% = "ok", and TWO whole lines must fail to breach it**, while the RUN 1 incident it exists to catch (241 prompts, 10 with the preamble) was PER-LINE, and the per-line numbers were computed and discarded. A per-line floor was ADDED beside the fleet one (nothing moved, so nothing is weakened), with a 10-candidate minimum so a fresh line's first record cannot read 0/1 and alarm. **P310 (F3) — `rejects_guard` COULD ONLY FIRE ON 4 OF 10 LEGS.** `EXPECTED_PASS_RATE` holds four keys; for the other six `exp_pass` is None and the `rc = 2` branch is unreachable — **60% of the leg population, including glm_5_2 at 13% and nemotron_3_super at 19%**, while the docstring promises "read against each model's MEASURED expectation". ⛔ **THE FIX WAS NOT TO INVENT EXPECTATIONS** — those four were MEASURED on 2026-07-25 and fabricating six more would be worse than the gap. Instead the absence is STATED in every affected row and in a summary line, and a **universal 95% backstop** catches only the DEFECT the docstring names ("our machinery rejecting everything") at a rate no capability gradient explains — deliberately far above the registered weakest anchor, qwen3.5-9b, which reads **84% against its expected 83%**, i.e. the gradient behaving exactly as designed. **P311 (F7) — A HEADLINE DISSERTATION NUMBER PRINTED WITH NO AGE.** `compute_ledger --report` showed `LATEST: 67,166 CPU-hours` from a single snapshot **87.7 h old**, while the module's own docstring says a mid-campaign reading is a LOWER BOUND over jobs completed by that moment. Okhrati explicitly docks missing or wrong wall-clock compute reporting. It now prints `age : 87.7 h old` plus an explicit STALE banner telling the reader to RE-SNAPSHOT and **not to extrapolate** — saying the age, never guessing a correction, because an extrapolated compute figure would be a fabrication. Second half: `mean_slots_per_task` was documented at `:205-213` as a cross-check that "must land near the packing depth we actually requested" and **nothing in the file compared it to anything**; it is now compared to the pack-8 the drivers actually request. ⚠ **STILL OPEN and registered, not fixed: `scripts/campaign_guards.py` carries the same D9 wrapped-line defect and is DRIFT-FENCED** — the `docs/ops/` copy is repaired, the fenced one waits for a deploy window. |
| **P307** | 2026-08-04 RUN22 pass 2 | ⭐⭐⭐ **A TOOL WHOSE STATED JOB IS "PRODUCED HERE FROM THE LIVE ARCHIVE" WAS PRINTING A HARDCODED, FALSE REASSURANCE THAT THE POPART CONFOUND DOES NOT TOUCH H2 — THE HEADLINE HYPOTHESIS.** FIXED: it now COMPUTES it. | **THE DEFECT.** `docs/ops/analysis_obligations.py:195-196` printed, as a literal string inside a function holding the whole archive: *"(Across the five LLM arms it is symmetric at ~3pp spread, so H2 is unaffected -- that half of 44.4 stands.)"* **It never computed it.** ⭐ **MEASURED THREE INDEPENDENT WAYS AND ALL THREE AGREE**: an auditor; then again from scratch by me on a different code path; and `docs/ops/retriage_alarms.py`, which has been COMPUTING it all along and printing `*** ASYMMETRIC -- RE-TRIAGE ***`. <br>`SEARCH` spread **6.8 pp** (the claim is roughly right here) · **`TEST` spread 67.2 pp** · **distributional 39.8% (1182/2972) vs scalar 74.2% (1773/2390) = 34.4 pp apart ON THE TWO ARMS OF THE HEADLINE CONTRAST**, on the SEALED tier where H2 is actually scored. `retriage_alarms` pooled reads 42.1% vs 73.1%. **Nowhere is it ~3 pp.** ⚠ **TWO INSTRUMENTS IN ONE REPOSITORY CONTRADICTED EACH OTHER AND THE ONE THAT *ASSERTED* WAS THE ONE THAT REASSURED.** A hardcoded number inside a live-archive tool cannot detect its own staleness. **THE FIX.** `load()` now carries the STAGE (root directory name only, no outcome field), and a new section (D2) computes the five-arm engagement table by stage, prints the H2 contrast, and fires an explicit NOT SYMMETRIC banner above 10 pp. ⚠⚠ **AND THE INTERPRETATION IS STATED RATHER THAN IMPLIED, BECAUSE OVERCLAIMING HERE WOULD BE ITS OWN DEFECT.** Under the identification principle only the reward PROGRAM varies across arms, and PopArt engages on `sigma_max = max(1.0, raw_rms)` of that program — so the gap is a **MEDIATOR on the fed -> code -> policy chain (exactly SQ2), not a threat to identification.** The defect fixed is the false claim of SYMMETRY; the asymmetry itself is mechanism and must be REPORTED beside H2. ⚠ **EFFECT-BLINDNESS PRESERVED**: `sigma_max > 1.0` is a training-mechanics flag; no Sharpe, CVaR, fitness or p-value is read, and the cycle board already prints this quantity's aggregate every sweep. **VERIFICATION**: ruff clean, live entry point re-run, the false sentence survives only inside the comment that quotes it, and a first draft of the new table clipped `1179/2971` to `1179/29` and was widened — a truncated denominator in an operator-facing table is the same defect class as a stale one. |
| **P308** | 2026-08-04 RUN22 pass 2 | ⭐ **`campaign_watch` COMPUTED A GUARD FAILURE AND THEN LEFT IT OUT OF THE ALERT — THREE FAIL-TOWARD-OK LEGS OF ONE CLASS, ALL FIXED.** | **(1) `rc` NEVER REACHED THE VERDICT.** `campaign_watch.py:134-152` ran the guards, printed `guards_rc=`, and then built `alert` from the NAMED guard set parsed out of stdout only. Whenever that parse produced nothing — a crash, an unreadable path, a format change — the tool printed the failing code beside the word `ok`. **(2) THE SCRIPT PATH WAS CWD-RELATIVE.** Demonstrated by the auditor: from the repo root `[ALERT] guards_rc=2 bad_guards=transport,truncation`; from elsewhere `[ALERT] guards_rc=2 bad_guards=none` — **a genuine guard CRITICAL and a `python: can't open file` were INDISTINGUISHABLE**, and only one contributed to the verdict. Now resolved from `__file__`. **(3) `sups >= 0` SUPPRESSED THE ALERT ON `_supervisors()` RETURNING ITS OWN -1 "could not measure" VALUE.** A monitor that goes quiet exactly when its probe breaks is the failure mode this ledger exists to stop; an unmeasurable supervisor count now ALERTS. ⚠ **The existing comment explaining why the NAMED set is tracked rather than the bare rc is CORRECT and was kept** — it is a reason to track the set as WELL, never a reason to drop the rc. The set catches a new guard failing; the rc catches the guards not having run at all. ruff clean, AST clean. |
| **F-gemini** | 2026-08-04 RUN22 pass 2 | ✔ **PROVEN-BENIGN with the measurement.** An auditor flagged that `driver_gemini-2_5-flash.log` and `driver_h3.log` had logged nothing for ~29 h and gemini's newest record was 43.9 h old, while no instrument in its target set distinguishes "silent because COMPLETE" from "silent because DEAD". | **They are complete.** All five gemini arms and gpt-5.6-luna's five and h3's one hold **569 directories each**, and S15's own verdict is `banked rung 568 ... COMPLETE -- every arm holds the full registered ladder` for all three lines. Their drivers are silent because they FINISHED. ⭐ **AND THE COVER EXISTS, JUST NOT IN THE AUDITED SET**: `session_preflight`'s `line_census` prints `roster=12 up=9 COMPLETE=gemini-2.5-flash,gpt-5.6-luna,h3` on every run. The auditor's structural point stands and is worth carrying — a dead line and a finished line look identical to those eight tools — but the campaign is not exposed, because preflight names the complete set explicitly. |
| **P306 + P306-b** | 2026-08-04 RUN22 pass 2 | ⭐⭐ **`occupancy_watch`'s CENTRAL QUANTITY WAS WRONG ON FOUR OF NINE LINES, BY THREE ORDERS OF MAGNITUDE ON TWO OF THEM — AND IT HAD RAISED ITS OWN FLAGSHIP ALARM ON A HEALTHY LINE.** Two independent defects pulling in OPPOSITE directions. FIXED, selftested, mutation-controlled. | **HOW IT WAS FOUND.** The pass-1 board flagged `sonnet-5` as **`3 pass(es)`** below the floor — the ACTIONABLE state this module exists to raise, whose own text says *"with an EMPTY queue, is the state the sawtooth cannot explain"*. Its driver read `437/445 done, 8 pending` with **one pack-8 job covering exactly those 8 units**. 100% coverage reported as 12.7%. **P306-a — A COMPLETED BATCH OWED WORK FOREVER.** The driver ends a batch with `[<b>] batch complete: {...}` and never emits a final `0 pending`, because completion is detected on the poll AFTER the last record lands. `owed_by_line` summed "the last progress line per batch", so a finished batch's stale non-zero `pending` was counted for the rest of the log. **MEASURED: sonnet-5 `owed=63` against 10 truly pending — 53 units (84%) from FIVE completed batches** (`sweep_t1` 11, `t3` 11, `t4` 10, `t5` 10, `t6` 11). **P306-b — AND THE SELFTEST I WROTE FOR P306-a FAILED, WHICH IS HOW THE BIGGER DEFECT SURFACED.** `PROGRESS` carried a **literal space** before `pending`. The log is hard-wrapped by the PowerShell host and the wrap falls right after the count (`... done, 8 \npending`), which after the newline-to-space collapse is a DOUBLE space. **3,385 of 24,549 progress records — 13.8% — were invisible**, and not evenly: <br>`glm-5_2` owed **1** against **2,691** · `kimi-k3` owed **2** against **2,692** · `deepseek-v4-pro` owed **0** against **60**. **A line owing 2,691 units and reported as owing 1 can NEVER be flagged under-covered** — the ratio divides by a near-zero denominator, which is exactly why kimi printed **247.273**. ⇒ **The instrument built to detect under-coverage was structurally blind to the two largest owing lines and failed toward OK.** `COMPLETE` had the same literal-space defect (`batch \ncomplete` is a real line in `driver_glm-5_2.log`), so it would have under-corrected P306-a on precisely the batches that had just finished. ⚠ **`vanished_array_watch` ALREADY CARRIES THIS EXACT LESSON in its own `SUBMITTED` pattern** (*"a single-space pattern matched none of the 14 multi-array blocks"*) — this file never received it. **A class fix is only as complete as the population you drew it over (P296), and the population was never swept.** **THE FIX.** `\s+` in both patterns; a batch whose `batch complete` appears POSITIONALLY AFTER its last progress line contributes 0; the correction is PRINTED (`P306: N unit(s) excluded ...`) rather than applied silently. **LIVE, BEFORE -> AFTER:** sonnet-5 owed 63 -> **8**, ratio 0.127 -> **1.000, alarm GONE**; glm 9 -> **2,690**; kimi 11 -> **2,690**, ratio 247.273 -> **1.011**; deepseek 6 -> **60**; core 42 -> **31**. Verdict now *"every line's fleet is proportionate to the work it owes"*, rc=0. **VERIFICATION.** ruff clean; **the module had NO TEST AT ALL**, which is how this survived a whole campaign — a `--selftest` was added on the driver's REAL hard-wrapped grammar, **3/3**. ⭐⭐ **FOUR MUTANTS, FOUR CAUGHT, each with a DISTINCT wrong answer so the discrimination is visible: M1** drop the completion exclusion (pre-P306) -> owed **16**; **M2** literal-space `PROGRESS` (pre-P306-b) -> owed **0**; **M2b** literal-space `COMPLETE` -> owed **16**; **M3** presence-only completion test -> owed **5**. ⭐ **M3 IS THE ONE THAT MATTERED: it is the control against my OWN fix OVER-correcting.** A batch can complete and then be re-entered in a later round, so a naive *"did this batch ever complete?"* test would DROP LIVE WORK and blind the alarm in the opposite direction — worse than the defect. The fixture's case C is a completed-then-re-entered batch and it is the reason the test is positional. ⚠ **NOT CLAIMED: `_job_token` uses substring matching (`if tok in jobname`), which is the `crash_watchdog` class. I checked it and it is SAFE TODAY** — tokens are model names (`deepseek_v4_pro`, `kimi_k3`), not leg tags, so the `leg1`/`leg10` collision does not arise, and `core` is already guarded as `c1_`. Left as-is; recorded so nobody re-derives it. |
| **P305-b** | 2026-08-04 RUN22 pass 1 | ⭐⭐ **AN AUDITOR SENT AT MY OWN SAME-DAY FIX FOUND A FAIL-OPEN IN IT, WITHIN THE HOUR — THE FOURTH TIME THIS PROJECT HAS INSTALLED ONE WHILE REMOVING A FALSE ALARM.** Four defects, all FIXED, all falsified. | **F1 — CRITICAL, AND IT IS THE ONE P305 ITSELF CAUSED TO BITE.** The `unresolved` list's own declaration has ALWAYS named three untested states — no id, unparsed timestamp, qacct unreachable — and **only the no-id branch ever appended.** The other two fell through to `sys.exit(0)` under the banner *"no vanished arrays detected"*. **This was pre-existing, and P305 is what exposed it: the chronic rc=2 had been masking it.** ⚠ **MEASURED LIVE**: `leg10_leg_kimi_k3_h2_pair_test`, arrays absent from the queue, **age 1,048 min = 17.5 h, past the 15 h `h_rt`**, qacct unreachable — reported as all-clear. **FIXED**: both branches now append and reach rc=2. ⭐ **AND THE OPERATIONAL HALF WAS CHASED TO GROUND RATHER THAN LEFT AS A CODE FIX: that block is BENIGN.** kimi's `h2_pair` now holds **31 records on BOTH arms** on disk — the arrays COMPLETED, which is exactly the P186 case the qacct test exists to catch, and the line has since entered C4 with **340 sweep jobs queued**. Nothing vanished. **The instrument still could not tell, and that is what was fixed.** **F2 — MAJOR: A FAILED `qstat` READ AS "NOTHING IS ALIVE", DIRECTLY UNDER A COMMENT OF MINE SAYING IT MUST NOT.** `ET.fromstring(out.stdout or "<x/>")` turns an empty/failed response into a well-formed EMPTY document: zero ids, zero names, **every pending block reads as VANISHED**. `out.returncode` was never inspected. The dangerous trigger is qmaster unreachable while ssh and qacct still answer, in which case nothing downgrades the alarm and the whole board fires at once. **FIXED**: `rc != 0 or empty stdout -> SystemExit(99)`, the code `cycle.py:1480` routes to ATTENTION. **F3 — MAJOR: MY OWN NEW TEST HOOK COULD REACH THE CLUSTER.** The offline guard tested `_LIVE_OVERRIDE` alone, so `--live-names=` looked offline and was not — a fixture carrying ids would have fired the real `qacct` ssh, six scans of a 33 GB accounting file on a login node (the P204 abuse). **The selftest could never have caught it, because cases G/H use a fixture with no ids.** FIXED via a single `_OFFLINE` predicate. **F4 — MINOR: THE ALL-CLEAR LINE WAS FACTUALLY FALSE** — *"every batch resolved to a job id"* while four blocks had resolved by NAME. FIXED to state the split. **F5 — MINOR: three stale `cycle.py:9xx` comment references** corrected to `:1455 / :1460 / :1466 / :1480`, verified line by line against the live file. **VERIFICATION.** ruff clean; **selftest 10/10** (E's expected exit code changed 0 -> 2, and **that change IS the falsification: the old case asserted the fail-open**). ⚠ **CASE J HAD TO BE ISOLATED AFTER IT FAILED FOR THE WRONG REASON** — it reused case A's fixture, which case C unlinks, so it read the fresh log, landed in the grace window and reported "benign", a green with nothing to do with the guard under test. Own fixture now. ⭐⭐ **AND THE TWO ERROR PATHS I RECORDED LAST PASS AS "verified by reading, not execution" ARE NOW PROVEN BY EXECUTION**, by stubbing the ssh call in a scratchpad copy: rc=255+empty, malformed XML and whitespace-only all reach rc=99 with no VANISHED. ⚠⚠ **AND MY FIRST CONTROL FOR THAT FAILED, WHICH IS WORTH MORE THAN IF IT HAD PASSED.** The pre-fix comparison returned rc=2, not the expected VANISHED, because I had stubbed only the `qstat` ssh — so the pre-fix code went on to make a REAL `qacct` call, that call answered, and the verdict was downgraded to UNKNOWN. **The control was measuring the qacct probe, not the parser under test.** A failed control means either the control or the fix is broken and you do not get to guess which. Re-run with BOTH ssh calls stubbed: **pre-fix parser rc=1 `*** VANISHED ARRAY ***`, fixed parser rc=99 no VANISHED, on byte-identical input.** The fix discriminates; the first control did not. **Mutation control round 2 final: 4 of 4 selftest-reachable mutants caught by exactly their own cases (M1→G, M2→H, M4→E+I, M6→J), and 3 of 3 error paths proven by execution.** **THREE STANDING ITEMS THE AUDITOR RAISED AND I AM NOT CLOSING**, recorded rather than quietly dropped: neither witness filters job STATE, so an `Eqw` job — precisely what the site cleanup purges — reads as alive on BOTH routes (pre-existing, symmetric, and no `Eqw` exists today); the name route has no recency notion, so a straggler from an earlier round could in principle rescue a block whose current round vanished (narrow, not constructible from the real logs); and `cycle.py:1482-1483` still glosses rc=99 as *"the probe could not be launched"*, which no longer covers the two new 99 sites. |
| **P305** | 2026-08-04 RUN22 pass 1 | ⭐ **FIXED + FALSIFIED + MUTATION-CONTROLLED — THE DETECTOR HAD A SECOND, BETTER WITNESS AVAILABLE IN THE `qstat` IT WAS ALREADY RUNNING, AND WAS THROWING IT AWAY.** | **THE STATE.** `vanished_array_watch` exited 2 on every pass and held `CYCLE_LOG.md` at **ATTN for an hour** (20:59Z onward) over five `qwen3_6-27b` sweep tiers carrying **2,233 pending units** that it could not resolve. RUN 21 was right to make them VISIBLE (P304: an UNKNOWN is not a negative), but the tool had no way to ever resolve them, so the board's first-read file sat amber on a benign, hourly-recurring state. **THE DEFECT.** Blocks were resolved ONLY by array ids scraped from a hard-wrapped driver log. ⚠ **AND THE REASON THE LOG CANNOT SUPPLY THEM IS STRUCTURAL, WHICH I LEARNED ONLY BY RUNNING THE FIX:** `driver.py:272` dedupes by job NAME, so a driver restarted by its supervisor **ADOPTS** the existing jobs and never writes a fresh `submitted ... as N array(s)` line. **After every supervisor restart the log route is blind to the adopted work by construction** — that is the normal state, not an edge case. ⚠⚠ **THE OBVIOUS DISCRIMINATOR WAS REFUTED BEFORE IT WAS USED, AND THIS IS THE PART WORTH KEEPING.** "`round 0` means never submitted" is FALSE — `round` counts REQUEUES — and a sweep of all twelve driver logs found **180 blocks reporting `round 0` while carrying a submission record**. Building on it would have blinded the detector across those 180 blocks. **THE FIX.** `live_job_ids()` -> `live_jobs() -> (ids, names)` off ONE `qstat -u ucestes -xml` (**`-xml` is required: plain `qstat` truncates `JB_name` to ten characters, P276**), plus `block_is_alive_by_name`, which matches `name == blk or name.startswith(blk + "_")`. ⚠ **THE UNDERSCORE IS LOAD-BEARING**: a bare `startswith` makes `c1_tpe_c1` match `c1_tpe_c12_p01`, the same substring class that let `crash_watchdog` recover `scalar` from `scalar_cvar5`. **VERIFICATION, AND IT WAS DONE ON THE ARTEFACT RATHER THAN THE HELPER.** AST parse OK; `ruff` clean; symbol diff — zero remaining references to the renamed `live_job_ids` anywhere in `docs/`; **selftest 8/8** (six original cases kept intact). **LIVE ENTRY POINT: rc=2 -> rc=0**, all 23 pending blocks resolved, four of them "by NAME", and the four name-resolved tiers independently confirmed against my own `qstat -xml` as holding real jobs (t2 3r, t3 1Rr, t4 1Rr+1r, t6 2r). ⭐⭐ **TRUE MUTATION CONTROL, mutating the FIXED file so each mutant is caught by the case NAMED for it and by no other**: **M1** delete the name route (== the pre-P305 behaviour) -> **only case G red**; **M2** bare `startswith` without the underscore -> **only case H red**. Two mutants, two caught, no cross-talk. ⚠ **ONE HONEST GAP, STATED NOT TESTED AROUND:** mutant **M3** (treat an unparsable `qstat -xml` as an empty result — the fail-open shape) is **NOT reachable from the selftest**, because the override path bypasses the parser. The guard raises `SystemExit(99)` and was verified by reading, not by execution; 99 is the code `cycle.py:1481` routes to ATTENTION, so a parse failure cannot read as "nothing alive". **That case remains unproven by test and should be closed by a future pass.** |
| **P303** | 2026-08-04 RUN21 pass 1 | ⚠ **A RISK P301 CREATED, CLOSED BEFORE IT FIRED — ONE FULL-ARCHIVE SCAN PER SWEEP.** | Moving the science audit out of the ssh gate let it coincide with the provenance seal, and both are full-archive scans. **The first cycle in which both came due measured `sweep=783.5s` against the 900 s cap `session_preflight.check_cycle_log` reads as "the monitoring loop is DEAD" — a margin of 117 s, on a sweep that grows linearly toward the ~42,000-record end state.** A false loop-is-dead would have been a defect I introduced while fixing one. `_heavy_budget = 1` now allows at most one heavy scan per sweep; the deferred one runs on the next sweep and **neither is starved, because a probe that runs resets its own age and is not due next time.** ⚠ **It throttles the WORK only — both verdicts are still CARRIED every cycle by `_cached_probe`, which is the entire point of P301.** ⚠ **AND THE MEASUREMENT THAT MUST TRAVEL WITH THIS ROW, because it stops the fix being over-claimed: the NEXT cycle swept 655.0 s having run NEITHER heavy probe** (STATE ages 822.8 / 820.1 / 685.1 s, all cached). So the sweep is elevated for a reason this guard does not address, and P303 bounds the known worst case rather than explaining the baseline. Pre-P301 sweeps in the same hour ran 221.9-441.3 s, so the variance predates the change. **OPEN as a WATCH row, not closed.** 31/31 `test_cycle.py`, ruff clean, symbol-diff NONE. |
| **P301** | 2026-08-04 RUN21 pass 1 | ⭐⭐ **THE SAME DEFECT, A THIRD TIME IN ONE DAY, ONE GATE HIGHER UP — AND A SECOND AUDITOR FOUND IT IN THE FIX THE FIRST AUDITOR HAD ALREADY CORRECTED.** | **P298-b fixed the INNER cadence gate and left the OUTER one.** The corrected science block still sat inside `if args.ssh or ssh_due:`, so the cached re-read only executed on ssh cycles. **MEASURED over 2026-08-04 10:00-16:59Z: 77 cycles, 17 carrying `cores=` — the deep-science verdict was evaluated on 22% of cycles, with a longest run of SEVEN consecutive unevaluated cycles and a maximum ssh gap of 3,222 s.** So a live science RED would have left `CYCLE_LOG.md` — the file a session is instructed to read FIRST — reading OK for up to **54 minutes**, which is WORSE than the 30-minute window P298-b was written to close. The two probes the idiom was copied from are evaluated EVERY cycle, which is exactly why theirs works. ⭐ **AND THE CLASS WAS LARGER THAN THE FIX: `vanished_array_watch` and `record_provenance_seal` had NO CACHE AT ALL** — both seeded `-1` and evaluated only on ssh cycles, so their verdicts were dropped on the other 78% too. That is P296's lesson again (*a class fix is only as complete as the population you drew it over*), so all three now go through **one** helper. **`_cached_probe(stamp, min_secs, argv, timeout, may_run)`** returns `(rc, out, cached, age)` with `None` = "no verdict has ever been produced" (the only value that reaches no alarm), `98` = "a verdict existed and its cache is unreadable", and every other value the probe's own rc, fresh or carried. The science audit and the seal are LOCAL scans and never needed the ssh gate at all; only `vanished_array_watch` keeps `may_run` bound to it, because it needs a login-node `qstat`. `-1` is gone from all three STATE fields — it collided with a genuine `-1` from a signal death or a Windows `0xFFFFFFFF` exit, the exact P230/P232 collision the surrounding comment invoked — and each rc now travels with the AGE of the attempt it came from. **Also closed here: the verdict parser could KILL THE SWEEP.** `int(_first) if _first.lstrip("-").isdigit() else 98` accepts `"--5"` and the superscript `"²"`, both of which then raise in `int()`; the siblings wrap their probes in `try/except` and this block did not. It parses inside `try/except ValueError` now. ⭐⭐ **AND THE BLOCK THAT HAD FAILED OPEN TWICE IN ONE DAY HAD ZERO TESTS while its sibling row had fifteen — `docs/ops/test_cycle.py` covered only `_sci_token`. Eleven cases added, all passing, 31/31 for the file.** The decisive one is **P3**: a cached FAILURE must be carried, not dropped, and it fails against every version of this code before P301. **Live: loop alive across the change, `CYCLE_LOOP_STDERR.log` 0 bytes, `drift=0`, module import clean.** |
| **P302** | 2026-08-04 RUN21 pass 1 | ⚠ **REGISTERED, NOT FIXED — A ROW THAT GRADES THE PUBLISHER BY A PROXY IT NEVER MEASURES, AND ITS FAILURE IS INVISIBLE TO BOTH ROWS THAT COULD SEE IT.** | Found by the second auditor while sweeping for the *infer-content-from-a-name* class. **`session_preflight.check_status_page` grades publication by the LOCAL page's mtime.** `publish_status.sh:259` writes the page unconditionally, and `:501` restores it with `git checkout --` when the ASCII gate rejects it — which REFRESHES the mtime; `:527` documents that `--only` returns rc=128 while a merge is in progress. **In either state the local page keeps looking fresh, nothing accumulates unpushed, so `check_git_backup` ALSO reads OK — both rows green while the page Tamer reads on his phone is frozen.** Fixing it means checking the remote (`git log origin/<branch> -1` or a push timestamp), a network call this row deliberately avoids. **Registered in the row's own docstring so nobody reads it as proof of publication**, which is the honest half of the fix and the half that survives without a network call. Two smaller corrections landed with it: the constants block cited **`check_publish_loop`, a function that does not exist anywhere in this repository** (it is `check_status_page`), and the "~67 s" publisher cadence quoted there is the CONFIGURED sleep, not the measured spacing. |
| **P299 + P299-b + P299-c** | 2026-08-04 RUN21 pass 1 | ⭐ **FIXED + FALSIFIED + MUTATION-CONTROLLED — AND THE FIRST VERSION OF MY OWN FIX WAS UNSOUND IN A WAY THIS REPOSITORY ALREADY HELD THE COUNTEREXAMPLE TO.** | **P299, the original defect.** `session_preflight.check_git_backup` reported *"N commit(s) on NO REMOTE AT ALL -- this work exists only on this machine"* whenever no remote ref contained HEAD, which is the **normal ~77-second state** between the status publisher's auto-commit and its push. It also counted against a **hardcoded branch name**, so the number was meaningless on any other branch while the verdict still spoke with authority. Replaced by `git rev-list --count HEAD --not --remotes` — branch-agnostic, and exactly the dangerous quantity. **P299-b, found by an auditor sent at that same fix within the hour, and all three findings verified first-hand before acting.** (1) ⚠⚠ **IT GRADED ON THE COMMIT SUBJECT, WHICH IS NOT PROOF OF CONTENT — and commit `d7b85965` in this very repository has subject `status: T+147h38m - 10/12 lines up` while carrying 366 insertions across `CHANGELOG.md`, `stage_eta.py`, `run_record_layers.sh`, `session_preflight.py` and `FLAWLESS_LEDGER.md`.** It was a bare `git commit` sweeping a dirty index, which is precisely why `--only docs/RUN4_STATUS.md` was added to `publish_status.sh:527` the same day (P251). **A subject-only test would have graded that commit safe to leave unpushed.** Now a publisher commit must carry the prefix **AND** touch exactly `docs/RUN4_STATUS.md`, read from `--name-only` in the same call. (2) **`IndexError` crashed the entire preflight** when `n_local > 5` and every subject was empty, because empty subjects were filtered out of the very list it then indexed — and those same empty subjects graded as publisher commits. Both closed by requiring the parse to account for **exactly `n_local`** commits; anything unaccounted for is UNKNOWN and routes to ATTENTION. (3) The stated publisher cadence (*"~2 min"*, *"~10 minutes"*) was **wrong and contradicted by this same file 140 lines away**; measured over the last 60 publisher commits: **median 77 s, mean 76 s, max 113 s**, so five commits is ~6 min of a stuck publisher, not ten. Corrected, along with a stale docstring sentence that P299 had falsified without editing. ⭐ **AND THE COMMITTED MUTATION-CONTROL SUITE WAS BROKEN BY MY FIRST FIX AND I DID NOT RUN IT** — `docs/ops/test_session_preflight.py` stubs `sh` on a TWO-command model, the new row asks THREE questions, and its **CONTROL case went RED** while four others passed only because `"abc commit"` fails `.isdigit()`. I had used a private stub in the scratchpad instead. The suite now models the real interface, keeps every original case as a named intent, and adds **eight** new ones. **44 passed, 0 failed.** ⭐⭐ **AND THE TEST IS PROVEN TO DISCRIMINATE BY TRUE MUTATION CONTROL — mutating the FIXED code, not the old code, because the old code answers different questions and can pass or fail for unrelated reasons.** Four mutants, four caught: M1 grade on the subject only → `d7b85965 class` RED · M2 drop the parse-accounts-for-every-commit guard → `listing accounts for fewer` RED · M3 raise the race max to 500 → `publisher STUCK` RED · M4 lenient count parse → RED, but **only after I added an isolating case**: the first count case passed against the lenient parse too, for an unrelated reason, so it was testing nothing. **A test that passes against the mutant is not a test.** ⭐⭐⭐ **P299-c, AND IT IS THE SHARPEST TESTING LESSON OF THE SESSION: THE SECOND AUDITOR SHOWED THAT MY REBUILT SUITE STILL COULD NOT SEE THE P257 MACHINERY AT ALL.** Five separate mutations — deleting `_is_ref`'s entire body, dropping its `/HEAD` clause, and dropping each of the three `rc != 0` terms from the UNKNOWN guard — **passed the whole suite undetected**, because four cases used a fixture with one substantive commit and therefore reached ATTENTION through the substantive-work path no matter what those guards did. **They passed for a reason unrelated to their own names.** Rebuilt on an ISOLATION RULE: a case must be able to move only through the mechanism it is named for, so those four now use `(0, "0\n")` with an empty listing, the only fixture in which the guard is the sole thing that can raise. ⚠ **And one honest consequence had to be STATED rather than tested around: after P299, `_is_ref` no longer affects any VERDICT** — the verdict comes from `rev-list --count`, and `holding` supplies only the "where" text. That is safe, and the safety runs through the count: a broken remote ref is skipped by `--not --remotes`, which excludes fewer commits and pushes the count UP, never down. So those two cases now assert on the DETAIL STRING, the only place the filter still lives; asserting a verdict there would be asserting something the code no longer decides. **Final: 47 passed, 0 failed, and TEN mutants, ten caught** — including M9, which needed its own isolating fixture (`(128, "0\n")`: git errors while its output happens to parse, so a non-zero rc must be UNKNOWN however plausible the bytes beside it look). Live: `session_preflight --full` **VERDICT OK, 17/17**. |
| **P298 + P298-b** | 2026-08-04 RUN21 pass 1 | ⭐ **FIXED + FALSIFIED ACROSS NINE STATES — AND MY OWN FIRST FIX TURNED A FALSE ALARM INTO A FAIL-OPEN, WHICH IS THE WORSE DEFECT.** | **P298, the original defect: a FALSE REASON PRINTED ON THE LIVE BOARD.** `cycle.py` seeded `_sci_rc = -1` and overwrote it only when the 1800 s cadence gate opened, so on every ssh pass where the rate limiter **correctly skipped** the audit the `elif _sci_rc != 0` branch printed *"the science audit could not run this cycle; new records are UNAUDITED for science"* and flipped the cycle verdict OK → ATTN. **Seven live instances in `ALERTS.txt`, the last at 15:16:24Z**, while the audit itself returns **rc=0 clean** — verified by hand at 16:07Z and again by layer L3 at 16:12Z. The ssh layer runs on the 1200 s ELAPSED trigger against an 1800 s audit cadence, so `ceil(1800/1200) = 2` and the bogus line fired on **one ssh pass in two**, not one in three as my first comment claimed; the ALERTS blocks at 13:51:17Z, 14:32:56Z and 15:16:24Z are 41.6 and 43.5 min apart, exactly two ssh periods. ⚠⚠ **P298-b, found by an auditor sent at that fix: MY CORRECTION DROPPED THE VERDICT INSTEAD OF CARRYING IT.** The stamp is written after **every** attempt regardless of rc, so once a real audit returned 1 or 99 the next ~1800 s of ssh passes were "not due", raised **nothing**, and the board would have read **OK during a live unresolved science breach** — with an info line positively asserting that the previous pass *"still stands"*. Pre-fix those cycles at least stayed ATTN, for the wrong reason. **I removed a false alarm and installed a silent one.** ⭐ **THE CORRECT IDIOM WAS ALREADY IN THIS FILE, 550 LINES ABOVE, AND MY COMMENT CLAIMED TO BE USING IT.** `sandbox_gap` (`:770`) and `integrity_gate` (`:845`) cache the rc **into** the stamp and **re-evaluate it on the skip path**, unreadable → 98 → the not-clean branch. I had adopted only the timing half. **A cadence gate may throttle the WORK; it may never throttle the VERDICT.** ⭐⭐ **FALSIFIED ON NINE STATES by exec'ing the real sliced source of both files.** The decisive one is **R (not due, last audit returned 1)**: P298-v1 shows `alerts=0 attn=0 info=1`; the fix shows `alerts=1` reading *"DEEP SCIENCE AUDIT FAILED (CACHED verdict, audited 5.0 min ago)"*. **S** (cached 99) → ATTN · **A** (cached 0) → info only, the P298 case · **L** (legacy float stamp) and **T** (torn/empty) → 98 → ATTN, fail-closed · **B/C/D** (due, rc 99/1/0) unchanged · **N** (no stamp) → still DUE, fail-toward-running. The stamp is also asserted to persist the rc. ⚠ **AND THE LEGACY-FORMAT TRANSITION WAS A LIVE HAZARD THAT HAD TO BE CLOSED BY HAND:** the stamp still held `1785861193.7413425`, so the next not-due cycle would have raised a spurious `rc=98`. Migrated to `0\n` — a **measured** verdict, not an assumption: the 16:33:13Z cycle ran the audit and its line is `OK` with zero alerts and zero attention, which is reachable only at rc=0, and two independent hand runs agree — with `os.utime` restoring the original mtime so the cadence is untouched. Loop verified alive across four subsequent cycles, `CYCLE_LOOP_STDERR.log` **0 bytes**, `drift=0`. |
| **P297** (the last five self-audit rows) | 2026-08-04 RUN20 pass 18 | ⭐ **FIXED + FALSIFIED, INCLUDING THE ONE WHERE I WAS SIMPLY WRONG AND SAID SO TO TAMER.** | **(4) THE LANE CACHE KEY OMITTED THE HALF OF THE INPUT THAT CHANGES.** I told Tamer the cache was *"not a weakening"*. **The auditor showed that is wrong and it is:** the verified property is JOINT over the loader and the archive, and `scripts/analyze_campaign.py` is **DRIFT-FENCED for the campaign's duration**, so its size and mtime can never change and the TTL was the SOLE invalidator. **My justification was true and irrelevant to the reachable trigger.** The key now carries a cheap ARCHIVE SIGNATURE (the sorted top-level line-directory names and their count -- one `iterdir`, no walk), covering exactly the uncovered case: a new or restored line subtree causing cross-line run_id collapse. **FALSIFIED: with 39 top-level directories, the PRE-FIX key does NOT change when a line appears and the SHIPPED key DOES.** ⭐ **AND THE LIVE RUN DEMONSTRATED THE DESIGN EXACTLY: cold 131 s, warm 0 s, and the only difference between the two outputs was `2 .pull_tmp dir(s)` -> `3` -- the CHEAP half is genuinely live on every call while the expensive loader half is cached.** **(5) THE PROBE DISCARDED ITS SUBPROCESS RETURN CODE** -- the precise pattern that failed OPEN in RUN 19, where a git warning on stderr became "safe off-machine". A non-zero rc with parseable stdout was silently accepted; it now returns UNKNOWN with the rc and stderr. **(10) ALL THREE `_shrink` DOCSTRINGS CLAIMED "any future code that indexes or `len()`s one FAILS LOUDLY".** FALSE where the guard idiom is `isinstance(x, (int, float))`, which rejects a list and **ACCEPTS an int**. Corrected to the true, narrower statement, with the direction stated (benign: such a guard admits more, suppresses nothing). ⚠ **My first repair MANGLED all three docstrings** by replacing only the tail of the sentence and leaving the head -- caught by grepping the artefact for the seam rather than trusting the patch script's `OK`, and repaired to zero occurrences. **P256, for the third time in one session: verify the ARTEFACT, never the patch script's exit code.** All four files ruff clean; `science_watch` re-run live at rc=0 over 13,383 records. |
| **P296** | 2026-08-04 RUN20 pass 17 | ⭐ **FIXED + FALSIFIED. I APPLIED A CLASS FIX AND MISSED THREE MEMBERS OF THE CLASS, ON THE SAME DAY.** | The auditor's finding, and it is the sharpest process lesson of the session: **`science_watch`, `results_audit` and `integrity_gate` still certified an EMPTY archive as clean** -- printing *"science ok"*, *"no hard invariant failed"* and *"I1 ... I6 -- all clean"*, each exiting 0 over zero records. **That is P286 exactly, in three files I edited the SAME DAY I fixed it in six others.** ⇒ **THE CAUSE IS THE SHAPE OF MY OWN SEARCH: I enumerated "the seven gated layers" and fixed the class within that list, instead of enumerating "everything that walks the archive".** A class fix is only as complete as the population you drew it over -- the §7① lesson, applied to a remediation rather than to a measurement. **FALSIFIED on an empty directory: `integrity_gate` rc=1 `I0 vacuity: 1 breach(es)`, `results_audit` rc=2 CANNOT VOUCH, `science_watch` rc=2 CANNOT VOUCH -- all three exited 0 with a CLEAN banner before.** ⚠ **`integrity_gate`'s guard is raised as a BREACH rather than a bare exit, deliberately: that file's contract is "an empty breach list means every invariant HELD", and it did not hold -- it was never evaluated.** **NO REGRESSION on the live archive: `integrity_gate` rc=0 with its full six-invariant OK line, `results_audit` rc=0 with its report.** Also in this pass: `loginnode_guard`'s USAGE table still documented three exit codes after P279 added a fourth -- corrected, because the rationale block documented `UNKNOWN_RC` while the text a reader actually sees did not. |
| **P295 / A-d14-successor** | 2026-08-04 RUN20 pass 16 | ⚠⚠ **MY P293 REASON WAS FALSE AND IT WAS PRINTED ON THE LIVE BOARD EVERY CYCLE. CORRECTED, AND THE `campaign.py` REGISTER IS OPENED.** | **THE CORRECTION FIRST, because it is mine.** I asserted -- in `cycle.py`'s comment, in its PRINTED TEXT, in this ledger, in the CHANGELOG and to Tamer -- that the ARM_CRASH marker *"CANNOT clear"* because `campaign.py` unlinks it *"only inside the C1 path"*. **A read-only auditor read all 2,072 lines and refuted it, and I verified first-hand at `campaign.py:1897-1902`: the unlink sits at the TOP LEVEL of `run_campaign_tiered`, immediately after the `if _crashed: ... return out` block, and every invocation re-runs C1 from the top before reaching it. A relaunch that clears C1 without a raising arm DOES clear the marker.** P269's lesson exactly -- *a false invariant is worse than a documented exception because the next session reasons from it* -- and this one was not merely commented, it was **printed**. ★ **THE FIX ITSELF (P293) REMAINS CORRECT; ONLY THE REASON CHANGES**, and the three things that ARE true each independently justify the demotion: **(1)** the clear horizon **exceeds the observation window** -- a complete clean C1 pass, which for a line mid-search is DAYS (nemotron's generations measured **25.3 h and 12.3 h**); **(2)** the clear condition is **WEAKER than the alarm condition** -- `_crashed` counts only results carrying an `error` key, so a pass in which arms returned `no_winner` or an R115 ineligibility clears the marker while the line is genuinely degraded; **(3)** the unlink's `except Exception: pass` is **completely silent**, so a transient Windows lock makes it genuinely permanent with nothing reporting it -- **that is the real "cannot clear" path, and it is not the one I named.** Verified: the false strings are now absent from the file (grep count 0), ruff clean, symbol-diffed, moved in atomically. ⛔ **AND THE AUDIT OPENED THE `campaign.py`/`driver.py` DEPLOY-WINDOW REGISTER -- SEE `docs/DEFERRED_FIXES_RUN4.md`.** Twelve findings over 100% of both fenced files, headed by **F1 (CRITICAL): an arm that fails SELECTION vanishes from C2 AND C4 with no log, no marker and no summary field** -- `campaign.py:1794-1795` returns without setting `winners[arm]` and both `:1905` and `:1980` filter with `if a in winners`. **Its LOUD variant is covered** (the C3 integrity gate reads `present=0/30`, exits 3, and the supervisor deliberately does not relaunch); **its SILENT variant -- an arm with complete core records whose selection later fails -- is covered by NOTHING**, and it is a silent cap on the COMMON RUNG. |
| **P294** (four defects in MY OWN fixes, same session) | 2026-08-04 RUN20 pass 15 | ⭐ **FIXED + FALSIFIED. AN AUDITOR SENT AT THIS SESSION'S OWN FOURTEEN CHANGES RETURNED TWELVE FINDINGS, AND ONE OF THEM WAS A LIVE FALSE-ALARM GENERATOR I HAD INTRODUCED HOURS EARLIER.** | **THE RULE HELD AGAIN: the author must not grade their own work.** RUN 19 had three of its own fixes defective; this session had four structural ones, and I would not have found them. **(A) THE LIVE ONE. My P286 vacuity guard in `record_provenance_seal.py` fires on a LEGITIMATE ZERO.** `cycle.py:1306` runs the seal as `--since-state`; in that mode an already-sealed record hits `skipped += 1; continue` at `:139` and NEVER reaches `n += 1` at `:149`, so **`n == 0` also means "no NEW record since the last clean pass"** -- the normal state during any quiet interval, every transport outage, **the announced Aug-12 maintenance ("may run two days")** and permanently after the Aug-27 stop. `cycle.py:1316` would then have announced *"the per-record seal could not run this cycle; new records are UNSEALED until it does"* on a cycle where it ran perfectly. **I built a false-alarm generator while removing one.** **FALSIFIED: a second consecutive `--since-state` run now prints `records sealed-checked : 0 (incremental: 13,292 already sealed in an earlier pass)` and exits 0; pre-fix it exited 2.** **(B) THE SAME GUARD SAT AFTER THE `P1-P4 CLEAN` BANNER**, so an empty archive printed CLEAN and *then* CANNOT-VOUCH -- defeating the exact method my own commit message that day named (*"read the tool's own VERDICT LINE, never its exit code"*). Moved above the reporting block; **falsified: an empty archive now exits 2 with ZERO occurrences of "P1-P4 CLEAN".** **(C) MY D14 DEMOTION COULD BORROW ANOTHER LINE'S FROZEN WINNER.** The `frozen/` fallback was applied PER ARM unconditionally, so a leg whose `frozen_<line>/` exists but lacks that arm's winner would satisfy `_all_frozen` from the CORE line's copy and assert *"every crashed arm now holds a FROZEN WINNER"* about a different line. The pre-existing `_roots` logic 40 lines above already resolves the root ONCE; this now mirrors it. Dormant today (all ten `frozen_leg_*` hold all five winners) but **a latent weakening inside a demotion, which is the one shape I had promised was not one.** **(D) `_shrink` WAS INSIDE `integrity_gate`'s SWALLOWING `try`** -- a `_shrink` failure would have been caught by the same `except` that catches an unreadable file, silently dropping a record from I1-I4 while the gate printed "all clean", **in the CONFIRMATORY-path gate.** Moved outside; **falsified: verdict byte-IDENTICAL to the pre-P291 baseline, rc=0.** ⚠ **AND I MADE A FIFTH ERROR WHILE FIXING THE FOURTH: my patch REMOVED the `_shrink` call instead of relocating it, silently undoing P291's 10.2x memory saving. Caught by grepping the file for `_shrink` immediately after the patch reported OK.** Verify the artefact, never the patch script's exit code -- P256, again. |
| **P292** | 2026-08-04 RUN20 pass 13 | ⭐ **FIXED + FALSIFIED. TAMER SAW A FALSE ALARM ON HIS OWN STATUS PAGE, AND HE WAS RIGHT TO ASK.** | He reported *"timeouts issues, and the fatal increased"*. The page said: **`timeouts 6h=13; worst streak 21/240 (8.8% to fatal), pull on core`**. **MEASURED PER DRIVER LOG: core's LAST pull failure was 13:31:17 local, streak 17 -- 137 MINUTES EARLIER -- and it is the tail of INC-1, the 31m50s login-node refusal that ended at 12:32:19Z when the VPN was reconnected. Core has had ZERO failures since. Every other driver's last failure is 28 hours to 5.5 days old, and the last `TimeoutExpired` anywhere is ~3 h old.** The fleet had been clean for over two hours while the row read like a live emergency. ⚠ **THE DEFECT IS NOT THE NUMBER, IT IS THE MISSING AGE -- AND THE MODULE'S OWN COMMENT SAYS SO.** `scan()` records `last_failure` per line and comments *"a stale `last` is only meaningful together with its timestamp, WHICH IS WHY BOTH ARE PRINTED"*. **`oneline()` never printed it**, and `oneline()` is what `publish_status.sh:278` renders into the cell a human reads. A streak that ENDED was byte-indistinguishable from one CLIMBING. Same family as P278 and W1: a statistic with no time attached cannot be acted on. **FALSIFIED, both strings captured on the live archive minutes apart:** before, `timeouts 6h=13; worst streak 21/240 (8.8% to fatal), pull on core`; after, `... pull on core, **2.3 h ago; none live, newest failure 2.3 h ago**`. Two helpers added, nothing removed, no pipe character (it is a markdown cell), ASCII only, `publish_status.sh` interpolates and never parses it (verified at :98 and :278), full report still rc=0 `VERDICT: HEALTHY`. ⇒ **A monitoring defect is measured by the false action it invites, and this one invited a real person to worry about a resolved incident.** |
| **P293** | 2026-08-04 RUN20 pass 13 | ⭐ **FIXED. AN ATTN THAT HAD FIRED EVERY CYCLE FOR 42 HOURS ON A CRASH THAT SELF-HEALED, AND STRUCTURALLY COULD NOT CLEAR.** | Found by sweeping `ALERTS.txt` after the transport question. **`ARM_CRASH_leg_nemotron_3_super.json`, stamped 2026-08-02 21:06:** *"scalar_cvar5: RuntimeError: 240 consecutive pull failures over 3.0 h"* -- the SEARCH lane's death clock, tripped by the Aug-2/3 VPN outage exactly as the maintenance playbook predicts for an outage over 3 h. **THE CRASH IS OVER BY EVERY AVAILABLE MEASURE: `frozen_leg_nemotron_3_super/scalar_cvar5-winner` EXISTS** (the arm finished its whole search and was SELECTED), `test_leg_nemotron_3_super/scalar_cvar5` is being sealed-tested right now on 4 running jobs, and `crash_watchdog --once` reads CLEAN. ⚠ **WHY IT COULD NEVER CLEAR, WHICH IS THE ACTUAL DEFECT:** the marker's own note and the alert's text both promise it "clears automatically on a clean pass", and **`campaign.py:1898` performs that `unlink()` INSIDE THE C1 PATH.** A line that crashed in C1, recovered, and advanced into C2/C4 **never re-enters C1**, so the clearing branch is unreachable and the marker is permanent. The alert's "can take 12h+" understates it: for this line it is never. **P259's family, live on the board, and this repo has already paid for it once -- the alarm-fatigue failure that let D15 sit unexamined for ten hours.** **THE FIX IS A STRICTLY STRONGER DISCRIMINATOR, NOT A WEAKENED CHECK:** the existing downgrade asks "has the crashed arm archived a record since the marker?"; it now also asks "does that arm hold a **FROZEN WINNER**?" -- categorically stronger, because a frozen winner means the arm completed its ENTIRE search and was selected by the registered criterion. Only then is the row demoted to `info`, and **it still PRINTS**, naming the marker, its age and the reason it cannot clear. An arm without a frozen winner still raises ATTENTION; an unreadable marker still lands in the RED branch. **The marker itself is PRESERVED as crash evidence for the execution record rather than deleted.** ⚠ `campaign.py` is drift-fenced so the `unlink` cannot be moved; `cycle.py` is under `docs/` and re-invoked each iteration, so this is the right and only place. Applied the P268 way, **including an explicit check that `info` is BOUND before the insertion point** -- the exact unbound-local that ruff and `ast.parse` both missed in P268. ⭐⭐ **FALSIFIED BY THE LIVE LOOP ON ITS OWN NEXT TWO INVOCATIONS, WHICH IS THE P259 PATTERN: THE BOARD'S VERDICT FLIPPED `ATTN` -> `OK`.** Over the preceding 30 cycles the verdict read **27 ATTN, 1 RED, 2 OK -- and both OK lines are the two that follow this edit** (14:59:10Z and 15:02:17Z). The 14:37:42Z alert block confirms why: the D14 marker was **the only UNACKNOWLEDGED attention row**, everything else in it being the acknowledged truncation / transport / `seed_alignment` set. ⇒ **A single stale marker from a 42-hour-old, fully-recovered crash had been holding the entire board off green.** |
| **W-refresh** | 2026-08-04 RUN20 pass 12 | ⚠ **THREE OF THE FIVE WATCH ROWS WERE STALE, AND A STALE WATCH ROW IS A DEFECT BY THIS LEDGER'S OWN AGING RULE.** | Nothing had re-measured them, so each was carrying a number a session could have acted on. All five re-measured and dated. **W5 was wrong by 3 and 2:** it said *"`tpe` owes 5 of 30, `bayes_opt` 4 of 30"*; measured, **each holds 28 records and owes 2**, with the chain floor at 0.37 d. **W1's quoted trend was wrong in DIRECTION:** the CUSUM reads **0.28**, LOWER than the "0.99 -> 2.56" recorded -- because `sentinel_events.jsonl` shows **15 sentinel restarts** and the statistic is PROCESS-LOCAL, so it resets and re-crosses `h=0.15` within ~2 samples. **It is unbounded WITHIN a process and NON-MONOTONE ACROSS restarts**, which refines D36 rather than contradicting it: the alarm is still permanent, only its magnitude is meaningless, and quoting a rising trend was a mistake. **W2 is superseded** by E-spend's exact $8.7603 realized / $36.7418 estimated split. **W3 is no longer trending** at 39.0 GB free against a floor of 20, stable all session. ⭐ **W4 RESOLVED, AND THE PREDICTION HELD:** both repair jobs are now **RUNNING** -- 83464 started 12:47:20 and 85065 at 13:08:40, inside the 9-18 h drain estimated when the row opened. |
| **LADDER-1** | 2026-08-04 RUN20 pass 12 | **MEASURED, AND IT IS THE LARGEST PER-LINE IMPROVEMENT AVAILABLE ON THE BOARD** | Job **83464 resolves to `leg6_leg_gpt_5_6_luna_sweep_t3_r1`** -- the `_r1` suffix is the driver's own REPAIR ROUND, and tier 3 is the block covering the missing seeds. **`gpt-5.6-luna` banks rung 189 against a frontier of 567**, capped by holes at seeds **192/193 across five arms** (`distributional` [193], `placebo` [192,193], `placebo_shuffled` [192], `scalar` [192,193], `scalar_cvar5` [192,193]). **If the repair lands, that line's banked rung moves from 189 toward 568 in one step.** ⚠ **AND IT MUST NOT BE OVERSOLD, because RUN 19 recorded the opposite-facing fact and both are true: it does NOT move the COMMON rung**, which is 0 and capped by core, deepseek, glm, nemotron and kimi. The two statements are consistent -- a per-line gain and a campaign-wide gain are different quantities, and conflating them is exactly what the common-rung discipline exists to prevent. **Watch it, do not act on it: the driver submitted the repair itself and no lever of ours is involved.** |
| **P290 + P291 + P289** | 2026-08-04 RUN20 pass 11 | ⭐⭐⭐ **THE OOM TRAJECTORY IS CLOSED. 20.7 GB OF PEAK MEMORY REDUCED TO 2.05 GB, EVERY STEP MEASURED AND EVERY VERDICT PROVEN UNCHANGED.** | **THE MEASUREMENT FIRST, because P270's projection was built on the wrong population.** Sampling every python process WITH ITS COMMAND LINE across a full seven-layer run gave: `results_audit` **8,032 MB** · `integrity_gate` **6,899 MB** · `science_watch` 683 MB (P280 holding) · **and every one of the seven RECORD LAYERS under 55 MB.** Free RAM floor during the run: **0.46 GB** on a 15.64 GB box hosting ~30 driver and supervisor processes. ⚠ **P270 measured `results_audit` at 1,475 MB -- it is 5.4x that now -- and `integrity_gate` WAS NOT IN P270'S LIST AT ALL, so its `ThreadPoolExecutor(max_workers=1)` mitigation never covered the second-largest consumer.** Together the two are **14.9 GB against a 15.64 GB box.** ★ **AND THE SAME MEASUREMENT DELIVERS THE REASSURING HALF: the certification stack is CLEAN.** The seven record layers stream properly; the hazard was entirely in the cycle's results layer. **P290 `results_audit.py`: 8,032 -> 689 MB (11.7x).** Safe because it was CHECKED -- the only generic read of a metric value is a non-finite scan whose predicate is `isinstance(v, float)`, STRICTLY float, so a list was never examined and an int is not either; six behavioural cases run against the candidate BEFORE it moved. **P291 `integrity_gate.py`: 6,899 -> 678 MB (10.2x).** Higher bar because **this gate guards the CONFIRMATORY path** (search -> frozen -> test): every field it reads was ENUMERATED (`max_tokens`, `model_snapshot`, `temperature`, `train_safe_call_count`, `train_safe_default_count`, `arm`, `reward_source_hash`, `candidate_id`, `reward_source`, `val_fitness` -- all scalars or strings, zero arrays), the shrink was applied ONCE at the parse site because three lists share the same object, and **the pre-fix verdict was captured BEFORE the patch and byte-diffed against the post-fix one: IDENTICAL** (`I1 self-hash | I2 search->frozen | I3 frozen->test | I4 selection | I5 model pin | I6 decoding pin -- all clean`). **P289 `.claude/lanes/openitems.py`: the 7,138 MB loader probe now runs hourly instead of per-preflight.** ⚠ **NOT a weakened check, and the distinction is the point:** the check still runs and still fails on its property; only the CADENCE changes, the cache key includes the SIZE AND MTIME of `scripts/analyze_campaign.py` -- the very file whose behaviour it verifies -- a TTL bounds staleness anyway, the cheap `.pull_tmp` half stays LIVE every call, and every cache failure falls through to running the probe, so the failure direction is "do the expensive correct thing", never "assume clean". **Falsified: cold run 196 s, warm run 1 s, outputs byte-IDENTICAL, and the LOADER-POOLING row still reports OPEN.** ⇒ **Free RAM measured at 7.97 GB after the three fixes, against a 0.46 GB floor before them. The P270 escalation -- "the box is exhausted at ~37,500 records; the ladder tops out at 42,128" -- is closed, and it was closed by measuring the right population rather than by trusting the earlier one.** ⭐ **PROVEN END TO END ON THE COMMAND THAT USED TO BE THE HAZARD: a full `session_preflight --full` was re-run with a per-process census attached, and the heaviest process reached 691 MB while the FREE-RAM FLOOR was 6.3 GB -- against 0.14 GB before the fixes, a 45x improvement in headroom -- with `VERDICT: OK, all 17 rows` and rc=0.** The three tools that were 20.7 GB now sit at 691 / 668 / 660 MB, and nothing else on the box exceeds 235 MB. |
| **P288** (new instrument) | 2026-08-04 RUN20 pass 10 | ⭐ **BUILT + SELFTEST 4/4 + RUN LIVE CLEAN. THE LAST UNADDRESSED ITEM ON RUN 20's OWN s.11 LIST.** | RUN 20's brief asks for exactly this: *"systematically diff every instrument that reports the same quantity."* The campaign has now found that defect **three times in three different tools**, the worst being P282, where a GATED layer printed a banked rung of **12** while the ungated measurement printed **0** -- a disagreement about THE REPORTED SCIENTIFIC RESULT, with the gated one reading high. **New `docs/analysis/instrument_agreement.py`.** ★ **THE DESIGN RULE THAT MAKES IT MORE THAN A DIFF, AND IT IS THE P259 TEST APPLIED TO A COMPARISON: a tool that prints "these differ, as expected" every run carries ZERO BITS.** So every row carries an EXPECTED RELATIONSHIP -- equality, or an identity that accounts for the scope difference exactly -- and the check is whether that relationship HOLDS. A1 the record count (`campaign_guards`' depth-4 glob against a per-tier census, as an IDENTITY rather than a comparison) · A2 the arm roster (`line_balance`'s ANY-subdirectory rule against the `-winner` rule S15 and `arm_jobs` both use) · A3 per-arm depth (record.json at ANY depth against `-s<N>` seed directories) · A4 the banked rung (S10 against S15). **Selftest 4/4, and each case CATCHES a different real divergence: a phantom roster entry, a record at the wrong depth, and a missing root that must not read clean.** **LIVE: every expected relationship HOLDS** -- `guards=13,009 = test 11,470 + search 1,539 + other 0` exactly, rosters identical on all 12 lines, per-arm depths identical on every (line, arm). ⭐ **AND THE `--deep` RUN CLOSES THE LOOP ON P282/P287: `A4 banked rung: S10=0 S15=0`.** That is the disagreement P282 found reading **12 against 0**, now proven closed by a THIRD instrument that executes both layers and parses each one's own printed verdict rather than re-implementing either. **A fix verified by the tool that would have caught it is the strongest form available here.** ⇒ **The four counting rules this campaign uses are now proven to agree, and the next time one of them drifts the tool will say so instead of a session finding it by accident three weeks later.** |
| **P287 / A6 CLOSED** | 2026-08-04 RUN20 pass 9 | ⭐ **A6 WAS NEVER A PRE-REGISTRATION QUESTION. IT WAS AN INSTRUMENT BUG, AND READING THE FROZEN TEXT SETTLED IT.** | **I PUT THIS TO TAMER AS A DECISION HE HAD TO RATIFY. THAT WAS MY ERROR: I SHOULD HAVE READ R101 FIRST.** The amendment row says it in words -- *"the confirmatory Opus 4.8 + **all 10 legs** climb ONE COMMON assurance-tier ladder ... the FINAL result is whatever **COMMON rung all 11** have COMPLETED by the stop"*. **The registered population is exactly eleven: the confirmatory core plus the ten legs.** `test_h3_singleshot` is the H3 **single-shot CONTROL** condition (R30, report-only, outside the frozen m=6), not one of the eleven; the 11 `baseline_*` arms are the **human-written reward canon for H1** (node N6), not models at all. **Both are excluded BY THE FROZEN TEXT, so there is nothing to decide and nothing to amend** -- the correct action is to make the INSTRUMENT match the FREEZE. S15's campaign-wide minimum ran over every `test*` line and folded h3 in; `record_science_audit`'s S10 already excluded it, so two instruments disagreed about the definition of the headline number. **FIXED: S15 now prints `population = 11 model line(s); EXCLUDED by R101: test_h3_singleshot` and quotes the registered clause beside it.** Selftest 25/25, ruff clean. **DIRECTION AND EXPOSURE BOTH STATED: including h3 could only push the minimum DOWN, and h3 banks 568 -- the ceiling -- so it has never BEEN the minimum and no reported value changes.** ⚠ **AND THAT IS EXACTLY WHY IT WAS FIXED NOW: a definitional correction made while nothing is at stake cannot be a forking path.** ⇒ **CONSEQUENCE FOR TAMER: there is no longer an open definitional decision on this axis that seeing an outcome could contaminate.** Serves Criterion 2 (*"faultless execution"*) and Priority 5 -- one quantity, one definition, and the two instruments that compute it now agree. |
| **P286** | 2026-08-04 RUN20 pass 8 | ⭐ **FIXED ACROSS THE WHOLE CLASS + FALSIFIED ON ALL SIX** | **ZERO IS NOT CLEAN, AND SIX OF THE SEVEN GATED LAYERS DID NOT KNOW IT.** `Path.rglob` over a missing or empty tree returns an empty iterator and raises nothing, so a layer walking an ABSENT archive printed **exactly the output a perfect archive produces** and exited 0. The archive is a **PULL MIRROR** -- `record_seed_completeness` says so in its own text -- so *"not here yet"* is a REACHABLE state, not a hypothetical: a remount, a path typo or a stalled pull would have produced six CLEAN banners and one honest failure. Only `record_window_identity` got it right; `line_balance` already states the rule in prose (*"a check that examined nothing must not report success"*, the P213 rule) and it had never been carried across. **FALSIFIED BEFORE AND AFTER, ON AN EMPTY DIRECTORY, READING EACH TOOL'S OWN VERDICT LINE:** before, `record_science_audit` printed *"S1-S10 CLEAN"*, `fed_text_identification` *"S11 CLEAN"* and `fed_value_coherence` *"V1-V5 CLEAN"*, all at **rc=0**; after, all six print *"CANNOT VOUCH FOR ANYTHING"* and exit **2**. ⚠ **AND THE TRAP THAT NEARLY FOOLED MY OWN TEST HARNESS IS THE FINDING WORTH KEEPING:** my first falsification passed a POSITIONAL path to tools that take `--root`, so **argparse exited 2 on a USAGE ERROR** -- the same code a vacuity guard uses -- and every tool looked correctly guarded. **Reading the tool's own VERDICT LINE rather than its exit code is what separated them**, which is the standing rule applied to my own test rather than to the campaign's. Applied the P268 way: each candidate written to a temp file, ast-parsed, symbol-diffed (0 dropped), then `os.replace`; ruff clean on all six; the full seven-layer stack re-run against the live archive afterwards to prove no regression. |
| **P285** (new instrument) | 2026-08-04 RUN20 pass 7 | ⭐⭐ **BUILT + SELFTEST 6/6 + RUN LIVE: THE ARCHIVE IS SCIENTIFICALLY PLAUSIBLE, AND IT IS THE FIRST TIME ANYTHING HAS ASKED.** | **TAMER SAID I WAS BEING LAZY AND ACTING AGAINST THE PRIORITIES, AND HE WAS RIGHT.** I answered *"are the results nonsense?"* with an essay about blindness instead of building the check. **The seven record layers verify INTERNAL CONSISTENCY ONLY** -- that a Sharpe replays from its own returns, that hashes match, that commits exist. **All seven read RC=0 over an archive whose every number could be scientifically absurd**, because not one of them asks whether a Sharpe is believable, a CVaR correctly signed, a weight on the simplex, or an arm degenerate. `CLAUDE.md` states the duty and names the precedent: this project's prototype "tail signal" was REFUTED on a wrong-unit error **that had passed every test**. **New `docs/analysis/science_plausibility.py`: B1-B9, streaming (O(arms), not O(archive) -- P280 applied at build time), selftest 6/6 with each case proving a different violation is CAUGHT.** ★ **THE BLINDNESS GUARANTEE IS ENFORCED IN CODE, NOT PROMISED:** every level is POOLED over all arms and lines, every per-arm statement is a boolean or a count, no difference or ordering is ever computed, and `_assert_blind()` re-reads the rendered text and REFUSES TO PRINT if a per-arm level would escape. **It fired on a single-arm fixture** -- correctly, because with one arm a "pooled" figure IS that arm's level -- so the tool now suppresses levels below 2 arms and says why. **LIVE VERDICT over 11,366 sealed-test records: PLAUSIBLE, rc=0.** `test_cvar05` all negative, median -0.0200, range [-0.0344, -0.0102]; `test_sharpe` median 1.0275, range [-1.09, +1.65]; **0 out of band on every field; 0 of 59 units degenerate; exactly ONE series length (1,571) across all 11,366 records; 0 sign disagreements between replay and archive; 0 simplex, series, turnover or gross violations.** ⇒ **THE NUMBERS ARE REAL, CORRECTLY SIGNED, NON-DEGENERATE AND COMPUTED OVER AN IDENTICAL WINDOW -- and no contrast was computed or seen.** |
| **P284** (three of my own, in one run) | 2026-08-04 RUN20 pass 7 | **FIXED -- ALL THREE WERE MY INSTRUMENT, NOT THE ARCHIVE** | The first live run of P285 reported **16,698 implausibility signals**. Every one was mine, and finding that out took three checks against the real configuration rather than against the field names. **(1) 5,011 "weights do not sum to 1"** -- `config/environment.yaml` sets **`include_cash: true`**, so the risky weights legitimately sum to LESS than 1 with cash as the residual; a book 19% in cash is the agent working, not a violation. Rule corrected to `sum <= 1` plus non-negativity. **(2) 11,357 "gross exposure out of [0, 5]"** -- `test_gross` is not an exposure. `src/orchestration/test_leg.py:149` writes it as a per-period series paired with `test_turnover`, and its values live in [-0.08, +0.058]: it is the **gross (pre-cost) RETURN series**, negative on down days by construction. **Reading a field's meaning off its NAME is exactly P271's `arms_full` mistake, and it manufactured 11,357 false findings in a single pass.** **(3) 330 non-finite `val_fitness`** -- NaN on every hand-written H1 baseline's test record BY DESIGN, since a baseline is not selected on a validation criterion. **330 = 11 baselines x 30 seeds exactly**, which is the arithmetic identity that proves the reading rather than asserting it. Reclassified as a named DISCLOSURE; a NaN anywhere else is still a finding. ⇒ **THE STANDING LESSON, EARNED FOUR TIMES IN ONE SESSION: A SURPRISING NEGATIVE IS A CLAIM ABOUT MY OWN SCRIPT FIRST.** (Also: the pack-tail hypothesis, refuted; the pooled-T hypothesis, refuted; the self-inflicted-queue hypothesis, refuted.) |
| **P283** | 2026-08-04 RUN20 pass 7 | **FIXED + FALSIFIED** | **R8 -- the endpoint-replay proof, and the only thing standing between a corrupted return series and a CLEAN certification -- PASSED SILENTLY ON EVERY NaN.** `abs(NaN - x) > 1e-9` evaluates to **False**, so one non-finite element anywhere in a 1,571-point `test_returns` made `mu`, `sd`, `sh` and `cv` all NaN and **both comparisons quietly succeeded**. Worse, the writer (`src/inference/bootstrap.py::sharpe_ratio`) DROPS non-finite values first, so it would archive a perfectly valid statistic over the finite points while this replay agreed with literally anything. Non-finiteness is now a POSITIVE finding on both sides -- a non-finite input, a non-finite replay, or a non-finite ARCHIVED value each raise their own violation. **FALSIFIED against a verbatim reconstruction of the pre-fix rule across four cases: C3 (one NaN in the series) and C4 (an archived NaN) are silent PASSES before and FLAGS after; the two controls are unchanged.** |
| **CHAIN-3 RESOLUTION** | 2026-08-04 RUN20 pass 6 | ⭐ **PROVEN-BENIGN. THE RISK DID NOT MATERIALISE, AND THE OUTCOME IS ON DISK.** | `c1_bayes_opt_c27` left the queue between 13:10:54Z and 13:12:39Z. **It COMPLETED, it was not killed:** `ledger/c1_bayes_opt_c27.epilogue.jsonl` reads `{"task":1,"host":"node-d00a-133...","rc":0,"secs":44541,...}` -- **rc=0 in 12.37 h**, clearing the 15.0 h wall with 2.6 h to spare. So the single serial step on the binding critical path finished, at 43% beyond `bayes_opt`'s own previous maximum of 8.66 h and inside the 7-of-1,581 tail. **THE CHAIN ADVANCED AND THE ETA IMPROVED, MEASURED:** `bayes_opt` **owes 3 -> 2 of 30** (27 candidate records on disk, `tpe` 28), and the critical-chain floor fell **0.56 d -> 0.37 d still to run**. Core's C1 now clears in ~8.9 h, so core reaches rung 30 in **~18.3 h against the ~23 h stated one pass earlier.** ⚠ **THE PROCESS LESSON IS THE ONE TO KEEP: the check that mattered was `cpu` against `wall`, not elapsed time.** A number that had read "owes 3" for five consecutive passes is the exact shape of a stall, and it was NOT one -- `cpu=98:43:36` on 8 slots gave a ratio of 8.01 and settled it in one command. Elapsed time alone would have supported either conclusion. |
| **P282** | 2026-08-04 RUN20 pass 6 | ⭐ **FIXED + FALSIFIED ON THE LIVE ARCHIVE, AND IT CLOSES A CROSS-INSTRUMENT DISAGREEMENT ABOUT *THE RESULT*** | **A GATED LAYER AND AN UNGATED MEASUREMENT DISAGREED ABOUT THE REPORTED SCIENTIFIC RESULT, AND THE GATED ONE READ HIGH.** `record_science_audit.py`'s S10 built its banked rung from `pair_seeds`, which only ever acquires a key when a record EXISTS -- so a line holding a REGISTERED frozen-winner arm with ZERO sealed-test records contributed its OTHER arms' depth instead of the 0 it actually banks. **Live: S10 printed `COMMON contiguous prefix 12` while `record_seed_completeness` (S15/C6) printed 0.** Third appearance of the P244 pathology: a minimum over a population that silently excludes the members that would make it bad news. The `!!` note below it DISCLOSED the gap in prose, but a session quoting the number rather than reading the note overstates the bankable result -- and the number is the headline. **THE FIX MATCHES S15 EXACTLY:** any line with a registered arm holding no record is scored 0. **FALSIFIED BY THE TOOL ITSELF, ON LIVE DATA, WITH BOTH VALUES PRINTED:** it now emits *"(over STARTED arms only this would read 12; the number below counts a registered arm with NO record as the 0 it actually banks)"* followed by `COMMON contiguous prefix 0` -- **S10 and S15 now agree.** L3 rc=0, ruff clean, AST parsed first. ⚠ **AND THE STALE SENTENCE INSIDE THE FIX WAS CAUGHT AND REPAIRED TOO:** the trailing note still said *"'banked rung' describes the STARTED arms; it is not a full-roster bank"*, which the fix had just made FALSE. It now states what the number is, that it agrees with S15, and the four channels that still make it an UPPER bound. ⚠ **DELIBERATELY NOT CHANGED: the 11 H1 baselines stay excluded from `pair_seeds`.** An auditor argued they are confirmatory under N6/R108 and belong in the minimum. That is a PRE-REGISTRATION question about what the reported result is defined over, not an ops patch, and S15 already checks them on a separate path. Same class as the escalated A6. |
| **CHAIN-3** | 2026-08-04 RUN20 pass 5 | ⚠ **THE ONE THING ON THE CRITICAL PATH THAT IS AT RISK, MEASURED AND NAMED. NOT HUNG, AND NO LEVER EXISTS.** | Tamer asked what has not started and is holding the speed. **It is `c1_bayes_opt_c27`, job 85816, and it is the single serial step on the campaign's binding path.** MEASURED from `qstat -j`: started 01:47:34, **elapsed 12.3 h**, `usage cpu=98:43:36` on 8 granted slots -> **CPU/wall = 8.01, i.e. every thread flat out.** ⇒ **IT IS COMPUTING, NOT HUNG** -- the check RUN 19's CORE-1 established, run again rather than assumed. **BUT `hard resource_list: h_rt=54000` = 15.0 h, so it has ~2.7 h before the scheduler kills it `rc=126`.** ⚠ **HOW UNUSUAL IS 12.3 h? MEASURED OVER 1,581 SUCCESSFUL SEARCH TASKS:** median **4.24 h**, p90 6.65, p99 10.79, **max ever 14.32**; only **7 of 1,581 (0.44%)** ever exceeded 12 h. And `bayes_opt`'s OWN history is n=28, median **4.08 h**, p90 6.99, **max 8.66 h** -- **c27 is already 42% beyond the worst candidate bayes_opt has ever completed.** Of the tasks that reach this depth, 5 finished and ~16 were wall-killed, so completion is precedented but is the minority outcome. **THE COST IF IT WALLS:** no record for c27, the driver's own repair round resubmits (the `_r1` mechanism, seen live on `c1_tpe_c26`), and the common-rung-30 ETA moves from ~23 h toward ~35 h. **NO LEVER EXISTS AND EVERY CANDIDATE WAS CHECKED:** `qalter -l` is REFUSED SITE-WIDE so the wall cannot be extended; raising priority is operator-only; lowering ours is a standing prohibition and one-way; and killing it forfeits 12.3 h of completed compute for nothing. ⚠ **AND THE STRUCTURAL OBSERVATION WORTH RECORDING BUT NOT ACTING ON:** core's `distributional`/`scalar` winners are ALREADY FROZEN, so its C2 `h2_pair` has no SCIENTIFIC dependency on `bayes_opt` -- which is an H4 comparator. The dependency is the C1 -> C2 ORDERING in `campaign.py`. **That file is drift-fenced, and changing it would mean editing fenced code and relaunching the core driver mid-chain to save ~13 h against a 22.5-day budget with rung 403 projected 08-09. The trade is bad and it is not taken.** |
| **P281** (completes P275) | 2026-08-04 RUN20 pass 5 | **ROOT-CAUSED IN FULL, AND IT IS NOT WHERE I FIRST SAID** | The second memory hog is now traced end to end by catching it in the act with a CIM census carrying full command lines AND parent command lines. The chain is: **`session_preflight.py:578` -> `.claude/lanes/openitems.py --open` -> `openitems.py:377` builds an inline `python -c` -> `from analyze_campaign import load_campaign_records; recs = load_campaign_records(root)` -> the WHOLE archive is materialised in one list.** **MEASURED PEAK: 7,138 MB**, larger than `science_watch`'s pre-P280 5,776 MB and the largest single process observed in this campaign. **So P275's instinct that "a preflight run costs 4.7 GB" was directionally right and its ATTRIBUTION was wrong** -- preflight does trigger the spike, but through a lane-infrastructure grandchild, not in its own address space. The verifier itself is legitimate: it runs the real loader to assert the LOADER-POOLING property, which the board wants asserted rather than grepped. ⚠ **ESCALATED RATHER THAN PATCHED, DELIBERATELY:** `.claude/lanes/**` is shared multi-session infrastructure that RUN 20's own brief says is ABANDONED and must not be registered with, `scripts/analyze_campaign.py` (where the memory actually lives) is DRIFT-FENCED, and the spike is transient and only fires on `--full`. **THE OPERATIONAL RULE UNTIL IT IS FIXED, and it is cheap: do not run `session_preflight --full` while free RAM is under ~8 GB.** The fix when a window opens is a TTL cache on that one verifier row so the loader runs hourly rather than per preflight. |
| **P279** | 2026-08-04 RUN20 pass 2 | ⭐ **FIXED + FALSIFIED AGAINST A LIVE OUTAGE, WHICH IS THE STRONGEST FALSIFICATION AVAILABLE** | ⛔ **THE LOGIN-NODE GUARD WENT SILENT AT EXACTLY THE MOMENT THE LOGIN NODE FAILED, AND EXITED 0.** Found by running the session-prompt board's FIRST command and noticing it printed **nothing** where it had printed `OK ... comfortable` forty minutes earlier. `loginnode_guard.py` returned **0 -- the same code as "comfortable" -- on BOTH failure branches**, and the only `print` in `sample()` sits in the success path, so a broken probe produced **EMPTY STDOUT AND rc=0**. Its own log knew: `PROBE-UNPARSED ''`, seven consecutive entries from **2026-08-04T12:00:29Z**. The old code justified this in writing as *"never let the guard itself fail loudly"* -- but `MAINTENANCE_2026-08-12.md:148` names this tool as **the ONE instrument whose verdict should change behaviour on an at-risk day**, so silence exactly when the login node is in trouble is worse than no guard at all. **THE CAUSE WAS REAL AND CONCURRENT, NOT A FIXTURE:** `ssh myriad13` returned `kex_exchange_identification: read: Connection reset by peer` / `Connection reset by 193.60.252.109 port 22`, the gated alias returned `Connection closed by UNKNOWN port 65535`, both aliases resolve to the same `login13.myriad.rc.ucl.ac.uk`, and the twelve driver logs were accumulating `pull failed` counts through 2, 3, 4 and on to **17 consecutive** while the guard said nothing. **FALSIFIED ON THAT EVENT: pre-fix `--once` produced 0 bytes and rc=0; the shipped version produced 919 bytes and rc=3 on the same failure, minutes apart.** New `UNKNOWN_RC = 3` is distinct from 0/1/2 and breaks nothing -- verified by grep across `docs/`, `scripts/`, `src/` and `.claude/` that **no consumer reads this exit code programmatically**; every reference is documentation or a human invocation. The UNKN block names the three causes this has actually had, and tells the reader NOT to retry in a loop or relaunch by hand, because a reconnect stampede is what earned the 2026-08-03 00:33:47Z penalty. Selftest still ALL PASS, ruff clean, AST parsed before the run, ASCII only. ⚠ The running 120 s daemon holds the old module in memory and is INERT until restarted; `--once` and every future session get the fix immediately. |
| **INC-1 RESOLUTION** | 2026-08-04 RUN20 pass 3 | ⭐ **ROOT CAUSE CONFIRMED BY THE REMEDY WORKING. 31 m 50 s, ZERO MEASURABLE COST.** | **THE DIAGNOSIS WAS TRACED TO THE PACKET, NOT GUESSED.** `ssh -vv` showed `Connection established` and `Local version string SSH-2.0-OpenSSH_10.2` and then `kex_exchange_identification: read: Connection reset by peer` -- **TCP completed, we sent our banner, and the server never sent its.** `Test-NetConnection` confirmed **port 22 OPEN on all three login IPs** (193.60.252.107/.108/.109) and `www.rc.ucl.ac.uk:443` reachable, so it was neither a lost route nor a network outage; the last good guard reading (`cores=0.00/6.0 mem=0.00GB qacct=0 comfortable`, 11:58:29Z) rules out a UCL usage penalty, which caps CPU and memory rather than blocking SSH. Reset timing 76 ms then ~1,072 ms twice, and **every login node refusing identically**, points at the SOURCE ADDRESS being refused site-wide. **Our VPN address was 10.151.114.155 -- and `acknowledged_alarms.txt:340` records the identical event from the identical /24: *"the 10.151.114.0/24 pool lost its route to 193.60.252.0/24; a reconnect onto 10.151.109.237 restored all three login nodes."*** Escalated to Tamer with one action. **He reconnected; the address became 10.151.110.107, outside the failing pool; the very next `ssh` returned `login13.myriad.ucl.ac.uk` and the guard read `OK ... comfortable` at 12:32:19Z.** ⚠ **NOTE THE MECHANISM IS STILL NOT FULLY EXPLAINED: a lost ROUTE cannot produce a completed TCP handshake, so the 2026-08-03 note's stated mechanism is inconsistent with what was measured today, even though its stated REMEDY is exactly what worked.** The honest statement is that the 10.151.114.0/24 pool is refused by the Myriad login nodes and a reconnect off it restores service; why is not established from this side. **COST, MEASURED AFTER RECOVERY: none detectable.** Records resumed and the backlog flushed (test tier 11,096 -> **11,196**, +100 in 28 min), the 12 h rate came back **ABOVE** its pre-outage value (164.7 -> 161.8 -> **165.1 rec/h**), the fleet never shrank (**2,018 -> 2,033 -> 2,015 slots**, zero `Eqw`/`hqw`), no driver died (worst consecutive peaked at 21 against a SEARCH death clock of 240), and `session_preflight --full` reads **VERDICT OK, all 17**. The jobs ran on the compute nodes throughout; only the pull was blocked, so the outage cost visibility and a queue of unpulled records, not work. |
| **INC-1** | 2026-08-04 RUN20 pass 2 | **LIVE INCIDENT, RIDDEN BY THE BOOK, NO ACTION TAKEN AND NONE OWED** | **login13 began refusing SSH at 12:00:29Z.** Signature `kex_exchange_identification: Connection reset by peer` -- sshd refusing before authentication, i.e. a transport/node event, **not** a UCL usage penalty (a penalty caps CPU and memory and arrives with an email; our last good reading at 11:58:29Z was `cores=0.00/6.0 mem=0.00GB qacct=0 comfortable`). Identical signature to the two `PROBE-UNPARSED` entries during the 2026-08-03 VPN outage, which recovered after 7 h 24 m. **MEASURED CONSEQUENCES, all expected:** `records=12633 (+0)` flattened, the 1 h rate fell 143 -> 118 rec/h, and worst-consecutive pull failures climbed 2 -> 17 in twelve minutes. **THE JOBS THEMSELVES ARE UNAFFECTED** -- they run on compute nodes; only the PULL of finished records is blocked, so nothing is lost, merely delayed. **Death clocks: TEST 240 x 180 s = 12.0 h; SEARCH 240 x 45 s = 3.0 h**, and ⚠ **core's C1 chain (`c1_tpe_c27`, `c1_bayes_opt_c27`) is in the SEARCH lane, so the confirmatory driver is on the 3.0 h clock** -- the fragile one, and the one that died in the Aug-3 outage. That is E1/E2 and it is expected: the supervisor relaunches on a 600 s backoff and no data is lost. **POSITION: RIDE IT.** Per `MAINTENANCE_2026-08-12.md` §5, check the guard and nothing else; do NOT relaunch by hand; do NOT retry in a loop. ⚠ **AND THE HONEST SELF-CHECK: this session made roughly ten gated `ssh` calls in the preceding thirty minutes** (hostname, qstat, four `qstat -xml`). They are unlikely to be decisive against twelve continuously-polling drivers and a 2-minute guard probe, but the possibility is recorded rather than dismissed, and ssh use was stopped on discovery. |
| **P276** (A-d14, THE ROW RUN 19 CALLED HIGHEST-VALUE) | 2026-08-04 RUN20 pass 1 | **FIXED + FALSIFIED + RUN LIVE** | ⭐ **THE PER-ARM DETECTOR NOW EXISTS: `docs/ops/arm_jobs.py`.** RUN 19 handed this over believing it could be built from what `line_balance` already collects. **It could not, and the reason is the finding: `qstat` TRUNCATES the job name to TEN CHARACTERS.** Measured live: `76849 2.00578 leg8_leg_s ucestes r ...`. The arm token is destroyed by the SCHEDULER'S OUTPUT FORMAT, not by `line_balance`'s parse at `:153`, so no care in that parser could ever have recovered it. `qstat -u ucestes -xml` returns the untruncated `JB_name` for the same scheduler query and the same login-node cost. The covering rule is READ FROM THE LAUNCHER, not assumed: a per-arm job name, `h2_pair` covering `distributional`+`scalar` (`campaign.py:1908`), and `_sweep_t<N>` covering every arm in the sweep unit list (`campaign.py:2012`). **⚠ MY FIRST TWO VERSIONS WERE BOTH WRONG AND I CAUGHT BOTH BY READING THE OUTPUT BACK.** (i) I derived the job prefix from the ARCHIVE name (`test_leg_glm_5_2`) when the job carries the BATCH TAG (`leg2_...`), so nothing matched on ten leg lines and it flagged **23 arms** -- including arms whose covering jobs I had read off the queue by hand five minutes earlier. (ii) A naive `"_scalar_" in name` reports `leg7_..._scalar_cvar5_test_p01` as covering `scalar`; the shipped rule prefers the LONGEST matching roster arm. **FALSIFIED, not merely tested:** cases A1 and A4 are TRUE under the naive rule and FALSE under the shipped one (pre-fix rule correct on 3/5, shipped on 5/5), and on the live shape the naive rule reports nemotron's `scalar` as covered by 4 jobs while it is covered by none. **Selftest 17/17. Fails toward CANNOT-DECIDE everywhere:** a failed queue read exits 2 and reports nothing clean (D1), and a line with an unreadable `frozen*/` roster is named LOUDLY rather than dropped the way `line_balance.py:134-135` drops it silently (D2). **RUN LIVE, and it produced a specific checkable list: 6 arms below their line's frontier with no covering job** -- `test`, `deepseek` and `nemotron`, all of them `distributional`/`scalar`. **Every one DISCRIMINATED to a cause from the driver log and PROVEN-BENIGN: all three lines are waiting on an upstream stage** (core's C2 h2_pair fires only after its serial C1 chain, `c1_tpe_c27` submitted 09:39:18; deepseek's newest submission is `placebo_shuffled_test`; nemotron's is `scalar_cvar5_test`, its fifth arm having only just frozen). The detector works, it named the right arms, and none of them is dead. |
| **P277** | 2026-08-04 RUN20 pass 1 | **FIXED + FALSIFIED** | **P4 CERTIFIED "every wall_clock is plausible" OVER A TIER IT NEVER EXAMINED.** `record_provenance_seal.py:234` guards with `if isinstance(wc, (int, float)) and wc > 0:` -- and `wall_clock` is **0.0 on ALL 11,082 sealed-test records and all 58 frozen markers**, measured EXHAUSTIVELY rather than sampled (`wall_clock == 0: 11082, absent: 0, anything else: 0`). The `> 0` guard excludes the only implausible value that actually occurs, so the band ran on the 1,539 search records alone and the banner spoke for the whole archive. The zero is now COUNTED and NAMED, the banner no longer claims the sealed tier, and the ledger substitute is printed beside it. **FALSIFIED ON THE LIVE ARCHIVE, not a fixture:** the shipped layer prints `P4 WALL-CLOCK POPULATION: checked 1,539 | ZERO 11,154 | absent 0` and the banner now reads *"every wall_clock the band could be applied to (1,539 of 12,693) is plausible"* -- **the pre-fix code printed NO population line at all and asserted the band over all 12,693.** The per-tier breakdown is printed too (`gemini 2,840 · gpt 2,832 · qwen3.5 2,232 · sonnet 1,528 · h3 568 · core 450 · haiku 150 · qwen3.6 150`). Layer rc=0, ruff clean, AST parsed before the run, ASCII-only. See E-wc for the escalation: the writer is fenced, but the compute is recoverable from `ledger/*.epilogue.jsonl`. |
| **P275** | 2026-08-04 RUN20 pass 1, **CORRECTED pass 3, DISCHARGED pass 11** | ⚠ **MY OWN ATTRIBUTION ERROR, CORRECTED BY MEASURING WHAT I HAD INFERRED -- AND THE UNDERLYING HAZARD IS NOW CLOSED.** ✅ **DISCHARGED: the real consumers were found (P281 -> P289, P290, P291) and reduced from 20.7 GB of combined peak to 2.05 GB; free RAM measured at 7.97 GB. The operational rule "do not run `preflight --full` under ~8 GB free" is RETIRED.** | **WHAT I WROTE IN PASS 1 WAS WRONG, AND IT REACHED THE LEDGER, THE CHANGELOG AND A MESSAGE TO TAMER AS A MEASURED FACT.** I claimed *"`session_preflight.py --full` is itself a ~4.7 GB single process"*. **It is not.** The real observation was sound -- a python process held **4,676 MB** while free RAM fell to **0.14 GB** -- but I obtained it by running `Get-Process python`, sorting by working set, and taking the top row, then identifying it as my preflight **because its StartTime matched the moment I launched preflight.** That is identity inferred from a coincidence of timing, and preflight spawns children that are also named `python.exe`. **I asserted an identity I had not measured** -- the exact §7① / P244 failure class, committed by me, one pass after writing the lesson down. **THE CORRECTED MEASUREMENT** (pass 3, a CIM census carrying each process's full COMMAND LINE, sampled every 12 s across a whole preflight run): the two large processes are **`docs/ops/science_watch.py` at 5,776 MB** and **an inline `python -c` archive-load probe at 4,801 MB**. `session_preflight.py` itself never appears in the top rows. **THE UNDERLYING RISK IS REAL AND WORSE THAN P270 RECORDED, so the row survives its own correction** -- see **P280**, which fixes the larger of the two. **THE LESSON: a process census must key on the COMMAND LINE, never on a PID's start time.** |
| **P280** | 2026-08-04 RUN20 pass 3 | ⭐ **FIXED + MEASURED 8.7x + BEHAVIOURALLY PROVEN + APPLIED THE P268 WAY** | **`science_watch.py` HELD THE WHOLE ARCHIVE IN MEMORY AND MEASURED 5,776 MB -- 37% OF THE BOX, AND 3.6x WHAT P270 RECORDED FOR THE SAME TOOL.** P270 measured it at 1,603 MB at 12,514 records and escalated the trend; at 12,633 records it reads **5,776 MB**, so **the true slope is far steeper than P270's projection and its `ThreadPoolExecutor(max_workers=1)` mitigation does not reach it at all** -- serialising two tools does not shrink either one. Cause: `_records()` appended the FULL parsed record, and the mean sealed test record is **~477 KB of JSON** (`test_returns`, `per_period_pnl`, `test_gross`, `test_turnover`, four `test_exposure` channels, `test_alloc.weights`, `train_curve`, several duplicated at top level AND inside `metrics`). **THE FIX IS SAFE BECAUSE THE BIG ARRAYS ARE NEVER READ, AND THAT WAS CHECKED RATHER THAN ASSUMED:** `test_returns` and `train_curve` occur on **exactly one line** in the file, 174, and only as a TRUTHINESS test -- no element is ever indexed, summed or measured. So every list longer than 64 is replaced at load time by **its LENGTH**: an empty list becomes `0` (falsy) and a non-empty list a positive int (truthy), which preserves line 174 bit-for-bit, carries strictly MORE information than a bool, and makes any future indexing FAIL LOUDLY instead of reading a wrong value silently. The rule is **structural, not a field whitelist**, so a schema that grows a new array is covered without anyone remembering. **MEASURED: 5,776 MB -> 667 MB, an 8.7x reduction, on the live archive**, with the tool exiting 0 and producing its complete report (12,791 records, the reconciliation line, every section). **APPLIED THE P268 WAY:** candidate written to a temp file, `ast.parse`d, symbol-diffed (0 removed, 1 added), **eight behavioural cases run against the candidate BEFORE it moved**, then `os.replace`. |
| **P278** | 2026-08-04 RUN20 pass 1 | **FIXED (a re-triage trigger that could never NOT be breached)** | The `guard:transport` acknowledgement's own re-triage trigger read *"timeout_events rising above 31"* -- but `timeout_events` is a **MONOTONE LIFETIME COUNT** over append-only driver logs, so it can only rise and the trigger is breached forever the moment it is crossed. Live: **179**. An auditor correctly reported the breach as actionable; **worked to a cause instead, and the cause is the trigger, not the transport.** Measured by hour: every event today is `1 consecutive, 0-1 min down` and self-recovering, 11 in the current hour against **57 in a single hour on 08-03** and a quiet overnight; the `240 consecutive` in the guard is the Aug-3 VPN outage preserved by a lifetime `max`. Trigger restated on a WINDOW rather than a total, so it can clear. **Sixth appearance of the counter-that-cannot-go-down family** (P259 `RED`, P262 `guards=2`, W1's CUSUM, P266's streak, F5's latch). |
| P244 | 2026-08-04 RUN19 | **FIXED** | S15 took each line's rung as a minimum over STARTED arms, so core/glm/kimi/nemotron printed 30 while banking 0. New check C6 reads the roster from `frozen*/`. Selftest 9→16; the four new cases were run against a verbatim reconstruction of the pre-fix `scan()` and each reads TRUE after / **FALSE before**. Case M is a regression guard reading 30 on both sides. |
| P245 | 2026-08-04 RUN19 | **FIXED** | `stage_eta` priced the serial chain as elapsed wall-clock and printed "0.00 d still to run" while `bayes_opt` held 26/30 and `tpe` 25/30. Now measured from candidate RECORDS against `lanes.SERIAL_CHAIN_BUDGET`; unreadable tree returns UNKNOWN, never 0. Selftest 38→42, ruff clean, page rc=0 with 0 non-ASCII, live on the page. |
| A-1 | 2026-08-04 RUN19 | **PROVEN-BENIGN** | Apparent duplicate monitor/driver processes. Resolved by ANCESTRY: each `.venv` launcher is the PARENT of its base-interpreter child (`ParentProcessId` chains verified). A pattern census counts CHAINS, not instances. |
| A-2 | 2026-08-04 RUN19 | **PROVEN-BENIGN** | Repair jobs 83464/85065 feared stuck. `qalter -w p` → *"found possible assignment with 8 slots"*; real PE `smp-[D]*`, `reserve: y`. Ranked last because SGE priority is monotone in submit time (verified across the whole pending set). Measured drain 9-18 h. |
| A-3 | 2026-08-04 RUN19 | **PROVEN-BENIGN** | RUN 18 §10 alleged the `-1h` predicate `max(0, min(k, rung-(len-k)))` was untested and possibly wrong. It is CORRECT in all three regimes (`L<=R`, crossing, `L-k>=R`), and deleting the column IS caught by the J3 parser. A disclosed defect that was not one. |
| A-4 | 2026-08-04 RUN19 | **PROVEN-BENIGN** | Auditor reported as MAJOR that the ETA table is printing GATED for low rungs while dating higher ones. Refuted by running it: every row is dated, none GATED. The structural half survives as F1. |
| P246 | 2026-08-04 RUN19 | **FIXED** | Mine: a heredoc inside a `bash -c` string, seventh occurrence. Blast radius NIL. Both documents were then written with the Write tool and appended by a script doing no shell quoting. |
| **P274** | 2026-08-04 pass 12 | **FIXED** | Mine, and the worst placement possible: I put backticked filenames inside a python -c string invoked from bash while editing **the RUN 20 handover brief**. Bash performed command substitution, EXECUTED them (three command-not-found lines on stderr) and wrote EMPTY STRINGS into the text -- so the brief shipped reading *and cannot be built while  is drift-fenced*, with three filenames missing from its most important paragraph. **EIGHTH occurrence of this family, and I did it inside the document that tells the next session not to do it.** Caught by reading the written artefact back rather than trusting the exit code, which is the P256 lesson applied. Repaired from a FILE, and the brief now carries the incident inline so the successor sees the rule proven rather than asserted. |
| **P272** (A-attr) | 2026-08-04 pass 12 | **FIXED + FALSIFIED ON LIVE DATA** | `attrition()` keyed only by ARM directory name across `search*/*/failures.jsonl`, **pooling all 11 lines**, so the "max-min across the five arms" it printed was a CROSS-LINE spread while the H2 contrast it exists to inform is **WITHIN-LINE**. A pooled figure can HIDE a badly handicapped arm on one line. It also folded the CORE line in, which `coverage()` excludes -- inconsistent scope inside one file. New `attrition_by_line()` keys by `(line, arm)`; the pooled signature is kept for existing callers and the within-line figure is printed FIRST. **Falsified live: WITHIN-LINE worst spread = 9 on `search_leg_glm_5_2` against a POOLED 14** -- a number no single line actually exhibits. |
| **P273** (A-d14) | 2026-08-04 pass 12 | **FIXED (the false claim) + ESCALATED (the detector)** | The alert said *"A LINE IS MISSING AN ARM (defect D14) -- the six repo guards cannot see this"*, which claims coverage `arm_coverage` does not have. It answers *"did this arm EVER ship a batch"*, which caught the ORIGINAL D14 (leg7, 2026-07-29, an arm dying before its first submission). **The MODERN path is invisible to it:** `campaign.py:1795` returns `{"ok": False}` WITHOUT setting `winners[arm]`, and `:1980`'s `sweep_units = [... if a in winners]` then **SILENTLY DROPS that arm from the entire C4 sweep** -- while `arm_coverage` prints `5/5`, because the arm shipped a search batch days ago. It cannot see C4 at all: 65% of the batch registry is unparseable by its arm regex. **⛔ THE DETECTOR CANNOT BE BUILT HERE -- `campaign.py` is DRIFT-FENCED while live.** What IS fixed is the false claim, because *an instrument that says it covers a failure mode is what stops the next session from looking for it*. The alert is now scoped "D14 at SEARCH time", and the code carries the exact design for the missing detector: **a REGISTERED arm with ZERO sealed-test records on a line whose OTHER arms are producing, with no job in flight** -- S15's C6 is the first half, and a PER-ARM refinement of `line_balance`'s STUCK/WAITING split is the second. Handed to RUN 20 as its highest-value row. |
| **P271** (C1-loop) | 2026-08-04 pass 11 | **FIXED + CONFIRMED THREE WAYS** | `arms_full=10/10` read **exactly 10/10 on all 5,038 lines ever written**, and an auditor found it describes neither what its name claims nor the current stage. **All three confirmed by executing the production regex:** (1) `^(line)_.*?_(arm)` requires a MIDDLE segment, but core batches are `c1_distributional_g5_p01` -- **ALL 380 `c1_*` entries match ZERO times**, so the CONFIRMATORY line never enters the map and `arm_coverage.py`'s `if line == "c1": continue` is **DEAD CODE that has never executed**; (2) **2,817 of 4,331 entries (65%) are unparseable**, because C4 sweep batches are `leg9_..._sweep_t2_p01` with all five arms in one batch and no arm token -- **the check measures the SEARCH stage, which has ended**; (3) it is a monotone high-water mark over a registry whose entries are never removed, so it means "did this arm EVER ship one batch" and saturated days ago. ⚠ **THE VALUE WAS CHANGED, NOT THE KEY, AND DELIBERATELY:** the auditor recommended renaming the key, but three consumers parse it by string and `health_watch.sh` empties **SILENTLY** if it vanishes -- renaming is the change most likely to break something quietly, the exact class this session keeps closing. `arms_full=10/10legs-ever` is self-describing at zero coupling risk; verified live that `health_watch`'s `[0-9/]*` still captures `10/10` and `publish_status`'s `5/5 arms submitted` key is untouched. ⚠ **NOT recency-gated, deliberately:** in C4 that would read `0/10` forever and pin the alert permanently RED -- the pathology P259 just removed. |
| **P270** | 2026-08-04 pass 11 | **FIXED (mitigated) + ESCALATED** | ⛔ **THE SCIENCE MONITORS ARE O(ARCHIVE) IN *MEMORY*, AND ON THE CURRENT TRAJECTORY THE BOX OOMs BEFORE THE REGISTERED PRIMARY TARGET.** Surfaced by the first meaningful `RED` since P259 made RED mean something again -- `sentinel: UNACKNOWLEDGED ram:CRITICAL`, the exact alert an auditor showed had been byte-identical to its neighbours. MEASURED at 12,514 records: `science_watch.py` **1,603 MB** + `results_audit.py` **1,475 MB** + a cycle sub-tool **1,396 MB** = **4.4 GB**, run CONCURRENTLY, on a **15.6 GB** box that also hosts **30 driver and supervisor processes**. RAM read **96.7% used, 0.5 GB free**. **INDEPENDENTLY CONFIRMED, not a one-point extrapolation:** `ram:CRITICAL` NEVER fired below ~5k records, fired **5 times on 08-03** (10,653 records) and **14 times in the first 11 hours of 08-04** (12,435) -- the alarm rate tracks archive growth. **PROJECTION at 0.357 MB/record: 8.4 GB at rung 100, 10.5 GB at 189, 14.0 GB at rung 403 (the REGISTERED PRIMARY TARGET), 14.7 GB at 568. The box is exhausted at ~37,500 records; the ladder tops out at 42,128.** ⚠ Worse than C7-loop, which was the same growth in TIME: a timeout degrades to `sci=BLIND`, an **OOM kills a process**, and the drivers share this box. **MITIGATED:** `cycle.py:451` ran the two heaviest tools under `ThreadPoolExecutor(max_workers=2)`; now **1**, halving the pair's peak (3,078 -> 1,603 MB) and roughly doubling the record count the box survives, taking it past the whole ladder. The cost is a longer sweep, which is the right trade -- a slower cadence is a degradation, an OOM that kills a driver is a data-losing incident. Applied via the P268 verified-candidate pattern. **⚠ ESCALATED TO TAMER: the mitigation buys headroom, it does not make the tools streaming. If the ladder runs deep, they need to stop holding the archive in memory.** |
| **P267** (C8-loop) | 2026-08-04 pass 10 | **FIXED + FALSIFIED ON LIVE DATA** | The ssh-gated layer ran **~7x less often than its own documentation claimed**: `cycle_loop.sh` gates on `i % 30`, justified as "30 x ~42 s = ~20 min", but the sweep has grown to 330-540 s so the observed `cores=` stamps were **2.0-4.3 h apart**. The work behind that gate is not cosmetic -- `record_provenance_seal`, whose comment asserts *"every NEW record is sealed within one ssh cadence (~20 min)"* (false by ~7x), and `vanished_array_watch`, the detector for the 15 h purge blind spot. Worse, `i` resets on every loop restart, so a loop restarted oftener than ~2.75 h would NEVER take an ssh cycle. **An iteration COUNT is the wrong unit for a wall-clock promise.** ⚠ THE FIX WENT IN `cycle.py`, NOT `cycle_loop.sh`, and that choice is the substance: the shell is a running `while ... done` that bash parsed once, so an edit there is INERT until a restart -- and restarting the campaign's eyes is a live operation not worth taking for a cadence fix. `cycle.py` is re-invoked every iteration, so it now triggers on ELAPSED TIME via a stamp file and the shell's counter becomes a floor. Falsified live: `.ssh_cycle_last` created, "triggered by ELAPSED TIME" fired, and the next cycle carried `cores=1736`. |
| **P269** (C3-loop) | 2026-08-04 pass 10 | **FIXED** | Both `cycle.py`'s header and `cycle_loop.sh` claimed the loop *"NEVER mutates the campaign"*. False: `lk.unlink()` removes files under the campaign root, and `REAPED_LOCKS.log` records **5 real reaps, two against the CORE/CONFIRMATORY line**. The reap predicate is narrow and defensible and the drivers break such locks themselves; **what was wrong was the invariant as stated**, and a false invariant is worse than a documented exception because the next session reasons from it. Now stated precisely: read-only with respect to campaign DATA (never a record, reward, env.json or frozen marker), writing exactly one class of coordination file, every removal logged. |
| **P268** | 2026-08-04 pass 10 | **MY ERROR -- ONE CYCLE LOST, AND IT EARNS A STANDING RULE** | My C8 patch inserted the ssh stamp block at line 1079 while `ssh_due` is defined at 1182 -- a use-before-assignment. **`ruff` PASSED and `ast.parse` PASSED**, because an unbound LOCAL is neither a syntax error nor an F821. I caught it by reading the line numbers back, but the live loop had already invoked the file once: `ALERTS.txt` at **2026-08-04T10:16:23Z** carries `UnboundLocalError: cannot access local variable 'ssh_due'`. **Blast radius: exactly one monitoring cycle, ~5 minutes blind; the next cycle at 10:21:34Z recovered on its own.** ⇒ **THE RULE, applied immediately to P269: for an instrument invoked every few minutes, VERIFY A COPY AND THEN MOVE IT IN. Post-hoc verification is too late** -- write the candidate to a temp file, parse it, lint it, diff its symbol set, and only then replace atomically. P269 was applied that way and the live loop never saw an unverified file. |
| **P263** (C4-loop) | 2026-08-04 pass 9 | **FIXED + PROVEN** | The cycle line was stamped at sweep **START** and appended at **END**, so its own age when the next line landed was `S_k + sleep + S_k+1`. **MEASURED on the live log: the 08:07:18Z line was 908 s old when its successor arrived, against `session_preflight`'s 900 s cap** -- a preflight in that window would have reported `cycle_log FAIL`, "the monitoring loop is DEAD", on a loop that was plainly alive. A FALSE RUN-KILLER on the campaign's primary liveness signal, and the file's own comment had predicted it "for the future" while it was already happening. Stamped at append time now; worst case falls to `sleep + S_k+1` and the sweep start stays recoverable as `stamp - sweep`. Structurally verified on the shipped file (`sweep_s` computed before `stamp`) and confirmed live. |
| **P264** (C7-loop) | 2026-08-04 pass 9 | **FIXED** | `integrity_gate` -- which does **two complete `os.walk` + json passes over every record** -- carried a **300 s** budget, the ONLY full-archive probe never raised, while `sandbox_gap` went to 900 s and the science layer to 600 s. At 12k records and heading for ~40k it would have begun timing out silently into `attention`, on the gate that guards the CONFIRMATORY path. Raised to 900 s to match its siblings. |
| **P265** (C9-loop) | 2026-08-04 pass 9 | **FIXED + FALSIFIED** | `STATE.json` was written with a bare `write_text`, so an interrupted or CONCURRENT write left a TORN file -- and `_prev_state` swallows the parse error and returns `{}`, which **silently disables five detectors** (the REMOTE_CONTROL change detector, the record delta, the spend-fell RED, the watch-rising diffs, the R115 arrival alert) with nothing anywhere reporting the loss. Concurrent invocations are not hypothetical: **108 duplicate timestamps exist in the log**. Falsified: a torn file parses to `{}`, while temp + `Path.replace` leaves a valid file and the reader can never observe a partial one. (`Path.replace`, not `os.replace` -- this module does not import `os` and a live instrument is the wrong place to add one.) |
| **P266** (C10-loop) | 2026-08-04 pass 9 | **FIXED + FALSIFIED** | A FAILED records probe **silently reset the drought streak**: `records=None` is not a zero delta, but because `None == 0` is False the streak went to 0 -- so an intermittent probe failure once every 15 cycles meant the drought alarm **could never fire at all**. The streak is now carried forward and the failure raises its own attention. Falsified across three cases: mid-drought failure now holds 14 where it reset to 0 before, and both real behaviours (a genuine zero delta, a real arrival) are unchanged. |
| **P260** (C5-loop) | 2026-08-04 pass 8 | **FIXED + FALSIFIED** | **`drift=0` COULD PRINT FROM A MEASUREMENT THAT NEVER RAN, and committed drift NEVER escalated.** `drift` is the invariant that says the running drivers execute the code we think they do. `cycle.py:1043/1051` discarded the return code, and `_run` returns `(99, "<probe failed: ...>")` on ANY exception, which the `<`-prefix filter then emptied to `[]` -- the CLEAN value, silently. Separately there was **no `alerts`/`attention` append for drift anywhere in the file**, only a `note`, so 191 historical lines read `drift=2` without touching the exit code while the module docstring promises exit 1. Now: rc captured, a failed probe prints **`drift=UNKNOWN`** and alerts, and committed drift alerts. Falsified on four inputs -- a timeout and an `index.lock` collision both printed 0/1 SILENTLY before (the collision case failed the *other* way, counting `fatal:` as a drifted path), real drift alerted zero times before, and the clean control is unchanged. |
| **P261** (C6-loop) | 2026-08-04 pass 8 | **FIXED + FALSIFIED** | The integrity gate -- which guards the **CONFIRMATORY path, i.e. the headline result** -- read `int((...splitlines() or ["0"])[0])`, so an **EMPTY stamp file returned 0 = CLEAN** for up to 600 s, and a non-numeric first line raised a `ValueError` that the outer handler swallowed, **skipping the gate with nothing appended anywhere**. This is verbatim the F-5 defect fixed for `sandbox_gap` **60 lines above it** and documented there as "absent reads as zero"; the correction was never carried across. Unreadable now means 98 = UNKNOWN, routed to the not-clean branch. Falsified on five stamps: empty read 0 before / 98 now, two torn stamps raised-and-were-swallowed before, and both real controls are unchanged. |
| **P262** (C2-loop) | 2026-08-04 pass 8 | **FIXED + FALSIFIED ON LIVE DATA** | `guards={rc}` printed the raw guard exit code, permanently **2 on all 5,038 lines** because two guards are acknowledged-failing -- so a NEW guard verdict moved nothing on the line a session is told to read first. Live proof of the cost: a cycle carrying `sentinel: UNACKNOWLEDGED ram:CRITICAL` was byte-identical in every field to its neighbours. The new/known split already existed in the code and simply never reached the line. **Falsified on the live loop, no fixture: the token now reads `guards=0n/2k`** -- zero unacknowledged, two known -- and can move the moment a new verdict appears. |
| **P259** | 2026-08-04 pass 7 | **FIXED + FALSIFIED ON LIVE DATA** | ⛔ **THE `RED` VERDICT WAS DEAD FOR 4,558 CONSECUTIVE CYCLES.** Found by an auditor sent at `cycle.py`. `ready` is derived from `frozen*/` markers ON DISK, which never disappear, so once every line held its full frozen roster the `★ C4 PRECONDITION MET` notice fired EVERY cycle FOREVER, and with the SWEEP-BOUND attention it pinned `verdict = "RED" if alerts` permanently. **Measured: 4,592 RED of 5,038 lines; the last non-RED line was 2026-07-31T19:22:15Z.** A cycle carrying `sentinel: UNACKNOWLEDGED ram:CRITICAL` was byte-identical in every field to its neighbours -- **RED carried zero bits on the one line a session is told to read first.** The notice's own text says *"DO NOT RESTART ... IT IS DONE"*: it is a standing NOTICE, not an alert. Both permanent contributors demoted to `info` (reported every cycle, never touching the verdict), which required threading `info` into `_results_layer`. **FALSIFIED WITHOUT A FIXTURE:** running `cycle.py` by hand would have created a duplicate log line (C9-loop), so the edit was left to the loop's own next invocation and the result read off live data -- **the verdict flipped RED -> ATTN on the very next cycle, the first non-RED in over four days.** ATTN is now driven by the D14 marker, which can clear. |
| **CHAIN-2** | 2026-08-04 pass 7 | **PROVEN-BENIGN (and it refines a closed claim)** | `tpe` advanced **25 -> 27/30** and the chain floor fell **0.74 -> 0.56 d**, but BOTH its jobs showed `qw` with none running, and `c1_tpe_c26` was queued for a candidate that ALREADY HELD A RECORD. Worked to a cause from the driver log: c26 completed at 09:39:09 via round 1, so the queued `c1_tpe_c26_r1` is a **superseded round-2 retry** the driver had already submitted -- its own self-repair mechanism, the same one that produced jobs 83464/85065. `c1_tpe_c27` (submitted 09:39:19) is the live next step. **AND THE MEASUREMENT REFINES s.6.2:** that section records core's jobs as starting in "9-30 min, not queue-starved". True for the SEARCH chain -- `c1_bayes_opt_c27` waited **31 min** (submitted 01:16:04, started 01:47:34). **NOT true for core's TEST work:** `c1_cma_es_test_p01..p04` were submitted 01:28 and are STILL `qw` at 09:41, a **8 h 13 m** queue wait, because pack-8 test jobs queue by submit time like every other line's. So core's C1 chain is compute-bound as recorded, while core's first sealed-test ladder is queue-bound. Not a fault -- fair-share, and every lever is prohibited -- but the two must not be quoted under one claim. |
| **SPEED-4** | 2026-08-04 pass 7 | **PROVEN-BENIGN (still improving)** | Second consecutive improvement: 12 h rate **169.4 -> 171.2**, concentration **67% -> 64%**, chain floor **0.74 -> 0.56 d**, rung-403 ETA **08-09 08:03 -> 06:41**, rung-568 **08-11 17:15 -> 15:18**. The binding DFO arm changed from `tpe` to `bayes_opt` (3 owed each). Eqw/hqw **0**, no line idle without work, drivers 10/10, disk 39.4 GB. Nothing to fix. |
| **A-f4** | 2026-08-04 pass 6 | **FIXED + FALSIFIED** | `publish_status.sh` sent the status commit's stderr to `/dev/null`, so `git commit --only` returning **rc=128** (*"fatal: cannot do a partial commit during a merge"*) killed BOTH pushes via the `&&` chain while the loop printed *"no change to publish"* -- indistinguishable from the benign case, with `check_status_page` measuring only the page's MTIME so the board stayed green and the page never left the machine. Now captures stderr and says so. **Falsified in a throwaway repo across four states:** merge in progress -> OLD prints "no change to publish", NEW prints `COMMIT FAILED rc=128 ... fatal: cannot do a partial commit during a merge`; a real change still commits; **and a no-op cycle stays SILENT**, so this adds no routine false alarm. ⚠ The edit itself was the hazard: `publish_status.sh` runs every ~2 min and editing a running bash script is P250. A waiter polled until a **verified idle window** (discriminating the real publisher, `bash.exe <path>`, from my own shells, which always carry `-c`), patched inside it, and re-checked the count was still 0 across the write. Live publisher verified healthy after: page 0.8 min old, status commits landing. |
| **P251-check** | 2026-08-04 pass 6 | **PROVEN-BENIGN (the fix is holding)** | Re-verified that P251's `--only` is doing its job on live traffic, not just in a fixture: status commits `af97b6b3` and `6ac5ae4f` each touch **exactly `docs/RUN4_STATUS.md` and nothing else**. Before P251 an unrelated 366-insertion instrument change was swept into one. |
| **SPEED-3** | 2026-08-04 pass 6 | **PROVEN-BENIGN (an improvement, measured)** | The four-pass decline REVERSED: 12 h rate **141.7 -> 169.4 rec/h**, slots **1,696 -> 1,904**, and single-line concentration **98% -> 67%**. That is the pass-3 line-handover completing: sonnet's jobs, dispatched 6 h earlier, have begun returning records, so the fleet now has two real producers instead of one. Corroborating: rung-30 remaining fell 428 -> 404, `tpe` advanced 25 -> **26/30**, the critical-chain floor fell 0.93 -> **0.74 d**, and the rung-403 ETA moved 08-10 -> **08-09**. **The declining trailing rate was never a fault; it was the cost of the handover, and this is the other side of it.** |
| **P257** | 2026-08-04 pass 5 | **FIXED + FALSIFIED** | **MY A11 FIX FAILED *OPEN* -- the worst defect class in this repository, and I introduced it while removing a false positive.** Found by an auditor. `sh()` returns `(stdout + stderr)` plus a return code, and I discarded the code (`_, refs = ...`); the only filter dropped lines starting with `fatal`. So a git `warning: ignoring broken ref ...` on STDERR, or `sh()`'s own exception path returning `99, "TimeoutExpired: ..."`, became a "holding ref" and the row printed **OK -- safe off-machine while ZERO remotes contained HEAD.** The code I replaced counted `git log` lines, so an error string RAISED the count and the alarm: **it failed SAFE, and my rewrite inverted the failure direction of the one alarm it promised to preserve.** P230/P232's rule exactly. Now: non-zero rc is UNKNOWN and raises ATTENTION, only strict `refs/remotes/<name>` lines count, and `origin/HEAD` is excluded properly (the old `endswith("/HEAD")` guard was DEAD CODE -- `%(refname:short)` renders it as `origin`). Proven by injecting each poison string: two states that printed OK now raise ATTENTION, control unchanged. **Six permanent tests added** (the auditor also found the change had shipped with zero coverage). |
| **P257b** | 2026-08-04 pass 5 | **FIXED** | Same audit: my docstring claimed *"a stale ref can only make it MORE pessimistic, never less."* **FALSE.** A tracking ref for a branch deleted or force-pushed server-side still satisfies `--contains HEAD` locally, so a stale ref makes the check OPTIMISTIC. A false reassurance inside the caveat that existed to be honest. Corrected, and the row's scope is narrowed to COMMITTED work -- the auditor correctly noted it claimed "safe off-machine" while measuring nothing about the 39 modified files in the working tree. |
| **P258** | 2026-08-04 pass 5 | **FIXED + FALSIFIED** | Mine, and a direct consequence of the P253 fix: it required the capping arm to have a HOLE, so an arm that is STARTED, perfectly CONTIGUOUS and merely SHALLOWER than the next rung named **nobody** -- the line printed `banked rung 0` with a blank reason. **P253 stopped naming the WRONG arm and started naming NO arm.** Live: `test_leg_kimi_k3` began its h2_pair with `distributional` and `scalar` at 12 contiguous seeds each, zero holes, and the most important number in the campaign was reported with no cause. All three cap reasons are now named. ⚠ And my first repair OVER-applied, printing *"holds only 568 contiguous seed(s), short of rung the ceiling"* on the two lines that have FINISHED -- caught by reading my own output; completed lines now read COMPLETE. Cases S1-S4. |
| **TIME-1** | 2026-08-04 pass 5 | **CORRECTED** | ⚠ The auditor ran for **6 hours** and I carried a stale "now" across the gap, reporting ~03:30 local while the true time was **09:14 local / 08:14 UTC**. Every figure in the pass-5 report was accurate WHEN MEASURED and ~6 h old when reported. Re-taken: records **10,897 -> 11,819**, cores 1,888, and **`qwen3.5-9b` advanced rung 30 -> 100**. **THE RULE: after any long wait, re-read the clock before reporting state -- elapsed time is not observable from inside a turn.** |
| **M3-note** | 2026-08-04 pass 5 | **FIXED** | Since A5, `M3_seed_completeness` exits 1 for EITHER a hole below a frontier OR a REGISTERED arm with no record (C6), but the runner's note still said only "holes exist" -- sending a reader to the wrong evidence, the same defect already fixed twice in this file family's verdict lines. Corrected to name both and to point at M3's own VERDICT line. Deliberately deferred until the script was IDLE (P250: never edit a shell script while an instance runs), and the idleness was VERIFIED first rather than assumed. |
| **P255** | 2026-08-04 pass 5 | **PROVEN-BENIGN (a false alarm I raised on myself)** | That idleness check reported **3** live `run_record_layers` processes, after I had already edited the file. Resolved by parent PID: all three were **my own current Bash invocation**, whose command line contains the script path precisely because I was asking about it. **A command-line pattern census matches the process asking the question** -- P229 exactly, where a match pattern on a PowerShell command line made the query kill its own shell. No instance was live, the edit was safe, `bash -n` passes. Recorded because the check was still right to run: asking cost seconds, not asking would have cost P250 a second time. |
| **P256** | 2026-08-04 pass 5 | **FIXED (process)** | Mine. I put a multi-line ledger row inside a `python -c "..."` string invoked from bash. Backslash-escaped quotes and an apostrophe inside a triple-quoted literal collided with bash's own quoting, the Python died on an unterminated string, **and the `&&` chain still committed the code fix without its ledger row** -- a partial write that looked like a success. This is the SEVENTH occurrence of the heredoc/inline-quoting family and the fix has never changed: **write to a FILE**. Blast radius NIL (caught immediately by grepping for the row that should have existed). The lesson worth keeping is the second half: **an `&&` chain whose first link fails silently can still complete its later links, so verify the ARTEFACT, not the exit code.** |
| **CORE-1** | 2026-08-04 pass 5 | **PROVEN-BENIGN (and it is the best campaign news of the session)** | The chain read `tpe 25/30` for a FOURTH consecutive pass, which is exactly the shape of a stall, so it was verified rather than assumed. It is progressing: `c1_tpe_c25` has been RUNNING since 23:41 UTC (~2.5 h into a ~4.45 h modelled serial step) and `c1_bayes_opt_c27` since 00:47 UTC -- bayes advanced 26 -> 27 between passes. **AND FOUR QUEUED JOBS TURNED OUT TO BE THE HEADLINE:** `c1_cma_es_test_p01..p04`, submitted 00:28 UTC, are the SEALED-TEST ladder for cma_es -- the first core arm to freeze. `outputs/campaign_cluster_run4/test/cma_es/` now EXISTS, the driver reports `[c1_cma_es_test] 0/30 done, 30 pending`, and **the core line has begun testing a frozen arm for the first time in the campaign.** ⚠ Precisely: this is per-arm test work AHEAD of the pipelined C4 block -- `grep -c "C4" driver_core.log` is still **0**, so the C4 marker has NOT fired and nothing here should be reported as "core entered C4". They are also the NEWEST jobs in the queue and therefore last, so they wait behind ~253 others. |
| **A11** | 2026-08-04 pass 4 | **FIXED + FALSIFIED** | Found by watching my own board: preflight's `unpushed` row raised ATTENTION **every single time this session committed**, three times, for the ~2 minutes until the publisher's next push -- on work that was already safe on the backup branch. The row compared HEAD only against the working branch and then SAID SO in its own message (*"the backup branch may still carry them"*): an imprecision DOCUMENTED rather than MEASURED. Its actual question is "is this work safe off-machine", so it now asks whether ANY remote ref contains HEAD. **Not a weakening** -- falsified on all three states in a throwaway repo: fully pushed -> OK; **backup-only -> OK now, ATTN before**; **no remote at all -> still ATTN**. The false positive is gone and the real risk is preserved. **A board that raises a routine self-clearing ATTENTION teaches its reader to ignore ATTENTIONs**, which is the `guards=2` pathology that hid P202 for 31 h. |
| **A5** | 2026-08-04 pass 4 | **FIXED + MUTATION-PROVEN** | C6 had NO place in the exit code: `if holed or over or dupes` meant an archive with ZERO holes but registered arms banking 0 exited **0** and printed "VERDICT: CLEAN". The condition C6 was built to surface had no machine-readable signal, and it was masked live only because 11 arms happen to hold holes. `unstarted` now sits in the same contract as `holed` -- both mean the seed set is INCOMPLETE, both are normal mid-campaign, both exit 1. **Deliberately not a NEW always-on alarm; it is the alarm the holes already raise, with the population corrected.** Exit 0 now means what a reader assumes: every REGISTERED arm holds a complete contiguous prefix. Cases **R1/R2/R3** use a fixture with a perfect contiguous arm plus one unstarted registered arm: **R2 confirms NO hole exists anywhere**, and R3 asserts the verdict still flips 0 -> 1. Reverting the exit condition fails R3; the shipped code passes. |
| **P254** | 2026-08-04 pass 4 | **FIXED (estimator settled)** | Mine, and the third value I have published for the same quantity. The repair jobs' wait went **9-18 h** (pass 1, from job start-times -- biased low, invisible completions), then **~6 h** (pass 3, from queue depth -- biased high, it was measuring the fleet EXPANDING into free capacity 1,600 -> 1,712, not steady-state dispatch). Both were the wrong estimator. At saturation -- which is where the fleet now is, slots flat at ~1,700 -- **dispatch equals completion, and completion is directly observable: records land 8 per pack-8 job, so jobs/h = rec/h / 8.** At 141.9 rec/h that is **17.7 jobs/h**, putting 258 jobs ahead of `85065` at **~14-15 h**. Stated with its assumption rather than as a point: it holds only while the fleet stays saturated. **THE LESSON: I published three numbers for one quantity in four passes because I kept changing estimator instead of naming the regime.** |
| **P253** | 2026-08-04 pass 3 | **FIXED + MUTATION-PROVEN** | **THE P244 FAILURE MODE RECURRING INSIDE THE P244 FIX, found by a read-only auditor and not by me.** The per-line note picked the binding cause with `max(arms, key=hole_COUNT)` -- while the comment three lines above it said *"report the binding cause, not the most eye-catching one"*. Hole COUNT and hole POSITION are different quantities: an arm with ONE hole at seed 5 banks 0 and CAPS the line, while an arm with 200 holes all above rung 403 banks 403 and caps nothing. The first version would have named the second, pointing a session at the wrong repair job -- the exact harm P244 was written to stop. Now selects among arms whose banked rung EQUALS the line's minimum. Cases **Q1/Q2** assert on the RENDERED note (what a session acts on); the pre-fix mutant fails Q2 while the shipped code passes. |
| **A2-A4** | 2026-08-04 pass 3 | **FIXED** | Same auditor: the UPPER BOUND claim was CORRECT but its stated reason was INCOMPLETE -- **four** channels remove a low-banking unit, not one. Now all four are printed, and two are made LOUD rather than left as prose: a line whose `frozen*/` roster is unreadable (C6 silently degrades to pre-fix for that line) and the **11 H1 baselines, which can NEVER enter a roster because baselines never get a `-winner` directory** -- verified: `frozen/` holds 7 entries and not one `baseline_*`, while the baselines are CONFIRMATORY node N6 under R108. Both now fail loud. Baseline names are READ from `h1_baselines` in the registration, never hardcoded. |
| **A7-A10** | 2026-08-04 pass 3 | **FIXED** | Same auditor, minor: the selftest comment claimed *"EVERY case below FAILS against the pre-fix code"* -- **false**, only J/K/L/N discriminate; M is a regression guard and O/P guard the fix's own failure modes. A false trust claim inside the file whose purpose is trust, and mine. Also: `report(td)` was called TWICE by an eager failure-detail argument; the verdict line said "N arm(s) hold a HOLE" even when only C4 or C5 fired; `tiers: []` passed the isinstance check and then died in `max()` with exit **1** ("a hole exists") instead of **2** ("could not run"); and case **D** asserts only on its own literal fixture, so it is labelled illustrative and now also exercises `banked_rung`. |
| **F14** | 2026-08-04 pass 3 | **FIXED** | The last inherited row, and it had survived THREE passes on a justification that did not survive checking. It was recorded as *"renaming variables inside live instruments is risk for no gain"* — but **all 12 of `record_validator.py`'s items are inside `_selftest()`, not the production validation path**, and the file has a `--selftest` that makes the change verifiable. The stated risk did not apply and the stated impossibility of verifying was false. All 18 cleared (E702 x14 by splitting statements, E741 x4 by renaming `l` to `ln`), across `record_validator.py`, `analysis_obligations.py`, `falsify_arm_coverage.py`, `json_standards_check.py`. ⚠ My own regex missed one f-string with a single-quoted inner literal and introduced an **F821 undefined name** — caught by re-running ruff rather than by reading the diff. **VERIFIED THE WAY RUN 18 ONLY CLAIMED TO:** selftest **ALL PASS**, all four files compile, ruff **fully clean**, and the live archive re-validated with the pre-edit output diffed line by line — **the only difference is the record count (10,846 -> 10,855, the archive grew by 9 in the interval) and the VERDICT is unchanged.** Not "byte-identical", which is impossible on a live archive; claiming that is precisely RUN 18's error. |
| **SPEED-2** | 2026-08-04 pass 3 | **PROVEN-BENIGN (and it looked like the opposite)** | Measured queue composition: **`leg8` (sonnet) holds 195 of 265 queued jobs = 74%**, submitted 08/03 02:41 which is the OLDEST and therefore the HIGHEST priority, while the five lines that actually CAP the common rung hold **17 jobs between them = 6%** (glm 8, core-C1 4, nemotron 4, deepseek 1), every one submitted later and therefore queued BEHIND all 195. That reads like the fleet starving the lines that matter. **It is not, and the reason is the part worth keeping:** the capping lines are blocked UPSTREAM at their C1/C2/C3 gates, not starved of slots -- they hold few queued jobs because they have not GENERATED more test work yet, and dispatching all 17 instantly would still leave the common rung at 0, because deepseek's repair only lifts `placebo_shuffled` while `distributional`/`scalar` hold no records at all. **A queue-position problem and a pipeline-stage problem look identical from the queue.** Consistent with s.6.2: the critical path is the serial C1 chain, not cores. No lever exists, and every mechanism that could create one is prohibited anyway (raising priority is operator-only, lowering ours is a standing prohibition and one-way, and killing reserved queued jobs forfeits the reservation). |
| **SPEED-1** | 2026-08-04 pass 3 | **PROVEN-BENIGN (measured, not assumed)** | The 12 h rate fell for a third pass running (153 -> 150.2 -> **145.4**) while slots ROSE (1,632 -> 1,600 -> **1,712**). Those point opposite ways, so it was worked to a cause. Per-10-minute arrivals over 2 h decline monotonically: 47, 42, 37, 32, 32, 29, 25, 22, 18, 13, 12, 13. Cause found in the per-line job split: **`leg8` (sonnet-5) now holds 145 running jobs, up from 92, with 82 dispatched in the last two hours, while `leg4` (qwen3.5) fell 106 -> 64.** A newly dispatched pack-8 job consumes slots for 8-15 h before its first record lands, so a LINE HANDOVER shows up as rising slots and a falling trailing rate. Corroborated: Eqw/hqw **0**, queue draining 314 -> 288 -> 265, `line_balance` CLEAN, drivers 10/10, disk fine. This is s.4(2) and s.4(5) of the brief and the composition caveat `stage_eta` already discloses. **Not a regression; the fleet is rebalancing onto a second producer.** |
| **P252** | 2026-08-04 pass 3 | **FIXED (estimate corrected)** | Mine: in pass 1 I priced the repair jobs' wait at **9-18 h** from "199 job starts in 11 h" = 18/h. That estimator is **biased low by construction** -- it counts start times of jobs STILL RUNNING, so every job that started AND FINISHED inside the window is invisible. Measured against queue DEPTH instead: 314 -> 265 in ~65 min = **~45/h net**, which puts ~264 jobs ahead of `85065` at **roughly 6 h, not 9-18**. Both estimators are biased in opposite directions (depth is net of new submissions), so the honest statement is hours, not days. **The same error family as P239: a rate whose numerator and denominator come from different populations.** |
| **P249b** | 2026-08-04 pass 3 | **FIXED** | The P249 census was still reporting `cycle_loop logical=2` every pass, and I was mentally discounting it -- which is exactly how a known-false alarm becomes permanent. Fixed rather than tolerated: a process now counts only if it names EXACTLY ONE known script (which excludes the boot task's shared `cmd.exe` launcher, the half of the lesson RUN 18 never recorded) and its parent does not also match (which excludes Git-bash and venv re-exec chains, the half it did). All six roster rows now read `ok` and agree with preflight's own `processes` row. |
| **P251** | 2026-08-04 pass 2 | **FIXED + FALSIFIED** | **AN AUTOMATED COMMITTER WAS ABSORBING HUMAN WORK.** `docs/ops/publish_status.sh:511` ran a BARE `git commit`, which commits THE WHOLE INDEX -- and that loop fires every ~2 minutes. Anything `git add`ed and not yet committed was swept into the next status commit. MEASURED: `d7b85965`, labelled *"status: T+147h38m"*, carries **366 insertions** of this session's `stage_eta` / `session_preflight` / ledger / CHANGELOG work. Nothing was lost (verified present at HEAD), but the commit log is a PRIMARY SOURCE for the write-up timeline, and it would just as happily have committed a HALF-FINISHED edit. It is the mirror image of P242, where a directory-level `git add` swept 17 runtime logs into an unrelated commit. Fixed to `git commit --only docs/RUN4_STATUS.md`, falsified in a throwaway repo: with an unrelated file staged, the status commit took only the status file and left the other staged. The publisher is re-invoked each iteration, so the fix is live without a restart. **⇒ TWO RULES: an automated committer must name its paths, and never leave files staged on this repo.** |
| **P250** | 2026-08-04 pass 2 | **FIXED + FALSIFIED** | **THE HIGHEST-VALUE FINDING OF THE PASS, and it was mine.** I edited `run_record_layers.sh` (the F13 wording fix) while a background instance of it was RUNNING. Bash reads a script INCREMENTALLY BY BYTE OFFSET, so the live instance resumed at the same offset in the new bytes, landed mid-token (`cord_science_audit.py: command not found`) and **re-executed two layers**. It then printed **`ALL SEVEN LAYERS RC=0`** anyway — because that banner asserted only `fail==0` and **counted nothing**, so it was equally true of a run that executed three layers, or none. Every layer happened to pass, so the certification of an irreplaceable archive was substantively true **by luck**. THREE fixes: (1) `layers_run` is now part of the verdict and a short count prints `ONLY n OF 7 LAYERS RAN. THIS IS NOT A CERTIFICATION.` and exits 1 — falsified on a 2-layer copy, which the old code would have passed at rc=0; (2) per-run `OUTDIR` keyed on `$$`, because two concurrent runs previously shared `/tmp/layer_<name>.out` and each printed an RC pointing at a file the other could overwrite; (3) the whole body is wrapped in one compound command, forcing bash to parse to the closing brace before executing, so a mid-run edit can no longer scramble control flow. **⇒ NEVER EDIT A SHELL SCRIPT WHILE AN INSTANCE IS RUNNING — and a banner that names a count must COUNT.** |
| **F3** | 2026-08-04 pass 2 | **FIXED + MUTATION-PROVEN** | The `-1h` VALUE had no assertion: both fixtures had an empty 1 h window by construction, so `d1` was identically 0 and `d1 = 0` scored full marks. New M11/M12 fixture: a cell at 32 records with 5 inside the hour was at 27 an hour ago, so rung 30 fell by **3** (the crossing part) and rung 100 by the full **5**. Mutants `d1 += 0` and the pre-fix whole-cell rule both fail. |
| **F4** | 2026-08-04 pass 2 | **FIXED + MUTATION-PROVEN** | `_parse_cores` and `concentration` were reachable-but-unasserted. `_parse_cores` carries a PRODUCTION contract (`publish_status.sh` passes `?` on ssh failure and `0` when everything is queued, and neither may crash the empirical block). M1-M8 pin both; letting a non-positive core count through fails M2/M3. |
| **F6** | 2026-08-04 pass 2 | **FIXED (as a stated bound)** | A missing unit is not in `cells`, contributes its FULL rung to `remaining`, and can NEVER contribute to `owing_rate` — so the gate cannot see it. Gating on it was considered and **rejected**: with 8 units missing it would gate every rung at every hour and the table would carry no information, the same degeneracy that killed the per-cell max. The page now states the asymmetry and its DIRECTION explicitly: *"those 8 units are NOT in the rate's denominator and CANNOT be ... Both columns are OPTIMISTIC by that share until those units start."* |
| **F8** | 2026-08-04 pass 2 | **FIXED + MUTATION-PROVEN** | The composition warning hardcoded a 12 h window while `eh2` falls back to 24 h when the 12 h window is empty — so it went SILENT in exactly the state where one line's dominance matters most. Window resolved once and shared. M13-M15 use a 13-23 h-old fixture; hardcoding 12 back fails M14. |
| **F11** | 2026-08-04 pass 2 | **FIXED + MUTATION-PROVEN** | Any stray subdirectory under a `test*` root became a registered unit owing a full rung. Now an arm must HOLD RECORDS or be a REGISTERED frozen winner — the same two-signal rule as S15's C6, so the two instruments cannot disagree about what an arm is. M9/M10. ⚠ My first version tested the directory NAME (`-s<N>`) and dropped every selftest fixture, failing six assertions at once: **a rule that reads the payload survives a layout it did not anticipate; a rule that reads the filename does not.** |
| F12 | 2026-08-04 pass 2 | **FIXED** | `session_preflight --full` advertised "~60 s" against a measured ~200 s. A session budgeting 60 s either kills it or concludes it hung. Corrected, with an instruction to re-measure rather than let it drift again. |
| F13 | 2026-08-04 pass 2 | **FIXED** | `run_record_layers.sh` called itself SEVEN in the banner and EIGHT in a comment. Reconciled: seven GATED layers plus three ungated MEASUREMENTS (S15 is a measurement, not a gate). |
| **P249** | 2026-08-04 pass 2 | **FIXED** | Mine: an ad-hoc process census reported `cycle_loop logical=2` and `publish_loop logical=2` against preflight's correct 1. Cause: the boot task's shared `cmd.exe` launcher names EVERY loop on its command line, so it matched each pattern and was counted as a separate root each time. Resolved by parent PID (12640 -> 25064 -> 25084 is ONE chain). **A pattern census counts CHAINS *and* LAUNCHERS** — RUN 18 recorded the first half of that lesson and I re-created it with the second. Preflight was right; my throwaway was wrong. |
| F5 | 2026-08-04 RUN19 | **FIXED** | `CEILING = RUNGS[-1]`; all **8 executable** `568` sites now derive from it (historical numbers in comments deliberately left, they record what was true then). |
| F9 | 2026-08-04 RUN19 | **FIXED** | The archive walk now precedes the clock sample, so every mtime held is <= the clock it is compared against. |
| F10 | 2026-08-04 RUN19 | **FIXED** | Selftest section J gained the `except` it lacked; an exception there is now a recorded FAIL rather than a traceback that suppresses every other result. |
| F7 | 2026-08-04 RUN19 | **FIXED** | E1 no longer asserts a host-dependent skew (it would FAIL on any UTC host, i.e. exactly where the defect is impossible). It reports the observation, and **E1b** asserts the portable invariant: no window bound in the file is built from `utcnow()`. ⚠ My first E1b was itself wrong — it matched the module docstring that DOCUMENTS the trap and its own source line. Narrowed to assignment targets. |
| **F2** | 2026-08-04 RUN19 | **FIXED + MUTATION-PROVEN** | The go-forward exclusion had NO coverage and both deleting and inverting it scored full marks. New **K** fixture: a near-ceiling HIGH producer (560 records, excluded), a mid cell (300, included) and a sub-rung-30 cell so the ladder dates. **K4 is a RATIO, not a gap** — the first version asserted "gap > 24 h" and the INVERTED mutant still cleared it on a 90-day horizon. Fixture rates 44 / 4 / 40 give ratios 11 / 1.1 / 1.0. Mutation proof: delete → K3+K4 fail; invert → K4 fails. |
| **F1** | 2026-08-04 RUN19 | **FIXED + MUTATION-PROVEN** | `GATED` is now **absorbing upward**: once a rung gates, every higher rung gates and is tagged `barrier>=R`. Reaching 568 requires reaching 279, so a low barrier cannot coexist with a high date. New **L** fixture reproduces the shape; removing absorption makes L2 fail. |
| **F15** | 2026-08-04 RUN19 | **FIXED** | **Found by the selftest failing to report its own failure.** A `ck` value can carry rendered page text, rendered text carries non-ASCII, and the console is cp1251 — so printing a FAIL line raised `UnicodeEncodeError` INSIDE the reporter. The run died with a traceback and **not one pass/fail line**. A reporter that crashes on the content it exists to report is the worst failure mode available; it is why F2/F1/E1b were invisible for one cycle. Now `backslashreplace`-sanitised. |
| **P247** | 2026-08-04 RUN19 | **FIXED** | Mine: **my A0a-A0d cases tested the FUNCTION but not that `render()` USES it.** The mutation proof reverted only the CALL SITE to the elapsed-wall-clock formula and every A0 case still passed. Added **A0e**, which asserts render's own output says `UNKNOWN still to run` on a fixture with no search tree. Caught by the proof, not by review. |
| **P248** | 2026-08-04 RUN19 | **FIXED** | Mine: F1's absorption silently made three existing fixtures gate every rung, so **J1/J2 began comparing empty lists** — vacuous passes created by my own fix, the precise class this campaign keeps finding. Caught because J3 (`rows >= 3`) failed. Fixtures gained a sub-rung-30 producer; J1 now exercises **seven** dated rows, up from four before the change. |
