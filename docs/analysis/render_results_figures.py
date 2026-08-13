"""Render the Chapter-5 (Results) figure suite from the SEALED campaign archive.

Every exhibit here is drawn from ``outputs/campaign_cluster_run4`` — the real, frozen test-leg
records. Nothing in this module fabricates, simulates or demo-stamps anything; the synthetic
``scripts/make_figures.py --demo`` renders are a separate, unrelated code path and none of their
output is read here.

The archive layout the loader walks::

    <root>/test/<arm>/<arm>-s<seed>/record.json                 # the CORE line (author: claude-opus-5)
    <root>/test_leg_<model>/<arm>/<arm>-s<seed>/record.json     # the ten replication legs

Eleven author lines x five LLM-authored arms x seeds 0..101 = 5,610 sealed records. ``N_SEEDS = 102``
is the banked contiguous rung: every (line, arm) cell has a complete, gap-free seed prefix 0..101, so
every panel is drawn at the same n and no cell is silently thinner than its neighbours.

Metric conventions, stated once and enforced in every axis label:

* ``test_sharpe``  — annualised (x sqrt(252)) Sharpe of the per-session **NET** return series, i.e.
  after the half-L1-drifted transaction cost. This is the record's own field; the figures never
  recompute it, so figure and table cannot diverge.
* ``test_gross``   — the same trajectory **BEFORE** the cost charge. The gross Sharpe is recomputed
  here with the identical estimator (``src.inference.bootstrap.sharpe_ratio``) so gross and net are
  comparable by construction.
* ``test_turnover``— per-session ``0.5 * ||w - w_held||_1``: the fraction of the book traded, one way.

Run::

    .venv/Scripts/python.exe docs/analysis/render_results_figures.py            # cache (if stale) + render
    .venv/Scripts/python.exe docs/analysis/render_results_figures.py --rebuild  # force a re-read of the archive
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Sequence

import numpy as np

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.inference.bootstrap import sharpe_ratio  # noqa: E402  (repo root must be on sys.path first)

_LOG = logging.getLogger("render_results_figures")

# --------------------------------------------------------------------------- #
# Archive coordinates — all verified against the sealed run, 2026-08-09        #
# --------------------------------------------------------------------------- #
ARCHIVE_ROOT = _REPO / "outputs" / "campaign_cluster_run4"
FIG_DIR = _REPO / "outputs" / "figures"
CACHE_PATH = _REPO / "docs" / "analysis" / ".results_figure_cache.npz"

#: The banked contiguous rung. Every (line, arm) cell carries seeds 0..101 with no gaps.
N_SEEDS = 102

#: The five LLM-authored arms, in the house rendering order (contribution first, controls last).
ARMS: tuple[str, ...] = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")
TREATMENT = "distributional"
CONTROL = "scalar"

#: (subdirectory, display label) for each of the eleven author lines. The core line is the
#: confirmatory author (``config/campaign.yaml: model_snapshot: claude-opus-5``); the ten legs are
#: ``config/legs.yaml`` in registered order.
LINES: tuple[tuple[str, str], ...] = (
    ("test", "opus-5"),
    ("test_leg_deepseek_v4_pro", "deepseek-v4-pro"),
    ("test_leg_glm_5_2", "glm-5.2"),
    ("test_leg_qwen3_6_27b", "qwen3.6-27b"),
    ("test_leg_qwen3_5_9b", "qwen3.5-9b"),
    ("test_leg_haiku_4_5", "haiku-4.5"),
    ("test_leg_gpt_5_6_luna", "gpt-5.6-luna"),
    ("test_leg_sonnet_5", "sonnet-5"),
    ("test_leg_kimi_k3", "kimi-k3"),
    ("test_leg_nemotron_3_super", "nemotron-3-super"),
    ("test_leg_gemini_2_5_flash", "gemini-2.5-flash"),
)
LINE_LABELS: tuple[str, ...] = tuple(label for _, label in LINES)
CORE_LINE = "opus-5"

#: Test window, panel ``univ5`` rows [3835, 5406) — ``config/inference.yaml: splits.univ5.test``.
TEST_SLICE = (3835, 5406)
TEST_N_SESSIONS = TEST_SLICE[1] - TEST_SLICE[0]
TEST_SPAN_LABEL = "2020-03-30 to 2026-06-30"

#: Exogenous stop: the pre-committed calendar cut-off for the seed campaign (never data-dependent),
#: ``config/preregistration.yaml: exogenous_stop``. The campaign is still running on the render date,
#: so ``N_SEEDS`` is the rung BANKED so far, not the rung the campaign will finish on. Every caption
#: must say so: a figure that implies the stop has already happened misstates the protocol.
STOPPING_DATE = "2026-08-27"
RUNG_MEASURED_DATE = "2026-08-09"

#: Trading sessions per year used for annualisation (matches ``sharpe_ratio``'s default).
PERIODS_PER_YEAR = 252

#: The expanding-window Sharpe trajectory is only meaningful once the window carries enough
#: sessions for a variance estimate; 126 sessions ~ six months. Stated in the caption.
TRAJECTORY_MIN_SESSIONS = 126
#: Sub-sample the trajectory grid so the cache stays small and the PDF stays light. 5 divides
#: ``TEST_N_SESSIONS - TRAJECTORY_MIN_SESSIONS`` exactly, so the LAST grid point is the full window
#: and the trajectory's endpoint reproduces the record's own ``test_sharpe`` rather than near-missing it.
TRAJECTORY_STRIDE = 5


# --------------------------------------------------------------------------- #
# Stage 1 — read the archive                                                   #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Cell:
    """One (line, arm) cell: ``N_SEEDS`` sealed test records reduced to plottable arrays."""

    line: str
    arm: str
    sharpe_net: np.ndarray      # (n_seeds,)   annualised, NET of transaction cost
    sharpe_gross: np.ndarray    # (n_seeds,)   annualised, GROSS (pre-cost)
    turnover: np.ndarray        # (n_seeds,)   mean per-session fraction of book traded
    cvar05: np.ndarray          # (n_seeds,)   per-session 5% CVaR of NET returns
    traj: np.ndarray            # (n_seeds, n_grid)  expanding-window annualised NET Sharpe
    #: Cross-seed MEDIAN of the compounded NET wealth path, and of the drawdown from its own running
    #: peak. Reduced at read time rather than stored per seed: 102 seeds x 1,571 sessions x 55 cells
    #: is 8.8 million floats, and the exhibit that uses them draws a median path per cell.
    equity: np.ndarray          # (n_sessions,)  median wealth of 1.0 invested at the window's open
    drawdown: np.ndarray        # (n_sessions,)  median fall from the running peak, as a fraction


def _record_path(line_dir: str, arm: str, seed: int) -> Path:
    return ARCHIVE_ROOT / line_dir / arm / f"{arm}-s{seed}" / "record.json"


def _trajectory_grid() -> np.ndarray:
    """Session counts at which the expanding-window Sharpe is evaluated (last point = full window)."""
    grid = np.arange(TRAJECTORY_MIN_SESSIONS, TEST_N_SESSIONS + 1, TRAJECTORY_STRIDE)
    if grid[-1] != TEST_N_SESSIONS:  # never let the endpoint near-miss the record's own test_sharpe
        grid = np.append(grid, TEST_N_SESSIONS)
    return grid


def _expanding_sharpe(net_returns: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """Annualised Sharpe of ``net_returns[:k]`` for each k in ``grid`` (population sd, as in the record).

    Computed from prefix sums so the whole grid costs one pass; the estimator is identical to
    ``sharpe_ratio`` (mean / population sd * sqrt(252)) so the last grid point reproduces the
    record's own ``test_sharpe`` to floating-point tolerance.
    """
    r = np.asarray(net_returns, dtype=float)
    csum = np.concatenate(([0.0], np.cumsum(r)))
    csum2 = np.concatenate(([0.0], np.cumsum(r * r)))
    k = grid.astype(float)
    mean = csum[grid] / k
    var = csum2[grid] / k - mean * mean
    sd = np.sqrt(np.maximum(var, 0.0))
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(sd > 0.0, mean / sd * np.sqrt(PERIODS_PER_YEAR), 0.0)
    return out


def _load_cell(line_dir: str, line_label: str, arm: str, grid: np.ndarray) -> Cell:
    n_grid = grid.size
    sharpe_net = np.full(N_SEEDS, np.nan)
    sharpe_gross = np.full(N_SEEDS, np.nan)
    turnover = np.full(N_SEEDS, np.nan)
    cvar05 = np.full(N_SEEDS, np.nan)
    traj = np.full((N_SEEDS, n_grid), np.nan)
    equity = np.full((N_SEEDS, TEST_N_SESSIONS), np.nan)
    drawdown = np.full((N_SEEDS, TEST_N_SESSIONS), np.nan)

    for seed in range(N_SEEDS):
        path = _record_path(line_dir, arm, seed)
        if not path.exists():
            raise FileNotFoundError(
                f"the banked rung claims n={N_SEEDS} but {path} is missing — refusing to draw a "
                f"figure at a silently thinner n"
            )
        with path.open("r", encoding="utf-8") as fh:
            rec = json.load(fh)
        m = rec["metrics"]
        net = np.asarray(m["test_returns"], dtype=float)
        if net.size != TEST_N_SESSIONS:
            raise ValueError(f"{path}: expected {TEST_N_SESSIONS} test sessions, got {net.size}")
        sharpe_net[seed] = float(m["test_sharpe"])
        cvar05[seed] = float(m["test_cvar05"])
        sharpe_gross[seed] = sharpe_ratio(np.asarray(m["test_gross"], dtype=float))
        turnover[seed] = float(np.mean(np.asarray(m["test_turnover"], dtype=float)))
        traj[seed] = _expanding_sharpe(net, grid)
        # Compounded, not summed. The record stores simple per-session net returns, so wealth is the
        # cumulative product; summing them would overstate a rising path and understate a falling one.
        w = np.cumprod(1.0 + net)
        equity[seed] = w
        drawdown[seed] = w / np.maximum.accumulate(w) - 1.0

    return Cell(line_label, arm, sharpe_net, sharpe_gross, turnover, cvar05, traj,
                np.median(equity, axis=0), np.median(drawdown, axis=0))


def build_cache(path: Path = CACHE_PATH) -> dict[str, Any]:
    """Read every sealed record once and persist the reduced arrays to ``path`` (npz)."""
    grid = _trajectory_grid()
    store: dict[str, np.ndarray] = {"__grid__": grid}
    for line_dir, line_label in LINES:
        for arm in ARMS:
            cell = _load_cell(line_dir, line_label, arm, grid)
            key = f"{line_label}|{arm}"
            store[f"{key}|sharpe_net"] = cell.sharpe_net
            store[f"{key}|sharpe_gross"] = cell.sharpe_gross
            store[f"{key}|turnover"] = cell.turnover
            store[f"{key}|cvar05"] = cell.cvar05
            store[f"{key}|traj"] = cell.traj
            store[f"{key}|equity"] = cell.equity
            store[f"{key}|drawdown"] = cell.drawdown
            _LOG.info("read %-22s %-18s n=%d  sharpe_net median=%.3f", line_label, arm,
                      N_SEEDS, float(np.median(cell.sharpe_net)))
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **store)
    return store


def load_cache(path: Path = CACHE_PATH, *, rebuild: bool = False) -> dict[str, np.ndarray]:
    """Return the reduced-array store, reading the archive only when the cache is absent/stale."""
    if rebuild or not path.exists():
        return build_cache(path)
    with np.load(path) as z:
        store = {k: z[k] for k in z.files}
    # The equity/drawdown fields were added after the first cache was written, so they are part of
    # the completeness test: an older cache is silently missing them and must be rebuilt, not used.
    expected = {f"{label}|{arm}|{f}" for _, label in LINES for arm in ARMS
                for f in ("sharpe_net", "equity", "drawdown")}
    if not expected.issubset(store.keys()):
        _LOG.warning("cache at %s is incomplete — rebuilding", path)
        return build_cache(path)
    return store


def cells(store: dict[str, np.ndarray]) -> Iterator[tuple[str, str]]:
    """Yield every (line label, arm) pair in rendering order."""
    for _, label in LINES:
        for arm in ARMS:
            yield label, arm


def get(store: dict[str, np.ndarray], line: str, arm: str, field: str) -> np.ndarray:
    return store[f"{line}|{arm}|{field}"]


# --------------------------------------------------------------------------- #
# Statistics helpers (seed-level resampling; deterministic)                     #
# --------------------------------------------------------------------------- #
def paired_contrast(store: dict[str, np.ndarray], line: str, field: str = "sharpe_net") -> np.ndarray:
    """Per-seed treatment-minus-control differences for one line (paired on the seed index)."""
    return get(store, line, TREATMENT, field) - get(store, line, CONTROL, field)


def mean_ci(x: Sequence[float] | np.ndarray, *, reps: int = 10_000, alpha: float = 0.05,
            seed: int = 0) -> tuple[float, float, float]:
    """(mean, lo, hi) with a deterministic percentile bootstrap over the sample."""
    a = np.asarray(x, dtype=float).ravel()
    a = a[np.isfinite(a)]
    if a.size == 0:
        return float("nan"), float("nan"), float("nan")
    if a.size < 2:
        return float(a[0]), float(a[0]), float(a[0])
    rng = np.random.default_rng(seed)
    boot = a[rng.integers(0, a.size, size=(reps, a.size))].mean(axis=1)
    lo, hi = np.quantile(boot, [alpha / 2, 1 - alpha / 2])
    return float(a.mean()), float(lo), float(hi)


def iqr(x: np.ndarray) -> float:
    a = np.asarray(x, dtype=float)
    a = a[np.isfinite(a)]
    q1, q3 = np.quantile(a, [0.25, 0.75])
    return float(q3 - q1)


def iqr_ci(x: np.ndarray, *, reps: int = 10_000, alpha: float = 0.05,
           seed: int = 0) -> tuple[float, float, float]:
    """(IQR, lo, hi) with a deterministic percentile bootstrap — no bare spread statistic either."""
    a = np.asarray(x, dtype=float).ravel()
    a = a[np.isfinite(a)]
    if a.size < 4:
        v = iqr(a) if a.size else float("nan")
        return v, v, v
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, a.size, size=(reps, a.size))
    q = np.quantile(a[idx], [0.25, 0.75], axis=1)
    boot = q[1] - q[0]
    lo, hi = np.quantile(boot, [alpha / 2, 1 - alpha / 2])
    return iqr(a), float(lo), float(hi)


def running_mean_ci(x: np.ndarray, *, reps: int = 2_000, alpha: float = 0.05,
                    seed: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Running mean of ``x[:n]`` for n = 1..len(x), with a bootstrap CI at each prefix.

    ``x`` MUST arrive in registered seed order. Sorting it — by value, by any statistic — turns the
    curve into a selection artifact and the exhibit is then invalid; the caller never sorts.
    """
    a = np.asarray(x, dtype=float).ravel()
    n = a.size
    point = np.cumsum(a) / np.arange(1, n + 1)
    lo = np.full(n, np.nan)
    hi = np.full(n, np.nan)
    rng = np.random.default_rng(seed)
    for k in range(2, n + 1):
        pref = a[:k]
        boot = pref[rng.integers(0, k, size=(reps, k))].mean(axis=1)
        lo[k - 1], hi[k - 1] = np.quantile(boot, [alpha / 2, 1 - alpha / 2])
    return point, lo, hi


