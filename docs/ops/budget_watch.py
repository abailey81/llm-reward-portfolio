"""BUDGET HEADROOM WATCH — will a key run dry before the authoring finishes?

WHY THIS EXISTS. On 2026-07-30 the Anthropic projection was reported as "$20.90, a 26 % margin" and
was wrong: it asked *which generations exist anywhere in a line's root*, saw g0..g5 present on the
confirmatory line and concluded authoring was done. Authoring is per (line, ARM) — that line's
`scalar` arm had reached g5 while its three CONTROL arms sat at g1, with fourteen arm-generations
still to write. The corrected projection was a ~$9 SHORTFALL (record §49).

`scripts/preflight.py` has no provider-headroom check either (DEFERRED_FIXES §3), and preflight only
fires at launch. Nothing watched this mid-run. This does.

WHAT IT DOES. Reads the per-line spend ledgers and the per-(line, arm) generation depth from the
archive, projects the remaining AUTHORING cost at each line's own observed cost per arm-generation,
and compares the total against the credited headroom per provider.

  exit 0  comfortable   (projected total leaves >= WARN_FRACTION of the credit unused)
  exit 1  TIGHT         (projected to finish, but with less than that margin)
  exit 2  SHORTFALL     (projected to exceed the credit — a key will run dry mid-run)

C4 (the seed ladder) needs NO LLM calls: it retrains an already-authored reward. So the authoring
projection is the WHOLE remaining exposure, which is what makes this projectable at all.

Usage:  python docs/ops/budget_watch.py [run_root]
"""
from __future__ import annotations

import glob
import json
import os
import sys
from collections import defaultdict

ROOT = sys.argv[1] if len(sys.argv) > 1 else "outputs/campaign_cluster_run4"
ARMS = ("distributional", "scalar", "placebo", "scalar_cvar5", "placebo_shuffled")
FINAL_GENERATION = 5          # the registered chain is 6 generations, g0..g5
WARN_FRACTION = 0.15          # below this much unused credit we call it TIGHT

#: line tag -> (archive root, provider). h3ss is SINGLE-SHOT: it authors once at g0 and then trains at
#: many seeds, so it has no remaining generations by design — the flag below encodes that, because
#: treating it like a six-generation line is exactly the artefact that produced a $25 phantom.
LINES: dict[str, tuple[str, str, bool]] = {
    "c1":    ("search",                       "anthropic",  False),
    "h3ss":  ("search_h3_singleshot",         "anthropic",  True),
    "leg5":  ("search_leg_haiku_4_5",         "anthropic",  False),
    "leg8":  ("search_leg_sonnet_5",          "anthropic",  False),
    "leg1":  ("search_leg_deepseek_v4_pro",   "openrouter", False),
    "leg2":  ("search_leg_glm_5_2",           "openrouter", False),
    "leg3":  ("search_leg_qwen3_6_27b",       "openrouter", False),
    "leg4":  ("search_leg_qwen3_5_9b",        "openrouter", False),
    "leg6":  ("search_leg_gpt_5_6_luna",      "openrouter", False),
    "leg7":  ("search_leg_nemotron_3_super",  "openrouter", False),
    "leg9":  ("search_leg_gemini_2_5_flash",  "openrouter", False),
    "leg10": ("search_leg_kimi_k3",           "openrouter", False),
}

#: Credited headroom, in USD. LEDGER ESTIMATES from the 2026-07-28 console quotes minus RUN 3's spend
#: — NOT balance readings. Only Tamer can read the real balance; update these when he does.
CREDIT = {"anthropic": 28.15, "openrouter": 19.31}


def _spent_by_line() -> dict[str, float]:
    out: dict[str, float] = defaultdict(float)
    for path in glob.glob(os.path.join(ROOT, "spend_ledger_*.jsonl")):
        line = os.path.basename(path)[len("spend_ledger_"):-len(".jsonl")]
        for raw in open(path, encoding="utf-8"):
            try:
                out[line] += float(json.loads(raw).get("cost_usd") or 0.0)
            except Exception:
                continue
    return out


def _generation_depth() -> dict[str, dict[str, int]]:
    depth: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(lambda: -1))
    for path in glob.glob(os.path.join(ROOT, "**", "record.json"), recursive=True):
        try:
            rec = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        arm = rec.get("arm")
        gen = rec.get("generation")
        if arm in ARMS and isinstance(gen, int):
            root = os.path.relpath(path, ROOT).replace("\\", "/").split("/")[0]
            depth[root][arm] = max(depth[root][arm], gen)
    return depth


def main() -> int:
    spent = _spent_by_line()
    depth = _generation_depth()

    per_provider_spent: dict[str, float] = defaultdict(float)
    per_provider_left: dict[str, float] = defaultdict(float)

    print("%-7s %-11s %-32s %5s %5s %9s %9s" %
          ("line", "provider", "generations reached", "done", "left", "spent", "left $"))
    for line, (root, provider, single_shot) in sorted(LINES.items()):
        g = depth.get(root, {})
        reached = {a: g.get(a, -1) for a in ARMS}
        done = sum(v + 1 for v in reached.values() if v >= 0)
        left = 0 if single_shot else sum(
            FINAL_GENERATION - v for v in reached.values() if 0 <= v < FINAL_GENERATION)
        avg = (spent[line] / done) if done else 0.0
        cost_left = avg * left
        per_provider_spent[provider] += spent[line]
        per_provider_left[provider] += cost_left
        shown = "single-shot (authors once)" if single_shot else " ".join(
            "%s=g%d" % (a[:4], reached[a]) for a in ARMS)
        print("%-7s %-11s %-32s %5d %5d %9.4f %9.4f"
              % (line, provider, shown[:32], done, left, spent[line], cost_left))

    print()
    worst = 0
    for provider, credit in CREDIT.items():
        s, l = per_provider_spent[provider], per_provider_left[provider]
        total, margin = s + l, credit - s - l
        frac = margin / credit if credit else 0.0
        if margin < 0:
            state, code = "*** SHORTFALL ***", 2
        elif frac < WARN_FRACTION:
            state, code = "TIGHT", 1
        else:
            state, code = "comfortable", 0
        worst = max(worst, code)
        print("%-11s spent $%6.2f  + still to author $%6.2f  = $%6.2f   credited $%6.2f   "
              "margin $%+7.2f (%+.0f%%)  %s"
              % (provider, s, l, total, credit, margin, 100 * frac, state))

    print()
    print("NOTE: credits are LEDGER ESTIMATES from the 2026-07-28 console quotes, not balance")
    print("      readings. C4 needs no LLM calls, so authoring is the whole remaining exposure.")
    if worst == 2:
        print("ACTION: top up before the projected shortfall is reached. If a key runs dry mid-run the")
        print("        line stops — and for `c1` that is the CONFIRMATORY author.")
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
