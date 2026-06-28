def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ema_ret": 0.0,
            "ema_var": 1e-6,
            "peak": 1.0,
            "cumulative": 1.0,
            "recent_rets": [],
            "step": 0,
        }

    alpha_fast = 0.05   # fast EMA for return/variance (~20 steps)
    alpha_slow = 0.01   # slow EMA for drawdown tracking (~100 steps)

    step = state["step"] + 1
    ema_ret = state["ema_ret"]
    ema_var = state["ema_var"]
    peak = state["peak"]
    cumulative = state["cumulative"]
    recent_rets = state["recent_rets"]

    # Update cumulative value and drawdown
    cumulative = cumulative * (1.0 + port_ret)
    if cumulative > peak:
        peak = cumulative
    drawdown = (peak - cumulative) / (peak + 1e-8)

    # Update EMA of returns and variance
    ema_ret = (1 - alpha_fast) * ema_ret + alpha_fast * port_ret
    ema_var = (1 - alpha_fast) * ema_var + alpha_fast * (port_ret - ema_ret) ** 2
    ema_std = np.sqrt(ema_var + 1e-8)

    # Online Sharpe component
    sharpe_component = ema_ret / ema_std

    # Track recent returns for tail-loss estimation (window=40)
    recent_rets.append(port_ret)
    if len(recent_rets) > 40:
        recent_rets.pop(0)

    # CVaR-like tail penalty: mean of worst 10% returns
    if len(recent_rets) >= 10:
        arr = np.array(recent_rets)
        cutoff = int(max(1, len(arr) * 0.1))
        tail_loss = -np.mean(np.sort(arr)[:cutoff])  # positive = bad
    else:
        tail_loss = 0.0

    # Turnover penalty (proxy for transaction costs)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.5 * turnover

    # Drawdown penalty (convex: punish large drawdowns more)
    drawdown_penalty = 2.0 * (drawdown ** 2)

    # Concentration penalty (encourage diversification, penalize extreme weights)
    # Herfindahl index minus cash weight
    non_cash_weights = weights[:-1] if len(weights) > 1 else weights
    herfindahl = np.sum(non_cash_weights ** 2)
    concentration_penalty = 0.3 * herfindahl

    # Combine components
    # Warm-up: scale down signal in early steps
    warmup = min(1.0, step / 20.0)

    total = (
        warmup * sharpe_component
        - drawdown_penalty
        - turnover_penalty
        - tail_loss * 1.5
        - concentration_penalty
        + port_ret * 5.0  # direct return signal
    )

    components = {
        "sharpe_component": float(sharpe_component),
        "drawdown_penalty": float(drawdown_penalty),
        "turnover_penalty": float(turnover_penalty),
        "tail_loss_penalty": float(tail_loss * 1.5),
        "concentration_penalty": float(concentration_penalty),
        "direct_return": float(port_ret * 5.0),
    }

    state["ema_ret"] = ema_ret
    state["ema_var"] = ema_var
    state["peak"] = peak
    state["cumulative"] = cumulative
    state["recent_rets"] = recent_rets
    state["step"] = step

    return float(total), components, state