# --------------------------------------------------------------------------- #
# Shared figure furniture                                                       #
# --------------------------------------------------------------------------- #
#: Every Sharpe axis in this suite says GROSS or NET out loud. The convention is not optional: the
#: whole mechanism result is a cost story, so an unlabelled Sharpe axis is a defect, not a shorthand.
SHARPE_NET_UNIT = "annualised Sharpe ratio, NET of transaction costs (dimensionless)"
TURNOVER_UNIT = "mean per-session turnover (fraction of book traded, one way)"

_ARCHIVE_STAMP = f"source: outputs/campaign_cluster_run4 (sealed) | n = {N_SEEDS} seeds per arm"


def _caption(*lines: str) -> str:
    """Join note lines for use as a multi-line axis label.

    Notes ride in the xlabel rather than in a free-floating ``fig.text`` on purpose: constrained
    layout reserves space for axis labels, so a note can never end up overhanging an axis or being
    clipped at the figure edge.
    """
    return "\n".join(lines)


def _test_dates() -> Any:
    """Calendar dates of the 1,571 test sessions, read from the gold panel index.

    Falls back to ``None`` (the trajectory then plots against session count) if the panel is absent,
    so the suite still renders on a machine without the licensed data.
    """
    panel = _REPO / "data" / "gold" / "returns_panel_univ5.parquet"
    if not panel.exists():
        _LOG.warning("gold panel not found at %s — trajectory will use session counts", panel)
        return None
    import pandas as pd

    idx = pd.read_parquet(panel, columns=[]).index[TEST_SLICE[0]:TEST_SLICE[1]]
    if len(idx) != TEST_N_SESSIONS:
        raise ValueError(f"panel test slice is {len(idx)} rows, expected {TEST_N_SESSIONS}")
    return idx


#: Characters per line that fit the text width at the 10 pt floor. TeX Gyre Heros averages about
#: 5.3 pt per character at 10 pt, so 453.6 pt holds roughly 85; 80 leaves a margin for the wide
#: glyphs a mean cannot see. Measured by the figure gate rather than assumed: at 88 the longest
#: caption lines still clipped.
_WRAP_COLS = 80


def _note_xlabel(ax: Any, *lines: str, size: float = 10.0) -> None:
    """Attach a multi-line note as the x-axis label, wrapped so it cannot run past the figure edge.

    ⚠ THE WRAP IS LOAD-BEARING NOW THAT THE TYPE FLOOR IS 10 pt AND THE PAGE IS FIXED.
    This helper used to keep notes inside the figure by setting them SMALLER than the axis-label
    default. That is no longer available: 8 pt is below the guideline floor, and the figures are now
    saved at exactly the text width instead of being cropped to their content, so an over-long line
    can no longer push the canvas outward either. Both of the old escape routes are closed, which
    leaves wrapping. Measured on the 2026-08-11 render before this change: six of the seven results
    figures carried at least one caption line clipped at the right edge, five of them in one figure.
    """
    # !! ONLY THE FIRST LINE IS AN AXIS LABEL. The rest were caption sentences living inside the
    # figure, and they cost twice: a reader could not tell them from an axis label, and they occupied
    # the strip below the axes, which is the only place a legend fits without covering data. This
    # module's own note at the forest plot recorded the consequence -- moving that legend below the
    # axes "is WORSE: it then collided with the multi-line axis note". Every dropped line is carried
    # by the LaTeX caption instead, which is word-excluded and set at 10 pt with an empty label.
    import textwrap

    head = textwrap.wrap(lines[0], _WRAP_COLS) if lines else [""]
    ax.set_xlabel(_caption(*head), fontsize=size)


def _place_labels(ax: Any, points: Sequence[tuple[float, float, str]], *,
                  fontsize: float = 10.0, avoid: Sequence[Any] = (),
                  avoid_curves: Sequence[tuple[np.ndarray, np.ndarray]] = (),
                  colors: Sequence[str] | None = None) -> None:
    """Annotate scatter points, choosing per-point offsets that do not collide.

    Greedy and deterministic: candidate offsets are tried in a fixed order and the first that
    overlaps neither an already-placed label box nor any data point is taken. Rendering label
    positions this way is what keeps an eleven-point panel readable at single-column width;
    a fixed offset for every point produces the overlapping stack it replaces.
    """
    ax.figure.canvas.draw()  # transforms must be current before any display-space arithmetic
    trans = ax.transData
    inv = trans.inverted()
    placed: list[tuple[float, float, float, float]] = []          # display-space label boxes
    for artist in avoid:  # legends and note boxes are obstacles too, not just other labels
        bb = artist.get_window_extent(renderer=ax.figure.canvas.get_renderer())
        placed.append((bb.x0, bb.y0, bb.x1, bb.y1))
    pts_disp = [trans.transform((x, y)) for x, y, _ in points]
    # Fitted and reference lines are obstacles too: a label a regression line runs through is as
    # unreadable as one another label sits on. Sample each curve densely in display space.
    curve_disp: list[np.ndarray] = []
    for cx, cy in avoid_curves:
        t = np.linspace(0.0, 1.0, 400)
        xs_c = np.interp(t, np.linspace(0.0, 1.0, len(cx)), np.asarray(cx, dtype=float))
        ys_c = np.interp(t, np.linspace(0.0, 1.0, len(cy)), np.asarray(cy, dtype=float))
        curve_disp.append(trans.transform(np.column_stack([xs_c, ys_c])))

    # Sizes must be in DISPLAY pixels, not points, or every box is ~a third too small at this
    # figure dpi and the overlap test silently passes on labels that do collide.
    px_per_pt = ax.figure.dpi / 72.0
    char_w, line_h = fontsize * 0.60 * px_per_pt, fontsize * 1.45 * px_per_pt
    # Candidate offsets: eight compass directions at four radii, near ones first. A point whose
    # near slots are all taken is pushed out and given a leader line rather than being stacked.
    # ⚠ THE LONG RADII ARE NOT PADDING, THEY ARE WHAT STOPS THE CLUSTER FROM STACKING. Six of the
    # eleven authoring lines sit inside a tenth of the panel around the origin, so their near slots
    # are taken by each other and the greedy search used to run out of candidates and fall through
    # to the "accept the crowding" branch, which is what produced the fan of crossing leaders in the
    # top-left corner of the compiled figure. The panel has a genuinely empty middle-right; radii out
    # to 96 px and two shallow horizontal directions let a blocked label reach it, and the leader
    # then does its job, which is to say which marker the name belongs to.
    dirs = [(1, 0.4), (1, -1), (-1, 0.4), (-1, -1), (0, 1), (0, -1.4), (1, 1.2), (-1, 1.2),
            (1, 0.0), (-1, 0.0), (1, -0.35), (1, 0.9)]
    candidates = [(ux * r * px_per_pt, uy * r * px_per_pt)
                  for r in (7, 14, 22, 32, 44, 58, 74, 96) for ux, uy in dirs]
    x_lo, x_hi = ax.get_window_extent().x0, ax.get_window_extent().x1
    y_lo, y_hi = ax.get_window_extent().y0, ax.get_window_extent().y1

    for idx, ((x, y, text), (px, py)) in enumerate(zip(points, pts_disp)):
        w, h = char_w * len(text), line_h
        best = None
        for dx, dy in candidates:
            x0 = px + dx if dx >= 0 else px + dx - w
            y0 = py + dy - (0.0 if dy >= 0 else h)
            box = (x0, y0, x0 + w, y0 + h)
            if box[0] < x_lo or box[2] > x_hi or box[1] < y_lo or box[3] > y_hi:
                continue  # never let a label hang over an axis
            hits_label = any(box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3]
                             for b in placed)
            # 9 px of clearance, not 5. At 5 the longest name ("deepseek-v4-pro") ended flush
            # against the registered node's diamond in the compiled figure, so the last glyph and
            # the marker touched. The margin is display pixels, so it is a real printed distance.
            hits_point = any(box[0] - 9 < qx < box[2] + 9 and box[1] - 9 < qy < box[3] + 9
                             for qx, qy in pts_disp)
            hits_curve = any(
                np.any((c[:, 0] > box[0] - 2) & (c[:, 0] < box[2] + 2)
                       & (c[:, 1] > box[1] - 2) & (c[:, 1] < box[3] + 2))
                for c in curve_disp
            )
            if not (hits_label or hits_point or hits_curve):
                best = (box, dx, dy)
                break
        if best is None:  # every slot blocked: fall back to the nearest one and accept the crowding
            x0, y0 = px + 8 * px_per_pt, py + 4 * px_per_pt
            best = ((x0, y0, x0 + w, y0 + h), 8 * px_per_pt, 4 * px_per_pt)
        box, dx, dy = best
        placed.append(box)
        colour = colors[idx] if colors is not None else "0.20"
        lx, ly = inv.transform((box[0], box[1] + h * 0.15))
        # A leader is drawn for EVERY label. In a crowded cluster the reader cannot otherwise tell
        # which marker a free-floating name belongs to, and colour alone is not enough.
        anchor_x = box[0] if dx >= 0 else box[2]
        ax0, ay0 = inv.transform((anchor_x, box[1] + h * 0.45))
        ax.plot([x, ax0], [y, ay0], color=colour, lw=0.7, alpha=0.85, zorder=2)
        ax.annotate(text, xy=(lx, ly), fontsize=fontsize, color=colour, zorder=5,
                    ha="left", va="bottom")


