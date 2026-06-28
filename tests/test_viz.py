"""Behaviour tests for the report-only figure engine (src/viz + scripts/make_figures).

Headless (Agg): every figure function must return a non-empty matplotlib Figure on synthetic data, the
style helpers must be deterministic + cover all 7 arms, and the demo script must render all five figures
(PNG + PDF) to disk. No display, no network; fast (no torch).
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pytest  # noqa: E402

from src.viz import figures as F  # noqa: E402
from src.viz import style as S  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import make_figures as MF  # noqa: E402


# ---- style helpers ---------------------------------------------------------------------------------- #
def test_arm_style_covers_all_arms_with_distinct_colors() -> None:
    colors = [S.arm_style(a)["color"] for a in S.ARM_ORDER]
    assert len(S.ARM_ORDER) == 7
    assert len(set(colors)) == 7  # every arm a distinct colour
    assert S.CONTROL_ARMS <= set(S.ARM_ORDER)
    for ctrl in S.CONTROL_ARMS:
        assert S.arm_style(ctrl)["hatch"]  # controls carry a non-colour (hatch) channel
    # unknown arm -> neutral default, never raises
    assert S.arm_style("mystery")["color"] == S.OKABE_ITO["black"]


def test_iqm_and_bootstrap_ci_deterministic_and_ordered() -> None:
    x = np.linspace(0, 1, 40)
    assert abs(S.iqm(x) - 0.5) < 1e-9  # symmetric -> IQM = mean = 0.5
    a = S.iqm_bootstrap_ci(x, seed=3)
    b = S.iqm_bootstrap_ci(x, seed=3)
    assert a == b  # deterministic under a fixed seed
    point, lo, hi = a
    assert lo <= point <= hi
    # singleton -> degenerate CI, no crash
    assert S.iqm_bootstrap_ci(np.array([0.7])) == (0.7, 0.7, 0.7)


def test_equivalence_band_draws_span_and_zero_line() -> None:
    fig, ax = plt.subplots()
    S.equivalence_band(ax, 0.05, orient="v")
    assert len(ax.patches) >= 1  # the shaded corridor
    assert any(line.get_linestyle() == "--" for line in ax.get_lines())  # the zero line
    plt.close(fig)


# ---- figure functions ------------------------------------------------------------------------------- #
@pytest.fixture
def demo() -> dict:
    return MF.synthesize_null(seed=1, n_seeds=20)


def test_equivalence_forest_returns_two_panel_figure(demo: dict) -> None:
    fig = F.equivalence_forest(demo["contrasts"])
    assert len(fig.axes) == 2  # Sharpe + CVaR legs
    plt.close(fig)


def test_rliable_intervals_one_axis_per_leg(demo: dict) -> None:
    fig = F.rliable_intervals(demo["scores_by_leg"])
    assert len(fig.axes) == 2
    plt.close(fig)


def test_risk_return_clouds_has_all_arms_in_legend(demo: dict) -> None:
    fig = F.risk_return_clouds(demo["sharpe"], demo["cvar"])
    ax = fig.axes[0]
    labels = [t.get_text() for t in ax.get_legend().get_texts()]
    assert set(labels) == set(S.ARM_ORDER)
    plt.close(fig)


def test_evidence_for_null_with_and_without_mcs(demo: dict) -> None:
    fig = F.evidence_for_null(demo["bf01_by_leg"], demo["mcs"])
    assert len(fig.axes) >= 2  # BF gauge + MCS strip (+ any colorbar)
    plt.close(fig)
    fig2 = F.evidence_for_null(demo["bf01_by_leg"], None)  # no MCS -> single panel, no crash
    assert len(fig2.axes) >= 1
    plt.close(fig2)


def test_reward_code_similarity_renders(demo: dict) -> None:
    fig = F.reward_code_similarity(demo["ast_distance"], demo["cand_arms"])
    assert len(fig.axes) >= 3  # dendrogram + sidebar + heatmap (+ colorbar)
    plt.close(fig)


def test_reward_code_similarity_handles_tiny_matrix() -> None:
    d = np.array([[0.0, 0.4], [0.4, 0.0]])
    fig = F.reward_code_similarity(d, ["distributional", "scalar"])
    assert fig is not None
    plt.close(fig)


# ---- the demo script end to end --------------------------------------------------------------------- #
def test_make_figures_demo_writes_png_and_pdf(tmp_path: Path) -> None:
    data = MF.synthesize_null(seed=2, n_seeds=15)
    saved = MF.render_all(data, tmp_path)
    assert len(saved) == 5
    for p in saved:
        assert p.exists() and p.stat().st_size > 0
        assert p.with_suffix(".pdf").exists()  # vector sibling


def test_synthesize_null_is_deterministic() -> None:
    a = MF.synthesize_null(seed=5, n_seeds=12)
    b = MF.synthesize_null(seed=5, n_seeds=12)
    assert np.allclose(a["sharpe"]["distributional"], b["sharpe"]["distributional"])
    assert np.allclose(a["ast_distance"], b["ast_distance"])
