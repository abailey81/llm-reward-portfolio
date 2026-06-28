def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or restore state
    state = info.get("reward_state") if info.get("reward_state") is not None else {}
    
    # Online return tracking for Sharpe computation
    ret_history = state.get("ret_history", [])
    peak = state.get("peak", 1.0)
    cum_value = state.get("cum_value", 1.0)
    
    # Update cumulative value and drawdown tracking
    cum_value = cum_value * (1.0 + port_ret)
    peak = max(peak, cum_value)
    drawdown = (peak - cum_value) / (peak + 1e-8)
    
    # Append current return to history
    ret_history.append(port_ret)
    # Keep a rolling window
    window = 60
    if len(ret_history) > window:
        ret_history = ret_history[-window:]
    
    n = len(ret_history)
    
    # Compute online Sharpe-like signal
    if n >= 2:
        arr = np.array(ret_history)
        mean_r = np.mean(arr)
        std_r = np.std(arr, ddof=1)
        sharpe_signal = mean_r / (std_r + 1e-8)
    else:
        sharpe_signal = port_ret
    
    # Drawdown penalty (quadratic to strongly penalize deep drawdowns)
    drawdown_penalty = drawdown ** 2
    
    # Tail loss penalty: extra penalty if this step's return is very negative
    tail_threshold = -0.02
    tail_penalty = min(0.0, port_ret - tail_threshold) ** 2
    
    # Turnover penalty (encourage stability)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.1 * turnover
    
    # Concentration penalty (encourage diversification via entropy)
    w_clipped = np.clip(weights, 1e-8, 1.0)
    entropy = -np.sum(w_clipped * np.log(w_clipped))
    max_entropy = np.log(len(weights) + 1e-8)
    concentration_penalty = 0.05 * (1.0 - entropy / (max_entropy + 1e-8))
    
    # Combine components
    # Sharpe signal is the main driver, scaled modestly
    total = (
        10.0 * sharpe_signal
        - 2.0 * drawdown_penalty
        - 5.0 * tail_penalty
        - turnover_penalty
        - concentration_penalty
    )
    
    components = {
        "sharpe_signal": 10.0 * sharpe_signal,
        "drawdown_penalty": -2.0 * drawdown_penalty,
        "tail_penalty": -5.0 * tail_penalty,
        "turnover_penalty": -turnover_penalty,
        "concentration_penalty": -concentration_penalty,
    }
    
    reward_state = {
        "ret_history": ret_history,
        "peak": peak,
        "cum_value": cum_value,
    }
    
    return total, components, reward_state