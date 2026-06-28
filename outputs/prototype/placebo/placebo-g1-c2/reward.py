def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize/retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_history": [],
            "peak": 0.0,
            "cumulative": 0.0,
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "alpha": 0.05,  # EMA decay for ~20-step window
            "step": 0,
        }

    alpha = state["alpha"]
    step = state["step"]

    # Update EMA of returns and squared returns for online Sharpe
    ema_ret = state["ema_ret"]
    ema_sq = state["ema_sq"]

    if step == 0:
        ema_ret = port_ret
        ema_sq = port_ret ** 2
    else:
        ema_ret = alpha * port_ret + (1 - alpha) * ema_ret
        ema_sq = alpha * (port_ret ** 2) + (1 - alpha) * ema_sq

    # Online Sharpe estimate
    ema_var = max(ema_sq - ema_ret ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)
    sharpe_signal = ema_ret / ema_std

    # Track cumulative return and drawdown
    cumulative = state["cumulative"] + port_ret
    peak = max(state["peak"], cumulative)
    drawdown = peak - cumulative  # always >= 0

    # Append return to history for CVaR
    returns_history = state["returns_history"] + [port_ret]
    if len(returns_history) > 100:
        returns_history = returns_history[-100:]

    # CVaR (expected shortfall at 5% tail)
    hist_arr = np.array(returns_history)
    if len(hist_arr) >= 10:
        cutoff = np.percentile(hist_arr, 5)
        tail = hist_arr[hist_arr <= cutoff]
        cvar = float(np.mean(tail)) if len(tail) > 0 else 0.0
    else:
        cvar = 0.0

    # Turnover penalty (transaction costs)
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = 0.1 * turnover

    # Drawdown penalty (nonlinear to penalize large drawdowns more)
    drawdown_penalty = 0.5 * (drawdown ** 2)

    # CVaR penalty
    cvar_penalty = max(-cvar, 0.0) * 2.0

    # Concentration penalty (discourage extreme concentration)
    n = len(weights)
    entropy = -np.sum(weights * np.log(np.clip(weights, 1e-8, 1.0)))
    max_entropy = np.log(n)
    concentration_penalty = 0.05 * (max_entropy - entropy) / max(max_entropy, 1e-8)

    # Core return signal scaled by online Sharpe direction
    # Use a blend: direct return + Sharpe signal
    ret_signal = port_ret
    sharpe_bonus = 0.3 * np.tanh(sharpe_signal)

    total = (
        ret_signal
        + sharpe_bonus
        - turnover_penalty
        - drawdown_penalty
        - cvar_penalty
        - concentration_penalty
    )

    components = {
        "ret_signal": ret_signal,
        "sharpe_bonus": sharpe_bonus,
        "turnover_penalty": -turnover_penalty,
        "drawdown_penalty": -drawdown_penalty,
        "cvar_penalty": -cvar_penalty,
        "concentration_penalty": -concentration_penalty,
    }

    state["ema_ret"] = ema_ret
    state["ema_sq"] = ema_sq
    state["cumulative"] = cumulative
    state["peak"] = peak
    state["returns_history"] = returns_history
    state["step"] = step + 1

    return float(total), components, state