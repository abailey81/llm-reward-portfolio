def reward(weights, returns, prev_weights, port_ret, info):
    reward_state = info.get("reward_state", None)
    
    # Initialize state
    if reward_state is None:
        reward_state = {
            "ret_history": [],
            "peak": 0.0,
            "cumulative": 0.0,
            "step": 0,
        }
    
    step = reward_state["step"] + 1
    ret_history = reward_state["ret_history"]
    
    # Update history (keep rolling window)
    window = 100
    ret_history.append(float(port_ret))
    if len(ret_history) > window:
        ret_history = ret_history[-window:]
    
    # Update cumulative return for drawdown
    cumulative = reward_state["cumulative"] + float(port_ret)
    peak = max(reward_state["peak"], cumulative)
    drawdown = peak - cumulative  # always >= 0
    
    # --- Component 1: Online Sharpe (annualized direction) ---
    if len(ret_history) >= 8:
        arr = np.array(ret_history)
        mean_r = np.mean(arr)
        std_r = np.std(arr) + 1e-8
        sharpe_signal = mean_r / std_r
    else:
        sharpe_signal = float(port_ret)
    
    # --- Component 2: Turnover penalty ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = 0.1 * turnover
    
    # --- Component 3: Drawdown penalty ---
    dd_penalty = 0.5 * drawdown
    
    # --- Component 4: Downside penalty (CVaR-like) ---
    if len(ret_history) >= 8:
        arr = np.array(ret_history)
        tail_threshold = np.percentile(arr, 10)
        tail_losses = arr[arr < tail_threshold]
        cvar_penalty = float(-np.mean(tail_losses)) * 0.3 if len(tail_losses) > 0 else 0.0
    else:
        cvar_penalty = max(0.0, -float(port_ret)) * 0.3
    
    # --- Total reward ---
    total = sharpe_signal - turnover_penalty - dd_penalty - cvar_penalty
    
    components = {
        "sharpe_signal": float(sharpe_signal),
        "turnover_penalty": float(-turnover_penalty),
        "drawdown_penalty": float(-dd_penalty),
        "cvar_penalty": float(-cvar_penalty),
    }
    
    reward_state = {
        "ret_history": ret_history,
        "peak": float(peak),
        "cumulative": float(cumulative),
        "step": step,
    }
    
    return float(total), components, reward_state