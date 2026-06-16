# Mutation prompt v0 (iterations 2..N)
We trained agents with your previous best reward function (source below) and measured the outcomes in the
reflection block. Propose an IMPROVED reward function.

You may: (a) re-weight existing components, (b) change a component's functional form, (c) add or remove
components. Briefly state, in one sentence per change, the mechanism by which the change should improve the
HELD-OUT fitness (not the training reward). Then output the full revised function in one code block,
obeying the same contract and safety instruction.

[PREVIOUS_BEST_REWARD_SOURCE]
[REFLECTION_BLOCK]   <!-- scalar or distributional, per arm -->
