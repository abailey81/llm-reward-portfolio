#!/usr/bin/env bash
# ALL SEVEN RECORD LAYERS, ONE COMMAND.
#
# Tamer's standing item (1): "constantly check each record, make sure every record individually is
# very strictly flawless, logical, meaningful." Seven independent layers now answer that, and until
# this file existed the seventh (S14) lived only in a session scratchpad -- an auditor's finding:
# "the seventh layer runs only when a human types the command", which is the instrument-nobody-reads
# shape this codebase repeatedly names.
#
# WHY A SESSION-LEVEL RUNNER RATHER THAN WIRING THEM INTO cycle.py: the cycle already opens every
# record every sweep and is SWEEP-BOUND (measured 13.1 s per 1,000 records; ~200 s at 8k). Adding
# ~5 minutes of full-archive walks to a 2-minute loop would be P194 exactly -- "a new monitor is a
# load on the monitor it joins". S1-S10 is already wired there and rate-limited to 30 minutes; the
# rest belong here, run once per session.
#
#     bash docs/ops/run_record_layers.sh            # all seven, prints RC per layer
#
# EXIT: 0 only if EVERY layer returned 0. Read the per-layer RC lines, never just the last one.
set -u
cd "$(dirname "$0")/../.." || exit 1
PY=.venv/Scripts/python.exe
[ -x "$PY" ] || PY=python

fail=0
run_layer () {
  name="$1"; shift
  start=$(date -u +%s)
  "$PY" "$@" > "/tmp/layer_${name}.out" 2>&1
  rc=$?
  end=$(date -u +%s)
  printf '%-30s RC=%-3s (%3ss)  %s\n' "$name" "$rc" "$((end-start))" "/tmp/layer_${name}.out"
  [ "$rc" -ne 0 ] && fail=1
  return 0
}

echo "=== SEVEN RECORD LAYERS  ($(date -u +%Y-%m-%dT%H:%M:%SZ)) ==="
echo "archive: $(find outputs/campaign_cluster_run4 -name record.json -not -path '*/.pull_tmp*' 2>/dev/null | wc -l) records"
echo

run_layer "L1_record_validator"        docs/analysis/record_validator.py
run_layer "L2_provenance_seal"         docs/analysis/record_provenance_seal.py
run_layer "L3_science_audit"           docs/analysis/record_science_audit.py
run_layer "L4_fed_text_identification" docs/analysis/fed_text_identification.py
run_layer "L5_reward_code_audit"       docs/analysis/reward_code_audit.py
run_layer "L6_fed_value_coherence"     docs/analysis/fed_value_coherence.py
run_layer "L7_window_identity"         docs/analysis/record_window_identity.py

echo
if [ "$fail" -eq 0 ]; then
  echo "ALL SEVEN LAYERS RC=0."
else
  echo "*** AT LEAST ONE LAYER FAILED -- read its output file above. ***"
fi
exit "$fail"
