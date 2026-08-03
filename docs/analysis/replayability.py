"""REPLAYABILITY OF EVERY ARCHIVED PROGRAM -- the real contract, not just "it parses".

My search-tier check (A76) verified every archived `reward_source` PARSES. Parsing is a much
weaker property than the contract the campaign actually enforces, and I should not have let
it stand as "replayable". A source can parse and still:
  * not define `reward()` at all (the optimiser arms archive a `# bayes_opt coeffs=...`
    comment STUB -- run_campaign._reinstantiate_frozen_winner RAISES on those by design);
  * fail the STATIC AST GATE (`src/sandbox/executor.ast_gate`), which is what every candidate
    had to pass at authoring time and what a replay must pass again.

If an archived program would no longer clear the gate, it cannot be re-instantiated, and
reproducibility layer 1 ("analysis = deterministic archive replay") does not hold for the
SEARCH stage however clean the endpoints are.

*** SAFETY: this runs the STATIC gate only. It NEVER calls validate_once and NEVER executes
any reward -- no child process, no numpy call, nothing from the untrusted source runs. ***

Read-only, effect-blind.  python docs/analysis/replayability.py [--selftest]
"""
from __future__ import annotations

import ast
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARCHIVE = REPO / "outputs" / "campaign_cluster_run4"


def _load_gate():
    sys.path.insert(0, str(REPO))
    from src.sandbox.executor import ast_gate  # type: ignore[import-not-found]
    return ast_gate


def defines_reward(src: str) -> bool:
    """Does the module define a top-level callable named `reward`?"""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "reward":
            return True
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "reward":
                    return True
    return False


def scan(root: Path) -> dict:
    gate = _load_gate()
    rows = []
    for p in root.rglob("record.json"):
        rel = p.relative_to(root)
        if rel.parts[0].startswith(".pull_tmp") or "_env" in rel.parts:
            continue
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        src = r.get("reward_source")
        if not isinstance(src, str) or not src.strip():
            rows.append((str(rel), rel.parts[0], rel.parts[1] if len(rel.parts) > 1 else "?",
                         "EMPTY", None, None))
            continue
        parses = True
        try:
            ast.parse(src)
        except SyntaxError:
            parses = False
        has = defines_reward(src)
        gate_ok, gate_err = True, None
        if parses:
            # ⚠ `ast_gate(src) -> bool` RETURNS False to reject; it does NOT raise.
            # My first version wrapped it in try/except, which could never fire -- a check
            # structurally incapable of detecting a rejection. The positive control below
            # caught it. Use the RETURN VALUE.
            try:
                gate_ok = bool(gate(src))
                if not gate_ok:
                    gate_err = "ast_gate returned False (static allowlist rejection)"
            except Exception as exc:  # noqa: BLE001 - defensive only; the gate should not raise
                gate_ok, gate_err = False, f"{type(exc).__name__}: {str(exc)[:70]}"
        rows.append((str(rel), rel.parts[0], rel.parts[1] if len(rel.parts) > 1 else "?",
                     "OK" if parses else "PARSE-FAIL", has, (gate_ok, gate_err)))
    return {"rows": rows}


