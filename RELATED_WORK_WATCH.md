# RELATED_WORK_WATCH.md — Novelty surveillance log

The novelty claim is conjunctive — (LLM reward-code synthesis for portfolio RL) ∧ (distributional-critic
feedback to the LLM designer) — and is always stated with a "to the best of our knowledge" hedge plus the
date of the most recent sweep below. Re-sweep monthly and in the week before any submission.

**Standing queries.** "LLM reward design finance/trading/portfolio" · "Eureka finance" · "reward code
generation financial RL" · "distributional feedback LLM reward" · "quantile/CVaR feedback reward design
language model" · citation lists of Eureka (2310.12931), Text2Reward (2309.11489), FinRL-DeepSeek
(2502.07393) on Semantic Scholar/Google Scholar · ICAIF accepted-paper lists · FinRL Contest task pages.

---

## Entry 1 — 2026-06-10 (two adversarial deep-research sweeps)
**Result: gap intact on the conjunction.** No located work applies Eureka/Text2Reward-style LLM
reward-*code* synthesis to trading or portfolio RL; no located work in ANY domain feeds distributional-critic
(quantile/CVaR/tail) statistics back to an LLM reward designer.
**Closest prior art (cite-and-distinguish list):**
- FinRL-DeepSeek (Benhenda 2025, arXiv:2502.07393): LLM **signals** (news → risk/recommendation scores)
  into a hand-specified CVaR-PPO; Nasdaq-100 2013–2023. *Signal-generator, not reward-designer.*
- Unnikrishnan 2024 (arXiv:2411.11059): LLM sentiment inside a hand-designed reward. Same category.
- LEARN-Opt (arXiv:2511.19355) & "When LLM Reward Design Fails" (arXiv:2605.28918): LLM reward design
  variance/failure-mode evidence in control domains — methodological allies, not competitors.
- Dorka 2024 (arXiv:2409.10164): quantile regression *inside* RLHF reward models — different object entirely.
- RAMAC (arXiv:2510.02695): IQN critic + CVaR actor, offline RL, **no LLM**.
**Next sweep due:** ~2026-07-10, and again in the week before the 2 Aug ICAIF deadline.

## Entry 2 — 2026-06-19 (10 GitHub-repo deep-research agents; reward-codegen SOTA + finance-RL + novelty sweep)
**Result: gap intact on the conjunction (verified mid-2026).** Exhaustive sweep of 2025–2026 reward-code-generation
+ agentic-code-evolution work found NO repo/paper feeding a realized-return DISTRIBUTION (CVaR profile / tail-mass /
skew) back to an LLM reward-CODE DESIGNER. (One WebFetch summary falsely claimed URDP "feeds CVaR to the LLM" —
verified FALSE against the abstract; do not repeat that phrasing.)
**New cite-and-distinguish neighbours (tightest yet — all reward-CODE designers, none distributional):**
- CARD (arXiv:2410.14660, KBS 2025): LLM Coder+Evaluator reward-code, **preference/TPE** feedback, control. % VERIFY
- URDP (arXiv:2507.02256): uncertainty-aware reward design via **candidate self-consistency** (skip sims), control. % VERIFY
- PROF (arXiv:2511.13765): LLM reward-code + offline imitation, **preference ranking**, Meta-World/ManiSkill2. % VERIFY
- LaRes (NeurIPS-2025, MIT): population reward-code + Thompson selection, **scalar** policy fitness, MetaWorld. % VERIFY
**Agentic-code-evolution canon (cite for lineage + the feedback taxonomy):** OpenEvolve (codelion, Apache-2.0 — its
evaluator "artifacts side-channel" is the implementation precedent your distributional feedback block instantiates);
Darwin-Gödel-Machine (arXiv:2505.22954); ADAS survey — its feedback taxonomy (scalar / preference / NL-critique /
surrogate / novelty) does NOT list a return distribution, which frames H2's novelty positively.
**Boundary hazard to state explicitly:** the distributional-RLHF reward-model cluster (Dorka QRM 2409.10164; Quantile
Reward Policy Opt 2507.08068; RiskPO 2510.00911) is "distribution INSIDE the reward model for RLHF" — the WRONG object
(reward that trains an LLM, not feedback to a reward-DESIGNER). State H2's novelty is the feedback DIRECTION explicitly.
**Must-watch (re-sweep monthly):** AlphaEvolve + OSS replicas (CodeEvolve, AlphaResearch); QuantEvolve/pwb-alphaevolve
(an OpenEvolve trading-strategy fork — the most plausible future collision vector); FinRL Contest tasks.
**Next sweep due:** ~2026-07-19, and the week before the ICAIF deadline.

