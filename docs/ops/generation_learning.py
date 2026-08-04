"""WHERE IN THE LOOP DOES THE WINNER COME FROM? — does the reflection loop actually LEARN?

WHY THIS EXISTS (2026-08-01, record §94.3). Record 71 characterised the fitness DISTRIBUTION (heavy
tail) and the winner's SEPARATION from its runner-up. Nobody had asked the question one step to the
left: **does the ITERATION do anything?** If each generation is an i.i.d. draw from the same quality
distribution, the loop is an expensive way to sample, and H3's registered null ("multi-generation <=
single-shot at matched budget") has a visible search-side signature long before the sealed test.

THE TEST. For a pool that completed all six generations, ask which generation its BEST candidate
first appeared in. Under the null "the loop learns nothing", that is uniform over the six -> 1/6 =
16.7 % each. A LEARNING loop must concentrate its best LATE.

⚠ THE POOLED VERSION IS CONFOUNDED AND IS PRINTED ONLY AS A WARNING. Pooling every pool's
generations together makes the loop look DEAD (best-so-far flat after g2, per-generation median
falling) — but the per-generation samples shrink with depth (279/218/222/189/127/95) because lines
sit at different depths: g0 contains all twelve lines, g5 only those that reached it. A generation
fewer pools reached will ALWAYS look under-represented. **Read section B, not section A.**

EFFECT-BLIND: reads search-lane `val_fitness` only — the SELECTION statistic, reported openly in
record 75.3. NEVER opens a sealed-test outcome for a treatment arm (lane-coordination rule 7).

Usage:  python docs/ops/generation_learning.py [ARCHIVE_ROOT]
"""
from __future__ import annotations

import collections
import glob
import json
import math
import os
import re
import statistics
import sys

LLM_ARMS = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")
CID = re.compile(r"-g(\d+)-c(\d+)$")
N_GENS = 6


# ⚠ THE CONSOLE IS cp1251 AND A NON-ASCII CHARACTER KILLS THE PROCESS. This file died at exit 1
# on a `×` in a print, swallowing its own BOUNDS caveat -- the honesty clause on the number
# `CLAUDE.md` names as the write-up's compute source. My first remedy HUNTED CHARACTERS and missed
# the one on the very next line; the repo already had the right fix, documented at
# `docs/ops/cycle.py:94-100` after the same defect hit live on 2026-07-31. Reconfigure the streams
# instead: this can degrade a CHARACTER but can never lose a MESSAGE.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval — every number in this project arrives with its uncertainty."""
    if n == 0:
        return (0.0, 0.0)
    p, d = k / n, 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((centre - half) / d, (centre + half) / d)


