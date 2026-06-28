"""Phase 0 GATE smoke test (FINAL_PLAN H, Phase 0; MASTER_EXECUTION_PLAN P2).

Purpose
-------
The hardware + software + plumbing gate that MUST pass before any heavy work (campaign).
It proves the fixed agents actually TRAIN on the real env, measures **minutes per 50k-step
run** (``m`` — the one unmeasured quantity every cost/time figure depends on), and finds the
laptop's concurrency knee.

What it verifies (acceptance criteria):
  1. The compute device (CPU / CUDA) and torch build are reported (NOT asserted == 4090:
     the prototype runs on this RTX-4050 laptop, and per the deep-research the SB3 [256,256]
     nets are CPU-bound, so the prototype uses CPU torch — the rented-4090 campaign uses CUDA).
  2. A REAL ``_univ3`` slice (or a SYNTHETIC slice of identical shape) loads.
  3. ``PortfolioEnv`` instantiates with a trivial reward and steps cleanly.
  4. SB3 ``SAC`` builds and trains (ONLINE path) with a MEMORY-SAFE buffer
     (``buffer_size == steps`` — the 1e6 default would need ~15 GB RAM at the 1893-dim obs).
  5. sb3-contrib ``TQC`` builds and trains (ONLINE path).
  6. Per-algo wall-clock, steps/sec, extrapolated minutes/50k, and critic-loss start-vs-end.
     (Critic-loss start->end is REPORTED for the operator to eyeball, NOT asserted: over a
     ~3000-step smoke window SAC/TQC critic loss is noisy and not reliably monotonic, so the
     gate asserts only that the final loss is finite — see the GREEN criterion below.)

Exit status:
  GREEN  -> both algos train, final critic loss finite, m printed.
  AMBER  -> trains but with a caveat (e.g. one algo failed, or a non-finite loss).
  RED    -> a hard precondition failed (env won't build/step, neither algo trains).

Flags
-----
  --steps      Training steps per algo (default 3000).
  --synthetic  Use a synthetic slice of identical shape instead of a real slice.
  --device     'cpu' | 'cuda' | 'auto' (default 'auto' -> cpu unless CUDA available).
  --algos      Comma list from {sac,tqc} (default 'sac,tqc').
  --end        Real-data slice end date (default 2006-12-31 -> a fast ~2-year slice).
"""
from __future__ import annotations

import argparse
import time


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Phase 0 GATE smoke test (FINAL_PLAN H, Phase 0).")
    p.add_argument("--steps", type=int, default=3000, help="Training steps per algo (default 3000).")
    p.add_argument("--synthetic", action="store_true", help="Use a synthetic slice of identical shape.")
    p.add_argument("--device", default="auto", choices=["cpu", "cuda", "auto"], help="Compute device.")
    p.add_argument("--algos", default="sac,tqc", help="Comma list from {sac,tqc}.")
    p.add_argument("--end", default="2006-12-31", help="Real-data slice end date (fast slice).")
    return p


def _trivial_reward(weights, returns, prev_weights, port_ret, info):
    """A minimal contract-conforming reward: optimise realised portfolio return.

    Matches the reward contract EXACTLY (5 positional params; see src/reward/contract.py).
    """
    pr = float(port_ret)
    return pr, {"port_ret": pr}, None


def _resolve_device(choice: str) -> str:
    import torch

    if choice == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return choice


def _load_panel(synthetic: bool, end: str):
    """Return a small ``Panel`` (real ``_univ3`` dev slice, or a synthetic slice)."""
    if synthetic:
        from src.data.synthetic import make_synthetic_panel

        return make_synthetic_panel(n_assets=30, n_days=600, seed=0), "synthetic(30x600)"
    from src.data.loaders import load_gold_panel

    res = load_gold_panel(phase="development", end=end)
    return res.panel, f"real _univ3 development -> {end} ({res.panel.T}x{res.panel.N})"


class _CriticLossRecorder:
    """A tiny SB3 callback that records 'train/critic_loss' values seen during training."""

    def __init__(self):
        self.losses: list[float] = []

    def make(self):
        from stable_baselines3.common.callbacks import BaseCallback

        recorder = self

        class _CB(BaseCallback):
            def _on_step(self) -> bool:
                v = self.model.logger.name_to_value.get("train/critic_loss")
                if v is not None:
                    recorder.losses.append(float(v))
                return True

        return _CB()


