def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 0.0,
            "cum_ret": 0.0,
            "step": 0,
        }

    state["step"] += 1
    state["ret_history"].append(port_ret)
    # Keep a rolling window of returns
    window = 200
    if len(state["ret_history"]) > window:
        state["ret_history"] = state["ret_history"][-window:]

    hist = np.array(state["ret_history"])

    # --- Component 1: Sortino-based signal ---
    n = len(hist)
    mean_ret = np.mean(hist)
    downside = hist[hist < 0.0]
    if len(downside) >= 2:
        downside_std = np.std(downside)
    else:
        downside_std = 1e-4
    downside_std = max(downside_std, 1e-5)
    sortino = mean_ret / downside_std
    # Scale sortino to a reasonable reward range
    sortino_reward = np.clip(sortino, -3.0, 3.0) * 0.5

    # --- Component 2: CVaR penalty (tail risk) ---
    cvar_threshold = max(1, int(0.05 * n))  # 5% tail
    sorted_hist = np.sort(hist)
    cvar_5 = np.mean(sorted_hist[:cvar_threshold])
    cvar_penalty = np.clip(cvar_5, -0.1, 0.0) * 5.0  # negative penalty

    # --- Component 3: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.1 * turnover

    # --- Component 4: Drawdown penalty ---
    state["cum_ret"] = state["cum_ret"] + port_ret
    if state["cum_ret"] > state["peak"]:
        state["peak"] = state["cum_ret"]
    drawdown = state["cum_ret"] - state["peak"]  # <= 0
    drawdown_penalty = np.clip(drawdown, -0.5, 0.0) * 0.2

    # --- Component 5: Direct return signal (scaled) ---
    # Mild direct return encouragement
    direct_ret = np.clip(port_ret, -0.05, 0.05) * 2.0

    # --- Total ---
    # In early steps, rely more on direct return; later on risk-adjusted
    warmup = min(state["step"] / 50.0, 1.0)
    risk_adjusted = warmup * (sortino_reward + cvar_penalty + drawdown_penalty) + direct_ret + turnover_penalty

    total = float(risk_adjusted)

    components = {
        "sortino_reward": float(sortino_reward),
        "cvar_penalty": float(cvar_penalty),
        "turnover_penalty": float(turnover_penalty),
        "drawdown_penalty": float(drawdown_penalty),
        "direct_ret": float(direct_ret),
        "warmup": float(warmup),
    }

    return total, components, state