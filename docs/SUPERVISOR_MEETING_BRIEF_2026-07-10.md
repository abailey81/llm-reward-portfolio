# Supervisor meeting brief — Dr Ramin Okhrati, 10 July 2026

> Prepared 2026-07-10. Every number below was re-verified against the live repo today
> (freeze gate, `config/preregistration.yaml`, `docs/SEED_DECISION_2026-07-05.md`,
> `power_analysis.py --assurance`, `determine_design.py`). **Your 3 July email is now one week
> stale — §1 lists exactly what changed and what you must NOT repeat.**

---

## §0 — The 90-second opener (say this first)

> "Since I wrote, three things changed. First, Myriad: the compute question is essentially solved —
> the full study now runs in days, not weeks, so the seed trade-off I asked you about has mostly
> dissolved. Second, I was wrong about one thing in my email: the **tail leg of my co-primary test is
> already conclusive at 30 seeds** — it's only the Sharpe leg that needs the big seed count, and that
> reframes the decision. Third, I've found a concrete mechanistic explanation for why a null would
> arise — a numeracy bottleneck — and it's testable. The pre-registration is complete and frozen-ready
> except for **one** parameter: the seed count. Your answer today unblocks the freeze."

That opener does four things Ramin rewards: leads with the update, **volunteers a self-correction**,
foregrounds mechanism, and gives him a concrete decision to make.

---

## §1 ⚠ WHAT CHANGED SINCE THE 3 JULY EMAIL — and what NOT to repeat

### 1.1 Corrections (things in your email that are now inaccurate)

| # | Your email said | The truth today | Why it matters |
|---|---|---|---|
| **C1** | "A clean equivalence result … is out of reach at a small number of seeds" | **Only for the Sharpe leg.** The **CVaR-5% (tail) leg has σ_D = 0.0015, ρ = +0.47** → 90% TOST CI half-width ≈ **0.00045 at n=30**. The tail leg is *comfortably conclusive at the floor.* | This is the single biggest correction. You told Ramin equivalence is unreachable; in fact **half of your co-primary headline is already reachable at n=30.** Fix this early or it looks like you don't know your own result. |
| **C2** | "over a family of six tests corrected with Benjamini–Hochberg" | The **decision rule is an intersection–union test (IUT), one-sided, per family, with *no* leg correction** (`per_family_iut_one_sided_no_leg_correction`). BH-over-6 is a **reported sensitivity, not the gate**. | Berger (1982): in an IUT you must reject *every* leg, so the family-wise error is automatically ≤ α — no correction needed. Ramin is a probabilist. He *will* catch "corrected with BH". |
| **C3** | "the deflated Sharpe ratio to account for the search over candidates" (implied primary) | **PBO/CSCV is the PRIMARY overfitting guard**; deflated Sharpe is **secondary** (`primary_overfitting_guard: pbo_cscv`, `deflated_sharpe: secondary`). | Because the trial count `N` is ill-defined under a *guided, sequential* LLM search (each proposal conditions on prior outcomes). PBO is rank-based and needs no trial count. This is a *strength* — say it. |
| **C4** | "a self-hosted open model is the only way to get a genuinely reproducible second author" | **Not self-hosted.** Qwen3-Coder-480B is served via **OpenRouter**; the reproducibility anchor is that the **weights are open** (downloadable forever) + we archive **every prompt/completion** + the **exact served snapshot id**. | Verified live today: served snapshot `qwen/qwen3-coder-480b-a35b-07-25`. Don't overclaim self-hosting — the honest claim is still strong. |
| **C5** | "about eleven days at 30 seeds … three weeks at ~350 … Cloud compute is out on cost" | **Myriad changes everything.** Distinction floor **~0.3–1.3 d**; full 95% study **~1.6–7.1 d**; 99% assurance **~2.1–9.4 d**. | Your entire seed/compute trade-off was framed on laptop timings. It no longer binds. |
| **C6** | "roughly 350 seeds … on the two central arms, controls held at 30" (arm-adaptive) | Now **uniform n across all 12 units** (7 arms + 4 H1 baselines + H3). Tier ladder **[30, 340, 403, 568]**. | Uniform-n kills the asymmetric-power compromise. "350" was just **340 (90% assurance) rounded** for seed-failure buffer. |

