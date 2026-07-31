"""Characterise the NON-STANDARD JSON tokens in the archive, by FIELD and by LANE.

WHY THIS MATTERS. `NaN` / `Infinity` / `-Infinity` are NOT part of JSON (RFC 8259). Python's
`json.load` accepts them by default, so nothing in our own pipeline notices -- but a STRICT parser
rejects the file outright, verified: `json.loads(..., parse_constant=raise)` fails on these records.
Go's encoding/json, Rust serde_json, JavaScript JSON.parse and R jsonlite all reject bare NaN.

Reproducibility is Stefan's criterion #3 ("THE critical point") and Tamer's #1. The artifact is meant
to be re-analysable BY ANYONE, and 367 records that a standard parser refuses to read is a real
(if low-severity) obstacle to exactly that. It is NOT a science defect -- no number is wrong.

This prints exactly WHICH fields and HOW MANY, so the fix can be scoped precisely rather than guessed.
"""
import glob
import json
import math
import os
from collections import Counter, defaultdict

ROOT = "outputs/campaign_cluster_run4"

field_counts = Counter()
lane_counts = Counter()
files_affected = set()
token_counts = Counter()


def walk(obj, prefix, path, lane):
    """Recursively find non-finite floats and record their dotted field path."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, f"{prefix}.{k}" if prefix else k, path, lane)
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, (int, float)) and not math.isfinite(v):
                field_counts[prefix + "[]"] += 1
                files_affected.add(path)
                lane_counts[lane] += 1
                token_counts["nan" if math.isnan(v) else "inf"] += 1
                return          # one report per list is enough
            if isinstance(v, (dict, list)):
                walk(v, prefix + "[]", path, lane)
    elif isinstance(obj, float) and not math.isfinite(obj):
        field_counts[prefix] += 1
        files_affected.add(path)
        lane_counts[lane] += 1
        token_counts["nan" if math.isnan(obj) else "inf"] += 1


for rec_path in glob.glob(os.path.join(ROOT, "**", "record.json"), recursive=True):
    norm = rec_path.replace("\\", "/")
    if "/.pull_tmp" in norm:
        continue
    lane = ("frozen" if "/frozen" in norm else
            "search" if "/search" in norm else
            "test" if "/test" in norm else "other")
    try:
        rec = json.load(open(rec_path, encoding="utf-8"))
    except Exception:
        continue
    walk(rec, "", norm, lane)

print(f"record.json files containing a non-standard JSON token: {len(files_affected)}")
print(f"token kinds: {dict(token_counts)}")
print()
print("by FIELD:")
for f, c in field_counts.most_common(20):
    print(f"   {c:6d}  {f}")
print()
print("by LANE (file-level occurrences):")
for l, c in lane_counts.most_common():
    print(f"   {c:6d}  {l}")
print()
print("IMPACT: a strict RFC-8259 parser rejects each of these files outright.")
print("        Our own pipeline is unaffected (Python json is permissive by default).")
