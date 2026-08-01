#!/usr/bin/env python3
"""Watch for reward programs that reference a name the SANDBOX CANNOT RESOLVE (record §100.31).

WHY THIS EXISTS. ``src/sandbox/executor.py::SAFE_BUILTINS`` is a SECURITY allowlist: it hands the
reward ``np`` plus 31 safe builtins and withholds ``open``/``exec``/``eval``/IO. **It contains no
exception type at all** — no ``Exception``, no ``ValueError``, nothing. Meanwhile the AST gate has no
opinion on ``Try``/``ExceptHandler`` (it screens only ``_FORBIDDEN_CALLS`` and ``_BANNED_ATTRS``).

**So an LLM that wraps risky maths in ``try: … except Exception:`` — the standard defensive pattern —
PASSES the gate and then dies on ``NameError: name 'Exception' is not defined``, on the very line
written to make it robust.** The gate admits code the runtime cannot execute, which makes defensive
code strictly WORSE than no defensive code. `Exception` is not a security risk; it was simply never
added to an allowlist, which is the classic allowlist gap.

WHY IT IS NOT FIXED IN CODE. ``SAFE_BUILTINS`` is **reward-evaluation semantics on the training
path** — the D17 category, never changed while live. Adding the exception hierarchy mid-campaign
would evaluate some candidates under one namespace and some under another, splitting the archive into
**two evaluation instruments** and breaking single-instrument replay (Priority 5). Measured exposure
at 2026-08-01 was ~0.008 of a candidate; trading a permanent reproducibility defect for that is a bad
bargain. **A uniformly-limited-and-disclosed campaign beats a half-and-half one.**

SO THE HAZARD IS MADE VISIBLE INSTEAD. This turns an invisible landmine into a detected one: if a
CONFIRMATORY-line candidate ever manifests the gap, it is reported the same cycle rather than
discovered at analysis time as an unexplained 50 % fallback.

WHAT IT REPORTS
  * every distinct reward program naming a load that cannot resolve (scope-aware: parameters, locals,
    comprehension targets, ``except … as`` bindings and imports are all excluded);
  * whether the reference has **MANIFESTED** (fallback > 0) or is **LATENT** (never fired — Python
    resolves an exception name only when an exception actually occurs);
  * a **CRITICAL** line if any manifestation lands on the core confirmatory line or the sealed test
    lane, which is the only case that would warrant waking anyone.

⚠ **READ THE 50 % SIGNATURE CORRECTLY.** A failure makes ``safe_call`` return state ``None`` and the
env assigns it back, **wiping the accumulated state**. A program whose steady-state branch is broken
therefore ALTERNATES init/steady and reads **exactly ~50 %**, not 100 %. **The fallback fraction is
not a severity scale — 50 % means "the steady-state branch never ran", not "half the rewards were
fine."** See §100.31 and ``docs/ops/probe_reward_failure_pattern.py``.

Read-only. Exit 0 clean / 1 if anything has MANIFESTED on a confirmatory path.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

#: Lanes whose records feed a CONFIRMATORY estimand. A manifestation here is the only CRITICAL case.
CONFIRMATORY_LANES = ("search", "frozen", "test", "search_h3_singleshot", "frozen_h3_singleshot")


def _safe_names() -> set[str]:
    from src.sandbox.executor import SAFE_BUILTINS       # noqa: PLC0415 - deliberate late import
    return set(SAFE_BUILTINS) | {"np", "__builtins__"}


class _Scope(ast.NodeVisitor):
    """Collect NAME LOADS that cannot resolve: not an exposed builtin, not np, not bound locally.

    Deliberately conservative — every binding form we can see (parameters, assignments, walrus,
    comprehension targets, ``except … as``, ``global``, function and lambda names) marks the name
    bound, so a reported name is one we are confident the interpreter would fail to find.
    """

    def __init__(self) -> None:
        self.bound: set[str] = set()
        self.loads: list[str] = []

    def visit_FunctionDef(self, n: ast.FunctionDef) -> None:
        a = n.args
        for arg in (*a.args, *a.kwonlyargs, *(x for x in (a.vararg, a.kwarg) if x), *getattr(a, "posonlyargs", [])):
            self.bound.add(arg.arg)
        self.bound.add(n.name)
        self.generic_visit(n)

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_Lambda(self, n: ast.Lambda) -> None:
        for arg in (*n.args.args, *n.args.kwonlyargs):
            self.bound.add(arg.arg)
        self.generic_visit(n)

    def visit_Name(self, n: ast.Name) -> None:
        if isinstance(n.ctx, ast.Store):
            self.bound.add(n.id)
        else:
            self.loads.append(n.id)
        self.generic_visit(n)

    def visit_ExceptHandler(self, n: ast.ExceptHandler) -> None:
        if n.name:
            self.bound.add(n.name)
        self.generic_visit(n)

    def visit_comprehension(self, n: ast.comprehension) -> None:
        for t in ast.walk(n.target):
            if isinstance(t, ast.Name):
                self.bound.add(t.id)
        self.generic_visit(n)

    def visit_Global(self, n: ast.Global) -> None:
        self.bound.update(n.names)
        self.generic_visit(n)

    visit_Nonlocal = visit_Global  # type: ignore[assignment]


def unresolvable_names(src: str, safe: set[str]) -> set[str]:
    """Names the reward loads that the sandbox namespace cannot supply. Empty set = clean."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return set()                                     # the gate rejects these long before runtime
    local = set(safe)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                local.add((alias.asname or alias.name).split(".")[0])
    scope = _Scope()
    scope.visit(tree)
    return {n for n in scope.loads if n not in local and n not in scope.bound}


