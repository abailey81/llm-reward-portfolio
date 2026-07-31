#!/usr/bin/env bash
# THE 2-MINUTE CADENCE, MACHINE-ENFORCED.
#
# WHY THIS EXISTS (2026-07-31). Tamer's one named complaint about the previous session was that it
# did not monitor constantly, and the answer at handover was to make the sweep ONE command so there
# would be no friction excuse. That was necessary and not sufficient: on 2026-07-31 the RUN 7 session
# still let a 01:20 -> 03:38 gap open (2 h 18 m, 46 records unwatched) while doing deep work, because
# a cadence that depends on an agent remembering to type a command between long tool calls is not a
# cadence -- it is an intention.
#
# publish_status.sh already solved this shape: a detached loop pushes the phone page every 5 minutes
# whether anyone is paying attention or not, and it survived two session handovers. This does the
# same for the monitoring cycle. The agent's job becomes READING the log, not producing it.
#
# WHAT IT DOES. Runs docs/ops/cycle.py every INTERVAL seconds, forever:
#   * every iteration appends one line to docs/ops/watch/CYCLE_LOG.md (cycle.py's own behaviour)
#   * every SSH_EVERY-th iteration also reads cores/jobs off Myriad -- NOT every cycle, because the
#     login node is shared and a 2-minute ssh poll is rude for a number that moves on the hour
#   * anything that is not OK is appended to docs/ops/watch/ALERTS.txt, which is the one file to
#     check after being away: it is empty when nothing has needed a human
#
# It NEVER mutates the campaign, never commits, and never pushes. Safe to run alongside a session
# that is also running cycle.py by hand (STATE.json is rewritten whole, so the worst case is one
# cycle's delta being attributed to the other caller).
#
#   bash docs/ops/cycle_loop.sh                 # foreground, ctrl-C to stop
#   INTERVAL=120 bash docs/ops/cycle_loop.sh    # explicit
#
# Launch it DETACHED so it outlives the session that started it. Stop it by killing its pid.

set -u

cd "$(dirname "$0")/../.." || exit 1

INTERVAL="${INTERVAL:-120}"     # seconds between cycles -- Tamer's standing order is 2 minutes
SSH_EVERY="${SSH_EVERY:-10}"    # read the cluster every Nth cycle (10 x 120 s = 20 min)

WATCH="docs/ops/watch"
ALERTS="$WATCH/ALERTS.txt"
mkdir -p "$WATCH"

i=0
while true; do
    i=$((i + 1))
    if [ $((i % SSH_EVERY)) -eq 0 ]; then
        out=$(python docs/ops/cycle.py --ssh --note "auto-cycle" 2>&1)
    else
        out=$(python docs/ops/cycle.py --note "auto-cycle" 2>&1)
    fi
    rc=$?

    # rc 0 = nothing needs a human. Anything else is recorded where it will be SEEN, with the full
    # cycle output attached -- a bare "RED at 03:38" costs another investigation to interpret.
    if [ "$rc" -ne 0 ]; then
        {
            printf '\n===== %s  rc=%s =====\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$rc"
            printf '%s\n' "$out"
        } >> "$ALERTS"
    fi

    sleep "$INTERVAL"
done
