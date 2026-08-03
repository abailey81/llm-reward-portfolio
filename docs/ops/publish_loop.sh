#!/bin/bash
# Re-armed 2026-07-29 by the successor session. Runs the proven publisher on a fixed cadence.
# Silent by design: it must not spam the session with notifications. Its evidence is the
# git history of docs/RUN4_STATUS.md and this log.
#
# CADENCE: 60 s (Tamer, 2026-08-03 — "change the run4 live status updates from every 5 minutes
# to every 1 minute"). Was 300 s. The publisher itself takes ~40-70 s when it has to reach the
# cluster for the core count, so the OBSERVED spacing will be roughly 100-130 s rather than 60 —
# `sleep` is the gap BETWEEN runs, not the period. Lowering it further would simply make the
# loop back-to-back; it would not publish faster.
#
# ⚠ EDITING THIS FILE DOES NOT CHANGE A RUNNING LOOP. bash parses the whole `while ... done`
# compound command once and then executes it from memory, so an in-place edit is inert until the
# loop is restarted. Change the value AND restart, or the cadence silently stays what it was.
set -u
PUB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/publish_status.sh"
LOG="${PUBLISH_LOG:-/tmp/publish_loop.log}"   # override with PUBLISH_LOG=<path>
INTERVAL="${PUBLISH_INTERVAL_SECS:-60}"       # override without editing: PUBLISH_INTERVAL_SECS=30
while true; do
  bash "$PUB" >>"$LOG" 2>&1 || echo "publish attempt failed $(date -u +%H:%M:%S)" >>"$LOG"
  sleep "$INTERVAL"
done
