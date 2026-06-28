def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize reward state ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "step": 0,
            "ema_ret": 0.0,
            "ema_sq_ret": 0.0,
            "ema_alpha": 0.05,  # smoothing factor for EMA
        }

    state["step"] += 1
    alpha = state["ema_alpha"]

    # --- Update EMA of returns and squared returns ---
    ema_ret = state["ema_ret"]
    ema_sq_ret = state["ema_sq_ret"]

    ema_ret = alpha * port_ret + (1 - alpha) * ema_ret
    ema_sq_ret = alpha * (port_ret ** 2) + (1 - alpha) * ema_sq_ret

    state["ema_ret"] = ema_ret
    state["ema_sq_ret"] = ema_sq_ret

    # --- Keep a rolling window of returns for tail risk ---
    ret_history = state["ret_history"]
    ret_history.append(port_ret)
    if len(ret_history) > 100:
        ret_history.pop(0)
    state["ret_history"] = ret_history

    # --- Online Sharpe (EMA-based) ---
    ema_var = max(ema_sq_ret - ema_ret ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)
    # Annualize-ish (assume ~252 steps/year, scale signal)
    online_sharpe = ema_ret / ema_std

    # --- CVaR penalty from rolling history ---
    cvar_penalty = 0.0
    if len(ret_history) >= 20:
        arr = np.array(ret_history)
        cutoff = np.percentile(arr, 5)
        tail = arr[arr <= cutoff]
        if len(tail) > 0:
            cvar = np.mean(tail)  # negative value
            cvar_penalty = -2.0 * max(-cvar, 0.0)  # penalize tail losses

    # --- Turnover penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.1 * turnover

    # --- Concentration penalty (encourage diversification) ---
    # Use negative entropy of weights as concentration measure
    w = np.clip(weights, 1e-8, 1.0)
    entropy = -np.sum(w * np.log(w))
    n = len(weights)
    max_entropy = np.log(n)
    # Normalize entropy to [0, 1] and penalize low entropy
    norm_entropy = entropy / max_entropy if max_entropy > 0 else 1.0
    concentration_penalty = -0.1 * (1.0 - norm_entropy)

    # --- Direct return component (scaled) ---
    # Keep a direct reward signal for each step
    direct_ret = port_ret * 10.0  # scale up for gradient signal

    # --- Downside penalty: penalize negative returns more ---
    downside_penalty = 0.0
    if port_ret < 0:
        downside_penalty = -0.5 * abs(port_ret)

    # --- Combine components ---
    # Primary: online Sharpe drives long-term behavior
    # Secondary: direct return for step-level signal
    # Penalties: CVaR, turnover, concentration, downside
    sharpe_weight = 1.0
    total = (
        sharpe_weight * online_sharpe
        + direct_ret
        + cvar_penalty
        + turnover_penalty
        + concentration_penalty
        + downside_penalty
    )

    components = {
        "online_sharpe": online_sharpe,
        "direct_ret": direct_ret,
        "cvar_penalty": cvar_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
        "downside_penalty": downside_penalty,
    }

    return float(total), components, state