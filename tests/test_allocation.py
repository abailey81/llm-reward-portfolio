"""Tests for the adaptive allocation system (telemetry parsers + the advisor's doctrine)."""
from __future__ import annotations

from src.cluster.allocation import (advise, chunking, pick_search_pool, recommend_pack,
                                    stripe, usable_pools)
from src.cluster.telemetry import (Snapshot, parse_cluster_pending, parse_our_jobs,
                                   parse_qhost_gpu, probe_verdicts)

_QHOST = """HOSTNAME  ARCH  NCPU
----------------------------------------------------------------------------------------------
node-e00a-008           lx-amd64       36    2   36   36     -  188.4G       -    1.8T       -
    Host Resource(s):      hc:gpu=2.000000
node-e00a-014           lx-amd64       36    2   36   36 10.16  188.4G   25.2G    1.8T    9.2M
    Host Resource(s):      hc:gpu=1.000000
node-l00a-006           lx-amd64       36    2   36   36  0.34  188.4G   24.4G    1.8T   16.6M
    Host Resource(s):      hc:gpu=3.000000
node-u00a-001           lx-amd64       48    2   48   48  3.28  251.4G   34.6G    1.7T    1.0G
    Host Resource(s):      hc:gpu=4.000000
node-d00a-001           lx-amd64       36    2   36   36  1.00  188.4G   10.0G    1.8T    1.0M
"""

_PENDING = """job-ID  prior   name   user   state submit
------------------------------------------------------------
 100 3.4 a userA qw 07/24
 101 3.3 b userA qw 07/24
 102 0.0 c userB hqw 07/24
 103 3.2 d userC qw 07/24
"""

_MINE = """job-ID  prior   name   user   state submit
------------------------------------------------------------
 8323 3.18533 mr ucestes qw 07/23
 8323 0.00000 mr ucestes hqw 07/23
 10293 1.10000 probe_u ucestes qw 07/24
"""


def _snap(qw: int = 3000, probes: dict | None = None, pools: dict | None = None) -> Snapshot:
    return Snapshot(ts="t", pool_free=pools or {"EF": 3, "L": 3},
                    cluster_qw=qw, cluster_users=100,
                    our_jobs=[], probe_states=probes or {})


def test_parse_qhost_pools_and_counts() -> None:
    free = parse_qhost_gpu(_QHOST)
    assert free == {"EF": 3, "L": 3, "U": 4}  # d-node ignored (no pool, and no gpu line counted


def test_parse_pending_counts_eligible_and_users() -> None:
    qw, users = parse_cluster_pending(_PENDING)
    assert qw == 3 and users == 3  # hqw not counted as eligible; userB still a user


def test_parse_our_jobs_rows() -> None:
    rows = parse_our_jobs(_MINE)
    assert [r["state"] for r in rows] == ["qw", "hqw", "qw"]
    assert rows[0]["prior"] == 3.18533


def test_probe_verdicts_running_pending_restricted() -> None:
    jobs = [{"id": "10293", "prior": 1.0, "state": "r"},
            {"id": "10294", "prior": 0.0, "state": "qw"}]
    v = probe_verdicts(jobs, pending_hours=1.0)
    assert "USABLE" in v["U"] and v["V"].startswith("pending")
    v48 = probe_verdicts(jobs, pending_hours=49.0)
    assert "RESTRICTED" in v48["V"]


def test_chunking_two_regimes() -> None:
    assert chunking(_snap(qw=3000))[0] == "CONTENDED"
    assert chunking(_snap(qw=200)) == ("QUIET", 1)


def test_usable_pools_gates_uv_on_probe_verdict() -> None:
    s = _snap(pools={"EF": 2, "L": 1, "U": 4}, probes={"U": "pending (qw)"})
    assert "U" not in usable_pools(s)
    s2 = _snap(pools={"EF": 2, "L": 1, "U": 4}, probes={"U": "RUNNING (USABLE)"})
    assert usable_pools(s2)["U"] == 4


def test_search_pool_prefers_fastest_with_headroom() -> None:
    assert pick_search_pool({"EF": 5, "L": 2}) == "L"
    assert pick_search_pool({"EF": 5, "L": 1}) == "EF"   # L lacks the 2-GPU headroom bar
    assert pick_search_pool({"EF": 0, "L": 0}) == "EF"   # fallback


def test_stripe_blocks_are_contiguous_pool_homogeneous_and_cover() -> None:
    order, blocks = stripe([(0, 29), (30, 99)], {"EF": 2, "L": 2})
    assert order[0] == "L"  # faster pool first at equal free counts
    seen: list[tuple[int, int]] = []
    for part in blocks.split(","):
        pool, rng = part.split(":")
        a, b = (int(x) for x in rng.split("-"))
        assert pool in ("EF", "L") and a <= b
        seen.append((a, b))
    # full coverage, no overlap, contiguity within each segment
    covered = sorted(seen)
    assert covered[0][0] == 0 and covered[-1][1] == 99
    for (a1, b1), (a2, b2) in zip(covered, covered[1:]):
        assert a2 == b1 + 1


def test_recommend_pack_gated_on_measurement() -> None:
    pools = {"EF": 2, "L": 2, "U": 4}
    unmeasured, note = recommend_pack(pools, measured_vram_per_training_gb=None)
    assert set(unmeasured.values()) == {5} and "pending" in note
    measured, _ = recommend_pack(pools, measured_vram_per_training_gb=2.8)
    assert measured["EF"] == 5 and measured["L"] == 8 and measured["U"] == 10  # capped by table


def test_advise_end_to_end_plan_shape() -> None:
    s = _snap(qw=200, pools={"EF": 3, "L": 4}, probes={"U": "pending (qw)", "V": "pending (qw)"})
    plan = advise(s, measured_trainings_per_day=800.0,
                  remaining_trainings={"tier403": 6800})
    assert plan.regime == "QUIET" and plan.chunk_tasks == 1
    assert plan.search_pool == "L"
    assert plan.eta_days == {"tier403": 8.5}
    assert "priorities untouched" in plan.notes[-1]
    # The ★ rule: the plan can never render a priority ACTION — no `-p <n>` flag, no qalter.
    import re

    rendered = plan.render()
    assert "qalter" not in rendered
    assert not re.search(r"(?:^|\s)-p\s+-?\d", rendered)
