"""VERIFY THE IDENTIFICATION PRINCIPLE DIRECTLY: does ONLY the reward vary across arms?

This is the load-bearing scientific claim of the entire design (CLAUDE.md: "ONLY the reward may vary
across arms; any new STATE/REWARD input is creep that breaks identification"). Record 66 verified that
the FED BLOCK differs correctly between arms. **Nothing has ever verified that everything ELSE is the
same** -- and if it is not, H2 is measuring a mixture of the manipulation and whatever else drifted.

Four things must hold across arms within a line:

  1. ENV FINGERPRINT identical -- same environment, same data, same config. A difference here means
     the arms trained in different worlds.
  2. SEED identical for matched candidates -- CRN pairing (the basis of every paired contrast) rests
     on arms facing the same draws.
  3. FOLD identical -- same train/val split.
  4. THE BASE PROMPT identical -- "the same exam for every student". The arms may differ ONLY in the
     feedback block appended at generation >= 1; the environment/contract description that precedes
     it must be byte-identical, or the arms were asked different questions.

Read-only. Validation/structural fields only; no sealed-test quantity is touched.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import re
from collections import defaultdict

ROOT = "outputs/campaign_cluster_run4"
ARMS = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")
# The reflection prompt = base contract text + the FEED BLOCK. Split on the reflection preamble so the
# BASE half can be compared across arms without the (legitimately differing) feedback.
REFLECT = "Reflect on the previous candidate's results"
EXPLORE = "[Exploration directive"


def base_of(prompt: str) -> str:
    """Everything that is NOT the arm-specific feedback: the contract text + the exploration directive."""
    p = prompt
    if REFLECT in p:                      # a reflection prompt: base is whatever follows the fed block
        i = p.find(EXPLORE)
        return p[i:] if i >= 0 else ""
    return p                              # generation 0: the whole thing IS the base prompt


rows = []
for path in glob.glob(os.path.join(ROOT, "search*", "**", "record.json"), recursive=True):
    n = path.replace("\\", "/")
    if "/.pull_tmp" in n:
        continue
    try:
        rec = json.load(open(path, encoding="utf-8"))
    except Exception:
        continue
    if rec.get("arm") not in ARMS:
        continue
    line = next((("core" if x == "search" else x[len("search_"):])
                 for x in n.split("/") if x.startswith("search")), "?")
    m = re.match(r"^[a-z0-9_]+-g(\d+)-c(\d+)$", str(rec.get("candidate_id") or ""))
    if not m:
        continue
    env = rec.get("env_fingerprint") or {}
    rows.append({
        "line": line, "arm": rec["arm"], "gen": int(m.group(1)), "idx": int(m.group(2)),
        "seed": rec.get("seed"), "fold": rec.get("fold"),
        "env": json.dumps(env, sort_keys=True),
        "base": hashlib.sha256(base_of(str(rec.get("prompt") or "")).encode()).hexdigest()[:16],
    })

print(f"records: {len(rows)}\n")

# ---- 1. ENV FINGERPRINT ------------------------------------------------------
by_line_env = defaultdict(set)
for r in rows:
    by_line_env[r["line"]].add(r["env"])
bad_env = {k: v for k, v in by_line_env.items() if len(v) > 1}
print("1. ENV FINGERPRINT identical across arms WITHIN a line")
print(f"   lines with >1 distinct env fingerprint: {len(bad_env)}   <- must be 0")
for k, v in list(bad_env.items())[:3]:
    print(f"     {k}: {len(v)} distinct")
    for e in list(v)[:2]:
        print(f"        {e[:150]}")

allenv = {r["env"] for r in rows}
print(f"   distinct env fingerprints campaign-wide: {len(allenv)}")
for e in list(allenv)[:3]:
    print(f"     {e[:140]}")

# ---- 2 + 3. SEED / FOLD ------------------------------------------------------
print("\n2+3. SEED and FOLD identical for MATCHED candidates (same line, gen, idx)")
seed_bad = fold_bad = 0
matched = defaultdict(dict)
for r in rows:
    matched[(r["line"], r["gen"], r["idx"])][r["arm"]] = r
for key, arms in matched.items():
    if len(arms) < 2:
        continue
    if len({a["seed"] for a in arms.values()}) > 1:
        seed_bad += 1
    if len({a["fold"] for a in arms.values()}) > 1:
        fold_bad += 1
print(f"   matched (line,gen,idx) cells with >=2 arms: {sum(1 for a in matched.values() if len(a)>=2)}")
print(f"   cells where SEED differs across arms: {seed_bad}   <- must be 0 (CRN pairing)")
print(f"   cells where FOLD differs across arms: {fold_bad}   <- must be 0 (same split)")
print(f"   distinct seeds seen in the search lane: {sorted({r['seed'] for r in rows})[:8]}")

# ---- 4. BASE PROMPT ----------------------------------------------------------
print("\n4. BASE PROMPT (contract + exploration directive, feedback EXCLUDED) identical across arms")
for gen in (0, 1, 5):
    sub = [r for r in rows if r["gen"] == gen]
    if not sub:
        continue
    per_line = defaultdict(set)
    for r in sub:
        per_line[r["line"]].add(r["base"])
    multi = {k: len(v) for k, v in per_line.items() if len(v) > 1}
    print(f"   generation {gen}: {len(sub):4d} records | lines whose arms share ONE base: "
          f"{sum(1 for v in per_line.values() if len(v)==1)}/{len(per_line)}"
          + (f"  DIFFERING: {multi}" if multi else ""))
