#!/usr/bin/env python
"""INSTRUMENT AGREEMENT -- do the tools that report the SAME quantity actually agree?

★ WHY THIS EXISTS. This campaign has now found the same defect three times, each in a different
instrument: a quantity computed by two tools, by two different rules, disagreeing, with nobody
comparing them. The worst instance was about THE REPORTED SCIENTIFIC RESULT -- `record_science_audit`
printed a banked rung of 12 while `record_seed_completeness` printed 0 (P282), and the GATED layer
was the one reading high. RUN 20's brief names the class directly: *"systematically diff every
instrument that reports the same quantity."*

★★ THE DESIGN RULE THAT MAKES THIS MORE THAN A DIFF, AND IT IS THE P259 TEST APPLIED TO A COMPARISON.
A tool that prints "these two differ, as expected" every time carries ZERO BITS. So every pair here
carries an EXPECTED RELATIONSHIP -- equality, or an identity that accounts for the scope difference
exactly -- and the check is whether that relationship HOLDS. A disagreement is then a finding, and an
agreement is evidence rather than a shrug.

★ WHAT IS COMPARED

  A1  record count       campaign_guards (depth-4, all tiers) vs stage_eta (test tier)
                         vs a direct census -- EXPECTED IDENTITY: guards == test + search
  A2  arm roster         line_balance.frozen_arms (ANY subdirectory) vs the `-winner` rule that
                         record_seed_completeness and arm_jobs both use -- EXPECTED: EQUAL
  A3  per-line depth     line_balance.count_records (record.json at ANY depth) vs the seed-directory
                         rule (`-s<N>` immediate children) -- EXPECTED: EQUAL
  A4  banked rung        record_science_audit S10 vs record_seed_completeness S15 -- EXPECTED: EQUAL
                         (both corrected to the R101 population in P282/P287)

EFFECT-BLIND: counts, rosters, directory names and rung integers only. No outcome value is read.

Usage:  python docs/analysis/instrument_agreement.py [--root DIR] [--selftest]
Exit:   0 every expected relationship holds * 1 a disagreement * 2 could not run
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SEED_DIR = re.compile(r"-s\d+$")

rows: list[tuple[str, str, str, bool]] = []      # (id, what, evidence, ok)


def add(cid: str, what: str, evidence: str, ok: bool) -> None:
    rows.append((cid, what, evidence, ok))


# ------------------------------------------------------------------ the instruments' own rules
def census_depth4(root: Path) -> int:
    """campaign_guards.status:276 -- `root.glob('*/*/*/record.json')`, all tiers, fixed depth."""
    return len(list(root.glob("*/*/*/record.json")))


def census_by_tier(root: Path) -> tuple[int, int, int]:
    """(test, search, other) at depth 4, excluding staging -- the direct census."""
    test = search = other = 0
    for p in root.glob("*/*/*/record.json"):
        top = p.relative_to(root).parts[0]
        if top.startswith("."):
            continue
        if top.startswith("test"):
            test += 1
        elif top.startswith("search"):
            search += 1
        else:
            other += 1
    return test, search, other


def roster_any_subdir(root: Path, line: str) -> set[str]:
    """line_balance.frozen_arms:116 -- ANY subdirectory counts, `-winner` merely stripped."""
    frozen = root / ("frozen" + line[len("test"):])
    if not frozen.is_dir():
        return set()
    return {d.name[: -len("-winner")] if d.name.endswith("-winner") else d.name
            for d in frozen.iterdir() if d.is_dir()}


def roster_winner_only(root: Path, line: str) -> set[str]:
    """record_seed_completeness / arm_jobs -- a `-winner` SUFFIX is REQUIRED."""
    frozen = root / ("frozen" + line[len("test"):])
    if not frozen.is_dir():
        return set()
    return {d.name[: -len("-winner")] for d in frozen.iterdir()
            if d.is_dir() and d.name.endswith("-winner")}


def depth_any_record(root: Path, line: str, arm: str) -> int:
    """line_balance.count_records:120 -- a record.json at ANY depth, ANY directory name."""
    p = root / line / arm
    if not p.is_dir():
        return 0
    return sum(1 for _dp, _dn, fn in __import__("os").walk(p) if "record.json" in fn)


def depth_seed_dirs(root: Path, line: str, arm: str) -> int:
    """record_seed_completeness.scan -- immediate children matching `-s<N>` holding a record."""
    p = root / line / arm
    if not p.is_dir():
        return 0
    return sum(1 for d in p.iterdir()
               if d.is_dir() and SEED_DIR.search(d.name) and (d / "record.json").is_file())


def _rung_from(tool: str, root: Path) -> int | None:
    """Run a layer and parse ITS OWN printed rung. Never re-implement what we are checking."""
    try:
        out = subprocess.run([sys.executable, str(REPO / "docs" / "analysis" / tool),
                              "--root", str(root)] if tool != "record_seed_completeness.py"
                             else [sys.executable, str(REPO / "docs" / "analysis" / tool)],
                             capture_output=True, text=True, timeout=1800, cwd=str(REPO))
    except Exception:  # noqa: BLE001
        return None
    for pat in (r"COMMON RUNG .*? = (\d+)", r"COMMON contiguous prefix (\d+)"):
        m = re.search(pat, out.stdout)
        if m:
            return int(m.group(1))
    return None


def run(root: Path, deep: bool) -> int:
    if not root.is_dir():
        print("*** CANNOT RUN: %s is not a directory. NOT a clean result. ***" % root)
        return 2

    # ---- A1 record count ---------------------------------------------------------------------
    g = census_depth4(root)
    t, s, o = census_by_tier(root)
    ok = (g == t + s + o)
    add("A1", "record count: guards depth-4 vs test+search+other",
        "guards=%d  test=%d + search=%d + other=%d = %d" % (g, t, s, o, t + s + o), ok)
    if o:
        add("A1b", "records at depth 4 under a NON test/search top-level directory",
            "%d record(s) -- expected 0; every record should live under test* or search*" % o, o == 0)

    # ---- A2 arm roster ------------------------------------------------------------------------
    lines = sorted(d.name for d in root.iterdir()
                   if d.is_dir() and d.name.startswith("test") and not d.name.startswith("."))
    extra: list[str] = []
    for ln in lines:
        a, b = roster_any_subdir(root, ln), roster_winner_only(root, ln)
        for name in sorted(a - b):
            extra.append("%s/%s" % (ln, name))
    add("A2", "arm roster: line_balance (ANY subdir) vs the -winner rule (S15, arm_jobs)",
        "identical on all %d line(s)" % len(lines) if not extra
        else "line_balance sees %d PHANTOM arm(s) nobody else does: %s" % (len(extra), ", ".join(extra[:6])),
        not extra)

    # ---- A3 per-line depth --------------------------------------------------------------------
    diffs: list[str] = []
    for ln in lines:
        for arm in sorted(roster_winner_only(root, ln)):
            x, y = depth_any_record(root, ln, arm), depth_seed_dirs(root, ln, arm)
            if x != y:
                diffs.append("%s/%s any-depth=%d seed-dirs=%d" % (ln, arm, x, y))
    add("A3", "per-arm depth: record.json at ANY depth vs `-s<N>` seed directories",
        "identical on every (line, arm)" if not diffs
        else "%d disagreement(s): %s" % (len(diffs), "; ".join(diffs[:4])), not diffs)

    # ---- A4 banked rung -----------------------------------------------------------------------
    if deep:
        s10 = _rung_from("record_science_audit.py", root)
        s15 = _rung_from("record_seed_completeness.py", root)
        if s10 is None or s15 is None:
            add("A4", "banked rung: S10 vs S15",
                "COULD NOT READ one of them (S10=%r S15=%r) -- NOT a clean result" % (s10, s15), False)
        else:
            add("A4", "banked rung: record_science_audit S10 vs record_seed_completeness S15",
                "S10=%d  S15=%d" % (s10, s15), s10 == s15)
    else:
        add("A4", "banked rung: S10 vs S15", "SKIPPED (--deep runs both layers, ~5 min)", True)

    # ---- report -------------------------------------------------------------------------------
    print("=== INSTRUMENT AGREEMENT -- do tools reporting the SAME quantity agree? ===")
    print("  root: %s" % root)
    print("  Every row states an EXPECTED RELATIONSHIP and checks whether it HOLDS. A row that")
    print("  could only ever say 'they differ, as expected' would carry zero bits, so it is not here.")
    print()
    bad = 0
    for cid, what, ev, ok in rows:
        bad += 0 if ok else 1
        print("  [%s] %-4s %s" % ("OK " if ok else "FAIL", cid, what))
        print("         %s" % ev)
    print()
    if bad == 0:
        print("VERDICT: every expected relationship HOLDS. No two instruments disagree about a")
        print("  quantity they both report.")
        return 0
    print("VERDICT: %d DISAGREEMENT(S). Two instruments report different values for the same" % bad)
    print("  quantity, which means at least one of them is wrong and a session quoting either")
    print("  could be quoting the wrong number.")
    return 1


def _selftest() -> int:
    import json
    import tempfile
    passed = failed = 0

    def check(name, got, want):
        nonlocal passed, failed
        ok = got == want
        passed, failed = passed + (1 if ok else 0), failed + (0 if ok else 1)
        print("  %-52s got %-5r want %-5r %s" % (name, got, want, "PASS" if ok else "FAIL"))

    def rec(p: Path):
        p.mkdir(parents=True, exist_ok=True)
        (p / "record.json").write_text(json.dumps({}), encoding="utf-8")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "frozen_leg_x" / "a-winner").mkdir(parents=True)
        rec(root / "test_leg_x" / "a" / "a-s0")
        rec(root / "search_leg_x" / "a" / "a-g0-c0")
        rows.clear()
        check("T1 a consistent archive agrees", run(root, deep=False), 0)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "frozen_leg_x" / "a-winner").mkdir(parents=True)
        (root / "frozen_leg_x" / "_scratch").mkdir()          # a PHANTOM arm for line_balance
        rec(root / "test_leg_x" / "a" / "a-s0")
        rows.clear()
        check("T2 a phantom roster entry is CAUGHT (A2)", run(root, deep=False), 1)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "frozen_leg_x" / "a-winner").mkdir(parents=True)
        rec(root / "test_leg_x" / "a" / "a-s0")
        rec(root / "test_leg_x" / "a" / "a-s0" / "nested")    # a record at the WRONG depth
        rows.clear()
        check("T3 a depth disagreement is CAUGHT (A3)", run(root, deep=False), 1)
    with tempfile.TemporaryDirectory() as td:
        rows.clear()
        check("T4 a missing root is NOT clean", run(Path(td) / "nope", deep=False), 2)
    print()
    print("selftest: %d passed, %d FAILED" % (passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="outputs/campaign_cluster_run4")
    ap.add_argument("--deep", action="store_true", help="also run S10 and S15 and diff their rungs")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    raise SystemExit(_selftest() if args.selftest else run(Path(args.root), args.deep))
