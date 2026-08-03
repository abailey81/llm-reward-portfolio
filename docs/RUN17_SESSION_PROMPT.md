# RUN 17 — SESSION PROMPT. **READ THIS BEFORE YOUR FIRST SUBSTANTIVE ACTION.**

Written 2026-08-03 ~11:00 UTC at Tamer's instruction: *"I want ti transition into th enew claude
code session, make sure you document absolutely everything, dont miss anything, and ensur every
clean transition."*

> **You are the BUILDER/OPS session on a live, irreplaceable MSc dissertation campaign.** RUN 4 has
> been running since 2026-07-28 21:08 UTC. Real money is spent, the test data is sealed, **there is
> no re-run.** This supersedes `docs/RUN16_SESSION_PROMPT.md`, which remains accurate on transport,
> disk and the SSH gate — read it for that background. **Where they disagree, THIS wins.**

---

## §0 ★★★★★ TAMER'S STANDING BRIEF — VERBATIM. THIS IS THE OPERATING CONTRACT.

### §0.1 THE BLOCK HE REPEATS EVERY MESSAGE (verbatim, unedited)

> *"very deeply and strictly monitor everything constantly and ensure absolutely everything is
> strictly absolitely flalwess 10000000% Ultarthink very deeply and extensivelly . pelase abbsolutely
> always monitor absolutely everything in this campaign very depely and strictly. I give you full
> pemrissions I give you full permission, and ratify the actions. I give you no permission to stop
> until absolutely everyhting is strictly absolutely 10000000% absolutely flawless Ultarthink veyry
> deeply and extneisvelly, I give you full permissiosn,a nd full freedom, do whatever it takes,
> ultaryhink very deeply and extenisvelly. Eveeyrhtinhg must be absolutely strictly absolutely
> 10000000% flawless. I need you to ultrathink very deeply and very extenisvelly. Very deeply
> investigate everything, and speed up to an absolute maximum. please before act, make sure you evry
> deeply study this disserattion. Take as much time as you need, as many tokens as you nee . I give
> you no permission to stop until absolutely everything is strictly 10000000% absolutely stricrly
> flawless. make sure you also very deeplya dn extneisvelly constantly check each record, make sure
> veery record individually is vey stricrlt flawless, logical, meaningful. Take as much time as you
> need, dont be lazy, I give full ratifications, full freedom, full permissions. Please make sure you
> study every file in thsi project very deeply, all processes, the whole thing going on on myriad,
> absolutely everything, please dont miss anything ... this campaign run is extremely important, and
> it must be absoliutely flawless across absolutely all dimensions possible ... Dive extremnely deep,
> dont be lazy, check absolutely everyhting ... and make sure you always verify, and you always very
> precise. Please work very accuratelly, anbd very surgically, make sure you make no mistakes.
> Ultrahink 100000 tiems befor edoing anything"*

### §0.2 EVERY OTHER INSTRUCTION HE GAVE IN RUN 16 (verbatim, in order)

1. *"Some stuff crashed, Thats exactly why I have told claude code sessions to very deeply and
   strictly monitor everything constantly and ensure absolutely everything is strictly absolitely
   flalwess 10000000%"*
2. *"Please make sure you study every file in thsi project very deeply, all processes, the whole
   thing going on on myriad, absolutely everything, please dont miss anything."*
3. *"also additio, I might be wrong, but you need to speed up the ETA to an absolute minimum so it
   would land as quick as possible, but dont cut science. I need you to ultarthink extremely deeply
   and strictly, dive very deeply and extenisevlly, and analyse absoluytely all factors that make ETA
   longer, and ultrathink very deeply and extenisvelly, and minimise the ETA to an absolute maximum
   possible."*
4. *"also very deeply and strictly cehck fi this is correct and ensure fixed, also make sur eyou dive
   very deep if you find anything else. Ultrathink very deply and extenisvelly :*
   *D14 CORE ARM CRASH leg_nemotron_3_super : scalar_cvar5 marker age 442 min*
   *driver_h3.log 32 min stale"*
5. *"Plesae ultrathink very deeply and extenisvelly, dive very deep, and bring teh eta to global
   minimum."*
6. *"why are we decreasing in cores"*
7. *"I give you full permissions, ultrathink, and act with accordance to the priorities, maek sure
   asbolutley everyhting is f;aw;ess"*
