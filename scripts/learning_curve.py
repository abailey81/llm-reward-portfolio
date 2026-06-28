"""Training-budget learning curve — choose the per-candidate step budget at the PLATEAU (under-training gate).

Why this exists
---------------
The campaign trains the fixed SB3-SAC for a per-candidate step budget that is *pre-registered* (audit
B-5): every arm gets the SAME budget, so the budget must be large enough that the agent has CONVERGED
on a representative reward — otherwise the headline H2 contrast measures *under-training noise*, not the
reward. The prototype budget (25k) was set from Phase-0 *timing* (minutes/run), never from a *convergence*
curve, and the prototype showed late-training critic explosions — so the budget was an unvalidated guess.

This tool produces the missing evidence: it trains the FIXED, explosion-fixed agent (PopArt
scale-normalization + the gated ``learning_starts``; src/agents/trainer.py) on a representative reward at a
ladder of budgets and records, for each, the held-out (validation) return and the critic-loss trajectory.
The operator reads the curve and sets the campaign budget at the knee — the smallest budget past which the
eval return has plateaued and the critic loss is flat/finite. It does **not** change any frozen config; it
INFORMS the (amendment-gated) choice of ``train_steps_per_candidate``.

What it is NOT
--------------
* Not a result that enters the dissertation — it is an engineering/convergence diagnostic on the MACHINERY
  (like ``scripts/smoke_test.py``), reported to justify the budget.
* Not the full study. Each 200k-step training is GPU-minutes and the four-budget ladder at several seeds is
  GPU-HOURS — this script BUILDS + smoke-tests the harness; the **operator runs the real ladder** on the
  campaign GPU (see ``--budgets`` / ``--seeds`` and the printed command in the dissertation notes).

Representative reward
---------------------
Default ``differential_sharpe`` (Moody-Saffell online Sharpe; ``src/baselines/rewards.py``) — a real
risk-adjusted, STATEFUL reward of the family the LLM authors, well-conditioned (no variance-floor blow-up),
so the curve reflects genuine optimisation progress rather than a degenerate target. Override with
``--reward <REWARD_CANON key>``.

Outputs (``--out-dir``, default ``outputs/tables``)
---------------------------------------------------
* ``learning_curve.json`` — per-(budget, seed) eval-IQM return, terminal + max critic loss, the subsampled
  critic-loss trajectory, and wall-clock; plus the per-budget seed-IQM summary.
* ``learning_curve.md``   — a human-readable table (budget | eval IQM | terminal critic | max critic | minutes).
* ``learning_curve.png``  — two stacked panels (eval-return vs budget; critic-loss-vs-step per budget) — the
  PLATEAU plot. Skipped automatically if matplotlib is unavailable or ``--no-plot``.

Flags
-----
  --budgets       Comma list of step budgets (default ``25000,50000,100000,200000``).
  --seeds         Comma list of seeds to average per budget (default ``0``; the campaign uses more).
  --reward        REWARD_CANON key for the representative reward (default ``differential_sharpe``).
  --synthetic     Use a synthetic panel instead of the real gold dev slice (default real).
  --end           Real-data slice end date (default ``2014-12-31`` — the dev TRAIN end).
  --device        ``cpu`` | ``cuda`` | ``auto`` (default ``auto``).
  --out-dir       Output directory (default ``outputs/tables``).
  --no-plot       Skip the PNG (still writes json + md).
  --smoke         Tiny-budget self-test ({200,400}, synthetic, cpu, no plot) — the unit-test mode; NOT a curve.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

__all__ = ["build_parser", "run_one_budget", "run_curve", "recommend_budget", "main"]


def recommend_budget(
    summary: list[dict[str, Any]],
    *,
    plateau_rel_tol: float = 0.03,
    min_budgets: int = 3,
) -> dict[str, Any]:
    """Objective convergence-knee detector over the (budget -> eval-IQM) curve (pre-registerable criterion).

    Removes the eyeballing: given the per-budget seed-median held-out eval IQM, returns the smallest budget
    past which the eval return is FLAT (within ``plateau_rel_tol`` of the curve's range) all the way to the
    ladder ceiling AND the critic loss is finite — the pre-registered ``train_steps_per_candidate`` knee.
    Critically, it reports ``converged=False`` (with a loud reason) when the eval is STILL RISING at the
    ceiling, so the operator knows to EXTEND ``--budgets`` higher rather than freeze an under-trained budget.

    Returns ``{recommended_budget, converged, reason, plateau_eval, budgets, evals}``. ``converged`` is
    ``None`` when there are too few usable budgets to judge. This is a diagnostic on the MACHINERY (no number
    enters the dissertation); it INFORMS the amendment-gated budget choice.
    """
    rows = [
        r for r in summary
        if r.get("eval_iqm_over_seeds") is not None
        and np.isfinite(float(r["eval_iqm_over_seeds"]))
        and int(r.get("n_ok", 0)) > 0
    ]
    rows = sorted(rows, key=lambda r: int(r["budget"]))
    budgets = [int(r["budget"]) for r in rows]
    evals = np.asarray([float(r["eval_iqm_over_seeds"]) for r in rows], dtype=float)
    finite = [bool(r.get("critic_finite_all", False)) for r in rows]
    base = {"budgets": budgets, "evals": [float(x) for x in evals]}

    if len(rows) < int(min_budgets):
        return {"recommended_budget": None, "converged": None, "plateau_eval": None,
                "reason": f"insufficient usable budgets ({len(rows)} < {min_budgets})", **base}

    rng = max(float(evals.max() - evals.min()), abs(float(evals.max())) * 1e-9, 1e-12)
    tol = float(plateau_rel_tol) * rng

    # (1) Still climbing at the ceiling -> NOT converged; the budget is under-trained, extend the ladder.
    last_gain = float(evals[-1] - evals[-2])
    if float(evals[-1]) >= float(evals.max()) - 1e-12 and last_gain > tol:
        return {"recommended_budget": budgets[-1], "converged": False, "plateau_eval": None,
                "reason": (f"eval return still RISING at the ladder ceiling (+{last_gain:.4g} over the last "
                           f"step > tol {tol:.4g} = {plateau_rel_tol:.0%} of range); EXTEND --budgets higher "
                           "before fixing train_steps_per_candidate (the agent is still under-trained)"),
                **base}

    # (2) Smallest budget from which the eval is flat (within tol) to the ceiling AND critic finite onward,
    #     with >= 1 budget after it confirming the plateau (so a lone noisy ceiling can't be the knee).
    for i in range(len(rows) - 1):
        tail = evals[i:]
        if float(tail.max() - tail.min()) <= tol and all(finite[i:]):
            return {"recommended_budget": budgets[i], "converged": True,
                    "plateau_eval": float(np.median(tail)),
                    "reason": (f"eval return flat (within {plateau_rel_tol:.0%} of range) from {budgets[i]} "
                               f"to {budgets[-1]} with finite critic loss"),
                    **base}

    # (3) Non-monotone/noisy or critic non-finite near the ceiling -> not safe to fix; add seeds / extend.
    return {"recommended_budget": budgets[-1], "converged": False, "plateau_eval": None,
            "reason": ("no confirmed plateau (eval non-monotone/noisy across seeds, or critic non-finite near "
                       "the ceiling); add --seeds and/or EXTEND --budgets higher"),
            **base}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Training-budget learning curve (under-training gate).")
    # Brackets the current 50k campaign budget and reaches 16x above it — wide enough to expose a plateau
    # even if the agent is ~10-40x under-trained (the audit estimate). The detector says to extend if not.
    p.add_argument("--budgets", default="50000,100000,200000,400000,800000", help="Comma list of step budgets.")
    p.add_argument("--seeds", default="0", help="Comma list of seeds to average per budget.")
    p.add_argument("--reward", default="differential_sharpe", help="REWARD_CANON key (representative reward).")
    p.add_argument("--synthetic", action="store_true", help="Use a synthetic panel instead of real gold.")
    p.add_argument("--end", default="2014-12-31", help="Real-data slice end date (dev TRAIN end).")
    p.add_argument("--device", default="auto", choices=["cpu", "cuda", "auto"], help="Compute device.")
    p.add_argument("--out-dir", default="outputs/tables", help="Output directory.")
    p.add_argument("--no-plot", action="store_true", help="Skip the PNG (still writes json + md).")
    p.add_argument(
        "--smoke",
        action="store_true",
        help="Tiny-budget self-test ({200,400}, synthetic, cpu, no plot) — the unit-test mode.",
    )
    return p


class _CriticLossRecorder:
    """SB3 callback recording (step, critic_loss) pairs seen during training (reused from smoke_test)."""

    def __init__(self) -> None:
        self.steps: list[int] = []
        self.losses: list[float] = []

    def make(self) -> Any:
        from stable_baselines3.common.callbacks import BaseCallback

        rec = self

        class _CB(BaseCallback):
            def _on_step(self) -> bool:
                v = self.model.logger.name_to_value.get("train/critic_loss")
                if v is not None and np.isfinite(v):
                    rec.steps.append(int(self.num_timesteps))
                    rec.losses.append(float(v))
                return True

        return _CB()


def _resolve_panel_and_windows(synthetic: bool, end: str, lookback: int) -> tuple[Any, tuple[int, int], tuple[int, int]]:
    """Return ``(panel, train_window, val_window)`` — synthetic or the real gold dev slice."""
    if synthetic:
        from src.data.synthetic import make_synthetic_panel

        panel = make_synthetic_panel(n_assets=30, n_days=600, seed=0)
        return panel, (lookback, 400), (400, panel.T)
    from src.data.loaders import load_gold_panel

    res = load_gold_panel(phase="development", end=end)
    panel = res.panel
    # Hold out the last ~20% of the slice as an in-slice eval window (a convergence probe, NOT the sealed
    # campaign val split — this tool never touches the 2018-2025 test leg). Keep a lookback-sized purge.
    split = max(lookback + 1, int(panel.T * 0.8))
    split = min(split, panel.T - 1)
    return panel, (lookback, split), (min(split + lookback, panel.T - 1), panel.T)


def _subsample(steps: list[int], losses: list[float], k: int = 60) -> list[list[float]]:
    """Down-sample the (step, loss) trajectory to <= k points for a compact JSON/plot payload."""
    n = len(steps)
    if n == 0:
        return []
    idx = np.unique(np.linspace(0, n - 1, min(k, n)).astype(int))
    return [[float(steps[i]), float(losses[i])] for i in idx]


def run_one_budget(
    budget: int,
    seed: int,
    reward_key: str,
    *,
    synthetic: bool,
    end: str,
    device: str,
) -> dict[str, Any]:
    """Train the FIXED (explosion-fixed) SAC at one (budget, seed); return eval + critic-loss diagnostics.

    Returns a dict with the held-out eval IQM return, the terminal and max critic loss, the subsampled
    critic-loss trajectory, and wall-clock seconds. Never raises into the ladder — a failed budget is
    reported with ``ok=False`` so the rest of the curve still runs.
    """
    out: dict[str, Any] = {"budget": int(budget), "seed": int(seed), "ok": False, "error": None}
    try:
        from src.agents.trainer import train_agent
        from src.baselines.rewards import REWARD_CANON
        from src.env.runner import make_env_builder
        from src.inference.bootstrap import iqm
        from src.utils.config import load_config

        if reward_key not in REWARD_CANON:
            raise KeyError(f"unknown reward {reward_key!r}; REWARD_CANON has {sorted(REWARD_CANON)}")
        reward_fn = REWARD_CANON[reward_key]

        env_cfg = load_config("environment")
        lookback = int(env_cfg["state"]["lookback_days"])
        panel, train_w, val_w = _resolve_panel_and_windows(synthetic, end, lookback)
        builder = make_env_builder(panel, env_cfg, train_w, val_w)
        bundle = builder(reward_fn)

        # The FIXED agent under the campaign numerics: PopArt on + the gated learning_starts. Buffer is
        # coupled to the budget (ADR-025 memory-safe full-history replay).
        agent_cfg = {
            "train_steps_per_candidate": int(budget),
            "buffer_size": int(budget),
            "normalize_obs": True,
            "popart": True,
            "device": device,
            "seed": int(seed),
        }
        rec = _CriticLossRecorder()
        t0 = time.perf_counter()
        policy = train_agent(bundle.train_env(), agent_cfg, seed=int(seed), callback=rec.make())
        dt = time.perf_counter() - t0

        val = np.asarray(bundle.val_returns(policy), dtype=float)
        out.update(
            ok=True,
            eval_iqm=float(iqm(val)) if val.size else float("nan"),
            eval_mean=float(np.mean(val)) if val.size else float("nan"),
            eval_n=int(val.size),
            critic_loss_terminal=float(rec.losses[-1]) if rec.losses else None,
            critic_loss_max=float(np.max(rec.losses)) if rec.losses else None,
            critic_loss_finite=bool(rec.losses and np.isfinite(rec.losses).all()),
            critic_trajectory=_subsample(rec.steps, rec.losses),
            seconds=round(dt, 2),
        )
    except Exception as exc:  # noqa: BLE001 - one failed budget must not abort the ladder
        import traceback

        out["error"] = f"{type(exc).__name__}: {exc}"
        out["traceback"] = traceback.format_exc().splitlines()[-3:]
    return out


def run_curve(
    budgets: list[int],
    seeds: list[int],
    reward_key: str,
    *,
    synthetic: bool,
    end: str,
    device: str,
) -> dict[str, Any]:
    """Run the full (budget x seed) ladder; return the raw runs + the per-budget seed-IQM summary."""
    runs = [
        run_one_budget(b, s, reward_key, synthetic=synthetic, end=end, device=device)
        for b in budgets
        for s in seeds
    ]
    summary: list[dict[str, Any]] = []
    for b in budgets:
        ok = [r for r in runs if r["budget"] == b and r["ok"]]
        evals = [r["eval_iqm"] for r in ok if r.get("eval_iqm") is not None and np.isfinite(r["eval_iqm"])]
        crit = [r["critic_loss_max"] for r in ok if r.get("critic_loss_max") is not None]
        summary.append(
            {
                "budget": int(b),
                "n_ok": len(ok),
                # Seed-IQM of the per-seed eval IQM (rliable-style; robust to a seed outlier).
                "eval_iqm_over_seeds": float(np.median(evals)) if evals else float("nan"),
                "eval_spread": float(np.std(evals)) if len(evals) > 1 else 0.0,
                "critic_loss_max": float(np.max(crit)) if crit else None,
                "critic_finite_all": bool(ok) and all(r["critic_loss_finite"] for r in ok),
            }
        )
    return {
        "reward": reward_key,
        "device": device,
        "runs": runs,
        "summary": summary,
        "convergence": recommend_budget(summary),
    }


def _write_markdown(result: dict[str, Any], path: Path) -> None:
    """Write the human-readable plateau table (budget | eval IQM | spread | max critic | finite)."""
    lines = [
        f"# Training-budget learning curve — reward `{result['reward']}` (device={result['device']})",
        "",
        "Read the budget at the PLATEAU: the smallest budget past which `eval_iqm_over_seeds` stops rising "
        "AND `critic_loss_max` is flat/finite. This is an engineering diagnostic on the machinery — no number "
        "enters the dissertation; it INFORMS the (amendment-gated) `train_steps_per_candidate`.",
        "",
        "| budget | n_ok | eval IQM (seed-median) | eval spread | max critic loss | critic finite |",
        "|--------|------|------------------------|-------------|-----------------|---------------|",
    ]
    for row in result["summary"]:
        cl = row["critic_loss_max"]
        lines.append(
            f"| {row['budget']} | {row['n_ok']} | {row['eval_iqm_over_seeds']:.6g} | "
            f"{row['eval_spread']:.3g} | {cl:.4g} | {row['critic_finite_all']} |"
            if cl is not None
            else f"| {row['budget']} | {row['n_ok']} | {row['eval_iqm_over_seeds']:.6g} | "
            f"{row['eval_spread']:.3g} | n/a | {row['critic_finite_all']} |"
        )
    conv = result.get("convergence")
    if conv:
        verdict = (
            "✅ CONVERGED" if conv.get("converged") is True
            else "⚠️ NOT CONVERGED" if conv.get("converged") is False
            else "❓ INSUFFICIENT DATA"
        )
        lines += [
            "",
            "## Convergence verdict (objective knee detector)",
            "",
            f"**{verdict}** — recommended `train_steps_per_candidate` = "
            f"**{conv.get('recommended_budget')}**",
            "",
            f"> {conv.get('reason')}",
        ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_plot(result: dict[str, Any], path: Path) -> bool:
    """Write the two-panel plateau plot (eval-vs-budget; critic-loss-vs-step). Returns False if skipped."""
    try:
        import matplotlib

        matplotlib.use("Agg")  # headless
        import matplotlib.pyplot as plt
    except Exception:  # pragma: no cover - matplotlib optional
        return False

    summary = result["summary"]
    budgets = [r["budget"] for r in summary]
    evals = [r["eval_iqm_over_seeds"] for r in summary]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 9))
    ax1.plot(budgets, evals, "o-", color="tab:blue")
    ax1.set_xlabel("training-step budget")
    ax1.set_ylabel("held-out eval IQM return")
    ax1.set_title(f"Eval return vs budget — pick the PLATEAU (reward={result['reward']})")
    ax1.grid(True, alpha=0.3)

    # Per-budget critic-loss trajectories (log scale — the explosion, if any, is orders of magnitude).
    for run in result["runs"]:
        traj = run.get("critic_trajectory") or []
        if run["ok"] and traj:
            xs = [p[0] for p in traj]
            ys = [max(p[1], 1e-12) for p in traj]
            ax2.plot(xs, ys, alpha=0.7, label=f"{run['budget']} (seed {run['seed']})")
    ax2.set_yscale("log")
    ax2.set_xlabel("training step")
    ax2.set_ylabel("critic loss (log)")
    ax2.set_title("Critic loss vs step — must stay flat/finite (no late explosion)")
    ax2.grid(True, alpha=0.3, which="both")
    if ax2.get_legend_handles_labels()[0]:
        ax2.legend(fontsize=7, ncol=2)

    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return True


def main() -> None:
    args = build_parser().parse_args()
    from src.utils.preload import preload

    preload()  # pyarrow before torch (real gold parquet) — ADR/audit

    if args.smoke:
        # Budgets > the 1000-step learning_starts floor so the critic actually regresses (exercises the
        # loss-trajectory + plot logic); synthetic + cpu so the self-test is hermetic and fast-ish (~30s).
        budgets, seeds = [1100, 1300], [0]
        synthetic, device, no_plot, end = True, "cpu", False, args.end
    else:
        budgets = [int(x) for x in str(args.budgets).split(",") if x.strip()]
        seeds = [int(x) for x in str(args.seeds).split(",") if x.strip()]
        synthetic, device, no_plot, end = bool(args.synthetic), args.device, bool(args.no_plot), args.end

    print("=" * 72)
    print("[learning_curve] training-budget convergence diagnostic (under-training gate)")
    print(f"  reward   : {args.reward}")
    print(f"  budgets  : {budgets}")
    print(f"  seeds    : {seeds}")
    print(f"  panel    : {'synthetic' if synthetic else f'real gold dev -> {end}'}")
    print(f"  device   : {device}")
    print("=" * 72)

    result = run_curve(budgets, seeds, args.reward, synthetic=synthetic, end=end, device=device)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "learning_curve.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    _write_markdown(result, out_dir / "learning_curve.md")
    plotted = False if no_plot else _write_plot(result, out_dir / "learning_curve.png")

    print("\n--- per-budget summary (eval IQM seed-median | max critic loss | finite) ---")
    for row in result["summary"]:
        cl = row["critic_loss_max"]
        cl_s = f"{cl:.4g}" if cl is not None else "n/a"
        print(
            f"  budget={row['budget']:>7}  n_ok={row['n_ok']}  eval_iqm={row['eval_iqm_over_seeds']:.6g}"
            f"  max_critic={cl_s}  finite={row['critic_finite_all']}"
        )
    conv = result.get("convergence") or {}
    verdict = (
        "CONVERGED" if conv.get("converged") is True
        else "NOT CONVERGED" if conv.get("converged") is False
        else "INSUFFICIENT DATA"
    )
    print("\n" + "=" * 72)
    print(f"[learning_curve] CONVERGENCE VERDICT: {verdict}")
    print(f"  recommended train_steps_per_candidate = {conv.get('recommended_budget')}")
    print(f"  {conv.get('reason')}")
    print("=" * 72)
    print(f"\n[learning_curve] wrote json + md to {out_dir}" + (" + png" if plotted else " (no png)"))
    if conv.get("converged") is False:
        print("[learning_curve] ACTION: re-run with a higher --budgets ceiling (and/or more --seeds) "
              "until the verdict is CONVERGED, then fix train_steps_per_candidate at the recommendation.")


if __name__ == "__main__":
    main()
