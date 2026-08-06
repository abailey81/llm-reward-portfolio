#!/bin/bash
# Watch the c1 FLOOR through its round-1 -> round-2 handover, and emit ONE line per state change.
#
# The hold that concentrates our tickets onto the floor leaves eligible=0, which is a DELIBERATE but
# COSTLY state: our running jobs finish with nothing to replace them. So this watch exists to make
# the release trigger observable rather than remembered.
#
# Emits on: round-2 submitted · round-2 dispatching · round-2 fully running (RELEASE NOW) ·
#           round 1 fully drained but round 2 absent (the failure case that needs a human) ·
#           our total core count crossing down through 400 while eligible is 0 (the hold is costing).
prev=""
while true; do
    out=$(ssh -o BatchMode=yes myriad 'c1r=$(qstat -u ucestes -s r 2>/dev/null | tail -n +3 | grep -c c1_); c1p=$(qstat -u ucestes -s p 2>/dev/null | tail -n +3 | grep -v hqw | grep -c c1_); elig=$(qstat -u ucestes -s p 2>/dev/null | tail -n +3 | grep -vc hqw); run=$(qstat -u ucestes -s r 2>/dev/null | tail -n +3 | wc -l); echo "$c1r $c1p $elig $run"' 2>/dev/null)
    set -- $out
    c1r="${1:-}"; c1p="${2:-}"; elig="${3:-}"; run="${4:-}"
    if [ -z "$c1r" ]; then sleep 120; continue; fi
    # ⚠⚠ AN EMPTY qstat IS NOT A MEASUREMENT OF ZERO, AND THIS SCRIPT LEARNED IT THE EXPENSIVE WAY.
    # 2026-08-06 14:07Z: `qstat -u ucestes` returned NOTHING with rc=0 under qmaster load, every
    # `wc -l` and `grep -c` above returned 0, and the -z guard did not fire because "0" is not
    # empty. This watch then announced "cores=0 -- the campaign is dead" while the cycle log was
    # banking +3 and +5 records from the very jobs it had just written off. A read from the SAME
    # response was internally contradictory: `c1 running: 8` beside `total running: 0`.
    #
    # THE DISCRIMINATOR: we always hold 794 jobs, so a response claiming ZERO jobs in EVERY state
    # is an unread queue, not an empty one. `arm_jobs.py` has carried this guard all along and
    # core_accumulator.py has now been given it too.
    if [ "$run" -eq 0 ] && [ "$elig" -eq 0 ] && [ "$c1r" -eq 0 ] && [ "$c1p" -eq 0 ]; then
        echo "qstat returned zero jobs in EVERY state -- treating as UNREAD, not empty. Skipping."
        sleep 120
        continue
    fi
    cores=$(( run * 8 ))
    key="$c1r/$c1p"
    if [ "$key" != "$prev" ]; then
        prev="$key"
        if [ "$c1p" -gt 0 ] && [ "$c1r" -le 8 ]; then
            echo "*** c1 ROUND 2 SUBMITTED: ${c1p} pending, ${c1r} running | eligible=${elig} cores=${cores}"
        elif [ "$c1p" -eq 0 ] && [ "$c1r" -gt 8 ]; then
            echo "*** c1 ROUND 2 FULLY RUNNING (${c1r} c1 jobs) -- RELEASE THE HOLD NOW | cores=${cores}"
        elif [ "$c1p" -eq 0 ] && [ "$c1r" -eq 0 ]; then
            echo "*** WARNING: ZERO c1 jobs running AND zero pending -- round 2 did not submit. Needs a human. | eligible=${elig} cores=${cores}"
        else
            echo "c1 state: running=${c1r} pending=${c1p} | eligible=${elig} cores=${cores}"
        fi
    fi
    if [ "$elig" -eq 0 ] && [ "$cores" -lt 400 ]; then
        echo "*** THE HOLD IS NOW COSTING: cores=${cores} with eligible=0 -- release regardless of c1 state"
        sleep 900
    fi
    sleep 150
done
