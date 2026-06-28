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

    # Update state
    state["step"] += 1
    state["cum_value"] *= (1.0 + port_ret)
    state["peak"] = max(state["peak"], state["cum_value"])
    state["ret_history"].append(port_ret)

    # Keep a rolling window
    window = 120
    hist = state["ret_history"][-window:]
    n = len(hist)
    hist_arr = np.array(hist)

    # --- Component 1: Smoothed return signal ---
    # Use exponential weighting to emphasize recent returns
    ret_signal = port_ret

    # --- Component 2: Online Sortino ratio (penalize downside variance) ---
    if n >= 8:
        mean_ret = np.mean(hist_arr)
        downside = hist_arr[hist_arr < 0.0]
        if len(downside) >= 2:
            downside_std = np.std(downside)
            sortino = mean_ret / (downside_std + 1e-8)
        else:
            sortino = mean_ret / (np.std(hist_arr) + 1e-8)
        # Clip to avoid extreme values
        sortino = np.clip(sortino, -3.0, 3.0)
    else:
        sortino = 0.0

    # --- Component 3: CVaR penalty (tail risk) ---
    if n >= 20:
        sorted_rets = np.sort(hist_arr)
        tail_idx = max(1, int(0.05 * n))
        cvar = np.mean(sorted_rets[:tail_idx])
        # Penalize negative CVaR
        cvar_penalty = min(0.0, cvar)
    else:
        cvar_penalty = 0.0

    # --- Component 4: Drawdown penalty ---
    drawdown = (state["cum_value"] - state["peak"]) / (state["peak"] + 1e-8)
    # Only penalize if in drawdown
    dd_penalty = min(0.0, drawdown)

    # --- Component 5: Turnover penalty (transaction costs already in port_ret,
    #     but extra regularization toward stable allocation) ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.005 * turnover

    # --- Component 6: Concentration penalty (encourage diversification) ---
    # Herfindahl index penalizes concentration
    n_assets = len(weights)
    hhi = np.sum(weights ** 2)
    min_hhi = 1.0 / n_assets  # perfectly diversified
    concentration_penalty = -0.02 * (hhi - min_hhi)

    # --- Combine components with adaptive scaling ---
    step = state["step"]

    # Warm-up: rely more on raw return early, shift to risk-adjusted later
    warmup = min(1.0, step / 60.0)

    # Base: direct return (always present)
    base = ret_signal * 10.0  # scale up small returns

    # Risk-adjusted overlay (grows in after warmup)
    risk_adj = warmup * (
        0.5 * sortino
        + 8.0 * cvar_penalty
        + 3.0 * dd_penalty
    )

    total = base + risk_adj + turnover_penalty + concentration_penalty

    components = {
        "ret_signal": base,
        "sortino_component": 0.5 * sortino * warmup,
        "cvar_penalty": 8.0 * cvar_penalty * warmup,
        "drawdown_penalty": 3.0 * dd_penalty * warmup,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
    }

    return float(total), components, state