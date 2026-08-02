#!/bin/bash
#$ -N cpuprobe14
#$ -cwd
#$ -j y
#$ -o /home/ucestes/cpuprobe14/
#$ -l h_rt=0:2:0
#$ -l mem=2G
#$ -l tmpfs=1G
#$ -pe smp 1
#
# CPU-MODEL PROBE, RUN 14 — the one unverified fact the pool-widening decision (D30) rests on.
#
# WHY THE RUN-13 PROBE (cpuprobe13.sh) COULD NEVER RUN (P188). It carried `-l mem=1G` with no
# `-pe`, no `-l tmpfs`, and no `-ac allow=`, so it requested a shape no queue offers and sat
# unschedulable on a queue that was AT `max_u_jobs`. Because `qdel` is blocked for the agent, that
# mistake permanently consumed two of one thousand job slots.
#
# THE SPEC BELOW IS DERIVED FROM A LIVE, RUNNING CAMPAIGN JOB, not from documentation:
#   qstat -j 69843 ->
#     hard resource_list: snx=1,tmpfs=1G,memory=2G,batch=true,h_rt=54000
#     parallel environment: smp-[D]* range: 8
#     context: allow=d
# `snx` and `batch` come from the site's default request, and `-pe smp` is resolved to the
# per-pool wildcard PE by the `allow=<pool>` context, so this asks for exactly one slot of the
# same shape a real training job asks for -- differing only in width (1 not 8) and walltime.
#
# THE POOL IS PASSED AT SUBMIT TIME (`qsub -ac allow=b|e|f`), so one script probes every candidate
# pool and the results are directly comparable.
#
# SAFETY. One core, two minutes, writes ONLY to ~/cpuprobe14/. It touches no spec, no batch, no
# ledger, and nothing under the campaign archive. The job name `cpuprobe14` is unique so it can be
# cleaned up by EXACT NAME -- never `qdel -u`.
echo "PROBE_POOL_REQUESTED=${POOL_TAG:-unset}"
echo "PROBE_HOST=$(hostname -s)"
echo "PROBE_MODEL=$(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2- | sed 's/^ *//')"
echo "PROBE_SOCKETS=$(grep '^physical id' /proc/cpuinfo | sort -u | wc -l)"
echo "PROBE_CORES=$(grep -c '^processor' /proc/cpuinfo)"
echo "PROBE_AVX512F=$(grep -m1 -c avx512f /proc/cpuinfo)"
echo "PROBE_MICROCODE=$(grep -m1 microcode /proc/cpuinfo | cut -d: -f2- | sed 's/^ *//')"
echo "PROBE_FLAGS_SHA=$(grep -m1 '^flags' /proc/cpuinfo | cut -d: -f2- | tr ' ' '\n' | sort | sha256sum | cut -c1-16)"
