def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get("reward_state")
    
    # Initialize state
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cumulative": 1.0,
            "step": 0,
        }
    
    step = state["step"] + 1
    ret_history = state["ret_history"]
    peak = state["peak"]
    cumulative = state["cumulative"]
    
    # Update cumulative wealth
    cumulative = cumulative * (1.0 + port_ret)
    peak = max(peak, cumulative)
    
    # Track return history (rolling window)
    window = 60
    ret_history = ret_history + [port_ret]
    if len(ret_history) > window:
        ret_history = ret_history[-window:]
    
    # --- Component 1: Sharpe-based signal ---
    if len(ret_history) >= 5:
        arr = np.array(ret_history)
        mean_r = np.mean(arr)
        std_r = np.std(arr) + 1e-8
        sharpe_signal = mean_r / std_r
    else:
        sharpe_signal = 0.0
    
    # --- Component 2: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.1 * turnover
    
    # --- Component 3: Drawdown penalty ---
    drawdown = (peak - cumulative) / (peak + 1e-8)
    drawdown_penalty = 0.5 * drawdown
    
    # --- Component 4: Concentration penalty (encourage diversification) ---
    # Penalize very concentrated portfolios (Herfindahl index)
    n = len(weights)
    herfindahl = np.sum(weights ** 2)
    max_herfindahl = 1.0
    min_herfindahl = 1.0 / n
    concentration = (herfindahl - min_herfindahl) / (max_herfindahl - min_herfindahl + 1e-8)
    concentration_penalty = 0.05 * concentration
    
    # --- Component 5: Direct return signal (scaled) ---
    # Clip to avoid extreme values
    direct_ret = np.clip(port_ret, -0.1, 0.1) * 10.0
    
    # --- Total reward ---
    # Blend: primarily sharpe-based + direct return, minus penalties
    total = (
        0.5 * sharpe_signal
        + 0.5 * direct_ret
        - turnover_penalty
        - drawdown_penalty
        - concentration_penalty
    )
    
    # Clip total to prevent extreme values destabilizing training
    total = float(np.clip(total, -5.0, 5.0))
    
    components = {
        "sharpe_signal": float(sharpe_signal),
        "direct_ret": float(direct_ret),
        "turnover_penalty": float(turnover_penalty),
        "drawdown_penalty": float(drawdown_penalty),
        "concentration_penalty": float(concentration_penalty),
    }
    
    reward_state = {
        "ret_history": ret_history,
        "peak": float(peak),
        "cumulative": float(cumulative),
        "step": step,
    }
    
    return total, components, reward_state