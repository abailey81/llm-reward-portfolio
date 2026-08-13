# -*- coding: utf-8 -*-
"""Plot the authored reward programs AS FUNCTIONS, by executing them.

WHY THIS EXHIBIT EXISTS. Dr Okhrati asked, in the 2026-08-07 review, whether the reward functions
could be graphed. The request is exact and this module answers it literally: a reward is a function,
a hundred lines of generated Python is not readable, and a scalar summary of it is not informative,
so the program is EXECUTED and its response surface drawn. It is also Stefan's M1, which says the
authored program is an object of study rather than an intermediate, and his M4, which asks that every
result be traced back to the code that produced it. Until now the document characterised what the
models wrote only through distances and counts, never through a picture of the function itself.

WHAT IS MEASURED. Each arm's frozen winning program is loaded from the sealed archive and probed on
two one-dimensional sweeps, holding everything else at the warmed state:

  * the day's portfolio return, swept from -4% to +4% with weights held still, which shows how the
    program treats a loss against a symmetric gain;
  * the fraction of the book traded, swept from 0 to 1 at a zero return, which shows what the
    program charges for turnover.

Both sweeps need a WARMED state, because several authored programs are stateful (they carry rolling
means, drawdown peaks, exponentially-weighted moments). Probing them cold measures the initialiser
rather than the reward, so each is driven for 250 steps of plausible daily returns first, and the
curve is the median over five warm-up seeds so one unlucky warm-up cannot set the shape.

⚠ THE VERTICAL SCALE IS DELIBERATELY NORMALISED AND SAYING SO MATTERS. Authored reward magnitude
spans a factor of 9.8 million across the archive, so plotting the raw values would render ten of the
eleven curves as flat lines against one spike. Each curve is divided by its own maximum absolute
value over the sweep, which is exactly the quantity the SAC value normaliser removes anyway. What
survives normalisation is the SHAPE, which is the object of interest, and the caption says so rather
than letting a reader assume the levels are comparable.

Report-only. Gates nothing. Writes two files and prints the numbers it drew.
"""
from __future__ import annotations

import argparse
import io
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

ARCHIVE = REPO / "outputs" / "campaign_cluster_run4" / "test"
FIG_DIR = REPO / "outputs" / "figures"

#: The five language-model arms, treatment first.
ARMS: tuple[str, ...] = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")
N_ASSET = 30
WARM_STEPS = 250
WARM_SEEDS = (0, 1, 2, 3, 4)

#: The dissertation's text width in points, from geometry margin=2.5cm on A4.
TEXT_WIDTH_PT = 453.6
FIG_WIDTH_IN = TEXT_WIDTH_PT / 72.0


def _pretty(arm: str) -> str:
    return {"distributional": "distributional (treatment)", "scalar": "scalar (primary control)",
            "scalar_cvar5": "scalar + CVaR-5%", "placebo": "placebo",
            "placebo_shuffled": "scrambled"}.get(arm, arm)


def load_reward(arm: str) -> Any:
    """Execute the arm's archived winning program and return its ``reward`` callable.

    The source is read from the sealed archive rather than regenerated, which is the same
    replay-not-regenerate contract the rest of the analysis uses. It has already passed the static
    allowlist gate that admitted it to the campaign, so executing it here re-runs code this study
    has already run thousands of times inside the training loop.
    """
    rec = next((ARCHIVE / arm).glob("*/record.json"), None)
    if rec is None:
        raise FileNotFoundError(f"no archived record for arm {arm!r} under {ARCHIVE}")
    src = json.loads(rec.read_text(encoding="utf-8")).get("reward_source") or ""
    if not src.strip():
        raise ValueError(f"arm {arm!r}: the archived record carries no reward source")
    ns: dict[str, Any] = {"np": np, "__builtins__": __builtins__}
    exec(src, ns)  # noqa: S102 - our own archived, gate-passed program, replayed
    fn = ns.get("reward")
    if fn is None:
        raise ValueError(f"arm {arm!r}: the archived source defines no reward()")
    return fn


def _warm(fn: Any, seed: int) -> tuple[Any, np.ndarray]:
    """Drive a stateful program for WARM_STEPS days so its rolling statistics are populated."""
    rng = np.random.default_rng(seed)
    w = np.full(N_ASSET + 1, 1.0 / (N_ASSET + 1))
    state = None
    for r in rng.normal(0.0004, 0.011, WARM_STEPS):
        _, _, state = fn(w, None, w, float(r), {"reward_state": state})
    return state, w


def _sweeps(arm: str) -> dict[str, np.ndarray]:
    """Return the two response curves for one arm, median over the warm-up seeds."""
    fn = load_reward(arm)
    returns = np.linspace(-0.04, 0.04, 41)
    traded = np.linspace(0.0, 1.0, 21)
    by_return, by_turnover = [], []
    for seed in WARM_SEEDS:
        state, w = _warm(fn, seed)

        def fresh() -> dict[str, Any]:
            return {"reward_state": dict(state) if isinstance(state, dict) else state}

        by_return.append([fn(w, None, w, float(x), fresh())[0] for x in returns])
        row = []
        for frac in traded:
            w2 = w.copy()
            k = max(1, int(N_ASSET * frac / 2))
            w2[:k] += w[0] * frac * 2
            w2[k:2 * k] -= w[0] * frac * 2
            w2 = np.clip(w2, 0.0, None)
            w2 /= w2.sum()
            row.append(fn(w2, None, w, 0.0, fresh())[0])
        by_turnover.append(row)
    return {"returns": returns, "r_curve": np.nanmedian(by_return, axis=0),
            "traded": traded, "t_curve": np.nanmedian(by_turnover, axis=0)}


