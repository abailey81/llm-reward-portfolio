def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state") or {}
    
    # Rolling window for statistics
    WINDOW = 60
    
    # --- Retrieve state ---
    ret_history = state.get("ret_history", [])
    peak = state.get("peak", 1.0)
    cumulative = state.get("cumulative", 1.0)
    
    # --- Update cumulative value and drawdown ---
    cumulative = cumulative * (1.0 + port_ret)
    peak = max(peak, cumulative)
    drawdown = (cumulative - peak) / (peak + 1e-8)  # <= 0
    
    # --- Update return history ---
    ret_history.append(port_ret)
    if len(ret_history) > WINDOW:
        ret_history = ret_history[-WINDOW:]
    
    ret_arr = np.array(ret_history)
    n = len(ret_arr)
    
    # --- Sharpe component (annualized direction, not scale) ---
    if n >= 5:
        mu = np.mean(ret_arr)
        sigma = np.std(ret_arr, ddof=1) + 1e-8
        sharpe = mu / sigma  # per-step Sharpe
    else:
        mu = port_ret
        sigma = 1e-8
        sharpe = 0.0
    
    # --- CVaR penalty (Expected Shortfall at 5%) ---
    if n >= 10:
        cutoff = max(1, int(np.floor(0.05 * n)))
        sorted_rets = np.sort(ret_arr)
        cvar = np.mean(sorted_rets[:cutoff])  # mean of worst 5%
    else:
        cvar = min(port_ret, 0.0)
    
    # CVaR penalty: penalize negative tail, reward positive
    cvar_penalty = cvar  # already negative when bad
    
    # --- Drawdown penalty ---
    # Penalize current drawdown level
    drawdown_penalty = drawdown  # <= 0
    
    # --- Concentration penalty (encourage diversification) ---
    # Herfindahl index: sum of squared weights, normalized
    n_assets = len(weights)
    hhi = np.sum(weights ** 2)
    # Normalize: 1/n_assets (fully diversified) to 1 (concentrated)
    hhi_min = 1.0 / max(n_assets, 1)
    concentration = (hhi - hhi_min) / (1.0 - hhi_min + 1e-8)
    concentration_penalty = -concentration  # <= 0
    
    # --- Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -turnover
    
    # --- Combine components ---
    # Primary: Sharpe-like signal
    # Secondary: tail risk and drawdown management
    w_sharpe = 1.0
    w_cvar = 2.0        # heavy weight on tail risk
    w_drawdown = 1.5    # penalize drawdowns
    w_concentration = 0.3
    w_turnover = 0.1
    
    total = (
        w_sharpe * sharpe
        + w_cvar * cvar_penalty
        + w_drawdown * drawdown_penalty
        + w_concentration * concentration_penalty
        + w_turnover * turnover_penalty
    )
    
    components = {
        "sharpe_component": float(w_sharpe * sharpe),
        "cvar_penalty": float(w_cvar * cvar_penalty),
        "drawdown_penalty": float(w_drawdown * drawdown_penalty),
        "concentration_penalty": float(w_concentration * concentration_penalty),
        "turnover_penalty": float(w_turnover * turnover_penalty),
        "port_ret": float(port_ret),
        "drawdown": float(drawdown),
        "cvar": float(cvar),
    }
    
    reward_state = {
        "ret_history": ret_history,
        "peak": peak,
        "cumulative": cumulative,
    }
    
    return float(total), components, reward_state