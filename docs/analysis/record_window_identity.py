"""S14 -- DID EVERY SEALED-TEST RECORD SEE THE SAME PERIOD, ON THE SAME SUBSTRATE, UNDER ITS OWN ARM?

WHY THIS LAYER EXISTS (2026-08-03, RUN 16, execution record s.118).

The six existing record layers check a great deal and this was still uncovered:

  * `record_science_audit` S2 asserts every sealed-test series is the REGISTERED LENGTH (1571).
  * S8 asserts every test record holds the MODAL number of steps.

**NEITHER CHECKS THE WINDOW BOUNDS, AND LENGTH IS NOT PERIOD.** `[3835,5406)` and `[3900,5471)` both
have length 1571. Two arms scored on different 1571-day periods would pass S2 and S8 while being
completely incomparable -- and comparability across arms at the same seed is the assumption EVERY
paired H2 contrast rests on. A silent divergence here would not corrupt any single record; it would
corrupt the CONTRAST, which is worse, because every per-record check would stay green.

The bounds are carried in `env_fingerprint.label`, which the env writes itself:

    campaign:<arm>:test[3835,5406)|dev=cpu

That one string also answers two more questions nothing else asks:

  W2  DEVICE HOMOGENEITY across the sealed test. The substrate fence (D15) is enforced by host
      exclusion at submission; this is the independent confirmation FROM THE RECORDS that every
      scored record actually ran on the same device class.
  W3  ARM AGREEMENT. Does the label's arm match the record's own `arm` field? A disagreement means
      a record is archived under an arm that is not the one it was produced for -- which would put a
      treatment record into a control pool and silently poison the contrast. Nothing checked this.

WHAT THIS DOES **NOT** CHECK, stated plainly because a passing check tells you what it TESTED:
  * It does not verify the window is the RIGHT one against the frozen splits file -- it verifies
    every record agrees with every other. If the whole campaign used a wrong-but-consistent window
    this layer stays green (S2's registered-length check is the partner that would catch that, and
    its own limitation is already recorded: the 1571 constant is sourced from a COMMENT).
  * It says nothing about VALUES. It is EFFECT-BLIND by construction -- it reads labels and arm
    names, never a metric, so it cannot leak a treatment outcome.
  * It covers the SEALED TEST only. Search-tier records are scored on the dev split by design.

    python docs/analysis/record_window_identity.py
    python docs/analysis/record_window_identity.py --selftest
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys

# docs/analysis/<this> -> docs/analysis -> docs -> repo. THREE levels. Taking two lands on `docs`
# and ROOT then points at a directory that does not exist, so the walk finds nothing -- which is
# exactly what happened on this file's first run inside the layer harness, and it reported CLEAN.
# The identical two-vs-three mistake was made in docs/ops/line_balance.py the same session.
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.join(REPO, "outputs", "campaign_cluster_run4")

#: `campaign:<arm>:<split>[lo,hi)|dev=<device>` -- written by the env, not by us.
LABEL_RE = re.compile(
    r"^campaign:(?P<arm>[^:]+):(?P<split>[a-z]+)\[(?P<lo>\d+),(?P<hi>\d+)\)\|dev=(?P<dev>\S+)$")


def scan(root: str) -> dict:
    """Walk the sealed-test tree once and tally the three invariants."""
    out = {
        "n": 0,
        "windows": collections.Counter(),
        "devices": collections.Counter(),
        "splits": collections.Counter(),
        "per_line": collections.defaultdict(collections.Counter),
        "arm_mismatch": [],
        "unparsed": [],
    }
    for dirpath, _dirnames, filenames in os.walk(root):
        if ".pull_tmp" in dirpath or "record.json" not in filenames:
            continue
        rel = os.path.relpath(dirpath, root).replace(os.sep, "/")
        line = rel.split("/")[0]
        if not line.startswith("test"):
            continue
        try:
            with open(os.path.join(dirpath, "record.json"), encoding="utf-8") as fh:
                rec = json.load(fh)
        except Exception:  # noqa: BLE001 -- a torn record is R1's business, not this layer's
            continue
        out["n"] += 1
        label = ((rec.get("env_fingerprint") or {}).get("label") or "")
        m = LABEL_RE.match(label)
        if not m:
            out["unparsed"].append((rel, label[:70]))
            continue
        win = (int(m.group("lo")), int(m.group("hi")))
        out["windows"][win] += 1
        out["devices"][m.group("dev")] += 1
        out["splits"][m.group("split")] += 1
        out["per_line"][line][win] += 1
        if m.group("arm") != rec.get("arm"):
            out["arm_mismatch"].append((rel, m.group("arm"), rec.get("arm")))
    return out


def report(res: dict) -> int:
    print("=== S14 WINDOW / SUBSTRATE / ARM IDENTITY (sealed test only) ===")
    print("  sealed-test records inspected : %d" % res["n"])
    if not res["n"]:
        # ⚠ ZERO RECORDS IS A FAILURE, NEVER A PASS (P213). This layer's FIRST run inside the
        # seven-layer harness inspected 0 records and printed CLEAN with rc=0, because ROOT was
        # mis-derived. A check that examined nothing and reported success is the P197 shape -- the
        # defect an independent auditor had to catch when "determinism is MEASURED" was claimed from
        # a check that compared nothing. A vacuous pass is worse than a failure: it BANKS a property
        # that was never tested. So an empty scan exits non-zero and says why.
        print("\nS14 *** CANNOT VOUCH FOR ANYTHING *** -- zero sealed-test records were found under")
        print("  %s" % ROOT)
        print("  This is NOT a clean result. Either the root is wrong or the archive is missing;")
        print("  in both cases the invariants below were NEVER EVALUATED.")
        return 2

    print("\n  W1 test window bounds:")
    for w, c in res["windows"].most_common():
        print("     [%d,%d)  length=%d   %d record(s)" % (w[0], w[1], w[1] - w[0], c))
    print("  W2 device: %s" % dict(res["devices"]))
    print("     split : %s" % dict(res["splits"]))
    print("  W3 label-arm vs record-arm mismatches: %d" % len(res["arm_mismatch"]))
    for r in res["arm_mismatch"][:5]:
        print("       %s  label=%s  field=%s" % r)
    if res["unparsed"]:
        print("  unparseable labels: %d" % len(res["unparsed"]))
        for r in res["unparsed"][:5]:
            print("       %s  %s" % r)

    bad = []
    if len(res["windows"]) > 1:
        bad.append("W1 MORE THAN ONE TEST WINDOW -- the arms did not see the same period, so no "
                   "paired contrast between them is comparable")
        for line, ws in sorted(res["per_line"].items()):
            if len(ws) > 1:
                bad.append("   %s spans %s" % (line, dict(ws)))
    if len(res["devices"]) > 1:
        bad.append("W2 MORE THAN ONE DEVICE across the sealed test -- substrate homogeneity broken")
    if res["arm_mismatch"]:
        bad.append("W3 %d record(s) are archived under an arm their own env fingerprint disagrees "
                   "with" % len(res["arm_mismatch"]))
    if res["unparsed"]:
        bad.append("%d label(s) did not parse -- this layer cannot vouch for them"
                   % len(res["unparsed"]))

    print()
    if bad:
        print("S14 *** VIOLATIONS ***")
        for b in bad:
            print("  " + b)
        return 1
    win = next(iter(res["windows"]))
    print("S14 CLEAN -- every sealed-test record covers [%d,%d), ran on %s, and agrees with its own"
          % (win[0], win[1], next(iter(res["devices"]))))
    print("  env fingerprint about which arm it belongs to. The sealed test is therefore COMPARABLE")
    print("  ACROSS ARMS, which is the assumption every paired H2 contrast rests on.")
    print("EFFECT-BLIND: labels and arm names only; no metric was read.")
    return 0


def _selftest() -> int:
    """Prove each violation is REACHABLE, not just that the clean path passes."""
    import shutil
    import tempfile

    tmp = tempfile.mkdtemp(prefix="s14_")
    try:
        def write(line, arm, run, label, arm_field=None):
            d = os.path.join(tmp, line, arm, run)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "record.json"), "w", encoding="utf-8") as fh:
                json.dump({"arm": arm_field or arm, "env_fingerprint": {"label": label}}, fh)

        cases = []

        write("test_leg_a", "scalar", "s0", "campaign:scalar:test[3835,5406)|dev=cpu")
        write("test_leg_a", "distributional", "s0", "campaign:distributional:test[3835,5406)|dev=cpu")
        r = scan(tmp)
        cases.append(("clean: one window, one device, arms agree", report_rc(r) == 0))

        write("test_leg_b", "scalar", "s0", "campaign:scalar:test[3900,5471)|dev=cpu")
        r = scan(tmp)
        cases.append(("W1 fires on a SECOND window of the SAME LENGTH (1571)", report_rc(r) == 1))
        shutil.rmtree(os.path.join(tmp, "test_leg_b"))

        write("test_leg_c", "scalar", "s0", "campaign:scalar:test[3835,5406)|dev=cuda")
        r = scan(tmp)
        cases.append(("W2 fires on a second device", report_rc(r) == 1))
        shutil.rmtree(os.path.join(tmp, "test_leg_c"))

        write("test_leg_d", "placebo", "s0", "campaign:scalar:test[3835,5406)|dev=cpu",
              arm_field="placebo")
        r = scan(tmp)
        cases.append(("W3 fires when the label's arm disagrees with the arm field",
                      report_rc(r) == 1))
        shutil.rmtree(os.path.join(tmp, "test_leg_d"))

        write("test_leg_e", "scalar", "s0", "not-a-label")
        r = scan(tmp)
        cases.append(("unparseable label is reported, never silently skipped", report_rc(r) == 1))
        shutil.rmtree(os.path.join(tmp, "test_leg_e"))

        write("search_leg_z", "scalar", "s0", "campaign:scalar:dev[0,100)|dev=cpu")
        r = scan(tmp)
        cases.append(("search-tier records are EXCLUDED (dev split, by design)", report_rc(r) == 0))

        # P213 REGRESSION: an EMPTY scan must never report success. This layer's first run in the
        # harness inspected 0 records and printed CLEAN with rc=0 because ROOT was mis-derived.
        # report() owns that branch, so this case must go through report(), not report_rc().
        empty = tempfile.mkdtemp(prefix="s14_empty_")
        try:
            cases.append(("EMPTY scan exits NON-ZERO -- a vacuous pass is worse than a failure",
                          report(scan(empty)) != 0))
        finally:
            shutil.rmtree(empty, ignore_errors=True)

        bad = 0
        for label, ok in cases:
            print("  %s  %s" % ("PASS" if ok else "FAIL", label))
            bad += 0 if ok else 1
        print("selftest: %d/%d cases pass" % (len(cases) - bad, len(cases)))
        return 1 if bad else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def report_rc(res: dict) -> int:
    """report() without the printing, for the selftest.

    ⚠ IT MUST AGREE WITH `report()` ON EVERY PATH, INCLUDING n == 0. It did not: `report()` returns
    2 on an empty scan (P213) while this returned 0, because all four violation conditions are
    false on empty counters. Six selftest cases route through here, so if any of their fixtures
    ever stopped writing records they would have passed VACUOUSLY -- the P213 shape re-created
    inside the harness built to prevent it. Found by an independent auditor.
    """
    if not res["n"]:
        return 2
    if len(res["windows"]) > 1 or len(res["devices"]) > 1 or res["arm_mismatch"] or res["unparsed"]:
        return 1
    return 0


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="S14 window / substrate / arm identity.")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=ROOT)
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    return report(scan(a.root))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
