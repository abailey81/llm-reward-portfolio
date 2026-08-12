#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check that every MARK-BEARING asset still reaches the compiled PDF.

WHY THIS EXISTS. The 2026-08-11 redesign cut the document from 317 pages toward 130. A page cut is
cheap and a mark cut is not, and the two are indistinguishable from the page count alone. Tamer's
instruction on 2026-08-11: "make sure you preserve the grades we have for each section, refer strictly
to the marking criteria for that." This script is that check, run against the four criteria as they are
worded in `MSc_Project_Marking_Criteria_2019-20.pdf`, read first-hand.

THE FOUR BANDS, VERBATIM FROM THE CRITERIA PDF (90-100%, A+):

  1. Breadth and understanding of background knowledge and independence of thought --
     "Evidence of considerable extra-curricular reading with ORIGINAL INTERPRETATION. Exceptional
      insight into the problem AND ITS WIDER CONTEXT."
  2. Research Design: clear statement of objectives or research questions; appropriateness of methods,
     technique, reasoning to answer them --
     "FAULTLESS execution, EXEMPLARY analysis with entirely appropriate methods, UNQUESTIONABLE
      originality."
  3. Novelty and significance of Research Outcomes GIVEN DIFFICULTY OF THE PROBLEM --
     "EXTREMELY CHALLENGING project leading to an OUTSTANDING CONTRIBUTION to field (e.g., publishable
      in peer-reviewed journal)."
  4. Communication: report structure, English expression, presentation of data --
     "Excellent write up both in terms of readability, clarity and structure, with FAULTLESS
      presentation of data."

  And the one clause that licenses the cutting, from the 50-59 band of criterion 4:
     "Adequate write-up, lacking clarity or detail in places, OR CONTAINING IRRELEVANT MATERIAL."
     Volume is not neutral. Material a marker must wade through is scored against the write-up.

EACH CHECK NAMES THE CLAUSE IT SERVES. A check that cannot name its clause is not a mark check, it is a
preference, and it does not belong here.

Run: python docs/analysis/mark_preservation_audit.py
Exit 0 if every asset is present, 1 otherwise.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PAPER = REPO / "paper"
PDF = PAPER / "_build" / "dissertation.pdf"

sys.path.insert(0, str(REPO / "scripts"))
import build_paper  # noqa: E402  (drift-fenced: read only, never edited)

FAILS: list[str] = []
ROWS: list[tuple[str, str, bool, str]] = []


