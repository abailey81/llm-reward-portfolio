# PAPER_DEEPDIVE_TABLE

One row per paper (195 deep-dives). `impl` = implementability class as labelled;
`rel` = relevance. `key_technique` truncated.

| file | rel | impl | key_technique (truncated) |
|---|---|---|---|
| Eureka__2310.12931 | HIGH | RELATED-WORK | LLM authors white-box reward CODE exposing components as a dict, improved via reward-reflection (credit-assigned editing). |
| IQN__1806.06923 | MED | RELATED-WORK | Risk via reweighting return quantiles with distortion measures (CVaR=τ~U([0,β])). |
| AED__2503.20804 | MED | RELATED-WORK | Learned preference reward model auto-gates LLM reward code (zero low-scoring trajectories). |
| ARM-FM__2510.14176 | MED | RELATED-WORK | Generator+critic FM loop emitting executable reward-spec (automaton labeling) code. |
| Auto-MC-Reward__2312.09238 | HIGH | RELATED-WORK | Fixed-sign scale constraint: LLM chooses only signs of preset dense/sparse magnitudes. |
| BusHolding-Reward__2410.10212 | MED | RELATED-WORK | Reward-refiner acceptance gate: promote LLM reward only if it beats prior TEST perf. |
| CARD__2410.14660 | MED | RELATED-WORK | Trajectory Preference Evaluation (order-preserving check) gates RL re-training. |
| CoopMARL-Incentive-Reward__2603.24324 | MED | RELATED-WORK | Validity-envelope gate on reward programs + selection on the TRUE sparse return. |
| DrEureka__2406.01967 | MED | RELATED-WORK | Prompt "safety instruction": LLM writes its own stability/smoothness terms. |
| Driving-Reward-LLM__2405.04135 | MED | RELATED-WORK | Reward-component ablation (each term singly/combined) to attribute behavior. |
| ICPL__2410.17233 | MED | RELATED-WORK | Per-component reward traces + LLM-computed diffs fed back as structured feedback. |
| LEARN-Opt__2511.19355 | HIGH | RELATED-WORK | Autonomous LLM-generated fitness metrics + best-of-N (high-variance) acceptance. |
| LERO__2503.21807 | LOW | RELATED-WORK | Reward as convex local/global combo R=λR_local+(1-λ)R_global (MARL). |
| LLM-Augmented-Observations__2510.08779 | LOW | RELATED-WORK | Inject LLM hints as extra observation channel (value+availability), not reward. |
| LMGT__2409.04744 | LOW | RELATED-WORK | LLM-as-online-reward-scorer: per-step +1/0/-1 shift into replay buffer. |
| Language-to-Rewards__2306.08647 | MED | RELATED-WORK | Two-stage Motion-Descriptor→Reward-Coder reward authoring. |
| MultiObj-Reward-Searcher__2409.02428 | MED | RELATED-WORK | Per-requirement reward components, each unit-tested+repaired by a Reward Critic. |
| Platoon-Reward__2504.19480 | MED | FUTURE-WORK | Convergence-aware multi-criterion fitness filter (disqualify non-converged runs). |
| REvolve__2406.01309 | HIGH | FUTURE-WORK | Population reward evolution: LLM as genetic operator + island migration. |
| STRIDE__2502.04692 | MED | RELATED-WORK | Env-as-context template-free reward-code gen + reflection from training deficits. |
| Text2Reward__2309.11489 | HIGH | RELATED-WORK | Execution-feedback self-repair loop for generated reward code. |
| Text2Touch__2509.07445 | MED | RELATED-WORK | Typed full-variable reward signature + scalable bonus/penalty exposed to LLM. |
| URDP__2507.02256 | MED | FUTURE-WORK | Self-consistency uncertainty screening of reward components (sim-free prune). |
| Decision-Language-Model__2402.14807 | HIGH | RELATED-WORK | Reflection on outcome DISTRIBUTIONS (not scalar fitness) to pick reward code. |
| Qu-Fraud-RewardEvolution__2509.18719 | MED | RELATED-WORK | Self-reflection-on-failure in reward-evolution + embedded domain metric defs. |
| Adaptive-Alpha-Weighting-PPO__2509.01393 | MED | RELATED-WORK | Vol-targeting position scaling + regime-aware risk penalty in reward. |
| Darmanin-Vella__2508.02366 | LOW | RELATED-WORK | Inject single LLM scalar (dir×entropy-confidence) into observation space. |
| FinRL-DAPO__2505.06408 | LOW | RELATED-WORK | Exponent-weighted (sent^α/risk^β) reward + dose-response sweep. |
| FinRL-DeepSeek__2502.07393 | MED | RELATED-WORK | LLM risk score multiplicatively rescales returns in CVaR-PPO. |
| FinRLlama__2502.01992 | LOW | RELATED-WORK | RL-from-Market-Feedback: confidence-scaled reward vs realised forward return. |
| News-Driven-LLM-RL-Portfolio__2411.11059 | LOW | RELATED-WORK | LLM sentiment-vs-price alignment bonus (vol-downweighted) in reward code. |
| ATLAS__2510.15949 | LOW | RELATED-WORK | Adaptive-OPRO: rolling-window scalar scoring + template separation for prompt opt. |
| Agentic-Trading-Survey__2605.19337 | LOW | RELATED-WORK | MR-1..MR-7 reporting checklist + R0–R3 reproducibility tiering. |
| Alpha-Mining-MCTS__2505.11122 | LOW | RELATED-WORK | MCTS over alpha-formula trees + Frequent-Subtree-Avoidance diversity regulariser. |
| Alpha-R1__2512.23515 | LOW | RELATED-WORK | Semantic gating: LLM activates/deactivates factors by NL profile vs market state. |
| AlphaQuanter__2510.14264 | LOW | RELATED-WORK | Asymmetric risk-aware discrete reward on EW multi-horizon forward return. |
| AlphaSharpe__2502.00029 | MED | IMPLEMENT-NOW | AS1–AS4 closed-form higher-moment/downside/regime risk-adjusted metrics. |
| CogAlpha__2511.18850 | MED | RELATED-WORK | Multi-agent quality checker: repair + leakage unit-test gate on LLM finance code. |
| Expert-Investment-Team__2602.23330 | LOW | RELATED-WORK | Fine-grained task decomposition (precomputed features in prompt) for multi-agent. |
| Janus-Q__2602.19919 | MED | RELATED-WORK | Hierarchical-gated reward: hard/soft gates compose objectives multiplicatively. |
| Macro-Economist-Agent__2606.08283 | MED | RELATED-WORK | Held-fixed interpretation-layer ablation + paired stationary block bootstrap. |
| MadEvolve__2605.23007 | MED | RELATED-WORK | IS-OOS degradation vs Bailey multiple-testing discount (overfitting check). |
| QuantEvolve__2510.18569 | LOW | RELATED-WORK | MAP-Elites QD archive over evolved strategy programs (risk-profile axes). |
| QuantaAlpha__2602.07085 | MED | FUTURE-WORK | Trajectory-level mutation (rewrite failure segment) + AST-redundancy scoring. |
| SHARP__2605.06822 | MED | RELATED-WORK | Tail-day structural credit assignment (worst Kattr P&L days → rule IDs). |
| Trade-R1__2601.03948 | MED | RELATED-WORK | Asymmetric reward gating: sign-dependent dampening of noisy returns. |
| Trading-R1__2509.11420 | LOW | RELATED-WORK | Vol-driven multi-horizon return discretization for 5-tier labels. |
| TradingGroup__2508.17565 | LOW | RELATED-WORK | Auto per-action reward = excess return − cost penalty (filter for PEFT). |
| Beyond-CVaR-Spectral__2501.02087 | MED | RELATED-WORK | Spectral risk = weighted sum of CVaRs at multiple levels (+ expectation weight). |
| Coache-Jaimungal-DynamicRisk__2112.13414 | MED | FUTURE-WORK | Time-consistent recursively-nested per-step CVaR (+entropy penalty). |
| CoacheJaimungal-RobustDistortionRiskRL__2024 | MED | RELATED-WORK | Wasserstein robustness = analytic shift of the cost-to-go quantile. |
| Composite-Risk-Reward__2506.04358 | MED | RELATED-WORK | Linearly-weighted multi-term reward (return−downside+diff-return+Treynor). |
| NatGas-Distributional-RL__2501.04421 | MED | RELATED-WORK | CVaR α as continuous risk dial + behavioural dose-response. |
| Quantile-Targeted-Portfolio__2510.19271 | HIGH | IMPLEMENT-NOW | Tail-Adjusted Sharpe (Sharpe/\|CVaR95\|, Cornish–Fisher mVaR95). |
| RAMAC__2510.02695 | MED | RELATED-WORK | BC regularization on diffusion/flow actor with CVaR-through-path gradient. |
| Sharpe-Regret-Reward__2502.02619 | MED | RELATED-WORK | Negative-Sharpe-regret reward vs forward-looking Oracle (train-only). |
| Tail-Safe__2510.04555 | MED | RELATED-WORK | PID Tail-Coverage Controller: temperature-tilted quantile sampling for CVaR. |
| DAR__2605.20740 | MED | RELATED-WORK | CRPS proper scoring rule + leave-one-out marginal credit (accuracy+dispersion). |
| DFPO__2602.05890 | MED | RELATED-WORK | Critic return distribution as neural-ODE flow + CVaR tail-shape regularization. |
| DPRM__2402.09764 | MED | RELATED-WORK | Distributional preference reward + Optimal-Transport (Wasserstein) loss. |
| DVPO__2512.03847 | MED | RELATED-WORK | Asymmetric tail-shaping: contract lower tail, expand upper tail of quantile dist. |
| Distribution-Alignment-Judge__2505.12301 | LOW | RELATED-WORK | KL+CE objective with adversarial worst-case distribution perturbation. |
| Distributional-Reasoning__2603.24844 | LOW | NOT-RELEVANT | Brier/proper-scoring-rule reward for calibrated multi-answer sets (LLM policy). |
| Q-Sharp__2502.20548 | LOW | RELATED-WORK | Learn reward-to-go distribution by MLE; value=β·ln E[exp(Z/β)] (entropic tilt). |
| QRM__2409.10164 | MED | RELATED-WORK | Concave exponential/entropic utility over reward distribution (raise left tail). |
| RAPO__2602.04224 | LOW | NOT-RELEVANT | Complexity-matched reward granularity (safe-reasoning depth ∝ attack complexity). |
| RARL-Pan-Liang-Lin__2602.09305 | LOW | RELATED-WORK | Outcome-vs-process reward-semantics taxonomy + reward-hacking framing (survey). |
| Retrospective-ICL-Credit__2602.17497 | LOW | RELATED-WORK | Advantage from log-prob ratio of LLM policy before/after in-context reflection. |
| Risk-Averse-Finetuning__2501.06911 | HIGH | RELATED-WORK | CVaR via batch-level worst-return-episode subsampling + soft-risk schedule. |
| RiskPO__2510.00911 | MED | RELATED-WORK | Mixed VaR (MVaR): weighted multi-region tail objective, lower-tail up-weighted. |
| DatedGPT__2603.11838 | LOW | RELATED-WORK | Crawl-date temporal partitioning + perplexity-reversal leakage probe. |
| Explicit-Bias-Consideration__2602.14233 | MED | RELATED-WORK | Structural Validity Checklist (temporal/survivorship/cost/calibration gates). |
| Look-Ahead-Bench__2601.13770 | LOW | RELATED-WORK | Alpha-decay across return-matched in-window vs post-cutoff regimes. |
| Look-Ahead-Bias-Fixes__2512.06607 | LOW | NOT-RELEVANT | Divergence decoding: logit-diff of forget/retain small models to enforce cutoff. |
| Look-Ahead-Test__2512.23847 | MED | RELATED-WORK | MIN-K% PROB memorization proxy + prediction×memorization interaction test. |
| MemGuard-Alpha__2603.26797 | LOW | RELATED-WORK | Cross-Model Memorization Disagreement (differing cutoffs as natural experiment). |
| ProfitMirage-LLMAgentLeakage__2025 | MED | RELATED-WORK | Counterfactual-perturbation leakage probing (invariance = memorization). |
| Temporal-Contamination-Detector__2602.17234 | LOW | RELATED-WORK | Shapley-DCLR: influence-weighted contamination ("leaks that move prediction"). |
| C51-Distributional-Perspective__1707.06887 | MED | RELATED-WORK | Categorical return distribution on fixed support + projected Bellman (KL loss). |
| CQL__2006.04779 | MED | RELATED-WORK | Conservative critic regularizer (gap-expanding lower-bound Q) for offline RL. |
| Deep-Hedging-Buehler__1802.03042 | HIGH | RELATED-WORK | Optimize policy directly vs convex risk (CVaR via OCE), α as risk dial. |
| DeepRL-Portfolio-EIIE__1706.10059 | MED | RELATED-WORK | Explicit log-return reward with recursive transaction-cost remainder factor. |
| PPO__1707.06347 | LOW | RELATED-WORK | Clipped probability-ratio surrogate (pessimistic lower bound) policy gradient. |
| SAC__1801.01290 | HIGH | RELATED-WORK | Reward magnitude = inverse entropy temperature (exploration/exploitation knob). |
| TD3__1802.09477 | MED | RELATED-WORK | Clipped Double Q-learning (min of twin target critics) curbs overestimation. |
| rliable__2108.13264 | HIGH | IMPLEMENT-NOW | IQM + stratified-bootstrap CIs + performance profiles for few-seed RL. |
| Acerbi-Spectral__2002 | MED | FUTURE-WORK | Spectral risk = decreasing-weight spectrum over tail quantiles; weighted order stats. |
| AcerbiTasche-ES__2002 | HIGH | IMPLEMENT-NOW | Coherent ES estimator = mean of floor(nα) worst order statistics. |
| AhmadiJavid-EVaR__2012 | MED | FUTURE-WORK | EVaR = inf_z z⁻¹ln(M_X(z)/α); coherent MGF/entropy upper bound on CVaR. |
| Artzner-Coherent__1999 | HIGH | RELATED-WORK | Four coherence axioms; subadditivity disqualifies VaR, justifies CVaR/ES. |
| Bailey-DSR__2014 | HIGH | IMPLEMENT-NOW | Deflate SR vs EVT expected-max-SR over N (effective) trials. |
| Bailey-PBO__2017 | HIGH | RELATED-WORK | CSCV: model-free PBO via balanced train/test row-splits (logit distribution). |
| Batra-Review__2025 | MED | RELATED-WORK | Four-function (simulate/act/analyse/advise) LLM-agent-finance taxonomy. |
| BlackLitterman__1992 | LOW | RELATED-WORK | Reverse-optimize market weights to equilibrium prior + Bayesian view blend. |
| CarteaCoacheJaimungal__2022 | HIGH | FUTURE-WORK | Strictly consistent joint (VaR,CVaR) scoring (no nested simulation). |
| CheriditoStadje-TimeConsistency__2009 | MED | RELATED-WORK | Recursive backward composition of one-period CVaR = time-consistent dynamic risk. |
| DSAC__2020 | MED | RELATED-WORK | Gaussian return-distribution critic; variance adaptively rescales updates. |
| DeMiguel-1overN__2009 | HIGH | IMPLEMENT-NOW | 1/N as the parameter-free severity benchmark optimized rules must beat OOS. |
| EX-DRL__2024 | MED | RELATED-WORK | Augment scarce tail samples with GPD (POT-EVT) synthetic draws (0<ξ<1). |
| FinRL-Meta__2022 | MED | RELATED-WORK | DataOps pipeline → gym envs with anti-leakage handling + frictions. |
| FinRL__2020 | MED | RELATED-WORK | Swappable reward modules (value-Δ/log-return/Sharpe) + turbulence gate. |
| FollmerSchied-Convex__2002 | MED | RELATED-WORK | Convex risk measure dual: sup_Q{E_Q[−X]−α(Q)} (penalty representation). |
| Hajrullahu-Thesis__2025 | LOW | NOT-RELEVANT | Intrinsic reward from hidden-state velocity/curvature (GRPO LLM training). |
| Hartley-RiskAttitudes__2025 | LOW | RELATED-WORK | CPT-parameter estimation from LLM-elicited certainty equivalents (Okhrati co-author). |
| HarveyLiuZhu-CrossSection__2016 | MED | IMPLEMENT-NOW | Holm (FWER) + BHY (FDR, arbitrary dependence) multiplicity adjustment. |
| Khraishi-Okhrati__2022 | MED | RELATED-WORK | CQL "value of conservatism" α-sweep (OOD overestimation fix) — Okhrati. |
| Kusuoka-LawInvariant__2001 | MED | RELATED-WORK | Kusuoka rep: every law-invariant coherent risk = mixture of CVaR levels. |
| LedoitWolf-SharpeTest__2008 | HIGH | IMPLEMENT-NOW | Studentized circular-block-bootstrap test for Sharpe-ratio DIFFERENCE. |
| LedoitWolf-Shrinkage__2004 | LOW | RELATED-WORK | Optimal linear covariance shrinkage to constant-correlation target. |
| LopezDePrado-HRP__2016 | MED | IMPLEMENT-NOW | Hierarchical clustering + recursive inverse-variance bisection allocator. |
| Maillard-RiskParity__2010 | LOW | RELATED-WORK | ES Euler additive risk-contribution decomposition (ERC, non-parametric). |
| Markowitz-PortfolioSelection__1952 | MED | RELATED-WORK | Mean-variance efficient frontier (variance/covariance risk). |
| MoodySaffell-DirectRL__2001 | MED | RELATED-WORK | Differential Sharpe / downside-deviation ratio (online recursive reward). |
| PolitisRomano-StationaryBootstrap__1994 | HIGH | IMPLEMENT-NOW | Geometric-random-length circular block resampling for dependent series. |
| QR-DQN__2017 | MED | RELATED-WORK | Quantile-regression (pinball/Huber) loss to estimate return quantiles. |
| RockafellarUryasev-CVaR__2000 | HIGH | RELATED-WORK | Auxiliary fn ζ+(1−α)⁻¹E[(loss−ζ)₊] → LP-tractable CVaR (+VaR as minimizer). |
| Sood-DiffSharpe__2023 | MED | RELATED-WORK | Differential Sharpe ratio as per-step online risk-adjusted reward. |
| White-RealityCheck__2000 | MED | FUTURE-WORK | Stationary-bootstrap max relative-performance for data-snooping p-value. |
| AlphaGPT__2023 | LOW | RELATED-WORK | Closed-loop generate-alpha-code → backtest → NL critique → regenerate (RAG). |
| ELfolio__2025 | MED | RELATED-WORK | CoT reasoning traces as accumulating evolutionary memory (strategy-code evo). |
| FINCON__2024 | MED | RELATED-WORK | CVaR within-episode tail alert + conceptual verbal reinforcement (multi-agent). |
| FinAgent__2024 | LOW | RELATED-WORK | Dual-level reflection auditing decisions vs realized trading curve (LLM agent). |
| FinMem__2023 | LOW | NOT-RELEVANT | Layered long-term memory with per-layer time-decay salience (LLM trader). |
| Hansen-SPA__2005 | HIGH | FUTURE-WORK | Studentized, loglog-thresholded bootstrap SPA test (1 benchmark vs many). |
| LopezLira-ChatGPT__2023 | LOW | RELATED-WORK | LLM financial reasoning as sophistication-thresholded emergent ability. |
| Motif__2023 | MED | RELATED-WORK | LLM preferences over caption pairs → Bradley-Terry intrinsic reward ("evaluate"). |
| ONI__2024 | MED | RELATED-WORK | Online intrinsic-reward learning from streaming LLM feedback on own data. |
| QuantAgent__2024 | MED | RELATED-WORK | Writer/judge inner loop + outer backtest feedback to a code-signal KB. |
| RD-Agent__2025 | MED | RELATED-WORK | Linear-Thompson-sampling bandit scheduling research directions (multi-agent). |
| Stock-Evol-Instruct__2024 | LOW | RELATED-WORK | LLM-as-Judge threshold-filtering of LLM-authored instructions. |
| TradingAgents__2024 | LOW | RELATED-WORK | 3-perspective risk-management debate layer (risky/neutral/safe). |
| AVaR-MDP-Bauerle__2011 | MED | RELATED-WORK | State-augmentation (carry VaR threshold s) → Bellman recursion for CVaR. |
| Bauer-TailRiskForecastEPA__2025 | MED | RELATED-WORK | DM/MCS EPA tests low-power at extreme quantiles; need joint VaR-ES (FZG). |
| BayerDimitriadis-RegressionESBacktest__2022 | MED | FUTURE-WORK | Strict forecast-only ES backtest via joint VaR-ES MZ regression. |
| BayesOpt-Snoek__2012 | MED | RELATED-WORK | Fully-Bayesian GP-EI (slice-sampled kernel, ARD Matern 5/2) — the search optimizer. |
| BayesOptReview-Shahriari__2016 | MED | RELATED-WORK | GP-surrogate + EI/UCB Bayesian optimization (already the GP-EI search leg). |
| BiasCorrectedPOT-CVaR-Troop__2021 | MED | FUTURE-WORK | Bias-corrected POT/GPD CVaR at extreme tails with confidence intervals. |
| CVaR-MDP-Chow__2014 | HIGH | RELATED-WORK | R-U variational CVaR + state-augmentation + VaR-auxiliary on its own timescale. |
| CVaR-Robust-Chow__2015 | MED | RELATED-WORK | CVaR = expected cost under worst-case model perturbation (robustness duality). |
| CVaR-Sampling-Tamar__2015 | LOW | RELATED-WORK | CVaR likelihood-ratio gradient over worst-α trajectories (VaR baseline). |
| ConcreteProblems-Amodei__2016 | MED | RELATED-WORK | Reward-hacking/Goodhart framing + defenses catalog. |
| DeepRLThatMatters-Henderson__2018 | HIGH | RELATED-WORK | Multi-seed bootstrap CIs + significance tests over single/top-N reporting. |
| ELM-Lehman__2022 | MED | RELATED-WORK | Code LLM as semantic mutation operator inside QD (MAP-Elites) loop. |
| FisslerZiegel-HigherOrderElicitability__2016 | MED | FUTURE-WORK | (VaR,ES) jointly 2-elicitable → closed-form joint consistent scoring. |
| FunSearch-RomeraParedes__2024 | HIGH | FUTURE-WORK | Program-skeleton + isolated-function evolution scored by deterministic evaluator. |
| LopezDePrado_10ReasonsMLFundsFail__2018 | MED | RELATED-WORK | DSR/PSR multiplicity- & non-normality-aware significance for selected strategy. |
| LopezDePrado_AFML_Chapter1__2018 | MED | RELATED-WORK | Backtest overfitting as central enemy: deflate SR + purge/embargo/CPCV. |
| NoldeZiegel-ElicitabilityBacktesting__2017 | HIGH | IMPLEMENT-NOW | DM comparative backtest on strictly-consistent joint (VaR,ES) score. |
| OPRO-Yang__2024 | MED | RELATED-WORK | Optimization-trajectory meta-prompt (sorted scored history) as LLM optimizer. |
| RewardHacking-Skalse__2022 | MED | RELATED-WORK | Proxy-vs-true (un)hackability framework; narrowing rarely removes hacking. |
| RewardMisspecification-Pan__2022 | MED | RELATED-WORK | Detect hacking via JSD/Hellinger action-dist divergence from trusted policy. |
| RewardShaping-Ng__1999 | MED | RELATED-WORK | Potential-based shaping (γΦ(s')−Φ(s)) is the only policy-invariant reward add. |
| RiskSensitiveRL-Prashanth__2018 | MED | RELATED-WORK | Lagrangian-constrained MDP (risk constraint) + two-timescale updates. |
| AIFeynman-Udrescu__2020 | LOW | RELATED-WORK | NN surrogate tests symmetry/separability to decompose symbolic regression. |
| ApprenticeshipLearning-Abbeel__2004 | MED | RELATED-WORK | Feature-expectation matching guarantees near-expert value (IRL). |
| AutoMLZero-Real__2020 | MED | RELATED-WORK | Evolve algorithm code from minimal ops + knock-out/knock-in motif analysis. |
| BenjaminiHochberg-FDR__1995 | HIGH | IMPLEMENT-NOW | Linear step-up FDR procedure (P(i)≤(i/m)q*). |
| BloombergGPT-Wu__2023 | LOW | RELATED-WORK | Mixed-corpus (~50% in-domain) domain-specialization pretraining. |
| CategoricalDRL-Rowland__2018 | MED | RELATED-WORK | Cramér-distance characterization of the categorical projection. |
| DeepRLHumanPreferences-Christiano__2017 | MED | RELATED-WORK | Learn reward from human pairwise preferences (Bradley-Terry), online. |
| DeepSymbolicRegression-Petersen__2021 | MED | RELATED-WORK | Risk-SEEKING policy gradient (top-ε quantile) — dual of CVaR. |
| EvaluatingTradingStrategies-Harvey__2014 | MED | RELATED-WORK | Multiple-testing Sharpe-ratio haircut (Bonferroni/Holm/BHY → deflated SR). |
| EvolvedPolicyGradients-Houthooft__2018 | MED | RELATED-WORK | Meta-optimize the loss/objective for FINAL trained-policy return (ES). |
| EvolvingRLAlgorithms-CoReyes__2021 | MED | RELATED-WORK | Search the loss as a typed computational graph (evolution) → DQNReg. |
| FQF-Yang__2019 | LOW | RELATED-WORK | Self-adjusting quantile fractions minimizing 1-Wasserstein (closed-form grad). |
| FinBERT-Araci__2019 | LOW | NOT-RELEVANT | Domain-adaptive further pretraining + anti-forgetting fine-tune schedules. |
| FinGPT-Yang__2023 | LOW | RELATED-WORK | Market-derived self-labeling (price reaction as free supervisory signal). |
| GP-RewardSearch-Niekum__2010 | MED | RELATED-WORK | Outer GP search over reward-code ADJUSTMENT to a fitness-based base reward. |
| IMRL-Evolutionary-Singh__2010 | HIGH | RELATED-WORK | Evolutionary search over reward functions; fitness ≠ reward (ORP). |
| IRL-NgRussell__2000 | LOW | RELATED-WORK | Margin-maximizing LP selecting simplest reward consistent with optimal behavior. |
| InternalRewards-Sorg__2010 | HIGH | RELATED-WORK | ORP: designed internal reward beats true objective for a BOUNDED agent. |
| InverseRewardDesign-HadfieldMenell__2017 | MED | RELATED-WORK | Proxy reward = noisy OBSERVATION of true intent (valid only in design context). |
| Kyle-PriceImpact__1985 | LOW | FUTURE-WORK | Kyle's λ = closed-form linear price-impact (illiquidity) coefficient. |
| LPG-Oh__2020 | LOW | RELATED-WORK | Meta-learn a domain-invariant RL update rule (population meta-gradient). |
| LossFunctionSearch-Gonzalez__2019 | MED | RELATED-WORK | Search the loss function as a symbolic program (GLO, GA+CMA-ES). |
| MarketImpact-Almgren__2005 | LOW | RELATED-WORK | Vol/ADV-normalized linear-permanent + 3/5-power-law temporary impact cost. |
| MaxEntIRL-Ziebart__2008 | LOW | RELATED-WORK | Max-entropy trajectory dist matching expert feature counts (forward-backward DP). |
| MetaGenRL-Kirsch__2020 | MED | RELATED-WORK | Meta-learn the objective (low-param neural loss) via off-policy 2nd-order grads. |
| MetaGradientRL-Xu__2018 | LOW | RELATED-WORK | Online cross-validation meta-gradient to tune return meta-params (γ,λ). |
| OptimalExecution-AlmgrenChriss__2000 | LOW | RELATED-WORK | Mean-variance penalty E+λV on implementation shortfall (efficient frontier). |
| OptimalRewardProblem-Sorg__2011 | HIGH | RELATED-WORK | Designer/agent reward separation for bounded agents; PGRD online reward tuning. |
| PIXIU-Xie__2023 | LOW | NOT-RELEVANT | Assemble expert-annotated finance datasets into instruction-tuning samples. |
| ProbabilisticSharpe-Bailey__2012 | HIGH | IMPLEMENT-NOW | PSR: skew/kurtosis/length-adjusted P(SR>SR*) + MinTRL. |
| PseudoMath-Bailey__2014 | HIGH | IMPLEMENT-NOW | Minimum Backtest Length: E[max_N SR]~sqrt(2 ln N / y) overfitting threshold. |
| PySR-Cranmer__2023 | LOW | FUTURE-WORK | Evolve-simplify-optimize symbolic regression with adaptive parsimony penalty. |
| RewardDesign-OGA-Sorg__2010 | MED | RELATED-WORK | ORP via online gradient ascent (PGRD) on proxy reward params. |
| RomanoWolf-Stepwise__2005 | MED | FUTURE-WORK | Bootstrap stepdown FWE control (studentized max-stat) over many strategies. |
| ScientificOutlook-Harvey__2017 | HIGH | IMPLEMENT-NOW | SD-MBF (−e·p·ln p) Bayesianized p-value under explicit prior odds. |
| SpeculativePrices-Mandelbrot__1963 | MED | RELATED-WORK | α-stable (infinite-variance) returns; tail risk via Pareto tail index α. |
| SquareRootLaw-Toth__2011 | MED | FUTURE-WORK | Square-root market impact I(Q)=Y·σ·sqrt(Q/V) from latent order book. |
| StatisticsSamples-Rowland__2019 | LOW | RELATED-WORK | Statistics-vs-samples imputation strategy for distributional Bellman updates. |
| StylizedFacts-Cont__2001 | MED | RELATED-WORK | Stylized-facts checklist + EVT block-maxima tail-index diagnostic. |
| SurvivorshipBias-Brown__1992 | MED | RELATED-WORK | Survivorship-induced spurious persistence (survival ∝ total-risk perf). |
| TradingCosts-Frazzini__2018 | MED | FUTURE-WORK | Concave square-root market-impact cost calibrated to real fills. |
| WhereRewardsComeFrom-Singh__2009 | HIGH | RELATED-WORK | ORP: fitness-maximizing reward need not equal fitness (designed proxy beats it). |
