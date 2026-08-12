"""Stamp real page numbers into the List of Figures and the List of Tables, from the compiled PDF.

⛔ THE DEFECT THIS CORRECTS. Both lists gave locations by SECTION rather than by page, under a stated
policy: *"Locations are given by section rather than by page: this document is compiled."* An
adversarial re-mark rejected that reasoning in one line, and it was right: *"For a fixed, submitted
302-page PDF this is not a rationale, it is a list that cannot be used to find anything."* A reader
holding the submitted artefact has page numbers in front of them and no way to use a section pointer
without first hunting the section.

⚠ WHY THE NUMBERS ARE GENERATED RATHER THAN TYPED. A hand-typed page number is correct exactly once.
Every rebuild moves the pagination, and this document is still being edited while a live campaign
fills its numbers, so a typed list would be stale within the day. That is the same failure that put a
thirty-seed abstract in front of a hundred-seed study. So the numbers are READ FROM THE ARTEFACT and
re-stamped on demand, and the list carries the date it was stamped.

HOW IT MATCHES. Each exhibit is located by searching the rendered text for its caption label
("Figure 5.1", "Table 5.9") in the position a caption occupies rather than anywhere it is mentioned,
which is why the match requires the label to be followed by a dash or the caption's own opening
words. An in-prose cross-reference such as "as Figure 5.3 shows" is deliberately NOT matched, because
the list must point at the exhibit and not at a sentence discussing it.

================================================================================================
⛔ THREE DEFECTS FOUND BY AN ADVERSARIAL RE-MARK ON 2026-08-10, WHICH BETWEEN THEM MADE ROUGHLY
FORTY-FOUR OF FIFTY-THREE ENTRIES WRONG WHILE THIS SCRIPT REPORTED SUCCESS. Each is recorded with
its cause, because "the list is generated" was being used as evidence that the list was right.

 1. THE CONTENTS PAGE WAS BEING MATCHED INSTEAD OF THE CAPTION. The bare-numbered specification
    tables are markdown HEADINGS ("### Table 6 — Nine published allocators"), so LaTeX puts them in
    the table of contents, dash and all. The table of contents comes first in the document, and this
    script took the FIRST match, so twelve of the thirteen bare-numbered tables pointed into the
    contents pages rather than at the exhibit. The chapter-numbered exhibits are bold paragraphs
    rather than headings, never reach the contents, and were therefore unaffected — which is exactly
    why the defect looked like a small numbering quirk instead of a systematic error.
    ⇒ FIX: index pages are identified STRUCTURALLY and excluded before any match is considered.

 2. TWO ROWS WERE INVISIBLE, AGAIN. The design-decision table and the Appendix E scale table are
    listed by TITLE because they carry no number, so neither the row pattern nor the "did I miss a
    row" pattern matched them, and both shipped with an empty Page cell while the script printed
    "0 not found". That is the third time a row has been dropped silently here.
    ⇒ FIX: the lists are now parsed by SECTION rather than by a label pattern. Every table row inside
    "List of Figures" or "List of Tables" that is not a header or a separator MUST resolve, and a row
    that does not is reported and blocks the write. A row is located by its label where it has one
    and by its title text where it does not.

 3. THE STAMP WAS NEVER RE-VERIFIED AGAINST THE BUILD IT SHIPPED WITH. Every chapter-numbered
    exhibit from Chapter 3 onward was off by exactly one page, because the numbers were stamped from
    a build one page shorter and the document then grew. Stamping is not idempotent in one pass:
    writing the numbers changes the front matter, which can change the pagination that produced
    them.
    ⇒ FIX: `--verify` re-reads the CURRENT PDF and fails loudly on any row whose stamped page is not
    where the exhibit actually renders. Run build → --write → build → --verify, and repeat until
    --verify is clean. A stamp that has not been verified against the shipped PDF is not evidence.

 4. ⛔ A FOURTH, FOUND 2026-08-10, AND IT IS THE ONE THIS SCRIPT'S OWN PARAGRAPH INVITED. The note
    beside the List of Figures boasts that this script "re-checks every stamped number against that
    same PDF under --verify, so a number carried over from an earlier build fails loudly instead of
    shipping." It checked the PAGE and never the TITLE. Directly above that sentence, the List of
    Figures gave Figure 5.7 the title "Capability tier against stability, the panel's clearest
    structural regularity" while the printed caption read "Seed-to-seed instability by model,
    ordered" — and Appendix G.27 spends a section disowning exactly the claim the front matter was
    asserting. A title carried over from an earlier build shipped, under a paragraph promising it
    could not. Twelve further rows of the List of Tables were paraphrases, and one was listed under
    a superseded name.
    ⇒ FIX: `--verify` now also compares the LISTED TITLE against the PRINTED CAPTION, and `--titles`
    prints the printed caption for every row so a list can be rebuilt from the artefact rather than
    from memory. The test is that the listed title must be a PREFIX of the caption once both are
    reduced to lowercase alphanumerics: a list entry may stop early, because captions carry a
    "What to conclude" clause a list has no room for, but it may not say something the page does
    not. Reduction to alphanumerics is what makes the comparison survive the typesetter — the
    rendered caption carries LaTeX's own hyphenation ("mo- tivation"), en dashes, ligatures and
    line breaks, none of which a source title has, and none of which change what the title SAYS.

⚠ LIGATURES. PyMuPDF returns what the font set, so "difficulty" comes back as "di<ffi>culty" with a
single ligature glyph and a literal search for the word fails. Page text is normalised before any
matching. This was found by a title search that silently returned nothing.
================================================================================================

Usage:
    python docs/analysis/exhibit_pages.py            # report the mapping, change nothing
    python docs/analysis/exhibit_pages.py --write    # stamp it into paper/FRONT_MATTER.md
    python docs/analysis/exhibit_pages.py --verify   # fail if a stamped page OR title is stale
    python docs/analysis/exhibit_pages.py --titles   # print each exhibit's PRINTED caption
"""
from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PDF = REPO / "paper" / "_build" / "dissertation.pdf"
FM = REPO / "paper" / "FRONT_MATTER.md"

