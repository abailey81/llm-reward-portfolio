# Corpus deep-mining — PART 3: FINAL BATCH (L15/L16/L20) + CONSOLIDATED ACTION LIST

Companion to PART 1 + PART 2. **ALL 20 agents landed; entire 210-PDF corpus read in full.**
**★ NOVELTY VERDICT (unanimous across all 20 slices): the conjunctive cell — (LLM authors reward CODE) ×
(fixed portfolio SAC) × (multi-level realised-return tail as the MANIPULATED feedback variable) ×
(pre-registered controlled comparison) × (mechanism) — is UNOCCUPIED. No single paper, and no named pair,
covers it. 20 independent adversarial deep-reads, zero scoops.**

---

## FINAL-BATCH highlights (L15 distributional-reward-for-LLMs, L16 foundational canon, L20 closest-neighbours)

### L20 — closest neighbours (the decisive novelty read)
- **DLM (`behari2024dlm`, NeurIPS'24) = the STRUCTURAL TWIN** (LLM authors reward code + self-reflection on a *distribution* + IQM/200-seed rliable + a task literally named "Tail Emphasis"). BUT its fed distribution is a **demographic state-feature share** (public-health RMAB), not a realised-return CVaR/ES vector; Reflection-vs-No-Reflection is its only manipulation (not scalar-vs-content). **Pin our distinction to CONTENT (realised-return lower tail) + manipulation (IV) + finance + pre-registration — NEVER to "vector-vs-scalar" alone** (DLM §4.4 already uses vector feedback). Adopt its Table-1 features-used-vs-ground-truth precision/recall as a mechanism-audit precedent.
- **GIFT (`wu2026gift`, Jun'26) = tightest finance neighbour + lead fence** (LLM selects from a FIXED risk-rule library for PPO portfolio; grep-confirmed ZERO CVaR/ES/VaR — deepest risk stat = drawdown; co-varies state+reward; win-counting, no CIs, no pre-reg).
- **⚠ Qu-Fraud (`qu2025selfevolving`, ACL'25) is in refs.bib but UNCITED in CH2** — the closest finance-*adjacent* LLM-reward-CODE evolver (eBay fraud block/pass, scalar $-precision feedback). "First LLM-reward-code in finance" would be FALSE → **add a one-clause CH2 §2.2 fence** (zero-cost, key exists).
- **RewardIsEnough/ICRL (`song2025reward`, ICLR'26) = the published counter-claim to H2** → strengthen the §2.1 rebuttal: its "scalar > verbal" is scalar-vs-*hallucinated-free-form-verbal* (Reflexion), orthogonal to scalar-vs-*structured-verified-tail-vector*; and it concedes external-feedback has a higher ceiling than self-evaluation — our tail vector is external/verified.

### L15 — distributional-reward-for-LLMs (tri-partite fence)
- The bin splits into **(A) distributional reward MODEL** (QRM, DPRM — scalarized before the agent), **(B) distributional CRITIC** (DFPO/DVPO/Q# = the LLM-world analog of our *secondary* DSAC/TQC axis), **(C) risk-as-the-agent's-OBJECTIVE** (RA-RLHF CVaR, RiskPO MVaR). **None feeds a tail vector to a reward-CODE author with the agent fixed.** Replace the single-lump boundary-hazard note (`RELATED_WORK_WATCH.md:42-43`) with this three-way split.
- **6-source "mean/scalar discards the tail" corroborator set** (RA-RLHF, QRM, RiskPO, DAR-formal-proof, DFPO/DVPO, Distributional-Reasoning) → the cross-domain evidence base for H2's premise (frame with the transmission caveat: none feeds a designer).
- Fence trio: **RiskPO** (MVaR multi-region ≈ spectral → protects the "multi-level" claim), **RA-RLHF** (CVaR-for-an-LLM bridge + adoptable reward-vs-return-quantile H2-Tail exhibit), **QRM** (entropic left-tail utility).

### L16 — foundational canon (all cites verified accurate — no mis-attribution)
- **DISCHARGE the `heavytailsDM2026` `% VERIFY`** (refs.bib:1846, read first-hand; CH7 B.5.2 accurate). Nuance: our returns near cubic-law **κ≈3 (finite variance)** → the Sharpe differential is in the Gaussian-safe zone; the **FZ0/ES differential** is the at-risk quantity (squared loss halves κ); our skew +0.21 is mild → don't quote the 70%. Since we predict a **null**, non-robust DM's over-rejection works *against* the null → the self-normalized subsampling DM/SPA test (Alg 3.1/Thm 3.2) *protects* the null claim. (Incidental: the authors disclose "Opus 4.6" as a language-editing tool — precedent for our AI-disclosure.)
- **rliable precision:** M=1 single market → "stratified" needs a genuine stratum (regime sub-periods) or soften to "paired seed bootstrap"; confirm the IQM trim is at the across-seed level. **SAC Thm 1 is tabular-only** → cite as positive support for the bounded-agent premise.

---

## ★★ CONSOLIDATED PRIORITISED ACTION LIST (all 20 slices) — for Tamer

### TIER 0 — corpus-grounding gaps that VIOLATE priority #4 (dead/uncited, highest ROI)
1. **Wire in the 6 L-bin refs.bib ORPHANS** (cited in ZERO chapters → **will not appear in the PDF**): `kwon2023rewarddesignlm` + `du2023ellm` (§2.1 lineage taxonomy: LLM-as-value-emitter → goal-proposer → code-author), `jaimungal2021robustriskaware` + `greenberg2022efficientriskaverse` + `tang2019worstcases` (§2.3 risk-in-critic-vs-feedback; Greenberg "blindness to success" justifies our off-critic design), `hambly2021rlfinancesurvey` (CH1/CH2 — sources the "field feeds scalar Sharpe/return, never a tail vector" claim + its §5 risk future-work motivates us).
2. **Cite the 3 uncited-but-mapped canon keys:** `fujimoto2018td3` (CH7 B.2.3 critic-divergence + CH4:74 twin-critic min), `buehler2019deephedging` (§2.3 risk-in-objective contrast + OCE→CVaR §3.6), `schulman2017ppo` (low).
3. **Cite `troop2021biascorrected` in prose** (CH4 §4.4, CH7 B.5.2 — defined-but-uncited) AND reword the EVT deferral (see corrections).
4. **Cite `sorg2010internal`, `bailey2014pseudomath`, `acerbi2002spectral`** more (all cited-but-underused; the null-anchor + spectral-basis + MinBTL leverage).
5. **Clear 3 stale DO-NOT-CITE flags** (verified real first-hand): QRM `2409.10164`, RiskPO `2510.00911`, RARL `2602.09305` (`RELATED_WORK_WATCH.md:143,170`).

### TIER 1 — LOAD-BEARING corrections (fix before freeze/submission)
- **DSAC misfiled → `ma2020dsac` not first-hand-verified** (add `duan2021dsac` for the variance-clip point; fix CH2:137). **Cartea byline → Coache/Jaimungal/Cartea 2023.** **Kusuoka atomless precondition §3.5** (also P30). **FZ Cor 5.4 check: does the fed vector include the VaR quantiles?** **FZ2016-vs-Nolde-Ziegel + Chow-2015 α-convention** sign/convention consistency (M1 box). **"Zero pre-registrations" misattribution** (reword RWW #8). **Negative-skew warning** (our skew is +0.21; don't cite Cont fact#3). **ARM-FM 300k plateau is DQN not SAC** (fix CAMPAIGN_DESIGN). **NatGas "monotone"→"tunable"**; **map "examiner Jaimungal"→Okhrati**. **Troop EVT wording** (rest on estimator-instability + heavy-tail-only scope; re-measure ξ̂ on Split-C; drop "light-tailed/94%-population" framing).

### TIER 2 — novelty fences to ADD/sharpen in CH2 + RELATED_WORK_WATCH
DLM (structural twin — pin to content+IV+finance+prereg), GIFT (drawdown-not-CVaR), **Qu-Fraud (add the missing fence)**, RewardIsEnough (strengthen rebuttal), RiskPO/RA-RLHF/QRM (tri-partite fence for "multi-level tail"), FINCON (CVaR-verbal-trigger+scalar-PnL), ONI (2-family taxonomy locates us), CoopMARL (closest structured-feedback), ICPL (30-budget + monotonicity control), SHARP (worst-K-day to a rubric editor), Coache-Jaimungal Robust Distortion (the G2 non-LLM portfolio comparator), RD-Agent ("8-dim vector to an LLM loop is not novel" — our cell = reward CODE × multi-level tail × pre-registered).

### TIER 3 — deep hooks to USE (priority #4 depth, examiner-grade)
- **Numeracy-bottleneck cluster** (OPRO-hallucination + Wallace + ERFSL + URDP/L2R + Batra + Hartley risk-neutral-default) → grounds the ADR-039 reframe; frontier-Opus ⇒ null isn't a capability floor.
- **Ng ⊂ Skalse-unhackable ⊂ hackable ladder** → locate the (tail−scalar) reward pair (mechanism).
- **Khraishi-Okhrati α→0=SAC bridge + Hartley CE-CPT probe on Opus 4.8** (examiner-authored null prediction + a buildable manipulation check).
- **RU Gaussian-collapse + Sorg intermediate-boundedness + PseudoMath compensation + Rowland Bellman-closedness + Moghimi-Ku "blindness to success"** → the null-plausibility theory stack + why MULTI-level.
- **6-source scalar-discards-tail set + Hambly "field feeds scalar" + Bailey-2012 PSR mixture-of-Normals** → the "why a tail vector" motivation.
- **P6/P9 contamination reframe** (structural §4.5 defence; P9 COVID-exclusion = contamination-hygiene benefit; P6 common-mode+conservative; CMMD cross-model Opus+Qwen).
- **Bauer power table + heavytailsDM subsampling DM** → "non-rejection at the tail is a weak test," CVaR-25/10 more reliable than 5/1, and the robust test *protects* the predicted null.
- **Mechanism-audit methodology:** AutoML-Zero (auto-simplify → convergent motifs → knock-out/knock-in; hyperparameter-coupling = surface-echo) + DLM feature precision/recall + LERO/GLO symbolic analysis + Pan ontological-misspecification.
