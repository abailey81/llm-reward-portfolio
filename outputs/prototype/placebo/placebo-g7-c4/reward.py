def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # Retrieve or initialize reward state
    state = info.get("reward_state")
    if state is None:
        state = {
            "ret_history": [],
            "peak": 0.0,
            "cum_ret": 0.0,
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "step": 0,
            "alpha": 0.05,  # EMA decay for ~20-step window
        }

    alpha = state["alpha"]
    step = state["step"]

    # Update cumulative return (log-compounding approximation)
    state["cum_ret"] += port_ret
    cum_ret = state["cum_ret"]

    # Update peak and drawdown
    if cum_ret > state["peak"]:
        state["peak"] = cum_ret
    drawdown = state["peak"] - cum_ret  # always >= 0

    # Online EMA of return and squared return (for volatility)
    if step == 0:
        state["ema_ret"] = port_ret
        state["ema_sq"] = port_ret ** 2
    else:
        state["ema_ret"] = (1 - alpha) * state["ema_ret"] + alpha * port_ret
        state["ema_sq"] = (1 - alpha) * state["ema_sq"] + alpha * (port_ret ** 2)

    ema_ret = state["ema_ret"]
    ema_var = max(state["ema_sq"] - ema_ret ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)

    # Append to short history for CVaR
    state["ret_history"].append(port_ret)
    # Keep history bounded
    if len(state["ret_history"]) > 100:
        state["ret_history"].pop(0)

    ret_arr = np.array(state["ret_history"])

    # ---- Component 1: Sharpe-like signal ----
    sharpe_signal = ema_ret / (ema_std + 1e-8)

    # ---- Component 2: CVaR penalty (tail risk) ----
    if len(ret_arr) >= 10:
        var_5 = np.percentile(ret_arr, 5)
        cvar = ret_arr[ret_arr <= var_5].mean() if (ret_arr <= var_5).sum() > 0 else var_5
    else:
        cvar = port_ret
    cvar_penalty = -min(cvar, 0.0)  # penalty only for negative tail

    # ---- Component 3: Drawdown penalty ----
    dd_penalty = drawdown  # penalize sustained drawdown

    # ---- Component 4: Turnover cost penalty ----
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.5 * turnover

    # ---- Component 5: Diversification bonus ----
    # Encourage spreading risk (entropy of weights)
    w_pos = np.clip(weights, 1e-8, 1.0)
    entropy = -np.sum(w_pos * np.log(w_pos))
    # Normalize: max entropy = log(n)
    n = len(weights)
    entropy_norm = entropy / np.log(n + 1e-8)
    diversification_bonus = 0.1 * entropy_norm

    # ---- Total reward ----
    # Annualization factor (assume ~252 steps/year, scaled down)
    scale = np.sqrt(252)
    
    total = (
        scale * sharpe_signal          # core risk-adjusted return
        - 2.0 * cvar_penalty           # tail risk
        - 1.0 * dd_penalty             # drawdown
        - turnover_penalty             # trading costs
        + diversification_bonus        # diversification
    )

    state["step"] += 1

    components = {
        "sharpe_signal": float(scale * sharpe_signal),
        "cvar_penalty": float(-2.0 * cvar_penalty),
        "dd_penalty": float(-dd_penalty),
        "turnover_penalty": float(-turnover_penalty),
        "diversification_bonus": float(diversification_bonus),
        "port_ret": float(port_ret),
    }

    return float(total), components, state