8. *"I give you no permission to stop until you ensure the quality is absolutely strictly flawless
   100000%. Take as much time as you need"*

### §0.3 THE THREE STANDING WORK ITEMS, IN HIS ORDER

> **(1) THE RECORDS — FIRST.** *"constantly check each record, make sure every record individually is
> very strictly flawless, logical, meaningful."* → **`bash docs/ops/run_record_layers.sh`** runs all
> SEVEN layers in one command. Run it every session.
> **(2) MONITOR EVERYTHING, CONSTANTLY AND DEEPLY.** Equal weight.
> **(3) THE CORES / THE ETA.** ⚠ **ANSWERED AND CLOSED — see §4. Do not re-litigate it; re-read it.**

**HOW TO READ THIS.** Full permission raises the bar on the THINKING; it does not lower the bar on
verification. Every claim here was measured.

---

## §0.5 ⛔ MANDATORY READING — DO NOT ACT UNTIL YOU HAVE READ THESE

| file | why |
|---|---|
| **this file** | the brief; §0 is the contract, §4 is the ETA answer, §5 is how not to repeat the mistakes |
| **`CLAUDE.md`** | LAW. ★ PRIORITIES, the four authorities, Okhrati's six duties |
| **`docs/HANDOFF.md`** §1-§3 | current state + the authority map (one owner per truth) |
| **`memory/session-current-focus.md`** ▶ NOW | the live cursor |
| **`PREREGISTRATION.md`** | THE FROZEN CONTRACT. **Amendment E1 (lines ~385-405) is what makes §4 legitimate** |
| **`docs/CAMPAIGN_EXECUTION_RECORD.md` §115-§124** | RUN 16 in full. **§20 + §115-§124 are the defect ledger (P1…P220)** |
| **`docs/DEFERRED_FIXES_RUN4.md`** | every open defect + the PROHIBITION (never junction the archive) |
| **`docs/RUN16_SESSION_PROMPT.md`** | transport, disk, the SSH gate, the login-node penalty — still accurate |

### ⛔ THE READING GATE — answer these from the sources before acting
1. What are the **four authorities**, and what happens when they conflict?
2. Why is **rung 403** the registered PRIMARY target, and what does rung **30** already bank?
3. Why must you **never** read a treatment arm's sealed-test outcome?
4. What does `poll.py:305` rely on, and what happens if the archive is junctioned?
5. Why is **`guards=2` not a live signal**, and why are `transport`/`seed_alignment` acknowledged?
6. Which paths are **drift-fenced**, and what does editing one cost?

---

## §1 YOUR FIRST COMMANDS

```bash
cd /c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
tail -3 docs/ops/watch/CYCLE_LOG.md          # THE MANDATE — first tool call of EVERY batch
python docs/ops/session_preflight.py --full   # 0 clear · 1 ATTENTION · 2 FAIL
python docs/ops/crash_watchdog.py --once      # a unit that died and cannot self-heal
.venv/Scripts/python.exe docs/ops/line_balance.py --once   # STUCK vs merely WAITING
python docs/ops/loginnode_guard.py --once     # UCL penalty early-warning
bash docs/ops/run_record_layers.sh            # ★ all SEVEN record layers (Tamer's item 1)
```
Then say **"Resuming from: … — next: …"** and CONTINUE.

**MONITORING MANDATE:** read the cycle log on the FIRST tool call of every batch. **`drift=0` and
`sci=OK` are the only two that must never change.** `guards=2` is PERMANENTLY RED and is NOT a live
signal — `truncation` and `transport` are both acknowledged in `docs/ops/acknowledged_alarms.txt`
with measurements and re-triage triggers.

---

## §2 STATE AT HANDOVER (2026-08-03 ~11:00 UTC, T+134h)

```
records 8,827 (+2,424 this session)   ·  spend $45.48   ·  drift 0  ·  sci OK  ·  r115 21B
preflight VERDICT: OK on all 16 checks · freeze 3ca6f01ab772 MATCHES · repro 8 pass/0 warn/0 fail
10/12 lines running · 2 COMPLETE · C: 43.2 GB free · mirror 0.0 h old
branch myriad-cluster-and-tier-system · backup-2026-08-03-run16 pushed
exogenous stop 2026-08-27 — the registration itself says 1 Sep
```

