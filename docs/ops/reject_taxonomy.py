"""WHY was each candidate rejected? -- is the gap OUR gate being strict, or the MODEL writing bad code?

Tamer: "why is there even a gap?" The gap between arms (28 vs a projected 24) exists because arms fail
at different rates -- treatments 7-10 %, controls 18-20 %. That difference is only acceptable as DATA
if every rejection was LEGITIMATE. If our AST gate is over-rejecting safe code, the gap is OUR defect,
and fixing it would be a REPAIR (allowed) rather than a design change (a forking path).

So: re-run the REAL gate over every archived rejected source and identify the EXACT construct that
tripped it. `failures.jsonl` preserves `reward_source`, so this is fully reconstructable.

Classification:
  * GENUINELY UNSAFE  -- eval/exec/open/__import__, numpy IO/FFI, dunder access: the gate is right,
    the model wrote something that must never run. The rejection is a real capability signal.
  * ARGUABLY OVER-STRICT -- a construct that is safe in context but caught by a blunt rule. That
    would be OUR defect and the candidates were lost to it.
"""
from __future__ import annotations

import ast
import glob
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.getcwd())
from src.sandbox.executor import (_BANNED_ATTRS, _FORBIDDEN_CALLS,  # noqa: E402
                                  ast_gate)

ARMS = ("distributional", "scalar", "placebo", "scalar_cvar5", "placebo_shuffled")
ROOT = "outputs/campaign_cluster_run4/search"


def diagnose(src: str) -> list[str]:
    """Return the exact constructs the gate objects to."""
    hits: list[str] = []
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return [f"SYNTAX ERROR: {exc.msg}"]
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            hits.append(f"import: {ast.unparse(node)[:60]}")
        elif isinstance(node, ast.Attribute) and node.attr in _BANNED_ATTRS:
            hits.append(f"banned attribute: .{node.attr}")
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            hits.append(f"dunder attribute: .{node.attr}")
        elif isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name) and f.id in _FORBIDDEN_CALLS:
                hits.append(f"forbidden call: {f.id}()")
            elif isinstance(f, ast.Attribute) and f.attr in _FORBIDDEN_CALLS:
                hits.append(f"forbidden call: .{f.attr}()")
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            hits.append(f"{type(node).__name__.lower()} statement")
        elif isinstance(node, ast.Name) and node.id in _FORBIDDEN_CALLS:
            hits.append(f"forbidden name: {node.id}")
    return hits


total = Counter()
per_arm = Counter()
rows = []
for arm in ARMS:
    fp = os.path.join(ROOT, arm, "failures.jsonl")
    if not os.path.isfile(fp):
        continue
    for line in open(fp, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except ValueError:
            continue
        src = r.get("reward_source") or ""
        err = str(r.get("error") or "")
        if "ast_gate" not in err:
            rows.append((arm, r.get("candidate_id"), "NOT-AST: " + err[:70], []))
            continue
        hits = diagnose(src)
        gate = ast_gate(src) if src else None
        per_arm[arm] += 1
        for h in hits:
            total[h.split(":")[0]] += 1
        rows.append((arm, r.get("candidate_id"),
                     f"gate_rerun={gate}", hits))

print(f"{'arm':18s} {'candidate':26s} {'gate re-run':14s} constructs found")
for arm, cid, gate, hits in rows:
    print(f"{arm:18s} {str(cid):26s} {gate:14s} {hits if hits else '(none found!)'}")

print()
print("CONSTRUCT CLASSES ACROSS ALL AST REJECTIONS:")
for k, v in total.most_common():
    print(f"   {v:3d}  {k}")
print()
print("per-arm ast_gate rejections:", dict(per_arm))
