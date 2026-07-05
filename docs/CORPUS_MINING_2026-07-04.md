# Corpus deep-mining — 20-agent full-text sweep, 2026-07-04

**What this is.** A user-requested full-text (not abstract) deep read of the entire 210-PDF literature corpus by
20 parallel agents (L1–L20), one disjoint slice each, mining for: methods/theorems to **cite-and-USE**, framings,
**novelty threats** to distinguish, **corrections** to our claims, fresh 2025-26 neighbours, and hooks to the
open questions from the 30-probe code sweep (reward-scale invariance, backtest look-ahead, equivalence testing,
EVT small-sample, mechanism/mediation, LLM numeracy). Cross-referenced against `refs.bib`,
`docs/LITERATURE_INTEGRATION_MAP.md`, `paper/01_LITERATURE_DOSSIER.md`, `RELATED_WORK_WATCH.md`.

**Landed:** L1–L7, L10, L11, L13, L14, L19 (**12 of 20**). Pending: L8, L9, L12, L15, L16, L17, L18, L20.

---

## ★ HEADLINE VERDICTS (cross-agent)

1. **Novelty is SAFE and, if anything, STRENGTHENED.** Every "machine designs the objective code" precedent read
   so far — Niekum GP-2010, Singh IMRL-2010, Sorg ORP, Gonzalez GLO-2019, Houthooft EPG-2018, Real AutoML-Zero-2020,
   Petersen DSR-2021, Co-Reyes EvolvingRL-2021, FunSearch, the Eureka family — searches/learns the objective under a
   **SCALAR fitness/feedback** signal. **None** uses a **multi-level TAIL feedback vector as the manipulated variable**,
   none is an **LLM authoring reward CODE for a downstream RL PORTFOLIO agent**, none is **pre-registered**. The
   repeated, powerful sharpening for CH2/abstract: *"prior reward/objective-code search uses a **scalar** fitness
   signal (Niekum 2010; Singh 2010; Gonzalez 2019; Eureka 2024); our manipulated variable is the **distributional
   richness of that signal** — a multi-level left-tail CVaR/ES vector vs a scalar."*

2. **Examiner alignment is a goldmine (L6).** Two of the examiner's own group's papers can be cited-and-USED to
   *predict our null* and anchor the mechanism — see the Examiner section.

3. **The null is theoretically well-grounded** by at least four independent corpus results (RU Gaussian collapse,
   Sorg intermediate-boundedness, PseudoMath compensation effects, Rowland CDRL mean-optimality) — see Null-anchors.

4. **The integration map + dossier are STALE** in several places (they list now-cited papers as "gaps"): reconcile.

---

## ★ refs.bib ADDITIONS (high-value gaps, with coordinates) — verify before adding, then cite-and-USE

