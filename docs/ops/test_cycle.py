"""Falsification tests for `cycle.py`'s one-token results verdict (`sci=`).

WHY THIS EXISTS (P230, 2026-08-03). `cycle.py` computed the headline science token as

    broken = [k for k in _HARD_ZERO if science.get(k)]
    sci    = "OK" if not broken else "!" + ",".join(broken)

`science.get(k)` returns None when a science tool TIMED OUT or when its output could not be parsed,
and None is FALSY. So a cycle whose science layer produced NOTHING AT ALL printed `sci=OK` -- the
token this repo's cadence contract names an invariant that "must never change", and the token
`session_preflight` gates on. It is the RUN 17 lesson in its purest form: an instrument that fails
silently IN THE DIRECTION OF REASSURANCE.

It was not hypothetical. Measured on the live `CYCLE_LOG.md`: 3 green-but-blind cycles in 4,774
(2026-08-03 10:26:51Z, 10:28:50Z, 16:25:51Z), every one under load -- i.e. exactly when the check is
most worth having. Two of the three PREDATE the reboot, so this is a standing defect, not a
reboot artefact.

THE DISCIPLINE THESE TESTS FOLLOW, earned the hard way across four sessions:
  * they call the PRODUCTION rule (`cycle._sci_token`) -- a test that re-implements its predicate
    tests nothing (RUN 17 lesson 4);
  * they are MUTATION CONTROLS, not smoke tests: case D pins the PRE-FIX rule and asserts the
    verdict FLIPS, so a regression that restores the old behaviour fails here;
  * they assert the check FAILS when it should, not merely that it passes on a healthy input --
    "found nothing wrong" and "looked at nothing" must not be indistinguishable (P213).

    python docs/ops/test_cycle.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cycle  # noqa: E402

PASS: list[str] = []
FAIL: list[str] = []

HARD = cycle._HARD_ZERO
N = len(HARD)


def check(name: str, got, want) -> None:
    (PASS if got == want else FAIL).append(f"{name}: got={got!r} want={want!r}")


def all_zero() -> dict:
    """The healthy archive: every hard invariant READ, every one reading zero, records WITNESSED."""
    d = {k: 0 for k in HARD}
    d.update({k: 9540 for k in cycle._WITNESS_COUNTS})
    return d


def all_blind() -> dict:
    """Both science tools timed out -- the exact 16:25:51Z state, every field None."""
    d = {k: None for k in HARD}
    d.update({k: None for k in cycle._WITNESS_COUNTS})
    return d


# --- A. the healthy path still reads OK (the fix must not cry wolf) ------------------------------
check("A1 all-zero reads OK", cycle._sci_token(all_zero()), "OK")

# --- B. total blindness is NOT OK ---------------------------------------------------------------
# This is the live 2026-08-03 16:25:51Z cycle: science_watch rc=99, every _SCIENCE_FIELDS entry
# unparsed. The pre-fix code printed "OK" here.
check("B1 all-None is not OK", cycle._sci_token(all_blind()) != "OK", True)
check("B1b all-None names the count", cycle._sci_token(all_blind()), f"BLIND({N}/{N}+norec)")

# --- C. PARTIAL blindness is also not OK --------------------------------------------------------
# One tool succeeding does not license OK for the fields the other tool owns. This is the case a
# naive "if not any fields parsed" guard would have missed.
one_blind = all_zero()
one_blind["sw_impossible"] = None
check("C1 one-None is not OK", cycle._sci_token(one_blind) != "OK", True)
check("C1b one-None counts exactly one", cycle._sci_token(one_blind), f"BLIND(1/{N})")

# --- D. THE MUTATION CONTROL: the pre-fix rule and the production rule must DISAGREE -------------
# `pre_fix` is the code as it stood before P230, reproduced here ONLY to prove the verdict flips.
# If a future edit restores the old behaviour, this case fails.
def pre_fix(science: dict) -> str:
    broken = [k for k in HARD if science.get(k)]
    return "OK" if not broken else "!" + ",".join(broken)


check("D1 pre-fix WOULD have said OK on a blind layer", pre_fix(all_blind()), "OK")
check("D2 production DISAGREES with pre-fix on a blind layer",
      cycle._sci_token(all_blind()) != pre_fix(all_blind()), True)
check("D3 pre-fix and production AGREE on a healthy layer",
      cycle._sci_token(all_zero()), pre_fix(all_zero()))

# --- E. a real breach still dominates, and is still named --------------------------------------
# A broken invariant must never be masked by BLIND: it is the more serious fact and it names itself.
broken_one = all_zero()
broken_one["ra_scalar_leaks"] = 3
check("E1 breach names the key", cycle._sci_token(broken_one), "!ra_scalar_leaks")

broken_and_blind = all_blind()
broken_and_blind["ra_scalar_leaks"] = 3
check("E2 breach outranks blindness", cycle._sci_token(broken_and_blind), "!ra_scalar_leaks")

# --- F. the token preflight gates on -----------------------------------------------------------
# session_preflight.check_cycle_log tests `sci == "OK"` by EQUALITY, so any non-OK token degrades
# that row to FAIL. Pin that BLIND is not accidentally equal to OK.
check("F1 BLIND is not the string OK", cycle._sci_token(all_blind()) == "OK", False)

# --- G. empty input must not read OK (P213: looked-at-nothing != found-nothing-wrong) ------------
# A `science` dict with no keys at all means every hard invariant is unread.
check("G1 empty science dict is not OK", cycle._sci_token({}) != "OK", True)
check("G1b empty science dict is fully blind", cycle._sci_token({}), f"BLIND({N}/{N}+norec)")

# --- H. THE AUDITOR'S F-1 CASE: every invariant reads 0 because NOTHING WAS WALKED ----------------
# Point either archive tool at an empty/renamed root and it exits 0, prints "0 records", and every
# _HARD_ZERO counter parses as 0 -- so the FIRST version of this fix still returned "OK". "Found
# nothing wrong" and "looked at nothing" must not be indistinguishable in a green board (P213).
empty_archive = all_zero()
for _k in cycle._WITNESS_COUNTS:
    empty_archive[_k] = 0
check("H1 zero records examined is NOT OK", cycle._sci_token(empty_archive) != "OK", True)
check("H1b zero records is flagged norec", cycle._sci_token(empty_archive), f"BLIND(0/{N}+norec)")

# One walker succeeding does not license OK for the other's fields.
half_witness = all_zero()
half_witness["ra_records"] = None
check("H2 one missing record count is NOT OK", cycle._sci_token(half_witness) != "OK", True)

# MUTATION CONTROL for H: the fix as first written (HARD_ZERO only, no witness) said OK here.
def pre_f1(science: dict) -> str:
    broken = [k for k in HARD if science.get(k)]
    if broken:
        return "!" + ",".join(broken)
    blind = [k for k in HARD if science.get(k) is None]
    return f"BLIND({len(blind)}/{N})" if blind else "OK"


check("H3 the FIRST fix WOULD have said OK on an empty archive", pre_f1(empty_archive), "OK")
check("H3b production DISAGREES with the first fix on an empty archive",
      cycle._sci_token(empty_archive) != pre_f1(empty_archive), True)

# A real breach still outranks a missing witness -- a breach is the more serious fact.
breach_no_witness = empty_archive.copy()
breach_no_witness["ra_hash_mismatch"] = 2
check("H4 breach outranks a missing witness", cycle._sci_token(breach_no_witness),
      "!ra_hash_mismatch")


print(f"_HARD_ZERO carries {N} invariants")
for line in PASS:
    print("  pass  " + line)
for line in FAIL:
    print("  FAIL  " + line)
print(f"cycle sci-token selftest: {len(PASS)}/{len(PASS) + len(FAIL)} passed")
raise SystemExit(1 if FAIL else 0)
