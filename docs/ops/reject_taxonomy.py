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

============================================================================================
CORRECTED 2026-07-31 (RUN 9, record 87). THE FIRST VERSION OF THIS FILE MISATTRIBUTED THE CAUSE.
============================================================================================
The original ``diagnose()`` reported *every* construct it recognised, in ast.walk order, and had two
structural blind spots that made its answer wrong rather than merely incomplete:

  1. it flagged ANY ``ast.Import`` / ``ast.ImportFrom`` node without consulting ``ALLOWED_IMPORTS``
     -- but ``ALLOWED_IMPORTS = {"numpy", "np"}`` and the live gate ACCEPTS ``import numpy as _np``
     (probe it below: ``ast_gate("import numpy as _np\\n" + GOOD)`` is True). An import line that the
     gate is perfectly happy with was reported as the reason for rejection;
  2. it never implemented gate check 2's ``_ALLOWED_ATTRS`` ALLOWLIST at all -- a 338-name frozenset
     that rejects any attribute not on it. That is the check which actually fires most often, so the
     tool was structurally incapable of naming the true cause.

Consequence: record 84 reported the core line's 20 rejections as "12 x import numpy as _np, 7 x dir(),
1 crash" and concluded "19 of 20 violate an UNSTATED rule". The true first-firing checks are
``12 x .resize not in _ALLOWED_ATTRS``, ``7 x dir()``, ``1 x non-AST crash``. Every one of the twelve
is ``np.resize(pw, w.shape)`` -- the PURE module-level function that returns a new array, whose
siblings ``reshape / ravel / flatten / tile / repeat / pad / concatenate / append`` are ALL allowlisted.
``resize`` is neither allowed nor banned: it is simply absent. Those candidates were lost to a
one-name omission in our own allowlist.

Record 84's companion claim -- "the model is never told numpy is in scope" -- is also wrong:
``prompts/system.txt`` (loaded at ``src/llm/prompts.py:135``, and freeze-bound) says verbatim
"numpy only (available as ``np``); no imports beyond numpy". Record 84 grepped only
``prompts/initial_generation.txt``, one of the TWO live prompt files.

This version therefore:
  * mirrors ``ast_gate`` node-for-node and reports the FIRST check that fires (the gate short-circuits,
    so only the first one is causal);
  * runs POSITIVE CONTROLS before printing any verdict -- a known-good reward must be accepted, an
    allowlisted numpy import must be accepted, and one planted violation per check must be named
    correctly. A check that cannot fail verifies nothing;
  * measures the COUNTERFACTUAL: how many candidates were lost SOLELY to ``resize`` being absent;
  * covers every line, not just the core one, and separates AST rejections from the (larger) class of
    candidates whose code simply crashed on a real observation.

Usage:  python docs/ops/reject_taxonomy.py [core|all]     (default: all)
"""
from __future__ import annotations

import ast
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.getcwd())

from src.reward.contract import ALLOWED_IMPORTS  # noqa: E402
from src.sandbox.executor import (_ALLOWED_ATTRS, _BANNED_ATTRS,  # noqa: E402
                                  _FORBIDDEN_CALLS, _FORMAT_FIELD_RE, ast_gate)

#: The one-name omission measured in record 87. Adding it is a REPAIR of our own defect, but it must
#: NOT be applied to the live campaign: it would change which candidates exist mid-search and leave
#: early generations judged by a stricter gate than late ones. Counterfactual only.
COUNTERFACTUAL_ATTRS = frozenset(_ALLOWED_ATTRS | {"resize"})

PATTERNS = {
    "core": "outputs/campaign_cluster_run4/search/*/failures.jsonl",
    "all": "outputs/campaign_cluster_run4/search*/*/failures.jsonl",
}


def _docstring_ids(tree: ast.AST) -> set[int]:
    """Mirror ast_gate's docstring exemption for check 5."""
    return {
        id(n.body[0].value)
        for n in ast.walk(tree)
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and n.body
        and isinstance(n.body[0], ast.Expr)
        and isinstance(n.body[0].value, ast.Constant)
        and isinstance(n.body[0].value.value, str)
    }


