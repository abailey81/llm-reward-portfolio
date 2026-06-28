def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Retrieve or initialize state ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "mean_ret":   0.0,
            "var_ret":    1e-8,
            "peak":       1.0,
            "nav":        1.0,
            "n":          0,
            "ema_alpha":  0.05,   # smoothing factor (~20-step half-life)
        }

    alpha = state["ema_alpha"]
    n     = state["n"] + 1

    # --- Update EMA mean and variance of port_ret ---
    prev_mean = state["mean_ret"]
    prev_var  = state["var_ret"]

    new_mean = (1 - alpha) * prev_mean + alpha * port_ret
    new_var  = (1 - alpha) * prev_var  + alpha * (port_ret - prev_mean) ** 2
    new_var  = max(new_var, 1e-8)

    # --- Online Sharpe component ---
    sharpe_ratio = new_mean / np.sqrt(new_var)

    # Incremental Sharpe: reward the change in estimated Sharpe
    # This gives a per-step signal proportional to improvement in Sharpe
    delta_mean = new_mean - prev_mean
    # Use approximate gradient of Sharpe w.r.t. return
    sigma = np.sqrt(new_var)
    # d(Sharpe)/d(r) ≈ (1/sigma) * (1 - 0.5 * sharpe * r/sigma)
    sharpe_increment = (port_ret - new_mean) / sigma * alpha

    # --- NAV and Drawdown ---
    nav  = state["nav"] * (1.0 + port_ret)
    peak = max(state["peak"], nav)
    drawdown = (nav - peak) / (peak + 1e-8)   # <= 0

    # Drawdown penalty: penalize proportionally to current drawdown depth
    drawdown_penalty = drawdown  # negative when in drawdown

    # --- Turnover penalty (encourage stability) ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.1 * turnover

    # --- Tail-loss penalty: penalize negative returns more than proportionally ---
    tail_penalty = 0.0
    if port_ret < 0.0:
        tail_penalty = -0.5 * (port_ret ** 2) / (new_var + 1e-8)

    # --- Combine ---
    # Main signal: scaled portfolio return adjusted by current risk estimate
    ret_signal = port_ret / sigma

    total = (
        0.6  * ret_signal        +
        0.2  * sharpe_increment  +
        0.1  * drawdown_penalty  +
        0.1  * turnover_penalty  +
        0.05 * tail_penalty
    )

    components = {
        "ret_signal":        ret_signal,
        "sharpe_increment":  sharpe_increment,
        "drawdown_penalty":  drawdown_penalty,
        "turnover_penalty":  turnover_penalty,
        "tail_penalty":      tail_penalty,
    }

    reward_state = {
        "mean_ret":  new_mean,
        "var_ret":   new_var,
        "peak":      peak,
        "nav":       nav,
        "n":         n,
        "ema_alpha": alpha,
    }

    return float(total), components, reward_state