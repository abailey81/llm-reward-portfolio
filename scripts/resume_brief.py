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

    # --- HANDOFF integrity check (the smart-continuity system, 2026-07-22) -------------------- #
    # docs/HANDOFF.md carries a machine-readable handoff_state block regenerated at session end
    # (scripts/update_handoff.py). Diff it against LIVE reality here so a stale snapshot
    # announces itself at boot instead of silently misleading the next session.
    try:
        import re as _re

        _htxt = read(REPO / "docs" / "HANDOFF.md")
        _m = _re.search(r"```yaml\nhandoff_state:\n(.*?)```", _htxt, _re.DOTALL)
        if not _m:
            out("!! HANDOFF: docs/HANDOFF.md has NO handoff_state block - restore it "
                "(scripts/update_handoff.py).")
        else:
            # Flat `key: value` lines — parsed by hand to keep this script stdlib-only.
            _snap: dict[str, str] = {}
            for _ln in _m.group(1).splitlines():
                if ":" in _ln:
                    _k, _v = _ln.split(":", 1)
                    _snap[_k.strip()] = _v.strip().strip('"')
            # The snapshot commit (and small follow-ups) move HEAD, so the snapshot may
            # legitimately record any of the last 3 commits. Older = a session ended un-closed.
            _recent = sh(["git", "log", "--format=%h", "-3"]).split()
            _live_head = _recent[0] if _recent else ""
            _live_frozen = "true" if _re.search(r"frozen:\s*true", prereg, _re.I) else "false"  # row 30h: case/space-tolerant
            _legs_n = len(_re.findall(r"^\s*-\s*label:", read(REPO / "config" / "legs.yaml"), _re.M))  # row 30h: indent-tolerant
            _rows = _re.findall(r"\|\s*\d{4}-\d{2}-\d{2}\s*\|\s*(R\d+)\s*\|",
                                read(REPO / "PREREGISTRATION.md"))
            _rmax = max(_rows, key=lambda r: int(r[1:])) if _rows else "R?"
            _diffs = []
            if _snap.get("head") not in _recent:
                _diffs.append(f"HEAD {_snap.get('head')} -> {_live_head}")
            if _snap.get("frozen") != _live_frozen:
                _diffs.append(f"frozen {_snap.get('frozen')} -> {_live_frozen}")
            if _snap.get("legs_n") != str(_legs_n):
                _diffs.append(f"legs_n {_snap.get('legs_n')} -> {_legs_n}")
            if _snap.get("amendments_through") != _rmax:
                _diffs.append(f"amendments {_snap.get('amendments_through')} -> {_rmax}")
            if _diffs:
                out("!! HANDOFF SNAPSHOT IS STALE (docs/HANDOFF.md S1 vs live): "
                    + "; ".join(_diffs))
                out("!! The last session ended without the protocol close-out. TRUST THE LIVE "
                    "REPO + the cursor; regenerate via scripts/update_handoff.py early.")
            else:
                out(f"HANDOFF S1 CURRENT [OK]  (regenerated {_snap.get('regenerated_utc')}; "
                    f"suite: {_snap.get('suite_status')})")
    except Exception as _exc:  # the brief must never break the session
        out(f"!! HANDOFF check unavailable ({type(_exc).__name__}) - read docs/HANDOFF.md "
            "manually.")

    out("-" * 74)
    out("-> READ ORDER: docs/HANDOFF.md (S1 state + standing orders + the authority map) ->")
    out("   memory/session-current-focus.md (the cursor NOW entry) -> CLAUDE.md (PRIORITIES +")
    out("   the four-authority rule). Say 'Resuming from: <state> - next: <action>' and CONTINUE.")
    out("   END-OF-WORK DUTIES (all four): update_handoff.py + short cursor entry + CHANGELOG +")
    out("   backup push (CLAUDE.md -> SESSION HANDOFF PROTOCOL).")
    out("=" * 74)

    print("\n".join(_lines))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # never let the hook error out the session
        print(f"[resume_brief] (brief unavailable: {type(exc).__name__}) - read "
              f"memory/session-current-focus.md + CLAUDE.md and continue.")
