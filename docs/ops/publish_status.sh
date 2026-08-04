#!/bin/bash
# Write docs/RUN4_STATUS.md and push it, so Tamer can read live progress from his phone via GitHub
# without the session having to be asked. Also pulls first, so any instruction he wrote into
# docs/REMOTE_CONTROL.md arrives before the push (and cannot be clobbered by it).
#
# 2026-07-30, on Tamer's instruction ("make sure you post DETAILED updates"): this used to publish
# eight scalars plus a "what to expect next" block that still described LAUNCH NIGHT two days later.
# A status page whose narrative is stale is worse than a short one, because it is read as current.
# It now reports STAGE, COMPUTE, RESULTS, per-rung ETAs and what needs him -- all computed live.
#
# ASCII ONLY. Non-ASCII mojibakes on his phone, so no em dashes, arrows or box characters.
set -u
REPO=/c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
ROOT=outputs/campaign_cluster_run4
cd "$REPO" || exit 1

# INTERPRETER, PINNED (auditor finding F-2, 2026-08-03) -- the same defect as P231, which was
# fixed in cycle_loop.sh and left LIVE here. This loop is started by the SAME boot-task line
# (scripts/install_onstart_task.ps1) from a Git-bash login shell whose PATH resolves a bare
# `python` to the BASE interpreter. That interpreter has no psutil and cannot `import src`, so
# two panels on the page Tamer reads from his phone were WRONG rather than missing:
#   * session_preflight --line-summary exited 1 (psutil unavailable) and this script rendered
#     '? / ?  <- a roster line is MISSING or a stray is present' -- a FALSE fleet alarm;
#   * stage_eta.py died on `import src`, giving '(eta model unavailable this cycle)'.
# An operator-facing page that invents an alarm is worse than one that omits a number.
# Fails LOUD rather than falling back: a silent fallback is exactly what caused this.
PY=".venv/Scripts/python.exe"
if [ ! -x "$PY" ]; then
    echo "publish_status: FATAL - no venv interpreter at $PY (cwd=$(pwd))" >&2
    echo "publish_status: refusing to publish a page built by an unknown interpreter" >&2
    exit 1
fi

git pull --rebase --quiet origin backup-2026-07-28 2>/dev/null || git pull --rebase --quiet 2>/dev/null || true

TS=$(date -u +'%Y-%m-%d %H:%M UTC')
LAUNCH=1785272938   # 2026-07-28 21:08:58 UTC, supervisors up
EL=$(( ($(date -u +%s) - LAUNCH) / 60 ))
HM="T+$((EL/60))h$(printf '%02d' $((EL%60)))m"

