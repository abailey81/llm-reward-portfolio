def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cumulative": 1.0,
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "ema_alpha": 0.06,
            "step": 0,
        }

    alpha = state["ema_alpha"]
    step = state["step"]

    # Update cumulative value and drawdown
    state["cumulative"] *= (1.0 + port_ret)
    if state["cumulative"] > state["peak"]:
        state["peak"] = state["cumulative"]
    drawdown = (state["peak"] - state["cumulative"]) / (state["peak"] + 1e-8)

    # Update EMA of returns and squared returns (online Sharpe)
    state["ema_ret"] = alpha * port_ret + (1.0 - alpha) * state["ema_ret"]
    state["ema_sq"] = alpha * (port_ret ** 2) + (1.0 - alpha) * state["ema_sq"]
    state["step"] = step + 1

    # Keep a short history for downside deviation
    state["ret_history"].append(port_ret)
    if len(state["ret_history"]) > 60:
        state["ret_history"].pop(0)

    # Online Sharpe component
    ema_var = state["ema_sq"] - state["ema_ret"] ** 2
    ema_std = np.sqrt(max(ema_var, 1e-8))
    sharpe_component = state["ema_ret"] / ema_std

    # Sortino-style: downside deviation from recent history
    hist = np.array(state["ret_history"])
    downside = hist[hist < 0.0]
    if len(downside) > 2:
        downside_std = np.sqrt(np.mean(downside ** 2) + 1e-8)
        sortino_component = state["ema_ret"] / downside_std
    else:
        sortino_component = sharpe_component

    # Drawdown penalty (nonlinear)
    drawdown_penalty = drawdown ** 2 * 5.0

    # Turnover penalty
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.05 * turnover

    # Tail loss penalty: CVaR-like from history
    if len(hist) >= 10:
        var_5 = np.percentile(hist, 5)
        cvar = np.mean(hist[hist <= var_5]) if np.any(hist <= var_5) else var_5
        tail_penalty = -0.5 * min(cvar, 0.0)
    else:
        tail_penalty = 0.0

    # Warm-up: scale contributions during early steps
    warmup = min(1.0, step / 30.0)

    total = (
        0.4 * sharpe_component * warmup
        + 0.3 * sortino_component * warmup
        + port_ret * 2.0  # direct return signal always active
        - drawdown_penalty
        - turnover_penalty
        - tail_penalty
    )

    components = {
        "sharpe_component": sharpe_component,
        "sortino_component": sortino_component,
        "drawdown_penalty": drawdown_penalty,
        "turnover_penalty": turnover_penalty,
        "tail_penalty": tail_penalty,
        "port_ret": port_ret,
    }

    return float(total), components, state