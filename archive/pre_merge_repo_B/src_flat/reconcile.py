"""Vendor reconciliation (plan block T3): per-ticker return correlation, max |Δ|,
days-over-tolerance, dividend-date mismatches, GE index-exit continuity. Writes the
table between the AUTO markers in reports/vendor_reconciliation_pilot.md.

Two vendors disagreeing is INFORMATION (Ince & Porter 2006) — this report seeds the
EDA-that-motivates-method section. Runs locally after `make pull-pilot`.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .config import get

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "reports" / "vendor_reconciliation_pilot.md"


def _load_returns() -> tuple[pd.DataFrame, pd.DataFrame | None]:
    yf_path = ROOT / "data" / "yfinance_pilot_returns.csv"
    if not yf_path.exists():
        raise FileNotFoundError("run `make pull-pilot` first")
    yf_ret = pd.read_csv(yf_path, index_col=0, parse_dates=True)
    rf_path = ROOT / "data" / "refinitiv_pilot_totalreturn.csv"
    rf_ret = None
    if rf_path.exists():
        rf = pd.read_csv(rf_path, index_col=0, parse_dates=True)
        rf_ret = rf / 100.0 if rf.abs().median().median() > 1 else rf  # TR.TotalReturn is %
    return yf_ret, rf_ret


def main() -> int:
    tol = float(get("data.vendors.reconciliation_tolerance.daily_return_abs"))
    yf_ret, rf_ret = _load_returns()
    rows = []
    for t in yf_ret.columns:
        if rf_ret is None or t not in rf_ret.columns:
            rows.append(f"| {t} | ⟨refinitiv pending⟩ | — | — | — | yfinance-only |")
            continue
        pair = pd.concat([yf_ret[t], rf_ret[t]], axis=1, keys=["yf", "rf"]).dropna()
        d = (pair["yf"] - pair["rf"]).abs()
        corr = pair["yf"].corr(pair["rf"])
        over = int((d > tol).sum())
        # dividend-day proxy: large one-day gaps that reverse (adjustment mismatches cluster there)
        div_mism = int(((d > 10 * tol) & (d.shift(-1) > 10 * tol)).sum())
        rows.append(f"| {t} | {corr:.6f} | {d.max():.2e} | {over} | {div_mism} | |")

    ge_note = "⟨refinitiv pending⟩"
    if rf_ret is not None and "GE" in rf_ret.columns:
        exit_d = pd.Timestamp(get("data.pilot.ge_index_exit"))
        win = rf_ret["GE"].loc[exit_d - pd.Timedelta(days=7): exit_d + pd.Timedelta(days=7)]
        ge_note = f"{win.notna().sum()}/{len(win)} obs present around exit; max |r|={win.abs().max():.3f}"

    block = "\n".join(
        ["| Ticker | corr(daily ret) | max \\|Δ\\| | days >tol | dividend mismatches | notes |",
         "|---|---|---|---|---|---|", *rows,
         f"GE index-exit continuity (±5d): {ge_note}"]
    )
    text = REPORT.read_text()
    text = re.sub(r"(<!-- BEGIN AUTO.*?-->\n).*?(\n<!-- END AUTO -->)",
                  lambda m: m.group(1) + block + m.group(2), text, flags=re.S)
    REPORT.write_text(text)
    print(f"[RECONCILE] wrote table -> {REPORT}")
    print(block)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
