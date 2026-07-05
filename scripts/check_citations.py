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


def cited_keys(chapter_texts: dict[str, str]) -> dict[str, list[str]]:
    """Map each cited bibkey -> the chapter files it appears in."""
    out: dict[str, list[str]] = {}
    for fname, text in chapter_texts.items():
        for span in _CODE_SPAN.findall(text):
            tok = span.strip()
            if _BIBKEY.match(tok):
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
    # Chapter prose = paper/*.md, excluding the bibliography dossier and manifests.
    chapters = {
        p.name: p.read_text(encoding="utf-8", errors="ignore")
        for p in sorted(paper.glob("*.md"))
        if "DOSSIER" not in p.name and "MANIFEST" not in p.name and "NOMENCLATURE" not in p.name
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

    problems = bool(dangling or verify_in_use)
    print(f"\n[citations] {'PROBLEMS FOUND' if problems else 'clean on dangling + verify-in-use'}.")
    if args.strict and problems:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
