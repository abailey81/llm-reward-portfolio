def reward(weights, returns, prev_weights, port_ret, info):
    # ── Recover / initialise state ─────────────────────────────────────────
    state = info.get("reward_state") or {}

    # EMA parameters
    alpha_fast = 0.05   # ~20-step half-life  (short vol/mean estimate)
    alpha_slow = 0.01   # ~100-step half-life (longer trend)

    ema_r   = state.get("ema_r",   0.0)
    ema_r2  = state.get("ema_r2",  1e-6)
    ema_r_s = state.get("ema_r_s", 0.0)
    ema_r2_s= state.get("ema_r2_s",1e-6)

    peak    = state.get("peak",    1.0)
    nav     = state.get("nav",     1.0)
    step    = state.get("step",    0)

    # Running buffer for tail-risk (CVaR)
    buf_size = 60
    ret_buf  = list(state.get("ret_buf", []))

    # ── Update state ───────────────────────────────────────────────────────
    step += 1
    nav   = nav * (1.0 + port_ret)
    peak  = max(peak, nav)

    ret_buf.append(port_ret)
    if len(ret_buf) > buf_size:
        ret_buf = ret_buf[-buf_size:]

    # EMA updates (fast)
    ema_r  = (1 - alpha_fast) * ema_r  + alpha_fast * port_ret
    ema_r2 = (1 - alpha_fast) * ema_r2 + alpha_fast * port_ret ** 2
    # EMA updates (slow)
    ema_r_s  = (1 - alpha_slow) * ema_r_s  + alpha_slow * port_ret
    ema_r2_s = (1 - alpha_slow) * ema_r2_s + alpha_slow * port_ret ** 2

    # ── Component 1: Online Sharpe (fast EMA) ──────────────────────────────
    var_fast = max(ema_r2 - ema_r ** 2, 1e-8)
    sharpe_fast = ema_r / np.sqrt(var_fast)

    # ── Component 2: Online Sharpe (slow EMA) ──────────────────────────────
    var_slow = max(ema_r2_s - ema_r_s ** 2, 1e-8)
    sharpe_slow = ema_r_s / np.sqrt(var_slow)

    # ── Component 3: Drawdown penalty ──────────────────────────────────────
    drawdown = (nav - peak) / (peak + 1e-8)   # <= 0
    dd_penalty = min(drawdown, 0.0)            # only penalise drawdowns

    # ── Component 4: CVaR tail penalty (5th percentile of recent returns) ──
    cvar_penalty = 0.0
    if len(ret_buf) >= 10:
        arr = np.array(ret_buf)
        cutoff = np.percentile(arr, 5)
        tail   = arr[arr <= cutoff]
        cvar_penalty = float(np.mean(tail)) if len(tail) > 0 else 0.0

    # ── Component 5: Concentration penalty (Herfindahl on risky weights) ──
    risky = weights[:-1]  # exclude cash (last element assumed cash)
    hhi   = float(np.sum(risky ** 2))
    conc_penalty = -hhi * 0.05   # mild nudge toward diversification

    # ── Blend ──────────────────────────────────────────────────────────────
    # Warm-up: down-weight Sharpe estimate until we have enough history
    warmup = min(1.0, step / 30.0)

    total = (
        0.40 * sharpe_fast * warmup
        + 0.20 * sharpe_slow * warmup
        + 0.20 * port_ret * 50.0          # direct return signal (scaled)
        + 0.10 * dd_penalty * 10.0        # drawdown
        + 0.05 * cvar_penalty * 10.0      # tail
        + 0.05 * conc_penalty
    )

    components = {
        "sharpe_fast":  float(sharpe_fast),
        "sharpe_slow":  float(sharpe_slow),
        "port_ret":     float(port_ret),
        "dd_penalty":   float(dd_penalty),
        "cvar_penalty": float(cvar_penalty),
        "conc_penalty": float(conc_penalty),
        "nav":          float(nav),
        "drawdown":     float(drawdown),
    }

    reward_state = {
        "ema_r":    ema_r,
        "ema_r2":   ema_r2,
        "ema_r_s":  ema_r_s,
        "ema_r2_s": ema_r2_s,
        "peak":     peak,
        "nav":      nav,
        "step":     step,
        "ret_buf":  ret_buf,
    }

    return float(total), components, reward_state