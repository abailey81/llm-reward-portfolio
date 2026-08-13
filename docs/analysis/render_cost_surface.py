# -*- coding: utf-8 -*-
"""The registered transaction-cost grid, drawn flat, in two panels that share one axis.

⛔ THIS WAS A THREE-DIMENSIONAL SURFACE UNTIL 2026-08-13 AND THE SURFACE WAS THE DEFECT. Tamer read
the compiled exhibit and reported that he understood nothing from it, which is the only test that
matters, and the diagnosis is not a matter of taste. Four things were wrong at once, and each of
them is structural rather than a tuning problem:

  1. **A projected height cannot be measured.** The z-axis was drawn detached at the right margin,
     several inches from the surface it scaled, so the one question the exhibit existed to answer,
     "what does this cell earn", had no answer a reader could read off. The old docstring conceded
     this in its own first sentence and then argued the shape excused it. It does not.
  2. **Colour and height carried the SAME variable**, so two thirds of the ink encoded one number
     while the two-patch legend implied a categorical scale the continuous ramp did not have.
  3. **The measured data were invisible.** The 55 cells were the only real quantities in the panel
     and they were squeezed into a thin band at the back-left edge where they read as a line of
     specks, while a FITTED sheet dominated the canvas. The gross fit that generated more than half
     of that sheet has R2 = 0.38. The exhibit gave a weak fit the visual authority of a measurement.
  4. **The floor contour was a second coloured object in a second plane**, and nothing told the
     reader how it related to the first.

WHAT REPLACES IT, AND WHY THE REPLACEMENT NEEDS NO FIT AT ALL. Both panels are exact arithmetic on
measured cells. Nothing is smoothed, so the R2 = 0.38 problem disappears rather than being disclosed.

  **Upper panel, the fan.** One vertical spine per cell, carrying that cell's Sharpe at all five
  registered prices. At the left, where a policy trades under one per cent of the book a session,
  the five prices land on top of one another and the spine is a dot. At the right the same spine is
  a streak several Sharpe units long. The fan IS the mechanism, and the reader sees it in one look.

  **Lower panel, the practitioner's threshold.** How dear trading would have to become before each
  cell stopped paying, which is one division per cell and answers the only question a desk asks.
  Measured, it falls almost exactly in inverse proportion to turnover: log-log slope -0.964 at
  r = -0.996 over a 156-fold span.

Both panels share the turnover axis, so a cell sits at the same horizontal position in each and the
two views can be read against one another.

⚠ THE OTHER 3-D FIGURES IN THE REPOSITORY ARE NOT USABLE EITHER. `F_risk_return_generation_3d`
carries a red banner reading "SYNTHETIC DEMO DATA - NOT RESULTS", is an unreadable point cloud, and
its title overprints the banner. Wiring it would be a defect. This module reads the sealed archive.

HOW THE REPRICING IS DONE, AND WHY IT NEEDS NO RETRAINING. Cost is charged after the action, so the
gross return series is cost-independent and every cell can be repriced arithmetically. For a cell
with gross Sharpe `Sg`, net Sharpe `Sn` at the headline 10 bps and mean per-session turnover, the
Sharpe at any other cost level `c` is

    S(c) = Sg - (c / 10) * (Sg - Sn),

which is exact whenever the return standard deviation is unchanged by the cost subtraction.

⚠ THAT ASSUMPTION IS CHECKED RATHER THAN ASSERTED. `outputs/cost_sweep_run4/cost_sweep.json` holds
the same curve computed the hard way, series by series, on the confirmatory line. This module
reproduces it from the two-point rule and PRINTS THE DISAGREEMENT. Measured at the 50 bps rung, the
furthest extrapolation, the two routes agree to about a third of one per cent. If that ever exceeds
one per cent the surface is misleading and the module says so instead of drawing it.

Report-only. Gates nothing.
"""
from __future__ import annotations

import argparse
import io
import json
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
SWEEP = REPO / "outputs" / "cost_sweep_run4" / "cost_sweep.json"
FIG_DIR = REPO / "outputs" / "figures"

