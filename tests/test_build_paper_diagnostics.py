"""Tests for the DELIVERABLE-verification gates in scripts/build_paper.py.

Why these exist
---------------
For nineteen days every build of this dissertation silently dropped seventeen characters from
the PDF — a Greek letter in a formula, a subscript on a norm, the ``≈`` in front of a reported
compute figure — and every lane reported the paper green. The engine had been NAMING each drop
on every single build. Two independent defects in this file threw the report away, either of
which was sufficient on its own:

  1. ``subprocess.run(..., text=True)`` with no ``encoding=`` decodes the child's output with the
     BOX's locale codec. On a cp1251 box the reader thread dies on the first non-decodable byte
     and ``subprocess.run`` STILL RETURNS rc=0 with both channels EMPTY — so the caller counted
     zero warnings out of an empty string and printed a green summary from no evidence at all.
  2. The warning filter matched only ``WARNING``/``Error``; tectonic prints lowercase
     ``warning:``. With the channel fully readable it still matched 0 of 51 emitted lines.

Every test below fails against the pre-fix code: tests 1–2 pin behaviour the old one-line filter
got wrong, tests 3–6 exercise functions that did not exist, and test 7 is a POSITIVE CONTROL that
reproduces defect (1) live on this machine rather than asserting it from the traceback.
"""
from __future__ import annotations

import locale
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import build_paper as bp  # noqa: E402

#: Verbatim from a real build's stderr, 2026-08-01 (three typesetting passes emit it three times).
REAL_MISSING_LINE = (
    "warning: texput.tex:3279: Missing character: There is no ≈ (U+2248) in font "
    "[lmroman12-regular]:mapping=tex-text;!"
)
#: The pre-fix filter, kept verbatim so the regression it caused is pinned rather than described.
_OLD_FILTER = staticmethod(lambda ln: "WARNING" in ln or "Error" in ln)


def test_lowercase_tectonic_warning_is_counted() -> None:
    """The exact regression: tectonic's lowercase 'warning:' matched nothing before this fix."""
    assert not _OLD_FILTER(REAL_MISSING_LINE), "positive control: the OLD filter missed this line"
    warnings, missing = bp.scan_diagnostics(REAL_MISSING_LINE)
    assert warnings == [REAL_MISSING_LINE]
    assert missing == [REAL_MISSING_LINE]


def test_pandoc_uppercase_warning_still_counted() -> None:
    """Widening the filter must not lose the form it already caught (citeproc's is the costly one)."""
    line = "[WARNING] Citeproc: citation kvasiuk2026madevolve not found"
    warnings, missing = bp.scan_diagnostics(line)
    assert warnings == [line]
    assert missing == []


def test_missing_characters_deduplicated_across_typesetting_passes() -> None:
    """One drop re-reported on each pass is ONE occurrence, not three."""
    channel = "\n".join([REAL_MISSING_LINE] * 3)
    _, missing = bp.scan_diagnostics(channel)
    assert len(missing) == 1


def test_distinct_source_lines_are_distinct_occurrences() -> None:
    channel = REAL_MISSING_LINE + "\n" + REAL_MISSING_LINE.replace("texput.tex:3279", "texput.tex:7975")
    _, missing = bp.scan_diagnostics(channel)
    assert len(missing) == 2


def test_tectonic_second_spelling_of_the_same_drop_is_also_caught() -> None:
    """The engine reports one drop twice, in two different message formats from two code paths.

    Matching only TeX's spelling would leave the gate depending on the driver continuing to emit
    the other one, which is a coincidence, not a contract.
    """
    line = ('warning: could not represent character "≈" (0x2248) in font '
            '"[lmroman12-regular]:mapping=tex-text;"')
    warnings, missing = bp.scan_diagnostics(line)
    assert warnings == [line]
    assert missing == [line]
    m = bp._MISSING_CHAR_RE.search(line)
    assert m is not None and (m.group(1) or m.group(3)).upper() == "2248"


def test_missing_char_regex_extracts_the_codepoint_and_font() -> None:
    m = bp._MISSING_CHAR_RE.search(REAL_MISSING_LINE)
    assert m is not None
    assert m.group(1).upper() == "2248"
    assert m.group(2) == "lmroman12-regular"


def test_ordinary_prose_containing_the_word_warning_does_not_fire() -> None:
    """Case-sensitive alternatives, deliberately: our own prose says 'warning' in sentences."""
    warnings, _ = bp.scan_diagnostics("we issue a warning to the reader about optional stopping")
    assert warnings == []


def test_control_bytes_found_and_tab_allowed() -> None:
    hits = bp.scan_control_bytes("clean line\nwith a bell \x07here\n\ttabbed is fine\n")
    assert [(lineno, cp) for lineno, cp, _ in hits] == [(2, 0x07)]


def test_control_byte_scan_is_clean_on_the_real_deliverable() -> None:
    assert bp.scan_control_bytes(bp.assemble(bp.REPO / "paper")) == []


