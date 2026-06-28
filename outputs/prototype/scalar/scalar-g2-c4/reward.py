def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize state
    state = info.get("reward_state") or {}
    
    # Rolling window for Sharpe estimation
    WINDOW = 60
    history = state.get("history", [])
    history.append(float(port_ret))
    if len(history) > WINDOW:
        history = history[-WINDOW:]
    state["history"] = history
    
    # Peak for drawdown tracking
    cumulative = state.get("cumulative", 1.0)
    cumulative *= (1.0 + float(port_ret))
    state["cumulative"] = cumulative
    
    peak = state.get("peak", 1.0)
    peak = max(peak, cumulative)
    state["peak"] = peak
    
    drawdown = (peak - cumulative) / (peak + 1e-8)
    
    n = len(history)
    
    if n < 5:
        # Warm-up: just use raw return, lightly scaled
        total = float(port_ret) * 10.0
        components = {"port_ret": float(port_ret), "sharpe_term": 0.0, "dd_penalty": 0.0}
        return total, components, state
    
    arr = np.array(history)
    mean_r = np.mean(arr)
    std_r = np.std(arr) + 1e-8
    
    # Annualized Sharpe (daily steps assumed, ~252 trading days)
    sharpe = mean_r / std_r * np.sqrt(252)
    
    # Rolling Sharpe as primary reward signal
    sharpe_term = np.clip(sharpe, -3.0, 3.0)
    
    # Drawdown penalty - penalize being in drawdown
    dd_penalty = -drawdown * 2.0
    
    # Tail risk: penalize large negative returns (CVaR-like)
    if n >= 20:
        sorted_r = np.sort(arr)
        cvar_cutoff = max(1, int(0.1 * n))
        cvar = np.mean(sorted_r[:cvar_cutoff])
        tail_penalty = np.clip(cvar * 20.0, -2.0, 0.0)
    else:
        tail_penalty = 0.0
    
    # Concentration penalty: encourage diversification slightly
    # Herfindahl index for non-cash weights
    hhi = np.sum(weights ** 2)
    concentration_penalty = -0.1 * hhi
    
    total = sharpe_term + dd_penalty + tail_penalty + concentration_penalty
    
    components = {
        "sharpe_term": float(sharpe_term),
        "dd_penalty": float(dd_penalty),
        "tail_penalty": float(tail_penalty),
        "concentration_penalty": float(concentration_penalty),
        "port_ret": float(port_ret),
        "drawdown": float(drawdown),
    }
    
    return float(total), components, state