# Missing-Citations Manifest

Dangling citation keys: cited in `paper/*.md` but **absent from `paper/refs.bib`**.
Generated 2026-06-28. Total dangling keys at generation: **104**.

> ## ✅ MERGE STATUS (2026-06-28, post-review)
> After human review of `paper/refs_staging.bib`, **61 of 104 dangling keys were resolved** and `refs.bib`
> grew 61→117 entries (zero duplicate keys; freeze hash unchanged):
> - **56 entries MERGED** into `refs.bib` (17 CORPUS-VERIFIED first-hand + 39 CLASSIC-`% VERIFY`).
> - **5 ALIAS keys RENAMED in the chapters** (not duplicated): `fisslerziegel2016higher`→`fissler2016higherorder`,
>   `rockafellar2000optimization`→`rockafellar2000cvar`, `skalse2022defining`→`skalse2022reward`,
>   `lopezdeprado2018advances`→`lopezdeprado2018afml`, `jiang2017deeprl`→`jiang2017eiie`.
> - **2 HELD (not merged)** — UNCERTAIN referent, confirm at reference round: `harvey1997testing`, `witzany2021bayesian`.
>
> **43 keys REMAIN dangling** = the reference-round / web-verify task (NONE fabricated):
> 32 NEEDS-WEB-VERIFY + 9 SUSPICIOUS-≥2025 (incl. `kvasiuk2026madevolve` highest-risk) + the 2 held.
> The 2 newly-caught MISLABELED corpus files (`ma2020dsac`→AI-Feynman, `li2024automc`→ELfolio/LopezLira) stay
> NEEDS-WEB-VERIFY. All `% VERIFY`-flagged merged entries still need coordinate confirmation before final submission.

Proposed BibTeX entries (STEP 2 + STEP 3) were staged in **`paper/refs_staging.bib`**
for human review (now merged per the status box above).

## Status legend

| Status | Meaning |
|---|---|
| **CORPUS-VERIFIED** | Page 1 of a matching on-disk PDF in `../01_literature` read first-hand; coordinates transcribed exactly. Entry written in `refs_staging.bib`. |
| **CLASSIC-%VERIFY** | Famous pre-2024 work NOT in corpus; canonical coordinates supplied with a `% VERIFY` note. Entry written in `refs_staging.bib`. |
| **NEEDS-WEB-VERIFY** | >=2024 (or otherwise unverifiable-from-disk) paper, plausibly real but not confirmable from corpus. **No entry written** — verify on the web before citing. |
| **SUSPICIOUS** | >=2025/2026-dated, not on disk; treat as possible hallucination until confirmed. **No entry written.** |
| **MISLABELED / FALSE-MATCH** | The surname+year heuristic matched an on-disk PDF that is a *different* paper. **Do not cite from that file.** |

`ALIAS-CANDIDATE` (noted inline in the staging .bib): the key is an alternate spelling of an entry **already present** in `refs.bib`; prefer renaming the in-text citation over adding a duplicate row.

---

## CORPUS-VERIFIED (entry in refs_staging.bib)