### 1.2 Genuinely new since 3 July

1. **UCL Myriad integrated end-to-end** — a full cluster adapter (`src/cluster/`, 10 modules), driver,
   array-job orchestration, effect-blind review gate, crash-resume. 2,095 tests green.
2. **The numeracy-bottleneck hypothesis** (§7) — a *mechanistic explanation for a null*, plus a
   pre-registered sub-experiment that tests it. **This is your strongest new intellectual asset.**
3. **The grade-securing tier ladder** — seeds partition into cumulative, order-only tiers, so the run
   is *complete and bankable at every stop*, and the stop is **exogenous** (throughput/deadline),
   which preserves single-look validity.
4. **k = 3 multi-seed search selection** — built and tested; attacks σ_seed *selection noise at source*
   (Eureka selects on 1 policy; this exceeds it). **Config-gated, currently OFF (default k=1).**
5. **D1 dose-response** — reflection depth {1, 2, 4, 6, 8} at matched budget. The reflection-value
   *curve* is measured nowhere in the Eureka lineage.
6. **The pre-registered "30→50 seeds if σ_D > 0.10" band is dead on arrival** — σ_D = 0.369 fires it,
   and **even n = 50 is insufficient.** ⇒ a dated amendment is *required*. Ramin should know this.

---

## §2 — Where the project actually stands (verified today)

| Item | Status |
|---|---|
| Codebase | **2,095 tests pass** (2,081 not-slow + 14 slow), ruff clean |
| Freeze gate | **21/21 consistency checks GREEN**, canonical hash `1c6b76b6…` |
| Pre-registration | `frozen: false` — **blocked on exactly ONE parameter** |
| `determine_design.py` verdict | **`BLOCKED on: ['n_seeds']`** — everything else FIXED/DECIDED |
| Data | `returns_panel_univ5.parquet`, **5,406 × 963**, SHA-256 verified, Split-C |
| 2nd LLM | Qwen3-Coder-480B via OpenRouter — **live-verified today**, snapshot archived |
| Compute | Myriad code-ready; **SSH key staged; never yet logged in** (VPN pending) |
| Deadline | **1 Sep 2026** (~7.5 weeks) |
| Cost to completion | **$42–81** total API (Opus authoring $33–63; Qwen $1–3) |

**Everything is frozen-ready except the seed count. His answer today is the gate.**

---

## §3 — The design (refresher, precise)

An LLM (**Claude Opus 4.8**) authors **reward-function code** for a **fixed** SAC agent allocating a
long-only portfolio over 30 large-cap US equities + cash. Across arms, **only the feedback block
varies** — the agent, environment, data, and budget are identical. This is the *identification
principle*: only the reward may vary.

**Seven arms:**

| Arm | Feedback shown to the LLM | Role |
|---|---|---|
| `distributional` | CVaR at 25/10/5/1% + `left_tail_mass` + `robust_skew` (6-vector) | **Treatment** |
| `scalar` | one scalar performance number | **Control** |
| `scalar_cvar5` | single-level tail (CVaR-5% only) | Dose control |
| `placebo` | uninformative feedback | Placebo |
| `placebo_shuffled` | same tail numbers, label↔value linkage destroyed | **Separates numbers from meaning** |
| `random_search` | no LLM | Floor |
| `bayes_opt` | no LLM (GP-EI) | Floor |

**Hypotheses:**
- **H1 — LLM vs hand-designed baselines.** *Report-only / descriptive*, subordinate to H2.
- **H2 — distributional vs scalar (HEADLINE).** **Two co-primary intersection–union tests:**
  - `h2_ra` (m=3): **Sharpe**, distributional vs {scalar, placebo, scalar_cvar5}
  - `h2_tail` (m=3): **CVaR-5%**, same three contrasts
  - Frozen family **m = 6**; α one-sided = 0.05; IUT ⇒ **no leg correction**.
- **H3 — iterative vs single-shot** at matched candidate budget.
- **H4 — LLM vs uninformed search** (a) random-search-over-code, (b) Bayesian optimisation.

