# DEEP_BENCH_T4 — the SOTA / FinRL "does it work / is it competitive?" band, interrogated

**Status:** read-only verification + recommendation dossier. NOT dissertation prose. No code, config, or
prereg was edited. **Date:** 2026-06-25. **Repo:** `llm-reward-portfolio`. **Author role:** quant-finance +
RL-reproducibility reviewer red-teaming the Tier-4 (external SOTA) band before the campaign freeze.
**Scope:** Tier-4 ONLY — the FinRL / FinRL-Meta / FinRL-DeepSeek published-Sharpe band used as external
context. (T0 classical floor, T1 Eureka reward baseline, T2 search baselines, T5 ES backtest are covered
elsewhere: `docs/CAMPAIGN_benchmarks.md`, `docs/CAMPAIGN_attribution.md`.)

**Companion / supersession.** Reads on top of `docs/CAMPAIGN_benchmarks.md §3` (which assembled the band).
This doc does NOT re-assemble the band — it **interrogates whether the band may be used at all**, and how.
Where the two differ, this doc is the more conservative and should win for Tier-4 framing decisions.

---

## 0. Bottom line up front (read this if you read nothing else)

1. **A head-to-head SOTA claim is indefensible and must NOT be made.** Universe, period, costs,
   rebalancing cadence, action space, and objective all differ between this dissertation and every FinRL
   number. It is a cross-study, apples-to-oranges comparison. Severity **CRITICAL** if claimed as ranking.

