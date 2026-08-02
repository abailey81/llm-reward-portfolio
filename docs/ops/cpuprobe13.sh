#!/bin/bash
# ============================================================================================
# ⚠⚠ SUPERSEDED AND UNSCHEDULABLE — DO NOT SUBMIT THIS FILE. USE `docs/ops/cpuprobe14.sh`.
#
# This spec asks for a shape no queue offers: it carries `-l mem=1G` with NO `-pe`, NO `-l tmpfs`
# and NO `-ac allow=`. Two jobs submitted from it on 2026-08-02 (73026, 73027) sat unschedulable
# on a queue that was AT `max_u_jobs`, and because `qdel` is blocked for the agent they
# permanently consumed two of one thousand job slots (P188).
#
# The corrected probe derives its spec from a LIVE RUNNING campaign job (`qstat -j`) instead of
# from documentation, and is verified to run: `cpuprobe14.sh` placed on node-b00a-013 and
# returned the CPU model that settled the D30 pool-widening decision.
# ============================================================================================
#$ -N cpuprobe13
#$ -cwd
#$ -j y
#$ -o /home/ucestes/cpuprobe13/
#$ -l h_rt=0:2:0
#$ -l mem=1G
#
# CPU-MODEL PROBE — the ONE unverified fact the pool-widening decision rests on (RUN 13, 2026-08-02).
#
# WHY. Pool d's own free capacity has collapsed from 2,472 slots (2026-07-31) to 480 cores' worth,
# while pools b00a / e00a / f00a hold 616 cores we could take — a 128 % increase on what d can still
# give us. The 2026-07-31 entry that DECLINED pool widening priced it at +4 % and said, verbatim,
# "re-open only if pool d's own capacity becomes the binding constraint". It now is.
#
# Pool b is already SETTLED — record §46.2 measured it as microarchitecture-identical
# (`Intel Xeon Gold 6240 @ 2.60GHz`). Pools e00a and f00a have the IDENTICAL qhost topology to d00a
# (36 NCPU / 2 sockets / 36 cores / 36 threads / 188.4 G) but have NEVER been probed, and topology is
# necessary, not sufficient: several 18-core Xeon SKUs share it.
#
# This matters because the C3 gate enforces per-seed substrate homogeneity, where the substrate string
# is `cpu model | omp | threads | cuda`. If e00a is a different SKU, widening onto it makes comparison
# units span two CPU models and PARKS every line at the gate — the intuitive speed move would be a
# campaign stop. D15 is the standing reminder: ONE heterogeneous host already cost four archived
# records.
#
# SAFETY. One core, two minutes, writes ONLY to ~/cpuprobe13/. It touches no spec, no batch, no
# ledger and NOTHING under the campaign archive. Job name `cpuprobe13` is unique so it can be cleaned
# up by EXACT NAME — never `qdel -u`.
echo "PROBE_HOST=$(hostname -s)"
echo "PROBE_MODEL=$(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2- | sed 's/^ *//')"
echo "PROBE_SOCKETS=$(grep -c '^physical id' /proc/cpuinfo 2>/dev/null)"
echo "PROBE_CORES=$(grep -c '^processor' /proc/cpuinfo)"
echo "PROBE_FLAGS_AVX512=$(grep -m1 -c avx512f /proc/cpuinfo)"
echo "PROBE_MICROCODE=$(grep -m1 microcode /proc/cpuinfo | cut -d: -f2- | sed 's/^ *//')"
