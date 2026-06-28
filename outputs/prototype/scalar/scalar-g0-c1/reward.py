def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Restore / initialise state ──────────────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_window": [],        # rolling window of port_ret
            "peak":           0.0,       # running peak for drawdown
            "cumulative":     0.0,       # log-cumulative return
        }

    # ── Update rolling window (keep last 60 steps) ─────────────────────────
    WINDOW = 60
    state["returns_window"].append(float(port_ret))
    if len(state["returns_window"]) > WINDOW:
        state["returns_window"].pop(0)
    rw = np.array(state["returns_window"], dtype=np.float64)

    # ── Update cumulative return & drawdown peak ────────────────────────────
    state["cumulative"] += float(port_ret)
    if state["cumulative"] > state["peak"]:
        state["peak"] = state["cumulative"]
    drawdown = state["peak"] - state["cumulative"]   # >= 0

    # ── Rolling volatility ──────────────────────────────────────────────────
    if len(rw) >= 2:
        roll_vol = float(np.std(rw, ddof=1))
    else:
        roll_vol = 1e-6
    roll_vol = max(roll_vol, 1e-6)

    # ── Rolling Sharpe (annualised via sqrt(252)) ───────────────────────────
    roll_mean = float(np.mean(rw))
    roll_sharpe = roll_mean / roll_vol * np.sqrt(252)

    # ── CVaR (Expected Shortfall) at 5 % tail ──────────────────────────────
    if len(rw) >= 10:
        sorted_r = np.sort(rw)
        cutoff = max(1, int(np.floor(0.05 * len(rw))))
        cvar = float(np.mean(sorted_r[:cutoff]))   # negative = bad
    else:
        cvar = float(port_ret)

    # ── Turnover cost penalty ───────────────────────────────────────────────
    turnover = 0.5 * float(np.sum(np.abs(weights - prev_weights)))
    cost_penalty = 10.0 * turnover      # scale to same order as returns

    # ── Concentration penalty (Herfindahl) ─────────────────────────────────
    risky_weights = weights[:30]
    hhi = float(np.sum(risky_weights ** 2))
    concentration_penalty = hhi        # 0 = perfectly diversified, 1 = all-in

    # ── Drawdown penalty ────────────────────────────────────────────────────
    drawdown_penalty = 2.0 * drawdown

    # ── CVaR penalty (penalise negative tail) ──────────────────────────────
    cvar_penalty = -5.0 * min(cvar, 0.0)   # positive penalty when cvar < 0

    # ── Assemble total reward ───────────────────────────────────────────────
    # Core: risk-adjusted return (rolling Sharpe), scaled back to per-step
    sharpe_component   = roll_sharpe / 252.0      # de-annualise for per-step scale

    total = (
        sharpe_component          # reward risk-adjusted return
        - cost_penalty            # discourage excessive trading
        - concentration_penalty   # encourage diversification
        - drawdown_penalty        # penalise deep drawdowns
        - cvar_penalty            # penalise heavy left tail
    )

    components = {
        "port_ret":             float(port_ret),
        "sharpe_component":     float(sharpe_component),
        "roll_vol":             float(roll_vol),
        "roll_sharpe":          float(roll_sharpe),
        "cvar":                 float(cvar),
        "turnover":             float(turnover),
        "cost_penalty":         float(cost_penalty),
        "concentration_hhi":    float(hhi),
        "concentration_pen":    float(concentration_penalty),
        "drawdown":             float(drawdown),
        "drawdown_penalty":     float(drawdown_penalty),
        "cvar_penalty":         float(cvar_penalty),
    }

    return float(total), components, state