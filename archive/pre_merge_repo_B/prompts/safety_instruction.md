# Safety instruction block (appended to every generation prompt)
<!-- Precedent: DrEureka's safety-instruction finding — prompting safety terms beats post-hoc filtering. -->
Hard constraints your reward must respect:
- Long-only, fully-invested-or-cash: the environment enforces softmax weights; do not fight it.
- Penalise turnover explicitly OR justify in a comment why not; daily costs compound.
- All components finite, bounded (|component| < 1e6), and defined for zero-variance windows
  (guard std==0, log(<=0), division by ~0 with epsilons).
- Use only `ctx` fields; `lookback_returns` and `regime_probs` are already lag-safe — do not attempt to
  reconstruct future information.
- numpy only; pure function of ctx; deterministic.
