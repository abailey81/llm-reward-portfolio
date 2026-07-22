"""Cluster campaign orchestrator tests — the FULL generation loop + per-arm pipeline + concurrent
multi-arm driver against a FAKE cluster and the keyless STUB author. No network, no GPU, no LLM.

The fake ``run_batch`` faithfully simulates the on-node ``run_one``: for each search spec it writes
a record (synthetic fitness) carrying the EXACT authored prompt (so provenance parity is testable);
for each test spec it writes a sealed-leg record. This lets us assert the science-bearing behaviour
(authoring count, generation-best selection, reflection-block carry, resume replay, the F5 failure
ledger) without training anything.
"""
from __future__ import annotations

import threading
from pathlib import Path

import pytest

from src.cluster.campaign import (
    ClusterRun,
    run_arm_pipeline,
    run_baselines_on_cluster,
    run_campaign_on_cluster,
    run_campaign_tiered,
    run_family_search_arm,
    run_search_arm,
    run_test_leg,
    spend_guard,
)
from src.io.results import write_run
from src.llm.loop import _REFLECTION_PREAMBLE


def _opts(*, seed=0, generations=2, candidates=4, diversity=False):
    from src.utils.config import load_config

    return {
        "pass_mode": "A", "provider": "stub", "seed": seed,
        "generations": generations, "candidates": candidates,
        "env_cfg": load_config("environment"), "n_assets": 31, "model": "stub",
        "train_steps": 100, "batch_size": 64, "normalize_obs": True,
        "n_trials": 1, "synthetic": True, "data": {}, "cvar_alpha": 0.05, "window": 20,
        "diversity_prompt_variation": diversity,
    }


def _index_fitness(cid):
    """Deterministic synthetic fitness: a search candidate ``…-c{ci}`` (or its k-seed member
    ``…-c{ci}-s{j}``) scores ``ci`` (so the highest candidate index is the generation best, and all
    k seeds of a candidate share its score → IQM == ci); a test record ``…-s{seed}`` scores 0.5."""
    import re

    m = re.search(r"-c(\d+)(?:-s\d+)?$", cid)
    return float(m.group(1)) if m else 0.5


class FakeCluster:
    """A fake run_batch that simulates run_one: writes a record per spec (unless its id is in
    ``fail``), threading the authored prompt into the search record for provenance-parity checks."""

    def __init__(self, root, *, fail=frozenset(), fitness=None):
        self.root = root
        self.fail = set(fail)
        self.fitness = fitness or _index_fitness
        self.calls = []  # (name, pool, pack, [ids])
        self._lock = threading.Lock()

    def run_batch(self, specs, name, *, pool="EF", pack=1, priority=0):
        ids = [s.get("candidate_id") or s.get("run_id") for s in specs]
        with self._lock:
            self.calls.append((name, pool, pack, ids, priority))
        for s in specs:
            cid = s.get("candidate_id") or s.get("run_id")
            if cid in self.fail:
                continue  # simulate a failed training -> no record (sandbox reject / exhausted)
            # honour the spec's archive_root (the search/test sub-root the on-node run_one writes to)
            arm_dir = str(Path(s["archive_root"]) / s["arm"])
            if s.get("leg") == "test":
                write_run({
                    "run_id": cid, "arm": s["arm"], "seed": int(s.get("seed", 0)), "fold": 0,
                    "candidate_id": cid, "generation": 0, "reward_source_hash": "h",
                    "feedback_block": "", "wall_clock": 0.0, "env_fingerprint": "x", "frozen": True,
                    "metrics": {"val_fitness": 0.0, "test_sharpe": self.fitness(cid),
                                "test_returns": [0.01, -0.02, 0.0]},
                }, arm_dir)
            else:
                write_run({
                    "run_id": cid, "arm": s["arm"], "seed": int(s.get("seed", 0)), "fold": 0,
                    "candidate_id": cid, "generation": int(s.get("generation", 0)),
                    "reward_source": str(s.get("reward", "")), "reward_source_hash": "h",
                    "prompt": s.get("prompt", ""), "feedback_block": "", "wall_clock": 0.0,
                    "env_fingerprint": "x",
                    "metrics": {"val_fitness": self.fitness(cid),
                                "tail_stats": {"cvar_05": -0.05, "cvar_10": -0.04,
                                               "cvar_25": -0.03, "cvar_01": -0.07,
                                               "left_tail_mass": 0.05, "robust_skew": 0.2},
                                "val_returns": [0.01, -0.01, 0.02],
                                # the on-node worker emits TRAIN returns for k>1 specs (B-A2 fed tail)
                                **({"train_returns": [0.005, -0.015, 0.01, 0.02]}
                                   if s.get("emit_train_returns") else {})},
                }, arm_dir)
        return {"ok": True, "completed": len(specs) - len(self.fail & set(ids))}


def _run(root, fake, **kw):
    return ClusterRun(run_batch=fake.run_batch, spec_archive_root=str(root), read_root=root, **kw)


# --------------------------------------------------------------------------- #
# SEARCH — authoring, selection, reflection, summary                            #
# --------------------------------------------------------------------------- #
def test_search_arm_authors_selects_reflects_and_summarises(tmp_path):
    fake = FakeCluster(tmp_path)
    summary = run_search_arm("distributional", _opts(generations=2, candidates=4), _run(tmp_path, fake))

    # 2 gens × 2 cand/gen = 4 candidates authored + trained, all accepted
    assert summary["n_candidates"] == 4 and summary["n_failed"] == 0
    assert summary["matched_budget_ok"] is True
    # the two generations were submitted as SEPARATE arrays (per-gen batching), each of 2 specs
    names = [c[0] for c in fake.calls]
    assert names == ["distributional_g0", "distributional_g1"]
    assert all(len(c[3]) == 2 for c in fake.calls)
    # winner fitness = the global max (candidate index 1 in each gen -> fitness 1.0)
    assert summary["winner_fitness"] == 1.0

    # REFLECTION carried forward: gen-0 records used the initial prompt; gen-1 used the reflection
    # preamble (proof the generation-best block fed the next generation).
    from src.io.results import load_run

    search_arm = str(tmp_path / "search" / "distributional")
    g0 = load_run("distributional-g0-c0", search_arm)
    g1 = load_run("distributional-g1-c0", search_arm)
    assert _REFLECTION_PREAMBLE not in g0["prompt"]
    assert _REFLECTION_PREAMBLE in g1["prompt"]


