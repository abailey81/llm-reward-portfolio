#!/usr/bin/env python3
"""Render the agent-environment diagram: the standard RL loop, wrapped in the designer loop.

WHY THIS EXHIBIT EXISTS, and it is asked for by two independent sources. Stefan's S3 asks for "a
universally recognised RL system diagram" so the work is not pattern-matched to "someone applied SAC
to a portfolio", and Tamer asked twice for the diagram the expose carried. C3 then fixes where it
goes: the frame precedes every parameter, split and budget, because a reader who meets a number
before the structure it sits in builds the wrong mental model and every later paragraph has to fight
it.

WHAT IT DRAWS, and the honest formalisation is two nested problems rather than one:

* the INNER problem is a genuine Markov decision process. State, action, transition, reward, solved
  by Soft Actor-Critic and held byte-identical across every arm. This is the Sutton-Barto loop a
  reinforcement-learning reader recognises on sight, drawn with our objects in it.
* the OUTER problem is a bandit over candidate reward programs. Its arms are programs, its payoff is
  the tail-blind validation fitness, and its proposal distribution is a language model conditioned on
  the fed block. Thirty pulls, no state evolution between candidates.

And the single edge that varies across experimental conditions is drawn as the only emphasised edge
in the figure. Everything else is common to all arms, which IS the identification argument, stated
graphically instead of in prose that costs words.

The layout is built on :mod:`docs.analysis.figure_typography`, whose ``Canvas.audit`` refuses to save
a figure with any label under 10 pt, any label outside its box, any label off the page, or any two
labels overlapping. Tamer's complaint about overlapping legends and unreadable small type is
therefore answered by construction here rather than by inspection.

Usage:
    python docs/analysis/render_rl_loop.py     # -> outputs/figures/F0_rl_loop.{png,pdf}
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from docs.analysis.figure_typography import (  # noqa: E402
    FIG_WIDTH_PT, MIN_PT, Canvas, distribute,
)

FIGDIR = REPO / "outputs" / "figures"

TITLE_PT = 11.0
BODY_PT = MIN_PT
EDGE_PT = MIN_PT

#: Okabe-Ito, the house palette. Imported lazily so the module can be read without matplotlib.
def _palette() -> dict[str, str]:
    from src.viz.style import OKABE_ITO

    return OKABE_ITO


def _row(c: Canvas, labels: list[str], *, y: float, margin: float, min_gap: float,
         padx: float = 11.0) -> list[tuple[float, float]]:
    """Left edges and widths for one row of boxes, spread across the column.

    Uses :func:`distribute`, which RAISES when the labels cannot fit at 10 pt rather than letting
    two boxes collide. A diagram that does not fit needs shorter labels, and finding that out at
    render time is the whole point.
    """
    widths = [c.box_size(s, size=BODY_PT, padx=padx)[0] for s in labels]
    lefts = distribute(FIG_WIDTH_PT - 2 * margin, widths, min_gap=min_gap)
    return [(margin + x, w) for x, w in zip(lefts, widths)]


def rl_loop() -> Canvas:
    """The nested loops, with the manipulated edge as the only emphasised one."""
    pal = _palette()
    blue = pal.get("blue", "#0072B2")
    orange = pal.get("vermillion", pal.get("orange", "#D55E00"))
    grey_fill = "#F2F2F2"
    band_fill = "#F7F7F7"

    H = 332.0
    c = Canvas(H)
    W = FIG_WIDTH_PT

    from matplotlib.patches import FancyBboxPatch

    def band(y0: float, y1: float) -> None:
        c.ax.add_patch(FancyBboxPatch((6.0, y0), W - 12.0, y1 - y0,
                                      boxstyle="round,pad=0,rounding_size=4.0",
                                      linewidth=0.8, facecolor=band_fill,
                                      edgecolor="0.78", zorder=0))

    # ----------------------------------------------------------------- title
    c.text(6.0, H - 6.0, "Two nested decision problems, and the one edge that varies",
           size=TITLE_PT, ha="left", va="top", fontweight="bold")

    # ================================================================= INNER
    inner_top, inner_bot = H - 28.0, 166.0
    band(inner_bot, inner_top)
    c.text(14.0, inner_top - 8.0, "Inner problem: a Markov decision process",
           size=BODY_PT, ha="left", va="top", fontweight="bold")

    cy = 240.0
    agent = c.box(112.0, cy, "Agent: the SAC policy", fc=grey_fill, size=BODY_PT, padx=13.0,
                  pady=8.0)
    envir = c.box(W - 112.0, cy, "Environment: 30 assets", fc=grey_fill, size=BODY_PT, padx=13.0,
                  pady=8.0)
    mid = (agent.x1 + envir.x0) / 2.0

    # action, left to right, above the axis of the two boxes
    y_act = cy + 24.0
    c.arrow((agent.x1 + 4.0, y_act), (envir.x0 - 4.0, y_act), color="0.25", lw=1.3)
    c.text(mid, y_act + 5.0, "action $a_t$: weights on the simplex", size=EDGE_PT, ha="center",
           va="bottom")

    # state and reward return together, the way Sutton and Barto draw the loop
    y_st = cy - 26.0
    c.arrow((envir.x0 - 4.0, y_st), (agent.x1 + 4.0, y_st), color=orange, lw=1.6)
    c.text(mid, y_st - 5.0, "state $s_{t+1}$, and reward $r_t = R(s_t, a_t)$", size=EDGE_PT,
           ha="center", va="top", color=orange)

    c.text(14.0, inner_bot + 8.0, "This loop is byte-identical in every arm.", size=EDGE_PT,
           ha="left", va="bottom", color="0.35", style="italic")

    # ================================================================= OUTER
    outer_top, outer_bot = 132.0, 10.0
    band(outer_bot, outer_top)
    c.text(14.0, outer_top - 8.0, "Outer problem: a bandit over candidate reward programs",
           size=BODY_PT, ha="left", va="top", fontweight="bold")

    oy = 62.0
    labels = ["Realised returns", "Reward designer", "$R$: a program"]
    slots = _row(c, labels, y=oy, margin=12.0, min_gap=30.0)
    ret = c.box(slots[0][0] + slots[0][1] / 2.0, oy, labels[0], fc=grey_fill, size=BODY_PT,
                padx=11.0, pady=8.0)
    des = c.box(slots[1][0] + slots[1][1] / 2.0, oy, labels[1], fc=blue, tc="white", size=BODY_PT,
                padx=11.0, pady=8.0)
    prog = c.box(slots[2][0] + slots[2][1] / 2.0, oy, labels[2], fc=grey_fill, size=BODY_PT,
                 padx=11.0, pady=8.0)

    # the manipulated edge: the only coloured, thick, bold-labelled edge in the figure
    c.arrow((ret.x1 + 4.0, oy), (des.x0 - 4.0, oy), color=orange, lw=2.4)
    c.text((ret.x1 + des.x0) / 2.0, oy + 17.0, "fed block $b_a$", size=EDGE_PT, ha="center",
           va="bottom", color=orange, fontweight="bold")

    c.arrow((des.x1 + 4.0, oy), (prog.x0 - 4.0, oy), color="0.25", lw=1.3)
    c.text((des.x1 + prog.x0) / 2.0, oy + 17.0, "writes", size=EDGE_PT, ha="center", va="bottom")

    c.text(14.0, outer_bot + 8.0, "The fed block is the only thing an arm changes.", size=EDGE_PT,
           ha="left", va="bottom", color=orange, style="italic")

    # ================================================== the two vertical links
    c.arrow((prog.cx, prog.y1 + 3.0), (prog.cx, inner_bot - 3.0), color=orange, lw=1.6)
    c.text(prog.cx - 6.0, inner_bot - 16.0, "installed as the reward", size=EDGE_PT,
           ha="right", va="center", color=orange)

    # ⚠ THIS LINK IS DRAWN IN TWO SEGMENTS, AND THE BREAK IS THE POINT. Drawn as one arrow it ran
    # straight through the bold heading "Outer problem: a bandit over candidate reward programs",
    # and the arrowhead landed on the "b" of "bandit" in the compiled figure. The heading starts at
    # the panel's left inset and the returns box sits under it, so there is no x where a straight
    # line clears both. A line that stops before a label and resumes after it is the ordinary
    # engineering-drawing convention for a link crossing an annotation, and it reads as one link.
    # The upper segment is headless; the lower one carries the head, so the direction still reads.
    c.arrow((ret.cx, inner_bot - 3.0), (ret.cx, outer_top + 2.0), color="0.25", lw=1.3, style="-")
    c.arrow((ret.cx, outer_top - 20.0), (ret.cx, ret.y1 + 3.0), color="0.25", lw=1.3)
    c.text(ret.cx + 6.0, inner_bot - 16.0, "read on the validation split", size=EDGE_PT,
           ha="left", va="center")

    c.audit(name="F0_rl_loop")
    return c


def main() -> int:
    import matplotlib.pyplot as plt

    from docs.analysis.figure_typeface import use_document_typeface

    use_document_typeface()
    FIGDIR.mkdir(parents=True, exist_ok=True)
    canvas = rl_loop()
    out = canvas.save(FIGDIR / "F0_rl_loop.png")
    plt.close(canvas.fig)
    print(f"wrote {out} (+ .pdf)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
