"""D17 evidence probe: why seven records across five models share a bit-identical 49.983%.

THE FINDING (2026-07-30). ``safe_call`` substitutes ``(SAFE_DEFAULT, {}, None)`` on failure -
including the ``None`` reward_state. A stateful reward with a cold-start branch (``if n < 2:``)
therefore enters a LIMIT CYCLE: the cold-start call succeeds and returns state, the next call
takes the main path and raises, the harness resets state to None, and the cycle repeats forever.

  period = (calls needed to leave the cold-start branch) + 1

so a 2-call warm-up gives 1/2 = 49.98% and a 3-call warm-up gives 1/3 = 33.33%, IDENTICALLY
across models, because the fraction is set by the reset cycle rather than by the defect. Five
different exceptions (UnboundLocalError, ambiguous-truth-value, non-finite, ZeroDivisionError,
IndexError) all produce the same fraction.

TWO CONSEQUENCES, both real:

1. The safe-default FRACTION IS NOT A SEVERITY MEASURE. 49.98% does not mean "trained half on a
   valid reward" - it means the reward never once executed its intended logic. The write-up must
   never read the fraction as partial success.
2. For a reward whose ONLY defect is at the warm-up boundary, the harness converts a one-step
   transient into a PERMANENT 50% failure, biasing that model's measured authoring reliability
   DOWNWARD. Confirmed for 2 of the 9 breaching records.

METHOD AND ITS LIMIT. Synthetic returns and a random policy, not the trained path - so the
counterfactual fractions are INDICATIVE, not the campaign's own. What is established firmly is
(a) the cycle mechanism, which reproduces the archived fractions to within 0.08 pp, and (b) that
for at least two rewards the main-path code is not itself broken. A record whose shipped failure
does not reproduce here is reported INCONCLUSIVE, never as evidence either way.

Read-only. Touches nothing under src/ (drift-fenced during the live run).
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "outputs" / "campaign_cluster_run4"
N_ASSETS, N_STEPS, EPISODE_LEN = 30, 400, 120
FLOOR = 0.10  # the R115 winner-eligibility execution floor


def load_reward(rel: str):
    """Compile an archived reward as the sandbox does: ``np`` injected, no imports required."""
    ns: dict = {"np": np, "math": math}
    src = (ARCHIVE / rel / "reward.py").read_text(encoding="utf-8")
    exec(compile(src, rel, "exec"), ns)  # noqa: S102 - archived, ast_gate-cleared reward code
    return ns["reward"]


def run(fn, *, reset_state_on_failure: bool) -> tuple[float, str]:
    """Replay the reward; return (failure fraction, the first 24 per-call verdicts).

    ``reset_state_on_failure=True`` mirrors the shipped ``safe_call``. False is the
    counterfactual that isolates the harness's contribution to the failure rate.
    """
    verdicts: list[str] = []
    state = None
    w_prev = np.full(N_ASSETS, 1.0 / N_ASSETS)
    rng = np.random.default_rng(0)  # identical stream per reward: differences are the reward's

    for t in range(N_STEPS):
        if t % EPISODE_LEN == 0:  # env reset hands back reward_state=None
            state, w_prev = None, np.full(N_ASSETS, 1.0 / N_ASSETS)
        rets = rng.normal(0.0004, 0.012, N_ASSETS)
        w = rng.dirichlet(np.ones(N_ASSETS))
        port_ret = float(np.dot(w, rets))
        info = {"weights": w, "prev_weights": w_prev, "reward_state": state}
        try:
            total, _components, new_state = fn(w, rets, w_prev, port_ret, info)
            total_f = float(total)
            if not math.isfinite(total_f):
                raise ValueError("non-finite total")
            if abs(total_f) > 1.0e6:  # the contract's magnitude bound, as safe_call applies it
                raise ValueError("magnitude exceeds the 1e6 contract bound")
            state = new_state
            verdicts.append(".")
        except Exception:  # noqa: BLE001 - mirrors safe_call's blanket except
            verdicts.append("X")
            if reset_state_on_failure:
                state = None
        w_prev = w

    return verdicts.count("X") / len(verdicts), "".join(verdicts[:24])


def breaching_units() -> list[tuple[str, float]]:
    """Every archived record at or above the R115 floor, worst first."""
    out = []
    for rec in ARCHIVE.rglob("record.json"):
        try:
            m = (json.loads(rec.read_text(encoding="utf-8")).get("metrics") or {})
        except Exception:  # noqa: BLE001
            continue
        calls, dflt = m.get("train_safe_call_count"), m.get("train_safe_default_count")
        if calls and dflt is not None and dflt / calls >= FLOOR:
            out.append((str(rec.parent.relative_to(ARCHIVE)).replace("\\", "/"), dflt / calls))
    return sorted(out, key=lambda kv: -kv[1])


def main() -> int:
    units = breaching_units()
    if not units:
        print("[probe] no records at or above the R115 floor")
        return 0

    print("%-50s %8s %8s %9s  %s" % ("unit", "archive", "shipped", "preserved", "CLASS"))
    tally = {"TRAPPED": 0, "BROKEN": 0, "INCONCLUSIVE": 0}
    for rel, archived in units:
        shipped, pattern = run(load_reward(rel), reset_state_on_failure=True)
        preserved, _ = run(load_reward(rel), reset_state_on_failure=False)

        # A record whose shipped failure does not reproduce here tells us NOTHING about the
        # counterfactual - guard against reading its low `preserved` as evidence of a trap.
        if shipped < FLOOR:
            cls = "INCONCLUSIVE (not reproduced under synthetic data)"
            tally["INCONCLUSIVE"] += 1
        elif preserved < FLOOR:
            cls = "TRAPPED transient -> reliability biased DOWNWARD"
            tally["TRAPPED"] += 1
        else:
            cls = "genuinely broken (defect, not harness)"
            tally["BROKEN"] += 1
        print("%-50s %7.2f%% %7.2f%% %8.2f%%  %s"
              % (rel.replace("search_leg_", ""), archived * 100, shipped * 100,
                 preserved * 100, cls))
        print("%-50s          %s" % ("", pattern))

    print("\n[probe] trapped=%(TRAPPED)d broken=%(BROKEN)d inconclusive=%(INCONCLUSIVE)d" % tally)
    print("[probe] the fraction encodes the RESET PERIOD, not the severity - see record section 37")
    return 0


if __name__ == "__main__":
    sys.exit(main())