def first_failing_check(src: str, allowed_attrs: frozenset[str] = _ALLOWED_ATTRS) -> str | None:
    """Name the FIRST gate check that rejects `src`, or None if the source is accepted.

    Mirrors ``src/sandbox/executor.py::ast_gate`` exactly, in the same ``ast.walk`` order, so the
    answer is the construct the LIVE gate objected to -- not merely a construct the source contains.
    ``allowed_attrs`` is parameterised only so the counterfactual can be measured; the default is the
    real frozenset.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return f"check0-syntax: {exc.msg}"
    docstrings = _docstring_ids(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in ALLOWED_IMPORTS:
                    return f"check1-import-not-allowlisted: import {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            return f"check1-from-import-forbidden: from {node.module} import ..."
        elif isinstance(node, ast.Attribute):
            if not isinstance(node.ctx, ast.Load):
                return f"check2-attribute-store/del: .{node.attr}"
            if node.attr.startswith("__"):
                return f"check2-dunder-attribute: .{node.attr}"
            if node.attr in _BANNED_ATTRS:
                return f"check2-banned-attribute: .{node.attr}"
            if node.attr not in allowed_attrs:
                return f"check2-attribute-NOT-IN-ALLOWLIST: .{node.attr}"
        elif isinstance(node, ast.Name):
            if node.id.startswith("__"):
                return f"check3-dunder-name: {node.id}"
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in _FORBIDDEN_CALLS:
                return f"check4-forbidden-call: {func.id}()"
            if isinstance(func, ast.Attribute) and func.attr in _FORBIDDEN_CALLS:
                return f"check4-forbidden-call: .{func.attr}()"
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) not in docstrings and _FORMAT_FIELD_RE.search(node.value):
                return "check5-format-field-in-string"
    return None


GOOD = (
    "def reward(weights, returns, prev_weights, port_ret, info):\n"
    "    m = float(np.mean(returns))\n"
    "    s = float(np.std(returns)) + 1e-8\n"
    "    return float(port_ret) - 0.5 * s, {'mean': m, 'std': s}, None\n"
)

#: One planted violation per gate check. `expected prefix -> source`.
PLANTS = {
    "check1-import-not-allowlisted": "import os\n" + GOOD,
    "check1-from-import-forbidden": "from numpy import load\n" + GOOD,
    "check2-dunder-attribute": GOOD.replace("float(np.mean(returns))", "float(().__class__ is tuple)"),
    "check2-banned-attribute": GOOD.replace("np.mean(returns)", "np.load('x')"),
    "check2-attribute-NOT-IN-ALLOWLIST": GOOD.replace("np.mean(returns)", "np.resize(returns, 3)"),
    "check4-forbidden-call": GOOD.replace("float(np.mean(returns))", "float(len(dir()))"),
}


def positive_controls() -> bool:
    """Prove the instrument FIRES before trusting any null it reports."""
    ok = True
    if not ast_gate(GOOD) or first_failing_check(GOOD) is not None:
        print(f"  FAIL control: known-good reward rejected ({first_failing_check(GOOD)})")
        ok = False
    else:
        print("  PASS control: known-good reward accepted by BOTH the real gate and the mirror")

    # The claim record 84 rested on: is an ALLOWLISTED numpy import actually a rejection cause?
    probe = "import numpy as _np\n" + GOOD
    if not ast_gate(probe) or first_failing_check(probe) is not None:
        print("  FAIL control: the real gate rejects an allowlisted numpy import (contract changed?)")
        ok = False
    else:
        print("  PASS control: 'import numpy as _np' is ACCEPTED -- it is never a rejection cause")

    for expected, src in PLANTS.items():
        if ast_gate(src):
            print(f"  FAIL control: real gate ACCEPTED a planted {expected}")
            ok = False
            continue
        got = first_failing_check(src)
        if got is None or not got.startswith(expected):
            print(f"  FAIL control: planted {expected} -> mirror said {got!r}")
            ok = False
        else:
            print(f"  PASS control: {expected:38s} -> {got}")

    # The counterfactual must isolate `resize` and must NOT rescue anything genuinely unsafe.
    for name in ("check1-import-not-allowlisted", "check2-banned-attribute", "check4-forbidden-call"):
        if first_failing_check(PLANTS[name], COUNTERFACTUAL_ATTRS) is None:
            print(f"  FAIL control: the counterfactual allowlist RESCUED a planted {name}")
            ok = False
    print("  PASS control: the counterfactual rescues nothing genuinely unsafe")
    return ok


def _normalise(err: str) -> str:
    """Collapse literals/numbers so error strings bucket by KIND, not by instance."""
    return re.sub(r"[0-9]+", "N", re.sub(r"'[^']*'", "X", err))[:95]


def main() -> None:
    scope = (sys.argv[1] if len(sys.argv) > 1 else "all").lower()
    if scope not in PATTERNS:
        sys.exit(f"usage: {sys.argv[0]} [core|all]")

    print("=== POSITIVE CONTROLS (a check that cannot fail verifies nothing) ===")
    if not positive_controls():
        sys.exit("\nCONTROLS FAILED -- the instrument is not trustworthy; no verdict printed.")

    rows: list[tuple[str, str, str, str]] = []
    ast_cause = Counter()
    nonast_cause = Counter()
    per_line = defaultdict(Counter)
    rescued: list[tuple[str, str]] = []
    mirror_disagreements = 0

    for fp in sorted(glob.glob(PATTERNS[scope])):
        parts = fp.replace("\\", "/").split("/")
        line, arm = parts[-3], parts[-2]
        for raw in open(fp, encoding="utf-8"):
            raw = raw.strip()
            if not raw:
                continue
            try:
                r = json.loads(raw)
            except ValueError:
                continue
            src = r.get("reward_source") or ""
            err = str(r.get("error") or "")
            cid = str(r.get("candidate_id"))
            if not src:
                rows.append((line, arm, cid, "NO ARCHIVED SOURCE"))
                continue

            gate_ok = ast_gate(src)
            why = first_failing_check(src)
            if gate_ok != (why is None):
                mirror_disagreements += 1
                print(f"  !! MIRROR DISAGREES WITH THE REAL GATE on {cid} -- investigate before trusting this run")

            if gate_ok:
                cause = f"NON-AST: {_normalise(err)}"
                nonast_cause[_normalise(err)] += 1
                per_line[line]["non-AST code failure"] += 1
            else:
                cause = why or "?"
                ast_cause[cause] += 1
                if first_failing_check(src, COUNTERFACTUAL_ATTRS) is None:
                    per_line[line]["lost to the `resize` omission"] += 1
                    rescued.append((line, cid))
                    cause += "   <-- RESCUED by allowlisting `resize` (OUR defect)"
                else:
                    per_line[line]["AST rejection that stands"] += 1
            rows.append((line, arm, cid, cause))

    n = len(rows)
    print(f"\n=== SCOPE {scope!r}: {n} archived rejections ===")
    print(f"  AST-gate rejections        : {sum(ast_cause.values())}")
    print(f"  non-AST (code crashed /    : {sum(nonast_cause.values())}")
    print("   broke the return contract)")
    print(f"  lost to the `resize` gap   : {len(rescued)}")
    if mirror_disagreements:
        print(f"  !! mirror/gate disagreements: {mirror_disagreements}")

    print("\n-- AST rejections, by the FIRST check that actually fires --")
    for k, v in ast_cause.most_common():
        print(f"  {v:4d}  {k}")

    print("\n-- non-AST rejections, by error kind (these ARE genuine capability signal) --")
    for k, v in nonast_cause.most_common(15):
        print(f"  {v:4d}  {k}")

    print("\n-- per line --")
    for line in sorted(per_line):
        c = per_line[line]
        print(f"  {line:34s} total={sum(c.values()):4d}  " +
              "  ".join(f"{k}={v}" for k, v in sorted(c.items())))

    if rescued:
        print(f"\n-- the {len(rescued)} candidates lost SOLELY to `resize` being absent from a 338-name allowlist --")
        for line, cid in rescued:
            print(f"  {line:34s} {cid}")
        print("\n  np.resize(a, shape) is a PURE function returning a NEW array. reshape/ravel/flatten/")
        print("  tile/repeat/pad/concatenate/append are all allowlisted. This is our omission, not a")
        print("  model failure -- see record 87. NOT fixed in the live gate: changing it mid-search")
        print("  would make early generations face a stricter gate than late ones.")

    print("\n-- per candidate --")
    for line, arm, cid, cause in rows:
        print(f"  {line:30s} {arm:18s} {cid:26s} {cause}")


if __name__ == "__main__":
    main()
