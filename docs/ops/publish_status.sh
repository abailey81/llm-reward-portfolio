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
spend=$(cat "$ROOT"/spend_ledger_*.jsonl 2>/dev/null | python -c "
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
# P210 (2026-08-03): this used to be `ls "$ROOT"/driver_*.log | wc -l` -- it counted LOG FILES, and
# a driver log exists FOREVER once created. So this panel printed "12 / 12" permanently and would
# have printed "12 / 12" with every single line dead. It is the number Tamer reads to know the
# campaign is alive, and it was structurally incapable of reporting a dead line: the P203 defect in
# the most user-visible place. It now counts RUNNING supervisors against the roster and names any
# line that is COMPLETE, at the REVIEW GATE, or MISSING -- reusing the census predicate rather than
# re-deriving a fourth copy. Falls back to the old count if the helper cannot run, so the page never
# breaks; the "(log files)" label makes that degraded mode obvious rather than silent.
drivers=$(ls "$ROOT"/driver_*.log 2>/dev/null | wc -l)
linestat=$(python docs/ops/session_preflight.py --line-summary 2>/dev/null) || linestat=""
[ -z "$linestat" ] && linestat="$drivers / 12 (log files -- live census unavailable)"
guards=$(python scripts/campaign_guards.py "$ROOT" all >/dev/null 2>&1; echo $?)
gnames=$(python scripts/campaign_guards.py "$ROOT" all 2>/dev/null | grep -E '^\[' | grep -v ' ok$' | sed 's/^\[//;s/\].*//' | tr '\n' ' ')
# *** 2026-07-31 (record 76.4): the default was `none`, which is FALSE-REASSURING. `gnames` is only
# printed when the guards are NOT green, so if this extraction ever broke (a wording change in
# campaign_guards.py) the page would read "RC=2, not green: none" -- a contradiction that scans as
# benign. An extraction that fails must SAY SO. Audited 2026-07-31: every other extraction on this
# page either yields a plausible value or fails loudly; this was the only reassuring-on-failure one.
gnames=${gnames:-"(GUARD-NAME EXTRACTION FAILED -- read campaign_guards.py output directly)"}
armsfull=$(python docs/ops/arm_coverage.py 2>/dev/null | grep -c '5/5 arms submitted')
armsfull=${armsfull:-?}

# staleness of the freshest driver log: a line can hold its process and stop progressing (D14)
freshest=$(python -c "
import glob, os, time
ts=[os.path.getmtime(p) for p in glob.glob('outputs/campaign_cluster_run4/driver_*.log')]
print(int((time.time()-max(ts))/60) if ts else '?')" 2>/dev/null || echo "?")

# STAGE: furthest generation reached per arm, across all twelve lines
stage=$(python -c "
import glob, json
from collections import defaultdict
ARMS=('distributional','scalar','placebo','scalar_cvar5','placebo_shuffled')
g=defaultdict(int); n=defaultdict(int)
for p in glob.glob('outputs/campaign_cluster_run4/**/record.json', recursive=True):
    try: r=json.load(open(p, encoding='utf-8'))
    except Exception: continue
    a=r.get('arm')
    if a in ARMS and isinstance(r.get('generation'), int):
        g[a]=max(g[a], r['generation']); n[a]+=1
for a in ARMS:
    print('| %s | g%d of 5 | %d |' % (a, g.get(a,0), n.get(a,0)))" 2>/dev/null || echo "| (stage scan unavailable) | | |")

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

# per-rung ETAs at the cores we actually hold (Tamer's standing reporting requirement)
etas=$(python docs/ops/stage_eta.py "${cores:-0}" 2>/dev/null | sed -n '3,12p')
etas=${etas:-"  (eta model unavailable this cycle)"}

# BUDGET, read LIVE every publish. Tamer holds the balance and the top-up decision (his instruction,
# 2026-07-31: "the budget is fine, I will just top up whenever needed, I watch the balance -- just
# make sure you precisely monitor it"). So this reports the current figures instead of asking him for
# anything, and it is generated rather than typed: the previous hand-written bullet still quoted
# $15.11 of remaining authoring after the real figure had moved to $13.47.
bud=$(python docs/ops/budget_watch.py 2>/dev/null | grep -E '^(anthropic|openrouter) ' | sed 's/^/  /')
bud=${bud:-"  (budget projection unavailable this cycle)"}

# THE 2-MINUTE MONITORING CYCLE (2026-07-31, Tamer's standing order). docs/ops/cycle.py runs the
# whole sweep and appends one line per cycle to docs/ops/watch/CYCLE_LOG.md. Publishing the last few
# lines makes the cadence CHECKABLE from his phone -- "monitored continuously" stops being a claim
# and becomes an audit trail, which is the standard everything else in this project is held to.
cyc=$(tail -n 6 docs/ops/watch/CYCLE_LOG.md 2>/dev/null)
cyc=${cyc:-"  (no cycle recorded yet)"}
cage=$(python -c "
import os, time
p='docs/ops/watch/CYCLE_LOG.md'
print(int((time.time()-os.path.getmtime(p))/60) if os.path.exists(p) else -1)" 2>/dev/null || echo "-1")
if [ "$cage" -lt 0 ]; then cnote="no cycle log yet"
elif [ "$cage" -gt 10 ]; then cnote="**last monitoring cycle was $cage min ago -- the 30-second cadence has lapsed**"
else cnote="last monitoring cycle $cage min ago"; fi

cat > docs/RUN4_STATUS.md <<EOF
# RUN 4 -- LIVE STATUS

**Auto-generated $TS -- $HM.** Refreshed every 5 minutes by the live session and pushed to GitHub, so
it is readable from a phone. To send an instruction back, edit
[docs/REMOTE_CONTROL.md](REMOTE_CONTROL.md) -- the session polls it on the same interval and writes
back what it did.

## Health

| | |
|---|---|
| elapsed | **$HM** (launched 2026-07-28 21:08 UTC; exogenous stop 2026-08-27) |
| lines up | **$linestat**, all five arms submitted on **$armsfull of the 10 leg lines** (h3ss is single-arm by design) |
| freshest driver log | **$freshest min** old (above ~30 would mean a line has stopped progressing) |
| records archived | **$records** |
| LLM calls / spend | $calls / **\$$spend** |
| transport timeouts | **$timeouts** |
| guards | $( [ "$guards" -eq 0 ] && echo '**all six green**' || echo "**RC=$guards**, not green: $gnames" ) |

## Compute

| | |
|---|---|
| cluster jobs | **$jobs** ($run running, $qw queued) |
| **cores computing** | **$cores** |

Per-rung ETAs from the registered model at the cores we actually hold:

\`\`\`
$etas
\`\`\`

### Are we using the maximum Myriad can give us? Measured 2026-07-31 (record section 70)

**Yes, and the limit is our own experiment, not the cluster.** Checked at every layer:

* **Right now (search phase):** there is room on pool d for **303 more of our jobs**, and we only have
  about **100 waiting**. We are not being held back - we have nothing more to submit. During the search
  each arm must wait for all 5 of its candidates to finish before it can write the next 5, so the
  ceiling is the 6-round chain, not the hardware.
* **Memory and disk block ZERO hosts.** Both were fixed/checked; neither costs us anything now.
* **At the seed-ladder phase (where cores really matter):** we could place about **900 jobs (~7,200
  cores)**, and the timing model stops improving past **~4,600 cores** - so we will have about **1.6x
  more capacity than we can even use**.
* **We have already proved it:** we held **over 1,000 cores for ~14 hours straight, peaking at 1,664** -
  and that was while still carrying two problems that have since been fixed (a 19.5x oversized memory
  request, and a priority setting that put us below every other user). Both are gone, so the ladder
  should do better than that.
* **Everything else has been tried and measured:** more threads makes it SLOWER (and would break
  reproducibility), a wider pool buys 4% but reintroduces a hardware-mixing problem, and priority is
  already fixed and now above the cluster average.

**Bottom line: buying more hardware cannot make this finish sooner.** The remaining wait is the
experiment's own serial structure. The seed ladder is tiered (30 -> 189 -> ... -> 568) and the stop date
is fixed, so if capacity ever fell short we would simply report at a lower rung - a valid, pre-registered
result, never a failure.

## Stage -- we are in the SEARCH phase (the LLM writing and rewriting rewards)

Each line's LLM writes 5 reward programs, each is trained once and scored on validation data, the
results are fed back, and it writes 5 more. Six rounds. A line finishes when its SLOWEST arm does.
The seed ladder (30 up to 568 seeds, scored on the SEALED data) is the NEXT phase and has not started
-- that is the phase the experiment's answer comes from, and where thousands of cores get used.

| arm | furthest generation | candidates so far |
|---|---|---|
$stage

## Results so far

Only the 11 hand-written comparison rewards have been scored on sealed data (30 seeds each). **The
LLM-written rewards have not been tested yet** -- that is the next phase, and it is the actual
experiment. No hypothesis has been looked at.

| | Sharpe | note |
|---|---|---|
| return_minus_turnover | **+1.16** | the only positive one; it is the one that prices trading |
| the other ten | -0.17 to -0.39 | they rebalance 78-91 pct of the book EVERY day = ~22 pct/yr in costs |
| S&P 500 total return | +1.13 | cap-weighted, same 1571 sealed sessions |
| equal-weight universe | +1.17 | |
| EW-30, same assets | +1.28 | |

Across-seed sd is 0.25 against the 0.244 the seed ladder was powered on, so the plan's core
statistical assumption is confirmed by live data.

## Monitoring -- the 30-second cycle ($cnote)

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

* **A12 -- the public OSF/Zenodo DOI deposit** (about 10 minutes; everything is staged in
  docs/A12_DEPOSIT_PACKAGE.md). A registered freeze-day obligation that is currently unmet.

## If something looks wrong

The campaign is independent of the Claude session: supervisors relaunch drivers, the watchdog revives
dead lines every 300 s, the sentinel watches health. **Stop lever:** create the file
\`outputs\\campaign_cluster_run4\\STOP_CAMPAIGN\` (or just ask via REMOTE_CONTROL.md).

Full narrative: [CAMPAIGN_EXECUTION_RECORD.md](CAMPAIGN_EXECUTION_RECORD.md), newest sections last.
EOF

git add docs/RUN4_STATUS.md
git commit -q -m "status: $HM - $drivers/12 lines, $cores cores, $records records, \$$spend, $timeouts timeouts" 2>/dev/null \
  && git push -q origin HEAD:backup-2026-07-28 2>/dev/null \
  && git push -q origin HEAD:myriad-cluster-and-tier-system 2>/dev/null \
  && echo "published $TS  ($HM, $cores cores, $records records)" \
  || echo "no change to publish at $TS"
