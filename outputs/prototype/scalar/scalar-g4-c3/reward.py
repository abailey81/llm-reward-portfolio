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
            "step": 0,
        }

    step = state["step"] + 1
    ret_history = state["ret_history"]
    ret_history.append(port_ret)

    # Keep a rolling window for Sharpe estimation
    window = 60
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    # Update cumulative value for drawdown tracking
    cum_value = state["cum_value"] * (1.0 + port_ret)
    peak = max(state["peak"], cum_value)
    drawdown = (peak - cum_value) / (peak + 1e-8)

    # EMA-based online Sharpe (faster adaptation)
    alpha = 0.06  # ~16-step half-life
    ema_ret = alpha * port_ret + (1 - alpha) * state["ema_ret"]
    ema_sq  = alpha * (port_ret ** 2) + (1 - alpha) * state["ema_sq"]
    ema_var = max(ema_sq - ema_ret ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)

    # Annualised Sharpe proxy (daily steps assumed, ~252 trading days)
    annualization = np.sqrt(252)
    sharpe_proxy = (ema_ret / ema_std) * annualization

    # Rolling-window Sharpe for stability (once enough history)
    if len(ret_history) >= 10:
        arr = np.array(ret_history)
        mu  = np.mean(arr)
        sig = np.std(arr) + 1e-8
        rolling_sharpe = (mu / sig) * annualization
    else:
        rolling_sharpe = sharpe_proxy

    # Blend EMA and rolling Sharpe
    sharpe_signal = 0.5 * sharpe_proxy + 0.5 * rolling_sharpe

    # Turnover penalty (L1 weight change)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.1 * turnover

    # Drawdown penalty — penalise being in drawdown, extra for large drawdowns
    dd_penalty = 2.0 * drawdown + 5.0 * max(drawdown - 0.10, 0.0)

    # Tail loss penalty: penalize large negative returns asymmetrically
    tail_thresh = -0.02
    tail_penalty = 3.0 * max(-port_ret - abs(tail_thresh), 0.0)

    # Concentration penalty (encourage diversification but not force it)
    # Herfindahl index on risky weights (all except last cash element)
    risky = weights[:-1]
    hhi = np.sum(risky ** 2) if risky.sum() > 1e-6 else 0.0
    concentration_penalty = 0.5 * hhi

    # Total reward: Sharpe-driven signal minus risk penalties
    # Scale sharpe_signal so it's in a reasonable range
    sharpe_component = np.clip(sharpe_signal / 10.0, -2.0, 2.0)

    total = (
        sharpe_component
        - turnover_penalty
        - dd_penalty
        - tail_penalty
        - concentration_penalty
    )

    components = {
        "sharpe_signal":         float(sharpe_component),
        "turnover_penalty":      float(-turnover_penalty),
        "drawdown_penalty":      float(-dd_penalty),
        "tail_penalty":          float(-tail_penalty),
        "concentration_penalty": float(-concentration_penalty),
        "port_ret":              float(port_ret),
        "drawdown":              float(drawdown),
    }

    reward_state = {
        "ret_history": ret_history,
        "peak":        peak,
        "cum_value":   cum_value,
        "ema_ret":     ema_ret,
        "ema_sq":      ema_sq,
        "step":        step,
    }

    return float(total), components, reward_state