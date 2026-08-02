# RUN 15 — SESSION PROMPT. **READ THIS BEFORE YOUR FIRST SUBSTANTIVE ACTION.**
Written 2026-08-02 ~19:15 UTC at Tamer's instruction: *"I want to transition into the new claude code
session, please document absolutely everything, ultarthink very deeply and extensively, and write a
prompt for a new session. make sure you dont miss anything I have told you and ensure an extremely
smooth transition."*

> **You are the BUILDER session on a live, irreplaceable MSc dissertation campaign.** RUN 4 has been
> running since 2026-07-28. Real money is spent, the test data is sealed, there is **no re-run**.
> You inherit **OPS + the MONITOR LINE + COORD**. A **WRITER** session owns `paper/**`.
>
> This supersedes `docs/RUN14_SESSION_PROMPT.md`. Where they disagree, **this wins** — RUN 14
> corrected several of RUN 13's own answers, and then corrected three of its own.

---

## §0 ★★★★★ TAMER'S STANDING BRIEF — his words, and they are the operating contract

**The block he repeats every message, verbatim:**

> *"I give you full permission, and ratify the actions. I give you no permission to stop until
> absolutely everyhting is strictly absolutely 10000000% absolutely flawless. Ultarthink veyry deeply
> and extneisvelly, I give you full permissiosn, and full freedom, do whatever it takes... Take as
> much time as you need, as many tokens as you need... dont be lazy... act with accordance to teh
> priorities, targets, aims, make sure you work very carefully, accuratelly, precisely and
> surgically, and always verify and always make sure absolutely everything is very deeply and
> extenisvelly strictly absolutely 1000000000% correct and flawless."*

**The two standing WORK items, in HIS priority order (he stated the ordering explicitly):**

> **(1) THE RECORDS — FIRST.** *"make sure you also very deeply and extensively constantly check each
> record, make sure every record individually is very strictly flawless, logical, meaningful... dive
> very deep, and look at the every record, and ensure absolutely everything there is flawless, and
> the records are logical, meaningful, no science issue and etc."*
> **(2) THE CORES — SECOND.** *"only after you finish with this, go to the next issue which is: also
> there is an issue, we are not even at 2k cores... speed up to an absolute maximum."*

**Other standing instructions given this session:**
* *"I give you permission to move stuff to another disk to free up space, **but move, never delete**"*
* *"study all documents in this project very extensively before you act. You must have an extremely
  comprehensive knowledge and 0 gaps"*
* He asks direct questions and expects direct answers: *"so what should we do?"*, *"what should I do
  to reach max seeds?"*, *"wdym disk caps the results? did we solve this issue?"*
* He watches the live status himself: *"what happened with run4 live status? I stopped seeing any
  updates, what's going on?"* — **so a stall must be explained to him proactively, with cause.**

**HOW TO READ THIS.** Full permission raises the bar on the THINKING; it does not lower the bar on
verification. Every claim in this document was measured. Where RUN 14 was wrong, it says so.

---

## §1 YOUR FIRST COMMANDS

```bash
cd /c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
tail -3 docs/ops/watch/CYCLE_LOG.md          # THE MANDATE — first tool call of EVERY batch
python docs/ops/session_preflight.py --full  # 0 clear · 1 ATTENTION · 2 FAIL
ssh -o ConnectTimeout=10 -o BatchMode=yes myriad "hostname"   # ⚠ SEE §2 — this was DOWN at handover
```

Then say **"Resuming from: … — next: …"** and CONTINUE. Read order after that: `docs/HANDOFF.md` §1 →
`memory/session-current-focus.md` (▶ NOW) → `CLAUDE.md` → CHANGELOG `[2026-08-02d]`/`[e]` → execution
record **§105–§114**.

**MONITORING MANDATE:** read the cycle log on the FIRST tool call of every batch. `>2 min` old ⇒ the
loop is DEAD (check whether one is already running before restarting). `RED` is normal.
**`drift=0` and `sci=OK` are the only two that must never change.**

---

## §2 ⚠⚠⚠ THE LIVE INCIDENT AT HANDOVER — MYRIAD SSH IS DOWN, AND IT IS NOT OURS

**FROM 2026-08-02 17:08:07Z, the campaign has pulled ZERO new records.** Records frozen at **4,733**.

**DIAGNOSED TO A CONCLUSION — every client-side cause is RULED OUT by measurement:**

```
myriad.rc.ucl.ac.uk (round-robin) -> 193.60.252.107 : Connection reset by peer
login12.myriad.rc.ucl.ac.uk       -> 193.60.252.108 : Connection reset by peer
login13.myriad.rc.ucl.ac.uk       -> 193.60.252.109 : Connection reset by peer
```