def scan(root: Path) -> list[dict]:
    safe = _safe_names()
    seen: set[str] = set()
    out: list[dict] = []
    for dirpath, _dirnames, filenames in os.walk(root):
        if "record.json" not in filenames:
            continue
        rel = os.path.relpath(dirpath, root).replace("\\", "/")
        parts = rel.split("/")
        if any(s.startswith((".pull_tmp", "_quarantine")) for s in parts):
            continue
        try:
            rec = json.loads(Path(dirpath, "record.json").read_text(encoding="utf-8"))
        except Exception:                                # noqa: BLE001
            continue
        src = rec.get("reward_source") or ""
        if "def reward" not in src:
            continue                                     # hand-written baselines carry a marker only
        key = rec.get("reward_source_hash") or src[:64]
        if key in seen:
            continue
        seen.add(key)
        bad = unresolvable_names(src, safe)
        if not bad:
            continue
        metrics = rec.get("metrics") or {}
        d, c = metrics.get("train_safe_default_count"), metrics.get("train_safe_call_count")
        rate = (d / c) if isinstance(d, (int, float)) and isinstance(c, (int, float)) and c else None
        out.append({
            "lane": parts[0], "arm": rec.get("arm"), "run_id": rec.get("run_id"),
            "names": sorted(bad), "fallback_rate": rate,
            "manifested": bool(rate),
            "confirmatory": parts[0] in CONFIRMATORY_LANES,
        })
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Detect rewards naming an unresolvable sandbox name.")
    ap.add_argument("root", nargs="?", default="outputs/campaign_cluster_run4")
    ap.add_argument("--quiet", action="store_true", help="print only the verdict line")
    args = ap.parse_args(argv)

    rows = scan(Path(args.root))
    manifested = [r for r in rows if r["manifested"]]
    critical = [r for r in manifested if r["confirmatory"]]

    if not args.quiet:
        print(f"[sandbox_gap] {len(rows)} distinct reward programs name an unresolvable load "
              f"| MANIFESTED {len(manifested)} | LATENT {len(rows) - len(manifested)}")
        for r in sorted(rows, key=lambda x: -(x["fallback_rate"] or 0)):
            state = f"{r['fallback_rate']*100:7.3f}%" if r["manifested"] else " LATENT "
            mark = "  <<< CONFIRMATORY" if r["confirmatory"] else ""
            print(f"   {state}  {str(r['lane'])[:28]:<29} {str(r['arm'])[:18]:<19} "
                  f"{','.join(r['names'])}{mark}")

    if critical:
        print(f"[sandbox_gap] CRITICAL: {len(critical)} manifestation(s) on a CONFIRMATORY path "
              f"-- a candidate was lost to the allowlist gap, not to its own logic. Record §100.31.")
        return 1
    print(f"[sandbox_gap] OK: no confirmatory-path manifestation "
          f"({len(rows) - len(manifested)} latent, harmless until a try-block raises).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
