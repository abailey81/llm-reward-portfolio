def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or restore state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "n": 0,
            "mean": 0.0,
            "M2": 0.0,      # for Welford online variance
            "min_ret": 0.0, # for drawdown tracking
            "peak": 1.0,
            "equity": 1.0,
        }

    # --- Welford online mean/variance update ---
    n = state["n"] + 1
    mean_old = state["mean"]
    mean_new = mean_old + (port_ret - mean_old) / n
    M2_new = state["M2"] + (port_ret - mean_old) * (port_ret - mean_new)
    state["n"] = n
    state["mean"] = mean_new
    state["M2"] = M2_new

    # Variance and std
    var = M2_new / max(n - 1, 1)
    std = np.sqrt(max(var, 1e-10))

    # --- Online Sharpe (annualized proxy, step-level) ---
    # Use a risk-free rate of 0 for simplicity
    sharpe = mean_new / std if n >= 5 else 0.0

    # --- Tail risk: penalize severe losses (CVaR proxy) ---
    ret_history = state["ret_history"]
    ret_history.append(float(port_ret))
    # Keep last 60 steps
    if len(ret_history) > 60:
        ret_history.pop(0)
    state["ret_history"] = ret_history

    if len(ret_history) >= 10:
        arr = np.array(ret_history)
        cutoff = np.percentile(arr, 10)  # 10th percentile
        tail = arr[arr <= cutoff]
        cvar_loss = -float(np.mean(tail)) if len(tail) > 0 else 0.0
    else:
        cvar_loss = max(-port_ret, 0.0)  # penalize loss directly early on

    # --- Drawdown penalty ---
    equity = state["equity"] * (1.0 + port_ret)
    peak = max(state["peak"], equity)
    drawdown = (peak - equity) / max(peak, 1e-8)
    state["equity"] = equity
    state["peak"] = peak

    # --- Turnover penalty (transaction costs proxy) ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = 0.005 * turnover  # small cost

    # --- Concentration penalty (encourage diversification) ---
    # Herfindahl index: sum of squares of weights
    hhi = float(np.sum(weights ** 2))
    n_assets = len(weights)
    hhi_min = 1.0 / n_assets  # perfectly diversified
    concentration_penalty = 0.01 * (hhi - hhi_min)

    # --- Composite reward ---
    # Primary signal: step return (direct, unscaled)
    ret_component = float(port_ret)

    # Scale components carefully
    sharpe_component = 0.1 * sharpe           # online Sharpe bonus
    cvar_component = -0.2 * cvar_loss         # tail loss penalty
    dd_component = -0.1 * drawdown            # drawdown penalty

    total = (ret_component
             + sharpe_component
             + cvar_component
             + dd_component
             - turnover_penalty
             - concentration_penalty)

    components = {
        "port_ret": ret_component,
        "sharpe_bonus": sharpe_component,
        "cvar_penalty": cvar_component,
        "drawdown_penalty": dd_component,
        "turnover_penalty": -turnover_penalty,
        "concentration_penalty": -concentration_penalty,
    }

    return float(total), components, state