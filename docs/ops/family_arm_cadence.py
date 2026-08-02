"""SEQUENTIAL FAMILY-ARM CADENCE -- the true critical path of RUN 4's core line.

WHY (RUN 13, 2026-08-02). The core line's H4 comparators `bayes_opt` (GP-EI), `cma_es` and `tpe` are
INHERENTLY SEQUENTIAL: each proposal is a function of the fitnesses already observed, so the code
runs them as an array-of-1 per candidate (`campaign.run_family_search_arm`, the comment there says
so in as many words). `random_search` is the opposite -- it samples all 30 sources UP FRONT and runs
them as ONE batch -- and it finished 30/30 long ago.

That asymmetry is the whole throughput story of the core line, and it is invisible in a slot count:
three arms, one 8-slot job each, 24 slots total, and the C1 barrier at `campaign.py` `as_completed`
cannot release until the SLOWEST of them has spent its full 30-candidate budget. Because the
reported result is the COMMON rung over all 11 lines, and the core line is one of them, the core
line's slowest sequential arm sets the date the whole campaign can enter C4.

This measures the REALISED cadence (hours per candidate, wall-to-wall, including the optimiser step
and queueing) rather than the training time alone -- the training time is the part we already knew
and is not what governs a sequential chain.

BLIND: reads candidate directory names, record mtimes and `wall_clock`. `wall_clock` is a duration,
not an outcome; no metric, return series or fitness is read.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else "outputs/campaign_cluster_run4/search")
BUDGET = 30          # config/campaign.yaml: candidates_per_arm
ARMS = sys.argv[2].split(",") if len(sys.argv) > 2 else ["cma_es", "bayes_opt", "tpe"]

print(f"budget per arm = {BUDGET} candidates (config/campaign.yaml: candidates_per_arm)")
print()
worst = (None, 0.0)
for arm in ARMS:
    d = ROOT / arm
    if not d.is_dir():
        print(f"== {arm}: MISSING")
        continue
    rows = []
    for x in sorted(d.iterdir()):
        r = x / "record.json"
        if not r.exists():
            continue
        try:
            wc = json.load(r.open(encoding="utf-8")).get("wall_clock")
        except Exception:
            wc = None
        rows.append((x.name, dt.datetime.fromtimestamp(r.stat().st_mtime), wc))
    rows.sort(key=lambda t: t[1])
    print(f"== {arm}   done={len(rows)}/{BUDGET}   remaining={BUDGET - len(rows)}")
    gaps = []
    prev = None
    for nm, t, wc in rows:
        g = (t - prev).total_seconds() / 3600.0 if prev else 0.0
        if prev:
            gaps.append(g)
        tw = (wc / 3600.0) if isinstance(wc, (int, float)) and wc else 0.0
        print(f"   {nm:18s} {t:%m-%d %H:%M}   gap={g:6.2f} h   train_wall={tw:5.2f} h")
        prev = t
    if gaps:
        s = sorted(gaps)
        med = s[len(s) // 2]
        mean = sum(gaps) / len(gaps)
        rem = BUDGET - len(rows)
        eta_med = rem * med
        eta_mean = rem * mean
        print(f"   -> CADENCE median {med:.2f} h/cand, mean {mean:.2f} h/cand")
        print(f"   -> ETA to finish this arm: {eta_med:.0f} h ({eta_med/24:.1f} d) at median, "
              f"{eta_mean:.0f} h ({eta_mean/24:.1f} d) at mean")
        if eta_med > worst[1]:
            worst = (arm, eta_med)
    print()

if worst[0]:
    print(f"CRITICAL PATH OF THE CORE LINE: {worst[0]}, ~{worst[1]:.0f} h ({worst[1]/24:.1f} d) of")
    print("SEQUENTIAL work remaining before the C1 barrier can release. Adding cores cannot shorten")
    print("a sequential chain; only a shorter chain or a faster per-link time can.")
