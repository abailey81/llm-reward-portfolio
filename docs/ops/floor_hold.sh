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
# --auto: HOLD ONLY WHILE THE HOLD IS ACTUALLY BUYING SOMETHING.
#
# ⚠ THE ORIGINAL DESIGN WAS "hold until the floor is served", AND THAT WAS WRONG. The ticket
# concentration only matters once c1's h2_pair array is PENDING and competing with our own sweep
# jobs. Before that moment it buys nothing and costs everything, because eligible=0 means finishing
# jobs cannot be replaced. Measured live 2026-08-06: round 1's last job (91237) passed 9.98 h
# against a 9.12 h median, and the tail of that distribution runs to the 15 h wall -- so "until the
# floor is served" could have meant FIVE MORE HOURS of an idle queue for no benefit at all.
#
# SGE recomputes tickets on a 10-minute interval, so applying the hold AFTER round 2 appears costs
# about ten minutes of concentration latency and saves hours of held capacity. That trade is not
# close.
#
# The state machine, in one line: hold iff h2_pair is PENDING and not yet running.
if [ "$MODE" = "--auto" ]; then
    pend=$(qstat -u ucestes -s p 2>/dev/null | tail -n +3 | grep -v hqw | grep -c h2_pair)
    run=$(qstat -u ucestes -s r 2>/dev/null | tail -n +3 | grep -c h2_pair)
    runtot=$(qstat -u ucestes -s r 2>/dev/null | tail -n +3 | wc -l)
    eligtot=$(qstat -u ucestes -s p 2>/dev/null | tail -n +3 | grep -vc hqw)
    heldtot=$(qstat -u ucestes -s hu 2>/dev/null | tail -n +3 | wc -l)
    # an empty qstat is not a measurement of zero (learned live 14:07Z)
    if [ "$runtot" -eq 0 ] && [ "$eligtot" -eq 0 ] && [ "$heldtot" -eq 0 ]; then
        echo "UNREAD: qstat returned no job in any state. No action."; exit 0
    fi
    echo "h2_pair pending=$pend running=$run | cores=$(( runtot * 8 )) eligible=$eligtot held=$heldtot"
    if [ "$pend" -gt 0 ] && [ "$run" -eq 0 ]; then
        if [ "$eligtot" -eq 0 ]; then echo "already concentrated."; exit 0; fi
        echo "*** HOLDING: h2_pair is PENDING -- concentrate our ticket share onto it."
        MODE="--apply"
    else
        # covers BOTH "not submitted yet" and "already running": in neither case does the hold buy
        # anything, and in both cases an idle queue is pure loss.
        floorheld=$(comm -12 <(qstat -u ucestes -s hu 2>/dev/null | tail -n +3 | awk '{print $1}' | sort -u) \
                             <(tr -d '\r' < "$HOME/floor_ids.txt" 2>/dev/null | sort -u) | wc -l)
        if [ "$floorheld" -eq 0 ]; then echo "nothing of the floor hold is held. No action."; exit 0; fi
        if [ "$run" -gt 0 ]; then echo "*** RELEASING: h2_pair is RUNNING -- the hold has served."
        else echo "*** RELEASING: h2_pair is not even submitted -- the hold buys nothing yet."; fi
        MODE="--release"
    fi
fi

