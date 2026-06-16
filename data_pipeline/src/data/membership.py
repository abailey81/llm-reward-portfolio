"""Point-in-time membership, survivorship & delisting (stage 7).

Sources (PREREG §5 / config data.universe): Refinitiv TR.IndexConstituentRIC for
>=2016; Datastream monthly lists LS&PCOMP MMYY for 2005-2016; stitched with a 2016
OVERLAP-YEAR cross-validation table (both vendors cover 2016 — their agreement is
the splice's quality certificate). Survivorship bias of ~0.9-1.4%/yr (Elton, Gruber
& Blake 1996; Brown, Goetzmann & Ross 1995) is the reason PIT membership exists.

Delisting: terminal returns are taken from the vendor when present; when missing,
Shumway (1997 JF) / Shumway & Warther (1999 JF) corrections apply (-30% NYSE/AMEX,
-55% Nasdaq; config data.series.delisting_corrections) — EVERY application is
appended to an audit log returned to the caller (logged corrections into derived
layers; raw untouched, R4). Leavers are LIQUIDATED at last traded price net of cost
in the panel stage — never silently dropped.

Leakage posture: `top30_at` uses the latest membership month-end STRICTLY BEFORE the
window start and market caps from the last session STRICTLY BEFORE the window start —
selection at t uses only information < t (R3).
"""
from __future__ import annotations

import pandas as pd

from ..config import get


def normalize_membership(long_df: pd.DataFrame, source: str) -> pd.DataFrame:
    """-> tidy frame {month_end: Timestamp, ric: str, source: str}, deduplicated."""
    df = long_df.rename(columns=str.lower).copy()
    if not {"month_end", "ric"} <= set(df.columns):
        raise ValueError("membership frame needs columns month_end, ric")
    df["month_end"] = pd.to_datetime(df["month_end"]) + pd.offsets.MonthEnd(0)
    df["ric"] = df["ric"].astype(str).str.strip()
    df["source"] = source
    return df[["month_end", "ric", "source"]].drop_duplicates().sort_values(
        ["month_end", "ric"]).reset_index(drop=True)


def stitch_membership(pre2016: pd.DataFrame | None, post2016: pd.DataFrame,
                      splice_year: int = 2016) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Splice Datastream (<splice_year) onto Refinitiv (>=splice_year) and build the
    overlap cross-validation table for every month BOTH sources cover.

    Returns (pit_membership, overlap_table). With pre2016 absent (entitlement gap),
    the splice degrades to the post-2016 span alone — the gap is the caller's
    quarantine item, never silently back-filled (R4)."""
    overlap_rows = []
    if pre2016 is not None and not pre2016.empty:
        both = sorted(set(pre2016["month_end"]) & set(post2016["month_end"]))
        for m in both:
            a = set(pre2016.loc[pre2016["month_end"] == m, "ric"])
            b = set(post2016.loc[post2016["month_end"] == m, "ric"])
            union, inter = a | b, a & b
            overlap_rows.append({
                "month_end": m, "n_pre_source": len(a), "n_post_source": len(b),
                "jaccard": round(len(inter) / len(union), 4) if union else 1.0,
                "only_pre": sorted(a - b)[:10], "only_post": sorted(b - a)[:10],
            })
        pit = pd.concat([
            pre2016[pre2016["month_end"] < pd.Timestamp(f"{splice_year}-01-01")],
            post2016[post2016["month_end"] >= pd.Timestamp(f"{splice_year}-01-01")],
        ], ignore_index=True)
    else:
        pit = post2016.copy()
    pit = pit.sort_values(["month_end", "ric"]).reset_index(drop=True)
    return pit, pd.DataFrame(overlap_rows)


def joiners_leavers(pit: pd.DataFrame) -> pd.DataFrame:
    """Month-on-month membership events -> the audit log {month_end, ric, event}."""
    months = sorted(pit["month_end"].unique())
    rows = []
    for prev, cur in zip(months, months[1:]):
        a = set(pit.loc[pit["month_end"] == prev, "ric"])
        b = set(pit.loc[pit["month_end"] == cur, "ric"])
        rows += [{"month_end": cur, "ric": r, "event": "joiner"} for r in sorted(b - a)]
        rows += [{"month_end": cur, "ric": r, "event": "leaver"} for r in sorted(a - b)]
    return pd.DataFrame(rows)


def apply_shumway_corrections(
    returns: pd.DataFrame,
    delisted: dict[str, dict],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Append the Shumway delisting return where the vendor's terminal return is
    missing. `delisted` maps column -> {date, exchange ('nyse_amex'|'nasdaq'),
    vendor_terminal_return (float|None)}.

    Returns (corrected_copy, audit_log). The input frame is NEVER mutated; every
    correction (and every skip-because-vendor-covered) is one audit row — the
    dissertation reports this log verbatim (R4: explicit, logged, cited)."""
    corr = get("data.series.delisting_corrections")
    out = returns.copy()
    log = []
    for name, info in delisted.items():
        if name not in out.columns:
            continue
        date = pd.Timestamp(info["date"])
        vendor_ret = info.get("vendor_terminal_return")
        if vendor_ret is not None and pd.notna(vendor_ret):
            log.append({"ric": name, "date": date, "action": "vendor_terminal_kept",
                        "value": float(vendor_ret)})
            continue
        exchange = info["exchange"]
        if exchange not in corr:
            raise KeyError(f"no delisting correction configured for exchange '{exchange}'")
        value = float(corr[exchange])
        if date not in out.index:
            raise KeyError(f"delisting date {date.date()} not in panel index for {name}")
        out.loc[date, name] = value
        log.append({"ric": name, "date": date, "action": "shumway_correction_applied",
                    "exchange": exchange, "value": value,
                    "citation": "Shumway 1997 JF; Shumway & Warther 1999 JF"})
    return out, pd.DataFrame(log)


def members_asof(pit: pd.DataFrame, when: pd.Timestamp) -> list[str]:
    """Members per the latest month-end STRICTLY BEFORE `when` (PIT, R3)."""
    prior = pit[pit["month_end"] < pd.Timestamp(when)]
    if prior.empty:
        raise ValueError(f"no membership month-end before {when} — span starts later")
    last = prior["month_end"].max()
    return sorted(prior.loc[prior["month_end"] == last, "ric"])


def top30_at(window_start: pd.Timestamp, mcap: pd.DataFrame,
             pit: pd.DataFrame, n: int | None = None) -> list[str]:
    """The pre-registered selection rule (PREREG §5): top-n by market cap among PIT
    members as of the window start. Caps are read from the LAST SESSION STRICTLY
    BEFORE window_start; names without a prior cap cannot be selected (no
    information -> no position, rather than any imputation)."""
    n = int(n if n is not None else get("environment.universe.n_assets"))
    when = pd.Timestamp(window_start)
    members = [m for m in members_asof(pit, when) if m in mcap.columns]
    prior_caps = mcap.loc[mcap.index < when]
    if prior_caps.empty:
        raise ValueError("no market-cap observation strictly before the window start")
    snapshot = prior_caps.iloc[-1][members].dropna().sort_values(ascending=False)
    if len(snapshot) < n:
        raise ValueError(f"only {len(snapshot)} capped members before {when.date()} — need {n}")
    return list(snapshot.index[:n])
