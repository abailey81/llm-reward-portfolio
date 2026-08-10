"""Archive reader for the preliminary-results notebook.

ONE pass over the campaign archive that extracts every quantity the notebook reports, so the
notebook itself contains analysis rather than plumbing. Records are read through
``src.io.results.load_all`` (the only sanctioned reader, which validates each record); nothing here
parses a run file ad hoc.

Two products, both cached to disk because a full validating read takes several minutes:

* ``rows``   -- one dict per test record, roughly forty derived scalars (performance, risk, tail,
  cost, turnover, concentration, learning, safety, compute).
* ``series`` -- per ``(line, arm)`` and restricted to the common floor seeds, the mean cumulative
  equity curve, the mean per-day turnover, the mean training curve, and the pooled daily returns
  used for distribution exhibits.

CONVENTIONS, verified against the archive rather than assumed (2026-08-07):

* ``test_sharpe`` in a record equals ``mean / std(ddof=0) * sqrt(252)``. Reproduced here as
  ``sharpe_recomputed`` so any divergence is visible instead of silent.
* ``test_cvar05`` equals the empirical mean of the worst five per cent of DAILY returns.
* ``test_returns``, ``per_period_pnl`` and ``metrics.test_returns`` are three copies of one series.
* ``test_gross`` is the same series BEFORE transaction costs, so ``gross - net`` is the cost drag.

⚠ The six tail statistics computed here are the same FORMULAS as the frozen fed vector
(``src/feedback/measurement.py``: ``left_tail_mass = mean(r < -2*std)``, ``robust_skew`` =
Groeneveld-Meeden gamma(0.05)) but they are NOT the fed vector. The fed vector is measured
in-sample on training returns during the search and routes CVaR-5% through an EVT fit. These are
descriptive, empirical, and computed on the sealed test window. Naming them the same thing would
be a category error, so every key here carries the ``oos_`` prefix.
"""
from __future__ import annotations

import json
import pathlib
import time
from typing import Any

import numpy as np

TRADING_DAYS = 252
LEFT_TAIL_K = 2.0          # mirrors measurement.LEFT_TAIL_K


def _banked_rung(default: int = 30) -> int:
    """The registered ladder tier every (line, arm) has COMPLETELY banked, read LIVE.

    This was a hardcoded ``30`` until 2026-08-10, which silently pinned every notebook product to
    the rung-30 floor months after the campaign had climbed past it: ``series`` aggregates dropped
    every seed >= 30, and the notebook's own ``D["floor"]`` mirrored the same constant. Reading it
    live means the presentation follows the ladder instead of freezing at whatever rung happened to
    be current when the file was written.

    ⚠ THE LADDER TIER, NOT THE CONTIGUOUS DEPTH. ``achieved_rung.json`` records both, and its own
    note is explicit: the depth (102 on 2026-08-09) is NOT a member of the frozen ladder
    [30,100,189,279,340,403,568], so quoting it "would claim a ladder tier the study has not
    reached". Paired contrasts may only use seeds present in EVERY arm, so the registered tier is
    the honest floor.

    ⚠ FAILS SAFE. A missing, unreadable or malformed file returns the pre-2026-08-10 constant
    rather than a guess, exactly as ``LINE_DURATION.json``'s reader does for the duration lever.
    """
    try:
        here = pathlib.Path(__file__).resolve()
        repo = next(p for p in here.parents if (p / "outputs").is_dir())
        blob = json.loads((repo / "outputs" / "tables" / "achieved_rung.json")
                          .read_text(encoding="utf-8"))
        rung = int(blob["achieved_rung"])
        return rung if rung > 0 else default
    except Exception:                      # noqa: BLE001 - a presentation must never fail to load
        return default


#: The common floor rung; ``series`` products are restricted to seeds < this. Re-derived on import.
FLOOR_SEEDS = _banked_rung()


# --------------------------------------------------------------------------- derived quantities
def _max_drawdown(equity: np.ndarray) -> float:
    """Most negative peak-to-trough fraction of a cumulative wealth path. Returned NEGATIVE."""
    peak = np.maximum.accumulate(equity)
    return float(np.min(equity / peak - 1.0))


def _tail_block(r: np.ndarray) -> dict[str, float]:
    """The six frozen tail formulas, computed EMPIRICALLY on out-of-sample returns."""
    out: dict[str, float] = {}
    for lvl in (0.01, 0.05, 0.10, 0.25):
        q = float(np.quantile(r, lvl))
        tail = r[r <= q]
        out["oos_cvar_%02d" % int(lvl * 100)] = float(tail.mean()) if tail.size else float("nan")
        out["oos_var_%02d" % int(lvl * 100)] = q
    sd = float(r.std())
    out["oos_left_tail_mass"] = float(np.mean(r < -LEFT_TAIL_K * sd))
    q05, q50, q95 = (float(np.quantile(r, t)) for t in (0.05, 0.50, 0.95))
    out["oos_robust_skew"] = ((q95 - q50) - (q50 - q05)) / ((q95 - q05) + 1e-12)
    return out


