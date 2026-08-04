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
# ⚠⚠ PARSE GUARD (P250, 2026-08-04). Bash reads a script INCREMENTALLY, BY BYTE OFFSET. Edit the
# file while an instance is running and that instance resumes at the same offset in the NEW bytes,
# which lands mid-token: on the day this was added, an edit to a comment made a live run print
# `cord_science_audit.py: command not found` and re-execute two layers. Wrapping the whole body in
# one compound command forces bash to parse to the closing brace BEFORE executing anything, so an
# edit mid-run can no longer scramble control flow. Cheap, and this script certifies an
# irreplaceable archive.
{
cd "$(dirname "$0")/../.." || exit 1
# ⚠ NO SILENT FALLBACK (auditor finding F-10, 2026-08-03). This read `[ -x "$PY" ] || PY=python`,
# which is precisely the fallback `cycle_loop.sh` condemns two files away -- and P231 proved the
# consequence is not theoretical: under the base interpreter the record layers cannot `import src`
# or numpy, so they would not fall back gracefully, they would FAIL while looking like a layer
# result. These SEVEN gated layers -- plus the three ungated MEASUREMENTS below them, which
# is where the 'eight' in an earlier version of this comment came from (S15 is a
# measurement, not a gate) -- are the evidence that every record in an irreplaceable
# archive is
# sound; running them under an interpreter that cannot load the project is not a degraded check,
# it is no check at all.
PY=.venv/Scripts/python.exe
if [ ! -x "$PY" ]; then
    echo "run_record_layers: FATAL - no venv interpreter at $PY (cwd=$(pwd))." >&2
    echo "run_record_layers: refusing to certify an irreplaceable archive with an unknown" >&2
    echo "run_record_layers: interpreter. Activate the venv and re-run." >&2
    exit 2
fi

fail=0
# ⚠⚠ THE BANNER USED TO COUNT NOTHING (found 2026-08-04, P250). It printed "ALL SEVEN LAYERS
# RC=0" whenever `fail` was 0 -- which is also true of a run that executed THREE layers, or none.
# On the day it was found, this script had been EDITED WHILE RUNNING: bash reads a script by BYTE
# OFFSET, so the edit shifted the offsets under the live instance, which resumed mid-token
# (`cord_science_audit.py: command not found`) and re-ran two layers. Every layer happened to pass,
# so the banner was substantively true by luck. A certification of an irreplaceable archive may not
# be true by luck. `layers_run` makes the count part of the verdict.
layers_run=0
EXPECTED_LAYERS=7
OUTDIR="${TMPDIR:-/tmp}/record_layers_$$"
mkdir -p "$OUTDIR" || exit 2
run_layer () {
  name="$1"; shift
  start=$(date -u +%s)
  "$PY" "$@" > "${OUTDIR}/layer_${name}.out" 2>&1
  rc=$?
  end=$(date -u +%s)
  printf '%-30s RC=%-3s (%3ss)  %s\n' "$name" "$rc" "$((end-start))" "${OUTDIR}/layer_${name}.out"
  [ "$rc" -ne 0 ] && fail=1
  layers_run=$((layers_run + 1))
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
if [ "$layers_run" -ne "$EXPECTED_LAYERS" ]; then
  echo "*** ONLY $layers_run OF $EXPECTED_LAYERS LAYERS RAN. THIS IS NOT A CERTIFICATION. ***"
  echo "*** A missing layer is indistinguishable from a passing one unless the count is checked."
  echo "*** Most likely cause: this script was EDITED WHILE RUNNING (bash re-reads by byte offset)."
  fail=1
elif [ "$fail" -eq 0 ]; then
  echo "ALL $EXPECTED_LAYERS LAYERS RAN, ALL RC=0."
else
  echo "*** AT LEAST ONE LAYER FAILED -- read its output file above. ***"
fi
echo "    (per-layer output in $OUTDIR -- unique per run, so concurrent runs cannot overwrite"
echo "     each other's results, which they previously did via fixed /tmp paths.)"

# ---------------------------------------------------------------------------------------------
# CAMPAIGN MEASUREMENTS -- NOT record layers, and DELIBERATELY OUTSIDE the exit code above.
#
# WHY THEY ARE HERE (2026-08-03, RUN 17, record s.130): both were written this session and were
# referenced by NOTHING. That is verbatim the failure s.124.5 named -- "S14 and line_balance were
# wired into NOTHING" -- which s.125 recorded as a lesson and which I then re-created twice in the
# same session. An instrument nobody runs is not an instrument. This is the one command a session
# is told to run every session, so they belong here.
#
# ⚠ THEY DO NOT AFFECT `$fail`, AND THAT IS DELIBERATE. `r115_threshold_sensitivity.py` exits 1 BY
# DESIGN -- the registered insensitivity claim IS falsified, that is the KNOWN and DISCLOSED state
# (docs/R115_DISCLOSURE_2026-08-03.md), and it cannot return to 0 without changing a frozen value,
# which is forbidden. Folding a permanently-1 check into a pass/fail gate would make the gate
# permanently red, which is the always-on-alarm pathology that let `guards=2` hide P202 for 31 h.
# So they REPORT; the seven layers GATE.
echo
echo "=== CAMPAIGN MEASUREMENTS (reported, NOT gated -- see the note in this script) ==="
for spec in "M1_authoring_reliability docs/ops/authoring_reliability.py" \
            "M2_r115_threshold        docs/analysis/r115_threshold_sensitivity.py" \
            "M3_seed_completeness     docs/analysis/record_seed_completeness.py"; do
  set -- $spec
  name="$1"; script="$2"
  start=$(date -u +%s)
  "$PY" "$script" > "${OUTDIR}/measure_${name}.out" 2>&1
  rc=$?
  end=$(date -u +%s)
  note=""
  [ "$name" = "M2_r115_threshold" ] && [ "$rc" -eq 1 ] && note="  <- EXPECTED: the registered claim IS falsified; a DISCLOSURE, not a regression"
  [ "$name" = "M3_seed_completeness" ] && [ "$rc" -eq 1 ] && note="  <- holes exist. NORMAL during pipelined C4. Actionable ONLY if the line has ZERO jobs -- check line_balance."
  [ "$rc" -eq 2 ] && note="  <- RC=2 means the check could not run or inspected NOTHING. Investigate."
  printf '%-26s RC=%-3s (%3ss)  %s%s\n' "$name" "$rc" "$((end-start))" "${OUTDIR}/measure_${name}.out" "$note"
done
echo "  (M1 is the corrected per-model authoring-reliability table -- D34; the guard's own panel"
echo "   understates it and omits the confirmatory line entirely. M2 re-derives R115's insensitivity"
echo "   claim; its positive control must read 56/56 or nothing it prints may be believed."
echo "   M3 is the gap NO record layer covered: every layer verifies a record is individually sound,"
echo "   none asked whether the SET is COMPLETE. A single hole below an arm's frontier DEMOTES the"
echo "   rung it banks, and the common rung is a MINIMUM -- gpt-5.6-luna held 2,832 perfect records"
echo "   and banked 189 instead of 568 because seeds 192/193 were absent.)"

exit "$fail"

} # end parse guard -- see the note at the top of this file