def _arm_label(arm: str) -> str:
    """The arm's PRINTED name, which is not always its config key.

    ⚠ THESE STRINGS ARE BAKED INTO A RASTER and cannot be corrected by editing the markdown, so they
    are the one place an arm can quietly acquire a second name. `placebo_shuffled` read
    "placebo (shuffled)" here until 2026-08-10 while the abstract, Table 5.3b and Table 5.9 all
    called it "scrambled" — a reader comparing a figure legend against a table column header had to
    infer that two differently named things were one arm. The document's canonical printed name for
    this arm is **scrambled**, bound to the config key in the Glossary, and this map must follow it.
    """
    pretty = {
        "distributional": "distributional (treatment)",
        "scalar": "scalar (primary control)",
        "scalar_cvar5": "scalar + CVaR-5%",
        "placebo": "placebo",
        "placebo_shuffled": "scrambled",
    }
    return pretty.get(arm, arm)


#: The dissertation's text width in points, from ``geometry:margin=2.5cm`` on A4. A figure saved wider
#: than this is scaled DOWN by pandoc's ``\pandocbounded``, and every glyph in it shrinks by the same
#: factor; a figure saved narrower is never scaled up. So this is the width to save at, exactly.
TEXT_WIDTH_PT = 453.6
FIG_WIDTH_IN = TEXT_WIDTH_PT / 72.0          # 6.30 in


def _rewrap_overwide_text(fig: Any) -> None:
    """Re-wrap any text artist that would render past the canvas, measuring rather than guessing.

    ⚠ WHY THIS EXISTS RATHER THAN A CHARACTER LIMIT. A per-string wrap width cannot work, because a
    label is centred on its AXES and the axes are inset by whatever the y-label and ticks need. Two
    lines of identical length therefore end at different x positions, and a title centred on the
    FIGURE has a different budget again. MEASURED on the 2026-08-11 render: six of the seven figures
    still clipped after an 80-character wrap, by 0.7 to 3.8 pt each, which is half a character and
    enough to cut the last word. One of them lost the end of "higher is better".

    So the width is measured on the drawn artist and the wrap is recomputed from the overrun. This is
    the single choke point every figure passes through, which is the right place for a rule that must
    hold for all of them. It never reduces type size: the 10 pt floor is the constraint being
    protected, so wrapping is the only degree of freedom left.
    """
    import textwrap

    # !! THE BUDGET IS SET BY THE CENTRE, NOT THE WIDTH. A label is centred on its own artist anchor,
    # and for an x-label that anchor is the centre of the AXES, which sits right of the figure centre
    # whenever a y-label and tick labels inset the left side. So a label NARROWER than the figure can
    # still run off the right edge. An earlier version of this function compared width against the
    # figure width and left five figures still clipping. The space actually available to a centred
    # artist is twice its distance to the NEARER edge.
    # Up to three passes, because re-wrapping adds lines, constrained layout reflows, and the anchor
    # can move. It converges quickly and the loop is bounded rather than open.
    for _ in range(3):
        fig.canvas.draw()
        W = fig.get_window_extent().width
        changed = False
        for art in fig.findobj(match=lambda o: hasattr(o, "get_text") and hasattr(o, "set_text")):
            txt = art.get_text()
            if not txt or len(txt) < 12:
                continue
            # ⚠ NEVER RE-WRAP A HAND-ALIGNED BLOCK. The turnover figure's numbered key lays its two
            # columns out with runs of spaces, and re-flowing it destroyed the alignment and cut the
            # model names: the rendered figure read "1 opus-5 (co", "2 deepseek-'", "4 qwen3.6-2".
            # A run of two or more spaces is the signature of a block whose author positioned it, and
            # such a block is never a candidate for automatic wrapping.
            if "  " in txt:
                continue
            try:
                ext = art.get_window_extent()
            except Exception:
                continue
            if ext.width <= 0 or (ext.x1 <= W and ext.x0 >= 0):
                continue
            cx = 0.5 * (ext.x0 + ext.x1)
            avail = 2.0 * max(1.0, min(cx, W - cx)) * 0.97
            longest = max((len(s) for s in txt.split("\n")), default=1)
            per_char = ext.width / max(longest, 1)
            fits = max(10, int(avail / max(per_char, 0.1)))
            if fits >= longest:
                continue
            # break_on_hyphens=False and break_long_words=False keep model identifiers intact:
            # the default would split "qwen3.6-27b" at its hyphen and "deepseek-v4-pro" twice.
            art.set_text("\n".join(
                seg for line in txt.split("\n")
                for seg in (textwrap.wrap(line, fits, break_on_hyphens=False,
                                          break_long_words=False) or [""])))
            changed = True
        if not changed:
            break
    fig.canvas.draw()


def _outside_legend(fig: Any, handles: Sequence[Any], labels: Sequence[str], *,
                    ncol: int = 3, size: float = 10.0) -> Any:
    """Put the legend BELOW every axes, at figure level, where it cannot deform the plot.

    ⚠ THIS IS THE FIX FOR THE WORST RENDERING DEFECT THE SUITE HAS SHIPPED, AND THE MECHANISM IS
    WORTH RECORDING BECAUSE IT IS INVISIBLE IN THE SOURCE. An axes-level ``ax.legend(...)`` with
    ``bbox_to_anchor`` remains a CHILD of the axes, so ``constrained_layout`` counts it as part of
    that axes' footprint. When the legend is wider than the axes -- three columns of sentence-length
    labels, in the case that failed -- the layout engine satisfies the constraint the only way it
    can, by shrinking the AXES until the combined box fits the canvas.

    MEASURED on the 2026-08-11 build, Figure 5.2 on page 53: the plotting area had collapsed to
    roughly a tenth of the text width, the x tick labels "0", "50" and "100" printed on top of one
    another as "5100 0", the axes title overlapped the y-axis label, and the legend entries wrapped
    across the full page around a plot nobody could read. The figure was not merely ugly. It carried
    no information at all, and it had passed every gate in the toolchain, because no gate looks at a
    rendered figure.

    A figure-level legend at ``loc="outside lower center"`` is laid out AGAINST the axes grid rather
    than inside it, so the engine reserves a strip for it and leaves the axes at full width.
    """
    return fig.legend(handles, labels, loc="outside lower center", ncol=ncol,
                      fontsize=size, frameon=False, handlelength=1.8, columnspacing=1.6)


def _save(fig: Any, stem: str) -> list[Path]:
    """Write ``<stem>.png`` (600 dpi) and ``<stem>.pdf`` at EXACTLY the text width.

    ⚠ THIS DELIBERATELY DOES NOT USE ``src.viz.style.savefig``, AND THE REASON IS MEASURED.
    That helper saves with ``bbox_inches="tight"``, which crops to the drawn content and therefore
    lets the page GROW when the content is wider than the canvas. Raising the type sizes to the
    10 pt guideline floor did exactly that: on 2026-08-11 the eleven-panel figure's page went from
    530 pt to 919 pt wide, pandoc scaled it by 0.493 to fit the text block, and the 10 pt labels
    landed at 4.9 pt. Enlarging the type had made the figure LESS legible. Tight cropping and a
    typographic floor are simply incompatible: one lets the page follow the content, the other needs
    the content to follow the page.

    Saving at a fixed width inverts that. The page is the text width, so pandoc's scale factor is
    exactly 1.000 and an authored 10 pt is a rendered 10 pt. ``constrained_layout`` (set by
    ``apply_house_style``) then does the adapting, shrinking the axes so the labels fit inside the
    canvas rather than pushing the canvas outward.

    ``src/viz/style.py`` is drift-fenced to the ops lane, so the helper cannot be corrected there;
    this override is the only place the behaviour can be changed. The height is left as each figure
    declared it, because only the width is bounded by the text block.
    """
    # !! bbox_inches=None IS LOAD-BEARING AND MUST BE PASSED EXPLICITLY. apply_house_style sets the
    # RCPARAM "savefig.bbox": "tight" (src/viz/style.py:72), so a bare fig.savefig() still crops and
    # still lets the page grow past the text width. Measured 2026-08-11: with the size fixed but the
    # rcParam left alone the pages came out 462-485 pt and the 10 pt type rendered at 9.3-9.8 pt.
    fig.set_size_inches(FIG_WIDTH_IN, fig.get_size_inches()[1])
    _rewrap_overwide_text(fig)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / f"{stem}.png"
    fig.savefig(out, dpi=600, bbox_inches=None)
    fig.savefig(out.with_suffix(".pdf"), bbox_inches=None)
    _LOG.info("wrote %s (+ .pdf) at %.1f pt wide", out, FIG_WIDTH_IN * 72.0)
    return [out, out.with_suffix(".pdf")]


