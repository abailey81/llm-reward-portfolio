def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cumulative": 1.0,
            "step": 0,
        }

    state["step"] += 1
    state["cumulative"] *= (1.0 + port_ret)
    state["peak"] = max(state["peak"], state["cumulative"])

    # Keep a rolling window of returns for Sharpe estimation
    window = 252
    state["ret_history"].append(port_ret)
    if len(state["ret_history"]) > window:
        state["ret_history"].pop(0)

    hist = np.array(state["ret_history"], dtype=np.float64)

    # --- Component 1: Sharpe-based signal ---
    if len(hist) >= 2:
        mu = np.mean(hist)
        sigma = np.std(hist, ddof=1)
        sigma = max(sigma, 1e-8)
        sharpe_signal = mu / sigma  # daily Sharpe, no annualisation needed for RL signal
    else:
        sharpe_signal = port_ret  # fallback first step

    # --- Component 2: Drawdown penalty ---
    drawdown = (state["peak"] - state["cumulative"]) / (state["peak"] + 1e-8)
    dd_penalty = -drawdown  # negative when in drawdown

    # --- Component 3: Turnover cost penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    # Typical transaction cost ~10bps per unit turnover
    cost_penalty = -0.001 * turnover

    # --- Component 4: Tail-risk penalty (CVaR on recent returns) ---
    if len(hist) >= 10:
        var_level = np.percentile(hist, 5)  # 5th percentile = VaR5
        tail_returns = hist[hist <= var_level]
        cvar = np.mean(tail_returns) if len(tail_returns) > 0 else var_level
        tail_penalty = cvar  # already negative for losses
    else:
        tail_penalty = 0.0

    # --- Blend components ---
    # Primary driver: Sharpe signal; secondary: drawdown + tail risk
    total = (
        0.5 * sharpe_signal
        + 0.3 * dd_penalty
        + 0.1 * tail_penalty
        + 0.1 * cost_penalty
    )

    components = {
        "sharpe_signal": float(sharpe_signal),
        "dd_penalty": float(dd_penalty),
        "cost_penalty": float(cost_penalty),
        "tail_penalty": float(tail_penalty),
        "port_ret": float(port_ret),
    }

    return float(total), components, state