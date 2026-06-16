"""Provenance: content hashing, git state, and environment fingerprinting.

Every run artifact records *what produced it* so results replay rather than regenerate
(audit C-2) and so the frozen pre-registration can be content-hashed (Phase 1.E). Reward
source is hashed to deduplicate/trace candidates; the data pipeline hashes each gold artifact
(audit C-3).
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from importlib import metadata
from pathlib import Path
from typing import Any

__all__ = [
    "sha256_bytes",
    "sha256_text",
    "sha256_file",
    "sha256_obj",
    "git_commit",
    "env_fingerprint",
]

_TRACKED_PACKAGES = (
    "numpy",
    "scipy",
    "scikit-learn",
    "pandas",
    "gymnasium",
    "stable-baselines3",
    "sb3-contrib",
    "torch",
    "d3rlpy",
)


def sha256_bytes(data: bytes) -> str:
    """SHA-256 hex digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    """SHA-256 of UTF-8 text (used for reward source de-duplication / tracing)."""
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: str | Path, *, chunk: int = 1 << 20) -> str:
    """Streaming SHA-256 of a file (for gold-data checksums)."""
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def sha256_obj(obj: Any) -> str:
    """SHA-256 of a canonical JSON encoding (sorted keys) — for hashing configs/records."""
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
    return sha256_text(canonical)


def git_commit(short: bool = False) -> str | None:
    """Current git commit hash, or ``None`` if not in a git work-tree."""
    try:
        args = ["git", "rev-parse", "--short" if short else "HEAD"]
        out = subprocess.run(args, capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def env_fingerprint() -> dict[str, Any]:
    """A reproducibility fingerprint: Python, platform, key package versions, git commit."""
    versions: dict[str, str] = {}
    for pkg in _TRACKED_PACKAGES:
        try:
            versions[pkg] = metadata.version(pkg)
        except metadata.PackageNotFoundError:
            versions[pkg] = "not-installed"
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "git_commit": git_commit(),
        "packages": versions,
    }
