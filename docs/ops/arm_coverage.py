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
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
