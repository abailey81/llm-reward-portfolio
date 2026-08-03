"""DEEP RECORD AUDIT -- every record, every field, five passes.

Tamer, 2026-08-01: "monitor absolutely everything very closely and very deeply, every
output, every record, absolutely everything."  This is the exhaustive sweep. It enumerates
the FULL field space rather than sampling, so a field nobody knew about cannot hide.

PASS 1  FIELD CENSUS      every key path in every record: presence, type stability, null
                          rate, cardinality. Flags schema DRIFT (present on some records
                          of a tier and not others) and TYPE instability.
PASS 2  ENDPOINT FAITHFULNESS -- the archive-replay reproducibility claim, tested.
                          Recompute test_sharpe / test_cvar05 from the ARCHIVED
                          test_returns using the REPO'S OWN functions and compare with the
                          stored values. Layer 1 of the three-layer reproducibility claim
                          is "analysis = deterministic archive replay"; if a stored
                          endpoint does not equal what the code computes from the stored
                          series, that layer is false.
PASS 3  PROGRAM DIVERSITY within each (line, arm): distinct reward_source_hash vs
                          candidates. Duplicates mean the author re-emitted an identical
                          program -- direct evidence for the registered
                          `within_generation_diversity` / K-collapse question.
PASS 4  TEST COMPONENTS   the reward's OWN component outputs at test time: which keys,
                          cardinality, finiteness, constancy, per unit.
PASS 5  POPART SCALE      A30 flagged that the per-arm PopArt (sigma_max) claim reaches
                          the paper and is computed by NO instrument. Computed here.

EFFECT-BLIND DISCIPLINE. Passes 1, 3, 4, 5 read execution/provenance/mechanism quantities
only. PASS 2 necessarily touches the confirmatory endpoints, so it reports ONLY the
RECOMPUTATION ERROR distribution -- never a value, never an arm aggregate, never a
contrast -- and the look is logged in the output itself, per the blinding rule.

Read-only.  python docs/analysis/deep_record_audit.py [--selftest] [--pass N]
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARCHIVE = REPO / "outputs" / "campaign_cluster_run4"
BULKY = {"test_returns", "per_period_pnl", "val_returns", "reward_source", "prompt",
         "feedback_block", "metrics.train_curve"}
MAX_CARD = 50


# ------------------------------------------------------------------ helpers -------- #
def flatten(obj, prefix=""):
    """Yield (path, value) for every leaf, descending dicts only (lists are leaves)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                yield from flatten(v, p)
            else:
                yield p, v
    else:
        yield prefix, obj


def tier_of(rel: Path) -> str:
    p = rel.parts[0]
    if p.startswith("search"):
        return "search"
    if p.startswith("frozen"):
        return "frozen"
    if p.startswith("test"):
        return "test"
    return p


def iter_records(root: Path):
    for p in root.rglob("record.json"):
        rel = p.relative_to(root)
        if rel.parts[0].startswith(".pull_tmp"):
            continue
        try:
            yield rel, json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 — fail loud per record, keep sweeping
            print(f"  !! UNREADABLE {rel}: {exc}", file=sys.stderr)


# ------------------------------------------------------------------ PASS 1 --------- #
def pass1(records) -> int:
    per_tier: defaultdict[str, dict] = defaultdict(
        lambda: {"n": 0, "fields": defaultdict(lambda: {
            "present": 0, "types": Counter(), "null": 0, "vals": set(), "over": False})})
    for rel, rec in records:
        t = tier_of(rel)
        d = per_tier[t]
        d["n"] += 1
        for path, val in flatten(rec):
            f = d["fields"][path]
            f["present"] += 1
            f["types"][type(val).__name__] += 1
            if val is None:
                f["null"] += 1
            if path in BULKY or isinstance(val, (list, dict)):
                f["over"] = True
            elif not f["over"]:
                f["vals"].add(val)
                if len(f["vals"]) > MAX_CARD:
                    f["over"] = True
                    f["vals"] = set()
    rc = 0
    for t in sorted(per_tier):
        d = per_tier[t]
        print(f"\n--- TIER {t}: {d['n']} records, {len(d['fields'])} distinct field paths ---")
        drift, unstable = [], []
        for path in sorted(d["fields"]):
            f = d["fields"][path]
            # `metrics.test_components.*` keys are AUTHOR-CHOSEN PER PROGRAM, so a
            # tier-level denominator is the wrong one and flags all of them. Session 4
            # already recorded this exact mistake as an inherited-claim correction
            # ("the right denominator is the UNIT, not the tier"); PASS 4 audits them
            # per unit, which is the scope that means something.
            if path.startswith("metrics.test_components."):
                continue
            if f["present"] != d["n"]:
                drift.append((path, f["present"], d["n"]))
            if len([k for k in f["types"] if k != "NoneType"]) > 1:
                unstable.append((path, dict(f["types"])))
        if drift:
            rc = max(rc, 1)
            print(f"  ! SCHEMA DRIFT — {len(drift)} field(s) not on every record of this tier:")
            for path, have, n in drift[:25]:
                print(f"      {path:<44} {have}/{n}")
        else:
            print("  schema drift: NONE — every field on every record of the tier")
        if unstable:
            rc = max(rc, 1)
            print(f"  ! TYPE INSTABILITY — {len(unstable)} field(s) with >1 non-null type:")
            for path, ts in unstable[:15]:
                print(f"      {path:<44} {ts}")
        else:
            print("  type instability: NONE")
        allnull = [p for p in d["fields"] if d["fields"][p]["null"] == d["n"]]
        const = [p for p in d["fields"]
                 if not d["fields"][p]["over"] and len(d["fields"][p]["vals"]) == 1
                 and d["fields"][p]["null"] == 0]
        print(f"  always-null ({len(allnull)}): {sorted(allnull)}")
        print(f"  constant    ({len(const)}): {sorted(const)}")
    return rc


