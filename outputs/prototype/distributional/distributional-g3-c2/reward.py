def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ema_ret": 0.0,
            "ema_sq": 0.0,
            "peak": 1.0,
            "cumulative": 1.0,
            "alpha": 0.05,       # EMA decay for Sharpe
            "alpha_slow": 0.01,  # slow EMA for drawdown tracking
            "step": 0,
            "ret_history": [],
        }

    alpha = state["alpha"]
    step = state["step"] + 1
    state["step"] = step

    # Bias-corrected EMA for mean and variance of returns
    ema_ret = state["ema_ret"] * (1 - alpha) + port_ret * alpha
    ema_sq  = state["ema_sq"]  * (1 - alpha) + (port_ret ** 2) * alpha

    state["ema_ret"] = ema_ret
    state["ema_sq"]  = ema_sq

    # Bias correction
    correction = 1.0 - (1.0 - alpha) ** step
    mean_est = ema_ret / correction
    sq_est   = ema_sq  / correction
    var_est  = max(sq_est - mean_est ** 2, 1e-8)
    std_est  = np.sqrt(var_est)

    # Online Sharpe (annualized scaling optional, keep daily for stability)
    online_sharpe = mean_est / std_est

    # Drawdown penalty
    state["cumulative"] = state["cumulative"] * (1.0 + port_ret)
    state["peak"] = max(state["peak"], state["cumulative"])
    drawdown = (state["cumulative"] - state["peak"]) / (state["peak"] + 1e-8)
    # drawdown <= 0 always

    # Turnover penalty (on top of built-in costs)
    turnover = float(np.sum(np.abs(weights - prev_weights)))

    # Tail penalty: penalize large negative returns directly
    tail_penalty = min(port_ret, 0.0) ** 2  # quadratic downside

    # Concentration penalty (encourage diversification, avoid all-cash)
    # Entropy of weights
    w_clipped = np.clip(weights, 1e-8, 1.0)
    entropy = -float(np.sum(w_clipped * np.log(w_clipped)))
    max_entropy = np.log(len(weights))
    entropy_ratio = entropy / (max_entropy + 1e-8)

    # Combine components
    # Primary: online Sharpe drives long-run risk-adjusted perf
    # Secondary: direct return gives fast learning signal
    # Tertiary: drawdown and tail penalize risk
    sharpe_component   =  1.0  * online_sharpe
    return_component   =  5.0  * port_ret          # direct, fast signal
    drawdown_component = -2.0  * abs(drawdown)
    tail_component     = -10.0 * tail_penalty
    turnover_component = -0.5  * turnover
    entropy_component  =  0.1  * entropy_ratio      # mild diversification nudge

    total = (sharpe_component + return_component + drawdown_component +
             tail_component + turnover_component + entropy_component)

    components = {
        "sharpe":    sharpe_component,
        "return":    return_component,
        "drawdown":  drawdown_component,
        "tail":      tail_component,
        "turnover":  turnover_component,
        "entropy":   entropy_component,
    }

    return float(total), components, state