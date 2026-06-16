"""Per-run results schema and the canonical results loader (FINAL_PLAN F.13, audit C-1).

This module defines the per-run record schema and provides the ONLY interface that
analysis code may use to read results (audit C-1: never parse run files ad hoc).
Every campaign run writes exactly one record under ``<root>/<run_id>/record.json``;
every table, figure and inference step reads it back through :func:`load_run` /
:func:`load_all`. Centralising IO here guarantees the provenance fields (hashes,
seeds, environment fingerprint) are always present and that the loader fails loudly
when a required field is missing.

If a record carries a ``reward_source`` string, it is archived alongside the record
as ``reward.py`` so results *replay from the archive* and are never regenerated
(audit C-2): the LLM that produced the reward is non-deterministic.

Audit refs: C-1 (analysis reads only through this module), C-2 (replay from archive).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

__all__ = ["REQUIRED_FIELDS", "write_run", "load_run", "load_all"]

#: Fields every persisted run record must contain. :func:`write_run` validates the
#: record against this set and raises ``KeyError`` naming the first missing field.
REQUIRED_FIELDS: tuple[str, ...] = (
    "run_id",
    "arm",
    "seed",
    "fold",
    "candidate_id",
    "generation",
    "reward_source_hash",
    "feedback_block",
    "metrics",
    "wall_clock",
    "env_fingerprint",
)

_RECORD_NAME = "record.json"
_REWARD_NAME = "reward.py"


def _validate(record: dict[str, Any]) -> None:
    """Raise ``KeyError`` naming the first missing required field."""
    for field in REQUIRED_FIELDS:
        if field not in record:
            raise KeyError(f"run record is missing required field {field!r}")


def write_run(record: dict[str, Any], root: str | Path) -> Path:
    """Validate and persist a single per-run record.

    Parameters
    ----------
    record : dict
        Mapping containing at least every field in :data:`REQUIRED_FIELDS`.
        If it carries a ``reward_source`` string, that source is written next to
        the record as ``reward.py``.
    root : str | Path
        Directory under which a ``<run_id>/`` subdirectory is created.

    Returns
    -------
    Path
        Path to the written ``record.json``.

    Raises
    ------
    KeyError
        If any field in :data:`REQUIRED_FIELDS` is absent (named in the message).
    """
    _validate(record)
    run_dir = Path(root) / str(record["run_id"])
    run_dir.mkdir(parents=True, exist_ok=True)

    record_path = run_dir / _RECORD_NAME
    with record_path.open("w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, sort_keys=True, default=str)

    reward_source = record.get("reward_source")
    if reward_source is not None:
        (run_dir / _REWARD_NAME).write_text(str(reward_source), encoding="utf-8")

    return record_path


def load_run(run_id: str, root: str | Path) -> dict[str, Any]:
    """Load a single per-run record by id.

    Parameters
    ----------
    run_id : str
        Identifier of the run to load.
    root : str | Path
        Directory containing the ``<run_id>/`` subdirectory.

    Returns
    -------
    dict
        The validated record. If a ``reward.py`` is present and the record does
        not already carry ``reward_source``, the source is reattached.

    Raises
    ------
    FileNotFoundError
        If the run record does not exist.
    KeyError
        If the loaded record fails schema validation.
    """
    run_dir = Path(root) / str(run_id)
    record_path = run_dir / _RECORD_NAME
    if not record_path.is_file():
        raise FileNotFoundError(f"no run record at {record_path}")
    with record_path.open(encoding="utf-8") as fh:
        record = json.load(fh)
    _validate(record)

    reward_path = run_dir / _REWARD_NAME
    if reward_path.is_file() and "reward_source" not in record:
        record["reward_source"] = reward_path.read_text(encoding="utf-8")
    return record


def load_all(
    root: str | Path, filter: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """Load all per-run records under ``root``, optionally filtered.

    Parameters
    ----------
    root : str | Path
        Directory containing per-run subdirectories.
    filter : dict | None
        Optional mapping of field -> required value; only records matching every
        constraint are returned (e.g. ``{"arm": "scalar"}``).

    Returns
    -------
    list[dict]
        Validated records matching the filter (all records when ``filter`` is
        ``None``), ordered by ``run_id``.
    """
    root_path = Path(root)
    records: list[dict[str, Any]] = []
    if not root_path.is_dir():
        return records
    for run_dir in sorted(p for p in root_path.iterdir() if p.is_dir()):
        if not (run_dir / _RECORD_NAME).is_file():
            continue
        record = load_run(run_dir.name, root_path)
        if filter is not None and not all(
            record.get(k) == v for k, v in filter.items()
        ):
            continue
        records.append(record)
    return records
