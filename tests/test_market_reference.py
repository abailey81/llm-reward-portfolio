"""Tests for the reference-data loaders (risk-free, market proxy, Fama-French factors; block B11/B13).

Behaviour: correct unit conversion, alignment to a date axis, no-future-leak forward fill, and graceful
degradation to an empty/zero series with ``available=False`` on a synthetic-only install (files absent).
The against-real-gold checks skip when the licensed files are not present.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.data.market_reference import (
    TRADING_DAYS_PER_YEAR,
    load_ff_factors,
    load_market_proxy_returns,
    load_risk_free_daily,
)

from src.data.loaders import gold_suffix

_FRED = Path("data/raw/fred_macro.csv")
_MKT = Path(f"data/gold/market_proxy_{gold_suffix()}.parquet")  # ACTIVE suffix (Split C: univ5)
_FF = Path("data/raw/french_F-F_Research_Data_Factors_daily.csv")


# --------------------------------------------------------------------------- #
# graceful degradation (synthetic-only install: files absent)                 #
# --------------------------------------------------------------------------- #
def test_risk_free_absent_is_zero_and_flagged(tmp_path: Path) -> None:
    dates = pd.bdate_range("2020-01-01", periods=50).to_numpy()
    rf = load_risk_free_daily(dates, raw_dir=tmp_path)
    assert rf.available is False
    assert rf.daily.shape == (50,) and np.all(rf.daily == 0.0)


def test_market_proxy_absent_is_zero_and_flagged(tmp_path: Path) -> None:
    dates = pd.bdate_range("2020-01-01", periods=40).to_numpy()
    mp = load_market_proxy_returns(dates, gold_dir=tmp_path)
    assert mp.available is False
    assert mp.returns.shape == (40,) and np.all(mp.returns == 0.0)


def test_ff_absent_is_empty_and_flagged(tmp_path: Path) -> None:
    dates = pd.bdate_range("2020-01-01", periods=40).to_numpy()
    ff = load_ff_factors(dates, raw_dir=tmp_path)
    assert ff.available is False and ff.factors == {}


# --------------------------------------------------------------------------- #
# unit conversion + alignment + no-future-leak (synthetic fixtures)           #
# --------------------------------------------------------------------------- #
def test_risk_free_converts_annual_pct_to_daily_decimal(tmp_path: Path) -> None:
    # a constant 2.52% annualised yield -> per-session (1+0.0252)**(1/252)-1
    dates = pd.bdate_range("2021-01-04", periods=10)
    df = pd.DataFrame({"observation_date": dates.strftime("%Y-%m-%d"), "DGS3MO": [2.52] * 10})
    df.to_csv(tmp_path / "fred_macro.csv", index=False)
    rf = load_risk_free_daily(dates.to_numpy(), raw_dir=tmp_path)
    assert rf.available is True
    expected = (1.0 + 2.52 / 100.0) ** (1.0 / TRADING_DAYS_PER_YEAR) - 1.0
    assert rf.daily == pytest.approx(expected, rel=1e-9)
    assert rf.annual_pct_mean == pytest.approx(2.52, rel=1e-9)


def test_risk_free_forward_fills_gaps_never_future(tmp_path: Path) -> None:
    # publish a yield only on day 0 and day 5; days 1-4 must read day-0 (the LAST KNOWN), not day-5.
    dates = pd.bdate_range("2021-01-04", periods=6)
    yields = [1.00, np.nan, np.nan, np.nan, np.nan, 5.00]
    pd.DataFrame({"observation_date": dates.strftime("%Y-%m-%d"), "DGS3MO": yields}).to_csv(
        tmp_path / "fred_macro.csv", index=False
    )
    rf = load_risk_free_daily(dates.to_numpy(), raw_dir=tmp_path)
    d1 = (1.0 + 1.00 / 100.0) ** (1.0 / TRADING_DAYS_PER_YEAR) - 1.0
    assert rf.daily[1] == pytest.approx(d1, rel=1e-9)  # forward-filled from day 0, NOT day 5
    assert rf.daily[3] == pytest.approx(d1, rel=1e-9)


def test_raw_path_prefers_refreshed_artifact(tmp_path: Path) -> None:
    """ADR-051: readers prefer the versioned extension refresh (x26) when present, else canonical."""
    from src.data.market_reference import _FF_CSV, _FRED_CSV, _raw_path

    # neither present -> canonical path returned (caller handles absence)
    assert _raw_path(tmp_path, _FRED_CSV).name == _FRED_CSV
    # refresh present -> preferred
    (tmp_path / "fred_macro_x26.csv").write_text("observation_date,DGS3MO\n2026-06-30,4.0\n")
    assert _raw_path(tmp_path, _FRED_CSV).name == "fred_macro_x26.csv"
    (tmp_path / "french_ff3_daily_x26.csv").write_text("Date,Mkt-RF,SMB,HML,RF\n2026-05-29,0.001,0.0,0.0,0.0\n")
    assert _raw_path(tmp_path, _FF_CSV).name == "french_ff3_daily_x26.csv"


def test_ff_factors_load_from_refreshed_file(tmp_path: Path) -> None:
    """The x26 ff3 layout (Date-indexed, decimal factors) loads through load_ff_factors unchanged."""
    idx = pd.bdate_range("2026-05-26", periods=4)
    rows = "\n".join(f"{d.date()},0.001,0.0002,-0.0003,0.0001" for d in idx)
    (tmp_path / "french_ff3_daily_x26.csv").write_text("Date,Mkt-RF,SMB,HML,RF\n" + rows + "\n")
    res = load_ff_factors(idx.to_numpy(), raw_dir=tmp_path)
    assert res.available is True
    assert res.factors["Mkt-RF"] == pytest.approx([0.001] * 4)


def test_market_proxy_aligns_and_zero_fills_outside(tmp_path: Path) -> None:
    idx = pd.bdate_range("2021-01-04", periods=5)
    pd.DataFrame({"market_ew": [0.01, -0.02, 0.0, 0.005, -0.001]}, index=idx).to_parquet(
        tmp_path / f"market_proxy_{gold_suffix()}.parquet"
    )
    mp = load_market_proxy_returns(idx.to_numpy(), gold_dir=tmp_path)
    assert mp.available is True
    assert mp.returns == pytest.approx([0.01, -0.02, 0.0, 0.005, -0.001])


# --------------------------------------------------------------------------- #
# against the real frozen reference data (skip if licensed files absent)      #
# --------------------------------------------------------------------------- #
@pytest.mark.skipif(not _FRED.exists(), reason="frozen FRED macro not present")
def test_real_risk_free_is_plausible() -> None:
    dates = pd.bdate_range("2005-01-03", "2017-12-29").to_numpy()
    rf = load_risk_free_daily(dates)
    assert rf.available and np.isfinite(rf.daily).all()
    assert 0.0 <= rf.daily.mean() * TRADING_DAYS_PER_YEAR < 0.10  # ~1-2%/yr over 2005-2017 (incl. ZIRP)


@pytest.mark.skipif(not _MKT.exists(), reason="frozen market proxy not present")
def test_real_market_proxy_is_a_real_series() -> None:
    dates = pd.bdate_range("2005-01-03", "2017-12-29").to_numpy()
    mp = load_market_proxy_returns(dates)
    assert mp.available and np.isfinite(mp.returns).all()
    assert mp.returns.std() > 0.0  # a genuine market line, not a constant 1/N stand-in


@pytest.mark.skipif(not _FF.exists(), reason="frozen Fama-French factors not present")
def test_real_ff_factors_present() -> None:
    dates = pd.bdate_range("2005-01-03", "2017-12-29").to_numpy()
    ff = load_ff_factors(dates)
    assert ff.available and "Mkt-RF" in ff.factors
    assert np.isfinite(ff.factors["Mkt-RF"]).all()
