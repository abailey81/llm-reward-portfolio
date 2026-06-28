def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_history": [],
            "portfolio_value": 1.0,
            "peak_value": 1.0,
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "step": 0,
        }

    state["step"] += 1
    step = state["step"]
    alpha = 0.06  # EMA decay for ~16-step half-life

    # Update EMA for online Sharpe
    state["ema_ret"] = (1 - alpha) * state["ema_ret"] + alpha * port_ret
    state["ema_sq"] = (1 - alpha) * state["ema_sq"] + alpha * (port_ret ** 2)

    # Online Sharpe estimate
    ema_var = state["ema_sq"] - state["ema_ret"] ** 2
    ema_std = np.sqrt(max(ema_var, 1e-8))
    online_sharpe = state["ema_ret"] / ema_std

    # Store return history for CVaR calculation
    state["returns_history"].append(port_ret)
    hist = np.array(state["returns_history"])

    # Update portfolio value and drawdown
    state["portfolio_value"] *= (1 + port_ret)
    state["peak_value"] = max(state["peak_value"], state["portfolio_value"])
    drawdown = (state["portfolio_value"] - state["peak_value"]) / state["peak_value"]

    # CVaR penalty: tail loss (worst 10% of returns so far)
    cvar_penalty = 0.0
    if len(hist) >= 10:
        cutoff = int(np.floor(0.10 * len(hist)))
        cutoff = max(cutoff, 1)
        sorted_rets = np.sort(hist)
        cvar_5 = np.mean(sorted_rets[:cutoff])
        cvar_penalty = min(cvar_5, 0.0)  # negative value = penalty

    # Turnover penalty
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.5 * turnover

    # Concentration penalty (encourage diversification)
    n_assets = len(weights)
    hhi = np.sum(weights ** 2)
    max_hhi = 1.0
    min_hhi = 1.0 / n_assets
    concentration_penalty = -0.3 * (hhi - min_hhi) / (max_hhi - min_hhi + 1e-8)

    # Drawdown penalty
    drawdown_penalty = 2.0 * drawdown  # drawdown is negative, so this adds a penalty

    # Combine components
    # Scale Sharpe contribution (clipped to avoid extremes)
    sharpe_component = np.clip(online_sharpe, -3.0, 3.0) * 0.3

    # Direct return component (scaled)
    return_component = port_ret * 10.0

    # CVaR penalty scaled
    cvar_component = 3.0 * cvar_penalty

    total = (
        return_component
        + sharpe_component
        + cvar_component
        + turnover_penalty
        + concentration_penalty
        + drawdown_penalty
    )

    components = {
        "return": return_component,
        "sharpe": sharpe_component,
        "cvar_penalty": cvar_component,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
        "drawdown_penalty": drawdown_penalty,
    }

    return float(total), components, state