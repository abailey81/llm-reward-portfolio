# DEEP_H1 — exhaustive scrutiny of H1 ("beat the human")

**Status:** read-only analysis dossier (no code edited). Prepared as a HARSH reward-design +
multiple-comparison-statistics reviewer making H1 bulletproof and the strongest *defensible* version.
**Date:** 2026-06-25. **Repo:** `llm-reward-portfolio`. **Grade context:** PDF-only, NO viva
(supervisor Dr Okhrati; corpus citations checked). A clean, pre-registered null is bankable — the job
here is to make the H1 *claim* survive a referee, whichever way it resolves.

**Scope note (as instructed):** I analyze the H1 **design / science**, not the in-flight wiring. An H1
agent has concurrently added the baseline TEST stage (`run_campaign.run_baselines`,
`evaluate_baselines_on_test`, `_baseline_reward_builder`) and the Eureka metric
(`analyze_campaign.beat_human_baseline`, `EUREKA_BEAT_FRACTION=0.83`, `EUREKA_NORM_IMPROVEMENT=0.52`).
I read those first-hand to know *what is being computed*, but the findings below are about the H1
hypothesis, the reference, the fairness handicap, the baseline strength, and the success metric —
design decisions for the user to ratify at freeze, not the wiring code.

---

## 0. What H1 actually is (verified against the frozen record)

**PREREGISTRATION.md §1 (the only place H1 is frozen):**
> **H1 — LLM vs hand-designed.** H0: median OOS risk-adjusted performance of LLM-designed rewards ≤
> the best hand-designed baseline (raw return; return−variance; return−CVaR; differential Sharpe).

The **four** frozen baselines are `config/campaign.yaml: h1_baselines = [raw_return,
return_minus_variance, return_minus_cvar, differential_sharpe]`, exactly the §1 list and a subset of the
9-strong secondary panel in `config/eureka_loop.yaml: baseline_rewards` / PREREGISTRATION §9. The
reference is the **MAX** over those four (the "best of the hand-designed baselines"). All four are real
keys in `src/baselines/rewards.py::REWARD_CANON` and pass `tests/test_baselines.py` first-hand
(contract + the exact `differential_sharpe` A/B/η sequence).

**The comparison the code implements** (`beat_human_baseline`, read first-hand): per frozen-winner test
seed, take the LLM winner's annualised test Sharpe; the "human bar" is the baseline with the greatest
**median** per-seed test Sharpe; report (i) `beat_fraction` = fraction of LLM per-seed Sharpes >
best-baseline median, (ii) `norm_improvement` = `(median_LLM − best_median)/|best_median|`, (iii) a
flagged-secondary `beat_fraction_paired` (per-seed-index), and (iv) a DSR side: median-per-seed winner
DSR deflated by `winner_n_trials` (the search multiplicity, e.g. 30) vs each baseline DSR deflated by
**N=1**. The asymmetric deflation is the FAIRNESS handicap analysed in §3.

---

## 1. CITATION-INTEGRITY DEFECTS (fix before freeze — these are the cheapest wins and a no-viva grade is citation-sensitive)

### C-1 [SEVERITY: HIGH — wrong section reference, repeated]  "PREREGISTRATION §18-19" does not exist.
The code and configs cite H1 to **"PREREGISTRATION §18-19"** in **≥6 places**:
`scripts/analyze_campaign.py` L1549, L1741-1745, L1779, L1924, L1936; `config/campaign.yaml` L39, L43;
`config/eureka_loop.yaml` (header). **PREREGISTRATION.md has only 12 numbered sections** (verified:
`## 1.`…`## 12.`, then `### Freeze record`, `### Amendment record`). **H1 is in §1; the hand-reward
panel is in §9.** There is no §18 or §19 anywhere. This is a dangling cross-reference that a careful
reader (or the supervisor, who co-authored two corpus papers) will catch. **Fix:** replace every
"§18-19" with "§1 (H1) / §9 (hand-reward panel)". This is a string fix, but it is in the frozen artifact
family, so it must be a dated amendment, not a silent edit.

### C-2 [SEVERITY: HIGH — wrong Eureka formula]  The "+52% normalised improvement" formula in the code/docs is NOT Eureka's.
`docs/CAMPAIGN_benchmarks.md` §2b and `beat_human_baseline` define the normalised improvement as
**`(LLM − best_hand)/|best_hand|`** and call it "the Eureka normalised improvement." **That is not how
Eureka defines it.** Verified first-hand from Ma et al. (ICLR 2024, arXiv:2310.12931, §4.2): Eureka's
**Human Normalized Score** is
> **(Method − Sparse) / |Human − Sparse|**

i.e. anchored at the **sparse ground-truth task metric** (0) and the **human reward** (1), averaged
across tasks. The +52% is the *average* of that score minus the human anchor, on a [0,3]-clipped scale.
The repo's `(LLM−Human)/|Human|` is a *different* quantity. **Two consequences:** (a) do NOT label the
repo's ratio "the Eureka normalised improvement" — it is a *Eureka-inspired* relative-Sharpe improvement;
(b) Eureka's actual formula **requires a sparse ground-truth anchor that finance does not have** (see
§5), so it is not even computable here. The honest move is to rename the repo metric "relative Sharpe
improvement over the best hand-reward" and cite Eureka as *inspiration*, not as the identical metric.
(The 83% and the existence of a +52% number are correctly cited; only the *formula* is mis-attributed.)

