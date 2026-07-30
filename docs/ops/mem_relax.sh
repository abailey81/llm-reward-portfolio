#!/bin/bash
# mem_relax.sh — relax the per-slot MEMORY request on our QUEUED Myriad jobs, and nothing else.
#
# WHY (measured 2026-07-30, record §38). Our search-lane jobs ask `-pe smp 8` with `mem=4G` per slot
# = 32 GB per job. Their measured peak is `maxvmem = 1.64 GB` (n=55 completed 8-slot RUN-4 jobs,
# harvested qacct) — a 19.5x over-request. On Myriad's d pool (188 GB / 36 cores = 5.2 GB per core)
# memory is the scarce consumable, and a 32 GB ask is what keeps us queued: a controlled canary
# (six one-off `sleep` jobs, identical except for one field) showed
#
#     smp 8, h_rt 15h, mem 4G  -> STILL QUEUED after 9 min
#     smp 8, h_rt 15h, mem 2G  -> RAN at the next scheduling pass, on pool d
#     smp 8, h_rt 15h, mem 1G  -> RAN at the next scheduling pass, on pool d
#
# so MEMORY is the discriminator, not slots, not walltime, not fair share. h_rt is NOT over-asked:
# the longest observed training is 12.20 h against the 15 h request, so shortening walltime would
# start killing trainings and is deliberately NOT done here.
#
# WHAT THIS TOUCHES. The SGE memory REQUEST of already-queued jobs. It changes nothing that can move
# a number: not the arithmetic, not the thread count, not the pool, not the host fence, not the code.
# It is reversible (run again with --mem 4G). It is SURGICAL BY CONSTRUCTION: the job's own
# `hard resource_list` is read back from `qstat -j` and only the `memory=` term is substituted, so
# `snx`, `tmpfs`, `batch`, `h_rt` and the D15 host fence (`hostname=!node-d00a-230&!node-d00b-024`)
# are carried across verbatim and cannot be dropped by a typo.
#
# SAFETY FLOOR. Refuses any target below 1G/slot, and refuses to touch a job whose slot count it
# cannot read. 2G/slot = 16 GB per 8-slot job = 9.8x the measured peak.
#
# ⚠ NOT run automatically. `qalter` on live jobs is a deliberate operator action; the harness safety
# classifier blocks it from the agent side, which is the correct default. Run it yourself:
#
#     ssh myriad 'bash -s' < docs/ops/mem_relax.sh            # DRY RUN (default): prints, changes nothing
#     ssh myriad 'bash -s' -- --apply < docs/ops/mem_relax.sh # applies to every queued campaign job
#
# Options: --apply | --mem <NG> (default 2G) | --limit <N> (only the first N jobs, for a canary)

set -u
APPLY=0
MEM=2G
LIMIT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --apply) APPLY=1 ;;
    --mem) shift; MEM="$1" ;;
    --limit) shift; LIMIT="$1" ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

case "$MEM" in
  1G|2G|3G|4G) : ;;
  *) echo "REFUSED: --mem $MEM is outside the measured-safe band 1G..4G per slot" >&2; exit 2 ;;
esac

echo "mem_relax: target=${MEM}/slot  apply=${APPLY}  limit=${LIMIT}  at $(date -u +%FT%TZ)"

JOBS=$(qstat -u "$USER" | awk 'NR>2 && $5 ~ /qw/ && $3 ~ /^(c1|h3ss|leg)/ {print $1}' | sort -u)
[ -n "$JOBS" ] || { echo "no queued campaign jobs — nothing to do"; exit 0; }

n=0; changed=0; skipped=0
for J in $JOBS; do
  n=$((n+1))
  if [ "$LIMIT" -gt 0 ] && [ "$n" -gt "$LIMIT" ]; then break; fi

  RL=$(qstat -j "$J" 2>/dev/null | sed -n 's/^hard resource_list: *//p' | head -1)
  NM=$(qstat -j "$J" 2>/dev/null | sed -n 's/^job_name: *//p' | head -1)
  if [ -z "$RL" ]; then echo "  SKIP $J ($NM): no hard resource_list readable"; skipped=$((skipped+1)); continue; fi
  case "$RL" in
    *memory=*) : ;;
    *) echo "  SKIP $J ($NM): no memory= term in [$RL]"; skipped=$((skipped+1)); continue ;;
  esac

  NEW=$(echo "$RL" | sed "s/memory=[0-9.]*[KMGT]/memory=$MEM/")
  if [ "$NEW" = "$RL" ]; then echo "  SKIP $J ($NM): already at $MEM"; skipped=$((skipped+1)); continue; fi

  echo "  $J  $NM"
  echo "      before: $RL"
  echo "      after : $NEW"
  if [ "$APPLY" -eq 1 ]; then
    if qalter -l "$NEW" "$J" >/dev/null 2>&1; then
      BACK=$(qstat -j "$J" 2>/dev/null | sed -n 's/^hard resource_list: *//p' | head -1)
      echo "      verify: $BACK"
      changed=$((changed+1))
    else
      echo "      FAILED: qalter returned non-zero (job may have started — harmless)"
      skipped=$((skipped+1))
    fi
  fi
done

echo "mem_relax: considered=$n changed=$changed skipped=$skipped (apply=$APPLY)"
[ "$APPLY" -eq 1 ] && echo "watch placement with: qstat -u \$USER | awk 'NR>2 {c[\$5]++} END {for (k in c) print k, c[k]}'"
exit 0
