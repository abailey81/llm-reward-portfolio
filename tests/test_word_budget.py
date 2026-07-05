"""Tests for the UCL word-budget tool (scripts/word_budget.py) — the exclusion rules are the science."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import word_budget as wb  # noqa: E402


def test_plain_prose_counts_exactly() -> None:
    assert wb.count_words("Five plain prose words here.") == 5


def test_fenced_code_excluded() -> None:
    md = "Two words.\n```python\nx = 1\nfor i in range(10): print(i)\n```\nThree more words."
    assert wb.count_words(md) == 5


def test_display_and_inline_math_excluded() -> None:
    md = "Before math $$\\int_0^1 f(x) dx$$ after math. Inline $x^2 + y$ done."
    # counted: Before math after math Inline done = 6
    assert wb.count_words(md) == 6


def test_table_lines_excluded() -> None:
    md = "Intro line.\n| a | b |\n|---|---|\n| 1 | 2 |\nOutro line."
    assert wb.count_words(md) == 4


def test_citation_group_counts_as_one_word() -> None:
    md = "A claim [`key2021one`; `key2022two`] stands."
    # A claim CITE stands = 4
    assert wb.count_words(md) == 4


def test_inline_code_and_comments_excluded() -> None:
    md = "Use `np.mean` here. <!-- hidden note ten words long should never count at all -->Done."
    assert wb.count_words(md) == 3  # Use + here + Done


def test_headings_and_blockquotes_counted() -> None:
    md = "# Chapter One\n\n> **Theorem.** Words in theorem prose count."
    assert wb.count_words(md) == 8


def test_report_shape_and_status() -> None:
    r = wb.report(Path(wb.REPO) / "paper")
    assert set(r) == {"per_chapter", "total", "limit", "pass_ceiling", "status"}
    assert r["status"] in {"PASS", "WARN", "FAIL"}
    assert all(isinstance(v, int) for v in r["per_chapter"].values())
    assert r["total"] == sum(v for v in r["per_chapter"].values() if v >= 0)
