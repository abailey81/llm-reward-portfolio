"""SEARCH-TIER INTEGRITY -- the half A60-A73 did not cover.

A60-A65 swept the TEST tier (realised series, endpoints, archive replay). The SEARCH tier
carries three things nothing has audited for CONTENT:

  Q1 val_returns    -- the validation series SELECTION is computed on. Length, finiteness,
                       degeneracy.
  Q2 within-arm distinctness -- if two candidates of one arm produce a BYTE-IDENTICAL
                       validation series they are INDISTINGUISHABLE to `max(val_fitness)`,
                       and the winner between them is decided by nothing.
  Q3 cross-arm collision -- two different reward programs yielding an identical validation
                       series means the reward did not influence the policy, or a spec was
                       wired twice. The search-tier analogue of A60's Q2.
  Q4 val_fitness    -- the selection statistic itself: present? finite? R115 filters on
                       execution and then takes `max(val_fitness)` among the eligible, so a
                       missing or non-finite value silently changes who wins.
  Q5 reward_source  -- does every archived program still PARSE? They passed the AST gate at
                       authoring time; an archived program that no longer parses cannot be
                       replayed, which breaks reproducibility layer 1 for the search stage.
  Q6 generation vs feedback -- A9 found 3 candidates at generation >= 1 whose prompt is the
                       generation-0 initial prompt (a designed fallback when a generation
                       yields no accepted candidate). Re-measured at full scale.

EFFECT-BLIND: val_fitness is the SEARCH-stage SELECTION statistic, not a sealed outcome
(s3's P131: it is NaN by design on test records). Only PRESENCE and FINITENESS are read --
no value, no ranking, no arm aggregate, no contrast.

Read-only.  python docs/analysis/search_integrity.py [--selftest]
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARCHIVE = REPO / "outputs" / "campaign_cluster_run4"
#: A9: the generation-0 initial prompt carries no reflection block. Any prompt lacking a
#: feedback marker at generation >= 1 is an un-fed candidate.
FEEDBACK_MARKERS = ("reference value", "feedback", "previous", "Reference value")

#: Cross-arm val_returns collisions already MEASURED, EXPLAINED and DISCLOSED. Still printed
#: every run, but they do not set CRITICAL — an instrument that reads CRITICAL forever on a
#: known condition hides the next one (coord's W4 alarm-saturation lesson).
#: ⚠ An entry here asserts the collision is UNDERSTOOD, not that it is convenient.
ACKNOWLEDGED_COLLISIONS = {
    # A74 (2026-08-01): nemotron placebo-g0-c0 vs scalar-g0-c1. Both programs read first-hand
    # and are NUMERICALLY IDENTICAL — online mean/var accumulator, then
    # mean/(sqrt(var)+eps) - 0.001*0.5*sum|w-w_prev|, same eps, same coefficients. Different
    # source, different hash, same computation ⇒ identical policy ⇒ identical series.
    "4515b355cb1f1d98",
}


def digest(seq) -> str:
    h = hashlib.sha256()
    for v in seq:
        h.update(repr(float(v)).encode())
    return h.hexdigest()[:16]


def scan(root: Path) -> dict:
    recs = []
    nested_divergent: list[str] = []
    for p in root.rglob("record.json"):
        rel = p.relative_to(root)
        if rel.parts[0].startswith(".pull_tmp") or not rel.parts[0].startswith("search"):
            continue
        if "_env" in rel.parts:
            continue
        # A3's two DOUBLE-NESTED duplicates live at <arm>/<cand>/<cand>/record.json (a
        # TOCTOU race in poll.pull_archive). They are byte-identical copies of their outer
        # sibling, so counting them as records fabricates a "duplicate series" in Q2/Q3. The
        # authority depth for a search record is search*/<arm>/<cand>/record.json = 4 parts.
        #
        # ⚠ BUT SKIPPING THEM OUTRIGHT WAS A FALSE NEGATIVE (suppression_audit.py, S4): A3
        # established they are byte-identical TODAY. A nested duplicate whose content DIVERGED
        # from its outer sibling would be real corruption, and the skip made it invisible.
        # So: exclude them from the record set, but VERIFY each one against its sibling and
        # record a violation if it differs.
        if len(rel.parts) != 4:
            if len(rel.parts) == 5 and rel.parts[2] == rel.parts[3]:
                outer = p.parent.parent / "record.json"
                try:
                    same = (outer.read_bytes().replace(b"\r\n", b"\n")
                            == p.read_bytes().replace(b"\r\n", b"\n"))
                except OSError:
                    same = False
                if not same:
                    nested_divergent.append(str(rel))
            continue
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        arm = f"{rel.parts[0]}/{rel.parts[1]}" if len(rel.parts) >= 2 else rel.parts[0]
        m = r.get("metrics") or {}
        vr = m.get("val_returns")
        if not isinstance(vr, list):
            vr = r.get("val_returns")
        entry = {
            "rel": str(rel), "arm": arm, "cand": rel.parts[2] if len(rel.parts) > 2 else "?",
            "gen": r.get("generation"),
            "vr_n": len(vr) if isinstance(vr, list) else None,
            "vr_bad": None, "vr_const": None, "vr_digest": None,
            "vf_present": "val_fitness" in m,
            "vf_finite": None,
            "src": r.get("reward_source") or "",
            "prompt": r.get("prompt") or "",
        }
        if isinstance(vr, list) and vr:
            vals = []
            bad = 0
            for v in vr:
                try:
                    f = float(v)
                except (TypeError, ValueError):
                    bad += 1
                    continue
                if not math.isfinite(f):
                    bad += 1
                    continue
                vals.append(f)
            entry["vr_bad"] = bad
            entry["vr_const"] = bool(vals) and (min(vals) == max(vals))
            entry["vr_digest"] = digest(vr)
        if entry["vf_present"]:
            try:
                entry["vf_finite"] = math.isfinite(float(m["val_fitness"]))
            except (TypeError, ValueError):
                entry["vf_finite"] = False
        recs.append(entry)
    return {"recs": recs, "nested_divergent": nested_divergent}


def report(res: dict) -> int:
    recs = res["recs"]
    rc = 0
    print(f"=== SEARCH-TIER INTEGRITY over {len(recs)} search records ===")

    # Q0 -- the nested duplicates are EXCLUDED from the record set (they are A3's TOCTOU
    # copies) but they are still CHECKED: a nested copy that DIVERGED from its outer sibling
    # is corruption, not a known artefact. Skipping them outright was a false negative (S4).
    nd = res.get("nested_divergent") or []
    if nd:
        rc = 2
        print(f"\n!! Q0 NESTED DUPLICATE WITH DIVERGENT CONTENT: {len(nd)}")
        for x in nd[:10]:
            print(f"     {x}")
    else:
        print("Q0 nested duplicates: byte-identical to their outer sibling (or none present)")

    # ---- Q1 val_returns shape -------------------------------------------------------
    have = [r for r in recs if r["vr_digest"]]
    lens = Counter(r["vr_n"] for r in have)
    print(f"\nQ1 val_returns present on {len(have)}/{len(recs)}; lengths {dict(lens)}")
    bad = [r for r in have if r["vr_bad"]]
    const = [r for r in have if r["vr_const"]]
    if bad:
        rc = 2
        print(f"   !! NON-FINITE in {len(bad)} record(s):")
        for r in bad[:10]:
            print(f"      {r['rel']}  bad={r['vr_bad']}")
    else:
        print("   finiteness OK")
    if const:
        rc = max(rc, 1)
        print(f"   ! DEGENERATE (zero-variance) validation series in {len(const)}:")
        for r in const[:10]:
            print(f"      {r['rel']}")
    else:
        print("   no zero-variance validation series")

    # ---- Q2 within-arm distinctness -------------------------------------------------
    by_arm: defaultdict[str, defaultdict[str, list]] = defaultdict(lambda: defaultdict(list))
    for r in have:
        by_arm[r["arm"]][r["vr_digest"]].append(r["cand"])
    dups = {a: {d: c for d, c in dd.items() if len(c) > 1} for a, dd in by_arm.items()}
    dups = {a: d for a, d in dups.items() if d}
    print(f"\nQ2 within-arm identical validation series: "
          f"{'NONE — every candidate distinguishable to selection' if not dups else ''}")
    if dups:
        rc = 2
        for a, dd in list(dups.items())[:15]:
            for d, cands in list(dd.items())[:3]:
                print(f"   !! {a}: {len(cands)} candidates share a series -> {cands[:6]}")

    # ---- Q3 cross-arm collision -----------------------------------------------------
    by_digest: defaultdict[str, set] = defaultdict(set)
    for r in have:
        by_digest[r["vr_digest"]].add(r["arm"])
    cross = {d: a for d, a in by_digest.items() if len(a) > 1}
    new_cross = {d: a for d, a in cross.items() if d not in ACKNOWLEDGED_COLLISIONS}
    print(f"Q3 cross-arm identical validation series: "
          f"{'NONE' if not cross else f'{len(cross)} collision(s), {len(new_cross)} NEW'}")
    for d, arms in list(cross.items())[:10]:
        tag = "  *** NEW ***" if d in new_cross else "  [known: A74, functional duplicate]"
        print(f"   {'!!' if d in new_cross else '  '} digest {d} spans {sorted(arms)}{tag}")
    if new_cross:
        rc = 2

    # ---- Q4 val_fitness -------------------------------------------------------------
    missing = [r for r in recs if not r["vf_present"]]
    nonfin = [r for r in recs if r["vf_present"] and r["vf_finite"] is False]
    print(f"\nQ4 val_fitness: present {len(recs)-len(missing)}/{len(recs)}, "
          f"non-finite {len(nonfin)}")
    if missing or nonfin:
        rc = max(rc, 1)
        for r in (missing + nonfin)[:12]:
            print(f"   ! {r['rel']}  present={r['vf_present']} finite={r['vf_finite']}")
    else:
        print("   every search record carries a present, finite selection statistic")
    print("   (presence/finiteness only — no value, ranking or aggregate read)")

    # ---- Q5 reward_source parses ----------------------------------------------------
    unparseable, empty = [], []
    for r in recs:
        s = r["src"]
        if not s.strip():
            empty.append(r)
            continue
        try:
            ast.parse(s)
        except SyntaxError as exc:
            unparseable.append((r["rel"], str(exc)[:70]))
    print(f"\nQ5 reward_source: {len(recs)-len(empty)}/{len(recs)} non-empty; "
          f"{len(unparseable)} fail to parse")
    if empty:
        print(f"   ! {len(empty)} record(s) carry an EMPTY reward_source "
              f"(baseline stubs are expected here):")
        for r in empty[:6]:
            print(f"      {r['rel']}")
    if unparseable:
        rc = 2
        for rel, e in unparseable[:10]:
            print(f"   !! {rel}: {e}")
    else:
        print("   every archived program still PARSES — replayable")

    # ---- Q6 generation vs feedback --------------------------------------------------
    unfed = [r for r in recs
             if isinstance(r["gen"], int) and r["gen"] >= 1 and r["prompt"]
             and not any(mk.lower() in r["prompt"].lower() for mk in FEEDBACK_MARKERS)]
    withp = [r for r in recs if r["prompt"]]
    print(f"\nQ6 generation-vs-feedback: {len(withp)}/{len(recs)} records carry a prompt")
    if not withp:
        print("   prompt absent from the archived record schema — A9's check is not")
        print("   reproducible from these records (s3 ran it on the prompt field when present)")
    else:
        gen0 = [r for r in withp if r["gen"] == 0]
        fed0 = [r for r in gen0
                if any(mk.lower() in r["prompt"].lower() for mk in FEEDBACK_MARKERS)]
        print(f"   POSITIVE CONTROL: {len(gen0)} generation-0 records, "
              f"{len(fed0)} of them carry a feedback marker (expect ~0)")
        if gen0 and fed0 == gen0:
            # The gen-0 prompt is the INITIAL prompt and must not look "fed". If every one
            # of them matches, the markers are matching template boilerplate ("you will
            # receive feedback"), so the detector cannot separate fed from un-fed and its
            # un-fed count is meaningless. Writeup's P107 is exactly this failure; s3's A9
            # used a STRUCTURAL prefix/suffix diff precisely because keywords cannot do it.
            print("   !! POSITIVE CONTROL FAILED — every generation-0 prompt matches a")
            print("      'feedback' marker, so these markers match TEMPLATE BOILERPLATE,")
            print("      not the reflection block. THE UN-FED COUNT IS NOT REPORTED:")
            print("      a detector that cannot fail cannot verify. Use s3's A9 structural")
            print("      method (per-arm common prefix/suffix diff), not keywords.")
        else:
            print(f"   un-fed at generation >= 1: {len(unfed)}"
                  f" ({100*len(unfed)/max(1,len(withp)):.2f}% of prompted records)")
            for r in unfed[:10]:
                print(f"      {r['arm']}  g{r['gen']}  {r['cand']}")

    print(f"\n  VERDICT: {'CRITICAL' if rc == 2 else 'REVIEW' if rc == 1 else 'CLEAN'}")
    return rc


def _selftest() -> int:
    import shutil
    import tempfile
    ok = True

    def case(name, cond):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok = ok and cond

    tmp = Path(tempfile.mkdtemp(prefix="searchint_"))
    try:
        def w(arm, cand, vr, vf=0.5, src="def reward(a,b,c,d,e):\n    return 0.0,{},None",
              gen=0, prompt="initial"):
            d = tmp / "search" / arm / cand
            d.mkdir(parents=True)
            (d / "record.json").write_text(json.dumps({
                "generation": gen, "reward_source": src, "prompt": prompt,
                "metrics": {"val_returns": vr, "val_fitness": vf}}), encoding="utf-8")

        w("a", "c0", [0.1, 0.2, 0.3])
        w("a", "c1", [0.4, 0.5, 0.6])
        w("b", "c0", [0.7, 0.8, 0.9])
        r = scan(tmp)
        case("clean fixture SEEN (denominator non-zero)", len(r["recs"]) == 3)
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = report(r)
        case("clean fixture -> CLEAN", rc == 0)

        w("a", "c2", [0.1, 0.2, 0.3])                       # within-arm duplicate
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = report(scan(tmp))
        case("Q2 FIRES on a within-arm identical series",
             "within-arm identical" in buf.getvalue() and rc == 2)

        w("b", "c1", [0.4, 0.5, 0.6])                       # cross-arm collision
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            report(scan(tmp))
        case("Q3 FIRES on a cross-arm collision", "collision(s)" in buf.getvalue())

        w("c", "c0", [1.0, 1.0, 1.0])                       # degenerate
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            report(scan(tmp))
        case("Q1 FIRES on a zero-variance series", "DEGENERATE" in buf.getvalue())

        w("d", "c0", [0.1, float("nan")])                   # non-finite
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            report(scan(tmp))
        case("Q1 FIRES on a non-finite value", "NON-FINITE" in buf.getvalue())

        w("e", "c0", [0.1, 0.2], src="def reward(:\n  bad syntax")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            report(scan(tmp))
        case("Q5 FIRES on an unparseable program", "fail to parse" in buf.getvalue()
             and "1 fail" in buf.getvalue())

        w("f", "c0", [0.1, 0.2], gen=3, prompt="no marker here")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            report(scan(tmp))
        case("Q6 FIRES on an un-fed generation>=1 candidate",
             "un-fed at generation >= 1: 1" in buf.getvalue())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\nselftest: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    raise SystemExit(report(scan(ARCHIVE)))
