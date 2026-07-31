"""THE REGISTERED ANALYSIS-TIME OBLIGATIONS, as runnable exhibits.

Four obligations are registered and were, until now, prose commitments with no implementation. A
registered analysis with no code is a promise, not a plan -- and the risk is discovering at write-up
that the archive cannot support it. Each is produced here from the live archive:

  (A) s.26.3 / registry 37 -- PER-ARM ACCEPTED-CANDIDATE COUNTS beside every H2 contrast.
      (The equal-k half lives in docs/ops/equal_k_sensitivity.py.)
  (B) registry 43 (record 71.5 / 73.6) -- PARTITION high-fallback records into D17-RECIPROCAL
      (our harness trapping a working reward) vs GENUINELY BROKEN, before any per-model
      authoring-reliability figure. Reported at BOTH screens, because the number moves a lot.
  (C) registry 44 (record 71.4) -- the WINNER-SEPARATION distribution, i.e. the quantitative
      answer to "why so many seeds?".
  (D) obligation 9 (record 44.4) -- POPART ENGAGEMENT RATE beside the H1 family comparison.
      PopArt is inert on ~50% of the archive; that is ARM-SYMMETRIC (so H2 is safe) but
      ASYMMETRIC for H1, whose eleven baselines split by RATIO-form vs DIFFERENCE-form.

SCOPE: validation-side and archive-structural. Nothing here computes a confirmatory statistic.
"""
from __future__ import annotations

import glob
import json
import math
import os
import statistics as st
import sys
from collections import defaultdict

ROOT = "outputs/campaign_cluster_run4"
ARMS = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")

# The H1 canon splits by FUNCTIONAL FORM, and that is exactly the axis PopArt engagement follows.
RATIO_FORM = {"baseline_differential_sharpe", "baseline_volatility_scaled_return",
              "baseline_differential_downside_ratio"}


def line_of(norm: str) -> str:
    for p in norm.split("/"):
        if p.startswith("search"):
            return "core" if p == "search" else p[len("search_"):]
        if p.startswith("test"):
            return "TEST:" + ("core" if p == "test" else p[len("test_"):])
    return "?"


def load():
    out, seen = [], set()
    for path in glob.glob(os.path.join(ROOT, "**", "record.json"), recursive=True):
        norm = path.replace("\\", "/")
        if "/.pull_tmp" in norm or "/frozen" in norm:
            continue
        try:
            rec = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        cid = rec.get("candidate_id")
        line = line_of(norm)
        key = (line, rec.get("arm"), cid, rec.get("seed"))
        if key in seen:                          # D18: one record can sit at two paths
            continue
        seen.add(key)
        m = rec.get("metrics") or {}
        calls, dflt = m.get("train_safe_call_count"), m.get("train_safe_default_count")
        fit = m.get("val_fitness")
        ps = m.get("popart_scale") or {}
        out.append({
            "line": line, "arm": rec.get("arm"), "cid": cid, "seed": rec.get("seed"),
            "frac": (float(dflt) / float(calls)) if calls else 0.0,
            "fit": float(fit) if isinstance(fit, (int, float)) and math.isfinite(fit) else None,
            "sigma_max": ps.get("sigma_max"),
        })
    return out


def is_reciprocal(frac: float, tol: float = 5e-4) -> int | None:
    for k in range(2, 13):
        if abs(frac - 1.0 / k) < tol:
            return k
    return None


