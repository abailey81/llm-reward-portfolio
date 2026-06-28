def reward(weights, returns, prev_weights, port_ret, info):
    reward_state = info.get("reward_state", None)
    
    # Initialize state
    if reward_state is None:
        reward_state = {
            "ret_history": [],
            "peak": 0.0,
            "cum_ret": 0.0,
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "ema_alpha": 0.06,
            "step": 0,
        }
    
    state = reward_state
    alpha = state["ema_alpha"]
    step = state["step"]
    
    # Update cumulative return and drawdown tracking
    state["cum_ret"] += port_ret
    state["peak"] = max(state["peak"], state["cum_ret"])
    drawdown = state["peak"] - state["cum_ret"]
    
    # Update EMA of returns and squared returns for online Sharpe
    if step == 0:
        state["ema_ret"] = port_ret
        state["ema_sq"] = port_ret ** 2
    else:
        state["ema_ret"] = alpha * port_ret + (1 - alpha) * state["ema_ret"]
        state["ema_sq"] = alpha * (port_ret ** 2) + (1 - alpha) * state["ema_sq"]
    
    # Store return history (cap at 200 steps)
    state["ret_history"].append(port_ret)
    if len(state["ret_history"]) > 200:
        state["ret_history"].pop(0)
    
    hist = np.array(state["ret_history"])
    n = len(hist)
    
    # --- Component 1: Online Sharpe (EMA-based) ---
    ema_var = max(state["ema_sq"] - state["ema_ret"] ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)
    online_sharpe = state["ema_ret"] / ema_std
    sharpe_reward = np.clip(online_sharpe, -3.0, 3.0) * 0.4
    
    # --- Component 2: Direct return reward (scaled) ---
    ret_reward = port_ret * 10.0
    
    # --- Component 3: CVaR penalty using history ---
    cvar_penalty = 0.0
    if n >= 20:
        sorted_hist = np.sort(hist)
        # CVaR at 10%
        cutoff_10 = max(int(np.floor(0.10 * n)), 1)
        cvar_10 = np.mean(sorted_hist[:cutoff_10])
        # CVaR at 5%
        cutoff_5 = max(int(np.floor(0.05 * n)), 1)
        cvar_5 = np.mean(sorted_hist[:cutoff_5])
        
        # Penalize bad tail behavior
        cvar_penalty = -np.clip(-cvar_10, 0, 0.1) * 5.0 - np.clip(-cvar_5, 0, 0.15) * 3.0
    
    # --- Component 4: Drawdown penalty ---
    dd_penalty = -np.clip(drawdown, 0, 0.5) * 1.5
    
    # --- Component 5: Turnover penalty (transaction costs awareness) ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -turnover * 0.05
    
    # --- Component 6: Concentration penalty (encourage diversification) ---
    # Penalize extreme concentration using Herfindahl index
    hhi = np.sum(weights ** 2)
    n_assets = len(weights)
    max_hhi = 1.0
    min_hhi = 1.0 / n_assets
    normalized_hhi = (hhi - min_hhi) / max(max_hhi - min_hhi, 1e-8)
    concentration_penalty = -normalized_hhi * 0.1
    
    # --- Combine components ---
    total = (ret_reward + sharpe_reward + cvar_penalty + 
             dd_penalty + turnover_penalty + concentration_penalty)
    
    state["step"] += 1
    
    components = {
        "ret_reward": ret_reward,
        "sharpe_reward": sharpe_reward,
        "cvar_penalty": cvar_penalty,
        "dd_penalty": dd_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
    }
    
    return float(total), components, state