ARMS: tuple[str, ...] = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")
# ⚠ THESE STRINGS ARE CACHE KEYS, NOT DISPLAY LABELS, AND THEY MUST TRACK
# `render_results_figures.LINE_LABELS` EXACTLY. The cache is keyed "<line>|<arm>|<field>" and a key
# that does not match is SKIPPED SILENTLY by `_cells`, so a drifted name here does not raise: it
# quietly draws 50 cells instead of 55 and prints a smaller count nobody reads. The first entry read
# "opus-5 (core)" until 2026-08-12, when the display label lost its "(core)" tag; a run against the
# stale cache still printed 55 and would have started dropping that line at the next regeneration.
LINES: tuple[str, ...] = ("opus-5", "deepseek-v4-pro", "glm-5.2", "qwen3.6-27b", "qwen3.5-9b",
                          "haiku-4.5", "gpt-5.6-luna", "nemotron-3-super", "sonnet-5",
                          "gemini-2.5-flash", "kimi-k3")
#: The cost grid registered report-only in config/environment.yaml.
GRID_BPS = (0.0, 5.0, 10.0, 25.0, 50.0)
HEADLINE_BPS = 10.0

TEXT_WIDTH_PT = 453.6
FIG_WIDTH_IN = TEXT_WIDTH_PT / 72.0
#: The extrapolation is only honest while the two routes agree this closely.
TOLERANCE = 0.01


def iqm(x: np.ndarray) -> float:
    a = np.sort(np.asarray(x, dtype=float))
    k = a.size // 4
    return float(a[k:a.size - k].mean())


def _cells() -> list[dict[str, float | str]]:
    z = np.load(CACHE, allow_pickle=False)
    out: list[dict[str, float | str]] = []
    missing: list[str] = []
    for line in LINES:
        for arm in ARMS:
            key = f"{line}|{arm}"
            if f"{key}|turnover" not in z.files:
                # FAIL LOUD. This branch used to `continue`, which is how a renamed display label
                # would have removed a whole authoring line from the surface without a word.
                missing.append(key)
                continue
            out.append({"line": line, "arm": arm,
                        "turnover": iqm(z[f"{key}|turnover"]),
                        "gross": iqm(z[f"{key}|sharpe_gross"]),
                        "net10": iqm(z[f"{key}|sharpe_net"])})
    if missing:
        raise KeyError(
            f"{len(missing)} of {len(LINES) * len(ARMS)} (line, arm) cells are absent from "
            f"{CACHE.name}: {missing[:6]}{'...' if len(missing) > 6 else ''}. LINES here must match "
            f"render_results_figures.LINE_LABELS exactly; regenerate the cache or fix the names.")
    return out


def reprice(cell: dict[str, float | str], bps: np.ndarray) -> np.ndarray:
    """Sharpe at each cost level, from the cell's gross and its headline net."""
    drop = float(cell["gross"]) - float(cell["net10"])
    return float(cell["gross"]) - (bps / HEADLINE_BPS) * drop


def validate() -> float:
    """Reproduce the independently computed sweep and return the worst absolute disagreement."""
    if not SWEEP.exists():
        print(f"  !! {SWEEP} absent; the surface cannot be validated and is NOT drawn")
        raise SystemExit(2)
    curve = json.loads(SWEEP.read_text(encoding="utf-8"))["curve"]
    grid = np.asarray(curve["grid_bps"], dtype=float)
    worst = 0.0
    print(f"{'arm':<20}{'route':<12}" + "".join(f"{b:>9.0f}" for b in grid))
    for arm in ARMS:
        entry = curve["arms"].get(arm)
        if entry is None:
            continue
        direct = np.asarray(entry["sharpe"], dtype=float)
        i0, i10 = int(np.argmin(np.abs(grid - 0.0))), int(np.argmin(np.abs(grid - 10.0)))
        two_point = direct[i0] - (grid / HEADLINE_BPS) * (direct[i0] - direct[i10])
        worst = max(worst, float(np.max(np.abs(direct - two_point))))
        print(f"{arm:<20}{'series':<12}" + "".join(f"{v:>9.4f}" for v in direct))
        print(f"{'':<20}{'two-point':<12}" + "".join(f"{v:>9.4f}" for v in two_point))
    print(f"\nworst disagreement between the two routes: {worst:.4f} Sharpe "
          f"({'within' if worst <= TOLERANCE else 'OUTSIDE'} the {TOLERANCE} tolerance)")
    if worst > TOLERANCE:
        raise SystemExit("the two-point repricing does not reproduce the series computation; "
                         "the surface would misinform and is not drawn")
    return worst


