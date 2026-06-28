def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 0.0,
            "cum_ret": 0.0,
        }

    # Update cumulative return and peak
    state["cum_ret"] = state["cum_ret"] + port_ret
    if state["cum_ret"] > state["peak"]:
        state["peak"] = state["cum_ret"]

    # Track return history (rolling window)
    state["ret_history"].append(port_ret)
    window = 60
    if len(state["ret_history"]) > window:
        state["ret_history"].pop(0)

    hist = np.array(state["ret_history"])

    # --- Component 1: Online Sharpe (primary signal) ---
    if len(hist) >= 5:
        mean_r = np.mean(hist)
        std_r = np.std(hist) + 1e-8
        sharpe_component = mean_r / std_r
    else:
        sharpe_component = port_ret * 10.0

    # --- Component 2: Drawdown penalty ---
    drawdown = state["peak"] - state["cum_ret"]
    drawdown_penalty = -0.5 * drawdown if drawdown > 0 else 0.0

    # --- Component 3: Turnover penalty (transaction costs proxy) ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.1 * turnover

    # --- Component 4: Tail loss penalty (CVaR-like) ---
    if len(hist) >= 10:
        var_threshold = np.percentile(hist, 10)
        tail_losses = hist[hist < var_threshold]
        cvar_penalty = -0.3 * abs(np.mean(tail_losses)) if len(tail_losses) > 0 else 0.0
    else:
        cvar_penalty = 0.0

    # --- Component 5: Concentration penalty (encourage diversification) ---
    # Penalize extreme concentration (but not too harshly)
    hhi = np.sum(weights ** 2)
    concentration_penalty = -0.05 * hhi

    total = (
        sharpe_component
        + drawdown_penalty
        + turnover_penalty
        + cvar_penalty
        + concentration_penalty
    )

    components = {
        "sharpe_component": float(sharpe_component),
        "drawdown_penalty": float(drawdown_penalty),
        "turnover_penalty": float(turnover_penalty),
        "cvar_penalty": float(cvar_penalty),
        "concentration_penalty": float(concentration_penalty),
    }

    return float(total), components, state