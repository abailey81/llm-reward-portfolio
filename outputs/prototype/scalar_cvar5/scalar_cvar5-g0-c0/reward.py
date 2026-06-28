def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Recover / initialise reward state ──────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "returns_window": [],      # rolling window of port_ret values
            "peak": 0.0,               # running peak for drawdown
            "cum_ret": 0.0,            # cumulative log-ish return
            "step": 0,
        }

    state["step"] += 1
    win_size = 60  # rolling window length

    # ── Update rolling window of returns ───────────────────────────────────
    rw = state["returns_window"]
    rw.append(float(port_ret))
    if len(rw) > win_size:
        rw.pop(0)
    arr = np.array(rw, dtype=np.float64)

    # ── Update cumulative return & peak ────────────────────────────────────
    state["cum_ret"] += float(port_ret)
    if state["cum_ret"] > state["peak"]:
        state["peak"] = state["cum_ret"]

    # ── 1. Rolling Sharpe (annualised, regularised) ─────────────────────────
    if len(arr) >= 5:
        mu  = np.mean(arr)
        sig = np.std(arr, ddof=1) + 1e-8
        sharpe = (mu / sig) * np.sqrt(252)
    else:
        sharpe = 0.0

    # ── 2. Drawdown penalty ────────────────────────────────────────────────
    drawdown = state["peak"] - state["cum_ret"]          # >= 0
    drawdown_penalty = -drawdown                          # negative contribution

    # ── 3. CVaR / tail-loss penalty (5 % tail) ─────────────────────────────
    if len(arr) >= 10:
        tail_cut = max(1, int(np.floor(0.05 * len(arr))))
        sorted_ret = np.sort(arr)
        cvar = np.mean(sorted_ret[:tail_cut])            # mean of worst 5 %
        tail_penalty = cvar                              # already negative on bad days
    else:
        tail_penalty = 0.0

    # ── 4. Turnover cost signal (explicit penalty in addition to port_ret) ──
    # port_ret already deducts costs, but we add a small extra signal to
    # discourage excessive churning.
    turnover = 0.5 * np.sum(np.abs(weights - prev_weights))
    turnover_penalty = -0.001 * turnover                 # light extra push

    # ── 5. Concentration penalty (encourage diversification) ───────────────
    risky_w = weights[:30]
    # Herfindahl index normalised to [0,1]; 1/30 is perfectly diversified
    herfindahl = np.sum(risky_w ** 2)
    min_herf = 1.0 / 30.0
    concentration_penalty = -0.5 * max(herfindahl - min_herf, 0.0)

    # ── 6. Combine ──────────────────────────────────────────────────────────
    # Weights chosen so Sharpe dominates, with softer auxiliary penalties.
    w_sharpe      = 0.60
    w_drawdown    = 0.15
    w_tail        = 0.15
    w_turnover    = 0.05
    w_conc        = 0.05

    total = (
        w_sharpe   * sharpe
        + w_drawdown * drawdown_penalty
        + w_tail     * tail_penalty
        + w_turnover * turnover_penalty
        + w_conc     * concentration_penalty
    )

    components = {
        "sharpe":               float(sharpe),
        "drawdown_penalty":     float(w_drawdown * drawdown_penalty),
        "tail_penalty":         float(w_tail * tail_penalty),
        "turnover_penalty":     float(w_turnover * turnover_penalty),
        "concentration_penalty":float(w_conc * concentration_penalty),
        "port_ret":             float(port_ret),
        "drawdown":             float(drawdown),
        "herfindahl":           float(herfindahl),
    }

    return float(total), components, state