# Literature Integration Map

Built first-hand from the 196-paper corpus extraction (13 clusters) cross-checked against
`paper/refs.bib` (57 entries, as of 2026-06-28). Citation presence is matched LOOSELY by author
surname + year against the `@type{key}` lines in `refs.bib`. Where a match is plausible but the
`refs.bib` coordinates carry a `% VERIFY` flag, the master table still treats the paper as "cited"
but it is listed under Integrity Flags. Anything I could not confirm is marked **verify**.

---

## 1. Master table — by dissertation section -> paper -> one-line leverage note

### RelatedWork

| Paper (year) | Cited? | One-line leverage note |
|---|---|---|
| AED (2025) | NO | Recent LLM-writes-reward-code outside finance; widens the lineage, reinforces empty-novelty-cell. |
| ARM-FM (2026) | NO | Contrast: constrains LLM to a verifiable automaton; motivates our sandbox/validity-envelope. |
| Auto MC-Reward (2024) | NO | Direct precedent for Designer/Critic/reflect triad; reflect-on-best is established practice not novelty. |
| BusHolding-Reward (2025) | NO | Nearest non-finance economic-control analogue; "filter ineffective rewards" parallels our fitness selection. |
| CoopMARL-Incentive (2026) | NO | Structurally closest: sandbox + fixed-budget + selection-on-fitness (MAPPO/Overcooked). |
| Driving-Reward-LLM (Zhou 2024) | NO | (also Discussion) prompt design materially shapes reward behaviour -> supports prompt-variation diversity. |
| ICPL (2025) | NO | Human-preference-in-the-loop branch; contrast with our preference-free pre-registered tail feedback. |
| LERO (2025) | NO | Evolutionary LLM-reward; confounds reward+observation channels -> our channel isolation is cleaner. |
| LLM-Augmented-Observations (2025) | NO | Explicit contrast: keeps LLM OUT of reward; sharpens reward-channel-as-object-of-study. |
| LMGT (2024) | NO | Scope delineation: tunes a reward shift/bias, not free-form reward CODE. |
| Language-to-Rewards / L2R (2023) | NO | Seminal LLM-reward-as-interface anchor; template-parameter vs free-form code. |
| REvolve (2025) | NO | Human-feedback evolutionary branch; contrast with our automated preference-free design. |
| ICPL/STRIDE/Platoon/Text2Touch (2024-25) | NO | Eureka-beating + simpler-reward lineage in robotics; keeps expanding but never financial tail risk. |
| Qu Fraud RewardEvolution (2025) | YES (`qu2025selfevolving`) | Closest finance-ADJACENT reward-CODE evolution; licenses N2 wording "first for a portfolio agent". |
| Adaptive-Alpha-Weighting-PPO (2026) | NO | LLM authors SIGNAL formulas into policy, reward is plain risk-adj return; sharpens contribution boundary. |
| Darmanin-Vella (2025) | NO | LLM signal -> STATE not reward; cleanest contrast for our reward-channel claim. |
| FinRLlama (2025) | NO | Inverse setup: RL trains the LLM signal-generator; disambiguates "LLM in the loop" directions. |
| News-Driven-LLM-RL-Portfolio (2024) | NO | Human hand-writes a sentiment-into-reward term for a PORTFOLIO RL agent — exactly what we automate. |
| QuantEvolve / QuantaAlpha / CogAlpha / Alpha-Mining-MCTS / Alpha-R1 (2025-26) | NO | LLM-evolves-EXECUTABLE alpha/factor code; objective is predictive IC/return, not a tail reward for RL. |
| Trading-R1 (2025) | NO | (also Baselines) leading LLM-as-RL-policy trading; "risk-sensitive remains underexplored" motivation. |
| AlphaQuanter / TradingGroup / Alpha-R1 (2025) | NO | Hand-designed trajectory rewards / multi-agent; the human baseline our LLM replaces. |
| ATLAS (2025) | NO | PROMPT-optimization branch contrast; "more info != better in noisy regimes" supports likely-null. |
| RAMAC (2025) | NO | CVaR term added to a base loss (L_BC+eta*L_Risk) mirrors our additive tail components; eta is sensitive. |
| NatGas-Distributional-RL (2025) | NO | CVaR objective gives controllable monotone risk-aversion in REAL trading — the mechanism we exploit. |
| EX-DRL (2024) | NO | EVT (GPD tail) + distributional RL precedent; grounds the EVT component (hedging, not portfolio). |
| FinRL-DeepSeek (2025) | YES (`benhenda2025finrldeepseek`) | THE primary novelty fence; near-null results corroborate the likely-null framing. |
| Decision-Language Model (2024) | YES (`behari2024dlm`) | Closest architectural precedent; reward-code + reflection-w/o-scalar-fitness, public-health not finance. |
| DPRM / DVPO / DFPO (2024-26) | NO | Distributional-reward-MODEL / asymmetric tail shaping in LLM-RL; distribution over rewards vs over RETURNS. |
| RARL survey (2026) | NO | Taxonomy anchor + reward-hacking/contamination sections; cross-link to G_contamination. |
| FinRL / FinRL-Meta (2020/22) | NO | "Commonly-used reward functions" status quo + the three named hazards (survivorship etc.). |
| Coache-Jaimungal Robust Distortion (2025) | NO (separate from `coache2024dynamicrisk`) | Robustness axis (Wasserstein ball) + elicitability; frame robustness as out-of-scope future work. |
| Chow-Ghavamzadeh CVaR-MDP (2014) | NO | Native CVaR-in-objective/gradient; the alternative our ablation/placebo arms benchmark against in spirit. |
| CVaR-Sampling-Tamar (2015) | NO | CVaR via sampled gradients; importance-sampling-for-small-alpha motivates our EVT estimator. |
| RiskSensitiveRL-Prashanth (2018) | NO | Authoritative survey anchoring the risk-sensitive-RL related-work section. |
| Christiano DeepRLHumanPreferences (2017) | NO | Reward-learned-from-human-feedback alternative; we keep a language spec, delegate the CODE. |
| ELM / AutoML-Zero / EvolvingRLAlgorithms / EPG / MetaGenRL / LPG / MetaGradientRL / GLO (2018-22) | NO | Learned-objective / search-over-objective-code lineage; the methodological program we sit in. |
| AI-Feynman / SymbolicRegression-SchmidtLipson / PySR / DeepSymbolicRegression / AutoML-Zero (2009-23) | NO | Program-search-under-a-metric exemplars; bound novelty (search exists, LLM-author-for-risk-reward does not). |
| IRL classics: Abbeel-Ng / Ng-Russell / MaxEnt-Ziebart (2000-08) | NO | "Where reward comes from" contrast: IRL infers reward; we GENERATE reward code (forward design). |
| GP-RewardSearch-Niekum (2010) | NO | Most direct prior "search the space of reward PROGRAMS"; GP predecessor to LLM-authored reward code. |
| BloombergGPT / FinGPT / PIXIU / FinBERT (2019-23) | NO | Finance-LLM work is NLP/sentiment, NOT reward authoring — supports the novelty fence. |
| ConcreteProblems-Amodei (2016) | NO | Canonical reward-hacking-from-misspecified-objectives motivation for placebo/differential analyses. |
| FINCON / FinAgent / FinMem / TradingAgents / QuantAgent / AlphaGPT / RD-Agent / Stock-Evol-Instruct (2023-25) | NO | LLM-financial-agent landscape; risk is verbal/prompt-level, the tail-reward-CODE cell is unoccupied. |
| Motif / ONI (2023-24) | NO | LLM-derives-reward-VALUE neighbours; ONI's 2-family taxonomy locates us in the "reward CODE" family. |
| ELfolio (2025) | YES (`zeng2025elfolio`) | Scoop MANAGED 2026-07-02: venue pinned (Intelligent Computing 4:0176), scalar-Sharpe fitness = our CONTROL condition; see §5 + §6. |
| GIFT (2026) | YES (`wu2026gift`) | Freshest finance neighbour: LLM designs STATE+REWARD jointly (FSE+RRS) for PPO from a FIXED risk-rule library; diagnostics feedback, NO tail vector; fenced in CH1/CH2. See §6. |
| LLM-Judge-SAC / Al Ridhawi (2026) | PENDING (verified-pending-cite, write-time fence) | LLM-judge ensemble scores behaviour -> credit-assigned penalty ADDED to a fixed hand-written SAC reward; score-emitter, not reward-code author. See §6. |

