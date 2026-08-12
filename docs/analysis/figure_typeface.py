"""One typeface for the whole document, figures included.

WHY THIS EXISTS, AND WHY IT IS NOT A COSMETIC MODULE
----------------------------------------------------
The compiled dissertation is set in **TeX Gyre Heros**, the URW Nimbus Sans / Helvetica clone
that `scripts/build_paper.py` loads by file so the IFTE0008 guideline ("it is recommended to
use Arial or Helvetica") is met without a system-font dependency.

Every figure, however, was drawn by matplotlib at its factory default, **DejaVu Sans**.

MEASURED on the 2026-08-12 build, by reading the embedded font list of each exhibit page of
`paper/_build/dissertation.pdf`: five vector figures (1.2, 3.1, 3.2, 4.1, 4.2) carried
`DejaVuSans` / `DejaVuSans-Bold` / `DejaVuSans-Oblique` subsets alongside the body's
`TeXGyreHeros-*`, and every raster figure had DejaVu baked into its pixels. So an examiner
turning a page met one typeface in the prose and a different one, with a visibly different
"a", "g" and digit set, inside the exhibit six centimetres below it.

That mismatch is the single most legible reason a figure suite reads as assembled rather than
designed, and it is invisible to every gate this project owns: the build is clean, the glyph
gates pass, the citation gate passes. Nothing in the pipeline looks at what a figure is SET IN.

WHY THE FONT FILES LIVE IN THE REPOSITORY
-----------------------------------------
`docs/figures/fonts/` holds the four faces, copied from the pinned Tectonic bundle that the
document itself resolves them from (digest recorded by
`build_paper.tectonic_bundle_provenance`). They are in the repository rather than read out of
`D:\\tectonic-cache` because Priority 5 is explicit that a dependency nobody can verify is
fictional: a figure build that silently falls back to DejaVu when a cache directory is missing
would reintroduce exactly the defect this module exists to remove, and would do it quietly.
The GUST Font Licence (an OFL variant) permits redistribution.

FAILING LOUD IS THE POINT
-------------------------
:func:`use_document_typeface` RAISES when a face is missing. A silent fallback is what produced
the defect in the first place.
"""

from __future__ import annotations

from pathlib import Path

#: The four faces, and the matplotlib rcParam family each one serves.
_FACES = (
    "texgyreheros-regular.otf",
    "texgyreheros-bold.otf",
    "texgyreheros-italic.otf",
    "texgyreheros-bolditalic.otf",
)

#: Repository-relative home of the faces. `docs/analysis/figure_typeface.py` -> repo root -> docs/figures/fonts.
FONT_DIR = Path(__file__).resolve().parents[2] / "docs" / "figures" / "fonts"

#: The family name the faces report to fontconfig/matplotlib once registered.
FAMILY = "TeX Gyre Heros"


def use_document_typeface() -> str:
    """Register the document's typeface with matplotlib and make it the default for figures.

    Call AFTER ``apply_house_style()`` and after any per-script ``rcParams.update`` that sets
    sizes, because this only touches the family keys and must not be overwritten by them.

    Returns the family name actually installed, so a caller can assert on it.

    Raises
    ------
    FileNotFoundError
        If any of the four faces is absent. Deliberate: a missing face would otherwise fall back
        to DejaVu Sans and silently restore the mismatch this module exists to remove.
    """
    import matplotlib
    import matplotlib.font_manager as fm

    missing = [f for f in _FACES if not (FONT_DIR / f).is_file()]
    if missing:
        raise FileNotFoundError(
            f"the document typeface is incomplete: {missing} absent from {FONT_DIR}. "
            "The figures would silently fall back to DejaVu Sans and stop matching the body text. "
            "Restore them from the pinned Tectonic bundle "
            "(D:/tectonic-cache/bundles/data/<digest>/texgyreheros-*.otf)."
        )

    for face in _FACES:
        fm.fontManager.addfont(str(FONT_DIR / face))

    matplotlib.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": [FAMILY, "DejaVu Sans"],
        # Mathtext is what sets a minus sign, an exponent and any $...$ in a label. Left at its
        # default it draws them in Computer Modern, so a single axis could carry THREE typefaces.
        # "custom" plus the four keys below routes every mathtext shape to the same family.
        "mathtext.fontset": "custom",
        "mathtext.rm": FAMILY,
        "mathtext.it": f"{FAMILY}:italic",
        "mathtext.bf": f"{FAMILY}:bold",
        "mathtext.sf": FAMILY,
        # A true minus (U+2212) exists in Heros, so unicode_minus stays on and the sign in "-0.5"
        # matches the sign the body text prints.
        "axes.unicode_minus": True,
    })
    return FAMILY


def assert_no_dejavu(pdf_path: str | Path, pages: list[int] | None = None) -> list[str]:
    """Return the DejaVu subsets still embedded in ``pdf_path`` (empty list means clean).

    The gate this module is worth having. Reads the compiled artefact rather than the source,
    because the source cannot tell you what a raster figure was drawn in.
    """
    import fitz

    hits: list[str] = []
    with fitz.Document(str(pdf_path)) as doc:
        for pi, page in enumerate(doc):
            if pages is not None and (pi + 1) not in pages:
                continue
            for font in page.get_fonts(full=True):
                if "DejaVu" in font[3]:
                    hits.append(f"page {pi + 1}: {font[3]}")
    return hits
