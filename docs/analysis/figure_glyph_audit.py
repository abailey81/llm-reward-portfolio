"""Every character the figure suite prints, checked against the typeface that has to print it.

WHY THIS GATE EXISTS
--------------------
When the figures moved to the document's own typeface (TeX Gyre Heros) on 2026-08-12, one
character stopped rendering: the subset sign in Figure 1.2's branch label "TOST U+2282 +-SESOI".
Heros carries no U+2282, so matplotlib substituted `.notdef` and drew an empty rectangle.

NOTHING IN THE PROJECT CAUGHT IT.

* `scripts/build_paper.py` has a missing-character gate, and it reads the TeX ENGINE's diagnostic
  channel. The engine typesets the prose. It never looks inside a figure, which arrives as a
  finished raster or as vector drawing operators.
* matplotlib emits a `UserWarning` for a missing glyph, which is swallowed by every script that
  does not configure warnings, and none did.
* The compiled PDF still extracts the ORIGINAL character, because the ToUnicode map records what
  was requested rather than what was drawn. So even reading the artefact's text does not show it.

The defect was therefore visible only to a person looking at the picture. This module makes it
visible to a command instead: it collects every string literal the figure modules print and tests
each character against the four Heros faces' own `cmap` tables.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
It does not parse f-strings or computed labels, so it is a LOWER BOUND on coverage rather than a
proof. That is stated rather than hidden. It catches the class of defect that actually occurred,
which is a hand-typed mathematical or typographic symbol in a literal label.

    python docs/analysis/figure_glyph_audit.py
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    # The console here is cp1251, so printing the very characters this module exists to inspect
    # raises UnicodeEncodeError and the gate dies before reporting anything.
    try:
        _s.reconfigure(encoding="utf-8", errors="backslashreplace")
    except (AttributeError, ValueError):  # pragma: no cover
        pass

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

FONT_DIR = REPO / "docs" / "figures" / "fonts"

#: The modules that write the eighteen figures the compiled PDF actually embeds. Verified against
#: the assembled deliverable's own image list rather than assumed: every `![](...)` path in
#: `paper/_build/dissertation.md` resolves to a file one of these writes.
SOURCES: tuple[Path, ...] = (
    REPO / "docs" / "analysis" / "render_schematics_legible.py",
    REPO / "docs" / "analysis" / "render_results_figures.py",
    REPO / "docs" / "analysis" / "render_cost_surface.py",
    REPO / "docs" / "analysis" / "render_benchmark_ladder.py",
    REPO / "docs" / "analysis" / "render_reward_response.py",
    REPO / "docs" / "analysis" / "render_rl_loop.py",
    REPO / "docs" / "analysis" / "render_f3_legible.py",
)

#: Scanned and REPORTED, but not allowed to fail the gate. Both are drift-fenced under `src/**`, so
#: they cannot be corrected from here, and neither writes a figure the deliverable embeds:
#: `schematics.prediction_branch` is the fenced twin of the F2 builder in
#: `render_schematics_legible` (which is what `build_all` calls), and `figures.equivalence_forest`
#: and the Bayes-factor panel are report-only exhibits that reach no page. Recorded rather than
#: dropped, because "it does not ship today" is a fact with a shelf life.
ADVISORY: tuple[Path, ...] = (
    REPO / "src" / "viz" / "schematics.py",
    REPO / "src" / "viz" / "figures.py",
)

#: Characters that never reach a Text artist even though they occur in a literal: they are matplotlib
#: format codes, path separators or mathtext markup that the renderer consumes rather than prints.
IGNORE = set("\n\t\r")


def font_charset() -> set[int]:
    """The union of the four faces' cmaps, as codepoints."""
    from fontTools.ttLib import TTFont

    chars: set[int] = set()
    for otf in sorted(FONT_DIR.glob("texgyreheros-*.otf")):
        with TTFont(str(otf), lazy=True) as f:
            for table in f["cmap"].tables:
                chars.update(table.cmap.keys())
    if not chars:
        raise FileNotFoundError(f"no faces found under {FONT_DIR}")
    return chars


def literals(path: Path) -> list[tuple[int, str]]:
    """(line number, value) for every string constant in one module, docstrings excluded.

    A module docstring is documentation, not a label, and this file's own header would otherwise
    report itself.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    doc_nodes = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                doc_nodes.add(id(body[0].value))
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in doc_nodes:
            out.append((node.lineno, node.value))
    return out


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    charset = font_charset()
    print(f"TeX Gyre Heros covers {len(charset)} codepoints across four faces")

    problems: list[str] = []
    advisory: list[str] = []
    seen_ok: set[str] = set()
    for src in (*SOURCES, *ADVISORY):
        if not src.is_file():
            print(f"  !! {src.relative_to(REPO)} absent, skipped")
            continue
        sink = problems if src in SOURCES else advisory
        for lineno, text in literals(src):
            for ch in text:
                if ch in IGNORE or ord(ch) < 0x80:
                    continue
                if ord(ch) in charset:
                    seen_ok.add(ch)
                    continue
                sink.append(
                    f"{src.relative_to(REPO)}:{lineno}  U+{ord(ch):04X} {ch!r} in {text[:56]!r}")

    if advisory:
        print(f"\n  advisory ({len(advisory)}), in drift-fenced modules that write no embedded "
              f"figure:")
        for a in advisory:
            print("    " + a)

    if seen_ok:
        print("  non-ASCII characters used and COVERED: "
              + " ".join(sorted(seen_ok, key=ord)))
    if problems:
        print(f"\nGLYPH AUDIT FAILED: {len(problems)} character occurrence(s) the typeface cannot "
              f"draw. matplotlib renders each as an empty rectangle and warns to a channel nobody "
              f"reads.\n")
        for p in problems:
            print("  " + p)
        return 1
    print("\nGLYPH AUDIT CLEAN: every non-ASCII character in the figure sources exists in the "
          "document's typeface.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
