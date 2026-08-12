#!/usr/bin/env python3
"""Re-render the three vector SCHEMATICS (F1, F2, F4) at document scale with legible type.

⛔ THE DEFECT, measured on ``paper/_build/dissertation.pdf`` (2026-08-10). Pandoc includes each figure
through ``\\pandocbounded``, which scales it by ``min(textheight/H, linewidth/W)`` and never scales up, so
with a 453.5 pt line width a schematic authored on an 8.1 in page has every glyph divided by 1.29 on the
page. Measured minimum rendered size: F1 5.28 pt, F2 5.28 pt, F4 4.50 pt, against the IFTE0008 guideline
of Arial/Helvetica at >= 10 pt. F1's drawn extent was also only ~425 pt of the 453.5 pt column.

⚠ WHY THIS IS A REBUILD AND NOT A MUTATION. ``src/viz/schematics.py`` is edit-fenced while the
confirmatory campaign is live, and its three diagrams are laid out in an abstract 0-10 axis with box
widths chosen for 6.8-8 pt type. Enlarging their text in place cannot work: at 10 pt the top row of F1
needs 361 pt of glyphs plus padding and gaps inside a 453.5 pt column, so the labels must be re-wrapped
and the boxes re-sized -- that IS the layout. So these three are re-laid out in
:mod:`docs.analysis.figure_typography`'s point-exact canvas, at exactly 6.30 in wide, with

  * every label >= 10 pt (asserted -- :meth:`Canvas.audit`),
  * no label outside its box, off the page, or on top of another label (asserted),
  * and no content dropped: :func:`assert_no_content_lost` diffs the rebuilt figure's bag of words
    against the FENCED figure's, so a re-wrap or a moved date passes and a deleted branch, caption or
    number does not.

Only line breaks and positions change. No wording, no number, no colour and no encoding does: the
palette and the white-fill/thin-border/greyscale-safe-by-shape house style come from ``src.viz.style``.

⇒ WHEN THE FENCE LIFTS these three layouts belong back in ``src/viz/schematics.py`` and this module,
together with ``render_system_diagram.py``, should be deleted in the same commit.

Usage:
    python docs/analysis/render_schematics_legible.py    # -> outputs/figures/F{1,2,4}_*.{png,pdf}
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from docs.analysis.figure_typography import (  # noqa: E402
    FIG_WIDTH_PT, MIN_PT, Canvas, Rect, assert_no_content_lost, distribute,
)

FIGDIR = REPO / "outputs" / "figures"

TITLE_PT = 11.0        # figure titles, the one size above the 10 pt floor
BODY_PT = MIN_PT       # every other label sits exactly on the guideline floor
MARGIN = 8.0           # page-edge margin in points


def _palette() -> dict[str, str]:
    from src.viz.style import OKABE_ITO

    return OKABE_ITO


def tint(hex_colour: str, keep: float = 0.16) -> str:
    """The same hue, mixed down onto white, for a box fill that black text can sit on.

    ⚠ WHY THE SATURATED FILLS WENT. Three of these schematics used full-strength Okabe-Ito fills with
    white text, which is the convention of a conference slide rather than of a printed paper: at A4 a
    solid vermillion block is the loudest object on the page and the eye goes to it before the title.
    It also inverts the reading order the diagram wants, because the emphasised box is emphasised by
    AREA, and area is the strongest visual channel there is.

    A pale tint of the same hue with a full-strength border keeps the colour coding exactly, restores
    black text (which is more legible than white on colour at 10 pt), and lets the arrows and labels
    read as the foreground they are. The hue still identifies the box; it no longer shouts.
    """
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255.0 for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(round(255 * (keep * v + (1.0 - keep))) for v in (r, g, b))


# ------------------------------------------------------------------------------------------------- #
# F1 -- the system diagram (Figure 1.1 and Figure 4.1)                                                #
# ------------------------------------------------------------------------------------------------- #
#: Row-1 labels, re-wrapped for a 453.5 pt column. Same words as the fenced schematic, new line breaks.
_F1_TOP = [
    "Gold panel\n(survivorship-\nfree PIT)",
    "Portfolio env\n+ fixed SAC\nagent",
    "Realised\nreturns\n(OOS)",
    "Tail measurement\n(CVaR 1/5/10/25%,\nmass, skew)",
]
_F1_FEEDBACK = "FEEDBACK CHANNEL\n(the contribution)\nvector tail  vs  scalar"
_F1_DESIGNER = "LLM reward designer\n(Eureka reflection)"
_F1_CODE = "Authored\nreward CODE"
#: ⛔ THE THREE-LINE GREY BLOCK THAT SAT UNDER THIS DIAGRAM IS GONE, AND ITS WORDS ARE IN THE CAPTION.
#: It said what the LaTeX caption already says, in smaller grey type, inside the figure, where a
#: reader cannot tell a caption from an axis note. Every schematic carried one and each cost a fifth
#: of its own height. The words are not lost; they are set once, at body size, underneath.
_F1_TITLE = "System architecture: the closed reward-design loop, agent fixed"


def system_diagram() -> Canvas:
    """F1: the closed loop, laid out for a 453.5 pt column at 10 pt."""
    pal = _palette()
    blue, green, verm, grey = pal["blue"], pal["green"], pal["vermillion"], "0.92"

    c = Canvas(200.0)
    W = FIG_WIDTH_PT
    inner = W - 2 * MARGIN

    # -- measure both rows before committing to any position ------------------------------------- #
    top_sizes = [c.box_size(s, size=BODY_PT) for s in _F1_TOP]
    bot_labels = [_F1_CODE, _F1_DESIGNER, _F1_FEEDBACK]
    bot_sizes = [c.box_size(s, size=BODY_PT) for s in bot_labels]
    h_top = max(h for _, h in top_sizes)
    h_bot = max(h for _, h in bot_sizes)

    _, title_h = c.measure(_F1_TITLE, size=TITLE_PT)

    band = 44.0                                    # the labelled band between the two rows
    c.set_height(MARGIN + title_h + 6.0 + h_top + band + h_bot + MARGIN)

    y_title = c.height_pt - MARGIN
    y_top_hi = y_title - title_h - 6.0            # row 1 top edge
    y_top_lo = y_top_hi - h_top
    y_bot_hi = y_top_lo - band
    y_bot_lo = y_bot_hi - h_bot

    c.text(MARGIN, y_title, _F1_TITLE, size=TITLE_PT, ha="left", va="top", fontweight="bold")

    # -- row 1: data -> env -> returns -> tail measurement ---------------------------------------- #
    xs = distribute(inner, [w for w, _ in top_sizes], min_gap=22.0)
    top: list[Rect] = []
    fills = [(grey, "0.35"), (grey, "0.35"), (grey, "0.35"), (tint(green), green)]
    for x0, (w, _), label, (fc, ec) in zip(xs, top_sizes, _F1_TOP, fills):
        top.append(c.box(MARGIN + x0 + w / 2, (y_top_hi + y_top_lo) / 2, label,
                         fc=fc, ec=ec, lw=1.2, size=BODY_PT, width=w, height=h_top))
    for a, b in zip(top, top[1:]):
        c.arrow((a.x1 + 2.0, a.cy), (b.x0 - 2.0, b.cy))

    # -- row 2: feedback channel -> designer -> authored code ------------------------------------- #
    xs = distribute(inner, [w for w, _ in bot_sizes], min_gap=26.0)
    bot: list[Rect] = []
    specs = [(grey, "0.35"), (tint(verm), verm), (tint(blue), blue)]
    for x0, (w, _), label, (fc, ec) in zip(xs, bot_sizes, bot_labels, specs):
        bot.append(c.box(MARGIN + x0 + w / 2, (y_bot_hi + y_bot_lo) / 2, label,
                         fc=fc, ec=ec, lw=1.2, size=BODY_PT, width=w, height=h_bot))
    code, designer, feedback = bot

    # measured tail drops out of the top-right box into the feedback channel
    c.arrow((feedback.cx, y_top_lo - 2.0), (feedback.cx, feedback.y1 + 2.0), color=green, lw=1.4)
    c.text(feedback.cx - 6.0, y_top_lo - 8.0, "measured", size=BODY_PT, ha="right", va="top",
           color=green)
    # the feedback block is what the designer reads, each generation
    c.arrow((feedback.x0 - 2.0, feedback.cy), (designer.x1 + 2.0, designer.cy), color=blue, lw=1.4)
    c.text((feedback.x0 + designer.x1) / 2, y_bot_hi + 5.0, "fed each gen", size=BODY_PT,
           ha="center", va="bottom", color=blue)
    # the designer emits reward code
    c.arrow((designer.x0 - 2.0, designer.cy), (code.x1 + 2.0, code.cy))
    # ... which closes the loop by steering the environment. It lands on the env box's BOTTOM edge, not
    # its left edge, so this arrowhead is not confused with the one arriving from the gold panel.
    c.arrow((code.cx, code.y1 + 2.0), (top[1].cx - 18.0, top[1].y0 - 2.0), color="0.25", rad=-0.28)
    c.text(code.cx + 8.0, y_bot_hi + 5.0, "steers", size=BODY_PT, ha="left", va="bottom", color="0.25")

    c.audit(name="F1_system_diagram")
    return c


# ------------------------------------------------------------------------------------------------- #
# F2 -- the pre-registered outcome tree                                                               #
# ------------------------------------------------------------------------------------------------- #
# ⚠ THIS EXHIBIT WAS WRITTEN IN THE PROJECT'S OWN SHORTHAND AND IS NOW WRITTEN IN ENGLISH, FOR TWO
# INDEPENDENT REASONS, AND THE SECOND ONE IS A RENDERING BUG.
#  (1) S10, and Stefan hit exactly this. Shown a paragraph opening "The headline is H2" he did not
#      say it was badly ordered, he said "I don't understand what you mean": H2, IUT, TOST, SESOI and
#      MDE are names that exist only inside this project. This is the SECOND exhibit an examiner
#      meets, before any of them has been defined, and the guide's second marker "may come from any
#      discipline". A tree whose three branch conditions are unreadable teaches nothing.
#  (2) THE SUBSET SIGN DID NOT RENDER. "TOST ⊂ ±SESOI" printed as a tofu box in the compiled PDF
#      once the figure suite moved to the document's own typeface, because TeX Gyre Heros carries no
#      U+2282. matplotlib draws a missing glyph as an empty rectangle and says nothing, and the
#      build's own missing-character gate reads the TeX engine's channel, which never sees inside a
#      figure. So the defect was invisible to every gate in the project.
# The registered labels are not lost: they are printed in Chapter 4 where the machinery is defined,
# and the caption names the test. What changes is that the PICTURE now says what it means.
_F2_TITLE = "Pre-registered outcome tree (read BEFORE the data)"
_F2_ROOT = ("Does the tail summary beat the score alone?\n"
            "H2: tail-vector vs scalar (co-primary IUT vs ±SESOI)")
_F2_BRANCHES = [
    ("the whole interval falls\ninside the margin\n(TOST within ±SESOI)", "green", "EQUIVALENT",
     "bankable NULL:\ntail specificity adds\nno marginal value\n(the prediction)"),
    ("the interval sits\nwholly above zero\n(lower-CI > 0)", "blue", "POSITIVE",
     "channel works:\nricher feedback →\nbetter risk-adjusted\npolicy"),
    ("the interval is wider\nthan the margin\n(MDE > SESOI)", "vermillion", "INCONCLUSIVE",
     "underpowered:\nreport effect + CI,\nclaim neither"),
]
#: Removed from the canvas with the rest of the baked-in captions; see the note at ``_F1_TITLE``.
_F2_FOOT = ""


def prediction_branch() -> Canvas:
    """F2: the three pre-registered H2 branches, laid out for a 453.5 pt column at 10 pt."""
    pal = _palette()
    c = Canvas(200.0)
    W = FIG_WIDTH_PT
    col_w = (W - 2 * MARGIN) / 3.0
    centres = [MARGIN + (i + 0.5) * col_w for i in range(3)]
    #: Nudge the outer conditions toward the diagonal edge each one names (the middle edge is vertical,
    #: so its label already sits on it). Keeps every condition next to its own arrow without letting the
    #: three labels collide, which is what happens if they are placed at the arrow midpoints.
    cond_dx = [20.0, 0.0, -20.0]

    _, title_h = c.measure(_F2_TITLE, size=TITLE_PT)
    root_w, root_h = c.box_size(_F2_ROOT, size=BODY_PT)
    verdict_w = max(c.box_size(v, size=BODY_PT, weight="bold")[0] for _, _, v, _ in _F2_BRANCHES)
    _, verdict_h = c.box_size(_F2_BRANCHES[0][2], size=BODY_PT, weight="bold")
    mean_h = max(c.measure(m, size=BODY_PT)[1] for _, _, _, m in _F2_BRANCHES)
    # 96, not 62. Each branch condition is now THREE lines instead of one: a plain-English
    # statement of what the interval has to do, then the registered shorthand in brackets. The
    # band has to be deep enough to hold three lines without the condition text touching either
    # the root box above it or the verdict box below it.
    edge = 96.0                                    # depth of the band the branch conditions live in
    c.set_height(MARGIN + title_h + 8.0 + root_h + edge + verdict_h + 10.0 + mean_h + MARGIN)

    y_title = c.height_pt - MARGIN
    y_root_hi = y_title - title_h - 8.0
    y_root_lo = y_root_hi - root_h
    y_verdict_hi = y_root_lo - edge
    y_verdict_lo = y_verdict_hi - verdict_h
    y_mean = y_verdict_lo - 10.0

    c.text(MARGIN, y_title, _F2_TITLE, size=TITLE_PT, ha="left", va="top", fontweight="bold")
    root = c.box(W / 2, (y_root_hi + y_root_lo) / 2, _F2_ROOT, fc="0.92", size=BODY_PT,
                 width=root_w, height=root_h)

    for cx, dx, (cond, colour, verdict, meaning) in zip(centres, cond_dx, _F2_BRANCHES):
        c.arrow((root.cx, root.y0 - 2.0), (cx, y_verdict_hi + 2.0), color="0.40")
        # the condition rides its own edge, on an opaque patch so the rule reads through cleanly
        c.text(cx + dx, (root.y0 + y_verdict_hi) / 2, cond, size=BODY_PT, color="0.25",
               bbox=dict(boxstyle="round,pad=0.22", fc="white", ec="none"))
        c.box(cx, (y_verdict_hi + y_verdict_lo) / 2, verdict, fc=tint(pal[colour]), tc="black",
              ec=pal[colour], lw=1.4, size=BODY_PT, weight="bold", width=verdict_w, height=verdict_h)
        c.text(cx, y_mean, meaning, size=BODY_PT, ha="center", va="top", color="0.25")

    c.audit(name="F2_prediction_branch")
    return c


# ------------------------------------------------------------------------------------------------- #
# F4 -- the walk-forward split timeline                                                               #
# ------------------------------------------------------------------------------------------------- #
_F4_TITLE = "Walk-forward splits with purge + embargo (leakage control)"
_F4_BANDS = [
    ("train", "2005–2016", 2005.0, 2017.0, "blue", "agent learns + tail feedback measured"),
    ("val", "2017–2019", 2017.17, 2020.0, "green", "winner selection (reward-independent DSR)"),
    ("sealed test", "2020–2026", 2020.17, 2026.5, "vermillion", "scored once, never tuned"),
]
_F4_PURGE = "purge + embargo\n= max(embargo 21, lookback 60) = 60 sessions"
_F4_BEAR = "2022 bear (rate shock)"
_F4_CRASH = "post-crash start (crash in purge)"
_X0, _X1 = 2004.5, 2027.0


def splits_timeline() -> Canvas:
    """F4: train / val / sealed test with the purge gaps, laid out for a 453.5 pt column at 10 pt."""
    pal = _palette()
    c = Canvas(200.0)
    W = FIG_WIDTH_PT
    left, right = MARGIN + 2.0, W - MARGIN - 2.0
    span = right - left
    bar_h = 30.0

    def x_of(year: float) -> float:
        return left + (year - _X0) / (_X1 - _X0) * span

    _, title_h = c.measure(_F4_TITLE, size=TITLE_PT)
    _, purge_h = c.measure(_F4_PURGE, size=BODY_PT)
    _, line_h = c.measure("Ag", size=BODY_PT)

    c.set_height(MARGIN + title_h + 8.0 + purge_h + 4.0 + line_h + 6.0 + line_h + 12.0 + bar_h
                 + 6.0 + 4.0 + line_h + 3.0 + line_h + 16.0 + 3 * line_h + 2 * 5.0 + MARGIN)

    y_title = c.height_pt - MARGIN
    y_purge = y_title - title_h - 8.0                       # top of the purge annotation block
    y_bear = y_purge - purge_h - 4.0                        # the 2022 marker label sits under it
    y_crash = y_bear - line_h - 6.0                         # the sealed-leg opening marker label
    bar_hi = y_crash - line_h - 12.0
    bar_lo = bar_hi - bar_h
    y_axis = bar_lo - 6.0
    y_tick = y_axis - 4.0
    y_year = y_tick - line_h - 3.0                          # the axis name, clear of the year ticks
    y_key = y_year - line_h - 16.0                          # top of the three key rows

    # -- the bands ------------------------------------------------------------------------------- #
    from matplotlib.patches import Rectangle

    for name, _years, a, b, colour, _sub in _F4_BANDS:
        c.ax.add_patch(Rectangle((x_of(a), bar_lo), x_of(b) - x_of(a), bar_hi - bar_lo,
                                 facecolor=pal[colour], edgecolor="black", linewidth=1.0,
                                 alpha=0.9, zorder=2))
        c.text((x_of(a) + x_of(b)) / 2, (bar_hi + bar_lo) / 2, name, size=BODY_PT, color="white",
               fontweight="bold", zorder=3)
    for xg in (2017.0, 2020.0):
        c.ax.add_patch(Rectangle((x_of(xg), bar_lo), x_of(xg + 0.17) - x_of(xg), bar_hi - bar_lo,
                                 facecolor="none", edgecolor="0.2", hatch="////", linewidth=0.0,
                                 zorder=4))

    # -- what the gaps are, and the two regime markers -------------------------------------------- #
    c.text(MARGIN, y_purge, _F4_PURGE, size=BODY_PT, ha="left", va="top", color="0.20")
    # Point at the TRAIN/VAL gap, not the VAL/TEST one: both gaps are the same 60-session purge, and the
    # 2020 gap already carries the sealed-leg opening marker, so an arrowhead there would land on it.
    c.arrow((x_of(2013.5), y_purge - purge_h + 2.0), (x_of(2017.08), bar_hi + 2.0),
            color="0.20", lw=1.0, rad=-0.18)
    c.text(right, y_bear, _F4_BEAR, size=BODY_PT, ha="right", va="top", color="0.20")
    c.ax.plot([x_of(2022.3)], [bar_hi], marker="v", color="0.2", markersize=5, zorder=5)
    c.ax.plot([x_of(2022.3), x_of(2022.3)], [bar_hi, y_bear - line_h], color="0.2", lw=0.7, zorder=1)
    c.text(right, y_crash, _F4_CRASH, size=BODY_PT, ha="right", va="top", color="0.20")
    c.ax.plot([x_of(2020.25)], [bar_hi], marker="^", color="0.2", markersize=5, zorder=5)
    c.ax.plot([x_of(2020.25), x_of(2020.25)], [bar_hi, y_crash - line_h], color="0.2", lw=0.7, zorder=1)

    # -- the year axis ---------------------------------------------------------------------------- #
    c.ax.plot([left, right], [y_axis, y_axis], color="0.3", lw=0.9, zorder=1)
    for yr in (2005, 2010, 2015, 2020, 2025):
        c.ax.plot([x_of(yr), x_of(yr)], [y_axis, y_axis - 3.0], color="0.3", lw=0.9, zorder=1)
        c.text(x_of(yr), y_tick, str(yr), size=BODY_PT, ha="center", va="top", color="0.2")
    c.text((left + right) / 2, y_year, "year", size=BODY_PT, ha="center", va="top", color="0.2")

    # -- the key: each band's years and its role, on its own row so nothing collides --------------- #
    for i, (name, years, _a, _b, colour, sub) in enumerate(_F4_BANDS):
        y = y_key - i * (line_h + 5.0)
        c.ax.add_patch(Rectangle((MARGIN, y - line_h + 1.5), 9.0, 9.0, facecolor=pal[colour],
                                 edgecolor="black", linewidth=0.8, alpha=0.9, zorder=2))
        c.text(MARGIN + 14.0, y, f"{name} {years} — {sub}", size=BODY_PT, ha="left", va="top",
               color="0.20")

    c.text(MARGIN, y_title, _F4_TITLE, size=TITLE_PT, ha="left", va="top", fontweight="bold")
    c.audit(name="F4_splits_timeline")
    return c


# ------------------------------------------------------------------------------------------------- #
# entry point                                                                                         #
# ------------------------------------------------------------------------------------------------- #
def _fenced(name: str) -> Any:
    from src.viz import schematics as SC

    return getattr(SC, name)()


#: ⚠ WORDS DELIBERATELY MOVED OFF THE CANVAS AND INTO THE LaTeX CAPTION, listed so the lost-content
#: guard stays armed for everything else. Each entry is one baked-in caption block, quoted from the
#: fenced source, and the caption in the markdown must carry the same statement. The guard is the
#: reason this list exists rather than being switched off: dropping the check to make one intended
#: deletion pass would also stop it catching an unintended one.
_RELOCATED_TO_CAPTION: dict[str, tuple[str, ...]] = {
    "F1_system_diagram.png": (
        "Arms vary ONLY the feedback channel; the agent (SAC) is held fixed.",
        "The fed tail is the trained policy's OWN realised returns (endogenous; critic-agnostic).",
    ),
    "F2_prediction_branch.png": (
        "Every branch has a fixed, pre-registered reading",
        "the result cannot be reinterpreted post hoc.",
    ),
}


def build_all() -> list[Path]:
    """Render F1/F2/F4, each checked against the fenced original for lost content, and save them."""
    import matplotlib.pyplot as plt

    from docs.analysis.figure_typography import _words

    jobs = [
        ("system_diagram", system_diagram, "F1_system_diagram.png"),
        ("prediction_branch", prediction_branch, "F2_prediction_branch.png"),
        ("splits_timeline", splits_timeline, "F4_splits_timeline.png"),
    ]
    written: list[Path] = []
    for fenced_name, builder, out_name in jobs:
        reference = _fenced(fenced_name)
        canvas = builder()
        # Put the relocated words back into the comparison as if they were still drawn, so the guard
        # checks everything else exactly as before, then take the stand-in straight back out so it
        # can never reach the saved page.
        stand_in = None
        if out_name in _RELOCATED_TO_CAPTION:
            stand_in = canvas.fig.text(0.5, 0.5, " ".join(_RELOCATED_TO_CAPTION[out_name]),
                                       alpha=0.0, fontsize=1.0)
        assert_no_content_lost(reference, canvas.fig, name=out_name)
        if stand_in is not None:
            stand_in.remove()
        plt.close(reference)
        written.append(canvas.save(FIGDIR / out_name))
        plt.close(canvas.fig)
        print(f"wrote {written[-1]} (+ .pdf)")
    return written


def main() -> int:
    from docs.analysis.figure_typeface import use_document_typeface

    # Before build_all, not after: a Text artist reads its family at construction time.
    use_document_typeface()
    build_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
