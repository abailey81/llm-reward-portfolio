# `prompts/` — LLM reward-designer prompt templates

**Status (post-merge, ADR-022/ADR-030).** Only the **A-set** templates live here, and they are the single
source of truth for the live loop. `src/llm/prompts.py::build_prompt_set` loads exactly `system.txt`,
`initial_generation.txt`, and `reflection.txt`; the orchestrator passes the rendered `PromptSet` to
`src/llm/loop.py` via `cfg["prompts"]` (the loop falls back to equivalent built-in minimal prompts —
`_SYSTEM_PROMPT`/`_INITIAL_PROMPT`/`_REFLECTION_PREAMBLE` — only when no prompts are supplied, e.g. unit
tests). No live code path loads any `*_v0.md` file.

## The live A-set
- **`system.txt`, `initial_generation.txt`, `reflection.txt`.** `system.txt` states the canonical reward
  contract `reward(weights, returns, prev_weights, port_ret, info) -> (total, components, reward_state)`
  (matching `src/reward/contract.py`). `initial_generation.txt` carries the `{ENV_INTERFACE}` placeholder
  (the env/observation/action/reward contract, filled by `src/llm/prompts.py::render_env_interface`), and
  `reflection.txt` carries `{ARM_BLOCK}` (the per-arm feedback block rendered at runtime by
  [`../src/feedback/schema.py`](../src/feedback/schema.py) `build_block` — the only thing that differs across
  the five LLM arms, so the contrast isolates information, not token-count).

## The B-set was archived (ADR-030)
The earlier **B-line arm-specific** variants — `portfolio_system_prompt_v0.md`,
`reflection_distributional_v0.md`, `reflection_scalar_v0.md`, `mutation_prompt_v0.md`,
`safety_instruction.md` — were **inert** (no code loaded them) and asserted the **abandoned IQN-SAC** line
(IQN-critic `Z(s0,·)` sourcing, the frozen-DROPPED `crossing_rate`/`left_tail_slope`, and a wrong
`compute_reward(ctx) -> (float, dict)` contract). They have been moved to
[`../archive/pre_merge_repo_B/prompts/`](../archive/pre_merge_repo_B/prompts/) for provenance — see that
folder and `DECISIONS.md` ADR-030. Their *intent* (the explicit distributional-vs-scalar H2 split) is fully
realised by `reflection.txt` + the per-arm `build_block`.
