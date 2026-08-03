"""STATUS PAGE FACTS - the SEARCH stage table and the LIVE SEED LADDER, from directory names only.

WHY THIS EXISTS (2026-08-03, RUN 17, execution record s.125.3).

`docs/ops/publish_status.sh` computes the status page Tamer reads on his phone. Two things were
wrong with the way it did it, and one of them was telling him something false about the campaign.

**(1) IT WAS 225x MORE EXPENSIVE THAN IT NEEDED TO BE, AND THE COST GROWS WITH THE ARCHIVE.**
The inline scan `json.load`ed EVERY record.json in the archive to read two fields. MEASURED
2026-08-03 at 9,027 records: **67.8 seconds**, run by `publish_loop.sh` roughly once a minute,
forever, growing linearly - at rung 568 (~42,000 records) it would be ~5 minutes per publish. It
ran CONCURRENTLY with `cycle.py`'s own full-archive sweep, which is already SWEEP-BOUND at
106-273 s and rising. That is P194 exactly ("a new monitor is a load on the monitor it joins")
operating live, on the machine whose monitoring cadence Tamer cares most about.
Reading the same facts from DIRECTORY NAMES costs **0.30 s** and opens no file at all.

**(2) THE `candidates so far` COLUMN WAS COUNTING THE SEALED TEST TOO.** It matched on the record's
`arm` field campaign-wide, so `distributional` read **2,136** when only **1,516** search candidates
exist in the entire campaign - it was adding every sealed-test seed of the same arm. A search-stage
column silently including test records is a mislabelled number on the page he reads, and it makes
the search look ~40% further along than it is. The candidate identity is in the DIRECTORY NAME
(`<arm>-g<G>-c<C>`, only ever created under `search*/`), so scoping it correctly and making it
cheap are the same change.

**(3) AND THE PAGE HAD NO LADDER AT ALL** - it asserted in prose that the seed ladder "is the NEXT
phase and has not started" while gemini-2.5-flash and h3 had ALREADY COMPLETED the full 568-seed
ladder. `ladder_rows()` replaces that prose with the measurement.

THE LADDER USES THE FROZEN ROSTER, NOT THE DIRECTORIES THAT HAPPEN TO EXIST. An arm that is frozen
but has not yet written its first sealed-test record has NO directory, so a scan of existing
directories reports the line as deeper than it is - the P215 blind spot. `line_balance.archive_depths`
already joins the `frozen*/-winner` markers to the test tree correctly (including the `-winner`
suffix strip that manufactured 56 phantom arms when it was got wrong), so it is IMPORTED rather
than re-derived. If that import fails the ladder says so instead of printing a wrong number.

EFFECT-BLIND: directory names and record COUNTS only. No record is opened, no metric is read.

    python docs/ops/status_stage.py            # both tables, as the page renders them
    python docs/ops/status_stage.py --stage    # the search-stage rows only
    python docs/ops/status_stage.py --ladder   # the seed-ladder rows only
    python docs/ops/status_stage.py --selftest
"""
from __future__ import annotations

import argparse
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_ROOT = os.path.join(REPO, "outputs", "campaign_cluster_run4")

ARMS = ("distributional", "scalar", "placebo", "scalar_cvar5", "placebo_shuffled")


def _split_candidate(arm: str, name: str):
    """`<arm>-g<G>-c<C>` -> (G, C), else None. Parsed, never regex-with-a-dollar-in-a-shell-string."""
    if not name.startswith(arm + "-g"):
        return None
    rest = name[len(arm) + 2:]
    if "-c" not in rest:
        return None
    g, _, c = rest.partition("-c")
    if not g.isdigit() or not c.isdigit():
        return None
    return int(g), int(c)


def stage_rows(root: str = DEFAULT_ROOT) -> list:
    """[(arm, furthest_generation, n_search_candidates)] over SEARCH roots only."""
    gen = {a: -1 for a in ARMS}
    n = {a: 0 for a in ARMS}
    try:
        lines = os.listdir(root)
    except OSError:
        return [(a, -1, 0) for a in ARMS]
    for line in lines:
        if not line.startswith("search"):
            continue
        lp = os.path.join(root, line)
        if not os.path.isdir(lp):
            continue
        for arm in os.listdir(lp):
            if arm not in ARMS:
                continue
            ap = os.path.join(lp, arm)
            if not os.path.isdir(ap):
                continue
            for d in os.listdir(ap):
                gc = _split_candidate(arm, d)
                if gc is None:
                    continue
                if os.path.isfile(os.path.join(ap, d, "record.json")):
                    gen[arm] = max(gen[arm], gc[0])
                    n[arm] += 1
    return [(a, gen[a], n[a]) for a in ARMS]


