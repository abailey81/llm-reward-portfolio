"""The campaign-lane monitor's I/O half: mirroring the epilogue ledgers + gathering live inputs.

The pure checks are tested in ``test_campaign_health.py``. What is tested here is the part that can
silently make them USELESS: a ledger that never reaches the driver, or a gatherer that invents inputs
instead of leaving a check switched off.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from scripts.sentinel import _gather_campaign_lane
from src.cluster.poll import sync_epilogue_ledgers


# --- mirroring the epilogue ledgers ------------------------------------------------------------

class FakeRemote:
    """A minimal stand-in for the ssh runner over a fake remote ledger dir."""

    def __init__(self, files: dict[str, str]) -> None:
        self.files = dict(files)
        self.cats: list[str] = []

    def __call__(self, cmd: list[str]) -> str:
        if cmd[0] == "find":
            return "".join(f"{len(body.encode())} /r/ledger/{n}\n"
                           for n, body in sorted(self.files.items()))
        if cmd[0] == "cat":
            name = cmd[1].rsplit("/", 1)[-1]
            self.cats.append(name)
            return self.files[name]
        raise AssertionError(f"unexpected remote command {cmd}")


def _row(task: int, host: str, rc: int) -> str:
    return json.dumps({"task": task, "host": host, "rc": rc, "secs": 30}) + "\n"


def test_ledgers_land_locally_so_the_bad_node_check_can_see_them(tmp_path):
    """Without this the driver is blind to every task that died WITHOUT archiving anything —
    exactly the failures the ledger exists to record (pull_archive only carries outputs/)."""
    remote = FakeRemote({"a.epilogue.jsonl": _row(1, "nA", 0) + _row(2, "nA", 127)})
    landed = sync_epilogue_ledgers("/r/ledger", tmp_path, remote)
    assert set(landed) == {"a.epilogue.jsonl"}
    from src.cluster.ledger import host_task_counts, read_epilogue
    attempts, failed = host_task_counts(read_epilogue(tmp_path / "a.epilogue.jsonl"))
    assert attempts == {"nA": 2} and failed == {"nA": 1}


def test_an_UNCHANGED_ledger_is_never_re_transferred(tmp_path):
    """A finished array's ledger stops growing; re-sending it every tick for 24 days is waste. The
    size test is exact because the file is append-only."""
    remote = FakeRemote({"a.epilogue.jsonl": _row(1, "nA", 0)})
    sync_epilogue_ledgers("/r/ledger", tmp_path, remote)
    assert remote.cats == ["a.epilogue.jsonl"]
    assert sync_epilogue_ledgers("/r/ledger", tmp_path, remote) == {}
    assert remote.cats == ["a.epilogue.jsonl"]          # not fetched a second time


def test_a_GROWN_ledger_IS_re_fetched_and_replaces_the_local_copy(tmp_path):
    remote = FakeRemote({"a.epilogue.jsonl": _row(1, "nA", 0)})
    sync_epilogue_ledgers("/r/ledger", tmp_path, remote)
    remote.files["a.epilogue.jsonl"] += _row(2, "nB", 0)
    sync_epilogue_ledgers("/r/ledger", tmp_path, remote)
    from src.cluster.ledger import read_epilogue
    assert [r["host"] for r in read_epilogue(tmp_path / "a.epilogue.jsonl")] == ["nA", "nB"]


def test_local_bytes_match_remote_bytes_exactly_or_the_skip_test_breaks_forever(tmp_path):
    """Windows CRLF translation would inflate every local file, so the size comparison would never
    match again and every tick would re-transfer the whole ledger."""
    body = _row(1, "nA", 0) + _row(2, "nB", 1)
    sync_epilogue_ledgers("/r/ledger", tmp_path, FakeRemote({"a.epilogue.jsonl": body}))
    assert (tmp_path / "a.epilogue.jsonl").stat().st_size == len(body.encode())


def test_a_DEAD_remote_degrades_to_no_data_rather_than_killing_the_monitor(tmp_path):
    """Monitoring must never take down the thing it monitors — the archive is the completion truth,
    the ledger is only forensics."""
    def dead(cmd: list[str]) -> str:
        raise OSError("ssh: connection refused")

    assert sync_epilogue_ledgers("/r/ledger", tmp_path, dead) == {}


def test_torn_listing_lines_and_foreign_files_are_ignored(tmp_path):
    class Weird(FakeRemote):
        def __call__(self, cmd):
            if cmd[0] == "find":
                return "garbage\nNOTANINT /r/ledger/x.epilogue.jsonl\n12 /r/ledger/other.txt\n"
            return super().__call__(cmd)

    assert sync_epilogue_ledgers("/r/ledger", tmp_path, Weird({})) == {}


def test_the_ledger_sync_RIDES_the_shared_pull_so_the_mirror_is_never_stale(tmp_path,
                                                                           monkeypatch):
    """Wiring test: if nothing CALLS the sync, the bad-node check is permanently blind. It must run
    on the driver's own rate-limited pull window, into <mirror>/ledger where the sentinel looks."""
    import src.cluster.poll as poll
    from src.cluster.campaign import build_cluster_run

    calls: dict[str, object] = {}
    monkeypatch.setattr(poll, "pull_archive", lambda *a, **k: 0)
    monkeypatch.setattr(poll, "sync_epilogue_ledgers",
                        lambda remote, local, runner: calls.update(remote=remote,
                                                                   local=Path(local)) or {})
    monkeypatch.setattr("src.cluster.submit.ssh_runner", lambda host: (lambda cmd: ""))

    run = build_cluster_run(
        local_batch_root=str(tmp_path / "b"), local_archive_root=str(tmp_path / "mirror"),
        remote_root="/scratch/run", remote_outputs_root="/scratch/run/outputs",
        gold_dir="/scratch/gold",
    )
    run.pull()
    assert calls["remote"] == "/scratch/run/ledger"
    # <mirror>/ledger is exactly where _gather_campaign_lane looks; anywhere else = still blind.
    assert calls["local"] == tmp_path / "mirror" / "ledger"


