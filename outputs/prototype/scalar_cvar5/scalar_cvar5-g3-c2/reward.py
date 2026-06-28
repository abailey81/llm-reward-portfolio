def reward(weights, returns, prev_weights, port_ret, info):
    reward_state = info.get("reward_state", None)
    
    # Initialize state
    if reward_state is None:
        reward_state = {
            "returns_history": [],
            "peak_value": 1.0,
            "portfolio_value": 1.0,
            "n": 0,
            "mean": 0.0,
            "M2": 0.0,  # for online variance (Welford)
        }
    
    # Update portfolio value and peak
    portfolio_value = reward_state["portfolio_value"] * (1.0 + port_ret)
    peak_value = max(reward_state["peak_value"], portfolio_value)
    reward_state["portfolio_value"] = portfolio_value
    reward_state["peak_value"] = peak_value
    
    # Welford online mean/variance for Sharpe
    n = reward_state["n"] + 1
    delta = port_ret - reward_state["mean"]
    mean = reward_state["mean"] + delta / n
    delta2 = port_ret - mean
    M2 = reward_state["M2"] + delta * delta2
    reward_state["n"] = n
    reward_state["mean"] = mean
    reward_state["M2"] = M2
    
    # Keep rolling window of returns for CVaR
    returns_history = reward_state["returns_history"]
    returns_history.append(port_ret)
    # Keep last 252 steps (approx 1 year)
    if len(returns_history) > 252:
        returns_history.pop(0)
    reward_state["returns_history"] = returns_history
    
    # --- Component 1: Online Sharpe-based reward ---
    if n >= 2:
        variance = M2 / (n - 1)
        std = np.sqrt(variance) if variance > 1e-10 else 1e-5
        sharpe_reward = mean / std
    else:
        sharpe_reward = port_ret
    
    # --- Component 2: CVaR penalty (tail risk) ---
    cvar_penalty = 0.0
    if len(returns_history) >= 20:
        arr = np.array(returns_history)
        cutoff = np.percentile(arr, 5)
        tail = arr[arr <= cutoff]
        if len(tail) > 0:
            cvar = tail.mean()  # negative number
            cvar_penalty = min(cvar, 0.0)  # ensure non-positive
    
    # --- Component 3: Drawdown penalty ---
    if peak_value > 0:
        drawdown = (portfolio_value - peak_value) / peak_value  # <= 0
    else:
        drawdown = 0.0
    drawdown_penalty = min(drawdown, 0.0)
    
    # --- Component 4: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -turnover
    
    # --- Component 5: Concentration penalty (entropy-based) ---
    w_clipped = np.clip(weights, 1e-10, 1.0)
    entropy = -np.sum(w_clipped * np.log(w_clipped))
    max_entropy = np.log(len(weights))
    # Normalize to [0, 1] and invert for penalty (low entropy = concentrated)
    concentration_penalty = (entropy / max_entropy) - 1.0  # range [-1, 0]
    
    # --- Combine components ---
    total = (
        0.5  * sharpe_reward
        + 0.25 * cvar_penalty * 10.0      # scale up CVaR (typically small)
        + 0.10 * drawdown_penalty * 10.0  # scale up drawdown
        + 0.05 * turnover_penalty
        + 0.10 * concentration_penalty
    )
    
    components = {
        "sharpe_reward": sharpe_reward,
        "cvar_penalty": cvar_penalty,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
        "total": total,
    }
    
    return total, components, reward_state