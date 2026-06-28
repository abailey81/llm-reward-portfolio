def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Recover or initialize state ---
    state = info.get("reward_state") or {}
    ret_history = list(state.get("ret_history", []))
    peak_value = float(state.get("peak_value", 1.0))
    log_value = float(state.get("log_value", 0.0))

    # Update portfolio value tracking
    log_value = log_value + np.log1p(port_ret)
    curr_value = np.exp(log_value)
    peak_value = max(peak_value, curr_value)

    # Store return
    ret_history.append(float(port_ret))
    if len(ret_history) > 252:
        ret_history = ret_history[-252:]

    arr = np.array(ret_history, dtype=np.float64)
    n = len(arr)

    # --- Core return signal ---
    core_reward = port_ret

    # --- Online Sharpe (annualized) ---
    sharpe_component = 0.0
    if n >= 10:
        mu = np.mean(arr)
        sigma = np.std(arr, ddof=1) + 1e-8
        sharpe_component = (mu / sigma) * np.sqrt(252) * 0.01  # small weight

    # --- CVaR penalty (tail loss) ---
    cvar_penalty = 0.0
    if n >= 20:
        # CVaR at 5% level
        threshold_5 = int(np.ceil(0.05 * n))
        threshold_10 = int(np.ceil(0.10 * n))
        sorted_arr = np.sort(arr)
        cvar_5 = np.mean(sorted_arr[:max(1, threshold_5)])
        cvar_10 = np.mean(sorted_arr[:max(1, threshold_10)])
        # Penalize bad tail losses (they are negative, so subtract them amplified)
        cvar_penalty = 0.3 * min(cvar_5, 0.0) + 0.2 * min(cvar_10, 0.0)

    # --- Drawdown penalty ---
    drawdown = (curr_value - peak_value) / (peak_value + 1e-8)
    # drawdown <= 0 always; penalize proportionally
    dd_penalty = 0.5 * drawdown  # negative contribution when in drawdown

    # --- Turnover penalty ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = -0.002 * turnover

    # --- Concentration penalty (encourage diversification) ---
    n_assets = len(weights)
    # Herfindahl index - penalize concentration
    hhi = float(np.sum(weights ** 2))
    uniform_hhi = 1.0 / n_assets
    concentration_penalty = -0.005 * max(0.0, hhi - uniform_hhi * 1.5)

    # --- Skewness bonus: reward positive skew of recent returns ---
    skew_bonus = 0.0
    if n >= 30:
        mu = np.mean(arr)
        sigma = np.std(arr, ddof=1) + 1e-8
        skewness = np.mean(((arr - mu) / sigma) ** 3)
        skew_bonus = 0.003 * np.clip(skewness, -2.0, 2.0)

    # --- Total reward ---
    total = (
        core_reward
        + sharpe_component
        + cvar_penalty
        + dd_penalty
        + turnover_penalty
        + concentration_penalty
        + skew_bonus
    )

    components = {
        "core_return": float(core_reward),
        "sharpe_component": float(sharpe_component),
        "cvar_penalty": float(cvar_penalty),
        "drawdown_penalty": float(dd_penalty),
        "turnover_penalty": float(turnover_penalty),
        "concentration_penalty": float(concentration_penalty),
        "skew_bonus": float(skew_bonus),
    }

    reward_state = {
        "ret_history": ret_history,
        "peak_value": float(peak_value),
        "log_value": float(log_value),
    }

    return float(total), components, reward_state