#: The two front-matter sections whose rows carry a Page column. The List of Listings deliberately
#: does not: its three entries are a code listing, an algorithm and a whole appendix, and only the
#: last of those is an exhibit a page number would help a reader find.
#: ⛔ THE LIST OF LISTINGS USED TO BE EXCLUDED HERE, on the stated ground that "only the last of
#: its three entries is an exhibit a page number would help a reader find". That reasoning was
#: backwards. A reader holding a 341-page PDF who wants Listing 1.1 -- the exhibit that prints the
#: entire manipulation -- cannot reach it from a list that gives only a section number, and
#: Listing 1.1 and Algorithm 4.1 are exactly the two entries a reader is most likely to want.
#: All three lists are now stamped.
#: ⚠ MATCHED AS A PREFIX, NOT AS AN EXACT STRING, and that is a defect this file has already had.
#: The heading was renamed "List of Listings and Algorithms" on 2026-08-10 (Algorithm 4.1 was filed
#: under a list naming only listings) and the exact-match test silently stopped yielding those two
#: rows: the run reported "61 located, 0 unresolved" and looked clean, because a row that is never
#: yielded cannot be unresolved. A count is printed below for exactly this reason -- compare it
#: against the number of rows in the three lists before believing a green report.
STAMPED_SECTION_PREFIXES = ("List of Figures", "List of Tables", "List of Listings")

#: A caption is the label followed by a dash, an en/em dash, or a colon. A prose mention
#: ("as Figure 5.3 shows") is followed by a word, so it does not match.
#: ⚠ THE NUMBER PART ACCEPTS A LETTER PREFIX (Table C.1, Table A.1) as well as a digit, and
#: the KIND part accepts Listing and Algorithm. Neither did until 2026-08-10, which is why
#: Table C.1 -- a real, captioned, cross-referenced exhibit -- could not be listed at all: a row
#: for it was unresolvable and this script refuses to write with a hole in the list. The
#: appendix-letter series runs A to H, so the class is bounded rather than [A-Z], to stop a
#: stray capitalised word matching.
#: ⚠ THIS BOUND IS A MAINTENANCE OBLIGATION, NOT A CONSTANT. It must be widened whenever an
#: appendix is added, and the failure is SILENT in the direction that matters: an exhibit whose
#: letter falls outside the class is not reported as an error, it simply never becomes an
#: exhibit, so it renders unnumbered and stays out of the List of Tables with nothing
#: complaining. That is exactly how Table C.1 went unlisted until 2026-08-10, and the class
#: moved G -> H on 2026-08-10 when Appendix H (the positioning-matrix sourcing table) was added.
APPENDIX_LETTERS = "A-H"
CAPTION = re.compile(
    rf"\b((?:Figure|Table|Listing|Algorithm)\s+(?:\d+|[{APPENDIX_LETTERS}])(?:\.\d+)?[a-z]?)\s*[-–—:]")
