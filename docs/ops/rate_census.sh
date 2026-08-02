#!/bin/bash
# TRAINING-RATE CENSUS (read-only). Runs ON MYRIAD; pipe it in with: ssh myriad 'bash -s' < this
#
# WHY THIS INSTRUMENT EXISTS (2026-08-02, RUN 13). The core-count question ("we are at a very low
# amount of cores") is the WRONG metric twice over. The first correction (RUN 12) was that cores !=
# concurrent trainings. The second, found here, is that a training SLOT is not a training RATE: job
# 62810 ran at 3.5 steps/s while its own sibling p01 -- same generation, same arm, same node family
# -- ran at 28.7 steps/s and finished in 3.87 h. An 8x spread inside one generation means the honest
# throughput denominator is STEPS/S SUMMED OVER LIVE TRAININGS, not slots and not job counts.
#
# It reads each live job's per-task `.o` file, which the trainer appends a
#   [train] step S/T elapsed Es rate R steps/s
# line to every 5,000 steps. Nothing is written; nothing is submitted; no record is read.
#
# THREE VALUES, NOT TWO (the register's own rule): a task dir with no `.o` is LAUNCHED-not-started;
# an `.o` that exists but carries no [train] line is STARTED-not-training (import/setup); only a
# task with a [train] line is measurable. All three are reported separately and never merged.
set -u

WALL_SECS=54000          # h_rt on every campaign job; the kill boundary
LOGROOT="$HOME/Scratch/llmrp4/logs"

qstat -u ucestes | tail -n +3 | awk '$5=="r" {print $1, $3}' > /tmp/rc_running.txt || exit 1
echo "running_jobs=$(wc -l < /tmp/rc_running.txt)"
echo
printf '%-8s %-46s %8s %10s %12s %9s %s\n' JOBID NAME STEP/K RATE ELAPSED_H ETA_H VERDICT

TOT_RATE=0; N_MEAS=0; N_STARTED=0; N_LAUNCHED=0; N_DOOMED=0
while read -r JID NM; do
  # The job NAME is the log directory name; array tasks land as <dir>/<task>.o
  D="$LOGROOT/$NM"
  if [ ! -d "$D" ]; then
    # qstat truncates the name to 10 chars, so resolve the full name from the job record.
    FULL=$(qstat -j "$JID" 2>/dev/null | awk '/^job_name:/ {print $2; exit}')
    [ -n "${FULL:-}" ] && D="$LOGROOT/$FULL"
  fi
  [ -d "$D" ] || { N_LAUNCHED=$((N_LAUNCHED+1)); continue; }
  FOUND=0
  for O in "$D"/*.o; do
    [ -e "$O" ] || continue
    FOUND=1
    LINE=$(grep '^\[train\] step' "$O" 2>/dev/null | tail -1)
    if [ -z "$LINE" ]; then
      N_STARTED=$((N_STARTED+1))
      printf '%-8s %-46s %8s %10s %12s %9s %s\n' "$JID" "${FULL:-$NM}" - - - - "STARTED_NO_TRAIN_LINE"
      continue
    fi
    S=$(echo "$LINE" | awk '{print $3}' | cut -d/ -f1)
    T=$(echo "$LINE" | awk '{print $3}' | cut -d/ -f2)
    E=$(echo "$LINE" | awk '{print $5}' | tr -d 's')
    R=$(echo "$LINE" | awk '{print $7}')
    REM=$((T - S))
    ETA=$(echo "scale=2; $REM / ($R * 3600)" | bc 2>/dev/null)
    EH=$(echo "scale=2; $E / 3600" | bc 2>/dev/null)
    LEFT=$(echo "scale=2; ($WALL_SECS - $E) / 3600" | bc 2>/dev/null)
    V=OK
    # DOOMED = at the CURRENT rate the remaining steps cannot fit in the remaining wall.
    if [ "$(echo "$ETA > $LEFT" | bc 2>/dev/null)" = "1" ]; then V="DOOMED(h_rt)"; N_DOOMED=$((N_DOOMED+1)); fi
    printf '%-8s %-46s %8s %10s %12s %9s %s\n' "$JID" "${FULL:-$NM}" "$((S/1000))/$((T/1000))" "$R" "$EH" "$ETA" "$V"
    TOT_RATE=$(echo "$TOT_RATE + $R" | bc)
    N_MEAS=$((N_MEAS+1))
  done
  [ "$FOUND" = 0 ] && N_LAUNCHED=$((N_LAUNCHED+1))
done < /tmp/rc_running.txt

echo
echo "measured_trainings=$N_MEAS  started_no_train_line=$N_STARTED  launched_no_o_file=$N_LAUNCHED"
echo "doomed_by_h_rt=$N_DOOMED"
echo "TOTAL_STEPS_PER_SEC=$TOT_RATE"
[ "$N_MEAS" -gt 0 ] && echo "MEAN_STEPS_PER_SEC=$(echo "scale=2; $TOT_RATE / $N_MEAS" | bc)"
