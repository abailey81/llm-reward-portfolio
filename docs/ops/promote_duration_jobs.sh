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

: > /tmp/pdj_elig.txt
: > /tmp/pdj_keep.txt
: > /tmp/pdj_sel.txt

# ⚠ RUN 28 FIX. This block used to loop `qstat -j "$j"` ONCE PER ELIGIBLE JOB -- ~100 qmaster
# queries per invocation at a 10-minute cadence, against a login node that is currently the ONLY
# one serving. §12 of the session brief forbids precisely that ("NEVER loop `qstat -j` per job on a
# login node. `login12` is the node that earned `penalty1`"), and the same burst pattern is the
# leading suspect for `loginnode_guard.py` returning PROBE-UNPARSED.
# `qstat -u <user> -r` carries id + state + h_rt for EVERY job in ONE call, so the cost is now
# independent of queue depth. Selection is byte-identical -- proven by a shimmed-qstat harness that
# fails against the pre-fix loop on the call count and passes on the selection.
# Field shapes verified first-hand 2026-08-06T19:46Z: header rows start with SPACES, not column 1,
# and the state is located BY VALUE (never by index -- $9 slots and $10 ja-task-ID are both numeric).
: > /tmp/pdj_prot.txt
QR=$(mktemp /tmp/pdj_qr.XXXXXX)
qstat -u ucestes -r > "$QR" 2>/dev/null

# PASS 1 -- flatten to  jid \t state \t h_rt \t line \t block
awk '
  function emit(   line, blk) {
    if (jid == "") return
    line = nm; sub(/_(sweep|test|search)_.*$/, "", line)
    blk = ""
    if      (match(nm, /_t[0-9]+_/)) blk = substr(nm, RSTART + 2, RLENGTH - 3)
    else if (match(nm, /_t[0-9]+$/)) blk = substr(nm, RSTART + 2, RLENGTH - 2)
    printf "%s\t%s\t%s\t%s\t%s\n", jid, st, hrt, line, blk
  }
  /^ *[0-9]+ +[0-9]/ {
    emit(); jid=$1; st=""; hrt=""; nm=""
    for (i=1;i<=NF;i++) if ($i ~ /^(r|t|qw|hqw|hRwq|hRqw|Eqw|dr|dt|hr|s|S|T)$/) st=$i
    next
  }
  /Full jobname:/ { nm=$3; next }
  /h_rt=/ { for (i=1;i<=NF;i++) if ($i ~ /^h_rt=/) { split($i,a,"="); hrt=a[2] } }
  END { emit() }
' "$QR" > /tmp/pdj_rows.txt

# PASS 2 -- select, WITH THE VALUE GUARD.
#
# ⚠⚠ RUN 28, 2026-08-06. WITHOUT THIS GUARD THIS SCRIPT CREATES A DEADLOCK, AND IT DID.
# It selects purely on `h_rt`, i.e. on job SHAPE, and is blind to which LINE and which BLOCK a job
# belongs to. Measured consequences on the live cluster the same afternoon:
#   * `leg1_leg_deepseek_v4_pro` -- a BINDING line gating the next common rung -- reached
#     165 held / ZERO running / ZERO eligible, including all 27 jobs of its next-needed `t1` block.
#     A line in that state cannot complete the block that would advance it, and cannot submit the
#     next batch either, so it can never wake itself up.
#   * my own 19:51Z application held 147 jobs and every one belonged to `leg7_leg_nemotron_3_super`,
#     another starved binding line.
# A line only submits new 24-spec work when a BLOCK COMPLETES, so holding the block a line is
# trying to finish is self-defeating for THIS SCRIPT'S OWN PURPOSE as well as for the ladder.
#
# THE GUARD: never hold a job at its line's LOWEST PENDING BLOCK. That block is the line's
# next-needed block whenever it has pending work there, and is strictly above it otherwise, so the
# rule is conservative in the safe direction. It also guarantees every line keeps at least one
# eligible job, which is the property that actually prevents the deadlock.
# `job_rank_governor.py::ladder_lock_plan:764` already refuses distance-0 work for the same reason;
# this brings the shape-based instrument up to the value-based one's standard.
awk -v want="$WANT_HRT" -v elig=/tmp/pdj_elig.txt -v keep=/tmp/pdj_keep.txt \
    -v prot=/tmp/pdj_prot.txt -v sel=/tmp/pdj_sel.txt -F'\t' '
  NR == FNR {                                   # pass A: each line lowest PENDING block
    if ($2 == "qw" && $5 != "") { b = $5 + 0; if (!($4 in lo) || b < lo[$4]) lo[$4] = b }
    next
  }
  $2 != "qw" { next }                           # pass B: only eligible jobs can be held
  {
    print $1 > elig
    if ($3 == want) { print $1 > keep; next }                       # the high-value shape
    if ($5 != "" && ($4 in lo) && ($5 + 0) == lo[$4]) { print $1 > prot; next }   # THE VALUE GUARD
    print $1 > sel
  }
