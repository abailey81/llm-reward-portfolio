def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize state
    state = info.get("reward_state") or {}
    
    # Rolling window parameters
    WINDOW = 60
    
    # Retrieve history
    ret_history = state.get("ret_history", [])
    peak = state.get("peak", 1.0)
    cumulative = state.get("cumulative", 1.0)
    
    # Update cumulative and drawdown
    cumulative = cumulative * (1.0 + port_ret)
    peak = max(peak, cumulative)
    drawdown = (peak - cumulative) / (peak + 1e-8)
    
    # Update return history
    ret_history.append(port_ret)
    if len(ret_history) > WINDOW:
        ret_history = ret_history[-WINDOW:]
    
    n = len(ret_history)
    arr = np.array(ret_history, dtype=np.float64)
    
    # Compute mean and std of returns
    mean_ret = np.mean(arr)
    std_ret = np.std(arr) + 1e-8
    
    # Sharpe-like component (annualized direction, but we keep it simple)
    sharpe_component = mean_ret / std_ret
    
    # Tail risk penalty: mean of worst returns (CVaR-like)
    if n >= 10:
        tail_cutoff = max(1, int(0.1 * n))
        sorted_arr = np.sort(arr)
        cvar = np.mean(sorted_arr[:tail_cutoff])
    else:
        cvar = 0.0
    tail_penalty = min(0.0, cvar)  # Only penalize negative tail
    
    # Drawdown penalty (non-linear)
    drawdown_penalty = -drawdown ** 1.5
    
    # Turnover penalty to reduce costs
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.5 * turnover
    
    # Concentration penalty (encourage some diversification)
    # Penalize extreme concentration in single asset
    herfindahl = np.sum(weights ** 2)
    n_assets = len(weights)
    min_herf = 1.0 / n_assets  # perfectly diversified
    concentration_penalty = -0.3 * (herfindahl - min_herf)
    
    # Scale and combine
    # Primary: return-based Sharpe signal
    # Secondary: risk controls
    if n < 5:
        # Warm-up: just use raw return
        total = port_ret * 10.0
    else:
        total = (
            sharpe_component * 1.0       # Sharpe ratio estimate
            + tail_penalty * 5.0         # CVaR penalty
            + drawdown_penalty * 2.0     # Drawdown penalty
            + turnover_penalty           # Transaction cost penalty
            + concentration_penalty      # Diversification nudge
        )
    
    components = {
        "sharpe_component": sharpe_component if n >= 5 else 0.0,
        "tail_penalty": tail_penalty,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
        "port_ret": port_ret,
    }
    
    reward_state = {
        "ret_history": ret_history,
        "peak": peak,
        "cumulative": cumulative,
    }
    
    return float(total), components, reward_state