| key | chapter(s) | status | source PDF / note |
|---|---|---|---|
| almgren2005direct | CH7 | CORPUS-VERIFIED | MarketImpact-Almgren__2005.pdf (venue/pages not on p.1 → % VERIFY) |
| amodei2016concrete | CH1 | CORPUS-VERIFIED | ConcreteProblems-Amodei__2016.pdf (arXiv:1606.06565 on p.1) |
| bailey2014pseudomath | CH2 | CORPUS-VERIFIED | PseudoMath-Bailey__2014.pdf (distinct from existing bailey2014deflated) |
| brown1992survivorship | CH4 | CORPUS-VERIFIED | SurvivorshipBias-Brown__1992.pdf (RFS 5(4):553-580 on p.1) |
| chow2015risk | 02_theory | CORPUS-VERIFIED | CVaR-Robust-Chow__2015.pdf (Chow/Tamar/Mannor/Pavone; matches robust-MDP usage, NOT the 2014 CVaR-MDP file) |
| fisslerziegel2016higher | 02_theory, CH2 | CORPUS-VERIFIED · ALIAS-CANDIDATE | FisslerZiegel-HigherOrderElicitability__2016.pdf (alias of existing fissler2016higherorder) |
| frazzini2018trading | CH7 | CORPUS-VERIFIED | TradingCosts-Frazzini__2018.pdf (working paper; no published venue on p.1) |
| hansen2005spa | CH2 | CORPUS-VERIFIED | Hansen-SPA__2005.pdf (JBES; vol/pages not on p.1 → % VERIFY) |
| harvey2016cross | CH2 | CORPUS-VERIFIED | HarveyLiuZhu-CrossSection__2016.pdf ("...and the Cross-Section of Expected Returns", RFS 2016) |
| kusuoka2001law | 02_theory, CH2 | CORPUS-VERIFIED | Kusuoka-LawInvariant__2001.pdf (p.1 footer = RIMS Kokyuroku 1215; canonical = Adv. Math. Econ. 3 → % VERIFY) |
| pan2022effects | CH1 | CORPUS-VERIFIED | RewardMisspecification-Pan__2022.pdf (arXiv:2201.03544; ICLR 2022) |
| rockafellar2000optimization | 02_theory, CH2 | CORPUS-VERIFIED · ALIAS-CANDIDATE | RockafellarUryasev-CVaR__2000.pdf (alias of existing rockafellar2000cvar) |
| romera2024funsearch | CH1, CH2 | CORPUS-VERIFIED | FunSearch-RomeraParedes__2024.pdf (Nature 625, 18 Jan 2024, p.468) |
| skalse2022defining | CH1 | CORPUS-VERIFIED · ALIAS-CANDIDATE | RewardHacking-Skalse__2022.pdf (alias of existing skalse2022reward) |
| snoek2012practical | CH4 | CORPUS-VERIFIED | BayesOpt-Snoek__2012.pdf (NeurIPS 25; pages not on p.1 → % VERIFY) |
| sood2023deep | CH1, CH4 | CORPUS-VERIFIED | Sood-DiffSharpe__2023.pdf (AAAI 2023 copyright; exact proceedings not on p.1) |
| white2000reality | CH2 | CORPUS-VERIFIED | White-RealityCheck__2000.pdf (Econometrica 68(5):1097-1126 on p.1) |

## CLASSIC-%VERIFY (entry in refs_staging.bib; canonical coords, confirm at ref round)

