"""The makespan model that decides the CPU/GPU lane split (2026-07-26).

The point of these tests is to lock the NON-OBVIOUS result: past ~1,640 CPU cores the campaign
stops being throughput-bound and becomes latency-bound on ONE 25-training sequential chain, so the
highest-leverage action stops being "more cores" and becomes "put 30 trainings on one GPU".
"""
from __future__ import annotations

import pytest

from src.cluster.lanes import (
    CONFIRMATORY_CPU_POOLS,
    CPU_STEPS_PER_S_PER_CORE,
    EXCLUDED_CPU_POOLS,
    GPU_PACK1_STEPS_PER_S,
    cpu_saturation_cores,
    plan_lanes,
    total_trainings,
    training_core_hours,
)


def test_measured_constants_give_the_documented_per_training_cost():
    """400k steps at the measured 13.0 steps/s/core = 8.54 core-hours (dossier §0-PRE M3)."""
    assert training_core_hours() == pytest.approx(8.547, rel=1e-3)
    # one GPU at pack-1 is ~7.8x faster PER TRAINING - the latency lever
    assert training_core_hours() / training_core_hours(steps_per_s=GPU_PACK1_STEPS_PER_S) == \
        pytest.approx(GPU_PACK1_STEPS_PER_S / CPU_STEPS_PER_S_PER_CORE, rel=1e-6)


def test_work_model_matches_the_registered_design():
    """total = 1,800 search + 71n test (9 core arms + 10 legs x 5 + 11 H1 canon + 1 H3).
    The roster grew 7 -> 9 on 2026-07-26 (+cma_es, +tpe as N4 CONFIRMATORY H4 comparators)."""
    assert total_trainings(0) == 1_800          # 9x30 core + 30 H3 + 10 legs x 5 x 30
    assert total_trainings(30) == 3_930
    assert total_trainings(403) == 30_413
    assert total_trainings(568) == 42_128


def test_below_the_crossover_the_campaign_is_throughput_bound():
    p = plan_lanes(rung=568, cpu_cores=628)
    assert p.binding == "throughput"
    assert p.makespan_days == pytest.approx(23.9, abs=0.5)
    assert "more CPU cores DO still help" in " ".join(p.notes)


def test_ABOVE_the_crossover_more_cores_buy_NOTHING():
    """THE headline result: 2,000 and 3,000 cores give the SAME makespan, because a 25-training
    serial chain -- not capacity -- is what the campaign is waiting on."""
    p2000 = plan_lanes(rung=568, cpu_cores=2000)
    p3000 = plan_lanes(rung=568, cpu_cores=3000)
    assert p2000.binding == "critical_chain" and p3000.binding == "critical_chain"
    assert p2000.makespan_days == pytest.approx(p3000.makespan_days, rel=1e-9)
    assert p2000.makespan_days == pytest.approx(8.90, abs=0.05)
    assert "MORE CPU CORES BUY NOTHING" in " ".join(p2000.notes)


def test_the_crossover_sits_near_1640_cores():
    sat = cpu_saturation_cores(rung=568, bayes_on_gpu=False)
    assert sat == pytest.approx(1685, rel=0.03)
    # at the crossover the two terms coincide
    p = plan_lanes(rung=568, cpu_cores=int(sat))
    assert p.throughput_days == pytest.approx(p.critical_chain_days, rel=0.02)


def test_a_gpu_for_bayes_ALONE_no_longer_unlocks_the_plan_TPE_becomes_the_pole():
    """Once cma_es/tpe became N4 CONFIRMATORY arms (2026-07-26), moving ONLY the 25-step GP chain
    to a GPU stops being sufficient: TPE's 20 SERIAL steps (batched startup) become the new
    critical path at 1 thread. Locked because the obvious-but-wrong move is to buy a GPU for
    bayes and expect the makespan to fall — it barely does."""
    cpu_only = plan_lanes(rung=568, cpu_cores=2500, bayes_on_gpu=False)
    with_gpu = plan_lanes(rung=568, cpu_cores=2500, bayes_on_gpu=True)

    assert cpu_only.makespan_days == pytest.approx(8.90, abs=0.05)   # bayes 25 serial binds
    assert with_gpu.makespan_days == pytest.approx(7.12, abs=0.1)    # ...now TPE's 20 binds
    assert with_gpu.binding == "critical_chain", "TPE, not capacity, is what it waits on"
    assert with_gpu.makespan_days < cpu_only.makespan_days           # a real but modest gain

    # THE ACTUAL UNLOCK is THREADING, which shortens EVERY cpu chain at once (no GPU needed).
    threaded = plan_lanes(rung=568, cpu_cores=2500, chain_threads=8)
    assert threaded.binding == "throughput"
    assert threaded.makespan_days < with_gpu.makespan_days


