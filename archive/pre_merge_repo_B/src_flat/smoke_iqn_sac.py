"""IQN-inside-SAC proof-of-life — plan block W2; API verified against d3rlpy 2.8.1
source (DECISIONS.md ADR-003). Run locally on the RTX 4090:

    make smoke          # or: python -m src.smoke_iqn_sac

PASS criteria: (1) SACConfig(q_func_factory=IQNQFunctionFactory(...)) constructs and
builds against a continuous env; (2) a few online steps train without error;
(3) the critic is introspected as IQN. Paste the PASS log into DECISIONS.md ADR-003.
Fallback on runtime quirks: QRQFunctionFactory (same module) — RQ2 needs *a*
distributional critic (CLAUDE.md crib sheet).
"""
from __future__ import annotations

import numpy as np


def main() -> int:
    try:
        import gymnasium as gym
        from d3rlpy.algos import SACConfig
        from d3rlpy.models import IQNQFunctionFactory
    except ImportError as e:
        print(f"[SMOKE][FAIL] import: {e} -> `make setup` first")
        return 1

    class DummyPortfolio(gym.Env):
        """Obs ~ flattened lookback (20), action ~ 6 logits — shapes only, no semantics."""
        observation_space = gym.spaces.Box(-np.inf, np.inf, shape=(20,), dtype=np.float32)
        action_space = gym.spaces.Box(-1.0, 1.0, shape=(6,), dtype=np.float32)

        def reset(self, *, seed=None, options=None):
            super().reset(seed=seed)
            self._i = 0
            return self.observation_space.sample(), {}

        def step(self, action):
            self._i += 1
            obs = self.observation_space.sample()
            reward = float(np.tanh(action.sum()) * 0.01 + np.random.normal(0, 0.001))
            return obs, reward, self._i >= 50, False, {}

    env = DummyPortfolio()
    factory = IQNQFunctionFactory(n_quantiles=64, n_greedy_quantiles=32, embed_size=64)
    print(f"[SMOKE] IQNQFunctionFactory OK: {factory}")

    device = None
    try:
        import torch
        device = "cuda:0" if torch.cuda.is_available() else "cpu:0"
    except ImportError:
        device = "cpu:0"

    sac = SACConfig(q_func_factory=factory, batch_size=64).create(device=device)
    print(f"[SMOKE] SAC created on {device}")

    sac.build_with_env(env)
    print("[SMOKE] build_with_env OK (continuous IQN forwarder constructed — ADR-003)")

    import d3rlpy
    buffer = d3rlpy.dataset.create_fifo_replay_buffer(limit=10_000, env=env)
    explorer = d3rlpy.algos.NormalNoise(mean=0.0, std=0.1)
    sac.fit_online(env, buffer, explorer=explorer, n_steps=300, n_steps_per_epoch=300,
                   update_start_step=128, show_progress=False)
    print("[SMOKE] 300 online steps trained")

    obs, _ = env.reset(seed=0)
    action = sac.predict(np.expand_dims(obs, 0))
    print(f"[SMOKE] predict OK, action shape={action.shape}")
    qf_repr = repr(getattr(sac, "impl", None) and sac.impl.q_function)
    assert "IQN" in qf_repr or "iqn" in qf_repr.lower(), f"critic is not IQN: {qf_repr[:200]}"
    print("[SMOKE][PASS] IQN critic confirmed inside SAC — quantile channel available.")
    print("        Next: extract Z(s0,.) quantiles via the forwarder for feedback_schema "
          "(week_plan Thu: calibration figure v0).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
