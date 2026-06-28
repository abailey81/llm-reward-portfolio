"""Embargo at the EXECUTED search-split boundary (PREREGISTRATION §7; Rank 18).

The prototype orchestrators (``scripts/run_prototype.py::_load_panel_and_windows`` and
``src/orchestration/parallel.py::_panel_and_windows``) used to ABUT train/val (``val_start ==
train_end + 1``), with NO purge+embargo — violating the frozen pre-registration. They now resolve the
val start through ``src.data.loaders.embargoed_val_start(lookback=...)``, returning ``max(materialized
embargo boundary 2015-02-03, train_end + max(embargo, lookback))`` (R18). The materialized +21 boundary is
the embargo FLOOR; under the production lookback=60 the lookback purge DOMINATES, so the EXECUTED val start
is ~2015-03-31 (boundary + 39), NOT 2015-02-03 — the byte-match to the frozen +21 boundary holds only at
``lookback=0`` (the per-unit fallback tests). It (2) FALLS BACK to advancing ``max(embargo, lookback)``
trading sessions when the split table omits the boundary.

These tests are fast: the unit tests build a synthetic ascending date index + a temp splits parquet (no
gold load); one end-to-end test exercises the real ``_load_panel_and_windows`` and is skipped when the
licensed gold panel is absent.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.data.loaders import embargoed_val_start

_GOLD = Path(__file__).resolve().parents[1] / "data" / "gold" / "returns_panel_univ3.parquet"
_SPLITS = Path(__file__).resolve().parents[1] / "data" / "gold" / "splits_univ3.parquet"


def _business_dates(start: str, n: int) -> np.ndarray:
    """``n`` ascending business-day sessions as ``datetime64[ns]`` (a stand-in trading calendar)."""
    return pd.bdate_range(start=start, periods=n).to_numpy()


def _write_splits(path: Path, val_post_embargo_start: str, embargo: int = 21) -> None:
    payload = {
        "development": {"train": ["2005-01-03", "2014-12-31"],
                        "validation_post_embargo": [val_post_embargo_start, "2017-12-29"]},
        "embargo_trading_days": embargo,
    }
    pd.DataFrame({"splits_json": [json.dumps(payload)]}).to_parquet(path)


def test_materialized_boundary_is_honoured(tmp_path: Path) -> None:
    """When the split table carries the boundary, val_start lands EXACTLY on it (byte-match)."""
    dates = _business_dates("2014-12-01", 80)  # spans the 2014->2015 boundary
    _write_splits(tmp_path / "splits_univ3.parquet", "2015-02-03", embargo=21)
    idx = embargoed_val_start(dates, "2014-12-31", phase="development", gold_dir=tmp_path)
    assert pd.Timestamp(dates[idx]) == pd.Timestamp("2015-02-03")


def test_embargo_is_non_empty_vs_abutting_start(tmp_path: Path) -> None:
    """The embargoed val_start sits strictly AFTER the old abutting (train_end+1) start."""
    dates = _business_dates("2014-12-01", 80)
    _write_splits(tmp_path / "splits_univ3.parquet", "2015-02-03", embargo=21)
    train_idx = int(np.searchsorted(dates, np.datetime64(pd.Timestamp("2014-12-31"))))
    idx = embargoed_val_start(dates, "2014-12-31", phase="development", gold_dir=tmp_path)
    assert idx > train_idx + 1  # a real purge gap, not abutting


def test_fallback_purges_embargo_trading_days(tmp_path: Path) -> None:
    """No split table -> purge exactly ``embargo_days`` SESSIONS (not calendar days) after train_end."""
    dates = _business_dates("2015-01-01", 60)  # bdate skips weekends -> a stand-in trading calendar
    train_end = str(pd.Timestamp(dates[10]))  # an in-range session to measure the embargo from
    train_idx = int(np.searchsorted(dates, np.datetime64(pd.Timestamp(train_end))))
    abut = train_idx + 1  # first post-train session (the OLD abutting val start)
    # gold_dir points at an EMPTY dir => no splits parquet => fallback path.
    idx = embargoed_val_start(dates, train_end, phase="development", embargo_days=21, gold_dir=tmp_path)
    assert idx - abut == 21  # the dropped [abut, idx) sessions number exactly 21


def test_lookback_purge_covers_feature_window(tmp_path: Path) -> None:
    """R18 (leakage fix): with a feature ``lookback``, the purge is max(embargo, lookback), so the
    downstream window's first observation cannot read a return from the prior split. ``lookback=0``
    (the default) preserves the legacy embargo-only gap."""
    dates = _business_dates("2015-01-01", 200)
    train_end = str(pd.Timestamp(dates[40]))
    abut = int(np.searchsorted(dates, np.datetime64(pd.Timestamp(train_end)))) + 1
    g0 = embargoed_val_start(dates, train_end, embargo_days=21, lookback=0, gold_dir=tmp_path)
    g60 = embargoed_val_start(dates, train_end, embargo_days=21, lookback=60, gold_dir=tmp_path)
    assert g0 - abut == 21  # legacy embargo-only behaviour preserved
    assert g60 - abut >= 60  # the purge now covers the 60-day feature lookback
    assert g60 - 60 >= abut  # the first val feature window does NOT reach train


def test_fallback_default_embargo_is_21(tmp_path: Path) -> None:
    """The fallback default (no arg) purges 21 trading sessions, matching config/data.yaml::embargo_days."""
    dates = _business_dates("2015-01-01", 60)
    train_end = str(pd.Timestamp(dates[5]))
    abut = int(np.searchsorted(dates, np.datetime64(pd.Timestamp(train_end)))) + 1
    idx = embargoed_val_start(dates, train_end, phase="development", gold_dir=tmp_path)
    assert idx - abut == 21


def test_fallback_when_boundary_absent_but_embargo_present(tmp_path: Path) -> None:
    """A split table WITHOUT validation_post_embargo still yields a 21-session purge from its embargo field."""
    payload = {"development": {"train": ["2005-01-03", "2014-12-31"]}, "embargo_trading_days": 21}
    pd.DataFrame({"splits_json": [json.dumps(payload)]}).to_parquet(tmp_path / "splits_univ3.parquet")
    dates = _business_dates("2015-01-01", 60)
    train_end = str(pd.Timestamp(dates[5]))
    abut = int(np.searchsorted(dates, np.datetime64(pd.Timestamp(train_end)))) + 1
    idx = embargoed_val_start(dates, train_end, phase="development", gold_dir=tmp_path)
    assert idx - abut == 21


@pytest.mark.skipif(not _SPLITS.exists(), reason="frozen splits_univ3.parquet not present (licensed data)")
def test_frozen_splits_carry_dev_post_embargo_boundary() -> None:
    """Sanity: the materialized dev boundary is 2015-02-03 with a 21-trading-day embargo."""
    cell = pd.read_parquet(_SPLITS)["splits_json"].iloc[0]
    splits = json.loads(cell)
    assert splits["embargo_trading_days"] == 21
    assert splits["development"]["validation_post_embargo"][0] == "2015-02-03"


@pytest.mark.skipif(not _GOLD.exists(), reason="frozen gold panel not present (licensed data)")
def test_executed_prototype_val_start_respects_embargo() -> None:
    """END-TO-END: the EXECUTED prototype window purges the FEATURE LOOKBACK at the train/val boundary.

    Drives the real ``_load_panel_and_windows`` against the frozen gold panel and asserts the val
    window starts at least ``lookback`` (60) trading sessions after the last TRAIN session, so the
    val window's first observation's 60-day feature lookback does NOT reach the train window (R18
    leakage fix, 2026-06-20: the prior 21-session embargo left 39 contaminated observations).
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import run_prototype  # noqa: WPS433 - test-time import of the script module

    data_cfg = {"phase": "development", "train_end": "2014-12-31", "val_end": "2017-12-31",
                "embargo_days": 21, "on_missing": "liquidate_to_cash"}
    panel, (t_lo, t_hi), (v_lo, v_hi) = run_prototype._load_panel_and_windows(
        synthetic=False, data_cfg=data_cfg, lookback=60
    )
    dates = np.asarray(panel.dates)
    last_train_idx = int(np.searchsorted(dates, np.datetime64(pd.Timestamp("2014-12-31"))))
    abut = last_train_idx + 1  # the OLD no-embargo val start (first session after last train)
    lookback = 60
    assert v_lo > abut, "executed train/val windows must NOT abut (embargo required)"
    # R18 (2026-06-20 leakage fix): the PURGE must cover the FEATURE LOOKBACK (60), not merely the
    # embargo (21). Each observation reads returns[t-lookback:t]; with only a 21-session gap the val
    # window's first (lookback - embargo) = 39 observations read TRAIN returns (returns[v_lo-lookback:
    # v_lo] reaches back across the boundary) — a López de Prado purge-insufficiency. The effective
    # purge is now max(embargo, lookback) = 60, and CRUCIALLY the first val feature window clears train.
    assert v_lo - abut >= lookback, "the purge must cover the feature lookback (>= 60 sessions)"
    assert v_lo - lookback >= abut, "the val window's first lookback must NOT reach the train window"
    assert v_hi == panel.T and v_lo < v_hi  # non-empty validation window