def test_a_FAILING_ledger_sync_never_fails_the_pull(tmp_path, monkeypatch):
    """Forensics must not be able to break the transport the campaign actually depends on."""
    import src.cluster.poll as poll
    from src.cluster.campaign import build_cluster_run

    monkeypatch.setattr(poll, "pull_archive", lambda *a, **k: 7)
    monkeypatch.setattr(poll, "sync_epilogue_ledgers",
                        lambda *a, **k: (_ for _ in ()).throw(OSError("ssh died")))
    monkeypatch.setattr("src.cluster.submit.ssh_runner", lambda host: (lambda cmd: ""))

    run = build_cluster_run(
        local_batch_root=str(tmp_path / "b"), local_archive_root=str(tmp_path / "mirror"),
        remote_root="/scratch/run", remote_outputs_root="/scratch/run/outputs",
        gold_dir="/scratch/gold",
    )
    assert run.pull() == 7


# --- gathering the live inputs -----------------------------------------------------------------

def _write_record(d: Path, **fields) -> None:
    d.mkdir(parents=True, exist_ok=True)
    (d / "record.json").write_text(json.dumps({"run_id": d.name, **fields}), encoding="utf-8")


def test_an_EMPTY_run_dir_yields_no_ARCHIVE_derived_inputs_so_those_checks_stay_off(tmp_path):
    """A monitor that guesses is worse than one that is silent: absent artifacts must leave the
    checks switched OFF, not fed with defaults. (The rung ladder and the stop are pre-registered
    CONFIG facts, so they are present independently of any run dir — and the forecast built on them
    reports INFO until the first training completes.)"""
    from scripts.sentinel import evaluate_health

    lane = _gather_campaign_lane(tmp_path, {"now": time.time()})
    assert "chain_progress" not in lane and "host_attempts" not in lane
    assert "env_fp_labels" not in lane and "expected_cores" not in lane
    forecast = [c for c in evaluate_health({**lane, "done_test_units": 0}).checks
                if c.name == "rung_forecast"]
    assert [c.severity for c in forecast] == ["INFO"]


def test_chain_progress_is_measured_from_the_archive_not_declared(tmp_path):
    now = time.time()
    for i in range(3):
        _write_record(tmp_path / "search" / "bayes_opt" / f"c{i}")
    lane = _gather_campaign_lane(tmp_path, {"now": now})
    assert lane["chain_progress"]["bayes_opt"]["completed"] == 3
    from src.cluster.lanes import SERIAL_CHAIN_STEPS
    assert lane["chain_progress"]["bayes_opt"]["total"] == SERIAL_CHAIN_STEPS["bayes_opt"]
    assert lane["chain_progress"]["bayes_opt"]["hours_since_last"] < 1.0


def test_a_STALLED_chain_is_visible_end_to_end_from_files_on_disk(tmp_path):
    """The whole path: archive mtimes -> gatherer -> check -> a WARN the operator sees."""
    import os
    d = tmp_path / "search" / "bayes_opt" / "c0"
    _write_record(d)
    old = time.time() - 20 * 3600
    os.utime(d / "record.json", (old, old))
    lane = _gather_campaign_lane(tmp_path, {"now": time.time()})
    assert check_chain(lane)["severity"] == "WARN"


def check_chain(lane: dict) -> dict:
    from src.cluster.campaign_health import check_chain_progress
    return check_chain_progress(lane["chain_progress"]).as_dict()


