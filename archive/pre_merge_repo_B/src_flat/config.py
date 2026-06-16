"""Single sanctioned parameter-access path (ADR-001). A numeric literal in src/ that
exists in config/ is a bug; load it from here instead."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


@lru_cache(maxsize=None)
def load(name: str) -> dict:
    """Load config/<name>.yaml (cached). e.g. load('inference')."""
    path = CONFIG_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"no such config: {path}")
    with open(path) as f:
        return yaml.safe_load(f)


def get(dotted: str, default: Any = ...) -> Any:
    """get('inference.dsr.unannualised_inputs') -> True. Raises KeyError unless a
    default is supplied — silent fallbacks hide misconfiguration."""
    name, *keys = dotted.split(".")
    node: Any = load(name)
    for k in keys:
        if not isinstance(node, dict) or k not in node:
            if default is ...:
                raise KeyError(f"config path not found: {dotted}")
            return default
        node = node[k]
    return node
