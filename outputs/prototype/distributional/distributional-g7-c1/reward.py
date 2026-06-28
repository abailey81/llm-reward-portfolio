def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize state ---
    state = info.get("reward_state") or {}
    ret_history = state.get("ret_history", [])
    peak = state.get("peak", 1.0)
    cum_value = state.get("cum_value", 1.0)

    # Update cumulative value and drawdown tracking
    cum_value = cum_value * (1.0 + port_ret)
    peak = max(peak, cum_value)
    drawdown = (peak - cum_value) / (peak + 1e-8)

    # Append current return to history
    ret_history.append(port_ret)
    # Keep a rolling window of recent returns for statistics
    window = 120
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    ret_arr = np.array(ret_history)
    n = len(ret_arr)

    # --- Component 1: Sharpe-based reward (online, rolling) ---
    if n >= 8:
        mu = np.mean(ret_arr)
        sigma = np.std(ret_arr) + 1e-8
        sharpe_contrib = mu / sigma  # per-step Sharpe proxy
    else:
        mu = port_ret
        sigma = 1e-8
        sharpe_contrib = port_ret * 10.0  # early steps: just use raw return

    # --- Component 2: CVaR penalty (tail risk) ---
    if n >= 16:
        sorted_rets = np.sort(ret_arr)
        # 5% CVaR
        cutoff_5 = max(1, int(np.floor(0.05 * n)))
        cvar_5 = np.mean(sorted_rets[:cutoff_5])
        # 10% CVaR
        cutoff_10 = max(1, int(np.floor(0.10 * n)))
        cvar_10 = np.mean(sorted_rets[:cutoff_10])
        # Combined CVaR penalty (penalize negative tail)
        cvar_penalty = 0.6 * min(cvar_5, 0.0) + 0.4 * min(cvar_10, 0.0)
    else:
        cvar_penalty = min(port_ret, 0.0) * 0.5

    # --- Component 3: Drawdown penalty ---
    # Penalize being in drawdown, especially deep ones
    dd_penalty = -drawdown * drawdown  # quadratic in drawdown depth

    # --- Component 4: Turnover / transaction cost penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.5 * turnover

    # --- Component 5: Concentration penalty (encourage diversification) ---
    # Herfindahl index on non-cash weights
    hhi = np.sum(weights ** 2)
    n_assets = len(weights)
    hhi_min = 1.0 / n_assets  # perfectly diversified
    concentration_penalty = -0.3 * (hhi - hhi_min)

    # --- Combine components ---
    # Scale CVaR penalty relative to current vol
    cvar_scale = 8.0
    total = (
        sharpe_contrib
        + cvar_scale * cvar_penalty
        + 2.0 * dd_penalty
        + turnover_penalty
        + concentration_penalty
    )

    components = {
        "sharpe_contrib": float(sharpe_contrib),
        "cvar_penalty": float(cvar_scale * cvar_penalty),
        "dd_penalty": float(2.0 * dd_penalty),
        "turnover_penalty": float(turnover_penalty),
        "concentration_penalty": float(concentration_penalty),
        "drawdown": float(drawdown),
        "port_ret": float(port_ret),
    }

    reward_state = {
        "ret_history": ret_history,
        "peak": float(peak),
        "cum_value": float(cum_value),
    }

    return float(total), components, reward_state