"""INDEPENDENT re-derivation of CONSTRUCT VALIDITY -- v3, against the REAL rendered labels.

Iteration history, kept because it is the point: v1 read `record.json["feedback_block"]` (empty in all
1,031 records -- the fed block lives in `prompt.txt`) and counted generation 0 (which has no feedback by
design); v2 fixed both but matched INTERNAL field names (`cvar_05`, `robust_skew`) that never appear in
the rendered prompt, so it returned 0 for EVERY arm. A check that returns 0 for the arm that must
return 6 cannot detect a leak either -- **its "0 leaks" was worthless, not reassuring.**

The real rendering, read from a live distributional prompt:

    Realized-return tail diagnostics (training period):
      CVaR 5%: -0.0268
      CVaR 10%: -0.0198
      CVaR 25%: -0.0118
      CVaR 1%: -0.0467  (high-variance estimate)
      left-tail mass: +0.0223
      left-tail skew: -0.0457

THE POSITIVE CONTROL IS PART OF THE TEST: `distributional` MUST read 6. If it does not, the
instrument is broken and every other number here is meaningless -- so the script says so and exits
non-zero rather than reporting a reassuring null.
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

ROOT = "outputs/campaign_cluster_run4"
ARMS = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")

# Rendered labels, anchored so "CVaR 1%" cannot match inside "CVaR 10%".
TAIL_PATTERNS = {
    "CVaR 5%": r"CVaR\s+5%",
    "CVaR 10%": r"CVaR\s+10%",
    "CVaR 25%": r"CVaR\s+25%",
    "CVaR 1%": r"CVaR\s+1%",
    "left-tail mass": r"left-tail\s+mass",
    "left-tail skew": r"left-tail\s+skew",
}
EXPECTED = {"distributional": 6, "scalar": 0, "scalar_cvar5": 1,
            "placebo": 0, "placebo_shuffled": 6}

seen = defaultdict(lambda: defaultdict(int))
offspec = defaultdict(list)
which = defaultdict(lambda: defaultdict(int))
n = 0

for rec_path in glob.glob(os.path.join(ROOT, "search*", "**", "record.json"), recursive=True):
    norm = rec_path.replace("\\", "/")
    if "/.pull_tmp" in norm:
        continue
    try:
        rec = json.load(open(rec_path, encoding="utf-8"))
    except Exception:
        continue
    arm = rec.get("arm")
    if arm not in ARMS:
        continue
    gen = rec.get("generation")
    if not isinstance(gen, int) or gen < 1:
        continue
    ppath = os.path.join(os.path.dirname(rec_path), "prompt.txt")
    if not os.path.exists(ppath):
        continue
    text = open(ppath, encoding="utf-8", errors="replace").read()
    n += 1
    present = {lbl for lbl, pat in TAIL_PATTERNS.items() if re.search(pat, text)}
    seen[arm][len(present)] += 1
    for lbl in present:
        which[arm][lbl] += 1
    if len(present) != EXPECTED[arm] and len(offspec[arm]) < 4:
        offspec[arm].append((norm, sorted(present)))

print(f"generation>=1 search-lane LLM prompts examined: {n}")
print()

# ---- POSITIVE CONTROL FIRST -------------------------------------------------
dist_counts = dict(seen["distributional"])
control_ok = bool(dist_counts) and set(dist_counts) == {6}
print(f"POSITIVE CONTROL  distributional must read 6 tail labels -> observed {dist_counts}"
      f"   {'PASS' if control_ok else '*** FAIL -- INSTRUMENT BROKEN ***'}")
if not control_ok:
    print("The leak result below is NOT trustworthy: a check that cannot see the tail in the arm")
    print("that HAS the tail cannot see it leaking into an arm that must not.")
    sys.exit(2)
print()

violations = leaks = 0
for arm in ARMS:
    dist = dict(sorted(seen[arm].items()))
    exp = EXPECTED[arm]
    bad = sum(c for k, c in dist.items() if k != exp)
    violations += bad
    if arm in ("scalar", "placebo"):
        leaks += sum(c for k, c in dist.items() if k > 0)
    print(f"{'OK ' if bad == 0 else 'OFF-SPEC'} {arm:18s} expect {exp} | "
          f"{{n_labels: n_prompts}} = {dist} | off-spec {bad}")
    if which[arm]:
        print(f"        labels seen: {dict(sorted(which[arm].items()))}")
    for p, pres in offspec[arm]:
        print(f"        {p} -> {pres}")

print()
print("=" * 78)
print(f"TAIL LEAKS into a tail-free arm (scalar / placebo): {leaks}   <- MUST be 0")
print(f"total off-spec prompts: {violations}")
print("CONSTRUCT VALIDITY HOLDS (independently re-derived)"
      if leaks == 0 and violations == 0 else "*** REVIEW THE OFF-SPEC ROWS ABOVE ***")