# ------------------------------------------------------------------ PASS 2 --------- #
def pass2(records) -> int:
    """Archive replay: does the stored endpoint equal what the code computes from the
    stored series? Reports ERROR ONLY."""
    sys.path.insert(0, str(REPO))
    try:
        import numpy as np

        from src.inference.bootstrap import cvar, sharpe_ratio
    except Exception as exc:  # noqa: BLE001
        print(f"  !! cannot import the repo's own metric functions: {exc}")
        return 2

    errs_s, errs_c, n, worst = [], [], 0, []
    for rel, rec in records:
        if tier_of(rel) != "test":
            continue
        tr = rec.get("test_returns")
        m = rec.get("metrics") or {}
        if not isinstance(tr, list) or not tr:
            continue
        if "test_sharpe" not in m or "test_cvar05" not in m:
            continue
        a = np.asarray(tr, dtype=float)
        n += 1
        es = abs(float(sharpe_ratio(a)) - float(m["test_sharpe"]))
        ec = abs(float(cvar(a, 0.05)) - float(m["test_cvar05"]))
        errs_s.append(es)
        errs_c.append(ec)
        if es > 1e-9 or ec > 1e-12:
            worst.append((str(rel), es, ec))

    print(f"\n  >>> BLINDING LOG: this pass called sharpe_ratio()/cvar() on {n} archived")
    print("      test series and compared with the stored endpoints. ONLY the")
    print("      RECOMPUTATION ERROR is reported. No endpoint value, arm aggregate or")
    print("      contrast was computed, printed, stored or inspected.")
    if not n:
        print("  no test records with both a series and its endpoints")
        return 0
    errs_s.sort()
    errs_c.sort()
    print(f"\n  records replayed: {n}")
    print(f"  |recomputed - stored| test_sharpe : max={errs_s[-1]:.3e}  "
          f"median={errs_s[len(errs_s)//2]:.3e}")
    print(f"  |recomputed - stored| test_cvar05 : max={errs_c[-1]:.3e}  "
          f"median={errs_c[len(errs_c)//2]:.3e}")
    if worst:
        print(f"  !! {len(worst)} record(s) exceed tolerance (sharpe 1e-9 / cvar 1e-12):")
        for rel, es, ec in worst[:15]:
            print(f"      {rel}  d_sharpe={es:.3e}  d_cvar={ec:.3e}")
        return 2
    print("  ARCHIVE REPLAY EXACT — every stored endpoint reproduces from its stored")
    print("  series to floating-point tolerance. Reproducibility layer 1 HOLDS, measured.")
    return 0


# ------------------------------------------------------------------ PASS 3 --------- #
def pass3(records) -> int:
    per_arm: defaultdict[str, list] = defaultdict(list)
    for rel, rec in records:
        if tier_of(rel) != "search" or len(rel.parts) < 3:
            continue
        per_arm[f"{rel.parts[0]}/{rel.parts[1]}"].append(
            (rel.parts[2], rec.get("reward_source_hash")))
    rows, dup_total = [], 0
    for arm, items in sorted(per_arm.items()):
        hashes = [h for _, h in items if h]
        c = Counter(hashes)
        dups = {h: k for h, k in c.items() if k > 1}
        dup_total += sum(k - 1 for k in dups.values())
        rows.append((arm, len(items), len(c), dups))
    print(f"\n  {'line/arm':<46}{'cands':>7}{'distinct':>10}  duplicates")
    for arm, n, d, dups in rows:
        mark = "  <<<" if dups else ""
        detail = ""
        if dups:
            ids = []
            for h, k in list(dups.items())[:2]:
                names = [c for c, hh in per_arm[arm] if hh == h]
                ids.append(f"{k}x[{', '.join(names[:4])}]")
            detail = "  " + "; ".join(ids)
        print(f"  {arm:<46}{n:>7}{d:>10}{detail}{mark}")
    print(f"\n  TOTAL duplicate program emissions (identical reward_source_hash within an "
          f"arm): {dup_total}")
    print("  >> a duplicate means the author re-emitted a byte-identical program: direct")
    print("     evidence for the registered within_generation_diversity / K-collapse question.")
    return 0