| key | chapter(s) | status | note |
|---|---|---|---|
| fisslerziegelgneiting2015 | CH4 | CLASSIC-%VERIFY | Short Risk note (arXiv:1507.00244, Risk Jan 2016) — DISTINCT from the on-disk Annals Higher-Order paper |
| harvey2015backtesting | CH2 | CLASSIC-%VERIFY | Harvey & Liu "Backtesting", JPM 42(1) 2015. On-disk Harvey file is the *different* 2014 "Evaluating Trading Strategies" |
| skalse2023invariance | 02_theory | CLASSIC-%VERIFY | Skalse et al. 2023 partial-identifiability paper (arXiv:2203.07475) — NOT the 2022 reward-hacking PDF on disk |
| ziegel2016coherence | 02_theory, CH2 | CLASSIC-%VERIFY | Ziegel 2016 "Coherence and Elicitability", Math. Finance 26(4). On-disk Ziegel files are Fissler-Ziegel/Nolde-Ziegel (different) |
| pickands1975statistical | CH4 | CLASSIC-%VERIFY | Ann. Statist. 3(1):119-131 |
| balkema1974residual | CH4 | CLASSIC-%VERIFY | Balkema & de Haan, Ann. Probab. 2(5) |
| mcneil2000estimation | CH4 | CLASSIC-%VERIFY | McNeil & Frey, J. Empir. Finance 7 |
| bellemare2017distributional | CH2 | CLASSIC-%VERIFY | C51, ICML 2017 |
| dabney2018qrdqn | CH2 | CLASSIC-%VERIFY | QR-DQN, AAAI 2018 |
| vanhasselt2016popart | CH4, CH5 | CLASSIC-%VERIFY | PopArt, NeurIPS 2016 |
| raffin2021sb3 | CH4 | CLASSIC-%VERIFY | Stable-Baselines3, JMLR 22(268) |
| gebru2021datasheets | CH4 | CLASSIC-%VERIFY | Datasheets for Datasets, CACM 64(12) |
| mitchell2019modelcards | CH4 | CLASSIC-%VERIFY | Model Cards, FAccT 2019 |
| newey1987simple | CH4 | CLASSIC-%VERIFY | Newey-West, Econometrica 55(3) |
| harvey1997testing | CH4 | CLASSIC-%VERIFY (UNCERTAIN) | Referent unclear; flagged in staging note — confirm exact paper before use |
| kothari1995another | CH4 | CLASSIC-%VERIFY | Kothari-Shanken-Sloan, J. Finance 50(1) |
| moody1998performance | CH1 | CLASSIC-%VERIFY | Moody et al., J. Forecasting 17 |
| haarnoja2019applications | CH4 | CLASSIC-%VERIFY | SAC Algorithms & Applications, arXiv:1812.05905 |
| krakovna2020specification | CH1 | CLASSIC-%VERIFY | DeepMind blog, specification gaming |
| shumway1997delisting | CH4 | CLASSIC-%VERIFY | Shumway, J. Finance 52(1) |
| shumway1999delisting | CH4, CH7 | CLASSIC-%VERIFY | Shumway & Warther, J. Finance 54(6) |
| iyengar2005robust | 02_theory | CLASSIC-%VERIFY | Robust DP, Math. OR 30(2) |
| nilim2005robust | 02_theory | CLASSIC-%VERIFY | Nilim & El Ghaoui, Oper. Res. 53(5) |
| frazzini2014bab | CH4 | CLASSIC-%VERIFY | Betting against Beta, JFE 111(1) |
| asness2019qmj | CH4 | CLASSIC-%VERIFY | Quality Minus Junk, Rev. Account. Stud. 24(1) |
| lakens2017equivalence | CH4, CH7 | CLASSIC-%VERIFY | TOST primer, SPPS 8(4) |
| shadish2002experimental | CH4, CH7 | CLASSIC-%VERIFY | Shadish-Cook-Campbell, Houghton Mifflin |
| kerr1998harking | CH1 | CLASSIC-%VERIFY | HARKing, PSPR 2(3) |
| gleave2021epic | 02_theory, CH5 | CLASSIC-%VERIFY | EPIC distance, ICLR 2021 (arXiv:2006.13900) |
| blackwell1951comparison | 02_theory | CLASSIC-%VERIFY | Comparison of Experiments, Berkeley Symp. 1951 |
| blackwell1953equivalent | 02_theory | CLASSIC-%VERIFY | Equivalent Comparisons, Ann. Math. Statist. 24(2) |
| lecam1964sufficiency | 02_theory | CLASSIC-%VERIFY | Le Cam, Ann. Math. Statist. 35(4) |
| lecam1986asymptotic | 02_theory | CLASSIC-%VERIFY | Le Cam, Springer 1986 |
| sherman1951theorem | 02_theory | CLASSIC-%VERIFY | Sherman, PNAS 37(12) |
| torgersen1991comparison | 02_theory | CLASSIC-%VERIFY | Torgersen, CUP 1991 |
| bellini2015elicitable | 02_theory | CLASSIC-%VERIFY | Bellini & Bignozzi, Quant. Finance 15(5) |
| bental2013robust | 02_theory | CLASSIC-%VERIFY | Ben-Tal et al., Manag. Sci. 59(2) |
| cont2010robustness | CH4, CH7 | CLASSIC-%VERIFY | Cont-Deguest-Scandolo, Quant. Finance 10(6) |
| kuznetsov2020tqc | CH4 | CLASSIC-%VERIFY | TQC, ICML 2020 (arXiv:2005.04269) |
| yang2021wcsac | CH4 | CLASSIC-%VERIFY | WCSAC, AAAI 2021 |
| theate2023risksensitive | CH2 | CLASSIC-%VERIFY | Théate & Ernst (arXiv:2212.14743) |
| jiang2017deeprl | CH4 | CLASSIC-%VERIFY | Jiang-Xu-Liang, arXiv:1706.10059 |
| lopezdeprado2018advances | CH4 | CLASSIC-%VERIFY · ALIAS-CANDIDATE | AFML (Wiley); alias of existing lopezdeprado2018afml |
| witzany2021bayesian | CH4, CH7 | CLASSIC-%VERIFY (UNCERTAIN) | Bayesian backtest-overfitting; confirm title/venue |
| kapoor2023leakage | CH4 | CLASSIC-%VERIFY | Kapoor & Narayanan, Patterns 4(9) |
| liu2022finrlmeta | CH2 | CLASSIC-%VERIFY | FinRL-Meta, NeurIPS 2022 (arXiv:2211.03107) |

## NEEDS-WEB-VERIFY (no entry written; verify on web before citing)

These are plausibly real but NOT confirmable from the corpus. Several are 2024+ (outside the
"famous pre-2023 classic" allowance); a few pre-2024 ones I could not confidently attribute
without guessing coordinates.

