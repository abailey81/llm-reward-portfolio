"""LLM-driven reward-discovery evolutionary loop (FINAL_PLAN F.8, B.3).

Purpose
-------
The core discovery loop. For a given experimental *arm* it prompts an LLM to
propose reward functions, validates and trains them, scores their held-out
fitness, and reflects across generations -- accumulating proposals into a
:class:`CandidateArchive`. The loop is the shared machinery; arms differ only in
the prompt's serialized "arm block" (see :func:`src.feedback.schema.build_block`).

Dependency injection
--------------------
Every heavy collaborator is injected so the loop is unit-testable WITHOUT real
training, a real LLM, or torch installed:

    - ``llm``           : has ``complete(system, user) -> str`` (the reward source).
    - ``agent_trainer`` : ``(env) -> policy`` (a trained policy; fake in tests).
    - ``measurement``   : factory of a fresh distribution estimator (e.g.
                          ``ReturnDistribution``) exposing ``.fit(returns)`` and
                          ``.tail_stats() -> dict``.
    - ``fitness_fn``    : ``(val_returns) -> float`` (e.g. ``held_out_fitness``).
    - ``env_builder``   : ``(reward_fn) -> env`` where ``env`` exposes
                          ``train_env()`` and ``val_returns(policy) -> np.ndarray``.

Algorithm (FINAL_PLAN B.3) -- runs ONCE per call
-------------------------------------------------
For each generation::

    build prompt  (system + initial for gen0, else reflection carrying the arm's
                   feedback block from schema.build_block)
    src  = llm.complete(system, user)
    fn   = validate_once(src, fixture)          # skip + log on SandboxError
    pol  = agent_trainer(env_builder(fn).train_env())
    valr = env.val_returns(pol)                 # realized VALIDATION returns
    fit  = fitness_fn(valr)                      # validation Deflated Sharpe
    dist = measurement().fit(train_returns)      # measure TRAINING realized returns
    tail = dist.tail_stats()
    block = schema.build_block(arm, fit, tail)   # next feedback block
    write_run(record, archive_root)              # archive (replay, audit C-2)
    reflect: carry block into the next generation's prompt

Single-shot semantics
----------------------
A single-shot arm spends the WHOLE matched budget in ONE generation
(``generations == 1``); multi-generation arms split the same budget across
generations. The total budget is matched across arms (FINAL_PLAN F.9). The
winner is the candidate with the best validation fitness.

Tests (tests/test_loop.py)
--------------------------
    - a 2-candidate / 1-gen loop archives reloadable artifacts (load_run round-trips).
    - the reflection prompt for the distributional arm CONTAINS the tail-stat lines
      (and the scalar arm does NOT).
    - a candidate whose source fails the sandbox gate is logged and SKIPPED.
    - single-shot draws the full budget in one generation.
    - the winner is the best-fitness candidate.
"""

from __future__ import annotations


import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from src.feedback import schema
from src.sandbox.executor import SandboxError, validate_once

__all__ = ["CandidateRecord", "CandidateArchive", "run_loop"]

_LOG = logging.getLogger(__name__)

#: System prompt used for every generation (arm-agnostic).
_SYSTEM_PROMPT = (
    "You are a reward-function engineer for a risk-sensitive portfolio RL agent. "
    "Return Python source defining `reward(weights, returns, prev_weights, "
    "port_ret, info)` using numpy only."
)

#: Initial (generation-0) user prompt; no prior feedback exists yet.
_INITIAL_PROMPT = (
    "Propose an initial reward function for the portfolio agent. "
    "Use numpy only and obey the reward contract."
)

#: Reflection-prompt preamble; the arm's feedback block is appended below it.
_REFLECTION_PREAMBLE = (
    "Reflect on the previous candidate's results and propose an improved reward "
    "function. Feedback from the previous candidate:"
)


@dataclass
class CandidateRecord:
    """One accepted candidate produced by :func:`run_loop`.

    Attributes
    ----------
    prompt : str
        The full rendered user prompt that produced this candidate.
    reward_source : str
        The raw reward source returned by the LLM.
    reward_hash : str
        SHA-256 hex digest of ``reward_source`` (provenance / dedup).
    feedback_block : str
        The serialized arm feedback block built from THIS candidate's results
        (carried forward into the next generation's reflection prompt).
    val_fitness : float
        Held-out (validation) fitness used for winner selection.
    tail_stats : dict
        The frozen tail-diagnostic set measured on TRAINING realized returns.
    generation : int
        The 0-based generation that produced this candidate.
    candidate_id : str
        Unique id within the run (``"{arm}-g{gen}-c{idx}"``).
    """

    prompt: str
    reward_source: str
    reward_hash: str
    feedback_block: str
    val_fitness: float
    tail_stats: dict
    generation: int
    candidate_id: str


