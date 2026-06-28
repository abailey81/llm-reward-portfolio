def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize state
    state = info.get("reward_state") or {}
    
    # Rolling window for return history
    window = 100
    ret_history = state.get("ret_history", [])
    ret_history.append(float(port_ret))
    if len(ret_history) > window:
        ret_history = ret_history[-window:]
    
    # Online Sharpe (annualized ~ daily * sqrt(252))
    arr = np.array(ret_history)
    n = len(arr)
    
    if n < 5:
        sharpe_contrib = port_ret * 10.0
    else:
        mu = np.mean(arr)
        sigma = np.std(arr) + 1e-8
        sharpe_contrib = (mu / sigma) * np.sqrt(252) / window
    
    # Drawdown tracking
    cum_rets = state.get("cum_rets", 1.0)
    peak = state.get("peak", 1.0)
    cum_rets = cum_rets * (1.0 + port_ret)
    peak = max(peak, cum_rets)
    drawdown = (peak - cum_rets) / (peak + 1e-8)
    
    # Turnover penalty (extra friction signal)
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    
    # Concentration (Herfindahl) - penalize extreme concentration
    hhi = float(np.sum(weights ** 2))
    n_assets = len(weights)
    hhi_excess = max(0.0, hhi - 1.0 / n_assets)
    
    # Tail loss: downside deviation component
    if n >= 10:
        neg_rets = arr[arr < 0]
        tail_penalty = float(np.mean(neg_rets ** 2)) if len(neg_rets) > 0 else 0.0
    else:
        tail_penalty = 0.0
    
    # Combine components
    sharpe_term = sharpe_contrib          # main signal
    dd_penalty = -0.5 * drawdown         # drawdown aversion
    tail_term = -20.0 * tail_penalty     # CVaR-like tail penalty
    turnover_penalty = -0.05 * turnover  # mild turnover cost
    hhi_penalty = -0.3 * hhi_excess      # mild concentration penalty
    
    total = sharpe_term + dd_penalty + tail_term + turnover_penalty + hhi_penalty
    
    components = {
        "sharpe_contrib": sharpe_contrib,
        "dd_penalty": dd_penalty,
        "tail_penalty": tail_term,
        "turnover_penalty": turnover_penalty,
        "hhi_penalty": hhi_penalty,
    }
    
    reward_state = {
        "ret_history": ret_history,
        "cum_rets": cum_rets,
        "peak": peak,
    }
    
    return float(total), components, reward_state