# DEEP_H4 — exhaustive scrutiny of H4 (LLM-designed reward vs random search + Bayesian optimization)

**Scope.** H4 asks whether the LLM is a *better reward-search procedure than uninformed black-box
optimisation*, at matched search budget, over a shared reward family. It splits into two
pre-registered tests (PREREGISTRATION §1, §3; FINAL_PLAN §H4):

- **H4a** — LLM-designed reward beats **random-search-over-code** (`src/search/random_search.py`).
- **H4b** — LLM-designed reward beats **Bayesian-optimisation-over-template** (`src/search/bayes_opt.py`),
  a fixed six-term linear reward family (`src/baselines/reward_family.py`).

**Author's verdict after reading the code first-hand.** H4 is *partially* defensible but is currently
**framed and configured in a way that an examiner who knows the AutoML / black-box-optimisation
literature can dismantle**. The single biggest problem is **not** the statistics — it is that the three
arms search **three different spaces of different richness**, so a naive "LLM beats search" reading
conflates *search-procedure quality* with *reward-form richness*. The second-biggest problem is that the
two search baselines are **under-powered by construction** (tiny budget, GP/EI warmup, a narrower
grammar for random-search, a frozen-out discrete dimension for BO), which makes a positive H4 look like
it could be **manufactured by crippling the controls**. Both are fixable before freeze, mostly by
**precise claim-scoping and a few config/label corrections** rather than new engineering.

This document is read-only on code. Every code/claim assertion below was verified against the live repo
(file + line cited). Citations are to the local literature cache
(`00_planning/LITERATURE_AND_DEFENSE_COMPANION.md`) and to web sources (listed at the end).

---

## 0. What actually runs (verified, first-hand)

| Element | Where | What it actually is |
|---|---|---|
| H4a random-search **space** | `src/search/random_search.py:91-114` (`_render_source`) | **3-term** code grammar: `a·port_ret − b·var(window=50) − c·cvar_5%(window=50)`, coeffs from a 5-point grid `{0,0.25,0.5,1,2}` (`:59`). **No** log, turnover, drawdown, or vol term. |
| H4b BO **space** | `src/baselines/reward_family.py:21-24`, `config/eureka_loop.yaml:45-51` | **6-term** linear family: `w_return·r + w_log·log1p(r) − w_turnover·turn − w_drawdown·dd − w_cvar·max(0,−CVaR_α) − w_vol·σ`, weights uniform over a frozen box; `cvar_alpha`, `window` **FIXED** (0.05, 20) for the continuous BO box. |
| H4b BO **algorithm** | `src/search/bayes_opt.py:180-286` | scikit-learn **GP + Matérn(ν=2.5) + WhiteKernel**, **Expected-Improvement** (ξ=0.01) maximised over 2000 random candidates; **`n_init=5`** random seed points; GP refit each step with `n_restarts_optimizer=2`. **NOT** TPE; **Optuna is not a dependency** (verified: no `optuna`/`skopt`/`bayesian-optimization` in `pyproject.toml`). |
| LLM **space** | `src/agents/evaluator.py`, the prompt/sandbox path | **Free-form Python** reward code (AST-gated, numpy-only), unconstrained in functional form within the contract. |
| Matched budget | `config/arms.yaml:3` (campaign `matched_budget: 30`); `config/prototype.yaml:11` (prototype 40) | All seven arms evaluate the same number of candidate rewards; the fixed SAC, `train_steps`, and `n_trials` DSR deflation are identical (`src/agents/evaluator.py:60-64`, `assert_fixed_agent_across_arms`). |
| Fitness identity | `src/agents/evaluator.py:39-98` | Search arms and LLM arms call the **identical** `held_out_fitness(val_returns, n_trials)` (validation Deflated Sharpe) on the **identical** train→rollout→select pipeline. This part is clean and is H4's main strength. |
| Seeding | `run_prototype.py:393,418`; `parallel.py:623,647-650` | Both search arms seed from the run seed (reproducible winner). Clean. |

### 0.1 Three config/label defects that MUST be fixed before freeze (they are footguns, not opinions)

