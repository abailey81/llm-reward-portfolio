#!/usr/bin/env python3
"""Build the dissertation PDF from the paper/ markdown chapters (the DELIVERABLE pipeline).

Why this exists
---------------
The dissertation is graded on the submitted PDF alone, but until 2026-07-02 the repo had NO
md->PDF toolchain at all (audit NEW-LENS A: no pandoc/LaTeX anywhere, no build target) — the
final deliverable was un-producible. This script + the PINNED portable toolchain in ``tools/``
(pandoc 3.10 + Tectonic 0.16.9, downloaded 2026-07-02; no system install, reproducible) close
that gap and make the PDF compilable from day one, so compile problems surface MONTHS before
the 1-Sep deadline instead of at submission week.

What it does
------------
1. Assembles the chapters in the UCL-required section order (``ASSEMBLY`` below; internal
   working files like 00_FRAMING / 01_LITERATURE_DOSSIER are deliberately excluded).
2. Rewrites the repo's citation convention -- [`key`] / [`k1`; `k2`] -- into pandoc citeproc
   syntax ([@key] / [@k1; @k2]), OUTSIDE fenced code blocks only (code stays byte-intact).
3. Runs pandoc --citeproc with the Harvard "Cite Them Right" CSL (paper/harvard-cite-them-right.csl,
   the UCL-house Harvard variant) over paper/refs.bib, PDF via the Tectonic XeTeX engine
   (full unicode; downloads TeX packages on first run, then cached).
4. Surfaces every warning pandoc OR the TeX engine emits (esp. citeproc "reference not found" — a
   dangling key in the PDF is a grading defect) and exits non-zero on any ERROR.
5. VERIFIES THE DELIVERABLE IT JUST WROTE, and fails on each of four defect classes that are all
   invisible in the source and all cost marks in the PDF:
     rc=3  a control byte in the assembled markdown (invisible to every editor and to grep);
     rc=4  a character the engine could not typeset — SILENTLY ABSENT from the PDF;
     rc=5  a glyph with no ToUnicode mapping — renders, but is unsearchable and uncopyable.
   Read ``_MISSING_CHAR_RE`` before touching the diagnostic plumbing: for nineteen days these
   checks were impossible because the channel that carries them was being decoded with the box's
   locale codec and silently emptied.

Usage
-----
    python scripts/build_paper.py                  # -> paper/_build/dissertation.pdf
    python scripts/build_paper.py --md-only        # -> paper/_build/dissertation.md (inspect/word-count)
    python scripts/build_paper.py --out X.pdf      # custom output

The assembled intermediate markdown is ALWAYS written next to the PDF so the exact compiled
text is inspectable (and is what scripts/word_budget.py counts).

Notes / deliberate choices
--------------------------
* ``--toc`` generates the Table of Contents with REAL page numbers; FRONT_MATTER.md's manual
  ToC/LoF/LoT lists remain for the md readers — at final-compile time keep exactly one of the
  two (tracked in the ULTRAPLAN write-up punchlist, not silently resolved here).
* Figures are not yet embedded in the chapters (they land at write-time from
  paper/FIGURE_TABLE_MANIFEST.md); ``--resource-path`` already covers paper/ and outputs/figures
  so embeds compile the moment they appear.
* The toolchain paths are PINNED to the portable copies in tools/ and fail LOUD with install
  instructions if absent — no silent PATH fallback (a different pandoc version could render
  differently at submission time).
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: The UCL 16-section submission order (IFTE0008), mapped onto the chapter files. Internal
#: working documents (00_FRAMING, 01_LITERATURE_DOSSIER, FIGURE_TABLE_MANIFEST, NOMENCLATURE)
#: are NOT part of the deliverable and are deliberately absent.
#: ⚠ 2026-08-01 (RUN 10, DEFERRED item 15a-i): NINE FINISHED ARTEFACTS WERE ABSENT FROM THE PDF.
#: This tuple is the WHOLE deliverable — there is no glob, no directory walk and no transclusion — so
#: a file that is authored but not listed here simply does not reach a marker.
#: `FIGURE_TABLE_MANIFEST.md` marked them BUILT, which was true of the FILES and false of the PDF:
#: nobody had distinguished *authored* from *wired*. Placement is the write-up lane's spec — each
#: table sits immediately AFTER the chapter that refers to it.
#:
#: ⚠ `BODY_CHAPTERS` in `scripts/word_budget.py` MUST NOT GAIN THESE ENTRIES. Its docstring says
#: "keep in sync with build_paper.py ASSEMBLY", and that sync is DELIBERATELY BROKEN for
#: word-excluded material (`APPENDIX_B` is the existing precedent). Tables and the nomenclature are
#: word-excluded under the UCL rules, so they belong here and NOT in the word count. Do not "fix"
#: the divergence — doing so would silently break the 10,000-word gate.
ASSEMBLY: tuple[str, ...] = (
    "FRONT_MATTER.md",                          # cover/title/abstract/ack/ToC-lists/ethics/AI-disclosure
    "NOMENCLATURE.md",                          # notation table (front-matter region; word-excluded)
    "CH1_introduction.md",                      # Introduction
    "CH2_related_work.md",                      # Literature Review
    "tables/T_literature_positioning.md",       # T10 positioning matrix + T18 innovation axes
    # ⚠ `02_CHAPTER_theory.md` USED TO SIT HERE and has been MOVED to APPENDICES as Appendix C
    # (2026-08-01, RUN 11, write-up request M189). Same half-migration shape as the prototype above:
    # the write-up lane had already converted the file's heading to
    # "# Appendix C — … (word-excluded)" and renumbered the whole document to the new order, so
    # leaving this entry in ASSEMBLY would once again render an APPENDIX MID-BODY — the exact defect
    # coord caught as M159. PROVENANCE, because this overrides a standing decision: the body
    # measured 23,309 words against IFTE0008's hard 10,000 (2.33x, on a rule whose own wording is
    # "Penalties for exceeding"), and TAMER chose the full compliance pass over the measured
    # alternatives. Relocation is ALSO a conformance fix independent of the budget — the 16-section
    # structure has no Theory section — and it is LOSSLESS: appendices are excluded from the word
    # COUNT, not from the reading.
    "CH4_methods.md",                           # Data + Methodology
    "tables/T_arms_and_hypotheses.md",          # T13-T15 + Table 3b inference machinery
    "tables/T_models_and_reward_canon.md",      # T16-T17 model pins + the 11-reward canon
    "tables/T_design_decisions.md",             # T11 choice / alternatives / rationale / cost
    "tables/T_reproducibility_and_mechanism.md",  # T19 three-layer repro + T20 mechanism apparatus
    # ⚠ `CH5_prototype.md` USED TO SIT HERE and has been MOVED to APPENDICES (2026-08-01, §100.39).
    # Its own first line now reads "# Appendix D — The Prototype … (word-excluded)": the CONTENT was
    # converted to an appendix by the restructure, and this ASSEMBLY position was not — a textbook
    # half-migration, invisible until the PDF actually compiled. The compiled body read
    #   Chapter 1 · 2 · 3 · 4 · **Appendix D** · Chapter 6 · Chapter 7
    # i.e. an APPENDIX RENDERED MID-BODY, immediately before Results. Found by the COORD lane (M159).
    "CH6_results.md",                           # Results
    "tables/T_benchmark_allocators.md",         # the classical-allocator floor (CH6 comparator)
    "CH7_discussion_limitations_conclusion.md",  # Discussion, Limitations, Conclusions
    # References are GENERATED by citeproc AFTER this list; APPENDICES then append after References.
    #
    # ⚠ THE FOUR `paper/sections/` FILES ARE DELIBERATELY **NOT** LISTED, and adding them would be a
    # DEFECT rather than an omission. They are INSERTS into body chapters (each says so in its own
    # header), carrying ~1,100 words of BODY prose. `word_budget.py` counts `BODY_CHAPTERS` only, so
    # wiring them as standalone entries would make that prose vanish from the 10,000-word gate —
    # word-count evasion, not the appendix escape hatch. They merge into CH1 / theory / CH7, where
    # they count. That merge is `paper/`-side work owned by the write-up lane.
)

#: Appendices append AFTER the generated References div, because UCL requires the reference list to
#: PRECEDE the appendices. The Limitations Register was extracted out of CH7 -- where it printed
#: BEFORE the References div and so violated that order (audit P28) -- into its own file listed here.
#: Each appendix file is word-excluded: it is deliberately ABSENT from scripts/word_budget.py
#: BODY_CHAPTERS so it never counts toward the 10,000-word main-body limit. citeproc still collects
#: any citations occurring in the appendices below and renders them into the References div above, so
#: their cites resolve normally.
APPENDICES: tuple[str, ...] = (
    "appendices/A_quality_control_record.md",    # Appendix A -- the execution/QC record (2026-08-01)
    "APPENDIX_B_limitations.md",                 # Appendix B -- Limitations Register (was embedded in CH7)
    # Appendix D -- The Prototype. MOVED HERE from mid-ASSEMBLY on 2026-08-01 (§100.39): the file's own
    # heading was converted to "# Appendix D — The Prototype … (word-excluded)" by the restructure while
    # its ASSEMBLY position stayed between the CH4 tables and Results, so the compiled PDF rendered an
    # APPENDIX INSIDE THE BODY, before the Results chapter. Placed in LETTER ORDER (A · B · D) so the
    # reader never meets D before A. ⚠ It is deliberately NOT in `word_budget.BODY_CHAPTERS` and must
    # not be added: the file is word-EXCLUDED by its own "(word-excluded)" heading, which is exactly
    # why `word_budget` already scores it 0.
    # Appendix C -- Theory. Moved out of the body 2026-08-01 (M189); see the note at its old
    # ASSEMBLY position for the provenance. POSITION IS LOAD-BEARING, NOT COSMETIC: appendix letters
    # are assigned by DOCUMENT ORDER and the write-up lane has already renumbered every heading and
    # cross-reference to A · B · C · D · E. B is PINNED and cannot move — the HASH-BOUND files cite
    # Appendix B SECTION numbers (PREREGISTRATION.md B.6.5/B.3.1, config/preregistration.yaml
    # B.3.3/B.2.6, src/feedback/schema.py B.2.7/B.2.8) — so theory takes C, and the prototype and the
    # scale table shift to D and E.
    "02_CHAPTER_theory.md",                      # Appendix C -- Theory (relocated 2026-08-01)
    "CH5_prototype.md",                          # Appendix D -- the prototype / machinery validation
    "tables/T_scale_and_difficulty.md",          # Appendix E -- T12 scale + difficulty
    # Appendix F -- prompts + authored reward code. WIRED 2026-08-01 (RUN 12 close) per the
    # instruction the write-up lane left INSIDE the file itself; it was authored but unwired, so it
    # reached no PDF at all. APPENDED LAST deliberately: appendix letters are assigned by DOCUMENT
    # ORDER and A-E are already renumbered across every heading and cross-reference, so taking the
    # next free letter renumbers nothing. ⚠ Deliberately NOT in `word_budget.BODY_CHAPTERS` -- its
    # heading carries "(word-excluded)", exactly like Appendix D, so word_budget already scores it 0.
    # The file is GENERATED by paper/appendices/gen_F_prompts_and_authored_code.py (self-locating).
    "appendices/F_prompts_and_authored_code.md",  # Appendix F -- prompts + authored reward code
)

PANDOC = REPO / "tools" / "pandoc-3.10" / "pandoc.exe"
TECTONIC = REPO / "tools" / "tectonic" / "tectonic.exe"
CSL = REPO / "paper" / "harvard-cite-them-right.csl"
BIB = REPO / "paper" / "refs.bib"

#: A bib key: starts with a letter and CONTAINS A 4-DIGIT YEAR (every key in refs.bib does) —
#: the year requirement is the discriminator that keeps bracketed inline code (e.g. [`np.mean`],
#: [`--gpu 3`]) out of the citation transform.
_KEY_RE = re.compile(r"`([A-Za-z][A-Za-z0-9_.+-]*\d{4}[A-Za-z0-9_:.+-]*)`")
#: A citation GROUP: a bracket (no nested brackets) containing >= 1 backticked year-key anywhere.
#: DOTALL-free but [^\[\]] admits newlines, so groups that WRAP ACROSS LINES are matched (the
#: first-compile audit found 18 such misses: multi-line groups + locator/prefix forms like
#: [`haarnoja2018sac`, SS5] and [`chow2015risk`, Prop. 1; cf. robust MDPs `iyengar2005robust`]).
_GROUP_RE = re.compile(
    r"\[([^\[\]]*?`[A-Za-z][A-Za-z0-9_.+-]*\d{4}[A-Za-z0-9_:.+-]*`[^\[\]]*?)\]"
)
_FENCE_RE = re.compile(r"^(```|~~~)")


def _transform_group(m: re.Match[str]) -> str:
    """Inside one citation group, turn every backticked year-key into @key; keep all other text.

    [`k2021a`]                              -> [@k2021a]
    [`k2021a`; `k2022b`]                    -> [@k2021a; @k2022b]     (incl. across a line wrap)
    [`k2018a`, SS5]                          -> [@k2018a, SS5]          (pandoc locator suffix)
    [`k2015a`, Prop. 1; cf. X `k2005b`]     -> [@k2015a, Prop. 1; cf. X @k2005b]  (prefix text)
    """
    return "[" + _KEY_RE.sub(lambda k: "@" + k.group(1), m.group(1)) + "]"


def rewrite_citations(md: str) -> str:
    """Rewrite the repo citation convention into pandoc citeproc syntax, skipping fenced code.

    Operates on whole unfenced SEGMENTS (not lines) so citation groups wrapping across newlines
    transform correctly; fenced code blocks (``` / ~~~) pass through byte-intact. Any transformed
    key that is absent from refs.bib then surfaces as a citeproc WARNING at compile time — the
    fail-loud path for dangling citations.
    """
    segments: list[str] = []
    buf: list[str] = []
    in_fence = False
    for line in md.splitlines(keepends=True):
        if _FENCE_RE.match(line.lstrip()):
            # flush the current segment, transform it iff it was prose
            segments.append("".join(buf) if in_fence else _GROUP_RE.sub(_transform_group, "".join(buf)))
            buf = [line]
            in_fence = not in_fence
            # the fence line itself belongs to the (new) code segment when opening, and to the
            # closing code segment when closing — either way it must not be transformed:
            segments.append("".join(buf))
            buf = []
            continue
        buf.append(line)
    segments.append("".join(buf) if in_fence else _GROUP_RE.sub(_transform_group, "".join(buf)))
    return "".join(segments)


def assemble(chapter_dir: Path, names: tuple[str, ...] = ASSEMBLY,
             appendices: tuple[str, ...] = APPENDICES) -> str:
    """Concatenate the deliverable in UCL submission order; fail loud on a missing file.

    Order: body chapters -> generated References div -> appendices. UCL requires the reference list
    to PRECEDE the appendices, so the appendices are appended AFTER the `#refs` div (citeproc still
    resolves any citations occurring inside them into that bibliography).
    """
    parts: list[str] = []
    missing = [n for n in (*names, *appendices) if not (chapter_dir / n).is_file()]
    if missing:
        raise FileNotFoundError(f"paper/ is missing required chapter file(s): {missing}")
    for name in names:
        text = (chapter_dir / name).read_text(encoding="utf-8")
        parts.append(text.rstrip() + "\n")
        if name == "FRONT_MATTER.md":
            # S10 (2026-07-06): the Table of Contents belongs AFTER the front matter (UCL order:
            # Cover -> Title -> Abstract -> Acknowledgements -> ToC) — raw LaTeX, real page numbers.
            # Replaces pandoc's --toc, which printed it BEFORE the title page.
            parts.append("\\clearpage\n\\tableofcontents\n\\clearpage\n")
    # UCL requires an explicit References section; citeproc places the bibliography inside the
    # `#refs` div (otherwise it is appended headingless at the document end). Unnumbered per style.
    parts.append(
        "# References {.unnumbered}\n\n::: {#refs}\n:::\n"
    )
    # Appendices follow the References (UCL order: reference list before appendices).
    for name in appendices:
        text = (chapter_dir / name).read_text(encoding="utf-8")
        parts.append(text.rstrip() + "\n")
    # \newpage between chapters so each starts on a fresh page (pandoc passes raw LaTeX through).
    return "\n\\newpage\n\n".join(parts) + "\n"


#: The engine's OWN report that it could not typeset a character. Tectonic/XeTeX prints, once per
#: occurrence per typesetting pass:
#:     warning: texput.tex:3279: Missing character: There is no ≈ (U+2248) in font [lmroman12-regular]…
#: The character is then silently ABSENT from the PDF. This is the authoritative absence signal —
#: strictly better than extracting the built PDF's text, because a text extractor also returns
#: U+FFFF for a glyph that RENDERS but carries no ToUnicode mapping (routine for TeX math fonts).
#: Absent and unmapped are different values; only this channel distinguishes them.
#:
#: ⚠ 2026-08-01 (RUN 11). Seventeen such drops were being emitted on EVERY build for nineteen days
#: and not one reached the operator. TWO independent defects hid them, EITHER of which alone was
#: sufficient — both reproduced by execution before this fix was written:
#:   (1) ``subprocess.run(..., text=True)`` with no ``encoding=`` decoded the channel with the box's
#:       LOCALE codec (cp1251 here). The reader thread died on the first non-decodable byte
#:       (UnicodeDecodeError, byte 0x98) and subprocess.run STILL RETURNED rc=0 with stdout='' and
#:       stderr='' — 40,871 characters of diagnostics replaced by a fabricated empty channel, so
#:       line "0 pandoc warning(s)" was printed from no evidence at all;
#:   (2) the filter matched only 'WARNING'/'Error', while tectonic prints lowercase 'warning:' —
#:       0 of 51 emitted lines matched even once the channel was made readable.
#: The lesson generalises past this script: "the build reported no warnings" is not evidence unless
#: the channel that carries warnings is proven readable.
#:
#: The engine emits the SAME drop in two spellings — TeX's own and Tectonic's driver message:
#:     warning: texput.tex:3279: Missing character: There is no ≈ (U+2248) in font [lmroman12-regular]…
#:     warning: could not represent character "≈" (0x2248) in font "[lmroman12-regular]:…"
#: MEASURED on one real build they paired 1:1 (30 and 30), but matching only one spelling would
#: make the gate depend on a coincidence between two independent message paths, so both are read.
_MISSING_CHAR_RE = re.compile(
    r"Missing character: There is no .{0,4}\(U\+([0-9A-Fa-f]{4,6})\) in font \[([^\]]+)\]"
    r'|could not represent character ".{1,4}" \(0x([0-9A-Fa-f]{2,6})\) in font "\[?([^\]"]+)'
)
#: Substrings that mark a line as reporting an un-typesettable character, in either spelling.
_MISSING_CHAR_MARKERS = ("Missing character", "could not represent character")

#: Both spellings the toolchain uses. Case-sensitive alternatives rather than a case-insensitive
#: match, so the ordinary prose words "warning"/"error" inside a pandoc echo of our own text cannot
#: fire the gate.
_DIAGNOSTIC_RE = re.compile(r"\[WARNING\]|WARNING|warning:|\[ERROR\]|Error|error:")


def scan_diagnostics(channel: str) -> tuple[list[str], list[str]]:
    """Split a build diagnostic channel into (warning/error lines, missing-character lines).

    Missing-character lines are DEDUPLICATED on their full text: the engine re-reports every drop
    on each typesetting pass, and a repeat carries a byte-identical ``texput.tex:<line>:`` prefix.
    Two distinct drops on the same source line therefore collapse into one — the count is a
    LOWER BOUND on occurrences, which is the safe direction for a gate that fires on any at all.
    """
    lines = channel.splitlines()
    warnings = [ln for ln in lines if _DIAGNOSTIC_RE.search(ln)]
    missing = sorted({ln.strip() for ln in lines
                      if any(mark in ln for mark in _MISSING_CHAR_MARKERS)})
    return warnings, missing


def verify_pdf_glyphs(pdf_path: Path) -> tuple[int, str]:
    """Second, INDEPENDENT route: extract the built PDF's text and count U+FFFF markers.

    Returns ``(count, status)``. ``status`` is "ok" when the extraction ran, or an explanatory
    string when it could not. A count of 0 from a check that never ran is NOT clean — the caller
    must treat a non-"ok" status as unverified rather than as a pass, so the return type keeps the
    two apart instead of collapsing them into a single integer.

    This route is deliberately kept ALONGSIDE the engine-diagnostic gate rather than replacing it:
    agreement between two independent derivations is evidence, one derivation repeated is not.
    It is also the weaker of the two — see ``_MISSING_CHAR_RE`` on why U+FFFF over-reports.
    """
    try:
        import fitz  # noqa: PLC0415 — optional; PyMuPDF is not a declared runtime dependency
    except ImportError as exc:
        return 0, f"NOT CHECKED (PyMuPDF unavailable: {exc})"
    try:
        # `fitz.Document`, not the `fitz.open` alias: this is a BINARY PDF reader, but the repo's
        # encoding-pin guard (tests/test_audit_regressions.py) matches any call named `open` without
        # an `encoding=` and cannot tell the two apart. It flagged this line, correctly by its own
        # rule. Using the real class name satisfies the guard by being accurate rather than by
        # exempting the call — a guard you weaken to pass is a guard you have deleted.
        with fitz.Document(pdf_path) as doc:
            return sum(page.get_text().count("￿") for page in doc), "ok"
    except Exception as exc:  # noqa: BLE001 — a broken PDF must report, never mask, the failure
        return 0, f"NOT CHECKED (extraction failed: {type(exc).__name__}: {exc})"


#: The four TeX Gyre Heros faces the deliverable's typeface is loaded from, BY FILE.
_HEROS_FACES = ("texgyreheros-regular.otf", "texgyreheros-bold.otf",
                "texgyreheros-italic.otf", "texgyreheros-bolditalic.otf")


def tectonic_bundle_provenance(cache_dir: Path) -> dict[str, Any]:
    """The content-addressed Tectonic bundle the fonts actually resolve from, and whether the four
    Heros faces are IN it.

    F-19 (coord, 2026-08-01). Since RUN 11 the deliverable's typeface is TeX Gyre Heros loaded BY
    FILE from Tectonic's bundle, so the bundle is now a REPRODUCIBILITY DEPENDENCY of the compiled
    artefact — and its digest was recorded nowhere. Priority 5 is explicit that "a pin nobody can
    verify is FICTIONAL" (the R85 lesson), so this does not assert the bundle: it resolves the
    content-addressed directory, records its digest, and CHECKS that all four faces are present.
    A missing face is why `mainfont` would silently fall back and re-flatten the document.

    Returns ``{"digest", "path", "faces_present", "faces_missing"}``; ``digest`` is None when the
    cache has not been populated yet (a first-ever compile downloads it), which is reported as
    unknown rather than as clean.
    """
    data = cache_dir / "bundles" / "data"
    if not data.is_dir():
        return {"digest": None, "path": str(data), "faces_present": [], "faces_missing": [],
                "reason": "bundle cache not populated (a first compile will fetch it)"}
    # The content-addressed bundle dir IS the digest; pick the one that actually holds the faces.
    for cand in sorted(p for p in data.iterdir() if p.is_dir()):
        present = [f for f in _HEROS_FACES if (cand / f).is_file()]
        if present:
            return {"digest": cand.name, "path": str(cand), "faces_present": present,
                    "faces_missing": [f for f in _HEROS_FACES if f not in present]}
    return {"digest": None, "path": str(data), "faces_present": [],
            "faces_missing": list(_HEROS_FACES),
            "reason": "no cached bundle carries the Heros faces"}


def scan_control_bytes(text: str) -> list[tuple[int, int, str]]:
    """Every control byte in the assembled deliverable, excluding tab/LF/CR.

    Returns ``(line_number, codepoint, line_excerpt)`` per hit. A stray BEL or NUL is invisible in
    every editor and every ``grep``, survives the whole pipeline, and can break the compile in a way
    whose diagnostic points somewhere else entirely.
    """
    hits: list[tuple[int, int, str]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for ch in line:
            if ord(ch) < 0x20 and ch != "\t":
                hits.append((lineno, ord(ch), line.strip()[:90]))
    return hits


def build(md_only: bool, out: Path | None) -> int:
    build_dir = REPO / "paper" / "_build"
    build_dir.mkdir(parents=True, exist_ok=True)
    assembled = rewrite_citations(assemble(REPO / "paper"))
    md_path = build_dir / "dissertation.md"
    md_path.write_text(assembled, encoding="utf-8")
    print(f"[build_paper] assembled {len(ASSEMBLY)} chapters + {len(APPENDICES)} appendix(es) -> {md_path}")

    control = scan_control_bytes(assembled)
    if control:
        print(f"[build_paper] FAILED: {len(control)} control byte(s) in the assembled deliverable "
              f"— invisible in every editor and in grep, and they reach the compiler:", file=sys.stderr)
        for lineno, cp, excerpt in control[:20]:
            print(f"  line {lineno}: U+{cp:04X} in: {excerpt}", file=sys.stderr)
        return 3

    if md_only:
        return 0

    for tool, hint in (
        (PANDOC, "download pandoc-3.10-windows-x86_64.zip from github.com/jgm/pandoc/releases "
                 "and extract into tools/ (see docs/CAMPAIGN_RUNBOOK.md, paper-build section)"),
        (TECTONIC, "download tectonic x86_64-pc-windows-msvc.zip from "
                   "github.com/tectonic-typesetting/tectonic/releases and extract into tools/tectonic/"),
        (CSL, "download harvard-cite-them-right.csl from the CSL styles repository into paper/"),
        (BIB, "paper/refs.bib is missing — the bibliography is required"),
    ):
        if not tool.exists():
            print(f"[build_paper] MISSING: {tool}\n  fix: {hint}", file=sys.stderr)
            return 2

    pdf_path = out or (build_dir / "dissertation.pdf")
    cmd = [
        str(PANDOC),
        str(md_path),
        "--from", "markdown+tex_math_dollars+raw_tex",
        "--citeproc",
        "--csl", str(CSL),
        "--bibliography", str(BIB),
        # S10 (2026-07-06): NO --toc and NO --number-sections. --toc printed pandoc's ToC BEFORE
        # the title page (UCL order: Cover -> Title -> Abstract -> Ack -> ToC), and --number-sections
        # double-numbered every heading (chapters carry manual numbers) while stamping the front
        # matter as 'Chapter 1' and the appendix as 'Chapter 9'. The ToC is emitted as raw LaTeX at
        # the END of the front matter by assemble() — real page numbers, correct position.
        "--pdf-engine", str(TECTONIC),
        "--resource-path", f"{REPO / 'paper'};{REPO / 'outputs' / 'figures'};{REPO}",
        "-V", "documentclass=report",
        "-V", "fontsize=12pt",
        "-V", "geometry:margin=2.5cm",
        # UCL IFTE0008 presentation rules: main text at 1.5 line spacing (setspace via pandoc's
        # linestretch) and a sans-serif typeface (DISSERTATION_ALIGNMENT_AND_GUIDELINES.md:26 —
        # "Arial/Helvetica >= 10pt"), with no system font file so the build stays reproducible
        # under Tectonic.
        #
        # ⚠ 2026-08-01 (RUN 11). This line read `\usepackage{helvet}\renewcommand{\familydefault}
        # {\sfdefault}` from 2026-07-05 to today and was the WORST OF BOTH WORLDS — it delivered
        # neither the typeface nor the shapes. Reported by WRITEUP (M168: "bold does not render");
        # cause established by BISECTION on a minimal document through this exact command line,
        # span-font census of each built PDF:
        #     helvet + sfdefault : LMRoman12-Regular x26, bold 0, italic 0   <- as shipped
        #     no header-include  : LMRoman12-Regular/Bold/Italic, bold 9, italic 2
        #     sfdefault ALONE    : LMSans12-Regular, LMSans10-Bold 9, LMSans12-Oblique 2
        # `helvet` declares Helvetica the classic 8-bit NFSS way, but pandoc's template loads
        # unicode-math (hence fontspec) for the XeTeX engine, so the phv family has no loadable
        # shapes here: every shape request — bold AND italic — fell back to the upright default,
        # SILENTLY and with no font-shape warning, while the body stayed the SERIF Latin Modern
        # Roman. So the shipped document was serif (guideline missed) with every emphasis in a
        # 230-page argument flattened (UCL dimension 4, "faultless presentation").
        # FIRST FIX (mine, superseded within the hour): drop `helvet`, keep `\sfdefault`. That gave
        # Latin Modern Sans — shapes restored, but LM Sans is the Computer Modern sans, NOT a
        # Helvetica. It traded a rendering defect for a CONFORMANCE regression on the very
        # guideline the line existed to satisfy. WRITEUP caught that (M178) and it was right.
        #
        # WHAT SHIPS: TeX Gyre Heros, loaded BY FILE. Heros is the URW Nimbus Sans / Helvetica
        # clone, so this is genuine Helvetica metrics — the guideline met properly rather than
        # approximately — with all four faces present. Two details are load-bearing, both measured:
        #   * BY FILE, not by name. `mainfont=TeX Gyre Heros` FAILS under Tectonic (no fontconfig,
        #     so fontspec cannot resolve a family name); the Extension/UprightFont/BoldFont/... form
        #     is what works.
        #   * REPRODUCIBLE. All four faces ship inside the PINNED Tectonic bundle
        #     (texgyreheros-{regular,bold,italic,bolditalic}.otf, verified present in the
        #     content-addressed cache) — no system font file, so Priority 5 holds. `mainfont=Arial`
        #     also works and is REFUSED for exactly that reason: Arial is a Windows system font and
        #     the build would stop being reproducible off this box.
        # Certified on the real 230-page deliverable, not on a minimal case; the document runs a
        # little longer than under LM Sans because Heros is wider, and page count is not a graded
        # limit (the 10,000 WORDS are).
        "-V", "linestretch=1.5",
        "-V", "mainfont=texgyreheros",
        "-V", "mainfontoptions=Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,"
              "ItalicFont=*-italic,BoldItalicFont=*-bolditalic",
        "-V", "linkcolor=blue",
        "-V", "urlcolor=blue",
        "--metadata", "link-citations=true",
        "-o", str(pdf_path),
    ]
    print(f"[build_paper] pandoc -> {pdf_path}")
    # Tectonic's TeX-package cache goes to D: — C: ran to 0 bytes free on the first-ever compile
    # (2026-07-02, os error 112) and the cache (~hundreds of MB) does not belong on the full system
    # drive. TECTONIC_CACHE_DIR is tectonic's supported cache override; the cache is regenerable.
    env = dict(os.environ)
    env.setdefault("TECTONIC_CACHE_DIR", r"D:\tectonic-cache")
    # F-19: record + CHECK the bundle the typeface resolves from (see tectonic_bundle_provenance).
    _bundle = tectonic_bundle_provenance(Path(env["TECTONIC_CACHE_DIR"]))
    if _bundle["digest"]:
        print(f"[build_paper] tectonic bundle {_bundle['digest'][:16]}… "
              f"({len(_bundle['faces_present'])}/4 TeX Gyre Heros faces present)")
    else:
        print(f"[build_paper] tectonic bundle: UNKNOWN — {_bundle.get('reason', 'not resolved')}",
              file=sys.stderr)
    if _bundle["faces_missing"] and _bundle["digest"]:
        print(f"[build_paper] WARNING: Heros face(s) absent from the bundle: "
              f"{', '.join(_bundle['faces_missing'])}. `mainfont` will silently fall back and the "
              f"document will lose those shapes — the exact 2026-08-01 defect.", file=sys.stderr)
    # encoding/errors are LOAD-BEARING, not tidiness: without them Python decodes this channel with
    # the box's locale codec and a single non-decodable byte silently empties it. See _MISSING_CHAR_RE.
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          cwd=str(REPO), env=env)
    # ⚠ `or ""` here is a CONVENIENCE, and it is the idiom that hid the original defect: when the
    # decode fails the attribute comes back as None, and `or ""` turns "never measured" into
    # "measured and empty". Keep the two apart explicitly before collapsing them.
    if proc.stderr is None or proc.stdout is None:
        print("[build_paper] WARNING: a diagnostic channel came back as None — the pipe was not "
              "decoded. Any 'no warnings' summary below is UNMEASURED, not clean.", file=sys.stderr)
    channel = (proc.stderr or "") + "\n" + (proc.stdout or "")
    if len(channel.strip()) == 0:
        print("[build_paper] WARNING: pandoc+tectonic emitted NO diagnostics at all over a "
              "multi-hundred-page compile. That is not a clean build, it is an unread channel — "
              "check the encoding= argument on the subprocess call before trusting this run.",
              file=sys.stderr)
    # Surface every warning: a citeproc "reference not found" in the PDF is a grading defect.
    warnings, missing = scan_diagnostics(channel)
    for ln in warnings:
        print(f"[pandoc] {ln}", file=sys.stderr)
    if proc.returncode != 0:
        tail = "\n".join(channel.splitlines()[-25:])
        print(f"[build_paper] FAILED (exit {proc.returncode}):\n{tail}", file=sys.stderr)
        return proc.returncode
    size_kb = pdf_path.stat().st_size // 1024
    print(f"[build_paper] pandoc/tectonic: {len(channel)} chars of diagnostics, "
          f"{len(warnings)} warning/error line(s)")

    # ---- the two glyph gates, run on the DELIVERABLE that was just written ------------------
    if missing:
        chars = sorted({(m.group(1) or m.group(3)).upper()
                        for ln in missing if (m := _MISSING_CHAR_RE.search(ln))})
        print(f"[build_paper] FAILED: the engine could not typeset {len(missing)} character "
              f"occurrence(s) — they are SILENTLY ABSENT from {pdf_path.name}. "
              f"Codepoints: {', '.join('U+' + c for c in chars) or '(unparsed)'}", file=sys.stderr)
        for ln in missing[:30]:
            print(f"  {ln}", file=sys.stderr)
        print("  fix: use the LaTeX form ($\\alpha$, $\\approx$, $\\geq$ …) rather than the literal "
              "character, or declare it in the preamble; the fonts here carry no Greek/relational "
              "glyphs in TEXT mode.", file=sys.stderr)
        return 4
    ffff, status = verify_pdf_glyphs(pdf_path)
    cross_check = "0 U+FFFF markers (2nd route)"
    if status != "ok":
        cross_check = f"2nd route {status}"
        print(f"[build_paper] glyph cross-check {status} — the engine gate above passed, but this "
              f"run has ONE route of evidence, not two.", file=sys.stderr)
    elif ffff:
        print(f"[build_paper] FAILED: {ffff} unmappable glyph marker(s) (U+FFFF) in the extracted "
              f"text of {pdf_path.name}. The engine reported no missing character, so these RENDER "
              f"but carry no ToUnicode mapping — the PDF is not text-searchable at those points and "
              f"a copy-paste of the passage loses them.", file=sys.stderr)
        return 5
    print(f"[build_paper] OK: {pdf_path} ({size_kb} KB); 0 missing characters; {cross_check}")
    return 0


#: S13 (2026-07-06): editorial placeholders/markers that must NEVER reach the submitted PDF. The
#: --final gate greps the ASSEMBLED deliverable for them and refuses; ~40 legitimately live in the
#: chapters today as fill-at-campaign contracts.
#: ⚠ 2026-07-26/27 (deep review, loops 107-108, #85/#86): the marker vocabulary is NOT closed — chapters
#: invent their own wording, and anything the gate does not know ships silently. MEASURED, three distinct
#: spellings of the SAME fill-at-campaign marker across the assembled chapters:
#:   `FRONT_MATTER.md:149,161`  "[RESULT — campaign slot.]"                        (the original)
#:   `CH7_…conclusion.md:40`    "[Result — finalise from the confirmatory campaign.]"
#:   `CH1_introduction.md:156`  "[Result — to be finalised from the confirmatory campaign.]"
#: Loop 107 added the CH7 spelling as a LITERAL; loop 108 found that was still too narrow — "finalise"
#: does not match "finalised", so CH1 §1.4's prototype-sourced result paragraph (in the INTRODUCTION)
#: stayed invisible. Replaced with a FAMILY pattern: a bracketed Result/RESULT marker followed, within the
#: same brackets, by "campaign" or "slot". That covers all three spellings and any future one.
#: The case-insensitivity is SCOPED to this alternative — making the whole regex case-insensitive would
#: make "FROM CAMPAIGN" match the ordinary prose phrase "from the campaign", firing on legitimate
#: sentences and training the operator to ignore the gate.
_PLACEHOLDER_RE = re.compile(
    r"FROM CAMPAIGN|Compile note|Status: structural scaffold|WORD COUNT: fill"
    r"|RESULT — campaign slot|CONFIRM AT COMPILE|INSERT AT SUBMISSION|TAMER: pick at compile"
    r"|\[from §6\]|\[in/out\]"
    r"|(?i:\[results?\b[^\]]{0,80}(?:campaign|slot))"
)


def final_lint(md_path: Path) -> int:
    """The submission gate: exit non-zero if any editorial placeholder survives in the deliverable."""
    text = md_path.read_text(encoding="utf-8")
    hits: list[str] = []
    for i, line in enumerate(text.splitlines(), 1):
        m = _PLACEHOLDER_RE.search(line)
        if m:
            hits.append(f"  line {i}: {m.group(0)!r} in: {line.strip()[:90]}")
    if hits:
        print(f"[build_paper] --final FAILED: {len(hits)} editorial placeholder(s) still in the deliverable:")
        for h in hits[:40]:
            print(h)
        return 1
    print("[build_paper] --final lint clean: no editorial placeholders in the deliverable.")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Assemble + compile the dissertation PDF.")
    ap.add_argument("--md-only", action="store_true", help="assemble the markdown only (no pandoc)")
    ap.add_argument("--out", type=Path, default=None, help="output PDF path")
    ap.add_argument("--final", action="store_true",
                    help="submission lint (S13): FAIL if the assembled deliverable still carries any "
                         "editorial placeholder (FROM CAMPAIGN / compile notes / fill slots) — the P8 "
                         "gate before the upload.")
    args = ap.parse_args(argv)
    # F-18 (coord, 2026-08-01): `--md-only --final` returned rc=0 HAVING COMPILED NOTHING. --final is
    # the SUBMISSION gate; satisfying it without ever producing a PDF is a false green of exactly the
    # class this file spent today fixing, and it is the most dangerous one here because the thing it
    # would wave through is the deliverable itself. The two flags are contradictory by construction:
    # --md-only stops before pandoc, --final certifies the compiled artefact. Refuse the combination
    # rather than silently honouring the weaker half.
    if args.final and args.md_only:
        print("[build_paper] REFUSING --final with --md-only: --final is the submission gate and "
              "certifies the COMPILED deliverable, while --md-only exits before pandoc. Passing "
              "both would return rc=0 having produced no PDF. Run --final on its own.",
              file=sys.stderr)
        return 2
    try:  # the lint echoes deliverable lines (unicode arrows etc.) — never crash on a legacy codepage
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    except Exception:  # noqa: BLE001
        pass
    rc = build(md_only=args.md_only, out=args.out)
    if rc == 0 and args.final:
        rc = final_lint(REPO / "paper" / "_build" / "dissertation.md")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
