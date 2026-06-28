def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 0.0,
            "cumulative": 0.0,
            "n": 0,
        }

    state["n"] += 1
    state["ret_history"].append(port_ret)
    state["cumulative"] += port_ret

    # Keep only recent window for online estimates
    window = 60
    hist = state["ret_history"]
    if len(hist) > window:
        state["ret_history"] = hist[-window:]
    hist = state["ret_history"]

    # --- Component 1: Online Sharpe (annualized approx) ---
    if len(hist) >= 5:
        arr = np.array(hist)
        mean_r = np.mean(arr)
        std_r = np.std(arr) + 1e-8
        sharpe = mean_r / std_r  # per-step Sharpe
    else:
        sharpe = 0.0

    # --- Component 2: Drawdown penalty ---
    cum = state["cumulative"]
    if cum > state["peak"]:
        state["peak"] = cum
    drawdown = state["peak"] - cum  # always >= 0
    drawdown_penalty = -drawdown * 0.5

    # --- Component 3: Turnover penalty (transaction cost proxy) ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.05 * turnover

    # --- Component 4: Tail risk penalty (CVaR-like) ---
    if len(hist) >= 10:
        arr = np.array(hist)
        cutoff = np.percentile(arr, 10)
        tail_losses = arr[arr < cutoff]
        cvar_penalty = -0.3 * abs(np.mean(tail_losses)) if len(tail_losses) > 0 else 0.0
    else:
        cvar_penalty = 0.0

    # --- Component 5: Raw return (small weight to keep signal) ---
    raw_return = port_ret * 2.0

    # --- Combine ---
    # Sharpe is primary driver; others are corrective penalties
    total = (
        sharpe * 0.5
        + raw_return
        + drawdown_penalty
        + turnover_penalty
        + cvar_penalty
    )

    components = {
        "sharpe": sharpe * 0.5,
        "raw_return": raw_return,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
        "cvar_penalty": cvar_penalty,
    }

    return float(total), components, state