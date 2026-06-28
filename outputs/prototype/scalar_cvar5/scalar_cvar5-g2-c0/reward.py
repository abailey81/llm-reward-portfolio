def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get("reward_state")
    
    # Initialize state
    if state is None:
        state = {
            "ret_history": [],
            "peak_value": 1.0,
            "cum_value": 1.0,
            "window": 60,
            "ema_mean": None,
            "ema_var": None,
            "alpha": 0.06,  # EMA decay for online stats
        }
    
    # Update cumulative portfolio value
    state["cum_value"] = state["cum_value"] * (1.0 + port_ret)
    if state["cum_value"] > state["peak_value"]:
        state["peak_value"] = state["cum_value"]
    
    # Track return history (rolling window)
    state["ret_history"].append(port_ret)
    window = state["window"]
    if len(state["ret_history"]) > window:
        state["ret_history"] = state["ret_history"][-window:]
    
    ret_arr = np.array(state["ret_history"])
    n = len(ret_arr)
    
    # --- Component 1: Online Sharpe (EMA-based, robust) ---
    alpha = state["alpha"]
    if state["ema_mean"] is None:
        state["ema_mean"] = port_ret
        state["ema_var"] = 0.0
    else:
        prev_mean = state["ema_mean"]
        state["ema_mean"] = (1 - alpha) * prev_mean + alpha * port_ret
        state["ema_var"] = (1 - alpha) * (state["ema_var"] + alpha * (port_ret - prev_mean) ** 2)
    
    ema_std = np.sqrt(max(state["ema_var"], 1e-8))
    sharpe_reward = state["ema_mean"] / ema_std
    
    # --- Component 2: CVaR penalty (tail risk, rolling window) ---
    cvar_penalty = 0.0
    if n >= 10:
        cvar_level = 0.05
        cutoff = max(1, int(np.floor(n * cvar_level)))
        sorted_rets = np.sort(ret_arr)
        cvar = np.mean(sorted_rets[:cutoff])  # mean of worst returns
        # Penalize negative CVaR (tail losses)
        cvar_penalty = min(cvar, 0.0) * 5.0  # amplify penalty for bad tails
    
    # --- Component 3: Drawdown penalty ---
    drawdown = (state["cum_value"] - state["peak_value"]) / state["peak_value"]
    # drawdown <= 0 always; penalize proportionally
    dd_penalty = drawdown * 2.0
    
    # --- Component 4: Turnover / transaction cost penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.001 * turnover  # mild penalty for excessive rebalancing
    
    # --- Component 5: Direct return signal (scaled) ---
    # Provide a direct return signal to avoid sparse gradients
    direct_ret = port_ret * 10.0  # scale up for signal clarity
    
    # --- Combine components ---
    # Primary driver: Sharpe; secondary: tail risk and drawdown management
    total = (
        0.40 * sharpe_reward
        + 0.30 * direct_ret
        + 0.15 * cvar_penalty
        + 0.10 * dd_penalty
        + 0.05 * turnover_penalty * 10  # normalize
    )
    
    components = {
        "sharpe_reward": float(sharpe_reward),
        "direct_ret": float(direct_ret),
        "cvar_penalty": float(cvar_penalty),
        "dd_penalty": float(dd_penalty),
        "turnover_penalty": float(turnover_penalty),
        "total": float(total),
    }
    
    return float(total), components, state