2. **The band itself is not a fixed quantity — it is a smear, and partly a smear of overfitting.** The
   FinRL ensemble's *own GitHub issue tracker* reports the **same code, same data, seeds fixed, Sharpe
   from 0.16 to 2.39** across re-runs (issue #190, verified first-hand below). A "band" whose endpoints
   are reproducibility noise on a *single* method cannot anchor a competitiveness claim with any
   authority. Using it as if it were a stable target lends it false precision. Severity **HIGH**.

3. **The defensible claim is the internal ladder, full stop.** "Does it work" = clears the **DeMiguel 1/N
   floor + classical allocators (T0)**, **beats the hand-written rewards (T1/H1, Eureka-style)**, and
   **beats uninformed search (T2/H4)** — all at **matched compute, same universe, same period, same costs,
   inside one pre-registered inference family**. That is a real, internally-valid "it works" statement.
   The SOTA band enters ONLY as a one-paragraph **plausibility ribbon** with heavy caveats, never as a tier
   the project must win.

4. **The honest plausibility ribbon, if cited: realized costed OOS US-equity DRL Sharpe ≈ 0.85–1.6**,
   centred ~1.3–1.5, with explicit exclusions (>2.0 red-flag; crypto; the 9.56-on-15-days artifact;
   Jiang-EIIE "average on stocks" + future-set leak). Cite it to show the arms are *plausible*, not to
   show they *win*.

5. **A same-panel SOTA re-run is the only thing that would make a comparison fair — and it is out of
   scope and low-value.** Re-running a FinRL PPO/SAC agent on THIS 30-asset PIT panel is feasible in
   principle (the env exists) but would (a) consume freeze-critical compute, (b) still not be a published
   SOTA number (it would be *your* re-implementation), and (c) be dominated by what T0/T1/T2 already buy.
   **Recommend: do NOT re-run; cite the band as context only.** Feasibility/value assessed in §6.

6. **The single sharpest landmine, specific to THIS project:** the prototype's realized arm Sharpes are
   **negative** (best *mean* Sharpe ≈ −0.39, 1 seed, directional-only — `project-prototype-results`).
   Even the *campaign* arms may land below the FinRL ribbon. If the band is plotted naively, the honest
   reading is "the arms underperform published SOTA," which is **expected** (different/older fixed cohort,
   bull-era 1/N is hard to beat — DeMiguel) but is a **gift to a hostile examiner** if not pre-framed.
   The band must be introduced *with* the reason the arms may sit below it, or not plotted at all. **HIGH.**

---

## 1. Is comparing THIS dissertation's winner to the FinRL band even VALID? (Question 1)

**Verdict: NO as a ranking; YES only as a loosely-bounded plausibility context, and even that is weak.**

The unit of inference in this project (PREREGISTRATION §1) is *a reward function's OOS risk-adjusted
performance, across seeds and the candidate population* — a **comparative, within-study** object. FinRL
numbers are **absolute, single-study** objects produced under different conditions on every axis that moves
a Sharpe ratio. The mismatch, axis by axis:

| Axis | THIS dissertation | FinRL SOTA band | Does it move Sharpe? |
|---|---|---|---|
| **Universe** | 30-name survivorship-free PIT sleeve (Refinitiv/LSEG; anonymised; **2005 cohort** fixed action space, R17) | DJIA-30 (Yang); Nasdaq-100 (Contest/DeepSeek); Dow-29 (multimodal) | **Yes, large.** Different constituents → different realized vol/return; Nasdaq-100 ≠ DJIA. |
| **Period** | Sealed OOS **2018–2025** (covers 2018-Q4, COVID-2020, 2022 bear, 2023-24 bull) | Yang test 2020-07→2022-03 (bull-heavy); Contest 2019–2023; multimodal varies | **Yes, large.** Regime determines Sharpe more than method (the 2020–22 window flatters everyone; DJIA itself ~1.3 there). |
| **Costs** | Costed; cost-robustness sweep `[0,5,10,25,50]` bps; every benchmark pays the **same** cost (T0 gate) | Often a single bps assumption, sometimes weakly disclosed; cross-engine cost handling varies | **Yes.** Costs compress optimized-vs-naive gaps (verified: under costs, naive portfolios are "less often outperformed"). |
| **Rebalancing** | Daily, simplex weights, fixed 30-asset action | Daily but different cadence/turnover regimes; Contest agents high-turnover (+342% cumret) | **Yes.** Turnover × cost interacts; high-turnover agents' Sharpe is cost-fragile. |
| **Objective / agent** | Fixed **SB3 SAC**, reward is the treatment; **off-policy** | PPO/A2C/DDPG/ensemble (Yang); CPPO+LLM-signal (DeepSeek); mixed | **Yes.** Off-policy SAC is *itself* flagged as poorly-suited to noisy financial rewards (§3, arXiv:2307.07694). |
| **Selection / multiplicity** | PBO/CSCV + DSR + BH/Romano-Wolf over a **frozen m=6 family**; trial count stated | Trial count almost never reported; contest = best-of-many-teams (extreme selection) | **Yes, decisive.** This is the overfitting axis (§2). |
| **Inference unit** | Per-seed rliable IQM + paired across-seed bootstrap (carries training-RNG variance, R16) | Usually a single backtest path, no seed distribution | **Yes.** A single-path Sharpe has no error bar; the band's points are points, not distributions. |

**What can legitimately be claimed:** at most, *"the learned arms' realized OOS Sharpe falls within the
range reported by the published US-equity DRL literature (~0.85–1.6), and does not exhibit the >2.0 values
that the backtest-overfitting literature flags as red-flags — i.e. the arms are in a plausible regime, not
an inflated one."* That is a **plausibility / sanity** statement about *order of magnitude and direction*,
not a competitiveness ranking. Anything stronger ("competitive with", "on par with", "approaches SOTA",
"beats FinRL") is unsupported by the design and must be struck.

**Even the plausibility statement has a hole** (be honest about it): if the arms land *below* 0.85 (very
possible given the prototype's negative Sharpes and the older fixed cohort), the band no longer certifies
"plausible" — it reads as "below the credible SOTA floor." So the band cannot be relied on to *flatter*;
it can only *bound from above* (rule out the overfit fantasy zone). Frame it that way: **the band is a
ceiling-of-credibility, not a floor-of-respectability.**

---

## 2. The band is suspect because the SOTA numbers are overfit / non-reproducible (Question 2)

This is the heart of the matter, and the project's own machinery is the argument. **The same literature
that produces the band also explains why the band's high end is not real.** Using it honestly means
*citing it against itself*.

### 2a. Reproducibility: the band's endpoints are partly noise — first-hand evidence

- **FinRL ensemble, GitHub issue #190 (AI4Finance), verified first-hand.** A user re-running the DDPG/
  ensemble strategy with **all seeds fixed** (`random`, `numpy`, `torch`, SB3, gym env + action space +
  vecenv) reports Sharpe ranging **0.162571 → 2.385978** across runs — a **~15× spread on identical code
  and data**, asking "is it supposed to be fluctuating so much?" *(github.com/AI4Finance-LLC/FinRL-Library/
  issues/190.)* This is the decisive fact: **the FinRL Sharpe is not a number, it is a wide random
  variable**, and the "0.9–2.7" folk-band is essentially its sampling range.
- **Henderson et al. (2018), "Deep RL That Matters" (AAAI).** Foundational: non-determinism + intrinsic
  variance make single-seed deep-RL results uninterpretable without significance metrics and seed
  distributions. The FinRL points are single-path, single-seed — exactly the reporting Henderson warns
  against. *(ojs.aaai.org/index.php/AAAI/article/view/11694.)*
- **Stable-Baselines3 docs (the FinRL backbone):** "Completely reproducible results are not guaranteed
  across PyTorch releases or different platforms... results need not be reproducible between CPU and GPU
  executions, even when using identical seeds." So even *bit-level* reproduction is not promised.
- **Implementation risk (arXiv:2603.20319, 2026), verified first-hand.** The **same strategy** across
  different backtest engines diverges materially: simple strategies ≤0.18% but high-turnover rotation up
  to **3.71% total-return** divergence purely from implementation choices; the authors recommend ≥2
  independent validators and call implementation risk "a material and previously invisible source of
  error." *Honest correction to any overclaim:* in THAT paper's 15-strategy sample the divergence never
  flipped the Sharpe *sign* (they report CSI = 0) — so cite it for *cross-engine dispersion*, not for
  "sign flips." The sign-flip risk is a *flagged possibility* (CSI is their red-flag indicator), not an
  observed outcome there.

**Implication:** comparing this project's *carefully-seeded, per-seed-IQM, 30-seed* Sharpe (with a real
error bar) against a FinRL *single-path point drawn from a 0.16–2.39 distribution* is not just
apples-to-oranges on conditions — it is **a distribution-vs-a-draw**. The project's number is the more
trustworthy object; the band is the noisier one. Say so. Do not let the band borrow authority it lacks.

### 2b. Overfitting: the high end is selection, not alpha

- **Bailey, Borwein, López de Prado, Zhu (2014), "Pseudo-Mathematics and Financial Charlatanism"
  (*Notices of the AMS* 61(5):458-471).** Core result: high backtest Sharpe is *easy* after trying a small
  number of configurations; the more configurations tried, the higher the probability the backtest is
  overfit; and **analysts almost never report the number of trials**, so readers cannot gauge overfitting.
  *(ams.org/notices/201405/rnoti-p458.pdf; ssrn 2308659.)* **Every FinRL contest number is the best of
  many teams' many configurations with the trial count unreported** — the textbook overfitting setup.
- **Bailey & López de Prado (2014), Deflated Sharpe Ratio (*JPM*).** The expected maximum Sharpe of N
  *skill-less* trials grows with N; a raw Sharpe must be deflated by the trial multiplicity and corrected
  for non-normality. The project *implements* DSR + PBO/CSCV; the FinRL band points are **un-deflated**.
  Comparing a deflated/PBO-guarded number to un-deflated ones is comparing a corrected quantity to an
  inflated one. *(davidhbailey.com/dhbpapers/deflated-sharpe.pdf; ssrn 2460551.)*
- **FinRL Contest organizers admit it.** In the benchmarking paper (arXiv:2504.02281) they (i) *reject*
  agents with high overfitting probability "at a 10% significance level," (ii) note participants' "models
  showed strong risk management... but their generalization to new, unseen market conditions remains a
  challenge," and (iii) report agents with **+335% / +342% cumulative return but Sharpe 0.95 / 0.29 and
  max drawdown −50.24% / −92.47%** — i.e. the contest's own headline returns are not risk-adjusted alpha.
  The organizers themselves do not treat their leaderboard Sharpes as deployable.
- **The 9.56 artifact, verified verbatim.** Contest-2023 team "Nik-Elena": **Sharpe 9.56 on a 15-trading-
  day window (2023-10-25→11-14), +3.50% cumret, −0.40% MaxDD**, then deteriorated in the next 6-day window.
  A short-window annualization artifact, not alpha. **Exclude**; cite as the cautionary illustration.
- **DRL-in-finance specifically overfits.** arXiv:2511.11481 (2025) reports its own agent going from
  **Sharpe 1.41 (before training) to 0.13 (after training)** and states plainly: "Reinforcement learning
  models often capture patterns specific to the training set, leading to poor generalization in
  out-of-sample backtests." The "before > after" inversion is the overfitting signature in the open.

### 2c. How to use the band without lending it false authority — the rule

> **Cite the band and its critique in the same breath.** Present ~0.85–1.6 as *"the range the published
> US-equity DRL literature reports, a range that the same literature shows is (a) not reproducible to
> better than ±a factor of ~15 on identical code [#190], (b) un-deflated for the many trials behind it
> [Bailey et al.], and (c) regime- and cost-dependent. We therefore use it only to locate our arms'
> order of magnitude, not to rank them."* The critique is not a hedge bolted on afterwards — it is the
> *reason the comparison is honest*. A band cited without its overfitting/reproducibility critique is the
> exact "pseudo-mathematics" Bailey et al. warn against; cited *with* it, the project demonstrates the
> methodological literacy that earns marks.

---

## 3. Should a SOTA claim be made AT ALL? (Question 3) — **Recommendation: NO; restrict to the internal ladder.**

**Decision: make NO SOTA competitiveness claim. Restrict "does it work" to the internal ladder, and cite
the FinRL band only as external plausibility context with the §2c caveat block.**

Reasons, in priority order:

1. **The internal ladder is sufficient and is the part that is actually valid.** "It works" is fully
   established, with internal validity, by three rungs the project controls end-to-end:
   - **T0 — clears the classical floor.** Frozen winner's median-per-seed Deflated Sharpe > best of 8
     allocators (DeMiguel 1/N, Markowitz-LW, ERC, HRP, GMV, max-div, inverse-vol, momentum), **every
     benchmark paying the same transaction cost** (`benchmark_floor`, wired). This is the DeMiguel "can you
     beat 1/N out of sample" bar — the one that genuinely separates value from noise.
   - **T1 — beats the hand-written rewards (H1, Eureka-faithful).** Fraction of (seed, window) cells where
     the LLM winner > best `REWARD_CANON` member, + median normalized improvement, vs Eureka's 83% / +52%.
     *(NOTE: T1 is currently a WIRING GAP — see `CAMPAIGN_benchmarks.md §2c/§4 G1`. This rung must be wired
     before H1 can be claimed at all. It is the binding constraint on the whole "does it work" story, far
     more than the SOTA band.)*
   - **T2 — beats uninformed search (H4a/H4b).** LLM winner > random-search-over-code and
     BO-over-template at matched candidate budget — two live frozen arms.
   All three are **same universe, same period, same costs, matched compute, one pre-registered inference
   family (m=6, BH q=0.05, Romano-Wolf, PBO/CSCV, DSR)**. That is a defensible "it works."

2. **The headline is comparative, not absolute (PREREGISTRATION §10).** The frozen claim is
   "distributional vs scalar feedback at matched compute," explicitly *not* "beats the market." A SOTA
   competitiveness claim is off-axis from the registered hypothesis and imports all of §1–§2's liabilities
   for zero gain to H2.

3. **PDF-only grade, citations checked, supervisor co-authored corpus papers.** A naked "competitive with
   SOTA" claim is the single most attackable sentence available to a hostile reader: it invites "which
   SOTA, on what universe, what period, what costs, deflated by how many trials, with what seed variance?"
   — all of which the project *cannot* answer for the FinRL numbers (it can only answer them for itself).
   Restraint here is not weakness; it is the methodological honesty the rubric rewards.

4. **The prototype already shows the arms may sit below the band.** Negative directional Sharpes mean a
   SOTA-competitiveness framing risks being *false in the wrong direction*. The internal-ladder + comparative
   framing is robust to the arms being absolutely modest (a flat/below-band absolute result in a bull era is
   *expected* under DeMiguel, and is a finding about the *question as posed*, not a failure).

**What to AVOID, explicitly (struck-phrase list for the write-up):**
- ✗ "competitive with / on par with / approaches / rivals state-of-the-art DRL"
- ✗ "beats FinRL / FinRL-Meta / the SOTA Sharpe"
- ✗ "achieves a Sharpe of X, comparable to the SOTA 1.5" (the comparison is invalid; the implication is false)
- ✗ any plot that places the arms *on the same axis as a single FinRL point* without the seed-distribution
  error bar on the arm and the "single-draw-from-0.16–2.39" caveat on the FinRL point
- ✗ citing the 9.56, any crypto Sharpe, or Jiang-EIIE as a comparator (exclusions, §5)

**What to CLAIM, explicitly (safe-phrase list):**
- ✓ "The LLM-designed winner clears the DeMiguel 1/N floor and the broader classical-allocator floor at
  matched transaction cost (T0)."
- ✓ "The LLM-designed rewards beat the best hand-engineered reward on X% of (seed, window) cells (H1),
  a direct analogue of Eureka's 83% beat-the-human result." *(once T1 is wired)*
- ✓ "The informed LLM beats uninformed search over the same reward space at matched budget (H4)."
- ✓ "For external context, the arms' realized OOS Sharpe falls within the ~0.85–1.6 range reported by the
  published US-equity DRL literature and below the >2.0 values that the backtest-overfitting literature
  flags as overfit; these published numbers differ in universe/period/cost and are not reproducible to
  better than a wide factor, so we use them to locate plausibility, not to rank." *(only if the arms are
  in fact ≥~0.85; otherwise omit the band and report the absolute result with the DeMiguel framing.)*

---

## 4. If a SOTA comparison WERE made, what minimum conditions make it fair? (Question 4)

For a comparison to be **fair** (not merely suggestive), it would have to neutralize every axis in §1's
table. The minimum conditions:

1. **Same universe** — the FinRL agent must trade *this* 30-asset PIT panel (same constituents, same
   survivorship-free PIT membership, same anonymization), not DJIA-30 / Nasdaq-100.
2. **Same period + same splits + same embargo** — identical 2018–2025 sealed OOS leg, identical
   train/val/test boundaries and purge/embargo, so regime is held constant.
3. **Same cost model** — identical bps and the same charge-after-action turnover accounting that T0 uses.
4. **Same action space + cadence** — long-only simplex over the same 30 names, same daily rebalance.
5. **Same selection discipline** — the FinRL agent's hyperparameters selected on the *same* validation
   protocol, with the *same* trial count entering a DSR/PBO deflation; no best-of-many-runs cherry-pick.
6. **Same inference unit** — N-seed per-seed IQM with the paired across-seed bootstrap, so the FinRL agent
   carries the *same* error bar (this alone defeats every published single-path point).

**This is exactly a same-panel re-run** (§6). Note the brutal corollary: once you impose conditions 1–6,
**the result is no longer "published SOTA" — it is *your* re-implementation of a FinRL agent on your
panel**, which (a) belongs in T2/T3 as just another arm/baseline, not in "T4 external SOTA," and (b) is
only as good as your re-implementation (implementation risk, §2a). So "make the SOTA comparison fair" and
"keep it a SOTA comparison" are **mutually exclusive**: fairness dissolves the externality. This is the
clinching reason to keep T4 as *context only* and not attempt a head-to-head.

---

## 5. Construct validity of "does it work" — Sharpe alone, and the multiple-testing of "beats SOTA" (Question 5)

**"Does it work" must not be operationalized as Sharpe alone.** Sharpe is necessary but radically
insufficient, and the band literature proves it:

- **Sharpe hides tail and drawdown.** The Contest agents with +335%/+342% cumret had Sharpe 0.95/0.29 and
  MaxDD **−50%/−92%**. A Sharpe-only "it works" would have rated catastrophic strategies as fine. The
  project's risk-shape thesis (distributional feedback should cut CVaR/MaxDD/turnover, possibly at a Sharpe
  cost) is *precisely* the dimension Sharpe-alone erases. **Report the full vector: Sharpe + CVaR(α) +
  MaxDD + turnover + Sortino/Calmar**, exactly as the project's `benchmark_floor` and ES-backtest (T5) do.
  The prototype's only pro-distributional signal was floor-raising (best mean Sharpe, best mean drawdown,
  highest hit-rate) — a multi-metric, central-tendency signal invisible to a single max-Sharpe number.
