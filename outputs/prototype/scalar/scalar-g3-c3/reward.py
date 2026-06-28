def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize or retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cum_value": 1.0,
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "ema_alpha": 0.06,
            "step": 0,
        }

    # Unpack state
    ret_history = state["ret_history"]
    peak = state["peak"]
    cum_value = state["cum_value"]
    ema_ret = state["ema_ret"]
    ema_sq = state["ema_sq"]
    alpha = state["ema_alpha"]
    step = state["step"]

    # Update cumulative value and drawdown
    cum_value = cum_value * (1.0 + port_ret)
    peak = max(peak, cum_value)
    drawdown = (peak - cum_value) / (peak + 1e-8)

    # Update EMA of returns and squared returns for online Sharpe
    ema_ret = alpha * port_ret + (1.0 - alpha) * ema_ret
    ema_sq = alpha * (port_ret ** 2) + (1.0 - alpha) * ema_sq

    # Online Sharpe estimate
    ema_var = max(ema_sq - ema_ret ** 2, 1e-10)
    ema_vol = np.sqrt(ema_var)
    online_sharpe = ema_ret / (ema_vol + 1e-8)

    # Keep a rolling window for CVaR calculation
    ret_history.append(port_ret)
    window = 60
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    # CVaR (Expected Shortfall) at 5% tail
    if len(ret_history) >= 10:
        arr = np.array(ret_history)
        cutoff = np.percentile(arr, 5)
        tail = arr[arr <= cutoff]
        cvar = float(np.mean(tail)) if len(tail) > 0 else cutoff
    else:
        cvar = -abs(port_ret)

    # Turnover penalty
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = 0.1 * turnover

    # Concentration penalty (encourage diversification, avoid extreme concentration)
    n_assets = len(weights)
    herfindahl = float(np.sum(weights ** 2))
    max_herfindahl = 1.0
    min_herfindahl = 1.0 / n_assets
    concentration = (herfindahl - min_herfindahl) / (max_herfindahl - min_herfindahl + 1e-8)
    concentration_penalty = 0.05 * concentration

    # Drawdown penalty (progressive)
    drawdown_penalty = 0.5 * (drawdown ** 2)

    # CVaR penalty
    cvar_penalty = 0.3 * abs(min(cvar, 0.0))

    # Core return component (scaled)
    ret_component = port_ret * 10.0

    # Sharpe component (only meaningful after warmup)
    sharpe_component = 0.0
    if step >= 20:
        sharpe_component = np.clip(online_sharpe, -3.0, 3.0) * 0.5

    # Total reward
    total = (
        ret_component
        + sharpe_component
        - turnover_penalty
        - concentration_penalty
        - drawdown_penalty
        - cvar_penalty
    )

    components = {
        "ret_component": ret_component,
        "sharpe_component": sharpe_component,
        "turnover_penalty": -turnover_penalty,
        "concentration_penalty": -concentration_penalty,
        "drawdown_penalty": -drawdown_penalty,
        "cvar_penalty": -cvar_penalty,
        "drawdown": drawdown,
        "online_sharpe": float(online_sharpe),
        "cvar": float(cvar),
    }

    new_state = {
        "ret_history": ret_history,
        "peak": peak,
        "cum_value": cum_value,
        "ema_ret": ema_ret,
        "ema_sq": ema_sq,
        "ema_alpha": alpha,
        "step": step + 1,
    }

    return float(total), components, new_state