#: A row whose first cell is a numbered exhibit label.
LABELLED = re.compile(
    rf"^(?:Figure|Table|Listing|Algorithm)\s+(?:\d+|[{APPENDIX_LETTERS}])(?:\.\d+)?[a-z]?$")
#: A separator row: dashes and colons only.
SEPARATOR = re.compile(r"^[-: ]+$")
#: The repeated column header LaTeX prints at the top of every page of a long list.
#: ⚠ IT MUST BE MATCHED WHITESPACE-INSENSITIVELY. PyMuPDF returns each table cell on its own line, so
#: the header extracts as "#\nTitle\nSection\nPage" and a literal "# Title Section" never matches. With
#: the literal test the list BODY pages were excluded only by accident, because one of them happened to
#: carry the "List of Listings" heading. One page of growth in the front matter moved that heading and
#: the accident stopped holding, which is how the latent bug surfaced.
LIST_HEADER = re.compile(r"#\s+Title\s+Section")
#: The three front-matter list headings, matched on the whitespace-collapsed page.
LIST_TITLE = re.compile(r"List of (?:Figures|Tables|Listings)")
#: Four or more dot leaders in a row is the table of contents and nothing else in this document.
LEADERS = re.compile(r"\.\s?\.\s?\.\s?\.")

LIGATURES = {"ﬀ": "ff", "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl",
             "ﬅ": "st", "ﬆ": "st"}


def normalise(text: str) -> str:
    """Rendered text with ligature glyphs expanded, so a literal search behaves as a reader would."""
    for glyph, plain in LIGATURES.items():
        text = text.replace(glyph, plain)
    return text


def flat(text: str) -> str:
    """One-line form of a page, for tests that must not care where the typesetter broke a line.

    A table cell, a heading and a wrapped title all extract with newlines inside them, so any test
    written against the way a page READS must be run on this form rather than on the raw extraction.
    """
    return re.sub(r"\s+", " ", text)


def page_texts(pdf: Path) -> list[str]:
    import fitz

    doc = fitz.open(pdf)
    out = [normalise(doc[i].get_text()) for i in range(doc.page_count)]
    doc.close()
    return out


def index_pages(texts: list[str]) -> set[int]:
    """Zero-based pages that are the table of contents or one of the front-matter lists.

    ⚠ THESE MUST BE EXCLUDED BEFORE ANY MATCH IS TAKEN, and identified by STRUCTURE rather than by a
    remembered page range, because the front matter moves whenever the document does. Two signatures
    do it, and both are properties LaTeX produces rather than things this project writes: the table
    of contents is the only place with dot leaders, and the lists repeat their column header on every
    page they span.
    """
    return {i for i, t in enumerate(texts)
            if len(LEADERS.findall(t)) >= 10
            or LIST_HEADER.search(flat(t))
            or LIST_TITLE.search(flat(t))}


def candidates(texts: list[str], skip: set[int]) -> dict[str, list[int]]:
    """Every one-based page on which each exhibit's CAPTION appears, index pages removed."""
    out: dict[str, list[int]] = {}
    for i, text in enumerate(texts):
        if i in skip:
            continue
        for m in CAPTION.finditer(text):
            out.setdefault(re.sub(r"\s+", " ", m.group(1)), []).append(i + 1)
    return out


def title_candidates(texts: list[str], skip: set[int], title: str) -> list[int]:
    """Pages carrying an unnumbered exhibit's own title, index pages removed.

    The two exhibits without numbers are located this way: the design-decision table heading reads
    "Table: Design decisions - ..." and the Appendix E heading reads "Appendix E - Scale and
    difficulty of the executed system", so each row's first cell is a literal substring of its own
    heading and of nothing else in the document once the lists and the contents are out of the way.
    """
    return [i + 1 for i, t in enumerate(texts) if i not in skip and title in flat(t)]


#: A caption runs from its label to the first sentence-ending full stop that is NOT inside an
#: abbreviation, a decimal or a bracketed aside. Rather than model that, the caption is taken whole
#: and the LISTED title is required to be a prefix of it, which needs no sentence boundary at all.
CAPTION_TEXT = re.compile(
    rf"\b(?:Figure|Table|Listing|Algorithm)\s+(?:\d+|[{APPENDIX_LETTERS}])(?:\.\d+)?[a-z]?\s*[-–—:]\s*")

#: Everything a typesetter can change without changing what a title SAYS.
_ALNUM = re.compile(r"[^a-z0-9]+")


