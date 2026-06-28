def reward(weights, returns, prev_weights, port_ret, info):
    reward_state = info.get("reward_state", None)
    
    # Initialize state
    if reward_state is None:
        reward_state = {
            "ret_history": [],
            "peak": 1.0,
            "cumulative": 1.0,
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "ema_alpha": 0.05,  # smoothing factor
            "step": 0,
        }
    
    state = reward_state
    state["step"] += 1
    alpha = state["ema_alpha"]
    
    # Update cumulative value and drawdown
    state["cumulative"] *= (1.0 + port_ret)
    state["peak"] = max(state["peak"], state["cumulative"])
    drawdown = (state["cumulative"] - state["peak"]) / state["peak"]  # <= 0
    
    # Keep a rolling window of returns for tail estimation
    state["ret_history"].append(port_ret)
    max_history = 200
    if len(state["ret_history"]) > max_history:
        state["ret_history"].pop(0)
    
    hist = np.array(state["ret_history"])
    n = len(hist)
    
    # Online EMA-based Sharpe
    state["ema_ret"] = (1 - alpha) * state["ema_ret"] + alpha * port_ret
    state["ema_sq"] = (1 - alpha) * state["ema_sq"] + alpha * port_ret**2
    ema_var = state["ema_sq"] - state["ema_ret"]**2
    ema_std = np.sqrt(max(ema_var, 1e-8))
    sharpe_signal = state["ema_ret"] / ema_std
    
    # CVaR penalty: mean of worst quantile of recent returns
    if n >= 20:
        sorted_hist = np.sort(hist)
        # CVaR at 5% level
        cvar5_k = max(1, int(np.floor(0.05 * n)))
        cvar5 = np.mean(sorted_hist[:cvar5_k])
        # CVaR at 10% level
        cvar10_k = max(1, int(np.floor(0.10 * n)))
        cvar10 = np.mean(sorted_hist[:cvar10_k])
        cvar_penalty = 0.5 * cvar5 + 0.5 * cvar10  # negative values
    else:
        cvar_penalty = 0.0
    
    # Skewness penalty (penalize negative skew)
    if n >= 20:
        mean_h = np.mean(hist)
        std_h = np.std(hist) + 1e-8
        skew = np.mean(((hist - mean_h) / std_h)**3)
        skew_penalty = min(skew, 0.0)  # only penalize negative skew
    else:
        skew = 0.0
        skew_penalty = 0.0
    
    # Drawdown penalty (quadratic to be more aggressive for large drawdowns)
    dd_penalty = drawdown - 2.0 * drawdown**2  # drawdown <= 0, so this is <= 0
    
    # Turnover penalty
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.5 * turnover
    
    # Concentration penalty (encourage some diversification)
    # Herfindahl index on non-cash weights
    hhi = np.sum(weights**2)
    concentration_penalty = -0.1 * hhi
    
    # Compose total reward
    # Primary: Sharpe signal (scaled)
    # Secondary: tail risk penalties
    w_sharpe = 1.0
    w_cvar = 3.0
    w_dd = 1.5
    w_skew = 0.3
    
    total = (
        w_sharpe * sharpe_signal
        + w_cvar * cvar_penalty
        + w_dd * dd_penalty
        + w_skew * skew_penalty
        + turnover_penalty
        + concentration_penalty
    )
    
    components = {
        "sharpe_signal": float(w_sharpe * sharpe_signal),
        "cvar_penalty": float(w_cvar * cvar_penalty),
        "dd_penalty": float(w_dd * dd_penalty),
        "skew_penalty": float(w_skew * skew_penalty),
        "turnover_penalty": float(turnover_penalty),
        "concentration_penalty": float(concentration_penalty),
        "port_ret": float(port_ret),
        "drawdown": float(drawdown),
    }
    
    return float(total), components, state