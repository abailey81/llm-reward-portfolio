def reward(weights, returns, prev_weights, port_ret, info):
    # --- Retrieve or initialize state ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cum_value": 1.0,
        }

    ret_history = state["ret_history"]
    peak = state["peak"]
    cum_value = state["cum_value"]

    # Update cumulative value and drawdown
    cum_value = cum_value * (1.0 + port_ret)
    if cum_value > peak:
        peak = cum_value
    drawdown = (peak - cum_value) / (peak + 1e-8)

    # Store return
    ret_history.append(port_ret)
    # Keep a rolling window for statistics
    window = 120
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    ret_arr = np.array(ret_history)
    n = len(ret_arr)

    # --- Component 1: Online Sharpe (annualized approximation) ---
    if n >= 8:
        mu = np.mean(ret_arr)
        sigma = np.std(ret_arr) + 1e-8
        sharpe = mu / sigma  # per-step Sharpe
    else:
        mu = port_ret
        sigma = 1e-8
        sharpe = 0.0

    # --- Component 2: CVaR penalty (tail risk) ---
    if n >= 16:
        tail_cutoff = max(1, int(0.05 * n))
        sorted_rets = np.sort(ret_arr)
        cvar = np.mean(sorted_rets[:tail_cutoff])  # negative = bad
        cvar_penalty = min(0.0, cvar)  # only penalize negative CVaR
    else:
        cvar_penalty = min(0.0, port_ret)

    # --- Component 3: Drawdown penalty ---
    drawdown_penalty = -drawdown ** 1.5  # superlinear to strongly penalize deep drawdowns

    # --- Component 4: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.5 * turnover

    # --- Component 5: Consistency bonus (downside deviation based) ---
    if n >= 8:
        downside = ret_arr[ret_arr < 0]
        if len(downside) > 0:
            downside_dev = np.sqrt(np.mean(downside ** 2)) + 1e-8
            sortino = mu / downside_dev
        else:
            sortino = sharpe * 2.0  # no downside, reward generously
        consistency = np.clip(sortino, -3.0, 3.0)
    else:
        consistency = 0.0

    # --- Combine components ---
    # Weights chosen to balance return encouragement vs. risk penalties
    total = (
        1.5 * sharpe           # primary: risk-adjusted return
        + 0.8 * consistency    # secondary: sortino-like
        + 3.0 * cvar_penalty   # tail risk penalty (scaled up since CVaR is small)
        + 1.5 * drawdown_penalty
        + turnover_penalty
    )

    components = {
        "sharpe": sharpe,
        "sortino_consistency": consistency,
        "cvar_penalty": cvar_penalty,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
        "port_ret": port_ret,
    }

    state["ret_history"] = ret_history
    state["peak"] = peak
    state["cum_value"] = cum_value

    return float(total), components, state