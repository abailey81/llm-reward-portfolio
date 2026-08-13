#!/usr/bin/env python3
"""Where the outcome variance actually comes from, drawn instead of only stated.

WHY THIS EXHIBIT EXISTS
-----------------------
`CLAUDE.md` (Okhrati's call summary, R7) calls the variance decomposition **the headline number of
the dissertation**: model identity explains roughly twice what the treatment does, and the
model-by-condition interaction is larger than either. Until now it appeared in the document only as
one sentence of §7.1 prose and a footnote of four intervals. A number that important with no exhibit
fails Law 1 of the project's own synthesis, "show the object, not only its summary", and it fails it
in the one place where showing it is FREE: UCL excludes figures from the word count (tension T3).

The reading it exists to make visible, in the corrected four-way form:

* **The interaction is the largest single component.** The reason there is no universally best
  feedback condition is not noise. It is a real, measured, model-dependent treatment effect, which is
  precisely Okhrati's own observation that "each model responds differently to the five feedback
  arms" appearing as a quantity.
* **Only 22.5 per cent is genuinely within-cell luck**, not the 57 per cent a two-way decomposition
  reports when it dumps the interaction into the residual.
* **And the four intervals OVERLAP.** The figure is drawn so that this is obvious rather than buried,
  because the only thing the data establish is that the interaction excludes small values. An exhibit
  that implied a clean ranking would be forcing a pattern the evidence does not carry (R1).

ONE COMPUTATION, TWO CONSUMERS
------------------------------
⚠ The point estimates and the intervals are computed HERE and printed, and §7.1's footnote quotes
what this prints. They are not computed twice. The arithmetic itself is imported from
`docs/analysis/abstract_quantities.variance_shares`, which is the instrument the abstract's own
quantities come from, so the figure cannot drift from the text by using a second implementation.
VERIFIED before this module was written: rebuilding the cell dictionary from the figure cache and
calling that function returns 27.9 / 14.8 / 34.8 / 22.5, which is what the document already prints.

    python docs/analysis/render_variance_shares.py
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="backslashreplace")
    except (AttributeError, ValueError):  # pragma: no cover
        pass

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

CACHE = REPO / "docs" / "analysis" / ".results_figure_cache.npz"
FIG_DIR = REPO / "outputs" / "figures"
TEXT_WIDTH_IN = 453.6 / 72.0
N_SEEDS = 102
#: The bootstrap seed is fixed so the printed intervals are reproducible and the footnote can quote them.
BOOT_SEED = 20260809
BOOT_REPS = 4000

#: Reader-facing names, ONE SHORT LINE EACH. The first draft gave each row a name plus a gloss on a
#: second line, and the longest ran to 47 characters: matplotlib sized the y-axis column to fit it,
#: the axes were squeezed into the right-hand third of the canvas, and the title and the x-label were
#: both cut off at the page edge. In a 453.6 pt column the tick column has to be short, and the gloss
#: belongs in the caption, which is word-excluded and read anyway.
LABEL = {
    "model": "author identity",
    "arm": "the feedback condition",
    "interaction": "author × condition",
    "residual": "seed noise",
}


def shares_with_intervals() -> tuple[dict[str, float], dict[str, tuple[float, float]], int]:
    """(point shares, 95% intervals, lines used), resampling the AUTHORING LINES.

    Resampling lines rather than seeds is the scheme the document states: a claim about automated
    reward design has to survive replacing the roster, not just replacing the seeds.
    """
    from docs.analysis.abstract_quantities import ARMS, variance_shares

    z = np.load(CACHE, allow_pickle=False)
    lines = sorted({k.split("|")[0] for k in z.files if "|" in k})
    cell: dict[tuple[str, str], dict[str, np.ndarray]] = {}
    for line in lines:
        for arm in ARMS:
            key = f"{line}|{arm}|sharpe_net"
            if key in z.files:
                cell[(line, arm)] = {"net": np.asarray(z[key], dtype=float)}
    full = [l for l in lines if all((l, a) in cell for a in ARMS)]
    if len(full) < 5:
        raise RuntimeError(f"only {len(full)} complete authoring lines in {CACHE.name}; "
                           f"regenerate it with render_results_figures.py --rebuild")

    point = variance_shares(cell, full, N_SEEDS)
    rng = np.random.default_rng(BOOT_SEED)
    draws: dict[str, list[float]] = {k: [] for k in LABEL}
    for _ in range(BOOT_REPS):
        pick = [full[i] for i in rng.integers(0, len(full), len(full))]
        resampled, names = {}, []
        for j, line in enumerate(pick):
            name = f"{line}#{j}"          # a line may be drawn twice; the names must stay distinct
            names.append(name)
            for arm in ARMS:
                resampled[(name, arm)] = cell[(line, arm)]
        v = variance_shares(resampled, names, N_SEEDS)
        for k in draws:
            draws[k].append(v[k])
    ci = {k: tuple(float(x) for x in np.percentile(draws[k], [2.5, 97.5])) for k in draws}
    return {k: float(point[k]) for k in LABEL}, ci, int(point["lines"])


def build(out: Path = FIG_DIR) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from docs.analysis.figure_typeface import use_document_typeface
    from src.viz.style import OKABE_ITO, apply_house_style

    apply_house_style()
    use_document_typeface()
    matplotlib.rcParams.update({
        "font.size": 10.0, "axes.titlesize": 11.0, "axes.labelsize": 10.0,
        "legend.fontsize": 10.0, "xtick.labelsize": 10.0, "ytick.labelsize": 10.0,
        "savefig.bbox": "standard",
    })

    point, ci, n_lines = shares_with_intervals()
    order = ["interaction", "model", "arm", "residual"]     # largest first, as measured
    colour = {"interaction": OKABE_ITO["blue"], "model": OKABE_ITO["green"],
              "arm": OKABE_ITO["vermillion"], "residual": OKABE_ITO["grey"]}

    # 2.85 in, not 3.35. MEASURED: at 3.35 the figure plus its caption needed 331 pt of a 725 pt
    # block and LaTeX gave it a page of its own, 142 words on page 80. Losing half an inch off the
    # interval panel costs nothing legible, because every value is also printed as text beside its
    # bar, and it is what lets the exhibit sit under the paragraph that cites it.
    # ⚠ 3.05 in, RAISED FROM 2.85, AND THE FOURTEEN POINTS BUY AN AXIS NAME. The composition strip
    # printed a ruler reading 0, 25, 50, 75, 100% with nothing anywhere saying what was being divided.
    # Tamer named that defect class on Figure 6.2 and it is the same one here: a reader met a
    # percentage scale and had to infer its subject. Naming it costs one line and closes it. The
    # 3.35 in version measured below still overflowed and is still out of reach, so the caption stays
    # on the same page. The build is re-checked rather than assumed.
    fig, axes = plt.subplots(2, 1, figsize=(TEXT_WIDTH_IN, 3.05),
                             height_ratios=(1.0, 2.6))

    # ---- the composition strip: one bar, four segments, so the whole adds to 100 visibly ----------
    top = axes[0]
    left = 0.0
    segments: list[tuple[float, float, str]] = []
    for key in order:
        w = point[key]
        top.barh([0], [w], left=left, height=0.62, color=colour[key], edgecolor="white", lw=1.0)
        segments.append((left + w / 2.0, w, key))
        left += w
    top.set_xlim(0, 100)
    # ⛔ THE "> 20 PER CENT" FLOOR IS GONE, AND IT WAS SUPPRESSING A NUMBER THAT FITS. The comment
    # that stood here argued a 14.8 per cent segment is 60 pt wide while "14.8%" is 27 pt, and then
    # concluded the label would not fit. Twenty-seven inside sixty leaves sixteen points of clearance
    # on each side. The measured axes is narrower than 60 pt per 14.8 per cent, but the label still
    # fits, and the segment it silenced is THE TREATMENT'S OWN SHARE, which is the one quantity this
    # dissertation exists to estimate. A stacked bar with an unlabelled band invites the reader to
    # wonder what it is, and this one left the answer off the most important band on the page.
    #
    # ⭐ THE REPLACEMENT MEASURES INSTEAD OF GUESSING. Each label is drawn, its rendered width read
    # back in data units, and kept inside the segment only if it clears both joins. Anything that
    # does not fit is moved above the bar in its own colour with a tick, so EVERY share is labelled
    # at every future value of the data, and no threshold has to be re-tuned when the shares move.
    top.set_ylim(-0.5, 1.30)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inv = top.transData.inverted()
    for cx, w, key in segments:
        t = top.text(cx, 0, f"{w:.1f}%", ha="center", va="center", color="white", fontsize=10)
        bb = t.get_window_extent(renderer=renderer)
        need = abs(inv.transform((bb.x1, 0))[0] - inv.transform((bb.x0, 0))[0])
        if need > w - 2.0:                      # 1 unit of clearance at each white separator
            t.remove()
            top.plot([cx, cx], [0.32, 0.58], color=colour[key], lw=0.9, zorder=3)
            top.text(cx, 0.66, f"{w:.1f}%", ha="center", va="bottom", color=colour[key], fontsize=10)
    top.set_yticks([])
    top.set_xticks([0, 25, 50, 75, 100])
    top.set_xticklabels(["0", "25", "50", "75", "100%"])
    # ⭐ THE STRIP NOW SAYS WHAT ITS PERCENTAGES ARE PERCENTAGES OF. It carried a 0 to 100% ruler and
    # named nothing, so a reader met a scale and had to work out its subject from the panel below.
    # The name is deliberately the SAME phrase the interval panel uses, because C1 says one object
    # takes one name: these are two views of a single quantity, not two quantities.
    top.set_xlabel("Share of the variance in terminal net Sharpe (%)", labelpad=2)
    top.grid(False)
    for side in ("left", "right", "top"):
        top.spines[side].set_visible(False)
    top.set_title("What actually moves the outcome, and how little of it is luck",
                  fontsize=11, loc="left")

    # ---- the intervals, which are the honest half of the exhibit ---------------------------------
    ax = axes[1]
    ys = np.arange(len(order))[::-1]
    for y, key in zip(ys, order):
        lo, hi = ci[key]
        ax.plot([lo, hi], [y, y], color=colour[key], lw=2.6, solid_capstyle="butt", zorder=2)
        ax.plot([lo, lo], [y - 0.13, y + 0.13], color=colour[key], lw=1.2, zorder=2)
        ax.plot([hi, hi], [y - 0.13, y + 0.13], color=colour[key], lw=1.2, zorder=2)
        ax.plot([point[key]], [y], marker="o", ms=6, color=colour[key], mec="white", mew=0.8,
                zorder=3)
        # The readings sit in a FIXED right-hand column rather than beside each bar's own end, so
        # they align into a small table the eye can scan down. Set beside the bar ends they
        # staircased, and the longest ran off the page.
        ax.text(97.0, y, f"{point[key]:.1f}%", va="center", ha="right", fontsize=10, color="0.15")
        ax.text(100.0, y, f"[{lo:.1f}, {hi:.1f}]", va="center", ha="left", fontsize=10, color="0.45")
    ax.set_yticks(ys)
    ax.set_yticklabels([LABEL[k] for k in order], fontsize=10)
    ax.set_ylim(-0.6, len(order) - 0.4)
    # The axis runs to 124 to hold the reading column, and the spine is bounded to the 0-50 the data
    # actually occupy, so the ruler never implies a scale the plot does not use.
    ax.set_xlim(0, 124)
    ax.set_xticks([0, 10, 20, 30, 40, 50])
    ax.spines["bottom"].set_bounds(0, 50)
    ax.set_xlabel("Share of the variance in terminal net Sharpe (%), with its 95% interval")
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", alpha=0.25)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)

    out.mkdir(parents=True, exist_ok=True)
    png = out / "F5_variance_shares.png"
    fig.savefig(png, dpi=600, bbox_inches=None, pad_inches=0.02, facecolor="white")
    fig.savefig(png.with_suffix(".pdf"), bbox_inches=None, pad_inches=0.02, facecolor="white")
    plt.close(fig)

    print(f"\n  over {n_lines} authoring lines at n = {N_SEEDS}, {BOOT_REPS} resamples, seed {BOOT_SEED}")
    print("  QUOTE THESE IN THE FOOTNOTE, so the figure and the text cannot diverge:")
    for k in ("model", "arm", "interaction", "residual"):
        lo, hi = ci[k]
        print(f"    {k:<12} {point[k]:5.1f} [{lo:.1f}, {hi:.1f}]")
    print(f"\nwrote {png} (+ .pdf) at {TEXT_WIDTH_IN * 72:.1f} pt wide")
    return png


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
