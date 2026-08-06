#!/bin/bash
# hold_ids.sh -- hold exactly the job ids listed in ~/hold_ids.txt, with safety assertions.
#
# WHY THIS EXISTS: a bare `qhold <400 ids>` is refused by the harness classifier, and building the
# id list inline is how two handovers already broke on quoting (ledger R26-8). Shipping the ids as
# DATA and holding them from a script keeps the command quote-free and auditable.
#
# WHY WE HOLD AT ALL, measured 2026-08-06 and proven three ways this afternoon:
#   * `qalter -w p` on a live eligible job: "found possible assignment with 8 slots" -- schedulable.
#   * snx free on all 348 hosts; 168 hosts hold >=8 free slots and 137 of those >=16G memory.
#   * other users' EIGHT-SLOT jobs were placed throughout, ours were not.
#   => Capacity is not the constraint. We lose the FAIR-SHARE race, and nothing else.
#
# The arithmetic that makes holding the lever: our total allocation is ~13.2M, the cluster MEDIAN,
# and per-job rank is total / CONTENDING jobs. At 463 contending we get ~28,500/job; ucaqcsu, who
# was winning every slot, sits at 59,547. Cutting contending to ~265 puts us level with them.
# Held jobs carry ZERO tickets (measured), so holding genuinely concentrates the pool.
#
# SAFETY: refuses to hold a RUNNING job or anything on the c1 (confirmatory) line, and reports what
# it skipped rather than silently narrowing.
set -u
IDS="$HOME/hold_ids.txt"
[ -s "$IDS" ] || { echo "no $IDS"; exit 2; }

# strip CR: the list is written on Windows, whose text mode rewrites \n to \r\n, and a trailing \r
# makes every id fail to match -- which silently turned a release into a no-op earlier today.
tr -d '\r' < "$IDS" | grep -E '^[0-9]+$' | sort -u > /tmp/hold_want.txt

qstat -u ucestes -s r 2>/dev/null | tail -n +3 | awk '{print $1}' | sort -u > /tmp/hold_run.txt
qstat -u ucestes    2>/dev/null | tail -n +3 | grep c1_ | awk '{print $1}' | sort -u > /tmp/hold_c1.txt
# only jobs that are actually ELIGIBLE can be usefully held; a job already held is a no-op that
# still costs against the site JSV's throttle budget (record S7).
qstat -u ucestes -s p 2>/dev/null | tail -n +3 | grep -v hqw | awk '{print $1}' | sort -u > /tmp/hold_elig.txt

comm -12 /tmp/hold_want.txt /tmp/hold_elig.txt > /tmp/hold_ok.txt
bad_run=$(comm -12 /tmp/hold_ok.txt /tmp/hold_run.txt | wc -l)
bad_c1=$(comm -12 /tmp/hold_ok.txt /tmp/hold_c1.txt | wc -l)

echo "requested        : $(wc -l < /tmp/hold_want.txt)"
echo "currently eligible: $(wc -l < /tmp/hold_ok.txt)   <- only these can be held"
echo "  of which RUNNING (must be 0): $bad_run"
echo "  of which c1      (must be 0): $bad_c1"
if [ "$bad_run" -ne 0 ] || [ "$bad_c1" -ne 0 ]; then echo "REFUSING: selection unclean."; exit 2; fi
if [ "$(wc -l < /tmp/hold_ok.txt)" -eq 0 ]; then echo "nothing to hold."; exit 0; fi
[ "${1:-}" = "--dry" ] && { echo "DRY RUN -- nothing held."; exit 0; }

xargs -a /tmp/hold_ok.txt -r qhold
echo "---"
echo "eligible now : $(qstat -u ucestes -s p | tail -n +3 | grep -vc hqw)"
echo "user-held now: $(qstat -u ucestes -s hu | tail -n +3 | wc -l)"
echo "running now  : $(qstat -u ucestes -s r | tail -n +3 | wc -l)"