**Agent settings (identical across arms):** SAC, `MlpPolicy` 256×256, B\* = **200,000 steps**,
buffer 50k, batch 256, lr 3e-4, γ = 0.99, PopArt value-target scale normalisation.
B\* set by a **convergence pilot** (flat within seed noise from ~100k; mildly overfitting by 350k) —
this pre-empts "the null is just under-training."

**State:** 60-day return window, realised vol (20d, 60d), **VIX lagged 1 day**, previous weights.
**Costs:** 10 bps turnover headline; swept {0, 5, 10, 25, 50}.

---

## §4 — The data (be specific; this is where the care went)

- Licensed **Refinitiv/LSEG**, survivorship-free, point-in-time daily panel.
- **5,406 trading days**, Jan 2005 → 30 Jun 2026. Retains full history of the **333 delisted names**.
- Universe rebuilt **as known on each date** (replaying index joins/leaves backwards) — a plain
  snapshot silently returns *today's* index chain = look-ahead.
- **Delisting:** `liquidate_to_cash` (post-delisting return 0). Conservative — *understates* the tail.
  Sensitivity band down to −100% total loss: effect on CVaR-5% ≈ **2%**.
- **Split C:** train 2005-01-01→2016-12-31 · val 2017-01-01→2019-12-31 · test 2020-01-01→2026-06-30.
- **Purge = max(embargo 21, lookback 60) = 60 sessions** at each boundary, so no observation's own
  feature window crosses a split (López de Prado).
- **Three-way decoupling:** tail is **measured on train**, winners **selected on val**, everything
  **scored once on a sealed test**.

**The catch you found (tell this story — it lands):** an earlier panel applied a flat delisting penalty
to all 333 dead names. Wrong twice: it *invented* losses on profitable mergers, and *double-counted*
losses already present in the price series. You recovered each dead name's true final return from the
daily series, showed all 333 were already present, and separately caught the vendor **backfilling a
delisting event three weeks after your data freeze**. Corrected panel differs from the earlier clean
one by **exactly zero cells** over the shared history.

---

## §5 — Statistics & inference (be ready to defend every choice)

| Choice | Justification | Cite |
|---|---|---|
| **Per-seed IQM + paired seed bootstrap** (not seed-averaging) | Averaging N i.i.d.-seed paths shrinks the tested object's variance ~N×, making a per-period bootstrap **anti-conservative by ~√N** | Agarwal et al. 2021 (rliable) |
| **IUT, no leg correction** | Reject the family ⇒ reject *every* leg ⇒ FWE ≤ α automatically | Berger 1982 |
| **TOST equivalence**, SESOI = **0.05** (validation-DSR units) | Reject both one-sided tests; p = **max** of the two | Schuirmann; Lakens 2017 |
| **PBO/CSCV primary**, DSR secondary | Trial count `N` is **ill-defined** under a guided sequential search; PBO is rank-based, trial-count-free | Bailey et al. 2017 |
| **Stationary block bootstrap** | Daily P&L is autocorrelated; size **certified empirically** by `null_calibration` | Politis–Romano 1994 |
| **Romano–Wolf / BH-FDR** | Reported sensitivity across the m=6 family (**not** the gate) | Romano & Wolf 2005 |
| **EVT/GPD (POT) for CVaR-5%, CVaR-1%** | Tail holds only ~75 exceedances; empirical primary for the body | McNeil–Frey |
| **Newey–West HAC** in factor attribution | 1987 estimator + **1994 lag rule** `⌊4(T/100)^{2/9}⌋` (**not** Schwert 1989) | NW 1987/1994 |