def test_the_gpu_is_an_optimisation_never_a_dependency():
    """Grade security: with NO GPU at all the campaign still completes in 8.9 days, well inside the
    31-day GO->Aug-27 window. The GPU makes it faster; its absence never blocks."""
    p = plan_lanes(rung=568, cpu_cores=2000, bayes_on_gpu=False)
    assert p.makespan_days < 31
    assert "never a blocker" in " ".join(p.notes)


def test_gpu_lane_does_not_help_the_FLOOR_rung_much():
    """At n=30 the work is small, so the serial chain dominates completely -- a useful sanity check
    that the model is not just scaling everything linearly."""
    p = plan_lanes(rung=30, cpu_cores=2000, bayes_on_gpu=False)
    assert p.binding == "critical_chain"
    assert p.makespan_days == pytest.approx(8.90, abs=0.05)


def test_cpu_lane_excludes_AMD_and_gpu_node_pools_with_stated_reasons():
    """Both exclusions are SCIENCE/ETIQUETTE decisions and must stay encoded, not remembered."""
    assert CONFIRMATORY_CPU_POOLS == ("d", "b")
    assert "t" in EXCLUDED_CPU_POOLS and "CRN" in EXCLUDED_CPU_POOLS["t"]
    for gpu_pool in ("e", "f", "l", "u", "v"):
        assert "blocks GPU jobs" in EXCLUDED_CPU_POOLS[gpu_pool]
    assert not set(CONFIRMATORY_CPU_POOLS) & set(EXCLUDED_CPU_POOLS)


def test_thread_counts_are_BOUND_to_the_registered_config_not_mirrored():
    """R107 registered the thread regime in `config/preregistration.yaml: execution`. A hardcoded
    copy in code is the DEFAULTS-CLASS bug the 2026-07-18 sweep killed for B*/candidates/
    generations — a mirror drifts silently. Bind them so drift is impossible."""
    from src.cluster.lanes import CPU_CHAIN_THREADS
    from src.utils.config import cfg_get, load_config

    execution = cfg_get(load_config("preregistration"), "execution", {}) or {}
    assert execution, "R107's execution block is missing from config/preregistration.yaml"
    assert CPU_CHAIN_THREADS == int(execution["chain_thread_count"]), \
        "lanes.CPU_CHAIN_THREADS has drifted from the REGISTERED chain_thread_count"
    assert int(execution["test_leg_thread_count"]) == 1, \
        "the SCORED leg must stay 1-thread: CRN bit-exactness lives there"
    assert int(execution["chain_thread_count_max"]) == 8, \
        "16 threads measured SLOWER than 8 — the registered ceiling must hold"


def test_the_thread_curve_has_a_measured_optimum_at_8_and_REGRESSES_at_16():
    """Jobs 17784/17836: two independent runs, 8 threads ~2.7x, 16 threads back down to 2.11x
    (small-matmul oversubscription). Locked so nobody 'optimises' the chain to 16 threads."""
    from src.cluster.lanes import CPU_CHAIN_THREADS, CPU_THREAD_SPEEDUP

    assert CPU_CHAIN_THREADS == 8
    assert CPU_THREAD_SPEEDUP[8] == max(CPU_THREAD_SPEEDUP.values())
    assert CPU_THREAD_SPEEDUP[16] < CPU_THREAD_SPEEDUP[8], "16 threads measured SLOWER than 8"
    # monotone increasing up to the optimum
    assert CPU_THREAD_SPEEDUP[1] < CPU_THREAD_SPEEDUP[2] < CPU_THREAD_SPEEDUP[4] < CPU_THREAD_SPEEDUP[8]


def test_threading_the_chain_REMOVES_the_need_for_a_gpu():
    """THE result of the sweep: at 8 threads the chain drops below the throughput term on pure CPU,
    so the campaign is throughput-bound WITHOUT any GPU. The GPU becomes optional, not required."""
    one_thread = plan_lanes(rung=568, cpu_cores=2000, chain_threads=1)
    threaded = plan_lanes(rung=568, cpu_cores=2000, chain_threads=8)

    assert one_thread.binding == "critical_chain"       # 8.9 d chain dominates
    assert threaded.binding == "throughput"             # ...until the chain is threaded
    assert threaded.critical_chain_days == pytest.approx(3.27, abs=0.1)
    assert threaded.makespan_days == pytest.approx(7.50, abs=0.2)
    assert threaded.makespan_days < one_thread.makespan_days

    # and with a GPU on top the makespan is UNCHANGED - the GPU no longer buys anything here
    with_gpu = plan_lanes(rung=568, cpu_cores=2000, chain_threads=8, bayes_on_gpu=True)
    assert with_gpu.makespan_days == pytest.approx(threaded.makespan_days, rel=1e-9)


def test_threading_pushes_the_cpu_saturation_point_out():
    """More cores keep paying for longer once the chain is threaded."""
    assert cpu_saturation_cores(568, chain_threads=8) > cpu_saturation_cores(568, chain_threads=1)
    assert cpu_saturation_cores(568, chain_threads=8) == pytest.approx(4584, rel=0.05)


