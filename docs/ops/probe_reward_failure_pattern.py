"""WHY did these rewards fail, and WHEN? -- the nine candidates at exactly 199,932/400,000.

Drives each reward exactly as src/env/portfolio_env.py does, including the detail that matters:
``safe_call`` returns ``(SAFE_DEFAULT, {}, None)`` on failure and the env then assigns
``info["reward_state"] = reward_state`` -- SO A FAILURE WIPES THE ACCUMULATED STATE TO None.

HYPOTHESIS: that reset creates a LIMIT CYCLE. Fresh state succeeds; state grows to a size that
fails; the failure resets it; repeat. A program that fails at n=2 alternates and fails ~50% of calls,
with a count set by the CYCLE rather than by the data -- which would explain nine INDEPENDENT
programs sharing an exact total.

``safe_call`` SWALLOWS the exception, so this also calls each reward DIRECTLY in a try/except to
capture the real error -- otherwise we learn THAT it failed and never WHY.

Read-only, synthetic inputs, touches nothing the campaign uses.
"""
import json
import math
import os
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.abspath("."))
from src.orchestration.parallel import _FIXTURE  # noqa: E402 - the campaign's OWN fixture
from src.reward.contract import SAFE_DEFAULT  # noqa: E402
from src.sandbox.executor import (  # noqa: E402
    candidate_failed, reset_failure_flag, safe_call, validate_once,
)

ROOT = "outputs/campaign_cluster_run4"
# ⚠ READ FROM THE FIXTURE, NOT ASSUMED. weights carries 30 assets PLUS CASH (31,), returns is (30,).
N_W = _FIXTURE[0].shape[0]
N_R = _FIXTURE[1].shape[0]
N_STEPS = 400


def collect():
    out, seen = [], set()
    for dp, dn, fn in os.walk(ROOT):
        if "record.json" not in fn:
            continue
        rel = os.path.relpath(dp, ROOT).replace("\\", "/")
        if any(s.startswith((".pull_tmp", "_quarantine")) for s in rel.split("/")):
            continue
        try:
            r = json.load(open(os.path.join(dp, "record.json"), encoding="utf-8"))
        except Exception:
            continue
        if (r.get("metrics") or {}).get("train_safe_default_count") != 199932:
            continue
        h = r.get("reward_source_hash", "")
        if h in seen:
            continue
        seen.add(h)
        out.append((rel.split("/")[0], r.get("arm"), r.get("reward_source", "")))
    return out


def why(total):
    """Classify a RETURNED total against the contract the sandbox enforces."""
    try:
        f = float(total)
    except Exception:                                   # noqa: BLE001
        return "total not float-able"
    if not math.isfinite(f):
        return f"NON-FINITE total ({f})"
    if abs(f) > 1.0e6:
        return f"MAGNITUDE bound |{f:.3e}| > 1e6"
    return None


def drive(fn, n_steps=N_STEPS, seed=0):
    rng = np.random.default_rng(seed)
    pattern, reasons = [], Counter()
    state = None
    prev_w = np.full(N_W, 1.0 / N_W)
    reset_failure_flag()
    for _ in range(n_steps):
        w = rng.dirichlet(np.ones(N_W))
        r_t = rng.normal(0.0, 0.01, N_R)
        port_ret = float(np.dot(w[:N_R], r_t))
        info = {"reward_state": state, "weights": w, "prev_weights": prev_w}

        # (a) the REAL call the env makes -- gives the pass/fail bit and the threaded state
        _t, _c, new_state = safe_call(fn, w, r_t, prev_w, port_ret, dict(info))
        failed = candidate_failed()
        pattern.append(1 if failed else 0)

        # (b) the SAME inputs, called directly, purely to capture WHY when it failed
        if failed:
            try:
                out = fn(w, r_t, prev_w, port_ret, dict(info))
                try:
                    tot = out[0]
                except Exception:                       # noqa: BLE001
                    reasons["return not indexable"] += 1
                else:
                    reasons[why(tot) or "unknown (safe_call disagreed)"] += 1
            except Exception as exc:                    # noqa: BLE001
                reasons[f"RAISED {type(exc).__name__}: {str(exc)[:60]}"] += 1

        state = new_state          # env assigns verbatim, INCLUDING None on failure
        prev_w = w
    return pattern, reasons


def shape_of(pattern):
    fails = sum(pattern)
    if fails == 0:
        return "no failures", 0.0
    first = pattern.index(1)
    seg = pattern[first:]
    if all(seg):
        s = "CLIFF - fails from onset and never recovers"
    elif len(seg) > 4 and all(seg[i] != seg[i + 1] for i in range(len(seg) - 1)):
        s = "ALTERNATING 1-0-1-0 - a LIMIT CYCLE driven by the state reset"
    else:
        s = "INTERMITTENT - recovers and re-fails, not a clean 2-cycle"
    return f"first fail at call {first}; {s}", fails / len(pattern)


def main():
    cands = collect()
    print(f"distinct reward programs at exactly 199,932/400,000 : {len(cands)}")
    print(f"driving each for {N_STEPS} synthetic steps; SAFE_DEFAULT={SAFE_DEFAULT}\n")
    agg = Counter()
    for top, arm, src in cands:
        try:
            fn = validate_once(src, _FIXTURE)
        except Exception as exc:                        # noqa: BLE001
            print(f"{top[:26]:<27} {str(arm)[:16]:<17} validate_once REFUSED: {type(exc).__name__}: {str(exc)[:70]}")
            continue
        pattern, reasons = drive(fn)
        desc, rate = shape_of(pattern)
        print(f"{top[:26]:<27} {str(arm)[:16]:<17} {rate*100:7.3f}%  {desc}")
        print(f"{'':<27} {'':<17}          first 48: {''.join(map(str, pattern[:48]))}")
        for r, n in reasons.most_common(3):
            print(f"{'':<27} {'':<17}          WHY: {r}  (x{n})")
            agg[r] += n
        print()
    if agg:
        print("AGGREGATE failure reasons across all nine:")
        for r, n in agg.most_common():
            print(f"   {n:>6}  {r}")


if __name__ == "__main__":
    main()
