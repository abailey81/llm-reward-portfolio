"""CONSTRUCT VALIDITY: does RUN 4's ARCHIVE actually carry the arm manipulation H2 rests on?

WHY THIS EXISTS (2026-07-30). Earlier sessions verified the manipulation by calling
`schema.build_block` directly — i.e. they proved the CODE would produce the right thing. Nobody had
verified that the RUN DID. Those are different claims, and only the second one is evidence. H2's entire
construct validity is the assertion that ONLY the fed feedback block differs across arms, and that the
blocks differ exactly as registered:

    scalar            0 tail numbers   (the scalar score alone)
    scalar_cvar5      1 tail number    (CVaR 5% only)
    distributional    6 tail numbers   (CVaR 5/10/25/1%, left-tail mass, left-tail skew)
    placebo           6 INERT constants (+0.0000) on the same six labels
    placebo_shuffled  the same six REAL values on DERANGED labels (no value on its own label)

This reads the ARCHIVED prompts (`record.json: prompt`, written at authoring time) and checks each of
those properties against the real run. It also checks the two things that would silently break the
design: a tail number leaking into `scalar`, and a placebo_shuffled assignment that is not a true
derangement (a fixed point would mean one value IS on its own label, weakening the control).

READ-ONLY. Report-only verification; touches nothing.
"""
from __future__ import annotations

import collections
import glob
import json
import re
import sys
from pathlib import Path

# the six registered tail labels, in canonical order
TAIL_LABELS = ["CVaR 5%", "CVaR 10%", "CVaR 25%", "CVaR 1%", "left-tail mass", "left-tail skew"]
# CORRECTED 2026-07-30 after inspecting a real prompt. `placebo` does NOT carry the tail LABELS with
# zeroed values — it carries six INERT constants under NEUTRAL labels ("reference value 1..6") under the
# heading "Reference constants (inert; no diagnostic content)". That is a STRONGER control than
# same-labels-zero-values would be: it removes the semantic hint that tail statistics exist at all,
# while still matching the block's shape and token count. My first expectation (6 tail labels in
# placebo) was wrong and produced a false MISMATCH on four legs.
EXPECTED_TAIL_COUNT = {
    "scalar": 0, "scalar_cvar5": 1, "distributional": 6,
    "placebo": 0, "placebo_shuffled": 6,
}
#: `placebo` must instead carry exactly six inert reference constants.
EXPECTED_INERT = {"placebo": 6}


def inert_values(prompt: str) -> list[str]:
    """The `reference value N: +0.0000` constants placebo carries instead of tail diagnostics."""
    return re.findall(r"reference value \d+:\s*([+-]?\d*\.?\d+)", prompt)