## Entry 2b — 2026-06-19 (meta-sweep of curated lists; exhaustiveness confirmed)
**The relevant repo space is now EXHAUSTIVELY covered** — 6 sweeps over awesome-quant / systematic-trading /
AI-in-finance / deep-RL / distributional-RL / LLM-agents / reward-learning / code-LLM / MLOps / reproducible-research
(+ GitHub search) converged with no new survivors. Two re-confirmations: NO open "LLM-writes-reward-code-for-finance"
system exists (validates N2 novelty); NO maintained, permissively-licensed all-in-one DSR+PBO package exists (validates
building custom audited inference) — **pypbo** (AGPL) is the READ-ONLY DSR/PBO oracle; **timeseriescv** (MIT) / skfolio
`CombinatorialPurgedCV` (BSD) are the clean purged-CV splitters to cross-check CSCV.
**One high-value NEW anchor — GEPA** (`gepa-ai/gepa`, MIT, 5.2k★; arXiv:2507.19457 — % VERIFY): paper-validated thesis
that reflecting on a RICH TEXTUAL TRACE beats "collapsing execution traces into a single scalar reward" — an
INDEPENDENT cross-domain validation of the exact H2 premise (distributional trace > scalar). CITE as the nearest
methodological anchor for H2 (caveat: GEPA benchmarks prompt-optimization, generalizes to code → a neighbour, not a
baseline to beat; borrow its rich-trace-vs-scalar framing + Pareto-frontier candidate archive as design references).
Add to related work the LLM-as-optimizer / self-improving-code lineage: Trace/OptoPrime, OPRO, TextGrad, ShinkaEvolve,
**REvolve + ICPL** (evolve reward-CODE on this exact task but with HUMAN/PREFERENCE feedback — the clean contrast to
numeric/distributional), and xtma/dsac (CVaR-distorted SAC prior art).
**Reconciliation:** the meta-sweep's "adopt Hydra/DVC/MLflow/pixi/sbx" suggestions are OVERRIDDEN by the deeper
dedicated tracks — Hydra/DVC/MLflow conflict with the frozen-prereg + replay-archive + contamination design (dev-tooling
track), and SBX replaces the fixed agent + has no native-Windows CUDA (numerical-RL track). Project-specific deep
analysis beats the broad meta-sweep on tooling fit.

## Entry 3 — 2026-06-19 (FINAL mid-2026 check: AlphaEvolve/OpenEvolve trading-fork wave + oracle re-scan)
**Result: gap INTACT on the conjunction; one oracle UPDATE (esback=GPL, NOT clean) + two clean EVT alternatives logged.**
A wave of 2026 AlphaEvolve/OpenEvolve trading forks surfaced — ALL are STRATEGY/ALPHA-CODE evolvers with SCALAR fitness,
NO RL agent, and NO return-distribution/CVaR feedback to the LLM. The precise deltas (each a one-line distinguisher):
- **QuantEvolve** (arXiv:2510.18569 % VERIFY; repo `tarsyang/quantevolve`, **Apache-2.0**): MAP-Elites/island QD evolving
  full Zipline strategies; fitness `Score = SR + IR + MDD` (scalar). δ: strategy-code not reward-code; QD not RL; no tail-to-LLM.
- **MadEvolve** (arXiv:2605.23007 % VERIFY; madevolve.org, license unstated): AlphaEvolve-style EVOLVE-BLOCK feature/strategy
  evolution on BTCUSD; fitness = impact-adjusted PnL (scalar); drawdown/Calmar computed post-hoc, never fed back. δ: no RL, no CVaR-to-LLM.
- **QuantaAlpha** (arXiv:2602.07085 % VERIFY): evolves alpha-FACTOR AST expressions; terminal reward = IC/RankIC/ARR/MDD (scalar). δ: alpha-factor not reward-code; no RL.
- **pwb-alphaevolve** (repo `paperswithbacktest/pwb-alphaevolve`, **MIT**): Backtrader strategy evolution; scalar Sharpe/CAGR/Calmar/DD. δ: strategy-code, no RL, no distributional feedback.
- **CodeEvolve** (arXiv:2510.14150 % VERIFY; `inter-co/science-codeevolve`, open): GENERAL-purpose program evolution (circle-packing/scheduling), scalar fitness, no finance/CVaR. δ: not finance, not reward-code.
**Reward-CODE designers (control/robotics; tightened the cite-and-distinguish list — none distributional, all confirmed):**
- **CARD** (arXiv:2410.14660, KBS 2025; repo `ShengjieSun419/CARD`): RESOLVED — the ScienceDirect "dynamic-feedback reward-design"
  paper IS CARD. Coder+Evaluator reward-code, **Trajectory-Preference-Evaluation (TPE)** feedback, control. δ: preference not distribution; control not finance.