if [ "$MODE" = "--release-when-ready" ]; then
    c1run=$(qstat -u ucestes -s r 2>/dev/null | tail -n +3 | grep -c h2_pair)
    runtot=$(qstat -u ucestes -s r 2>/dev/null | tail -n +3 | wc -l)
    eligtot=$(qstat -u ucestes -s p 2>/dev/null | tail -n +3 | grep -vc hqw)
    heldtot=$(qstat -u ucestes -s hu 2>/dev/null | tail -n +3 | wc -l)
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
    # Release the FLOOR HOLD only, never the LADDER LOCK.
    #
    # ⚠ THE TWO HOLDS ARE DIFFERENT INSTRUMENTS AND MUST NOT BE UNDONE TOGETHER. The LADDER LOCK
    # (386 jobs) is Tamer's ratified ORDERING policy -- every line works its lowest incomplete
    # block -- and it is meant to persist for days. The FLOOR HOLD (408) is a tactical ticket
    # concentration that expires the moment c1's h2_pair array is running. Releasing both would
    # silently revert the ordering policy to the pipelined scatter that D73 exists to correct,
    # and nothing would report that it had happened.
    #
    # Releasing only the floor set also restores 408 eligible jobs, comfortably above the 291-job
    # burst floor, so depth returns without giving up the ordering.
    #
    # ~/floor_ids.txt is written by the APPLY path at the bottom of this file. ⚠ CORRECTED 2026-08-06
    # (RUN 28): this comment previously said it was "written at hold time from
    # docs/ops/watch/FLOOR_HOLD.json", and that was NEVER TRUE -- nothing wrote it anywhere, so this
    # branch scoped against whatever a previous era had left on disk (measured: 408 ids from 14:46Z
    # against 546 actually held). The write now exists; see the R27-5 FIX note beside it.
    # If the file is missing we fall back to "every held non-c1 job", which is the OLD, blunter
    # behaviour -- and we say so, because silently doing something broader than asked is how a fix
    # becomes a fault. ⚠ THE FALLBACK IS NOW THE DANGEROUS BRANCH, not the safe one: it also lifts
    # the LADDER LOCK. Prefer re-applying the hold (which writes the file) over taking the fallback.
    if [ -s "$HOME/floor_ids.txt" ]; then
        # intersect the recorded floor set with what is ACTUALLY held: the live queue is the
        # authority, and a job that has already been released must not be "released" again.
        qstat -u ucestes -s hu | tail -n +3 | grep -v c1_ | awk '{print $1}' | sort -u \
            > /tmp/floor_live_held.txt
        # ⚠ STRIP CR. The id list is written on Windows, whose text mode silently rewrites \n to
        # \r\n, and a trailing \r makes every id fail to match -- which turned this release into a
        # SILENT NO-OP ("would release: 0") when it was previewed on 2026-08-06. Caught only by
        # previewing the selection instead of trusting it, minutes before it had to work.
        tr -d '\r' < "$HOME/floor_ids.txt" | sort -u > /tmp/floor_recorded.txt
        comm -12 /tmp/floor_live_held.txt /tmp/floor_recorded.txt > "$SEL"
        echo "releasing the FLOOR HOLD only; the LADDER LOCK stays held (ordering policy)"
    else
        echo "!! ~/floor_ids.txt MISSING -- falling back to releasing EVERY held non-c1 job."
        echo "!! That also lifts the LADDER LOCK. Re-run the governor afterwards to restore it."
        qstat -u ucestes -s hu | tail -n +3 | grep -v c1_ | awk '{print $1}' | sort -u > "$SEL"
    fi
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

# ⚠⚠ R27-5 FIX, RUN 28, 2026-08-06. THIS WRITE DID NOT EXIST, AND THE WHOLE RELEASE PATH DEPENDS ON IT.
# `~/floor_ids.txt` was READ in three places -- the --auto release branch and both --release branches
# -- and WRITTEN in none, so it only ever held whatever a previous era had left on disk. Measured on
# the node at 20:29Z: 408 ids, mtime 14:46:11Z, six hours stale, against 546 jobs actually held.
# TWO failure modes followed, and the second is worse than the one first recorded:
#   1. --release intersects the live held set with a stale list and SILENTLY UNDER-RELEASES;
#   2. --auto computes `floorheld` from that same stale list, so it can conclude "nothing of the
#      floor hold is held. No action." WHILE THE HOLD IS HELD -- a silent no-op in a script whose
#      entire design is to be run on a loop.
# Written AFTER the qhold and only on the apply path, so a --dry run still mutates nothing, and with
# `>` rather than `>>` so a second apply can never accumulate ids from a previous hold.
sort -u "$SEL" > "$HOME/floor_ids.txt"
echo "recorded      : $(grep -c . "$HOME/floor_ids.txt") id(s) -> ~/floor_ids.txt (what --release will scope to)"
echo "---"
echo "held now      : $(qstat -u ucestes -s h | tail -n +3 | wc -l)   (expect ~$((n + $(cat "$C1" | wc -l) * 0 )) more than before)"
echo "eligible now  : $(qstat -u ucestes -s p | tail -n +3 | grep -vc hqw)"
echo "c1 untouched  : $(qstat -u ucestes | tail -n +3 | grep -c c1_) c1 job(s) in the queue"