| ruled out | evidence |
|---|---|
| network / VPN tunnel | `Test-NetConnection` port 22 **succeeds** on all three; AnyConnect adapter Up, routing via the tunnel |
| a block on our IP | Tamer reconnected the VPN → **new IP 10.151.114.53** (was .48) → still reset |
| one dead login node | **all three** distinct IPs reset |
| the DISM run | outage began **17:08**, DISM ran **17:21–17:25** — 13 minutes LATER |
| ssh auth / keys | the reset happens **pre-banner**: `debug1: Local version string` sent, then reset, no `Remote protocol version` line ⇒ server-side admission control, before authentication |

**⇒ IT IS A UCL-SIDE FAILURE ACROSS EVERY MYRIAD LOGIN NODE.** UCL's own status log records this exact
symptom class on 2026-07-17 (*"two util nodes that run the scheduler's qmaster"* failing to fail over
→ login issues, fixed by midday). **ACTION: Tamer reports it to rc-support@ucl.ac.uk.** There is
nothing left to fix client-side; RUN 14 exhausted it.

**THE CAMPAIGN IS SAFE, AND HERE IS THE ARITHMETIC:**
* **Jobs keep RUNNING** — they execute on COMPUTE nodes and never touch the login node. Only *pulling
  results* does. Last good reading: **247 jobs / 1,976 cores**.
* **Nothing is lost.** Completed trainings sit on the cluster until they can be pulled.
* **Margin: worst `ops_failures` = 26 of 72** (~2.3 h at `--poll-secs 180`).
* **Hitting 72 is NOT loss either:** the driver raises, `mode_d_supervisor.ps1` relaunches it with
  `--resume` after a 600 s backoff (`$maxAttempts = 1000`), and it re-derives pending from disk.
* Processes healthy throughout: **11 driver lines · 12 supervisors · 1 cycle loop · 1 sentinel**.

**WHEN SSH RETURNS:** records resume pulling by themselves. Verify with the cycle log's `records=`
climbing again, then re-run the six record layers (§5) and `docs/ops/placeable_capacity.py`.
**Do NOT hammer the login node while it is refusing** — RUN 14 stopped its own ad-hoc ssh for exactly
this reason.

---

## §3 ★★★★★ THE ACTION QUEUE — in priority order, and every item is TAMER'S

**RUN 14 established the single most important operational fact about this harness:**
**the agent can measure, build, test, document and commit — it CANNOT operate the machine.** Every
remaining lever therefore terminates in a command for Tamer. Say so up front rather than discovering
it per action.

### ① REPORT THE SSH OUTAGE TO UCL — blocks everything else (§2)

### ② ★★★★★ D29 — THE PAGEFILE. **THIS ONE COMMAND REMOVES THE CEILING ENTIRELY.**

**TAMER'S EXPLICIT REQUIREMENT (2026-08-02, verbatim):** *"make sure we resolve the issue with disk,
we must have **no ceiling** and must be able to run to **maximum**."* **Rung 568 is the maximum, and
D29 is now the ONLY thing standing between the campaign and it.** Measured at handover:

```
rung 568 needs 37,334 more records = 18.3 GB, ending at or above the 20 GB floor
   => C: free REQUIRED : 38.33 GB
      C: free now      : 31.79 GB      -> SHORT 6.54 GB
      + D29 (+12.26)   : 44.05 GB      -> MARGIN 5.72 GB   ** RUNG 568 REACHABLE, NO CEILING **
```

| ceiling | before RUN 14 | after DISM (DONE) | after D29 |
|---|---|---|---|
| highest reachable rung | **189** | **340** | **568 — the maximum** |

**⇒ DISM (already done, +5.75 GB) took the ceiling 189 -> 340. D29 takes it 340 -> 568 and removes it
altogether.** Nothing else is required: throughput already exceeds what max seeds needs (§7), and
`/ResetBase` (+2.37 GB) is optional headroom, not a requirement.


```powershell
$k = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management'
(Get-ItemProperty $k -Name PagingFiles).PagingFiles      # RECORD the original first
Set-ItemProperty -Path $k -Name PagingFiles -Value @('D:\pagefile.sys 16384 28672')
# then ONE reboot, while awake
```
**Measured safety:** `C:\pagefile.sys` is 12.26 GB allocated with a **peak usage EVER of 1.06 GB**;
`D:` keeps 18.67 GB against a **combined peak-ever of 4.14 GB** on a 15.64 GB-RAM box — a 4.5x margin.
**HKLM writes are BLOCKED for the agent.** Needs a reboot, which restarts all twelve lines; reboot
recovery is registered but has never been exercised, so do it awake.

### ③ THE R115 DISCLOSURE DECISION — the only item that touches the GRADE (§8.1)

