#!/usr/bin/env bash
# CAMPAIGN MONITOR (2026-07-18) — the proven v3 state-class pattern, pointed at the campaign.
# Run from the repo root in Git Bash, backgrounded, at launch (runbook §5a):
#   bash scripts/campaign_monitor.sh
# Emits a line ONLY on change (state-class transitions for c1_*/h3ss_* jobs, local record
# counts for the campaign roots, any Eqw, driver-heartbeat staleness >15 min). Quiet = healthy.

PREV=""
while true; do
  QS=$(ssh myriad "qstat 2>/dev/null" 2>/dev/null | awk '/c1_|h3ss_/ {print $1, $3, $5}' | sort | uniq | tr '\n' ';')
  EQW=$(printf '%s' "$QS" | grep -c "Eqw")
  NSEARCH=$(find outputs/campaign_cluster/search -name record.json 2>/dev/null | wc -l)
  NTEST=$(find outputs/campaign_cluster/test -name record.json 2>/dev/null | wc -l)
  STALE=""
  NOW=$(date +%s)
  for hb in outputs/campaign_cluster/driver_status/*.json; do
    [ -f "$hb" ] || continue
    TS=$(python -c "import json,sys;print(int(float(json.load(open(sys.argv[1])).get('ts',0))))" "$hb" 2>/dev/null || echo 0)
    if [ "$TS" -gt 0 ] && [ $((NOW - TS)) -gt 900 ]; then
      STALE="$STALE $(basename "$hb" .json):$(( (NOW - TS) / 60 ))m"
    fi
  done
  STATE="search=$NSEARCH test=$NTEST eqw=$EQW stale=${STALE:-none} | $QS"
  if [ "$STATE" != "$PREV" ]; then
    echo "$(date '+%m-%d %H:%M') | search=$NSEARCH test=$NTEST eqw=$EQW stale=${STALE:-none}"
    # full queue detail only when the queue-state part changed
    if [ "${STATE#*|}" != "${PREV#*|}" ]; then
      printf '%s' "$QS" | tr ';' '\n' | sed 's/^/    /' | head -40
    fi
    PREV="$STATE"
  fi
  sleep 300
done
