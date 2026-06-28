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

_FRED = Path("data/raw/fred_macro.csv")
_MKT = Path("data/gold/market_proxy_univ3.parquet")
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


def test_market_proxy_aligns_and_zero_fills_outside(tmp_path: Path) -> None:
    idx = pd.bdate_range("2021-01-04", periods=5)
    pd.DataFrame({"market_ew": [0.01, -0.02, 0.0, 0.005, -0.001]}, index=idx).to_parquet(
        tmp_path / "market_proxy_univ3.parquet"
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
