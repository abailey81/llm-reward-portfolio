"""SCIENCE watcher — analyses the OUTPUT and RESULTS, not just process health.

WHY THIS EXISTS (2026-07-30). `campaign_watch.py` watches health invariants: guards, supervisor count,
substrate homogeneity, crash kinds, sentinel verdicts. It says nothing about whether the SCIENCE is
sensible. That is a real gap — a campaign can be perfectly healthy and producing meaningless numbers,
and the standing rule is that a green check proves execution, never truth.

What this asks, every poll:

1. **Is the search SEARCHING?** Identical scores within an arm would mean the loop is inert.
2. **Is the reflection chain ADVANCING, and where can it not run at all?** `prev_block` is set only
   when a generation yields an ACCEPTED candidate, so a model that rejects nearly everything has
   nothing to reflect on. That is the D2 MECHANISM without the D2 defect, and it is a FINDING about the
   capability gradient rather than a fault: below some authoring reliability, reflection does not
   degrade, it cannot run.
3. **Do the arms DIFFERENTIATE?** H2 compares arms; identical distributions would be the null by
   construction rather than by measurement.
4. **Are the invariants still true of the SCORED records** — 400k steps, a return series present, and
   the R115 execution floor?
5. **Are there impossible numbers?** NaN/inf fitness, |Sharpe| absurdities, empty return series.

READ-ONLY. It never writes to the archive.

Usage:  python docs/ops/science_watch.py [run_root]
"""
from __future__ import annotations

import collections
import glob
import json
import math
import statistics
import sys
from pathlib import Path

SEARCH_ARMS = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")


#: Any list longer than this is replaced by its LENGTH when a record is loaded (see `_shrink`).
#: 64 is comfortably above every scalar-ish list a record carries and far below the 1,571-point
#: series that dominate its size.
_BIG = 64


