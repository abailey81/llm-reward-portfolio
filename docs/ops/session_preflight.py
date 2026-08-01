"""SESSION PREFLIGHT — one command that PROVES the campaign's state, so nothing rests on memory.

WHY THIS EXISTS (2026-08-01, RUN 12 close). The session model collapsed from four lanes to two, and
the surviving BUILDER session inherits ops + the monitor line + coord. The handover brief lists what
to check; a list is only as good as the reader's diligence at 3 a.m. **This makes the check
mechanical.** It was written immediately after I nearly handed over without D21 (reboot recovery) —
not because the risk was live (it is resolved) but because I had to REMEMBER to look, and the next
person will not.

WHAT IT IS NOT: a re-implementation. Every check either reads an artefact the campaign already
maintains or shells out to the tool that already owns that truth (`freeze.py`, `audit_reproducibility`,
`openitems.py`). Duplicating a check is how two instruments come to disagree about the same fact.

READ-ONLY. Touches no archive, submits nothing, changes no design.

    python docs/ops/session_preflight.py           # fast (~5 s): the state that can kill a run
    python docs/ops/session_preflight.py --full    # + freeze, reproducibility, board (~60 s)

EXIT: 0 all clear · 1 ATTENTION (something needs a human) · 2 FAIL (a run-killer is live).
"""
from __future__ import annotations

import calendar
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RUN = REPO / "outputs" / "campaign_cluster_run4"
CYCLE_LOG = REPO / "docs" / "ops" / "watch" / "CYCLE_LOG.md"
MIRROR = Path("D:/llm_rp_archive_mirror/campaign_cluster_run4")
DISK_FLOOR_GB = 20.0          # same floor scripts/sentinel.py::check_disk enforces
CYCLE_STALE_S = 150.0         # the mandate's "~2 minutes"

OK, ATTN, FAIL = "OK", "ATTENTION", "FAIL"
_rows: list[tuple[str, str, str]] = []


def add(name: str, status: str, detail: str) -> None:
    _rows.append((name, status, detail))


def sh(args: list[str], timeout: int = 120) -> tuple[int, str]:
    try:
        p = subprocess.run(args, cwd=REPO, capture_output=True, text=True,
                           timeout=timeout, encoding="utf-8", errors="replace")
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except Exception as exc:  # noqa: BLE001 — a preflight must never be the thing that fails
        return 99, f"{type(exc).__name__}: {exc}"


# --------------------------------------------------------------------------- #
def check_cycle_log() -> None:
    """The monitoring mandate: >~2 min old means the loop is DEAD."""
    if not CYCLE_LOG.is_file():
        add("cycle_log", FAIL, "CYCLE_LOG.md missing — the monitoring loop has never run")
        return
    last = ""
    for line in CYCLE_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        if re.match(r"^\d{4}-\d\d-\d\dT", line):
            last = line
    m = re.match(r"^(\S+Z)", last)
    if not m:
        add("cycle_log", FAIL, "no timestamped line found")
        return
    # UTC, unambiguously. `time.mktime` interprets the struct as LOCAL time, so on this box (UTC+2)
    # the very first run of this file reported a FRESH log as 7,222 s stale and returned FAIL — a
    # claim about THIS SCRIPT, not about the campaign. `calendar.timegm` is the inverse of gmtime and
    # needs no correction term to get wrong.
    age = time.time() - calendar.timegm(time.strptime(m.group(1), "%Y-%m-%dT%H:%M:%SZ"))
    fields = dict(re.findall(r"(\w+)=([^\s]+)", last))
    drift, sci = fields.get("drift", "?"), fields.get("sci", "?")
    st = OK if age <= CYCLE_STALE_S else FAIL
    add("cycle_log", st, f"{age:.0f}s old (dead >{CYCLE_STALE_S:.0f}s) · records={fields.get('records','?')} "
                         f"drift={drift} sci={sci}")
    # drift and sci are the two that must NEVER change
    add("drift_sci", OK if (drift == "0" and sci == "OK") else FAIL,
        f"drift={drift} sci={sci} (both are invariants; a transient drift=N around your own "
        f"commits is expected and clears in ~100 s)")


def check_drift_arms(running_sha: str) -> None:
    """BOTH arms: committed diff vs RUNNING_SHA, and the working tree."""
    paths = ["src", "scripts", "config", "prompts"]
    _, a1 = sh(["git", "diff", "--name-only", running_sha, "HEAD", "--", *paths])
    _, a2 = sh(["git", "status", "--porcelain", "--", *paths])
    n1 = len([x for x in a1.splitlines() if x.strip()])
    n2 = len([x for x in a2.splitlines() if x.strip()])
    add("drift_arm1", OK if n1 == 0 else FAIL, f"{n1} file(s) differ {running_sha}..HEAD")
    add("drift_arm2", OK if n2 == 0 else FAIL, f"{n2} uncommitted file(s) in {'/'.join(paths)}")


