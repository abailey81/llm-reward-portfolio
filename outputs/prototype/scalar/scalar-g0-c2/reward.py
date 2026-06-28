def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── 1. Restore / initialise state ────────────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_window": [],        # recent portfolio returns (up to 252)
            "peak":           1.0,       # for drawdown tracking
            "equity":         1.0,       # cumulative equity
            "step":           0,
        }

    returns_window: list = state["returns_window"]
    peak:   float = state["peak"]
    equity: float = state["equity"]
    step:   int   = state["step"]

    # ── 2. Update equity curve & drawdown ────────────────────────────────────
    equity = equity * (1.0 + port_ret)
    peak   = max(peak, equity)
    drawdown = (peak - equity) / (peak + 1e-8)          # ∈ [0, ∞)

    # ── 3. Maintain a rolling window of recent returns ────────────────────────
    WINDOW = 252
    returns_window.append(float(port_ret))
    if len(returns_window) > WINDOW:
        returns_window = returns_window[-WINDOW:]

    ret_arr = np.array(returns_window, dtype=np.float64)

    # ── 4. Rolling Sharpe (annualised) ───────────────────────────────────────
    MIN_OBS = 20
    if len(ret_arr) >= MIN_OBS:
        mu_r  = float(np.mean(ret_arr))
        sig_r = float(np.std(ret_arr, ddof=1)) + 1e-8
        # daily Sharpe, scale by sqrt(252) for annualisation
        rolling_sharpe = (mu_r / sig_r) * np.sqrt(252)
    else:
        # not enough data yet — use raw return scaled modestly
        rolling_sharpe = float(port_ret) * 10.0

    # ── 5. CVaR / tail-loss penalty (5 % tail) ───────────────────────────────
    CVAR_ALPHA = 0.05
    if len(ret_arr) >= MIN_OBS:
        q = float(np.quantile(ret_arr, CVAR_ALPHA))
        tail_returns = ret_arr[ret_arr <= q]
        cvar = float(np.mean(tail_returns)) if len(tail_returns) > 0 else q
        # cvar is negative (loss); penalty is positive when losses are large
        cvar_penalty = max(0.0, -cvar) * np.sqrt(252)
    else:
        cvar_penalty = max(0.0, -float(port_ret)) * np.sqrt(252)

    # ── 6. Turnover penalty ───────────────────────────────────────────────────
    # transaction cost already baked into port_ret, but we add a soft penalty
    # to discourage excessive churn beyond the 10 bps hard cost
    turnover = float(np.sum(np.abs(weights - prev_weights))) * 0.5
    turnover_penalty = turnover * 0.5   # additional soft penalty weight

    # ── 7. Drawdown penalty ───────────────────────────────────────────────────
    # quadratic penalty on drawdown to strongly discourage deep drawdowns
    dd_penalty = drawdown ** 2 * 10.0

    # ── 8. Concentration penalty (encourage diversification) ─────────────────
    # soft Herfindahl–Hirschman index on risky weights
    risky_w = weights[:30]
    hhi = float(np.sum(risky_w ** 2))          # 1/30 (uniform) → 1 (concentrated)
    conc_penalty = hhi * 0.5

    # ── 9. Combine into total reward ─────────────────────────────────────────
    # Core signal: rolling Sharpe
    # Minus: CVaR penalty, drawdown penalty, turnover penalty, concentration penalty
    total = (
        rolling_sharpe
        - 1.5 * cvar_penalty
        - dd_penalty
        - turnover_penalty
        - conc_penalty
    )

    components = {
        "port_ret":        float(port_ret),
        "rolling_sharpe":  float(rolling_sharpe),
        "cvar_penalty":    float(cvar_penalty),
        "drawdown":        float(drawdown),
        "dd_penalty":      float(dd_penalty),
        "turnover":        float(turnover),
        "turnover_penalty":float(turnover_penalty),
        "conc_penalty":    float(conc_penalty),
        "total":           float(total),
    }

    # ── 10. Save updated state ────────────────────────────────────────────────
    new_state = {
        "returns_window": returns_window,
        "peak":           float(peak),
        "equity":         float(equity),
        "step":           step + 1,
    }

    return float(total), components, new_state