def _unit(y: np.ndarray) -> np.ndarray:
    """Scale a curve to its own maximum absolute value, so shapes are comparable across arms."""
    m = float(np.nanmax(np.abs(y)))
    return y / m if m > 0 else y


def build(out: Path = FIG_DIR) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from docs.analysis.figure_typeface import use_document_typeface
    from src.viz.style import apply_house_style, arm_style

    apply_house_style()
    use_document_typeface()   # the body typeface, so the exhibit matches the page it sits on
    # The house style sets every default type size below the IFTE0008 10pt floor and lives in a
    # drift-fenced module, so the override lands here, exactly as it does in render_results_figures.
    matplotlib.rcParams.update({
        "font.size": 10.0, "axes.labelsize": 10.0, "axes.titlesize": 11.0,
        "legend.fontsize": 10.0, "xtick.labelsize": 10.0, "ytick.labelsize": 10.0,
        "figure.constrained_layout.use": True, "savefig.bbox": None,
    })

    data = {arm: _sweeps(arm) for arm in ARMS}

    # ⚠ 3.5 in WAS TOO SHORT AND THE LABELS COLLIDED. At that height constrained layout gave the two
    # x-labels less width than they need, so "the day's portfolio return (per cent)" ran into
    # "fraction of the book traded", and the y-label was clipped against the suptitle. Measured on
    # the render, not inferred. The height went to 4.1 in and both axis labels were shortened, which
    # is the better fix in any case: an axis label is a name, and the sweep it describes belongs in
    # the caption.
    fig, axes = plt.subplots(1, 2, figsize=(FIG_WIDTH_IN, 4.1))
    # ⛔ THE TREATMENT AND ITS PRIMARY CONTROL USED TO BE DRAWN THICK AND SOLID WHILE THE OTHER THREE
    # WERE THIN AND DASHED, AND THAT WAS A DEFECT RATHER THAN A CONVENTION. It told a reader, before
    # they had read a number, that two of the five curves mattered and three were background. The
    # study says otherwise on its own measurements: the treatment is the best design on NONE of the
    # eleven authoring lines, while `placebo` takes five and `scalar_cvar5` four. Demoting three arms
    # to dashed hairlines suppressed exactly the comparisons a reader most needs to make here, and
    # the loss-aversion numbers this module prints are among the most interesting in the study for
    # precisely those arms. All five are now drawn at one weight and told apart by colour, which the
    # house palette already makes distinct, so the reader ranks them rather than being told.
    for arm in ARMS:
        st = arm_style(arm)
        kw = dict(color=st["color"], lw=1.9, ls="-", zorder=3)
        axes[0].plot(data[arm]["returns"] * 100.0, _unit(data[arm]["r_curve"]), **kw)
        axes[1].plot(data[arm]["traded"] * 100.0, _unit(data[arm]["t_curve"]), **kw)

    axes[0].axvline(0.0, color="0.7", lw=0.8, zorder=1)
    axes[0].axhline(0.0, color="0.7", lw=0.8, zorder=1)
    axes[0].set_xlabel("the day's return (%)")
    axes[0].set_ylabel("reward, scaled to its own peak")
    axes[0].set_title("What it pays for a return", fontsize=11)

    axes[1].axhline(0.0, color="0.7", lw=0.8, zorder=1)
    axes[1].set_xlabel("share of the book traded (%)")
    # ⚠ THE RIGHT PANEL NAMES ITS OWN VERTICAL AXIS, AND UNTIL NOW IT DID NOT. The two panels are
    # separate axes with separate autoscaling, not a shared pair, so this one drew its own ruler from
    # -1.2 to +0.2 with nothing saying what those numbers were. The reader could reasonably have
    # taken them for reward units, or for a fraction, or for the same scale as the left panel, and
    # only the left panel said. Each is normalised to ITS OWN peak, so the two rulers are genuinely
    # different objects and naming both is the only honest option.
    axes[1].set_ylabel("reward, scaled to its own peak")
    axes[1].set_title("What it charges for trading", fontsize=11)
    for ax in axes:
        ax.grid(alpha=0.25)

    handles = [plt.Line2D([], [], color=arm_style(a)["color"],
                          lw=2.2 if a in ("distributional", "scalar") else 1.3,
                          ls="-" if a in ("distributional", "scalar") else (0, (4, 2)),
                          label=_pretty(a)) for a in ARMS]
    fig.legend(handles=handles, loc="outside lower center", ncol=3, frameon=False, fontsize=10)
    fig.suptitle("The reward programs the models wrote, executed and plotted as functions",
                 fontsize=11.5)

    out.mkdir(parents=True, exist_ok=True)
    png = out / "F5_reward_response.png"
    fig.savefig(png, dpi=600, bbox_inches=None)
    fig.savefig(png.with_suffix(".pdf"), bbox_inches=None)
    plt.close(fig)

    print(f"{'arm':<20}{'loss aversion':>15}{'turnover charge':>18}")
    for arm in ARMS:
        d = data[arm]
        lo, hi = float(d["r_curve"][0]), float(d["r_curve"][-1])
        ratio = abs(lo) / abs(hi) if hi else float("nan")
        charge = float(-(d["t_curve"][-1] - d["t_curve"][0]))
        scale = float(np.nanmax(np.abs(d["t_curve"]))) or 1.0
        print(f"{arm:<20}{ratio:>15.3f}{charge / scale:>18.3f}")
    print(f"wrote {png} (+ .pdf) at {TEXT_WIDTH_PT} pt wide")
    return [png, png.with_suffix(".pdf")]


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