# COUNT THE SAME WAY THE AUTHORITY DOES. `scripts/campaign_guards.py status` -- which is what the
# cycle log's `records=` comes from -- counts `root.glob("*/*/*/record.json")`, a FIXED depth. A bare
# recursive `find` counts 29 more: the `frozen*/` winner markers (depth 3), and a stale
# `.pull_tmp.<pid>/` partial-pull staging dir (depth 5) holding a byte-identical DUPLICATE of a record
# that is already in the archive. So for the whole campaign this page showed Tamer a number ~29 higher
# than the cycle log, with no note that the two count different things, and one of the 29 was a
# duplicate. Neither number was wrong; they answered different questions while wearing the same label.
# `-mindepth 4 -maxdepth 4` reproduces the glob exactly (verified: both = 1527 on 2026-07-31).
records=$(find "$ROOT" -mindepth 4 -maxdepth 4 -name record.json 2>/dev/null | wc -l)
calls=$(cat "$ROOT"/spend_ledger_*.jsonl 2>/dev/null | wc -l)
spend=$(cat "$ROOT"/spend_ledger_*.jsonl 2>/dev/null | "$PY" -c "
import sys,json
t=0.0
for l in sys.stdin:
    l=l.strip()
    if l:
        try: t+=float(json.loads(l).get('cost_usd') or 0)
        except Exception: pass
print(f'{t:.4f}')" 2>/dev/null || echo "0")
# TRANSPORT TIMEOUTS.
# *** FIXED 2026-07-31 (record 76). This counted the literal string 'timed out after', which
# **NOTHING IN THE CODEBASE EVER EMITS** -- `grep -rn "timed out" src/` finds exactly one hit, and it
# is a RETRY-CLASSIFICATION KEYWORD LIST in campaign.py:515, not a log message. The counter was
# therefore STRUCTURALLY ZERO: it could never report a timeout however many occurred, and "transport
# timeouts: 0" has been shown to Tamer on every status page for the whole campaign as if it were a
# measurement. (The value happened to be TRUE -- independently verified: zero `ssh_timeout_diagnostic`
# lines, zero `TimeoutExpired`, zero timeout-ish lines of any kind in any driver log -- but it was
# correct by accident, not by measurement, which is exactly the "a check that cannot fail verifies
# nothing" failure this project keeps finding.)
# It now counts what a real transport timeout ACTUALLY produces: the D9 diagnostic emitted at
# src/cluster/submit.py on `subprocess.TimeoutExpired` (the 120 s `_RUNNER_TIMEOUT_SECS` path), and
# the re-raised exception name.
#
# *** AND THE FIRST VERSION OF THIS FIX WAS ALSO BROKEN. *** It summed with `paste -sd+ | bc` --
# and `bc` IS NOT INSTALLED on this machine, so the whole pipeline yielded empty and defaulted to 0.
# A falsification test (synthetic logs containing both markers -> counter must read 2) caught it
# BEFORE it shipped; without that test one false-green would simply have replaced another. Summing
# is done with `awk`, which is always present.
timeouts=$(grep -hcE 'ssh_timeout_diagnostic|TimeoutExpired' "$ROOT"/driver_*.log 2>/dev/null \
             | awk '{s+=$1} END{print s+0}')
timeouts=${timeouts:-0}
# *** 2026-08-03 (RUN 17, record s.127). THE COUNTER ABOVE IS A LEVEL WITH NO RATE AND NO SEVERITY.
# It is CUMULATIVE-EVER over append-only logs, so it can only rise (58 -> 116 inside one session)
# and cannot distinguish a dead campaign from a healthy one -- the P205 / `guard:transport`
# antipattern, found for the FOURTH time. It also counts LINES, and these logs wrap.
# A timeout only matters through the CONSECUTIVE STREAK it belongs to, measured against the bound
# that actually kills an arm (240, from src/cluster/campaign.py:183 -- 3.0 h on the 45 s SEARCH
# poll, 12.0 h on the 180 s TEST poll). That number is what `transport_health.py` reports, and it
# is the one that would have said something useful while `core` and `nemotron` were dying.
# Kept side by side deliberately: the cumulative figure stays visible but is now LABELLED as the
# level it is, so removing it cannot be mistaken for hiding it.
# ⚠⚠ NO `|| thealth=""` HERE, AND THAT IS THE WHOLE POINT (found by an auditor, 2026-08-03).
# `x=$(cmd) || x=""` DISCARDS THE OUTPUT WHENEVER cmd EXITS NON-ZERO -- and `transport_health.py
# --oneline` returns 1 precisely when "a streak is materially advanced toward fatal" and 2 when the
# scan parsed nothing. So the instrument built to answer "how close are we to a crash" went SILENT
# at exactly the moment it had something to say, and the page printed "unavailable" instead of the
# number. It worked only because the verdict happened to be 0. Capture first, judge after.
thealth=$("$PY" docs/ops/transport_health.py --oneline 2>/dev/null)
thealth_rc=$?
[ -z "$thealth" ] && thealth="(transport health UNAVAILABLE this cycle -- the instrument could not run)"
[ "$thealth_rc" = "1" ] && thealth="** $thealth **  <- ATTENTION: a streak is advanced toward fatal"
[ "$thealth_rc" = "2" ] && thealth="** $thealth **  <- the scan parsed NOTHING; treat as UNKNOWN, not healthy"
# P210 (2026-08-03): this used to be `ls "$ROOT"/driver_*.log | wc -l` -- it counted LOG FILES, and
# a driver log exists FOREVER once created. So this panel printed "12 / 12" permanently and would
# have printed "12 / 12" with every single line dead. It is the number Tamer reads to know the
# campaign is alive, and it was structurally incapable of reporting a dead line: the P203 defect in
# the most user-visible place. It now counts RUNNING supervisors against the roster and names any
# line that is COMPLETE, at the REVIEW GATE, or MISSING -- reusing the census predicate rather than
# re-deriving a fourth copy. Falls back to the old count if the helper cannot run, so the page never
# breaks; the "(log files)" label makes that degraded mode obvious rather than silent.
drivers=$(ls "$ROOT"/driver_*.log 2>/dev/null | wc -l)
# ⚠⚠ SAME BUG, SECOND SITE, AND THIS ONE RE-CREATED P210 (auditor, 2026-08-03).
# `--line-summary` returns 1 exactly when a roster line is MISSING or a stray is present. With
# `|| linestat=""` the real census was DISCARDED at that moment and the page fell back to
# `$drivers / 12` -- the LOG-FILE counter P210 exists to replace, which "would have printed 12/12
# with every single line dead". `$upcount` then greps `12` out of it into the commit message, so
# the git history (a PRIMARY SOURCE for the write-up timeline) would record 12/12 with a line down.
# The fix P210 claimed did not hold in the one case it was written for. Capture first, judge after.
linestat=$("$PY" docs/ops/session_preflight.py --line-summary 2>/dev/null)
linestat_rc=$?
[ -z "$linestat" ] && linestat="$drivers / 12 (log files -- live census unavailable)"
[ "$linestat_rc" = "1" ] && linestat="** $linestat **  <- a roster line is MISSING or a stray is present"
guards=$("$PY" scripts/campaign_guards.py "$ROOT" all >/dev/null 2>&1; echo $?)
gnames=$("$PY" scripts/campaign_guards.py "$ROOT" all 2>/dev/null | grep -E '^\[' | grep -v ' ok$' | sed 's/^\[//;s/\].*//' | tr '\n' ' ')
# *** 2026-07-31 (record 76.4): the default was `none`, which is FALSE-REASSURING. `gnames` is only
# printed when the guards are NOT green, so if this extraction ever broke (a wording change in
# campaign_guards.py) the page would read "RC=2, not green: none" -- a contradiction that scans as
# benign. An extraction that fails must SAY SO. Audited 2026-07-31: every other extraction on this
# page either yields a plausible value or fails loudly; this was the only reassuring-on-failure one.
gnames=${gnames:-"(GUARD-NAME EXTRACTION FAILED -- read campaign_guards.py output directly)"}
armsfull=$("$PY" docs/ops/arm_coverage.py 2>/dev/null | grep -c '5/5 arms submitted')
armsfull=${armsfull:-?}

# ⚠ THIS ROW REPORTED THE **FRESHEST** LOG AND CALLED IT THE STALENESS ALARM (P218).
#
# It computed `(now - MAX(mtime))/60` -- the MINIMUM age across all driver logs -- and rendered it
# under "above ~30 would mean a line has stopped progressing". That can only exceed 30 when EVERY
# line is stale, so it was structurally incapable of reporting the one thing it claimed to report.
# Measured 2026-08-03: it published **0.1 min** while driver_h3.log was 470.5 min and
# driver_gemini-2_5-flash.log 446.0 min old. `cycle.py` correctly uses max(ages).
#
# It is the P210 shape ONE TABLE ROW BELOW the counter fixed earlier the same day, found by an
# independent auditor. Now: the STALEST, and -- exactly as cycle.py does since P209 -- with lines
# whose terminal state is COMPLETE excluded, because a finished ladder never writes again and would
# otherwise pin this row red forever.
stalest=$("$PY" -c "
import glob, os, sys, time
sys.path.insert(0, 'docs/ops')
try:
    from session_preflight import line_terminal_state_by_tag as _st
except Exception:
    _st = None
root='outputs/campaign_cluster_run4'
worst=('', -1.0)
for p in glob.glob(os.path.join(root,'driver_*.log')):
    tag=os.path.basename(p)[len('driver_'):-len('.log')]
    if _st is not None and _st(root, tag) == 'COMPLETE':
        continue
    age=(time.time()-os.path.getmtime(p))/60.0
    if age>worst[1]: worst=(tag, age)
print(('%d min (%s)' % (int(worst[1]), worst[0])) if worst[1]>=0 else '?')" 2>/dev/null || echo "?")

# STAGE + LADDER. Both now come from docs/ops/status_stage.py, which reads DIRECTORY NAMES and
# opens no record at all.
#
# *** 2026-08-03 (RUN 17, record s.125.3). THE INLINE SCAN THIS REPLACES WAS BROKEN TWICE OVER. ***
# (1) COST: it `json.load`ed EVERY record.json in the archive to read two fields -- MEASURED at
#     67.8 s over 9,027 records, run roughly once a MINUTE by publish_loop.sh, growing linearly,
#     CONCURRENTLY with cycle.py's own full-archive sweep (already SWEEP-BOUND at 100-270 s). That
#     is P194 live: a monitor loading the monitor it runs beside. The replacement costs 0.48 s.
# (2) CORRECTNESS: it matched the record's `arm` field campaign-wide, so the "candidates so far"
#     column ADDED EVERY SEALED-TEST SEED of the same arm -- `distributional` published 2,136 when
#     only 1,516 search candidates exist in the whole campaign. A search-stage column silently
#     including test records made the search look ~40% further along than it is.
stage=$("$PY" docs/ops/status_stage.py --stage 2>/dev/null) || stage=""
stage=${stage:-"| (stage scan unavailable) | | |"}
ladder=$("$PY" docs/ops/status_stage.py --ladder 2>/dev/null) || ladder=""
ladder=${ladder:-"| (ladder unavailable this cycle) | | | | |"}
# THE STUCK ALARM'S LIVE VERDICT. It was hardcoded prose ("and currently reads CLEAN") until
# 2026-08-03, i.e. the page asserted CLEAN unconditionally -- including with a line genuinely
# stuck. Read from the instrument now. NO `||` here: line_balance returns 1 on STUCK and 2 on
# UNDECIDED, and discarding its output on non-zero is the exact bug fixed above for `thealth`.
lbverdict=$("$PY" docs/ops/line_balance.py --once 2>/dev/null | grep -E "^(CLEAN|\*\*\* STUCK|UNDECIDED)" | head -3)
[ -z "$lbverdict" ] && lbverdict="(line_balance could not run this cycle -- treat as UNKNOWN, not clean)"

# cluster side (best effort - a failed ssh must not stop the status publish)
# ⚠ ConnectTimeout 20 -> 30 (2026-08-03). An explicit -o here OVERRIDES ~/.ssh/config, so this
# value alone decided whether the publisher survived the SSH admission gate's queue. At 20 it did
# not: queued publishes died at the banner and the page showed `? cores` -- which is exactly what
# Tamer saw. The gate's --max-wait was also lowered to 12 so no caller can be starved; this is the
# belt to that braces, because this is the one page he actually watches.
CL=$(ssh -o BatchMode=yes -o ConnectTimeout=30 myriad 'Q=$(qstat -u ucestes | tail -n +3); echo "jobs=$(echo "$Q" | grep -c .)"; echo "run=$(echo "$Q" | awk "\$5==\"r\"" | grep -c .)"; echo "qw=$(echo "$Q" | awk "\$5 ~ /qw/" | grep -c .)"; echo "cores=$(echo "$Q" | awk "\$5==\"r\" {s+=\$9} END {print s+0}")"' 2>/dev/null)
jobs=$(echo "$CL"  | grep '^jobs='  | cut -d= -f2); jobs=${jobs:-?}
run=$(echo "$CL"   | grep '^run='   | cut -d= -f2); run=${run:-?}
qw=$(echo "$CL"    | grep '^qw='    | cut -d= -f2); qw=${qw:-?}
cores=$(echo "$CL" | grep '^cores=' | cut -d= -f2); cores=${cores:-?}

# THE H1 CANON'S LIVE SEED DEPTH (P240). The page used to assert "30 seeds each" as a flat design
# claim. Amendment R111 registered that the canon CLIMBS the ladder, so 30 is its CURRENT depth, not
# its target -- and a hardcoded depth beside a hand-carried Sharpe table is precisely how a page
# keeps showing a number that stopped being true. Read from the archive on every publish.
canon_depth=$("$PY" -c "
import sys; sys.path.insert(0, 'docs/ops')
import stage_eta as se
d = [len(m) for (t, a), m in se.test_cells().items() if a.startswith('baseline_')]
print(min(d) if d else '?')
" 2>/dev/null)
canon_depth=${canon_depth:-?}

# MYRIAD MAINTENANCE COUNTDOWN (2026-08-03). Tamer confirmed the window was DELAYED from the usual
# second Tuesday (Aug 11) to WEDNESDAY 2026-08-12, at risk all day from 08:00. It is on the page
# because a planned outage that surprises the operator reads exactly like a failure, and the day's
# alarms are all expected. Playbook: docs/ops/MAINTENANCE_2026-08-12.md
maint_days=$("$PY" -c "
import datetime as dt
w = dt.datetime(2026, 8, 12, 8, 0, 0)
d = (w - dt.datetime.utcnow()).total_seconds() / 86400.0
print('IN PROGRESS or PASSED' if d < 0 else ('%.1f days' % d))
" 2>/dev/null)
maint_days=${maint_days:-?}

# per-rung ETAs at the cores we actually hold (Tamer's standing reporting requirement)
# ⚠ NO POSITIONAL SLICE (P234, 2026-08-03). This read `| sed -n '3,12p'` -- a claim about which
# LINES of another tool's output happen to be the interesting ones. Any change to that tool silently
# shifts the window and the page renders the wrong rows with no error. `--page` makes the tool emit
# exactly the block, so the contract is a FLAG rather than a line count.
#
# ⚠ AND STDERR IS KEPT (RUN 17 lesson 2). `2>/dev/null` discarded the diagnostic in precisely the
# case where the tool had something to say -- that is how "(eta model unavailable this cycle)" sat on
# the page for hours with the CAUSE thrown away. Capture first, judge after.
etas=$("$PY" docs/ops/stage_eta.py --page "${cores:-0}" 2>/tmp/stage_eta.err)
eta_rc=$?
if [ "$eta_rc" -ne 0 ] || [ -z "$etas" ]; then
    etas="  (eta unavailable this cycle, rc=$eta_rc) -- $(head -c 300 /tmp/stage_eta.err 2>/dev/null)"
fi

# BUDGET, read LIVE every publish. Tamer holds the balance and the top-up decision (his instruction,
# 2026-07-31: "the budget is fine, I will just top up whenever needed, I watch the balance -- just
# make sure you precisely monitor it"). So this reports the current figures instead of asking him for
# anything, and it is generated rather than typed: the previous hand-written bullet still quoted
# $15.11 of remaining authoring after the real figure had moved to $13.47.
bud=$("$PY" docs/ops/budget_watch.py 2>/dev/null | grep -E '^(anthropic|openrouter) ' | sed 's/^/  /')
bud=${bud:-"  (budget projection unavailable this cycle)"}

# THE 2-MINUTE MONITORING CYCLE (2026-07-31, Tamer's standing order). docs/ops/cycle.py runs the
# whole sweep and appends one line per cycle to docs/ops/watch/CYCLE_LOG.md. Publishing the last few
# lines makes the cadence CHECKABLE from his phone -- "monitored continuously" stops being a claim
# and becomes an audit trail, which is the standard everything else in this project is held to.
cyc=$(tail -n 6 docs/ops/watch/CYCLE_LOG.md 2>/dev/null)
cyc=${cyc:-"  (no cycle recorded yet)"}
cage=$("$PY" -c "
import os, time
p='docs/ops/watch/CYCLE_LOG.md'
print(int((time.time()-os.path.getmtime(p))/60) if os.path.exists(p) else -1)" 2>/dev/null || echo "-1")
if [ "$cage" -lt 0 ]; then cnote="no cycle log yet"
elif [ "$cage" -gt 10 ]; then cnote="**last monitoring cycle was $cage min ago -- the loop has lapsed**"
else cnote="last monitoring cycle $cage min ago"; fi

cat > docs/RUN4_STATUS.md <<EOF
# RUN 4 -- LIVE STATUS

**Auto-generated $TS -- $HM.** Refreshed about every 1-1.5 minutes (measured; the publish itself takes
~60 s, dominated by one ssh for the live core count) and pushed to GitHub, so
it is readable from a phone. To send an instruction back, edit
[docs/REMOTE_CONTROL.md](REMOTE_CONTROL.md) -- the session polls it on the same interval and writes
back what it did.

## Health

| | |
|---|---|
| elapsed | **$HM** (launched 2026-07-28 21:08 UTC; exogenous stop 2026-08-27) |
| lines up | **$linestat**, all five arms submitted on **$armsfull of the 10 leg lines** (h3ss is single-arm by design) |
| stalest driver log | **$stalest** old (P218: the STALEST of the still-running lines, completed ladders excluded; above ~30 means that line has stopped progressing) |
| records archived | **$records** |
| **Myriad maintenance** | **2026-08-12 from 08:00 UTC, at risk all day** (in $maint_days). Delayed from Aug 11. Jobs may die and REQUEUE idempotently; the supervisors ride it. Playbook: docs/ops/MAINTENANCE_2026-08-12.md |
| LLM calls / spend | $calls / **\$$spend** |
| transport health | **$thealth** |
| transport timeouts (cumulative, ever) | $timeouts -- a level with no rate; read the row above |
| guards | $( [ "$guards" -eq 0 ] && echo '**all six green**' || echo "**RC=$guards**, not green: $gnames" ) |

## Compute

| | |
|---|---|
| cluster jobs | **$jobs** ($run running, $qw queued) |
| **cores computing** | **$cores** |

Per-rung ETAs. **The EMPIRICAL block is the one to read**: it is remaining work divided by the rate
we are actually achieving, anchored at the moment this page was generated. The registered model is
kept beneath it as a **duration** and to name the binding constraint. *(Until 2026-08-03 this panel
anchored the model's makespan to LAUNCH rather than to now, so it printed dates in the PAST -- it
showed 08-02 on a page generated 08-03. Fixed; an ETA is now never a past date.)*

\`\`\`
$etas
\`\`\`

### Are we using the maximum Myriad can give us? Re-derived from SGE itself, 2026-08-03 (record sections 120, 121, 122, 123)

**Yes, and the reason changed.** This block used to say the limit was our own experiment having
nothing more to submit. **That is no longer true and has been replaced with what was measured** -- we
now hold a deep backlog we cannot place, and the binding constraint is UCL's fair-share policy, which
is not ours to change.

* **The jobs ARE assignable and we still do not get the slots.** \`qalter -w p\` on a real pending job
  returns *"found possible assignment with 8 slots"*; \`qquota -u ucestes\` is EMPTY, so no quota caps
  us; every host has 105-167 GB free; **2,576 cores are placeable** -- and our core count stays
  pinned. That combination has exactly one explanation: **functional fair-share by user**
  (\`policy_hierarchy OSF\`, \`weight_tickets_functional 500000000\` against \`share 10000\`, 6+ active
  users). More users on the cluster means a smaller share each, and that is the whole story.
* **Every other lever has been individually EXCLUDED BY MEASUREMENT, not by argument.** \`qdel\` on our
  own running jobs would destroy up to 15 h of irreplaceable work each; \`qalter\` on the parallel
  environment is refused site-wide by the JSV; raising priority is operator-only; and **lowering our
  own priority is permitted but INERT** (\`npprior\` is 0.500 for every job on the cluster, so the
  weight cancels out) **and ONE-WAY** -- \`qalter -p 0\` is denied, so it cannot be undone. Widening the
  pool buys 2-4% and memory 0.7%, and both need a twelve-line relaunch of a live campaign.
* **And there is no waste to reclaim on the other side of the equation.** The 8.8% gate-failure rate
  counts candidates rejected BEFORE any training is submitted (one LLM call, not a 15 h training),
  and **zero trainings have been lost**: every completed ladder -- gemini's five arms and h3 -- has
  568 seeds with **ZERO holes**, as does every 30-seed line.
* **Memory and disk block ZERO hosts.** Memory was never scarce at all (160 GB free per host); the
  three separate investigations that "fixed" it were fixing a non-problem.

**Bottom line: buying more hardware cannot make this finish sooner, and neither can any setting we
control.** The seed ladder is tiered (30 -> 189 -> ... -> 568), a truncated run banks the largest
COMPLETED rung, and the stop date is fixed -- so if capacity ever fell short we would simply report at
a lower rung, which is a valid pre-registered result, never a failure.

**Why the cores figure sometimes FALLS while everything is healthy.** Two effects superimpose. A
**completion wave**: every pack-8 job that exits releases 8 slots AND delivers 8 records at once, so
*cores down with records up is throughput ARRIVING*, not leaving (measured 309 -> 437 -> 469 records/h
while cores fell 2,320 -> 1,776). And **rising competition**: other users appearing takes share from
us. A level read without its rate tells the opposite story, which is why the record count and its
delta sit on every monitoring line below.

## Stage -- BOTH phases are running at once

Two things happen per line. **SEARCH:** the LLM writes 5 reward programs, each is trained once and
scored on validation data, the results are fed back, and it writes 5 more -- six rounds. **SEED
LADDER:** once a line's five winners are frozen, they are re-trained on the SEALED data at 30, 100,
189, 279, 340, 403 and finally 568 seeds. **The ladder is NOT a future phase -- it is running now,
and two lines have already finished the whole thing.**

| arm | furthest generation | search candidates so far |
|---|---|---|
$stage

### The seed ladder, live -- and the top row IS the reported result

Under the registered rule (R101) every model climbs ONE ladder together and the result is the
**COMMON RUNG: the MINIMUM over every frozen arm of every line.** So work done by the deepest line
adds NOTHING to the headline until the shallowest catches up, and the top row of this table is the
number the dissertation reports.

!! **THE TWO NUMBER COLUMNS ARE RECORD COUNTS, NOT REGISTERED RUNGS** (corrected 2026-08-03; the
header used to say "rung" and it was wrong). A count can OVERSTATE the rung an arm actually banks,
because an arm banks the largest rung whose WHOLE seed prefix it holds: \`gpt-5.6-luna\` held 567
records with a frontier at seed 567 and banked **189**, not 568, because seeds 192 and 193 were
missing. For the TRUE banked rung run \`docs/analysis/record_seed_completeness.py\` (S15).

| line | **fewest records on any arm** | most on any arm | frozen arms | note |
|---|---|---|---|---|
$ladder

A line reading **0** is MID-FILL, not stuck: its \`distributional\` and \`scalar\` arms are tested last,
behind the C1 barrier, so they sit at zero until their block runs. The check that would matter is a
line with zero jobs RUNNING **and** zero QUEUED, continuously for 45 minutes --
\`docs/ops/line_balance.py\` watches exactly that, and its live verdict is:

\`\`\`
$lbverdict
\`\`\`

!! That line is now **read from the instrument on every publish**. It used to be the fixed sentence
"and currently reads CLEAN" hardcoded in this script, which would have kept telling you CLEAN with a
line genuinely stuck -- the same shape as the log-file counter P210 replaced. (Corrected 2026-08-03
after an auditor found it; the alarm also gained a 45-minute dwell requirement that day, because a
healthy line is legitimately job-less BETWEEN BATCHES for about 20 minutes.)

## Results so far

**No treatment outcome has been looked at, and none may be** -- the confirmatory analysis is
pre-registered to run ONCE, at the end, at whatever rung is reached. Every monitoring instrument is
effect-blind by construction.

What IS reported below is the **hand-written comparison canon (H1)** -- 11 human-designed rewards,
currently at **${canon_depth:-?} seeds each** (read live from the archive on this publish). !! THE
CANON IS NOT PINNED AT 30: amendment **R111** registered that it **CLIMBS THE SEED LADDER** with
everything else, so its depth is a LIVE quantity and \`_TEST_UNITS_PER_RUNG = 71\` carries all 11 in
the per-rung denominator. This line used to read "30 seeds each" as a flat design claim -- true as a
count while the core line sits in C1, but wrong as a statement of the design, and it would have gone
silently stale the moment that line enters C4.
**=> THE SHARPE TABLE BELOW WAS MEASURED AT 30 SEEDS.** It is hand-carried prose, not recomputed on
each publish, so once the number above moves past 30 the table is STALE until re-derived. These are
the BASELINES the LLM is measured against, not the experiment. (LLM-arm
sealed-test records also exist and are counted in the ladder above; their SCORES have not been read.)

| | Sharpe | note |
|---|---|---|
| return_minus_turnover | **+1.16** | the only positive one; it is the one that prices trading |
| the other ten | -0.17 to -0.39 | they rebalance 78-91 pct of the book EVERY day = ~22 pct/yr in costs |
| S&P 500 total return | +1.13 | cap-weighted, same 1571 sealed sessions |
| equal-weight universe | +1.17 | |
| EW-30, same assets | +1.28 | |

Across-seed sd is 0.25 against the 0.244 the seed ladder was powered on, so the plan's core
statistical assumption is confirmed by live data.

## Monitoring -- the cycle ($cnote)

Every cycle runs the six repo guards, the arm-coverage check the guards cannot do, the budget
projection, driver-log freshness, the drift check against the sha the live drivers were launched
from, and your instruction channel.

**Since 2026-07-31 it also checks the RESULTS, not just the processes** (your instruction). Every
cycle opens the archive: the fed block is re-derived from every LLM-arm prompt (a scalar-arm prompt
carrying a tail number would mean the manipulation had leaked), authored programs are checked for
duplication across arms, every reward's source hash is re-computed, and the scored-record invariants
(400,000 steps, the R115 execution floor, no impossible numbers) are re-tested. Four of those are
hard validity invariants and turn the cycle RED on any non-zero reading; the rest are reported with
their movement since the previous cycle. The \`sci=\` token on each line below is that verdict, and
\`r115=\` is the execution-floor breach count (\`B\` = a contaminated candidate currently tops its arm,
which is the floor doing its job). One line is written per cycle; the last six:

\`\`\`
$cyc
\`\`\`

Verdicts: OK nothing needs a human. ATTN something changed. RED a real problem, named on the line.
Acknowledged-and-understood alarms are deliberately kept quiet so a NEW one is loud -- the reasoning
for each is in docs/ops/acknowledged_alarms.txt.

## Budget -- reported, yours to act on

You said you watch the balance and will top up when needed, so this is a report, not a request. Live
figures this publish (spend is measured from the ledgers; "still to author" is projected at each
line's own observed cost per arm-generation; C4 needs no LLM calls, so authoring is the whole
remaining exposure):

\`\`\`
$bud
\`\`\`

The **credited** column is a ledger ESTIMATE carried from the 2026-07-28 console quote, not a balance
reading -- only your console knows the truth, which is exactly why this no longer raises an alarm.
The number to watch is **still to author** on \`anthropic\`: that is the confirmatory line's remaining
exposure. Detail: record section 49.

## Needs Tamer

* ~~\`qdel\` the eight dead jobs~~ **DONE 2026-08-03, on your ratification -- nothing needed from you.**
  All eight (6 \`sshorig\`, 2 \`cpuprobe13\`) deleted, rc=0. **And \`qdel\` was never actually blocked** --
  the brief had said so for three sessions and nobody had tested it. The proof they could never run
  turned out to be mechanical rather than circumstantial: they requested parallel environment
  \`smp-[TBD]\`, and \`qconf -spl\` has no such PE. Before 689 jobs / 1,480 slots, after 680 / 1,488,
  zero error or held throughout. Priced honestly: **no ETA gain** (we sit well under the 1,000-job
  cap); the value is crash-loop margin. Record section 126.1.
* **The R115 disclosure decision.** The frozen registration defends the 10% winner-eligibility floor
  as *"THRESHOLD-INSENSITIVE ... a 96x EMPTY GAP"*. **That gap has since FILLED**: at the tier where
  the rule acts, 15 of 60 (line, arm) groups now have a DIFFERENT eligible set across the band the
  registration calls identical, and one frozen winner IS the 9.08% candidate. **The VALUE is safe** --
  it was pre-committed before any campaign data existed and the rule never reads a performance number,
  so it is not a forking path. What is wrong is the JUSTIFICATION, and both files are inside the
  freeze hash, so it cannot be edited. **The choice is yours: a dated amendment row, or a stated
  Limitation. The threshold itself must NOT be changed** -- that would turn a presentational fix into
  a post-data forking path.
* **A12 -- the public OSF/Zenodo DOI deposit** (about 10 minutes; everything is staged in
  docs/A12_DEPOSIT_PACKAGE.md). A registered freeze-day obligation that is currently unmet.

## If something looks wrong

The campaign is independent of the Claude session: supervisors relaunch drivers, the watchdog revives
dead lines every 300 s, the sentinel watches health. **Stop lever:** create the file
\`outputs\\campaign_cluster_run4\\STOP_CAMPAIGN\` (or just ask via REMOTE_CONTROL.md).

Full narrative: [CAMPAIGN_EXECUTION_RECORD.md](CAMPAIGN_EXECUTION_RECORD.md), newest sections last.
EOF

# ---- PAGE ASCII GATE (P241) --------------------------------------------------------------------
# The header rule ("ASCII ONLY. Non-ASCII mojibakes on his phone") was broken FOUR times, twice by
# the person fixing the previous breach. Enforce it on the artefact instead of on the author: read
# back what was actually written and refuse to publish anything with a codepoint > 127.
# Fails LOUD and leaves the last good page in place -- a stale correct page beats a fresh broken one.
if ! "$PY" -c "
import sys
bad = []
for n, line in enumerate(open('docs/RUN4_STATUS.md', encoding='utf-8'), 1):
    for ch in line:
        if ord(ch) > 127:
            bad.append((n, hex(ord(ch)), line.strip()[:80]))
            break
if bad:
    print('publish_status: FATAL - %d non-ASCII line(s) in the page:' % len(bad), file=sys.stderr)
    for n, cp, s in bad[:5]:
        print('  line %d (%s): %s' % (n, cp, s), file=sys.stderr)
    sys.exit(1)
"; then
    echo "publish_status: REFUSING to commit a page with non-ASCII (it mojibakes on the phone)." >&2
    echo "publish_status: the previous page is left in place. Fix the emitting line and re-run." >&2
    git checkout -- docs/RUN4_STATUS.md 2>/dev/null || true
    exit 1
fi

git add docs/RUN4_STATUS.md
# P210, second site: this carried `$drivers/12` too, so every status commit in the git history
# reads "12/12 lines" regardless of how many are actually up. The commit log is a PRIMARY SOURCE for
# the write-up's timeline, so a counter that cannot go down would have written a false record of the
# campaign into history. `$upcount` is the live supervisor count from the same census the panel uses.
upcount=$(printf '%s' "$linestat" | grep -oE '^[0-9]+' || echo "$drivers")
# ⚠⚠ `--only docs/RUN4_STATUS.md` IS LOAD-BEARING (P251, 2026-08-04). This was a BARE `git commit`,
# which commits THE WHOLE INDEX -- and this loop runs every ~2 minutes. Any file a human or another
# session had `git add`ed and not yet committed was silently swept into the next status commit.
# MEASURED: commit d7b85965, labelled "status: T+147h38m", carries 366 insertions of RUN 19's
# stage_eta/preflight/ledger/CHANGELOG work. Nothing was lost, but the campaign's own commit log is
# a PRIMARY SOURCE for the write-up timeline, and an automated committer that absorbs unrelated
# staged work corrupts that record -- and would happily commit a half-finished edit.
# It is the mirror image of P242, where a directory-level `git add` swept 17 runtime logs into an
# unrelated commit. `--only <path>` commits that path REGARDLESS of what else sits in the index.
git commit -q --only docs/RUN4_STATUS.md -m "status: $HM - $upcount/12 lines up, $cores cores, $records records, \$$spend, $timeouts timeouts" 2>/dev/null \
  && git push -q origin HEAD:backup-2026-07-28 2>/dev/null \
  && git push -q origin HEAD:myriad-cluster-and-tier-system 2>/dev/null \
  && echo "published $TS  ($HM, $cores cores, $records records)" \
  || echo "no change to publish at $TS"
