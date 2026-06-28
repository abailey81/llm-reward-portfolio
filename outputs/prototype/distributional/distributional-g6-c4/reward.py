def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # Initialize or retrieve state
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_history": [],
            "peak_value": 1.0,
            "cum_value": 1.0,
            "ema_mean": 0.0,
            "ema_var": 1e-6,
            "step": 0,
            "cvar_window": [],
        }

    step = state["step"] + 1
    state["step"] = step

    # Update cumulative portfolio value
    cum_value = state["cum_value"] * (1.0 + port_ret)
    state["cum_value"] = cum_value

    # Update peak and drawdown
    peak = max(state["peak_value"], cum_value)
    state["peak_value"] = peak
    drawdown = (peak - cum_value) / (peak + 1e-8)

    # Track returns history
    state["returns_history"].append(port_ret)
    window = state["returns_history"][-252:]  # ~1 year window
    state["returns_history"] = window

    # Update CVaR tracking window (larger)
    cvar_window = state["cvar_window"]
    cvar_window.append(port_ret)
    if len(cvar_window) > 500:
        cvar_window = cvar_window[-500:]
    state["cvar_window"] = cvar_window

    # Online EMA Sharpe (fast adaptation)
    alpha = 0.05  # EMA decay
    ema_mean = (1 - alpha) * state["ema_mean"] + alpha * port_ret
    ema_var = (1 - alpha) * state["ema_var"] + alpha * (port_ret - ema_mean) ** 2
    state["ema_mean"] = ema_mean
    state["ema_var"] = ema_var
    ema_std = np.sqrt(max(ema_var, 1e-8))

    # --- Component 1: EMA Sharpe signal ---
    sharpe_signal = ema_mean / ema_std

    # --- Component 2: CVaR penalty (tail loss) ---
    cvar_penalty = 0.0
    if len(cvar_window) >= 20:
        arr = np.array(cvar_window)
        # CVaR at 5%
        threshold_5 = np.percentile(arr, 5)
        tail_5 = arr[arr <= threshold_5]
        cvar_5 = float(np.mean(tail_5)) if len(tail_5) > 0 else 0.0
        # CVaR at 10%
        threshold_10 = np.percentile(arr, 10)
        tail_10 = arr[arr <= threshold_10]
        cvar_10 = float(np.mean(tail_10)) if len(tail_10) > 0 else 0.0
        # Weighted CVaR penalty (penalize negative tail)
        cvar_penalty = 2.0 * min(cvar_5, 0.0) + 1.0 * min(cvar_10, 0.0)

    # --- Component 3: Drawdown penalty ---
    # Penalize drawdown non-linearly (quadratic for large drawdowns)
    dd_penalty = -drawdown ** 1.5 * 5.0

    # --- Component 4: Downside deviation (Sortino-like) ---
    sortino_signal = 0.0
    if len(window) >= 10:
        arr_w = np.array(window)
        downside = arr_w[arr_w < 0.0]
        downside_std = np.sqrt(np.mean(downside ** 2)) if len(downside) > 0 else 1e-8
        sortino_signal = np.mean(arr_w) / max(downside_std, 1e-8)

    # --- Component 5: Turnover penalty (transaction costs proxy) ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = -0.5 * turnover

    # --- Component 6: Concentration penalty (encourage diversification) ---
    # Herfindahl index penalizes over-concentration
    hhi = float(np.sum(weights ** 2))
    concentration_penalty = -0.3 * hhi

    # --- Component 7: Direct return component (scaled) ---
    # Use return but clip extremes to reduce noise
    ret_component = np.clip(port_ret, -0.05, 0.05) * 10.0

    # Blend components with warm-up scaling
    warmup = min(1.0, step / 50.0)

    total = (
        ret_component * 0.3
        + sharpe_signal * 0.3 * warmup
        + sortino_signal * 0.2 * warmup
        + cvar_penalty * 3.0 * warmup
        + dd_penalty * warmup
        + turnover_penalty * 0.5
        + concentration_penalty * 0.2
    )

    components = {
        "ret_component": ret_component,
        "sharpe_signal": sharpe_signal,
        "sortino_signal": sortino_signal,
        "cvar_penalty": cvar_penalty,
        "dd_penalty": dd_penalty,
        "turnover_penalty": turnover_penalty,
        "concentration_penalty": concentration_penalty,
    }

    return float(total), components, state