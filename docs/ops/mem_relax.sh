#!/bin/bash
# ##############################################################################################
# ⚠⚠ SUPERSEDED 2026-07-30 16:05 UTC — THIS SCRIPT CANNOT WORK. It is kept as EVIDENCE, not as a
# tool, and it refuses to run.
#
# UCL forbids modifying a queued job's resource list, site-wide:
#
#     $ qconf -sconf | grep jsv
#     jsv_url          /opt/geassist/bin/policyjsv
#     jsv_allowed_mod  ac,h,i,e,o,j,M,N,p,w          <-- no `l`
#
#     $ qalter -l mem=2G 45433
#     rejected due to jsv_allowed_mod configuration which does not allow: l_hard
#     rc=1
#
#     $ qalter -N zzname_test 45433                  <-- the CONTROL: `N` IS on the list
#     modified job name of job 45433
#     rc=0
#
# So the memory request of an ALREADY-QUEUED job is immutable — for us, for Tamer, for anyone
# without RC privileges. The dry run this script offered was correct about the SUBSTITUTION and
# silent about the PERMISSION, and that gap is the whole lesson: **a dry run that deliberately
# does not call the mutating command cannot discover a policy that forbids the mutation.** The
# check that would have caught it is one line — `qconf -sconf | grep jsv_allowed_mod` — and it
# should have been run BEFORE the tooling was built around the idea.
#
# WHAT REPLACES IT. The same measured sizing, moved into the RENDERER where it reaches every NEW
# job: `src/cluster/jobscript.py` now defaults `mem_per_core` to a lane-aware value computed from
# the measured per-training peak (1.64 GB), scoped to the CPU lane:
#
#     search lane  pack 1 on 8 cores ->  mem=1G   (8 GB/job, 4.9x the 1.64 GB peak)
#     test lane    pack 4 on 4 cores ->  mem=2G   (8 GB/job, 1.29x the measured 6.2 GB peak)
#     GPU lane                       ->  mem=4G   (unchanged; the measurement was CPU-only)
#
# and it reaches the cluster through a DRIVER RELAUNCH, which is the only delivery mechanism left.
#
# THE MEASUREMENTS BEHIND IT ALL STAND, and are why the fix is worth a relaunch:
#   * 19.5x over-request: maxvmem p50 1.57 GB / max 1.64 GB over n=55 of OUR 8-slot RUN-4 tasks
#     (scoped by job name inside the run window — the harvested qacct files also hold other users'
#     accounting from 2022-23), against a 32 GB request.
#   * dispatch: eight one-off canaries identical except one field — 15 h 8-slot at `mem=4G` waited
#     43-46 min; at 1G/2G/3G the same job placed at the FIRST scheduling pass, four for four.
#     Walltime was NOT the discriminator (4/8/12/15 h all placed in one window).
#   * no enforcement: at `mem=2G` a node reports `ulimit -v unlimited`, no cgroup limit, only an
#     informational `SGE_UCL_MEM`; a canary held 3 GiB for 90 s and exited rc=0.
#   * the C4 ceiling: `max_u_jobs = maxujobs = 1000`; at 4 cores/job that is exactly 4,000 cores,
#     but 1,000 x 16 GB = 16 TB of reservation against ~12 TB free pool-d memory. At 2G it is 8 TB.
#
# Full narrative: record §38 (the experiment), §43 (the 4,000-core route), §45 (this refutation).
# ##############################################################################################
echo "REFUSED: qalter -l is forbidden site-wide (jsv_allowed_mod = ac,h,i,e,o,j,M,N,p,w — no 'l')." >&2
echo "A queued job's memory request cannot be changed. See record §45." >&2
echo "The fix now lives in src/cluster/jobscript.py and ships via a driver relaunch." >&2
exit 3
