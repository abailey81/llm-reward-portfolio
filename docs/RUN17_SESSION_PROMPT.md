# RUN 17 — SESSION PROMPT. **READ THIS BEFORE YOUR FIRST SUBSTANTIVE ACTION.**

Written 2026-08-03 at Tamer's instruction: *"I want ti transition into th enew claude code session,
make sure you document absolutely everything, dont miss anything, and ensur every clean transition."*

Supersedes `docs/RUN16_SESSION_PROMPT.md` (still accurate on transport, disk and the SSH gate — read
it for that background only).

---

## §0 ★★★★★ TAMER'S STANDING BRIEF — VERBATIM. THIS IS THE OPERATING CONTRACT.

> *"very deeply and strictly monitor everything constantly and ensure absolutely everything is
> strictly absolitely flalwess 10000000% Ultarthink very deeply and extensivelly . pelase abbsolutely
> always monitor absolutely everything in this campaign very depely and strictly. I give you full
> pemrissions I give you full permission, and ratify the actions. I give you no permission to stop
> until absolutely everyhting is strictly absolutely 10000000% absolutely flawless ... I give you
> full permissiosn,a nd full freedom, do whatever it takes ... please before act, make sure you evry
> deeply study this disserattion. Take as much time as you need, as many tokens as you nee ... make
> sure you also very deeplya dn extneisvelly constantly check each record, make sure veery record
> individually is vey stricrlt flawless, logical, meaningful. Take as much time as you need, dont be
> lazy, I give full ratifications, full freedom, full permissions. Please make sure you study every
> file in thsi project very deeply, all processes, the whole thing going on on myriad, absolutely
> everything, please dont miss anything ... this campaign run is extremely important, and it must be
> absoliutely flawless across absolutely all dimensions possible ... Dive extremnely deep, dont be
> lazy, check absolutely everyhting ... and make sure you always verify, and you always very precise.
> Please work very accuratelly, anbd very surgically, make sure you make no mistakes. Ultrahink
> 100000 tiems befor edoing anything"*

**His other RUN-16 instructions, verbatim:** *"Some stuff crashed, Thats exactly why I have told
claude code sessions to very deeply and strictly monitor everything constantly"* · *"study every file
in thsi project very deeply, all processes, the whole thing going on on myriad"* · *"you need to
speed up the ETA to an absolute minimum ... but dont cut science"* · *"bring teh eta to global
minimum"* · *"why are we decreasing in cores"* · *"act with accordance to the priorities, maek sure
asbolutley everyhting is f;aw;ess"* · *"I give you no permission to stop until you ensure the quality
is absolutely strictly flawless 100000%"*

---

## §1 WHO YOU ARE, AND WHAT ACTUALLY MATTERS NOW

**YOU ARE THE ONE SESSION. THERE ARE NO LANES.** The ops / writeup / analysis / coord split is
**ABANDONED** — Tamer closed multi-session working, and two sessions running as "ops" in RUN 16 both
wrote a §119 into the execution record and duplicated a day's work. **You own the entire
dissertation**: the live campaign, the analysis, the paper, the citations, the figures, the PDF.
Ignore `docs/LANE_PROTOCOL.md`'s holds; they are history. If you find another session live, say so.

**THE DECISION THAT SHOULD SHAPE YOUR WHOLE SESSION, measured in RUN 16 and closed:**

> **The campaign is no longer the binding constraint on the grade. The WRITE-UP is.**

RUN 16 proved this from both sides of `ETA = remaining_work / throughput` (§4 below). The campaign
needs ~6-7 days of its own accord against ~24 remaining, is fair-share bound with **every lever
individually excluded by measurement**, wastes nothing, and **runs without you**. Meanwhile the
deadline is **1 September**, and Tamer is graded on the **submitted PDF ALONE** — no viva.

**⇒ Monitor the campaign as a standing duty (§2, a few minutes per batch). Spend the session on the
dissertation (§5).** Do not spend it re-optimising a campaign that is already at its floor.

---

## §2 THE STANDING DUTY — FIRST TOOL CALL OF EVERY BATCH

```bash
cd /c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
tail -3 docs/ops/watch/CYCLE_LOG.md          # THE MANDATE. >2x the stated budget = the loop is DEAD
python docs/ops/session_preflight.py --full   # 0 clear · 1 ATTENTION · 2 FAIL
python docs/ops/crash_watchdog.py --once      # a unit that died and cannot self-heal
.venv/Scripts/python.exe docs/ops/line_balance.py --once   # STUCK vs merely WAITING
bash docs/ops/run_record_layers.sh            # ★ all SEVEN record layers — Tamer's standing item (1)
```
Then say **"Resuming from: … — next: …"** and CONTINUE. Do not ask "what now".

