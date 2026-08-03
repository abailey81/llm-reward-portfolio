# RUN 16 — SESSION PROMPT. **READ THIS BEFORE YOUR FIRST SUBSTANTIVE ACTION.**

Written 2026-08-03 ~02:00 UTC at Tamer's instruction: *"I want to transition to another claude code
session. Ensure you document absolutely everyhting, write a prompt, and ensure absolutely strictly
flawless transition. make sure you dont forget also to include the first first prompt I gave you, and
other prompts relevant to it as well. make sure it has a comprehensive undertsanding of the project,
and has zero gaps."*

> **You are the BUILDER/OPS session on a live, irreplaceable MSc dissertation campaign.** RUN 4 has
> been running since 2026-07-28 21:08 UTC. Real money is spent, the test data is sealed, **there is
> no re-run.** This supersedes `docs/RUN15_SESSION_PROMPT.md`; where they disagree, **this wins** —
> RUN 15 contained several claims this session measured and found FALSE (listed in §9).

---

## §0 ★★★★★ TAMER'S STANDING BRIEF — VERBATIM. THIS IS THE OPERATING CONTRACT.

### §0.1 THE BLOCK HE REPEATS EVERY MESSAGE (verbatim, unedited)

> *"I give you full permission, and ratify the actions. I give you no permission to stop until
> absolutely everyhting is strictly absolutely 10000000% absolutely flawless Ultarthink veyry deeply
> and extneisvelly, I give you full permissiosn,a nd full freedom, do whatever it takes, ultaryhink
> very deeply and extenisvelly. Eveeyrhtinhg must be absolutely strictly absolutely 10000000%
> flawless. I need you to ultrathink very deeply and very extenisvelly. Very deeply investigate
> everything, and speed up to an absolute maximum. please before act, make sure you evry deeply
> study this disserattion. Take as much time as you need, as many tokens as you nee. I give you no
> permission to stop until absolutely everything is strictly 10000000% absolutely stricrly flawless.
> make sure you also very deeplya dn extneisvelly constantly check each record, make sure veery
> record individually is vey stricrlt flawless, logical, meaningful. Take as much time as you need,
> dont be lazy"*

### §0.2 HIS FIRST PROMPT OF THIS SESSION (verbatim — he asked explicitly that it be carried over)

> *"I give you full permissiposn t move the stuff from teh disk and etc, there must be no ceiling, we
> must have full ladder, also ultrathink veyr deeply and extneisvelly, and fix the myriad issue, try
> extenisvelly, but please make sure you act very accuratelly and surgically and with regards to
> otehrs, I ratify, ultrathink and proceed"* — followed by the §0.1 block.

### §0.3 EVERY OTHER INSTRUCTION HE GAVE THIS SESSION (verbatim, in order)

1. *"add additional task for your plan, if you dont manage to suceed, try connecting again every 20
   minutes, teh issues could be possible fixed in some time"*
2. *"remove the incident report for now"*
3. *"I am back, check myriad again"*
4. *"just use local disk d no? It has a lot of space"* + *"Yes, do it, make sure everyhting is
   strictly flawless, and we have full ladder"*
5. *"I give you my full permissions, and fully ratify, please use my ucl password: <REDACTED>"*
   ⚠ **HE MUST ROTATE THAT PASSWORD — it was posted twice in the RUN 15 transcript.** It was used
   ONLY for the gateway diagnosis and was never written to any file.
6. *"move some additional stuff from c to d just in case"*
7. *"Dont stop until teh ceiling issue is gone"*
8. *"try one last time in a very smart manner before drafting an email"* → *"wait stop, let me
   restart teh vpn before the very last attempt"* → *"done"*
9. *"could you please change the run4 live status updates from every 5 minutes to every 1 minute"*
   then *"also change it to report every 1 minute"*
10. *"Please make sure yiu handke violations, I dont want to receive another penalty"* +
    *"please ultrathink very deeplya dn extenisvelly, very deeply analyse that email, I dont want to
    risk it and receive anothe rpenalty"*
11. *"Please make you ultarthink very deeply and extenisvelly, and build and extremely advacned and
    precise system that ensures that would never happen again. I give you full freeedom, and full
    permissions, and ratify"*
12. *"Do it on my behalf, i ratify"* (activating the SSH gate on the LIVE path)
13. *"Why run4_status.md is not working again? fix"*
14. *"di you think relauncg worth it, or we would be better off just leaving everything as it is?"*
15. *"so in campaign, where are we currently at, whats going on now, where in the ladder are we? what
    are we doing right now? What are the results? I need to nw everything"*
16. *"Creashed? Thats exactly why I have told you to very deeply and strictly monitor everything
    constantly and ensure absolutely everything is strictly absolitely flalwess... pelase
    abbsolutely always monitor absolutely everything in this campaign very depely and strictly"*

### §0.4 THE TWO STANDING WORK ITEMS, IN HIS ORDER (he stated the ordering explicitly)

