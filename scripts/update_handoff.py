"""Regenerate the MACHINE-STATE block in docs/HANDOFF.md from LIVE facts (the handoff system).

The smart-continuity contract (CLAUDE.md → SESSION HANDOFF PROTOCOL): HANDOFF §1 is regenerated,
never appended. This script makes that a one-command mechanical act — it reads the live repo
(git HEAD, the frozen flag, the executed leg count, the highest amendment row, the gate-check
count) and rewrites the fenced ``handoff_state`` block. The SessionStart hook (resume_brief.py)
diffs that block against the same live facts at every boot, so a session that forgot to run this
gets a LOUD staleness warning instead of silently inheriting a stale snapshot.

Usage (at the end of substantive work, after the last commit):
    python scripts/update_handoff.py --suite-status "exit 0 (Nth certification)"
The prose rows of §1 are still reviewed by hand; this block is the mechanically-verified core.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
HANDOFF = REPO / "docs" / "HANDOFF.md"

BLOCK_RE = re.compile(r"```yaml\nhandoff_state:\n.*?```", re.DOTALL)


def live_facts() -> dict[str, object]:
    """The facts the block asserts — read from the SAME sources the rest of the repo trusts."""
    import yaml

    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                          capture_output=True, text=True).stdout.strip()
    prereg = yaml.safe_load((REPO / "config" / "preregistration.yaml").read_text(encoding="utf-8"))
    legs = yaml.safe_load((REPO / "config" / "legs.yaml").read_text(encoding="utf-8"))["legs"]
    rows = re.findall(r"\|\s*\d{4}-\d{2}-\d{2}\s*\|\s*(R\d+)\s*\|",
                      (REPO / "PREREGISTRATION.md").read_text(encoding="utf-8"))
    r_max = max(rows, key=lambda r: int(r[1:])) if rows else "R?"
    return {
        "head": head,
        "frozen": bool(prereg.get("frozen")),
        "legs_n": len(legs),
        "amendments_through": r_max,
    }


def render_block(facts: dict[str, object], suite_status: str, gate_checks: int,
                 backup_branch: str) -> str:
    return (
        "```yaml\n"
        "handoff_state:\n"
        f'  regenerated_utc: "{time.strftime("%Y-%m-%d", time.gmtime())}"\n'
        f'  head: "{facts["head"]}"\n'
        f'  frozen: {str(facts["frozen"]).lower()}\n'
        f'  legs_n: {facts["legs_n"]}\n'
        f'  amendments_through: {facts["amendments_through"]}\n'
        f'  suite_status: "{suite_status}"\n'
        f"  gate_checks: {gate_checks}\n"
        f"  backup_branch: {backup_branch}\n"
        "```"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--suite-status", required=True,
                    help='e.g. "exit 0 (11th certification)" — the one fact the script cannot '
                         "derive (run the suite first; verify-then-claim).")
    ap.add_argument("--gate-checks", type=int, default=21)
    ap.add_argument("--backup-branch", default="backup-2026-07-21")
    args = ap.parse_args(argv)

    text = HANDOFF.read_text(encoding="utf-8")
    if not BLOCK_RE.search(text):
        raise SystemExit("HANDOFF.md has no handoff_state block — restore it before regenerating")
    block = render_block(live_facts(), args.suite_status, args.gate_checks, args.backup_branch)
    HANDOFF.write_text(BLOCK_RE.sub(block, text, count=1), encoding="utf-8")
    print(f"[update_handoff] regenerated: {block.splitlines()[2].strip()} … "
          f"{block.splitlines()[5].strip()}")
    print("[update_handoff] REMINDER: review §1's PROSE rows for anything this session changed "
          "(they are hand-maintained), then commit + push the backup branch.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
