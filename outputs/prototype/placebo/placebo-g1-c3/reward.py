def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_history": [],
            "peak": 1.0,
            "cum_value": 1.0,
            "step": 0,
        }

    state["step"] += 1

    # Update cumulative portfolio value and drawdown tracking
    state["cum_value"] = state["cum_value"] * (1.0 + port_ret)
    state["peak"] = max(state["peak"], state["cum_value"])
    current_drawdown = (state["cum_value"] - state["peak"]) / (state["peak"] + 1e-8)

    # Keep a rolling window of returns for risk estimation
    window = 60
    state["returns_history"].append(port_ret)
    if len(state["returns_history"]) > window:
        state["returns_history"].pop(0)

    hist = np.array(state["returns_history"])
    n = len(hist)

    # --- Component 1: Smoothed return signal ---
    ret_component = port_ret

    # --- Component 2: Online Sharpe-based signal (annualized) ---
    if n >= 8:
        mu = np.mean(hist)
        sigma = np.std(hist, ddof=1) + 1e-8
        sharpe_signal = mu / sigma
        # Scale down to be in same ballpark as returns
        sharpe_component = np.clip(sharpe_signal * 0.05, -0.5, 0.5)
    else:
        sharpe_component = 0.0

    # --- Component 3: Drawdown penalty ---
    # Penalize being in drawdown — quadratic to punish deep drawdowns more
    drawdown_penalty = 2.0 * current_drawdown  # current_drawdown <= 0, so this is <= 0

    # --- Component 4: CVaR / tail loss penalty ---
    if n >= 16:
        # 5th percentile tail (CVaR-like)
        tail_cutoff = np.percentile(hist, 10)
        tail_returns = hist[hist <= tail_cutoff]
        cvar = np.mean(tail_returns) if len(tail_returns) > 0 else 0.0
        tail_penalty = np.clip(cvar * 2.0, -0.5, 0.0)
    else:
        tail_penalty = 0.0

    # --- Component 5: Turnover penalty (transaction costs already in port_ret,
    #     but extra penalty for excessive churning) ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.001 * turnover

    # --- Component 6: Concentration penalty (encourage diversification) ---
    # Penalize highly concentrated portfolios via Herfindahl index
    herfindahl = np.sum(weights ** 2)
    n_assets = len(weights)
    # Normalized: 0 = perfectly diversified, 1 = fully concentrated
    herfindahl_norm = (herfindahl - 1.0 / n_assets) / (1.0 - 1.0 / n_assets + 1e-8)
    concentration_penalty = -0.005 * np.clip(herfindahl_norm, 0, 1)

    # --- Total reward ---
    # Primary driver: return + Sharpe signal
    # Secondary: risk penalties
    total = (
        ret_component
        + sharpe_component
        + drawdown_penalty
        + tail_penalty
        + turnover_penalty
        + concentration_penalty
    )

    components = {
        "ret": ret_component,
        "sharpe_signal": sharpe_component,
        "drawdown_penalty": drawdown_penalty,
        "tail_penalty": tail_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
    }

    return float(total), components, state