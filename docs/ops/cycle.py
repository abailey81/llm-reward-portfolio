"""THE 2-MINUTE MONITORING CYCLE -- one command, the whole sweep, a compact verdict.

Tamer's standing order (2026-07-31): **monitor everything, constantly, every 2 minutes.** The reason
the previous session drifted to 20-40 minute gaps was friction -- six separate commands, each with its
own output format, none of which said "nothing changed, carry on". This is that sweep as ONE call.

    python docs/ops/cycle.py                 # the full sweep, ~7 s
    python docs/ops/cycle.py --note "..."     # ...and record what you were doing this cycle
    python docs/ops/cycle.py --ssh            # ...and also read cores/jobs off Myriad (adds ~5-20 s)

WHAT IT CHECKS (everything the campaign can plausibly fail at, cheapest first):
  1. docs/REMOTE_CONTROL.md          -- Tamer's inbound channel; flagged LOUDLY the cycle it changes
  2. the STOP_CAMPAIGN lever         -- present means someone (or something) asked for a halt
  3. campaign_guards.py <root> all   -- the six repo guards (freeze hash, rejects, transport, ...)
  4. docs/ops/arm_coverage.py        -- the guards CANNOT see a missing arm; this can (defect D14)
  5. docs/ops/budget_watch.py        -- per-(line, arm) authoring projection; REPORTED, never RED
  6. driver-log freshness            -- a line can hold its process and stop progressing
  7. drift vs the RUNNING sha        -- what the live drivers execute vs what HEAD now says
  8. records + spend                 -- and the DELTA since the previous cycle, which is the real
                                        health signal: a flat record count across cycles is a stall
  9. THE RESULTS LAYER (see below)   -- science_watch.py + results_audit.py, EVERY cycle

** 9. THE RESULTS LAYER -- Tamer, 2026-07-31 **

    "when you monitor, very deeply and strictly check not only the processes, they must be
     accurate and logical and meaningful as well, but also the RESULTS, they must be very
     logical, correct and meaningful."

Checks 1-8 are all PROCESS: is it running, is it placing, is it spending, is it drifting. A campaign
can pass every one of them and be producing meaningless numbers -- which is the standing rule that a
green check proves execution, never truth. So every cycle now also runs the two tools that open the
science, both of which cost ~1.8 s (MEASURED 2026-07-31, so there is no tiering and no excuse):

  * docs/ops/science_watch.py   -- is the search SEARCHING (non-zero spread), is the reflection chain
                                   ADVANCING, are the scored-record invariants (400k steps, the R115
                                   execution floor) intact, are there impossible numbers?
  * docs/ops/results_audit.py   -- opens every record: reward_source_hash == sha256(source), schema,
                                   ranges, finiteness, the fed block RE-DERIVED from every LLM-arm
                                   prompt, authored-program diversity, PopArt engagement, the D17
                                   repeated-fraction anomaly hunt.

Their numbers are extracted into STATE.json and DIFFED against the previous cycle, because on a live
run the dangerous event is not a bad absolute value -- it is a value that MOVED. Four quantities are
hard validity invariants and go RED on any non-zero reading (a construct-validity leak, a program
shared across arms, a source-hash mismatch, a non-finite metric); the rest escalate on CHANGE.

⚠ EXTRACTION FAILS LOUD. If a regex stops matching -- because a tool's output format changed -- the
cycle says so rather than reporting the check as passed. A monitor that silently stops monitoring is
the D15 failure mode, and it is worse than no monitor at all.

EXIT CODES -- read them, they are the point:
  0  all clear, nothing needs a human
  1  ATTENTION: something changed or is worth a look (new remote instruction, no new records, drift,
     the budget projection, a science quantity that moved)
  2  RED: guards failed, the stop file exists, a driver log is stale, or a RESULTS invariant broke

Every run appends one line to docs/ops/watch/CYCLE_LOG.md and rewrites docs/ops/watch/STATE.json, so
the cadence is auditable after the fact -- "I monitored continuously" becomes a checkable claim rather
than an assertion, which is the standard the rest of this project is held to.

Nothing here mutates the campaign. It is safe at any cadence, including from a loop.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# ⚠⚠ THE MONITOR MUST NEVER CRASH ON ITS OWN OUTPUT. Found live 2026-07-31 (record §74).
#
# THE DEFECT: this script prints alert lines containing non-ASCII markers (★, §, →). When stdout is
# a TERMINAL, Python picks a UTF-8-capable encoding and everything works. When stdout is REDIRECTED
# OR PIPED, Python falls back to the locale codepage -- `cp1251` on this machine -- which cannot
# encode `★` (U+2605), and `print()` raises UnicodeEncodeError. The whole cycle then dies.
#
# WHY THAT WAS CATASTROPHIC RATHER THAN COSMETIC: `docs/ops/cycle_loop.sh` runs this via COMMAND
# SUBSTITUTION -- `out=$(python docs/ops/cycle.py ...)` -- which is a pipe. So in production the
# crashing path was the ONLY path. And the single line that carries `★` is the **C4-BOUNDARY
# DETECTOR** -- the most important operational event in the campaign. On 2026-07-31 the boundary
# was genuinely reached (`frozen_leg_qwen3_5_9b` hit 5/5 frozen winners), the detector fired, the
# print raised, and what landed in ALERTS.txt was a **Python traceback instead of the alert**.
# The instrument failed precisely at the moment it mattered.
#
# THE FIX: force UTF-8 on stdout/stderr with `errors="replace"`, so a rendering limitation can
# degrade a CHARACTER but can never lose a MESSAGE. Belt and braces -- `reconfigure` exists on
# 3.7+, and the guard keeps this safe if stdout is ever a non-reconfigurable stream.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
# ─────────────────────────────────────────────────────────────────────────────

REPO = Path(__file__).resolve().parents[2]
WATCH = REPO / "docs" / "ops" / "watch"
STATE_PATH = WATCH / "STATE.json"
LOG_PATH = WATCH / "CYCLE_LOG.md"
ROOT = REPO / "outputs" / "campaign_cluster_run4"
REMOTE = REPO / "docs" / "REMOTE_CONTROL.md"
ACK_FILE = REPO / "docs" / "ops" / "acknowledged_alarms.txt"

# The commit the LIVE drivers were launched from -- re-based 2026-07-31 by the TMPFS relaunch
# (record section 60). Lineage: c99716e (s.46, memory) -> 2a072df (s.54, priority) -> f5014ce
# (s.58, pack 8) -> 50b6e07 (s.60, tmpfs).
#   * s.58 was the only one that had to move the SUPERVISORS, because PowerShell binds their
#     argument array at supervisor start and --pack lives in that array.
#   * s.46, s.54 and s.60 are DRIVER-only relaunches: they change code the driver imports
#     (jobscript.py / campaign.py), which is rendered laptop-side, so the supervisors relaunch the
#     drivers onto it without themselves restarting.
# Change this ONLY when the drivers are actually relaunched; it is the reference for the drift
# invariant and a wrong value here silently disarms that check.
RUNNING_SHA = "d866afd3"  # re-based 2026-08-01: … -> b38ad14 (§100.40) -> 26807b8 (§100.43/47) -> 775c942d (§100.49, the leg --pipeline-rungs fix) -> 58b388f2 -> a8ff5e64 (RUN 12: src/viz/figures.py::seed_trajectory, D2/registry row 38) -> dd51ba59 -> d866afd3 (RUN 13: D27, CMA-ES generation batching + the chain_progress unit fix; the CORE line was relaunched onto it, and the change is provably unreachable from any leg, so this sha describes every line's behaviour).
# a8ff5e64 is a re-base of the FIRST kind — `docs/ops/import_closure.py`, run over the LIVE diff,
# reports `src.viz.figures` NOT reachable from either entry point, so the running code is untouched
# IN FACT and no relaunch is owed. The figure layer is report-only and is imported by the paper/
# figure build, never by the driver or the on-node worker.
# ⚠ 775c942d IS A DIFFERENT KIND OF RE-BASE AND THE DISTINCTION MATTERS. The three before it moved
# files PROVEN unreachable from the driver, so the running code was untouched in fact. This one
# moves `scripts/mode_d_supervisor.ps1`, which IS the launch path — but PowerShell binds a script
# at PROCESS START, so the eleven live supervisors keep the argument vector they were started with
# and the running campaign is equally untouched. The change is STAGED, not applied: it takes effect
# only when a supervisor is next started. Re-basing here keeps the drift arm honest about what is
# committed; it does NOT assert that the fix is live. It is not, until the leg lines are restarted.
# FENCED FILES HAVE MOVED ACROSS §100.33-§100.40, AND EVERY ONE IS PROVEN OUTSIDE THE DRIVER CLOSURE:
#   * src/inference/multiple_testing.py  -- the structurally-untestable reporting fix (§100.33)
#   * scripts/analyze_campaign.py        -- H1's beat-the-canon IUT reaching the R31 sensitivity (§100.34)
#                                        -- and the stale H4 {H4a,H4b} comment (§100.40, comment only)
#   * scripts/build_paper.py             -- the unread diagnostic channel + the flattened bold (§100.40)
#                                        -- and TeX Gyre Heros + the theory->Appendix C move (§100.47)
#   * scripts/power_analysis.py          -- TEST_TRACK_LENGTH, for the A16 conservative margin (§100.43)
#   * scripts/resume_brief.py            -- the same unpinned-encoding class, outside the closure
#   * src/inference/validity_tier.py     -- node N2's registered non-inferiority rule (§100.43)
# A static walk from scripts/run_campaign_cluster.py + src/cluster/run_one.py reaches 193 first-party
# modules and NONE is among them. The INFERENCE, ANALYSIS and BUILD layers run at analysis/write time,
# never inside a driver, so the executed experiment is untouched and no relaunch was needed. Same
# sanctioned exit as the 402d59e -> b44a566 re-base (§100.19): "prove unreachable with
# docs/ops/import_closure.py, or re-base at restart."
# ⚠ RUN 11: docs/ops/import_closure.py no longer hard-codes its targets — it now derives them from
# the live diff and reads THIS constant to do it, so the proof and the reference can no longer drift
# apart. Run it with no arguments before every re-base; an empty target set reports NOTHING TO CHECK
# rather than passing.
DRIFT_PATHS = ("src", "scripts", "config", "prompts")

# A driver log older than this means its line has stopped writing -- the D14 failure mode, where the
# process is alive (so the supervisor never relaunches it) but no longer progressing.
STALE_DRIVER_MINUTES = 30.0

# Consecutive zero-record cycles before a drought is worth mentioning. At the 2-minute cadence this
# is ~30 minutes, and it re-states every ZERO_DELTA_CYCLES thereafter rather than every cycle.
ZERO_DELTA_CYCLES = 15


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], timeout: int = 120) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=timeout)
    except Exception as exc:  # noqa: BLE001 - a probe that cannot run is itself a finding
        return 99, f"<probe failed: {exc}>"
    return p.returncode, ((p.stdout or "") + (p.stderr or "")).strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16] if path.exists() else ""


def _prev_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


# --------------------------------------------------------------------------------------------------
# THE RESULTS LAYER
# --------------------------------------------------------------------------------------------------
#: Quantities pulled out of the two science tools. Each entry is (key, regex, source) where source is
#: "sw" (science_watch) or "ra" (results_audit). Group 1 of every regex is an integer.
#:
#: These are deliberately ANCHORED on distinctive words rather than on line position, so a tool
#: gaining a line does not silently break extraction -- and any that fails to match is REPORTED,
#: never treated as zero. "Absent" and "zero" are different facts and must never be conflated.
_SCIENCE_FIELDS: tuple[tuple[str, str, str], ...] = (
    ("sw_records",          r"SCIENCE WATCH:\s+(\d+)\s+records",                          "sw"),
    ("sw_budget_breaches",  r"train_safe_call_count\s*!=\s*400,000\s*:\s*(\d+)",           "sw"),
    ("sw_r115_breaches",    r"R115 floor breaches[^:]*:\s*(\d+)",                          "sw"),
    ("sw_impossible",       r"impossible/non-finite scores\s*:\s*(\d+)",                   "sw"),
    ("ra_records",          r"results_audit:\s+(\d+)\s+records",                           "ra"),
    ("ra_dup_runid",        r"duplicate \(root, run_id\)\s*:\s*(\d+)",                     "ra"),
    ("ra_hash_mismatch",    r"reward_source_hash mismatches\s*:\s*(\d+)",                  "ra"),
    ("ra_out_of_range",     r"out-of-range gen/seed\s*:\s*(\d+)",                          "ra"),
    ("ra_non_finite",       r"non-finite metrics\s*:\s*(\d+)",                             "ra"),
    ("ra_scalar_leaks",     r"scalar prompts leaking a tail statistic\s*:\s*(\d+)",        "ra"),
    ("ra_cross_arm_shared", r"programs identical ACROSS arms\s*:\s*(\d+)",                 "ra"),
    ("ra_popart_engaged",   r"engaged\s+(\d+)\s+\(",                                       "ra"),
    ("ra_popart_pinned",    r"pinned at the floor\s+(\d+)\s+\(",                           "ra"),
    ("ra_popart_breaks",    r"invariant sigma_max ==[^:]*:\s*(\d+)",                       "ra"),
    # Per-arm candidate counts, for the ARM-DEPTH check below.
    #
    # ★ 2026-08-01 (RUN 10): these read `pool=` from results_audit's new §3b, NOT `records=` from
    # its diversity pass. The diversity counts include the H3 SINGLE-SHOT control, which writes
    # `arm='distributional'` into its own `*_h3_singleshot/` subtrees and is a DISJOINT hypothesis
    # condition — `analyze_campaign.py`'s walker skips it for exactly this reason. Pooling it made
    # this alarm read **2.39x** for a quantity whose value is **1.30x**, and — because h3ss entered
    # packed C4 at ~116 records/h, all tagged distributional — it was about to climb through 3x, 4x,
    # 5x WHILE THE REAL H2 IMBALANCE IMPROVED (the core line went 1.87x -> 1.65x the same night).
    # An alarm that rises as its own risk falls trains the operator to ignore the one number
    # guarding the headline hypothesis. Raised by the ANALYSIS lane, verified first-hand, fixed at
    # the source rather than by adjusting the threshold.
    ("n_distributional",    r"^\s*distributional\s+pool=(\d+)",                            "ra"),
    ("n_scalar",            r"^\s*scalar\s+pool=(\d+)",                                    "ra"),
    ("n_placebo",           r"^\s*placebo\s+pool=(\d+)",                                   "ra"),
    ("n_scalar_cvar5",      r"^\s*scalar_cvar5\s+pool=(\d+)",                              "ra"),
    ("n_placebo_shuffled",  r"^\s*placebo_shuffled\s+pool=(\d+)",                          "ra"),
)

#: ARM DEPTH. The four arms of H2's 3-leg IUT: `distributional` must beat `scalar`, `placebo` AND
#: `scalar_cvar5` (PREREGISTRATION.md line 94). Each arm's frozen winner is `max(val_fitness)` over
#: its ACCEPTED candidates, and the expectation of a maximum RISES with the number of draws — so an
#: arm with half the pool fields a systematically weaker winner and its IUT leg becomes easier to
#: reject than the design intends, biasing TOWARD a false positive for our own hypothesis.
#:
#: This is not hypothetical. On 2026-07-31 the `-p` ladder (§54) had left the two treatment arms at
#: 82 %/79 % of the registered 30-candidate budget and the two control comparators at 40 %/36 % —
#: a 2.27x pool asymmetry on one IUT leg (§56). Every guard was green throughout: `arm_coverage.py`
#: asserts every arm is SUBMITTING, and nothing watched how DEEP each arm had got.
#: ⚠ DENOMINATOR, stated because this ratio is a monitoring signal and not the reportable figure:
#: `results_audit` counts records across ALL roots, which includes the `h3ss` single-shot line (a
#: `distributional`-only line, ~29 records) and the handful of `frozen/*-winner` markers. That
#: inflates the `distributional` count relative to the others, so the spread printed here is an
#: UPPER BOUND on the imbalance. The exact search-only figures — 272/262/131/120, a 2.27x worst leg
#: — are derived in §56 and are the ones to quote. The bound is the right thing for an alarm: it is
#: conservative in the direction of noticing.
_IUT_ARMS = ("n_distributional", "n_scalar", "n_placebo", "n_scalar_cvar5")
#: Ratio of the largest to the smallest IUT-arm pool at which the imbalance is worth a look. Arms
#: legitimately progress at different rates mid-run, so this is deliberately not a hard failure —
#: but it must be SEEN every cycle rather than discovered at analysis time.
_ARM_SPREAD_ATTN = 1.5

#: Non-zero on ANY of these is a validity failure, not a slowdown -- it means the experiment is no
#: longer measuring what it was registered to measure. Each names the hypothesis it would destroy.
_HARD_ZERO: dict[str, str] = {
    "ra_scalar_leaks":     "a SCALAR-arm prompt contains a tail statistic -- H2's manipulation has "
                           "leaked and the arm contrast is no longer clean",
    "ra_cross_arm_shared": "an authored program is IDENTICAL across two arms -- the arms are no "
                           "longer independent draws and H2 compares contaminated populations",
    "ra_hash_mismatch":    "reward_source_hash != sha256(reward_source) -- an archived reward is not "
                           "the reward that was run, so the record cannot be replayed",
    "ra_non_finite":       "a non-finite metric is archived -- it will propagate into the analysis",
    "ra_out_of_range":     "a generation or seed is outside the registered range",
    "sw_impossible":       "an impossible/non-finite score is present in a scored record",
    "sw_budget_breaches":  "a scored record's train_safe_call_count != 400,000 -- the registered "
                           "training budget was not honoured",
    "ra_popart_breaks":    "the PopArt invariant sigma_max == max(floor, raw_rms_max) is broken",
}

#: Quantities that legitimately grow on a live run. A rise is worth a LOOK, never a halt -- but it
#: must be SEEN, because "it drifted slowly" is how a real regression hides in a healthy-looking run.
_WATCH_RISING: dict[str, str] = {
    "sw_r115_breaches": "R115 execution-floor breaches",
    "ra_dup_runid":     "duplicate (root, run_id) pairs -- D18 baseline is 1",
}


def _results_layer(prev: dict, alerts: list[str], attention: list[str]) -> dict:
    """Run the two science tools, extract their numbers, and judge them against the invariants.

    Returns the extracted quantities for STATE.json. Escalates through `alerts` / `attention` in
    place. Never raises: a probe that cannot run is itself reported as a finding.
    """
    # 2026-08-01 (RUN 10): run the two archive walks CONCURRENTLY. They are independent, read-only,
    # and each re-reads every record, so serialising them doubled the one component of the sweep that
    # GROWS with the campaign. Measured on 1,730 records: 2.89 s + 2.79 s serial -> ~2.9 s together.
    #
    # ⚠ THIS IS A SCHEDULING CHANGE, NOT A SAMPLING ONE. Both tools still read EVERY record, which is
    # what makes `sci=OK` mean anything; the brief's standing warning is against sampling the archive
    # to make the sweep cheap, and nothing here touches what is read or how it is judged.
    #
    # ⚠ AND THE FIGURES THE BRIEF CARRIES ARE WRONG, MEASURED 2026-08-01. It states the sweep is
    # "linear in archive size (~6.3 ms/record)" heading for "~250 s at the full ladder", and that a
    # 46.1 s reading proved it. Both halves fail measurement: the two archive tools cost **3.3
    # ms/record combined** (5.68 s over 1,730), so the full-ladder projection is ~117 s serial and
    # ~58 s concurrent, not 250 s; and the 46.1 s outlier was **ssh contention from RUN 10's own
    # 12-way driver relaunch**, not archive growth — every neighbouring cycle read 9-15 s at the same
    # archive size. The real components at 1,730 records: archive 5.7 s, budget_watch 2.7 s, ssh
    # qstat 1.5 s, git drift 0.08 s, plus ~1 s interpreter start per subprocess.
    #
    # THE SWEEP IS THEREFORE NOT BINDING TODAY (13-15 s against a 30 s interval) and becomes binding
    # near **~9,000 records**. The durable fix is an INCREMENTAL cache keyed on (path, mtime, size)
    # — still reading every record ONCE, retaining its verdict — and it is deliberately NOT built
    # here: these two tools ARE the science verdict, and a caching bug would produce a reassuring
    # `sci=OK` from an instrument that cannot fire, which is the worst failure mode this project has.
    # It ships as its own change, with a falsification asserting cached and uncached output are
    # byte-identical on the live archive.
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as _ex:
        _sw = _ex.submit(_run, [sys.executable, "docs/ops/science_watch.py"], 300)
        _ra = _ex.submit(_run, [sys.executable, "docs/ops/results_audit.py"], 300)
        sw_rc, sw_out = _sw.result()
        ra_rc, ra_out = _ra.result()
    text = {"sw": sw_out, "ra": ra_out}

    got: dict[str, int | None] = {}
    unparsed: list[str] = []
    for key, pattern, src in _SCIENCE_FIELDS:
        # MULTILINE: several patterns anchor with ``^`` to pin a value to the start of its own line
        # (so ``scalar`` cannot match inside ``scalar_cvar5``). Without re.M, ``^`` matches only the
        # start of the whole blob and every one of those patterns silently fails -- which is exactly
        # what happened when the arm-depth fields were added, and what the fail-loud branch caught.
        m = re.search(pattern, text[src], re.M)
        if m:
            got[key] = int(m.group(1))
        else:
            got[key] = None
            unparsed.append(key)

    # A tool that fails to RUN, and a field that fails to PARSE, are both blind spots. Say so.
    if ra_rc == 2:
        alerts.append("results_audit rc=2 -- a HARD record invariant failed. Read its output in full "
                      "before anything else; this is a validity failure, not a slowdown.")
    if sw_rc not in (0, 1):
        alerts.append(f"science_watch rc={sw_rc} -- the science check could not complete")
    if unparsed:
        attention.append(f"results layer: could NOT parse {', '.join(unparsed)} -- the tool's output "
                         f"format may have changed. These checks are BLIND until fixed; absent is "
                         f"not the same as zero.")

    for key, why in _HARD_ZERO.items():
        val = got.get(key)
        if val:
            alerts.append(f"RESULTS INVARIANT BROKEN -- {key}={val}: {why}")

    for key, label in _WATCH_RISING.items():
        val, was = got.get(key), (prev.get("science") or {}).get(key)
        if isinstance(val, int) and isinstance(was, int) and val > was:
            attention.append(f"{label} rose {was} -> {val} since the previous cycle -- identify the "
                             f"new one and confirm it is the known mechanism, not a new failure")

    # R115 BINDING means a fallback-contaminated candidate currently TOPS its arm. That is the floor
    # doing its job (record §35), but the moment it happens on a line whose winner is about to be
    # frozen it stops being academic -- so its ARRIVAL is surfaced, not just its presence.
    binding = "R115 IS BINDING" in sw_out
    got["sw_r115_binding"] = int(binding)
    if binding and not (prev.get("science") or {}).get("sw_r115_binding"):
        attention.append("R115 is now BINDING -- a fallback-contaminated candidate tops its arm. "
                         "Expected behaviour of the floor; confirm the affected line and that the "
                         "best ELIGIBLE candidate is the one that gets frozen.")

    # ★ C4-BOUNDARY DETECTOR. A line enters the seed ladder once all five of its arms have a frozen
    # winner. That boundary is the ONLY window in which `--pack 8` can be applied, and applying it is
    # worth roughly half the rung-568 makespan (§50) -- at the core counts measured on 2026-07-31,
    # rung 568 lands 08-30 (MISSING the Aug-27 stop) without the extra concurrency.
    #
    # ⚠ AND IT IS A HEAVIER OPERATION THAN IT LOOKS. `--pack 4` is hard-coded in the ARGUMENT ARRAY of
    # `scripts/mode_d_supervisor.ps1`, and PowerShell binds that array when the SUPERVISOR starts --
    # not when it relaunches a driver. So `--pack 8` requires restarting the twelve SUPERVISORS, which
    # is the full teardown, not the gentle driver-only relaunch used for §46 and §54. Miss the window
    # and C4 runs at half the cores for its entire duration.
    #
    # ⚠⚠ CORRECTED 2026-07-31 (RUN 9, record §91). THIS COULD FIRE EARLY ON THE **CORE** LINE.
    # The old predicate counted EVERY `frozen*/<arm>-winner/` marker in a line and fired at >= 5. That
    # is right for a LEG, which runs only the five LLM arms -- but the CORE line (`frozen/`) also runs
    # the FOUR H4 optimiser arms (`random_search`, `bayes_opt`, `cma_es`, `tpe`; PREREGISTRATION.md §3,
    # "The nine arms"), so `frozen/` accumulates up to NINE markers. It can therefore reach 5 with as
    # few as ONE LLM arm frozen, and it is ALREADY contaminated: at the time of writing `frozen/` held
    # `distributional-winner`, `random_search-winner`, `scalar-winner` -- reported as "3/5" everywhere,
    # when the confirmatory count is **2 of 5**.
    #
    # WHY IT MATTERS: this alert is the TRIGGER for the deferred-fix relaunch decision -- the one action
    # §12.1 describes as "the relaunch that protects a confirmatory quantity". Firing it while the core
    # line's LLM arms are still searching would invite exactly the mid-search relaunch §75.1 argues
    # against, on the only line whose numbers are confirmatory.
    #
    # AND THE OPPOSITE DEFECT, in the same predicate: `frozen_h3_singleshot/` runs ONE arm
    # (`distributional`), so it can never reach 5 and **the h3 line's boundary was undetectable**.
    #
    # THE FIX: count only the five LLM arms' winners, and require ALL the LLM arms that line actually
    # runs -- read from the line's own `search*` directory rather than assumed, so a roster change
    # cannot silently re-open this.
    _LLM_ARMS = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")
    frozen_by_line: dict[str, int] = {}          # LLM-arm winners only (the confirmatory count)
    all_markers_by_line: dict[str, int] = {}     # every marker, kept for the status line
    for marker in ROOT.glob("frozen*/*-winner/record.json"):
        line = marker.parent.parent.name
        all_markers_by_line[line] = all_markers_by_line.get(line, 0) + 1
        if marker.parent.name[: -len("-winner")] in _LLM_ARMS:
            frozen_by_line[line] = frozen_by_line.get(line, 0) + 1
    got["frozen_winners_by_line"] = frozen_by_line
    got["frozen_markers_by_line"] = all_markers_by_line
    # ⚠⚠ CORRECTED AGAIN 2026-08-02 (RUN 13). The 2026-07-31 fix above closed the half where the CORE
    # line fired EARLY on a count contaminated by H4 markers -- and left the other half open. The C1
    # barrier in `campaign.run_tiered_campaign` is `as_completed` over EVERY arm in `arms`, not over
    # the five LLM arms, so on the core line it also waits for `bayes_opt`, `cma_es` and `tpe`.
    # Measured this session: all five core LLM arms are frozen, yet `cma_es` stood at 9 of its 30
    # candidates and is STRICTLY SEQUENTIAL (each CMA-ES proposal is a function of the fitnesses
    # already observed), i.e. ~7.5 days of chain still to run. The alert nonetheless announced
    # "the seed ladder has begun on that line" for `frozen/`.
    #
    # It also announced it for six LEG lines that were still running C1 TEST blocks -- freezing a
    # winner is upstream of the test leg, the C1 barrier, C2's h2_pair and the C3 gate.
    #
    # `session_preflight.py`'s `c4_entered` check greps the driver logs for `[C4|pipelined]` and read
    # ZERO at the same moment. Two instruments disagreed, and the one that OBSERVES beats the one that
    # INFERS. So: require every arm the line actually runs (LLM *and* family, read from its own
    # `search*` directory so a roster change cannot re-open this), and state the claim as the
    # PRECONDITION it is rather than as an observation of C4.
    _FAMILY_ARMS = ("random_search", "bayes_opt", "cma_es", "tpe")
    ready = []
    for line, n_frozen in frozen_by_line.items():
        # How many arms does this line actually run? `frozen_leg_x` <-> `search_leg_x`.
        search_dir = ROOT / ("search" + line[len("frozen"):])
        if not search_dir.is_dir():
            expected_llm, expected_fam, got_fam = 5, 0, 0
        else:
            expected_llm = sum(1 for a in _LLM_ARMS if (search_dir / a).is_dir())
            expected_fam = sum(1 for a in _FAMILY_ARMS if (search_dir / a).is_dir())
            got_fam = sum(1 for a in _FAMILY_ARMS
                          if (ROOT / line / f"{a}-winner" / "record.json").exists())
        if expected_llm and n_frozen >= expected_llm and got_fam >= expected_fam:
            ready.append(line)
    ready = sorted(ready)
    got["lines_at_c4_boundary"] = ready
    if ready:
        alerts.append(
            f"★ C4 PRECONDITION MET on {', '.join(ready)} (every arm that line runs has a frozen "
            f"winner). This is the FREEZE boundary, NOT evidence that the ladder has begun: the test "
            f"leg, the C1 barrier, C2's h2_pair and the C3 gate all sit between here and C4. The "
            f"OBSERVATION of C4 is `[C4|pipelined]` in a driver log -- "
            f"`python docs/ops/session_preflight.py` reports it as `c4_entered`. "
            f"✔ `--pack 8` IS ALREADY LIVE (§58, applied 2026-07-31 by a rolling "
            f"supervisor restart; VERIFIED 2026-07-31 19:35 UTC on all 24 driver command lines, and "
            f"visible in the C4 job names as 4 packs for 30 seeds, e.g. `..._test_p01..p04`). "
            f"*** DO NOT RESTART THE SUPERVISORS FOR PACK 8 -- IT IS DONE. *** "
            f"✔ AND THE DEFERRED FIXES ARE DEPLOYED TOO (2026-08-01, RUN 10, commit 402d59e): "
            f"D13 D14 D15 D18 D20 D21 + the §39 constant + the timeout counter + A15, on all 24 "
            f"drivers, drift 0, freeze MATCHES. *** DO NOT RELAUNCH FOR THEM EITHER. *** "
            f"This line previously read \"What REMAINS ... is the outstanding DEFERRED_FIXES\" and "
            f"listed items that are now APPLIED -- a STANDING alert carrying a STALE instruction is "
            f"how a session is told to redo finished work, which is exactly what the pack-8 half of "
            f"this same alert had to be corrected for on 2026-07-31. "
            f"STILL OPEN and NOT worth disturbing a live ladder for: item 3 (preflight headroom, "
            f"cannot affect anything live), item 12/D19 (search h_rt -- the tight lane ends first), "
            f"D17 (NEVER while live: it changes reward-evaluation semantics on the training path). "
            f"Records §74, §100.")

    # ★ CORE-LINE ARM DEPTH -- the ratio that actually gates the CONFIRMATORY claim.
    #
    # ⚠ CORRECTION 2026-07-31, found by an independent auditor (record §56.6). The pooled 11-line
    # ratio below is NOT the confirmatory quantity. Winner selection is per (line, arm), and the ten
    # `search_leg_*` roots are REPORT-ONLY (R80) — the confirmatory H2 IUT draws from the Opus core
    # line `search/` ALONE. Measured the same minute: pooled says 2.22x on the worst leg, the core
    # line says **3.11x** (`scalar_cvar5` 9 candidates against `distributional` 28). Reporting only
    # the pooled figure understated the confirmatory threat by ~40 %.
    core_pools: dict[str, int] = {}
    for arm in ("distributional", "scalar", "placebo", "scalar_cvar5"):
        core_pools[arm] = sum(1 for _ in (ROOT / "search" / arm).glob("*/record.json"))
    got["core_line_pools"] = core_pools
    if all(core_pools.values()):
        c_hi, c_lo = max(core_pools.values()), min(core_pools.values())
        got["core_arm_spread"] = round(c_hi / c_lo, 3)
        if c_hi / c_lo >= _ARM_SPREAD_ATTN:
            worst = min(core_pools, key=lambda k: core_pools[k])
            attention.append(
                f"CORE-LINE arm depth {c_hi / c_lo:.2f}x — {worst}={c_lo} against {c_hi}. This is the "
                f"CONFIRMATORY pool (the legs are report-only, R80), so this ratio — not the pooled "
                f"one — is what biases H2's IUT legs. Record §56.6.")
    else:
        got["core_arm_spread"] = None

    # ARM DEPTH, pooled across all eleven lines -- context, not the confirmatory quantity.
    pools = {k: got.get(k) for k in _IUT_ARMS if isinstance(got.get(k), int) and got.get(k)}
    if len(pools) == len(_IUT_ARMS):
        lo_k, lo = min(pools.items(), key=lambda kv: kv[1])
        hi_k, hi = max(pools.items(), key=lambda kv: kv[1])
        ratio = hi / lo
        got["arm_pool_spread"] = round(ratio, 3)
        got["arm_pool_min"] = lo_k[2:]
        if ratio >= _ARM_SPREAD_ATTN:
            attention.append(
                f"ARM DEPTH IMBALANCE {ratio:.2f}x across H2's IUT arms "
                f"({hi_k[2:]}={hi} vs {lo_k[2:]}={lo}). Each arm's winner is max(val_fitness) over "
                f"its pool and E[max] rises with n, so a starved comparator makes its IUT leg easier "
                f"to reject -- biased TOWARD a false positive. Record §56; the pre-registered remedy "
                f"is the equal-k sensitivity analysis (§26.3).")
    else:
        got["arm_pool_spread"] = None

    got["science_watch_rc"] = sw_rc
    got["results_audit_rc"] = ra_rc
    return got


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--note", default="", help="one line: what you are doing this cycle")
    ap.add_argument("--ssh", action="store_true", help="also read cores/jobs off Myriad")
    ap.add_argument("--quiet", action="store_true", help="print the verdict line only")
    ap.add_argument("--interval", type=float, default=0.0,
                    help="the loop's sleep interval, so the sweep can warn when it EXCEEDS it")
    args = ap.parse_args()
    _t_sweep0 = time.monotonic()

    WATCH.mkdir(parents=True, exist_ok=True)
    prev = _prev_state()
    stamp = _utc()
    alerts: list[str] = []      # exit 2
    attention: list[str] = []   # exit 1
    info: list[str] = []        # reported every cycle, never changes the exit code
    lines: list[str] = []

    if not ROOT.exists():
        print(f"RED  campaign root missing: {ROOT}", file=sys.stderr)
        return 2

    # 1. Tamer's channel, first, always -- anything he wrote outranks everything below it.
    remote_hash = _sha256(REMOTE)
    remote_changed = bool(prev) and remote_hash != prev.get("remote_control_sha", remote_hash)
    if remote_changed:
        attention.append("*** docs/REMOTE_CONTROL.md CHANGED -- READ IT NOW, before anything else ***")

    # 2. the stop lever
    stop_file = ROOT / "STOP_CAMPAIGN"
    if stop_file.exists():
        alerts.append(f"STOP_CAMPAIGN EXISTS at {stop_file} -- the campaign is being halted")

    # 3-5. the three monitors, filtered through the ACKNOWLEDGED ledger.
    #
    # Alarm hygiene is the whole point (docs/ops/acknowledged_alarms.txt: "make the KNOWN quiet so the
    # NEW is loud"). Two guard verdicts and two sentinel CRITICALs are permanently rc=2 because the
    # underlying ledgers are append-only and can never return green -- so a raw rc=2 every cycle would
    # train the operator to ignore rc=2, which is precisely how D15 survived ten hours. Anything in the
    # ledger is reported as (known); anything NOT in it is RED.
    acked = {ln.strip() for ln in ACK_FILE.read_text(encoding="utf-8").splitlines()
             if ln.strip() and not ln.lstrip().startswith("#")} if ACK_FILE.exists() else set()

    guards_rc, guards_out = _run([sys.executable, "scripts/campaign_guards.py",
                                  str(ROOT.relative_to(REPO)), "all"], timeout=300)
    failing = [ln.split("]")[0].lstrip("[") for ln in guards_out.splitlines()
               if ln.startswith("[") and not ln.rstrip().endswith(" ok")]
    new_guards = [g for g in failing if f"guard:{g}" not in acked]
    known_guards = [g for g in failing if f"guard:{g}" in acked]
    if new_guards:
        alerts.append(f"campaign_guards: UNACKNOWLEDGED verdict(s) {', '.join(new_guards)} "
                      f"-- investigate, then either fix or add a REASONED entry to "
                      f"docs/ops/acknowledged_alarms.txt")
    elif guards_rc != 0 and not failing:
        attention.append(f"campaign_guards rc={guards_rc} but no failing guard parsed -- read the output")

    cov_rc, cov_out = _run([sys.executable, "docs/ops/arm_coverage.py"], timeout=120)
    full_lines = cov_out.count("5/5 arms submitted")
    if "VERDICT: ALL LINES FULL" not in cov_out:
        alerts.append("arm_coverage: A LINE IS MISSING AN ARM (defect D14) -- the six repo guards "
                      "cannot see this. Find which arm, and why it stopped being submitted.")
    sentinel_bad = re.findall(r"^\[sentinel\]\s+(CRITICAL|UNKNOWN)\s+(\S+)", cov_out, flags=re.M)
    new_sentinel = [f"{chk}:{sev}" for sev, chk in sentinel_bad if f"{chk}:{sev}" not in acked]
    known_sentinel = [f"{chk}:{sev}" for sev, chk in sentinel_bad if f"{chk}:{sev}" in acked]
    if new_sentinel:
        alerts.append(f"sentinel: UNACKNOWLEDGED verdict(s) {', '.join(new_sentinel)} -- a CRITICAL "
                      f"is a VALIDITY issue, not a slowdown. Run it to ground before anything else.")

    # 4b. THE SANDBOX ALLOWLIST GAP (record §100.31). `SAFE_BUILTINS` exposes np + 31 builtins and NO
    # exception type, while the AST gate has no opinion on Try/ExceptHandler -- so a reward writing
    # `try: ... except Exception:` PASSES the gate and dies on `NameError: name 'Exception' is not
    # defined`, on the very line meant to make it robust. NOT fixed in code: SAFE_BUILTINS is
    # reward-evaluation semantics on the training path (D17, never while live), and changing it would
    # split the archive into two evaluation instruments for a measured exposure of ~0.03 candidates.
    # So the hazard is made VISIBLE instead: 13 programs carry it LATENT (10 on confirmatory paths),
    # harmless until a try-block actually raises, because Python resolves an exception name only when
    # an exception occurs. This alerts if one ever FIRES on a confirmatory path -- the single case
    # that would mean a candidate was lost to OUR defect rather than to its own logic.
    #
    # TIME-GUARDED (not every cycle): the scan AST-parses every distinct reward source, ~6 s at 2,300
    # records and growing with the archive. The hazard fires at most once, so a 10-minute detection
    # latency costs nothing while an unbounded per-cycle scan would eat the sweep budget.
    # HARD-WRAPPED: this check must never be able to break the monitoring loop.
    try:
        _gap_stamp = Path("docs/ops/watch/.sandbox_gap_last")
        _due = (not _gap_stamp.exists()
                or (time.time() - _gap_stamp.stat().st_mtime) > 600)
        if _due:
            _gap_rc, _gap_out = _run([sys.executable, "docs/ops/sandbox_gap_watch.py", "--quiet"],
                                     timeout=180)
            _gap_stamp.parent.mkdir(parents=True, exist_ok=True)
            _gap_stamp.write_text(f"{_gap_rc}\n{_gap_out}", encoding="utf-8")
        else:
            _gap_rc = int((_gap_stamp.read_text(encoding="utf-8").splitlines() or ["0"])[0])
        if _gap_rc == 1:
            alerts.append(
                "sandbox_gap: a reward on a CONFIRMATORY path has MANIFESTED the SAFE_BUILTINS "
                "allowlist gap -- a candidate was lost to OUR defect, not to its own logic. It reads "
                "~50% fallback (the state-reset limit cycle), so R115 will have excluded it. Record "
                "§100.31; decide with Tamer whether that candidate is re-authored.")
        elif _gap_rc not in (0, 1):
            # A WATCHER THAT CANNOT RUN IS ITSELF A FINDING (_run's own comment says so, and it
            # returns rc=99 rather than raising). Without this branch a broken sandbox_gap_watch would
            # simply stop watching and NOTHING would say so -- the silent-blind-spot failure this
            # whole file exists to prevent.
            attention.append(f"sandbox_gap: the watcher could not run (rc={_gap_rc}) -- the latent "
                             f"allowlist-gap hazard is currently UNWATCHED. Record §100.31.")
    except Exception as _gap_exc:                        # noqa: BLE001 - must never break the sweep
        # ⚠ print, NOT a logger. cycle.py defines no module logger, and the first draft of this
        # handler called `_LOG.warning(...)` -- which would have raised NameError *inside the except
        # block*, propagating out and breaking the very sweep the guard exists to protect. A
        # fail-safe whose failure path can itself fail is not a fail-safe.
        print(f"[cycle] sandbox_gap check failed (non-fatal): {_gap_exc!r}", file=sys.stderr)

    # 4c. THE CONFIRMATORY-PATH INTEGRITY GATE (record §100.32). Six invariants that must hold for the
    # results to mean anything: I1 every record's hash matches its own source · I2 each frozen winner
    # equals the search candidate it won as · I3 each TEST record equals its arm's frozen winner (the
    # one whose breach would invalidate the headline) · I4 each frozen winner is the max-fitness
    # R115-ELIGIBLE candidate of its arm · I5 requested model == served model · I6 max_tokens and
    # temperature match the registration.
    #
    # WHY IT IS AUTOMATED RATHER THAN AUDITED. All six were verified BY HAND on 2026-08-01 and were
    # clean (32/32 winners correct, 0 hash mismatches over 1,024 frozen+test records). That was a
    # SNAPSHOT. The campaign runs to 08-27 and nobody re-runs a hand audit daily, so any of these could
    # break tomorrow with nothing to say so. The gate encodes VERIFIED-TRUE invariants, which is what
    # makes a future red meaningful: a check that has never been green against known-good data cannot
    # tell you anything when it fails. 15 falsification tests prove each invariant can FIRE
    # (tests/test_integrity_gate.py), including the two that must NOT fire -- an R115-ineligible best
    # candidate, and the DISCLOSED kimi alias of §100.26.
    #
    # rc 2 = CONFIRMATORY breach (RED) · rc 1 = report-only leg breach (ATTN, R80 never gates H1-H4)
    # · rc 0 = clean. Same 600 s time-guard and hard wrap as 4b, for the same reasons.
    try:
        _int_stamp = Path("docs/ops/watch/.integrity_gate_last")
        _int_due = (not _int_stamp.exists()
                    or (time.time() - _int_stamp.stat().st_mtime) > 600)
        if _int_due:
            _int_rc, _int_out = _run([sys.executable, "docs/ops/integrity_gate.py", "--quiet"],
                                     timeout=300)
            _int_stamp.parent.mkdir(parents=True, exist_ok=True)
            _int_stamp.write_text(f"{_int_rc}\n{_int_out}", encoding="utf-8")
        else:
            _int_rc = int((_int_stamp.read_text(encoding="utf-8").splitlines() or ["0"])[0])
        if _int_rc == 2:
            alerts.append(
                "integrity_gate: a CONFIRMATORY-PATH INVARIANT IS BREACHED -- the search->frozen->test "
                "code chain, the winner selection, or a model/decoding pin no longer holds. THE "
                "HEADLINE RESULT CANNOT BE TRUSTED until this is run to ground. "
                "Run `python docs/ops/integrity_gate.py` for the detail. Record §100.32.")
        elif _int_rc == 1:
            attention.append("integrity_gate: an invariant is breached on a REPORT-ONLY leg (R80, "
                             "never gates H1-H4). Not a run-stopper -- but find the cause. §100.32.")
        elif _int_rc != 0:
            attention.append(f"integrity_gate: the gate could not run (rc={_int_rc}) -- the "
                             f"confirmatory-path invariants are currently UNCHECKED. §100.32.")
    except Exception as _int_exc:                        # noqa: BLE001 - must never break the sweep
        print(f"[cycle] integrity_gate check failed (non-fatal): {_int_exc!r}", file=sys.stderr)

    # 5. the budget. TAMER, 2026-07-31: "The budget is fine, cross it out, I will just top up whenever
    # needed, I watch the balance. Just make sure you precisely monitor it as well."
    #
    # So the OWNER holds the balance and the top-up decision, and this check stops being a run-stopper.
    # It is NOT dropped -- it is downgraded from RED to a REPORTED number, because the thing it was
    # comparing against was never observable to us: `budget_watch.CREDIT` is a LEDGER ESTIMATE from a
    # 2026-07-28 console quote (record §49.3), and Tamer tops up ad hoc, so the credit side of that
    # comparison is stale by design. Escalating on a number we cannot observe is the alarm-hygiene
    # failure this file exists to prevent. What we CAN observe precisely -- spend to date and the
    # projected remaining authoring cost -- is extracted and logged every cycle instead.
    bud_rc, bud_out = _run([sys.executable, "docs/ops/budget_watch.py"], timeout=180)
    budget: dict[str, dict[str, float]] = {}
    for m in re.finditer(r"^(anthropic|openrouter)\s+spent \$\s*([0-9.]+)\s*\+ still to author "
                         r"\$\s*([0-9.]+)\s*= \$\s*([0-9.]+)", bud_out, flags=re.M):
        budget[m.group(1)] = {"spent": float(m.group(2)), "to_author": float(m.group(3)),
                              "projected_total": float(m.group(4))}
    if not budget:
        attention.append("budget_watch: could not parse the per-provider projection -- that number is "
                         "BLIND this cycle, which is not the same as healthy")
    else:
        for prov, b in sorted(budget.items()):
            was = ((prev.get("budget") or {}).get(prov) or {}).get("spent")
            delta = f" ({b['spent'] - was:+.4f} this cycle)" if isinstance(was, (int, float)) else ""
            info.append(f"budget {prov:<10} spent ${b['spent']:.4f}{delta}  + to author "
                        f"${b['to_author']:.4f}  = projected ${b['projected_total']:.4f}")

    # 5b. ★ STALE DRIVER LOCKS (D20, found live 2026-07-31 — it had stranded the h3 line).
    #
    # `_acquire_driver_lock` writes the owner pid and, on collision, breaks the lock only if
    # `psutil.pid_exists(pid)` is False. **That check cannot survive PID REUSE.** Windows recycled a
    # dead driver's pid onto `OpenConsole.exe`; `pid_exists` said True, the lock was never broken, and
    # the h3 line sat refusing to start — 0 drivers, supervisor retrying into the same wall, log going
    # stale — with every guard green. The driver's own error text anticipates it ("If that pid is NOT
    # a driver, delete ... and relaunch"), which is precisely the manual step nobody was there to take.
    #
    # The right test is not "does the pid exist" but "is the pid A DRIVER". That is cheap to check
    # here, and it is the difference between a self-healing lock and a silently stranded line.
    # ★★ 2026-08-01 (RUN 10, record §100): DETECTION WAS NOT ENOUGH — IT NOW SELF-HEALS.
    # The detector above fired correctly on `leg4_leg_qwen3_5_9b_h2_pair_test.driver.lock` (owner pid
    # 34216 recycled onto `backgroundTaskHost.exe`) and the line — one of the two ALREADY AT C4 — sat
    # in a permanent 600 s crash-loop, dying 12 s into every relaunch, for as long as no human was
    # awake to run the one-line `rm`. **An alarm whose remedy is a manual command is an alarm that
    # fails while you sleep.** So the cycle now performs the remedy the driver's own error text
    # prescribes, under a predicate STRICTLY NARROWER than the one that would make it unsafe:
    #
    #   reap  iff  the owner pid EXISTS  and  its cmdline was read SUCCESSFULLY  and  is NON-EMPTY
    #              and  does NOT contain `run_campaign_cluster`  and  the lock is >= 60 s old
    #
    # Every clause earns its place:
    #   * pid EXISTS          — a dead owner is already handled by `_acquire_driver_lock` itself.
    #   * cmdline read OK     — an AccessDenied must NEVER be read as "not a driver" (that would
    #                           delete a LIVE driver's lock and permit the double-drive the lock
    #                           exists to prevent). Any read failure means SKIP.
    #   * cmdline NON-EMPTY   — same reason: an empty string trivially "does not contain" the marker.
    #                           This is the hole the pure DETECTOR above had; a false RED is cheap,
    #                           a false REAP is not.
    #   * no marker           — POSITIVE identification of a different program, not an inference.
    #   * >= 60 s old         — belt-and-braces against any write-then-observe race.
    # A torn/unreadable lock is deliberately NOT reaped: the driver already treats it as stale, and
    # the only way to observe one is to catch a lock mid-write, where deleting would be exactly wrong.
    stale_locks: list[str] = []
    reaped_locks: list[str] = []
    dead_pid_locks = 0
    try:
        import psutil
        for lk in sorted((ROOT / "batches").glob("*.driver.lock")):
            try:
                _lk = json.loads(lk.read_text(encoding="utf-8"))
                owner = int(_lk.get("pid", -1))
                lk_ts = float(_lk.get("ts", 0.0))
            except Exception:                                    # noqa: BLE001 — torn lock = stale
                stale_locks.append(f"{lk.name} (unreadable)")
                continue
            if owner <= 0 or not psutil.pid_exists(owner):
                dead_pid_locks += 1
                continue                                          # the driver's own check handles this
            try:
                proc = psutil.Process(owner)
                pname = proc.name()
                cmd = " ".join(proc.cmdline())
            except Exception:                                     # noqa: BLE001 — vanished/denied
                continue                                          # fail SAFE: never reap on unknowns
            if not cmd or "run_campaign_cluster" in cmd:
                continue                                           # a live driver, or unidentifiable
            why = f"{lk.name} (pid {owner} is {pname}, NOT a driver)"
            if (time.time() - lk_ts) < 60.0:
                stale_locks.append(why + " [too young to reap this cycle]")
                continue
            try:
                lk.unlink()
                reaped_locks.append(why)
                with (WATCH / "REAPED_LOCKS.log").open("a", encoding="utf-8") as fh:
                    fh.write(f"{_utc()}  REAPED {lk.name}  owner_pid={owner} owner_name={pname}\n"
                             f"    owner_cmdline={cmd[:400]}\n"
                             f"    lock_age_h={(time.time() - lk_ts) / 3600.0:.2f}\n")
            except Exception as exc:                              # noqa: BLE001 — report, never crash
                stale_locks.append(why + f" [REAP FAILED: {exc}]")
    except ImportError:
        attention.append("psutil unavailable — the stale-lock check is BLIND this cycle")
    if reaped_locks:
        attention.append(
            f"D20 SELF-HEAL: auto-reaped {len(reaped_locks)} stale driver lock(s) whose pid had been "
            f"REUSED by a non-driver process — {', '.join(reaped_locks[:3])}"
            f"{' …' if len(reaped_locks) > 3 else ''}. Each would otherwise have blocked its batch "
            f"forever. Evidence appended to docs/ops/watch/REAPED_LOCKS.log; the line's supervisor "
            f"relaunches on its own backoff. The MECHANISM fix (record identity, not just the pid) "
            f"is DEFERRED-13 and ships at the C4 relaunch.")
    if stale_locks:
        alerts.append(f"STALE DRIVER LOCK(S) NOT auto-reaped: {', '.join(stale_locks[:3])}"
                      f"{' …' if len(stale_locks) > 3 else ''}. The driver's staleness check tests "
                      f"pid EXISTENCE, not pid IDENTITY, so it will refuse to start that batch "
                      f"forever. Verify no live driver owns it, then delete the lock file (D20).")
    if dead_pid_locks:
        info.append(f"locks {dead_pid_locks} lock(s) held by a DEAD pid (auto-broken by the driver on "
                    f"contact; each is a latent D20 landmine until a driver touches that batch)")
    science_locks = len(stale_locks)

    # 5c. ★ D14 ARM-CRASH MARKERS (2026-08-01, RUN 10 — the watching half of the D14 fix).
    #
    # `run_campaign_tiered` now STOPS a pass when a core arm raised, rather than building the
    # CRN-paired H2 array with that arm silently absent, and drops a line-qualified marker beside
    # the archive. Without this block that marker is a file nobody reads — the exact "instrument
    # that cannot fire" shape that has produced fourteen defects across three sessions. The line
    # exits non-zero and its supervisor relaunches it on the 600 s backoff, so a TRANSIENT crash
    # self-heals and the marker disappears on the next clean pass; a marker that PERSISTS across
    # several cycles means the crash is deterministic and needs a human.
    for _m in sorted(ROOT.glob("ARM_CRASH_*.json")):
        try:
            _p = json.loads(_m.read_text(encoding="utf-8"))
            _arms = ", ".join(f"{k} ({v})" for k, v in sorted((_p.get("arms") or {}).items()))
            _age = (time.time() - float(_p.get("ts", 0))) / 60.0
        except Exception:                                        # noqa: BLE001 — torn = still real
            _arms, _age = "(unreadable marker)", -1.0
        alerts.append(
            f"D14 CORE ARM CRASH on {_m.stem.replace('ARM_CRASH_', '')}: {_arms}. The pass STOPPED "
            f"before the H2 pair array rather than submitting it with a missing arm (which would "
            f"have CRN-paired every seed against the wrong comparator set). The supervisor "
            f"relaunches on its backoff and --resume re-runs only the crashed arm. Marker age "
            f"{_age:.1f} min — if it survives several relaunches the crash is DETERMINISTIC and "
            f"needs a human.")

    # 6. driver-log freshness
    now = time.time()
    ages = {p.name: round((now - p.stat().st_mtime) / 60.0, 1) for p in sorted(ROOT.glob("driver*.log"))}
    stalest_name, stalest = ("", 0.0)
    if ages:
        stalest_name, stalest = max(ages.items(), key=lambda kv: kv[1])
        if stalest > STALE_DRIVER_MINUTES:
            alerts.append(f"{stalest_name} is {stalest:.0f} min stale (>{STALE_DRIVER_MINUTES:.0f}) "
                          f"-- that line has stopped progressing (defect D14)")

    # 7. drift vs the RUNNING sha, not vs HEAD
    _, drift_out = _run(["git", "diff", "--name-only", RUNNING_SHA, "HEAD", "--", *DRIFT_PATHS])
    drift = [ln for ln in drift_out.splitlines() if ln.strip() and not ln.startswith("<")]
    # ⚠ ...AND the working tree. `git diff <sha> HEAD` compares two COMMITS and is therefore blind to
    # an applied-but-uncommitted edit to `src/` — which would read as zero drift while the drivers ran
    # something else entirely. Found by an independent auditor 2026-07-31; the tree was clean, so this
    # closes a hole rather than a live exposure. An uncommitted change to a drift-fenced path is MORE
    # dangerous than a committed one, not less, because nothing else in the repo records it.
    _, dirty_out = _run(["git", "status", "--porcelain", "--", *DRIFT_PATHS])
    dirty = [ln.strip() for ln in dirty_out.splitlines() if ln.strip() and not ln.startswith("<")]
    if dirty:
        alerts.append(f"UNCOMMITTED changes under {'/'.join(DRIFT_PATHS)}: {', '.join(dirty[:4])}"
                      f"{' …' if len(dirty) > 4 else ''} — the drift diff compares COMMITS and cannot "
                      f"see these. Commit or revert before trusting drift=0.")

    # 8. records + spend, and the DELTA that actually tells you whether it is moving
    _, st_out = _run([sys.executable, "scripts/campaign_guards.py",
                      str(ROOT.relative_to(REPO)), "status"], timeout=120)
    records = spend = None
    m = re.search(r"records=(\d+)", st_out)
    if m:
        records = int(m.group(1))
    m = re.search(r"spend_total=\$([0-9.]+)", st_out)
    if m:
        spend = float(m.group(1))
    d_rec = (records - prev["records"]) if records is not None and isinstance(prev.get("records"), int) else None

    # MONOTONICITY. The archive and the spend ledgers are both APPEND-ONLY, so neither count can ever
    # fall. A decrease is not a slowdown -- it means records were deleted, a ledger was truncated, or
    # the monitor is pointed at a different root than it was last cycle. Any of those invalidates the
    # numbers being reported, so it is RED rather than ATTN. (Added 2026-07-31 after the budget print
    # was widened to 4 dp and the first cross-format comparison produced a spurious -$0.0034: the
    # artefact was harmless, but nothing in the cycle would have told me a REAL one was impossible.)
    prev_spend = prev.get("spend_total_usd")
    if isinstance(d_rec, int) and d_rec < 0:
        alerts.append(f"RECORD COUNT FELL {prev['records']} -> {records}. The archive is append-only; "
                      f"a decrease means deletion, a truncated tree, or a changed root.")
    if isinstance(spend, (int, float)) and isinstance(prev_spend, (int, float)) and spend < prev_spend:
        alerts.append(f"SPEND TOTAL FELL ${prev_spend} -> ${spend}. The spend ledgers are append-only; "
                      f"a decrease means a ledger was truncated, rewritten, or replaced.")

    # A DROUGHT, not a single quiet cycle. Records land in bursts as packed jobs complete, so at a
    # 2-minute cadence a zero delta is the COMMON case, not a signal -- raising attention on the first
    # one filled the alert file with noise the moment the cadence was automated (2026-07-31), which is
    # the same alarm-hygiene failure being fixed everywhere else in this file. What is diagnostic is a
    # SUSTAINED drought, so the streak is carried in STATE.json and only a long one speaks.
    zero_streak = (prev.get("zero_delta_streak") or 0) + 1 if d_rec == 0 else 0
    if zero_streak and zero_streak % ZERO_DELTA_CYCLES == 0:
        attention.append(f"no new record for {zero_streak} consecutive cycles "
                         f"(~{zero_streak * 2} min) -- trainings take 4-6 h so bursts are normal, but "
                         f"a drought this long is worth confirming against the cluster queue")

    # 9. THE RESULTS LAYER -- are the numbers themselves logical, correct and meaningful?
    science = _results_layer(prev, alerts, attention)

    cores = jobs = ""
    _vanished_rc = -1        # -1 => the ssh-cadence layer did not run this cycle (see below)
    _record_seal_rc = -1     # -1 => same; 0 = sealed clean, 1 = a record disagrees with its files
    if args.ssh:
        rc, out = _run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", "myriad",
                        'Q=$(qstat -u ucestes | tail -n +3); '
                        'echo "run=$(echo "$Q" | awk "\\$5==\\"r\\"" | grep -c .)"; '
                        'echo "qw=$(echo "$Q" | awk "\\$5 ~ /qw/" | grep -c .)"; '
                        'echo "cores=$(echo "$Q" | awk "\\$5==\\"r\\" {s+=\\$9} END {print s+0}")"'],
                       timeout=90)
        if rc == 0:
            got = dict(ln.split("=", 1) for ln in out.splitlines() if "=" in ln)
            cores = got.get("cores", "")
            jobs = f"{got.get('run', '?')}r/{got.get('qw', '?')}q"
        else:
            attention.append("ssh to myriad failed this cycle (the campaign is unaffected; retry next cycle)")

        # ── VANISHED-ARRAY LAYER (RUN 13, 2026-08-02) ───────────────────────────────────────────
        # The one failure mode this cycle could not see. `driver.py` line 6 makes SGE's walltime the
        # stall detector, which is right for a SLOW job and blind to a VANISHED one: an array purged
        # in Eqw leaves no qacct row, so the driver waits out the full 54,000 s h_rt before it
        # requeues. Measured on `cma_es-c4`: submitted 07-30 14:56, requeued 07-31 11:10 -- 20.2 h of
        # nothing, on the arm that is the campaign's critical path (9/30 candidates, strictly
        # sequential, and the C1 barrier waits for it). 76 such events across the 12 driver logs.
        #
        # Deliberately on the SSH cadence (~20 min), not every cycle: it needs a `qstat`, the login
        # node is shared, and 20 minutes against a 15-hour blind spot is already a ~45x improvement.
        # It is a COMPOSER -- it shells out to the instrument rather than re-deriving its logic, so
        # the two can never come to disagree about the same fact.
        _va_rc, _va_out = _run([sys.executable, "docs/ops/vanished_array_watch.py"], timeout=300)
        # Recorded in STATE.json so a later session can see the layer RAN. A check that is silent
        # when clean and leaves no trace is indistinguishable from a check that was never wired in --
        # which is the "a green board is not evidence" rule applied to my own addition.
        _vanished_rc = _va_rc
        if _va_rc == 1 and "VANISHED" in _va_out:
            alerts.append(
                "VANISHED ARRAY(S) -- a submitted array has left the queue while its block is still "
                "pending. The driver will not notice until h_rt expires (up to 15 h). Run "
                "`python docs/ops/vanished_array_watch.py` for the line and block.\n"
                + "\n".join(ln for ln in _va_out.splitlines() if "VANISHED" in ln or "!!!" in ln))
        elif _va_rc not in (0, 1):
            attention.append(f"vanished_array_watch rc={_va_rc} -- the blind-spot detector could not "
                             "run; the 15 h purge blind spot is UNWATCHED this cycle")

        # ── PER-RECORD PROVENANCE SEAL (RUN 13, 2026-08-02) ────────────────────────────────────
        # Tamer: "constantly check each record, make sure every record individually is very strictly
        # flawless". `record_validator.py` (R1-R9) is the deep per-record contract check and is run
        # per session; this is the SEAL between a record and the files beside it -- its `env.json`
        # digest and its `reward.py` hash -- which nothing checked before, because `results.py`
        # verifies the env digest only on the CANONICAL read path and `record_validator` reads raw
        # JSON. INCREMENTAL: it seals only records newer than the last CLEAN pass, so the cost stays
        # flat as the archive grows toward ~42,000 records while every NEW record is sealed within
        # one ssh cadence (~20 min). A check too expensive to run is a check that does not run.
        _seal_rc, _seal_out = _run(
            [sys.executable, "docs/analysis/record_provenance_seal.py", "--since-state"], timeout=900)
        _record_seal_rc = _seal_rc
        if _seal_rc == 1:
            alerts.append(
                "RECORD PROVENANCE SEAL FAILED -- a record disagrees with the env.json or reward.py "
                "beside it, or names a commit this repository does not contain. That is an archive "
                "integrity failure, not a monitoring nit. Run "
                "`python docs/analysis/record_provenance_seal.py` for the full report.\n"
                + "\n".join(ln for ln in _seal_out.splitlines() if "P1-" in ln or "P2-" in ln
                            or "P3-" in ln or "P4-" in ln or "FAILURES" in ln))
        elif _seal_rc != 0:
            attention.append(f"record_provenance_seal rc={_seal_rc} -- the per-record seal could not "
                             "run this cycle; new records are UNSEALED until it does")

    state = {
        "written_utc": stamp,
        "note": args.note,
        "records": records,
        "records_delta": d_rec,
        "zero_delta_streak": zero_streak,
        "spend_total_usd": spend,
        "guards_rc": guards_rc,
        "guards_failing": failing,
        "guards_known_acked": known_guards,
        "sentinel_known_acked": known_sentinel,
        "lines_with_all_arms": full_lines,
        "stale_driver_locks": science_locks,
        "budget_rc": bud_rc,
        "budget": budget,
        "science": science,
        "driver_log_age_minutes": ages,
        "stalest_driver": [stalest_name, stalest],
        "running_sha": RUNNING_SHA,
        "head_sha": _run(["git", "rev-parse", "--short", "HEAD"])[1],
        "drift_vs_running_sha": drift,
        "remote_control_sha": remote_hash,
        "remote_control_changed": remote_changed,
        "stop_file_present": stop_file.exists(),
        "cores": cores,
        "jobs": jobs,
        # -1 = the ssh cadence did not run this cycle; 0 = ran, clean; 1 = ran, vanished array found.
        "vanished_array_rc": _vanished_rc,
        "record_seal_rc": _record_seal_rc,
        "alerts": alerts,
        "attention": attention,
    }
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    # ── SWEEP DURATION: the cadence is only as fast as the SLOWER of sleep and sweep ──────────────
    # ADDED 2026-07-31 (record 78). Both heavy layers read EVERY record, so the sweep is LINEAR in
    # archive size: 9.7 s at 1,534 records = 6.29 ms/record. Projected at the registered rung-568
    # ladder (~39,760 trainings) the sweep alone is ~250 s, so a loop configured at INTERVAL=30 would
    # actually run a ~280 s cadence -- and would still be described everywhere as "30 seconds".
    #
    # That is this session's recurring defect in its purest form: a number that quietly stops being
    # true. The cure is NOT to sample the archive (reading every record is what makes `sci=OK` mean
    # anything, record 77) but to make the degradation impossible to miss: the true sweep time goes on
    # every cycle line, and the moment it exceeds the configured sleep the line says so.
    #
    # ⚠ THIS MUST SIT BEFORE `verdict` IS COMPUTED. My first version appended to `attention` AFTER
    # that line: the exit code escalated (it is derived at the end) but the verdict token on the LOG
    # LINE still read OK -- a log that disagrees with its own exit code. Caught by checking the
    # ordering rather than assuming it.
    sweep_s = time.monotonic() - _t_sweep0
    sweep_tok = f"  sweep={sweep_s:.1f}s"
    if args.interval and sweep_s > args.interval:
        sweep_tok += f"(SWEEP-BOUND: >{args.interval:.0f}s sleep)"
        attention.append(
            f"the sweep now takes {sweep_s:.1f}s, longer than the configured {args.interval:.0f}s "
            f"sleep -- the REAL cadence is ~{sweep_s + args.interval:.0f}s, not {args.interval:.0f}s. "
            f"Expected as the archive grows (linear, ~6.3 ms/record). Do NOT fix this by sampling the "
            f"archive; either re-state the cadence honestly or make the sweep incremental. Record 78.")

    verdict = "RED" if alerts else ("ATTN" if attention else "OK")
    # `sci=` is the results layer in one token: OK when every hard invariant reads zero, otherwise the
    # broken ones by name. r115 is carried separately because it is expected to move and its VALUE is
    # the signal. A cadence log that records only process health cannot evidence "the results were
    # monitored", which is precisely the claim Tamer asked to be able to check.
    broken = [k for k in _HARD_ZERO if science.get(k)]
    sci = "OK" if not broken else "!" + ",".join(broken)
    summary = (f"{stamp}  {verdict}  records={records}"
               f"{'' if d_rec is None else f' ({d_rec:+d})'}  spend=${spend}  guards={guards_rc}  "
               f"arms_full={full_lines}/10  budget={bud_rc}  stalest={stalest:.1f}m  "
               # ⚠ THE TOKEN MUST CARRY BOTH ARMS (RUN 9, record §98). This printed `len(drift)` —
               # the COMMITS-only arm — so the cycle log and Tamer's status page both read `drift=0`
               # while three drift-fenced files sat MODIFIED in the working tree. The uncommitted
               # ALERT fired correctly (6 times, naming all three), but the headline number did not,
               # and the headline is what a session reads during its first-hand state check. Caught
               # live on 2026-08-01 by watching my own D16/D12 edits fail to move it.
               # `drift=0` must be able to mean ONLY "genuinely clean"; anything else is unmissable.
               f"drift={len(drift)}{f'+{len(dirty)}dirty' if dirty else ''}  "
               f"sci={sci}  r115={science.get('sw_r115_breaches')}"
               f"{'B' if science.get('sw_r115_binding') else ''}"
               + (f"  cores={cores}" if cores else "")
               + sweep_tok
               + (f"  {args.note}" if args.note else ""))
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(summary + "\n")

    if not args.quiet:
        for a in alerts:
            lines.append("RED   " + a)
        for a in attention:
            lines.append("ATTN  " + a)
        if known_guards or known_sentinel:
            lines.append("known " + ", ".join(known_guards + known_sentinel)
                         + "  (acknowledged in docs/ops/acknowledged_alarms.txt -- re-read the entry, "
                           "each one carries its own RE-TRIAGE trigger)")
        if drift:
            lines.append(f"note  drift vs running sha {RUNNING_SHA}: {', '.join(drift)} "
                         f"(prove unreachable with docs/ops/import_closure.py, or re-base at restart)")
        lines.append(
            "sci   records sw={sw}/ra={ra}  r115={r115}{b}  popart engaged={eng}/pinned={pin}  "
            "leaks={lk} cross-arm={xa} hash={hm} non-finite={nf}".format(
                sw=science.get("sw_records"), ra=science.get("ra_records"),
                r115=science.get("sw_r115_breaches"),
                b=" BINDING" if science.get("sw_r115_binding") else "",
                eng=science.get("ra_popart_engaged"), pin=science.get("ra_popart_pinned"),
                lk=science.get("ra_scalar_leaks"), xa=science.get("ra_cross_arm_shared"),
                hm=science.get("ra_hash_mismatch"), nf=science.get("ra_non_finite")))
        lines.append(
            "arms  IUT pools dist={d} scal={s} plac={p} scv5={c} (shuf={z})  spread={r}x"
            .format(d=science.get("n_distributional"), s=science.get("n_scalar"),
                    p=science.get("n_placebo"), c=science.get("n_scalar_cvar5"),
                    z=science.get("n_placebo_shuffled"), r=science.get("arm_pool_spread")))
        for ln in info:
            lines.append("info  " + ln)
        for ln in lines:
            print(ln)
    print(summary)
    return 2 if alerts else (1 if attention else 0)


if __name__ == "__main__":
    raise SystemExit(main())
