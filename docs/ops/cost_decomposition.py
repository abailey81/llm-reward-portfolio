"""IS THE NEGATIVE SHARPE LOGICAL? Decompose it into gross skill and transaction-cost drag.

WHY (2026-07-30, Tamer's challenge — the second time he has pushed on this and the second time it
was the right thing to push on). Ten of eleven H1 baselines score test Sharpe -0.171..-0.325 over a
sealed window in which an equal-weighted buy-and-hold of the SAME thirty assets returned
**+1.2825 Sharpe / +183.3 %**. A long-only agent losing money on a rising asset base is not obviously
sensible, and "transaction costs" is an assertion until it is an arithmetic.

⚠ CORRECTED 2026-07-30 (record s.36): the earlier +0.817 / +122 % figure was computed over 1,631
sessions from 2020-01-02, but the agents traded only the 1,571 sessions from 2020-03-30 -- the
60-session production-lookback purge (R18), which silently contains the COVID crash. THIS SCRIPT was
never affected, because it reads each record's OWN `test_returns` / `test_gross` series rather than
re-deriving a window from the panel; only the free-standing benchmark comparison was wrong. That is
exactly why analysis-time obligation 8 now requires every benchmark window to come from the records.

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

#: ★★★ SEALED TREATMENT ARMS — NEVER PRINTED BY THIS SCRIPT, UNDER ANY FLAG (UNBLIND-GLOB, coord
#: M287, 2026-08-01). This file globs ``test/*/*`` and prints a per-unit SEALED-TEST SHARPE. That was
#: SAFE ON THE DAY IT WAS WRITTEN (2026-07-30), when ``test/`` held only the eleven H1 baselines and
#: random_search — the glob was IMPLICITLY SCOPED BY WHAT EXISTED. **C4 widens it automatically**:
#: ``test/placebo`` now holds 30 records, and placebo is one of the three registered H2-RA
#: comparators, so running this unchanged would print a treatment arm's sealed outcome. Nobody has to
#: do anything wrong for that to happen, and the docstring above still tells the reader it is about
#: baselines — the mental model was correct on the day and silently expired.
#: The standing rule is absolute: NEVER read a treatment arm's SEALED-TEST outcome until the ladder
#: completes. So the scope is now EXPLICIT and DENY-BY-DEFAULT rather than incidental.
H2_SEALED_ARMS = frozenset({
    "distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled",
})
#: Default inclusion: the H1 hand-designed baselines this script was WRITTEN for. Anything new that
#: C4 creates is excluded until someone opts in by name, which is the direction that fails safe.
DEFAULT_PREFIX = "baseline_"

ANN = 252.0
BPS = 10.0          # config/environment.yaml headline_bps (== prereg cost_bps_oneway)
COST = BPS * 1e-4   # cost per unit turnover


def sharpe(r: list[float]) -> float:
    if len(r) < 3:
        return float("nan")
    sd = statistics.stdev(r)
    return math.sqrt(ANN) * statistics.fmean(r) / sd if sd > 0 else float("nan")


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    include_all = "--include-non-baseline" in argv
    root = args[0] if args else "outputs/campaign_cluster_run4"
    rows = []
    refused: set[str] = set()
    skipped: set[str] = set()
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
        if unit in H2_SEALED_ARMS:
            refused.add(unit)          # unconditional: no flag can print a sealed treatment arm
            continue
        if not (include_all or unit.startswith(DEFAULT_PREFIX)):
            skipped.add(unit)
            continue
        gross = [n + COST * t for n, t in zip(net, tov)]
        rows.append((unit, statistics.fmean(tov), sharpe(net), sharpe(gross),
                     math.prod(1.0 + x for x in net) - 1.0,
                     math.prod(1.0 + x for x in gross) - 1.0))

    # Report the omissions BY NAME. A silent skip is how a scope guard becomes a lie about coverage.
    if refused:
        print(f"REFUSED (sealed H2 treatment arms, never printable): {', '.join(sorted(refused))}")
    if skipped:
        print(f"skipped (not {DEFAULT_PREFIX}*; pass --include-non-baseline to include): "
              f"{', '.join(sorted(skipped))}")
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
