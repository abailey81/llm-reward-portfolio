"""ARM-COVERAGE GUARD — the detector that did not exist when leg7 lost two arms.

WHY THIS EXISTS (2026-07-29). `nemotron-3-super` (leg7) ran for 8 h 29 m with 3 of its 5 arms,
having lost `scalar` and `placebo_shuffled` to the D13 TypeError at 00:11 local. Every one of the
six repo guards reported OK throughout, because not one of them asks the question "does this line
still have all of its arms?".

THE ASYMMETRY THIS CATCHES. When EVERY arm of a line crashes, the line dies, the supervisor logs
LINE COMPLETE, and the watchdog revives it 300 s later — a total failure is LOUD and SELF-HEALING
(six lines did exactly that 10x each on launch night and all recovered). When only SOME arms crash,
the line stays alive on its survivors, `run_campaign_tiered` never returns, no supervisor exit
fires, no watchdog revive triggers, and the dead arms are stranded for the life of the process.
PARTIAL failure is SILENT and does NOT self-heal. That is strictly the more dangerous case, and it
was the unmonitored one.

WHAT IT MEASURES. Cluster-batch submission per (line, arm) read from the `batches/` registry —
i.e. work actually SHIPPED, not merely authored. An arm can hold a populated `search_.../<arm>/`
directory (the authoring happened, `llm_calls.jsonl` is non-empty) and still have shipped nothing;
leg7's two dead arms looked exactly like that, which is why the archive directory listing is NOT a
sufficient check and this reads the batch registry instead.

EFFECT-BLIND by construction: it reads submission COUNTS only, never a performance field, so it
cannot condition the run on observed effects.

Exit 0 = every line holds its full arm roster. Exit 2 = an arm is missing — investigate before it
costs a leg its H2 contrast.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

# The five LLM arms every replication leg must carry. `scalar` is the H2 contrast partner for
# `distributional`; losing it makes the leg useless for the confirmatory comparison, which is why
# a missing arm is exit 2 and not a warning.
LEG_ARMS = {"distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled"}
# h3ss is single-arm BY DESIGN (config/campaign.yaml h3_singleshot_generations: the H3 single-shot
# control is archived to search_h3_singleshot/ for the distributional arm only) — not a defect.
EXPECTED = {"h3ss": {"distributional"}}

_ARM_RE = re.compile(
    r"^(?P<line>c1|h3ss|leg\d+)_.*?_(?P<arm>distributional|scalar_cvar5|scalar|placebo_shuffled|"
    r"placebo|random_search|bayes_opt|cma_es|tpe|baselines)(_g\d+)?(_r\d+)?(_p\d+)?$"
)


def coverage(root: Path) -> dict[str, set[str]]:
    """{line_tag: {arms with >=1 batch SUBMITTED}} from the batch registry."""
    seen: dict[str, set[str]] = defaultdict(set)
    batches = root / "batches"
    if not batches.is_dir():
        return seen
    for entry in batches.iterdir():
        name = entry.name.removesuffix(".driver.lock")
        m = _ARM_RE.match(name)
        if m:
            seen[m.group("line")].add(m.group("arm"))
    return seen


def attrition(root: Path) -> dict[str, int]:
    """{arm: author-side rejects} from every `failures.jsonl` in the run.

    WHY THIS IS HERE (2026-07-29). A candidate rejected by the author-side AST gate is ledgered
    `permanent: True` and **never replaced** — `run_search_arm` does `failed += 1; continue`, and on
    resume P8 refuses to re-ship a permanent row. So the arm simply searches over FEWER candidates
    than the registered 30.

    That is fine when it is symmetric across arms, and an IDENTIFICATION problem when it is not:
    H2 compares `max(val_fitness)` over each arm's candidates, and fewer draws lowers the expected
    maximum. Differential attrition therefore imposes a systematic handicap on whichever arm loses
    more candidates — and if that arm is a CONTROL (`placebo`, `placebo_shuffled`), the bias runs
    TOWARD a false positive for the hypothesis. Reported here so the per-arm counts are visible
    continuously rather than reconstructed at analysis time.

    Effect-blind: reads `candidate_id` and the reject reason only, never a performance field.
    """
    # A-attr / P272: THIS POOLED ALL 11 LINES INTO ONE PER-ARM COUNT, so the "max-min across the
    # five arms" it feeds was a CROSS-LINE spread while the H2 contrast it exists to inform is
    # WITHIN-LINE. A pooled figure can hide a badly handicapped arm on a single line: measured
    # per line, glm_5_2 spreads 9, nemotron 8 and gemini 6, against a pooled 14. It also folded
    # the CORE line in, which `coverage()` excludes -- inconsistent scope inside one file.
    # Keyed by (line, arm) now; `attrition()` keeps its pooled signature for callers, and
    # `attrition_by_line()` is the one to quote.
    out: dict[str, int] = defaultdict(int)
    for (_line, arm), n in attrition_by_line(root).items():
        out[arm] += n
    return out


def attrition_by_line(root: Path) -> dict:
    """{(line, arm): author-side rejects} -- the WITHIN-LINE population the science actually uses."""
    per: dict = defaultdict(int)
    for led in root.glob("search*/*/failures.jsonl"):
        arm = led.parent.name
        line = led.parent.parent.name
        for row in led.read_text(encoding="utf-8").splitlines():
            if row.strip():
                per[(line, arm)] += 1
    return per


_SEVERITY_RANK = {"OK": 0, "INFO": 0, "UNKNOWN": 1, "WARN": 2, "CRITICAL": 3}


def sentinel_worst(root: Path) -> list[tuple[str, str, str, str]]:
    """The sentinel's OUTSTANDING non-OK verdicts, worst first.

    WHY THIS IS HERE (2026-07-30, D15). The sentinel raised **CRITICAL `substrate_fields`** — a
    scored-leg CPU-model mix, i.e. a CRN validity failure — and it sat unread for TEN HOURS, because
    `campaign_guards.py all` returned RC=0 throughout (substrate homogeneity is not one of its six
    guards) and the sentinel writes only to `sentinel_events.jsonl`. An alarm that fires into a file
    nobody reads is indistinguishable from an alarm that never fired.

    Only the LATEST verdict per check is reported: the sentinel re-runs every check on each pass, so
    an old WARN that has since gone OK must not keep shouting.
    """
    path = root / "sentinel_events.jsonl"
    if not path.is_file():
        return []
    latest: dict[str, tuple[str, str, str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        # NARROW on purpose. This was `except Exception`, and because `json` was not imported the
        # resulting NameError was swallowed on EVERY line — so the guard printed "no outstanding
        # non-OK verdicts" while a CRITICAL substrate verdict was live. A torn final line is the only
        # tolerable failure here; a programming error must propagate loudly (P14).
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        check = str(r.get("check", "?"))
        latest[check] = (str(r.get("severity", "?")), check,
                         str(r.get("ts", "?")), str(r.get("detail", ""))[:190])
    out = [v for v in latest.values() if _SEVERITY_RANK.get(v[0], 1) > 0]
    return sorted(out, key=lambda v: -_SEVERITY_RANK.get(v[0], 1))


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else "outputs/campaign_cluster_run4")
    seen = coverage(root)
    if not seen:
        print(f"[arm_coverage] no batch registry under {root} — nothing submitted yet")
        return 0

    rc = 0
    for line in sorted(seen, key=lambda s: (s[:3], len(s), s)):
        got = seen[line]
        if line == "c1":
            # The core carries the DFO family + baselines too, and its five LLM arms are released
            # only when the C0 canary clears — so "missing" here is expected pre-clearance and is
            # reported, never failed on.
            print(f"[arm_coverage] c1   (core, canary-gated): {len(got)} units: {' '.join(sorted(got))}")
            continue
        want = EXPECTED.get(line, LEG_ARMS)
        missing = want - got
        if missing:
            rc = 2
            print(f"[arm_coverage] {line:<5} MISSING {sorted(missing)}  (has {sorted(got & want)})")
        else:
            print(f"[arm_coverage] {line:<5} ok  {len(got & want)}/{len(want)} arms submitted")
    print("[arm_coverage] VERDICT:", "ALL LINES FULL" if rc == 0 else "*** AN ARM IS MISSING ***")

    # --- B1 matched-budget watch: author-side attrition, per ARM ------------------------------- #
    att = attrition(root)
    total = sum(att.values())
    if total:
        worst = max(att.values())
        spread = worst - min(att.get(a, 0) for a in LEG_ARMS)
        print(f"[attrition] author-side rejects total={total} "
              f"by arm: {dict(sorted(att.items(), key=lambda kv: -kv[1]))}")
        per_line = attrition_by_line(root)
        lines_seen = sorted({ln for ln, _a in per_line})
        worst_line, worst_spread = None, -1
        for ln in lines_seen:
            vals = [per_line.get((ln, a), 0) for a in LEG_ARMS]
            sp = max(vals) - min(vals)
            if sp > worst_spread:
                worst_line, worst_spread = ln, sp
        if worst_line is not None:
            print(f"[attrition] WITHIN-LINE worst spread = {worst_spread} candidate(s) on "
                  f"{worst_line} -- this is the number the H2 contrast cares about; the pooled "
                  f"figure below mixes 11 lines and can HIDE a handicapped arm (A-attr).")
        print(f"[attrition] POOLED max-min across the five arms = {spread} candidate(s). "
              "These are NEVER replaced, so this is the per-arm search-width handicap. "
              "Report it; do not silently average over it.")
    else:
        print("[attrition] no author-side rejects yet — arms are budget-matched")

    # --- route the sentinel's outstanding verdicts somewhere a decision gets made (D15) --------- #
    worst = sentinel_worst(root)
    if not worst:
        print("[sentinel] no outstanding non-OK verdicts")
    else:
        for sev, check, ts, detail in worst:
            print(f"[sentinel] {sev:<8} {check:<26} {ts}  {detail}")
        if any(s == "CRITICAL" for s, *_ in worst):
            print("[sentinel] *** A CRITICAL VERDICT IS OUTSTANDING — this is a VALIDITY issue, "
                  "not a slowdown. Do not treat six green guards as a clean run. ***")
            rc = 2
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
