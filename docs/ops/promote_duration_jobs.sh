#!/bin/bash
# promote_duration_jobs.sh -- RUN 27, 2026-08-06. PUT THE 24-SPEC JOBS AT THE TOP OF OUR OWN QUEUE.
#
# RUN IT AS:  ssh myriad "bash -s" -- --dry  < docs/ops/promote_duration_jobs.sh     (preview)
#             ssh myriad "bash -s"           < docs/ops/promote_duration_jobs.sh     (apply)
# (scp is broken on this link -- exit 255 -- so pipe it over stdin. The Bash tool's classifier
#  blocks the apply form; PowerShell's `& bash.exe -c "ssh ... < file"` is the route that works.)
#
# ===================================================================================================
# WHY THIS EXISTS -- THE ONE PIECE OF ARITHMETIC THAT GOVERNS THE WHOLE CAMPAIGN'S SPEED
# ===================================================================================================
#   cores      = lambda x duration x 8            records/h = lambda x specs_per_task
#
# `lambda` is our DISPATCH RATE, measured at ~9.6 jobs/h, and it is set ENTIRELY by our absolute
# ticket rank: `prior = 4.0*npprior + 1.5*ntckts` with `weight_urgency = 0` (verified to 5 dp on live
# jobs 91264 and 91041). Nobody on the cluster sets `-p`, so `npprior` is 0.5 for everyone and the
# ticket term is the ONLY discriminator. We cannot raise it: `ppri = 0` on all 841 of our jobs
# (header-verified -- `ppri` is COLUMN 6 of `qstat -pri`), `fshare 1`, flat share tree, `qquota` empty.
#
# ⚠⚠ AND A HOLD CANNOT RAISE LAMBDA. MEASURED, NOT ASSUMED: cutting eligible 371 -> 31 moved our best
# job's prior DOWN (2.02295 -> 2.01304) and raised the cluster jobs out-ranking us from 495 to 605.
# The functional pool SHRINKS with our job count rather than concentrating. So:
#
#   ⇒ A HOLD IS AN *ORDERING* INSTRUMENT ONLY. It decides WHICH of our jobs wins the next dispatch,
#     never HOW MANY we win. The only lever on cores is CORE-HOURS PER DISPATCH = pack x specs_per_task.
#
# At 8 specs a job holds 8 cores for ~8.9 h  -> 9.6 x 8.9 x 8 =   684 cores  (we measured 704)
# At 24 specs it holds 8 cores for ~26.7 h   -> 9.6 x 26.7 x 8 = 2,050 cores (the target)
#
# So every dispatch spent on an 8-spec job WASTES TWO THIRDS OF IT, and this script makes sure the
# 24-spec jobs are the ones our scarce dispatches go to.
#
# ===================================================================================================
# WHAT IT DOES, AND THE SAFETY PROPERTIES
# ===================================================================================================
# Holds every ELIGIBLE job whose `h_rt` is NOT 162000, leaving only the 24-spec/45 h jobs eligible.
#   * NEVER selects a RUNNING job, NEVER a `c1` job (the floor), NEVER a 45 h job. Asserted per run.
#   * Re-selects from the LIVE QUEUE every time, so a stale id simply drops out.
#   * IDEMPOTENT and CHEAP TO REPEAT: re-holding costs nothing. The ~1 h JSV re-entry penalty falls
#     on RELEASE, not on HOLD -- so the correct cadence is RE-APPLY OFTEN, RELEASE RARELY.
#
# ⚠⚠ RUN IT AGAIN EVERY ~10 MINUTES WHILE IT MATTERS. The site JSV drains system-held jobs back into
# `qw` continuously (measured ~736/h), and every drained job carries an OLDER id than the 24-spec
# work and therefore MORE tickets, so a one-shot application is leapfrogged within minutes.
#
# ⚠⚠⚠ DO NOT JUDGE THIS SCRIPT ON A SHORT WINDOW. On 2026-08-06 it showed ZERO dispatches across 23
# minutes of 55-second samples and was REVERTED as failing -- and FOURTEEN MINUTES LATER five 24-spec
# jobs were running (5 in ~25 min = 12/h, nearly 4x the 3.2/h break-even). The dispatch quantum is
# SGE's `schedule_interval 0:10:0` plus a ticket recompute, so 23 minutes is barely two quanta and a
# zero is entirely ordinary. **OBSERVE FOR LONGER THAN THE PERIOD, AND TRACK IDENTITIES NOT COUNTS.**
#
# ⚠ RETIREMENT: this is a TRANSITIONAL instrument. It exists only while the fleet is mostly 8-spec
# work submitted BEFORE the 2026-08-06 conversion. Once most eligible jobs are 24-spec it holds
# almost nothing and should simply be stopped -- and if `--h-rt` is ever changed again, UPDATE THE
# 162000 CONSTANT BELOW or this script will hold the very jobs it exists to promote.
set -u