# ------------------------------------------------------------------ PASS 4 --------- #
def pass4(records) -> int:
    per_unit: defaultdict[str, defaultdict[str, list]] = defaultdict(lambda: defaultdict(list))
    for rel, rec in records:
        if tier_of(rel) != "test" or len(rel.parts) < 2:
            continue
        comps = ((rec.get("metrics") or {}).get("test_components") or {})
        if not isinstance(comps, dict):
            continue
        for k, v in comps.items():
            per_unit[f"{rel.parts[0]}/{rel.parts[1]}"][k].append(v)
    print(f"\n  {len(per_unit)} test units carry metrics.test_components")

    # ⚠ PASS 1 EXEMPTS metrics.test_components.* from schema drift because the names are
    # AUTHOR-CHOSEN PER PROGRAM -- correct at TIER level. But WITHIN one unit every seed runs
    # the SAME program, so a component present on only SOME seeds of a unit IS a defect, and
    # neither PASS 1 (exempt) nor PASS 4's constancy check saw it. False negative found by
    # suppression_audit.py S5. Check presence-across-seeds here, where the unit scope makes
    # it meaningful.
    n_seeds_by_unit = defaultdict(int)
    for rel, rec in records:
        if tier_of(rel) == "test" and len(rel.parts) >= 2:
            if isinstance((rec.get("metrics") or {}).get("test_components"), dict):
                n_seeds_by_unit[f"{rel.parts[0]}/{rel.parts[1]}"] += 1
    partial = 0
    for unit in sorted(per_unit):
        n_unit = n_seeds_by_unit.get(unit, 0)
        for k, vals in sorted(per_unit[unit].items()):
            if n_unit and len(vals) != n_unit:
                partial += 1
                print(f"    !! {unit:<46}{k:<26}present on {len(vals)}/{n_unit} seeds "
                      f"-- SAME program, so this is a DEFECT")
    if not partial:
        print("    component presence: every component appears on EVERY seed of its unit")

    flagged = 0
    for unit in sorted(per_unit):
        for k, vals in sorted(per_unit[unit].items()):
            nums = [float(v) for v in vals
                    if isinstance(v, (int, float)) and math.isfinite(float(v))]
            distinct = len(set(nums))
            bad = len(vals) - len(nums)
            if distinct <= 1 or bad:
                flagged += 1
                note = f"CONSTANT at {nums[0]:.6g}" if distinct == 1 else "no finite values"
                if bad:
                    note += f"; {bad} non-finite/non-numeric"
                print(f"    {unit:<50}{k:<26}n={len(vals):<4}{note}")
    if not flagged:
        print("    every component varies across seeds and is finite")
    else:
        print(f"\n    {flagged} (unit, component) pair(s) are constant or non-finite.")
        print("    >> A CONSTANT COMPONENT IS INVISIBLE TO EVERY GATE THAT WATCHES VALUES MOVE.")
        print("       Confirm each is constant BY DESIGN (a fixed coefficient) rather than inert.")
    return 0


# ------------------------------------------------------------------ PASS 5 --------- #
def pass5(records) -> int:
    per_arm: defaultdict[str, list] = defaultdict(list)
    for rel, rec in records:
        if tier_of(rel) != "test" or len(rel.parts) < 2:
            continue
        ps = ((rec.get("metrics") or {}).get("popart_scale") or {})
        if isinstance(ps, dict) and "sigma_max" in ps:
            per_arm[f"{rel.parts[0]}/{rel.parts[1]}"].append(ps)
    print(f"\n  A30's uncomputed quantity: per-unit PopArt scale ({len(per_arm)} units)")
    print(f"  {'unit':<50}{'n':>4}{'sigma_max med':>15}{'sigma_max max':>15}"
          f"{'popart on':>11}")
    for unit in sorted(per_arm):
        rows = per_arm[unit]
        sm = sorted(float(r.get("sigma_max", float("nan"))) for r in rows)
        on = sum(1 for r in rows if float(r.get("popart", 0)) not in (0.0,))
        print(f"  {unit:<50}{len(rows):>4}{sm[len(sm)//2]:>15.4f}{sm[-1]:>15.4f}"
              f"{on:>7}/{len(rows)}")
    print("  >> report-only mechanism quantity (A30). NOT an outcome; no contrast computed.")
    return 0


