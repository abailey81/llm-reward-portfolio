def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize state ---
    state = info.get("reward_state") or {}
    
    # Running statistics for online Sharpe
    n = state.get("n", 0)
    mean_ret = state.get("mean_ret", 0.0)
    m2_ret = state.get("m2_ret", 0.0)  # sum of squared deviations
    
    # Drawdown tracking
    peak = state.get("peak", 1.0)
    cum_value = state.get("cum_value", 1.0)
    
    # Recent returns for tail risk (keep last 60 steps)
    recent_rets = state.get("recent_rets", [])
    
    # --- Update portfolio value and drawdown ---
    cum_value = cum_value * (1.0 + port_ret)
    peak = max(peak, cum_value)
    drawdown = (peak - cum_value) / (peak + 1e-8)
    
    # --- Online Welford mean/variance update ---
    n += 1
    delta = port_ret - mean_ret
    mean_ret += delta / n
    delta2 = port_ret - mean_ret
    m2_ret += delta * delta2
    
    variance = m2_ret / n if n > 1 else 1e-6
    std_ret = np.sqrt(max(variance, 1e-10))
    
    # Online Sharpe (annualized approximation, daily steps assumed)
    sharpe = (mean_ret / std_ret) if std_ret > 1e-8 else 0.0
    
    # --- Recent returns for CVaR-like tail penalty ---
    recent_rets.append(port_ret)
    if len(recent_rets) > 60:
        recent_rets = recent_rets[-60:]
    
    arr = np.array(recent_rets)
    if len(arr) >= 10:
        var_5 = np.percentile(arr, 5)
        # CVaR: mean of returns below VaR
        tail = arr[arr <= var_5]
        cvar = float(np.mean(tail)) if len(tail) > 0 else var_5
    else:
        cvar = min(port_ret, 0.0)
    
    # --- Turnover penalty ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = 0.1 * turnover
    
    # --- Concentration penalty (encourage diversification) ---
    # Herfindahl index penalizes concentration
    hhi = float(np.sum(weights ** 2))
    concentration_penalty = 0.05 * hhi
    
    # --- Compose reward ---
    # Core: realized return
    ret_component = port_ret
    
    # Sharpe bonus (scaled down, builds over time)
    sharpe_component = 0.3 * np.tanh(sharpe) if n >= 20 else 0.0
    
    # Drawdown penalty
    drawdown_penalty = 0.5 * drawdown * drawdown  # quadratic
    
    # Tail risk penalty
    tail_penalty = 0.2 * max(-cvar, 0.0)
    
    total = (
        ret_component
        + sharpe_component
        - drawdown_penalty
        - tail_penalty
        - turnover_penalty
        - concentration_penalty
    )
    
    components = {
        "ret": ret_component,
        "sharpe_bonus": float(sharpe_component),
        "drawdown_penalty": float(-drawdown_penalty),
        "tail_penalty": float(-tail_penalty),
        "turnover_penalty": float(-turnover_penalty),
        "concentration_penalty": float(-concentration_penalty),
        "drawdown": float(drawdown),
        "online_sharpe": float(sharpe),
    }
    
    reward_state = {
        "n": n,
        "mean_ret": mean_ret,
        "m2_ret": m2_ret,
        "peak": peak,
        "cum_value": cum_value,
        "recent_rets": recent_rets,
    }
    
    return float(total), components, reward_state