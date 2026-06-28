# LIT_gap — Risk-sensitive / distributional / portfolio RL: positioning, theory-soundness audit, gaps, framing

**Scope.** Deep literature-gap + **theory-grounding** analysis for the headline contribution — *distributional /
tail-statistics feedback to an LLM reward-DESIGNER, for a FIXED SB3-SAC long-only risk-sensitive portfolio agent,
with CVaR/EVT tail measurement under a coherent-risk framing*. This is the companion to `docs/DEEP_H2.md` (which
audits H2's **statistical inference and construct validity**) and `docs/LIT_gap_llm_reward_optimizer.md` (the
LLM-as-optimizer lineage). **This document is the per-AREA positioning and the theory-soundness audit** — the part
the supervisor (Dr Ramin Okhrati: stochastic control / risk measures / RL) will scrutinise hardest. No code was
modified. Citations are precise; every load-bearing theorem was re-verified first-hand (PyMuPDF extracts of the
source PDFs in `D:\tmp\littxt\`) or by adversarial web research this session; verification status is flagged
throughout. Read-only on code.

**Verdict in one line.** The theory backbone is genuinely strong and unusually rigorous for an MSc — the
Blackwell-sufficiency / Kusuoka-spanning / Rowland-off-critic spine is the right argument and is correctly
cited at the level of *substance*. The exposure is **not** in the claims but in the **precision of phrasing**:
five specific over-statements (catalogued in §3) would each be probed by a risk-measures examiner, and one
genuine theoretical attack (the **finite-moment / moment-problem** rebuttal to "the tail is off-critic", §3.4)
must be pre-empted in the exact wording given. Plus there is **one cross-area gap the literature now fills**
(2025–26 Eureka successors confirm the novelty cell is still empty — §1.A) and **two strongest-framing moves**
(§5) that turn the theory from "cited" into "load-bearing and defended".

---

## 0. The cross-area map (which cell is empty, and why each neighbour is not it)

The contribution sits at the intersection of **three mature literatures**, in a cell none of them occupies. The
"empty-cell" logic is `(who designs the objective) × (what signal feeds the design) × (domain)`:

| Area | What it does | What feeds the design | Why it is NOT this contribution |
|---|---|---|---|
| **(I) LLM reward design** (Eureka lineage) | LLM writes reward CODE, evolutionary reflection | **scalar** fitness / per-component reward stats / trajectory preferences | robotics/control; **no return distribution** ever fed back; no finance |
| **(II) Risk-sensitive / distributional RL** (CVaR-RL, distributional critics, coherent-risk RL) | optimise a risk functional of return | **the human fixes** the distortion/risk objective a priori | the *researcher* specifies the objective; **no LLM designs the reward** |
| **(III) DRL for portfolio** (FinRL, EIIE, alpha/strategy evolution) | learn an allocation policy | human-written reward; or LLM evolves *strategy*, not reward | the reward stays human-authored, or the LLM evolves *what to trade*, not the objective |

The unoccupied cell — **LLM-as-reward-CODE-designer × realized-return-distribution feedback × deep-RL portfolio
allocation** — is the contribution (N1). The remainder of this document positions against each area, audits the
theory that links them, and lists the implementable improvements.

---

# PART A — PER-AREA POSITIONING (SOTA, contribution, novelty, gaps)

## 1.A — Risk-sensitive / safe / CVaR RL and distributional RL

### SOTA (verified)
- **CVaR-RL algorithmic lineage** (all `[KNOWN]`, citation-verified): Chow–Ghavamzadeh 2014 (mean-CVaR PG +
  actor-critic, arXiv:1406.3339); Tamar–Glassner–Mannor 2015 (CVaR via sampling, arXiv:1404.3862);
  Tamar–Chow–Ghavamzadeh–Mannor 2015 (PG for the **whole coherent-risk class** via the risk-envelope dual,
  arXiv:1502.03919); Chow–Tamar–Mannor–Pavone 2015 (CVaR value-iteration + the **robustness dual** "CVaR =
  worst-case expected cost over a `1/α`-bounded density-ratio ambiguity set", arXiv:1506.02188); Prashanth–Fu 2022
  monograph (the one-stop survey, arXiv:1810.09126).
- **Distortion/spectral deep-RL, modern**: the **Coache–Jaimungal** trilogy — dynamic convex risk (arXiv:2112.13414,
  in corpus, read first-hand), conditionally-elicitable spectral (arXiv:2206.14666), **robust distortion-risk RL**
  (arXiv:2409.10096, SIAM JMDS, **demonstrated on portfolio allocation** — the single closest non-LLM neighbour);
  DSAC (Ma et al., JAIR 83 2025); SRCPO (Kim et al., NeurIPS 2024, spectral-risk-constrained, arXiv:2405.18698
  `% VERIFY`); O-RAAC (risk-averse offline, arXiv:2102.05371).
- **Distributional-RL theory canon** (all citation-verified first-hand or by agent): C51 (Bellemare–Dabney–Munos
  2017, arXiv:1707.06887); QR-DQN (Dabney et al. 2018, arXiv:1710.10044); IQN (Dabney–Ostrovski–Silver–Munos 2018,
  arXiv:1806.06923, in corpus); the **Bellemare–Dabney–Rowland 2023 textbook** (MIT Press, ISBN 9780262048019, free
  at distributional-rl.org — **cite the BOOK**, Ch. 4 metrics/contraction, Ch. 7 §7.6–7.8 risk, Ch. 8
  functionals/closedness).
- **Distributional RL in finance** (corpus family E): RAMAC (arXiv:2510.02695, generative actor + IQN critic
  optimising CVaR); EX-DRL (arXiv:2408.12446, ICAIF 2025, **GPD tail modelling for extreme-quantile hedging** — the
  off-critic-EVT-tail analogue and the strongest precedent for "estimate the deep tail with a GPD, not a neural
  count"); Tail-Safe (arXiv:2510.04555, RL CBF–QP hedger with CVaR as a QP constraint).

### Contribution + novelty (N1)
The **off-critic distributional FEEDBACK** to a reward *designer* is categorically different from a distributional
**CRITIC** inside the agent. This is **audit A-1** and the single most important distinction in the whole project:
- A distributional critic (C51/IQN/QR-DQN/TQC/DSAC) learns the return *distribution* to compute a risk-sensitive
  *value*, then acts greedily/softly w.r.t. it. The risk attitude is **baked into the agent's value recursion**.
- This contribution measures the realized-return distribution **off-critic** (a separate estimator,
  `src/feedback/measurement.py`) and feeds it as **text** to an LLM that **writes the per-step reward code**. The
  agent (SB3-SAC) is a **plain mean-critic** and is **held fixed across all arms**. The risk attitude is
  discovered by the *reward designer*, not embedded in the critic.

**Why this matters for grading.** It lets the contribution stand on a vanilla, well-understood agent (clean
internal validity), and it makes the distributional content **provably extra information the critic cannot carry**
(§2.4, Rowland). The secondary SAC-vs-TQC critic experiment is the *known* question (DSAC, Tail-Safe); it is
explicitly **not** the novelty.

### Gaps the examiner will probe (this area)
1. **Differentiation from Coache–Jaimungal (2409.10096).** It already does CVaR/distortion-risk RL on portfolios.
   The delta is N1 (LLM designs the reward; they fix it a priori). **An architectural delta alone is thin** — the
   `SOTA_AND_NOVELTY_VERIFICATION` open-question #3 flags that the dissertation likely needs an *empirical* edge (or
   honest null) of the LLM-designed reward over a strong fixed risk objective in their spirit. **Framing fix in §5.**
2. **"Why not a distributional critic instead?"** Answer is on record (A-1): the contribution is the *feedback
   channel*, measured off-critic so it is **critic-agnostic** (NOT agent-independent — the fed tail is endogenous to the policy it steers); the critic is a separate, known experiment. State it once,
   crisply, near the architecture diagram.
3. **Static-CVaR time-inconsistency.** The classic attack (Boda–Filar 2006; Shapiro 2009/2012; Cheridito–Stadje
   2009). **Already fully defended** in `H2_THEORY_FOUNDATIONS` §"time-consistency": the optimised object is a
   **per-step additive (Markov/recursive) reward** written by the LLM — *not* a static terminal-CVaR — so the
   Ruszczyński-nested time-consistency is satisfied by construction; CVaR appears only in (a) the feedback channel
   (a diagnostic) and (b) the held-out evaluation (a one-shot descriptive measure of a fixed series, the correct use
   of static CVaR). This converts the attack into a design strength. **Keep this paragraph verbatim in the
   Methodology; it is one of the strongest defensive moves in the project.**

### NOVELTY RE-CHECK (2025–26 sweep, this session) — claim SURVIVES
A fresh fan-out (≈50 web searches + ≈25 primary fetches) found **no** work feeding a return distribution / CVaR /
quantile / tail signal **back** to an LLM designing a reward. New near-misses to **cite to pre-empt reviewers**
(all confirmed first-hand, none breaks N1):
- **LaRes** (NeurIPS 2025, OpenReview `jRjvcqtdtA`): EA+RL with LLM reward search; feedback = **scalar policy
  performance**. The most structurally similar paper to this one — and it stops at scalar fitness.
- **CARD** (arXiv:2410.14660, *Knowledge-Based Systems* 2025): LLM reward design with **trajectory-preference**
  feedback — preferences, not a distribution; robotics.
- **RF-Agent** (arXiv:2602.23876, Mar 2026): Eureka-style **scalar** training results via MCTS.
- **Gran Turismo automated reward** (arXiv:2511.02094, Sony AI): VLM/human preference + reward-value-over-training;
  a "distribution of racing metrics" appears only in the *evaluation figure*, **not** fed to the LLM.
- **READY** (arXiv:2601.21847, Jan 2026): LLM discovers reward code for black-box optimisers; **scalar** feedback.

> **Read-flag for the write-up:** the word "distribution" recurs in URDP (`2507.02256`), DrEureka, RF-Agent meaning
> *weight priors / parent-selection / domain-randomisation / MDP-initial-state* distributions — **never a return
> distribution fed to the LLM**. Pre-empt this explicitly so a reviewer skimming a title does not assume overlap.
> **FORGE** (ICLR 2026 submission, OpenReview `Z6GStCfccl`) was **WITHDRAWN 30 Nov 2025** — do not cite as prior art.

---

## 2.A — LLM reward design (Eureka lineage) — the machinery this adapts

### SOTA + what this adapts
**Eureka** (Ma et al., ICLR 2024, arXiv:2310.12931, read first-hand): LLM writes reward code → trains RL → serialises
training stats back as text ("reward reflection") → revises; evolutionary selection on a scalar fitness. The
**reward-reflection ablation is the headline empirical analogue**: removing reflection drops the average
human-normalised score by **−28.6%** (verbatim, confirmed: *"Averaged over all Isaac tasks, Eureka without reward
reflection reduces the average normalized score by 28.6%"*; degradation larger on higher-dimensional tasks).

**The three finance-forced changes** (this is the contribution's deviation from Eureka): (1) Eureka's fitness is a
ground-truth simulator score; finance has none, so fitness = **held-out validation Deflated Sharpe**, decoupled from
the candidate reward; (2) Eureka's reflection is performance numbers; this one **carries the realized-return
distribution** (the contribution); (3) Eureka's environment is a simulator; this one is a **PIT market**, forcing a
contamination defence Eureka never needed.

### The "richer reflection accelerates search" claim (Part b of the theory)
- **GEPA** (Agrawal et al., **ICLR 2026 Oral**, arXiv:2507.19457, *"Reflective Prompt Evolution Can Outperform
  Reinforcement Learning"*): a genetic-Pareto reflective *prompt* optimiser. Verbatim: *"GEPA outperforms GRPO by 6%
  on average and by up to 20%, while using up to 35× fewer rollouts."* **Citation upgrade:** it is **ICLR 2026
  (Oral)**, not a bare preprint, and the precise phrasing is "outperforms the RL method GRPO (by up to 20%) while
  using up to 35× fewer rollouts" — the 35× attaches to rollout efficiency, the 6–20% to the quality margin; do not
  compress to "beats RL at 35× fewer rollouts".
- **Status discipline (critical for Okhrati on the theory).** The dissertation's `H2_THEORY_SPINE` §1(b) already
  **correctly demarcates** this: (b.i) the data-processing inequality giving "distributional feedback carries weakly
  higher expected information gain per evaluation" is a **THEOREM**; (b.ii) Bernardo 1979 (EIG = expected log-score
  utility) is a **THEOREM**; but (b.iii) "higher EIG ⇒ strictly fewer expensive SAC runs in *this* non-convex
  gradient-free program search" is an **ANALOGY** (Freund 1997 is a bound in a *different* model — realizable
  hypothesis class, i.i.d. queries; Wu et al. 2017 is a structural twin in a different method class; Eureka/GEPA are
  empirical precedents). **Keep this demarcation exactly.** The single most common way these projects lose theory
  marks is asserting (b.iii) as a theorem; the spine does not, which is a genuine strength.

### Gap (this area)
**The acceleration claim is the one the matched-compute design puts at risk** (null condition §5.5 of the spine):
if acceleration is the *only* mechanism and compute is matched past the point where it binds, the arms can tie on
final OOS while the distributional arm reached its winner in fewer generations. **Implementable improvement:**
report **generations-to-winner** alongside final OOS (the spine names this; confirm it is logged). A null on final
OOS *with* a visible generation-count gap is itself the publishable "acceleration-but-not-ceiling" finding.

---

## 3.A — DRL for portfolio + the backtest-integrity critique

### SOTA + failure modes (verified, with corrections)
- **The canon:** Jiang–Xu–Liang 2017 EIIE/PVM (arXiv:1706.10059 — **a non-refereed preprint; cite as such**); FinRL
  (Liu et al. 2020 workshop / 2021 ICAIF / 2022 FinRL-Meta NeurIPS D&B); Hambly–Xu–Yang 2023 (Math. Finance
  33(3):437–503 — the **peer-reviewed** survey to situate DRL-in-finance).
- **The critique literature (the dissertation's honesty backbone):**
  - **Sun–Wang–An 2023** (ACM TIST 14(3) Art. 44, DOI 10.1145/3582560): verbatim — *"due to the low signal-to-noise
    nature of financial markets, FinRL methods with only high profit on backtesting are likely to overfit on
    historical data and fail in real-world deployment."* The single best "the field is fragile" cite.
  - **Gort et al. 2022** (arXiv:2209.05559): operationalises **PBO as a hypothesis test on DRL agents**.
    **Correction:** 5th author is **Shuaiyu Chen**, not "Yang".
  - **Off-policy SAC struggles on noisy financial rewards** (arXiv:2307.07694, **single author Lu Chung I**):
    verbatim — *"the off-policy algorithms DDPG, TD3 and SAC are unable to learn the right Q-function due to the noisy
    rewards and therefore perform poorly. The on-policy algorithms PPO and A2C … are able to deal with the noise."*
    **Caveat: this is on SIMULATED GBM data, not live markets** — cite as a controlled-simulation result. This is
    **L19** in the limitations register (the prototype's critic divergences — 6 diverged runs, ~2.5%; "64" was an
    `anomalies.jsonl` line-count, not a run-count — are the same failure mode); the defence
    is that SAC is **fixed across arms**, so the instability is differenced out of the comparative H2 and the campaign
    runs a hardened critic (PopArt + LayerNorm).
- **The weak-baseline / reproducibility critique** (relevance is **by analogy** — none are finance papers):
  Ferrari Dacrema et al. 2019 (RecSys Best **Long** Paper, arXiv:1907.06902 — **18 neural methods analysed → 7
  reproducible → 6 beaten** by tuned heuristics; state all three numbers); **Henderson et al. 2018** *Deep RL that
  Matters* (the one to lean on hardest — it is RL: seeds/hyperparameters/reward-scaling make apparent gains variance
  artefacts; directly backs the per-seed rliable + matched-budget design); Melis et al. 2018; Lin 2018/19. This is
  **L16** (untuned hand-baselines, the H1 "you beat a strawman" exposure).
- **The benchmark canon (makes the comparison credible):** DeMiguel–Garlappi–Uppal 2009 (RFS 22(5):1915–1953 —
  across **7 datasets, none of 14** optimising models consistently beats **1/N** on Sharpe/CEQ/turnover — the
  non-negotiable floor); Ledoit–Wolf shrinkage (2003/2004); López de Prado HRP 2016.
- **Backtest inference:** Bailey–López de Prado DSR 2014 (JPM 40(5):94–107); Bailey–Borwein–López de Prado–Zhu
  PBO/CSCV (J. Comp. Finance 20(4):39–69 — **cite "online 2016 / issue 2017", not 2015**); Harvey–Liu–Zhu 2016 (RFS
  29(1):5–68, t>3 — **third author Heqing Zhu**, not "Caroline Zhu").

### Gap (this area) — the BAB / low-volatility attribution risk (L15, the red-team's CRITICAL gap)
A long-only agent that lowers volatility to improve the tail **structurally loads on Betting-Against-Beta**
(Frazzini–Pedersen 2014, JFE 111(1):1–25 — US BAB Sharpe **0.78**, 1926–Mar 2012, US equity; **distinct from the
0.81 Treasury BAB**) and the **low-volatility anomaly** (Ang et al. 2006; Baker–Bradley–Wurgler 2011). An examiner
reflexively regresses any vol-lowering equity strategy on a factor panel; if the intercept dies once BAB enters, the
headline is "a repackaged low-beta harvest", not RL skill.
- **Defence on record (correct):** the headline is **comparative** (distributional vs scalar, both long-only, both
  potentially BAB-loaded), so the factor load is **common-mode** — the object tested is the **difference-in-α**
  (distributional − scalar) after controlling for FF5 + momentum + BAB (`campaign_attribution`).
- **Implementable improvement:** **pre-register the factor-attribution ladder as a declared secondary family** (it
  exists in code but was NOT in `config/preregistration.yaml`). **Citation hygiene:** the **post-2018 BAB/low-vol
  decay** claim is **FOLKLORE** — no clean dated peer-reviewed source establishes it; McLean–Pontiff 2016 (general
  cross-anomaly decay, ~58% post-publication, predates 2018) and **Novy-Marx–Velikov 2022** (JFE 143(1):80–106, the
  strongest BAB *mechanism* challenge — BAB's performance comes from micro-cap equal-weighting, not the beta
  mechanism) are solid; if you assert post-2018 decay, **frame it explicitly as practitioner observation**, not
  established fact.

---

# PART B — THE THEORY-SOUNDNESS AUDIT (the part Okhrati scrutinises most)

The H2 theory spine decomposes the headline into a **two-part theorem** (true only if BOTH hold), which is the right
structure. The substance of every load-bearing claim was re-verified this session — **the claims are correct**. The
risk is entirely in **precision of phrasing**. Below: each claim, its verified status, and the *exact* over-statement
an examiner would attack, with the safe wording.

## §2.1 — Part (a.i)/(a.ii): Sharpe is a Blackwell garbling of the distribution

**Claim.** Sharpe `g(F)=√252·E_F[X]/σ_F` is a deterministic measurable functional of `F`, hence the scalar
experiment `μ_S: F↦g(F)` is a (degenerate, Dirac) garbling of the distributional experiment `μ_D`; by
Blackwell–Sherman–Stein the distributional channel **weakly dominates** the scalar for the reward-design decision
**under every objective**.

**Status: RIGOROUS in substance.** Blackwell 1953 (Ann. Math. Statist. 24(2):265–272) verified first-hand by agent.

**THREE precision traps an examiner will spring** (all verified against primary sources):

1. **Demote "Blackwell-dominates" to the DATA-PROCESSING direction.** You only use, and only need, the **easy
   half** — sufficiency/garbling ⇒ domination, which is the data-processing inequality and needs **no finiteness /
   no regularity at all**. The full BSS *equivalence* (the hard direction, "more-informative ⇒ garbling") requires a
   **finite parameter space** (Torgersen 1970; the infinite case is Le Cam 1964, not BSS) and **dominated experiments
   on standard Borel spaces**. Invoking the full equivalence imports caveats you do not need and is exactly the kind
   of over-claim a measure-theoretic examiner flags. **Fix:** *"Because Sharpe is a deterministic statistic of the
   same sample whose empirical law is the richer signal, the distributional channel weakly dominates the scalar by
   the post-processing (data-processing) direction of Blackwell's comparison — the converse (hard) direction, and
   hence the full Blackwell–Sherman–Stein equivalence, is not invoked."*
   - *Subtlety to also note:* BSS finiteness that Blackwell 1953 **removes** is on the **outcome/signal** space; the
     finiteness that **remains** (for the exact garbling-kernel form) is on the **parameter** space. These two axes
     are routinely conflated. Since you use only the easy direction, neither bites — but say so.

2. **Fix the parameter as `θ = Z` (latent quality), NOT `θ = F`.** Blackwell experiments share **one** parameter
   space. Use the genuine Markov chain `Z → F_Z → g(F_Z)` (latent reward quality → induced return law → Sharpe);
   Sharpe factors through `F`, which makes the garbling kernel **state-independent** (the load-bearing hypothesis).
   If you instead set `θ = F`, then `μ_D` is a zero-noise identity channel and "identity dominates a function of
   identity" is true but **borderline vacuous** (and the mutual information `I(F; g(F))` is degenerate/infinite for
   continuous `F`). **Fix:** state `θ = Z` explicitly.

3. **Keep it WEAK (≥); argue strictness SEPARATELY; flag Sharpe's domain.** The garbling argument gives **weak**
   domination only. Strictness — that Sharpe is genuinely *tail-blind* — is a **separate** argument (the toy proof
   §2.3 / Kusuoka §2.2), not a corollary of Blackwell. Also: `g(F)` is Borel-measurable **only on its domain**
   (finite second moment, **strictly positive variance**); at `σ_F=0` (an all-cash policy) Sharpe is `0/0`/`±∞` —
   exclude `σ_F=0` from the parameter space or note it has probability zero under any non-degenerate prior. An
   examiner will look for exactly this.

## §2.2 — Part (a.iii): Kusuoka/Acerbi — the CVaR profile is sufficient for coherent risk; Sharpe is a lossy, non-coherent projection

**Claim.** By Kusuoka 2001, every law-invariant coherent risk measure is a sup over mixtures of CVaR; the CVaR
profile `α ↦ CVaR_α(F)` is a **sufficient coordinate basis for the whole law-invariant coherent-risk class**, while
Sharpe (built on `σ`, not monotone, hence not coherent — Artzner 1999) is a strictly lossy projection.

**Status: RIGOROUS — verified FIRST-HAND from the Kusuoka 2001 primary source** (`D:\tmp\littxt\…Kusuoka…`). The
extract confirms the theorem **exactly**, and the precise conditions matter:
- **Theorem 4 (general case):** `ρ(X) = sup{ ∫₀¹ ρ_α(X) m(dα) : m ∈ M₀ }` over a **compact convex set `M₀`** of
  probability measures on [0,1], **iff** `ρ` is a **law-invariant coherent risk measure with the Fatou property**.
  Here `ρ_α` is exactly CVaR/AVaR at level α (the paper's `ρ_α(X)=α⁻¹∫_{1-α}^1 Z(x,F_{-X})dx`). ✅ This is the
  "**sup over CVaR-mixtures**" statement, verbatim.
- **Theorem 7 (comonotone case):** if **additionally comonotone-additive**, it is a **single** mixture
  `ρ(X)=∫₀¹ ρ_α(X) m(dα)` (no sup) — the spectral measures. ✅
- **Theorem 5 (uniqueness):** the mixing measure `m` is **unique**. ✅

**TWO conditions to state in-text (Okhrati WILL check these):**
1. **The atomless / standard-probability-space assumption is load-bearing.** Kusuoka's theorem is proved on a
   **non-atomic standard probability space** (the paper reduces to Lebesgue space `[0,1)` explicitly). State it. (The
   empirical return panel is finite-sample, so the representation is the *population* statement that justifies the
   *choice* of coordinates; the finite CVaR grid is a near-sufficient discretisation — §2.6.)
2. **The Fatou property** (lower semicontinuity) is required in Theorems 4/7. It holds for CVaR and is standard, but
   it is a hypothesis, not free.

**Citation-integrity flag (the corpus PDF is mis-named).** The **spectral-measures** citation is **Acerbi 2002,
*Spectral measures of risk*, J. Banking & Finance 26(7):1505–1518, DOI 10.1016/S0378-4266(02)00257-X** — a
**different** paper from the PDF stored in the corpus as `AcerbiTasche-ES__2002.txt`, which is **Acerbi–Tasche,
*On the coherence of Expected Shortfall*** (also 2002, also JBF, but a distinct paper). **Cite the correct Acerbi
2002 spectral paper for the spectral form, and Acerbi–Tasche 2002 for the ES-coherence point — do not conflate the
two.** (Logged in `project-citation-integrity-flags`; surface here because the spectral form is a load-bearing
citation.) The spectral form itself — `M_φ(X)=−∫₀¹ φ(p)F_X^{-1}(p)dp`, coherent iff `φ≥0` non-increasing,
`∫φ=1`; CVaR = `φ` uniform on `[0,α]`; **mean = the degenerate flat spectrum `φ≡1`** — is correctly stated in the
spine and confirmed by agent.

**Artzner 1999 (coherence axioms) — verified first-hand.** The four axioms (monotonicity, translation invariance,
positive homogeneity, subadditivity) and the VaR-subadditivity-failure repair are confirmed. **One scope note:**
Artzner's original setting is a **finite state space Ω** (the paper says so explicitly); the extension to general
`L^∞` with law-invariance is standard (Delbaen) but is the version Kusuoka uses — cite Artzner for the axioms and
note the general-space coherence is via Delbaen / Föllmer–Schied (2002).

**This §2.2 block is the strongest single piece of the theory** and the cleanest answer to "why CVaR at multiple
levels and not an arbitrary list?": the levels span the coherent class. Lead the Methodology risk section with it.

## §2.3 — The toy proof (Sharpe-insufficient, CVaR-sufficient): the strict-dominance witness

**Status: RIGOROUS, self-contained, correct.** Two mean-0/variance-1 laws — Gaussian `F_A` vs a 2-point
variance-matched law `F_B` (`X_B=−√19≈−4.359` w.p. 0.05, `+0.229` w.p. 0.95) — have **identical Sharpe** (both 0)
but **CVaR_05(F_B)=4.359 > 2.063=CVaR_05(F_A)** (closed forms verified). This is the explicit witness that the
strict-dominance regime (§2.5) is non-empty and *financially natural* (Gaussian-vs-tail at matched mean–variance is
the textbook risk-management failure mode). **Keep it; it is exactly the kind of worked, self-contained proof an
examiner rewards.** One polish: state that the conclusion is identical for a continuous variant (variance-matched
Student-`t` / skew-`t`), so the 2-point law is a computational convenience, not a knife-edge.

## §2.4 — Part (a.iii) continued: Rowland — the tail is genuinely off-critic (Bellman-closedness). **THE key vulnerability**

**Claim.** By Rowland et al. 2019 (Thm 4.3 / Lemma 4.4), only moments are Bellman-closed among finite statistic sets;
CVaR/VaR/distortion-tail functionals are not; hence the tail content is information the SAC critic's recursion
**cannot exactly carry** — it is genuinely off-critic.

**Status: RIGOROUS in kind, but THE phrasing must be tightened, and ONE attack pre-empted.** Verified first-hand
from the PMLR PDF by agent. Corrections that **must** be applied:

1. **Keep Theorem 4.3's "expectation-form" qualifier.** The theorem's exact hypothesis is statistics *"of the form
   `s(µ)=E_{Z∼µ}[h(Z)]`"*. It says moments are the only Bellman-closed **expectation-form** sets — **not** the only
   Bellman-closed statistics of *any* form. **Any sentence that drops "expectation-form" and says "moments are the
   only Bellman-closed statistics" OVERSTATES the theorem.** Keep the qualifier.
2. **Do NOT cite Rowland for "CVaR/VaR/distortion are not Bellman-closed".** The strings "CVaR", "VaR", "distortion"
   **appear nowhere** in the paper. Lemma 4.4 covers the statistics learned by **CDRL (categorical) and QDRL
   (quantile)**, derived **as a corollary of Theorem 4.3** (the word "counterexample" is not used — soften "explicit
   counterexample"). VaR = a quantile, so its non-closedness is **your inference** extending Lemma 4.4; CVaR/distortion
   are **not expectation-form** and fall **outside Theorem 4.3's hypothesis entirely** (the theorem is *silent* on
   them). **Label these as your own extension, not Rowland's result.**
3. **Pre-empt the MOMENT-PROBLEM attack — this is the one genuine theoretical hole, with a decisive rebuttal.**
   - *The attack (steelmanned).* SAC's critic learns the mean (a moment — Bellman-closed). Portfolio returns are
     **bounded** ⇒ **compact support** ⇒ the **Hausdorff moment problem is determinate**: the *full infinite* moment
     sequence uniquely determines the distribution (Weierstrass: polynomials dense), hence determines CVaR/VaR. So
     "moments determine the tail" — making "off-critic" look like a matter of **degree** (carry enough moments), not
     **kind**.
   - *Why it FAILS against the Bellman-recursion claim (kind, not degree).* **(i)** Bellman closedness is
     intrinsically a **finite-set** property (Rowland Def 4.1: *"a **finite** set of statistical functionals"*); the
     determinacy result needs the **full INFINITE** sequence and says **nothing** about any finite truncation.
     **(ii)** Any **finite** set of moments does **not** pin down VaR/CVaR — this is a theorem-backed fact: the
     literature on *optimal VaR/CVaR bounds given moment information* exists precisely because the finite-moment
     problem is non-unique; for given first-N moments the tight CVaR is the **inf/sup over a feasible set of
     moment-consistent distributions**, a non-degenerate bracket. **(iii)** Rowland Thm 4.3 closes the loop: the only
     finite expectation-form sets that are self-consistent under the Bellman recursion are (spans of) moments, and
     CVaR/VaR lie in no finite moment span (and CVaR is not even expectation-form). So **no finite-statistic Bellman
     recursion can be closed on a tail functional** — a difference in kind.
   - *The one concession to state (degree, for the REPRESENTATION claim).* As the number of carried moments →∞, a
     compact-support distribution (hence its W₁-continuous CVaR) **is** determined in the limit, and finitely many
     moments give *converging bounds*. So if you ever phrase the benefit as *"a distributional critic can REPRESENT
     the tail and a mean-critic cannot"*, that is **degree** (QR-DQN/IQN do exactly this) — and it is not the robust
     claim.
   - **SAFE WORDING (use verbatim):** *"The tail is off-critic in the sense that **no finite-statistic Bellman
     recursion of the kind SAC's critic runs is closed on a tail functional** (Rowland et al. 2019, Thm 4.3 + Lemma
     4.4 for expectation-form / quantile statistics; the extension to CVaR/VaR is ours, since these are not
     expectation-form and lie in no finite moment span); approximating the tail instead requires explicitly
     representing many quantiles of the return distribution, which is precisely the off-critic measurement the
     project performs."* This phrasing is bulletproof; "genuinely off-critic" full-stop is defensible **only** with
     this finite-recursion gloss attached.

**Supporting distributional-RL theorems (verified, with corrections):**
- **C51 contraction (Bellemare et al. 2017) — verified first-hand from the PDF.** Policy-evaluation operator is a
  γ-contraction in the **maximal/supremal `p`-Wasserstein** metric (Lemma 3); **not** a contraction in TV/KL/Kolmogorov
  (explicit); the **control** operator is **not** a contraction in any metric (Prop 1) and need not have a fixed point
  (Prop 2); the **mean** still contracts in control (Lemma 4). Cite Prop 1 **and** Prop 2 together for the full
  negative result.
- **Lyle–Castro–Bellemare 2019 — the "mean = representational, risk = intrinsic" framing is HALF fair; FLAG the
  other half.** The paper proves the **mean-equivalence** half (tabular/linear distributional RL gives the same mean
  as expected RL; divergence needs **nonlinear** approximation — Props 2–5/8, Prop 9). The *"for risk it is
  intrinsic"* half is **NOT proved by this paper** and partly cuts against it (the paper notes the distributional
  estimator does **not** give lower-variance *value estimates*). **Do not cite Lyle 2019 for "risk is intrinsic";**
  attribute that to the risk-sensitive distributional-RL line (IQN) or present it as your own interpretation.
- **Marthe–Garivier–Vernade 2023 — the exactly-DP-optimisable class is EXPONENTIAL/ENTROPIC utilities, not the
  general Kolmogorov–Nagumo family.** Verbatim Thm 2: *"The only W₁-continuous Bellman Optimizable statistical
  functionals … are exponential utilities `(1/λ)log E[exp(λR)]`."* The phrase "generalized means / Kolmogorov–Nagumo"
  **overstates** it. **Fix:** say "exponential utilities / entropic risk measures". (Their Thm 1 gives a
  **policy-evaluation** error bound for distorted means with `L=1/α` for CVaR — a *measurement* bound, **not** a
  planning/regret bound; undiscounted finite-horizon.) This result is **strongly pro-contribution**: it shows even
  *with the full distribution* the tail (CVaR) is not exactly DP-optimisable, only approximable — reinforcing that
  the tail objective is better discovered by a **reward designer** than baked into the agent's DP.

## §2.5 — The strict-vs-weak dominance conditions (the conditional theorem)

**Status: RIGOROUS (conditional), correctly stated as an iff.** Weak dominance is **unconditional**; strict
dominance holds **iff** (1) the objective discriminates the discarded coordinate (a non-flat spectrum `φ≢1` — a
genuine tail-asymmetric risk attitude; the toy proof §2.3 is the witness) **AND** (2) the optimiser is responsive
(the Bayes-optimal user, or empirically a non-constant-in-the-extra-coordinates LLM). This is the right structure
and it is **what makes the null informative**: a tie is the *correct* answer if the objective is tail-indifferent
(condition 1 fails) **or** the LLM ignores the signal (condition 2 fails — the **mechanism null**, tested by the
**scrambled-feedback placebo**). The mechanism-null precedent is **verified**: **Gupta–Hartford–Liu 2025**, *"LLMs
for Bayesian Optimization in Scientific Domains: Are We There Yet?"* (Findings of EMNLP 2025, arXiv:2509.21403) —
verbatim **(a)** *"classical methods such as linear bandits and Gaussian process optimization consistently outperform
LLM agents"* and **(b)** *"LLM-based agents show no sensitivity to experimental feedback: replacing true outcomes
with randomly permuted labels has no impact on performance."* **Citation precision:** the real title is the
BayesOpt-in-scientific-domains one above (not a generic title); the domain is **experimental design for scientific
discovery**, so cite it as an **analogous-mechanism precedent**, not direct portfolio-RL evidence.

**One construct-validity caveat (cross-ref DEEP_H2 §4).** The selection metric is validation Deflated Sharpe with
**λ=0** (tail-blind), so condition (1)'s "tail-sensitive Φ" is carried by **whether DSR rewards the lower-vol /
thinner-left-tail policies a tail-aware reward induces**. The rf-robustness check (R20) confirms DSR is
tail-sensitive in practice, but the cleanest fix is `DEEP_H2`'s recommendation to **elevate CVaR-5% to a co-primary
tail hypothesis** so the mechanism is tested on the dimension the feedback most plausibly moves. (That is a
statistics/pre-registration change, owned by `DEEP_H2`; flagged here only because it is what makes §2.5 condition (1)
empirically live.)

## §2.6 — Elicitability (Fissler–Ziegel / Gneiting / Ziegel): CORRECT but it is a deliberate RED HERRING for the descriptive use — frame it as such

This is the subtlest theory point and the one where an examiner could either be impressed or catch an over-reach.

**The facts (all verified verbatim against primary sources):**
- **CVaR/ES alone is NOT elicitable** (Gneiting 2011 Thm 11: non-convex level sets). ✅
- **The PAIR (VaR_α, ES_α) IS jointly elicitable** (Fissler–Ziegel 2016 Cor 5.5, relative to distributions with
  finite first moment and unique α-quantiles); the score is **necessarily non-separable** (FZ Remark 5.3). **Cite the
  2021 erratum** (Ann. Statist. 49(1):614, arXiv:1901.08826 — corrects regularity in Prop 3.4 / Thm 5.2(ii); the
  headline stands). ✅
- **FZ0** (Patton–Ziegel–Chen 2019, J. Econometrics 211(2):388–413) requires **ES strictly negative** (the `log(−e)`
  term; fine for left-tail returns at α≤0.1) and **generates 0-homogeneous loss DIFFERENCES** — **write exactly
  that**, never "FZ0 is 0-homogeneous" (it shifts by `+log(k)` under scaling). ✅
- **Ziegel 2016:** the only elicitable **law-invariant coherent** risk measures are essentially **expectiles**
  (minus the τ-expectile, τ∈(0,½] under her profit sign convention, modulo −E). **Always fix the sign convention**
  (Ziegel's τ∈(0,½] vs the loss-orientation literature's τ≥½ is the *same* expectiles) and append "law-invariant,
  modulo −E". The crisp Venn: **VaR** elicitable-not-coherent; **ES** coherent-not-elicitable; **expectiles**
  uniquely both. ✅

**The framing decision (decisive).** The dissertation **measures** CVaR descriptively from a single realized,
fixed backtest series and reports it as **diagnostic feedback**. It does **not** (a) score/rank competing
*forecasts*, (b) run an M-estimator targeting CVaR, or (c) backtest a CVaR forecast — **the only three regimes where
(non-)elicitability binds.** On the empirical distribution, `CVaR_α(F̂)` is just the average of the worst `⌊nα⌋`
realized losses — as well-defined and computable as the sample mean. **The "CVaR is not elicitable" objection, if
raised against feeding CVaR as feedback, commits a CATEGORY ERROR** (conflating "T is not the argmin of an expected
score over a class" with "T(F̂) cannot be computed/reported"). **The killer analogy: variance is not elicitable
either (Lambert–Pennock–Shoham 2008), yet nobody claims you cannot report a sample variance.**

**So why cite elicitability at all?** Two legitimate, non-red-herring uses — keep these, drop any other:
1. **The (VaR, ES) joint-elicitability + FZ0 score is the PRINCIPLED, CITED companion to the bespoke CVaR-difference
   test** (`src/inference/es_backtest`, a Diebold–Mariano comparative backtest on FZ0). This is L7's load-bearing
   move: the bespoke test is size-certified but unpublished; the FZ0/(VaR,ES) DM backtest is the *cited,
   elicitability-grounded* one that does the heavy inferential lifting. **This is the correct, defensible use of
   elicitability in the whole project** — comparing the *arms' tail forecasts* via a strictly consistent score.
   (Note the subtlety, already on record in `SOTA_AND_NOVELTY_VERIFICATION`: the FZ machinery underpins *comparative
   backtesting of forecasts*, which is a **different question** from comparing the *realized* CVaR of two return
   series — the bespoke test's job. Report both; agreement between them is stronger than either alone.)
2. **As a scope/limitation honesty point:** elicitability is *why* CVaR cannot be a stand-alone M-estimation target
   and *why* (VaR,ES) must be carried as a pair — which is consistent with feeding a **profile**, not a lone CVaR
   scalar.

**SAFE WORDING (use):** *"We do not rely on the elicitability of CVaR: the tail statistics are descriptive
functionals of a fixed realized return series (computed like a sample mean), not forecasts being scored, so
elicitability is irrelevant to the feedback channel (cf. variance, which is likewise non-elicitable yet routinely
reported). Elicitability enters only where it should — in the **comparative tail backtest**, where the joint
elicitability of (VaR_α, ES_α) (Fissler–Ziegel 2016; erratum 2021) and the FZ0 strictly consistent score
(Patton–Ziegel–Chen 2019) license a Diebold–Mariano comparison of the arms' tail forecasts."*

**The one genuine concern to concede gracefully (it is NOT elicitability):** **tail estimation error /
non-robustness** — empirical ES uses only the worst `⌊nα⌋` points, so higher variance / slower convergence / lower
robustness than the mean, especially under heavy tails (Yamai–Yoshiba 2002; Cont–Deguest–Scandolo 2010). This is
**L6** (CVaR-1% low power, ~7–8 exceedances) and **L17** (measurement-noise → feedback-content confound) — address
via sufficient backtest length, the EVT/GPD POT fit (EX-DRL precedent), and a block-bootstrap band. Categorically
distinct from elicitability; conflating them is the trap.

## §2.7 — Part (2): the bounded-agent license (Sorg–Singh–Lewis ORP) — why reward design is even coherent

**Status: RIGOROUS (cited).** The Optimal Reward Problem (Singh–Lewis–Barto 2010, IEEE TAMD 2(2):70–82;
Sorg–Lewis–Singh 2010, NeurIPS): `R* = argmax_R E_𝒟[F(A(R))]`, and **`R*≠F` precisely because the agent is
bounded**; the value of reward design shrinks to 0 as capability →∞ (the `B≺E⪯C` lattice). The fixed bounded SB3-SAC
sits at `E`. **This is the clean answer to "why not just optimise Sharpe directly?"** — the bounded agent's `R*` is
not Sharpe, and *finding* `R*` needs the distribution. **Keep it.** One citation-hygiene note: the two back-to-back
TAMD DOIs (Singh …2051031 vs Niekum …2051436) must not be swapped (`H2_THEORY_FOUNDATIONS` already flags this).

## §2.8 — Part (3): the expressivity wall (Skalse–Abate / Abel) — the positive reason the distribution MUST enter via feedback

**Status: RIGOROUS, verified verbatim** (`H2_THEORY_SPINE` confirms against arXiv:2401.14811). **Citation
correction already on record:** "Skalse 2024" is **Skalse & Abate, UAI 2023, PMLR 216:1974–1984** — cite the **2023
UAI** venue. Thm 2 (γ≥0.5): a Markov reward inducing the same trajectory order as `R` is an **affine** transform of
the return; Cor 6–9: **CARA/CRRA/log/mean–variance utilities are NOT Markov-expressible**. Abel et al. 2021
(NeurIPS, arXiv:2111.00876): SOAP/PO/TO task specs exist that no Markov reward expresses. **The argument:**
risk-sensitive portfolio objectives ARE the Cor 6–9 family and are path-dependent, so they **cannot** be baked into
a per-step Markov reward — the risk information **must** enter via the **feedback channel**. This is a *positive*
argument for the architecture (the distribution must enter via feedback because it cannot live in a per-step reward).
**The state-augmentation boundary is correctly stated** (Bäuerle–Ott 2011; Bäuerle–Glauner): with a state augmented
by the running return/VaR threshold, static-CVaR/path-dependent objectives *do* become an ordinary MDP — but the
agent is **held fixed and un-augmented**, so the distribution must (and does) enter through feedback.
- **Citation correction (verified this session):** for the **static spectral-augmentation** result cite
  **Bäuerle–Glauner 2021, *"Minimizing spectral risk measures applied to Markov decision processes"*, MMOR
  94(1):35–69 (arXiv:2012.04521)** — **NOT** the *recursive* paper *"MDPs with recursive risk measures"* (EJOR
  296(3):953–966, **2022**), which yields a Bellman recursion with **no** augmentation and is a different result.
  The augmentation is `(x, running-accumulated-discounted-reward, running-discount)`; the optimal policy depends on
  that running statistic, **not on the mean** (Ott via Rockafellar–Uryasev's `η`-infimum; Glauner via the
  Kusuoka/Pichler infimum — for *full* spectral the outer optimisation is **infinite-dimensional**, unlike CVaR's
  single scalar `η`). The `s_{t+1}=(s_t−r_t)/γ` "remaining-budget" form is **Chow et al. 2015**, the mirror of
  Bäuerle–Ott's accumulation form — attribute correctly.

## §2.9 — The rigorous/hand-wavy ledger (the spine's §6) is itself a grading asset

The spine's strict ledger (12 rows, each tagged RIGOROUS / RIGOROUS-conditional / NEAR-RIGOROUS / HAND-WAVY /
EMPIRICAL) is **exactly** the self-aware demarcation that reads as independence of thought to an examiner. The one
row to double-check after applying §2.4: row 4 ("the tail is off-critic") should be annotated **RIGOROUS (in the
finite-recursion sense; the representation version is a matter of degree)** rather than unqualified RIGOROUS. Row 10
(EIG ⇒ fewer SAC runs) is correctly HAND-WAVY. **Reproduce this ledger in the dissertation** (lightly edited) — it
is a stronger move than presenting the theory as uniformly airtight.

---

# PART C — THE GAPS (consolidated) and PART D — STRONGEST FRAMING

## §3 — Gaps an examiner (Okhrati) would attack, ranked by severity

| # | Gap | Type | Severity | Where it bites | Disposition |
|---|---|---|---|---|---|
| G1 | **"Off-critic" phrased without the finite-recursion gloss** → moment-problem rebuttal | Theory phrasing | **HIGH** | §2.4 | Apply the safe wording verbatim; annotate the ledger row |
| G2 | **Differentiation from Coache–Jaimungal is architectural only** | Positioning | **HIGH** | §1.A | §5 framing: comparative LLM-vs-fixed-objective + honest null; cite as the risk-engine prior art |
| G3 | **Blackwell over-claimed** (full equivalence vs data-processing; θ=F vs θ=Z; weak vs strict) | Theory phrasing | MODERATE | §2.1 | Demote to DPI direction; fix θ=Z; keep weak |
| G4 | **Rowland cited for CVaR/VaR non-closedness** (out of the theorem's scope) | Citation scope | MODERATE | §2.4 | Keep "expectation-form"; label CVaR/VaR as your extension |
| G5 | **Elicitability risks being read as misapplied** to the descriptive feedback | Theory framing | MODERATE | §2.6 | Frame as deliberate red herring (variance analogy); confine elicitability to the FZ0 comparative backtest |
| G6 | **Marthe over-labelled** ("Kolmogorov–Nagumo" vs exponential/entropic) | Citation precision | LOW–MOD | §2.4 | Say "exponential utilities / entropic risk" |
| G7 | **Lyle cited for "risk is intrinsic"** (paper proves only the mean half) | Citation scope | LOW–MOD | §2.4 | Drop that attribution; present as own interpretation |
| G8 | **Kusuoka/Artzner conditions unstated** (atomless space, Fatou property, finite-Ω origin) | Theory completeness | LOW–MOD | §2.2 | State the hypotheses in-text |
| G9 | **Acerbi 2002 spectral vs Acerbi–Tasche 2002 ES PDF conflation** in the corpus | Citation integrity | LOW | §2.2 | Cite the correct Acerbi 2002 spectral paper + DOI |
| G10 | **Bäuerle–Glauner 2021 (static) vs 2022 (recursive) mis-citation risk** | Citation precision | LOW | §2.8 | Cite the 2021 MMOR 94 static paper for augmentation |
| G11 | **post-2018 BAB/low-vol decay asserted as fact** (it is folklore) | Finance citation | LOW | §3.A | Frame as practitioner observation; cite Novy-Marx–Velikov 2022 instead |
| G12 | **CVaR-1% on ~7–8 exceedances + EVT-noise confound** (tail estimation error) | Empirical/measurement | MODERATE | §2.6 | Lead with CVaR-5/10%; EVT/GPD POT + bootstrap band; L6/L17 disclosure |

**Note the asymmetry:** G1, G3, G4, G6, G7, G8 are all **phrasing/scope** fixes (zero compute, pre-freeze-safe) that
strictly *protect* the theory — none changes a result. G2 is the one substantive positioning gap. G12 is the genuine
empirical limitation (already on record as L6/L17). **The theory is sound; the work is in saying it precisely.**

## §4 — The single strongest framing (lead the theory chapter with this)

State H2 as a **corollary of three theorems plus one license**, in this order:

1. **Signal sufficient; scalar not** (Kusuoka 2001 §2.2 — risk content = the CVaR profile = the coordinate basis of
   the law-invariant coherent class; Artzner 1999 — Sharpe is not even coherent; the toy proof §2.3 — explicit
   Gaussian-vs-tail witness at matched mean–variance).
2. **Sufficiency ⇒ channel dominance** (the data-processing direction of Blackwell §2.1 — since Sharpe is a
   deterministic statistic of the same sample, the distributional channel weakly dominates for the design decision
   under *every* objective; strictly under any genuine non-flat risk attitude).
3. **The tail is provably extra information the agent's value recursion cannot carry** (Rowland 2019 §2.4, in the
   finite-recursion sense) — so it *must* be measured off-critic; and it *cannot* be baked into a per-step Markov
   reward (Skalse–Abate / Abel §2.8) — so it *must* enter via the feedback channel.
4. **The whole enterprise is coherent only because the agent is bounded** (Sorg–Singh–Lewis §2.7 — `R*≠F`, so there
   is a reward worth designing, and finding it needs the distribution).
5. **∴ H2** asks the one empirical question the theory leaves open: *does our bounded LLM optimiser, at matched
   compute, actually USE that sufficient signal?* The theory bounds an **envelope** (more information cannot hurt the
   optimal user); H2 measures whether the real optimiser attains it. **This makes the null informative** (it can fail
   for the four catalogued reasons — tail-indifferent objective, unresponsive optimiser, unmeasurable tail at n≈750,
   or matched-compute-erases-acceleration) **and the win mechanistic** — which is exactly what a pre-registered
   headline needs.

**Why this framing wins (and is the move that earns 90–100% on theory):** it is **examiner-proof on both sides** —
the finance/risk reviewer sees Kusuoka/Artzner/Acerbi/Rockafellar–Uryasev/elicitability; the ML reviewer sees
Rowland/Blackwell/Lindley/active-learning — meeting at the single concept *"sufficient statistic / value of
information."* It cleanly separates the contribution from **Eureka** (scalar-component reflection *against an oracle*
→ distributional reflection under **no** oracle) and from **Coache–Jaimungal** (researcher-fixed distortion →
**LLM-designed** objective). And it carries its own honest demarcation (the §2.9 ledger; (b.iii) labelled analogy).

**Second-strongest framing move (closes G2): reframe the Coache–Jaimungal differentiation as an empirical contrast,
not just an architectural delta.** Position Coache–Jaimungal (2409.10096) as the **strongest non-LLM
distributional-RL-on-portfolio comparator** and state the delta as N1 (the objective is *designed/iterated by the
LLM*, not fixed a priori). Where feasible, show an empirical edge — **or an honest null** — of LLM-designed rewards
over a strong fixed risk objective in their spirit; a *null* here is still a clean, pre-registered finding (the LLM
search did not beat a well-specified human risk objective at matched compute), and is far more defensible than an
architectural-novelty claim alone.

---

# PART E — PRIORITISED IMPLEMENTABLE IMPROVEMENTS

Grade-ROI × pre-freeze risk × strict verdict (conservative). **All theory/citation items below are
documentation-only (zero code, freeze-safe).** The empirical/pre-registration items defer to `DEEP_H2.md` and the
limitations register, which own them.

| # | Improvement | Grade-ROI | Pre-freeze risk | Verdict |
|---|---|---|---|---|
| **T1** | **Apply the §2.4 "off-critic / finite-recursion" safe wording** + annotate ledger row 4. Pre-empts the moment-problem attack — the one genuine theory hole. | **HIGH** | **None** (prose) | **DO NOW** — green |
| **T2** | **Apply the §2.1 Blackwell precision** (data-processing direction; θ=Z; weak-only; σ=0 domain). | **HIGH** | None (prose) | **DO NOW** — green |
| **T3** | **Apply the §2.4 Rowland scope fix** (keep "expectation-form"; label CVaR/VaR non-closedness as your own extension). | **HIGH** | None (prose) | **DO NOW** — green |
| **T4** | **Frame elicitability as a deliberate red herring for the descriptive use (§2.6 safe wording + variance analogy)**; confine elicitability to the FZ0 comparative backtest. | **HIGH** | None (prose) | **DO NOW** — green |
| **T5** | **State the Kusuoka/Artzner hypotheses in-text** (atomless standard space, Fatou property, finite-Ω origin + Delbaen general-space extension). | MODERATE | None (prose) | **DO NOW** — green |
| **T6** | **Citation corrections:** Acerbi 2002 spectral ≠ Acerbi–Tasche 2002 ES (G9); Bäuerle–Glauner **2021 MMOR 94** static, not 2022 EJOR recursive (G10); Skalse–Abate **2023 UAI**; Marthe = exponential/entropic not Kolmogorov–Nagumo (G6); drop Lyle for "risk intrinsic" (G7); Gort 5th author Chen; Harvey–Liu–Zhu third author Heqing Zhu; PBO "2016/2017". | **HIGH** (supervisor catches bad cites) | None (refs.bib) | **DO NOW** — green |
| **T7** | **Reproduce the §2.9 rigorous/hand-wavy ledger** in the dissertation (with row-4 annotation). Demarcation reads as rigour. | **HIGH** | None (prose) | **DO NOW** — green |
| **T8** | **Add the GEPA (ICLR 2026 Oral) + Eureka −28.6% + Gupta–Hartford–Liu citation upgrades** (§2.5, §1.A-Eureka); cite LaRes/CARD/RF-Agent as near-misses to pre-empt the novelty objection; mark FORGE withdrawn. | MODERATE | None (refs.bib) | **DO NOW** — green |
| **T9** | **Reframe Coache–Jaimungal as an empirical contrast (§4 move 2)** — name the comparative-vs-fixed-objective delta; show an edge or an honest null. Closes G2. | **HIGH** | Empirical (needs the comparator run); the *framing* is free | Framing **DO NOW**; the comparator run defers to campaign scope |
| **T10** | **Pre-register the FF5+UMD+BAB factor-attribution ladder as a declared secondary family** (L15); frame post-2018 BAB decay as practitioner observation (G11). | **HIGH** (the single attack that can recast the headline) | **Pre-registration amendment** — user approval required | **DO** — needs user ratify (already a flagged amendment) |
| **T11** | **Report generations-to-winner alongside final OOS** (§1.A-Eureka gap) so a matched-compute tie still yields the "acceleration-but-not-ceiling" finding. | MODERATE | Verify it is logged (likely no code change) | **DO** — verify-green |
| **T12** | **CVaR-1% / EVT-noise disclosure** (G12) — lead with CVaR-5/10%; report the threshold-sensitivity spread; L6/L17 paragraphs. | MODERATE | None (already on record) | **DO** — defers to limitations register |

**The decisive set for the theory grade (Okhrati):** **T1–T7** (all zero-risk prose/citation fixes) convert a
theory section that is *correct in substance* into one that is *correct in phrasing under expert scrutiny* — which is
the difference between a strong distinction and 90–100% on the dimension he weights most. **T9/T10** are the two
substantive positioning/robustness moves; T10 needs the user's pre-registration ratification.

---

## Appendix — verification ledger (what was checked first-hand this session)

**Primary sources read first-hand (PyMuPDF extracts, `D:\tmp\littxt\`):**
- **Kusuoka 2001** (`…Kusuoka-LawInvariant…`): Theorems 4 (sup-of-CVaR-mixtures, general), 5 (uniqueness of mixing
  measure), 7 (single mixture, comonotone), 9; the atomless-standard-space + Fatou-property hypotheses; `ρ_α` =
  CVaR/AVaR. ✅ confirms §2.2 exactly.
- **Artzner et al. 1999** (`…Artzner-Coherent…`): the four coherence axioms via the acceptance-set formulation;
  finite-Ω origin; VaR-subadditivity repair. ✅
- **Acerbi–Tasche 2002** (`…AcerbiTasche-ES…`): confirmed this is the **ES-coherence** paper, **not** the
  spectral-measures paper — citation-integrity flag G9. ✅

**Verified by adversarial web research this session (verbatim quotes confirmed by sub-agents from primary PDFs /
journal pages / arXiv / ACL Anthology):** Blackwell 1953 (finite-parameter caveat; DPI = the easy direction);
Fissler–Ziegel 2016 + erratum 2021 (joint elicitability, non-separable score); Gneiting 2011 (CVaR not elicitable,
Thm 11); Ziegel 2016 (expectiles = only elicitable law-invariant coherent, sign convention); Patton–Ziegel–Chen 2019
(FZ0 generates 0-homogeneous loss *differences*, ES<0 condition); Rowland et al. 2019 (Thm 4.3 expectation-form
scope, Lemma 4.4 = corollary not counterexample, "CVaR/VaR/distortion" absent from the paper); C51 2017
(Wasserstein contraction, control non-contraction Prop 1+2); Lyle et al. 2019 (mean-equivalence only, not "risk
intrinsic"); Marthe et al. 2023 (exponential/entropic, not Kolmogorov–Nagumo; Thm 1 = evaluation bound);
Bäuerle–Glauner 2021 static vs 2022 recursive; GEPA (ICLR 2026 Oral, "35× fewer rollouts", GRPO baseline); Eureka
−28.6% reflection ablation; Gupta–Hartford–Liu 2025 (both claims verbatim, Findings of EMNLP 2025); the
moment-problem / finite-moment VaR-CVaR bound non-uniqueness (the §2.4 rebuttal); the portfolio-DRL critique
corrections (Sun–Wang–An verbatim; Gort 5th author Chen; 2307.07694 single-author + simulated data; DeMiguel 7
datasets/14 models; Ferrari Dacrema 18/7/6; Harvey–Liu–Zhu Heqing Zhu; Frazzini–Pedersen 0.78 scope;
Novy-Marx–Velikov 2022 as the BAB mechanism challenge; post-2018 decay = folklore).

**Grounded against (read fully this session):** `00_planning/H2_THEORY_SPINE_2026-06-21.md`,
`H2_THEORY_FOUNDATIONS_2026-06-19.md`, `LITERATURE_AND_DEFENSE_COMPANION.md`,
`research/SOTA_AND_NOVELTY_VERIFICATION.md`, `LIMITATIONS_REGISTER.md` (L1–L19),
`research/ADVERSARIAL_REVIEW_2026-06-17.md`, `docs/DEEP_H2.md` (the complementary statistical/construct-validity
audit this document does **not** duplicate).

**Out of scope here (owned elsewhere):** the H2 statistical-inference machinery — conjunction×BH double-correction,
IUT reframe, TOST unit-matching, per-seed rliable bootstrap, EVT bias-correction-vs-code reconciliation, CVaR-5%
co-primary elevation — is the subject of `docs/DEEP_H2.md` and is referenced, not re-derived, above.
