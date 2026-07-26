"""Feedback-block serialization — a shared schema with structure-matched controls (B.5 / F.3).

The headline contribution (H2) is the *information content* of the feedback, not
its token count. To isolate content from token count, the PLACEBO controls (placebo,
placebo_shuffled) match the distributional block's EXACT line count and field layout,
differing only in content; the scalar and scalar_cvar5 arms deliberately carry FEWER
lines (a scalar-only header, and header-plus-one-line respectively). This module renders
every block deterministically.

Arms (FINAL_PLAN B.5 / F.3) and their block content:
  - distributional : scalar metric + the FULL frozen tail set (CVaR 5/10/25/1%,
    left-tail mass, robust skew). CVaR-1% is annotated "(high-variance estimate)".
  - scalar         : scalar metric only; adds NOTHING beyond the shared header.
  - placebo        : scalar metric + an INERT block matched to the distributional
    block in line-count and (approx) length (isolates information from token-count).
  - scalar_cvar5   : scalar metric + EXACTLY ONE downside number, the CVaR-5% line
    (isolates tail-*shape* from *any* downside number).
  - placebo_shuffled : the distributional block's EXACT structure (header, intro, the six
    labelled lines, the CVaR-1% high-variance annotation) but with the six real tail VALUES
    candidate-seeded-PERMUTED (a derangement) across their labels — matches FORMAT and the
    MARGINAL set of numbers, breaks the coherent tail SHAPE. The structure-vs-content control
    (R32): distributional > placebo_shuffled isolates "uses the coherent tail shape" from
    "responds to a plausible-looking numeric table" (the Gupta-Hartford format-vs-content threat).

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

import hashlib

import numpy as np

#: Header line carrying the scalar metric (shared by every arm).
_HEADER = "Your previous reward scored: {metric:.2f} (validation Deflated Sharpe)."

#: Intro line preceding the tail block in the distributional arm.
_TAIL_INTRO = "Realized-return tail diagnostics (training period):"

#: Intro line for the placebo's inert block (matched in role to _TAIL_INTRO). DELIBERATE design choice,
#: KEPT after the 2026-07-02 audit flagged the "inert" wording as an instruction tell: the tell is
#: TRUTHFUL zero-information — without it, six 0.000-valued lines would read as REAL diagnostics
#: reporting a degenerate (riskless) return distribution, i.e. active MISinformation, a strictly worse
#: confound than the disclosed "ignore this" instruction. The tell-free structure control is
#: placebo_shuffled (same _TAIL_INTRO, real deranged values, byte-length-matched to the distributional
#: block); plain placebo is the coarse block-presence control. Both roles + this intro-text confound are
#: disclosed in the write-up, and both caveats are CONSERVATIVE for a null (they make controls easier to
#: beat, so they cannot manufacture the predicted equivalence).
#:
#: ⚠ COMPLETED 2026-07-26 (deep review, loop 8) — the sentence above is TRUE but DIRECTIONAL, and the
#: missing half sits on a load-bearing branch. "Conservative for a null" says the tell cannot manufacture
#: a TIE. It says nothing about a REJECTION — and H2 is a 3-leg intersection-union test that REQUIRES
#: `distributional > placebo` to reject. On that branch the direction inverts: the "ignore this block"
#: tell plausibly SUPPRESSES any format/anchoring response in the plain-placebo arm, so part of a
#: distributional-over-placebo win could be the tell rather than the tail CONTENT. Two things keep this
#: bounded rather than fatal, and both must be stated wherever the leg is reported: (1) the registered
#: a-priori prediction (PREREGISTRATION.md §1a) is the NULL branch, which is exactly the branch the
#: conservativeness argument covers; and (2) the tell-free control `placebo_shuffled` — same
#: `_TAIL_INTRO`, real values DERANGED, byte-length matched — carries no such instruction, which is
#: precisely why it, and not plain placebo, is the structure control promoted to node N5. So the
#: content-over-format claim rests on the tell-free arm; the plain-placebo leg is the coarser
#: block-presence control and should never be the sole evidence for a content claim.
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
    """Deterministic fixed-precision number formatting (RAW renderer — the close-small-float vector)."""
    return f"{value:+.3f}"


#: Decile-rank reference grid (legible rendering only). A line's value is bucketed into a 1..10 decile by
#: its position in [_RANK_LO, _RANK_HI] and tagged "(decile d/10)" — a coarse, legible ORDINAL framing of
#: the small-float magnitude (the numeracy-bottleneck mechanism: rank/bps framing is easier for an LLM to
#: compare than -0.0577 vs -0.0582). Skew, being dimensionless and signed, uses a symmetric reference span.
_RANK_LO, _RANK_HI = -0.12, 0.0  # CVaR return levels live in this (mostly-negative) band
_SKEW_LO, _SKEW_HI = -1.0, 1.0
#: ``left_tail_mass`` is a PROBABILITY (P[return < -k*sigma], typically 0-0.10) — not a return level.
#: It gets its OWN legible unit (percent) and decile band: bucketing it against the mostly-negative
#: CVaR band clamped every nonnegative mass to a constant "decile 10/10" and printed a probability as
#: "bps" (2026-07-05 P21 fix — one of six fields in the numeracy-ablation leg was mis-unit'd and
#: carried zero ordinal information).
_MASS_LO, _MASS_HI = 0.0, 0.10

#: Fields whose VALUE FALLS as tail RISK RISES (a more negative CVaR; a more negative — i.e. longer —
#: left-tail skew). Their positional decile is INVERTED so that on ALL SIX lines a HIGHER decile means
#: MORE tail risk. Without this the tag meant OPPOSITE things on different lines of the SAME block:
#: a clearly risky tail rendered as "CVaR 1%: decile 1/10" beside "left-tail mass: decile 9/10", both
#: denoting "worst" (2026-07-26 review). That defeats the device's whole purpose — the decile exists to
#: give a coarse ORDINAL framing an LLM can compare WITHOUT float arithmetic, so a direction that flips
#: between lines is worse than no tag, and it biases the numeracy-bottleneck leg
#: (``responsiveness.legible_format_responsiveness_differential``) toward a spurious null.
#: ``left_tail_mass`` is a probability that RISES with risk, so it alone keeps its positional decile.
_DECILE_INVERTED_FIELDS: frozenset[str] = frozenset(
    {"cvar_05", "cvar_10", "cvar_25", "cvar_01", "robust_skew"}
)


def _decile(value: float, lo: float, hi: float) -> int:
    """Bucket ``value`` into a 1..10 decile of [lo, hi] (clamped); deterministic ordinal legibility tag."""
    if hi <= lo:
        return 1
    frac = (float(value) - lo) / (hi - lo)
    frac = min(max(frac, 0.0), 1.0 - 1e-12)
    return int(frac * 10) + 1


def _legible_value(field_id: str, value: float) -> str:
    """The LEGIBLE rendering of one tail value: integer basis points for the CVaR levels, a percent
    for the ``left_tail_mass`` probability (P21 fix), a 2-dp dimensionless number for ``robust_skew``.
    Basis points (value*1e4, rounded to int) lift the close small floats (e.g. -0.0410 -> -410 bps)
    out of the LLM's float-comparison failure regime."""
    if field_id == "robust_skew":
        return f"{float(value):+.2f}"
    if field_id == "left_tail_mass":
        return f"{float(value) * 100.0:.1f}%"
    return f"{int(round(float(value) * 1e4)):+d} bps"


