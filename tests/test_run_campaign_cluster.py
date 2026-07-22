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


def test_root_suffix_validation_and_h3_conflict(tmp_path, monkeypatch):
    """C6-class guard: --root-suffix must be [a-z0-9_]+ and cannot combine with --h3-singleshot
    (which manages its own roots). Validation fires before any cluster contact."""
    import pytest
    import run_campaign as rc

    monkeypatch.setattr(rc, "enforce_freeze",
                        lambda allow_unfrozen=False: {"enforced": True, "frozen": True})
    with pytest.raises(SystemExit, match="lowercase"):
        rcc.main(["--synthetic", "--root-suffix", "Curve-C10", "--output-dir", str(tmp_path)])
    with pytest.raises(SystemExit, match="do not combine"):
        rcc.main(["--synthetic", "--h3-singleshot", "--root-suffix", "curve_c10",
                  "--output-dir", str(tmp_path)])


# ---------------------------------------------------------------------------------------------
# 2026-07-18 DEFAULTS-CLASS SWEEP regression lock (the launch-critical B*-resolution bug + its
# class): argparse defaults must NEVER hardcode mirrors of frozen config values — None resolves
# from the same keys the laptop main reads, asserted against the pre-registration where bound.
# ---------------------------------------------------------------------------------------------

def test_design_argparse_defaults_are_none_not_hardcoded_mirrors():
    """The bug class itself: a hardcoded default (30/6/30/21/25k) is a mirror that drifts."""
    args = rcc.build_parser().parse_args([])
    for name in ("train_steps", "candidates", "generations", "n_trials", "embargo"):
        assert getattr(args, name) is None, f"--{name} regressed to a hardcoded config mirror"


def test_bstar_none_resolves_from_campaign_yaml_and_matches_prereg():
    """THE launch-critical instance: train_steps=None must assemble at campaign.yaml's B*
    (the R77 400k), not prototype.yaml's 25k."""
    from src.utils.config import cfg_get, load_config

    expected = int(cfg_get(load_config("campaign"), "train_steps_per_candidate", 0))
    assert expected > 0
    inp = rcc.assemble_cluster_inputs(
        arms=["distributional"], seeds=[0], output_dir="outputs/_t",
        synthetic=True, train_steps=None, n_trials=1, candidates=4, generations=2,
        search_seed=0, embargo=21, pass_mode="A", provider="stub", llm_cfg=None, resume=False,
    )
    assert int(inp["agent_cfg"]["train_steps_per_candidate"]) == expected
    assert int(inp["opts"]["train_steps"]) == expected
    prereg = int(cfg_get(load_config("preregistration"), "train_steps_per_candidate", 0))
    assert expected == prereg  # the mirror pair the assembly asserts


def test_bstar_mirror_drift_refuses_assembly(monkeypatch):
    """If campaign.yaml and preregistration.yaml disagree on B*, assembly must refuse loudly."""
    import pytest

    import src.utils.config as cfgmod

    real = cfgmod.load_config

    def drifted(name, *a, **k):
        cfg = real(name, *a, **k)
        if name == "preregistration":
            cfg = dict(cfg)
            cfg["train_steps_per_candidate"] = 12345  # deliberate drift
        return cfg

    monkeypatch.setattr(cfgmod, "load_config", drifted)
    with pytest.raises(SystemExit, match="mirror drift"):
        rcc.assemble_cluster_inputs(
            arms=["distributional"], seeds=[0], output_dir="outputs/_t",
            synthetic=True, train_steps=None, n_trials=1, candidates=4, generations=2,
            search_seed=0, embargo=21, pass_mode="A", provider="stub", llm_cfg=None,
            resume=False,
        )


