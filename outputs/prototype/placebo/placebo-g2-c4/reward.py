def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cum_value": 1.0,
            "step": 0,
        }

    state["step"] += 1
    state["ret_history"].append(port_ret)
    state["cum_value"] *= (1.0 + port_ret)
    state["peak"] = max(state["peak"], state["cum_value"])

    ret_hist = np.array(state["ret_history"])
    n = len(ret_hist)

    # --- Component 1: Online Sharpe (primary signal) ---
    window = min(n, 60)
    recent = ret_hist[-window:]
    mean_r = np.mean(recent)
    std_r = np.std(recent) + 1e-8
    sharpe_component = mean_r / std_r  # ~annualizable ratio

    # --- Component 2: Drawdown penalty ---
    dd = (state["peak"] - state["cum_value"]) / (state["peak"] + 1e-8)
    drawdown_penalty = -dd * 0.5

    # --- Component 3: Turnover / transaction cost penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.01 * turnover

    # --- Component 4: CVaR / tail risk penalty ---
    if n >= 20:
        tail_window = ret_hist[-min(n, 60):]
        var_5 = np.percentile(tail_window, 5)
        cvar = np.mean(tail_window[tail_window <= var_5]) if np.any(tail_window <= var_5) else var_5
        tail_penalty = 0.1 * cvar  # cvar is negative, so this penalizes
    else:
        tail_penalty = 0.0

    # --- Component 5: Concentration penalty (encourage diversification) ---
    # Penalize extreme concentration (Herfindahl index)
    n_assets = len(weights)
    hhi = np.sum(weights ** 2)
    # Normalize: max concentration = 1.0, uniform = 1/n_assets
    hhi_penalty = -0.05 * (hhi - 1.0 / n_assets)

    # --- Total reward ---
    # Primary: Sharpe signal + supporting penalties
    total = (
        sharpe_component
        + drawdown_penalty
        + turnover_penalty
        + tail_penalty
        + hhi_penalty
    )

    components = {
        "sharpe_component": float(sharpe_component),
        "drawdown_penalty": float(drawdown_penalty),
        "turnover_penalty": float(turnover_penalty),
        "tail_penalty": float(tail_penalty),
        "hhi_penalty": float(hhi_penalty),
        "port_ret": float(port_ret),
    }

    return float(total), components, state