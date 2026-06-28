def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state") or {}
    
    # Online return history for Sharpe estimation
    ret_history = state.get("ret_history", [])
    step = state.get("step", 0)
    
    # Append current portfolio return
    ret_history.append(port_ret)
    
    # Keep a rolling window for Sharpe estimation
    window = 252
    if len(ret_history) > window:
        ret_history = ret_history[-window:]
    
    step += 1
    
    # ---- Core Sharpe component ----
    if len(ret_history) >= 2:
        arr = np.array(ret_history, dtype=np.float64)
        mu = np.mean(arr)
        sigma = np.std(arr, ddof=1)
        # Avoid division by zero; use a small floor
        sigma_floor = 1e-8
        sharpe = mu / max(sigma, sigma_floor)
    else:
        sharpe = 0.0
    
    # ---- CVaR penalty (rolling tail risk) ----
    cvar_penalty = 0.0
    if len(ret_history) >= 20:
        arr = np.array(ret_history, dtype=np.float64)
        # 5% CVaR (Expected Shortfall)
        cutoff = int(np.floor(0.05 * len(arr)))
        cutoff = max(cutoff, 1)
        sorted_rets = np.sort(arr)
        cvar_5 = np.mean(sorted_rets[:cutoff])
        # Penalize negative tail: scale penalty to be comparable to Sharpe
        cvar_penalty = min(cvar_5, 0.0) * 20.0  # negative contribution
    
    # ---- Drawdown penalty ----
    drawdown_penalty = 0.0
    if len(ret_history) >= 2:
        arr = np.array(ret_history, dtype=np.float64)
        cum = np.cumprod(1.0 + arr)
        running_max = np.maximum.accumulate(cum)
        drawdowns = cum / running_max - 1.0
        current_dd = drawdowns[-1]
        # Penalize current drawdown (already <= 0)
        drawdown_penalty = current_dd * 5.0
    
    # ---- Concentration penalty (encourage diversification) ----
    # Gini-like: penalize extreme concentration
    n_assets = len(weights)
    if n_assets > 1:
        # Herfindahl index ranges from 1/n (equal) to 1 (concentrated)
        hhi = np.sum(weights ** 2)
        hhi_min = 1.0 / n_assets
        # Normalize to [0,1] and apply mild penalty
        hhi_norm = (hhi - hhi_min) / (1.0 - hhi_min + 1e-8)
        concentration_penalty = -0.3 * hhi_norm
    else:
        concentration_penalty = 0.0
    
    # ---- Combine ----
    # Use current step return as a direct signal scaled down,
    # plus the rolling Sharpe as the main learning target
    direct_return = port_ret * 10.0  # scale up small returns
    
    total = (
        direct_return
        + 0.5 * sharpe
        + cvar_penalty
        + drawdown_penalty
        + concentration_penalty
    )
    
    components = {
        "direct_return": direct_return,
        "sharpe": sharpe,
        "cvar_penalty": cvar_penalty,
        "drawdown_penalty": drawdown_penalty,
        "concentration_penalty": concentration_penalty,
    }
    
    reward_state = {
        "ret_history": ret_history,
        "step": step,
    }
    
    return float(total), components, reward_state