### Methods

| Paper (year) | Cited? | One-line leverage note |
|---|---|---|
| CARD (2024) | YES (`sun2025card`) | TPE avoids full RL train per step; precedent for budget-matched search; preference (not distribution) feedback. |
| MultiObj-Reward-Searcher / ERFSL (2024) | NO | Multi-component reward composition + critic-fixes-code; how the LLM assembles return vs tail terms. |
| URDP (2025) | NO | Self-consistency filtering + BO for hyperparams; cite as related efficiency work (NOT adopted). |
| Expert-Investment-Team (2026) | NO | Leakage-controlled backtest protocol supporting PIT/purge/embargo; Zohren/Roberts authority. |
| SAC (2018) | YES (`haarnoja2018sac`) | THE fixed agent; flag reward-scale<->entropy-temperature coupling as a construct-validity confound. |
| TD3 (2018) | YES (`fujimoto2018td3`) | Twin-critic/overestimation machinery SAC inherits; grounds critic-explosion reporting. |
| QRM (2024) | NO | Eq.4 utility E[-e^{-lambda r}] is exactly the tail-emphasis the LLM reward could emit; lambda = risk knob. |
| DAR (2026) | NO | Distribution-aware (CRPS+LOO) reward measurably changes tail behaviour; concrete reward-code template. |
| QR-DQN (2017) | YES (within `dabney2018iqn` family? NO separate key) | **verify** — quantile-regression machinery; no separate refs.bib key (only IQN/C51 present). |
| DSAC (2020) | NO | Distributional critic in max-ent SAC; variance-clipping addresses the prototype critic-explosion. |
| Troop POT-CVaR (2021) | YES (`troop2021biascorrected`) | EVT estimator backbone for multi-level tail feedback (NOTE: shipped tail is plain GPD MLE; Troop = future work). |
| Temporal-Contamination-Detector (2026) | NO | Decision-critical leakage rate (Shapley); maps onto severity framing; TimeSPEC 2x2 ablation template. |
| Look-Ahead-Test / LAP (2026) | NO | Most rigorous contamination detector; cite to show awareness even if not run. |
| BayesOpt-Snoek (2012) | YES (`snoek2012bayesopt`) | Canonical GP-EI search baseline (register switched TPE->GP-EI, R29). |

### Theory

| Paper (year) | Cited? | One-line leverage note |
|---|---|---|
| IQN (2018) | YES (`dabney2018iqn`) | Distortion-risk-measure formalism for the tail objective; do NOT attribute EVT/elicitability to it. |
| Beyond-CVaR-Spectral / Moghimi-Ku (2025) | NO | SRM = integral of CVaR over a spectrum; static-vs-dynamic time-consistency for multi-level CVaR. |
| Coache-Jaimungal DynamicRisk (2022/24) | YES (`coache2024dynamicrisk`) | Time-consistent dynamic-risk formalism; examiner-ADJACENT lineage (Jaimungal is a leading author in the coherent-risk-RL area; the EXAMINER is Dr Okhrati); risk_measure.py taxonomy menu. |
| Quantile-Targeted-Portfolio (2025) | NO | Quantile-preference -> portfolio-tilt + distributional-Bellman contraction (closest to continuous-weight). |
| Tail-Safe (2025) | NO | IQN-CVaR-PPO + KL-DRO->worst-case-CVaR bound; model for the limitations chapter. |
| Distributional-Reasoning-MIT (2026) | NO | Proper-scoring-rule (Brier) reward backbone for "reward a distribution not a point". |
| Q-Sharp (2025) | NO | Variance-dependent guarantees from distributional value learning; "distributional carries more info". |
| Acerbi-Spectral (2002) | YES (`acerbi2002spectral`) | Multi-level CVaR is coherent iff the spectrum is non-increasing — license for the spectral reward. |
| Acerbi-Tasche ES (2002) | YES (`acerbi2002coherence`) | Pin ES=CVaR; warn naive TCE penalties not coherent on discrete samples (construct-validity check). |
| AhmadiJavid EVaR (2012) | NO | EVaR as an alternative coherent tail measure; future-work tractable upper bound. |
| Artzner Coherent (1999) | YES (`artzner1999coherent`) | The four coherence axioms — rubric to grade whether LLM-authored reward is coherent. |
| CarteaCoacheJaimungal (2022) | NO | **verify** — conditionally-elicitable dynamic spectral risk; closest comparator; not in refs.bib. |
| Cheridito-Stadje (2009) | NO | VaR not time-consistent; justify CVaR/ES over VaR + per-step tail dynamic-inconsistency caveat. |
| Kusuoka (2001) | YES (`kusuoka2001lawinvariant`) | Any law-invariant coherent measure is a mixture of CVaRs — underwrites multi-level CVaR. |
| Follmer-Schied Convex (2002) | NO | **unparseable** — broadens coherence to convexity; do NOT quote formulas from this copy. |
| Markowitz (1952) | NO | Origin of risk-return objective; "variance as the original risk term"; tail measures extend it. |
| RockafellarUryasev CVaR (2000) | YES (`rockafellar2000cvar`) | THE operational CVaR definition the reward approximates; gold reference for the construct-validity check. |
| Fissler-Ziegel (2016) | YES (`fissler2016higherorder`) | ES not elicitable alone but (VaR,ES) jointly is; do NOT attribute to examiner. |
| C51 (2017) | YES (`bellemare2017c51`) | Value distribution carries the tail info; motivate "distributional could help" then null via severity. |
| AVaR-MDP-Bauerle (2011) | NO | AVaR=CVaR achievable only via state augmentation -> justifies tail feedback via REWARD not native SAC. |
| CVaR-Robust-Chow (2015) | NO | CVaR=robustness duality; principled robustness reading even under likely-null. |
| FQF-Yang (2019) | NO | Quantile-function machinery for CVaR estimation; caveat we feed tail stats not a quantile critic. |
| CategoricalDRL-Rowland (2018) | NO | Distributional value learning well-founded; tail info must enter via REWARD (fixed scalar critic). |
| StatisticsSamples-Rowland (2019) | NO | Which tail statistics (quantiles/expectiles/CVaR) to feed — principled statistic-selection. |
| FisslerZiegel + Janus-Q HGRM (2016/26) | NO (Janus-Q) | Multi-objective reward modeling foil; interpretable code > opaque learned gate. |
| Mandelbrot (1963) | NO | Heavy-tailed returns justify a TAIL-aware reward over mean-variance; normal-Sharpe inference suspect. |
| Singh2009 / Sorg-ORP / InternalRewards-Sorg / IMRL-Evolutionary-Singh (2009-11) | PARTLY | Optimal-reward / bounded-agent theory backbone (see Top-20); `singh2009rewards`,`sorg2010orp` present. |
| RewardShaping-Ng (1999) | NO | Potential-based shaping theorem: classify tail terms as policy-invariant vs genuinely risk-sensitive. |