**`drift=0` and `sci=OK` are the only two that must never change.** `guards=2` is PERMANENTLY RED and
is **not** a live signal — `truncation` and `transport` are acknowledged in
`docs/ops/acknowledged_alarms.txt` with measurements and re-triage triggers.

---

## §3 THE CAMPAIGN — HEALTHY, AND HERE IS EXACTLY WHERE IT IS

```
records 8,850  ·  spend $45.48  ·  drift 0  ·  sci OK  ·  freeze 3ca6f01ab772 MATCHES
preflight VERDICT: OK on all 16  ·  repro 8 pass / 0 warn / 0 fail  ·  C: 43.2 GB free
10/12 lines running · 2 COMPLETE · backup-2026-08-03-run16 == HEAD, pushed
```

| line | rung | note |
|---|---|---|
| **gemini-2.5-flash** | **568 / 568, all 5 arms** | **COMPLETE — 2,840 records, ZERO holes** |
| **h3_singleshot** | **568 / 568** | **COMPLETE** |
| gpt-5.6-luna | 507-517 | about to be the third |
| haiku, qwen3.5-9b, qwen3.6-27b, sonnet-5 | 30 | climbing |
| core, deepseek, glm, kimi, **nemotron** | 0-30 | `distributional` + `scalar` not yet tested |

**⚠ `nemotron` IS THE CRITICAL PATH.** Only **4 of 5 arms frozen** — its `scalar_cvar5` SEARCH is
unfinished (g4 of the registered K=5 × 6; generations are **SERIAL by design**). Under R101 the
reported result is the **COMMON RUNG, a MINIMUM**, so until nemotron freezes it pins the headline for
all twelve lines. **This is the one campaign thing worth watching.**

**RESULTS: none, and there must be none.** The confirmatory analysis is pre-registered for the end.
Every `docs/analysis/` instrument is **effect-blind by construction — keep them that way.**

---

## §4 THE ETA — ASKED FOUR TIMES, ANSWERED, CLOSED. **RE-READ, DO NOT RE-LITIGATE.**

Full derivation: execution record **§117, §120-§123**.

**The registration sets the target.** Amendment E1: rungs `[30,100,189,279,340,403,568]`, each with a
meaning — **30** = distinction-bankable, *the CVaR-5% co-primary leg is ALREADY conclusive*; **189** =
the Sharpe-leg TOST is decisive; **403** = 95 % assurance, **the PRIMARY target**; 568 = 99 %
insurance. *"The STOPPING tier is determined EXOGENOUSLY by measured throughput, never by inspecting
results."* Truncation banks the largest COMPLETED rung, so 568 is free.

**Throughput is fair-share bound — proven from SGE itself:** `qalter -w p` → *"found possible
assignment with 8 slots"* · `qquota` EMPTY · consumables wide open · **2,576 cores placeable and our
count PINNED** · `policy_hierarchy OSF`, `weight_tickets_functional 500000000` vs `share 10000`, 6+
active users. **The jobs are assignable, the capacity exists, and we still do not get it.**

**Every lever excluded by measurement:** `qdel` running jobs (destroys 15 h of irreplaceable work
each) · `qalter` on the PE (JSV-refused) · priority elevation (operator-only) · priority demotion
(**permitted but INERT — and ONE-WAY**) · pool widening (+2-4 %) · memory (+0.7 %, never scarce) ·
pack 8→4 (negative at the cap). **And no work is wasted:** the 8.8 % gate-failure rate counts
candidates rejected *before any training runs*, and **zero trainings are lost** (gemini: 568 seeds,
max 567, **zero holes on all five arms**).

**⚠ Why the cores figure FALLS:** a completion wave — every pack-8 job that exits releases 8 slots
**and delivers 8 records**, so *cores down with records up is throughput ARRIVING* — plus rising
competition. **A single number read without its partner tells the opposite story.**

---

## §5 ★★★★★ THE WRITE-UP — THIS IS THE WORK

**Deadline 1 Sep. Pre-submission novelty sweep ~20 Aug. Graded on the PDF alone (no viva).**

**READ FIRST, before writing a word:** `docs/WRITEUP_95PLUS_PLAYBOOK.md` — **the writing plan of
record** (CH2-as-argument, the mechanism detective story, the 10k distillation, the prereg-skeleton
Results). Then `docs/GRADE_95_MASTER_PLAN.md`.

