#!/bin/bash
# close_watch -- the RUN 4 live watch loop.
#
# Emits ONLY on change, plus a heartbeat every HEARTBEAT_EVERY cycles so that silence is never
# ambiguous (a watcher that goes quiet on both "healthy" and "dead" is useless). Any guard
# returning 2 is emitted every cycle until it clears -- a stop-the-run condition must not be
# reported once and then swallowed by change-detection.
set -u

ROOT="${1:-outputs/campaign_cluster_run4}"
INTERVAL="${2:-180}"
HEARTBEAT_EVERY="${3:-10}"
WATCH_PY="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/run4_watch.py"
REPO="/c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio"

cd "$REPO" || { echo "close_watch: cannot cd to repo"; exit 1; }

prev=""
cycle=0
while true; do
    cycle=$((cycle + 1))
    out="$(python "$WATCH_PY" "$ROOT" all 2>&1)"
    rc=$?

    # Lines up: count live supervisor/driver processes without matching our own shell.
    lines_up="$(ls "$ROOT"/driver_*.log 2>/dev/null | wc -l | tr -d ' ')"

    # THE DIGEST IS BUILT FROM ALARM-RELEVANT FIELDS ONLY, not from the whole guard output.
    # First version hashed everything except a few lines, which still included `levels={'INFO': N}` --
    # a counter that grows every cycle -- so EVERY cycle reported CHANGE on identical health. That is
    # the same failure this session flagged in the sentinel's gate-failure panel: a watcher that cries
    # change constantly teaches its reader to ignore it. Extract the fields whose MOVEMENT means
    # something and hash only those.
    # THE DIGEST KEYS ON ERROR *KINDS*, NOT ERROR *COUNTS*.
    # Second correction: keying on the count made the watcher fire every cycle once six legs were
    # parked on a known OpenRouter 403, because each 600 s relaunch adds ~30 identical tracebacks.
    # A monotonically rising count of an ALREADY-TRIAGED condition is not news; a NEW kind of error
    # is. So the digest carries the distinct exception/status set, and a novel one fires at once.
    kinds="$(grep -hoE '^[A-Za-z_.]*(Error|Exception):|Error code: [0-9]+' "$ROOT"/driver_*.log 2>/dev/null \
        | sort -u | tr '\n' ',')"
    digest="$(printf '%s|%s' "$kinds" "$(printf '%s' "$out" | grep -oE \
        'foreign=[0-9]+|truncated=[0-9]+|worst_consecutive=[0-9]+|diagnostics=[0-9]+|reject_markers=[0-9]+|ledgered_abandonments=[0-9]+|CRITICAL|STALE DRIVER|reflection_shown=[0-9]+/[0-9]+')" \
        | md5sum | cut -c1-12)"
    # `by_line={...}` is dropped from the emitted summary: it is a dozen figures that change every
    # cycle, which would make every notification unique and drown the signal. The full breakdown is
    # always one `run4_watch.py <root> status` away.
    summary="$(printf '%s' "$out" \
        | grep -E 'reject_markers=|reflection_shown=|llm_calls=|timeout_events=|records=|spend_total=|core_line_spend=|levels=' \
        | sed -E 's/ by_line=.*//; s/ \(canary shield.*//; s/ \(both log formats.*//; s/^ +//' \
        | tr '\n' '|')"
    # error kinds are shown too, so a fired notification says WHICH kind is new rather than only that
    # something changed.
    summary="$summary kinds=[$(printf '%s' "$kinds" | sed 's/,$//')]"

    if [ "$rc" -eq 2 ]; then
        echo "CRITICAL [cycle $cycle] $(date -u +%H:%M:%SZ) driver_logs=$lines_up :: $summary"
        printf '%s\n' "$out" | grep -E 'CRITICAL|FOREIGN|\*\*\*'
    elif [ "$digest" != "$prev" ]; then
        echo "CHANGE   [cycle $cycle] $(date -u +%H:%M:%SZ) driver_logs=$lines_up :: $summary"
    elif [ $((cycle % HEARTBEAT_EVERY)) -eq 0 ]; then
        echo "ok       [cycle $cycle] $(date -u +%H:%M:%SZ) driver_logs=$lines_up :: $summary"
    fi
    prev="$digest"
    sleep "$INTERVAL"
done
