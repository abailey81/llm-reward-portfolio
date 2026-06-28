def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize state
    state = info.get("reward_state") or {}
    
    # Running statistics for online Sharpe
    n = state.get("n", 0)
    mean_ret = state.get("mean_ret", 0.0)
    M2 = state.get("M2", 0.0)  # sum of squared deviations
    peak = state.get("peak", 1.0)
    cumulative = state.get("cumulative", 1.0)
    
    # Update cumulative return
    cumulative = cumulative * (1.0 + port_ret)
    peak = max(peak, cumulative)
    drawdown = (peak - cumulative) / peak
    
    # Welford's online mean and variance update
    n += 1
    delta = port_ret - mean_ret
    mean_ret += delta / n
    delta2 = port_ret - mean_ret
    M2 += delta * delta2
    
    # Compute variance and std
    if n >= 2:
        variance = M2 / (n - 1)
        std_ret = np.sqrt(max(variance, 1e-10))
    else:
        std_ret = 1e-5
    
    # Online Sharpe (annualized approximation with 252 steps/year)
    sharpe = (mean_ret / std_ret) * np.sqrt(252) if std_ret > 1e-10 else 0.0
    
    # Downside deviation (for Sortino-like measure)
    downside_M2 = state.get("downside_M2", 0.0)
    neg_ret = min(port_ret, 0.0)
    downside_M2 += neg_ret ** 2
    if n >= 2:
        downside_std = np.sqrt(max(downside_M2 / n, 1e-10))
    else:
        downside_std = 1e-5
    
    sortino = (mean_ret / downside_std) * np.sqrt(252) if downside_std > 1e-10 else 0.0
    
    # Turnover cost penalty
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.1 * turnover
    
    # Drawdown penalty - penalize deep drawdowns nonlinearly
    drawdown_penalty = 2.0 * (drawdown ** 2)
    
    # Core reward: blend of step return and running Sharpe signal
    # Use incremental Sharpe contribution as primary reward
    # Step-level reward: return scaled by risk context
    step_reward = port_ret / (std_ret + 1e-8)
    
    # Normalize step reward to avoid large magnitudes
    step_reward_clipped = np.clip(step_reward, -5.0, 5.0)
    
    # Total reward combines step signal with penalties
    total = (0.6 * step_reward_clipped 
             + 0.2 * np.clip(sortino / 10.0, -2.0, 2.0)
             - drawdown_penalty 
             - turnover_penalty)
    
    components = {
        "step_reward": float(step_reward_clipped),
        "sortino_component": float(np.clip(sortino / 10.0, -2.0, 2.0)),
        "drawdown_penalty": float(-drawdown_penalty),
        "turnover_penalty": float(-turnover_penalty),
        "port_ret": float(port_ret),
        "running_sharpe": float(sharpe),
    }
    
    reward_state = {
        "n": n,
        "mean_ret": mean_ret,
        "M2": M2,
        "downside_M2": downside_M2,
        "peak": peak,
        "cumulative": cumulative,
    }
    
    return float(total), components, reward_state