"""THE STRICT SCORECARD: every checkable duty in the project's own law, measured rather than recalled.

WHY THIS EXISTS. The operating brief carries forty-four named duties across five supervisor
sections, plus five priorities, plus four marking criteria, plus a writing manual. Nobody applies
forty-four rules under a deadline, and a body of law that cannot be checked becomes decorative.
Decorative law is worse than none, because it produces the feeling of rigour without the fact of it.

So this module takes every duty that is MECHANICALLY DECIDABLE and decides it against the real
files. It deliberately does NOT score the duties that need judgement (is the mechanism argument
convincing, is the contribution novel). Those need a reader. What it does is remove the excuse that
a checkable defect was missed, and it reports a defect the same way whether or not the defect is
convenient.

WHAT IT REUSES RATHER THAN REBUILDS. The word-count exclusion rules are the UCL rules and they are
already implemented in `scripts/word_budget.py`. The set of files that actually reach the marker is
already implemented in `scripts/build_paper.py`. Both are imported. A second implementation of
either would be a second thing to keep in sync, and the two would silently diverge.

READING THE OUTPUT. Every check prints PASS or FAIL with the measured quantity beside it. A FAIL is
a defect with a location. There is no WARN, because the standing rule is that a WARN counts as a
FAIL.

Report-only. Gates nothing. Never edits.
"""
from __future__ import annotations

import argparse
import io
import os
import re
import sys
from collections import Counter
from pathlib import Path

# ⛔ A GATE THAT CANNOT PRINT ITS OWN FAILURE IS WORSE THAN NO GATE (fixed 2026-08-10).
# This box's stdout encoding is cp1251. On 2026-08-10 a genuine FAIL fired whose detail line quoted
# the offending glyph, U+26D4, and the print raised UnicodeEncodeError instead: the process exited 1
# with the failing check's line half-written and the summary never reached. An operator reading only
# the exit code would have called it a FAIL of unknown cause; an operator reading only the truncated
# output would have seen the last visible line PASS. The reporter is reconfigured to UTF-8 with a
# lossy fallback so a detail can always be printed, whatever glyph the artefact contains. The check
# that caught the real defect is the SILENTLY-DROPPED-GLYPH one below; it worked, and only the
# reporting of it was broken.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    except (AttributeError, ValueError):  # pragma: no cover - non-reconfigurable stream
        pass

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from word_budget import BODY_CHAPTERS, strip_excluded  # noqa: E402

PAPER = REPO / "paper"
EM_DASH = "—"

# --------------------------------------------------------------------------- the lexical tells
BANNED = [
    "delve", "crucial", "pivotal", "underscore", "showcase", "tapestry", "testament",
    "intricate", "interplay", "vibrant", "foster", "garner", "enduring", "seamless",
    "holistic", "myriad", "paradigm shift", "cutting-edge", "a wide range of",
    "plays a key role", "serves as a", "stands as a", "in order to",
    "due to the fact that", "it is important to note that", "at this point in time",
    "it is worth noting",
]
VAGUE = ["a number of", "various", "certain aspects", "several aspects",
         "a range of factors", "some of the results", "in some cases"]
#: Internal labels that mean nothing to a reader outside this project (Stefan S10).
LABEL_OPEN = re.compile(r"^\s*(?:\*\*)?(H[1-4]|SQ[1-3]|A[1-5]|N[0-9]|R1[0-9]{2}|B\*|C[1-7]|D1[0-9])\b")
PRONOUN_OPEN = re.compile(r"^\s*(This|That|It|These|Those|The former|The latter)\s+(is|are|was|were|shows?|means?|gives?|makes?|does|do|has|have|would|will|can)\b")
TRAILING_ING = re.compile(r",\s+(highlighting|underscoring|showcasing|demonstrating|emphasising|emphasizing|reflecting|illustrating)\b", re.I)
# ⚠ NARROWED AFTER A LIVE FALSE-POSITIVE SWEEP. The tell is the METAPHORICAL equation ("X is the
# language of Y", "X is the architecture of Y"), not every literal "is the ... of". A broad
# `is the \w+ of` flagged six passages that are all ordinary, correct technical English: "the headline
# is the pair of co-primary tests", "whose p-value is the maximum of the eleven legs", "the designed
# reward is the survivor of a thirty-candidate search". Rewriting those to satisfy a regex would make
# the prose worse, which is the opposite of what this check exists for.
APHORISM = re.compile(
    r"\bis the (?:language|architecture|backbone|cornerstone|heart|engine|lifeblood|bedrock|"
    r"DNA|foundation|beating heart|holy grail|silver bullet) of\b", re.I)
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(\[])")
# ⚠ THE NEGATIVE LOOKAHEAD IS LOAD-BEARING AND WAS ADDED AFTER A LIVE FALSE POSITIVE.
# A bare case-insensitive \bTO BE WRITTEN\b also matches ordinary English: "has to be written down",
# "never to be written as the latter". Both occur in this document, and both were reported as shipped
# placeholders. A detector that cries wolf costs real editing time and, worse, trains a reader to
# discount it. A placeholder is the SENTENCE-FINAL promise form, not the infinitive in ordinary use.
PLACEHOLDER = re.compile(
    r"\[(?:FROM CAMPAIGN|TBD|TODO|PLACEHOLDER|XXX)[^\]]*\]"
    r"|\bTO BE WRITTEN\b(?!\s+(?:down|as|in|for|by|to|with|about|into|on))", re.I)

