def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_mean": 0.0,
            "ret_var": 1e-8,
            "n": 0,
            "peak": 1.0,
            "cum_value": 1.0,
            "ema_ret": 0.0,
            "ema_sq": 1e-8,
            "alpha": 0.05,  # EMA decay for ~20-step window
        }

    alpha = state["alpha"]
    n = state["n"] + 1

    # --- EMA-based online mean and variance of portfolio returns ---
    ema_ret = state["ema_ret"]
    ema_sq = state["ema_sq"]

    ema_ret_new = alpha * port_ret + (1 - alpha) * ema_ret
    ema_sq_new = alpha * (port_ret ** 2) + (1 - alpha) * ema_sq
    ema_var = max(ema_sq_new - ema_ret_new ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)

    # --- Sharpe-like signal ---
    sharpe_signal = ema_ret_new / ema_std

    # --- Drawdown penalty ---
    cum_value = state["cum_value"] * (1.0 + port_ret)
    peak = max(state["peak"], cum_value)
    drawdown = (peak - cum_value) / (peak + 1e-8)
    drawdown_penalty = drawdown ** 2  # quadratic to penalize deep drawdowns more

    # --- Tail risk penalty: extra penalty for large negative returns ---
    tail_threshold = -0.02  # 2% single-step loss threshold
    tail_penalty = 0.0
    if port_ret < tail_threshold:
        tail_penalty = (port_ret - tail_threshold) ** 2 * 10.0

    # --- Diversification bonus (entropy of weights, excluding cash if last) ---
    w_clipped = np.clip(weights, 1e-8, 1.0)
    entropy = -np.sum(w_clipped * np.log(w_clipped))
    n_assets = len(weights)
    max_entropy = np.log(n_assets + 1e-8)
    div_bonus = 0.1 * (entropy / (max_entropy + 1e-8))

    # --- Turnover penalty (supplemental) ---
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.05 * turnover

    # --- Combine components ---
    # Warm-up: scale down signal for first few steps
    warmup_scale = min(1.0, n / 20.0)

    total = (
        warmup_scale * sharpe_signal
        - 3.0 * drawdown_penalty
        - tail_penalty
        + div_bonus
        - turnover_penalty
    )

    components = {
        "sharpe_signal": float(warmup_scale * sharpe_signal),
        "drawdown_penalty": float(-3.0 * drawdown_penalty),
        "tail_penalty": float(-tail_penalty),
        "div_bonus": float(div_bonus),
        "turnover_penalty": float(-turnover_penalty),
    }

    # Update state
    state["ema_ret"] = ema_ret_new
    state["ema_sq"] = ema_sq_new
    state["cum_value"] = cum_value
    state["peak"] = peak
    state["n"] = n

    return float(total), components, state