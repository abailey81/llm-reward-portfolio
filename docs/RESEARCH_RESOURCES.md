# Research resources (deep web sweep, 2026-06-20)

42 resources that passed a strict 2-vote relevance vetting ("genuinely helpful for THIS project, not merely
topical; real URL; concrete action"). Grouped by use. Every entry is a citation, a cross-check oracle, a
baseline/control, or an adoptable component — not a reading list. Sourced by a 120-agent research workflow.

> **Headline takeaways.** (1) The *publishable gap holds*: no prior work feeds a return DISTRIBUTION / tail
> statistics as LLM reward-reflection feedback, and none applies reward-CODE search to portfolio RL — the
> closest finance analogue (MadEvolve) evolves *strategy* code on *scalar* PnL. (2) Three inference
> cross-check oracles are **already installed** (`rliable`, `arch.bootstrap.StepM`) or trivially addable
> (`pypbo`). (3) `skfolio`/`Riskfolio-Lib` and `empyrical-reloaded`/`ffn` are independent oracles for the
> just-rebuilt 8 allocators and the B11 metric suite.

## Cite / justify (lineage + theory)
- **Eureka** (Ma et al., ICLR 2024) — https://github.com/eureka-research/eureka (MIT). PRIMARY lineage: the
  reward-code reflection loop this project re-implements. Its aggregate/scalar reward-reflection format **IS
  the H2 scalar control arm** — instantiate the control by mirroring its prompt.
- **Beyond CVaR: static spectral risk measures** (Moghimi & Ku, ICML 2025) — https://arxiv.org/abs/2501.02087.
  HEADLINE THEORY for H2: a per-step/scalar risk knob is the wrong object; a coherent static spectral weighting
  over the full distribution is. Code: https://github.com/MehrdadMoghimi/QRSRM (MIT).
- **DSAC** (Distributional Soft Actor-Critic, JAIR 2025) — https://arxiv.org/pdf/2004.14547. Cleanest
  peer-reviewed H2 justification in the exact continuous-action SAC family: the mean is not a sufficient
  statistic for tail risk.
- **TQC** (Kuznetsov et al., ICML 2020) — https://arxiv.org/abs/2005.04269. REQUIRED citation for the TQC arm;
  source of `top_quantiles_to_drop_per_net`.
- **Text2Reward** (ICLR 2024) — https://github.com/xlang-ai/text2reward (SB3-native, pins SB3 1.8.0). Closest
  SB3-native precedent for LLM-written dense reward CODE; adopt its compact env-as-class grounding pattern.
- **REvolve** (ICLR 2025) — https://github.com/RishiHazra/Revolve (MIT). LLM-as-evolutionary-operator
  counterpoint to Eureka's independent sampling.
- **Auto MC-Reward** (CVPR 2024, https://arxiv.org/abs/2312.09238) + **Language-to-Rewards** (DeepMind,
  https://github.com/google-deepmind/language_to_reward_2023, Apache-2.0) + **RF-Agent** (NeurIPS 2025,
  https://github.com/deng-ai-lab/RF-Agent — NO LICENSE, cite only). Antecedents / outer-loop-operator framing.
- **Automated Reward Design for Gran Turismo** (Sony AI, Nov 2025, https://arxiv.org/abs/2511.02094) — closest
  published analogue: Eureka-style LLM-writes-reward on a SAC-family (QR-SAC, distributional) learner.
- **MadEvolve** (May 2026, https://arxiv.org/html/2605.23007v1) — single closest FINANCE LLM-code-search;
  confirms both gaps (strategy not reward code; scalar PnL not distribution). **When LLM Reward Design Fails**
  (https://arxiv.org/html/2605.28918) — contemporary support that structured feedback ≫ scalar.

## Cross-check oracles (validate my implementations as tests)
- **rliable** (google-research, Apache-2.0, **INSTALLED**) — https://github.com/google-research/rliable.
  Oracle for `inference.{reporting,bootstrap}.iqm` + probability_of_improvement + stratified-bootstrap CIs.
- **arch.bootstrap.StepM** (Romano-Wolf, **INSTALLED**, arch 7.2.0) —
  https://arch.readthedocs.io/en/latest/multiple-comparison/multiple-comparisons.html. GAP found: the
  Romano-Wolf stepdown in `multiple_testing.py` is **un-oracled** (the cross-check covers only BH + stationary
  bootstrap). ACTION: add a StepM agreement test.
- **esvhd/pypbo** (AGPL-3.0 — run ISOLATED, never vendor) — https://github.com/esvhd/pypbo. Twin of
  `overfitting.py::pbo` (same C(S,S/2) CSCV, ω=rank/(N+1)) + DSR/PSR. ACTION: dev-only PBO cross-check.
- **skfolio** (BSD-3) https://github.com/skfolio/skfolio + **Riskfolio-Lib** (BSD-3)
  https://github.com/dcajasn/Riskfolio-Lib — independent convex-solver oracle for the 8 rebuilt allocators
  (diff to ~1e-4 on matched covariance + HRP linkage). skfolio also has `CombinatorialPurgedCV` (CSCV ref).
- **empyrical-reloaded** (Apache-2.0) https://github.com/stefan-jansen/empyrical-reloaded + **ffn** (MIT)
  https://github.com/pmorissette/ffn — metric oracles for the B11 tearsheet (Sharpe/Sortino/Calmar/Omega/CVaR
  via empyrical; Ulcer/Martin-UPI via ffn, which empyrical lacks). ACTION: dev-only agreement tests.
- **vectorbt** ReturnsAccessor (offline only) — the one lib with BOTH deflated_sharpe_ratio AND coherent CVaR.

## Baselines / controls
- **FinRL** env_stocktrading.py (MIT, SB3-native) — https://github.com/AI4Finance-Foundation/FinRL. Net-of-cost
  portfolio-value-change reward → the "profit/return" hand-crafted reward baseline arm.
- **Moody & Saffell — Differential Sharpe Ratio** (NIPS 1998) —
  https://papers.nips.cc/paper/1551-reinforcement-learning-for-trading. The canonical "smarter scalar than raw
  Sharpe" online reward; already in `REWARD_CANON` — confirm the closed-form per-step EWMA update.
- **ACSRM / Risk-sensitive Actor-Critic SRM** (Moghimi & Ku 2025, https://arxiv.org/abs/2507.03900;
  https://github.com/MehrdadMoghimi/ACSRM, MIT) — a hand-coded *risk-sensitive non-LLM* control with a
  long-only transaction-cost portfolio twin.
- **FinRL-Meta** portfolio env (NeurIPS 2022) — https://github.com/AI4Finance-Foundation/FinRL-Meta. Closest
  public simplex/softmax-reallocation match; cross-check the projection + cost accounting.

## N3 contamination control
- **FinRL-DeepSeek** (MIT, arXiv:2502.07393) — https://github.com/benstaf/FinRL_DeepSeek. Closest published
  cousin (LLM + risk-sensitive portfolio RL + CVaR), DeepSeek/Qwen-authored → the contamination exemplar.
- **Profit Mirage + FinLake-Bench** (2025, https://arxiv.org/abs/2510.07920) — METHODOLOGICAL BACKBONE for N3:
  formalises leakage/memorization across GPT/DeepSeek/Qwen/Llama (vs Claude/Gemini absent); adopt its
  temporal-segmentation + input-perturbation test to prove the LLM uses the distribution causally.
- **QuantAgent** (Feb 2024, arXiv:2402.03755) + **Alpha Jungle MCTS** (AAAI 2026, arXiv:2505.11122) —
  contamination-timeline datapoints + multi-dimensional-feedback precedent.

## Adopt / throughput
- **sb3-contrib TQC** (**INSTALLED**) — https://sb3-contrib.readthedocs.io/en/master/modules/tqc.html. IS the
  TQC arm; `from sb3_contrib import TQC`, zero new infra.
- **SBX (SB3+JAX)** (araffin) — https://github.com/araffin/sbx. THE 30-seed SAC+TQC throughput lever (both
  frozen algos, SB3 API). **PARITY-GATE**: adopt ONLY if pre-registered before seed 1 and a 5-seed
  PyTorch-vs-SBX parity check passes — switching engines touches the frozen design.
- **SB3 SAC `train_freq`/`gradient_steps`** — https://stable-baselines3.readthedocs.io/en/master/modules/sac.html.
  The only unambiguously parity-safe throughput lever (hold the replay ratio constant).
