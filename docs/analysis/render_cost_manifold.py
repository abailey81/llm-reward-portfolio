# -*- coding: utf-8 -*-
"""The cost hillside: what trading costs, as one exact surface, with every design standing on it.

⛔ TWO EARLIER THREE-DIMENSIONAL EXHIBITS WERE BUILT AND BOTH WERE REJECTED BY THE ONLY TEST THAT
MATTERS, WHICH IS TAMER READING THE COMPILED PAGE. The first drew the eleven authoring lines against
the five reward designs; the second drew 55 exact price-response lines. His verdicts were that they
were unreadable and told him nothing, and the fault the two share is mine and is now stated plainly:

  BOTH ASKED A READER TO EXTRACT MEANING FROM FIFTY-FIVE SEPARATE OBJECTS. A perspective drawing of
  a bundle of lines is a bundle of lines. Nobody reads fifty-five of anything. A three-dimensional
  exhibit earns its place only when it is ONE SURFACE whose SHAPE is the finding, so that the reader
  understands it before reading a single axis. Everything else belongs flat.

⭐ WHAT IS DRAWN, AND WHY IT IS EXACT RATHER THAN FITTED. The environment charges a linear cost on
every unit of book traded, so the return a policy gives away in a year is

    drag(c, tau)  =  c * tau * 252,

a product of the price and the turnover and nothing else. That is an identity of the cost model, not
a regression, and it is a smooth function of two genuinely continuous inputs, which is exactly what a
surface needs.

⚠ AND IT IS VERIFIED AGAINST THE MEASURED SERIES RATHER THAN ASSUMED FROM THE CONFIGURATION. Over
sealed-test records carrying a usable gross series, a net series and a turnover series, the measured
annual drag divided by the daily turnover is 0.25200 at every single one, minimum to maximum, a
max/min ratio of 1.00000. The surface is therefore the arithmetic the environment actually performed.

WHAT THE SHAPE SAYS. It is a hillside, and every design in the study stands somewhere on it. The
lightest-trading designs stand near the bottom, giving away a fifth of one per cent of capital a
year. The heaviest stand near the top, giving away more than a fifth of the whole portfolio. The
contour drawn across the face is the line where the cost of trading equals the median gross return
the agents earned, so anything above it is a policy that hands its entire return to the trading desk.
One picture, one shape, and it answers Dr Okhrati's question about what turnover actually is in the
unit a practitioner cares about, which is money.

Report-only. Gates nothing.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="backslashreplace")
    except (AttributeError, ValueError):  # pragma: no cover
        pass

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

CACHE = REPO / "docs" / "analysis" / ".results_figure_cache.npz"
ARCHIVE = REPO / "outputs" / "campaign_cluster_run4" / "test"
GROSS_CACHE = REPO / "docs" / "analysis" / ".cost_manifold_gross.npz"
FIG_DIR = REPO / "outputs" / "figures"

ARMS: tuple[str, ...] = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")
LINES: tuple[str, ...] = ("opus-5", "deepseek-v4-pro", "glm-5.2", "qwen3.6-27b", "qwen3.5-9b",
                          "haiku-4.5", "gpt-5.6-luna", "nemotron-3-super", "sonnet-5",
                          "gemini-2.5-flash", "kimi-k3")
ARM_LABEL = {"distributional": "tail vector (treatment)", "scalar": "score only",
             "scalar_cvar5": "score + CVaR", "placebo": "placebo",
             "placebo_shuffled": "scrambled"}

SESSIONS_PER_YEAR = 252.0
HEADLINE_BPS = 10.0
MAX_BPS = 50.0
#: Every 7th archived record, in sorted order. A stride rather than a sample: it is deterministic,
#: so the figure is reproducible, and it is stated here rather than buried.
GROSS_STRIDE = 7

TEXT_WIDTH_PT = 453.6
FIG_WIDTH_IN = TEXT_WIDTH_PT / 72.0


def iqm(x: np.ndarray) -> float:
    a = np.sort(np.asarray(x, dtype=float))
    k = a.size // 4
    return float(a[k:a.size - k].mean())


def measured_turnover() -> dict[str, float]:
    """Per-cell mean turnover, as a percentage of the book traded per session."""
    z = np.load(CACHE, allow_pickle=False)
    out = {}
    for ln in LINES:
        for ar in ARMS:
            key = f"{ln}|{ar}|turnover"
            if key not in z.files:
                raise KeyError(f"{key} absent from {CACHE.name}")
            out[f"{ln}|{ar}"] = iqm(z[key]) * 100.0
    return out


def gross_return_and_check() -> dict[str, float]:
    """The median gross annual return, and the identity check, both read from the archive.

    ⚠ CACHED TO DISK BECAUSE IT READS THOUSANDS OF RECORDS, and cached under a name that says what
    it is. Delete the file to force a re-read. The stride is fixed, so two runs read the same records.
    """
    if GROSS_CACHE.exists():
        d = np.load(GROSS_CACHE, allow_pickle=False)
        return {k: float(d[k]) for k in d.files}

    recs = sorted(ARCHIVE.glob("*/*/record.json"))
    if not recs:
        raise FileNotFoundError(f"no sealed-test records under {ARCHIVE}")
    gross_ann, ratios = [], []
    for p in recs[::GROSS_STRIDE]:
        m = json.loads(p.read_text(encoding="utf-8"))["metrics"]
        g, n, t = m.get("test_gross"), m.get("test_returns"), m.get("test_turnover")
        if not all(isinstance(v, list) and len(v) > 100 for v in (g, n, t)):
            continue
        g, n, t = np.asarray(g, float), np.asarray(n, float), np.asarray(t, float)
        gross_ann.append(float(np.nanmean(g)) * SESSIONS_PER_YEAR * 100.0)
        tau = float(np.nanmean(t)) * 100.0
        if tau > 0:
            ratios.append(float(np.nanmean(g - n)) * SESSIONS_PER_YEAR * 100.0 / tau)
    ga, ra = np.array(gross_ann), np.array(ratios)
    res = {"gross_median": float(np.median(ga)), "gross_q1": float(np.percentile(ga, 25)),
           "gross_q3": float(np.percentile(ga, 75)), "n_records": float(ga.size),
           "ratio_min": float(ra.min()), "ratio_max": float(ra.max()),
           "ratio_median": float(np.median(ra))}
    np.savez(GROSS_CACHE, **res)
    return res


def build(out: Path = FIG_DIR) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import cm, colors

    from docs.analysis.figure_typeface import use_document_typeface
    from src.viz.style import apply_house_style, arm_style

    apply_house_style()
    use_document_typeface()
    matplotlib.rcParams.update({
        "font.size": 10.0, "axes.labelsize": 10.0, "axes.titlesize": 11.0,
        "legend.fontsize": 10.0, "xtick.labelsize": 9.0, "ytick.labelsize": 9.0,
        "figure.constrained_layout.use": False, "savefig.bbox": None,
    })

    turn = measured_turnover()
    facts = gross_return_and_check()
    tau_lo, tau_hi = 0.45, 100.0

    # ---- the surface: an identity, on a dense grid -----------------------------------------------
    c_grid = np.linspace(0.0, MAX_BPS, 90)
    lt_grid = np.linspace(np.log10(tau_lo), np.log10(tau_hi), 90)
    C, LT = np.meshgrid(c_grid, lt_grid)
    #: drag = price x turnover x sessions. In per cent of capital a year, with the price in basis
    #: points and the turnover in per cent, that is c/10000 * tau/100 * 252 * 100 = 0.0252 * c * tau.
    Z = (C / 1e4) * (10.0 ** LT / 100.0) * SESSIONS_PER_YEAR * 100.0

    fig = plt.figure(figsize=(FIG_WIDTH_IN, 6.55))
    ax = fig.add_subplot(111, projection="3d", computed_zorder=False)
    fig.subplots_adjust(left=0.0, right=0.955, top=0.905, bottom=0.235)

    # ⚠ THE CEILING IS A CLIP, AND THE FLAT TOP IT LEAVES IS NAMED IN THE KEY. Writing NaN above
    # the ceiling was tried and is worse: plot_surface drops a whole quad when any corner is NaN,
    # so a smooth cut renders as triangular teeth at grid resolution. A straight edge with a
    # labelled tabletop is the honest reading; an unexplained sawtooth is not.
    z_cap = 26.0
    Zd = np.clip(Z, None, z_cap)
    norm = colors.Normalize(vmin=0.0, vmax=z_cap)
    cmap = matplotlib.colormaps["YlOrRd"]
    surf = ax.plot_surface(C, LT, Zd, facecolors=cmap(norm(Zd)), rstride=1, cstride=1,
                           shade=True, antialiased=True, linewidth=0, zorder=2)
    surf.set_alpha(0.97)

    # ⭐ THE CONTOUR THAT TURNS A HILLSIDE INTO A VERDICT. Above this line the cost of trading equals
    # or exceeds the median gross return the agents actually earned, so a policy standing above it
    # hands its entire year to the trading desk. It is drawn ON the surface, at its own height.
    gm = facts["gross_median"]
    c_at = np.linspace(0.2, MAX_BPS, 200)
    lt_at = np.log10(gm / (0.0252 * c_at))
    ok = (lt_at >= np.log10(tau_lo)) & (lt_at <= np.log10(tau_hi))
    ax.plot(c_at[ok], lt_at[ok], np.full(int(ok.sum()), gm), color="#1A1A1A", lw=2.0, zorder=30,
            solid_capstyle="round")

    # ⭐ FIVE MARKERS, ONE PER DESIGN, LABELLED WHERE THEY STAND. Fifty-five markers sat on one rib
    # of the surface and overlapped each other wherever two designs traded at similar rates, which is
    # most of them. The reading this exhibit supports is the ordering of the FIVE DESIGNS, so it
    # carries five points, at each design's median turnover across the eleven authoring lines, with
    # its name beside it. The 55 individual cells stay in the document and are drawn flat, where a
    # reader can resolve them.
    arm_pts = []
    for arm in ARMS:
        t_med = float(np.median([turn[f"{ln}|{arm}"] for ln in LINES]))
        arm_pts.append((arm, t_med, 0.0252 * HEADLINE_BPS * t_med))
    # ⚠ NOT LABELLED IN THE SCENE. Five names anchored to five points that project close together is
    # five collisions, which is what the previous revision shipped. The names live in the key, where
    # the layout is one-dimensional and a collision is impossible.
    for arm, t_med, cost in arm_pts:
        st = arm_style(arm)
        ax.plot([HEADLINE_BPS, HEADLINE_BPS], [np.log10(t_med)] * 2, [0.0, cost],
                color=st["color"], lw=1.1, alpha=0.6, zorder=39)
        ax.scatter([HEADLINE_BPS], [np.log10(t_med)], [cost], s=66, color=st["color"],
                   edgecolors="0.15", linewidths=0.9, depthshade=False, zorder=40)

    ax.set_xlim(0.0, MAX_BPS)
    ax.set_ylim(np.log10(tau_lo), np.log10(tau_hi))
    ax.set_zlim(0.0, z_cap)
    ax.set_xticks([0, 10, 25, 50])
    ax.set_xticklabels(["0", "10", "25", "50"], fontsize=9.0)
    yt = [0.5, 1, 3, 10, 30, 90]
    ax.set_yticks([np.log10(v) for v in yt])
    ax.set_yticklabels([f"{v:g}" for v in yt], fontsize=9.0)
    ax.set_zticks([0, 5, 10, 15, 20, 25])

    ax.set_xlabel("Price of trading (bps each way)", labelpad=10, fontsize=9.8)
    ax.set_ylabel("Turnover: share of the book\ntraded per session (%), log", labelpad=18,
                  fontsize=9.8)
    ax.set_zlabel("Cost of trading\n(% of capital a year)", labelpad=10, fontsize=9.8)
    ax.view_init(elev=22, azim=-119)
    ax.set_box_aspect((1.30, 1.20, 0.86))
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.set_facecolor("white")
        pane.set_edgecolor("0.90")
    ax.grid(True, color="0.91", lw=0.5)

    # ⭐ THE KEY IS THE PER-DESIGN TABLE, ordered exactly as the designs stand on the hill, so a reader
    # gets the ranking and both numbers without decoding a single marker position.
    handles = [plt.Line2D([], [], marker="o", ls="", ms=7.0, mfc=arm_style(a)["color"], mec="0.15",
                          mew=0.9, label=f"{ARM_LABEL[a]}: {t:.2f}% a session, {c:.2f}% a year")
               for a, t, c in sorted(arm_pts, key=lambda r: r[1])]
    handles.append(plt.Line2D([], [], color="#1A1A1A", lw=2.0,
                              label=f"where the cost equals the median gross return, {gm:.1f}%"))
    # ⚠ THE CUT-OFF IS NAMED, NOT LEFT TO BE NOTICED. The identity keeps climbing past the top of the
    # box, so the surface is flat-topped there. A flat top a reader cannot account for looks like a
    # property of the data, and it is a property of the axis.
    handles.append(plt.Line2D([], [], color="#7F0000", lw=6.0, alpha=0.85,
                              label=f"the surface is cut off at {z_cap:.0f}% a year and keeps climbing"))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.006), ncol=1,
               frameon=False, fontsize=8.8, handlelength=1.6, columnspacing=1.6,
               handletextpad=0.5, labelspacing=0.42)

    tvals = np.array([turn[f"{ln}|{ar}"] for ln in LINES for ar in ARMS])
    fig.text(0.026, 0.995, "The cost of trading is a hillside, and every design stands on it",
             ha="left", va="top", fontsize=11.5)
    fig.text(0.026, 0.958,
             f"The surface is an identity, price x turnover x {SESSIONS_PER_YEAR:.0f} sessions, "
             f"verified against the measured\ngross and net series at a max/min ratio of "
             f"{facts['ratio_max'] / facts['ratio_min']:.5f}. Each marker is one reward design at "
             f"the 10 bps\nthis study charges. Across all {tvals.size} cells, "
             f"{tvals.min():.2f}% a session costs {0.0252 * HEADLINE_BPS * tvals.min():.2f}% of "
             f"capital a year and\n{tvals.max():.0f}% costs "
             f"{0.0252 * HEADLINE_BPS * tvals.max():.0f}%.",
             ha="left", va="top", fontsize=9.2, color="0.25", linespacing=1.5)

    out.mkdir(parents=True, exist_ok=True)
    png = out / "F5_cost_manifold.png"
    fig.savefig(png, dpi=600, bbox_inches=None, facecolor="white")
    fig.savefig(png.with_suffix(".pdf"), bbox_inches=None, facecolor="white")
    plt.close(fig)

    print(f"wrote {png} (+ .pdf)")
    print(f"  identity check over {int(facts['n_records'])} archived records: annual drag per unit "
          f"of daily turnover {facts['ratio_min']:.5f} to {facts['ratio_max']:.5f}, "
          f"ratio {facts['ratio_max'] / facts['ratio_min']:.5f}")
    print(f"  gross annual return: median {gm:.2f}%, IQR [{facts['gross_q1']:.2f}, "
          f"{facts['gross_q3']:.2f}]")
    print(f"  turnover of the 55 designs: {tvals.min():.2f}% to {tvals.max():.2f}% a session; "
          f"at 10 bps that is {0.0252 * HEADLINE_BPS * tvals.min():.2f}% to "
          f"{0.0252 * HEADLINE_BPS * tvals.max():.2f}% of capital a year")
    print(f"  the cost equals the median gross return at {gm / (0.0252 * HEADLINE_BPS):.1f}% "
          f"turnover when the price is 10 bps")
    return png


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refresh", action="store_true", help="re-read the archive, ignoring the cache")
    a = ap.parse_args(argv)
    if a.refresh and GROSS_CACHE.exists():
        GROSS_CACHE.unlink()
    build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
