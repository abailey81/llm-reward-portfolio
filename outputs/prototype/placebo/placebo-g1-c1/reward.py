def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Restore / initialise state ──────────────────────────────────────────
    state = info.get("reward_state") or {}
    
    # Rolling window of portfolio returns (for Sharpe estimation)
    hist = list(state.get("hist", []))
    peak = float(state.get("peak", 1.0))
    nav  = float(state.get("nav",  1.0))
    step = int(state.get("step", 0))

    # ── Update NAV and drawdown tracking ───────────────────────────────────
    nav  = nav * (1.0 + port_ret)
    peak = max(peak, nav)
    drawdown = (nav - peak) / (peak + 1e-8)   # <= 0

    # ── Rolling history (window = 60 steps) ────────────────────────────────
    WINDOW = 60
    hist.append(float(port_ret))
    if len(hist) > WINDOW:
        hist = hist[-WINDOW:]

    step += 1

    # ── Component 1: Incremental Sharpe signal ─────────────────────────────
    if len(hist) >= 5:
        arr  = np.array(hist)
        mu   = arr.mean()
        sigma = arr.std() + 1e-8
        sharpe_signal = mu / sigma          # rolling Sharpe (un-annualised)
    else:
        sharpe_signal = port_ret / (abs(port_ret) + 1e-8) * 0.01

    # ── Component 2: Step return (dampened to avoid scale dominance) ────────
    step_ret = np.tanh(port_ret * 20.0)     # maps returns to (-1, 1)

    # ── Component 3: Drawdown penalty (convex) ─────────────────────────────
    dd_penalty = 5.0 * (drawdown ** 2)      # always >= 0, penalise via subtraction

    # ── Component 4: Tail-risk (downside deviation) penalty ───────────────
    if len(hist) >= 5:
        arr = np.array(hist)
        downside = arr[arr < 0.0]
        cvar = float(downside.mean()) if len(downside) > 0 else 0.0
        tail_penalty = -2.0 * cvar          # cvar <= 0, so -2*cvar >= 0 as penalty
    else:
        tail_penalty = 0.0

    # ── Component 5: Turnover cost signal ──────────────────────────────────
    turnover = float(np.sum(np.abs(weights - prev_weights)))
    # mild penalty — don't over-penalise or agent goes to cash
    turnover_penalty = 0.1 * turnover

    # ── Combine ────────────────────────────────────────────────────────────
    # Primary driver: rolling Sharpe (encourages sustained risk-adjusted return)
    # Secondary: step return nudge
    # Penalise: drawdown, tail losses, excess turnover
    total = (
        0.5  * sharpe_signal
        + 0.3  * step_ret
        - dd_penalty
        - tail_penalty
        - turnover_penalty
    )

    components = {
        "sharpe_signal":   sharpe_signal,
        "step_ret":        step_ret,
        "dd_penalty":      -dd_penalty,
        "tail_penalty":    -tail_penalty,
        "turnover_penalty":-turnover_penalty,
    }

    reward_state = {
        "hist": hist,
        "peak": peak,
        "nav":  nav,
        "step": step,
    }

    return float(total), components, reward_state