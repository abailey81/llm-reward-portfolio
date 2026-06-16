"""PIT universe build: assemble the entitled Refinitiv pulls into the RESEARCH panel
(replaces the shadow universe the moment `pull-universe --live` completes; ADR-020/021).

Inputs (raw vault, checksum-verified): rf_trd_* (daily total returns, datagrid long
form, PERCENT), rf_mcapm_* (monthly market cap, long form), staged pit_membership.
Outputs: staged returns/mcap panels → clean authority-merged returns (refinitiv
primary, yfinance shadow cross-check) → gold via `panel.build_gold` with membership +
mcap supplied, which materialises D2 (mcap panel), D3 (top-30 per window) and the
PIT rebuild of D1/D4/D6 under suffix `_univ`.

Pure assembly — no fabrication: percent→decimal is the only transform on returns;
missing stays missing (the missing-data engine counts it); panels are XNYS-aligned.
"""
from __future__ import annotations

import pandas as pd

from ..config import get
from . import validate
from .panel import build_gold
from .reconcile_full import reconcile_returns
from .security_master import ric_to_yf_ticker
from .vault import freeze, manifest_entries, read_verified, record_lineage


def assemble_long_panel(frames: list[pd.DataFrame], value_name: str,
                        scale: float = 1.0) -> pd.DataFrame:
    """Concatenate datagrid long frames (Instrument, Date, value) -> wide panel.
    Duplicate (date, ric) cells keep the LAST occurrence (chunk overlap guard);
    `scale` converts units (percent -> decimal for returns)."""
    tidy = []
    for df in frames:
        d = df.copy()
        d.columns = ["ric", "date", "value"][: len(d.columns)]
        d["date"] = pd.to_datetime(d["date"], errors="coerce")
        d["value"] = pd.to_numeric(d["value"], errors="coerce")
        tidy.append(d.dropna(subset=["date"]))
    long = pd.concat(tidy, ignore_index=True)
    long = long.drop_duplicates(subset=["date", "ric"], keep="last")
    wide = long.pivot(index="date", columns="ric", values="value").sort_index()
    wide.columns.name = None
    wide.index.name = None
    return wide * scale


def _collect(prefix: str) -> list[pd.DataFrame]:
    return [read_verified(e["relpath"]) for e in manifest_entries()
            if e["layer"] == "raw" and e["name"].startswith(prefix)]


def build_universe(suffix: str = "_univ", run_id: str = "build_universe") -> dict:
    """Assemble staged panels and build the PIT gold layer. Raises loudly when the
    required pulls are absent (never substitutes; R4)."""
    trd = _collect("rf_trd_")
    if not trd:
        raise FileNotFoundError("no rf_trd_* artifacts — run `make pull-universe LIVE=1` first")
    mcapm = _collect("rf_mcapm_")
    pit_entries = [e for e in manifest_entries() if e["name"].startswith("pit_membership")]
    if not pit_entries:
        raise FileNotFoundError("pit_membership missing — A1 has not landed")
    pit = read_verified(pit_entries[-1]["relpath"])   # latest grid (incl. selection buffer)
    pit["month_end"] = pd.to_datetime(pit["month_end"])

    window = get("data.window")
    returns = assemble_long_panel(trd, "tr", scale=0.01)        # percent -> decimal
    sessions = validate.trading_sessions(window["start"],
                                         min(pd.Timestamp(window["end"]),
                                             returns.index.max()).date().isoformat())
    returns_aligned, align_rep = validate.align_to_calendar(returns, sessions)
    flags, missing_rep = validate.classify_missing(returns_aligned, sessions,
                                                   raw_index=returns.index)

    raw_inputs = [e for e in manifest_entries() if e["layer"] == "raw"
                  and e["name"].startswith(("rf_trd_", "rf_mcapm_"))]
    art_ret = freeze(returns_aligned, "staged", f"staged_returns_refinitiv{suffix}.parquet",
                     {"vendor": "refinitiv", "stage": "build_universe",
                      "units": "decimal (percent/100)", "alignment": align_rep,
                      "missing": missing_rep.as_dict()}, fmt="parquet", run_id=run_id)
    record_lineage(art_ret, raw_inputs, "build_universe.staging",
                   {"n_names": int(returns_aligned.shape[1])})

    mcap_art = None
    mcap_panel = None
    if mcapm:
        mcap_panel = assemble_long_panel(mcapm, "mcap")
        mcap_art = freeze(mcap_panel, "staged", f"staged_mcap_refinitiv{suffix}.parquet",
                          {"vendor": "refinitiv", "stage": "build_universe",
                           "frequency": "monthly"}, fmt="parquet", run_id=run_id)
        record_lineage(mcap_art, raw_inputs, "build_universe.staging", {})

    # clean: refinitiv IS the authority for total_return (config vendor_authority);
    # the yfinance shadow stays a parallel staged panel for reconciliation, never
    # blended cell-wise into the research series (R4).
    art_clean = freeze(returns_aligned, "clean", f"clean_returns{suffix}.parquet",
                       {"vendor": "refinitiv", "stage": "build_universe",
                        "authority": "refinitiv (config data.platform.vendor_authority)"},
                       fmt="parquet", run_id=run_id)
    record_lineage(art_clean, [art_ret], "authority", {})

    fred = next((e for e in manifest_entries() if e["name"] == "fred_macro.csv"), None)
    if fred is None:
        raise FileNotFoundError("fred_macro.csv missing — VIX required for gold features")
    vix = read_verified("fred_macro.csv")["VIXCLS"].astype(float)
    vix.index = pd.to_datetime(vix.index)

    gold = build_gold(returns_aligned, vix, sessions,
                      clean_mcap=mcap_panel, pit_membership=pit,
                      run_id=run_id, input_artifacts=[art_clean], suffix=suffix)
    recon = reconcile_against_shadow(returns_aligned)
    return {"staged_returns": art_ret.relpath,
            "staged_mcap": mcap_art.relpath if mcap_art else None,
            "clean": art_clean.relpath,
            "gold": {k: a.relpath for k, a in gold["artifacts"].items()},
            "n_names": int(returns_aligned.shape[1]),
            "n_sessions": int(len(sessions)),
            "missing": missing_rep.as_dict(),
            "reconciliation": recon}


