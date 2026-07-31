"""INDEPENDENT verification of the science invariants `sci=OK` asserts.

s.66 independently re-derived ONE of them (construct validity / tail leaks). This does the rest,
WITHOUT importing or invoking science_watch.py / results_audit.py -- two independent routes agreeing
is evidence; re-running the same tool is an echo.

It also adds an invariant the monitor does NOT appear to check, and which guards the dissertation's
core instrument:

  *** CVaR MONOTONICITY ***  CVaR at level a is the mean of the worst a-fraction of returns, so
  necessarily  cvar_01 <= cvar_05 <= cvar_10 <= cvar_25.  This is a MATHEMATICAL identity of the
  estimator, not a modelling assumption. If it is ever violated, the tail measurement -- the fed
  vector that IS the manipulated variable of H2 -- is broken. A violation would invalidate the
  experiment in a way no downstream check would catch.

Every check states its own denominator and prints offenders.
"""
import glob
import hashlib
import json
import math
import os
from collections import defaultdict

ROOT = "outputs/campaign_cluster_run4"
LLM_ARMS = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")
STEPS = 400_000
SEED_MAX = 567          # registered ladder tops out at 568 seeds -> ids 0..567

fail = defaultdict(list)
n = 0
n_hash = n_tail = n_popart = n_fit = n_steps = n_seed = 0
by_hash_arm = defaultdict(set)
by_hash_path = {}

for rec_path in glob.glob(os.path.join(ROOT, "**", "record.json"), recursive=True):
    norm = rec_path.replace("\\", "/")
    if "/.pull_tmp" in norm or "/frozen" in norm:
        continue
    try:
        rec = json.load(open(rec_path, encoding="utf-8"))
    except Exception as exc:
        fail["unreadable record"].append(f"{norm}: {exc}")
        continue
    n += 1
    arm = rec.get("arm")
    m = rec.get("metrics") or {}

    # ---- 1. HASH INTEGRITY -------------------------------------------------
    src, h = rec.get("reward_source"), rec.get("reward_source_hash")
    if src is not None and h:
        n_hash += 1
        if hashlib.sha256(src.encode("utf-8")).hexdigest() != h:
            fail["hash mismatch (source vs recorded hash)"].append(norm)
        rp = os.path.join(os.path.dirname(rec_path), "reward.py")
        if os.path.exists(rp):
            if hashlib.sha256(open(rp, "rb").read()).hexdigest() != h:
                fail["hash mismatch (reward.py on disk vs recorded hash)"].append(norm)
        if arm in LLM_ARMS:
            by_hash_arm[h].add(arm)
            by_hash_path.setdefault(h, norm)

    # ---- 2/3. CVaR MONOTONICITY AND SIGN ------------------------------------
    ts = m.get("tail_stats") or {}
    keys = ("cvar_01", "cvar_05", "cvar_10", "cvar_25")
    if all(k in ts for k in keys):
        n_tail += 1
        v = [ts[k] for k in keys]
        if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in v):
            fail["non-finite CVaR"].append(f"{norm} {v}")
        else:
            # mathematical identity: worse tail level => more negative
            if not (v[0] <= v[1] <= v[2] <= v[3]):
                fail["*** CVaR MONOTONICITY VIOLATED ***"].append(
                    f"{norm} 01={v[0]:.6f} 05={v[1]:.6f} 10={v[2]:.6f} 25={v[3]:.6f}")
            if any(x > 0 for x in v):
                fail["CVaR positive (left tail of signed returns must be <= 0)"].append(
                    f"{norm} {v}")
        for k, val in ts.items():
            if not (isinstance(val, (int, float)) and math.isfinite(val)):
                fail["non-finite tail_stat"].append(f"{norm} {k}={val!r}")

    # ---- 4. val_fitness: Deflated Sharpe is a PROBABILITY in [0,1] ----------
    f = m.get("val_fitness")
    if f is not None:
        n_fit += 1
        if not (isinstance(f, (int, float)) and math.isfinite(f)):
            fail["non-finite val_fitness"].append(f"{norm} {f!r}")
        elif not (0.0 <= f <= 1.0):
            fail["val_fitness outside [0,1] (DSR is a probability)"].append(f"{norm} {f}")

    # ---- 5. val_returns finite ---------------------------------------------
    vr = m.get("val_returns")
    if isinstance(vr, list) and vr:
        bad = [x for x in vr if not (isinstance(x, (int, float)) and math.isfinite(x))]
        if bad:
            fail["non-finite val_returns"].append(f"{norm} {len(bad)} bad of {len(vr)}")

    # ---- 6. REGISTERED STEP COUNT ------------------------------------------
    calls = m.get("train_safe_call_count")
    if calls is not None:
        n_steps += 1
        if int(calls) != STEPS:
            fail[f"train_safe_call_count != {STEPS:,}"].append(f"{norm} calls={calls}")

    # ---- 7. PopArt invariants ----------------------------------------------
    ps = m.get("popart_scale") or {}
    if ps:
        n_popart += 1
        rl, rm = ps.get("raw_rms_last"), ps.get("raw_rms_max")
        sl, sm = ps.get("sigma_last"), ps.get("sigma_max")
        vals = [rl, rm, sl, sm]
        if any(v is None or not math.isfinite(v) for v in vals):
            fail["non-finite popart_scale"].append(f"{norm} {ps}")
        else:
            if rm < rl - 1e-9:
                fail["popart raw_rms_max < raw_rms_last"].append(f"{norm} max={rm} last={rl}")
            if sm < sl - 1e-9:
                fail["popart sigma_max < sigma_last"].append(f"{norm} max={sm} last={sl}")
            # sigma = max(popart_min_scale=1.0, raw_rms)  -- the documented floor
            for tag, sg, rr in (("last", sl, rl), ("max", sm, rm)):
                expect = max(1.0, rr)
                if abs(sg - expect) > 1e-6 * max(1.0, abs(expect)):
                    fail[f"popart sigma_{tag} != max(1.0, raw_rms_{tag})"].append(
                        f"{norm} sigma={sg} raw={rr} expect={expect}")

    # ---- 8. SEED RANGE ------------------------------------------------------
    s = rec.get("seed")
    if s is not None:
        n_seed += 1
        if not (isinstance(s, int) and 0 <= s <= SEED_MAX):
            fail[f"seed outside [0,{SEED_MAX}]"].append(f"{norm} seed={s!r}")

# ---- 9. PROGRAM SHARED ACROSS ARMS ------------------------------------------
shared = {h: arms for h, arms in by_hash_arm.items() if len(arms) > 1}
for h, arms in shared.items():
    fail["*** identical program under >1 ARM ***"].append(f"{h[:16]} arms={sorted(arms)} e.g. {by_hash_path[h]}")

print(f"records examined (frozen/ and .pull_tmp excluded): {n}")
print(f"  with reward hash    : {n_hash}")
print(f"  with tail_stats     : {n_tail}")
print(f"  with val_fitness    : {n_fit}")
print(f"  with step count     : {n_steps}")
print(f"  with popart_scale   : {n_popart}")
print(f"  with seed           : {n_seed}")
print(f"  distinct LLM programs: {len(by_hash_arm)}")
print()
if not fail:
    print("=" * 78)
    print("ALL INVARIANTS HOLD -- independently re-derived, zero violations.")
else:
    print("=" * 78)
    for k, v in sorted(fail.items(), key=lambda kv: -len(kv[1])):
        print(f"{len(v):6d}  {k}")
        for item in v[:5]:
            print(f"           {item}")
