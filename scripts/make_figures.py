"""Render the dissertation's headline figure suite (report-only; faultless-presentation lever).

Produces the five data-driven headline figures from :mod:`src.viz.figures` — the co-primary equivalence
forest, the rliable IQM intervals, the collapsed risk–return clouds, the evidence-FOR-the-null panel
(Bayes factor + Model Confidence Set), and the reward-code AST-similarity heatmap — into ``outputs/figures/``
as 600-dpi PNG + vector PDF, in a consistent Okabe-Ito house style.

The confirmatory campaign is unrun, so the headline figures need ``[CAMPAIGN]`` data. This script's
``--demo`` mode (default) synthesises NULL-shaped data (all arms drawn indistinguishable) so the whole
suite is buildable and visually validatable NOW; post-campaign, ``--results-root <dir>`` will load the real
per-seed/inference outputs and re-render the identical figures. Deterministic.

Usage::

    python scripts/make_figures.py                       # demo (synthetic null) -> outputs/figures/
    python scripts/make_figures.py --out outputs/figures
    python scripts/make_figures.py --results-root outputs/campaign   # (post-campaign; not yet wired)
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # headless/remote-safe: render to files, never a GUI

import numpy as np

from src.viz import figures as F
from src.viz.style import ARM_ORDER, apply_house_style, savefig

_LEGS = ("sharpe", "cvar")


def synthesize_null(seed: int = 7, n_seeds: int = 30) -> dict[str, Any]:
    """Synthesise NULL-shaped per-seed scores + inference outputs (all arms indistinguishable).

    Pure illustration so the figure ENGINE is validatable pre-campaign; NO number here is a result.
    """
    rng = np.random.default_rng(seed)
    arms = list(ARM_ORDER)
    # All arms share one Sharpe/CVaR neighbourhood; tiny per-arm offsets << the ±0.05 SESOI -> a true null.
    sharpe = {a: 0.55 + rng.normal(0, 0.18, n_seeds) + rng.uniform(-0.02, 0.02) for a in arms}
    cvar = {a: -0.058 + rng.normal(0, 0.012, n_seeds) + rng.uniform(-0.002, 0.002) for a in arms}
    scores_by_leg = {"Sharpe": sharpe, "CVaR-5%": cvar}

    # Co-primary contrasts: distributional vs each control, both legs; estimates ~0, 90% TOST ⊂ ±0.05.
    contrasts = []
    for leg, ref in (("sharpe", sharpe), ("cvar", cvar)):
        for other in ("scalar", "placebo", "scalar_cvar5"):
            est = float(np.mean(ref["distributional"]) - np.mean(ref[other]))
            est = float(np.clip(est, -0.03, 0.03))
            half = 0.035
            contrasts.append({
                "label": f"dist − {other}", "leg": leg, "estimate": est,
                "tost_lo": est - half, "tost_hi": est + half,
                "ci_lo": est - 0.055, "ci_hi": est + 0.055,
            })

    bf01_by_leg = {"sharpe": 6.4, "cvar": 4.8}  # moderate evidence for H0 (illustrative)

    from src.inference.model_confidence_set import model_confidence_set

    mcs = model_confidence_set(sharpe, size=0.10, reps=500, seed=1)

    # AST-distance matrix: candidates from all arms, with clusters that cut ACROSS arms (the mechanism).
    n_per = 3
    cand_arms = [a for a in arms for _ in range(n_per)]
    n = len(cand_arms)
    # latent structural "template" id NOT aligned to arm -> cross-arm blocks (placebo writes same code).
    template = rng.integers(0, 3, size=n)
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            base = 0.08 if template[i] == template[j] else 0.62
            dist[i, j] = base + rng.uniform(0, 0.06)
    dist = 0.5 * (dist + dist.T)
    np.fill_diagonal(dist, 0.0)

    return {
        "scores_by_leg": scores_by_leg, "sharpe": sharpe, "cvar": cvar,
        "contrasts": contrasts, "bf01_by_leg": bf01_by_leg, "mcs": mcs,
        "ast_distance": dist, "cand_arms": cand_arms,
    }


def render_all(data: dict[str, Any], out: Path) -> list[Path]:
    """Render the five headline figures from a data bundle; return the saved PNG paths."""
    apply_house_style()
    saved: list[Path] = []

    def _save(fig: Any, name: str) -> None:
        p = out / name
        savefig(fig, p)
        saved.append(p)
        import matplotlib.pyplot as plt

        plt.close(fig)

    _save(F.equivalence_forest(data["contrasts"]), "F_equivalence_forest.png")
    _save(F.rliable_intervals(data["scores_by_leg"]), "F_rliable_intervals.png")
    _save(F.risk_return_clouds(data["sharpe"], data["cvar"]), "F_risk_return_clouds.png")
    _save(F.evidence_for_null(data["bf01_by_leg"], data["mcs"]), "F_evidence_for_null.png")
    _save(F.reward_code_similarity(data["ast_distance"], data["cand_arms"]), "F_reward_code_similarity.png")
    return saved


def main() -> None:
    ap = argparse.ArgumentParser(description="Render the headline figure suite (report-only).")
    ap.add_argument("--out", default="outputs/figures", help="output dir (default outputs/figures)")
    ap.add_argument("--results-root", default=None,
                    help="post-campaign results dir to load real data from (not yet wired; uses --demo until then)")
    ap.add_argument("--seed", type=int, default=7, help="synthetic-demo seed")
    args = ap.parse_args()

    out = Path(args.out)
    if args.results_root:
        raise SystemExit(
            "real-data loading is not yet wired (the confirmatory campaign is unrun). Re-run without "
            "--results-root for the synthetic-null demo; the figure functions in src/viz/figures.py are "
            "the post-campaign API (feed per-seed scores + inference outputs)."
        )
    data = synthesize_null(seed=args.seed)
    saved = render_all(data, out)
    print(f"[make_figures] DEMO (synthetic null) — {len(saved)} figures -> {out}/")
    for p in saved:
        print(f"  {p.name}  (+ {p.with_suffix('.pdf').name})")


if __name__ == "__main__":
    main()
