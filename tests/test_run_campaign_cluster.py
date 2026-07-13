"""Entry-point tests for scripts/run_campaign_cluster.py — the config assembly + the dry-run wiring
validation, exercised WITHOUT a cluster (synthetic panel, stub author)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ (for the shared FakeCluster)
import run_campaign_cluster as rcc  # noqa: E402


def test_parse_seeds_ranges_lists_and_dedup():
    assert rcc._parse_seeds("0-4") == [0, 1, 2, 3, 4]
    assert rcc._parse_seeds("0,1,5") == [0, 1, 5]
    assert rcc._parse_seeds("0-2,1-3") == [0, 1, 2, 3]  # overlapping -> deduped + sorted
    assert rcc._parse_seeds("0-402") == list(range(403))


def test_assemble_cluster_inputs_synthetic_is_arm_independent_and_author_ready():
    inp = rcc.assemble_cluster_inputs(
        arms=["distributional", "scalar"], seeds=[0, 1, 2], output_dir="outputs/_t",
        synthetic=True, train_steps=200, n_trials=1, candidates=4, generations=2,
        search_seed=0, embargo=21, pass_mode="A", provider="stub", llm_cfg=None, resume=False,
    )
    # opts are arm-independent (the arm is a run_search_arm parameter)
    assert inp["opts_for"]("distributional") is inp["opts_for"]("scalar")
    opts = inp["opts"]
    # everything the cluster author + spec builder consume is present
    for key in ("env_cfg", "n_assets", "provider", "pass_mode", "generations", "candidates",
                "seed", "model", "train_steps", "data", "cvar_alpha", "window"):
        assert key in opts, f"opts missing {key}"
    # test_leg_kwargs carries the windows the nodes reuse
    tlk = inp["test_leg_kwargs"]
    assert set(tlk) == {"panel_descriptor", "env_cfg", "agent_cfg", "train_window", "val_window",
                        "test_window", "embargo", "lookback"}
    tw, vw, te = inp["windows"]
    assert tw[0] < tw[1] <= vw[0] < vw[1] <= te[0] < te[1]  # ordered, embargoed
    assert inp["frozen_root"].name == "frozen"


def test_dry_run_validates_wiring_without_a_cluster(capsys):
    rc = rcc.main(["--dry-run", "--synthetic", "--arms", "distributional", "scalar",
                   "--seeds", "0-5", "--candidates", "4", "--generations", "2"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "wiring valid" in out and "2 arms" in out


def test_capstone_full_roster_end_to_end(tmp_path):
    """The WHOLE stack in one shot: assemble the REAL (synthetic) config -> run an LLM arm + a
    family arm + an H1 baseline CONCURRENTLY through a fake cluster -> assert the complete archive
    in the analyze_campaign parity layout (search/<arm>, test/<arm>, test/baseline_<name>)."""
    from test_cluster_campaign import FakeCluster, _inject_select_freeze  # shared fake

    from src.cluster.campaign import ClusterRun, run_campaign_on_cluster
    from src.io.results import load_all

    inp = rcc.assemble_cluster_inputs(
        arms=["distributional", "random_search"], seeds=[0, 1], output_dir=str(tmp_path),
        synthetic=True, train_steps=200, n_trials=1, candidates=2, generations=1,
        search_seed=0, embargo=21, pass_mode="A", provider="stub", llm_cfg=None, resume=False,
    )
    fake = FakeCluster(tmp_path)
    run = ClusterRun(run_batch=fake.run_batch, spec_archive_root=str(tmp_path), read_root=tmp_path)
    _inject_select_freeze(run)

    results = run_campaign_on_cluster(
        ["distributional", "random_search"], inp["opts_for"], inp["seeds"], run,
        test_leg_kwargs=inp["test_leg_kwargs"], frozen_root=tmp_path / "frozen",
        baseline_names=["differential_sharpe"],
    )
    assert all(results[k]["ok"] for k in ("distributional", "random_search", "__baselines__"))

    def ids(sub):
        return {r["run_id"] for r in load_all(str(tmp_path / sub))}

    # LLM arm + family arm both produced SEARCH candidates (disjoint sub-root)
    assert ids("search/distributional") == {"distributional-g0-c0", "distributional-g0-c1"}
    assert ids("search/random_search") == {"random_search-c0", "random_search-c1"}
    # every unit produced its sealed TEST records (arms + the H1 baseline), all under test/
    assert ids("test/distributional") == {"distributional-s0", "distributional-s1"}
    assert ids("test/random_search") == {"random_search-s0", "random_search-s1"}
    assert ids("test/baseline_differential_sharpe") == {
        "baseline_differential_sharpe-s0", "baseline_differential_sharpe-s1"}
    # search and test roots are disjoint (BUG-1 invariant) across the whole roster
    assert (tmp_path / "search").is_dir() and (tmp_path / "test").is_dir()


# --------------------------------------------------------------------------- #
# P19 (2026-07-13 pre-spend audit): the cluster entry point mirrors the laptop's
# verify-or-refuse freeze gate. These lock the semantics freeze-state-independently
# (enforce_freeze is monkeypatched on run_campaign, which main imports at call time).
# --------------------------------------------------------------------------- #
def test_freeze_gate_refuses_unfrozen_non_dry_run(tmp_path, monkeypatch):
    import run_campaign as rc

    def _refuse(*, allow_unfrozen=False):
        raise rc.CampaignNotFrozenError("NOT frozen (test)")

    monkeypatch.setattr(rc, "enforce_freeze", _refuse)
    import pytest

    with pytest.raises(SystemExit, match="NOT frozen"):
        rcc.main(["--synthetic", "--arms", "distributional", "--output-dir", str(tmp_path)])


def test_freeze_gate_exempts_dry_run(tmp_path, monkeypatch):
    import run_campaign as rc

    def _refuse(*, allow_unfrozen=False):  # would sink the run if the exemption regressed
        raise rc.CampaignNotFrozenError("NOT frozen (test)")

    monkeypatch.setattr(rc, "enforce_freeze", _refuse)
    rc_code = rcc.main(["--dry-run", "--synthetic", "--arms", "distributional",
                        "--output-dir", str(tmp_path)])
    assert rc_code == 0


def test_freeze_gate_allow_unfrozen_passes_through(tmp_path, monkeypatch):
    """--allow-unfrozen reaches enforce_freeze with the flag set, then main PROCEEDS to the
    next guard (F2 dirty-dir refusal proves we got past the gate without ssh)."""
    import run_campaign as rc

    calls: list[bool] = []

    def _stamp(*, allow_unfrozen=False):
        calls.append(allow_unfrozen)
        return {"enforced": True, "frozen": False, "allow_unfrozen": allow_unfrozen}

    monkeypatch.setattr(rc, "enforce_freeze", _stamp)
    dirty = tmp_path / "search" / "distributional" / "x"
    dirty.mkdir(parents=True)
    (dirty / "record.json").write_text("{}", encoding="utf-8")
    import pytest

    with pytest.raises(SystemExit, match="RE-AUTHORS"):
        rcc.main(["--synthetic", "--arms", "distributional", "--allow-unfrozen",
                  "--output-dir", str(tmp_path)])
    assert calls == [True]


def test_write_campaign_summary_mirrors_run_campaign_keys(tmp_path):
    """P7: the cluster writes an analyze/sentinel-compatible campaign_summary.json at the mirror
    root (test_window is what analyze_campaign's DeMiguel floor reads)."""
    import json

    inp = rcc.assemble_cluster_inputs(
        arms=["distributional"], seeds=[0], output_dir=str(tmp_path), synthetic=True,
        train_steps=200, n_trials=1, candidates=2, generations=1, search_seed=0,
        embargo=21, pass_mode="A", provider="stub", llm_cfg=None, resume=False,
    )
    rcc._write_campaign_summary(str(tmp_path), inp, freeze_stamp={"enforced": True},
                                extra={"tiered": True, "all_arms_tested": True, "exit_code": 0})
    s = json.loads((tmp_path / "campaign_summary.json").read_text(encoding="utf-8"))
    assert s["source"] == "run_campaign_cluster"
    assert s["gold_panel"] == {"synthetic": True}
    assert s["freeze"] == {"enforced": True}
    assert s["all_arms_tested"] is True and s["tiered"] is True
    tw = s["test_window"]  # exactly what analyze_campaign.main consumes for the benchmark floor
    assert isinstance(tw, list) and len(tw) == 2 and all(isinstance(x, int) for x in tw)


def test_h3_singleshot_flag_forces_shape_and_dry_runs(tmp_path, capsys):
    """C5: --h3-singleshot forces arms=[distributional] + generations from campaign.yaml's
    h3_singleshot_generations (1), and the keyless dry-run validates the wiring."""
    rc = rcc.main(["--h3-singleshot", "--dry-run", "--synthetic",
                   "--candidates", "4", "--output-dir", str(tmp_path)])
    assert rc == 0
    outtext = capsys.readouterr().out
    assert "1 arms" in outtext  # distributional only


def test_h3_singleshot_conflicts_with_tiered(tmp_path):
    import pytest

    with pytest.raises(SystemExit, match="SEPARATE invocations"):
        rcc.main(["--h3-singleshot", "--tiered", "--dry-run", "--synthetic",
                  "--output-dir", str(tmp_path)])