> **(1) THE RECORDS — FIRST.** *"constantly check each record, make sure every record individually is
> very strictly flawless, logical, meaningful... no science issue and etc."*
> **(2) THE CORES — SECOND.** *"only after you finish with this... we are not even at 2k cores...
> speed up to an absolute maximum."*
> **(3) ADDED THIS SESSION — MONITOR EVERYTHING, CONSTANTLY AND DEEPLY.** Raised after a crashed
> pipeline went unnoticed for hours (§4). Treat it as a standing duty of equal weight.

**HOW TO READ THIS.** Full permission raises the bar on the THINKING; it does not lower the bar on
verification. Every claim in this document was measured. Where RUN 15 was wrong, it says so.

---

## §1 YOUR FIRST COMMANDS

```bash
cd /c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
tail -3 docs/ops/watch/CYCLE_LOG.md              # THE MANDATE — first tool call of EVERY batch
python docs/ops/crash_watchdog.py --once         # ★ NEW — a unit that died and cannot self-heal
python docs/ops/loginnode_guard.py --once        # ★ NEW — are we near a UCL usage penalty
python docs/ops/session_preflight.py --full      # 0 clear · 1 ATTENTION · 2 FAIL
ssh -o BatchMode=yes myriad "hostname"           # transport (goes through the SSH GATE now)
```

Then say **"Resuming from: … — next: …"** and CONTINUE. Read order after that: `docs/HANDOFF.md` §1
→ `memory/session-current-focus.md` (▶ NOW) → `CLAUDE.md` → CHANGELOG `[2026-08-03a]`.

**MONITORING MANDATE:** read the cycle log on the FIRST tool call of every batch. `>2 min` old ⇒ the
loop is DEAD. `RED` is normal. **`drift=0` and `sci=OK` are the only two that must never change.**
⚠ **`guards=2` is PERMANENTLY RED and is NOT a live signal** — see §4, this is what hid a real fault.

---

## §2 STATE AT HANDOVER (2026-08-03 ~01:52 UTC, T+124h44m)

```
records 6,403 (climbing +3..+9/cycle)  ·  spend $45.4830  ·  drift 0  ·  sci OK  ·  r115 21B
cores 2,280  ·  jobs 789 (285 running, 504 queued)  ·  26.1% of the ENTIRE cluster
C: free 37.5 GB decimal  ·  archive NTFS-compressed 1.75:1  ·  FULL LADDER TO RUNG 568 FITS
12/12 lines up · 13 supervisors · cycle loop · sentinel · fenced watchdog
branch myriad-cluster-and-tier-system  ·  backup-2026-08-03-run15 pushed
exogenous stop 2026-08-27 00:00 UTC — 23 days 22 hours left, only 17.8% of the window elapsed
```

### WHERE EACH LINE IS — three different stages, and this matters
| stage | lines |
|---|---|
| **C1 reward search** | `core`, `nemotron` |
| **C2 arm / pair test** | `deepseek`, `glm-5.2`, `haiku`, `kimi`, `qwen3.6-27b`, `sonnet-5` |
| **C4 seed ladder** | `gemini-2.5-flash`, `gpt-5.6-luna`, `qwen3.5-9b` |

### THE LADDER — and the uncomfortable truth
```
test_leg_gemini_2_5_flash  2,820 records  prefix 549   <- 66% of ALL sealed-test records
test_leg_gpt_5_6_luna        180          prefix  30
test (core)                  450          prefix  30
sonnet_5 / qwen3_5_9b        150 each     prefix  30
nemotron                      60          prefix  30
haiku_4_5                    117          prefix   4
qwen3_6_27b / kimi / glm / deepseek        prefix   0   (arms JUST started — mid-fill, self-heals)
```
**Under R101 the reported result is the COMMON rung. Gemini's 549-seed lead contributes NOTHING.**
The bottleneck is BALANCE, not cores. 36% of sealed-test work sits above the common rung.

### RESULTS
**None yet, and there must be none.** The confirmatory analysis is pre-registered to run at the end;
reading treatment outcomes now is optional stopping and would destroy the design. **Every instrument
in `docs/analysis/` is effect-blind by construction — KEEP THEM THAT WAY.**
What DOES exist (process measurement, not a treatment effect) is the authoring-reliability table,
which confirms the pre-registered numeracy-bottleneck prediction: `qwen3_5_9b 84% reject (predicted
~83%)`, nemotron 19%, glm 13%, qwen3_6_27b 9%, deepseek 5%, haiku/gemini/gpt 3%, kimi 1%, sonnet 0%.

---

## §3 ⚠⚠⚠ THE ONE OPEN DEFECT — `core / bayes_opt` IS DEAD AND CANNOT SELF-HEAL

```
DEAD UNIT   core   bayes_opt   crashed 2026-08-02T23:20:08Z (during the transport outage)
            no log activity and no newer records since
search candidates:  random_search 30/30 · tpe 22/30 · cma_es 18/30 · bayes_opt 25/30  <- STUCK
```

