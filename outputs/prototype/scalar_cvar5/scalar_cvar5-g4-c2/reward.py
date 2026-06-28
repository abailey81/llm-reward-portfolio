def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Retrieve or initialise reward state ──────────────────────────────────
    state = info.get("reward_state") or {}

    # Online mean / variance of portfolio returns (Welford's algorithm)
    n        = state.get("n", 0)
    mean_ret = state.get("mean_ret", 0.0)
    M2       = state.get("M2", 0.0)          # sum of squared deviations
    peak     = state.get("peak", 1.0)        # for drawdown tracking
    equity   = state.get("equity", 1.0)
    ret_buf  = list(state.get("ret_buf", []))  # rolling window for CVaR

    WINDOW   = 100   # rolling window length for tail-risk estimate
    MIN_N    = 10    # minimum samples before Sharpe term is trusted
    DAILY_RF = 0.0   # risk-free rate per step

    # ── Update equity & peak ──────────────────────────────────────────────────
    equity   = equity * (1.0 + port_ret)
    peak     = max(peak, equity)
    drawdown = (peak - equity) / (peak + 1e-8)   # in [0, 1)

    # ── Welford online update ─────────────────────────────────────────────────
    n       += 1
    delta    = port_ret - mean_ret
    mean_ret = mean_ret + delta / n
    delta2   = port_ret - mean_ret
    M2       = M2 + delta * delta2

    variance = M2 / n if n > 1 else 1e-6
    std_ret  = np.sqrt(max(variance, 1e-8))

    # ── Rolling buffer for CVaR ───────────────────────────────────────────────
    ret_buf.append(port_ret)
    if len(ret_buf) > WINDOW:
        ret_buf.pop(0)

    # CVaR (expected shortfall at 5% tail)
    if len(ret_buf) >= MIN_N:
        arr       = np.array(ret_buf, dtype=np.float64)
        cutoff    = np.percentile(arr, 5)
        tail      = arr[arr <= cutoff]
        cvar      = float(np.mean(tail)) if len(tail) > 0 else cutoff
    else:
        cvar      = 0.0

    # ── Turnover penalty ─────────────────────────────────────────────────────
    turnover = float(np.sum(np.abs(weights - prev_weights)))

    # ── Concentration penalty (encourage diversification) ────────────────────
    # Herfindahl index on risky weights (exclude cash = last element assumed)
    risky_w      = weights[:-1] if len(weights) > 1 else weights
    herfindahl   = float(np.sum(risky_w ** 2))   # 0 = perfect spread, 1 = concentrated

    # ── Sharpe-style online component ────────────────────────────────────────
    excess_ret  = mean_ret - DAILY_RF
    if n >= MIN_N:
        sharpe_online = excess_ret / std_ret
    else:
        sharpe_online = 0.0

    # ── Step-level return signal (to get early gradient signal) ──────────────
    step_signal = port_ret - DAILY_RF

    # ── Assemble total reward ─────────────────────────────────────────────────
    # Weights tuned to balance signal strength
    w_step      =  1.0    # immediate return
    w_sharpe    =  0.5    # online Sharpe encouragement
    w_cvar      =  2.0    # tail-risk penalty (cvar is negative for losses)
    w_drawdown  =  1.0    # drawdown penalty
    w_turnover  =  0.1    # transaction-cost proxy
    w_hhi       =  0.2    # concentration penalty

    total = (
        w_step    * step_signal
      + w_sharpe  * sharpe_online
      - w_cvar    * abs(min(cvar, 0.0))      # penalise bad tail
      - w_drawdown * drawdown
      - w_turnover * turnover
      - w_hhi     * herfindahl
    )

    components = {
        "step_signal":    step_signal,
        "sharpe_online":  sharpe_online,
        "cvar_penalty":  -abs(min(cvar, 0.0)),
        "drawdown":      -drawdown,
        "turnover":      -turnover,
        "herfindahl":    -herfindahl,
    }

    reward_state = {
        "n":        n,
        "mean_ret": mean_ret,
        "M2":       M2,
        "peak":     peak,
        "equity":   equity,
        "ret_buf":  ret_buf,
    }

    return float(total), components, reward_state