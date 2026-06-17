"""Tests for the real-gold loader (``src/data/loaders.py``).

These run against the frozen gold panel in ``data/gold/`` and are skipped if it is absent (so CI without
the licensed data still passes). They check the two invariants the loader exists to guarantee:
finiteness (the env's contract) and anonymisation (the contamination defence).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from src.data.loaders import load_gold_panel
from src.data.panel import Panel

_GOLD = Path(__file__).resolve().parents[1] / "data" / "gold" / "returns_panel_univ3.parquet"
pytestmark = pytest.mark.skipif(not _GOLD.exists(), reason="frozen gold panel not present (licensed data)")


def test_dev_panel_loads_finite_and_shaped() -> None:
    res = load_gold_panel("development")
    p = res.panel
    assert isinstance(p, Panel)
    assert p.returns.shape[1] == 30  # top-30 universe
    assert p.returns.shape[0] == p.vix.shape[0] == p.dates.shape[0]  # aligned T
    assert np.isfinite(p.returns).all()  # env rejects non-finite — the loader's job
    assert np.isfinite(p.vix).all()


def test_panel_is_anonymised() -> None:
    """No RIC/ticker/string identity may live in the Panel (N3 contamination defence)."""
    res = load_gold_panel("development")
    assert res.panel.asset_ids.dtype.kind in "iu"  # integer ids only
    assert list(res.panel.asset_ids) == list(range(30))
    # the RIC map is provenance-only and lives OUTSIDE the panel
    assert len(res.ric_by_id) == 30
    assert all(isinstance(r, str) for r in res.ric_by_id.values())


def test_liquidate_to_cash_makes_dead_names_finite() -> None:
    """Wachovia (WB.N^A09, delists 2009) is in the dev top-30; default policy must absorb its NaNs."""
    res = load_gold_panel("development", on_missing="liquidate_to_cash")
    assert np.isfinite(res.panel.returns).all()
    assert "WB.N^A09" in res.ric_by_id.values()  # the dead name is RETAINED, not survivorship-dropped


def test_error_policy_flags_delisting_nans() -> None:
    """on_missing='error' must refuse the dev window (it contains mid-window delistings)."""
    with pytest.raises(ValueError, match="NaN"):
        load_gold_panel("development", on_missing="error")


def test_walk_forward_requires_explicit_end() -> None:
    with pytest.raises(ValueError, match="explicit `end`"):
        load_gold_panel("walk_forward")
