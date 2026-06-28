def reward(weights, returns, prev_weights, port_ret, info):
    reward_state = info.get("reward_state", None)
    
    # Initialize state
    if reward_state is None:
        reward_state = {
            "ret_history": [],
            "peak": 1.0,
            "cum_ret": 1.0,
            "ema_ret": 0.0,
            "ema_sq_ret": 0.0,
            "ema_neg_sq": 0.0,
            "alpha": 0.05,   # EMA decay for fast stats
            "alpha_slow": 0.02,  # slower EMA
            "step": 0,
        }
    
    rs = reward_state
    rs["step"] += 1
    alpha = rs["alpha"]
    alpha_slow = rs["alpha_slow"]
    
    # Update EMAs
    rs["ema_ret"] = (1 - alpha) * rs["ema_ret"] + alpha * port_ret
    rs["ema_sq_ret"] = (1 - alpha) * rs["ema_sq_ret"] + alpha * port_ret**2
    rs["ema_neg_sq"] = (1 - alpha) * rs["ema_neg_sq"] + alpha * min(port_ret, 0.0)**2
    
    # Keep rolling window for tail estimation (last 100 steps)
    rs["ret_history"].append(port_ret)
    if len(rs["ret_history"]) > 120:
        rs["ret_history"].pop(0)
    
    # Update cumulative return and drawdown
    rs["cum_ret"] *= (1.0 + port_ret)
    rs["peak"] = max(rs["peak"], rs["cum_ret"])
    drawdown = (rs["cum_ret"] - rs["peak"]) / (rs["peak"] + 1e-8)
    
    step = rs["step"]
    
    # --- Component 1: Sortino-style ratio ---
    ema_mean = rs["ema_ret"]
    ema_downside_var = rs["ema_neg_sq"]
    downside_std = np.sqrt(ema_downside_var + 1e-8)
    sortino = ema_mean / downside_std
    
    # --- Component 2: Tail penalty (CVaR from rolling window) ---
    tail_penalty = 0.0
    if len(rs["ret_history"]) >= 20:
        hist = np.array(rs["ret_history"])
        # CVaR at 5%
        threshold_5 = np.percentile(hist, 5)
        tail_5 = hist[hist <= threshold_5]
        cvar_5 = np.mean(tail_5) if len(tail_5) > 0 else threshold_5
        # CVaR at 10%
        threshold_10 = np.percentile(hist, 10)
        tail_10 = hist[hist <= threshold_10]
        cvar_10 = np.mean(tail_10) if len(tail_10) > 0 else threshold_10
        # Tail penalty: punish bad CVaR
        tail_penalty = 2.0 * cvar_5 + 1.0 * cvar_10
    
    # --- Component 3: Drawdown penalty ---
    dd_penalty = 3.0 * drawdown  # drawdown is negative, so this is negative penalty
    
    # --- Component 4: Concentration penalty (Herfindahl index) ---
    hhi = np.sum(weights**2)
    n = len(weights)
    hhi_normalized = (hhi - 1.0/n) / (1.0 - 1.0/n + 1e-8)
    concentration_penalty = -0.1 * hhi_normalized
    
    # --- Component 5: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.05 * turnover
    
    # --- Blend ---
    # Warmup: scale stat-based components by confidence
    warmup_scale = min(1.0, step / 30.0)
    
    # Base return signal (always present)
    base = 5.0 * port_ret
    
    # Risk-adjusted component
    risk_adj = warmup_scale * (
        0.4 * sortino
        + 1.5 * tail_penalty
        + dd_penalty
    )
    
    total = base + risk_adj + concentration_penalty + turnover_penalty
    
    components = {
        "base_return": base,
        "sortino": sortino * warmup_scale * 0.4,
        "tail_penalty": tail_penalty * 1.5 * warmup_scale,
        "drawdown_penalty": dd_penalty,
        "concentration_penalty": concentration_penalty,
        "turnover_penalty": turnover_penalty,
    }
    
    return float(total), components, rs