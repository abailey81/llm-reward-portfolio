"""Global deterministic seeding (FINAL_PLAN F.14, audit C-6).

Seeds every stochastic stack from a single run seed so a run reproduces (modulo documented
nondeterminism: some CUDA kernels; and LLM calls, which are replayed from the archive, not
regenerated — audit C-2). The seed is recorded in every run artifact (``src.io.results``).
"""
from __future__ import annotations

import os
import random

import numpy as np

__all__ = ["set_global_seed", "rng"]


def set_global_seed(seed: int) -> int:
    """Seed Python ``random``, NumPy, ``PYTHONHASHSEED`` and (if importable) torch + cuDNN.

    Returns the seed so callers can record it in the run artifact.
    """
    if not isinstance(seed, int):
        raise TypeError(f"seed must be int, got {type(seed)!r}")
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)  # legacy global RNG (SB3 / older libs read this)

    try:  # torch is optional in the analysis/test environment
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except ImportError:
        pass

    return seed


def rng(seed: int) -> np.random.Generator:
    """Return a fresh, isolated NumPy ``Generator`` (preferred over the legacy global RNG)."""
    return np.random.default_rng(seed)
