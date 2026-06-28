# OPTION A — Compute-Enabled Expansion (UCL supercomputer) — strategy & integrity plan

> **Status: strategy memo (2026-06-27), backed by a 12-scout deep research sweep.** OPTIONAL. Option B (the
> laptop campaign + the written dissertation) already targets 90%+ and is preserved unchanged (§7). This memo
> says what a UCL supercomputer would add, in what order, at what cost, and — critically — how to use it
> **without breaking the freeze, the scope discipline, or the bankable-null floor.**

## 0. The one-paragraph verdict

A supercomputer raises the **publishability ceiling**, not the **grade ceiling** — with a single exception that
moves both. The grade (90%+) is already bankable on the written PDF + the pre-registered null; nine of the twelve
scouts independently reached this conclusion. The exception is **training the agent to convergence**: a null on a
demonstrably-undertrained agent (the current 50k steps is 20–60× below SAC's convergence regime) is
*uninterpretable* and, at a top venue, *desk-rejectable* — so fixing it is the one compute use that is both a
grade fix and the gate to publishability. Everything else (multi-model, multi-universe, the λ-sweep, the
dose-response mechanism, walk-forward CPCV, the critic 2×2, scaled reward search) is the path from a
"finance-workshop / TMLR null" to an "ICAIF main-track (oral-plausible)" paper — pure ceiling-raising, and only
worth doing **if there is time that does not delay the document**, which remains the binding constraint.

## 1. The integrity backbone — three tiers, the confirmatory null is immutable

The supercomputer's danger is the garden of forking paths: "the data may be used only once for hypothesis testing"
(Wagenmakers et al. 2012; Gelman & Loken 2013). The rule is absolute: **no data-contingent, compute-enabled choice
ever flows into the frozen confirmatory inference.** Everything partitions cleanly into three tiers, all of which
are safe:

- **Tier 1 — Registered confirmatory at full power [SAFE].** Run the *exact* frozen design (the H2-RA Sharpe +
  H2-Tail CVaR-5% IUTs), only with more seeds and a converged agent. No knob, condition or p-value changes. This
  is the bankable null; compute here is "the same single test at higher power", which is free of integrity cost.
- **Tier 2 — Pre-registered secondary robustness [SAFE].** Analyses already named in the frozen pre-registration
  (placebo_shuffled, PBO/DSR, the delisting band, factor attribution, and — see §3 — the walk-forward folds that
  were *in the original plan then deferred for compute*). Reported in a "pre-registered robustness" subsection.
- **Tier 3 — NEW exploratory extensions [SAFE ONLY IF WALLED OFF].** The λ-sweep, multi-model, multi-universe,
  dose-response mechanism, scaled/island reward search, the critic 2×2. Each enters via **either** a clearly-headed
  *"Exploratory analyses (not pre-registered)"* section (hypothesis-*generating*, no p-values into the headline,
  reported as a full specification-curve/multiverse not a cherry-picked branch — Simonsohn 2020; Steegen 2016),
  **or** a separately time-stamped **v2 pre-registration** written before running (Weston/Mellor secondary-data
  template) if a Tier-3 result is to carry quasi-confirmatory weight.

**Sequencing rule (load-bearing):** the convergence study (§2) is the one Tier-1 item that must run **before** the
freeze, because it *sets the frozen training budget*. Order: **learning-curve ladder → choose budget at the knee →
(re-tune arms if needed) → compute the freeze SHA → run the campaign at full power → Tier-2/Tier-3 extensions.**

## 2. TIER 1 — Train to convergence (the single highest-value compute use; grade + publishability)

The #1 internal-validity limitation is undertraining: 50k env-steps vs SAC's canonical 1M (HalfCheetah/Hopper),
3M (Ant), 10M (Humanoid) regime [Haarnoja et al. 2018, fetched figures; SB3 RL-Zoo defaults 1M–2M]. With
`learning_starts=10,000`, only ~40k post-warmup gradient steps occur. A null on this agent is not interpretable.

**The fix — a pre-freeze learning-curve ladder.** Train a *representative subset* of arms (scalar / distributional
/ placebo) over `{25k, 50k, 100k, 200k, 500k, 1M}` env-steps × ~5–10 seeds, reporting per rung: (i) in-sample IQM
return + stratified-bootstrap CI (rliable sample-efficiency curve; plateau via last-10% time-average, Patterson et
al. 2024); (ii) critic-loss / Q-magnitude stability (the deadly-triad axis — explains the 64 critic explosions);
(iii) **out-of-sample metric + PBO vs steps** (the finance twist — more steps can *overfit* the backtest, so the
budget is the *knee* where in-sample plateaus but OOS has not yet decayed). Pick that knee as the single frozen
`total_timesteps`.

- **Cost:** ladder ≈ 1.875M steps/seed; 3 arms × 5 seeds ≈ ~28M steps total — a *fraction* of one MuJoCo paper
  (one Humanoid run is 10M). Hours-to-low-days of wall-clock on the existing parallel engine.
- **Integrity:** freeze-SAFE and *mandatory* — it fixes a construct-validity threat and must be recorded in the
  pre-registration before the SHA. Per Patterson et al., tuning is budget-conditional, so the order above is not
  optional.
- **Ceiling:** raises **both**. Retires the "was it trained enough?" objection that otherwise caps the work at a
  workshop "no matter how much else you add" (venue scout). **Recommendation: do this even in Option B if *any*
  compute is available — it is the highest-leverage single action in the whole project.**

**Also Tier-1: more seeds.** 30 → ~100 (DLM bought its NeurIPS credibility with 200 seeds and only 4 candidates).
Tightens the CIs so a non-rejection can *exclude the SESOI* (the difference between "p>0.05, a non-result" and "a
powered, bounded equivalence"). Freeze-safe if the seed count is set/registered before the freeze.

## 3. TIER 2 — Pre-registered robustness at scale

- **Walk-forward + Combinatorial Purged CV (CPCV).** The original design specified rolling walk-forward folds
  (5y/1y/1y) then *deferred them for compute*; restoring them **fulfils the registered plan** (Tier-2, freeze-safe
  if declared before the SHA). CPCV (López de Prado 2018, Ch. 12; Gort et al. 2022 for the DRL-specific PBO) yields
  a *distribution* of OOS paths (N=8,k=2 → 28 splits → 7 paths) feeding PBO/DSR — converting "one sealed split"
  into "a distribution of paths under the field's most rigorous protocol", with peer-reviewed evidence that CPCV
  beats walk-forward on overfitting control (Arian-Norouzi-Seco 2024). **Wrap it in a nested structure** (inner
  CPCV for reward/hyperparameter selection, outer sealed paths for the reported H2 inference) — the clean defence
  against "tuned-on-test". *Cost:* ~28× the test-leg (sample a fixed subset of splits if needed; LdP sanctions
  this). The per-seed rliable inference becomes per-(seed×path), which *strengthens* it.
- **The critic 2×2 (named secondary).** A `{mean / quantile-TQC critic} × {scalar / tail feedback}` factorial —
  genuine white-space (no prior work runs it on one task) that tests whether an in-critic risk-aware critic makes
  the fed-tail feedback *redundant* (sub-additive) or *complementary* (super-additive). Defensible because the
  axes are mechanistically distinct (Nauman-Cygan 2023: critic-risk = certainty-equivalent on value;
  feedback-risk = shaping the signal). *Cost:* TQC is 2–3× per-step + needs ≥10 seeds/cell + DSAC-T-grade
  gradient-clipping to avoid worse critic explosions. *Integrity:* stays the pre-registered SECONDARY; the
  off-critic headline is unchanged. High publishability upside; **not** needed for the grade; risk of diluting the
  headline if done sloppily.
- **Square-root transaction-cost sweep** and **regime-conditional breakdown** at scale (already specified;
  cheap; Tier-2 robustness).

## 4. TIER 3 — The exploratory extensions that build a publishable paper

Ranked by value-toward-publication, all walled off per §1.

1. **λ-sweep × feedback interaction — the lever most likely to turn the null into a POSITIVE result.** The theory
   (Chapter 3) predicts the channel is realised only when the *selector* rewards the tail (λ>0); the frozen design
   sits at λ=0 (the Null branch). A 2-D grid `{tail-fed vs tail-blind} × {λ ∈ 0,…,λ_K}` tests the dominance
   theory's Strict prediction directly; the **interaction contrast** ("tail feedback helps *iff* λ>0") is the
   strongest possible publishable result — an interaction effect with a Blackwell / MORL-scalarization mechanism.
   **Critical, check the repo:** if λ enters only at *selection* over an already-trained candidate pool (a
   re-ranking of stored returns), the whole sweep is *nearly free* — "an afternoon, not a supercomputer job".
   *Integrity:* register as a secondary confirmatory hypothesis (mirroring the H2 IUT structure) **with the
   hypothesis stated qualitatively** ("∃ λ>0 with non-zero interaction", *not* monotone — value of information is
   non-monotone in risk aversion, Abbas et al. 2013), and apply multiplicity control across the λ family + DSR
   deflation at every λ. The original λ=0 null stays primary; the sweep is additive.
2. **Multi-model panel — the lever that earns the plural "LLMs".** The dominant external-validity hole is one
   Claude family. Add **DeepSeek-V3/R1** (open-weights, *different family and training cutoff* → simultaneously
   satisfies cross-family validity AND the §8 contamination screen) and **Qwen3** (third family, coding-strong),
   self-hosted on HPC via vLLM as *frozen, reproducible artifacts*. Mirror Eureka's GPT-4-vs-GPT-3.5 backbone
   ablation; hold contract prompt/sandbox/budget/seeds identical (the campaign engine already does this — one
   config field per model). *Watch the capability floor* (Revisiting-OPRO: small LLMs can't run the loop at all —
   pre-specify a "can it run the loop" competence check so a weak-model null isn't misread). *Cost:* GPU-hours
   (sunk on HPC) + ~2–4 weeks to stand up vLLM. *Integrity:* partly new scope → exploratory or v2-prereg. **This is
   the single biggest publishability lever** — it converts "do *this Claude model* use tail feedback?" into "do
   *LLM reward-designers* use it?".
3. **Dose-response mechanism battery — converts the correlational responsiveness into a CAUSAL claim.** Sweep the
   fed-tail magnitude across ~5–7 graded levels + a *permuted-tail placebo as the primary causal contrast* + a
   tail-removed level, across seeds × both designer models, measuring the change in the authored reward code (tail-
   term weight / CVaR-sensitivity). A flat curve + a placebo that matches the real arm = a strong, *visual*, causal
   null; the Sonnet-vs-Opus contrast tests whether the negative responsiveness is a *capability threshold* rather
   than a fundamental channel failure (the near-isomorphic precedent: Wainrib et al. 2026 "lab-in-the-loop", 800
   replicated experiments, permuted-feedback placebo, model-version-as-dose). *Integrity:* the dose-response +
   placebo is pre-registrable as a confirmatory mechanism test; the model-version contrast + mediation NDE/NIE
   decomposition are exploratory. **A measured, predictive mechanism is what makes a null a *scientific*
   contribution** (the "Are More LLM Calls"/GANs-Equal move).
4. **Multi-universe generalization — the top-venue generalization, but a v2/second paper.** US **small-cap**
   (Russell 2000 / S&P 600 via CRSP/WRDS — *free at UCL*, survivorship-free) is the best single addition: the
   fattest-tailed *trivially-PIT-feasible* universe, where the tail channel should bite hardest (your large-cap
   headline is the *thinnest*-tailed, channel-suppressing test). Add a regime-sliced re-analysis (calm / COVID /
   2022-bear) as a cheap second axis. Report per-instance + pooled via stratified bootstrap (rliable). *Integrity:*
   **NEW SCOPE, do NOT fold into the frozen null** (scope discipline + forking paths) — a separately pre-registered
   "generalization" study / v2 / labelled-exploratory appendix. *Ceiling:* pure publishability; **named as future
   work it also scores grade points for honest limitation disclosure.**
5. **Scaled / island reward search — needed for the top-venue bar, risky for H4.** 30 candidates is *defensible
   for H2* (Eureka's own ablation: the feedback loop ≫ raw candidate count) but the H4 LLM-vs-search result may sit
   on the *steep* part of the scaling curve where the LLM advantage is overstated (literature inflection ~hundreds–
   2,000 candidates; CodeEvolve 45→200 calls moved reward 66→144). To clear the AlphaEvolve/FunSearch bar, raise to
   ~200–500 candidates/arm with an island/MAP-Elites layer and report Coverage + QD-Score. *Integrity:* candidate
   budget is a frozen matched-compute parameter — **scale ALL arms equally**, register the new condition or label
   exploratory, and report islands as a *different method*, not "more samples". Never claim "explored the reward
   space" at 30 (that lives at 10³–10⁶).

## 5. The publication-ceiling map (what compute actually buys)

The realistic main-track target is **ICAIF** (the accepted-papers list already contains CVaR-constrained RL,
portfolio reward-design, and risk-preference reward learning; ~32% overall / ~15% oral; 8 pages, no supplementary,
no rebuttal — write the whole case self-contained). The workshop→main-track delta is the **five NECESSARY items**
(none compute-solvable by scale alone): **(1) demonstrated convergence/training adequacy [the gate], (2)
multi-model, (3) multi-universe + walk-forward, (4) a *measured, predictive mechanism* for the null (not a
caveat), (5) power that lets a CI exclude the SESOI.** A NeurIPS/ICML shot exists **only if** the framing escapes
finance ("tail-risk / multi-level feedback transmission in LLM reward-design", finance as the testbed) — a ~1-in-4
lottery even then. **TMLR remains the bankable floor** (its criteria explicitly drop novelty/SOTA → a clean null
passes by design). The decisive reframe across all of this: stop selling "LLMs don't use tail feedback" (a bare
null) and sell **"a pre-registered, multi-model, multi-universe instrument that *maps the boundary condition*
under which LLM reward-designers transmit tail-risk feedback, with the mechanism that explains it"** — the
MAST / GANs-Equal move that gets a rigorous null onto a main track.

## 6. The engineering reality (do not let scaling break the freeze)

- **UCL Myriad runs SGE, not Slurm** (`#$ -t 1-10000` arrays, `$SGE_TASK_ID`, `#$ -l gpu=1`, 48h walltime,
  A100/V100). Kathleen-ng is Slurm (`--array`, but UCL caps arrays at 1000 → chunk/throttle). **Email
  `rc-support@ucl.ac.uk` to confirm the granted cluster + scheduler + MaxArraySize before writing jobscripts**;
  make the campaign emitter scheduler-agnostic. The sweep is embarrassingly parallel (one task per
  arm×seed×candidate) → no heavy checkpointing, just an idempotent "rerun the missing task IDs" manifest.
- **The #1 reproducibility risk of scaling = cross-device floating-point non-determinism.** The byte-identical
  replay was proven on *one fixed laptop*; the scheduler can place jobs on V100 or different A100 SKUs, and FP
  non-associativity + TF32 + cuDNN benchmarking guarantee non-identical replay across devices (arXiv:2408.05148;
  PyTorch reproducibility notes). **Mitigate:** (i) device-pin the whole campaign with `#$ -ac allow=L`; (ii)
  force deterministic kernels (`CUBLAS_WORKSPACE_CONFIG=:4096:8`, `torch.use_deterministic_algorithms(True)`,
  `cudnn.deterministic=True/benchmark=False`, and **disable TF32** — this *reverses* the prototype's TF32 speed
  amendment, the right trade for a frozen study); (iii) **reframe the guarantee** to "device-pinned,
  deterministic-kernel byte-identical replay within the pinned A100-L class; cross-device identity is not claimed".
  Do **not** adopt submitit/Ray (Slurm-only + adaptive schedulers violate pre-registration) — keep the
  already-proven freeze-aware array emitter and bolt on passive provenance logging only.

## 7. Option B is preserved (the default, no supercomputer)

If no supercomputer materialises: run the laptop campaign (~600 runs, ~2.6 days) at the frozen 50k budget, write
the dissertation (front matter + Chapters 1–7 are already drafted; only Chapter 6 Results is campaign-gated),
disclose undertraining/single-instance/single-model as the honest boundary conditions they are, and submit. This
already targets 90%+ and a TMLR/workshop publication. **Nothing in Option A is required for the grade** — with the
*one* caveat that, if even a little compute is available, the convergence ladder (§2) is worth running because it
is the cheapest fix to the single most damaging limitation.

## 8. Recommended decision (the honest hybrid)

1. **Regardless of Option A/B:** finish the written document (the binding constraint) and run the convergence
   ladder (§2) if any compute exists — it is the highest-leverage single action and is grade-relevant.
2. **If the supercomputer arrives AND there is time that does not delay submission:** do Tier-1 (converged agent +
   100 seeds) and the **λ-sweep** (§4.1 — check if it is nearly-free re-ranking first) and the **dose-response
   mechanism** (§4.3) — these are the highest value-per-effort and the ones most likely to convert the null into a
   *characterised, mechanistically-explained* result. Add the **multi-model panel** (§4.2) if aiming at ICAIF main.
3. **Treat multi-universe (§4.4), the critic 2×2 (§3), and scaled island search (§4.5) as the v2 / second-paper /
   post-submission programme** — the path to a top venue, explicitly named as future work in the dissertation.
4. **Never** let any of it touch the frozen confirmatory null. Freeze after the convergence ladder; everything
   else is Tier-2 robustness or walled-off Tier-3 exploratory.

The supercomputer is a publishability multiplier and a convergence-fix — not a grade requirement and not a licence
to break the freeze. Used in the order above, it converts a bankable Distinction-grade null into a credible
ICAIF-main-track paper without risking either.
