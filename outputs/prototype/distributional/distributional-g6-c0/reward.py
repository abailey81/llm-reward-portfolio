def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get("reward_state")
    
    # Initialize state
    if state is None:
        state = {
            "ret_history": [],
            "peak": 0.0,
            "cum_ret": 0.0,
            "step": 0,
        }
    
    ret_history = state["ret_history"]
    peak = state["peak"]
    cum_ret = state["cum_ret"]
    step = state["step"]
    
    # Update cumulative return and drawdown tracking
    cum_ret = cum_ret + port_ret
    peak = max(peak, cum_ret)
    drawdown = peak - cum_ret  # always >= 0
    
    # Store return
    ret_history.append(port_ret)
    
    # Rolling window for statistics
    window = 60
    if len(ret_history) > window:
        ret_history = ret_history[-window:]
    
    ret_arr = np.array(ret_history)
    n = len(ret_arr)
    
    # --- Component 1: Sharpe-like signal (online) ---
    if n >= 5:
        mu = np.mean(ret_arr)
        sigma = np.std(ret_arr) + 1e-8
        sharpe_approx = mu / sigma
    else:
        sharpe_approx = 0.0
    
    # --- Component 2: CVaR penalty (rolling) ---
    if n >= 10:
        # 5th percentile tail
        threshold_5 = np.percentile(ret_arr, 5)
        tail_returns_5 = ret_arr[ret_arr <= threshold_5]
        cvar_5 = np.mean(tail_returns_5) if len(tail_returns_5) > 0 else threshold_5
        
        # 10th percentile tail
        threshold_10 = np.percentile(ret_arr, 10)
        tail_returns_10 = ret_arr[ret_arr <= threshold_10]
        cvar_10 = np.mean(tail_returns_10) if len(tail_returns_10) > 0 else threshold_10
        
        # Combined CVaR penalty (penalize bad tail)
        cvar_penalty = 0.6 * cvar_5 + 0.4 * cvar_10  # negative values → penalty
    else:
        cvar_penalty = 0.0
    
    # --- Component 3: Drawdown penalty ---
    # Penalize current drawdown level
    dd_penalty = -drawdown
    
    # --- Component 4: Downside deviation (Sortino-like) ---
    if n >= 5:
        downside = ret_arr[ret_arr < 0]
        if len(downside) > 0:
            downside_dev = np.sqrt(np.mean(downside ** 2)) + 1e-8
            sortino_approx = np.mean(ret_arr) / downside_dev
        else:
            sortino_approx = sharpe_approx
    else:
        sortino_approx = 0.0
    
    # --- Component 5: Turnover cost signal ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.5 * turnover
    
    # --- Combine components ---
    # Primary: blend Sharpe and Sortino for stability
    ret_quality = 0.4 * sharpe_approx + 0.6 * sortino_approx
    
    # Scale factors tuned to keep signals in similar magnitude
    w_ret_quality = 0.50
    w_cvar = 1.5
    w_dd = 0.3
    w_turnover = 0.1
    
    total = (
        w_ret_quality * ret_quality
        + w_cvar * cvar_penalty        # cvar_penalty already negative for losses
        + w_dd * dd_penalty
        + w_turnover * turnover_penalty
    )
    
    step += 1
    state = {
        "ret_history": ret_history,
        "peak": peak,
        "cum_ret": cum_ret,
        "step": step,
    }
    
    components = {
        "sharpe_approx": sharpe_approx,
        "sortino_approx": sortino_approx,
        "cvar_penalty": cvar_penalty,
        "dd_penalty": dd_penalty,
        "turnover_penalty": turnover_penalty,
        "total": total,
    }
    
    return float(total), components, state