def test_host_attribution_is_gathered_from_the_mirrored_ledgers(tmp_path):
    (tmp_path / "ledger").mkdir(parents=True)
    (tmp_path / "ledger" / "a.epilogue.jsonl").write_text(
        _row(1, "nA", 127) + _row(2, "nA", 127), encoding="utf-8")
    lane = _gather_campaign_lane(tmp_path, {"now": time.time()})
    assert lane["host_attempts"] == {"nA": 2} and lane["host_failures"] == {"nA": 2}


def test_ONE_half_written_record_does_not_take_the_live_census_dark(tmp_path):
    """load_all is all-or-nothing (right for the fail-loud GATE, fatal for a live monitor): a single
    torn record mid-campaign must not blind the homogeneity check to the other 40,000."""
    _write_record(tmp_path / "test" / "a" / "s1", env_fingerprint={"label": "e|dev=cpu"})
    torn = tmp_path / "test" / "a" / "s2"
    torn.mkdir(parents=True)
    (torn / "record.json").write_text('{"env_fingerprint": {"lab', encoding="utf-8")
    lane = _gather_campaign_lane(tmp_path, {"now": time.time()})
    assert lane["env_fp_labels"] == {"e|dev=cpu": 1}


def test_the_homogeneity_census_covers_the_SCORED_leg_only(tmp_path):
    """The search leg legitimately explores; it is the scored leg whose CRN pairing a substrate mix
    would break, so a search-leg-only archive must produce no census."""
    _write_record(tmp_path / "search" / "llm_tail" / "c0",
                  env_fingerprint={"label": "e|dev=cuda"})
    assert "env_fp_labels" not in _gather_campaign_lane(tmp_path, {"now": time.time()})
    _write_record(tmp_path / "test" / "llm_tail" / "s1", env_fingerprint={"label": "e|dev=cpu"})
    lane = _gather_campaign_lane(tmp_path, {"now": time.time()})
    assert lane["env_fp_labels"] == {"e|dev=cpu": 1}


def test_the_capacity_FORECAST_survives_an_advisor_cycle_and_reaches_the_check(tmp_path,
                                                                              monkeypatch):
    """save_state REPLACES the state file, so the advisor must carry the lane facts forward — a
    single cycle that dropped them would silently switch the capacity check back off mid-campaign,
    and it is the one lane input derivable from neither the archive nor the pre-registration."""
    from src.cluster import telemetry
    from src.cluster.campaign_health import check_capacity_accumulation

    state_path = tmp_path / "allocation_state.json"
    telemetry.save_state({"lane_expected_cores": 2400, "lane_forecast_utc": 1.0}, state_path)
    carried = {k: v for k, v in telemetry.load_state(state_path).items()
               if k not in ("prev_regime", "last_plan")}
    telemetry.save_state({**carried, "prev_regime": "QUIET", "last_plan": {"pack": 5}}, state_path)

    after = telemetry.load_state(state_path)
    assert after["lane_expected_cores"] == 2400 and after["last_plan"] == {"pack": 5}
    c = check_capacity_accumulation({"status": "plateaued", "late_mean_cores": 600},
                                    expected_cores=after["lane_expected_cores"], hours_in=8.0)
    assert c.severity == "WARN" and "RE-FORECAST" in c.detail


def test_the_stop_and_the_rung_ladder_come_from_the_PREREGISTRATION_not_a_GO_day_entry():
    """A launch-day step that can be forgotten would leave the rung forecast silently off for the
    whole campaign. Both facts are pre-registered, so they are read, not re-declared."""
    from scripts.sentinel import _prereg_stop_and_rungs
    from src.cluster.lanes import total_trainings
    from src.utils.config import load_config

    hours, rungs = _prereg_stop_and_rungs(time.time())
    tiers = load_config("preregistration")["seeds"]["tiers"]
    assert hours is not None and hours > 0
    assert set(rungs) == set(tiers)
    assert all(rungs[t] == total_trainings(t) for t in tiers)   # costed, never hand-typed
    assert rungs[min(tiers)] < rungs[max(tiers)]


def test_the_rung_forecast_is_live_from_config_end_to_end(tmp_path):
    """The gathered ladder must actually reach the check and name a rung."""
    from src.cluster.campaign_health import check_rung_forecast

    lane = _gather_campaign_lane(tmp_path, {"now": time.time()})
    c = check_rung_forecast(completed_trainings=12_000, elapsed_hours=100.0,
                            hours_remaining=lane["lane_hours_remaining"],
                            rung_targets=lane["rung_targets"])
    assert c.evidence["reachable_rung"] in lane["rung_targets"]


def test_elapsed_falls_back_to_the_earliest_record_when_GO_recorded_no_start(tmp_path):
    import os
    d = tmp_path / "test" / "a" / "s1"
    _write_record(d)
    old = time.time() - 12 * 3600
    os.utime(d / "record.json", (old, old))
    lane = _gather_campaign_lane(tmp_path, {"now": time.time()})
    assert lane["lane_hours_in"] == pytest.approx(12.0, abs=0.1)
