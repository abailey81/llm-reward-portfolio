#!/bin/bash
# Write docs/RUN4_STATUS.md and push it, so Tamer can read live progress from his phone via GitHub
# without the session having to be asked. Also pulls first, so any instruction he wrote into
# docs/REMOTE_CONTROL.md arrives before the push (and cannot be clobbered by it).
set -u
REPO=/c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
ROOT=outputs/campaign_cluster_run4
cd "$REPO" || exit 1

git pull --rebase --quiet origin backup-2026-07-28 2>/dev/null || git pull --rebase --quiet 2>/dev/null || true

TS=$(date -u +'%Y-%m-%d %H:%M UTC')
LAUNCH=1785272938   # 2026-07-28 21:08:58 UTC, supervisors up
EL=$(( ($(date -u +%s) - LAUNCH) / 60 ))

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

# cluster side (best effort - a failed ssh must not stop the status publish)
CL=$(ssh -o BatchMode=yes -o ConnectTimeout=20 myriad 'Q=$(qstat -u ucestes | tail -n +3); echo "jobs=$(echo "$Q" | grep -c .)"; echo "run=$(echo "$Q" | awk "\$5==\"r\"" | grep -c .)"; echo "cores=$(echo "$Q" | awk "\$5==\"r\" {s+=\$9} END {print s+0}")"' 2>/dev/null)
jobs=$(echo "$CL"  | grep '^jobs='  | cut -d= -f2); jobs=${jobs:-?}
run=$(echo "$CL"   | grep '^run='   | cut -d= -f2); run=${run:-?}
cores=$(echo "$CL" | grep '^cores=' | cut -d= -f2); cores=${cores:-?}

cat > docs/RUN4_STATUS.md <<EOF
# RUN 4 -- LIVE STATUS

**Auto-generated $TS -- T+$((EL/60))h$(printf '%02d' $((EL%60)))m.** Refreshed by the live session and
pushed to GitHub, so it is readable from a phone. To send an instruction back, edit
[docs/REMOTE_CONTROL.md](REMOTE_CONTROL.md).

| | |
|---|---|
| elapsed | **T+$((EL/60))h$(printf '%02d' $((EL%60)))m** (launched 2026-07-28 21:08 UTC) |
| lines up | **$drivers / 12** |
| cluster jobs | **$jobs** ($run running) |
| **cores computing** | **$cores** |
| records archived | **$records** |
| LLM calls | $calls |
| spend (ledger estimate) | **\$$spend** |
| transport timeouts | **$timeouts** |
| guards | $( [ "$guards" -eq 0 ] && echo '**all green**' || echo "**RC=$guards -- SEE THE RECORD**" ) |

## What to expect next

* first records land when the C0 canary's ~8 h trainings finish (**~05:08-07:08 UTC, 29 Jul**)
* the canary clearing is what releases the core line's Opus authoring -- core spend stays \$0 until then
* exogenous stop **2026-08-27**

## If something looks wrong

The campaign is independent of the Claude session: supervisors relaunch, the watchdog revives dead
lines every 300 s, the sentinel watches health. **Stop lever:** create the file
\`outputs\\campaign_cluster_run4\\STOP_CAMPAIGN\` (or ask via REMOTE_CONTROL.md).

Full narrative: [CAMPAIGN_EXECUTION_RECORD.md](CAMPAIGN_EXECUTION_RECORD.md) section 22-section 23.
EOF

git add docs/RUN4_STATUS.md
git commit -q -m "status: T+$((EL/60))h$(printf '%02d' $((EL%60)))m - $drivers/12 lines, $cores cores, $records records, \$$spend, $timeouts timeouts" 2>/dev/null \
  && git push -q origin HEAD:backup-2026-07-28 2>/dev/null \
  && git push -q origin HEAD:myriad-cluster-and-tier-system 2>/dev/null \
  && echo "published $TS  (T+$((EL/60))h$(printf '%02d' $((EL%60)))m, $cores cores, $records records)" \
  || echo "no change to publish at $TS"