# --------------------------------------------------------------------------- #
# (a) Cross-line forest of the treatment-minus-control contrast                 #
# --------------------------------------------------------------------------- #
def fig_cross_line_forest(store: dict[str, np.ndarray]) -> Any:
    """One row per author line: mean paired (distributional - scalar) terminal Sharpe, 95% CI."""
    import matplotlib.pyplot as plt
    from src.viz.style import OKABE_ITO

    rows = []
    for i, label in enumerate(LINE_LABELS):
        d = paired_contrast(store, label, "sharpe_net")
        m, lo, hi = mean_ci(d, seed=100 + i)
        rows.append((label, m, lo, hi))
    rows.sort(key=lambda r: r[1])
    n_excl = sum(1 for _, _, lo, hi in rows if lo > 0.0 or hi < 0.0)
    n_pos = sum(1 for _, m, _, _ in rows if m > 0.0)

    fig, ax = plt.subplots(figsize=(6.15, 4.25))
    ys = np.arange(len(rows))
    for y, (label, m, lo, hi) in zip(ys, rows):
        colour = OKABE_ITO["blue"]
        ax.plot([lo, hi], [y, y], color=colour, lw=1.6, solid_capstyle="butt", zorder=2)
        ax.plot([lo, lo], [y - 0.16, y + 0.16], color=colour, lw=1.2, zorder=2)
        ax.plot([hi, hi], [y - 0.16, y + 0.16], color=colour, lw=1.2, zorder=2)
        ax.plot([m], [y], marker="o", ms=5, color=colour, mec="white", mew=0.6, zorder=3)
        if label == CORE_LINE:
            ax.plot([m], [y], marker="o", ms=10, mfc="none", mec="0.20", mew=1.1, zorder=4)
    ax.axvline(0.0, color="0.35", lw=1.0, ls="--", zorder=1)

    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows])
    ax.set_ylim(-0.7, len(rows) - 0.2)
    _note_xlabel(
        ax,
        "Contrast in terminal Sharpe (annualised, NET)",
        f"bars: 95% percentile bootstrap CI over {N_SEEDS} paired seeds",
        f"{n_excl} of {len(rows)} lines exclude zero; {n_pos} of {len(rows)} favour distributional",
        size=10.0,
    )
    ax.set_title("The treatment-minus-control contrast, by authoring model")

    span = max(abs(v) for _, _, lo, hi in rows for v in (lo, hi))
    ax.set_xlim(-1.35 * span, 1.35 * span)
    y_arrow = len(rows) - 0.55
    ax.annotate("", xy=(1.18 * span, y_arrow), xytext=(0.25 * span, y_arrow),
                arrowprops=dict(arrowstyle="->", color="0.35", lw=1.0))
    ax.text(0.24 * span, y_arrow + 0.16, "distributional better", color="0.30", fontsize=10, ha="left")
    ax.annotate("", xy=(-1.18 * span, y_arrow), xytext=(-0.25 * span, y_arrow),
                arrowprops=dict(arrowstyle="->", color="0.35", lw=1.0))
    ax.text(-0.24 * span, y_arrow + 0.16, "scalar better", color="0.30", fontsize=10, ha="right")

    # ⚠ THE LABELS ARE SHORT BECAUSE THE LEGEND'S WIDTH, NOT ITS PLACEMENT, WAS THE DEFECT.
    # At 10 pt the old labels ("opus-5, the registered single-look node") made the box 1.6 axis units
    # wide, so at "lower right" it reached back past x = -0.25 and covered the gpt-5.6-luna point and
    # its entire error bar. Moving it below the axes was tried and is WORSE: it then collided with the
    # multi-line axis note. Shortening the labels is the fix that works, and it is better design in any
    # case, because a legend entry is an index and not a sentence. The registered node is identified in
    # full by the caption and by the bold row label, so nothing is lost. Both versions were rendered and
    # looked at before this one was kept.
    handles = [
        plt.Line2D([], [], color=OKABE_ITO["blue"], marker="o", ls="-", ms=5,
                   label="one authoring line"),
        plt.Line2D([], [], color="none", marker="o", ls="", ms=10, mfc="none", mec="0.20", mew=1.1,
                   label="the registered node"),
        plt.Line2D([], [], color="0.35", ls="--", lw=1.0, label="no difference"),
    ]
    _outside_legend(fig, handles, [h.get_label() for h in handles], ncol=3)
    return fig


# --------------------------------------------------------------------------- #
# (b) Per-seed dispersion of terminal Sharpe                                    #
# --------------------------------------------------------------------------- #
def fig_seed_dispersion(store: dict[str, np.ndarray], line: str = CORE_LINE) -> Any:
    """Raincloud of the ACTUAL per-seed terminal Sharpe cloud for each arm — never bars of means."""
    import matplotlib.pyplot as plt
    from scipy.stats import gaussian_kde

    from src.viz.style import arm_style, iqm_bootstrap_ci

    fig, ax = plt.subplots(figsize=(6.15, 4.10))
    rng = np.random.default_rng(7)
    for i, arm in enumerate(ARMS):
        y0 = len(ARMS) - 1 - i  # house order top-to-bottom
        x = get(store, line, arm, "sharpe_net")
        st = arm_style(arm)

        kde = gaussian_kde(x)
        xs = np.linspace(x.min() - 0.1, x.max() + 0.1, 256)
        dens = kde(xs)
        dens = 0.34 * dens / dens.max()
        ax.fill_between(xs, y0 + 0.10, y0 + 0.10 + dens, color=st["color"], alpha=0.35,
                        lw=0.8, edgecolor=st["color"], hatch=st["hatch"], zorder=2)

        jitter = y0 - 0.14 - rng.uniform(0.0, 0.20, size=x.size)
        ax.scatter(x, jitter, s=5, color=st["color"], alpha=0.55, lw=0, zorder=2)

        q1, med, q3 = np.quantile(x, [0.25, 0.5, 0.75])
        ax.plot([q1, q3], [y0 + 0.02, y0 + 0.02], color="0.15", lw=4.0, solid_capstyle="butt", zorder=3)
        ax.plot([med], [y0 + 0.02], marker="|", ms=10, color="white", mew=1.6, zorder=4)
        point, lo, hi = iqm_bootstrap_ci(x, seed=i)
        ax.plot([lo, hi], [y0 - 0.42, y0 - 0.42], color="0.15", lw=1.2, zorder=3)
        ax.plot([point], [y0 - 0.42], marker="D", ms=5, color="0.15", mec="white", mew=0.6, zorder=4)

    ax.set_yticks([len(ARMS) - 1 - i + 0.05 for i in range(len(ARMS))])
    ax.set_yticklabels([_arm_label(a) for a in ARMS])
    # The legend now sits OUTSIDE the axes, so the empty band that used to be reserved for it inside
    # them is dead space. It ran to -1.5, a full arm's height of blank paper under the lowest cloud.
    ax.set_ylim(-0.85, len(ARMS) - 0.35)
    _note_xlabel(
        ax,
        "Terminal Sharpe ratio (annualised, NET) — higher is better",
        f"one point per seed, {N_SEEDS} seeds per arm",
    )
    ax.set_title(f"Per-seed dispersion of terminal Sharpe, {line} line")

    handles = [
        plt.Line2D([], [], marker="o", ls="", ms=4, color="0.35", label="one seed"),
        plt.Line2D([], [], color="0.15", lw=4, label="median and IQR"),
        plt.Line2D([], [], color="0.15", marker="D", ls="-", ms=5,
                   label="interquartile mean, 95% CI"),
    ]
    # Three columns now fit, where they did not before, because the labels are short and the legend
    # is laid out at FIGURE level against the full text block rather than against the axes.
    _outside_legend(fig, handles, [h.get_label() for h in handles], ncol=3)
    return fig


def fig_dispersion_all_lines(store: dict[str, np.ndarray]) -> Any:
    """The same per-seed clouds for ALL eleven author lines, so no single line stands for the study.

    The companion single-line raincloud shows one line in full detail; this panel is the one that
    carries the dispersion claim, because the reported conclusion is a statement about eleven lines
    rather than about whichever line the registered plan happened to seat.
    """
    import matplotlib.pyplot as plt
    from src.viz.style import arm_style

    order = sorted(LINE_LABELS,
                   key=lambda lb: float(np.median([iqr(get(store, lb, a, "sharpe_net")) for a in ARMS])))
    # ⚠ THREE COLUMNS, NOT FOUR, AND THE REASON IS THE TYPE FLOOR. At four columns each panel is
    # 453.6/4 = 113 pt wide, and at the 10 pt floor the longest line names overrun it: the rendered
    # figure printed "gemini-2.5-flash" and "nemotron-3-super" as one run-together string. Three
    # columns give 151 pt per panel, which holds the longest name with room to spare, and eleven
    # lines plus the legend fill 3 x 4 exactly with no empty cell.
    ncol = 3
    nrow = int(np.ceil((len(order) + 1) / ncol))
    # ⚠ 1.72 in PER ROW, AND THE NUMBER IS SET BY THE CAPTION, NOT BY THE PANELS. At 2.0 the figure
    # was 576 pt tall and LaTeX gave it a page of its own, which pushed its four-line caption to the
    # NEXT page: page 55 of the 2026-08-12 build carried a caption and nothing else, orphaned from
    # the exhibit it describes. A4 at 2.5 cm margins leaves about 700 pt of text height and the
    # caption needs roughly 60, so 4 x 1.72 in = 495 pt leaves the figure and its caption on one page
    # with room to spare. A caption on a different page from its figure is a Criterion-4 defect and
    # this is the only lever that fixes it, because the caption length is not negotiable.
    # !! sharey=False DELIBERATELY. Nine of the eleven lines cluster inside about 0.4 Sharpe and
    # two spread over 1.6. Sharing the axis put those nine on the wide range, so each used the top
    # fifth of its panel and four fifths were empty -- the dispersion this exhibit exists to show
    # became invisible in exactly the panels where it is tightest. Each panel now sets its own
    # range and the caption states that the ranges differ, which is the honest way to show shape.
    fig, axes = plt.subplots(nrow, ncol, figsize=(6.15, 1.50 * nrow), sharey=False)
    flat = axes.ravel()
    rng = np.random.default_rng(3)
    lo = min(get(store, lb, a, "sharpe_net").min() for lb in order for a in ARMS)
    hi = max(get(store, lb, a, "sharpe_net").max() for lb in order for a in ARMS)

    # The bottom-most panel in each column carries the arm names. Repeating five labels under all
    # eleven panels would be 55 labels restating one legend; omitting them entirely, which is what
    # this figure did until now, left the reader unable to say which cloud was which arm without
    # counting colours against a legend in the corner. Labelling the last panel of each column is the
    # standard small-multiples answer, because every panel shares the same five categories.
    bottom_of_col = {c: max(i for i in range(len(order)) if i % ncol == c) for c in range(ncol)}

    for idx, (ax, label) in enumerate(zip(flat, order)):
        medians = []
        for i, arm in enumerate(ARMS):
            x = get(store, label, arm, "sharpe_net")
            st = arm_style(arm)
            ax.scatter(i + rng.uniform(-0.26, 0.26, x.size), x, s=2.2, color=st["color"],
                       alpha=0.45, lw=0, zorder=2)
            q1, med, q3 = np.quantile(x, [0.25, 0.5, 0.75])
            medians.append(med)
            ax.plot([i - 0.34, i + 0.34], [med, med], color="0.10", lw=1.3, zorder=4)
            ax.plot([i, i], [q1, q3], color="0.10", lw=0.9, zorder=3)
        # ⭐ RING THE WINNING ARM. This is the one addition that turns a page of clouds into the
        # dissertation's central claim, and it costs no words: the reader sees at a glance that the
        # ringed arm MOVES from panel to panel. A stable mechanism with an unstable winner is the
        # argument the whole document is built to deliver, and here it is visible rather than counted.
        best = int(np.argmax(medians))
        ax.plot([best], [medians[best]], marker="o", ms=9, mfc="none", mec="0.10", mew=1.2, zorder=5)
        ax.set_title(label, fontsize=10)
        ax.set_xticks(range(len(ARMS)))
        if idx == bottom_of_col.get(idx % ncol):
            ax.set_xticklabels(["dist", "scalar", "+CVaR", "placebo", "scram"],
                               rotation=45, ha="right", rotation_mode="anchor", fontsize=10)
        else:
            ax.set_xticklabels([])
        ax.set_xlim(-0.6, len(ARMS) - 0.4)
        ax.axhline(0.0, color="0.6", lw=0.6, ls=":", zorder=1)
        ax.tick_params(labelsize=10)
    # !! THE GLOBAL set_ylim THAT STOOD HERE IS GONE WITH sharey. It ran after the loop, so it bound
    # only the LAST axis, which under sharey propagated to all eleven and now would leave one panel
    # on the global range while its ten neighbours autoscale. That is worse than either policy
    # applied consistently, and it is exactly the kind of half-applied change a rendered check
    # catches and a code read does not: the glm-5.2 panel came back with a visibly different scale.

    for ax in flat[len(order):]:  # spare cells carry the legend rather than an empty frame
        ax.axis("off")
    # ⚠ THE LEGEND IS SPLIT IN TWO, AND THE SPLIT IS ARITHMETIC RATHER THAN TASTE. Eight entries
    # stacked at the 10 pt floor need about 112 pt of height; the spare grid cell is 1.50 in, i.e.
    # 108 pt. So the single legend did not fit and matplotlib let it overflow UPWARD, out of its own
    # cell and into the row above, which is what made the panel grid read as broken in the compiled
    # figure: the block of keys appeared to float between rows three and four rather than sitting in
    # a cell. Dropping to 9 pt would have fixed the height and broken the guide's 10 pt floor.
    # Five arm keys fit the cell (5 x 14 = 70 pt) and the three annotation keys become a strip under
    # the grid, where there is a whole figure width to put them in.
    arm_handles = [plt.Line2D([], [], marker="o", ls="", ms=4, color=arm_style(a)["color"],
                              label=_arm_label(a)) for a in ARMS]
    flat[len(order)].legend(handles=arm_handles, loc="center", fontsize=10, frameon=False,
                            labelspacing=0.55)
    note_handles = [plt.Line2D([], [], color="0.10", lw=1.3, label="median"),
                    plt.Line2D([], [], color="0.10", lw=0.9, label="interquartile range"),
                    plt.Line2D([], [], marker="o", ls="", ms=9, mfc="none", mec="0.10", mew=1.2,
                               label="best arm on this line")]
    _outside_legend(fig, note_handles, [h.get_label() for h in note_handles], ncol=3)

    # ⚠ ONE SHARED Y-LABEL, NOT ONE PER ROW. Four two-line labels fitted while the panels were 2.0 in
    # tall. At 1.50 in they do not: each label is centred on its own row, the rows are now shorter
    # than the label, and the compiled figure printed "Terminal SharpeTerminal SharpeTerminal Sharpe"
    # stacked on top of itself down the left margin. A figure-level label says the same thing once,
    # centred on the whole grid, and cannot collide with anything.
    fig.supylabel("Terminal Sharpe (annualised, NET)", fontsize=10)
    fig.suptitle(f"Per-seed dispersion of terminal Sharpe, every author line (n = {N_SEEDS} seeds per arm)",
                 fontsize=10)
    # !! THE THREE-LINE FOOTER THAT STOOD HERE IS NOW IN THE LaTeX CAPTION, together with the
    # statement that the panels no longer share a y-axis. It was caption text rendered inside the
    # figure, which is the confusion Tamer named: a reader could not tell it from an axis label.
    return fig