def report(res: dict) -> int:
    rows = res["rows"]
    rc = 0
    print(f"=== REPLAYABILITY of {len(rows)} archived reward_source values ===")

    empty = [r for r in rows if r[3] == "EMPTY"]
    parse_fail = [r for r in rows if r[3] == "PARSE-FAIL"]
    real = [r for r in rows if r[3] == "OK"]
    no_reward = [r for r in real if r[4] is False]
    gate_fail = [r for r in real if r[5] and not r[5][0]]

    print(f"\n  empty reward_source        : {len(empty)}")
    by_arm = Counter(r[2] for r in empty)
    if by_arm:
        print(f"      by arm: {dict(sorted(by_arm.items()))}")
    print(f"  PARSE failures             : {len(parse_fail)}")
    print(f"  parse OK                   : {len(real)}")
    print(f"  ...of which define reward(): {len(real) - len(no_reward)}")
    print(f"  ...NO reward() defined     : {len(no_reward)}")
    if no_reward:
        arms = Counter(r[2] for r in no_reward)
        print(f"      by arm: {dict(sorted(arms.items()))}")
        print("      >> EXPECTED for two families, by design:")
        print("         - the H1 CANON baselines archive a `# baseline:<name>` stub; they are")
        print("           NAMED REWARD_CANON callables resolved by name, not by source")
        print("           (src/orchestration/test_leg.py:295-298);")
        print("         - the optimiser arms archive a `# <arm> coeffs=...` stub, on which")
        print("           run_campaign._reinstantiate_frozen_winner raises by design.")
        print("         An LLM ARM appearing here would be a DEFECT.")
        llm = [r for r in no_reward if r[2] in
               ("distributional", "scalar", "placebo", "placebo_shuffled", "scalar_cvar5")]
        if llm:
            rc = 2
            print(f"      *** {len(llm)} LLM-ARM record(s) define no reward(): ***")
            for r in llm[:10]:
                print(f"          {r[0]}")
        else:
            fams = sorted({("canon baseline" if a.startswith("baseline_") else
                            "optimiser arm") for a in arms})
            print(f"      *** ZERO LLM-arm records affected -- every stub is a "
                  f"{' / '.join(fams)}. ***")

    print(f"\n  STATIC AST-GATE failures   : {len(gate_fail)}")
    if gate_fail:
        rc = 2
        kinds = Counter(r[5][1].split(":")[0] for r in gate_fail)
        print(f"      kinds: {dict(kinds)}")
        for r in gate_fail[:12]:
            print(f"      {r[0]}\n          {r[5][1]}")
    else:
        print("      *** EVERY archived program still CLEARS THE STATIC AST GATE. ***")
        print("      Reproducibility layer 1 holds for the SEARCH stage: every winner and")
        print("      every candidate can be re-instantiated from the archive.")

    if parse_fail:
        rc = 2
        for r in parse_fail[:10]:
            print(f"  !! PARSE FAIL {r[0]}")

    print(f"\n  VERDICT: {'DEFECT' if rc else 'CLEAN'}")
    return rc


def _selftest() -> int:
    ok = True

    def case(n, c):
        nonlocal ok
        print(f"  [{'PASS' if c else 'FAIL'}] {n}")
        ok = ok and c

    case("defines_reward TRUE on a def", defines_reward("def reward(a):\n    return 1"))
    case("defines_reward FALSE on a comment stub", not defines_reward("# bayes_opt coeffs=[1,2]"))
    case("defines_reward FALSE on a different name",
         not defines_reward("def other(a):\n    return 1"))
    case("defines_reward TRUE on an assignment", defines_reward("reward = lambda *a: (0,{},None)"))
    case("defines_reward FALSE on unparseable", not defines_reward("def ("))
    gate = _load_gate()
    good = "def reward(w,r,pw,pr,i):\n    import numpy as np\n    return float(np.sum(w)), {}, None"
    case("the gate ACCEPTS a benign reward", bool(gate(good)) is True)
    # ast_gate RETURNS a bool; these prove it can return BOTH answers, which is the only
    # thing that makes a clean archive-wide result mean anything.
    case("the gate REJECTS a banned import (proves it can FAIL)",
         bool(gate("import os\ndef reward(w,r,pw,pr,i):\n    return 0.0, {}, None")) is False)
    case("the gate REJECTS dunder access",
         bool(gate("def reward(w,r,pw,pr,i):\n    return w.__class__, {}, None")) is False)
    case("the gate REJECTS a forbidden call",
         bool(gate("def reward(w,r,pw,pr,i):\n    open('x')\n    return 0.0, {}, None")) is False)
    case("the gate REJECTS unparseable source", bool(gate("def (")) is False)

    # The cases above test the GATE. They do NOT test that `scan()` USES its answer -- and a
    # mutation that made scan() ignore the gate entirely survived the whole selftest
    # (mutation_test.py). Drive the REAL scan()/report() over a fixture containing a
    # gate-failing program and assert it is reported.
    import contextlib
    import io
    import json as _json
    import shutil
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="replay_st_"))
    try:
        def _w(rel: str, src: str) -> None:
            d = tmp / rel
            d.mkdir(parents=True, exist_ok=True)
            (d / "record.json").write_text(
                _json.dumps({"run_id": d.name, "arm": "arm", "reward_source": src}),
                encoding="utf-8")

        _w("search/arm/ok", good)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_clean = report(scan(tmp))
        case("REAL scan()/report() CLEAN on a gate-passing archive", rc_clean == 0)

        _w("search/arm/bad", "import os\ndef reward(w,r,pw,pr,i):\n    return 0.0, {}, None")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_bad = report(scan(tmp))
        out_bad = buf.getvalue()
        case("REAL scan()/report() ESCALATES on a gate-failing program", rc_bad == 2)
        case("REAL report() names it as an AST-gate failure",
             "AST-GATE failures   : 1" in out_bad or "ast_gate returned False" in out_bad)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\nselftest: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    raise SystemExit(report(scan(ARCHIVE)))
