# PRE-SUBMISSION / PRE-FREEZE CHECKLIST — the staged worklist

> Consolidated 2026-07-09 from the overnight self-improvement loops
> (`docs/SELF_IMPROVEMENT_LOOP_LOG_2026-07-08.md` §STAGED). **This is the tidy list to work from when
> the write-up resumes** — every citation below was VERIFIED FIRST-HAND (author/venue/claim) unless
> marked `%VERIFY`. Loop refs (Lnn) point back to the loop-log entry with the full evidence.
> NOTHING here is applied to the paper yet (write-up deferred by Tamer 2026-07-08). The freeze hash
> `1c6b76b6` is UNCHANGED; all cites are additive.

## 0. Status at consolidation (loop 78)
- **Code: converged-flawless.** ~28 core modules + the ENTIRE confirmatory decision path
  (paired_seed_difference_test → IUT legs → h2_conjunction → H2_supported; power_analysis for n) +
  leakage-prevention + factor-attribution first-principles verified, AND the full pytest suite is GREEN
  (**2090 tests / 117 files, exit 0**, L77). Only real code fix all session: variance_decomposition.py
  honest σ²_search=0 rendering (L56, applied+verified).
- **Novelty cell ROBUST to July-2026** (LLM authors reward CODE + multi-level tail feedback as the
  manipulated variable + pre-registered controlled comparison + portfolio-RL): the reward-code-design space
  is active but all non-finance/generic-feedback/no-prereg; the finance-LLM space doesn't author reward code.

## 1. CITATIONS TO APPLY (verified first-hand; bib keys + placement)

### CH2 — related work, cite-and-DISTINGUISH (the novelty fence)
| bib key / id | one-line what it is → how to distinguish |
|---|---|
| `GIFT` 2606.08450 | LLM shapes a predefined state/reward INTERFACE (PPO, adaptive, no pre-reg, no LLM at test) → we author reward CODE, tail-feedback-manipulated, pre-registered. |
| `FinRL-DeepSeek` 2502.07393 | LLM supplies NEWS signals/risk-assessment, not reward code. |
| `RDA` 2606.01672 | VLM (visual) reward-design agent for ROBOTICS, not LLM+finance. |
| `URDP` 2507.02256 | Eureka+uncertainty successor, general robotics, general reward design (not tail). |
| `Adaptive-Alpha-PPO` 2509.01393 | LLM generates ALPHA signals; PPO weights them (not reward code). |
| `Moira` 2605.01954 (May-26) | LLM-AS-POLICY via prompt-updates for PAIR trading (not reward-code, not tail, not pre-reg). |
| `LEARN-Opt` 2511.19355 | Eureka-style reward-CODE but robotics/CONTROL, standard metrics. Its "no env-source-code" result SUPPORTS our channel-isolation deviation. |
| `CARD` 2410.14660 / KBS-2025 | Closest journal-published "LLM reward-CODE + dynamic feedback": MiniGrid/MuJoCo, generic trajectory/preference feedback, not pre-registered. |
| catalogued distinct | `PROF` 2511.13765 (offline imitation), `RF-Agent` 2602.23876 (tree search), `Risk-Averse-Finetuning-of-LLMs` 2501.06911 (LLM is the POLICY). |

