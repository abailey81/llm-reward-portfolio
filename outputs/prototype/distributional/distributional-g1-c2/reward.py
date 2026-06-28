def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 0.0,
            "cum_ret": 0.0,
            # EMA stats for online Sharpe
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "ema_alpha": 0.05,
            "step": 0,
        }

    state["step"] += 1
    alpha = state["ema_alpha"]

    # Update EMA of returns and squared returns
    state["ema_ret"] = alpha * port_ret + (1 - alpha) * state["ema_ret"]
    state["ema_sq"] = alpha * (port_ret ** 2) + (1 - alpha) * state["ema_sq"]

    # Store return history (cap length to save memory)
    state["ret_history"].append(port_ret)
    if len(state["ret_history"]) > 252:
        state["ret_history"].pop(0)

    # Update cumulative return and drawdown
    state["cum_ret"] += port_ret
    state["peak"] = max(state["peak"], state["cum_ret"])
    drawdown = state["peak"] - state["cum_ret"]

    # --- Component 1: Online Sharpe-based return signal ---
    ema_ret = state["ema_ret"]
    ema_sq = state["ema_sq"]
    variance = max(ema_sq - ema_ret ** 2, 1e-8)
    std = np.sqrt(variance)
    # Differential Sharpe: reward for improving Sharpe
    sharpe_signal = ema_ret / std

    # Scale return reward: use port_ret normalized by running std
    ret_component = port_ret / (std + 1e-6)

    # --- Component 2: Drawdown penalty ---
    dd_penalty = -0.5 * drawdown

    # --- Component 3: CVaR-inspired tail penalty ---
    tail_penalty = 0.0
    hist = state["ret_history"]
    if len(hist) >= 20:
        arr = np.array(hist)
        cutoff = np.percentile(arr, 10)
        tail_returns = arr[arr <= cutoff]
        if len(tail_returns) > 0:
            cvar_10 = np.mean(tail_returns)
            tail_penalty = 0.3 * cvar_10  # negative value -> penalty

    # --- Component 4: Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.05 * turnover

    # --- Component 5: Concentration penalty (encourage diversification) ---
    # Herfindahl index on risky assets (exclude last element = cash if applicable)
    hhi = np.sum(weights ** 2)
    concentration_penalty = -0.1 * hhi

    # Combine: weighted sum, scaled to reasonable range
    step = state["step"]
    warmup = min(step / 50.0, 1.0)  # ramp up slowly to let EMA stabilize

    total = (
        ret_component * 1.0
        + dd_penalty * warmup
        + tail_penalty * warmup
        + turnover_penalty
        + concentration_penalty * 0.5
    )

    components = {
        "ret_component": ret_component,
        "sharpe_signal": sharpe_signal,
        "dd_penalty": dd_penalty,
        "tail_penalty": tail_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
    }

    return float(total), components, state