**WHY IT CANNOT RECOVER ON ITS OWN.** `src/cluster/campaign.py:1840-1845` catches a per-unit crash
deliberately (*"one unit must not sink the ladder"*), records `ok: False`, and **does not retry**.
The supervisor only relaunches a driver that **EXITS** — and the core driver is alive and healthy,
still running `tpe` and `cma_es`. So the unit stays dead indefinitely, silently.

**WHY IT MATTERS.** `bayes_opt` is an H4 search-method comparator. At 25/30 against
`random_search`'s 30/30 the comparison is unbalanced.

**THE FIX: restart the CORE line only** (one process, not twelve). `--resume` re-derives pending
from disk; nothing is lost; the core line has already been relaunched twice successfully
(supervisor "attempt 3"). **Process termination is BLOCKED for the agent** — this is Tamer's.
The core driver is one of the `run_campaign_cluster.py` python.exe processes with **no `--leg`
flag** (PIDs 42064 / 4880 at handover — RE-IDENTIFY, PIDs change). The supervisor is PID 33076
(`-Line core`). Kill the DRIVER and the supervisor revives it.
⚠ **Verify afterwards with `python docs/ops/crash_watchdog.py --once` — it must print CLEAN.**

---

## §4 ★★★★★ THE MONITORING LESSON — WHY A CRASH WENT UNNOTICED, AND WHAT WAS BUILT

**The detection existed and the SIGNAL WAS LOST.** `campaign_guards.py` printed the crash and
returned RC=2 — but **`guards=2` has been continuously red for days** on an older unrelated issue
("truncation transport"). A NEW fault inside a permanently-red aggregate changes nothing observable.
**That is signal saturation, and it is the single most important operational lesson of this session.**

**⇒ RULE: an alarm that is always on is not an alarm. Every new monitor must alert on the DELTA.**

