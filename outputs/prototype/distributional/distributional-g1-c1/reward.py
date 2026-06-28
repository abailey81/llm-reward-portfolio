def reward(weights, returns, prev_weights, port_ret, info):
    reward_state = info.get("reward_state", None)
    
    # Initialize state
    if reward_state is None:
        reward_state = {
            "returns_history": [],
            "step": 0,
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "alpha": 0.05,  # EMA decay for online estimates
        }
    
    step = reward_state["step"]
    alpha = reward_state["alpha"]
    
    # Update EMA of returns and squared returns
    ema_ret = reward_state["ema_ret"]
    ema_sq = reward_state["ema_sq"]
    
    if step == 0:
        ema_ret = port_ret
        ema_sq = port_ret ** 2
    else:
        ema_ret = alpha * port_ret + (1 - alpha) * ema_ret
        ema_sq = alpha * (port_ret ** 2) + (1 - alpha) * ema_sq
    
    # Online variance and std
    ema_var = max(ema_sq - ema_ret ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)
    
    # Keep recent returns for CVaR estimate
    returns_history = reward_state["returns_history"]
    returns_history.append(float(port_ret))
    # Keep rolling window
    window = 100
    if len(returns_history) > window:
        returns_history = returns_history[-window:]
    
    # --- Reward components ---
    
    # 1. Sharpe-like signal (EMA based)
    sharpe_signal = ema_ret / (ema_std + 1e-8)
    
    # 2. Turnover penalty (transaction costs proxy)
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = 0.1 * turnover
    
    # 3. CVaR penalty on recent history
    cvar_penalty = 0.0
    if len(returns_history) >= 20:
        arr = np.array(returns_history)
        cutoff = int(0.05 * len(arr))
        if cutoff < 1:
            cutoff = 1
        sorted_r = np.sort(arr)
        tail = sorted_r[:cutoff]
        cvar_5 = float(np.mean(tail))  # negative value
        cvar_penalty = -0.5 * min(cvar_5, 0.0)  # penalize bad CVaR
    
    # 4. Concentration penalty to encourage diversification
    # Penalize extreme concentration (Herfindahl index)
    hhi = float(np.sum(weights ** 2))
    n = len(weights)
    hhi_normalized = (hhi - 1.0 / n) / (1.0 - 1.0 / n + 1e-8)
    concentration_penalty = 0.05 * hhi_normalized
    
    # 5. Downside penalty: extra penalty for large negative returns this step
    downside_penalty = 0.0
    if port_ret < 0:
        downside_penalty = 0.2 * (port_ret ** 2) / (ema_var + 1e-8)
    
    # Total reward: Sharpe signal + direct return, minus penalties
    # Scale sharpe_signal to be comparable to port_ret
    total = (
        0.3 * sharpe_signal * ema_std  # effectively ema_ret scaled
        + 0.7 * port_ret               # direct return signal
        - turnover_penalty
        - cvar_penalty
        - concentration_penalty
        - downside_penalty
    )
    
    components = {
        "sharpe_signal": float(sharpe_signal * ema_std * 0.3),
        "direct_return": float(0.7 * port_ret),
        "turnover_penalty": float(-turnover_penalty),
        "cvar_penalty": float(-cvar_penalty),
        "concentration_penalty": float(-concentration_penalty),
        "downside_penalty": float(-downside_penalty),
    }
    
    reward_state["ema_ret"] = ema_ret
    reward_state["ema_sq"] = ema_sq
    reward_state["step"] = step + 1
    reward_state["returns_history"] = returns_history
    
    return float(total), components, reward_state