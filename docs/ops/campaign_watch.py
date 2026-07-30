"""CONTINUOUS campaign watcher — emits ONE line only when something MATERIALLY changes.

WHY THIS SHAPE (2026-07-30). Three lessons from this campaign are built in:

* **Keyed on KINDS, not counts.** A watcher keyed on counts cries wolf every poll (the 2026-07-28
  digest lesson). This one hashes a STATE SIGNATURE and speaks only when the signature changes.
* **A CRITICAL that fires into a file nobody reads never fired** (D15: the substrate CRITICAL sat
  unexamined for ten hours while `campaign_guards.py` returned RC=0). So the sentinel's verdicts are
  first-class here, not an afterthought.
* **Triage, so a known alarm cannot MASK a new one.** Acknowledged verdicts live in
  `docs/ops/acknowledged_alarms.txt` (one `check:severity` per line, `#` comments allowed). An
  acknowledged verdict is reported as `(ack)` and does not raise the alert level; anything NOT
  acknowledged does. Alarm fatigue is how D15 survived — this is the countermeasure.

It is READ-ONLY. It never touches the campaign, the archive, or any frozen artefact.

Usage:  python docs/ops/campaign_watch.py [run_root] [--interval SECS] [--once]
"""
from __future__ import annotations

import collections
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

EXPECTED_LINES = 12
_SEV_RANK = {"OK": 0, "INFO": 0, "UNKNOWN": 1, "WARN": 2, "CRITICAL": 3}


def _acknowledged() -> set[str]:
    p = Path(__file__).with_name("acknowledged_alarms.txt")
    out: set[str] = set()
    if p.is_file():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            if line:
                out.add(line)
    return out