def key(text: str) -> str:
    """A title reduced to what it says: lowercase alphanumerics, nothing else.

    ⚠ THIS IS THE ONLY SAFE COMPARISON. The rendered caption carries LaTeX's own hyphenation
    ("the empirical mo- tivation"), en and em dashes, ligature glyphs, `\\allowbreak` seams and line
    breaks; the source title carries markdown emphasis, backticks and maths. Reducing both to
    alphanumerics removes every one of those without ever inventing a word: it DELETES separators
    rather than joining across them, so a hyphen-broken "mo- tivation" and an unbroken "motivation"
    reduce to the same key while no new token is fabricated in the output — the reduced form is used
    for comparison only and is never printed as prose.

    ⚠ ONE KNOWN LIMIT, and it fails in the SAFE direction. A title carrying maths would compare a
    source `$\\lambda$` against a rendered `λ`: the Greek glyph is not in `[a-z0-9]` and is dropped,
    while "lambda" survives on the source side, so the row would be reported as a mismatch it is not.
    No exhibit title currently carries maths. If one ever does, the failure is a false ALARM rather
    than a silent pass, which is the direction this check is allowed to be wrong in.
    """
    return _ALNUM.sub("", text.lower())


def printed_caption(texts: list[str], page: int, label: str) -> str:
    """The caption as the PDF renders it, from `label` onward, joined across the page break.

    The next page is appended because a caption that begins near the foot of a page continues on the
    following one, and a title compared against a truncated caption would fail for a reason that has
    nothing to do with the title.
    """
    body = flat(texts[page - 1])
    if page < len(texts):
        body += " " + flat(texts[page])
    hits = [m for m in CAPTION_TEXT.finditer(body)
            if re.sub(r"\s+", " ", m.group(0)).strip().rstrip("-–—:").strip() == label]
    if not hits:
        return ""
    return body[hits[0].end():]


def rows(lines: list[str]):
    """Yield (line index, cells) for every data row of the two stamped lists.

    Parsing by SECTION rather than by a label pattern is what makes an unrecognised row impossible to
    miss: anything inside these lists that is not a header or a separator is a row this script is
    responsible for, whether or not it looks like one. The section heading itself is matched by
    PREFIX, because renaming one of them once removed two rows from the script's attention without
    removing them from the document.
    """
    section = ""
    for idx, line in enumerate(lines):
        if line.startswith("#"):
            section = line.lstrip("#").strip()
        if not section.startswith(STAMPED_SECTION_PREFIXES) or not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or cells[0] in ("#", "") or SEPARATOR.match(cells[0]):
            continue
        yield idx, cells


