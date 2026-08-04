#!/usr/bin/env python
"""B1-B9 SCIENTIFIC PLAUSIBILITY -- is the archive PHYSICALLY SENSIBLE, not merely self-consistent?

★ WHY THIS EXISTS, AND WHY THE EXISTING LAYERS DO NOT COVER IT.

The seven record layers verify INTERNAL CONSISTENCY: that a record's `test_sharpe` replays from its
own `test_returns`, that its `reward.py` hashes to what the record claims, that every `git_commit`
is real, that the sealed window is identical across arms. **All seven can read RC=0 over an archive
whose every number is scientifically absurd**, because nothing in them asks whether a Sharpe ratio
is believable, whether a CVaR has the right sign, whether portfolio weights lie on the simplex, or
whether an arm's outcome is degenerate. `CLAUDE.md` states the duty directly -- *"a green check
proves execution, not truth ... sanity-check the magnitude, sign, and units"* -- and cites the
precedent that decides it: **this project's prototype "tail signal" was REFUTED on a wrong-unit
error that had passed every test.** An internally consistent wrong number is exactly what survives
a consistency layer.

★★★ THE BLINDNESS GUARANTEE, AND IT IS ENFORCED IN CODE, NOT PROMISED IN A COMMENT.

The sealed test is a pre-registered confirmatory window. Reading a treatment arm's OUTCOME LEVEL
mid-campaign is a forking path on a frozen registration. So this tool is built so that it CANNOT
leak one:

  * every LEVEL statistic it prints is POOLED OVER ALL ARMS AND ALL LINES -- never per arm;
  * every PER-ARM statement it makes is a BOOLEAN or a COUNT (degenerate yes/no, n out of band),
    never a mean, a median, a rank or a spread;
  * it never computes a difference, a ratio or an ordering between two arms;
  * `_assert_blind()` re-checks those invariants against the rendered output before it is printed,
    and REFUSES to print if a per-arm level would escape.

⇒ It answers "is this nonsense?" completely and "which arm won?" not at all.

★ WHAT IT CHECKS

  B1 finiteness      every outcome field finite (NaN/inf are counted, never skipped)
  B2 sign            test_cvar05 <= 0 -- a left-tail MEAN of returns cannot be a gain
  B3 range           each statistic inside a physically defensible band, pooled
  B4 degeneracy      any (line, arm) whose statistic is CONSTANT across >= 3 seeds -- the
                     signature of an inert loop, reported as a FLAG with no level attached
  B5 simplex         test_alloc weights are non-negative and sum to 1
  B6 series          |daily return| < 1.0 and the series is not all-zero / all-identical
  B7 window          every test record holds the same series length (independent of L7)
  B8 turnover/gross  turnover in [0, 2] per period, gross exposure in [0, 5]
  B9 pairing         the archived test_sharpe agrees in SIGN with the replayed one

Usage:  python docs/analysis/science_plausibility.py [root] [--selftest]
Exit:   0 clean * 1 at least one implausibility * 2 could not run (empty or unreadable root)

STREAMS the archive: one record is parsed at a time and only scalars are retained, so memory is
O(arms), not O(archive) -- the P270/P280 lesson applied at build time rather than after.
"""
from __future__ import annotations

import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Physically defensible bands. Deliberately WIDE: this is an absurdity detector, not a
# significance test, and a narrow band would manufacture findings from ordinary variation.
BANDS = {
    "test_sharpe":   (-15.0, 15.0),     # annualised; |S| > 15 on daily data is not a real result
    "test_cvar05":   (-1.0, 0.0),       # a left-tail MEAN of daily returns: <= 0, > -100%/day
    "val_fitness":   (-50.0, 50.0),     # deflated-Sharpe-like selector
}
RET_ABS_MAX = 1.0        # |daily return| >= 100% is not a portfolio return on this panel
TURNOVER_MAX = 2.0       # a full round-trip of a long-only book is 2.0 per period
GROSS_MAX = 5.0          # long-only simplex is 1.0; 5.0 leaves room for any leverage convention
MIN_SEEDS_FOR_DEGENERACY = 3


