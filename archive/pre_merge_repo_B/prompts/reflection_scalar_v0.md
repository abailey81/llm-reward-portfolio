# Reflection template — SCALAR arm (H2 control)
<!-- Eureka-style: per-component time series at checkpoints + fitness. NO distributional information. -->
Training reflection for candidate {candidate_id} (algorithm {algo}, seeds {seeds}):
- Fitness on validation window: F = {fitness:.4f}  (rank {rank}/{k} this generation)
- Validation: Sharpe(unann)={sr:.4f}, cum.return={cumret:.2%}, max drawdown={mdd:.2%},
  mean daily turnover={turnover:.3%}, mean daily cost={cost_bps:.1f}bps
- Reward components at checkpoints {checkpoints}:
{component_timeseries_table}
- Training stability: {n_seeds_converged}/{n_seeds} seeds converged; inter-seed fitness std={seed_std:.4f}
