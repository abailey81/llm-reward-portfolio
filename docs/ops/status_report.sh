#!/bin/bash
# RUN 4 operational dashboard, LOCAL half - one command, the same numbers every time.
# Pair with: Send-Remote.ps1 -ScriptPath remote_status.sh  (the cluster half).
#
# Tamer asked to be kept updated on timeline / cores / jobs in progress, so this exists to make
# every update consistent rather than whatever I happened to query that hour.
#
# All times UTC. Driver logs are LOCAL (BST = UTC+1) - that ambiguity already cost this project one
# retracted analysis, so nothing here reads a log timestamp for arithmetic.
ROOT="${1:-outputs/campaign_cluster_run4}"
REPO=/c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
cd "$REPO" || exit 1

echo "############ RUN 4 STATUS  $(date -u +'%Y-%m-%d %H:%M UTC') ############"

python - <<'PY'
import datetime as dt
LAUNCH = dt.datetime(2026, 7, 28, 21, 8, 58)   # supervisors up, UTC
STOP   = dt.datetime(2026, 8, 27)              # R109 exogenous stop
now = dt.datetime.utcnow()
el = now - LAUNCH
h, rem = divmod(int(el.total_seconds()), 3600)
legs = LAUNCH + dt.timedelta(seconds=3620)
print(f"TIMELINE   T+{h}h{rem//60:02d}m    launched {LAUNCH:%Y-%m-%d %H:%M} UTC")
print(f"           legs+h3 wake {legs:%H:%M} UTC  [{'DONE' if now>legs else 'pending'}]")
print(f"           canary ETA   {LAUNCH+dt.timedelta(hours=8):%m-%d %H:%M}-"
      f"{LAUNCH+dt.timedelta(hours=10):%m-%d %H:%M} UTC  (gates ALL Opus spend)")
print(f"           exogenous stop {STOP:%Y-%m-%d}  ->  {(STOP-now).days} days remaining")
PY

echo
echo "---- PROGRESS (local mirror) ----"
echo "records archived   : $(find "$ROOT" -name record.json 2>/dev/null | wc -l)"
echo "rewards authored   : $(find "$ROOT" -name reward.py 2>/dev/null | wc -l)"
echo "driver logs (lines): $(ls "$ROOT"/driver_*.log 2>/dev/null | wc -l) of 12"
echo "supervisor logs    : $(ls "$ROOT"/supervisor_*.log 2>/dev/null | wc -l) of 12"
echo "batches in flight  : $(ls "$ROOT"/driver_status/*.json 2>/dev/null | wc -l)"
echo "epilogue rows      : $(cat "$ROOT"/ledger/*.jsonl 2>/dev/null | wc -l)"

echo
echo "---- SPEND (ledger = an ESTIMATE, never billed spend) ----"
tot=0
for f in "$ROOT"/spend_ledger_*.jsonl; do
    [ -e "$f" ] || { echo "  none yet (correct until the legs wake)"; break; }
    n=$(wc -l < "$f")
    c=$(python -c "
import json,sys
s=0.0
for line in open(sys.argv[1],encoding='utf-8',errors='replace'):
    line=line.strip()
    if line:
        try: s+=float(json.loads(line).get('cost_usd') or 0)
        except Exception: pass
print(f'{s:.4f}')" "$f")
    printf '  %-30s %4s calls  $%s\n' "$(basename "$f" .jsonl)" "$n" "$c"
done

echo
echo "---- GUARDS ----"
python scripts/campaign_guards.py "$ROOT" all 2>&1 | grep -E '^\[|CRITICAL|FOREIGN|\*\*\*|foreign=|timeout_events=|levels='
echo "guards_rc=${PIPESTATUS[0]}"