def check_processes() -> None:
    """Driver/supervisor/loop census.

    ⚠ THE TRAP THIS ENCODES: a `$(...)` subshell inherits its parent's command line, and a loose
    match also matches THIS PROCESS'S OWN QUERY. Both have invented processes for three separate
    sessions. So: match on the executable name, and EXCLUDE any candidate whose parent is itself a
    candidate.
    """
    try:
        import psutil  # type: ignore
    except Exception:  # noqa: BLE001
        add("processes", ATTN, "psutil unavailable — count processes manually (see the brief §3)")
        return
    procs = []
    for p in psutil.process_iter(["pid", "ppid", "name", "cmdline"]):
        try:
            cl = " ".join(p.info.get("cmdline") or [])
        except Exception:  # noqa: BLE001
            continue
        if p.info["pid"] == os.getpid():
            continue
        procs.append((p.info["pid"], p.info["ppid"], (p.info.get("name") or "").lower(), cl))

    def census(pred) -> list[int]:
        hit = [(pid, ppid) for pid, ppid, nm, cl in procs if pred(nm, cl)]
        ids = {pid for pid, _ in hit}
        return [pid for pid, ppid in hit if ppid not in ids]   # drop children of the same class

    drivers = census(lambda nm, cl: "python" in nm and "run_campaign_cluster" in cl)
    sups = census(lambda nm, cl: "powershell" in nm and re.search(r"-File .*mode_d_supervisor\.ps1", cl))
    loops = census(lambda nm, cl: "bash" in nm and "cycle_loop.sh" in cl)
    sent = census(lambda nm, cl: "python" in nm and "sentinel.py" in cl)
    add("processes", OK if (loops and sent and sups) else FAIL,
        f"driver-lines={len(drivers)} supervisors={len(sups)} cycle_loops={len(loops)} sentinel={len(sent)}")
    if len(loops) > 1:
        add("cycle_loop_dupes", FAIL,
            f"{len(loops)} cycle loops — two writers race the same '>>' append and TEAR lines "
            f"in ALERTS.txt. Kill all but one.")


def check_reboot_recovery() -> None:
    """D21: without a boot task, a Windows Update reboot kills the whole fleet and NOTHING returns."""
    rc, out = sh(["powershell", "-NoProfile", "-Command",
                  "$t=Get-ScheduledTask -TaskName 'LLMRewardCampaignResume' -ErrorAction "
                  "SilentlyContinue; if($t){ $t.State; ($t.Actions | ForEach-Object { $_.Arguments }) } "
                  "else { 'MISSING' }"], timeout=60)
    if "MISSING" in out or rc not in (0, 1):
        add("reboot_recovery", FAIL,
            "NO boot task — a reboot kills 12 supervisors + all drivers + the cycle loop and NONE "
            "come back, while Myriad keeps running with nobody polling (D21)")
        return
    # The 2026-08-01 fix re-enters through mode_d_launch.ps1 (the single source of truth) and MUST
    # carry BOTH excluded hosts, or the substrate fence is absent on the reboot path (the D15 defect).
    good = "mode_d_launch.ps1" in out and "node-d00a-230" in out and "node-d00b-024" in out
    add("reboot_recovery", OK if good else ATTN,
        "boot task present, re-enters via mode_d_launch.ps1 with BOTH host exclusions" if good
        else "boot task present but its action looks WRONG (must call mode_d_launch.ps1 and carry "
             "node-d00a-230 AND node-d00b-024) — see D21")


def check_disk() -> None:
    t, u, f = shutil.disk_usage(str(REPO))
    gb = f / 1e9
    st = FAIL if gb < DISK_FLOOR_GB else (ATTN if gb < DISK_FLOOR_GB + 10 else OK)
    add("disk", st, f"C: {gb:.1f} GB free (CRITICAL floor {DISK_FLOOR_GB:.0f}); "
                    f"test records are ~480 KB each")


def check_mirror() -> None:
    """The mirror is what makes a C: failure cost records rather than the campaign."""
    if not MIRROR.is_dir():
        add("mirror", FAIL, f"archive mirror {MIRROR} MISSING — a disk failure would be total")
        return
    newest = 0.0
    for root, _dirs, files in os.walk(MIRROR):
        for fn in files:
            try:
                newest = max(newest, os.path.getmtime(os.path.join(root, fn)))
            except OSError:
                pass
        if time.time() - newest < 600:      # fresh enough; stop walking a 20 GB tree
            break
    age_h = (time.time() - newest) / 3600 if newest else 999
    add("mirror", OK if age_h < 2 else ATTN, f"archive mirror {age_h:.1f} h old")


