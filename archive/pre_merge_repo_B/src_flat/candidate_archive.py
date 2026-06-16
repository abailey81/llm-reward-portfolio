"""Append-only verbatim archive of every generated reward candidate (CLAUDE.md R6).

Every candidate — valid, invalid, rejected by the static gate, or crashed — is archived
with its prompt, model snapshot id, temperature, and outcome, under
`config eureka_loop.contract.archive_dir` (data/candidates). Rationale: model drift
makes LLM outputs irreproducible; the verbatim archive is the reproducibility anchor
(and the raw material of the reward-code forensics chapter).

Write-once discipline (R4 applied to the archive): files are never modified or
overwritten — re-archiving the same (arm, iteration, sample) coordinates raises.
Layout per candidate:
    <arm>_i<iter>_s<sample>__<sha16>.py     verbatim source (byte-exact)
    <arm>_i<iter>_s<sample>__<sha16>.json   metadata + outcome
plus one line appended to index.jsonl (the queryable ledger of the archive).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from .config import get

ROOT = Path(__file__).resolve().parent.parent


def candidate_id(source: str) -> str:
    """Content-addressed id: first 16 hex chars of SHA-256 of the verbatim source."""
    return hashlib.sha256(source.encode()).hexdigest()[:16]


def archive_candidate(
    source: str,
    *,
    arm: str,
    iteration: int,
    sample_idx: int,
    prompt: str,
    model_snapshot: str,
    temperature: float,
    outcome: dict,
    archive_dir: str | Path | None = None,
) -> Path:
    """Archive one candidate verbatim. Returns the path of the .py artefact.

    `outcome` is a JSON-serializable dict (e.g. static-gate reason, sandbox result
    summary, fitness if evaluated). Raises FileExistsError on coordinate collision —
    the archive is append-only by construction.
    """
    base = Path(archive_dir) if archive_dir is not None else ROOT / get("eureka_loop.contract.archive_dir")
    base.mkdir(parents=True, exist_ok=True)
    cid = candidate_id(source)
    stem = f"{arm}_i{iteration:02d}_s{sample_idx:02d}__{cid}"
    py_path = base / f"{stem}.py"
    meta_path = base / f"{stem}.json"
    if py_path.exists() or meta_path.exists():
        raise FileExistsError(f"{stem} already archived — the archive is append-only (R6/R4)")

    meta = {
        "candidate_id": cid,
        "arm": arm,
        "iteration": iteration,
        "sample_idx": sample_idx,
        "model_snapshot": model_snapshot,
        "temperature": temperature,
        "prompt": prompt,
        "outcome": outcome,
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    py_path.write_text(source)
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True))
    with open(base / "index.jsonl", "a") as f:
        f.write(json.dumps({"stem": stem, "arm": arm, "iteration": iteration,
                            "sample_idx": sample_idx, "candidate_id": cid,
                            "ok": bool(outcome.get("ok", False))}, sort_keys=True) + "\n")
    return py_path
