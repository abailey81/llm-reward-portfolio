def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── 1. Restore / initialise state ──────────────────────────────────────
    state = info.get("reward_state", None)
    if state is None:
        state = {
            "ret_history":    np.zeros(252, dtype=np.float64),   # circular buffer
            "buf_idx":        0,
            "buf_filled":     0,
            "peak_value":     1.0,
            "current_value":  1.0,
            "step":           0,
        }

    ret_history   = state["ret_history"]
    buf_idx       = state["buf_idx"]
    buf_filled    = state["buf_filled"]
    peak_value    = state["peak_value"]
    current_value = state["current_value"]
    step          = state["step"]

    r = float(port_ret)

    # ── 2. Update rolling return buffer ────────────────────────────────────
    ret_history[buf_idx] = r
    buf_idx    = (buf_idx + 1) % 252
    buf_filled = min(buf_filled + 1, 252)
    step      += 1

    # Valid history slice
    valid = ret_history if buf_filled == 252 else ret_history[:buf_filled]

    # ── 3. Rolling volatility (annualised) ─────────────────────────────────
    window_vol = 60
    if buf_filled >= window_vol:
        # last `window_vol` entries in circular buffer (order doesn't matter for std)
        if buf_filled == 252:
            idx_start = (buf_idx - window_vol) % 252
            if idx_start + window_vol <= 252:
                recent = ret_history[idx_start : idx_start + window_vol]
            else:
                recent = np.concatenate([
                    ret_history[idx_start:],
                    ret_history[:window_vol - (252 - idx_start)]
                ])
        else:
            recent = ret_history[max(0, buf_filled - window_vol): buf_filled]
        roll_vol = float(np.std(recent, ddof=1)) * np.sqrt(252)
    else:
        roll_vol = max(float(np.std(valid, ddof=1)) * np.sqrt(252) if buf_filled > 1 else 0.01, 0.01)

    roll_vol = max(roll_vol, 1e-6)

    # ── 4. Drawdown ─────────────────────────────────────────────────────────
    current_value = current_value * (1.0 + r)
    if current_value > peak_value:
        peak_value = current_value
    drawdown = (peak_value - current_value) / (peak_value + 1e-9)   # [0, ∞)

    # ── 5. CVaR / tail loss  (5% tail of rolling history) ──────────────────
    if buf_filled >= 20:
        alpha     = 0.05
        cutoff    = max(1, int(np.floor(alpha * buf_filled)))
        sorted_r  = np.sort(valid)          # ascending
        tail      = sorted_r[:cutoff]
        cvar_loss = -float(np.mean(tail))   # positive = bad
    else:
        cvar_loss = 0.0

    # ── 6. Turnover cost term ───────────────────────────────────────────────
    # turnover already baked into port_ret; penalise extra for concentration
    turnover = 0.5 * float(np.sum(np.abs(weights - prev_weights)))

    # ── 7. Concentration penalty (Herfindahl on risky weights) ─────────────
    risky_w    = weights[:30]
    herfindahl = float(np.sum(risky_w ** 2))   # 1/N for uniform, 1 for full concentration

    # ── 8. Rolling Sharpe (online, annualised) ──────────────────────────────
    if buf_filled >= 20:
        mean_r   = float(np.mean(valid))
        std_r    = float(np.std(valid, ddof=1)) if buf_filled > 1 else 1e-8
        std_r    = max(std_r, 1e-8)
        sharpe   = mean_r / std_r * np.sqrt(252)
    else:
        sharpe   = r / (roll_vol + 1e-8) * np.sqrt(252)

    # ── 9. Composite reward ─────────────────────────────────────────────────
    # Base: risk-adjusted step return (Sharpe-scaled incremental return)
    base_reward        = r / roll_vol                # annualises cancel; dimensionless

    # Drawdown penalty — exponential to punish deep drawdowns harder
    drawdown_penalty   = 2.0 * (np.exp(3.0 * drawdown) - 1.0)

    # CVaR penalty
    cvar_penalty       = 1.5 * cvar_loss

    # Turnover penalty (costs already in port_ret, add light extra signal)
    turnover_penalty   = 0.5 * turnover

    # Concentration penalty (mild, allow some concentration)
    conc_penalty       = 0.3 * max(herfindahl - 1.0 / 30.0, 0.0)

    # Rolling Sharpe bonus — reward sustained good risk-adjusted performance
    sharpe_bonus       = 0.05 * np.tanh(sharpe / 2.0)   # bounded in (-0.05, 0.05)

    total = (base_reward
             - drawdown_penalty
             - cvar_penalty
             - turnover_penalty
             - conc_penalty
             + sharpe_bonus)

    # ── 10. Save state ──────────────────────────────────────────────────────
    new_state = {
        "ret_history":   ret_history,
        "buf_idx":       buf_idx,
        "buf_filled":    buf_filled,
        "peak_value":    peak_value,
        "current_value": current_value,
        "step":          step,
    }

    components = {
        "port_ret":        r,
        "base_reward":     float(base_reward),
        "roll_vol":        float(roll_vol),
        "drawdown":        float(drawdown),
        "drawdown_pen":    float(drawdown_penalty),
        "cvar_loss":       float(cvar_loss),
        "cvar_pen":        float(cvar_penalty),
        "turnover":        float(turnover),
        "turnover_pen":    float(turnover_penalty),
        "herfindahl":      float(herfindahl),
        "conc_pen":        float(conc_penalty),
        "rolling_sharpe":  float(sharpe),
        "sharpe_bonus":    float(sharpe_bonus),
        "total":           float(total),
    }

    return float(total), components, new_state