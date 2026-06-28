def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Restore / initialise state ──────────────────────────────────────────
    state = info.get("reward_state") or {}

    # EMA parameters
    alpha_fast = 0.05   # ~20-step half-life  (mean/var tracking)
    alpha_slow = 0.02   # ~50-step half-life  (drawdown tracking)

    ema_ret   = state.get("ema_ret",   0.0)
    ema_sq    = state.get("ema_sq",    1e-6)
    peak_val  = state.get("peak_val",  1.0)
    port_val  = state.get("port_val",  1.0)
    step      = state.get("step",      0)

    # Recent returns window for tail estimation (ring buffer)
    win_size  = 60
    ret_buf   = list(state.get("ret_buf", []))

    # ── Update statistics ───────────────────────────────────────────────────
    step += 1
    port_val  = port_val * (1.0 + port_ret)
    peak_val  = max(peak_val, port_val)

    ema_ret   = (1 - alpha_fast) * ema_ret  + alpha_fast * port_ret
    ema_sq    = (1 - alpha_fast) * ema_sq   + alpha_fast * port_ret ** 2
    ema_var   = max(ema_sq - ema_ret ** 2, 1e-8)
    ema_std   = np.sqrt(ema_var)

    ret_buf.append(port_ret)
    if len(ret_buf) > win_size:
        ret_buf.pop(0)

    # ── Component 1: online Sharpe signal ──────────────────────────────────
    # Annualise loosely (252 steps/yr assumed); kept moderate scale
    sharpe_signal = ema_ret / ema_std          # dimensionless

    # ── Component 2: drawdown penalty ──────────────────────────────────────
    drawdown      = (peak_val - port_val) / peak_val   # in [0,1]
    dd_penalty    = -2.0 * drawdown ** 2               # quadratic, hurts bad DDs

    # ── Component 3: tail / CVaR penalty ───────────────────────────────────
    if len(ret_buf) >= 10:
        buf_arr   = np.array(ret_buf)
        pct5      = np.percentile(buf_arr, 5)
        tail_mask = buf_arr[buf_arr <= pct5]
        cvar5     = float(np.mean(tail_mask)) if len(tail_mask) > 0 else 0.0
        tail_pen  = 3.0 * cvar5               # cvar5 ≤ 0, so this is negative
    else:
        tail_pen  = 0.0
        cvar5     = 0.0

    # ── Component 4: turnover penalty ──────────────────────────────────────
    turnover      = float(np.sum(np.abs(weights - prev_weights)))
    to_penalty    = -0.5 * turnover

    # ── Component 5: direct return (small weight to stay responsive) ────────
    direct_ret    = 10.0 * port_ret            # scale to similar magnitude

    # ── Combine ─────────────────────────────────────────────────────────────
    # Warm-up: suppress noisy early steps
    warmup        = min(1.0, step / 30.0)

    total = warmup * (
        0.4 * sharpe_signal
        + 0.3 * direct_ret
        + 0.15 * dd_penalty
        + 0.10 * tail_pen
        + 0.05 * to_penalty
    )

    components = {
        "sharpe_signal": sharpe_signal,
        "direct_ret":    direct_ret,
        "dd_penalty":    dd_penalty,
        "tail_pen":      tail_pen,
        "to_penalty":    to_penalty,
        "drawdown":      drawdown,
        "cvar5":         cvar5,
        "ema_ret":       ema_ret,
        "ema_std":       ema_std,
    }

    reward_state = {
        "ema_ret":  ema_ret,
        "ema_sq":   ema_sq,
        "peak_val": peak_val,
        "port_val": port_val,
        "step":     step,
        "ret_buf":  ret_buf,
    }

    return float(total), components, reward_state