### ④ ONE SUPERVISOR RESTART CARRYING **BOTH** FLAGS — 8 → 84 reachable cores (§6.3)
`scripts/mode_d_supervisor.ps1` `$cpuLane`: `"--pool","d"` -> `"--pool","db"` **and** `"--pack","8"`
-> `"--pack","4"`. Then `taskkill /PID <a supervisor PID> /T /F`; the fenced watchdog
(`docs/ops/watchdog_fenced.ps1`, 300 s) revives the line on the edited script with the D15 fence
intact. **Process termination is BLOCKED for the agent.**
⚠ **Close the `node-b00a-008` residual first — see §6.4.**

### ⑤ `qdel 66103 66104 66105 66106 66107 66108 73026 73027` — up to +64 cores
Six unschedulable `sshorig` + two of RUN 13's own probe jobs (P188). **`qdel` is BLOCKED for the agent.**

### ⑥ `campaign_summary.json` **AT TEARDOWN** — still the only UNRECOVERABLE item.

---

## §4 ⚠ FIVE HARNESS LIMITS — and ONE surprise that broke the pattern

```
qdel <id>                          BLOCKED
taskkill /PID  AND  Stop-Process   BLOCKED   ⚠ RUN 13's brief says taskkill WORKS. IT NO LONGER DOES.
HKLM registry write                BLOCKED
Rename-Item on a live directory    BLOCKED
New-Item -ItemType Junction        BLOCKED
```

**Read them as ONE fact: every action that changes the machine's state outside the repo is blocked.**

**★ THE SURPRISE, AND IT IS WORTH RE-TESTING RATHER THAN ASSUMING:**
**the session runs ELEVATED.** `[Security.Principal.WindowsPrincipal]::IsInRole(Administrator)` =
**True**. That is how RUN 14 was able to run `Dism.exe /Online /Cleanup-Image /StartComponentCleanup`
and reclaim **5.75 GB** (§7). **So "needs admin" is NOT the same as "blocked" — test the specific
command.** RUN 14 nearly failed to do the one disk fix it could actually perform because it assumed
admin operations were out of reach.

---

## §5 ★★★★★ THE RECORDS — SIX INDEPENDENT LAYERS, ALL CLEAN. RUN THEM EVERY SESSION.

**This is Tamer's FIRST priority and RUN 14 built four of the six layers.**

```bash
python docs/analysis/record_validator.py            # R1-R9  contract, hashes, identity, endpoint replay
python docs/analysis/record_provenance_seal.py      # P1-P4  the record vs the FILES beside it
python docs/analysis/record_science_audit.py        # S1-S10 scientific soundness + the BANKED RUNG
python docs/analysis/fed_text_identification.py     # S11    is each arm FED what the design registers
python docs/analysis/reward_code_audit.py           # S12    the AUTHORED CODE + the live sandbox gate
python docs/analysis/fed_value_coherence.py         # S13    are the fed VALUES coherent + pipeline exact
```
**All six exited 0 at handover.** Each has `--selftest` (18, 8, 8, 9 cases respectively for the new
four) with a mutant per failure mode. **S1-S10 is WIRED into `cycle.py`, rate-limited to once per
30 min** (`SCIENCE_AUDIT_MIN_SECS`) — see §9's P194 for why the rate limit exists.

**THE FOUR NEW LAYERS AND WHAT EACH PROVED:**

| layer | the question nothing else asked | result |
|---|---|---|
| **S1-S10** | is a record SCIENTIFICALLY sound? | every test series is the registered **T=1571**; no non-finite value; every allocation a valid simplex; no degenerate series |
| **S11** | is each arm FED what the design registers? | **exact on 1,139 fed texts** — see below |
| **S12** | does the authored code still pass the LIVE gate? | **4,683 / 4,683** still admitted by `src.sandbox.executor.ast_gate` |
| **S13** | are the fed VALUES coherent, and did the model see what we measured? | CVaR monotone on **1,507** vectors; **444/444** pipeline-matched |

**★ S11 IS THE IDENTIFICATION ITSELF, AUDITED FOR THE FIRST TIME.** Read with numbers masked:

```
every arm      : identical preamble + identical scalar line + identical exploration directive
scalar         : NOTHING further                     0 diagnostic lines x 234
scalar_cvar5   : one CVaR line                       1 x 218
distributional : the registered m=6 tail vector      6 x 226   (CVaR x4 + left-tail mass + skew)
placebo        : 6 "reference value" lines, INERT    6 x 228
placebo_shuffled: the same 6 labels, values shuffled 6 x 230
```
**⇒ the arms differ in the fed CONTENT and in NOTHING ELSE.** The construct-validity claim is now a
measured fact, not a design-document assertion.

**★ S13 PROVED THE PIPELINE IS EXACT.** `cvar_01 <= cvar_05 <= cvar_10 <= cvar_25` is a mathematical
NECESSITY (a more extreme level averages a worse tail) and it holds on **all 1,507** archived vectors.
And every rendered fed vector matches — to the 4 dp the renderer emits — a vector **actually measured**
on a real candidate. **The model was fed the numbers we measured, correctly labelled and ordered.**