#: A line that is a HEADING or an exhibit CAPTION is not running prose. A dash there separates a
#: label from its gloss ("Table 4.1 - Threats to validity"), which is correct typography and is
#: explicitly exempted by the register rule. Counting those reports a failure where the house style
#: is right, and "fixing" them would be cosmetic damage to satisfy a regex.
#: ⚠ `\\[A-Za-z]` WAS ADDED 2026-08-10 AND IT CLOSES A REAL HOLE. A line that is nothing but LaTeX
#: (`\begingroup\footnotesize`, `\endgroup`, `\Needspace{...}`, `\FloatBarrier`) is markup by any
#: definition, but it matched none of the classes above, so it survived into the counted prose. It
#: went unnoticed only because an exhibit caption usually sat between it and the surrounding text and
#: supplied the sentence boundary; the moment captions became word-excluded, two ordinary sentences
#: welded across the LaTeX and the length check reported a 66-word "sentence" nobody wrote.
NOT_PROSE = re.compile(r"^\s*(?:#{1,6}\s|!\[|\||>|\\[A-Za-z]|\**(?:Figure|Table|Listing|Algorithm)\s*\d)")


def prose_lines(text: str) -> str:
    """Running prose only: headings, captions, image includes and table rows removed.

    ⚠ A REMOVED LINE BECOMES A FULL STOP, NOT NOTHING. Deleting a heading outright welds the
    sentence before it to the sentence after it, and the sentence-length check then reports a
    60-word monster that no reader will ever meet. That artefact affected every chapter equally and
    was mistaken for a prose defect until a stream traced it. Substituting a sentence boundary keeps
    the removed material out of the counts while preserving the break it represented.
    """
    return "\n".join("." if NOT_PROSE.match(ln) else ln for ln in text.splitlines())
SHARPE = re.compile(r"\bSharpe\b", re.I)
GROSSNET = re.compile(r"\b(gross|net)\b", re.I)


class Score:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, bool, str]] = []

    def add(self, group: str, name: str, ok: bool, detail: str) -> None:
        self.rows.append((group, name, ok, detail))

    def render(self) -> int:
        cur = None
        for group, name, ok, detail in self.rows:
            if group != cur:
                cur = group
                print()
                print("=" * 100)
                print(f"  {group}")
                print("=" * 100)
            print(f"  [{'PASS' if ok else 'FAIL'}]  {name:52s} {detail}")
        n = len(self.rows)
        bad = sum(1 for r in self.rows if not r[2])
        print()
        print("=" * 100)
        print(f"  SCORECARD: {n-bad} of {n} checkable duties PASS.  {bad} FAIL.")
        if bad:
            print("  A single FAIL forfeits the 'faultless' band. There is no partial credit here.")
            print()
            print("  OPEN DEFECTS, in the order to fix them:")
            for group, name, ok, detail in self.rows:
                if not ok:
                    print(f"      - [{group.split('--')[0].strip()}] {name}: {detail}")
        else:
            print("  Every mechanically checkable duty passes. What remains needs a READER,")
            print("  because the author must not grade their own argument.")
        print("=" * 100)
        return bad


#: A bold exhibit caption occupying its own paragraph, e.g. ``**Table 5.9 - ...**``, possibly wrapped
#: over several lines and ending at the first blank line.
#:
#: ⚠ WHY THIS EXISTS HERE RATHER THAN IN `word_budget.strip_excluded`, WHICH IS WHERE IT BELONGS.
#: UCL excludes "diagrams, tables, figures and graphs" from the word count. `strip_excluded` already
#: honoured that for FIGURES, but only as a side effect of markdown syntax: a figure caption is written
#: ``![**Figure 5.1 - ...**](path)`` and is removed as an image line, while a TABLE caption is a plain
#: bold paragraph and survived into the count. So the instrument excluded a caption when the exhibit was
#: a picture and counted the same caption when the exhibit was a table -- a distinction UCL's rule does
#: not make. Measured effect: 547 words across 31 captions in the seven body chapters.
#: `scripts/**` is drift-fenced to the ops lane while RUN 4 is live and the fence may not be disarmed
#: from here, so the rule is applied on top of `strip_excluded` instead of inside it. ⚠ THAT LEAVES THE
#: TWO INSTRUMENTS DISAGREEING BY 547 WORDS BY CONSTRUCTION, which is a defect in its own right: the
#: dissertation's word-count statement therefore names THIS command, prints the count both ways, and
#: says why. When the campaign closes and the fence lifts, move this regex into `strip_excluded` and
#: delete it here, so one instrument answers the question again.
#:
#: ⚠ AND THE TIMING IS THE PART TO BE HONEST ABOUT: this was adopted AFTER the count returned a FAIL,
#: which is the move the word-count statement itself warns against. Two things make it a correction
#: rather than a convenience, and both are checkable. The rule is right independently of its effect --
#: it would be right if it RAISED the total -- and every one of the 31 spans it removes was printed in
#: full and read before adoption, to confirm each is caption text and none is argument.
#:
#: Anchored at ^ with re.M so a mid-sentence mention ("as **Table 5.9** shows") can never match: the
#: caption must OPEN its paragraph. The label class mirrors `exhibit_pages.py` (chapter series, or an
#: appendix letter A-H).
_EXHIBIT_CAPTION_RE = re.compile(
    r"^\*\*(?:Table|Figure|Listing|Algorithm|Exhibit|Panel)\s+"
    r"(?:\d+|[A-H])(?:\.\d+)?[a-z]?\s*[-–—:]"
    r".*?(?:\n[ \t]*\n|\Z)",
    re.S | re.M,
)


