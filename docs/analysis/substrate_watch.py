"""SUBSTRATE WATCH -- has the campaign landed on hardware we have not verified?

WHY THIS EXISTS (analysis lane, session 5, 2026-08-01). Ops is deepening cluster
submission to raise throughput. Deeper submission reaches nodes we have never used.
`cpu_randomised_device_block` is a RATIFIED premise -- "every CRN comparison unit stays
device-HOMOGENEOUS (seed-pool blocks), so the device cancels in each paired difference"
-- and D16 already cost a both-sides quarantine plus a re-run when four seeds landed on
a second CPU model. RUN 4's archive is currently 2,488/2,488 Intel Xeon Gold 6240, ONE
model: that homogeneity is the strongest determinism evidence in the campaign and it can
be spent by accident.

MEASURED BASELINE (session 5): RUN 4's 1,821 host-stamped task-runs landed on exactly
187 distinct nodes -- d00a x178, d00b x9, nothing else. We have NEVER run on d97a, d97b,
e00a, b00a, l00a or t00a, and `-ac allow=d` admits d97a/d97b (686 free slots) now that
tmpfs was relaxed 15G -> 1G.

FOUR CHECKS, in decreasing directness:
  C1 CRITICAL  any record whose cpu.model_name is not the reference model
  C2 CRITICAL  any COMPARISON UNIT carrying more than one model (the ratified premise)
  C3 HIGH      any task-run on a host outside the verified families
  C4 INFO      task-runs on nodes new since the baseline (expected as depth grows)

C1/C2 are the ground truth -- they read the archive itself. C3 is the EARLY warning: it
fires when we land somewhere new, before that node's records are even written.

Read-only. Effect-blind: CPU strings, hostnames, unit paths. No outcome field is read.
Usage:  python docs/analysis/substrate_watch.py [--selftest]
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUTPUTS = REPO / "outputs"
RUN = "campaign_cluster_run4"
REFERENCE_MODEL = "Intel(R) Xeon(R) Gold 6240 CPU @ 2.60GHz"
VERIFIED_FAMILIES = {"d00a", "d00b"}
BASELINE_NODE_COUNT = 187
HOST_RE = re.compile(r"^node-([a-z]\d{2}[a-z])-(\d+)")


def _cpu_of(env_path: Path) -> str | None:
    try:
        d = json.loads(env_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    m = ((d.get("cpu") or {}).get("model_name") or "").strip()
    return m or None


def _comparison_unit(rel: Path) -> str | None:
    """The CRN comparison unit a record belongs to: <tier>/<unit>.

    Pairing happens across seeds WITHIN a unit, so that is the scope over which the
    device must be constant. Search-tier records are not paired across seeds and are
    excluded rather than silently folded in.
    """
    parts = rel.parts
    if len(parts) < 3 or not parts[0].startswith("test"):
        return None
    return f"{parts[0]}/{parts[1]}"


def scan(root: Path) -> dict:
    models: Counter[str] = Counter()
    offenders: list[tuple[str, str]] = []
    per_unit: defaultdict[str, set[str]] = defaultdict(set)

    for env_p in root.rglob("env.json"):
        rel = env_p.relative_to(root)
        if rel.parts[0].startswith(".pull_tmp"):
            continue
        cpu = _cpu_of(env_p)
        if cpu is None:
            continue
        models[cpu] += 1
        if cpu != REFERENCE_MODEL:
            offenders.append((str(rel), cpu))
        unit = _comparison_unit(rel)
        if unit:
            per_unit[unit].add(cpu)

    mixed = {u: sorted(c) for u, c in per_unit.items() if len(c) > 1}

    hosts: Counter[str] = Counter()
    foreign: list[tuple[str, int, str]] = []
    led = root / "ledger"
    if led.is_dir():
        for p in led.glob("*.epilogue.jsonl"):
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                host = str(d.get("host", "")).split(".")[0]
                if not host:
                    continue
                hosts[host] += 1
                m = HOST_RE.match(host)
                fam = m.group(1) if m else "?"
                if fam not in VERIFIED_FAMILIES:
                    foreign.append((p.name.replace(".epilogue.jsonl", ""),
                                    int(d.get("task", -1)), host))

    return {"models": models, "offenders": offenders, "mixed_units": mixed,
            "hosts": hosts, "foreign": foreign}


def report(res: dict) -> int:
    rc = 0
    print("=== SUBSTRATE WATCH ===")
    print(f"  reference model : {REFERENCE_MODEL}")
    total = sum(res["models"].values())
    print(f"  records w/ cpu  : {total} across {len(res['models'])} distinct model(s)")
    for m, n in res["models"].most_common():
        print(f"      {n:>6}  {m}")

    if res["offenders"]:
        rc = 2
        print(f"\n  !! C1 CRITICAL -- {len(res['offenders'])} record(s) on a NON-REFERENCE CPU:")
        for rel, cpu in res["offenders"][:20]:
            print(f"       {rel}  ->  {cpu}")
    else:
        print("\n  C1 OK -- every record is on the reference model")

    if res["mixed_units"]:
        rc = 2
        print(f"\n  !! C2 CRITICAL -- {len(res['mixed_units'])} COMPARISON UNIT(S) span >1 model")
        print("     (this is the ratified cpu_randomised_device_block premise breaking)")
        for u, cs in list(res["mixed_units"].items())[:20]:
            print(f"       {u}: {cs}")
    else:
        print("  C2 OK -- no comparison unit spans more than one CPU model")

    if res["foreign"]:
        rc = max(rc, 1)
        fams = Counter(HOST_RE.match(h).group(1) if HOST_RE.match(h) else "?"
                       for _, _, h in res["foreign"])
        print(f"\n  ! C3 HIGH -- {len(res['foreign'])} task-run(s) on UNVERIFIED families {dict(fams)}")
        for batch, task, host in res["foreign"][:20]:
            print(f"       {host}  batch={batch} task={task}")
        print("     -> check those hosts' CPU model before trusting their records")
    else:
        print(f"  C3 OK -- all task-runs on verified families {sorted(VERIFIED_FAMILIES)}")

    n_nodes = len(res["hosts"])
    delta = n_nodes - BASELINE_NODE_COUNT
    print(f"  C4 INFO -- {n_nodes} distinct nodes used "
          f"({delta:+d} vs the {BASELINE_NODE_COUNT}-node session-5 baseline)")
    print(f"\n  VERDICT: {'CRITICAL' if rc == 2 else 'WARN' if rc == 1 else 'CLEAN'}")
    return rc


# --------------------------------------------------------------------------------- #
def _selftest() -> int:
    """Every check must be PROVEN able to fire. A check that cannot fail verifies nothing."""
    import shutil
    import tempfile

    ok = True

    def case(name: str, cond: bool) -> None:
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok = ok and cond

    tmp = Path(tempfile.mkdtemp(prefix="substrate_selftest_"))
    try:
        unit = tmp / "test" / "baseline_x"
        (unit / "baseline_x-s0").mkdir(parents=True)
        (unit / "baseline_x-s1").mkdir(parents=True)
        good = {"cpu": {"model_name": REFERENCE_MODEL}}
        (unit / "baseline_x-s0" / "env.json").write_text(json.dumps(good), encoding="utf-8")
        (unit / "baseline_x-s1" / "env.json").write_text(json.dumps(good), encoding="utf-8")
        led = tmp / "ledger"
        led.mkdir()
        (led / "b1.epilogue.jsonl").write_text(
            json.dumps({"task": 1, "host": "node-d00a-105.myriad.ucl.ac.uk", "rc": 0}) + "\n",
            encoding="utf-8")

        r = scan(tmp)
        case("clean fixture -> no offenders", not r["offenders"])
        case("clean fixture -> no mixed units", not r["mixed_units"])
        case("clean fixture -> no foreign hosts", not r["foreign"])
        case("clean fixture -> the unit IS seen (denominator non-zero)",
             sum(r["models"].values()) == 2)

        # C1 + C2 must fire on an injected second model
        bad = {"cpu": {"model_name": "Intel(R) Xeon(R) Gold 6140 CPU @ 2.30GHz"}}
        (unit / "baseline_x-s1" / "env.json").write_text(json.dumps(bad), encoding="utf-8")
        r = scan(tmp)
        case("C1 FIRES on a non-reference CPU", len(r["offenders"]) == 1)
        case("C2 FIRES on a mixed comparison unit",
             r["mixed_units"].get("test/baseline_x") is not None)

        # C3 must fire on a foreign family
        (led / "b2.epilogue.jsonl").write_text(
            json.dumps({"task": 7, "host": "node-d97a-003.myriad.ucl.ac.uk", "rc": 0}) + "\n",
            encoding="utf-8")
        r = scan(tmp)
        case("C3 FIRES on an unverified family (d97a)",
             any(h.startswith("node-d97a") for _, _, h in r["foreign"]))
        case("C3 does NOT fire on the verified d00a host",
             not any(h.startswith("node-d00a") for _, _, h in r["foreign"]))

        # a SEARCH-tier record must not be treated as a comparison unit
        s = tmp / "search" / "arm" / "cand"
        s.mkdir(parents=True)
        (s / "env.json").write_text(json.dumps(bad), encoding="utf-8")
        r = scan(tmp)
        case("search-tier records are NOT counted as comparison units",
             all(not u.startswith("search") for u in r["mixed_units"]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\nselftest: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    raise SystemExit(report(scan(OUTPUTS / RUN)))
