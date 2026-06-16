"""Tests for src/feedback/schema.py — matched-structure feedback blocks (F.3, B.5)."""

from __future__ import annotations

from src.feedback.schema import block_fields, build_block

ARMS = ["distributional", "scalar", "placebo", "scalar_cvar5"]

TAIL_STATS = {
    "cvar_01": -0.067,
    "cvar_05": -0.041,
    "cvar_10": -0.029,
    "cvar_25": -0.016,
    "left_tail_mass": 0.061,
    "robust_skew": -0.38,
}
METRIC = 0.83


def test_all_blocks_build_without_error() -> None:
    """All four feedback arms render blocks without error (B.5)."""
    for arm in ARMS:
        block = build_block(arm, METRIC, TAIL_STATS)
        assert isinstance(block, str) and len(block) > 0


def test_placebo_matches_distributional_field_count_and_length() -> None:
    """Placebo block matches distributional in line-count and length (inert content)."""
    dist = build_block("distributional", METRIC, TAIL_STATS)
    placebo = build_block("placebo", METRIC, None)

    assert len(dist.splitlines()) == len(placebo.splitlines())
    assert len(block_fields("placebo")) == len(block_fields("distributional"))

    # Char-length within +/-15%.
    ratio = len(placebo) / len(dist)
    assert 0.85 <= ratio <= 1.15


def test_scalar_cvar5_is_scalar_plus_exactly_one_field() -> None:
    """scalar_cvar5 block == scalar block + exactly the CVaR-5% line."""
    scalar = build_block("scalar", METRIC, None)
    cvar5 = build_block("scalar_cvar5", METRIC, TAIL_STATS)

    scalar_lines = scalar.splitlines()
    cvar5_lines = cvar5.splitlines()
    assert len(cvar5_lines) == len(scalar_lines) + 1
    assert cvar5_lines[:len(scalar_lines)] == scalar_lines
    assert "CVaR 5%" in cvar5_lines[-1]

    assert block_fields("scalar_cvar5") == block_fields("scalar") + ["cvar_05"]


def test_scalar_block_adds_nothing_beyond_header() -> None:
    """The scalar arm adds no tail content beyond the shared scalar header."""
    scalar = build_block("scalar", METRIC, None)
    assert len(scalar.splitlines()) == 1
    assert "CVaR" not in scalar
    assert "tail" not in scalar.lower()
    assert block_fields("scalar") == ["scalar_metric"]


def test_serialization_is_deterministic() -> None:
    """Same (arm, scalar_metric, tail_stats) yields byte-identical output."""
    for arm in ARMS:
        a = build_block(arm, METRIC, TAIL_STATS)
        b = build_block(arm, METRIC, TAIL_STATS)
        assert a == b


def test_distributional_block_flags_cvar1_high_variance() -> None:
    """The rendered distributional block flags CVaR-1% as high-variance (B-7)."""
    dist = build_block("distributional", METRIC, TAIL_STATS)
    assert "CVaR 1%" in dist
    assert "high-variance" in dist.lower()


def test_block_fields_consistent_with_rendered_block() -> None:
    """block_fields length matches the rendered field/line layout."""
    # distributional: header + intro + 6 field lines = fields + 1 intro line.
    dist = build_block("distributional", METRIC, TAIL_STATS)
    # number of content lines (header + field lines) excluding intro == len(fields).
    assert len(block_fields("distributional")) == len(_DIST_CONTENT_LINES(dist))


def _DIST_CONTENT_LINES(block: str) -> list[str]:
    """Lines that correspond to a field (header + per-field lines), excluding intros."""
    return [
        ln for ln in block.splitlines()
        if "diagnostics" not in ln  # drop the intro line
    ]