- **PROF** (arXiv:2511.13765 % VERIFY): LLM reward-code + offline imitation; **Reward-Preference-Ranking (RPR)** dominance scores, MetaWorld/ManiSkill. δ: preference-ranking not distribution.
- **LaRes** (NeurIPS-2025; repo `yeshenpy/LaRes`): reward-code POPULATION + **Thompson-sampling** elite selection, **scalar** policy fitness, 12 MetaWorld tasks. δ: scalar fitness not distribution; robotics.
- **URDP** (arXiv:2507.02256 % VERIFY): uncertainty-aware reward-code via **self-consistency** (epistemic uncertainty to skip sims), control. δ: epistemic-uncertainty not realized-return tail.
- **GEPA** (arXiv:2507.19457 — now **ICLR-2026 Oral**, was % VERIFY; `gepa-ai/gepa`, MIT — now optimizes "prompts, code, and more"):
  UPGRADE the H2 anchor — paper-validated "rich textual trace > single scalar reward". Still a NEIGHBOUR (prompt/code opt, not portfolio-RL), not a baseline to beat.
**FinRL-Contest:** 2025 had 4 tasks (FinRL-DeepSeek, FinRL-AlphaSeek, Open-FinLLM ReFT, DRR) — NONE write reward-code, NONE feed
CVaR to an LLM; **no 2026 contest announced yet** (re-check). **ICAIF'26 confirmed: Milan, 14-17 Nov 2026, deadline 2 Aug 2026.**
**ICAIF'25 accepted-list scan:** no Eureka-style reward-design-for-finance; nearest is **TS-Agent** (arXiv:2508.13915, "Structured
Agentic Workflows", NUS/UCL/Edinburgh) — agentic time-series MODELING (select/refine/fine-tune) w/ reflective feedback, NO RL agent, NO reward-code, NO tail. Clear miss.
**ORACLE re-scan (Mandate b):** NOTHING NEW for the bespoke studentized CVaR-DIFFERENCE test — still NO published named two-sample
difference-in-CVaR test and NO library function (statsmodels/arch lack it); the `null_calibration` empirical-size certification
remains the correct approach. **NEW for FZ0/ES backtest:** R **`esback`+`esreg`** (Bayer-Dimitriadis 2020 ES-regression backtest)
exists but is **GPL-3 — NOT license-clean** for an MIT repo and has **no Python port**; treat like pypbo (read-only cross-check in R only, never vendor).
**NEW clean EVT alternatives** (besides the pinned `pyextremes`): **scikit-extremes** (MIT) and **thresholdmodeling** (MIT, JOSS) —
both GPD/POT estimators; `pyextremes` stays the primary oracle, these are MIT-clean backups to cross-check `scipy.stats.genpareto.fit`.
**Bottom line:** novelty conjunction holds; the closest collisions are now reward-CODE designers in robotics (CARD/PROF/LaRes/URDP)
and finance strategy/alpha evolvers (QuantEvolve/MadEvolve/QuantaAlpha/pwb-alphaevolve) — the H2 distinguisher (realized-return
DISTRIBUTION fed back to a reward-CODE DESIGNER for a FIXED SAC agent) is unoccupied on BOTH axes simultaneously.
**Next sweep due:** ~2026-07-19, and the week before the 2 Aug ICAIF deadline (watch QuantEvolve/pwb-alphaevolve for a CVaR-feedback commit; watch FinRL-Contest-2026 announcement).