def _train_one(algo: str, panel, cfg, steps: int, device: str) -> dict:
    """Build + train one agent on a fresh env; return a metrics dict (never raises)."""
    out: dict = {"algo": algo, "ok": False, "error": None}
    try:
        from src.agents.factory import make_distributional_agent, make_headline_agent
        from src.env.portfolio_env import PortfolioEnv

        env = PortfolioEnv(panel, cfg, _trivial_reward)
        # Smoke a few env steps first (cheap; proves reset/step before SB3 wrapping).
        obs, _ = env.reset(seed=0)
        for _ in range(3):
            obs, r, term, trunc, info = env.step(env.action_space.sample())
            if term or trunc:
                env.reset(seed=0)
        out["obs_dim"] = int(obs.shape[0])

        # MEMORY-SAFE buffer (P2/ADR-025): buffer_size == steps, NOT the 1e6 default.
        agent_cfg = {
            "policy": "MlpPolicy",
            "learning_rate": 3e-4,
            "buffer_size": int(steps),
            "batch_size": 256,
            "learning_starts": min(1000, steps // 3),
            "gamma": 0.99,
            "ent_coef": "auto",
            "seed": 0,
            "verbose": 0,
            "device": device,
        }
        fresh_env = PortfolioEnv(panel, cfg, _trivial_reward)
        agent = (
            make_headline_agent(fresh_env, agent_cfg)
            if algo == "sac"
            else make_distributional_agent(fresh_env, agent_cfg)
        )
        rec = _CriticLossRecorder()
        t0 = time.perf_counter()
        agent.learn(total_timesteps=steps, callback=rec.make(), progress_bar=False)
        dt = time.perf_counter() - t0

        out["ok"] = True
        out["seconds"] = round(dt, 2)
        out["steps_per_sec"] = round(steps / dt, 1) if dt > 0 else float("inf")
        out["minutes_per_50k"] = round((50000 / (steps / dt)) / 60, 2) if dt > 0 else float("nan")
        out["critic_loss_first"] = rec.losses[0] if rec.losses else None
        out["critic_loss_last"] = rec.losses[-1] if rec.losses else None
        out["critic_loss_n"] = len(rec.losses)
    except Exception as exc:  # noqa: BLE001 - the gate must report, not crash
        import traceback

        out["error"] = f"{type(exc).__name__}: {exc}"
        out["traceback"] = traceback.format_exc().splitlines()[-4:]
    return out


def main() -> None:
    args = build_parser().parse_args()
    from src.utils.config import load_config
    from src.utils.preload import preload

    preload()  # pyarrow before torch (else loading the real gold parquet after torch SIGSEGVs) -- ADR/audit
    import torch

    device = _resolve_device(args.device)
    print("=" * 72)
    print("[smoke_test] Phase 0 GATE")
    print(f"  torch        : {torch.__version__}  | cuda_available={torch.cuda.is_available()}")
    print(f"  device       : {device}")
    print(f"  steps/algo   : {args.steps}")
    cfg = load_config("environment")
    panel, panel_desc = _load_panel(args.synthetic, args.end)
    print(f"  panel        : {panel_desc}")
    print("=" * 72)

    algos = [a.strip() for a in args.algos.split(",") if a.strip()]
    results = [_train_one(a, panel, cfg, args.steps, device) for a in algos]

    print("\n--- results ---")
    for r in results:
        if r["ok"]:
            print(
                f"  [{r['algo'].upper():>3}] OK  obs_dim={r.get('obs_dim')}  "
                f"{r['seconds']}s  {r['steps_per_sec']} steps/s  "
                f"~{r['minutes_per_50k']} min/50k  "
                f"critic_loss {r['critic_loss_first']}->{r['critic_loss_last']} (n={r['critic_loss_n']})"
            )
        else:
            print(f"  [{r['algo'].upper():>3}] FAIL  {r['error']}")
            for line in r.get("traceback", []):
                print(f"        {line}")

    trained = [r for r in results if r["ok"]]
    # GREEN asserts FINITENESS of the final critic loss only (NOT movement): over a ~3000-step
    # smoke window SAC/TQC critic loss is noisy and not reliably monotonic, so the start->end
    # delta is reported above for the operator to eyeball but is deliberately not gated on.
    finite_loss = [
        r for r in trained if r["critic_loss_last"] is not None and abs(r["critic_loss_last"]) < 1e9
    ]
    if len(trained) == len(algos) and len(finite_loss) == len(trained):
        status = "GREEN"
    elif trained:
        status = "AMBER"
    else:
        status = "RED"

    print(f"\n[smoke_test] STATUS: {status}")
    if trained:
        ms = [r["minutes_per_50k"] for r in trained]
        print(f"[smoke_test] measured m (min/50k-run): {min(ms)}–{max(ms)} on device={device}")
    print("[smoke_test] record the result + m in docs/DECISION_LOG.md (PHASE-0 entry).")
    raise SystemExit(0 if status == "GREEN" else (1 if status == "AMBER" else 2))


if __name__ == "__main__":
    main()