def test_search_arm_resume_replays_without_reauthoring(tmp_path):
    fake = FakeCluster(tmp_path)
    opts = _opts(generations=2, candidates=4)
    run_search_arm("scalar", opts, _run(tmp_path, fake))
    calls_first = len(fake.calls)

    # resume: everything is archived -> NO new training arrays submitted, same summary
    fake.calls.clear()
    summary = run_search_arm("scalar", opts, _run(tmp_path, fake), resume=True)
    assert fake.calls == []  # nothing re-trained
    assert summary["n_candidates"] == 4 and summary["matched_budget_ok"] is True
    assert calls_first == 2


def test_search_arm_ledgers_failures_and_skips_them_on_resume(tmp_path):
    # candidate g0-c1 fails its training -> no record
    fake = FakeCluster(tmp_path, fail={"scalar-g0-c1"})
    opts = _opts(generations=1, candidates=2)
    summary = run_search_arm("scalar", opts, _run(tmp_path, fake))
    assert summary["n_candidates"] == 1 and summary["n_failed"] == 1
    ledger = tmp_path / "search" / "scalar" / "failures.jsonl"
    assert ledger.is_file()
    import json

    rows = [json.loads(x) for x in ledger.read_text().splitlines() if x.strip()]
    assert rows and rows[0]["candidate_id"] == "scalar-g0-c1"

    # P3 (2026-07-13 audit): resume RESUBMITS the ledgered candidate from the ledger row's STORED
    # source — never re-authored (the paid call is preserved), candidate identity kept. Here the
    # fake still fails it (deterministic failure), so it re-ledgers and the summary is unchanged;
    # exactly ONE training batch is submitted, containing only the resubmitted candidate.
    fake.calls.clear()
    s2 = run_search_arm("scalar", opts, _run(tmp_path, fake), resume=True)
    assert [c[3] for c in fake.calls] == [["scalar-g0-c1"]]  # resubmitted, alone, no survivor churn
    assert s2["n_candidates"] == 1 and s2["n_failed"] == 1

    # An INFRA-style failure (the fake now lets it train) recovers on the NEXT resume — the
    # stranded authoring spend is realized instead of abandoned.
    fake.fail.clear()
    fake.calls.clear()
    s3 = run_search_arm("scalar", opts, _run(tmp_path, fake), resume=True)
    assert s3["n_candidates"] == 2 and s3["n_failed"] == 0


def test_search_arm_k3_fans_out_3_seeds_per_candidate_and_selects_on_iqm(tmp_path):
    """B-A2: with search_seeds_per_candidate=3, each candidate trains at 3 consecutive seeds
    ({cid}-s0/s1/s2) in ONE generation array, and is selected on the IQM aggregate."""
    fake = FakeCluster(tmp_path)
    opts = _opts(generations=1, candidates=2)
    opts["search_seeds_per_candidate"] = 3
    summary = run_search_arm("distributional", opts, _run(tmp_path, fake))
    # 2 candidates x 3 seeds = 6 specs in the single generation array
    assert len(fake.calls) == 1 and len(fake.calls[0][3]) == 6
    assert sorted(fake.calls[0][3]) == [
        f"distributional-g0-c{c}-s{s}" for c in (0, 1) for s in (0, 1, 2)]
    # both candidates valid (all 3 seeds ok) -> selected on the IQM aggregate (c1 > c0)
    assert summary["n_candidates"] == 2 and summary["n_failed"] == 0
    assert summary["winner_fitness"] == 1.0  # IQM of candidate c1's seeds (all score 1)
    # a candidate with a FAILED seed is all-or-nothing failed
    fake2 = FakeCluster(tmp_path / "b", fail={"distributional-g0-c0-s1"})
    o2 = _opts(generations=1, candidates=2)
    o2["search_seeds_per_candidate"] = 3
    s2 = run_search_arm("distributional", o2, _run(tmp_path / "b", fake2))
    assert s2["n_candidates"] == 1 and s2["n_failed"] == 1


def test_search_arm_pins_the_confirmatory_pool(tmp_path):
    fake = FakeCluster(tmp_path)
    run_search_arm("distributional", _opts(generations=2, candidates=2),
                   _run(tmp_path, fake, pool_confirmatory="EF"))
    assert {c[1] for c in fake.calls} == {"EF"}  # device homogeneity within the contrast


# --------------------------------------------------------------------------- #
# FAMILY search (H4: random_search + bayes_opt) — NOT LLM-authored              #
# --------------------------------------------------------------------------- #
def test_random_search_is_one_array_of_sampled_sources(tmp_path):
    fake = FakeCluster(tmp_path)
    summary = run_family_search_arm("random_search", _opts(candidates=4), _run(tmp_path, fake))
    # sampled UP FRONT, trained as ONE array (no reflection, no gen loop)
    assert len(fake.calls) == 1 and fake.calls[0][0] == "random_search_search"
    assert len(fake.calls[0][3]) == 4 and summary["n_candidates"] == 4
    # NO LLM authoring happened (no llm_calls.jsonl under the search sub-root)
    assert not (tmp_path / "search" / "random_search" / "llm_calls.jsonl").exists()


def test_bayes_opt_is_sequential_one_eval_per_array(tmp_path):
    fake = FakeCluster(tmp_path)
    summary = run_family_search_arm("bayes_opt", _opts(candidates=3), _run(tmp_path, fake))
    # the driver GP trains each proposed coefficient vector as an array-of-1 (sequential)
    assert len(fake.calls) == 3 and all(len(c[3]) == 1 for c in fake.calls)
    assert summary["n_candidates"] == 3


