def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize state ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cumulative": 1.0,
            "n": 0,
        }

    ret_history = state["ret_history"]
    peak = state["peak"]
    cumulative = state["cumulative"]
    n = state["n"]

    # Update cumulative NAV and drawdown tracking
    cumulative = cumulative * (1.0 + port_ret)
    if cumulative > peak:
        peak = cumulative
    drawdown = (peak - cumulative) / (peak + 1e-8)

    # Store return
    ret_history.append(port_ret)
    n += 1

    # --- Component 1: Online Sharpe-based return signal ---
    # Use exponential moving statistics for stability
    alpha = 0.05  # decay for EMA (heavier weight on recent)
    if n == 1:
        ema_ret = port_ret
        ema_var = 0.0
    else:
        ema_ret = state.get("ema_ret", port_ret)
        ema_var = state.get("ema_var", 0.0)
        ema_ret = (1 - alpha) * ema_ret + alpha * port_ret
        ema_var = (1 - alpha) * ema_var + alpha * (port_ret - ema_ret) ** 2

    ema_std = np.sqrt(ema_var + 1e-8)

    # Sharpe-like signal: reward return above zero, normalized by volatility
    sharpe_signal = ema_ret / ema_std

    # --- Component 2: Tail loss penalty (CVaR approximation) ---
    tail_penalty = 0.0
    if len(ret_history) >= 20:
        arr = np.array(ret_history[-100:])  # use recent window
        threshold_5 = np.percentile(arr, 5)
        tail_returns = arr[arr <= threshold_5]
        if len(tail_returns) > 0:
            cvar_5 = np.mean(tail_returns)
            tail_penalty = -cvar_5  # positive when losses are large

    # --- Component 3: Drawdown penalty ---
    drawdown_penalty = drawdown ** 2  # quadratic to penalize deep drawdowns more

    # --- Component 4: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.05 * turnover

    # --- Component 5: Concentration penalty (entropy regularization) ---
    # Encourage diversification
    w_clean = np.clip(weights, 1e-8, 1.0)
    w_clean = w_clean / w_clean.sum()
    entropy = -np.sum(w_clean * np.log(w_clean))
    max_entropy = np.log(len(weights) + 1e-8)
    concentration_penalty = 0.1 * (1.0 - entropy / (max_entropy + 1e-8))

    # --- Combine components ---
    # Scale sharpe signal to be primary driver
    w_sharpe = 1.0
    w_tail = 0.5
    w_dd = 0.3
    w_turn = 1.0
    w_conc = 0.2

    total = (
        w_sharpe * sharpe_signal
        - w_tail * tail_penalty
        - w_dd * drawdown_penalty
        - w_turn * turnover_penalty
        - w_conc * concentration_penalty
    )

    components = {
        "sharpe_signal": float(w_sharpe * sharpe_signal),
        "tail_penalty": float(-w_tail * tail_penalty),
        "drawdown_penalty": float(-w_dd * drawdown_penalty),
        "turnover_penalty": float(-w_turn * turnover_penalty),
        "concentration_penalty": float(-w_conc * concentration_penalty),
    }

    # Update state
    state["ret_history"] = ret_history[-200:]  # keep bounded
    state["peak"] = peak
    state["cumulative"] = cumulative
    state["n"] = n
    state["ema_ret"] = ema_ret
    state["ema_var"] = ema_var

    return float(total), components, state