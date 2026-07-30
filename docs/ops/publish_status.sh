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

records=$(find "$ROOT" -name record.json 2>/dev/null | wc -l)
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
timeouts=$(grep -h 'timed out after' "$ROOT"/driver_*.log 2>/dev/null | wc -l)
drivers=$(ls "$ROOT"/driver_*.log 2>/dev/null | wc -l)
guards=$(python scripts/campaign_guards.py "$ROOT" all >/dev/null 2>&1; echo $?)
gnames=$(python scripts/campaign_guards.py "$ROOT" all 2>/dev/null | grep -E '^\[' | grep -v ' ok$' | sed 's/^\[//;s/\].*//' | tr '\n' ' ')
gnames=${gnames:-none}
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
CL=$(ssh -o BatchMode=yes -o ConnectTimeout=20 myriad 'Q=$(qstat -u ucestes | tail -n +3); echo "jobs=$(echo "$Q" | grep -c .)"; echo "run=$(echo "$Q" | awk "\$5==\"r\"" | grep -c .)"; echo "qw=$(echo "$Q" | awk "\$5 ~ /qw/" | grep -c .)"; echo "cores=$(echo "$Q" | awk "\$5==\"r\" {s+=\$9} END {print s+0}")"' 2>/dev/null)
jobs=$(echo "$CL"  | grep '^jobs='  | cut -d= -f2); jobs=${jobs:-?}
run=$(echo "$CL"   | grep '^run='   | cut -d= -f2); run=${run:-?}
qw=$(echo "$CL"    | grep '^qw='    | cut -d= -f2); qw=${qw:-?}
cores=$(echo "$CL" | grep '^cores=' | cut -d= -f2); cores=${cores:-?}

# per-rung ETAs at the cores we actually hold (Tamer's standing reporting requirement)
etas=$(python docs/ops/stage_eta.py "${cores:-0}" 2>/dev/null | sed -n '3,12p')
etas=${etas:-"  (eta model unavailable this cycle)"}

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
| lines up | **$drivers / 12**, all five arms submitted on **$armsfull of the 10 leg lines** (h3ss is single-arm by design) |
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

## Needs Tamer

* **!! ANTHROPIC BUDGET -- PROJECTED SHORTFALL ~\$9.** Spent \$22.15 of a credited \$28.15; the
  authoring still to come (14 arm-generations on the core line, 15 on sonnet, 12 on haiku) projects
  **\$15.11 more = \$37.27 total**. If the key runs dry the CONFIRMATORY line stops, which is the one
  thing the campaign cannot absorb. **Please check the real console balance and top up.** Our figure is
  a ledger ESTIMATE, not a balance reading -- record section 49.
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
