def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get("reward_state")
    
    # Initialize state
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cum_ret": 1.0,
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "ema_alpha": 0.06,  # ~16-step halflife
            "step": 0,
        }
    
    step = state["step"] + 1
    alpha = state["ema_alpha"]
    
    # Update EMA of returns and squared returns (online Sharpe)
    ema_ret = alpha * port_ret + (1 - alpha) * state["ema_ret"]
    ema_sq  = alpha * (port_ret ** 2) + (1 - alpha) * state["ema_sq"]
    
    # Rolling return history for CVaR (keep last 100 steps)
    ret_history = state["ret_history"] + [port_ret]
    if len(ret_history) > 100:
        ret_history = ret_history[-100:]
    
    # ---- Component 1: EMA-Sharpe ----
    var_est = max(ema_sq - ema_ret ** 2, 1e-8)
    std_est = np.sqrt(var_est)
    sharpe_reward = ema_ret / std_est if step > 5 else 0.0
    
    # ---- Component 2: CVaR penalty (tail risk) ----
    cvar_penalty = 0.0
    if len(ret_history) >= 10:
        arr = np.array(ret_history)
        # CVaR at 10% level
        threshold_10 = np.percentile(arr, 10)
        tail_10 = arr[arr <= threshold_10]
        cvar_10 = float(np.mean(tail_10)) if len(tail_10) > 0 else 0.0
        
        # CVaR at 5% level
        threshold_5 = np.percentile(arr, 5)
        tail_5 = arr[arr <= threshold_5]
        cvar_5 = float(np.mean(tail_5)) if len(tail_5) > 0 else 0.0
        
        # Penalize negative CVaR values (tail losses)
        cvar_penalty = 2.0 * min(cvar_10, 0.0) + 1.0 * min(cvar_5, 0.0)
    
    # ---- Component 3: Drawdown penalty ----
    cum_ret = state["cum_ret"] * (1.0 + port_ret)
    peak = max(state["peak"], cum_ret)
    drawdown = (cum_ret - peak) / max(peak, 1e-8)  # <= 0
    dd_penalty = 1.5 * drawdown  # proportional penalty
    
    # ---- Component 4: Turnover penalty ----
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = -0.05 * turnover
    
    # ---- Component 5: Direct return signal (small) ----
    # Softplus-like: reward positive returns, penalize negative asymmetrically
    if port_ret >= 0:
        ret_signal = 0.5 * port_ret
    else:
        ret_signal = 1.5 * port_ret  # stronger penalty for losses
    
    # ---- Component 6: Concentration penalty ----
    # Discourage extreme concentration (encourage diversification)
    hhi = float(np.sum(weights ** 2))
    concentration_penalty = -0.1 * max(hhi - 0.3, 0.0)
    
    # ---- Combine ----
    total = (
        sharpe_reward
        + cvar_penalty
        + dd_penalty
        + turnover_penalty
        + ret_signal
        + concentration_penalty
    )
    
    components = {
        "sharpe_reward": float(sharpe_reward),
        "cvar_penalty": float(cvar_penalty),
        "dd_penalty": float(dd_penalty),
        "turnover_penalty": float(turnover_penalty),
        "ret_signal": float(ret_signal),
        "concentration_penalty": float(concentration_penalty),
    }
    
    state["ema_ret"] = ema_ret
    state["ema_sq"] = ema_sq
    state["ret_history"] = ret_history
    state["cum_ret"] = cum_ret
    state["peak"] = peak
    state["step"] = step
    
    return float(total), components, state