1. **`bayesopt_tpe` is a misnomer (HIGH severity for write-up integrity).** `config/eureka_loop.yaml:21`
   labels the BO arm `bayesopt_tpe` with the comment "Optuna TPE, 240 trials". **The wired code is
   GP-EI, not TPE, and there is no Optuna.** `config/arms.yaml:13` and `config/campaign.yaml` correctly
   call it `bayes_opt` (`search: template`). If the dissertation text says "TPE" or "Optuna" anywhere it
   is **factually false and trivially caught** (the supervisor co-authored corpus papers; a method
   mislabel is a credibility hit, CLAUDE.md prime directive 4). **Action: either change the code to real
   Optuna-TPE, or change every label/comment to "GP-EI Bayesian optimisation" and cite Snoek et al.
   2012, not Bergstra 2011.** Recommended: keep GP-EI (it is a legitimate, citable BO; see §5) and fix
   the label. Note also that the `eureka_loop.yaml` budget comment says "240 trials" while the live
   matched budget is 30 (campaign) / 40 (prototype) — another stale number to reconcile.

2. **`reward_family` in `eureka_loop.yaml` advertises a space the BO cannot search (MEDIUM).**
   `config/eureka_loop.yaml:52-53` lists `cvar_alpha_choices: [0.01,0.05,0.10]` and
   `window_choices: [20,60]` "sampled uniformly", and line 40 says *"random_search & bayesopt_tpe draw
   from THIS space only."* In reality (a) the BO box is continuous-only and **fixes** `cvar_alpha=0.05`,
   `window=20` (`reward_family.py:18-19`; `prototype.yaml:84-85`), and (b) random-search does **not** use
   this family at all — it uses the separate 3-term grammar (§0, row 1). The config over-states the
   common space. **Action: rewrite the comment to state exactly which dims each arm searches.**

3. **`config/eureka_loop.yaml:40-44` claims the family "vertices recover the hand-designed canon, making
   H4 a like-for-like search-procedure comparison" — this sentence is half-true and is the crux of §1.**
   It is true the *family* can express canon-like rewards. It is **false** that this makes the
   *three-way* H4 comparison like-for-like, because random-search and the LLM are **not** searching this
   family. Keep the sentence only for H4b-vs-the-family; do not let it license H4 as a whole.

---

## 1. THE LOAD-BEARING CRITIQUE — "like-for-like" vs "richer-space" (SEVERITY: CRITICAL)

This is the critique most likely to sink H4 in marking, and it has two layers.

### 1.1 The LLM searches a strictly richer space than either baseline

The LLM authors **free-form code**; random-search draws from a **3-term** grammar; BO tunes a **6-term
linear** family with two dims frozen. These are nested by richness:

```
{3-term random grammar}  ⊂  {6-term linear family}  ⊊  {free-form LLM code}
        (H4a space)              (H4b space)                  (LLM space)
```

(The ⊂ is not literal — the random grammar's CVaR uses `np.quantile`/window=50 while the family uses
`np.sort`/`np.ceil`/window=20, so they are not exactly nested implementations — but in *expressive
class* the ordering holds: linear-in-more-primitives dominates linear-in-three, and arbitrary code
dominates any fixed linear form.)

**Consequence.** If the LLM wins H4, the win is **confounded** between two distinct causes:

- **(C-procedure)** the LLM is a smarter *search procedure* over a *given* space; and
- **(C-richness)** the LLM is *allowed a richer hypothesis space* (it can write `tanh`, ratios,
  regime switches, Sortino-style asymmetric penalties, state machines — none reachable by a 3- or 6-term
  linear combination).

A positive H4 as currently wired supports **(C-richness ∨ C-procedure)** but **cannot separate them**.
That is a weaker and different claim than the prose implies. An examiner will say: *"You did not show the
LLM is a better optimiser; you showed that a richer reward language helps — which is unsurprising and is
not about the LLM's intelligence at all. A random sampler over your free-form grammar might do as well."*

