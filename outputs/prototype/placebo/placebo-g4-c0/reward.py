def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ema_ret": 0.0,
            "ema_var": 1e-6,
            "peak": 1.0,
            "cumulative": 1.0,
            "step": 0,
            "recent_rets": [],
            "alpha": 0.05,  # EMA decay for short-term smoothing
        }

    alpha = state["alpha"]
    step = state["step"] + 1

    # Update EMA of return and variance
    ema_ret = (1 - alpha) * state["ema_ret"] + alpha * port_ret
    deviation = port_ret - ema_ret
    ema_var = (1 - alpha) * state["ema_var"] + alpha * (deviation ** 2)
    ema_std = np.sqrt(max(ema_var, 1e-8))

    # Online Sharpe component (annualized roughly)
    sharpe_signal = ema_ret / ema_std

    # Drawdown penalty
    cumulative = state["cumulative"] * (1.0 + port_ret)
    peak = max(state["peak"], cumulative)
    drawdown = (peak - cumulative) / max(peak, 1e-8)
    drawdown_penalty = drawdown ** 2  # squared to penalize deep drawdowns more

    # Turnover penalty (proxy for transaction costs beyond what port_ret already deducts)
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.1 * turnover

    # Concentration penalty (encourage diversification, reduce single-asset risk)
    n_assets = len(weights)
    hhi = np.sum(weights ** 2)  # Herfindahl index: 1/n = perfect diversification
    concentration_penalty = 0.05 * hhi

    # Tail loss (downside) penalty
    tail_penalty = 0.5 * max(-port_ret, 0.0) ** 2

    # Combine components
    # Core: Sharpe signal scaled + raw return signal
    # Penalties for drawdown, turnover, concentration, tail
    core = sharpe_signal + port_ret  # both scale similarly
    total = (
        core
        - 2.0 * drawdown_penalty
        - turnover_penalty
        - concentration_penalty
        - tail_penalty
    )

    # Warm-up scaling: reduce signal magnitude in early steps to avoid misleading gradients
    warmup = min(1.0, step / 20.0)
    total = total * warmup

    # Update state
    state["ema_ret"] = ema_ret
    state["ema_var"] = ema_var
    state["peak"] = peak
    state["cumulative"] = cumulative
    state["step"] = step

    components = {
        "sharpe_signal": float(sharpe_signal),
        "port_ret": float(port_ret),
        "drawdown_penalty": float(-2.0 * drawdown_penalty),
        "turnover_penalty": float(-turnover_penalty),
        "concentration_penalty": float(-concentration_penalty),
        "tail_penalty": float(-tail_penalty),
        "drawdown": float(drawdown),
        "ema_ret": float(ema_ret),
        "ema_std": float(ema_std),
        "warmup": float(warmup),
    }

    return float(total), components, state