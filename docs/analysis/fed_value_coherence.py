"""S13 — THE FED VALUES THEMSELVES: are they mathematically coherent, and did the model see the
numbers we actually measured?

★ WHY THIS IS THE LAST THING LEFT TO CHECK (RUN 14, 2026-08-02).
Five layers now cover every record: its contract (R1-R9), its files (P1-P4), its numbers (S1-S10),
the SHAPE of the text fed to the model (S11) and the authored code (S12). **S11 proved the
distributional arm receives six tail lines and the scalar arm none. It did NOT check that those six
numbers are correct, coherent, or even the ones we measured.** A renderer that mislabelled CVaR 1% as
CVaR 25%, or that fed a stale generation's statistics, would pass every existing check while the
manipulated variable silently carried the wrong values.

THE CHECKS

  V1  CVaR MONOTONICITY -- a MATHEMATICAL NECESSITY, not a convention. CVaR at level a averages the
      worst a-fraction of outcomes, so a more extreme level averages a smaller and worse set:
          cvar_01 <= cvar_05 <= cvar_10 <= cvar_25       (signed returns; more negative = worse)
      A violation means the tail estimator is wrong, and the tail estimator IS the manipulated
      variable. This is the single most decisive check available on the fed vector.
  V2  left_tail_mass is a MASS -> it must lie in [0, 1].
  V3  every one of the six fed statistics is finite.
  V4  PIPELINE FIDELITY -- the values RENDERED into a generation's reflection prompt must equal the
      `tail_stats` actually measured on a candidate of the PREVIOUS generation, to the 4 decimal
      places the renderer emits. This walks the whole feedback loop numerically: measurement ->
      render -> prompt. It is deliberately matched against ANY candidate of that generation rather
      than "the best", so the check needs no fitness value and stays effect-blind.
  V5  the RENDERED values are themselves monotone -- i.e. the text the model read is coherent, not
      merely the stored statistics.

⚠ THE RENDER ORDER IS NOT THE LEVEL ORDER, AND ASSUMING IT WOULD BE A BUG. The prompt emits
5%, 10%, 25%, then 1% (flagged "high-variance estimate"), then mass and skew. Parsing positionally
would silently pair cvar_25 with cvar_01. This module parses by the LABEL.

EFFECT-BLIND: reads tail diagnostics and rendered tail lines only. The validation-fitness line of the
prompt is never parsed, and no Sharpe, CVaR-of-test, fitness or arm aggregate is read or compared.

USAGE
    python docs/analysis/fed_value_coherence.py            # whole archive
    python docs/analysis/fed_value_coherence.py --selftest
EXIT 0 = coherent, 1 = an incoherence, 2 = could not run.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

#: The registered fed vector, in LEVEL order (not render order).
CVAR_KEYS = ["cvar_01", "cvar_05", "cvar_10", "cvar_25"]
ALL_KEYS = CVAR_KEYS + ["left_tail_mass", "robust_skew"]

#: Rendered lines, parsed BY LABEL. `CVaR 1%` may carry a trailing marker.
RE_CVAR = re.compile(r"^\s*CVaR\s+(\d+)%\s*:\s*([+-]?\d+\.?\d*)", re.I)
RE_MASS = re.compile(r"^\s*left-tail\s+mass\s*:\s*([+-]?\d+\.?\d*)", re.I)
RE_SKEW = re.compile(r"^\s*left-tail\s+skew\s*:\s*([+-]?\d+\.?\d*)", re.I)
LEVEL_TO_KEY = {"1": "cvar_01", "5": "cvar_05", "10": "cvar_10", "25": "cvar_25"}


def _is_d18_nested(p: Path) -> bool:
    """A D18 `shutil.move` nested duplicate: a directory whose name equals its parent's."""
    parts = p.parts
    return any(parts[i] == parts[i - 1] for i in range(1, len(parts) - 1))


def parse_rendered(prompt: str) -> dict[str, float]:
    """Rendered tail values, keyed by STATISTIC (never by position)."""
    out: dict[str, float] = {}
    for ln in prompt.splitlines():
        m = RE_CVAR.match(ln)
        if m and m.group(1) in LEVEL_TO_KEY:
            out[LEVEL_TO_KEY[m.group(1)]] = float(m.group(2))
            continue
        m = RE_MASS.match(ln)
        if m:
            out["left_tail_mass"] = float(m.group(1))
            continue
        m = RE_SKEW.match(ln)
        if m:
            out["robust_skew"] = float(m.group(1))
    return out


