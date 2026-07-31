"""COUNT BASE-PROMPT RE-AUTHORINGS at generation >= 1, across every arm and line.

FOUND INCIDENTALLY (record s.66) while re-deriving construct validity: two `scalar_cvar5` prompts at
generation 3 on the qwen3.5-9b leg carry NO CVaR number. The cause is not a leak or a rendering bug --
those two prompts are the BASE prompt ("Here is the environment interface and the reward contract",
~2.6 kB) rather than a reflection prompt ("Reflect on the previous candidate's results", ~0.4 kB).
With no accepted prior candidate to reflect on, the loop re-authors from base. On the capability-
gradient BOTTOM anchor (qwen3.5-9b, ~92 % reject rate) that is expected behaviour.

WHY IT IS WORTH COUNTING ANYWAY. A base-prompt re-authoring is NOT a generation-g reflection
candidate -- it is effectively a SINGLE-SHOT candidate sitting inside an iterative arm. That is
harmless on a report-only leg, but on the CORE line it would dilute exactly the iterative-vs-
single-shot contrast H3 measures, and nothing currently counts them.

The tail-label check can only SEE this in `scalar_cvar5` (in `scalar`/`placebo` zero tail labels is
the expected reading either way), so it must be counted directly.
"""
import glob
import json
import os
from collections import defaultdict

ROOT = "outputs/campaign_cluster_run4"
ARMS = ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")
BASE_MARK = "Here is the environment interface and the reward contract"
REFLECT_MARK = "Reflect on the previous candidate's results"

per_line = defaultdict(lambda: defaultdict(int))
totals = defaultdict(int)
rows = []

for rec_path in glob.glob(os.path.join(ROOT, "search*", "**", "record.json"), recursive=True):
    norm = rec_path.replace("\\", "/")
    if "/.pull_tmp" in norm:
        continue
    try:
        rec = json.load(open(rec_path, encoding="utf-8"))
    except Exception:
        continue
    arm = rec.get("arm")
    gen = rec.get("generation")
    if arm not in ARMS or not isinstance(gen, int) or gen < 1:
        continue
    ppath = os.path.join(os.path.dirname(rec_path), "prompt.txt")
    if not os.path.exists(ppath):
        continue
    text = open(ppath, encoding="utf-8", errors="replace").read()

    parts = norm.split("/")
    line = next((("core" if p == "search" else p[len("search_"):])
                 for p in parts if p.startswith("search")), "?")

    totals["gen>=1 prompts"] += 1
    is_base = BASE_MARK in text
    is_reflect = REFLECT_MARK in text
    if is_base and not is_reflect:
        totals["BASE re-authoring"] += 1
        per_line[line][arm] += 1
        rows.append((line, arm, rec.get("candidate_id"), gen, len(text)))
    elif is_reflect:
        totals["reflection"] += 1
    else:
        totals["UNCLASSIFIED"] += 1

print(f"generation>=1 prompts examined : {totals['gen>=1 prompts']}")
print(f"  reflection prompts           : {totals['reflection']}")
print(f"  BASE re-authorings           : {totals['BASE re-authoring']}")
print(f"  UNCLASSIFIED (neither marker): {totals['UNCLASSIFIED']}  <- should be 0")
print()
if rows:
    print("every base re-authoring at generation >= 1:")
    for line, arm, cid, gen, ln in sorted(rows):
        print(f"   {line:22s} {arm:16s} {cid:24s} gen={gen}  prompt_len={ln}")
print()
core = per_line.get("core", {})
print(f"ON THE CONFIRMATORY CORE LINE : {sum(core.values())} {dict(core) if core else ''}"
      f"   <- must be 0 for H3's iterative contrast to be clean")
