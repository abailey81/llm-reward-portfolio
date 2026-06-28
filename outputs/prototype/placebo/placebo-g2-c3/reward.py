def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get("reward_state")
    
    # Initialize state
    if state is None:
        state = {
            "ew_mean": 0.0,
            "ew_var": 1e-6,
            "peak_value": 1.0,
            "cum_value": 1.0,
            "ret_history": [],
            "step": 0,
        }
    
    alpha = 0.06  # EWM decay for ~16-step half-life
    
    ew_mean = state["ew_mean"]
    ew_var = state["ew_var"]
    peak_value = state["peak_value"]
    cum_value = state["cum_value"]
    ret_history = state["ret_history"]
    step = state["step"]
    
    # Update EWM mean and variance
    ew_mean = (1 - alpha) * ew_mean + alpha * port_ret
    ew_var = (1 - alpha) * ew_var + alpha * (port_ret - ew_mean) ** 2
    ew_std = np.sqrt(max(ew_var, 1e-8))
    
    # Online Sharpe component
    sharpe_component = ew_mean / ew_std
    
    # Update cumulative value and drawdown
    cum_value = cum_value * (1.0 + port_ret)
    peak_value = max(peak_value, cum_value)
    drawdown = (peak_value - cum_value) / max(peak_value, 1e-8)
    drawdown_penalty = drawdown ** 2  # Quadratic penalty
    
    # Turnover penalty
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.1 * turnover
    
    # Tail risk: CVaR from recent history
    ret_history.append(port_ret)
    if len(ret_history) > 60:
        ret_history.pop(0)
    
    cvar_penalty = 0.0
    if len(ret_history) >= 10:
        arr = np.array(ret_history)
        cutoff = np.percentile(arr, 10)
        tail = arr[arr <= cutoff]
        if len(tail) > 0:
            cvar = np.mean(tail)
            cvar_penalty = -0.5 * min(cvar, 0.0)  # Only penalize negative CVaR
    
    # Direct return component (scaled)
    ret_component = port_ret * 10.0  # Scale up for stronger signal
    
    # Total reward
    total = (
        ret_component
        + 0.3 * sharpe_component
        - 1.5 * drawdown_penalty
        - turnover_penalty
        - cvar_penalty
    )
    
    # Update state
    state["ew_mean"] = ew_mean
    state["ew_var"] = ew_var
    state["peak_value"] = peak_value
    state["cum_value"] = cum_value
    state["ret_history"] = ret_history
    state["step"] = step + 1
    
    components = {
        "ret_component": ret_component,
        "sharpe_component": sharpe_component,
        "drawdown_penalty": -1.5 * drawdown_penalty,
        "turnover_penalty": -turnover_penalty,
        "cvar_penalty": -cvar_penalty,
    }
    
    return float(total), components, state