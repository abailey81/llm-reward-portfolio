#!/usr/bin/env bash
# THE 2-MINUTE CADENCE, MACHINE-ENFORCED.
#
# WHY THIS EXISTS (2026-07-31). Tamer's one named complaint about the previous session was that it
# did not monitor constantly, and the answer at handover was to make the sweep ONE command so there
# would be no friction excuse. That was necessary and not sufficient: on 2026-07-31 the RUN 7 session
# still let a 01:20 -> 03:38 gap open (2 h 18 m, 46 records unwatched) while doing deep work, because
# a cadence that depends on an agent remembering to type a command between long tool calls is not a
# cadence -- it is an intention.
#
# publish_status.sh already solved this shape: a detached loop pushes the phone page every 5 minutes
# whether anyone is paying attention or not, and it survived two session handovers. This does the
# same for the monitoring cycle. The agent's job becomes READING the log, not producing it.
#
# WHAT IT DOES. Runs docs/ops/cycle.py every INTERVAL seconds, forever:
#   * every iteration appends one line to docs/ops/watch/CYCLE_LOG.md (cycle.py's own behaviour)
#   * every SSH_EVERY-th iteration also reads cores/jobs off Myriad -- NOT every cycle, because the
#     login node is shared and a 2-minute ssh poll is rude for a number that moves on the hour
#   * anything that is not OK is appended to docs/ops/watch/ALERTS.txt, which is the one file to
#     check after being away: it is empty when nothing has needed a human
#
# It NEVER mutates the campaign, never commits, and never pushes. Safe to run alongside a session
# that is also running cycle.py by hand (STATE.json is rewritten whole, so the worst case is one
# cycle's delta being attributed to the other caller).
#
#   bash docs/ops/cycle_loop.sh                 # foreground, ctrl-C to stop
#   INTERVAL=120 bash docs/ops/cycle_loop.sh    # explicit
#
# Launch it DETACHED so it outlives the session that started it. Stop it by killing its pid.

set -u

cd "$(dirname "$0")/../.." || exit 1

# ── CADENCE ─────────────────────────────────────────────────────────────────────────────────────
# 2026-07-31: Tamer raised the cadence from 2 minutes to 30 SECONDS. Two things must be said honestly
# about what that actually delivers, because the loop is `run; sleep INTERVAL` (sequential, never
# overlapping):
#
#   * THE SWEEP ITSELF TAKES ~12 s (measured: 12.7 s without ssh, 11.0 s with). So INTERVAL=30 gives a
#     REAL cadence of ~42 s, not 30 s, and the duty cycle rises from ~9 % to ~29 %. Verified safe:
#     laptop CPU was 2 % with 16 logical cores at the time of the change.
#   * IT WILL LENGTHEN AS THE ARCHIVE GROWS. The 12 s is dominated by science_watch + results_audit,
#     which each open every record. At C4's full seed ladder (~39,760 trainings) the sweep will take
#     minutes and the effective cadence will be sweep-bound, not sleep-bound. That is NOT a fault --
#     cycles cannot overlap -- but do not expect 30 s to survive C4, and do not "fix" it by sampling
#     the archive: reading every record every cycle is the property that makes `sci=OK` mean anything.
#
# ⚠ SSH_EVERY IS SCALED WITH IT, DELIBERATELY. The cluster read is a poll of a SHARED LOGIN NODE, and
# this file's own note says a 2-minute ssh poll would be rude. Leaving SSH_EVERY=10 while cutting the
# interval 4x would have tripled our polling of a resource other researchers share. 30 x ~42 s keeps
# the cluster read at ~20 minutes, exactly where it was. The cluster numbers move on the hour; the
# PROCESS and RESULTS checks are the ones worth doing more often, and those are now 4x faster.
INTERVAL="${INTERVAL:-30}"      # seconds between cycles -- Tamer, 2026-07-31 (was 120)
SSH_EVERY="${SSH_EVERY:-30}"    # cluster read every Nth cycle (30 x ~42 s = ~20 min, unchanged)

