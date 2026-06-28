def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── 1. Restore / initialise state ────────────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_window": [],      # rolling window of port_ret values
            "peak":           0.0,     # running peak for drawdown
            "cum_ret":        0.0,     # log-cumulative return proxy
            "ema_ret":        None,    # EMA of returns  (for Sharpe)
            "ema_sq":         None,    # EMA of squared returns (for Sharpe)
            "step":           0,
        }

    WINDOW      = 60          # rolling window length
    EMA_ALPHA   = 2 / (WINDOW + 1)   # ≈ 0.032
    DD_PENALTY  = 3.0         # drawdown aversion
    CVAR_ALPHA  = 0.05        # tail proportion (worst 5 %)
    CVAR_WEIGHT = 2.0         # CVaR penalty weight
    TURNOVER_W  = 1.0         # extra turnover penalty on top of env cost
    CONC_WEIGHT = 0.5         # concentration (HHI) penalty

    r = float(port_ret)
    step = state["step"] + 1

    # ── 2. Rolling returns window ─────────────────────────────────────────────
    window: list = state["returns_window"]
    window.append(r)
    if len(window) > WINDOW:
        window.pop(0)
    arr = np.array(window, dtype=np.float64)

    # ── 3. Online EMA mean & variance (for Sharpe) ───────────────────────────
    ema_ret = state["ema_ret"]
    ema_sq  = state["ema_sq"]
    if ema_ret is None:
        ema_ret = r
        ema_sq  = r * r
    else:
        ema_ret = EMA_ALPHA * r + (1 - EMA_ALPHA) * ema_ret
        ema_sq  = EMA_ALPHA * r * r + (1 - EMA_ALPHA) * ema_sq

    ema_var = max(ema_sq - ema_ret ** 2, 1e-10)
    ema_std = np.sqrt(ema_var)

    # Annualised-ish Sharpe (daily, no annualisation factor to keep scale stable)
    sharpe_step = ema_ret / ema_std

    # ── 4. Drawdown penalty ──────────────────────────────────────────────────
    cum_ret = state["cum_ret"] + r          # simple cumulative sum (approx)
    peak    = max(state["peak"], cum_ret)
    drawdown = peak - cum_ret               # ≥ 0

    # ── 5. CVaR (tail loss) from rolling window ───────────────────────────────
    if len(arr) >= max(int(1 / CVAR_ALPHA), 5):
        k = max(1, int(np.floor(CVAR_ALPHA * len(arr))))
        tail = np.sort(arr)[:k]             # k worst returns
        cvar = -float(np.mean(tail))        # positive = bad
    else:
        cvar = max(-r, 0.0)                 # fallback: current loss

    # ── 6. Turnover penalty (agent-side, complements env cost) ───────────────
    turnover = 0.5 * float(np.sum(np.abs(weights - prev_weights)))

    # ── 7. Concentration penalty (Herfindahl on risky assets) ────────────────
    risky_w = weights[:30]
    hhi = float(np.sum(risky_w ** 2))      # 1/N … 1

    # ── 8. Assemble reward ───────────────────────────────────────────────────
    # Base: risk-adjusted return via EMA Sharpe
    base          =  sharpe_step
    dd_pen        = -DD_PENALTY    * drawdown
    cvar_pen      = -CVAR_WEIGHT   * cvar
    turnover_pen  = -TURNOVER_W    * turnover
    conc_pen      = -CONC_WEIGHT   * hhi

    total = float(base + dd_pen + cvar_pen + turnover_pen + conc_pen)

    components = {
        "sharpe_step":   float(sharpe_step),
        "ema_ret":       float(ema_ret),
        "ema_std":       float(ema_std),
        "drawdown":      float(drawdown),
        "cvar":          float(cvar),
        "turnover":      float(turnover),
        "hhi":           float(hhi),
        "port_ret":      r,
        "dd_pen":        float(dd_pen),
        "cvar_pen":      float(cvar_pen),
        "turnover_pen":  float(turnover_pen),
        "conc_pen":      float(conc_pen),
    }

    # ── 9. Update state ───────────────────────────────────────────────────────
    state["returns_window"] = window
    state["peak"]           = peak
    state["cum_ret"]        = cum_ret
    state["ema_ret"]        = ema_ret
    state["ema_sq"]         = ema_sq
    state["step"]           = step

    return total, components, state