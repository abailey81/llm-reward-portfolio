def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get("reward_state")
    
    # Initialize state
    if state is None:
        state = {
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "alpha": 0.05,          # EMA decay for short-term
            "alpha_slow": 0.01,     # EMA decay for long-term drawdown
            "peak": 0.0,
            "cumulative": 0.0,
            "step": 0,
            "recent_rets": [],
        }
    
    alpha = state["alpha"]
    alpha_slow = state["alpha_slow"]
    step = state["step"] + 1
    state["step"] = step
    
    # Update cumulative log-return proxy for drawdown
    state["cumulative"] = state["cumulative"] + port_ret
    if state["cumulative"] > state["peak"]:
        state["peak"] = state["cumulative"]
    drawdown = state["peak"] - state["cumulative"]  # always >= 0
    
    # Online EMA mean and variance of portfolio returns
    state["ema_ret"] = (1 - alpha) * state["ema_ret"] + alpha * port_ret
    state["ema_sq"] = (1 - alpha) * state["ema_sq"] + alpha * (port_ret ** 2)
    
    ema_var = max(state["ema_sq"] - state["ema_ret"] ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)
    
    # Sharpe-like signal: annualized scaling ~ sqrt(252) but keep relative
    sharpe_signal = state["ema_ret"] / ema_std
    
    # Tail risk penalty: penalize returns below -1.5 std deviations
    tail_threshold = state["ema_ret"] - 1.5 * ema_std
    tail_penalty = min(port_ret - tail_threshold, 0.0) ** 2  # 0 if above threshold
    
    # Drawdown penalty (nonlinear to penalize deep drawdowns more)
    drawdown_penalty = drawdown ** 2
    
    # Turnover cost penalty (encourage stable allocations)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.5 * turnover
    
    # Concentration penalty: encourage diversification via entropy
    w_assets = np.clip(weights, 1e-8, 1.0)
    entropy = -np.sum(w_assets * np.log(w_assets))
    max_entropy = np.log(len(weights))
    concentration_penalty = max(0.0, 0.3 * (0.3 - entropy / max(max_entropy, 1e-8)))
    
    # Core return component (direct signal)
    return_component = port_ret * 10.0  # scaled to give meaningful gradient
    
    # Combine components
    sharpe_weight = 3.0
    drawdown_weight = 5.0
    tail_weight = 20.0
    
    total = (
        return_component
        + sharpe_weight * sharpe_signal
        - drawdown_weight * drawdown_penalty
        - tail_weight * tail_penalty
        - turnover_penalty
        - concentration_penalty
    )
    
    components = {
        "return_component": return_component,
        "sharpe_signal": sharpe_signal,
        "drawdown_penalty": -drawdown_weight * drawdown_penalty,
        "tail_penalty": -tail_weight * tail_penalty,
        "turnover_penalty": -turnover_penalty,
        "concentration_penalty": -concentration_penalty,
    }
    
    return float(total), components, state