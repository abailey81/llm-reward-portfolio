def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "step": 0,
            "ema_mean": 0.0,
            "ema_var": 1e-6,
            "alpha": 0.05,  # EMA decay for online stats
        }

    alpha = state["alpha"]
    step = state["step"]
    ret_history = state["ret_history"]

    # Update EMA mean and variance (Welford-style EMA)
    ema_mean = state["ema_mean"]
    ema_var = state["ema_var"]

    if step == 0:
        ema_mean = port_ret
        ema_var = 1e-6
    else:
        ema_mean = alpha * port_ret + (1 - alpha) * ema_mean
        ema_var = (1 - alpha) * (ema_var + alpha * (port_ret - ema_mean) ** 2)

    ema_std = np.sqrt(max(ema_var, 1e-8))

    # Online Sharpe signal (annualized scaling not needed, relative is fine)
    sharpe_signal = ema_mean / ema_std

    # Rolling window for tail risk (CVaR)
    ret_history.append(port_ret)
    window = 60
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    # CVaR penalty (expected shortfall at 10%)
    cvar_penalty = 0.0
    if len(ret_history) >= 10:
        arr = np.array(ret_history)
        cutoff = np.percentile(arr, 10)
        tail = arr[arr <= cutoff]
        if len(tail) > 0:
            cvar_10 = np.mean(tail)  # negative number
            cvar_penalty = min(cvar_10, 0.0)  # only penalize losses

    # Turnover penalty (encourages stable allocations)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.1 * turnover

    # Concentration penalty (encourage diversification)
    # Herfindahl index on non-cash weights
    hhi = np.sum(weights ** 2)
    concentration_penalty = -0.05 * hhi

    # Combine components
    # Scale sharpe_signal to be primary driver
    sharpe_component = np.clip(sharpe_signal, -3.0, 3.0)

    # CVaR penalty scaled
    cvar_component = 2.0 * cvar_penalty  # amplify tail risk penalty

    total = (
        sharpe_component
        + cvar_component
        + turnover_penalty
        + concentration_penalty
    )

    components = {
        "sharpe_signal": float(sharpe_component),
        "cvar_penalty": float(cvar_component),
        "turnover_penalty": float(turnover_penalty),
        "concentration_penalty": float(concentration_penalty),
        "port_ret": float(port_ret),
        "ema_mean": float(ema_mean),
        "ema_std": float(ema_std),
    }

    state["ema_mean"] = ema_mean
    state["ema_var"] = ema_var
    state["step"] = step + 1
    state["ret_history"] = ret_history

    return float(total), components, state