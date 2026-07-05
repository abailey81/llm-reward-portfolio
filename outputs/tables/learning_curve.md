# Training-budget learning curve — reward `differential_sharpe` (device=cuda)

Read the budget at the PLATEAU: the smallest budget past which `eval_iqm_over_seeds` stops rising AND `critic_loss_max` is flat/finite. This is an engineering diagnostic on the machinery — no number enters the dissertation; it INFORMS the (amendment-gated) `train_steps_per_candidate`.

| budget | n_ok | eval IQM (seed-median) | eval spread | max critic loss | critic finite |
|--------|------|------------------------|-------------|-----------------|---------------|
| 25000 | 3 | -0.000319718 | 9.69e-05 | 409.5 | True |
| 50000 | 3 | -0.000702979 | 0.000192 | 409.5 | True |
| 100000 | 3 | -0.000412067 | 0.000217 | 409.5 | True |
| 200000 | 3 | -0.000309877 | 0.000358 | 409.5 | True |
| 350000 | 3 | -0.000560521 | 0.000202 | 409.5 | True |

## Convergence verdict (objective knee detector)

**⚠️ NOT CONVERGED** — recommended `train_steps_per_candidate` = **350000**

> no confirmed plateau (eval non-monotone/noisy across seeds, or critic non-finite near the ceiling); add --seeds and/or EXTEND --budgets higher

## Campaign duration projection (how long is enough)

**ADAPT** — projected **20.98 days** wall-clock (1007.1 GPU-h) for the full 600-training campaign at B* = `350000` steps, at 2x concurrency.

> 600 trainings x 350000 steps @ 17.3 ms/step = 1007 GPU-h; at 2x concurrency = 21.0 days -> tight — trim headline-first (full convergence on the H2 arms; fewer optional H1 seeds) or move to a faster GPU; no validity is lost

Run breakdown: {'search': 210, 'winners': 210, 'h1_baselines': 120, 'h3_singleshot': 60}.
