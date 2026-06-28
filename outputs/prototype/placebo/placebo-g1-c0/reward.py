def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve state
    state = info.get("reward_state")
    if state is None:
        state = {
            "mean": 0.0,
            "M2": 0.0,        # for Welford's online variance
            "n": 0,
            "peak": 1.0,
            "cum_ret": 1.0,
        }

    n = state["n"] + 1
    # Welford's online mean and variance
    delta = port_ret - state["mean"]
    mean = state["mean"] + delta / n
    delta2 = port_ret - mean
    M2 = state["M2"] + delta * delta2

    # Update cumulative return and drawdown tracking
    cum_ret = state["cum_ret"] * (1.0 + port_ret)
    peak = max(state["peak"], cum_ret)
    drawdown = (peak - cum_ret) / peak  # 0 = at peak, positive = underwater

    # --- Components ---

    # 1. Online Sharpe-like signal: mean / std of returns
    if n >= 2:
        var = M2 / (n - 1)
        std = np.sqrt(var) if var > 0 else 1e-8
        sharpe_signal = mean / std
    else:
        sharpe_signal = 0.0

    # 2. Incremental return contribution (scaled)
    ret_component = port_ret * 10.0  # amplify signal

    # 3. Drawdown penalty — penalize being underwater
    dd_penalty = -drawdown * 2.0

    # 4. Turnover cost awareness (encourage stability)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -turnover * 0.5

    # 5. Concentration penalty (encourage diversification to reduce tail risk)
    # Exclude cash (last element) from concentration measure
    asset_weights = weights[:-1]
    herfindahl = np.sum(asset_weights ** 2)
    n_assets = len(asset_weights)
    min_herf = 1.0 / n_assets if n_assets > 0 else 1.0
    concentration_penalty = -(herfindahl - min_herf) * 1.0

    # Total reward — weighted combination
    # Sharpe signal is the primary driver after enough data
    if n < 10:
        total = ret_component + dd_penalty + turnover_penalty
    else:
        total = (
            sharpe_signal * 1.0
            + ret_component * 0.5
            + dd_penalty * 1.0
            + turnover_penalty * 0.5
            + concentration_penalty * 0.3
        )

    # Update state
    state["n"] = n
    state["mean"] = mean
    state["M2"] = M2
    state["cum_ret"] = cum_ret
    state["peak"] = peak

    components = {
        "sharpe_signal": float(sharpe_signal),
        "ret_component": float(ret_component),
        "dd_penalty": float(dd_penalty),
        "turnover_penalty": float(turnover_penalty),
        "concentration_penalty": float(concentration_penalty),
        "drawdown": float(drawdown),
    }

    return float(total), components, state