"""Feedback-block serialization — identical structure across arms (B.5 / F.3).

The headline contribution (H2) is the *information content* of the feedback, not
its token count. To make that claim cleanly, every feedback block shares an
IDENTICAL structure (line count, field layout); only the *content* differs across
arms. This module renders those blocks deterministically.

Arms (FINAL_PLAN B.5 / F.3) and their block content:
  - distributional : scalar metric + the FULL frozen tail set (CVaR 5/10/25/1%,
    left-tail mass, robust skew). CVaR-1% is annotated "(high-variance estimate)".
  - scalar         : scalar metric only; adds NOTHING beyond the shared header.
  - placebo        : scalar metric + an INERT block matched to the distributional
    block in line-count and (approx) length (isolates information from token-count).
  - scalar_cvar5   : scalar metric + EXACTLY ONE downside number, the CVaR-5% line
    (isolates tail-*shape* from *any* downside number).

Worked example (distributional block, from FINAL_PLAN F.3):
    Your previous reward scored: 0.83 (validation Deflated Sharpe).
    Realized-return tail diagnostics (training period):
      CVaR 5%:  -0.041
      CVaR 10%: -0.029
      CVaR 25%: -0.016
      CVaR 1%:  -0.067  (high-variance estimate)
      left-tail mass: 0.061
      left-tail skew: -0.38

Audit refs: A-1 (feedback channel is the contribution), B-5 (matched-structure arms),
B-7 (CVaR-1% flagged high-variance in the rendered text).
"""

from __future__ import annotations

#: Header line carrying the scalar metric (shared by every arm).
_HEADER = "Your previous reward scored: {metric:.2f} (validation Deflated Sharpe)."

#: Intro line preceding the tail block in the distributional arm.
_TAIL_INTRO = "Realized-return tail diagnostics (training period):"

#: Intro line for the placebo's inert block (matched in role to _TAIL_INTRO).
_PLACEBO_INTRO = "Reference constants (inert; no diagnostic content):"

#: Ordered (field-id, label) pairs composing the distributional tail block. The
#: order matches the worked example in the module docstring.
_DIST_FIELDS: list[tuple[str, str]] = [
    ("cvar_05", "CVaR 5%"),
    ("cvar_10", "CVaR 10%"),
    ("cvar_25", "CVaR 25%"),
    ("cvar_01", "CVaR 1%"),
    ("left_tail_mass", "left-tail mass"),
    ("robust_skew", "left-tail skew"),
]

#: Annotation appended to the CVaR-1% line (audit B-7).
_HIGH_VARIANCE = "  (high-variance estimate)"


def _fmt(value: float) -> str:
    """Deterministic fixed-precision number formatting."""
    return f"{value:+.3f}"


def _dist_line(field_id: str, label: str, tail_stats: dict) -> str:
    """Render one distributional tail line."""
    line = f"  {label}: {_fmt(float(tail_stats[field_id]))}"
    if field_id == "cvar_01":
        line += _HIGH_VARIANCE
    return line


def build_block(arm: str, scalar_metric: float, tail_stats: dict | None) -> str:
    """Render the feedback block for the given arm, deterministically.

    Parameters
    ----------
    arm : str
        One of ``"distributional"``, ``"scalar"``, ``"placebo"``, ``"scalar_cvar5"``.
    scalar_metric : float
        The previous candidate's validation Deflated Sharpe.
    tail_stats : dict or None
        The frozen tail-diagnostic dict (:meth:`ReturnDistribution.tail_stats`), or
        ``None`` for arms that carry no tail content (``scalar``, ``placebo``).

    Returns
    -------
    str
        The rendered feedback block. Identical inputs yield a byte-identical string.

    Raises
    ------
    ValueError
        If ``arm`` is unknown, or a tail-carrying arm is given ``tail_stats=None``.
    """
    header = _HEADER.format(metric=float(scalar_metric))

    if arm == "scalar":
        return header

    if arm == "distributional":
        if tail_stats is None:
            raise ValueError("distributional arm requires tail_stats")
        lines = [header, _TAIL_INTRO]
        lines += [_dist_line(fid, label, tail_stats) for fid, label in _DIST_FIELDS]
        return "\n".join(lines)

    if arm == "scalar_cvar5":
        if tail_stats is None:
            raise ValueError("scalar_cvar5 arm requires tail_stats")
        cvar5_line = f"  CVaR 5%: {_fmt(float(tail_stats['cvar_05']))}"
        return "\n".join([header, cvar5_line])

    if arm == "placebo":
        # Inert block matched to the distributional block in line count, and within
        # +/-15% of its character length, with neutral placeholder values. The intro
        # plus one line per distributional field keeps the line count identical.
        lines = [header, _PLACEBO_INTRO]
        for i in range(len(_DIST_FIELDS)):
            lines.append(f"  reference value {i + 1}: {_fmt(0.0)}")
        return "\n".join(lines)

    raise ValueError(f"unknown arm: {arm!r}")


def block_fields(arm: str) -> list[str]:
    """Return the ordered field names composing the given arm's block.

    Used by the tests to assert matched field-structure across arms (placebo vs
    distributional field-count, scalar_cvar5 == scalar + one).

    Parameters
    ----------
    arm : str
        Arm name.

    Returns
    -------
    list of str
        Ordered list of field identifiers present in that arm's block (header
        included as ``"scalar_metric"``).

    Raises
    ------
    ValueError
        If ``arm`` is unknown.
    """
    if arm == "scalar":
        return ["scalar_metric"]
    if arm == "distributional":
        return ["scalar_metric"] + [fid for fid, _ in _DIST_FIELDS]
    if arm == "scalar_cvar5":
        return ["scalar_metric", "cvar_05"]
    if arm == "placebo":
        return ["scalar_metric"] + [
            f"reference_value_{i + 1}" for i in range(len(_DIST_FIELDS))
        ]
    raise ValueError(f"unknown arm: {arm!r}")
