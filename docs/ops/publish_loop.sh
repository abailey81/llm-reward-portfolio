#!/bin/bash
# Re-armed 2026-07-29 by the successor session. Runs the proven publisher every 5 minutes.
# Silent by design: it must not spam the session with notifications. Its evidence is the
# git history of docs/RUN4_STATUS.md and this log.
set -u
PUB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/publish_status.sh"
LOG="${PUBLISH_LOG:-/tmp/publish_loop.log}"   # override with PUBLISH_LOG=<path>
while true; do
  bash "$PUB" >>"$LOG" 2>&1 || echo "publish attempt failed $(date -u +%H:%M:%S)" >>"$LOG"
  sleep 300
done
