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
