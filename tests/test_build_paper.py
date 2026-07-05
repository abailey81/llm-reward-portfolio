"""Tests for the dissertation build pipeline's pure text transforms (scripts/build_paper.py).

The citation rewrite is load-bearing: a missed group renders as literal text in the submitted PDF
with NO warning, while a transformed key missing from refs.bib fails loud via citeproc — so the
transform must catch every real citation form used in the chapters (incl. the 18 forms the
first-compile audit found: multi-line groups, locator suffixes, prefix text) and must never touch
code or non-citation brackets.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import build_paper as bp  # noqa: E402


def test_simple_group() -> None:
    assert bp.rewrite_citations("A claim [`agarwal2021rliable`].") == "A claim [@agarwal2021rliable]."


def test_multi_key_group() -> None:
    out = bp.rewrite_citations("X [`du2017backtesting`; `bauer2025equal`].")
    assert out == "X [@du2017backtesting; @bauer2025equal]."


def test_group_wrapping_across_lines() -> None:
    md = "claim [`zhang2017deeper`;\n`fedus2020revisiting`] end."
    out = bp.rewrite_citations(md)
    assert "[@zhang2017deeper;\n@fedus2020revisiting]" in out


def test_locator_suffix() -> None:
    assert bp.rewrite_citations("scale [`haarnoja2018sac`, §5].") == "scale [@haarnoja2018sac, §5]."


def test_prefix_text_and_mixed_items() -> None:
    md = "[`chow2015risk`, Prop. 1; cf. robust MDPs `iyengar2005robust`; `nilim2005robust`]"
    out = bp.rewrite_citations(md)
    assert out == "[@chow2015risk, Prop. 1; cf. robust MDPs @iyengar2005robust; @nilim2005robust]"


def test_non_citation_brackets_untouched() -> None:
    # No 4-digit year in the backtick token -> not a citation.
    for md in ("run [`--gpu 3`] now", "use [`np.mean`] here", "a [markdown link](https://x) stays"):
        assert bp.rewrite_citations(md) == md


def test_fenced_code_passes_through_byte_intact() -> None:
    md = "prose [`ma2024eureka`]\n```python\nx = ledger[`key2021fake`]\n```\ntail [`sood2023deep`]"
    out = bp.rewrite_citations(md)
    assert "[@ma2024eureka]" in out and "[@sood2023deep]" in out
    assert "ledger[`key2021fake`]" in out  # inside the fence: untouched


def test_assemble_appends_references_section() -> None:
    md = bp.assemble(bp.REPO / "paper")
    assert "# References {.unnumbered}" in md and "::: {#refs}" in md
    # Chapters are separated by explicit page breaks.
    assert "\\newpage" in md