**Risk-measure chain (get this exactly right — it's his field):**
Artzner's four axioms → **VaR fails *subadditivity* specifically** → CVaR/ES is coherent →
**ES alone is *not elicitable*** (Gneiting 2011) → but **(VaR, ES) is *jointly* elicitable**
(Fissler–Ziegel 2016) → licenses the **FZ0 strictly consistent score** → Diebold–Mariano-style
**comparative backtest** (Nolde–Ziegel 2017).

**Honesty item you must volunteer:** the fed tail is **endogenous** to the agent — it's fitted on the
*trained policy's own realised returns* under the candidate reward. So H2 compares **two coupled
reward → policy → measurement loops**, not an exogenous risk measurement. *Never say "agent-independent."*
"Critic-agnostic" (architecture-independent) is the correct, defensible phrase.

---

## §6 — THE SEED DECISION (the core of the meeting)

### 6.1 The measured facts

| Quantity | Value | Source |
|---|---|---|
| σ_seed (per-seed SD of test annualised Sharpe, fixed reward) | **0.244** | pilot |
| **σ_D** (SD of per-seed Sharpe **difference**, 15 CRN pairs) | **0.369** | σ_D² = 2σ²(1−ρ) ✓ |
| ρ (CRN pairing correlation, Sharpe) | **−0.141**, n.s. at n=15 (95% CI ≈ [−0.6, +0.4]) | pilot |
| **CVaR-5% leg:** σ_D | **0.0015**, ρ = **+0.47** | pilot |
| SESOI | **0.05** (validation-DSR units) | frozen |
| n at the **point** σ̂_D (SESOI crossing) | **189** | MC tool |

**Why ρ < 0 matters:** normally common random numbers *reduce* difference variance. Here pairing is
mildly **negative**, so it *inflates* it: `Var(D) = 2σ²(1 − ρ)`. Your power-analysis bug was exactly
this — ignoring a negative ρ **understated** σ_D. **But ρ is not significant** (CI spans zero) —
report it as a one-line methods note, **never as mechanism evidence.**

### 6.2 The assurance ladder (χ² upper bound on σ_D, df = 14)

`n(C) = 189 × (σ_up(C) / σ̂_D)²`, with `σ_up = σ̂ · √(14 / χ²_{1−C,14})`

| Assurance | σ_up | factor | **n** | Tier name |
|---|---|---|---|---|
| — | 0.369 (point) | 1.000 | 189 | — |
| 80% | 0.449 | 1.216 | **279** | — |
| **90%** | 0.495 | 1.341 | **340** | ← your email's "≈350" (rounded for seed-failure buffer) |
| **95%** | 0.539 | 1.460 | **403** | **recommended** |
| **99%** | 0.640 | 1.733 | **568** | reachable on Myriad |

**Tier ladder actually implemented:** `[30, 340, 403, 568]` — cumulative, **order-only** (an earlier
tier's seeds are a strict subset; later tiers only *extend*, never re-run). Tier-0 (n=30) is the
**distinction-bankable core**: complete H2 + mechanism + H1 + H3.

### 6.3 The reframe you must land (C1 again — it's the intellectual point)

- **Tail leg (CVaR-5%):** σ_D = 0.0015, ρ = +0.47 → **90% TOST CI half-width ≈ 0.00045 at n = 30.**
  **Conclusive at the floor.**
- **Sharpe leg:** σ_D = 0.369 → at n=30 the CI half-width ≈ **0.111**, more than **2× the SESOI**.
  This leg alone drives the seed count.

⇒ *"The seed count is not buying me the headline. It is buying me a **clean equivalence statement on the
risk-adjusted leg**. The tail leg — the one the treatment is actually built for — is already
conclusive at 30 seeds."*

### 6.4 Wall-clock, at Myriad (this is what dissolves the trade-off)

| Target | Trainings | GPU-h | Cautious (C=12) | **Max (all 38 V100, packed)** |
|---|---|---|---|---|
| **Floor n=30 — complete study** | 1,104 | 644 | 1.3 d | **0.28 d (~7 h)** |
| n=340 (90%) | 4,824 | 2,814 | 5.6 d | ~1.4 d |
| **n=403 (95%)** | 5,580 | 3,254 | 6.5 d | **~1.6 d** |
| n=568 (99%) | 8,130 | 4,743 | 9.4 d | **~2.1 d** |

(Full Stage 1 incl. D1 dose-response = 6,141 trainings / 3,580 GPU-h. Grand total incl. all optional
extensions = 16,391 trainings / 6,934 GPU-h ≈ 2–6 days.)

**Honest caveat:** the packing factor `F` and sustained fair-share concurrency are **measured at G1**,
before the timeline commits. The training count is exact; the parallelism is bracketed.

### 6.5 Your recommendation to him

> **Uniform n = 403 (95% assurance), with the ladder pre-registered to 568 (99%) and the stop
> determined exogenously by measured throughput against the calendar minus a 25% buffer.**

Why this is the *statistically clean* answer:
- Powering on **σ_D (a nuisance parameter) estimated from an effect-blind pilot** is not a forking
  path — no effect estimate is consulted.
- The tiers **partition** the seed set (CRN preserved); every boundary is a **complete uniform-n
  design**; the truncation rule is **exogenous** (throughput/deadline), so the single look stays valid.
- The continuation gate is **effect-blind** — it reads counts and device homogeneity only, never a
  performance statistic.

---

## §7 — The mechanism (your originality) + the numeracy bottleneck

The headline is the **mechanism**, with the H2 performance result as its rigorous backdrop:

> *"Does showing the LLM the downside change the reward **code** it writes?"*

Three sub-questions, four pre-registered instruments (all **report-only**, disjoint from the frozen m=6):
- **SQ1 Responsiveness** — does the authored code track the fed tail signal? (Spearman + bootstrap CI,
  with a `ci_reliable` gate because the code feature is integer-valued.)
- **SQ2 Transmission** — mediation: fed tail (X) → code feature (M) → realised tail (Y);
  bootstrap CI on the indirect effect `a·b` (Preacher–Hayes), with a stability guard on
  `prop_mediated` when the total effect is near zero.
- **SQ3 Specificity** — genuine use vs **surface echo** (AST named-vs-blinded, reward-code distance,
  program taxonomy).
- **Information-utilisation gap** — how much non-redundant signal was **GIVEN** (1 − redundancy of the
  6-vector given the scalar) vs how much the code **USED** (|SQ1 coefficient|).

**Why a null is a *result*, not a failure:** if `a ≈ 0` (the fed signal doesn't move the code), then
`a·b ≈ 0` **for any b** — the causal chain is **severed at link 1**, and the equivalence in Y is
*explained*, not merely observed. That is a **boundary condition**, in exactly the spirit of his
personality-and-risk work.

### 7.1 The numeracy bottleneck — your best new idea

Frontier LLMs **cannot reliably compare close small floats** (≈50–70% accuracy). The fed CVaR values
(e.g. **−0.0577 vs −0.0582**) sit squarely in that failure regime.

> If the channel is silent because the numbers are **illegible**, not because tail information is
> **useless**, then presenting the *same* information in a more legible format (basis points,
> rank/decile framing) should **raise** responsiveness.

That contrast is implemented (`legible_format_responsiveness_differential`): a positive, CI-separated
differential is a **citable mechanism for the null** *and* a concrete scaling hypothesis —
**legibility, not capacity, is the lever.** Supporting literature: close-float comparison failure
(arXiv:2602.07812), NUMCoT (arXiv:2406.02864), tokenizer number-fragmentation (arXiv:2601.14658),
FinVerBench arithmetic gap (arXiv:2605.29586), Bradford-Levy 2026 (JAR).

**This is the thing to sell him.** It converts "my effect was null" into "I found *why*, and it's a
property of how LLMs read numbers."

---

## §8 — Compute: Myriad (status, honest)

- **Believed granted** (you told me so; LSEG licence on UCL systems confirmed). **But you have never
  logged in.** SSH key staged (`~/.ssh/id_ed25519_myriad`), `~/.ssh/config` filled with `ucestes`.
  VPN was blocked by an unrelated laptop antivirus problem — **fixed today.**
- **Hardware:** 74 GPUs — **38 × V100-16G** (E/F), 24 × A100-40 (L), 12 × A100-80 (U/V). Grid Engine
  (SGE), 48 h walltime, array jobs.
- **Stage 1 is V100-only** (device homogeneity — a contrast must never mix GPU models).
- **Key technical finding (measured):** a training is **neither compute- nor env-bound**. The env step
  costs **49 µs = 0.3%** of the 18.2 ms step; the rest is the single-threaded SB3 Python loop (~40%)
  and **two GPU round-trips per step** (~60%, dominated by Windows WDDM submission latency). Hence:
  Linux/V100 ≈ **1.75×** faster (floored by the Python loop); **A100 ≈ V100 per training** (the
  256×256 MLP never touches tensor cores); **packing is the only real throughput lever.**
- **Acknowledgement is mandatory:** *"The author acknowledges the use of the UCL Myriad High
  Performance Computing Facility (Myriad@UCL), and associated support services, in the completion of
  this work."*
- **Possible ask:** an **Additional Resource Request (ARR) → CRAG** (meets monthly, 2nd Tuesday —
  ~14 July / ~11 Aug) for a short priority window (~3,600 GPU-h over 7–10 days on the V100 pool).
  **Requires the supervisor to co-sign.**

---

## §9 — Novelty fence (fresh; re-swept)

| Neighbour | What it does | How you differ |
|---|---|---|
| **GIFT** | LLM-guided portfolio agent | Selects from a **fixed library** of risk rules; changes state *and* reward together; feeds drawdown/generic diagnostics — **never a CVaR vector** |
| **ELfolio** | Evolves LLM-written strategy code | Selects on **scalar Sharpe** — that is *your control arm*, not your treatment |
| **Gallego** | Coins "feedback engineering" | Policy code in **social dilemmas**; no controls, no statistics |
| **Eureka** | LLM reward-code search | Varies the **search**; you hold search fixed and vary **risk content of the feedback**. Also: Eureka selects on **1 policy**; your k=3 IQM selection **exceeds** its rigor |

**The claim, stated safely:** drawdown is *already* fed to such systems, so the contribution is
specifically **feeding a coherent expected-shortfall tail vector to a reward-code author under a
pre-registered, controlled comparison** — always with *"to our knowledge."*

**Proximity to his own work (cite precisely):**
- **Khraishi & Okhrati (2022)** — offline RL / CQL. Your design is *simulated-online off-policy SAC on
  a sealed historical replay*; the relabel→CQL bridge is the honest connection.
- **Hartley, … Okhrati (2025, ACL)** — LLM risk behaviour ("personality-and-risk"). **This is the
  golden neighbour** — asking whether a model *uses* the risk it is shown is the same species of
  intervention.
- ❌ **Do NOT attribute to him:** CVaR elicitability, *Deep Hedging* (that's Buehler et al.),
  "Hedging Beyond the Mean", or Capiński.

---

## §10 — Limitations to volunteer proactively (he rewards this; it's his 5/5)

1. **Fed tail is endogenous** to the agent (two coupled loops). Never "agent-independent."
2. **Search width is limited** — 30 candidates, K = 5 per generation.
3. **Trial count is ill-defined** under guided search ⇒ PBO primary, DSR secondary and disclosed.
4. **CVaR-1% is EVT-extrapolated** from few exceedances → **high-variance, flagged everywhere.**
5. **Annualised Sharpe assumes i.i.d.** (Lo 2002) — reported as a *descriptive point estimate only*;
   all inference runs on the per-seed paired bootstrap of the actual return series.
6. **ρ = −0.141 is not significant** — a methods note, not evidence.
7. **Prototype** (Sonnet, 6 arms, 18 h, $3.17) is **single-seed and directional only** — *no number
   from it enters the dissertation.*
8. **Single universe / single market** (30 US large caps). FTSE replication is optional Stage 2.
9. **The pre-registered "30→50 if σ_D > 0.10" band is unusable** and needs a dated amendment.

---

## §11 — What you need FROM Ramin (ranked)

| # | Ask | Why it's blocking |
|---|---|---|
| **1** | **Seed decision** — endorse uniform **n = 403** with the ladder to 568 | `determine_design` reports **`BLOCKED on: ['n_seeds']`**. Literally the only thing standing between you and the freeze. |
| **2** | **Written sign-off on the research-question pivot** (performance → mechanism) | A **tracked item**. You asked on 3 July; still outstanding. Get it in writing today. |
| **3** | **Approve the seed-band amendment** (the dead "30→50" rule) | Procedural integrity — a pre-registered rule you cannot satisfy must be amended, dated, and disclosed. |
| **4** | **Myriad**: has UCL contacted him? Is the account active? Would he **co-sign an ARR to CRAG**? | You've never logged in. If the account isn't provisioned, that's a multi-day lead time you must know about *now*. |
| **5** | **Which deep analyses to expand** (his "depth beats breadth") | Directly shapes where you spend the remaining 7 weeks. |
| **6** | His **evidential standard for the null** | Determines what you must show to make the null land as a mechanism result rather than a failure. |

---

## §12 — THE QUESTIONS (ask in this order)

**Q1 — Seeds (the freeze gate).**
> "Given Myriad, the seed cost has collapsed from three weeks to about two days, so I can now afford
> 403 seeds — 95% assurance on the χ² upper bound of σ_D — or even 568 for 99%. And since the CVaR leg
> is already conclusive at 30 seeds, the extra seeds are buying a clean **equivalence** statement on
> the *Sharpe* leg specifically. Would you power to 95%, go to 99% since it's nearly free, or hold at
> the 90% figure I originally proposed? And are you comfortable that re-sizing n on σ_D from an
> **effect-blind** pilot is not a forking path?"

*(Why: gets the decision **and** invites him to bless the inferential legitimacy. If he blesses it,
you freeze today.)*

**Q2 — The null as a result.**
> "Would you read a null — the model does not exploit the downside it is shown — as a genuine mechanism
> and boundary-condition result, in the spirit of your personality-and-risk paper? Concretely: I can
> show the chain is severed at link one, that responsiveness `a ≈ 0`, and — this is new — that the fed
> CVaR values sit in the close-small-float regime where LLMs are only 50–70% accurate. I have a
> sub-experiment that re-renders the *same* information in basis points to test whether the bottleneck
> is **legibility rather than capacity**. **What evidence would most convince you this is a real
> failure to use the information rather than an artefact?**"

*(Why: this is the question that most raises your grade. It foregrounds mechanism, cites his work
correctly, and asks him to specify his own evidential bar — which you can then meet.)*

**Q3 — Depth.**
> "You've said depth beats breadth. Of the mechanism instruments — responsiveness, the mediation chain,
> surface-echo-vs-genuine-use, the information-utilisation gap, and the new legibility experiment —
> which would you expand, and is there anything you'd cut?"

**Q4 — Myriad / ARR.**
> "Have you had any request from UCL about my Myriad access? I have the account details but haven't
> authenticated yet. And if free fair-share throughput proves thin, would you be willing to co-sign an
> Additional Resource Request to CRAG for a short priority window — roughly 3,600 GPU-hours over seven
> to ten days?"

**Q5 — Procedural (short).**
> "Two tracked items: your written agreement on the research-question change, and a dated amendment
> retiring the pre-registered '30→50 seeds' rule, which the pilot has made unusable. Can I send both
> for signature today?"

**Q6 — If time allows.**
> "The main body is capped at 10,000 words and I'm currently at ~17,000. My plan is to keep the
> mechanism chapter deep in the body and push the robustness suite into word-excluded appendices.
> Does that match how you'd allocate it?"

---

## §13 — Questions HE is likely to ask → your prepared answers

**"Why is your effect size 0.05?"**
> Pre-registered SESOI in validation-DSR units — the smallest deflated-Sharpe difference that would
> change a practitioner's choice of reward-design procedure. Fixed before any effect was seen.

**"σ_D = 0.369 against a SESOI of 0.05 — isn't the study simply underpowered?"**
> For the Sharpe leg at small n, yes — and that's *itself* a finding: **training-seed randomness
> dominates the feedback-content effect by ~7×**. The tail leg is unaffected (σ_D = 0.0015). At
> n = 403 the 90% TOST CI half-width is ≈ 0.044 even at the 95% upper bound of σ_D, i.e. inside the
> SESOI. The ladder is *constructed* to guarantee that.

**"Why not just use the deflated Sharpe ratio for the search?"**
> Because DSR needs a trial count `N`, and under a **guided, sequential** LLM search each proposal
> conditions on prior outcomes, so `N` is ill-defined. PBO/CSCV is rank-based and needs no `N` — it's
> primary; DSR is reported alongside with the effective-`N` caveat stated.

**"How do you know the null isn't just under-training?"**
> The convergence pilot: held-out performance is flat within seed noise from ~100k steps and mildly
> *overfitting* by 350k. B\* = 200k sits ≥ 2× past the critic knee and below the overfit onset — and
> the same ladder will be re-run on the V100 pool as an independent second confirmation.

**"Isn't your measured tail contaminated by the agent that produced it?"**
> Yes — and I say so explicitly. The estimator is **critic-agnostic** (architecture-independent) but
> **not agent-independent**: it fits the trained policy's own realised returns. H2 therefore compares
> two coupled reward → policy → measurement loops. That is the legitimate object of study; the
> train/val split mitigates selection-overfitting but does not break the endogeneity.

**"You changed your research question."**
> Yes, and it's documented and disclosed. It sharpened from performance to mechanism because the
> feedback content is the only thing that can be varied cleanly with everything else fixed — and a null
> is far more informative as *"where does the channel break?"* than as *"it didn't beat the baseline."*
> I'd like your written agreement on the note.

**"Why not multi-agent / world models / hierarchical / meta-RL?"** *(if he probes ambition)*
> Those live at the **agent-architecture** layer; my contribution lives at the **reward-design** layer.
> They're orthogonal — a fancier agent doesn't deepen the contribution, it adds confounds to a study
> whose whole value is clean identification. My instrument is **architecture-agnostic**, and the natural
> future work is to let it author rewards *for* those learners. Offline RL and risk-sensitive/CVaR — the
> two directions closest to your own work — are already the spine of the design.

---

## §14 — Traps: do NOT say these

- ❌ "Equivalence is out of reach." → **Only for the Sharpe leg.** The tail leg is conclusive at n=30.
- ❌ "Corrected with Benjamini–Hochberg." → The **gate is the IUT, no leg correction**; BH is a sensitivity.
- ❌ "Deflated Sharpe accounts for the search." → **PBO/CSCV is primary**; DSR secondary with the caveat.
- ❌ "Self-hosted Qwen." → **OpenRouter**, open weights, archived snapshot.
- ❌ "Agent-independent tail measurement." → **Critic-agnostic**, *not* agent-independent.
- ❌ "The negative correlation shows the arms interfere." → **ρ is not significant.** Methods note only.
- ❌ Quoting any prototype number as a result. → Single seed, directional, **nothing enters the PDF**.
- ❌ Claiming Myriad is running. → **You have not logged in yet.**
- ❌ Attributing *Deep Hedging* or CVaR-elicitability to Ramin.

---

## §15 — Number cheat-sheet (one glance)

```
DATA        5,406 × 963 · Jan-2005 → Jun-2026 · 333 delisted retained · purge 60 sessions
SPLITS      train 2005–2016 · val 2017–2019 · test 2020–2026-06
AGENT       SAC, MLP 256×256, B* = 200,000 steps, buffer 50k, batch 256, lr 3e-4, γ 0.99
ARMS        7 · frozen testing family m = 6 · two co-primary IUTs (Sharpe m=3, CVaR-5% m=3)
SESOI       0.05 (validation-DSR) · α one-sided 0.05 · IUT ⇒ no leg correction

σ_seed      0.244        σ_D (Sharpe)  0.369   ρ = −0.141 (n.s.)
σ_D (CVaR)  0.0015       ρ = +0.47     → tail leg conclusive at n = 30
n at point σ̂_D  189
LADDER      80%→279 · 90%→340 · 95%→403 · 99%→568      tiers [30, 340, 403, 568]

MYRIAD      74 GPUs (38×V100-16G, 24×A100-40, 12×A100-80) · SGE · Stage 1 = V100-only
WALL-CLOCK  floor 0.3–1.3 d · 95% 1.6–7.1 d · 99% 2.1–9.4 d
TRAININGS   floor 1,104 · n=403 5,580 · Stage-1 total 6,141 (3,580 GPU-h) · grand 16,391
COST        $42–81 total API
STATUS      2,095 tests green · freeze gate 21/21 · hash 1c6b76b6 · BLOCKED on n_seeds only
DEADLINE    1 Sep 2026
```

---

## §16 — Immediately after the meeting

1. Record his seed answer → I run the hash-bound recording → `n_seeds` DECIDED → **you freeze.**
2. Email him the **pivot-disclosure note** + the **seed-band amendment** for written agreement.
3. If he confirms Myriad: connect VPN → key-install → **G0 → build_env → G1** (measures the real
   packing factor `F`, which re-anchors every wall-clock number above).
4. Top up the Anthropic key to ~$70 (currently $5; Stage-1 authoring costs $33–63).
5. Log any steer on "which deep analyses" straight into `docs/PRE_SUBMISSION_CHECKLIST.md`.

---

*Prepared 2026-07-10. All figures re-verified against the live repository today.*
