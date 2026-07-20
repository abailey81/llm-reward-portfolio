"""The rung-freshness compile gate (v2; CH6 reporting rule 5, V2_MASTER_PLAN §2b item 5).

Campaign numbers enter the prose tagged with the E1 rung they were computed at:

* ``<!--RUNG:n-->``      — a core-ladder number (n must equal the ACHIEVED rung; anything else is
                           a stale survivor of a rung refresh and FAILS the gate);
* ``<!--LEG-TIER:30-->`` — a replication-leg number (legs run at the floor tier by design and
                           never refresh on the ladder; any value other than 30 FAILS).

Modes
-----
* default  — fail on stale ``RUNG:`` tags and malformed ``LEG-TIER:`` tags (the per-rung refresh
             check, run after every ladder rung lands);
* --final  — additionally fail on any remaining unfilled ``[FROM CAMPAIGN`` slot (the
             pre-submission gate: zero unfilled slots, zero stale tags).

The achieved rung comes from ``--achieved N`` or, if omitted, from
``outputs/tables/achieved_rung.json`` (``{"achieved_rung": N}``). No source ⇒ fail loud —
freshness against an unknown rung is unverifiable, never assumed. Exit 0 = green; 1 = violations
(each reported as file:line); 2 = usage/config error.

Usage
-----
    python scripts/check_rung_freshness.py --achieved 30
    python scripts/check_rung_freshness.py --achieved 403 --final
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

#: The frozen E1 assurance ladder (preregistration seeds.tiers) — the only legal achieved rungs.
E1_LADDER = (30, 100, 189, 279, 340, 403, 568)
#: The frozen leg seed tier (model_suite.leg_seed_tier).
LEG_TIER = 30

_RUNG_RE = re.compile(r"<!--\s*RUNG:(\d+)\s*-->")
_LEG_RE = re.compile(r"<!--\s*LEG-TIER:(\d+)\s*-->")
_SLOT_RE = re.compile(r"\[FROM CAMPAIGN")
#: Non-compiled working files that must not gate the compile.
_EXCLUDE_PREFIXES = ("DRAFTS_",)


def paper_files(paper_dir: Path) -> list[Path]:
    return sorted(
        p for p in paper_dir.glob("*.md") if not p.name.startswith(_EXCLUDE_PREFIXES)
    )


def scan_file(path: Path, achieved: int, final: bool) -> list[str]:
    """Violations for one file, each ``file:line: message``."""
    violations: list[str] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        for m in _RUNG_RE.finditer(line):
            rung = int(m.group(1))
            if rung != achieved:
                violations.append(
                    f"{path.name}:{lineno}: stale RUNG:{rung} (achieved rung is {achieved} — "
                    "refresh this number)"
                )
        for m in _LEG_RE.finditer(line):
            tier = int(m.group(1))
            if tier != LEG_TIER:
                violations.append(
                    f"{path.name}:{lineno}: LEG-TIER:{tier} is not the frozen floor tier "
                    f"({LEG_TIER})"
                )
        if final and _SLOT_RE.search(line):
            violations.append(f"{path.name}:{lineno}: unfilled [FROM CAMPAIGN…] slot at --final")
    return violations


def resolve_achieved(explicit: int | None, achieved_json: Path) -> int:
    if explicit is None:
        if not achieved_json.exists():
            raise SystemExit(
                f"ERROR: no --achieved given and {achieved_json} does not exist — the achieved "
                "rung must be stated, never assumed (exit 2)."
            )
        explicit = int(json.loads(achieved_json.read_text(encoding="utf-8"))["achieved_rung"])
    if explicit not in E1_LADDER:
        raise SystemExit(
            f"ERROR: achieved rung {explicit} is not on the frozen E1 ladder {list(E1_LADDER)} "
            "(exit 2)."
        )
    return explicit


def main(argv: list[str] | None = None) -> int:
    repo = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--achieved", type=int, default=None,
                    help="the achieved E1 rung (omit to read outputs/tables/achieved_rung.json)")
    ap.add_argument("--final", action="store_true",
                    help="pre-submission mode: unfilled [FROM CAMPAIGN…] slots also fail")
    ap.add_argument("--paper-dir", type=Path, default=repo / "paper",
                    help="directory of compiled chapter .md files (test seam)")
    ap.add_argument("--achieved-json", type=Path,
                    default=repo / "outputs" / "tables" / "achieved_rung.json",
                    help="fallback achieved-rung record (test seam)")
    args = ap.parse_args(argv)

    achieved = resolve_achieved(args.achieved, args.achieved_json)
    files = paper_files(args.paper_dir)
    if not files:
        raise SystemExit(f"ERROR: no .md files under {args.paper_dir} (exit 2).")

    violations: list[str] = []
    n_rung = n_leg = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        n_rung += len(_RUNG_RE.findall(text))
        n_leg += len(_LEG_RE.findall(text))
        violations.extend(scan_file(path, achieved, args.final))

    mode = "FINAL" if args.final else "per-rung"
    print(f"rung-freshness gate ({mode}; achieved rung {achieved}): "
          f"{len(files)} files, {n_rung} RUNG tags, {n_leg} LEG-TIER tags")
    for v in violations:
        print(f"  FAIL  {v}")
    if violations:
        print(f"RESULT: {len(violations)} violation(s) — the prose is NOT fresh.")
        return 1
    print("RESULT: green — every tagged number is at the achieved rung"
          + (" and every slot is filled." if args.final else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
