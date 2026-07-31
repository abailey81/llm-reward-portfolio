"""VERIFY THE TAIL MEASUREMENT INSTRUMENT against its own inputs.

This is the deepest available check of the quantity that IS H2's manipulated variable. The test-lane
records carry BOTH the realised return series (`test_returns`) and the archived tail measurement
(`test_cvar05`), so the estimator can be re-derived from the data it was computed on -- something no
other record type permits (search-lane `tail_stats` are training-period while `val_returns` are
validation, so they are not comparable).

WHAT IS AND IS NOT EXPECTED. Per amendment R27 the shipped estimator is a **plain GPD-MLE EVT** CVaR,
not the empirical average of the worst 5 %. So an empirical recomputation is NOT expected to match to
the digit -- it is expected to AGREE IN SIGN, MAGNITUDE AND ORDERING. What would be alarming:
  * a sign disagreement (EVT says the left tail is positive)
  * a magnitude disagreement of more than a factor of ~2
  * no rank correlation between the two across records (the estimator would be measuring noise)
That last one is the real test: if the archived CVaR does not track the empirical CVaR of the same
series, the fed vector is not a function of the data it claims to summarise.
"""
import glob
import json
import math
import os
import statistics as st

ROOT = "outputs/campaign_cluster_run4"
ALPHA = 0.05

rows = []
for p in glob.glob(os.path.join(ROOT, "test*", "**", "record.json"), recursive=True):
    n = p.replace("\\", "/")
    if "/.pull_tmp" in n:
        continue
    try:
        r = json.load(open(p, encoding="utf-8"))
    except Exception:
        continue
    m = r.get("metrics") or {}
    tr, cv = m.get("test_returns"), m.get("test_cvar05")
    if not isinstance(tr, list) or len(tr) < 100:
        continue
    if not isinstance(cv, (int, float)) or not math.isfinite(cv):
        continue
    s = sorted(x for x in tr if isinstance(x, (int, float)) and math.isfinite(x))
    if len(s) < 100:
        continue
    k = max(1, int(math.floor(ALPHA * len(s))))
    emp = st.fmean(s[:k])                      # empirical CVaR-5%: mean of the worst 5%
    var5 = s[k - 1]                            # empirical VaR-5% (the quantile itself)
    rows.append({"arm": r.get("arm"), "cid": r.get("candidate_id"), "seed": r.get("seed"),
                 "evt": float(cv), "emp": emp, "var": var5, "n": len(s), "path": n})

print(f"test-lane records carrying BOTH a return series and an archived CVaR: {len(rows)}")
if not rows:
    print("none -- cannot run this check")
    raise SystemExit(0)

print(f"series length: {sorted({r['n'] for r in rows})}")
print()

# ---- sign and magnitude -----------------------------------------------------
sign_bad = [r for r in rows if r["evt"] > 0]
print(f"1. SIGN   archived CVaR-5% > 0 (left tail positive -> impossible): {len(sign_bad)}  <- must be 0")

ratios = [r["evt"] / r["emp"] for r in rows if r["emp"] != 0]
ratios_s = sorted(ratios)
print(f"2. MAGNITUDE  ratio archived/empirical over {len(ratios)} records:")
print(f"     min={ratios_s[0]:.3f}  p10={ratios_s[len(ratios_s)//10]:.3f}  "
      f"median={st.median(ratios):.3f}  p90={ratios_s[9*len(ratios_s)//10]:.3f}  max={ratios_s[-1]:.3f}")
far = [r for r in rows if r["emp"] != 0 and not (0.5 <= r["evt"] / r["emp"] <= 2.0)]
print(f"     records more than 2x away from the empirical value: {len(far)}")
for r in far[:5]:
    print(f"        {r['arm']}/{r['cid']}-s{r['seed']}  evt={r['evt']:.5f} emp={r['emp']:.5f} "
          f"ratio={r['evt']/r['emp']:.2f}")

# ---- does it TRACK the data? (Spearman) -------------------------------------
def spearman(a, b):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        rk = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for t in range(i, j + 1):
                rk[order[t]] = avg
            i = j + 1
        return rk
    ra, rb = rank(a), rank(b)
    ma, mb = st.fmean(ra), st.fmean(rb)
    va = sum((x - ma) ** 2 for x in ra)
    vb = sum((x - mb) ** 2 for x in rb)
    if va <= 0 or vb <= 0:
        return float("nan")
    return sum((x - ma) * (y - mb) for x, y in zip(ra, rb)) / math.sqrt(va * vb)

rho = spearman([r["evt"] for r in rows], [r["emp"] for r in rows])
print()
print(f"3. DOES IT TRACK THE DATA?  Spearman(archived EVT, empirical) = {rho:.4f}")
print("     near +1 => the estimator is a faithful function of the series it summarises")
print("     near  0 => the fed vector would not be measuring these returns at all")

# ---- coherence: CVaR must be at least as extreme as VaR ---------------------
viol = [r for r in rows if r["evt"] > r["var"] + 1e-12]
print()
print(f"4. COHERENCE  CVaR-5% must be <= VaR-5% (tail mean beyond a quantile is more extreme)")
print(f"     violations: {len(viol)}  <- must be 0")
for r in viol[:5]:
    print(f"        {r['arm']}/{r['cid']}-s{r['seed']}  cvar={r['evt']:.5f} var={r['var']:.5f}")
