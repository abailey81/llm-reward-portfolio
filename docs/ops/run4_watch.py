"""RUN 4 live guards — the invariants ~2,870 unit tests structurally cannot check.

Every collision that has hurt this campaign (D1 the reject-marker collision, D5 the C3 gate
collision, and the 2026-07-19 `pending_specs` case) is ONE shape: a resource shared by twelve
concurrent lines, keyed by an identifier unique only WITHIN one line. Every test exercises a
single line, so no test can see it. The only reliable detector is a live invariant — this file.

Schemas here were read off the real RUN 1 / RUN 3 archives, not from memory:
  <root>/<sub_root>/<arm>/<candidate_id>/record.json   generation, prompt, metrics{}
  <root>/<sub_root>/<arm>/llm_calls.jsonl              stop_reason, usage, request_pins
  <root>/<sub_root>/_rejects/<run_id>.json             permanent reject markers
  <root>/batches/<base>/<base>.permanent.jsonl         ledgered permanent abandonments
  <root>/spend_ledger_<tag>.jsonl                      cost rows (+ stop_reason from 18dead8)
  <root>/driver_<line>.log                             per-line driver output

Subcommands: collision | reflection | truncation | transport | status | all
Exit code 2 == a STOP-THE-RUN regression.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

# Mirrors src/llm/client._INCOMPLETE_STOP_REASONS. A value here means the archived response was
# CUT OFF, which reaches the sandbox as "defines no callable named 'reward'" — indistinguishable
# from a model that simply could not write the code. That distinction is a registered deliverable.
INCOMPLETE_STOP_REASONS = frozenset({"max_tokens", "refusal", "length", "content_filter"})

# src/llm/loop.py:_REFLECTION_PREAMBLE, verbatim. A generation>0 prompt that does NOT start with
# this was composed with prev_block=None (parallel.py:1041) — i.e. the reflection loop, which is
# the mechanism H2 is ABOUT, silently fell back to the initial prompt. That is exactly what D1 did.
REFLECTION_PREAMBLE = "Reflect on the previous candidate's results"

CANDIDATE_DIR_RE = re.compile(r"-g\d+-c\d+$")


# ----------------------------------------------------------------------------- helpers
def _iter_json(path: Path):
    """Yield parsed rows of a JSONL file, tolerating torn trailing lines."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue  # a torn last line must never sink a guard


def _sub_roots(root: Path) -> list[Path]:
    return [
        p
        for p in sorted(root.iterdir())
        if p.is_dir() and (p.name == "search" or p.name.startswith(("search_", "test")))
    ]