def fit_surface(cells: list[dict[str, float | str]]) -> tuple[Any, Any, float, float, float, float]:
    """Fit the two functions of turnover that generate the whole surface, and report how well they fit.

    THE SURFACE IS NOT A SMOOTHER. It is the mechanism written down. Cost is charged after the action,
    so for one cell the Sharpe at cost ``c`` is exactly ``gross - (c/10) * drop``, where ``drop`` is
    what the headline 10 bps removed. Two quantities therefore generate the entire response over both
    inputs, and both are functions of a single number, how heavily the policy trades:

        G(tau)  the gross Sharpe, which the cost never touches
        D(tau)  the drop at 10 bps, which is what trading costs buy you

    Fitting those two and drawing ``S(tau, c) = G(tau) - (c/10) D(tau)`` gives a surface whose SHAPE
    is a claim about the mechanism, and the 55 measured cells are then drawn on top of it so a reader
    can see the residuals rather than take the fit on trust.

    Both fits are least squares in ``log10`` turnover, which is the scale the data live on: the cells
    span 0.57 to 88.9 per cent of the book per session, a factor of 156.
    """
    tau = np.array([float(c["turnover"]) for c in cells])
    gross = np.array([float(c["gross"]) for c in cells])
    drop = gross - np.array([float(c["net10"]) for c in cells])
    lx = np.log10(tau * 100.0)

    def _fit(y: np.ndarray, deg: int) -> tuple[Any, float]:
        coef = np.polyfit(lx, y, deg)
        pred = np.polyval(coef, lx)
        r2 = 1.0 - float(((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum())
        return coef, r2

    g_coef, g_r2 = _fit(gross, 2)
    d_coef, d_r2 = _fit(np.log10(drop), 1)     # drop is proportional to turnover, so linear in logs
    print(f"  G(tau): quadratic in log-turnover, R2 = {g_r2:.4f}")
    print(f"  D(tau): log-linear in log-turnover, R2 = {d_r2:.4f}  "
          f"(slope {d_coef[0]:.3f}; 1.0 would be exact proportionality)")
    return g_coef, d_coef, g_r2, d_r2, float(lx.min()), float(lx.max())


def facts(cells: list[dict[str, float | str]]) -> dict[str, object]:
    """Every number the exhibit annotates, computed from the cells rather than remembered.

    A figure that prints a measured quantity must derive it at draw time. Hard-coding "0.34" into a
    label is how a caption goes stale in silence when the archive is regenerated, and this suite has
    already lost a printed count that way once.
    """
    tau = np.array([float(c["turnover"]) for c in cells]) * 100.0
    gross = np.array([float(c["gross"]) for c in cells])
    net10 = np.array([float(c["net10"]) for c in cells])
    drag = gross - net10
    priced = {b: gross - (b / HEADLINE_BPS) * drag for b in GRID_BPS}
    # The cost at which each cell exactly breaks even. Sharpe is linear in the price, so this is one
    # division: S(c) = 0 at c = 10 * gross / drag. Exact, per cell, no fit.
    breakeven = HEADLINE_BPS * gross / drag
    lt, lb = np.log10(tau), np.log10(breakeven)
    slope, intercept = np.polyfit(lt, lb, 1)
    return {
        "tau": tau, "gross": gross, "net10": net10, "priced": priced, "breakeven": breakeven,
        "span": {b: float(v.max() - v.min()) for b, v in priced.items()},
        "losers": {b: int((v < 0.0).sum()) for b, v in priced.items()},
        "tau_ratio": float(tau.max() / tau.min()),
        "be_slope": float(slope), "be_intercept": float(intercept),
        "be_r": float(np.corrcoef(lt, lb)[0, 1]),
        "gross_r": float(np.corrcoef(lt, gross)[0, 1]),
    }


def build(out: Path = FIG_DIR) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from docs.analysis.figure_typeface import use_document_typeface
    from src.viz.style import OKABE_ITO, apply_house_style
    apply_house_style()
    use_document_typeface()   # the body typeface, so the exhibit matches the page it sits on
    matplotlib.rcParams.update({
        "font.size": 10.0, "axes.labelsize": 10.0, "legend.fontsize": 10.0,
        "xtick.labelsize": 9.0, "ytick.labelsize": 9.0,
        "figure.constrained_layout.use": False, "savefig.bbox": "tight",
    })

    worst = validate()
    cells = _cells()
    f = facts(cells)
    tau, gross, priced, be = f["tau"], f["gross"], f["priced"], f["breakeven"]

    # The two functions of turnover are still FITTED and PRINTED, and the contrast between them is
    # the whole finding: the drag tracks turnover at R2 = 0.99 while the gross Sharpe barely depends
    # on it. Nothing is DRAWN from either fit any more, which is what retires the R2 = 0.38 problem.
    _, _, g_r2, d_r2, _, _ = fit_surface(cells)

    # ⚠ ONE COLOUR PER PRICE, ORDERED LIGHT TO DARK, AND THE ORDER IS THE POINT. A reader must be
    # able to say which marker is the dearest price without consulting the legend, so the ramp is
    # monotone in the quantity it encodes. The 0 bps marker is hollow, which is the convention the
    # rest of this figure suite already uses for "gross of costs" (see F5_gross_vs_net).
    price_face = {0.0: "white", 5.0: "#FDBB84", 10.0: "#E34A33", 25.0: "#B30000", 50.0: "#4D0000"}
    price_edge = {0.0: "0.30", 5.0: "0.35", 10.0: "white", 25.0: "white", 50.0: "white"}

    from matplotlib import gridspec
    # ⭐ hspace 0.30, NOT 0.16, AND THE EXTRA GAP IS AN AXIS NAME RATHER THAN WHITE SPACE. Tamer read
    # the compiled exhibit and reported that one of its panels had no x axis label, and he was right:
    # the upper panel drew neither tick labels nor a name, on the theory that the panel below shares
    # the axis and names it for both. That reasoning holds only when two panels read as ONE object.
    # Here a second panel title sits between them, so the upper panel presented a horizontal spread
    # of 55 spines with no ruler and no name anywhere near it, and a reader had to travel past a
    # title and a whole second panel to discover what the horizontal position meant. Each panel now
    # carries its own complete axis. The five repeated tick values are a cheap price for a panel that
    # can be read where it sits.
    fig = plt.figure(figsize=(FIG_WIDTH_IN, 7.30))
    gs = gridspec.GridSpec(2, 1, height_ratios=(1.32, 1.00), hspace=0.30,
                           left=0.125, right=0.985, top=0.920, bottom=0.108)
    ax = fig.add_subplot(gs[0])
    bx = fig.add_subplot(gs[1], sharex=ax)

    # ---------------------------------------------------------------- upper panel: the fan
    # ⭐ THE SPINE IS THE EXHIBIT. Each cell contributes one vertical line running from its dearest
    # price to its cheapest, and the LENGTH of that line is what trading cost that cell. At the left
    # the line is shorter than the marker and reads as a dot; at the right it is several Sharpe units
    # long. Nothing else in this study makes the mechanism visible in a single glance.
    for i in range(tau.size):
        col = [priced[b][i] for b in GRID_BPS]
        ax.plot([tau[i], tau[i]], [min(col), max(col)], color="0.78", lw=0.8, zorder=1,
                solid_capstyle="round")
    for b in GRID_BPS:
        ax.scatter(tau, priced[b], s=27.0 if b == HEADLINE_BPS else 21.0,
                   facecolors=price_face[b], edgecolors=price_edge[b], linewidths=0.55,
                   zorder=4 if b == HEADLINE_BPS else 3, label=f"{b:g}")

    ax.axhspan(-7.0, 0.0, color=OKABE_ITO["vermillion"], alpha=0.045, lw=0, zorder=0)
    ax.axhline(0.0, color="0.15", lw=1.1, zorder=2)
    # ⚠ THIS LABEL SITS ON THE LEFT, AND THE SIDE IS NOT ARBITRARY. On the right it printed straight
    # through the two heaviest-trading spines, which are the only cells that cross the line and
    # therefore the only ones a reader looks at here.
    ax.text(0.012, 0.0, " break even", transform=ax.get_yaxis_transform(), ha="left",
            va="bottom", fontsize=8.8, color="0.30", zorder=6)

    # ⭐ THE LEGEND AND THE TAKEAWAY BOTH LIVE BELOW THE ZERO LINE ON THE LEFT, AND THAT WHOLE
    # QUADRANT IS EMPTY BY CONSTRUCTION rather than by luck: a cell that barely trades cannot lose
    # money to trading costs, at any price on the grid. Nothing will ever be drawn there.
    leg = ax.legend(loc="upper left", bbox_to_anchor=(0.012, 0.745), ncol=1, frameon=False,
                    fontsize=9.0, handletextpad=0.35, labelspacing=0.34, borderpad=0.0,
                    title="price charged\n(bps each way)")
    leg.get_title().set_fontsize(9.0)
    leg.get_title().set_color("0.30")
    leg.get_title().set_multialignment("left")

    ax.text(0.145, 0.055,
            f"Before costs the {tau.size} cells sit in a band {f['span'][0.0]:.2f} Sharpe wide.\n"
            f"Charge 50 bps and the same cells span {f['span'][50.0]:.2f}, and {f['losers'][50.0]} "
            f"of {tau.size} lose money.\nTrading buys nothing before costs. It only ever costs.",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=9.3, color="0.20",
            linespacing=1.45, zorder=6)
    ax.set_ylim(-6.5, 1.62)
    ax.set_ylabel("Sharpe, net of the price charged\n(annualised)")
    ax.set_title("Every cell priced five times over, one spine per cell", fontsize=10.5, pad=4)
    ax.set_xlabel("Turnover: share of the book traded per session (%), logarithmic")

    # ---------------------------------------------------------------- lower panel: the threshold
    # ⭐ EXACT, NOT FITTED. Sharpe is linear in the price, so the price at which a cell breaks even
    # is one division. This panel answers the only question a trading desk asks of the whole
    # chapter, and it answers it per cell rather than through a model.
    xs = np.array([tau.min() * 0.72, tau.max() * 1.30])
    bx.fill_between(xs, 3.0, HEADLINE_BPS, color=OKABE_ITO["vermillion"], alpha=0.10, lw=0, zorder=0)
    # ⛔ THE OTHER REGISTERED GRID LEVELS ARE NOT DRAWN HERE, AND LEAVING THEM OUT IS THE FIX. Faint
    # rules at 5, 25 and 50 bps carried no label a reader could decode, so they read as unexplained
    # furniture on a panel whose whole virtue is that every mark means something. The grid is stated
    # in the caption and drawn, colour-coded, in the panel above.
    bx.plot(xs, 10.0 ** (f["be_intercept"] + f["be_slope"] * np.log10(xs)),
            color="0.45", lw=1.0, ls=(0, (5, 2)), zorder=2)
    bx.axhline(HEADLINE_BPS, color="0.15", lw=1.3, zorder=3)
    bx.scatter(tau, be, s=26, facecolors=OKABE_ITO["blue"], edgecolors="white", linewidths=0.45,
               alpha=0.92, zorder=4)

    # ⚠ EVERY LABEL IN THIS PANEL IS PLACED AGAINST THE DATA'S OWN SHAPE, NOT BY EYE. The cloud runs
    # from upper left to lower right along a slope of -1, so exactly two large regions stay empty at
    # every redraw: the wedge above the cloud on the RIGHT, and the strip below the 10 bps line. The
    # first version put the takeaway bottom-left and the price label bottom-right, and both printed
    # straight through the line they were describing.
    bx.text(0.012, HEADLINE_BPS, " 10 bps, the price this study charges",
            transform=bx.get_yaxis_transform(), ha="left", va="bottom", fontsize=8.8, color="0.20",
            zorder=6)
    bx.text(0.985, 0.955,
            f"Only {f['losers'][10.0]} of {tau.size} cells break even below the price\n"
            f"this study charges. The threshold falls almost exactly\n"
            f"in proportion to turnover: log-log slope {f['be_slope']:.2f}, r = {f['be_r']:.3f}.",
            transform=bx.transAxes, ha="right", va="top", fontsize=9.3, color="0.20",
            linespacing=1.45, zorder=6)

    i_hi, i_lo = int(np.argmax(be)), int(np.argmin(be))
    bx.annotate(f"{tau[i_hi]:.2f}% a session survives to {be[i_hi]:.0f} bps",
                xy=(tau[i_hi], be[i_hi]), xytext=(tau[i_hi] * 1.45, be[i_hi] * 1.9),
                fontsize=8.6, color="0.30", ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color="0.55", lw=0.7, shrinkA=2, shrinkB=3))
    bx.annotate(f"{tau[i_lo]:.0f}% a session dies at {be[i_lo]:.1f} bps",
                xy=(tau[i_lo], be[i_lo]), xytext=(22.0, 6.4),
                fontsize=8.6, color="0.30", ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color="0.55", lw=0.7, shrinkA=2, shrinkB=3))

    bx.set_yscale("log")
    bx.set_ylim(5.0, 3200.0)
    bx.set_yticks([10, 30, 100, 300, 1000, 3000])
    bx.set_yticklabels(["10", "30", "100", "300", "1000", "3000"])
    bx.set_ylabel("The price at which this cell\nstops paying (bps each way)")
    bx.set_title("How dear trading would have to become before each cell stopped paying",
                 fontsize=10.5, pad=4)

    # ⚠ TICKS AT ROUND NUMBERS, NOT AT ROUND LOGARITHMS. A log locator left to itself prints
    # "3.16228" and "31.6228", which are decade roots rather than quantities anyone reads.
    # ⚠ AND THEY ARE SET ON BOTH AXES EXPLICITLY. `add_subplot(..., sharex=ax)` shares the limits and
    # the scale, but each Axis keeps its OWN locator and formatter, so setting fixed ticks on the
    # lower panel alone would have left the upper panel printing decade roots beneath the axis name
    # that was just added to it. Shared limits are not shared labels.
    bx.set_xscale("log")
    bx.set_xlim(*xs)
    bx.set_xlabel("Turnover: share of the book traded per session (%), logarithmic")

    for a in (ax, bx):
        a.set_xscale("log")
        a.set_xticks([0.5, 1, 3, 10, 30, 90])
        a.set_xticklabels(["0.5", "1", "3", "10", "30", "90"])
        a.minorticks_off()
        a.grid(True, which="major", color="0.92", lw=0.6)
        a.set_axisbelow(True)
        for side in ("top", "right"):
            a.spines[side].set_visible(False)

    fig.suptitle("One number decides every cell: how heavily its policy trades",
                 fontsize=11.5, y=0.978)

    out.mkdir(parents=True, exist_ok=True)
    png = out / "F5_cost_surface.png"
    fig.savefig(png, dpi=600)
    fig.savefig(png.with_suffix(".pdf"))
    plt.close(fig)
    print(f"\nwrote {png} (+ .pdf); {len(cells)} cells drawn as exact repricings, no fitted "
          f"geometry. Spans by price: " + ", ".join(f"{b:g} bps {f['span'][b]:.3f}" for b in GRID_BPS))
    print(f"  break-even threshold vs turnover: log-log slope {f['be_slope']:.3f}, r = {f['be_r']:.4f}")
    print(f"  gross Sharpe vs log turnover: r = {f['gross_r']:+.3f} (fits printed above: "
          f"gross R2 {g_r2:.3f}, drag R2 {d_r2:.3f}); repricing validated to {worst:.4f} Sharpe")
    return png


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