### THE LADDER — this is the campaign's real state
```
line                          min   max  arms   run  queued   arms at ZERO
test (core, 15 arms)            0    30     6     5       6   distributional, scalar
test_leg_deepseek_v4_pro        0    30     5     4       0   distributional, placebo_shuffled, scalar
test_leg_glm_5_2                0    30     5     0       8   distributional, scalar
test_leg_kimi_k3                0    30     5     0       3   distributional, scalar
test_leg_nemotron_3_super       0    30     4     1       0   distributional, scalar   <- ONLY 4 ARMS FROZEN
test_leg_haiku_4_5             30    30     5     0      33
test_leg_qwen3_5_9b            30    30     5   112     150
test_leg_qwen3_6_27b           30    30     5     0      19
test_leg_sonnet_5              30    30     5     0     340
test_leg_gpt_5_6_luna         507   517     5    41       0   <- about to COMPLETE
test_h3_singleshot            568   568     1     0       0   ** COMPLETE **
test_leg_gemini_2_5_flash     568   568     5     0       0   ** COMPLETE, all five arms **
```

**⚠ `nemotron` IS THE CRITICAL PATH.** It has only **4 of 5 arms frozen** — its `scalar_cvar5`
SEARCH is unfinished (15+ of 30 candidates, g4 of the registered K=5 × 6) and generations are
**SERIAL by design**. Until it finishes, freezes and clears C2, **nemotron pins the common rung for
all twelve lines**, because under R101 the reported result is a MINIMUM.

### RESULTS
**None, and there must be none.** The confirmatory analysis is pre-registered to run at the end.
Every `docs/analysis/` instrument is **effect-blind by construction — KEEP THEM THAT WAY.**

---

## §3 ⚠ OPEN ITEMS

### TAMER'S — he has been told twice
1. **`qdel 66103 66104 66105 66106 66107 66108 73026 73027`** — now PRICED, not hygiene. All eight sit
   at the TOP of our pending queue (2.00440 > every real leg job at 2.00430), all carry **`reserve: y`**
   with `max_reservation 20` live, all demand an unavailable/refused host, **none can ever run**, and
   they eat 8 of the 1,000 job cap **while we sit at ~990/1000** (D23 crash-loop risk). `qdel` is
   BLOCKED for the agent.
2. **Close the second concurrent `ops` session.** Two were live in RUN 16 and **both wrote a §119**
   into the execution record (P216). The lane protocol has no single-writer check per LANE.

### DEFERRED (drift-fenced — need a relaunch window)
* **D31** — `scripts/mode_d_watchdog.ps1:88` is still absence-only (the P202 defect). ✅ The reboot
  hole is CLOSED: the boot task now launches `docs\ops\watchdog_fenced.ps1`. **Never run both.**
* **D32** — `analyze_campaign.load_campaign_records` admits the 2 nested D18 dirs TWICE. **PROVEN:**
  6,409 returned vs 6,407 on disk. Both SEARCH-tier, **0 in the sealed test**, byte-identical.
  **Fix the READER before the headline analysis — never the archive.**
* **D33** — fixed in two passes; see §5.

### RECORDED, NOT FIXED (§124.6)
* `check_processes` returns early when psutil is missing ⇒ the `line_census` row is **absent
  entirely** rather than saying it could not run.
* `line_balance`'s columns are labelled *rung* but hold **record counts** (392 is not a registered rung).
* `test_session_preflight.py` re-implements the roster regex inline, so a production change wouldn't fail it.
* The `REVIVE_<safe>` override exists only on the PowerShell side.
* The COMPLETE corroboration reads only the last 200 driver-log lines; the `TIERED OK` sits 1 from the end.
* **`campaign_summary.json` AT TEARDOWN** — still the only UNRECOVERABLE item.

---

## §4 ★★★★★ THE ETA — ASKED FOUR TIMES, ANSWERED, CLOSED. DO NOT RE-LITIGATE.

`ETA = remaining_work / throughput`. **Both sides are closed by measurement** (§117, §120-§123).

