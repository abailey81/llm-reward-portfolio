def reward(weights, returns, prev_weights, port_ret, info):
    reward_state = info.get("reward_state", None)

    # Initialize state
    if reward_state is None:
        reward_state = {
            "ret_history": [],
            "peak": 1.0,
            "cum_ret": 1.0,
            "step": 0,
        }

    ret_history = reward_state["ret_history"]
    peak = reward_state["peak"]
    cum_ret = reward_state["cum_ret"]
    step = reward_state["step"]

    # Update cumulative return and drawdown tracking
    cum_ret = cum_ret * (1.0 + port_ret)
    peak = max(peak, cum_ret)
    drawdown = (peak - cum_ret) / (peak + 1e-8)

    # Record return
    ret_history.append(port_ret)
    window = 60
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    step += 1

    # --- Component 1: Online Sharpe (annualized, rolling) ---
    if len(ret_history) >= 5:
        arr = np.array(ret_history)
        mean_r = np.mean(arr)
        std_r = np.std(arr) + 1e-8
        sharpe = mean_r / std_r * np.sqrt(252)
    else:
        sharpe = 0.0

    # --- Component 2: CVaR penalty (5% tail) ---
    cvar_penalty = 0.0
    if len(ret_history) >= 10:
        arr = np.array(ret_history)
        cutoff = np.percentile(arr, 5)
        tail = arr[arr <= cutoff]
        if len(tail) > 0:
            cvar = np.mean(tail)  # negative value
            cvar_penalty = min(0.0, cvar) * 5.0  # penalize bad tails

    # --- Component 3: Drawdown penalty ---
    drawdown_penalty = -drawdown * 2.0

    # --- Component 4: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -turnover * 0.5

    # --- Component 5: Concentration penalty (encourage diversification) ---
    n = len(weights)
    hhi = np.sum(weights ** 2)
    max_hhi = 1.0
    min_hhi = 1.0 / n
    concentration_penalty = -((hhi - min_hhi) / (max_hhi - min_hhi + 1e-8)) * 0.3

    # --- Component 6: Direct return signal (scaled) ---
    ret_signal = port_ret * 10.0

    # Combine: sharpe is primary, supplemented by other risk controls
    # Ramp in sharpe signal once we have enough history
    sharpe_weight = min(1.0, step / 20.0)
    total = (
        sharpe_weight * sharpe * 0.5
        + (1 - sharpe_weight) * ret_signal
        + cvar_penalty
        + drawdown_penalty
        + turnover_penalty
        + concentration_penalty
    )

    components = {
        "sharpe_contribution": sharpe_weight * sharpe * 0.5,
        "ret_signal": (1 - sharpe_weight) * ret_signal,
        "cvar_penalty": cvar_penalty,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
    }

    reward_state["ret_history"] = ret_history
    reward_state["peak"] = peak
    reward_state["cum_ret"] = cum_ret
    reward_state["step"] = step

    return float(total), components, reward_state