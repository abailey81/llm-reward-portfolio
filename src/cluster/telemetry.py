"""Myriad live telemetry — the SENSOR half of the adaptive allocation system (2026-07-24).

Collects one structured snapshot of everything the allocation advisor needs, in ONE ssh
round-trip: per-pool free GPUs, cluster contention, our own jobs' states/priorities, and the
U/V access-probe verdict. Read-only against the cluster; NEVER touches priorities.

Design: the PARSERS are pure functions over command text (fully unit-tested offline); the
collector is a thin ssh shell. The dossier (docs/MYRIAD_EXPERT_DOSSIER_2026-07-24.md) is the
ground truth for the semantics encoded here (pools, dispatch mechanics, the two-regime doctrine).
"""
from __future__ import annotations

import json
import re
import subprocess
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

#: Node-prefix -> pool letter map (dossier §2). EF is ONE scheduling pool (`-ac allow=EF`).
_PREFIX_POOL = (("node-e", "EF"), ("node-f", "EF"), ("node-l", "L"),
                ("node-u", "U"), ("node-v", "V"))

#: Registered per-training speed factors vs V100 (dossier §2; canary re-measures).
POOL_SPEED = {"EF": 1.0, "L": 1.9, "U": 2.1, "V": 2.1}

#: The U/V access probes submitted 2026-07-24 (runbook §10 best-hardware protocol).
PROBE_JOBS = {"10293": "U", "10294": "V", "10295": "EF-control"}

#: Contention threshold (eligible `qw` jobs cluster-wide) separating the two chunking regimes
#: (dossier §3b). Calibration: the 2026-07-23/24 jam measured ~3,000 qw; quiet nights run <500.
CONTENDED_QW = 1500


@dataclass
class Snapshot:
    """One timestamped telemetry frame (all fields safe to archive/print — no secrets)."""

    ts: str
    pool_free: dict[str, int]            # pool -> free GPU count (from `qhost -F gpu`)
    cluster_qw: int                      # eligible pending jobs cluster-wide
    cluster_users: int                   # distinct users with pending jobs
    our_jobs: list[dict]                 # [{id, prior, state}] for our user
    probe_states: dict[str, str]         # probe job id -> qstat state ("r"/"qw"/"done"/"absent")
    errors: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)


# --------------------------------------------------------------------------------------- #
# Pure parsers (unit-tested offline)                                                       #
# --------------------------------------------------------------------------------------- #
def parse_qhost_gpu(text: str) -> dict[str, int]:
    """``qhost -F gpu`` -> {pool: free_gpu_count}.

    The listing alternates host lines (``node-xNNa-…``) with resource lines
    (``Host Resource(s):      hc:gpu=N``); a missing resource line means 0 free.
    """
    free: dict[str, int] = {}
    current_pool: str | None = None
    for line in text.splitlines():
        s = line.strip()
        m = re.match(r"(node-[a-z]\d+a?-?\d*)", s)
        if m:
            current_pool = None
            for prefix, pool in _PREFIX_POOL:
                if m.group(1).startswith(prefix):
                    current_pool = pool
                    break
            continue
        g = re.search(r"hc:gpu=(\d+(?:\.\d+)?)", s)
        if g and current_pool:
            free[current_pool] = free.get(current_pool, 0) + int(float(g.group(1)))
            current_pool = None
    return free


def parse_cluster_pending(text: str) -> tuple[int, int]:
    """``qstat -u '*' -s p`` -> (eligible qw job count, distinct users)."""
    qw = 0
    users: set[str] = set()
    for line in text.splitlines()[2:]:
        cols = line.split()
        if len(cols) >= 5 and cols[4] == "qw":
            qw += 1
        if len(cols) >= 5:
            users.add(cols[3])
    return qw, len(users)


def parse_our_jobs(text: str) -> list[dict]:
    """``qstat`` (our user) -> [{id, prior, state}] (one row per qstat line, arrays included)."""
    out: list[dict] = []
    for line in text.splitlines()[2:]:
        cols = line.split()
        if len(cols) >= 5 and cols[0].isdigit():
            out.append({"id": cols[0], "prior": float(cols[1]), "state": cols[4]})
    return out


def probe_verdicts(our_jobs: list[dict], *, pending_hours: float,
                   restricted_after_h: float = 48.0) -> dict[str, str]:
    """The U/V experiment verdict per probe (runbook §10 branch).

    ``run``/``done`` (absent after having been submitted) => the pool answered => USABLE.
    still pending past ``restricted_after_h`` => effectively RESTRICTED. Else PENDING.
    """
    states = {j["id"]: j["state"] for j in our_jobs}
    verdicts: dict[str, str] = {}
    for jid, pool in PROBE_JOBS.items():
        st = states.get(jid)
        if st is None:
            verdicts[pool] = "ran-or-gone (USABLE if it ran — check accounting)"
        elif st.startswith("r"):
            verdicts[pool] = "RUNNING (USABLE)"
        elif pending_hours >= restricted_after_h:
            verdicts[pool] = "pending>%dh (effectively RESTRICTED)" % int(restricted_after_h)
        else:
            verdicts[pool] = f"pending ({st})"
    return verdicts


# --------------------------------------------------------------------------------------- #
# The collector (thin ssh shell — one round trip)                                          #
# --------------------------------------------------------------------------------------- #
_REMOTE = (
    "echo '#QHOST'; qhost -F gpu 2>/dev/null; "
    "echo '#PENDING'; qstat -u '*' -s p 2>/dev/null; "
    "echo '#MINE'; qstat 2>/dev/null"
)


def collect(host: str = "myriad", *, probe_age_hours: float = 0.0,
            timeout: int = 45) -> Snapshot:
    """One ssh round trip -> a parsed :class:`Snapshot` (errors captured, never raised)."""
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    errors: list[str] = []
    sections = {"QHOST": "", "PENDING": "", "MINE": ""}
    try:
        r = subprocess.run(["ssh", "-o", "ConnectTimeout=20", host, _REMOTE],
                           capture_output=True, text=True, timeout=timeout)
        current = None
        for line in (r.stdout or "").splitlines():
            if line.startswith("#") and line[1:] in sections:
                current = line[1:]
                continue
            if current:
                sections[current] += line + "\n"
        if r.returncode != 0:
            errors.append(f"ssh rc={r.returncode}: {(r.stderr or '')[-200:]}")
    except Exception as exc:  # noqa: BLE001 — telemetry must degrade, never crash a caller
        errors.append(f"{type(exc).__name__}: {exc}")

    qw, users = parse_cluster_pending(sections["PENDING"])
    mine = parse_our_jobs(sections["MINE"])
    return Snapshot(
        ts=ts,
        pool_free=parse_qhost_gpu(sections["QHOST"]),
        cluster_qw=qw,
        cluster_users=users,
        our_jobs=mine,
        probe_states=probe_verdicts(mine, pending_hours=probe_age_hours),
        errors=errors,
    )


def append_log(snap: Snapshot, path: str | Path = "outputs/myriad_telemetry.jsonl") -> None:
    """Append one frame to the local telemetry log (atomic-enough single write)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(asdict(snap)) + "\n")
