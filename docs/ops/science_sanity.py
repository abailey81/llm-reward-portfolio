"""Are the RESULTS meaningful -- not merely present?

The guards in scripts/campaign_guards.py answer "is the machinery correct". This answers the other
half of the standing instruction: do the numbers make sense.

STAGE-AWARENESS IS THE WHOLE POINT, and it is not optional. A test-leg baseline record carries
`val_fitness` PRESENT-but-NaN, because a hand-written H1 comparator has no validation-selected
winner; its score is `test_sharpe`. Applying the search-record schema to it counts a perfectly
healthy record as corrupt -- which is exactly the false positive the repo's own sentinel was fixed
for on 2026-07-28 (`_primary_metric`), and which I reproduced in an ad-hoc check before reading it.

Lives under docs/ops/ deliberately: scripts/ is inside the drift pathspec, and RUN 4 is live.
"""
from __future__ import annotations

import glob
import json
import math
import statistics
import sys
from collections import defaultdict

ROOT = sys.argv[1] if len(sys.argv) > 1 else "outputs/campaign_cluster_run4"


def primary(rec: dict) -> tuple[str, float | None]:
    """(name, value) of the score that MATTERS for this record's stage."""
    m = rec.get("metrics", {}) or {}
    # a frozen/test record is scored on the sealed window; val_fitness is inherited or absent
    if rec.get("frozen") or "test_sharpe" in m:
        return "test_sharpe", m.get("test_sharpe")
    return "val_fitness", m.get("val_fitness")


def finite(x) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(x)


rows = []
for f in glob.glob(f"{ROOT}/**/record.json", recursive=True):
    try:
        r = json.load(open(f, encoding="utf-8"))
    except Exception:  # noqa: BLE001
        continue
    name, val = primary(r)
    m = r.get("metrics", {}) or {}
    rows.append({
        "arm": r.get("arm"), "run_id": r.get("run_id"), "stage": name, "score": val,
        "steps": m.get("train_safe_call_count"), "fallback": m.get("train_safe_default_count"),
        "n_ret": len(m.get("test_returns") or m.get("val_returns") or []),
        "frozen": bool(r.get("frozen")),
    })

if not rows:
    print("no records yet")
    raise SystemExit(0)

print(f"=== {len(rows)} records ===\n")
by_arm: dict[str, list] = defaultdict(list)
for r in rows:
    by_arm[r["arm"]].append(r)

for arm in sorted(by_arm):
    rs = by_arm[arm]
    scores = [r["score"] for r in rs if finite(r["score"])]
    stage = rs[0]["stage"]
    bad = [r for r in rs if not finite(r["score"])]
    s = (f"mean={statistics.mean(scores):+.4f} min={min(scores):+.4f} max={max(scores):+.4f}"
         if scores else "no finite scores yet")
    print(f"  {arm:32s} n={len(rs):3d} [{stage}] {s}")
    if bad:
        print(f"       ^ {len(bad)} record(s) with a NON-FINITE {stage}  <-- investigate")

print()
print("--- INVARIANTS ---")
steps_bad = [r for r in rows if r["steps"] not in (None, 400000)]
fb_bad = [r for r in rows if (r["fallback"] or 0) > 0]
ret_bad = [r for r in rows if r["n_ret"] == 0]
print(f"  every training ran the registered 400,000 steps : {'YES' if not steps_bad else f'NO ({len(steps_bad)})'}")
print(f"  R115 floor -- any reward fell back to R66       : {'none' if not fb_bad else f'{len(fb_bad)} RECORDS'}")
print(f"  every record carries a return series            : {'YES' if not ret_bad else f'NO ({len(ret_bad)})'}")

print()
print("--- IS THE SEARCH ACTUALLY SEARCHING? (identical scores would mean it is not) ---")
for arm in sorted(by_arm):
    scores = [r["score"] for r in by_arm[arm] if finite(r["score"])]
    if len(scores) >= 2:
        spread = max(scores) - min(scores)
        print(f"  {arm:32s} spread={spread:+.4f} over n={len(scores)}"
              f"   {'<-- DEGENERATE, all identical' if spread == 0 else ''}")