@dataclass
class CandidateArchive:
    """Accumulated per-candidate records produced by one :func:`run_loop` call.

    Attributes
    ----------
    arm : str
        Name of the experimental arm that produced these candidates.
    candidates : list[CandidateRecord]
        Accepted candidate records, in generation/draw order.
    failures : list[dict]
        Logged validation failures that were skipped (audit trail); each holds
        ``generation``, ``reward_source``, and ``error``.
    meta : dict
        Run-level metadata (budget spent, generations, seeds, model id, etc.).

    Notes
    -----
    The winning candidate is the accepted record with the highest
    :attr:`CandidateRecord.val_fitness`; see :meth:`winner`.
    """

    arm: str
    candidates: list[CandidateRecord] = field(default_factory=list)
    failures: list[dict] = field(default_factory=list)
    meta: dict = field(default_factory=dict)

    def winner(self) -> CandidateRecord | None:
        """Return the accepted candidate with the best validation fitness.

        Returns
        -------
        CandidateRecord or None
            The best-fitness candidate, or ``None`` if none were accepted.
        """
        if not self.candidates:
            return None
        return max(self.candidates, key=lambda c: c.val_fitness)


def _cfg_get(cfg: Any, key: str, default: Any = None) -> Any:
    """Read ``key`` from a dict-like or attribute-like config object."""
    if cfg is None:
        return default
    if isinstance(cfg, dict):
        return cfg.get(key, default)
    return getattr(cfg, key, default)


def _reward_hash(src: str) -> str:
    """Stable SHA-256 hex digest of reward source."""
    return hashlib.sha256(src.encode("utf-8")).hexdigest()


def _budget_for_generation(total_budget: int, generations: int, gen: int) -> int:
    """Split a matched total budget evenly across generations.

    Single-shot arms (``generations == 1``) get the WHOLE budget in one
    generation; multi-generation arms split it, with any remainder front-loaded.
    """
    base = total_budget // generations
    remainder = total_budget % generations
    return base + (1 if gen < remainder else 0)


