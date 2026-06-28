def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_history": [],
            "step": 0,
            "ema_mean": 0.0,
            "ema_var": 1e-6,
            "ema_alpha": 0.05,
        }

    state["step"] += 1
    alpha = state["ema_alpha"]

    # Update EMA mean and variance of portfolio returns
    r = float(port_ret)
    prev_mean = state["ema_mean"]
    prev_var = state["ema_var"]

    new_mean = (1 - alpha) * prev_mean + alpha * r
    new_var = (1 - alpha) * prev_var + alpha * (r - prev_mean) ** 2
    new_var = max(new_var, 1e-8)

    state["ema_mean"] = new_mean
    state["ema_var"] = new_var

    # Keep a rolling window for CVaR estimation
    history = state["returns_history"]
    history.append(r)
    if len(history) > 200:
        history.pop(0)
    state["returns_history"] = history

    # --- Component 1: EMA Sharpe signal ---
    ema_sharpe = new_mean / np.sqrt(new_var)

    # --- Component 2: Incremental return reward (scaled) ---
    # Annualized approximation: encourage positive returns
    ret_reward = r * 100.0  # scale up small daily returns

    # --- Component 3: CVaR penalty (tail risk) ---
    cvar_penalty = 0.0
    if len(history) >= 20:
        arr = np.array(history)
        cutoff_5 = np.percentile(arr, 5)
        tail = arr[arr <= cutoff_5]
        if len(tail) > 0:
            cvar_5 = float(np.mean(tail))
            # Penalize negative CVaR (losses in the tail)
            cvar_penalty = min(cvar_5, 0.0) * 50.0  # negative contribution

    # --- Component 4: Turnover penalty ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = -0.5 * turnover

    # --- Component 5: Concentration penalty (encourage diversification) ---
    # Penalize extreme concentration (Herfindahl index)
    hhi = float(np.sum(weights ** 2))
    n = len(weights)
    hhi_min = 1.0 / n  # perfectly diversified
    concentration_penalty = -0.5 * (hhi - hhi_min)

    # --- Total reward ---
    # Weight components carefully
    # Primary: Sharpe-like signal; secondary: raw return; tertiary: penalties
    sharpe_weight = 2.0
    ret_weight = 0.3
    cvar_weight = 1.0
    turn_weight = 1.0
    conc_weight = 1.0

    total = (
        sharpe_weight * ema_sharpe
        + ret_weight * ret_reward
        + cvar_weight * cvar_penalty
        + turn_weight * turnover_penalty
        + conc_weight * concentration_penalty
    )

    components = {
        "ema_sharpe": float(ema_sharpe),
        "ret_reward": float(ret_reward),
        "cvar_penalty": float(cvar_penalty),
        "turnover_penalty": float(turnover_penalty),
        "concentration_penalty": float(concentration_penalty),
    }

    return float(total), components, state