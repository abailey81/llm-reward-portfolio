#!/usr/bin/env python3
"""Citation-integrity check for paper/ (READ-ONLY; mutates nothing).

Cross-checks the bibkeys CITED in the chapter markdown against ``paper/refs.bib`` and
reports four integrity problems, in priority order:

  1. DANGLING  — a key cited in prose with NO entry in refs.bib (a broken/hallucinated cite).
  2. VERIFY-IN-USE — a refs.bib entry still flagged ``% VERIFY`` whose key IS cited in prose
     (an unconfirmed reference about to enter the compiled PDF — the supervisor co-authored
     corpus papers, so an unverified cite is a direct integrity risk).
  3. LITERAL-VERIFY — the literal token ``VERIFY`` leaking into chapter prose (a stray marker).
  4. UNUSED    — a refs.bib entry never cited (informational only; harmless).

Citation convention (verified): keys appear as inline-code spans, e.g. [`ma2024eureka`] or
[`ma2024eureka`, §3.3]. We extract backtick spans shaped like a bibkey (author+year+word).

Exit code 0 always (advisory report). Use ``--strict`` to exit 1 when DANGLING or
VERIFY-IN-USE problems exist (for CI). Stdlib only.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

#: A bibkey looks like ``author + 4-digit-year + optional suffix`` (e.g. ma2024eureka, heavytailsDM2026,
#: fisslerziegelgneiting2015). Character classes MIRROR build_paper.py's ``_KEY_RE`` so this integrity guard
#: sees exactly the key set the build resolves — uppercase and bare-year-ending keys included (F-F2, 2026-07-04).
_BIBKEY = re.compile(r"^[A-Za-z][A-Za-z0-9_.+-]*\d{4}[A-Za-z0-9_:.+-]*$")
#: An inline-code span in markdown: `...`
_CODE_SPAN = re.compile(r"`([^`]+)`")
#: A bib entry header: @type{key,
_BIB_HEADER = re.compile(r"^@\w+\{\s*([^,\s]+)\s*,", re.MULTILINE)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def bib_entries(bib_text: str) -> dict[str, bool]:
    """Map each bibkey -> whether its entry block is flagged VERIFY.

    Entries are split on ``@``; the key is the header's first token, and an entry is
    'VERIFY' if the token ``VERIFY`` appears anywhere in its block.
    """
    out: dict[str, bool] = {}
    for block in re.split(r"(?m)^(?=@)", bib_text):
        block = block.strip()
        if not block:
            continue
        m = _BIB_HEADER.search(block)
        if not m:
            continue
        out[m.group(1)] = "VERIFY" in block
    return out


#: A citation in the COMPILED PDF, i.e. what `build_paper.rewrite_citations` actually emits.
_EMITTED_CITE = re.compile(r"@([A-Za-z][A-Za-z0-9_.+-]*\d{4}[A-Za-z0-9_:.+-]*)")


def cited_keys(chapter_texts: dict[str, str]) -> dict[str, list[str]]:
    """Map each cited bibkey -> the shipped files it appears in.

    ★ 2026-08-01 (RUN 10). This used to scan EVERY code span and test it against `_BIBKEY`, with no
    requirement that it sit inside a `[...]` group and no awareness of fenced code blocks. The
    BUILDER only rewrites backticked keys INSIDE brackets and outside fences, so the two disagreed
    about what a citation is — the checker could flag a token that never becomes a citation.

    That mattered the moment item 15a-i wired the `tables/` files in: a bare model pin in a table
    cell, `` `claude-haiku-4-5-20251001` ``, was reported as a DANGLING citation. It is not a
    citation at all — no brackets, so `rewrite_citations` leaves it alone and it never reaches
    citeproc. Widening the scan without fixing this would have poured false dangling keys into the
    one gate that guards citation integrity, which is the cry-wolf failure in its purest form.

    **The fix is to stop having a second definition.** We run the BUILDER'S OWN transform and read
    the citations out of its output, so the checker measures exactly what ships and the two cannot
    diverge again. `rewrite_citations` already handles fenced code blocks, so fences come for free.
    """
    from build_paper import rewrite_citations                  # noqa: PLC0415 - deliberate late import

    out: dict[str, list[str]] = {}
    for fname, text in chapter_texts.items():
        for raw in _EMITTED_CITE.findall(rewrite_citations(text)):
            # ⚠ TRAILING punctuation is NOT part of the key. Pandoc treats only INTERNAL punctuation
            # as part of a citation key, so `[@blackwell1953equivalent.]` cites `...equivalent` and
            # leaves the period as text. Without this strip the checker reported a DANGLING key that
            # renders perfectly well -- my own false positive, caught by reading the source line
            # rather than trusting the alarm (the period is inside the bracket group in
            # 02_CHAPTER_theory.md:150, which is legal and harmless).
            key = raw.rstrip(".,;:")
            out.setdefault(key, [])
            if fname not in out[key]:
                out[key].append(fname)
    return out


def unrendered_bibkey_lookalikes(chapter_texts: dict[str, str]) -> dict[str, list[str]]:
    """Backticked tokens that LOOK like bibkeys but will NOT render as citations.

    Kept as an ADVISORY rather than dropped, because the narrowing above could otherwise hide a
    real defect: a citation the author wrote WITHOUT brackets is silently not a citation in the
    PDF, and the old scan was the only thing that would have noticed. Reported, never fatal —
    almost every hit is a legitimate model pin, filename or hash in a table.
    """
    from build_paper import rewrite_citations                  # noqa: PLC0415

    out: dict[str, list[str]] = {}
    for fname, text in chapter_texts.items():
        emitted = set(_EMITTED_CITE.findall(rewrite_citations(text)))
        for span in _CODE_SPAN.findall(text):
            tok = span.strip()
            if _BIBKEY.match(tok) and tok.rstrip(".,;:") not in {e.rstrip(".,;:") for e in emitted}:
                out.setdefault(tok, [])
                if fname not in out[tok]:
                    out[tok].append(fname)
    return out


def literal_verify(chapter_texts: dict[str, str]) -> dict[str, int]:
    """Map chapter -> count of literal 'VERIFY' tokens leaking into prose."""
    out: dict[str, int] = {}
    for fname, text in chapter_texts.items():
        n = len(re.findall(r"VERIFY", text))
        if n:
            out[fname] = n
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Read-only citation-integrity check for paper/.")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if DANGLING or VERIFY-IN-USE problems exist (for CI)")
    args = ap.parse_args(argv)

    root = repo_root()
    paper = root / "paper"
    bib_path = paper / "refs.bib"
    if not bib_path.is_file():
        print(f"[citations] refs.bib not found at {bib_path}", file=sys.stderr)
        return 0

    entries = bib_entries(bib_path.read_text(encoding="utf-8", errors="ignore"))
    # Shipped prose = every file `build_paper.py` actually assembles.
    #
    # ★ 2026-08-01 (RUN 10, DEFERRED item 15e). This globbed `paper/*.md` TOP LEVEL ONLY, which was
    # correct while the build assembled only top-level chapters. Item 15a-i wired nine further
    # artefacts into the PDF — seven `tables/` files and `appendices/A_quality_control_record.md` —
    # and those carry **79 cite-references** between them. Left unwidened, this gate would have
    # scanned none of them: dangling keys and un-verified references would have gone into the
    # compiled PDF while the integrity check reported CLEAN. That is why the write-up lane made
    # landing the two changes in the SAME commit a condition, and they were right.
    #
    # The scope is now DERIVED from the build, not maintained in parallel, so a future ASSEMBLY
    # entry cannot escape the gate by being forgotten here.
    _shipped: list[Path] = []
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from build_paper import APPENDICES, ASSEMBLY          # noqa: PLC0415 - deliberate late import
        _shipped = [paper / rel for rel in (*ASSEMBLY, *APPENDICES)]
    except Exception:                                          # noqa: BLE001
        # FAIL LOUD-ish: fall back to a WIDER scan than before, never a narrower one. A gate that
        # silently reverts to top-level-only is the exact hole this change closes.
        print("[citations] WARNING: could not import build_paper's ASSEMBLY; falling back to a "
              "recursive paper/**.md scan (wider, never narrower)", file=sys.stderr)
        _shipped = sorted(paper.rglob("*.md"))
    chapters = {
        str(p.relative_to(paper)).replace("\\", "/"): p.read_text(encoding="utf-8", errors="ignore")
        for p in _shipped
        if p.is_file() and "DOSSIER" not in p.name and "MANIFEST" not in p.name
    }
    cited = cited_keys(chapters)

    dangling = sorted(k for k in cited if k not in entries)
    verify_in_use = sorted(k for k in cited if entries.get(k) is True)
    unused = sorted(k for k in entries if k not in cited)
    leaks = literal_verify(chapters)

    print(f"[citations] {len(entries)} bib entries | {len(cited)} distinct keys cited "
          f"across {len(chapters)} chapters\n")

    print(f"1. DANGLING (cited, no bib entry): {len(dangling)}")
    for k in dangling:
        print(f"   - {k}  (in {', '.join(cited[k])})")

    print(f"\n2. VERIFY-IN-USE (cited but still % VERIFY): {len(verify_in_use)}")
    for k in verify_in_use:
        print(f"   - {k}  (in {', '.join(cited[k])})")

    print(f"\n3. LITERAL 'VERIFY' in chapter prose: {sum(leaks.values())} across {len(leaks)} files")
    for f, n in sorted(leaks.items()):
        print(f"   - {f}: {n}")

    print(f"\n4. UNUSED bib entries (informational): {len(unused)}")

    # 2026-08-01 (RUN 10): ADVISORY, never fatal. Backticked tokens that look like bibkeys but sit
    # outside a `[...]` group, so `rewrite_citations` leaves them alone and they never become
    # citations. Almost all are legitimate model pins / filenames / hashes in the wired tables.
    # Reported so the narrowing of `cited_keys` cannot hide a citation someone wrote WITHOUT
    # brackets — which would silently not be a citation in the PDF.
    lookalikes = unrendered_bibkey_lookalikes(chapters)
    print(f"5. BIBKEY-SHAPED but NOT rendered as citations (advisory): {len(lookalikes)}")
    for k in sorted(lookalikes)[:6]:
        print(f"   - {k}  (in {', '.join(lookalikes[k])})")
    if len(lookalikes) > 6:
        print(f"   ... and {len(lookalikes) - 6} more")

    problems = bool(dangling or verify_in_use)
    print(f"\n[citations] {'PROBLEMS FOUND' if problems else 'clean on dangling + verify-in-use'}.")
    if problems and not args.strict:
        print("[citations] NOTE: exiting 0 because --strict was not passed. A gate that reports a "
              "problem and returns success cannot fail a pipeline — pass --strict in any automated "
              "caller. (Recorded 2026-08-01; the default is left unchanged so no existing caller's "
              "behaviour moves silently.)")
    if args.strict and problems:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
