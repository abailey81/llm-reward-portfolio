# -*- coding: utf-8 -*-
"""Every cross-reference in the compiled document, checked against what is actually printed.

WHY THIS EXISTS, AND IT IS NOT HYPOTHETICAL. On 2026-08-12 a block move swept Figures 5.1 and 5.2 out
of the Results chapter and into the quality-control appendix. §5.2 went on saying "Figures 5.1 and 5.2
give the per-line contrast and its convergence" while both figures printed forty pages later under a
heading about execution defects. The build was clean. The citation gate was clean. The word gate was
clean. The scorecard was 28 of 28. Nothing in the toolchain could see it, because nothing in the
toolchain compared what the prose PROMISES against what the document CONTAINS.

The 95+ doctrine's own gate table records this: the cross-reference row reads "no committed script
exists", and notes that the one audit that ever ran was in a session scratchpad and is gone. This is
that script.

WHAT IT CHECKS, over the assembled markdown so it sees exactly what pandoc sees:

  1. DANGLING   a reference in prose to an exhibit that has no caption anywhere.
  2. ORPHAN     a captioned exhibit that no prose sentence ever refers to.
  3. DUPLICATE  two captions claiming the same number.
  4. GAPS       a numbering sequence with a hole in it, which reads as a deleted exhibit.
  5. SECTIONS   a reference to a section number that no heading defines.

⚠ ORPHANS ARE REPORTED, NOT FAILED. A figure may legitimately be referred to only from its own
caption in a chapter that introduces it graphically, and Okhrati's criterion is about untidy
cross-referencing rather than about a rule that every exhibit be named in a sentence. Dangling
references, duplicates and gaps are defects with no innocent reading, and those set the exit code.

Report-only in the sense that it edits nothing. Exit 1 on a real defect.
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from collections import defaultdict
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="backslashreplace")
    except (AttributeError, ValueError):  # pragma: no cover
        pass

REPO = Path(__file__).resolve().parents[2]
ASSEMBLED = REPO / "paper" / "_build" / "dissertation.md"

#: A caption declares an exhibit. Tables and listings open with a bold run at the start of a line;
#: figures open the alt text of an image include.
CAPTION = re.compile(
    r"(?:^|!\[)\*\*(Table|Figure|Listing|Algorithm)\s+([A-F0-9]+\.\d+[a-z]?)\*{0,2}\s*[—-]", re.M)
#: A reference names one in running prose. The negative lookahead keeps a caption from counting as a
#: reference to itself.
REFERENCE = re.compile(r"(?<!\*)\b(Table|Figure|Listing|Algorithm)s?\s+([A-F0-9]+\.\d+[a-z]?)"
                       r"(?:\s+and\s+([A-F0-9]+\.\d+[a-z]?))?")
HEADING = re.compile(r"(?m)^#{2,4}\s+([A-F0-9]+(?:\.\d+)+)\s")
SECTION_REF = re.compile(r"§\s?([A-F0-9]+(?:\.\d+)+[a-z]?)")


def audit(text: str) -> int:
    # ⚠ HTML COMMENTS DO NOT COMPILE, SO THEY ARE NOT CROSS-REFERENCES. This document carries long
    # provenance comments, several of which name the exhibit numbers a block used to have. Counting
    # those reported three dangling references that no reader can ever meet.
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    captions: dict[str, str] = {}
    dupes: list[str] = []
    for kind, num in CAPTION.findall(text):
        key = f"{kind} {num}"
        if key in captions:
            dupes.append(key)
        captions[key] = kind

    refs: dict[str, int] = defaultdict(int)
    for kind, a, b in REFERENCE.findall(text):
        refs[f"{kind} {a}"] += 1
        if b:
            refs[f"{kind} {b}"] += 1
    # a caption also matches REFERENCE; discount exactly one hit per caption
    for key in captions:
        if refs.get(key):
            refs[key] -= 1

    dangling = sorted(k for k, n in refs.items() if n > 0 and k not in captions)
    orphans = sorted(k for k in captions if refs.get(k, 0) <= 0)

    # numbering gaps, per kind and per chapter
    gaps: list[str] = []
    seq: dict[tuple[str, str], list[int]] = defaultdict(list)
    for key in captions:
        kind, num = key.split(" ", 1)
        head, _, tail = num.partition(".")
        m = re.match(r"(\d+)", tail)
        if m:
            seq[(kind, head)].append(int(m.group(1)))
    for (kind, head), nums in sorted(seq.items()):
        want = set(range(1, max(nums) + 1))
        missing = sorted(want - set(nums))
        if missing:
            gaps.append(f"{kind} {head}.x is missing {', '.join(str(m) for m in missing)}")

    headings = {h for h in HEADING.findall(text)}
    sec_dangling = sorted({s for s in SECTION_REF.findall(text)
                           if s not in headings and s.split(".")[0] not in {"A", "B", "C", "D", "E", "F"}})

    print(f"captions found      : {len(captions)}")
    print(f"prose references    : {sum(refs.values())}")
    print(f"\nDANGLING references (named in prose, no caption anywhere): {len(dangling)}")
    for k in dangling:
        print(f"   {k}")
    print(f"DUPLICATE numbers   : {len(dupes)}")
    for k in dupes:
        print(f"   {k}")
    print(f"NUMBERING GAPS      : {len(gaps)}")
    for g in gaps:
        print(f"   {g}")
    print(f"DANGLING section refs (body chapters only): {len(sec_dangling)}")
    for s in sec_dangling:
        print(f"   §{s}")
    print(f"\nORPHAN exhibits (captioned, never named in prose): {len(orphans)}  [reported, not failed]")
    for k in orphans:
        print(f"   {k}")

    bad = len(dangling) + len(dupes) + len(gaps) + len(sec_dangling)
    print("\n" + ("CROSS-REFERENCES CLEAN" if bad == 0 else f"{bad} CROSS-REFERENCE DEFECTS"))
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    if not ASSEMBLED.exists():
        print(f"{ASSEMBLED} absent; run scripts/build_paper.py first")
        return 2
    return audit(ASSEMBLED.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