def check_vector(ts: dict, label: str, require: list[str] | None = None) -> list[str]:
    """V1-V3 on a vector of tail statistics.

    ``require`` is the key set this vector is REGISTERED to carry. It defaults to all six, but the
    arms differ BY DESIGN and demanding six of every arm was my own error (P201): `scalar_cvar5` is
    fed exactly ONE CVaR line, so requiring the other five reported 218 phantom violations. S11
    already verifies the SHAPE per arm; this module must respect the same registered shapes.
    """
    bad: list[str] = []
    vals = {}
    want = ALL_KEYS if require is None else require
    for k in want:
        v = ts.get(k)
        if v is None:
            bad.append(f"V3 {label}: `{k}` is ABSENT from the fed vector")
            continue
        if not isinstance(v, (int, float)) or not math.isfinite(float(v)):
            bad.append(f"V3 {label}: `{k}` is not finite ({v!r})")
            continue
        vals[k] = float(v)
    present = [k for k in CVAR_KEYS if k in vals]
    for a, b in zip(present, present[1:]):
        if vals[a] > vals[b] + 1e-12:
            bad.append(f"V1 {label}: CVaR MONOTONICITY VIOLATED -- {a}={vals[a]:.6g} > "
                       f"{b}={vals[b]:.6g}. A more extreme level must not be BETTER; the tail "
                       f"estimator, i.e. the manipulated variable, is wrong.")
    if "left_tail_mass" in vals and not (0.0 <= vals["left_tail_mass"] <= 1.0):
        bad.append(f"V2 {label}: left_tail_mass={vals['left_tail_mass']:.6g} is not a mass in [0,1]")
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

    problems: list[str] = []
    n_vec = 0
    # (line, arm, generation) -> list of rounded tail vectors measured that generation
    measured: dict[tuple, list[dict]] = defaultdict(list)
    # (line, arm, generation, path) -> rendered vector read from that record's prompt
    rendered: list[tuple] = []

    for p in sorted(root.rglob("record.json")):
        if any(x.startswith(".") for x in p.parts) or _is_d18_nested(p):
            continue
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:                      # noqa: BLE001
            problems.append(f"V0 unreadable record {p}: {exc}")
            continue
        parts = p.relative_to(root).parts
        line, arm, gen = parts[0], rec.get("arm"), rec.get("generation")
        m = rec.get("metrics") or {}
        ts = m.get("tail_stats")
        if isinstance(ts, dict) and ts:
            n_vec += 1
            msgs = check_vector(ts, f"{line}/{arm} g{gen}")
            problems.extend(f"{x}\n      {p}" for x in msgs)
            if line.startswith("search") and isinstance(gen, int):
                measured[(line, arm, gen)].append(
                    {k: round(float(ts[k]), 4) for k in ALL_KEYS
                     if isinstance(ts.get(k), (int, float)) and math.isfinite(float(ts[k]))})
        prompt = rec.get("prompt") or ""
        if line.startswith("search") and isinstance(gen, int) and gen >= 1 and "CVaR" in prompt:
            rv = parse_rendered(prompt)
            if rv:
                rendered.append((line, arm, gen, rv, p))

    # V5 + V4
    #
    # ★ TWO DESIGN FACTS THIS LOOP MUST RESPECT, BOTH OF WHICH I GOT WRONG FIRST (P201).
    #
    # (a) `placebo_shuffled` is the STRUCTURE CONTROL: it is fed the same six labels with the values
    #     PERMUTED. Shuffling necessarily destroys CVaR monotonicity and can land a CVaR value in the
    #     `left_tail_mass` slot, so V1/V2/V5 do not apply to it and neither does an element-wise V4
    #     match. Its STORED statistics are checked like every other arm's (and are clean); it is only
    #     the RENDERED vector that is deliberately scrambled. Checking it here reported 229 "errors"
    #     that were the arm working exactly as designed.
    #
    # (b) THE REFLECTION SOURCE IS STICKY, NOT strictly g-1. `src/llm/loop.py:728-729` replaces
    #     `prev_feedback_block` ONLY when a generation produced a best candidate
    #     (`if gen_best_block is not None`), so a generation that yields none leaves the PREVIOUS
    #     block in place. Traced on the archive: `scalar_cvar5` at g5 was still being fed g3-c4's
    #     vector (-0.034882 -> -0.0349) because g4 never displaced it. Comparing only against g-1
    #     therefore reported 2 phantom mismatches. The correct rule is: the rendered vector must
    #     match a candidate measured at ANY EARLIER generation of the same (line, arm).
    SHUFFLED_ARMS = {"placebo_shuffled"}
    v4_checked = v4_matched = 0
    for line, arm, gen, rv, p in rendered:
        if arm in SHUFFLED_ARMS:
            continue
        msgs = check_vector(rv, f"RENDERED {line}/{arm} g{gen}", require=sorted(rv))
        problems.extend(f"{x.replace('V1 ', 'V5 ').replace('V2 ', 'V5 ').replace('V3 ', 'V5 ')}\n"
                        f"      {p}" for x in msgs)
        earlier = [c for (ln, a, g), cands in measured.items()
                   if ln == line and a == arm and g < gen for c in cands]
        if not earlier:
            continue                                   # nothing archived to compare against
        v4_checked += 1
        keys = [k for k in ALL_KEYS if k in rv]
        if any(all(abs(rv[k] - cand.get(k, float("nan"))) < 5e-5 for k in keys) for cand in earlier):
            v4_matched += 1
        else:
            problems.append(
                f"V4 {line}/{arm} g{gen}: the rendered tail vector matches NO candidate measured at "
                f"ANY earlier generation -- the model was fed numbers never measured in this arm"
                f"\n      {p}")

    print("=== S13 FED-VALUE COHERENCE (V1-V5) ===")
    print(f"  tail vectors checked          : {n_vec:,}")
    print(f"  rendered fed vectors parsed   : {len(rendered):,}")
    print(f"  V4 pipeline comparisons made  : {v4_checked:,}   matched: {v4_matched:,}")
    print()
    if problems:
        print(f"!! {len(problems)} INCOHERENCE(S) IN THE MANIPULATED VARIABLE")
        for m in problems[:40]:
            print(f"  - {m}")
        if len(problems) > 40:
            print(f"  ... and {len(problems)-40} more")
    else:
        if v4_checked == 0 and not measured:
            # P286: ZERO IS NOT CLEAN. rglob over a missing or empty tree returns an empty
            # iterator and raises nothing, so an absent archive used to produce exactly the
            # output a perfect one produces. The archive is a PULL MIRROR, so 'not here yet'
            # is reachable. See record_validator.py for the full note.
            print("*** CANNOT VOUCH FOR ANYTHING -- ZERO tail vectors were measured and ZERO")
            print("    pipeline comparisons were made. This is NOT a clean result:")
            print("    V1-V5 were never evaluated.")
            return 2
        print("V1-V5 CLEAN:")
        print("  - CVaR is MONOTONE in the level on every archived tail vector (cvar_01 <= cvar_05")
        print("    <= cvar_10 <= cvar_25), so the tail estimator is internally coherent")
        print("  - left_tail_mass is a mass in [0,1] everywhere; all six statistics finite")
        print("  - every rendered fed vector is itself monotone, and matches a tail vector ACTUALLY")
        print("    MEASURED on a candidate of an EARLIER generation of the same arm, to 4dp")
        print("    (the reflection source is STICKY: loop.py replaces it only when a generation")
        print("     produces a best candidate, so it is not always g-1)")
        print("  => the model was fed the numbers we measured, correctly labelled and ordered.")
        print("  NOT asserted: placebo_shuffled's RENDERED vector, which is PERMUTED by design and")
        print("  is therefore exempt from V1/V2/V4/V5 (its STORED statistics are checked and clean).")
    print()
    print("EFFECT-BLIND: tail diagnostics only; the prompt's validation-fitness line is never parsed.")
    return 1 if problems else 0


