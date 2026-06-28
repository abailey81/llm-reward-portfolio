def reward(weights, returns, prev_weights, port_ret, info):
    # Retrieve or initialize state
    state = info.get("reward_state") or {}
    
    # EMA parameters
    alpha_fast = 0.05   # ~20-step window for mean/var
    alpha_slow = 0.02   # ~50-step window for tail tracking
    
    # --- Update rolling statistics ---
    mu_ema   = state.get("mu_ema",   port_ret)
    var_ema  = state.get("var_ema",  1e-4)
    tail_ema = state.get("tail_ema", port_ret)
    step     = state.get("step",     0) + 1
    
    # EMA mean and variance of portfolio returns
    mu_ema_new  = (1 - alpha_fast) * mu_ema  + alpha_fast * port_ret
    dev         = port_ret - mu_ema_new
    var_ema_new = (1 - alpha_fast) * var_ema + alpha_fast * dev**2
    std_ema     = np.sqrt(max(var_ema_new, 1e-8))
    
    # EMA of tail losses (track bad returns only)
    tail_threshold = mu_ema_new - std_ema
    tail_loss = min(port_ret - tail_threshold, 0.0)  # negative when return is in lower tail
    tail_ema_new = (1 - alpha_slow) * tail_ema + alpha_slow * tail_loss
    
    # --- Sharpe-like component ---
    sharpe_signal = mu_ema_new / std_ema
    
    # --- Tail risk penalty (CVaR-style) ---
    # tail_ema_new is <= 0; penalize negative tail
    tail_penalty = tail_ema_new  # already negative or zero
    
    # --- Concentration penalty (Herfindahl index) ---
    hhi = float(np.sum(weights**2))
    n = len(weights)
    hhi_min = 1.0 / n
    conc_penalty = -(hhi - hhi_min)  # negative when concentrated
    
    # --- Warm-up: scale down reward until we have enough history ---
    warmup_scale = min(1.0, step / 30.0)
    
    # --- Combine components ---
    w_sharpe = 1.0
    w_tail   = 0.5
    w_conc   = 0.1
    
    total = warmup_scale * (
        w_sharpe * sharpe_signal
        + w_tail  * tail_penalty
        + w_conc  * conc_penalty
    )
    
    components = {
        "sharpe_signal": float(sharpe_signal),
        "tail_penalty":  float(tail_penalty),
        "conc_penalty":  float(conc_penalty),
        "mu_ema":        float(mu_ema_new),
        "std_ema":       float(std_ema),
        "warmup_scale":  float(warmup_scale),
    }
    
    reward_state = {
        "mu_ema":   mu_ema_new,
        "var_ema":  var_ema_new,
        "tail_ema": tail_ema_new,
        "step":     step,
    }
    
    return float(total), components, reward_state