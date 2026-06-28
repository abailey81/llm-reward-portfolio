def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Retrieve or initialize persistent state ──────────────────────────────
    state = info.get("reward_state") or {}

    # Rolling window of portfolio returns (for CVaR and Sharpe)
    ret_history = state.get("ret_history", [])
    peak_value  = state.get("peak_value", 1.0)
    cum_value   = state.get("cum_value", 1.0)

    # Update cumulative portfolio value
    cum_value = cum_value * (1.0 + port_ret)
    peak_value = max(peak_value, cum_value)

    # Store return in history (keep last 120 steps)
    ret_history.append(port_ret)
    WINDOW = 120
    if len(ret_history) > WINDOW:
        ret_history = ret_history[-WINDOW:]

    ret_arr = np.array(ret_history, dtype=np.float64)
    n = len(ret_arr)

    # ── 1. Sharpe-like signal (exponentially weighted) ───────────────────────
    if n >= 2:
        # Exponential weights — more recent steps matter more
        decay = 0.97
        ew = np.array([decay ** (n - 1 - i) for i in range(n)])
        ew /= ew.sum()
        ew_mean = np.dot(ew, ret_arr)
        ew_var  = np.dot(ew, (ret_arr - ew_mean) ** 2)
        ew_std  = np.sqrt(ew_var + 1e-8)
        sharpe_signal = ew_mean / ew_std
    else:
        sharpe_signal = 0.0

    # ── 2. CVaR penalty (5% tail) ────────────────────────────────────────────
    if n >= 20:
        sorted_rets = np.sort(ret_arr)
        cutoff_idx  = max(1, int(np.floor(0.05 * n)))
        cvar_5      = sorted_rets[:cutoff_idx].mean()   # negative = bad
        cvar_penalty = min(0.0, cvar_5)   # only penalize negative tail
    else:
        cvar_penalty = 0.0

    # ── 3. Drawdown penalty ───────────────────────────────────────────────────
    drawdown = (cum_value - peak_value) / (peak_value + 1e-8)   # <= 0
    drawdown_penalty = min(0.0, drawdown)

    # ── 4. Turnover / transaction cost signal ────────────────────────────────
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -turnover

    # ── 5. Concentration penalty (encourage diversification) ─────────────────
    # Penalize HHI above a threshold
    n_assets = len(weights)
    hhi = np.sum(weights ** 2)
    hhi_neutral = 1.0 / max(n_assets, 1)
    concentration_penalty = -max(0.0, hhi - 2.0 * hhi_neutral)

    # ── Combine components ────────────────────────────────────────────────────
    # Scale factors tuned to keep components in similar magnitudes
    w_sharpe        = 1.0
    w_cvar          = 5.0
    w_drawdown      = 2.0
    w_turnover      = 0.1
    w_concentration = 0.5

    total = (
        w_sharpe        * sharpe_signal
        + w_cvar        * cvar_penalty
        + w_drawdown    * drawdown_penalty
        + w_turnover    * turnover_penalty
        + w_concentration * concentration_penalty
    )

    components = {
        "sharpe_signal":        sharpe_signal,
        "cvar_penalty":         w_cvar * cvar_penalty,
        "drawdown_penalty":     w_drawdown * drawdown_penalty,
        "turnover_penalty":     w_turnover * turnover_penalty,
        "concentration_penalty": w_concentration * concentration_penalty,
    }

    reward_state = {
        "ret_history": ret_history,
        "peak_value":  peak_value,
        "cum_value":   cum_value,
    }

    return float(total), components, reward_state