# --------------------------------------------------------------------------- #
# (c) Capability gradient: within-arm dispersion, ordered across lines          #
# --------------------------------------------------------------------------- #
def fig_capability_gradient(store: dict[str, np.ndarray]) -> Any:
    """Within-arm IQR of terminal Sharpe per line, lines ordered by their across-arm median IQR."""
    import matplotlib.pyplot as plt
    from src.viz.style import arm_style

    table: dict[str, dict[str, tuple[float, float, float]]] = {}
    for li, label in enumerate(LINE_LABELS):
        table[label] = {arm: iqr_ci(get(store, label, arm, "sharpe_net"), seed=10 * li + ai)
                        for ai, arm in enumerate(ARMS)}
    order = sorted(LINE_LABELS, key=lambda lb: float(np.median([v[0] for v in table[lb].values()])))

    # ⛔ THE MODEL AXIS IS VERTICAL, AND THAT CHOICE REPLACES A LONG-RUNNING ARGUMENT ABOUT ROTATION.
    # Three successive passes tried 30, then 55, then 75 degrees of tick rotation to stop eleven
    # model names overprinting one another along a horizontal axis, each angle computed from the
    # measured per-tick slot. The 75-degree version still shipped a defect: on the compiled page the
    # rotated names ran straight through the legend block beneath them, because the rotation buys
    # horizontal room by spending vertical room, and the legend lives in exactly the space it spends.
    # Transposing the axes deletes the problem instead of managing it. A model name laid along the
    # y-axis is horizontal, reads at full size, needs no rotation and cannot collide with anything.
    # The ordering also reads better this way: most stable at the top, which is the direction a reader
    # scans a ranked list. Get the representation right and the special case disappears.
    fig, ax = plt.subplots(figsize=(6.3, 4.55))
    offsets = np.linspace(0.30, -0.30, len(ARMS))
    for ai, arm in enumerate(ARMS):
        st = arm_style(arm)
        ys, xs, los, his = [], [], [], []
        for yi, label in enumerate(order):
            v, lo, hi = table[label][arm]
            ys.append(yi + offsets[ai]); xs.append(v); los.append(v - lo); his.append(hi - v)
        ax.errorbar(xs, ys, xerr=[los, his], fmt=st["marker"], ms=4.6, color=st["color"],
                    ecolor=st["color"], elinewidth=0.8, capsize=1.6, lw=0, mec="white", mew=0.4,
                    label=_arm_label(arm), zorder=3)
    med = [float(np.median([table[lb][a][0] for a in ARMS])) for lb in order]
    ax.plot(med, np.arange(len(order)), color="0.35", lw=1.2, zorder=2,
            label="median of the five arms")
    # A faint band behind alternate rows, which is what lets an eye track a row across the full width
    # without a heavy grid. Standard in ranked tables and it costs no ink the data needs.
    for yi in range(0, len(order), 2):
        ax.axhspan(yi - 0.5, yi + 0.5, color="0.94", zorder=0)

    ax.set_yticks(np.arange(len(order)))
    ax.set_yticklabels(order)
    ax.set_ylim(len(order) - 0.5, -0.5)
    # ⚠ A LOG X-AXIS, AND THE REASON IS THAT THE LOAD-BEARING CLAIM IS A RATIO. The controlled
    # within-family contrast this exhibit exists to support is "qwen3.5-9b is 5.4 times less stable
    # than qwen3.6-27b", and on a log axis a ratio is a DISTANCE, so the reader measures the claim by
    # eye. A linear axis also wastes two thirds of its width: the values span 0.02 to 0.93, one arm
    # of one model sits at 0.77, and on a linear scale that single point squeezes nine of the eleven
    # rows into the left third of the panel.
    ax.set_xscale("log")
    ax.set_xticks([0.02, 0.05, 0.1, 0.2, 0.5, 1.0])
    ax.set_xticklabels(["0.02", "0.05", "0.1", "0.2", "0.5", "1.0"])
    ax.grid(axis="y", visible=False)
    _note_xlabel(ax, "Within-arm IQR of terminal Sharpe (NET) — left is more stable")
    # ⚠ THE TITLE MUST NOT NAME A GRADIENT. The axis is sorted by the quantity plotted, so the
    # top-to-bottom rise is arithmetic; a title reading "Capability gradient" claimed exactly what the
    # caption then had to retract in fourteen bolded lines (Criterion 4 pass, 2026-08-10). The honest
    # title names the quantity and says it is ordered. What the ordering licenses is Appendix G.27.
    ax.set_title("Seed-to-seed instability, by model (ordered)")
    handles, labels = ax.get_legend_handles_labels()
    # The median line is registered first because it is drawn last; move it to the end so the legend
    # reads arms-then-summary, which is the order the eye needs them in.
    handles, labels = handles[1:] + handles[:1], labels[1:] + labels[:1]
    _outside_legend(fig, handles, labels, ncol=3)
    return fig


# --------------------------------------------------------------------------- #
# (d) Expanding-window Sharpe trajectory                                        #
# --------------------------------------------------------------------------- #
def fig_sharpe_trajectory(store: dict[str, np.ndarray], line: str = CORE_LINE) -> Any:
    """Expanding-window NET Sharpe against calendar time: every seed path, plus the quantile fan."""
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from src.viz.style import arm_style

    grid = store["__grid__"]
    dates = _test_dates()
    x = dates[grid - 1] if dates is not None else grid

    # ⛔ ONE PANEL WITH BOTH ARMS OVERLAID, NOT TWO STACKED PANELS. The two conditions used to be
    # drawn one above the other, and the reader had to hold one fan in memory while looking at the
    # other to answer the only question the exhibit is here to answer: do the paths differ? They do
    # not, and overlaid that is visible in a second rather than inferred from a comparison the reader
    # performs. It also halves the height, which on a fixed page budget is a page returned to the
    # discussion. The per-seed spaghetti stays, because the duty this figure discharges is to show
    # the random object rather than a summary of it.
    arms = (TREATMENT, CONTROL)
    fig, ax = plt.subplots(figsize=(6.3, 3.40))
    handles: list[Any] = []
    for arm in arms:
        traj = get(store, line, arm, "traj")
        st = arm_style(arm)
        for row in traj:
            ax.plot(x, row, color=st["color"], lw=0.3, alpha=0.055, zorder=1)
        q1, med, q3 = np.quantile(traj, [0.25, 0.5, 0.75], axis=0)
        ax.fill_between(x, q1, q3, color=st["color"], alpha=0.28, lw=0, zorder=2)
        (h,) = ax.plot(x, med, color=st["color"], lw=1.8, zorder=3, label=_arm_label(arm))
        handles.append(h)
    ax.axhline(0.0, color="0.45", lw=0.8, ls=":", zorder=1)
    ax.set_ylim(bottom=-0.35)

    handles += [
        plt.Line2D([], [], color="0.45", lw=0.6, label=f"one seed ({N_SEEDS} per arm)"),
        plt.Rectangle((0, 0), 1, 1, color="0.45", alpha=0.28, label="25-75th percentile"),
    ]
    # Short labels here, not the house arm names. Four columns of the full names overran the text
    # block and the auto-rewrap then broke "distributional (treatment)" across two lines while
    # clipping "25-75th percentile" at the right edge. The arms are named in full in the caption.
    leg_labels = ["distributional", "scalar", f"one seed ({N_SEEDS}/arm)", "25-75th pct"]
    # !! ONE FIGURE-LEVEL LEGEND, NOT ONE PER PANEL, AND IT MUST BE fig.legend RATHER THAN
    # ax.legend. Both panels carried an identical four-entry legend sitting on the data. Attaching
    # the merged legend to the lower AXES instead put a very wide artist inside a constrained layout
    # that then shrank the axes to fit it: the rendered trajectory collapsed to a single vertical
    # line about 40 pt wide. `loc="outside lower center"` reserves a strip on the FIGURE, so the
    # axes keep their width. Caught by looking at the render, which a code read would not have.
    _outside_legend(fig, handles, leg_labels, ncol=4, size=9.6)

    ax.set_ylabel(_caption("Expanding-window Sharpe", "(annualised, NET)"))
    if dates is not None:
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    # The span, the session count and the 126-session opening are in the LaTeX caption now. Only the
    # quantity the axis measures stays, which is what an axis label is for.
    ax.set_xlabel("End of the expanding window")
    ax.set_title(f"Sharpe trajectory through the test window, {line} line", fontsize=11)
    return fig


# --------------------------------------------------------------------------- #
# (e) Seed trajectory: the running estimate against the number of seeds         #
# --------------------------------------------------------------------------- #
#: Prefix below which the cross-line panel draws no interval (see the comment at its use site).
_BAND_MIN_N = 6


