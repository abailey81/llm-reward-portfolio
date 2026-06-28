"""Data-contract validation for a frozen :class:`~src.data.panel.Panel`.

WHY THIS EXISTS. ``Panel.__post_init__`` already enforces the *structural* contract (2-D shape,
matching ``(T, N)`` dimensions, finite returns). This module adds the *semantic / research*
invariants the constructor cannot express — the ones whose violation would be a silent data error
or, worse, a **look-ahead leak** (the cardinal sin in a finance backtest). It consolidates the checks
that were previously implicit/scattered (checksum, NaN policy, the leakage-free VIX fill) into one
auditable contract that can be asserted on load and unit-tested directly.

It is a *report-only* validator: it reads an already-built panel and never mutates it, so it is
deterministic and adds no dependency. Scope discipline: this is NOT supervised-learning data
validation (there are no labels/classes here) — it is the leakage + integrity contract for an RL
returns panel (see ``docs/DATA_PIPELINE_LIFECYCLE_ASSESSMENT.md`` for the strict relevance map).
"""
from __future__ import annotations

import numpy as np

from .panel import Panel

__all__ = ["PanelContractError", "validate_panel"]

#: A long simple return can lose AT MOST 100%, i.e. ``r >= -1.0``; exactly ``-1.0`` is a legitimate total
#: loss (delisting / bankruptcy — and this project's delisting band includes -100%). Only ``r < -1.0``
#: (losing MORE than 100%) is impossible and signals a mis-scaled action/units error. Returns whose
#: magnitude exceeds ``_MAX_ABS_RETURN`` are implausible at daily frequency (split/units artifact).
_IMPOSSIBLE_RETURN = -1.0  # checked with strict "<" so -1.0 (total loss) is allowed
_MAX_ABS_RETURN = 10.0  # +1000% in one day — a screen flag, not a hard cap


class PanelContractError(ValueError):
    """Raised when a :class:`Panel` violates the data contract (``validate_panel(strict=True)``)."""


def validate_panel(
    panel: Panel,
    *,
    strict: bool = True,
    max_abs_return: float = _MAX_ABS_RETURN,
) -> list[str]:
    """Assert the semantic + leakage invariants of a built ``Panel``.

    Checks (each a distinct, named violation):

    - **Dates strictly increasing** — no duplicate, unsorted, or non-monotone sessions. This is the
      load-bearing **leakage** invariant: an out-of-order or duplicated date silently admits future
      information into a window.
    - **Returns sane** — every simple return is ``> -1.0`` (a long position cannot lose more than
      100%) and ``|r| <= max_abs_return`` (implausible daily moves flag a split/units artifact).
    - **VIX non-negative + finite** — a volatility index cannot be negative.
    - **asset_ids unique + integer** — the anonymisation contract (ids carry no semantic meaning and
      must be distinct; never tickers/strings).
    - **market_caps non-negative** (when present).
    - **No all-zero return column** — a dead / gap-filled asset surfaced as a constant-0 series.

    Structural invariants (shape, finiteness) are already enforced by ``Panel.__post_init__`` and are
    re-checked here defensively.

    Parameters
    ----------
    panel:
        The built panel to validate (never mutated).
    strict:
        If ``True`` (default) raise :class:`PanelContractError` on the first non-empty violation list;
        if ``False`` return the list of violation strings (empty == clean) for the caller to handle.
    max_abs_return:
        The implausible-daily-move screen threshold (default ``10.0`` == +1000%).

    Returns
    -------
    list[str]
        Violation messages (empty if the panel satisfies the contract). Only returned when
        ``strict=False``; otherwise a non-empty list raises.
    """
    issues: list[str] = []

    # --- structural (defensive; Panel.__post_init__ also enforces these) ---
    if panel.returns.ndim != 2:
        issues.append(f"returns must be 2-D (T, N); got {panel.returns.shape}")
        # cannot continue meaningfully without a 2-D matrix
        return _finish(issues, strict)
    if not np.isfinite(panel.returns).all():
        issues.append("returns contains non-finite values (post-NaN-policy finiteness invariant)")

    # --- leakage: dates strictly increasing (no duplicate / unsorted / future) ---
    dates = np.asarray(panel.dates)
    if dates.size >= 2:
        # int64 view works for datetime64[*] (epoch units) and integer date encodings alike.
        order = dates.astype("int64")
        d = np.diff(order)
        if not (d > 0).all():
            n_bad = int((d <= 0).sum())
            issues.append(
                f"dates not strictly increasing ({n_bad} non-positive gap(s)) -- duplicate/unsorted "
                "sessions admit look-ahead leakage"
            )

    # --- returns sanity ---
    r = panel.returns
    if (r < _IMPOSSIBLE_RETURN).any():
        n_bad = int((r < _IMPOSSIBLE_RETURN).sum())
        issues.append(
            f"{n_bad} return(s) < {_IMPOSSIBLE_RETURN} -- impossible for a long simple return "
            "(can lose at most 100%; exactly -1.0 total loss IS allowed for delisting)"
        )
    if (np.abs(r) > max_abs_return).any():
        n_bad = int((np.abs(r) > max_abs_return).sum())
        issues.append(
            f"{n_bad} return(s) with |r| > {max_abs_return} -- implausible daily move (split/units artifact?)"
        )
    # all-zero column = dead / gap-filled asset
    n_zero_cols = int((np.abs(r).sum(axis=0) == 0.0).sum())
    if n_zero_cols:
        issues.append(f"{n_zero_cols} all-zero return column(s) -- dead or gap-filled asset")

    # --- vix ---
    vix = np.asarray(panel.vix, dtype=float)
    if not np.isfinite(vix).all():
        issues.append("vix contains non-finite values")
    if (vix < 0.0).any():
        issues.append("vix < 0 -- a volatility index cannot be negative")

    # --- asset_ids: anonymisation contract ---
    aid = np.asarray(panel.asset_ids)
    if not np.issubdtype(aid.dtype, np.integer):
        issues.append(f"asset_ids must be integer (anonymisation contract); got dtype {aid.dtype}")
    if np.unique(aid).size != aid.size:
        issues.append("asset_ids not unique")

    # --- market caps ---
    if panel.market_caps is not None:
        mc = np.asarray(panel.market_caps, dtype=float)
        if np.isfinite(mc).all() and (mc < 0.0).any():
            issues.append("market_caps < 0 -- a market capitalisation cannot be negative")

    return _finish(issues, strict)


def _finish(issues: list[str], strict: bool) -> list[str]:
    if strict and issues:
        raise PanelContractError(
            "Panel data-contract violated:\n  - " + "\n  - ".join(issues)
        )
    return issues
