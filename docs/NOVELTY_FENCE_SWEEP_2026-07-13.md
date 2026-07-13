# Novelty-fence sweep — 2026-07-13 (dated; the ~2–3-week cadence)

> Previous sweep: 2026-06-26/28 (24-agent + publishability push). Method this time: one web-research
> agent, 21 structured queries + 12 first-hand abstract-page fetches; every claim below verified
> first-hand unless listed under "unverified". Next sweep due: ~2026-07-27–08-03, plus the
> MANDATORY pre-submission sweep.

## VERDICT

**The conjunctive novelty cell is still EMPTY — HIGH confidence.** No work combines: LLM-authored
executable reward-function *code* for a *fixed* deep-RL *portfolio* agent + the *feedback channel*
(multi-level tail-risk statistics vs scalar) as the manipulated variable + a *pre-registered,
placebo-controlled* comparative design. Pressure is converging from two flanks that have not met:
the **finance flank** (GIFT, ELfolio, AlgoEvolve, MadEvolve, QuantaAlpha — LLMs author finance
artifacts, none authors the reward of a fixed RL agent under a tail-feedback manipulation) and the
**methods flank** (Gallego, RDA — feedback-channel *content* is now an explicitly manipulated
variable, but with social/visual feedback in social dilemmas/robotics, never tail-risk, never
pre-registered). The squeeze RAISES the urgency of the pre-submission sweep; it does not touch the
conjunction today.

## Status changes vs the June sweep

- **ELfolio — now journal-published** (*Intelligent Computing* 4:0176, DOI 10.34133/icomputing.0176).
  Our bib already carries the journal version (`zeng2025elfolio` ✓, applied 07-02). No 2026
  portfolio follow-up found under the author names. ⚠ Open thread: the SPJ full text 403'd — a
  library-access read to confirm the journal version added no RL-reward arm (pre-submission item).
- **CARD** — KBS journal version already in the bib (`sun2024card` ✓).
- **Gallego 2026** — final version identified precisely: arXiv 2603.19453, final 2026-06-30,
  NExT-Game @ ICML 2026. Bib current (`gallego2026beyondscalar` ✓). His "feedback aliasing" concept
  is usefully convergent with our numeracy-bottleneck mechanism — engage it in CH2/CH7 at write
  time (LLM *policy* code, social metrics, no reward authorship, no placebo, no pre-registration).
- **GIFT (finance)** — full metadata now verified (arXiv 2606.08450, 2026-06-07, 13 authors):
  composes auxiliary rewards from a risk-RULE LIBRARY **and modifies the state space**. The
  four-axis distinction (rule-library not free-form code; state+reward varied — breaks the
  only-the-reward-varies identification; no tail-vs-scalar manipulation; no pre-registration) is
  already in the FRAMING positioning paragraph ✓. ⚠ Acronym clash: an unrelated robotics "GIFT"
  (arXiv 2603.22574) exists — never conflate.
- **DLM lineage** — the Verma et al. restless-bandit follow-up is now a Springer chapter
  (10.1007/978-3-032-08064-6_19); public-health, no finance/tail.
- **`kvasiuk2026madevolve` — the 2026-06-30 "possible hallucination" flag is RESOLVED: REAL**
  (arXiv 2605.23007 fetched first-hand; Kvasiuk, Li, Colegrove, Münchmeyer). The entry stays.
- **RD-Agent(Q), AlgoEvolve, Eureka/Text2Reward/DrEureka** — no relevant movement.

## New adjacent works (verified; added to refs.bib where useful)

- **RDA** (arXiv 2606.01672, robotics; replaces Eureka's numerical feedback with visual trajectory
  analysis) — already in the bib from 07-02 ✓. Evidence the field recognizes feedback CONTENT as
  the axis; no finance, no tail, no controlled comparison.
- **LaRes** (NeurIPS 2025; LLM adaptive reward search in evolutionary RL) — ADDED
  (`lares2025adaptive`). Eureka-lineage cite.
- **"The End of Reward Engineering?"** (arXiv 2601.08237, position paper) — ADDED
  (`su2026endrewardengineering`). Candidate CH2 field-framing cite.
- **FinRL-DeepSeek** (`benhenda2025finrldeepseek` ✓ already in): LLM emits *signals* into a
  CVaR-PPO agent — the identification-breaking move (signals into state/reward) our design
  excludes; cite as the contrast.
- Confirmed non-threats (no LLM or no reward authorship): Risk-Aware Reward (2506.04358),
  Decomposable Forex Reward (2604.00031), Tail-Safe Hedging (2510.04555 — possible CVaR-under-RL
  genre cite), Darmanin & Vella FLLM 2025 (strategy directives, not reward code).
- The 2026 "reward survey" papers (2602.09305, 2505.02686) are about reward models for LLM
  post-training — a DIFFERENT lineage; do not cite for our cell.

## Unverified (do NOT cite as confirmed; recheck at the pre-submission sweep)

FORGE (OpenReview Z6GStCfccl; venue status unknown) · ERFSL (2605.19259) · PROF (2511.13765) ·
LEARN-Opt (2511.19355) · title-level-only: SELAUR, platoon-reward, incentive-aware MARL,
multimodal evolutionary policy search, Agentic Trading, Alpha Illusion, Regret-Driven Portfolios,
FinPos, QuantAgent, EvoTrainer.

## Action items

1. ✓ Bib current (2 new entries added; ELfolio/CARD/Gallego/GIFT/RDA were already journal-current).
2. Write-time: engage Gallego's "feedback aliasing" in CH2/CH7; one MadEvolve p-hacking-rigor line.
3. Pre-submission sweep MUST: re-run the fresh-entrant queries; resolve the ELfolio full-text 403;
   re-check the unverified list; re-verify FORGE's venue.
