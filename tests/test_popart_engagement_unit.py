"""PopArt engagement must be judged at the CELL, never at the record.

WHY THIS TEST EXISTS -- a false alarm on the registered protection for the HEADLINE hypothesis,
raised and resolved 2026-08-06 (RUN 28).

`docs/ops/acknowledged_alarms.txt` records that the only surviving protection for H2 against a
reward-scale confound is that PopArt engagement is ARM-SYMMETRIC across the five LLM arms, measured
2026-07-30 (s.44.4, n=1,024) at 65.5 / 65.2 / 67.1 / 67.4 / 62.1 % -- a 5.3 pp spread.
`retriage_alarms.py` then reported 44.3 / 76.7 / 29.7 / 34.9 / 48.0 %, a 46.9 pp spread, and printed
"*** ASYMMETRIC -- RE-TRIAGE ***".

It was an estimator artefact, established three independent ways:

  A. MECHANISM. `sigma_max = max(popart_min_scale, rms(value targets))`, and the value-target scale
     is set by the REWARD PROGRAM's magnitude. Each (line, arm) cell holds ONE frozen winning
     program retrained across up to 568 seeds. Measured: 50 of 54 cells are PERFECTLY degenerate --
     every seed agrees -- with a median cell size of 334 seeds.
  B. CORRECT UNIT. One value per cell gives 52.7 / 71.5 / 36.4 / 49.9 / 64.7 %, a 35.1 pp spread
     over ~11 cells per arm against an SE-of-difference of 21.2 pp (ratio 1.66), with all five 95%
     CIs overlapping. Not established.
  C. LIKE-FOR-LIKE. On the SEARCH-stage population the 07-30 baseline actually measured (175
     distinct candidate programs), the arms remain symmetric at 7.0 pp against the recorded 5.3 pp.

⇒ The record-level estimator inflates n by roughly the seed count, so a handful of cells flipping
reads as an overwhelming arm effect. That is the FOURTH instance of this project's recurring error
class (R25-2, R25-3, R26-13): *a comparison is evidence only if both sides are the same population
at the same point of their lifecycle.*

⚠ THIS IS NOT AN ALL-CLEAR, AND THE TEST ENCODES THAT. 35.1 pp at 1.66 SE is "not established", not
"zero"; with ~11 cells per arm the comparison is badly underpowered. The alarm must keep firing when
the CELL-level spread is genuinely large, which the second test pins.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
#: Overridable ONLY so these assertions can be mutation-tested against a COPY.
RT_PATH = Path(os.environ.get("RT_PATH") or (REPO / "docs" / "ops" / "retriage_alarms.py"))


@pytest.fixture(scope="module")
def fn():
    """Load `engagement_by_arm` without executing the module's scanning main body."""
    src = RT_PATH.read_text(encoding="utf-8")
    marker = "# ---- END OF PURE HELPERS"
    assert marker in src, (
        "retriage_alarms.py must isolate its pure helpers above %r so a test can import them "
        "without scanning the whole archive" % marker
    )
    ns: dict = {}
    exec(compile(src.split(marker)[0], str(RT_PATH), "exec"), ns)   # noqa: S102 - our own file
    assert "engagement_by_arm" in ns, "engagement_by_arm is not defined among the pure helpers"
    return ns["engagement_by_arm"]


def _cell(line, arm, n, engaged_fraction):
    """n records for one (line, arm) cell, `engaged_fraction` of them engaged."""
    k = round(n * engaged_fraction)
    return [{"line": line, "arm": arm, "sigma_max": (2.0 if i < k else 1.0)} for i in range(n)]


def test_a_degenerate_cell_counts_once_not_once_per_seed(fn):
    """THE DEFECT. Two arms, each one cell, each cell 568 identical seeds. At the record level this
    looks like n=568 per arm and a 100 pp spread; at the cell level it is n=1 per arm, which is what
    it actually is."""
    recs = _cell("lineA", "scalar", 568, 1.0) + _cell("lineA", "placebo", 568, 0.0)
    res = fn(recs, arms=["scalar", "placebo"])
    assert res["scalar"]["cells"] == 1, (
        "568 seeds of ONE frozen program were counted as %d independent units"
        % res["scalar"]["cells"]
    )
    assert res["placebo"]["cells"] == 1
    assert res["scalar"]["rate"] == pytest.approx(100.0)
    assert res["placebo"]["rate"] == pytest.approx(0.0)


def test_the_record_level_denominator_is_reported_but_not_inferential(fn):
    """The raw record counts stay visible -- hiding them would be its own defect -- but they must be
    labelled as descriptive, so nobody re-derives the false alarm from them."""
    recs = _cell("lineA", "scalar", 568, 1.0) + _cell("lineB", "scalar", 30, 0.0)
    res = fn(recs, arms=["scalar"])
    assert res["scalar"]["records"] == 598, "the record count must still be reported"
    assert res["scalar"]["cells"] == 2
    # cell-level: one cell at 1.0 and one at 0.0 -> 50%. Record-level would be 568/598 = 95.0%.
    assert res["scalar"]["rate"] == pytest.approx(50.0), (
        "the inferential rate must weight CELLS equally, not seeds: a 568-seed cell and a 30-seed "
        "cell are one frozen program each"
    )


def test_a_genuinely_large_cell_level_spread_still_alarms(fn):
    """The guard against over-correcting. Silencing a real asymmetry would be worse than the false
    alarm this replaces, so the alarm must survive when the CELLS disagree."""
    recs = []
    for i in range(8):
        recs += _cell("line%d" % i, "scalar", 30, 1.0)          # every scalar cell engaged
        recs += _cell("line%d" % i, "placebo", 30, 0.0)         # every placebo cell pinned
    res = fn(recs, arms=["scalar", "placebo"])
    assert res["scalar"]["cells"] == 8 and res["placebo"]["cells"] == 8
    spread = abs(res["scalar"]["rate"] - res["placebo"]["rate"])
    assert spread == pytest.approx(100.0), "a real, well-sampled asymmetry must still read 100 pp"


def test_a_mixed_cell_contributes_its_fraction_not_a_hard_vote(fn):
    """4 of 54 live cells are genuinely mixed (e.g. haiku/placebo at 278 of 566). Collapsing those
    to a hard 0/1 vote would discard real information and could flip a marginal verdict."""
    recs = _cell("lineA", "scalar", 100, 0.5)
    res = fn(recs, arms=["scalar"])
    assert res["scalar"]["cells"] == 1
    assert res["scalar"]["rate"] == pytest.approx(50.0)


def test_no_records_yields_no_rate_rather_than_a_zero(fn):
    """ZERO IS NOT CLEAN (the P213 rule). An arm with no records must be absent, never 0.0%, or an
    unscanned archive reads as a perfectly pinned arm."""
    res = fn([], arms=["scalar"])
    assert "scalar" not in res or res["scalar"]["cells"] == 0


def test_records_missing_sigma_max_are_excluded_not_counted_as_pinned(fn):
    """A missing field is unknown, not evidence of non-engagement."""
    recs = _cell("lineA", "scalar", 10, 1.0)
    recs += [{"line": "lineA", "arm": "scalar", "sigma_max": None} for _ in range(90)]
    res = fn(recs, arms=["scalar"])
    assert res["scalar"]["records"] == 10, "null sigma_max must not enter the denominator"
    assert res["scalar"]["rate"] == pytest.approx(100.0)
