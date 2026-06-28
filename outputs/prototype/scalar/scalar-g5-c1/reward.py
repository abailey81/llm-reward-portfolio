def reward(weights, returns, prev_weights, port_ret, info):
    # --- Retrieve or initialize state ---
    state = info.get("reward_state") or {}
    
    # Running statistics for Sharpe estimation
    ret_history = state.get("ret_history", [])
    peak = state.get("peak", 1.0)
    cumulative = state.get("cumulative", 1.0)
    
    # Update cumulative return and drawdown tracking
    cumulative = cumulative * (1.0 + port_ret)
    peak = max(peak, cumulative)
    drawdown = (peak - cumulative) / (peak + 1e-8)
    
    # Store return history (keep last 60 steps for rolling stats)
    ret_history.append(port_ret)
    if len(ret_history) > 60:
        ret_history = ret_history[-60:]
    
    n = len(ret_history)
    ret_arr = np.array(ret_history)
    
    # --- Core signal: rolling risk-adjusted return ---
    mean_ret = np.mean(ret_arr)
    std_ret = np.std(ret_arr) + 1e-8
    
    # Sharpe-like signal (annualized feel, but just directional)
    sharpe_signal = mean_ret / std_ret
    
    # --- Downside deviation (Sortino-style) ---
    downside = ret_arr[ret_arr < 0]
    if len(downside) > 1:
        downside_std = np.std(downside) + 1e-8
        sortino_signal = mean_ret / downside_std
    else:
        sortino_signal = sharpe_signal
    
    # --- Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.5 * turnover
    
    # --- Drawdown penalty (non-linear to discourage deep drawdowns) ---
    dd_penalty = 2.0 * (drawdown ** 2)
    
    # --- Tail loss penalty: CVaR approximation ---
    if n >= 10:
        var_5 = np.percentile(ret_arr, 5)
        tail_losses = ret_arr[ret_arr <= var_5]
        cvar = np.mean(tail_losses) if len(tail_losses) > 0 else var_5
        tail_penalty = max(0.0, -cvar) * 3.0
    else:
        tail_penalty = 0.0
    
    # --- Concentration penalty (encourage diversification) ---
    # Penalize Herfindahl index (sum of squares of weights)
    herfindahl = np.sum(weights ** 2)
    n_assets = len(weights)
    min_herfindahl = 1.0 / n_assets  # perfectly diversified
    concentration_penalty = 0.3 * (herfindahl - min_herfindahl)
    
    # --- Blend signals ---
    # Primary: step return (immediate feedback)
    # Secondary: rolling Sharpe (risk-adjusted trend)
    # Tertiary: Sortino (downside focus)
    
    if n < 5:
        # Warm-up: just use raw return
        core = port_ret * 10.0
    else:
        # Blend: weight toward Sortino for downside protection
        core = (
            0.4 * port_ret * 10.0 +
            0.3 * sharpe_signal +
            0.3 * sortino_signal
        )
    
    total = (
        core
        - turnover_penalty
        - dd_penalty
        - tail_penalty
        - concentration_penalty
    )
    
    components = {
        "core": core,
        "port_ret_scaled": port_ret * 10.0,
        "sharpe_signal": sharpe_signal if n >= 5 else 0.0,
        "sortino_signal": sortino_signal if n >= 5 else 0.0,
        "turnover_penalty": -turnover_penalty,
        "drawdown_penalty": -dd_penalty,
        "tail_penalty": -tail_penalty,
        "concentration_penalty": -concentration_penalty,
    }
    
    reward_state = {
        "ret_history": ret_history,
        "peak": peak,
        "cumulative": cumulative,
    }
    
    return float(total), components, reward_state