| key | chapter(s) | status | best-guess referent / note |
|---|---|---|---|
| li2024automc | CH2 | NEEDS-WEB-VERIFY | LLM "trajectory-analysing critic" for reward/auto-MC design (heuristic FALSE-matched ELfolio & Lopez-Lira PDFs — neither is it) |
| ma2020dsac | CH2 | NEEDS-WEB-VERIFY | "Distributional Soft Actor-Critic" (Ma et al. 2020). Heuristic MISLABEL-matched AIFeynman-Udrescu (a different paper) |
| cao2024survey | CH2 | NEEDS-WEB-VERIFY | Survey of LLMs in RL (2024) |
| sun2024card | CH1, CH2 | NEEDS-WEB-VERIFY | LLM-reward "CARD"-style method using trajectory returns (2024) |
| nie2024directional | CH1, CH2 | NEEDS-WEB-VERIFY | "Directional" LLM-reward / decision paper (2024) |
| ren2024derandomized | CH2 | NEEDS-WEB-VERIFY | De-randomized evaluation / reward paper (2024) |
| winkel2024simplex | CH4 | NEEDS-WEB-VERIFY | Simplex / Dirichlet allocation method (2024) |
| andrews2024winners | CH2 | NEEDS-WEB-VERIFY | "Winner's curse" / multiple-testing in ML (2024) |
| andre2020dirichlet | CH4 | NEEDS-WEB-VERIFY | Dirichlet-action policy (2020); could not attribute coordinates safely |
| colas2018seeds | CH2 | NEEDS-WEB-VERIFY | Colas et al. "How many random seeds?" (2018); confirm coords |
| dacrema2019progress | CH1 | NEEDS-WEB-VERIFY | Dacrema et al. "Are We Really Making Much Progress?" RecSys 2019; confirm coords |
| lucic2018gans | CH1 | NEEDS-WEB-VERIFY | Lucic et al. "Are GANs Created Equal?" NeurIPS 2018; confirm coords |
| bertinetto2021preregml | CH2 | NEEDS-WEB-VERIFY | Pre-registration in ML (NeurIPS pre-registration workshop, ~2021); confirm |
| rubin2017forking | CH2 | NEEDS-WEB-VERIFY | Forking-paths / researcher-DoF (Rubin or Gelman line); confirm exact ref |
| olken2015promises | CH2 | NEEDS-WEB-VERIFY | Olken "Promises and Perils of Pre-Analysis Plans", JEP 2015; confirm |
| du2017backtesting | CH4, CH7 | NEEDS-WEB-VERIFY | Du & Escanciano backtesting ES (~2017); confirm coords |
| giles2016biascorrected | CH7 | NEEDS-WEB-VERIFY | Bias-corrected estimator (Giles, ~2016); confirm exact ref |
| smith1985maximum | CH4 | NEEDS-WEB-VERIFY | R.L. Smith "Maximum likelihood estimation in a class of nonregular cases" Biometrika 1985; confirm |
| smith1987estimating | CH4 | NEEDS-WEB-VERIFY | R.L. Smith "Estimating tails of probability distributions" Ann. Statist. 1987; confirm |
| liese2006divergences | 02_theory | NEEDS-WEB-VERIFY | Liese & Vajda "On divergences and informations in statistics" IEEE-IT 2006; confirm |
| raginsky2011shannon | 02_theory | NEEDS-WEB-VERIFY | Raginsky "Shannon meets Blackwell and Le Cam" (ISIT 2011); confirm |
| frongillokash2021complexity | 02_theory | NEEDS-WEB-VERIFY | Frongillo & Kash on elicitation complexity; confirm coords |
| polyanskiiwu2024it | 02_theory | NEEDS-WEB-VERIFY | Polyanskiy & Wu "Information Theory" textbook (CUP 2024/25), cited by Thm number; confirm |
| shapiro2013kusuoka | 02_theory | NEEDS-WEB-VERIFY | Shapiro on Kusuoka representation (~2013); confirm exact ref |
| fisslerziegel2021correction | 02_theory | NEEDS-WEB-VERIFY | Fissler-Ziegel correction/correigendum (~2019-2021); confirm |
| distributionalrewardshaping2022 | CH2 | NEEDS-WEB-VERIFY (already % VERIFY in chapter) | Distributional reward shaping (2022); non-standard key, confirm |
| skalse2024starc | 02_theory, CH5 | NEEDS-WEB-VERIFY | Skalse et al. "STARC" reward-distance metric (2023/2024); confirm |
| belzile2020improved | CH4, CH7 | NEEDS-WEB-VERIFY | Belzile et al. improved threshold/EVT diagnostics (~2020); confirm |
| chen2023chatgpt | CH4, CH7 | NEEDS-WEB-VERIFY | Chen et al. ChatGPT/LLM determinism or finance (2023); confirm exact ref |
| zheng2025survey | CH1, CH2 | NEEDS-WEB-VERIFY | LLM survey (2025) — see SUSPICIOUS note below; prompt flags as probably-real-but-unverifiable |
| gaopavel2017softmax | CH4, CH7 | NEEDS-WEB-VERIFY | Softmax/Gumbel allocation (key may be malformed; "gaopavel"); confirm authors |
| wang2022ebh | CH2 | NEEDS-WEB-VERIFY | "EBH" enhanced/empirical-Bayes method (2022); confirm |

