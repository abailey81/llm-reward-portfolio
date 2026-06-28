# Notes — FinRL-DeepSeek (Benhenda 2025, arXiv:2502.07393)  [closest prior art]
Pinned: CPPO (CVaR-PPO) + LLM-generated risk/recommendation signals from FNSPID news (DeepSeek-V3,
Qwen-2.5, Llama-3.3); Nasdaq-100; prices 2013–2023, backtest 2019–2023; basis of FinRL Contest 2025 Task 1.
Contrast sentence (use verbatim): "LLM-as-signal-generator (Benhenda 2025) vs LLM-as-reward-designer (this work)."
**CPPO (CVaR-PPO) objective** (Benhenda 2025 §4.1.2 eq. (1), attributing the CVaR-PPO form to Ying et al.
2022; transcribed from the full-text cache `C_signals_into_rewards__FinRL-DeepSeek__2502.07393.txt`
~:97-118):

> L_CVaR-PPO(θ, η, λ) = L_PPO(θ) + λ · [ (1 / (1 − α)) · E[(η − D(π_θ))₊] − η + β ]

where, in the paper's notation:
- **L_PPO(θ)** = the clipped PPO surrogate, L_PPO(θ) = E[ min( r_t(θ)·A_t, clip(r_t(θ), 1−ε, 1+ε)·A_t ) ],
  r_t(θ) = π_θ(a_t|s_t) / π_{θ_old}(a_t|s_t) the probability ratio, A_t the advantage, ε the clip range.
- **D(π_θ)** = the trajectory return (the random variable whose lower tail is constrained).
- **η** = the CVaR threshold (a VaR-like level; (η − D(π_θ))₊ = max(0, η − D(π_θ)) is the shortfall beyond it).
- **α** = the CVaR confidence level (e.g. 0.05 for the worst 5%).
- **λ** = the Lagrange multiplier enforcing the risk constraint; **β** = an auxiliary penalty parameter.
- The LLM signal enters *separately* (not in this loss) by scaling the action: a_t^mod = S_f · a_t, with the
  per-stock recommendation score S_f ≈ 1 (S_f>1 amplifies, S_f<1 dampens), kept near 1 for stability.

**Notation map to THIS project (the contrast, not a port):** Benhenda constrains the *agent's training
objective* (CVaR penalty inside the policy-gradient loss, a Door-B agent change) and injects the LLM as an
action-scaling *signal*. This work instead holds the **agent fixed (SB3 SAC)** and has the **LLM design the
reward-function code**, with the realized-return *distribution* (tail statistics incl. CVaR_α) fed back as
the reflection channel — "LLM-as-signal-generator (Benhenda 2025) vs LLM-as-reward-designer (this work)."
The shared object is CVaR_α(·) on the return tail; the locus differs (their training-loss constraint vs our
reward-design feedback). *(VERIFY: equation transcribed from the cached PDF text; the repo
`github.com/benstaf/FinRL_DeepSeek` agents/ code was NOT re-read first-hand for this note.)*
