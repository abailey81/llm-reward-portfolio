def reward(weights, returns, prev_weights, port_ret, info):
    reward_state = info.get("reward_state", None)
    
    # Initialize state
    if reward_state is None:
        reward_state = {
            "ret_history": [],
            "window": 60,
            "ema_mean": 0.0,
            "ema_var": 1e-6,
            "ema_alpha": 0.05,
            "step": 0,
        }
    
    state = reward_state
    state["step"] += 1
    alpha = state["ema_alpha"]
    
    # Update EMA mean and variance for online Sharpe
    prev_mean = state["ema_mean"]
    state["ema_mean"] = (1 - alpha) * prev_mean + alpha * port_ret
    state["ema_var"] = (1 - alpha) * state["ema_var"] + alpha * (port_ret - prev_mean) ** 2
    ema_std = np.sqrt(max(state["ema_var"], 1e-8))
    
    # Track return history for CVaR calculation
    state["ret_history"].append(port_ret)
    if len(state["ret_history"]) > state["window"]:
        state["ret_history"].pop(0)
    
    # --- Component 1: Online Sharpe contribution ---
    # Differential Sharpe-like signal
    sharpe_reward = state["ema_mean"] / ema_std
    
    # --- Component 2: Tail risk penalty (CVaR-based) ---
    cvar_penalty = 0.0
    if len(state["ret_history"]) >= 20:
        arr = np.array(state["ret_history"])
        cutoff_5 = np.percentile(arr, 5)
        tail_returns = arr[arr <= cutoff_5]
        if len(tail_returns) > 0:
            cvar_5 = np.mean(tail_returns)
            # Penalize if CVaR is negative
            cvar_penalty = min(cvar_5, 0.0) * 2.0
    
    # --- Component 3: Asymmetric step return signal ---
    # Reward gains less than penalize losses (loss aversion)
    if port_ret >= 0:
        step_signal = port_ret * 1.0
    else:
        step_signal = port_ret * 2.5  # stronger downside penalty
    
    # --- Component 4: Concentration penalty ---
    # Mild penalty for over-concentration (encourages diversification)
    n_assets = len(weights)
    herfindahl = np.sum(weights ** 2)
    max_herfindahl = 1.0
    min_herfindahl = 1.0 / n_assets
    concentration_penalty = -0.1 * (herfindahl - min_herfindahl) / max(max_herfindahl - min_herfindahl, 1e-8)
    
    # --- Component 5: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.05 * turnover
    
    # --- Combine ---
    # Scale sharpe_reward to be comparable to step signals
    # Use step signal as primary, sharpe as secondary shaping
    step = state["step"]
    if step < 20:
        # Early steps: rely mostly on step signal
        sharpe_weight = 0.1
    else:
        sharpe_weight = 0.3
    
    total = (
        (1.0 - sharpe_weight) * step_signal
        + sharpe_weight * sharpe_reward * 0.01  # scale sharpe to ~return magnitude
        + cvar_penalty
        + concentration_penalty
        + turnover_penalty
    )
    
    components = {
        "step_signal": step_signal,
        "sharpe_reward": sharpe_reward,
        "cvar_penalty": cvar_penalty,
        "concentration_penalty": concentration_penalty,
        "turnover_penalty": turnover_penalty,
    }
    
    return float(total), components, state