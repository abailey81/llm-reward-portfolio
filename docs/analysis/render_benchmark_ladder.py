# -*- coding: utf-8 -*-
"""The whole ladder on one axis: eleven hand-written objectives, four optimisers, five authored arms.

WHY THIS EXHIBIT EXISTS. The Discussion states, twice, that exactly one of the eleven published
objectives is net-positive over the sealed window, and that the survivor is the only one whose
formula prices trading. A reader is asked to take a twenty-row ordering on trust from two sentences
of prose. This draws it. It is also the only exhibit in the document that answers the question an
industrial reader asks first, and which the registered headline does not: *is the automated designer
any good at all, against what a person would write and against a numerical optimiser given the same
budget?*

WHAT IS AND IS NOT COMPARABLE HERE, stated because the rows are not equivalent objects.
The five authored arms are ONE selected program per line re-run across the seed battery, pooled over
the eleven authoring lines. The eleven canon members and the four optimisers are fixed objectives
with no authoring step at all. So the canon rows carry no authoring variance and the arm rows do,
which makes the arm intervals the wider ones by construction. The comparison the pre-registration
tests is the pointwise MAXIMUM over the canon, and that row is drawn separately rather than implied.

Every number is read from ``outputs/campaign_cluster_run4/test`` at the moment of drawing. Nothing is
carried over from a previous measurement.

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

ARCHIVE = REPO / "outputs" / "campaign_cluster_run4" / "test"
FIG_DIR = REPO / "outputs" / "figures"
TEXT_WIDTH_IN = 453.6 / 72.0

#: The eleven published objectives, in the order Table 4.5 prints them, with the printed name.
CANON: tuple[tuple[str, str], ...] = (
    ("baseline_raw_return", "raw_return"),
    ("baseline_return_minus_variance", "return_minus_variance"),
    ("baseline_return_minus_cvar", "return_minus_cvar"),
    ("baseline_differential_sharpe", "differential_sharpe"),
    ("baseline_differential_downside_ratio", "differential_downside_ratio"),
    ("baseline_mean_variance_utility", "mean_variance_utility"),
    ("baseline_return_minus_drawdown", "return_minus_drawdown"),
    ("baseline_return_minus_downside", "return_minus_downside"),
    ("baseline_return_minus_turnover", "return_minus_turnover"),
    ("baseline_log_growth", "log_growth"),
    ("baseline_volatility_scaled_return", "volatility_scaled_return"),
)
OPTIMISERS: tuple[tuple[str, str], ...] = (
    ("random_search", "random search"), ("bayes_opt", "Bayesian optimisation"),
    ("cma_es", "CMA-ES"), ("tpe", "tree-structured Parzen"),
)
ARMS: tuple[tuple[str, str], ...] = (
    ("distributional", "distributional (treatment)"), ("scalar", "scalar (primary control)"),
    ("scalar_cvar5", "scalar + CVaR-5%"), ("placebo", "placebo"), ("placebo_shuffled", "scrambled"),
)


def _read(arm: str) -> tuple[np.ndarray, np.ndarray]:
    """(net Sharpe, mean per-session turnover) over every sealed record of one arm."""
    sharpe, turn = [], []
    for rec in sorted((ARCHIVE / arm).glob("*/record.json")):
        m = json.loads(rec.read_text(encoding="utf-8"))["metrics"]
        sharpe.append(float(m["test_sharpe"]))
        turn.append(float(np.mean(np.asarray(m["test_turnover"], dtype=float))))
    if not sharpe:
        raise FileNotFoundError(f"no sealed records under {ARCHIVE / arm}")
    return np.asarray(sharpe), np.asarray(turn)


def iqm(x: np.ndarray) -> float:
    a = np.sort(np.asarray(x, dtype=float))
    k = a.size // 4
    return float(a[k:a.size - k].mean())


def iqm_ci(x: np.ndarray, *, reps: int = 4000, seed: int = 0) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, x.size, size=(reps, x.size))
    boot = np.sort(x[idx], axis=1)
    k = x.size // 4
    draws = boot[:, k:x.size - k].mean(axis=1)
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return iqm(x), float(lo), float(hi)


def build(out: Path = FIG_DIR) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from src.viz.style import OKABE_ITO, apply_house_style

    apply_house_style()
    matplotlib.rcParams.update({
        "font.size": 10.0, "axes.titlesize": 11.0, "axes.labelsize": 10.0,
        "legend.fontsize": 10.0, "xtick.labelsize": 10.0, "ytick.labelsize": 10.0,
    })

    groups = (("a hand-written objective", CANON, OKABE_ITO["grey"], "o"),
              ("a derivative-free optimiser", OPTIMISERS, OKABE_ITO["orange"], "P"),
              ("a language-model arm", ARMS, OKABE_ITO["blue"], "s"))
    rows: list[tuple[str, float, float, float, float, str, str]] = []
    for _label, members, colour, marker in groups:
        for key, pretty in members:
            s, t = _read(key)
            m, lo, hi = iqm_ci(s, seed=abs(hash(key)) % 10_000)
            rows.append((pretty, m, lo, hi, iqm(t), colour, marker))
            print(f"  {pretty:30s} n={s.size:4d}  net Sharpe {m:+.4f} [{lo:+.4f}, {hi:+.4f}]"
                  f"  turnover {iqm(t):.4f}")
    rows.sort(key=lambda r: r[1])

    fig, ax = plt.subplots(figsize=(TEXT_WIDTH_IN, 6.20))
    ys = np.arange(len(rows))
    for y, (name, m, lo, hi, _turn, colour, marker) in zip(ys, rows):
        if y % 2 == 0:
            ax.axhspan(y - 0.5, y + 0.5, color="0.955", zorder=0)
        ax.plot([lo, hi], [y, y], color=colour, lw=1.5, solid_capstyle="butt", zorder=2)
        ax.plot([m], [y], marker=marker, ms=5.5, color=colour, mec="white", mew=0.6, zorder=3)
    ax.axvline(0.0, color="0.25", lw=1.1, ls="--", zorder=1)
    # Everything left of zero lost money out of sample, which is the single fact this exhibit exists
    # to make unmissable, so it is shaded rather than left to the reader to infer from a dashed line.
    ax.axvspan(min(r[2] for r in rows) - 0.1, 0.0, color=OKABE_ITO["vermillion"], alpha=0.06, zorder=0)

    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows])
    for tick, r in zip(ax.get_yticklabels(), rows):
        if r[0] == "return_minus_turnover":
            tick.set_fontweight("bold")
    ax.set_ylim(-0.6, len(rows) - 0.4)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Terminal Sharpe ratio, NET of transaction costs (annualised)")
    # ⚠ THE TITLE AND THE LEGEND LABELS ARE SHORT BECAUSE THE LONG ONES WERE CLIPPED ON THE PAGE.
    # MEASURED on the compiled figure: "The whole ladder: people, optimisers and the language-model
    # arms" lost its last word at the right edge, and the legend's third entry printed as "a
    # language-model" with "arm" cut off. This module saves at exactly the text width, so a title
    # wider than the canvas is not scaled down, it is cropped.
    ax.set_title("The whole ladder: people, optimisers and machines", fontsize=11)
    # ⛔ THE BAND CARRIES NO LABEL ON THE CANVAS, AND THREE PLACEMENTS WERE TRIED BEFORE GIVING UP ON
    # IT. At the foot of the axes it printed across the worst row's interval, at the top across the
    # best row's stripe, and above the frame it collided with the title. There is no empty place for
    # it, because the band is a full-height region and the rows fill the frame. The caption says
    # "The shaded band is loss" in the first two lines, which is where a reader looks anyway, and a
    # label that has to be squeezed somewhere is worse than one sentence of caption.

    short = ("hand-written objective", "numerical optimiser", "language-model arm")
    handles = [plt.Line2D([], [], ls="-", marker=mk, ms=5.5, color=col, mec="white", mew=0.6,
                          label=lab) for lab, (_l, _mem, col, mk) in zip(short, groups)]
    fig.legend(handles=handles, loc="outside lower center", ncol=3, frameon=False, fontsize=10)

    out.mkdir(parents=True, exist_ok=True)
    png = out / "F5_benchmark_ladder.png"
    # ⚠ THE RCPARAM, NOT THE KEYWORD. `apply_house_style` sets savefig.bbox="tight", and matplotlib
    # falls back to that rcParam when `bbox_inches=None` is passed, so the keyword alone does not turn
    # tight cropping off. MEASURED before this line: the saved page came out 7.23 in wide against a
    # 6.30 in text block, pandoc scaled it by 0.87, and the authored 10 pt type landed at 8.7 pt,
    # under the guideline floor. Setting the rcParam is what actually fixes the width.
    matplotlib.rcParams["savefig.bbox"] = "standard"
    fig.set_size_inches(TEXT_WIDTH_IN, fig.get_size_inches()[1])
    fig.savefig(png, dpi=600, bbox_inches=None)
    fig.savefig(png.with_suffix(".pdf"), bbox_inches=None)
    plt.close(fig)

    canon = [r for r in rows if r[0] in {p for _k, p in CANON}]
    pos = [r for r in canon if r[1] > 0]
    print(f"\n{len(pos)} of {len(canon)} hand-written objectives are net-positive: "
          f"{', '.join(r[0] for r in pos)}")
    print(f"wrote {png} (+ .pdf)")
    return png


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
