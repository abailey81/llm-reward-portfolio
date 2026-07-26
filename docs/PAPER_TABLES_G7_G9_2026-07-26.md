# Paper tables G7–G9 (2026-07-26) — insertion-ready markdown

> Corpus-standard tables identified as missing vs top-band papers (deep sweep 2026-07-26). All values are
> first-hand-verified from `config/` + the frozen prompts (not asserted). Insertion targets noted per table;
> these are **[NOW]** (design/config facts, not campaign-gated). Reconcile numbering to final chapter order
> at compile. See `docs/METRICS_AND_FIGURES_COMPLETENESS_2026-07-26.md`.

---

## G7 — Fixed agent + training + environment configuration (reproducibility table)
**Insert:** CH4 Methods (§ agent/training). Doubles as a reproducibility artifact — every knob is held
IDENTICAL across arms (audit A-1), so only the reward differs. Verified from `config/agent.yaml`,
`config/environment.yaml`, `config/preregistration.yaml`.

| Group | Parameter | Value | Note |
|---|---|---|---|
| **Agent** | Algorithm | SB3 Soft Actor–Critic (Haarnoja 2018) | fixed architecture + hyperparameters across arms |
| | Policy / critic net | MlpPolicy (SB3 default) | |
| | Learning rate | 3 × 10⁻⁴ | |
| | Batch size | 256 | |
| | Discount γ | 0.99 | |
| | Entropy coefficient | `auto` (tuned) | adapts to reward scale (bounded by the PopArt ablation) |
| | Learning starts | 1 000 | the Phase-0-gated warmup (floored) |
| | Replay buffer | 50 000 (memory-safe cap, ADR-025) | decoupled from the step budget |
| | Obs normalization | train-only `VecNormalize` (`norm_obs=True`, `norm_reward=False`) | frozen train stats re-applied at eval |
| | Value-scale norm | PopArt-style (`popart=on`) | critic invariant to reward scale; `port_ret` forwarded unchanged |
| **Training** | Steps per candidate **B\*** | **400 000** | the measured knee (R77 pre-committed rule; ~90% of attainable gain at 2× compute) |
| | Candidates per arm | 30 | matched budget across all arms |
| | Winner seed ladder | tiered {30, 100, 189, 279, 340, 403, **568**} | assurance-tier ladder (403 = 95% primary target; 568 = 99%) |
| | float32 matmul (TF32) | on (Ampere/Ada) | identical in search + test (no select-vs-eval asymmetry) |
| **Environment** | Feature lookback | 60 trading days | |
| | Realized-vol windows | 20, 60 days | |
| | Action bound | pre-softmax logits ∈ [−10, 10] → simplex | long-only over risky assets + cash |
| | Transaction cost | 10 bps (headline; swept {0,…} report-only) | charged after the action (C-5) |
| | Purge / embargo | max(embargo 21, lookback 60) sessions at each split boundary | Lopez de Prado 2018 (R18 leakage guard) |
| **Splits (Split C)** | Train / Val / Test | 2005–2016 / 2017–2019 / **2020–2026 (sealed)** | select-on-val → freeze → test-once |

---

## G8 — Novelty matrix: the conjunctive empty cell (positioning table)
**Insert:** CH2 Related Work. The contribution is the **conjunction** of columns, not any single one — every
prior system satisfies some columns; **none satisfies all five**. Nearest neighbours verified first-hand
(corpus sweep). ✓ = yes · ✗ = no · ~ = partial (see notes).