### Baselines

| Paper (year) | Cited? | One-line leverage note |
|---|---|---|
| Platoon-Reward / STRIDE (2025) | NO | Eureka-beating evidence base for H1; ~10%/250% are control-task, non-risk figures. |
| Composite-Risk-Reward (2025) | NO | Closest HUMAN-authored composite risk reward; the ideal H1 expert baseline. |
| Sharpe-Regret-Reward (2025) | NO | Hand-crafted Regret-Sharpe+oracle baseline; CAUTION: oracle look-ahead = leakage our PIT forbids. |
| Trading-R1 (2025) | NO | Leading LLM-as-RL-policy trading; they RL-train the policy, we isolate the reward channel. |
| RA-Finetuning (2025) | NO | CVaR objective beats risk-neutral in worst quantiles — exact head-to-head structure of H2. |
| BlackLitterman (1992) | NO | Classic estimation-aware allocator (optional benchmark); image scan, verify FAJ coords. |
| DeMiguel 1/N (2009) | YES (`demiguel2009naive`) | 1/N is the honest hard OOS baseline; strengthens likely-null (beating 1/N is hard). |
| LedoitWolf-Shrinkage (2004) | NO | Shrinkage inside any MVO baseline so the comparison is fair (don't strawman raw-cov MVO). |
| LopezDePrado-HRP (2016) | NO | Modern robust allocator (HRP) benchmark alongside 1/N and shrinkage-MVO. |
| Maillard-RiskParity file (2010/14) | NO | **mislabeled-file** — actually Cagna-Casuccio ERC-with-ES; can only support an ERC-ES baseline. |
| Sood-DiffSharpe (2023) | YES (`sood2023drl`) | DRL-vs-MVO template + differential-Sharpe scalar arm; venue ICAPS FinPlan not ICAIF. |
| BayesOptReview-Shahriari (2016) | NO | "Take the human out of the loop" framing; supports GP-EI baseline + black-box reward-search. |

### Reporting

| Paper (year) | Cited? | One-line leverage note |
|---|---|---|
| Macro-Economist-Agent (2026) | NO | Held-info-set-fixed comparison + block-bootstrap + candid limitations paragraph — model write-up template. |
| Bailey-DSR (2014) | YES (`bailey2014deflated`) | Report DSR not raw Sharpe, deflated by number of reward candidates searched. |
| Bailey-PBO (2017) | YES (`bailey2017pbo`) | CSCV/PBO overfitting probability over walk-forward; disclose Witzany near-zero-mean bias. |
| rliable (2021) | YES (`agarwal2021rliable`) | Per-seed/IQM/stratified-bootstrap inference; licenses "don't revert to seed-averaging". |
| HarveyLiuZhu CrossSection (2016) | NO | **verify** — multiple-testing t>3 hurdle; named in refs.bib header as to-be-promoted, no key found. |
| LedoitWolf-SharpeTest (2008) | NO | **verify** — exact heavy-tail-robust Sharpe-difference test; named in header as to-be-promoted, no key. |
| BenjaminiHochberg FDR (1995) | YES (`benjamini1995fdr`) | Cross-hypothesis multiplicity correction (R31); pair with Romano-Wolf. |
| White-RealityCheck (2000) | NO | Formal data-snooping correction for selecting best reward program from many candidates. |
| Hansen-SPA (2005) | NO | SPA vs Reality Check; tight pre-registered comparator set (irrelevant alternatives inflate correction). |
| RomanoWolf-Stepwise (2005) | NO | **verify** — FWER dependence-aware "strategies vs benchmark"; named in header to-be-promoted, no key. |
| Bauer-TailRiskForecastEPA (2025) | NO | (also Limitations) EPA tests under-powered against tail-underestimation -> non-rejection is a weak test. |
| BayerDimitriadis-RegressionESBacktest (2022) | NO | Defensible ES backtest (joint VaR-ES MZ regression); don't hand-roll the tail evaluation. |
| ProbabilisticSharpe-Bailey (2012) | NO | PSR alongside raw Sharpe given heavy tails; honest inference on the Sharpe co-primary. |
| PseudoMath-Bailey (2014) | NO | PBO + "configs-tried-inflate-Sharpe" cornerstone for pre-registration + deflated Sharpe. |
| EvaluatingTradingStrategies-Harvey (2014) | NO | Sharpe multiplicity haircut for the 7-arm comparison. |
| Politis-Romano (1994) | YES (`politis1994stationary`) | The resampling engine for all bootstrap inference; tune/disclose block length. |
| Henderson Matters (2018) | YES (`henderson2018matters`) | Warrant for per-seed rliable, multi-seed protocol, significance discipline. |

### Discussion

| Paper (year) | Cited? | One-line leverage note |
|---|---|---|
| Driving-Reward-LLM (2024) | NO | Prompt design shapes reward -> supports R38 prompt-leak fingerprint as the differentiating mechanism. |
| Trade-R1 (2026) | NO | Designed rewards on stochastic market returns invite reward HACKING — the threat our null must address. |
| SHARP (2026) | NO | Structured/auditable beats free-form under low-SNR delayed rewards; our argument for reward CODE. |
| LopezDePrado AFML Ch1 (2018) | YES (`lopezdeprado2018afml`) | Research-factory framing (strategist vs backtester); overfitting warnings for theory-guided design. |
| MemGuard-Alpha (2026) | NO | **preprint-only-coords** — signal-level contamination filtering; treat headline numbers cautiously. |
| Hartley-RiskAttitudes (2025) | YES (`hartley2025personality`) | If LLMs default risk-neutral, that confounds whether the tail reward is genuinely risk-averse. Examiner. |
| RewardMisspecification-Pan (2022) | NO | Optimizing misspecified proxy can sharply degrade true objective; caution + placebo as misspec check. |
| InverseRewardDesign-HadfieldMenell (2017) | YES (`hadfieldmenell2017ird`) | Treat LLM reward as a fallible proxy; risk-averse handling under shift = cover for severity testing. |
| LopezLira-ChatGPT (2023) | NO | LLMs encode tradeable reasoning (motivates the approach) + alpha-decays-with-adoption (tempers claims). |
| ScientificOutlook-Harvey (2017) | NO | Motivates pre-registration + minimum-Bayes-factor; a pre-registered null is the Distinction posture. |

### Limitations

| Paper (year) | Cited? | One-line leverage note |
|---|---|---|
| LEARN-Opt (2025) | NO | High-variance / average-candidate-fails / multi-run — strongest external corroboration of the likely-null. |
| DatedGPT (2026) | NO | Gold-standard-but-costly parametric-leakage fix; frame why our reward-authoring sidesteps it. |
| Look-Ahead-Bias-Fixes / Divergence Decoding (2025) | NO | Low-cost inference-time unlearning; answer "why didn't you unlearn?". |
| Bauer-TailRiskForecastEPA (2025) | NO | EPA tests under-powered against tail-underestimation at the extreme levels we care about. |
| LopezDePrado 10 Reasons ML Funds Fail (2018) | NO | **preprint-only-coords** — false-discovery-at-speed motivates deflated/overfit-aware evaluation. |

### Data

| Paper (year) | Cited? | One-line leverage note |
|---|---|---|
| Kyle-PriceImpact (1985) | NO | Origin of linear price impact (Kyle's lambda) for the transaction-cost/impact term. |
| MarketImpact-Almgren (2005) | NO | Calibrate impact-cost functional form/magnitude; note 3/5 vs 1/2 debate (vs Toth) as a limitation. |
| OptimalExecution-AlmgrenChriss (2000) | NO | Transaction-cost/impact model + risk-vs-cost trade-off (L-VaR adjacent to CVaR). |
| SquareRootLaw-Toth (2011) | NO | Square-root impact law; juxtapose with Almgren-2005 3/5 law as modeling-choice uncertainty. |
| StylizedFacts-Cont (2001) | NO | Environment-realism checks (heavy tails, vol clustering) + non-normal performance inference. |
| SurvivorshipBias-Brown (1992) | NO | Defends the survivorship-free PIT universe (953 RICs) as a deliberate design choice. |
| TradingCosts-Frazzini (2018) | NO | **preprint-only-coords** — calibrate REALISTIC (not overstated) costs; honest cost sensitivity. |

### NotRelevant (logged, excluded from leverage)
Distribution-Alignment-Judge (2025); RAPO (2026); Retrospective-ICL-Credit (2026); Hajrullahu-Thesis (2025). These are correctly out of scope and excluded from the owned-but-uncited gap.

---

## 2. OWNED-BUT-NOT-CITED (leverage gaps)

Corpus papers with `dissertation_section != NotRelevant` whose author-surname+year is ABSENT from
`refs.bib`. These are read-and-extracted but not yet wired into the bibliography. Grouped by priority.

### High priority (load-bearing or closest-neighbour / examiner-relevant)
1. **Composite-Risk-Reward (Srivastava et al. 2025)** — the ideal H1 human-authored-composite-reward baseline. **Gap.**
2. **CarteaCoacheJaimungal (2022)** — conditionally-elicitable dynamic spectral risk; closest comparator + examiner lineage (Jaimungal). **Gap.**
3. **Coache-Jaimungal Robust Distortion (2025)** — distinct paper from `coache2024dynamicrisk`; elicitability + robustness axis. **Gap (second Coache-Jaimungal entry needed).**
4. **RewardShaping-Ng (1999)** — potential-based shaping theorem; the sharp lens for the reward-program-differential / placebo distinction. **Gap (high theory value).**
5. **WhereRewardsComeFrom-Singh (2009, CogSci)** — `singh2009rewards` IS present but its `note` cites the CogSci paper as the lineage anchor; the corpus "Where Do Rewards Come From?" is covered. **Covered (verify the CogSci vs the OGA conflation in `sorg2010orp`).**
6. **InternalRewards-Sorg (2010, ICML)** and **OptimalRewardProblem-Sorg (2011 PhD)** — the ORP bounded-agent backbone; refs.bib only has `sorg2010orp` (= Reward Design via OGA). The *Internal Rewards* and the *2011 dissertation* are SEPARATE and uncited. **Gap (theory spine).**
7. **IMRL-Evolutionary-Singh (2010, IEEE TAMD)** — optimal-reward evolutionary framework; uncited. **Gap.**
8. **HarveyLiuZhu CrossSection (2016)** — t>3 multiplicity hurdle; named in refs.bib header as "to be promoted" but NO key. **Gap (reporting).**
9. **LedoitWolf-SharpeTest (2008)** — the exact Sharpe-difference test; header says to-be-promoted, NO key. **Gap (reporting, load-bearing for H2-RA).**
10. **RomanoWolf-Stepwise (2005)** — FWER stepwise; header to-be-promoted, NO key. **Gap (reporting).**
11. **White-RealityCheck (2000)** — data-snooping correction for best-of-many reward selection. **Gap (reporting).**
12. **Hansen-SPA (2005)** — SPA test; more powerful than Reality Check. **Gap (reporting).**

### Medium priority (strengthen Theory / Methods / Data)
13. Beyond-CVaR-Spectral / Moghimi-Ku (2025) — spectral SRM time-consistency. **Gap.**
14. Quantile-Targeted-Portfolio (Barunik 2025) — quantile-preference portfolio tilt. **Gap.**
15. Tail-Safe (2025) — IQN-CVaR-PPO + KL-DRO bound. **Gap.**
16. AVaR-MDP-Bauerle (2011) — state-augmentation justification for reward-channel tail. **Gap (theory).**
17. CVaR-Robust-Chow (2015) + Chow-Ghavamzadeh CVaR-MDP (2014) + CVaR-Sampling-Tamar (2015). **Gap (risk-RL).**
18. Markowitz (1952) — origin of risk-return objective. **Gap (theory canon, surprising omission).**
19. AhmadiJavid EVaR (2012) — alternative coherent tail measure. **Gap.**
20. Cheridito-Stadje (2009) — VaR time-inconsistency, CVaR justification. **Gap (theory).**
21. QR-DQN (Dabney 2017) — quantile-regression machinery (only IQN/C51 present). **Gap (methods).**
22. DSAC (2020) — distributional SAC variance-clipping vs critic-explosion. **Gap (methods).**
23. QRM (Dorka 2024) — entropic utility tail-emphasis reward form. **Gap (methods).**
24. MultiObj-Reward-Searcher / ERFSL (2024) — multi-component reward composition. **Gap (methods).**
25. ProbabilisticSharpe-Bailey (2012), PseudoMath-Bailey (2014), EvaluatingTradingStrategies-Harvey (2014) — DSR/PSR/Sharpe-haircut family; only Bailey-DSR/PBO present. **Gap (reporting).**
26. BayerDimitriadis ES backtest (2022), Bauer EPA (2025) — ES backtesting + power. **Gap (reporting/limitations).**
27. Macro-Economist-Agent (2026) — honest-stats write-up template. **Gap (reporting).**
28. Data-cost canon: Kyle (1985), Almgren (2005), Almgren-Chriss (2000), Toth (2011), Cont (2001), Brown (1992), Frazzini (2018), Mandelbrot (1963). **Gap (Data chapter — entire cluster uncited).**

### Lower priority (RelatedWork breadth / lineage)
29. LEARN-Opt (2025) — strongest likely-null corroborator (HIGH analytic value despite "lower" lineage tag). **Gap — promote.**
30. Reward-design lineage breadth: AED, ARM-FM, Auto-MC-Reward, BusHolding, CoopMARL, Driving-Reward-LLM, ICPL, LERO, LLM-Augmented-Observations, LMGT, L2R, REvolve, STRIDE, Platoon, Text2Touch, URDP, DrEureka (`ma2024dreureka` IS present). **Gaps (lineage paragraph).**
31. Signals-into-rewards breadth: FinRL-DAPO, News-Driven-LLM-RL-Portfolio, Adaptive-Alpha-Weighting, Darmanin-Vella, FinRLlama. **Gaps.**
32. Evolve-trading-code breadth: MadEvolve, QuantEvolve, QuantaAlpha, CogAlpha, Alpha-Mining-MCTS, Trade-R1, Trading-R1, Alpha-R1, AlphaQuanter, Janus-Q, SHARP, ATLAS, TradingGroup, Expert-Investment-Team, Agentic-Trading-Survey. **Gaps.**
33. Distributional-reward-for-LLMs breadth: DAR, DFPO, DPRM, DVPO, Distributional-Reasoning, Q-Sharp, RA-Finetuning, RiskPO, RARL-survey. **Gaps.**
34. Contamination breadth: Explicit-Bias-Consideration, Look-Ahead-Bench, Look-Ahead-Bias-Fixes, Look-Ahead-Test, MemGuard-Alpha, ProfitMirage, Temporal-Contamination-Detector, DatedGPT. **Gaps.**
35. RL/program-search canon: PPO (`schulman2017ppo` present), Skalse (present), FunSearch (present), OPRO (present), ELM, AutoML-Zero, EvolvingRLAlgorithms, EPG, MetaGenRL, LPG, MetaGradientRL, GLO, AI-Feynman, SchmidtLipson, PySR, DeepSymbolicRegression, IRL trio (Abbeel-Ng, Ng-Russell, MaxEnt-Ziebart), GP-RewardSearch-Niekum, ConcreteProblems-Amodei, RewardMisspecification-Pan, DeepRLHumanPreferences-Christiano. **Gaps.**
36. Finance-LLM landscape: BloombergGPT, FinGPT, PIXIU, FinBERT, FINCON, FinAgent, FinMem, TradingAgents, QuantAgent, AlphaGPT, RD-Agent, Stock-Evol-Instruct, Motif, ONI, LopezLira-ChatGPT. **Gaps.** (ELfolio REMOVED from this gap list 2026-07-02 — now cited as `zeng2025elfolio`; see §5/§6.)
37. FinRL (2020) / FinRL-Meta (2022), RAMAC, NatGas-Distributional-RL, EX-DRL, Sharpe-Regret-Reward, RA-Finetuning, RiskSensitiveRL-Prashanth, FQF, CategoricalDRL-Rowland, StatisticsSamples-Rowland, BlackLitterman, LedoitWolf-Shrinkage, LopezDePrado-HRP. **Gaps.**

**Owned-but-uncited count (section != NotRelevant, no surname+year match in refs.bib): ~150 of 196.**
The refs.bib is a deliberate Tier-1 CORE set (the file header says so); the gap is therefore *expected*
but the High/Medium items above are the ones whose ABSENCE is a genuine leverage loss for a
publication-standard chapter — especially the Data cluster (entirely uncited) and the reporting
multiplicity family (White/Hansen/Romano-Wolf/Ledoit-Wolf-Sharpe/Harvey-Liu-Zhu).

---

## 3. INTEGRITY-FLAGS list (verbatim from corpus, plus refs.bib coordinate flags)

### mislabeled-file
- **FinRLlama (2502.01992):** `mislabeled-file(content matches filename; but PDF prints a placeholder ACM DOI/ISBN that must NOT be cited as real published coordinates)`
- **Cheridito-Stadje (2009):** `mislabeled-file(filename title 'TimeConsistency' wrong; real title is 'Time-inconsistency of VaR and time-consistent alternatives' (Cheridito-Stadje, FRL 2009); content is correct)`
- **Maillard-RiskParity (2010):** `mislabeled-file(actual = Cagna & Casuccio, 'Equally-weighted Risk Contribution Portfolios: an empirical study using expected shortfall', CeRP WP 142/14 ~2014; NOT Maillard-Roncalli-Teiletche 2010)`

### unparseable
- **Follmer-Schied Convex (2002):** `unparseable` — PDF body is custom-font-garbled; do NOT quote formulas/pages; verify against the published Finance & Stochastics version.

### possible-scoop
- **ELfolio (2025):** `possible-scoop` — **MANAGED 2026-07-02**: venue pinned (Intelligent Computing vol. 4 art. 0176, DOI 10.34133/icomputing.0176, 2025-11-17), added to refs.bib as `zeng2025elfolio`, cite-and-distinguish sentences live in CH1/CH2. Residual status: nearest neighbour, no longer un-managed. See §5/§6.

### preprint-only-coords (corpus-flagged) — cite as preprint, never assert a published venue/DOI
CoopMARL-Incentive (2026); DrEureka (2024); Language-to-Rewards (2023); Qu-Fraud (2025); FinRL-DeepSeek (2025); FinRL-DAPO (2025); News-Driven-LLM-RL-Portfolio (2024); Adaptive-Alpha-Weighting (2026); Darmanin-Vella (2025); FinRLlama (2025); AlphaSharpe (2025); MadEvolve (2026); QuantEvolve (2025); QuantaAlpha (2026); CogAlpha (2025); Alpha-Mining-MCTS (2025); Trade-R1 (2026); Trading-R1 (2025); Alpha-R1 (2025); AlphaQuanter (2025); Janus-Q (2026, +placeholder ACM DOI); SHARP (2026); ATLAS (2025); TradingGroup (2025); Expert-Investment-Team (2026); Macro-Economist-Agent (2026); Agentic-Trading-Survey (2026); Coache-Jaimungal DynamicRisk (2022); Coache-Jaimungal Robust Distortion (2025, +filename/year mismatch 2024 vs v3 2025); Composite-Risk-Reward (2025); NatGas-Distributional-RL (2025); Quantile-Targeted-Portfolio (2025); RAMAC (2025); Sharpe-Regret-Reward (2025); Tail-Safe (2025); DAR (2026); DFPO (2026); DVPO (2026); Distributional-Reasoning (2026); RAPO (2026); RARL-survey (2026); Retrospective-ICL-Credit (2026); MemGuard-Alpha (2026, +no self-printed arXiv id); SAC (2018); CQL (2020); DeMiguel-1/N (2009); LedoitWolf-Shrinkage (2004); LopezDePrado-HRP (2016); AVaR-MDP-Bauerle (2011); LopezDePrado 10 Reasons (2018); RewardShaping-Ng (1999); BloombergGPT (2023); FinGPT (2023); PIXIU (2023); DeepSymbolicRegression (2021); DeepRLHumanPreferences-Christiano (2017); EvolvedPolicyGradients (2018); EvolvingRLAlgorithms (2021); InverseRewardDesign (2017); LPG-Oh (2020); LossFunctionSearch-GLO (2019); MarketImpact-Almgren (2005); MetaGenRL (2020); MetaGradientRL (2018); OptimalExecution-AlmgrenChriss (2000); OptimalRewardProblem-Sorg (2011); ProbabilisticSharpe-Bailey (2012); PseudoMath-Bailey (2014, note: published AMS coords exist); PySR (2023); RewardDesign-OGA-Sorg (2010); SquareRootLaw-Toth (2011); TradingCosts-Frazzini (2018); Stock-Evol-Instruct (2024, anonymous OpenReview).

### refs.bib internal coordinate flags (`% VERIFY` in the bib — these are CITED entries with unconfirmed published coordinates)
behari2024dlm, qu2025selfevolving, yuksel2025alphasharpe, benhenda2025finrldeepseek, kumar2020cql, coache2024dynamicrisk, rockafellar2000cvar, artzner1999coherent, acerbi2002coherence, kusuoka2001lawinvariant, nolde2017elicitability, patton2019dynamic, troop2021biascorrected, bailey2014deflated, bailey2017pbo, lopezdeprado2018afml, benjamini1995fdr, bergstra2012randomsearch, snoek2012bayesopt, sood2023drl, moody2001directrl, demiguel2009naive, buehler2019deephedging, schulman2017ppo (no venue — correct), yang2024opro, agrawal2026gepa, sun2025card, singh2009rewards, sorg2010orp, hadfieldmenell2017ird, khraishi2022offline, hartley2025personality, batra2025review, mcneilfrey2000, belziledavison2022, rubin2025preregistration, mayo2018severetesting, gelman2014forking, lakens2018tost, campbell2018cet.

### refs.bib MUST-ACQUIRE (cited key, not in corpus, second-hand only)
- **abel2021expressivity** (On the Expressivity of Markov Reward) — flagged in bib as not-on-disk; do not present as first-hand-read. **verify / acquire.**

---

## 4. TOP 20 papers to lean on MORE (section + sentence-level use)

1. **OptimalRewardProblem-Sorg (2011 PhD)** [Theory] — *uncited.* Sentence: "For a computationally bounded agent (our fixed SAC), the reward maximizing the designer's objective need not equal that objective (Sorg 2011), which formally licenses an LLM-searched risk reward as a testable object rather than a hack." Add a SEPARATE key (`sorg2011orp`) — current `sorg2010orp` is the OGA paper.
2. **InternalRewards-Sorg (2010 ICML)** [Theory] — *uncited.* Sentence: "Well-designed internal rewards demonstrably help bounded agents (Sorg, Singh & Lewis 2010); our fixed-SAC agent is exactly such a bounded learner."
3. **WhereRewardsComeFrom-Singh (2009)** [Theory] — *covered as `singh2009rewards`.* Lean MORE: "Reward is an object to be DISCOVERED via automated search (Singh, Lewis & Barto 2009) — the precise role our LLM plays — and a searched reward may or may not beat the fitness, grounding the likely-null."
4. **LEARN-Opt (2025)** [Limitations] — *uncited.* Sentence: "Automated LLM reward design is high-variance: the average candidate fails and only a multi-run search surfaces good ones (Cardenoso & Caarls 2025), independently corroborating our per-seed (not seed-averaged) inference and likely-null framing."
5. **RewardShaping-Ng (1999)** [Theory/Discussion] — *uncited.* Sentence: "Potential-based shaping is the unique additive transform preserving the optimum (Ng, Harada & Russell 1999); we use it to classify each LLM-authored tail term as policy-invariant vs genuinely optimum-changing — the sharp test separating the tail arm from the placebo."
6. **Agentic-Trading-Survey (2026)** [Limitations] — *uncited.* Sentence: "Of 19 closed-loop LLM-trading studies, only 2 report time-consistent splits, 1 a cost model, 1 survivorship handling, and NONE reach R3 reproducibility (Xia et al. 2026); our PIT/survivorship-free panel, explicit costs, walk-forward splits and freeze hash place us at the reproducible end of a field shown to be overwhelmingly R0."
7. **Composite-Risk-Reward (2025)** [Baselines] — *uncited.* Sentence: "Our H1 expert baseline is a hand-designed composite of return + downside-risk + Treynor terms with grid-searched weights (Srivastava et al. 2025) — precisely the component selection and weighting our LLM automates."
8. **CarteaCoacheJaimungal (2022)** [Theory/RelatedWork] — *uncited.* Sentence: "Risk-sensitive actor-critics optimize time-consistent dynamic spectral risk via conditionally-elicitable scores (Cartea, Coache & Jaimungal 2022); we instead hold SAC fixed and let the LLM author the reward, leaving the designed-vs-LLM-authored cell open." (Examiner lineage.)
9. **RewardMisspecification-Pan (2022)** [Discussion] — *uncited.* Sentence: "More-capable agents can achieve higher proxy but lower true reward with abrupt phase transitions (Pan, Bhatia & Steinhardt 2022); we therefore read any arm that scores well on the LLM proxy but worse on true risk-adjusted return as a misspecification signal, monitored by the placebo arm."
10. **Skalse Reward Hacking (2022)** [Theory] — *cited (`skalse2022reward`), underused.* Sentence: "Only trivial reward pairs are unhackable over all stochastic policies (Skalse et al. 2022), and narrowing a reward usually does not make it unhackable — directly informing whether adding tail terms is safe."
11. **White-RealityCheck (2000) + Hansen-SPA (2005)** [Reporting] — *uncited.* Sentence: "Selecting the best of many LLM-authored reward programs is a specification search; we report a Reality Check / SPA p-value (White 2000; Hansen 2005) so the headline 'best reward beats scalar' is data-snooping-robust, using a tight pre-registered comparator set to avoid the irrelevant-alternatives power loss Hansen documents."
12. **LedoitWolf-SharpeTest (2008)** [Reporting] — *uncited.* Sentence: "Sharpe-difference inference uses the studentized HAC/bootstrap test valid under heavy tails and autocorrelation (Ledoit & Wolf 2008), paired with the stationary bootstrap." (Load-bearing for H2-RA.)
13. **RomanoWolf-Stepwise (2005)** [Reporting] — *uncited.* Sentence: "Arm-vs-benchmark comparisons use the dependence-aware stepwise FWER procedure (Romano & Wolf 2005), more powerful than Bonferroni and matched to our 7-arms-vs-baseline design."
14. **HarveyLiuZhu (2016)** [Reporting] — *uncited.* Sentence: "Because we search many reward programs, the bar for a new 'tail-beats-scalar' claim is raised (t > 3.0; Harvey, Liu & Zhu 2016), reinforcing the deflated-Sharpe stance."
15. **Tail-Safe (2025)** [Theory] — *uncited.* Sentence: "A per-state KL bound controls worst-case CVaR (Zhang 2025, Tail-Safe), giving our multi-level tail feedback a theoretical footing while its synthetic-only limitation contrasts with our licensed real panel."
16. **Beyond-CVaR-Spectral / Moghimi-Ku (2025)** [Theory] — *uncited.* Sentence: "A spectral risk measure is a convex combination of CVaRs across levels (Moghimi & Ku 2025); our multi-level tail feedback is therefore a spectral-style preference, with the caveat that per-step CVaR shaping optimizes neither static nor dynamic risk."
17. **AVaR-MDP-Bauerle (2011)** [Theory] — *uncited.* Sentence: "A CVaR/AVaR criterion is achievable in a sequential MDP only via VaR-level state augmentation (Bauerle & Ott 2011), which is why we inject tail-sensitivity through the REWARD rather than as a native SAC objective."
18. **Macro-Economist-Agent (2026)** [Reporting] — *uncited.* Sentence: "We mirror the held-information-set-fixed comparison, block-bootstrap inference, and candid single-regime/unadjusted-multiplicity disclosure of Wang et al. (2026) as the template for honest, Distinction-grade reporting."
19. **NatGas-Distributional-RL (2025)** [RelatedWork] — *uncited.* Sentence: "A CVaR objective on a distributional critic produces controllable, monotone risk-aversion in real financial trading (Heche et al. 2025) — the dose-response mechanism our multi-level alpha feedback is meant to exploit, with their QR-DQN instability as a caution."
20. **SHARP (2026)** [Discussion] — *uncited.* Sentence: "Under low-SNR delayed P&L rewards, structured/auditable optimization beats unconstrained free-form text (Chen et al. 2026, SHARP) — the core argument for LLM-authored reward CODE over prompt tweaking, and a source for the strict walk-forward discipline."

Honourable mentions to promote: QRM (Dorka 2024, the entropic-utility reward form), DSAC (2020, critic-explosion fix), RA-Finetuning (2025, CVaR-objective-for-an-LLM-agent head-to-head), Trade-R1 (2026, reward-hacking-on-market-returns), and the entire Data cost-model cluster (Kyle/Almgren/Toth/Cont/Brown/Frazzini) which is presently 0% cited.

---

## 5. SCOOP verdict

**The novelty conjunction (N):** an LLM AUTHORS executable reward-function CODE for a FIXED off-the-shelf
RL agent (SAC), where the reflection loop is fed the realized-return **lower-tail distribution**
(multi-level EVT/CVaR), in a **portfolio-allocation** domain, evaluated as a **pre-registered,
severity-tested** comparison. The conjunction requires ALL of: (a) LLM-writes-reward-CODE, (b) fixed
agent, (c) distributional/tail FEEDBACK channel, (d) portfolio/return-distribution domain.

**Verdict: NO paper in the corpus satisfies the full conjunction. The novelty cell is intact.** The
closest threats and exactly which conjunct each one breaks:

- **DLM / Behari 2024 (`behari2024dlm`)** — has (a)+(b)+(reflection-on-a-distribution) but the distribution is the spread of POPULATION GROUPS in a public-health RMAB, not a return lower-tail, and the domain is not portfolio. **Breaks (c-as-return-tail) and (d).** Cite-and-distinguish; already in bib.
- **ELfolio 2025 (`zeng2025elfolio`) — MANAGED 2026-07-02** — LLM evolves STRATEGY/heuristic code across RL/evolutionary/DL paradigms; first-hand read (venue pinned: Intelligent Computing 4:0176) confirms the killer verbatim: selection uses "the Sharpe ratio serving as the fitness function" — a SCALAR. Its RL-path template CAN rewrite reward functions, but selection stays scalar-Sharpe; CVaR appears only in formulation background, baseline names (MinCVaR) and eval tables, NEVER as feedback to the LLM. It therefore instantiates our CONTROL condition. **Breaks (c) outright and (a-as-reward-code-under-tail-selection).** Now cited + distinguished in CH1/CH2 (fence: "selection is driven by a scalar Sharpe-ratio fitness function ... it thereby instantiates precisely the scalar-feedback control condition of our design, not its treatment").
- **GIFT 2026 (`wu2026gift`) — the freshest finance neighbour, VERIFIED + FENCED 2026-07-02** — arXiv:2606.08450 (v1 2026-06-07), LLM-guided state-reward interface for PPO portfolio RL. It DOES put the LLM in the reward channel (RRS: LLM intrinsic term + subset of a FIXED risk-rule library) but co-varies the STATE (FSE) — breaking reward-only identification — and its DGR refinement loop feeds generic rollout diagnostics (ICs, reward trend/variability, drawdown), NO CVaR/quantile/tail vector; framework-vs-baselines, no feedback-content ablation, no pre-registration; PPO not SAC. **Breaks (b), (c) and the pre-registration limb of the conjunction; (a) only partially (library-constrained, state co-varied).** Fenced in CH1 + CH2.
- **LLM-Judge-SAC / Al Ridhawi 2026 (pending cite, write-time fence)** — arXiv:2605.05739: LLM-judge ensemble scores agent BEHAVIOUR on six dimensions; deficient scores become a credit-assigned penalty ADDED to a fixed, hand-written SAC reward. The LLM is a score-EMITTER, never a reward-code author; SAC controls two hyperparameters of a stock-FORECASTING system (not portfolio allocation); no tail/CVaR anywhere. **Breaks (a), (c) and (d).**
- **FinRL-DeepSeek / Benhenda 2025 (`benhenda2025finrldeepseek`)** — risk-sensitive RL trading with LLM signals, but the CVaR-PPO reward is HAND-WRITTEN and the LLM only supplies a 0.9-1.1 scalar. **Breaks (a).** The primary novelty fence; in bib.
- **FinRL-DAPO / Qu Fraud / Composite-Risk-Reward / AlphaSharpe** — each breaks at least one conjunct: DAPO has a human-set parametric risk reward (breaks a); Qu is fraud-detection classification not portfolio (breaks c+d); AlphaSharpe outputs a static ranking metric with no RL loop (breaks a+b); Composite-Risk-Reward is hand-designed not LLM-generated (breaks a).
- **FINCON** — CVaR via VERBAL reinforcement over beliefs, no numeric reward function trained into a policy. **Breaks (a).**
- **CARD / Auto-MC-Reward / ERFSL / Eureka-family** — LLM-writes-reward-CODE (a) but in robotics/control with SCALAR or preference feedback and no tail/portfolio. **Break (c)+(d).**

**Net (updated 2026-07-02):** the ELfolio scoop item is CLOSED (cited `zeng2025elfolio` + distinguished in
CH1/CH2), GIFT — the freshest and sharpest finance neighbour — is cited (`wu2026gift`) + fenced, and
LLM-Judge-SAC is verified-pending-cite (write-time fence). No paper threatens the full conjunction; the
Related-Work fence paragraph (CH2) now cite-and-distinguishes DLM, FinRL-DeepSeek, GIFT, ELfolio, CARD/Eureka
and MadEvolve explicitly.

---

## 6. ADDED 2026-07-02 — nearest-neighbour verification sweep (3 papers, first-hand)

Three papers verified first-hand on 2026-07-02 (coordinates fence-checked); the two arXiv PDFs were
downloaded into the corpus the same day and re-read via PyMuPDF (page count + first-page title confirmed).

### 6.1 GIFT (Wu et al. 2026) — `wu2026gift`
- **Where it lives:** `01_literature/B_closest_neighbours/GIFT__2606.08450.pdf` (arXiv:2606.08450 v1,
  2026-06-07, 25 pp, 13 authors, cs.AI; code at github.com/KAG778/GIFT). Title verified on p.1:
  "GIFT: LLM-Guided State-Reward Interface for Financial Reinforcement Learning".
- **Honest summary:** GIFT uses an LLM to design the *learning interface* of a PPO portfolio-trading
  agent, jointly on BOTH channels: Factor-guided State Enhancement (FSE) generates state features from
  financial-factor primitives, and Risk-rule-guided Reward Shaping (RRS) generates auxiliary rewards as
  an LLM intrinsic term plus a selected subset of a FIXED library of portfolio-risk rules
  (concentration/turnover/drawdown/vol/regime/momentum). A Diagnostic-guided Refinement (DGR) loop
  revises candidate interfaces using generic PPO rollout diagnostics — information coefficients, reward
  trend/variability, drawdown and risk-adjusted performance — then FREEZES the selected interface before
  evaluation. Full-text scan confirms: zero occurrences of "CVaR"/"conditional value"; no quantile/tail
  vector is ever fed back; evaluation is framework-vs-baselines on rolling windows with no controlled
  feedback-content manipulation and no pre-registration; backbone is PPO (A2C transfer check), not SAC.
- **How it integrates:** cited + fenced in CH1 (intro fence: "GIFT lets it select reward terms from a
  fixed risk-rule library ... "), and CH2 Related Work ("The freshest finance neighbour, GIFT, does move
  the language model into the reward channel ... but it redesigns the state jointly with the reward ...
  its refinement loop feeds generic rollout diagnostics ... rather than any multi-level realised-return
  tail vector, and it is a framework demonstrated against baselines, not a controlled manipulation of
  feedback content"). Distinguishers: state co-varied (breaks our reward-only identification), fixed
  rule library (not free-form reward code under tail selection), diagnostics-not-tail feedback, no
  ablation of feedback content, no pre-registration, PPO not SAC.

### 6.2 ELfolio (Zeng, Chen, Wang & Liang 2025) — `zeng2025elfolio`
- **Where it lives:** `01_literature/I_also_mentioned/ELfolio__2025.pdf`. Venue now PINNED:
  Intelligent Computing (Science Partner Journal), vol. 4, article 0176, published 2025-11-17,
  DOI 10.34133/icomputing.0176 (supersedes the earlier "manual, venue unconfirmed" status in
  `also_mentioned_log.md`).
- **Honest summary:** ELfolio evolves LLM-written portfolio-STRATEGY code across RL, evolutionary and
  DL path templates. The killer verbatim, confirmed first-hand: candidates are selected "with the
  Sharpe ratio serving as the fitness function" — a SCALAR fitness, i.e. exactly this project's CONTROL
  condition. Its RL-path template CAN rewrite state-action rules and reward functions, but selection
  never sees anything but scalar Sharpe; CVaR appears only in the formulation background, in baseline
  names (MinCVaR) and as an evaluation-table metric — never as feedback to the LLM. No fixed RL agent,
  no pre-registration.
- **How it integrates:** cited + fenced in CH1 ("ELfolio evolves whole strategy code under a *scalar
  Sharpe fitness*") and CH2 ("The closest portfolio system, ELfolio ... selection is driven by a scalar
  Sharpe-ratio fitness function, with tail measures appearing only in its evaluation tables and never in
  the feedback to the model; it thereby instantiates precisely the scalar-feedback *control* condition
  of our design, not its treatment"). This converts the former possible-scoop into corroboration: the
  nearest portfolio+risk+LLM+RL system operationalizes our control arm, not our treatment.

### 6.3 LLM-Judge-SAC (Al Ridhawi, Haj Ali & Al Osman 2026) — cite key PENDING (verified-pending-cite, write-time fence)
- **Where it lives:** `01_literature/B_closest_neighbours/LLM-Judge-SAC__2605.05739.pdf`
  (arXiv:2605.05739, 2026-05-07, 17 pp; submitted to Taylor & Francis Applied Artificial Intelligence).
  Title verified on p.1: "Multi-Dimensional Behavioral Evaluation of Agentic Stock Prediction Systems
  Using Large Language Model Judges with Closed-Loop Reinforcement Learning Feedback".
- **Honest summary:** An ensemble of three LLM judges scores logged behavioural traces of an agentic
  stock-FORECASTING system along six dimensions (regime detection, routing, adaptation, risk
  calibration, strategy coherence, error recovery); cross-judge agreement Krippendorff alpha = 0.85,
  composite score correlates Spearman rho = 0.72 with realized 20-day Sharpe. Closing the loop,
  deficient per-dimension scores become a credit-assigned penalty ADDED (strength lambda, stable at
  <=0.20, best 0.15) to the FIXED hand-written reward of a SAC controller whose 2-D action adjusts a
  regime threshold and a blending weight; dimension weights are validation-frozen Spearman correlations
  with Sharpe. Result: one-day MAPE 0.61% -> 0.54% on a held-out 2017-2025 test, Diebold-Mariano
  significant, Giacomini-White-localized to the high-vol regime. Full-text scan: zero "CVaR", zero
  "portfolio" — forecasting accuracy, not allocation.
- **How it integrates:** verified-pending-cite — a write-time fence for the Related-Work neighbour
  paragraph when CH2 is next touched (do NOT add to refs.bib until then). Distinguishers: the LLM is a
  score-EMITTER (judge), never a reward-code author; the penalty modulates a fixed human-written SAC
  reward (structurally the FinRL-DeepSeek pattern, on the reward instead of the action); domain is
  single-name forecasting MAPE, not portfolio allocation; no return-tail vector is fed anywhere.
  Breaks conjunction limbs (a), (c), (d).

---

## Summary

- **Owned-but-uncited:** ~150 of 196 corpus papers (section != NotRelevant) have NO surname+year match in
  refs.bib. This is expected (refs.bib is a declared Tier-1 CORE set), but ~28 High/Medium items are real
  leverage losses — most acutely the **entire Data cost-model cluster (0% cited)** and the **reporting
  multiplicity family** (White, Hansen, Romano-Wolf, Ledoit-Wolf-Sharpe, Harvey-Liu-Zhu — all named in the
  bib header as "to-be-promoted" but with NO key yet).
- **Integrity flags:** 3 mislabeled-file (FinRLlama, Cheridito-Stadje, Maillard/Cagna-Casuccio) + 1
  unparseable (Follmer-Schied) + 1 possible-scoop (ELfolio — **MANAGED 2026-07-02**) + ~70
  preprint-only-coords (corpus) + ~40 `% VERIFY` coordinate flags inside refs.bib + 1 MUST-ACQUIRE
  (abel2021expressivity, second-hand only).
- **Scoop risks (updated 2026-07-02):** 0 actionable — ELfolio closed (cited + distinguished as the
  CONTROL condition), GIFT cited + fenced, LLM-Judge-SAC verified-pending-cite; 0 breach the full
  novelty conjunction (intact). See §6.

### Top 5 highest-value leverage actions
1. ~~**Add ELfolio (2025) to refs.bib and write the cite-and-distinguish sentence**~~ — **DONE
   2026-07-02** (`zeng2025elfolio` in refs.bib; CH1/CH2 fences live; venue pinned — see §6.2).
2. **Promote the reporting multiplicity family** (White 2000, Hansen 2005, Romano-Wolf 2005,
   Ledoit-Wolf-Sharpe 2008, Harvey-Liu-Zhu 2016) — these are load-bearing for the severity/null headline
   and are currently keyless despite being flagged "to-be-promoted" in the bib header.
3. **Wire the Optimal-Reward-Problem theory spine correctly** — split the conflated `sorg2010orp` into
   the OGA paper + Sorg 2011 PhD + InternalRewards-Sorg 2010 + IMRL-Singh 2010, and add RewardShaping-Ng
   1999; this is the formal license for the whole premise and is presently thin.
4. **Cite the Data cost-model cluster** (Kyle 1985, Almgren 2005, Almgren-Chriss 2000, Toth 2011,
   Cont 2001, Brown 1992, Frazzini 2018, Mandelbrot 1963) — the Methods/Data chapter currently has 0
   transaction-cost / stylized-facts / survivorship citations on disk-read papers.
5. **Lean LEARN-Opt (2025) and Agentic-Trading-Survey (2026) hard in Limitations/Reporting** — the two
   strongest external corroborators of the likely-null and of the field-level reproducibility argument
   that justifies the entire rigor stack.
