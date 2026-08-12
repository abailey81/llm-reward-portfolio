# Literature & Strategy Dossier — 24-scout web sweep (2026-06-26)

Consolidated output of 24 strict web-research scouts (each forbidden from fabricating citations; every
source tagged VERIFIED-FETCHED vs SNIPPET). This is the citation backbone, novelty defence, examiner
alignment, grading-rubric targets, and publication plan for the dissertation. **Before any 2025-26
arXiv id or any DOI enters `paper/refs.bib`, re-verify it first-hand**(the supervisor co-authors in
this space). Flags at the end are load-bearing.

---

## A. HEADLINE VERDICTS

1. **The novelty cell is EMPTY (confirmed by 3 independent scouts + a dedicated scoop sweep).** No
   single work occupies the conjunction: *(LLM authors reward-function CODE) × (fed the realized-return
   lower-tail distribution / multi-level CVaR as off-critic iteration feedback) × (risk-sensitive
   PORTFOLIO RL, fixed agent) × (pre-registered comparative inference).*Axis 4 (pre-registration) is
   essentially unique across the entire LLM-reward-design literature.
2. **The 90%+ band is reachable but is gated on WRITING, not science.** UCL's own descriptors define
   86–100 as *"of publishable quality… would receive that judgement at a peer-reviewed journal… clearly
   capable of doctoral research."*A pre-registered, well-disclosed null IS a publishable contribution.
3. **Best publication path for this (likely-null, single-instance) result:** a NeurIPS/ICAIF **finance
   workshop**(null-friendly, non-archival) → **TMLR**(its acceptance criteria explicitly drop novelty/
   SOTA; a well-evidenced null passes by design) → optionally ICAIF main. This sequencing also satisfies
   the dissertation's "publishable" grade descriptor.

---

## B. NOVELTY DEFENCE — the empty cell, neighbours, scoop threats, counter-evidence

