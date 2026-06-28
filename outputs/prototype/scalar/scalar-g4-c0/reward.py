def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get("reward_state")
    
    # Initialize state
    if state is None:
        state = {
            "ew_mean": 0.0,
            "ew_var": 1e-6,
            "peak_value": 1.0,
            "port_value": 1.0,
            "step": 0,
            "alpha": 0.05,  # EW decay: ~20-step half-life
        }
    
    alpha = state["alpha"]
    step = state["step"] + 1
    
    # --- Online exponentially-weighted mean and variance of port_ret ---
    ew_mean = state["ew_mean"]
    ew_var = state["ew_var"]
    
    # Welford-style EW update
    diff = port_ret - ew_mean
    ew_mean_new = (1 - alpha) * ew_mean + alpha * port_ret
    ew_var_new = (1 - alpha) * (ew_var + alpha * diff ** 2)
    ew_var_new = max(ew_var_new, 1e-8)
    
    ew_std = np.sqrt(ew_var_new)
    
    # Online Sharpe (de-meaned: excess over zero, but use EW estimates)
    online_sharpe = ew_mean_new / ew_std
    
    # --- Drawdown penalty ---
    port_value = state["port_value"] * (1.0 + port_ret)
    peak_value = max(state["peak_value"], port_value)
    drawdown = (peak_value - port_value) / (peak_value + 1e-8)
    drawdown_penalty = drawdown ** 2  # quadratic to penalize deep drawdowns more
    
    # --- Turnover penalty (beyond what's already in costs) ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.5 * turnover
    
    # --- Concentration penalty (Herfindahl index on risky assets) ---
    # Exclude cash (last element) for concentration calc
    risky_weights = weights[:-1] if len(weights) > 1 else weights
    herfindahl = np.sum(risky_weights ** 2)
    # Normalize: max concentration = 1.0, equal weight = 1/n
    n_risky = max(len(risky_weights), 1)
    min_herf = 1.0 / n_risky
    concentration_penalty = max(0.0, herfindahl - min_herf)
    
    # --- Downside deviation (semi-variance) penalty ---
    # Penalize negative returns more strongly
    downside = min(port_ret, 0.0) ** 2
    
    # --- Compose total reward ---
    # Primary: online Sharpe (main driver)
    # Secondary penalties for drawdown, concentration, downside
    r_sharpe = np.clip(online_sharpe, -5.0, 5.0)
    
    total = (
        r_sharpe
        - 2.0 * drawdown_penalty
        - 0.5 * turnover_penalty
        - 1.0 * concentration_penalty
        - 10.0 * downside
    )
    
    # Update state
    state["ew_mean"] = ew_mean_new
    state["ew_var"] = ew_var_new
    state["peak_value"] = peak_value
    state["port_value"] = port_value
    state["step"] = step
    
    components = {
        "online_sharpe": float(r_sharpe),
        "drawdown_penalty": float(-2.0 * drawdown_penalty),
        "turnover_penalty": float(-0.5 * turnover_penalty),
        "concentration_penalty": float(-1.0 * concentration_penalty),
        "downside_penalty": float(-10.0 * downside),
        "port_ret": float(port_ret),
        "drawdown": float(drawdown),
    }
    
    return float(total), components, state