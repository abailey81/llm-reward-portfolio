"""Native-library preload that prevents a torch/pyarrow ABI segfault (verified 2026-06-20).

On this stack (torch 2.6 + pyarrow, Windows), importing ``pyarrow(.parquet)`` — which
``src.data.loaders.load_gold_panel`` uses to read the REAL gold parquet — AFTER torch has been imported
SEGFAULTS (SIGSEGV/exit 139): a first-loader-wins native-runtime conflict. Verified: torch-then-gold => crash,
gold-then-torch => OK, and pyarrow-then-torch-then-gold => OK. Every process that uses BOTH the real gold data
AND torch must therefore import pyarrow FIRST.

This matters precisely because the project trains ONLY on real survivorship-free gold data — there is no
synthetic fallback in a real run — so the gold load must be rock-solid. Call :func:`preload` at the very top
of each entry point (and the pool worker init) BEFORE any torch import.
"""

from __future__ import annotations


def preload() -> None:
    """Import pyarrow before torch is ever imported, avoiding the ABI segfault on real-gold parquet loads."""
    try:
        import pyarrow  # noqa: F401
        import pyarrow.parquet  # noqa: F401
    except Exception:  # pragma: no cover - pyarrow optional only in a torch-less minimal env
        pass