def fig_seed_trajectory(store: dict[str, np.ndarray]) -> Any:
    """Running contrast estimate vs seed count, seeds entering in REGISTERED order (never sorted)."""
    import matplotlib.pyplot as plt
    from src.viz.style import OKABE_ITO

    ns = np.arange(1, N_SEEDS + 1)
    core = paired_contrast(store, CORE_LINE, "sharpe_net")  # registered seed order 0..101, as banked
    point, lo, hi = running_mean_ci(core, seed=11)

    fig, axes = plt.subplots(2, 1, figsize=(6.3, 4.80), sharex=True)

    ax = axes[0]
    band = ax.fill_between(ns, lo, hi, color=OKABE_ITO["vermillion"], alpha=0.20, lw=0)
    (curve,) = ax.plot(ns, point, color=OKABE_ITO["vermillion"], lw=1.7)
    (zero,) = ax.plot([], [], color="0.35", lw=1.0, ls="--")
    ax.axhline(0.0, color="0.35", lw=1.0, ls="--")
    ax.axvline(N_SEEDS, color="0.20", lw=1.0, ls="-")
    ax.plot([N_SEEDS], [point[-1]], marker="D", ms=6, color="0.10", zorder=5)
    # ⚠ A DEPTH IS NOT A RUNG, and this document makes that distinction load-bearing. 102 is the
    # contiguous seed DEPTH; the banked tier on the frozen ladder [30, 100, 189, 279, 340, 403, 568]
    # is rung 100. An earlier annotation read "banked rung n = 102", which names a tier the study has
    # not reached and which `check_rung_freshness.py` rejects outright (passing 102 exits 2).
    # ⛔ THE ANNOTATION SITS ABOVE THE TERMINAL POINT, NOT BELOW IT (2026-08-11).
    # It was offset (-14, -34), which put it in the lower-right quadrant -- the same quadrant as the
    # legend at `loc="lower right"` below. Measured on the compiled figure, the annotation and the
    # legend's "no difference" entry overlapped by 65.9 pt, and because the legend carries an opaque
    # frame it painted over the annotation's second line, so "(estimate -0.076)" was unreadable.
    # Flipping the offset moves it to the upper-right quadrant, which carries no text at all: the
    # zero reference line's own label lives in the legend rather than on the line.
    ax.annotate(f"n = {N_SEEDS}, rung 100\n{point[-1]:+.3f}",
                xy=(N_SEEDS, point[-1]), xytext=(-16, 26), textcoords="offset points",
                ha="right", va="bottom", fontsize=9.6, color="0.15",
                arrowprops=dict(arrowstyle="-", color="0.35", lw=0.8))
    ax.set_ylabel(_caption("Contrast in Sharpe", "(annualised, NET)"))
    ax.set_title(f"The registered node, {CORE_LINE}", fontsize=10, loc="left")

    ax = axes[1]
    leg_handles: list[Any] = []
    for i, label in enumerate(LINE_LABELS):
        d = paired_contrast(store, label, "sharpe_net")
        # Every line gets its own interval: a panel of eleven bare running means would be exactly
        # the point-estimate-without-spread defect this whole exhibit exists to avoid.
        run, rlo, rhi = running_mean_ci(d, reps=1_000, seed=500 + i)
        # A bootstrap interval on two or three seeds is not an interval, and drawing it would
        # stretch the shared y-range so far that the eleven curves stop being separable.
        rlo, rhi = rlo.copy(), rhi.copy()
        rlo[:_BAND_MIN_N - 1] = np.nan
        rhi[:_BAND_MIN_N - 1] = np.nan
        if label == CORE_LINE:
            ax.fill_between(ns, rlo, rhi, color=OKABE_ITO["vermillion"], alpha=0.22, lw=0, zorder=3)
            ax.plot(ns, run, color=OKABE_ITO["vermillion"], lw=1.8, zorder=4)
        else:
            leg = ax.fill_between(ns, rlo, rhi, color=OKABE_ITO["blue"], alpha=0.13, lw=0, zorder=1)
            (line_h,) = ax.plot(ns, run, color=OKABE_ITO["blue"], lw=0.8, alpha=0.75, zorder=2)
            if i == 1:
                leg_handles = [line_h, leg]
    ax.axhline(0.0, color="0.35", lw=1.0, ls="--")
    ax.axvline(N_SEEDS, color="0.20", lw=1.0, ls="-")
    ax.set_ylabel(_caption("Contrast in Sharpe", "(annualised, NET)"))
    ax.set_title("All eleven author lines", fontsize=10, loc="left")
    ax.set_xlim(1, N_SEEDS + 3)
    # ONE legend for the whole figure, below both panels. Two axes-level legends with long labels
    # were what crushed the plotting area to a sliver on the shipped 2026-08-11 build.
    _outside_legend(fig, [curve, band] + leg_handles + [zero],
                    ["registered node", "its 95% CI", "one of ten legs", "their 95% CIs",
                     "no difference"], ncol=3, size=9.6)
    _note_xlabel(
        ax,
        "Seeds included, in registered order, never sorted",
        "Above the zero line the treatment is better; below it the control is better.",
        f"Lower panel: running means from n = 1, intervals from n = {_BAND_MIN_N} where a bootstrap"
        " interval is meaningful.",
        f"Stopping is EXOGENOUS: the pre-committed calendar cut-off of {STOPPING_DATE}, never a"
        " data-dependent stop.",
        f"The marked rung n = {N_SEEDS} is the contiguous rung banked as at {RUNG_MEASURED_DATE};"
        " the campaign is still running.",
        "NO inference was drawn at any prefix. The prefix curve is a diagnostic only.",
        size=10.0,
    )
    fig.suptitle("Seed trajectory: how the estimate settled as seeds accumulated", fontsize=12)
    return fig


