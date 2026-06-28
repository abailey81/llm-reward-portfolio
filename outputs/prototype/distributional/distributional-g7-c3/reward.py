def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # --- Restore or initialize state ---
    state = info.get("reward_state") or {}
    
    # Rolling window for return history (for CVaR estimation)
    history = list(state.get("history", []))
    
    # Online mean/variance tracking (Welford)
    n       = state.get("n", 0)
    mean    = state.get("mean", 0.0)
    M2      = state.get("M2", 0.0)
    
    # Drawdown tracking
    peak    = state.get("peak", 1.0)
    cum_ret = state.get("cum_ret", 1.0)

    # --- Update cumulative return and drawdown ---
    cum_ret  = cum_ret * (1.0 + port_ret)
    peak     = max(peak, cum_ret)
    drawdown = (peak - cum_ret) / peak  # in [0, 1]

    # --- Welford online update for mean & variance ---
    n      += 1
    delta   = port_ret - mean
    mean   += delta / n
    delta2  = port_ret - mean
    M2     += delta * delta2
    variance = M2 / n if n > 1 else 1e-8
    std      = max(np.sqrt(variance), 1e-8)

    # --- Maintain rolling window (last 100 steps) ---
    history.append(port_ret)
    window = 100
    if len(history) > window:
        history = history[-window:]

    # --- CVaR penalty using rolling window ---
    cvar_penalty = 0.0
    if len(history) >= 10:
        arr = np.array(history)
        threshold_5  = np.percentile(arr, 5)
        tail_losses  = arr[arr <= threshold_5]
        cvar_5       = float(np.mean(tail_losses)) if len(tail_losses) > 0 else 0.0
        # Penalize negative tail mean
        cvar_penalty = min(cvar_5, 0.0)  # negative or zero

    # --- Turnover / transaction cost penalty ---
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = 0.3 * turnover

    # --- Online Sharpe-like signal ---
    sharpe_signal = mean / std  # annualization not needed for RL signal

    # --- Drawdown penalty (convex — punish large drawdowns harder) ---
    dd_penalty = 2.0 * (drawdown ** 2)

    # --- Concentration penalty (encourage diversification) ---
    # Herfindahl index on risky assets (exclude cash = last element)
    risky_w = weights[:-1]
    herfindahl = float(np.sum(risky_w ** 2))
    concentration_penalty = 0.1 * herfindahl

    # --- Assemble total reward ---
    # Core: port_ret scaled by inverse-vol (risk-adjusted step return)
    risk_adj_return = port_ret / std

    # CVaR penalty weight: scaled to be meaningful
    cvar_weight = 3.0
    
    total = (
        risk_adj_return
        - cvar_weight * abs(cvar_penalty)   # tail risk penalty
        - dd_penalty                          # drawdown penalty
        - turnover_penalty                    # transaction cost
        - concentration_penalty               # diversification nudge
    )

    components = {
        "risk_adj_return":      risk_adj_return,
        "cvar_penalty":         -cvar_weight * abs(cvar_penalty),
        "drawdown_penalty":     -dd_penalty,
        "turnover_penalty":     -turnover_penalty,
        "concentration_penalty":-concentration_penalty,
        "sharpe_signal":         sharpe_signal,
        "drawdown":              drawdown,
    }

    reward_state = {
        "history":  history,
        "n":        n,
        "mean":     mean,
        "M2":       M2,
        "peak":     peak,
        "cum_ret":  cum_ret,
    }

    return float(total), components, reward_state