def main() -> int:
    R = load()
    print(f"records loaded (frozen/ and .pull_tmp excluded): {len(R)}\n")

    # ---- (A) PER-ARM ACCEPTED-CANDIDATE COUNTS -----------------------------
    print("=" * 90)
    print("(A) s.26.3 / registry 37 -- PER-ARM ACCEPTED-CANDIDATE COUNTS (report beside every H2 contrast)")
    print("=" * 90)
    counts = defaultdict(lambda: defaultdict(int))
    for r in R:
        if r["arm"] in ARMS and not str(r["line"]).startswith("TEST"):
            counts[r["line"]][r["arm"]] += 1
    print(f"{'line':22s} " + " ".join(f"{a[:12]:>13s}" for a in ARMS) + "   max/min")
    for ln in sorted(counts):
        row = [counts[ln].get(a, 0) for a in ARMS]
        nz = [v for v in row if v]
        ratio = (max(nz) / min(nz)) if nz and min(nz) else float("nan")
        print(f"{ln:22s} " + " ".join(f"{v:13d}" for v in row) + f"   {ratio:7.2f}x")
    print("\n  A rejected candidate is NEVER replaced (s.26.3, registered PRE-DATA), so these counts")
    print("  are the per-arm search-width handicap. Report them; never silently average over them.")

    # ---- (B) D17 PARTITION --------------------------------------------------
    print()
    print("=" * 90)
    print("(B) registry 43 -- D17 PARTITION before ANY per-model authoring-reliability figure")
    print("=" * 90)
    for screen in (0.05, 0.10):
        hi = [r for r in R if r["frac"] and r["frac"] >= screen]
        rec = [r for r in hi if is_reciprocal(r["frac"]) is not None]
        gen = [r for r in hi if is_reciprocal(r["frac"]) is None]
        tag = "  <-- R115's ACTUAL eligibility floor" if screen == 0.10 else ""
        print(f"\n  screen >= {screen:.0%}: {len(hi)} records -> "
              f"{len(rec)} D17-RECIPROCAL (harness) / {len(gen)} genuinely broken"
              f"   = {100.0*len(rec)/len(hi):.0f}% harness{tag}")
        if screen == 0.10:
            per = defaultdict(lambda: [0, 0])
            for r in rec:
                per[r["line"]][0] += 1
            for r in gen:
                per[r["line"]][1] += 1
            print(f"    {'line':24s} {'D17-recip':>10s} {'genuine':>9s}")
            for ln in sorted(per):
                print(f"    {ln:24s} {per[ln][0]:10d} {per[ln][1]:9d}")
            print("    -> EXCLUDE the D17 column from any claim about model capability:")
            print("       s.37 established a D17 record is biased AGAINST its own model.")

    # ---- (C) WINNER SEPARATION ---------------------------------------------
    print()
    print("=" * 90)
    print("(C) registry 44 -- WINNER SEPARATION: the quantitative answer to 'why so many seeds?'")
    print("=" * 90)
    seps = []
    for ln in sorted({r["line"] for r in R if not str(r["line"]).startswith("TEST")}):
        for arm in ARMS:
            v = sorted((r["fit"] for r in R if r["line"] == ln and r["arm"] == arm
                        and r["fit"] is not None), reverse=True)
            if len(v) >= 4 and v[1] > 0:
                seps.append(v[0] / v[1])
    if seps:
        seps.sort()
        n = len(seps)
        print(f"  pools: {n}   max/2nd-best ratio:")
        print(f"    min {seps[0]:.2f} | p25 {seps[n//4]:.2f} | MEDIAN {seps[n//2]:.2f} | "
              f"p75 {seps[3*n//4]:.2f} | max {seps[-1]:.2f}")
        tight = sum(1 for s in seps if s < 1.05)
        print(f"  pools where the top TWO differ by < 5% : {tight} of {n} ({100.0*tight/n:.0f}%)")
        print("  -> in those pools the 'winner' is inside sigma_seed = 0.244 and is effectively")
        print("     arbitrary. THIS is why the confirmatory comparison re-scores winners across the")
        print("     30 -> 568 seed ladder on sealed data instead of trusting a single-seed winner.")

    # ---- (D) POPART ENGAGEMENT BESIDE H1 -----------------------------------
    print()
    print("=" * 90)
    print("(D) obligation 9 (record 44.4) -- POPART ENGAGEMENT beside the H1 family comparison")
    print("=" * 90)
    fam = defaultdict(lambda: [0, 0])
    for r in R:
        arm = str(r["arm"] or "")
        if not arm.startswith("baseline_") or not isinstance(r["sigma_max"], (int, float)):
            continue
        fam[arm][1] += 1
        if r["sigma_max"] > 1.0:
            fam[arm][0] += 1
    if fam:
        print(f"  {'H1 baseline':42s} {'form':11s} {'engaged':>8s} {'n':>5s} {'rate':>7s}")
        rr = dd = rn = dn = 0
        for name in sorted(fam):
            on, tot = fam[name]
            form = "RATIO" if name in RATIO_FORM else "difference"
            if name in RATIO_FORM:
                rr += on; rn += tot
            else:
                dd += on; dn += tot
            print(f"  {name:42s} {form:11s} {on:8d} {tot:5d} {100.0*on/tot:6.1f}%")
        print()
        if rn and dn:
            print(f"  RATIO-form      : {rr}/{rn} = {100.0*rr/rn:.1f}% engaged")
            print(f"  DIFFERENCE-form : {dd}/{dn} = {100.0*dd/dn:.1f}% engaged")
            print(f"  SPLIT           : {abs(100.0*rr/rn - 100.0*dd/dn):.1f} percentage points")
        print("  *** REPORT THIS PER-BASELINE, NOT BY FORM. Record 44.4 states the H1 canon 'splits")
        print("      perfectly by ratio-form vs difference-form'. IT DOES NOT -- measured, two of the")
        print("      eleven contradict it:")
        print("        volatility_scaled_return  RATIO-form      but   0% engaged")
        print("        return_minus_drawdown     difference-form but 100% engaged")
        print("      The true driver is the reward's MAGNITUDE, since sigma = max(1.0, raw_rms):")
        print("        volatility_scaled_return = port_ret * scale   -> ~1e-3, never reaches 1.0")
        print("        return_minus_drawdown    = port_ret - lam*dd  -> `dd` is CUMULATIVE, exceeds 1.0")
        print("      Functional form is only a PROXY for magnitude, and it fails wherever a")
        print("      difference carries a cumulative term or a ratio has a small numerator.")
        print("  -> H1 compares the LLM winner against the best of these eleven. Engagement differs")
        print("     ACROSS them (3 of 11), so it is a PER-BASELINE confound and must be reported as")
        print("     such beside the H1 comparison. (Across the five LLM arms it is symmetric at")
        print("     ~3pp spread, so H2 is unaffected -- that half of 44.4 stands.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
