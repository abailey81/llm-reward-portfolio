"""THE FULL WINNER IDENTITY CHAIN: search candidate -> frozen marker -> test records.

R9 in record_validator verifies the SECOND link (a test record's reward hash equals its
frozen winner's). *** Nobody has verified the FIRST link. *** The frozen marker is supposed to
be a faithful copy of the winning SEARCH record; if it diverged, the sealed test leg would
have trained a reward that is not the one selection actually chose -- and every downstream
comparison would be about a program no arm ever won with.

The chain, and what each link must satisfy:

  L1  frozen/<arm>-winner.candidate_id  MUST name a real candidate in search*/<arm>/
  L2  frozen marker.reward_source_hash  MUST equal that search record's hash
  L3  frozen marker.reward_source       MUST be byte-identical to it
  L4  the hash MUST equal sha256(the source)              (self-consistency, both ends)
  L5  every test record of that unit    MUST carry the same hash   (= R9, re-checked here so
                                                                    the chain is one object)

Effect-blind: hashes, ids, source bytes. No outcome, no val_fitness, no ranking.

Read-only.  python docs/analysis/winner_chain.py [--selftest]
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARCHIVE = REPO / "outputs" / "campaign_cluster_run4"


def canonical_hash(src: str) -> str:
    return hashlib.sha256(str(src).encode("utf-8")).hexdigest()


def _read(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def scan(root: Path) -> list[dict]:
    out = []
    for fz in sorted(root.glob("frozen*")):
        if not fz.is_dir():
            continue
        sfx = "" if fz.name == "frozen" else fz.name[len("frozen"):]
        search_root = root / f"search{sfx}"
        test_root = root / f"test{sfx}"
        for marker in sorted(fz.glob("*-winner/record.json")):
            arm = marker.parent.name[: -len("-winner")]
            m = _read(marker)
            row = {"line": fz.name, "arm": arm, "violations": []}
            if m is None:
                row["violations"].append("L0 marker unreadable")
                out.append(row)
                continue
            cid = m.get("candidate_id")
            mh = m.get("reward_source_hash")
            msrc = m.get("reward_source") or ""
            row["candidate_id"] = cid

            # L1 -----------------------------------------------------------------------
            cand_rec = None
            if isinstance(cid, str) and cid:
                cand_path = search_root / arm / cid / "record.json"
                if cand_path.is_file():
                    cand_rec = _read(cand_path)
                else:
                    row["violations"].append(
                        f"L1 candidate {cid!r} not found at search{sfx}/{arm}/{cid}")
            else:
                row["violations"].append("L1 marker carries no candidate_id")

            # L2 / L3 ------------------------------------------------------------------
            if cand_rec is not None:
                ch = cand_rec.get("reward_source_hash")
                csrc = cand_rec.get("reward_source") or ""
                if ch != mh:
                    row["violations"].append(
                        f"L2 marker hash {str(mh)[:12]}.. != candidate {str(ch)[:12]}..")
                if csrc != msrc:
                    row["violations"].append(
                        f"L3 marker source differs from the candidate's "
                        f"({len(msrc)} vs {len(csrc)} chars)")

            # L4 -----------------------------------------------------------------------
            if msrc.strip() and isinstance(mh, str) and len(mh) == 64:
                if canonical_hash(msrc) != mh:
                    row["violations"].append("L4 marker hash != sha256(marker source)")

            # L5 -----------------------------------------------------------------------
            unit = test_root / arm
            n_test, mismatched = 0, 0
            if unit.is_dir():
                for tp in unit.glob("*-s*/record.json"):
                    t = _read(tp)
                    if t is None:
                        continue
                    n_test += 1
                    if t.get("reward_source_hash") != mh:
                        mismatched += 1
            row["n_test"] = n_test
            if mismatched:
                row["violations"].append(
                    f"L5 {mismatched}/{n_test} test records carry a DIFFERENT reward hash")
            out.append(row)
    return out


def report(rows: list[dict]) -> int:
    bad = [r for r in rows if r["violations"]]
    print(f"=== WINNER IDENTITY CHAIN over {len(rows)} frozen winners ===")
    print("    search candidate -> frozen marker -> test records\n")
    print(f"  {'line':<26}{'arm':<18}{'candidate':<26}{'n test':>7}  chain")
    for r in sorted(rows, key=lambda r: (r["line"], r["arm"])):
        state = "OK" if not r["violations"] else f"{len(r['violations'])} VIOLATION(S)"
        print(f"  {r['line']:<26}{r['arm']:<18}{str(r.get('candidate_id')):<26}"
              f"{r.get('n_test', 0):>7}  {state}")
        for v in r["violations"]:
            print(f"        !! {v}")
    print(f"\n  winners with an intact chain: {len(rows) - len(bad)}/{len(rows)}")
    if not bad:
        print("  *** EVERY frozen winner is a faithful copy of a real search candidate, its")
        print("      hash matches its own source, and every test record of its unit carries")
        print("      that same hash. The identity chain holds end to end. ***")
    return 2 if bad else 0


def _selftest() -> int:
    import shutil
    import tempfile
    ok = True

    def case(n, c):
        nonlocal ok
        print(f"  [{'PASS' if c else 'FAIL'}] {n}")
        ok = ok and c

    src = "def reward(a,b,c,d,e):\n    return 0.0, {}, None"
    h = canonical_hash(src)
    tmp = Path(tempfile.mkdtemp(prefix="chain_"))
    try:
        def w(rel, **kw):
            d = tmp / rel
            d.mkdir(parents=True, exist_ok=True)
            base = {"run_id": d.name, "arm": "arm", "candidate_id": "arm-g0-c0",
                    "reward_source": src, "reward_source_hash": h}
            base.update(kw)
            (d / "record.json").write_text(json.dumps(base), encoding="utf-8")

        w("search/arm/arm-g0-c0")
        w("frozen/arm-winner", run_id="arm-winner")
        w("test/arm/arm-s0", run_id="arm-s0", candidate_id="arm-g0-c0")
        rows = scan(tmp)
        case("intact chain -> no violations", rows and not rows[0]["violations"])

        w("frozen/arm-winner", run_id="arm-winner", candidate_id="arm-g9-c9")
        case("L1 FIRES when the marker names a candidate that does not exist",
             any(v.startswith("L1") for v in scan(tmp)[0]["violations"]))

        w("frozen/arm-winner", run_id="arm-winner", reward_source_hash="f" * 64)
        v = scan(tmp)[0]["violations"]
        case("L2 FIRES on a marker/candidate hash mismatch",
             any(x.startswith("L2") for x in v))
        case("L4 FIRES when the marker hash != sha256(its own source)",
             any(x.startswith("L4") for x in v))

        w("frozen/arm-winner", run_id="arm-winner",
          reward_source="def reward(a,b,c,d,e):\n    return 1.0, {}, None")
        case("L3 FIRES when the marker source differs from the candidate's",
             any(x.startswith("L3") for x in scan(tmp)[0]["violations"]))

        w("frozen/arm-winner", run_id="arm-winner")
        w("test/arm/arm-s1", run_id="arm-s1", reward_source_hash="a" * 64)
        case("L5 FIRES when a test record carries a different hash",
             any(x.startswith("L5") for x in scan(tmp)[0]["violations"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\nselftest: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    raise SystemExit(report(scan(ARCHIVE)))
