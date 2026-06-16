"""Structured logging setup.

A single ``get_logger`` entry point so scripts and modules log consistently (run id, level,
timestamp). Campaign scripts call ``configure_logging`` once at start-up.
"""
from __future__ import annotations

import logging
import sys

__all__ = ["configure_logging", "get_logger"]

_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"
_configured = False


def configure_logging(level: int | str = logging.INFO) -> None:
    """Configure root logging once (idempotent). Call at script start-up."""
    global _configured
    if _configured:
        logging.getLogger().setLevel(level)
        return
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(logging.Formatter(_FORMAT, datefmt=_DATEFMT))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a module logger, configuring logging on first use."""
    if not _configured:
        configure_logging()
    return logging.getLogger(name)