def derive(rec: dict[str, Any]) -> dict[str, Any]:
    """Every scalar the notebook reports, from one validated record."""
    m = rec.get("metrics", {})
    r = np.asarray(m.get("test_returns") or rec.get("test_returns") or [], dtype=float)
    r = r[np.isfinite(r)]
    row: dict[str, Any] = {
        "arm": rec["arm"], "seed": int(rec["seed"]), "run_id": rec.get("run_id", ""),
        "candidate_id": rec.get("candidate_id", ""), "generation": rec.get("generation"),
        "sharpe": m.get("test_sharpe"), "cvar05_recorded": m.get("test_cvar05"),
        "val_fitness": m.get("val_fitness"), "wall_clock": rec.get("wall_clock"),
        "device": m.get("device"), "n_days": int(r.size),
        "reward_hash": (rec.get("reward_source_hash") or "")[:12],
        "reward_chars": len(rec.get("reward_source") or ""),
    }
    if r.size < 10:
        return row

    sd = float(r.std())                                   # ddof=0, matching the recorded Sharpe
    mean = float(r.mean())
    row["mean_daily"] = mean
    row["sd_daily"] = sd
    row["sharpe_recomputed"] = mean / sd * np.sqrt(TRADING_DAYS) if sd > 0 else float("nan")
    row["ann_return"] = mean * TRADING_DAYS
    row["ann_vol"] = sd * np.sqrt(TRADING_DAYS)

    equity = np.cumprod(1.0 + r)
    row["total_return"] = float(equity[-1] - 1.0)
    row["max_drawdown"] = _max_drawdown(equity)
    row["calmar"] = row["ann_return"] / abs(row["max_drawdown"]) if row["max_drawdown"] < 0 else float("nan")

    downside = r[r < 0.0]
    dd = float(np.sqrt(np.mean(downside ** 2))) if downside.size else 0.0
    row["downside_dev"] = dd * np.sqrt(TRADING_DAYS)
    row["sortino"] = mean * TRADING_DAYS / row["downside_dev"] if dd > 0 else float("nan")

    c = r - mean
    row["skew"] = float(np.mean(c ** 3) / sd ** 3) if sd > 0 else float("nan")
    row["kurtosis"] = float(np.mean(c ** 4) / sd ** 4) if sd > 0 else float("nan")
    row["hit_rate"] = float(np.mean(r > 0.0))
    row["worst_day"] = float(r.min())
    row["best_day"] = float(r.max())
    row.update(_tail_block(r))

    g = np.asarray(m.get("test_gross") or [], dtype=float)
    if g.size == r.size:
        row["mean_gross"] = float(g.mean())
        row["cost_drag"] = float(g.mean() - mean)
        row["cost_share_of_gross"] = float((g.mean() - mean) / g.mean()) if g.mean() != 0 else float("nan")
        gsd = float(g.std())
        row["sharpe_gross"] = float(g.mean() / gsd * np.sqrt(TRADING_DAYS)) if gsd > 0 else float("nan")

    t = np.asarray(m.get("test_turnover") or [], dtype=float)
    if t.size:
        row["turnover_mean"] = float(t.mean())
        row["turnover_median"] = float(np.median(t))
        row["turnover_max"] = float(t.max())

    exp = m.get("test_exposure") or {}
    for k in ("hhi", "eff_n", "max_weight", "top5"):
        v = np.asarray(exp.get(k) or [], dtype=float)
        if v.size:
            row["exp_%s" % k] = float(np.nanmean(v))

    for k, v in (m.get("test_components") or {}).items():
        if isinstance(v, (int, float)):
            row["comp_%s" % k] = float(v)

    pa = m.get("popart_scale") or {}
    for k in ("popart", "sigma_last", "sigma_max", "raw_rms_last", "raw_rms_max"):
        if isinstance(pa.get(k), (int, float)):
            row["popart_%s" % k] = float(pa[k])

    calls = m.get("train_safe_call_count") or 0
    defaults = m.get("train_safe_default_count") or 0
    row["safe_calls"] = int(calls)
    row["safe_defaults"] = int(defaults)
    row["safe_default_rate"] = float(defaults) / float(calls) if calls else float("nan")

    tc = m.get("train_curve") or {}
    tr = np.asarray(tc.get("return") or [], dtype=float)
    if tr.size:
        row["train_return_final"] = float(tr[-1])
        row["train_return_max"] = float(np.nanmax(tr))
        row["train_curve_pts"] = int(tr.size)
    for k in ("actor_loss", "critic_loss", "ent_coef"):
        v = np.asarray(tc.get(k) or [], dtype=float)
        if v.size:
            row["train_%s_final" % k] = float(v[-1])
    return row