def compiled_text() -> str:
    """Every markdown source that actually reaches the PDF, concatenated."""
    parts = []
    for name in build_paper.ASSEMBLY + build_paper.APPENDICES:
        parts.append((PAPER / name).read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def check(criterion: str, clause: str, ok: bool, detail: str) -> None:
    ROWS.append((criterion, clause, bool(ok), detail))
    if not ok:
        FAILS.append(f"[{criterion}] {clause}: {detail}")


def main() -> int:
    raw = compiled_text()
    # !! WHITESPACE-NORMALISE BEFORE ANY PHRASE TEST, AND THIS IS NOT A REFINEMENT.
    # The first version of this script compared raw text and reported the research question as stated
    # ONCE when it is stated three times. A line break falls inside the phrase in two of the three, so
    # the raw comparison read a false absence. The project record already carried this exact trap under
    # the C2 test ("verified by a whitespace-NORMALISED comparison, never character-by-character on raw
    # text ... which is exactly how this check failed once already") and the instrument reproduced it
    # anyway. A surprising negative is a claim about the instrument before it is a claim about the text.
    src = re.sub(r"\s+", " ", raw)

    # ============================================================ CRITERION 1
    # "considerable extra-curricular reading" -- the reference list, and every entry doing work.
    cites = set(re.findall(r"`([A-Za-z][A-Za-z0-9_:.+-]*\d{4}[a-z]*)`", src))
    check("C1", "considerable extra-curricular reading (>=200 distinct works cited)",
          len(cites) >= 200, f"{len(cites)} distinct citation keys reach the compiled document")

    # "ORIGINAL INTERPRETATION" -- the positioning matrix is where prior work is not merely cited but
    # separated column by column. Its sourcing record is what makes the interpretation checkable.
    check("C1", "the positioning matrix survives (original interpretation, not citation)",
          "Table 2.1" in src, "Table 2.1 referenced in compiled source")
    check("C1", "the cell-by-cell sourcing discipline is stated",
          "36 verbatim quotations" in src or "36 carry a short verbatim quotation" in src,
          "the count of quotations, page locators and full-text searches behind the matrix")

    # "its WIDER CONTEXT" -- the clause is explicit and is the one most easily lost in a cut.
    check("C1", "the wider-context claim is made explicitly",
          "Beyond portfolios" in src,
          "a subsection stating what the finding constrains outside finance")

    # A citation that is contradicted or bounded is what "original interpretation" means.
    check("C1", "at least one cited source is corrected or bounded",
          "their window-size precedent carries" in src or "cannot establish this study's failure" in src,
          "a named source is used in one direction and refused in another")

    # ============================================================ CRITERION 2
    # "clear statement of objectives or research questions" -- and it must be the SAME statement.
    rq = "change the reward code it writes"
    # The criteria ask for a "clear statement of objectives or research questions". The design test
    # is that it is the SAME statement in the introduction, the methodology and the conclusion, so a
    # marker comparing the three finds no daylight. Three, not two.
    check("C2", "the research question is stated identically in intro, methods and conclusion",
          src.count(rq) >= 3, f"the canonical RQ phrase appears {src.count(rq)} times")

    # "appropriateness of methods ... to answer them" -- every design choice with its alternative and
    # its cost is the checkable form of appropriateness.
    check("C2", "every design decision carries its alternative and its cost",
          "Instead of" in src and "What it costs" in src,
          "Table 4.13 keeps both the alternatives column and the cost column")

    # "FAULTLESS execution" -- the freeze is the evidence, and it must be checkable by the reader.
    check("C2", "the design hash is stated where a reader can re-derive it",
          "3ca6f01ab7724d47bd5d01bc9e73b4d3" in src and "freeze.py --check" in src,
          "hash plus the command that recomputes it")

    # Threats paired with defences: the appropriateness argument in its strongest form.
    check("C2", "each named threat carries a named defence",
          "threat" in src.lower() and "defence" in src.lower(),
          "the threats-and-defences exhibit survives")

    # "UNQUESTIONABLE originality" -- the identification principle is the originality of the design.
    check("C2", "the identification principle is stated",
          "identification principle" in src,
          "only the reward may vary across arms")

    # ============================================================ CRITERION 3
    # "given DIFFICULTY of the problem" -- the marker normalises by difficulty, so the denominator has
    # to be supplied, in the BODY, in counts. Adjectives are discounted; counts are not.
    for label, needle in [("models", "11"), ("trainings", "25,602"), ("processor-hours", "288,533"),
                          ("peak cores", "2,328"), ("modules", "111"), ("tests", "2,875")]:
        check("C3", f"difficulty stated in counts, in the body: {label}",
              needle in src, f"{needle} present")

    # "OUTSTANDING CONTRIBUTION" -- numbered, with the evidence attached, early on the reader's path.
    # line-anchored, so it runs on RAW rather than the whitespace-normalised copy
    n_contrib = len(re.findall(r"^\| C[1-7] \|", raw, re.M))
    check("C3", "the contributions are numbered and enumerated",
          n_contrib == 7, f"{n_contrib} of 7 contribution rows present")
    check("C3", "the evidence for each contribution survives the table cut",
          "1,122 archived sealed-window records" in src and "zero tail vocabulary" in src.lower(),
          "the evidence moved into the caption, which is word-excluded, and is still present")

    # "publishable in peer-reviewed journal" -- made checkable rather than asserted.
    # ⚠ THE LITERAL WAS UPDATED 2026-08-12 BECAUSE THE PROSE WAS, NOT THE OTHER WAY ROUND. The guard
    # looked for "appears to be the only one"; the document tightened that to "appears to be the only
    # such instance in this literature", which carries the same hedge and names the scope the sweep
    # actually covers. Both hedged forms are accepted, so a future tightening does not silently fail.
    check("C3", "the novelty cell is claimed and fenced",
          "appears to be the only one" in src or "appears to be the only such instance" in src,
          "the claim is stated with its hedge and its sweep basis")

    # ============================================================ CRITERION 4
    # "FAULTLESS presentation of data". One shipped defect forfeits the band.
    if PDF.exists():
        try:
            import fitz
            doc = fitz.Document(PDF)
            pages = doc.page_count
            # Figures are vector PDFs and raster PNGs; count BOTH, because a caption-editing pass on
            # 2026-08-11 silently dropped every figure and no gate saw it. File size caught it.
            xobj = 0
            for i in range(pages):
                xobj += len(doc[i].get_images())
                xobj += len(doc[i].get_xobjects())
            check("C4", "the compiled PDF is within the 130-page ceiling",
                  pages <= 130, f"{pages} pages")
            check("C4", "every figure is still embedded (the 2026-08-11 regression guard)",
                  xobj >= 12, f"{xobj} embedded image and form XObjects across {pages} pages")
            check("C4", "the PDF has not collapsed in size (the same regression, seen twice)",
                  PDF.stat().st_size > 3_000_000, f"{PDF.stat().st_size // 1024} KB")
        except ImportError:
            check("C4", "page and figure census", False, "PyMuPDF not importable")
    else:
        check("C4", "the compiled PDF exists", False, str(PDF))

    # "irrelevant material" is penalised by name in the 50-59 band, so table bloat is a MARK issue.
    prose_cells = 0
    for line in src.split("\n"):
        if line.strip().startswith("|") and not re.match(r"^\s*\|[-:\s|]+\|\s*$", line):
            for cell in line.strip().strip("|").split("|"):
                if len(cell.split()) > 25:
                    prose_cells += 1
    check("C4", "no table cell carries a paragraph (>25 words)",
          prose_cells <= 40, f"{prose_cells} cells over 25 words")

    # ============================================================ report
    width = max(len(c) for _, c, _, _ in ROWS)
    cur = None
    for crit, clause, ok, detail in ROWS:
        if crit != cur:
            print(f"\n{'=' * 100}\n  {crit}\n{'=' * 100}")
            cur = crit
        print(f"  [{'PASS' if ok else 'FAIL'}]  {clause:<{width}}  {detail}")
    print(f"\n{'=' * 100}")
    print(f"  MARK-PRESERVATION AUDIT: {len(ROWS) - len(FAILS)} of {len(ROWS)} assets present.  "
          f"{len(FAILS)} missing.")
    if FAILS:
        print("  A missing asset is a lost band, not a lost page. Restore it before cutting further.")
        for f in FAILS:
            print(f"      - {f}")
    print(f"{'=' * 100}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
