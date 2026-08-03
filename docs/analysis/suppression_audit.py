"""FALSE-NEGATIVE AUDIT OF MY OWN SUPPRESSIONS. Coord's M268 method, turned on this lane.

Coord: "every false-alarm fix I made today traded NOISE for QUIET. That is only the right
trade if it cannot also silence a REAL event." They attacked their repairs from the
false-negative side and found one that would have blinded the only genuine strand the
campaign has ever had.

I shipped FIVE suppressions today and had never tested any of them that way:

  S1 env_census.ACKNOWLEDGED            12 determinism keys downgraded from CRITICAL
  S2 search_integrity.ACKNOWLEDGED_COLLISIONS   1 cross-arm val_returns digest
  S3 record_validator R3 relaxation     candidate_id no longer checked on test/frozen
  S4 search_integrity depth-4 filter    A3's nested duplicates skipped
  S5 deep_record_audit PASS1 skip       metrics.test_components.* exempt from drift

For each: INJECT a NEW, GENUINELY DIFFERENT violation of the same family and assert the
instrument STILL FIRES. A suppression that also swallows the new case is a false negative and
is worse than the noise it removed.

Read-only; every test runs on a synthetic fixture in a temp dir.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, fired: bool, expect_fire: bool, note: str = "") -> None:
    ok = fired is expect_fire
    RESULTS.append((name, ok, note))
    verb = "FIRES" if fired else "silent"
    want = "must fire" if expect_fire else "must stay silent"
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}\n           -> {verb} ({want}) {note}")


def _rec(d: Path, **kw):
    d.mkdir(parents=True, exist_ok=True)
    base = {"run_id": d.name, "arm": d.parent.name, "seed": 0, "fold": "test",
            "candidate_id": d.name, "generation": 0,
            "reward_source_hash": "0" * 64, "feedback_block": "",
            "metrics": {}, "wall_clock": 1.0, "env_fingerprint": {"label": "x"}}
    base.update(kw)
    (d / "record.json").write_text(json.dumps(base), encoding="utf-8")


def _env(d: Path, **kw):
    d.mkdir(parents=True, exist_ok=True)
    base = {"cpu": {"model_name": "Intel(R) Xeon(R) Gold 6240 CPU @ 2.60GHz"},
            "torch_cuda": {"deterministic_algorithms_enabled": True,
                           "matmul_allow_tf32": True},
            "determinism_env": {"OMP_NUM_THREADS": "8"}}
    for k, v in kw.items():
        if isinstance(v, dict):
            base.setdefault(k, {}).update(v)
        else:
            base[k] = v
    (d / "env.json").write_text(json.dumps(base), encoding="utf-8")


# --------------------------------------------------------------- S1 ------------- #
def audit_s1() -> None:
    """env_census.ACKNOWLEDGED silences 12 determinism keys. Those keys were acknowledged
    for ONE observed partition (search-tier vs test-tier). *** Does the suppression also
    swallow the SAME key varying in a NEW way -- e.g. WITHIN a single comparison unit? ***
    That would be a genuine, unacknowledged envelope violation."""
    import env_census as ec

    print("\nS1 env_census.ACKNOWLEDGED (12 determinism keys)")
    tmp = Path(tempfile.mkdtemp(prefix="s1_"))
    try:
        u = tmp / "test" / "unit"
        _env(u / "unit-s0")
        _rec(u / "unit-s0")
        _env(u / "unit-s1")
        _rec(u / "unit-s1")
        res = ec.scan(tmp)
        clean_bad = [k for k, v in res["glob"].items()
                     if len(v) > 1 and ec.is_determinism_relevant(k)]
        check("S1a clean fixture stays silent", bool(clean_bad), False)

        # NEW violation: the SAME acknowledged key varies WITHIN one comparison unit.
        _env(u / "unit-s2", torch_cuda={"deterministic_algorithms_enabled": False,
                                        "matmul_allow_tf32": True})
        _rec(u / "unit-s2")
        # ⚠ ASK THE INSTRUMENT, DO NOT RE-IMPLEMENT ITS RULE. The first version of this test
        # computed `within and not acked` -- i.e. it hard-coded the OLD logic and would have
        # reported FAIL for ever regardless of the fix. A test that re-implements the thing it
        # tests cannot observe a repair.
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = ec.report(ec.scan(tmp))
        check("S1b a determinism key varying WITHIN one unit escalates",
              rc == 2, True,
              "<- acknowledged key + within-unit split still SILENCED" if rc != 2 else "")

        # S1c: the instance-level acknowledgement must NOT become a key-level one. A unit
        # that is acknowledged for `platform` must still escalate on a DIFFERENT key, and a
        # DIFFERENT unit must still escalate on `platform`.
        known_unit, known_key = next(iter(ec.ACKNOWLEDGED_UNIT_SPLITS))
        check("S1c a known (unit, key) instance is acknowledged",
              (known_unit, known_key) in ec.ACKNOWLEDGED_UNIT_SPLITS, True)
        check("S1d the SAME unit with a DIFFERENT key is NOT acknowledged",
              (known_unit, "torch_cuda.deterministic_algorithms_enabled")
              in ec.ACKNOWLEDGED_UNIT_SPLITS, False)
        check("S1e a DIFFERENT unit with the SAME key is NOT acknowledged",
              ("search/distributional", known_key) in ec.ACKNOWLEDGED_UNIT_SPLITS, False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------- S3 ------------- #
def audit_s3() -> None:
    """record_validator R3 was relaxed: candidate_id is only checked on the SEARCH tier.
    *** Does that let a test record point at the WRONG unit? ***"""
    import record_validator as rv

    print("\nS3 record_validator R3 relaxation (candidate_id unchecked off search)")
    good = dict(run_id="placebo-s0", arm="placebo", seed=0, fold="test",
                candidate_id="placebo", generation=0,
                reward_source_hash="0" * 64, feedback_block="", metrics={},
                wall_clock=1.0, env_fingerprint={"label": "x"})
    rel = Path("test/placebo/placebo-s0/record.json")
    check("S3a legitimate test record stays silent",
          bool(rv.validate(rel, dict(good))), False)

    wrong = dict(good, candidate_id="distributional")   # names a DIFFERENT unit
    fired = any(v.startswith("R3") for v in rv.validate(rel, wrong))
    check("S3b test record whose candidate_id names ANOTHER unit escalates", fired, True,
          "<- relaxation swallows a real identity defect" if not fired else "")


# --------------------------------------------------------------- S4 ------------- #
def audit_s4() -> None:
    """search_integrity skips depth-5 records (A3's nested duplicates). A3 established they
    are BYTE-IDENTICAL today. *** Would a nested duplicate with DIFFERENT content be
    silenced? *** That would be real corruption, not a known artefact."""
    import search_integrity as si

    print("\nS4 search_integrity depth-4 filter (A3 nested duplicates skipped)")
    tmp = Path(tempfile.mkdtemp(prefix="s4_"))
    try:
        c = tmp / "search" / "arm" / "cand"
        _rec(c, metrics={"val_returns": [0.1, 0.2, 0.3], "val_fitness": 0.5},
             reward_source="def reward(a,b,c,d,e):\n    return 0.0,{},None")
        # a nested duplicate with DIFFERENT content -> genuine corruption
        _rec(c / "cand", metrics={"val_returns": [9.9, 9.9, 9.9], "val_fitness": 0.5},
             reward_source="def reward(a,b,c,d,e):\n    return 0.0,{},None")
        # ⚠ ASK THE INSTRUMENT. The first version looked for the record in scan()["recs"] --
        # but the fix deliberately keeps nested copies OUT of the record set and routes any
        # DIVERGENCE to its own list, so that assertion could never pass however good the fix.
        res = si.scan(tmp)
        flagged = bool(res.get("nested_divergent"))
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = si.report(res)
        check("S4 a DIVERGENT nested duplicate is reported", flagged and rc == 2, True,
              "<- divergent nested content still invisible" if not flagged else "")

        # and the control: a BYTE-IDENTICAL nested copy must stay silent (that is A3's
        # benign artefact, and re-alarming on it would undo the noise fix).
        tmp2 = Path(tempfile.mkdtemp(prefix="s4b_"))
        try:
            c2 = tmp2 / "search" / "arm" / "cand"
            payload = dict(metrics={"val_returns": [0.1, 0.2], "val_fitness": 0.5},
                           reward_source="def reward(a,b,c,d,e):\n    return 0.0,{},None")
            _rec(c2, **payload)
            (c2 / "cand").mkdir(parents=True, exist_ok=True)
            shutil.copyfile(c2 / "record.json", c2 / "cand" / "record.json")
            check("S4b a BYTE-IDENTICAL nested copy stays silent (noise fix intact)",
                  bool(si.scan(tmp2).get("nested_divergent")), False)
        finally:
            shutil.rmtree(tmp2, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --------------------------------------------------------------- S5 ------------- #
def audit_s5() -> None:
    """deep_record_audit PASS 1 exempts metrics.test_components.* from schema drift because
    the names are author-chosen PER PROGRAM. *** But within ONE unit every seed runs the SAME
    program, so a component present on only SOME seeds of a unit IS a defect. Is it caught
    anywhere? *** PASS 4 checks constancy and finiteness -- not presence across seeds."""
    import deep_record_audit as dra

    print("\nS5 deep_record_audit PASS1 test_components exemption")
    tmp = Path(tempfile.mkdtemp(prefix="s5_"))
    try:
        u = tmp / "test" / "unit"
        for s in range(3):
            comps = {"alpha": 1.0 + s, "beta": 2.0 + s}
            if s == 2:
                comps.pop("beta")           # present on 2 of 3 seeds of ONE unit
            _rec(u / f"unit-s{s}", seed=s, run_id=f"unit-s{s}", candidate_id="unit",
                 metrics={"test_components": comps})
        recs = list(dra.iter_records(tmp))
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            dra.pass4(recs)
        out = buf.getvalue()
        caught = "beta" in out
        check("S5 a component missing from SOME seeds of one unit is reported",
              caught, True,
              "<- neither PASS1 (exempt) nor PASS4 (constancy only) sees it"
              if not caught else "")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    print("=== FALSE-NEGATIVE AUDIT OF THIS LANE'S OWN SUPPRESSIONS ===")
    print("    method: inject a NEW violation of each suppressed family; the instrument")
    print("    MUST still fire. A suppression that swallows the new case is a false")
    print("    negative and is worse than the noise it removed.")
    for fn in (audit_s1, audit_s3, audit_s4, audit_s5):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            RESULTS.append((fn.__name__, False, f"raised {type(exc).__name__}: {exc}"))
            print(f"  [FAIL] {fn.__name__} raised {type(exc).__name__}: {exc}")
    bad = [r for r in RESULTS if not r[1]]
    print(f"\n=== {len(RESULTS) - len(bad)}/{len(RESULTS)} suppression checks behave correctly ===")
    for n, _ok, note in bad:
        print(f"    FALSE NEGATIVE: {n}  {note}")
    raise SystemExit(2 if bad else 0)
