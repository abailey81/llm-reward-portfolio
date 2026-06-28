def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get("reward_state", None)
    
    # Initialize state
    if state is None:
        state = {
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "peak": 1.0,
            "cum_value": 1.0,
            "alpha": 0.05,   # EMA decay: ~20-step memory
            "n": 0,
        }
    
    alpha = state["alpha"]
    n = state["n"] + 1
    state["n"] = n
    
    # Blend alpha: faster adaptation early, then stabilize
    eff_alpha = max(alpha, 1.0 / n)
    
    # Update EMA of returns and squared returns
    state["ema_ret"] = (1 - eff_alpha) * state["ema_ret"] + eff_alpha * port_ret
    state["ema_sq"]  = (1 - eff_alpha) * state["ema_sq"]  + eff_alpha * (port_ret ** 2)
    
    ema_ret = state["ema_ret"]
    ema_sq  = state["ema_sq"]
    
    # EMA variance (unbiased-ish)
    ema_var = max(ema_sq - ema_ret ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)
    
    # Sharpe-like signal (annualize later if needed, keep simple)
    sharpe_signal = ema_ret / ema_std
    
    # Drawdown penalty
    state["cum_value"] = state["cum_value"] * (1.0 + port_ret)
    state["peak"] = max(state["peak"], state["cum_value"])
    drawdown = (state["peak"] - state["cum_value"]) / (state["peak"] + 1e-8)
    drawdown_penalty = drawdown ** 2  # quadratic penalty for deep drawdowns
    
    # Turnover penalty (beyond what's already in port_ret costs)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.1 * turnover
    
    # Concentration penalty (encourage diversification)
    herfindahl = np.sum(weights ** 2)
    concentration_penalty = 0.05 * herfindahl
    
    # Tail loss: direct step loss penalty (downside emphasis)
    tail_penalty = 0.5 * min(port_ret, 0.0) ** 2 / (ema_var + 1e-8)
    
    # Total reward
    total = (
        sharpe_signal
        - drawdown_penalty
        - turnover_penalty
        - concentration_penalty
        - tail_penalty
    )
    
    components = {
        "sharpe_signal":        sharpe_signal,
        "drawdown_penalty":     -drawdown_penalty,
        "turnover_penalty":     -turnover_penalty,
        "concentration_penalty":-concentration_penalty,
        "tail_penalty":         -tail_penalty,
    }
    
    return float(total), components, state