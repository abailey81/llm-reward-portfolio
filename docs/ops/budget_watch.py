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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from record_shrink_cache import load_shrunken_records  # noqa: E402
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
#:
#: ⚠ KNOWN IMPRECISION IN THE ANTHROPIC FIGURE, measured 2026-07-31, deliberately NOT "corrected".
#: 28.15 was derived as (the $31.96 quote) − (RUN 3's $3.8136). But RUN 3 predates the D10 fix, so
#: EVERY row in its ledgers is stamped `provider: anthropic`, including the eight OpenRouter legs.
#: Re-attributing RUN 3 by line gives a TRUE Anthropic portion of **$3.1023** (c1 $0, h3ss $2.5107,
#: leg8 $0.4479, leg5 $0.1437) and $0.7114 on OpenRouter — so this constant understates the credit by
#: about $0.71 IF the $31.96 quote was taken before RUN 3 ran, and is right if it was taken after.
#: That timing is not recorded anywhere, so changing the number would trade a documented imprecision
#: for an undocumented guess. It stays as written, with the arithmetic above stated instead — and it
#: is moot in practice: Tamer holds the balance and the top-up decision (his instruction 2026-07-31),
#: so the credit side of this comparison is owner-held and stale by design. The SPEND and PROJECTION
#: columns are ours and are measured; the CREDIT column is an estimate and is labelled as one.
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


def _project(obj):
    """Keep ONLY the two fields this file reads. The cache stores the RESULT of this, so the entry is
    ~60 bytes instead of the ~23 KB a full shrunken record costs — about 1 MB for the whole archive.

    ⚠ IT MUST STAY A PURE FUNCTION OF THE RECORD, because `record_shrink_cache` keys its cache on this
    function's SOURCE: change what is projected and every entry is invalidated and rebuilt, which is
    the intended behaviour and the reason a stale cache cannot outlive its definition.
    """
    if isinstance(obj, dict):
        return {"arm": obj.get("arm"), "generation": obj.get("generation")}
    return {}


def _generation_depth() -> dict[str, dict[str, int]]:
    """Deepest generation reached per (archive root, arm).

    ⚠⚠ SWEEP-1, SECOND APPLICATION, 2026-08-05. THIS FUNCTION WAS A THIRD FULL-ARCHIVE WALKER AND IT
    WAS THE ONE STILL BREAKING THE CYCLE. It ran `glob.glob(ROOT/**/record.json)` and `json.load` on
    every record, against `cycle.py`'s 180 s timeout, so the board read `budget=99` — "that number is
    BLIND this cycle" — on most cycles once the archive passed ~18,000 records. **The W6 row blamed a
    spend-ledger scan; the ledgers are STATIC at 2,956 rows and the spend has not moved since C1
    closed. It was always this walk.** Measured live at 2026-08-05 22:11:49Z: a 998.6 s sweep with
    1,029 s between cycle lines, on a loop I had just observed executing `budget_watch` — i.e. the
    false-DEAD condition, ALIVE, with `science_watch` and `results_audit` already cached down to
    seconds. **SWEEP-1 did not close that on its own.**

    ⚠ THE ONE BEHAVIOURAL DIFFERENCE, MEASURED RATHER THAN ASSUMED TO BE HARMLESS. This walk excluded
    NOTHING; the cache excludes `.pull_tmp*` and `_quarantined*`. Measured on the live archive:
    `_quarantined*` is **0 directories and 0 records**, and `.pull_tmp*` is **3 records, all with the
    `.pull_tmp` directory as their FIRST path segment**. Those three can therefore only ever key into
    roots named `.pull_tmp.28884` / `.pull_tmp.34624` — and `main()` iterates the FIXED `LINES`
    registry and reads `depth.get(root, {})`, so a root outside that registry is never looked at.
    **The exclusion is provably output-neutral here, and the byte-identity proof against
    `git show HEAD:` confirms it rather than resting on this argument.**
    """
    depth: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(lambda: -1))
    records, _unreadable = load_shrunken_records(ROOT, _project)
    for path, rec in records:
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
        s, left_usd = per_provider_spent[provider], per_provider_left[provider]
        total, margin = s + left_usd, credit - s - left_usd
        frac = margin / credit if credit else 0.0
        # The verdict is stated against the CREDIT ESTIMATE, and says so. It used to read
        # "*** SHORTFALL ***", which asserts a fact about a balance this script cannot see — and on
        # 2026-07-31 Tamer's answer was that he watches the balance himself and tops up as needed.
        # An alarm raised against an unobservable quantity is the alarm-hygiene failure the whole
        # acknowledged-alarms discipline exists to prevent, so the wording now matches what is
        # actually known. The arithmetic and the exit codes are unchanged.
        if margin < 0:
            state, code = "over the credit ESTIMATE (owner-watched)", 2
        elif frac < WARN_FRACTION:
            state, code = "near the credit ESTIMATE", 1
        else:
            state, code = "comfortable", 0
        worst = max(worst, code)
        # 4 dp, not 2: Tamer's instruction of 2026-07-31 is "I watch the balance -- just make sure you
        # PRECISELY monitor it as well", and at 2 dp a single cycle's spend rounds to zero, so the
        # per-cycle delta the monitor reports would be structurally blind to the thing being watched.
        print("%-11s spent $%8.4f  + still to author $%8.4f  = $%8.4f   credited $%8.4f   "
              "margin $%+9.4f (%+.0f%%)  %s"
              % (provider, s, left_usd, total, credit, margin, 100 * frac, state))

    print()
    print("NOTE: credits are LEDGER ESTIMATES from the 2026-07-28 console quotes, not balance")
    print("      readings. C4 needs no LLM calls, so authoring is the whole remaining exposure.")
    if worst == 2:
        print("OWNER: Tamer watches the real balance and tops up as needed (2026-07-31). The figure to")
        print("       track is `still to author` on anthropic - the CONFIRMATORY line's exposure.")
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