def run_loop(
    arm: str,
    env_builder: Any,
    llm: Any,
    agent_trainer: Any,
    measurement: Any,
    fitness_fn: Any,
    cfg: Any,
    archive_root: Any,
) -> CandidateArchive:
    """Run the LLM reward-discovery loop once for one arm (FINAL_PLAN B.3).

    Parameters
    ----------
    arm : str
        Experimental arm name; selects the serialized feedback block
        (``"distributional"``, ``"scalar"``, ``"placebo"``, ``"scalar_cvar5"``).
    env_builder : Any
        Callable ``(reward_fn) -> env``; ``env`` exposes ``train_env()`` and
        ``val_returns(policy) -> np.ndarray``.
    llm : Any
        An ``LLMClient`` (or compatible) with ``complete(system, user) -> str``.
    agent_trainer : Any
        Callable ``(train_env) -> policy`` returning a trained policy.
    measurement : Any
        Zero-arg factory of a fresh distribution estimator exposing
        ``.fit(returns)`` and ``.tail_stats() -> dict`` (e.g. ``ReturnDistribution``).
    fitness_fn : Any
        Callable ``(val_returns) -> float`` (e.g. ``held_out_fitness``).
    cfg : Any
        Configuration carrying ``generations`` (default 1), ``candidates_per_gen``
        (default 1), ``budget`` (matched total; default 0), ``seed``, ``n_trials``,
        ``model`` (id), and ``run_prefix``.
    archive_root : Any
        Directory passed to :func:`src.io.results.write_run` for each candidate.

    Returns
    -------
    CandidateArchive
        The accumulated, reloadable archive of candidates and artifacts. The
        winner is :meth:`CandidateArchive.winner`.

    Notes
    -----
    Runs ONCE; single-shot arms (``generations == 1``) spend the whole matched
    budget in one generation. Invalid candidates are logged in ``failures`` and
    SKIPPED -- they never crash the loop (audit A-5). Every accepted candidate is
    archived via ``write_run`` so results replay rather than regenerate (C-2).
    """
    from src.io.results import write_run

    generations = int(_cfg_get(cfg, "generations", 1))
    candidates_per_gen = int(_cfg_get(cfg, "candidates_per_gen", 1))
    total_budget = int(_cfg_get(cfg, "budget", 0))
    seed = _cfg_get(cfg, "seed", 0)
    n_trials = int(_cfg_get(cfg, "n_trials", 1))
    model_id = _cfg_get(cfg, "model", _cfg_get(getattr(llm, "cfg", None), "model", ""))
    run_prefix = _cfg_get(cfg, "run_prefix", "run")
    env_fingerprint = _cfg_get(cfg, "env_fingerprint", "injected")

    archive = CandidateArchive(arm=arm)
    archive.meta = {
        "generations": generations,
        "candidates_per_gen": candidates_per_gen,
        "budget": total_budget,
        "seed": seed,
        "model": model_id,
    }

    # Fixture passed to validate_once (anonymized arrays + scalar + info dict).
    fixture: tuple = (
        np.array([0.5, 0.5], dtype=float),   # weights
        np.array([0.01, -0.02], dtype=float),  # returns
        np.array([0.5, 0.5], dtype=float),   # prev_weights
        0.0,                                   # port_ret
        {},                                    # info
    )

    # The feedback block fed into the next generation's reflection prompt. None at
    # generation 0 -> the initial prompt is used; reflection thereafter.
    prev_feedback_block: str | None = None
    budget_spent = 0

    for gen in range(generations):
        gen_budget = _budget_for_generation(total_budget, generations, gen)

        # 1. Build the prompt: initial at gen 0, else reflection with the arm block.
        if prev_feedback_block is None:
            user_prompt = _INITIAL_PROMPT
        else:
            user_prompt = f"{_REFLECTION_PREAMBLE}\n{prev_feedback_block}"

        for cidx in range(candidates_per_gen):
            candidate_id = f"{arm}-g{gen}-c{cidx}"

            # 2. Sample a candidate reward source from the LLM.
            src = llm.complete(_SYSTEM_PROMPT, user_prompt)

            # 3. Validate; LOG + SKIP on failure (never crash the loop).
            try:
                reward_fn = validate_once(src, fixture)
            except SandboxError as exc:
                _LOG.warning(
                    "candidate %s failed validation and was skipped: %s",
                    candidate_id,
                    exc,
                )
                archive.failures.append(
                    {
                        "generation": gen,
                        "candidate_id": candidate_id,
                        "reward_source": src,
                        "error": str(exc),
                    }
                )
                continue

            # 4. Train the fixed agent on the (reward-bound) train env.
            env = env_builder(reward_fn)
            policy = agent_trainer(env.train_env())
            budget_spent += gen_budget

            # 5. Evaluate on the VALIDATION split (realized val returns).
            val_returns = np.asarray(env.val_returns(policy), dtype=float)

            # 6. Held-out fitness (validation Deflated Sharpe), reward-independent.
            val_fitness = float(fitness_fn(val_returns, n_trials))

            # 7. Measure the TRAINING realized-return distribution -> tail stats.
            train_returns = np.asarray(env.train_returns(policy), dtype=float)
            dist = measurement()
            dist.fit(train_returns)
            tail_stats = dist.tail_stats()

            # 8. Build the next feedback block (carry state forward).
            #    Tail-carrying arms get tail_stats; scalar/placebo get None.
            tail_for_block = (
                tail_stats if arm in ("distributional", "scalar_cvar5") else None
            )
            feedback_block = schema.build_block(arm, val_fitness, tail_for_block)

            reward_h = _reward_hash(src)
            record = CandidateRecord(
                prompt=user_prompt,
                reward_source=src,
                reward_hash=reward_h,
                feedback_block=feedback_block,
                val_fitness=val_fitness,
                tail_stats=tail_stats,
                generation=gen,
                candidate_id=candidate_id,
            )
            archive.candidates.append(record)

            # 9. Archive the candidate (replay, audit C-2). Conforms to the
            #    results-IO schema so load_run round-trips.
            run_id = f"{run_prefix}-{candidate_id}"
            write_run(
                {
                    "run_id": run_id,
                    "arm": arm,
                    "seed": seed,
                    "fold": _cfg_get(cfg, "fold", 0),
                    "candidate_id": candidate_id,
                    "generation": gen,
                    "reward_source": src,
                    "reward_source_hash": reward_h,
                    "feedback_block": feedback_block,
                    "metrics": {
                        "val_fitness": val_fitness,
                        "tail_stats": tail_stats,
                    },
                    "wall_clock": 0.0,
                    "env_fingerprint": env_fingerprint,
                },
                archive_root,
            )

            # 10. Reflect: this candidate's feedback block seeds the next prompt.
            prev_feedback_block = feedback_block

    archive.meta["budget_spent"] = budget_spent
    archive.meta["accepted"] = len(archive.candidates)
    archive.meta["failed"] = len(archive.failures)
    return archive
