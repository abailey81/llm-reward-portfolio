def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Initialize state ---
    state = info.get("reward_state") or {}
    
    # Rolling window for statistics
    WINDOW = 60
    ret_history = state.get("ret_history", [])
    peak = state.get("peak", 1.0)
    cum_ret = state.get("cum_ret", 1.0)

    # Update cumulative return and drawdown tracking
    cum_ret = cum_ret * (1.0 + port_ret)
    peak = max(peak, cum_ret)
    drawdown = (cum_ret - peak) / peak  # <= 0

    # Update return history
    ret_history.append(port_ret)
    if len(ret_history) > WINDOW:
        ret_history = ret_history[-WINDOW:]

    # --- Component 1: Base return signal ---
    ret_component = port_ret

    # --- Component 2: Online Sharpe (rolling) ---
    sharpe_component = 0.0
    if len(ret_history) >= 8:
        arr = np.array(ret_history)
        mean_r = np.mean(arr)
        std_r = np.std(arr) + 1e-8
        sharpe_component = mean_r / std_r
        # Scale to be comparable
        sharpe_component = np.clip(sharpe_component, -3.0, 3.0) * 0.01
    
    # --- Component 3: Drawdown penalty ---
    # Penalize being in drawdown, more severely for deep drawdowns
    dd_penalty = 0.5 * drawdown  # drawdown <= 0, so this is <= 0

    # --- Component 4: Turnover / transaction cost penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    # Penalize excessive rebalancing
    turnover_penalty = -0.002 * turnover

    # --- Component 5: Tail risk penalty (downside semi-deviation) ---
    tail_penalty = 0.0
    if len(ret_history) >= 8:
        arr = np.array(ret_history)
        downside = arr[arr < 0]
        if len(downside) > 0:
            cvar_approx = np.mean(downside)  # approximate CVaR
            tail_penalty = 0.3 * cvar_approx  # negative contribution

    # --- Component 6: Concentration penalty (encourage diversification) ---
    # Penalize highly concentrated portfolios (Herfindahl-like)
    hhi = np.sum(weights ** 2)
    n = len(weights)
    max_hhi = 1.0
    min_hhi = 1.0 / n
    # Normalized concentration
    concentration_penalty = -0.005 * (hhi - min_hhi) / (max_hhi - min_hhi + 1e-8)

    # --- Combine ---
    total = (
        ret_component
        + sharpe_component
        + dd_penalty
        + turnover_penalty
        + tail_penalty
        + concentration_penalty
    )

    components = {
        "ret": ret_component,
        "sharpe": sharpe_component,
        "drawdown_penalty": dd_penalty,
        "turnover_penalty": turnover_penalty,
        "tail_penalty": tail_penalty,
        "concentration_penalty": concentration_penalty,
    }

    reward_state = {
        "ret_history": ret_history,
        "peak": peak,
        "cum_ret": cum_ret,
    }

    return float(total), components, reward_state