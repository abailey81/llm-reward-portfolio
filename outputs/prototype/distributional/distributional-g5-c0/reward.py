def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Recover or initialize state ---
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history": [],
            "n": 0,
            "mean": 0.0,
            "M2": 0.0,       # for Welford online variance
            "ema_mean": 0.0,
            "ema_var": 1e-8,
        }

    # --- Update Welford online mean/variance ---
    n = state["n"] + 1
    mean_old = state["mean"]
    M2_old = state["M2"]

    delta = port_ret - mean_old
    mean_new = mean_old + delta / n
    delta2 = port_ret - mean_new
    M2_new = M2_old + delta * delta2

    state["n"] = n
    state["mean"] = mean_new
    state["M2"] = M2_new

    # Online std (Welford)
    if n > 2:
        var = M2_new / (n - 1)
        std = np.sqrt(max(var, 1e-10))
    else:
        std = 1e-4

    # --- Maintain a rolling window for CVaR ---
    hist = state["ret_history"]
    hist.append(float(port_ret))
    # Keep last 200 steps
    if len(hist) > 200:
        hist.pop(0)
    state["ret_history"] = hist

    # --- EMA-based Sharpe signal (faster adaptation) ---
    alpha = 0.05
    ema_mean = (1 - alpha) * state["ema_mean"] + alpha * port_ret
    ema_var  = (1 - alpha) * state["ema_var"]  + alpha * (port_ret - ema_mean) ** 2
    state["ema_mean"] = ema_mean
    state["ema_var"]  = max(ema_var, 1e-10)
    ema_std = np.sqrt(state["ema_var"])

    # Blend online Sharpe (global) and EMA Sharpe (local)
    sharpe_global = mean_new / std
    sharpe_ema    = ema_mean / ema_std
    sharpe_signal = 0.5 * sharpe_global + 0.5 * sharpe_ema

    # --- CVaR penalty (5th percentile of recent returns) ---
    cvar_penalty = 0.0
    if len(hist) >= 20:
        arr = np.array(hist)
        cutoff = np.percentile(arr, 5)
        tail = arr[arr <= cutoff]
        if len(tail) > 0:
            cvar = float(np.mean(tail))
            # penalize negative CVaR
            cvar_penalty = min(cvar, 0.0)  # negative number → penalty

    # --- Turnover penalty ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = -0.5 * turnover

    # --- Drawdown penalty from recent history ---
    drawdown_penalty = 0.0
    if len(hist) >= 5:
        arr = np.array(hist)
        cum = np.cumprod(1.0 + np.clip(arr, -0.5, None))
        running_max = np.maximum.accumulate(cum)
        dd = (cum - running_max) / (running_max + 1e-10)
        current_dd = float(dd[-1])
        drawdown_penalty = min(current_dd, 0.0)  # negative or zero

    # --- Concentration penalty (encourage diversification) ---
    # Penalize very concentrated portfolios (Herfindahl)
    hhi = float(np.sum(weights ** 2))
    n_assets = len(weights)
    hhi_min = 1.0 / n_assets  # perfectly diversified
    concentration_penalty = -0.5 * max(hhi - hhi_min, 0.0)

    # --- Combine components ---
    # Scale sharpe signal to be meaningful per-step
    sharpe_component   = 0.4 * np.tanh(sharpe_signal * 10)  # bounded
    cvar_component     = 2.0 * cvar_penalty
    turnover_component = turnover_penalty
    drawdown_component = 1.0 * drawdown_penalty
    conc_component     = concentration_penalty

    # Direct return signal (scaled) for early learning
    ret_component = 10.0 * port_ret

    total = (
        ret_component
        + sharpe_component
        + cvar_component
        + turnover_component
        + drawdown_component
        + conc_component
    )

    components = {
        "ret":          ret_component,
        "sharpe":       float(sharpe_component),
        "cvar":         float(cvar_component),
        "turnover":     float(turnover_component),
        "drawdown":     float(drawdown_component),
        "concentration":float(conc_component),
    }

    return float(total), components, state