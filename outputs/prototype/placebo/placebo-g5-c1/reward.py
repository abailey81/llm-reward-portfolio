def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve state
    state = info.get("reward_state", None)
    
    if state is None:
        state = {
            "ema_ret": 0.0,
            "ema_var": 1e-6,
            "peak": 0.0,
            "cumulative": 0.0,
            "recent_rets": [],
            "step": 0,
        }
    
    step = state["step"] + 1
    alpha = 0.05  # EMA decay for fast adaptation
    alpha_slow = 0.01  # slower decay for variance
    
    # Update EMA of returns and variance
    ema_ret = (1 - alpha) * state["ema_ret"] + alpha * port_ret
    deviation = port_ret - state["ema_ret"]
    ema_var = (1 - alpha_slow) * state["ema_var"] + alpha_slow * (deviation ** 2)
    ema_std = np.sqrt(max(ema_var, 1e-8))
    
    # Online Sharpe component
    sharpe_signal = ema_ret / ema_std
    
    # Update cumulative return for drawdown
    cumulative = state["cumulative"] + np.log1p(port_ret)
    peak = max(state["peak"], cumulative)
    drawdown = peak - cumulative  # always >= 0
    
    # Drawdown penalty (exponential to punish deep drawdowns more)
    drawdown_penalty = -np.expm1(drawdown) * 0.5  # ~= -drawdown for small values
    
    # Maintain recent returns buffer for tail risk
    recent_rets = state["recent_rets"].copy()
    recent_rets.append(port_ret)
    window = 60
    if len(recent_rets) > window:
        recent_rets = recent_rets[-window:]
    
    # CVaR-like tail penalty (average of bottom 10% returns)
    tail_penalty = 0.0
    if len(recent_rets) >= 10:
        arr = np.array(recent_rets)
        cutoff = int(max(1, 0.1 * len(arr)))
        tail_returns = np.sort(arr)[:cutoff]
        cvar = np.mean(tail_returns)
        tail_penalty = min(cvar, 0.0) * 0.5  # penalty for bad tail
    
    # Turnover penalty
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.1 * turnover
    
    # Concentration penalty (encourage diversification, penalize extreme weights)
    n = len(weights)
    hhi = np.sum(weights ** 2)  # Herfindahl index; 1/n for equal weight
    concentration_penalty = -0.05 * (hhi - 1.0 / n)
    
    # Raw return component (scaled)
    ret_component = port_ret * 10.0
    
    # Combine components with scaling
    sharpe_component = sharpe_signal * 0.3
    
    total = (
        ret_component
        + sharpe_component
        + drawdown_penalty
        + tail_penalty
        + turnover_penalty
        + concentration_penalty
    )
    
    components = {
        "ret_component": ret_component,
        "sharpe_signal": sharpe_component,
        "drawdown_penalty": drawdown_penalty,
        "tail_penalty": tail_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
    }
    
    new_state = {
        "ema_ret": ema_ret,
        "ema_var": ema_var,
        "peak": peak,
        "cumulative": cumulative,
        "recent_rets": recent_rets,
        "step": step,
    }
    
    return float(total), components, new_state