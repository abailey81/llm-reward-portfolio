#!/bin/bash
# RATE vs NODE LOAD, split by THREADS-PER-TRAINING. Read-only. ssh myriad 'bash -s' < this
#
# THE HYPOTHESIS UNDER TEST (RUN 13, 2026-08-02). Live rates split cleanly by lane:
#   SEARCH  (`threads=8`, pack 1)  ranges 3.5 .. 31.9 steps/s  -- a 9x spread
#   TEST    (`threads=1`, pack 8)  ranges 11.6 .. 15.7 steps/s -- essentially flat
# Same nodes, same CPU model, same job shape (`-pe smp 8`). If the spread is NODE CONTENTION, then
# an 8-thread training needs 8 cores free SIMULTANEOUSLY and degrades catastrophically on a loaded
# node, while a 1-thread training does not care -- so rate should fall with the host's load in the
# search lane and be FLAT in the test lane. If instead the spread is the authored reward's own
# compute cost, rate and load will be uncorrelated in BOTH lanes.
#
# The two lanes are each other's CONTROL. That is the point of measuring them together: a bare
# "search jobs vary a lot" observation has no comparator and proves nothing.
set -u
LOGROOT="$HOME/Scratch/llmrp4/logs"

qhost 2>/dev/null | awk 'NR>3 && $1!="global" {print $1, $7}' > /tmp/rl_load.txt

printf '%-46s %-18s %7s %8s %7s\n' JOB HOST LOAD RATE LANE
qstat -u ucestes | tail -n +3 | awk '$5=="r" {print $1, $8}' | while read -r JID Q; do
  H=$(echo "$Q" | sed 's/.*@//; s/\..*//')
  L=$(awk -v h="$H" '$1==h {print $2; exit}' /tmp/rl_load.txt)
  NM=$(qstat -j "$JID" 2>/dev/null | awk '/^job_name:/ {print $2; exit}')
  [ -n "${NM:-}" ] || continue
  D="$LOGROOT/$NM"
  [ -d "$D" ] || continue
  for O in "$D"/*.o; do
    [ -e "$O" ] || continue
    P=$(grep -c 'step 5000/' "$O" 2>/dev/null)
    [ "${P:-0}" -gt 0 ] || continue
    # INSTANTANEOUS rate over the last two heartbeats of ONE stream, not the cumulative average:
    # a job that started fast and slowed reports a flattering cumulative number, and the cumulative
    # number is exactly what made 62810 look merely "slow" rather than already stalled.
    MED=$(grep '^\[train\] step' "$O" | tail -"$P" | awk '{print $7}' | sort -n | awk '{a[NR]=$1} END {if(NR) print (NR%2)?a[(NR+1)/2]:(a[NR/2]+a[NR/2+1])/2}')
    if [ "$P" -eq 1 ]; then LANE="search_thr8"; else LANE="test_thr1"; fi
    printf '%-46s %-18s %7s %8s %7s\n' "$NM" "$H" "${L:-?}" "$MED" "$LANE"
  done
done
