"""RE-TRIAGE EVERY ACKNOWLEDGED ALARM AGAINST ITS OWN STATED TRIGGER.

docs/ops/acknowledged_alarms.txt carries 8 entries. RUN 8 checked `guard:truncation` (its third-model
trigger had FIRED). The remaining 7 were left unchecked -- which is exactly the "an open item goes
quiet" failure the record's s.20.2 warns about. This works ALL of the live-checkable ones.

Each check derives its answer from the raw archive, NOT by re-running the tool that raised the alarm.
"""
import glob
import json
import os
from collections import defaultdict

ROOT = "outputs/campaign_cluster_run4"
LLM_ARMS = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")
R115_FLOOR = 0.10          # a candidate falling back on >=10% of steps is ineligible to win


def line_of(norm):
    for p in norm.split("/"):
        if p.startswith("search"):
            return "core" if p == "search" else p[len("search_"):]
        if p.startswith("test"):
            return ("TEST:core" if p == "test" else "TEST:" + p[len("test_"):])
    return "?"


def engagement_by_arm(records, arms=LLM_ARMS, floor=1.0):
    """{arm: {rate, cells, records, degenerate}} -- PopArt engagement at the CELL, not the record.

    ⚠⚠ THIS REPLACED A RECORD-LEVEL COUNT THAT RAISED A FALSE ALARM ON THE HEADLINE HYPOTHESIS'S
    OWN PROTECTION, 2026-08-06 (RUN 28).

    `sigma_max = max(popart_min_scale, rms(value targets))`, and the value-target scale is set by the
    REWARD PROGRAM's magnitude. Each `(line, arm)` cell holds ONE frozen winning program retrained
    across up to 568 seeds, so engagement is a property of the CELL and every seed inherits it.
    Measured live: **50 of 54 cells are perfectly degenerate, median cell size 334 seeds.**

    Counting records therefore inflates n by roughly the seed count. It reported a 46.9 pp arm
    spread and printed "*** ASYMMETRIC -- RE-TRIAGE ***" against a registered 5.3 pp baseline, which
    reads as the H2 reward-scale protection having collapsed. At the correct unit the spread is
    35.1 pp over ~11 cells per arm against an SE-of-difference of 21.2 pp (ratio 1.66), with all
    five 95% CIs overlapping -- NOT ESTABLISHED. And on the SEARCH-stage population the 2026-07-30
    baseline actually measured, the arms are still symmetric at 7.0 pp against the recorded 5.3 pp.

    ⚠ NOT AN ALL-CLEAR. "Not established" is not "zero": with ~11 cells per arm this comparison is
    badly underpowered, and the cell count only grows as lines complete their ladders. Re-measure.

    A MIXED cell contributes its FRACTION rather than a hard vote -- 4 of the 54 live cells are
    genuinely mixed (haiku/placebo at 278 of 566 is the largest), and collapsing those to 0/1 would
    discard real information. Records with a null `sigma_max` are EXCLUDED, never counted as pinned:
    a missing field is unknown, not evidence.
    """
    cells = defaultdict(list)
    for r in records:
        if r.get("arm") in arms and isinstance(r.get("sigma_max"), (int, float)):
            cells[(r.get("line"), r["arm"])].append(float(r["sigma_max"]) > floor)
    out = {}
    for arm in arms:
        mine = {k: v for k, v in cells.items() if k[1] == arm}
        if not mine:
            continue                       # ZERO IS NOT CLEAN (P213): absent, never 0.0%
        fracs = [sum(v) / len(v) for v in mine.values()]
        out[arm] = {
            "rate": 100.0 * sum(fracs) / len(fracs),
            "cells": len(mine),
            "records": sum(len(v) for v in mine.values()),
            "degenerate": sum(1 for v in mine.values() if len(set(v)) == 1),
        }
    return out


# ---- END OF PURE HELPERS (everything below scans the archive and prints) ----------------------

records = []
for rec_path in glob.glob(os.path.join(ROOT, "**", "record.json"), recursive=True):
    norm = rec_path.replace("\\", "/")
    if "/.pull_tmp" in norm or "/frozen" in norm:
        continue                      # frozen/ holds COPIES of search records (would double-count)
    try:
        rec = json.load(open(rec_path, encoding="utf-8"))
    except Exception:
        continue
    m = rec.get("metrics") or {}
    calls = m.get("train_safe_call_count")
    defaults = m.get("train_safe_default_count")
    frac = (float(defaults) / float(calls)) if calls else None
    ps = m.get("popart_scale") or {}
    records.append({
        "path": norm,
        "line": line_of(norm),
        "arm": rec.get("arm"),
        "cid": rec.get("candidate_id"),
        "seed": rec.get("seed"),
        "fitness": m.get("val_fitness"),
        "frac": frac,
        "calls": calls,
        "defaults": defaults,
        "sigma_max": (ps or {}).get("sigma_max"),
    })

print(f"records loaded (frozen/ and .pull_tmp excluded): {len(records)}")
print()

# =====================================================================================
print("=" * 86)
print("A. record_sanity:CRITICAL  -- trigger: a high-fallback record on the CORE line, OR a")
print("   high-fallback record TOPPING its arm on a line whose winner is NOT yet frozen")
print("=" * 86)

breaches = [r for r in records if r["frac"] is not None and r["frac"] >= R115_FLOOR]
print(f"R115 breaches (fallback >= {R115_FLOOR:.0%}): {len(breaches)}")