# --------------------------------------------------------------------------- #
# (f) The measured mechanism: turnover change against Sharpe change             #
# --------------------------------------------------------------------------- #
def fig_turnover_mechanism(store: dict[str, np.ndarray]) -> Any:
    """Delta turnover vs delta Sharpe, one point per line, both axes carrying bootstrap CIs."""
    import matplotlib.pyplot as plt
    from scipy.stats import spearmanr
    from src.viz.style import OKABE_ITO

    pts = []
    for i, label in enumerate(LINE_LABELS):
        dt = paired_contrast(store, label, "turnover")
        ds = paired_contrast(store, label, "sharpe_net")
        tm, tlo, thi = mean_ci(dt, seed=200 + i)
        sm, slo, shi = mean_ci(ds, seed=300 + i)
        pts.append((label, tm, tlo, thi, sm, slo, shi))

    xs = np.array([p[1] for p in pts])
    ys = np.array([p[4] for p in pts])
    rho, pval = spearmanr(xs, ys)

    fig, ax = plt.subplots(figsize=(6.3, 4.62))
    ax.axhline(0.0, color="0.55", lw=0.8, ls=":", zorder=1)
    ax.axvline(0.0, color="0.55", lw=0.8, ls=":", zorder=1)
    slope, intercept = np.polyfit(xs, ys, 1)
    xf = np.linspace(xs.min() - 0.05, xs.max() + 0.05, 50)
    ax.plot(xf, slope * xf + intercept, color="0.45", lw=1.0, ls="--", zorder=2,
            label=f"least-squares fit (slope {slope:+.2f} Sharpe per unit turnover)")
    # ⛔ THE TWO QUADRANT GLOSSES ARE GONE, AND THE CORNERS THEY HELD ARE THE FIX FOR THIS FIGURE.
    # They read "trades more, earns more" and "trades less, earns less", placed in the two corners the
    # data never occupies. As orientation they were redundant with the x-label, which already says
    # "right = the treatment trades MORE", and they were occupying the only two regions of the panel
    # with room to spare. What they cost was severe: eight of the eleven lines sit inside a fifth of
    # the x-range, `_place_labels` had nowhere to send them, and the compiled figure carried seven
    # names fanned across the middle on long crossing leaders. Which name belonged to which point was
    # not recoverable by eye. The upper-right corner now holds a zoom of that cluster instead.

    def _draw_points(target: Any, subset: Sequence[Any], *, ms: float, ring: float) -> None:
        for label, tm, tlo, thi, sm, slo, shi in subset:
            target.errorbar([tm], [sm], xerr=[[tm - tlo], [thi - tm]],
                            yerr=[[sm - slo], [shi - sm]], fmt="o", ms=ms, color=OKABE_ITO["blue"],
                            ecolor=OKABE_ITO["blue"], elinewidth=0.9, capsize=1.8, mec="white",
                            mew=0.6, zorder=3)
            if label == CORE_LINE:
                target.plot([tm], [sm], marker="o", ms=ring, mfc="none", mec="0.20", mew=1.1,
                            zorder=4)

    _draw_points(ax, pts, ms=5, ring=10)
    # pad 0.05, not 0.16. At 0.16 the axes ran a seventh of the x-range past the data on BOTH sides,
    # so a panel already too crowded in its middle was spending a third of its width on margin.
    pad_x = 0.05 * (xs.max() - xs.min())
    pad_y = 0.08 * (ys.max() - ys.min())
    ax.set_xlim(xs.min() - pad_x, xs.max() + pad_x)
    ax.set_ylim(ys.min() - pad_y, ys.max() + pad_y)

    # ★ THE ZOOM. The claim this exhibit carries is a slope across the whole range, and the whole
    # range is set by three lines that trade very differently from the other eight. Those eight are
    # not noise to be cropped away: they are the lines on which the treatment barely moved turnover,
    # and whether they sit on the same slope is precisely what decides whether the mechanism is one
    # relationship or two populations. So the panel keeps every point and the corner shows the
    # crowded part at a readable scale. The window is taken from the data rather than hard-coded, so
    # it cannot go stale if a line's contrast moves.
    # ⚠ 0.05, AND THE WIDER 0.12 WAS TRIED FIRST AND FAILED FOR A REASON WORTH RECORDING. At 0.12 the
    # inset held eight lines, which sounds better and reads worse: five of those eight sit inside
    # 0.06 of turnover and 0.09 of Sharpe of one another, so at a zoom wide enough to also hold
    # haiku-4.5 and gpt-5.6-luna the five were still coincident and their names still needed leaders
    # across the panel. Three successive placement fixes each moved the collision somewhere else
    # rather than removing it, which is the signal that the window was wrong rather than the placer.
    # A zoom must be tight enough that the points it magnifies actually separate. At 0.05 the inset
    # holds exactly the five that overlap, they spread across its full width, and the three lines it
    # sheds have room to be labelled on the main panel, where nothing else competes for their corner.
    CLUSTER_HALF_WIDTH = 0.05
    cluster = [p for p in pts if abs(p[1]) <= CLUSTER_HALF_WIDTH]
    outer = [p for p in pts if abs(p[1]) > CLUSTER_HALF_WIDTH]
    cx = np.array([p[1] for p in cluster])
    cy = np.array([p[4] for p in cluster])
    # The inset takes the whole upper-right quadrant, which the fit line leaves empty: the line falls
    # from +0.31 at the left edge to -1.05 at the right, so everything above y = 0.3 and right of
    # x = 0.2 is free. A smaller inset was tried first at 0.44 x 0.42 and it merely relocated the
    # crowding, because four of the eight lines sit inside 0.04 of turnover of each other and need
    # real width before their names separate.
    axins = ax.inset_axes([0.455, 0.495, 0.545, 0.475])
    axins.axhline(0.0, color="0.55", lw=0.8, ls=":", zorder=1)
    axins.axvline(0.0, color="0.55", lw=0.8, ls=":", zorder=1)
    axins.plot(xf, slope * xf + intercept, color="0.45", lw=1.0, ls="--", zorder=2)
    _draw_points(axins, cluster, ms=4.5, ring=9)
    # ⚠ THE HEADROOM IS ASYMMETRIC, AND EVERY SIDE OF IT WAS SET BY A RENDERED FAILURE.
    # Right: the rightmost point is gpt-5.6-luna, the longest name in the cluster, and without extra
    # width its label ran off the inset's own edge and was clipped mid-word.
    # Bottom: the note sits down there (see below) and needs a clear band, or `_place_labels` fills
    # it and the two print through each other.
    # Top: kept small. The indicator rectangle on the main panel is drawn from the INSET'S LIMITS, so
    # any headroom also inflates the rectangle. At 0.52 the rectangle claimed to magnify a region
    # reaching y = 0.42 when the highest cluster point is 0.20, and it collided with the title.
    ins_rx = cx.max() - cx.min()
    ins_ry = cy.max() - cy.min()
    axins.set_xlim(cx.min() - 0.10 * ins_rx, cx.max() + 0.34 * ins_rx)
    # The bottom band is 0.55 of the range, not 0.34, because the note has to clear the ERROR BARS
    # and not merely the markers: sonnet-5's lower whisker reaches 0.03 below its point and grazed
    # the note text. `cy` holds point estimates, so any clearance computed from it under-reserves.
    axins.set_ylim(cy.min() - 0.55 * ins_ry, cy.max() + 0.16 * ins_ry)
    axins.tick_params(labelsize=10, length=2.5, pad=1.5)
    axins.grid(alpha=0.20)
    axins.set_facecolor("white")
    axins.patch.set_alpha(0.94)
    # The note goes INSIDE the inset, not in a title. As an axes title it printed immediately under
    # the figure's own title and read as a subtitle of the whole exhibit rather than a label on the
    # corner panel, which inverted its meaning: it appeared to say the FIGURE showed eight lines.
    # ⚠ BOTTOM-LEFT, NOT TOP-LEFT, AND THE MOVE IS WHAT FREED THE HARDEST LABEL. At the top the note
    # sat directly over the only isolated point in the cluster, haiku-4.5 at (-0.072, +0.196). Its
    # three upward slots were blocked by the note and its two sideways slots by its neighbours, so the
    # greedy placer pushed it to the bottom of the panel on a leader that crossed the entire inset --
    # the exact defect the inset was built to remove, reproduced inside the inset. The cluster's
    # bottom-left corner holds no point at all, so the note costs nothing there.
    ins_note = axins.text(0.02, 0.04, f"zoom: the crowded middle, {len(cluster)} of {len(pts)} lines",
                          transform=axins.transAxes, ha="left", va="bottom", fontsize=10,
                          color="0.35")
    for side in ("top", "right"):
        axins.spines[side].set_visible(False)
    # The rectangle and its two connectors are what make the inset a zoom rather than a second,
    # unexplained scatter. Without them a reader has no way to know the corner panel is a magnified
    # region of the panel it sits inside.
    ax.indicate_inset_zoom(axins, edgecolor="0.45", lw=0.8, alpha=0.9)

    _note_xlabel(
        ax,
        f"Change in {TURNOVER_UNIT}",
        "distributional minus scalar, paired on the seed index",
        "right = the treatment trades MORE",
    )
    ax.set_ylabel(_caption("Change in Sharpe (annualised, NET)"), fontsize=10)
    # The title carries the CLAIM only. It read "The measured mechanism: what the reward changes is
    # how heavily the policy trades", 79 characters, which at the 11 pt title size is about 466 pt
    # against a 453.6 pt canvas, so the last word was clipped off the page. The dropped label was
    # redundant in any case: the caption already opens "The mechanism, measured".
    ax.set_title("What the reward changes is how heavily the policy trades")
    handles = [
        plt.Line2D([], [], color=OKABE_ITO["blue"], marker="o", ls="", ms=5,
                   label="one authoring line"),
        plt.Line2D([], [], color="none", marker="o", ls="", ms=10, mfc="none", mec="0.20", mew=1.1,
                   label="the registered node"),
        plt.Line2D([], [], color="0.45", ls="--", lw=1.0,
                   label=f"fitted slope {slope:+.2f}"),
    ]
    leg = _outside_legend(fig, handles, [h.get_label() for h in handles], ncol=3)

    # ⛔ THE POINTS CARRY THEIR OWN NAMES NOW. THE NUMBERED KEY IS GONE, AND SO IS THE STATS BOX.
    # Two devices used to sit on this panel and both cost the reader more than they gave. A key of
    # eleven numbers made the figure a lookup exercise: to learn which model traded most you read a
    # digit off the scatter, found it in a four-column list underneath, and came back. And a white
    # statistics box sat inside the axes, over the fitted line, restating two numbers the caption
    # already carries. Direct labels remove both. `_place_labels` searches eight directions at five
    # radii per point and draws a leader, so a name never lands on a marker, on another name or on
    # the fit. The Spearman statistic belongs in the caption, which is word-excluded and read anyway.
    # ⭐ EACH NAME IS PLACED ON THE PANEL THAT CAN HOLD IT. All eleven used to be placed on the main
    # axes, where eight of them competed for the same tenth of the canvas. Now the three lines that
    # set the range are named where they sit, with short offsets and room around them, and the other
    # eight are named inside the zoom, which has the same eight points spread over the full width of
    # a corner panel. No name travels more than a few millimetres from its point in either panel, so
    # the reader never has to trace a leader across the figure to answer "which model is that".
    xline = np.linspace(*ax.get_xlim(), 200)
    _place_labels(ax, [(p[1], p[4], p[0]) for p in outer],
                  avoid=[axins], avoid_curves=[(xline, slope * xline + intercept)],
                  colors=["0.25"] * len(outer), fontsize=10)
    # ⚠ TOP-DOWN ORDER, NOT ROSTER ORDER, AND IT IS NOT COSMETIC. `_place_labels` is greedy: it takes
    # the first non-colliding slot per point, in the order it is handed them. Handed the cluster in
    # roster order it reached haiku-4.5 last, by which time its neighbours had taken every near slot
    # around it, and pushed the name to the foot of the inset on a leader crossing the whole panel.
    # Sorting by descending y hands the topmost point its own top slot first, and each subsequent
    # point is placed against a frontier that is already above it rather than around it. Deterministic
    # either way; this order is simply the one that leaves no long leaders.
    xins = np.linspace(*axins.get_xlim(), 200)
    _place_labels(axins, [(p[1], p[4], p[0]) for p in sorted(cluster, key=lambda p: -p[4])],
                  avoid=[ins_note], avoid_curves=[(xins, slope * xins + intercept)],
                  colors=["0.25"] * len(cluster), fontsize=10)
    _LOG.info("turnover mechanism: Spearman rho=%+.3f p=%.2e slope=%+.3f", rho, pval, slope)
    return fig


# --------------------------------------------------------------------------- #
# (g) The ablation that names the mechanism: the same arms, gross and net       #
# --------------------------------------------------------------------------- #
def fig_gross_vs_net(store: dict[str, np.ndarray]) -> Any:
    """The five arms' median terminal Sharpe on every line, drawn twice: before costs and after.

    This is the exhibit that answers "why does the placebo arm win where it wins?". Removing the
    transaction cost is a one-variable ablation that needs no retraining, because the environment
    charges cost after the action, so the gross series is already in the archive. If the reward
    designs differed in what they DISCOVER, the gross panel would separate them. It does not: the
    median between-arm spread is roughly five times wider after costs than before, on every line.

    ⚠ Both panels share one x-axis deliberately. Letting each panel autoscale would make two very
    different spreads look identical, which is the exact opposite of what the figure is for.
    """
    import matplotlib.pyplot as plt

    from src.viz.style import arm_style

    med = {(l, a, f): float(np.median(get(store, l, a, f)))
           for l in LINE_LABELS for a in ARMS for f in ("sharpe_gross", "sharpe_net")}
    spread = {f: [max(med[(l, a, f)] for a in ARMS) - min(med[(l, a, f)] for a in ARMS)
                  for l in LINE_LABELS] for f in ("sharpe_gross", "sharpe_net")}
    # order the rows by how much the costs cost them, worst at the bottom
    order = sorted(LINE_LABELS, key=lambda l: -(spread["sharpe_net"][LINE_LABELS.index(l)]))

    # ⛔ ONE PANEL, TWO SUB-ROWS PER LINE. THIS REPLACES A SIDE-BY-SIDE PAIR THAT WAS UNREADABLE.
    # The old layout drew gross in a left panel and net in a right one, both on a shared x-axis so
    # the widths stayed comparable. Sharing the axis is right and it is why the pairing was kept, but
    # the consequence on the page was that the GROSS panel became a smear: every arm of every line
    # sits inside 0.07 Sharpe, the shared axis spans 1.7, and so all five markers of all eleven lines
    # printed on top of one another against six tenths of empty panel. The reader saw a column of
    # blobs, not a result.
    # Stacking the two conditions as sub-rows of ONE row keeps the shared scale, doubles the width
    # available to each, and puts the comparison where the eye already is: a short bar directly above
    # a long one, eleven times. The piling of the gross markers is then the FINDING rather than a
    # rendering failure, because it sits two millimetres above the net row that fans out.
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_IN, 5.3))
    lo = min(med.values()) - 0.10
    hi = max(med.values()) + 0.12
    dy = 0.19
    for y, line in enumerate(order):
        if y % 2 == 0:
            ax.axhspan(y - 0.5, y + 0.5, color="0.955", zorder=0)
        # ⛔⛔ THE OFFSETS WERE INVERTED AND THE LEGEND THEREFORE NAMED THE WRONG CONDITION.
        # `set_ylim(len-0.5, -0.5)` puts the origin at the TOP and makes y increase DOWNWARD, so the
        # old `sharpe_gross` at `+dy` rendered BELOW its row and `sharpe_net` at `-dy` rendered ABOVE
        # it, while the legend read "upper bar: spread GROSS / lower bar: spread NET". Every one of
        # the eleven rows was labelled backwards, in the one exhibit whose whole job is to separate
        # before-cost from after-cost. It is visible in the rendered figure once you know to look:
        # qwen3.5-9b's UPPER bar runs from -0.28 to 1.23, and a spread that wide is what costs DO to
        # a line, not what it looked like before them. Signs against an inverted axis are exactly the
        # silent error a code read misses and a rendered read catches.
        # The offsets are now negative-for-gross, so the row reads top-to-bottom as before, then
        # after, which is also the order the caption and the sentence in the body use.
        for field, off, colour, lw, size in (("sharpe_gross", -dy, "0.55", 1.8, 4.6),
                                             ("sharpe_net", +dy, "0.15", 3.6, 5.8)):
            vals = [med[(line, a, field)] for a in ARMS]
            # alpha 0.80, not 0.55. The two bars are distinguished by lightness and by weight, and at
            # 0.55 both washed towards the same mid grey against the 0.955 row stripe, which is what
            # made them read as one repeated object rather than two conditions.
            ax.plot([min(vals), max(vals)], [y + off] * 2, color=colour, lw=lw,
                    solid_capstyle="round", alpha=0.80, zorder=1)
            for a in ARMS:
                st = arm_style(a)
                ax.plot([med[(line, a, field)]], [y + off], marker=st["marker"], ms=size,
                        color=st["color"], mec="white", mew=0.5, zorder=3)
    ax.set_xlim(lo, hi)
    ax.set_ylim(len(order) - 0.5, -0.5)
    ax.set_yticks(np.arange(len(order)))
    ax.set_yticklabels(order)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", alpha=0.25)
    _note_xlabel(ax, "Median terminal Sharpe ratio over 102 sealed seeds (annualised)")
    # ⛔ THE BOLD ROW LABEL FOR THE REGISTERED NODE IS GONE, ON THE STANDING RULE (Tamer,
    # 2026-08-08): "Opus keeps no special status anywhere -- not in the abstract, not in CH5's
    # ordering, not in a figure's highlighting, not in a table's row order." This figure's rows are
    # ordered by how much cost took from each line, so nothing here depends on which line is which,
    # and the registration is disclosed where it belongs, in Chapter 4 and in the caption of the two
    # figures that actually show a per-line contrast.
    # The two sub-rows are named in the legend rather than on the canvas. An in-canvas label has to
    # anchor somewhere, and every anchor tried collided with something: attached to the top row's
    # leftmost marker it sat on the y tick label, attached to its rightmost it sat on the bar.

    g, n = float(np.median(spread["sharpe_gross"])), float(np.median(spread["sharpe_net"]))
    wider = sum(1 for a, b in zip(spread["sharpe_net"], spread["sharpe_gross"]) if a > b)
    _LOG.info("gross-vs-net: median spread %.3f gross, %.3f net, factor %.1f; net wider on %d of %d",
              g, n, n / g, wider, len(LINE_LABELS))
    ax.set_title("Costs create the separation, not the reward designs", fontsize=11.5)
    # ⚠ THE ARITHMETIC BELONGS IN THE CAPTION, NOT ON THE CANVAS. A fig.text placed at a fixed
    # figure coordinate cannot see the legend that constrained layout is still positioning, and the
    # first render put the two on top of each other. The caption is word-excluded and can hold the
    # numbers safely, so the figure keeps only what has to be seen next to the marks.
    handles = [plt.Line2D([], [], ls="", marker=arm_style(a)["marker"], ms=5.5,
                          color=arm_style(a)["color"], label=_arm_label(a)) for a in ARMS]
    handles += [plt.Line2D([], [], color="0.55", lw=1.8, alpha=0.80, solid_capstyle="round",
                           label="upper, thin bar: GROSS of costs"),
                plt.Line2D([], [], color="0.15", lw=3.6, alpha=0.80, solid_capstyle="round",
                           label="lower, thick bar: NET of costs")]
    fig.legend(handles=handles, loc="outside lower center", ncol=3, fontsize=10, frameon=False)
    return fig


