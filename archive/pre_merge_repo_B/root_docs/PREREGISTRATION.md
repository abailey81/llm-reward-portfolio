# PREREGISTRATION — Experimental Design v1.0

**Status: DRAFT.** This document becomes FROZEN the moment it is committed with the message
`T4: freeze pre-registration v1.0` and its commit hash is recorded in `DECISIONS.md` (target: 12 June 2026).
After freezing, any change is a **deviation**: it requires a dated ADR, supervisor notification, and explicit
disclosure in the dissertation. The dissertation will cite: *"Design frozen 12 June 2026, commit `<hash>`."*

Rationale: the reward search below evaluates hundreds of candidate strategies. Without a pre-committed
design, every reported number is vulnerable to the selection-bias critique (Bailey & López de Prado, 2014).
Pre-registration is what makes the Deflated Sharpe Ratio computable with an honest trial count, and what
makes a negative result *strong* rather than apologetic — per the supervisor's explicit guidance.

---

## 1. Research question (primary, verbatim everywhere)

> Do LLM-evolved reward functions, refined under distributional (IQN) tail-risk feedback, produce deep-RL
> portfolio policies with superior out-of-sample risk-adjusted performance versus hand-designed rewards, on a
> survivorship-bias-free 30-stock US large-cap universe (2005–2025), across market regimes and under
> realistic transaction costs?

## 2. Hypotheses (two-sided unless stated; tested per §7)

- **H1 (LLM priors).** Best LLM-evolved reward ≠ best hand-designed reward on held-out fitness, net of costs.
  Direction of interest: LLM > hand-designed.
- **H2 (Distributional channel — the novelty hypothesis).** Rewards evolved under *distributional* reflection
  ≠ rewards evolved under *scalar* reflection at matched compute. Direction of interest: distributional > scalar.
- **H3 (Iteration).** Generation-5 best ≠ generation-1 best at matched total candidate count
  (evolution vs single-shot sampling).
- **H4 (Search value).** LLM search ≠ matched-compute random reward search and Bayesian-optimisation
  search over the parameterised reward family.

Pre-committed interpretation: if H1/H2 fail to reject (or reject in the negative direction) under the
machinery of §7, the dissertation's headline becomes a *rigorous negative result with diagnosis*
(variance decomposition, regime analysis, reward-code forensics). This is declared in advance.

## 3. Fitness function (selection criterion — never the training reward)

**F = SR_val − λ · max(0, −CVaR̂_α(r_val))**, computed on the **validation window only**, where

- `SR_val` = unannualised Sharpe ratio of daily net portfolio returns on the validation window;
- `CVaR̂_α` = empirical CVaR at **α = 5%** of daily net returns (mean of the worst ⌈αT⌉ days);
- `λ` is calibrated ONCE by grid {0, 1, 2, 5, 10} on a **pre-2015 calibration fold**
  (train 2005–2012, validate 2013–2014, hand-designed rewards only), chosen to maximise rank stability
  of known-good vs known-degenerate rewards, then **frozen and recorded in `config/inference.yaml`
  with an ADR before the first LLM call.**

Fitness is reported to the LLM in reflection but is never differentiated through, never shaped, and never
available to the agent during training (Eureka's fitness/reward separation, made out-of-sample because
finance has no ground-truth oracle).

## 4. Search and compute budgets (these numbers ARE the DSR trial count)

| Quantity | Value | Anchor |
|---|---|---|
| Generations (iterations) N | **5** | Eureka (Ma et al., 2024) |
| Candidates per generation K | **16** | Eureka |
| Independent restarts R | **3** | Eureka used 5; 3 chosen for the June–August compute window (ADR-004) |
| Arms at matched budget | LLM-distributional, LLM-scalar, LLM single-shot (80 one-shot samples), random reward search (240), BayesOpt-TPE over the parameterised reward family (240) | H2/H3/H4 |
| Algorithms | SAC, PPO, TD3 (SB3); IQN-SAC (d3rlpy 2.8.1, ADR-003) | fixed hyperparameters from `config/` |
| Seeds | **5** per headline cell; **3** per ablation cell; seed list [0,1,2,3,4] | no single-seed claims |

**Trial-count rule:** the DSR's N = *every candidate evaluated on validation fitness across all arms and
restarts*, maintained programmatically by `stats_inference.TrialLedger`. Nothing evaluated is excluded.

