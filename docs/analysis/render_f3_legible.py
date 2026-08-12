#!/usr/bin/env python3
"""Re-render F3 (the stylised-facts EDA figure) at document scale with legible type.

⛔ THE DEFECT, measured on ``paper/_build/dissertation.pdf`` (2026-08-10). F3 was authored on a
10.29 x 7.32 in canvas and the document gives it a 453.5 pt column, so pandoc's ``\\pandocbounded``
divides every glyph by 1.63. Measured on the page: 3.00-6.12 pt, the WORST of the five vector figures,
with the provenance footnote -- the thing that says the sealed years were never read -- arriving at
3.0-3.4 pt and simply unreadable. The guideline is Arial/Helvetica at >= 10 pt.

✅ WHY THIS ONE IS A MUTATION, NOT A REBUILD. F3 is a DATA figure: it plots the licensed gold panel's
TRAIN window, and every annotated number is computed by ``src.viz.eda.stylised_fact_stats``. Re-drawing
it here would fork that computation, which is exactly the failure mode ``src/viz/eda.py``'s own docstring
guards against. So this module plots nothing. It calls the FENCED ``build_f3`` -- same loader, same
window, same statistics, same provenance footnote -- intercepts the Figure on its way to disk, and then
changes exactly five things:

  1. the page size, to :data:`FIG_WIDTH_IN` x :data:`FIG_HEIGHT_IN`, so the document's scale factor
     becomes 1.000 and the figure fills the page height it is given instead of a little under half;
  2. every font size, to >= 10 pt, and the tick locators/formatters that density implies
     (:func:`_plain_log_labels` also removes the one construct that CANNOT reach 10 pt: a mathtext
     exponent, fixed by mathtext at 0.7 of its base);
  3. the line breaks, re-flowed to the width each label actually has (:func:`wrap_to_width`);
  4. two label strings, and only these two -- see :data:`_LABEL_FIXES` for why each one is textual
     rather than typographic;
  5. the position of three labels whose original placement only worked at 5 pt
     (:func:`resolve_collisions`), resolved against measured extents rather than by eye.

No datum, no number, no colour and no wording beyond (4) is touched: :func:`figure_words` is compared
across the re-flow, so a re-wrap passes and a dropped clause does not, and :func:`audit` re-checks type
size, containment and label-on-label overlap before anything is written.

⚠ ORDER OF OPERATIONS. ``scripts/make_figures.py`` writes the UNCORRECTED F3 to the same path, so run
this after it. When the ``src/**`` fence lifts, fold the page size, the sizes and the two label strings
back into ``fig_stylised_facts`` and delete this module.

Usage:
    python docs/analysis/render_f3_legible.py     # -> outputs/figures/F3_stylised_facts.{png,pdf}
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Iterable

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import matplotlib  # noqa: E402

matplotlib.use("Agg")  # measure and draw headlessly; the repo default is TkAgg

from docs.analysis.figure_typography import (  # noqa: E402
    EPS_PT, FIG_WIDTH_IN, MIN_PT, Rect, figure_words, renderer_for, wrap_to_width,
)

OUT = REPO / "outputs" / "figures" / "F3_stylised_facts.png"

#: Page height, chosen against the page budget rather than by eye. \textheight here is 700.1 pt (A4 less
#: two 2.5 cm margins). F3's caption in ``paper/CH4_methods.md`` is 485 characters, which sets 7-8 lines
#: at 12 pt / 1.5 spacing = 126-144 pt, plus ~10 pt of caption skip. A figure of 536 pt therefore leaves
#: 10-28 pt of slack on a float page, where the previous 322 pt-tall rendering left ~230 pt of it empty.
#: Going to the full ~565 pt would overrun the page by about a point once the caption is counted.
FIG_HEIGHT_IN = 7.45
SUPTITLE_PT = 11.0
BODY_PT = MIN_PT
#: Fraction of an axes' width a panel title may claim. Titles are left-aligned at the axes edge and the
#: gutter to their right is empty, so a little overhang is free; 1.10 was measured to stay clear of the
#: next column's y-label.
TITLE_WIDTH_FACTOR = 1.10
#: Fraction of an axes' width an in-panel annotation block may claim (it also carries a rounded patch).
ANNOT_WIDTH_FACTOR = 0.92
#: ...except in a panel that also labels individual markers. Panel (b) calls out each fed level next to
#: its point, and the deepest level's point sits in the bottom-right CORNER, so a full-width annotation
#: block leaves that callout nowhere to go -- neither above nor below its marker is clear. Holding the
#: block to two thirds of the panel costs it one extra line and gives the callouts a lane.
CALLOUT_PANEL_ANNOT_FACTOR = 0.66


def _capture_fenced_figure() -> Any:
    """Run the fenced ``build_f3`` and hand back its Figure instead of letting it reach disk.

    ``build_f3`` ends in ``savefig(fig, path)``; ``savefig`` is bound in ``src.viz.eda``'s namespace, so
    swapping that one name captures the figure while every line that touches the DATA runs untouched.
    The alternative -- re-implementing ``build_f3``'s loader glue here -- would duplicate the window
    selection and the provenance footnote, and those two are the figure's snoop-cleanliness claim.
    """
    from src.viz import eda

    captured: list[Any] = []

    def _capture(fig: Any, path: Any, **_kw: Any) -> None:
        captured.append(fig)

    original = eda.savefig
    eda.savefig = _capture  # type: ignore[assignment]
    try:
        eda.build_f3(OUT)
    finally:
        eda.savefig = original  # type: ignore[assignment]
    if len(captured) != 1:
        raise RuntimeError(
            f"expected build_f3 to save exactly one figure, it saved {len(captured)}. The fenced "
            "builder has changed shape; re-read it before trusting this repair.")
    fig = captured[0]
    renderer_for(fig)  # build_f3 ends in plt.close(); restore a canvas that can measure and draw
    return fig


def _titles(ax: Any) -> list[Any]:
    """The axes' non-empty title artists.

    There are three of them -- centre, left and right -- and ``set_title(loc="left")``, which every F3
    panel uses, writes to the LEFT one while ``ax.title`` stays empty. They are read off
    ``get_children()`` rather than off the private ``_left_title`` attribute, and told apart from the
    panel's annotations by not being in ``ax.texts``.
    """
    from matplotlib.text import Text

    annotations = set(map(id, ax.texts))
    return [c for c in ax.get_children()
            if isinstance(c, Text) and id(c) not in annotations and c.get_text()]


def _text_artists(ax: Any) -> list[Any]:
    """Every Text an axes owns: titles, axis labels, tick labels, offset text, annotations, legend."""
    items = list(_titles(ax)) + [ax.xaxis.label, ax.yaxis.label] + list(ax.texts)
    items += list(ax.get_xticklabels()) + list(ax.get_yticklabels())
    items += [ax.xaxis.get_offset_text(), ax.yaxis.get_offset_text()]
    leg = ax.get_legend()
    if leg is not None:
        items += list(leg.get_texts())
    return [t for t in items if t.get_text()]


def _panel_tag(ax: Any) -> str:
    """The panel letter from its "(a) ..." title, or "" for an axes without one."""
    for t in _titles(ax):
        s = t.get_text().lstrip()
        if len(s) > 2 and s[0] == "(" and s[2] == ")":
            return s[1]
    return ""


#: Two textual corrections applied to the built figure, each for a reason the type size cannot fix.
#:
#: ``realized`` -> ``realised``. ``src/viz/eda.py`` line 439 writes "realized vol" while the SAME
#: f-string spells "annualised" the British way and the document uses "realised" 97 times elsewhere; it
#: was one of only two American spellings left in the built PDF.
#:
#: ``CVaR$_\alpha$`` -> ``CVaR-α``. Mathtext renders a subscript at a FIXED 0.7 of the base, so this
#: label put its α on the page at 7 pt no matter how large the surrounding text was set -- the only
#: thing on any of the five figures that could not reach the 10 pt guideline. Setting the base to
#: 14.3 pt to drag the subscript up to 10 pt would leave one oversized axis label on a 10 pt figure.
#: The hyphenated form carries exactly the same referent, at one size, and is the convention the figure
#: suite already uses: this very panel's callouts read ``cvar_25``/``cvar_01`` and F1's box reads
#: "CVaR 1/5/10/25%". Revert this one entry to restore the subscript, at the cost of two 7 pt glyphs.
_LABEL_FIXES = {"realized": "realised", "CVaR$_\\alpha$": "CVaR-α"}


def correct_labels(fig: Any) -> dict[str, int]:
    """Apply :data:`_LABEL_FIXES` to every label on ``fig``; return how often each one fired.

    Fails loudly if any correction fires zero times, because finding nothing to correct would mean the
    fenced label has been reworded and this repair is now aimed at a string that no longer exists.
    """
    counts = {bad: 0 for bad in _LABEL_FIXES}
    artists = list(fig.texts)
    for ax in fig.axes:
        artists += _text_artists(ax)
    for t in artists:
        s = t.get_text()
        fixed = s
        for bad, good in _LABEL_FIXES.items():
            if bad in fixed:
                counts[bad] += fixed.count(bad)
                fixed = fixed.replace(bad, good)
        if fixed != s:
            t.set_text(fixed)
    missing = [bad for bad, n in counts.items() if n == 0]
    if missing:
        raise RuntimeError(
            f"expected to correct {missing} somewhere on F3 and found nothing; the fenced labels have "
            "been reworded, so re-read src/viz/eda.py before trusting this repair.")
    return counts


#: Each fenced panel title is two lines: a claim, then a gloss. At the 10 pt floor the pair re-flows to
#: three and four lines and eats a quarter of every panel, which is what made this figure read as prose
#: with a chart underneath. The claim alone is the title; the gloss is caption material and is carried
#: there. Keyed on the FIRST line so a reworded gloss cannot silently disable the shortening.
_SHORT_TITLES = {
    "(a) Heavy tails": "(a) Crash days a Normal cannot see",
    # 36 characters, matching panel (d), because at 37 the wrap budget for this column breaks the
    # title across two lines while its three neighbours sit on one. Measured, not guessed.
    "(b) The tail is a curve": "(b) The tail is a curve, not a point",
    "(c) Tail risk arrives in clusters": "(c) Tail risk arrives in clusters",
    "(d) Co-crashes": "(d) Diversification fails in the tail",
}


def shorten_titles(fig: Any) -> int:
    """Replace each two-line panel title with a one-line claim. Fails loudly if a key stops matching."""
    hits = 0
    for ax in fig.axes:
        for t in _titles(ax):
            for key, short in _SHORT_TITLES.items():
                if t.get_text().lstrip().startswith(key):
                    t.set_text(short)
                    hits += 1
                    break
    if hits != len(_SHORT_TITLES):
        raise RuntimeError(
            f"[F3_stylised_facts] shortened {hits} of {len(_SHORT_TITLES)} panel titles; the fenced "
            "titles in src/viz/eda.py have been reworded, so re-read them before trusting this repair.")
    return hits


def strip_fact_boxes(fig: Any) -> int:
    """Remove the four white annotation boxes from the canvas.

    ⚠ THEY WERE THE SINGLE LARGEST LEGIBILITY DEFECT ON THIS FIGURE, AND THE CONTENT IS NOT LOST.
    Each panel carried a bordered white block of two to four lines of statistics, placed in axes
    coordinates at a corner chosen when the type was 7.5 pt. At the 10 pt guideline floor each block
    grew by roughly a third and there was nowhere for it to go: in panel (a) it reached the histogram
    it was describing, and in panel (c) it sat across the 2008 volatility peak, which is the single
    most informative feature in that series.

    Every number in them is preserved and moved to the LaTeX caption, which is word-excluded, set at
    the same size as body text, and read by anyone who reads the figure. A statistic in a caption is
    not a statistic hidden; a statistic printed over the data it describes is data hidden.

    The artists are REMOVED rather than emptied. Emptying was tried first and fails: ``_text_artists``
    filters on a non-empty string while ``enlarge`` iterates ``ax.texts`` directly, so an emptied
    artist is absent from the snapshot dictionary and present in the loop that reads it, and the
    re-flow dies on a ``KeyError``. An artist that is gone is gone from both.
    """
    removed = 0
    for ax in fig.axes:
        for t in list(ax.texts):
            if t.get_bbox_patch() is not None and len(t.get_text()) > 20:
                t.remove()
                removed += 1
    if removed != 4:
        raise RuntimeError(
            f"[F3_stylised_facts] expected 4 boxed fact blocks and found {removed}; the fenced figure "
            "has changed, so re-read src/viz/eda.py before trusting this repair.")
    # The three-line grey provenance footnote goes with them, for the same reason and to the same
    # place. It states the window, the universe and the anonymisation, all of which the caption and
    # the data chapter already carry, and at 10 pt it occupied a tenth of the figure's height.
    foot = [t for t in fig.texts if t is not getattr(fig, "_suptitle", None) and t.get_text()]
    if len(foot) != 1:
        raise RuntimeError(
            f"[F3_stylised_facts] expected exactly 1 figure-level footnote and found {len(foot)}; "
            "re-read src/viz/eda.py before trusting this repair.")
    foot[0].remove()
    return removed


def _extent(fig: Any, artist: Any) -> Rect:
    bb = artist.get_window_extent(renderer=renderer_for(fig))
    k = 72.0 / fig.dpi
    return Rect(bb.x0 * k, bb.y0 * k, bb.x1 * k, bb.y1 * k)


def _obstacles(fig: Any, ax: Any, exclude: Iterable[Any]) -> list[Rect]:
    """Extents of every other label in the panel -- what a moved label must not land on."""
    skip = set(map(id, exclude))
    items = [t for t in ax.texts if id(t) not in skip]
    leg = ax.get_legend()
    if leg is not None:
        items += list(leg.get_texts())
    return [_extent(fig, t) for t in items if t.get_text()]


def resolve_collisions(fig: Any) -> None:
    """Move the few labels whose original positions only worked at 5 pt. Positions only.

    Enlarging type moves nothing, so two placements that were merely tight at 4.9 pt become real
    collisions at 10 pt. Both are resolved against MEASURED extents, after the layout has settled, so
    the fix does not depend on eyeballing this particular render:

    (a) the −3σ / −5σ rules were labelled at the very top of the panel, which the 10 pt legend now
        reaches; they drop to just above the annotated fact box and are staggered so that the two,
        which stand only 2σ apart, cannot touch each other either.
    (b) the fed-level callouts hang below their markers, which puts the deepest one -- at the very
        bottom-right of the panel -- underneath the annotation box. Each callout keeps the author's
        placement unless it collides, and flips above its marker only if it does.
    """
    for ax in fig.axes:
        tag = _panel_tag(ax)
        if tag == "a":
            sigmas = sorted((t for t in ax.texts if t.get_text().endswith("σ")),
                            key=lambda t: t.get_position()[0])
            # ⚠ THE ANCHOR USED TO BE THE ANNOTATED FACT BOX, WHICH NO LONGER EXISTS.
            # These two labels sat at the very top of the panel, where the 10 pt legend now reaches,
            # so they were dropped to just above the white statistics block. That block has since been
            # moved off the canvas into the caption, and with nothing to anchor to this branch fell
            # through and left the two labels back at the top, overlapping each other by 62 pt^2 and
            # the legend by 49. Caught by this module's own audit, which is what it is for.
            # The floor of the panel is now empty, so that is where they go: an absolute base, with
            # the two staggered because they stand only 2 sigma apart on the axis.
            base = 0.0
            if not sigmas:
                continue
            for t, dy in zip(sigmas, (0.14, 0.02)):  # deepest (leftmost) sits higher
                t.set_position((t.get_position()[0], base + dy))
                t.set_va("bottom")
        elif tag == "b":
            callouts = sorted((t for t in ax.texts if t.get_text().startswith("cvar_")),
                              key=lambda t: t.xy[0])
            if len(callouts) >= 2:
                callouts[-1].set_ha("left")        # largest α = the LEFT end (the axis is inverted)
                callouts[0].set_ha("right")        # smallest α = the right end
            blocked = _obstacles(fig, ax, exclude=callouts)
            panel = _extent(fig, ax)
            for t in callouts:
                dx = t.xyann[0]
                for dy, va in ((-13.0, "top"), (13.0, "bottom")):
                    t.xyann = (dx, dy)
                    t.set_va(va)
                    fig.canvas.draw()
                    here = _extent(fig, t)
                    clear = not any(here.overlap(r) > EPS_PT for r in blocked)
                    if clear and panel.contains(here, slack=2.0):
                        break                    # inside the panel AND clear of every other label
                blocked.append(_extent(fig, t))  # later callouts must clear the ones already placed


#: Points a panel loses on its left to the y-label plus its widest tick label, at 10 pt. Only used to
#: seed the FIRST wrapping pass, before any layout has run; every later pass measures the real thing.
_GUTTER_PT = 52.0
#: Points a panel row loses to its title, x tick labels and x-label, at 10 pt -- same seeding role.
_ROW_CHROME_PT = 92.0
#: Points the suptitle and the provenance footnote take off the page -- same seeding role.
_PAGE_CHROME_PT = 76.0


def _grid_estimate(fig: Any) -> tuple[float, float, float]:
    """(width, height, left edge) a panel can expect, from the GRID alone -- no layout required."""
    gs = fig.axes[0].get_subplotspec().get_gridspec()
    fig_w, fig_h = (v * 72.0 for v in fig.get_size_inches())
    col_w, row_h = fig_w / gs.ncols, (fig_h - _PAGE_CHROME_PT) / gs.nrows
    return col_w - _GUTTER_PT, row_h - _ROW_CHROME_PT, _GUTTER_PT


def _plain_log_labels(axis: Any) -> None:
    """Label a log axis "0.1, 1, 10, 100" instead of 10^-1, 10^0, ... -- no mathtext, no 7 pt exponent.

    Matplotlib's default log labels are mathtext powers, and mathtext renders a superscript at a fixed
    0.7 of the base, so a 10 pt tick label puts its exponent on the page at 7 pt. Plain decimals carry
    the same values, at one size, and read better at this scale. An axis whose labels were fixed by the
    author (panel (b) sets its own) is left alone.
    """
    from matplotlib.ticker import LogFormatter, NullFormatter, ScalarFormatter

    if not isinstance(axis.get_major_formatter(), LogFormatter):
        return  # a FixedFormatter or anything bespoke: the author chose these labels, keep them
    fmt = ScalarFormatter()
    fmt.set_scientific(False)
    fmt.set_useOffset(False)
    axis.set_major_formatter(fmt)
    axis.set_minor_formatter(NullFormatter())


def _draw_checked(fig: Any) -> None:
    """Draw, and refuse to continue if constrained layout gave up on this figure."""
    import warnings

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        fig.canvas.draw()
    collapsed = [str(w.message) for w in caught if "collapsed" in str(w.message)]
    if collapsed:
        raise RuntimeError(
            "constrained layout gave up and fell back to the default subplot parameters, so the panel "
            f"geometry below is meaningless: {collapsed[0]}")


def enlarge(fig: Any) -> Any:
    """Resize the page, raise every font to >= 10 pt, and re-flow each label to the width it has."""
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt

    fig.set_size_inches(FIG_WIDTH_IN, FIG_HEIGHT_IN)

    # Snapshot the ORIGINAL strings: re-flowing must always start from them, never from an already
    # wrapped copy, or the second pass would treat inserted breaks as the author's own.
    originals: dict[int, tuple[Any, str]] = {}
    for ax in fig.axes:
        for t in _text_artists(ax):
            originals[id(t)] = (t, t.get_text())
    for t in fig.texts:
        originals[id(t)] = (t, t.get_text())

    for ax in fig.axes:
        for t in _text_artists(ax):
            t.set_fontsize(BODY_PT)
        # Fewer, larger ticks: at 10 pt the auto locator's density collides on a ~190 pt-wide panel.
        # A DATE axis needs its own locator/formatter pair -- putting a numeric locator on one produces
        # ticks at arbitrary instants, which the date formatter then prints as full "2005-02-08" stamps.
        for axis in (ax.xaxis, ax.yaxis):
            converter = axis.get_converter()
            if converter is not None and type(converter).__module__ == mdates.__name__:
                axis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=6))
                axis.set_major_formatter(mdates.ConciseDateFormatter(axis.get_major_locator()))
            elif axis.get_scale() == "log":
                _plain_log_labels(axis)
            else:
                axis.set_major_locator(plt.MaxNLocator(nbins=5, steps=[1, 2, 2.5, 5, 10]))
    for t in fig.texts:
        t.set_fontsize(SUPTITLE_PT if t is getattr(fig, "_suptitle", None) else BODY_PT)

    # THE ORDER HERE IS LOAD-BEARING. Constrained layout sizes a panel to fit its decorations, so an
    # unwrapped 230 pt title in a 227 pt column makes it give up entirely ("axes sizes collapsed to
    # zero") and fall back to the default subplot parameters. Measuring the axes at that point returns a
    # 47 pt-wide panel, and wrapping the titles to THAT produces fifteen-line titles. So the first pass
    # wraps against the GRID geometry, which is known before any layout runs; only once the layout has
    # succeeded do the later passes refine against what each panel actually got.
    fig_w = fig.get_size_inches()[0] * 72.0
    for pass_no in range(3):
        for ax in fig.axes:
            if pass_no == 0:
                ax_w, ax_h, ax_x0 = _grid_estimate(fig)
            else:
                box = ax.get_window_extent()
                k = 72.0 / fig.dpi
                ax_w, ax_h, ax_x0 = box.width * k, box.height * k, box.x0 * k
            # A left-aligned title starts at the axes' left edge and may overhang into the empty gutter
            # to its right -- but never past the page, which is what binds for the right-hand column.
            title_budget = min(ax_w * TITLE_WIDTH_FACTOR, fig_w - ax_x0 - 6.0)
            for t in _titles(ax):
                t.set_text(wrap_to_width(fig, originals[id(t)][1], size=BODY_PT, max_pt=title_budget))
            has_callouts = any(t.get_text().startswith("cvar_") for t in ax.texts)
            annot_w = ax_w * (CALLOUT_PANEL_ANNOT_FACTOR if has_callouts else ANNOT_WIDTH_FACTOR)
            for t in ax.texts:
                if t.get_text().startswith("cvar_"):
                    continue                     # a marker callout, not a block: never wrapped
                t.set_text(wrap_to_width(fig, originals[id(t)][1], size=BODY_PT, max_pt=annot_w))
            # The y-label runs along the axes HEIGHT, so that -- not the width -- is its budget.
            for t, budget in ((ax.xaxis.label, ax_w), (ax.yaxis.label, ax_h)):
                if t.get_text():
                    t.set_text(wrap_to_width(fig, originals[id(t)][1], size=BODY_PT, max_pt=budget))
        for t in fig.texts:
            if t is getattr(fig, "_suptitle", None):
                continue
            t.set_text(wrap_to_width(fig, originals[id(t)][1], size=BODY_PT, max_pt=fig_w - 14.0))
        _draw_checked(fig)

    # Reserve a bottom strip for the provenance footnote, now that it sets four lines at 10 pt rather
    # than three at 6.3 pt, so constrained layout does not pack panel (c)/(d) on top of it.
    from matplotlib.layout_engine import ConstrainedLayoutEngine

    engine = fig.get_layout_engine()
    if isinstance(engine, ConstrainedLayoutEngine):
        foot = [t for t in fig.texts if t is not getattr(fig, "_suptitle", None)]
        strip = max((t.get_window_extent().height * 72.0 / fig.dpi for t in foot), default=0.0)
        # ``rect`` is (left, bottom, WIDTH, HEIGHT), not (x0, y0, x1, y1): passing a height of 1.0 with a
        # non-zero bottom pushes the layout region off the top of the page and the panel titles with it.
        bottom = (strip + 6.0) / (FIG_HEIGHT_IN * 72.0)
        engine.set(rect=(0.0, bottom, 1.0, 1.0 - bottom))
        _draw_checked(fig)

    resolve_collisions(fig)  # last: it measures where things actually landed
    return fig


def audit(fig: Any) -> None:
    """Raise unless every text on the figure is >= 10 pt and every LABEL sits inside the page.

    The containment half deliberately skips tick labels: matplotlib keeps tick artists for locations
    outside the current view, which are never drawn, so testing them reports phantom overflows.
    """
    problems: list[str] = []
    sized = list(fig.texts)
    placed = list(fig.texts)
    for ax in fig.axes:
        sized += _text_artists(ax)
        placed += _titles(ax) + list(ax.texts) + [ax.xaxis.label, ax.yaxis.label]
        leg = ax.get_legend()
        if leg is not None:
            placed += list(leg.get_texts())
    for t in sized:
        if t.get_fontsize() < MIN_PT - 1e-9:
            problems.append(f"{t.get_text()[:34]!r} is {t.get_fontsize():.2f} pt")
    fig.canvas.draw()
    w_px, h_px = fig.get_size_inches() * fig.dpi
    for t in placed:
        if not t.get_text():
            continue
        bb = t.get_window_extent()
        if bb.x0 < -1.0 or bb.y0 < -1.0 or bb.x1 > w_px + 1.0 or bb.y1 > h_px + 1.0:
            problems.append(
                f"{t.get_text()[:34]!r} runs off the page "
                f"(x {bb.x0 * 72 / fig.dpi:.0f}..{bb.x1 * 72 / fig.dpi:.0f} pt, "
                f"y {bb.y0 * 72 / fig.dpi:.0f}..{bb.y1 * 72 / fig.dpi:.0f} pt)")

    # Label-on-label overlap, panel by panel. Tick labels stay out of it (matplotlib keeps artists for
    # out-of-view ticks) and so do titles, which live outside the panel and cannot reach its contents.
    for ax in fig.axes:
        inside = [t for t in ax.texts if t.get_text()]
        leg = ax.get_legend()
        if leg is not None:
            inside += list(leg.get_texts())
        rects = [(t, _extent(fig, t)) for t in inside]
        for i, (a, ra) in enumerate(rects):
            for b, rb in rects[i + 1:]:
                if ra.overlap(rb) > EPS_PT:
                    problems.append(
                        f"in panel ({_panel_tag(ax) or '?'}) {a.get_text()[:24]!r} overlaps "
                        f"{b.get_text()[:24]!r} by {ra.overlap(rb):.1f} pt^2")
    if problems:
        raise RuntimeError("[F3_stylised_facts] audit failed:\n  - " + "\n  - ".join(problems))


def main() -> int:
    import matplotlib.pyplot as plt

    fig = _capture_fenced_figure()
    print(f"[F3] label corrections applied: {correct_labels(fig)}")
    # Both of these CHANGE THE WORDING, so they run before the snapshot that forbids wording changes.
    # Each carries its own loud guard against the fenced source drifting underneath it.
    print(f"[F3] panel titles shortened: {shorten_titles(fig)}")
    print(f"[F3] fact boxes removed from the canvas: {strip_fact_boxes(fig)}")
    before = figure_words(fig)      # snapshot BEFORE the re-flow: only line breaks may change
    enlarge(fig)
    after = figure_words(fig)
    if before != after:
        raise RuntimeError(
            f"[F3_stylised_facts] the re-flow changed the wording, not just the line breaks: "
            f"lost {sorted((before - after).elements())}, gained {sorted((after - before).elements())}")
    audit(fig)

    # ``apply_house_style`` (called inside build_f3) sets savefig.bbox='tight'. A tight crop would change
    # the saved page width, and the whole repair depends on that width being exactly 6.30 in.
    plt.rcParams["savefig.bbox"] = "standard"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=600, bbox_inches=None, pad_inches=0.0, facecolor="white")
    fig.savefig(OUT.with_suffix(".pdf"), bbox_inches=None, pad_inches=0.0, facecolor="white")
    plt.close(fig)
    print(f"wrote {OUT} (+ .pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
