def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np
    
    # Initialize or retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_history": [],
            "peak_value": 1.0,
            "cumulative_value": 1.0,
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "ema_alpha": 0.05,   # ~20-step window
            "step": 0,
        }
    
    # Update cumulative portfolio value and drawdown
    state["cumulative_value"] *= (1.0 + port_ret)
    state["peak_value"] = max(state["peak_value"], state["cumulative_value"])
    drawdown = (state["peak_value"] - state["cumulative_value"]) / state["peak_value"]
    
    # Update EMA of returns and squared returns for online Sharpe
    alpha = state["ema_alpha"]
    state["ema_ret"] = alpha * port_ret + (1 - alpha) * state["ema_ret"]
    state["ema_sq"] = alpha * (port_ret ** 2) + (1 - alpha) * state["ema_sq"]
    
    # Store recent returns for CVaR computation
    state["returns_history"].append(port_ret)
    # Keep a rolling window
    window = 100
    if len(state["returns_history"]) > window:
        state["returns_history"] = state["returns_history"][-window:]
    
    state["step"] += 1
    
    # --- Component 1: Online Sharpe (EMA-based) ---
    ema_ret = state["ema_ret"]
    ema_sq = state["ema_sq"]
    ema_var = max(ema_sq - ema_ret ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)
    sharpe_signal = ema_ret / ema_std
    
    # --- Component 2: CVaR penalty (rolling window) ---
    hist = np.array(state["returns_history"])
    cvar_penalty = 0.0
    if len(hist) >= 10:
        # CVaR at 5% level
        threshold_5 = np.percentile(hist, 5)
        tail_5 = hist[hist <= threshold_5]
        cvar_5 = float(np.mean(tail_5)) if len(tail_5) > 0 else 0.0
        
        # CVaR at 10% level
        threshold_10 = np.percentile(hist, 10)
        tail_10 = hist[hist <= threshold_10]
        cvar_10 = float(np.mean(tail_10)) if len(tail_10) > 0 else 0.0
        
        # Penalize bad CVaR (note: cvar is negative for losses)
        cvar_penalty = -2.0 * abs(min(cvar_5, 0.0)) - 1.0 * abs(min(cvar_10, 0.0))
    
    # --- Component 3: Drawdown penalty ---
    drawdown_penalty = -1.5 * (drawdown ** 1.5)
    
    # --- Component 4: Turnover penalty (transaction costs proxy) ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = -0.1 * turnover
    
    # --- Component 5: Asymmetric return reward ---
    # Reward positive returns more, penalize negative returns more heavily
    if port_ret >= 0:
        asymmetric_ret = port_ret
    else:
        asymmetric_ret = 2.5 * port_ret  # heavier downside penalty
    
    # --- Component 6: Concentration penalty (diversification bonus) ---
    # Penalize extreme concentration (but not cash)
    risky_weights = weights[:-1]  # exclude cash
    hhi = float(np.sum(risky_weights ** 2))
    concentration_penalty = -0.3 * hhi
    
    # --- Combine ---
    # Scale sharpe signal to be on similar scale as returns
    sharpe_component = 0.3 * sharpe_signal * (abs(ema_ret) + 1e-6)
    
    total = (
        asymmetric_ret
        + sharpe_component
        + cvar_penalty
        + drawdown_penalty
        + turnover_penalty
        + concentration_penalty
    )
    
    components = {
        "asymmetric_ret": asymmetric_ret,
        "sharpe_component": sharpe_component,
        "cvar_penalty": cvar_penalty,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
        "drawdown": drawdown,
    }
    
    return float(total), components, state