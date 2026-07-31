"""DEEP RESULTS AUDIT, stage 1: does the manipulated variable actually DO anything?

Everything verified so far proves the archive is STRUCTURALLY sound (hashes, step counts, seeds,
CVaR monotonicity, no cross-arm program reuse). None of it asks whether the NUMBERS ARE MEANINGFUL.
This asks the question that would be most damaging if the answer were wrong:

  *** DO DIFFERENT REWARD PROGRAMS PRODUCE DIFFERENT POLICIES? ***

If two DISTINCT reward programs produce bit-identical validation return series, then the reward did
not influence the policy at all, and the entire experiment measures nothing. That failure would be
invisible to every check run so far -- every such record has a valid hash, 400,000 steps, a finite
fitness and a monotone CVaR vector.

SCOPE DISCIPLINE: this reads VALIDATION-side and training-period quantities only (val_fitness,
val_returns, tail_stats). It does NOT touch the sealed-test comparison and computes nothing
resembling an H2 test statistic. Validation fitness is the SELECTION signal the reflection loop
already consumes, so inspecting it is ordinary monitoring, not peeking.
"""
import glob
import hashlib
import json
import math
import os
import statistics as st
from collections import defaultdict

ROOT = "outputs/campaign_cluster_run4"
LLM_ARMS = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")

recs = []
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
    vr = m.get("val_returns")
    if not isinstance(vr, list) or not vr:
        continue
    line = next((("core" if x == "search" else x[len("search_"):])
                 for x in n.split("/") if x.startswith("search")), "?")
    recs.append({
        "path": n, "line": line, "arm": r["arm"], "cid": r.get("candidate_id"),
        "prog": r.get("reward_source_hash"),
        "fit": m.get("val_fitness"),
        "vr": vr,
        "vr_hash": hashlib.sha256(json.dumps(vr).encode()).hexdigest(),
        "tail": m.get("tail_stats") or {},
    })

print(f"LLM-arm search records with a validation return series: {len(recs)}")
print(f"distinct reward PROGRAMS   : {len({r['prog'] for r in recs})}")
print(f"distinct OUTCOME series    : {len({r['vr_hash'] for r in recs})}")
print()

# ---- A. IDENTICAL OUTCOMES FROM DIFFERENT PROGRAMS -------------------------
by_out = defaultdict(list)
for r in recs:
    by_out[r["vr_hash"]].append(r)

collisions = []
for h, group in by_out.items():
    progs = {g["prog"] for g in group}
    if len(group) > 1 and len(progs) > 1:
        collisions.append((h, group, progs))

print("A. IDENTICAL VALIDATION OUTCOMES FROM *DIFFERENT* REWARD PROGRAMS")
print(f"   colliding outcome series: {len(collisions)}   <- must be 0")
for h, group, progs in collisions[:6]:
    print(f"     outcome {h[:12]} shared by {len(group)} records / {len(progs)} distinct programs:")
    for g in group[:4]:
        print(f"        {g['line']}/{g['arm']}/{g['cid']}  prog={str(g['prog'])[:10]} fit={g['fit']}")

# same program run twice SHOULD give the same outcome (determinism) -- report separately
same_prog_same_out = sum(1 for h, g in by_out.items()
                         if len(g) > 1 and len({x["prog"] for x in g}) == 1)
print(f"   (same program -> same outcome, i.e. DETERMINISM holding: {same_prog_same_out} groups)")

# ---- B. DEGENERATE POLICIES -------------------------------------------------
print()
print("B. DEGENERATE / NON-TRADING POLICIES")
const, near_const, zero_fit = [], [], []
for r in recs:
    vr = r["vr"]
    try:
        sd = st.pstdev(vr)
    except Exception:
        sd = float("nan")
    if sd == 0.0:
        const.append(r)
    elif math.isfinite(sd) and sd < 1e-12:
        near_const.append(r)
    if r["fit"] == 0.0:
        zero_fit.append(r)
print(f"   EXACTLY constant validation return series : {len(const)}")
for r in const[:5]:
    print(f"      {r['line']}/{r['arm']}/{r['cid']}  fit={r['fit']}")
print(f"   near-constant (sd < 1e-12)                : {len(near_const)}")
print(f"   val_fitness exactly 0.0                   : {len(zero_fit)}")

# ---- C. MAGNITUDE SANITY ----------------------------------------------------
print()
print("C. MAGNITUDE SANITY (daily equity-portfolio returns)")
allmax = max(max(abs(x) for x in r["vr"]) for r in recs)
lens = {len(r["vr"]) for r in recs}
print(f"   validation series lengths present : {sorted(lens)}")
print(f"   largest |daily return| anywhere   : {allmax:.4f}")
absurd = [r for r in recs if max(abs(x) for x in r["vr"]) > 1.0]
print(f"   records with a |daily return| > 100% : {len(absurd)}")
for r in absurd[:5]:
    print(f"      {r['line']}/{r['arm']}/{r['cid']} max|r|={max(abs(x) for x in r['vr']):.3f}")

cv5 = [r["tail"]["cvar_05"] for r in recs if "cvar_05" in r["tail"]]
if cv5:
    print(f"   CVaR-5% over {len(cv5)} records: min={min(cv5):.4f} med={st.median(cv5):.4f} max={max(cv5):.4f}")
    imp = [v for v in cv5 if v < -1.0]
    print(f"   implausible CVaR-5% (< -100% daily): {len(imp)}")

# ---- D. FITNESS DISTRIBUTION (selection signal health) ----------------------
print()
print("D. VALIDATION-FITNESS DISTRIBUTION per arm (the SELECTION signal)")
print(f"   {'arm':18s} {'n':>4s} {'min':>9s} {'median':>9s} {'max':>9s} {'#==0':>5s} {'#distinct':>9s}")
for arm in LLM_ARMS:
    f = [r["fit"] for r in recs if r["arm"] == arm and isinstance(r["fit"], (int, float))]
    if not f:
        continue
    print(f"   {arm:18s} {len(f):4d} {min(f):9.5f} {st.median(f):9.5f} {max(f):9.5f} "
          f"{sum(1 for x in f if x == 0.0):5d} {len(set(f)):9d}")