# --------------------------------------------------------------------------- #
# (h) The money, and the loss a holder would have lived through                 #
# --------------------------------------------------------------------------- #
def fig_wealth_and_drawdown(store: dict[str, np.ndarray]) -> Any:
    """What a pound did over the sealed window, and how far it fell from its own peak on the way.

    ⭐ WHY THIS EXHIBIT EXISTS, IN THE SUPERVISOR'S OWN WORDS. *"Relying solely on an end-of-period
    Sharpe ratio is fundamentally misleading. A model could achieve a final Sharpe of 1.0+ while
    having gone severely negative mid-period, only recovering later. From a risk management
    perspective such a trajectory is dangerous, yet the single terminal number masks that volatility
    entirely."* Every other exhibit in this chapter reports a functional of the path. This one draws
    the path, in the units a person actually holds, and then draws the thing a terminal statistic
    hides most completely: the worst moment.

    The two panels share one time axis on purpose. A drawdown is only interpretable against the
    wealth path that produced it, and reading them apart invites the reader to date one from the
    other by eye.
    """
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from src.viz.style import arm_style

    dates = _test_dates()
    x = dates if dates is not None else np.arange(TEST_N_SESSIONS)

    fig, axes = plt.subplots(2, 1, figsize=(FIG_WIDTH_IN, 6.00), sharex=True,
                             height_ratios=(1.55, 1.0))
    for arm in ARMS:
        st = arm_style(arm)
        # Every line is drawn faintly and the cross-line median heavily, so the reader sees both the
        # spread across authors and the central path without eleven legends.
        eq = np.array([get(store, lb, arm, "equity") for lb in LINE_LABELS])
        dd = np.array([get(store, lb, arm, "drawdown") for lb in LINE_LABELS])
        for row in eq:
            axes[0].plot(x, row, color=st["color"], lw=0.4, alpha=0.20, zorder=1)
        axes[0].plot(x, np.median(eq, axis=0), color=st["color"], lw=1.7, zorder=3,
                     label=_arm_label(arm))
        # ⚠ THE PER-LINE DRAWDOWN PATHS ARE DRAWN, AND UNTIL 2026-08-12 THEY WERE NOT. The lower
        # panel carried the five cross-line MEDIANS only, so its axis stopped near -22 per cent
        # while the caption's sharpest sentence -- "the worst single line under the tail-fed
        # condition falls 48.2 per cent from its peak" -- described something the reader could not
        # see anywhere on the page. A caption that states a number its own exhibit contradicts is a
        # worse defect than a missing number, because the reader who checks finds a disagreement.
        # Drawing the eleven faint paths behind each median makes the claim visible and costs
        # nothing: it is the same treatment the wealth panel already gives, and it is what O2 asks
        # for, the object behind the summary.
        for row in dd:
            axes[1].plot(x, row, color=st["color"], lw=0.35, alpha=0.16, zorder=1)
        axes[1].plot(x, np.median(dd, axis=0), color=st["color"], lw=1.4, zorder=3)

    axes[0].axhline(1.0, color="0.35", lw=0.9, ls="--", zorder=2)
    # Log wealth, because a doubling should look the same wherever it happens. The minor ticks are
    # silenced explicitly: matplotlib labels a decade boundary it considers under-populated, and it
    # printed "6 x 10^-1" under the axis floor, which is a decade marker and not a wealth anyone holds.
    from matplotlib.ticker import NullFormatter, NullLocator
    axes[0].set_yscale("log")
    axes[0].set_ylim(0.62, 3.25)
    axes[0].set_yticks([0.75, 1.0, 1.5, 2.0, 3.0])
    axes[0].set_yticklabels(["0.75", "1.00", "1.50", "2.00", "3.00"])
    axes[0].yaxis.set_minor_locator(NullLocator())
    axes[0].yaxis.set_minor_formatter(NullFormatter())
    axes[0].set_ylabel(_caption("Wealth from 1.00 invested", "(NET of costs, log scale)"))
    axes[0].set_title("What one pound did, and the worst it felt on the way", fontsize=11, loc="left")

    axes[1].axhline(0.0, color="0.35", lw=0.9, zorder=2)
    axes[1].set_ylabel(_caption("Fall from the", "running peak"))
    axes[1].yaxis.set_major_formatter(lambda v, _p: f"{v:.0%}")
    if dates is not None:
        axes[1].xaxis.set_major_locator(mdates.YearLocator())
        axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axes[1].set_xlabel("Sealed test window, 2020-03-30 to 2026-06-30")

    handles, labels = axes[0].get_legend_handles_labels()
    # ⛔ THE FAINT PATHS WERE UNEXPLAINED, AND THEY ARE MOST OF THE INK. Each panel carries 55 pale
    # lines (eleven authoring lines x five arms) behind five heavy ones, and the legend named only the
    # five. So the single most striking feature of the exhibit -- a wide haze reaching down to 0.72
    # and to -48 per cent while the heavy lines sit in a tight band -- had no key anywhere, and a
    # reader could not tell whether the pale lines were seeds, lines, arms or a confidence band. Two
    # keys fix it. They are drawn at alpha 1.0 rather than the canvas 0.20 because a 10 pt swatch at
    # 0.20 is invisible: the key identifies the object, it does not sample its colour.
    handles += [plt.Line2D([], [], color="0.35", lw=0.9, label="one authoring line, 11 per arm"),
                plt.Line2D([], [], color="0.15", lw=1.7, label="the median across those 11")]
    labels = [h.get_label() for h in handles]
    _outside_legend(fig, handles, labels, ncol=3)
    worst = {a: float(np.min([get(store, lb, a, "drawdown").min() for lb in LINE_LABELS]))
             for a in ARMS}
    _LOG.info("worst median drawdown by arm: %s",
              ", ".join(f"{a} {v:.1%}" for a, v in sorted(worst.items(), key=lambda kv: kv[1])))
    return fig


# --------------------------------------------------------------------------- #
# Render-all                                                                    #
# --------------------------------------------------------------------------- #
#: (file stem, builder) in manifest order.
FIGURES: tuple[tuple[str, Any], ...] = (
    ("F5_cross_line_forest", fig_cross_line_forest),
    ("F5_seed_dispersion", fig_seed_dispersion),
    ("F5_dispersion_all_lines", fig_dispersion_all_lines),
    ("F5_capability_gradient", fig_capability_gradient),
    ("F5_sharpe_trajectory", fig_sharpe_trajectory),
    ("F5_seed_trajectory", fig_seed_trajectory),
    ("F5_turnover_mechanism", fig_turnover_mechanism),
    ("F5_gross_vs_net", fig_gross_vs_net),
    ("F5_wealth_drawdown", fig_wealth_and_drawdown),
)


def render_all(store: dict[str, np.ndarray], only: Sequence[str] | None = None) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from docs.analysis.figure_typeface import use_document_typeface
    from src.viz.style import apply_house_style

    apply_house_style()
    use_document_typeface()   # the body typeface, so the exhibit matches the page it sits on

    # ⚠ THE HOUSE STYLE SETS EVERY DEFAULT TYPE SIZE BELOW THE GUIDELINE FLOOR, AND IT IS FENCED.
    # src/viz/style.py::apply_house_style sets font.size 9, axes.labelsize 9, legend.fontsize 8,
    # xtick.labelsize 8 and ytick.labelsize 8. IFTE0008 asks for "a font size of no less than 10"
    # and requires diagrams to be legible, so every one of those defaults ships under the floor.
    # src/** is drift-fenced to the ops lane, so the module cannot be corrected there; the override
    # lands here instead, immediately after the call, which is the only place it can.
    # MEASURED before this override (2026-08-11, on the vector twins): the smallest rendered type in
    # the seven results figures ran 6.0 to 7.0 pt on the page.
    # !! DO NOT "SIMPLIFY" THIS BY DELETING apply_house_style ABOVE. That call also sets the
    # colourblind-safe palette, the vector-safe font embedding and the constrained layout, all of
    # which are wanted. Only the sizes are overridden.
    matplotlib.rcParams.update({
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.titlesize": 12,
        # !! AND THE CROP MUST BE TURNED OFF HERE, NOT AT THE CALL SITE. apply_house_style sets
        # "savefig.bbox": "tight" (src/viz/style.py:72). matplotlib treats savefig's own
        # bbox_inches=None as "unspecified, fall back to rcParams", so passing None does NOT disable
        # cropping -- measured 2026-08-11, the pages stayed 8.4 pt over the text width, which is
        # exactly the crop pad, and the 10 pt type still rendered at 9.3-9.8 pt. Only clearing the
        # rcParam actually turns it off.
        "savefig.bbox": None,
    })

    written: list[Path] = []
    for stem, builder in FIGURES:
        if only and stem not in only:
            continue
        fig = builder(store)
        written += _save(fig, stem)
        plt.close(fig)
    return written


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #
def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rebuild", action="store_true", help="re-read the sealed archive, ignoring the cache")
    ap.add_argument("--cache-only", action="store_true", help="build/refresh the cache and stop")
    ap.add_argument("--only", nargs="*", default=None, help="render only these file stems")
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    store = load_cache(rebuild=args.rebuild)
    if args.cache_only:
        n_cells = sum(1 for _ in cells(store))
        _LOG.info("cache ready: %d cells x n=%d seeds", n_cells, N_SEEDS)
        return 0

    written = render_all(store, only=args.only)
    _LOG.info("%d files written to %s", len(written), FIG_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
