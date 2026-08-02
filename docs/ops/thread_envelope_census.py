"""THREAD/DETERMINISM-ENVELOPE CENSUS across the RUN 4 archive -- BLIND to every outcome.

WHY (RUN 13, 2026-08-02). Measured live on the cluster: a SEARCH job (`-pe smp 8`, pack 1) burns
cpu=104 h against 12.35 h of wall -- a ratio of 8.45, i.e. EIGHT threads for ONE training -- while a
TEST job (`-pe smp 8`, pack 8) burns cpu=68 h against 8.38 h -- a ratio of 8.13, i.e. ONE thread per
training. Thread count changes BLAS reduction order, which is inside the FROZEN determinism envelope
(CLAUDE.md -> REPRODUCIBILITY §1). The execution record separately states "2,041/2,041 records
single-substrate (search 1,450 + test 591)". Those two statements cannot both be about the same
quantity, so one of them is about something else -- and the rule is that when two derivations
disagree you STOP and measure rather than pick the comfortable one.

WHAT IT PROVES (or refutes): whether the archived determinism provenance is HOMOGENEOUS *within*
each stage and, decisively, *within each comparison unit*. Homogeneous-within-unit is what every
paired contrast actually needs. A search-vs-test difference is legitimate on its face -- a test leg
is a FRESH training of the frozen reward, so no search-stage float ever reaches a test number -- but
it must be MEASURED and DISCLOSED rather than assumed, because the reproducibility priority makes a
knowingly-unstated envelope difference a defect.

[WARN] FIRST VERSION OF THIS SCRIPT RETURNED "None" FOR ALL 2,980 RECORDS. That was a claim about the
script, not the archive: the provenance does not live in `record.json` at all, it lives in the
sibling `env.json` (`record.json` carries only `env_fingerprint.env_json_sha256`). Recorded because
the surprising-negative rule earned it.

BLINDING. Reads ONLY `env.json` -- never `record.json`'s metrics, `test_returns` or `per_period_pnl`.
The unit name is used for grouping and is printed; no outcome value is loaded, printed or compared.
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

DET_KEYS = ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "PYTHONHASHSEED", "CUBLAS_WORKSPACE_CONFIG",
            "CUDA_VISIBLE_DEVICES")

root = Path(sys.argv[1] if len(sys.argv) > 1 else "outputs/campaign_cluster_run4")


def stage_of(p: Path) -> str:
    names = [q.name for q in p.parents]
    for nm in names:
        if nm.startswith("search"):
            return "search"
        if nm.startswith("test"):
            return "test"
        if nm.startswith("frozen"):
            return "frozen"
    return "other"


by_stage: dict[str, Counter] = defaultdict(Counter)
cpu_by_stage: dict[str, Counter] = defaultdict(Counter)
det_by_stage: dict[str, Counter] = defaultdict(Counter)
unit_threads: dict[str, set] = defaultdict(set)
unit_cpu: dict[str, set] = defaultdict(set)
n = missing = 0

for env_path in root.rglob("env.json"):
    s = str(env_path)
    if ".pull_tmp" in s or "_quarantined" in s:
        continue
    # A unit directory carries an `_env/` STORE whose env.json is a container, not a training, and
    # its determinism vector is all-null. Counting it produced a false "32 units with MIXED thread
    # counts" on this script's first correct run -- ZERO/ABSENT/LAUNCHED again, in my own instrument.
    # The discriminator is a sibling `record.json`: no record, no training.
    if env_path.parent.name == "_env" or not (env_path.parent / "record.json").exists():
        continue
    try:
        d = json.loads(env_path.read_text(encoding="utf-8"))
    except Exception:
        continue
    n += 1
    det = d.get("determinism_env") or {}
    cpu = (d.get("cpu") or {}).get("model_name")
    thr = det.get("OMP_NUM_THREADS")
    if thr is None:
        missing += 1
    st = stage_of(env_path)
    by_stage[st][str(thr)] += 1
    cpu_by_stage[st][str(cpu)] += 1
    det_by_stage[st][json.dumps({k: det.get(k) for k in DET_KEYS}, sort_keys=True)] += 1
    unit = str(env_path.parent.parent)          # the COMPARISON UNIT directory
    unit_threads[unit].add(str(thr))
    unit_cpu[unit].add(str(cpu))

print(f"env.json files scanned: {n}   (no OMP_NUM_THREADS: {missing})")
print()
print("(1) THREADS BY STAGE -- the search-vs-test question")
for st in sorted(by_stage):
    print(f"   {st:8s} {dict(by_stage[st])}")
print()
print("(2) CPU MODEL BY STAGE -- the substrate question, independently")
for st in sorted(cpu_by_stage):
    print(f"   {st:8s} {dict(cpu_by_stage[st])}")
print()
print("(3) FULL DETERMINISM VECTOR -- distinct settings per stage")
for st in sorted(det_by_stage):
    print(f"   {st}:")
    for vec, c in det_by_stage[st].most_common():
        print(f"      n={c:5d}  {vec}")
print()
mt = {u: v for u, v in unit_threads.items() if len(v) > 1}
mc = {u: v for u, v in unit_cpu.items() if len(v) > 1}
print(f"(4) UNITS WITH MIXED THREAD COUNTS  (fatal for CRN pairing): {len(mt)}")
for u, v in list(mt.items())[:10]:
    print(f"      {sorted(v)}  {u}")
print(f"(5) UNITS WITH MIXED CPU MODELS     (fatal for CRN pairing): {len(mc)}")
for u, v in list(mc.items())[:10]:
    print(f"      {sorted(v)}  {u}")