## SUSPICIOUS (>=2025/2026; possible hallucination — no entry written)

| key | chapter(s) | status | note |
|---|---|---|---|
| kvasiuk2026madevolve | CH2 | **SUSPICIOUS-POSSIBLE-HALLUCINATION** | 2026-dated "MADevolve"; not on disk. Highest hallucination risk (future-dated, obscure). Verify existence before any use. |
| song2025reward | CH2 | SUSPICIOUS (LIKELY-REAL) | 2025 reward-design/LLM paper; verify on web |
| yuan2025nondeterminism | CH4, CH7 | SUSPICIOUS (LIKELY-REAL) | 2025 LLM non-determinism paper; verify on web |
| choudhary2025risk | CH1 | SUSPICIOUS (LIKELY-REAL) | 2025 risk/portfolio-RL paper; verify on web |
| fissler2025tail | 02_theory | SUSPICIOUS (LIKELY-REAL; already % VERIFY in chapter) | 2025 Fissler tail-risk elicitability paper; verify on web |
| hazra2025revolve | CH2 | SUSPICIOUS (LIKELY-REAL) | 2025 "REvolve" LLM-reward-evolution paper; verify on web |
| yamada2025aiscientist | CH2 | NEEDS-WEB-VERIFY (prompt: probably real) | AI Scientist v2 (Sakana, 2025); verify on web |
| deepmind2025alphaevolve | CH1, CH2 | NEEDS-WEB-VERIFY (prompt: probably real) | DeepMind AlphaEvolve (2025); verify on web |
| lu2024aiscientist | CH1, CH2 | NEEDS-WEB-VERIFY | Lu et al. "The AI Scientist" (Sakana, 2024); verify on web |

## MISLABELED / FALSE-MATCH (do NOT cite from the matched on-disk file)

| key | bad match on disk | what the file actually is | correct status |
|---|---|---|---|
| ma2020dsac | AIFeynman-Udrescu__2020.pdf | "AI Feynman: A Physics-Inspired Method for Symbolic Regression" (Udrescu & Tegmark, Sci. Adv. 2020) — a completely different paper | real referent (Distributional SAC, Ma et al. 2020) is NOT in corpus → NEEDS-WEB-VERIFY |
| li2024automc | ELfolio__2025.pdf; LopezLira-ChatGPT__2023.pdf | ELfolio (Zeng et al. 2025) and "Can ChatGPT Forecast Stock Price Movements?" (Lopez-Lira & Tang) — neither is a "Li 2024" paper | real referent NOT in corpus → NEEDS-WEB-VERIFY |

Note: the surname+year matcher also produced benign near-misses already handled correctly above
(e.g. chow2015risk → the 2015 robust-CVaR file not the 2014 MDP file; harvey2015backtesting →
NOT the on-disk 2014 "Evaluating Trading Strategies"; the three Fissler/Ziegel keys → the right
distinct papers). Those are resolved in the table rows, not mislabels.

---

### Counts by status (each of the 104 keys counted once)

- CORPUS-VERIFIED: **17** (entries written)
- CLASSIC-%VERIFY: **46** (entries written: 4 disambiguated + 42 famous classics)
- NEEDS-WEB-VERIFY: **32** (no entry) — INCLUDES the 2 MISLABELED keys below
- SUSPICIOUS (>=2025/2026): **9** (no entry)

Total: 17 + 46 + 32 + 9 = **104**. `refs_staging.bib` holds **63** proposed entries (= 17 + 46).

**MISLABELED / FALSE-MATCH (2):** `ma2020dsac`, `li2024automc` — the on-disk PDF the heuristic
matched is a different paper; both reclassified into NEEDS-WEB-VERIFY (listed in both tables, but
counted once, within NEEDS-WEB-VERIFY).

The 9 SUSPICIOUS keys are the full >=2025/2026 set: kvasiuk2026madevolve, song2025reward,
yuan2025nondeterminism, choudhary2025risk, fissler2025tail, hazra2025revolve,
yamada2025aiscientist, deepmind2025alphaevolve, lu2024aiscientist (the last is 2024 but lives in
the same AI-Scientist/AlphaEvolve family — verify-before-use; the prompt deems the last three
"probably real but unverifiable from disk").