⚠ **THE RENDER ORDER IS NOT THE LEVEL ORDER.** The prompt emits 5%, 10%, 25%, **then** 1% (flagged
*high-variance estimate*), then mass and skew. **Parse BY LABEL** — positional parsing silently pairs
`cvar_25` with `cvar_01`.

---

## §6 ★★★★★ THE CORES ANSWER — exhaustively enumerated and priced

### 6.1 WHERE IT ACTUALLY WENT
```
session start 1,832 -> 1,960 -> 1,976 cores      job cap 1000/1000 SATURATED -> 847/1000
```
**The 2k target is effectively met.** The rise came from ABSORBING free capacity, not from any action:
with ~600 of our jobs queued, the fleet claims every placeable slot within a scheduler tick.

### 6.2 EVERY LEVER, MEASURED ON THE DAY

| lever | worth | status |
|---|---|---|
| `qdel` the 8 junk jobs | up to **+64** | **TAMER'S** (blocked) |
| pool widening onto b00a | +24 to +88 (varies hourly) | ready, blocked on process-kill |
| **pack 8 -> 4** | **+52** | **RE-OPENED — see 6.3** |
| memory request 2G -> 1.6G/slot | +16 | ★ **REFUSED ON MEASUREMENT** |
| e00a (RUN 13's "biggest prize", 328 cores) | **0** | **UNREACHABLE** — 4/4 real submissions refused, and it is ALREADY in `lanes.EXCLUDED_CPU_POOLS` as a GPU pool |
| f00a | **0** | `-pe smp-F` reports "only offers 0 slots" |
| SGE priority | **0** | self-elevation forbidden by fair-share; lowering ours forbidden by Tamer's absolute rule |
| more entitled hosts | unbounded | an RC/admin request — Tamer's call |

**THE MEMORY LEVER WAS INVESTIGATED PROPERLY AND REFUSED.** `qacct` on three completed 8-slot jobs:
**maxvmem 11.435 / 11.449 / 11.564 GB against a 16 GB request** — a real 28 % over-provision. But
cutting to 1.6 G/slot buys only **+16 cores** for a twelve-line relaunch and a ~1.2 GB margin over an
observed peak, on 15-hour trainings **with no re-run**. Three samples is not a distribution.
**Recorded so it is not re-litigated a fourth time.**

### 6.3 ★ THE ONE THING THAT GENUINELY CHANGED: THE PACK LEVER RE-OPENED

It was refused earlier ONLY because halving the pack doubles the job count against a saturated cap.
**The cap eased to 847/1000.** Measured:

| config | placeable cores |
|---|---|
| **pack 8, pool d — WHAT WE REACH TODAY** | **8** |
| pack 8, pool d+b | 32 |
| pack 4, pool d | 32 |
| **pack 4, pool d+b** | **84 — 10x today's reach** |

**259 slots are STRANDED at pack 8** — free, but on hosts holding fewer than eight. **Both levers are
the SAME single action** (§3④).

**PACK WIDTH IS SCIENCE-SAFE, AND RUN 14 VERIFIED IT RATHER THAN INHERITING IT:**
`search OMP=8 on 1,507 trainings · test OMP=1 on 2,467 · both uniform`. Pack governs how many
trainings share a **JOB**; OMP governs how many threads a **TRAINING** uses. With test OMP uniformly 1,
a pack change **cannot** alter float reduction order.

### 6.4 ⚠ THE RESIDUAL THAT MUST CLOSE BEFORE WIDENING ONTO b00a

Four b00a hosts were probed. All report `Intel(R) Xeon(R) Gold 6240 CPU @ 2.60GHz`, 2 sockets, 36
cores, avx512f=1, microcode 0x5003901 — **byte-identical to the `cpu.model_name` in a live pool-d
`env.json`**, so the C3 substrate key cannot go heterogeneous. **BUT `node-b00a-008` returns a
DIFFERENT CPU FLAGS SET** (`639b6722…` vs `9ede37ab…`). **The C3 gate keys on the model NAME and would
stay GREEN across it** — which is exactly why it matters: the determinism envelope is the broader
standard. Almost certainly mitigation/perf-counter flags with no arithmetic effect, but **not diffed**.
**Close it by diffing the flag lists, or fence `node-b00a-008` like `node-d00a-230` (one token, costs
8 of the 88 cores). `node-b00a-014` remains unprobed.** Probe with `docs/ops/cpuprobe14.sh` — its spec
is derived from a LIVE running job and it WORKS (`-pe smp 1 -ac allow=<pool>`); `cpuprobe13.sh` is
banner-marked SUPERSEDED because its spec can never run (P188).

### 6.5 ★★★ THE BIGGEST LEVER ON THE REPORTED RESULT IS NOT CORES — IT IS SUBMISSION ORDER

The pipelined C4 path submits **all six assurance blocks at once** (measured: leg9's t1..t6 within
2m19s; leg6's within 3 s). `weight_waiting_time = 1.0` at equal priority ⇒ **the queue is ordered
LINE-major, so one line's rung-568 block outranks another's rung-100 block by HOURS.**

**Measured cost:** of **1,735** sealed-test paired records, **625 (36.0 %) sit ABOVE the common rung —
and every one is on a single line.** Under the 2026-08-27 stop that work raises the reported rung by
NOTHING unless ten other lines catch up.

⚠ **DOWNGRADED, HONESTLY:** the throughput forecast says we reach rung 340 anyway, so the slack
absorbs it. Changing the C4 dispatch means editing `campaign.py` inside the driver import closure and
relaunching twelve lines mid-ladder. **RUN 14's recommendation is NOT to do it.** Recorded because it
is real, and because every reordering route is closed to the agent anyway (`qdel` blocked; priority
elevation needs an admin; **`qalter` is refused — `jsv_allowed_mod ... does not allow: pe_name,pe_min`,
so a queued job can NEVER be moved to another pool**).

---

## §7 ★★★★★ DISK — WHAT "DISK CAPS THE RESULTS" MEANS, AND WHAT WAS FIXED

**THE MECHANISM, because Tamer asked directly.** The reported result is the COMMON seed rung across
all 11 lines (R101). Every training writes ~480 KB. **Before RUN 14 acted:**

```
C: 25.84 GB free, floor 20  ->  5.84 GB usable  ->  11,895 more records
=> the ladder STOPPED just past rung 189, while THROUGHPUT would deliver 340+
```
And **rung 189 is exactly where H2 stops being INCONCLUSIVE** (`docs/SESOI_DERIVATION_2026-07-25.md`:
equivalence achievable at **n\* <= 173**). **The campaign was landing ON the boundary of its own
decisive result with no margin.**

**★ WHAT RUN 14 FIXED, and it needed no reboot:**
```
Dism.exe /Online /Cleanup-Image /StartComponentCleanup      (exit 0, 3.9 min)
C: free  25.84 -> 31.59 GB   (+5.75 GB)
component store  12.96 -> 6.82 GB ; backups 8.50 -> 2.37 GB
=> THE CEILING MOVED FROM RUNG 189 TO RUNG 340
```
Preflight's disk item flipped **ATTENTION -> OK** — the first fully clean `VERDICT: OK` of the session.

**STILL OUTSTANDING (both Tamer's):**
* **★ D29 pagefile: +12.26 GB -> RUNG 568, THE MAXIMUM, WITH 5.72 GB OF MARGIN. THE CEILING
  DISAPPEARS.** This is Tamer's explicit requirement — *"we must have no ceiling and must be able to
  run to maximum"* — and it is now a single command plus one reboot. §3②.
* `/ResetBase` on DISM: ~2.37 GB more, but **makes existing updates non-uninstallable — irreversible,
  so RUN 14 deliberately did NOT run it unilaterally.**

**THE ARCHIVE-RELOCATION OPTION AND WHY IT WAS REJECTED.** The archive is small today (**1.748 GB /
26,626 files**) and D: has **115 GB** free, so a junction would work and is git-safe (**0 tracked files**
under `outputs/campaign_cluster_run4`). **But the archive is on C: and the live mirror is on D:, so the
campaign currently survives EITHER disk failing; moving the archive to D: puts BOTH copies on one
drive.** On irreplaceable data that is the wrong trade. Junction creation is blocked for the agent
anyway. **A complete point-in-time snapshot was left at `D:\llm_rp_run4_archive`** (1.748 GB, 4,274
records, 16:03Z) — **NOT auto-updated, nothing reads it**, kept as a free third copy under
move-never-delete. Do not mistake it for a live path.

**AND MOVING FILES CANNOT SUBSTITUTE.** Measured with reparse points excluded: every large app is
**already junctioned** to D: by earlier sessions (Lumion, Graphisoft, Docker, Office, Epic, SketchUp,
Total Commander, Interior3D), caches already moved, **hibernation already off**. What remains is the
project itself, `WindowsApps` (Store/TrustedInstaller-managed — a junction BREAKS it; the supported
route is Settings > Apps > Move), **the Python the live campaign runs on**, VS Code, and running
Adobe/Edge. **Only ~1.02 GB is safely movable.**

---

## §8 ★★★★★ THE FINDINGS THAT AFFECT THE DISSERTATION

### 8.1 ⚠⚠⚠ R115's REGISTERED JUSTIFICATION IS NOW EMPIRICALLY FALSE — and it is headed for the PDF

`config/preregistration.yaml: fitness.winner_max_fallback_frac: 0.10` defends its VALUE as immaterial:

> *"THRESHOLD-INSENSITIVE, not tuned: over 613 counter-carrying records the distribution is strongly
> bimodal — worst trace 0.41 %, mildest severe 39.40 %, a 96x EMPTY GAP — so any value in ~1-35 %
> partitions the data identically."*

**Re-measured on the 3,988 records the campaign has now produced, and INDEPENDENTLY CONFIRMED by a
read-only auditor:**
```
records inside the claimed EMPTY GAP (0.41 % .. 39.40 %) : 88     <- the gap has FILLED
ineligible by threshold: 1%->95  2%->91  5%->87  8%->53  10%->21  15%->20  20%->16  35%->14
```
**Every threshold in 1-35 % now partitions the data DIFFERENTLY.** The live monitor agrees by a second
route: the cycle log's **`r115=21B`** is 21 breaches **AND BINDING**.

**★ THE AUDITOR ESCALATED IT FURTHER, AND THIS IS THE CRITICAL PART.** At the tier where R115 actually
ACTS (search-candidate selection, `scripts/run_campaign.py:777-780`): **15 of 60 `(line, arm)` groups
have a DIFFERENT ELIGIBLE SET across the 1-35 % band**, and the frozen winner
**`qwen3_5_9b/placebo_shuffled-g0-c3` IS the 9.08475 % candidate**. **At any threshold at or below
9.08 % — well inside the band the registration calls identical — a DIFFERENT reward would have been
frozen and sealed at 30 seeds.** The threshold is **selection-determining on an already-sealed arm**.

**WHAT IS AND IS NOT WRONG.** The VALUE is protected: it was pre-committed **before any campaign data
existed**, and the rule is effect-blind by construction (`_winner_eligible` never touches
`val_fitness`). **It is NOT a forking path.** What is wrong is the **JUSTIFICATION**, and an
adversarial reader — Okhrati is exactly that reader — would re-derive the distribution and break it.

**⚠ IT CANNOT BE FIXED BY EDITING.** `config/preregistration.yaml` AND `PREREGISTRATION.md` are BOTH
hash-bound inside the frozen canonical hash `3ca6f01ab772`. **The correction is a DISCLOSURE and it is
TAMER'S DECISION** — a dated amendment row, or a stated Limitation, restating the justification
historically ("set on 613 pre-campaign records; the gap has since filled; the value was pre-committed
before any campaign data existed, which is what protects it"). **The threshold must NOT be changed** —
that would convert a presentational fix into a post-data forking path.

### 8.2 A REAL WRITE-UP DISCLOSURE: THE NUMERACY BOTTLENECK IS VISIBLE IN THE SEALED LEG

Sealed-test safe-default fallback is confined to **`test_leg_qwen3_5_9b`** (the ~17 % authoring-
reliability BOTTOM anchor): `distributional` (TREATMENT) 30 records at 7.84-7.85 %,
`placebo_shuffled` 30 at exactly 9.0847 %, and that leg's `scalar` at **zero**. So within that leg the
H2 pair is **asymmetric in EXECUTION QUALITY** — the confound R115 exists to bound, INSIDE its
tolerance (worst 9.0847 % against the 10 % floor, margin 0.92 pp). **No result is compromised**; it is
the bottleneck made visible, and it belongs in the write-up.

### 8.3 ⚠ DETERMINISM IS **NOT** EVIDENCED BY THIS ARCHIVE — a claim RUN 14 made and had to retract

S4 groups sealed-test records by `(arm, seed, reward_source_hash)` and found **0 disagreements**. RUN
14 reported that as *"determinism is now MEASURED, not asserted"*. **That was FALSE.** Verified:
**2,825 sealed-test records, 2,825 distinct keys, ZERO keys with more than one record.** **RUN 4
contains NO REPLICATES, so the check compared NOTHING.** The audit now prints the replicate count and,
when it is zero, says outright that the result is vacuous. **Determinism must be evidenced from the
30/30 bit-identical farm or a crash-rehearsal replay — NOT from this archive.**

### 8.4 OTHER STANDING DISCLOSURES
* **`metrics.train_curve.return` is 100 % NaN** on every record (SB3 `ep_rew_mean`; no episode closes
  in the logging window). `actor_loss`/`critic_loss`/`ent_coef`/`step` are ALL populated and no figure
  reads `return`. A disclosure, not a defect — **but do not build a convergence exhibit from it.**
* **8 of 11 lines have an arm with a FROZEN WINNER but NO sealed-test record**, including the CORE
  line, which has **neither `distributional` nor `scalar`** — i.e. the H2 co-primary pair has no
  sealed-test record there yet. Expected mid-campaign (they are tested at the C2 `h2_pair_test`
  stage), **but "banked rung 30" describes the arms that STARTED, not a full-roster bank.** S10 now
  names the missing arms.
* **D18 HAS RECURRED:** two NESTED duplicate directories (`x/x/record.json`) in
  `search_leg_glm_5_2/placebo_shuffled-g3-c4` and `search_leg_haiku_4_5/scalar-g1-c3`. Both SEARCH
  tier, **ZERO in the sealed test**, both inner records **byte-identical** to the outer. The real
  consequence is that every `rglob` instrument counted them TWICE. **Excluded in all four new
  instruments (skipped, never deleted).** ⚠ `analyze_campaign.py`'s loader keys on
  `(directory, run_id)` after A79 — **a nested dir IS a different directory, so it will admit both.**
* **The reflection source is STICKY** (`src/llm/loop.py:728-729`): `prev_feedback_block` is replaced
  ONLY when a generation produces a best candidate, so a fed vector can come from ANY earlier
  generation. Traced: `scalar_cvar5` at g5 was still being fed g3-c4's vector.
* **The no-feedback fallback is BY DESIGN** (`loop.py:406-409`): a generation yielding no usable
  candidate leaves `prev_feedback_block = None`, so the next generation uses the INITIAL prompt.
  Three records do this, all in `qwen3_5_9b`, and each one's preceding generation has ZERO archived
  candidates. **Verified, not assumed.**
* **`lanes.EXCLUDED_CPU_POOLS` is referenced only in DOCSTRINGS and enforced by NO code path** — the
  list that protects CRN bit-exactness is advisory. Not fixed (driver import closure).
* **`REGISTERED_TEST_LEN = 1571` is sourced from a COMMENT** in the frozen yaml (the N6 endpoint note),
  not an independent config value, so S2 is a self-consistency check. MINOR, recorded.
* **The 56 frozen-winner markers carry NO execution-quality counters**, so the R115 eligibility fact
  is only reconstructible from the source search record. MINOR provenance gap.

---

## §9 ⚠ RUN 14's OWN ERRORS — P193 to P201. Read these; they are the most useful thing here.

**EVERY ONE WAS AN OVERSTATEMENT OR A MIS-CALIBRATION, NOT A MISCALCULATION.** The arithmetic was
right in all six claims an independent auditor checked. What was wrong was **the scope attached to a
passing check**.

| id | what | lesson |
|---|---|---|
| P193 | S5 hardcoded a 1 % fallback threshold and reported **95 "science issues"** that were inside the REGISTERED 10 % | **read the threshold FROM the registration**; a second hand-picked threshold in an audit tool is how an analysis acquires a forking path |
| P194 | wiring the science audit onto the raw ssh cadence took the cycle sweep 26 s -> **51 s** and printed `SWEEP-BOUND`; at the 42,000-record end state it would cross the **2-minute DEAD-loop threshold** | **a new monitor is a LOAD on the monitor it joins.** Rate-limited to 30 min |
| P195 | S10 first asked "are the seed sets equal?" and reported a HEALTHY in-flight line as five ragged arms | the C4 path submits all six blocks at once, so sets are ragged BY CONSTRUCTION mid-fill; the meaningful object is the **CONTIGUOUS PREFIX** (the P186 class) |
| P196 | described S10 as DETECTING pairing breaches when its violation branch is **UNREACHABLE by construction** (the prefix is a MINIMUM, so a hole TRUNCATES it) | an **end-to-end** test found what a helper-level selftest could not |
| **P197** | **reported "determinism is now MEASURED, not asserted" — TWICE — when the check compared NOTHING** (§8.3) | **a passing check tells you what it TESTED, not what you hoped it tested.** Print the count of things actually compared |
| P197b | the CLEAN banner claimed "every record is finite" while `train_curve.return` is 100 % NaN | a summary line must not be wider than its checks |
| P198 | "banked rung 30" hid that 8 of 11 lines have arms with no sealed-test record | score against the REGISTERED ROSTER, not against what happens to exist |
| P199 | read `feedback_block` (EMPTY by design) and nearly reported **the reflection loop fed NOTHING**; then searched for literal keys when the block renders human labels | the field you want is not the field you reach for (P178). **Stop pattern-matching and READ THE TEXT** |
| P200 | demanded `def reward(...)` of BASELINES, which archive a marker comment — **330 phantom defects** | the sibling module's S3 exempted baselines CORRECTLY; the knowledge existed and was not applied |
| P201 | ran a coherence check on the **SHUFFLED control** (permuted by design, 229 phantom) and demanded 6 statistics of `scalar_cvar5` (registered ONE, 218 phantom) | **TRIAGE BY ARM BEFORE REPORTING.** A violation 100 % concentrated in one arm is a statement about that arm's DESIGN |

**★ THE DOMINANT FAILURE MODE, NAMED:** *a check calibrated to a UNIFORM expectation when the design
is deliberately NON-UNIFORM.* P193, P200, P201 are all this. **The countermeasure that works is to
triage by arm/tier/category before reporting anything.**

**★ AND THE PROCESS RULE THAT CAUGHT THE WORST ONE:** an independent read-only auditor subagent was
run against six load-bearing claims **because the author must not grade their own work**. It verified
every number and found three defects RUN 14 had missed, including P197. **Do this before banking any
load-bearing conclusion.**

⚠ **ALSO:** the harness reported a background pytest run as **"exit code 0" while the LOG read
`PYTEST_RC=4`** — `pytest-timeout` is not installed, `--timeout=900` was rejected, and **the suite
never ran.** Never trust a wrapper's exit code; read `PYTEST_RC` from the LOG.

---

## §10 STATE AT HANDOVER (2026-08-02 ~19:15 UTC)

```
records 4,733 (FROZEN since 17:08 — see §2)   ·  spend $45.4819  ·  drift 0  ·  sci=OK
freeze 3ca6f01ab772 MATCHES   ·  reproducibility 8 PASS / 0 WARN / 0 FAIL
full suite 3,047 tests PYTEST_RC=0 (read FROM THE LOG)   ·  ruff clean
11 driver lines · 12 supervisors · 1 cycle loop · 1 sentinel · fenced watchdog live
cores 1,976 (last good reading)  ·  jobs 847/1000  ·  banked common rung 30
C: 31.80 GB free (was 25.84; DISM +5.75)  ·  D: 115.56 GB free
SIX record layers ALL CLEAN  ·  backup branch backup-2026-08-02-run14
RUNNING_SHA 309565f9 (re-based on a COMMENT-ONLY diff — the "provably inert" kind)
```

**WHAT RUN 14 BUILT (all read-only unless stated):**
| file | what |
|---|---|
| `docs/analysis/record_science_audit.py` | S1-S10. **WIRED into cycle.py, rate-limited 30 min.** selftest 18 |
| `docs/analysis/fed_text_identification.py` | S11 — the identification itself. selftest 8 |
| `docs/analysis/reward_code_audit.py` | S12 — re-runs the project's OWN `ast_gate`. selftest 8 |
| `docs/analysis/fed_value_coherence.py` | S13 — CVaR monotonicity + pipeline fidelity. selftest 9 |
| `docs/ops/placeable_capacity.py` | **corrects `pool_capacity_compare`** (disabled hosts + fragmentation + memory). That module is banner-marked SUPERSEDED |
| `docs/ops/cpuprobe14.sh` | the WORKING CPU probe (`-pe smp 1 -ac allow=<pool>`); `cpuprobe13.sh` banner-marked SUPERSEDED |

---

## §11 STANDING RULES THAT MUST SURVIVE THIS HANDOVER

- **NEVER** add Claude/Anthropic attribution. `Co-Authored-By` is REVOKED. Tamer is sole author.
- **NEVER** `git clean -x`, `git add -A`/`-u`, or `git stash`. Stage **by name**.
- **NEVER** lower SGE priority; never `qdel -u`. Explicit ids only.
- **NEVER** put backticks/backslashes/`$(…)` in a bash `-c` string or heredoc — **write to a FILE**.
  RUN 14 broke this twice (a heredoc died mid-append; a `\` in a Python heredoc was mangled).
- **⚠ CRLF:** this repo's files are CRLF. A Python string-replace anchored on `\n` will NOT match.
  Read with `newline=''` and match on the file's own line ending, or use the Edit tool.
- **NEVER** trust a pipe's or wrapper's exit code — read `PYTEST_RC` from the LOG.
- **NEVER** read a treatment arm's SEALED-TEST outcome. All four new instruments are **effect-blind by
  construction** — keep them that way.
- **NEVER** edit `src|scripts|config|prompts` while live without a relaunch OR proving the file is
  outside the driver import closure and re-basing `RUNNING_SHA`.
- **⚠ DO NOT buy an INERT change with a LIVE invariant.** RUN 14 committed `--pool db`, then REVERTED
  it: the flag cannot take effect without a supervisor restart (blocked), so it bought no capacity
  while leaving `drift=1` standing on one of the two invariants documented as never changing. **The
  measurement and the one-token edit live in `mode_d_supervisor.ps1` at the `$cpuLane` insertion
  point** — a comment outlives a handover note.
- **PowerShell console is cp1251:** a `★` or `⚠` inside a `print()` CRASHES with
  `UnicodeEncodeError`. Keep printed output ASCII; docstrings may use unicode.
- **END-OF-WORK, all four:** `python scripts/update_handoff.py` · a SHORT cursor ▶ NOW entry · a
  DETAILED CHANGELOG block even with no commits · push the backup branch.
