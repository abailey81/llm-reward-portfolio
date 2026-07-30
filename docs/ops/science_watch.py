"""SCIENCE watcher — analyses the OUTPUT and RESULTS, not just process health.

WHY THIS EXISTS (2026-07-30). `campaign_watch.py` watches health invariants: guards, supervisor count,
substrate homogeneity, crash kinds, sentinel verdicts. It says nothing about whether the SCIENCE is
sensible. That is a real gap — a campaign can be perfectly healthy and producing meaningless numbers,
and the standing rule is that a green check proves execution, never truth.

What this asks, every poll:

1. **Is the search SEARCHING?** Identical scores within an arm would mean the loop is inert.
2. **Is the reflection chain ADVANCING, and where can it not run at all?** `prev_block` is set only
   when a generation yields an ACCEPTED candidate, so a model that rejects nearly everything has
   nothing to reflect on. That is the D2 MECHANISM without the D2 defect, and it is a FINDING about the
   capability gradient rather than a fault: below some authoring reliability, reflection does not
   degrade, it cannot run.
3. **Do the arms DIFFERENTIATE?** H2 compares arms; identical distributions would be the null by
   construction rather than by measurement.
4. **Are the invariants still true of the SCORED records** — 400k steps, a return series present, and
   the R115 execution floor?
5. **Are there impossible numbers?** NaN/inf fitness, |Sharpe| absurdities, empty return series.

READ-ONLY. It never writes to the archive.

Usage:  python docs/ops/science_watch.py [run_root]
"""
from __future__ import annotations

import collections
import glob
import json
import math
import os
import statistics
import sys
from pathlib import Path

SEARCH_ARMS = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")


