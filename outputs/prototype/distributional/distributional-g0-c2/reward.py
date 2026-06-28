def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Restore or initialise state ──────────────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_window": [],        # rolling window of port_ret values
            "peak": 0.0,                 # running peak for drawdown
            "cum_ret": 0.0,              # cumulative log-like return
            "step": 0,
        }

    state["step"] += 1
    win_size = 60          # rolling window length

    # ── Update rolling returns window ────────────────────────────────────────
    state["returns_window"].append(float(port_ret))
    if len(state["returns_window"]) > win_size:
        state["returns_window"].pop(0)

    arr = np.array(state["returns_window"], dtype=np.float64)

    # ── Cumulative return & drawdown ─────────────────────────────────────────
    state["cum_ret"] += float(port_ret)
    state["peak"] = max(state["peak"], state["cum_ret"])
    drawdown = state["peak"] - state["cum_ret"]          # non-negative

    # ── Rolling statistics (need at least 2 observations) ───────────────────
    n = len(arr)

    if n >= 2:
        roll_mean = arr.mean()
        roll_std  = arr.std(ddof=1) + 1e-8

        # Online Sharpe (annualised by sqrt(252))
        sharpe = (roll_mean / roll_std) * np.sqrt(252)

        # CVaR – expected loss beyond the 5th percentile (tail penalty)
        threshold = np.percentile(arr, 5)
        tail_losses = arr[arr <= threshold]
        cvar = float(tail_losses.mean()) if len(tail_losses) > 0 else float(threshold)
        # cvar is typically negative; we want to penalise large negative values

        # Sortino – downside deviation only
        neg_rets = arr[arr < 0]
        if len(neg_rets) >= 2:
            downside_std = neg_rets.std(ddof=1) + 1e-8
        else:
            downside_std = roll_std
        sortino = (roll_mean / downside_std) * np.sqrt(252)
    else:
        sharpe  = 0.0
        cvar    = float(port_ret)
        sortino = 0.0
        roll_std = 1e-8

    # ── Turnover cost (explicit penalty on top of env cost) ──────────────────
    turnover = 0.5 * float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = 2.0 * turnover          # extra incentive to stay put

    # ── Concentration penalty (encourage diversification) ────────────────────
    risky_w = weights[:30]
    herfindahl = float(np.sum(risky_w ** 2))   # 1/N for uniform; 1 for single asset
    concentration_penalty = herfindahl          # small but persistent signal

    # ── Drawdown penalty ─────────────────────────────────────────────────────
    dd_penalty = 0.5 * drawdown

    # ── CVaR penalty (tail risk) ──────────────────────────────────────────────
    # cvar ≤ 0 usually; we penalise it
    cvar_penalty = -2.0 * cvar                 # positive when cvar is negative

    # ── Composite reward ──────────────────────────────────────────────────────
    # Core: blended Sharpe + Sortino, scaled to be roughly ±1
    risk_adj = 0.5 * sharpe + 0.5 * sortino
    risk_adj_scaled = np.tanh(risk_adj * 0.3)  # squash to (-1, 1)

    # Raw step return contribution (small direct incentive)
    ret_component = 100.0 * float(port_ret)    # e.g. 1 % → +0.01 * 100 = +1

    total = (
        ret_component
        + risk_adj_scaled
        - cvar_penalty
        - dd_penalty
        - turnover_penalty
        - concentration_penalty
    )

    components = {
        "port_ret":            float(port_ret),
        "ret_component":       float(ret_component),
        "sharpe_roll":         float(sharpe),
        "sortino_roll":        float(sortino),
        "risk_adj_scaled":     float(risk_adj_scaled),
        "cvar":                float(cvar),
        "cvar_penalty":        float(cvar_penalty),
        "drawdown":            float(drawdown),
        "dd_penalty":          float(dd_penalty),
        "turnover":            float(turnover),
        "turnover_penalty":    float(turnover_penalty),
        "concentration":       float(herfindahl),
        "concentration_pen":   float(concentration_penalty),
        "total":               float(total),
    }

    return float(total), components, state