| System (year) | Authors reward **CODE** | Iteration signal = realized **lower-tail** distribution | Risk-sensitive **finance**, no oracle | **Pre-registered** controlled comparison | **Off-critic** 3-way decoupling |
|---|:---:|:---:|:---:|:---:|:---:|
| Eureka (2023) | ✓ | ✗ (per-component scalar trajectories) | ✗ (robotics) | ✗ | ✗ |
| Text2Reward (2023) | ✓ | ✗ (scalar) | ✗ (robotics) | ✗ | ✗ |
| DrEureka (2024) | ✓ | ✗ (scalar) | ✗ (sim-to-real) | ✗ | ✗ |
| REvolve (2024) | ✓ | ✗ (human preference) | ✗ (driving) | ✗ | ✗ |
| CARD (2024) | ✓ | ✗ (trajectory preference) | ✗ (control) | ✗ | ✗ |
| Decision-Language-Model (2024) | ✓ | ~ (population-across-states spread) | ✗ (public health) | ✗ | ✗ (agent not held fixed) |
| GIFT (2026) | ~ (selects/clips from a rule library) | ✗ (scalar diagnostics) | ✓ | ✗ | ✗ |
| ELfolio (2025) | ✓ (strategy code) | ✗ (scalar Sharpe) — **our control condition** | ✓ | ✗ | ✗ |
| RD-Agent(Q) (2025) | ✓ (factor/model code) | ✗ (8 scalars; tops out at max-drawdown) | ✓ | ✗ | ✗ |
| **This work (2026)** | **✓** | **✓ (CVaR 5/10/25/1%, left-tail mass, robust skew)** | **✓** | **✓ (placebo + structure controls)** | **✓ (fed-train / select-val-DSR / test-CVaR)** |

**Notes.** DLM's "distribution" is a population-across-states spread in resource allocation, not the
realized-return *lower tail* of one agent's outcomes, and its agent is not held fixed off-critic. GIFT
composes/parameterises rewards from a *registered risk-rule library* (clipped before execution) — constrained,
not open-ended authorship. ELfolio's scalar-Sharpe evolution is exactly our `scalar` control arm. The novelty
claim is guarded by dated literature sweeps + a mandatory pre-submission sweep.

---

## G9 — Frozen prompt reference (reproducibility)
**Insert:** CH4 Methods (pointer) + **Appendix** (verbatim, word-excluded). The prompts are **hash-bound by
the freeze** (`scripts/freeze.py` binds the prompt files + `arms.yaml` + the inference family, R62), so the
exact author instructions are permanent. Reproduced verbatim in the appendix; the table indexes them.

| Prompt | File (frozen) | Role | Varies across arms? |
|---|---|---|---|
| System | `prompts/system.txt` | Persona + the reward-function contract (signature, sandbox rules, return type) | **No** — byte-identical across all arms |
| Initial generation | `prompts/initial_generation.txt` | First-candidate task prompt (design a reward from the task description) | **No** |
| Reflection | **in code**: `src/llm/loop.py::_REFLECTION_PREAMBLE` (+ `schema.build_block`) | The iterate prompt: a fixed two-sentence preamble + **the feedback block** | **Only the feedback block** — the single manipulated variable (multi-level tail vector vs scalar vs placebo) |

> ⚠ **CORRECTED 2026-07-26 (deep code-review loop 81, finding #54).** This row previously named
> `prompts/reflection.txt` and listed it as frozen. **That file is DEAD** — no runtime path loads it
> (verified: no `.py` in the repo reads it), and `scripts/freeze.py` **deliberately EXCLUDES** it from
> `_BOUND_TREATMENT` for exactly that reason (see its own comment). The reflection turn is composed at
> run time from the in-code `_REFLECTION_PREAMBLE` (`src/llm/loop.py`, verbatim: *"Reflect on the
> previous candidate's results and propose an improved reward function. Feedback from the previous
> candidate:"*) plus the per-arm block from `src/feedback/schema.py::build_block`. Publishing the old
> row would have shown an examiner a prompt file the model never received — and promised it "verbatim
> in the appendix". **The appendix must reproduce the in-code preamble, not `reflection.txt`.**
> ⚠ Note also that the frozen set is `arms.yaml` + `system.txt` + `initial_generation.txt`; the
> reflection preamble lives in Python source and is therefore **NOT hash-bound**. It is identical
> across arms (so identification is unaffected) and version-controlled, but whether to add it to
> `_BOUND_TREATMENT` is a pre-registration decision, not a documentation fix — flagged, not actioned.

**The identification hinge (state explicitly in CH4).** Every arm shares a byte-identical scaffold —
`system.txt` + `initial_generation.txt` (both frozen) + the in-code `_REFLECTION_PREAMBLE`; arms differ
ONLY in the feedback block spliced into the reflection prompt. That single-substitution design is what
makes any downstream difference attributable to the feedback *content* (audit A-1). The full verbatim
prompts — including the in-code preamble — appear in Appendix [X].
