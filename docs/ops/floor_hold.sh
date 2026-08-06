#!/bin/bash
# floor_hold.sh -- concentrate our functional-ticket share onto the c1 FLOOR jobs.
#
# WHY (measured 2026-08-06):
#   * Dispatch order on Myriad is decided ENTIRELY by ntckts: weight_urgency=0, so waiting time
#     contributes nothing, and prior = 4.0*npprior + 1.5*ntckts (exact to 5 dp on a live job).
#   * share_functional_shares=TRUE, so our ticket pool is DIVIDED among our contending jobs.
#     At 897 contending we get 14,757/job -- the lowest of any major user but one.
#   * c1's round-2 floor jobs would land alongside 412 of our OWN sweep jobs at near-identical
#     ntckts, i.e. 8 entries in a raffle of 420, holding the NEWEST job ids.
#   Holding the sweep drops contending to ~108 and puts our whole allocation on the floor.
#
# SAFETY: selects PENDING, NOT-ALREADY-HELD, NON-c1 jobs only. Refuses to run if the selection
# contains a c1 job or a running job. Re-selects at run time, so it can never touch a round-2 job
# that did not exist when this was written.
#
# USAGE:  bash ~/floor_hold.sh --dry     # show what would be held, change nothing
#         bash ~/floor_hold.sh           # apply
#         bash ~/floor_hold.sh --release # release exactly what this script holds (the time-box)
set -u

MODE="${1:---apply}"
SEL=/tmp/floor_hold_ids.txt
RUN=/tmp/floor_hold_running.txt
C1=/tmp/floor_hold_c1.txt

# --release-when-ready: a SAFE no-op until the hold has served its purpose, so it can be invoked on
# a loop. The hold exists to put our whole ticket allocation on c1's round-2 (h2_pair) array; the
# moment that array is RUNNING the concentration has done its job and every further minute is pure
# cost, because eligible=0 means finishing jobs cannot be replaced.
#
# TWO release conditions, and the second is the safety valve:
#   1. an h2_pair job is RUNNING  -> purpose served, release.
#   2. cores < 400 while eligible is 0 -> the hold is now costing more than it can buy; release
#      regardless of c1, because a floor that is not dispatching is not worth an idle fleet.
# It deliberately does NOT release merely because round 2 was SUBMITTED: submitted-and-queued is
# exactly the state the concentration exists to get through.
if [ "$MODE" = "--release-when-ready" ]; then
    c1run=$(qstat -u ucestes -s r 2>/dev/null | tail -n +3 | grep -c h2_pair)
    runtot=$(qstat -u ucestes -s r 2>/dev/null | tail -n +3 | wc -l)
    eligtot=$(qstat -u ucestes -s p 2>/dev/null | tail -n +3 | grep -vc hqw)
    heldtot=$(qstat -u ucestes -s h 2>/dev/null | tail -n +3 | wc -l)
    cores=$(( runtot * 8 ))
    # ⚠ AN EMPTY qstat IS NOT A MEASUREMENT OF ZERO (learned live 2026-08-06 14:07Z, when an empty
    # rc=0 response made a watch announce the campaign was dead while records were still landing).
    # Zero jobs in EVERY state is an unread queue, and releasing on it would be acting on nothing.
    if [ "$runtot" -eq 0 ] && [ "$eligtot" -eq 0 ] && [ "$heldtot" -eq 0 ]; then
        echo "UNREAD: qstat returned no job in any state. No action."
        exit 0
    fi
    if [ "$heldtot" -eq 0 ]; then
        echo "nothing held. No action."
        exit 0
    fi
    echo "h2_pair running=$c1run  cores=$cores  eligible=$eligtot  held=$heldtot"
    if [ "$c1run" -gt 0 ]; then
        echo "*** RELEASING: the floor's h2_pair array is RUNNING -- the hold has served its purpose."
        MODE="--release"
    elif [ "$cores" -lt 400 ] && [ "$eligtot" -eq 0 ]; then
        echo "*** RELEASING: cores=$cores with eligible=0 -- the hold now costs more than it buys."
        MODE="--release"
    else
        echo "holding: the floor's h2_pair array is not running yet."
        exit 0
    fi
fi

if [ "$MODE" = "--release" ]; then
    # Release every NON-c1 job we hold. c1 is never held by this script, so it is never released
    # by it either -- the floor's state is untouched in both directions.
    qstat -u ucestes -s h | tail -n +3 | grep -v c1_ | awk '{print $1}' | sort -u > "$SEL"
    n=$(wc -l < "$SEL")
    echo "releasing $n held non-c1 job(s)"
    [ "$n" -gt 0 ] && xargs -a "$SEL" -r qrls
    echo "held now: $(qstat -u ucestes -s h | tail -n +3 | wc -l)"
    exit 0
fi

# pending, not already held, not c1
qstat -u ucestes -s p | tail -n +3 | grep -v hqw | grep -v c1_ | awk '{print $1}' | sort -u > "$SEL"
# the two things that must NOT be in the selection
qstat -u ucestes -s r | tail -n +3 | awk '{print $1}' | sort -u > "$RUN"
qstat -u ucestes    | tail -n +3 | grep    c1_ | awk '{print $1}' | sort -u > "$C1"

n=$(wc -l < "$SEL")
bad_run=$(comm -12 "$SEL" "$RUN" | wc -l)
bad_c1=$(comm -12 "$SEL" "$C1" | wc -l)

echo "selected      : $n job(s)"
echo "  of which RUNNING (must be 0) : $bad_run"
echo "  of which c1      (must be 0) : $bad_c1"
echo "by line:"
qstat -u ucestes -s p | tail -n +3 | grep -v hqw | grep -v c1_ | awk '{print $3}' | sed 's/_.*//' \
    | sort | uniq -c | sed 's/^/    /'

if [ "$bad_run" -ne 0 ] || [ "$bad_c1" -ne 0 ]; then
    echo "REFUSING: the selection is not clean. Nothing was held."
    exit 2
fi
if [ "$n" -eq 0 ]; then
    echo "nothing to hold."
    exit 0
fi
if [ "$MODE" = "--dry" ]; then
    echo "DRY RUN -- nothing held. Re-run without --dry to apply."
    exit 0
fi

xargs -a "$SEL" -r qhold
echo "---"
echo "held now      : $(qstat -u ucestes -s h | tail -n +3 | wc -l)   (expect ~$((n + $(cat "$C1" | wc -l) * 0 )) more than before)"
echo "eligible now  : $(qstat -u ucestes -s p | tail -n +3 | grep -vc hqw)"
echo "c1 untouched  : $(qstat -u ucestes | tail -n +3 | grep -c c1_) c1 job(s) in the queue"
