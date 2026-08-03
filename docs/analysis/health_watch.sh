#!/usr/bin/env bash
# ANALYSIS-LANE watcher v2 (read-only). Emits ONLY actionable TRANSITIONS -- never a steady state,
# never the 42 s cadence. v2 adds: bus-inbox watch, per-batch progress (the A1 blind spot), and
# de-duped drift so a long ops edit session cannot drown a real signal.
set -u
REPO="/c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio"
TOP="/c/Users/User/Desktop/dissertation_papers"
LOG="$REPO/docs/ops/watch/CYCLE_LOG.md"
AL="$REPO/docs/ops/watch/ALERTS.txt"
ST="$REPO/docs/ops/watch/STATE.json"
RUN4="$REPO/outputs/campaign_cluster_run4"
LANE="$TOP/.claude/lanes/lanebus.py"

prev_sig=""; prev_al=""; prev_spend_band=""; prev_rec=""; prev_inbox=""
last_rec_change=$(date +%s); emitted_stall=0
declare -A batch_seen batch_since

while true; do
  now=$(date +%s)

  # ---------- 1. the ops cycle ----------
  if [ -f "$LOG" ]; then
    line=$(grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}T' "$LOG" | tail -1)
    # ⚠ PARSE-FAILURE GUARD (added 05:50Z after coord's "another lane's output format is not your
    # contract"). This watcher parses THREE ops-owned artefacts. Without this, a format change on
    # ops' side leaves every field EMPTY, the signature changes exactly once, and the watcher then
    # goes PERMANENTLY SILENT on the campaign's primary monitor -- silence I would read as health.
    # That is a FALSE CLEAN, the worst degradation mode. Fail LOUD and keep failing.
    if [ -z "$line" ]; then
      echo "WATCH-FAIL  $LOG exists but NO line matches the expected cycle format -- the ops log format may have changed. THIS WATCHER IS BLIND UNTIL FIXED; do not read its silence as health."
      sleep 120; continue
    fi
    ts=${line%% *}
    rec=$(sed -n 's/.*records=\([0-9]*\).*/\1/p' <<<"$line")
    spend=$(sed -n 's/.*spend=\$\([0-9.]*\).*/\1/p' <<<"$line")
    drift=$(sed -n 's/.*drift=\([^ ]*\).*/\1/p' <<<"$line")
    sci=$(sed -n 's/.*sci=\([^ ]*\).*/\1/p' <<<"$line")
    stal=$(sed -n 's/.*stalest=\([0-9.]*\)m.*/\1/p' <<<"$line")
    guards=$(sed -n 's/.*guards=\([0-9]*\).*/\1/p' <<<"$line")
    armsf=$(sed -n 's/.*arms_full=\([0-9/]*\).*/\1/p' <<<"$line")
    verdict=$(awk '{print $2}' <<<"$line")

    if [ -n "${rec:-}" ] && [ "$rec" != "$prev_rec" ]; then
      [ -n "$prev_rec" ] && last_rec_change=$now
      prev_rec="$rec"; emitted_stall=0
    fi
    if [ $(( (now - last_rec_change) / 60 )) -ge 45 ] && [ "$emitted_stall" -eq 0 ]; then
      echo "STALL  no new record for $(( (now-last_rec_change)/60 )) min (records=$rec verdict=$verdict stalest=${stal}m)"
      emitted_stall=1; last_rec_change=$now
    fi

    # ONE signature covers verdict/drift/sci/guards/arms -- emitted only when it CHANGES,
    # so a long ops edit session produces one line, not one every two minutes.
    sig="$verdict|$drift|$sci|$guards|$armsf"
    if [ "$sig" != "$prev_sig" ]; then
      if [ -n "$prev_sig" ]; then
        echo "CYCLE $ts  $prev_sig -> $sig  (records=$rec spend=\$$spend stalest=${stal}m)"
        case "$drift" in
          0) ;;                                     # clean
          *dirty) : ;;                              # ops working in-tree; the signature line says it
          # A bare (non-"dirty") drift number is NOT automatically severe: a RUNNING_SHA re-base is a
          # routine, announced ops operation and the cycle reports non-zero until its loop reloads.
          # Overstating a risk is as inaccurate as understating one -- so prompt the check, do not
          # assert the verdict. (Softened 05:55Z after this fired on exactly such a re-base.)
          *) echo "  ^^ commit drift vs RUNNING_SHA (not a dirty tree). VERIFY before treating as an incident: git diff --name-only <RUNNING_SHA>..HEAD -- src scripts config prompts. Empty => a re-base transient, benign." ;;
        esac
        [ "$sci" != "OK" ] && echo "  ^^ SCIENCE LAYER NON-CLEAN (sci=$sci)"
      fi
      prev_sig="$sig"
    fi

    if [ -n "${stal:-}" ] && awk "BEGIN{exit !($stal > 30)}"; then
      echo "STALE-DRIVER  $ts  stalest=${stal}m (>30m)"
    fi
    if [ -n "${spend:-}" ]; then
      band=${spend%%.*}
      if [ "$band" != "$prev_spend_band" ]; then
        [ -n "$prev_spend_band" ] && echo "SPEND crossed \$$band at $ts (records=$rec)"
        prev_spend_band="$band"
      fi
    fi
  else
    echo "WATCH-FAIL cycle log missing: $LOG"
  fi

  # ---------- 2. the ops cycle itself dying (a log tail cannot see this) ----------
  if [ -f "$ST" ]; then
    age=$(( now - $(stat -c %Y "$ST") ))
    [ "$age" -gt 600 ] && echo "CYCLE-DEAD  STATE.json unwritten for $((age/60)) min -- the ops loop may have stopped"
  fi

  # ---------- 3. ALERTS content ----------
  if [ -f "$AL" ]; then
    h=$(sha256sum "$AL" | cut -c1-16)
    if [ "$h" != "$prev_al" ]; then
      [ -n "$prev_al" ] && echo "ALERTS-CHANGED  $(grep -cE '^(RED|ATTN)' "$AL" 2>/dev/null) RED/ATTN lines"
      prev_al="$h"
    fi
  fi

  # ---------- 4. per-batch progress -- STOOD DOWN 2026-08-01 01:57Z ----------
  # The A1 blind spot is now covered by the COORD lane's .claude/lanes/batch_progress.py, armed on a
  # 5-minute loop against a verified 324-batch baseline (37 active / 21 complete / 259 superseded /
  # 7 flagged, six of the seven independently confirmed complete). Theirs is strictly better than the
  # log-tuple heuristic that lived here: it has an independent completion test (done==total is NOT
  # terminal -- a permanently-rejected unit leaves a finished batch at 4/5), a --test-only mode, and a
  # verified baseline to diff against. Two detectors disagreeing at 4am is worse than one good one, so
  # this lane defers. Removed rather than commented out: dead scaffolding is a defect.

  # ---------- 4b. THE DATED FALSIFIER on coord's sequencing account (M27) ----------
  # Prediction: leg4's h2_pair_test is QUEUED behind the per-arm test legs (campaign.py:1832-1846),
  # not stranded, so it should start producing after the three running batches drain (~06:10Z, from a
  # measured 13 records/h arrival proxy against 53 remaining units). FALSIFIER: still 0 at 08:00Z,
  # with ~2 h of margin on a 4.1 h estimate. Fires ONCE either way so the answer is not left to a guess.
  # ⚠ RECALIBRATED 04:25Z (P119). The original 08:00Z clock falsifier was WRONG in exactly the way
  # coord's 480-min threshold was: it treated "still 0/60" as evidence, but coord's measured
  # time-to-FIRST-completion distribution (n=254: p50 5.36 h, p90 25.06, p95 27.95, MAX 30.56) shows a
  # HEALTHY batch sits at done=0 for up to ~30 h. At 08:00Z leg4 would be ~21 h old -- INSIDE p90 -- so
  # the old rule would have fired a FALSE REFUTATION on the right conclusion for the wrong reason.
  # THE DISCRIMINATING CONDITION IS EVENT-DRIVEN, NOT CLOCK-DRIVEN: campaign.py:1832-1846 sequences
  # h2_pair AFTER the per-arm test legs drain, so the test is -- once placebo_test AND
  # placebo_shuffled_test are complete, does h2_pair get enumerated?
  if [ "${m27_done:-0}" -eq 0 ]; then
    n_pair=$(find "$RUN4/test_leg_qwen3_5_9b/distributional" "$RUN4/test_leg_qwen3_5_9b/scalar" \
             -name record.json 2>/dev/null | wc -l)
    n_plc=$(find "$RUN4/test_leg_qwen3_5_9b/placebo" -name record.json 2>/dev/null | wc -l)
    n_shf=$(find "$RUN4/test_leg_qwen3_5_9b/placebo_shuffled" -name record.json 2>/dev/null | wc -l)
    if [ "$n_pair" -gt 0 ]; then
      echo "M27-CONFIRMED  leg4 h2_pair has STARTED ($n_pair distributional+scalar test records) -- coord's sequencing account HOLDS; it was queued, not stranded."
      m27_done=1
    elif [ "$n_plc" -ge 30 ] && [ "$n_shf" -ge 30 ]; then
      # The precondition is now satisfied: both per-arm legs are complete. If h2_pair still has not
      # been ENUMERATED (not merely not completed), the sequencing account is refuted on the right axis.
      if ! grep -q "h2_pair" <(tail -300 "$RUN4/driver_qwen3_5-9b.log" 2>/dev/null); then
        echo "M27-REFUTED  placebo (${n_plc}/30) and placebo_shuffled (${n_shf}/30) are COMPLETE, so h2_pair's sequencing precondition is satisfied -- yet the driver still does not ENUMERATE it in its last 300 log lines. The sequencing account is refuted ON THE CORRECT AXIS (unmentioned, not merely uncompleted). Needs a driver intervention. See ANALYSIS_LANE A1 + bus M27/M54."
        m27_done=1
      fi
    fi
  fi

  # ---------- 4c. A12-bis: the D16 re-run restoring the CRN seed-set invariant ----------
  # Ops quarantined seeds 14-17 of baseline_volatility_scaled_return (D16 option B, 02:40Z), so the
  # core test lane transiently holds TWO seed sets instead of one. Until the re-runs land, an N6 IUT
  # leg computes on 26 pairs while its siblings use 30 -- silent, and in an IUT the MAX-over-legs
  # p-value makes the weakest leg disproportionately likely to decide the node. Fire ONCE on restore.
  if [ "${d16_done:-0}" -eq 0 ]; then
    n_vsr=$(find "$RUN4/test/baseline_volatility_scaled_return" -name record.json 2>/dev/null | wc -l)
    if [ "$n_vsr" -ge 30 ]; then
      echo "D16-RESTORED  baseline_volatility_scaled_return is back to ${n_vsr} records -- RE-VERIFY NOW: (a) seeds 0-29 complete and one shared seed set across all 12 units, (b) the unit device-HOMOGENEOUS on 6240 for all thirty (a re-run landing on another 6140 reproduces the defect). See ANALYSIS_LANE A12-bis."
      d16_done=1
    fi
  fi

  # ---------- 5. the lane bus ----------
  if [ -f "$LANE" ]; then
    ib=$(python "$LANE" --as analysis board 2>/dev/null | grep -E '^INBOX' | head -1)
    if [ -n "$ib" ] && [ "$ib" != "$prev_inbox" ]; then
      case "$ib" in *"0 unread"*) ;; *) echo "BUS  $ib  -- run: lane inbox" ;; esac
      prev_inbox="$ib"
    fi
  fi

  sleep 120
done