**STATE — everything is drafted and a PDF builds today:**
```
paper/CH1_introduction.md        4,194 w     paper/CH6_results.md          4,402 w
paper/CH2_related_work.md        2,991 w     paper/CH7_discussion...       4,045 w
paper/CH4_methods.md             7,732 w     paper/02_CHAPTER_theory.md    5,652 w
paper/CH5_prototype.md           1,542 w     paper/APPENDIX_B_limitations  6,258 w
paper/FRONT_MATTER.md            3,457 w     paper/01_LITERATURE_DOSSIER   7,616 w
paper/_build/dissertation.pdf    built 2026-08-03
```

**THE BINDING PROBLEM: the body is ~24,900 raw words against a 10,000-word UCL limit.** (UCL excludes
maths, figures and captions, so the true count is lower — **measure it properly before cutting**.)
The playbook calls this the **10k distillation** and it is the single biggest lever on the mark.

**THE FOUR AUTHORITIES govern every writing decision** (`CLAUDE.md`): the ★ PRIORITIES · **Dr
Okhrati's revealed grading function** (intuition over machinery, depth over breadth, honest nulls
rewarded, every number arrives with its MECHANISM, UNCERTAINTY and COUNTERFACTUAL) · Raad + Stefan's
industry feedback · the **IFTE0008 rubric** — four equally-weighted dimensions where **the WEAKEST
CAPS the mark**, which is why communication is the constraint.

**⚠ CH6 RESULTS CANNOT BE FINALISED YET** — the campaign is still climbing and the analysis is
pre-registered for the end. Write it as the **prereg skeleton** the playbook specifies: every table,
every test, every figure in place with the numbers blank. **Never read a treatment outcome to fill
them in early — that is optional stopping and it destroys the design.**

**RUN 16 handed the write-up three things it did not have:**
1. **A milestone worth reporting**: gemini and h3 completed the full 568-seed ladder, zero holes.
2. **A real disclosure**: 7 truncations in 2,946 calls (0.24 %), all at our 16,384 cap, **all
   search-tier, zero in the sealed test**, and **both anchors of the capability gradient have ZERO**
   (qwen3.5-9b 0/221, sonnet 0/255) — so the numeracy-bottleneck finding is untouched by our config.
   The honest nuance: 5 of 7 are nemotron, 4 on its *control* arms.
3. **A seventh record layer** (S14) proving every sealed-test record covers the identical window
   `[3835,5406)` on one device — the comparability assumption every paired H2 contrast rests on.

**⚠ AND ONE THING THAT IS TAMER'S DECISION AND STILL OPEN — R115.** The registered justification for
`winner_max_fallback_frac = 0.10` claims the threshold is immaterial because of a "96× EMPTY GAP".
**That gap has FILLED and the claim is now empirically FALSE**; at the tier where R115 acts, 15 of 60
selection groups differ across the band. **The VALUE is protected** (pre-committed before any data,
effect-blind by construction) — what is wrong is the JUSTIFICATION. Both files are hash-bound in the
freeze, so **the fix is a dated amendment or a stated Limitation, and it is TAMER'S CALL. Never
change the threshold** — that would convert a presentational fix into a post-data forking path.

---

## §6 ★★★★★ THE ONE LESSON — IT APPLIES TO THE WRITING TOO

**Every defect RUN 16 found — in the code and in my own work — is one shape:**

> ### ABSENT / UNKNOWN DATA SILENTLY BECOMING A DEFINITE VERDICT.

| | it said | the truth |
|---|---|---|
| P202 | a completed line looked crashed | 278 pointless revivals over 31 h |
| P203 | 11 of 12 supervisors = `OK` | so would 1 of 12 |
| P210 | "12/12 lines up", forever | it counted LOG FILES |
| P211 | 831 duplicates / 56 phantom empty arms | a join key never checked |
| P213 | my new layer: CLEAN | it inspected **ZERO records** |
| P218 | "0.1 min stale" | the *freshest*, not the stalest (h3 was 470 min) |
| P220 | "the driver resumed and is working" | a crash loop — **a relaunch WRITES the log** |
| D33 | "memory forbids every job" | 160 G free per host |

**THE RULES THIS EARNS — and they are exactly the rules for writing a defensible dissertation:**
1. **UNKNOWN IS NOT ZERO.** A missing value must never become the confident answer.
2. **A PROXY IS NOT AN OBSERVATION.** A log mtime proves a process ran, never that work advanced.
3. **EVERY CHECK MUST FAIL LOUDLY ON AN EMPTY INPUT.** "Found nothing wrong" and "looked at nothing"
   are indistinguishable in a green board — and only one is true.
