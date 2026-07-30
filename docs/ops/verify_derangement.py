"""Is `placebo_shuffled` GENUINELY DERANGED? A structural test using only the archive.

WHY (2026-07-30). §34.4 recorded honestly that the derangement — the property that no fed value sits on
its OWN label — was verified at BUILD time by `schema.build_block`'s test but NOT from the archive. That
left a registered control property resting on a unit test rather than on the run. This closes it.

THE IDEA. A genuine tail vector is MONOTONE in the CVaR ladder: a more extreme quantile is at least as
negative, so

        CVaR 1%  <=  CVaR 5%  <=  CVaR 10%  <=  CVaR 25%

That is a mathematical property of the estimator (nested tail sets), not a modelling assumption, so it
must hold in EVERY `distributional` block. If `placebo_shuffled` carries the same six values permuted
off their own labels, the permutation will in general BREAK that ordering. So:

    distributional    -> monotone ladder in ~100 % of blocks
    placebo_shuffled  -> monotone ladder in FAR fewer (a derangement of 4 ladder positions leaves the
                         ordering intact only by coincidence)

This is a necessary-condition test, not a proof of derangement: a permutation could accidentally
preserve monotonicity. So the verdict is stated as evidence with its strength, and the two arms are
compared against EACH OTHER, which controls for the estimator itself.

It also reports the fed-block CHARACTER LENGTH per arm — the registered token control (the arms must be
length-comparable so token count cannot confound the manipulation).

READ-ONLY.
"""
from __future__ import annotations

import collections
import glob
import json
import re
import sys
from pathlib import Path

LADDER = ["CVaR 1%", "CVaR 5%", "CVaR 10%", "CVaR 25%"]   # most extreme -> least extreme
ALL_LABELS = LADDER + ["left-tail mass", "left-tail skew"]


def fed(prompt: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for lab in ALL_LABELS:
        m = re.search(re.escape(lab) + r":\s*([+-]?\d*\.?\d+)", prompt)
        if m:
            out[lab] = float(m.group(1))
    return out


def block_len(prompt: str) -> int:
    """Characters of the fed block: the diagnostics/constants section only."""
    m = re.search(r"(Realized-return tail diagnostics.*?|Reference constants.*?)(?:\n\n|\n\[)", prompt,
                  re.S)
    return len(m.group(1)) if m else 0


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else "outputs/campaign_cluster_run4")
    mono: dict[str, list[bool]] = collections.defaultdict(list)
    lens: dict[str, list[int]] = collections.defaultdict(list)
    examples: dict[str, dict[str, float]] = {}

    for p in glob.glob(str(root / "search*" / "*" / "*" / "record.json")):
        try:
            r = json.load(open(p, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        arm, pr = r.get("arm"), r.get("prompt") or ""
        if not pr.startswith("Reflect on the previous candidate"):
            continue
        v = fed(pr)
        lens[arm].append(block_len(pr))
        if all(k in v for k in LADDER):
            vals = [v[k] for k in LADDER]
            mono[arm].append(all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1)))
            examples.setdefault(arm, v)

    print("=== IS THE CVaR LADDER MONOTONE?  (CVaR 1% <= 5% <= 10% <= 25%) ===")
    print(f"{'arm':20s} {'blocks':>7s} {'monotone':>9s} {'rate':>7s}")
    rates: dict[str, float] = {}
    for arm in ("distributional", "placebo_shuffled"):
        m = mono.get(arm, [])
        if not m:
            print(f"{arm:20s} {'0':>7s} {'-':>9s} {'-':>7s}")
            continue
        rate = sum(m) / len(m)
        rates[arm] = rate
        print(f"{arm:20s} {len(m):>7d} {sum(m):>9d} {rate:>6.1%}")

    for arm in ("distributional", "placebo_shuffled"):
        if arm in examples:
            print(f"\n  example {arm}: " +
                  "  ".join(f"{k}={examples[arm][k]:+.4f}" for k in LADDER))

    print("\n=== FED-BLOCK CHARACTER LENGTH (the registered token control) ===")
    for arm in ("scalar", "scalar_cvar5", "distributional", "placebo", "placebo_shuffled"):
        L = [x for x in lens.get(arm, []) if x]
        if L:
            print(f"  {arm:20s} n={len(L):4d}  min={min(L):4d} max={max(L):4d} "
                  f"{'CONSTANT' if min(L) == max(L) else 'varies'}")
        else:
            print(f"  {arm:20s} no fed block (expected for `scalar`)")

    rc = 0
    print("\n--- VERDICT ---")
    d, s = rates.get("distributional"), rates.get("placebo_shuffled")
    if d is None or s is None:
        print("  not enough blocks on both arms yet")
    elif d > 0.99 and s < 0.5:
        print(f"  distributional is monotone {d:.1%} of the time and placebo_shuffled only {s:.1%}.")
        print("  The ladder ordering is a MATHEMATICAL property of nested tail sets, so the only way")
        print("  placebo_shuffled can break it is if its values are NOT on their own labels.")
        print("  => STRONG archive-side evidence that the derangement is real and active.")
    elif d > 0.99 and s > 0.99:
        rc = 2
        print(f"  *** placebo_shuffled is ALSO monotone {s:.1%} of the time. That is what an IDENTITY")
        print("  mapping looks like — the derangement may not be applied. INVESTIGATE. ***")
    else:
        print(f"  inconclusive: distributional {d:.1%} monotone, placebo_shuffled {s:.1%}.")
        print("  A distributional rate below 100% would mean the ladder assumption itself needs review.")
    print("\n  NOTE: this is a NECESSARY-condition test. A permutation can preserve monotonicity by")
    print("  coincidence, so a low rate is strong evidence of derangement while it cannot PROVE that")
    print("  every block is a derangement. The build-time test in schema.build_block owns that claim.")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