- **Annualization fragility.** Short-window Sharpes annualize to nonsense (the 9.56/15-day artifact). The
  project's 2018–2025 OOS leg (~2087 days) is long enough to annualize honestly; FinRL contest windows
  (15–21 days) are not. A construct-valid comparison cannot put a 2000-day Sharpe next to a 15-day one.
- **"Beats SOTA" is itself a multiple-testing trap.** With a band spanning 0.85–1.6 (and folk-extending to
  2.7 via reproducibility noise), one can almost always find *a* FinRL point a given arm "beats" or "ties."
  Choosing the comparator post hoc to flatter the arm is the Bailey-et-al. multiplicity sin applied to the
  *comparison itself*. The project's discipline (frozen m=6 family, BH/Romano-Wolf, trial count stated)
  applies *within* the study but **cannot be applied across studies** — there is no defined family of
  "all SOTA comparisons," so the multiplicity is uncontrollable. This is a further, independent reason the
  SOTA comparison cannot be a *test* (only loose context): **you cannot FDR-correct a comparison whose
  family you cannot enumerate.**
- **Construct validity of the *band* as a "SOTA" proxy.** "SOTA" is not a measured construct here; it is a
  convenience label over a heterogeneous, partly-overfit, partly-crypto literature. Treating it as a single
  latent "state of the art" is a construct error. The honest construct is narrower: *"the range of
  realized costed OOS US-equity DRL Sharpes reported in a handful of FinRL-family papers."*

