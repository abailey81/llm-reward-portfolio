#!/usr/bin/env python3
"""UCL word-budget compliance — count the MAIN-BODY PROSE against the hard 10,000-word limit.

Why this exists
---------------
IFTE0008 sets a hard **10,000-word main-body prose** limit, EXCLUDING math/equations, code,
figures/tables, footnotes, references, the abstract, and appendices (the escape hatch). The body
was last hand-estimated at ~11.5k (2026-06-30) — over budget — and every write-time decision
("push the formal apparatus into excluded math", "move X to an appendix") needs a NUMBER, not a
guess. This tool applies the exclusion rules mechanically and reports per-chapter + total, so
compliance is measurable at every edit instead of discovered at submission.

Counting conventions (deliberate, documented, conservative-where-ambiguous)
---------------------------------------------------------------------------
EXCLUDED (per the UCL rules): fenced code blocks; inline code spans; display math ($$..$$,
\\[..\\], LaTeX equation environments); inline math ($..$); markdown tables (| rows and
separator lines); footnote definitions; HTML comments; image/figure lines. FRONT_MATTER.md is
excluded wholesale (cover/abstract/acknowledgements/lists are all outside the limit).
COUNTED: headings and blockquote prose (theorem statements in words are prose — conservative),
and each citation group ([`key`; ...] -> rendered "(Author, Year)") as **1 word** — a slight
undercount vs the rendered text, which is why the tool's PASS ceiling is **9,500** (5% headroom
below the true 10,000 gate; WARN in 9,500-10,000; FAIL above 10,000).

Usage
-----
    python scripts/word_budget.py                # count the real chapters
    python scripts/word_budget.py --limit 10000  # override the gate (default 10000)

Exit code: 0 PASS/WARN (advisory band), 1 FAIL (over the hard limit) — usable as a CI gate.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: Body chapters that count toward the limit (FRONT_MATTER + appendices excluded by the rules;
#: keep in sync with scripts/build_paper.py ASSEMBLY).
BODY_CHAPTERS: tuple[str, ...] = (
    "CH1_introduction.md",
    "CH2_related_work.md",
    "02_CHAPTER_theory.md",
    "CH4_methods.md",
    "CH5_prototype.md",
    "CH6_results.md",
    "CH7_discussion_limitations_conclusion.md",
)

#: In-file appendices are word-excluded (the UCL escape hatch): truncate a chapter at the first
#: heading that declares itself an appendix marked "word-excluded" (e.g. CH7's Appendix B).
_APPENDIX_CUT_RE = re.compile(r"^#{1,6}\s+Appendix\b.*word-excluded", re.MULTILINE | re.IGNORECASE)
_CITE_GROUP_RE = re.compile(r"\[(?:`[A-Za-z0-9_:.+-]+`)(?:\s*;\s*`[A-Za-z0-9_:.+-]+`)*\]")
_DISPLAY_MATH_RE = re.compile(r"\$\$.*?\$\$|\\\[.*?\\\]|\\begin\{(equation|align|gather)\*?\}.*?\\end\{\1\*?\}",
                              re.DOTALL)
_INLINE_MATH_RE = re.compile(r"(?<!\$)\$(?!\$)[^$\n]+\$(?!\$)")
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_FOOTNOTE_DEF_RE = re.compile(r"^\[\^[^\]]+\]:.*$", re.MULTILINE)
_IMAGE_LINE_RE = re.compile(r"^!\[[^\]]*\]\([^)]*\).*$", re.MULTILINE)
_WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’\-]*")


def strip_excluded(md: str) -> str:
    """Remove every UCL-excluded region from raw chapter markdown, leaving countable prose.

    Order matters: fenced code first (their content must not be seen by later regexes), then
    display math (can span lines), then tables (line-wise), then the inline/comment classes.
    Each citation GROUP is replaced by the single token ``CITE`` (counts as one word — see the
    module docstring for why the PASS ceiling holds 5% headroom against this undercount).
    """
    # Word-excluded in-file appendix: everything from its heading onward is outside the limit.
    cut = _APPENDIX_CUT_RE.search(md)
    if cut:
        md = md[: cut.start()]

    # Fenced code blocks (``` or ~~~), line-wise so an unterminated fence still drops its tail.
    lines: list[str] = []
    in_fence = False
    for line in md.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    text = "\n".join(lines)

    text = _HTML_COMMENT_RE.sub(" ", text)
    text = _DISPLAY_MATH_RE.sub(" ", text)
    text = _CITE_GROUP_RE.sub(" CITE ", text)  # before inline-code (keys are backticked)
    text = _INLINE_MATH_RE.sub(" ", text)
    text = _INLINE_CODE_RE.sub(" ", text)
    text = _FOOTNOTE_DEF_RE.sub(" ", text)
    text = _IMAGE_LINE_RE.sub(" ", text)

    # Tables: drop any line that is a table row or separator (starts with '|' after indent).
    text = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("|"))
    return text


def count_words(md: str) -> int:
    """Word count of the countable prose (see :func:`strip_excluded` for the conventions)."""
    return len(_WORD_RE.findall(strip_excluded(md)))


def report(chapter_dir: Path, limit: int = 10_000, pass_ceiling: int = 9_500) -> dict[str, object]:
    """Per-chapter + total main-body word counts with the PASS/WARN/FAIL verdict."""
    per: dict[str, int] = {}
    for name in BODY_CHAPTERS:
        p = chapter_dir / name
        per[name] = count_words(p.read_text(encoding="utf-8")) if p.is_file() else -1
    total = sum(v for v in per.values() if v >= 0)
    status = "PASS" if total <= pass_ceiling else ("WARN" if total <= limit else "FAIL")
    return {"per_chapter": per, "total": total, "limit": limit,
            "pass_ceiling": pass_ceiling, "status": status}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="UCL 10k main-body word-budget check.")
    ap.add_argument("--limit", type=int, default=10_000)
    ap.add_argument("--pass-ceiling", type=int, default=9_500)
    args = ap.parse_args(argv)
    r = report(REPO / "paper", limit=args.limit, pass_ceiling=args.pass_ceiling)
    print(f"{'chapter':<45} {'words':>7}")
    for name, n in r["per_chapter"].items():  # type: ignore[union-attr]
        print(f"{name:<45} {n:>7}")
    print(f"{'TOTAL (main body)':<45} {r['total']:>7}   "
          f"[{r['status']}] limit={r['limit']} (PASS ceiling {r['pass_ceiling']})")
    return 1 if r["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
