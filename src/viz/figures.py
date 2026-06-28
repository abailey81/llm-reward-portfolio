"""The headline figure functions (report-only). Each returns a ``matplotlib.figure.Figure``; deterministic.

Designed for a corroborated NULL — every figure visualises equivalence/overlap HONESTLY:

* :func:`equivalence_forest`     — TOST intervals vs the ±SESOI band, both co-primary legs (F5/F6).
* :func:`rliable_intervals`      — per-arm IQM + stratified-bootstrap CIs, the canonical RL-eval figure.
* :func:`risk_return_clouds`     — the collapsed (CVaR, Sharpe) frontier: the 7 arms pile into one blob.
* :func:`evidence_for_null`      — Bayes-factor gauge + Model-Confidence-Set strip (evidence FOR H0).
* :func:`reward_code_similarity` — AST-distance clustered heatmap: the placebo writes the same code.

The functions take ALREADY-COMPUTED arrays/dicts (per-seed scores, TOST bounds, BF01, MCS result, an
AST-distance matrix) so they are decoupled from the inference layer and trivially testable. Captions and
the SESOI value are the caller's responsibility; defaults match the pre-registration (SESOI = 0.05 DSR).
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np

from src.viz.style import (
    OKABE_ITO,
    arm_style,
    equivalence_band,
    iqm_bootstrap_ci,
)

__all__ = [
    "equivalence_forest",
    "rliable_intervals",
    "risk_return_clouds",
    "evidence_for_null",
    "reward_code_similarity",
]

_LEG_LABEL = {"sharpe": "H2-RA: Sharpe", "cvar": "H2-Tail: CVaR-5%"}


def _is_equivalent(tost_lo: float, tost_hi: float, sesoi: float) -> bool:
    return bool(tost_lo >= -sesoi and tost_hi <= sesoi)


def equivalence_forest(
    contrasts: Sequence[Mapping[str, Any]],
    *,
    sesoi: float = 0.05,
    legs: Sequence[str] = ("sharpe", "cvar"),
    title: str = "Co-primary equivalence: contrasts vs the ±SESOI band",
) -> Any:
    """Forest plot of contrast effect sizes with 90% TOST intervals against the equivalence corridor.

    ``contrasts``: an iterable of mappings with keys ``label`` (e.g. "dist − scalar"), ``leg``
    (``"sharpe"``/``"cvar"``), ``estimate``, ``tost_lo``, ``tost_hi``, ``ci_lo``, ``ci_hi``. A row is drawn
    FILLED when its 90% TOST interval lies inside [-sesoi, +sesoi] (EQUIVALENT) and OPEN otherwise
    (INCONCLUSIVE) — the figure never reads a null off a p-value.
    """
    import matplotlib.pyplot as plt

    legs = [leg for leg in legs if any(c["leg"] == leg for c in contrasts)] or list(legs)
    fig, axes = plt.subplots(len(legs), 1, figsize=(6.2, 1.2 + 1.6 * len(legs)), sharex=True, squeeze=False)
    for ax, leg in zip(axes[:, 0], legs):
        rows = [c for c in contrasts if c["leg"] == leg]
        equivalence_band(ax, sesoi, orient="v")
        for y, c in enumerate(rows):
            equiv = _is_equivalent(float(c["tost_lo"]), float(c["tost_hi"]), sesoi)
            col = OKABE_ITO["blue"] if equiv else OKABE_ITO["vermillion"]
            # 95% CI = thin whisker; 90% TOST interval = thick bar; estimate = marker.
            ax.plot([c["ci_lo"], c["ci_hi"]], [y, y], color=col, lw=1.0, zorder=3)
            ax.plot([c["tost_lo"], c["tost_hi"]], [y, y], color=col, lw=3.2, solid_capstyle="round", zorder=4)
            ax.plot([c["estimate"]], [y], marker="o", ms=6, color=col,
                    markerfacecolor=col if equiv else "white", markeredgecolor=col, zorder=5)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels([c["label"] for c in rows])
        ax.set_ylim(-0.6, len(rows) - 0.4)
        ax.invert_yaxis()
        ax.set_title(_LEG_LABEL.get(leg, leg), loc="left", fontsize=9)
    axes[-1, 0].set_xlabel("contrast effect size (deflated-Sharpe units)")
    # one shared legend entry for the band + a filled/open key
    handles = [
        plt.Line2D([], [], marker="o", color=OKABE_ITO["blue"], ls="-", lw=3.2, label="equivalent (TOST ⊂ band)"),
        plt.Line2D([], [], marker="o", color=OKABE_ITO["vermillion"], markerfacecolor="white", ls="-", lw=3.2, label="inconclusive"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.04))
    fig.suptitle(title, fontsize=10)
    return fig


def rliable_intervals(
    scores_by_leg: Mapping[str, Mapping[str, np.ndarray]],
    *,
    seed: int = 0,
    title: str = "Aggregate performance (IQM, 95% stratified-bootstrap CI)",
) -> Any:
    """Per-arm IQM point + bootstrap CI for each leg (Agarwal 2021). Overlapping CIs ⇒ consistent with H0.

    ``scores_by_leg``: ``{leg_label: {arm: per-seed score array}}``. One column per leg; one row per arm
    (controls drawn hatched). The visual payload of a null is overlapping intervals across all arms.
    """
    import matplotlib.pyplot as plt

    legs = list(scores_by_leg)
    arms = list(next(iter(scores_by_leg.values())))
    fig, axes = plt.subplots(1, len(legs), figsize=(3.2 * len(legs), 0.5 + 0.42 * len(arms)), squeeze=False)
    for ax, leg in zip(axes[0], legs):
        for y, arm in enumerate(arms):
            st = arm_style(arm)
            point, lo, hi = iqm_bootstrap_ci(np.asarray(scores_by_leg[leg][arm]), seed=seed + y)
            ax.plot([lo, hi], [y, y], color=st["color"], lw=2.4, solid_capstyle="round", zorder=3)
            ax.plot([point], [y], marker=st["marker"], ms=7, color=st["color"],
                    markerfacecolor=st["color"], markeredgecolor="black", markeredgewidth=0.4, zorder=4)
            if st["hatch"]:
                ax.plot([point], [y], marker="o", ms=13, markerfacecolor="none",
                        markeredgecolor=st["color"], markeredgewidth=0.8, alpha=0.6, zorder=2)
        ax.set_yticks(range(len(arms)))
        ax.set_yticklabels(arms if ax is axes[0, 0] else [""] * len(arms))
        ax.set_ylim(-0.6, len(arms) - 0.4)
        ax.invert_yaxis()
        ax.set_title(leg, fontsize=9, loc="left")
        ax.set_xlabel("IQM")
    fig.suptitle(title, fontsize=10)
    return fig


def risk_return_clouds(
    sharpe_by_arm: Mapping[str, np.ndarray],
    cvar_by_arm: Mapping[str, np.ndarray],
    *,
    title: str = "Risk–return: per-seed clouds collapse onto one neighbourhood",
) -> Any:
    """Scatter each arm's per-seed (CVaR-5% x, Sharpe y) points as a translucent cloud + an IQM centroid.

    The whole-story null figure: if the channel mattered the clouds would separate; here they pile up.
    """
    import matplotlib.pyplot as plt

    from src.viz.style import iqm

    fig, ax = plt.subplots(figsize=(5.6, 4.4))
    for arm in sharpe_by_arm:
        st = arm_style(arm)
        x = np.asarray(cvar_by_arm[arm], dtype=float).ravel()
        y = np.asarray(sharpe_by_arm[arm], dtype=float).ravel()
        ax.scatter(x, y, s=14, color=st["color"], alpha=0.22, marker=st["marker"],
                   edgecolors="none", zorder=2)
        ax.scatter([iqm(x)], [iqm(y)], s=120, color=st["color"], marker=st["marker"],
                   edgecolors="black", linewidths=0.7, zorder=4, label=arm)
    ax.set_xlabel("CVaR-5% (less negative = safer →)")
    ax.set_ylabel("Sharpe ratio")
    ax.set_title(title, fontsize=10, loc="left")
    ax.legend(loc="best", ncol=2, fontsize=7)
    return fig


def evidence_for_null(
    bf01_by_leg: Mapping[str, float],
    mcs: Mapping[str, Any] | None = None,
    *,
    title: str = "Evidence FOR the null: Bayes factor + Model Confidence Set",
) -> Any:
    """Bayes-factor gauge per leg (log strip with Jeffreys bands) + the MCS membership strip.

    ``bf01_by_leg``: ``{leg: BF01}`` (BF01 > 1 favours H0). ``mcs``: the dict from
    :func:`src.inference.model_confidence_set.model_confidence_set` (``included``/``excluded``/``pvalues``);
    a populated set = "the data cannot single out a best channel". Converts absence-of-evidence into
    bounded evidence-of-absence.
    """
    import matplotlib.pyplot as plt

    has_mcs = bool(mcs and mcs.get("pvalues"))
    fig, axes = plt.subplots(2 if has_mcs else 1, 1, figsize=(6.0, 3.4 if has_mcs else 1.9),
                             squeeze=False, gridspec_kw={"height_ratios": [1, 1.1] if has_mcs else [1]})

    ax = axes[0, 0]
    # Jeffreys evidence bands on a log axis (BF01): 1–3 anecdotal, 3–10 moderate, 10–30 strong, >30 v.strong.
    bands = [(1, 3, "0.92", "anecdotal"), (3, 10, "0.82", "moderate"), (10, 30, "0.70", "strong"),
             (30, 100, "0.58", "very strong")]
    for lo, hi, shade, lab in bands:
        ax.axvspan(lo, hi, color=shade, zorder=0)
        ax.text(np.sqrt(lo * hi), 1.0, lab, ha="center", va="center", fontsize=6.5, color="0.3")
    ax.axvline(1.0, color="0.4", lw=0.8, ls="--", zorder=1)  # BF01=1: no evidence either way
    for i, (leg, bf) in enumerate(bf01_by_leg.items()):
        ax.plot([max(float(bf), 0.3)], [i], marker="D", ms=9, color=OKABE_ITO["blue"],
                markeredgecolor="black", markeredgewidth=0.5, zorder=3)
        ax.text(max(float(bf), 0.3), i + 0.18, f"BF₀₁={bf:.2g}", ha="center", fontsize=7)
    ax.set_xscale("log")
    ax.set_xlim(0.3, 100)
    ax.set_yticks(range(len(bf01_by_leg)))
    ax.set_yticklabels([_LEG_LABEL.get(k, k) for k in bf01_by_leg])
    ax.set_ylim(-0.6, len(bf01_by_leg) - 0.2)
    ax.set_xlabel("Bayes factor BF₀₁  (→ favours H0)")
    ax.set_title("evidence for equivalence (JZS BF₀₁)", fontsize=9, loc="left")

    if has_mcs:
        axm = axes[1, 0]
        assert mcs is not None
        pv = mcs["pvalues"]
        arms = list(pv)
        included = set(mcs.get("included", []))
        for x, arm in enumerate(arms):
            st = arm_style(arm)
            inset = arm in included
            axm.scatter([x], [0], s=240, marker=st["marker"],
                        color=st["color"] if inset else "white",
                        edgecolors=st["color"], linewidths=1.4, zorder=3)
            axm.text(x, 0.32, arm, ha="center", va="bottom", rotation=30, fontsize=7)
            axm.text(x, -0.3, f"p={pv[arm]:.2f}", ha="center", va="top", fontsize=6.5, color="0.3")
        axm.set_xlim(-0.7, len(arms) - 0.3)
        axm.set_ylim(-0.8, 0.9)
        axm.set_yticks([])
        axm.set_xticks([])
        for s in axm.spines.values():
            s.set_visible(False)
        n_in = len(included)
        axm.set_title(f"Model Confidence Set (size {mcs.get('size', '?')}): {n_in}/{len(arms)} arms retained "
                      f"— filled = in set", fontsize=9, loc="left")
    fig.suptitle(title, fontsize=10)
    return fig


def reward_code_similarity(
    distance: np.ndarray,
    arm_labels: Sequence[str],
    *,
    title: str = "Authored reward-code structure clusters across arms, not by arm",
) -> Any:
    """AST-distance clustered heatmap + dendrogram + an arm colour sidebar (the mechanism figure).

    ``distance``: a symmetric (N×N) pairwise AST-distance matrix between authored reward programs (e.g.
    ``1 - structural_similarity``). ``arm_labels``: the arm of each of the N candidates. Clusters that cut
    ACROSS arms are the signature of the null: the feedback channel did not change what the LLM wrote.
    """
    import matplotlib.pyplot as plt
    from scipy.cluster.hierarchy import dendrogram, linkage
    from scipy.spatial.distance import squareform

    d = np.asarray(distance, dtype=float)
    n = d.shape[0]
    d = 0.5 * (d + d.T)
    np.fill_diagonal(d, 0.0)
    order = list(range(n))
    if n >= 2:
        z = linkage(squareform(d, checks=False), method="average")
        order = dendrogram(z, no_plot=True)["leaves"]

    fig = plt.figure(figsize=(6.6, 6.0))
    gs = fig.add_gridspec(2, 2, width_ratios=[1, 5.0], height_ratios=[1.2, 5.0],
                          wspace=0.02, hspace=0.02)
    ax_dend = fig.add_subplot(gs[0, 1])
    ax_bar = fig.add_subplot(gs[1, 0])
    ax_heat = fig.add_subplot(gs[1, 1])

    if n >= 2:
        dendrogram(z, ax=ax_dend, color_threshold=0, above_threshold_color="0.4", no_labels=True)
    ax_dend.set_xticks([])
    ax_dend.set_yticks([])
    for s in ax_dend.spines.values():
        s.set_visible(False)

    dd = d[np.ix_(order, order)]
    im = ax_heat.imshow(dd, cmap="viridis", aspect="auto", origin="upper")
    ax_heat.set_xticks([])
    ax_heat.set_yticks([])
    ax_heat.set_xlabel("authored reward programs (clustered)")
    fig.colorbar(im, ax=ax_heat, fraction=0.046, pad=0.02, label="AST distance (1 − structural similarity)")

    arms_ordered = [arm_labels[i] for i in order]
    colors = np.array([_to_rgb(arm_style(a)["color"]) for a in arms_ordered]).reshape(n, 1, 3)
    ax_bar.imshow(colors, aspect="auto", origin="upper")
    ax_bar.set_xticks([])
    ax_bar.set_yticks([])
    ax_bar.set_ylabel("arm")
    # legend for the arm colour sidebar
    seen: dict[str, Any] = {}
    for a in arm_labels:
        if a not in seen:
            seen[a] = plt.Line2D([], [], marker="s", ls="", color=arm_style(a)["color"], label=a)
    ax_heat.legend(handles=list(seen.values()), loc="upper left", bbox_to_anchor=(1.18, 1.0), fontsize=7)
    fig.suptitle(title, fontsize=10)
    return fig


def _to_rgb(hexcolor: str) -> tuple[float, float, float]:
    import matplotlib.colors as mcolors

    return mcolors.to_rgb(hexcolor)