def reconcile_against_shadow(univ_returns: pd.DataFrame) -> dict | None:
    """Two-vendor reconciliation at last (stage 9, activated): map the universe
    panel's RIC columns to yfinance tickers (security_master convention) and
    reconcile against the shadow panel on the intersection. Returns the summary dict
    (full markdown written to reports/) or None when no shadow panel exists."""
    shadow_entry = next((e for e in manifest_entries()
                         if e["name"] == "staged_returns_yfinance_v2.parquet"), None)
    if shadow_entry is None:
        return None
    shadow = read_verified(shadow_entry["relpath"])
    shadow.index = pd.to_datetime(shadow.index)
    mapped = univ_returns.copy()
    mapped.columns = [ric_to_yf_ticker(str(c)) for c in mapped.columns]
    mapped = mapped.loc[:, ~mapped.columns.duplicated(keep="first")]
    common = sorted(set(mapped.columns) & set(shadow.columns))
    if not common:
        return {"common_names": 0}

    def _collect_yf(prefix: str) -> pd.DataFrame | None:
        frames = [read_verified(e["relpath"]) for e in manifest_entries()
                  if e["layer"] == "raw" and e["name"].startswith(prefix)]
        if not frames:
            return None
        out = pd.concat(frames, axis=1)
        out = out.loc[:, ~out.columns.duplicated()]
        out.index = pd.to_datetime(out.index)
        return out

    divs = _collect_yf("yf_dividends_")               # ex-div/split clustering context:
    spl = _collect_yf("yf_splits_")                   # adjustment-methodology gaps cluster there
    rep = reconcile_returns(mapped[common], shadow[common], dividends=divs, splits=spl)
    from . import vault
    root = vault.ROOT                       # vault's ROOT: tmp-redirected in tests
    out = root / "reports" / "vendor_reconciliation_univ.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("# Two-vendor reconciliation — Refinitiv (authority) vs yfinance (shadow)\n\n"
                   f"Names compared: {len(common)} (RIC→ticker mapped via security master). "
                   "Tolerance: config data.vendors.reconciliation_tolerance.\n\n"
                   + rep.to_markdown() + "\n")
    rows = rep.rows
    return {"common_names": len(common),
            "median_corr": float(pd.Series([r.corr for r in rows]).median()),
            "total_days_over_tol": int(sum(r.days_over_tol for r in rows)),
            "unexplained_quarantined": 0 if rep.quarantine is None else int(len(rep.quarantine)),
            "report": str(out.relative_to(root))}