---

## 6. Feasibility & value of a same-panel SOTA re-run (Question 4, operationalized)

**Feasibility: technically YES, practically NO. Value: LOW. Recommendation: DO NOT do it before freeze.**

- **Feasible because** the env (`PortfolioEnv`), the rollout/costing harness (`rollout_port_returns`,
  `WeightPolicy`), the gold panel, and SB3 (SAC already; PPO/A2C are SB3-native) all exist. Standing up a
  FinRL-style PPO/A2C agent on the same panel/period/costs/seeds is a bounded engineering task.
- **Low-value because:**
  1. **It stops being "SOTA."** Per §4, conditions 1–6 turn it into *your* re-implementation — a T2/T3
     baseline, not an external SOTA number. It cannot support a "competitive with published SOTA" claim;
     at best it supports "an off-the-shelf PPO baseline on our panel scores X," which T0/T2 already bracket
     (1/N + search are stronger, more standard, already-wired baselines).
  2. **Implementation risk taxes it** (§2a): a single re-implementation's Sharpe carries the same
     engine-dependent dispersion; one would need ≥2 validators to trust it — more scope.
  3. **It competes with freeze-critical work.** The binding gap is **T1 wiring (H1)**, not T4. Compute and
     calendar should go to closing G1 (the Eureka beat-the-human arm), not to a re-run that yields a weaker
     baseline than the ones already in the ladder.
  4. **Marginal defensive value over T0.** The reviewer worry a SOTA re-run would answer — "is DRL even
     competitive here?" — is *already* answered more cleanly by "the LLM winner beats 1/N, the classical
     allocators, the hand rewards, and uninformed search, same conditions, corrected for multiplicity." A
     PPO re-run adds a weaker comparator, not a stronger claim.
