def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state") or {}
    
    # Rolling window of portfolio returns (for risk estimation)
    window = state.get("window", [])
    peak = state.get("peak", 1.0)
    equity = state.get("equity", 1.0)
    
    # Update equity curve
    equity = equity * (1.0 + port_ret)
    peak = max(peak, equity)
    
    # Track returns in window (max 60 steps)
    window = window + [port_ret]
    if len(window) > 60:
        window = window[-60:]
    
    n = len(window)
    ret_arr = np.array(window)
    
    # --- Component 1: Incremental return signal ---
    ret_component = port_ret
    
    # --- Component 2: Online Sharpe (annualized approximation) ---
    if n >= 5:
        mean_r = np.mean(ret_arr)
        std_r = np.std(ret_arr) + 1e-8
        sharpe = mean_r / std_r  # per-step Sharpe
        # Scale: weight by confidence (more data = more weight)
        conf = min(n / 60.0, 1.0)
        sharpe_component = conf * sharpe
    else:
        sharpe_component = 0.0
    
    # --- Component 3: Drawdown penalty ---
    drawdown = (peak - equity) / (peak + 1e-8)
    # Penalize more severely as drawdown deepens (convex penalty)
    dd_penalty = -drawdown ** 1.5
    
    # --- Component 4: Tail risk penalty (CVaR at 10%) ---
    if n >= 10:
        tail_cutoff = max(1, int(0.10 * n))
        sorted_rets = np.sort(ret_arr)
        cvar = np.mean(sorted_rets[:tail_cutoff])  # mean of worst 10%
        tail_penalty = min(cvar, 0.0)  # only penalize negative tail
    else:
        tail_penalty = 0.0
    
    # --- Component 5: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.05 * turnover
    
    # --- Component 6: Concentration penalty (entropy-based) ---
    # Encourage diversification but don't force it
    w_clipped = np.clip(weights, 1e-8, 1.0)
    entropy = -np.sum(w_clipped * np.log(w_clipped))
    max_entropy = np.log(len(weights))
    concentration_penalty = 0.02 * (entropy / (max_entropy + 1e-8) - 1.0)
    
    # --- Combine components ---
    # Primary signal: Sharpe-based (scales with quality of returns)
    # Secondary: penalize drawdown and tail risk
    total = (
        0.3 * ret_component        # immediate return
        + 0.5 * sharpe_component   # risk-adjusted return quality
        + 0.3 * dd_penalty         # drawdown penalty
        + 0.2 * tail_penalty       # tail risk penalty
        + turnover_penalty         # transaction cost awareness
        + concentration_penalty    # mild diversification nudge
    )
    
    components = {
        "ret": ret_component,
        "sharpe": sharpe_component,
        "drawdown_penalty": dd_penalty,
        "tail_penalty": tail_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration": concentration_penalty,
    }
    
    reward_state = {
        "window": window,
        "peak": peak,
        "equity": equity,
    }
    
    return float(total), components, reward_state