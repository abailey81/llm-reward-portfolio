def reward(weights, returns, prev_weights, port_ret, info):
    reward_state = info.get("reward_state", None)
    
    # Initialize state
    if reward_state is None:
        reward_state = {
            "ret_history": [],
            "peak": 1.0,
            "cumulative": 1.0,
            "ema_mean": 0.0,
            "ema_var": 1e-6,
            "step": 0,
        }
    
    rs = reward_state
    rs["step"] += 1
    step = rs["step"]
    
    # Update cumulative return and drawdown tracking
    rs["cumulative"] *= (1.0 + port_ret)
    rs["peak"] = max(rs["peak"], rs["cumulative"])
    drawdown = (rs["cumulative"] - rs["peak"]) / (rs["peak"] + 1e-8)
    
    # EMA-based mean and variance (fast adaptation)
    alpha = 0.05  # decay factor
    rs["ema_mean"] = (1 - alpha) * rs["ema_mean"] + alpha * port_ret
    rs["ema_var"] = (1 - alpha) * rs["ema_var"] + alpha * (port_ret - rs["ema_mean"]) ** 2
    ema_std = np.sqrt(rs["ema_var"] + 1e-8)
    
    # Keep rolling window of returns for CVaR
    rs["ret_history"].append(port_ret)
    if len(rs["ret_history"]) > 200:
        rs["ret_history"].pop(0)
    
    ret_arr = np.array(rs["ret_history"])
    
    # --- Components ---
    
    # 1. Sharpe-like signal using EMA stats
    sharpe_signal = (rs["ema_mean"] / ema_std) * 0.01  # scale down
    
    # 2. CVaR penalty (5% tail)
    cvar_penalty = 0.0
    if len(ret_arr) >= 20:
        tail_cutoff = np.percentile(ret_arr, 5)
        tail_returns = ret_arr[ret_arr <= tail_cutoff]
        cvar = np.mean(tail_returns) if len(tail_returns) > 0 else tail_cutoff
        cvar_penalty = -2.0 * max(0.0, -cvar)  # penalize negative CVaR
    
    # 3. Drawdown penalty
    drawdown_penalty = 2.0 * drawdown  # drawdown is negative, so this adds negative signal
    
    # 4. Direct return signal (scaled)
    ret_signal = port_ret * 10.0
    
    # 5. Concentration penalty (encourage diversification)
    n_assets = len(weights)
    hhi = np.sum(weights ** 2)
    max_hhi = 1.0
    min_hhi = 1.0 / n_assets
    concentration_penalty = -0.1 * (hhi - min_hhi) / (max_hhi - min_hhi + 1e-8)
    
    # 6. Left-tail penalty for current step
    current_tail_penalty = 0.0
    if port_ret < -0.01:
        current_tail_penalty = -1.0 * (port_ret ** 2) * 50.0  # quadratic penalty for large losses
    
    total = (
        ret_signal
        + sharpe_signal
        + cvar_penalty
        + drawdown_penalty
        + concentration_penalty
        + current_tail_penalty
    )
    
    components = {
        "ret_signal": ret_signal,
        "sharpe_signal": sharpe_signal,
        "cvar_penalty": cvar_penalty,
        "drawdown_penalty": drawdown_penalty,
        "concentration_penalty": concentration_penalty,
        "current_tail_penalty": current_tail_penalty,
    }
    
    return float(total), components, rs