- **The one scenario where it has value (optional, post-freeze, clearly labelled future work):** a single
  PPO/A2C agent on the same panel, reported *purely as a sanity datapoint* ("an off-the-shelf DRL agent
  on our exact panel lands at Sharpe X, consistent with the plausibility ribbon"), with the seed
  distribution and the "this is our re-implementation, not a published number" disclaimer. Only if compute
  is free after the campaign. **Not a freeze prerequisite. Not a SOTA claim.**

---

## 7. The honest band, with precise citations and overfit exclusions (carried + re-verified)

**In-band (realistic, US-equity, costed) — the plausibility ribbon ≈ 0.85–1.6, centred ~1.3–1.5:**

| Source | Universe / window | Method | Reported Sharpe | Verification status |
|---|---|---|---|---|
| Yang et al. (2020), FinRL ensemble, *ICAIF* | DJIA-30, test 2020-07→2022-03 | PPO/A2C/DDPG ensemble | **ensemble 1.30** vs **DJIA 0.47**, **min-var 0.45** (Columbia/openfin print of the ensemble paper); the readthedocs/CAMPAIGN_benchmarks variant cites ensemble 1.53 / A2C 1.37 / PPO 0.99 / DDPG 0.88 / DJIA 1.32 for a different window | **Numbers differ by source/window — DO NOT quote a single canonical value.** This *is* the reproducibility problem (§2a). Cite as "~1.3 ensemble vs ~0.5 baseline in one window; ~1.5 in another" and flag the spread. `% VERIFY` the exact pairing before use. |
| FinRL-Meta (Liu et al., NeurIPS 2022 D&B; arXiv:2211.03107) | US stocks (Dow) | ElegantRL / SB3 | ElegantRL **1.457**; SB3 **1.621** | carried from CAMPAIGN_benchmarks §3 (verified there); `% VERIFY` against the NeurIPS PDF table before quoting. |
| Multimodal DRL (arXiv:2412.17293) | Dow-29 | PPO + signals in FinRL | **0.86** (ann. 16.24%, vol 17.49%, Sortino 1.27) | carried from CAMPAIGN_benchmarks §3; **PDF would not parse via WebFetch this session** — `% VERIFY` first-hand before quoting. Use as the *floor of credible*. |
| FinRL Contest 2025 (FinRL-DeepSeek; arXiv:2504.02281) | Nasdaq-100, test 2019-01-01→2023-12-31 (1258 days) | CPPO + LLM (DeepSeek) signal | **Otago Alpha 1.08** (top, +191% cumret); Ruijian&Sally **0.95** (+335% cumret, MaxDD −50.24%); Queen's Gambit **0.29** (+342% cumret, MaxDD −92.47%) | **verified first-hand this session.** Use the 0.29/0.95-vs-huge-cumret rows as the *Sharpe-hides-risk* illustration, not as band anchors (Nasdaq-100 ≠ this universe). |

**Out-of-band — exclusions (cite as cautions, never as comparators):**

- **>2.0 on US equity = overfit red flag.** Grounded in Bailey-Borwein-López-de-Prado-Zhu (2014) +
  Deflated Sharpe (Bailey-López de Prado 2014). The project's PBO/CSCV + DSR + embargoed purge + BH/
  Romano-Wolf are exactly the safeguards that separate credible from inflated.
- **FinRL Contest 2023 Sharpe 9.56 — verified: 15 trading days (2023-10-25→11-14), +3.50% cumret, −0.40%
  MaxDD**, deteriorated next window. Short-window annualization artifact. **Exclude.**
- **Crypto — exclude wholesale.** FinRL-Meta crypto Sharpe **2.992** (ann. 360.8%) — different asset class,
  no survivorship-free PIT equivalent. (Carried; `% VERIFY` the exact figure.)
- **Jiang & Liang (2017), EIIE (arXiv:1706.10059) — exclude, with rationale.** Crypto-only; **the authors
  report only "average" performance when EIIE is tested on the stock market**; and a **look-ahead leak**
  (CV set placed at the *end* of the price matrix, in the future of the test set). Not an equity SOTA
  comparator. (Carried from CAMPAIGN_benchmarks §3b; the "average on stocks" + future-CV claims should be
  `% VERIFY`'d against the EIIE paper text directly if cited in the dissertation.)

**Reproducibility/overfitting citations (the load-bearing ones for §2c):**
- FinRL ensemble GitHub issue #190 — Sharpe 0.16→2.39 same code, seeds fixed (github.com/AI4Finance-LLC/
  FinRL-Library/issues/190). **Verified first-hand.** *(This is the single most useful citation in the
  whole dossier — it converts "the band is overfit" from assertion to documented fact.)*
- Bailey, Borwein, López de Prado, Zhu (2014), *Notices of the AMS* 61(5):458-471 (ssrn 2308659).
- Bailey & López de Prado (2014), Deflated Sharpe Ratio, *JPM* (ssrn 2460551;
  davidhbailey.com/dhbpapers/deflated-sharpe.pdf).
- Henderson et al. (2018), "Deep RL That Matters," AAAI 32(1) (ojs.aaai.org/index.php/AAAI/article/view/11694).
- Implementation risk: arXiv:2603.20319 (2026) — cross-engine return divergence up to 3.71%; CSI=0 in
  their sample (no sign flip *observed*). **Verified first-hand.** `% VERIFY` the arXiv id at submission
  (2026 id; sweep-surfaced).
- DRL-in-finance overfits: arXiv:2511.11481 (2025) — Sharpe 1.41(pre)→0.13(post-training). **Verified
  first-hand.** `% VERIFY` id at submission.
- DRL portfolio sample-complexity / off-policy failure: arXiv:2307.07694 — off-policy (DDPG/TD3/**SAC**)
  "perform poorly" on noisy rewards; on-policy (PPO/A2C) cope; ">2m steps ≈ 8,000 years of daily prices."
  **Verified first-hand (abstract).** *(Directly relevant: it questions THIS project's fixed SAC choice —
  see §8.)*

---

## 8. A project-specific landmine the band exposes — the SAC choice (severity HIGH, but defensible)

The most directly relevant external finding this session is **arXiv:2307.07694**: *off-policy* algorithms
(DDPG, TD3, **SAC**) "are unable to learn the right Q-function due to the noisy rewards and therefore
perform poorly," while *on-policy* PPO/A2C cope. The project's **headline agent is SB3 SAC** — and the
prototype logged critic-loss divergence (loss → 2.55e+05) in **6 distinct diverged runs (~2.5% of ~240
trainings; 4 transient)** — *64 was the `anomalies.jsonl` line-count, not a run-count* (the 64 advisory
lines cluster, by step-resets, into 6 runs). These are the same failure mode.

- **Why it's a landmine:** an examiner who knows this paper (a FinRL-adjacent reader well might) can ask
  "you fixed the one agent class the literature says struggles on noisy financial rewards — and your own
  critics diverged. Doesn't that confound H2?" *(precisely: 6 diverged runs, ~2.5% of trainings; the often-cited
  "64" is the `anomalies.jsonl` line-count, not a run-count.)*
- **Why it's defensible (pre-empt it in the methodology/limitations):**
  1. **SAC is held FIXED across all arms** — it is the *constant*, not the treatment. Any SAC weakness is
     differenced out of the comparative H2 (distributional vs scalar); it affects *absolute* level, not the
     *contrast*. This is the central design choice (PREREGISTRATION §2) and it directly neutralizes the
     concern for the headline.
  2. The critic instability is **acknowledged and mitigated** — PopArt / critic-LayerNorm are the
     identified fix (`project-critical-audit-register`; the prototype explosions *motivated* it). State
     that the campaign runs the hardened critic.
  3. **It re-confirms the SOTA comparison is off-axis.** If the fixed agent is deliberately a constant
     chosen for clean differencing (not for absolute-return maximization), then comparing its absolute
     Sharpe to a PPO-ensemble SOTA number is doubly invalid — different agent, chosen for a different
     purpose. Another nail in the "no head-to-head SOTA claim" coffin.

**Action:** add one limitations paragraph: "We fix SB3 SAC as the common substrate so the reward-feedback
contrast is clean; SAC is known to be sensitive on noisy financial rewards (arXiv:2307.07694) and our
prototype exhibited critic instability, which the campaign mitigates via PopArt/critic-LayerNorm. Because
the agent is held constant, any such sensitivity is differenced out of the comparative hypotheses and
affects only absolute performance level — which is itself why we make no absolute SOTA-competitiveness
claim." This converts the landmine into evidence of methodological awareness.

---

## 9. Prioritized, concrete pre-freeze hardening

**P0 — (claim language) Freeze the Tier-4 framing as "plausibility ribbon, never ranking."** In the prereg
/ benchmarks doc, write the exact safe/struck phrase lists from §3 verbatim. Specifically: T4 is *external
context*, the headline stays *comparative* (§10), and **no sentence asserts SOTA competitiveness.** This is
a documentation/wording change, zero compute, and removes the single largest overclaiming risk. *(Severity
of NOT doing it: CRITICAL.)*

**P0 — (precondition for the whole "does it work" story) Close T1/H1 (the Eureka beat-the-human arm).**
This is the binding gap (`CAMPAIGN_benchmarks.md §4 G1`), *not* T4. Without it there is no internal "it
works vs the human baseline." It dominates every T4 task in value. *(CRITICAL; it's the actual deliverable
the SOTA band is a poor substitute for.)*

**P1 — (caveat block) Write the §2c "cite-the-band-against-itself" paragraph** to accompany any appearance
of the band: reproducibility (#190's 0.16–2.39), un-deflated trials (Bailey et al.), regime/cost
dependence, single-path-vs-seed-distribution. The band may not appear in the PDF without this block
adjacent. *(HIGH.)*

**P1 — (conditional-display rule) Make the band plot conditional on the arms landing ≥~0.85.** If the
campaign arms' realized OOS Sharpe is below the credible floor (live possibility given the prototype),
**omit the ribbon** and report the absolute result with the DeMiguel "beating 1/N in a bull era is the
real bar; a modest absolute Sharpe is expected, not failure" framing. Never plot the arms below a "SOTA"
ribbon without that framing — it hands the examiner a false "underperforms SOTA" reading. *(HIGH — this is
the prototype-negative-Sharpe landmine, §0.6.)*

**P1 — (limitations) Add the SAC-on-noisy-rewards paragraph (§8).** Pre-empts the 2307.07694 objection;
converts the critic divergences (6 diverged runs, ~2.5%; "64" was an `anomalies.jsonl` line-count, not a
run-count) + fixed-SAC choice into evidence of awareness. *(HIGH.)*

**P2 — (multi-metric construct) Ensure "does it work" is reported as the full vector** (Sharpe + CVaR +
MaxDD + turnover + Sortino/Calmar), not Sharpe alone, in the T4-context paragraph as well as the internal
ladder — citing the Contest +342%-cumret/−92%-DD/0.29-Sharpe row as the reason. (`benchmark_floor` already
emits the vector; this is a reporting-emphasis instruction.) *(MEDIUM.)*

**P2 — (citation integrity) Mark every band number `% VERIFY` until confirmed first-hand against the
primary table.** Specifically unverified-this-session: the Yang ensemble exact value (1.30 vs 1.53 — they
differ by source/window; resolve which window/source you quote), FinRL-Meta 1.457/1.621, multimodal 0.86
(PDF didn't parse), crypto 2.992, EIIE "average on stocks" + future-CV. The 2025–2026 arXiv ids
(2511.11481, 2603.20319, 2412.17293, 2504.02281) are sweep-surfaced — confirm ids at submission per the
CLAUDE.md `% VERIFY` rule (supervisor co-authored corpus papers). *(MEDIUM, but mandatory before the PDF.)*

**P3 — (optional, post-freeze, future work only) Same-panel PPO sanity datapoint** (§6) — only if compute
is free after the campaign, reported as *our re-implementation*, not SOTA, with seed distribution. **Not a
freeze prerequisite.** *(LOW.)*

---

## 10. The strongest DEFENSIBLE "is it competitive?" framing (the recommended sentences)

Use this as the template; it makes the maximal honest claim and is robust to a hostile, citation-literate
reader and to the arms being absolutely modest:

> *"We do not make a head-to-head state-of-the-art claim: published FinRL/FinRL-Meta results are produced
> on different universes (DJIA-30, Nasdaq-100), different periods and regimes, different cost and
> rebalancing assumptions, and a different (often on-policy or ensemble) agent, and — critically — they are
> single-path numbers that the source code itself does not reproduce to better than roughly a factor of
> fifteen with seeds fixed [FinRL issue #190], are not deflated for the many configurations behind them
> [Bailey, Borwein, López de Prado & Zhu, 2014; Deflated Sharpe, Bailey & López de Prado, 2014], and span
> a range partly attributable to backtest overfitting (the same literature rejects >2.0 US-equity Sharpes
> and the 9.56-on-15-days contest artifact). We therefore use these numbers only as an external
> plausibility ribbon (~0.85–1.6): they tell us our arms operate in a credible regime rather than the
> inflated >2.0 zone, not that our arms rank above or below any particular agent. Our competitiveness
> claim is instead internal and fully matched: the LLM-designed reward clears the DeMiguel 1/N floor and
> the classical-allocator floor, beats the best hand-engineered reward [the Eureka beat-the-human bar:
> 83% / +52%], and beats uninformed search over the same reward space — all at matched compute, on the
> same survivorship-free point-in-time universe, over the same costed out-of-sample period, inside one
> pre-registered multiple-testing family with PBO/CSCV and a Deflated Sharpe guard. That is the sense in
> which the method is competitive: not against an un-reproducible external leaderboard, but against the
> strongest controlled baselines, with the overfitting controls the external numbers lack."*

**Why this is the strongest defensible version:** it (a) concedes nothing false, (b) turns every weakness
of the SOTA band (different conditions, irreproducibility, overfitting) into *evidence of the project's
superior rigor*, (c) keeps the real, valid claim (internal ladder, matched, corrected) front and centre,
(d) survives the arms being absolutely below the band (the claim never depended on out-ranking them), and
(e) demonstrates exactly the backtest-overfitting + reproducibility literacy that a Distinction-grade,
citation-checked, viva-less PDF is marked on.

---

## Appendix — provenance of every external claim (first-hand this session unless noted)

- **FinRL issue #190 (Sharpe 0.162571→2.385978, seeds fixed):** github.com/AI4Finance-LLC/FinRL-Library/
  issues/190 — fetched, exact numbers confirmed.
- **FinRL Contest 2025 (Otago 1.08/+191%; Ruijian 0.95/+335%/−50.24%DD; Queen's Gambit 0.29/+342%/−92.47%DD;
  test 2019-01-01→2023-12-31, 1258 days; overfit rejection at 10%; "generalization remains a challenge"):**
  arXiv:2504.02281v3 — fetched, confirmed.
- **FinRL Contest 2023 9.56 artifact (15 trading days 2023-10-25→11-14, +3.50% cumret, −0.40% MaxDD):**
  arXiv:2504.02281v3 — fetched, confirmed verbatim.
- **Implementation risk (≤0.18% simple / up to 3.71% high-turnover divergence; CSI=0, no observed sign
  flip; ≥2 validators recommended):** arXiv:2603.20319 — fetched, confirmed (note the honest CSI=0
  correction).
- **DRL overfits (Sharpe 1.41 pre → 0.13 post-training; "capture patterns specific to the training set"):**
  arXiv:2511.11481v1 — fetched, confirmed.
- **Off-policy SAC/DDPG/TD3 "perform poorly" on noisy rewards; PPO/A2C cope; >2m steps ≈ 8,000 yrs:**
  arXiv:2307.07694 — fetched (abstract-level), confirmed.
- **Bailey-Borwein-López de Prado-Zhu (2014), "Pseudo-Mathematics and Financial Charlatanism," *Notices of
  the AMS* 61(5):458-471:** ssrn 2308659; ams.org/notices/201405/rnoti-p458.pdf — located + summarized.
- **Deflated Sharpe Ratio (Bailey & López de Prado 2014, *JPM*):** ssrn 2460551;
  davidhbailey.com/dhbpapers/deflated-sharpe.pdf — located.
- **Henderson et al. (2018), "Deep RL That Matters," AAAI:** ojs.aaai.org/index.php/AAAI/article/view/11694
  — located + summarized.
- **Stable-Baselines3 reproducibility disclaimer:** SB3 docs (surfaced via search) — "not guaranteed across
  PyTorch releases / platforms; not reproducible CPU vs GPU even with identical seeds."
- **Yang ensemble (1.30 ensemble / 0.47 DJIA / 0.45 min-var in the openfin/Columbia print; 1.53 variant in
  CAMPAIGN_benchmarks):** openfin.engineering.columbia.edu/.../ensemble.pdf; arXiv:2111.09395 — **PDF would
  not parse via WebFetch this session; numbers carried from CAMPAIGN_benchmarks §3 + the ensemble-print
  search hit; the 1.30-vs-1.53 discrepancy is itself the §2a point. `% VERIFY` the exact pairing.**
- **FinRL-Meta (ElegantRL 1.457 / SB3 1.621 stock; crypto 2.992); multimodal 0.86; EIIE crypto + leak:**
  carried from `docs/CAMPAIGN_benchmarks.md §3` (verified there; multimodal/EIIE not re-parsed this
  session). `% VERIFY` against primaries before the PDF.

**Internal facts (read first-hand, this + prior session):** `docs/CAMPAIGN_benchmarks.md` (§2–§4),
`docs/CAMPAIGN_attribution.md`, `00_planning/LITERATURE_AND_DEFENSE_COMPANION.md` (Parts 1–9),
`PREREGISTRATION.md` (§1, §2, §3, §10 + R11/R13/R15/R16/R17/R20), `docs/notes/{eureka,finrl_deepseek,
sood_2023}.md`, and the memory node `project-prototype-results-and-benchmarks` (winner DSR ranking; best
mean Sharpe ≈ −0.39 at 1 seed; 6 diverged runs (~2.5%; "64" was an `anomalies.jsonl` line-count, not a
run-count); the 6-tier ladder; directional-only status).
