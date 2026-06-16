"""Phase 0 GATE smoke test (FINAL_PLAN H, Phase 0).

Purpose
-------
Hardware + software + plumbing gate that MUST pass GREEN before any heavy
work (data build, freeze, campaign) is permitted. This is a precondition
recorded by ``scripts/freeze.py``.

What it WILL verify (acceptance criteria for Phase 0):
  1. CUDA is available and the active GPU is an RTX 4090.
  2. A small REAL data slice (or a SYNTHETIC slice of identical shape) loads.
  3. ``PortfolioEnv`` instantiates with a trivial reward_fn and steps cleanly.
  4. An SB3 ``SAC`` agent builds and trains a few thousand steps (ONLINE path).
  5. An sb3-contrib ``TQC`` agent builds and trains a few thousand steps
     (ONLINE path).
  6. Per-run wall-clock minutes are printed for each algo.
  7. Critic-loss start-vs-end is printed for each algo (sanity that learning
     is wired, not that it converged).

Exit status:
  GREEN  -> all checks pass, gate open.
  AMBER  -> trains but on a non-4090 GPU or with degraded timing; proceed with
            caution, record deviation in DECISION_LOG.
  RED    -> a hard precondition failed; gate closed.

Flags
-----
  --steps      Training steps per algo (default a few thousand).
  --synthetic  Use a synthetic slice of identical shape instead of real data.
"""

from __future__ import annotations


import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Phase 0 GATE smoke test (FINAL_PLAN H, Phase 0).",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=3000,
        help="Training steps per algo on the ONLINE path (default: 3000).",
    )
    parser.add_argument(
        "--synthetic",
        action="store_true",
        help="Use a synthetic slice of identical shape instead of a real slice.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    print("[smoke_test] Phase 0 GATE — planned actions:")
    print("  1. Assert CUDA available and GPU == RTX 4090.")
    print(
        f"  2. Load {'SYNTHETIC' if args.synthetic else 'REAL'} slice "
        "(identical shape either way)."
    )
    print("  3. Instantiate PortfolioEnv with a trivial reward_fn; step it.")
    print(f"  4. Build SB3 SAC; train {args.steps} steps (ONLINE) under a timer.")
    print(f"  5. Build sb3-contrib TQC; train {args.steps} steps (ONLINE) under a timer.")
    print("  6. Print per-run minutes and critic-loss start vs end per algo.")
    print("  7. Emit GREEN / AMBER / RED exit status.")

    # Lazy/guarded imports so the stub does not crash before implementation.
    try:
        from src.env.portfolio import PortfolioEnv  # noqa: F401
    except ImportError as exc:  # pragma: no cover - stub guard
        print(f"[smoke_test] NOTE: src.env.portfolio not yet implemented ({exc}).")

    # TODO(FINAL_PLAN H, Phase 0): implement the gate.
    #   - torch.cuda.is_available(); torch.cuda.get_device_name(0) contains "4090".
    #   - load slice via src.data loaders (real) or synth generator.
    #   - PortfolioEnv(reward_fn=lambda *_: 0.0); reset/step assertions.
    #   - SAC + TQC build; learn(args.steps); capture train/critic_loss.
    #   - time.perf_counter() around each .learn() call -> minutes.
    #   - decide GREEN/AMBER/RED and raise SystemExit with the right code.
    raise SystemExit("STUB — implement per FINAL_PLAN H Phase 0")


if __name__ == "__main__":
    main()
