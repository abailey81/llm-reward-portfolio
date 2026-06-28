def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state") or {}
    
    # Rolling window for return history
    window = 60
    ret_history = state.get("ret_history", [])
    ret_history.append(float(port_ret))
    if len(ret_history) > window:
        ret_history = ret_history[-window:]
    
    # Peak tracking for drawdown
    cumulative = state.get("cumulative", 1.0)
    cumulative = cumulative * (1.0 + float(port_ret))
    peak = state.get("peak", 1.0)
    peak = max(peak, cumulative)
    drawdown = (peak - cumulative) / (peak + 1e-8)
    
    arr = np.array(ret_history, dtype=np.float64)
    n = len(arr)
    
    # --- Component 1: Online Sharpe-based reward ---
    if n >= 5:
        mean_ret = np.mean(arr)
        std_ret = np.std(arr) + 1e-8
        sharpe_reward = mean_ret / std_ret
    else:
        sharpe_reward = float(port_ret)
    
    # --- Component 2: CVaR penalty (Expected Shortfall at 5%) ---
    if n >= 10:
        sorted_arr = np.sort(arr)
        cutoff_idx = max(1, int(np.floor(0.05 * n)))
        cvar_5 = np.mean(sorted_arr[:cutoff_idx])
        # Penalize negative CVaR (tail losses)
        cvar_penalty = min(0.0, cvar_5) * 3.0
    else:
        cvar_penalty = 0.0
    
    # --- Component 3: Drawdown penalty ---
    drawdown_penalty = -drawdown * 1.5
    
    # --- Component 4: Turnover / transaction cost penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -turnover * 0.05
    
    # --- Component 5: Skewness bonus (reward positive skew) ---
    if n >= 10:
        mean_ret = np.mean(arr)
        std_ret = np.std(arr) + 1e-8
        skewness = np.mean(((arr - mean_ret) / std_ret) ** 3)
        skew_bonus = np.clip(skewness, -1.0, 1.0) * 0.05
    else:
        skewness = 0.0
        skew_bonus = 0.0
    
    # --- Combine components ---
    # Scale sharpe reward to be primary driver
    total = (
        sharpe_reward * 0.5
        + cvar_penalty
        + drawdown_penalty
        + turnover_penalty
        + skew_bonus
    )
    
    components = {
        "sharpe_reward": float(sharpe_reward),
        "cvar_penalty": float(cvar_penalty),
        "drawdown_penalty": float(drawdown_penalty),
        "turnover_penalty": float(turnover_penalty),
        "skew_bonus": float(skew_bonus),
        "port_ret": float(port_ret),
        "drawdown": float(drawdown),
    }
    
    reward_state = {
        "ret_history": ret_history,
        "cumulative": cumulative,
        "peak": peak,
    }
    
    return float(total), components, reward_state