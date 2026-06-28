# Reflection template — DISTRIBUTIONAL arm (the novelty channel)
<!-- Everything in the scalar template PLUS the IQN-derived return-distribution block
     (src/feedback_schema.py serializer; quantiles SORTED before stats; crossing rate reported pre-sort).
     Theory: a CVaR profile across alpha levels is a discretisation of the canonical coordinates of
     law-invariant coherent risk measures (Kusuoka 2001) — see docs/distributional_feedback_schema.md. -->
[ALL FIELDS FROM reflection_scalar_v0]

Return-DISTRIBUTION diagnostics from the IQN critic at Z(s0,·), cross-checked against empirical
held-out episode returns:
{distributional_block}    <!-- emitted by feedback_schema.to_prompt_block() -->

Interpretation hints for you (the designer):
- cvar_05 vs mean gap = left-tail thickness your current reward tolerates;
- left_tail_slope steepening across checkpoints = the policy is concentrating crash risk;
- bowley_skew < 0 with rising sharpe = gains bought with asymmetric downside;
- crossing_rate > {crossing_warn} = treat tail stats this checkpoint as noisy.
Use these to decide WHICH component to change, not just how much.
