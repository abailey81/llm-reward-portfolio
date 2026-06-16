"""Shared pytest fixtures.

These back the behaviour tests across the suite: a reproducible RNG, a small synthetic market
panel, closed-form-checkable return samples (normal, Student-t), an equal-Sharpe / equal-CVaR pair
for null-calibration tests, and an isolated results directory.
"""
from __future__ import annotations

import numpy as np
import pytest

from src.data.panel import Panel
from src.data.synthetic import make_synthetic_panel

SEED = 12345


@pytest.fixture
def seed() -> int:
    return SEED


@pytest.fixture
def rng() -> np.random.Generator:
    """A fresh, isolated NumPy Generator."""
    return np.random.default_rng(SEED)


@pytest.fixture
def synthetic_panel() -> Panel:
    """A small synthetic panel (fast) with heavy tails and volatility clustering."""
    return make_synthetic_panel(n_assets=8, n_days=600, seed=SEED)


@pytest.fixture
def normal_returns(rng: np.random.Generator) -> np.ndarray:
    """A large standard-normal sample for closed-form CVaR/quantile checks."""
    return rng.standard_normal(200_000)


@pytest.fixture
def heavy_tail_returns(rng: np.random.Generator) -> np.ndarray:
    """A heavy-tailed (Student-t, df=3) daily-return-scaled sample."""
    return 0.01 * rng.standard_t(3, size=50_000)


@pytest.fixture
def equal_sharpe_pair(rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Two iid return series drawn from the SAME distribution (true Sharpe difference = 0).

    Used to check that difference-test p-values are ~uniform under the null.
    """
    a = 0.0005 + 0.01 * rng.standard_normal(2_000)
    b = 0.0005 + 0.01 * rng.standard_normal(2_000)
    return a, b


@pytest.fixture
def results_dir(tmp_path):
    """An isolated results directory for IO round-trip tests."""
    d = tmp_path / "runs"
    d.mkdir()
    return d
