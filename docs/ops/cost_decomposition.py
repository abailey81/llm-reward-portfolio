"""IS THE NEGATIVE SHARPE LOGICAL? Decompose it into gross skill and transaction-cost drag.

WHY (2026-07-30, Tamer's challenge — the second time he has pushed on this and the second time it
was the right thing to push on). Ten of eleven H1 baselines score test Sharpe -0.171..-0.325 over a
sealed window in which an equal-weighted buy-and-hold of the SAME thirty assets returned +0.817 Sharpe
/ +122 %. A long-only agent losing money on a rising asset base is not obviously sensible, and
"transaction costs" is an assertion until it is an arithmetic.

THE METHOD IS REGISTERED, NOT INVENTED HERE. `config/preregistration.yaml` line 338 states the exact
repricing identity — `net_c = gross - bps*1e-4*turnover` — and notes it is EXACT because the cost is
charged linearly, which is why `cost_sweep` (grid 0/5/10/25/50 bps, report_only) can reprice without
retraining. Every record carries both `test_returns` (NET of cost) and `test_turnover` (the per-period
turnover series), so the gross series is recoverable exactly:

    gross_t = net_t + bps*1e-4 * turnover_t

This script reports, per unit: realised mean turnover, the implied annual cost drag, the NET Sharpe as
archived, and the GROSS (zero-cost) Sharpe. If the gross Sharpes are positive, the negative net result
is a cost phenomenon and the agents have gross skill; if they stay negative, the agents genuinely have
no edge. Either answer is publishable, and the point is to MEASURE rather than assume.

READ-ONLY. Report-only analysis; changes no design and no archive.
"""
from __future__ import annotations

import glob
import json
import math
import os
import statistics
import sys

ANN = 252.0
BPS = 10.0          # config/environment.yaml headline_bps (== prereg cost_bps_oneway)
COST = BPS * 1e-4   # cost per unit turnover


def sharpe(r: list[float]) -> float:
    if len(r) < 3:
        return float("nan")
    sd = statistics.stdev(r)
    return math.sqrt(ANN) * statistics.fmean(r) / sd if sd > 0 else float("nan")


def main(argv: list[str]) -> int:
    root = argv[1] if len(argv) > 1 else "outputs/campaign_cluster_run4"
    rows = []
    for p in glob.glob(os.path.join(root, "test", "*", "*", "record.json")):
        try:
            rec = json.load(open(p, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        m = rec.get("metrics") or {}
        net = m.get("test_returns")
        tov = m.get("test_turnover")
        if not isinstance(net, list) or not isinstance(tov, list) or len(net) != len(tov):
            continue
        unit = p.replace("\\", "/").split("/")[-3]
        gross = [n + COST * t for n, t in zip(net, tov)]
        rows.append((unit, statistics.fmean(tov), sharpe(net), sharpe(gross),
                     math.prod(1.0 + x for x in net) - 1.0,
                     math.prod(1.0 + x for x in gross) - 1.0))

    if not rows:
        print("no records carrying BOTH test_returns and test_turnover yet")
        return 0

    agg: dict[str, list] = {}
    for unit, tv, sn, sg, cn, cg in rows:
        agg.setdefault(unit, []).append((tv, sn, sg, cn, cg))

    print(f"=== COST DECOMPOSITION at the registered {BPS:.0f} bps one-way "
          f"({len(rows)} records, {len(agg)} units) ===")
    print(f"{'unit':38s} {'n':>3s} {'turnover':>9s} {'cost/yr':>8s} "
          f"{'NET Sh':>8s} {'GROSS Sh':>9s} {'net cum':>9s} {'gross cum':>10s}")
    for unit in sorted(agg):
        v = agg[unit]
        tv = statistics.fmean(x[0] for x in v)
        print(f"{unit:38s} {len(v):3d} {tv:9.4f} {tv*COST*ANN:7.1%} "
              f"{statistics.fmean(x[1] for x in v):+8.4f} "
              f"{statistics.fmean(x[2] for x in v):+9.4f} "
              f"{statistics.fmean(x[3] for x in v):+9.1%} "
              f"{statistics.fmean(x[4] for x in v):+10.1%}")

    allv = [x for v in agg.values() for x in v]
    tv = statistics.fmean(x[0] for x in allv)
    print(f"\n  ACROSS ALL UNITS: mean per-period turnover = {tv:.4f} "
          f"=> implied cost drag = {tv:.4f} x {COST:.4f} x {ANN:.0f} = {tv*COST*ANN:.1%} / year")
    print(f"  mean NET Sharpe   {statistics.fmean(x[1] for x in allv):+.4f}")
    print(f"  mean GROSS Sharpe {statistics.fmean(x[2] for x in allv):+.4f}")
    print("\n  READ IT LIKE THIS: if GROSS is clearly positive while NET is negative, the negative")
    print("  result is a TRANSACTION-COST phenomenon and the policies do have gross skill. If GROSS")
    print("  is also negative, the policies have no edge and cost is not the explanation.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
