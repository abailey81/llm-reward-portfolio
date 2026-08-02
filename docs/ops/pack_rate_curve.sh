#!/bin/bash
# PACK-DEPTH vs PER-TRAINING RATE (read-only). ssh myriad 'bash -s' < this
#
# THE QUESTION IT ANSWERS. A test job packs P trainings onto 8 slots; a search job packs 1. Live
# rates are ~12.8 steps/s in test jobs and 3.5-31.8 steps/s in search jobs. Two rival explanations,
# and they imply OPPOSITE actions:
#   (A) CONTENTION -- packing P trainings onto 8 cores slows each one, so the packed test blocks are
#       paying a latency tax we could buy back with the free slots we are not using.
#   (B) REWARD COST -- the spread is the LLM-authored reward's own compute cost, which varies by
#       candidate, and packing is innocent. Then un-packing buys nothing and costs 8x the slots.
# The discriminator is WITHIN the test lane, where every training in a block runs the SAME frozen
# winner: if rate falls as P rises across blocks of the same arm, (A). If rate is flat in P, (B).
#
# Method: a job's `.o` interleaves its P streams; each stream announces itself once with
# "step 5000/", so counting that marker COUNTS THE TRAININGS -- it does not assume the pack flag.
# The rate reported is the MEDIAN of the last P heartbeat lines, so one stream's stall cannot set it.
set -u
LOGROOT="$HOME/Scratch/llmrp4/logs"

printf '%-46s %6s %8s %10s\n' JOB PACK MED_RATE LANE
qstat -u ucestes | tail -n +3 | awk '$5=="r" {print $1}' | while read -r JID; do
  NM=$(qstat -j "$JID" 2>/dev/null | awk '/^job_name:/ {print $2; exit}')
  [ -n "${NM:-}" ] || continue
  D="$LOGROOT/$NM"
  [ -d "$D" ] || continue
  for O in "$D"/*.o; do
    [ -e "$O" ] || continue
    P=$(grep -c 'step 5000/' "$O" 2>/dev/null)
    [ "${P:-0}" -gt 0 ] || continue
    MED=$(grep '^\[train\] step' "$O" | tail -"$P" | awk '{print $7}' | sort -n | awk '{a[NR]=$1} END {if(NR) print (NR%2)?a[(NR+1)/2]:(a[NR/2]+a[NR/2+1])/2}')
    case "$NM" in
      *_test*|*sweep*) LANE=test ;;
      *) LANE=search ;;
    esac
    printf '%-46s %6s %8s %10s\n' "$NM" "$P" "$MED" "$LANE"
  done
done
