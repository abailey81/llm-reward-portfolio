"""The junction-safety lock — written because the unsafe version DESTROYED the data directory.

On 2026-07-27 `certify_commit` junctioned the real `data/` into a throwaway worktree and cleaned up
with `shutil.rmtree`. A Windows junction is not a symlink, rmtree walked through it, and the cleanup
deleted the REAL directory: 1,179 tracked files (restored from git) and ~1.2 GB of untracked data
including the gold panel, which is not in git. These tests make that unrepeatable.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from scripts.certify_commit import _is_reparse_point, unlink_reparse_points

pytestmark = pytest.mark.skipif(os.name != "nt", reason="junction semantics are Windows-specific")


def _junction(link: Path, target: Path) -> bool:
    r = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                       capture_output=True)
    return r.returncode == 0


def test_a_junction_is_recognised_even_though_it_is_not_a_symlink(tmp_path):
    """The root cause: Path.is_symlink() returns False for a junction, so the old guard missed it."""
    target = tmp_path / "real"
    target.mkdir()
    (target / "precious.txt").write_text("do not delete", encoding="utf-8")
    link = tmp_path / "link"
    if not _junction(link, target):
        pytest.skip("mklink unavailable")
    assert _is_reparse_point(link) is True
    assert link.is_symlink() is False          # exactly why the naive check failed


def test_severing_a_link_NEVER_touches_the_target(tmp_path):
    """os.rmdir on a junction removes the link only. This is the property the fix depends on."""
    target = tmp_path / "real"
    target.mkdir()
    (target / "precious.txt").write_text("survive", encoding="utf-8")
    holder = tmp_path / "holder"
    holder.mkdir()
    if not _junction(holder / "data", target):
        pytest.skip("mklink unavailable")

    removed = unlink_reparse_points(holder)
    assert removed and not (holder / "data").exists()
    assert (target / "precious.txt").read_text(encoding="utf-8") == "survive"


def test_after_severing_a_recursive_delete_cannot_reach_the_target(tmp_path):
    """The end-to-end guarantee: sever first, THEN delete, and the real data survives."""
    import shutil

    target = tmp_path / "real"
    target.mkdir()
    (target / "gold.parquet").write_bytes(b"expensive")
    holder = tmp_path / "holder"
    holder.mkdir()
    (holder / "code.py").write_text("x = 1", encoding="utf-8")
    if not _junction(holder / "data", target):
        pytest.skip("mklink unavailable")

    unlink_reparse_points(holder)              # the step whose absence caused the loss
    shutil.rmtree(holder, ignore_errors=True)
    assert not holder.exists()
    assert (target / "gold.parquet").read_bytes() == b"expensive"