## Entry — 2026-06-27 (6-agent corroboration sweep: new-tech + GitHub-repos + tooling)
**Result: novelty conjunction INTACT (third independent confirmation).** No paper or public repo occupies the
LLM-reward-**code** × portfolio RL × EVT/GPD-tail-feedback × SAC/TQC intersection. Full capture in
`docs/RESEARCH_SCAN_2026-06-27.md`.
**Re-confirmed closest neighbours (verified first-hand; already tracked above):** FinRL-DeepSeek (2502.07393,
LLM-signal-into-fixed-CPPO — the one mandatory fence + natural ablation baseline), CARD (2410.14660,
reward-code but no scalar-vs-multilevel ablation).
**New cite-and-distinguish neighbour:** Risk-sensitive RL via **Convex Scoring Functions** (Han, Liu, Yu —
arXiv:2505.04553, May 2025): elicitability/Fissler–Ziegel tied to RL objectives (CVaR/ES/EVaR), stat-arb app.
*Optimises the objective via convex scoring; we author the reward program.* Closest neighbour on the
elicitability axis — pre-empt explicitly. % VERIFY
**Methods-defensibility (zero-compute citation upgrades):** Fissler-Liu-Wang-Wei 2024 (arXiv:2404.14136, *Math.
Finance* 2025 — replace stale 2015/16 elicitability cites); Coronéo-Iacone 2024 (arXiv:2409.12662 — DM power
under serial correlation, one sentence by the HLN correction); López de Prado-Lipton-Zoonekynd 2025 (SSRN
5520741 — DSR refresh); AdaStop (TMLR Dec 2024, arXiv:2306.10882 — seed-budget lane, cite + differentiate from
our pre-registered fixed-N rliable design). All % VERIFY.
**Future Work (do NOT add to frozen pipeline):** nsEVDx (arXiv:2509.07261 — non-stationary GPD with VIX
covariate); Hué-Hurlin-Lu 2024 (arXiv:2405.02012 — duration/severity ES backtest).
**Integrity:** several search-listing-only IDs were flagged UNVERIFIED (see `docs/RESEARCH_SCAN_2026-06-27.md`
§6) and must NOT enter `refs.bib` as confirmed.
**Next sweep due:** unchanged (~2026-07-19 + week before ICAIF).

## Entry — 2026-06-28 (deep-research harness: 99-agent, 3-vote adversarial verification)
**Result: NO SCOOP — novelty conjunction confirmed UNOCCUPIED at HIGH confidence** (24/25 claims survived 3-0
adversarial verification; run wf_3e5ea496-4d7). Verdict + fences are now source-verified, not sweep-asserted.
- **Verified neighbour fences:** Eureka (2310.12931, ICLR 2024, robotics, reward-reflection = scalar training
  stats), CARD (2410.14660, KBS 2025, reward-code but TPE *preference* feedback, robotics), URDP (2507.02256,
  self-consistency uncertainty over candidate code, robotics), FinRL-DeepSeek (2502.07393, LLM *scores* into a
  FIXED reward, **CPPO not SAC**), Han-Liu-Yu convex-scoring risk-RL (2505.04553, **no LLM**, custom
  actor-critic, stat-arb = single-pair not portfolio [2-1 caveat]). Each fails >=1 prong.
- **Verified methods backbone:** McNeil-Frey 2000 (J.Emp.Fin 7(3-4):271-300, GARCH-EVT/POT CVaR);
  Bayer-Dimitriadis 2022 (J.Fin.Econometrics 20(3):437-471, regression ES backtest); Fissler-Liu-Wang-Wei
  2024 (arXiv:2404.14136, *Math. Finance* 2025, doi:10.1111/mafi.70016, nests FZ (VaR,ES) scores);
  Rockafellar-Uryasev (CVaR coherence — cite for general-distribution CVaR/coherence ONLY; the "multi-level
  coherent tail-profile" framing was REFUTED 0-3, do not over-claim it).
- **CITATION CORRECTION (verified):** arXiv:1503.08123 = Fissler-Ziegel "Higher Order Elicitability and
  Osband's Principle", **Annals of Statistics 44(4):1680-1707 (2016)** — coordinates now CONFIRMED (the
  refs.bib `% VERIFY` on that entry is CLEARED). DISTINCT from the short Risk note arXiv:1507.00244
  (Fissler-Ziegel-Gneiting, Risk Jan 2016 pp.58-61) on the joint (VaR,ES) backtest. (1507.00244 is not in
  refs.bib; no conflation present.)
- **STILL UNVERIFIED (do NOT cite):** the 8 flagged IDs (2602.09305, 2605.08061, 2409.10164, 2512.23139,
  2605.23007, SSRN 5950754, Wang-Liu JRFM 2025, Grant et al. J.Forecasting 2026) were NOT resolved — several
  imply 2026 dates beyond the verification horizon. Confirmed ABSENT from refs.bib (hygiene held). Also
  unverified in this run (fetched but below the verify-budget): HLN 1997, Coroneo-Iacone 2409.12662,
  Bailey-LdP DSR/PBO, rliable 2108.13264, Text2Reward 2309.11489, OPRO 2309.03409 — resolve before relying.
