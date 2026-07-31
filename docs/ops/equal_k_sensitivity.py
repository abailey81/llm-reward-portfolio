"""THE PRE-REGISTERED EQUAL-k SENSITIVITY — reference implementation (registry row 37, record 26.3).

s.26.3 registered this obligation PRE-DATA:

    "report per-arm accepted-candidate counts beside every H2 contrast + a pre-committed
     equal-k sensitivity analysis"

s.56 turned it from a robustness garnish into a load-bearing control: a rejected candidate is NEVER
replaced, so arms search different widths, and each arm's winner is `max(val_fitness)` over its pool.
E[max] rises with n, so a STARVED comparator makes its IUT leg easier to reject -- biased TOWARD a
false positive. The remedy is to truncate every arm to a COMMON k and re-select.

s.65 proved this is implementable: over 1,052 records, 0 missing `generation`, 0 missing
`candidate_id`, 0 unparseable -- the registered order is fully recoverable.

WHY THIS LIVES IN docs/ops/ AND NOT IN scripts/analyze_campaign.py
    `scripts/` is inside the drift watch (record s.3): the drivers execute the sha they were launched
    from, and an edit there -- committed or not -- makes the drift check permanently non-zero, turning
    the 2-minute monitor into a standing alarm for code the drivers never import. This is therefore
    the VERIFIED REFERENCE IMPLEMENTATION, to be ported into `analyze_campaign.py` as a mechanical
    step once the campaign is off the drift watch. Building it now removes the risk that a
    pre-registered analysis is discovered to be unimplementable after the data is in.

TWO RULES THAT MAKE THIS A SENSITIVITY RATHER THAN A SELECTION
    1. Truncation follows the REGISTERED (generation, candidate index) ORDER -- never the score.
       Truncating on score would manufacture exactly the selection effect the analysis removes.
    2. R115 eligibility is applied at BOTH widths. The winner is the best ELIGIBLE candidate, so a
       fallback-contaminated candidate cannot win either pool (record 67.2 shows the floor doing
       exactly this on the live archive).

SCOPE: validation-side. It answers "does matching the draws change WHICH candidate wins?", which is
the mechanism by which the imbalance would bias an IUT leg. The full analysis-time version re-runs the
IUT on SEALED data at the seed ladder; that is deliberately not done here and must not be.
"""
from __future__ import annotations

import glob
import json
import math
import os
import re
import sys
from collections import defaultdict

ROOT = "outputs/campaign_cluster_run4"
ARMS = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")
R115_FLOOR = 0.10                       # a candidate falling back on >=10% of steps cannot win
CID = re.compile(r"^(?P<arm>[a-z0-9_]+)-g(?P<gen>\d+)-c(?P<idx>\d+)$")


def line_of(norm: str) -> str:
    for part in norm.split("/"):
        if part.startswith("search"):
            return "core" if part == "search" else part[len("search_"):]
    return "?"


def load() -> dict[tuple[str, str], list[dict]]:
    """Return {(line, arm): [candidate, ...]} in REGISTERED order."""
    pools: dict[tuple[str, str], list[dict]] = defaultdict(list)
    seen: set[tuple[str, str, str]] = set()
    for path in glob.glob(os.path.join(ROOT, "search*", "**", "record.json"), recursive=True):
        norm = path.replace("\\", "/")
        if "/.pull_tmp" in norm:
            continue
        try:
            rec = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        arm = rec.get("arm")
        if arm not in ARMS:
            continue
        cid = str(rec.get("candidate_id") or "")
        m = CID.match(cid)
        if not m:
            continue
        line = line_of(norm)
        key = (line, arm, cid)
        if key in seen:                 # D18: one record can sit at two paths; count it once
            continue
        seen.add(key)
        mt = rec.get("metrics") or {}
        calls, dflt = mt.get("train_safe_call_count"), mt.get("train_safe_default_count")
        frac = (float(dflt) / float(calls)) if calls else 0.0
        fit = mt.get("val_fitness")
        pools[(line, arm)].append({
            "cid": cid,
            "order": (int(m.group("gen")), int(m.group("idx"))),
            "fit": float(fit) if isinstance(fit, (int, float)) and math.isfinite(fit) else None,
            "frac": frac,
            "eligible": frac < R115_FLOOR,
        })
    for key in pools:
        pools[key].sort(key=lambda c: c["order"])       # REGISTERED order, never score
    return pools


def winner(cands: list[dict]) -> dict | None:
    """Best ELIGIBLE candidate by validation fitness (R115 applied)."""
    ok = [c for c in cands if c["eligible"] and c["fit"] is not None]
    return max(ok, key=lambda c: c["fit"]) if ok else None


def main() -> int:
    pools = load()
    lines = sorted({ln for ln, _ in pools})
    print(f"lines: {len(lines)}   (line, arm) pools: {len(pools)}")
    print()

    changed_total = full_total = 0
    rows = []
    for ln in lines:
        sizes = {a: len(pools.get((ln, a), [])) for a in ARMS}
        present = {a: n for a, n in sizes.items() if n}
        if len(present) < 2:
            continue
        k = min(present.values())
        for arm in ARMS:
            cands = pools.get((ln, arm), [])
            if not cands:
                continue
            w_full = winner(cands)
            w_k = winner(cands[:k])
            if w_full is None:
                continue
            full_total += 1
            same = (w_k is not None and w_k["cid"] == w_full["cid"])
            if not same:
                changed_total += 1
            drop = ((w_full["fit"] - w_k["fit"]) if w_k else None)
            rows.append((ln, arm, len(cands), k, w_full, w_k, same, drop))

    print(f"{'line':22s} {'arm':17s} {'n':>4s} {'k':>3s} {'winner(full)':>22s} {'fit':>8s} "
          f"{'winner(equal-k)':>22s} {'fit':>8s}  same")
    for ln, arm, n, k, wf, wk, same, drop in rows:
        wkc = wk["cid"] if wk else "-- none eligible --"
        wkf = f"{wk['fit']:.5f}" if wk else "n/a"
        print(f"{ln:22s} {arm:17s} {n:4d} {k:3d} {wf['cid']:>22s} {wf['fit']:8.5f} "
              f"{wkc:>22s} {wkf:>8s}  {'yes' if same else '*** NO ***'}")

    print()
    print("=" * 96)
    print(f"pools evaluated                         : {full_total}")
    print(f"pools whose WINNER CHANGES under equal-k : {changed_total} "
          f"({100.0 * changed_total / full_total:.1f}%)" if full_total else "")
    drops = [d for *_, d in rows if d is not None and d > 0]
    if drops:
        drops.sort()
        print(f"fitness given up by matching the draws   : median {drops[len(drops)//2]:.5f}  "
              f"max {drops[-1]:.5f}")
    print()
    print("READ THIS AS: the fraction of arms whose selected candidate is an artefact of having")
    print("searched WIDER than its comparator. It is the mechanism s.56 warned about, measured.")
    print("The analysis-time version re-runs the IUT on SEALED data; this is the selection half.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
