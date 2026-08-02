"""S12 — THE AUTHORED REWARD CODE ITSELF: does every archived reward still parse, still pass the
project's OWN sandbox gate, and is the search actually exploring distinct designs?

★ WHY THIS IS THE LAST UNAUDITED LAYER (RUN 14, 2026-08-02).
The dissertation's object of study is the CODE the LLM writes. Four instruments already cover the
record's contract (R1-R9), its files (P1-P4), its numbers (S1-S10) and the text fed to the model
(S11). **Not one of them looks at the reward source.** A record whose `reward_source` no longer
parses, or which would be REFUSED by today's sandbox gate, is a record whose result cannot be
reproduced by re-running the pipeline -- and reproducibility is Priority 5.

★ IT RE-RUNS THE PROJECT'S OWN GATE, NOT A REIMPLEMENTATION.
`src.sandbox.executor.ast_gate` is the real allowlist gate the campaign applies at authoring time
(`ALLOWED_IMPORTS` = numpy only; attribute hops restricted to `_ALLOWED_ATTRS`). Re-running THAT
function over the archive answers a question no reimplementation could: *would every reward we have
already trained on still be admitted today?* A private copy of the rules would only prove that my
copy agrees with itself.

⚠ IT NEVER EXECUTES A REWARD. `ast_gate` parses and inspects; nothing here calls `exec`, `compile`
for execution, or `validate_once`. Auditing untrusted model-authored code must not run it.

THE CHECKS
  C1  parses            -- `ast.parse` succeeds on `reward_source`
  C2  defines a reward  -- a module-level `def reward(...)` exists
  C3  SANDBOX GATE      -- `ast_gate(src)` is True, re-run from the project's own module
  C4  arity             -- the reward signature takes the registered 5 parameters
  C5  distinctness      -- candidates WITHIN one (line, arm, generation) are not byte-identical.
                           The exploration directive fed to the model explicitly asks for designs
                           DISTINCT from the other candidates of that generation, so duplicates mean
                           the K-wide search is narrower than it is reported to be. Reported as a
                           MEASUREMENT, not a failure: a model repeating itself is a finding about
                           the model, not a defect in the archive.

EFFECT-BLIND: reads source code and identifiers only. No fitness, Sharpe, CVaR or arm aggregate is
read, printed or compared.

USAGE
    python docs/analysis/reward_code_audit.py              # whole archive
    python docs/analysis/reward_code_audit.py --selftest
EXIT 0 = every archived reward parses, defines a reward, and passes the live gate; 1 = a defect.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.sandbox.executor import ast_gate  # noqa: E402  -- the REAL gate, deliberately

REGISTERED_PARAMS = ["weights", "returns", "prev_weights", "port_ret", "info"]


def _is_d18_nested(p, root) -> bool:
    """True for a D18 `shutil.move` NESTED duplicate: a unit dir whose name equals its parent's.

    D18 is root-caused in DEFERRED_FIXES_RUN4: `shutil.move` into an EXISTING directory nests, and
    the guard cannot close a TOCTOU race on a `read_root` shared by twelve drivers. Measured on
    2026-08-02: exactly TWO such directories exist archive-wide, both in the SEARCH tier, and both
    hold a record BYTE-IDENTICAL to the outer copy -- so no value diverges. But every `rglob`
    instrument counts them TWICE, so they are skipped here exactly as dot-prefixed `.pull_tmp`
    directories are. Skipped, never deleted: the archive is append-only evidence.
    """
    parts = p.parts
    return any(parts[i] == parts[i - 1] for i in range(1, len(parts) - 1))

def find_reward_def(tree: ast.Module) -> ast.FunctionDef | None:
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "reward":
            return node  # type: ignore[return-value]
    return None


def audit_source(src: str, arm: str = "") -> list[str]:
    """C1-C4 on one reward source. Returns violation messages.

    BASELINES ARE EXEMPT FROM C2/C4, AND FORGETTING THAT WAS MY OWN ERROR (P200).
    The hand-written canon rewards are ANALYTIC allocators implemented in `src/baselines/rewards.py`;
    their records archive a MARKER COMMENT (`# baseline:<name>`) because there is no authored code to
    archive. My first version demanded `def reward(...)` of every record and produced 330 "defects",
    every one a baseline and not one an LLM-authored reward. This is the THIRD time I have
    mis-calibrated a check by forgetting a legitimate exempt category (cf. P193) -- and the sibling
    module's S3 exempts baselines correctly, so the knowledge existed and was simply not applied.
    C1 (parses) and C3 (the sandbox gate) STILL apply to baselines: a marker comment must still be
    valid Python and must still be admitted.
    """
    bad: list[str] = []
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return [f"C1 reward_source does NOT parse: {exc.msg} (line {exc.lineno})"]
    is_baseline = str(arm).startswith("baseline_")
    fn = find_reward_def(tree)
    if fn is None and not is_baseline:
        bad.append("C2 no module-level `def reward(...)` in reward_source")
    elif fn is not None:
        names = [a.arg for a in fn.args.args]
        if len(names) != len(REGISTERED_PARAMS):
            bad.append(f"C4 reward takes {len(names)} parameter(s) {names}, the contract registers "
                       f"{len(REGISTERED_PARAMS)} {REGISTERED_PARAMS}")
    try:
        if not ast_gate(src):
            bad.append("C3 REFUSED by the project's own sandbox ast_gate -- this reward would NOT "
                       "be admitted today, so the run cannot be reproduced by re-running it")
    except Exception as exc:                      # noqa: BLE001 -- a gate crash IS a finding
        bad.append(f"C3 ast_gate raised on this source: {exc!r}")
    return bad


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="outputs/campaign_cluster_run4")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()

    root = Path(args.root)
    if not root.is_dir():
        print(f"root {root} does not exist", file=sys.stderr)
        return 2

    failures: list[str] = []
    n = n_src = 0
    gate_ok = 0
    # C5: (line, arm, generation) -> {source sha -> [candidate ids]}
    gens: dict[tuple, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    for p in sorted(root.rglob("record.json")):
        if any(x.startswith(".") for x in p.parts):
            continue
        if _is_d18_nested(p, root):
            continue
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:                  # noqa: BLE001
            failures.append(f"C0 unreadable record {p}: {exc}")
            continue
        n += 1
        src = rec.get("reward_source") or ""
        if not src.strip():
            continue                              # winner markers / non-authored rows
        n_src += 1
        msgs = audit_source(src, str(rec.get("arm") or ""))
        if not any(m.startswith("C3") for m in msgs):
            gate_ok += 1
        for m in msgs:
            failures.append(f"{m}\n      {p}")
        parts = p.relative_to(root).parts
        line, gen = parts[0], rec.get("generation")
        arm = rec.get("arm")
        if line.startswith("search") and isinstance(gen, int) and arm:
            sha = hashlib.sha256(src.encode("utf-8")).hexdigest()[:16]
            gens[(line, arm, gen)][sha].append(str(rec.get("candidate_id") or p.parent.name))

    dup_groups = {k: v for k, v in gens.items()
                  if any(len(ids) > 1 for ids in v.values())}
    dup_pairs = sum(len(ids) - 1 for v in dup_groups.values() for ids in v.values() if len(ids) > 1)
    total_cands = sum(len(ids) for v in gens.values() for ids in v.values())

    print("=== S12 AUTHORED REWARD CODE AUDIT (C1-C5) ===")
    print(f"  records scanned              : {n:,}")
    print(f"  carrying a reward_source     : {n_src:,}")
    print(f"  PASS the live sandbox gate   : {gate_ok:,} / {n_src:,}")
    print()
    if failures:
        print(f"!! {len(failures)} REWARD-CODE DEFECT(S)")
        for m in failures[:40]:
            print(f"  - {m}")
        if len(failures) > 40:
            print(f"  ... and {len(failures)-40} more")
    else:
        print("C1-C4 CLEAN -- every archived reward parses, defines `def reward(...)` with the")
        print("registered 5-parameter signature, and is STILL ADMITTED by the project's own")
        print("sandbox ast_gate. Every trained result can be reproduced by re-running its source.")

    print()
    print("=== C5 SEARCH DISTINCTNESS (a measurement, not a failure) ===")
    print(f"  search candidates with source : {total_cands:,}")
    print(f"  (line, arm, generation) groups: {len(gens):,}")
    print(f"  groups containing a DUPLICATE : {len(dup_groups):,}")
    print(f"  duplicate candidates          : {dup_pairs:,}"
          f"  ({100.0*dup_pairs/total_cands if total_cands else 0:.2f}% of drawn candidates)")
    if dup_groups:
        print("  the exploration directive asks each candidate to differ from its generation-mates,")
        print("  so a duplicate means the K-wide search was narrower than reported. Examples:")
        for k, v in list(dup_groups.items())[:6]:
            for sha, ids in v.items():
                if len(ids) > 1:
                    print(f"    {k[0]}/{k[1]} g{k[2]}: {len(ids)} identical sources -> {ids}")
                    break
    else:
        print("  no two candidates in any generation share a byte-identical reward source.")
    print()
    print("EFFECT-BLIND: source code and identifiers only; no performance quantity was read.")
    print("NOT EXECUTED: the gate parses and inspects; no archived reward was run.")
    return 1 if failures else 0


def selftest() -> int:
    """Each mutant must be caught; the clean control must pass."""
    good = ("import numpy as np\n"
            "def reward(weights, returns, prev_weights, port_ret, info):\n"
            "    return float(port_ret)\n")
    cases = [
        ("clean reward", good, None),
        ("syntax error", "def reward(:\n", "C1"),
        ("no reward def", "import numpy as np\ndef other(a):\n    return a\n", "C2"),
        ("wrong arity", "def reward(a, b):\n    return 0.0\n", "C4"),
        ("forbidden import", "import os\ndef reward(weights, returns, prev_weights, port_ret, info):\n"
                             "    return 0.0\n", "C3"),
        ("eval escape", "def reward(weights, returns, prev_weights, port_ret, info):\n"
                        "    return eval('1')\n", "C3"),
    ]
    # The baseline exemption must be REAL IN BOTH DIRECTIONS: a marker comment passes for a baseline
    # arm and STILL FAILS for an LLM arm. An exemption that never refuses is a hole, not a rule.
    marker = "# baseline:differential_sharpe\n"
    extra = [
        ("baseline marker exempt from C2", marker, None, "baseline_differential_sharpe"),
        ("same marker NOT exempt for an LLM arm", marker, "C2", "distributional"),
    ]
    passed = failed = 0
    for name, src, want in cases:
        msgs = audit_source(src, "distributional")
        hit = any(m.startswith(want) for m in msgs) if want else not msgs
        if hit:
            passed += 1
            print(f"  ok    {name}")
        else:
            failed += 1
            print(f"  FAIL  {name}: expected {want or 'no violation'}, got {msgs}")
    for name, src, want, arm in extra:
        msgs = audit_source(src, arm)
        hit = any(m.startswith(want) for m in msgs) if want else not msgs
        if hit:
            passed += 1
            print(f"  ok    {name}")
        else:
            failed += 1
            print(f"  FAIL  {name}: expected {want or 'no violation'}, got {msgs}")
    print(f"\nselftest: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