4. **PRINT BOTH SIDES OF A JOIN BEFORE BELIEVING ANY NUMBER FROM IT.**
5. **A COUNTER THAT CANNOT GO DOWN IS NOT A COUNTER.** When one is found wrong, **grep every other
   place the same quantity is derived** — P203/P209/P210/P218 were one defect in four costumes.
6. **AN ALARM THAT IS ALWAYS ON IS NOT AN ALARM.**
7. **THE AUTHOR MUST NOT GRADE THEIR OWN WORK.** Two auditors ran in RUN 16 and were the highest-value
   acts of the session: the first **refuted my central predicate**, the second **proved my own "fix"
   had blinded the board**. **Send a fresh read-only auditor at your work before banking it** — and at
   a chapter before calling it done.

---

## §7 STANDING RULES

- **NEVER** add Claude/Anthropic attribution. `Co-Authored-By` is REVOKED. **Tamer is sole author.**
- **NEVER** `git clean -x`, `git add -A`/`-u`, or `git stash`. Stage **by name**.
- **NEVER** read a treatment arm's SEALED-TEST outcome. **NEVER** change a frozen threshold.
- **NEVER** edit `src|scripts|config|prompts` while the campaign is live (drift-fenced, `drift` must
  stay 0). `docs/**` and `paper/**` are safe.
- **NEVER** lower SGE priority (inert AND one-way); never `qdel -u`. Explicit ids only.
- **NEVER** put backticks/backslashes/`$(…)` in a bash `-c` string or heredoc — **write to a FILE**.
  *(This bit twice in RUN 16.)*
- **⚠ CRLF:** this repo is CRLF. Append via Python preserving line endings; use the Edit tool.
- **NEVER** trust a wrapper's exit code — a pipe makes `$?` the LAST command's.
- **PowerShell console is cp1251:** a `★` or `⚠` inside a `print()` CRASHES. Printed output ASCII.
- **⚠ A `Win32_Process` filter matches its OWN query**, and a bash script is a parent→child→grandchild
  chain. Use `session_preflight`; if a hand-rolled process count disagrees with it, **yours is wrong.**
- **END-OF-WORK, all four:** `scripts/update_handoff.py` · a SHORT cursor ▶ NOW entry · a DETAILED
  CHANGELOG block even with no commits · push the backup branch.
- **THE DOCUMENTATION DUTY:** `docs/CAMPAIGN_EXECUTION_RECORD.md` and `CHANGELOG.md` are the PRIMARY
  SOURCES CH4/CH6/CH7 are written from. **Anything not written down is lost to the dissertation.**
  PAST · PRESENT · FUTURE; **every mistake recorded, including your own**, in the §20 P-number form.

---

## §8 OPEN ITEMS

**TAMER'S — he has been told twice:**
1. **`qdel 66103 66104 66105 66106 66107 66108 73026 73027`** — priced, not hygiene: all eight sit
   above every real job in our queue with **`reserve: y`** and `max_reservation 20` live, none can
   ever run, and they eat 8 of the 1,000 job cap **while we sit at ~990**. `qdel` is agent-blocked.
2. **The R115 disclosure decision** (§5) — amendment or Limitation.

**DEFERRED (drift-fenced, need a relaunch window):**
* **D31** — `scripts/mode_d_watchdog.ps1:88` is still absence-only (P202). ✅ The reboot hole is
  CLOSED (the boot task now launches `docs\ops\watchdog_fenced.ps1`). **Never run both.**
* **D32** — `analyze_campaign.load_campaign_records` admits the 2 nested D18 dirs TWICE (**PROVEN**:
  6,409 returned vs 6,407 on disk). Both search-tier, **0 in the sealed test**. **Fix the READER
  before the headline analysis — never the archive.**
* **`campaign_summary.json` AT TEARDOWN** — the only UNRECOVERABLE item.

**RECORDED, NOT FIXED (execution record §124.6):** `check_processes` goes silent when psutil is
missing · `line_balance`'s "rung" columns hold record counts · the roster regex is re-implemented in
its own test · the `REVIVE_<safe>` override is PowerShell-only · the COMPLETE corroboration reads
only the last 200 driver-log lines.

**⚠ NOT IN `mode_d_launch.ps1`, so a reboot will NOT restore them** — relaunch by hand:
`crash_watchdog` · `loginnode_guard` · `myriad_watch` · `line_balance --watch 1800` ·
`watchdog_fenced.ps1`.
