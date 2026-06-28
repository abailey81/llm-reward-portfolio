def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_mean": 0.0,
            "ret_var": 1e-8,
            "n": 0,
            "peak": 1.0,
            "cum_ret": 1.0,
            "ema_mean": 0.0,
            "ema_var": 1e-8,
        }

    n = state["n"]
    alpha = 0.05  # EMA decay for online estimates

    # Update EMA of return mean and variance
    ema_mean = state["ema_mean"]
    ema_var = state["ema_var"]
    ema_mean_new = (1 - alpha) * ema_mean + alpha * port_ret
    ema_var_new = (1 - alpha) * ema_var + alpha * (port_ret - ema_mean) ** 2

    # Update cumulative return and drawdown tracking
    cum_ret = state["cum_ret"] * (1.0 + port_ret)
    peak = max(state["peak"], cum_ret)
    drawdown = (peak - cum_ret) / (peak + 1e-8)

    # Online Sharpe: use EMA estimates
    sharpe_std = max(np.sqrt(ema_var_new), 1e-6)
    # Incremental Sharpe contribution: return normalized by running vol
    sharpe_contrib = port_ret / sharpe_std

    # Drawdown penalty - nonlinear to penalize large drawdowns more
    dd_penalty = drawdown ** 2

    # Turnover penalty
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.1 * turnover

    # Tail loss penalty: penalize large negative returns
    tail_penalty = 0.0
    if port_ret < 0:
        tail_penalty = 2.0 * (port_ret ** 2)

    # Warm-up: reduce signal noise for first few steps
    warmup_scale = min(1.0, (n + 1) / 20.0)

    # Total reward
    total = warmup_scale * (
        sharpe_contrib
        - 2.0 * dd_penalty
        - turnover_penalty
        - tail_penalty
    )

    components = {
        "sharpe_contrib": float(sharpe_contrib),
        "dd_penalty": float(-2.0 * dd_penalty),
        "turnover_penalty": float(-turnover_penalty),
        "tail_penalty": float(-tail_penalty),
        "port_ret": float(port_ret),
        "drawdown": float(drawdown),
    }

    state["ema_mean"] = ema_mean_new
    state["ema_var"] = ema_var_new
    state["cum_ret"] = cum_ret
    state["peak"] = peak
    state["n"] = n + 1

    return float(total), components, state