def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get("reward_state", None)
    
    # Initialize state
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cum_value": 1.0,
            "n": 0,
        }
    
    # Update cumulative value and drawdown tracking
    state["cum_value"] *= (1.0 + port_ret)
    state["peak"] = max(state["peak"], state["cum_value"])
    drawdown = (state["peak"] - state["cum_value"]) / (state["peak"] + 1e-8)
    
    # Maintain return history for risk estimation
    state["ret_history"].append(port_ret)
    state["n"] += 1
    
    # Keep a rolling window
    window = 60
    if len(state["ret_history"]) > window:
        state["ret_history"] = state["ret_history"][-window:]
    
    hist = np.array(state["ret_history"])
    n = len(hist)
    
    # Compute mean and downside deviation
    mean_ret = np.mean(hist)
    
    if n < 5:
        # Not enough data — just use raw return
        sharpe_component = port_ret * 10.0
        downside_component = 0.0
        drawdown_penalty = 0.0
    else:
        # Annualized-style Sharpe using downside deviation (Sortino-like)
        downside_diff = hist[hist < 0.0]
        if len(downside_diff) > 1:
            downside_std = np.sqrt(np.mean(downside_diff ** 2))
        else:
            downside_std = np.std(hist) + 1e-8
        
        downside_std = max(downside_std, 1e-6)
        
        # Sortino-like ratio as main signal
        sharpe_component = mean_ret / downside_std
        
        # Tail risk: CVaR penalty (expected loss in worst 10% of steps)
        tail_cutoff = max(1, int(0.1 * n))
        sorted_hist = np.sort(hist)
        cvar = -np.mean(sorted_hist[:tail_cutoff])
        downside_component = -cvar * 0.5
        
        # Drawdown penalty — scaled
        drawdown_penalty = -drawdown * 0.5
    
    # Turnover penalty (encourages stability)
    turnover = np.sum(np.abs(weights - prev_weights)) / 2.0
    turnover_penalty = -turnover * 0.1
    
    # Concentration penalty (encourage diversification slightly)
    # Herfindahl index
    hhi = np.sum(weights ** 2)
    concentration_penalty = -hhi * 0.05
    
    # Total reward
    total = sharpe_component + downside_component + drawdown_penalty + turnover_penalty + concentration_penalty
    
    components = {
        "sharpe_component": float(sharpe_component),
        "downside_component": float(downside_component),
        "drawdown_penalty": float(drawdown_penalty),
        "turnover_penalty": float(turnover_penalty),
        "concentration_penalty": float(concentration_penalty),
    }
    
    return float(total), components, state