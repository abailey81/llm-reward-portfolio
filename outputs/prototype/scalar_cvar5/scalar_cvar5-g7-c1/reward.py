def reward(weights, returns, prev_weights, port_ret, info):
    import numpy as np

    # ── Retrieve or initialise persistent state ──────────────────────────────
    state = info.get("reward_state") or {}
    ret_history   = state.get("ret_history",   [])
    peak          = state.get("peak",           1.0)
    cum_value     = state.get("cum_value",      1.0)
    loss_history  = state.get("loss_history",   [])   # stores negative returns for CVaR

    # ── Update running state ─────────────────────────────────────────────────
    ret_history.append(float(port_ret))
    cum_value = cum_value * (1.0 + float(port_ret))
    peak      = max(peak, cum_value)

    # Track losses for tail-risk estimation
    loss_history.append(float(port_ret))
    # Keep a rolling window for stability
    window = 120
    if len(ret_history) > window:
        ret_history  = ret_history[-window:]
        loss_history = loss_history[-window:]

    # ── Components ───────────────────────────────────────────────────────────
    n = len(ret_history)

    # 1. Online Sharpe (annualised proxy)
    if n >= 5:
        arr  = np.array(ret_history)
        mu   = arr.mean()
        sig  = arr.std(ddof=1) + 1e-8
        sharpe = mu / sig  # per-step Sharpe (scaling constant doesn't change optimisation)
    else:
        sharpe = 0.0

    # 2. CVaR penalty (5% tail, i.e. worst ~5% of returns)
    if n >= 20:
        arr = np.array(loss_history)
        cutoff = int(np.floor(0.05 * n))
        cutoff = max(1, cutoff)
        worst  = np.sort(arr)[:cutoff]
        cvar   = worst.mean()            # negative number → penalty when bad
    else:
        cvar = 0.0

    # 3. Drawdown penalty
    drawdown = (cum_value - peak) / (peak + 1e-8)   # ≤ 0

    # 4. Turnover penalty (transaction costs proxy)
    turnover = float(np.sum(np.abs(weights - prev_weights)))

    # 5. Concentration penalty (encourage diversification, penalise extreme bets)
    # Herfindahl index on risky assets (exclude last element = cash if any)
    w_risky = weights[:-1] if len(weights) > 1 else weights
    herfindahl = float(np.sum(w_risky ** 2))   # 1/N baseline; higher = more concentrated

    # ── Combine ──────────────────────────────────────────────────────────────
    # Weights tuned to balance Sharpe improvement vs tail/drawdown control
    w_sharpe   =  1.00
    w_cvar     =  3.00   # heavy penalty on tail losses
    w_dd       =  1.50   # drawdown matters
    w_turn     =  0.10   # mild turnover friction
    w_conc     =  0.20   # mild diversification pressure

    total = (
        w_sharpe  * sharpe
      + w_cvar    * cvar       # cvar is negative → subtracts when tail is bad
      - w_dd      * abs(drawdown)
      - w_turn    * turnover
      - w_conc    * herfindahl
    )

    components = {
        "sharpe":      sharpe,
        "cvar_penalty": w_cvar * cvar,
        "dd_penalty":  -w_dd * abs(drawdown),
        "turnover":    -w_turn * turnover,
        "herfindahl":  -w_conc * herfindahl,
    }

    reward_state = {
        "ret_history":  ret_history,
        "loss_history": loss_history,
        "peak":         peak,
        "cum_value":    cum_value,
    }

    return float(total), components, reward_state