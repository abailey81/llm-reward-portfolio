def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get("reward_state") or {}
    
    # --- Unpack state ---
    ret_history = state.get("ret_history", [])
    peak = state.get("peak", 1.0)
    cumulative = state.get("cumulative", 1.0)
    
    # Update cumulative and drawdown tracking
    cumulative = cumulative * (1.0 + port_ret)
    peak = max(peak, cumulative)
    drawdown = (peak - cumulative) / (peak + 1e-8)
    
    # Add current return to history
    ret_history.append(port_ret)
    # Keep a rolling window
    window = 120
    if len(ret_history) > window:
        ret_history = ret_history[-window:]
    
    hist = np.array(ret_history)
    n = len(hist)
    
    # --- Base return signal ---
    base = port_ret
    
    # --- Online Sharpe component ---
    if n >= 8:
        mu = np.mean(hist)
        sigma = np.std(hist, ddof=1) + 1e-8
        sharpe_contrib = mu / sigma * 0.1
    else:
        sharpe_contrib = 0.0
    
    # --- CVaR penalty (rolling) ---
    if n >= 16:
        sorted_rets = np.sort(hist)
        # 5% CVaR
        cutoff_5 = max(1, int(np.floor(0.05 * n)))
        cvar_5 = np.mean(sorted_rets[:cutoff_5])
        # 10% CVaR
        cutoff_10 = max(1, int(np.floor(0.10 * n)))
        cvar_10 = np.mean(sorted_rets[:cutoff_10])
        # Penalize tail losses (cvar is negative, so penalty > 0 when bad)
        cvar_penalty = -0.3 * cvar_5 - 0.2 * cvar_10
    else:
        cvar_penalty = 0.0
    
    # --- Drawdown penalty ---
    dd_penalty = 0.5 * (drawdown ** 1.5)
    
    # --- Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.05 * turnover
    
    # --- Concentration penalty (encourage diversification) ---
    # Penalize extreme concentration (but allow some)
    hhi = np.sum(weights ** 2)
    n_assets = len(weights)
    min_hhi = 1.0 / n_assets
    concentration_penalty = 0.1 * (hhi - min_hhi)
    
    # --- Downside deviation penalty (current step) ---
    downside = min(0.0, port_ret)  # only penalize losses
    downside_penalty = -1.5 * downside  # positive penalty for losses
    
    # --- Combine ---
    total = (
        base
        + sharpe_contrib
        - cvar_penalty
        - dd_penalty
        - turnover_penalty
        - concentration_penalty
        - downside_penalty * 0.3
    )
    
    components = {
        "base": base,
        "sharpe_contrib": sharpe_contrib,
        "cvar_penalty": -cvar_penalty,
        "dd_penalty": -dd_penalty,
        "turnover_penalty": -turnover_penalty,
        "concentration_penalty": -concentration_penalty,
        "downside_penalty": -downside_penalty * 0.3,
        "drawdown": drawdown,
    }
    
    reward_state = {
        "ret_history": ret_history,
        "peak": peak,
        "cumulative": cumulative,
    }
    
    return float(total), components, reward_state