#!/usr/bin/env python
"""ANALYSIS-lane RESULTS cycle -- read-only, run every ~30 min.

This is the instrument the analysis lane was missing on 2026-08-01: the outgoing session
monitored PROCESS HEALTH (ops' cycle log, drift, spend, stalls) and analysed the SCIENCE only
episodically. This walks the archive itself and reports what the numbers say.

It prints ONLY (a) what CHANGED since the previous cycle and (b) anything scientifically wrong
regardless of whether it changed -- so a quiet run means quiet, not unwatched.

BLINDING. The campaign's stop is a calendar date (2026-08-27), fully exogenous, and the analysis
plan is frozen and mechanical -- so observing interim numbers cannot bias the stop. Even so this
tool deliberately computes NO confirmatory arm-vs-arm contrast and NO p-value. Its targets are
integrity, provenance, execution and report-only quantities. Keep it that way.

Usage:  python docs/analysis/results_cycle.py [--full] [--state PATH]
        --full   print every panel, not just the deltas (use on the first cycle of a session)
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import sys
from collections import defaultdict

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN4 = os.path.join(REPO, "outputs", "campaign_cluster_run4")
DEFAULT_STATE = os.path.join(REPO, "docs", "analysis", ".results_cycle_state.json")

# ⚠ DO NOT REINTRODUCE GLOB PATTERNS HERE. The first draft of this script used three fixed-depth
# globs (`search*/*/*/record.json` etc.) and silently missed 594 of 2,369 records -- every frozen
# winner (which sits at DEPTH 3, not 4), the whole `test_h3_singleshot` tier, and two depth-5
# search records -- then reported a clean over the 75% it could see. That is error P121 exactly,
# committed by the tool built to prevent it. The archive holds records at depths 3, 4 and 5 and
# will grow new tiers; a depth assumption is a latent false-clean. WALK THE TREE, CLASSIFY BY NAME.
def classify(rel: str) -> str:
    """Map an archive-relative record path to its tier. Unknown prefixes surface as `other:<dir>`
    rather than being dropped -- an unclassified record must be visible, never silently skipped."""
    top = rel.split("/", 1)[0]
    if top.startswith("frozen"):
        return "frozen"
    if top.startswith("search"):
        return "search"
    if top.startswith("test"):
        if "_leg_" in top:
            return "test_leg"
        return "test_core" if top == "test" else f"test_{top[5:]}"
    return f"other:{top}"
LLM_ARMS = ("distributional", "scalar", "placebo", "scalar_cvar5", "placebo_shuffled")

# ⚠ THE OUTCOME FIELD IS TIER-DEPENDENT, AND GETTING THIS WRONG IS THE LANE'S SIGNATURE ERROR.
# `val_fitness` is a SEARCH-STAGE quantity. On the test tiers it is NaN by design (verified on the
# live archive: 326/356 core records) and, where present, it is the winner's carried-over search
# number -- IDENTICAL across all thirty seed replicates BY CONSTRUCTION. The quantity that actually
# varies per seed on a test record is `test_sharpe` / `test_cvar05`. The first draft of this script
# read `val_fitness` on every tier and produced 326 false "non-finite" and 4 false "degenerate"
# findings -- i.e. it committed the very error (A10/A11: reading a value whose MEANING was not what
# its NAME implied) it exists to detect. Do not undo this.
OUTCOME_BY_TIER = {
    "search": ("metrics.val_fitness",),
    "test_leg": ("metrics.test_sharpe", "metrics.test_cvar05"),
    "test_core": ("metrics.test_sharpe", "metrics.test_cvar05"),
    "test_h3_singleshot": ("metrics.test_sharpe", "metrics.test_cvar05"),
}
# Records are seed REPLICATES only on the test tiers. The search tier runs every candidate at a
# single seed (verified: distributional-g0-c0..g1-c0 all seed=0), so a repeated seed there is the
# design, not a defect.
SEED_REPLICATE_TIERS = ("test_leg", "test_core")

# Fields whose values are arrays or free text -- summarised by type/length, never compared for
# constancy (a 500-element return series is not a "constant field" finding).
BULKY = {"val_returns", "reward_source", "prompt", "feedback_block", "tail_stats"}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval. Correct at k=0 and k=n, where the normal approximation is not."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def flatten(obj, prefix="", out=None):
    """Flatten a record to dotted paths. Bulky leaves become a type tag, not a value.

    ⚠ AN *EMPTY* BULKY LEAF KEEPS ITS REAL VALUE (fixed 2026-08-01, session 4). The original
    collapsed every BULKY field to a shape tag, so a `None` became the STRING ``"<bulk>"`` and an
    empty string became ``"<str:0>"`` — neither of which the always-null sweep counts as null. That
    made the sweep structurally incapable of finding the lane's own best historical finding, A11
    (``feedback_block`` empty on 100% of search records), because `feedback_block` is itself in
    BULKY. The shape tag exists so a 1,571-element return series is not compared for constancy; it
    was never meant to hide an EMPTY field, which is exactly the "value that never moves" case this
    tool exists to catch.
    """
    out = {} if out is None else out
    for key, val in obj.items():
        path = f"{prefix}{key}"
        if key in BULKY:
            if val is None or (hasattr(val, "__len__") and len(val) == 0):
                out[path] = val                      # visible to the null sweep, by design
            else:
                out[path] = f"<{type(val).__name__}:{len(val)}>"
        elif isinstance(val, dict):
            flatten(val, path + ".", out)
        elif isinstance(val, (list, tuple)):
            out[path] = f"<list:{len(val)}>"
        else:
            out[path] = val
    return out


def load_records():
    """Return [(tier, unit, relpath, flat_record)]. `unit` is the comparison unit -- the level at
    which CRN pairing and device homogeneity must hold (one directory above the seed dir)."""
    rows = []
    for path in glob.glob(os.path.join(RUN4, "**", "record.json"), recursive=True):
        rel = os.path.relpath(path, RUN4).replace("\\", "/")
        tier = classify(rel)
        # The unit is one level above the candidate/seed directory -- the level at which CRN pairing
        # and device homogeneity must hold. Degrades correctly for the depth-3 frozen records.
        parts = rel.split("/")
        unit = "/".join(parts[:-2]) if len(parts) >= 3 else parts[0]
        try:
            with open(path, encoding="utf-8") as fh:
                rec = json.load(fh)
        except Exception as exc:                          # a truncated mid-write record is a finding
            rows.append((tier, unit, rel, {"__unreadable__": repr(exc)}))
            continue
        rows.append((tier, unit, rel, flatten(rec)))
    return rows


def panel_counts(rows):
    counts = Counter_(t for t, _, _, _ in rows)
    counts["TOTAL"] = len(rows)
    return counts


def Counter_(it):
    d = defaultdict(int)
    for x in it:
        d[x] += 1
    return dict(d)


def panel_safe_default(rows):
    """Execution quantity: the fraction of candidates where the sandbox substituted SAFE_DEFAULT.
    Per-arm, with Wilson intervals -- an arm-differential rate would threaten identification."""
    any_sub, seen, frac_sum = defaultdict(int), defaultdict(int), defaultdict(float)
    for tier, _, _, r in rows:
        if tier != "search" or r.get("arm") not in LLM_ARMS:
            continue
        dflt, calls = r.get("metrics.train_safe_default_count"), r.get("metrics.train_safe_call_count")
        if dflt is None or not calls:
            continue
        arm = r["arm"]
        seen[arm] += 1
        frac_sum[arm] += dflt / calls
        if dflt > 0:
            any_sub[arm] += 1
    out = {}
    for arm in LLM_ARMS:
        if seen[arm]:
            lo, hi = wilson(any_sub[arm], seen[arm])
            out[arm] = (any_sub[arm], seen[arm], 100 * lo, 100 * hi, frac_sum[arm] / seen[arm])
    return out


def panel_constant_fields(rows):
    """THE highest-yield detector this lane has (findings A10/A11): a field that is null or
    constant on 100% of records is invisible to every gate that watches values MOVE."""
    values, nulls, total = defaultdict(set), defaultdict(int), 0
    for _, _, _, r in rows:
        if "__unreadable__" in r:
            continue
        total += 1
        for key, val in r.items():
            if val is None or val == "" or val == {}:
                nulls[key] += 1
            values[key].add(val if isinstance(val, (str, int, float, bool)) else str(val))
    always_null = sorted(k for k in values if nulls[k] == total)
    # Bulky/array leaves are stored as a `<list:N>` shape tag, so "one distinct value" there means
    # a constant LENGTH, not a constant VALUE -- reporting those as constant fields is noise.
    constant, shape_constant = [], []
    for key, vals in values.items():
        if key in always_null or len(vals) != 1:
            continue
        (only,) = tuple(vals)
        (shape_constant if isinstance(only, str) and only.startswith("<") else constant).append(key)
    return {"total": total, "always_null": always_null, "constant": sorted(constant),
            "shape_constant": sorted(shape_constant)}


# ⚠ THE HOMOGENEITY KEY IS `env_fingerprint.label`, NOT `env_fingerprint` (fixed 2026-08-01,
# session 4). `env_fingerprint` is a DICT -- `{env_json_sha256, label}` -- so `flatten()` expands it
# to two dotted paths and `r.get("env_fingerprint")` returned None on EVERY record: `fps` stayed
# empty and `split_fingerprint` was unconditionally `{}`. The determinism envelope, one of the five
# mandated per-pass computations, checked NOTHING, and because the panel only prints when it finds
# something, its silence read as clean. Third instance of this tool committing the error it exists
# to detect (after val_fitness and the fixed-depth globs).
# `env_json_sha256` is the WRONG key in the other direction: it hashes env.json, which carries the
# SEED, so it is distinct per record BY DESIGN -- grouping on it reports every 30-seed unit as
# "30 fingerprints", a catastrophic false alarm (my P137). `label` is the quantity the 2026-07-26
# CPU-lane change stamped `|dev=<device>` into, and it is the one that must be constant per unit.
_FINGERPRINT_KEY = "env_fingerprint.label"


def panel_homogeneity(rows):
    """Determinism envelope: within one comparison unit every record must share an env_fingerprint
    label (device included -- it is stamped as |dev=<device>) and hold ONE seed set. A unit split
    across two labels breaks the CRN pairing every paired contrast rests on."""
    fps, seeds = defaultdict(set), defaultdict(list)
    for tier, unit, _, r in rows:
        if "__unreadable__" in r:
            continue
        fp = r.get(_FINGERPRINT_KEY)
        if fp is not None:
            fps[unit].add(str(fp))
        # Only the test tiers hold seed replicates -- see SEED_REPLICATE_TIERS.
        if tier in SEED_REPLICATE_TIERS and r.get("seed") is not None:
            seeds[unit].append(r["seed"])
    split = {u: sorted(v) for u, v in fps.items() if len(v) > 1}
    dupes = {u: len(s) - len(set(s)) for u, s in seeds.items() if len(s) != len(set(s))}
    devices = defaultdict(int)
    for unit, fp_set in fps.items():
        for fp in fp_set:
            m = re.search(r"\|dev=([^|]+)", fp)
            devices[m.group(1) if m else "unstamped"] += 1
    return {"units": len(fps), "split_fingerprint": split, "duplicate_seeds": dupes,
            "device_mix": dict(devices), "records_seen": sum(len(v) for v in seeds.values())}


def panel_periodic_failure(rows):
    """The D17 state-reset limit cycle, censused on BOTH sides of the R115 floor.

    CREDIT: the mechanism is `docs/ops/probe_safe_default_cycle.py` (D17, 2026-07-30) --
    ``safe_call`` returns ``reward_state=None`` on failure, so a stateful reward whose
    state-dependent branch raises resets its own counter and fails again with a FIXED PERIOD;
    the substitution fraction is then 1/k and encodes the RESET PERIOD, not the severity.

    WHY THIS PANEL EXISTS. That probe's ``breaching_units()`` filters ``frac >= 0.10``, so it
    enumerates only periods k <= 10 and is structurally blind to the long-period half -- which is
    exactly the half that PASSES R115. Measured 2026-08-01: five sub-floor periodic candidates,
    one of them a FROZEN WINNER (`placebo_shuffled-g0-c3`, 1/11), whose reward's entire stateful
    mechanism therefore never engaged across 400,000 training steps.
    """
    out = []
    for tier, _, rel, r in rows:
        if tier != "search" or "__unreadable__" in r:
            continue
        d, c = r.get("metrics.train_safe_default_count"), r.get("metrics.train_safe_call_count")
        if not d or not c:
            continue
        frac = d / c
        recip = 1.0 / frac
        k = round(recip)
        # A near-integral reciprocal is the deterministic-period signature. The tolerance admits a
        # period-k cycle truncated at episode boundaries and excludes an arbitrary fraction.
        if 2 <= k <= 2000 and abs(recip - k) <= 0.02:
            out.append((rel, r.get("arm"), frac, k, frac >= 0.10))
    return sorted(out, key=lambda x: -x[2])


def panel_test_tier_substitution(rows):
    """SAFE_DEFAULT substitution in the TEST trainings -- the ones the endpoints are computed from.

    R115 is a SEARCH-stage eligibility rule; nothing else looks at the test records' own counters,
    yet every test seed retrains for 400,000 steps under the SELECTED reward. Measured 2026-08-01:
    two confirmatory canon units (`differential_downside_ratio`, `differential_sharpe`) carry 5
    substituted calls each out of 12,000,000 -- immaterial, but NOT zero, so the sentence "no
    confirmatory training used SAFE_DEFAULT" is false while "zero R115 breaches on the confirmatory
    line" is true. Keep the distinction; a marker can check it.
    """
    agg = defaultdict(lambda: [0, 0, 0])            # unit -> [seeds_with_any, n_seeds, total_subs]
    for tier, unit, _, r in rows:
        if not tier.startswith("test") or "__unreadable__" in r:
            continue
        d, c = r.get("metrics.train_safe_default_count"), r.get("metrics.train_safe_call_count")
        if c is None:
            continue
        a = agg[unit]
        a[1] += 1
        if d:
            a[0] += 1
            a[2] += d
    return {u: tuple(v) for u, v in agg.items() if v[0]}


def panel_sanity(rows):
    """Magnitude / sign / finiteness of the outcome measure. A non-finite or absent val_fitness on
    a completed record is a defect; a perfectly degenerate one is the A10/A11 tell again."""
    bad_finite, missing, degenerate = [], [], []
    by_unit = defaultdict(lambda: defaultdict(list))
    for tier, unit, rel, r in rows:
        if "__unreadable__" in r:
            continue
        for field in OUTCOME_BY_TIER.get(tier, ()):
            val = r.get(field)
            if val is None:
                missing.append((rel, field))
            elif not isinstance(val, (int, float)) or not math.isfinite(val):
                bad_finite.append((rel, field, val))
            elif tier in SEED_REPLICATE_TIERS:
                # Degeneracy is only meaningful where records are seed replicates of one unit.
                by_unit[unit][field].append(val)
    for unit, fields in by_unit.items():
        for field, vals in fields.items():
            if len(vals) >= 5 and len(set(vals)) == 1:
                degenerate.append((unit, field, len(vals), vals[0]))
    return {"non_finite": bad_finite, "missing": missing, "degenerate_units": degenerate}


def panel_unreadable(rows):
    return [rel for _, _, rel, r in rows if "__unreadable__" in r]


def selftest() -> int:
    """Prove each panel CAN fire. Three of this tool's panels have shipped a false clean; a check
    that has never been shown to fail certifies nothing. Every case below is FALSIFYING -- it
    injects the defect and asserts the panel reports it, then asserts a clean input reports nothing.
    """
    ok = True

    def check(name, cond):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok &= bool(cond)

    # ⚠ THE FIXTURE IS BUILT FROM THE REAL NESTED SCHEMA AND PUT THROUGH `flatten()` -- it must NEVER
    # be keyed on `_FINGERPRINT_KEY`. The first version of this selftest did exactly that, so the
    # fixture matched whatever the constant said and the suite PASSED with the pre-fix key
    # `"env_fingerprint"` still in place: a test built from the constant it is testing cannot detect
    # a wrong constant. Note `env_json_sha256` deliberately VARIES per record -- keying on it (my
    # P137) must make "clean on a homogeneous unit" fail, and it does.
    def _rec(i, **over):
        raw = {"seed": i,
               "env_fingerprint": {"label": "campaign:u:test[0,10)|dev=cpu",
                                   "env_json_sha256": f"{i:064x}"},
               "metrics": {"test_sharpe": 0.1 + i, "test_cvar05": -0.01 - i,
                           "train_safe_default_count": 0, "train_safe_call_count": 400000}}
        raw.update(over)
        return flatten(raw)

    good = [("test_core", "test/u", f"test/u/u-s{i}/record.json", _rec(i)) for i in range(6)]
    h = panel_homogeneity(good)
    check("homogeneity sees the unit at all (units == 1)", h["units"] == 1)
    check("homogeneity clean on a homogeneous unit", not h["split_fingerprint"])
    rows = [(t, u, p, _rec(i, env_fingerprint={"label": "campaign:u:test[0,10)|dev=cuda",
                                               "env_json_sha256": f"{i:064x}"}) if i == 0 else r)
            for i, (t, u, p, r) in enumerate(good)]
    check("homogeneity FIRES on an injected device split",
          len(panel_homogeneity(rows)["split_fingerprint"]) == 1)
    check("homogeneity FIRES on a duplicate seed",
          bool(panel_homogeneity(good + [good[0]])["duplicate_seeds"]))

    miss = [(t, u, p, {k: v for k, v in r.items() if k != "metrics.test_sharpe"})
            for t, u, p, r in good]
    check("sanity reports a MISSING outcome field", len(panel_sanity(miss)["missing"]) == 6)
    check("sanity clean when the outcome is present", not panel_sanity(good)["missing"])
    nonfin = [(t, u, p, {**r, "metrics.test_sharpe": float("nan")}) for t, u, p, r in good]
    check("sanity FIRES on a non-finite outcome", len(panel_sanity(nonfin)["non_finite"]) == 6)
    degen = [(t, u, p, {**r, "metrics.test_sharpe": 0.5}) for t, u, p, r in good]
    check("sanity FIRES on a degenerate unit", len(panel_sanity(degen)["degenerate_units"]) == 1)

    srch = [("search", "s/a", f"search/a/c{i}/record.json",
             flatten({"arm": "scalar",
                      "metrics": {"train_safe_default_count": d,
                                  "train_safe_call_count": 400000}}))
            for i, d in enumerate([0, 36364, 133333, 7777])]
    per = panel_periodic_failure(srch)
    check("periodic panel finds 1/11 and 1/3 and NOT the aperiodic one",
          sorted(k for _, _, _, k, _ in per) == [3, 11])
    check("periodic panel flags the sub-floor member as ADMITTED",
          any(k == 11 and not b for _, _, _, k, b in per))

    dirty = [(t, u, p, {**r, "metrics.train_safe_default_count": 1}) for t, u, p, r in good]
    check("test-tier substitution FIRES", panel_test_tier_substitution(dirty) == {"test/u": (6, 6, 6)})
    check("test-tier substitution silent when clean", panel_test_tier_substitution(good) == {})

    c = panel_constant_fields(good)
    check("constant sweep finds the constant fingerprint label",
          _FINGERPRINT_KEY in c["constant"])

    # An EMPTY BULKY field must reach the always-null sweep. Against the pre-fix flatten() these two
    # FAIL: `None` collapsed to the string "<bulk>" and "" to "<str:0>", so neither counted as null
    # -- which is why the sweep could never have found A11 (`feedback_block` empty on 100%).
    empt = [("search", "s/a", f"search/a/c{i}/record.json",
             flatten({"arm": "scalar", "feedback_block": "", "val_returns": None,
                      "reward_source": "def reward(): pass"}))
            for i in range(4)]
    ce = panel_constant_fields(empt)
    check("null sweep sees an EMPTY bulky field (feedback_block == '')",
          "feedback_block" in ce["always_null"])
    check("null sweep sees a NULL bulky field (val_returns is None)",
          "val_returns" in ce["always_null"])
    check("a NON-empty bulky field is still summarised, not compared by value",
          "reward_source" in ce["shape_constant"])
    print("\nselftest:", "ALL PASS" if ok else "FAILURES ABOVE")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--full", action="store_true", help="print every panel, not just deltas")
    ap.add_argument("--selftest", action="store_true",
                    help="prove every panel can FIRE; run after any edit to this file")
    ap.add_argument("--state", default=DEFAULT_STATE)
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    if not os.path.isdir(RUN4):
        print(f"FATAL  archive not found: {RUN4}", file=sys.stderr)
        return 2

    rows = load_records()
    if not rows:
        # Fail LOUD. An empty walk means the tree moved or the glob depth is wrong -- it does NOT
        # mean the campaign is clean. This is error P121 encoded as a guard.
        print("FATAL  walked the archive and found ZERO records. The tree layout or glob depth has\n"
              "       changed. DO NOT read this as a clean campaign -- fix the globs in TIERS.",
              file=sys.stderr)
        return 2

    now = {
        "counts": panel_counts(rows),
        "safe_default": panel_safe_default(rows),
        "constant": panel_constant_fields(rows),
        "homogeneity": panel_homogeneity(rows),
        "sanity": panel_sanity(rows),
        "unreadable": panel_unreadable(rows),
        "periodic": panel_periodic_failure(rows),
        "test_subst": panel_test_tier_substitution(rows),
    }
    prev = {}
    if os.path.exists(args.state):
        try:
            with open(args.state, encoding="utf-8") as fh:
                prev = json.load(fh)
        except Exception:
            prev = {}

    first = not prev
    show = args.full or first
    said = []

    # --- counts -------------------------------------------------------------------------------
    pc = prev.get("counts", {})
    if show or now["counts"] != pc:
        delta = {k: now["counts"][k] - pc.get(k, 0) for k in now["counts"]}
        said.append("COUNTS   " + "  ".join(
            f"{k}={v}{'' if first else f' ({delta[k]:+d})'}" for k, v in sorted(now["counts"].items())))

    # --- ALWAYS reported, changed or not: things that are simply wrong -------------------------
    if now["unreadable"]:
        said.append(f"UNREADABLE  {len(now['unreadable'])} record(s) failed to parse: "
                    + ", ".join(now["unreadable"][:5]))
    s = now["sanity"]
    if s["non_finite"]:
        said.append(f"NON-FINITE val_fitness on {len(s['non_finite'])} record(s): {s['non_finite'][:5]}")
    if s["degenerate_units"]:
        said.append(f"DEGENERATE  {len(s['degenerate_units'])} unit(s) have an identical val_fitness "
                    f"on >=5 seeds -- a real result or a stuck pipe, decide which: {s['degenerate_units'][:3]}")
    # `missing` was computed and DISCARDED until 2026-08-01. An outcome field that is ABSENT is
    # invisible to every check that reads a value: it is not non-finite (that needs a value) and it
    # never enters the degeneracy grouping. Absence must be reported separately from wrongness.
    if s["missing"]:
        said.append(f"MISSING OUTCOME  {len(s['missing'])} record(s) have no outcome field at all: "
                    f"{s['missing'][:5]}")
    h = now["homogeneity"]
    # FAIL LOUD if the envelope check saw nothing. Silence here previously meant "the key lookup
    # returned None on every record", not "every unit is homogeneous".
    if h["units"] == 0:
        said.append("HOMOGENEITY PANEL SAW ZERO UNITS -- it is not reporting clean, it is not "
                    f"reporting at all. Check that '{_FINGERPRINT_KEY}' still exists in the schema.")
    if h["split_fingerprint"]:
        said.append(f"HETEROGENEOUS UNIT  {len(h['split_fingerprint'])} comparison unit(s) span >1 "
                    f"env_fingerprint -- CRN pairing is broken for these: "
                    f"{list(h['split_fingerprint'])[:3]}")
    if h["duplicate_seeds"]:
        said.append(f"DUPLICATE SEEDS  {h['duplicate_seeds']}")

    # --- report-only execution quantity -------------------------------------------------------
    if show or now["safe_default"] != prev.get("safe_default", {}):
        lines = ["SAFE-DEFAULT substitution by arm (search tier, Wilson 95%)"]
        bands = []
        for arm, (k, n, lo, hi, mean_frac) in sorted(now["safe_default"].items()):
            lines.append(f"    {arm:<20} {k:>4}/{n:<5} = {100*k/n:5.1f}%  [{lo:4.1f},{hi:5.1f}]"
                         f"   mean frac {mean_frac:.5f}")
            bands.append((k / n, lo, hi))
        # ⚠ THE ALARM COMPARES INTERVALS, NOT POINT ESTIMATES (fixed 2026-08-01, session 4).
        # The original rule was `max(rate) > 2 * min(rate)`, which at these counts fires on noise:
        # on the PERIODIC sub-class (18 events over 5 arms) it declared "ARM-DIFFERENTIAL" while a
        # 200,000-draw permutation test returned p = 0.67. Flagging a point-estimate ratio against
        # nothing is the exact defect CLAUDE.md's scope clause, consequence 1, names -- committed by
        # the alarm meant to protect identification. Disjoint Wilson intervals are the real signal.
        if bands:
            top = max(bands, key=lambda b: b[0])
            bot = min(bands, key=lambda b: b[0])
            if top[1] > bot[2]:
                lines.append("    >> ARM-DIFFERENTIAL: the extreme arms' Wilson intervals are "
                             "DISJOINT. This can manufacture a between-arm effect. INVESTIGATE "
                             "before it reaches the write-up.")
        said.append("\n".join(lines))

    # --- the D17 limit cycle, both sides of the R115 floor ------------------------------------
    per, pper = now["periodic"], prev.get("periodic", [])
    if show or [x[0] for x in per] != [x[0] for x in pper]:
        lines = [f"PERIODIC REWARD FAILURE (D17 state-reset limit cycle): {len(per)} candidate(s); "
                 f"{sum(1 for x in per if not x[4])} sit BELOW the R115 floor and therefore PASS it"]
        for rel, arm, frac, k, breach in per:
            lines.append(f"    {rel:<66} {arm:<18} {frac:.6f} = 1/{k}  "
                         f"{'R115 breach' if breach else 'ADMITTED by R115'}")
        lines.append("    >> the fraction encodes the RESET PERIOD, not the severity: at 1/k the "
                     "reward executed its intended logic on NO call whose state had advanced.")
        said.append("\n".join(lines))

    # --- substitution inside the TEST trainings the endpoints are computed from ----------------
    ts, pts = now["test_subst"], prev.get("test_subst", {})
    if show or ts != pts:
        lines = ["SAFE-DEFAULT INSIDE THE TEST TRAININGS (the endpoints' own rollouts)"]
        for unit, (k, n, tot) in sorted(ts.items()):
            conf = "CONFIRMATORY" if unit.startswith(("test/", "test_h3")) else "report-only leg"
            lines.append(f"    {unit:<52} {k}/{n} seeds, {tot} substituted call(s)  [{conf}]")
        if not ts:
            lines.append("    none")
        said.append("\n".join(lines))

    # --- the constant/null sweep --------------------------------------------------------------
    c, pcst = now["constant"], prev.get("constant", {})
    new_null = sorted(set(c["always_null"]) - set(pcst.get("always_null", [])))
    new_const = sorted(set(c["constant"]) - set(pcst.get("constant", [])))
    if show:
        said.append(f"CONSTANT/NULL SWEEP over {c['total']} records\n"
                    f"    always-null ({len(c['always_null'])}): {c['always_null']}\n"
                    f"    constant    ({len(c['constant'])}): {c['constant']}\n"
                    "    >> A field that never moves is invisible to every gate that watches values "
                    "move (findings A10/A11). Confirm each is constant BY DESIGN.")
    elif new_null or new_const:
        said.append(f"CONSTANT/NULL SWEEP -- NEWLY always-null: {new_null}  NEWLY constant: {new_const}")

    if said:
        print("\n".join(said))
    else:
        print(f"no change ({now['counts'].get('TOTAL')} records, "
              f"{h['units']} units, devices {h['device_mix']})")

    os.makedirs(os.path.dirname(args.state), exist_ok=True)
    with open(args.state, "w", encoding="utf-8") as fh:
        json.dump(now, fh, indent=1, sort_keys=True, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
