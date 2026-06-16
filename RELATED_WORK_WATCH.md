# RELATED_WORK_WATCH.md — Novelty surveillance log

The novelty claim is conjunctive — (LLM reward-code synthesis for portfolio RL) ∧ (distributional-critic
feedback to the LLM designer) — and is always stated with a "to the best of our knowledge" hedge plus the
date of the most recent sweep below. Re-sweep monthly and in the week before any submission.

**Standing queries.** "LLM reward design finance/trading/portfolio" · "Eureka finance" · "reward code
generation financial RL" · "distributional feedback LLM reward" · "quantile/CVaR feedback reward design
language model" · citation lists of Eureka (2310.12931), Text2Reward (2309.11489), FinRL-DeepSeek
(2502.07393) on Semantic Scholar/Google Scholar · ICAIF accepted-paper lists · FinRL Contest task pages.

---

## Entry 1 — 2026-06-10 (two adversarial deep-research sweeps)
**Result: gap intact on the conjunction.** No located work applies Eureka/Text2Reward-style LLM
reward-*code* synthesis to trading or portfolio RL; no located work in ANY domain feeds distributional-critic
(quantile/CVaR/tail) statistics back to an LLM reward designer.
**Closest prior art (cite-and-distinguish list):**
- FinRL-DeepSeek (Benhenda 2025, arXiv:2502.07393): LLM **signals** (news → risk/recommendation scores)
  into a hand-specified CVaR-PPO; Nasdaq-100 2013–2023. *Signal-generator, not reward-designer.*
- Unnikrishnan 2024 (arXiv:2411.11059): LLM sentiment inside a hand-designed reward. Same category.
- LEARN-Opt (arXiv:2511.19355) & "When LLM Reward Design Fails" (arXiv:2605.28918): LLM reward design
  variance/failure-mode evidence in control domains — methodological allies, not competitors.
- Dorka 2024 (arXiv:2409.10164): quantile regression *inside* RLHF reward models — different object entirely.
- RAMAC (arXiv:2510.02695): IQN critic + CVaR actor, offline RL, **no LLM**.
**Next sweep due:** ~2026-07-10, and again in the week before the 2 Aug ICAIF deadline.