def ladder_rows(root: str = DEFAULT_ROOT) -> list:
    """[(test_dir, min_seeds, max_seeds, n_frozen_arms, n_arms_at_zero)] over the FROZEN roster.

    Sorted shallowest-first, because under R101 the reported result is the MINIMUM over lines and
    the top of this table is therefore the number that IS the result.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import line_balance as _lb
    except Exception:  # noqa: BLE001 - a status page must degrade loudly, never silently
        return []
    # ⚠ `root` USED TO BE ACCEPTED AND IGNORED. `archive_depths()` reads `line_balance.ROOT`, a
    # module constant, so `--root <anything>` silently measured the PRODUCTION archive -- which also
    # meant no selftest could ever exercise this half of the file on a fixture. An auditor caught it.
    # Bind the constant for the call and restore it, so the parameter now means what it says.
    prev = _lb.ROOT
    try:
        _lb.ROOT = root
        depths = _lb.archive_depths()
    finally:
        _lb.ROOT = prev
    out = []
    for test_dir, per_arm in depths.items():
        if not per_arm:
            continue
        vals = list(per_arm.values())
        out.append((test_dir, min(vals), max(vals), len(vals), sum(1 for v in vals if v == 0)))
    out.sort(key=lambda r: (r[1], r[2]))
    return out


def render_stage(root: str = DEFAULT_ROOT) -> str:
    rows = stage_rows(root)
    if not rows or all(r[2] == 0 for r in rows):
        return "| (stage scan found NO search candidates -- this is not a healthy zero) | | |"
    return "\n".join("| %s | g%d of 5 | %d |" % (a, max(g, 0), n) for a, g, n in rows)


def render_ladder(root: str = DEFAULT_ROOT) -> str:
    rows = ladder_rows(root)
    if not rows:
        return "| (ladder unavailable -- line_balance.archive_depths did not load) | | | |"
    body = []
    for test_dir, lo, hi, n_arms, zeros in rows:
        name = test_dir[len("test_leg_"):] if test_dir.startswith("test_leg_") else test_dir
        note = "COMPLETE" if lo >= 568 else ("%d arm(s) still at zero" % zeros if zeros else "")
        body.append("| %s | **%d** | %d | %d | %s |" % (name, lo, hi, n_arms, note))
    return "\n".join(body)


def common_rung(root: str = DEFAULT_ROOT) -> int:
    """The MINIMUM seed depth over every frozen arm of every line -- the reported result under R101."""
    rows = ladder_rows(root)
    return min((r[1] for r in rows), default=-1)


def selftest() -> int:
    import tempfile
    ok = 0
    fail = 0

    def check(name, cond, detail=""):
        nonlocal ok, fail
        if cond:
            ok += 1
            print("  PASS  %s" % name)
        else:
            fail += 1
            print("  FAIL  %s  %s" % (name, detail))

    check("A candidate name parses", _split_candidate("distributional", "distributional-g4-c2") == (4, 2))
    check("B a SEED dir is NOT a candidate", _split_candidate("distributional", "distributional-s17") is None)
    check("C a foreign arm's dir does not parse", _split_candidate("scalar", "distributional-g1-c1") is None)
    check("D a malformed generation does not parse", _split_candidate("scalar", "scalar-gX-c1") is None)

    with tempfile.TemporaryDirectory() as td:
        # a SEARCH candidate and a TEST seed for the same arm: only the candidate may be counted.
        for sub, d in (("search_leg_x", "distributional-g3-c1"),
                       ("search_leg_x", "distributional-g0-c0"),
                       ("test_leg_x", "distributional-s0")):
            p = os.path.join(td, sub, "distributional", d)
            os.makedirs(p, exist_ok=True)
            with open(os.path.join(p, "record.json"), "w", encoding="utf-8") as fh:
                fh.write("{}")
        rows = {a: (g, n) for a, g, n in stage_rows(td)}
        check("E the sealed TEST seed is excluded from the search-stage count",
              rows["distributional"] == (3, 2), str(rows["distributional"]))

    with tempfile.TemporaryDirectory() as td:
        rows = stage_rows(td)
        check("F an EMPTY root yields zeros, and render says so rather than printing a table",
              all(n == 0 for _, _, n in rows) and "not a healthy zero" in render_stage(td))

    # G-I: THE LADDER HALF, which previously had ZERO coverage because `root` was ignored. This is
    # the half that renders onto Tamer's page and that the file was written for.
    with tempfile.TemporaryDirectory() as td:
        for arm, n in (("distributional", 30), ("scalar", 12)):
            for s in range(n):
                p = os.path.join(td, "test_leg_x", arm, "%s-s%d" % (arm, s))
                os.makedirs(p, exist_ok=True)
                with open(os.path.join(p, "record.json"), "w", encoding="utf-8") as fh:
                    fh.write("{}")
            fp = os.path.join(td, "frozen_leg_x", "%s-winner" % arm)
            os.makedirs(fp, exist_ok=True)
            with open(os.path.join(fp, "record.json"), "w", encoding="utf-8") as fh:
                fh.write("{}")
        rows = ladder_rows(td)
        check("G ladder_rows HONOURS --root (it silently read production before)",
              len(rows) == 1 and rows[0][0] == "test_leg_x", str(rows))
        check("H the ladder reports the line's MINIMUM over arms, not its maximum",
              bool(rows) and rows[0][1] == 12 and rows[0][2] == 30, str(rows))
        check("I common_rung is that minimum", common_rung(td) == 12, str(common_rung(td)))

    with tempfile.TemporaryDirectory() as td:
        check("J an empty root makes the ladder say 'unavailable' and main() exit 2",
              "unavailable" in render_ladder(td) and main(["--root", td, "--ladder"]) == 2)

    print("\nselftest: %d passed, %d failed" % (ok, fail))
    return 0 if fail == 0 else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Status-page stage and ladder tables.")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--stage", action="store_true")
    ap.add_argument("--ladder", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    # ⚠ THIS USED TO `return 0` UNCONDITIONALLY -- including when the render emitted
    # "(stage scan found NO search candidates)" or "(ladder unavailable)". `publish_status.sh`
    # relies on the rc, so a VACUOUS scan was published as if it had been measured: the standing
    # "fail loudly on an empty input" rule, broken in the file that feeds Tamer's page.
    stage = render_stage(a.root)
    ladder = render_ladder(a.root)
    bad = ("not a healthy zero" in stage) or ("unavailable" in ladder)
    if a.stage:
        print(stage)
        return 2 if "not a healthy zero" in stage else 0
    if a.ladder:
        print(ladder)
        return 2 if "unavailable" in ladder else 0
    print(stage)
    print()
    print(ladder)
    return 2 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
