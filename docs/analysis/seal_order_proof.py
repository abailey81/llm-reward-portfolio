"""PROOF: the archive-integrity seal is ORDER-DEPENDENT, and it reports SPURIOUS "CHANGED".

`scripts/archive_integrity.py` is the project's tamper-evidence guarantee -- its own docstring
calls it "deterministic, order-independent" and "a tamper-evident reproducibility guarantee,
not a vibe". It keys the manifest on run_id:

    key = run_id or f"__PATH__:{...}"
    # A duplicate run_id (two dirs, same id) must not silently overwrite: disambiguate by path
    if key in out:
        key = f"{key}@{path}"
    out[key] = digest

The collision case IS anticipated -- good defensive coding -- but the disambiguation is applied
to whichever record is seen SECOND, and records are visited in `sorted(root.rglob(...))` order.
*** So which record holds the BARE key depends on path sort order. When a NEW record arrives
whose path sorts EARLIER than the current holder, the bare key's DIGEST changes and the seal
reports "CHANGED" -- although no record was mutated. ***

That is exactly what the live archive showed:
    1 CHANGED record(s): ['placebo-s27']
    1 ADDED: ['placebo-s27@test_leg_gpt_5_6_luna/placebo/placebo-s27']
Both name the same run_id, and `placebo-s27` exists in several lines.

WHY IT MATTERS: a tamper-evidence seal that cries wolf on ordinary growth trains its readers to
ignore it, and *** a GENUINE silent edit becomes indistinguishable from the routine noise. ***

THE FIX is smaller than the current code: key on PATH ALWAYS. Paths are unique by construction,
run_ids are not, and path-keying is genuinely order-independent -- which is what the docstring
already promises.

Read-only; operates on a synthetic fixture, never on the real archive.
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))


def _write(base: Path, rel: str, run_id: str, payload: str) -> None:
    d = base / rel
    d.mkdir(parents=True, exist_ok=True)
    (d / "record.json").write_text(
        json.dumps({"run_id": run_id, "payload": payload}, sort_keys=True), encoding="utf-8")


def main() -> int:
    from archive_integrity import record_digests  # type: ignore[import-not-found]

    tmp = Path(tempfile.mkdtemp(prefix="sealproof_"))
    try:
        # Two lines, SAME run_id -- exactly the campaign's situation.
        _write(tmp, "test_leg_bbb/placebo/placebo-s27", "placebo-s27", "BBB-content")
        d1 = record_digests(tmp)
        print("=== step 1: one line holds run_id 'placebo-s27' ===")
        for k, v in sorted(d1.items()):
            print(f"    {k:<56} {v[:16]}")

        # A NEW record arrives on a line whose path sorts EARLIER ("aaa" < "bbb").
        # NOTHING existing has been touched.
        _write(tmp, "test_leg_aaa/placebo/placebo-s27", "placebo-s27", "AAA-content")
        d2 = record_digests(tmp)
        print("\n=== step 2: a NEW record arrives on an earlier-sorting line ===")
        print("    (nothing existing was modified -- one file was ADDED)")
        for k, v in sorted(d2.items()):
            print(f"    {k:<56} {v[:16]}")

        bare = "placebo-s27"
        changed = d1.get(bare) != d2.get(bare)
        print("\n=== RESULT ===")
        print(f"    bare key '{bare}' digest before : {d1.get(bare, '<none>')[:16]}")
        print(f"    bare key '{bare}' digest after  : {d2.get(bare, '<none>')[:16]}")
        if changed:
            print("    *** THE BARE KEY'S DIGEST CHANGED THOUGH NO RECORD WAS MUTATED. ***")
            print("    A verifier diffing these manifests reports a SPURIOUS 'CHANGED'")
            print("    record plus an 'ADDED' one -- precisely the live archive's output.")
        else:
            print("    bare key stable -- the defect did NOT reproduce; investigate before")
            print("    claiming anything.")

        # The proposed fix: key on PATH always.
        def path_keyed(root: Path) -> dict[str, str]:
            import hashlib
            out = {}
            for p in sorted(Path(root).rglob("record.json")):
                raw = p.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
                out[p.parent.relative_to(root).as_posix()] = hashlib.sha256(raw).hexdigest()
            return out

        p1 = path_keyed(tmp)
        _write(tmp, "test_leg_000/placebo/placebo-s27", "placebo-s27", "000-content")
        p2 = path_keyed(tmp)
        stable = all(p1[k] == p2[k] for k in p1)
        print("\n=== THE PROPOSED FIX (key on PATH always) ===")
        print(f"    keys before: {len(p1)}   after adding an even-earlier-sorting record: {len(p2)}")
        print(f"    every pre-existing key's digest UNCHANGED: {stable}")
        print("    " + ("*** FIX HOLDS: additions are purely ADDED, never CHANGED. ***"
                        if stable else "*** FIX DOES NOT HOLD -- do not adopt. ***"))
        return 0 if changed and stable else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