### B.1 The "feedback shown to an LLM reward designer" taxonomy (your delta, made precise)
- Human NL / preference: Kwon 2023; Text2Reward (failure summaries); REvolve (Elo preferences).
- Per-component **scalar** training time-series + aggregate fitness: **Eureka** (verbatim §3.3: reflection
  "tracks the **scalar values** of all reward components and the task fitness function at intermediate
  policy checkpoints"); DrEureka; CARD (process feedback).
- Trajectory/behaviour analysis: Auto-MC-Reward; CARD (trajectory feedback).
- Coarse distribution **check**: CARD (binary success>failure return ordering) — the closest "distribution"
  flavour, but NOT a multi-level tail.
- News-sentiment **scores** into a fixed reward (not code): FinRL-DeepSeek.
- **YOUR CELL (empty):** multi-quantile realized-return **lower-tail profile** (CVaR-5/10/25/1%, tail mass,
  robust skew), measured **off-critic**, fed to a **code-writing** LLM reward designer, in **risk-sensitive
  portfolio RL**, under **pre-registration**.

### B.2 Nearest neighbours — cite-and-distinguish in Related Work (failing to cite = the most likely ding)

> ⭐ **VERIFICATION PASS, 2026-08-10 — ALL NINE POSITIONING-MATRIX NEIGHBOURS RE-READ FROM THE ON-DISK PDFs,
> AND THE RESULT NOW SHIPS INSIDE THE DISSERTATION AS APPENDIX H.** Every cell of the Table 10 matrix was
> re-sourced page by page from the corpus copies (Eureka 45 pp · Text2Reward 37 pp · REvolve 42 pp ·
> CARD 28 pp · DLM 38 pp · ELfolio 15 pp · FinRL-DeepSeek 5 pp · GIFT 25 pp · FINCON 30 pp). Of the 54
> weight-bearing cells, **36 now carry a verbatim quotation with its page, 3 carry a page locator, and 15
> are counted full-text searches** because the cell asserts an absence and no quotation can establish one.
> (Counted mechanically from the shipped table, not by hand: a first hand tally read 37/2/15 and was wrong
> on REvolve's agent cell, which is a locator rather than a quotation.)
> ⚠ **THE READ-DATE RECORD WAS THINNER THAN THIS FILE IMPLIED, and Appendix H states it rather than fixing
> it silently:** a dated first-hand read is recorded here for **three of the nine** (ELfolio 2026-07-02,
> GIFT 2026-07-02, FINCON 2026-08-10). Eureka carries a quoted verbatim claim but no date; **Text2Reward,
> REvolve, CARD, DLM and FinRL-DeepSeek carried neither** until this pass. Their rows in Appendix H
> therefore read "none recorded" and give the 2026-08-10 *verification* date instead, which is a weaker
> thing than a reading date and is labelled as one. **Do not backfill a reading date that was never taken.**
- **DLM (Behari et al., NeurIPS 2024, arXiv:2402.14807)** — structural twin (LLM proposes reward code,
  iterates on simulated feedback shown a distribution). Distinct: public-health RMABs not finance; the
  distribution is over **demographic state-features**, not realised returns, so it is not a tail profile;
  no risk/tail objective; no pre-registration. **Disclose prominently.**
  ⛔ **THE "AGENT NOT HELD FIXED" DISTINCTION WAS WRONG AND IS WITHDRAWN, 2026-08-10.** This entry, and
  Table 10's cell with it, read *"bandit not continuous-action SAC"* as if DLM trained no fixed learner.
  It does. **§4.3, p. 5:** *"We evaluate each LLM-proposed reward function $R_{1:K}$ by training a policy
  network $\theta$ under each proposed reward $R_i$"*, updated with PPO at Algorithm 1 line 13. The cell's
  supporting quotation had been taken from DLM's **§2 Related Work**, where it describes how RMABs were
  *classically* solved by the Whittle index — someone else's method, not DLM's. **DLM therefore holds one
  learner fixed while the reward varies, which is this study's own identification structure, and the honest
  distinction is narrower: the learner is discrete-action rather than continuous-action, and Algorithm 1
  initialises the policy and critic once per iteration (line 5) outside the per-reward loop (line 6), so
  candidates are not re-initialised between rewards.** The conjunction survives on domain, feedback content
  and risk-sensitivity. **Lesson for every other row: check the enclosing SECTION of a quotation, not only
  its page. A Related Work sentence cannot evidence what a paper does.**
- **FinRL-DeepSeek (arXiv:2502.07393)** — finance + "risk-sensitive" + LLM. Distinct: LLM = sentiment/risk
  **score encoder** scaling actions; the **reward is the fixed hand-written CPPO/CVaR-PPO objective**; no
  reward code authored; no tail fed to the LLM.
  ✅ **THE CORRUPT-FETCH CAVEAT IS CLOSED, 2026-08-10.** It read: *"PDF fetch was corrupt across 2 scouts —
  re-verify the 'human-written reward' claim from the HTML before citing it as the key distinction."* The
  corpus copy (`C_signals_into_rewards/FinRL-DeepSeek__2502.07393.pdf`) opens and extracts cleanly at
  **5 pages**, and the answer is sharper than the claim it was checked against: **the string `reward`
  occurs ZERO times in the entire paper.** So nothing is authored, revised or fed back as a reward at all.
  The paper's own statement of what it does, verbatim from p. 1: *"We extend the Conditional Value-at-Risk
  Proximal Policy Optimization (CPPO) algorithm, by adding risk assessment and trading recommendation
  signals generated by a LLM from financial news."* The LLM's scores enter as multiplicative perturbations
  on the action (p. 2, *"Sf > 1: Amplifies actions under positive recommendation"*). Recorded in the
  dissertation at Appendix H.
- **FINCON (Yu et al., NeurIPS 2024, arXiv:2407.06567v3)** — [VERIFIED first-hand 2026-08-10 from
  `01_literature/I_also_mentioned/FINCON__2024.pdf`, 30 pp.; cited `yu2024fincon`, row in T10] a
  manager-analyst LLM multi-agent system for financial decision-making. Distinct on the column that
  matters: **no numeric reward is trained into a policy at all.** Risk control is dual-level and
  *verbal* — verbatim from the contributions list, "Within episodes, risk is supervised using the
  Conditional Value at Risk (CVaR) ... Across episodes, we introduced a verbal reinforcement mechanism,
  where investment beliefs are updated based on reasoning trajectories and profit-and-loss (PnL) trends".
  ⚠ CORRECTED 2026-08-10: this quotation previously ended "based on reason[ing]", a truncation that the
  PDF does not support; re-read from p. 2 of the on-disk copy. Full-text counts over the 30 pages:
  `CVaR` 30, `Conditional Value at Risk` 4, `verbal reinforcement` **12**, `belief` **44**, counted
  case-insensitively over the whole 30 pages with the source's line-break hyphenation joined. The PDF
  prints no proceedings volume number, so none is asserted in `refs.bib`.
  ⚠ CORRECTED 2026-08-10: this line read `verbal reinforcement` 7 and `belief` 42, and neither figure is
  reproducible under any stated convention (case-sensitive gives 8 and 42, case-insensitive gives 12 and
  44). The dissertation's Appendix H prints the case-insensitive figures and states the convention, which
  is what makes them checkable; these are now the same numbers.
  ⚠ ADDED 2026-08-10 BECAUSE ITS ABSENCE WAS A LIVE DEFECT: FINCON had occupied a full row of the
  positioning matrix while having no entry here, no bibkey and no citation anywhere in the document —
  four lines below a preamble pledging that every cell traces to a first-hand-read entry in this file.
- **GIFT (Wu et al., arXiv:2606.08450, v1 2026-06-07)** — [VERIFIED first-hand 2026-07-02; cited
  `wu2026gift`, fenced in CH1+CH2; PDF in B_closest_neighbours] the **freshest finance neighbour**: LLM
  designs the PPO state-reward interface — FSE generates state features from factor primitives, RRS
  generates an LLM intrinsic reward term + a subset of a **fixed risk-rule library**, DGR refines on
  **generic rollout diagnostics** (ICs, reward trend/variability, drawdown). Distinct: co-varies **state
  AND reward**(breaks our reward-only identification); library-constrained not free-form reward code;
  **no CVaR/quantile/tail vector anywhere** (full-text scan: 0 hits); framework-vs-baselines with no
  feedback-content ablation; no pre-registration; PPO not SAC.
- **ELfolio (Zeng, Chen, Wang & Liang, Intelligent Computing 4:0176, 2025-11-17, DOI
  10.34133/icomputing.0176)**— [VERIFIED first-hand 2026-07-02; cited `zeng2025elfolio`, fenced in
  CH1+CH2; PDF in I_also_mentioned] the **closest portfolio system**: evolves LLM-written trading-STRATEGY
  code across RL/evolutionary/DL path templates. Killer verbatim: candidates selected "with the Sharpe
  ratio serving as the fitness function" — **scalar-Sharpe fitness = precisely our CONTROL condition**.
  Its RL-path template CAN rewrite reward functions, but selection never sees anything but scalar Sharpe;
  CVaR appears only in formulation background, baseline names (MinCVaR) and eval tables — never as
  feedback to the LLM. No fixed RL agent; no pre-registration. Former possible-scoop, now managed:
  the nearest portfolio+risk+LLM+RL system operationalizes our control arm, not our treatment.
- **LLM-Judge-SAC (Al Ridhawi, Haj Ali & Al Osman, arXiv:2605.05739, 2026-05-07)** — [VERIFIED first-hand
  2026-07-02; **verified-pending-cite** (write-time fence — key to be added when CH2 is next touched);
  PDF in B_closest_neighbours] ensemble of 3 LLM judges scores behavioural traces of an agentic
  stock-forecasting system on six dimensions; deficient scores become a **credit-assigned penalty ADDED
  to a fixed hand-written SAC reward**(strength λ ≤ 0.20 stable). Distinct: LLM = score-** emitter**
  (judge), never a reward-code author; SAC only tunes two hyperparameters (regime threshold + blending
  weight) of a forecasting pipeline — single-name MAPE, **not portfolio allocation**; zero CVaR/tail
  content (full-text scan: 0 "CVaR", 0 "portfolio"). Structurally the FinRL-DeepSeek pattern moved from
  the action channel onto the reward.
- **CARD (arXiv:2410.14660; KBS 2025/26)** — LLM writes reward code + dynamic feedback, *beats a human
  oracle on 3/12 tasks*. Distinct: robotics/control; feedback is process/trajectory/binary-preference, not
  a multi-level tail; no finance, no pre-registration. Cite for the "beat-the-human precedent" (so H1 is
  not over-claimed as novel).
- **Eureka (arXiv:2310.12931, ICLR 2024)** — the method you instantiate + the H1 "beat-the-human" template
  (beats humans on 83% of 29 tasks, +52%). The **−28.6% reward-reflection ablation** is your single
  strongest "feedback content matters" citation.
- **MadEvolve (arXiv:2605.23007, 2026) / QuantEvolve (arXiv:2510.18569) / RF-Agent (arXiv:2602.23876,
  NeurIPS'25 Spotlight?)**— evolve *strategy* code (not reward) or generate reward code in *robotics*; no
  RL-portfolio + tail + pre-reg. MadEvolve is the freshest look-alike → cite + distinguish (whole-strategy
  code, not RL; scalar fitness; no pre-reg).
- **ShinkaEvolve (arXiv:2509.19349) / OpenEvolve / AlphaEvolve (arXiv:2506.13131) / FunSearch (Nature 625,
  2024)**— the "rich feedback channels already exist" objection. Concede the *channel*; your novelty is
  the **financial object placed in it** (a return tail). None feeds a return-distribution as fitness.

### B.3 SCOOP / COUNTER threats you MUST cite-and-rebut (an informed examiner knows these)
- **"Reward Is Enough: LLMs Are In-Context RL" (arXiv:2506.06303, 2025)** — strongest published claim that
  *scalar reward suffices* for LLM self-improvement. Rebut: short-horizon reasoning, not reward-code design;
  their gain needs *accumulated multi-round* reward trajectories, not one fed distribution; Eureka's −28.6%
  and the directional-feedback line show the margin is large where it's been measured.
- **The LLM-numeracy cluster** (Exposing Numeracy Gaps arXiv:2502.11075; NumeroLogic; Min et al. EMNLP 2022
  "random labels barely hurt" arXiv:2202.12837) — the "your NEGATIVE responsiveness is a model-numeracy
  artefact, not a channel result" attack. **Turn it into the finding:** the negative sign says the LLM edits
  on *semantic/format* cues (it sees "tail/CVaR" tokens) not on the fed *magnitudes* — a documented,
  interpretable mode, framed via Nie et al. (directional vs non-directional feedback, arXiv:2405.16434) and
  scoped to a frontier model (Revisiting-OPRO arXiv:2405.10276: small LLMs flatline, frontier exploit).

---

## C. CITATION BACKBONE BY CHAPTER (verified identifiers; status tagged)

### C.1 Method lineage (LLM reward design)
- Eureka — Ma et al., **ICLR 2024**, arXiv:2310.12931 [VERIFIED]. Reward reflection = scalar component
  time-series; −28.6% ablation [VERIFIED verbatim].
- Kwon et al., **ICLR 2023**, arXiv:2303.00001; Text2Reward — Xie et al., **ICLR 2024 Spotlight**,
  arXiv:2309.11489; Language-to-Reward — Yu et al., **CoRL 2023**, arXiv:2306.08647; DrEureka — **RSS 2024**,
  arXiv:2406.01967; Auto-MC-Reward — **CVPR 2024**, arXiv:2312.09238; REvolve — **ICLR 2025**,
  arXiv:2406.01309; CARD — arXiv:2410.14660 (+ KBS DOI — verify issue); Self-Refine — Madaan, **NeurIPS
  2023**, arXiv:2303.17651; Survey: Cao et al. **IEEE TNNLS 2024**arXiv:2404.00282 (the "reward designer"
  taxonomy slot to claim).
- Program search: FunSearch — **Nature 625:468–475 (2024)**, DOI 10.1038/s41586-023-06924-6 (cite 2024 not
  2023); AlphaEvolve — arXiv:2506.13131 (DeepMind tech report, not peer-reviewed); ShinkaEvolve
  arXiv:2509.19349; OpenEvolve (GitHub).

### C.2 Feedback-content matters / LLM-optimizer responsiveness
- Nie et al. "Directional Feedback for LLM Optimizers" arXiv:2405.16434 (NeurIPS'23 FMDM workshop —
  **workshop, not main**) [VERIFIED] — the framing keystone.
- FCP "Learn from Verbal Feedback without Scalar Rewards" arXiv:2509.22638 [VERIFIED] (Table 5 = "the model
  genuinely uses feedback content" rebuttal); GEPA arXiv:2507.19457 (**ICLR 2026 Oral**); OPRO — Yang et al.
  **ICLR 2024** arXiv:2309.03409; Reflexion — **NeurIPS 2023** arXiv:2303.11366; TextGrad arXiv:2406.07496;
  Min et al. **EMNLP 2022** arXiv:2202.12837; Kossen et al. **ICLR 2024** arXiv:2307.12375 (cite both — a
  contested pair); "LLMs Cannot Self-Correct Reasoning Yet" **ICLR 2024** arXiv:2310.01798.

### C.3 Distributional & risk-sensitive RL (the axis you are NOT on — off-critic)
- C51 — Bellemare-Dabney-Munos **ICML 2017** arXiv:1707.06887; QR-DQN — Dabney et al. **AAAI 2018**
  arXiv:1710.10044 (cite **2018**); IQN — Dabney et al. **ICML 2018** arXiv:1806.06923; FQF — **NeurIPS 2019**
  arXiv:1911.02140; book: Bellemare-Dabney-Rowland, *Distributional RL*, **MIT Press 2023**.
- Risk-sensitive: **DSAC — Ma et al., JAIR, arXiv:2004.14547** (the primary contrast; disambiguate from the
  autonomous-driving "DSAC"); WCSAC — **AAAI 2021**; Théate-Ernst arXiv:2212.14743 (+ their *Expert Systems
  w/ Apps 2022*portfolio sibling) — **the cleanest "prior risk-sensitive portfolio RL needs a
  distributional critic; you don't" contrast**; "Distributional Reward Shaping" (RLDM 2022, ssanner) —
  **the precedent that a scalar reward signal can carry CVaR/tail sensitivity without a distributional
  critic**(FETCH + verify the title/authors — PDF wouldn't parse).

### C.4 Risk-sensitive RL for portfolios + the reward family
- **Sood et al. 2023** — FinPlan'23/ICAPS, JPMorgan; reward = Moody Differential Sharpe; cash-row state
  = **vol20, vol20/vol60, VIX** (your exact tail-feature triple) [VERIFIED at equation level]. ⚠ a duplicate
  arXiv:2602.17098 carries a 2026 id — **cite the 2023 venue**.
- Moody-Wu-Liao-Saffell 1998 (*J. Forecasting* 17:441–470, DSR origin) + Moody-Saffell 2001 (*IEEE TNN*
  12(4)); Choudhary et al. 2025 (*IJCIS*, DOI 10.1007/s44196-025-00875-8 — Sharpe+Sortino+Calmar+CVaR+
  drawdown+turnover, grounds your reward palette); FinRL — Liu et al. **ICAIF 2022** DOI 10.1145/3490354.
  3494366 + FinRL-Meta **NeurIPS 2022** arXiv:2112.06753.

### C.5 Coherent-risk THEORY (Okhrati's deepest scrutiny zone — get exact)
- **Kusuoka 2001**, *Advances in Mathematical Economics* Vol.3 (Springer Tokyo) pp.83–95, DOI
  10.1007/978-4-431-67891-5_4 — **NOT RIMS Kokyuroku**.
- **Shapiro 2013**, *Math. of OR* 38(1):142–152, DOI 10.1287/moor.1120.0563 [VERIFIED full text] — the
  quotable modern restatement: law-invariant coherent = sup over mixtures of AV@R; a **comonotonic** one is
  a **unique** mixture of CVaRs (= spectral). **This single cite de-risks the "multi-level CVaR is a coherent
  basis" claim.**
- Artzner-Delbaen-Eber-Heath 1999, *Math. Finance* 9(3):203–228, DOI 10.1111/1467-9965.00068; **Acerbi 2002
  "Spectral measures" JBF 26(7):1505–1518 DOI …00281-9**and **Acerbi-Tasche 2002 "Coherence of ES" JBF
  26(7):1487–1503 DOI …00283-2**(DISTINCT papers — the classic conflation); Rockafellar-Uryasev 2000
  *J. Risk* 2(3):21–41 (**no DOI — don't invent one**; the 2002 JBF version DOI 10.1016/S0378-4266(02)
  00271-6 has one); Föllmer-Schied 2002, *Finance & Stochastics* 6(4):429–447 DOI 10.1007/s007800200072;
  **Blackwell 1953**, *Ann. Math. Stat.* 24(2):265–272, DOI 10.1214/aoms/1177729032 (state the garbling/
  coarsening bridge explicitly — it's an *analogy* to experiments, not risk measures).

### C.6 Backtest overfitting / data-snooping / multiple testing (examiner-central)
- **DSR** — Bailey & López de Prado, *JPM* 40(5):94–107 (2014), SSRN 2460551 [VERIFIED formula]; **PSR/MinTRL**
  origin = Bailey-LdP *J. Risk* 15(2):3–44 (2012), SSRN 1821643 (cite for PSR); **PBO/CSCV** — Bailey-Borwein-
  LdP-Zhu, *J. Computational Finance* **20(4):39–69 (2017)**, SSRN 2326253 [VERIFIED Def 2.2 + Algorithm 2.3;
  your full-enumeration C(16,8)=12,870 matches CSCV]; "Pseudo-Mathematics" *Notices AMS* 61(5):458–471 (2014)
  — motivation only, NOT the PBO source.
- White 2000 *Econometrica* 68(5):1097–1126 DOI 10.1111/1468-0262.00152; Hansen 2005 SPA *JBES* 23(4):365–380
  DOI 10.1198/073500105000000063; Romano-Wolf 2005 *Econometrica* 73(4):1237–1282 DOI 10.1111/j.1468-0262.
  2005.00615.x; Harvey-Liu-Zhu 2016 *RFS* 29(1):5–68 DOI 10.1093/rfs/hhv059 (t>3 hurdle); **Harvey-Liu 2015
  "Backtesting" *JPM* 42(1):13–28**(applies **BHY to Sharpe ratios**— the bridge to your BH-over-family);
  BH 1995 *JRSS-B* 57(1):289–300; **BY 2001** *Ann. Stat.* 29(4):1165–1188 DOI 10.1214/aos/1013699998
  (**decide PRDS-BH vs BY arbitrary-dependence inflation and SAY which** — top citation flag);
  **Witzany 2021** *Risks* 9(1):18 DOI 10.3390/risks9010018 — the peer-reviewed CSCV-bias critique (negatively
  biased near zero-mean; over-optimistic if one strategy dominates) — **cite to pre-emptively disclose**.
- Factor attribution: Fama-French 1993/2015, Carhart 1997, **Frazzini-Pedersen BAB 2014** *JFE* 111(1):1–25
  (cite **2014** not 2010), **Asness-Frazzini-Pedersen QMJ 2019** *Rev. Acc. Studies* 24(1):34–112 (cite
  **2019**), Newey-West 1987 *Econometrica* 55(3):703–708, GRS 1989 (joint alpha=0 test).

### C.7 Expected-Shortfall backtesting + elicitability
- **Fissler-Ziegel-Gneiting 2015** arXiv:1507.00244 [VERIFIED] — the keystone: ES non-elicitable, joint
  (VaR,ES) score, **proposes the DM comparative ES backtest**; **FZ-2016** *Ann. Stat.* 44(4):1680–1707 DOI
  10.1214/16-AOS1439 (the theorem; **has an Erratum arXiv:1901.08826**); **FZ0** = Patton-Ziegel-Chen 2019
  *J. Econometrics* 211(2):388–413 (FZ0 is THEIRS, label = G1=0,G2=−1/x, the 0-homogeneous power property);
  Harvey-Leybourne-Newbold 1997 *IJF* 13(2):281–291 DOI 10.1016/S0169-2070(96)00719-4 (the √[(T+1−2h+h(h−1)/T)
  /T] factor + t(T−1); **could not open the 1997 PDF — verify parenthesisation**); Gneiting 2011 *JASA*
  106(494):746–762; Diebold-Mariano 1995 *JBES* 13(3):253–263; Nolde-Ziegel 2017 *AOAS* 11(4):1833–1874
  DOI 10.1214/17-AOAS1041; Acerbi-Székely 2014 (*Risk*) + 2017 *Management Science* 63(4) DOI 10.1287/mnsc.
  2015.2342 (the **calibration/contrast**, not elicitability support).
- ⚠ **EXAMINER ATTACK (new, critical):** "Heavy Tails and Predictive Ability Testing" (arXiv:2605.16866,
  2026) — when loss differentials have infinite variance (tail index <2), the DM test rejects a true null
  **up to 70% of the time irrespective of sample size**. HLN fixes *small-sample* size, NOT heavy-tail
  distortion. **Disclose; check the FZ0 loss-differential tail index / finite variance.** Pair with Du-
  Escanciano 2017 / Bayer-Dimitriadis 2022 (ES backtests underpowered) + Fissler "Forecaster's Dilemma"
  *Stat. Sci.* 32(1):106–127 (2017).

### C.8 EVT / tail estimation (measurement.py + the "750-point CVaR is noisy" defence)
- Canon: Pickands 1975 *Ann. Stat.* 3(1):119–131; Balkema-de Haan 1974 *Ann. Prob.* 2(5):792–804; Smith 1987
  *Ann. Stat.* 15(3):1174–1207 (GPD-MLE); Davison-Smith 1990 *JRSS-B* 52(3):**393–425**; McNeil-Frey 2000
  *J. Empirical Finance* 7(3-4):271–300 (EVT for ES — the examiner-aligned cite); McNeil-Frey-Embrechts
  *QRM* (Princeton 2015); Embrechts-Klüppelberg-Mikosch 1997.
- Small-sample LIMITATION arsenal: **Smith 1985** *Biometrika* 72(1):67–90 (xi≤−0.5 non-regular — your
  guard's justification); Giles-Feng-Godwin 2016 *Comm. Stat.* 45(8):2465–2483 (analytic O(1/n) GPD-MLE
  bias); **Belzile-Davison 2020** arXiv:2007.10780 (threshold/POT route is the biased one); Cont-Deguest-
  Scandolo 2010 *Quant. Finance* 10(6):593–606 (CVaR/ES *less robust* to estimate than VaR); Scarrott-
  MacDonald 2012 *REVSTAT* 10(1):33–60 (threshold instability; REVSTAT has **no DOI**).

### C.9 Survivorship / delisting / PIT (data chapter)
- **Shumway 1997** *JF* 52(1):327–340 DOI 10.1111/j.1540-6261.1997.tb03818.x — **−30% = NYSE/AMEX**
  (empirical average, not a prescribed round number) [VERIFIED verbatim]; **Shumway-Warther 1999** *JF*
  54(6):2361–2379 DOI 10.1111/0022-1082.00192 — **−55% = NASDAQ**, and **explicitly excludes M&A/migration
  (codes 501/502) from performance delistings; ≤1% of merger returns are even missing**[VERIFIED — this
  textually proves your univ4 M&A-surcharge limitation; quote it]; **Beaver-McNichols-Price 2007** *JAE*
  43(2-3):341–368 DOI 10.1016/j.jacceco.2006.12.002 (the operationalised −30/−55 rule — cite for *applying*
  it). Survivorship: Brown-Goetzmann-Ibbotson-Ross 1992 *RFS* 5(4):553–580; Kothari-Shanken-Sloan 1995
  *JF* 50(1):185–224 (look-ahead/back-fill). ⚠ **Do NOT attribute −55% to Shumway 1997.**

### C.10 RL evaluation rigor (legitimizes your per-seed inference)
- **Agarwal et al. 2021** *NeurIPS Outstanding Paper* arXiv:2108.13264 — rliable: IQM + stratified bootstrap
  CIs + probability of improvement + performance profiles. **Your machinery is this protocol by name.**
- Colas et al. 2018 arXiv:1806.08295 (**≥20 seeds**; your 30 exceeds it — state this); Henderson et al.
  **AAAI 2018** DOI 10.1609/aaai.v32i1.11694 (single-seed unreliable; reward-rescaling sensitivity);
  Patterson et al. *JMLR 2024* arXiv:2304.01315 (multi-agent comparison best-practice); Jordan et al.
  **ICML 2020** arXiv:2006.16958 (authors = Jordan, Chandak, Cohen, Zhang, Thomas); Bouthillier et al. MLSys
  2021 arXiv:2103.03098 (variance accounting).

### C.11 Pre-registration / equivalence / open science
- **Lakens 2017** *SPPS* 8(4):355–362 DOI 10.1177/1948550617697177 + **Lakens-Scheel-Isager 2018** *AMPPS*
  1(2):259–269 DOI 10.1177/2515245918770963 [both VERIFIED] — TOST/SESOI backbone. (⚠ set a *substantive
  economic*SESOI, not Lakens' power-based one.)
- Nosek et al. 2018 *PNAS* 115(11):2600–2606; **Olken 2015** *JEP* 29(3):61–80 DOI 10.1257/jep.29.3.61 (the
  econ/finance pre-analysis-plan precedent); NeurIPS Pre-registration-in-ML workshops (PMLR v148 2021 /
  v181 2022 — "rare and emerging", don't over-claim); Hofman et al. 2023 arXiv:2311.18807 (preprint);
  Pineau et al. *JMLR 2021* (reproducibility checklist); **Rubin 2017** *Rev. Gen. Psych.* 21(4):321–329
  DOI 10.1037/gpr0000135 — **must address: argues pre-registration ALONE doesn't beat forking paths;
  adjusted-alpha does. You do BOTH (pre-reg + BH/conjunction) — cite him and show you clear his bar.**
  Gelman-Loken 2014 *American Scientist* 102(6):460 (the publishable version).

### C.12 Agent / SAC / reward scaling (training-adequacy defence)
- SAC — Haarnoja et al. **ICML 2018** arXiv:1801.01290 (**PMLR 80:1856–1865**) [VERIFIED — finalize the stale
  VERIFY note]; SAC-Applications arXiv:1812.05905 (auto-α); TQC — Kuznetsov et al. **ICML 2020**
  arXiv:2005.04269 (ships in `sb3-contrib`); **PopArt — van Hasselt et al. NeurIPS 2016 arXiv:1602.07714**;
  SB3 — Raffin et al. *JMLR 22(268):1–8 (2021)*; Engstrom et al. **ICLR 2020** arXiv:2005.12729.
- ⚠ **THE reward-scale confound, in the authors' own words (VERIFIED):** SAC paper §5 — reward scale "serves
  the role of the temperature… and thus controls its stochasticity"; it is "the only hyperparameter that
  requires tuning." Small scale → near-uniform policy (under-exploits); large scale → near-deterministic
  (poor optima). Because your arms author different-scale rewards and SB3 runs `ent_coef="auto"`, the
  effective entropy regularisation differs by arm — **name the mechanism, present PopArt as the principled
  mitigation, disclose the residual, and report the σ_max table + popart=False ablation.**
- **ADD 5 missing refs to refs.bib:** haarnoja2019applications, kuznetsov2020tqc, vanhasselt2016popart,
  raffin2021sb3, engstrom2020implementation.

### C.13 Reward design THEORY (the intellectual license) + reward hacking
- **Optimal Reward Problem (the license to design a reward that beats the true objective for a BOUNDED
  agent):**Singh-Lewis-Barto 2009 "Where Do Rewards Come From?" **CogSci 2009**pp.2601–2606 (cite **2009**);
  Sorg 2011 PhD thesis (UMich) — "one reward confounds defining preferences and guiding behaviour"; Sorg-
  Singh-Lewis 2010 "Internal Rewards Mitigate Agent Boundedness" **ICML 2010** + "Reward Design via Online
  Gradient Ascent" **NeurIPS 2010** (two distinct papers). **Lead the justification with Sorg's bounded-agent
  framing — your SAC agent is bounded/undertrained, so a designed reward is licensed.**
- Ng-Harada-Russell 1999 **ICML 1999** (potential-based shaping invariance — cite for the concept, but DON'T
  conflate with PopArt's value-target invariance); Skalse et al. **NeurIPS 2022** arXiv:2209.13085 (⚠ arXiv
  title "Reward Hacking" vs proceedings "Reward Gaming" — note both); Pan-Bhatia-Steinhardt **ICLR 2022**
  arXiv:2201.03544 (more-capable agents hack more — phase transitions); Krakovna et al. 2020 + Clark-Amodei
  2016 + Amodei et al. 2016 arXiv:1606.06565 (motivation; the first two are blogs — cite with access date).

### C.14 CVaR time-inconsistency (high-probability Okhrati attack)
- **Attack:** Boda-Filar 2006 *MMOR* 63(1):169–186 DOI 10.1007/s00186-005-0045-1 (CVaR need not be
  time-consistent); Lim-Malik **NeurIPS 2022** (the RL-native statement: optimal static-CVaR policy is
  non-Markovian; naive nesting converges to neither object). **Defence:** the static tail is *designer
  feedback, not a nested risk-to-go*— Artzner et al. 2007 / Ruszczyński 2010 / Shapiro 2009,2012 constrain
  recursive Bellman risk mappings you never perform; the policy stays Markov; static CVaR is the *more
  interpretable*practitioner object (Moghimi-Ku 2025 arXiv:2501.02087) and is a studied objective (Tamar
  et al. AAAI 2015; Chow et al. NeurIPS 2015; Bäuerle-Ott 2011 — Markov-optimal via state augmentation,
  which you deliberately don't need). **Pre-empt this in one paragraph.**

---

## D. EXAMINER ALIGNMENT — Dr Ramin Okhrati (supervisor / likely first marker)
- Mathematician-first (PhD applied probability; quadratic hedging, non-smooth Itô, coherent risk), moved
  into offline/risk-sensitive RL-in-finance; founder UCL-AIRiskLab; Bank of England collaboration.
- **Two scrutiny zones:** (a) theorem-level rigour on risk measures / stochastic finance — get CVaR/ES
  definitions, coherence, and the **non-smooth/kinked** nature of ES exactly right; (b) applied offline/
  risk-sensitive RL.
- **Cite (confirmed his):** Khraishi-Okhrati 2022 ICAIF '22 DOI 10.1145/3533271.3561682 (offline deep RL,
  **CQL** — your prototype's family; **it is consumer-credit pricing, NOT portfolio — frame as offline-RL
  methodology + supervisor lineage, not a portfolio baseline**); Khraishi-Okhrati 2023 noisy-env-augmentation
  arXiv:2305.02882; **Hartley et al. 2025 ACL Findings "How Personality Traits Shape LLM Risk-Taking"
  arXiv:2503.04735**(his own LLM×risk bridge — legitimises your premise); Okhrati-Schmock 2015 (non-smooth
  Itô — cite when invoking non-smoothness of risk functionals); Garrido-Okhrati 2018 *Risks* 6(1):23
  (risk-measure-dependent portfolios — supports H2's "which risk functional the reward encodes").
- **Alignment moves:** frame H2 as "which risk functional the reward encodes" (his sensibility); treat ES
  with full rigour; position offline/conservative training against his CQL paper; foreground the LLM-risk
  angle with his 2025 paper. ⚠ **Do NOT attribute elicitability/EVT to him** (not his area — he'd catch a
  misattribution); verify ORCID; don't cite the unconfirmed hedging arXivs as his.

---

## E. GRADING RUBRIC → ENGINEERING TARGETS (UCL-verified descriptors)
- **Hard gates (UCL CS Scheme of Award):** Distinction needs overall ≥70 **AND dissertation ≥70 AND no mark
  <50**. Dissertation = 1/3 of degree, **double-marked, non-condonable**. It is both a gate and the
  highest-leverage artifact.
- **86–100 band (verbatim):** *"of publishable quality… would receive that judgement if submitted to a
  peer-reviewed journal… clearly highly capable of doctoral research"*; *"analysis of such originality as to
  potentially change conventional understanding"*(LSE); *"reads as if professionally copy-edited"*(UCL CS).
- **The 70→80→90 ladder:** 70s = sound + your own analysis; 80s = distinctive + a novel/creative move +
  excellent critical synthesis + best-practice rigour (significance tests, ablations, robustness); 90+ =
  publication-grade synthesis + sophisticated conceptual framework + flawless craft.
- **Highest-leverage 90s moves:** (1) make the publishability claim literally true (write it as a journal
  paper); (2) lead with critical literature *synthesis* (use the B.1 taxonomy ladder); (3) surface the
  evaluation rigour and tie each guard to a named failure mode (rliable/PBO/DSR/IUT/placebo); (4)
  replicability + validation as first-class (freeze SHA, configs, seeds); (5) structured honest limitations;
  (6) flawless citation/figure craft; (7) a one-sentence quotable contribution statement.
- **What caps strong theses below Distinction:** description-not-analysis (#1 mark-loser); over-claiming
  beyond evidence (the live risk for a null — calibrate every claim); thin evaluation; scope drift; surface
  errors (read as sloppy thinking).

---

## F. PUBLICATION PLAN (for a pre-registered, likely-null, single-instance result)
1. **NeurIPS/ICAIF finance WORKSHOP** (non-archival, "preliminary/under-review work welcome") — fastest,
   null-friendly, gives feedback + a venue line. Watch the **ICAIF'26 Milan** workshop round (~Sep–Oct 2026)
   and the NeurIPS'26 GenAI-in-Finance equivalent (~Aug–Sep 2026).
2. **TMLR** — acceptance = *"claims supported by convincing evidence"* + *"some audience interested"*;
   **explicitly drops novelty/SOTA** → a well-evidenced null passes by design. Archival, indexed, certified.
   The best "publishable" anchor for the grade descriptor. (Workshop → TMLR ordering keeps the non-archival
   rule clean.)
3. **ICAIF'26 main** (deadline **Aug 2, 2026**; **8 pages incl. refs, NO appendix, no rebuttal**) — only with
   a positive sub-finding or a sharply-characterised boundary condition. Plan the write-up to 8pp with an
   arXiv/OSF companion for the pre-registration + reward code from day one.
- **arXiv (cs.LG + q-fin.PM) first** — citable artifact; all targets permit prior arXiv. Position explicitly
  vs Eureka. Scope every claim to the single instance (the universal rejection mode is over-generalisation).

---

## G. CITATION-INTEGRITY MASTER FLAGS (these are the ones that get caught)
1. **Acerbi 2002 (spectral, …281-9) ≠ Acerbi-Tasche 2002 (ES coherence, …283-2)** — distinct, same JBF issue.
2. **Kusuoka 2001 = Advances in Math. Economics Vol.3**, not RIMS Kokyuroku.
3. **PBO/CSCV = JCF 2017 20(4):39–69 (Bailey-Borwein-LdP-Zhu)**; **PSR = J.Risk 2012**; **DSR = JPM 2014
   (Bailey & LdP only)**— three different papers; don't merge or mis-author. No DOIs on the risk.net ones
   (use SSRN/RePEc; never invent a DOI).
4. **FZ-2016 (theorem, AoS, has Erratum) ≠ FZG-2015 (DM-backtest note, arXiv) ≠ FZ0 (Patton-Ziegel-Chen
   2019).**Don't conflate.
5. **−30% = Shumway 1997 (NYSE/AMEX); −55% = Shumway-Warther 1999 (NASDAQ); rule = BMP 2007.**
6. **BAB = 2014 (JFE), QMJ = 2019 (RAS), HLZ title starts with an ellipsis** ("… and the Cross-Section").
7. **BH vs BY under dependence** — state PRDS-BH or BY-inflation explicitly.
8. **Skalse: "Reward Hacking" (arXiv) vs "Reward Gaming" (NeurIPS proceedings).**
9. **QR-DQN = 2018 (AAAI)**, not 2017; **FunSearch = Nature 2024**; **Sood = 2023 FinPlan** (ignore the 2602
   arXiv re-post); **DSAC (risk) = Ma et al. JAIR**, disambiguate from autonomous-driving DSAC.
10. **Don't cite Okhrati for elicitability/EVT.** **Rockafellar-Uryasev 2000 has no DOI.** **REVSTAT has no
    DOI.****Krakovna/Clark-Amodei are blogs.****Nie et al. & "Reward Is Enough" are workshop/preprint.**
11. **2026 arXiv ids (MadEvolve 2605.23007, RF-Agent 2602.23876, Heavy-Tails-DM 2605.16866, etc.) are
    venue-unverified**— re-sweep ~2 weeks before submission; mark "concurrent/under review."

---

## H. NEW THREATS / LIMITATIONS the sweep surfaced (add to the limitations register)
- **Heavy-tailed DM-test size distortion** (arXiv:2605.16866): your FZ0/ES corroboration may be oversized if
  the loss-differential has infinite variance — check the tail index; HLN does not fix this.
- **CSCV/PBO known bias regimes** (Witzany 2021): negatively biased near zero-mean (your near-null tail
  channel sits there) — disclose + cross-check PBO vs DSR.
- **DSR effective-N under correlated trials** — the documented soft spot; justify your independent-trial count.
- **EVT CVaR finite-sample bias on ~750 points** (Belzile-Davison 2020; Giles 2016; Cont 2010) — bound it;
  consider a bootstrap RMSE on the fitted GPD rather than borrowing a number.
- **SAC reward-scale ⇒ effective-entropy confound** (Haarnoja §5) — the σ_max table + popart=False ablation
  are now *must-haves*, not optional.
- **Static-CVaR time-inconsistency** (Boda-Filar; Lim-Malik) — pre-empt with the designer-feedback defence.
- **LLM numeracy** (numeracy-gap cluster) — frame NEGATIVE responsiveness as semantic-vs-magnitude editing,
  scoped to a frontier model.
- **Single Claude family / single universe** — the universal "over-generalisation" rejection mode; scope all
  claims; disclose.

---
---

# PART II — ADVANCED / SOPHISTICATION LAYER (20-scout deep sweep, 2026-06-26)

Theorem-level, frontier, and cross-disciplinary depth beyond Part I. Purpose: lift the dissertation from
high-Distinction to *publishable / doctoral-capable* (the verified 86–100 band) and bulletproof it against an
expert's subtlest objections. **Headline: many of these enable concrete NEW analyses computable on data already
on disk (the 239 archived reward programs + the winner-seed-ladder × arm matrix — Amendment E1; tiers to n=568, primary target 403) with NO new compute**— see §M. All cites
verified-vs-snippet tagged; new integrity flags in §N.

## I. THEORY PILLARS — three deep, rigorous foundations for the contribution

### I.1 Pillar A — Comparison of experiments (makes the dominance claim a *theorem*, not a hand-wave)
The central claim ("an optimal user of the tail vector weakly dominates an optimal user of a scalar") is exactly
the **Blackwell–Sherman–Stein (BSS)** theorem: because the scalar is a *measurable reduction* `f` of the tail
vector, `E_scalar = f∘E_vec` is a **garbling** of `E_vec`, hence weakly dominates it **for every loss and prior**.
- **Blackwell 1953** "Equivalent Comparisons of Experiments" *Ann. Math. Stat.* 24(2):265–272, DOI
  10.1214/aoms/1177729032 [VERIFIED] — uses the word "garble"; the general-state-space primary. Pair with
  **Blackwell 1951** (2nd Berkeley Symp., pp.93–102) + **Blackwell–Girshick 1954** (book) + **Sherman 1951**
  *PNAS* 37(12):826–831 (the "S"; Stein's contribution is *unpublished*, cite as attributed in Blackwell 1953).
- **Quantitative sharpening — Le Cam deficiency:** **Le Cam 1964** "Sufficiency and approximate sufficiency"
  *Ann. Math. Stat.* 35:1419–1455, DOI 10.1214/aoms/1177700372 [VERIFIED] + **Le Cam 1986** book Thm 2 p.20;
  **Torgersen 1991** *Comparison of Statistical Experiments* (CUP, DOI 10.1017/CBO9780511666353); **Strasser
  1985**(De Gruyter, Ch.9). Deficiency δ(E_scalar,E_vec) **uniformly bounds the excess risk**of the scalar
  over any bounded loss — converts binary dominance into "dominates, with a worst-case price δ."
- **Sophistication move:** state the claim as a **two-line theorem + quantitative corollary** (BSS dominance +
  Le Cam-deficiency excess-risk bound). Disclose honestly: BSS bounds the *attainable* risk (optimal user),
  while SAC is a *fixed, suboptimal* decision rule — so the gap "optimal-user-of-tail vs what-SAC-extracts" is
  itself the empirical question.

### I.2 Pillar A′ — Information theory (the *same* theorem in a second language → "bilingual" rigor)
The information-theoretic twin: a scalar = (stochastic) channel applied to the tail vector ⇒ by the **Data-
Processing Inequality**it cannot increase any f-divergence between good-tail and bad-tail return laws, with
**strict** loss unless the scalar is a *sufficient statistic*.
- **Polyanskiy–Wu 2024/25** *Information Theory: From Coding to Learning* (CUP, ISBN 978-1-108-83290-8) [VERIFIED
  full draft] — Thm 7.4 (DPI for f-divergences), Thm 2.17/3.9 (equality ⇔ sufficiency), Fisher-info DPI. The
  four load-bearing results. **Liese–Vajda 2006** *IEEE Trans. IT* 52(10):4394–4412 DOI 10.1109/TIT.2006.881731;
  **Raginsky 2011** ISIT (welds Blackwell↔Le Cam↔DPI — the "bilingual" anchor); **Csiszár**/**Chentsov 1982**
  (Fisher metric is the unique monotone-under-garbling metric — a uniqueness capstone).
- **Sophistication move:** prove the dichotomy (good-tail P vs bad-tail Q) *two ways* — decision-theoretic (BSS
  garbling) and information-theoretic (DPI) — and cite Raginsky/Liese–Vajda that for a dichotomy these are the
  *same theorem*. ⚠ A finite CVaR vector is sufficient for the spectral class only in the limit/sub-class —
  phrase via deficiency (approximate sufficiency), don't assert exact sufficiency.

### I.3 Pillar A″ — Information economics (elevates it from RL plumbing to an information-value claim)
- **Cabrales–Gossner–Serrano 2013** "Entropy and the Value of Information for Investors" *AER* 103(1):360–377,
  DOI 10.1257/aer.103.1.360 [VERIFIED] — **the bridge**: ties an information measure to the value of information
  for a *ruin-averse, no-arbitrage portfolio investor* — almost exactly your risk-sensitive setting. **Blackwell
  1951/1953**(econ statement); **Kamenica–Gentzkow 2011***AER*101(6):2590–2615 (Bayesian persuasion — the
  "what to put in the channel" framing); **Frankel–Kamenica 2019** *AER* 109(10):3650–3680; **Athey–Levin 2018**
  *Res. Econ.* 72(1):101–116; Hirshleifer–Riley textbook. ⚠ CGS ordering is *complete but prior-dependent*
  (opposite trade-off to Blackwell's *partial but prior-free*) — state which you invoke.

### I.4 Pillar B — Elicitability / sufficiency of the fed vector (Okhrati's deepest-scrutiny zone)
The fed signal is a *jointly identifiable + elicitable, hence sufficient, finite representation of the lower tail*.
- **Fissler–Ziegel 2016** *Ann. Stat.* 44(4):1680–1707 DOI 10.1214/16-AOS1439 **Corollary 5.5** [VERIFIED] —
  a finite-support spectral measure (a multi-level ES/CVaR mixture) + its quantiles is **(k+1)-elicitable**.
  MUST pair with the **2021 correction note** *Ann. Stat.* 49(1):614, DOI 10.1214/20-AOS2014 (+ arXiv:1901.08826).
  **Fissler–Liu–Wang–Wei 2025** *Math. Finance*, DOI 10.1111/mafi.70016 (arXiv:2404.14136) — newest generator
  framework, generalizes to the whole tail class. **Frongillo–Kash 2021** *Biometrika* 108(4):857–879 (elicitation
  complexity ≤ k+1). **Ziegel 2016** *Math. Finance* 26(4):901–918 + **Bellini–Bignozzi 2015** *Quant. Finance*
  15(5):725–733 (expectiles are the ONLY elicitable coherent measure ⇒ *why you must feed a vector*). Acerbi–
  Székely 2017 (backtestability necessary conditions); Nolde–Ziegel 2017 (comparative backtesting).
- **Sophistication move:** carry the three distinctions **identifiability vs elicitability vs backtestability**
  explicitly — pre-empts the "but ES isn't elicitable" objection by showing you mean *higher-order joint*
  elicitability. Exactly the depth Okhrati rewards.

### I.5 Pillar C — CVaR = Distributional Robustness (a SECOND theory pillar, orthogonal to coherence)
- **Chow–Tamar–Mannor–Pavone 2015** NeurIPS pp.1522–1530 (arXiv:1506.02188) [VERIFIED verbatim] — Eq.(2):
  `CVaR_α(Z)=max_{ξ∈U} E_ξ[Z]`, density bounded by 1/α (a φ-divergence ball); **Prop.1**: minimizing CVaR =
  worst-case expected return under *budgeted perturbations of the transition kernel*. **The exact bridge: feeding
  the tail = feeding a distribution-shift-robustness signal — which is precisely what the sealed-OOS test
  measures.**Support: Ben-Tal et al. 2013 *Mgmt Sci* 59(2):341–357; Duchi–Namkoong 2021 *Ann. Stat.*
  49(3):1378–1406; Esfahani–Kuhn 2018 *Math. Prog.* 171:115–166 (Wasserstein DRO); Nilim–El Ghaoui 2005 / Iyengar
  2005 (robust MDPs); Föllmer–Schied (coherent = sup of expectations — the supervisor-facing parent).
- **Sophistication move:** add a two-line dual-interpretation paragraph ("the tail-aware reward is a robustness
  signal") — a second deep pillar answering "why CVaR" at the level a math-finance examiner rewards.

### I.6 Pillar D — Reward-distance geometry (turns "is the reward actually different?" into a measurement)
- **STARC** (Skalse et al., **ICLR 2024**, arXiv:2309.15257) — a reward pseudometric that **both upper- and
  lower-bounds worst-case regret**(provably tight, essentially unique); VAL canonicalisation needs only sampling.
  **EPIC** (Gleave et al., **ICLR 2021**, arXiv:2006.13900) — the cheaper Pearson-distance predecessor. Skalse
  et al. **ICML 2023** (arXiv:2203.07475) — *partial identifiability* (many rewards → same optimal policy ⇒ why
  reward design is non-trivial). Ng–Harada–Russell 1999 (potential-shaping invariance — your non-invariant LLM
  rewards are exactly the policy-changing class). Knox et al. AIJ 2023 (8 reward-sanity checks).
- **Sophistication move (BUILDABLE, no retrain):** compute the **EPIC + STARC distance matrix** over the 239
  archived reward programs — intra/inter-arm + distance-to-canonical-human-reward. Small distance ⇒ the arm is
  near-policy-invariant *shaping* (a null-supporting signal); large ⇒ a genuinely distinct objective. Directly
  answers the dissertation's central question with a regret-bounded number.

## J. INFERENCE & DESIGN SOPHISTICATION

### J.1 Construct validity (rename your controls in examiner vocabulary, zero engineering cost)
- **Shadish–Cook–Campbell 2002** (ISBN 0-395-61556-9) — four validity types + named threats (mono-operation/
  mono-method bias; confounding construct with levels). **Hauser–Ellsworth–Gonzalez 2018** *Front. Psychol.*
  9:998, DOI 10.3389/fpsyg.2018.00998 [VERIFIED] — your responsiveness probe + reward-program differential **are
  behavioral manipulation checks**(the *superior* non-verbal class). Sigall–Mills 1998; Campbell–Stanley 1963.
- **Sophistication move:** a "Construct Validity of the Manipulation" subsection mapping placebo / scalar_cvar5 /
  shuffled-placebo one-to-one onto named SCC threats. ⚠ Montgomery DOE cuts both ways (OFAT can't detect
  agent×feedback interaction) — frame single-factor isolation on causal-cleanliness grounds + disclose the
  un-probed interaction space.

### J.2 Causal mediation (gives the mechanism chapter a real causal spine; rescues the negative responsiveness)
T = fed-tail arm; **M = the authored reward code**; Y = realized performance. Responsiveness = the **indirect
effect T→M→Y**; the negative prototype finding = **inconsistent mediation / suppression**, a recognized estimand.
- **Imai–Keele–Yamamoto 2010** *Stat. Sci.* 25(1):51–71 DOI 10.1214/10-STS321 (ACME identification + ρ
  sensitivity) [VERIFIED]; **Imai–Keele–Tingley 2010** *Psych. Methods* 15(4):309–334 (`mediation` R pkg);
  **VanderWeele 2015/2016** (NDE/NIE); **O'Rourke–MacKinnon 2018** *JSAD* 79(2):171–181 [VERIFIED] — *the* cite
  that a null total effect with a tested mechanism is a research imperative; MacKinnon–Krull–Lockwood 2000
  (suppression = inconsistent mediation); Smith–VanderWeele 2019 (mediational E-value); Pearl 2001 (front-door).
- **Sophistication move (BUILDABLE):** formalize responsiveness as the ACME/NIE through the reward-code mediator;
  report a **dual sensitivity analysis** (ρ + mediational E-value); interpret the negative NIE as
  suppression. ⚠ sequential ignorability is strong/untestable — state it + run the sensitivity analyses.

### J.3 Bayesian evidence FOR the null (positive evidence, not "failure to reject")
- **Dienes 2014** *Front. Psychol.* 5:781, DOI 10.3389/fpsyg.2014.00781 [VERIFIED] — *natively about your
  problem*; thresholds B<1/3 (H0), B>3 (H1), between = **"data insensitive"** (the honest third category =
  reputational insurance). **Rouder et al. 2009** *PBR* 16(2):225–237 (JZS Bayes factor); **Kruschke–Liddell
  2018***PBR*25(1):178–206 (ROPE+HDI — cite THIS for ROPE, not the 2013 BEST paper); Kass–Raftery 1995;
  **Mayo 2018** *Statistical Inference as Severe Testing* + **Mayo–Spanos 2006** *BJPS* 57(2):323–357 (severity —
  a null that passes a severe test is corroborated); Schad et al. 2023 *Psych. Methods* 28(6):1404–1426 (BF prior-
  robustness). Benavoli et al. 2017 *JMLR* 18(77) (Bayesian classifier comparison).
- **Sophistication move (BUILDABLE):** a triangulated, pre-registered, prior-robust null — **BF01 + ROPE-in-HDI +
  TOST**, each SESOI-keyed, with a BF prior-sensitivity sweep, all framed under **severity**. Three convergent
  positive-evidence statements from three statistical philosophies = the move that makes a null *publishable*.

### J.4 Selective / anytime-valid inference frontier (signals frontier awareness)
- **Andrews–Kitagawa–McCloskey 2024** "Inference on Winners" *QJE* 139(1):305–358, DOI 10.1093/qje/qjad043 —
  **the exact formalization of your design** (select best reward per arm → infer on the winner); certifies your
  sealed-leg/held-out split as the canonical **winner's-curse remedy**. **Wang–Ramdas 2022** e-BH *JRSS-B*
  84(3):822–852 (FDR under *arbitrary dependence*, no BY penalty); **Ren–Barber 2024** derandomized knockoffs
  (the principled fix for run-to-run selection variability); Ramdas et al. 2023 SAVI (anytime-valid for the
  *sequential reflective search*); Barber–Candès 2015 / Candès et al. 2018 (knockoffs); Berk et al. 2013 (PoSI).
- **Sophistication move:** a "Why BH+IUT, and the frontier alternatives" subsection — name e-BH / derandomized
  knockoffs / inference-on-winners, map each to your design, justify BH+IUT as the pre-registered conservative
  choice. *Informed* choice, not default.

### J.5 Hierarchical Bayesian re-analysis (a complement to rliable; multiplicity by construction)
- **Gelman–Hill–Yajima 2012** *JREE* 5(2):189–211, DOI 10.1080/19345747.2011.618213 — partial pooling controls
  multiplicity *at the modeling stage* (a principled contrast to BH+IUT). **Longjohn–Gopalan–Casleton 2025**
  (arXiv:2501.04234, NeurIPS'24 wkshp) — near-drop-in HBM template for ML-benchmark metrics, explicit "HBM-vs-
  bootstrap" framing. Gelman–Hill 2007; BDA3 2013; Bayesian Workflow 2020; Makowski et al. 2019 (Probability of
  Direction).
- **Sophistication move (BUILDABLE):** a varying-intercepts model over (arm, seed) on per-seed Sharpe/CVaR-5%;
  report the tail-channel contrast as a posterior credible interval + Probability of Direction; PPC on per-seed
  dispersion directly addresses the undertraining/critic-noise concern.

### J.6 Model Confidence Set + conditional predictive ability (reframes the whole results chapter)
- **Hansen–Lunde–Nason 2011** "The Model Confidence Set" *Econometrica* 79(2):453–497, DOI 10.3982/ECTA5771
  [VERIFIED] — takes the loss matrix you already have, returns "the 90% MCS of the 9 arms is {…}", **natively
  family-wise-error-controlled (retires the conjunction-BH double-correction worry)**. ⚠ use the **range statistic
  T_R**only (a corrigendum withdrew T_max). **Giacomini–White 2006***Econometrica*74(6):1545–1578 (conditional
  predictive ability — regime-by-regime, preserves estimation error); West 1996; Hansen SPA 2005; Diebold 2015
  (forecast-vs-model distinction — the self-defense cite); Corradi–Swanson 2006 (predictive *density* eval — for
  the distributional arms).
- **Sophistication move (BUILDABLE):** report the arm comparison as an **MCS** under each co-primary loss + layer
  Giacomini–White conditioning on a crisis indicator. Reframes "A beats B" into rigorous set-selection.

## K. EMPIRICS REALISM (bulletproofs the data/results chapters)

### K.1 Regimes / structural breaks (pre-empts "your result is regime-specific")
- **Hamilton 1989** *Econometrica* 57(2):357–384 (Markov-switching, endogenous regime dating); **Bai–Perron
  1998***Econometrica*66(1):47–78 + **2003***J. Appl. Econometrics* 18(1):1–22 (multiple breaks, tested, with
  CIs on break dates). Ang–Bekaert 2002 *RFS*; Guidolin–Timmermann 2007 *JEDC*; Pettenuzzo–Timmermann 2011
  *J. Econometrics* (+2022 corrigendum); Ang–Timmermann 2012 *Ann. Rev. Fin. Econ.* (instability-is-risk framing).
- **Sophistication move (BUILDABLE):** a pre-registered **regime-conditional tail-channel breakdown** dated by
  *two independent methods* (Markov-switching + Bai–Perron) with a Wald/Chow cross-regime equality test. If the
  effect concentrates in the crisis regime, that is the *strongest* result for a tail-aware reward (it fires when
  tails matter); if stable, that is external-validity evidence. Either way it is rigor. ⚠ Pesaran–Timmermann 2002
  title is "...return **Prediction**..." not "predictability".

### K.2 Transaction costs / market impact (makes the cost-fairness defense unkillable)
- **Almgren et al. 2005** "Direct Estimation of Equity Market Impact" (*Risk*) [VERIFIED equations] — fitted
  γ=0.314, η=0.142; a 10%-of-ADV large-cap trade ≈ 18–43 bps realized; **temporary impact ∝ (rate)^{3/5}** (NOT
  √). **Frazzini–Israel–Moskowitz 2018** (SSRN 3229719) [VERIFIED] — real institutional cost ≈ **6 bps median**,
  and a "**coefficient close to ½ → square-root**" on live data. Gatheral 2010 (no-arbitrage → square-root needs
  power-law decay); Kyle 1985 (linear λ, the small-order case); Korajczyk–Sadka 2004 (capacity/break-even
  template); Almgren–Chriss 2000 (the 3-component decomposition).
- **Sophistication move (BUILDABLE):** replace/stress flat bps with the **empirical square-root impact law**
  `cost = Y·σ·√(turnover/ADV_frac)`, sweep Y∈{0.5,0.75,1.0} + a participation cap; report each arm under flat /
  square-root / square-root+half-spread. Bulletproofs baseline-fairness + the daily-RL **rebalancing-frequency
  tax**+ capacity at once. ⚠ FIM's 6 bps is AQR's *optimized/sliced* execution — a daily-rebalancing RL agent
  does not get it; disclose the execution-style gap.

### K.3 Action-space limitation (turns "softmax can't flee to cash" into a cited design decision)
- **Gao–Pavel 2017** (arXiv:1704.00805) — softmax image is the **open** simplex ⇒ an exact cash corner is
  provably unreachable (the formal statement of your limitation). **Xue–Ye 2025** (arXiv:2510.06466) — names your
  exact softmax+projection design + its failure modes + the Dirichlet alternative (cash as coordinate-0 for risk
  budgeting). Winkel et al. 2024 (simplex decomposition); André–Coqueret 2020 (Dirichlet policy, closed-form
  gradients); Dalal et al. 2018 (safety layer); Achiam et al. 2017 (CPO); Chow et al. 2017 (CVaR-constrained RL).
- **Sophistication move (BUILDABLE, no retrain):** reframe as a ranked 3-axis design menu (softmax-interior /
  Dirichlet-by-construction / differentiable-projection), cite it, then add **one diagnostic** — how close to the
  cash corner the trained policy gets in worst tail states. If risky-weight→~0 in stress, the open-simplex limit
  is empirically *non-binding*.

## L. FRONTIER FRAMING & ROBUSTNESS

### L.1 Automated-discovery framing (inherits Nature/DeepMind/Sakana prestige; names the open niche)
- **Sakana AI-Scientist** (Lu et al. 2024 arXiv:2408.06292; v2 Yamada et al. 2025 arXiv:2504.08066); **FunSearch**
  (Nature 625, 2024); **AlphaEvolve** (DeepMind 2025, arXiv:2506.13131); **survey** Zheng et al. 2025
  (arXiv:2505.13259, EMNLP'25) — Tool→Analyst→Scientist taxonomy, **explicitly notes no pre-registered/controlled
  protocols exist**in the discovery line. Hypothesis-generation survey arXiv:2504.05496 (LLMs more novel, less
  valid).
- **Sophistication move (intro sentence):** "We treat LLM-authored reward code not as reward engineering but as
  an instance of *automated discovery of objective functions* — the FunSearch/AlphaEvolve/AI-Scientist paradigm —
  and supply what that line conspicuously lacks: a **pre-registered, controlled evaluation with falsifiable
  hypotheses**, not a demonstration." Makes the pre-registered null the *headline rigor differentiator*. ⚠ all
  discovery systems are author-validated demos; don't misattribute a pre-registration claim to any.

### L.2 Quality-Diversity (deepens H4 + a buildable reward-search diversity analysis)
- **Pugh–Soros–Stanley 2016** *Front. Robotics & AI* 3:40, DOI 10.3389/frobt.2016.00040 [VERIFIED] — QD-score,
  coverage, k-NN novelty, behavior characterization (the formulas). Lehman–Stanley 2011 (novelty search;
  objectives can be *deceptive*); Mouret–Clune 2015 (MAP-Elites); Cully et al. 2015 (Nature). LLM-evolution
  precedents: **ELM** (Lehman et al. 2022, arXiv:2206.08896); **QDAIF** (Bradley et al., ICLR 2024,
  arXiv:2310.13032). FunSearch's island model = a diversity-maintenance mechanism your reflect-on-best loop lacks
  (a precise, citable limitation).
- **Sophistication move (BUILDABLE, the `tail_stats` are already logged):** a QD analysis over the 239 programs —
  behavioral descriptor = each program's induced `tail_stats` vector; report per-arm **coverage / QD-score** and a
  **k-NN novelty trajectory across generations** (does reflect-on-best collapse novelty vs flat random_search?).
  Turns the diversity *concern* into a measured *result*, with the missing island-model as the mechanism.

### L.3 Synthetic-null falsification (proves the result isn't a data-mining artifact — the right tool for an
implicit/unbounded LLM search that PBO/DSR can't fully deflate)
- **Nikolopoulos 2026** (arXiv:2604.15531) [VERIFIED, full template] — a falsification audit re-running the whole
  workflow on **5 induced-null DGPs** (IID; regime-switching; **microstructure/friction placebo**; factor null;
  GARCH) with a HAC-t gate, Bonferroni-across-nulls, and a `K_eff` effective-multiplicity formalism. Canon:
  **Theiler et al. 1992** *Physica D* 58:77–94 (surrogate-data paradigm); Schreiber–Schmitz 2000 (IAAFT
  surrogates); **Politis–Romano 1994** *JASA* 89(428):1303–1313 (stationary bootstrap — preserves vol clustering);
  White 2000 / Hansen 2005; López de Prado (Monte-Carlo backtesting).
- **Sophistication move (BUILDABLE):** a "Synthetic-Null Falsification" exhibit — re-run the full pipeline on
  IID-shuffle / stationary-block-bootstrap / IAAFT / GARCH null markets and show the tail-channel differential
  collapses inside the null band. PBO/DSR deflate a *known* trial count; the LLM reward-search has an
  *implicit/unbounded* one, so this is the *correct* tool — a genuine novelty hook. ⚠ Nikolopoulos is a fresh
  unrefereed preprint — anchor the section on the peer-reviewed canon (Theiler/Politis-Romano/White).

### L.4 Reproducibility + LLM non-determinism (turns the loop's weakest point into a cited strength)
- Artifacts: **Datasheets** (Gebru et al., *CACM* 64(12), 2021, DOI 10.1145/3458723); **Model Cards** (Mitchell
  et al., FAccT 2019); **Pineau et al. 2021** *JMLR* 22(164) (repro checklist); **REFORMS** (Kapoor–Narayanan et
  al., *Science Advances* 10(18), 2024 — leakage-focused, your genre). LLM non-determinism: **Chen–Zaharia–Zou
  2023**(arXiv:2307.09009, model-version *drift*); **Yuan et al. 2025**(arXiv:2506.09501 — FP non-associativity
  ⇒ up to 9% accuracy / 9,000-token variation on GPUs; the peer-reviewed-grade evidence); Thinking Machines blog
  (batch-invariance mechanism — cite alongside Yuan, it's a blog); Fu et al. 2026 (token-prob non-determinism).
- **Sophistication move:** a "Provenance & Replay" subsection separating **(a) computational reproducibility** of
  the analysis (deterministic; your byte-identical equivalence proof IS the guarantee) from **(b) LLM-generation
  reproducibility**which is *provably* impossible (cite drift + numerical). Design contract: "archive at
  generation, replay not regenerate." Reframes the weakest point as a literature-grounded engineered strength.

### L.5 The rhetoric of a publishable null (the highest-leverage WRITING move)
- **Dacrema et al. 2019** RecSys (arXiv:1907.06902) — "Are We Really Making Much Progress?" (simple tuned
  baselines beat the fancy method — your rhetorical north star); **Henderson et al. 2018** AAAI (variance makes
  claimed gains uninterpretable — your domain); **Lucic et al. 2018** NeurIPS ("Are GANs Created Equal?" — wins
  come from compute/tuning, the matched-budget precedent); Melis et al. 2018 ICLR; Recht et al. 2019 ICML
  (boundary-condition framing); Sculley et al. 2018 ("science is knowledge, not wins"); **Kerr 1998** (HARKing —
  cite next to your pre-registration); Kapoor–Narayanan 2023 *Patterns* (leakage crisis); the NeurIPS **ICBINB**
  negative-results workshop (a real venue + genre legitimizer).
- **Sophistication move:** write the abstract's result sentence in the Lucic/Dacrema two-clause cadence — *"Under
  a pre-registered, matched-budget, leakage-controlled protocol, LLM-designed reward code does not outperform a
  well-tuned human baseline …; apparent advantages elsewhere are consistent with [budget/tuning/leakage]. We
  establish a boundary condition and a reusable protocol."*Lead with methodology-as-contribution; cite Kerr for
  no-HARKing.

## M. THE SOPHISTICATION MOVES — actionable register (★ = buildable on data already on disk, NO new compute)

| # | New analysis / section | Cite anchor | Grade lever |
|---|---|---|---|
| 1★ | **Reward-distance matrix (EPIC+STARC)** over 239 programs → "different objective vs just shaping" | STARC ICLR'24 | answers the central question with a regret-bounded number |
| 2★ | **QD reward-search diversity** (coverage/QD-score/novelty-over-generations) | Pugh 2016 | turns diversity concern → measured result; hardens H4 |
| 3★ | **Hierarchical Bayesian re-analysis** (arm,seed) + Probability of Direction | Gelman-Hill-Yajima 2012 | multiplicity-by-construction; robustness to BH+IUT |
| 4★ | **Model Confidence Set** of the 9 arms | Hansen-Lunde-Nason 2011 | family-wise-controlled set; retires conjunction-BH worry |
| 5★ | **Triangulated null**: BF01 + ROPE-in-HDI + TOST under severity | Dienes 2014, Mayo 2018 | makes the null *publishable* |
| 6★ | **Mediation analysis** of responsiveness (ACME + ρ + E-value) | Imai 2010, O'Rourke 2018 | causal spine; rescues the negative responsiveness |
| 7 | **Synthetic-null falsification** (re-run pipeline on null markets) | Theiler 1992, Nikolopoulos 2026 | proves not-a-mining-artifact; novelty hook |
| 8 | **Square-root transaction-cost** robustness sweep | Almgren 2005, FIM 2018 | unkillable cost-fairness defense |
| 9★ | **Regime-conditional breakdown** + cross-regime equality test | Hamilton 1989, Bai-Perron 1998 | pre-empts "regime-specific"; external validity |
| 10★ | **Construct-validity subsection** (arms → SCC threats; probes = manipulation checks) | Shadish-Cook-Campbell 2002 | examiner-vocabulary rigor, zero compute |
| 11 | **Theory ch.**: BSS-garbling + Le Cam-deficiency + DPI (bilingual) | Blackwell 1953, Polyanskiy-Wu | doctoral-grade rigor |
| 12 | **Theory ch.**: CVaR = DRO second pillar | Chow 2015 | answers "why CVaR" deeply |
| 13 | **Elicitability/sufficiency** of the fed vector (id ≠ elic ≠ backtest) | FZ 2016 Cor 5.5 | Okhrati's scrutiny zone |
| 14★ | **Provenance & Replay** subsection (det. analysis vs non-det. LLM) | Yuan 2025, Chen-Zaharia-Zou | turns weakest point into strength |
| 15★ | **Action-space diagnostic** (closeness-to-cash in tail states) + design-menu | Gao-Pavel 2017, Xue-Ye 2025 | cited design decision, not hand-wave |
| 16 | **"Why BH+IUT" frontier subsection** (e-BH / knockoffs / inference-on-winners) | Andrews 2024, Wang-Ramdas 2022 | frontier-awareness signal |
| 17 | **Null-rhetoric abstract** (Lucic/Dacrema cadence + Kerr no-HARKing) | Dacrema 2019, Kerr 1998 | highest-leverage writing move |

**Nine of seventeen (★) need no new training compute** — they are post-hoc analyses over the 239 archived programs
+ the winner-seed-ladder × arm matrix (Amendment E1; primary target 403) + the prose. That is the cheapest, fastest route from high-Distinction to publishable.

## N. NEW CITATION-INTEGRITY FLAGS (Part II)
- **FZ-2016 has a 2021 correction note** (*Ann. Stat.* 49(1):614) — pair it; Okhrati will expect it.
- **Stein's "Notes on comparison of experiments" is unpublished** — cite as attributed in Blackwell 1953; no DOI.
- **ROPE = Kruschke–Liddell 2018**, not the 2013 BEST paper (web routinely misattributes).
- **MCS: cite the range statistic T_R only** (a corrigendum withdrew T_max); DOI 10.3982/ECTA5771.
- **Almgren 2005 temporary impact is 3/5-power, NOT √**; FIM 2018 is the ½/square-root one — don't conflate.
- **Reward-hacking: arXiv "Reward Hacking" vs NeurIPS-proceedings "Reward Gaming"** (Skalse 2022) — note both.
- **STARC = ICLR 2024** (not arXiv-only); **EPIC = ICLR 2021**.
- **Royset 2025 SIAM Review survey is single-authored** (not Rockafellar & Royset).
- **Cabrales-Gossner-Serrano ordering is complete-but-prior-dependent** (vs Blackwell partial-but-prior-free) —
  state which you invoke or a math-finance examiner catches the equivocation.
- **O'Rourke–MacKinnon 2018 (JSAD)** is the null-total-effect paper — NOT Fairchild-MacKinnon (a near-miss).
- **Pesaran–Timmermann 2002** title is "...return **Prediction**...".
- **Fresh 2026 preprints** (Nikolopoulos 2604.15531; Heavy-Tails-DM 2605.16866; Fu 2601.06118; AI-Scientist-v2)
  are venue-unverified — cite as preprint, anchor load-bearing claims on peer-reviewed canon, re-sweep before
  submission.
- **Blogs** (Thinking Machines non-determinism; Krakovna/Clark-Amodei specification-gaming) — cite with access
  date, always alongside a peer-reviewed primary.
