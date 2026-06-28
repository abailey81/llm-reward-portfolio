def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize state
    state = info.get("reward_state")
    if state is None:
        state = {
            "returns_history": [],
            "portfolio_value": 1.0,
            "peak_value": 1.0,
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "step": 0,
            "alpha": 0.05,  # EMA decay for online stats
        }

    alpha = state["alpha"]
    step = state["step"]

    # Update portfolio value and peak
    pv = state["portfolio_value"] * (1.0 + port_ret)
    peak = max(state["peak_value"], pv)
    drawdown = (peak - pv) / (peak + 1e-8)

    # Online EMA of return and squared return for Sharpe estimation
    ema_ret = alpha * port_ret + (1 - alpha) * state["ema_ret"]
    ema_sq = alpha * (port_ret ** 2) + (1 - alpha) * state["ema_sq"]

    # Variance and std from EMA
    variance = max(ema_sq - ema_ret ** 2, 1e-8)
    std = np.sqrt(variance)

    # Sharpe-like signal: mean / std, scaled
    sharpe_signal = ema_ret / std

    # Turnover penalty (transaction costs)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.1 * turnover

    # Drawdown penalty (convex to punish deep drawdowns)
    dd_penalty = 2.0 * (drawdown ** 2)

    # Tail loss: penalize large negative returns (CVaR-like)
    tail_threshold = -0.02
    tail_loss = min(0.0, port_ret - tail_threshold)
    tail_penalty = 3.0 * abs(tail_loss) if port_ret < tail_threshold else 0.0

    # Concentration penalty to encourage diversification
    cash_weight = weights[-1] if len(weights) > 0 else 0.0
    asset_weights = weights[:-1]
    hhi = np.sum(asset_weights ** 2)  # Herfindahl index
    concentration_penalty = 0.1 * hhi

    # Main reward components
    # 1. Sharpe contribution (main driver)
    sharpe_component = sharpe_signal * 0.5

    # 2. Direct return signal (scaled)
    ret_component = port_ret * 10.0

    # 3. Combine
    total = (
        sharpe_component
        + ret_component
        - turnover_penalty
        - dd_penalty
        - tail_penalty
        - concentration_penalty
    )

    # Update state
    state["portfolio_value"] = pv
    state["peak_value"] = peak
    state["ema_ret"] = ema_ret
    state["ema_sq"] = ema_sq
    state["step"] = step + 1

    components = {
        "sharpe_signal": sharpe_component,
        "ret_component": ret_component,
        "turnover_penalty": -turnover_penalty,
        "drawdown_penalty": -dd_penalty,
        "tail_penalty": -tail_penalty,
        "concentration_penalty": -concentration_penalty,
        "drawdown": drawdown,
        "ema_ret": ema_ret,
        "ema_std": std,
    }

    return float(total), components, state