"""IS `placebo_shuffled` GENUINELY DERANGED? -- v2, against the CORRECT reference.

v1 compared each record's FED values against ITS OWN `tail_stats` and got 0/107 matches. That was my
mis-specification: the fed block describes **the PREVIOUS candidate's** results ("Reflect on the
previous candidate's results ... Feedback from the previous candidate"), not this one's. Comparing a
candidate's feedback to its own outcome is comparing across a generation boundary.

v2 finds the reference empirically, and uses `distributional` as a POSITIVE CONTROL for the method:
that arm is fed the six statistics VERBATIM, so if the linkage logic is right, distributional's fed
values must match SOME earlier candidate's tail_stats EXACTLY and IN ORDER. If that positive control
fails, the linkage is wrong and nothing about placebo_shuffled can be concluded.

Then, for placebo_shuffled: locate the earlier candidate whose tail_stats form the same SET as the fed
values, and check the permutation is a DERANGEMENT (no statistic left in its own slot). That is what
makes it a structure control (confirmatory node N5) rather than a second treatment arm.
"""
from __future__ import annotations

import glob
import json
import os
import re
from collections import Counter, defaultdict

ROOT = "outputs/campaign_cluster_run4"
LABELS = [("CVaR 5%", "cvar_05"), ("CVaR 10%", "cvar_10"), ("CVaR 25%", "cvar_25"),
          ("CVaR 1%", "cvar_01"), ("left-tail mass", "left_tail_mass"),
          ("left-tail skew", "robust_skew")]
KEYS = [k for _, k in LABELS]
NUM = r"([-+]?\d*\.?\d+)"
R = 4                                  # the prompt prints 4 decimals


def load(arm_filter):
    out = []
    for path in glob.glob(os.path.join(ROOT, "search*", "**", "record.json"), recursive=True):
        norm = path.replace("\\", "/")
        if "/.pull_tmp" in norm:
            continue
        try:
            rec = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        if rec.get("arm") not in arm_filter:
            continue
        m = re.match(r"^[a-z0-9_]+-g(\d+)-c(\d+)$", str(rec.get("candidate_id") or ""))
        if not m:
            continue
        line = next((("core" if x == "search" else x[len("search_"):])
                     for x in norm.split("/") if x.startswith("search")), "?")
        ts = (rec.get("metrics") or {}).get("tail_stats") or {}
        prompt = str(rec.get("prompt") or "")
        fed = {}
        for label, key in LABELS:
            mm = re.search(re.escape(label) + r"\s*:\s*" + NUM, prompt)
            if mm:
                fed[key] = round(float(mm.group(1)), R)
        out.append(dict(line=line, arm=rec["arm"], gen=int(m.group(1)), idx=int(m.group(2)),
                        cid=rec["candidate_id"],
                        ts={k: round(float(ts[k]), R) for k in KEYS if k in ts},
                        fed=fed))
    return out


def pool(recs):
    p = defaultdict(list)
    for r in recs:
        p[(r["line"], r["arm"])].append(r)
    return p


def main() -> int:
    recs = load({"distributional", "placebo_shuffled"})
    P = pool(recs)

    for arm, title in (("distributional", "POSITIVE CONTROL"), ("placebo_shuffled", "THE CONTROL ARM")):
        print(f"=== {arm}  ({title}) ===")
        n = matched = ordered = deranged = 0
        fixed = Counter()
        unmatched = []
        for (line, a), rs in P.items():
            if a != arm:
                continue
            earlier = defaultdict(list)
            for r in rs:
                earlier[r["gen"]].append(r)
            for r in rs:
                if r["gen"] < 1 or len(r["fed"]) != 6:
                    continue
                n += 1
                fedvals = sorted(r["fed"].values())
                # search EVERY earlier candidate in the same (line, arm) for a matching value SET
                cand = None
                for g in range(r["gen"] - 1, -1, -1):
                    for e in earlier.get(g, []):
                        if len(e["ts"]) == 6 and sorted(e["ts"].values()) == fedvals:
                            cand = e
                            break
                    if cand:
                        break
                if not cand:
                    unmatched.append(r["cid"])
                    continue
                matched += 1
                if all(abs(r["fed"][k] - cand["ts"][k]) < 1e-9 for k in KEYS):
                    ordered += 1
                fp = [k for k in KEYS if abs(r["fed"][k] - cand["ts"][k]) < 1e-9]
                if not fp:
                    deranged += 1
                for k in fp:
                    fixed[k] += 1
        print(f"  gen>=1 records with a 6-value fed block : {n}")
        print(f"  fed SET traced to an earlier candidate  : {matched} ({100.0*matched/n if n else 0:.1f}%)")
        print(f"  fed values in the SAME ORDER (verbatim) : {ordered}")
        print(f"  FULL DERANGEMENT (no fixed point)       : {deranged}")
        if fixed:
            print(f"  fixed points by statistic               : {dict(fixed)}")
        if unmatched:
            print(f"  untraceable: {len(unmatched)} e.g. {unmatched[:3]}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
