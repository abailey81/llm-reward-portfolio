"""LOADER-POOLING DETECTOR -- does the analysis loader's (arm, seed) key COLLIDE across model lines?

⚠ WHY THIS EXISTS, AND WHY IT IS URGENT DESPITE PRODUCING NO NUMBER THE DISSERTATION REPORTS.
`scripts/analyze_campaign.py` produces THE RESULT and runs exactly ONCE, at teardown. It is
DRIFT-FENCED for the campaign's duration, so it cannot be corrected while the campaign is live.
This file is the unfenced half of that problem: it makes a defect that would surface at teardown
visible TODAY, on every pass, while there is still time to plan for it.

THE DEFECT, established first-hand on 2026-08-04 (RUN 21, from an auditor's finding):

  * `load_campaign_records` (`scripts/analyze_campaign.py:1152-1184`) walks the archive to depth
    `_MAX_ARCHIVE_DEPTH = 3` and skips exactly two things: DOT-prefixed directories and
    `*_h3_singleshot`. **`test_leg_*` is NOT skipped**, so every replication leg's records enter the
    same `records` list as the core line, carrying the SAME `arm` labels.
  * Its de-duplication key is `(directory, run_id)`, so two lines holding the same `run_id` do not
    displace each other -- **both load**. That is deliberate (the A79 fix), and it is what makes the
    collision downstream rather than at load time.
  * `_seed_scores` (`:1394-1425`) then groups by `(arm, seed)` alone. On CONFLICTING duplicates it
    RAISES `ValueError`; `analyze()` guards only `AssertionError`, so the whole analysis aborts.

⇒ **THE H2 CO-PRIMARY PATH FAILS LOUD.** That is the reassuring half and it must be stated, because
"the loader pools leg records into the confirmatory verdict" reads as a silent-wrong-number defect
and on this path it is not one. **The silent paths are `benchmark_floor` (`:5444-5448`) and
`h1_beat_human` (`:5847`), which take `np.mean(np.stack(vecs))` over every distributional TEST
record with NO duplicate guard at all** -- those would average across models and report a number.

MEASURED WHEN THIS FILE WAS WRITTEN: the core line holds NO `distributional` and NO `scalar`
directory at all (it has not reached C2), while SEVEN leg lines already hold
`distributional/distributional-s0`. So the collision is not hypothetical and it is already present.

EFFECT-BLIND BY CONSTRUCTION. This file reads ONLY `arm`, `seed` and `run_id` from each record --
identity metadata, never an outcome. It never opens `test_returns`, a Sharpe, a CVaR or a fitness,
and it computes no contrast. `_assert_blind()` enforces that at exit over the fields actually read.

    python docs/analysis/loader_collision_watch.py [--root outputs/campaign_cluster_run4]

exit 0 = no cross-line collision on any arm the analysis groups by
exit 1 = at least one (arm, seed) is held by more than one line
exit 2 = the archive could not be read (UNKNOWN -- never reported as clean)
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

#: Mirrors `scripts/analyze_campaign.py:1106`. If that constant changes, this detector is measuring
#: a different population than the analysis and must be updated with it.
MAX_ARCHIVE_DEPTH = 3
RECORD_NAME = "record.json"

#: The only fields this file is permitted to read. Enforced, not asserted in prose.
BLIND_FIELDS = ("arm", "seed", "run_id")


def _walk(directory: Path, depth: int, out: list[tuple[str, Path]], line: str) -> None:
    """The analysis loader's own walk, reproduced exactly (dot-dirs and h3 skipped, depth-bounded)."""
    if not directory.is_dir():
        return
    children = sorted(p for p in directory.iterdir() if p.is_dir())
    for c in children:
        if (c / RECORD_NAME).is_file():
            out.append((line, c))
    if depth < MAX_ARCHIVE_DEPTH:
        for child in children:
            if child.name.startswith(".") or child.name.endswith("_h3_singleshot"):
                continue
            _walk(child, depth + 1, out, line)


