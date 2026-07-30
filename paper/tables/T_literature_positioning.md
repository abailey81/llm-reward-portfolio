# Table (CH2): Literature positioning matrix

**Purpose.** The single artefact that makes the novelty cell legible in three seconds. Rows are the
nearest neighbours; columns are the dimensions that actually separate them from this work. Tables are
excluded from the 10,000-word limit, so this carries the comparison that prose would otherwise have to
spend ~400 words on.

**Sourcing discipline.** Every cell is traceable to a first-hand-read entry in
`paper/01_LITERATURE_DOSSIER.md` (all 196+ corpus PDFs read first-hand; each neighbour below carries a
`VERIFIED first-hand` date or a quoted verbatim claim). **Papers named in external commentary but for
which the dossier holds no detailed entry — RD-Agent, Auto-MC-Reward, DrEureka — are DELIBERATELY OMITTED
rather than filled in from memory.** A matrix is only as strong as its weakest cell, and an invented cell
is worse than an absent row.

---

## The matrix

| Work | Domain | Who authors the reward | What the loop's feedback contains | Agent held fixed? | Risk-sensitive objective? | Pre-registered? |
|---|---|---|---|---|---|---|
| **Eureka** (ICLR 2024) | robotics / control | **LLM writes reward code** | per-component **scalar** training series + aggregate fitness (verbatim §3.3: "tracks the **scalar values** of all reward components") | yes | no | **no** |
| **Text2Reward** (ICLR 2024 Spotlight) | robotics / control | **LLM writes reward code** | human natural-language **failure summaries** | yes | no | **no** |
| **REvolve** (ICLR 2025) | autonomous driving | **LLM writes reward code** | human **Elo preferences** | yes | no | **no** |
| **CARD** (arXiv 2410.14660) | robotics / control | **LLM writes reward code** | process / trajectory feedback + a **binary** success>failure return ordering | yes | no | **no** |
| **DLM** (NeurIPS 2024) — *structural twin* | public-health RMABs (bandit) | **LLM writes reward code** | simulated-outcome **distribution** | no (bandit, not continuous-action) | no | **no** |
| **ELfolio** (2025) — *closest portfolio system* | **portfolio** | LLM writes trading-**strategy** code (not the reward) | **scalar Sharpe** as fitness (verbatim: "the Sharpe ratio serving as the fitness function") | no (path templates vary) | no | **no** |
| **FinRL-DeepSeek** (arXiv 2502.07393) | **portfolio** | **fixed, hand-written** CPPO / CVaR-PPO objective | LLM emits sentiment/risk **scores that scale actions** | yes | **yes** (CVaR objective) | **no** |
| **GIFT** (arXiv 2606.08450) — *freshest finance neighbour* | **portfolio** | LLM designs the **state–reward interface**: an intrinsic term + a subset of a **fixed risk-rule library** | generic rollout diagnostics (ICs, reward trend/variability, drawdown) | **no — co-varies the STATE** | partially (fixed rule library) | **no** |
| **FINCON** | **portfolio** | no numeric reward trained into a policy | CVaR by **verbal** reinforcement over beliefs | n/a | **yes** (CVaR, verbally) | **no** |
| **▶ THIS WORK** | **portfolio** | **LLM writes reward code** | **multi-quantile realized-return lower-tail profile** — CVaR 5/10/25/1 %, left-tail mass, robust skew — measured **off-critic** | **YES — SAC held fixed; ONLY the fed block varies** | **yes** (tail-aware by construction) | **YES — frozen hash `3ca6f01a…`, tag `prereg-v2.1`** |

---

## What the matrix is designed to show

**1. The conjunctive cell is empty.** No prior work combines *LLM-authored reward CODE* + *multi-level
tail feedback as the manipulated variable* + *a fixed agent* + *risk-sensitive portfolio RL*. Each
neighbour fails at least one column, and the failures are structural rather than incidental:

* the **reward-design lineage** (Eureka, Text2Reward, REvolve, CARD, DLM) feeds **scalars, prose, or
  preferences** — never a distributional tail profile — and none is in finance or risk-sensitive;
* the **finance neighbours** either do not let the LLM author the reward at all (FinRL-DeepSeek: a score
  encoder over a *fixed* CVaR objective; FINCON: verbal, no trained reward), author a *strategy* rather
  than a reward (ELfolio, on **scalar Sharpe** fitness — which is *precisely this study's control arm*),
  or **co-vary the state** alongside the reward (GIFT), which forfeits identification.

**2. The pre-registration column is the strongest claim, and it should lead.** The empty-cell claim is
disputable by construction — a referee can always name an adjacent paper. But "no pre-registration
anywhere in the automated-reward-design literature" is a claim about a **practice**: it is verifiable in
an afternoon, and it cannot be defeated by pointing at a similar study. It is the limb that satisfies the
rubric's *unquestionable* wording, so it goes first in the prose.

**3. ELfolio is the sharpest single comparison.** Its fitness is scalar Sharpe — *this study's control
condition* — so the nearest portfolio system in the literature is, in effect, running our baseline arm
without the treatment. That is a far more useful sentence than "no one has done this".

---

## Cross-references (to be wired at write time)

* Prose that uses this table: CH2 (Related Work), the converging five-move argument.
* The four affirmative contributions that stand even if the cell crowds: instrument / protocol /
  theory envelope / mechanism audit.
* Companion table: "what each test and control defends against" (the five rival accounts and their
  fingerprints).
* Every citation key here resolves in `paper/refs.bib`; run `/verifying-citations` before compiling.

**⚠ Maintenance.** Novelty is protected by dated sweeps every 2–3 weeks plus a MANDATORY pre-submission
sweep. If a sweep surfaces a new neighbour, it gets a row here **and** a cite-and-distinguish sentence in
CH2 — never a silent omission.