## 5. Data design

- **Universe:** 30 US large-caps under **point-in-time S&P 500 membership**: Refinitiv
  `TR.IndexConstituentRIC` (≥2016) + Datastream monthly lists `LS&PCOMP MMYY` (2005–2016). Selection rule:
  top-30 by market cap among members as of each training-window start; constituents leaving mid-window are
  **liquidated at last traded price net of cost** (no silent disappearance).
- **Series:** daily total returns (Datastream `RI` / Refinitiv total-return); Shumway delisting corrections
  (−30% NYSE/AMEX; −55% Nasdaq) where terminal returns are missing; Ince–Porter screens (prior price ≥ $1;
  returns > 300% reversing within one month → missing).
- **Auxiliary:** FRED {VIXCLS, DGS3MO, DGS10, T10Y2Y}; Fama-French daily factors (attribution only).
- **Costs:** proportional, grid **{0, 5, 10, 20, 50} bps** (0 on cash); headline tables at **10 bps**;
  one-way turnover = ½·Σ|Δw|. DeMiguel et al. (2009) 50 bps is the stress column.
- **Immutability:** all pulls frozen as CSV snapshots with SHA-256 manifest (`data/manifest/checksums.txt`).

## 6. Splits, leakage controls, and regimes

- **Development split (the ONLY data the reward search ever sees):** train **2005-01-01 → 2014-12-31**,
  validation **2015-01-01 → 2017-12-31**. All candidate generation, reflection, and selection happen here.
- **Evaluation (frozen winners only):** walk-forward over **2018 → 2025**: train 5y / test 1y, stepping 1y
  (8 test years), agents retrained per window with the *frozen* reward code; plus CPCV
  (S = 16 blocks, purged) on the same span as the overfitting-control view.
- **Embargo:** **21 trading days** at every split boundary (López de Prado, 2018).
- **Regimes:** 3-state Gaussian HMM on daily index returns, **fit on the training window only**,
  **filtered probabilities**, **shift(1)** before any use; regime-stratified results reported for
  bull/bear/high-vol states; 2008-type stress assessed via the development window's GFC years
  (a deliberate design choice: the search must see a crisis, or evolved rewards are untested against one).
- The 2008 GFC inside the development window and COVID-2020/2022-bear inside evaluation windows give
  both phases at least one crisis regime.

## 7. Inference rules (locked)

1. **Deflated Sharpe Ratio** (Bailey & López de Prado, 2014) for the selected reward: unannualised inputs,
   N and V[SR] from the TrialLedger; report DSR alongside raw Sharpe in every headline table.
2. **PBO via CSCV** (S = 16) over the full candidate PnL matrix; report PBO and the λ-distribution plot.
3. **Head-to-head Sharpe differences:** Ledoit–Wolf (2008) studentised circular block bootstrap
   (block 5, 4,999 resamples).
4. **Multiplicity:** Benjamini–Hochberg FDR at q = 0.05 across the pre-registered comparison suite
   (H1–H4 × {10 bps} × headline algorithm set).
5. **Effect reporting:** point estimates with bootstrap 95% CIs; no claim language ("outperforms") for
   comparisons that fail 1–4.
6. **MinTRL** reported for the selected strategy.

## 8. Exclusions (binding scope lock)

News/NLP sentiment; multi-agent LLM committees; transformer/GNN/Mamba encoders; additional asset classes;
Decision Transformers; LLM fine-tuning; intraday/LOB data; market-impact models; additional DRL algorithms;
live paper trading. (Reasoning: confound the reward-design question or destroy the budget; full table in
`docs/` strategy notes and CLAUDE.md R2.)

## 9. Deviation protocol

Any post-freeze change → ADR with: date, what changed, why, what analyses were already run at the time
(to bound garden-of-forking-paths exposure), supervisor informed (date), dissertation disclosure sentence
drafted in the ADR itself.

## 10. Sign-off

| Field | Value |
|---|---|
| Author | Tamer Atesyakar |
| Supervisor informed of design | ⟨date⟩ |
| Freeze commit hash | ⟨paste after `make freeze-design`⟩ |
| λ (fitness penalty) frozen value | ⟨set by §3 procedure, with ADR number⟩ |
