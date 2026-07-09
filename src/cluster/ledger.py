"""Failure forensics from Grid Engine accounting + the epilogue ledger (§14.1/§14.4).

``qacct -j <job_id>`` is the scheduler's own truth (exit_status, failed-category, maxvmem,
wallclock per task) — independent of our records and of the epilogue file, so a task that died
before writing ANYTHING still shows up here. ``parse_qacct`` turns the record-block format into
rows; ``failures`` filters the ones needing attention; ``requeue_specs`` maps them back to specs
(bounded retries; 3rd strike = permanent ledger row, same JSON-lines shape as failures.jsonl).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

__all__ = ["parse_qacct", "failures", "requeue_specs", "read_epilogue"]

_RETRY_KEY = "_cluster_retries"
MAX_RETRIES = 2


def parse_qacct(text: str) -> list[dict[str, Any]]:
    """Parse ``qacct -j`` output (blocks separated by ==== lines) into per-task dicts."""
    rows: list[dict[str, Any]] = []
    block: dict[str, Any] = {}
    for line in text.splitlines():
        if line.startswith("====") :
            if block:
                rows.append(block)
            block = {}
            continue
        parts = line.split(None, 1)
        if len(parts) == 2:
            block[parts[0]] = parts[1].strip()
    if block:
        rows.append(block)
    return rows


def failures(qacct_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rows with a nonzero exit_status or a nonzero Grid Engine 'failed' category."""
    bad: list[dict[str, Any]] = []
    for r in qacct_rows:
        exit_status = str(r.get("exit_status", "0")).split()[0]
        failed = str(r.get("failed", "0")).split()[0]
        if exit_status not in ("0", "") or failed not in ("0", ""):
            bad.append(r)
    return bad


def requeue_specs(
    failed_task_ids: list[int],
    task_specs: dict[int, dict[str, Any]],
    permanent_ledger: str | Path,
) -> list[dict[str, Any]]:
    """Specs to resubmit (retry count bumped); exhausted ones go to the permanent ledger.

    The ledger file is append-only JSON-lines (one row per abandoned task) so the bank-gate
    accounting and the matched-budget guard can consume it exactly like failures.jsonl.
    """
    retry: list[dict[str, Any]] = []
    ledger_path = Path(permanent_ledger)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    for tid in failed_task_ids:
        spec = dict(task_specs[tid])
        n = int(spec.get(_RETRY_KEY, 0))
        if n < MAX_RETRIES:
            spec[_RETRY_KEY] = n + 1
            retry.append(spec)
        else:
            with ledger_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({"task": tid, "spec": spec, "reason": "retries_exhausted"},
                                    sort_keys=True, default=str) + "\n")
    return retry


def read_epilogue(path: str | Path) -> list[dict[str, Any]]:
    """Tolerant reader for the per-array epilogue JSONL (§14.4) — skips torn lines."""
    p = Path(path)
    if not p.is_file():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows
