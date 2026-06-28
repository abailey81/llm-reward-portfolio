def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize state ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "ema_alpha": 0.06,        # decay for ~16 steps half-life
            "peak": 0.0,
            "cum_ret": 0.0,
            "recent_rets": [],
            "max_window": 60,         # window for CVaR
            "step": 0,
        }

    # Unpack state
    ema_ret   = state["ema_ret"]
    ema_sq    = state["ema_sq"]
    alpha     = state["ema_alpha"]
    peak      = state["peak"]
    cum_ret   = state["cum_ret"]
    recent    = state["recent_rets"]
    max_win   = state["max_window"]
    step      = state["step"]

    # --- Update running stats ---
    step += 1
    ema_ret = alpha * port_ret + (1 - alpha) * ema_ret
    ema_sq  = alpha * (port_ret ** 2) + (1 - alpha) * ema_sq

    ema_var = max(ema_sq - ema_ret ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)

    # --- Update cumulative return and drawdown ---
    cum_ret = (1 + cum_ret) * (1 + port_ret) - 1
    peak    = max(peak, cum_ret)
    drawdown = (peak - cum_ret) / max(1 + peak, 1e-8)

    # --- Maintain recent returns window for CVaR ---
    recent.append(port_ret)
    if len(recent) > max_win:
        recent.pop(0)

    # --- Component 1: Online Sharpe contribution ---
    # Bias-corrected Sharpe signal using EMA
    sharpe_signal = ema_ret / ema_std if step > 5 else 0.0

    # --- Component 2: CVaR penalty ---
    cvar_penalty = 0.0
    if len(recent) >= 10:
        arr = np.array(recent)
        cutoff = np.percentile(arr, 5)
        tail = arr[arr <= cutoff]
        if len(tail) > 0:
            cvar_5 = tail.mean()   # negative number = bad
            cvar_penalty = -max(-cvar_5, 0.0)  # penalize negative CVaR

    # --- Component 3: Drawdown penalty ---
    dd_penalty = -drawdown ** 1.5   # nonlinear to penalize large drawdowns more

    # --- Component 4: Turnover cost penalty ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.05 * turnover

    # --- Component 5: Concentration penalty (entropy) ---
    # Encourage diversification
    w_risky = weights[:-1]  # exclude cash
    eps = 1e-8
    w_safe = np.clip(w_risky, eps, 1.0)
    w_safe = w_safe / w_safe.sum()
    entropy = -np.sum(w_safe * np.log(w_safe))
    max_entropy = np.log(max(len(w_safe), 1))
    norm_entropy = entropy / max(max_entropy, eps)
    concentration_bonus = 0.02 * norm_entropy

    # --- Combine components ---
    # Sharpe signal is primary; others are regularizers
    total = (
        0.6  * sharpe_signal
        + 0.5  * port_ret * 10       # direct return signal (scaled)
        + 1.5  * cvar_penalty
        + 0.3  * dd_penalty
        + turnover_penalty
        + concentration_bonus
    )

    # --- Save state ---
    reward_state = {
        "ema_ret":    ema_ret,
        "ema_sq":     ema_sq,
        "ema_alpha":  alpha,
        "peak":       peak,
        "cum_ret":    cum_ret,
        "recent_rets": recent,
        "max_window": max_win,
        "step":       step,
    }

    components = {
        "sharpe_signal":      sharpe_signal,
        "port_ret_scaled":    port_ret * 10,
        "cvar_penalty":       cvar_penalty,
        "dd_penalty":         dd_penalty,
        "turnover_penalty":   turnover_penalty,
        "concentration_bonus": concentration_bonus,
    }

    return float(total), components, reward_state