# REFERENCES.md — citation bank with roles
One line per source: what it anchors in THIS project. Full bibliographic details verified at write-up.
VERIFY-flagged items must be checked against the primary PDF before citing in prose (CLAUDE.md R7).

## Method core
- **Ma et al. 2024, "Eureka", ICLR (arXiv:2310.12931)** — the loop: code-as-context, K=16×N=5, reward
  reflection, fitness/reward separation, snapshot pinning (gpt-4-0314), human-init & evolution ablations.
- **Xie et al. 2024, "Text2Reward", ICLR (2309.11489)** — dense reward code from env abstraction; iterative
  error-correction precedent.
- **DrEureka (Ma et al. 2024)** — safety-instruction-in-prompt precedent → our finance safety block.
- **LEARN-Opt (arXiv:2511.19355)** — "automated reward design is a high-variance problem; average candidate
  fails" → justifies multi-seed/multi-candidate + selection-aware inference.
- **"When LLM Reward Design Fails" (arXiv:2605.28918, 2026, preprint — VERIFY authors)** — failure taxonomy
  {reward flooding, semantic/API misunderstanding, weak shaping}; generation-variance decomposition → forensics chapter.
- **Benhenda 2025, "FinRL-DeepSeek" (2502.07393)** — closest prior art; LLM-as-SIGNAL into hand-written
  CVaR-PPO (CPPO). Contrast sentence lives in RELATED_WORK_WATCH. VERIFY exact CPPO equation from §Methods.

## Distributional & risk-sensitive RL
- **Dabney et al. 2018, IQN, ICML (1806.06923)** — quantile embedding (cos, 64), quantile-Huber κ=1,
  risk-sensitive policies via τ-distortion (CVaR: τ~U[0,α]). VERIFY N,N′ used in original experiments.
- **Non-Crossing Quantile Regression, NeurIPS 2020** — IQN crossing problem + fix → our sorting rule.
- **DSAC / DSAC-T (Duan et al., 2310.05858)** — distributional-SAC alternative baseline (cited, not built).
- **RAMAC (2510.02695)** — IQN critic + CVaR actor (offline, no LLM) — precedent we extend.
- **Coache & Jaimungal 2024, Math. Finance; Ruszczyński 2010** — static-CVaR time-inconsistency; we state
  the static choice + consequence explicitly (threat-assessment item #4).
- **Kusuoka 2001; Acerbi 2002; Artzner et al. 1999; Rockafellar & Uryasev 2000** — coherent/spectral risk
  theory: the feedback schema's justification.

## Portfolio RL environment & baselines
- **Sood, Papasotiriou, Vaiciulis, Balch 2023, ICAPS FinPlan (JPM)** — env template: state [(n+1)×T], T=60,
  softmax, differential-Sharpe reward, 5-seed walk-forward. (A 2026 arXiv re-post exists — cite the 2023 original.)
- **Jiang, Xu, Liang 2017 (1706.10059)** — EIIE, PVM/prev-weight injection, cash bias.
- **Moody & Saffell 2001 (IEEE TNN); Moody, Wu, Liao, Saffell 1998** — differential Sharpe (and downside-
  deviation variant): the canonical hand-designed baseline.
- **"Recursive Reward Aggregation" (2507.08537)** — documented inconsistency of differential-Sharpe
  approximation → why beating it is plausible; also a non-LLM competitor to acknowledge.
- **DeMiguel, Garlappi, Uppal 2009, RFS** — 1/N result + 50bps convention.
- **Ledoit & Wolf 2004 (Honey…)** — constant-correlation shrinkage MVO baseline.
- **Maillard, Roncalli, Teiletche 2010** — ERC risk parity baseline.

## Evaluation integrity
- **Bailey & López de Prado 2014 (JPM 40(5))** — DSR/PSR/MinTRL; expected-max-SR with Euler–Mascheroni.
- **Bailey, Borwein, López de Prado, Zhu — PBO via CSCV (J. Comp. Finance)** — S≥16 protocol.
- **López de Prado 2018, AFML** — purging, embargo, CPCV.
- **Ledoit & Wolf 2008, J. Empirical Finance** — robust Sharpe-difference test (block bootstrap 5, ~4999).
- **Benjamini & Hochberg 1995** — FDR across the comparison suite.
- **Arian et al. 2024 (KBS)** vs **walk-forward framework (2512.12924, preprint)** — CPCV-vs-WF debate:
  we run both (overfitting-control view + deployment-realism view).

## Data integrity
- **Ince & Porter 2006, JFR** — vendor screens ($1 prior price; >300% reversal); naïve-vendor inflation evidence.
- **Shumway 1997 JF; Shumway & Warther 1999 JF** — delisting corrections −30% / −55%.
- **Elton, Gruber & Blake 1996 RFS; Brown, Goetzmann & Ross 1995 JF** — survivorship-bias magnitudes (~0.9–1.4%/yr).
- **Hamilton 1989, Econometrica; Ang & Bekaert** — regime-switching foundations for the HMM design.
- **Gebru et al., "Datasheets for Datasets" (CACM)** — the datasheet appendix pattern.

## Reward hacking / forensics
- **Skalse, Howe, Krasheninnikov, Krueger 2022, NeurIPS (2209.13085)** — formal reward hacking/gaming
  (VERIFY final title wording) — forensics backbone.
- **Manheim & Garrabrant 2018** — Goodhart taxonomy; **Krakovna et al.** — specification-gaming corpus;
- **Karwowski et al., ICLR 2024 (2310.09144)** — Goodhart's law in RL.
- **Goodhart-in-finance bridge (alpha decay: McLean & Pontiff; factor crowding)** — OUR framing; sweeps
  found it unbridged — state as "to our knowledge".

## Supervisor-adjacent
- **Khraishi & Okhrati 2022 (arXiv:2203.03003)** — "Offline Deep RL for Dynamic Pricing of Consumer Credit"; the harm criterion. CORE PAPER #3. ⚠ The on-disk PDF prints NO ICAIF / no conference venue — do NOT cite "ICAIF 2022" until the published venue is confirmed externally (matches `paper/refs.bib`; supervisor-authored → citation-integrity critical).
- **Khraishi & Okhrati 2023 (2305.02882)** — noise augmentation (optional robustness flag).
- **Hartley, Hamill, Seddon, Batra, Okhrati, Khraishi 2025, ACL Findings** — LLM risk-taking behaviour.
- **Batra, …, Okhrati, …, Khraishi, Cowan 2025 (SSRN 5381584)** — UCL–NatWest LLM-agents review (positioning).