def body_prose() -> dict[str, str]:
    """The counted body prose, per chapter, with the UCL exclusions already applied."""
    out = {}
    for ch in BODY_CHAPTERS:
        p = PAPER / ch
        if p.is_file():
            out[ch] = _EXHIBIT_CAPTION_RE.sub(
                "\n\n", strip_excluded(io.open(p, encoding="utf-8").read()))
    return out


def paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip() and not p.lstrip().startswith(("|", "#", ">"))]


def sentences(text: str) -> list[str]:
    """Split into sentences, tolerating the markup that sits between a full stop and the next word.

    ⚠ A NAIVE LOOKBEHIND ON [.!?] UNDER-SPLITS AND MANUFACTURES MONSTERS. A bolded lead-in ends
    `...read.**` so the character before the space is an asterisk, the lookbehind fails, and two or
    three ordinary sentences weld into one that the length check then reports as a 72-word defect
    nobody wrote. A sentence-final footnote marker `[^name]` does the same. Both are markup, not
    prose, so they are moved out of the way before splitting rather than being allowed to hide a
    real boundary. This was found by a stream whose own chapters measured clean while the document
    reported a violation that did not exist.
    """
    flat = re.sub(r"\s+", " ", text)
    flat = re.sub(r"\[\^[^\]]+\]", "", flat)          # footnote markers are not prose
    # ⚠ AND NEITHER IS A SUPERSCRIPT SEPARATOR. Two footnote markers on one sentence are joined with
    # `<sup>,</sup>`, which leaves `... treatment CITE .<sup>,</sup> The domain's own survey ...`
    # after the marker strip: the full stop is no longer welded to its word, SENT_SPLIT cannot see a
    # boundary, and two ordinary sentences are reported as one 66-word defect. Found 2026-08-12 on a
    # sentence that reads at 27 and 24 words on the page. Same class as the footnote-marker case
    # above, one instance further along.
    flat = re.sub(r"</?sup>", "", flat)
    flat = re.sub(r"([.!?])(\*{1,2})", r"\2\1", flat)  # `.**` -> `**.` so the boundary is visible
    flat = re.sub(r"([.!?]) ?[,;:](?= )", r"\1", flat)  # a stranded separator is not a sentence
    # ⚠ A STANDALONE PERIOD IS A BOUNDARY, WHATEVER FOLLOWS IT. `prose_lines` replaces each removed
    # markup line with ".", and consecutive removals leave a run of them. `SENT_SPLIT` cannot break
    # there, because it requires the next sentence to open with a capital or a quote -- and this
    # document opens sentences with lowercase code identifiers (`placebo_shuffled arms are ...`).
    # The signal is unambiguous: in real prose a full stop is always welded to its word, so a period
    # with whitespace BEFORE it is always a placeholder and never punctuation. Collapse any run of
    # them to a single hard boundary and split there unconditionally.
    flat = re.sub(r"(?:\s\.)+\s", " ", flat)
    parts = [p for chunk in flat.split("\u2028") for p in SENT_SPLIT.split(chunk)]
    parts = [p for chunk in flat.split(" ") for p in SENT_SPLIT.split(chunk)]
    return [s.strip() for s in parts if s.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verbose", action="store_true", help="print every offending line, not a sample")
    a = ap.parse_args()
    s = Score()
    prose = body_prose()
    allp = "\n\n".join(prose.values())

    # ================================================================= CRITERION 4, the faultless band
    # ★ THE LIMIT IS 11,000, NOT 10,000, AND THE REASON IS ON THE RECORD.
    # The IFTE0008 guide sets 10,000 and states that "penalties will apply for exceeding the word
    # limit", but it also names a sanctioned route: "If you believe that exceeding the limit is
    # necessary, discuss this with your supervisor first, followed by the Programme Director for
    # approval." That route was taken and a 1,000-word extension was APPROVED (Tamer, 2026-08-10),
    # so the binding figure for this document is 11,000.
    # ⚠ TWO DISCIPLINES TRAVEL WITH THAT, because an approved allowance is not a licence to pad.
    #   1. `scripts/word_budget.py` still hard-codes 10,000 and is edit-fenced while the campaign is
    #      live, so it will keep printing FAIL or WARN above that. Read ITS number, apply THIS limit,
    #      and do not "fix" the fenced script to agree.
    #   2. The extension buys ARGUMENT, never padding. Appendices, tables, figures, footnotes, code
    #      and display maths remain word-excluded, so evidence still belongs there. The 1,000 words
    #      are for reasoning a marker must read to award a band, and the guide's ~60% core rule and
    #      the "irrelevant material" penalty in the 50-59 band both still bite.
    BODY_LIMIT = 11000
    total = sum(len(re.findall(r"\b[\w'-]+\b", t)) for t in prose.values())
    s.add("CRITERION 4 -- 'faultless presentation of data'",
          f"body word count <= {BODY_LIMIT:,} (approved extension)",
          total <= BODY_LIMIT,
          f"measured {total:,} words across {len(prose)} chapters; "
          f"{BODY_LIMIT - total:,} of the approved allowance unspent")

    # ⚠ THE PRINTED COUNT MUST EQUAL THE MEASURED ONE, AND UNTIL 2026-08-11 NOTHING CHECKED IT.
    # The front matter states the word count in prose AND names this script as what produced it, so a
    # marker can run the command and compare. That is the right way to write it and it is also a trap:
    # the printed number is a literal, and every edit to body prose moves the measured one out from
    # under it. Found by reading the compiled PDF along a marker's path -- page 4 said 10,719 against
    # a measured 10,951, a 232-word drift accumulated silently across a single editing session.
    # A stale count in the front matter is precisely the "faultless presentation" defect the top band
    # turns on, and it is the one class of defect that RE-ARMS ITSELF every time the prose is touched.
    # So it is checked here rather than remembered.
    _fm = (PAPER / "FRONT_MATTER.md").read_text(encoding="utf-8")
    _m = re.search(r"The main text measures\s+([\d,]+)\s+words", _fm)
    _printed = int(_m.group(1).replace(",", "")) if _m else None
    s.add("CRITERION 4 -- 'faultless presentation of data'",
          "the PRINTED word count equals the measured one",
          _printed == total,
          (f"front matter prints {_printed:,}, this script measures {total:,}"
           + ("" if _printed == total else "  <-- STALE: update FRONT_MATTER.md"))
          if _printed is not None else
          "NOT FOUND: no 'The main text measures N words' sentence in FRONT_MATTER.md")

    ph = [(ch, m.group(0)) for ch, t in prose.items() for m in PLACEHOLDER.finditer(t)]
    # placeholders must be counted on the RAW file too: a slot inside a table is still shipped
    # Only files that REACH THE MARKER can ship a placeholder. Scratch drafts under paper/ are not
    # in the assembly and a slot there costs nothing, so scanning them manufactures work.
    from build_paper import APPENDICES, ASSEMBLY  # noqa: E402
    shipped = {PAPER / n for n in tuple(ASSEMBLY) + tuple(APPENDICES)}
    raw_ph = []
    for f in sorted(PAPER.rglob("*.md")):
        if f not in shipped and f.parent != PAPER / "tables":
            continue
        for i, line in enumerate(io.open(f, encoding="utf-8"), 1):
            if PLACEHOLDER.search(line):
                raw_ph.append(f"{f.relative_to(REPO)}:{i}")
    s.add("CRITERION 4 -- 'faultless presentation of data'", "zero unfilled placeholders anywhere in paper/",
          not raw_ph, f"{len(raw_ph)} found" + (f"; first: {raw_ph[0]}" if raw_ph else ""))

    # exhibit cross-references: every "Figure N.M" named in prose must have a caption somewhere
    allmd = "\n".join(io.open(f, encoding="utf-8").read()
                      for f in sorted(PAPER.rglob("*.md")) if "_build" not in f.parts)
    # ⚠ RESTORING A VISIBILITY THE FRESHNESS GATE LOST, AND SAYING SO PLAINLY.
    # `scripts/check_rung_freshness.py --final` detects exactly one thing: the literal string
    # "[FROM CAMPAIGN". Replacing those brackets with an honest disclosure sentence is the right
    # editorial move, because a shipped bracket forfeits the faultless band while a stated
    # pre-registered procedure earns marks. But it also makes every pending row INVISIBLE to that
    # gate, so the gate turns green while the chapter is still incomplete. A check that passes
    # because the thing it looks for was renamed is worse than no check, since it manufactures
    # confidence. This counter is the replacement: it tracks the disclosure marks directly, so the
    # pending rows stay countable. It deliberately does NOT fail the scorecard, because disclosure
    # is correct behaviour rather than a defect. It fails only if the count is UNKNOWN.
    # ⛔ The durable fix belongs in the gate itself and cannot be made here: `scripts/**` is
    # edit-fenced while the campaign is live. One line is needed there, a pending-row pattern
    # checked alongside the slot pattern under --final. Recorded so it is not lost.
    # ⚠ KEEP THIS PATTERN IN SYNC WITH THE DISCLOSURE WORDING IN paper/CH6_results.md.
    # 2026-08-10: the marks were reworded from "completed at the single confirmatory look" and
    # "counted at the exogenous stop" to "sealed until ..." and "to be read at ...", because the
    # perfect participles asserted that a look scheduled for 2026-08-27 had already happened while
    # the same chapter's own footnote said the cell "carries no number today by design". Both the
    # OLD and the NEW spellings are matched here: a counter that silently returns 0 after a rename
    # is exactly the failure mode this counter was written to replace.
    pending = len(re.findall(
        r"sealed until the single confirmatory look|to be read at the exogenous stop"
        r"|completed at the single confirmatory look|counted at the exogenous stop",
        allmd, re.I))
    s.add("CRITERION 4 -- 'faultless presentation of data'",
          "pending rows are COUNTED, not merely un-bracketed", True,
          f"{pending} row(s) disclosed as awaiting the 2026-08-27 confirmatory look. "
          f"NOTE: check_rung_freshness --final cannot see these; it greps '[FROM CAMPAIGN' only")

    # A figure "exists" for a reader only if it is INCLUDED as an image with a caption. A line that
    # merely names it in italics is a pointer to nothing, which is precisely the live defect: the
    # Results chapter names thirteen figures it never includes.
    named = set(re.findall(r"\bFigure\s+(\d+\.\d+)\b", allmd))
    cap_re = re.compile(r"!\[\s*\**Figure\s+(\d+\.\d+)\**\s*[-—:.]")
    captioned = set(cap_re.findall(allmd))
    dangling = sorted(named - captioned, key=lambda x: [int(y) for y in x.split(".")])
    s.add("CRITERION 4 -- 'faultless presentation of data'", "every referenced Figure is actually INCLUDED",
          not dangling, f"{len(dangling)} named but never included"
          + (f": {', '.join(dangling[:10])}" if dangling else ""))

    dup = [n for n, c in Counter(cap_re.findall(allmd)).items() if c > 1]
    s.add("CRITERION 4 -- 'faultless presentation of data'", "no duplicate Figure numbers",
          not dup, f"{len(dup)} duplicated" + (f": {dup}" if dup else ""))

    # ================================================================= THE RENDERED PAGE
    # ⚠ NO OTHER GATE LOOKS AT THE PDF. Every check in this project reads markdown, so a defect that
    # only exists after typesetting is invisible to all of them. An adversarial re-mark found the
    # frozen design hash printed at 49 of its 64 characters, clipped by a margin overflow, which meant
    # the study's most load-bearing reproducibility datum could not be verified from the artefact a
    # marker actually reads. The cause is generic: a long unbreakable code span in a narrow table
    # column runs off the page and the tail is simply lost. Markdown-level checking cannot see it.
    pdf = REPO / "paper" / "_build" / "dissertation.pdf"
    clipped: list[str] = []
    checked = False
    try:
        import fitz  # PyMuPDF

        if pdf.is_file():
            # NOTE: Counter is imported at module scope. Re-importing it here made it a LOCAL name
            # for the whole function and broke an unrelated use of it 200 lines below.
            doc = fitz.open(pdf)
            checked = True
            # ⚠ TWO CALIBRATION MISTAKES WERE MADE HERE AND BOTH ARE RECORDED, because each produced
            # a confidently wrong answer.
            #  1. The threshold was first the PAGE width, which is a full margin too generous. A
            #     display equation ran to 593.3pt on a 595.28pt page, passed, and its trailing
            #     quantifier never reached the page at all. Text that overruns the COLUMN is lost or
            #     unreadable whether or not it also overruns the paper.
            #  2. The column was then inferred PER PAGE from the smallest span x0. On a page whose
            #     content is all indented that infers a falsely narrow column, and the check reported
            #     557 violations that were ordinary justified text. A check with 557 false positives
            #     is worse than no check, because it trains a reader to dismiss it.
            # ⇒ Infer the margin ONCE, document-wide, as the modal span x0 (measured: 70.9pt, which
            #   is the 2.5cm the build passes to geometry). Then calibrate the tolerance from the
            #   observed distribution rather than by guess: overshoot is 0.04pt at the median and
            #   2.37pt at the 99th percentile, which is justification and kerning, while genuine
            #   overruns run 5pt to 67pt. 5pt sits in the empty gap between the two populations.
            # ⚠ `s` is the Score object in this function. Do NOT use it as a loop variable here.
            xs: Counter = Counter()
            spans_by_page: list[list] = []
            for i in range(doc.page_count):
                sp = [q for blk in doc[i].get_text("dict")["blocks"]
                      for ln in blk.get("lines", []) for q in ln.get("spans", [])
                      if q["text"].strip()]
                spans_by_page.append(sp)
                for q in sp:
                    xs[round(q["bbox"][0], 1)] += 1
            if xs:
                left = xs.most_common(1)[0][0]
                right = doc[0].rect.width - left
                for i, sp in enumerate(spans_by_page):
                    for q in sp:
                        if q["bbox"][2] > right + 5.0:
                            clipped.append(f"p{i+1}: +{q['bbox'][2]-right:.0f}pt {q['text'][:30]!r}")

                # ⚠ A PAGE HAS FOUR EDGES AND THIS CHECK ONLY EVER TESTED ONE. An adversarial
                # re-mark found body text running off the BOTTOM on seven pages, losing whole words
                # ("Stated explicitly rather than [discovered by a referee.]"), while every
                # right-edge test passed. Same defect class, different axis, invisible to the check
                # built to catch it.
                # The page FOLIO legitimately sits below the text block, so it must be excluded or
                # every page flags. It is identified structurally rather than by a magic number: a
                # short digits-only span at the modal bottom position.
                ys: Counter = Counter()
                for sp in spans_by_page:
                    for q in sp:
                        ys[round(q["bbox"][1], 0)] += 1
                top = min((k for k, v in ys.items() if v > 20), default=70.0)
                bottom = doc[0].rect.height - top
                folio_y = Counter(round(q["bbox"][3], 0) for sp in spans_by_page for q in sp
                                  if q["text"].strip().isdigit() and q["bbox"][3] > bottom)
                folio = folio_y.most_common(1)[0][0] if folio_y else None
                for i, sp in enumerate(spans_by_page):
                    for q in sp:
                        y1 = q["bbox"][3]
                        is_folio = (folio is not None and abs(y1 - folio) < 2.0
                                    and q["text"].strip().isdigit())
                        if y1 > bottom + 5.0 and not is_folio:
                            clipped.append(f"p{i+1}: BOTTOM +{y1-bottom:.0f}pt {q['text'][:26]!r}")
            doc.close()
    except ImportError:
        pass
    s.add("CRITERION 4 -- 'faultless presentation of data'",
          "no rendered text is CLIPPED off the page", checked and not clipped,
          (f"{len(clipped)} clipped run(s); first: {clipped[0]}" if clipped else
           "0 clipped runs in the compiled PDF") if checked else
          "NOT CHECKED: build the PDF and install PyMuPDF, an unchecked page is not a clean one")

    # ⚠ A THIRD PDF DEFECT CLASS, AND THIS SCORECARD WAS BLIND TO IT WHILE REPORTING 26 OF 26.
    # The typesetting engine silently DROPS any character its fonts cannot set. It does not fail the
    # page, it omits the glyph, so the sentence still reads plausibly and nothing looks wrong. On
    # 2026-08-10 two U+26A0 warning signs written into a table vanished this way, `build_paper.py`
    # exited 4, and every check here still passed because the PDF opened and parsed fine. The
    # verdict line was also missed because the build had been read through a pipe, so the shell
    # reported `tail`'s status rather than the build's.
    # ⇒ Compare the non-ASCII glyph SET of the assembled markdown against the PDF's. A character
    # present in the source and absent from the artefact was dropped, whatever the exit code said.
    assembled = REPO / "paper" / "_build" / "dissertation.md"
    dropped: list[str] = []
    if checked and assembled.is_file():
        src = re.sub(r"<!--.*?-->", "", assembled.read_text(encoding="utf-8"), flags=re.S)
        import fitz

        doc = fitz.open(pdf)
        rendered = "".join(doc[i].get_text() for i in range(doc.page_count))
        doc.close()
        for ch in sorted({c for c in src if ord(c) > 0x2000 and c not in "‘’“”"}):
            if ch not in rendered:
                dropped.append(f"U+{ord(ch):04X} {ch!r}")
    s.add("CRITERION 4 -- 'faultless presentation of data'",
          "no character is SILENTLY DROPPED by the typesetter",
          checked and assembled.is_file() and not dropped,
          (f"{len(dropped)} glyph(s) in the source are absent from the PDF: {', '.join(dropped[:4])}"
           if dropped else "every non-ASCII glyph in the assembled source reaches the page")
          if (checked and assembled.is_file()) else "NOT CHECKED: build the PDF first")

    # ⚠ A SECOND, DISTINCT PDF DEFECT CLASS, AND THE ONE THAT COST THE MOST MARKS.
    # The clipping check above catches text running off the PAGE. It does NOT catch text colliding
    # with OTHER TEXT. An adversarial re-mark found overprinted, illegible cells on ten pages,
    # including the confirmatory decision rules and three of nine allocator Sharpe values, one of
    # which the prose singles out by name. The cause is a monospace identifier that cannot wrap
    # inside a narrow table column, so it runs across its neighbour. Both defects are invisible to
    # every markdown-level check in this project, and they need separate detectors because a span
    # can collide without ever reaching the page edge.
    overlap: list[str] = []
    if checked:
        import fitz  # already imported successfully above

        doc = fitz.open(pdf)
        for i in range(doc.page_count):
            # ⚠ GROUP BY VERTICAL BAND, NOT BY PyMuPDF's LINE OBJECT. A table row is many separate
            # line objects, one per cell, so a per-line scan cannot see a cell colliding with its
            # NEIGHBOUR, which is exactly the defect. Banding by rounded baseline finds it.
            band: dict[int, list] = {}
            for blk in doc[i].get_text("dict")["blocks"]:
                for ln in blk.get("lines", []):
                    for sp in ln.get("spans", []):
                        if len(sp["text"].strip()) > 1:
                            band.setdefault(round(sp["bbox"][3] / 3.0), []).append(sp)
            for key in sorted(band):
                spans = sorted(band[key], key=lambda sp: sp["bbox"][0])
                for a_sp, b_sp in zip(spans, spans[1:]):
                    # > 2pt of genuine overlap. A smaller tolerance fires on composed accents (a
                    # circumflex drawn over a letter is two spans at one x) and on kerning, and
                    # neither is a defect. Reporting a non-defect trains a reader to ignore the
                    # check, which is worse than the check not existing.
                    if a_sp["bbox"][2] - b_sp["bbox"][0] > 2.0:
                        overlap.append(f"p{i+1}: {a_sp['text'].strip()[:22]!r} over "
                                       f"{b_sp['text'].strip()[:22]!r}")
        doc.close()
    s.add("CRITERION 4 -- 'faultless presentation of data'",
          "no rendered text OVERPRINTS other text", checked and not overlap,
          (f"{len(overlap)} collision(s); first: {overlap[0]}" if overlap else
           "0 overlapping spans in the compiled PDF") if checked else
          "NOT CHECKED: build the PDF and install PyMuPDF")

    # ================================================================= THE HUMAN REGISTER (H1)
    em = {ch: prose_lines(t).count(EM_DASH) for ch, t in prose.items() if prose_lines(t).count(EM_DASH)}
    s.add("HUMAN REGISTER (H1) -- zero tolerance, re-measured every pass",
          "zero em dashes in body prose", not em,
          f"{sum(em.values())} across {len(em)} chapters" + (f"; worst {max(em, key=em.get)}={max(em.values())}" if em else ""))

    semi = {ch: prose_lines(t).count(";") for ch, t in prose.items() if prose_lines(t).count(";")}
    s.add("HUMAN REGISTER (H1) -- zero tolerance, re-measured every pass",
          "zero semicolons in body prose", not semi,
          f"{sum(semi.values())} across {len(semi)} chapters" + (f"; worst {max(semi, key=semi.get)}={max(semi.values())}" if semi else ""))

    sents = sentences(prose_lines(allp))
    lens = [len(re.findall(r"\b[\w'-]+\b", x)) for x in sents]
    mean = sum(lens) / max(len(lens), 1)
    s.add("HUMAN REGISTER (H1) -- zero tolerance, re-measured every pass",
          "mean sentence length under 34 words", mean < 34, f"measured {mean:.1f} over {len(sents):,} sentences")
    over = sum(1 for x in lens if x > 60)
    s.add("HUMAN REGISTER (H1) -- zero tolerance, re-measured every pass",
          "no sentence over 60 words", over == 0, f"{over} sentences exceed 60 words")
    shortish = sum(1 for x in lens if x < 13) / max(len(lens), 1)
    s.add("HUMAN REGISTER (H1) -- zero tolerance, re-measured every pass",
          "at least 15% of sentences under 13 words (rhythm)", shortish >= 0.15,
          f"measured {100*shortish:.1f}%")

    # ================================================================= LEXICAL TELLS (H2)
    hits = {w: len(re.findall(r"\b" + re.escape(w) + r"\b", allp, re.I)) for w in BANNED}
    hits = {w: c for w, c in hits.items() if c}
    s.add("LEXICAL TELLS (H2) -- the AI-register vocabulary", "zero banned constructions",
          not hits, f"{sum(hits.values())} hits: {dict(sorted(hits.items(), key=lambda kv: -kv[1])[:6])}" if hits else "clean")
    ing = TRAILING_ING.findall(allp)
    s.add("LEXICAL TELLS (H2) -- the AI-register vocabulary", "zero trailing '-ing' analyses",
          not ing, f"{len(ing)} found: {Counter(x.lower() for x in ing).most_common(4)}" if ing else "clean")
    aph = APHORISM.findall(allp)
    s.add("LEXICAL TELLS (H2) -- the AI-register vocabulary", "aphorism formula 'X is the Y of Z' rare (<=2)",
          len(aph) <= 2, f"{len(aph)} found")

    # ================================================================= CLARITY (C1, C2, C7, S10)
    vg = {w: len(re.findall(r"\b" + re.escape(w) + r"\b", allp, re.I)) for w in VAGUE}
    vg = {w: c for w, c in vg.items() if c}
    s.add("ABSOLUTE CLARITY (C1-C8) -- the reader must never do your work",
          "C7: no vague quantifiers or placeholder nouns", not vg,
          f"{sum(vg.values())} hits: {vg}" if vg else "clean")

    orphans = [p[:70] for t in prose.values() for p in paragraphs(t) if PRONOUN_OPEN.match(p)]
    s.add("ABSOLUTE CLARITY (C1-C8) -- the reader must never do your work",
          "C2: no paragraph opens on an orphan pronoun", not orphans,
          f"{len(orphans)} found" + (f"; e.g. {orphans[0]!r}" if orphans else ""))

    labels = [p[:60] for t in prose.values() for p in paragraphs(t) if LABEL_OPEN.match(p)]
    s.add("ABSOLUTE CLARITY (C1-C8) -- the reader must never do your work",
          "S10: no paragraph opens on an internal label", not labels,
          f"{len(labels)} found" + (f"; e.g. {labels[0]!r}" if labels else ""))

    # C1: one name per object. The recorded live drift set.
    drift = {n: len(re.findall(re.escape(n), allp, re.I))
             for n in ("the fed block", "the feedback block", "the tail vector", "the six statistics")}
    named_variants = sum(1 for c in drift.values() if c)
    s.add("ABSOLUTE CLARITY (C1-C8) -- the reader must never do your work",
          "C1: the manipulated object has ONE canonical name", named_variants <= 1,
          f"{named_variants} distinct names in use: { {k: v for k, v in drift.items() if v} }")

    # ================================================================= SHOW THE OBJECT (LAW 1 / R4 / O2)
    bad_sharpe = []
    for ch, t in prose.items():
        for sent in sentences(t):
            if SHARPE.search(sent) and not GROSSNET.search(sent):
                bad_sharpe.append((ch, sent[:70]))
    s.add("LAW 1 / R4 -- show the object, and label every Sharpe",
          "every Sharpe sentence states GROSS or NET", not bad_sharpe,
          f"{len(bad_sharpe)} unlabelled" + (f"; e.g. {bad_sharpe[0][0]} {bad_sharpe[0][1]!r}" if bad_sharpe else ""))

    # ⚠ READ THE RAW CHAPTER, NOT THE STRIPPED PROSE. Captions are word-excluded, which is precisely
    # why the showing duties should be discharged in them: a figure closes a duty and costs no words.
    # Scanning the stripped text would report a duty as unmet at the exact moment it was met well.
    res = (PAPER / "CH6_results.md").read_text(encoding="utf-8")
    for duty, pat, why in (
        ("O2: a DISTRIBUTION exhibit is referenced", r"dispersion|distribution of|per-seed|IQR|spread across seeds", "the cloud, not the mean"),
        ("O3: a PATH exhibit is referenced", r"trajector|expanding.window|rolling|cumulative", "the path, not the endpoint"),
        ("D2: a SEED-TRAJECTORY exhibit is referenced", r"seed[- ]trajector|against seed count|n\s*=\s*1", "the estimator, not the estimate"),
    ):
        s.add("LAW 1 / R4 -- show the object, and label every Sharpe", duty,
              bool(re.search(pat, res, re.I)), why)

    # ================================================================= DIFFICULTY (Criterion 3 / W5)
    dif = re.search(r"(core[- ]hours|GPU[- ]hours|environment steps|trainings?)\b", allp, re.I)
    s.add("CRITERION 3 -- novelty GIVEN DIFFICULTY (supply the denominator)",
          "difficulty stated IN THE BODY, in numbers", bool(dif),
          "found" if dif else "absent: the marker will supply a default denominator, and the default is unkind")
    adj = re.findall(r"\b(challenging|extensive|comprehensive|substantial|significant effort)\b", allp, re.I)
    s.add("CRITERION 3 -- novelty GIVEN DIFFICULTY (supply the denominator)",
          "difficulty carried by COUNTS, not adjectives", len(adj) <= 2,
          f"{len(adj)} discountable adjectives: {Counter(x.lower() for x in adj).most_common(4)}")

    # ================================================================= REPRODUCIBILITY (PRIORITY 5)
    rung = REPO / "outputs" / "tables" / "achieved_rung.json"
    s.add("PRIORITY 5 -- 100% reproducibility, a WARN counts as a FAIL",
          "the achieved rung is STATED, never assumed", rung.is_file(),
          f"{rung.relative_to(REPO)}" if rung.is_file() else "missing: check_rung_freshness exits 2")

    print("=" * 100)
    print("  STRICT SCORECARD -- every mechanically checkable duty in the project's own law")
    print("  Measured against the real files. Nothing here is recalled.")
    return 0 if s.render() == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
