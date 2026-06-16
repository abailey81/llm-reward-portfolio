"""Immutable market-data container shared across the system.

A ``Panel`` is the frozen, point-in-time, survivorship-free data object the environment,
the pipeline, and the measurement code all consume. Asset identities are **anonymised
integer ids** — no tickers, no dates ever flow to a reward function (contamination
defence, FINAL_PLAN B.8 / N3). The gold panel is built by ``src.data.pipeline``; an
identically-shaped synthetic panel is built by ``src.data.synthetic`` for tests and for
shipping (the licensed gold data is not redistributable, audit C-3).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

__all__ = ["Panel"]


@dataclass(frozen=True)
class Panel:
    """A frozen ``(T, N)`` market panel.

    Parameters
    ----------
    returns : np.ndarray, shape (T, N)
        Simple per-asset daily returns. ``returns[t]`` is realised *after* the action at
        step ``t`` (timing enforced by the environment, audit C-5).
    vix : np.ndarray, shape (T,)
        A volatility-index level. The environment only ever exposes a **lagged** value so
        it is knowable at decision time.
    dates : np.ndarray, shape (T,)
        ``datetime64[D]`` (or integer) index. Used by the pipeline/splits/regimes — never
        passed into a reward.
    asset_ids : np.ndarray, shape (N,)
        Anonymised integer ids. Stable within a frozen panel; carry no semantic meaning.
    market_caps : np.ndarray | None, shape (T, N)
        Optional point-in-time market caps for top-N selection.
    """

    returns: np.ndarray
    vix: np.ndarray
    dates: np.ndarray
    asset_ids: np.ndarray
    market_caps: np.ndarray | None = None

    def __post_init__(self) -> None:
        if self.returns.ndim != 2:
            raise ValueError(f"returns must be 2-D (T, N); got shape {self.returns.shape}")
        t, n = self.returns.shape
        if self.vix.shape != (t,):
            raise ValueError(f"vix must be shape ({t},); got {self.vix.shape}")
        if self.dates.shape != (t,):
            raise ValueError(f"dates must be shape ({t},); got {self.dates.shape}")
        if self.asset_ids.shape != (n,):
            raise ValueError(f"asset_ids must be shape ({n},); got {self.asset_ids.shape}")
        if self.market_caps is not None and self.market_caps.shape != (t, n):
            raise ValueError(f"market_caps must be shape ({t}, {n}); got {self.market_caps.shape}")
        if not np.isfinite(self.returns).all():
            raise ValueError("returns contains non-finite values")

    @property
    def T(self) -> int:  # noqa: N802 - conventional dimension name
        """Number of time steps."""
        return self.returns.shape[0]

    @property
    def N(self) -> int:  # noqa: N802 - conventional dimension name
        """Number of assets (excluding cash)."""
        return self.returns.shape[1]

    def slice(self, start: int, end: int) -> "Panel":
        """Return a contiguous ``[start, end)`` time-slice as a new ``Panel``."""
        return Panel(
            returns=self.returns[start:end],
            vix=self.vix[start:end],
            dates=self.dates[start:end],
            asset_ids=self.asset_ids,
            market_caps=None if self.market_caps is None else self.market_caps[start:end],
        )
