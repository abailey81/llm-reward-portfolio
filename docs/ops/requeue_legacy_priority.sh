#!/bin/bash
# REQUEUE THE LEGACY -p -100 JOBS SO THEY COME BACK AT FULL FAIR-SHARE STANDING.
#
# WHY (record §54). Until 2026-07-31 our jobs were submitted with `-p -100`, and Myriad weights the
# POSIX priority field at `weight_priority = 4.0` — the largest weight in `qconf -ssconf`. Measured:
# our jobs sat at `prior` 1.811-1.828 against every other user at 2.000-2.082, with 1,888 of 2,395
# pending jobs outranking us. The fix (all `-p` values -> 0) is live, but it only reaches NEW
# submissions: the jobs already sitting in `qw` keep the `-p` they were submitted with, and those are
# overwhelmingly the three CONTROL arms, which gate every line (a line completes when its SLOWEST arm
# does). `qalter -p` cannot rescue them — SGE refuses:
#     denied: "ucestes" must be operator to increase job priority
# so the only route is to delete the QUEUED ones and let the driver resubmit them at 0.
#
# WHY THIS IS SAFE, and it is safe BY DESIGN rather than by luck. `src/cluster/driver.py` was
# hardened for exactly this case on 2026-07-13 (finding P13). `_attempted_run_ids()` returns None
# when a round leaves NO qacct trace — "the deleted-pending class (an admin purge / qdel before
# dispatch)" — and the drain handler then logs
#     "the array was purged before dispatch; requeueing N spec(s) WITHOUT a retry bump"
# i.e. the specs come back with their retry budget UNTOUCHED. Deleting a never-dispatched job is a
# requeue, not an abandonment.
#
# THE ONE RULE THAT MAKES IT TRUE: **only ever delete a job in `qw`.** A job that has STARTED leaves
# qacct rows, which the driver reads as attempt evidence and DOES bump the retry counter for — and
# retries are bounded, so a bumped spec can eventually exhaust and be permanently lost (§26.3: a
# rejected candidate is never replaced). This script therefore re-reads each job's state immediately
# before deleting it and skips anything that is not `qw`, so a job that starts mid-sweep is left alone.
#
# BOUNDED TO ONE PASS: the driver tolerates at most 3 CONSECUTIVE evidence-less drains per batch
# before it stops requeueing and exhausts loudly. One sweep spends one of those three. Do not run this
# repeatedly against the same batches.
#
#   bash docs/ops/requeue_legacy_priority.sh              # DRY RUN (default) - lists, deletes nothing
#   bash docs/ops/requeue_legacy_priority.sh --apply      # actually delete the queued legacy jobs
#
# Run it ON the cluster:  ssh myriad 'bash -s' -- --apply < docs/ops/requeue_legacy_priority.sh

#
# 2026-07-31, SECOND USE (record §60): generalised from "legacy -p" to "legacy CONFIG". The tmpfs
# fix (15G -> 1G) has the same shape as the priority fix -- it reaches only NEWLY SUBMITTED jobs,
# while the jobs already sitting in `qw` keep the request they were submitted with. `--stale-tmpfs`
# selects those instead of the negative-priority ones. `--limit N` stops after N so the first use of
# any new selector can be canaried before a mass requeue.
#
#   bash requeue_legacy_priority.sh --apply --stale-tmpfs --limit 5   # canary
#   bash requeue_legacy_priority.sh --apply --stale-tmpfs             # the rest

set -u
APPLY=0; LIMIT=0; MODE=priority
while [ $# -gt 0 ]; do
    case "$1" in
        --apply)        APPLY=1 ;;
        --stale-tmpfs)  MODE=tmpfs ;;
        --limit)        shift; LIMIT="${1:-0}" ;;
    esac
    shift
done

USER_ID=$(whoami)
echo "=== requeue_legacy_priority  (user=$USER_ID  mode=$([ $APPLY -eq 1 ] && echo APPLY || echo DRY-RUN)) ==="

mapfile -t QW < <(qstat -u "$USER_ID" 2>/dev/null | tail -n +3 | awk '$5 ~ /qw/ {print $1}')
echo "queued (qw) jobs found: ${#QW[@]}"

targets=(); skipped_ok=0; skipped_state=0
for J in "${QW[@]}"; do
    if [ "$MODE" = "tmpfs" ]; then
        # A job's own hard resource_list is the truth; the jobscript on disk may already be the NEW
        # one while this job carries the OLD request (that is exactly the situation being fixed).
        TF=$(qstat -j "$J" 2>/dev/null | grep -m1 'hard resource_list' | grep -o 'tmpfs=[0-9]*[GM]' | head -1)
        case "$TF" in
            tmpfs=1G|"") skipped_ok=$((skipped_ok+1)); continue ;;
        esac
    else
        P=$(qstat -j "$J" 2>/dev/null | awk '/^priority:/{print $2}')
        P=${P:-0}
        if [ "$P" = "0" ]; then skipped_ok=$((skipped_ok+1)); continue; fi
    fi
    targets+=("$J")
    if [ "$LIMIT" -gt 0 ] && [ "${#targets[@]}" -ge "$LIMIT" ]; then break; fi
done

echo "  selector                          : $MODE"
echo "  already correct (left alone)      : $skipped_ok"
echo "  stale-config (to requeue)         : ${#targets[@]}${LIMIT:+  (limit $LIMIT)}"
if [ ${#targets[@]} -eq 0 ]; then echo "nothing to do."; exit 0; fi

deleted=0
for J in "${targets[@]}"; do
    # RE-READ the state immediately before acting: a job that has started since the listing must be
    # left alone, because deleting a DISPATCHED job bumps its retry counter (see the header).
    S=$(qstat -u "$USER_ID" 2>/dev/null | awk -v j="$J" '$1==j {print $5}')
    if [ "$S" != "qw" ]; then
        echo "  SKIP $J - state is '${S:-gone}', not qw"
        skipped_state=$((skipped_state+1))
        continue
    fi
    N=$(qstat -j "$J" 2>/dev/null | awk '/^job_name:/{print $2}')
    if [ $APPLY -eq 1 ]; then
        if qdel "$J" >/dev/null 2>&1; then
            deleted=$((deleted+1)); echo "  DELETED $J  $N"
        else
            echo "  FAILED  $J  $N"
        fi
    else
        echo "  would delete $J  $N"
    fi
done

echo ""
echo "  skipped because they had started : $skipped_state"
echo "  deleted                          : $deleted"
if [ $APPLY -eq 1 ]; then
    echo ""
    echo "NEXT: within one poll interval each affected driver should log"
    echo "  'the array was purged before dispatch; requeueing N spec(s) WITHOUT a retry bump'"
    echo "and resubmit at -p 0. Verify with:"
    echo "  grep -c 'WITHOUT a retry bump' outputs/campaign_cluster_run4/driver_*.log"
    echo "  and confirm new jobscripts carry '#\$ -p 0'."
else
    echo ""
    echo "DRY RUN only. Re-run with --apply to act."
fi
