# Research brief — one page for the first group meeting  (Tamer Atesyakar, w/c 8 Jun 2026)

**Title.** Can Large Language Models Design Reward Functions for Risk-Sensitive Portfolio RL?
An Eureka-Style Evaluation with Distributional Feedback on US Equities, 2005–2025.

**RQ.** Do LLM-evolved reward functions, refined under distributional (IQN) tail-risk feedback, produce
deep-RL portfolio policies with superior out-of-sample risk-adjusted performance vs hand-designed rewards,
on a survivorship-free 30-stock US large-cap universe (2005–2025), across regimes and under 0–50bps costs?

**What the core paper used as data → implication.** Eureka used NO dataset (simulators + code-as-context +
a separate ground-truth fitness). Finance has neither: the environment is BUILT from data (data quality
bounds everything — hence data-first), and fitness must be HELD-OUT (no oracle).

**Who used the paradigm, on what data.** Robotics/games/control only (DrEureka, Text2Reward, L2R,
Auto MC-Reward, LEARN-Opt, REvolve). Finance: none for reward design (3 sweeps + 2 adversarial re-checks,
latest 10 Jun 26). Closest: FinRL-DeepSeek — LLM signals from FNSPID news into a hand-written CVaR-PPO,
Nasdaq-100 2013–23. Distinction: LLM-as-signal-generator vs LLM-as-reward-designer (this work).

**My data + required characteristics.** 30 US large-caps, point-in-time S&P membership (Refinitiv ≥2016;
Datastream LS&PCOMP lists 2005–16), RI total returns, Shumway delisting corrections, Ince–Porter screens,
yfinance cross-validation, FRED VIX/rates, French factors. Characteristics: regime-diverse (GFC→2025),
survivorship-free/PIT, total-return, cost-modellable, frozen+checksummed.
*Live status (10 Jun):* pipeline built and run end-to-end on real data — clean panel **5,282 sessions ×
35 names** (2005–2025, shadow universe, **provisional pending PIT membership**), all pulls SHA-256-
manifested; embargoed splits materialised exactly per the pre-registration (dev validation starts 21
trading days after the boundary). EDA headline: excess kurtosis up to **49.9** (Citigroup), Hill left-tail
index **2.1–3.6 across all 35 names** — the empirical case for CVaR-penalised selection. Entitlements:
LSEG credentials authenticate but data scopes are pending (DSWS needs one service flag; escalation drafted);
build degrades gracefully and back-fills when access lands.

**Core papers.** (1) Ma et al. 2024 "Eureka" — the method, adapted with out-of-sample fitness,
regime-contextual reflection, mandate conditioning. (2) Dabney et al. 2018 IQN — the risk channel; my novel
piece feeds its quantile statistics back to the LLM. (3) Khraishi & Okhrati 2022 ICAIF — finance-RL
discipline + the offline/online frame: replay-sim satisfies the harm criterion; reward-relabelling makes
the search offline-compatible for deployment.

**Either-way design.** Matched-compute baselines (random/BayesOpt/single-shot/differential-Sharpe) +
selection-aware inference (DSR over the true candidate count; PBO) → a negative result is a strong result.
Pre-registration is staged to freeze Friday 12 Jun (commit-hash protocol; deviations thereafter are
flagged ADRs with supervisor notification).

**Question for Ramin.** ICAIF 2026 deadline is 2 Aug (before the dissertation): main track / workshop /
dissertation-first?
