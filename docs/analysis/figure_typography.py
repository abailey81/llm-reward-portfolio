#!/usr/bin/env python3
"""Point-exact layout + typography toolkit for the vector schematic figures.

WHY THIS EXISTS. The dissertation includes every figure with pandoc's ``\\pandocbounded``, which scales
the image by ``min(textheight/H, linewidth/W)`` and never scales UP. With ``geometry:margin=2.5cm`` on
A4 the line width is :data:`TEXT_WIDTH_PT` = 453.5 pt, so a figure whose source page is ``W`` points wide
renders every one of its glyphs at ``size * 453.5 / W``. The schematics were authored on 8.0-10.3 inch
canvases, so their 6.5-9 pt labels arrived on the page at 3.0-7.8 pt against an IFTE0008 guideline of
Arial/Helvetica at >= 10 pt (measured on ``paper/_build/dissertation.pdf``, 2026-08-10).

THE FIX THIS TOOLKIT ENFORCES. Author the figure at EXACTLY :data:`FIG_WIDTH_IN` = 6.30 in, i.e. a page
453.6 pt wide, so the page scale factor is 1.000 and the authored point size IS the rendered point size.
Then no font may be smaller than :data:`MIN_PT`.

HOW. :class:`Canvas` puts a single full-bleed axes on the figure whose data units ARE typographic points
in both directions, so every layout number below is a real measurement on the printed page rather than an
abstract axis fraction. Boxes size themselves to their own text (:meth:`Canvas.box`), rows distribute the
slack that is left (:func:`distribute`), and :meth:`Canvas.audit` refuses to let a figure be saved with
undersized type, with text spilling out of its own box, or with two labels on top of each other.

Nothing here draws data. The data figure (F3) is repaired by mutation in ``render_f3_legible.py``.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

#: Line width of the dissertation body text: A4 (210 mm) less two 2.5 cm margins = 160 mm.
TEXT_WIDTH_PT = 453.5
#: Author every figure at EXACTLY that width, to the point, so the document's scale factor is 1.000 and
#: the authored point size is the rendered point size. Rounding this to 6.30 in (453.6 pt) instead makes
#: the factor 0.99978 and lands every 10 pt label on the page at 9.998 pt -- below the guideline by a
#: rounding error, which is still below the guideline.
FIG_WIDTH_PT = TEXT_WIDTH_PT
FIG_WIDTH_IN = FIG_WIDTH_PT / 72.0
#: IFTE0008 presentation guideline: Arial/Helvetica at >= 10 pt.
MIN_PT = 10.0
#: Tolerance (pt) for the geometry assertions -- below this an overlap is a rounding artefact, not ink.
EPS_PT = 0.5


@dataclass(frozen=True)
class Rect:
    """An axis-aligned rectangle in page points (origin bottom-left of the figure)."""

    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def w(self) -> float:
        return self.x1 - self.x0

    @property
    def h(self) -> float:
        return self.y1 - self.y0

    @property
    def cx(self) -> float:
        return 0.5 * (self.x0 + self.x1)

    @property
    def cy(self) -> float:
        return 0.5 * (self.y0 + self.y1)

    def overlap(self, other: "Rect") -> float:
        """Area of the intersection with ``other`` (0.0 when they are disjoint)."""
        dx = min(self.x1, other.x1) - max(self.x0, other.x0)
        dy = min(self.y1, other.y1) - max(self.y0, other.y0)
        return dx * dy if dx > 0 and dy > 0 else 0.0

    def contains(self, other: "Rect", *, slack: float = EPS_PT) -> bool:
        return (other.x0 >= self.x0 - slack and other.x1 <= self.x1 + slack
                and other.y0 >= self.y0 - slack and other.y1 <= self.y1 + slack)


def distribute(total: float, widths: Sequence[float], *, min_gap: float) -> list[float]:
    """Left edges that spread ``widths`` across ``total`` with equal gaps; raises when they cannot fit.

    Fails loudly rather than letting boxes collide: a schematic that does not fit at >= 10 pt needs its
    labels re-wrapped, and silently overlapping them is the defect this module exists to remove.
    """
    slack = total - sum(widths)
    n_gaps = len(widths) - 1
    gap = slack / n_gaps if n_gaps else 0.0
    if n_gaps and gap < min_gap - 1e-9:
        raise ValueError(
            f"cannot lay out {len(widths)} boxes in {total:.1f} pt: content is {sum(widths):.1f} pt, "
            f"leaving {gap:.1f} pt gaps (need >= {min_gap:.1f}). Re-wrap the longest label."
        )
    out, x = [], 0.0
    for w in widths:
        out.append(x)
        x += w + gap
    return out


class Canvas:
    """A figure exactly :data:`FIG_WIDTH_IN` wide whose data coordinates are page points.

    ``Canvas(height_pt)`` gives a drawing surface ``FIG_WIDTH_PT x height_pt``; every ``x``/``y`` passed
    to the drawing methods is therefore a position ON THE PRINTED PAGE, and every returned
    :class:`Rect` is a real printed extent. Track artists as they are drawn so :meth:`audit` can check
    them; drawing outside these methods is allowed (arrows, patches) but is not audited.
    """

    def __init__(self, height_pt: float) -> None:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        self.height_pt = float(height_pt)
        self.fig = plt.figure(figsize=(FIG_WIDTH_IN, self.height_pt / 72.0))
        self.ax = self.fig.add_axes((0.0, 0.0, 1.0, 1.0))
        self.ax.set_xlim(0.0, FIG_WIDTH_PT)
        self.ax.set_ylim(0.0, self.height_pt)
        self.ax.axis("off")
        self._texts: list[Any] = []
        self._boxes: list[tuple[Rect, Any]] = []  # (box rect, its text artist)

    def set_height(self, height_pt: float) -> None:
        """Re-declare the canvas height, BEFORE anything is drawn.

        Text metrics depend only on the point size and the dpi, never on the figure's height, so a
        builder can measure its blocks on a provisional canvas, add them up, and only then commit to a
        height that leaves no dead strip at the bottom. Drawing first and resizing after would silently
        move every artist, since positions are absolute points measured from the bottom edge.
        """
        if self._texts or self._boxes:
            raise RuntimeError("set_height() must be called before anything is drawn")
        self.height_pt = float(height_pt)
        self.fig.set_size_inches(FIG_WIDTH_IN, self.height_pt / 72.0)
        self.ax.set_ylim(0.0, self.height_pt)

    # -- measurement ------------------------------------------------------------------------------ #
    def _renderer(self) -> Any:
        return renderer_for(self.fig)

    def extent(self, artist: Any) -> Rect:
        """Printed extent of ``artist`` in page points."""
        bb = artist.get_window_extent(renderer=self._renderer())
        k = 72.0 / self.fig.dpi
        return Rect(bb.x0 * k, bb.y0 * k, bb.x1 * k, bb.y1 * k)

    def measure(self, s: str, *, size: float, weight: str = "normal", style: str = "normal") -> tuple[float, float]:
        """(width, height) in points that ``s`` will occupy -- measured, never estimated."""
        t = self.ax.text(0.0, 0.0, s, fontsize=size, fontweight=weight, style=style)
        r = self.extent(t)
        t.remove()
        return r.w, r.h

    # -- drawing ---------------------------------------------------------------------------------- #
    def text(self, x: float, y: float, s: str, *, size: float = MIN_PT, ha: str = "center",
             va: str = "center", audit: bool = True, **kw: Any) -> Any:
        t = self.ax.text(x, y, s, fontsize=size, ha=ha, va=va, **kw)
        if audit:
            self._texts.append(t)
        return t

    def box(self, cx: float, cy: float, label: str, *, fc: str, tc: str = "black", size: float = MIN_PT,
            padx: float = 9.0, pady: float = 7.0, ec: str = "black", lw: float = 1.0,
            weight: str = "normal", width: float | None = None, height: float | None = None) -> Rect:
        """A rounded box sized to its own text (or to ``width``/``height``), centred on ``(cx, cy)``."""
        from matplotlib.patches import FancyBboxPatch

        tw, th = self.measure(label, size=size, weight=weight)
        w = width if width is not None else tw + 2 * padx
        h = height if height is not None else th + 2 * pady
        r = Rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
        self.ax.add_patch(FancyBboxPatch((r.x0, r.y0), r.w, r.h,
                                         boxstyle="round,pad=0,rounding_size=3.0",
                                         linewidth=lw, facecolor=fc, edgecolor=ec, zorder=2))
        t = self.text(cx, cy, label, size=size, color=tc, zorder=3, fontweight=weight, audit=False)
        self._boxes.append((r, t))
        return r

    def box_size(self, label: str, *, size: float = MIN_PT, padx: float = 9.0, pady: float = 7.0,
                 weight: str = "normal") -> tuple[float, float]:
        """The (width, height) :meth:`box` would use -- for laying a row out before drawing it."""
        tw, th = self.measure(label, size=size, weight=weight)
        return tw + 2 * padx, th + 2 * pady

    def arrow(self, p0: tuple[float, float], p1: tuple[float, float], *, color: str = "0.25",
              lw: float = 1.2, rad: float = 0.0, style: str = "-|>") -> None:
        self.ax.annotate("", xy=p1, xytext=p0,
                         arrowprops=dict(arrowstyle=style, color=color, lw=lw, shrinkA=0, shrinkB=0,
                                         connectionstyle=f"arc3,rad={rad}"), zorder=1)

    # -- verification ----------------------------------------------------------------------------- #
    def audit(self, *, name: str) -> None:
        """Raise unless every label is >= 10 pt, inside its box, and clear of every other label."""
        problems: list[str] = []
        artists = [t for t in self._texts] + [t for _, t in self._boxes]
        for t in artists:
            if t.get_fontsize() < MIN_PT - 1e-9:
                problems.append(f"{t.get_text()[:32]!r} is {t.get_fontsize():.2f} pt (< {MIN_PT})")
        for r, t in self._boxes:
            if not r.contains(self.extent(t)):
                e = self.extent(t)
                problems.append(
                    f"text {t.get_text()[:32]!r} ({e.w:.1f}x{e.h:.1f} pt) spills out of its "
                    f"{r.w:.1f}x{r.h:.1f} pt box")
        page = Rect(0.0, 0.0, FIG_WIDTH_PT, self.height_pt)
        for t in artists:
            e = self.extent(t)
            if not page.contains(e, slack=1.0):
                problems.append(f"{t.get_text()[:32]!r} runs off the page ({e.x0:.1f}..{e.x1:.1f} pt)")
        for i, a in enumerate(artists):
            for b in artists[i + 1:]:
                ov = self.extent(a).overlap(self.extent(b))
                if ov > EPS_PT:
                    problems.append(
                        f"{a.get_text()[:28]!r} overlaps {b.get_text()[:28]!r} by {ov:.1f} pt^2")
        if problems:
            raise RuntimeError(f"[{name}] layout audit failed:\n  - " + "\n  - ".join(problems))

    # -- output ----------------------------------------------------------------------------------- #
    def save(self, png_path: Path | str) -> Path:
        """Write PNG (600 dpi) + the vector PDF sibling at EXACTLY the authored page size.

        ``bbox_inches`` is deliberately NOT ``"tight"``: a tight crop changes the saved page width, and
        the whole repair depends on that width being 6.30 in so the document's scale factor is 1.000.
        """
        p = Path(png_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        self.fig.savefig(p, dpi=600, bbox_inches=None, pad_inches=0.0, facecolor="white")
        self.fig.savefig(p.with_suffix(".pdf"), bbox_inches=None, pad_inches=0.0, facecolor="white")
        return p


def renderer_for(fig: Any) -> Any:
    """A renderer able to measure text on ``fig``, whatever backend built it.

    A figure that has been through ``plt.close`` under a GUI backend is left holding a plain
    ``FigureCanvasBase``, which cannot measure or draw; re-binding an Agg canvas restores both and does
    not affect ``savefig``, which selects a canvas per output format anyway.
    """
    get = getattr(fig.canvas, "get_renderer", None)
    if get is None:
        from matplotlib.backends.backend_agg import FigureCanvasAgg

        FigureCanvasAgg(fig)  # rebinds fig.canvas
        get = fig.canvas.get_renderer
    return get()


def wrap_to_width(fig: Any, text: str, *, size: float, max_pt: float, weight: str = "normal") -> str:
    """Re-flow ``text`` so no line is wider than ``max_pt``, breaking only between words.

    Line breaks already in ``text`` are kept as hard breaks (they separate a panel's title from its
    "so what" line, or one annotated fact from the next), and each such paragraph is re-flowed
    independently. Widths are MEASURED with the real font, not estimated from a character count, so this
    is exact for the mixed digits, Greek and mathematical signs these figures carry.

    A single word wider than ``max_pt`` is emitted on its own line rather than broken: hyphenating
    ``kurtosis`` or a number would change what the figure says.
    """
    ax = fig.axes[0] if fig.axes else fig
    renderer = renderer_for(fig)
    k = 72.0 / fig.dpi

    def width(s: str) -> float:
        t = ax.text(0.0, 0.0, s, fontsize=size, fontweight=weight)
        w = t.get_window_extent(renderer=renderer).width * k
        t.remove()
        return w

    def flow(para: str, budget: float) -> list[str]:
        lines: list[str] = []
        line = ""
        for word in para.split(" "):
            trial = word if not line else f"{line} {word}"
            if line and width(trial) > budget:
                lines.append(line)
                line = word
            else:
                line = trial
        lines.append(line)
        return lines

    out: list[str] = []
    for para in text.split("\n"):
        lines = flow(para, max_pt)
        # Balance: greedy flow leaves orphans ("...clusters, not" / "uniformly"), which read as an
        # error rather than a line break. Narrow the budget while the LINE COUNT is unchanged and keep
        # the tightest such flow -- same height, evener lines, and never an extra line.
        if len(lines) > 1:
            best = lines
            for shrink in (0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60):
                candidate = flow(para, max_pt * shrink)
                if len(candidate) != len(lines):
                    break
                best = candidate
            lines = best
        out.extend(lines)
    return "\n".join(out)


# ------------------------------------------------------------------------------------------------- #
# Drift guard: the repaired figure must still SAY everything the fenced figure said                   #
# ------------------------------------------------------------------------------------------------- #
_WORD = re.compile(r"[0-9A-Za-zÀ-ɏͰ-Ͽ%/]+")


def _words(strings: Iterable[str]) -> Counter:
    bag: Counter = Counter()
    for s in strings:
        bag.update(w.lower() for w in _WORD.findall(s))
    return bag


def figure_words(fig: Any) -> Counter:
    """Bag of words over every text artist on ``fig`` (line breaks and punctuation normalised away)."""
    texts = list(fig.texts)
    for ax in fig.axes:
        texts.extend(ax.texts)
        if ax.get_title():
            texts.append(ax.title)
    return _words(t.get_text() if hasattr(t, "get_text") else str(t) for t in texts)


def assert_no_content_lost(reference: Any, rebuilt: Any, *, name: str) -> None:
    """Raise if the rebuilt figure dropped any word the fenced original carried.

    Re-wrapping a label, moving a date from a bar into a key row, or splitting a sentence over two lines
    all leave this invariant untouched; deleting a caption, a branch or a number does not. Extra words in
    the rebuild are allowed (a re-layout may add a connective), so this is a one-sided check by design.
    """
    want, got = figure_words(reference), figure_words(rebuilt)
    missing = want - got
    if missing:
        detail = ", ".join(f"{w} x{n}" for w, n in sorted(missing.items()))
        raise RuntimeError(f"[{name}] the rebuild lost content the fenced figure carried: {detail}")