def test_glyph_check_reports_unverified_rather_than_zero(tmp_path: Path) -> None:
    """A count of 0 from a check that could not run must NOT be readable as 'clean'."""
    count, status = bp.verify_pdf_glyphs(tmp_path / "does_not_exist.pdf")
    assert count == 0
    assert status != "ok", "an unrunnable check must report its status, not a clean-looking zero"


def test_final_refuses_md_only_because_it_would_certify_nothing(capsys) -> None:
    """F-18: `--md-only --final` returned rc=0 HAVING COMPILED NOTHING.

    `--final` is the SUBMISSION gate and certifies the compiled deliverable; `--md-only` exits
    before pandoc. Passing both waved the gate through on a PDF that was never built — the same
    false-green class as the unread diagnostic channel, aimed at the deliverable itself.
    """
    assert bp.main(["--md-only", "--final"]) == 2
    assert "REFUSING --final with --md-only" in capsys.readouterr().err


def test_bundle_provenance_reports_unknown_rather_than_clean(tmp_path) -> None:
    """F-19: an unresolvable bundle must report UNKNOWN, never an empty-but-clean-looking result."""
    got = bp.tectonic_bundle_provenance(tmp_path)
    assert got["digest"] is None
    assert got["reason"], "an unresolved bundle must carry a stated reason, not a silent blank"


def test_bundle_provenance_finds_the_faces_and_the_digest(tmp_path) -> None:
    """The digest is the content-addressed directory NAME, and all four faces must be found in it."""
    d = tmp_path / "bundles" / "data" / ("a" * 64)
    d.mkdir(parents=True)
    for f in bp._HEROS_FACES:
        (d / f).write_bytes(b"")
    got = bp.tectonic_bundle_provenance(tmp_path)
    assert got["digest"] == "a" * 64
    assert got["faces_missing"] == []
    assert len(got["faces_present"]) == 4


def test_bundle_provenance_names_a_missing_face() -> None:
    """A missing face is why `mainfont` would silently fall back and re-flatten the document, so it
    must be NAMED rather than counted."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        d = root / "bundles" / "data" / ("b" * 64)
        d.mkdir(parents=True)
        for f in bp._HEROS_FACES[:3]:          # bolditalic deliberately absent
            (d / f).write_bytes(b"")
        got = bp.tectonic_bundle_provenance(root)
        assert got["faces_missing"] == ["texgyreheros-bolditalic.otf"]


def test_the_real_bundle_carries_all_four_heros_faces() -> None:
    """Against the REAL cache: the deliverable's typeface is loaded BY FILE from this bundle, so a
    pin nobody can verify is fictional (Priority 5 / the R85 lesson). Skips if never populated."""
    got = bp.tectonic_bundle_provenance(Path(r"D:\tectonic-cache"))
    if got["digest"] is None:
        pytest.skip(f"tectonic cache not populated here: {got.get('reason')}")
    assert got["faces_missing"] == [], f"bundle {got['digest'][:16]} is missing {got['faces_missing']}"


@pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
def test_subprocess_text_mode_without_encoding_loses_the_channel() -> None:
    """POSITIVE CONTROL, executed: reproduce defect (1) on this machine.

    A child writing UTF-8 bytes that the box's locale codec cannot decode must be readable with
    ``encoding='utf-8'`` and — on a legacy codepage — must be SILENTLY LOST without it. The loss
    half is asserted only where the box actually has a legacy codec, so the test states a fact
    about the machine it runs on rather than a guess about every machine.

    ⚠ MEASURED, and it corrects my own first description of this defect: the lost channel comes
    back as ``None``, not as ``""``. Reading it through ``(proc.stderr or "")`` — which the caller
    did — turns the two into the same thing, so an UNMEASURED channel became an OBSERVED-EMPTY one
    at the point of use. Zero and absent are different values; the idiom that conflates them is
    what let the caller print a green summary. The pinned contract is therefore stated as the
    difference between the two calls, not as an equality against a particular falsy value.

    The unhandled-thread-exception warning is filtered HERE ONLY: that exception is the phenomenon
    under test, and its warning would otherwise be indistinguishable from an unexplained one.
    """
    prog = r'import sys; sys.stdout.buffer.write(b"\xe2\x80\x98")'  # U+2018, byte 0x98 in UTF-8
    good = subprocess.run([sys.executable, "-c", prog], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    assert good.stdout == "‘", "the FIXED form must read the channel"

    if locale.getpreferredencoding(False).lower().replace("-", "") in {"utf8", "cp65001"}:
        pytest.skip("box already defaults to UTF-8; the loss cannot be reproduced here")
    bad = subprocess.run([sys.executable, "-c", prog], capture_output=True, text=True)
    assert bad.returncode == 0, "the defect is silent: the child still reports success"
    assert not bad.stdout, (
        "expected the legacy-codec decode failure to destroy the channel while still returning "
        f"rc=0; got {bad.stdout!r}"
    )
    assert bad.stdout != good.stdout, "the unfixed call must not be able to see what the fixed one sees"