def test_batching_TPE_keeps_it_OFF_the_critical_path():
    """TPE drove Optuna with `study.optimize` (one trial at a time) = a 30-step serial chain,
    LONGER than GP-EI's 25. Now that `campaign.run_family_search_arm` passes `batch_eval_fn`, the
    startup trials go as ONE array and the chain is 30-10 = 20 — so `bayes_opt` (25) is once again
    the longest, and including the DFO arms no longer lengthens the critical path at all."""
    from src.cluster.lanes import _BAYES_SERIAL_STEPS, _TPE_SERIAL_STEPS

    assert _TPE_SERIAL_STEPS == 20, "TPE's serial chain must reflect the WIRED batched reality"
    assert _TPE_SERIAL_STEPS < _BAYES_SERIAL_STEPS, "batched TPE must no longer be the long pole"

    default = plan_lanes(rung=568, cpu_cores=2000, chain_threads=8)
    with_dfo = plan_lanes(rung=568, cpu_cores=2000, chain_threads=8, include_dfo=True)

    # bayes (25) still dominates, so the DFO arms are fully absorbed
    assert with_dfo.critical_chain_days == pytest.approx(default.critical_chain_days, rel=1e-9)
    assert with_dfo.makespan_days == pytest.approx(default.makespan_days, rel=1e-9)
    assert with_dfo.binding == "throughput"


def test_plan_renders_the_binding_constraint_for_an_operator():
    text = plan_lanes(rung=568, cpu_cores=3000).render()
    assert "MAKESPAN" in text and "BINDING: critical_chain" in text


@pytest.mark.parametrize("bad", [0, -1])
def test_rejects_nonsense_inputs(bad):
    with pytest.raises(ValueError):
        plan_lanes(rung=568, cpu_cores=bad)
    with pytest.raises(ValueError):
        training_core_hours(steps_per_s=bad)


def test_saturation_is_a_CURVE_PROPERTY_and_is_STRUCTURALLY_PERMITTED():
    """Guards a real confusion (Tamer, 2026-07-26: "who said we can get 4584 cores?" then "who
    said not attainable?"). BOTH corrections matter, and they are different:

    1. `cpu_saturation_cores` answers only "above what point do more cores stop helping?" — it is a
       property of the WORK CURVE and says nothing about availability. Never quote it beside
       measured capacity without labelling which is which.
    2. It is NOT "unattainable". SGE's `maxujobs = 1000` (max RUNNING jobs per user) at 8 cores per
       job permits ~8,000 cores — comfortably ABOVE saturation — and the d+b pools hold 11,160
       cores. Whether we GET there depends on free capacity and what the scheduler grants, both of
       which are unmeasured above the 636 we actually observed. So: push for it.

    This test therefore locks the STRUCTURAL headroom and the fact that the governor scales with
    free capacity — deliberately NOT any ordering that depends on a sampled free-core reading,
    since rising capacity is good news and must never fail a test.
    """
    from src.cluster.killswitch import ABSOLUTE_CORE_CEILING, plan_footprint

    saturation = cpu_saturation_cores(568, chain_threads=8)

    MAXUJOBS, CORES_PER_JOB = 1000, 8          # qconf -ssconf, and the measured best job shape
    assert MAXUJOBS * CORES_PER_JOB > saturation, (
        "saturation must sit INSIDE the scheduler's structural per-user headroom — otherwise it "
        "really would be unreachable and the 'push for more cores' plan would be wrong")
    assert ABSOLUTE_CORE_CEILING >= MAXUJOBS * CORES_PER_JOB, (
        "our own backstop must not bind below what SGE structurally permits")

    # the governor must TAKE more when more is free — so a generous cluster is exploited, not capped
    lo, _ = plan_footprint(free_cores=4_500, pending_jobs=100)
    hi, _ = plan_footprint(free_cores=9_000, pending_jobs=100)
    assert hi > lo, "plan_footprint must scale with free capacity"
    assert hi >= saturation, "on a genuinely idle cluster the policy must allow reaching saturation"

    # ...and past saturation the makespan genuinely stops improving (the floor is real)
    at_sat = plan_lanes(rung=568, cpu_cores=int(saturation), chain_threads=8)
    beyond = plan_lanes(rung=568, cpu_cores=int(saturation) * 2, chain_threads=8)
    # rel=1e-3, not 1e-9: at exactly int(saturation) the throughput term still sits a hair ABOVE
    # the chain (integer-core rounding), so the two agree to ~1e-4, not to machine precision.
    assert beyond.makespan_days == pytest.approx(at_sat.makespan_days, rel=1e-3)
    assert beyond.binding == "critical_chain"
    # DOUBLING the cores past saturation buys nothing at all - that floor is real
    assert beyond.makespan_days == pytest.approx(beyond.critical_chain_days, rel=1e-9)
