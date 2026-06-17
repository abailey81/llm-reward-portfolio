# `prompts/` — LLM reward-designer prompt templates

**Status (post-merge, ADR-022).** The *live* prompts the Eureka loop currently sends are **hardcoded** in
[`../src/llm/loop.py`](../src/llm/loop.py) (`_SYSTEM_PROMPT`, `_INITIAL_PROMPT`, `_REFLECTION_PREAMBLE`).
The files here are **reference templates**, not yet loaded by the code — wiring `loop.py` to read them (and
filling `{ENV_INTERFACE}`) is build task **T4** (see the advanced-prototype blueprint). Until then this
folder is documentation, and the two sets below are kept side by side intentionally.

## The two sets
- **A (engine line) — `system.txt`, `initial_generation.txt`, `reflection.txt`.** The reference templates
  that correspond 1:1 to the hardcoded prompts in `loop.py`. `initial_generation.txt` carries the
  `{ENV_INTERFACE}` placeholder (the env/observation/action/reward contract to inject) and `reflection.txt`
  carries `{ARM_BLOCK}` (the per-arm feedback block, rendered at runtime by
  [`../src/feedback/schema.py`](../src/feedback/schema.py) `build_block`). These placeholders are filled by
  code at T4, not by hand.
- **B (data line) — `portfolio_system_prompt_v0.md`, `reflection_distributional_v0.md`,
  `reflection_scalar_v0.md`, `mutation_prompt_v0.md`, `safety_instruction.md`.** Earlier **arm-specific**
  variants — note the explicit `reflection_distributional` vs `reflection_scalar` split, which prefigures
  the headline H2 contrast (distributional vs scalar feedback). Retained as design reference to inform the
  T4 wiring; not superseded so much as not-yet-reconciled with the A templates.

## T4 (when implemented) should
1. Load the system/initial/reflection templates from this folder (single source of truth, no hardcoding).
2. Fill `{ENV_INTERFACE}` from the env spec (`../docs/environment_spec_v1.md`) — anonymised contract only.
3. Render `{ARM_BLOCK}` per arm via `feedback/schema.build_block`, reconciling the A templates with B's
   distributional/scalar variants.
