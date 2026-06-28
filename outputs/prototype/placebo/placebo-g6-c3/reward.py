def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "peak": 1.0,
            "cum_value": 1.0,
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "alpha": 0.05,   # EMA decay for online Sharpe
            "step": 0,
        }

    alpha = state["alpha"]
    step = state["step"]

    # Update cumulative portfolio value & drawdown
    state["cum_value"] *= (1.0 + port_ret)
    state["peak"] = max(state["peak"], state["cum_value"])
    drawdown = (state["peak"] - state["cum_value"]) / (state["peak"] + 1e-8)

    # Keep a rolling window of recent returns for Sharpe estimation
    state["ret_history"].append(port_ret)
    window = 60
    if len(state["ret_history"]) > window:
        state["ret_history"].pop(0)

    hist = np.array(state["ret_history"])
    n = len(hist)

    # Online EMA-based mean and variance
    state["ema_ret"] = (1 - alpha) * state["ema_ret"] + alpha * port_ret
    state["ema_sq"] = (1 - alpha) * state["ema_sq"] + alpha * port_ret ** 2
    ema_var = state["ema_sq"] - state["ema_ret"] ** 2
    ema_std = np.sqrt(max(ema_var, 1e-8))

    # Core: Sharpe-like signal from EMA
    sharpe_signal = state["ema_ret"] / ema_std

    # Rolling Sharpe (more stable once we have enough data)
    if n >= 5:
        roll_mean = np.mean(hist)
        roll_std = np.std(hist) + 1e-8
        roll_sharpe = roll_mean / roll_std
    else:
        roll_sharpe = 0.0

    # Blend EMA and rolling Sharpe
    blend = min(n / window, 1.0)
    sharpe_component = (1 - blend) * sharpe_signal + blend * roll_sharpe

    # Turnover penalty — discourage excessive rebalancing
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.5 * turnover

    # Drawdown penalty — convex to penalize deep drawdowns more
    dd_penalty = 2.0 * (drawdown ** 1.5)

    # Tail loss penalty: penalize large negative returns directly
    tail_penalty = 0.0
    if port_ret < -0.02:
        tail_penalty = 5.0 * abs(port_ret)

    # Raw return as a small direct signal
    ret_component = 10.0 * port_ret

    # Total reward
    total = (
        sharpe_component
        + ret_component
        - turnover_penalty
        - dd_penalty
        - tail_penalty
    )

    state["step"] = step + 1

    components = {
        "sharpe_component": sharpe_component,
        "ret_component": ret_component,
        "turnover_penalty": -turnover_penalty,
        "dd_penalty": -dd_penalty,
        "tail_penalty": -tail_penalty,
    }

    return float(total), components, state