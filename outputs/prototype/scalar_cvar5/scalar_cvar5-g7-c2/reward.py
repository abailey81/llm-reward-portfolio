def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cum_value": 1.0,
            "ema_mean": 0.0,
            "ema_var": 1e-6,
            "step": 0,
            "alpha": 0.05,  # EMA decay (faster adaptation)
        }

    step = state["step"]
    alpha = 0.06  # EMA smoothing factor
    ret_history = state["ret_history"]

    # Update cumulative portfolio value
    cum_value = state["cum_value"] * (1.0 + port_ret)
    state["cum_value"] = cum_value

    # Track peak for drawdown
    peak = state["peak"]
    if cum_value > peak:
        peak = cum_value
    state["peak"] = peak

    # Drawdown penalty
    drawdown = (peak - cum_value) / (peak + 1e-8)
    drawdown_penalty = -2.0 * drawdown

    # Update EMA of mean and variance
    ema_mean = state["ema_mean"]
    ema_var = state["ema_var"]

    ema_mean = alpha * port_ret + (1 - alpha) * ema_mean
    ema_var = alpha * (port_ret - ema_mean) ** 2 + (1 - alpha) * ema_var
    ema_std = np.sqrt(max(ema_var, 1e-8))

    state["ema_mean"] = ema_mean
    state["ema_var"] = ema_var

    # Keep rolling history for CVaR computation (last 100 steps)
    ret_history.append(port_ret)
    if len(ret_history) > 100:
        ret_history.pop(0)
    state["ret_history"] = ret_history

    # Online Sharpe-like signal
    sharpe_signal = ema_mean / (ema_std + 1e-8)

    # CVaR penalty: expected loss in worst 5% of observed returns
    cvar_penalty = 0.0
    if len(ret_history) >= 20:
        arr = np.array(ret_history)
        cutoff = np.percentile(arr, 5)
        tail = arr[arr <= cutoff]
        if len(tail) > 0:
            cvar_val = np.mean(tail)  # negative number typically
            cvar_penalty = 2.5 * cvar_val  # penalize bad tail

    # Turnover penalty (transaction costs proxy)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.1 * turnover

    # Downside deviation penalty (semi-variance)
    downside = min(port_ret, 0.0) ** 2
    downside_penalty = -5.0 * downside

    # Base return component
    ret_component = port_ret

    # Combine all components
    # Scale sharpe signal contribution
    if step < 10:
        # Early steps: rely more on raw return
        total = ret_component + turnover_penalty + downside_penalty + drawdown_penalty
    else:
        total = (
            0.5 * ret_component
            + 0.3 * sharpe_signal
            + cvar_penalty
            + turnover_penalty
            + downside_penalty
            + drawdown_penalty
        )

    state["step"] = step + 1

    components = {
        "ret": ret_component,
        "sharpe_signal": sharpe_signal if step >= 10 else 0.0,
        "cvar_penalty": cvar_penalty,
        "turnover_penalty": turnover_penalty,
        "downside_penalty": downside_penalty,
        "drawdown_penalty": drawdown_penalty,
    }

    return float(total), components, state