def load(root: str) -> dict[tuple[str, str], dict[int, list[float]]]:
    pools: dict[tuple[str, str], dict[int, list[float]]] = collections.defaultdict(
        lambda: collections.defaultdict(list))
    for p in glob.glob(os.path.join(root, "search*", "*", "*", "record.json")):
        n = p.replace("\\", "/")
        if any(seg.startswith((".pull_tmp", "_quarantined")) for seg in n.split("/")):
            continue
        try:
            r = json.load(open(p, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        arm, cid = r.get("arm"), str(r.get("candidate_id") or "")
        m = CID.search(cid)
        if arm not in LLM_ARMS or not m:
            continue
        v = (r.get("metrics") or {}).get("val_fitness")
        if isinstance(v, (int, float)) and math.isfinite(v):
            pools[(n.split("/")[-4], arm)][int(m.group(1))].append(float(v))
    return pools


def main(argv: list[str]) -> int:
    root = argv[1] if len(argv) > 1 else "outputs/campaign_cluster_run4"
    pools = load(root)
    if not pools:
        print(f"*** NOTHING TO ANALYSE: 0 LLM-arm search records under {root} ***")
        print("    This is NOT a result. Check the archive root.")
        return 2

    # ---- A: the CONFOUNDED pooled view, printed as a warning ------------------------------------
    by_gen: dict[int, list[float]] = collections.defaultdict(list)
    for gens in pools.values():
        for g, v in gens.items():
            by_gen[g].extend(v)
    print("=== A. THE POOLED VIEW — ⚠ CONFOUNDED, DO NOT REPORT THIS ===")
    print(f"  {'gen':>4s} {'n':>5s} {'median':>10s} {'max':>10s} {'best-so-far':>12s}")
    best = 0.0
    for g in sorted(by_gen):
        v = sorted(by_gen[g])
        best = max(best, v[-1])
        print(f"  {g:>4d} {len(v):>5d} {v[len(v)//2]:>10.5f} {v[-1]:>10.5f} {best:>12.5f}")
    print("  ⚠ n FALLS with generation because lines sit at different depths — g0 holds all twelve")
    print("    lines, the last generation only those that reached it. Any apparent decline here is")
    print("    a COMPOSITION artefact. Section B is the unconfounded test.")

    # ---- B: the CLEAN test over pools that completed every generation ---------------------------
    complete = [k for k, g in pools.items() if set(g) >= set(range(N_GENS))]
    print(f"\n=== B. THE CLEAN TEST — {len(complete)} pool(s) with ALL {N_GENS} generations present ===")
    if not complete:
        print("  No pool has completed the full ladder yet — nothing to test. NOT a result.")
        return 0

    where = collections.Counter()
    detail = []
    for k in sorted(complete):
        g = pools[k]
        top = max(x for v in g.values() for x in v)
        first = min(gg for gg, v in g.items() if max(v) == top)
        where[first] += 1
        detail.append((k[0], k[1], first, top))

    n = len(complete)
    null_pct = 100.0 / N_GENS
    print(f"  {'gen':>4s} {'pools whose BEST is here':>26s} {'observed':>9s} {'null':>7s}")
    for gg in range(N_GENS):
        c = where.get(gg, 0)
        print(f"   g{gg} {c:>26d} {100.0*c/n:>8.0f}% {null_pct:>6.1f}%  " + "#" * c)

    late = sum(where.get(g, 0) for g in (N_GENS - 2, N_GENS - 1))
    early = sum(where.get(g, 0) for g in (0, 1))
    lo, hi = wilson(late, n)
    lo2, hi2 = wilson(early, n)
    print(f"\n  BEST IN THE LAST TWO  : {late}/{n} = {100.0*late/n:.0f}%  "
          f"95% CI [{100*lo:.0f}%, {100*hi:.0f}%]   null {2*null_pct:.0f}%")
    print(f"  BEST IN THE FIRST TWO : {early}/{n} = {100.0*early/n:.0f}%  "
          f"95% CI [{100*lo2:.0f}%, {100*hi2:.0f}%]   null {2*null_pct:.0f}%")

    arm_mix = collections.Counter(a for _, a, _, _ in detail)
    print(f"\n  ⚠ ARM COMPOSITION of the complete pools: {dict(arm_mix)}")
    print("    The arms that finish FIRST dominate this sample, so an arm-specific learning effect")
    print("    in a slower arm would be invisible here. State this beside any claim.")

    print("\n  HOW TO READ IT: a LEARNING loop concentrates its best LATE, so `last two` should sit")
    print("  ABOVE the null and its interval should EXCLUDE it. A loop drawing i.i.d. from a fixed")
    print("  distribution places the best UNIFORMLY. This is a search-side PREDICTION for H3's")
    print("  registered null, never a substitute for the sealed test.")

    print("\n  PER-POOL")
    for line, arm, first, top in detail:
        print(f"    {line:28s} {arm:18s} best={top:.5f}  first appeared in g{first}")

    # A median-shift companion: does the TYPICAL candidate improve, or only the max?
    ups = sum(1 for k in complete
              if statistics.median([x for g, v in pools[k].items() if g > 0 for x in v])
              > statistics.median(pools[k][0]))
    print(f"\n  companion — pools whose MEDIAN candidate improved after g0: {ups}/{n} "
          f"({100.0*ups/n:.0f}%). Selection consumes the MAX, so a flat median is expected even")
    print("  when the loop works; it is reported so the two are never conflated.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
