def reward(weights, returns, prev_weights, port_ret, info):
    reward_state = info.get("reward_state", None)
    
    # Initialize state
    if reward_state is None:
        reward_state = {
            "returns_window": [],
            "peak_value": 1.0,
            "cumulative_value": 1.0,
            "step_count": 0,
        }
    
    # Update state
    rs = reward_state
    rs["step_count"] += 1
    rs["cumulative_value"] *= (1.0 + port_ret)
    rs["peak_value"] = max(rs["peak_value"], rs["cumulative_value"])
    
    # Maintain a rolling window of returns for risk estimates
    window_size = 120
    rs["returns_window"].append(port_ret)
    if len(rs["returns_window"]) > window_size:
        rs["returns_window"].pop(0)
    
    ret_arr = np.array(rs["returns_window"])
    n = len(ret_arr)
    
    # --- Component 1: Base return signal ---
    base_return = port_ret
    
    # --- Component 2: Online Sharpe (annualized proxy) ---
    if n >= 5:
        mu = np.mean(ret_arr)
        sigma = np.std(ret_arr) + 1e-8
        sharpe_signal = mu / sigma
    else:
        sharpe_signal = 0.0
    
    # --- Component 3: CVaR penalty (tail risk) ---
    if n >= 10:
        sorted_rets = np.sort(ret_arr)
        # 5% CVaR
        cvar_idx_5 = max(1, int(np.floor(0.05 * n)))
        cvar_5 = np.mean(sorted_rets[:cvar_idx_5])
        # 10% CVaR
        cvar_idx_10 = max(1, int(np.floor(0.10 * n)))
        cvar_10 = np.mean(sorted_rets[:cvar_idx_10])
        # Weighted tail penalty
        cvar_penalty = 0.6 * cvar_5 + 0.4 * cvar_10
    else:
        cvar_penalty = 0.0
    
    # --- Component 4: Drawdown penalty ---
    drawdown = (rs["cumulative_value"] - rs["peak_value"]) / (rs["peak_value"] + 1e-8)
    # Convex drawdown penalty — hurts more as drawdown deepens
    dd_penalty = drawdown * abs(drawdown)
    
    # --- Component 5: Turnover cost (already in port_ret but add regularization) ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.0005 * turnover
    
    # --- Component 6: Concentration penalty (encourage diversification) ---
    # Herfindahl index on risky asset weights (exclude cash = last element)
    risky_w = weights[:-1] if len(weights) > 1 else weights
    herfindahl = np.sum(risky_w ** 2)
    concentration_penalty = -0.002 * herfindahl
    
    # --- Adaptive weighting based on step count ---
    # Early steps: rely more on return; later: rely more on risk-adjusted metrics
    warmup = 30
    if rs["step_count"] < warmup:
        alpha_sharpe = 0.0
        alpha_cvar = 0.0
    else:
        alpha_sharpe = 1.0
        alpha_cvar = 1.0
    
    # --- Combine components ---
    total = (
        0.4  * base_return
        + 0.4  * alpha_sharpe * sharpe_signal * 0.01  # scale sharpe to return units
        + 0.5  * alpha_cvar   * cvar_penalty
        + 0.3  * dd_penalty
        + turnover_penalty
        + concentration_penalty
    )
    
    components = {
        "base_return":          base_return,
        "sharpe_signal":        alpha_sharpe * sharpe_signal * 0.01,
        "cvar_penalty":         alpha_cvar * cvar_penalty,
        "drawdown_penalty":     dd_penalty,
        "turnover_penalty":     turnover_penalty,
        "concentration_penalty": concentration_penalty,
    }
    
    return float(total), components, rs