def resolve(lines: list[str], texts: list[str]) -> tuple[dict[int, tuple[list[str], int]], list[str]]:
    """Map each list row to its page. Returns (row index -> (cells, page)), and the failures."""
    skip = index_pages(texts)
    caps = candidates(texts, skip)
    found: dict[int, tuple[list[str], int]] = {}
    problems: list[str] = []
    for idx, cells in rows(lines):
        label = cells[0]
        hits = caps.get(label, []) if LABELLED.match(label) else title_candidates(texts, skip, label)
        if not hits:
            kind = "caption" if LABELLED.match(label) else "title"
            problems.append(f"line {idx+1}: {label!r} has no {kind} match outside the contents "
                            f"and the front-matter lists")
            continue
        found[idx] = (cells, hits[0])
        if len(hits) > 1:
            print(f"  {label:20s} -> p.{hits[0]}   (also on {hits[1:]}; first is taken)")
        else:
            print(f"  {label:20s} -> p.{hits[0]}")
    return found, problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="stamp the numbers into FRONT_MATTER.md")
    ap.add_argument("--verify", action="store_true",
                    help="fail if any stamped page, or any listed title, is not what the PDF renders")
    ap.add_argument("--titles", action="store_true",
                    help="print each row's PRINTED caption, so a list can be rebuilt from the artefact")
    a = ap.parse_args()

    if not PDF.is_file():
        print(f"no compiled PDF at {PDF}; run scripts/build_paper.py first")
        return 1
    texts = page_texts(PDF)
    skip = index_pages(texts)
    if not skip:
        print("  REFUSING TO PROCEED: no contents or list pages were identified, so the matcher")
        print("  cannot exclude them and would point every bare-numbered table at the contents.")
        return 1
    print(f"  contents / list pages excluded from matching: "
          f"{sorted(p + 1 for p in skip)}")
    print()

    lines = io.open(FM, encoding="utf-8").read().split("\n")
    found, problems = resolve(lines, texts)

    print()
    print(f"  {len(found)} located, {len(problems)} unresolved")
    for p in problems:
        print(f"  UNRESOLVED  {p}")

    # ⚠ THE OTHER DIRECTION, and it is the one that has failed three times. Everything above asks
    # "does each LISTED row exist in the PDF". An exhibit that is PRINTED but listed nowhere passes
    # every one of those checks by never being asked about — which is exactly how Table C.1, the two
    # unnumbered tables and the whole of Chapter 5's figures each went missing in turn. So the
    # printed captions are enumerated independently and differenced against the lists.
    listed = {cells[0] for _, cells in rows(lines)}
    printed = candidates(texts, skip)
    unlisted = sorted(set(printed) - listed)
    if unlisted:
        print()
        print(f"  UNLISTED: {len(unlisted)} exhibit(s) print a caption but appear in no list:")
        for label in unlisted:
            print(f"      - {label} (p.{printed[label][0]})")
        problems.append(f"{len(unlisted)} printed exhibit(s) are in no list")

    if a.titles:
        print()
        print("  PRINTED CAPTIONS, read from the compiled PDF. Rebuild the lists from these.")
        for idx, (cells, pg) in sorted(found.items()):
            cap = printed_caption(texts, pg, cells[0])
            print(f"\n  {cells[0]}  (p.{pg})")
            print(f"      listed : {cells[1] if len(cells) > 1 else ''}")
            print(f"      printed: {cap[:400] if cap else '<<caption not located on that page>>'}")
        return 0

    if a.verify:
        stale, mistitled = [], []
        for idx, (cells, pg) in found.items():
            was = cells[3] if len(cells) > 3 else ""
            if was.strip() != str(pg):
                stale.append(f"{cells[0]}: list says {was.strip() or '(blank)'}, renders on p.{pg}")
            listed = cells[1] if len(cells) > 1 else ""
            cap = printed_caption(texts, pg, cells[0])
            # ⚠ THE HOLE A PREFIX TEST HAS, CLOSED EXPLICITLY. The empty string is a prefix of
            # everything, so a row that lost its title would PASS the comparison below and ship
            # silently — which is the same shape as the empty-Page-cell defect this file already
            # records. An absent title is therefore its own failure, checked before the prefix test.
            if not key(listed):
                mistitled.append(f"{cells[0]}: the list row carries no title at all")
            elif not cap:
                mistitled.append(f"{cells[0]}: no caption located on p.{pg} to check the title against")
            elif not key(cap).startswith(key(listed)):
                mistitled.append(f"{cells[0]}:\n          listed : {listed}\n"
                                 f"          printed: {cap[:160]}")
        print()
        if stale or mistitled or problems:
            if stale:
                print(f"  STALE PAGE: {len(stale)} row(s) do not match the compiled PDF.")
                for s in stale:
                    print(f"      - {s}")
            if mistitled:
                print(f"  STALE TITLE: {len(mistitled)} row(s) do not open the caption they point at.")
                for m in mistitled:
                    print(f"      - {m}")
                print("      A listed title may STOP EARLY (the caption carries a 'What to conclude'")
                print("      clause a list has no room for) but it may not say something else. Copy")
                print("      the printed caption; `--titles` prints all of them.")
            if stale:
                print("  Re-run with --write, rebuild, and verify again. Stamping is not idempotent in")
                print("  one pass, because writing the numbers can move the pagination that produced them.")
            return 1
        print("  VERIFIED: every listed page is the page the exhibit renders on in this build, and")
        print("  every listed title opens the caption that is printed there.")
        return 0

    if not a.write:
        print("  (report only; pass --write to stamp)")
        return 0 if not problems else 1
    if problems:
        print("  REFUSING TO WRITE while any row is unresolved. A list with a hole in it is worse")
        print("  than a list with no page numbers, because the hole looks like an omission.")
        return 1

    out_lines = list(lines)
    for idx, (cells, pg) in found.items():
        # ⚠ IDEMPOTENCE. On a SECOND run the row already carries a Page column, so the row is always
        # rebuilt from its first THREE fields and never appended to. Appending produced a
        # five-column row and silently corrupted the list the first time this was written.
        label, caption, sec = cells[0], cells[1] if len(cells) > 1 else "", cells[2] if len(cells) > 2 else ""
        out_lines[idx] = f"| {label} | {caption} | {sec} | {pg} |"
    io.open(FM, "w", encoding="utf-8").write("\n".join(out_lines))
    print(f"  stamped into {FM.relative_to(REPO)}")
    print("  NOW REBUILD AND RUN --verify. A stamp taken from the previous build is the defect this")
    print("  script exists to remove, and it has shipped once already.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
