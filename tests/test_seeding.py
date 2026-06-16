"""Tests for global seeding (FINAL_PLAN F.14, audit C-6)."""
from __future__ import annotations

import numpy as np

from src.utils.seeding import rng, set_global_seed


def test_set_global_seed_returns_seed_and_seeds_numpy() -> None:
    """``set_global_seed`` returns the seed and makes the legacy global RNG reproducible."""
    assert set_global_seed(123) == 123
    a = np.random.random(5)
    set_global_seed(123)
    b = np.random.random(5)
    np.testing.assert_array_equal(a, b)


def test_set_global_seed_rejects_non_int() -> None:
    """Non-integer seeds fail loudly."""
    import pytest

    with pytest.raises(TypeError):
        set_global_seed(1.5)  # type: ignore[arg-type]


def test_rng_is_isolated_and_reproducible() -> None:
    """Two generators with the same seed produce identical streams; different seeds differ."""
    s1 = rng(7).standard_normal(1000)
    s2 = rng(7).standard_normal(1000)
    s3 = rng(8).standard_normal(1000)
    np.testing.assert_array_equal(s1, s2)
    assert not np.array_equal(s1, s3)


def test_global_seed_does_not_leak_into_isolated_generator() -> None:
    """An isolated ``rng`` stream is unaffected by interleaved global RNG use (no shared state)."""
    set_global_seed(0)
    expected = rng(42).standard_normal(100)
    set_global_seed(0)
    _ = np.random.random(50)  # perturb the global RNG
    got = rng(42).standard_normal(100)
    np.testing.assert_array_equal(expected, got)