# ── INTERPRETER, PINNED EXPLICITLY (P231, 2026-08-03) ───────────────────────────────────────────
# ⚠⚠ THIS LOOP USED TO CALL A BARE `python`, AND THAT IS AN AMBIENT-PATH DEPENDENCY IN A PROCESS
# NOBODY LAUNCHES BY HAND. Measured after the 16:23:35Z reboot: the boot task starts this loop from
# `scripts/install_onstart_task.ps1`, which runs `bash -lc "cd <repo> && nohup bash
# docs/ops/cycle_loop.sh ..."`, and THAT Git-bash login shell's PATH resolves `python` to the BASE
# interpreter (C:\Users\User\AppData\Local\Programs\Python\Python311) rather than to `.venv`.
# ⚠ CORRECTED on an auditor's finding (F-7): the first version of this comment blamed
# `mode_d_launch.ps1`, which contains no reference to bash, python or this loop at all -- it only
# starts the twelve supervisors. Naming the wrong launcher is not pedantry: the CORRECT chain is
# what reveals that the very next line of the same boot task starts `publish_loop.sh`, which had the
# IDENTICAL defect and was still corrupting the operator-facing status page. The venv carries
# psutil 7.2.2; the base interpreter has no psutil at all -- so from the first post-reboot cycle
# onward `cycle.py` reported "psutil unavailable -- the stale-lock check is BLIND this cycle".
# That string appears in ALERTS.txt exactly twice, both AFTER the reboot and never once in the
# preceding days: the interpreter silently CHANGED underneath a monitor that had been healthy for
# 139 hours, and the only symptom was one check quietly degrading to blind.
#
# It is pinned HERE rather than in `scripts/mode_d_launch.ps1` because `scripts/**` is drift-fenced
# while the campaign is live, and because the loop should not depend on its caller's environment in
# the first place -- the dependency is what made the failure invisible.
#
# AND IT FAILS LOUD RATHER THAN FALLING BACK. A silent `|| PY=python` fallback would restore exactly
# the defect being fixed: the run would continue with a degraded interpreter and say nothing. If the
# venv is gone, that is a fact an operator must be told, not one to route around.
PY=".venv/Scripts/python.exe"
if [ ! -x "$PY" ]; then
    echo "cycle_loop: FATAL - no venv interpreter at $PY (cwd=$(pwd))." >&2
    echo "cycle_loop: refusing to run under an unknown interpreter; psutil and the science tools'" >&2
    echo "cycle_loop: dependencies live in the venv, and running without them degrades checks to" >&2
    echo "cycle_loop: BLIND while still printing a green cycle line." >&2
    exit 1
fi

WATCH="docs/ops/watch"
ALERTS="$WATCH/ALERTS.txt"
mkdir -p "$WATCH"

i=0
last_sig=""        # md5 of the previous cycle's alert lines, timestamps stripped
last_alert_ts=0    # epoch seconds of the last append, for the hourly heartbeat
while true; do
    i=$((i + 1))
    if [ $((i % SSH_EVERY)) -eq 0 ]; then
        out=$("$PY" docs/ops/cycle.py --ssh --interval "$INTERVAL" --note "auto-cycle" 2>&1)
    else
        out=$("$PY" docs/ops/cycle.py --interval "$INTERVAL" --note "auto-cycle" 2>&1)
    fi
    rc=$?

    # rc 0 = nothing needs a human. Anything else is recorded where it will be SEEN, with the full
    # cycle output attached -- a bare "RED at 03:38" costs another investigation to interpret.
    #
    # ⚠ DEDUPED BY CONTENT (2026-07-31). Appending on every non-zero cycle looked right until a
    # PERSISTENT condition arrived: the §56 arm-depth imbalance fires every ~2 minutes and will keep
    # firing for days until the control arms catch up, which had already written 105 near-identical
    # entries and destroyed the one property this file exists for -- "empty means nothing has needed
    # a human". That is the same alarm-fatigue failure being fixed everywhere else in this repo, in
    # the tool built to fix it. A NEW alert must stand out from a standing one.
    #
    # So: append only when the SET of alert/attention lines CHANGES, or once an hour regardless (so a
    # standing condition still leaves a heartbeat and cannot be silently forgotten). Timestamps are
    # stripped before hashing, since they differ every cycle by construction.
    if [ "$rc" -ne 0 ]; then
        sig=$(printf '%s\n' "$out" | grep -E '^(RED|ATTN)' | sed -E 's/[0-9]+/N/g' | sort | md5sum | cut -d' ' -f1)
        now=$(date -u +%s)
        if [ "$sig" != "$last_sig" ] || [ $((now - last_alert_ts)) -ge 3600 ]; then
            if [ "$sig" = "$last_sig" ]; then hdr="STILL PRESENT (hourly heartbeat)"; else hdr="CHANGED"; fi
            {
                printf '\n===== %s  rc=%s  [%s] =====\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$rc" "$hdr"
                printf '%s\n' "$out"
            } >> "$ALERTS"
            last_sig="$sig"; last_alert_ts="$now"
        fi
    fi

    sleep "$INTERVAL"
done