def test_family_random_search_k3_fans_out_seeds(tmp_path):
    """B-A2: k=3 applies to the H4 family arms too (so LLM-vs-family is not confounded by k)."""
    fake = FakeCluster(tmp_path)
    opts = _opts(candidates=2)
    opts["search_seeds_per_candidate"] = 3
    summary = run_family_search_arm("random_search", opts, _run(tmp_path, fake))
    assert len(fake.calls) == 1 and len(fake.calls[0][3]) == 6  # 2 sources x 3 seeds
    assert sorted(fake.calls[0][3]) == [f"random_search-c{c}-s{s}" for c in (0, 1) for s in (0, 1, 2)]
    assert summary["n_candidates"] == 2


def test_pipeline_dispatches_family_arm_to_family_search(tmp_path):
    fake = FakeCluster(tmp_path)
    run = _run(tmp_path, fake)
    _inject_select_freeze(run)
    result = run_arm_pipeline("random_search", _opts(candidates=2), [0], run,
                              test_leg_kwargs=_test_leg_kwargs(), frozen_root=tmp_path / "frozen")
    assert result["ok"]
    names = [c[0] for c in fake.calls]
    assert "random_search_search" in names  # the FAMILY array, not a *_g0 LLM array
    assert not any(n.endswith("_g0") for n in names)


# --------------------------------------------------------------------------- #
# TEST leg — one array, resume-skips                                            #
# --------------------------------------------------------------------------- #
def _test_leg_kwargs():
    return dict(
        panel_descriptor={"synthetic": True}, env_cfg={"state": {"lookback_days": 60}},
        agent_cfg={"train_steps": 100}, train_window=(0, 100), val_window=(100, 150),
        test_window=(150, 200), embargo=21, lookback=60,
    )


def test_run_test_leg_is_one_array_and_resume_skips_done(tmp_path):
    winner = {"arm": "distributional", "reward_source": "def reward(*a): return 0.0",
              "reward_source_hash": ""}
    fake = FakeCluster(tmp_path)
    run_test_leg([("distributional", winner)], [0, 1, 2], _run(tmp_path, fake),
                 name="distributional_test", **_test_leg_kwargs())
    # ONE array carrying all 3 seeds
    assert len(fake.calls) == 1 and fake.calls[0][0] == "distributional_test"
    assert sorted(fake.calls[0][3]) == ["distributional-s0", "distributional-s1", "distributional-s2"]

    # resume: all archived -> nothing submitted
    fake.calls.clear()
    s2 = run_test_leg([("distributional", winner)], [0, 1, 2], _run(tmp_path, fake),
                      name="distributional_test", **_test_leg_kwargs())
    assert fake.calls == [] and s2.get("submitted") == 0


# --------------------------------------------------------------------------- #
# PIPELINE + concurrent driver                                                  #
# --------------------------------------------------------------------------- #
def _inject_select_freeze(run):
    """Real-shaped select (max val_fitness) + a no-op freeze, injected so the pipeline is
    hermetic (no scripts/run_campaign import)."""
    from src.io.results import load_all

    def select(arm_root):
        recs = load_all(arm_root)
        if not recs:
            return None
        w = max(recs, key=lambda r: r.get("metrics", {}).get("val_fitness", float("-inf")))
        w.setdefault("reward_source", "def reward(*a): return 0.0")
        return w

    frozen = []

    def freeze(arm, winner, *, search_seed, frozen_root, env_fingerprint):
        frozen.append(arm)

    run.select_winner = select
    run.freeze_winner = freeze
    return frozen


def test_run_arm_pipeline_search_select_freeze_test(tmp_path):
    fake = FakeCluster(tmp_path)
    run = _run(tmp_path, fake)
    frozen = _inject_select_freeze(run)
    result = run_arm_pipeline(
        "distributional", _opts(generations=2, candidates=2), [0, 1], run,
        test_leg_kwargs=_test_leg_kwargs(), frozen_root=tmp_path / "frozen",
    )
    assert result["ok"] and frozen == ["distributional"]
    # search arrays (2) THEN one test array
    names = [c[0] for c in fake.calls]
    assert names[:2] == ["distributional_g0", "distributional_g1"]
    assert names[-1] == "distributional_test"
    # RESUME-BUG REGRESSION: search + test records are in DISJOINT sub-roots, so select_winner
    # (max val_fitness) can NEVER pick a test record on resume (a test record carries the winner's
    # val_fitness — same-dir would let it win/tie). The search sub-root holds ONLY search candidates.
    from src.io.results import load_all

    search_ids = {r["run_id"] for r in load_all(str(tmp_path / "search" / "distributional"))}
    test_ids = {r["run_id"] for r in load_all(str(tmp_path / "test" / "distributional"))}
    assert search_ids and test_ids and search_ids.isdisjoint(test_ids)
    assert all("-c" in i for i in search_ids) and all("-s" in i for i in test_ids)


def test_run_campaign_concurrent_arms_serialise_authoring_and_isolate_crashes(tmp_path):
    class TrackingLock:
        def __init__(self):
            self._l = threading.Lock()
            self.entries = 0
            self.active = 0
            self.max_active = 0

        def __enter__(self):
            self._l.acquire()
            self.entries += 1
            self.active += 1
            self.max_active = max(self.max_active, self.active)
            return self

        def __exit__(self, *a):
            self.active -= 1
            self._l.release()

    lock = TrackingLock()
    fake = FakeCluster(tmp_path)
    run = _run(tmp_path, fake, author_lock=lock)
    _inject_select_freeze(run)

    arms = ["distributional", "scalar", "scalar_cvar5"]
    results = run_campaign_on_cluster(
        arms, lambda arm: _opts(generations=2, candidates=4), [0, 1], run,
        test_leg_kwargs=_test_leg_kwargs(), frozen_root=tmp_path / "frozen",
    )
    assert set(results) == set(arms)
    assert all(results[a]["ok"] for a in arms)
    # authoring serialised across arm threads: 3 arms × 2 gens × 2 cand/gen = 12 authorings,
    # and NEVER concurrent (the shared lock enforces arm-serial API — max_active stays 1).
    assert lock.entries == 12 and lock.max_active == 1