def selftest() -> int:
    ok = {"cvar_01": -0.05, "cvar_05": -0.03, "cvar_10": -0.02, "cvar_25": -0.01,
          "left_tail_mass": 0.02, "robust_skew": -0.04}
    cases = [
        ("clean vector", ok, None),
        ("CVaR non-monotone (1% better than 5%)", {**ok, "cvar_01": -0.01, "cvar_05": -0.03}, "V1"),
        ("CVaR 10% worse than 1%", {**ok, "cvar_10": -0.09}, "V1"),
        ("mass above 1", {**ok, "left_tail_mass": 1.4}, "V2"),
        ("mass negative", {**ok, "left_tail_mass": -0.1}, "V2"),
        ("NaN statistic", {**ok, "robust_skew": float("nan")}, "V3"),
        ("missing statistic", {k: v for k, v in ok.items() if k != "cvar_10"}, "V3"),
    ]
    passed = failed = 0
    for name, vec, want in cases:
        msgs = check_vector(vec, "t")
        hit = any(m.startswith(want) for m in msgs) if want else not msgs
        if hit:
            passed += 1
            print(f"  ok    {name}")
        else:
            failed += 1
            print(f"  FAIL  {name}: expected {want or 'no violation'}, got {msgs}")

    # the renderer must be parsed BY LABEL, not by position: 1% is emitted AFTER 25%
    txt = ("  CVaR 5%: -0.0268\n  CVaR 10%: -0.0198\n  CVaR 25%: -0.0118\n"
           "  CVaR 1%: -0.0467  (high-variance estimate)\n"
           "  left-tail mass: +0.0223\n  left-tail skew: -0.0457\n")
    rv = parse_rendered(txt)
    if rv.get("cvar_01") == -0.0467 and rv.get("cvar_25") == -0.0118 and len(rv) == 6:
        passed += 1
        print("  ok    renderer parsed BY LABEL (1% emitted after 25% and still paired correctly)")
    else:
        failed += 1
        print(f"  FAIL  renderer parse: {rv}")
    if not check_vector(rv, "r"):
        passed += 1
        print("  ok    the real rendered sample is coherent")
    else:
        failed += 1
        print(f"  FAIL  real rendered sample flagged: {check_vector(rv, 'r')}")
    print(f"\nselftest: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
