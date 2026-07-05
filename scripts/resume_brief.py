#!/usr/bin/env python3
"""Live SessionStart resume briefing — the dynamic layer of the session-continuity system.

Run by the project's SessionStart hook. Prints a COMPUTED snapshot of where the project is
*right now* — recent git activity, work-in-progress, recently-touched files, and adaptive
phase probes (frozen? campaign running? pilots done?) — so a brand-new chat resumes from the
REAL state, not just a possibly-stale cursor. This complements (does not replace) the
auto-loaded layers: the cursor (`memory/session-current-focus.md`, the intent + next action),
CLAUDE.md (the contract + priorities), and the memory index (durable knowledge).

Design: stdlib-only (works with any Python), fully fault-tolerant (every probe is guarded; a
failure degrades to a shorter brief, never an error), and concise (it is injected into context
every session). Smart = it adapts the brief to the detected phase; Dynamic = recomputed each
start; Robust = if git or files are absent, it still prints the resume directive.
"""
from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:  # make stdout UTF-8-tolerant on Windows consoles (belt-and-suspenders; output is ASCII anyway)
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")  # type: ignore[union-attr]
except Exception:
    pass

REPO = Path(__file__).resolve().parents[1]  # llm-reward-portfolio/
NOW = datetime.now().timestamp()
_lines: list[str] = []


def out(s: str = "") -> None:
    _lines.append(s)


def sh(args: list[str], head: int | None = None) -> str:
    """Run a command in the repo; return stdout (head lines), '' on any failure."""
    try:
        r = subprocess.run(args, cwd=str(REPO), capture_output=True, text=True, timeout=8)
        txt = (r.stdout or "").strip()
        return "\n".join(txt.splitlines()[:head]) if head else txt
    except Exception:
        return ""


def age_h(ts: float) -> float:
    return max(0.0, (NOW - ts) / 3600.0)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def recent_files(hours: int = 72, limit: int = 12) -> list[tuple[float, Path]]:
    cutoff = NOW - hours * 3600
    hits: list[tuple[float, Path]] = []
    for sub in ("src", "paper", "config", "scripts", "docs"):
        d = REPO / sub
        if not d.is_dir():
            continue
        for p in d.rglob("*"):
            if (
                p.is_file()
                and p.suffix in (".py", ".md", ".yaml", ".yml", ".bib")
                and "__pycache__" not in p.parts
            ):
                try:
                    m = p.stat().st_mtime
                    if m >= cutoff:
                        hits.append((m, p.relative_to(REPO)))
                except Exception:
                    pass
    hits.sort(reverse=True)
    return hits[:limit]


# --------------------------------------------------------------------------- #
def main() -> None:
    out("=" * 74)
    out("> RESUME BRIEFING - live repo state (read WITH the auto-loaded cursor + CLAUDE.md)")
    out("=" * 74)

    # --- Adaptive phase probes -------------------------------------------- #
    phase_bits: list[str] = []
    prereg = read(REPO / "config" / "preregistration.yaml")
    if prereg:
        if "frozen: true" in prereg:
            phase_bits.append("pre-registration FROZEN")
        elif "frozen: false" in prereg:
            phase_bits.append("pre-registration NOT frozen (pre-freeze)")
    camp = REPO / "outputs" / "campaign"
    if camp.is_dir():
        try:
            newest = max((p.stat().st_mtime for p in camp.rglob("*") if p.is_file()), default=0.0)
            if newest:
                phase_bits.append(f"campaign output present (last write {age_h(newest):.0f}h ago)")
        except Exception:
            pass
    else:
        phase_bits.append("campaign not yet run")
    for art, label in (
        ("outputs/tables/learning_curve.json", "convergence pilot done"),
        # outputs/sigma_pilot (NOT outputs/campaign) — where the farm writes and the analyzer's
        # default root now points (batch-5 m2, 2026-07-03).
        ("outputs/sigma_pilot/sigma_seed_pilot.json", "sigma_D pilot done"),
    ):
        if (REPO / art).is_file():
            phase_bits.append(label)
    if phase_bits:
        out("Phase: " + " | ".join(phase_bits))

    # --- Cursor freshness -------------------------------------------------- #
    # The cursor lives in the auto-memory dir (already auto-loaded); surface its freshness if findable.
    for cand in (
        Path.home() / ".claude" / "projects" / "c--Users-User-Desktop-dissertation-papers" / "memory" / "session-current-focus.md",
    ):
        if cand.is_file():
            out(f"Cursor last updated: {age_h(cand.stat().st_mtime):.0f}h ago "
                f"(memory/session-current-focus.md - already in context)")
            break

    # --- Git activity ------------------------------------------------------ #
    branch = sh(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if branch:
        out(f"Git branch: {branch}")
        commits = sh(["git", "log", "--oneline", "-8"])
        if commits:
            out("Recent commits:")
            for c in commits.splitlines():
                out(f"  {c}")
        status = sh(["git", "status", "--porcelain"], head=15)
        if status:
            out("Uncommitted work-in-progress:")
            for s in status.splitlines():
                out(f"  {s}")
        else:
            out("Working tree clean.")

    # --- Recently touched files ------------------------------------------- #
    rf = recent_files()
    if rf:
        out("Recently modified (<=72h) - what was being worked on:")
        for m, p in rf:
            out(f"  {age_h(m):5.0f}h  {p}")

    out("-" * 74)
    out("-> Read memory/session-current-focus.md (the cursor) + CLAUDE.md (PRIORITIES + CURRENT")
    out("   STATE), say 'Resuming from: <state> - next: <action>', and CONTINUE the work - do")
    out("   NOT ask 'what would you like to do'. UPDATE the cursor before ending substantive work.")
    out("=" * 74)

    print("\n".join(_lines))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # never let the hook error out the session
        print(f"[resume_brief] (brief unavailable: {type(exc).__name__}) - read "
              f"memory/session-current-focus.md + CLAUDE.md and continue.")
