def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_hist": [],
            "peak": 0.0,
            "cum_ret": 0.0,
        }

    # Update cumulative return (log-approx)
    state["cum_ret"] += port_ret
    state["peak"] = max(state["peak"], state["cum_ret"])

    # Store recent returns for variance estimation
    state["ret_hist"].append(port_ret)
    if len(state["ret_hist"]) > 60:
        state["ret_hist"].pop(0)

    hist = state["ret_hist"]
    n = len(hist)

    # --- Component 1: Realized return (clipped to avoid huge spikes) ---
    ret_component = np.clip(port_ret, -0.15, 0.15)

    # --- Component 2: Variance penalty (online estimate) ---
    if n >= 8:
        arr = np.array(hist)
        mean_r = np.mean(arr)
        var_r = np.mean((arr - mean_r) ** 2)
        std_r = np.sqrt(var_r + 1e-8)
        # Sharpe-like: reward mean, penalize std
        sharpe_bonus = mean_r / (std_r + 1e-8)
        # Scale sharpe_bonus to be comparable to ret_component
        var_penalty = -0.5 * var_r * 100  # penalize variance
    else:
        sharpe_bonus = 0.0
        var_penalty = 0.0

    # --- Component 3: Drawdown penalty ---
    drawdown = state["peak"] - state["cum_ret"]
    drawdown_penalty = -0.5 * max(drawdown, 0.0)

    # --- Component 4: Turnover penalty (encourages stability) ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.05 * turnover

    # --- Component 5: Downside / tail penalty ---
    if n >= 8:
        arr = np.array(hist)
        downside = arr[arr < 0]
        if len(downside) > 0:
            cvar = np.mean(downside)  # negative number
            tail_penalty = 0.3 * cvar  # further penalize tail losses
        else:
            tail_penalty = 0.0
    else:
        tail_penalty = 0.0

    # --- Combine: primary signal is port_ret, with risk adjustments ---
    # Weight the sharpe_bonus lightly to provide directional guidance
    sharpe_weight = 0.05
    total = (
        ret_component
        + sharpe_weight * sharpe_bonus
        + var_penalty
        + drawdown_penalty
        + turnover_penalty
        + tail_penalty
    )

    components = {
        "ret": ret_component,
        "sharpe_bonus": sharpe_bonus * sharpe_weight,
        "var_penalty": var_penalty,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
        "tail_penalty": tail_penalty,
    }

    return float(total), components, state