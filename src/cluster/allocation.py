"""The allocation ADVISOR — the BRAIN of the adaptive speed system (2026-07-24).

Pure decision logic over a telemetry :class:`~src.cluster.telemetry.Snapshot` + our own measured
throughput, emitting THE ALLOCATION PLAN: pool assignments, the exact ``--seed-pool-blocks``
stripe string, the chunking regime, pack recommendations, and recomputed milestone ETAs.

INVARIANTS ENCODED (so every recommendation is legal by construction):
- NEVER emits any priority action (the CLAUDE.md ★ rule; ``-p`` is not in this module's alphabet).
- CRN device homogeneity: stripes are contiguous pool-homogeneous blocks WITHIN each rung
  segment (the ratified block structure); pool/pack changes apply to NEW batches only.
- ADVISORY ONLY: the plan is printed/archived; applying it is an explicit human/launcher act.

Ground truth: docs/MYRIAD_EXPERT_DOSSIER_2026-07-24.md (the priority formula, the two-regime
chunking doctrine §3b, pool speeds §2) + the ratified runbook levers (§10).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from src.cluster.telemetry import CONTENDED_QW, POOL_SPEED, Snapshot

#: Conservative pack depth by GPU VRAM GB (validated pack-5 baseline on the pilot pool; deeper
#: packs UNLOCK ONLY once the canary's archived nvidia-smi confirms per-training VRAM headroom).
PACK_BY_VRAM_GB = {16: 5, 32: 6, 40: 8, 80: 10}

#: Default per-pool VRAM (GB) until the canary measures the E-node cards (16 vs 32 unresolved).
POOL_VRAM_DEFAULT = {"EF": 16, "L": 40, "U": 80, "V": 80}


@dataclass
class Plan:
    """The advisor's output — human-readable via :meth:`render`, machine-usable as fields."""

    regime: str                          # "CONTENDED" | "QUIET"
    chunk_tasks: int                     # recommended --chunk-tasks for NEW submissions
    search_pool: str                     # the latency-critical lane's pool pin
    stripe_pools: list[str]              # pools included in the test stripe, best-first
    seed_pool_blocks: str                # the exact --seed-pool-blocks string
    pack: dict[str, int]                 # pool -> recommended pack (canary-gated above 5)
    pack_note: str
    eta_days: dict[str, float] | None    # milestone -> days-from-now (None until measured)
    notes: list[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [
            f"REGIME: {self.regime}  ->  --chunk-tasks {self.chunk_tasks}",
            f"SEARCH LANE: --pool {self.search_pool}",
            f"TEST STRIPE POOLS (best-first): {','.join(self.stripe_pools)}",
            f"--seed-pool-blocks \"{self.seed_pool_blocks}\"",
            f"PACK: {self.pack}  ({self.pack_note})",
        ]
        if self.eta_days:
            lines.append("ETA (days from now): "
                         + ", ".join(f"{k}={v:.1f}" for k, v in self.eta_days.items()))
        lines += [f"NOTE: {n}" for n in self.notes]
        return "\n".join(lines)


def usable_pools(snap: Snapshot) -> dict[str, int]:
    """Pools we may schedule on, with free-GPU counts. U/V join ONLY on a RUNNING/ran probe
    verdict (the runbook §10 branch); EF/L are always ours (documented allow=EF|L)."""
    pools = {p: snap.pool_free.get(p, 0) for p in ("EF", "L")}
    for pool in ("U", "V"):
        verdict = snap.probe_states.get(pool, "")
        if "USABLE" in verdict:
            pools[pool] = snap.pool_free.get(pool, 0)
    return pools


def chunking(snap: Snapshot) -> tuple[str, int]:
    """The two-regime doctrine (dossier §3b): contended -> big arrays; quiet -> many arrays."""
    if snap.cluster_qw >= CONTENDED_QW:
        return "CONTENDED", 25       # few, heavy arrays: priority-per-job dominates
    return "QUIET", 1                # the mode-D flood: 1-task chunks ramp 1/job/cycle in parallel


def pick_search_pool(pools: dict[str, int]) -> str:
    """The latency-critical chain lane goes to the FASTEST pool with real headroom (>=2 free
    GPUs so a chain never waits on its own lane); falls back to EF (always-eligible)."""
    candidates = sorted(pools.items(), key=lambda kv: -POOL_SPEED.get(kv[0], 0.0))
    for pool, free in candidates:
        if free >= 2:
            return pool
    return "EF"


def stripe(seed_segments: list[tuple[int, int]], pools: dict[str, int],
           pack: dict[str, int] | None = None) -> tuple[list[str], str]:
    """Generate the exact ``--seed-pool-blocks`` string, throughput-weighted.

    Each rung segment ``[a, b]`` (inclusive) is split into contiguous pool-homogeneous blocks
    sized by each pool's effective throughput share (free_gpus x speed x pack/5) — the CRN
    blocked-design invariant of the ratified stripes, generalized to N pools. Pools with zero
    weight are dropped. Returns (pools-used-best-first, the blocks string).
    """
    pack = pack or {}
    weights = {p: f * POOL_SPEED.get(p, 1.0) * (pack.get(p, 5) / 5.0)
               for p, f in pools.items() if f > 0}
    if not weights:                       # nothing free right now -> single-pool EF fallback
        weights = {"EF": 1.0}
    order = sorted(weights, key=lambda p: -weights[p])
    total = sum(weights.values())
    parts: list[str] = []
    for a, b in seed_segments:
        n = b - a + 1
        cursor = a
        for i, p in enumerate(order):
            share = n * weights[p] / total
            take = n - (cursor - a) if i == len(order) - 1 else max(1, round(share))
            take = min(take, b - cursor + 1)
            if take <= 0:
                continue
            parts.append(f"{p}:{cursor}-{cursor + take - 1}")
            cursor += take
            if cursor > b:
                break
    return order, ",".join(parts)


def recommend_pack(pools: dict[str, int], *, measured_vram_per_training_gb: float | None,
                   pool_vram: dict[str, int] | None = None) -> tuple[dict[str, int], str]:
    """Pack depth per pool. WITHOUT a canary measurement everything stays at the validated 5;
    WITH one, depth = floor(VRAM * 0.9 / per-training) capped by PACK_BY_VRAM_GB."""
    vram = pool_vram or POOL_VRAM_DEFAULT
    if measured_vram_per_training_gb is None or measured_vram_per_training_gb <= 0:
        return {p: 5 for p in pools}, "pack-5 everywhere (canary VRAM measurement pending)"
    out: dict[str, int] = {}
    for p in pools:
        fit = int((vram.get(p, 16) * 0.9) // measured_vram_per_training_gb)
        out[p] = max(1, min(fit, PACK_BY_VRAM_GB.get(vram.get(p, 16), 5)))
    return out, f"from measured {measured_vram_per_training_gb:.1f}G/training (canary)"


def eta(remaining_trainings: dict[str, int],
        measured_trainings_per_day: float | None) -> dict[str, float] | None:
    """Milestone ETAs from OUR measured throughput (records/day). None until measured — the
    advisor never invents a rate (the accuracy rule)."""
    if not measured_trainings_per_day or measured_trainings_per_day <= 0:
        return None
    return {k: v / measured_trainings_per_day for k, v in remaining_trainings.items()}


def advise(snap: Snapshot, *, seed_segments: list[tuple[int, int]] | None = None,
           measured_vram_per_training_gb: float | None = None,
           remaining_trainings: dict[str, int] | None = None,
           measured_trainings_per_day: float | None = None) -> Plan:
    """The full plan from one snapshot (+ optional measured facts)."""
    segments = seed_segments or [(0, 29), (30, 99), (100, 188), (189, 278),
                                 (279, 339), (340, 402), (403, 567)]
    pools = usable_pools(snap)
    regime, chunk = chunking(snap)
    pack, pack_note = recommend_pack(pools, measured_vram_per_training_gb=measured_vram_per_training_gb)
    order, blocks = stripe(segments, pools, pack)
    plan = Plan(
        regime=regime,
        chunk_tasks=chunk,
        search_pool=pick_search_pool(pools),
        stripe_pools=order,
        seed_pool_blocks=blocks,
        pack=pack,
        pack_note=pack_note,
        eta_days=eta(remaining_trainings or {}, measured_trainings_per_day),
    )
    for pool in ("U", "V"):
        v = snap.probe_states.get(pool, "")
        if v and "USABLE" not in v:
            plan.notes.append(f"pool {pool}: {v}")
    if snap.errors:
        plan.notes.append(f"telemetry degraded: {snap.errors}")
    plan.notes.append("advisory only — apply at batch boundaries; priorities untouched")
    return plan