| Proposed key | Paper | Coordinates | Why (where) |
|---|---|---|---|
| `bailey2012psr` | Bailey & López de Prado, **Probabilistic Sharpe Ratio** | *J. Risk* 15(2):3–44 (2012); SSRN 1821643 | **DSR/PBO/PseudoMath (all cited) rest on it.** PSR + Mertens heavy-tail SE `σ̂=√[(1−γ₃·SR+((γ₄−1)/4)·SR²)/(n−1)]` **de-inflates Sharpe for our skew/kurtosis-15 regime**; MinTRL answers "is the window long enough". App-3 has Python. Reporting / H2-RA co-primary. (L3) |
| `ledoit2008` | Ledoit & Wolf, **Robust Sharpe-ratio hypothesis test** | *J. Empirical Finance* 15(4):850–859 (2008); DOI 10.1016/j.jempfin.2008.03.002 | *The* heavy-tail/HAC + **studentized stationary-block-bootstrap** Sharpe-**difference** test; the JKM/Memmel test (used by DeMiguel-2009 and, likely, our H2-RA) is **invalid under heavy tails** (rejects 14.5% vs 5.1% nominal). Pairs with cited `politis1994stationary`. Replaces JKM everywhere. (L6, L7) |
| `markowitz1952` | Markowitz, **Portfolio Selection** | *J. Finance* 7(1):77–91 (1952) | Origin of the risk-return objective; **fn.13 M₃/asymmetry** anticipates downside preference → tidy 1952→RU-2000→our-tail arc. Baseline + theory lineage. (L7) |
| `ledoit2004wellconditioned` | Ledoit & Wolf, **Well-conditioned covariance estimator** | *J. Multivariate Anal.* 88(2):365–411 (2004) | **CORRECTION:** `src/baselines/strategies.py:121` uses `sklearn.LedoitWolf` (scaled-identity target) = THIS paper, NOT the cited constant-correlation `ledoit2004honey`. Baseline code is currently mis-cited. (L7) |
| `harveyliu2014evaluating` | Harvey & Liu, **Evaluating Trading Strategies** | *J. Portfolio Mgmt* 40th Anniv. (2014), pp.108–117 | The 200-random-strategies "Sharpe 0.92 but luck" **motivating exhibit** for the placebo arm; `t=SR·√years`; **recommends BHY (dependency-robust FDR) for trading** → resolves our BH-vs-BY flag; endorses DSR+PBO+BH stack; its own "Sharpe inadequate under downside risk" motivates our tail co-primary. Distinct from cited `harvey2015backtesting`/`harvey2016cross`. (L1) |
| `singh2010imrl` | Singh, Lewis, Barto, **Intrinsically Motivated RL / ORP** | IEEE TAMD 2(2):70–82 (2010) | **Formula-level ORP** `r*=argmax_r E_E E_h[F(h)]` (stronger than the cited CogSci `singh2009where`); §VII **shaping-vs-redefinition** → basis for the Ng-1999 placebo classification. Theory-envelope. (L2, L3) |
| `niekum2010gp` | Niekum, Barto, Spector, **Genetic Programming reward search** | IEEE TAMD 2(2):83–90 (2010) | The **closest algorithmic precedent to "a machine authors reward CODE"** (GP over reward programs, fixed agent, scalar fitness) — the CH2 fence anchor + a mechanism-audit (interpret-the-evolved-program) precedent. (L2) |
| `almgrenchriss2000` | Almgren & Chriss, **Optimal Execution** | *J. Risk* 3(2):5–39 (2000) | Cost-model lineage source for the cited `almgren2005direct`; λ-utility risk-cost trade-off; **L-VaR → our coherent CVaR** upgrade line. Data ch. (L3) |
| `kyle1985` | Kyle, **Continuous Auctions & Insider Trading** | *Econometrica* 53(6):1315–1336 (1985) | Linear price-impact `P=p₀+λ·flow`, **λ=½√(Σ₀)/σ_u**; pedigree of the linear-impact term + depth vocabulary; pair with √-law contrast. Data cost cluster (Kyle/Almgren/Toth still 0% cited). (L2) |
| `lopezdeprado2016hrp` | López de Prado, **Hierarchical Risk Parity** | *J. Portfolio Mgmt* 42(4):59–69 (2016) | Robust allocator baseline (corr-distance clustering, no matrix inversion; lower OOS variance than CLA/IVP). Add IF HRP enters the ladder. (L7) |
| (ERC-ES key) | **Cagna & Casuccio**, ERC with Expected Shortfall | CeRP WP 142/14 | Fairest *classical tail-aware* baseline (marginal-CVaR/Tasche + Gaussian-ES). **INTEGRITY: this is the actual content of the mislabeled `Maillard-RiskParity__2010.pdf`** — never cite Maillard-2010 from that file; source the real Maillard-Roncalli-Teiletche (2010) *JPM* 36(4):60–70 separately. (L7) |
| optional | `finGPT2023` (Yang, Liu & Wang — 3 authors), `liu2020finrl`, `dabney2018fqf`, `co-reyes2021evolving`, `real2020automlzero`, `houthooft2018epg`, `rowland2018cramer`, `christiano2017preferences`, `abbeel2004apprenticeship`, `petersen2021dsr` (⚠ acronym clash w/ Deflated-Sharpe), `gonzalez2019glo`, `oh2020lpg`, `xu2018metagradient`, `kirsch2020metagenrl` | see per-slice notes | RelatedWork breadth + specific hooks below |

---

