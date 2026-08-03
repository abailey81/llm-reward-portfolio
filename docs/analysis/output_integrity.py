"""OUTPUT INTEGRITY -- are the campaign's actual OUTPUTS distinct, finite and non-degenerate?

The campaign's scientific output is (a) the authored reward programs and (b) the realised
return series the trained policies produce. Sessions 3-4 audited (a) heavily (construct
prevalence, load-bearing terms, safe-default counters) and checked (b) only for LENGTH
("all 388 test records carry test_returns of length 1571"). Nobody has looked at the
CONTENT.

Four questions, all effect-blind -- this compares HASHES and structural properties, never
values, means, or any arm-vs-arm contrast. No hypothesis quantity is computed:

  Q1 WITHIN a unit, are the seed replicates DISTINCT?
     30 seeds must give 30 different series. Identical seeds => the seeding is not
     reaching the policy and every CI in the study is fiction.
  Q2 ACROSS units, is any series shared?
     Two different reward programs producing a byte-identical realised series means the
     reward did not influence the policy, or a winner was wired twice.
  Q3 Is any series DEGENERATE -- constant, all-zero, or (near-)zero variance?
     A policy that went all-cash or froze produces a valid-looking record with no content.
  Q4 Is any series NON-FINITE or the wrong length?

Read-only. Run:  python docs/analysis/output_integrity.py [--selftest]
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARCHIVE = REPO / "outputs" / "campaign_cluster_run4"
SERIES_FIELDS = ("test_returns", "per_period_pnl")


def _digest(seq) -> str:
    h = hashlib.sha256()
    for v in seq:
        h.update(repr(float(v)).encode())
    return h.hexdigest()[:16]


def _stats(seq) -> tuple[int, int, float, float]:
    """(n, n_nonfinite, min, max) without importing numpy -- keep the probe dependency-free."""
    n = len(seq)
    bad = 0
    lo, hi = math.inf, -math.inf
    for v in seq:
        try:
            f = float(v)
        except (TypeError, ValueError):
            bad += 1
            continue
        if not math.isfinite(f):
            bad += 1
            continue
        lo = min(lo, f)
        hi = max(hi, f)
    if lo is math.inf:
        lo = hi = float("nan")
    return n, bad, lo, hi


def scan(root: Path) -> dict:
    """One pass over every TEST-tier record. Search records are excluded: their series are
    validation-split objects with a different length and are not seed replicates."""
    recs = []
    for p in root.rglob("record.json"):
        rel = p.relative_to(root)
        if rel.parts[0].startswith(".pull_tmp") or not rel.parts[0].startswith("test"):
            continue
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        unit = f"{rel.parts[0]}/{rel.parts[1]}"
        entry = {"unit": unit, "run_id": r.get("run_id"), "seed": r.get("seed"),
                 "rel": str(rel), "series": {}}
        for f in SERIES_FIELDS:
            s = r.get(f)
            if isinstance(s, list) and s:
                n, bad, lo, hi = _stats(s)
                entry["series"][f] = {"n": n, "bad": bad, "lo": lo, "hi": hi,
                                      "d": _digest(s), "const": (hi == lo)}
        recs.append(entry)
    return {"records": recs}


def report(res: dict) -> int:
    recs = res["records"]
    rc = 0
    print(f"=== OUTPUT INTEGRITY over {len(recs)} TEST-tier records ===")

    for field in SERIES_FIELDS:
        have = [r for r in recs if field in r["series"]]
        if not have:
            print(f"\n-- {field}: ABSENT on every record")
            continue
        lens = Counter(r["series"][field]["n"] for r in have)
        print(f"\n-- {field}: present on {len(have)}/{len(recs)}; "
              f"lengths {dict(lens)}")

        bad = [r for r in have if r["series"][field]["bad"]]
        if bad:
            rc = 2
            print(f"   !! Q4 NON-FINITE in {len(bad)} record(s):")
            for r in bad[:10]:
                print(f"      {r['rel']}  bad={r['series'][field]['bad']}")
        else:
            print("   Q4 OK -- every value finite")

        const = [r for r in have if r["series"][field]["const"]]
        if const:
            rc = max(rc, 1)
            print(f"   ! Q3 DEGENERATE (zero-variance) in {len(const)} record(s):")
            for r in const[:10]:
                s = r["series"][field]
                print(f"      {r['rel']}  constant at {s['lo']}")
        else:
            print("   Q3 OK -- no zero-variance series")

        # Q1 within-unit duplicate seeds
        by_unit: defaultdict[str, defaultdict[str, list]] = defaultdict(lambda: defaultdict(list))
        for r in have:
            by_unit[r["unit"]][r["series"][field]["d"]].append(r)
        dup_within = {u: {d: v for d, v in dd.items() if len(v) > 1}
                      for u, dd in by_unit.items()}
        dup_within = {u: d for u, d in dup_within.items() if d}
        if dup_within:
            rc = 2
            print(f"   !! Q1 IDENTICAL SEED REPLICATES inside {len(dup_within)} unit(s):")
            for u, dd in list(dup_within.items())[:10]:
                for d, v in list(dd.items())[:3]:
                    ids = ", ".join(str(x["run_id"]) for x in v[:6])
                    print(f"      {u}: {len(v)} records share digest {d} -> {ids}")
        else:
            print("   Q1 OK -- every seed replicate distinct within its unit")

        # Q2 cross-unit collisions
        by_digest: defaultdict[str, set] = defaultdict(set)
        holder: defaultdict[str, list] = defaultdict(list)
        for r in have:
            by_digest[r["series"][field]["d"]].add(r["unit"])
            holder[r["series"][field]["d"]].append(r)
        cross = {d: u for d, u in by_digest.items() if len(u) > 1}
        if cross:
            rc = 2
            print(f"   !! Q2 SERIES SHARED ACROSS {len(cross)} digest(s) spanning >1 unit:")
            for d, units in list(cross.items())[:10]:
                ex = ", ".join(str(x["run_id"]) for x in holder[d][:4])
                print(f"      digest {d}: units {sorted(units)}  e.g. {ex}")
        else:
            print("   Q2 OK -- no series shared between different units")

    print(f"\n  VERDICT: {'CRITICAL' if rc == 2 else 'WARN' if rc == 1 else 'CLEAN'}")
    return rc


# --------------------------------------------------------------------------------- #
def _selftest() -> int:
    import shutil
    import tempfile
    ok = True

    def case(name, cond):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok = ok and cond

    tmp = Path(tempfile.mkdtemp(prefix="outint_"))
    try:
        def write(unit, rid, series, pnl=None):
            d = tmp / "test" / unit / rid
            d.mkdir(parents=True)
            (d / "record.json").write_text(json.dumps(
                {"run_id": rid, "seed": 0, "test_returns": series,
                 "per_period_pnl": pnl if pnl is not None else series}), encoding="utf-8")

        write("u1", "u1-s0", [0.1, 0.2, 0.3])
        write("u1", "u1-s1", [0.15, 0.25, 0.35])
        write("u2", "u2-s0", [0.4, 0.5, 0.6])
        r = scan(tmp)
        case("clean fixture is SEEN (denominator non-zero)", len(r["records"]) == 3)
        case("clean fixture -> no within-unit duplicates",
             report_quiet(r, "dup_within") == 0)
        case("clean fixture -> no cross-unit collisions", report_quiet(r, "cross") == 0)
        case("clean fixture -> no degenerate", report_quiet(r, "const") == 0)
        case("clean fixture -> no non-finite", report_quiet(r, "bad") == 0)

        write("u1", "u1-s2", [0.1, 0.2, 0.3])                    # dup of u1-s0
        r = scan(tmp)
        case("Q1 FIRES on identical seed replicates", report_quiet(r, "dup_within") > 0)

        # ⚠ THE CASES ABOVE USE `report_quiet`, WHICH RE-IMPLEMENTS THE COUNTING. That means
        # they exercise the helper, NOT the real `report()` -- so a mutation that disables
        # the duplicate detection INSIDE report() survived the whole selftest
        # (mutation_test.py). A selftest that does not run the reporting path cannot detect
        # that path breaking. These cases drive the REAL report() and assert on its rc.
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc_dup = report(scan(tmp))
        out_dup = buf.getvalue()
        case("REAL report() escalates on identical seed replicates", rc_dup == 2)
        case("REAL report() names the within-unit duplicate",
             "IDENTICAL SEED REPLICATES" in out_dup)

        write("u3", "u3-s0", [0.4, 0.5, 0.6])                    # dup of u2-s0
        r = scan(tmp)
        case("Q2 FIRES on a cross-unit collision", report_quiet(r, "cross") > 0)

        write("u4", "u4-s0", [0.7, 0.7, 0.7])                    # constant
        r = scan(tmp)
        case("Q3 FIRES on a zero-variance series", report_quiet(r, "const") > 0)

        write("u5", "u5-s0", [0.1, float("nan"), 0.3])
        r = scan(tmp)
        case("Q4 FIRES on a non-finite value", report_quiet(r, "bad") > 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\nselftest: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


def report_quiet(res: dict, what: str) -> int:
    """Count a single condition without printing -- used only by the selftest."""
    recs = [r for r in res["records"] if "test_returns" in r["series"]]
    if what == "bad":
        return sum(1 for r in recs if r["series"]["test_returns"]["bad"])
    if what == "const":
        return sum(1 for r in recs if r["series"]["test_returns"]["const"])
    by_unit: defaultdict[str, Counter] = defaultdict(Counter)
    by_digest: defaultdict[str, set] = defaultdict(set)
    for r in recs:
        d = r["series"]["test_returns"]["d"]
        by_unit[r["unit"]][d] += 1
        by_digest[d].add(r["unit"])
    if what == "dup_within":
        return sum(1 for u, c in by_unit.items() for d, n in c.items() if n > 1)
    if what == "cross":
        return sum(1 for d, u in by_digest.items() if len(u) > 1)
    raise KeyError(what)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    raise SystemExit(report(scan(ARCHIVE)))