def _legible_line(field_id: str, label: str, value: float) -> str:
    """Render one tail line in the legible format: the EXACT label substring (so ``_was_fed_tail`` still
    matches), the bps/percent/dimensionless value, and an appended decile-rank tag (each field bucketed
    over its OWN band). The CVaR-1% high-variance annotation is preserved (matched-structure across the
    raw/legible renderings)."""
    if field_id == "robust_skew":
        lo, hi = _SKEW_LO, _SKEW_HI
    elif field_id == "left_tail_mass":
        lo, hi = _MASS_LO, _MASS_HI
    else:
        lo, hi = _RANK_LO, _RANK_HI
    decile = _decile(value, lo, hi)
    if field_id in _DECILE_INVERTED_FIELDS:
        decile = 11 - decile  # 1..10 -> 10..1: a HIGHER decile always means MORE tail risk
    line = f"  {label}: {_legible_value(field_id, value)}  (decile {decile}/10)"
    if field_id == "cvar_01":
        line += _HIGH_VARIANCE
    return line


def _dist_line(field_id: str, label: str, tail_stats: dict, *, legible: bool = False) -> str:
    """Render one distributional tail line — RAW (close-small-float) by default, LEGIBLE (bps + decile) when
    ``legible`` is set. The label substring is identical in both renderings."""
    value = float(tail_stats[field_id])
    if legible:
        return _legible_line(field_id, label, value)
    line = f"  {label}: {_fmt(value)}"
    if field_id == "cvar_01":
        line += _HIGH_VARIANCE
    return line


