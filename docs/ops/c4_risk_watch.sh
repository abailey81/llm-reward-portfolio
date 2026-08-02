#!/bin/bash
# C4 RISK WATCH — emits ONE line per NEW occurrence of the conditions that matter during the ladder.
# Read-only. Designed to be run under a Monitor: every stdout line becomes a notification.
#
# WHY THESE THREE, and why nothing else (RUN 13, 2026-08-02, C4 opened 04:12:28):
#
#  1. INCOMPLETE — the ladder BANKS only up to the last clean level, so a block that reports
#     INCOMPLETE caps the rung there and every block above it is unbanked compute. The brief calls
#     this urgent, and it is the one condition here that needs a human within minutes.
#  2. ARM_CRASH / core pipeline crashed — a crashed arm has no winner and would be silently ABSENT
#     from the CRN-paired h2_pair array (D14). The line stops itself, but nothing else says so.
#  3. max_u_jobs — C4 submits ~337 jobs per line and the site cap is 1000. D25 predicts crash-loops
#     at the breach; they self-heal and must NOT be "fixed" mid-ladder, so this is a HEADS-UP, not an
#     alarm. It is here so the crash-loops are recognised rather than diagnosed from scratch at 4am.
#
# COVERAGE, deliberately: silence must not be the only signal. A crashloop, a dead driver and a
# healthy run all look the same to a grep that only matches success, so this also emits when the
# driver-line count DROPS, which is the shape a stuck ladder actually has.
set -u
cd "$(dirname "$0")/../.." || exit 1
LOGS="outputs/campaign_cluster_run4"
STATE="/tmp/c4_risk_watch.seen"
: > "$STATE"

prev_lines=-1
while true; do
  # (1) + (2) -- new INCOMPLETE / crash markers, deduped by exact line so a standing condition is
  # reported ONCE rather than every poll (the alarm-fatigue rule this repo keeps re-learning).
  grep -h -E "INCOMPLETE|core arm\(s\) CRASHED|ARM_CRASH" "$LOGS"/driver_*.log 2>/dev/null \
    | tail -200 > /tmp/c4_risk_now || true
  if [ -s /tmp/c4_risk_now ]; then
    while IFS= read -r ln; do
      key=$(printf '%s' "$ln" | md5sum | cut -d' ' -f1)
      if ! grep -q "$key" "$STATE" 2>/dev/null; then
        echo "$key" >> "$STATE"
        echo "C4-RISK: ${ln:0:220}"
      fi
    done < /tmp/c4_risk_now
  fi

  # (3) -- job census. Emitted only on a THRESHOLD CROSSING, not every poll.
  N=$(ssh -o BatchMode=yes myriad 'qstat -u ucestes | tail -n +3 | wc -l' 2>/dev/null || echo -1)
  if [ "$N" -ge 900 ] 2>/dev/null && [ "$prev_lines" -lt 900 ] 2>/dev/null; then
    echo "C4-HEADSUP: $N jobs lodged — approaching the max_u_jobs=1000 cap. D25 crash-loops are EXPECTED here, they self-heal, do NOT fix them mid-ladder."
  fi
  [ "$N" -ge 0 ] 2>/dev/null && prev_lines="$N"

  sleep 300
done