# --------------------------------------------------------------------------- the archive pass
def build(archive: pathlib.Path, cache_dir: pathlib.Path, *, verbose: bool = True) -> tuple[list[dict], dict]:
    """Read every test record once. Returns (rows, series) and writes both caches."""
    import sys
    repo = archive.parents[1]
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from src.io.results import load_all

    t0 = time.time()
    rows: list[dict] = []
    acc: dict[str, dict[str, Any]] = {}

    lines = sorted(p for p in archive.iterdir() if p.is_dir() and p.name.startswith("test"))
    for li, line_dir in enumerate(lines, 1):
        for arm_dir in sorted(p for p in line_dir.iterdir() if p.is_dir()):
            key = "%s|%s" % (line_dir.name, arm_dir.name)
            for rec in load_all(arm_dir):
                row = derive(rec)
                row["line"] = line_dir.name
                rows.append(row)
                if row["seed"] >= FLOOR_SEEDS or row["n_days"] < 10:
                    continue
                m = rec.get("metrics", {})
                r = np.asarray(m.get("test_returns") or [], dtype=float)
                a = acc.setdefault(key, {"n": 0, "eq": None, "turn": None, "train": None, "pool": []})
                eq = np.cumprod(1.0 + r)
                a["eq"] = eq if a["eq"] is None else a["eq"] + eq
                t = np.asarray(m.get("test_turnover") or [], dtype=float)
                if t.size == r.size:
                    a["turn"] = t if a["turn"] is None else a["turn"] + t
                tc = np.asarray((m.get("train_curve") or {}).get("return") or [], dtype=float)
                if tc.size:
                    if a["train"] is None or a["train"].size == tc.size:
                        a["train"] = tc if a["train"] is None else a["train"] + tc
                # train_curve["return"] is NaN in EVERY record (verified 2026-08-07 across six
                # arms): the rollout return was never captured. The loss curves ARE populated, so
                # learning dynamics are shown through those and the gap is reported, not papered over.
                for name in ("critic_loss", "actor_loss", "ent_coef"):
                    v = np.asarray((m.get("train_curve") or {}).get(name) or [], dtype=float)
                    if not v.size:
                        continue
                    slot = "tc_" + name
                    if a.get(slot) is None:
                        a[slot] = v.copy()
                        a[slot + "_n"] = 1
                    elif a[slot].size == v.size:
                        a[slot] += v
                        a[slot + "_n"] += 1
                a["pool"].append(r.astype(np.float32))
                a["n"] += 1
        if verbose:
            print("  [%2d/%2d] %-30s rows=%d  %.0fs" % (li, len(lines), line_dir.name, len(rows), time.time() - t0))

    series: dict[str, Any] = {}
    for key, a in acc.items():
        if not a["n"]:
            continue
        series[key] = {
            "n_seeds": a["n"],
            "equity_mean": (a["eq"] / a["n"]).astype(np.float32),
            "turnover_mean": (a["turn"] / a["n"]).astype(np.float32) if a["turn"] is not None else None,
            "pooled_returns": np.concatenate(a["pool"]).astype(np.float32),
        }
        for name in ("critic_loss", "actor_loss", "ent_coef"):
            slot = "tc_" + name
            if a.get(slot) is not None and a.get(slot + "_n"):
                series[key][slot] = (a[slot] / a[slot + "_n"]).astype(np.float32)

    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "rows.json").write_text(json.dumps(rows), encoding="utf-8")
    flat: dict[str, np.ndarray] = {}
    for key, s in series.items():
        for field in ("equity_mean", "turnover_mean", "pooled_returns",
                      "tc_critic_loss", "tc_actor_loss", "tc_ent_coef"):
            if s.get(field) is not None:
                flat["%s@@%s" % (key, field)] = s[field]
        flat["%s@@n_seeds" % key] = np.asarray([s["n_seeds"]], dtype=np.int32)
    np.savez_compressed(cache_dir / "series.npz", **flat)
    if verbose:
        print("wrote %d rows and %d series cells in %.0f s" % (len(rows), len(series), time.time() - t0))
    return rows, series


def load(archive: pathlib.Path, cache_dir: pathlib.Path, *, force: bool = False,
         verbose: bool = True) -> tuple[list[dict], dict]:
    """Cached :func:`build`. Reports what it did rather than loading silently."""
    rj, sn = cache_dir / "rows.json", cache_dir / "series.npz"
    if rj.exists() and sn.exists() and not force:
        rows = json.loads(rj.read_text(encoding="utf-8"))
        z = np.load(sn, allow_pickle=False)
        series: dict[str, Any] = {}
        for name in z.files:
            key, field = name.split("@@")
            series.setdefault(key, {})[field] = z[name]
        for key, s in series.items():
            s["n_seeds"] = int(s["n_seeds"][0]) if "n_seeds" in s else 0
        if verbose:
            print("loaded from CACHE: %d rows, %d series cells" % (len(rows), len(series)))
            print("   -> pass force=True to re-read the live archive")
        return rows, series
    return build(archive, cache_dir, verbose=verbose)