## ★ EXAMINER ALIGNMENT (L6 — highest leverage; the examiner is Dr Okhrati)

- **Khraishi & Okhrati 2022 (`khraishi2022offline`, cited).** §4.1.3 verbatim: *"where α is close to zero, we recover an offline version of the SAC algorithm."* Their CQL loss = `α·[CQL reg] + L_SAC`. → **Position our fixed SB3 SAC as the α=0 pole of the examiner's own CQL conservatism spectrum**; justify "simulated-online not offline" (we have a replay simulator, so α=0 + sealed-OOS instead of a conservatism penalty). Their reward is a **hand-written scalar** → "even the supervisor's offline-RL finance work hand-specifies the reward; we automate authoring it." (Verify ACM DOI before asserting; on-disk copy = arXiv 2203.03003.)
- **Hartley et al. 2025 (`hartley2025personality`, cited) — the examiner's own group (Hartley/Batra/Okhrati/Khraishi).** **Frontier LLMs are risk-NEUTRAL by default** (GPT-4o, Claude-3 Sonnet, Gemini-1.5 ≈ CPT params 1) and shift risk attitude on **semantic/persona cues, NOT numeric magnitudes** → **the examiner's own paper PREDICTS our null** and grounds the "LLM edits on the words 'tail/CVaR', not the fed numbers" mechanism (SQ3). Distilled models (Haiku, GPT-4o-mini) lose the pattern → justifies ADR-039's **frontier-Opus, no-Haiku** panel. **BUILDABLE:** their certainty-equivalent CPT probe (System-prompt Fig.4, temp=1, 15 seeds, Nelder-Mead) is a drop-in **manipulation check on Opus 4.8's own risk attitude** — if risk-neutral, our null responsiveness is the *predicted* outcome. Keep CPT ≠ coherent-CVaR distinct; scope Claude-3→Opus-4.8 transfer.
- **Batra 2025 review (`batra2025review`, cited)** — the group's own finance-LLM survey; situate our work inside "his" review.
- Do **NOT** misattribute to Okhrati: Kusuoka representation, the Ledoit-Wolf Sharpe test, elicitability/EVT.

---

## ★ NULL-PLAUSIBILITY THEORY ANCHORS (deepen the "why a null is the honest prediction" argument)

- **RU-2000 Gaussian Proposition (`rockafellar2000cvar`, cited, UNDERused).** Under normal returns, β≥0.5, min-CVaR ≡ min-VaR ≡ **min-variance (Markowitz)**, CVaR=μ+c(β)σ. → tail feedback carries information **beyond the scalar Sharpe/variance arm only insofar as realized returns are non-Gaussian**: a principled a-priori reason arms collapse (null), localizing any true effect to the fat-tail component. Theory box + "why null is plausible." (L7)
- **Sorg 2010 intermediate-boundedness (`sorg2010internal`, cited, UNDERused).** Benefit of a designed internal reward **peaks at intermediate agent-boundedness and →0 at both extremes**. → literature-grounded explanation for a bounded-effect null: "we locate our agent on that curve." Discussion. (L2)
- **PseudoMath compensation effects (`bailey2014pseudomath`, cited, UNDERused).** On memory-bearing series (AR(1)/vol-clustering), overfitting is **detrimental**: SR_A^IS>SR_B^IS ⟺ SR_A^OOS<SR_B^OOS. → a **numeracy-independent mechanism for negative responsiveness** to fold into the mechanism-audit. Also **MinBTL** (Thm 3.1) + `E[max_N]≈√(2 ln N)` (Prop 2.1): compute/report the minimum-backtest-length for our N candidates as a severity exhibit. (L3)
- **Rowland 2018 CDRL (add `rowland2018cramer`).** The categorical distributional Bellman operator is a **√γ-contraction in Cramér (not Wasserstein)**, and CDRL/C51 control still **converges to the MEAN-optimal policy** (Thm 2). → **modelling the return distribution in the CRITIC does not by itself make an agent risk-sensitive; risk must enter via the OBJECTIVE — i.e. our LLM-authored REWARD.** Rigorous justification for "tail-via-reward, not tail-via-critic" (the two-distributional-axes point). Measure-theoretic register for Okhrati; attribute *theory* to Rowland, *algorithm* to Bellemare/C51. (L1)

