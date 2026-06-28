def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize state ---
    state = info.get("reward_state") or {}
    
    # Rolling window for returns history (for risk estimation)
    history = state.get("history", [])
    peak = state.get("peak", 1.0)
    nav = state.get("nav", 1.0)
    
    # Update NAV and drawdown tracking
    nav = nav * (1.0 + port_ret)
    peak = max(peak, nav)
    drawdown = (peak - nav) / (peak + 1e-8)
    
    # Append current return to history
    history.append(float(port_ret))
    # Keep a rolling window of ~60 steps
    window = 60
    if len(history) > window:
        history = history[-window:]
    
    n = len(history)
    hist_arr = np.array(history, dtype=np.float64)
    
    # --- Component 1: Sharpe-style signal ---
    if n >= 5:
        mu = np.mean(hist_arr)
        sigma = np.std(hist_arr, ddof=1) + 1e-8
        sharpe_signal = mu / sigma
    else:
        sharpe_signal = port_ret / (abs(port_ret) + 1e-4)
    
    # --- Component 2: Drawdown penalty ---
    # Penalize current drawdown non-linearly
    dd_penalty = -3.0 * (drawdown ** 1.5)
    
    # --- Component 3: CVaR tail penalty ---
    if n >= 10:
        sorted_ret = np.sort(hist_arr)
        tail_idx = max(1, int(0.1 * n))  # worst 10%
        cvar = np.mean(sorted_ret[:tail_idx])
        tail_penalty = 2.0 * min(cvar, 0.0)  # only penalize negative tail
    else:
        tail_penalty = 0.0
    
    # --- Component 4: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.5 * turnover
    
    # --- Component 5: Concentration penalty (entropy regularization) ---
    # Encourage diversification via weight entropy
    w_clipped = np.clip(weights, 1e-8, 1.0)
    entropy = -np.sum(w_clipped * np.log(w_clipped))
    max_entropy = np.log(len(weights) + 1e-8)
    # Normalized entropy bonus, mild weight
    entropy_bonus = 0.3 * (entropy / (max_entropy + 1e-8))
    
    # --- Component 6: Direct return signal (immediate feedback) ---
    # Scaled to reduce noise dominance but keep learning signal
    direct_ret = 5.0 * port_ret
    
    # --- Combine components ---
    # Primary driver: online Sharpe signal + direct return
    # Secondary: penalties for tail risk, drawdown, turnover
    total = (
        direct_ret
        + 2.0 * sharpe_signal
        + dd_penalty
        + tail_penalty
        + turnover_penalty
        + entropy_bonus
    )
    
    components = {
        "direct_ret": direct_ret,
        "sharpe_signal": sharpe_signal,
        "dd_penalty": dd_penalty,
        "tail_penalty": tail_penalty,
        "turnover_penalty": turnover_penalty,
        "entropy_bonus": entropy_bonus,
        "drawdown": drawdown,
    }
    
    reward_state = {
        "history": history,
        "peak": peak,
        "nav": nav,
    }
    
    return float(total), components, reward_state