### BUILT THIS SESSION (all read-only, all with `--selftest`, all ASCII-safe, all ruff-clean)
| file | what it does |
|---|---|
| **`docs/ops/crash_watchdog.py`** | finds units that crashed and never resumed, via TWO independent signals (log activity + newer records); tracks state so a NEW death is loud. selftest 10 cases. **RUNNING, 300 s** |
| **`docs/ops/loginnode_guard.py`** | warns before UCL's usage detector fires; probes via **`myriad13` (UNGATED)** so the observer is outside the mechanism it observes. **RUNNING, 120 s** |
| **`docs/ops/ssh_gate.py`** | ProxyCommand admission gate — a hard concurrency cap on login-node sessions. **ACTIVE on `Host myriad`** |
| **`docs/ops/myriad_watch.py`** | raw-socket transport watcher, 20-min cadence (Tamer's instruction). **RUNNING** |
| `docs/ops/disk_runway.py` | **FIXED** — it measured LOGICAL size and would now report a ceiling that no longer exists |

---

## §5 ★★★★★ THE UCL LOGIN-NODE PENALTY AND THE SSH GATE

**2026-08-03 00:33:47Z UCL auto-penalised `ucestes`** (penalty1: CPU/memory capped at 80% of
6 cores / 30 GB for 30 min on login12). Diagnosed to a cause:

```
steady state (4 consecutive minutes) : 236-314% CPU, 0.05 GB, EXACTLY 4 concurrent qacct
the limit                            : 6 cores  => STEADY STATE IS LEGAL
/opt/sge/default/common/accounting   : 33 GB    <= why ONE qacct costs ~73% of a core
detector fired                       : 108 SECONDS after SSH access returned
```
**⇒ the violation was a STAMPEDE** — all twelve lines resuming at once after the outage,
`tar`-extracting a ~1,400-record backlog while running qacct forensics. The email's own averages
total ~3.5 cores (under the limit); it fired on the PEAK, and it says so.

**THREE FIXES REJECTED ON MEASUREMENT, and the reasons must not be re-litigated:**
1. **kill/nice the remote qacct** — `driver.py` P13 treats a MISSING qacct trace as evidence an array
   was purged and can **RESUBMIT** work. Unacceptable on irreplaceable data.
2. **flock-serialise qacct remotely** — the count sits at exactly 4 because arrival rate already
   meets service rate; serialising builds an unbounded queue, crosses the driver's 120 s timeout,
   and lands in the SAME resubmit path.
3. **change poll flags / driver code** — correct, but needs a twelve-line relaunch.

**⇒ the gate.** `~/.ssh/config` `Host myriad` now carries:
```
ProxyCommand …ssh_gate.py --connect %h %p --max-wait 12
ConnectionAttempts 2
ConnectTimeout 35
```
**PROVEN before activation on a separate `myriadgate` alias:** 12 simultaneous sessions → **12/12
succeeded, 0 cap breaches**; **3 MB of random binary round-tripped MD5-identical** (a `0x1A` in text
mode would silently truncate a tar stream).

**⚠⚠ TWO TIMING CONSTRAINTS THAT ARE SAFETY, NOT TUNING:**
* **`ConnectTimeout` MUST EXCEED `--max-wait`.** ssh starts its patience clock when the ProxyCommand
  is SPAWNED, not when the socket opens. At `ConnectTimeout 10`, **8 of 12** sessions died with
  *"Connection timed out during banner exchange"*.
* **`--max-wait` MUST BE BELOW THE SMALLEST CALLER-SUPPLIED `ConnectTimeout`.** An explicit
  `-o ConnectTimeout=N` on a caller's command line **OVERRIDES `~/.ssh/config`**. Six callers pass
  their own: `publish_status.sh` 30 (was 20), `cycle.py` 20, `compute_ledger.py` 25,
  `Send-Remote.ps1` 25, `loginnode_guard.py` 15 (ungated path), and **`src/cluster/telemetry.py` 20
  — which is DRIFT-FENCED and cannot be edited without a twelve-line relaunch.** At `--max-wait 25`
  those callers were STARVED: `RUN4_STATUS.md` published **`? cores`** and 2 real
  `ssh_timeout_diagnostic` events appeared. Lowered to **12**, which leaves 8 s of slack under a
  20 s caller and repairs all six at once **including the one that is unreachable.**

**⚠ HONEST LIMIT: the cap is SOFT.** Under sustained load a session waits then proceeds ungated
(51 of 138 waits did, at the old 25 s setting). That is the deliberate safety valve — a gate that
blocks the campaign is worse than no gate. It **flattens** a burst; it does not forbid one.
**The complete fix is longer `--poll-secs`/`--search-poll-secs` at the next relaunch**, which lowers
the FLOOR as well as the peak. That is the single best thing to do the next time a line restarts
anyway.

---

## §6 ★★★★★ THE MYRIAD OUTAGE — RESOLVED, AND THE ROOT CAUSE IS A TRAP

**17:08:07Z → 00:31:59Z (7 h 24 m).** All three login nodes reset us pre-banner.

```
before : 10.151.114.53  -> 193.60.252.107/.108/.109  RESET, no banner
after  : 10.151.109.237 -> all three                 SSH-2.0-OpenSSH_7.4  SERVING
```

**⇒ the `10.151.114.0/24` VPN pool lost its route/ACL to `193.60.252.0/24`. Myriad was never down.**

**★ THE TRAP, AND IT COST HOURS: a VPN reconnect only helps if it lands on a DIFFERENT /24.**
An earlier reconnect went `.48 → .53`, still inside `10.151.114.0/24`, and RUN 14 recorded that as
*"a new IP — still reset"*, which made a client-side cause look excluded. **It was excluded for the
wrong reason.** **RECOVERY PROCEDURE: reconnect the VPN, then CHECK THE /24.**

**Proved before the fix** by tunnelling through `ssh-gateway.ucl.ac.uk`: login12 answered
`SSH-2.0-OpenSSH_7.4` and accepted our key, with **256 jobs running, 6,027 records in Scratch, 462
written in the last 2 h** — so the campaign never stopped and no job was stalled on a hung
filesystem. `/etc/hosts.deny` also ruled out first-hand (empty, no `10.151.*`).

**FALLBACK KEPT: `ssh myriadjump`** (ProxyCommand via ssh-gateway, key-only, 0.2 s) works
end-to-end. ⚠ Its ProxyCommand path MUST be Windows-style `C:/Users/...` — `$HOME` expands to
`/c/Users/User` under Git Bash, Windows OpenSSH cannot resolve it, **no key is offered**, and ssh
falls through to a password prompt. That is what caused a *"Too many authentication failures"*
disconnect from a shared university gateway. ⚠ The gateway is load-balanced (`ejp-gateway01/02`,
an F5 `.gtm.` VIP) with **per-node LOCAL homes**, so `authorized_keys` on one node is absent on the
other — a diagnostic escape hatch, **not** a production route.

---

## §7 ★★★★★ DISK — THE CEILING IS GONE, AND ONE THING MUST NEVER BE DONE

```
C: free 31.78 -> 37.5 GB decimal   ·   archive NTFS-compressed 1.75:1, 100% coverage
rung 568: needs 10.1 GB on disk, leaves 27.5 GB against the 20 GB floor
docs/ops/disk_runway.py: "The full ladder fits above the floor on the CURRENT free space."
```

**HOW:** ten inert trees relocated to D: behind verified junctions (copy → verify file count AND
bytes → only then remove source → junction → prove read-through), then **NTFS compression on the
archive**. Byte-identity proved: the same `record.json` hashes to `CA5CE6F5C513D04EEFD6EEA231BEBB44`
before and after, with `Compressed=True`. Records pulled AFTER recovery arrive compressed, so it
holds for the whole remaining ladder. **Sweep time unchanged** (32-65 s) — no new monitor load.

**★ THE DESIGN POINT: the compression attribute is on the archive ROOT, and that is load-bearing.**
A new file INHERITS compression; a file **RENAMED** into a compressed directory does NOT. The pull
commits via `os.rename` from `.pull_tmp`, so compressing only the leg directories would leave every
FUTURE record uncompressed while looking like it worked.

### ⛔ PROHIBITION — NEVER JUNCTION THE ARCHIVE (OR ANY LEG SUB-ROOT) TO ANOTHER VOLUME
`src/cluster/poll.py:305` commits every pulled record with `os.rename`, whose stated correctness
argument is *"same filesystem by construction"*. **Measured:**
```
os.rename(.pull_tmp\rec -> <junction to D:>\rec)
  OSError winerror=17 errno=18  "The system cannot move the file to a different disk drive"
```
`poll.py:306`'s except-branch runs `shutil.rmtree(src)` — **every pulled record silently DELETED
while the driver reports success.** Only a whole-root move (staging + destinations on one volume) is
safe, and it is unnecessary. Recorded in `docs/DEFERRED_FIXES_RUN4.md`.

⚠ **C: and D: are ONE PHYSICAL DISK** (WD SN740 512 GB, DiskNumber 0, one serial). RUN 14's
"the campaign survives either drive failing" was FALSE — that redundancy never existed.

---

## §8 HARNESS LIMITS MEASURED THIS SESSION (test the specific command; do not assume)

```
taskkill / Stop-Process              BLOCKED
HKLM registry write                  BLOCKED  (and Win32_PageFileSetting WMI too)
New-Item -ItemType Junction          WORKS    ⚠ RUN 15 says BLOCKED — IT IS NOT
compact.exe (NTFS compression)       WORKS
Dism.exe                             WORKS (session runs ELEVATED)
firewall rule creation               BLOCKED
moving trees out of C:\Program Files BLOCKED  (user-profile + project trees are allowed)
editing ~/.ssh/config                allowed after Tamer's explicit ratification
```

---

## §9 ⚠ CLAIMS IN RUN 15 THAT THIS SESSION MEASURED AND FOUND FALSE

| RUN 15 said | measured truth |
|---|---|
| §4 `New-Item -ItemType Junction` BLOCKED | **WORKS** |
| §7 archive on C:, mirror on D: ⇒ survives either drive failing | **VOID** — one physical disk |
| §8.4 `analyze_campaign.py` admits the `.pull_tmp` duplicates | **FALSE** — `:1179` skips dot-prefixed dirs (M267 already fixed it) |
| §2 outage margin "26 of 72 (~2.3 h)" | **UNDERSTATED** — `driver.py:350 max_transport_outage_secs = 43200` = **12 h** |
| §3⑤ `qdel` the 8 junk jobs worth "+64 cores" | **STALE** — that held only while the job cap was saturated; now 664/1000 with 336 free |
| §6.3 pack 8→4 is a gain | **CONTESTED** — it doubles job count against a hard `maxujobs 1000`; at the cap pack 8 gives 8,000 potential cores vs pack 4's 4,000 |

**MY OWN ERRORS THIS SESSION — read these, they are the most useful part:**
1. **GiB vs decimal GB, twice.** Claimed C: had "lost 2.2 GB" and that the pagefile was "11.42 not
   12.26 GB". Both were unit confusion; RUN 15 was right. **State the unit every time.**
2. **An invalid experiment reported as evidence.** My first cross-volume `os.rename` probe used
   `os.system` quoting that silently failed to create the junction, so the `FileNotFoundError`
   proved nothing. Re-run properly against a verified reparse point.
3. **A 142-minute "outage spread" that was an artefact** of my own streak-reset logic treating
   ordinary INFO lines as recovery. The real spread was 129 SECONDS.
4. **Seven "dead pipelines" that were one.** My first crash sweep matched the crash's unit token
   EXACTLY against later activity — but the crash names the ARM (`[placebo]`) while later work is
   logged under the BATCH (`leg4_..._placebo_g3`). Corrected with two independent signals: **1 dead,
   not 7.** *The dominant failure mode remains a check calibrated to a UNIFORM expectation when the
   design is deliberately NON-UNIFORM. Triage by arm/tier/stage BEFORE reporting anything.*
5. **An incomplete fix.** I raised `ConnectTimeout` in `~/.ssh/config` and did not reconcile the six
   callers that pass their own — which broke `RUN4_STATUS.md` (`? cores`). **When a fact changes,
   find EVERY call site.**
6. **A non-ASCII glyph in a `print()`** — this console is cp1251 and it would have crashed.
7. **Instrument bugs my own selftests caught before shipping:** a float-comparison defect
   (`6.0*0.8 = 4.800000000000001` made an exact-ceiling breach report WARN not OVER); a warn
   threshold so lax it rated the measured 2.9-core floor "comfortable"; and a one-shot dead-slot
   reclaim that let 8 of 12 sessions breach the gate's cap.

---

## §10 STANDING RULES THAT MUST SURVIVE THIS HANDOVER

- **NEVER** add Claude/Anthropic attribution. `Co-Authored-By` is REVOKED. Tamer is sole author.
- **NEVER** `git clean -x`, `git add -A`/`-u`, or `git stash`. Stage **by name**.
- **NEVER** lower SGE priority; never `qdel -u`. Explicit ids only.
- **NEVER** read a treatment arm's SEALED-TEST outcome. Every `docs/analysis/` instrument is
  effect-blind **by construction** — keep them that way.
- **NEVER** edit `src|scripts|config|prompts` while live without a relaunch (drift-fenced).
  `docs/**` is safe and does not move `drift`.
- **NEVER** put backticks/backslashes/`$(…)` in a bash `-c` string or heredoc — write to a FILE.
- **⚠ CRLF:** this repo's files are CRLF. Use the Edit tool, not `\n`-anchored replaces.
- **NEVER** trust a wrapper's exit code — read `PYTEST_RC` from the LOG.
- **PowerShell console is cp1251:** a `★` or `⚠` inside a `print()` CRASHES. Printed output ASCII.
- **⚠ Editing a running bash loop is INERT** — bash parses `while…done` once and runs from memory.
  Change the value AND restart, or the cadence silently stays what it was.
- **END-OF-WORK, all four:** `python scripts/update_handoff.py` · a SHORT cursor ▶ NOW entry ·
  a DETAILED CHANGELOG block even with no commits · push the backup branch.

---

## §10b ★★★★★ IN-FLIGHT WORK — WHAT I WAS DOING WHEN STOPPED. **CONTINUE FROM HERE.**

Tamer: *"make sure the new session would be aware of everything, doesnt miss anything, and would
also continue on what you have been doing as well."* This section is that continuation point.

### WHAT WAS MID-STREAM AT THE MOMENT OF HANDOVER
1. **★ I was identifying the CORE driver's PID in order to restart it and resume `bayes_opt` (§3).**
   Established: the core supervisor is `powershell.exe -Line core`; the core DRIVER is a
   `run_campaign_cluster.py` python.exe with **no `--leg` flag** (every other line has one). At
   handover the two no-`--leg` PIDs were **42064** and **4880** — **RE-IDENTIFY, PIDs change.**
   Kill the DRIVER (not the supervisor); the supervisor revives it with `--resume`.
   **This is the single most important outstanding action.**
2. **The six record layers have NOT been re-run since the archive grew.** Last full run was at
   **6,184 records**; it is now **6,403+**. They were ALL CLEAN then. **Re-run all six** (§ below) —
   this is Tamer's item (1) and it must be current, not inherited.
3. **The cores write-up (Tamer's item 2) was answered but not written into the record.** The
   measured conclusion is in §11 item 6 and CHANGELOG `[2026-08-03a]`; no separate document exists.

### THE SIX RECORD LAYERS — RUN ALL OF THEM, EVERY SESSION (Tamer's item 1)
```bash
python docs/analysis/record_validator.py          # R1-R9  contract, hashes, identity, endpoint replay
python docs/analysis/record_provenance_seal.py    # P1-P4  the record vs the FILES beside it
python docs/analysis/record_science_audit.py      # S1-S10 scientific soundness + the BANKED RUNG
python docs/analysis/fed_text_identification.py   # S11    is each arm FED what the design registers
python docs/analysis/reward_code_audit.py         # S12    authored code vs the LIVE sandbox gate
python docs/analysis/fed_value_coherence.py       # S13    fed VALUES coherent + pipeline exact
```
All six exited 0 at 6,184 records. Each has `--selftest`. **S1-S10 is wired into `cycle.py`,
rate-limited to once per 30 min** (a monitor is a LOAD on the monitor it joins).
⚠ **S10 reporting "common prefix 0 / banked rung 0" is a MID-FILL ARTEFACT, not a regression.** Arms
that previously had zero sealed-test records have just started and their first seeds are not 0
(measured: `qwen3_6_27b` distributional/scalar hold only seeds {28,29}). The prefix is a MINIMUM over
arms, so a newly-started arm drags it to 0 and it self-heals as seeds 0..27 land. **Verify before
reporting it as damage.**

### EVERYTHING RUNNING AT HANDOVER (counts include parent shells)
```
run_campaign_cluster 23   mode_d_supervisor 12   cycle_loop 4   sentinel 3
crash_watchdog 3  loginnode_guard 3  myriad_watch 3  allocation_advisor 3
publish_loop 2  watchdog_fenced 2  ssh_reaper 2  campaign_backup 2
```
**If `crash_watchdog`, `loginnode_guard` or `myriad_watch` are absent, RELAUNCH THEM** — they are new
this session and are not yet in `mode_d_launch.ps1`, so **a reboot will NOT bring them back.**
```bash
nohup python docs/ops/crash_watchdog.py  --interval-secs 300  --quiet >/dev/null 2>&1 &
nohup python docs/ops/loginnode_guard.py --interval-secs 120  --quiet >/dev/null 2>&1 &
nohup python docs/ops/myriad_watch.py    --interval-secs 1200 --quiet >/dev/null 2>&1 &
```
**★ WORTH DOING: add those three to `mode_d_launch.ps1` so they survive a reboot** — but that file is
`scripts/**` and DRIFT-FENCED, so it needs a relaunch window. Logged, not done.

### SCRATCH ARTEFACTS FROM THIS SESSION (kept, not repo files)
`D:\tmp\claude\…\scratchpad\` holds `ssh_probe.py`, `login_enum.py`, `onset_v2.py`,
`gateway_probe.py` (the ssh-gateway tunnel diagnostic — reads its password from stdin, never stores
it), `relocate.ps1` (the verified move-and-junction tool), `silent_failure_sweep.py`,
`crash_triage.py`, `rc_support_email.txt` (drafted, **not sent, no longer needed**), and `pkg/`
(an isolated paramiko install — the campaign venv was NOT modified).
⚠ `D:\llm_rp_relocated\Users_User_Desktop_dissertation_papers__CLAUDE_TRANSFER__1_` is a verified
copy whose SOURCE could not be purged (long paths + classifier), so **0.26 GB is duplicated** —
harmless, recorded, nothing lost.

## §10c ★★★★★ STILL-LIVE FINDINGS INHERITED FROM RUN 15 — **NOT SUPERSEDED. DO NOT LOSE THESE.**

RUN 16 supersedes RUN 15 on transport, disk and cores. **Everything below remains TRUE and
UNRESOLVED** and was verified as still open at this handover.

### ⚠⚠⚠ (A) R115 — THE ONLY OPEN ITEM THAT TOUCHES THE GRADE
`config/preregistration.yaml: fitness.winner_max_fallback_frac: 0.10` defends its VALUE as
immaterial: *"THRESHOLD-INSENSITIVE, not tuned: over 613 counter-carrying records the distribution
is strongly bimodal — worst trace 0.41 %, mildest severe 39.40 %, a 96x EMPTY GAP — so any value in
~1-35 % partitions the data identically."*

**That justification is now EMPIRICALLY FALSE** (re-measured on the campaign's own records and
independently confirmed by a read-only auditor): the claimed empty gap has FILLED, and every
threshold in 1-35 % now partitions the data differently. At the tier where R115 actually ACTS
(search-candidate selection, `scripts/run_campaign.py:777-780`), **15 of 60 `(line, arm)` groups have
a DIFFERENT ELIGIBLE SET across the band**, and the frozen winner
`qwen3_5_9b/placebo_shuffled-g0-c3` **IS the 9.08475 % candidate** — so at any threshold at or below
9.08 %, well inside the band the registration calls identical, **a DIFFERENT reward would have been
frozen and sealed at 30 seeds.** The live monitor agrees by a second route: `r115=21B` in the cycle
log is 21 breaches AND BINDING.

**WHAT IS AND IS NOT WRONG.** The VALUE is protected — pre-committed BEFORE any campaign data
existed, and the rule is effect-blind by construction (`_winner_eligible` never touches
`val_fitness`). **It is NOT a forking path.** What is wrong is the **JUSTIFICATION**, and an
adversarial reader (Okhrati is exactly that reader) would re-derive the distribution and break it.
**⚠ IT CANNOT BE FIXED BY EDITING** — both `config/preregistration.yaml` and `PREREGISTRATION.md`
are hash-bound inside the frozen canonical hash `3ca6f01ab772`. **The correction is a DISCLOSURE and
it is TAMER'S DECISION**: a dated amendment row or a stated Limitation, restating the justification
historically. **The threshold must NOT be changed** — that would convert a presentational fix into a
post-data forking path.

### (B) THE NUMERACY BOTTLENECK IS VISIBLE IN THE SEALED LEG — a real write-up disclosure
Sealed-test safe-default fallback is confined to `test_leg_qwen3_5_9b` (the ~17 % authoring-
reliability BOTTOM anchor): `distributional` (TREATMENT) 30 records at 7.84-7.85 %,
`placebo_shuffled` 30 at exactly 9.0847 %, that leg's `scalar` at ZERO. Within that leg the H2 pair
is **asymmetric in EXECUTION QUALITY** — the confound R115 exists to bound, INSIDE its tolerance
(worst 9.0847 % against the 10 % floor, margin 0.92 pp). **No result is compromised**; it is the
bottleneck made visible, and it belongs in the write-up. (This session re-measured the same
phenomenon from the other side: the per-model reject table, §2.)

### (C) DETERMINISM IS **NOT** EVIDENCED BY THIS ARCHIVE
S4 groups sealed-test records by `(arm, seed, reward_source_hash)` and finds 0 disagreements — but
**RUN 4 contains NO REPLICATES**, so the check compares NOTHING and the result is VACUOUS. The audit
now prints the replicate count and says so outright. **Determinism must be evidenced from the 30/30
bit-identical farm or a crash-rehearsal replay — NEVER from this archive.** (RUN 14 twice reported
"determinism is now MEASURED" from this check and had to retract it.)

### (D) OTHER STANDING DISCLOSURES — all still true
* **`metrics.train_curve.return` is 100 % NaN** on every record (SB3 `ep_rew_mean`; no episode closes
  in the logging window). `actor_loss`/`critic_loss`/`ent_coef`/`step` ARE populated and no figure
  reads `return`. A disclosure, not a defect — **but never build a convergence exhibit from it.**
* **The reflection source is STICKY** (`src/llm/loop.py:728-729`): `prev_feedback_block` is replaced
  ONLY when a generation produces a best candidate, so a fed vector can come from ANY earlier
  generation (traced: `scalar_cvar5` at g5 still being fed g3-c4's vector).
* **The no-feedback fallback is BY DESIGN** (`loop.py:406-409`): a generation yielding no usable
  candidate leaves `prev_feedback_block = None`, so the next generation uses the INITIAL prompt.
  Three records do this, all in `qwen3_5_9b`. Verified, not assumed.
* **`lanes.EXCLUDED_CPU_POOLS` is referenced only in DOCSTRINGS and enforced by NO code path** — the
  list that protects CRN bit-exactness is advisory.
* **`REGISTERED_TEST_LEN = 1571` is sourced from a COMMENT** in the frozen yaml, not an independent
  config value, so S2 is a self-consistency check. MINOR, recorded.
* **The 56 frozen-winner markers carry NO execution-quality counters**, so the R115 eligibility fact
  is only reconstructible from the source search record. MINOR provenance gap.
* **⚠ THE RENDER ORDER IS NOT THE LEVEL ORDER.** The prompt emits CVaR 5 %, 10 %, 25 %, **then** 1 %
  (flagged *high-variance estimate*), then mass and skew. **PARSE BY LABEL** — positional parsing
  silently pairs `cvar_25` with `cvar_01`.
* **e00a is UNREACHABLE** (4/4 real submissions refused; it is a GPU pool). **f00a offers 0 slots.**
  Do not re-litigate either as a core lever.
* **The MEMORY lever (2G → 1.6G/slot) was investigated and REFUSED on measurement** — `qacct` on
  three completed 8-slot jobs showed maxvmem 11.435/11.449/11.564 GB against a 16 GB request, but it
  buys only +16 cores for a twelve-line relaunch on 15-hour trainings with no re-run. Recorded so it
  is not re-litigated a fourth time.

### (E) LANE PROTOCOL — YOU ARE NOT THE ONLY SESSION
`docs/LANE_PROTOCOL.md` governs multi-session working. **`paper/**` belongs to the WRITEUP lane;
`src|scripts|config|prompts|docs/ops|outputs` belong to OPS (you).** Register at session start:
```bash
.venv/Scripts/python.exe ../.claude/lanes/lanebus.py join ops
```
A SessionStart hook prints the bus; `[M###]` threads are inter-lane messages. ⚠ 15 claims on that bus
are **WITHDRAWN** — do not act on or re-transmit them.

### (F) THE FOUR AUTHORITIES — checked EXPLICITLY on every substantive decision
`CLAUDE.md` is auto-loaded and is law: (1) the ★ PRIORITIES (95%+ floor, world-class, deep,
corpus-grounded + novel, **100 % reproducibility**), (2) **Dr Okhrati's revealed grading function**
+ his six duties (every number arrives with its MECHANISM, UNCERTAINTY and COUNTERFACTUAL; the
seed-trajectory duty; every surprise is an obligation), (3) **Raad + Stefan's industry feedback**,
(4) the **IFTE0008 guidelines** (10,000-word body, 16 sections in order, four equally-weighted
dimensions where the WEAKEST CAPS the mark). Read it before writing anything for the PDF.

## §11 THE ACTION QUEUE

1. **⚠ RESTART THE CORE LINE** to resume `bayes_opt` (§3). Tamer's — process kill is blocked.
   Verify with `crash_watchdog.py --once` → must print CLEAN.
2. **TAMER: ROTATE THE UCL PASSWORD** (§0.3 item 5).
3. **At the next natural relaunch of any line**, apply longer `--poll-secs 300 --search-poll-secs
   120` — the complete fix for login-node load (§5).
4. **Fix the D18 nested-dir admission in `load_campaign_records`** before the headline analysis:
   `_walk` should skip a child whose parent already carries a `record.json`. Bounded at 2 of 4,192,
   both SEARCH tier, zero in the sealed test. Do NOT move the directories — that trips
   `mirror_archive.ps1`'s shrink guard.
5. **D-RUN15-1** — the driver's STARTUP path (`submit.py:148`, resolving `$HOME` over ssh) has no
   transport-outage tolerance, so any line relaunched during an outage crash-loops at 600 s.
   Fix when the lines are next relaunched.
6. **CORES (Tamer's item 2):** we hold **26.1% of the cluster, 2.3× the next user**, with queued jobs
   priced BELOW others — this is fair-share, not a fault (`qquota` confirms nothing caps us). The
   real lever on the REPORTED result is **line balance, not more cores** (§2). Both remaining core
   levers need a relaunch and are individually worth ~3%.
7. **`campaign_summary.json` AT TEARDOWN** — still the only UNRECOVERABLE item.
