"""The BANK-GATE runsheet as ONE command (OVERALL_DESIGN §6 "crisp-up"; PLAN §3).

The single-look hour is the highest-stakes step of the campaign; this wrapper turns it from tribal
knowledge into a replayed procedure: each step is an EXISTING certified tool, run in the registered
order, fail-fast, with every step's stdout captured to a timestamped log directory. Nothing here
computes science — it only SEQUENCES the tools (so rehearsing it on prototype data exercises the
identical procedure the sealed look will use).

Order (the registered runsheet):
  1. archive_integrity.py      — the archive is complete/uncorrupted (counts + homogeneity)
  2. resume_audit.py           — read-only: nothing pending, mirror parity
  3. analyze_campaign.py       — THE single confirmatory look (only once, on the real gate)
  4. variance_decomposition.py — D3 depth bundle
  5. fed_delta_snr.py          — instrument (h) exhibit (R76)
  6. make_prereg_bundle.py     — the frozen-design results bundle

Usage:
    python scripts/bank_gate.py --archive <campaign_root> --rehearsal   # prototype dress rehearsal
    python scripts/bank_gate.py --archive <campaign_root>              # the real gate (Tamer-run)

``--rehearsal`` stamps every log line + the output dir REHEARSAL (directional data only; no
dissertation number) and tolerates step-skips where a tool needs campaign-only inputs. The REAL gate
runs all steps and stops on the first failure.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PY = sys.executable


def step(cmd: list[str], name: str, log_dir: Path, *, tolerate: bool) -> bool:
    print(f"\n=== [bank_gate] {name} ===\n    $ {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8",
                         errors="replace")
    (log_dir / f"{name}.log").write_text(
        f"$ {' '.join(cmd)}\nexit={res.returncode}\n\n--- stdout ---\n{res.stdout}\n"
        f"--- stderr ---\n{res.stderr}", encoding="utf-8")
    tail = "\n".join((res.stdout or "").splitlines()[-5:])
    print(tail)
    if res.returncode != 0:
        print(f"[bank_gate] {name} FAILED (exit {res.returncode}) — log: {log_dir / (name + '.log')}")
        if not tolerate:
            return False
        print("[bank_gate] REHEARSAL mode: tolerated, continuing.")
    return True


def main() -> int:
    p = argparse.ArgumentParser(description="The bank-gate runsheet, sequenced fail-fast.")
    p.add_argument("--archive", required=True, help="Campaign archive root (local mirror).")
    p.add_argument("--rehearsal", action="store_true",
                   help="Dress-rehearsal mode (prototype data): label everything REHEARSAL and "
                        "tolerate steps that need campaign-only inputs.")
    p.add_argument("--skip", nargs="*", default=[], help="Step names to skip (documented reason!).")
    args = p.parse_args()

    tag = "REHEARSAL" if args.rehearsal else "GATE"
    stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = REPO / "outputs" / "bank_gate_logs" / f"{tag}_{stamp}"
    log_dir.mkdir(parents=True, exist_ok=True)
    print(f"[bank_gate] mode={tag}  archive={args.archive}  logs={log_dir}")

    steps: list[tuple[str, list[str]]] = [
        ("archive_integrity", [PY, "scripts/archive_integrity.py", "--archive", args.archive]),
        ("resume_audit", [PY, "scripts/resume_audit.py", "--archive", args.archive]),
        ("analyze_campaign", [PY, "scripts/analyze_campaign.py", "--archive", args.archive]),
        ("variance_decomposition", [PY, "scripts/variance_decomposition.py", "--archive", args.archive]),
        ("fed_delta_snr", [PY, "scripts/fed_delta_snr.py", "--archive", args.archive,
                           "--json", str(log_dir / "fed_delta_snr.json")]),
        ("make_prereg_bundle", [PY, "scripts/make_prereg_bundle.py"]),
    ]
    for name, cmd in steps:
        if name in args.skip:
            print(f"=== [bank_gate] {name} SKIPPED (--skip) ===")
            continue
        if not step(cmd, name, log_dir, tolerate=args.rehearsal):
            print(f"[bank_gate] STOPPED at {name}. Fix, then re-run — do NOT proceed past a red step.")
            return 1
    print(f"\n[bank_gate] {tag} COMPLETE — logs in {log_dir}")
    if args.rehearsal:
        print("[bank_gate] REHEARSAL data is directional-only; no number enters the dissertation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
