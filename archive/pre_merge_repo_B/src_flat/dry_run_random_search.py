"""TrialLedger end-to-end dry run on THROWAWAY candidates (week plan, Friday block).

    python -m src.dry_run_random_search        # or: run(...) from tests

What this proves — and the only thing it proves: the plumbing. Family candidates are
sampled from the pre-registered space, pushed through the PortfolioEnv (contract
validated at every step), scored by the fitness on a synthetic "validation" slice,
counted by the TrialLedger, and summarised by DSR + PBO/CSCV exactly as the real arms
will be. NOTHING here is evidence about any hypothesis:

  * returns are SYNTHETIC (seeded Gaussian) — no market data is touched (R4);
  * policies are NOT trained — each candidate is paired with a fixed seeded
    random-logit allocation, so the reward function cannot influence the policy;
  * λ is an EXPLICIT THROWAWAY (passed by argument); `inference.fitness.lambda_frozen`
    stays null and the §3 calibration remains pending;
  * the ledger lives and dies inside this run — nothing is persisted into any real
    trial count.

Artifacts: a JSON sidecar under runs/dry_run/ (config hashes, seed in filename,
wall-clock, per-candidate table) per the compute-reporting convention in CLAUDE.md.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

import numpy as np
from scipy.stats import kurtosis, skew

from .config import CONFIG_DIR
from .fitness import cvar_penalised_sharpe, unannualised_sharpe
from .portfolio_env import PortfolioEnv
from .reward_family import params_id, params_to_reward, sample_params
from .stats_inference import TrialLedger, pbo_cscv

ROOT = Path(__file__).resolve().parent.parent
ARM_LABEL = "random_search[dry-run]"
THROWAWAY_LAMBDA = 1.0  # explicit, labelled; NOT the §3-calibrated value (still null)


def _config_hashes() -> dict[str, str]:
    out = {}
    for p in sorted(CONFIG_DIR.glob("*.yaml")):
        out[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    return out


def _rollout_net_returns(returns: np.ndarray, reward_fn, logits: np.ndarray,
                         lookback: int, cost_bps: float) -> np.ndarray:
    """Daily net returns of a fixed-logit allocation rolled through the env (the env
    validates the reward contract at every step as a side effect)."""
    env = PortfolioEnv(returns, reward_fn, cost_bps=cost_bps, lookback=lookback)
    env.reset(seed=0)
    net, done = [], False
    while not done:
        _, _, done, _, info = env.step(logits)
        net.append(info["net_return"])
    return np.asarray(net)


def run(n_candidates: int = 10, t_total: int = 460, n_assets: int = 5,
        lookback: int = 60, cost_bps: float = 10.0, seed: int = 0,
        n_blocks: int | None = None, write_sidecar: bool = True) -> dict:
    """Execute the dry run; returns the summary dict (also written as the sidecar)."""
    t0 = time.monotonic()
    rng = np.random.default_rng(seed)
    synthetic = rng.normal(0.0003, 0.012, size=(t_total, n_assets))  # synthetic, R4-safe

    ledger = TrialLedger()
    rows, pnl_cols = [], []
    for i in range(n_candidates):
        params = sample_params(rng)
        cid = params_id(params)
        logits = rng.normal(0.0, 1.0, size=n_assets + 1).astype(np.float32)
        net = _rollout_net_returns(synthetic, params_to_reward(params), logits,
                                   lookback, cost_bps)
        sr = unannualised_sharpe(net)
        fit = cvar_penalised_sharpe(net, lam=THROWAWAY_LAMBDA)
        ledger.register(ARM_LABEL, cid, sr, n_obs=net.size)
        rows.append({"candidate_id": cid, "params": params, "sharpe_unann": sr,
                     "fitness_throwaway": fit, "n_obs": int(net.size)})
        pnl_cols.append(net)

    best = max(rows, key=lambda r: r["fitness_throwaway"])
    best_net = pnl_cols[rows.index(best)]
    dsr = ledger.dsr_for(
        best["sharpe_unann"], n_obs=best_net.size,
        skew=float(skew(best_net)), kurt=float(kurtosis(best_net, fisher=False)),  # RAW kurtosis (R5)
    )
    pnl = np.column_stack(pnl_cols)
    pbo = pbo_cscv(pnl, n_blocks=int(n_blocks if n_blocks is not None else 16))

    summary = {
        "label": "DRY RUN — throwaway candidates, synthetic data, untrained policies; "
                 "plumbing proof only (no hypothesis evidence)",
        "arm": ARM_LABEL,
        "seed": seed,
        "throwaway_lambda": THROWAWAY_LAMBDA,
        "n_candidates": n_candidates,
        "ledger_n_trials": ledger.n_trials,
        "best_candidate": best["candidate_id"],
        "best_fitness_throwaway": best["fitness_throwaway"],
        "dsr": {k: (float(v) if isinstance(v, float) else v) for k, v in dsr.items()},
        "pbo": float(pbo["pbo"]),
        "pbo_n_combinations": int(pbo["n_combinations"]),
        "candidates": rows,
        "config_sha256_16": _config_hashes(),
        "wall_clock_s": round(time.monotonic() - t0, 3),
    }
    if write_sidecar:
        out_dir = ROOT / "runs" / "dry_run"
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / f"dry_run_random_search_seed{seed}.json"
        out.write_text(json.dumps(summary, indent=2, sort_keys=True))
        summary["sidecar"] = str(out)
    return summary


def main() -> int:
    s = run()
    print(f"[DRY-RUN] {s['label']}")
    print(f"[DRY-RUN] ledger N = {s['ledger_n_trials']} (all candidates counted — R5)")
    print(f"[DRY-RUN] best {s['best_candidate']}  F_throwaway={s['best_fitness_throwaway']:+.4f}")
    print(f"[DRY-RUN] DSR={s['dsr']['dsr']:.4f}  SR0={s['dsr']['sr0']:+.4f}  "
          f"N={s['dsr']['n_trials']}  PBO={s['pbo']:.3f} ({s['pbo_n_combinations']} splits)")
    print(f"[DRY-RUN] sidecar: {s.get('sidecar', '(not written)')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
