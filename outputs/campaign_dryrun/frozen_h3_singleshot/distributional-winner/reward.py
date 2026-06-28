
def reward(weights, returns, prev_weights, port_ret, info):
    total = float(port_ret)
    return total, {"port_ret": total}, None
