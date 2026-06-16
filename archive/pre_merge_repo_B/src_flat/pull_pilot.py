"""Pilot data pulls (plan block T2): 5 stress-chosen tickers x {Refinitiv/Datastream,
yfinance} + FRED + Ken French, frozen to data/ with SHA-256 manifest lines (R4).

Runs LOCALLY (network + entitlements + .env). Vendor sections degrade gracefully:
a missing entitlement prints the docs/DATA_ENTITLEMENTS.md pointer instead of crashing.
"""
from __future__ import annotations

import hashlib
import os
from datetime import date
from pathlib import Path

import pandas as pd

from .config import get

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MANIFEST = Path(__file__).resolve().parent.parent / get("data.manifest")


def _freeze(df: pd.DataFrame, name: str) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / name
    if path.exists():
        raise FileExistsError(f"{path} exists — data is write-once (R4); version the filename + ADR")
    df.to_csv(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with open(MANIFEST, "a") as f:
        f.write(f"{digest}  {name}  frozen={date.today().isoformat()}\n")
    print(f"[FROZEN] {name}  sha256={digest[:16]}…  rows={len(df)}")


def pull_yfinance(tickers: list[str], start: str, end: str) -> None:
    try:
        import yfinance as yf
    except ImportError:
        print("[SKIP] yfinance not installed")
        return
    px = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)["Close"]
    _freeze(px, "yfinance_pilot_adjclose.csv")
    _freeze(px.pct_change().dropna(how="all"), "yfinance_pilot_returns.csv")


def pull_refinitiv(tickers: list[str], start: str, end: str) -> None:
    try:
        import refinitiv.data as rd  # Workspace desktop session must be running
    except ImportError:
        print("[SKIP] refinitiv.data not installed/entitled -> docs/DATA_ENTITLEMENTS.md "
              "(tests 1-6 + escalation email). Reconciliation will run yfinance-only.")
        return
    rd.open_session()
    df = rd.get_history(universe=tickers, fields=["TR.TotalReturn"], start=start, end=end)
    _freeze(df, "refinitiv_pilot_totalreturn.csv")
    rd.close_session()


def pull_fred(series: list[str], start: str, end: str) -> None:
    key = os.environ.get("FRED_API_KEY")
    try:
        if key:
            from fredapi import Fred
            fred = Fred(api_key=key)
            df = pd.DataFrame({s: fred.get_series(s, start, end) for s in series})
        else:
            from pandas_datareader import data as pdr
            df = pdr.DataReader(series, "fred", start, end)
    except Exception as e:
        print(f"[SKIP] FRED: {e}")
        return
    _freeze(df, "fred_macro_pilot.csv")


def pull_french(files: list[str], start: str) -> None:
    try:
        from pandas_datareader import data as pdr
        for fname in files:
            ds = pdr.DataReader(fname, "famafrench", start=start)
            _freeze(ds[0] / 100.0, f"french_{fname.replace('/', '_')}.csv")  # percent -> decimal
    except Exception as e:
        print(f"[SKIP] French: {e}")


def main() -> int:
    cfg = get("data.window")
    tickers = get("data.pilot.tickers")
    start, end = cfg["start"], cfg["end"]
    print(f"[PILOT] {tickers}  {start} -> {end}")
    pull_yfinance(tickers, start, end)
    pull_refinitiv(tickers, start, end)
    pull_fred(get("data.macro_fred"), start, end)
    pull_french(get("data.factors_french"), start)
    print(f"[PILOT] manifest: {MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