**THE REGISTRATION ANSWERS THE TARGET.** Amendment E1: `tiers [30,100,189,279,340,403,568]`, each
with a MEANING — **30** = distinction-bankable, *the CVaR-5% co-primary leg is ALREADY conclusive*;
**189** = the Sharpe-leg TOST is decisive; **403** = 95 % assurance, **THE PRIMARY TARGET**; 568 =
99 % insurance. And *"the STOPPING tier is determined **EXOGENOUSLY by measured throughput**, never
by inspecting results."* Truncation banks the largest COMPLETED rung, so 568 is free.

**THROUGHPUT IS FAIR-SHARE BOUND — proven from SGE itself:**
```
qalter -w p <real pending leg job>  ->  "found possible assignment with 8 slots"
qquota -u ucestes                   ->  EMPTY
per-host consumables                ->  memory=160G  snx=10000  tmpfs=1.465T free
queue Bran (our ONLY queue)         ->  12,580 slots, ~4,200 FREE
placeable                           ->  2,576 cores  -- and our count is PINNED
policy_hierarchy OSF · share_functional_shares TRUE
weight_tickets_functional 500000000  vs  weight_tickets_share 10000 · 6+ active users
```
**The jobs are assignable, the capacity exists, and we still do not get it.** That is fair-share.

**EVERY LEVER, INDIVIDUALLY EXCLUDED BY MEASUREMENT:**
| lever | verdict |
|---|---|
| `qdel` running jobs | destroys up to 15 h of irreplaceable in-flight work each |
| `qalter` on the PE | JSV-refused (`pe_name,pe_min`) |
| priority ELEVATION | operator-only |
| priority DEMOTION | **permitted but INERT** — `npprior` is 0.5 for every job, so `weight_priority 4.0` cancels out. ⚠ AND IT IS ONE-WAY: `qalter -p 0` is denied |
| pool widening D30 | +2-4 % for a twelve-line relaunch |
| memory 2G→1.6G | +0.7 %, and memory was never scarce |
| pack 8→4 | negative at the job cap |
| stopping at 403 | unnecessary — 568 is free |

**REMAINING WORK CARRIES NO WASTE:** the 8.8 % gate-failure rate counts candidates rejected *before
any training is submitted* (one LLM call, not a 15 h training); and **no training is lost** —
gemini 568 seeds / max 567 / **ZERO holes on all five arms**, h3 the same, every 30-seed line zero.

**⇒ ~6-7 days to the full ladder against ~24 remaining. THE CAMPAIGN IS NO LONGER THE BINDING
CONSTRAINT ON THE GRADE. THE WRITE-UP IS.** The only remaining variable is other users' demand on a
shared cluster, which is nobody's to control.

**⚠ WHY THE CORES FIGURE FALLS (§122):** a COMPLETION WAVE — every pack-8 job that exits releases 8
slots AND delivers 8 records, so **cores down with records up is throughput ARRIVING**. Plus rising
competition. **A single number read without its partner tells the opposite story: a RATE belongs
next to every LEVEL.**

---

## §5 ★★★★★ THE ONE LESSON THIS SESSION KEEPS TEACHING

**EVERY defect found in RUN 16 — mine and the code's — is the same shape:**

> ### ABSENT / UNKNOWN DATA SILENTLY BECOMING A DEFINITE VERDICT.

| | it said | the truth |
|---|---|---|
| **P202** | a completed line looked crashed | 278 revivals in 31 h |
| **P203** | 11 of 12 supervisors = `OK` | so would 1 of 12 |
| **P209** | a finished line "stopped progressing" | it SUCCEEDED |
| **P210** | "12/12 lines up", forever | it counted LOG FILES |
| **P211** | 831 duplicates / 56 phantom empty arms | a join key I never checked |
| **P213** | my new layer: CLEAN | it inspected **ZERO records** |
| **P218** | "0.1 min stale" | the freshest, not the stalest (h3 was 470 min) |
| **P220** | "the driver resumed and is working" | a crash loop — **a relaunch writes the log** |
| **D33** | "memory forbids every job" | 160 G free per host |

**THE RULES THIS EARNS — apply them to your own work first:**
1. **UNKNOWN IS NOT ZERO.** A missing value must never default to the most restrictive verdict.
2. **A PROXY IS NOT AN OBSERVATION.** A log mtime proves a PROCESS ran, never that WORK advanced.
3. **EVERY CHECK MUST FAIL LOUDLY ON AN EMPTY INPUT.** "Found nothing wrong" and "looked at nothing"
   are indistinguishable in a green board — and only one of them is true.