---

## ★ MECHANISM-AUDIT METHODOLOGY (cite-and-USE, buildable on the 239 archived programs)

- **AutoML-Zero 2020 (`real2020automlzero`).** Adopt their interpret-searched-code protocol verbatim: **auto-simplify → find recurring MOTIFS across independent runs (convergent evolution) → verify with knock-out/knock-in ablations.** Their **"hyperparameter coupling"** hazard (a coincidental expression produces a good value without *using* the variable) = the exact analogue of our **SQ3 surface-echo-vs-genuine-use** ("does the LLM genuinely use the fed tail magnitudes?") → motivates knock-out probes. (L1)
- **GLO-2019 (`gonzalez2019glo`)** symbolic "what makes Baikal work" analysis + **canonicalized-tree fitness caching** (mirrors our `canonical_hash` dedup). (L2)
- **EPG-2018 (`houthooft2018epg`)** input gradient-saliency of the learned objective — precedent for "does the reward use the fed inputs". Its objective is an **opaque NN** → foil for our **interpretable reward CODE**. (L1)
- **Niekum-2010 / DSR-2021 / EvolvingRL-2021** all interpret their searched objective analytically — the reward-program-taxonomy lineage. (L1, L2)

---

## ★ LIKELY-NULL / SEARCH-VARIANCE CORROBORATION (Limitations)

- EvolvingRLAlgorithms App.E: **4/10 meta-runs succeed, 2/10 rediscover** the good algorithm. AutoML-Zero: good programs are **1-in-10⁷ to 10¹²**. DSR "expectation problem" (optimizing the mean is wrong when you search for the single best). → concrete, quantified external evidence that automated objective-code search is **high-variance / most candidates fail**; triangulates with LEARN-Opt-2025. (L1, L3)

---

## ★ DISTRIBUTIONAL-CRITIC NEIGHBOURS (the axis we deliberately do NOT take — cite-and-distinguish)

- **FQF-2019, QR-DQN-2018 (`dabney2018qrdqn`, cited), CategoricalDRL/Rowland, EX-DRL-2024, DSAC-2020** put the tail in the **value representation**; ours enters **off-critic via the LLM-authored REWARD** atop a standard expected-value SAC critic — orthogonal channel, sharpens identification. EX-DRL corroborates: constrains **GPD shape 0<ε<1 for finite CVaR** (a concrete guard for our GPD-MLE — ties to P19/P20), argues *against* just adding quantiles (supports a **compact** multi-level vector), shares our `troop2021biascorrected` cite. (L1, L6, L7)

## ★ CONTROL-CONDITION / SUBSTRATE citations
- **Sood 2023 (`sood2023deep`, cited) = our closest published substrate:** exact DSR reward (η=1/252), SB3 stack, LW-shrinkage MVO; its **Future Work "add a drawdown component to the reward"** = precisely what our LLM automates → novelty framing. (L7)
- **Moody-Saffell 2001 (`moody2001directrl`, cited):** defines our scalar arm's DSR; already moved to a **downside-deviation** objective (DDR) because "Sharpe penalizes large gains" = our tail-over-scalar motivation. Contrast: M-S fixed-reward/learned-policy vs our LLM-reward/fixed-policy. Pre-empt "SAC is the value-function class M-S warn against" (we hold the learner fixed as a controlled substrate). (L7)
- **FinRL-2020 / FinRL-Meta-2022 (`liu2022finrlmeta`, cited):** the three named scalar rewards (Δvalue, log-return, Sharpe) = our **control condition**; FinRL-Meta's "three hazards (SNR / survivorship / overfitting)" = the Methods framing our rigor stack answers. (L6)

---

## ★ CORRECTIONS / INTEGRITY FLAGS (act on these)