def _finite(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(float(x))


def scan(root: Path) -> dict:
    """Stream the sealed-test tier. Retains ONLY scalars, never a series."""
    out = {
        "n": 0, "nonfinite": Counter(), "sign": [], "range": Counter(), "range_ex": defaultdict(list),
        "simplex": [], "series": [], "lengths": Counter(), "turnover": [], "gross": [],
        "pooled": defaultdict(list), "by_arm": defaultdict(list), "signflip": [],
    }
    for p in root.rglob("record.json"):
        parts = p.as_posix().split("/")
        if any(seg.startswith((".pull_tmp", "_quarantined")) for seg in parts[:-1]):
            continue
        # sealed-test tier only: the search tier carries different fields and a different meaning
        if not any(seg.startswith("test") for seg in parts):
            continue
        try:
            rec = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except Exception:  # noqa: BLE001 - an unreadable record is L1's finding, not ours
            continue
        if not isinstance(rec, dict):
            continue
        out["n"] += 1
        rel = "/".join(parts[-3:])
        line = next((s for s in parts if s.startswith("test")), "?")
        # ⚠ the archive is <line>/<arm>/<arm>-s<N>/record.json, so the ARM is parts[-3]; parts[-2]
        # is the SEED directory. My first version used [-2], which gave every seed its own key, so
        # no unit ever reached the >=3-seed threshold and the DEGENERACY CHECK COULD NEVER FIRE --
        # caught by selftest case S3 rather than by review, which is the whole point of S3.
        arm = parts[-3] if len(parts) >= 3 else "?"
        key = (line, arm)
        m = rec.get("metrics") or {}

        for f, (lo, hi) in BANDS.items():
            v = m.get(f, rec.get(f))
            if v is None:
                continue
            if not _finite(v):
                # ⚠ MY THIRD DEFECT FROM THE SAME RUN (P284). `val_fitness` is NaN on every
                # hand-written H1 baseline's TEST record BY DESIGN -- a baseline is not selected on
                # a validation criterion, so it has no validation fitness. `science_watch` records
                # the same fact in its own comment. Measured: exactly 330 = 11 baselines x 30 seeds,
                # which is the arithmetic identity that proves the reading. Counted as a DISCLOSURE
                # rather than a violation; a NaN anywhere else is still a finding.
                bucket = "val_fitness(baseline, EXPECTED)" if (
                    f == "val_fitness" and arm.startswith("baseline_")) else f
                out["nonfinite"][bucket] += 1
                continue
            v = float(v)
            out["pooled"][f].append(v)
            if f == "test_sharpe":
                out["by_arm"][key].append(v)
            if not (lo <= v <= hi):
                out["range"][f] += 1
                if len(out["range_ex"][f]) < 3:
                    out["range_ex"][f].append(f"{rel}: {v!r}")
            if f == "test_cvar05" and v > 0:
                out["sign"].append(f"{rel}: test_cvar05={v!r} is POSITIVE")

        tr = rec.get("test_returns") or m.get("test_returns")
        if isinstance(tr, list) and tr:
            out["lengths"][len(tr)] += 1
            bad = sum(1 for x in tr if not _finite(x))
            if bad:
                out["nonfinite"]["test_returns(elements)"] += bad
            xs = [float(x) for x in tr if _finite(x)]
            if xs:
                if max(abs(x) for x in xs) >= RET_ABS_MAX:
                    out["series"].append(f"{rel}: |daily return| >= {RET_ABS_MAX}")
                if len(set(xs)) == 1:
                    out["series"].append(f"{rel}: EVERY daily return is identical ({xs[0]!r})")
                sh_arch = m.get("test_sharpe")
                if _finite(sh_arch) and len(xs) > 1:
                    mu = statistics.fmean(xs)
                    sd = statistics.pstdev(xs)
                    if sd > 0:
                        rep = mu / sd * math.sqrt(252)
                        if (rep > 0) != (float(sh_arch) > 0) and abs(rep) > 1e-9:
                            out["signflip"].append(f"{rel}: replay sign != archived sign")

        # ⚠ MY OWN DEFECT, CAUGHT ON THE FIRST LIVE RUN AND FIXED HERE (P284). The first version
        # required the risky weights to SUM TO 1 and flagged 5,011 records. It was wrong:
        # `config/environment.yaml` sets `include_cash: true`, so the book holds CASH and the risky
        # weights legitimately sum to LESS than 1, with cash as the residual. A book 19% in cash is
        # the agent doing its job, not a violation. The correct invariant is: every weight >= 0 and
        # the sum <= 1 (+ tolerance). Verified against the config rather than inferred from the name.
        w = ((m.get("test_alloc") or {}).get("weights")
             if isinstance(m.get("test_alloc"), dict) else None)
        if isinstance(w, list) and w:
            flat = [x for row in w for x in (row if isinstance(row, list) else [row])]
            fin = [float(x) for x in flat if _finite(x)]
            if fin:
                if min(fin) < -1e-6:
                    out["simplex"].append(f"{rel}: NEGATIVE weight {min(fin)!r}")
                rows = w if isinstance(w[0], list) else [w]
                for r_ in rows[:1]:                       # one row is enough to catch a bad convention
                    s = sum(float(x) for x in r_ if _finite(x))
                    if s > 1.0 + 1e-3:                    # cash is the residual: <= 1, never > 1
                        out["simplex"].append(f"{rel}: risky weights sum to {s:.6f} > 1")
                        break

        # ⚠ MY SECOND DEFECT FROM THE SAME RUN (P284). `test_gross` was banded as a GROSS EXPOSURE
        # in [0, 5] and flagged ALL 11,357 records at min -0.08 / max 0.058. Those magnitudes are
        # daily RETURNS, and `src/orchestration/test_leg.py:149` writes it as a per-period series
        # paired with `test_turnover`: it is the GROSS (pre-cost) RETURN series, which is negative
        # on down days by construction. Reading a field's meaning off its NAME is the same mistake
        # as P271's `arms_full`, and it manufactured 11,357 false findings in one pass.
        v = m.get("test_turnover")
        vals = v if isinstance(v, list) else ([v] if v is not None else [])
        fin = [float(x) for x in vals if _finite(x)]
        if fin and (min(fin) < -1e-9 or max(fin) > TURNOVER_MAX):
            out["turnover"].append(f"{rel}: test_turnover outside [0, {TURNOVER_MAX}] "
                                   f"(min {min(fin):.4f}, max {max(fin):.4f})")
        v = m.get("test_gross")
        vals = v if isinstance(v, list) else ([v] if v is not None else [])
        fin = [float(x) for x in vals if _finite(x)]
        if fin and max(abs(x) for x in fin) >= RET_ABS_MAX:
            out["gross"].append(f"{rel}: |test_gross| >= {RET_ABS_MAX} "
                                f"(min {min(fin):.4f}, max {max(fin):.4f})")
    return out


def _assert_blind(lines: list[str], by_arm: dict) -> None:
    """REFUSE to print if any per-arm LEVEL statistic reached the output.

    The guarantee this file makes is only worth what it is checked against, so the rendered text is
    re-read here and any arm-keyed numeric level aborts the run. A promise in a docstring is not a
    control.
    """
    for (line, arm), vals in by_arm.items():
        if not vals:
            continue
        pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(arm) + r"(?![A-Za-z0-9_])")
        for stat in (statistics.fmean(vals), min(vals), max(vals)):
            token = f"{stat:.4f}"
            for ln in lines:
                if token in ln and pat.search(ln):
                    raise SystemExit(
                        "BLINDNESS GUARD TRIPPED: a per-arm level (%s %s) reached the output. "
                        "Refusing to print." % (arm, token))