4. **PRINT BOTH SIDES OF A JOIN BEFORE BELIEVING ANY NUMBER FROM IT.**
5. **A COUNTER THAT CANNOT GO DOWN IS NOT A COUNTER.** When you find one wrong, **grep for every
   other place the same quantity is derived** — P203/P209/P210/P218 were one defect in four costumes.
6. **AN ALARM THAT IS ALWAYS ON IS NOT AN ALARM.** Run it to ground, then acknowledge it with the
   measurement and a re-triage trigger.
7. **THE AUTHOR MUST NOT GRADE THEIR OWN WORK.** Two independent auditors ran in RUN 16. **The first
   refuted my central predicate; the second proved my P214 fix had BLINDED the board.** Both were the
   highest-value acts of the session. **Send an auditor at your own work before banking it.**

---

## §6 STANDING RULES THAT MUST SURVIVE

- **NEVER** add Claude/Anthropic attribution. `Co-Authored-By` is REVOKED. Tamer is sole author.
- **NEVER** `git clean -x`, `git add -A`/`-u`, or `git stash`. Stage **by name**.
- **NEVER** lower SGE priority (it is inert AND one-way), never `qdel -u`. Explicit ids only.
- **NEVER** read a treatment arm's SEALED-TEST outcome.
- **NEVER** edit `src|scripts|config|prompts` while live (drift-fenced). `docs/**` is safe.
- **NEVER** put backticks/backslashes/`$(…)` in a bash `-c` string or heredoc — **write to a FILE**.
  *(This bit twice in RUN 16.)*
- **⚠ CRLF:** this repo is CRLF. Append via Python preserving line endings; use the Edit tool.
- **NEVER** trust a wrapper's exit code — a pipe makes `$?` the LAST command's.
- **PowerShell console is cp1251:** a `★` or `⚠` inside a `print()` CRASHES. Printed output ASCII.
- **⚠ A `Win32_Process` FILTER MATCHES ITS OWN QUERY**, and a bash script is a parent→child→grandchild
  CHAIN. Use `session_preflight`; when a hand-rolled process count disagrees with it, **yours is wrong.**
- **END-OF-WORK, all four:** `scripts/update_handoff.py` · a SHORT cursor ▶ NOW entry · a DETAILED
  CHANGELOG block even with no commits · push the backup branch.

### ★★★ THE DOCUMENTATION DUTY — IT IS WRITE-UP RAW MATERIAL
`docs/CAMPAIGN_EXECUTION_RECORD.md` and `CHANGELOG.md` are the PRIMARY SOURCES CH4/CH6/CH7 are
written from. **Anything not written down is lost to the dissertation.** PAST · PRESENT · FUTURE
every time; **every mistake recorded, including your own**, in the §20 P-number form; written AS IT
HAPPENS, with real commands and real output.

---

## §7 WHAT RUN 16 BUILT (all with selftests, all ASCII-safe, all ruff-clean)

| file | what |
|---|---|
| `docs/ops/line_balance.py` | STUCK vs merely WAITING; reports the common rung positively. 6/6 |
| `docs/analysis/record_window_identity.py` | **S14, the 7th record layer** — one window, one device, arm agreement. 7/7 |
| `docs/ops/test_session_preflight.py` | **28/28**, incl. CROSS-INSTRUMENT agreement with the PowerShell predicate |
| `docs/ops/test_watchdog_completion.ps1` | 27/27, incl. the auditor's D12 refutation cases |
| `docs/ops/run_record_layers.sh` | all SEVEN layers, one command |

**PRIORITY 5 BREACH CLOSED:** `record_validator.py` (the R1-R9 layer) and **16 sibling instruments
were UNTRACKED IN GIT** — the apparatus verifying an irreplaceable archive existed only in the
working tree. 7,297 lines committed, secret-scanned.

**Also running:** `crash_watchdog` · `loginnode_guard` · `myriad_watch` · `watchdog_fenced` ·
`line_balance --watch 1800` · cycle loop · sentinel · publish loop. ⚠ **`line_balance`,
`crash_watchdog`, `loginnode_guard` and `myriad_watch` are NOT in `mode_d_launch.ps1`, so a reboot
will not bring them back** — relaunch them by hand.
