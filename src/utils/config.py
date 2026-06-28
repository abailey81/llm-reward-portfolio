"""Typed configuration access.

``config/*.yaml`` is the single source of truth (CLAUDE.md). This module loads those files into
attribute-accessible mappings, resolves the repo root robustly, and offers ``require`` for
fail-loud access to mandatory keys. Code reads config; it never hardcodes parameters.
"""
from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

import yaml

__all__ = ["repo_root", "config_dir", "load_config", "load_all", "DotDict", "cfg_get"]


class DotDict(dict):
    """A ``dict`` with attribute access and fail-loud ``require``.

    Nested dicts are wrapped on access so ``cfg.splits.train.start`` works.
    """

    def __getattr__(self, name: str) -> Any:
        try:
            value = self[name]
        except KeyError as exc:  # pragma: no cover - trivial
            raise AttributeError(name) from exc
        return DotDict(value) if isinstance(value, dict) else value

    def require(self, key: str) -> Any:
        """Return ``self[key]`` or raise a clear error naming the missing key."""
        if key not in self:
            raise KeyError(f"required config key '{key}' is missing (have: {sorted(self)})")
        value = self[key]
        if value is None:
            raise ValueError(f"config key '{key}' is null — set it before use")
        return DotDict(value) if isinstance(value, dict) else value


def repo_root() -> Path:
    """Return the repository root (the directory containing ``config/``)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "config").is_dir() and (parent / "pyproject.toml").is_file():
            return parent
    raise RuntimeError("could not locate repo root (no parent has both config/ and pyproject.toml)")


def config_dir() -> Path:
    """Return the ``config/`` directory."""
    return repo_root() / "config"


@functools.lru_cache(maxsize=None)
def load_config(name: str) -> DotDict:
    """Load ``config/<name>.yaml`` (``name`` may include or omit the ``.yaml`` suffix)."""
    stem = name[:-5] if name.endswith(".yaml") else name
    path = config_dir() / f"{stem}.yaml"
    if not path.is_file():
        available = sorted(p.stem for p in config_dir().glob("*.yaml"))
        raise FileNotFoundError(f"no config '{stem}.yaml' in {config_dir()}; available: {available}")
    with path.open() as fh:
        data = yaml.safe_load(fh) or {}
    return DotDict(data)


def load_all() -> DotDict:
    """Load every ``config/*.yaml`` keyed by stem (``environment``, ``algos``, ...)."""
    return DotDict({p.stem: load_config(p.stem) for p in sorted(config_dir().glob("*.yaml"))})


def cfg_get(cfg: Any, key: str, default: Any = None) -> Any:
    """Read ``key`` from a dict-like or attribute-like config, with a default.

    Centralizes the ``_cfg_get`` / ``_get`` helper that was copy-pasted across 6 modules
    (audit P1-1, 2026-06-19). Works for plain dicts, :class:`DotDict`, and any object
    exposing attributes; returns ``default`` for a ``None`` cfg or a missing key.
    """
    if cfg is None:
        return default
    if isinstance(cfg, dict):
        return cfg.get(key, default)
    return getattr(cfg, key, default)