def test_main_resolves_all_design_values_from_configs(monkeypatch):
    """A flag-free launch (the supervisor line's shape) must resolve candidates/generations/
    n_trials/embargo from campaign.yaml + inference.yaml, laptop-parity, and leave train_steps
    None for the asserted in-assembly resolution."""
    captured = {}
    real = rcc.assemble_cluster_inputs

    def spy(**kw):
        captured.update(kw)
        return real(**kw)

    monkeypatch.setattr(rcc, "assemble_cluster_inputs", spy)
    rc = rcc.main(["--dry-run", "--synthetic", "--arms", "distributional"])
    assert rc == 0
    from src.utils.config import cfg_get, load_config

    camp = load_config("campaign")
    assert captured["candidates"] == int(camp["candidates_per_arm"])
    assert captured["generations"] == int(cfg_get(camp.get("llm") or {}, "generations", 1))
    assert captured["n_trials"] == captured["candidates"]  # laptop parity (run_campaign.py:2138)
    inf = load_config("inference")
    assert captured["embargo"] == int(cfg_get(cfg_get(inf, "splits", {}),
                                              "embargo_trading_days", 21))
    assert captured["train_steps"] is None


def test_candidates_mirror_drift_refuses_launch(monkeypatch):
    """campaign.yaml candidates_per_arm vs preregistration.yaml matched_budget must agree."""
    import pytest

    import src.utils.config as cfgmod

    real = cfgmod.load_config

    def drifted(name, *a, **k):
        cfg = real(name, *a, **k)
        if name == "preregistration":
            cfg = dict(cfg)
            cfg["matched_budget"] = 99
        return cfg

    monkeypatch.setattr(cfgmod, "load_config", drifted)
    with pytest.raises(SystemExit, match="mirror drift"):
        rcc.main(["--dry-run", "--synthetic", "--arms", "distributional"])


def test_real_spend_refuses_explicit_design_overrides():
    """Pass-mode B without --allow-unfrozen must refuse ANY explicit design flag (the guard that
    makes the resolved-and-asserted path the only real-spend path)."""
    import pytest

    with pytest.raises(SystemExit, match="explicit design override"):
        rcc.main(["--dry-run", "--pass-mode", "B", "--candidates", "30",
                  "--arms", "distributional"])


def test_autosize_h_rt_sizes_on_the_resolved_bstar():
    """Catch #2: the walltime autosizer read a NONEXISTENT campaign.agent key then a stale
    hardcoded 200k — at B*=400k every pack-5 array task (~6:09 needed) would have been sized
    ~4h and walltime-killed. Lock the formula to the resolved top-level B*."""
    from src.utils.config import cfg_get, load_config

    bstar = int(cfg_get(load_config("campaign"), "train_steps_per_candidate", 0))
    # the campaign agent block must NOT grow a shadowing copy (the key the old code read)
    assert "train_steps_per_candidate" not in (cfg_get(load_config("campaign"), "agent", {}) or {})
    got = rcc.autosize_h_rt(5, bstar)
    hours = int(got.split(":")[0])
    # pack-5 at 400k on the worst-case curve needs ~6.2h -> 7; a 200k-sized 4h is the dead zone
    need_secs = (bstar * 5 / (0.5 * 253.0) + 1200.0) * 1.3
    assert hours * 3600 >= need_secs
    assert got == f"{int(need_secs // 3600) + 1}:0:0"


def test_baselines_guard_rejects_unknown_name_in_dry_run():
    """row 30l: the R97 fail-before-ssh guard must fire IN THE DRY-RUN PATH (it already regressed
    once by sitting below the dry-run exit — this locks the placement)."""
    import pytest

    with pytest.raises(SystemExit, match="unknown REWARD_CANON key"):
        rcc.main(["--dry-run", "--synthetic", "--arms", "distributional",
                  "--baselines", "not_a_real_reward"])


def test_canary_guard_rejects_unknown_name_in_dry_run():
    """row 30l: --canary names route through the same validation (they previously bypassed it
    and would have failed only after ssh/submit)."""
    import pytest

    with pytest.raises(SystemExit, match="unknown REWARD_CANON key"):
        rcc.main(["--dry-run", "--synthetic", "--tiered", "--arms", "distributional",
                  "--canary", "raw_retrun"])


def test_baselines_guard_accepts_full_canon_in_dry_run():
    """row 30l: every REWARD_CANON name (the ten-name §9 panel) passes the guard."""
    from src.baselines.rewards import REWARD_CANON

    rc = rcc.main(["--dry-run", "--synthetic", "--arms", "distributional",
                   "--baselines", *sorted(REWARD_CANON)])
    assert rc in (0, None)
