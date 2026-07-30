#!/bin/bash
# mem_relax.sh — relax the per-slot MEMORY request on our QUEUED Myriad jobs, and nothing else.
#
# WHY (measured 2026-07-30, record §38). Our search-lane jobs ask `-pe smp 8` with `mem=4G` per slot
# = 32 GB per job. Their measured peak is `maxvmem = 1.64 GB` (n=55 completed 8-slot RUN-4 tasks,
# scoped by OUR job names inside RUN 4's window — the harvested qacct files also contain other users'
# accounting, so the scoping is load-bearing). That is a 19.5x over-request. On Myriad's d pool
# (188 GB / 36 cores = 5.2 GB per core) memory is the scarce consumable, and the over-ask is what
# keeps us waiting: eight one-off canary jobs, identical except one field, showed
#
#     smp 8, h_rt 15h, mem 1G / 2G / 3G  -> placed at the FIRST scheduling pass, four for four
#     smp 8, h_rt 15h, mem 4G            -> waited 46 min (and two siblings were still waiting)
#
# so the memory request is a DISPATCH-LATENCY multiplier, not a hard gate. h_rt is NOT over-asked
# (longest observed training 12.20 h against the 15 h request), so shortening walltime is refused.
#
# ENFORCEMENT, measured on-node (record §38): with `mem=2G` the job sees `ulimit -v unlimited`,
# `Max address space unlimited`, no cgroup memory limit, and only an informational `SGE_UCL_MEM`
# env var. The request is a SCHEDULING RESERVATION, not a kill limit.
#
# WHAT THIS TOUCHES. The SGE memory REQUEST of already-queued jobs. It changes nothing that can move
# a number: not the arithmetic, not the thread count, not the pool (`-ac allow=d` is untouched), not
# the host fence, not the code. Reversible: run again with --mem 4G.
#
# SURGICAL BY CONSTRUCTION: each job's own `hard resource_list` is read back from `qstat -j` and only
# the `memory=` term is substituted, so `snx`, `tmpfs`, `batch`, `h_rt` and the D15 host fence
# (`hostname=!node-d00a-230&!node-d00b-024`) are carried across verbatim and cannot be dropped by a
# typo. A post-substitution self-check refuses any edit that changed more than the memory term.
#
# LANE SAFETY: only 8-slot jobs are touched — the search lane, which runs ONE training per job. The
# packed test lane (`--pack 4 --cores-per-training 1`, 4 slots, FOUR concurrent trainings) is left
# alone, because its footprint is ~4x a single training and it is not the lane that is queuing.
#
# ⚠ Run it yourself; `qalter` on live jobs is an operator action:
#     ssh myriad 'bash -s' < docs/ops/mem_relax.sh                       # DRY RUN, changes nothing
#     ssh myriad 'bash -s' -- --apply --limit 5 < docs/ops/mem_relax.sh  # five-job canary
#     ssh myriad 'bash -s' -- --apply < docs/ops/mem_relax.sh            # the rest
#
# Options: --apply | --mem <NG> (default 2G, band 1G..4G) | --limit <N> | --slots <N> (default 8)

set -u
APPLY=0
MEM=2G
LIMIT=0
WANT_SLOTS=8
while [ $# -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --mem)   shift; MEM="$1" ;;
    --limit) shift; LIMIT="$1" ;;
    --slots) shift; WANT_SLOTS="$1" ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

case "$MEM" in
  1G|2G|3G|4G) : ;;
  *) echo "REFUSED: --mem $MEM is outside the measured-safe band 1G..4G per slot" >&2; exit 2 ;;
esac

echo "mem_relax: target=${MEM}/slot  slots=${WANT_SLOTS}  apply=${APPLY}  limit=${LIMIT}  $(date -u +%FT%TZ)"

JOBS=$(qstat -u "$USER" | awk 'NR>2 && $5 ~ /qw/ && $3 ~ /^(c1|h3ss|leg)/ {print $1}' | sort -u)
[ -n "$JOBS" ] || { echo "no queued campaign jobs — nothing to do"; exit 0; }

n=0; changed=0; skipped=0; wrongslots=0
for J in $JOBS; do
  DETAIL=$(qstat -j "$J" 2>/dev/null)
  [ -n "$DETAIL" ] || { echo "  SKIP $J: no qstat -j detail (already started?)"; skipped=$((skipped+1)); continue; }

  NM=$(echo "$DETAIL"  | sed -n 's/^job_name: *//p' | head -1)
  RL=$(echo "$DETAIL"  | sed -n 's/^hard resource_list: *//p' | head -1)
  SLOTS=$(echo "$DETAIL" | sed -n 's/.*parallel environment: *[^ ]* *range: *//p' | head -1)

  if [ "${SLOTS:-0}" != "$WANT_SLOTS" ]; then
    echo "  SKIP $J ($NM): ${SLOTS:-?} slots, not $WANT_SLOTS — the packed lane is deliberately left alone"
    wrongslots=$((wrongslots+1)); continue
  fi
  case "$RL" in
    *memory=*) : ;;
    *) echo "  SKIP $J ($NM): no memory= term in [$RL]"; skipped=$((skipped+1)); continue ;;
  esac

  NEW=$(echo "$RL" | sed "s/memory=[0-9.]*[KMGT]/memory=$MEM/")
  if [ "$NEW" = "$RL" ]; then echo "  SKIP $J ($NM): already at $MEM"; skipped=$((skipped+1)); continue; fi

  # self-check: normalise the memory term on BOTH sides; anything else that differs is a bug
  A=$(echo "$RL"  | sed 's/memory=[0-9.]*[KMGT]/memory=X/')
  B=$(echo "$NEW" | sed 's/memory=[0-9.]*[KMGT]/memory=X/')
  if [ "$A" != "$B" ]; then
    echo "  REFUSED $J ($NM): the substitution changed more than the memory term"
    echo "      before: $RL"
    echo "      after : $NEW"
    skipped=$((skipped+1)); continue
  fi

  n=$((n+1))
  if [ "$LIMIT" -gt 0 ] && [ "$n" -gt "$LIMIT" ]; then n=$((n-1)); break; fi

  echo "  $J  $NM  (${SLOTS} slots)"
  echo "      before: $RL"
  echo "      after : $NEW"
  if [ "$APPLY" -eq 1 ]; then
    if qalter -l "$NEW" "$J" >/dev/null 2>&1; then
      BACK=$(qstat -j "$J" 2>/dev/null | sed -n 's/^hard resource_list: *//p' | head -1)
      echo "      verify: $BACK"
      case "$BACK" in
        *memory=$MEM*) changed=$((changed+1)) ;;
        *) echo "      ⚠ VERIFY FAILED: memory is not $MEM after qalter"; skipped=$((skipped+1)) ;;
      esac
    else
      echo "      FAILED: qalter returned non-zero (job may have started — harmless)"
      skipped=$((skipped+1))
    fi
  fi
done

echo "mem_relax: eligible=$n changed=$changed skipped=$skipped other-lane=$wrongslots (apply=$APPLY)"
if [ "$APPLY" -eq 1 ]; then
  echo "watch placement with:"
  echo "  qstat -u \$USER | awk 'NR>2 {c[\$5]++} END {for (k in c) print k, c[k]}'"
fi
exit 0
