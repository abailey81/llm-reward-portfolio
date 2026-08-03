"""RFC-8259 EXPORT for the public deposit — closes registry row 42 (record 69.4).

THE DEFECT. 360 archive `record.json` files contain a bare `NaN`, which is **not valid JSON**
(RFC 8259 admits no `NaN`, `Infinity` or `-Infinity`). Python's `json.load` accepts them BY DEFAULT,
which is why nothing in our own pipeline ever complained -- but a strict parser rejects the file
outright, and Go's `encoding/json`, Rust's `serde_json`, JavaScript's `JSON.parse` and R's `jsonlite`
all refuse it. A replicator working in any of those hits a hard parse failure on 360 files BEFORE
reaching any science. Reproducibility is Stefan's criterion #3 ("THE critical point") and Tamer's #1.

Scope, measured: 690 tokens, all `nan` (no Infinity), in exactly TWO fields --
`metrics.train_curve.return[]` (360 files) and `metrics.val_fitness` (330 files) -- ALL on the TEST
lane. ZERO on `search/` and ZERO on `frozen/`, so the confirmatory archive is already compliant.

WHY THIS IS AN EXPORT AND NOT AN IN-PLACE REWRITE -- three reasons, all binding:
  1. THE ARCHIVE IS THE PRIMARY RECORD. Rewriting 360 archived files in place would mutate evidence
     that hashes, guards and the reproducibility claim all rest on. The archive is written once and
     read forever.
  2. IT IS A MIRROR. `pull_archive` re-syncs from the cluster, so an in-place edit would be
     silently reverted -- and worse, INTERMITTENTLY, which is the ugliest failure mode available.
  3. IT IS NOT A SCIENCE DEFECT. Both affected fields are inapplicable-or-diagnostic
     (`train_curve.return` is SB3's rollout return before the first episode completes;
     `val_fitness` has no meaning on a lane with no validation step). No reported number is wrong.

THE CONVENTION, which MUST be stated in the repro checklist beside the deposit:
    a non-finite or inapplicable value is exported as JSON `null`.
    `null` therefore means "not applicable / not finite" -- it does NOT mean zero.

Usage:
    python docs/ops/json_rfc8259_export.py --check          # report only (default)
    python docs/ops/json_rfc8259_export.py --out DIR        # write a compliant COPY of the tree
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys

ROOT = "outputs/campaign_cluster_run4"


def sanitise(obj):
    """Recursively replace non-finite floats with None. Returns (clean_obj, n_replaced)."""
    n = 0
    if isinstance(obj, float):
        if not math.isfinite(obj):
            return None, 1
        return obj, 0
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out[k], c = sanitise(v)
            n += c
        return out, n
    if isinstance(obj, list):
        out = []
        for v in obj:
            cv, c = sanitise(v)
            out.append(cv)
            n += c
        return out, n
    return obj, 0


def strict_loads(text: str):
    """Parse with RFC-8259 strictness: reject NaN/Infinity instead of silently accepting."""
    def _reject(const):
        raise ValueError(f"non-standard JSON constant: {const}")
    return json.loads(text, parse_constant=_reject)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--out", default=None, help="write a compliant COPY of the tree here")
    ap.add_argument("--check", action="store_true", help="report only (the default)")
    args = ap.parse_args()

    paths = sorted(glob.glob(os.path.join(args.root, "**", "record.json"), recursive=True))
    offending, total_tokens, written = [], 0, 0

    for p in paths:
        raw = open(p, encoding="utf-8").read()
        try:
            strict_loads(raw)
            compliant = True
        except ValueError:
            compliant = False
        if compliant:
            continue
        obj = json.loads(raw)                      # permissive: this is how it was written
        clean, n = sanitise(obj)
        offending.append((p.replace("\\", "/"), n))
        total_tokens += n

        if args.out:
            rel = os.path.relpath(p, args.root)
            dst = os.path.join(args.out, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, "w", encoding="utf-8", newline="") as fh:
                json.dump(clean, fh, allow_nan=False, ensure_ascii=False, indent=None)
            # PROVE the export is compliant, rather than assuming the dump succeeded
            strict_loads(open(dst, encoding="utf-8").read())
            written += 1

    print(f"record.json scanned                     : {len(paths)}")
    print(f"files REJECTED by a strict RFC-8259 parser: {len(offending)}")
    print(f"non-finite tokens within them             : {total_tokens}")
    if offending:
        print("\nfirst few:")
        for p, n in offending[:5]:
            print(f"   {n:4d} token(s)  {p}")
    if args.out:
        print(f"\ncompliant copies written + re-validated  : {written} -> {args.out}")
        print("CONVENTION: null == 'not applicable / not finite', NOT zero. State this in the")
        print("            reproducibility checklist that ships with the deposit.")
    elif offending:
        print("\n(report only; pass --out DIR to write a compliant copy for the deposit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