def test_run_baselines_is_one_array_of_names_by_seeds(tmp_path):
    """H1 baselines (fixed rewards, no search) run as ONE test array — names × seeds."""
    fake = FakeCluster(tmp_path)
    run_baselines_on_cluster(["differential_sharpe", "return_minus_cvar"], [0, 1],
                             _run(tmp_path, fake), test_leg_kwargs=_test_leg_kwargs())
    assert len(fake.calls) == 1
    assert sorted(fake.calls[0][3]) == [
        "baseline_differential_sharpe-s0", "baseline_differential_sharpe-s1",
        "baseline_return_minus_cvar-s0", "baseline_return_minus_cvar-s1",
    ]


def test_campaign_floods_baselines_concurrently_with_arms(tmp_path):
    """The H1 baselines run alongside the arm pipelines (no search dependency) and archive under
    their own test/baseline_<name>/ roots, disjoint from the arms."""
    from src.io.results import load_all

    fake = FakeCluster(tmp_path)
    run = _run(tmp_path, fake)
    _inject_select_freeze(run)
    results = run_campaign_on_cluster(
        ["distributional"], lambda a: _opts(generations=1, candidates=2), [0], run,
        test_leg_kwargs=_test_leg_kwargs(), frozen_root=tmp_path / "frozen",
        baseline_names=["differential_sharpe"],
    )
    assert results["distributional"]["ok"] and results["__baselines__"]["ok"]
    base_ids = {r["run_id"] for r in load_all(str(tmp_path / "test" / "baseline_differential_sharpe"))}
    assert base_ids == {"baseline_differential_sharpe-s0"}


def test_run_campaign_tiered_c_ladder_canary_priorities_pair_and_sweep(tmp_path):
    """The C-ladder (PLAN §13.1): C0 canary at -p 0 → C1-C3 (H2 at -p 0, others -100; the H2 pair
    core-test is ONE pair-adjacent interleaved array) → C4 round-robin sweep blocks; tiers
    PARTITION the seeds so every block boundary is a complete design at that n."""
    from src.io.results import load_all

    fake = FakeCluster(tmp_path)
    run = _run(tmp_path, fake)
    _inject_select_freeze(run)
    out = run_campaign_tiered(
        ["distributional", "scalar", "random_search"], lambda a: _opts(generations=1, candidates=2),
        {"mode": "tiered", "tiers": [2, 4]}, run,
        test_leg_kwargs=_test_leg_kwargs(), frozen_root=tmp_path / "frozen",
        h2_arms=("distributional", "scalar"),
        baseline_names=["differential_sharpe"], canary_baselines=["differential_sharpe"],
        review_gate=False,
    )
    assert out["n_tiers"] == 2 and out["tier_sizes"] == [2, 2] and out["ok"]
    by_name = {c[0]: c for c in fake.calls}
    # C0 (MODE-D 2026-07-21c): the canary runs CONCURRENTLY with the no-spend arms (its batch is
    # present at -p 0 but no longer necessarily FIRST); only LLM authoring waits on its verdict.
    assert by_name["canary"][4] == 0
    # priorities: H2 search arrays at 0; the non-H2 family arm at -100
    assert by_name["distributional_g0"][4] == 0 and by_name["scalar_g0"][4] == 0
    assert by_name["random_search_search"][4] == -100
    # dedup contract: baselines covered by the canary are NOT re-submitted as a second batch
    # (concurrent double-submission of the same run_ids = the P4 write-race class).
    assert "baselines" not in by_name
    # C2: the H2 pair core-test = ONE interleaved array at -p 0 (dist-s0, scalar-s0, dist-s1, ...)
    pair = by_name["h2_pair_test"]
    assert pair[4] == 0
    assert pair[3] == ["distributional-s0", "scalar-s0", "distributional-s1", "scalar-s1"]
    # the non-H2 arm's core test flooded per-arm (zero barrier) at -100
    assert by_name["random_search_test"][4] == -100
    # C4: ONE round-robin sweep block over ALL units (3 arms + 1 baseline) x seeds 2-3, seed-major
    sweep = by_name["sweep_t1"]
    # row 30n/C6: sweep block 1 = the tier-100 rung at PRIORITY_STAGE1 (-100), NEVER 0 — the
    # sequential path now mirrors the pipelined ladder (rungs sit in the registered queue,
    # below core-0 and above nothing they may starve; the old 0 inverted the queue vs the legs).
    assert sweep[4] == -100 and len(sweep[3]) == 8
    assert sweep[3][:4] == ["distributional-s2", "scalar-s2", "random_search-s2",
                            "baseline_differential_sharpe-s2"]
    # partition: H2 test seeds 0-3 all present, no overlap/gap
    ids = {r["run_id"] for r in load_all(str(tmp_path / "test" / "distributional"))}
    assert ids == {f"distributional-s{k}" for k in range(4)}


def test_run_campaign_tiered_gate_holds_then_approval_resumes(tmp_path):
    """The review gate under an EXPLICIT manual hold (``hold_at_gate=True``): the ladder STOPS after
    the C3 floor with the EFFECT-BLIND integrity report written even though execution health is
    green; creating the approval file + re-running with resume proceeds into C4 without re-training
    anything. (The default — auto-proceed on green — is the companion test below.)"""
    fake = FakeCluster(tmp_path)
    run = _run(tmp_path, fake)
    _inject_select_freeze(run)
    kw = dict(
        test_leg_kwargs=_test_leg_kwargs(), frozen_root=tmp_path / "frozen",
        h2_arms=("distributional",), baseline_names=None, canary_baselines=None,
    )
    out1 = run_campaign_tiered(
        ["distributional"], lambda a: _opts(generations=1, candidates=2),
        {"mode": "tiered", "tiers": [2, 4]}, run, review_gate=True, hold_at_gate=True, **kw)
    assert out1.get("awaiting_review") is True and "sweep_t1" not in out1["results"]
    assert out1.get("gate") == "manual-hold" and out1.get("gate_health_ok") is True
    report = Path(out1["integrity_report"])
    assert report.is_file()
    text = report.read_text(encoding="utf-8")
    assert "EFFECT-BLIND" in text and "test_sharpe" not in text  # counts only, no effects
    n_calls_before = len(fake.calls)

    # Tamer approves -> re-run with resume: C0-C3 replay from the archive, C4 submits the sweep
    Path(out1["approve_by_creating"]).write_text("approved\n", encoding="utf-8")
    out2 = run_campaign_tiered(
        ["distributional"], lambda a: _opts(generations=1, candidates=2),
        {"mode": "tiered", "tiers": [2, 4]}, run, review_gate=True, hold_at_gate=True,
        resume=True, **kw)
    assert out2["ok"] and "sweep_t1" in out2["results"]
    new_names = [c[0] for c in fake.calls[n_calls_before:]]
    assert new_names == ["sweep_t1"]  # nothing re-trained except the sweep block


