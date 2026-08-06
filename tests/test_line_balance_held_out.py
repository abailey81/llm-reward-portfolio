"""A line held to a standstill must not read as healthy.

WHY THIS TEST EXISTS -- a measured, live blind spot, 2026-08-06 (RUN 28).

`line_balance.HELD_STATES` are counted INTO `queued` so the STUCK alarm cannot fire on a line whose
jobs are merely held. That was a correct fix, and it rests on a premise stated in its own comment:
*"a hold is reversible by construction and the jobs run the moment it is released."*

The premise is only true if something will actually release them. Measured at 19:55Z,
`leg1_leg_deepseek_v4_pro` -- a BINDING line gating the next common rung -- held 165 jobs with ZERO
running and ZERO eligible, and nothing was scheduled to release them: `ladder_lock_plan` releases
only ids in its own journal, and `promote_duration_jobs.sh` had no release path at all. The line
could neither complete the block that would advance it nor submit the next batch. `line_balance`
classified it WAITING and the published page said CLEAN.

The tests drive `classify_below`, which `report()` itself calls -- never a re-implementation of the
predicate. That discipline is the file's own hard-won lesson: an earlier selftest there asserted
`(now - (now - x)) >= BOUND`, a tautology that executed no production code.

Row shape, from `report()`: (min_records, max_records, test_dir, tag, running, queued_incl_held,
empty_arms, n_arms).
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
#: Overridable ONLY so these assertions can be mutation-tested against a COPY. line_balance.py is
#: run by the monitoring cycle; mutating it in place to prove a test can fail is not acceptable.
LB_PATH = Path(os.environ.get("LB_PATH") or (REPO / "docs" / "ops" / "line_balance.py"))


@pytest.fixture(scope="module")
def lb():
    spec = importlib.util.spec_from_file_location("_line_balance", LB_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _row(tag, running, queued_incl_held, min_rec=30):
    return (min_rec, min_rec, "test_leg_" + tag, tag, running, queued_incl_held, 0, 5)


def test_a_line_whose_only_work_is_held_is_flagged_held_out(lb):
    """The deepseek case, reproduced exactly: 0 running, 165 held, so 0 eligible."""
    rows = [_row("leg1", running=0, queued_incl_held=165)]
    unknown, idle, waiting, held_out = lb.classify_below(rows, {"leg1": 165})

    # it is still WAITING -- held_out is a SUBSET, not a replacement, so nothing that reads
    # `waiting` changes behaviour
    assert [r[3] for r in waiting] == ["leg1"]
    assert not idle and not unknown
    # ...and it is now ALSO surfaced as held-out, which is the whole point
    assert [r[3] for r in held_out] == ["leg1"], (
        "a line with 0 running and 0 ELIGIBLE was not flagged. This is the exact state deepseek "
        "sat in while gating the next common rung, and every instrument reported CLEAN."
    )


def test_the_pre_fix_predicate_could_not_see_it(lb):
    """Demonstrate the defect rather than assert it: the old rule put deepseek in `waiting` and had
    no vocabulary to say anything further."""
    rows = [_row("leg1", running=0, queued_incl_held=165)]
    pre_fix_waiting = [r for r in rows if r[4] > 0 or r[5] > 0]          # the rule as it stood
    assert [r[3] for r in pre_fix_waiting] == ["leg1"]
    _, _, _, held_out = lb.classify_below(rows, {"leg1": 165})
    assert held_out, "the new classification must distinguish what the old one could not"


def test_a_healthy_held_line_with_eligible_work_is_NOT_flagged(lb):
    """The false-positive guard. `glm` had 157 jobs held during an authorised reorder while still
    holding eligible work; flagging that would recreate the false STUCK this file already fixed."""
    rows = [_row("leg2", running=0, queued_incl_held=160)]
    _, _, waiting, held_out = lb.classify_below(rows, {"leg2": 157})     # 3 still eligible
    assert [r[3] for r in waiting] == ["leg2"]
    assert held_out == [], "a line retaining eligible work must not be flagged held-out"


def test_a_running_line_is_never_held_out(lb):
    """Running work means the line is producing, whatever is held behind it."""
    rows = [_row("leg7", running=3, queued_incl_held=245)]
    _, _, _, held_out = lb.classify_below(rows, {"leg7": 245})
    assert held_out == []


def test_a_line_with_no_jobs_at_all_is_idle_not_held_out(lb):
    """0 running and 0 queued is the STUCK candidate path and must stay there -- held_out must not
    quietly absorb it, because STUCK carries a dwell timer and an alarm that this does not."""
    rows = [_row("leg9", running=0, queued_incl_held=0)]
    unknown, idle, waiting, held_out = lb.classify_below(rows, {})
    assert [r[3] for r in idle] == ["leg9"]
    assert waiting == [] and held_out == [] and unknown == []


def test_unknown_transport_is_preserved_and_never_flagged(lb):
    """-1 means the ssh failed or the tag did not resolve. UNKNOWN PRESERVES: it must not be read as
    a held-out line, or one failed qstat would invent an alarm."""
    rows = [_row("leg4", running=-1, queued_incl_held=-1)]
    unknown, idle, waiting, held_out = lb.classify_below(rows, {"leg4": 10})
    assert [r[3] for r in unknown] == ["leg4"]
    assert held_out == [] and idle == [] and waiting == []


def test_inconsistent_held_count_cannot_manufacture_a_flag(lb):
    """Pin an equivalence rather than leave it to luck.

    Mutating `for r in waiting` to `for r in below` SURVIVED the rest of this file, and the honest
    reading is that it is an EQUIVALENT MUTANT rather than a gap: `parse_qstat_tally` counts held
    jobs INTO `queued`, so an idle row (0 running, 0 queued) can never carry a non-zero held count,
    and unknown rows are excluded by `r[4] == 0`. That equivalence is only true while the caller
    passes consistent data, so it is asserted here instead of assumed -- a caller that passes a held
    count for a line with no queued jobs at all must still not produce an alarm.
    """
    rows = [_row("leg9", running=0, queued_incl_held=0)]
    unknown, idle, waiting, held_out = lb.classify_below(rows, {"leg9": 7})   # deliberately absurd
    assert [r[3] for r in idle] == ["leg9"], "an all-zero line stays a STUCK candidate"
    assert held_out == [], (
        "a line with no queued jobs at all was flagged held-out on the strength of a stale or "
        "inconsistent held count -- that would invent an alarm out of a bookkeeping error"
    )


def test_report_calls_the_extracted_predicate(lb):
    """Guard against the classification silently drifting back inline, which would leave these tests
    passing against dead code -- the exact failure the file's own dwell-selftest note describes."""
    src = LB_PATH.read_text(encoding="utf-8")
    assert "classify_below(below, LAST_HELD)" in src, (
        "report() no longer calls classify_below, so these tests would no longer drive production"
    )
