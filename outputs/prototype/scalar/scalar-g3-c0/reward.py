def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Recover / initialise state ──────────────────────────────────────────
    state = info.get("reward_state") or {}

    ret_history = state.get("ret_history", [])
    high_water  = state.get("high_water", 1.0)
    cum_value   = state.get("cum_value", 1.0)

    # ── Update cumulative value & drawdown ──────────────────────────────────
    cum_value  = cum_value * (1.0 + port_ret)
    high_water = max(high_water, cum_value)
    drawdown   = (cum_value - high_water) / (high_water + 1e-8)  # <= 0

    # ── Maintain rolling return window (up to 60 steps) ────────────────────
    ret_history.append(float(port_ret))
    window = 60
    if len(ret_history) > window:
        ret_history = ret_history[-window:]

    arr = np.array(ret_history, dtype=np.float64)
    n   = len(arr)

    # ── Online Sharpe (annualised, assuming ~252 steps/year) ────────────────
    if n >= 5:
        mu  = np.mean(arr)
        sig = np.std(arr, ddof=1) + 1e-8
        sharpe_contrib = (mu / sig) * np.sqrt(252)
    else:
        sharpe_contrib = 0.0

    # ── Tail-risk penalty: mean of worst 10% returns (CVaR) ─────────────────
    if n >= 10:
        cutoff     = max(1, int(np.floor(0.10 * n)))
        tail_ret   = np.sort(arr)[:cutoff]
        cvar       = np.mean(tail_ret)           # negative number
        tail_pen   = min(0.0, cvar) * 3.0        # amplify tail loss
    else:
        tail_pen = 0.0

    # ── Drawdown penalty (proportional, but capped) ──────────────────────────
    dd_penalty = np.clip(drawdown * 2.0, -1.0, 0.0)

    # ── Turnover penalty (discourages churning) ──────────────────────────────
    turnover    = float(np.sum(np.abs(weights - prev_weights)))
    to_penalty  = -0.05 * turnover

    # ── Combine ──────────────────────────────────────────────────────────────
    # Primary driver: Sharpe contribution (already risk-adjusted)
    # Auxiliary: drawdown, CVaR tail, turnover
    total = (
        0.5  * sharpe_contrib
        + 0.3  * dd_penalty
        + 0.15 * tail_pen
        + to_penalty
        + port_ret * 5.0   # immediate return signal to bootstrap learning
    )

    components = {
        "sharpe_contrib": sharpe_contrib,
        "dd_penalty":     dd_penalty,
        "tail_pen":       tail_pen,
        "to_penalty":     to_penalty,
        "port_ret":       port_ret,
    }

    reward_state = {
        "ret_history": ret_history,
        "high_water":  high_water,
        "cum_value":   cum_value,
    }

    return float(total), components, reward_state