"""Tests for the LLM reward-discovery loop (FINAL_PLAN F.8, B.3).

Everything heavy is injected via fakes (no real LLM, training, or torch):
    - FakeLLM     : returns a fixed VALID numpy reward source and records prompts.
    - FakeEnv     : built per reward; yields synthetic train/val returns.
    - fake_trainer: returns a fake policy (carries a per-candidate fitness seed).

Covers: reloadable archive (load_run round-trips), reflection-prompt arm block
(distributional carries tail-stat lines; scalar does not), sandbox-gate failures
logged + skipped, single-shot budget, and best-fitness winner selection.
"""

from __future__ import annotations


import numpy as np

from src.io.results import load_run
from src.llm import loop
from src.selection.fitness import held_out_fitness


# A valid reward conforming to the contract; passes the sandbox AST gate.
_VALID_REWARD_SRC = (
    "def reward(weights, returns, prev_weights, port_ret, info):\n"
    "    total = float(np.dot(weights, returns))\n"
    "    return total, {'pnl': total}, None\n"
)

# Fails the AST gate (forbidden import).
_INVALID_REWARD_SRC = (
    "import os\n"
    "def reward(weights, returns, prev_weights, port_ret, info):\n"
    "    return 0.0, {}, None\n"
)


class FakeLLM:
    """Injected LLM stub: returns a fixed source and records every prompt."""

    def __init__(self, source: str, cfg: dict | None = None) -> None:
        self.source = source
        self.cfg = cfg or {"model": "fake-model-2026"}
        self.prompts: list[tuple[str, str]] = []

    def complete(self, system: str, user: str) -> str:
        self.prompts.append((system, user))
        return self.source


class FakePolicy:
    """A fake trained policy carrying a deterministic return level."""

    def __init__(self, level: float) -> None:
        self.level = level


class FakeEnv:
    """Per-reward fake env exposing train/val realized returns."""

    _counter = 0

    def __init__(self, reward_fn) -> None:
        self.reward_fn = reward_fn
        # Distinct level per construction so successive candidates differ.
        FakeEnv._counter += 1
        self.level = float(FakeEnv._counter)

    def train_env(self):
        return self

    def train_returns(self, policy) -> np.ndarray:
        rng = np.random.default_rng(int(self.level) * 7 + 1)
        # Negative-mean, heavy-ish tail so tail_stats are well-defined.
        return -0.001 + 0.01 * rng.standard_t(5, size=512)

    def val_returns(self, policy) -> np.ndarray:
        # Higher policy.level -> higher mean -> higher fitness (deterministic).
        rng = np.random.default_rng(int(self.level) * 13 + 3)
        return policy.level * 0.001 + 0.01 * rng.standard_normal(512)


def _make_trainer():
    """Trainer assigning ascending policy levels so winner selection is checkable."""
    state = {"n": 0}

    def _train(train_env) -> FakePolicy:
        state["n"] += 1
        return FakePolicy(level=float(state["n"]))

    return _train


def _measurement_factory():
    from src.feedback.measurement import ReturnDistribution

    return ReturnDistribution()


def _run(arm: str, source: str, cfg: dict, archive_root):
    """Run the loop with the standard fakes and return (archive, llm)."""
    FakeEnv._counter = 0
    llm = FakeLLM(source)
    archive = loop.run_loop(
        arm=arm,
        env_builder=FakeEnv,
        llm=llm,
        agent_trainer=_make_trainer(),
        measurement=_measurement_factory,
        fitness_fn=held_out_fitness,
        cfg=cfg,
        archive_root=archive_root,
    )
    return archive, llm


def test_two_candidate_one_generation_archives(tmp_path) -> None:
    """A 2-candidate / 1-generation run archives reloadable artifacts."""
    cfg = {"generations": 1, "candidates_per_gen": 2, "budget": 100, "n_trials": 5}
    archive, _ = _run("distributional", _VALID_REWARD_SRC, cfg, tmp_path)

    assert len(archive.candidates) == 2
    for cand in archive.candidates:
        record = load_run(f"run-{cand.candidate_id}", tmp_path)
        assert record["arm"] == "distributional"
        assert record["reward_source_hash"] == cand.reward_hash
        # reward.py is reattached on load -> replay, not regenerate (C-2).
        assert "reward_source" in record
        assert record["reward_source"] == _VALID_REWARD_SRC
        assert record["metrics"]["val_fitness"] == cand.val_fitness


def test_reflection_prompt_distributional_has_tail_lines_scalar_does_not(tmp_path) -> None:
    """Distributional reflection prompt carries tail-stat lines; scalar does not."""
    cfg = {"generations": 2, "candidates_per_gen": 1, "budget": 100, "n_trials": 5}

    dist_archive, dist_llm = _run("distributional", _VALID_REWARD_SRC, cfg, tmp_path / "d")
    # Gen 0 prompt is the initial prompt; gen 1 is the reflection prompt.
    gen1_user = dist_llm.prompts[1][1]
    assert "tail diagnostics" in gen1_user
    assert "CVaR 5%" in gen1_user
    assert "left-tail" in gen1_user

    scalar_archive, scalar_llm = _run("scalar", _VALID_REWARD_SRC, cfg, tmp_path / "s")
    scalar_gen1_user = scalar_llm.prompts[1][1]
    assert "CVaR" not in scalar_gen1_user
    assert "tail diagnostics" not in scalar_gen1_user
    # Both produced one accepted candidate per generation.
    assert len(dist_archive.candidates) == 2
    assert len(scalar_archive.candidates) == 2


def test_validation_failure_logged_and_skipped(tmp_path) -> None:
    """A candidate failing the sandbox gate is logged and skipped, not fatal."""
    cfg = {"generations": 1, "candidates_per_gen": 2, "budget": 100, "n_trials": 5}
    archive, _ = _run("scalar", _INVALID_REWARD_SRC, cfg, tmp_path)

    # No candidate accepted; both draws failed and were recorded.
    assert archive.candidates == []
    assert len(archive.failures) == 2
    assert all("error" in f for f in archive.failures)
    assert archive.winner() is None


def test_single_shot_draws_full_budget_in_one_generation(tmp_path) -> None:
    """A single-shot arm spends the whole matched budget in one generation."""
    cfg = {"generations": 1, "candidates_per_gen": 1, "budget": 250, "n_trials": 5}
    archive, llm = _run("scalar", _VALID_REWARD_SRC, cfg, tmp_path)

    assert archive.meta["generations"] == 1
    assert archive.meta["budget_spent"] == 250
    # Exactly one generation -> one prompt drawn, the INITIAL prompt.
    assert len(llm.prompts) == 1
    assert archive.candidates[0].generation == 0


def test_winner_is_best_fitness_candidate(tmp_path) -> None:
    """The winner is the accepted candidate with the highest validation fitness."""
    cfg = {"generations": 1, "candidates_per_gen": 4, "budget": 100, "n_trials": 5}
    archive, _ = _run("distributional", _VALID_REWARD_SRC, cfg, tmp_path)

    assert len(archive.candidates) == 4
    winner = archive.winner()
    best = max(c.val_fitness for c in archive.candidates)
    assert winner is not None
    assert winner.val_fitness == best