def check_records() -> None:
    """Per-tier counts + the arm-freeze census — the campaign's actual progress."""
    if not RUN.is_dir():
        add("records", FAIL, f"{RUN} missing")
        return
    def n(pat: str) -> int:
        return sum(1 for _ in RUN.glob(pat))
    core = n("test/*/*/record.json")
    legs = n("test_leg_*/*/*/record.json")
    h3 = n("test_h3_singleshot/*/*/record.json")
    search = n("search*/*/*/record.json")
    frozen = {p.name.replace("frozen_leg_", "").replace("frozen", "core"): len(list(p.iterdir()))
              for p in sorted(RUN.glob("frozen*")) if p.is_dir()}
    add("records", OK, f"core_test={core} leg_test={legs} h3={h3} search={search} "
                       f"TOTAL={core+legs+h3+search}")
    add("arms_frozen", OK, " ".join(f"{k}={v}" for k, v in frozen.items()))
    # The H2 headline: distributional/scalar are tested ONLY in C2, behind the C1 barrier.
    c4 = sum(1 for p in RUN.glob("driver_*.log")
             if "C4|pipelined" in p.read_text(encoding="utf-8", errors="replace")[-400_000:])
    add("c4_entered", OK, f"{c4} line(s) have executed a C4 block "
                          f"(0 = still C1/C2; expect qw to jump to hundreds when the first enters)")


def check_git_backup() -> None:
    _, out = sh(["git", "log", "--oneline", "origin/myriad-cluster-and-tier-system..HEAD"])
    n = len([x for x in out.splitlines() if x.strip() and not x.startswith("fatal")])
    add("unpushed", OK if n == 0 else ATTN,
        f"{n} commit(s) not on the working branch remote (the backup branch may still carry them)")


def check_full() -> None:
    rc, out = sh([sys.executable, "scripts/freeze.py", "--check"], timeout=180)
    add("freeze", OK if rc == 0 and "MATCHES" in out else FAIL,
        "canonical hash MATCHES" if "MATCHES" in out else f"freeze --check rc={rc}")
    rc, out = sh([sys.executable, "scripts/audit_reproducibility.py"], timeout=300)
    m = re.search(r"(\d+) pass / (\d+) warn / (\d+) fail", out)
    if m:
        p, w, f = m.groups()
        add("reproducibility", OK if (w == "0" and f == "0") else FAIL,
            f"{p} pass / {w} warn / {f} fail — Priority 5 requires ZERO warn AND zero fail")
    else:
        add("reproducibility", ATTN, f"could not parse the audit (rc={rc})")
    rc, out = sh([sys.executable, str(REPO.parent / ".claude" / "lanes" / "openitems.py"), "--open"],
                 timeout=180)
    m = re.search(r"NOT DONE:\s*(\d+)", out)
    add("open_items", OK, f"{m.group(1) if m else '?'} open row(s) on the verified board")


def main(argv: list[str]) -> int:
    full = "--full" in argv
    running_sha = "unknown"
    try:
        cyc = (REPO / "docs" / "ops" / "cycle.py").read_text(encoding="utf-8", errors="replace")
        m = re.search(r'RUNNING_SHA\s*=\s*"([0-9a-f]+)"', cyc)
        running_sha = m.group(1) if m else "unknown"
    except OSError:
        pass

    check_cycle_log()
    check_drift_arms(running_sha)
    check_processes()
    check_reboot_recovery()
    check_disk()
    check_mirror()
    check_records()
    check_git_backup()
    if full:
        check_full()

    width = max(len(n) for n, _, _ in _rows)
    worst = OK
    print(f"\n=== SESSION PREFLIGHT — RUNNING_SHA {running_sha} "
          f"{'(full)' if full else '(fast; --full adds freeze/repro/board)'} ===")
    for name, st, detail in _rows:
        mark = {OK: "  OK ", ATTN: " ATTN", FAIL: " FAIL"}[st]
        print(f"[{mark}] {name.ljust(width)}  {detail}")
        if st == FAIL or (st == ATTN and worst == OK):
            worst = st if st == FAIL else ATTN
    print(f"\nVERDICT: {worst}")
    if worst != OK:
        print("A FAIL is a run-killer or an invariant breach — act before doing anything else.\n"
              "An ATTENTION needs a human decision, not necessarily an action.")
    return {OK: 0, ATTN: 1, FAIL: 2}[worst]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
