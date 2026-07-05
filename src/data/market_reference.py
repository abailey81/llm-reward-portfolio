"""Portfolio-level REFERENCE series for the evaluation / reporting layer (block B11/B13).

These series live ENTIRELY in inference/reporting — they never enter the frozen, anonymised env
observation or a reward (so H2's contribution surface is untouched; data-enrichment research
2026-06-20). All three are already pulled + frozen on disk by ``data_pipeline``:

* **risk-free rate** — FRED ``DGS3MO`` (3-month T-bill secondary-market yield) from
  ``data/raw/fred_macro.csv``, converted to a per-session decimal. Replaces the ``rf = 0`` hardwire
  in the headline Sharpe/Sortino/Deflated-Sharpe (the "rf cancels in pairwise comparison" defence is
  false for differing-volatility benchmark comparisons). The per-session rate is the GEOMETRIC
  ``(1 + DGS3MO/100)**(1/252) - 1`` (annualised yield in percent -> daily decimal); DGS3MO is preferred
  over the Fama-French daily RF, which is piecewise-constant within each month (Dimitrov & Govindaraj,
  JOIM 2021). Any change to the rf CONVENTION in the headline is pre-registration-relevant (R20).
* **market proxy** — ``market_ew`` (equal-weight return of the FULL survivorship-free PIT universe)
  from ``data/gold/market_proxy_<suffix>.parquet``. A REAL broad-market line for alpha / beta /
  information-ratio reporting — distinct from the 30-asset 1/N strategy (the anonymised panel has no
  index column, so this EW-universe series is the defensible market stand-in; a cap-weighted SPX-TR
  remains a documented limitation).
* **Fama-French factors** — ``Mkt-RF, SMB, HML`` from ``data/raw/french_F-F_Research_Data_Factors_daily.csv``
  (the Momentum file ``french_F-F_Momentum_Factor_daily.csv`` is on disk but NOT loaded here; add it to
  ``load_ff_factors`` if a 4-factor attribution is wanted), for OUT-OF-SAMPLE attribution in the analysis chapter.

Every loader ALIGNS to the panel's own session axis (so a value is knowable at each trading date),
forward-fills the rare publication gaps (never reading the future), and degrades gracefully to a
zero/empty series with ``available=False`` when a file is absent (a synthetic-only install), so no
caller crashes. Any change to the RF/benchmark CONVENTION is pre-registration-relevant (ADR-038, R20).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

__all__ = [
    "RiskFreeResult",
    "MarketProxyResult",
    "FactorResult",
    "load_risk_free_daily",
    "load_market_proxy_returns",
    "load_ff_factors",
    "TRADING_DAYS_PER_YEAR",
]

TRADING_DAYS_PER_YEAR = 252
_RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
_GOLD_DIR = Path(__file__).resolve().parents[2] / "data" / "gold"
_FRED_CSV = "fred_macro.csv"
_FF_CSV = "french_F-F_Research_Data_Factors_daily.csv"

#: ADR-051 (Split C to 2026-06-30): the ORIGINAL raw reference files end before the cutoff
#: (fred_macro 2025-12-31; the French dailies 2026-04-30), so extension refreshes land as
#: VERSIONED write-once artifacts. Readers prefer the newest refresh WHEN PRESENT and fall back
#: to the canonical name — same layout/units (verified 2026-07-02: fred keeps observation_date +
#: percent yields; the ff3 refresh keeps Date + Mkt-RF/SMB/HML/RF decimals). Newest-first tuples.
_REFRESHED_RAW: dict[str, tuple[str, ...]] = {
    _FRED_CSV: ("fred_macro_x26.csv",),
    _FF_CSV: ("french_ff3_daily_x26.csv",),
}


def _raw_path(raw_dir: Path | str, canonical: str) -> Path:
    """The freshest available raw artifact for ``canonical`` (refresh preferred, else canonical)."""
    for cand in _REFRESHED_RAW.get(canonical, ()):
        p = Path(raw_dir) / cand
        if p.exists():
            return p
    return Path(raw_dir) / canonical


class RiskFreeResult:
    """Per-session risk-free decimal returns aligned to a date axis, + provenance."""

    def __init__(self, daily: np.ndarray, *, available: bool, source: str, annual_pct_mean: float) -> None:
        self.daily = daily
        self.available = available
        self.source = source
        self.annual_pct_mean = annual_pct_mean


class MarketProxyResult:
    """Per-session market-proxy decimal returns aligned to a date axis, + provenance."""

    def __init__(self, returns: np.ndarray, *, available: bool, column: str) -> None:
        self.returns = returns
        self.available = available
        self.column = column


class FactorResult:
    """Per-session Fama-French factor decimals (columns Mkt-RF/SMB/HML), + provenance."""

    def __init__(self, factors: dict[str, np.ndarray], *, available: bool) -> None:
        self.factors = factors
        self.available = available


def _aligned_series(frame: pd.DataFrame, col: str, dates: np.ndarray) -> tuple[np.ndarray, bool]:
    """Reindex ``frame[col]`` onto ``dates`` (forward-filled, no future read). Returns (values, ok)."""
    d = pd.DatetimeIndex(pd.to_datetime(np.asarray(dates)))
    s = pd.to_numeric(frame[col], errors="coerce")
    s.index = pd.DatetimeIndex(pd.to_datetime(frame.index if frame.index.name else frame.iloc[:, 0]))
    # Restrict to <= each target date then forward-fill so a gap reads the LAST KNOWN value, never a
    # future publication; leading gaps (before the first observation) fall back to 0.0.
    s = s[~s.index.duplicated(keep="last")].sort_index()
    aligned = s.reindex(s.index.union(d)).ffill().reindex(d)
    return aligned.to_numpy(dtype=float), True


def load_risk_free_daily(
    dates: np.ndarray, *, source: str = "DGS3MO", raw_dir: Path | str = _RAW_DIR
) -> RiskFreeResult:
    """Per-session risk-free DECIMAL return aligned to ``dates`` (FRED ``DGS3MO``/252, default).

    DGS3MO is an ANNUALISED yield in PERCENT; the per-session decimal is ``(1 + y/100)**(1/252) - 1``.
    Falls back to an all-zero series with ``available=False`` if the FRED file is absent.
    """
    path = _raw_path(raw_dir, _FRED_CSV)
    n = int(np.asarray(dates).size)
    if not path.exists():
        return RiskFreeResult(np.zeros(n), available=False, source=source, annual_pct_mean=0.0)
    fm = pd.read_csv(path)
    date_col = "observation_date" if "observation_date" in fm.columns else fm.columns[0]
    fm = fm.set_index(date_col)
    if source not in fm.columns:
        return RiskFreeResult(np.zeros(n), available=False, source=source, annual_pct_mean=0.0)
    annual_pct, _ok = _aligned_series(fm, source, dates)
    annual_pct = np.nan_to_num(annual_pct, nan=0.0)  # leading gap -> 0
    daily = np.power(1.0 + annual_pct / 100.0, 1.0 / TRADING_DAYS_PER_YEAR) - 1.0
    return RiskFreeResult(
        daily.astype(float), available=True, source=source, annual_pct_mean=float(np.nanmean(annual_pct))
    )


def load_market_proxy_returns(
    dates: np.ndarray, *, suffix: str | None = None, gold_dir: Path | str = _GOLD_DIR
) -> MarketProxyResult:
    """Per-session market-proxy DECIMAL return (``market_ew``) aligned to ``dates``.

    Reads ``data/gold/market_proxy_<suffix>.parquet`` (a one-column daily-return series). ``suffix=None``
    (default) resolves to ``gold_suffix()`` so the market line tracks the SAME universe as the traded
    panel under ``LLM_RP_GOLD_SUFFIX`` (critical-review 2026-06-20). Falls back to an all-zero series with
    ``available=False`` if the file is absent.
    """
    if suffix is None:
        from src.data.loaders import gold_suffix

        suffix = gold_suffix()
    path = Path(gold_dir) / f"market_proxy_{suffix}.parquet"
    n = int(np.asarray(dates).size)
    if not path.exists():
        return MarketProxyResult(np.zeros(n), available=False, column="market_ew")
    mp = pd.read_parquet(path)
    col = "market_ew" if "market_ew" in mp.columns else str(mp.columns[0])
    s = pd.to_numeric(mp[col], errors="coerce")
    s.index = pd.DatetimeIndex(pd.to_datetime(mp.index))
    d = pd.DatetimeIndex(pd.to_datetime(np.asarray(dates)))
    # Forward-fill interior publication gaps (e.g. bond-market holidays on which equities still
    # traded) so a gap carries the LAST KNOWN market return rather than a spurious flat 0.0% — same
    # convention as ``_aligned_series`` (RF/FF) and the module's forward-fill contract. We can't reuse
    # ``_aligned_series`` directly because this parquet stores dates in an UNNAMED DatetimeIndex, which
    # its column-0 index heuristic would misread as the value column (fix: market-proxy ffill).
    s = s[~s.index.duplicated(keep="last")].sort_index()
    aligned = s.reindex(s.index.union(d)).ffill().reindex(d)
    # nan_to_num now only catches a genuine LEADING gap (a target date before the first observation).
    return MarketProxyResult(np.nan_to_num(aligned.to_numpy(dtype=float), nan=0.0), available=True, column=col)


def load_ff_factors(dates: np.ndarray, *, raw_dir: Path | str = _RAW_DIR) -> FactorResult:
    """Per-session Fama-French factor DECIMALS (Mkt-RF/SMB/HML) aligned to ``dates`` for attribution."""
    path = _raw_path(raw_dir, _FF_CSV)
    if not path.exists():
        return FactorResult({}, available=False)
    ff = pd.read_csv(path)
    date_col = "Date" if "Date" in ff.columns else ff.columns[0]
    ff = ff.set_index(date_col)
    out: dict[str, np.ndarray] = {}
    for col in ("Mkt-RF", "SMB", "HML"):
        if col in ff.columns:
            vals, _ = _aligned_series(ff, col, dates)
            out[col] = np.nan_to_num(vals, nan=0.0)  # already decimals in the French daily file
    return FactorResult(out, available=bool(out)) if out else FactorResult({}, available=False)
