def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get("reward_state", None)
    
    # Initialize state
    if state is None:
        state = {
            "ret_history": [],
            "ew_mean": 0.0,
            "ew_var": 1e-6,
            "peak": 1.0,
            "cum_value": 1.0,
            "n": 0,
        }
    
    # Update cumulative value and drawdown
    state["cum_value"] *= (1.0 + port_ret)
    if state["cum_value"] > state["peak"]:
        state["peak"] = state["cum_value"]
    drawdown = (state["peak"] - state["cum_value"]) / (state["peak"] + 1e-8)
    
    # Exponentially weighted mean and variance (fast decay for responsiveness)
    alpha = 0.05  # decay factor (smaller = more history)
    state["n"] += 1
    n = state["n"]
    
    if n == 1:
        state["ew_mean"] = port_ret
        state["ew_var"] = 1e-6
    else:
        old_mean = state["ew_mean"]
        state["ew_mean"] = (1 - alpha) * old_mean + alpha * port_ret
        state["ew_var"] = (1 - alpha) * (state["ew_var"] + alpha * (port_ret - old_mean) ** 2)
    
    ew_std = np.sqrt(max(state["ew_var"], 1e-8))
    sharpe_component = state["ew_mean"] / ew_std
    
    # CVaR penalty using rolling history
    state["ret_history"].append(port_ret)
    max_history = 200
    if len(state["ret_history"]) > max_history:
        state["ret_history"] = state["ret_history"][-max_history:]
    
    cvar_penalty = 0.0
    if len(state["ret_history"]) >= 20:
        hist = np.array(state["ret_history"])
        cutoff_5 = np.percentile(hist, 5)
        tail = hist[hist <= cutoff_5]
        if len(tail) > 0:
            cvar_5 = np.mean(tail)  # negative number
            cvar_penalty = cvar_5  # penalize bad tails
    
    # Turnover penalty
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.002 * turnover
    
    # Drawdown penalty
    drawdown_penalty = 0.5 * drawdown
    
    # Combine: primary signal is online Sharpe (annualized approx)
    # Scale sharpe to be in a reasonable range
    sharpe_scaled = sharpe_component * np.sqrt(252)
    
    # Total reward
    # Base: raw return to keep incentive aligned
    # Sharpe term: risk-adjusted signal
    # CVaR: tail risk penalty
    # Drawdown: path-dependent risk
    # Turnover: cost penalty
    
    w_ret = 0.3
    w_sharpe = 0.4
    w_cvar = 0.2
    w_dd = 0.1
    
    # Normalize sharpe to similar scale as port_ret
    sharpe_norm = sharpe_scaled / 252.0  # bring back to per-step scale
    
    total = (
        w_ret * port_ret
        + w_sharpe * sharpe_norm
        + w_cvar * cvar_penalty
        - w_dd * drawdown_penalty
        - turnover_penalty
    )
    
    components = {
        "port_ret": port_ret,
        "sharpe_norm": sharpe_norm,
        "cvar_penalty": cvar_penalty,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
    }
    
    return float(total), components, state