**Next sweep due:** unchanged (~2026-07-19 + week before ICAIF).


## Entry 7 — 2026-06-28 (cutting-edge 2024-2026 sweep, 100 agents + 196-PDF corpus deep-read, 13 agents)
**Result: novelty conjunction STILL EMPTY — HIGH confidence** (cutting-edge sweep: 24 unanimous 3-0 claims;
corpus read: 0 conjunction breaches across all 196 owned papers). No verified work combines all legs:
LLM-authors-reward-CODE + fixed-SAC + risk-sensitive PORTFOLIO RL + multi-level EVT/CVaR tail-feedback-vs-scalar.
- **LLM-writes-reward-code lineage (robotics/control, NO finance/tail):** RF-Agent (NeurIPS 2025, MCTS over
  reward code), LEARN-Opt (Nov 2025, autonomous, no env-source), URDP, CARD — RELATED-WORK, none scoop.
- **Finance-LLM-RL (LLM=signal, hand-designed reward):** FinRL-DeepSeek (2502.07393, closest competitor; LLM
  emits news signals into CPPO, not reward code; no SAC; no tail-feedback comparison), HARLF. Do NOT scoop.
- **Risk-sensitive/distributional RL (NO LLM):** Tail-Safe Hedging IQN-CVaR-PPO, MARCD, Boosting-CVaR-PG.
- **1 actionable scoop to manage (corpus read):** ELfolio (2025) — the only un-managed nearest-neighbour in the
  portfolio+risk+LLM+RL cell. ACTION: verify its id first-hand, then add a cite-and-distinguish sentence.
- **TECHNIQUE-TO-CONSIDER passing the determinism + LSEG-licence + no-scope-creep gate: NONE.** Design stays clean.
**Corpus leverage gaps (docs/LITERATURE_INTEGRATION_MAP.md):** promote the keyless reporting-multiplicity family
(White 2000, Hansen 2005, Romano-Wolf 2005, Ledoit-Wolf 2008, Harvey-Liu-Zhu 2016); cite the Data cost-model
cluster (Kyle, Almgren-Chriss, Toth, Cont) — currently 0 disk-read cites; split the ORP theory spine
(sorg2010orp key title is "Reward Design via Online Gradient Ascent" — separate from Sorg 2011 PhD; add Ng 1999
shaping, Singh 2010 IMRL). 3 mislabeled corpus files (FinRLlama DOI, Cheridito-Stadje Time-INconsistency,
Maillard=Cagna-Casuccio), 1 unparseable (Follmer-Schied — do not quote).
**CITE-INTEGRITY:** suspicious 26xx ids (incl. RF-Agent 2602.23876) -> cite VENUE (NeurIPS 2025) + % VERIFY until
first-hand checked. DO-NOT-CITE re-confirmed: 2602.09305, 2604.23505, 2602.18053, 2605.08061, 2512.23139,
2605.23007, 2605.28918, SSRN 5950754 — none enter refs.bib unverified.
**Next sweep due:** week before ICAIF submission.

## 2026-06-28 — Deep-dive corpus additions (verified, staged in paper/refs_staging.bib)

All six below were arXiv-id-VERIFIED (abs page + cross-check) and page-1-read first-hand via PyMuPDF before staging. PDFs in `01_literature/L_deepdive_additions/`. Staged as `% VERIFY` entries only — NOT merged into refs.bib.

