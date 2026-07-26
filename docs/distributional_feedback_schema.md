# Distributional feedback schema v1 — the novelty artefact  (plan block F2)

Implementation: the frozen tail-diagnostic set is **measured off-critic** by
`src/feedback/measurement.py` (`ReturnDistribution`, empirical body + EVT/GPD tails) and **serialized** into
the per-arm feedback block by `src/feedback/schema.py` (`build_block`). Both are unit-tested. The block is
rendered into the reflection prompt at runtime by the Eureka loop (`src/llm/loop.py`), which appends the
block directly to the in-code `_REFLECTION_PREAMBLE` — there is no template file in that path.
⚠ **CORRECTED 2026-07-26 (deep review loop 81, #54):** this sentence previously said "the live A-set
template is `prompts/reflection.txt` (it carries the `{ARM_BLOCK}` marker that `build_block` fills)".
`reflection.txt` is DEAD — no runtime path loads it, its `{ARM_BLOCK}` marker is never substituted, and
`scripts/freeze.py` excludes it from the bound treatment files for that reason.

**Source of the distribution (off-critic — audit A-1).** The statistics are measured **directly from the
realized portfolio simple (arithmetic, per-step) returns**, NOT read off any agent critic. They are computed on the **training-period**
realized returns (audit B-2: measuring on validation and then selecting on validation would re-introduce
overfitting), by a separate post-hoc estimator that reads no Q-network, so it is **critic-agnostic** (it works regardless of
the critic architecture — SB3 SAC mean-critic headline, TQC quantile-critic secondary) but is **NOT
agent-independent**: the tail is fit on the trained policy's OWN realized returns under the candidate reward,
so the fed signal is endogenous to the agent it steers (H2 compares two coupled reward→policy→measurement
loops, not an exogenous measurement). There is **no IQN critic** in the live design and no
`Z(s,a)` object: the audit rejected the neural-IQN line in favour of this empirical+EVT estimator
(`DECISIONS.md` ADR-022).

**Estimator (audit B-1).** EMPIRICAL is primary for the body (for a 1-D sample the empirical quantile is the
efficient estimator); a GENERALIZED-PARETO / EVT peaks-over-threshold fit (per EX-DRL) supplies the extreme
levels (CVaR-5%, CVaR-1%) where only ~7–37 tail observations exist. The level routing is at
`EVT_ALPHA_CUTOFF = 0.05` (≤ that → EVT; above → empirical).

**Data-dependent EVT→empirical fallback (R46 — do NOT read these levels as "unconditionally EVT").** The level
routing above (α ≤ 0.05 → EVT) is *necessary* but not *sufficient*. A per-candidate GPD fit additionally falls back
to the empirical estimator when the realised tail is too shallow for a reliable extreme-value fit — specifically
when the requested level α exceeds the peaks-over-threshold exceedance fraction `F_u`, or when the fitted shape
parameter ξ ≤ −0.5 (the non-regular GPD region; Smith 1985) or ξ ≥ 1 (infinite-mean tail). So `cvar_05` and
`cvar_01` are EVT-estimated *for a well-behaved tail* and empirical otherwise. This routing is **per candidate** and
is **logged** (`measurement.py::_record_fed_estimator` / `fed_estimator_log()`), so the realised estimator path
across the campaign is auditable and is reported in Results — the headline tail contrast is read against that log,
not assumed uniformly EVT.

**Fields (the frozen tail-diagnostic set — EXACTLY these six, returned by `ReturnDistribution.tail_stats`).**

| field | definition |
|---|---|
| `cvar_01` | CVaR at α = 1% (EVT/GPD for a well-behaved tail, else empirical — see the fallback note; **high-variance**) |
| `cvar_05` | CVaR at α = 5% (EVT/GPD for a well-behaved tail, else empirical — see the fallback note) |
| `cvar_10` | CVaR at α = 10% (empirical: mean of the worst ⌈αT⌉ returns) |
| `cvar_25` | CVaR at α = 25% (empirical) |
| `left_tail_mass` | `mean(returns < −k·std)`, k = 2.0 (`LEFT_TAIL_K`) |
| `robust_skew` | quantile (Bowley) skew `((Q95−Q50) − (Q50−Q05)) / (Q95−Q05 + eps)`, signed **negative** when the left tail is longer |

`cvar_01` is RETAINED but **explicitly flagged high-variance** (audit B-7): it is the EVT-extrapolated extreme
estimated from few tail observations, and the rendered distributional block annotates its line
"(high-variance estimate)" (`src/feedback/schema.py`).

> **Frozen-DROPPED (not in the live schema):** `crossing_rate`, `left_tail_slope`, `bowley_skew`/`moment_skew`
> (the live skew field is named `robust_skew`), `mean`, `std`, `n_quantiles`, and `source`. `crossing_rate`
> was a neural-IQN quantile-crossing reliability diagnostic with no off-critic analogue and was dropped from
> the headline at the merge (ADR-022); the others belonged to the pre-audit B-line `feedback_schema.py` now
> preserved under `archive/pre_merge_repo_B/src_flat/`.

**Why these fields (the theory doing work).** Every law-invariant coherent risk measure admits a Kusuoka
(2001) representation as a supremum of CVaR mixtures; spectral risk measures (Acerbi 2002) are weighted
integrals of the quantile function. A CVaR profile across α is therefore a discretisation of the canonical
coordinate system for the entire class of such risk objectives — the channel transmits a *basis* sufficient
to evaluate any of them, which is exactly what a designer of risk-sensitive rewards needs and what a scalar
Sharpe cannot carry. The α-grid {1, 5, 10, 25}% is the discretisation choice; its error is acknowledged.

**Budget.** The serialized block is matched in line-count/length across arms (`build_block`), so the H2
contrast isolates *information content*, not token count; it stays within the reflection token budget
(`config/llm.yaml`).