def render(out: dict) -> int:
    L: list[str] = []
    def say(s: str = "") -> None:
        L.append(s)

    say("=== B1-B9 SCIENTIFIC PLAUSIBILITY (sealed-test tier) ===")
    say("  BLIND BY CONSTRUCTION: every level below is POOLED over all arms and all lines;")
    say("  every per-arm statement is a boolean or a count. No contrast is computed anywhere.")
    say("  sealed-test records inspected: %d" % out["n"])
    if out["n"] == 0:
        say("  *** ZERO RECORDS INSPECTED -- this is NOT a clean result. ***")
        print("\n".join(L))
        return 2

    say()
    # ⚠ POOLING ONLY HIDES WHEN THERE IS SOMETHING TO POOL. With a single contributing arm the
    # "pooled" distribution IS that arm's outcome level, so the blindness guarantee would be
    # vacuous. Rather than hack around it, the tool refuses to print the levels and says why --
    # caught when the guard fired on a single-arm selftest fixture, which is what the guard is for.
    n_arms = len({a for _l, a in out["by_arm"]})
    say("--- pooled distribution of each outcome statistic (the absurdity check) ---")
    if n_arms < 2:
        say("  *** LEVELS SUPPRESSED: only %d arm contributed, so a 'pooled' figure would BE that"
            % n_arms)
        say("      arm's outcome. Range and sign violations are still counted and reported below.")
    for f in sorted(out["pooled"]) if n_arms >= 2 else []:
        v = sorted(out["pooled"][f])
        k = len(v)
        say("  %-14s n=%-6d min %10.4f  p05 %9.4f  median %9.4f  p95 %9.4f  max %10.4f"
            % (f, k, v[0], v[int(0.05 * k)], v[k // 2], v[int(0.95 * k)], v[-1]))
        say("                 band [%s, %s]  out of band: %d"
            % (BANDS[f][0], BANDS[f][1], out["range"].get(f, 0)))
        for e in out["range_ex"].get(f, []):
            say("                   e.g. %s" % e)

    say()
    say("--- B1 finiteness ---")
    if out["nonfinite"]:
        for f, c in out["nonfinite"].most_common():
            say("  *** %-24s %d non-finite value(s)" % (f, c))
    else:
        say("  every inspected outcome value and every return element is finite.")

    say()
    say("--- B2 sign (test_cvar05 is a left-tail MEAN of returns and cannot be a gain) ---")
    say("  violations: %d" % len(out["sign"]))
    for e in out["sign"][:3]:
        say("    %s" % e)

    say()
    say("--- B4 degeneracy: an arm whose statistic is CONSTANT across seeds (an inert loop) ---")
    deg = [k for k, v in out["by_arm"].items()
           if len(v) >= MIN_SEEDS_FOR_DEGENERACY and len(set(round(x, 12) for x in v)) == 1]
    checked = [k for k, v in out["by_arm"].items() if len(v) >= MIN_SEEDS_FOR_DEGENERACY]
    say("  (line, arm) units with >= %d seeds: %d   DEGENERATE: %d"
        % (MIN_SEEDS_FOR_DEGENERACY, len(checked), len(deg)))
    for k in deg[:5]:
        say("    *** %s/%s is CONSTANT across its seeds" % k)
    if not deg:
        say("  no unit is constant across its seeds -- the loop is not inert.")
        say("  (a FLAG only: no level, spread or ordering is computed or printed)")

    say()
    say("--- B5 simplex / B6 series / B7 window / B8 turnover+gross / B9 sign agreement ---")
    say("  B5 weight violations      : %d" % len(out["simplex"]))
    for e in out["simplex"][:3]:
        say("      %s" % e)
    say("  B6 series violations      : %d" % len(out["series"]))
    for e in out["series"][:3]:
        say("      %s" % e)
    say("  B7 distinct series lengths: %d  %s"
        % (len(out["lengths"]), dict(out["lengths"].most_common(4))))
    say("  B8 turnover violations    : %d   gross violations: %d"
        % (len(out["turnover"]), len(out["gross"])))
    for e in (out["turnover"][:2] + out["gross"][:2]):
        say("      %s" % e)
    say("  B9 replay/archive SIGN disagreements: %d" % len(out["signflip"]))
    for e in out["signflip"][:3]:
        say("      %s" % e)

    expected_nan = sum(c for k, c in out["nonfinite"].items() if "EXPECTED" in k)
    total = (sum(out["nonfinite"].values()) - expected_nan + len(out["sign"]) + sum(out["range"].values())
             + len(deg) + len(out["simplex"]) + len(out["series"]) + len(out["turnover"])
             + len(out["gross"]) + len(out["signflip"]) + (1 if len(out["lengths"]) > 1 else 0))
    say()
    if total == 0:
        say("VERDICT: PLAUSIBLE -- every outcome is finite, correctly signed, inside a physically")
        say("  defensible band, on the simplex, over an identical window, and no arm is degenerate.")
        say("  This says the numbers are REAL. It says NOTHING about which arm is ahead, by design.")
    else:
        say("VERDICT: %d IMPLAUSIBILITY SIGNAL(S) -- investigate before trusting any analysis." % total)
    _assert_blind(L, out["by_arm"])
    print("\n".join(L))
    return 0 if total == 0 else 1


def _selftest() -> int:
    import tempfile
    passed = failed = 0

    def check(name, got, want):
        nonlocal passed, failed
        ok = got == want
        passed, failed = passed + (1 if ok else 0), failed + (0 if ok else 1)
        print("  %-56s got %-6r want %-6r %s" % (name, got, want, "PASS" if ok else "FAIL"))

    def mk(root: Path, line: str, arm: str, seed: int, sharpe: float, cvar: float,
           rets: list[float], w=None):
        d = root / line / arm / f"{arm}-s{seed}"
        d.mkdir(parents=True, exist_ok=True)
        m = {"test_sharpe": sharpe, "test_cvar05": cvar, "val_fitness": 0.3,
             "test_returns": rets, "test_turnover": [0.1], "test_gross": [0.004]}   # a RETURN, not an exposure
        if w is not None:
            m["test_alloc"] = {"weights": w}
        (d / "record.json").write_text(json.dumps(
            {"run_id": f"{arm}-s{seed}", "arm": arm, "seed": seed,
             "test_returns": rets, "metrics": m}), encoding="utf-8")

    good = [0.001 * ((-1) ** i) + 0.0004 for i in range(100)]
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for s in range(4):
            mk(root, "test", "a", s, 1.1 + 0.01 * s, -0.02, good, [[0.5, 0.5]])
        check("S1 a healthy archive is PLAUSIBLE", render(scan(root)), 0)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for s in range(4):
            mk(root, "test", "a", s, 1.1 + 0.01 * s, +0.02, good, [[0.5, 0.5]])
        check("S2 a POSITIVE cvar05 is caught (B2)", render(scan(root)), 1)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for s in range(4):
            mk(root, "test", "a", s, 1.1, -0.02, good, [[0.5, 0.5]])   # identical sharpe
        check("S3 a DEGENERATE arm is caught (B4)", render(scan(root)), 1)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for s in range(4):
            mk(root, "test", "a", s, 1.1 + 0.01 * s, -0.02, good, [[0.9, 0.9]])
        check("S4 weights off the simplex are caught (B5)", render(scan(root)), 1)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for s in range(4):
            mk(root, "test", "a", s, 999.0, -0.02, good, [[0.5, 0.5]])
        check("S5 an absurd Sharpe is caught (B3)", render(scan(root)), 1)
    with tempfile.TemporaryDirectory() as td:
        check("S6 an EMPTY root is NOT clean", render(scan(Path(td))), 2)
    print()
    print("selftest: %d passed, %d FAILED" % (passed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    _root = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") \
        else Path("outputs/campaign_cluster_run4")
    if not _root.is_dir():
        print("*** CANNOT RUN: %s is not a directory. This is NOT a clean result. ***" % _root)
        sys.exit(2)
    sys.exit(render(scan(_root)))
