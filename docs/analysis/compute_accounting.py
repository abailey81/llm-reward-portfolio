"""COMPUTE ACCOUNTING, derived -- because no instrument computes it and the archive says 0.0.

THE GAP (A64, this session):
  * `src/orchestration/test_leg.py:193` writes ``"wall_clock": 0.0`` as a HARDCODED literal,
    so ALL 1,151 test records carry zero. Search records are fine (1,450 distinct values).
  * The sealed TEST leg is ~96 % of all campaign work (ops: 40,328 test trainings vs 1,800
    search), so the zeroed field covers almost the entire compute budget.
  * `scripts/analyze_campaign.py`'s registered ``compute_accounting`` key counts candidates
    attempted/accepted/failed + prompt TOKENS (R35). It contains no reference to wall_clock,
    cpu_hours or core_hours -- grep confirms zero hits.
  * Okhrati explicitly docks marks for missing wall-clock compute reporting (CLAUDE.md,
    authority #2), and the write-up must report it.

THE RECOVERY: the generated job scripts carry an EXIT trap writing {"task","host","rc",
"secs","ts"} per task to <remote>/ledger/<batch>.epilogue.jsonl, and those ledgers ARE
pulled back. ``secs`` is the task's own $SECONDS. Each task held ``-pe smp N`` slots for
that long, and N is parsed from the batch's generated .sh. So:

    task wall-clock = secs                     (elapsed)
    CPU-seconds     = secs * slots             (resource actually consumed)

HONEST BOUNDS, stated rather than buried: this counts tasks whose epilogue line was
written AND pulled. A task still running, or one whose ledger has not been pulled, is not
here -- so every figure is a LOWER BOUND on work completed to date, and the campaign is
live. Coverage is reported alongside every total so the bound is visible.

Read-only, effect-blind (durations, slot counts, exit codes; no outcome touched).
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUNS = ("campaign_cluster_run4", "campaign_cluster_run3", "campaign_cluster")
SMP_RE = re.compile(r"^#\$\s+-pe\s+smp\s+(\d+)", re.M)
PACK_RE = re.compile(r"--pack\s+(\d+)")


def slots_for(run_dir: Path, batch: str, cache: dict) -> tuple[int, int]:
    """(slots, pack) requested by a batch, read from its own generated job script."""
    if batch in cache:
        return cache[batch]
    slots, pack = 0, 0
    d = run_dir / "batches" / batch
    if d.is_dir():
        for sh in d.glob("*.sh"):
            txt = sh.read_text(encoding="utf-8", errors="replace")
            m, p = SMP_RE.search(txt), PACK_RE.search(txt)
            if m:
                slots = int(m.group(1))
            if p:
                pack = int(p.group(1))
            break
    cache[batch] = (slots, pack)
    return slots, pack


# ⚠ THE CONSOLE IS cp1251 AND A NON-ASCII CHARACTER KILLS THE PROCESS. This file died at exit 1
# on a `×` in a print, swallowing its own BOUNDS caveat -- the honesty clause on the number
# `CLAUDE.md` names as the write-up's compute source. My first remedy HUNTED CHARACTERS and missed
# the one on the very next line; the repo already had the right fix, documented at
# `docs/ops/cycle.py:94-100` after the same defect hit live on 2026-07-31. Reconfigure the streams
# instead: this can degrade a CHARACTER but can never lose a MESSAGE.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def tier_of_batch(batch: str) -> str:
    """Which tier did this batch belong to? SEARCH (8-thread DFO) or the sealed TEST leg (1-thread).

    !!!! THIS PUBLISHED AN INVERTED SPLIT, AND `CLAUDE.md` NAMES THIS FILE AS THE SOURCE OF THE
    WRITE-UP'S COMPUTE FIGURE (found 2026-08-04, RUN 21, by the blind-quality-report build).
    The C4 sweep -- the pipelined sealed-test stage, and the LARGEST test population in the
    campaign -- names its batches `<tag>_sweep_t<N>_p<NN>`, which matched none of the old patterns
    and fell through to SEARCH. **MEASURED FIRST-HAND: 1,295 of 3,399 epilogue ledgers, i.e. EVERY
    sweep ledger, were labelled SEARCH.** The printed run-4 split read `SEARCH 3,086 tasks /
    19,886 h` against `TEST 322 / 2,887 h`; the true split is `SEARCH 1,584 rc=0 / 7,358 h` against
    `TEST 1,609 rc=0 / 15,099 h`. **The tiers were essentially transposed.**

    ✔ **GRAND TOTALS AND CPU-HOURS ARE UNAFFECTED** -- every batch requests `-pe smp 8`, verified on
    a sweep, a per-arm and a generation batch -- so this is a TIER-ATTRIBUTION defect, not a
    total-compute one. That distinction matters: the headline compute number this file exists to
    produce was always right, and only its breakdown was wrong.

    !! AND THE "TRUE SPLIT" FIGURE ABOVE WAS QUOTED FROM THE WRONG INSTRUMENT (auditor, same day).
    `SEARCH 1,584 / 7,358 h` is `blind_quality_report`'s section-4 population -- rc==0 tasks ONLY,
    with the canary folded back into SEARCH -- three lines above the paragraph explaining that the
    canary gets its own label so it cannot inflate the search figure. **THIS file does not filter
    rc**, and what it actually prints for run 4 is `SEARCH 1,771 / 7,410.0 h`, `TEST 1,623 /
    15,257.7 h`, `CANARY 23 / 189.1 h`. Both readings are defensible; quoting one file's number in
    another file's docstring is not. The transposition claim is unaffected either way.

    THE RULE IS NOW POSITIVE FOR SEARCH RATHER THAN NEGATIVE FOR TEST. The old form asked "does
    this look like a test batch, else SEARCH", so any unrecognised NEW batch name silently became
    SEARCH -- which is exactly how the sweep was lost. A generation batch is the one that carries a
    `_g<N>` generation index or an explicit search tag; everything on the sealed path is TEST.
    Anything matching NEITHER is returned as UNKNOWN so it appears in the table instead of
    inflating a tier: a batch nobody classified must be visible, not absorbed.
    """
    b = batch.lower()
    # SEALED-TEST tier: the C4 sweep, the per-arm test legs, the H1 baselines, the C2 pair test.
    if ("_sweep_t" in b or "_test" in b or b.endswith("test")
            or "baselines" in b or "h2_pair" in b):
        return "TEST (sealed leg)"
    # SEARCH tier: a generation index `_g<N>_` (or trailing `_g<N>`), or an explicit search tag.
    # `_g<N>` is a leg's generation index; `_c<N>` is the core line's DFO candidate index
    # (`c1_bayes_opt_c10`). The UNKNOWN bucket below surfaced 113 of the latter on the first run,
    # which is exactly what it is for -- an unclassified batch must be VISIBLE, not absorbed into
    # whichever tier the fall-through happens to name.
    # The GO canary is pre-launch throughput calibration. It is neither tier, and folding it into
    # SEARCH would inflate the number the write-up quotes as the campaign's search compute, so it
    # gets its own label. 23 such batches exist.
    if "canary" in b:
        return "CANARY (pre-launch calibration)"
    if (re.search(r"_g(?:en)?\d+(_|$)", b) or re.search(r"_c\d+(_|$)", b) or "_startup" in b
            or "_search" in b or b.endswith("search")):
        return "SEARCH"
    return "UNKNOWN (unclassified batch name)"


def main() -> int:
    grand = defaultdict(lambda: {"tasks": 0, "secs": 0.0, "cpu_s": 0.0,
                                 "no_slots": 0, "rc_nonzero": 0})
    per_run = {}
    for run in RUNS:
        run_dir = REPO / "outputs" / run
        led = run_dir / "ledger"
        if not led.is_dir():
            continue
        cache: dict = {}
        acc = defaultdict(lambda: {"tasks": 0, "secs": 0.0, "cpu_s": 0.0,
                                   "no_slots": 0, "rc_nonzero": 0})
        for p in led.glob("*.epilogue.jsonl"):
            batch = p.name.replace(".epilogue.jsonl", "")
            slots, _pack = slots_for(run_dir, batch, cache)
            tier = tier_of_batch(batch)
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                secs = float(d.get("secs") or 0.0)
                a = acc[tier]
                a["tasks"] += 1
                a["secs"] += secs
                if slots:
                    a["cpu_s"] += secs * slots
                else:
                    a["no_slots"] += 1
                try:
                    if int(d.get("rc", 0)) != 0:
                        a["rc_nonzero"] += 1
                except (TypeError, ValueError):
                    pass
        per_run[run] = acc
        for tier, a in acc.items():
            g = grand[tier]
            for k in ("tasks", "secs", "cpu_s", "no_slots", "rc_nonzero"):
                g[k] += a[k]

    print("=== COMPUTE ACCOUNTING, derived from the epilogue ledgers ===")
    print("    (the archive's per-record wall_clock is HARDCODED 0.0 on the test tier —")
    print("     src/orchestration/test_leg.py:193 — so this is the only available route)\n")
    for run, acc in per_run.items():
        if not acc:
            continue
        print(f"--- {run} ---")
        print(f"  {'tier':<20}{'tasks':>8}{'elapsed h':>13}{'CPU-hours':>14}"
              f"{'rc!=0':>8}{'no slots':>10}")
        for tier in sorted(acc):
            a = acc[tier]
            print(f"  {tier:<20}{a['tasks']:>8}{a['secs']/3600:>13,.1f}"
                  f"{a['cpu_s']/3600:>14,.1f}{a['rc_nonzero']:>8}{a['no_slots']:>10}")
        print()

    print("=== GRAND TOTAL (all runs, all tiers) ===")
    tt = sum(a["tasks"] for a in grand.values())
    ts = sum(a["secs"] for a in grand.values())
    tc = sum(a["cpu_s"] for a in grand.values())
    tn = sum(a["no_slots"] for a in grand.values())
    tr = sum(a["rc_nonzero"] for a in grand.values())
    for tier in sorted(grand):
        a = grand[tier]
        print(f"  {tier:<20}{a['tasks']:>8} tasks{a['secs']/3600:>13,.1f} elapsed-h"
              f"{a['cpu_s']/3600:>14,.1f} CPU-h")
    print(f"  {'TOTAL':<20}{tt:>8} tasks{ts/3600:>13,.1f} elapsed-h{tc/3600:>14,.1f} CPU-h")
    print(f"\n  tasks with a non-zero exit code: {tr}")
    print(f"  tasks whose batch script could not be read for its slot count: {tn}"
          f"  ({'their CPU-hours are EXCLUDED, so the total is a lower bound' if tn else 'none'})")
    print("\n  !! BOUNDS: counts only tasks whose epilogue line was written AND pulled back.")
    print("    Running tasks and un-pulled ledgers are absent, and the campaign is LIVE,")
    print("    so every figure above is a LOWER BOUND on work completed to date.")
    print("    CPU-hours = secs × the batch's `-pe smp N` (slots actually held), not × pack.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
