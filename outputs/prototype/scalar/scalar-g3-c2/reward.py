def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ema_ret": 0.0,
            "ema_var": 1e-6,
            "peak": 1.0,
            "cum_ret": 1.0,
            "alpha": 0.05,   # EMA decay: ~20-step half-life
            "step": 0,
        }

    alpha = state["alpha"]
    step = state["step"]

    # Update cumulative return and drawdown tracking
    cum_ret = state["cum_ret"] * (1.0 + port_ret)
    peak = max(state["peak"], cum_ret)
    drawdown = (peak - cum_ret) / (peak + 1e-8)

    # Online EMA mean and variance of returns (Welford-style EMA)
    ema_ret = state["ema_ret"]
    ema_var = state["ema_var"]

    # Update EMA statistics
    diff = port_ret - ema_ret
    ema_ret_new = (1 - alpha) * ema_ret + alpha * port_ret
    ema_var_new = (1 - alpha) * (ema_var + alpha * diff ** 2)
    ema_var_new = max(ema_var_new, 1e-8)

    # Incremental Sharpe ratio component
    sharpe_est = ema_ret_new / np.sqrt(ema_var_new)

    # Scale Sharpe to reasonable reward range
    sharpe_reward = np.clip(sharpe_est, -3.0, 3.0)

    # Turnover penalty: encourage stability, reduce transaction costs
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.1 * turnover

    # Drawdown penalty: penalize being in drawdown (nonlinear)
    dd_penalty = 2.0 * (drawdown ** 1.5)

    # Tail/downside penalty: extra penalty for large negative returns
    downside_penalty = 0.0
    if port_ret < 0:
        downside_penalty = 0.5 * (port_ret ** 2) * 100  # scale by 100 to match return magnitudes

    # Total reward
    total = sharpe_reward - turnover_penalty - dd_penalty - downside_penalty

    # Components for logging
    components = {
        "sharpe_reward": float(sharpe_reward),
        "turnover_penalty": float(-turnover_penalty),
        "dd_penalty": float(-dd_penalty),
        "downside_penalty": float(-downside_penalty),
        "port_ret": float(port_ret),
        "ema_sharpe": float(sharpe_est),
        "drawdown": float(drawdown),
    }

    # Update state
    state["ema_ret"] = ema_ret_new
    state["ema_var"] = ema_var_new
    state["cum_ret"] = cum_ret
    state["peak"] = peak
    state["step"] = step + 1

    return float(total), components, state