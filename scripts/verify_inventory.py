"""One-shot verified physical inventory for the data requirements report.

Re-hashes EVERY manifested artifact (R4: checksums verified, not trusted), loads each
payload for rows/cols/date-range/ticker coverage, checks provenance sidecars, scans the
layers for unmanifested files (write-once integrity), and byte-checks the frozen D5
split artifacts against PREREGISTRATION §6 literals. Emits JSON to stdout.

Read-only: writes nothing under data/. Run: .venv/bin/python scripts/verify_inventory.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import get  # noqa: E402
from src.data.vault import manifest_entries  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_frame(path: Path, fmt: str) -> pd.DataFrame:
    if fmt == "parquet":
        return pd.read_parquet(path)
    df = pd.read_csv(path, index_col=0)
    try:
        df.index = pd.to_datetime(df.index, format="ISO8601")
    except (ValueError, TypeError):
        pass
    return df


def inventory() -> dict:
    rows, failures = [], []
    seen_paths = set()
    for e in manifest_entries():
        path = ROOT / e["relpath"]
        seen_paths.add(path)
        rec = {"name": e["name"], "layer": e["layer"], "rows": e["rows"], "cols": e["cols"],
               "manifest_sha16": e["sha256"][:16]}
        if not path.exists():
            rec["checksum"] = "FAIL: file missing"
            failures.append(rec)
            rows.append(rec)
            continue
        digest = sha256(path)
        rec["checksum"] = "PASS" if digest == e["sha256"] else f"FAIL: on-disk {digest[:16]}"
        if rec["checksum"] != "PASS":
            failures.append(rec)
        sidecar = path.with_suffix(path.suffix + ".provenance.json")
        rec["sidecar"] = sidecar.exists()
        try:
            df = load_frame(path, e["format"])
            if isinstance(df.index, pd.DatetimeIndex) and len(df):
                rec["date_range"] = [str(df.index.min().date()), str(df.index.max().date())]
            cols = [str(c) for c in df.columns]
            rec["n_series"] = len(cols)
            rec["series_sample"] = cols[:6]
        except Exception as ex:  # noqa: BLE001 — inventory must report, not crash
            rec["load_note"] = f"{type(ex).__name__}: {ex}"[:120]
        rows.append(rec)

    # write-once integrity: payload files on disk not present in the manifest
    unmanifested = []
    for layer, rel in get("data.platform.layers").items():
        d = ROOT / rel
        if not d.exists():
            continue
        for p in sorted(d.rglob("*")):
            if p.is_dir() or p.name.endswith(".provenance.json"):
                continue
            if p not in seen_paths:
                unmanifested.append(str(p.relative_to(ROOT)))
    return {"artifacts": rows, "checksum_failures": failures, "unmanifested": unmanifested}


def verify_splits_vs_prereg() -> dict:
    """D5: the F