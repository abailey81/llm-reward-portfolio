"""RESULTS AUDIT — open every record and ask whether what is INSIDE it is coherent.

The six repo guards, `arm_coverage.py` and `science_watch.py` all check EXECUTION. None of them opens
a record. The standing lesson (record §20.2) is that a session once reported "the science checks out"
having verified only invariants, and was right to be challenged. This is the pass that opens them.

EFFECT-BLIND BY CONSTRUCTION: no performance field is read except to confirm it is finite. The single
confirmatory look stays at the pre-declared date.

Five passes:
  1. INTEGRITY  - duplicate run_ids, reward_source_hash == sha256(reward_source), schema, ranges,
                  non-finite metrics.
  2. CONSTRUCT  - the fed block re-derived from the PROMPT of every LLM-arm record, per arm.
  3. DIVERSITY  - distinct authored programs per arm, and any program shared ACROSS arms.
  4. POPART     - is normalisation ENGAGED or pinned at its `popart_min_scale` floor, and is the
                  invariant sigma_max == max(floor, raw_rms_max) satisfied.
  5. ANOMALY    - the D17 method: numbers that repeat where independence says they should not.

Usage:  python docs/ops/results_audit.py [run_root]      (default outputs/campaign_cluster_run4)
Exit 2 if any HARD invariant fails; 0 otherwise. Findings that are properties rather than faults are
printed as NOTE and never change the exit code.

⚠ THREE TRAPS THIS SCRIPT WAS BITTEN BY AND NOW ENCODES:
  * metrics are NESTED under record["metrics"]; a flat accessor silently reads None for everything.
  * `popart_scale` is a DICT, not a float. Type-checking for (int, float) reports "0 records carry it".
  * sigma_max and raw_rms_max agree to ~1e-9 RELATIVE, not absolutely; an absolute tolerance produced
    45 false "invariant breaks". Overstating a risk is as inaccurate as understating one.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict

ROOT = sys.argv[1] if len(sys.argv) > 1 else "outputs/campaign_cluster_run4"
LLM_ARMS = ("distributional", "scalar", "placebo", "scalar_cvar5", "placebo_shuffled")
#: the registered number of DECIMAL values each arm's fed block carries from generation 1 onward
EXPECTED_DECIMALS = {"distributional": 6, "scalar": 1, "scalar_cvar5": 2,
                     "placebo": 6, "placebo_shuffled": 6}
POPART_FLOOR = 1.0          # config/algos.yaml popart_min_scale
TAIL_WORDS = ("cvar", "shortfall", "quantile")

hard_failures: list[str] = []

#: Any list longer than this is replaced by its LENGTH at load time (see `_shrink`).
_BIG = 64


def _shrink(obj):
    """Replace every long list inside a parsed record with its LENGTH, recursively.

    ⚠ P290, 2026-08-04. MEASURED, not modelled: this file peaked at **8,032 MB** during a
    seven-layer run, against P270's recorded 1,475 MB for the same tool -- 5.4x -- while
    `integrity_gate` peaked at 6,899 MB and free RAM fell to 0.46 GB on a 15.64 GB box hosting ~30
    driver and supervisor processes. The cause is `records.append(rec)` below holding every full
    record, and the mean sealed test record is ~477 KB of JSON.

    ⚠ SAFE BECAUSE IT WAS CHECKED, NOT ASSUMED. The only generic read of a metric VALUE in this file
    is the non-finite scan, whose predicate is `isinstance(v, float)` -- STRICTLY float. A list was
    never examined by it, and an int is not examined either, so replacing a long list with its length
    leaves that check bit-identical. A grep for `test_returns|per_period_pnl|train_curve|
    test_exposure|test_alloc` finds no other reference anywhere in this file.

    The rule is STRUCTURAL rather than a whitelist of field names, so a record schema that grows a
    new array is covered without anyone remembering to update a list. Any future code that tries to
    index or `len()` one FAILS LOUDLY instead of silently reading a wrong value.
    """
    if isinstance(obj, list):
        if len(obj) > _BIG:
            return len(obj)
        return [_shrink(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _shrink(v) for k, v in obj.items()}
    return obj


records = []
for path in glob.glob(os.path.join(ROOT, "**", "record.json"), recursive=True):
    # Exclude the in-flight staging tree AND the set-aside past, per the convention
    # `scripts/sentinel.py:1348` established after three instruments tripped on it: a pull
    # stages into `.pull_tmp.<pid>/` (byte-identical duplicates of canonical records -- D18,
    # observed 2026-07-31), and `_quarantined*` holds an earlier run's records.
    if any(seg.startswith((".pull_tmp", "_quarantined")) for seg in
           os.path.relpath(path, ROOT).replace("\\", "/").split("/")[:-1]):
        continue
    try:
        rec = json.load(open(path, encoding="utf-8"))
    except Exception as exc:                                   # noqa: BLE001
        hard_failures.append("UNREADABLE %s (%s)" % (path, exc))
        continue
    rec["_path"] = path.replace("\\", "/")
    rec["_root"] = os.path.relpath(path, ROOT).replace("\\", "/").split("/")[0]
    records.append(_shrink(rec))

print("results_audit: %d records under %s" % (len(records), ROOT))

# ------------------------------------------------------------------ 1 INTEGRITY
print("\n== 1. INTEGRITY ==")
dupes = {k: v for k, v in Counter((r["_root"], r.get("run_id")) for r in records).items() if v > 1}
print("  duplicate (root, run_id) : %d %s" % (len(dupes), list(dupes)[:3]))
if dupes:
    print("     NOTE D18: a record can exist at two paths. analyze_campaign.py dedupes by run_id and")
    print("     is depth-limited, so the confirmatory path is safe; recursive consumers are not.")

bad = [r["run_id"] for r in records
       if r.get("reward_source") is not None and r.get("reward_source_hash") is not None
       and hashlib.sha256(r["reward_source"].encode("utf-8")).hexdigest() != r["reward_source_hash"]]
print("  reward_source_hash mismatches : %d %s" % (len(bad), bad[:3]))
if bad:
    hard_failures.append("reward_source_hash mismatch on %d record(s)" % len(bad))

missing = Counter()
for r in records:
    for f in ("arm", "run_id", "seed", "generation", "metrics", "reward_source"):
        if f not in r:
            missing[f] += 1
print("  missing required fields  : %s" % (dict(missing) or "NONE"))
if missing:
    hard_failures.append("missing required fields: %s" % dict(missing))

oor = [(r.get("run_id"), k, v) for r in records
       for k, v in (("generation", r.get("generation")), ("seed", r.get("seed")))
       if isinstance(v, int) and not (0 <= v <= (5 if k == "generation" else 567))]
print("  out-of-range gen/seed    : %d %s" % (len(oor), oor[:3]))
if oor:
    hard_failures.append("out-of-range generation/seed on %d record(s)" % len(oor))

nonfinite = [(r.get("run_id"), k) for r in records for k, v in (r.get("metrics") or {}).items()
             if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf")))
             and not (k == "val_fitness" and str(r.get("arm", "")).startswith("baseline"))]
print("  non-finite metrics       : %d %s" % (len(nonfinite), nonfinite[:3]))
if nonfinite:
    hard_failures.append("non-finite metrics on %d record(s)" % len(nonfinite))

# ------------------------------------------------------------------ 2 CONSTRUCT
print("\n== 2. CONSTRUCT VALIDITY (re-derived from every LLM-arm prompt) ==")
NUM = re.compile(r"-?\d+\.\d+")
hist = defaultdict(Counter)
leaks = []
for r in records:
    arm = r.get("arm")
    if arm not in LLM_ARMS:
        continue
    prompt = r.get("prompt") or ""
    low = prompt.lower()
    idx = max(low.find("reference value"), low.find("feedback"), low.find("realised"),
              low.find("realized"))
    block = prompt[idx:idx + 1200] if idx >= 0 else ""
    hist[arm][len(NUM.findall(block))] += 1
    if arm == "scalar" and any(w in low for w in TAIL_WORDS):
        leaks.append(r.get("run_id"))
for arm in LLM_ARMS:
    if not hist[arm]:
        continue
    want = EXPECTED_DECIMALS[arm]
    counts = hist[arm]
    good = counts.get(want, 0)
    zero = counts.get(0, 0)                       # generation 0 has nothing to feed
    other = sum(n for k, n in counts.items() if k not in (want, 0))
    print("  %-18s n=%3d  expected(%d)=%3d  g0(0)=%3d  OTHER=%d" % (arm, sum(counts.values()),
                                                                    want, good, zero, other))
    if other:
        hard_failures.append("%s: %d prompt(s) carry an unexpected decimal count %s"
                             % (arm, other, [k for k in counts if k not in (want, 0)]))
print("  scalar prompts leaking a tail statistic : %d %s" % (len(leaks), leaks[:3]))
if leaks:
    hard_failures.append("tail vocabulary leaked into %d scalar prompt(s)" % len(leaks))

# ------------------------------------------------------------------ 3 DIVERSITY
print("\n== 3. AUTHORED-PROGRAM DIVERSITY ==")
by_arm = defaultdict(list)
hash_arms = defaultdict(set)
for r in records:
    if r.get("arm") in LLM_ARMS and r.get("reward_source_hash"):
        by_arm[r["arm"]].append(r["reward_source_hash"])
        hash_arms[r["reward_source_hash"]].add(r["arm"])
for arm in LLM_ARMS:
    hs = by_arm[arm]
    if hs:
        print("  %-18s records=%3d distinct=%3d (%.0f%% unique)"
              % (arm, len(hs), len(set(hs)), 100.0 * len(set(hs)) / len(hs)))
shared = [h for h, a in hash_arms.items() if len(a) > 1]
print("  programs identical ACROSS arms : %d" % len(shared))

# ---------------------------------------------------------------- 3b E[max] ARM POOLS
# ★ 2026-08-01 (RUN 10, record §100.14): THE ARM-DEPTH ALARM WAS POOLING A DISJOINT CONDITION,
# AND IT WAS MOVING IN THE OPPOSITE DIRECTION TO THE RISK IT NAMES.
#
# The counts in section 3 above are the right ones for DIVERSITY -- every authored program counts,
# wherever it was authored. They are the WRONG ones for the E[max] arm-depth ratio, which the cycle
# escalates on, because they include the H3 SINGLE-SHOT control. `*_h3_singleshot/` writes its own
# search/frozen/test subtrees under the SAME output dir with `arm='distributional'`, and it is a
# DISJOINT hypothesis condition (DEEP_H3 §1) -- `analyze_campaign.py`'s walker skips it explicitly,
# with a comment saying that walking in would "silently pool single-shot candidates into the
# HEADLINE distributional arm's records". The ops metric did exactly that.
#
# MEASURED at the moment of the fix: distributional read 521, of which **244 were h3_singleshot**;
# every other arm 0. The alarm reported a spread of **2.39x** for a quantity whose value is 1.30x.
#
# ⚠ AND IT WAS ABOUT TO GET MUCH LOUDER WHILE THE RISK SHRANK. h3ss entered packed C4 and is
# producing ~116 records/h, ALL tagged distributional, so this alarm would have climbed through
# 3x, 4x, 5x over the following hours -- while the actual H2 imbalance IMPROVED (the core line
# measured 1.87x -> 1.65x over the same night). An alarm that rises as its own risk falls is worse
# than no alarm: it trains the operator to ignore the one number that guards the headline
# hypothesis. Raised by the ANALYSIS lane; verified first-hand here before changing anything.
#
# Section 3 is left untouched -- both facts are true and neither may be conflated.
print("\n== 3b. E[max] ARM POOLS (h3_singleshot EXCLUDED -- disjoint H3 condition) ==")
_pool = Counter()
for r in records:
    if r.get("arm") in LLM_ARMS and r.get("reward_source_hash") \
            and not str(r.get("_root", "")).endswith("_h3_singleshot"):
        _pool[r["arm"]] += 1
for arm in LLM_ARMS:
    if _pool[arm]:
        print("  %-18s pool=%3d" % (arm, _pool[arm]))
_iut = [_pool[a] for a in ("distributional", "scalar", "placebo", "scalar_cvar5") if _pool[a]]
if len(_iut) >= 2:
    print("  H2 IUT pool spread : %.3fx  (max=%d min=%d)"
          % (max(_iut) / min(_iut), max(_iut), min(_iut)))
    print("     The winner is max(val_fitness) over the SEARCH pool, so E[max] rises with pool size;")
    print("     a starved comparator makes its IUT leg easier to reject. This is the ratio that")
    print("     bears on H2 -- section 3's counts include the disjoint H3 single-shot condition.")
if shared:
    print("     NOTE: identical code under different feedback is INTERESTING (it is what a null looks")
    print("     like at the code level), but it must be checked against a prompt mix-up before it is")
    print("     reported as a result.")

# ------------------------------------------------------------------ 4 POPART
print("\n== 4. POPART: instrumented, or actually ENGAGED? ==")
eng = Counter()
breaks = []
for r in records:
    p = (r.get("metrics") or {}).get("popart_scale")
    if not isinstance(p, dict):
        continue
    smax, rmax = p.get("sigma_max"), p.get("raw_rms_max")
    if isinstance(smax, (int, float)) and isinstance(rmax, (int, float)):
        expect = max(POPART_FLOOR, float(rmax))
        if abs(float(smax) - expect) > 1e-6 * max(1.0, expect):
            breaks.append(r.get("run_id"))
        eng["engaged" if float(smax) > POPART_FLOOR else "pinned at the floor"] += 1
tot = sum(eng.values())
for k, v in eng.most_common():
    print("  %-22s %5d (%.1f%%)" % (k, v, 100.0 * v / tot if tot else 0.0))
print("  invariant sigma_max == max(%.1f, raw_rms_max) breaks : %d" % (POPART_FLOOR, len(breaks)))
if breaks:
    hard_failures.append("PopArt invariant broken on %d record(s)" % len(breaks))
if eng.get("pinned at the floor"):
    print("     NOTE (obligation 9): PopArt is INERT wherever sigma sits at the floor. ON is not")
    print("     ENGAGED - report the engagement rate beside any H1 family comparison.")

# ------------------------------------------------------------------ 5 ANOMALY
print("\n== 5. ANOMALY HUNT (the D17 method) ==")
frac = Counter()
for r in records:
    m = r.get("metrics") or {}
    c, d = m.get("train_safe_call_count"), m.get("train_safe_default_count")
    if isinstance(c, (int, float)) and isinstance(d, (int, float)) and c:
        frac[round(d / c, 6)] += 1
repeats = [(f, n) for f, n in frac.most_common() if f > 0 and n > 2]
print("  non-zero safe-default fractions repeating >2x : %s" % (repeats or "none"))
if repeats:
    print("     NOTE: a REPEATED non-zero fraction is the D17 signature (a fail-safe clearing the")
    print("     reward's state produces period = warm-up calls + 1). Investigate before reporting.")

rms = defaultdict(list)
for r in records:
    p = (r.get("metrics") or {}).get("popart_scale")
    if isinstance(p, dict) and isinstance(p.get("raw_rms_max"), (int, float)):
        rms[round(float(p["raw_rms_max"]), 1)].append((r.get("arm"), r.get("run_id")))
clusters = [(v, rows) for v, rows in rms.items() if len(rows) > 3 and v > 1000]
print("  large raw_rms_max values shared by >3 records : %s"
      % ([(v, len(rows)) for v, rows in clusters] or "none"))

print("\n== VERDICT ==")
if hard_failures:
    print("  *** %d HARD FAILURE(S) ***" % len(hard_failures))
    for f in hard_failures:
        print("      -", f)
    sys.exit(2)
print("  no hard invariant failed. NOTEs above are properties to REPORT, not faults to fix.")
sys.exit(0)
