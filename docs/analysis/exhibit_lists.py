# -*- coding: utf-8 -*-
"""Regenerate the List of Tables and the List of Figures FROM THE CAPTIONS.

WHY DERIVED RATHER THAN MAINTAINED. Both lists were kept by hand and both went stale, in the way a
hand-kept index always does. The List of Tables carried Tables 5.4 and 5.5 after both were deleted.
The List of Figures went on naming Figures 5.1 and 5.2 after a block move had swept them out of the
Results chapter and into an appendix, and NOTHING else in the toolchain could see it: the build was
clean, the citations were clean, the word gate was clean and the scorecard read 28 of 28. What found
it was regenerating this list from the captions and noticing two numbers had no source.

So the lists are computed. A number that is not the caption of a real exhibit cannot appear in them,
and an exhibit whose caption exists cannot be missing from them.

WHAT THIS DOES NOT DO. It writes page number 0 for every row. `docs/analysis/exhibit_pages.py --write`
then reads the real pages out of the compiled PDF, and `--verify` checks them against a REBUILT one.
Nothing here asserts a page it has not measured.

THE ORDER OF OPERATIONS, and it matters:

    python docs/analysis/exhibit_lists.py     # titles, from the captions
    python scripts/build_paper.py             # so the pages exist to be read
    python docs/analysis/exhibit_pages.py --write
    python scripts/build_paper.py             # the stamp changed the source
    python docs/analysis/exhibit_pages.py --verify

⚠ CONTIGUITY IS ASSERTED, NOT REPORTED. A renumbering pass that runs twice leaves a hole and a
duplicate, which is exactly what happened on 2026-08-12. This module refuses to write a list whose
numbering has a gap, because a gap reads to a marker as a deleted exhibit.

Writes `paper/FRONT_MATTER.md`. Exit 1 if the numbering is not contiguous.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="backslashreplace")
    except (AttributeError, ValueError):  # pragma: no cover
        pass

REPO = Path(__file__).resolve().parents[2]
PAPER = REPO / "paper"
FRONT = PAPER / "FRONT_MATTER.md"

#: Assembly order, so the lists read in the order a reader meets the exhibits. Kept beside
#: `build_paper.ASSEMBLY` rather than imported, because that module is drift-fenced and this one is
#: not; a divergence shows up immediately as a missing exhibit rather than silently.
ORDER: tuple[str, ...] = (
    "FRONT_MATTER.md", "NOMENCLATURE.md", "CH1_introduction.md", "CH2_related_work.md",
    "tables/T_literature_positioning.md", "CH4_methods.md", "tables/T_arms_and_hypotheses.md",
    "tables/T_models_and_reward_canon.md", "tables/T_design_decisions.md",
    "tables/T_reproducibility_and_mechanism.md", "CH6_results.md",
    "tables/T_benchmark_allocators.md", "CH7_discussion_limitations_conclusion.md",
    "appendices/A_quality_control_record.md", "APPENDIX_B_limitations.md",
    "02_CHAPTER_theory.md", "CH5_prototype.md", "tables/T_scale_and_difficulty.md",
    "appendices/F_prompts_and_authored_code.md",
)
SECTION = {"1": "Chapter 1", "2": "Chapter 2", "3": "Chapter 3", "4": "Chapter 4", "5": "Chapter 5",
           "6": "Chapter 6", "7": "Chapter 7", "A": "Appendix A", "B": "Appendix B",
           "C": "Appendix C", "D": "Appendix D", "E": "Appendix E", "F": "Appendix F"}

#: A title longer than this wraps its column and pushes the page number onto a second line.
TITLE_MAX = 46

TABLE_CAP = re.compile(r"^\*\*Table ([A-F0-9]+\.\d+[a-z]?) — (.+?)\*\*", re.M)
FIGURE_CAP = re.compile(r"!\[\*\*Figure (\d+\.\d+)\*{0,2}\s*[—-]\s*(.+?)[.*]")
#: These two are listed with the figures rather than in lists of their own; there is one of each.
EXTRA = (("Listing 1.1", "The entire manipulation", "Chapter 1"),
         ("Algorithm 4.1", "The reward-design loop, as executed", "Chapter 4"))


def _clip(title: str) -> str:
    title = title.strip().rstrip(".,:")
    return title if len(title) <= TITLE_MAX else title[:TITLE_MAX].rsplit(" ", 1)[0]


def collect(pattern: re.Pattern[str], label: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    for name in ORDER:
        p = PAPER / name
        if not p.exists():
            continue
        text = re.sub(r"<!--.*?-->", "", p.read_text(encoding="utf-8"), flags=re.S)
        for num, title in pattern.findall(text):
            if num in seen:
                raise SystemExit(f"DUPLICATE {label} {num} in {name}: two captions claim one number")
            seen.add(num)
            rows.append((f"{label} {num}", _clip(title), SECTION.get(num.split(".")[0], "")))
    return rows


def assert_contiguous(rows: list[tuple[str, str, str]], label: str) -> None:
    """Refuse a list with a hole in it. A gap reads as a deleted exhibit."""
    by_chapter: dict[str, list[int]] = {}
    for num, _, _ in rows:
        head, _, tail = num.split(" ", 1)[1].partition(".")
        m = re.match(r"(\d+)", tail)
        if m:
            by_chapter.setdefault(head, []).append(int(m.group(1)))
    for head, nums in sorted(by_chapter.items()):
        missing = sorted(set(range(1, max(nums) + 1)) - set(nums))
        if missing:
            raise SystemExit(f"{label} {head}.x has a numbering gap at "
                             f"{', '.join(str(m) for m in missing)}; close it before regenerating")


def write_list(heading: str, rows: list[tuple[str, str, str]]) -> None:
    table = ("| # | Title | Section | Page |\n|---|---|---|---|\n"
             + "\n".join(f"| {n} | {t} | {s} | 0 |" for n, t, s in rows) + "\n")
    text = FRONT.read_text(encoding="utf-8")
    start = text.find(heading)
    if start < 0:
        raise SystemExit(f"{heading} not found in {FRONT}")
    ts = text.find("| # | Title", start)
    te = text.find("\n\n", ts)
    FRONT.write_text(text[:ts] + table + text[te + 1:], encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="report what would be written and change nothing")
    a = ap.parse_args(argv)

    tables = collect(TABLE_CAP, "Table")
    figures = collect(FIGURE_CAP, "Figure")
    assert_contiguous(tables, "Table")
    assert_contiguous(figures, "Figure")
    figures = figures + [EXTRA[0], EXTRA[1]]

    print(f"{len(tables)} tables, {len(figures)} figures and named exhibits")
    for n, t, s in tables + figures:
        print(f"   {n:<14} {s:<11} {t}")
    if a.check:
        print("\n--check: nothing written")
        return 0
    write_list("## List of Tables", tables)
    write_list("## List of Figures", figures)
    print(f"\nwritten to {FRONT}")
    print("NOW: build_paper -> exhibit_pages --write -> build_paper -> exhibit_pages --verify")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