def build_block(
    arm: str,
    scalar_metric: float,
    tail_stats: dict | None,
    *,
    shuffle_seed: int | None = None,
    legible: bool = False,
) -> str:
    """Render the feedback block for the given arm, deterministically.

    Parameters
    ----------
    arm : str
        One of ``"distributional"``, ``"scalar"``, ``"placebo"``, ``"scalar_cvar5"``,
        ``"placebo_shuffled"``.
    scalar_metric : float
        The previous candidate's validation Deflated Sharpe.
    tail_stats : dict or None
        The frozen tail-diagnostic dict (:meth:`ReturnDistribution.tail_stats`), or
        ``None`` for arms that carry no tail content (``scalar``, ``placebo``).
    shuffle_seed : int or None
        REQUIRED for ``placebo_shuffled`` (candidate-seeded, replayable): seeds the
        derangement that permutes the six real tail values across their labels. Ignored by
        every other arm. Keyword-only, so existing positional calls are unaffected.
    legible : bool
        Report-only LEGIBLE rendering of the ``distributional`` tail block (the numeracy-bottleneck
        sub-experiment, ADR-039): the six tail lines render CVaR / left-tail-mass values as integer
        BASIS POINTS and ``robust_skew`` as a 2-dp dimensionless value, each with an appended
        ``(decile d/10)`` rank tag — keeping the EXACT label substrings so ``_was_fed_tail`` still
        matches. Default ``False`` reproduces the raw close-small-float bytes exactly. Only the
        ``distributional`` arm (the six-line block) is affected; ignored by every other arm.

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
        lines += [_dist_line(fid, label, tail_stats, legible=legible) for fid, label in _DIST_FIELDS]
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

    if arm == "placebo_shuffled":
        if tail_stats is None:
            raise ValueError("placebo_shuffled arm requires tail_stats")
        if shuffle_seed is None:
            raise ValueError("placebo_shuffled arm requires a (candidate-seeded) shuffle_seed")
        # Structure-IDENTICAL to the distributional block (same header, _TAIL_INTRO, labels, and the
        # CVaR-1% high-variance annotation), but the six real tail VALUES are permuted across their
        # labels by a candidate-seeded DERANGEMENT (no value left in its own label slot). Matches the
        # FORMAT and the MARGINAL set of numbers; breaks the coherent label->value mapping (the tail
        # SHAPE). The structure-vs-content control (R32).
        values = [float(tail_stats[fid]) for fid, _ in _DIST_FIELDS]
        n = len(values)
        rng = np.random.default_rng(int(shuffle_seed))
        order = np.arange(n)
        perm = np.roll(order, 1)  # guaranteed-derangement fallback (no fixed point)
        for _ in range(64):
            cand = rng.permutation(n)
            if not np.any(cand == order):
                perm = cand
                break
        shuffled = [values[int(i)] for i in perm]
        lines = [header, _TAIL_INTRO]
        for (fid, label), val in zip(_DIST_FIELDS, shuffled):
            line = f"  {label}: {_fmt(val)}"
            if fid == "cvar_01":
                line += _HIGH_VARIANCE
            lines.append(line)
        return "\n".join(lines)

    raise ValueError(f"unknown arm: {arm!r}")


def shuffle_seed_from_id(candidate_id: str) -> int:
    """Deterministic, cross-platform seed for the ``placebo_shuffled`` derangement, derived from the
    candidate id so the permutation is per-candidate and REPLAYABLE from the archive. Python's salted
    builtin ``hash()`` is NOT usable (varies per process); ``hashlib.blake2b`` is stable across runs."""
    return int.from_bytes(
        hashlib.blake2b(candidate_id.encode("utf-8"), digest_size=8).digest(), "big"
    )


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
    if arm == "placebo_shuffled":
        # Same field STRUCTURE as distributional (identical labels; only the VALUES are permuted).
        return ["scalar_metric"] + [fid for fid, _ in _DIST_FIELDS]
    raise ValueError(f"unknown arm: {arm!r}")
