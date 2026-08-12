"""Generate paper/appendices/F_prompts_and_authored_code.md from the REAL frozen sources.

Every block is read from the artefact it claims to quote: the hash-bound prompt files, the live
reflection preamble in src/llm/loop.py, and reward programs from the executed campaign archive.
Nothing here is hand-transcribed. Prints the paths it read.
"""
from __future__ import annotations

import difflib
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]   # <repo>/paper/appendices/ -> <repo>
OUT = REPO / "paper" / "appendices" / "F_prompts_and_authored_code.md"
ARCH = REPO / "outputs" / "campaign_cluster_run4" / "search" / "distributional"

# The corpus renders authored code at ~7pt (Eureka App. G). We wrap the blocks in \footnotesize,
# which lets far more of each line survive unwrapped. WIDTH is set from the PDF measurement below.
#
# ⚠ WRAP WAS 96 AND THAT OVERRAN THE PAGE, silently, on four pages of this appendix. The number
# has to come from the rendered artefact, not from a habit, so here is the measurement it comes
# from. The code fences start at the document's left margin, x0 = 70.87pt, and the text column
# ends at 524.38pt on a 595.28pt A4 page, giving 453.51pt of usable width. At \footnotesize the
# listing font is LMMono10-Regular, whose advance is a measured 5.2304pt per character, uniform
# across every glyph in these blocks. So the column holds 453.51 / 5.2304 = 86.7 characters, and
# 96 of them ran 48.6pt past the edge -- the tail of each over-long prompt line simply never
# reached the page. 85 leaves 8.9pt of slack, which absorbs any glyph that falls back to a wider
# font, and it costs only eleven extra wrapped lines across all four blocks.
#
# ⚠ EVERY BLOCK MUST THEREFORE SIT INSIDE SMALL_OPEN/SMALL_CLOSE, because WRAP is calibrated to
# the \footnotesize metric and to nothing else. F.3 was the one block that did not, and at the
# 12pt body metric (6.155pt per character, so 73 characters to the column) its 84-character
# reflection sentence ran 63.7pt off the page while every other block sat comfortably inside it.
#
# ⚠ THE WRAPPING IS A LAYOUT CHANGE AND MUST STAY ONE. This appendix is evidence: the study
# measures prompt length to the character, so `reflow` may insert line breaks and indent
# padding for display and may NOT alter any non-whitespace character. That invariant is
# asserted below rather than trusted.
WRAP = 85
SMALL_OPEN = "\\begingroup\\footnotesize"
SMALL_CLOSE = "\\endgroup"


def read(p: Path) -> str:
    print(f"  READ {p}  ({p.stat().st_size} bytes)")
    return p.read_text(encoding="utf-8")


def _bare(s: str) -> str:
    """The evidence-bearing content of `s`: every non-whitespace character, in order."""
    return "".join(s.split())


def reflow(text: str, width: int = WRAP) -> tuple[str, int]:
    """Hard-wrap over-long lines so nothing overflows the page. Returns (text, n_wrapped).

    Wrapping is presentation. It inserts line breaks and hanging-indent padding, and it drops the
    single space it breaks at. It must never touch a non-whitespace character, because this
    appendix is the study's verbatim evidence and prompt length is measured to the character.
    That is asserted per line below, not assumed: a dropped tail or a stray hyphen would otherwise
    reach the PDF looking exactly like a legitimate wrap.
    """
    out, wrapped = [], 0
    for ln in text.splitlines():
        if len(ln) <= width:
            out.append(ln)
            continue
        wrapped += 1
        mark = len(out)
        indent = len(ln) - len(ln.lstrip())
        pad = " " * (indent + 4)
        cur = ln
        while len(cur) > width:
            cut = cur.rfind(" ", 0, width)
            if cut <= indent:
                cut = width
            out.append(cur[:cut])
            cur = pad + cur[cut:].lstrip()
        out.append(cur)
        if _bare("".join(out[mark:])) != _bare(ln):
            raise AssertionError(
                "reflow altered the evidence, which is a defect and not a layout choice.\n"
                f"  in : {ln!r}\n  out: {out[mark:]!r}")
    return "\n".join(out), wrapped


def source_of(name: str) -> tuple[str, dict]:
    rec = json.loads(read(ARCH / name / "record.json"))
    return (rec.get("reward_source") or ""), rec


