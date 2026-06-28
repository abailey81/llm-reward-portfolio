def reward(weights, returns, prev_weights, port_ret, info):
    state = info.get('reward_state')
    prev = np.asarray(state, dtype=float) if state is not None else np.zeros(0, dtype=float)
    history = np.append(prev, float(port_ret))
    window = 50
    if history.size > window:
        history = history[-window:]
    var = float(np.var(history)) if history.size >= 2 else 0.0
    thresh = float(np.quantile(history, 0.05))
    tail = history[history <= thresh]
    cvar = -float(np.mean(tail)) if tail.size > 0 else 0.0
    cvar = cvar if cvar > 0.0 else 0.0
    total = 0.5 * float(port_ret) - 0.25 * var - 0.25 * cvar
    components = {
        'return': float(port_ret),
        'variance': var,
        'cvar': cvar,
    }
    return float(total), components, history