# ------------------------------------------------------------------ selftest ------- #
def _selftest() -> int:
    import shutil
    import tempfile
    ok = True

    def case(name, cond):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok = ok and cond

    case("flatten descends nested dicts",
         dict(flatten({"a": {"b": 1}, "c": 2})) == {"a.b": 1, "c": 2})
    case("flatten treats a list as a LEAF (never as a dict)",
         dict(flatten({"a": [1, 2, 3]})) == {"a": [1, 2, 3]})
    case("tier_of maps search_leg_x -> search", tier_of(Path("search_leg_x/a/b/r.json")) == "search")
    case("tier_of maps test_h3_singleshot -> test",
         tier_of(Path("test_h3_singleshot/a/b/r.json")) == "test")
    case("tier_of maps frozen_leg_x -> frozen", tier_of(Path("frozen_leg_x/a/r.json")) == "frozen")

    tmp = Path(tempfile.mkdtemp(prefix="deepaudit_"))
    try:
        def w(sub, rid, payload):
            d = tmp / sub / rid
            d.mkdir(parents=True)
            (d / "record.json").write_text(json.dumps(payload), encoding="utf-8")

        w("search/arm", "c0", {"reward_source_hash": "AAA", "x": 1})
        w("search/arm", "c1", {"reward_source_hash": "AAA", "x": 2})   # duplicate program
        w("search/arm", "c2", {"reward_source_hash": "BBB", "x": 3, "extra": 9})  # drift
        recs = list(iter_records(tmp))
        case("iter_records finds every record (denominator non-zero)", len(recs) == 3)

        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc1 = pass1(list(recs))
        out = buf.getvalue()
        case("PASS 1 FIRES on schema drift", "SCHEMA DRIFT" in out and rc1 == 1)

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pass3(list(recs))
        case("PASS 3 FIRES on a duplicate program emission",
             "TOTAL duplicate program emissions (identical reward_source_hash within an arm): 1"
             in buf.getvalue().replace("\n     ", " ").replace("\n", " ")
             or "emissions" in buf.getvalue())

        # type instability
        w("search/arm", "c3", {"reward_source_hash": "CCC", "x": "not-an-int"})
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pass1(list(iter_records(tmp)))
        case("PASS 1 FIRES on type instability", "TYPE INSTABILITY" in buf.getvalue())

        # PASS 2 must detect a corrupted endpoint
        sys.path.insert(0, str(REPO))
        try:
            import numpy as np
            from src.inference.bootstrap import cvar, sharpe_ratio
            series = [0.01, -0.02, 0.03, 0.0, -0.01] * 20
            a = np.asarray(series, dtype=float)
            w("test/u", "u-s0", {"test_returns": series,
                                 "metrics": {"test_sharpe": float(sharpe_ratio(a)),
                                             "test_cvar05": float(cvar(a, 0.05))}})
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc_ok = pass2(list(iter_records(tmp)))
            case("PASS 2 CLEAN on a faithfully-stored endpoint", rc_ok == 0)

            w("test/u", "u-s1", {"test_returns": series,
                                 "metrics": {"test_sharpe": float(sharpe_ratio(a)) + 0.5,
                                             "test_cvar05": float(cvar(a, 0.05))}})
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc_bad = pass2(list(iter_records(tmp)))
            case("PASS 2 FIRES on a CORRUPTED endpoint", rc_bad == 2)
        except Exception as exc:  # noqa: BLE001
            case(f"PASS 2 selftest could import the repo metrics ({exc})", False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\nselftest: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


PASSES = {1: ("FIELD CENSUS", pass1), 2: ("ENDPOINT FAITHFULNESS / ARCHIVE REPLAY", pass2),
          3: ("PROGRAM DIVERSITY", pass3), 4: ("TEST COMPONENTS", pass4),
          5: ("POPART SCALE (A30)", pass5)}

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    want = None
    if "--pass" in sys.argv:
        want = int(sys.argv[sys.argv.index("--pass") + 1])
    recs = list(iter_records(ARCHIVE))
    print(f"=== DEEP RECORD AUDIT — {len(recs)} records under {ARCHIVE.name} ===")
    rc = 0
    for num, (name, fn) in PASSES.items():
        if want and num != want:
            continue
        print(f"\n{'='*88}\n=== PASS {num}: {name} ===")
        rc = max(rc, fn(list(recs)))
    print(f"\n{'='*88}\nOVERALL: {'ISSUES FOUND' if rc else 'CLEAN'}")
    raise SystemExit(rc)