def test_run_campaign_tiered_gate_autoproceeds_on_green_health(tmp_path):
    """The DEFAULT gate (no manual hold): green execution health AUTO-PROCEEDS into C4 in one shot —
    no manual approval latency (Tamer's time-security requirement). The gate reads only counts +
    homogeneity censuses, so releasing on green never conditions continuation on an effect. The
    effect-blind report is still written, and the sealed-safe selection section names the winner's
    authored reward CODE without any performance statistic."""
    fake = FakeCluster(tmp_path)
    run = _run(tmp_path, fake)
    _inject_select_freeze(run)
    out = run_campaign_tiered(
        ["distributional"], lambda a: _opts(generations=1, candidates=2),
        {"mode": "tiered", "tiers": [2, 4]}, run, review_gate=True,  # hold_at_gate defaults False
        test_leg_kwargs=_test_leg_kwargs(), frozen_root=tmp_path / "frozen",
        h2_arms=("distributional",), baseline_names=None, canary_baselines=None)
    assert out.get("awaiting_review") is not True  # did NOT stop
    assert out["ok"] and "sweep_t1" in out["results"]
    assert out.get("gate_health_ok") is True
    text = Path(out["integrity_report"]).read_text(encoding="utf-8")
    assert "EFFECT-BLIND" in text and "test_sharpe" not in text
    assert "Selection" in text  # the sealed-safe winner-code section is present


def test_canary_failure_aborts_before_any_authoring(tmp_path):
    """C0: a failing canary raises LOUD before any Opus spend (the whole point of the canary)."""
    fake = FakeCluster(tmp_path, fail={"baseline_differential_sharpe-s0"})

    # make the fake report not-ok for the canary batch
    orig = fake.run_batch

    def rb(specs, name, **kw):
        res = orig(specs, name, **kw)
        return {**res, "ok": name != "canary"}

    run = ClusterRun(run_batch=rb, spec_archive_root=str(tmp_path), read_root=tmp_path)
    _inject_select_freeze(run)
    with pytest.raises(RuntimeError, match="CANARY FAILED"):
        run_campaign_tiered(
            ["distributional"], lambda a: _opts(generations=1, candidates=2),
            {"mode": "tiered", "tiers": [2, 4]}, run,
            test_leg_kwargs=_test_leg_kwargs(), frozen_root=tmp_path / "frozen",
            canary_baselines=["differential_sharpe"], review_gate=False,
        )


def test_run_campaign_captures_a_single_arm_crash(tmp_path):
    fake = FakeCluster(tmp_path)
    run = _run(tmp_path, fake)

    def select(arm_root):
        raise RuntimeError("boom in select")

    run.select_winner = select
    run.freeze_winner = lambda *a, **k: None
    results = run_campaign_on_cluster(
        ["distributional"], lambda arm: _opts(generations=1, candidates=2), [0], run,
        test_leg_kwargs=_test_leg_kwargs(), frozen_root=tmp_path / "frozen",
    )
    assert results["distributional"]["ok"] is False
    assert "boom in select" in results["distributional"]["error"]


def test_spend_guard_raises_at_cap():
    guard = spend_guard(max_calls=3)
    guard()
    guard()
    guard()  # 3 == cap, still ok
    with pytest.raises(RuntimeError, match="spend cap"):
        guard()  # the 4th exceeds


def test_spend_guard_wired_into_search_stops_a_runaway(tmp_path):
    fake = FakeCluster(tmp_path)
    run = _run(tmp_path, fake, author_guard=spend_guard(max_calls=2))
    # 1 gen × 4 candidates would author 4 -> the 3rd trips the cap
    with pytest.raises(RuntimeError, match="spend cap"):
        run_search_arm("scalar", _opts(generations=1, candidates=4), run)


# --------------------------------------------------------------------------- #
# Production wiring factory                                                     #
# --------------------------------------------------------------------------- #
def test_build_cluster_run_binds_driver_and_throttles_the_shared_pull(tmp_path, monkeypatch):
    from src.cluster import campaign as C

    rb_calls = []
    monkeypatch.setattr("src.cluster.driver.run_batch",
                        lambda specs, name, **kw: rb_calls.append((name, kw)) or {"ok": True})
    monkeypatch.setattr("src.cluster.submit.ssh_runner", lambda host: (lambda cmd: ""))
    pulls = {"n": 0}
    monkeypatch.setattr("src.cluster.poll.pull_archive",
                        lambda *a, **k: pulls.__setitem__("n", pulls["n"] + 1) or 1)

    # min_pull_interval huge -> the shared puller pulls ONCE then reuses (no ssh storm across arms)
    run = C.build_cluster_run(
        remote_root="/r", remote_outputs_root="/r/outputs", local_batch_root=tmp_path / "b",
        local_archive_root=tmp_path / "a", gold_dir="/inputs", pool_confirmatory="EF",
        min_pull_interval=1e9, max_author_calls=5,
    )
    assert run.spec_archive_root == "/r/outputs" and run.pool_confirmatory == "EF"
    assert isinstance(run.read_root, type(tmp_path))

    # run_batch binds driver.run_batch with the infra + the chosen pool
    run.run_batch([{"candidate_id": "c0", "arm": "x"}], "x_g0", pool="EF", pack=2)
    assert rb_calls and rb_calls[0][0] == "x_g0"
    shared = rb_calls[0][1]["pull"]
    assert shared() == 1 and shared() == 1  # 2nd call throttled -> pull_archive hit ONCE
    assert pulls["n"] == 1
    # the spend cap is live
    assert callable(run.author_guard)


