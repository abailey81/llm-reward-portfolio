def reward(weights, returns, prev_weights, port_ret, info):
    reward_state = info.get("reward_state", None)
    
    # Initialize state
    if reward_state is None:
        reward_state = {
            "ret_history": [],
            "n": 0,
            "mean": 0.0,
            "M2": 0.0,  # for Welford's online variance
        }
    
    # Welford's online mean/variance update
    n = reward_state["n"] + 1
    mean = reward_state["mean"]
    M2 = reward_state["M2"]
    
    delta = port_ret - mean
    mean = mean + delta / n
    delta2 = port_ret - mean
    M2 = M2 + delta * delta2
    
    reward_state["n"] = n
    reward_state["mean"] = mean
    reward_state["M2"] = M2
    
    # Keep rolling window of returns for CVaR
    ret_history = reward_state["ret_history"]
    ret_history.append(port_ret)
    window = 60
    if len(ret_history) > window:
        ret_history = ret_history[-window:]
    reward_state["ret_history"] = ret_history
    
    # --- Component 1: Online Sharpe-based reward ---
    if n >= 5:
        variance = M2 / n  # population variance
        std = np.sqrt(max(variance, 1e-8))
        sharpe_increment = port_ret / std
    else:
        sharpe_increment = port_ret * 10.0  # early steps: just use scaled return
    
    # --- Component 2: CVaR penalty (tail risk) ---
    cvar_penalty = 0.0
    if len(ret_history) >= 10:
        arr = np.array(ret_history)
        cutoff_5 = int(np.floor(0.05 * len(arr)))
        cutoff_5 = max(cutoff_5, 1)
        sorted_rets = np.sort(arr)
        cvar_5 = np.mean(sorted_rets[:cutoff_5])
        # Penalize if CVaR is negative
        cvar_penalty = min(cvar_5, 0.0) * 2.0  # negative contribution
    
    # --- Component 3: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.05 * turnover
    
    # --- Component 4: Concentration penalty (Herfindahl) ---
    # Exclude cash (last weight) from concentration calc
    asset_weights = weights[:-1] if len(weights) > 1 else weights
    herfindahl = np.sum(asset_weights ** 2)
    n_assets = len(asset_weights)
    # Normalized: 0 = perfectly diversified, 1 = fully concentrated
    if n_assets > 1:
        hhi_norm = (herfindahl - 1.0/n_assets) / (1.0 - 1.0/n_assets + 1e-8)
        concentration_penalty = -0.1 * max(hhi_norm, 0.0)
    else:
        concentration_penalty = 0.0
    
    # --- Total reward ---
    # Scale sharpe increment to be primary signal
    total = (
        0.6 * sharpe_increment
        + 0.3 * cvar_penalty
        + turnover_penalty
        + concentration_penalty
    )
    
    components = {
        "sharpe_increment": sharpe_increment,
        "cvar_penalty": cvar_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
    }
    
    return float(total), components, reward_state