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
    drawdown = (peak - cum_value) / peak  # >= 0

    # Append current return to history
    ret_history.append(port_ret)

    # Keep a rolling window for statistics
    window = 120
    recent = ret_history[-window:] if len(ret_history) >= window else ret_history
    recent_arr = np.array(recent, dtype=np.float64)

    n = len(recent_arr)

    # --- Component 1: Online Sharpe-like signal ---
    if n >= 2:
        mu = np.mean(recent_arr)
        sigma = np.std(recent_arr, ddof=1) + 1e-8
        sharpe_contrib = mu / sigma
    else:
        sharpe_contrib = port_ret

    # --- Component 2: CVaR penalty (Expected Shortfall at 5%) ---
    if n >= 20:
        sorted_rets = np.sort(recent_arr)
        cutoff_idx = max(1, int(np.floor(0.05 * n)))
        cvar = np.mean(sorted_rets[:cutoff_idx])  # negative value = tail loss
        cvar_penalty = min(0.0, cvar)  # only penalize losses
    else:
        cvar_penalty = min(0.0, port_ret)

    # --- Component 3: Drawdown penalty ---
    # Penalize proportionally to drawdown severity
    drawdown_penalty = -drawdown ** 1.5  # convex penalty: worse for large drawdowns

    # --- Component 4: Turnover / transaction cost penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.1 * turnover

    # --- Component 5: Direct return signal (scaled) ---
    # Small direct return signal to keep the agent return-seeking
    direct_ret = np.clip(port_ret, -0.1, 0.1)

    # --- Combine components with tuned weights ---
    # Primary driver: Sharpe-like signal
    # Secondary: CVaR and drawdown deterrence
    total = (
        0.40 * sharpe_contrib
        + 2.0  * cvar_penalty        # strong tail-loss aversion
        + 0.50 * drawdown_penalty    # moderate drawdown aversion
        + turnover_penalty           # cost awareness
        + 0.20 * direct_ret * 100    # small direct return nudge (scaled)
    )

    components = {
        "sharpe_contrib": float(sharpe_contrib),
        "cvar_penalty": float(cvar_penalty),
        "drawdown_penalty": float(drawdown_penalty),
        "turnover_penalty": float(turnover_penalty),
        "direct_ret": float(direct_ret),
        "total": float(total),
    }

    reward_state = {
        "ret_history": ret_history,
        "peak": float(peak),
        "cum_value": float(cum_value),
    }

    return float(total), components, reward_state