def test_build_cluster_run_threads_apptainer_and_cores_per_training(tmp_path, monkeypatch):
    """LIVE-rehearsal fixes (2026-07-10/11): the container image AND a right-sized core footprint must
    reach the jobscript. cores = cores_per_training × the call's pack (Myriad GPU-node CORES are the
    binding scheduling constraint); apptainer_sif is mandatory (the cluster venv is container-built).
    Both are OFF by default so the jobscript keeps its own defaults (4×pack, native venv)."""
    from src.cluster import campaign as C

    rb_calls: list[dict] = []
    monkeypatch.setattr("src.cluster.driver.run_batch",
                        lambda specs, name, **kw: rb_calls.append(kw) or {"ok": True})
    monkeypatch.setattr("src.cluster.submit.ssh_runner", lambda host: (lambda cmd: ""))
    monkeypatch.setattr("src.cluster.poll.pull_archive", lambda *a, **k: 1)

    run = C.build_cluster_run(
        remote_root="/r", remote_outputs_root="/r/outputs", local_batch_root=tmp_path / "b",
        local_archive_root=tmp_path / "a", gold_dir="/inputs",
        apptainer_sif="~/python311.sif", cores_per_training=2,
    )
    run.run_batch([{"candidate_id": "c0", "arm": "x"}], "x_g0", pool="EF", pack=5)
    kw = rb_calls[0]
    assert kw["apptainer_sif"] == "~/python311.sif"
    assert kw["cores"] == 10  # 2 cores/training × pack 5 -> jobscript renders -pe smp 10

    rb_calls.clear()
    run2 = C.build_cluster_run(
        remote_root="/r", remote_outputs_root="/r/outputs", local_batch_root=tmp_path / "b2",
        local_archive_root=tmp_path / "a2", gold_dir="/inputs",
    )
    run2.run_batch([{"candidate_id": "c0", "arm": "x"}], "x_g0", pool="EF", pack=5)
    assert "cores" not in rb_calls[0] and "apptainer_sif" not in rb_calls[0]
    assert "h_rt" not in rb_calls[0]  # default: the renderer's conservative walltime stands

    rb_calls.clear()
    run3 = C.build_cluster_run(
        remote_root="/r", remote_outputs_root="/r/outputs", local_batch_root=tmp_path / "b3",
        local_archive_root=tmp_path / "a3", gold_dir="/inputs", h_rt="0:50:0",
    )
    run3.run_batch([{"candidate_id": "c0", "arm": "x"}], "x_g0", pool="EF", pack=1)
    # max-throughput 2026-07-11: a MEASURED, tight walltime threads through to the jobscript so
    # campaign tasks are backfill-eligible (the renderer's 3h default is a ~5.5x over-request at B*).
    assert rb_calls[0]["h_rt"] == "0:50:0"


def test_batch_tag_namespaces_every_batch(tmp_path, monkeypatch):
    """2026-07-11d regression: the driver's double-submit guard matches queued jobs by NAME across
    the user's whole queue, so two concurrent runs sharing arm names collide (the prototype adopted
    the rehearsal's queued `distributional_g0` and polled an archive that job never writes to).
    A per-run batch_tag must prefix the batch name at the run_batch choke point."""
    import src.cluster.campaign as C

    names: list[str] = []
    monkeypatch.setattr("src.cluster.driver.run_batch",
                        lambda specs, name, **kw: names.append(name) or {"ok": True})
    monkeypatch.setattr("src.cluster.submit.ssh_runner", lambda host: (lambda cmd: ""))
    monkeypatch.setattr("src.cluster.poll.pull_archive", lambda *a, **k: 1)
    run = C.build_cluster_run(
        remote_root="/r", remote_outputs_root="/r/outputs", local_batch_root=tmp_path / "b",
        local_archive_root=tmp_path / "a", gold_dir="/inputs", batch_tag="pm",
    )
    run.run_batch([{"candidate_id": "c0", "arm": "x"}], "distributional_g0", pool="EF", pack=1)
    assert names == ["pm_distributional_g0"]


def test_seed_pool_blocks_partition_and_parser(tmp_path):
    """Device-stratified seed blocks (2026-07-11c): the test leg partitions its taskfile BY SEED
    into per-pool arrays — every CRN pair (same seed, all arms) stays on ONE device class, the
    device cancels in the paired difference, and unassigned seeds fall back to the base pool."""
    import src.cluster.campaign as C

    # parser: blocks, disjointness fail-loud, bad-shape fail-loud
    blocks = C.parse_seed_pool_blocks("EF:0-1,L:2-3")
    assert blocks == [("EF", {0, 1}), ("L", {2, 3})]
    with pytest.raises(ValueError, match="overlap"):
        C.parse_seed_pool_blocks("EF:0-2,L:2-3")
    with pytest.raises(ValueError, match="POOL:LO-HI"):
        C.parse_seed_pool_blocks("EF")

    calls: list[tuple[str, str, list[int]]] = []

    def fake_run_batch(specs, name, *, pool, pack, priority=0):
        calls.append((name, pool, sorted(int(s["seed"]) for s in specs)))
        return {"ok": True, "submitted": len(specs)}

    run = C.ClusterRun(run_batch=fake_run_batch, spec_archive_root="/r/outputs",
                       read_root=tmp_path, seed_pool_blocks=blocks)
    winners = [("distributional", {"arm": "distributional", "reward_source": "def reward(*a): ...",
                                   "candidate_id": "w0", "val_fitness": 1.0})]
    out = C.run_test_leg(
        winners, [0, 1, 2, 3, 4], run, panel_descriptor={"synthetic": True}, env_cfg={},
        agent_cfg={"train_steps_per_candidate": 10}, train_window=(0, 5), val_window=(6, 8),
        test_window=(9, 12), embargo=0, lookback=1, name="t", resume=False,
    )
    assert out["ok"] and set(out["blocks"]) == {"EF", "L"}
    by_name = {n: (p, seeds) for n, p, seeds in calls}
    assert by_name["t_EF"] == ("EF", [0, 1])   # block 1 on the V100 pool
    assert by_name["t_L"] == ("L", [2, 3])     # block 2 on the A100 pool
    assert by_name["t"][1] == [4]              # unassigned seed falls back to base pool — never dropped


