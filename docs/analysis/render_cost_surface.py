# -*- coding: utf-8 -*-
"""The registered transaction-cost grid as a response surface, in three dimensions.

WHY THIS EXHIBIT IS THREE-DIMENSIONAL, AND WHY THAT IS NOT DECORATION. A three-dimensional scatter
is almost always worse than two two-dimensional ones, because a reader cannot read a value off a
projected axis. This exhibit is not a scatter. It is a RESPONSE SURFACE over two genuinely
independent inputs, how heavily a policy trades and what trading costs, and the thing it shows is the
SHAPE of that surface: flat along the cost axis where turnover is low, and plunging where turnover is
high. That shape is the mechanism of this dissertation, and it cannot be drawn in one plane, because
each of the 55 cells has its own curve and the point is how those curves fan out.

⚠ THE EXISTING 3-D FIGURES IN THE REPOSITORY ARE NOT USABLE AND THIS ONE REPLACES THEM.
`F_risk_return_generation_3d` carries a red banner reading "SYNTHETIC DEMO DATA - NOT RESULTS", is an
unreadable point cloud, and its title overprints the banner. Wiring it would be a defect. This module
reads the sealed archive.

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
LINES: tuple[str, ...] = ("opus-5 (core)", "deepseek-v4-pro", "glm-5.2", "qwen3.6-27b", "qwen3.5-9b",
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
    for line in LINES:
        for arm in ARMS:
            key = f"{line}|{arm}"
            if f"{key}|turnover" not in z.files:
                continue
            out.append({"line": line, "arm": arm,
                        "turnover": iqm(z[f"{key}|turnover"]),
                        "gross": iqm(z[f"{key}|sharpe_gross"]),
                        "net10": iqm(z[f"{key}|sharpe_net"])})
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


def build(out: Path = FIG_DIR) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    worst = validate()
    cells = _cells()
    bps = np.linspace(0.0, 50.0, 26)

    from src.viz.style import apply_house_style
    apply_house_style()
    matplotlib.rcParams.update({
        "font.size": 10.0, "axes.labelsize": 10.0, "legend.fontsize": 10.0,
        "xtick.labelsize": 9.0, "ytick.labelsize": 9.0,
        "figure.constrained_layout.use": False, "savefig.bbox": "tight",
    })

    g_coef, d_coef, g_r2, d_r2, lo, hi = fit_surface(cells)

    # ⛔ A SURFACE, NOT FIFTY-FIVE RIBBONS. The first version of this exhibit drew one thin line per
    # cell, which is a bundle of curves rather than a response surface: the eye cannot integrate 55
    # overlapping strands into a shape, the strands hide one another wherever they cross, and the
    # thing the figure exists to show is precisely the SHAPE. It is drawn as a shape now, and the 55
    # measured cells sit on top of it as points, so the fit is shown together with its residuals
    # rather than asserted.
    fig = plt.figure(figsize=(FIG_WIDTH_IN, 5.15))
    ax = fig.add_subplot(111, projection="3d", computed_zorder=False)

    gx = np.linspace(lo, hi, 90)
    gy = np.linspace(0.0, 50.0, 60)
    X, Y = np.meshgrid(gx, gy)
    Z = np.polyval(g_coef, X) - (Y / HEADLINE_BPS) * (10.0 ** np.polyval(d_coef, X))

    zmin = -5.2
    Zc = np.clip(Z, zmin, None)
    cmap = plt.get_cmap("viridis")
    norm = plt.Normalize(zmin, float(np.nanmax(Z)))
    # !! `cmap=`/`norm=`, NOT `facecolors=`. Passing pre-computed face colours and then calling
    # `set_facecolor` to suppress the solid fallback renders the whole surface BLACK on matplotlib
    # 3.11: the second call overwrites the per-face array it was meant to preserve. Handing the
    # colormap to the artist is the supported route and the one that actually colours the faces.
    ax.plot_surface(X, Y, Zc, cmap=cmap, norm=norm, rstride=1, cstride=1,
                    linewidth=0, antialiased=True, alpha=0.95, shade=False, zorder=1)

    # The zero-Sharpe contour, projected onto the surface. This is the line a practitioner reads: on
    # its far side the cell has stopped paying for the trading it does.
    cs = ax.contour(X, Y, Zc, levels=[0.0], colors="white", linewidths=1.8, zorder=3)
    ax.contour(X, Y, Zc, levels=[0.0], colors="0.15", linewidths=0.7, zorder=4)

    # The 55 measured cells, at the two costs the archive actually holds: 0 bps (the gross series)
    # and the headline 10 bps. Everything between and beyond is the arithmetic the module validated.
    tx = np.log10(np.array([float(c["turnover"]) for c in cells]) * 100.0)
    ax.scatter(tx, np.zeros_like(tx), [float(c["gross"]) for c in cells],
               s=9, c="white", edgecolors="0.20", linewidths=0.5, depthshade=False, zorder=5)
    ax.scatter(tx, np.full_like(tx, HEADLINE_BPS), [float(c["net10"]) for c in cells],
               s=9, c="0.12", edgecolors="white", linewidths=0.4, depthshade=False, zorder=5)

    # Short axis labels. A 3-D axis label is drawn along a projected edge, so a long one sweeps
    # across the panel and lands on whatever is behind it; the units live in the caption instead.
    ax.set_xlabel("turnover per session (% of book)", labelpad=8)
    ax.set_ylabel("cost (bps each way)", labelpad=6)
    ax.set_zlabel("Sharpe", labelpad=-2)
    # ⚠ TICKS AT ROUND NUMBERS, NOT AT ROUND LOGARITHMS. Spacing the ticks evenly in log space
    # printed "3.16228" and "31.6228", which is a decade root and not a quantity anyone reads.
    # The positions are the logarithms of 1, 3, 10, 30 and 90 instead.
    decades = [v for v in (0.5, 1, 3, 10, 30, 90) if lo - 0.02 <= np.log10(v) <= hi + 0.02]
    ax.set_xticks([np.log10(v) for v in decades])
    ax.set_xticklabels([f"{v:g}" for v in decades])
    # 5 is dropped from the printed ticks. The registered grid is 0/5/10/25/50 and all five are
    # drawn, but at this view angle the 0, 5 and 10 labels land within a few points of one another at
    # the near corner and printed as "0 5 10" run together. The grid itself is stated in the caption.
    ax.set_yticks([b for b in GRID_BPS if b != 5.0])
    ax.set_zlim(zmin, 1.6)
    ax.view_init(elev=22, azim=-58)
    ax.set_box_aspect((1.35, 1.00, 0.66))
    ax.tick_params(pad=1.5)
    ax.set_title("The cost surface: what every cell earns at every price of trading",
                 fontsize=11, y=0.99)

    # The colourbar goes in its own axes on the LEFT, where the projection leaves a genuinely empty
    # wedge. On the right, which is the default, it printed straight through the z tick labels and
    # the z-axis label: a 3-D axes reserves no margin, so `pad` cannot move a bar out of the way.
    cax = fig.add_axes((0.055, 0.30, 0.018, 0.40))
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
    cb.set_label("Sharpe (annualised)", fontsize=9.6)
    cb.ax.tick_params(labelsize=9)
    cb.outline.set_linewidth(0.6)
    # The two marker classes and the contour are named here rather than on the canvas: a 3-D axes has
    # no empty corner that stays empty when the view angle changes.
    import matplotlib.lines as mlines
    fig.legend(handles=[
        mlines.Line2D([], [], ls="", marker="o", ms=4.5, mfc="white", mec="0.20",
                      label="a measured cell, gross (0 bps)"),
        mlines.Line2D([], [], ls="", marker="o", ms=4.5, mfc="0.12", mec="white",
                      label="the same cell at 10 bps"),
        mlines.Line2D([], [], color="0.15", lw=1.4, label="zero Sharpe"),
    ], loc="lower center", ncol=3, frameon=False, fontsize=9.6, bbox_to_anchor=(0.5, 0.005))
    # The 3-D axes is stretched to fill the canvas by hand. A projected cube leaves large empty
    # wedges at two corners whatever the view angle, so leaving the default position wastes roughly a
    # third of the figure; `bbox_inches="tight"` then crops the page rather than the axes and the
    # exhibit arrives on the page smaller than it needs to be.
    ax.set_position((0.03, 0.06, 0.99, 0.90))

    out.mkdir(parents=True, exist_ok=True)
    png = out / "F5_cost_surface.png"
    fig.savefig(png, dpi=600, bbox_inches=None, pad_inches=0.02)
    fig.savefig(png.with_suffix(".pdf"), bbox_inches=None, pad_inches=0.02)
    plt.close(fig)
    print(f"\nwrote {png} (+ .pdf); {len(cells)} cells on a surface fitted at "
          f"R2 = {g_r2:.3f} (gross) and {d_r2:.3f} (cost drag), validated to {worst:.4f} Sharpe")
    return png


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
