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


def _is_d18_nested(p, root) -> bool:
    """True for a D18 `shutil.move` NESTED duplicate: a unit dir whose name equals its parent's.

    D18 is root-caused in DEFERRED_FIXES_RUN4: `shutil.move` into an EXISTING directory nests, and
    the guard cannot close a TOCTOU race on a `read_root` shared by twelve drivers. Measured on
    2026-08-02: exactly TWO such directories exist archive-wide, both in the SEARCH tier, and both
    hold a record BYTE-IDENTICAL to the outer copy -- so no value diverges. But every `rglob`
    instrument counts them TWICE, so they are skipped here exactly as dot-prefixed `.pull_tmp`
    directories are. Skipped, never deleted: the archive is append-only evidence.
    """
    parts = p.parts
    return any(parts[i] == parts[i - 1] for i in range(1, len(parts) - 1))

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
    # S1b -- the TRAINING-CURVE channels, tallied as a DISCLOSURE rather than a failure.
    # `metrics.train_curve.return` is entirely NaN on 100% of records: SB3 logs `ep_rew_mean`, and
    # with a single long episode per training no episode closes inside the logging window, so the
    # channel is structurally empty. actor_loss / critic_loss / ent_coef / step are all POPULATED,
    # so the learning curve remains usable for convergence evidence and NO figure reads `return`
    # (checked across src/viz). It is a disclosure, not a defect -- but it must be VISIBLE, because
    # the CLEAN banner used to claim "every record is finite" while this channel was all-NaN.
    tc = metrics.get("train_curve")
    if isinstance(tc, dict):
        v = tc.get("return")
        if isinstance(v, list) and v:
            nums = [x for x in v if isinstance(x, (int, float))]
            if nums and all(isinstance(x, float) and math.isnan(x) for x in nums):
                bad.append("__TRAINCURVE_RETURN_ALL_NAN__")
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
    n = n_test = a62 = tc_nan = 0
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
        if _is_d18_nested(p, root):
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
            elif m == "__TRAINCURVE_RETURN_ALL_NAN__":
                tc_nan += 1
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

    # ROSTER AWARENESS (added after an independent audit, P198). The prefix is computed over arms
    # that have STARTED, so a line whose `distributional` and `scalar` test leg has not run yet
    # scores the same as a line that has completed all five arms. Measured on run 4: EIGHT of the
    # eleven non-h3 lines are missing whole arms, and the CORE line is missing BOTH `distributional`
    # and `scalar` -- i.e. the H2 co-primary pair has no sealed-test record there at all. Reporting
    # 'banked rung 30' without that materially overstates what is banked, so the roster is read
    # from the frozen-winner directories (the arms the design says each line RUNS) and any arm with
    # a frozen winner but no sealed-test record is named.
    roster: dict[str, set] = defaultdict(set)
    for _d in root.glob('frozen*'):
        if not _d.is_dir():
            continue
        _key = _d.name.replace('frozen_leg_', '').replace('frozen', '').strip('_') or 'core'
        for _w in _d.iterdir():
            if _w.is_dir() and _w.name.endswith('-winner'):
                roster[_key].add(_w.name[:-len('-winner')])

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
    # ★ THE REPLICATE COUNT IS THE FIGURE THAT MATTERS, AND IT WAS MISSING (P197).
    # `dup_keys` counts keys whose members DISAGREE. It does NOT say how many keys had more than
    # one member to compare in the first place -- so "0 disagree" reads as strong determinism
    # evidence when it may mean NOTHING WAS COMPARED. Measured on run 4: every sealed-test key has
    # exactly ONE record, so S4's comparison never fires. Printing this makes the vacuity visible
    # instead of letting a silent zero masquerade as a passed test.
    replicate_keys = sum(1 for v in det.values() if len(v) > 1 or sum(1 for _ in v) > 1)

    print("=== DEEP SCIENCE AUDIT (S1-S10) -- are the records LOGICAL and MEANINGFUL? ===")
    print(f"  records audited        : {n:,}   (test-tier: {n_test:,})")
    print(f"  registered test length : {REGISTERED_TEST_LEN}   observed lengths: "
          f"{dict(step_counts) if len(step_counts) <= 4 else str(len(step_counts)) + ' distinct'}")
    print(f"  registered train budget: {REGISTERED_TRAIN_STEPS:,}")
    print(f"  S4 determinism         : {len(det):,} distinct (arm, seed, reward_hash) keys; "
          f"{replicate_keys} key(s) have a REPLICATE to compare; {dup_keys} disagree")
    if replicate_keys == 0:
        print("      !! NO REPLICATES EXIST IN THIS ARCHIVE, so S4 tested NOTHING. A '0 disagree'")
        print("        result here is VACUOUS and is NOT evidence of determinism. Determinism must")
        print("        be evidenced from a run that re-trains an identical (arm, seed, reward) --")
        print("        e.g. the 30/30 bit-identical farm or a crash-rehearsal replay -- not from this.")
    print()

    all_fail = [f"{m}\n      {p}" for p, m in failures] + det_violations + s8 + s10
    if all_fail:
        print(f"!! {len(all_fail)} SCIENCE ISSUE(S)")
        for msg in all_fail[:60]:
            print(f"  - {msg}")
        if len(all_fail) > 60:
            print(f"  ... and {len(all_fail) - 60} more")
    else:
        # ⚠ THIS BANNER IS DELIBERATELY NARROWER THAN ITS FIRST VERSION (P197). It used to say
        # "every record is finite", which is FALSE: S1 covers the outcome series and the exposure
        # diagnostics, and `metrics.train_curve.return` is entirely NaN on 100% of records (see the
        # disclosure below). A summary line that overstates its own scope is the same defect class
        # as a check calibrated to the auditor's intuition.
        print("S1-S10 CLEAN, in the scope each check actually covers:")
        print("  - the OUTCOME series and exposure diagnostics are finite (S1)")
        print("  - every sealed-test series is the registered length (S2) and every training ran")
        print("    the registered budget (S3)")
        print("  - no degenerate/constant series, no impossible magnitude (S7), every allocation")
        print("    is a valid simplex (S6), one common window (S8)")
        print("  - inside every line's banked prefix, each paired arm holds each seed (S10)")
        print("  NOT asserted here: determinism (S4 -- see the note above) and the finiteness of")
        print("  diagnostic channels outside S1's scope.")

    print()
    print("=== S10 CRN PAIRING / BANKED RUNG (under R101 the COMMON rung IS the result) ===")
    _legs = {k: v for k, v in line_prefix.items() if k != "test_h3_singleshot"}
    # ⚠ P282, 2026-08-04. THE HEADLINE NUMBER USED TO BE A MINIMUM OVER THE ARMS THAT HAD STARTED.
    # `pair_seeds` only ever acquires a key when a record exists, so a line holding a REGISTERED
    # frozen-winner arm with ZERO sealed-test records contributed its OTHER arms' depth instead of
    # the 0 it actually banks. Measured live 2026-08-04: this GATED layer printed the core line at
    # prefix 30 while `record_seed_completeness` (S15/C6), the ungated measurement, printed 0 -- two
    # instruments disagreeing about THE REPORTED SCIENTIFIC RESULT, and the gated one reading high.
    # The `!!` note below already DISCLOSED the gap in prose, but a session that quotes the number
    # rather than reading the note overstates the bankable result, and that is exactly the P244
    # failure this repository has now found three times: a minimum taken over a population that
    # silently excludes the members that would make it bad news.
    # THE CORRECTION IS NARROW AND MATCHES S15 EXACTLY: a line with any registered arm holding no
    # record banks 0. Nothing else about this section changes, and the started-arms figure is still
    # printed beside it because it is the right number for the CRN-pairing question S10 asks.
    _started = dict(_legs)
    for _ln in list(_legs):
        _kk = 'core' if _ln == 'test' else _ln.replace('test_leg_', '')
        if roster.get(_kk, set()) - set(pair_seeds.get(_ln, {}).keys()):
            _legs[_ln] = 0
    if _legs:
        _common = min(_legs.values())
        _banked = max([r for r in REGISTERED_RUNGS if r <= _common], default=0)
        _common_started = min(_started.values())
        if _common != _common_started:
            print(f"  (over STARTED arms only this would read {_common_started}; the number below")
            print("   counts a registered arm with NO record as the 0 it actually banks -- P282)")
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
        _short = []
        for _ln in sorted(_legs):
            _k = _ln.replace('test_leg_', '')
            _k = 'core' if _ln == 'test' else _k
            _miss = sorted(roster.get(_k, set()) - set(pair_seeds.get(_ln, {}).keys()))
            if _miss:
                _short.append((_ln, _miss))
        if _short:
            print(f"  !! {len(_short)} of {len(_legs)} line(s) have an arm with a FROZEN WINNER but")
            print("     NO sealed-test record. Since P282 each of those lines is scored 0, which is")
            print("     what it actually banks; before P282 they contributed their STARTED arms'")
            print("     depth and this section read HIGH. The arms are named so the cause is visible:")
            for _ln, _miss in _short:
                print(f"       {_ln:34s} missing: {', '.join(_miss)}")
            print("     => the rung above IS a full-roster bank over frozen winners, and it agrees")
            print("        with record_seed_completeness (S15/C6). It is still an UPPER bound for")
            print("        the four reasons S15 lists (an arm still in C1, a line with no test dir,")
            print("        an unreadable frozen roster, and the 11 H1 baselines, which are excluded")
            print("        from pair_seeds by design and are checked separately by S15).")

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
    print(f"TRAIN-CURVE DISCLOSURE: metrics.train_curve.return is ENTIRELY NaN on {tc_nan:,} "
          f"record(s). SB3 logs ep_rew_mean and no episode closes inside the logging window, so the "
          f"channel is structurally empty. actor_loss/critic_loss/ent_coef/step ARE populated and no "
          f"figure reads `return` -- a disclosure, not a defect, but it is why the CLEAN banner no "
          f"longer claims 'every record is finite'.")
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