This is exactly the failure mode the FunSearch/Eureka literature is careful about: **the contribution of
an LLM-search method must be isolated from the contribution of the search *space*.** Eureka itself runs a
"sampling more initial rewards does not match iteration" ablation precisely to show the *procedure* (not
just the space) matters ([Eureka, Ma et al. 2024](https://arxiv.org/abs/2310.12931)). H4 has no
equivalent space-controlled comparison.

### 1.2 What each H4 test legitimately licenses (state this PRECISELY in the dissertation)

| Test | What it CAN claim | What it CANNOT claim |
|---|---|---|
| **H4a** (vs random-over-code) | "Against an **uninformed random sampler over a comparable code grammar**, LLM proposals at matched budget yield higher OOS Deflated Sharpe." Because both produce *code*, this is the closest thing to a procedure-only comparison — **but only if the grammars are comparable** (currently they are not; the random grammar is poorer, §2). | It cannot claim parity of search space with the LLM (the LLM's free-form space is richer than the 3-term grammar). So even H4a is partly a richness comparison until the grammar is widened. |
| **H4b** (vs BO-over-family) | "Against **Bayesian optimisation of a fixed expressive linear reward family**, the LLM's free-form rewards beat the best tuned family member at matched budget." This is a **richness + procedure** comparison and is *legitimate and interesting* — **provided you frame it as "free-form code beats parameterised search," not "the LLM searches the same space better."** | It is **not** like-for-like search-procedure: BO is denied the LLM's functional freedom. Do not claim "the LLM is a better optimiser than BO." Claim "the LLM's open-ended reward language beats BO over the best fixed linear family we could write." |

**Recommended precise wording (bankable):**

> *H4 tests whether an LLM reward-designer, at matched candidate budget, produces rewards with higher
> out-of-sample risk-adjusted performance than two non-LLM search controls: (a) random search over a
> comparable risk-aware code grammar, and (b) Bayesian optimisation of a fixed six-term linear reward
> family whose vertices recover the hand-designed canon. H4a isolates **proposal quality** at comparable
> expressive power; H4b isolates the value of an **open-ended reward language** against tuning a fixed
> parametric one. We do **not** claim the LLM is a superior black-box optimiser over an identical search
> space; the LLM's hypothesis space is deliberately richer, and that richness is part of what H4b
> measures.*

This converts the confound from a hidden weakness into an **explicitly scoped, defensible** dual claim.

---

## 2. Is the random-search baseline (H4a) a FAIR control? (SEVERITY: HIGH)

The decisive AutoML result here is **Bergstra & Bengio (2012), "Random Search for Hyper-Parameter
Optimization," JMLR 13:281-305**: random search is a *strong* baseline, often matching or beating grid
search and competitive with early model-based methods, **especially in low effective dimensionality**
([JMLR](https://jmlr.org/papers/v13/bergstra12a.html)). The corollary that matters for H4: *if you want a
positive H4a to be credible, random search must be given a genuinely fair shot* — a weak random baseline
makes H4a **trivially true and therefore uninformative** (over-claiming).

Three concrete fairness defects in the current random-search arm:

1. **The grammar is poorer than both the BO family and the LLM space (HIGH).** Random-search can only
   express `return − var − cvar` (3 terms), so it **cannot even represent** a turnover-penalised,
   drawdown-aware, or log-growth reward — forms the LLM *and* the BO family can. So H4a is biased toward
   the LLM by a **space handicap on the control**, not (only) by proposal quality. This makes H4a's
   "isolates search quality" docstring (`random_search.py:8-9`) **false as written** — it currently
   isolates *space* as much as *search*. **Action (highest priority for H4a): widen the random grammar to
   draw from the SAME six primitives as the BO family** (return, log, turnover, drawdown, cvar, vol), so
   H4a and H4b share a space and H4a becomes a true procedure-only control. This is a small, pre-freeze
   change to `_render_source` + the grid; it is the single most important H4 hardening.

2. **Budget = 30 is small for a fair random shot in a richer grammar (MEDIUM).** Bergstra-Bengio's random
   search is strong but its strength grows with draws; 30 uniform draws over a widened 6-coeff grid is
   thin. The mitigant is that the *effective* dimensionality is low (a few coefficients dominate), which
   is exactly the regime where random search needs *fewer* draws (Bergstra-Bengio). Still, **report H4a
   with an explicit budget caveat** and, if compute allows, a sensitivity at a larger random budget on
   the development split (see §6). Note the budget is genuinely matched (the LLM also gets 30), so this is
   a *power* caveat, not an *unfairness*: a null H4a at 30 is honest; a *positive* H4a at 30 needs the
   widened grammar (defect 1) to be defensible.

3. **The grid is coarse and non-negative-only (LOW-MEDIUM).** Coeffs ∈ `{0,0.25,0.5,1,2}` and all
   penalties are sign-fixed. That matches the LLM's risk-aware intent and the family's `[0,·]` boxes, so
   it is defensible, but state it: random-search is a *risk-aware* random baseline, not an unconstrained
   one. (This is fine and arguably *favourable* to the control — it bakes in domain priors the LLM also
   has — but it should be disclosed.)

**Net:** H4a is salvageable into a genuinely fair, citable control, but **only after widening the
grammar to the BO family's six primitives.** As-is, a positive H4a is over-claimed.

---

## 3. Is the Bayesian-optimisation baseline (H4b) well-configured, or crippled? (SEVERITY: HIGH)

A crippled BO makes H4b trivially true → over-claiming. Audit of the actual GP-EI config
(`src/search/bayes_opt.py`):

| BO design choice | Value (verified) | Assessment |
|---|---|---|
| Surrogate | GP, `ConstantKernel × Matérn(ν=2.5) + WhiteKernel`, `normalize_y=True`, `n_restarts_optimizer=2` (`:246-254,263-268`) | **Reasonable and standard** (Matérn-2.5 is the Snoek et al. 2012 default; WhiteKernel models the SAC training noise — important, since the same coeffs at the same seed are deterministic here but across the noisy fitness it matters). Defensible. |
| Acquisition | Expected Improvement, ξ=0.01, argmax over 2000 uniform candidates (`:257,271-273`) | **Standard.** EI is the canonical BO acquisition. The 2000-point random inner optimisation is crude vs L-BFGS multi-start but adequate for a 6-D box. Defensible. |
| Init | `n_init=5` random seed points (`:184,227`) | **This is the load-bearing BO fairness knob.** Of a 30-budget, 5 random + 25 GP-guided. A GP on 5 points in 6-D is **barely identified** (the length-scales are nearly unconstrained early), so the first several "BO-guided" steps are little better than random. Compare: **Optuna's TPE default warmup is `n_startup_trials=10`** ([Optuna docs](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html)). With budget 30, the *fraction* of informed steps is what matters: `n_init=5` → 25/30 informed is actually *generous* to BO (more informed steps than TPE's default would give). So BO is **not crippled on warmup** — if anything its warmup is favourable. **Keep `n_init` ≈ 5-8 and state it; do not raise it past ~10 or BO loses too many informed steps at budget 30.** |
| Discrete dims frozen | `cvar_alpha=0.05`, `window=20` fixed; BO searches only the 6 weights (`reward_family.py:18-19`) | **MEDIUM unfairness, but it cuts AGAINST the LLM-favouring direction in a subtle way.** Freezing 2 dims makes BO's job *easier* (6-D not 8-D), so it does **not** cripple BO — it *helps* it (smaller space, same budget). BUT it means the **BO family cannot match a reward that needs `window=60` or `cvar_alpha=0.01`**, whereas the LLM can choose any window inline. So the freeze handicaps the *family's expressiveness*, not BO's *search*. Net effect on H4b: ambiguous; disclose it. The honest framing is "BO over the 6-weight slice of the family at fixed (α=0.05, win=20)." |
| Budget | 30 (campaign) | See §3.1. |
| Surrogate noise | `WhiteKernel(1e-5, [1e-10,1e-1])` (`:253`) | Good — without it the GP would interpolate noisy SAC fitness and over-trust spurious peaks. Shows the BO was built with care, which *helps* H4b's credibility (you cannot be accused of a strawman GP). |

### 3.1 The budget question for BO (the deepest BO-specific threat)

The literature is two-sided and you must cite both:
- **Pro-BO:** GP-BO can beat random search even with **few** evaluations on low-dimensional smooth
  objectives ([Bayesian optimization for computationally extensive distributions, PMC5837188](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5837188/)).
  So 30 is *not* obviously too few for a 6-D box — BO should plausibly beat random *within the family*.
- **Anti-BO (the threat to "BO is a fair control"):** BO/GP methods "usually work well only when provided
  with sufficient data," and **specialised low-budget methods (e.g. TPE) are proposed precisely because
  GP-BO struggles in tight budgets** ([Meta-Surrogate Benchmarking, arXiv:1905.12982];
  [low-budget BBO challenge, arXiv:2012.10335]). With only 5 init points the GP's hyper-parameters are
  poorly estimated, so early "guided" picks are near-random.

**The unit test even enshrines the pro-BO claim:** `tests/test_search.py:173-199`
(`test_bayes_opt_beats_random_on_average`) asserts GP-EI beats matched-budget random *on a smooth concave
toy*. That is reassuring that the BO is not broken, **but a smooth 2-D concave toy is the friendliest
possible case** — it does NOT certify BO is competitive on the **noisy, possibly-multimodal, 6-D**
real fitness. Do not cite that test as evidence BO is a strong control on the real problem.

**Recommended hardening for H4b's BO-fairness (in priority order):** see §6 items B1-B3. The cheapest
high-value one: **add an in-family random-search control** (`random_search_over_template` already exists,
`bayes_opt.py:126-177`, and is currently test-only) **as a reported reference**, so the dissertation can
show *whether BO actually beat random within the family*. If BO ≈ random in-family at budget 30, then H4b
is really "LLM vs random-over-family," and the GP adds nothing — better to know and disclose that than to
be asked it in absentia.

---

## 4. Matched budget, selection, and statistics (SEVERITY: MEDIUM — mostly clean)

- **Matched compute is real and verified.** All arms evaluate the same candidate count; the fixed SAC,
  `train_steps`, `n_trials` DSR deflation, env, panel, and windows are identical
  (`evaluator.py`; `assert_fixed_agent_across_arms`, `factory.py:251-331`). The matched unit is
  **candidate count**, i.e. number of full SAC trainings — the right unit (LLM tokens are off-GPU and
  free; `CAMPAIGN_DEEP_RESEARCH_FINDINGS_2026-06-21.md:134`). **This is H4's strongest leg — lean on it.**
- **One real asymmetry in the budget accounting (LOW-MEDIUM):** random-search and BO **only ever
  consume budget on candidates that pass the gate / are in-box**, and `random_search_over_code`
  *re-samples* on gate failure so it always lands exactly `budget` *valid* candidates
  (`random_search.py:201-233`). The LLM arm, by contrast, **burns budget on gate-failed candidates**
  (the LLM can emit invalid code; `parallel.py:569` increments `failed`). So at matched *nominal* budget,
  the LLM may evaluate **fewer valid** rewards than the search arms. **Direction: this handicaps the LLM,
  so it is conservative for a positive H4** — but it must be **disclosed and quantified** (report
  per-arm valid-candidate counts; the prototype already records them — distributional had 39 vs 40 for
  the search arms, `outputs/prototype/analysis_report.md:6-13`). If H4 is *null*, this asymmetry is a
  confound you must address; if H4 is *positive*, note it favours the null (strengthens the result).
- **Selection is reward-unit-invariant (clean).** Winner = validation Deflated Sharpe on realized
  returns, independent of the candidate reward's own scale (PREREGISTRATION §5), so a search reward
  cannot "win" by inflating its own reward magnitude. Good.
- **Deflated-Sharpe trial count (LOW).** `n_trials` = per-arm candidate count (30/40) is used for the
  expected-max correction uniformly across arms (`run_prototype.py:380,408`). For *guided* search (BO,
  LLM) the effective number of independent trials is **less** than the nominal count (PREREGISTRATION §10
  already flags "effective trial count ill-defined under guided search" and makes **PBO/CSCV primary, DSR
  secondary**). This is handled correctly at the framework level. For H4 specifically, note PBO is the
  primary overfitting guard and is computed per-arm from the per-candidate val-return vectors that all
  arms (incl. search) archive (`evaluator.py:39-64`).
- **H4 is NOT in the frozen m=6 multiple-testing family.** The frozen family (PREREGISTRATION §10, R13)
  is the three H2 contrasts × {Sharpe, CVaR}. **H4a/H4b are separate tests and are not BH-corrected
  within that family.** This is defensible (H4 is a different question) **but you must state H4's own
  multiplicity**: it is 2 tests (H4a, H4b) on the headline metric; apply at least a Holm/Bonferroni over
  those 2, or report them as the two pre-registered comparisons they are. Do **not** silently leave H4
  uncorrected and unmentioned — that is the kind of selective-reporting gap an examiner probes.

---

## 5. Literature grounding (precise; for the Methods + Results + Defence)

**Random search as the H4a control:**
- **Bergstra & Bengio (2012)**, *Random Search for Hyper-Parameter Optimization*, JMLR 13:281-305.
  Random search is a strong, theoretically-motivated baseline; dominates grid search; competitive in low
  effective dimensionality. **Use to justify *why* random-over-code is the right H4a control and to set
  the bar a positive H4a must clear.** ([JMLR](https://jmlr.org/papers/v13/bergstra12a.html))

**Bayesian optimisation as the H4b control (NB: cite the method you actually run — GP-EI, not TPE):**
- **Snoek, Larochelle & Adams (2012)**, *Practical Bayesian Optimization of Machine Learning Algorithms*,
  NeurIPS. The GP-EI-with-Matérn recipe your `bayes_opt.py` implements. Already in the cache as the
  designated "BO baseline" (`LITERATURE_AND_DEFENSE_COMPANION.md:152`, "Snoek/Shahriari (BO baseline)").
  **This is your H4b method citation.**
- **Shahriari et al. (2016)**, *Taking the Human Out of the Loop: A Review of Bayesian Optimization*,
  Proc. IEEE. The survey; cite for EI/acquisition + the small-budget caveat. (Cache: same line.)
- **Bergstra et al. (2011)**, *Algorithms for Hyper-Parameter Optimization*, NeurIPS — **the TPE paper**.
  Cite **only if** you switch the code to real TPE. Otherwise do **not** cite it as your method; the code
  is GP-EI. (The `eureka_loop.yaml` "bayesopt_tpe" label currently mis-points here — see §0.1.1.)
- **Small-budget BO is contested:** specialised low-budget methods (TPE) exist *because* GP-BO can
  struggle with few evaluations. Cite to pre-empt "your BO had too few trials": you can argue *either*
  (a) 6-D is low enough that GP-BO is fine at 30 (Snoek), *or* (b) you add the in-family random control
  to show empirically whether BO's surrogate helped (§6 B2). ([Meta-Surrogate, arXiv:1905.12982](https://arxiv.org/pdf/1905.12982);
  [low-budget BBO, arXiv:2012.10335](https://arxiv.org/pdf/2012.10335))

**LLM-as-optimiser / program-search (the framing + the adversarial citations):**
- **Eureka (Ma et al., ICLR 2024)**, arXiv:2310.12931. The machinery H4 instantiates; its "no reward
  reflection" and "sampling more does not match iteration" ablations are the *template* for isolating
  procedure from space — **and the precedent that an LLM-reward method must beat both human and
  non-iterative controls.** ([arXiv](https://arxiv.org/abs/2310.12931)) (Cache: §2.1, Tier 1.)
- **FunSearch (Romera-Paredes et al., Nature 2024)**, 625:468-475. LLM + evaluator evolutionary *program*
  search; **the closest precedent for "LLM searches function space."** Its discipline — score against
  strong known baselines, maintain diversity to avoid local optima — is the standard H4 is held to.
  ([Nature](https://www.nature.com/articles/s41586-023-06924-6)) (Cache: Tier 2, FunSearch/OPRO.)
- **OPRO (Yang et al., ICLR 2024)**, arXiv:2309.03409 — *LLMs as Optimizers*. The canonical "LLM as
  black-box optimiser" reference. (Cache: Tier 2.)
- **ADVERSARIAL — "Revisiting OPRO: The Limitations of Small-Scale LLMs as Optimizers" (Zhang et al.,
  ACL Findings 2024)**, arXiv:2405.10276, **AND** the broader finding that **heuristic/classical
  algorithms start to outperform LLM optimisers as problem dimension grows, with LLM-optimiser evidence
  concentrated at D<10** ([survey, arXiv:2509.08269]). **This is the single most dangerous citation an
  examiner can bring to H4** — it is the published basis for "the LLM is not actually a better optimiser
  than random/BO; it only looks that way in tiny, low-dimensional, in-distribution settings." **Pre-empt
  it explicitly**: your reward-coefficient space is exactly the low-D regime where the gap is smallest, so
  a *positive* H4 here is a *conservative* place to find an LLM edge (if anything the literature predicts
  the edge should be *hardest* to find here, making a positive result more, not less, notable); and your
  claim is scoped to *reward design with a financial fitness*, not general-purpose optimisation.
  ([Revisiting OPRO](https://arxiv.org/abs/2405.10276))
- **AlphaEvolve / LLM-evolutionary search (2025)** — position as *future work* (richer evolutionary
  operators over the reward-code space); your critical-audit register already rejects QD/AlphaEvolve for
  the campaign and parks them as future work — keep that, and cite the line as the natural extension of
  H4 (LLM-as-mutation-operator vs random mutation). Do not claim to implement it.

**Reward-hacking caveat (needed because H4 is "let a search procedure write the reward"):**
- **Skalse et al. (2022)** reward hacking; **Hadfield-Menell et al. (2017)** Inverse Reward Design;
  **Ng, Harada & Russell (1999)** reward shaping invariance. (Cache: Tier 1/2.) Relevant to H4 because a
  *search* procedure (random/BO) optimising a proxy is the textbook reward-hacking setup; your
  reward-unit-invariant DSR selection (§4) is the defence and should be cited alongside these.

---

## 6. PRIORITISED pre-freeze hardening (concrete, mostly config/label + framing)

Ranked by (impact on defensibility) × (1/cost). **A-items are nearly free and should all be done.**

### A. Free / near-free — DO ALL OF THESE BEFORE FREEZE
- **A1 (CRITICAL, framing).** Adopt the **precise dual claim** from §1.2 verbatim in the hypothesis
  statement and Methods. State explicitly that H4 does **not** assert "LLM is a better optimiser over an
  identical space"; H4a ≈ procedure-at-comparable-richness, H4b = open-ended-language-vs-fixed-family.
  This alone neutralises the §1 critique.
- **A2 (HIGH, integrity).** Fix the **`bayesopt_tpe` mislabel** and the "Optuna/240 trials" comments in
  `config/eureka_loop.yaml` (→ "GP-EI Bayesian optimisation; matched budget 30"). Ensure **no "TPE" or
  "Optuna" string survives** in any doc/figure/caption. Cite **Snoek 2012**, not Bergstra 2011, for H4b.
- **A3 (HIGH).** Rewrite the misleading **docstrings/config comments** that claim H4 is "like-for-like"
  and that random-search "isolates search quality": (`random_search.py:8-9`, `reward_family.py:5-7`,
  `eureka_loop.yaml:40-44,52-53`). Make them say exactly which space each arm searches. (Read-only task
  for me; these are the edits the build agent should make.)
- **A4 (MEDIUM).** **Report per-arm valid-candidate counts** and disclose the LLM-pays-for-gate-failures
  asymmetry (§4); note it is conservative for a positive H4.
- **A5 (MEDIUM).** State **H4's own multiplicity** (2 pre-registered tests) and apply Holm/Bonferroni
  over {H4a, H4b}; record it in the analysis plan so H4 is not silently uncorrected.

### B. Cheap engineering (small, pre-freeze; each turns a likely examiner question into a reported number)
- **B1 (HIGHEST engineering value — makes H4a a true control).** **Widen the random-search grammar to the
  same six primitives as the BO family** (return, log, turnover, drawdown, cvar, vol), so H4a and H4b
  share a space and H4a becomes procedure-only at comparable richness. ~20-line change to
  `_render_source` + grid; re-run the search leg (search budget unchanged → matched compute intact). This
  removes the §2.1 space-handicap that currently makes a positive H4a over-claimed.
- **B2 (HIGH — certifies BO is a fair control).** **Promote `random_search_over_template` to a reported
  reference arm** (it already exists, `bayes_opt.py:126-177`): run random sampling over the **same 6-term
  family** at the same budget and report it next to BO. This answers "did your GP surrogate actually beat
  random within the family at budget 30?" empirically. If BO ≈ in-family-random, disclose that the GP
  adds little at this budget (honest, and still leaves H4b = "LLM-code vs best-tuned-family"). This is the
  most surgical fix to the §3.1 small-budget-BO threat.
- **B3 (MEDIUM).** If feasible on the dev split, run a **budget-sensitivity** point for both search arms
  at a larger budget (e.g. 100) **report-only on development** (never re-selecting; never touching test),
  to show the H4 gap is not an artefact of the tight 30. Pre-register it as a robustness check.
- **B4 (OPTIONAL).** If you would rather the BO be unimpeachably "standard," swap GP-EI for **real
  Optuna-TPE** and *then* the `bayesopt_tpe` name + a Bergstra-2011 cite become correct. Higher cost (new
  dep, re-validation) and **not recommended** — GP-EI is already a citable, well-built BO; A2 (fix the
  label) is the cheaper route to integrity.

### C. Write-up framing (the bankable-null + the strongest positive)
- **C1.** Lead H4 with the **matched-compute** strength and the **reward-unit-invariant selection**
  (the two things the controls cannot attack).
- **C2.** Use the **prototype directional signal honestly**: in the prototype, random_search (winner DSR
  +0.0518, IQM +0.00274) and bayes_opt (winner +0.0198, IQM +0.00215) were **competitive with the LLM
  arms** (scalar winner +0.110, distributional winner +0.060;
  `outputs/prototype/analysis_report.md:6-13`) — i.e. **the prototype did NOT show a clean LLM>search
  gap**; if anything random-search was a *strong* baseline, exactly as Bergstra-Bengio predicts. **Frame
  this as evidence your controls are NOT crippled** (the opposite of over-claiming), and let the campaign
  (Opus 4.8, 30 seeds-on-winners, sealed test) be the actual test. **Do not** present the prototype as
  positive H4.

---

## 7. The STRONGEST defensible H4 framing (use this)

> **H4 (final framing).** At a candidate budget matched to the LLM arms (the same number of full SAC
> trainings), and with winners selected by a reward-unit-invariant validation Deflated Sharpe, we compare
> the LLM reward-designer against two non-LLM search controls: **(H4a)** random search over a risk-aware
> reward *code* grammar built from the same six primitives as the parametric family, isolating *proposal
> quality at comparable expressive power*; and **(H4b)** GP-based Bayesian optimisation (Matérn-EI; Snoek
> et al. 2012) of a fixed six-term linear reward family whose vertices recover the hand-designed canon,
> isolating the value of an *open-ended reward language* against tuning a fixed parametric one. We report
> an in-family random-search reference to certify the BO surrogate is a fair control at this budget. We do
> **not** claim the LLM is a superior black-box optimiser over an identical search space — its hypothesis
> space is deliberately richer, and quantifying the benefit of that richness is part of H4b. Random search
> is a deliberately strong baseline (Bergstra & Bengio 2012); the literature finds classical search often
> matches LLM optimisers in exactly this low-dimensional regime (Revisiting OPRO 2024), so any LLM edge we
> find here is a conservative lower bound, and a null is a substantive, pre-registered finding.

---

## 8. The bankable NULL statement (write this now; it is grade-safe regardless of outcome)

> **If H4 returns null** (the LLM does not beat random-over-code and/or BO-over-family at matched budget):
> this is a **clean, pre-registered, and informative** result. It states that, for risk-sensitive
> portfolio reward design in a low-dimensional reward space, *intelligent* LLM proposal confers no
> out-of-sample advantage over uninformed search at equal compute — consistent with the AutoML evidence
> that random search is a strong baseline (Bergstra-Bengio 2012) and that LLM optimisers do not reliably
> beat classical search at low dimension (Revisiting OPRO 2024). It **does not** undercut the headline H2
> (which is about the *feedback channel* to a fixed designer, not about beating search) — H4 and H2 are
> orthogonal. The contribution survives a null H4 intact; H4 is a *scope-defining* control, and reporting
> its honest result (with PBO as the primary overfitting guard, the matched-budget proof, and the
> disclosed valid-candidate asymmetry) is exactly the pre-registration discipline the dissertation is
> graded on. **A credible null here is worth more than a fragile, over-claimed positive.**

---

## 9. Severity-ranked threat register (one-glance summary)

| # | Threat | Severity | Status / fix |
|---|---|---|---|
| T1 | "LLM beats search" conflates **richer space** with **better procedure** (free-form vs 3-/6-term) | **CRITICAL** | Reframe (A1); widen random grammar (B1). Not a defect once scoped. |
| T2 | Random-search grammar (3-term) **poorer** than BO family & LLM → H4a biased toward LLM | **HIGH** | B1 (widen to 6 primitives) — do before freeze. |
| T3 | `bayesopt_tpe`/"Optuna"/"240 trials" **mislabels** — code is GP-EI, budget 30 | **HIGH** (integrity) | A2 — fix all labels; cite Snoek not Bergstra-2011. |
| T4 | Small-budget BO (n=30, n_init=5) may add nothing over random-in-family → H4b "BO control" attackable | **HIGH** | B2 (report in-family random); §3.1 framing; cite both sides. |
| T5 | BO **freezes** cvar_alpha/window → family less expressive than the LLM's inline choice | **MEDIUM** | Disclose; frame H4b as "6-weight slice at α=0.05,win=20". |
| T6 | LLM **pays budget for gate failures**, search arms re-sample → fewer valid LLM candidates | **MEDIUM** | A4 — report counts; note it is conservative for positive H4. |
| T7 | H4 **not in** the frozen m=6 family; its own 2-test multiplicity unstated | **MEDIUM** | A5 — Holm over {H4a,H4b}; record in plan. |
| T8 | DSR effective-trial count ill-defined under guided search | **LOW** (handled) | PBO primary (PREREGISTRATION §10) — already correct. |
| T9 | Coarse non-negative random grid; risk-aware-only | **LOW** | Disclose as a risk-aware (not unconstrained) random baseline. |
| T10 | Config over-states the "common space" (`eureka_loop.yaml:40,52-53`) | **LOW-MED** | A3 — fix comments. |

---

### Sources (web)
- Bergstra & Bengio 2012, Random Search for Hyper-Parameter Optimization — https://jmlr.org/papers/v13/bergstra12a.html
- Optuna TPESampler (`n_startup_trials` default 10) — https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html
- Snoek/Shahriari BO context; small-budget BO is contested — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5837188/ ; https://arxiv.org/pdf/1905.12982 ; https://arxiv.org/pdf/2012.10335
- Eureka, Ma et al. ICLR 2024 — https://arxiv.org/abs/2310.12931
- FunSearch, Romera-Paredes et al. Nature 2024 — https://www.nature.com/articles/s41586-023-06924-6
- OPRO, Yang et al. ICLR 2024 — https://arxiv.org/abs/2309.03409
- Revisiting OPRO (limitations of LLM optimisers; classical methods overtake as dimension grows) — https://arxiv.org/abs/2405.10276
- Survey: LLMs for evolutionary optimization (LLM-optimiser evidence concentrated at low D) — https://arxiv.org/pdf/2509.08269