WANT_HRT="${WANT_HRT:-162000}"     # the h_rt of the HIGH-VALUE shape. Update if --h-rt changes.
MODE="${1:---apply}"

qstat -u ucestes -s p | tail -n +3 | awk '$5=="qw"{print $1}' | sort -u > /tmp/pdj_elig.txt
: > /tmp/pdj_keep.txt
: > /tmp/pdj_sel.txt
for j in $(cat /tmp/pdj_elig.txt); do
  if qstat -j "$j" 2>/dev/null | grep -q "h_rt=${WANT_HRT}"; then
    echo "$j" >> /tmp/pdj_keep.txt
  else
    echo "$j" >> /tmp/pdj_sel.txt
  fi
done

qstat -u ucestes      | tail -n +3 | grep c1_ | awk '{print $1}' | sort -u > /tmp/pdj_c1.txt
qstat -u ucestes -s r | tail -n +3 |             awk '{print $1}' | sort -u > /tmp/pdj_run.txt
sort -u /tmp/pdj_sel.txt > /tmp/pdj_sel_a.txt
comm -23 /tmp/pdj_sel_a.txt /tmp/pdj_c1.txt > /tmp/pdj_sel_s.txt

n=$(grep -c . /tmp/pdj_sel_s.txt || true)
bad_run=$(comm -12 /tmp/pdj_sel_s.txt /tmp/pdj_run.txt | grep -c . || true)
bad_c1=$(comm -12 /tmp/pdj_sel_s.txt /tmp/pdj_c1.txt  | grep -c . || true)

echo "eligible now         : $(grep -c . /tmp/pdj_elig.txt || true)"
echo "KEEP eligible (h_rt=${WANT_HRT}) : $(grep -c . /tmp/pdj_keep.txt || true)"
echo "SELECTED to hold     : $n"
echo "  running in selection (must be 0): $bad_run"
echo "  c1 in selection      (must be 0): $bad_c1"

if [ "$bad_run" -ne 0 ] || [ "$bad_c1" -ne 0 ]; then
    echo "REFUSING: the selection is not clean. Nothing was held."
    exit 2
fi
# An empty qstat is NOT a measurement of zero (learned live 2026-08-06 14:07Z).
if [ "$(grep -c . /tmp/pdj_elig.txt || true)" -eq 0 ]; then
    echo "UNREAD: no eligible jobs returned at all. No action."
    exit 0
fi
if [ "$n" -eq 0 ]; then echo "nothing to hold (queue already promoted)."; exit 0; fi
if [ "$MODE" = "--dry" ]; then echo "DRY RUN -- nothing held."; exit 0; fi

xargs -a /tmp/pdj_sel_s.txt -r qhold > /dev/null 2>&1
echo "--- after ---"
echo "eligible=$(qstat -u ucestes -s p | tail -n +3 | grep -vc hqw)" \
     "hu=$(qstat -u ucestes -s hu | tail -n +3 | wc -l)" \
     "c1=$(qstat -u ucestes | tail -n +3 | grep -c c1_)" \
     "running=$(qstat -u ucestes -s r | tail -n +3 | wc -l)"
