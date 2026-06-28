# Supercomputer Execution Runbook — to Sept 1 dissertation + a top-venue paper

> Operational plan given the two decisions (2026-06-27): **dissertation deadline = 1 September 2026 (~9 weeks)**
> and **target a top-venue paper in addition to the Distinction**. Built on the Option A strategy
> (`OPTION_A_compute_enabled_expansion.md`). Two repo facts verified: `scripts/learning_curve.py` exists (the
> convergence study is ready to run), and the λ-sweep's *selection* step is free (re-rank archived
> `record.json: val_returns` at any λ via `held_out_fitness(..., lam=…)`; only new winners need test-legs).

## The single most important framing: two sequenced artifacts

- **Artifact 1 — the dissertation (hard deadline 1 Sept).** Phases 0–2 (converged agent → full campaign + CPCV →
  λ-sweep + mechanism). This is a genuinely world-class, publishable-in-itself dissertation and **secures the
  90%+**. Do NOT gate it on the heaviest extensions.
- **Artifact 2 — the top-venue paper (submitted after 1 Sept).** The same campaign + Phase 3 (multi-model panel,
  multi-universe). The realistic strong target is **ICLR 2027 (≈ late-Sept 2026 deadline) or TMLR (rolling)**, not
  ICAIF'26 (its ≈ 2 Aug deadline is too tight to also include the heavy extensions). A workshop is the safe interim.
  The dissertation's results carry straight into the paper; Phase 3 is added in Sept–Oct.

## The critical-path bottleneck (act today)

**The HPC account is the gate.** Submit the UCL Research Computing request now (the drafted form) — approval +
onboarding is realistically 1–2 weeks. **Everything compute-bound waits on it**, so the freeze/campaign cannot
start until it lands. Use the wait productively (Week 0 below). **Fallback:** if the account is not productive by
~late July, run the convergence ladder + campaign at a *reduced* budget on the laptop / rented GPU for the
dissertation (Option B still hits 90%+), and use the supercomputer purely for the paper extensions afterward — so
HPC delays never threaten the 1 Sept deadline.

## The non-negotiable sequencing rule

`convergence ladder (pre-freeze) → choose budget at the knee → pre-register λ-sweep + multi-model as secondary →
FREEZE → campaign + CPCV → walled-off extensions`. The convergence study **must** finish before the freeze because
it sets `total_timesteps`. Nothing data-contingent ever flows into the frozen confirmatory null.

## Week-by-week (≈9 weeks)

**Week 0 (now → ~4 Jul) — no HPC needed; remove every non-compute blocker.**
- Submit the HPC account request (critical path).
- Email `rc-support@ucl.ac.uk`: confirm the granted cluster + scheduler (Myriad=SGE / Kathleen=Slurm), max
  job-array size, GPU node types, and the no-internet-on-compute-nodes workflow.
- Prepare the **pre-freeze package** so HPC day-1 is productive: (a) the convergence-ladder run protocol + the
  exact `learning_curve.py` invocation + an SGE/Slurm job-array template; (b) a **pre-registration amendment**
  adding the λ-sweep (qualitative ∃λ>0 interaction) and the multi-model panel as *secondary* hypotheses, with the
  budget/seed fields left to the ladder result.
- In parallel: finish the dissertation document (Chapter 6 scaffold; `refs.bib` from the verified backbone) and
  **build the no-compute analyses** on the 239 archived candidates (reward-distance EPIC/STARC, QD diversity,
  hierarchical Bayes, Model Confidence Set, triangulated null, mediation) — real Chapter-6 machinery now, and it
  de-risks the campaign analysis code.

**Weeks 1–2 (~4–18 Jul) — HPC onboarding + Phase 0 + FREEZE.**
- Stand up the environment on the cluster (venv, deterministic kernels: `CUBLAS_WORKSPACE_CONFIG=:4096:8`,
  `use_deterministic_algorithms(True)`, **TF32 off**, device-pin `#$ -ac allow=L`).
- Run the **convergence ladder** {25k…1M steps} × ~5–10 seeds on scalar/distributional/placebo; pick the budget at
  the knee (in-sample plateau AND OOS/PBO not yet decaying). Raise seeds 30 → ~100.
- Record the budget/seeds in the pre-registration; pre-register the λ-sweep + multi-model secondary; **freeze**
  (`freeze.py`, new SHA, git tag + OTS).

**Weeks 3–4 (~18 Jul–1 Aug) — Phase 1 + Phase 2.**
- Run the **full confirmatory campaign**: 7 arms × ~100 seeds × converged budget, SGE job array (one task per
  arm×seed×candidate; idempotent rerun-the-gaps manifest), + **walk-forward CPCV** (nested: inner CPCV for
  selection, outer sealed paths for H2). This fills Chapter 6 / secures the grade.
- Run the cheap walled-off extensions: **λ-sweep** (free re-ranking + a handful of new-winner test-legs) and the
  **dose-response mechanism battery** (fed-tail magnitude × permuted-placebo × Sonnet-vs-Opus).

**Weeks 5–6 (~1–15 Aug) — analysis + Chapter 6.**
- Run the full analysis stack on the campaign (PBO/DSR/IUT/rliable + the 9 analyses, now confirmatory). Write
  **Chapter 6 (Results + mechanism)**; finalise the result sentence in the abstract/intro/discussion.

**Weeks 7–8 (~15–29 Aug) — finalise the dissertation.**
- Citation pass (every `refs.bib` entry verified; `% VERIFY` cleared); polish; Limitations + Rigour-Ledger
  appendices; figures; internal read-through against the marking rubric. Secure Okhrati's written sign-off on the
  proposal-pivot disclosure.

**Week 9 (~29 Aug–1 Sept) — submit the dissertation.**

**Post-1 Sept — the top-venue paper (Phase 3).**
- Multi-model panel (Claude + DeepSeek + Qwen, vLLM-self-hosted, frozen artifacts) and multi-universe (US small-cap
  via UCL's free WRDS/CRSP + regime breakdown), each as a separately pre-registered exploratory extension. Reframe
  as "a pre-registered instrument that maps the boundary condition + the mechanism." Target ICLR 2027 / TMLR /
  workshop. The critic 2×2 and scaled island search are optional further depth.

## What raises the GRADE vs the PAPER (so effort is allocated right)
- **Grade (1 Sept):** convergence (the gate) + full-power campaign + CPCV + the no-compute analyses + flawless
  writing. The λ-sweep and dose-response add depth/insurance. Multi-model/multi-universe are NOT needed for 90%+.
- **Paper (post-Sept):** the 5 necessary items — converged agent, **multi-model**, **multi-universe + walk-forward**,
  a **measured mechanism** (dose-response), and **power** (CIs excluding the SESOI). The λ-sweep is the wildcard
  that could turn the null into a positive interaction result and would be the paper's headline if it fires.