def test_seed_pool_blocks_drive_concurrently_not_serially(tmp_path):
    """P16 (2026-07-13 audit): the per-pool block drivers must OVERLAP — the old serial loop
    idled the second pool for the whole first block. A 2-party barrier inside the fake
    run_batch deadlocks (and fails loud) unless both blocks are in flight simultaneously."""
    import threading

    import src.cluster.campaign as C

    blocks = C.parse_seed_pool_blocks("EF:0-0,L:1-1")
    both_in_flight = threading.Barrier(2, timeout=20)

    def fake_run_batch(specs, name, *, pool, pack, priority=0):
        both_in_flight.wait()  # raises BrokenBarrierError if the blocks were serialized
        return {"ok": True, "submitted": len(specs)}

    run = C.ClusterRun(run_batch=fake_run_batch, spec_archive_root="/r/outputs",
                       read_root=tmp_path, seed_pool_blocks=blocks)
    winners = [("distributional", {"arm": "distributional", "reward_source": "def reward(*a): ...",
                                   "candidate_id": "w0", "val_fitness": 1.0})]
    out = C.run_test_leg(
        winners, [0, 1], run, panel_descriptor={"synthetic": True}, env_cfg={},
        agent_cfg={"train_steps_per_candidate": 10}, train_window=(0, 5), val_window=(6, 8),
        test_window=(9, 12), embargo=0, lookback=1, name="t", resume=False,
    )
    assert out["ok"] and set(out["blocks"]) == {"EF", "L"}


def test_crn_pair_device_consistency_replaces_per_unit_homogeneity(tmp_path):
    """2026-07-12 gate fix (implements the device-stratified seed-block ratification, 2026-07-11c):
    under seed-pool blocks a unit legitimately SPANS devices, so per-unit homogeneity must not gate.
    The correct invariant is per-SEED CRN consistency (every unit at seed s on one device class);
    a genuine cross-unit device mismatch at one seed must still fail the gate."""
    import json as _json

    from src.cluster.integrity import _test_census, write_integrity_report

    def put(unit: str, seed: int, gpu: str | None) -> None:
        rid = f"{unit}-s{seed}"
        write_run({
            "run_id": rid, "arm": unit, "seed": seed, "fold": 0, "candidate_id": rid,
            "generation": 0, "reward_source_hash": "h", "feedback_block": "",
            "wall_clock": 0.0, "env_fingerprint": "x", "frozen": True,
            "metrics": {"val_fitness": 0.0},
        }, str(tmp_path / "test" / unit))
        if gpu:
            (tmp_path / "test" / unit / rid / "env.json").write_text(_json.dumps(
                {"nvidia_smi": {"gpus": [f"550.127.05, {gpu}"]}}), encoding="utf-8")

    # Device-blocked but CRN-consistent: seed 0 on V100 everywhere, seed 1 on A100 everywhere.
    for unit in ("distributional", "scalar"):
        put(unit, 0, "Tesla V100-PCIE-32GB")
        put(unit, 1, "NVIDIA A100-PCIE-40GB")

    class _Run:
        read_root = tmp_path
        def search_read(self):
            return tmp_path / "search"
        def test_read(self):
            return tmp_path / "test"

    census = _test_census(tmp_path / "test" / "distributional", "distributional", [0, 1])
    assert census["per_seed_device"] == {"0": "Tesla V100-PCIE-32GB", "1": "NVIDIA A100-PCIE-40GB"}
    assert census["device_homogeneous"]  # metrics.device is absent -> per-unit field unaffected

    report, _, _ = write_integrity_report(
        _Run(), arms=["distributional", "scalar"], h2_arms=["distributional"], baseline_names=[],
        core_seeds=[0, 1], opts_for=lambda a: {"candidates": 0, "search_seeds_per_candidate": 1},
        out_dir=tmp_path)
    v = report["verdict"]
    assert v["crn_pair_device_consistent"] and v["health_ok"]  # blocks pass under the new invariant

    # A REAL CRN violation: scalar's seed 1 record retrained on a V100 -> devices differ at seed 1.
    (tmp_path / "test" / "scalar" / "scalar-s1" / "env.json").write_text(
        _json.dumps({"nvidia_smi": {"gpus": ["550.127.05, Tesla V100-PCIE-32GB"]}}), encoding="utf-8")
    report2, _, _ = write_integrity_report(
        _Run(), arms=["distributional", "scalar"], h2_arms=["distributional"], baseline_names=[],
        core_seeds=[0, 1], opts_for=lambda a: {"candidates": 0, "search_seeds_per_candidate": 1},
        out_dir=tmp_path)
    v2 = report2["verdict"]
    assert not v2["crn_pair_device_consistent"] and not v2["health_ok"]
    assert "1" in v2["crn_device_violations"]


