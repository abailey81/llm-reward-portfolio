def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 0.0,
            "cum_log_ret": 0.0,
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "step": 0,
            "alpha": 0.05,  # EMA decay ~ 1/20 steps
        }

    alpha = state["alpha"]
    step = state["step"]

    # Update EMA of returns and squared returns (online Sharpe)
    ema_ret = state["ema_ret"]
    ema_sq = state["ema_sq"]

    if step == 0:
        ema_ret = port_ret
        ema_sq = port_ret ** 2
    else:
        ema_ret = alpha * port_ret + (1 - alpha) * ema_ret
        ema_sq = alpha * (port_ret ** 2) + (1 - alpha) * ema_sq

    ema_var = max(ema_sq - ema_ret ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)

    # Online Sharpe component (annualized scaling ~252 steps/yr)
    sharpe_component = ema_ret / ema_std

    # Cumulative log return for drawdown tracking
    cum_log_ret = state["cum_log_ret"] + np.log1p(port_ret)
    peak = max(state["peak"], cum_log_ret)
    drawdown = peak - cum_log_ret  # always >= 0

    # Drawdown penalty - penalize being in drawdown
    drawdown_penalty = -drawdown * 0.5

    # Turnover penalty (transaction costs proxy)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -turnover * 0.1

    # Tail loss penalty: penalize large negative returns more
    tail_threshold = -0.02
    tail_penalty = 0.0
    if port_ret < tail_threshold:
        tail_penalty = -((port_ret - tail_threshold) ** 2) * 10.0

    # Combine components
    # Sharpe is the main driver; others are penalties
    total = sharpe_component + drawdown_penalty + turnover_penalty + tail_penalty

    # Update state
    state["ema_ret"] = ema_ret
    state["ema_sq"] = ema_sq
    state["cum_log_ret"] = cum_log_ret
    state["peak"] = peak
    state["step"] = step + 1

    components = {
        "sharpe_component": sharpe_component,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
        "tail_penalty": tail_penalty,
        "port_ret": port_ret,
        "ema_ret": ema_ret,
        "ema_std": ema_std,
    }

    return float(total), components, state