### CH2/mechanism — numeracy-bottleneck grounding, cite-and-USE (all VERIFIED)
- `zhu2024numbers` (2401.03735, numbers linearly encoded) + `2601.09706` (value-aware numeric representations)
  + `2510.06824` (BitTokens, single-token IEEE-754 magnitude-preserving) = the mechanistic WHY the fed CVaR
  floats may not be reliably USED (tokenisation doesn't encode magnitude → legibility differential).
- `levy2026caution` (Bradford Levy, *"Caution Ahead: Numerical Reasoning and Look-Ahead Bias in AI Models"*,
  **JAR 64:1139–1188, 2026**) — top-journal; dual use (LLM-finance performance is a modelling artefact + a
  look-ahead-bias test on numerical content).
- `shrestha2025mathematical` (2502.08680, Shrestha/Kim/Ross, *"Mathematical Reasoning in LLMs…Wide Numerical
  Ranges"*) — VERIFIED L89; QUANTITATIVE anchor: ~14-pp rise in logical error rate with numerical complexity,
  SYSTEMATIC not random, degrades OOD + when computations are EMBEDDED in a task (our CVaR floats sit embedded
  in the reward-design task). The mechanism is reconfirmed at the 2026 frontier (digit-wise representation ⟹
  embedding-similarity ≠ numerical-proximity ⟹ the "9.11>9.8" close-decimal failure = our fed-CVaR regime).

### CH4 — methods (EVT / tail-backtest), cite-and-position (VERIFIED)
- `dinnocenzo2026joint` (D'Innocenzo, Lucas, Schwaab, Zhang, *"Joint extreme VaR & ES dynamics with a single
  integrated tail shape parameter"*, **JBES 2026**) — SOTA time-varying conditional-GPD; positions our
  deliberately-static per-window empirical+EVT estimator (the fed vector is what varies, not the estimator).
- `mcneil2000estimation` — ALREADY APPLIED to CH4 (the POT/window-size precedent).
- `bauer2025evaluating` (Lukas Bauer, *"Evaluating financial tail risk forecasts: Testing Equal Predictive
  Ability"*, arXiv 2505.23333, 2025) — EPA neighbour for our comparative FZ0 backtest; grounds the
  low-power/type-III caveat at α=1% on short OOS (already cited in es_backtest.py; safe to migrate to prose).

### CH4 / §limitations — contamination & bias controls, cite-and-USE (VERIFIED)
- `li2025profit` (*"Profit Mirage"*, 2510.07920) — LLM-agent back-test returns evaporate past the knowledge
  cutoff via leakage → motivates our contamination/embargo; argue our anonymised-array + sealed-OOS design
  CLOSES that channel by construction.
- `kong2026evaluating` (2602.14233, Feb-26, Kong…Bradford Levy…Stefan Zohren) — five-bias taxonomy
  (look-ahead, survivorship, narrative, objective, cost) maps 1:1 onto our controls (embargo /
  univ5-survivorship-free-PIT / cost_sweep); "structural validity before any result is used" ≈ our
  prereg+freeze. Position paper, no novelty threat.
- `yao2026beyond` (2606.08285, Yao & Zheng, *"Beyond Agent Architecture: Execution Assumptions and
  Reproducibility in LLM-Based Trading Systems"*, 2026 — VERIFIED L82) — a field-wide reproducibility AUDIT
  (30 studies) whose named gaps our design CLOSES one-by-one: point-in-time (univ5 PIT loader),
  temporal-split discipline (purge+embargo sealed-leg), execution timing (C-5 rebalance-then-realize),
  turnover/transaction-cost modelling (drifted-turnover + cost_sweep), artifact release (archive-replay +
  freeze). Turns a field critique into a checklist we PASS — the strongest reproducibility positioning cite.

### CH7 — future work / positioning (VERIFIED)
- `moghimi2025beyond` (*"Beyond CVaR: static Spectral Risk Measures in distributional RL"*, **ICML 2025**,
  PMLR 267:44571–44593) — theoretical umbrella for our fed vector as a COHERENT-RISK PROFILE; the
  spectral-risk future-work anchor. Pair with `moghimi2025risksensitive` (2507.03900, SRM actor-critic,
  online+offline — VERIFIED L80; same authors; the offline-RL angle ties to Okhrati's CQL field).

### DISCUSSION — reward-hacking / Goodhart framing (L75, NOVEL angle)
- `2605.28918` (Wang et al., *"When LLM Reward Design Fails"*, 2026 — VERIFIED: MiniGrid/MuJoCo method paper,
  failure-mode taxonomy incl. "reward flooding") + survey `wang2026reward` (2604.13602, VERIFIED L80) +
  `gao2023scaling` (2210.10760, Gao/Schulman/Hilton reward-model overoptimization scaling laws, ICML 2023,
  VERIFIED L80). See the paragraph in §2.

## 2. GRADED-PROSE PARAGRAPHS TO INSERT (drafts ready)

### (a) CH7 Mayoian-severity anchoring — near the "corroborated prediction" claim (~`CH7:47`)
Pre-empts the register's TOP-RANKED objection (§1: epistemology of a pre-registered null). Verify
Mayo/Rubin/Gelman-Loken bib keys before inserting. **Draft** (in the loop-log §STAGED [LOOP 26]).

### (b) Discussion — reward-hacking / Goodhart (NOVEL, L75)
Two moves: (i) frame our reward-INDEPENDENT validation-DSR selection + eval-on-realised-`port_ret`-not-reward-
total + PopArt scale-norm as STRUCTURAL DEFENSES against the LLM-reward-design failure modes (`2605.28918`
"reward flooding"; `2210.10760` overoptimization); (ii) the ORIGINAL reframe — the numeracy bottleneck (SQ1
null) IMMUNISES the designer against Goodhart-gaming its own fed tail metric (SQ3 = "does the designer game the
fed metric"). Ties the mechanism to a live safety literature Okhrati (LLM-risk) values; cite-and-distinguish.

## 3. `%VERIFY` BEFORE CITING (not yet first-hand verified)
- **NOW VERIFIED first-hand (L80), moved out of %VERIFY:**
  - `wang2026reward` (2604.13602, *"Reward Hacking in the Era of Large Models: Mechanisms, Emergent
    Misalignment, Challenges"*, Wang et al., 2026) — a SURVEY (Proxy Compression Hypothesis); the
    reward-hacking landscape cite for the Discussion. About model/agent gaming, distinct from our
    LLM-reward-DESIGNER role.
  - `gao2023scaling` (2210.10760, *"Scaling Laws for Reward Model Overoptimization"*, Gao, Schulman, Hilton;
    arXiv 2022 → **ICML 2023**) — canonical Goodhart/overoptimization scaling laws.
  - `moghimi2025risksensitive` (2507.03900, *"Risk-sensitive Actor-Critic with Static Spectral Risk Measures
    for Online and Offline RL"*, Moghimi & Ku, Jul 2025) — SRM actor-critic generalizing CVaR/Mean-CVaR;
    SAME authors as `moghimi2025beyond` (a coherent SRM thread), and its OFFLINE-RL applicability ties to
    Okhrati's CQL/offline-RL field. The intended `2507.03900` for the CH7 SRM positioning.
- **NOW VERIFIED (L83):** `yin2026implementation` (2603.20319, Yin/Miki/Lesnichenko/Gural, *"Implementation
  Risk in Portfolio Backtesting"*, Financial Innovation 2026) — CH7 future-work (execution-realism error
  source; finance-methodology, not a threat).
- **✅ QUEUE NOW EMPTY (L88) — the last two verified first-hand:**
  - `liu2026beyond` (DistRLVR, *"Beyond Scalar Critics: A Distributional Perspective on RL with Verifiable
    Rewards for LLMs"*, Liu et al., **ICLR 2026**) — CH2 cite-and-distinguish + SUPPORTIVE motivation
    (distributional CRITIC for LLM RLVR, distinct from our distributional FED feedback; its "scalar critics
    obscure the distributional return structures and attenuate tail information" independently confirms our
    premise at a different layer).
  - `arian2024backtest` (Arian, Norouzi, Seco, *"Backtest Overfitting in the ML Era"*, **Knowledge-Based
    Systems 2024**) — CH4 methods: its finding that CPCV OUTPERFORMS K-Fold/Purged-K-Fold/Walk-Forward
    VALIDATES our CPCV-on-winners choice. (Abstract/venue-confirmed; full text paywalled but the cited
    finding is the abstract.)
- **All staged citations are now verified first-hand** (scorecard 29 verified / 2 caught / 1 mis-bin fixed).

## 4. ⚠ DROPPED — do NOT cite (caught mischaracterised)
- `2601.14658` — general tokenizer "phantom edits", NOT number-fragmentation. Do NOT cite for numeracy.
- `2605.29586` (FinVerBench) — verification-CALIBRATION, NOT a financial-arithmetic gap. Do NOT cite for numeracy.
- `2405.19313` — belongs in the RISK-CHOICE bin (arithmetic-trained-LMs predict human risk/time choice,
  adjacent to Okhrati ACL'25), NOT the numeracy-embedding basis.

## 5. PRE-FREEZE FIXES (hash-bound — do at the freeze, not autonomously)
- `config/preregistration.yaml`: the `search.headline_reflect_protocol` comment cites the reflect-on-best
  logic at `src/llm/loop.py:604-615`, but the code drifted to `399-402 / 436-438 / 685-693`. The CLAIM is
  TRUE (Eureka-faithful reflect-on-BEST, verified L63); only the LINE REFERENCE is stale. Cosmetic; fix
  during the pre-freeze pass (preregistration.yaml is hash-bound — a comment edit will re-hash, so do it as
  part of the deliberate freeze, not before).

## 6. ALREADY APPLIED THIS SESSION (reference — not to redo)
- CH4: EVT/GARCH disclosure via `mcneil2000estimation` (L26).
- `scripts/variance_decomposition.py`: honest σ²_search=0 rendering (L56; 20/20 tests, hash unchanged).
- `scripts/myriad/build_env.sh` Apptainer fallback + `scripts/install_onstart_task.ps1` boot-roster (earlier).
- WRITE-UP strengthening (staged): frame per-training resume as convergence-aware-OPTIMAL for ≤3h single-GPU
  jobs (cite the 2024 convergence-aware-checkpointing work) — turns a design choice into a literature-justified one.
