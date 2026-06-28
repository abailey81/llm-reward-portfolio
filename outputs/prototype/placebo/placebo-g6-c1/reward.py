def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Retrieve / initialise state ───────────────────────────────────────
    state = info.get("reward_state") or {}
    rets_history = state.get("rets_history", [])
    peak         = state.get("peak", 1.0)
    equity       = state.get("equity", 1.0)
    step         = state.get("step", 0)

    # ── Update equity curve & drawdown ───────────────────────────────────
    equity = equity * (1.0 + port_ret)
    peak   = max(peak, equity)
    dd     = (equity - peak) / peak   # <= 0

    # ── Record return ─────────────────────────────────────────────────────
    rets_history.append(port_ret)
    # Keep a rolling window (252 steps ~ 1 year)
    window = 252
    if len(rets_history) > window:
        rets_history = rets_history[-window:]

    step += 1

    # ── Online Sharpe (annualised, daily assumed) ─────────────────────────
    arr = np.array(rets_history, dtype=np.float64)
    if len(arr) >= 5:
        mu    = np.mean(arr)
        sigma = np.std(arr, ddof=1) + 1e-8
        sharpe = (mu / sigma) * np.sqrt(252)
    else:
        sharpe = 0.0

    # ── Turnover penalty ─────────────────────────────────────────────────
    turnover = np.sum(np.abs(weights - prev_weights))
    turnover_penalty = 0.5 * turnover   # proportional penalty

    # ── CVaR penalty (tail loss over history) ────────────────────────────
    if len(arr) >= 10:
        alpha      = 0.05
        cutoff     = int(np.floor(alpha * len(arr)))
        cutoff     = max(cutoff, 1)
        sorted_r   = np.sort(arr)
        cvar       = np.mean(sorted_r[:cutoff])   # expected shortfall, <= 0 typically
        cvar_penalty = max(-cvar, 0.0) * 2.0
    else:
        cvar_penalty = 0.0

    # ── Drawdown penalty ─────────────────────────────────────────────────
    dd_penalty = abs(min(dd, 0.0)) * 1.0

    # ── Concentration penalty (entropy regularisation) ───────────────────
    # Encourage diversification; penalise extreme concentration
    n = len(weights)
    w_clip = np.clip(weights, 1e-8, 1.0)
    entropy = -np.sum(w_clip * np.log(w_clip))
    max_entropy = np.log(n)
    concentration_penalty = 0.1 * max(0.0, (max_entropy - entropy) / max_entropy)

    # ── Compose reward ────────────────────────────────────────────────────
    # Primary: running Sharpe (already risk-adjusted)
    # Modulate by step to avoid noise early on
    ramp = min(step / 20.0, 1.0)

    total = (
        ramp * sharpe * 0.1            # scale Sharpe to reasonable magnitude
        - turnover_penalty
        - cvar_penalty
        - dd_penalty
        - concentration_penalty
        + port_ret * 10.0              # immediate return signal to bootstrap learning
    )

    components = {
        "sharpe":               sharpe,
        "sharpe_contrib":       ramp * sharpe * 0.1,
        "port_ret":             port_ret,
        "turnover_penalty":     -turnover_penalty,
        "cvar_penalty":         -cvar_penalty,
        "dd_penalty":           -dd_penalty,
        "concentration_penalty":-concentration_penalty,
        "drawdown":             dd,
        "equity":               equity,
        "step":                 float(step),
    }

    reward_state = {
        "rets_history": rets_history,
        "peak":         peak,
        "equity":       equity,
        "step":         step,
    }

    return float(total), components, reward_state