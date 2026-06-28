def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Recover or initialise rolling state ──────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_window": [],          # rolling window of port_ret values
            "peak":           0.0,         # running peak for drawdown
            "cum_ret":        0.0,         # log-cumulative return proxy
        }

    returns_window: list = state["returns_window"]
    peak:           float = state["peak"]
    cum_ret:        float = state["cum_ret"]

    # ── Update rolling window (keep last 60 steps) ───────────────────────────
    WINDOW = 60
    returns_window.append(float(port_ret))
    if len(returns_window) > WINDOW:
        returns_window.pop(0)

    arr = np.array(returns_window, dtype=np.float64)
    n   = len(arr)

    # ── 1. Rolling Sharpe (annualised) ───────────────────────────────────────
    if n >= 2:
        mu_r  = np.mean(arr)
        sig_r = np.std(arr, ddof=1) + 1e-8
        sharpe = (mu_r / sig_r) * np.sqrt(252)          # daily → annual scale
    else:
        sharpe = 0.0

    # ── 2. Drawdown penalty ──────────────────────────────────────────────────
    cum_ret += float(port_ret)                           # additive log-ret approx
    if cum_ret > peak:
        peak = cum_ret
    drawdown = peak - cum_ret                            # >= 0
    drawdown_penalty = -drawdown                         # penalise proportionally

    # ── 3. CVaR / tail-loss penalty (5 % tail of rolling window) ────────────
    if n >= 10:
        tail_cutoff = max(1, int(np.floor(0.05 * n)))
        sorted_rets = np.sort(arr)
        cvar_5 = np.mean(sorted_rets[:tail_cutoff])     # expected shortfall
    else:
        cvar_5 = np.minimum(float(port_ret), 0.0)
    tail_penalty = -np.maximum(-cvar_5, 0.0)            # penalise only negative ES

    # ── 4. Concentration penalty (Herfindahl on risky weights) ───────────────
    risky_w = weights[:30]
    hhi     = float(np.sum(risky_w ** 2))               # 1/30 ≤ HHI ≤ 1
    # penalise heavy concentration; mild signal
    concentration_penalty = -(hhi - 1.0 / 30.0)

    # ── 5. Turnover penalty (extra signal on top of env cost) ────────────────
    turnover = 0.5 * float(np.sum(np.abs(weights - prev_weights)))
    turnover_penalty = -turnover * 0.5   # 50 bps effective multiplier

    # ── 6. Combine ────────────────────────────────────────────────────────────
    # Primary signal: rolling Sharpe (already risk-adjusted mean/vol)
    # Secondary:      tail, drawdown, concentration, turnover
    w_sharpe        = 0.40
    w_port_ret      = 0.20
    w_tail          = 0.20
    w_drawdown      = 0.10
    w_concentration = 0.05
    w_turnover      = 0.05

    total = (
        w_sharpe        * sharpe
        + w_port_ret    * float(port_ret) * 252         # annualised level
        + w_tail        * tail_penalty    * 252
        + w_drawdown    * drawdown_penalty
        + w_concentration * concentration_penalty
        + w_turnover    * turnover_penalty
    )

    components = {
        "sharpe":               float(sharpe),
        "port_ret_ann":         float(port_ret) * 252,
        "tail_penalty":         float(tail_penalty) * 252,
        "drawdown_penalty":     float(drawdown_penalty),
        "concentration_penalty":float(concentration_penalty),
        "turnover_penalty":     float(turnover_penalty),
        "total":                float(total),
    }

    new_state = {
        "returns_window": returns_window,
        "peak":           peak,
        "cum_ret":        cum_ret,
    }

    return float(total), components, new_state