#: A seeded test run directory is named `<arm>-s<seed>` and sits under `<line>/<arm>/`.
_SEEDED = re.compile(r"^(?P<arm>.+)-s(?P<seed>\d+)$")


def collect(root: Path) -> tuple[dict, list[str]]:
    """Return {(arm, seed): {line: [run_id, ...]}} plus any read errors.

    ⚠ FROM DIRECTORY NAMES, NOT FROM RECORD CONTENTS, AND THE REASON IS MEASURED. Opening 13,500
    records at ~480 KB each is the 7-8 GB / multi-minute cost P289-P291 had to engineer away; a
    detector that cannot run on every pass is a detector that does not run. `--verify-fields`
    samples records to confirm the naming convention still holds, which is the cheap half of the
    same assurance.
    """
    errors: list[str] = []
    cells: dict[tuple[str, object], dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    # ⚠ THE TOP LEVEL OBEYS THE SAME TWO SKIPS. The loader calls `_walk(root, 0)`, so its dot-dir
    # and `*_h3_singleshot` exclusions apply to the LINE directories as well. A first version of
    # this file walked every top-level directory and duly reported `test_h3_singleshot` as a
    # colliding holder of `distributional` seeds -- which is exactly the pooling the loader
    # already prevents, i.e. MY detector was wrong, not the loader. A surprising positive is a
    # claim about your own script first.
    lines = sorted(p for p in root.iterdir()
                   if p.is_dir() and not p.name.startswith(".")
                   and not p.name.endswith("_h3_singleshot"))
    for line_dir in lines:
        found: list[tuple[str, Path]] = []
        try:
            _walk(line_dir, 1, found, line_dir.name)
        except OSError as exc:
            errors.append(f"{line_dir}: {type(exc).__name__}: {exc}")
            continue
        for line, rec_dir in found:
            m = _SEEDED.match(rec_dir.name)
            if not m:
                continue                       # a SEARCH candidate, not a seeded test record
            cells[(m.group("arm"), int(m.group("seed")))][line].append(rec_dir.name)
    return cells, errors


def verify_fields(cells: dict, root: Path, n: int = 20) -> list[str]:
    """Sample n cells and confirm the record's own `arm`/`seed` match the directory name.

    The grouping key `_seed_scores` uses is `r["arm"]` and `r["seed"]`, NOT the path, so the
    path-derived census above is a proxy. This checks the proxy rather than assuming it -- a
    directory convention nobody verifies is a convention that has already drifted somewhere.
    """
    bad: list[str] = []
    sample = sorted(cells.items(), key=lambda kv: (kv[0][0], kv[0][1]))[:n]
    for (arm, seed), holders in sample:
        line = sorted(holders)[0]
        run_id = holders[line][0]
        p = root / line / arm / run_id / RECORD_NAME
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            bad.append(f"{p}: {type(exc).__name__}: {exc}")
            continue
        if str(raw.get("arm")) != arm or raw.get("seed") != seed:
            bad.append(f"{p}: record says arm={raw.get('arm')!r} seed={raw.get('seed')!r}, "
                       f"path says arm={arm!r} seed={seed!r}")
    return bad


def _assert_blind() -> None:
    """The blindness guarantee, PROVEN over this file's own AST rather than promised.

    ⚠ A SUBSTRING SCAN IS THE WRONG INSTRUMENT AND THE FIRST VERSION USED ONE. It matched the words
    `test_returns`, `metrics` and `val_fitness` in the explanatory text this file PRINTS -- prose
    about the defect, not a read of it -- and raised a breach on a run that had opened nothing. The
    property to check is not "does the word appear" but "is any outcome key ever LOOKED UP", so this
    walks the AST and collects every string used as a `.get(...)` argument or a `[...]` subscript
    against a loaded record. Those are the only ways a field can be read here.
    """
    import ast

    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    looked_up: set[str] = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get" and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)):
            looked_up.add(node.args[0].value)
        if (isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
                and isinstance(node.slice.value, str)):
            looked_up.add(node.slice.value)
    # `arm` and `seed` are also regex group names, which is why they are named here explicitly.
    allowed = set(BLIND_FIELDS)
    breach = sorted(looked_up - allowed)
    if breach:
        raise AssertionError(
            f"BLINDNESS BREACH: this file looks up record field(s) {breach}. It may read only "
            + ", ".join(BLIND_FIELDS))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="outputs/campaign_cluster_run4")
    ap.add_argument("--verify-fields", action="store_true",
                    help="sample 20 records and confirm arm/seed match the directory names")
    args = ap.parse_args()
    root = Path(args.root)

    print("=== LOADER COLLISION WATCH -- (arm, seed) held by more than one model line ===")
    if not root.is_dir():
        print(f"  ARCHIVE NOT READABLE at {root} -- UNKNOWN, never reported as clean")
        return 2
    cells, errors = collect(root)
    if not cells:
        # P286: an empty result must never read as clean. "Looked at nothing" and "found nothing
        # wrong" are different states and this campaign has confused them before.
        print("  ZERO seeded records enumerated -- CANNOT VOUCH. Either the archive is empty or the "
              "walk is pointed at the wrong root; both are UNKNOWN, not clean.")
        return 2

    collisions = {k: v for k, v in cells.items() if len(v) > 1}
    n_lines = len({ln for v in cells.values() for ln in v})
    print(f"  root: {root}")
    print(f"  seeded (arm, seed) cells enumerated: {len(cells)}   model lines walked: {n_lines}")
    if errors:
        print(f"  ⚠ {len(errors)} path(s) unreadable -- listed below; treat the verdict as partial")
        for e in errors[:5]:
            print(f"      {e}")
    if args.verify_fields:
        bad = verify_fields(cells, root)
        print(f"  --verify-fields: sampled 20 cell(s); "
              f"{'ALL agree with the directory names' if not bad else str(len(bad)) + ' DISAGREE'}")
        for b in bad[:5]:
            print(f"      {b}")

    if not collisions:
        print("\n  NO cross-line collision. Every (arm, seed) the analysis groups by is held by "
              "exactly one line.")
        _assert_blind()
        print("\nEFFECT-BLIND: arm, seed and run_id only. No outcome field was opened.")
        return 0

    by_arm: dict[str, int] = defaultdict(int)
    for (arm, _seed) in collisions:
        by_arm[arm] += 1
    print(f"\n  !! {len(collisions)} (arm, seed) cell(s) are held by MORE THAN ONE LINE.")
    print("  per arm:")
    for arm, n in sorted(by_arm.items(), key=lambda kv: -kv[1]):
        print(f"      {arm:<22} {n:>5} colliding seed(s)")
    print("\n  first five, with the lines that hold them:")
    for (arm, seed), holders in sorted(collisions.items(), key=lambda kv: (kv[0][0], str(kv[0][1])))[:5]:
        print(f"      arm={arm!r} seed={seed}: " + ", ".join(sorted(holders)))

    print("\n  WHAT THIS MEANS AT TEARDOWN, and the two halves differ:")
    print("    * `_seed_scores` groups by (arm, seed) and RAISES ValueError on conflicting")
    print("      duplicates, so the H2 co-primary path FAILS LOUD and `analyze()` aborts.")
    print("    * `benchmark_floor` and `h1_beat_human` have NO duplicate guard and would average")
    print("      across model lines SILENTLY, reporting a number computed on pooled models.")
    print("  `scripts/**` is DRIFT-FENCED while the campaign is live, so this is a REGISTERED")
    print("  deferred fix (docs/DEFERRED_FIXES_RUN4.md), not something to patch now.")
    _assert_blind()
    print("\nEFFECT-BLIND: arm, seed and run_id only. No outcome field was opened.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