core_breaches = [r for r in breaches if r["line"] == "core"]
print(f"  ON THE CONFIRMATORY CORE LINE: {len(core_breaches)}   <- trigger clause 1; MUST be 0")
for r in core_breaches:
    print(f"     *** {r['line']}/{r['arm']}/{r['cid']}  fallback={r['frac']:.2%} ***")

# does a breach TOP its arm? compare against the arm's max val_fitness on the same line
best = {}
for r in records:
    if r["arm"] in LLM_ARMS and isinstance(r["fitness"], (int, float)):
        k = (r["line"], r["arm"])
        if k not in best or r["fitness"] > best[k]["fitness"]:
            best[k] = r

frozen_winner = {}
for wpath in glob.glob(os.path.join(ROOT, "frozen*", "*-winner", "record.json")):
    n = wpath.replace("\\", "/")
    parts = n.split("/")
    froot = next((p for p in parts if p.startswith("frozen")), "")
    line = "core" if froot == "frozen" else froot[len("frozen_"):]
    try:
        wr = json.load(open(wpath, encoding="utf-8"))
    except Exception:
        continue
    frozen_winner[(line, wr.get("arm"))] = wr.get("candidate_id")

topping = []
for r in breaches:
    k = (r["line"], r["arm"])
    b = best.get(k)
    if b and b["cid"] == r["cid"]:
        topping.append((r, frozen_winner.get(k)))

print(f"  breaches that TOP their arm: {len(topping)}   <- trigger clause 2")
for r, fw in topping:
    state = "WINNER ALREADY FROZEN" if fw else "*** WINNER NOT YET FROZEN -- TRIGGER FIRES ***"
    print(f"     {r['line']}/{r['arm']}/{r['cid']}  fallback={r['frac']:.2%} "
          f"fitness={r['fitness']:.4f}  frozen_winner={fw!r}  -> {state}")

# =====================================================================================
print()
print("=" * 86)
print("B. reward_scale:WARN -- the surviving protection is that PopArt engagement is ARM-SYMMETRIC")
print("   across the five LLM arms (s.44.4). If it stopped being uniform, H2 could be confounded.")
print("=" * 86)
print("   !! MEASURED AT THE CELL, NOT THE RECORD. A (line, arm) cell is ONE frozen program retrained")
print("     across up to 568 seeds, and 50 of 54 live cells are perfectly degenerate, so counting")
print("     records inflates n by ~the seed count. The record-level count is shown for context only.")
eng = engagement_by_arm(records)
rates = {}
for arm in LLM_ARMS:
    e = eng.get(arm)
    if not e:
        continue
    rates[arm] = e["rate"]
    print(f"   {arm:18s} {e['rate']:5.1f}%   cells={e['cells']:3d}"
          f"  (degenerate {e['degenerate']}/{e['cells']})   records={e['records']:5d} [descriptive]")
if rates:
    spread = max(rates.values()) - min(rates.values())
    ncell = min(eng[a]["cells"] for a in rates)
    pbar = sum(rates.values()) / len(rates) / 100.0
    se_diff = (100.0 * (pbar * (1 - pbar) / max(1, ncell)) ** 0.5) * (2 ** 0.5)
    ratio = spread / se_diff if se_diff else float("inf")
    verdict = ("ARM-SYMMETRIC, H2 protected" if spread <= 15 else
               "NOT ESTABLISHED at this cell count -- WATCH, re-measure as cells accrue"
               if ratio < 2.0 else "*** ASYMMETRIC -- RE-TRIAGE ***")
    print(f"   spread across the five LLM arms = {spread:.1f} pp"
          f"   (SE of a difference at {ncell} cells/arm = {se_diff:.1f} pp; ratio {ratio:.2f})")
    print(f"   => {verdict}")
    print("   !! 'not established' is NOT 'zero': ~11 cells per arm is badly underpowered. The")
    print("     analysis-time obligation stands -- report this beside the H1 family comparison,")
    print("     at the CELL level with its uncertainty, never at the record level.")

# =====================================================================================
print()
print("=" * 86)
print("C. record_sanity:WARN -- benign DSR warm-up: baselines with exactly ONE safe-default in 400k")
print("=" * 86)
tiny = [r for r in records if r["frac"] is not None and 0 < r["frac"] < 1e-4]
names = sorted({(r["arm"] or r["cid"] or "?") for r in tiny})
print(f"   records with a tiny non-zero fallback: {len(tiny)}   distinct names: {names[:8]}")
worst = max((r["frac"] for r in tiny), default=0.0)
print(f"   largest such fraction: {worst:.6%}  (R115 floor is {R115_FLOOR:.0%} -- "
      f"{R115_FLOOR / worst:,.0f}x below it)" if worst else "   none")

# =====================================================================================
print()
print("=" * 86)
print("D. OVERALL FALLBACK HEALTH (context for all of the above)")
print("=" * 86)
clean = sum(1 for r in records if r["frac"] == 0.0)
withfrac = sum(1 for r in records if r["frac"] is not None)
print(f"   records with a fallback fraction recorded : {withfrac}")
print(f"   perfectly clean (0 fallback)              : {clean} ({100.0*clean/withfrac:.1f}%)")
print(f"   breaching the R115 floor                  : {len(breaches)} "
      f"({100.0*len(breaches)/withfrac:.2f}%)")
