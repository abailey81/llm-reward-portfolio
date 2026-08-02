"""DEEP SCIENCE AUDIT -- is every record LOGICAL, MEANINGFUL and free of a science issue?

★ WHY THIS EXISTS, AND WHY IT IS NOT A DUPLICATE OF WHAT WE ALREADY RUN (RUN 14, 2026-08-02).
Tamer: *"dive very deep, and look at the every record, and ensure absolutely everything there is
flawless, and the records are logical, meaningful, no science issue."*

Two per-record instruments already run archive-wide and both come back CLEAN, but neither asks a
SCIENTIFIC question:

  record_validator.py      R1-R9 : contract fields, hashes, identity, seed/generation tokens,
                                   counter ordering, series-length AGREEMENT, endpoint replay,
                                   cross-tier hash chain.
  record_provenance_seal.py P1-P4 : the record vs the files beside it -- env.json digest,
                                   reward.py hash, git commit, wall-clock plausibility.

A record can satisfy every one of those and still be scientifically worthless: trained for a tenth
of the registered budget, holding a return series of the wrong LENGTH, carrying a policy whose
weights do not sum to one, produced by a reward that fell back to its safe default on every call,
or -- worst of all -- DISAGREEING with a second record that shares its arm, seed and reward hash,
which would mean the determinism the whole reproducibility claim rests on does not hold.

R7 is the sharp illustration. It checks that a record's series share ONE length AS EACH OTHER. It
does NOT check that the length is the REGISTERED test length, so a record holding 200 sessions
instead of 1,571 passes R7 while describing a different experiment.

★ EFFECT-BLIND BY CONSTRUCTION, AND THIS IS A HARD CONSTRAINT, NOT A COURTESY.
The blinding rule binds on the sealed test arms. This module therefore NEVER prints, returns, or
compares a Sharpe, a CVaR, a fitness, or any arm-level performance aggregate. It reads outcome
SERIES only to ask structural questions of them -- are they finite, the right length, non-degenerate,
byte-identical to their own duplicate -- and reports COUNTS and VIOLATIONS. Where a violation must
name a magnitude it names the magnitude of the BREACH (a data-integrity fact), never a performance
value, and never an arm ranking. Nothing here can reveal which arm won.

THE CHECKS
  S1  numerical health      -- no NaN/Inf in any archived series
  S2  registered test length-- every test series is exactly T=1571 (the executed test length that
                               PREREGISTRATION.md's N6 note measures the design against)
  S3  training budget       -- train_safe_call_count == 400,000, the FIXED per-candidate budget
                               (config/algos.yaml + config/campaign.yaml, mirrored by the preflight)
  S4  DETERMINISM           -- records sharing (arm, seed, reward_source_hash) must have
                               BYTE-IDENTICAL test_returns. This is the reproducibility claim,
                               tested against the archive rather than asserted.
  S5  reward degeneracy     -- train_safe_default_count / train_safe_call_count. A reward that
                               falls back to its safe default is not the reward we claim to study.
  S6  allocation validity   -- portfolio weights finite, non-negative, summing to 1 within tolerance
  S7  magnitude sanity      -- no single-session return beyond a physically implausible band, and
                               no zero-variance (degenerate/dead) policy series
  S8  universe invariance   -- every record must see the SAME number of steps; a record that saw a
                               different window is not comparable to its CRN partners
  S9  pnl identity          -- per_period_pnl vs test_returns (the A62 disclosure, tracked)
  S10 BANKED RUNG / CRN     -- reports each line's BANKABLE CONTIGUOUS PREFIX: the largest r such
                               that every paired (non-baseline) arm holds every seed in {0..r-1}.
                               Under R101 the COMMON prefix across lines IS the reported result, so
                               this MEASURES the headline from the archive rather than forecasting it.

                               ⚠ HONEST SCOPE, CORRECTED AFTER AN END-TO-END TEST OF MY OWN CLAIM.
                               I first described S10 as DETECTING pairing breaches. It does not, and
                               it structurally cannot: the prefix is defined as the MINIMUM over
                               arms, so every arm necessarily holds every seed below it and the
                               "missing seed" branch is UNREACHABLE by construction. A synthetic
                               end-to-end run against this module confirmed it -- an arm with a hole
                               at seed 2 collapses the prefix to 2 rather than reporting a breach.
                               The branch is retained as defence-in-depth against a BUG in the
                               prefix computation itself, and is documented as that rather than
                               advertised as a pairing detector. The MEASUREMENT is the deliverable.

                               ⚠ THE PREFIX FRAMING IS STILL LOAD-BEARING, for the OPPOSITE reason:
                               not to catch breaches but to avoid MANUFACTURING them. Asking "are
                               the seed sets equal?" flags every line that is MID-SWEEP: the C4 path
                               submits all six assurance blocks at once, so seeds land out of order
                               across tiers and the sets are ragged BY CONSTRUCTION while work is in
                               flight. The cumulative-tier rule banks a rung only when it and every
                               rung below are complete, so the meaningful object is the CONTIGUOUS
                               PREFIX. My first version lacked this and reported a healthy in-flight
                               line as a defect (P195, the P186 class).

USAGE
    python docs/analysis/record_science_audit.py                # whole archive
    python docs/analysis/record_science_audit.py --selftest     # falsification tests
    python docs/analysis/record_science_audit.py --root <dir>   # a subtree

EXIT 0 = clean, 1 = at least one science issue, 2 = the audit could not run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

# --- registered constants, each with the file that fixes it ---------------------------------- #
#: The EXECUTED test length. PREREGISTRATION.md's N6 endpoint note reasons explicitly "at the
#: executed test length T=1571", and every archived test record observed carries 1571.
REGISTERED_TEST_LEN = 1571
#: The FIXED per-candidate training budget (config/algos.yaml:16 and config/campaign.yaml:20,
#: mirrored by the preflight budget guard). R77 raised it to the measured knee.
REGISTERED_TRAIN_STEPS = 400_000
#: The registered assurance-tier ladder (Amendment E1 / R101). A rung BANKS only when it and
#: every rung below it are complete, which is why S10 measures a CONTIGUOUS PREFIX.
REGISTERED_RUNGS = [30, 100, 189, 279, 340, 403, 568]
#: A single-session portfolio return outside this band is not a market move, it is a bug. The
#: gold panel's own worst session is far inside it; this is a physical-impossibility screen, NOT a
#: performance judgement, and it is deliberately loose so that only defects trip it.
MAX_ABS_SESSION_RETURN = 1.0
#: Weights are a simplex allocation; allow float drift only.
WEIGHT_SUM_TOL = 1e-4
#: ★ THE FALLBACK FLOOR IS NOT MINE TO CHOOSE — it is REGISTERED as R115
#: (`config/preregistration.yaml: fitness.winner_max_fallback_frac`, enforced at
#: `scripts/run_campaign.py:754`), and it is inside the frozen hash. Read it from the registration
#: rather than hardcoding a number here: a second, hand-picked threshold living in an audit tool is
#: exactly how an analysis quietly acquires a forking path.
#:
#: MY FIRST VERSION HARDCODED 1% AND WAS WRONG. It reported 95 "science issues" that were nothing of
#: the sort -- candidates comfortably inside the registered tolerance, i.e. the authoring-reliability
#: phenomenon this campaign EXISTS to measure (the numeracy bottleneck). A check calibrated to the
#: auditor's intuition instead of the registered design manufactures alarm.
REGISTERED_FALLBACK_KEY = ("fitness", "winner_max_fallback_frac")


def registered_fallback_floor(root: Path = Path(".")) -> float:
    """The registered winner-eligibility fallback floor. FAILS LOUD if absent.

    Mirrors `run_campaign.py`'s own refusal: a missing key means the R115 eligibility floor is not
    in force, and silently substituting a default would let this audit pass a campaign the design
    would have refused.
    """
    p = root / "config" / "preregistration.yaml"
    txt = p.read_text(encoding="utf-8", errors="replace")
    # Deliberately a targeted scan rather than a YAML load: this module must not import a parser
    # that could reformat, and the key is a scalar on its own line.
    for line in txt.splitlines():
        s = line.strip()
        if s.startswith("winner_max_fallback_frac:"):
            return float(s.split(":", 1)[1].split("#")[0].strip())
    raise SystemExit(
        "fitness.winner_max_fallback_frac is missing from config/preregistration.yaml -- the R115 "
        "winner-eligibility floor is what keeps a contaminated reward out of the sealed leg, and "
        "this audit will not substitute a value for it.")

SERIES_FIELDS = ("test_returns", "per_period_pnl", "test_gross", "test_turnover")


def _finite_violations(seq, label: str, cap: int = 3) -> list[str]:
    """Indices of non-finite entries, as messages. Reports POSITIONS, never values."""
    out: list[str] = []
    for i, v in enumerate(seq):
        if not isinstance(v, (int, float)) or not math.isfinite(float(v)):
            out.append(f"S1 {label}[{i}] is not finite")
            if len(out) >= cap:
                out.append(f"S1 {label}: ... (further non-finite entries suppressed)")
                break
    return out


def _series_digest(seq) -> str:
    """A stable digest of a float series, for EQUALITY testing only.

    repr() of a Python float round-trips exactly, so two series digest equal iff they are
    element-wise identical. Using a digest rather than the series keeps determinism testing O(1)
    in memory across a 40,000-record archive -- and keeps the VALUES out of this program's output,
    which is what makes S4 effect-blind.
    """
    h = hashlib.sha256()
    for v in seq:
        h.update(repr(float(v)).encode("ascii"))
        h.update(b",")
    return h.hexdigest()


def audit_record(rec: dict, path: Path, fallback_floor: float = 0.10) -> list[str]:
    """Every S-check that is answerable from ONE record. Returns violation messages.

    ``fallback_floor`` is the REGISTERED R115 winner-eligibility floor, passed in so the caller
    reads it from the frozen registration exactly once.
    """
    bad: list[str] = []
    metrics = rec.get("metrics") or {}

    def series(name):
        v = rec.get(name)
        if v is None:
            v = metrics.get(name)
        return v if isinstance(v, list) else None

    is_test = series("test_returns") is not None

    # S1 -- numerical health across every archived series ------------------------------------- #
    for fld in SERIES_FIELDS:
        s = series(fld)
        if s:
            bad.extend(_finite_violations(s, fld))
    # ...including the per-step EXPOSURE diagnostics, which are full-length series in their own
    # right (eff_n / hhi / max_weight / top5) and are read by the mechanism exhibits.
    expo = metrics.get("test_exposure")
    if isinstance(expo, dict):
        for k, v in expo.items():
            if isinstance(v, list) and v:
                bad.extend(_finite_violations(v, f"test_exposure.{k}"))

    tr = series("test_returns")

    # S2 -- the REGISTERED test length, not merely self-agreement ------------------------------ #
    if is_test and len(tr) != REGISTERED_TEST_LEN:
        bad.append(f"S2 test_returns length {len(tr)} != registered executed length "
                   f"{REGISTERED_TEST_LEN} -- this record describes a different test window")

    # S3 -- the fixed training budget ----------------------------------------------------------- #
    calls = metrics.get("train_safe_call_count", rec.get("train_safe_call_count"))
    # Baselines are analytic allocators with no authored-reward training loop; they legitimately
    # archive 0 calls, so they are exempt rather than failed (checked by arm name, not by luck).
    is_baseline = str(rec.get("arm", "")).startswith("baseline_")
    if is_test and not is_baseline and isinstance(calls, int) and calls != REGISTERED_TRAIN_STEPS:
        bad.append(f"S3 train_safe_call_count {calls:,} != registered budget "
                   f"{REGISTERED_TRAIN_STEPS:,} -- incomparable training effort")

    # S5 -- reward degeneracy, AGAINST THE REGISTERED FLOOR --------------------------------------- #
    # A FAILURE is a SEALED-TEST record at or above the registered R115 eligibility floor: that
    # record's reward was substituted often enough that the design itself declares it ineligible,
    # and the H2 contrast would be confounded with EXECUTION QUALITY rather than reward CONTENT.
    # Below the floor is the measured phenomenon, not a defect -- reported as a DISCLOSURE by the
    # caller, never as an alarm.
    dflt = metrics.get("train_safe_default_count", rec.get("train_safe_default_count"))
    if isinstance(calls, int) and isinstance(dflt, int) and calls > 0:
        frac = dflt / calls
        if is_test and frac >= fallback_floor:
            bad.append(f"S5 SEALED-TEST record at {frac:.2%} safe-default fallback, AT OR ABOVE the "
                       f"registered R115 eligibility floor {fallback_floor:.0%} -- the reported "
                       f"result would rest on a reward the design declares ineligible")
        elif frac > 0:
            bad.append(f"__S5_DISCLOSE__{'TEST' if is_test else 'search'}|{frac}")

    # S6 -- allocation validity ----------------------------------------------------------------- #
    # SHAPE, READ FROM THE ARCHIVE RATHER THAN ASSUMED: `weights` is a list of SNAPSHOTS, each a
    # vector over the `asset_idx` TRACKED SUBSET (20 of the universe), and `other[i]` carries the
    # residual weight held outside that subset at snapshot i. So the simplex identity to test is
    #     sum(weights[i]) + other[i] == 1
    # Testing sum(weights[i]) == 1 alone would flag every record, because the tracked subset is a
    # subset by construction. (My first version did exactly that, and also treated `other` as a
    # scalar -- it is a per-snapshot list. Both were caught by running it.)
    alloc = metrics.get("test_alloc")
    if isinstance(alloc, dict):
        w = alloc.get("weights")
        other = alloc.get("other")
        if isinstance(w, list) and w and isinstance(w[0], list):
            for r_i, row in enumerate(w):
                if not all(isinstance(x, (int, float)) and math.isfinite(float(x)) for x in row):
                    bad.append(f"S6 weights snapshot {r_i} holds a non-finite entry")
                    break
                if any(float(x) < -WEIGHT_SUM_TOL for x in row):
                    bad.append(f"S6 weights snapshot {r_i} holds a NEGATIVE weight "
                               f"(the design is long-only)")
                    break
                resid = 0.0
                if isinstance(other, list) and r_i < len(other):
                    o = other[r_i]
                    if isinstance(o, (int, float)) and math.isfinite(float(o)):
                        resid = float(o)
                    else:
                        bad.append(f"S6 alloc.other[{r_i}] is not a finite number")
                        break
                tot = float(sum(float(x) for x in row)) + resid
                if abs(tot - 1.0) > 1e-3:
                    bad.append(f"S6 snapshot {r_i}: tracked weights + other = {tot:.6f}, not 1 "
                               f"-- the allocation is not a simplex")
                    break

    # S7 -- magnitude + non-degeneracy ---------------------------------------------------------- #
    if tr:
        finite = [float(x) for x in tr if isinstance(x, (int, float)) and math.isfinite(float(x))]
        if finite:
            worst = max(abs(x) for x in finite)
            if worst > MAX_ABS_SESSION_RETURN:
                bad.append(f"S7 a single-session return of magnitude {worst:.3f} exceeds the "
                           f"physical screen {MAX_ABS_SESSION_RETURN} -- a defect, not a market move")
            if len(set(finite)) == 1:
                bad.append("S7 test_returns is CONSTANT -- a dead/degenerate policy series")

    # S9 -- the A62 disclosure ------------------------------------------------------------------ #
    ppl = series("per_period_pnl")
    if tr is not None and ppl is not None and len(tr) == len(ppl):
        if all(float(a) == float(b) for a, b in zip(tr, ppl)):
            bad.append("__A62_IDENTICAL__")     # tallied, not a failure

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

    floor = registered_fallback_floor(Path("."))
    failures: list[tuple[str, str]] = []
    disclose: dict[str, list[float]] = {"TEST": [], "search": []}
    n = n_test = a62 = 0
    step_counts: Counter[int] = Counter()
    # S4: (arm, seed, reward_hash) -> {series digest -> first path}
    det: dict[tuple, dict[str, str]] = defaultdict(dict)
    det_violations: list[str] = []
    # S10: line -> arm -> set(seeds), test tier only (pairing is a test-leg property)
    pair_seeds: dict[str, dict[str, set]] = defaultdict(lambda: defaultdict(set))

    for p in sorted(root.rglob("record.json")):
        # a partially-pulled record lives under a dot-prefixed dir and is not archive content
        if any(part.startswith(".") for part in p.parts):
            continue
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:                       # noqa: BLE001 -- an unreadable record IS a finding
            failures.append((str(p), f"S0 unreadable record: {exc}"))
            continue
        n += 1
        msgs = audit_record(rec, p, fallback_floor=floor)
        for m in msgs:
            if m == "__A62_IDENTICAL__":
                a62 += 1
            elif m.startswith("__S5_DISCLOSE__"):
                tier, frac = m[len("__S5_DISCLOSE__"):].split("|", 1)
                disclose[tier].append(float(frac))
            else:
                failures.append((str(p), m))

        metrics = rec.get("metrics") or {}
        tr = rec.get("test_returns")
        if tr is None:
            tr = metrics.get("test_returns")
        if isinstance(tr, list):
            n_test += 1
            step_counts[len(tr)] += 1
            try:
                _line = p.relative_to(root).parts[0]
            except ValueError:
                _line = "?"
            _arm = rec.get("arm")
            _sd = rec.get("seed")
            # baselines are the UNPAIRED H1 comparator family and legitimately carry their own
            # seed counts, so including them would manufacture raggedness that is by design
            if (_arm is not None and isinstance(_sd, int)
                    and not str(_arm).startswith("baseline_")):
                pair_seeds[_line][_arm].add(_sd)
            key = (rec.get("arm"), rec.get("seed"), rec.get("reward_source_hash"))
            dg = _series_digest(tr)
            seen = det[key]
            if dg not in seen and seen:
                first = next(iter(seen.values()))
                det_violations.append(
                    f"S4 DETERMINISM BREACH: {key[0]} seed={key[1]} same reward hash produced "
                    f"TWO DIFFERENT test_returns\n      {first}\n      {p}")
            seen.setdefault(dg, str(p))

    # S8 -- universe invariance ------------------------------------------------------------------ #
    s8: list[str] = []
    if len(step_counts) > 1:
        modal, modal_n = step_counts.most_common(1)[0]
        for ln, c in sorted(step_counts.items()):
            if ln != modal:
                s8.append(f"S8 {c} test record(s) hold {ln} steps against the modal {modal} "
                          f"({modal_n} records) -- they did not see the same window")


    # S10 -- CRN PAIRING within each line's BANKABLE CONTIGUOUS PREFIX -------------------------- #
    def _prefix(sd: set) -> int:
        """Largest r such that {0..r-1} is a subset of sd."""
        r = 0
        while r in sd:
            r += 1
        return r

    s10: list[str] = []
    line_prefix: dict[str, int] = {}
    for _line in sorted(pair_seeds):
        _arms = pair_seeds[_line]
        if not _arms:
            continue
        pre = min(_prefix(v) for v in _arms.values())
        line_prefix[_line] = pre
        # Inside the prefix the pairing must be exact. VERIFIED rather than assumed -- `pre` is a
        # minimum over arms, so this can only fail if the prefix computation itself is wrong, which
        # is precisely the kind of thing to check rather than trust.
        for _a, _v in sorted(_arms.items()):
            missing = [x for x in range(pre) if x not in _v]
            if missing:
                s10.append(f"S10 {_line}/{_a} is missing seed(s) {missing[:8]} BELOW the line's "
                           f"banked prefix {pre} -- CRN pairing is broken inside BANKED work")

    dup_keys = sum(1 for k, v in det.items() if len(v) > 1)

    print("=== DEEP SCIENCE AUDIT (S1-S10) -- are the records LOGICAL and MEANINGFUL? ===")
    print(f"  records audited        : {n:,}   (test-tier: {n_test:,})")
    print(f"  registered test length : {REGISTERED_TEST_LEN}   observed lengths: "
          f"{dict(step_counts) if len(step_counts) <= 4 else str(len(step_counts)) + ' distinct'}")
    print(f"  registered train budget: {REGISTERED_TRAIN_STEPS:,}")
    print(f"  determinism groups     : {len(det):,} distinct (arm, seed, reward_hash) keys; "
          f"{dup_keys} key(s) disagree")
    print()

    all_fail = [f"{m}\n      {p}" for p, m in failures] + det_violations + s8 + s10
    if all_fail:
        print(f"!! {len(all_fail)} SCIENCE ISSUE(S)")
        for msg in all_fail[:60]:
            print(f"  - {msg}")
        if len(all_fail) > 60:
            print(f"  ... and {len(all_fail) - 60} more")
    else:
        print("S1-S10 CLEAN -- every record is finite, the registered length, trained to the")
        print("registered budget, non-degenerate, simplex-valid, and every record sharing an")
        print("(arm, seed, reward hash) with another is BYTE-IDENTICAL to it.")

    print()
    print("=== S10 CRN PAIRING / BANKED RUNG (under R101 the COMMON rung IS the result) ===")
    _legs = {k: v for k, v in line_prefix.items() if k != "test_h3_singleshot"}
    if _legs:
        _common = min(_legs.values())
        _banked = max([r for r in REGISTERED_RUNGS if r <= _common], default=0)
        _slow = sorted(k for k, v in _legs.items() if v == _common)
        _lead = sorted(((v, k) for k, v in _legs.items()), reverse=True)[:1]
        print(f"  lines {len(_legs)}   COMMON contiguous prefix {_common}   "
              f"largest fully banked registered rung {_banked}")
        print(f"  set by {len(_slow)} line(s): " + ", ".join(_slow[:4])
              + (" ..." if len(_slow) > 4 else ""))
        if _lead and _lead[0][0] > _common:
            print(f"  furthest ahead: {_lead[0][1]} at prefix {_lead[0][0]} -- work above the")
            print("  common rung cannot raise the reported result until every line catches up")
        _nxt = next((r for r in REGISTERED_RUNGS if r > _common), None)
        if _nxt:
            print(f"  next rung {_nxt} needs {_nxt - _common} more contiguous seed(s) on the slowest")

    print()
    print("=== S5 DISCLOSURE: safe-default fallback BELOW the registered R115 floor ===")
    print(f"  registered winner_max_fallback_frac = {floor:.0%}  (read from the frozen registration)")
    for tier in ("TEST", "search"):
        fr = sorted(disclose[tier], reverse=True)
        if not fr:
            print(f"  {tier:6s}: no record carries any fallback")
            continue
        print(f"  {tier:6s}: {len(fr)} record(s) with a non-zero fallback; worst {fr[0]:.4%}; "
              f"margin to the floor {floor - fr[0]:.4%}")
    tw = max(disclose["TEST"], default=0.0)
    if tw > 0:
        print(f"  ==> the sealed test's worst case sits {floor - tw:.4%} below the floor. This is the")
        print("      AUTHORING-RELIABILITY phenomenon the campaign measures, INSIDE the registered")
        print("      tolerance -- a disclosure for the write-up, not a defect.")
    print()
    print(f"A62 DISCLOSURE: per_period_pnl identical to test_returns on {a62:,} record(s) "
          f"(a COUNT, not a value; no consumer reads per_period_pnl)")
    print()
    print("EFFECT-BLIND: no Sharpe, CVaR, fitness or arm aggregate was printed, returned or")
    print("compared. Outcome series were read ONLY for structure (finiteness, length, equality).")
    return 1 if all_fail else 0


def selftest() -> int:
    """Falsification tests -- each must FAIL a deliberately broken record.

    A check that cannot fail verifies nothing, so every S-check gets a mutant that trips it and a
    clean control that does not.
    """
    ok = lambda: {                                            # noqa: E731 -- terse fixture
        "arm": "distributional", "seed": 3, "reward_source_hash": "h",
        "metrics": {"train_safe_call_count": REGISTERED_TRAIN_STEPS,
                    "train_safe_default_count": 0,
                    "test_returns": [0.001 * ((i % 7) - 3) for i in range(REGISTERED_TEST_LEN)]},
    }
    cases: list[tuple[str, dict, str]] = []

    c = ok()
    cases.append(("clean control", c, ""))

    c = ok()
    c["metrics"]["test_returns"][5] = float("nan")
    cases.append(("S1 non-finite", c, "S1"))

    c = ok()
    c["metrics"]["test_returns"] = c["metrics"]["test_returns"][:200]
    cases.append(("S2 wrong length", c, "S2"))

    c = ok()
    c["metrics"]["train_safe_call_count"] = 40_000
    cases.append(("S3 short budget", c, "S3"))

    # S5 is now calibrated to the REGISTERED floor, so it must fail ABOVE it and stay silent BELOW.
    # Both directions are tested: a check that only fires upward would have re-created the false
    # alarm that the hardcoded 1% version produced.
    c = ok()
    c["metrics"]["train_safe_default_count"] = 40_000        # 10.0% -- AT the floor
    cases.append(("S5 sealed-test AT the registered floor", c, "S5"))

    c = ok()
    c["metrics"]["train_safe_default_count"] = 240_000       # 60% -- far above
    cases.append(("S5 sealed-test far above the floor", c, "S5"))

    c = ok()
    c["metrics"]["train_safe_default_count"] = 36_340        # 9.085% -- BELOW the floor
    cases.append(("S5 below the floor is a DISCLOSURE, not a failure", c, "__S5_DISCLOSE__"))

    # a SEARCH candidate (no test_returns) must never trip S5 as a failure, however bad it is
    c = ok()
    c["metrics"].pop("test_returns")
    c["metrics"]["train_safe_default_count"] = 399_920
    cases.append(("S5 search candidate at 99.98% is not a sealed-test failure", c,
                  "__S5_DISCLOSE__"))

    c = ok()
    c["metrics"]["test_alloc"] = {"weights": [[0.5, -0.2, 0.7]]}
    cases.append(("S6 negative weight", c, "S6"))

    c = ok()
    c["metrics"]["test_alloc"] = {"weights": [[0.2, 0.2, 0.2]]}
    cases.append(("S6 weights do not sum to 1", c, "S6"))

    c = ok()
    c["metrics"]["test_returns"][10] = 3.5
    cases.append(("S7 impossible magnitude", c, "S7"))

    c = ok()
    c["metrics"]["test_returns"] = [0.0] * REGISTERED_TEST_LEN
    cases.append(("S7 constant series", c, "S7"))

    # a BASELINE with 0 training calls must NOT trip S3 -- the exemption must be real
    c = ok()
    c["arm"] = "baseline_equal_weight"
    c["metrics"]["train_safe_call_count"] = 0
    cases.append(("baseline exempt from S3", c, ""))

    passed = failed = 0
    for name, rec, expect in cases:
        msgs = [m for m in audit_record(rec, Path("x")) if m != "__A62_IDENTICAL__"]
        hit = any(m.startswith(expect) for m in msgs) if expect else not msgs
        if hit:
            passed += 1
            print(f"  ok    {name}")
        else:
            failed += 1
            print(f"  FAIL  {name}: expected {expect or 'no violation'}, got {msgs}")

    # S10 prefix logic, with a mutation control. The prefix is the whole reason S10 does not
    # false-alarm on an in-flight line (P195), so it gets its own falsification.
    def _pref(sd):
        r = 0
        while r in sd:
            r += 1
        return r

    _cases = [
        (set(range(30)), 30, 'contiguous 0..29'),
        (set(range(30)) | {50, 51}, 30, 'ragged ABOVE the prefix is NOT counted'),
        (set(range(30)) - {7}, 7, 'a hole BELOW truncates the prefix'),
        (set(), 0, 'empty set'),
    ]
    for _sd, _want, _lbl in _cases:
        if _pref(_sd) == _want:
            passed += 1
            print(f'  ok    S10 prefix: {_lbl}')
        else:
            failed += 1
            print(f'  FAIL  S10 prefix: {_lbl} -> {_pref(_sd)}, want {_want}')

    # S4 digest equality: identical series digest equal, one changed element does not
    a = [0.1, 0.2, 0.3]
    b = [0.1, 0.2, 0.3]
    c2 = [0.1, 0.2, 0.30000000000000004]
    if _series_digest(a) == _series_digest(b) and _series_digest(a) != _series_digest(c2):
        passed += 1
        print("  ok    S4 digest distinguishes a 1-ulp difference")
    else:
        failed += 1
        print("  FAIL  S4 digest")

    print(f"\nselftest: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
