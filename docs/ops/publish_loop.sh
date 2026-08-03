#!/bin/bash
# Re-armed 2026-07-29 by the successor session. Runs the proven publisher on a fixed cadence.
# Silent by design: it must not spam the session with notifications. Its evidence is the
# git history of docs/RUN4_STATUS.md and this log.
#
# CADENCE (Tamer, 2026-08-03: "report every 1 minute"). `sleep` is the gap BETWEEN runs, not the
# period, and ONE publish was MEASURED at 61.6 s -- it is dominated by the ssh that fetches the
# live core count from a busy scheduler. So the achievable period is ~62 s no matter what, and a
# 5 s gap lands the observed spacing at ~67 s, which is as close to one minute as the publisher
# can physically go. Setting this to 0 would gain ~5 s and make the loop back-to-back, keeping an
# ssh to the login node permanently open -- not worth it while we are under a usage penalty.
# History: 300 s -> 60 s -> 5 s. Making this smaller does NOT publish faster; only making
# publish_status.sh itself faster would.
#
# ⚠ EDITING THIS FILE DOES NOT CHANGE A RUNNING LOOP. bash parses the whole `while ... done`
# compound command once and then executes it from memory, so an in-place edit is inert until the
# loop is restarted. Change the value AND restart, or the cadence silently stays what it was.
set -u
PUB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/publish_status.sh"
LOG="${PUBLISH_LOG:-/tmp/publish_loop.log}"   # override with PUBLISH_LOG=<path>
INTERVAL="${PUBLISH_INTERVAL_SECS:-5}"       # override without editing: PUBLISH_INTERVAL_SECS=30
while true; do
  bash "$PUB" >>"$LOG" 2>&1 || echo "publish attempt failed $(date -u +%H:%M:%S)" >>"$LOG"
  sleep "$INTERVAL"
done