- **Kwon, Xie, Bullard, Sadigh — "Reward Design with Language Models" (ICLR 2023), arXiv 2303.00001.** LLM-reward-proxy lineage: the direct ancestor where an LLM IS the reward function via a natural-language prompt. CORRECTION: candidate-supplied authors "Boutilier, Finn" were wrong; verified authors are Kwon / Sang Michael Xie / Kalesha Bullard / Dorsa Sadigh. (The round-number id 2303.00001 is nonetheless the correct canonical id.)
- **Du, Watkins, Wang, Colas, Darrell, Abbeel, Gupta, Andreas — "Guiding Pretraining in RL with LLMs (ELLM)" (ICML 2023), arXiv 2302.06692.** LLM-reward-proxy lineage: LLM-prompted exploration reward shaping; close neighbour to LLM-designs-reward.
- **Jaimungal, Pesenti, Wang, Tatsat — "Robust Risk-Aware Reinforcement Learning", arXiv 2108.10403 (2021).** Risk-aware RL neighbour: RDEU + Wasserstein-ball-robust risk-aware policy optimisation.
- **Tang, Zhang, Salakhutdinov — "Worst Cases Policy Gradients" (Apple), arXiv 1911.03618 (2019).** Risk-aware RL neighbour: CVaR-level actor-critic over the modelled return distribution. (Exact title is "Worst Cases", not "Worst-Cases".)
- **Greenberg, Chow, Ghavamzadeh, Mannor — "Efficient Risk-Averse Reinforcement Learning", arXiv 2205.05138 (2022).** Risk-aware RL neighbour: CVaR/soft-risk optimisation, local-optimum-barrier result + cross-entropy sampler.
- **Hambly, Xu, Yang — "Recent Advances in Reinforcement Learning in Finance", arXiv 2112.04553 (2021).** Finance-RL survey situating the portfolio-RL problem setting. (First posted Dec 2021; PDF v3 dated Mar 2023.)


## Entry 3 — 2026-06-28 (5-agent frontier + scoop sweep: selective inference / Bayesian-null / RL-eval / risk-backtesting / LLM-reward tooling)
**Result: gap intact on the conjunction (re-verified mid-2026).** A five-axis sweep of 2025-2026 work found NO paper holding the full conjunction {LLM authors reward CODE} x {multi-level tail-risk feedback CONTENT as the manipulated variable} x {fixed SAC agent} x {finance/portfolio} x {pre-registered placebo-controlled causal test}. The space stays split into two unjoined halves: finance-LLM-RL (no reward-code authoring, no feedback-content IV) and code-authoring reward design (robotics, scalar feedback, no pre-registration).
**New closest prior art to cite-and-distinguish (the IV axis):**
- **URDP - "Uncertainty-aware Reward Design Process" (Yang et al. 2025, arXiv:2507.02256 % VERIFY).** The NEAREST IV-axis neighbour and the biggest claimed scoop risk; fetched first-hand. Robotics; its "uncertainty" is self-consistency UQ over LLM outputs + Bayesian-opt hyperparameter tuning - NOT a distributional-tail feedback CHANNEL and NOT a scalar-vs-distributional feedback-content manipulation. No finance, no CVaR, no pre-registration, no placebo. -> cite-and-distinguish on (feedback-content-as-IV, finance/CVaR, pre-registered placebo control); the differentiation is cleaner than it first appears.
- **MadEvolve (2026, arXiv:2605.23007 % VERIFY):** finance + LLM-writes-code, but evolves STRATEGY code directly - no RL agent, no reward-for-a-fixed-agent. Structurally unrelated.
**Currency citations to fold into the relevant chapters (NO design change):**
- Reward-distance pseudometrics: EPIC/STARC remain SOTA mid-2026; add **SRRD (arXiv:2504.11508 % VERIFY)** (coverage-sensitivity patch for transition-sparse MDPs - our portfolio MDP) and **DARD (arXiv:2201.10081 % VERIFY)**.
- Negative-responsiveness / LLM-numeracy (Discussion): **Nie et al. 2024 (arXiv:2405.16434 % VERIFY, directional vs scalar feedback)** = the best mechanistic cite; **Yang-Leitner-Burke 2025 (arXiv:2507.14906 % VERIFY)**; **Shi et al. 2023 (arXiv:2302.00093 % VERIFY)**; **Levy-Geva 2024 (arXiv:2410.11781 % VERIFY, digit base-10 encoding)**.
- Reward-hacking / specification-gaming (Discussion): Skalse 2022 (2209.13085), Pan 2022 (2201.03544), Gao 2023 (2210.10760), Karwowski 2024 (2310.09144) - all % VERIFY.
- RL-evaluation authority alongside rliable (Agarwal 2021): **Patterson, Neumann, White & White 2024, "Empirical Design in RL", JMLR (arXiv:2304.01315 % VERIFY)** + Jordan et al. ICML 2024 (arXiv:2406.16241 % VERIFY).
**Action before freeze:** add URDP to the cite-and-distinguish fence and the dossier (an examiner on the IV axis will look for it). The rest are write-up citations, not design changes; all arXiv ids stay % VERIFY until checked first-hand.
**Next sweep due:** the week before the 2 Aug ICAIF deadline.
