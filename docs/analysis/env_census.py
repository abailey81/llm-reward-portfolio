"""EXHAUSTIVE PROVENANCE CENSUS -- every env.json, every key, across the whole archive.

CLAUDE.md, PRIORITY 5 and the DETERMINISM ENVELOPE: "Anything that changes floating-point
arithmetic is part of the FROZEN DESIGN, not an ops detail" -- device, thread counts, BLAS
parallelism, torch.compile, fp16/tf32, fused optimisers, batch/buffer sizes, library
versions, and every provider/quantisation/reasoning pin -- and "every determinism-relevant
fact is RECORDED in the per-record provenance, so a violation is DETECTABLE BY AUDIT".

That is the promise. This is the audit. Session 3 diffed ONE PAIR of env.json files (s14 vs
s13, 2 differing keys of 156). Nobody has censused all of them.

  PASS A  GLOBAL: for every key path, how many distinct values across the whole archive?
          Any determinism-relevant key with >1 value is a Priority-5 finding.
  PASS B  PER COMPARISON UNIT: is the envelope constant inside each CRN unit? This is the
          ratified `cpu_randomised_device_block` premise generalised from the CPU model to
          EVERY recorded environment fact -- pairing is across seeds within a unit, so the
          whole envelope must cancel there, not just the device.
  PASS C  COVERAGE: which records have no env.json at all (a provenance hole is as bad as
          a violation, because it is undetectable rather than merely wrong).

Read-only, effect-blind.  python docs/analysis/env_census.py [--selftest]
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARCHIVE = REPO / "outputs" / "campaign_cluster_run4"

#: Key fragments whose variation changes floating-point arithmetic or invalidates a pin.
#: Matched case-insensitively against the full dotted key path.
DETERMINISM_KEYS = (
    "cpu", "device", "thread", "blas", "mkl", "omp", "torch", "cuda", "cudnn", "compile",
    "fp16", "tf32", "amp", "optim", "batch", "buffer", "seed", "numpy", "python",
    "platform", "glibc", "version", "quant", "provider", "reason", "gpu", "sha", "hash",
)


#: The record's OWN `seed` field varies across seed replicates BY DESIGN — that is the seed
#: ladder, not an envelope violation. Excluded explicitly so the "seed" fragment can still
#: match PYTHONHASHSEED, which IS envelope-relevant.
NOT_ENVELOPE = {"seed"}

#: FINDINGS ALREADY MEASURED, REPORTED AND DISCLOSED. They are still PRINTED every run, but
#: they do not set the CRITICAL verdict — otherwise this instrument reads CRITICAL forever on
#: known conditions and a NEW violation becomes invisible in the verdict line. An alarm that
#: always fires is not an alarm (coord's W4 saturation lesson, 2026-08-01).
#: ⚠ ADDING A KEY HERE IS AN ASSERTION THAT IT IS UNDERSTOOD AND WRITTEN UP. Do not use it to
#: silence something inconvenient — every entry names its finding and date.
ACKNOWLEDGED = {
    # A70 (2026-08-01): the packed cluster path archives from the PARENT, which never ran
    # `_worker_init`, so these five understate the hardening the WORKERS actually applied
    # (`set_global_seed(..., deterministic_torch=True)` at parallel.py:368 / test_leg.py:292).
    # Search runs --search-pack 1 (inline, truthful); test runs --pack 8 (parent-captured).
    "torch_cuda.deterministic_algorithms_enabled",
    "determinism_env.PYTHONHASHSEED",
    "determinism_env.CUBLAS_WORKSPACE_CONFIG",
    "torch_cuda.float32_matmul_precision",
    "torch_cuda.matmul_allow_tf32",
    # A72 (2026-08-01): DECLARED thread asymmetry — `--search-threads 8` vs
    # `--cores-per-training 1`. The tiers are never CRN-paired with each other and each is
    # internally uniform. Disclosed; the write-up says "uniform WITHIN EACH TIER".
    "determinism_env.OMP_NUM_THREADS", "determinism_env.MKL_NUM_THREADS",
    "determinism_env.OPENBLAS_NUM_THREADS", "determinism_env.NUMEXPR_NUM_THREADS",
    "torch_cuda.num_threads", "torch_cuda.num_interop_threads",
    # A71 (2026-08-01): kernel PATCH level (…1160.147 vs …1160.149). Does not change
    # userspace floating-point arithmetic; search units are not CRN-paired across seeds.
    "platform",
}

#: (unit, key) INSTANCES acknowledged for the PER-UNIT pass. Instance-level, never key-level:
#: a NEW unit -- or any OTHER key splitting inside a unit -- still escalates to CRITICAL.
#: A71 (2026-08-01): eight SEARCH units span two kernel patch levels (…1160.147 / …1160.149).
#: Search candidates are one seed each and are not CRN-paired across seeds, and a kernel patch
#: level does not change userspace floating-point arithmetic.
#: ⚠ Adding a row asserts the instance is understood and written up -- never to quiet noise.
ACKNOWLEDGED_UNIT_SPLITS = {
    ("search_leg_deepseek_v4_pro/distributional", "platform"),
    ("search_leg_deepseek_v4_pro/scalar", "platform"),
    ("search_leg_gemini_2_5_flash/scalar_cvar5", "platform"),
    ("search_leg_haiku_4_5/scalar", "platform"),
    ("search_leg_haiku_4_5/scalar_cvar5", "platform"),
    ("search_leg_nemotron_3_super/scalar", "platform"),
    ("search_leg_sonnet_5/distributional", "platform"),
    ("search_leg_sonnet_5/placebo_shuffled", "platform"),
}


def is_determinism_relevant(path: str) -> bool:
    if path in NOT_ENVELOPE:
        return False
    p = path.lower()
    return any(k in p for k in DETERMINISM_KEYS)


def flatten(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from flatten(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        yield prefix, json.dumps(obj, sort_keys=True)[:400]
    else:
        yield prefix, obj


def unit_of(rel: Path) -> str:
    parts = rel.parts
    return f"{parts[0]}/{parts[1]}" if len(parts) >= 2 else parts[0]


def _excluded(rel: Path) -> bool:
    """Reject non-record env.json files.

    ``_env/`` is the WINDOWS LAUNCHER SIDECAR — one per (tier, arm), written by the
    submitting laptop, not by a training. Counting it as a record is the single most
    repeated error in this codebase (s3's A2 "the 20 AMD64/16-core entries are the _env
    launcher sidecars"; ops' M196 "rglob sweeping the _env LAUNCHER SIDECAR"; the P150
    correction). It carries Windows/AMD64/16-core/cuda_available=True values that will
    masquerade as a determinism-envelope violation in EVERY unit it appears in.
    """
    return rel.parts[0].startswith(".pull_tmp") or "_env" in rel.parts


def scan(root: Path) -> dict:
    glob_vals: defaultdict[str, Counter] = defaultdict(Counter)
    per_unit: defaultdict[str, defaultdict[str, set]] = defaultdict(lambda: defaultdict(set))
    n_env = 0
    n_sidecar = 0
    env_dirs, rec_dirs = set(), set()
    for p in root.rglob("record.json"):
        rel = p.relative_to(root)
        # `frozen*/<arm>-winner/` holds a COPY of the winning search record as a marker; no
        # training ran there, so it legitimately has no env.json. Counting those 45 markers
        # as provenance holes is the frozen-marker miscount that has now bitten four lanes
        # (coord's phantom "1", ops' M196, s4's P140).
        if _excluded(rel) or rel.parts[0].startswith("frozen"):
            continue
        rec_dirs.add(p.parent)
    for p in root.rglob("env.json"):
        rel = p.relative_to(root)
        if _excluded(rel):
            n_sidecar += 1
            continue
        env_dirs.add(p.parent)
        try:
            e = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        n_env += 1
        u = unit_of(rel)
        for path, val in flatten(e):
            try:
                key = val if isinstance(val, (str, int, float, bool, type(None))) else str(val)
            except Exception:
                key = "<unhashable>"
            glob_vals[path][key] += 1
            per_unit[u][path].add(key)
    return {"glob": glob_vals, "per_unit": per_unit, "n_env": n_env,
            "n_sidecar": n_sidecar,
            "missing_env": sorted(d for d in rec_dirs if d not in env_dirs)}


def report(res: dict) -> int:
    rc = 0
    g = res["glob"]
    print(f"=== PROVENANCE CENSUS — {res['n_env']} TRAINING env.json files, "
          f"{len(g)} distinct key paths ===")
    print(f"    ({res['n_sidecar']} `_env/` LAUNCHER SIDECARS excluded — they are written by "
          f"the submitting\n     Windows laptop, not by a training, and counting them "
          f"fabricates an envelope violation)")

    varying = {k: v for k, v in g.items() if len(v) > 1}
    det_varying = {k: v for k, v in varying.items() if is_determinism_relevant(k)}
    print("\n--- PASS A: GLOBAL ---")
    print(f"  constant across the WHOLE archive : {len(g) - len(varying)} key(s)")
    print(f"  varying                            : {len(varying)} key(s)")
    print(f"  of which DETERMINISM-RELEVANT      : {len(det_varying)}")
    new_varying = {k: v for k, v in det_varying.items() if k not in ACKNOWLEDGED}
    if det_varying:
        print(f"\n  determinism-relevant keys that VARY — {len(det_varying)} total, "
              f"{len(det_varying) - len(new_varying)} ACKNOWLEDGED, "
              f"{len(new_varying)} NEW:")
        for k in sorted(det_varying, key=lambda k: -len(g[k])):
            vals = g[k]
            shown = ", ".join(f"{repr(v)[:40]}x{n}" for v, n in vals.most_common(4))
            tag = "  [known: A70/A71/A72]" if k in ACKNOWLEDGED else "  *** NEW ***"
            print(f"    {k:<46} {len(vals):>4} distinct  {shown}{tag}")
        if new_varying:
            rc = max(rc, 1)
    else:
        print("  NONE — every determinism-relevant key is globally constant")

    if varying and not det_varying:
        print("\n  varying but NOT determinism-relevant (expected to differ per record):")
        for k in sorted(varying)[:20]:
            print(f"    {k:<46} {len(g[k])} distinct")

    print("\n--- PASS B: PER COMPARISON UNIT (the CRN pairing scope) ---")
    # ⚠⚠ THE KEY-LEVEL `ACKNOWLEDGED` SET IS **NOT** CONSULTED HERE, AND THAT IS DELIBERATE.
    # The 12 acknowledged keys were acknowledged for ONE observed partition: the SEARCH tier
    # differs from the TEST tier (A70/A72). That says nothing about the same key varying
    # *WITHIN a single comparison unit* -- which is the D16 shape and a genuine violation of
    # the ratified `cpu_randomised_device_block` premise. Suppressing it here would silence
    # exactly the event this pass exists to catch.
    # Found by the false-negative audit (docs/analysis/suppression_audit.py, S1b), applying
    # coord's M268 method to this lane's own suppressions: a noise fix is only right if it
    # cannot also silence a real event. The earlier version consulted ACKNOWLEDGED and was
    # SILENT on an injected within-unit split.
    # Acknowledgement here is at the (UNIT, KEY) **INSTANCE** level, never the key class --
    # so the eight known kernel-patch units stay quiet while a NEW unit, or ANY other key
    # splitting inside a unit, escalates. Key-level acknowledgement was a false negative (S1b);
    # no acknowledgement at all was a false positive on a known-benign condition. Instance
    # level is the only setting that is neither.
    offenders, novel = [], []
    for unit, fields in sorted(res["per_unit"].items()):
        bad = {k: v for k, v in fields.items()
               if len(v) > 1 and is_determinism_relevant(k)}
        if bad:
            offenders.append((unit, bad))
            fresh = {k: v for k, v in bad.items()
                     if (unit, k) not in ACKNOWLEDGED_UNIT_SPLITS}
            if fresh:
                novel.append((unit, fresh))
    if offenders:
        print(f"  {len(offenders)} unit(s) inhomogeneous; {len(novel)} NOT previously "
              f"acknowledged at the (unit, key) level")
        for unit, bad in offenders[:20]:
            for k, v in list(bad.items())[:4]:
                vals = ", ".join(repr(x)[:40] for x in list(v)[:3])
                tag = ("  *** NEW ***" if (unit, k) not in ACKNOWLEDGED_UNIT_SPLITS
                       else "  [known: A71 kernel patch level]")
                print(f"     {unit:<46}{k:<30}{len(v)} values: {vals}{tag}")
        if novel:
            rc = 2
    else:
        print("  CLEAN — every comparison unit is homogeneous on every determinism-relevant key")

    print("\n--- PASS C: COVERAGE ---")
    miss = res["missing_env"]
    if miss:
        rc = max(rc, 1)
        print(f"  !! {len(miss)} record director(ies) carry NO env.json (provenance hole):")
        for d in miss[:15]:
            print(f"     {d}")
    else:
        print("  CLEAN — every record directory carries an env.json")

    print(f"\n  VERDICT: {'CRITICAL' if rc == 2 else 'REVIEW' if rc == 1 else 'CLEAN'}")
    return rc


def _selftest() -> int:
    import shutil
    import tempfile
    ok = True

    def case(name, cond):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok = ok and cond

    case("determinism filter catches a cpu key", is_determinism_relevant("cpu.model_name"))
    case("determinism filter catches thread counts", is_determinism_relevant("env.OMP_NUM_THREADS"))
    case("determinism filter catches a torch version", is_determinism_relevant("versions.torch"))
    case("determinism filter ignores an unrelated key",
         not is_determinism_relevant("run.started_at"))
    case("flatten renders a list as a stable string",
         dict(flatten({"a": [1, 2]}))["a"] == "[1, 2]")

    tmp = Path(tempfile.mkdtemp(prefix="envcensus_"))
    try:
        def w(unit, rid, env, with_rec=True):
            d = tmp / "test" / unit / rid
            d.mkdir(parents=True)
            if with_rec:
                (d / "record.json").write_text("{}", encoding="utf-8")
            if env is not None:
                (d / "env.json").write_text(json.dumps(env), encoding="utf-8")

        base = {"cpu": {"model_name": "X"}, "versions": {"torch": "2.6.0"}, "t": 1}
        w("u1", "u1-s0", base)
        w("u1", "u1-s1", base)
        r = scan(tmp)
        case("clean fixture SEEN (denominator non-zero)", r["n_env"] == 2)
        case("clean fixture -> no varying determinism key",
             not [k for k, v in r["glob"].items() if len(v) > 1 and is_determinism_relevant(k)])
        case("clean fixture -> no coverage hole", not r["missing_env"])

        w("u1", "u1-s2", {"cpu": {"model_name": "Y"}, "versions": {"torch": "2.6.0"}, "t": 1})
        r = scan(tmp)
        case("PASS A FIRES on a varying determinism key",
             any(len(v) > 1 and is_determinism_relevant(k) for k, v in r["glob"].items()))
        case("PASS B FIRES on a heterogeneous comparison unit",
             len(r["per_unit"]["test/u1"]["cpu.model_name"]) > 1)

        w("u2", "u2-s0", None)                       # record with no env.json
        r = scan(tmp)
        case("PASS C FIRES on a missing env.json", len(r["missing_env"]) == 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\nselftest: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    raise SystemExit(report(scan(ARCHIVE)))
