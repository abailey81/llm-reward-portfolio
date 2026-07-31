"""DEEP RESULTS AUDIT, stage 2: is the EFFECTIVE SEARCH WIDTH really K = 5?

Stage 1 found one bit-identical cross-arm outcome pair, explained as two functionally identical
programs at generation 0 (where the arms share the base prompt, so they are exchangeable by design).
That is benign -- but it raises a much sharper question that nothing in the campaign measures:

  *** WITHIN one (line, arm, generation), do the 5 candidates actually EXPLORE 5 DISTINCT designs? ***

The prompt carries an explicit exploration directive -- "propose a reward DISTINCT from the other
candidates this generation ... Do not reuse a design you would give a different candidate index."
If candidates collapse onto near-identical designs, the EFFECTIVE search width is below 5, and that
matters directly:
  * K = 5 search width is a REGISTERED limitation of the design;
  * every arm's winner is max(val_fitness) over its pool, and E[max] depends on the number of
    genuinely INDEPENDENT draws, not the number of submitted jobs. s.56's whole argument about
    starved comparators is an E[max] argument, so the effective n is the quantity that matters.

Measures three things per (line, arm, generation):
  1. distinct reward-program hashes among the candidates
  2. distinct OUTCOME series (bit-identical returns => the same policy)
  3. NEAR-duplicate outcomes: pairwise Pearson correlation > 0.9999 (functionally the same policy
     even when the source text differs)

VALIDATION-side only. Nothing here touches the sealed test comparison.
"""
import glob
import hashlib
import json
import math
import os
import statistics as st
from collections import defaultdict
from itertools import combinations

ROOT = "outputs/campaign_cluster_run4"
LLM_ARMS = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")
NEAR = 0.9999

units = defaultdict(list)
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
    g = r.get("generation")
    if not isinstance(vr, list) or not vr or not isinstance(g, int):
        continue
    line = next((("core" if x == "search" else x[len("search_"):])
                 for x in n.split("/") if x.startswith("search")), "?")
    units[(line, r["arm"], g)].append({
        "cid": r.get("candidate_id"), "prog": r.get("reward_source_hash"),
        "out": hashlib.sha256(json.dumps(vr).encode()).hexdigest(),
        "vr": vr, "fit": m.get("val_fitness"),
    })


def corr(a, b):
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]
    ma, mb = st.fmean(a), st.fmean(b)
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    if va <= 0 or vb <= 0:
        return float("nan")
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    return cov / math.sqrt(va * vb)


tot_cands = tot_units = 0
prog_dup_units = out_dup_units = near_dup_units = 0
eff_widths = []
examples = []

for key in sorted(units):
    cands = units[key]
    k = len(cands)
    if k < 2:
        continue
    tot_units += 1
    tot_cands += k
    nprog = len({c["prog"] for c in cands})
    nout = len({c["out"] for c in cands})
    if nprog < k:
        prog_dup_units += 1
    if nout < k:
        out_dup_units += 1

    # near-duplicate clustering by correlation
    parent = list(range(k))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    near_pairs = 0
    for i, j in combinations(range(k), 2):
        c = corr(cands[i]["vr"], cands[j]["vr"])
        if math.isfinite(c) and c > NEAR:
            near_pairs += 1
            parent[find(i)] = find(j)
    eff = len({find(i) for i in range(k)})
    eff_widths.append((k, eff))
    if eff < k:
        near_dup_units += 1
        if len(examples) < 8:
            examples.append((key, k, eff, nprog, nout, near_pairs))

print(f"(line, arm, generation) units with >=2 candidates : {tot_units}")
print(f"candidates covered                                : {tot_cands}")
print()
print(f"units with a DUPLICATE reward PROGRAM   : {prog_dup_units}")
print(f"units with a DUPLICATE OUTCOME (exact)  : {out_dup_units}")
print(f"units with NEAR-duplicate outcomes (r > {NEAR}) : {near_dup_units}")
print()
subm = sum(k for k, _ in eff_widths)
effs = sum(e for _, e in eff_widths)
print(f"TOTAL candidates submitted            : {subm}")
print(f"TOTAL effectively-independent designs : {effs}")
print(f"EFFECTIVE SEARCH WIDTH = {effs/tot_units:.3f} of a nominal {subm/tot_units:.3f} "
      f"  ({100.0*effs/subm:.1f}% of submitted candidates are independent)")
print()
if examples:
    print("units where candidates COLLAPSED (nominal k -> effective):")
    for key, k, eff, nprog, nout, np_ in examples:
        print(f"   {key[0]:22s} {key[1]:16s} g{key[2]}  k={k} -> eff={eff}  "
              f"(distinct progs {nprog}, distinct outcomes {nout}, near-pairs {np_})")
else:
    print("NO unit shows candidate collapse: every candidate is an independent design.")
