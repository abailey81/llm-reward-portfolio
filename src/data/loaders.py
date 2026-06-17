"""Load the frozen REAL gold panel (Refinitiv) into the engine's :class:`Panel`.

The gold panel in ``data/gold/`` is the survivorship-free, point-in-time research data built by
``data_pipeline/`` (ADR-019…022): ``returns_panel_univ3.parquet`` (5,283 sessions × 953 RICs,
2005–2025), ``cash_features_univ3.parquet`` (``vol20``, ``vol20_over_vol60``, ``vix`` = FRED VIXCLS —
CBOE ``.VIX`` is not licensed), and ``top30_selection_univ3.parquet`` (the point-in-time top-30 RICs at
each window start). This module slices a single window's top-30 into a finite, **anonymised** ``Panel``
the environment can train on.

Two invariants are enforced here so the contamination defence (N3, FINAL_PLAN B.8) and the env's
finiteness contract hold:

1. **Anonymisation.** The ``Panel`` carries only integer ``asset_ids`` (``0..N-1``) — **no RICs, no
   tickers, no dates ever reach a reward**. The RIC↔id mapping is returned *separately* (opt-in) for
   provenance/analysis only and must never be passed into a reward or the LLM.

2. **Finiteness via an explicit delisting policy.** A survivorship-free top-30 contains names that die
   mid-window (e.g. Wachovia ``WB.N^A09`` delists 2009; Dell ``DELL.OQ^J13`` goes private 2013), so the
   raw slice has NaNs after delisting. The env *rejects* non-finite rows (``environment_spec_v1``), so a
   policy is required. The default, ``on_missing="liquidate_to_cash"``, sets post-event / missing returns
   to ``0.0`` (proceeds held flat ≈ cash) — the standard survivorship-correct treatment that preserves
   the dead names rather than dropping them (dropping would silently re-introduce survivorship bias).

   ⚠ **PROVISIONAL — needs preregistration sign-off (see DECISIONS.md ADR-024).** The intra-window
   delisting mechanic is a frozen-design decision the env does not yet model explicitly; ``liquidate_to_cash``
   is a defensible default for the prototype, not a ratified choice for the headline result.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd

from .panel import Panel

__all__ = ["load_gold_panel", "GoldLoadResult"]

# Repo-root-relative default location of the frozen gold artifacts.
_GOLD_DIR = Path(__file__).resolve().parents[2] / "data" / "gold"
_SUFFIX = "univ3"  # canonical research panel (ADR-021); _univ/_univ2 are superseded

# Split ends (inclusive) from the frozen preregistration §data_splits. Used only to bound a window when
# an explicit ``end`` is not given; kept here as a documented default, not a source of truth.
_DEV_END = "2014-12-31"  # train split end (val begins 2015)

OnMissing = Literal["liquidate_to_cash", "ffill_then_zero", "error"]


class GoldLoadResult:
    """A loaded panel plus its (non-reward) provenance mapping.

    ``panel`` is the anonymised, finite :class:`Panel` for the environment. ``ric_by_id`` maps each
    integer ``asset_id`` back to its Refinitiv RIC — **for provenance/analysis only**; it must never be
    handed to a reward function or the LLM (contamination defence).
    """

    def __init__(self, panel: Panel, ric_by_id: dict[int, str], window: str) -> None:
        self.panel = panel
        self.ric_by_id = ric_by_id
        self.window = window


def _read(name: str, gold_dir: Path) -> pd.DataFrame:
    path = gold_dir / f"{name}_{_SUFFIX}.parquet"
    if not path.exists():
        raise FileNotFoundError(
            f"gold artifact not found: {path}. Build it via data_pipeline/ (needs Refinitiv creds) "
            f"or check data/gold/."
        )
    return pd.read_parquet(path)


def _window_rics(top30: pd.DataFrame, phase: str) -> tuple[list[str], pd.Timestamp]:
    rows = top30[top30["phase"] == phase]
    if rows.empty:
        raise KeyError(f"phase {phase!r} not in top30_selection (have {sorted(top30['phase'].unique())})")
    row = rows.iloc[0]
    sel = row["selection"]
    if not isinstance(sel, (list, tuple, np.ndarray)):
        sel = ast.literal_eval(sel)
    return list(sel), pd.Timestamp(row["window_start"])


def load_gold_panel(
    phase: str = "development",
    *,
    end: str | pd.Timestamp | None = None,
    gold_dir: Path | str = _GOLD_DIR,
    on_missing: OnMissing = "liquidate_to_cash",
) -> GoldLoadResult:
    """Load one window's point-in-time top-30 into a finite, anonymised :class:`Panel`.

    Parameters
    ----------
    phase
        A window label in ``top30_selection_univ3`` (``"development"`` or a ``"walk_forward"`` start).
        For ``"walk_forward"`` there are several rows; pass an explicit ``end`` to disambiguate the span.
    end
        Inclusive last session. Defaults to the train-split end (``2014-12-31``) for ``"development"``;
        for walk-forward windows an explicit ``end`` is required (no silent guess).
    on_missing
        Delisting / missing-return policy (see module docstring). ``"liquidate_to_cash"`` (default) →
        fill NaN with ``0.0``; ``"ffill_then_zero"`` → forward-fill within the window then zero-fill the
        leading gaps; ``"error"`` → raise if any NaN remains (use only for a continuously-alive universe).
    """
    gold_dir = Path(gold_dir)
    returns = _read("returns_panel", gold_dir)
    cash = _read("cash_features", gold_dir)
    top30 = _read("top30_selection", gold_dir)

    rics, start = _window_rics(top30, phase)
    if end is None:
        if phase == "development":
            end = pd.Timestamp(_DEV_END)
        else:
            raise ValueError(f"phase {phase!r} needs an explicit `end` (walk-forward span is ambiguous).")
    end = pd.Timestamp(end)

    missing_rics = [r for r in rics if r not in returns.columns]
    if missing_rics:
        raise KeyError(f"top-30 RICs absent from returns panel: {missing_rics}")

    sub = returns.loc[start:end, rics].copy()
    vix_s = cash.loc[start:end, "vix"].copy()
    if sub.empty:
        raise ValueError(f"empty window {start}..{end} for phase {phase!r}")

    # --- finiteness via the delisting policy ---
    if on_missing == "liquidate_to_cash":
        sub = sub.fillna(0.0)
    elif on_missing == "ffill_then_zero":
        sub = sub.ffill().fillna(0.0)
    elif on_missing == "error":
        if sub.isna().any().any():
            bad = sub.columns[sub.isna().any()].tolist()
            raise ValueError(f"NaNs present under on_missing='error' (names: {bad[:5]}…)")
    else:  # pragma: no cover - guarded by Literal
        raise ValueError(f"unknown on_missing={on_missing!r}")
    # VIX must be knowable; forward-fill the (rare) gaps, never leak the future.
    vix_s = vix_s.ffill().bfill()

    returns_arr = sub.to_numpy(dtype=float)
    vix_arr = vix_s.to_numpy(dtype=float)
    dates_arr = sub.index.to_numpy()  # datetime64[ns]; never enters a reward
    n_assets = returns_arr.shape[1]
    asset_ids = np.arange(n_assets, dtype=int)  # ANONYMISED — no RICs in the Panel

    if not np.isfinite(returns_arr).all():
        raise ValueError("returns still non-finite after the missing-data policy — investigate the slice")
    if not np.isfinite(vix_arr).all():
        raise ValueError("vix non-finite after fill — check cash_features.vix over the window")

    panel = Panel(returns=returns_arr, vix=vix_arr, dates=dates_arr, asset_ids=asset_ids)
    ric_by_id = {i: ric for i, ric in enumerate(rics)}  # provenance ONLY — never to a reward/LLM
    return GoldLoadResult(panel=panel, ric_by_id=ric_by_id, window=phase)