### C-3 [SEVERITY: MEDIUM — author/attribution]  `differential_sharpe` attribution is incomplete.
`src/baselines/rewards.py` and PREREGISTRATION cite "Moody & Saffell, 1998". The 1998 paper has **four
authors**: **Moody, Wu, Liao & Saffell (1998), *J. Forecasting* 17(5-6):441-470**. The two-author
canonical reference is **Moody & Saffell (2001), "Learning to Trade via Direct Reinforcement," *IEEE
Trans. Neural Networks* 12(4):875-889** (DOI 10.1109/72.935097). **Fix in `refs.bib`:** cite the 2001
IEEE TNN paper as primary (it is the canonical differential-Sharpe reference) and, if the 1998 paper is
cited, list all four authors. (LITERATURE_AND_DEFENSE_COMPANION §3.x already calls it "Moody-Saffell,
Learning to Trade via Direct Reinforcement (2001)" — align the baseline docstring to that.)

### C-4 [SEVERITY: LOW — internal traceability]  `docs/CAMPAIGN_benchmarks.md` §4/G2 says the deep-research findings doc is "absent."
That doc (`00_planning/CAMPAIGN_DEEP_RESEARCH_FINDINGS_2026-06-21.md`) **now exists** (verified). The
"absent" note in CAMPAIGN_benchmarks.md is stale. Minor, but it undercuts the provenance trail; update or
drop the G2 note.

---

## 2. THE REFERENCE — is "best-of-4" right, and is it statistically principled? (Hsu's MCB; the winner's curse on the baseline)

### 2.1 The direction is correct and conservative — keep "best-of-4."
Deterministically, for realised scores b₁…b₄, `max(b₁..b₄) ≥ b_j ∀j`, so requiring the LLM winner to
beat the **best** of the four is **at least as hard** as beating any single fixed baseline. This is
*strictly more conservative than the established Eureka protocol*, which compared the LLM reward against
**one** human reward per task (Ma et al. 2024, verified) with **no** multiple-testing correction. So on
the reference choice alone, this design is already harder on the LLM than the field's headline result —
a strong, citable defensibility point. **State it explicitly in the write-up.**

### 2.2 But "best-of-4" is a biased-high order statistic — the winner's curse on the BASELINE side.
The hazard a referee will raise: `max` over noisy estimates is biased UP. For unbiased estimates b̂_j of
true means μ_j, **E[max_j b̂_j] ≥ max_j μ_j** (Jensen on the convex max; D'Eramo et al. arXiv:1302.7175;
Thaler 1988 *JEP* 2(1):191-202; Capen-Clapp-Campbell 1971 winner's curse). This cuts BOTH ways:
- **For a POSITIVE H1 claim ("LLM beat the best human"):** the inflated bar is *favourable* — if the LLM
  clears an over-estimated max, the true-mean comparison favours it even more. Conservative. Good.
- **For a NEGATIVE / null result ("LLM did NOT beat the best human"):** you **cannot** cleanly conclude
  the LLM is worse than the best *true* baseline — the loss may be the baseline's upward sampling noise.
  This matters for the bankable-null framing (§8): a null against an *inflated* bar is a *weaker* null
  than a null against an unbiased bar.

### 2.3 The principled name for "compare a method against the best of k" is Hsu's MCB.
**Hsu, J.C. (1996), *Multiple Comparisons: Theory and Methods*, Chapman & Hall** (ISBN 0-412-98281-1);
origin **Hsu (1981), *Ann. Statist.* 9(5):1026-1034** ("Simultaneous Confidence Intervals for all
Distances from the 'Best'") and **Edwards & Hsu (1983), *JASA* 78(384):965-971**. MCB constructs
**simultaneous** confidence intervals for
> **θ_i = μ_i − max_{j≠i} μ_j**  (each treatment minus the best of the others),

with joint coverage `P(θ_i ∈ [L_i,U_i] ∀i) ≥ 1−α`. The constrained intervals use the **one-sided
Dunnett critical value**. The relevance:
- MCB exists **precisely because the comparator is the selected winner, not a fixed control** — it prices
  in "the best-of-k is random/data-determined." Dunnett's comparison-with-a-control (Dunnett 1955 *JASA*
  50(272):1096-1121) is valid ONLY if the control is **pre-specified before seeing data**. The moment
  "which baseline is best" depends on the data, the correct tool is MCB, not a naive two-sample test.
- MCB **contains Gupta's subset selection** (Gupta 1965 *Technometrics* 7(2):225-245) as its one-sided
  (upper-bound) projection: the set of baselines not significantly worse than the best.

**The error MCB guards against — and whether THIS design commits it.** The classic mistake is: pick the
empirically-best baseline on the **same sample** you then test against, using a **standard** critical
value as if it were fixed. That yields a Type-I inflation toward `1−(1−α)^k` plus the order-statistic
bias. **Does this repo commit it?** Partially mitigated, partially exposed:
- *Mitigated:* the four baselines and the LLM winner are evaluated on the **sealed test leg** (2018-2025),
  disjoint + embargoed from search/selection (§7). Fresh test noise removes the *first-order* selection
  bias on the baseline identity. Good.
- *Exposed:* `beat_human_baseline` picks `best_name = argmax median(test Sharpe)` **on the test leg**, the
  same data the win is reported on, and then reports `beat_fraction` against that test-selected best with
  **no MCB / max-statistic correction**. So the *identity* of the best baseline is chosen on the test
  data and the comparison is made on the test data — exactly the same-sample selection MCB warns about,
  only with the test leg playing the role of the contaminated hold-out (White 2000 *Econometrica*
  68(5):1097-1126, "A Reality Check for Data Snooping": a reused hold-out stops being held-out).

### 2.4 [THREAT T-REF, SEVERITY: HIGH] The reported H1 number has no multiple-comparison correction for the max-of-4.
`beat_fraction` and `norm_improvement` are **point estimates** against a **test-selected** max; there is
no simultaneous CI, no Reality-Check / Hansen-SPA bootstrap, no MCB interval. The frozen `m=6` BH/Romano-
Wolf family (§10, R13) is the **H2** arm-contrast family and **explicitly excludes** H1 (the code is
careful: `beat_human_baseline` writes `out["h1_beat_human"]` with **no** `arm_a/arm_b/metric/level`
keys, so `assert_realized_family_matches_frozen` never sees it). So H1 currently has **zero** formal
inferential control. For a *report-only* panel that is defensible IF framed as descriptive; but the
prereg §1 states H1 as a hypothesis with an H0, which invites a referee to ask for the test.

**RECOMMENDATION R-REF (prioritised):**
1. **(Highest value, cheapest) Reframe H1 explicitly as a DESCRIPTIVE, pre-registered, report-only
   Eureka-style panel** — "the LLM winner's realised OOS Sharpe vs the best of four fixed hand-rewards" —
   and state that the **headline inferential claim is the comparative H2**, not H1 (this is already the
   project's stated posture: PREREGISTRATION §10 "the headline claim is comparative, not 'beats the
   market'"; `beat_human_baseline` docstring "POST-FREEZE, REPORT-ONLY … the headline is the comparative
   H2, not H1"). Make that subordination explicit in §1 so H1 is not read as an inferential claim it
   cannot support. **This alone resolves T-REF** — a descriptive panel needs no MCB.
2. **(If H1 is to carry any inferential weight) Add an MCB / max-statistic correction.** Either: (a)
   report a **simultaneous CI for θ_LLM = μ_LLM − max_j μ_baseline_j** via a stratified-bootstrap
   max-statistic (the rliable per-seed resampling already in the repo can be extended: resample seeds,
   recompute `LLM_IQM − max_j baseline_IQM`, take the CI); L>0 ⇒ "strictly better than the best,
   simultaneity-corrected." Or (b) a **Hansen (2005) SPA / White Reality Check** bootstrap with the null
   "the LLM is no better than the best of the four," critical value built from all four contrasts jointly.
3. **Fix the same-sample best-baseline selection (T-REF core):** choose the best baseline's **identity on
   VALIDATION**, then report the LLM-vs-that-fixed-baseline gap on the sealed **test** leg. That converts
   the max-of-4 from a test-data order statistic (biased, data-snooped) into a pre-committed control
   (Dunnett-valid). The baselines already produce validation records via the same path; this is an
   analysis-time change, not new training. **Do this regardless of (1) vs (2).**

---

## 3. THE MATCHED-COMPUTE FAIRNESS — is the n_trials=30 vs n_trials=1 deflation a FAIR handicap? (the deepest H1 question)

### 3.1 The mechanism (verified first-hand in code + against the source).
`beat_human_baseline` deflates the LLM winner DSR with `winner_n_trials` (= the search candidate count,
30 in campaign.yaml; the headline arm's `dsr[head]["n_trials"]` is threaded in at L1558/L1881) and each
baseline DSR with **N=1** (L1892, `deflated_sharpe_ratio(v, 1)`). The DSR deflation is the False Strategy
Theorem (Bailey & López de Prado 2014, *J. Portfolio Management* 40(5):94-107, SSRN 2460551; implemented
in `src/inference/deflated_sharpe.py::expected_max_sharpe`):
> E[max SR] = √Var_SR · ( (1−γ)·Φ⁻¹[1−1/N] + γ·Φ⁻¹[1−1/(N·e)] ),  γ ≈ 0.5772.

Monotone in N: larger N ⇒ larger E[max SR] = `sr_star` ⇒ smaller (SR − sr_star) ⇒ lower DSR ⇒ harder to
reject "no skill." Deflating the LLM at N=30 and the human at N=1 therefore **raises only the LLM's bar.**

### 3.2 [VERDICT] This is the statistically PRINCIPLED direction and it is CONSERVATIVE for H1.
The LLM *searched and kept the max-of-30*; the human did *not* search, so the human's single Sharpe is
not an inflated order statistic. Deflating only the side that took the max is exactly correct (it is the
DSR's stated purpose: "a backtest where the researcher has not controlled for the extent of the search
involved is worthless"). The handicap biases **against** H1 — good for a defensible positive claim, and
honest for a null. The code's own comment ("this asymmetry FAVOURS the baselines … CONSERVATIVE for H1")
is **correct**.

### 3.3 [THREAT T-NTRIALS, SEVERITY: MEDIUM] But n_trials=30 is itself an OVER-count — the 30 trials are NOT independent.
This is the nuance a López-de-Prado-literate referee will press, and it is **in LdP's own appendix.** DSR
paper Appendix 3 (verified verbatim): *"the N used to compute E[max{SR}] corresponds to the number of
**independent** trials. Suppose that we run M trials, where only N trials are independent, N<M. Clearly,
using M instead of N will **overstate** E[max{SR}]."* The canonical effective-trials method is **López de
Prado & Lewis (2019), "Detection of False Investment Strategies Using Unsupervised Learning Methods,"
*Quantitative Finance* 19(9):1555-1565** (DOI 10.1080/14697688.2019.1622311; SSRN 3167017): cluster
correlated trials (ONC) and use the number of clusters **K ≤ N** as the effective count; restated in AFML
(2018) Ch. 8. An **evolutionary LLM loop** — where each generation reflects on the prior best (the repo's
`reflect-on-best` headline, R24) — produces **highly correlated** candidates, so the *effective*
independent-trial count is **well below 30.** Using 30 therefore **over-deflates** the LLM.

**Direction for H1:** this is *doubly* conservative (asymmetric deflation + an over-counted N on the LLM
side), so it never threatens a positive claim. It DOES weaken a null: a referee can argue "with the
correct effective N̂ << 30 the LLM's bar is lower and its edge larger / its null softer." 

**RECOMMENDATION R-NTRIALS:** report the H1 DSR comparison **both ways** — (a) n_trials = 30 (the
conservative upper bound, the frozen default), and (b) a **clustering-based effective N̂** as a robustness
check (the repo already has the cross-trial machinery in `winner_dsr`; the ONC/clustering count is a
small add). State explicitly that n_trials is "ill-defined under guided search" (LdP) and that 30 is the
deliberate conservative bound. *Caveat:* the average-correlation N̂ estimator is fragile when M exceeds
the return-series length; prefer the clustering estimator and flag the fragility (LdP & Lewis warn of
exactly this). **Do not silently switch the frozen N — add (b) as a reported robustness column.**

### 3.4 [THREAT T-EFFORT, SEVERITY: MEDIUM — the asymmetry that cuts AGAINST the null] The human "N=1" UNDER-counts the human's effective search.
The flip side: each hand-reward is itself the distillation of a large *implicit* historical search
(Markowitz 1952; Rockafellar-Uryasev 2000; Moody-Saffell 2001 — decades of community optimisation). So
"N=1 for the human" arguably under-counts the human's effective trials, which would *raise* the human bar
and make H1 *harder* than the DSR accounts for. There is **no single quotable proof** of this (FLAGGED) —
the nearest support is the NAS framing that human design "has mostly been developed manually by human
experts … time-consuming and error-prone" (Elsken-Metzen-Hutter 2019, *JMLR* 20(55), NAS survey,
arXiv:1808.05377). **This is a genuine limitation AGAINST the null and the Distinction-grade move is to
disclose it**, not bury it: state plainly that the fairness asymmetry runs both ways — the DSR corrects
the LLM's *explicit* 30-candidate search but does *not* credit the human's *implicit* prior search, so
the matched-compute claim is "matched explicit search budget," not "matched total design effort." (§8
folds this into the bankable-null wording.)

### 3.5 The principled framing of "matching search-compute" — what the literature actually says.
There is no single theorem, but a strong, established methodological principle: an automated search must
be compared against a baseline given an **equivalent tuning/compute budget**, or any win is attributable
to budget, not method.
- **Melis, Dyer & Blunsom (2018), ICLR, arXiv:1707.05589** — tuned LSTMs beat NAS cells once
  hyperparameters are controlled; they **propose "leagues" with predefined computational budgets** (the
  clearest statement of compute-matched comparison).
- **Lucic et al. (2018), NeurIPS, arXiv:1711.10337** ("Are GANs Created Equal?") — "improvements can
  arise from a higher computational budget and tuning more than fundamental algorithmic changes."
- **Yu et al. (2020), ICLR, arXiv:1902.08142** and **Yang et al. (2020), ICLR, arXiv:1912.12522** — NAS
  search often does **no better than random** selection from the same pool; the proper control is "does
  the search beat **random selection of the same budget**?"
- **Li & Talwalkar (2019), UAI, arXiv:1902.07638** — random search with early stopping is a competitive
  NAS baseline; "NAS is a specialized hyperparameter optimization problem."

**The good news: this project ALREADY has the right control.** The H4 arms (`random_search` over reward
code, `bayes_opt` over the template) are **budget-matched blind/uninformed searches over the same
candidate budget** (PREREGISTRATION §3-4; `docs/CAMPAIGN_benchmarks.md` T2). So the Yu/Yang/Li critique
("does the search beat random?") is answered by **H4**, not H1. **The cleanest framing is to route the
"is the LLM's search worth it?" question to H4 and keep H1 as "did the LLM winner beat fixed *human*
rewards?"** — and to say so, linking H1's fairness defense to the H4 controls.

---

## 4. ARE THE FOUR BASELINES STRONG ENOUGH? (the overclaiming / weak-baseline risk — and the ONE concrete code-level defect)

### 4.1 [THREAT T-UNTUNED, SEVERITY: HIGH — concrete, code-grounded, the single biggest H1 vulnerability] The baselines train at HARDCODED DEFAULTS — they are UN-TUNED.
Traced first-hand through the train path:
- `run_campaign._baseline_reward_builder(name)` returns the **bare** callable `getattr(rewards, name)`
  (`return fn`), ignoring any source/params.
- The env (`src/env/portfolio_env.py:293-304`) calls `reward_fn(w, r_t, w_prev, port_ret, info)` with
  **`info = {"weights", "prev_weights", "reward_state"}` ONLY** — it injects **no** `lambda`, `window`,
  `alpha`, or `eta`.
- Therefore every parameterised baseline runs at its **module default**:
  `return_minus_variance` → **λ=1.0, window=20**; `return_minus_cvar` → **λ=1.0, α=0.05, window=50**;
  `differential_sharpe` → **η=0.1**. These defaults (`info.get("lambda", 1.0)` etc.) are **arbitrary,
  never calibrated** — λ=1.0 is a placeholder risk-aversion, η=0.1 a placeholder EMA decay.

This is **exactly** the weak-baseline confound the reproducibility literature was built to catch:
- **Ferrari Dacrema, Cremonesi & Jannach (2019), RecSys (Best Paper), arXiv:1907.06902** — of 7
  reproducible neural recommenders, **6 were beaten by well-tuned simple heuristics**; journal version
  (TOIS 2021, arXiv:1911.07698) **11 of 12.**
- **Yang, Lu, Yang & Lin (2019), SIGIR, arXiv:1904.09171** ("the Neural Hype") — gains over a **weak**
  baseline vanish over a **tuned** one (the additivity principle).
- **Musgrave et al. (2020), ECCV, arXiv:2003.08505**; **Lipton & Steinhardt (2019), CACM,
  arXiv:1807.03341** — "failure to identify the sources of empirical gains … when gains actually stem
  from hyper-parameter tuning."

**The referee's sentence writes itself:** "You searched 30 LLM candidates but pitted them against four
hand-rewards frozen at an arbitrary λ=1.0 / η=0.1. The win is a tuning artefact." For a no-viva PDF, this
objection must be pre-empted *in the document*, because there is no live defense.

**RECOMMENDATION R-UNTUNED (prioritised, and this is the most important single recommendation in this
dossier):**
1. **(Minimum, mandatory) DISCLOSE it as a stated limitation** with the precise wording: "the hand-
   baselines are evaluated at their canonical default parameters (λ=1.0, etc.), not re-tuned; the H4
   budget-matched search controls handle the 'search budget' confound, and H1 is the fixed-default-human
   comparison." This is the floor.
2. **(Strongly recommended, modest cost) Add a TUNED-BASELINE CONTROL** — the standard antidote (Melis
   "leagues," Lucic "equal HPO budget"). Give the three parameterised baselines a **small budget-matched
   sweep** over λ (and η, α, window) — even a coarse grid of ~the same size as one generation — selected
   on **validation** DSR (the same selection rule as the LLM winner), then evaluate the tuned baseline on
   the sealed test leg. This turns "LLM beat an un-tuned human" into "LLM beat a *budget-matched-tuned*
   human," which is the genuinely strong claim. Mechanically cheap: the env already round-trips
   `reward_state`; the only missing piece is injecting a per-baseline `info` with the swept params (the
   reward functions already read `info.get("lambda", …)` — they are *built* for this). This is a
   pre-freeze design addition, so it needs a prereg amendment.
3. **(If (2) is out of scope) At minimum run a λ-SCALE-ROBUSTNESS check** on the best baseline (e.g.
   λ ∈ {0.5, 1, 2, 5}) and report that the LLM still clears the *best λ* — a ×{1,…} rank-invariance
   check, cheaper than a full tune. (Mirrors the existing cost-robustness sweep, R15, and the H2
   scale-robustness posture.)

### 4.2 Baseline-by-baseline strength verdict (harsh; for the limitations section).
| Baseline | Verdict | Grounds |
|---|---|---|
| `raw_return` | **Weak by construction** | risk-blind; beating it on a risk-sensitive objective is near-automatic. Keep only as a floor/sanity reference, never as "the human." |
| `return_minus_variance` (sample MV) | **Defensibly weak OOS** | **DeMiguel-Garlappi-Uppal (2009), *RFS* 22(5):1915-1953** (verified verbatim): of 14 optimising models across 7 datasets, **none consistently beat 1/N** in Sharpe/CEQ/turnover. A *naive sample* MV reward is estimation-error-ridden; beating it is easy. **To be non-trivial it needs shrinkage (Ledoit-Wolf), and 1/N — the hardest benchmark to beat — should be in the comparison.** Note: 1/N **is** in the T0 allocator gate (`benchmark_floor`), so the project clears it elsewhere; but it is **absent from the H1 reward family**, so the H1 panel includes the weak MV and omits the strong 1/N. Consider adding `equal_weight` (a degenerate constant-weight "reward") as a reference line in the H1 panel, or explicitly cross-reference the T0 gate. |
| `return_minus_cvar` | **Reasonable / standard** | Rockafellar-Uryasev (2000) *J. Risk* 2(3):21-41; CVaR coherent (Acerbi-Tasche 2002). The most defensible "strong" tail-aware baseline of the four — *if* α and λ are sensible (they are at defaults, see T-UNTUNED). |
| `differential_sharpe` | **Legitimate but ~25-yr-old / dated** | Moody-Saffell (2001) IEEE TNN — still a recognised online-Sharpe baseline (O(1)/step), but recent (2024-26) deep-RL-trading work reports DSR can be hard to learn / yield mediocre returns, motivating composite rewards. Fine to call it "the canonical online risk-adjusted reward" (LITERATURE_COMPANION does); do **not** imply it is current SOTA. |

**Net:** the four are an *honest, recognised* set, but two are weak (raw_return trivially; sample-MV per
DeMiguel) and one is dated. Beating raw_return and sample-MV is **trivial**; the only non-trivial wins are
over `return_minus_cvar` and `differential_sharpe`, **and those are only non-trivial if tuned** (R-UNTUNED).
Because the reference is the **max** of the four, the *effective* human bar in practice will almost
certainly be `return_minus_cvar` or `differential_sharpe` (the two non-trivial ones), which is reassuring
— but only if they are not crippled by default params.

---

## 5. IS THE EUREKA 83% / +52% BAR TRANSFERABLE? (apples-to-oranges — single task, OOS, no ground truth)

### 5.1 [THREAT T-EUREKA, SEVERITY: HIGH for any "we replicate Eureka" framing] The Eureka metric's VALIDITY CONDITIONS are falsified here.
Eureka's headline is an **in-distribution, cross-task win-rate scored against a ground-truth fitness
function**. A single-task, OOS, no-ground-truth finance problem has **none** of the three preconditions:
1. **No OOS split in Eureka.** Eureka trains and evaluates inside the same Isaac Gym task on the same
   distribution with the same task metric (§4.2): the reward is *selected by the very quantity it is then
   reported on*. Finance **must** be OOS (the entire backtest-overfitting literature: Bailey-LdP DSR;
   PBO/CSCV). So Eureka's number is an *in-sample* win-rate; importing it to an OOS setting is not
   like-for-like.
2. **A ground-truth fitness F exists in Eureka.** Definition 2.1: *"F: Π → ℝ … a scalar evaluation of
   any policy"* — task-specific, known (e.g. `-cur_dist`, success), and it is BOTH the search signal AND
   the human-baseline yardstick. **Finance has no F** — only one noisy realised return path. The sharpest
   critique is **REvolve (Hazra et al., ICLR 2025, arXiv:2406.01309)** (FLAG: arXiv June 2024 but
   *published 2025* — cite as 2025): *"Eureka relies on having access to fitness functions … a
   chicken-and-egg dilemma — if designing a good fitness measure was feasible, one could arguably design
   an effective reward function just as easily."* This is the single most citable statement that Eureka's
   protocol presupposes a quantifiable ground truth — which fails exactly here.
3. **Eureka aggregates over 29 TASKS** (83% = 24/29). For **one** task the "fraction of tasks beaten"
   collapses to a Bernoulli {0,1}. The repo correctly substitutes **seeds** for tasks
   (`beat_fraction` over 30 seeds), but that measures **optimiser/seed noise**, not a cross-task win-rate
   — a *different* quantity from Eureka's 83%. And Eureka used **no significance test** (verified: mean of
   max over 5 PPO seeds, no p-values), so it is not even a rigorous bar to match.

### 5.2 The right success metric for a SINGLE-task, OOS reward comparison.
Not "% of tasks beaten" (needs a task population) and not "in-sample normalised improvement" (needs F and
in-distribution measurement). The defensible substitutes — **all already in the repo**:
- **A properly-tested difference in an OOS performance statistic** — the **Ledoit-Wolf (2008), *J.
  Empirical Finance* 15(5):850-859** robust Sharpe-difference test (HAC/QS kernel + studentized circular-
  block bootstrap; two return series on the **same** dates). The repo's `sharpe_difference_test` /
  per-seed `paired_seed_difference_test` (R16) is the right family — apply it to LLM-vs-best-baseline.
- **rliable interval estimates + Probability of Improvement** (Agarwal et al., NeurIPS 2021,
  arXiv:2108.13264) **across seeds within the one task**, with IQM and stratified-bootstrap CIs — already
  the project's seed-reporting standard (§10). This is the correct single-task analogue of "win-rate."
- **Deflate for the searched-candidate count** (DSR / PBO) — already done (§3).

**RECOMMENDATION R-EUREKA:** Demote the 83%/+52% bars to **context, not a target**. Frame: "Eureka (robot
manipulation, dense rewards, in-distribution, ground-truth F) reports the LLM beat the human reward on
83% of tasks at +52% normalised improvement; we report the **single-task OOS analogue** — the LLM
winner's realised test Sharpe and its rliable probability-of-improvement vs the best of four fixed
hand-rewards, deflated for search — and note the protocols differ (cross-task in-sample vs single-task
OOS), so the numbers are not directly comparable." The code's existing labelling ("POST-FREEZE,
REPORT-ONLY context — NOT a pass/fail threshold") is already correct; make the *prose* match it and add
the protocol caveat. **Do not write "we replicate / match Eureka."**

---

## 6. THE OOS EVALUATION & THE "PAIRED" COMPARISON

### 6.1 [THREAT T-PAIR, SEVERITY: MEDIUM] `beat_fraction` against a scalar bar is not a paired test; `beat_fraction_paired` is correctly flagged.
- `beat_fraction = mean(LLM_per_seed_Sharpe > best_baseline_MEDIAN)` compares a **distribution** (30 LLM
  seeds) against a **single scalar** (the baseline's median). That is a one-sample exceedance fraction,
  **not** a two-sample or paired test. It answers "how often does the LLM clear the baseline's central
  tendency," which is descriptive and fine *as such*, but it is not a significance statement and must not
  be reported as one.
- `beat_fraction_paired` (LLM seed s vs best-per-seed baseline at seed s) is **correctly flagged as a
  sensitivity only** in the code: *"The seed index is NOT a paired draw across two DIFFERENT rewards (each
  reward induces its own trajectory)."* That caution is **right but slightly overstated.** The pairing on
  **seed** IS a valid matched-pairs design *if* the seed is the common-random-number (CRN) block: the seed
  is assigned **before** training, is identical across both reward arms, and is not a function of which
  reward is used (it sets env reset + net init + exploration RNG). Pairing on a **pre-treatment** variable
  is the textbook validity condition — so the design is **valid**; what is *not guaranteed* is the
  **efficiency** (variance reduction), because the two rewards drive the policy to different states and the
  consumed random draws **decorrelate** along the trajectory (Glasserman & Yao 1992, *Mgmt Sci*
  38(6):884-908 — CRN variance reduction is guaranteed only under monotonicity/continuity; the paired-t is
  the correct interval but can backfire if ρ < 0). So: **valid design, uncertain efficiency.**

**RECOMMENDATION R-PAIR:**
1. Keep `beat_fraction` as **descriptive** only; do not attach a p-value to it.
2. Promote a **proper paired/contemporaneous test** to the H1 panel: the LLM winner vs the (validation-
   selected, §2.3) best baseline, both on the **same test dates**, via the Ledoit-Wolf (2008)
   studentized block-bootstrap Sharpe-difference — the repo already has the analogue.
3. For the per-seed paired statistic, **report the empirical paired correlation / realised variance
   reduction** (paired-difference variance vs unpaired) rather than asserting blocking helped — this
   converts the code's hand-wave into a measured fact and pre-empts the CRN objection.

### 6.2 The OOS leg itself is clean (verified). 
Search/select on train(2005-14)/val(2015-17); test 2018-25 sealed; inter-split purge = max(embargo 21,
lookback 60) = 60 sessions (R18, López de Prado 2018). No feature window crosses a split. The composition
limitation (2005-cohort traded through 2018-25; R17) is **already a stated headline limitation** with a
PIT-universe robustness re-run available — good, leave as is. The baselines run through the **identical**
env/cost path as the winners (`evaluate_baselines_on_test` → same `_baseline_winner_record` schema), so
every reward pays the same transaction cost — the comparison is like-for-like on costs. ✔

---

## 7. THREAT-TO-VALIDITY REGISTER (severity-ranked; the harsh summary)

| # | Threat | Severity | Direction vs H1 | Fix (§) |
|---|---|---|---|---|
| **T-UNTUNED** | Baselines train at arbitrary hardcoded defaults (λ=1.0, η=0.1, α=0.05) — un-tuned weak baselines; env injects no params (verified code) | **HIGH** | inflates H1 (weak human) — the overclaiming risk | R-UNTUNED (§4.1): disclose + tuned-baseline control + λ-robustness |
| **C-1** | "PREREGISTRATION §18-19" cited ≥6× but the prereg has only 12 sections (H1 is §1) | **HIGH** | citation defect (catchable) | §1: amend to §1/§9 |
| **C-2** | Repo's "Eureka normalised improvement" formula `(LLM−H)/|H|` ≠ Eureka's `(M−Sparse)/|H−Sparse|` | **HIGH** | mis-attribution | §1: rename "relative Sharpe improvement"; cite Eureka as inspiration |
| **T-REF** | No multiple-comparison/MCB correction for max-of-4; best baseline selected on the SAME test data it's reported on (data-snoop) | **HIGH** | softens a null; data-snoops the identity | R-REF (§2.4): reframe descriptive OR add MCB/SPA; select best on validation |
| **T-EUREKA** | Eureka's validity conditions (in-distribution, ground-truth F, cross-task) are falsified here | **HIGH** (if "replicate Eureka" framing) | apples-to-oranges | R-EUREKA (§5): demote to context, add protocol caveat |
| **T-EFFORT** | Human "N=1" under-counts the human's implicit historical search | **MEDIUM** | makes H1 *harder* than DSR credits — against the null | §3.4: disclose the two-way asymmetry |
| **T-NTRIALS** | n_trials=30 over-counts effective trials (evolutionary candidates correlated; LdP "ill-defined") | **MEDIUM** | doubly conservative for a positive claim; softens a null | R-NTRIALS (§3.3): report N=30 + clustered N̂ robustness |
| **T-PAIR** | `beat_fraction` vs a scalar is not a test; per-seed pairing valid but efficiency unproven | **MEDIUM** | descriptive overstated as inferential | R-PAIR (§6.1): proper Ledoit-Wolf paired test; report realised ρ |
| **C-3** | `differential_sharpe` cited "Moody & Saffell 1998" (4 authors; canonical is 2001 IEEE TNN) | **MEDIUM** | citation precision | §1: fix refs.bib |
| **C-4** | CAMPAIGN_benchmarks.md says the deep-research doc is "absent" (it now exists) | **LOW** | stale provenance note | §1: update |

**Cross-cutting good news (do not "fix"):** the asymmetric DSR deflation is principled and conservative
(§3.2); best-of-4 is conservative for a positive claim and stricter than Eureka's 1-human protocol
(§2.1); the H4 arms already supply the budget-matched-search control the AutoML critique demands (§3.5);
the OOS leg, purge, and identical-cost benchmark rollout are clean (§6.2); the code already labels H1
"REPORT-ONLY, the headline is H2" (§2.4 R-REF item 1) — the prose just needs to match.

---

## 8. THE STRONGEST DEFENSIBLE H1 FRAMING + THE BANKABLE-NULL STATEMENT

### 8.1 The strongest framing (what to write).
> **H1 is a pre-registered, post-freeze, REPORT-ONLY descriptive panel — a single-task, out-of-sample,
> finance analogue of Eureka's "beat-the-human" result — and is deliberately subordinate to the
> comparative headline (H2).** On a sealed 2018-2025 test leg, the LLM-designed winner's realised
> risk-adjusted performance is compared against the best of four canonical hand-designed rewards
> {raw return, return−variance, return−CVaR, differential Sharpe}, each run through the identical costed
> environment. The comparison is engineered to be **conservative for the LLM**: (i) the reference is the
> **maximum** over the four (a strictly higher bar than Eureka's single-human protocol, and stricter than
> any one baseline); (ii) the LLM winner's Deflated Sharpe is **deflated by its 30-candidate search
> multiplicity** (False Strategy Theorem, Bailey-López de Prado 2014) while the un-searched baselines are
> deflated by N=1 — the asymmetry **favours the human**. The "is the LLM's *search* worth it?" question
> is answered separately and rigorously by the **budget-matched H4 controls** (random-search-over-code,
> Bayesian-opt-over-template), so H1 isolates the "fixed-human-reward" comparison. **Two fairness
> asymmetries are disclosed up front:** the hand-baselines are evaluated at canonical default parameters
> (not re-tuned — mitigated by a budget-matched tuned-baseline robustness check and a λ-scale-invariance
> check), and the DSR credits the LLM's *explicit* search but not the human's *implicit* historical
> search, so "matched compute" means *matched explicit search budget*, not *matched total design effort*.

### 8.2 The bankable null (what to write if H1 does NOT clear the bar — and why it still grades well).
> **A pre-registered non-result on H1 is a clean, informative finding.** With (a) the reference fixed as
> the max-of-four *before* the run, (b) the LLM handicapped by a 30-trial DSR deflation that the human
> does not pay, (c) the baselines at their canonical defaults *plus* a budget-matched tuned-baseline
> control, and (d) the rliable per-seed inference (IQM, probability of improvement, stratified-bootstrap
> CI) and a Ledoit-Wolf paired Sharpe-difference test on the sealed leg, "the LLM-designed reward did not
> reliably beat the best hand-designed reward out-of-sample" answers H1 *as posed*. It does **not**
> undercut the dissertation, because the **contribution is the feedback channel (H2)** and the
> **method/machinery (the LLM reward-design loop adapted to finance with a no-oracle held-out fitness)**,
> neither of which depends on H1 resolving positive. **The honest reading is sharper than a bare null:**
> a single fixed RL agent over a 30-name PIT sleeve, OOS through 2018-25, is a *hard* setting where even
> 14 optimising allocators fail to beat 1/N (DeMiguel-Garlappi-Uppal 2009); that an LLM-authored reward
> *matches* (rather than dominates) decades-distilled hand-rewards under a search-deflation handicap is
> itself a result about the difficulty of the domain, not a failure of the method.

### 8.3 The strongest POSITIVE claim (if H1 clears the bar) — what you ARE allowed to say.
> "Under a search-deflation handicap and against the **maximum** of four canonical hand-rewards
> (including a budget-matched **tuned** variant), the LLM-designed winner's OOS risk-adjusted performance
> exceeded the best human baseline on the sealed test leg, with [rliable probability of improvement] and
> a Ledoit-Wolf paired Sharpe-difference [significant/CI]." **Not** allowed: "advances the state of the
> art" (the baselines are recognised but not current SOTA; the headline is comparative, §10), or "matches
> Eureka's 83%/+52%" (different protocol, §5).

---

## 9. PRIORITISED PRE-FREEZE HARDENING CHECKLIST

**Tier A — do before freeze (cheap, high-value, several are pure documentation):**
1. **[C-1]** Replace all "§18-19" with "§1 / §9" (code comments + 2 configs). Dated amendment.
2. **[C-2]** Rename the repo's normalised-improvement metric to "relative Sharpe improvement over the best
   hand-reward"; cite Eureka as *inspiration*; correct `docs/CAMPAIGN_benchmarks.md §2b`. Do NOT claim the
   Eureka formula.
3. **[R-REF item 1]** Add one sentence to PREREGISTRATION §1 stating H1 is a **descriptive, report-only**
   panel subordinate to H2 (matches the code's own docstring). This *retires* the "no MCB" objection for
   free by removing the inferential claim.
4. **[R-REF item 3 / T-REF]** Change `beat_human_baseline` to select the best-baseline **identity on
   validation**, evaluate the gap on test (analysis-time, no retrain). Amendment.
5. **[R-EUREKA]** Add the protocol-difference caveat (single-task OOS vs cross-task in-sample; no
   ground-truth F; REvolve 2025 chicken-and-egg) wherever the 83%/52% bars appear.
6. **[T-EFFORT / §3.4]** Add the two-way fairness-asymmetry disclosure to the H1 limitations.
7. **[C-3, C-4]** Fix the `differential_sharpe` citation (Moody-Saffell 2001 IEEE TNN, 4-author 1998);
   drop the stale "absent doc" note.

**Tier B — strongly recommended (modest cost, converts the biggest threat into a strength):**
8. **[R-UNTUNED item 2]** Add a **budget-matched tuned-baseline control**: a small validation-selected
   sweep over λ/η/α/window for the three parameterised baselines, evaluated on the sealed leg. The reward
   functions already read `info.get("lambda", …)` — only a per-baseline `info` injection is missing.
   Prereg amendment. **This is the single most defensibility-increasing change available for H1.**
9. **[R-NTRIALS]** Report the H1 DSR comparison at both n_trials=30 (frozen) **and** a clustering-based
   effective N̂ (LdP & Lewis 2019) as a robustness column.
10. **[R-PAIR]** Add a proper **Ledoit-Wolf paired Sharpe-difference test** (LLM vs validation-selected
    best baseline, same test dates) to the H1 panel; report the realised per-seed paired correlation.

**Tier C — optional (only if budget allows):**
11. **[§4.2]** Add `equal_weight` (1/N) as a reference line in the H1 reward panel, or explicitly
    cross-reference the T0 gate, so the panel does not omit the literature's hardest benchmark while
    keeping the weak sample-MV.
12. **[R-UNTUNED item 3]** If (8) is out of scope, run at least the λ ∈ {0.5,1,2,5} scale-robustness check
    on the best baseline.

---

## 10. PROVENANCE

**Code read first-hand (read-only):** `src/baselines/rewards.py` (REWARD_CANON, the 4 H1 rewards + 5
secondary, all defaults); `src/selection/fitness.py` (held-out validation-DSR selection; var_sr=None
proxy); `src/inference/deflated_sharpe.py` (`expected_max_sharpe` False-Strategy-Theorem, `deflated_
sharpe_ratio`, the within-series proxy vs cross-trial var); `scripts/analyze_campaign.py` (`winner_dsr`
L299, `beat_human_baseline` L1770, `EUREKA_*` L1746-1747, `analyze` H1 wiring L1549-1565, the §18-19
strings); `scripts/run_campaign.py` (`_baseline_reward_builder` L581 `return fn`, `run_baselines`/
`evaluate_baselines_on_test` L599+, `_baseline_winner_record` L551); `src/orchestration/parallel.py`
(`train_candidate` baseline branch L210-215 `getattr(R, spec["reward"])`, no param injection);
`src/env/portfolio_env.py` L293-311 (`info = {weights, prev_weights, reward_state}` — NO λ/window/α/η
injected — the T-UNTUNED root cause); `tests/test_baselines.py`; `config/campaign.yaml` (`h1_baselines`
L47, candidates_per_arm 30, seeds 0-29), `config/eureka_loop.yaml` (10-name panel since R97, now real names),
`config/prototype.yaml` (40 candidates / 8 gen). `PREREGISTRATION.md` §1/§5/§9/§10 + amendment record
(verified: 12 sections, no §18-19).

**Literature (web-verified this session; full citations inline above; flags carried from the research):**
Hsu MCB — Hsu (1996) *Multiple Comparisons*; Hsu (1981) *Ann. Statist.* 9(5):1026-1034; Edwards & Hsu
(1983) *JASA* 78(384):965-971; Gupta (1965) *Technometrics* 7(2):225-245; Dunnett (1955) *JASA*
50(272):1096-1121. Data-snooping — White (2000) *Econometrica* 68(5):1097-1126; Hansen (2005) SPA.
Eureka — Ma et al. (2024) ICLR, arXiv:2310.12931 (83% = 24/29; HNS = (M−Sparse)/|H−Sparse|; K=16,
N=5 iters, 5 PPO seeds, no significance test — all §4.2/§3.2 verified). REvolve — Hazra et al. ICLR 2025,
arXiv:2406.01309 (FLAG: arXiv 2024, published 2025). Text2Reward — Xie et al. ICLR 2024, arXiv:2309.11489.
DrEureka — Ma et al. RSS 2024, arXiv:2406.01967. DSR — Bailey & López de Prado (2014) *JPM* 40(5):94-107,
SSRN 2460551 (False Strategy Theorem + Appendix-3 "using M instead of N will overstate E[max SR]"
verified verbatim). Effective trials — López de Prado & Lewis (2019) *Quant. Finance* 19(9):1555-1565,
SSRN 3167017 (K ≤ N, clustering); AFML (2018) Ch. 8. Weak-baseline — Ferrari Dacrema et al. RecSys 2019
arXiv:1907.06902 (6/7) + TOIS 2021 arXiv:1911.07698 (11/12); Yang-Lu-Yang-Lin SIGIR 2019 arXiv:1904.09171;
Musgrave et al. ECCV 2020 arXiv:2003.08505; Lipton-Steinhardt CACM 2019 arXiv:1807.03341. Compute-matched —
Melis et al. ICLR 2018 arXiv:1707.05589 ("leagues"); Lucic et al. NeurIPS 2018 arXiv:1711.10337; Yu et al.
ICLR 2020 arXiv:1902.08142; Yang et al. ICLR 2020 arXiv:1912.12522; Li & Talwalkar UAI 2019 arXiv:1902.07638;
Elsken-Metzen-Hutter JMLR 2019 arXiv:1808.05377 (NAS survey). Baselines — Markowitz (1952) *J. Finance*
7(1):77-91; DeMiguel-Garlappi-Uppal (2009) *RFS* 22(5):1915-1953 (14 models, none beat 1/N — verified
verbatim); Rockafellar-Uryasev (2000) *J. Risk* 2(3):21-41; Acerbi-Tasche (2002) *JBF* 26(7):1487-1503;
Moody-Saffell (2001) *IEEE TNN* 12(4):875-889; Moody-Wu-Liao-Saffell (1998) *J. Forecasting* 17(5-6):441-470.
Sharpe test — Ledoit & Wolf (2008) *J. Empirical Finance* 15(5):850-859 (HAC/QS + studentized block
bootstrap, contemporaneous). RL seeds — Agarwal et al. NeurIPS 2021 arXiv:2108.13264 (rliable: IQM, PoI,
stratified bootstrap); Henderson et al. AAAI 2018 arXiv:1709.06560 (seed variance); Colas et al.
arXiv:1806.08295 (≥20 for the bootstrap test). CRN — Glasserman & Yao (1992) *Mgmt Sci* 38(6):884-908;
Law & Kelton, *Simulation Modeling and Analysis*. Order-statistic bias — D'Eramo et al. arXiv:1302.7175;
Thaler (1988) *JEP* 2(1):191-202; Capen-Clapp-Campbell (1971) *JPT* 23(6):641-653.

**Flags (carried verbatim from the research legs — verify before they enter refs.bib):** Edwards & Hsu
(1983) DOI + 1984 corrigendum page unconfirmed (paywall); False-Strategy-Theorem published *year*
(2018 preprint vs AMM Vol. 128 ≈ 2021); Rockafellar-Uryasev pages 21-41 (ignore SciRP "21-42"/"Vol. 3");
REvolve year (2025 not 2024); Sculley et al. "Winner's Curse?" has NO arXiv id (OpenReview rJWF0Fywf
only — do not cite arXiv:1807.03341, which is Lipton-Steinhardt); the "DSR mediocre/hard-to-learn" adjective
for differential Sharpe is community sentiment (secondary) — attribute to a specific 2024-26 paper or drop;
the per-seed reward-A-vs-B trajectory-decorrelation argument is an analytical synthesis (Glasserman-Yao
conditions), not a measured result — fill with own campaign data.