def _sentinel(root: Path) -> list[tuple[str, str, str]]:
    """Latest verdict per check, non-OK only, worst first. (severity, check, detail)"""
    p = root / "sentinel_events.jsonl"
    if not p.is_file():
        return []
    latest: dict[str, tuple[str, str, str]] = {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        latest[str(r.get("check"))] = (str(r.get("severity")), str(r.get("check")),
                                       str(r.get("detail", ""))[:150])
    bad = [v for v in latest.values() if _SEV_RANK.get(v[0], 1) > 0]
    return sorted(bad, key=lambda v: -_SEV_RANK.get(v[0], 1))


def _crash_kinds(root: Path) -> collections.Counter:
    """Exception TYPES seen in driver logs — a KIND, so a rising count of a known kind is silent."""
    kinds: collections.Counter = collections.Counter()
    for f in glob.glob(str(root / "driver_*.log")):
        try:
            txt = open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for line in txt.splitlines():
            s = line.strip()
            if s.startswith(("openai.", "TypeError", "RuntimeError", "ValueError", "KeyError",
                             "AttributeError", "OSError", "ConnectionError")):
                kinds[s.split(":", 1)[0]] += 1
    return kinds


def _substrate_mix(root: Path) -> int:
    """Comparison units whose records span >1 (cpu, thread-regime) signature."""
    per_unit: dict[str, set[str]] = collections.defaultdict(set)
    for rec in glob.glob(str(root / "**" / "record.json"), recursive=True):
        d = os.path.dirname(rec)
        envp = os.path.join(d, "env.json")
        if not os.path.isfile(envp):
            continue
        try:
            env = json.load(open(envp, encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        cpu = env.get("cpu") or {}
        det = env.get("determinism_env") or {}
        sig = f"{cpu.get('model_name')}|{det.get('OMP_NUM_THREADS') if isinstance(det, dict) else None}"
        parts = d.replace("\\", "/").split("/")
        per_unit["/".join(parts[-3:-1])].add(sig)
    return sum(1 for s in per_unit.values() if len(s) > 1)


def _supervisors() -> int:
    try:
        # MUST exclude $PID. This query's OWN command line contains the string
        # 'mode_d_supervisor', so without the exclusion it counts ITSELF and reports 13/12 — a false
        # ALERT, which is worse than no watcher because it trains the reader to ignore alerts. This is
        # the P10 class (a process filter that matches the process running it), and it bit here on the
        # very first run of this file. The standing rule is absolute: any process query that greps
        # command lines excludes $PID.
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "@(Get-CimInstance Win32_Process -Filter \"Name='powershell.exe'\" | "
             "Where-Object { $_.ProcessId -ne $PID -and $_.CommandLine -match 'mode_d_supervisor' })"
             ".Count"],
            capture_output=True, text=True, timeout=90)
        return int((out.stdout or "0").strip() or 0)
    except (subprocess.SubprocessError, ValueError):
        return -1


def snapshot(root: Path) -> tuple[str, list[str]]:
    """(signature, human lines). The signature decides whether to speak."""
    ack = _acknowledged()
    sups = _supervisors()
    mix = _substrate_mix(root)
    kinds = _crash_kinds(root)
    sent = _sentinel(root)

    # Capture WHICH guards are non-ok, not just the exit code. The truncation guard went CRITICAL on
    # 2026-07-30 over a single `stop_reason: length` row and can never go green again (the spend ledger
    # is append-only), so `guards_rc` is now PERMANENTLY 2. An rc alone would therefore mask every
    # future guard failure — the same masking problem the sentinel ack file solves. Tracking the named
    # verdict set means a NEW guard failing changes the signature and is reported.
    proc = subprocess.run([sys.executable, "scripts/campaign_guards.py", str(root), "all"],
                          capture_output=True, text=True)
    rc = proc.returncode
    bad_guards = sorted({
        m.group(1)
        for m in re.finditer(r"^\[(\w+)\]\s+(?!ok\b)(\w+)", proc.stdout or "", re.MULTILINE)
    })
    ack_guards = {g.split(":", 1)[1] for g in ack if g.startswith("guard:")}
    unack_guards = [g for g in bad_guards if g not in ack_guards]

    unack = [v for v in sent if f"{v[1]}:{v[0]}" not in ack]
    # `mix > 0` and the sentinel's `substrate_fields` verdict are the SAME FACT. Counting both would
    # pin the header at ALERT for as long as D15's four records sit in the archive, and a label that
    # never changes carries no information — the very alarm-fatigue failure this file exists to stop.
    # So an acknowledged substrate verdict suppresses the mix contribution; a mix appearing while
    # substrate_fields is NOT acknowledged still alerts.
    mix_alerts = mix > 0 and "substrate_fields:CRITICAL" not in ack
    alert = (bool(unack_guards) or (sups != EXPECTED_LINES and sups >= 0)
             or mix_alerts or bool(unack))

    lines: list[str] = []
    head = "ALERT" if alert else "ok"
    gtxt = ",".join(f"{g}{'' if g in ack_guards else '(NEW)'}" for g in bad_guards) or "none"
    lines.append(f"[{head}] guards_rc={rc} bad_guards={gtxt} "
                 f"supervisors={sups}/{EXPECTED_LINES} "
                 f"substrate_mixed_units={mix} crash_kinds={len(kinds)}")
    for sev, check, detail in sent:
        tag = "(ack)" if f"{check}:{sev}" in ack else "(NEW)"
        lines.append(f"   sentinel {tag} {sev} {check}: {detail}")
    if kinds:
        lines.append("   crash kinds: " + ", ".join(f"{k}x{v}" for k, v in kinds.most_common(6)))

    sig = hashlib.sha256(
        json.dumps([rc, bad_guards, sups, mix, sorted(kinds), [(s, c) for s, c, _ in sent]],
                   sort_keys=True).encode()
    ).hexdigest()[:16]
    return sig, lines


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    root = Path(args[0] if args else "outputs/campaign_cluster_run4")
    once = "--once" in argv
    interval = 300
    if "--interval" in argv:
        interval = int(argv[argv.index("--interval") + 1])

    prev = None
    while True:
        try:
            sig, lines = snapshot(root)
        except Exception as exc:  # a watcher must not die on a transient read
            print(f"[watch] snapshot failed: {type(exc).__name__}: {exc}", flush=True)
            sig, lines = "error", []
        if sig != prev:
            for ln in lines:
                print(ln, flush=True)
            prev = sig
        if once:
            return 0
        time.sleep(interval)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
