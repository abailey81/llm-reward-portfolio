def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize state
    state = info.get("reward_state") or {}
    
    # Unpack state with defaults
    ret_history = state.get("ret_history", [])
    peak = state.get("peak", 1.0)
    equity = state.get("equity", 1.0)
    
    # Update equity curve
    equity = equity * (1.0 + port_ret)
    peak = max(peak, equity)
    drawdown = (peak - equity) / peak
    
    # Store return
    ret_history.append(port_ret)
    # Keep a rolling window
    window = 60
    if len(ret_history) > window:
        ret_history = ret_history[-window:]
    
    ret_arr = np.array(ret_history)
    n = len(ret_arr)
    
    # --- Component 1: Base return signal ---
    base_return = port_ret
    
    # --- Component 2: Online Sharpe (annualized approximation) ---
    if n >= 5:
        mu = np.mean(ret_arr)
        sigma = np.std(ret_arr, ddof=1) + 1e-8
        sharpe = mu / sigma  # step-level Sharpe
    else:
        sharpe = 0.0
    
    # --- Component 3: CVaR penalty ---
    # Penalize expected tail loss (worst 10% of observed returns)
    if n >= 10:
        tail_cutoff = int(np.floor(0.10 * n))
        tail_cutoff = max(1, tail_cutoff)
        sorted_rets = np.sort(ret_arr)
        cvar = np.mean(sorted_rets[:tail_cutoff])  # mean of worst returns
        cvar_penalty = min(0.0, cvar)  # only penalize negative CVaR
    else:
        cvar_penalty = min(0.0, port_ret)
    
    # --- Component 4: Drawdown penalty ---
    # Penalize large drawdowns non-linearly
    dd_penalty = -(drawdown ** 2)
    
    # --- Component 5: Concentration penalty (Herfindahl) ---
    # Penalize extreme concentration (but allow some focus)
    hhi = np.sum(weights ** 2)
    n_assets = len(weights)
    # Normalize: max HHI = 1 (all in one), min = 1/n
    hhi_excess = hhi - 1.0 / n_assets
    concentration_penalty = -hhi_excess * 0.5
    
    # --- Component 6: Turnover cost penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -turnover * 0.005  # small penalty for excessive trading
    
    # --- Combine components ---
    # Weight Sharpe heavily, add return, penalize tail risk and drawdown
    w_sharpe = 0.5
    w_return = 0.3
    w_cvar = 0.4
    w_dd = 0.2
    w_conc = 0.1
    w_turn = 0.1
    
    total = (w_return * base_return
             + w_sharpe * sharpe
             + w_cvar * cvar_penalty
             + w_dd * dd_penalty
             + w_conc * concentration_penalty
             + w_turn * turnover_penalty)
    
    components = {
        "base_return": base_return,
        "sharpe": sharpe,
        "cvar_penalty": cvar_penalty,
        "dd_penalty": dd_penalty,
        "concentration_penalty": concentration_penalty,
        "turnover_penalty": turnover_penalty,
    }
    
    reward_state = {
        "ret_history": ret_history,
        "peak": peak,
        "equity": equity,
    }
    
    return float(total), components, reward_state