- **Integration map + dossier STALE:** list `sorg2010orp/2011/2010internal`, `singh2009where`, `almgren2005direct`, `bailey2014pseudomath`, `harvey2016cross`, `hadfieldmenell2017ird` as "gaps" — all cited. Reconcile the map's gap list. (L2, L3, L6)
- **`ledoit2004honey` mis-cites the baseline code** → add `ledoit2004wellconditioned` (see table). (L7)
- **`Maillard-RiskParity__2010.pdf` is mislabeled** — it's Cagna-Casuccio ERC-ES. Never cite Maillard-2010 from it. (L7)
- **Almgren-2005 = 3/5-power temporary impact, NOT square-root** (γ=0.314, η=0.142); cost sweep must run **both** 3/5 and ½ and disclose (Frazzini/Toth = ½ camp). (L3)
- **`benjamini1995fdr` coordinates now first-hand-verified** (JRSS-B 57(1):289–300, 1995) — the "unverified/0-byte-cache" note can be cleared. FDR under our **correlated 7 arms → cite/acknowledge Benjamini-Yekutieli-2001** (dependency-robust), which Harvey-Liu-2014 recommends (BHY) — resolves the P17 open BH-vs-BY flag. (L1)
- **FinGPT fence must be SHARPENED:** FinGPT has a real RL component (**RLSP**, fixed price reward) + lists "portfolio/risk" applications → do NOT write "finance-LLMs have no RL/reward". Distinction: *who authors the reward and what the agent is.* Byline = Yang, Liu & Wang (3 authors). (L2)
- **"DSR" acronym collision:** Deep Symbolic Regression (Petersen 2021) vs Deflated Sharpe Ratio (Bailey 2014) — disambiguate if citing Petersen. (L1)
- **RU β/α notation:** RU's β=confidence, α=VaR auxiliary; our α=tail level. RU's (1−β)=our α. Any theory box transcribing RU must reconcile or it reads as a sign slip to an examiner. (L7)
- **Föllmer-Schied on-disk PDF is font-garbled** — web-verify coordinates; never quote from that copy. **Kusuoka key = `kusuoka2001law`** (not `...lawinvariant`). **Kusuoka Thm 7** is the *primary* source for "comonotone law-invariant coherent = unique spectral CVaR mixture" (dossier mis-credits Shapiro-2013). (L6)
- **PseudoMath ref pages:** Romano-Wolf is *Econometrica* 73(4):1237–1282 (not 1273–1282). (L3)
- Two legit "Where Rewards Come From": CogSci-2009 pp.2601–2606 (= `singh2009where`, correct) vs AISB-2010 pp.111–116 — don't "correct" the key to 2010. (L2)

---

## Per-slice TOP items (condensed pointers)
- **L1** (K: DRL/evolved-objective/FDR): add `harveyliu2014evaluating`; Rowland "tail-via-reward" theorem; AutoML-Zero mechanism protocol; likely-null triad; the collective novelty fence; clear the BH coord flag + BY-under-dependence.
- **L2** (K: reward-search/finLLM): add `singh2010imrl`+`niekum2010gp` (formula-level ORP + closest reward-code precedent); shaping-vs-redefinition placebo basis; LPG Fig-5 "vector>scalar"; fix the FinGPT fence; Kyle-λ + FinBERT numeracy example.
- **L3** (K: execution/meta-RL/DSR): **add `bailey2012psr`** (top item — heavy-tail Sharpe de-inflation the kurtosis-15 EDA demands); Sorg "confounds two purposes" + weak-dominance-with-approximation (null is ORP-consistent); PSR mixture-of-Normals (scalar Sharpe garbles the tail); Almgren-Chriss-2000 + 3/5-power correction.
- **L6** (H: examiner/finRL/CVaR): **Khraishi-Okhrati α→0=SAC bridge**; **Hartley null-prediction + CE-CPT probe**; **promote `ledoit2008`**; Kusuoka Thm 7 (primary); FinRL-Meta three hazards; EX-DRL 0<ε<1 GPD guard.
- **L7** (H: portfolio/CVaR/bootstrap): Sood substrate (4 uses inc. Future-Work novelty fence); RU Gaussian-collapse null anchor; **Ledoit-Wolf citation-precision fix**; add `markowitz1952`/`lopezdeprado2016hrp`; White Reality-Check wired to Politis-Romano; block-length p-sensitivity (headline fixed p=0.1 vs PPW-2009 selector in `ood_stress.py`).
