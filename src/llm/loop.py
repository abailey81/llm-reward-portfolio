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
import time
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from src.feedback import schema
from src.sandbox.executor import SandboxError, extract_reward_source, validate_once
from src.utils.config import cfg_get

__all__ = ["CandidateRecord", "CandidateArchive", "run_loop"]

_LOG = logging.getLogger(__name__)


class _NoMon:
    """No-op monitor: every ``monitor.<m>(...)`` call is a safe no-op when no RunMonitor is injected
    (unit tests, offline runs), so ``run_loop`` can call the monitor unconditionally."""

    def __getattr__(self, _name: str) -> Any:
        return lambda *a, **k: None


_NULL_MONITOR = _NoMon()

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
    popart_scale : dict or None
        The realised PopArt scale the SAC critic saw while training THIS candidate (T2.4):
        ``{"popart": 1.0, "sigma_max", "sigma_last", "count"}`` when PopArt is on, ``{"popart": 0.0}``
        when off, or ``None`` if the trainer did not surface it (e.g. a fake test trainer). Logged so the
        CROSS-ARM ``sigma`` distribution is auditable — a unit ``sigma_max`` across arms shows the
        "fixed-agent" design carries no latent, scale-driven entropy-regularisation difference.
    """

    prompt: str
    reward_source: str
    reward_hash: str
    feedback_block: str
    val_fitness: float
    tail_stats: dict
    generation: int
    candidate_id: str
    popart_scale: dict | None = None


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


def _reward_hash(src: str) -> str:
    """Stable SHA-256 hex digest of reward source."""
    return hashlib.sha256(src.encode("utf-8")).hexdigest()


def _diversity_directive(cidx: int, n: int) -> str:
    """A per-candidate exploration directive giving within-generation diversity by PROMPT VARIATION.

    Eureka samples ``n`` candidates per generation from the SAME prompt and relies on sampling
    ``temperature`` for variety; a reward-author that rejects the ``temperature`` parameter
    (e.g. Claude Opus 4.8) needs the variety injected another way. Appending a distinct directive
    per candidate index does that. The directive set is IDENTICAL across arms AND (R38 de-seed)
    names NO specific risk statistic — it asks the LLM to vary WHICH statistics it tracks, not to use
    CVaR/drawdown — so it neither differentially favours an arm nor pre-seeds the tail to the
    non-distributional arms; only the arm's feedback block introduces the tail. Also reused by the
    parallel scheduler (``src/orchestration/parallel.py``) so both run paths diversify identically.
    """
    return (
        f"[Exploration directive {cidx + 1}/{n}: propose a reward DISTINCT from the other "
        f"candidates this generation — vary which statistics of the return history you track, the "
        f"rolling window, and the functional form. Do not reuse a design you would give a different "
        f"candidate index.]"
    )


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

    generations = int(cfg_get(cfg, "generations", 1))
    candidates_per_gen = int(cfg_get(cfg, "candidates_per_gen", 1))
    total_budget = int(cfg_get(cfg, "budget", 0))
    seed = cfg_get(cfg, "seed", 0)
    n_trials = int(cfg_get(cfg, "n_trials", 1))
    model_id = cfg_get(cfg, "model", cfg_get(getattr(llm, "cfg", None), "model", ""))
    run_prefix = cfg_get(cfg, "run_prefix", "run")
    env_fingerprint = cfg_get(cfg, "env_fingerprint", "injected")
    # Within-generation diversity by per-candidate PROMPT VARIATION (uniform across arms) — needed
    # when the reward-author rejects the ``temperature`` parameter (e.g. Claude Opus 4.8). Off by
    # default (temperature-honoring models like Gemini get diversity from sampling instead).
    diversity = bool(cfg_get(cfg, "diversity_prompt_variation", False))
    monitor = cfg_get(cfg, "monitor", None) or _NULL_MONITOR  # RunMonitor; no-op when absent (tests/offline)

    # C3 (ADR-029): when the orchestrator supplies rendered prompts (system + initial with the
    # env interface filled, src/llm/prompts.py), use them; else fall back to the built-in minimal
    # prompts so unit tests need no prompt files. The REFLECTION body is composed from the arm's
    # feedback block (schema.build_block) either way — that block is the only thing that differs
    # across the five LLM arms and is what carries the tail diagnostics for the distributional arm.
    _prompts = cfg_get(cfg, "prompts", None)
    if _prompts is None:
        system_prompt, initial_prompt = _SYSTEM_PROMPT, _INITIAL_PROMPT
    else:
        system_prompt = _prompts["system"] if isinstance(_prompts, dict) else _prompts.system
        initial_prompt = _prompts["initial"] if isinstance(_prompts, dict) else _prompts.initial

    archive = CandidateArchive(arm=arm)
    archive.meta = {
        "generations": generations,
        "candidates_per_gen": candidates_per_gen,
        "budget": total_budget,
        "seed": seed,
        "model": model_id,
    }

    # Fixture passed to validate_once (anonymized arrays + scalar + info dict).
    # Real-ish per-step shapes (final-audit #12): a realistic asset count so a reward whose
    # allocation scales with the input surfaces at validate_once (under the Linux child's RLIMIT_AS)
    # rather than only at training time, where safe_call has no rlimit/timeout. Equal-length arrays
    # keep the smoke contract-agnostic; the true N+1-vs-N shapes are exercised during training.
    _n_fix = max(2, int(cfg_get(cfg, "fixture_n_assets", 31)))
    fixture: tuple = (
        np.full(_n_fix, 1.0 / _n_fix, dtype=float),   # weights (simplex over ~30 risky + cash)
        np.full(_n_fix, 0.001, dtype=float),          # returns
        np.full(_n_fix, 1.0 / _n_fix, dtype=float),   # prev_weights
        0.0,                                          # port_ret
        {},                                           # info
    )

    # The feedback block fed into the next generation's reflection prompt. None at
    # generation 0 -> the initial prompt is used; reflection thereafter.
    prev_feedback_block: str | None = None
    budget_spent = 0

    for gen in range(generations):
        gen_budget = _budget_for_generation(total_budget, generations, gen)
        # Spend the generation's budget ONCE per generation (M2 fix, ADR-026): gen_budget is the
        # WHOLE generation's allocation, so accumulate it here — not inside the per-candidate loop,
        # where with candidates_per_gen>1 it over-counted by a factor of the accepted-candidate count
        # (and excluded failures). Summed over generations this equals total_budget, the matched
        # spend, restoring a correct archive.meta['budget_spent'] provenance figure.
        budget_spent += gen_budget

        # 1. Build the prompt: initial at gen 0, else reflection with the arm block.
        if prev_feedback_block is None:
            user_prompt = initial_prompt
        else:
            user_prompt = f"{_REFLECTION_PREAMBLE}\n{prev_feedback_block}"

        # M5: reflect on the generation's BEST candidate (Eureka-faithful + parity with the parallel
        # path), not the last. Track the best WITHIN this generation; seed the next prompt at the boundary.
        gen_best_fitness: float | None = None
        gen_best_block: str | None = None

        for cidx in range(candidates_per_gen):
            candidate_id = f"{arm}-g{gen}-c{cidx}"
            cand_n = gen * candidates_per_gen + cidx  # 0-based candidate index WITHIN the arm
            monitor.candidate_start(arm, cand_n, gen)
            cand_t0 = time.perf_counter()

            # Per-candidate prompt variation -> within-generation diversity without temperature
            # (see _diversity_directive). cand_prompt is the EXACT prompt sent + archived (C-2).
            cand_prompt = user_prompt
            if diversity and candidates_per_gen > 1:
                cand_prompt = f"{user_prompt}\n\n{_diversity_directive(cidx, candidates_per_gen)}"

            # 2. Sample a candidate reward source from the LLM, salvaging fenced / prose-wrapped
            #    output so a well-formed reward is never rejected for FORMATTING (final-audit P0).
            _llm_t0 = time.perf_counter()
            src = extract_reward_source(llm.complete(system_prompt, cand_prompt))
            _arch = getattr(llm, "archive", None)  # LLMClient archives a ProvenanceRecord (with token usage)
            _u = (getattr(_arch[-1], "usage", None) or {}) if _arch else {}
            monitor.llm_call(arm, cand_n, secs=time.perf_counter() - _llm_t0,
                             in_tok=_u.get("input_tokens"), out_tok=_u.get("output_tokens"), model=model_id)

            # 3. Validate; LOG + SKIP on failure (never crash the loop).
            try:
                reward_fn = validate_once(src, fixture)
                monitor.sandbox_result(arm, cand_n, ok=True)
            except SandboxError as exc:
                _LOG.warning(
                    "candidate %s failed validation and was skipped: %s",
                    candidate_id,
                    exc,
                )
                monitor.sandbox_result(arm, cand_n, ok=False, reason=str(exc)[:120])
                monitor.candidate_done(arm, cand_n, fitness=None, status="sandbox_reject",
                                       secs=time.perf_counter() - cand_t0)
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
            # T2.4: capture the realised PopArt scale the critic saw for this candidate (None for a
            # fake/raw trainer that does not surface it) so the cross-arm sigma distribution is auditable.
            popart_scale = getattr(policy, "popart_scale", None)

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
            #    Tail-carrying arms get tail_stats; scalar/placebo get None. placebo_shuffled (R32)
            #    is tail-carrying too, but its values are deranged by a candidate-seeded shuffle.
            tail_for_block = (
                tail_stats
                if arm in ("distributional", "scalar_cvar5", "placebo_shuffled")
                else None
            )
            feedback_block = schema.build_block(
                arm,
                val_fitness,
                tail_for_block,
                shuffle_seed=(
                    schema.shuffle_seed_from_id(candidate_id)
                    if arm == "placebo_shuffled"
                    else None
                ),
            )

            reward_h = _reward_hash(src)
            record = CandidateRecord(
                prompt=cand_prompt,
                reward_source=src,
                reward_hash=reward_h,
                feedback_block=feedback_block,
                val_fitness=val_fitness,
                tail_stats=tail_stats,
                generation=gen,
                candidate_id=candidate_id,
                popart_scale=popart_scale,
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
                    "fold": cfg_get(cfg, "fold", 0),
                    "candidate_id": candidate_id,
                    "generation": gen,
                    # Rank 14: persist the rendered prompt so the replay archive doesn't DROP it
                    # (CLAUDE.md directive 6: "archive every prompt"). results.write_run dumps it to
                    # a prompt.txt sidecar; OPTIONAL_FIELDS so REQUIRED_FIELDS / round-trips unchanged.
                    "prompt": cand_prompt,
                    "reward_source": src,
                    "reward_source_hash": reward_h,
                    "feedback_block": feedback_block,
                    "metrics": {
                        "val_fitness": val_fitness,
                        "tail_stats": tail_stats,
                        # Realized validation returns archived so analyze_results can run the
                        # Sharpe/CVaR difference tests + FZ ES backtest on the winners (P6).
                        "val_returns": [float(x) for x in val_returns],
                        # T2.4: realised PopArt scale (sigma_max/last) the critic saw, for the cross-arm
                        # sigma audit. Optional/back-compatible (omitted when the trainer doesn't surface it).
                        **({"popart_scale": popart_scale} if popart_scale is not None else {}),
                    },
                    "wall_clock": 0.0,
                    "env_fingerprint": env_fingerprint,
                },
                archive_root,
            )

            # 10. Reflect-on-BEST (M5): track the generation's best candidate; its feedback block
            #     seeds the NEXT generation's prompt (set at the generation boundary below).
            if gen_best_fitness is None or val_fitness > gen_best_fitness:
                gen_best_fitness = val_fitness
                gen_best_block = feedback_block
            monitor.candidate_done(arm, cand_n, fitness=val_fitness, status="ok",
                                   secs=time.perf_counter() - cand_t0)

        # Generation boundary: the generation's BEST candidate seeds the next prompt (M5 reflect-on-
        # best — Eureka-faithful, and consistent with the parallel reflect-on-best path).
        if gen_best_block is not None:
            prev_feedback_block = gen_best_block

    archive.meta["budget_spent"] = budget_spent
    archive.meta["accepted"] = len(archive.candidates)
    archive.meta["failed"] = len(archive.failures)
    return archive
