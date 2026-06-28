def reward(weights, returns, prev_weights, port_ret, info):
    reward_state = info.get("reward_state", None)

    # Initialize state
    if reward_state is None:
        reward_state = {
            "ret_history": [],
            "peak": 0.0,
            "cumulative": 0.0,
            "ema_ret": 0.0,
            "ema_ret2": 0.0,
            "ema_alpha": 0.06,
            "step": 0,
        }

    state = reward_state
    alpha = state["ema_alpha"]
    step = state["step"]

    # Update cumulative and peak for drawdown
    state["cumulative"] += port_ret
    if state["cumulative"] > state["peak"]:
        state["peak"] = state["cumulative"]
    drawdown = state["peak"] - state["cumulative"]

    # Update EMA of returns and squared returns (for online Sharpe)
    if step == 0:
        state["ema_ret"] = port_ret
        state["ema_ret2"] = port_ret ** 2
    else:
        state["ema_ret"] = alpha * port_ret + (1 - alpha) * state["ema_ret"]
        state["ema_ret2"] = alpha * port_ret**2 + (1 - alpha) * state["ema_ret2"]

    # Online Sharpe estimate
    ema_var = state["ema_ret2"] - state["ema_ret"] ** 2
    ema_std = np.sqrt(max(ema_var, 1e-8))
    online_sharpe = state["ema_ret"] / ema_std

    # Maintain a rolling window of returns for CVaR calculation
    state["ret_history"].append(port_ret)
    window = 60  # ~60 steps rolling window
    if len(state["ret_history"]) > window:
        state["ret_history"].pop(0)

    hist = np.array(state["ret_history"])

    # CVaR 5% penalty
    if len(hist) >= 10:
        threshold_5 = np.percentile(hist, 5)
        tail_5 = hist[hist <= threshold_5]
        cvar_5 = float(np.mean(tail_5)) if len(tail_5) > 0 else float(threshold_5)
        threshold_10 = np.percentile(hist, 10)
        tail_10 = hist[hist <= threshold_10]
        cvar_10 = float(np.mean(tail_10)) if len(tail_10) > 0 else float(threshold_10)
    else:
        cvar_5 = min(port_ret, 0.0)
        cvar_10 = min(port_ret, 0.0)

    # Turnover penalty
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = 0.5 * turnover

    # Drawdown penalty (scaled)
    drawdown_penalty = 2.0 * drawdown

    # CVaR penalty (tail risk)
    cvar_penalty = 3.0 * (-cvar_5) + 1.5 * (-cvar_10)

    # Sharpe component (scaled to reasonable range)
    sharpe_component = 2.0 * online_sharpe

    # Direct return component (mild)
    ret_component = 10.0 * port_ret

    # Combine
    total = (
        ret_component
        + sharpe_component
        - cvar_penalty
        - drawdown_penalty
        - turnover_penalty
    )

    components = {
        "ret_component": ret_component,
        "sharpe_component": sharpe_component,
        "cvar_5_penalty": -3.0 * (-cvar_5),
        "cvar_10_penalty": -1.5 * (-cvar_10),
        "drawdown_penalty": -drawdown_penalty,
        "turnover_penalty": -turnover_penalty,
        "online_sharpe": online_sharpe,
        "port_ret": port_ret,
    }

    state["step"] += 1
    reward_state = state

    return float(total), components, reward_state