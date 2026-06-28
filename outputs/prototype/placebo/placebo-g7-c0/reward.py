def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

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
            "alpha": 0.05,  # EMA decay for ~20-step window
        }

    alpha = state["alpha"]
    step = state["step"]

    # Update EMA of returns and squared returns (online Sharpe)
    ema_ret = state["ema_ret"]
    ema_sq = state["ema_sq"]

    if step == 0:
        ema_ret = port_ret
        ema_sq = port_ret ** 2
    else:
        ema_ret = alpha * port_ret + (1 - alpha) * ema_ret
        ema_sq = alpha * (port_ret ** 2) + (1 - alpha) * ema_sq

    ema_var = max(ema_sq - ema_ret ** 2, 1e-8)
    ema_std = np.sqrt(ema_var)

    # Sharpe-like signal (annualized loosely)
    sharpe_signal = ema_ret / ema_std

    # Track cumulative portfolio value for drawdown
    cum_value = state["cum_value"] * (1.0 + port_ret)
    peak = max(state["peak"], cum_value)
    drawdown = (peak - cum_value) / peak  # in [0, 1]

    # Drawdown penalty (quadratic to penalize deep drawdowns more)
    drawdown_penalty = drawdown ** 2

    # Tail penalty: extra penalty for very negative single-step returns
    tail_threshold = -0.02  # -2% single step
    tail_penalty = min(port_ret - tail_threshold, 0.0) ** 2  # only fires if port_ret < threshold

    # Concentration penalty (encourage diversification)
    # Herfindahl index: sum of squared weights (excluding cash = last element)
    asset_weights = weights[:-1] if len(weights) > 1 else weights
    herfindahl = float(np.sum(asset_weights ** 2))
    n = max(len(asset_weights), 1)
    # Normalize: 1/n is perfectly diversified, 1.0 is fully concentrated
    concentration_penalty = herfindahl - 1.0 / n

    # Combine components
    w_sharpe = 1.0
    w_drawdown = 2.0
    w_tail = 5.0
    w_conc = 0.1

    total = (
        w_sharpe * sharpe_signal
        - w_drawdown * drawdown_penalty
        - w_tail * tail_penalty
        - w_conc * concentration_penalty
    )

    components = {
        "sharpe_signal": float(sharpe_signal),
        "drawdown_penalty": float(-w_drawdown * drawdown_penalty),
        "tail_penalty": float(-w_tail * tail_penalty),
        "concentration_penalty": float(-w_conc * concentration_penalty),
        "ema_ret": float(ema_ret),
        "ema_std": float(ema_std),
        "drawdown": float(drawdown),
        "port_ret": float(port_ret),
    }

    # Update state
    state["ema_ret"] = ema_ret
    state["ema_sq"] = ema_sq
    state["cum_value"] = cum_value
    state["peak"] = peak
    state["step"] = step + 1

    return float(total), components, state