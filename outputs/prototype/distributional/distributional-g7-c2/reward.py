def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get("reward_state")
    
    if state is None:
        state = {
            "ret_history": [],
            "peak": 0.0,
            "cum_ret": 0.0,
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "ema_alpha": 0.05,
            "step": 0,
        }
    
    step = state["step"] + 1
    alpha = state["ema_alpha"]
    
    # Update EMA of returns and squared returns
    ema_ret = alpha * port_ret + (1 - alpha) * state["ema_ret"]
    ema_sq  = alpha * (port_ret ** 2) + (1 - alpha) * state["ema_sq"]
    
    # Online Sharpe estimate
    ema_var = max(ema_sq - ema_ret ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)
    sharpe_signal = ema_ret / ema_std
    
    # Keep a rolling window of returns for tail estimates
    history = state["ret_history"] + [port_ret]
    if len(history) > 200:
        history = history[-200:]
    
    ret_arr = np.array(history)
    
    # CVaR penalty: penalize expected loss in worst 5% of steps
    if len(ret_arr) >= 20:
        threshold = np.percentile(ret_arr, 5)
        tail_returns = ret_arr[ret_arr <= threshold]
        cvar_5 = np.mean(tail_returns) if len(tail_returns) > 0 else 0.0
        cvar_penalty = -min(cvar_5, 0.0)  # positive penalty for losses
    else:
        cvar_penalty = 0.0
    
    # Drawdown penalty
    state["cum_ret"] = state["cum_ret"] + port_ret
    peak = max(state["peak"], state["cum_ret"])
    drawdown = peak - state["cum_ret"]  # >= 0
    dd_penalty = drawdown * 0.5
    
    # Asymmetric return component: downside gets penalized more
    if port_ret < 0:
        asym_ret = 2.0 * port_ret   # amplify losses
    else:
        asym_ret = port_ret
    
    # Turnover penalty to reduce transaction costs
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.002 * turnover
    
    # Combine components
    w_sharpe    = 1.0
    w_cvar      = 3.0
    w_dd        = 0.5
    w_asym      = 2.0
    
    total = (
        w_sharpe * sharpe_signal
        + w_asym * asym_ret
        - w_cvar * cvar_penalty
        - w_dd  * dd_penalty
        - turnover_penalty
    )
    
    components = {
        "sharpe_signal":  float(w_sharpe * sharpe_signal),
        "asym_ret":       float(w_asym * asym_ret),
        "cvar_penalty":   float(-w_cvar * cvar_penalty),
        "dd_penalty":     float(-w_dd * dd_penalty),
        "turnover_pen":   float(-turnover_penalty),
    }
    
    state["ema_ret"]      = ema_ret
    state["ema_sq"]       = ema_sq
    state["ret_history"]  = history
    state["peak"]         = peak
    state["step"]         = step
    
    return float(total), components, state