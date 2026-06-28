def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve reward state
    state = info.get("reward_state")
    if state is None:
        state = {
            "returns_history": [],
            "peak": 1.0,
            "cum_value": 1.0,
            "step": 0,
        }

    # Update cumulative value and drawdown tracking
    state["cum_value"] *= (1.0 + port_ret)
    state["step"] += 1
    state["peak"] = max(state["peak"], state["cum_value"])

    # Store return in history (bounded window for stationarity)
    window = 60
    state["returns_history"].append(float(port_ret))
    if len(state["returns_history"]) > window:
        state["returns_history"].pop(0)

    hist = np.array(state["returns_history"], dtype=np.float64)
    n = len(hist)

    # --- Component 1: Sharpe-based signal ---
    if n >= 8:
        mu = np.mean(hist)
        sigma = np.std(hist, ddof=1) + 1e-8
        sharpe_signal = mu / sigma  # per-step Sharpe (unannualized)
    else:
        # Warm-up: just use return directly, scaled down
        mu = np.mean(hist) if n > 0 else port_ret
        sigma = 1e-8
        sharpe_signal = mu / (np.std(hist, ddof=0) + 1e-8) if n > 1 else 0.0

    # Scale sharpe to reasonable reward magnitude
    sharpe_reward = np.clip(sharpe_signal * 0.1, -2.0, 2.0)

    # --- Component 2: Drawdown penalty ---
    drawdown = (state["peak"] - state["cum_value"]) / (state["peak"] + 1e-8)
    drawdown_penalty = -np.clip(drawdown * 2.0, 0.0, 1.5)

    # --- Component 3: CVaR / tail-loss penalty ---
    if n >= 10:
        tail_cutoff = int(np.floor(0.1 * n))  # bottom 10%
        tail_cutoff = max(tail_cutoff, 1)
        sorted_hist = np.sort(hist)
        cvar = np.mean(sorted_hist[:tail_cutoff])
        tail_penalty = np.clip(cvar * 5.0, -2.0, 0.0)
    else:
        tail_penalty = 0.0

    # --- Component 4: Turnover / transaction cost penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -np.clip(turnover * 0.05, 0.0, 0.5)

    # --- Component 5: Concentration penalty (encourage diversification) ---
    # Penalize if heavily concentrated (Herfindahl index)
    hhi = np.sum(weights ** 2)
    n_assets = len(weights)
    min_hhi = 1.0 / n_assets  # perfectly diversified
    concentration_penalty = -np.clip((hhi - min_hhi) * 0.2, 0.0, 0.5)

    # --- Total reward ---
    # Primary driver: Sharpe signal; secondary: drawdown + tail + turnover
    total = (
        sharpe_reward
        + 0.5 * drawdown_penalty
        + 0.5 * tail_penalty
        + turnover_penalty
        + 0.3 * concentration_penalty
    )

    components = {
        "sharpe_reward": float(sharpe_reward),
        "drawdown_penalty": float(drawdown_penalty),
        "tail_penalty": float(tail_penalty),
        "turnover_penalty": float(turnover_penalty),
        "concentration_penalty": float(concentration_penalty),
    }

    return float(total), components, state