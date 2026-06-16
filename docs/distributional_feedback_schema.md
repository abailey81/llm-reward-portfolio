# Distributional feedback schema v1 — the novelty artefact  (plan block F2)
Implementation: `src/feedback_schema.py` (tested). Consumed by `prompts/reflection_distributional_v0.md`.
**Verified as-built 2026-06-10**: fields, sorting rule (stats on sorted; crossing_rate pre-sort), α-grid
single-sourced from `config/inference.yaml`, `empirical_cvar` now self-enforces ascending input (R5),
prompt block under the token budget — doc and code match.

**Source of quantiles.** The IQN critic models Z(s,a), the discounted-return distribution. We serialize
statistics of **Z(s₀, a₀)** (agent-internal view at episode start) AND cross-check against the empirical
distribution of realised held-out episode returns — the two are distinct objects and the schema labels which
is which (`source` field). Divergence between them is itself diagnostic (calibration figure, Pillar III).

**Sorting rule.** IQN's randomly-sampled τ make quantile CROSSING more likely than QR-DQN
(NeurIPS 2020, Non-Crossing QR). All tail statistics are computed on SORTED values; `crossing_rate` is
computed on the raw τ-ordered array first and reported so the LLM can discount noisy checkpoints.

**Fields.** `cvar_01, cvar_05, cvar_10, cvar_25` (mean of worst ⌈αN⌉ values); `mean, std`;
`bowley_skew` = (Q3+Q1−2·Q2)/(Q3−Q1) (robust) and `moment_skew`; `left_tail_slope` = OLS slope of
quantile value on τ for τ≤0.10 (crash-risk steepness); `crossing_rate`; `n_quantiles`; `source`.

**Why these fields (the theory doing work).** Every law-invariant coherent risk measure admits a Kusuoka
(2001) representation as a supremum of CVaR mixtures; spectral risk measures (Acerbi 2002) are weighted
integrals of the quantile function. A CVaR profile across α is therefore a discretisation of the canonical
coordinate system for the entire class of such risk objectives — the channel transmits a *basis* sufficient
to evaluate any of them, which is exactly what a designer of risk-sensitive rewards needs and what a scalar
Sharpe cannot carry. The α-grid {1,5,10,25}% is the discretisation choice; its error is acknowledged.

**Budget.** `to_prompt_block()` output stays under `llm.yaml: prompt_token_budget_reflection`.
