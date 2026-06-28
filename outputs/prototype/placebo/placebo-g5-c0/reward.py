def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_history": [],
            "peak": 0.0,
            "cum_ret": 0.0,
            "ema_ret": 0.0,
            "ema_sq_ret": 0.0,
            "alpha": 0.05,  # EMA decay (fast)
            "alpha_slow": 0.01,  # slow EMA
        }

    alpha = state["alpha"]
    alpha_slow = state["alpha_slow"]

    # Update cumulative return and peak for drawdown
    state["cum_ret"] = state["cum_ret"] + port_ret + state["cum_ret"] * port_ret  # compound
    state["peak"] = max(state["peak"], state["cum_ret"])

    # Drawdown from peak
    drawdown = state["peak"] - state["cum_ret"]

    # Update EMA of returns and squared returns for running Sharpe
    state["ema_ret"] = (1 - alpha) * state["ema_ret"] + alpha * port_ret
    state["ema_sq_ret"] = (1 - alpha) * state["ema_sq_ret"] + alpha * (port_ret ** 2)

    # Store returns history (keep last 100)
    state["returns_history"].append(port_ret)
    if len(state["returns_history"]) > 100:
        state["returns_history"].pop(0)

    hist = state["returns_history"]

    # --- Compute reward components ---

    # 1. Base: portfolio return (net of costs already in port_ret)
    ret_component = port_ret

    # 2. Running Sharpe signal (EMA-based)
    ema_var = state["ema_sq_ret"] - state["ema_ret"] ** 2
    ema_std = np.sqrt(max(ema_var, 1e-8))
    sharpe_component = state["ema_ret"] / ema_std

    # 3. Drawdown penalty
    drawdown_penalty = -drawdown * 2.0

    # 4. Turnover penalty (proxy for transaction costs)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.1 * turnover

    # 5. Tail loss penalty (downside semi-deviation from history)
    if len(hist) >= 10:
        hist_arr = np.array(hist)
        downside = hist_arr[hist_arr < 0]
        if len(downside) > 0:
            tail_penalty = -0.5 * np.mean(downside ** 2) / max(np.var(hist_arr), 1e-8)
        else:
            tail_penalty = 0.0
        # CVaR-like: mean of worst 10%
        n_tail = max(1, int(0.1 * len(hist_arr)))
        sorted_r = np.sort(hist_arr)
        cvar = np.mean(sorted_r[:n_tail])
        cvar_penalty = -0.5 * max(-cvar, 0)
    else:
        tail_penalty = 0.0
        cvar_penalty = 0.0

    # 6. Concentration penalty (encourage diversification, penalize extreme weights)
    # Herfindahl index
    hhi = np.sum(weights ** 2)
    n = len(weights)
    hhi_penalty = -0.05 * (hhi - 1.0 / n)

    # Combine: primary signal is Sharpe-based, supplemented by other terms
    # Scale sharpe to be in similar range as ret
    sharpe_scaled = np.clip(sharpe_component, -3.0, 3.0) * 0.01

    total = (
        0.4 * ret_component
        + 0.3 * sharpe_scaled
        + 0.15 * drawdown_penalty
        + 0.05 * turnover_penalty
        + 0.05 * tail_penalty
        + 0.03 * cvar_penalty
        + 0.02 * hhi_penalty
    )

    components = {
        "ret": ret_component,
        "sharpe_ema": sharpe_scaled,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
        "tail_penalty": tail_penalty,
        "cvar_penalty": cvar_penalty,
        "hhi_penalty": hhi_penalty,
    }

    return total, components, state