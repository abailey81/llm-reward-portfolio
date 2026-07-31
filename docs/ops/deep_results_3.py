"""DEEP RESULTS AUDIT, stage 3: is the SCIENCE behaving the way the design predicts?

Structural validity is established. This asks whether the numbers MEAN anything:

  1. DOES THE REFLECTION LOOP LEARN?  Validation fitness by generation. If g5 is no better than g0,
     the six-round chain -- the entire cost driver of the campaign -- is buying nothing, and that is
     a mechanism finding (SQ1 responsiveness) rather than a bug.
  2. IS SELECTION SIGNAL OR NOISE?  How far is each arm's winner above its own pack? If max is
     barely above median, "the winner" is a draw from noise and E[max] dominates.
  3. THE D17 RECIPROCAL SIGNATURE.  s.37 found a limit cycle whose fallback fraction is a RECIPROCAL
     (1/2 -> 49.983%, 1/3 -> 33.333%) because its period is the cold-start warm-up plus one. Sweep
     for every record whose fallback fraction is close to 1/k for small k -- that identifies
     harness-trapped rewards which are biased AGAINST their own model.
  4. DO THE FED TAIL NUMBERS ACTUALLY VARY?  If the six fed scalars are near-constant across
     candidates, the manipulation carries no information to vary on -- the A5 rational-insensitivity
     account (s.52's fed-delta SNR question) in its starkest form.

REPORT-ONLY / VALIDATION-SIDE. Nothing here touches the sealed test data or computes an H2 statistic.
These are monitoring observations, not inference.
"""
import glob
import json
import math
import os
import statistics as st
from collections import defaultdict

ROOT = "outputs/campaign_cluster_run4"
LLM_ARMS = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")
TAILS = ("cvar_01", "cvar_05", "cvar_10", "cvar_25", "left_tail_mass", "robust_skew")

R = []
for p in glob.glob(os.path.join(ROOT, "search*", "**", "record.json"), recursive=True):
    n = p.replace("\\", "/")
    if "/.pull_tmp" in n:
        continue
    try:
        r = json.load(open(p, encoding="utf-8"))
    except Exception:
        continue
    if r.get("arm") not in LLM_ARMS:
        continue
    m = r.get("metrics") or {}
    f, g = m.get("val_fitness"), r.get("generation")
    if not isinstance(f, (int, float)) or not math.isfinite(f) or not isinstance(g, int):
        continue
    line = next((("core" if x == "search" else x[len("search_"):])
                 for x in n.split("/") if x.startswith("search")), "?")
    calls, dflt = m.get("train_safe_call_count"), m.get("train_safe_default_count")
    R.append({"line": line, "arm": r["arm"], "gen": g, "fit": f, "cid": r.get("candidate_id"),
              "frac": (dflt / calls) if calls else None, "tail": m.get("tail_stats") or {}})

print(f"records: {len(R)}")

# ---- 1. DOES THE LOOP LEARN? ------------------------------------------------
print()
print("=" * 84)
print("1. VALIDATION FITNESS BY GENERATION  (does the six-round reflection chain improve anything?)")
print("=" * 84)
print(f"{'arm':18s} " + " ".join(f"{'g'+str(g):>12s}" for g in range(6)))
for arm in LLM_ARMS:
    row = []
    for g in range(6):
        v = [x["fit"] for x in R if x["arm"] == arm and x["gen"] == g]
        row.append(f"{st.median(v):12.5f}" if v else f"{'-':>12s}")
    print(f"{arm:18s} " + " ".join(row))
print()
print("  same, but BEST-so-far (the quantity selection actually uses):")
print(f"{'arm':18s} " + " ".join(f"{'g'+str(g):>12s}" for g in range(6)))
for arm in LLM_ARMS:
    row, best = [], None
    for g in range(6):
        v = [x["fit"] for x in R if x["arm"] == arm and x["gen"] <= g]
        best = max(v) if v else None
        row.append(f"{best:12.5f}" if best is not None else f"{'-':>12s}")
    print(f"{arm:18s} " + " ".join(row))

# ---- 2. WINNER SEPARATION ---------------------------------------------------
print()
print("=" * 84)
print("2. IS THE WINNER SIGNAL OR NOISE?  (max vs 2nd vs median, per line+arm)")
print("=" * 84)
seps = []
for line in sorted({x["line"] for x in R}):
    for arm in LLM_ARMS:
        v = sorted((x["fit"] for x in R if x["line"] == line and x["arm"] == arm), reverse=True)
        if len(v) < 4:
            continue
        mx, second, med = v[0], v[1], st.median(v)
        ratio = (mx / second) if second > 0 else float("inf")
        seps.append((ratio, line, arm, mx, second, med, len(v)))
seps.sort(reverse=True)
print(f"{'line':22s} {'arm':17s} {'n':>4s} {'max':>9s} {'2nd':>9s} {'median':>9s} {'max/2nd':>8s}")
for ratio, line, arm, mx, sc, med, n in seps[:8]:
    print(f"{line:22s} {arm:17s} {n:4d} {mx:9.5f} {sc:9.5f} {med:9.5f} {ratio:8.2f}")
print("   ...")
for ratio, line, arm, mx, sc, med, n in seps[-4:]:
    print(f"{line:22s} {arm:17s} {n:4d} {mx:9.5f} {sc:9.5f} {med:9.5f} {ratio:8.2f}")
rr = [s[0] for s in seps if math.isfinite(s[0])]
print(f"\n   max/2nd across {len(rr)} line-arm pools: median={st.median(rr):.2f} "
      f"min={min(rr):.2f} max={max(rr):.2f}")

# ---- 3. D17 RECIPROCAL SIGNATURE -------------------------------------------
print()
print("=" * 84)
print("3. D17 RECIPROCAL SIGNATURE SWEEP  (fallback fraction ~ 1/k => a harness-trapped reward)")
print("=" * 84)
hits = []
for x in R:
    f = x["frac"]
    if not f or f < 0.05:
        continue
    for k in range(2, 13):
        if abs(f - 1.0 / k) < 5e-4:
            hits.append((x, k, f))
            break
print(f"   records with fallback >= 5%: {sum(1 for x in R if x['frac'] and x['frac'] >= 0.05)}")
print(f"   of which match a RECIPROCAL 1/k (k=2..12): {len(hits)}  <- the D17 limit-cycle class")
for x, k, f in sorted(hits, key=lambda t: -t[2])[:10]:
    print(f"      {x['line']:22s} {x['arm']:16s} {x['cid']:22s} {f:8.5%}  ~ 1/{k}")

# ---- 4. DO THE FED TAIL NUMBERS VARY? --------------------------------------
print()
print("=" * 84)
print("4. FED-VECTOR VARIATION  (if the six scalars barely move, there is nothing to respond to)")
print("=" * 84)
print(f"{'statistic':18s} {'n':>5s} {'min':>10s} {'median':>10s} {'max':>10s} {'sd':>10s} {'sd/|med|':>9s}")
for t in TAILS:
    v = [x["tail"][t] for x in R if t in x["tail"] and isinstance(x["tail"][t], (int, float))]
    if len(v) < 3:
        continue
    med, sd = st.median(v), st.pstdev(v)
    rel = abs(sd / med) if med else float("inf")
    print(f"{t:18s} {len(v):5d} {min(v):10.5f} {med:10.5f} {max(v):10.5f} {sd:10.5f} {rel:9.3f}")