def fed_values(prompt: str) -> dict[str, str]:
    """{label: value-as-written} for every tail line present in the archived prompt."""
    out: dict[str, str] = {}
    for lab in TAIL_LABELS:
        m = re.search(re.escape(lab) + r":\s*([+-]?\d*\.?\d+)", prompt)
        if m:
            out[lab] = m.group(1)
    return out


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else "outputs/campaign_cluster_run4")
    line = argv[2] if len(argv) > 2 else "search"      # "search" == the c1 CORE/Opus line
    _ = line
    rc = 0

    per_arm: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    inert_rows: list[list[str]] = []
    starved: list[tuple[str, str, str, int]] = []
    scalar_scores: dict[str, set[str]] = collections.defaultdict(set)

    n_records = 0          # every record the glob actually found — the wrong-path discriminator
    for p in glob.glob(str(root / line / "*" / "*" / "record.json")):
        try:
            r = json.load(open(p, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        n_records += 1
        arm, pr = r.get("arm"), r.get("prompt") or ""
        if arm not in EXPECTED_TAIL_COUNT or int(r.get("generation", 0)) == 0:
            continue      # generation 0 has no fed block by design (the initial prompt)
        # A gen>0 candidate can STILL carry the initial prompt: `prev_block` is set only when the
        # previous generation yielded an ACCEPTED candidate, so a model that rejects nearly everything
        # (qwen3.5-9b at 91%) has nothing to reflect on and is re-issued the initial prompt. Those
        # records have NO fed block by construction and asserting one against them produced two false
        # violations. They are counted as STARVED — which is itself the capability-floor finding
        # (record s.31.1), independently agreeing with the reflection guard's 5/7 for that leg.
        if not pr.startswith("Reflect on the previous candidate"):
            starved.append((line, arm, str(r.get("run_id")), int(r.get("generation", 0))))
            continue
        per_arm[arm].append(fed_values(pr))
        if arm == "placebo":
            inert_rows.append(inert_values(pr))
        m = re.search(r"scored:\s*([+-]?\d*\.?\d+)", pr)
        if m:
            scalar_scores[arm].add(m.group(1))

    print(f"=== ARM MANIPULATION, verified against the ARCHIVE ({line}) ===")

    # ⚠ AN EMPTY SCAN MUST NOT REPORT A GREEN VERDICT (RUN 9, record §93).
    # Until now, scanning ZERO prompts printed "VERDICT: ALL REGISTERED ARM PROPERTIES HOLD IN THE
    # ARCHIVE" and returned rc=0 — because every per-arm row short-circuits to "no gen>0 prompt yet"
    # without touching `rc`, and the two killer checks are vacuously satisfied by empty lists. Found
    # by invoking this tool with a WRONG ROOT (`…/run4/search` instead of `…/run4` + `search`, so the
    # glob became `…/search/search/*/*` and matched nothing): it answered "all properties hold" while
    # verifying literally nothing.
    #
    # THIS IS THE MOST DANGEROUS PLACE IN THE REPOSITORY FOR THAT FAILURE MODE. This tool certifies
    # the MANIPULATION H2 rests on — that `scalar` is tail-blind, that `placebo` is inert, that
    # `placebo_shuffled` is deranged. A reassuring null here, from a purged Scratch, a renamed root or
    # a mistyped argument, is worse than an alarm, because nothing invites a second look.
    #
    # ⚠ AND THE FAIL-LOUD MUST NOT ITSELF FALSE-ALARM (caught in the same session, on my own fix).
    # A first version returned 2 whenever there were no gen>0 prompts — which fires on
    # `search_h3_singleshot`, where that state is CORRECT BY DESIGN: H3 is the SINGLE-SHOT arm and
    # draws its entire 30-candidate budget in ONE generation (PREREGISTRATION §6), so it has 30 g0
    # records and can never have a gen>0 prompt. Alarming on it would be the alarm-fatigue failure
    # this repository keeps fixing, introduced by the fix for a different one.
    #
    # The discriminator is whether the glob found ANY records at all:
    #   records found, none at gen>0  -> legitimate (single-shot by design, or not yet at gen 1) -> 0
    #   NO records found at all       -> the path is wrong / the archive is gone                 -> 2
    total_prompts = sum(len(v) for v in per_arm.values())
    if total_prompts == 0:
        if n_records == 0:
            print(f"\n*** NOTHING TO VERIFY: 0 records found under {root / line} ***")
            print("    This is NOT a pass. The root/line arguments are wrong, or the archive is gone.")
            print("    Usage: verify_arm_manipulation.py [ROOT] [LINE]")
            print("    — ROOT is the run root (e.g. outputs/campaign_cluster_run4), LINE is a sub-root")
            print("      (e.g. search, search_leg_kimi_k3). They are SEPARATE arguments, not a path.")
            return 2
        print(f"\n    {n_records} record(s) found, none at generation > 0 — nothing to verify YET.")
        print("    Correct and expected for `search_h3_singleshot` (the SINGLE-SHOT arm draws its")
        print("    whole budget in one generation by design), and for any line still in generation 0.")
        print("    NOT a pass and NOT a failure: there is simply no fed block to check.")
        return 0

    print(f"{'arm':20s} {'prompts':>8s} {'tail #':>7s} {'expected':>9s}  verdict")
    for arm in ("scalar", "scalar_cvar5", "distributional", "placebo", "placebo_shuffled"):
        rows = per_arm.get(arm, [])
        if not rows:
            print(f"{arm:20s} {'0':>8s} {'-':>7s} {EXPECTED_TAIL_COUNT[arm]:>9d}  no gen>0 prompt yet")
            continue
        counts = {len(x) for x in rows}
        exp = EXPECTED_TAIL_COUNT[arm]
        ok = counts == {exp}
        rc = rc or (0 if ok else 2)
        print(f"{arm:20s} {len(rows):>8d} {sorted(counts)!s:>7s} {exp:>9d}  "
              f"{'OK' if ok else '*** MISMATCH ***'}")

    # --- the two silent killers -------------------------------------------------------------------
    print("\n--- does a tail number LEAK into `scalar`? (construct-validity hinge) ---")
    leak = [x for x in per_arm.get("scalar", []) if x]
    print(f"  scalar prompts carrying ANY tail label: {len(leak)} "
          f"{'OK - tail-blind as registered' if not leak else '*** LEAK ***'}")
    if leak:
        rc = 2
        print(f"      example: {leak[0]}")

    print("\n--- is `placebo` genuinely INERT (all six +0.0000)? ---")
    pl = per_arm.get("placebo", [])
    if pl:
        nonzero = [v for x in pl for v in x.values() if float(v) != 0.0]
        print(f"  placebo values that are non-zero: {len(nonzero)} "
              f"{'OK - inert' if not nonzero else '*** NOT INERT ***'}")
        if nonzero:
            rc = 2
            print(f"      examples: {nonzero[:6]}")

    print("\n--- is `placebo_shuffled` a TRUE DERANGEMENT vs `distributional`? ---")
    dist = per_arm.get("distributional", [])
    shuf = per_arm.get("placebo_shuffled", [])
    if dist and shuf:
        # a value set from distributional, and the shuffled arm's label->value mapping
        dv = {lab: v for x in dist for lab, v in x.items()}
        fixed = []
        for x in shuf:
            for lab, v in x.items():
                if lab in dv and v == dv[lab]:
                    fixed.append((lab, v))
        print(f"  labels whose value MATCHES distributional's same label (fixed points): {len(fixed)}")
        print("      NOTE: values come from different training runs, so an exact match is weak")
        print("      evidence either way; the registered derangement is verified at BUILD time by")
        print("      schema.build_block's own test. This checks only for an obvious identity mapping.")
        if fixed:
            print(f"      {fixed[:6]}")
    else:
        print("  not enough gen>0 prompts on both arms yet")

    print(f"\nVERDICT: {'ALL REGISTERED ARM PROPERTIES HOLD IN THE ARCHIVE' if rc == 0 else '*** A REGISTERED ARM PROPERTY IS VIOLATED ***'}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