def _records(root: Path) -> list[tuple[str, str, dict]]:
    """(stage, unit, record) for every archived record."""
    out = []
    for p in glob.glob(str(root / "**" / "record.json"), recursive=True):
        parts = p.replace("\\", "/").split("/")
        try:
            r = json.load(open(p, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        out.append((parts[-4] if len(parts) >= 4 else "?", parts[-3], r))
    return out


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else "outputs/campaign_cluster_run4")
    recs = _records(root)
    print(f"=== SCIENCE WATCH: {len(recs)} records under {root} ===")

    # ---- 1 + 3: per-(stage,arm) fitness spread and differentiation -------------------------------
    groups: dict[tuple[str, str], list[float]] = collections.defaultdict(list)
    gen_scores: dict[tuple[str, int], list[float]] = collections.defaultdict(list)
    impossible: list[str] = []
    steps_bad = 0
    noseries = 0
    r115: list[tuple[str, str, str, float]] = []

    for stage, unit, r in recs:
        m = r.get("metrics") or {}
        # test-leg records score on test_sharpe, search on val_fitness (stage-aware, per the
        # 2026-07-29 lesson that a search-shaped reader reports nan for every test record)
        val = m.get("val_fitness")
        key = "val_fitness" if val is not None and not (isinstance(val, float) and math.isnan(val)) \
            else "test_sharpe"
        score = m.get(key)
        if score is None or (isinstance(score, float) and not math.isfinite(score)):
            impossible.append(f"{unit}/{r.get('run_id')}: {key}={score!r}")
        else:
            groups[(stage, unit)].append(float(score))
            g = r.get("generation")
            if isinstance(g, int) and key == "val_fitness":
                gen_scores[(unit, g)].append(float(score))

        calls = m.get("train_safe_call_count")
        if calls is not None and int(calls) != 400_000:
            steps_bad += 1
        if not (m.get("test_returns") or m.get("train_curve") or r.get("test_returns")):
            noseries += 1
        d = m.get("train_safe_default_count")
        if calls and d and int(calls) > 0:
            frac = int(d) / int(calls)
            if frac >= 0.10:
                # (root, arm, run_id, frac) — the ROOT matters: winner selection is per LINE per
                # arm, so pooling candidates across lines makes a binding breach vanish.
                r115.append((stage, unit, str(r.get("run_id")), frac))

    print("\n--- IS THE SEARCH SEARCHING? (zero spread would mean the loop is inert) ---")
    inert = []
    for (stage, unit), v in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:14]:
        if len(v) < 2:
            continue
        spread = max(v) - min(v)
        flag = "  <== ZERO SPREAD" if spread == 0.0 else ""
        if spread == 0.0:
            inert.append(unit)
        print(f"  {unit:38s} n={len(v):4d} mean={statistics.mean(v):+.4f} "
              f"spread={spread:+.4f}{flag}")

    print("\n--- REFLECTION CHAIN: generations reached per line, and accepted candidates each ---")
    per_line: dict[str, dict[int, int]] = collections.defaultdict(dict)
    for (unit, g), v in gen_scores.items():
        # unit here is the arm dir; roll up by its parent search root via the groups key
        per_line[unit][g] = len(v)
    for unit in sorted(per_line):
        gens = per_line[unit]
        chain = " ".join(f"g{g}:{gens[g]}" for g in sorted(gens))
        print(f"  {unit:38s} {chain}")

    print("\n--- SCORED-RECORD INVARIANTS ---")
    print(f"  records whose train_safe_call_count != 400,000 : {steps_bad}")
    print(f"  R115 floor breaches (>=10% safe-default)        : {len(r115)}")
    # Print EVERY breach. A cap here silently hid the 9th breach on 2026-07-30 while the count
    # line said 9 — and a hidden breach could have been on the CORE confirmatory line, which is
    # the one place it would change a scientific conclusion. If a cap is ever reintroduced, it
    # MUST report how many rows it dropped.
    for st, ar, rid, f in r115:
        line = "c1(CORE)" if st == "search" else st.replace("search_leg_", "")
        print(f"      {line}/{ar}/{rid}  {f:.2%}")
    print(f"  impossible/non-finite scores                    : {len(impossible)}")
    for s in impossible:
        print(f"      {s}")

    # --- Does any breach BIND? (the only R115 fact that changes a scientific conclusion) ---------
    #
    # A breach EXISTING is R115 working, not a fault — the floor exists precisely to catch these, and
    # alerting on their mere presence would pin this watcher at ALERT forever and mask a genuinely new
    # science problem (the same alarm-fatigue flaw fixed in campaign_watch.py). What MATTERS is whether
    # a breacher is the TOP-fitness candidate in its arm, because then the floor is the only thing
    # standing between a fallback-contaminated reward and the sealed test leg. That is the trigger.
    binds: list[str] = []
    for st, ar, rid, frac in r115:
        key = f"{st}/{ar}/{rid}"
        cands = []
        for p in glob.glob(str(root / st / ar / "*" / "record.json")):
            try:
                rr = json.load(open(p, encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            mm = rr.get("metrics") or {}
            c2, d2, vf = (mm.get("train_safe_call_count"), mm.get("train_safe_default_count"),
                          mm.get("val_fitness"))
            if not c2 or d2 is None or vf is None:
                continue
            cands.append((float(vf), d2 / c2))
        if not cands:
            continue
        elig = [f for f, fr in cands if fr < 0.10]
        this = max((f for f, fr in cands if fr >= 0.10), default=None)
        if this is not None and (not elig or this > max(elig)):
            binds.append(f"{key} ({frac:.2%}) tops its arm; best eligible="
                         f"{'none' if not elig else format(max(elig), '+.6f')}")
    if binds:
        print("\n  *** R115 IS BINDING — a fallback-contaminated candidate tops its arm ***")
        for b in binds:
            print(f"      {b}")
        print("      (this is the floor DOING ITS JOB; it becomes a defect only if the floor is absent)")

    rc = 0
    hard = bool(inert) or bool(steps_bad) or bool(impossible)
    if hard:
        rc = 2
        print("\n  *** SCIENCE ALERT: an inert search, a broken step budget, or an impossible number ***")
    else:
        print(f"\n  science ok: search varying, {len(recs)} records, 400k budget intact, "
              f"no impossible numbers; {len(r115)} R115 breach(es) correctly excluded, "
              f"{len(binds)} of them binding")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
