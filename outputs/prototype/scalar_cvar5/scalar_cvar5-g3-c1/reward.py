def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get("reward_state", None)
    
    # Initialize state
    if state is None:
        state = {
            "returns_window": [],
            "peak": 0.0,
            "cum_ret": 0.0,
            "step": 0,
        }
    
    step = state["step"] + 1
    returns_window = state["returns_window"]
    
    # Track cumulative return for drawdown
    cum_ret = state["cum_ret"] + port_ret
    peak = max(state["peak"], cum_ret)
    drawdown = peak - cum_ret  # always >= 0
    
    # Maintain a rolling window of returns (up to 60 steps)
    window_size = 60
    returns_window = (returns_window + [port_ret])[-window_size:]
    
    n = len(returns_window)
    arr = np.array(returns_window)
    
    # --- Component 1: Online Sharpe-like signal ---
    if n >= 5:
        mu = np.mean(arr)
        sigma = np.std(arr) + 1e-8
        sharpe_signal = mu / sigma
    else:
        sharpe_signal = port_ret  # early steps: use raw return
    
    # --- Component 2: CVaR penalty (tail risk) ---
    if n >= 10:
        sorted_arr = np.sort(arr)
        cvar_idx = max(1, int(np.floor(0.05 * n)))
        cvar = np.mean(sorted_arr[:cvar_idx])  # negative in bad cases
        # Penalize severely bad tail (CVaR is already negative for losses)
        cvar_penalty = min(0.0, cvar) * 3.0  # amplify tail loss penalty
    else:
        cvar_penalty = 0.0
    
    # --- Component 3: Drawdown penalty ---
    # Penalize current drawdown relative to a scaled threshold
    drawdown_penalty = -0.5 * drawdown if drawdown > 0.02 else 0.0
    
    # --- Component 4: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.1 * turnover
    
    # --- Component 5: Concentration penalty (avoid over-concentration) ---
    # Herfindahl index on risky weights (exclude cash = last element)
    risky = weights[:-1]
    if np.sum(risky) > 1e-6:
        norm_risky = risky / (np.sum(risky) + 1e-8)
        herfindahl = np.sum(norm_risky ** 2)
        concentration_penalty = -0.05 * herfindahl
    else:
        concentration_penalty = 0.0
    
    # --- Combine ---
    # Scale sharpe signal to be the primary driver
    total = (
        0.6 * sharpe_signal
        + 0.2 * cvar_penalty
        + 0.1 * drawdown_penalty
        + 0.05 * turnover_penalty
        + 0.05 * concentration_penalty
    )
    
    # Update state
    reward_state = {
        "returns_window": returns_window,
        "peak": peak,
        "cum_ret": cum_ret,
        "step": step,
    }
    
    components = {
        "sharpe_signal": sharpe_signal,
        "cvar_penalty": cvar_penalty,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
    }
    
    return float(total), components, reward_state