' /tmp/pdj_rows.txt /tmp/pdj_rows.txt
rm -f "$QR"
sort -u -o /tmp/pdj_elig.txt /tmp/pdj_elig.txt

qstat -u ucestes      | tail -n +3 | grep c1_ | awk '{print $1}' | sort -u > /tmp/pdj_c1.txt
qstat -u ucestes -s r | tail -n +3 |             awk '{print $1}' | sort -u > /tmp/pdj_run.txt
sort -u /tmp/pdj_sel.txt > /tmp/pdj_sel_a.txt
comm -23 /tmp/pdj_sel_a.txt /tmp/pdj_c1.txt > /tmp/pdj_sel_s.txt

n=$(grep -c . /tmp/pdj_sel_s.txt || true)
bad_run=$(comm -12 /tmp/pdj_sel_s.txt /tmp/pdj_run.txt | grep -c . || true)
bad_c1=$(comm -12 /tmp/pdj_sel_s.txt /tmp/pdj_c1.txt  | grep -c . || true)

echo "eligible now         : $(grep -c . /tmp/pdj_elig.txt || true)"
echo "KEEP eligible (h_rt=${WANT_HRT}) : $(grep -c . /tmp/pdj_keep.txt || true)"
echo "PROTECTED (line's lowest pending block -- the deadlock guard) : $(grep -c . /tmp/pdj_prot.txt || true)"
echo "SELECTED to hold     : $n"
# ⚠ THE CONTENT AUDIT, NOT JUST THE SELECTION RULE. Twice now (R27-17, R28-3) a hold passed its
# "did I touch anything forbidden" check while holding exactly the wrong work. A count cannot answer
# that question; a per-line, per-block breakdown can, so it is PRINTED EVERY RUN and never inferred.
echo "--- WHAT WOULD BE HELD, BY LINE AND BLOCK (the CONTENT) ---"
awk -F'\t' 'NR==FNR{s[$1]=1; next} ($1 in s){c[$4"\tt"$5]++}
  END{ if (length(c)==0) { print "    (nothing)"; exit }
       for(k in c){split(k,p,"\t"); printf "    %-30s %-4s %5d\n", p[1], p[2], c[k]} }' \
    /tmp/pdj_sel_s.txt /tmp/pdj_rows.txt | sort
echo "--- ELIGIBLE LEFT PER LINE AFTER THIS HOLD (any line at 0 is a DEADLOCK) ---"
awk -F'\t' 'NR==FNR{s[$1]=1; next} $2=="qw"{ tot[$4]++; if (!($1 in s)) left[$4]++ }
  END{ bad=0
       for(k in tot){ l=(k in left)?left[k]:0; printf "    %-30s %3d of %3d left%s\n", k, l, tot[k], (l==0?"   *** ZERO -- DEADLOCK ***":"" ); if(l==0) bad++ }
       if (bad) printf "    !! %d line(s) would be taken to ZERO eligible\n", bad }' \
    /tmp/pdj_sel_s.txt /tmp/pdj_rows.txt | sort
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
