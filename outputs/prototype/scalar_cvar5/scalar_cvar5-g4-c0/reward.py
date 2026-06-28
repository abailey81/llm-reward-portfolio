def reward(weights, returns, prev_weights, port_ret, info):
    # --- Retrieve or initialize state ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cum_ret": 1.0,
            "n": 0,
        }

    ret_history = state["ret_history"]
    peak = state["peak"]
    cum_ret = state["cum_ret"]
    n = state["n"]

    # --- Update cumulative state ---
    ret_history.append(port_ret)
    cum_ret = cum_ret * (1.0 + port_ret)
    peak = max(peak, cum_ret)
    n += 1

    # Keep only recent window for stats (rolling 60 steps)
    window = 60
    recent = ret_history[-window:]

    # --- Component 1: Incremental Sharpe contribution ---
    if len(recent) >= 4:
        mu = np.mean(recent)
        sigma = np.std(recent, ddof=1)
        sigma = max(sigma, 1e-8)
        sharpe_contrib = mu / sigma
    else:
        # Early steps: just use raw return, scaled down
        sharpe_contrib = port_ret * 5.0

    # --- Component 2: CVaR penalty (expected shortfall at 5%) ---
    cvar_penalty = 0.0
    if len(recent) >= 10:
        arr = np.array(recent)
        cutoff = np.percentile(arr, 5)
        tail = arr[arr <= cutoff]
        if len(tail) > 0:
            cvar = np.mean(tail)
            # Penalize negative CVaR
            cvar_penalty = min(cvar, 0.0) * 2.0  # negative contribution
    else:
        # Penalize large negative individual returns in early steps
        cvar_penalty = min(port_ret, 0.0) * 0.5

    # --- Component 3: Drawdown penalty ---
    if peak > 1e-8:
        drawdown = (peak - cum_ret) / peak
    else:
        drawdown = 0.0
    drawdown_penalty = -drawdown * 0.5

    # --- Component 4: Turnover penalty (transaction costs already in port_ret,
    #     but we add extra discouragement of churn) ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -turnover * 0.05

    # --- Component 5: Concentration penalty (encourage diversification) ---
    # Herfindahl index on risky assets (exclude last element = cash)
    risky_w = weights[:-1] if len(weights) > 1 else weights
    hhi = np.sum(risky_w ** 2)
    n_assets = len(risky_w)
    min_hhi = 1.0 / max(n_assets, 1)
    concentration_penalty = -(hhi - min_hhi) * 0.1

    # --- Total reward ---
    total = (
        sharpe_contrib
        + cvar_penalty
        + drawdown_penalty
        + turnover_penalty
        + concentration_penalty
    )

    components = {
        "sharpe_contrib": float(sharpe_contrib),
        "cvar_penalty": float(cvar_penalty),
        "drawdown_penalty": float(drawdown_penalty),
        "turnover_penalty": float(turnover_penalty),
        "concentration_penalty": float(concentration_penalty),
    }

    reward_state = {
        "ret_history": ret_history,
        "peak": float(peak),
        "cum_ret": float(cum_ret),
        "n": n,
    }

    return float(total), components, reward_state