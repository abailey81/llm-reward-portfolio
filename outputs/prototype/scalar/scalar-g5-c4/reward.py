def reward(weights, returns, prev_weights, port_ret, info):
    # Initialize / retrieve state
    state = info.get("reward_state") or {}

    # EMA parameters
    alpha_fast = 0.05   # ~20-step memory for mean
    alpha_slow = 0.02   # ~50-step memory for variance

    # Retrieve running stats
    ema_ret    = state.get("ema_ret",    port_ret)
    ema_sq     = state.get("ema_sq",     port_ret ** 2)
    peak       = state.get("peak",       1.0)
    nav        = state.get("nav",        1.0)
    step       = state.get("step",       0)

    # Update NAV and drawdown peak
    nav  = nav * (1.0 + port_ret)
    peak = max(peak, nav)
    drawdown = (peak - nav) / (peak + 1e-8)

    # Update EMA mean and EMA of squared returns (for variance)
    ema_ret = (1 - alpha_fast) * ema_ret + alpha_fast * port_ret
    ema_sq  = (1 - alpha_slow) * ema_sq  + alpha_slow * port_ret ** 2

    # Online variance and std
    variance = max(ema_sq - ema_ret ** 2, 1e-8)
    std      = np.sqrt(variance)

    # Sharpe-like signal (annualised direction, not magnitude)
    sharpe_signal = ema_ret / (std + 1e-8)

    # Incremental Sharpe: reward the step return scaled by running vol
    step_sharpe = port_ret / (std + 1e-8)

    # Drawdown penalty — convex to punish deep drawdowns more
    dd_penalty = drawdown ** 2

    # Turnover cost (small friction signal)
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = 0.1 * turnover

    # Tail penalty: penalise large negative returns (CVaR-like proxy)
    tail_penalty = 0.0
    if port_ret < -0.02:
        tail_penalty = 5.0 * (port_ret + 0.02) ** 2  # quadratic beyond -2%

    # Combine: primary signal is step Sharpe, shaped by drawdown and tail
    total = (
        step_sharpe
        - 2.0 * dd_penalty
        - turnover_penalty
        - tail_penalty
    )

    step += 1

    reward_state = {
        "ema_ret": ema_ret,
        "ema_sq":  ema_sq,
        "peak":    peak,
        "nav":     nav,
        "step":    step,
    }

    components = {
        "step_sharpe":      step_sharpe,
        "sharpe_signal":    sharpe_signal,
        "dd_penalty":       dd_penalty,
        "turnover_penalty": turnover_penalty,
        "tail_penalty":     tail_penalty,
    }

    return float(total), components, reward_state