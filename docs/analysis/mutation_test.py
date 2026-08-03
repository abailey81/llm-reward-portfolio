"""MUTATION-TEST THIS LANE'S OWN SELFTESTS. Coord's M278 escalation, applied here.

Coord mutation-tested their board's selftest and found it could not detect a BROKEN
VERIFIER -- it asserted only that both answers appeared SOMEWHERE across the board, an
aggregate a single flipped verifier survives untouched.

I have 133 falsification cases across 11 instruments and have never proven that ANY of them
can detect the instrument itself silently breaking. A selftest that passes against a mutated
instrument is decoration.

METHOD: copy each instrument to a temp file, apply a targeted mutation that DISABLES one real
check, import the mutant, run ITS OWN `_selftest()`, and assert the selftest FAILS.
    mutation KILLED   = the selftest caught it              -> the case has teeth
    mutation SURVIVED = the selftest passed on broken code  -> A HOLE, and the finding

Non-destructive: the real files are never modified; every mutant lives in a temp dir.

Read-only.  python docs/analysis/mutation_test.py
"""
from __future__ import annotations

import importlib.util
import io
import shutil
import sys
import tempfile
import contextlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

#: (instrument, description, original snippet, mutated snippet)
#: Each mutation disables ONE genuine check -- the shape of "this silently stopped working".
MUTATIONS: list[tuple[str, str, str, str]] = [
    ("record_validator", "R2 hash-vs-source check disabled",
     "        if actual != h:", "        if False:"),
    ("record_validator", "R8 endpoint replay tolerance made infinite",
     'if abs(sh - float(mt["test_sharpe"])) > 1e-9:',
     'if abs(sh - float(mt["test_sharpe"])) > 1e99:'),
    ("record_validator", "R6 counter sanity disabled",
     "        if dflt > calls:", "        if False:"),
    ("output_integrity", "within-unit duplicate detection disabled",
     "if len(v) > 1}", "if len(v) > 99999}"),
    ("env_census", "determinism-relevance filter always False",
     "    return any(k in p for k in DETERMINISM_KEYS)", "    return False"),
    ("search_integrity", "cross-arm collision detection disabled",
     "cross = {d: a for d, a in by_digest.items() if len(a) > 1}",
     "cross = {d: a for d, a in by_digest.items() if len(a) > 99999}"),
    ("substrate_watch", "C1 non-reference-CPU check disabled",
     "        if cpu != REFERENCE_MODEL:", "        if False:"),
    ("replayability", "AST gate result ignored (always accepts)",
     "                gate_ok = bool(gate(src))", "                gate_ok = True"),
    ("winner_chain", "L2 marker/candidate hash check disabled",
     "                if ch != mh:", "                if False:"),
    ("winner_chain", "L4 self-consistency check disabled",
     "                if canonical_hash(msrc) != mh:", "                if False:"),
    ("deep_record_audit", "PASS 1 schema-drift detection disabled",
     "            if f[\"present\"] != d[\"n\"]:", "            if False:"),
]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)          # type: ignore[arg-type]
    sys.modules[name] = mod
    spec.loader.exec_module(mod)                          # type: ignore[union-attr]
    return mod


def run_one(inst: str, desc: str, old: str, new: str, tmp: Path) -> tuple[bool, str]:
    src_path = HERE / f"{inst}.py"
    text = src_path.read_text(encoding="utf-8")
    if old not in text:
        return False, "MUTATION TARGET NOT FOUND (the snippet has moved -- fix the harness)"
    mutant_dir = tmp / f"{inst}_{abs(hash(desc)) % 100000}"
    mutant_dir.mkdir(parents=True, exist_ok=True)
    # copy the whole analysis dir so intra-package imports still resolve
    for p in HERE.glob("*.py"):
        shutil.copyfile(p, mutant_dir / p.name)
    (mutant_dir / f"{inst}.py").write_text(text.replace(old, new, 1), encoding="utf-8")

    saved = list(sys.path)
    sys.path.insert(0, str(mutant_dir))
    for k in [k for k in sys.modules if k.startswith("mut_")]:
        del sys.modules[k]
    try:
        mod = _load(mutant_dir / f"{inst}.py", f"mut_{inst}_{abs(hash(desc)) % 100000}")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            rc = mod._selftest()
        out = buf.getvalue()
        killed = (rc != 0) or ("[FAIL]" in out)
        detail = ""
        if killed:
            fails = [ln.strip() for ln in out.splitlines() if "[FAIL]" in ln]
            detail = fails[0][:88] if fails else f"rc={rc}"
        return killed, detail
    except Exception as exc:  # a mutant that crashes the selftest is also KILLED
        return True, f"selftest raised {type(exc).__name__}"
    finally:
        sys.path[:] = saved


def main() -> int:
    print("=== MUTATION TEST OF THIS LANE'S OWN SELFTESTS ===")
    print("    a selftest that PASSES against a deliberately broken instrument is")
    print("    decoration. Each row disables ONE real check; the selftest MUST fail.\n")
    tmp = Path(tempfile.mkdtemp(prefix="mut_"))
    survived = []
    try:
        print(f"  {'instrument':<20}{'mutation':<48}verdict")
        print("  " + "-" * 94)
        for inst, desc, old, new in MUTATIONS:
            killed, detail = run_one(inst, desc, old, new, tmp)
            mark = "KILLED" if killed else "*** SURVIVED ***"
            print(f"  {inst:<20}{desc:<48}{mark}")
            if detail:
                print(f"  {'':<20}    caught by: {detail}")
            if not killed:
                survived.append((inst, desc, detail))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n=== {len(MUTATIONS) - len(survived)}/{len(MUTATIONS)} mutants KILLED ===")
    if survived:
        print("  *** SURVIVING MUTANTS -- these selftests cannot detect their own instrument")
        print("      silently breaking. Each is a hole to close: ***")
        for inst, desc, detail in survived:
            print(f"      {inst}: {desc}   {detail}")
    else:
        print("  Every mutation was caught by the instrument's own selftest.")
    return 2 if survived else 0


if __name__ == "__main__":
    raise SystemExit(main())