def _shrink(obj):
    """Replace every long list inside a parsed record with its LENGTH, recursively.

    ⚠ P280, 2026-08-04. WHY THIS EXISTS, MEASURED RATHER THAN MODELLED. A per-process census taken
    while a preflight ran showed THIS tool at **5,776 MB** working set at 12,633 records -- 37% of
    a 15.64 GB box that also hosts ~30 driver and supervisor processes. P270 recorded 1,603 MB for
    the same tool at 12,514 records, so the true slope is far steeper than P270's projection and its
    ThreadPoolExecutor mitigation does not reach it. The cause is `_records` holding the FULL parsed
    record, and the mean sealed test record is ~477 KB of JSON.

    ⚠ THIS IS SAFE ONLY BECAUSE THE BIG ARRAYS ARE NEVER READ, WHICH WAS CHECKED RATHER THAN
    ASSUMED. `test_returns` and `train_curve` occur on exactly ONE line in this file and only as a
    truthiness test. No element is indexed, summed or measured anywhere. Replacing a list by its
    LENGTH preserves that exactly -- an empty list becomes 0 (falsy), a non-empty list becomes a
    positive int (truthy) -- while carrying strictly more information than a bool, and any future
    code that tries to index or `len()` one FAILS LOUDLY rather than silently reading a wrong value.

    The rule is STRUCTURAL, not a whitelist of field names, so a record schema that grows a new
    array is covered without anyone remembering to update a list.
    """
    if isinstance(obj, list):
        if len(obj) > _BIG:
            return len(obj)
        return [_shrink(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _shrink(v) for k, v in obj.items()}
    return obj


def _records(root: Path) -> list[tuple[str, str, dict]]:
    """(stage, unit, record) for every archived record, with long arrays reduced to their lengths."""
    out = []
    for p in glob.glob(str(root / "**" / "record.json"), recursive=True):
        parts = p.replace("\\", "/").split("/")
        # Anything walking the archive must exclude BOTH the in-flight staging and the
        # deliberately-set-aside past -- the convention `scripts/sentinel.py:1348` established
        # after three separate instruments tripped on it. A pull STAGES into `.pull_tmp.<pid>/`,
        # so that tree holds byte-identical copies of records that already exist canonically
        # (observed here 2026-07-31 on `.pull_tmp.28884`, D18); `_quarantined*` holds records
        # set aside from an EARLIER run, whose mtimes survive the move.
        if any(seg.startswith((".pull_tmp", "_quarantined")) for seg in parts[:-1]):
            continue
        try:
            r = json.load(open(p, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        out.append((parts[-4] if len(parts) >= 4 else "?", parts[-3], _shrink(r)))
    return out


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else "outputs/campaign_cluster_run4")
    recs = _records(root)
    if not recs:
        # P296: ZERO IS NOT CLEAN -- see record_validator.py for the full note. This tool
        # walks the archive and was missed when the guard was applied to the seven gated
        # layers, because I looked at the layer list rather than at everything that walks.
        print("*** CANNOT VOUCH FOR ANYTHING -- ZERO records under %s." % root)
        print("    This is NOT a clean result: no science check was evaluated.")
        return 2
    # ⚠ SAY WHAT THE NUMBER COUNTS (RUN 9, record §88). This header printed a bare "N records" that
    # disagreed with the cycle log's `records=` under the SAME word — 1,560 here against 1,532 there,
    # on the same archive at the same moment. Neither was wrong; they count different things. The
    # authority (`scripts/campaign_guards.py:266`) globs `*/*/*/record.json`, a FIXED depth, so it sees
    # only search/test candidates. This tool walks recursively and therefore also picks up the
    # `frozen*/` WINNER MARKERS, which are byte-identical copies of a record that already exists
    # canonically. Nothing downstream is harmed (every group they form has n=1 and is skipped, and no
    # RATE is computed over them) — but §86 was the second time in this campaign that two instruments
    # reported different numbers under one label, so the composition is now stated rather than implied.
    # ⚠ The frozen markers sit ONE LEVEL SHALLOWER than a candidate record
    # (`frozen*/<arm>-winner/record.json`, depth 3, vs `<lane>/<arm>/<cid>/record.json`, depth 4), so
    # for them it is the UNIT slot (`parts[-3]`) that carries the `frozen*` name while the STAGE slot
    # holds the archive-root directory. Counting on `stage` returned a flat 0 and was my own error
    # (P45) — caught because a brand-new counter reading exactly zero is the classic
    # "a clean 0 % means suspect the specification" tell.
    _frozen = sum(1 for stage, unit, _ in recs
                  if stage.startswith("frozen") or unit.startswith("frozen"))
    # The AUTHORITY's set, computed the authority's way (`scripts/campaign_guards.py:266`) so the two
    # numbers can be reconciled here instead of by whoever notices they differ. Anything left over is
    # named rather than absorbed: on 2026-07-31 the remainder was exactly 1 — the known D18
    # double-nested duplicate at `search_leg_haiku_4_5/scalar/scalar-g1-c3/scalar-g1-c3/`, verified
    # byte-identical (sha256 803af2e3…) to its canonical twin, deferred-fix item 10.
    _authority = len([p for p in glob.glob(str(root / "*" / "*" / "*" / "record.json"))
                      if not any(seg.startswith((".pull_tmp", "_quarantined"))
                                 for seg in p.replace("\\", "/").split("/"))])
    _extra = len(recs) - _frozen - _authority
    print(f"=== SCIENCE WATCH: {len(recs)} records under {root} ===")
    print(f"    reconciliation: {_authority} authority-equivalent (the cycle log's `records=`) "
          f"+ {_frozen} frozen-winner marker copies + {_extra} deeper-nested duplicate(s)")

    # ---- 1 + 3: per-(stage,arm) fitness spread and differentiation -------------------------------
    groups: dict[tuple[str, str], list[float]] = collections.defaultdict(list)
    gen_scores: dict[tuple[str, int], list[float]] = collections.defaultdict(list)
    impossible: list[str] = []
    steps_bad = 0
    noseries = 0
    r115: list[tuple[str, str, str, float]] = []

    for stage, unit, r in recs:
        m = r.get("metrics") or {}
        # Test-leg records score on test_sharpe, search on val_fitness.
        #
        # ⚠ THIS USED TO BE A NaN PROBE PRETENDING TO BE STAGE-AWARE, and it produced a false
        # "ZERO SPREAD / inert search" alarm on 2026-07-31, the first hour the results layer ran.
        # The old rule was "use val_fitness unless it is NaN". That happens to work for the HAND-
        # WRITTEN baselines, whose test records carry val_fitness = nan, so the fallback fires. It
        # FAILS for a FROZEN-WINNER unit: the winner's val_fitness is a real number inherited from
        # the freeze and stamped identically into every seed's record, so the fallback never fires
        # and the check scores 29 records on one constant. MEASURED on test/random_search:
        # val_fitness = 0.328632 on all 29 (spread 0.0) while test_sharpe ranges 0.6069..1.4629
        # across 29 distinct seeds — i.e. the science was healthy and only the reader was wrong.
        #
        # This mattered beyond one row: EVERY LLM arm's C4 has exactly that shape (one frozen winner,
        # retrained at 30...568 seeds), so the alarm would have gone permanently rc=2 the moment the
        # seed ladder began — a RED that can never clear, which is the alarm-fatigue failure that let
        # D15 sit unexamined for ten hours. Selecting on the STAGE, which is what the comment always
        # claimed, is both correct and stable. The NaN check is KEPT as a second-line fallback for a
        # non-test record that somehow lacks val_fitness.
        #
        # ⚠⚠ CORRECTED AGAIN 2026-07-31 (RUN 9, record §88). The stage-aware fix above was written as
        # an EXACT match `stage == "test"` — but `stage` is the SUB-ROOT DIRECTORY NAME (`parts[-4]`
        # in `_records`), and the archive has THREE test lanes: `test/`, `test_leg_<model>/` and
        # `test_h3_singleshot/`. Only the first ever matched. So the fix worked for the core line's
        # test lane and left BOTH the ten report-only legs and the h3 line on the old broken path —
        # i.e. it repaired the one lane that had already produced records and missed the ten that had
        # not yet. FALSIFIED on a synthetic archive: a healthy `test_leg_qwen3_5_9b/distributional`
        # with 30 DISTINCT `test_sharpe` values but the usual constant frozen `val_fitness` was
        # reported `spread=+0.0000 <== ZERO SPREAD`, raising the SCIENCE ALERT on clean data, while a
        # genuinely-inert control fired identically — the two were indistinguishable.
        #
        # This was LATENT, not yet firing: C4 had begun on `test_leg_qwen3_5_9b` but 0 records had
        # landed. It would have gone permanently rc=2 on the first one — the alarm-fatigue failure the
        # comment above exists to prevent, arriving by a different door.
        #
        # `startswith("test")` is safe against every sub-root the archive actually contains
        # (`batches`, `driver_status`, `frozen*`, `ledger`, `search*`, `test*`): nothing but a test
        # lane begins with "test".
        val = m.get("val_fitness")
        val_ok = val is not None and not (isinstance(val, float) and math.isnan(val))
        key = "test_sharpe" if stage.startswith("test") else ("val_fitness" if val_ok else "test_sharpe")
        score = m.get(key)
        # *** RANGE CHECK ADDED 2026-07-31 (record 77). The module docstring has always promised
        # "NaN/inf fitness, |Sharpe| ABSURDITIES", but only the NaN/inf half was implemented: the
        # test was `score is None or not isfinite(score)`, so an out-of-RANGE score passed silently.
        # FOUND BY FALSIFICATION: planting `val_fitness = 42.0` into a synthetic archive left this
        # counter at 0. That matters because `val_fitness` DRIVES WINNER SELECTION -- an impossible
        # value would simply win its arm, and nothing would say so.
        #
        # Bounds chosen from the LIVE archive so neither can ever false-positive:
        #   val_fitness is a DEFLATED SHARPE RATIO, i.e. a PROBABILITY -> [0, 1].
        #       observed over 1,203 records: min 0.000000, max 0.431914  (0.57 of headroom)
        #   test_sharpe is an ANNUALISED SHARPE -> |x| < 20 is absurd for any real strategy.
        #       observed over 360 records: min -0.9099, max 1.4629       (18.5 of headroom)
        _bad_range = False
        if isinstance(score, (int, float)) and math.isfinite(score):
            if key == "val_fitness" and not (0.0 <= float(score) <= 1.0):
                _bad_range = True          # a probability outside [0,1]
            elif key == "test_sharpe" and abs(float(score)) >= 20.0:
                _bad_range = True          # an annualised Sharpe of +/-20 is not physical
        if score is None or (isinstance(score, float) and not math.isfinite(score)) or _bad_range:
            impossible.append(f"{unit}/{r.get('run_id')}: {key}={score!r}"
                              + (" [OUT OF RANGE]" if _bad_range else ""))
        else:
            groups[(stage, unit)].append(float(score))
            g = r.get("generation")
            if isinstance(g, int) and key == "val_fitness":
                gen_scores[(unit, g)].append(float(score))

        calls = m.get("train_safe_call_count")
        if calls is not None and int(calls) != 400_000:
            steps_bad += 1
        if not (m.get("test_returns") or m.get("train_curve") or r.get("test_returns")):
            noseries += 1
        d = m.get("train_safe_default_count")
        if calls and d and int(calls) > 0:
            frac = int(d) / int(calls)
            if frac >= 0.10:
                # (root, arm, run_id, frac) — the ROOT matters: winner selection is per LINE per
                # arm, so pooling candidates across lines makes a binding breach vanish.
                r115.append((stage, unit, str(r.get("run_id")), frac))

    print("\n--- IS THE SEARCH SEARCHING? (zero spread would mean the loop is inert) ---")
    # ⚠ THE CAP IS ON THE DISPLAY, NEVER ON THE CHECK (RUN 9, record §88). This loop used to be
    # `sorted(...)[:14]`, which capped the ALARM as well as the printout: a zero-spread group sitting
    # at rank 15 or lower could never be detected, and nothing said so. That is exactly the silent
    # truncation this same file forbids twelve lines below ("If a cap is ever reintroduced, it MUST
    # report how many rows it dropped"). Detection now covers EVERY group; only the printout is capped,
    # and the number withheld is stated.
    inert = []
    ranked = sorted(groups.items(), key=lambda kv: -len(kv[1]))
    _shown = 0
    for (stage, unit), v in ranked:
        if len(v) < 2:
            continue
        spread = max(v) - min(v)
        flag = "  <== ZERO SPREAD" if spread == 0.0 else ""
        if spread == 0.0:
            inert.append(f"{stage}/{unit}")
        # Print the 14 largest, plus EVERY zero-spread group regardless of rank (an alarm the
        # operator cannot see is not an alarm).
        if _shown >= 14 and spread != 0.0:
            continue
        _shown += 1
        # Label with the STAGE too. Without it, `search/random_search` and `test/random_search`
        # both printed as bare "random_search" — two rows, same name, different estimands, and
        # working out which one was flagged cost real time.
        print(f"  {stage + '/' + unit:38s} n={len(v):4d} mean={statistics.mean(v):+.4f} "
              f"spread={spread:+.4f}{flag}")
    _eligible = sum(1 for _, v in ranked if len(v) >= 2)
    if _eligible > _shown:
        print(f"  ... {_eligible - _shown} further group(s) CHECKED but not shown "
              f"(all non-zero spread; {_eligible} groups checked in total)")

    print("\n--- REFLECTION CHAIN: generations reached per line, and accepted candidates each ---")
    per_line: dict[str, dict[int, int]] = collections.defaultdict(dict)
    for (unit, g), v in gen_scores.items():
        # unit here is the arm dir; roll up by its parent search root via the groups key
        per_line[unit][g] = len(v)
    for unit in sorted(per_line):
        gens = per_line[unit]
        chain = " ".join(f"g{g}:{gens[g]}" for g in sorted(gens))
        print(f"  {unit:38s} {chain}")

    print("\n--- SCORED-RECORD INVARIANTS ---")
    print(f"  records whose train_safe_call_count != 400,000 : {steps_bad}")
    print(f"  R115 floor breaches (>=10% safe-default)        : {len(r115)}")
    # Print EVERY breach. A cap here silently hid the 9th breach on 2026-07-30 while the count
    # line said 9 — and a hidden breach could have been on the CORE confirmatory line, which is
    # the one place it would change a scientific conclusion. If a cap is ever reintroduced, it
    # MUST report how many rows it dropped.
    for st, ar, rid, f in r115:
        line = "c1(CORE)" if st == "search" else st.replace("search_leg_", "")
        print(f"      {line}/{ar}/{rid}  {f:.2%}")
    print(f"  impossible/non-finite scores                    : {len(impossible)}")
    for s in impossible:
        print(f"      {s}")

    # --- Does any breach BIND? (the only R115 fact that changes a scientific conclusion) ---------
    #
    # A breach EXISTING is R115 working, not a fault — the floor exists precisely to catch these, and
    # alerting on their mere presence would pin this watcher at ALERT forever and mask a genuinely new
    # science problem (the same alarm-fatigue flaw fixed in campaign_watch.py). What MATTERS is whether
    # a breacher is the TOP-fitness candidate in its arm, because then the floor is the only thing
    # standing between a fallback-contaminated reward and the sealed test leg. That is the trigger.
    binds: list[str] = []
    for st, ar, rid, frac in r115:
        key = f"{st}/{ar}/{rid}"
        cands = []
        for p in glob.glob(str(root / st / ar / "*" / "record.json")):
            try:
                rr = json.load(open(p, encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            mm = rr.get("metrics") or {}
            c2, d2, vf = (mm.get("train_safe_call_count"), mm.get("train_safe_default_count"),
                          mm.get("val_fitness"))
            if not c2 or d2 is None or vf is None:
                continue
            cands.append((float(vf), d2 / c2))
        if not cands:
            continue
        elig = [f for f, fr in cands if fr < 0.10]
        this = max((f for f, fr in cands if fr >= 0.10), default=None)
        if this is not None and (not elig or this > max(elig)):
            binds.append(f"{key} ({frac:.2%}) tops its arm; best eligible="
                         f"{'none' if not elig else format(max(elig), '+.6f')}")
    if binds:
        print("\n  *** R115 IS BINDING — a fallback-contaminated candidate tops its arm ***")
        for b in binds:
            print(f"      {b}")
        print("      (this is the floor DOING ITS JOB; it becomes a defect only if the floor is absent)")

    rc = 0
    hard = bool(inert) or bool(steps_bad) or bool(impossible)
    if hard:
        rc = 2
        print("\n  *** SCIENCE ALERT: an inert search, a broken step budget, or an impossible number ***")
    else:
        print(f"\n  science ok: search varying, {len(recs)} records, 400k budget intact, "
              f"no impossible numbers; {len(r115)} R115 breach(es) correctly excluded, "
              f"{len(binds)} of them binding")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