def main() -> int:
    print("SOURCES READ:")
    system = read(REPO / "prompts" / "system.txt").rstrip()
    initial = read(REPO / "prompts" / "initial_generation.txt").rstrip()
    loop_src = read(REPO / "src" / "llm" / "loop.py")
    m = re.search(r"_REFLECTION_PREAMBLE = \(\s*(.*?)\s*\)\n", loop_src, re.S)
    # The constant is written as adjacent string literals; Python concatenates them with NO
    # separator, so joining with a space would silently insert one that the model never saw.
    preamble = "".join(re.findall(r'"([^"]*)"', m.group(1))) if m else "<NOT FOUND>"
    preamble, _ = reflow(preamble)

    g0, r0 = source_of("distributional-g0-c0")
    g1, r1 = source_of("distributional-g1-c0")

    sys_w, n1 = reflow(system)
    ini_w, n2 = reflow(initial)
    g0_w, n3 = reflow(g0.rstrip())
    g1_w, n4 = reflow(g1.rstrip())
    print(f"  lines hard-wrapped to fit the page: system {n1}, initial {n2}, g0 {n3}, g1 {n4}")

    diff = list(difflib.unified_diff(
        g0.splitlines(), g1.splitlines(),
        fromfile="generation 0 (no feedback yet)", tofile="generation 1 (after tail feedback)",
        lineterm="", n=2))
    diff_w, n5 = reflow("\n".join(diff))
    print(f"  diff lines: {len(diff)} (wrapped {n5})")

    SO, SC = SMALL_OPEN, SMALL_CLOSE
    doc = f"""<!-- ⚠ THIS FILE IS NOT YET WIRED INTO THE BUILD, so it does NOT appear in the compiled PDF.
     TO WIRE IT: add, as the LAST entry of `APPENDICES` in scripts/build_paper.py:
         "appendices/F_prompts_and_authored_code.md",
     Appending LAST takes the next free letter (F), so nothing renumbers. It must NOT be added to
     `word_budget.BODY_CHAPTERS` — its heading says "(word-excluded)", exactly like Appendix D.
     It was left unwired on 2026-08-01 because scripts/** was drift-fenced during a live
     confirmatory campaign and a non-owner edit turns that run RED.
     REGENERATE, don't hand-edit: this file is produced from the real frozen sources by
     paper/appendices/gen_F_prompts_and_authored_code.py, which prints every path it reads. -->

# Appendix F — The prompts, and the code the model actually wrote (word-excluded)

This appendix prints the manipulation and its output verbatim. It exists because the surrounding
literature treats this as the standard of evidence and the two closest financial neighbours do not
meet it: of seven directly comparable systems, all seven print their prompts, five print
model-authored artefacts, and the two finance papers print neither authored code nor a worked
iteration. A reader cannot otherwise check that the loop did what the method section claims.

Every block below is reproduced from the artefact it names. The two prompt files are bound by the
design freeze, so what is printed here is what the campaign executed. Lines too long for the page
are hard-wrapped with a hanging indent. Nothing is elided, and no line is edited.

## F.1 The system prompt (`prompts/system.txt`, hash-bound)

Identical for every arm and every model, in every generation.

{SO}

```text
{sys_w}
```

{SC}

<!-- The filename is forced onto its own line. Section headings are set JUSTIFIED, so an
     \\allowbreak inside the \\texttt run is not enough: breaking early would leave a first line
     needing 73pt of stretch across four spaces, which TeX scores as infeasible, so it took the
     overfull line instead and 53.2pt of the path ran off the page. \\newline is not subject to
     that trade-off. F.1's path is short enough to fit and is left alone. -->

## F.2 The generation-0 prompt\\newline(`prompts/initial_generation.txt`, hash-bound)

Used once per arm, before any feedback exists.

{SO}

```text
{ini_w}
```

{SC}

## F.3 The reflection turn

Every generation after the first opens with a single fixed sentence, composed in code rather than
from a template file, and the arm's feedback block is appended directly beneath it.

{SO}

```text
{preamble}
```

{SC}

The five feedback blocks that may follow that sentence are printed in Listing 1.1 of the
Introduction, and are the whole of what differs across the language-model arms. `prompts/reflection.txt`
exists in the repository but is **dead** and is deliberately not loaded, a fact recorded here because
a reader inspecting the repository would otherwise reasonably assume it was the live template.

## F.4 What the model actually wrote

A complete authored reward program, exactly as archived, from the registered inference line's
`distributional` arm at generation 0. It was written from the contract alone, before the model
had seen any feedback.

{SO}

```python
{g0_w}
```

{SC}

## F.5 The iteration ladder

The same arm and candidate slot one generation later, after a single tail-feedback block. This is
the exhibit the lineage uses to show that the loop is doing something: the *same object* changing
under feedback, rather than a final artefact presented alone. The unified diff below is computed
between the two archived sources.

{SO}

```diff
{diff_w}
```

{SC}
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    # ⚠ APPENDIX G IS HAND-WRITTEN AND LIVES AT THE TAIL OF THIS SAME FILE, so it must survive
    # regeneration. It is here rather than in a file of its own because `scripts/build_paper.py`
    # names every appendix explicitly in `APPENDICES` and that tree is drift-fenced, so a new file
    # would reach no PDF; appending after F also gives G the letter document order already implies.
    # Losing it silently would delete twenty-five relocated notes from the deliverable, so the block
    # is carried across verbatim rather than rebuilt.
    if OUT.is_file():
        previous = OUT.read_text(encoding="utf-8")
        cut = previous.find("\n# Appendix G ")
        if cut != -1:
            doc = doc.rstrip() + "\n" + previous[cut:]
            n_carried = previous[cut:].count("\n## ")
            print(f"  carried the hand-written Appendix G/H block across ({n_carried} sections)")
        elif "\n## G." in previous or "\n# Appendix H" in previous:
            # FAIL LOUD. The carry-across is keyed on one exact heading string, so renaming that
            # heading would make the search miss while the sections it protects still exist -- and
            # the failure mode is a SILENT deletion of the whole correction record on the next
            # regeneration. Refuse to write rather than destroy work no build error would reveal.
            raise SystemExit(
                "REFUSING TO WRITE: the previous file carries hand-authored G/H sections but the\n"
                "  carry-across marker '# Appendix G ' was not found, so regenerating would DELETE\n"
                "  them. Restore that exact heading, or update the marker in this script, then re-run."
            )
    OUT.write_text(doc, encoding="utf-8")
    print(f"\nWROTE {OUT}  ({OUT.stat().st_size} bytes)")
    longest = max((len(l) for l in doc.splitlines()), default=0)
    print(f"longest line in the generated appendix: {longest} chars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
