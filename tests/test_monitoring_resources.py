"""Focused tests for the long-run GPU-thermal + RAM resource guards (campaign-robustness §E / §C/§D).

The resource sampler already records ``gpu_temp`` + ``ram_pct``; these tests pin the WARN/ABORT
thresholds added to :meth:`RunMonitor._check_resource_anomalies` (inherited by ``ParallelMonitor``,
so one method covers serial + parallel monitors) and the ~60 s cooldown that prevents anomaly spam.
No torch / no SAC; the monitor runs headless (no TTY).
"""
from __future__ import annotations

import src.utils.monitoring as M
from src.utils.monitoring import ParallelMonitor, RunMonitor


def _monitor(tmp_path) -> RunMonitor:
    return RunMonitor(
        tmp_path / "run", title="t", total_arms=1, candidates_per_arm=1, train_steps=10, model="stub"
    )


def _kinds(mon: RunMonitor) -> list[str]:
    return [a["kind"] for a in mon._anomalies]


def test_no_anomaly_below_thresholds(tmp_path) -> None:
    mon = _monitor(tmp_path)
    before = len(mon._anomalies)
    mon._check_resource_anomalies({"gpu_temp": 70, "ram_pct": 60.0})
    assert len(mon._anomalies) == before  # nothing flagged in the safe band


def test_gpu_temp_warn_and_critical_fire_at_thresholds(tmp_path) -> None:
    mon = _monitor(tmp_path)
    mon._check_resource_anomalies({"gpu_temp": M._GPU_TEMP_WARN_C, "ram_pct": 50.0})
    assert "gpu_thermal_warn" in _kinds(mon)

    mon2 = _monitor(tmp_path / "b")
    mon2._check_resource_anomalies({"gpu_temp": M._GPU_TEMP_CRIT_C, "ram_pct": 50.0})
    assert "gpu_thermal_critical" in _kinds(mon2)


def test_ram_warn_and_critical_fire_at_thresholds(tmp_path) -> None:
    mon = _monitor(tmp_path)
    mon._check_resource_anomalies({"gpu_temp": 60, "ram_pct": M._RAM_PCT_WARN})
    assert "ram_pressure_warn" in _kinds(mon)

    mon2 = _monitor(tmp_path / "b")
    mon2._check_resource_anomalies({"gpu_temp": 60, "ram_pct": M._RAM_PCT_CRIT})
    assert "ram_pressure_critical" in _kinds(mon2)


def test_cooldown_dedups_repeated_thermal_anomalies(tmp_path) -> None:
    """A sustained-hot GPU must not spam anomalies on every ~0.3 s flush (60 s cooldown)."""
    mon = _monitor(tmp_path)
    for _ in range(5):
        mon._check_resource_anomalies({"gpu_temp": M._GPU_TEMP_CRIT_C, "ram_pct": 50.0})
    assert _kinds(mon).count("gpu_thermal_critical") == 1  # deduped by the cooldown


def test_missing_or_nonnumeric_fields_are_ignored(tmp_path) -> None:
    """A probe without gpu_temp/ram_pct (NVML/psutil absent) is a safe no-op."""
    mon = _monitor(tmp_path)
    before = len(mon._anomalies)
    mon._check_resource_anomalies({})  # empty sample (no GPU, no psutil)
    mon._check_resource_anomalies({"gpu_temp": None, "ram_pct": "n/a"})
    assert len(mon._anomalies) == before


def test_parallel_monitor_inherits_the_resource_guard(tmp_path) -> None:
    """ParallelMonitor gets the SAME guard (one edit covers serial + parallel)."""
    pm = ParallelMonitor(
        tmp_path / "par", title="t", total_arms=1, candidates_per_arm=1, train_steps=10, model="stub"
    )
    assert hasattr(pm, "_check_resource_anomalies")
    pm._check_resource_anomalies({"gpu_temp": M._GPU_TEMP_CRIT_C, "ram_pct": 50.0})
    assert "gpu_thermal_critical" in [a["kind"] for a in pm._anomalies]