# ----------------------------------------------------------------------------- guards
def collision_guard(root: Path) -> tuple[int, list[str]]:
    """EVERY ledgered permanent abandonment must trace to a marker in its OWN sub-root.

    A single foreign one reproduces the defect that invalidated RUN 1 and is a stop-the-run
    regression, not a warning.
    """
    out: list[str] = []
    markers_by_root: dict[str, set[str]] = {}
    for sub in _sub_roots(root):
        ids = set()
        for m in sub.rglob("_rejects/*.json"):
            try:
                row = json.loads(m.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if row.get("permanent"):
                ids.add(str(row.get("run_id") or m.stem))
        markers_by_root[sub.name] = ids

    total_markers = sum(len(v) for v in markers_by_root.values())
    abandoned = 0
    foreign: list[str] = []
    # driver.py:346 -> `Path(local_batch_root) / f"{base_name}.permanent.jsonl"`, i.e. FLAT under
    # batches/. An earlier nested glob here matched nothing and made this guard silently vacuous
    # on the RUN 1 archive -- caught only by falsifying it against data where the defect is known
    # to exist. Both shapes are matched now so a layout change cannot re-silence it.
    ledgers = sorted({*root.glob("batches/*.permanent.jsonl"), *root.glob("batches/*/*.permanent.jsonl")})
    if not ledgers:
        out.append("NOTE: no *.permanent.jsonl ledger found yet (none written until an abandonment)")
    for led in ledgers:
        for row in _iter_json(led):
            if row.get("reason") != "permanent_node_reject":
                continue
            abandoned += 1
            spec = row.get("spec") or {}
            rid = str(spec.get("run_id") or spec.get("candidate_id") or "")
            ar = str(spec.get("archive_root") or "")
            own = Path(ar).name if ar else ""
            if own and rid and rid not in markers_by_root.get(own, set()):
                foreign.append(f"{led.name}: run_id={rid} claims sub_root={own} but NO marker there")

    out.append(f"reject_markers={total_markers} ledgered_abandonments={abandoned} foreign={len(foreign)}")
    for f in foreign[:10]:
        out.append(f"  FOREIGN: {f}")
    return (2 if foreign else 0), out


#: A line needs at least this many generation>0 candidates before a per-line ratio means anything
#: (P309). Without it, the very first archived candidate of a fresh line reads 0/1 = 0% and alarms.
_REFLECTION_MIN_N = 10


def reflection_guard(root: Path, floor: float = 0.80) -> tuple[int, list[str]]:
    """Fraction of generation>0 candidates actually SHOWN a reflection block.

    RUN 1 archived 241 prompts of which only 10 carried the preamble — the mechanism under study
    was off and nothing alarmed. Below `floor` the reflection loop is starving.
    """
    total = shown = 0
    per_root: Counter[str] = Counter()
    per_root_shown: Counter[str] = Counter()
    for rec in root.glob("*/*/*-g*-c*/record.json"):
        try:
            r = json.loads(rec.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if int(r.get("generation", 0)) <= 0:
            continue
        sub = rec.parents[2].name
        total += 1
        per_root[sub] += 1
        if str(r.get("prompt", "")).lstrip().startswith(REFLECTION_PREAMBLE):
            shown += 1
            per_root_shown[sub] += 1
    if total == 0:
        return 0, ["reflection: no generation>0 candidates archived yet (expected early in a run)"]
    frac = shown / total
    lines = [f"reflection_shown={shown}/{total} ({frac:.1%}) floor={floor:.0%}"]
    for sub in sorted(per_root):
        lines.append(f"  {sub}: {per_root_shown[sub]}/{per_root[sub]}")
    # ⚠⚠ P309 (RUN 22 pass 3, 2026-08-04) -- THE VERDICT WAS A FLEET MEAN, SO ONE LINE'S TOTAL
    # FAILURE COULD NOT TRIP IT, AND THE PER-LINE NUMBERS WERE COMPUTED AND THEN THROWN AWAY.
    # This function's own docstring names the defect class as "a resource shared by twelve
    # concurrent lines, keyed by an identifier unique only WITHIN one line" -- and it then
    # aggregated over exactly those twelve. MEASURED on the live archive: 1141/1144 = 99.7%, with
    # the largest single line holding 125 of 1,144. So a line falling to ZERO still reads
    # 1016/1144 = 88.8% = "ok", and TWO ENTIRE LINES must fail before the fleet floor is breached.
    # The RUN 1 incident this guard exists to catch (241 prompts, 10 with the preamble) was a
    # PER-LINE event. The fleet floor stays exactly where it is -- this ADDS a per-line floor
    # rather than moving anything, so nothing is weakened.
    starved = sorted(sub for sub in per_root
                     if per_root[sub] >= _REFLECTION_MIN_N
                     and per_root_shown[sub] / per_root[sub] < floor)
    if starved:
        lines.append(f"  *** PER-LINE STARVATION on {len(starved)} line(s): "
                     + ", ".join(f"{s} {per_root_shown[s]}/{per_root[s]}" for s in starved))
        lines.append("      The fleet mean can be healthy while a single line's reflection loop is")
        lines.append("      OFF. The RUN 1 incident was per-line; so is this check now.")
    return (2 if (frac < floor or starved) else 0), lines


def truncation_guard(root: Path) -> tuple[int, list[str]]:
    """Provider-confirmed truncations, plus proof the stop_reason field is actually being written.

    RUN 4 is the FIRST run where the spend ledger carries stop_reason (it landed in 18dead8). Rows
    without the key mean a driver is running pre-18dead8 code — the exact ambiguity that halted
    RUN 3, and it must be caught here rather than discovered in the archive afterwards.
    """
    reasons: Counter[str] = Counter()
    worst = 0.0
    calls = 0
    for jl in root.glob("*/*/llm_calls.jsonl"):
        for row in _iter_json(jl):
            calls += 1
            reasons[str(row.get("stop_reason"))] += 1
            pins = row.get("request_pins") or {}
            usage = row.get("usage") or {}
            cap = pins.get("max_tokens") or 0
            out_tok = usage.get("output_tokens") or 0
            if cap:
                worst = max(worst, out_tok / cap)

    ledger_rows = with_field = 0
    for sl in root.glob("spend_ledger_*.jsonl"):
        for row in _iter_json(sl):
            ledger_rows += 1
            if "stop_reason" in row:
                with_field += 1

    bad = sum(n for k, n in reasons.items() if k in INCOMPLETE_STOP_REASONS)
    lines = [
        f"llm_calls={calls} truncated={bad} worst_completion={worst:.1%}_of_cap",
        f"  stop_reasons={dict(reasons)}",
        f"  spend_ledger rows={ledger_rows} carrying stop_reason={with_field}",
    ]
    rc = 0
    if bad:
        rc = 2
        lines.append("  *** TRUNCATION: our cap is contaminating the authoring-reliability finding")
    if ledger_rows and with_field != ledger_rows:
        rc = 2
        lines.append("  *** STALE DRIVER: spend rows lack stop_reason => code older than 18dead8")
    return rc, lines


#: The driver logs carry TWO logging formats and a count that sees only one silently undercounts.
#: RUN 3 was recorded as "881 INFO / 41 WARNING / 0 ERROR"; that is format A alone. Counting both
#: gives 7,776 INFO / 798 WARNING / 1 ERROR over the same files. Both patterns are applied here so
#: the totals are the real ones.
_LEVEL_A = re.compile(r"\|\s*(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s*\|")          # "| WARNING |"
_LEVEL_B = re.compile(r"\d{2}:\d{2}:\d{2}(?:,\d+)?\s+(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s")
#: A new LOG RECORD starts with a date; anything else is a hard-wrapped continuation of the one
#: above it (P309-b). Both log formats in these files begin the same way, so one pattern covers both.
_RECORD_START = re.compile(r"^\d{4}-\d\d-\d\d ")


def transport_guard(root: Path, max_consecutive_alarm: int = 8) -> tuple[int, list[str]]:
    """Transport failure rate, consecutive-failure depth, and the D9 diagnostic.

    RUN 1 climbed 5.2 % -> 55.3 % over ten hours because failed pulls leaked their ssh child; a
    monotonic climb here means the leak is back. RUN 3 (post-fix) ran 647 timeout events with a
    max of 5 consecutive and always self-healed, so a handful of consecutive failures is NORMAL
    and must not cry wolf -- the alarm is on DEPTH beyond RUN 3's observed worst.

    An ERROR line is reported but is deliberately NOT a stop condition: RUN 3's single ERROR was
    the driver correctly announcing a GENUINE permanent reject. The stop condition for the defect
    that actually invalidated a run lives in `collision_guard`, where it belongs.
    """
    levels: Counter[str] = Counter()
    timeouts = diag = timeout_mentions = 0
    worst_consecutive = 0
    child_exited: Counter[str] = Counter()
    err_samples: list[str] = []
    for log in sorted(root.glob("driver_*.log")):
        try:
            text = log.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        # ⚠⚠ P309-b -- THE D9 DIAGNOSTIC REGEX MATCHED NOTHING, FOR THE WHOLE CAMPAIGN.
        # The PowerShell host that runs the supervisor HARD-WRAPS the driver log, and
        # `src/cluster/submit.py:135-140` emits one message whose `child_already_exited=` lands on
        # the NEXT physical line. Iterating physical lines therefore searched for it on a line that
        # never contains it: `grep -c "ssh_timeout_diagnostic.*child_already_exited"` returns
        # **0 across all twelve logs**, while the value is present **173 times (164 False, 9 True)**.
        # The panel printed an EMPTY dict, and 164 False is an ACTIONABLE conclusion -- the remote
        # command genuinely hung, so the search moves cluster-side -- that this instrument has never
        # once delivered.
        #
        # Rejoining continuations first is the same idiom `vanished_array_watch` and
        # `transport_health` already use; this file simply never received it. Level counting is
        # unaffected because a continuation line carries no level token and was never counted.
        _recs: list[str] = []
        for _ln in text.splitlines():
            if _RECORD_START.match(_ln) or not _recs:
                _recs.append(_ln)
            else:
                _recs[-1] += " " + _ln.strip()
        for line in _recs:
            for pat in (_LEVEL_A, _LEVEL_B):
                m = pat.search(line)
                if m:
                    levels[m.group(1)] += 1
                    if m.group(1) == "ERROR" and len(err_samples) < 5:
                        err_samples.append(f"{log.name}: {line.strip()[:150]}")
                    break
            # P309-b, AND MY FIRST VERSION OF THIS FIX WAS ITSELF WRONG -- RECORDED BECAUSE THE
            # CORRECTION IS THE POINT. I widened the test to the UNION of "timed out after",
            # "ssh_timeout_diagnostic" and "TimeoutExpired", which took the count 113 -> 351 and
            # made it LESS accurate, not more: those three phrases mark different things, and a
            # union over-counts exactly as the sibling's 179 double-counts six retry notes.
            #
            # `ssh_timeout_diagnostic` is emitted ONCE PER TIMEOUT EVENT, so it is the authoritative
            # marker and the ground truth is 173. The looser phrases appear in retry notes and in
            # the pull's own message too, so they are MENTIONS, not events. Both are reported, each
            # under the name of what it actually is.
            if "ssh_timeout_diagnostic" in line:
                timeouts += 1
            elif "timed out after" in line or "TimeoutExpired" in line:
                timeout_mentions += 1
            c = re.search(r"\((\d+) consecutive", line)
            if c:
                worst_consecutive = max(worst_consecutive, int(c.group(1)))
            if "ssh_timeout_diagnostic" in line:
                diag += 1
                d = re.search(r"child_already_exited=(\w+)", line)
                if d:
                    child_exited[d.group(1)] += 1

    lines = [
        f"levels={dict(levels)} (both log formats counted)",
        f"timeout_events={timeouts} worst_consecutive={worst_consecutive} diagnostics={diag}",
        f"  (+{timeout_mentions} looser 'timed out' MENTIONS in retry notes and the pull's own "
        f"message -- counted separately because they are NOT one-per-event)",
    ]
    for s in err_samples:
        lines.append(f"  ERROR: {s}")
    if diag:
        lines.append(f"  *** D9 EVIDENCE child_already_exited={dict(child_exited)}")
        lines.append("      True => wall-clock spent in the PARENT's pipe read (pipe-handle race)")
        lines.append("      False => the remote command genuinely hung; search moves cluster-side")
    rc = 2 if worst_consecutive >= max_consecutive_alarm else 0
    if rc:
        lines.append(f"  *** consecutive failures reached {worst_consecutive} (RUN 3 worst was 5)")
    return rc, lines


def status(root: Path) -> tuple[int, list[str]]:
    """Progress and spend — the 'is this meaningful' view, not just 'is it running'."""
    records = len(list(root.glob("*/*/*/record.json")))
    rewards = len(list(root.glob("*/*/*/reward.py")))
    spend: dict[str, float] = {}
    for sl in sorted(root.glob("spend_ledger_*.jsonl")):
        tag = sl.stem.replace("spend_ledger_", "")
        spend[tag] = round(sum(float(r.get("cost_usd") or 0.0) for r in _iter_json(sl)), 4)
    lines = [
        f"records={records} authored_rewards={rewards}",
        f"spend_total=${sum(spend.values()):.4f} by_line={spend}",
        f"core_line_spend=${spend.get('c1', 0.0):.4f} (canary shield: expect $0.00 until C0 clears)",
        f"driver_logs={len(list(root.glob('driver_*.log')))} supervisors={len(list(root.glob('supervisor_*.log')))}",
    ]
    return 0, lines


#: Measured per-model authoring reliability (2026-07-25 gate campaign). The point of RUN 4 is that
#: this gradient EXISTS -- qwen3.5-9b is the deliberately weakest anchor and its rejects are a
#: registered finding, not a fault. The repo's `check_gate_failure_rate` is a single GLOBAL rate
#: calibrated on the prototype's ~2.5 % (one strong model), so it will sit at WARN/CRIT for the
#: whole of RUN 4 by design. A permanently-on CRITICAL is how an operator learns to ignore a panel,
#: so the per-model view below is what should actually be read.
EXPECTED_PASS_RATE = {
    "qwen3_5_9b": 0.17,          # the capability-gradient BOTTOM anchor
    "qwen3_6_27b": 0.83,
    "gemini_2_5_flash": 0.83,
    "deepseek_v4_pro": 1.00,
}

#: P310: the reject rate above which NO capability gradient is a plausible explanation, applied to
#: every leg that has no MEASURED expectation of its own. It is deliberately far above the
#: registered weakest anchor (qwen3.5-9b, measured ~83% reject) so it can only ever fire on the
#: DEFECT this guard exists to separate from the finding -- our machinery rejecting everything.
#: It is a BACKSTOP, not a per-model expectation, and it must never be tuned downward to make a
#: leg "look" thresholded: the honest state for those six legs is un-thresholded, and the row says so.
_UNIVERSAL_REJECT_BACKSTOP = 0.95


def rejects_guard(root: Path) -> tuple[int, list[str]]:
    """Per-line reject rate, read against each model's MEASURED expectation.

    Distinguishes the FINDING (a weak model writing reward code that fails the sandbox -- expected,
    frequent, and a registered deliverable) from a DEFECT (our machinery rejecting everything). The
    discriminator is per-model: qwen3.5-9b at ~83 % reject is the study working; deepseek at 83 %
    reject would be the study broken.
    """
    lines: list[str] = []
    rc = 0
    for sub in sorted(root.glob("search_leg_*")):
        leg = sub.name.replace("search_leg_", "")
        markers = len(list(sub.glob("_rejects/*.json")))
        records = len(list(sub.glob("*/*/record.json")))
        attempted = markers + records
        if not attempted:
            continue
        reject_rate = markers / attempted
        exp_pass = EXPECTED_PASS_RATE.get(leg)
        note = ""
        if exp_pass is not None:
            exp_reject = 1.0 - exp_pass
            note = f" (expected ~{exp_reject:.0%})"
            # Only flag a model doing FAR worse than its own measured baseline.
            if reject_rate > exp_reject + 0.35 and attempted >= 10:
                rc = 2
                note += "  *** far worse than its measured baseline"
        else:
            # ⚠⚠ P310 (RUN 22 pass 3) -- SIX OF TEN LEGS COULD NEVER RAISE THIS GUARD.
            # `EXPECTED_PASS_RATE` holds FOUR keys from the 2026-07-25 gate campaign; for the other
            # six `exp_pass` is None and the `rc = 2` branch above is simply unreachable. Measured
            # live: glm_5_2 13% reject, nemotron_3_super 19%, plus gpt_5_6_luna, haiku_4_5, kimi_k3
            # and sonnet_5 -- 60% of the leg population -- while the docstring promises "read
            # against each model's MEASURED expectation" and warns that "deepseek at 83% reject
            # would be the study broken". A collapse on any of the six printed `[rejects] ok`.
            #
            # ⛔ THE FIX IS NOT TO INVENT EXPECTATIONS. Those four numbers were MEASURED, and
            # fabricating six more would be worse than the gap. Two honest things are done instead:
            # the absence is stated in the row, and a UNIVERSAL BACKSTOP catches only the DEFECT
            # case this guard's own docstring names -- "our machinery rejecting everything" -- at a
            # rate no capability gradient explains. The registered weakest anchor, qwen3.5-9b, was
            # measured at ~83% reject, so the backstop sits well clear of the science and cannot
            # misfire on the finding the campaign exists to produce.
            note = " (NO measured expectation -- not thresholded per-model)"
            if reject_rate >= _UNIVERSAL_REJECT_BACKSTOP and attempted >= 10:
                rc = 2
                note += (f"  *** >= {_UNIVERSAL_REJECT_BACKSTOP:.0%} REJECT: no capability gradient "
                         "explains this; suspect the machinery, not the model")
        lines.append(f"{leg}: rejects={markers} records={records} reject_rate={reject_rate:.0%}{note}")
    _unthresholded = sorted(sub.name.replace("search_leg_", "")
                            for sub in root.glob("search_leg_*")
                            if sub.name.replace("search_leg_", "") not in EXPECTED_PASS_RATE)
    if _unthresholded:
        lines.append(f"  NOTE: {len(_unthresholded)} leg(s) carry NO measured expectation and are "
                     f"covered only by the {_UNIVERSAL_REJECT_BACKSTOP:.0%} backstop: "
                     + ", ".join(_unthresholded))
    if not lines:
        lines.append("no leg candidates resolved yet")
    return rc, lines


GUARDS = {
    "collision": collision_guard,
    "reflection": reflection_guard,
    "truncation": truncation_guard,
    "transport": transport_guard,
    "rejects": rejects_guard,
    "status": status,
}


def main() -> int:
    ap = argparse.ArgumentParser(description="RUN 4 live guards")
    ap.add_argument("root", help="campaign output root, e.g. outputs/campaign_cluster_run4")
    ap.add_argument("guard", nargs="?", default="all", choices=[*GUARDS, "all"])
    args = ap.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        print(f"[guards] root does not exist yet: {root}")
        return 0

    names = list(GUARDS) if args.guard == "all" else [args.guard]
    worst = 0
    for name in names:
        rc, lines = GUARDS[name](root)
        worst = max(worst, rc)
        tag = "CRITICAL" if rc else "ok"
        print(f"[{name}] {tag}")
        for line in lines:
            print(f"    {line}")
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
