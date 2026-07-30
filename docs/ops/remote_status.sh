#!/bin/bash
# RUN 4 cluster-side operational snapshot: jobs, cores, placement. Read-only.
Q=$(qstat -u ucestes | tail -n +3)

TOTAL=$(echo "$Q" | grep -c .)
LADDER=$(echo "$Q" | grep -c 'l16')
CAMP=$((TOTAL - LADDER))
RUN=$(echo "$Q" | awk '{print $5}' | grep -c '^r$')
QW=$(echo "$Q" | awk '{print $5}' | grep -c '^qw$')
# SLOTS COLUMN IS STATE-DEPENDENT. A RUNNING row carries a queue field (NF=10, $8=queue, $9=slots);
# a QUEUED row does NOT (NF=9, $8=slots, $9=ja-task-ID). Summing $9 for both reads the array
# TASK-ID as a slot count for every queued job -- which is how an earlier version of this script
# reported 292 slots while the allocation advisor reported 1520. The advisor was right.
SLOTS_RUN=$(echo "$Q" | awk '$5=="r"  {s+=$9} END {print s+0}')
SLOTS_QUEUED=$(echo "$Q" | awk '$5=="qw" {s+=$8} END {print s+0}')
SLOTS=$((SLOTS_RUN + SLOTS_QUEUED))
SLOTS_LADDER=$(echo "$Q" | awk '/l16/ && $5=="r" {s+=$9} END {print s+0}')

echo "JOBS_TOTAL=$TOTAL"
echo "JOBS_CAMPAIGN=$CAMP"
echo "JOBS_LADDER=$LADDER"
echo "JOBS_RUNNING=$RUN"
echo "JOBS_QUEUED=$QW"
echo "CORES_GRANTED_CAMPAIGN=$((SLOTS_RUN - SLOTS_LADDER))   # what is actually COMPUTING"
echo "CORES_GRANTED_INCL_LADDER=$SLOTS_RUN"
echo "CORES_QUEUED_WAITING=$SLOTS_QUEUED                     # demand already lodged with the scheduler"
echo "SLOTS_TOTAL_REQUESTED=$SLOTS"

echo "--- campaign batches in flight ---"
echo "$Q" | grep -v 'l16' | awk '{print $3}' | sed 's/_p[0-9]*$//' | sort | uniq -c | sort -rn | head -10

echo "--- distinct hosts we are on ---"
echo "$Q" | awk '$5=="r" {print $8}' | sed 's/.*@//; s/\..*//' | sort -u | wc -l

echo "--- cluster context (how contended it is) ---"
echo "cluster_qw_total=$(qstat -u '*' 2>/dev/null | awk '$5=="qw"' | wc -l)"

echo "--- archived records on the remote side ---"
echo "remote_records=$(find "$HOME/Scratch/llmrp4/outputs" -name record.json 2>/dev/null | wc -l)"
echo "remote_epilogues=$(cat "$HOME/Scratch/llmrp4/ledger"/*.jsonl 2>/dev/null | wc -l)"