def test_h3_singleshot_disjoint_roots_namespaced_batches_and_gen1(tmp_path):
    """C5 (P4 closed 2026-07-13): the H3 single-shot control runs search(gens=1, no reflection)
    -> select -> freeze -> test on the cluster with STRUCTURALLY disjoint *_h3_singleshot roots
    (same-root reuse would let the compacted resume adopt headline run_ids and fabricate the H3
    null), h3ss_-prefixed batch names, and the -100 priority class."""
    import src.cluster.campaign as C
    from src.io.results import load_all

    fc = FakeCluster(tmp_path)
    run = ClusterRun(run_batch=fc.run_batch, spec_archive_root=str(tmp_path), read_root=tmp_path)
    frozen = _inject_select_freeze(run)

    # a PRE-EXISTING headline record with a COLLIDING run_id — the P4 adoption hazard
    write_run({
        "run_id": "distributional-g0-c1", "arm": "distributional", "seed": 0, "fold": 0,
        "candidate_id": "distributional-g0-c1", "generation": 0, "reward_source": "def reward(*a): return 0.0",
        "reward_source_hash": "HEADLINE", "prompt": "", "feedback_block": "", "wall_clock": 0.0,
        "env_fingerprint": "x", "metrics": {"val_fitness": 99.0, "val_returns": [0.01]},
    }, str(tmp_path / "search" / "distributional"))

    opts = _opts(generations=6, candidates=3)  # headline shape; C5 overrides gens itself
    opts["h3_singleshot_generations"] = 1
    out = C.run_h3_singleshot_on_cluster(
        opts, [0, 1], run,
        test_leg_kwargs=dict(panel_descriptor={"synthetic": True}, env_cfg={},
                             agent_cfg={"train_steps_per_candidate": 10}, train_window=(0, 5),
                             val_window=(6, 8), test_window=(9, 12), embargo=0, lookback=1),
        frozen_root=tmp_path / "frozen_h3_singleshot",
    )
    assert out["ok"] and out["arm"] == "distributional_singleshot"
    # the FULL candidate budget authored in ONE generation (no reflection at gens=1)
    ids = {r["run_id"] for r in load_all(str(tmp_path / "search_h3_singleshot" / "distributional"))}
    assert ids == {"distributional-g0-c0", "distributional-g0-c1", "distributional-g0-c2"}
    # sealed test leg at the campaign seeds, in ITS root
    tids = {r["run_id"] for r in load_all(str(tmp_path / "test_h3_singleshot" / "distributional"))}
    assert tids == {"distributional-s0", "distributional-s1"}
    # the headline root holds EXACTLY its pre-existing record (no adoption in, no writes out) and
    # the winner came from the H3 candidates (c2 = best index fitness), NOT the 99.0 headline decoy
    hd = load_all(str(tmp_path / "search" / "distributional"))
    assert [r["reward_source_hash"] for r in hd] == ["HEADLINE"]
    assert out["winner_id"] == "distributional-g0-c2" and frozen == ["distributional"]
    assert not (tmp_path / "test" / "distributional").exists()
    # every array namespaced h3ss_ + the C5 priority class
    assert fc.calls and all(name.startswith("h3ss_") for name, *_ in fc.calls)
    assert all(call[4] == C.PRIORITY_H3_SINGLESHOT for call in fc.calls)
    # construct fidelity: NO reflection at gens=1 — every candidate authored from the INITIAL
    # prompt (the archived prompts never carry the reflection preamble)
    h3recs = load_all(str(tmp_path / "search_h3_singleshot" / "distributional"))
    assert all(_REFLECTION_PREAMBLE not in (r.get("prompt") or "") for r in h3recs)


def test_seed_pool_blocks_striped_spec_merges_per_pool(tmp_path):
    """Launch ratification (2026-07-13): the STRIPED split (both pools engaged at every ladder
    rung) parses with repeated pool names MERGED into one block per pool — two same-pool blocks
    would otherwise submit two arrays under the same batch name (P12 lock collision)."""
    import src.cluster.campaign as C

    blocks = C.parse_seed_pool_blocks("EF:0-14,L:15-29,EF:30-64,L:65-99")
    assert [p for p, _ in blocks] == ["EF", "L"]  # merged, order-preserving
    ef, lp = dict(blocks)["EF"], dict(blocks)["L"]
    assert ef == set(range(0, 15)) | set(range(30, 65))
    assert lp == set(range(15, 30)) | set(range(65, 100))
    with pytest.raises(ValueError, match="overlap"):
        C.parse_seed_pool_blocks("EF:0-14,L:10-29")  # cross-pool overlap still fails loud
    with pytest.raises(ValueError, match="overlap"):
        C.parse_seed_pool_blocks("EF:0-14,EF:10-20")  # same-pool overlap is ALSO a spec error


def test_pending_specs_scopes_completion_to_each_specs_own_subroot(tmp_path):
    """2026-07-19 audit (CONFIRMED critical): test run_ids are bare ``{arm}-s{seed}`` so a disjoint
    -root invocation (H3 C5 test_h3_singleshot/, or a --root-suffix re-search) reuses run_ids that
    also exist under the headline test/ root. A mirror-wide completion diff would mark the H3 unit
    'done' from the HEADLINE record and never train it — a silently empty (fabricated) H3 archive.
    pending_specs must scope completion to each spec's OWN archive sub-root."""
    from src.cluster.poll import pending_specs
    from src.io.results import write_run

    mirror = tmp_path
    # The headline already wrote distributional-s0 under test/.
    write_run({"run_id": "distributional-s0", "arm": "distributional", "seed": 0, "fold": 0,
               "candidate_id": "distributional-winner", "generation": 0, "reward_source_hash": "h",
               "feedback_block": "", "wall_clock": 0.0, "env_fingerprint": "x", "frozen": True,
               "metrics": {"val_fitness": 0.0, "test_sharpe": 0.1, "test_returns": [0.01, -0.02]}},
              str(mirror / "test" / "distributional"))
    headline = {"run_id": "distributional-s0", "arm": "distributional",
                "archive_root": "/remote/outputs/test"}
    h3 = {"run_id": "distributional-s0", "arm": "distributional",
          "archive_root": "/remote/outputs/test_h3_singleshot"}
    pending = pending_specs([headline, h3], mirror)
    pending_roots = {Path(s["archive_root"]).name for s in pending}
    # The headline unit is done (record exists under test/); the H3 unit is NOT (empty h3 sub-root).
    assert pending_roots == {"test_h3_singleshot"}, (
        "the H3 spec must remain pending — its own test_h3_singleshot/ archive is empty")
    assert all(Path(s["archive_root"]).name != "test" for s in pending)
